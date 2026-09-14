"""
Auth Module Unit Tests

Tests for JWT token parsing, verification, and permission checking.
Covers both happy paths and expected failure modes.
"""

import unittest
import json
from unittest.mock import patch, MagicMock, mock_open
from jose import jwt as jose_jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from datetime import datetime, timedelta
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from flask import Flask


class TestGetTokenAuthHeader(unittest.TestCase):
    """Tests for get_token_auth_header function"""

    def setUp(self):
        """Set up test fixtures with Flask app"""
        self.app = Flask(__name__)

    def test_valid_bearer_token(self):
        """Test extraction of valid Bearer token"""
        from auth.auth import get_token_auth_header
        
        with self.app.test_request_context(headers={'Authorization': 'Bearer valid_token_string'}):
            token = get_token_auth_header()
            self.assertEqual(token, 'valid_token_string')

    def test_missing_authorization_header(self):
        """Test that missing Authorization header raises AuthError"""
        from auth.auth import get_token_auth_header, AuthError
        
        with self.app.test_request_context():
            with self.assertRaises(AuthError) as context:
                get_token_auth_header()
            
            self.assertEqual(context.exception.status_code, 401)
            self.assertEqual(context.exception.error['code'], 'authorization_header_missing')

    def test_malformed_header_no_bearer(self):
        """Test that non-Bearer header raises AuthError"""
        from auth.auth import get_token_auth_header, AuthError
        
        with self.app.test_request_context(headers={'Authorization': 'Basic some_token'}):
            with self.assertRaises(AuthError) as context:
                get_token_auth_header()
            
            self.assertEqual(context.exception.status_code, 401)
            self.assertEqual(context.exception.error['code'], 'invalid_header')

    def test_malformed_header_no_token(self):
        """Test that Bearer without token raises AuthError"""
        from auth.auth import get_token_auth_header, AuthError
        
        with self.app.test_request_context(headers={'Authorization': 'Bearer'}):
            with self.assertRaises(AuthError) as context:
                get_token_auth_header()
            
            self.assertEqual(context.exception.status_code, 401)
            self.assertEqual(context.exception.error['code'], 'invalid_header')

    def test_malformed_header_too_many_parts(self):
        """Test that too many parts in header raises AuthError"""
        from auth.auth import get_token_auth_header, AuthError
        
        with self.app.test_request_context(headers={'Authorization': 'Bearer token extra part'}):
            with self.assertRaises(AuthError) as context:
                get_token_auth_header()
            
            self.assertEqual(context.exception.status_code, 401)
            self.assertEqual(context.exception.error['code'], 'invalid_header')


class TestCheckPermissions(unittest.TestCase):
    """Tests for check_permissions function"""

    def test_permission_present_in_payload(self):
        """Test that valid permission passes check"""
        from auth.auth import check_permissions
        
        payload = {
            'permissions': ['get:drinks', 'post:drinks']
        }
        result = check_permissions('get:drinks', payload)
        self.assertTrue(result)

    def test_missing_permissions_claim(self):
        """Test that missing permissions claim raises AuthError"""
        from auth.auth import check_permissions, AuthError
        
        payload = {'sub': 'user123'}
        with self.assertRaises(AuthError) as context:
            check_permissions('get:drinks', payload)
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.error['code'], 'invalid_claims')

    def test_permission_not_in_payload(self):
        """Test that missing required permission raises AuthError"""
        from auth.auth import check_permissions, AuthError
        
        payload = {
            'permissions': ['get:drinks']
        }
        with self.assertRaises(AuthError) as context:
            check_permissions('delete:drinks', payload)
        
        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.error['code'], 'insufficient_permissions')

    def test_empty_permissions_array(self):
        """Test that empty permissions array raises AuthError"""
        from auth.auth import check_permissions, AuthError
        
        payload = {
            'permissions': []
        }
        with self.assertRaises(AuthError) as context:
            check_permissions('get:drinks', payload)
        
        self.assertEqual(context.exception.status_code, 403)


