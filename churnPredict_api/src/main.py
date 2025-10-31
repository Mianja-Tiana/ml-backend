from fastapi import FastAPI
import mlflow
import pandas as pd
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
# from sqlmodel import Session, select
from db.database import create_db_and_tables
from utils.create_admin_user import create_default_admin

from controllers.routes import auth, prediction, user, admin

# --------------------------
# Load MLflow model from Registry
# --------------------------
# load_dotenv()

# # Absolute path to your mlruns folder
# BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# MLFLOW_TRACKING_URI = f"file://{os.path.join(BASE_DIR, 'mlruns')}"

# mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# MODEL_NAME = os.getenv("MODEL_NAME", "Churn_RandomForest")
# MODEL_VERSION = os.getenv("MODEL_VERSION", "1")  # specify a version explicitly

# # Construct the MLflow model URI
# model_uri = f"models:/{MODEL_NAME}/{MODEL_VERSION}"

# # Load the model using the sklearn flavor
# model = mlflow.sklearn.load_model(model_uri)


# # client = MlflowClient()

# # # Get all versions of the model
# # all_versions = client.get_latest_versions(MODEL_NAME)

# # # Get the latest version
# # latest_version_info = max(all_versions, key=lambda v: int(v.version))
# # run_id = latest_version_info.run_id

# # # Optionally, print vers1:5000 (Press CTRL+C to quit)ion and stage
# # print(f"Latest version: {latest_version_info.version}, stage: {latest_version_info.current_stage}")


# # Get experiment name from environment or use default
# PREPROCESS_EXPERIMENT_NAME = os.getenv("EXPERIMENT_NAME", "telecom_churn_preprocessing")

# # Initialize MLflow client
# client = MlflowClient()

# # Get the experiment by name
# experiment = client.get_experiment_by_name(PREPROCESS_EXPERIMENT_NAME)

# if experiment is None:
#     raise ValueError(f"Experiment '{PREPROCESS_EXPERIMENT_NAME}' not found!")

# # Search for the latest run in that experiment
# runs = mlflow.search_runs(
#     experiment_ids=[experiment.experiment_id],
#     order_by=["start_time DESC"],
#     max_results=1
# )

# if runs.empty:
#     raise ValueError(f"No runs found in experiment '{PREPROCESS_EXPERIMENT_NAME}'.")

# # Extract the latest run ID dynamically
# latest_run_id = runs.loc[0, "run_id"]
# print(f"Latest run ID: {latest_run_id}")

# # Optional: Get model version info if a model was logged in this run
# model_versions = client.search_model_versions(f"run_id='{latest_run_id}'")

# # if model_versions:
# #     latest_version_info = max(model_versions, key=lambda v: int(v.version))
# #     run_id = latest_version_info.run_id
# #     print(f"Latest model version: {latest_version_info.version}, stage: {latest_version_info.current_stage}")
# # else:
# #     print(" No model version found for this run.")


# # Load the artifact file into a DataFrame
# columns_path = "X_final_columns.csv"
# artifact_uri = mlflow.artifacts.download_artifacts(run_id=latest_run_id, artifact_path=columns_path)
# train_columns = pd.read_csv(artifact_uri)["columns"].tolist()

# print("Loaded training columns from MLflow:", train_columns)


# @app.on_event("startup")
# def on_startup():
#     # ensure tables exist
#     create_db_and_tables()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup code
#     create_db_and_tables_2()
#     yield



@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup code ---
    create_db_and_tables()  # ensure tables exist
    try:
        create_default_admin()  # ensure admin user exists
    except Exception as e:
        print("Failed to create default admin on startup:", e)

    yield  # app runs here





# @app.post("/predict")
# def predict_churn(data: ChurnInput):
#     # Convert input to DataFrame
#     input_df = pd.DataFrame([data.model_dump()])


#     # ----------------------------------------------------------
#     # Feature Engineering
#     # ----------------------------------------------------------
#     input_df['TotalCalls'] = input_df['InboundCalls'] + input_df['OutboundCalls']
#     input_df.drop(columns=['InboundCalls', 'OutboundCalls'], inplace=True)

#     # ----------------------------------------------------------
#     # Handle Missing Values
#     # ----------------------------------------------------------
#     num_features = input_df.select_dtypes(include=['int64', 'float64']).columns
#     cat_features = input_df.select_dtypes(include=['object', 'category']).columns

#     num_imputer = SimpleImputer(strategy='median')
#     cat_imputer = SimpleImputer(strategy='most_frequent')

#     input_df[num_features] = num_imputer.fit_transform(input_df[num_features])
#     input_df[cat_features] = cat_imputer.fit_transform(input_df[cat_features])

#     # ----------------------------------------------------------
#     # Encode Binary Features
#     # ----------------------------------------------------------
#     binary_features = ['RespondsToMailOffers', 'MadeCallToRetentionTeam']
#     binary_mapping = {'Yes': 1, 'No': 0}

#     for col in binary_features:
#         if col in input_df.columns:
#             input_df[col] = input_df[col].map(binary_mapping).astype(int)

#     # ----------------------------------------------------------
#     # One-hot Encode Low-cardinality Categorical Features
#     # ----------------------------------------------------------
#     low_card_features = ['CreditRating', 'IncomeGroup', 'Occupation', 'PrizmCode']
#     df_onehot = pd.get_dummies(input_df[low_card_features], drop_first=True)
#     input_df.drop(columns=low_card_features, inplace=True)
#     input_df = pd.concat([input_df, df_onehot], axis=1)


#     input_df = input_df.reindex(columns=train_columns, fill_value=0)

#     # ----------------------------------------------------------
#     # Normalize Numeric Features
#     # ----------------------------------------------------------
#     scaler = StandardScaler()
#     num_cols = input_df.select_dtypes(include=['float64', 'int64']).columns
#     input_df[num_cols] = scaler.fit_transform(input_df[num_cols])

#     # ----------------------------------------------------------
#     # Make Prediction
#     # ----------------------------------------------------------
#     prediction = model.predict(input_df)
#     probability = model.predict_proba(input_df)[0, 1]

#     return {
#         "churn_prediction": int(prediction[0]),
#         "churn_probability": float(probability)
#     }


app = FastAPI(title="Churn Prediction API", lifespan=lifespan)

# Register routers
app.include_router(auth.router)
app.include_router(prediction.router)
app.include_router(admin.router)
app.include_router(user.router)
