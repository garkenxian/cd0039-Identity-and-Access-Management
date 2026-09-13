# PROJECT SOURCE OF TRUTH (IMMUTABLE-BY-DEFAULT)

Document owner: Project team
Status: Active source of truth
Change policy: Immutable by default. Update only if a rubric conflict, grading blocker, or factual error is discovered.
Last updated: 2026-09-13

## 1) Purpose and Scope

This document is the canonical requirements and planning reference for the Udacity IAM Coffee Shop submission project.

Primary objective:
- Build and submit a rubric-compliant full-stack application that secures a Flask REST API with Auth0 RBAC and integrates with the provided Ionic frontend.

Scope includes:
- Required work in Project/03_coffee_shop_full_stack/starter_code/backend
- Required work in Project/03_coffee_shop_full_stack/starter_code/frontend
- Submission packaging and validation requirements

Out of scope for grading unless explicitly chosen as enhancements:
- Production hardening beyond rubric and agreed guardrails
- Major architectural rewrites that alter the starter contract

Required companion specification documents:
- project documents/API_SPECIFICATION.md
- project documents/JWT_AUTH_SPEC.md
- project documents/PROJECT_TASK_PACKETS.md

## 2) Project Goal (Short Summary)

We are implementing a secure digital cafe menu system where:
- Public users can view drink names/graphics.
- Baristas can view detailed recipes.
- Managers can create/update/delete drinks.

Core technical goals:
- Implement and secure REST endpoints in Flask.
- Enforce JWT + RBAC using Auth0.
- Keep backend and frontend loosely coupled via API + configuration.
- Deliver a submission-ready project in expected starter format.

## 3) Current State (as of 2026-09-13)

Current status snapshot:
- Starter structure exists and is intact.
- Backend auth and required endpoint TODOs are not yet complete.
- Frontend Auth0 environment configuration is not yet complete.
- Documentation exists but needs a single authoritative requirement source (this file now serves that role).

Interpretation:
- The project is currently in planning/discovery stage, not implementation complete.

## 4) Non-Negotiable Submission Contract Guardrails

These guardrails exist to prevent drifting from what reviewers expect.

1. Preserve starter project contract:
- Keep folder layout recognizable to reviewers.
- Do not relocate, rename, or remove the expected starter directories and key files unless absolutely required.
- Keep required endpoints and files in their expected locations.

2. Submission-first over production-first:
- Every implementation choice must pass a rubric alignment check first.
- If a modern practice conflicts with expected project behavior/format, prefer rubric-safe implementation and document tradeoff.

3. Minimize breaking changes:
- Avoid unnecessary dependency churn and framework upgrades that risk compatibility with starter scripts.
- No broad rewrites of frontend framework, backend framework, or data model contract.

4. Keep secrets out of source control:
- No real tokens/secrets in committed source except where rubric explicitly requires JWT in exported Postman collection for reviewer verification.
- Rotate or refresh JWTs near submission due to expiration constraints.

5. Preserve reviewer testability:
- Keep startup commands and README instructions accurate and reproducible.
- Ensure project can be run with expected course workflow (backend + ionic serve).

6. Validate before phase exit:
- No phase closes without checklist evidence and test/verification notes in PROJECT_PROGRESS.md.

## 5) Rubric-Derived Requirements (Instructions + Rubric Consolidated)

## 5.1 Functional Product Expectations

The application must:
- Display graphics representing ingredient ratios.
- Allow public view of drink names and graphics.
- Allow barista role to view recipe details.
- Allow manager role to create and edit drinks (and delete per required endpoint set).

## 5.2 Backend Flask + REST Requirements

Required endpoints:
- GET /drinks (public, short representation)
- GET /drinks-detail (secured)
- POST /drinks (secured)
- PATCH /drinks/<id> (secured)
- DELETE /drinks/<id> (secured)

Backend behavior requirements:
- Complete all TODO items in backend/src/api.py.
- Use proper Flask route decorators and request methods.
- Perform CRUD on SQLite via provided model interface.
- Implement robust error handling including common error paths and AuthError handling.
- Backend runs with flask run and responds correctly to required requests.

## 5.3 Auth0 + JWT + RBAC Requirements

Auth requirements:
- Auth0 is configured and operational for submission.
- Auth0 tenant/account signup and initial setup are required project tasks.
- Auth0 application and API must be created and configured in the tenant.
- auth.py includes required configuration values (domain/audience/client information as expected by project implementation).
- Custom requires_auth decorator is fully implemented.
- Authorization header parsing, JWT verification, claim validation, and permission checks are enforced.
- Expected auth failures are raised for expired token, invalid claims/token, and missing required permission.
- If optional management endpoints are implemented, machine credentials (client ID/client secret) must be configured via environment variables and never committed.

