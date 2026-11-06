# app/database/deps.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

APP_ENV = os.getenv("APP_ENV")
if not APP_ENV:
    APP_ENV = "production" if os.getenv("K_SERVICE") or os.getenv("GAE_ENV") else "development"
APP_ENV = APP_ENV.strip().lower()


def resolve_database_url(app_env: str, database_url: str | None) -> str:
    """Use SQLite only as a local fallback; require a managed DB in production."""
    environment = app_env.strip().lower()
    normalized_url = database_url.strip() if database_url else None

    if not normalized_url:
        if environment in {"production", "prod", "staging", "stage"}:
            raise RuntimeError("DATABASE_URL must be configured for staging and production.")
        return "sqlite:///./clearpte_local.db"

    if environment in {"production", "prod", "staging", "stage"} and normalized_url.startswith("sqlite"):
        raise RuntimeError("SQLite is not supported as the staging or production database.")
    return normalized_url


DATABASE_URL = resolve_database_url(APP_ENV, os.getenv("DATABASE_URL"))

# Create SQLAlchemy engine
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=2,
    future=True,
    connect_args=connect_args,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables only for local/test SQLite development. Staging/production schema
# must be applied explicitly through Alembic before the service starts.
if DATABASE_URL.startswith("sqlite") and APP_ENV in {"development", "dev", "test", "testing"}:
    from app.database.models import Base

    Base.metadata.create_all(bind=engine)

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# # app/database/deps.py

# import os
# from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from google.cloud.alloydbconnector import Connector, IPTypes

# load_dotenv()

# # Env vars
# USE_CONNECTOR = os.getenv("USE_CONNECTOR", "false").lower() == "true"
# INSTANCE_URI = os.getenv("ALLOYDB_INSTANCE_URI",
#     "projects/clear-pte-ff08c/locations/us-east1/clusters/clearpte/instances/clearpte-primary"
# )
# DB_USER = os.getenv("DB_USER", "postgres")
# DB_PASS = os.getenv("DB_PASSWORD", "")
# DB_NAME = os.getenv("DB_NAME", "postgres")
# DB_HOST = os.getenv("DB_HOST", "35.237.95.55")  # Public IP for local
# DB_PORT = os.getenv("DB_PORT", "5432")

# if USE_CONNECTOR:
#     # Cloud Run / GCP
#     connector = Connector()

#     def getconn():
#         return connector.connect(
#             INSTANCE_URI,
#             "pg8000",
#             user=DB_USER,
#             password=DB_PASS,
#             db=DB_NAME,
#             ip_type=IPTypes.PRIVATE,  # private IP inside VPC
#         )

#     engine = create_engine(
#         "postgresql+pg8000://",
#         creator=getconn,
#         pool_size=5,
#         max_overflow=2,
#         pool_pre_ping=True,
#         future=True,
#     )
# else:
#     # Localhost / public IP
#     DATABASE_URL = os.getenv(
#         "DATABASE_URL",
#         f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
#     )
#     engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()





# # app/database/deps.py

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from os import getenv
# from dotenv import load_dotenv

# load_dotenv()

# Supply DATABASE_URL through the environment when using a remote PostgreSQL database.

# engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
