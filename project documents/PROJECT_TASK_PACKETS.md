# PROJECT TASK PACKETS (Mini-Model Ready)

Last updated: 2026-09-13
Scope: Submission-first execution packets for Phases 0-5
Authority: Must follow project documents/PROJECT_SOURCE_OF_TRUTH.md, project documents/API_SPECIFICATION.md, and project documents/JWT_AUTH_SPEC.md

## How to Use This Document

- Execute one packet at a time.
- Do not start next packet until phase gate checks pass.
- Every packet run must append evidence to project documents/PROJECT_PROGRESS.md.
- If any anti-drift trigger is hit, stop and request human decision.

## Global Mini-Model Prompt (Prefix For Every Run)

Use this exact prefix before phase-specific instructions:

You are executing a submission-first task for the Udacity IAM Coffee Shop project.
Constraints:
1. Preserve starter project structure and expected file paths.
2. Do not rename required endpoints, methods, or response envelope keys.
3. Do not introduce framework rewrites or major dependency upgrades.
4. Do not commit secrets or real credentials.
5. Keep route handlers thin; follow data access, service, and API layering.
6. Run validation after each logical change and report evidence.
7. If a change risks rubric mismatch, stop and ask for human approval.
Output format:
- What changed
- Why changed
- Validation evidence
- Risks/blockers
- Next step

## Packet P0 - Phase 0 Baseline and Constraints

Goal:
- Confirm planning artifacts are complete, aligned, and approval-ready.

Inputs:
- project documents/PROJECT_SOURCE_OF_TRUTH.md
- project documents/API_SPECIFICATION.md
- project documents/JWT_AUTH_SPEC.md
- project documents/PROJECT_PROGRESS.md

Execution steps:
1. Verify all four documents exist.
2. Verify DB expectation explicitly states SQLite, not Postgres.
3. Verify Auth0 ownership model and RS256 verification expectations are explicit.
4. Verify required endpoint contract in API spec exactly matches rubric.
5. Verify internal quality gates include backend and frontend coverage >= 80%.
6. Verify phase gate checklist exists and requires evidence logging.
7. Log Phase 0 validation outcome in PROJECT_PROGRESS.

Acceptance checks:
- No unresolved ambiguity in endpoint contract, auth model, role matrix, or DB type.
- Planning docs are consistent and ready for execution handoff.

Required evidence to log:
- File list checked
- Any discrepancy found and resolution
- Final approval note for Phase 0

Stop conditions:
- Any contradiction between source-of-truth and companion specs.

## Packet P1 - Phase 1 Auth Foundation

Goal:
- Deliver working Auth0 integration and backend auth enforcement foundation.

Inputs:
- backend/src/auth/auth.py
- frontend/src/environments/environment.ts
- project documents/JWT_AUTH_SPEC.md

Execution steps:
1. Complete Auth0 tenant setup tasks (tenant, app, API, RBAC claims).
2. Configure roles and permissions per matrix.
3. Create barista and manager users in Auth0 and assign roles.
4. Implement backend auth functions:
- token header parsing
- JWKS retrieval and token verification
- issuer/audience validation
- permission checking
- consistent AuthError raising
5. Add/expand auth-focused backend tests for happy and failure paths.
6. Validate no endpoint business logic is mixed into auth module.
7. Log setup decisions and test evidence in PROJECT_PROGRESS.

Acceptance checks:
- Valid role token passes required permission checks.
- Missing/invalid/expired/insufficient tokens fail with structured errors.
- Auth tests pass.

Required evidence to log:
- Auth0 config checklist completion
- Test output summary
- Open risks (token TTL, environment config)

Stop conditions:
- Need to deviate from RS256/JWKS model.
- Missing tenant capability for required RBAC claims.

## Packet P2 - Phase 2 Required Backend Endpoints

Goal:
- Implement all required API routes and error handlers with layered architecture.

Inputs:
- backend/src/api.py
- backend/src/database/models.py
- project documents/API_SPECIFICATION.md

