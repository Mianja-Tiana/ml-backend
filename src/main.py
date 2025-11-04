import structlog
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.db.database import engine,Base
from src.controllers.routes.users import router as users_router
from src.utils.logging import configure_logging
from src.controllers.middleware.middleware import RequestIDMiddleware
from fastapi.middleware.cors import CORSMiddleware  

configure_logging(log_level="INFO", json_logs=True)

log = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        raise

    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)


app.include_router(users_router, prefix="/api", tags=["users"])

@app.get("/")
def root():
    log.info("root_endpoint_called", method="GET", path="/")
    return {"message": "ML Backend API"}
