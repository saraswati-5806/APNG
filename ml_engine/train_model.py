import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import IsolationForest


# ==========================================
# PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

TRAIN_FILE = BASE_DIR / "datasets" / "processed" / "normal_train.csv"
MODEL_FILE = BASE_DIR / "ml_engine" / "model.joblib"


# ==========================================
# LOAD PROCESSED DATA
# ==========================================

print("=" * 60)
print("APNG - ISOLATION FOREST TRAINING")
print("=" * 60)

print("\nLoading normal training data...")

data = pd.read_csv(TRAIN_FILE)

print(f"Training samples : {len(data):,}")
print(f"Features         : {len(data.columns)}")


# ==========================================
# TRAIN ISOLATION FOREST
# ==========================================

print("\nTraining Isolation Forest...")
print("Please wait...")

model = IsolationForest(
    n_estimators=100,
    contamination="auto",
    random_state=42,
    n_jobs=-1
)

model.fit(data)


# ==========================================
# SAVE MODEL
# ==========================================

joblib.dump(model, MODEL_FILE)


# ==========================================
# VERIFY MODEL
# ==========================================

print("\n" + "=" * 60)
print("TRAINING COMPLETED")
print("=" * 60)

print(f"\nModel saved to:")
print(MODEL_FILE)

print("\nModel configuration:")
print("  Algorithm      : Isolation Forest")
print("  Trees          : 100")
print("  Contamination  : auto")
print("  Random state   : 42")

print("\nThe model has learned patterns from normal network traffic.")

print("\nDay 4 training is complete.")