from fastapi import APIRouter, Depends, HTTPException, Request, status
import pandas as pd
from sqlmodel import Session, select
from schemas.churn_input import ChurnInput
from models.model import User, Prediction, PredictionLog, MLModel, PredictionMetadata
from controllers.middleware.auth import get_current_user, get_session
#from utils.ml_utils import model, train_columns, latest_version
from ml.pipeline import preprocess_input
from schemas.schema import PredictionRead
from typing import List
from loaders.model_loader import ModelArtifacts

router = APIRouter(prefix="/predict", tags=["Prediction"])


### Optimized prediction endpoint

@router.post("/", summary="Predict Customer Churn", response_model=dict)
def predict_churn(
    data: ChurnInput,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    print(f"Prediction request made by user: {current_user.username}")

    df = pd.DataFrame([data.model_dump()])

    # Only use the stored transforms and model
    X = ModelArtifacts.fe.transform(df)
    y_pred = ModelArtifacts.model.predict(X)[0]
    prob = float(ModelArtifacts.model.predict_proba(X)[0, 1])

    # store prediction + metadata + log exactly same as before
    prediction_record = Prediction(
        user_id=current_user.id,
        input_data=df.to_json(),
        prediction=int(y_pred),
        probability=prob
    )
    session.add(prediction_record)
    session.commit()
    session.refresh(prediction_record)

    # Attach model version / metadata link same way like before
    model_record = session.exec(
        select(MLModel).where(
            MLModel.name == ModelArtifacts.model_name,
            MLModel.version == ModelArtifacts.version
        )
    ).first()

    metadata_record = PredictionMetadata(
        prediction_id=prediction_record.id,
        model_id=model_record.id
    )
    session.add(metadata_record)
    session.commit()

    log_record = PredictionLog(
        prediction_id=prediction_record.id,
        user_id=current_user.id,
        request_ip=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    session.add(log_record)
    session.commit()

    return {
        "user": current_user.username,
        "prediction": int(y_pred),
        "probability": prob,
        "prediction_id": prediction_record.id,
        "model_version": ModelArtifacts.version
    }



# Endpoint to list all predictions

@router.get("/predictions/", response_model=List[PredictionRead])
def list_predictions(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    List all predictions in the database.
    
    Authentication is required, but predictions are not user-specific.
    """
    predictions = session.exec(select(Prediction)).all()
    return predictions



# Endpoint: Get a single prediction

@router.get("/predictions/{prediction_id}", response_model=PredictionRead)
def get_prediction(
    prediction_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)  # endpoint still protected
):
    """
    Retrieve a single prediction by its ID.
    
    Authentication is required, but predictions are not user-specific.
    """
    prediction = session.get(Prediction, prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return prediction



@router.delete("/predictions/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prediction(
    prediction_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)  # endpoint still protected
):
    """
    Delete a prediction by its ID.
    
    Authentication is required, but predictions are not user-specific.
    """
    prediction = session.get(Prediction, prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    session.delete(prediction)
    session.commit()