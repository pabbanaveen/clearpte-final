# ClearPTE Production Readiness Plan

**Status:** Discovery and planning document. This is not a claim that the application is production-ready.
**Scope:** Existing React/TypeScript frontend, FastAPI/Python backend, SQLAlchemy data access, and planned third-party services.

## 1. Product objective

ClearPTE is intended to provide PTE Academic practice for Speaking, Writing, Reading, and Listening. Learners should be able to register, choose practice, answer questions, receive useful feedback/scores, and review durable progress. Authorized content managers should create/import questions. If monetization is enabled, learners should be able to buy a plan and have entitlements applied reliably.

## 2. Current integrations: what is really connected

| Capability | Current state | Notes |
|---|---|---|
| Login/registration | Frontend email/password signup/login uses Firebase Auth and requires email verification; database-auth endpoints were removed from the backend | Firebase web configuration is supplied by frontend build-time variables. FastAPI maps verified Firebase UIDs to `firebase_identities` rows. Live backend verification still requires project/ADC setup and an end-to-end live token test. |
| Firebase | Firebase Web SDK handles frontend auth; Firebase Admin verifies backend tokens | Verified-token dependencies protect question, scoring, profile, and upload routes. Question uploads require a trusted Firebase `admin` custom claim. No claim provisioning workflow exists yet, so uploads are denied to all users until this is safely provisioned. Hosting deployment and media storage are not implemented. |
| Payments | No payment gateway integration found | `payments`, `subscriptions`, and plan-related SQL are schema ideas only; no Stripe, Razorpay, or PayPal checkout/webhook implementation was found. |
| Question data | SQLAlchemy models, allow-listed learner read responses, CRUD/read/upload routes, and Alembic schema revisions for the active ORM tables | Some frontend practice screens fetch API data; many use bundled mock datasets. `tables.sql` is now explicitly labeled a legacy draft and is not the deployment schema. Attempt/score persistence remains unimplemented. |
| User media storage | No durable object-storage integration found | Audio recordings generally go from browser as an upload to an API for scoring and are put in temporary files, then deleted. Question media is often represented as a URL. No signed upload/download workflow or retention policy was found. |
| AI scoring | OpenAI SDK is used for transcription and scoring | `OPENAI_API_KEY` is server-side. Some routes call transcription (`whisper-1`) and chat models (including `gpt-4o-mini` and `gpt-4o`). Keep keys only on the server and track per-feature costs. |
| Email | Firebase verification emails are initiated by the frontend after registration; unverified Firebase accounts are denied by both frontend auth and backend token dependencies | Live provider configuration and end-to-end tests, password reset tests, and operational email checks remain to be completed. |
| Progress/analytics | Frontend service definitions and sample/static screens | Frontend calls `/progress` paths but no progress router was found in the backend route tree. Some scores are hard-coded and some attempts only persist in browser localStorage. |

## 3. Proposed cost-conscious architecture

Treat these as candidates to validate against launch regions, expected traffic, compliance, and current provider pricing. Do not select a provider solely on headline price.

### Recommended first production shape

- **Frontend:** Keep React initially. Deploy static assets to a CDN-backed static host. Choose a single cloud provider/region if convenient for operations. Keep the app's backend URL in build-time configuration and never put server secrets in the React bundle.
- **Backend:** FastAPI in a managed container/service with health checks, TLS, autoscaling limits, request timeouts, structured logs, and separate staging/production environments. Avoid the current development server/reload mode in production.
- **Relational data:** Managed PostgreSQL for users, question metadata, entitlements, attempts, scores, and audit events. PostgreSQL is a natural fit for the existing SQLAlchemy/PostgreSQL schema. Local SQLite remains for development/tests only. Use migrations (Alembic), backups, least-privilege DB users, and connection pooling.
- **Authentication:** Prefer a managed identity provider over extending bespoke password/JWT code. Firebase Authentication is a pragmatic low-startup-cost candidate because the project already has Firebase configuration; alternatively compare a managed auth service such as Supabase Auth or an OIDC provider. Pick exactly one identity source of truth. Verify provider-issued tokens on every protected backend request. Add email verification, password reset, rate limits, account disable/role handling, and secure browser sessions. Never trust a role supplied by the browser.
- **Audio/video and uploaded files:** Use private object storage (for example Google Cloud Storage if already on Google Cloud; compare S3-compatible storage and other providers for expected egress). Upload/download with short-lived signed URLs; validate size, content type, ownership, and duration. Keep object keys in the database, not media bytes. Use lifecycle rules and explicit deletion/retention. Avoid serving private learner audio from public URLs.
- **AI scoring:** Keep OpenAI calls in backend workers/routes. Add per-user quotas, rate limits, request size limits, timeouts, retry/backoff for transient errors, idempotency where possible, and metering by task/model. Use lower-cost suitable models for routine feedback and reserve more capable/expensive models for tasks where evaluation quality justifies it. Version prompts and rubrics, validate structured JSON using Pydantic, and test scoring with curated examples. Do not claim AI scores are official PTE scores. Define consent, retention, and deletion for audio sent to AI providers.
- **Payments (only if monetization is approved):** Select gateway based on merchant country, currency, taxes, and payout needs. Stripe Checkout/Billing is a good default where supported; Razorpay may fit India-focused merchants; PayPal can be an optional wallet where commercially useful. Compare supported countries and all fees before deciding. Start with hosted checkout to reduce PCI scope. Server creates checkout sessions; only signed, replay-safe webhooks grant/revoke entitlements. Never trust the browser redirect as proof of payment; never store card details.
- **Email delivery:** Use the identity provider's verification/reset emails initially. For transactional product emails, choose a reputable service after confirming regional deliverability and data terms.
- **Operations:** Centralized error monitoring, uptime/health monitoring, log redaction, audit trails, secrets manager, infrastructure configuration, CI builds/tests, dependency and secret scanning, backups, restore drills, and documented incident response.

