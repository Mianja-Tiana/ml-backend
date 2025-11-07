# import os
# from sqlalchemy import create_engine, text
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# DB_USER = os.getenv("DB_USER", "user_placeholder")
# DB_PASS = os.getenv("DB_PASS", "pass_placeholder")
# DB_HOST = os.getenv("DB_HOST", "localhost")
# DB_PORT = os.getenv("DB_PORT", "5432")
# DB_NAME = os.getenv("DB_NAME", "db_placeholder")

# # Get the database server URL from environment variable

# DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# engine = create_engine(DATABASE_URL, echo=True)

# # Database name you want to create
# new_db_name = "telecom_churn"

# # Execute CREATE DATABASE

# # Use autocommit to run CREATE DATABASE
# with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
#     conn.execute(text(f"CREATE DATABASE {new_db_name}"))


# print(f"Database {new_db_name} created successfully!")



# inside container path /app/init_db.py
import os
from sqlalchemy import create_engine, text
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
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

DEFAULT_DB_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/postgres"
)

def create_database_if_not_exists(new_db_name: str):
    engine = create_engine(DEFAULT_DB_URL, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        exists = conn.execute(text("""
            SELECT 1 FROM pg_database WHERE datname=:dbname
        """), {"dbname": new_db_name}).scalar()
        if not exists:
            conn.execute(text(f"CREATE DATABASE {new_db_name}"))
            print(f"Database '{new_db_name}' created successfully!")
        else:
            print(f"Database '{new_db_name}' already exists.")

if __name__ == "__main__":
    create_database_if_not_exists("churn_db")
