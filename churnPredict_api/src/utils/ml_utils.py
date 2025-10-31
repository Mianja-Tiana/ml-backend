# from fastapi import FastAPI
import mlflow
import pandas as pd
import os
from dotenv import load_dotenv
from mlflow.tracking import MlflowClient
# from sqlmodel import Session, select


# --------------------------
# Load MLflow model from Registry
# --------------------------
load_dotenv()

# Absolute path to your mlruns folder
# BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# MLFLOW_TRACKING_URI = f"file://{os.path.join(BASE_DIR, 'mlruns')}"

# MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")

# mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# # Absolute path to your desired mlruns folder
# BASE_DIR = "/Users/ammi/Documents/telCustomerChurn"
# MLRUNS_PATH = os.path.join(BASE_DIR, "mlruns")

# # Make sure the directory exists
# os.makedirs(MLRUNS_PATH, exist_ok=True)

# # Set MLflow tracking URI
# MLFLOW_TRACKING_URI = f"{MLRUNS_PATH}"


MLFLOW_TRACKING_URI = "/Users/ammi/Documents/fastapiApp/mlruns"

print(f"{MLFLOW_TRACKING_URI}")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

MODEL_NAME = os.getenv("MODEL_NAME", "Churn_RandomForest")
# MODEL_VERSION = os.getenv("MODEL_VERSION", "1")  # specify a version explicitly

# Get the latest version of the model from MLflow
client = MlflowClient()
latest_version_info = client.get_latest_versions(MODEL_NAME, stages=["None", "Production", "Staging"])

# Sort by version number to get the latest
latest_version = max([int(v.version) for v in latest_version_info])

# Construct the MLflow model URI for the latest version
model_uri = f"models:/{MODEL_NAME}/{latest_version}"

print(f"Using model URI: {model_uri}")

# # Construct the MLflow model URI
# model_uri = f"models:/{MODEL_NAME}/{MODEL_VERSION}"

# # Load the model using the sklearn flavor
model = mlflow.sklearn.load_model(model_uri)


# client = MlflowClient()

# # Get all versions of the model
# all_versions = client.get_latest_versions(MODEL_NAME)

# # Get the latest version
# latest_version_info = max(all_versions, key=lambda v: int(v.version))
# run_id = latest_version_info.run_id

# # Optionally, print vers1:5000 (Press CTRL+C to quit)ion and stage
# print(f"Latest version: {latest_version_info.version}, stage: {latest_version_info.current_stage}")


# Get experiment name from environment or use default
PREPROCESS_EXPERIMENT_NAME = os.getenv("EXPERIMENT_NAME", "telecom_churn_preprocessing")

# Initialize MLflow client
client = MlflowClient()

# Get the experiment by name
experiment = client.get_experiment_by_name(PREPROCESS_EXPERIMENT_NAME)

if experiment is None:
    raise ValueError(f"Experiment '{PREPROCESS_EXPERIMENT_NAME}' not found!")

# Search for the latest run in that experiment
runs = mlflow.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["start_time DESC"],
    max_results=1
)

if runs.empty:
    raise ValueError(f"No runs found in experiment '{PREPROCESS_EXPERIMENT_NAME}'.")

# Extract the latest run ID dynamically
latest_run_id = runs.loc[0, "run_id"]
print(f"Latest run ID: {latest_run_id}")

# Optional: Get model version info if a model was logged in this run
model_versions = client.search_model_versions(f"run_id='{latest_run_id}'")

# Load the artifact file into a DataFrame
columns_path = "X_final_columns.csv"
artifact_uri = mlflow.artifacts.download_artifacts(run_id=latest_run_id, artifact_path=columns_path)
train_columns = pd.read_csv(artifact_uri)["columns"].tolist()

print("Loaded training columns from MLflow:", train_columns)