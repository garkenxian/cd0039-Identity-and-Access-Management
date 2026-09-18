#!/usr/bin/env python3
"""
Quick test to verify /drinks-detail endpoint works with Auth0 tokens.
"""

import sys
import json
import requests
import subprocess
import time
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api import app
from src.database.models import setup_db, db, Drink

def get_auth0_token(role='barista'):
    """Get a JWT token from Auth0"""
    auth0_domain = 'dev-53bey634viqgnyzc.us.auth0.com'
    client_id = 'ofXDWA2aKqT3Wy5uKhWwAAx45VDLrgMr'
    client_secret = 'cauQsfbdnaxI5JthQ5nkjWPgLhExPbm80Mf0LgzFAvoLHuzh4uL6cca8pSouLp5x'
    
    credentials = {
        'barista': {
            'username': 'barista@test.local',
            'password': 'pEgJtK2*Ee6ubZj2'
        },
        'manager': {
            'username': 'manager@test.local',
            'password': 'TempPass123!Manager'
        }
    }
    
    cred = credentials.get(role)
    if not cred:
        print(f"ERROR: Unknown role '{role}'")
        return None
    
    payload = {
        'grant_type': 'password',
        'username': cred['username'],
        'password': cred['password'],
        'audience': 'coffee-shop-api',
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    try:
        response = requests.post(
            f'https://{auth0_domain}/oauth/token',
            json=payload
        )
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            print(f"ERROR: Auth0 returned {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def test_endpoint():
    """Test the /drinks-detail endpoint"""
    print("=" * 70)
    print("TESTING /drinks-detail ENDPOINT")
    print("=" * 70)
    print()
    
    # Check database
    print("1. Checking database...")
    with app.app_context():
        drinks = Drink.query.all()
        print(f"   ✓ Found {len(drinks)} drinks in database")
        if not drinks:
            print("   ERROR: Database is empty!")
            return False
    
    # Get token
    print()
    print("2. Getting Auth0 token for barista...")
    token = get_auth0_token('barista')
    if not token:
        print("   ERROR: Failed to get token")
        return False
    print(f"   ✓ Token obtained (first 50 chars): {token[:50]}...")
    
    # Test endpoint
    print()
    print("3. Testing /drinks-detail endpoint...")
    
    # Create test client
    with app.test_client() as client:
        response = client.get(
            '/drinks-detail',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            print(f"   ✓ Status: {response.status_code}")
            data = response.get_json()
            print(f"   ✓ Response: success={data.get('success')}, drinks count={len(data.get('drinks', []))}")
            
            if data.get('drinks'):
                for drink in data['drinks'][:3]:
                    print(f"     - {drink.get('title')}")
            return True
        else:
            print(f"   ✗ Status: {response.status_code}")
            print(f"   ✗ Response: {response.get_data(as_text=True)}")
            return False

if __name__ == '__main__':
    try:
        success = test_endpoint()
        print()
        print("=" * 70)
        if success:
            print("✓✓✓ ENDPOINT TEST PASSED ✓✓✓")
        else:
            print("✗✗✗ ENDPOINT TEST FAILED ✗✗✗")
        print("=" * 70)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
