# Fix: Enable Auth0 Password Grant for CLI Token Generation

## Problem
```
Error: Failed to get token
The remote server returned an error: (401) Unauthorized.
```

This happens when Auth0 doesn't allow the "Resource Owner Password" grant type.

## Solution: Enable Password Grant (5 minutes)

### Step 1: Go to Auth0 Dashboard
Visit: https://manage.auth0.com/dashboard

### Step 2: Select Your Application
- Click **Applications** in the left menu
- Find your application (e.g., "Coffee Shop Setup")
- Click on it

### Step 3: Enable Password Grant
- Click the **Settings** tab
- Scroll down to **"Grant Types"**
- Check the box for: **✓ Resource Owner Password**
- Click **Save Changes**

### Step 4: Enable the Connection
- Scroll back up to **"Connections"**
- Make sure **"Username-Password-Authentication"** is toggled ON
- If not, toggle it on and save

### Step 5: Test
```powershell
make token-barista
```

You should now see your JWT token!

---

## Verification Checklist

✓ Application Grant Types includes "Resource Owner Password"
✓ "Username-Password-Authentication" connection is enabled
✓ Users "barista@test.local" and "manager@test.local" exist (created by `make auth0-init`)
✓ Auth0 credentials are in `.env` (AUTH0_DOMAIN, AUTH0_CLIENT_ID)

---

## If Still Getting 401

1. **Clear browser cache** and log back into Auth0 Dashboard
2. **Wait 30 seconds** - Auth0 settings can take a moment to propagate
3. **Try again:**
   ```powershell
   make token-barista
   ```

4. **Check the exact error:**
   ```powershell
   cd Project/03_coffee_shop_full_stack/starter_code/backend/_helpers
   powershell -NoProfile -ExecutionPolicy Bypass -File get_token.ps1 -Role barista -Verbose
   ```

---

## Alternative: Use Postman (No Auth0 Config Needed)

If you don't want to enable password grant, use Postman's built-in OAuth2 flow:
1. Create a request in Postman
2. Go to **Authorization** tab
3. Select **OAuth 2.0**
4. Let Postman handle the login - it will work without password grant enabled

See TOKEN_GENERATION.md for full Postman setup.
