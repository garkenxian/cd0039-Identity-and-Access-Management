#!/usr/bin/env python3
"""
Auth0 Test Token Generator

Generate JWT tokens for test users to use in Postman testing.

Usage:
    python generate_token.py barista    # Generate barista token
    python generate_token.py manager    # Generate manager token
"""

import os
import sys
import json
import requests

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
    """Generate JWT token for test user"""
    
    if role not in TEST_USERS:
        raise ValueError(f"Invalid role '{role}'. Must be 'barista' or 'manager'")
    
    if not AUTH0_CLIENT_ID:
        return {
            "error": "AUTH0_CLIENT_ID not configured",
            "message": "Run 'make auth0-init' to set up Auth0"
        }
    
    user = TEST_USERS[role]
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    
    payload = {
        "grant_type": "http://auth0.com/oauth/grant-type/passwordless/otp",
        "username": user["email"],
        "password": user["password"],
        "audience": API_AUDIENCE,
        "client_id": AUTH0_CLIENT_ID,
        "realm": "Username-Password-Authentication"
    }
    
    try:
        response = requests.post(token_url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python generate_token.py <role>")
        print("  barista  - Generate token for barista user")
        print("  manager  - Generate token for manager user")
        sys.exit(1)
    
    role = sys.argv[1].lower()
    
    try:
        token_response = get_token(role)
        
        if "error" in token_response:
            print(f"Error: {token_response.get('message', token_response['error'])}")
            sys.exit(1)
        
        print(json.dumps(token_response, indent=2))
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
