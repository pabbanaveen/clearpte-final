# ClearPTE Go-Live Guide

**Purpose:** A safe, beginner-friendly sequence for taking over the inherited ClearPTE codebase and preparing it for a live launch.

**Important:** This is a deployment plan, not a statement that the app is production-ready. Complete each phase in order. Do not deploy the inherited configuration as-is: the current deployment files contain references to a previous Google Cloud project and resources. Never paste API keys, passwords, service-account JSON, or tokens into chat, Git, or frontend code.

## Recommended first architecture

Keep the existing React frontend and FastAPI backend. Use one new Google Cloud project connected to Firebase:

| Need | Service | Responsibility |
|---|---|---|
| React website | Firebase Hosting | Serves the built frontend over HTTPS |
| Python API | Cloud Run | Runs FastAPI; not Firebase Hosting |
| Login | Firebase Authentication | Signup, sign-in, verification, password recovery |
| Existing relational application data | Managed PostgreSQL (Cloud SQL is the default to evaluate) | Users/profile mapping, questions, attempts, scores |
| User uploads | Private Google Cloud Storage bucket | Audio and other private media |
| Credentials | Google Secret Manager | OpenAI key, database credentials, other server-only secrets |
| AI evaluation | OpenAI API, called only by FastAPI | Transcription/scoring; usage must be monitored and limited |
| Payments, if/when approved | Payment provider such as Stripe | Hosted checkout; backend-verified webhooks only |

Firebase Hosting, Authentication, and Google Cloud services can be managed under one Google account/project, but they are distinct products with separate setup, permissions, configuration, and possible charges. Do not add Firestore merely because Firebase is in use: the application already uses SQLAlchemy and relational data, so decide and document the PostgreSQL target first.

## Phase 0 — Take ownership and protect existing data

- [x] Confirm whether the old app has real users: the owner confirmed it has test users only and no real users to migrate. Test accounts can be recreated in the new authentication system.
- [ ] Separately confirm whether question content, uploads, scores, or other test data should be retained. Back up anything valuable before replacing the old database or storage; test-only status does not automatically mean all content can be discarded.
- [ ] Get access to the source repository, current hosting accounts, DNS/domain, database, Firebase project (if any), and billing owner. Ask the previous developer/company for a handover and backup if possible.
- [ ] Create a backup/export of any existing production database and uploaded files before changing infrastructure. Do not run destructive migrations or reset accounts.
- [ ] Review Git history and current working changes for credentials and environment-specific configuration. If any real credential was committed or shared, revoke/rotate it through its provider; removing it from the current file alone is insufficient.
- [ ] Verify the current live app manually: frontend URL, API URL, account creation/login, a sample practice/scoring path, admin workflow, and current data persistence. Record what succeeds and fails.
- [ ] Keep this work in a branch or a copy of the repository. Do not discard the existing uncommitted changes.

**Stop here if:** you cannot establish whether production data exists, or do not have a backup/restore plan for it.

## Phase 1 — Create and secure your Google Cloud/Firebase project

