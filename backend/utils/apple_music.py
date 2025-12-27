import jwt
import time
import os
from pathlib import Path
from typing import Optional

# Token expiration: 180 days (maximum allowed by Apple Music API)
TOKEN_EXPIRATION_DAYS = 180

# In-memory cache with expiration tracking
_cached_token: Optional[str] = None
_token_expires_at: float = 0


def get_apple_music_token() -> str:
    """
    Generate and cache Apple Music API developer token.
    Token lasts 180 days before needing regeneration.
    
    The token is cached in memory with expiration tracking. Tokens are regenerated
    when they expire or when the process restarts.
    """
    global _cached_token, _token_expires_at
    
    current_time = time.time()
    
    # Return cached token if still valid (with 1 hour buffer before expiration)
    if _cached_token and current_time < (_token_expires_at - 3600):
        return _cached_token
    
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
    iat = int(current_time)
    exp = iat + (TOKEN_EXPIRATION_DAYS * 24 * 60 * 60)
    
    payload = {
        'iss': team_id,
        'iat': iat,
        'exp': exp
    }
    
    token = jwt.encode(
        payload,
        private_key,
        algorithm='ES256',
        headers={'kid': key_id}
    )
    
    # Cache the token
    _cached_token = token
    _token_expires_at = exp
    
    return token
