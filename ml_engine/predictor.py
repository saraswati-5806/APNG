import os
import joblib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "model.joblib")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.joblib")
AUTOENCODER_PATH = os.path.join(BASE_DIR, "autoencoder.joblib")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
autoencoder = joblib.load(AUTOENCODER_PATH)

AUTOENCODER_THRESHOLD = 7.411527198257522

FEATURE_MAP = {
    "flow_duration": "Flow Duration",
    "total_fwd_packets": "Total Fwd Packets",
    "total_backward_packets": "Total Backward Packets",
    "total_length_fwd_packets": "Total Length of Fwd Packets",
    "total_length_bwd_packets": "Total Length of Bwd Packets",
    "flow_bytes_per_sec": "Flow Bytes/s",
    "flow_packets_per_sec": "Flow Packets/s",
    "packet_length_mean": "Packet Length Mean",
    "packet_length_std": "Packet Length Std",
    "syn_flag_count": "SYN Flag Count",
    "ack_flag_count": "ACK Flag Count",
}


def predict_flow(flow_data: dict) -> dict:

    for feature in FEATURE_MAP:
        if feature not in flow_data:
            raise ValueError(f"Missing feature: {feature}")

    features = pd.DataFrame(
        [[float(flow_data[api_name]) for api_name in FEATURE_MAP]],
        columns=list(FEATURE_MAP.values())
    )

    # Scale input for both ML models
    scaled_array = scaler.transform(features)

    scaled_features = pd.DataFrame(
        scaled_array,
        columns=list(FEATURE_MAP.values())
    )

    # Isolation Forest
    prediction_value = model.predict(scaled_features)[0]
    isolation_score = float(
        model.decision_function(scaled_features)[0]
    )

    isolation_prediction = (
        "ANOMALY" if prediction_value == -1 else "NORMAL"
    )

    # Autoencoder
    reconstructed = autoencoder.predict(scaled_array)

    reconstruction_error = float(
        np.mean((scaled_array - reconstructed) ** 2)
    )

    autoencoder_prediction = (
        "ANOMALY"
        if reconstruction_error > AUTOENCODER_THRESHOLD
        else "NORMAL"
    )

    # Combined result
    if (
        isolation_prediction == "ANOMALY"
        or autoencoder_prediction == "ANOMALY"
    ):
        final_prediction = "ANOMALY"
    else:
        final_prediction = "NORMAL"

    return {
        "prediction": final_prediction,

        "isolation_forest": {
            "prediction": isolation_prediction,
            "anomaly_score": isolation_score,
        },

        "autoencoder": {
            "prediction": autoencoder_prediction,
            "reconstruction_error": reconstruction_error,
            "threshold": AUTOENCODER_THRESHOLD,
        },

        "anomaly_model": "IsolationForest + Autoencoder",
    }