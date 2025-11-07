import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
from dotenv import load_dotenv

load_dotenv()

import os
from pathlib import Path

def read_secret(path: str) -> str | None:
    p = Path(path)
    if p.exists():
        return p.read_text().strip()
    return None

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

# secrets (password only stored as docker secret)
POSTGRES_PASSWORD =os.getenv("POSTGRES_PASSWORD")

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


# try:     
#         with SessionLocal() as db:
#             db.execute(text("SELECT 1")).scalar()
# except Exception as exc:
       
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail="Database is unavailable"
#         ) from exc


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def create_db_and_tables() -> None:
    """
    Create database tables for all imported models.
    Safe to call multiple times; existing tables are not overwritten.
    """
    # Import all models here to ensure metadata is populated
    from models.model import User, Prediction, PredictionLog, Feedback, MLModel, PredictionMetadata  # noqa: F401

    print("Creating database tables if they don't exist...")
    SQLModel.metadata.create_all(engine)
    print("Database tables are ready.")



def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
