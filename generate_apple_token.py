#!/usr/bin/env python3
"""
Apple Music Developer Token Generator

This script generates a JWT token for Apple Music API authentication.
Tokens are valid for 180 days (maximum allowed by Apple).

Prerequisites:
1. Apple Developer Program membership ($99/year)
2. MusicKit key created at: https://developer.apple.com/account/resources/authkeys/list
3. Your .p8 private key file downloaded

Usage:
    python generate_apple_token.py

Or with environment variables:
    APPLE_TEAM_ID=ABC123 APPLE_KEY_ID=XYZ789 python generate_apple_token.py

Requirements:
    pip install pyjwt cryptography
"""

import os
import sys
import time
from pathlib import Path

try:
    import jwt
except ImportError:
    print("Error: PyJWT not installed. Run: pip install pyjwt cryptography")
    sys.exit(1)


def find_p8_file():
    """Find .p8 key file in current directory."""
    p8_files = list(Path(".").glob("AuthKey_*.p8"))
    if p8_files:
        return p8_files[0]
    
    p8_files = list(Path(".").glob("*.p8"))
    if p8_files:
        return p8_files[0]
    
    return None


def generate_token(team_id: str, key_id: str, private_key: str, 
                   expiry_days: int = 180) -> str:
    """
    Generate Apple Music developer token.
    
    Args:
        team_id: 10-character Team ID from Apple Developer portal
        key_id: 10-character Key ID from your MusicKit key
        private_key: Contents of your .p8 private key file
        expiry_days: Token validity in days (max 180)
    
    Returns:
        JWT token string
    """
    headers = {
        "alg": "ES256",
        "kid": key_id
    }
    
    payload = {
        "iss": team_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + (expiry_days * 24 * 60 * 60)
    }
    
    token = jwt.encode(
        payload,
        private_key,
        algorithm="ES256",
        headers=headers
    )
    
    return token


def main():
    print("=" * 60)
    print("Apple Music Developer Token Generator")
    print("=" * 60)
    print()
    
    # Get Team ID
    team_id = os.getenv("APPLE_TEAM_ID")
    if not team_id:
        team_id = input("Enter your Team ID (from developer.apple.com/account): ").strip()
    
    if len(team_id) != 10:
        print(f"Warning: Team ID should be 10 characters (got {len(team_id)})")
    
    # Get Key ID
    key_id = os.getenv("APPLE_KEY_ID")
    if not key_id:
        key_id = input("Enter your Key ID (from your MusicKit key): ").strip()
    
    if len(key_id) != 10:
        print(f"Warning: Key ID should be 10 characters (got {len(key_id)})")
    
    # Get private key
    key_path = os.getenv("APPLE_KEY_PATH")
    if not key_path:
        # Try to find .p8 file
        found_key = find_p8_file()
        if found_key:
            print(f"Found key file: {found_key}")
            use_it = input("Use this key? (y/n): ").strip().lower()
            if use_it == 'y':
                key_path = str(found_key)
        
        if not key_path:
            key_path = input("Enter path to your .p8 private key file: ").strip()
    
    # Read private key
    try:
        with open(key_path, 'r') as f:
            private_key = f.read()
    except FileNotFoundError:
        print(f"Error: Key file not found: {key_path}")
        sys.exit(1)
    
    print()
    print("Generating token...")
    
    try:
        token = generate_token(team_id, key_id, private_key)
        
        print()
        print("=" * 60)
        print("SUCCESS! Your Apple Music Developer Token:")
        print("=" * 60)
        print()
        print(token)
        print()
        print("=" * 60)
        print()
        print("Token Details:")
        print(f"  - Length: {len(token)} characters")
        print(f"  - Expires: {time.strftime('%Y-%m-%d', time.localtime(time.time() + 180*24*60*60))}")
        print()
        print("Next Steps:")
        print("  1. Copy this token")
        print("  2. Set it as APPLE_MUSIC_DEVELOPER_TOKEN in your environment")
        print("  3. For Render: Add it to your Web Service environment variables")
        print()
        print("IMPORTANT: Set a calendar reminder to regenerate this token")
        print("           before it expires in 180 days!")
        
        # Optionally save to file
        save = input("\nSave token to token.txt? (y/n): ").strip().lower()
        if save == 'y':
            with open("apple_music_token.txt", 'w') as f:
                f.write(token)
            print("Token saved to apple_music_token.txt")
            print("Remember to delete this file after copying to Render!")
        
    except Exception as e:
        print(f"Error generating token: {e}")
        print()
        print("Common issues:")
        print("  - Invalid .p8 file format")
        print("  - Wrong Team ID or Key ID")
        print("  - Corrupted private key")
        sys.exit(1)


if __name__ == "__main__":
    main()
