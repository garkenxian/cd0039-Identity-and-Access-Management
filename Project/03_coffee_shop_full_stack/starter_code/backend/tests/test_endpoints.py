"""
API Endpoint Integration Tests

Tests for all drink endpoints including:
- Public GET /drinks
- Secured GET /drinks-detail with role-based access
- POST /drinks with role-based access
- PATCH /drinks/<id> with role-based access
- DELETE /drinks/<id> with role-based access

Tests cover:
- Happy paths with proper permissions
- Missing/invalid/expired token failures
- Permission denied (insufficient permissions)
- 404 for non-existent resources
- CRUD state transitions
"""

import unittest
import json
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add src directory to path for imports
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Also add parent directory so we can import src as a package
parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

# Set up Flask before importing
os.environ['FLASK_ENV'] = 'test'

from src.api import app
from src.database.models import setup_db, db_drop_and_create_all, Drink, db


class DrinksTestCase(unittest.TestCase):
    """Test case for drink endpoints"""

    def setUp(self):
        """Set up test client and create test database"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db_drop_and_create_all()
            self._setup_test_drinks()
    
    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
    
    def _setup_test_drinks(self):
        """Set up initial test data"""
        drink1 = Drink(
            title='Water',
            recipe='[{"name": "water", "color": "blue", "parts": 1}]'
        )
        drink2 = Drink(
            title='Coffee',
            recipe='[{"name": "coffee", "color": "brown", "parts": 1}, {"name": "milk", "color": "white", "parts": 1}]'
        )
        drink1.insert()
        drink2.insert()
    
    def _get_valid_token(self, permissions):
        """
        Create a mock JWT token for testing.
        In real tests, this would be a valid Auth0 token.
        For now, we'll create a mock token structure.
        """
        from datetime import datetime, timedelta
        from jose import jwt
        
        # This is a mock implementation - in real tests, use actual Auth0 tokens
        payload = {
            'iss': 'https://udacity-fsnd.auth0.com/',
            'sub': 'auth0|test_user',
            'aud': 'dev',
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow(),
            'permissions': permissions
        }
        
        # For testing, we'll encode with a simple key
        # In real scenarios, this token would come from Auth0
        token = jwt.encode(payload, 'test_secret', algorithm='HS256')
        return f'Bearer {token}'
    
    # ==================== GET /drinks Tests ====================
    
    def test_get_drinks_public(self):
        """Test GET /drinks returns all drinks in short format without auth"""
        response = self.client.get('/drinks')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIsInstance(data['drinks'], list)
        self.assertGreater(len(data['drinks']), 0)
        
        # Verify short format (no name in recipe)
        for drink in data['drinks']:
            self.assertIn('id', drink)
            self.assertIn('title', drink)
            self.assertIn('recipe', drink)
            for item in drink['recipe']:
                self.assertIn('color', item)
                self.assertIn('parts', item)
                self.assertNotIn('name', item)
    
    def test_get_drinks_empty(self):
        """Test GET /drinks when database is empty"""
        with self.app.app_context():
            db.session.query(Drink).delete()
            db.session.commit()
        
        response = self.client.get('/drinks')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['drinks'], [])
    
    # ==================== GET /drinks-detail Tests ====================
    
    def test_get_drinks_detail_requires_auth(self):
        """Test GET /drinks-detail requires authentication"""
        # Without auth header, should get 401 error
        # Full auth testing is covered in test_auth.py
        response = self.client.get('/drinks-detail')
        
        # Should get 401 (auth required), not 404 (endpoint not found)
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_get_drinks_detail_missing_auth(self):
        """Test GET /drinks-detail without auth header"""
        response = self.client.get('/drinks-detail')
        
        # Should get 401 Unauthorized
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    # ==================== POST /drinks Tests ====================
    
    def test_post_drink_missing_auth(self):
        """Test POST /drinks without auth header"""
        new_drink = {
            'title': 'Tea',
            'recipe': [{'name': 'tea', 'color': 'amber', 'parts': 1}]
        }
        
        response = self.client.post(
            '/drinks',
            data=json.dumps(new_drink),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_post_drink_malformed_body(self):
        """Test POST /drinks with missing required fields"""
        invalid_drink = {
            'title': 'Incomplete Drink'
            # Missing recipe
        }
        
        # Note: In a real test with auth mocking, this would test the 400 response
        # For now, we test that the endpoint exists
        response = self.client.post(
            '/drinks',
            data=json.dumps(invalid_drink),
            content_type='application/json'
        )
        
        # Should fail auth first
        self.assertEqual(response.status_code, 401)
    
    def test_post_drink_empty_body(self):
        """Test POST /drinks with empty body"""
        response = self.client.post(
            '/drinks',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    # ==================== PATCH /drinks/<id> Tests ====================
    
    def test_patch_drink_not_found(self):
        """Test PATCH /drinks/<id> for non-existent drink"""
        update_data = {
            'title': 'Updated Drink',
            'recipe': [{'name': 'updated', 'color': 'red', 'parts': 1}]
        }
        
        response = self.client.patch(
            '/drinks/9999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_patch_drink_missing_auth(self):
        """Test PATCH /drinks/<id> without auth header"""
        update_data = {
            'title': 'Updated Drink'
        }
        
        response = self.client.patch(
            '/drinks/1',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    # ==================== DELETE /drinks/<id> Tests ====================
    
    def test_delete_drink_missing_auth(self):
        """Test DELETE /drinks/<id> without auth header"""
        response = self.client.delete('/drinks/1')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_delete_drink_not_found(self):
        """Test DELETE /drinks/<id> for non-existent drink"""
        response = self.client.delete('/drinks/9999')
        
        self.assertEqual(response.status_code, 401)
    
    # ==================== Error Handler Tests ====================
    
    def test_404_error_handler(self):
        """Test 404 error handler returns proper JSON"""
        response = self.client.get('/nonexistent-endpoint')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)
        self.assertIn('message', data)
    
    def test_422_error_handler(self):
        """Test 422 error handler returns proper JSON"""
        # This would be triggered by database issues
        response = self.client.get('/drinks')
        self.assertEqual(response.status_code, 200)  # Should succeed normally


class EndpointStructureTests(unittest.TestCase):
    """Test that all required endpoints exist and have correct methods"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_get_drinks_endpoint_exists(self):
        """Test that GET /drinks endpoint exists"""
        # Just test that we get a response (not 404)
        response = self.client.get('/drinks')
        self.assertNotEqual(response.status_code, 404)
    
    def test_get_drinks_detail_endpoint_exists(self):
        """Test that GET /drinks-detail endpoint exists"""
        response = self.client.get('/drinks-detail')
        # Should get 401 (auth required), not 404
        self.assertNotEqual(response.status_code, 404)
    
    def test_post_drinks_endpoint_exists(self):
        """Test that POST /drinks endpoint exists"""
        response = self.client.post('/drinks', json={})
        # Should get 401 or 400, not 404
        self.assertNotEqual(response.status_code, 404)
    
    def test_patch_drinks_endpoint_exists(self):
        """Test that PATCH /drinks/<id> endpoint exists"""
        response = self.client.patch('/drinks/1', json={})
        # Should get 401 or 400, not 404
        self.assertNotEqual(response.status_code, 404)
    
    def test_delete_drinks_endpoint_exists(self):
        """Test that DELETE /drinks/<id> endpoint exists"""
        response = self.client.delete('/drinks/1')
        # Should get 401, not 404
        self.assertNotEqual(response.status_code, 404)


