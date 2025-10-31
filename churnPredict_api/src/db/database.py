# app/db.py
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
import os
from dotenv import load_dotenv

# Get absolute path to the root project directory
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
dotenv_path = os.path.join(base_dir, ".env")

# Load the .env file from the root
load_dotenv(dotenv_path)

# Environment variables for the second database
DB2_USER = os.getenv("DB2_USER")
DB2_PASS = os.getenv("DB2_PASS")
DB2_HOST = os.getenv("DB2_HOST")
DB2_PORT = os.getenv("DB2_PORT", "5432")
DB2_NAME = os.getenv("DB2_NAME")

# Get the database server URL from environment variable

DATABASE_URL = f"postgresql+psycopg2://{DB2_USER}:{DB2_PASS}@{DB2_HOST}:{DB2_PORT}/{DB2_NAME}"

# echo=True prints SQL for debugging. Turn off in prod.
app_engine = create_engine(DATABASE_URL, echo=True)

# def create_db_and_tables_2():
#     from model import SQLModel  # avoid circular import, but we'll import metadata differently
#     # Better: call SQLModel.metadata.create_all(engine) from main after importing models
#     from sqlmodel import SQLModel
#     SQLModel.metadata.create_all(app_engine)


def create_db_and_tables() -> None:
    """
    Create database tables for all imported models.
    Safe to call multiple times; existing tables are not overwritten.
    """
    # Import all models here to ensure metadata is populated
    from models.model import User, Prediction, PredictionLog, Feedback, MLModel, PredictionMetadata  # noqa: F401

    print("Creating database tables if they don't exist...")
    SQLModel.metadata.create_all(app_engine)
    print("Database tables are ready.")

def get_session() -> Generator[Session, None, None]:
    with Session(app_engine) as session:
        yield session
