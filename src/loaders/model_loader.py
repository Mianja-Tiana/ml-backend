import pickle
import joblib
from pathlib import Path
from .blob_loader import BlobLoader
import os
from dotenv import load_dotenv




load_dotenv()

class ModelArtifacts:
    model = None
    fe = None

    @classmethod
    def load(cls):
        if cls.model and cls.fe:
            return  # already loaded

        loader = BlobLoader()

        # Azure blob paths from env vars
        model_blob = os.getenv(
            "MODEL_BLOB_PATH",
            "mlflow/1/models/m-1294491f521b479d96686a0db03633ee/artifacts/model.pkl"
        )
        fe_blob = os.getenv(
            "FE_BLOB_PATH",
            "mlflow/1/77419d51036c49b4940e3eadf9f048a3/artifacts/mlflow-artifacts/feature_engineer.joblib"
        )

        # Local paths from env vars or defaults
        local_model = os.getenv("LOCAL_MODEL_PATH", "/tmp/model.pkl")
        local_fe = os.getenv("LOCAL_FE_PATH", "/tmp/feature_engineering.joblib")

        loader.download(model_blob, local_model)
        loader.download(fe_blob, local_fe)

        with open(local_model, "rb") as f:
            cls.model = pickle.load(f)

        cls.fe = joblib.load(local_fe)