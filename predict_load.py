import torch
import os
from google.cloud import storage
from model import LoadForecastingANN

# ================= CONFIG =================
BUCKET = "load-forecasting-models-2026"
BLOB_PATH = "models/load_model.pth"
LOCAL_MODEL_PATH = "cached_model.pth"

# TRUE LOAD RANGE (same as training)
LOAD_MIN = 1540.9425
LOAD_MAX = 8565.135

_model = None


# ================= DENORMALIZATION =================
def denormalize(y):
    return y * (LOAD_MAX - LOAD_MIN) + LOAD_MIN


# ================= LOAD MODEL =================
def load_model():
    global _model

    if _model is None:
        if not os.path.exists(LOCAL_MODEL_PATH):
            client = storage.Client()
            bucket = client.bucket(BUCKET)
            blob = bucket.blob(BLOB_PATH)
            blob.download_to_filename(LOCAL_MODEL_PATH)
            print("✅ Model downloaded from GCS")

        checkpoint = torch.load(LOCAL_MODEL_PATH, map_location="cpu")

        _model = LoadForecastingANN(
            checkpoint["input_size"],
            checkpoint["hidden_size"],
            checkpoint["output_size"]
        )
        _model.load_state_dict(checkpoint["model_state_dict"])
        _model.eval()

        print("✅ Model loaded into memory")

    return _model


# ================= PREDICTION =================
def predict_load(x):
    if len(x) != 11:
        raise ValueError("Model expects 11 input features")

    model = load_model()

    with torch.no_grad():
        y_norm = model(torch.FloatTensor([x])).item()

    # 🔥 CRITICAL FIX
    mw = denormalize(y_norm)

    # clamp to safe range
    mw = max(LOAD_MIN, min(mw, LOAD_MAX))

    return round(mw, 2)
