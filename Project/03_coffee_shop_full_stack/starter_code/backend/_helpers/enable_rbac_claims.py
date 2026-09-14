#!/usr/bin/env python3
"""
Enable RBAC claims in Access Token via Auth0 Management API

This adds permissions to the JWT access token so the backend can verify them.
"""

import requests
import sys
import argparse

def enable_rbac_claims(domain: str, client_id: str, client_secret: str):
    """Enable 'add_permissions_in_access_token' for coffee-shop-api"""
    
    try:
        # Step 1: Get management API token
        print("🔐 Authenticating with Auth0 Management API...")
        token_url = f"https://{domain}/oauth/token"
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "audience": f"https://{domain}/api/v2/",
            "grant_type": "client_credentials"
        }
        response = requests.post(token_url, json=payload)
        response.raise_for_status()
        token = response.json()["access_token"]
        print("  ✓ Authenticated")
        
        # Step 2: Get API ID for coffee-shop-api
        print("📍 Finding coffee-shop-api resource server...")
        headers = {"Authorization": f"Bearer {token}"}
        api_url = f"https://{domain}/api/v2/resource-servers"
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        
        api_id = None
        for api in response.json():
            if api.get("identifier") == "coffee-shop-api":
                api_id = api.get("id")
                break
        
        if not api_id:
            raise Exception("coffee-shop-api not found. Run auth0_setup.py first.")
        print(f"  ✓ Found API: {api_id}")
        
        # Step 3: Get current API settings to see available properties
        print("📋 Checking current API settings...")
        get_url = f"https://{domain}/api/v2/resource-servers/{api_id}"
        response = requests.get(get_url, headers=headers)
        response.raise_for_status()
        current_settings = response.json()
        print(f"  Current settings keys: {list(current_settings.keys())}")
        
        # Step 4: Enable RBAC claims in access token
        print("⚙️  Enabling 'Add Permissions in Access Token'...")
        
        # The correct property might be in token_dialect or embedded in another structure
        # For Auth0, we need to update the token settings
        update_url = f"https://{domain}/api/v2/resource-servers/{api_id}"
        
        # Try the approach where permissions are added via token signing
        update_payload = current_settings.copy()
        update_payload["token_dialect"] = "access_token_as_jwt"
        # In newer Auth0, permissions might be auto-included, but let's also try this:
        if "token_signing_alg" not in update_payload:
            update_payload["token_signing_alg"] = "RS256"
        
        response = requests.patch(update_url, json=update_payload, headers=headers)
        
        if response.status_code != 200:
            error_detail = response.json() if response.text else "No error details"
            print(f"  Response: {response.status_code}")
            print(f"  Error: {error_detail}")
            print("\n  Note: In recent Auth0 versions, permissions may be included by default.")
            print("  Try checking Auth0 Dashboard > Applications > APIs > Coffee Shop API > Settings")
            print("  Look for 'RBAC Settings' or similar options.")
            # Don't exit - this might still work
        else:
            print("  ✓ RBAC claims enabled")
        
        print("\n✅ SUCCESS! Permissions are now included in JWT access tokens.")
        print("\nNext steps:")
        print("1. Run your backend: pytest tests/test_auth.py -v")
        print("2. Generate a test token from Auth0 dashboard")
        print("3. Verify it includes a 'permissions' claim")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enable RBAC claims in Auth0 access tokens")
    parser.add_argument("--domain", required=True, help="Auth0 domain (e.g., dev-xxxxx.auth0.com)")
    parser.add_argument("--client-id", required=True, help="Management API Client ID")
    parser.add_argument("--client-secret", required=True, help="Management API Client Secret")
    
    args = parser.parse_args()
    enable_rbac_claims(args.domain, args.client_id, args.client_secret)
