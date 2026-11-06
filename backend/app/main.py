# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.core import firebase

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://clearpte.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # allowed origins
    allow_credentials=True,       # allow cookies/auth headers
    allow_methods=["*"],          # allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],          # allow all headers
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to the API"}