### Keep initial scope small

Do not add payment or video streaming until the product requirements justify them. For an MVP, prioritize the content catalog, audio prompts, learner recordings, scoring, and durable progress. Video can be deferred; if introduced, distinguish simple static lesson videos (object storage/CDN) from adaptive streaming (specialized video platform) and compare costs/rights requirements.

## 4. Critical gaps to close before production

### P0 — Security and data safety

1. Replace fallback JWT signing secrets with a required secret-manager value; fail startup in production if missing. Rotate any credentials previously committed or shared, including historical Git secrets.
2. Verify Firebase Admin project/ADC configuration in staging with real Firebase ID tokens; the backend now has token verification dependencies, but mocked tests are not proof that cloud configuration is correct.
3. Enforce admin permissions on question uploads/changes in the backend. UI hiding is not authorization.
4. The frontend now uses Firebase Auth for signup/sign-in and email verification. Legacy first-party register/login endpoints were removed. The backend checks Firebase token validity and verified email; finish live project/ADC validation, create trusted custom-claim provisioning for administrators, add throttling and password-reset checks as appropriate, and never rely on frontend role/session state for API authorization.
5. Stop returning raw internal exception messages to callers. Redact secrets, uploaded content, auth headers, and personal data from logs.
6. Add upload size/type limits, safe temporary-file handling, and ownership checks. Treat recordings and learner submissions as sensitive personal data.
7. Define policy and consent for sending learner audio/text to AI providers, retention, deletion, and age/privacy requirements for target markets.

### P1 — Make the product paths actually end-to-end

1. Standardize all frontend calls on one API client/base URL. Current services use both `REACT_APP_BACKEND_URL` and `REACT_APP_API_URL`; the latter has no checked-in local config. Eliminate `/api` prefix duplication and centralize auth/error behavior.
2. The backend now exposes authenticated self-profile `GET/PUT /api/users/profile`, keyed by Firebase UID with validated inputs. Update the frontend profile service to use this contract and the shared authenticated API client.
3. Implement the progress/attempt backend or remove/nonfunctionalize the frontend `/progress` promises. Persist attempts and scores server-side by authenticated user.
4. Question catalog endpoints now use explicit learner-safe allowlists; answer keys, sample solutions, and scoring rubrics are not returned. Update practice/scoring contracts to submit answers to the backend and have it score against server-held keys. Decide which question types are DB-backed versus static, seed content, and avoid silently showing demo content as real progress.
5. Active ORM tables now have an Alembic baseline, list-valued fields use portable JSON, and SQLite runtime table creation is limited to local/test environments; staging/production require explicit non-SQLite `DATABASE_URL`. Validate this migration chain on PostgreSQL, add attempts/scores as later migrations, and never rely on runtime `create_all` for production.
6. Build one vertical slice per skill: fetch prompt → answer/record → backend validation/scoring → result → persisted attempt → history/progress.
7. Add a robust admin content workflow: server-side role check, validation, preview, transaction, audit trail, rollback/duplicate handling, and file import error report.
8. Correct evaluation routes to use a guarded OpenAI client (some routes currently dereference the client directly even when the key is missing), typed JSON schemas, current supported model identifiers, and predictable API errors.

### P2 — Operability and launch quality

- Separate dev/test/staging/prod configuration and origins; remove hard-coded production origins that are not needed.
- Use production ASGI server/container configuration, TLS, health/readiness checks, and graceful shutdown.
- Add automated unit, API integration, browser/e2e, authz, migration, upload, and AI contract tests. Mock paid AI in CI.
- Add usage budgets/alerts and rate limits for AI and storage; monitor latency, error rates, DB pool saturation, and cost per completed task.
- Add accessibility, mobile, browser, media-permission, and real-user testing. Label mock/sample numbers clearly or replace them.
- Establish privacy policy, terms, cookie/session policy, refund/cancellation terms if payments exist, data export/deletion, and content/licensing review.

