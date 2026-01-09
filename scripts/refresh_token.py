#!/usr/bin/env python3
"""
Script to refresh the Apple Music Developer Token.
Generates a new JWT using the .p8 private key and updates the .env file.
"""
import os
import sys
import re
from pathlib import Path

# Add project root to path to allow imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from backend.utils.apple_music import get_apple_music_token

def update_env_file(token):
    """Update the .env file with the new token."""
    env_path = project_root / '.env'
    
    if not env_path.exists():
        print(f"Error: .env file not found at {env_path}")
        return False
        
    with open(env_path, 'r') as f:
        content = f.read()
        
    # Regex to find and replace the token line
    pattern = r'(APPLE_MUSIC_DEVELOPER_TOKEN\s*=\s*)(.*)'
    
    if re.search(pattern, content):
        new_content = re.sub(pattern, f'\\g<1>{token}', content)
    else:
        # If not found, append it
        new_content = content + f"\nAPPLE_MUSIC_DEVELOPER_TOKEN={token}\n"
        
    with open(env_path, 'w') as f:
        f.write(new_content)
        
    print(f"Successfully updated .env with new token.")
    return True

def main():
    print("Generating new Apple Music Developer Token...")
    try:
        # Load env vars first as get_apple_music_token relies on them or os.environ
        from dotenv import load_dotenv
        load_dotenv(project_root / '.env')
        
        token = get_apple_music_token()
        print(f"Token generated successfully (starts with: {token[:20]}...)")
        
        if update_env_file(token):
            print("Done! You may need to restart the backend for changes to take effect.")
        else:
            print("Failed to update .env file.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error generating token: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure APPLE_TEAM_ID and APPLE_KEY_ID are set in .env")
        print("2. Ensure APPLE_KEY_PATH points to a valid .p8 file")
        print("3. Ensure the .p8 file exists at that path")
        sys.exit(1)

if __name__ == "__main__":
    main()
