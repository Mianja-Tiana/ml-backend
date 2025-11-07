from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from schemas.schema import UserRead, FeedbackRead, FeedbackCreate, User, UserOut
from schemas.schema import MLModelRead, MLModelCreate
from db.database import get_session
from controllers.middleware.auth import get_current_user
from models.model import Feedback, MLModel, PredictionLog, UserRole
import mlflow
import os

router = APIRouter(prefix="/api", tags=["Telecom Churn"])

# USERS

@router.get("/users/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    """Get the current authenticated user's profile"""
    return current_user

# Admin-only users listing

@router.get("/users/", response_model=List[UserOut])
def list_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    List all users — Admin access only
    """
    # Check if the current user has an admin role
    roles = [ur.role.name for ur in current_user.roles]
    if "admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Fetch all users
    users = session.exec(select(User)).all()
    return users


# FEEDBACK

@router.post("/feedback/", response_model=FeedbackRead)
def create_feedback(
    feedback_in: FeedbackCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback for a prediction. 
    Only the authenticated user can submit feedback.
    """
    # Create SQLModel Feedback instance
    feedback = Feedback(
        prediction_id=feedback_in.prediction_id,
        correct=feedback_in.correct,
        comment=feedback_in.comment,
        user_id=current_user.id  # enforce user ownership
    )

    # Add and commit to DB
    session.add(feedback)
    session.commit()
    session.refresh(feedback)

    return feedback


# Admin-only endpoint

@router.get("/feedback/", response_model=List[FeedbackRead])
def list_feedback(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    List all feedback submitted by any user.
    Only admin users can access this endpoint.
    """
    # Check if the current user has admin role
    roles = [ur.role.name for ur in current_user.roles]  # ur = UserRole instance
    if "admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Fetch all feedback entries
    feedbacks = session.exec(select(Feedback)).all()
    return feedbacks


# Admin-only endpoint

@router.get("/models/", response_model=List[MLModelRead])
def list_models(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    List all ML models.
    Only admin users can access this endpoint.
    """
    # Check if the current user has admin role
    roles = [ur.role.name for ur in current_user.roles]  # ur = UserRole instance
    if "admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Fetch all ML models
    models = session.exec(select(MLModel)).all()
    return models



# Model creation with MLflow load (no admin check)

@router.post("/models/", response_model=MLModelRead)
def create_model(
    model_in: MLModelCreate,
    session: Session = Depends(get_session)
):
    """
    Register a new ML model in the database.
    Automatically loads the latest version from MLflow using the sklearn flavor (Endpoint to be modified)
    """

    # MLflow setup
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    MLFLOW_TRACKING_URI = f"file://{os.path.join(BASE_DIR, 'mlruns')}"
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    # Get latest model version
    try:
        latest_version_info = mlflow.client.MlflowClient().get_latest_versions(
            model_in.name, stages=["None", "Production", "Staging"]
        )
        if not latest_version_info:
            raise HTTPException(
                status_code=400,
                detail=f"No MLflow model found for name: {model_in.name}"
            )
        latest_version = max(int(v.version) for v in latest_version_info)
        model_uri = f"models:/{model_in.name}/{latest_version}"
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error retrieving MLflow model: {str(e)}"
        )

    #  Load MLflow model (sklearn flavor)
    try:
        model = mlflow.sklearn.load_model(model_uri)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to load MLflow model: {str(e)}"
        )

    #  Save model metadata in DB
    db_model = MLModel(
        name=model_in.name,
        version=str(latest_version),
        description=model_in.description
    )
    session.add(db_model)
    session.commit()
    session.refresh(db_model)

    return db_model


@router.get("/logs/", response_model=List[PredictionLog])
def list_logs(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all prediction logs (for all users). Admin only."""
    
    # Check if current user is admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Admins only"
        )
    logs = session.exec(select(PredictionLog)).all()
    return logs
