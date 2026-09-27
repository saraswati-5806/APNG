import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
import joblib


# ==============================
# PATHS
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "datasets"
OUTPUT_DIR = BASE_DIR / "datasets" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==============================
# FIND DATASET FILES
# ==============================

monday_file = DATASET_DIR / "Monday-WorkingHours.pcap_ISCX.csv"

ddos_files = list(DATASET_DIR.glob("*DDoS*.csv"))

if not monday_file.exists():
    raise FileNotFoundError(
        f"Monday dataset not found:\n{monday_file}"
    )

if not ddos_files:
    raise FileNotFoundError(
        "DDoS CSV not found inside the datasets folder."
    )

ddos_file = ddos_files[0]


print("=" * 60)
print("APNG - CICIDS2017 PREPROCESSING")
print("=" * 60)

print(f"\nMonday file : {monday_file.name}")
print(f"DDoS file   : {ddos_file.name}")


# ==============================
# LOAD DATA
# ==============================

print("\nLoading Monday dataset...")
monday = pd.read_csv(monday_file)

print("Loading DDoS dataset...")
ddos = pd.read_csv(ddos_file)


# ==============================
# CLEAN COLUMN NAMES
# ==============================

monday.columns = monday.columns.str.strip()
ddos.columns = ddos.columns.str.strip()


print(f"\nMonday rows : {len(monday):,}")
print(f"DDoS rows   : {len(ddos):,}")


# ==============================
# FEATURES FOR APNG
# ==============================

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
    "ACK Flag Count"
]


# ==============================
# CHECK FEATURES
# ==============================

missing_monday = [f for f in FEATURES if f not in monday.columns]
missing_ddos = [f for f in FEATURES if f not in ddos.columns]

if missing_monday:
    raise ValueError(
        f"Missing features in Monday dataset:\n{missing_monday}"
    )

if missing_ddos:
    raise ValueError(
        f"Missing features in DDoS dataset:\n{missing_ddos}"
    )


# ==============================
# SELECT FEATURES
# ==============================

X_train = monday[FEATURES].copy()
X_test = ddos[FEATURES].copy()


# ==============================
# CONVERT TO NUMERIC
# ==============================

for column in FEATURES:
    X_train[column] = pd.to_numeric(
        X_train[column], errors="coerce"
    )

    X_test[column] = pd.to_numeric(
        X_test[column], errors="coerce"
    )


# ==============================
# HANDLE INFINITY
# ==============================

X_train = X_train.replace([np.inf, -np.inf], np.nan)
X_test = X_test.replace([np.inf, -np.inf], np.nan)


# ==============================
# REMOVE MISSING VALUES
# ==============================

before_train = len(X_train)
before_test = len(X_test)

X_train = X_train.dropna()
X_test = X_test.dropna()

print("\nRows removed during cleaning:")
print(f"Monday : {before_train - len(X_train):,}")
print(f"DDoS   : {before_test - len(X_test):,}")


# ==============================
# SCALING
# ==============================

print("\nScaling features...")

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


# ==============================
# SAVE PROCESSED DATA
# ==============================

train_output = OUTPUT_DIR / "normal_train.csv"
test_output = OUTPUT_DIR / "ddos_test.csv"
scaler_output = OUTPUT_DIR / "scaler.joblib"

pd.DataFrame(
    X_train_scaled,
    columns=FEATURES
).to_csv(train_output, index=False)

pd.DataFrame(
    X_test_scaled,
    columns=FEATURES
).to_csv(test_output, index=False)

joblib.dump(scaler, scaler_output)


# ==============================
# SUMMARY
# ==============================

print("\n" + "=" * 60)
print("PREPROCESSING COMPLETED")
print("=" * 60)

print(f"\nTraining samples : {len(X_train_scaled):,}")
print(f"Testing samples  : {len(X_test_scaled):,}")
print(f"Features         : {len(FEATURES)}")

print("\nSelected features:")

for feature in FEATURES:
    print(f"  - {feature}")

print("\nGenerated files:")

print(f"  {train_output}")
print(f"  {test_output}")
print(f"  {scaler_output}")

print("\nDay 3 preprocessing is complete.")