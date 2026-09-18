# Test Token Generation Guide

## ⚠️ QUICK FIX: If Getting 401 Error

You'll get `401 Unauthorized` if Auth0 password grant isn't enabled.

**Follow this 5-minute setup:** [SETUP_PASSWORD_GRANT.md](SETUP_PASSWORD_GRANT.md)

After that, this will work:
```powershell
make token-barista
```

---

## Quick Start

### Test User Credentials
- **Barista:** `barista@test.local` / `TempPass123!Barista`
- **Manager:** `manager@test.local` / `TempPass123!Manager`

## CLI Automation (PowerShell)

**Generate tokens directly from the command line:**

```powershell
make token-barista    # Generate barista JWT token
make token-manager    # Generate manager JWT token
```

Or directly:
```powershell
cd Project/03_coffee_shop_full_stack/starter_code/backend/_helpers
powershell -NoProfile -ExecutionPolicy Bypass -File get_token.ps1 -Role barista
powershell -NoProfile -ExecutionPolicy Bypass -File get_token.ps1 -Role manager
```

---

## Getting 401 Error?

The CLI automation requires Auth0 password grant to be enabled. See [SETUP_PASSWORD_GRANT.md](SETUP_PASSWORD_GRANT.md) for a quick 5-minute setup guide.

---

## Getting JWT Tokens (Alternative Methods)

### Option 1: Auth0 Dashboard (Easiest)
1. Go to [Auth0 Dashboard](https://manage.auth0.com/dashboard)
2. Select **Applications** from the left menu
3. Find your application (e.g., "Coffee Shop Setup")
4. Click the **Test** tab
5. Use the test endpoints to get a token

### Option 2: Postman (Recommended for API Testing)
1. Create a new request in Postman
2. Click **Authorization** tab
3. Select **OAuth 2.0** from the dropdown
4. Fill in:
   - **Grant Type:** Authorization Code Flow (or Implicit for testing)
   - **Callback URL:** `http://localhost:3000/callback`
   - **Auth URL:** `https://dev-53bey634viqgnyzc.us.auth0.com/authorize`
   - **Access Token URL:** `https://dev-53bey634viqgnyzc.us.auth0.com/oauth/token`
   - **Client ID:** `LhgYzneJPGKmuasdbBAQaMQt6MCEwYar`
   - **Audience:** `coffee-shop-api`
   - **Realm:** `Username-Password-Authentication`
5. Click **Get New Access Token**
6. Log in with barista@test.local or manager@test.local
7. Postman will automatically add the token to your request header

### Option 3: cURL Command

**Bash/Linux/Mac:**
```bash
curl -X POST https://dev-53bey634viqgnyzc.us.auth0.com/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "password",
    "username": "barista@test.local",
    "password": "TempPass123!Barista",
    "audience": "coffee-shop-api",
    "client_id": "LhgYzneJPGKmuasdbBAQaMQt6MCEwYar",
    "realm": "Username-Password-Authentication"
  }'
```

**PowerShell:**
```powershell
$body = @{
    grant_type = "password"
    username = "barista@test.local"
    password = "TempPass123!Barista"
    audience = "coffee-shop-api"
    client_id = "LhgYzneJPGKmuasdbBAQaMQt6MCEwYar"
    realm = "Username-Password-Authentication"
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://dev-53bey634viqgnyzc.us.auth0.com/oauth/token" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

For manager, replace `username` and `password` with:
```powershell
username = "manager@test.local"
password = "TempPass123!Manager"
```

## Using the Token

### In Postman
1. Copy the `access_token` from the response
2. In your API request, go to **Headers** tab
3. Add a new header:
   - **Key:** `Authorization`
   - **Value:** `Bearer <paste_token_here>`

### In cURL
```bash
curl -H "Authorization: Bearer <access_token>" \
  http://127.0.0.1:5000/drinks-detail
```

### In Python
```python
headers = {
    "Authorization": f"Bearer {access_token}"
}
response = requests.get("http://127.0.0.1:5000/drinks-detail", headers=headers)
```

## Token Permissions

**Barista Role:**
- `get:drinks` - View drink list
- `get:drinks-detail` - View drink recipes

**Manager Role:**
- `get:drinks` - View drink list
- `get:drinks-detail` - View drink recipes
- `post:drinks` - Create new drinks
- `patch:drinks` - Update drinks
- `delete:drinks` - Delete drinks

## Help

### Token not working?
1. Make sure the token hasn't expired (default: 24 hours)
2. Verify you're using the correct Auth0 domain: `dev-53bey634viqgnyzc.us.auth0.com`
3. Check that the `Authorization` header format is: `Bearer <token>`

### See info about your token
Visit [jwt.io](https://jwt.io) and paste your token to decode it and verify the claims and permissions.
