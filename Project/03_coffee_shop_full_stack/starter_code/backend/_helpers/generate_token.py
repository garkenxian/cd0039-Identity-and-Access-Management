#!/usr/bin/env python3
"""
Auth0 Test Token Generator - CLI Tool

Generate JWT tokens for test users for local testing and Postman.

Usage:
    python generate_token.py barista     # Get barista token
    python generate_token.py manager     # Get manager token

This uses Auth0's public OIDC endpoints for user authentication.
"""

import os
import sys
import json
import requests
from pathlib import Path

# Load .env file if it exists
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, _, value = line.partition('=')
                os.environ.setdefault(key.strip(), value.strip())

# Auth0 Configuration
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', 'dev-53bey634viqgnyzc.us.auth0.com')
AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
API_AUDIENCE = os.getenv('API_AUDIENCE', 'coffee-shop-api')

# Test User Credentials
TEST_USERS = {
    "barista": {
        "email": "barista@test.local",
        "password": "TempPass123!Barista"
    },
    "manager": {
        "email": "manager@test.local",
        "password": "TempPass123!Manager"
    }
}


def get_token(role: str) -> dict:
    """Generate JWT token for test user via Auth0 password grant"""
    
    if role not in TEST_USERS:
        raise ValueError(f"Invalid role '{role}'. Must be 'barista' or 'manager'")
    
    if not AUTH0_CLIENT_ID:
        raise ValueError("AUTH0_CLIENT_ID not configured in .env")
    
    user = TEST_USERS[role]
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    
    # Use password grant to authenticate as the test user
    payload = {
        "grant_type": "password",
        "username": user["email"],
        "password": user["password"],
        "audience": API_AUDIENCE,
        "client_id": AUTH0_CLIENT_ID,
        "realm": "Username-Password-Authentication"
    }
    
    try:
        response = requests.post(token_url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        # Check for specific Auth0 errors
        try:
            error_data = e.response.json()
            raise ValueError(f"Auth0 Error ({e.response.status_code}): {error_data.get('error_description', error_data.get('error', str(e)))}")
        except (ValueError, json.JSONDecodeError):
            raise ValueError(f"Failed to get token: {e}")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Network error: {e}")


def print_token(role: str):
    """Print token in a format suitable for copying to Postman"""
    try:
        token_data = get_token(role)
        
        print("\n" + "="*70)
        print(f"✓ JWT Token for {role.upper()}")
        print("="*70)
        print(f"\nAccess Token:\n")
        print(token_data['access_token'])
        
        print(f"\n\nToken Details:")
        print(f"  Type: {token_data.get('token_type', 'Bearer')}")
        print(f"  Expires in: {token_data.get('expires_in', 'unknown')} seconds")
        
        print(f"\n\nUsage in Postman:")
        print(f"  1. Copy the token above")
        print(f"  2. Go to request → Headers tab")
        print(f"  3. Add header: Authorization = Bearer <paste-token>")
        
        print(f"\n\nUsage in cURL:")
        print(f"  curl -H \"Authorization: Bearer {token_data['access_token'][:20]}...\" \\")
        print(f"    http://127.0.0.1:5000/drinks-detail")
        
        print("\n" + "="*70 + "\n")
        
        return token_data
        
    except ValueError as e:
        print(f"\n❌ Error: {e}\n", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python generate_token.py <role>")
        print("\nAvailable roles:")
        for role in TEST_USERS.keys():
            print(f"  • {role}")
        sys.exit(1)
    
    role = sys.argv[1].lower()
    
    if role not in TEST_USERS:
        print(f"Error: Unknown role '{role}'")
        print(f"Available roles: {', '.join(TEST_USERS.keys())}")
        sys.exit(1)
    
    print_token(role)


