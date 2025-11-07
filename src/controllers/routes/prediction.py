from fastapi import APIRouter, Depends, HTTPException, Request, status
<<<<<<< HEAD
=======
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
>>>>>>> main
import pandas as pd
from sqlmodel import Session, select
from schemas.churn_input import ChurnInput
from models.model import User, Prediction, PredictionLog, MLModel, PredictionMetadata
<<<<<<< HEAD
from controllers.middleware.auth import get_current_user, get_session
#from utils.ml_utils import model, train_columns, latest_version
from ml.pipeline import preprocess_input
from schemas.schema import PredictionRead
from typing import List
from loaders.model_loader import ModelArtifacts

router = APIRouter(prefix="/predict", tags=["Prediction"])


### Optimized prediction endpoint

=======
from auth.security import get_current_user, get_session
# from app.database import get_session
from utils.ml_utils import model, train_columns, latest_version
from schemas.schema import PredictionRead
from typing import List

router = APIRouter(prefix="/predict", tags=["Prediction"])

>>>>>>> main
@router.post("/", summary="Predict Customer Churn", response_model=dict)
def predict_churn(
    data: ChurnInput,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
<<<<<<< HEAD
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
=======
    """
    Protected churn prediction endpoint.
    Only accessible with a valid JWT token.
    """

    # Log who is making the request (optional)
    print(f"Prediction request made by user: {current_user.username}")

    # Convert input to DataFrame
    input_df = pd.DataFrame([data.model_dump()])

    # ----------------------------------------------------------
    # Feature Engineering
    # ----------------------------------------------------------
    input_df['TotalCalls'] = input_df['InboundCalls'] + input_df['OutboundCalls']
    input_df.drop(columns=['InboundCalls', 'OutboundCalls'], inplace=True)

    # ----------------------------------------------------------
    # Handle Missing Values
    # ----------------------------------------------------------
    num_features = input_df.select_dtypes(include=['int64', 'float64']).columns
    cat_features = input_df.select_dtypes(include=['object', 'category']).columns

    num_imputer = SimpleImputer(strategy='median')
    cat_imputer = SimpleImputer(strategy='most_frequent')

    input_df[num_features] = num_imputer.fit_transform(input_df[num_features])
    input_df[cat_features] = cat_imputer.fit_transform(input_df[cat_features])

    # ----------------------------------------------------------
    # Encode Binary Features
    # ----------------------------------------------------------
    binary_features = ['RespondsToMailOffers', 'MadeCallToRetentionTeam']
    binary_mapping = {'Yes': 1, 'No': 0}

    for col in binary_features:
        if col in input_df.columns:
            input_df[col] = input_df[col].map(binary_mapping).astype(int)

    # ----------------------------------------------------------
    # One-hot Encode Low-cardinality Categorical Features
    # ----------------------------------------------------------
    low_card_features = ['CreditRating', 'IncomeGroup', 'Occupation', 'PrizmCode']
    df_onehot = pd.get_dummies(input_df[low_card_features], drop_first=True)
    input_df.drop(columns=low_card_features, inplace=True)
    input_df = pd.concat([input_df, df_onehot], axis=1)

    # Reindex columns to match training features
    input_df = input_df.reindex(columns=train_columns, fill_value=0)

    # ----------------------------------------------------------
    # Normalize Numeric Features
    # ----------------------------------------------------------
    scaler = StandardScaler()
    num_cols = input_df.select_dtypes(include=['float64', 'int64']).columns
    input_df[num_cols] = scaler.fit_transform(input_df[num_cols])

    # ----------------------------------------------------------
    # Make Prediction
    # ----------------------------------------------------------
    prediction = model.predict(input_df)
    prediction_val = model.predict(input_df)[0]
    # probability = model.predict_proba(input_df)[0, 1]
    probability_val = float(model.predict_proba(input_df)[0, 1])

    model_version=latest_version

    # -----------------------------
    # Save Prediction in DB
    # -----------------------------
    prediction_record = Prediction(
        user_id=current_user.id,
        input_data=input_df.to_json(),
        prediction=int(prediction_val),
        probability=probability_val
>>>>>>> main
    )
    session.add(prediction_record)
    session.commit()
    session.refresh(prediction_record)

<<<<<<< HEAD
    # Attach model version / metadata link same way like before
    model_record = session.exec(
        select(MLModel).where(
            MLModel.name == ModelArtifacts.model_name,
            MLModel.version == ModelArtifacts.version
        )
    ).first()

=======
    # -----------------------------
# Save PredictionMetadata
# -----------------------------
# Retrieve the MLModel record used
    model_record = session.exec(
        select(MLModel).where(MLModel.name == "Churn_RandomForest", MLModel.version == latest_version)
    ).first()

    if not model_record:
        raise HTTPException(status_code=500, detail="ML model record not found in DB")

    # Create PredictionMetadata
>>>>>>> main
    metadata_record = PredictionMetadata(
        prediction_id=prediction_record.id,
        model_id=model_record.id
    )
<<<<<<< HEAD
    session.add(metadata_record)
    session.commit()

=======

    session.add(metadata_record)
    session.commit()
    session.refresh(metadata_record)


    # -----------------------------
    # Save Prediction Log
    # -----------------------------
>>>>>>> main
    log_record = PredictionLog(
        prediction_id=prediction_record.id,
        user_id=current_user.id,
        request_ip=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    session.add(log_record)
    session.commit()

<<<<<<< HEAD
    return {
        "user": current_user.username,
        "prediction": int(y_pred),
        "probability": prob,
        "prediction_id": prediction_record.id,
        "model_version": ModelArtifacts.version
    }



# Endpoint to list all predictions

=======
    # -----------------------------
    # Return Response
    # -----------------------------
    return {
        "user": current_user.username,
        "churn_prediction": int(prediction_val),
        "churn_probability": probability_val,
        "prediction_id": prediction_record.id,
        "model_version": model_version
    }

    # return {
    #     "user": current_user.username,
    #     "churn_prediction": int(prediction[0]),
    #     "churn_probability": float(probability)
    # }



# -----------------------------
# Endpoint to list all predictions
# -----------------------------
>>>>>>> main
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


<<<<<<< HEAD

# Endpoint: Get a single prediction

=======
# -----------------------------
# Endpoint: Get a single prediction
# -----------------------------
>>>>>>> main
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