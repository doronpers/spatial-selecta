import jwt
import time
import os
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=1)
def get_apple_music_token() -> str:
    """
    Generate and cache Apple Music API developer token.
    Token lasts 180 days before needing regeneration.
    """
    # Load credentials from environment variables
    team_id = os.getenv('APPLE_TEAM_ID')
    key_id = os.getenv('APPLE_KEY_ID')
    key_path = os.getenv('APPLE_KEY_PATH', 'AuthKey.p8')
    
    if not team_id or not key_id:
        raise ValueError(
            "Missing APPLE_TEAM_ID or APPLE_KEY_ID environment variables"
        )
    
    # Read the private key
    key_file = Path(key_path)
    if not key_file.exists():
        raise FileNotFoundError(f"Private key file not found at {key_path}")
    
    with open(key_file, 'r') as f:
        private_key = f.read()
    
    # Create JWT token
    payload = {
        'iss': team_id,
        'iat': int(time.time()),
        'exp': int(time.time()) + (180 * 24 * 60 * 60)  # 180 days
    }
    
    token = jwt.encode(
        payload,
        private_key,
        algorithm='ES256',
        headers={'kid': key_id}
    )
    
    return token
