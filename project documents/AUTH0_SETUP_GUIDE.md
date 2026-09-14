# Auth0 Setup Guide - Phase 1 Auth Foundation

**Status:** Required setup steps for Coffee Shop project

**Reference:** JWT_AUTH_SPEC.md (Section 2-3), PROJECT_SOURCE_OF_TRUTH.md (Section 5.3)

---

## Step 1: Create Auth0 Tenant

1. Go to https://auth0.com
2. Sign up for a free account (or log in if you have one)
3. Create a new tenant:
   - Choose a tenant name (e.g., `coffee-shop-dev`)
   - Select region (typically US)
4. **Save your Auth0 Domain** (format: `xxxxx.auth0.com`) - you'll need this later

---

## Step 2: Create Auth0 Application

1. In Auth0 Dashboard, go to **Applications** → **Applications**
2. Click **Create Application**
3. Fill in:
   - **Name:** `Coffee Shop Ionic App` (or similar)
   - **Application Type:** Single Page Application (SPA)
4. Click **Create**
5. In the settings tab:
   - Note the **Client ID** - save this
   - Under **Allowed Callback URLs**, add:
     ```
     http://localhost:8100/callback
     ```
   - Under **Allowed Logout URLs**, add:
     ```
     http://localhost:8100
     ```
6. Save changes

**Save for later:**
- Auth0 Domain: `xxxxx.auth0.com`
- Client ID from this application
- Auth0 API Audience (we'll set this in Step 3)

---

## Step 3: Create Auth0 API

1. Go to **Applications** → **APIs**
2. Click **Create API**
3. Fill in:
   - **Name:** `Coffee Shop API` (or similar)
   - **Identifier:** `coffee-shop-api` (this is your API_AUDIENCE - save it!)
   - **Signing Algorithm:** RS256 (default - do not change)
4. Click **Create**
5. Go to the **Permissions** tab
6. Add the following permissions:

   | Permission | Description |
   |------------|-------------|
   | `get:drinks` | View drink list |
   | `get:drinks-detail` | View drink details/recipes |
   | `post:drinks` | Create drinks |
   | `patch:drinks` | Update drinks |
   | `delete:drinks` | Delete drinks |

---

## Step 4: Configure Roles and Assign Permissions

### Create Barista Role

1. Go to **User Management** → **Roles**
2. Click **Create Role**
3. Fill in:
   - **Name:** `barista`
   - **Description:** `Barista can view drink details and recipes`
4. Click **Create**
5. In the **Permissions** tab, add:
   - `get:drinks`
   - `get:drinks-detail`

### Create Manager Role

1. Click **Create Role**
2. Fill in:
   - **Name:** `manager`
   - **Description:** `Manager can manage all drinks (create, read, update, delete)`
3. Click **Create**
4. In the **Permissions** tab, add:
   - `get:drinks`
   - `get:drinks-detail`
   - `post:drinks`
   - `patch:drinks`
   - `delete:drinks`

---

## Step 5: Create Test Users and Assign Roles

### Create Barista Test User

1. Go to **User Management** → **Users**
2. Click **Create User**
3. Fill in:
   - **Email:** `barista@test.local`
   - **Password:** (generate a strong password, save it)
   - **Connection:** Username-Password-Authentication
4. Click **Create**
5. In the user's **Roles** tab, assign the `barista` role

### Create Manager Test User

1. Click **Create User**
2. Fill in:
   - **Email:** `manager@test.local`
   - **Password:** (generate a strong password, save it)
   - **Connection:** Username-Password-Authentication
3. Click **Create**
4. In the user's **Roles** tab, assign the `manager` role

---

## Step 6: Enable RBAC Claims in Token

1. Go to **Applications** → **APIs**
2. Click your **Coffee Shop API**
3. Go to **Settings** tab
4. Enable **Add Permissions in Access Token** (toggle ON)
5. Save changes

**This ensures JWT tokens include the permissions claim required by the backend.**

---

## Step 7: Verify Configuration in Postman (Optional Now)

1. In Auth0 Dashboard, go to **Applications** → **APIs** → **Coffee Shop API** → **Test** tab
2. Select an application from the dropdown
3. Click **Get Access Token** to test a token request
4. Use that token to test API calls (we'll do this in Postman after backend is ready)

---

## Configuration Values Needed for Project

After completing the steps above, you should have:

```
AUTH0_DOMAIN = xxxxx.auth0.com
API_AUDIENCE = coffee-shop-api  (the identifier you set in Step 3)
ALGORITHMS = ["RS256"]  (default, do not change)
CLIENT_ID = (from Step 2 - for frontend)
```

These will be used in:
- **Backend:** `backend/src/auth/auth.py`
- **Frontend:** `frontend/src/environments/environment.ts`

---

## What's Next

Once Auth0 is configured:
1. Backend auth functions will use these values to verify tokens
2. Tokens will include `permissions` claim due to RBAC configuration
3. Test users can log in via frontend and get tokens
4. Tokens will be validated by backend auth module

