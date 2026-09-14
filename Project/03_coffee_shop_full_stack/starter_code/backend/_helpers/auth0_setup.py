#!/usr/bin/env python3
"""
Auth0 Setup Automation Script

Automates the creation of API, permissions, roles, and test users in Auth0.

PREREQUISITES:
1. Auth0 account created at auth0.com
2. Tenant created (you'll have a domain: xxxxx.auth0.com)
3. Management API credentials obtained:
   - Create an application in Auth0 for "Auth0 Management API"
   - Grant it "Management API" access with required scopes
   - Copy Client ID and Client Secret

USAGE:
    python auth0_setup.py \\
        --domain your-tenant.auth0.com \\
        --client-id YOUR_MANAGEMENT_API_CLIENT_ID \\
        --client-secret YOUR_MANAGEMENT_API_CLIENT_SECRET

OUTPUT:
    Creates .env file with configuration values ready to use
"""

import argparse
import json
import sys
import os
import requests
from typing import Dict, Optional

try:
    from auth0.management import Auth0
except ImportError:
    print("ERROR: auth0 package not found.")
    print("Install it with: pip install auth0-python")
    sys.exit(1)


class Auth0Setup:
    """Handles Auth0 tenant configuration"""

    # Configuration constants
    API_IDENTIFIER = "coffee-shop-api"
    API_NAME = "Coffee Shop API"
    
    PERMISSIONS = [
        {"name": "get:drinks", "description": "View drink list"},
        {"name": "get:drinks-detail", "description": "View drink details/recipes"},
        {"name": "post:drinks", "description": "Create drinks"},
        {"name": "patch:drinks", "description": "Update drinks"},
        {"name": "delete:drinks", "description": "Delete drinks"},
    ]
    
    ROLES = {
        "barista": {
            "name": "barista",
            "description": "Barista can view drink details and recipes",
            "permissions": ["get:drinks", "get:drinks-detail"]
        },
        "manager": {
            "name": "manager",
            "description": "Manager can manage all drinks (create, read, update, delete)",
            "permissions": ["get:drinks", "get:drinks-detail", "post:drinks", "patch:drinks", "delete:drinks"]
        }
    }
    
    TEST_USERS = {
        "barista": {
            "email": "barista@test.local",
            "password": None,  # Will be generated
            "connection": "Username-Password-Authentication",
            "role": "barista"
        },
        "manager": {
            "email": "manager@test.local",
            "password": None,  # Will be generated
            "connection": "Username-Password-Authentication",
            "role": "manager"
        }
    }

    def __init__(self, domain: str, client_id: str, client_secret: str):
        """Initialize Auth0 management client"""
        self.domain = domain
        self.client_id = client_id
        self.client_secret = client_secret
        
        try:
            # Get management API token using client credentials flow
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
            
            try:
                # auth0-python 6.5+ uses tenant_domain and keyword-only args.
                self.mgmt = Auth0(tenant_domain=domain, token=token)
            except TypeError:
                try:
                    # Some 6.x builds may accept domain as the keyword.
                    self.mgmt = Auth0(domain=domain, token=token)
                except TypeError:
                    # Backward compatibility for older auth0-python versions.
                    self.mgmt = Auth0(domain, token)
        except Exception as e:
            raise Exception(f"Failed to authenticate with Auth0: {e}")
        
        self.api_id = None
        self.permission_ids = {}
        self.role_ids = {}
        self.user_ids = {}

    def log(self, message: str, status: str = "✓"):
        """Print formatted log message"""
        print(f"  {status} {message}")

    def log_section(self, title: str):
        """Print section header"""
        print(f"\n{title}")
        print("=" * len(title))

    @staticmethod
    def _field(item, key: str, default=None):
        """Read a field from either a dict-like or object-like SDK response."""
        if isinstance(item, dict):
            return item.get(key, default)
        return getattr(item, key, default)

    def create_api(self) -> bool:
        """Create or retrieve API resource"""
        self.log_section("Step 1: Create/Verify API")
        
        try:
            if hasattr(self.mgmt, "resource_servers"):
                apis = self.mgmt.resource_servers.list()
                for api in apis:
                    if self._field(api, "identifier") == self.API_IDENTIFIER:
                        self.api_id = self._field(api, "id")
                        self.log(f"API already exists: {self.API_IDENTIFIER}")
                        return True

                api = self.mgmt.resource_servers.create(
                    name=self.API_NAME,
                    identifier=self.API_IDENTIFIER,
                    signing_alg="RS256",
                    token_lifetime=86400,
                    skip_consent_for_verifiable_first_party_clients=True,
                )
            else:
                # Legacy auth0-python fallback.
                apis = self.mgmt.apis.all()
                for api in apis:
                    if self._field(api, "identifier") == self.API_IDENTIFIER:
                        self.api_id = self._field(api, "id")
                        self.log(f"API already exists: {self.API_IDENTIFIER}")
                        return True

                api_body = {
                    "name": self.API_NAME,
                    "identifier": self.API_IDENTIFIER,
                    "signing_alg": "RS256",
                    "token_lifetime": 86400,
                    "token_expiration_for_browser": None,
                    "skip_consent_for_verifiable_first_party_clients": True,
                }
                api = self.mgmt.apis.create(api_body)

            self.api_id = self._field(api, "id")
            self.log(f"Created API: {self.API_IDENTIFIER}")
            return True
            
        except Exception as e:
            self.log(f"Failed to create API: {e}", "✗")
            return False

    def create_permissions(self) -> bool:
        """Create permissions for API"""
        self.log_section("Step 2: Create Permissions")
        
        try:
            if hasattr(self.mgmt, "resource_servers"):
                api = self.mgmt.resource_servers.get(self.api_id)
                existing_scopes = list(self._field(api, "scopes", []) or [])
                existing_names = {
                    self._field(scope, "value") for scope in existing_scopes if self._field(scope, "value")
                }

                changed = False
                for perm in self.PERMISSIONS:
                    if perm["name"] in existing_names:
                        self.permission_ids[perm["name"]] = perm["name"]
                        self.log(f"Permission already exists: {perm['name']}")
                    else:
                        existing_scopes.append({
                            "value": perm["name"],
                            "description": perm["description"],
                        })
                        self.permission_ids[perm["name"]] = perm["name"]
                        self.log(f"Created permission: {perm['name']}")
                        changed = True

                if changed:
                    self.mgmt.resource_servers.update(self.api_id, scopes=existing_scopes)
            else:
                # Legacy auth0-python fallback.
                existing_perms = {}
                perms = self.mgmt.apis.all_scopes(self.api_id)
                for perm in perms:
                    existing_perms[self._field(perm, "value")] = self._field(perm, "id")

                for perm in self.PERMISSIONS:
                    if perm["name"] in existing_perms:
                        self.permission_ids[perm["name"]] = existing_perms[perm["name"]]
                        self.log(f"Permission already exists: {perm['name']}")
                    else:
                        scope_body = {
                            "value": perm["name"],
                            "description": perm["description"]
                        }
                        scope = self.mgmt.apis.create_scopes(self.api_id, scope_body)
                        self.permission_ids[perm["name"]] = self._field(scope, "id")
                        self.log(f"Created permission: {perm['name']}")
            
            return True
            
        except Exception as e:
            self.log(f"Failed to create permissions: {e}", "✗")
            return False

    def create_roles(self) -> bool:
        """Create roles"""
        self.log_section("Step 3: Create Roles")
        
        try:
            existing_roles = {}
            if hasattr(self.mgmt.roles, "list"):
                roles = self.mgmt.roles.list()
            else:
                roles = self.mgmt.roles.all()

            for role in roles:
                existing_roles[self._field(role, "name")] = self._field(role, "id")
            
            # Create missing roles
            for role_name, role_config in self.ROLES.items():
                if role_name in existing_roles:
                    self.role_ids[role_name] = existing_roles[role_name]
                    self.log(f"Role already exists: {role_name}")
                else:
                    if hasattr(self.mgmt.roles, "list"):
                        role = self.mgmt.roles.create(
                            name=role_config["name"],
                            description=role_config["description"],
                        )
                    else:
                        role_body = {
                            "name": role_config["name"],
                            "description": role_config["description"]
                        }
                        role = self.mgmt.roles.create(role_body)

                    self.role_ids[role_name] = self._field(role, "id")
                    self.log(f"Created role: {role_name}")
            
            return True
            
        except Exception as e:
            self.log(f"Failed to create roles: {e}", "✗")
            return False

    def assign_permissions_to_roles(self) -> bool:
        """Assign permissions to roles"""
        self.log_section("Step 4: Assign Permissions to Roles")
        
        try:
            for role_name, role_config in self.ROLES.items():
                role_id = self.role_ids[role_name]
                
                existing_perms = {}
                if hasattr(self.mgmt.roles, "permissions"):
                    role_perms = self.mgmt.roles.permissions.list(role_id)
                else:
                    role_perms = self.mgmt.roles.all_permissions(role_id)

                for perm in role_perms:
                    existing_perms[self._field(perm, "permission_name")] = True
                
                # Add missing permissions
                for perm_name in role_config["permissions"]:
                    if perm_name not in existing_perms:
                        if hasattr(self.mgmt.roles, "permissions"):
                            self.mgmt.roles.permissions.add(
                                role_id,
                                permissions=[
                                    {
                                        "resource_server_identifier": self.API_IDENTIFIER,
                                        "permission_name": perm_name,
                                    }
                                ],
                            )
                        else:
                            perm_body = {
                                "permissions": [
                                    {
                                        "resource_server_identifier": self.API_IDENTIFIER,
                                        "permission_name": perm_name
                                    }
                                ]
                            }
                            self.mgmt.roles.add_permissions(role_id, perm_body)
                        self.log(f"Assigned {perm_name} to {role_name}")
                    else:
                        self.log(f"Permission {perm_name} already assigned to {role_name}")
            
            return True
            
        except Exception as e:
            self.log(f"Failed to assign permissions: {e}", "✗")
            return False

    def create_users(self) -> bool:
        """Create test users"""
        self.log_section("Step 5: Create Test Users")
        
        try:
            def resolve_user_id_by_email(email: str):
                """Find an existing user id by exact email."""
                if hasattr(self.mgmt.users, "list_users_by_email"):
                    users = self.mgmt.users.list_users_by_email(email=email)
                else:
                    users = self.mgmt.users.list(search_engine="v3", q=f'email:"{email}"')

                for user in users:
                    if self._field(user, "email") == email:
                        return self._field(user, "user_id")
                return None

            existing_users = {}
            
            # Create missing users
            for user_key, user_config in self.TEST_USERS.items():
                email = user_config["email"]
                
                if email in existing_users:
                    self.user_ids[user_key] = existing_users[email]
                    self.log(f"User already exists: {email}")
                else:
                    existing_id = resolve_user_id_by_email(email)
                    if existing_id:
                        self.user_ids[user_key] = existing_id
                        self.log(f"User already exists: {email}")
                        continue

                    # Generate a simple password
                    password = f"TempPass123!{user_key.capitalize()}"
                    
                    try:
                        if hasattr(self.mgmt.users.create, "__call__"):
                            try:
                                user = self.mgmt.users.create(
                                    email=email,
                                    password=password,
                                    connection=user_config["connection"],
                                    email_verified=True,
                                    user_metadata={},
                                )
                            except TypeError:
                                # Legacy auth0-python fallback.
                                user_body = {
                                    "email": email,
                                    "password": password,
                                    "connection": user_config["connection"],
                                    "email_verified": True,
                                    "user_metadata": {}
                                }
                                user = self.mgmt.users.create(user_body)
                        else:
                            user_body = {
                                "email": email,
                                "password": password,
                                "connection": user_config["connection"],
                                "email_verified": True,
                                "user_metadata": {}
                            }
                            user = self.mgmt.users.create(user_body)
                    except Exception as create_error:
                        error_text = str(create_error).lower()
                        if "status_code: 409" in error_text or "already exists" in error_text:
                            existing_id = resolve_user_id_by_email(email)
                            if existing_id:
                                self.user_ids[user_key] = existing_id
                                self.log(f"User already exists: {email}")
                                continue
                        raise

                    self.user_ids[user_key] = self._field(user, "user_id")
                    self.log(f"Created user: {email}")
            
            return True
            
        except Exception as e:
            self.log(f"Failed to create users: {e}", "✗")
            return False

    def assign_roles_to_users(self) -> bool:
        """Assign roles to users"""
        self.log_section("Step 6: Assign Roles to Users")
        
        try:
            for user_key, user_config in self.TEST_USERS.items():
                user_id = self.user_ids[user_key]
                role_name = user_config["role"]
                role_id = self.role_ids[role_name]
                
                existing_roles = {}
                if hasattr(self.mgmt.users, "roles"):
                    user_roles = self.mgmt.users.roles.list(user_id)
                else:
                    user_roles = self.mgmt.users.list_roles(user_id)

                for role in user_roles:
                    existing_roles[self._field(role, "name")] = True
                
                if role_name not in existing_roles:
                    if hasattr(self.mgmt.users, "roles"):
                        self.mgmt.users.roles.assign(user_id, roles=[role_id])
                    else:
                        body = {"roles": [role_id]}
                        self.mgmt.users.add_roles(user_id, body)
                    self.log(f"Assigned {role_name} role to {user_config['email']}")
                else:
                    self.log(f"User {user_config['email']} already has {role_name} role")
            
            return True
            
        except Exception as e:
            self.log(f"Failed to assign roles: {e}", "✗")
            return False

    def enable_rbac_claims(self) -> bool:
        """Enable RBAC claims in token"""
        self.log_section("Step 7: Enable RBAC Claims in Token")
        
        try:
            # Update API settings to include permissions in token
            api_body = {
                "include_in_access_token": True
            }
            # Note: The auth0 SDK may not support this directly,
            # so we might need to do this manually or via Management API directly
            self.log("MANUAL STEP: Enable 'Add Permissions in Access Token' in Auth0 dashboard")
            self.log(f"Location: Applications > APIs > {self.API_IDENTIFIER} > Settings")
            return True
            
        except Exception as e:
            self.log(f"Note: {e}", "ℹ")
            return True  # Non-critical

    def generate_env_file(self) -> bool:
        """Generate .env file with configuration"""
        self.log_section("Step 8: Generate Configuration")
        
        try:
            env_content = f"""# Auth0 Configuration
# Generated by auth0_setup.py on {os.environ.get('DATE', 'today')}

# Auth0 Domain (your tenant)
AUTH0_DOMAIN={self.domain}

# API Audience (must match Auth0 API identifier)
API_AUDIENCE={self.API_IDENTIFIER}

# JWT Algorithms (RS256 is standard for Auth0)
ALGORITHMS=RS256

# Frontend Configuration (optional, for reference)
REACT_APP_AUTH0_DOMAIN={self.domain}
REACT_APP_AUTH0_AUDIENCE={self.API_IDENTIFIER}
REACT_APP_API_SERVER_URL=http://127.0.0.1:5000

# Test User Credentials (for manual testing in Postman)
# Barista User
TEST_BARISTA_EMAIL=barista@test.local
TEST_BARISTA_ROLE=barista
TEST_BARISTA_PERMISSIONS=get:drinks,get:drinks-detail

# Manager User
TEST_MANAGER_EMAIL=manager@test.local
TEST_MANAGER_ROLE=manager
TEST_MANAGER_PERMISSIONS=get:drinks,get:drinks-detail,post:drinks,patch:drinks,delete:drinks
"""
            
            env_path = ".env"
            with open(env_path, "w") as f:
                f.write(env_content)
            
            self.log(f"Created .env file: {env_path}")
            return True
            
        except Exception as e:
            self.log(f"Failed to create .env file: {e}", "✗")
            return False

    def run(self) -> bool:
        """Run full setup sequence"""
        print("\n" + "=" * 60)
        print("AUTH0 COFFEE SHOP SETUP")
        print("=" * 60)
        print(f"Domain: {self.domain}")
        
        steps = [
            ("API", self.create_api),
            ("Permissions", self.create_permissions),
            ("Roles", self.create_roles),
            ("Assign Permissions to Roles", self.assign_permissions_to_roles),
            ("Users", self.create_users),
            ("Assign Roles to Users", self.assign_roles_to_users),
            ("RBAC Claims", self.enable_rbac_claims),
            (".env File", self.generate_env_file),
        ]
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    print(f"\n❌ Setup failed at step: {step_name}")
                    return False
            except Exception as e:
                self.log(f"Unexpected error: {e}", "✗")
                return False
        
        self.print_summary()
        return True

    def print_summary(self):
        """Print setup summary"""
        print("\n" + "=" * 60)
        print("✅ AUTH0 SETUP COMPLETE")
        print("=" * 60)
        
        print("\n📋 CONFIGURATION SUMMARY:")
        print(f"  Domain: {self.domain}")
        print(f"  API Identifier: {self.API_IDENTIFIER}")
        print(f"  Permissions: {len(self.PERMISSIONS)}")
        print(f"  Roles: {list(self.ROLES.keys())}")
        print(f"  Test Users: {[u['email'] for u in self.TEST_USERS.values()]}")
        
        print("\n📝 NEXT STEPS:")
        print("  1. Copy .env values to your project configuration")
        print("  2. Update frontend/src/environments/environment.ts with Auth0 domain and Client ID")
        print("  3. Test tokens in Postman or Auth0 dashboard")
        print("  4. Run: pytest backend/tests/test_auth.py -v")
        
        print("\n⚠️  MANUAL STEPS REQUIRED:")
        print("  1. Auth0 Dashboard > Applications > APIs > Coffee Shop API > Settings")
        print("  2. Enable toggle: 'Add Permissions in Access Token'")
        print("  3. Save")
        
        print("\n📚 TEST USER CREDENTIALS:")
        for user_key, user_config in self.TEST_USERS.items():
            print(f"  {user_config['role'].upper()}:")
            print(f"    Email: {user_config['email']}")
            print(f"    Password: [Check Auth0 dashboard for reset if needed]")
            print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Automate Auth0 setup for Coffee Shop project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python auth0_setup.py --domain my-tenant.auth0.com --client-id ABC123 --client-secret XYZ789
  
PREREQUISITES:
  1. Auth0 account at auth0.com
  2. Tenant created (provides domain)
  3. Management API credentials obtained
  4. python-jose and auth0 packages installed: pip install python-jose auth0
        """
    )
    
    parser.add_argument("--domain", required=True, help="Auth0 domain (e.g., my-tenant.auth0.com)")
    parser.add_argument("--client-id", required=True, help="Management API Client ID")
    parser.add_argument("--client-secret", required=True, help="Management API Client Secret")
    
    args = parser.parse_args()
    
    try:
        setup = Auth0Setup(args.domain, args.client_id, args.client_secret)
        success = setup.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
