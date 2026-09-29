import os
import joblib
import pandas as pd
from sklearn.neural_network import MLPRegressor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(
    BASE_DIR, "..", "datasets", "processed", "normal_train.csv"
)
SCALER_PATH = os.path.join(BASE_DIR, "scaler.joblib")
MODEL_PATH = os.path.join(BASE_DIR, "autoencoder.joblib")

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

print("Loading training data...")
df = pd.read_csv(DATA_PATH, usecols=FEATURES)

df = df.replace([float("inf"), float("-inf")], 0)
df = df.fillna(0)

# Use the existing scaler so both ML models use the same feature scale.
scaler = joblib.load(SCALER_PATH)
X = scaler.transform(df)

print("Training Autoencoder...")

autoencoder = MLPRegressor(
    hidden_layer_sizes=(8, 4, 8),
    activation="relu",
    solver="adam",
    max_iter=50,
    random_state=42,
    batch_size=256,
    early_stopping=True,
    validation_fraction=0.1,
    n_iter_no_change=5
)

autoencoder.fit(X, X)

joblib.dump(autoencoder, MODEL_PATH)

print("Autoencoder saved:", MODEL_PATH)
print("Iterations:", autoencoder.n_iter_)
print("Training loss:", autoencoder.loss_)