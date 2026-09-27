import pandas as pd
import joblib
import numpy as np
from pathlib import Path
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score
)


# ==========================================
# PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

TEST_FILE = BASE_DIR / "datasets" / "processed" / "ddos_test.csv"
MODEL_FILE = BASE_DIR / "ml_engine" / "model.joblib"


# ==========================================
# LOAD DATA AND MODEL
# ==========================================

print("=" * 60)
print("APNG - ISOLATION FOREST EVALUATION")
print("=" * 60)

print("\nLoading DDoS test data...")

X_test = pd.read_csv(TEST_FILE)

print(f"Test samples : {len(X_test):,}")
print(f"Features     : {len(X_test.columns)}")

print("\nLoading trained Isolation Forest...")

model = joblib.load(MODEL_FILE)

print("Model loaded successfully.")


# ==========================================
# PREDICT
# ==========================================

print("\nRunning anomaly detection...")
print("Please wait...")

predictions = model.predict(X_test)

# Isolation Forest:
#  1  = normal
# -1  = anomaly

y_pred = np.where(predictions == -1, 1, 0)


# ==========================================
# DDoS TEST DATA
# ==========================================

# Since this test file contains DDoS traffic,
# we treat every row as an actual attack.

y_true = np.ones(len(X_test), dtype=int)


# ==========================================
# CALCULATE ANOMALY SCORES
# ==========================================

scores = model.decision_function(X_test)

# Lower Isolation Forest decision scores
# indicate more anomalous observations.


# ==========================================
# METRICS
# ==========================================

precision = precision_score(
    y_true,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_true,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_true,
    y_pred,
    zero_division=0
)


# ==========================================
# CONFUSION MATRIX
# ==========================================

cm = confusion_matrix(y_true, y_pred)


# ==========================================
# RESULTS
# ==========================================

print("\n" + "=" * 60)
print("EVALUATION RESULTS")
print("=" * 60)

print(f"\nDDoS samples tested : {len(X_test):,}")

print(
    f"DDoS detected       : {np.sum(y_pred == 1):,}"
)

print(
    f"DDoS missed         : {np.sum(y_pred == 0):,}"
)

print("\nPerformance:")

print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")

print("\nConfusion Matrix:")
print(cm)

print("\nAnomaly score information:")

print(f"Minimum score : {scores.min():.4f}")
print(f"Maximum score : {scores.max():.4f}")
print(f"Mean score    : {scores.mean():.4f}")

print("\n" + "=" * 60)
print("DAY 5 EVALUATION COMPLETED")
print("=" * 60)
