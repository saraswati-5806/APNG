import os
import joblib
import pandas as pd


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "model.joblib")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.joblib")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)


# Public/API feature names → original CICIDS2017 training names
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
    """
    Run Isolation Forest prediction on one network flow.
    """

    # Check that all required API fields are present
    for feature in FEATURE_MAP:
        if feature not in flow_data:
            raise ValueError(f"Missing feature: {feature}")

    # Convert API names to the exact names used during model training
    features = pd.DataFrame(
        [[
            float(flow_data[api_name])
            for api_name in FEATURE_MAP
        ]],
        columns=list(FEATURE_MAP.values())
    )

    # Apply the same scaler used during training
    scaled_array = scaler.transform(features)

    # Keep the original training feature names for the model
    scaled_features = pd.DataFrame(
        scaled_array,
        columns=list(FEATURE_MAP.values())
    )

    prediction_value = model.predict(scaled_features)[0]
    anomaly_score = float(
        model.decision_function(scaled_features)[0]
    )

    prediction = (
        "ANOMALY"
        if prediction_value == -1
        else "NORMAL"
    )

    return {
        "prediction": prediction,
        "anomaly_score": anomaly_score,
        "anomaly_model": "IsolationForest",
    }