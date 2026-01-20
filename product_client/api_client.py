import requests
import time
from hwid_utils import get_hwid
from crypto_utils import sign_data

import os

SERVER_URL = "http://127.0.0.1:5000" # CHANGE THIS TO YOUR PUBLIC URL (ngrok/VPS) FOR PRODUCTION
CLIENT_SECRET = "SHARED_SECRET_KEY_XYZ" # REPLACE WITH YOUR SECRET BEFORE BUILDING EXE
# Note: For the Python source in Git, we keep a placeholder. 
# When building the EXE, you MUST change this string to your real secret.

def validate_license(key):
    hwid = get_hwid()
    try:
        # Create Payload
        payload = {
            "key": key, 
            "hwid": hwid,
            "timestamp": int(time.time())
        }
        
        # Sign Payload
        signature = sign_data(payload, CLIENT_SECRET)
        payload["signature"] = signature
        
        response = requests.post(f"{SERVER_URL}/validate", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('valid'):
                return True, data.get('message')
            else:
                return False, data.get('message')
        elif response.status_code == 404:
             return False, "Invalid License Key"
        elif response.status_code == 403:
             return False, response.json().get('message', 'License Error')
        else:
            return False, f"Server Error: {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return False, "Connection Failed. Check Internet."
    except Exception as e:
        return False, f"Error: {str(e)}"