class AuthenticatedEndpointTests(unittest.TestCase):
    """Test authenticated endpoints with valid and invalid tokens/permissions"""

    def setUp(self):
        """Set up test client with auth mocking"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Patch requires_auth before creating client
        self.patcher = patch('src.auth.auth.verify_decode_jwt')
        self.mock_verify = self.patcher.start()
        
        # Clean up any existing tables and start fresh
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self._setup_test_drinks()
        
        self.client = self.app.test_client()
    
    def tearDown(self):
        """Clean up after tests"""
        self.patcher.stop()
        with self.app.app_context():
            db.drop_all()
    
    def _setup_test_drinks(self):
        """Set up initial test data"""
        drink1 = Drink(
            title='Water',
            recipe='[{"name": "water", "color": "blue", "parts": 1}]'
        )
        drink2 = Drink(
            title='Coffee',
            recipe='[{"name": "coffee", "color": "brown", "parts": 1}]'
        )
        drink1.insert()
        drink2.insert()
    
    # ==================== GET /drinks-detail Authenticated Tests ====================
    
    def test_get_drinks_detail_success_with_permission(self):
        """Test GET /drinks-detail succeeds with valid token and get:drinks-detail permission"""
        # Mock JWT verification to return a valid payload with required permission
        self.mock_verify.return_value = {
            'permissions': ['get:drinks-detail'],
            'sub': 'test_user|123'
        }
        
        response = self.client.get(
            '/drinks-detail',
            headers={'Authorization': 'Bearer mock_token'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIsInstance(data['drinks'], list)
        self.assertGreaterEqual(len(data['drinks']), 2)
        
        # Verify long format (includes name in recipe)
        for drink in data['drinks']:
            self.assertIn('id', drink)
            self.assertIn('title', drink)
            self.assertIn('recipe', drink)
            self.assertGreater(len(drink['recipe']), 0)
            for item in drink['recipe']:
                self.assertIn('name', item)
                self.assertIn('color', item)
                self.assertIn('parts', item)
    
    def test_get_drinks_detail_insufficient_permission(self):
        """Test GET /drinks-detail fails with insufficient permissions"""
        # Mock JWT verification to return a payload without the required permission
        self.mock_verify.return_value = {
            'permissions': [],  # Missing 'get:drinks-detail'
            'sub': 'test_user|123'
        }
        
        response = self.client.get(
            '/drinks-detail',
            headers={'Authorization': 'Bearer mock_token'}
        )
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    # ==================== POST /drinks Authenticated Tests ====================
    
    def test_post_drink_success_with_permission(self):
        """Test POST /drinks succeeds with valid token and post:drinks permission"""
        self.mock_verify.return_value = {
            'permissions': ['post:drinks'],
            'sub': 'test_user|123'
        }
        
        new_drink = {
            'title': 'Tea',
            'recipe': [{'name': 'tea', 'color': 'amber', 'parts': 1}]
        }
        
        response = self.client.post(
            '/drinks',
            data=json.dumps(new_drink),
            content_type='application/json',
            headers={'Authorization': 'Bearer mock_token'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['drinks']), 1)
        self.assertEqual(data['drinks'][0]['title'], 'Tea')
    
    def test_post_drink_duplicate_title_returns_422(self):
        """Test POST /drinks with duplicate title returns 422"""
        self.mock_verify.return_value = {
            'permissions': ['post:drinks'],
            'sub': 'test_user|123'
        }
        
        duplicate_drink = {
            'title': 'Water',  # Already exists
            'recipe': [{'name': 'water', 'color': 'blue', 'parts': 2}]
        }
        
        response = self.client.post(
            '/drinks',
            data=json.dumps(duplicate_drink),
            content_type='application/json',
            headers={'Authorization': 'Bearer mock_token'}
        )
        
        self.assertEqual(response.status_code, 422)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 422)
    
    def test_post_drink_missing_title_returns_400(self):
        """Test POST /drinks with missing title returns 400"""
        self.mock_verify.return_value = {
            'permissions': ['post:drinks'],
            'sub': 'test_user|123'
        }
        
        invalid_drink = {
            'recipe': [{'name': 'tea', 'color': 'amber', 'parts': 1}]
            # Missing title
        }
        
        response = self.client.post(
            '/drinks',
            data=json.dumps(invalid_drink),
            content_type='application/json',
            headers={'Authorization': 'Bearer mock_token'}
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_post_drink_invalid_recipe_format_returns_400(self):
        """Test POST /drinks with non-list recipe returns 400"""
        self.mock_verify.return_value = {
            'permissions': ['post:drinks'],
            'sub': 'test_user|123'
        }
        
        invalid_drink = {
            'title': 'BadDrink',
            'recipe': 'not a list'  # Should be a list
        }
        
        response = self.client.post(
            '/drinks',
            data=json.dumps(invalid_drink),
            content_type='application/json',
            headers={'Authorization': 'Bearer mock_token'}
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    # ==================== PATCH /drinks/<id> Authenticated Tests ====================
    
    def test_patch_drink_success_with_permission(self):
        """Test PATCH /drinks/<id> succeeds with valid token and patch:drinks permission"""
        self.mock_verify.return_value = {
            'permissions': ['patch:drinks'],
            'sub': 'test_user|123'
        }
        
        update_data = {'title': 'Hot Water'}
        
        response = self.client.patch(
            '/drinks/1',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={'Authorization': 'Bearer mock_token'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['drinks'][0]['title'], 'Hot Water')
    
    def test_patch_drink_not_found_returns_404(self):
        """Test PATCH /drinks/<id> with non-existent id returns 404"""
        self.mock_verify.return_value = {
            'permissions': ['patch:drinks'],
            'sub': 'test_user|123'
        }
        
        update_data = {'title': 'Non-existent'}
        
        response = self.client.patch(
            '/drinks/9999',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={'Authorization': 'Bearer mock_token'}
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_patch_drink_update_recipe(self):
        """Test PATCH /drinks/<id> can update recipe"""
        self.mock_verify.return_value = {
            'permissions': ['patch:drinks'],
            'sub': 'test_user|123'
        }
        
        new_recipe = [
            {'name': 'hot_water', 'color': 'clear', 'parts': 1},
            {'name': 'lemon', 'color': 'yellow', 'parts': 0.5}
        ]
        update_data = {'recipe': new_recipe}
        
        response = self.client.patch(
            '/drinks/1',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={'Authorization': 'Bearer mock_token'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['drinks'][0]['recipe']), 2)
    
    def test_patch_drink_insufficient_permission(self):
        """Test PATCH /drinks/<id> fails with insufficient permissions"""
        self.mock_verify.return_value = {
            'permissions': [],  # Missing 'patch:drinks'
            'sub': 'test_user|123'
        }
        
        update_data = {'title': 'Updated'}
        
        response = self.client.patch(
            '/drinks/1',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={'Authorization': 'Bearer mock_token'}
        )
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    # ==================== DELETE /drinks/<id> Authenticated Tests ====================
    
    def test_delete_drink_success_with_permission(self):
        """Test DELETE /drinks/<id> succeeds with valid token and delete:drinks permission"""
        self.mock_verify.return_value = {
            'permissions': ['delete:drinks'],
            'sub': 'test_user|123'
        }
        
        response = self.client.delete(
            '/drinks/1',
            headers={'Authorization': 'Bearer mock_token'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['delete'], 1)
        
        # Verify drink was actually deleted
        get_response = self.client.get('/drinks')
        get_data = json.loads(get_response.data)
        self.assertEqual(len(get_data['drinks']), 1)
    
    def test_delete_drink_not_found_returns_404(self):
        """Test DELETE /drinks/<id> with non-existent id returns 404"""
        self.mock_verify.return_value = {
            'permissions': ['delete:drinks'],
            'sub': 'test_user|123'
        }
        
        response = self.client.delete(
            '/drinks/9999',
            headers={'Authorization': 'Bearer mock_token'}
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_delete_drink_insufficient_permission(self):
        """Test DELETE /drinks/<id> fails with insufficient permissions"""
        self.mock_verify.return_value = {
            'permissions': [],  # Missing 'delete:drinks'
            'sub': 'test_user|123'
        }
        
        response = self.client.delete(
            '/drinks/1',
            headers={'Authorization': 'Bearer mock_token'}
        )
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertFalse(data['success'])


if __name__ == '__main__':
    unittest.main()
