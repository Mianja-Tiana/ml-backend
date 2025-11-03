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



import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB2_USER", "user_placeholder")
DB_PASS = os.getenv("DB2_PASS", "pass_placeholder")
DB_HOST = os.getenv("DB2_HOST", "localhost")
DB_PORT = os.getenv("DB2_PORT", "5432")

# Notice we do NOT use DB_NAME here because we connect to default "postgres" to manage DBs
DEFAULT_DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/postgres"

def create_database_if_not_exists(new_db_name: str):
    engine = create_engine(DEFAULT_DB_URL, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        # Check if database exists
        result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = :dbname"), {"dbname": new_db_name})
        exists = result.scalar() is not None
        if exists:
            print(f"Database '{new_db_name}' already exists.")
            return False
        else:
            conn.execute(text(f"CREATE DATABASE {new_db_name}"))
            print(f"Database '{new_db_name}' created successfully!")
            return True
    engine.dispose()

