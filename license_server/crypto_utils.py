import hmac
import hashlib
import json
import time

def sign_data(data_dict, secret_key):
    """
    Signs a dictionary using HMAC-SHA256.
    The dictionary is sorted by key to ensure consistent ordering.
    """
    # Sort keys to ensure consistent serialization
    canonical_string = json.dumps(data_dict, sort_keys=True, separators=(',', ':'))
    
    signature = hmac.new(
        secret_key.encode('utf-8'),
        canonical_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return signature

def verify_signature(data_dict, signature, secret_key):
    expected = sign_data(data_dict, secret_key)
    return hmac.compare_digest(expected, signature)
