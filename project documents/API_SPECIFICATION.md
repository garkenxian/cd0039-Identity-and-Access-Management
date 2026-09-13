# API Specification (Submission Contract)

Last updated: 2026-09-13
Scope: Udacity IAM Coffee Shop starter project submission
Primary backend path: Project/03_coffee_shop_full_stack/starter_code/backend/src

## 1) Contract Rules

- This specification is the required API contract for submission.
- Do not rename endpoints, change HTTP methods, or change response top-level keys.
- Keep JSON response shapes consistent across success and error flows.

## 2) Base Configuration

- Base URL (local default): http://127.0.0.1:5000
- Content-Type: application/json for request bodies
- Auth scheme for secured endpoints: Authorization: Bearer <jwt>

## 3) Data Model

Drink object long form:
- id: integer
- title: string
- recipe: array of objects

Recipe item:
- name: string
- color: string
- parts: number

Drink object short form:
- id: integer
- title: string
- recipe: array of objects containing only:
  - color: string
  - parts: number

## 4) Role and Permission Matrix

Public:
- `GET /drinks`

Barista:
- get:drinks
- get:drinks-detail

Manager:
- get:drinks
- get:drinks-detail
- post:drinks
- patch:drinks
- delete:drinks

## 5) Endpoints

## 5.1 `GET /drinks`

Purpose:
- Public list of drinks in short format.

Auth:
- Not required.

Success response:
- Status: 200
- Body:
```json
{
  "success": true,
  "drinks": [DrinkShort]
}
```

Failure expectations:
- 422 for unprocessable response construction issues

## 5.2 `GET /drinks-detail`

Purpose:
- Return detailed recipe data.

Auth:
- Required permission: get:drinks-detail

Success response:
- Status: 200
- Body:
```json
{
  "success": true,
  "drinks": [DrinkLong]
}
```

Failure expectations:
- 401 for missing/invalid/expired token
- 403 for valid token without permission

## 5.3 `POST /drinks`

Purpose:
- Create a new drink.

Auth:
- Required permission: post:drinks

Request body:
```json
{
  "title": "string",
  "recipe": [
    {
      "name": "string",
      "color": "string",
      "parts": 1
    }
  ]
}
```

Success response:
- Status: 200
- Body:
```json
{
  "success": true,
  "drinks": [DrinkLong]
}
```

Failure expectations:
- 400 if body is malformed
- 401 for missing/invalid/expired token
- 403 for missing permission
- 422 for validation/insert errors

## 5.4 `PATCH /drinks/<id>`

Purpose:
- Update an existing drink.

Auth:
- Required permission: patch:drinks

Path parameter:
- id: integer

Request body:
- Partial or full drink payload accepted by implementation.

Success response:
- Status: 200
- Body:
```json
{
  "success": true,
  "drinks": [DrinkLong]
}
```

Failure expectations:
- 400 for invalid id/body
- 401 for missing/invalid/expired token
- 403 for missing permission
- 404 if drink id does not exist
- 422 for update failures

## 5.5 `DELETE /drinks/<id>`

Purpose:
- Delete existing drink.

Auth:
- Required permission: delete:drinks

Path parameter:
- id: integer

Success response:
- Status: 200
- Body:
```json
{
  "success": true,
  "delete": <id>
}
```

Failure expectations:
- 400 for invalid id
- 401 for missing/invalid/expired token
- 403 for missing permission
- 404 if drink id does not exist

## 6) Standard Error Shape

All handled errors should return:
```json
{
  "success": false,
  "error": <http_status_code>,
  "message": "human readable message"
}
```

Minimum required handlers:
- 404 resource not found
- 422 unprocessable
- AuthError handler mapping auth failures to structured JSON

Recommended additional handlers:
- 400 bad request
- 405 method not allowed

## 7) Non-Functional Expectations

- PEP 8 style and clear naming.
- Clear comments only where needed.
- Secrets not committed in source.
- SQLite remains the project DB for submission path.

## 8) Test Requirements (Team Gate)

Backend tests must validate:
- Endpoint happy path by role
- Permission-denied paths
- Missing/invalid/expired token paths
- 404 for missing drink id
- CRUD state transitions

Coverage gate:
- pytest coverage >= 80% for backend in-scope code before phase sign-off.

## 9) Submission Validation Checklist (API)

- All five required endpoints implemented with correct methods.
- Response envelopes match this spec.
- RBAC matrix verified with Auth0 tokens.
- Postman collection updated and exported in required location.
