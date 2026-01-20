import random
import string

def generate_license_key():
    """Generates a random license key in format XXXX-XXXX-XXXX-XXXX"""
    segment_length = 4
    num_segments = 4
    chars = string.ascii_uppercase + string.digits
    
    key_segments = []
    for _ in range(num_segments):
        segment = ''.join(random.choices(chars, k=segment_length))
        key_segments.append(segment)
        
    return '-'.join(key_segments)
