# app/api/__init__.py

from fastapi import APIRouter, Depends
from app.api import healthcheck, openai_routes, auth_routes, evaluation_routes, uploadquestions, questions, users, practice_routes
from app.core.auth import get_current_user, require_admin

api_router = APIRouter()

api_router.include_router(healthcheck.router, prefix="/health", tags=["Healthcheck"])
api_router.include_router(
	openai_routes.router,
	prefix="/compare",
	tags=["Audio Comparison"],
	dependencies=[Depends(get_current_user)],
)
api_router.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
api_router.include_router(
	practice_routes.router,
	prefix="/practice",
	tags=["Practice"],
	dependencies=[Depends(get_current_user)],
)
api_router.include_router(
	evaluation_routes.router,
	prefix="/evaluate",
	tags=["Evaluation"],
	dependencies=[Depends(get_current_user)],
)
api_router.include_router(
	uploadquestions.router,
	prefix="/upload",
	tags=["Upload Questions"],
	dependencies=[Depends(require_admin)],
)
api_router.include_router(
	questions.router,
	prefix="/questions",
	tags=["Questions"],
	dependencies=[Depends(get_current_user)],
)
api_router.include_router(
	users.router,
	prefix="/users",
	tags=["Users"],
	dependencies=[Depends(get_current_user)],
)

