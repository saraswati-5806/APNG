from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd


FEATURES = [
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Packet Length Mean",
    "Packet Length Std",
    "SYN Flag Count",
    "ACK Flag Count",
]


BASE_DIR = Path(__file__).resolve().parent
MODEL_FILE = BASE_DIR / "model.joblib"
SCALER_FILE = BASE_DIR / "scaler.joblib"


@lru_cache(maxsize=1)
def load_artifacts():
    scaler = joblib.load(SCALER_FILE)
    model = joblib.load(MODEL_FILE)
    return scaler, model


def predict(features: dict) -> dict:
    missing = [name for name in FEATURES if name not in features]

    if missing:
        raise ValueError(f"Missing ML features: {missing}")

    feature_row = {
        name: float(features[name])
        for name in FEATURES
    }

    frame = pd.DataFrame(
        [feature_row],
        columns=FEATURES,
    )

    scaler, model = load_artifacts()

    scaled = pd.DataFrame(
        scaler.transform(frame),
        columns=FEATURES,
    )

    prediction_value = model.predict(scaled)[0]

    anomaly_score = float(
        model.decision_function(scaled)[0]
    )

    prediction = (
        "ANOMALY"
        if prediction_value == -1
        else "NORMAL"
    )

    return {
        "prediction": prediction,
        "anomaly_score": anomaly_score,
    }