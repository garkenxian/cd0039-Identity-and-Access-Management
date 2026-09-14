# Backend Helper Scripts

This folder contains utility scripts for backend development and deployment.

## auth0_setup.py

Automates Auth0 tenant configuration for the Coffee Shop project.

### What It Does

Automatically creates and configures:
- ✅ Auth0 API resource (`coffee-shop-api`)
- ✅ 5 permissions (get:drinks, get:drinks-detail, post:drinks, patch:drinks, delete:drinks)
- ✅ 2 roles (barista, manager)
- ✅ Permission-to-role assignments
- ✅ 2 test users (barista@test.local, manager@test.local)
- ✅ Role-to-user assignments
- ✅ `.env` configuration file

### Prerequisites

1. **Auth0 Account & Tenant** (manual setup)
   - Create account at https://auth0.com
   - Create a new tenant (get domain: xxxxx.auth0.com)

2. **Management API Credentials** (manual setup)
   - In Auth0 Dashboard: Applications > Applications > Create Application
   - Name: "Coffee Shop Setup Bot" (or any name)
   - Application Type: Machine to Machine
   - Click Create
   - In the API dropdown, select "Auth0 Management API"
   - Authorize required scopes (the script needs: read/create/update for APIs, roles, permissions, users)
   - Copy the **Client ID** and **Client Secret**

3. **Python Dependencies**
   ```bash
   pip install auth0 python-jose
   ```

### Usage

```bash
cd backend/_helpers

python auth0_setup.py \
  --domain your-tenant.auth0.com \
  --client-id YOUR_MANAGEMENT_API_CLIENT_ID \
  --client-secret YOUR_MANAGEMENT_API_CLIENT_SECRET
```

**Example:**
```bash
python auth0_setup.py \
  --domain coffee-shop-dev.auth0.com \
  --client-id mB7x3K9nQpZ2vL1mT4x \
  --client-secret r8K_p2vL9x3qM1n5vZ8xT6y9o2p5q8t1u4v7w0x3y6z
```

### Output

The script creates:
- **`.env`** - Configuration file with `AUTH0_DOMAIN`, `API_AUDIENCE`, etc.
- **Console output** - Setup progress and summary

### What's NOT Automated (Manual Step)

One Auth0 dashboard setting must be enabled manually after script runs:

1. Auth0 Dashboard → Applications → APIs → Coffee Shop API → Settings
2. Find: **"Add Permissions in Access Token"**
3. Toggle ON
4. Click Save

This ensures JWT tokens include the `permissions` claim needed by your backend.

### Next Steps After Running

1. **Update Environment:**
   ```bash
   # Copy generated .env to your environment
   cp .env ../../../.env
   ```

2. **Update Frontend:**
   - Edit `frontend/src/environments/environment.ts`
   - Set `auth0.url` to your domain
   - Set `auth0.clientId` to your SPA application Client ID (different from Management API credentials)

3. **Run Tests:**
   ```bash
   cd ..
   pytest tests/test_auth.py -v
   ```

4. **Generate Test Tokens:**
   - Auth0 Dashboard → Applications → APIs → Coffee Shop API → Test
   - Select your application
   - Click "Get Access Token"
   - Use in Postman or API tests

### Troubleshooting

**Error: "auth0 package not found"**
```bash
pip install auth0
```

**Error: "Failed to authenticate with Auth0"**
- Verify domain format: `xxxxx.auth0.com` (no https://)
- Verify Client ID and Secret are correct
- Verify credentials are for Management API credentials (not SPA app)

**Error: "Permission not found"**
- Make sure script ran successfully (check for errors above)
- Verify API was created (check Auth0 dashboard)

**Tokens not including permissions**
- Remember to manually enable "Add Permissions in Access Token" in API settings
- Restart your backend after enabling

### Script Architecture

The script uses:
- `auth0.management.Auth0` - Management API client
- Idempotent operations - safe to run multiple times
- Clear logging - each step shows what's happening
- Error handling - stops on critical failures

### Security Notes

- Script requires Management API Client Secret - keep it safe
- Never commit the script with credentials
- Test user passwords are generated - change them if using in production
- `.env` file is created locally and should be in `.gitignore`

