"""
Auth0 Token Generator for Testing

Generates JWT tokens for test users via Auth0's Resource Owner Password Grant.
"""

import os
import requests
from typing import Dict, Optional


class TokenGenerator:
    """Generate JWT tokens from Auth0 for testing"""
    
    # Auth0 Test User Credentials
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
    
    def __init__(self):
        """Initialize token generator with Auth0 config"""
        self.domain = os.getenv('AUTH0_DOMAIN', 'dev-53bey634viqgnyzc.us.auth0.com')
        self.client_id = os.getenv('AUTH0_CLIENT_ID')
        self.audience = os.getenv('API_AUDIENCE', 'coffee-shop-api')
    
    def get_token(self, role: str) -> Optional[Dict]:
        """
        Get a JWT token for a test user.
        
        Args:
            role (str): Either 'barista' or 'manager'
        
        Returns:
            dict: Token response with 'access_token', 'token_type', 'expires_in'
            None: If token generation fails
        
        Raises:
            ValueError: If role is not valid
        """
        if role not in self.TEST_USERS:
            raise ValueError(f"Invalid role '{role}'. Must be 'barista' or 'manager'")
        
        user = self.TEST_USERS[role]
        
        # For development/testing: if AUTH0_CLIENT_ID is not set, 
        # return a message about setup
        if not self.client_id:
            return {
                "error": "AUTH0_CLIENT_ID not configured",
                "message": "Run 'make auth0-init' to set up Auth0 and configure credentials"
            }
        
        token_url = f"https://{self.domain}/oauth/token"
        
        payload = {
            "grant_type": "http://auth0.com/oauth/grant-type/passwordless/otp",
            "username": user["email"],
            "password": user["password"],
            "audience": self.audience,
            "client_id": self.client_id,
            "realm": "Username-Password-Authentication"
        }
        
        try:
            response = requests.post(token_url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": "token_request_failed",
                "message": str(e)
            }


# Module-level function for convenience
def get_test_token(role: str) -> Optional[Dict]:
    """
    Quick access function to get a test token.
    
    Args:
        role (str): Either 'barista' or 'manager'
    
    Returns:
        dict: Token response or error details
    """
    generator = TokenGenerator()
    return generator.get_token(role)