Execution steps:
1. Implement required routes:
- GET /drinks (public)
- GET /drinks-detail (secured)
- POST /drinks (secured)
- PATCH /drinks/<id> (secured)
- DELETE /drinks/<id> (secured)
2. Enforce permission decorators on secured routes.
3. Implement structured error handlers for 404, 422, and AuthError at minimum.
4. Create minimal service/data-access modules if needed to keep API layer thin.
5. Add endpoint tests covering role access, token failures, and CRUD lifecycle.
6. Run coverage and verify backend is >= 80%.
7. Log evidence and residual risks in PROJECT_PROGRESS.

Acceptance checks:
- Endpoint contract exactly matches API spec.
- Role behavior matches source-of-truth matrix.
- Backend test suite passes with coverage >= 80%.

Required evidence to log:
- Endpoint test matrix (route x role x expected status)
- Coverage percent and command used

Stop conditions:
- Any endpoint rename/path change is proposed.
- Coverage target not met after reasonable iteration.

## Packet P3 - Phase 3 Frontend Integration

Goal:
- Complete frontend auth configuration and role-aware behavior with tests.

Inputs:
- frontend/src/environments/environment.ts
- frontend/src/app/services/auth.service.ts
- frontend/src/app/services/drinks.service.ts
- relevant pages/components under frontend/src/app/pages

Execution steps:
1. Configure frontend environment values for Auth0 and backend URL.
2. Validate login redirect and callback token parsing.
3. Validate token persistence and logout behavior.
4. Validate UI permission gating for public, barista, and manager flows.
5. Validate CRUD interactions map to backend permissions and responses.
6. Add/expand frontend tests for services and role-dependent UI behavior.
7. Run coverage and verify frontend is >= 80%.
8. Log evidence and issues in PROJECT_PROGRESS.

Acceptance checks:
- App runs with ionic serve and expected role behavior.
- Frontend test suite passes with coverage >= 80%.

Required evidence to log:
- Manual flow checks for each role
- Coverage report summary

Stop conditions:
- Changes require framework migration or heavy UI rewrite.

## Packet P4 - Phase 4 Submission Hardening

Goal:
- Produce reviewer-ready, reproducible, submission-safe package.

Inputs:
- backend and frontend README files
- backend postman collection file
- .gitignore and project artifact layout

Execution steps:
1. Run full backend and frontend test suites; confirm coverage thresholds.
2. Verify endpoint contract, error shapes, and RBAC matrix one final time.
3. Validate run instructions for current environment clarity.
4. Refresh role JWTs near submission time.
5. Export/update required Postman collection path.
6. Ensure ignore rules prevent local artifacts/secrets leakage.
7. Assemble zip with required structure intact.
8. Log final verification checklist in PROJECT_PROGRESS.

Acceptance checks:
- Rubric-required functionality verified end to end.
- Submission package preserves expected starter structure.

Required evidence to log:
- Final test and coverage summaries
- Postman validation outcome
- Submission checklist completion status

Stop conditions:
- Missing valid role token set near submission cutoff.

## Packet P5 - Phase 5 Standout Enhancements (Optional)

Goal:
- Implement optional enhancements without breaking core rubric contract.

Inputs:
- source-of-truth standout section
- JWT/auth spec for management credential handling

Execution steps:
1. Select one enhancement track at a time.
2. Define boundaries and rollback plan before coding.
3. Implement with isolated, test-backed changes.
4. Re-run core regression checks from Phases 2-4.
5. Log enhancement value and any tradeoffs in PROJECT_PROGRESS.

Acceptance checks:
- Core rubric behavior remains unchanged and passing.
- New functionality is documented and tested.

Required evidence to log:
- Regression test pass summary
- Enhancement-specific test summary

Stop conditions:
- Enhancement threatens submission readiness timeline.

## Per-Task Command Checklist Template

Use this minimal template when assigning a task to a mini model:

Task ID:
Phase:
Objective:
Files allowed to edit:
Files forbidden to edit:
Required validations:
Acceptance criteria:
Evidence to record in PROJECT_PROGRESS:
Rollback plan:

## Definition of Done For Any Packet

A packet is done only when:
1. All acceptance checks pass.
2. No unresolved stop condition exists.
3. Evidence is appended to PROJECT_PROGRESS.
4. Next packet prerequisites are satisfied.
