# ClearPTE Backend Completion Plan

**Goal:** Make the FastAPI backend safe, data-backed, testable, and deployable before wiring every frontend feature to it. This plan tracks work; completion requires the stated tests and staging evidence, not just code changes.

**Current decision:** Keep Firebase Authentication for identity, FastAPI for APIs, and SQLAlchemy/PostgreSQL for product data. Firebase handles passwords, sign-in, email verification, and password reset emails. FastAPI verifies Firebase ID tokens and owns API authorization. Firebase client configuration is not a server credential. The owner has confirmed there are test users only.

**No cloud deployment or paid provider calls are part of local implementation.** Cloud Run and managed PostgreSQL deployment may require billing. Do not deploy the inherited Cloud Build configuration unchanged; it targets another project.

## Backend exit gates before deployment

### Phase A — Secure API foundation

- [x] Firebase ID token verification dependency checks signature, revocation, project, and verified email.
- [x] Require verified Firebase identity for question, scoring, profile, and upload route families; admin uploads require a trusted server-issued admin claim.
- [x] Remove unused first-party password login/register endpoints from backend.
- [ ] Verify configured Firebase project and ADC with real local Firebase ID tokens (current tests mock provider verification).
- [ ] Establish a reviewed, auditable admin-claim grant/revoke process. Until then, question upload routes intentionally reject everyone without the claim.
- [ ] Review all endpoints, identity mapping, per-user ownership, payload limits, rate limits, and error/log redaction.
- [x] Return learner-safe allow-listed question DTOs. Correct answers, sample solutions, scoring references, and rubrics are omitted from learner catalog responses; unknown question model types fail closed.
- [ ] Add server-side answer/scoring handling and end-to-end contracts. Frontend practice paths that relied on receiving answer keys from the question API must be updated before they are considered functional.
- [x] Stop the health/readiness route from returning raw database exception text and make database failure produce an appropriate unhealthy HTTP status.

### Phase B — Database and identity mapping

- [x] Define stable Firebase UID-to-application-user mapping in a dedicated `firebase_identities` table; Firebase signups are provisioned idempotently and do not require local password hashes.
- [x] Replace insecure caller-ID profile lookup with authenticated `GET/PUT /api/users/profile`, validated score/date fields, and a server-created student role.
- [x] Define the active current schema for Firebase identity/profile and question catalog ORM tables. New databases no longer create the unused first-party password tables; local legacy test rows are left untouched. Attempt/answer/score/audit tables remain future work in the vertical-slice phase.
- [x] Align migration definitions with active ORM metadata; list-valued content columns use portable JSON and upload parsing returns typed Python lists. The old hand-written `tables.sql` is marked legacy and must not be executed.
- [x] Add Alembic revisions for Firebase identity and active question catalog tables; disposable SQLite upgrade/downgrade and no-drift checks pass.
- [ ] Apply/test the migration chain against a new staging PostgreSQL database. PostgreSQL-specific behavior, permissions, backups, and restore are not validated yet.
- [x] Require explicit `DATABASE_URL` for staging/production and reject SQLite in those environments; runtime `create_all` is limited to local/test SQLite.
- [ ] Add PostgreSQL connection/readiness tests, backups, and a restore rehearsal.

### Phase C — One complete learning API slice

- [x] Pick Read Aloud and define typed score/feedback DTOs.
- [x] Fetch a question without answer keys; accept a bounded, typed audio file; invoke a guarded scoring service with strict response validation.
- [x] Persist attempt, scores/feedback, model/rubric version, and timestamp under verified Firebase UID. Do not retain audio or raw transcription.
- [x] Add authenticated, paginated history scoped to the current Firebase UID.
- [x] Test success with mocked scoring, invalid media, unknown question, provider failure, duplicate idempotency key, pagination, and cross-user history exclusion.
- [ ] Run end-to-end scoring using a configured key in an approved staging environment; routine tests remain mocked and incur no AI charges.
- [ ] Add per-user rate/quota enforcement and an explicit budget ceiling before allowing client production traffic.

### Phase D — Complete and harden remaining backend APIs

