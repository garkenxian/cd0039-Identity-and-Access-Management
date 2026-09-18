#!/usr/bin/env python3
"""
Auth0 Test Token Generator

This is a reference script for generating JWT tokens for test users.
Note: Auth0 token generation requires specific client configuration.

RECOMMENDED: Get tokens directly from Auth0 Dashboard or use Postman's OAuth2 support:

1. Auth0 Dashboard Method:
   - Go to: https://manage.auth0.com/dashboard
   - Click on "Applications" → Select your application
   - Go to the "Test" tab
   - Use the test endpoints there

2. Postman Method:
   - Set Authorization Type to "OAuth 2.0"
   - Configure with your Auth0 domain and audience
   - Get token automatically

3. Manual cURL:
   curl -X POST https://{AUTH0_DOMAIN}/oauth/token \
     -H "Content-Type: application/json" \
     -d '{
       "client_id": "{YOUR_CLIENT_ID}",
       "client_secret": "{YOUR_CLIENT_SECRET}",
       "audience": "coffee-shop-api",
       "grant_type": "client_credentials"
     }'

Test Credentials:
  Barista: barista@test.local / TempPass123!Barista
  Manager: manager@test.local / TempPass123!Manager
"""

import os
import sys

if __name__ == '__main__':
    print(__doc__)
    sys.exit(0)

