import jwt
import time
import os
from functools import lru_cache
from pathlib import Path

# Token expiration: 180 days (maximum allowed by Apple Music API)
TOKEN_EXPIRATION_DAYS = 180

@lru_cache(maxsize=1)
def get_apple_music_token() -> str:
    """
    Generate and cache Apple Music API developer token.
    Token lasts 180 days before needing regeneration.
    
    Note: The token is cached for the lifetime of the process. Since tokens
    are valid for 180 days, manual cache clearing or process restart is needed
    after expiration. In production, consider implementing TTL-based caching.
    """
    # Load credentials from environment variables
    team_id = os.getenv('APPLE_TEAM_ID')
    key_id = os.getenv('APPLE_KEY_ID')
    key_path = os.getenv('APPLE_KEY_PATH')
    
    if not team_id or not key_id:
        raise ValueError(
            "Missing APPLE_TEAM_ID or APPLE_KEY_ID environment variables"
        )
    
    if not key_path:
        raise ValueError(
            "Missing APPLE_KEY_PATH environment variable. "
            "Please specify the path to your .p8 private key file."
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
        'exp': int(time.time()) + (TOKEN_EXPIRATION_DAYS * 24 * 60 * 60)
    }
    
    token = jwt.encode(
        payload,
        private_key,
        algorithm='ES256',
        headers={'kid': key_id}
    )
    
    return token
