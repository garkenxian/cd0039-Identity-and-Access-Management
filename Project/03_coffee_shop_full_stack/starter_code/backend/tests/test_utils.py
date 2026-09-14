"""
Utilities and fixtures for testing auth-decorated endpoints

This module provides helper functions to test endpoints that require authentication
without needing full Auth0 mocking complexity.
"""

import json
from functools import wraps
from flask import Flask

def create_test_app_with_mock_auth():
    """
    Create a test app where auth decorators are mocked.
    This allows testing endpoint business logic without Auth0.
    """
    from src.api import app as original_app
    
    # Store original requires_auth
    from src import auth
    original_requires_auth = auth.requires_auth
    
    # Create mock decorator
    def mock_requires_auth(permission=''):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                # Pass mock payload to decorated function
                mock_payload = {
                    'sub': 'test_user_123',
                    'permissions': [
                        'get:drinks',
                        'get:drinks-detail',
                        'post:drinks',
                        'patch:drinks',
                        'delete:drinks'
                    ]
                }
                return f(mock_payload, *args, **kwargs)
            return wrapper
        return decorator
    
    # Temporarily replace requires_auth
    auth.requires_auth = mock_requires_auth
    
    # Re-import api to use mocked auth
    import importlib
    import sys
    if 'src.api' in sys.modules:
        del sys.modules['src.api']
    
    from src import api
    
    # Restore original (though new imports will use mocked version)
    auth.requires_auth = original_requires_auth
    
    return api.app


def mock_auth_response(payload=None):
    """
    Create a mock authentication payload for testing.
    
    Args:
        payload: Optional dict to merge with default mock payload
    
    Returns:
        dict: Mock JWT payload
    """
    mock_payload = {
        'sub': 'test_user_123',
        'iss': 'https://test.auth0.com/',
        'aud': 'test-api',
        'permissions': [
            'get:drinks',
            'get:drinks-detail',
            'post:drinks',
            'patch:drinks',
            'delete:drinks'
        ]
    }
    
    if payload:
        mock_payload.update(payload)
    
    return mock_payload