RBAC requirements:
- Roles and permissions configured in Auth0 and present in JWT claims.
- Barista permissions:
  - get:drinks
  - get:drinks-detail
- Manager permissions:
  - get:drinks
  - get:drinks-detail
  - post:drinks
  - patch:drinks
  - delete:drinks

Postman requirement:
- Update/export collection at starter_code/backend/udacity-fsnd-udaspicelatte.postman_collection.json.
- Configure barista and manager JWT tokens in collection auth sections.
- Ensure tokens are valid at review time.

## 5.4 Frontend Requirements

Frontend configuration:
- Configure frontend environment file with backend URL + Auth0 settings.
- Keep auth/REST loose coupling through configuration and service boundaries.

Runtime requirement:
- Frontend runs locally with ionic serve without errors and shows expected behavior.

## 5.5 Packaging + Repository Hygiene Requirements

Submission requirements:
- Submit complete project as a zip.
- Include all required project code.
- Ensure virtual environment, cache, and local artifacts are ignored.
- README must include dependency install and run instructions.
- Secrets handled as environment variables where applicable.

## 6) Additional Engineering Requirements (Team Policy)

These are mandatory for moving to the next phase in this project workflow.

1. Test coverage gate (hard requirement):
- Backend pytest coverage >= 80% on project backend code in scope.
- Frontend test coverage >= 80% on project frontend code in scope.

2. Security baseline:
- Enforce least privilege via RBAC checks.
- Centralize auth checks in decorator and service layers.
- Validate inputs and return consistent JSON errors.

3. Separation of concerns baseline:
- Keep auth logic, API routing, and model logic clearly separated.
- Keep frontend auth service separate from drink data service and UI components.
- Enforce a layered backend architecture pattern for implementation phases:
  - Data access layer: persistence and query operations only.
  - Service layer: business rules, validation orchestration, and permission-aware workflow logic.
  - API layer: HTTP concerns only (request parsing, response formatting, status codes, route decorators).
- API routes must not contain direct business logic beyond minimal transport concerns.
- Service layer should be the primary unit-test target for business behavior; API tests validate contract and integration.

4. Test strategy baseline:
- Unit tests for auth and permission logic.
- API integration tests for endpoint success/failure matrix by role.
- Frontend component/service tests for auth state, permission gating, and request behavior.

Note:
- These quality gates are stricter than minimum rubric and are required internally before phase advancement.

## 7) High-Level Phase Plan (Planning Session v1)

Phase 0 - Baseline and constraints:
- Confirm branch strategy, environment setup, and immutable planning docs.
- Freeze contract assumptions and acceptance checklists.
- Publish and lock API specification and JWT/auth specification documents.

Phase 1 - Auth foundation:
- Complete Auth0 tenant signup/setup and configure application/API/roles/permissions.
- Implement JWT parsing/verification and permission checks.
- Implement/validate reusable auth decorator behavior.

Phase 2 - Required backend endpoints:
- Implement all 5 required endpoints and error handlers.
- Add endpoint tests and role-based access tests.

Phase 3 - Frontend integration:
- Configure environment values.
- Validate public/barista/manager flows against backend behavior.
- Add/expand frontend tests for role-gated UX and service behavior.

Phase 4 - Submission hardening:
- Run full validation checklist.
- Ensure README/run instructions are clear and current.
- Refresh Postman JWTs near submission window.
- Prepare zip submission package with expected structure intact.

Phase 5 - Standout enhancements (optional, post-core pass):
- Auth0 user management endpoints and admin role model.
- Deployment and/or MFA/social auth enhancement.
- Targeted UI enhancement while preserving starter compatibility.

## 8) Validation Matrix (What must be true before submission)

Core pass criteria:
- All rubric-required endpoints implemented and tested.
- Auth0 RBAC correctly enforced per role matrix.
- Postman collection passes with valid role tokens.
- Frontend runs and demonstrates expected role-based behavior.
- Starter structure remains intact for reviewer workflow.

Phase 0 exit criteria:
- Source-of-truth document exists and is approved.
- API_SPECIFICATION.md exists and defines required endpoint contract.
- JWT_AUTH_SPEC.md exists and defines signature verification model and auth guardrails.
- Explicitly documented that submission DB expectation is SQLite, not Postgres.

Internal quality pass criteria:
- Backend pytest coverage >= 80%.
- Frontend test coverage >= 80%.
- Security/separation/testing guardrails satisfied and documented.

