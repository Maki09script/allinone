from flask import Flask, request, jsonify
import database
import key_gen
import datetime
import os
import logging
from logging.handlers import RotatingFileHandler

# SETUP LOGGING
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(level=logging.INFO)
handler = RotatingFileHandler('logs/server.log', maxBytes=1000000, backupCount=5)
handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s [%(remote_addr)s] %(message)s'
))
logger = logging.getLogger('werkzeug') # Grab Flask's logger or use root
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Custom Logger for App Logic
app_logger = logging.getLogger('maki_server')
app_logger.setLevel(logging.INFO)
app_logger.addHandler(handler)

class ContextFilter(logging.Filter):
    def filter(self, record):
        record.remote_addr = request.remote_addr if request else 'SERVER'
        return True

app_logger.addFilter(ContextFilter())
handler.addFilter(ContextFilter())

app = Flask(__name__)

# CONFIGURATION (Loaded from Environment)
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "CHANGE_THIS_IN_PROD")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "CHANGE_THIS_IN_PROD")

# Initialize DB on startup
database.init_db()
app_logger.info("Server Started")

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "online", "time": datetime.datetime.now().isoformat()})

@app.route('/validate', methods=['POST'])
def validate():
    # 1. Rate Limiting
    client_ip = request.remote_addr
    if is_rate_limited(client_ip):
        return jsonify({"valid": False, "message": "Rate limit exceeded. Try again later."}), 429

    data = request.json
    license_key = data.get('key')
    hwid = data.get('hwid')
    timestamp = data.get('timestamp')
    signature = data.get('signature')

    if not all([license_key, hwid, timestamp, signature]):
        return jsonify({"valid": False, "message": "Missing authentication parameters"}), 400

    # 2. Replay Protection
    if abs(time.time() - timestamp) > MAX_REQUEST_AGE:
        return jsonify({"valid": False, "message": "Request expired (Check PC time)"}), 403

    # 3. Signature Verification
    # Reconstruct payload dict for verification (exclude signature itself)
    verify_payload = {
        "key": license_key,
        "hwid": hwid,
        "timestamp": timestamp
    }
    
    if not verify_signature(verify_payload, signature, CLIENT_SECRET):
        app_logger.warning(f"Signature Mismatch for key: {license_key[:5]}...")
        return jsonify({"valid": False, "message": "Security Verification Failed"}), 403

    license_data = database.get_license(license_key)

    if not license_data:
        app_logger.warning(f"Invalid Key Attempt: {license_key}")
        return jsonify({"valid": False, "message": "Invalid License Key"}), 404

    if license_data['is_banned']:
        app_logger.warning(f"Banned Key Attempt: {license_key[:5]}...")
        return jsonify({"valid": False, "message": "License Banned"}), 403

    # Check Expiry
    if license_data['expires_at']:
        expires_at = datetime.datetime.fromisoformat(license_data['expires_at'])
        if datetime.datetime.now() > expires_at:
            app_logger.info(f"Expired Key Attempt: {license_key[:5]}...")
            return jsonify({"valid": False, "message": "License Expired"}), 403
    
    # Check First Activation for Timed Keys
    elif "_DAYS" in license_data['type']:
        # Format "30_DAYS"
        try:
            days = int(license_data['type'].split('_')[0])
            database.activate_license(license_key, days)
            # Refetch to get new expiry
            license_data = database.get_license(license_key) 
            app_logger.info(f"Activated New Key: {license_key[:5]}... ({days} Days)")
        except: pass

    # Check HWID
    stored_hwid = license_data['hwid']
    if stored_hwid:
        if stored_hwid != hwid:
            app_logger.warning(f"HWID Mismatch: {license_key[:5]}... stored={stored_hwid} req={hwid}")
            return jsonify({"valid": False, "message": "Invalid HWID (Key locked to another device)"}), 403
    else:
        # First activation, lock to HWID
        database.update_license_hwid(license_key, hwid)
        app_logger.info(f"Existing Key Locked to HWID: {license_key[:5]}...")

    app_logger.info(f"Validation Success: {license_key[:5]}...")
    return jsonify({
        "valid": True, 
        "type": license_data['type'], 
        "message": "License Valid",
        "expires_at": license_data['expires_at']
    })

@app.route('/generate', methods=['POST'])
def generate():
    if request.headers.get('X-API-KEY') != ADMIN_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    duration = data.get('duration') # 'lifetime' or int (days)
    
    key = key_gen.generate_license_key()
    license_type = "LIFETIME"
    days = None

    if duration != 'lifetime':
        try:
            days = int(duration)
            license_type = f"{days}_DAYS"
        except:
            return jsonify({"error": "Invalid duration"}), 400

    if database.create_license(key, license_type, days):
        return jsonify({"key": key, "type": license_type})
    else:
        return jsonify({"error": "Failed to create key"}), 500

@app.route('/reset', methods=['POST'])
def reset_hwid():
    if request.headers.get('X-API-KEY') != ADMIN_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    key = data.get('key')
    
    if not database.get_license(key):
        return jsonify({"error": "Key not found"}), 404
        
    database.reset_hwid(key)
    return jsonify({"success": True, "message": "HWID Reset Successfully"})

@app.route('/delete', methods=['POST'])
def delete_key():
    if request.headers.get('X-API-KEY') != ADMIN_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    key = data.get('key')
    
    if database.delete_license(key):
        return jsonify({"success": True, "message": f"Key {key} deleted"})
    else:
        return jsonify({"error": "Key not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