## 5. Proposed data model areas

Keep PostgreSQL as the authoritative store for structured records. Finalize schema through migrations rather than manually executing the current SQL file.

- `firebase_identities`: a SQLAlchemy model and Alembic migration map stable Firebase UID, verified email, learner role, profile preferences, and timestamps. The migration is verified on disposable SQLite; PostgreSQL staging verification remains open.
- Existing local SQLite still contains an inherited password-auth `users` table with a test-only row. The new Firebase-first schema does not provision that table; no local data has been deleted. Export/retain it only if the product owner wants the old test record.
- Question/content tables: versioned prompt content, skill/type, difficulty, public/private state, media object key, answer rubric, created-by and timestamps.
- `practice_attempts`: user, question/content version, start/submit timestamps, status, time spent.
- `answers` and `scores`: typed response metadata, rubric/model/prompt version, score breakdown, feedback, model request id. Avoid storing large audio blobs here.
- `media_assets`: object key, owner, purpose, MIME type, byte size, duration, checksum, retention/deletion state.
- `plans`, `payment_events`, `entitlements`: provider IDs and webhook state. Payment-event rows need unique provider event IDs to prevent duplicate processing.
- `admin_audit_logs`: actor, action, target, timestamp, redacted details.

Do not persist full AI prompts/audio/transcripts by default unless needed and disclosed. Define retention and purge jobs.

## 6. Rollout sequence and exit criteria

### Phase 0 — Product and provider decisions

- Confirm launch countries, target users/ages, languages, expected monthly active users, free/paid model, supported payment currencies, data-residency constraints, audio/video retention, and monthly budget.
- Decide whether Firebase Auth or another managed identity provider is selected; decide hosting/storage provider based on current quote and region.
- Deliverable: approved architecture decision record and data-flow/privacy inventory.

### Phase 1 — Safe foundation

- Remove/rotate exposed secrets; add environment validation and secret manager.
- Standardize API URLs and CORS; pin/manage dependencies and add CI baseline.
- Add Alembic migrations, PostgreSQL staging, backups, and restore test.
- Exit: clean deployment from migrations; no secret scan findings; health/readiness succeeds.

### Phase 2 — Identity and permissions

- Implement chosen identity provider end-to-end, verify tokens server-side, email verification/reset, logout/session behavior, and admin roles.
- Exit: tests prove anonymous users cannot access protected APIs, learners cannot administer content, and role escalation attempts fail.

### Phase 3 — Learning vertical slice

- Implement one speaking task and one writing task end-to-end including persisted history. Standardize API schemas/errors. Then add remaining task types.
- Exit: browser tests prove fetch → submit → result → reload history for each supported task family.

### Phase 4 — Media and AI reliability

- Add private object storage, signed URLs, media limits/retention; adapt AI calls with typed schemas, quotas, model/prompt versioning, monitoring, and cost ceilings.
- Exit: tests cover invalid/oversize media, upload ownership, provider timeout, AI error, retries, and deletion.

### Phase 5 — Payments (if required)

- Implement hosted checkout, signed webhook processing, idempotent payment events, entitlement checks, cancellation/refund handling, and reconciliation.
- Exit: sandbox tests cover success, failure, duplicate/out-of-order webhook, refund, cancellation, and entitlement expiry.

### Phase 6 — Launch readiness

- Load/security/accessibility testing; legal/privacy docs; dashboards/alerts; incident runbooks; restore drill; staged rollout with spend limits.
- Exit: named owners, support process, rollback plan, agreed SLOs, privacy review, and budget alerts.

## 7. Questions the product owner must decide

1. Which countries will accept payments from and pay out to the business entity?
2. Is the product free, subscription-based, one-time purchase, or freemium? Which features are gated?
3. Who are the users, and can minors use it?
4. Is learner audio stored after scoring? If yes, for how long and for what purpose?
5. Which hosting/cloud account and data region are preferred? Is there an existing GCP/Firebase account to retain?
6. Expected users, concurrent scoring requests, monthly audio minutes, and AI budget?
7. Is AI feedback practice guidance only, and what disclaimer/appeal path is needed for scores?
8. Who can create admins, manage content, approve payments/refunds, and handle deletion requests?

## 8. Decision recommendation

For the lowest operational risk at early scale: keep FastAPI + React, choose a managed PostgreSQL service, use one managed identity provider, private object storage with signed URLs, and keep OpenAI behind the backend with quotas. Defer payments until pricing/country requirements are clear; when needed, use a hosted checkout supported in the merchant's country and a webhook-driven entitlement model. Choose Google Cloud storage/hosting if the existing project is maintained and its regional total cost is favorable; compare at least one alternative with actual expected egress, database, and AI volumes before committing.