## 9) Anti-Drift Warnings (Use before any major change)

Stop and re-check this source of truth if a proposed change:
- Renames/moves key starter folders or files.
- Changes expected endpoint names/paths/methods.
- Introduces new frameworks, major version jumps, or substantial architecture rewrites.
- Prioritizes polish/features over incomplete rubric requirements.
- Reduces testability or reviewer reproducibility.

If any trigger is hit:
- Record rationale first in PROJECT_PROGRESS.md.
- Require explicit decision to proceed.
- Confirm no violation of submission contract.

## 10) Governance

Immutability rule:
- Treat this file as locked after approval.
- Prefer appending clarifications rather than rewriting intent.

Change threshold ("big if" rule):
- Change only for: rubric correction, discovered factual conflict, or blocker that threatens submission success.

Progress logging rule:
- Do not log daily execution progress here.
- Log all phase execution and evidence in PROJECT_PROGRESS.md.

## 11) Submission Gotchas (Explicit Callouts)

These are high-impact pitfalls that can cause rubric failure or reviewer friction.

1. Database expectation is SQLite, not Postgres:
- This starter uses SQLite in the backend model configuration.
- Do not migrate to Postgres for the submission path unless explicitly required by instructor guidance.
- Rationale: switching DB engines introduces unnecessary risk and may break reviewer expectations or starter workflow.

2. Keep starter project format intact:
- Reviewer workflows assume the provided starter layout and key file paths.
- Avoid moving/renaming key backend/frontend files, route modules, or collection paths.

3. Auth0 token expiry can invalidate reviewer checks:
- The rubric warns that JWT tokens can expire before review.
- Refresh and export the Postman collection close to submission time.

4. Required endpoint contract is fixed:
- Endpoint names, paths, and methods must match rubric exactly.
- Avoid REST redesigns that are cleaner but non-compliant with expected contract.

5. Frontend environment configuration file naming can be confusing:
- Use the actual project file in the frontend source tree for environment values.
- Verify path and filename directly in workspace before changes; do not rely on README wording alone.

6. Windows shell command differences:
- Some README commands use Unix-style environment variable syntax.
- Provide Windows-compatible run notes so reviewer/tester setup remains reproducible in this environment.

7. Submission target is course project, not lesson exercises:
- Lesson folders may contain placeholders or incomplete samples.
- Prioritize correctness and completeness under the starter_code project directories used for grading.

8. Internal quality gates are stricter than rubric minimum:
- Backend pytest coverage >= 80% and frontend coverage >= 80% are required to pass to next phase.
- Do not close a phase until coverage evidence is logged in PROJECT_PROGRESS.md.

## 12) Phase Execution Playbooks (Detailed)

This section converts the high-level plan into execution-ready work packages for manual work or mini-model execution.

## 12.1 Global Mini-Model Operating Instructions

Use these instructions at the start of every mini-model session:
- Mission: deliver submission-safe progress only, aligned to this source of truth and companion specs.
- Hard constraints:
  - Do not change required endpoint names, methods, or response envelopes.
  - Do not move or rename starter structure paths.
  - Do not introduce framework rewrites or major dependency upgrades.
  - Do not commit secrets.
- Execution style:
  - Prefer small, isolated edits.
  - Run verification after each logical change.
  - Log evidence and decisions in PROJECT_PROGRESS.md.
- Stop conditions requiring human review:
  - Any anti-drift trigger from Section 9 is hit.
  - Auth0 flow requires account-level decision not already documented.
  - Coverage drops or regressions appear outside target scope.

Required mini-model output format per task:
- What changed
- Why it changed
- Validation run and result
- Risks introduced
- Next suggested step

## 12.2 Phase 0 - Baseline and Constraints

Objective:
- Finalize planning artifacts and freeze execution guardrails.

Detailed tasks:
1. Confirm source-of-truth, API spec, and JWT spec exist and are cross-consistent.
2. Confirm gotchas and anti-drift warnings include submission-critical pitfalls.
3. Confirm quality gates include backend and frontend coverage >= 80%.
4. Confirm layered architecture policy is documented.
5. Confirm progress log template and current phase entry are ready.

Acceptance criteria:
- Planning artifacts are complete and approved.
- No unresolved ambiguity about DB, auth issuer, endpoint contract, or role matrix.

Mini-model instructions:
- Documentation changes only.
- No runtime code edits.

## 12.3 Phase 1 - Auth Foundation

Objective:
- Establish working Auth0 integration and reusable backend auth enforcement.

Detailed tasks:
1. Auth0 tenant setup:
  - Create tenant/account.
  - Create SPA application for frontend.
  - Create API identifier for backend audience.
  - Enable RBAC and permission claims in access token.
