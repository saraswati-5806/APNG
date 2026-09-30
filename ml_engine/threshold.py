import os
import joblib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(
    BASE_DIR, "..", "datasets", "processed", "normal_train.csv"
)

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

model = joblib.load(MODEL_PATH)

df = pd.read_csv(DATA_PATH, usecols=FEATURES)

df = df.replace([np.inf, -np.inf], 0)
df = df.fillna(0)

# The training CSV is already in the same feature space used by the model.
X = df.values

# Reconstruction error
reconstructed = model.predict(X)
errors = np.mean((X - reconstructed) ** 2, axis=1)

threshold = np.percentile(errors, 99)

print("Autoencoder Threshold Results")
print("--------------------------------")
print("Mean reconstruction error:", errors.mean())
print("Maximum reconstruction error:", errors.max())
print("99th percentile threshold:", threshold)

print("\nThreshold calculation complete.")