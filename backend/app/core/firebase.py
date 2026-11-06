"""Firebase Admin initialization for verifying Firebase Authentication tokens.

Cloud Run should use its attached service identity. For local development, use
Google Application Default Credentials. Never commit service-account keys.
"""

import os

import firebase_admin
from firebase_admin import App


class FirebaseConfigurationError(RuntimeError):
	"""Raised when Firebase Admin cannot be initialized safely."""


def get_firebase_app() -> App:
	"""Return the default Admin SDK app for the explicitly configured project."""
	project_id = os.getenv("FIREBASE_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
	if not project_id:
		raise FirebaseConfigurationError(
			"Set FIREBASE_PROJECT_ID or GOOGLE_CLOUD_PROJECT for Firebase token verification."
		)

	try:
		app = firebase_admin.get_app()
	except ValueError:
		try:
			app = firebase_admin.initialize_app(options={"projectId": project_id})
		except Exception as exc:
			raise FirebaseConfigurationError(
				"Firebase Admin initialization failed; configure Application Default Credentials."
			) from exc

	if app.project_id != project_id:
		raise FirebaseConfigurationError(
			"The initialized Firebase Admin project does not match the configured project."
		)
	return app


def verify_firebase_id_token(id_token: str) -> dict:
	"""Verify signature, audience, issuer, expiration, and revocation status."""
	return firebase_admin.auth.verify_id_token(
		id_token,
		check_revoked=True,
		app=get_firebase_app(),
	)