- [x] Firebase project created: `clear-pte-67fdc` (confirmed from the owner's Firebase Console screenshot). Confirm Google Cloud project access/billing ownership before creating Google Cloud resources.
- [ ] Enable billing only after understanding the services you plan to create. Add budget alerts and review cost dashboards. Alerts notify you; they are not guaranteed spending caps.
- [x] User region confirmed: India. Recommended starting region is Mumbai (`asia-south1`) for Cloud Run, PostgreSQL, and Cloud Storage, subject to checking current product availability, pricing, and any data-residency requirements before creating resources. Keep these services in the same region where practical.
- [x] Firebase Authentication Email/Password sign-in enabled (confirmed by the owner).
- [ ] Enable only the required services as each phase needs them. Firebase Hosting configuration is scaffolded in [firebase.json](../firebase.json); no hosting deployment has been run. Cloud Run, Cloud SQL, Cloud Storage, and Secret Manager are deferred until billing/cost decisions.
- [ ] Use named service accounts with least privilege. Do not use a downloaded service-account key in the frontend or commit one to the repository.
- [ ] Create separate development/staging and production environments where feasible. Start in staging; do not point a test build at a real production database.

**Checkpoint:** You can identify the new project and region, billing alerts are configured, and you know which account owns recovery and billing.

## Phase 2 — Audit and adapt the inherited app before deployment

- [ ] Read [PRODUCTION_READINESS_PLAN.md](PRODUCTION_READINESS_PLAN.md) and compare it against the current code. Treat it as an audit to verify, not as proof that anything is already complete.
- [ ] Inspect and replace old project IDs, database instance names, service accounts, VPC connectors, regions, domains, and API URLs. In particular, do not deploy [backend/cloudbuild.yaml](../backend/cloudbuild.yaml) unchanged: it hard-codes the previous project's image, database instance, service account, and region.
- [ ] Choose one backend deployment path. This guide recommends Cloud Run; do not also deploy App Engine unless you intentionally choose it. Review [backend/app.yaml](../backend/app.yaml) as inherited configuration, not an instruction to deploy both.
- [ ] Verify the application starts locally with documented environment variables and a local/test database. Do not use production secrets for local development.
- [ ] Centralize frontend API configuration and verify the production build points to the new Cloud Run URL. The frontend currently uses `REACT_APP_BACKEND_URL`; frontend variables are included in the built bundle, so never put secrets there.
- [ ] Add tests for the critical paths before moving on. Mock OpenAI in routine tests so CI does not make paid calls.

**Checkpoint:** No deployment file silently targets the previous owner's project, and the app can be built and started locally without production credentials.

## Phase 3 — Configure PostgreSQL and secrets

- [ ] Decide whether to use a new managed PostgreSQL instance or retain an existing one. Cloud SQL is a straightforward default to evaluate; the inherited configuration mentions AlloyDB, so compare its cost/access and migrate only deliberately.
- [ ] Confirm the ORM models and actual schema agree. Add versioned migrations (for example, Alembic) before relying on production schema changes; do not use `create_all` as the production migration process.
- [ ] Test a clean database creation and migration in staging. If preserving old data, rehearse an import/upgrade against a copy and verify row counts and key user records.
- [ ] Configure Cloud Run database connectivity and a restricted database user. Keep database networking private where practical.
- [ ] Put database credentials and `OPENAI_API_KEY` in Secret Manager and grant access only to the backend service identity. Use environment-variable names in configuration, never secret values in source control.
- [ ] Verify database backups and perform a restore test before production data is placed there.

**Checkpoint:** Staging can connect to the database, apply migrations, and recover from a tested backup without exposing credentials.

## Phase 4 — Move authentication safely

- [ ] Enable Firebase Authentication providers you intend to support and configure authorized domains, email verification, and password-reset behavior.
- [x] Integrate frontend Firebase Email/Password Auth, send verification on signup, block unverified frontend sign-in, and provide resend. The old database-login fallback is removed from the frontend because there are test accounts only; recreate any needed test accounts in Firebase. See [FIREBASE_SPARK_SETUP.md](FIREBASE_SPARK_SETUP.md).
- [x] Firebase is the sole identity provider used by the frontend auth service. The old database registration/login endpoints have been removed from FastAPI; recreate any needed test accounts in Firebase.
- [x] FastAPI verifies Firebase ID tokens and the verified-email claim for question, scoring, profile, and upload APIs. Upload APIs require a trusted Firebase `admin` custom claim; with no claim-provisioning process, uploads deny everyone by default.
- [ ] Configure local Application Default Credentials and `FIREBASE_PROJECT_ID`, then test real Firebase tokens end to end. Unit tests use mocked tokens and do not validate Google project credentials.
- [ ] Add/verify a safe Firebase UID-to-application-profile mapping. Current profile endpoints return not-found until an app database user exists for the verified Firebase email.
- [ ] Build and audit an administrator custom-claim provisioning process using trusted server-side tooling. Registration must never accept an admin role from the browser. Continue requiring backend role checks for every admin endpoint, including question imports.
- [ ] Decide how existing users will sign in. The current custom password hashes generally cannot be copied directly into Firebase Auth. Plan a tested password-reset/account-recovery and data-linking path if real users exist.
- [ ] Test signup, email verification, login, logout, password reset, expired/invalid token, anonymous API denial, learner denial of admin actions, and account recovery.

**Checkpoint:** An unauthenticated request cannot perform a protected operation, and a learner cannot gain admin access by editing browser data or request fields.

## Phase 5 — Configure private media storage

- [ ] Create a private Cloud Storage bucket in the chosen region. Do not make learner recordings or private content publicly readable.
- [ ] Decide whether recordings are stored at all, why, and for how long. Document consent, deletion, and retention before launch.
- [ ] Validate file size, allowed media types, ownership, and duration on the backend. Add short-lived signed upload/download URLs if appropriate.
- [ ] Test unauthorized access, oversize/wrong-type uploads, deletion, and lifecycle cleanup. Keep media bytes out of database rows; store object identifiers and relevant metadata.

**Checkpoint:** Only the intended owner/backend can access a private test file, and its deletion/retention behavior is verified.

## Phase 6 — Deploy a staging backend and frontend

- [ ] Deploy FastAPI to Cloud Run in the chosen project/region with production-style settings, health endpoint, request timeout, and conservative scaling limits.
- [ ] Configure CORS to allow only the actual staging website origin(s), not every origin.
- [ ] Deploy the React production build to Firebase Hosting with single-page-app routing fallback. Confirm the Hosting build output directory before initialization (Create React App commonly outputs `frontend/build`).
- [ ] Set the frontend API base URL to the staging Cloud Run service URL. Do not put OpenAI, database, or service-account secrets in frontend environment variables.
- [ ] Confirm TLS works, health/readiness checks pass, logs contain no secrets or personal content, and the staging frontend can reach the API.
- [ ] Exercise a real staging user through register/login → fetch question → submit response → score → persist result → reload history. Use test accounts and controlled AI usage.

**Checkpoint:** The staging app works end to end, with no local URLs, old project references, mock results presented as real, or unauthorized admin endpoints.

## Phase 7 — Launch readiness and production cutover

- [ ] Resolve remaining P0 security and P1 end-to-end gaps from the production plan, especially protected APIs, admin authorization, persistent progress, uploads, and profile API mismatches.
- [ ] Run automated frontend/backend tests, dependency and secret scans, browser checks, and a modest load test. Do not use live OpenAI calls in normal CI.
- [ ] Add error monitoring, uptime checks, log redaction, backup alerts, database/storage monitoring, OpenAI quotas, and usage/cost alerts. Define who responds to alerts.
- [ ] Review privacy policy, terms, consent for AI processing, retention/deletion, target user ages, and required support contact before opening to users.
- [ ] Write a rollback plan and take a final backup. Deploy a tagged/reversible release and test the rollback in staging first.
- [ ] Cut over domain/DNS only after staging sign-off. Monitor errors and spending closely after launch.

**Do not describe the app as production-ready until these checks have passed and the product owner accepts the remaining risks.**

## Phase 8 — Payments (only after the product/business decisions)

Payments are not required to make the free product live. Before implementing them, decide merchant country, currencies, plans/pricing, taxes/refunds, and which features are gated.

- [ ] Select a provider that supports the business's merchant country and payout requirements.
- [ ] Use hosted checkout; never store card details.
- [ ] Create checkout sessions server-side. Grant or remove access only after a signed, verified, idempotently processed webhook—not from a browser success page.
- [ ] Test success, failure, repeated/out-of-order webhook, cancellation, refund, and entitlement expiry in sandbox mode.

## Launch notes / decisions to fill in

- New Google Cloud/Firebase project ID: `clear-pte-67fdc` (Firebase project confirmed; verify matching Cloud project and access).
- Production region and reason: India; Mumbai (`asia-south1`) recommended, pending availability/pricing check.
- Existing real users? No; test users only (confirmed). Other test data to preserve? ___________________
- PostgreSQL choice and backup owner: ________________________________
- Authentication migration/recovery plan: ____________________________
- Audio retention and deletion policy: _______________________________
- Staging site/API URLs: _____________________________________________
- Production site/API URLs: __________________________________________
- Rollback owner and procedure: _____________________________________

## What to do first

The owner confirmed there are no real users, only test users, so production account migration is not currently required. Still determine whether test question content or uploads should be retained. Don’t create databases or run the existing Cloud Build deployment until the old project references are reviewed. Then work through one phase at a time and stop at each checkpoint if a test fails.