- [ ] Normalize API errors, schemas, pagination, status codes, and OpenAPI contracts across all route families.
- [ ] Fix profile contract/ownership and seed/import workflows. Validate bulk imports, transactions, duplicates, and audit records.
- [x] Add 10 MB audio and MIME limits to the legacy evaluation/audio-comparison routes, use the guarded OpenAI client with bounded timeout/retries, and move blocking Read Aloud scoring off the async event loop.
- [x] Replace model-output `eval()` with strict JSON and range checks; sanitize errors from evaluation and question-upload routes.
- [ ] Add global request-body limits, per-user AI quotas/rate limits, request budget ceilings, cost monitoring, and duration validation.
- [ ] Ensure every remaining endpoint has typed schemas and safe error handling; review bulk-import duplicate/idempotency and transaction semantics. Health/readiness and learner answer-key filtering are already addressed.
- [ ] Build backend unit/integration/authorization/migration tests with paid AI mocked.

## Still required before backend staging

- [ ] Configure and verify real Firebase Admin ADC/project settings with a real verified test-account token. Current auth tests mock Firebase verification.
- [ ] Provision a new staging PostgreSQL database and test Alembic upgrade/connection/readiness there; SQLite is the only migration target validated to date.
- [ ] Add persistent attempts/history and validated contracts for each supported task type; only Read Aloud currently has a complete backend-scored persisted attempt route.
- [ ] Add per-user scoring quotas/rate limits, a spend ceiling, and monitored provider usage. The 10 MB media cap is not a cost quota.
- [ ] Review/validate JSON response schemas and score ranges for every legacy writing/speaking evaluation route; safely reject malformed model output.
- [ ] Create a trusted admin custom-claim grant/revoke process and prove admin imports succeed only for approved identities.
- [ ] Fix all import-route transaction rollback, duplicate detection, and realistic error-report behavior; run route-level tests for each content type.
- [ ] Confirm backup/restore for PostgreSQL, staging config/secrets/CORS, and Cloud Run service identity. Do not deploy production until owner approves cloud billing and launch.

### Phase E — Staging backend deployment gate

- [ ] Confirm Google Cloud project ownership, region (India audience; Mumbai is provisional), billing/cost approval, and staging/production separation.
- [ ] Replace inherited project IDs/service accounts/connector settings. Choose one deployment target (Cloud Run); do not deploy App Engine and Cloud Run accidentally.
- [ ] Configure Secret Manager and Cloud Run service identity; verify Firebase Admin ADC and database permissions without service-account key files.
- [ ] Provision staging PostgreSQL, apply migrations, seed non-sensitive test content, verify backups, and check readiness.
- [ ] Deploy backend to staging only, run Firebase-token and API end-to-end checks, review logs/costs, then obtain explicit production-cutover approval.

## Recommended execution order

1. Finish Phase A safety gaps, including hidden-answer API responses and live Firebase token validation.
2. Finish Phase B schema/migrations/identity mapping.
3. Deliver and test Phase C as the first persisted vertical slice.
4. Bring all other backend routes through Phase D tests and contract checks.
5. Deploy to staging only after A–D exit criteria pass; production deployment is a separate approved step.
6. Then connect frontend features against the tested OpenAPI contracts and run browser end-to-end tests.

## Current risks / owner decisions

- Are existing question prompts/media/import files worth preserving, even though current users are test-only?
- Who is authorized to be a content administrator? Admin access must be provisioned from trusted server tooling, never from registration or browser storage.
- Is audio retained after scoring? Define purpose, consent, retention, and deletion before storing it.
- Approve the cloud budget and billing plan before creating Cloud Run/PostgreSQL resources or making live AI scoring calls.

See [PRODUCTION_READINESS_PLAN.md](PRODUCTION_READINESS_PLAN.md) for the broader product/security audit and [CLEARPTE_GO_LIVE_GUIDE.md](CLEARPTE_GO_LIVE_GUIDE.md) for owner-operated cloud setup steps.

## Migration commands (local/test databases only for now)

Run Alembic from the `backend` directory with `DATABASE_URL` set directly in the local environment. The URL must point to a disposable local/test database while validating these initial revisions. The current migration chain creates the Firebase identity/profile table and the active ORM question/content tables. It does not create future attempt/score/audit tables or the unused draft tables from `tables.sql`.

- Apply revisions: `alembic upgrade head`
- Inspect current revision: `alembic current`
- Inspect revision graph: `alembic history`
- Downgrade the new identity table only in a disposable test database: `alembic downgrade base`

Do not run a downgrade on a database with data you need. Existing local SQLite is an older `create_all` database with one test user row and is deliberately not being altered by migration tests. Do not target production or a shared database until the full product schema, backup/restore, and PostgreSQL migration tests have been reviewed.
