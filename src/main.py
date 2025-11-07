from fastapi import FastAPI
import mlflow
import pandas as pd
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
# from sqlmodel import Session, select
from db.database import create_db_and_tables
from controllers.routes import feedback
from utils.create_admin_user import create_default_admin
from loaders.model_loader import ModelArtifacts

from controllers.routes import prediction, admin, health_check, users
# from init_db import create_database_if_not_exists

import structlog
from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.database import engine,Base
from controllers.routes.users import router as users_router
from utils.logging import configure_logging
from controllers.middleware.middleware import RequestIDMiddleware
from fastapi.middleware.cors import CORSMiddleware  


# @app.on_event("startup")
# def on_startup():
#     # ensure tables exist
#     create_db_and_tables()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup code
#     create_db_and_tables_2()
#     yield


configure_logging(log_level="INFO", json_logs=True)

log = structlog.get_logger()



@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Block ---
    # 1) Create DB tables
    create_db_and_tables()

    # 2) Create default admin
    try:
        create_default_admin()
    except Exception as e:
        print("Failed to create default admin:", e)

    # 3) Load model + feature engineering artifacts ONCE
    try:
        ModelArtifacts.load()
        print("ML artifacts loaded successfully")
    except Exception as e:
        print("Failed loading ML artifacts:", e)

    yield



# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     create_database_if_not_exists("telecom_churn")
#     create_db_and_tables()
#     try:
#         await create_default_admin()
#     except Exception as e:
#         print("Failed to create default admin on startup:", e)

#     yield


app = FastAPI(title="Churn Prediction API", lifespan=lifespan)

# Register routers
app.include_router(health_check.router)
app.include_router(users.router)
app.include_router(prediction.router)
app.include_router(admin.router)
app.include_router(feedback.router)
app.add_middleware(RequestIDMiddleware)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     try:
#         Base.metadata.create_all(bind=engine)
#     except Exception as e:
#         raise

#     yield

# app = FastAPI(lifespan=lifespan)


# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],  
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )


# app.add_middleware(RequestIDMiddleware)


# app.include_router(users_router, prefix="/api", tags=["users"])

@app.get("/")
def root():
    log.info("root_endpoint_called", method="GET", path="/")
    return {"message": "ML Backend API"}
