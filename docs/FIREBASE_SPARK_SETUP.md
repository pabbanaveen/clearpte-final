# Firebase Spark setup (frontend authentication and optional Hosting)

This setup uses Firebase Authentication Email/Password and optionally Firebase Hosting. It does not configure billing, Cloud Run, SQL, or Storage. Backend Firebase ID-token verification is now implemented in the code, but still needs local credentials/configuration and a live-token end-to-end test before deployment.

## Firebase Console steps

1. Open the Firebase project you intend to use, or create a Firebase project without linking a billing account.
2. In **Project settings → General → Your apps**, register a **Web app**. The app nickname is only a label; do not enable Hosting from the setup wizard unless you want to configure it there.
3. Copy the web app configuration fields into a local file at `frontend/.env.local`, using [frontend/.env.firebase.example](../frontend/.env.firebase.example) as the key-name template:
   - `REACT_APP_FIREBASE_API_KEY`
   - `REACT_APP_FIREBASE_AUTH_DOMAIN`
   - `REACT_APP_FIREBASE_PROJECT_ID`
   - `REACT_APP_FIREBASE_STORAGE_BUCKET`
   - `REACT_APP_FIREBASE_MESSAGING_SENDER_ID`
   - `REACT_APP_FIREBASE_APP_ID`
4. In **Authentication → Sign-in method**, enable **Email/Password**. Do not enable billing. Add `localhost` and the eventual site hostname under **Authentication → Settings → Authorized domains** as applicable.
5. Restart the frontend development server after creating or changing `.env.local`; Create React App reads these settings when it starts/builds.

These Firebase web-app values are client configuration and will be included in the browser bundle. They are not server credentials. Never put service-account keys, database URLs/passwords, OpenAI keys, or other server secrets in this file. Keep `.env.local` untracked; it is ignored by the frontend Git rules.

## What the current frontend does

- Registration and sign-in use Firebase Email/Password when Firebase web configuration is present.
- Registration sends a Firebase verification email and does not create an app session until the user verifies the address. Login and session restoration reject unverified Firebase accounts; the dialog offers a resend action.
- The frontend no longer falls back to the old database-backed login. Existing test accounts in that system must be recreated in Firebase Auth or the old flow must be deliberately migrated before reuse.
- Logout and session restoration use Firebase Auth. The existing UI is retained, and provider errors are shown in the dialog.
- Firebase ID tokens are attached to API requests. FastAPI now verifies Firebase ID tokens, checks revocation and verified email, protects question/scoring/profile APIs, and requires a trusted Firebase `admin` custom claim for question uploads. Never treat frontend route guards or local role state as backend authorization.
- Old database-backed `/api/auth/register` and `/api/auth/login` endpoints have been removed from the backend. Recreate needed test accounts in Firebase Auth. The authenticated `/api/auth/me` endpoint now idempotently creates a `firebase_identities` row keyed by verified Firebase UID. Self-profile uses `GET/PUT /api/users/profile`, and does not accept a caller-selected user ID.
- Alembic revisions now create the Firebase identity/profile table and active question catalog tables. Legacy first-party password tables are not part of a fresh Firebase-first schema. All revisions upgrade/downgrade on disposable SQLite, and Alembic reports no ORM drift there. This is not a PostgreSQL test; validate with a new staging PostgreSQL database before deployment. `backend/app/database/tables.sql` is a legacy draft, not the authoritative schema.
- The backend rejects missing `DATABASE_URL` and SQLite when `APP_ENV` is staging/production (and detects Cloud Run/App Engine runtime markers). Local development can still use the SQLite fallback; runtime `create_all` is disabled for staging/production. Run Alembic migrations explicitly before starting a deployed backend.
- No admin custom-claim provisioning workflow exists yet. Therefore question upload endpoints intentionally deny access to ordinary users and all accounts until an authorized project owner provisions the claim through trusted server-side tooling.
- The frontend never assigns admin roles. Existing legacy admin state is intentionally not trusted by the UI.

## Optional Firebase Hosting scaffold

The repository-level [firebase.json](../firebase.json) serves the Create React App build from `frontend/build` and routes SPA paths to `index.html`. It contains no project selection and performs no deployment. Before any future deploy, build with the intended public Firebase configuration, sign in with the Firebase CLI, select the correct project locally, review the generated bundle and hosting target, and confirm the project remains on Spark. Never run a deploy as part of this setup without explicit approval.

## Local backend token verification

1. Set `FIREBASE_PROJECT_ID` in the backend's untracked local environment file to the Firebase project ID. The project ID is configuration, not a credential.
2. The backend uses Firebase Admin SDK Application Default Credentials. For local development, sign in with the Google Cloud CLI's Application Default Credentials using an account that has the minimum Firebase Authentication permissions needed for token and revocation checks. Never create or commit a service-account JSON key.
3. On Cloud Run, use its attached service identity and grant only the needed Firebase Authentication verification permissions. Do not put credentials in the React environment or pass them through chat.
4. Test no-token, malformed/expired token, unverified user, verified learner, and admin-claim behavior before allowing real traffic. Unit/API tests mock token verification and do not prove that the configured cloud project and live tokens work together.