2. Define permissions:
  - get:drinks
  - get:drinks-detail
  - post:drinks
  - patch:drinks
  - delete:drinks
3. Define roles:
  - Barista with read permissions.
  - Manager with full drink permissions.
4. Create test users and assign roles.
5. Implement backend auth module responsibilities:
  - Authorization header parsing.
  - JWT verification via JWKS.
  - Claim validation for issuer and audience.
  - Permission checks.
  - Consistent AuthError behavior.
6. Add targeted auth unit tests.

Acceptance criteria:
- Valid token accepted for matching permission.
- Missing/invalid/expired/insufficient tokens rejected with structured errors.
- Auth tests pass.

Mini-model instructions:
- Edit auth code and auth tests only unless a dependency is required.
- Do not implement business endpoint logic in this phase.
- Use the JWT spec as the single auth contract.

## 12.4 Phase 2 - Required Backend Endpoints

Objective:
- Implement and verify all rubric-required API endpoints and error handling.

Detailed tasks:
1. Implement required routes:
  - GET /drinks
  - GET /drinks-detail
  - POST /drinks
  - PATCH /drinks/<id>
  - DELETE /drinks/<id>
2. Apply requires_auth permission guards to secured routes.
3. Implement error handlers at minimum for 404, 422, and AuthError.
4. Keep route handlers thin and delegate business logic to service layer.
5. Add backend endpoint tests:
  - Success by role
  - Permission denied
  - Missing token
  - Not found cases
  - CRUD lifecycle checks
6. Confirm backend coverage is >= 80%.

Acceptance criteria:
- Endpoint behavior matches API_SPECIFICATION.md.
- Test suite passes with coverage threshold met.

Mini-model instructions:
- Follow layered architecture:
  - API layer for HTTP transport concerns.
  - Service layer for logic.
  - Data access for persistence operations.
- If service/data-access modules do not exist, create minimal versions without reorganizing starter paths aggressively.

## 12.5 Phase 3 - Frontend Integration

Objective:
- Complete frontend configuration and validate role-aware user flows.

Detailed tasks:
1. Configure frontend environment variables for backend URL and Auth0 values.
2. Validate login callback token capture and token persistence.
3. Validate permission-driven UI behavior for public, barista, manager.
4. Verify drinks retrieval, create/update/delete flows against backend.
5. Add or improve frontend tests for:
  - Auth service token handling
  - Permission checks
  - Drinks service request behavior
  - Core page/component behavior tied to roles
6. Confirm frontend coverage is >= 80%.

Acceptance criteria:
- Frontend runs via ionic serve with expected behavior.
- Frontend tests pass with coverage threshold met.

Mini-model instructions:
- Prefer focused service and component edits.
- Avoid visual overhauls in this phase unless fixing clarity/usability blockers.

## 12.6 Phase 4 - Submission Hardening

Objective:
- Produce a reviewer-ready submission package with reproducible validation evidence.

Detailed tasks:
1. Run backend and frontend tests and capture final coverage evidence.
2. Re-verify endpoint contract, role matrix, and error envelopes.
3. Update README run instructions and platform notes where needed.
4. Refresh Postman role tokens close to submission time.
5. Export Postman collection to required file path.
6. Verify ignore rules and remove accidental local artifacts.
7. Build final zip preserving required structure.

Acceptance criteria:
- Rubric checks pass with evidence logged.
- Submission package preserves starter contract and expected files.

Mini-model instructions:
- No feature expansion in this phase.
- Only stabilization, validation, and documentation fixes.

## 12.7 Phase 5 - Standout Enhancements (Optional)

Objective:
- Implement selected standout items only after core submission readiness is confirmed.

Detailed tasks:
1. Choose enhancement track(s):
  - Auth0 management endpoints and expanded role model.
  - Deployment.
  - MFA/social auth options.
  - Frontend enhancements.
2. Define strict boundaries so enhancements do not break core contract.
3. Add tests for any new endpoint or permission logic.
4. Update docs with setup and rollback notes.

Acceptance criteria:
- Core rubric compliance remains intact.
- Enhancements are optional, isolated, and documented.

Mini-model instructions:
- Run enhancement work in a separate branch.
- Re-run full core validation before merging enhancement changes.

## 13) Phase Gate Checklist

Before closing any phase, all must be true:
- Scope delivered matches the phase objective.
- Required tests for that phase pass.
- Coverage target remains satisfied or improved.
- No anti-drift trigger unresolved.
- PROJECT_PROGRESS.md updated with evidence, risks, and decisions.
