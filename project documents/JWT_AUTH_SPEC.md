# JWT and Auth0 Specification (Submission Contract)

Last updated: 2026-09-13
Scope: Udacity IAM Coffee Shop starter project submission

## 1) Objective

Define exactly how JWT authentication and RBAC authorization must work for this project, including signature verification expectations and environment variable guidance.

## 1.1 Token Acquisition Flow (No Basic-to-Bearer Exchange)

Project expectation:
- Users do not trade a basic token for a bearer token in this submission flow.
- The frontend redirects the user to Auth0 login and receives an Auth0 access token directly.
- That access token is then sent as Bearer in API requests.

Clarification:
- HTTP Basic authentication is not part of the required project path.
- The backend never issues bearer tokens in this architecture; Auth0 is the token issuer.

Submission-safe flow:
1. User clicks login in frontend.
2. Frontend redirects to Auth0 authorize endpoint.
3. Auth0 authenticates user and returns access token.
4. Frontend stores token and sends Authorization: Bearer <token> to backend.
5. Backend verifies token and permissions per route.

Note on alternatives:
- OAuth authorization-code plus PKCE token exchange is a modern pattern, but not required to satisfy this starter submission contract unless intentionally adopted later as a controlled enhancement.

## 2) Token Model and Signing Expectation

Expected token type:
- Auth0-issued access token
- Algorithm: RS256

Signing model:
- Auth0 signs JWTs with its private key.
- Backend verifies signature using Auth0 public keys fetched from JWKS endpoint.

Critical clarification:
- For RS256 verification in this project, backend does not sign tokens and does not need a local shared signing secret string.
- Therefore, a local .env JWT signing secret is not required for the core rubric path.

## 3) Verification Requirements in Backend

Verification flow must include:
1. Read Authorization header.
2. Enforce Bearer token format.
3. Fetch JWKS from https://<AUTH0_DOMAIN>/.well-known/jwks.json.
4. Select key by kid in token header.
5. Verify signature and algorithm.
6. Validate claims:
- audience must match configured API audience
- issuer must match https://<AUTH0_DOMAIN>/
7. Validate permissions claim includes required permission for secured endpoint.

Expected auth failure categories:
- authorization_header_missing
- invalid_header
- token_expired
- invalid_claims
- invalid token/signature
- missing permissions claim
- permission_not_found

## 4) Authorization Contract

Decorator behavior:
- requires_auth(permission) wraps protected routes.
- On success, decoded payload is passed to route handler.
- On failure, raise AuthError with consistent status code and message shape.

Permission mapping:
- get:drinks-detail required for GET /drinks-detail
- post:drinks required for POST /drinks
- patch:drinks required for PATCH /drinks/<id>
- delete:drinks required for DELETE /drinks/<id>

## 5) Environment Variables and Secrets Guidance

Core submission path variables (backend):
- AUTH0_DOMAIN
- API_AUDIENCE
- ALGORITHMS (usually RS256)

Frontend config variables:
- auth0 url/domain prefix
- auth0 audience
- auth0 clientId
- callback URL

Do we need a .env with a secret string?
- Not for RS256 token signature verification in this core project path.
- Yes for configuration management convenience (domain, audience, optional app settings), but not for a JWT shared secret.

When a secret string may be needed:
- If implementing optional Auth0 Management API endpoints (standout feature), client credentials such as client secret must be stored in environment variables and never committed.

## 6) Storage and Operational Security

- Never commit real Auth0 secrets to source control.
- Postman JWT tokens are a rubric exception for reviewer verification; refresh near submission due to expiry.
- Use short-lived tokens and least privilege role assignments.

## 7) Testing Requirements (Team Gate)

Backend auth tests should cover:
- Missing Authorization header
- Malformed Bearer header
- Expired token path
- Invalid claims path
- Permission missing path
- Valid token with required permission

Coverage gate:
- Include auth module in overall backend pytest coverage >= 80%.

## 8) Gotchas

- Do not switch to HS256 unless explicitly required; it changes secret handling and can break intended starter behavior.
- Domain and audience mismatches are common and must be validated early.
- Role permissions must appear in token permissions claim (Auth0 RBAC settings must enable this).