class TestVerifyDecodeJwt(unittest.TestCase):
    """Tests for verify_decode_jwt function"""

    @patch('auth.auth.urlopen')
    @patch('auth.auth.jwt')
    def test_valid_token(self, mock_jose_jwt, mock_urlopen):
        """Test successful token verification and decoding"""
        from auth.auth import verify_decode_jwt
        
        # Mock JWKS response
        jwks_data = {
            'keys': [
                {
                    'kid': 'test_kid_123',
                    'use': 'sig',
                    'n': 'test_n_value',
                    'e': 'AQAB',
                    'kty': 'RSA'
                }
            ]
        }
        mock_urlopen.return_value.read.return_value = json.dumps(jwks_data).encode()
        
        # Mock JWT header and decode
        mock_jose_jwt.get_unverified_header.return_value = {'kid': 'test_kid_123'}
        expected_payload = {
            'sub': 'user123',
            'aud': 'coffee-shop-api',
            'iss': 'https://test.auth0.com/',
            'permissions': ['get:drinks']
        }
        mock_jose_jwt.decode.return_value = expected_payload
        
        token = 'test_token_string'
        result = verify_decode_jwt(token)
        
        self.assertEqual(result, expected_payload)

    @patch('auth.auth.jwt')
    def test_missing_kid_in_header(self, mock_jose_jwt):
        """Test that token without kid raises AuthError"""
        from auth.auth import verify_decode_jwt, AuthError
        
        mock_jose_jwt.get_unverified_header.return_value = {}
        
        with self.assertRaises(AuthError) as context:
            verify_decode_jwt('test_token')
        
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.error['code'], 'invalid_header')

    @patch('auth.auth.urlopen')
    @patch('auth.auth.jwt')
    def test_expired_token(self, mock_jose_jwt, mock_urlopen):
        """Test that expired token raises AuthError"""
        from auth.auth import verify_decode_jwt, AuthError
        
        # Mock JWKS response
        jwks_data = {'keys': [{'kid': 'test_kid', 'n': 'test', 'e': 'AQAB'}]}
        mock_urlopen.return_value.read.return_value = json.dumps(jwks_data).encode()
        
        # Mock JWT header
        mock_jose_jwt.get_unverified_header.return_value = {'kid': 'test_kid'}
        
        # Mock expired token error
        mock_jose_jwt.decode.side_effect = ExpiredSignatureError()
        
        with self.assertRaises(AuthError) as context:
            verify_decode_jwt('expired_token')
        
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.error['code'], 'token_expired')

    @patch('auth.auth.urlopen')
    @patch('auth.auth.jwt')
    def test_invalid_claims(self, mock_jose_jwt, mock_urlopen):
        """Test that invalid claims raise AuthError"""
        from auth.auth import verify_decode_jwt, AuthError
        
        # Mock JWKS response
        jwks_data = {'keys': [{'kid': 'test_kid', 'n': 'test', 'e': 'AQAB'}]}
        mock_urlopen.return_value.read.return_value = json.dumps(jwks_data).encode()
        
        # Mock JWT header
        mock_jose_jwt.get_unverified_header.return_value = {'kid': 'test_kid'}
        
        # Mock JWT claims error (audience/issuer mismatch)
        mock_jose_jwt.decode.side_effect = JWTClaimsError('Invalid claims')
        
        with self.assertRaises(AuthError) as context:
            verify_decode_jwt('invalid_claims_token')
        
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.error['code'], 'invalid_claims')

    @patch('auth.auth.urlopen')
    @patch('auth.auth.jwt')
    def test_kid_not_found_in_jwks(self, mock_jose_jwt, mock_urlopen):
        """Test that kid not found in JWKS raises AuthError"""
        from auth.auth import verify_decode_jwt, AuthError
        
        # Mock JWKS with different kid
        jwks_data = {
            'keys': [
                {
                    'kid': 'other_kid',
                    'n': 'test',
                    'e': 'AQAB'
                }
            ]
        }
        mock_urlopen.return_value.read.return_value = json.dumps(jwks_data).encode()
        
        # Mock JWT header with different kid
        mock_jose_jwt.get_unverified_header.return_value = {'kid': 'not_found_kid'}
        
        with self.assertRaises(AuthError) as context:
            verify_decode_jwt('token_with_unknown_kid')
        
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.error['code'], 'invalid_header')


class TestIntegration(unittest.TestCase):
    """Integration tests for auth flow"""

    def setUp(self):
        """Set up test fixtures with Flask app"""
        self.app = Flask(__name__)

    @patch('auth.auth.urlopen')
    @patch('auth.auth.jwt')
    def test_complete_auth_flow_barista(self, mock_jose_jwt, mock_urlopen):
        """Test complete auth flow with barista permissions"""
        from auth.auth import (
            get_token_auth_header,
            verify_decode_jwt,
            check_permissions
        )
        
        with self.app.test_request_context(headers={'Authorization': 'Bearer valid_token'}):
            # Step 1: Valid bearer token
            token = get_token_auth_header()
            self.assertEqual(token, 'valid_token')
            
            # Step 2: Mock JWKS and token verification
            jwks_data = {'keys': [{'kid': 'key1', 'n': 'test', 'e': 'AQAB'}]}
            mock_urlopen.return_value.read.return_value = json.dumps(jwks_data).encode()
            
            mock_jose_jwt.get_unverified_header.return_value = {'kid': 'key1'}
            barista_payload = {
                'sub': 'barista123',
                'aud': 'coffee-shop-api',
                'iss': 'https://test.auth0.com/',
                'permissions': ['get:drinks', 'get:drinks-detail']
            }
            mock_jose_jwt.decode.return_value = barista_payload
            
            payload = verify_decode_jwt(token)
            self.assertEqual(payload['sub'], 'barista123')
            
            # Step 3: Check permissions
            self.assertTrue(check_permissions('get:drinks-detail', payload))

    @patch('auth.auth.urlopen')
    @patch('auth.auth.jwt')
    def test_complete_auth_flow_insufficient_permissions(self, mock_jose_jwt, mock_urlopen):
        """Test auth flow with insufficient permissions"""
        from auth.auth import (
            get_token_auth_header,
            verify_decode_jwt,
            check_permissions,
            AuthError
        )
        
        with self.app.test_request_context(headers={'Authorization': 'Bearer barista_token'}):
            # Step 1: Valid bearer token
            token = get_token_auth_header()
            
            # Step 2: Mock verification with barista permissions
            jwks_data = {'keys': [{'kid': 'key1', 'n': 'test', 'e': 'AQAB'}]}
            mock_urlopen.return_value.read.return_value = json.dumps(jwks_data).encode()
            
            mock_jose_jwt.get_unverified_header.return_value = {'kid': 'key1'}
            barista_payload = {
                'sub': 'barista123',
                'permissions': ['get:drinks', 'get:drinks-detail']
            }
            mock_jose_jwt.decode.return_value = barista_payload
            
            payload = verify_decode_jwt(token)
            
            # Step 3: Barista tries to post drinks (should fail)
            with self.assertRaises(AuthError) as context:
                check_permissions('post:drinks', payload)
            
            self.assertEqual(context.exception.status_code, 403)


if __name__ == '__main__':
    unittest.main()
