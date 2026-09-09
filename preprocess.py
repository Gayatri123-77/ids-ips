import os
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
 
DATA_DIR = "data"
ARTIFACT_DIR = "artifacts"
 
# Official NSL-KDD column names (41 features + label + difficulty)
COLUMN_NAMES = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes",
    "land", "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in",
    "num_compromised", "root_shell", "su_attempted", "num_root",
    "num_file_creations", "num_shells", "num_access_files", "num_outbound_cmds",
    "is_host_login", "is_guest_login", "count", "srv_count", "serror_rate",
    "srv_serror_rate", "rerror_rate", "srv_rerror_rate", "same_srv_rate",
    "diff_srv_rate", "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count",
    "dst_host_same_srv_rate", "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate", "dst_host_srv_serror_rate", "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate", "label", "difficulty",
]
 
CATEGORICAL_COLS = ["protocol_type", "service", "flag"]
 
 
def load_raw(filename):
    path = os.path.join(DATA_DIR, filename)
    df = pd.read_csv(path, names=COLUMN_NAMES, header=None)
    return df
 
 
def to_binary_label(df):
    # NSL-KDD's "label" column holds the specific attack name (or "normal").
    # For a 1-day binary classifier we only care about normal vs attack.
    return (df["label"].str.strip() != "normal").astype(int)
 
 
def preprocess():
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
 
    train_df = load_raw("KDDTrain+.txt")
    test_df = load_raw("KDDTest+.txt")
 
    y_train = to_binary_label(train_df)
    y_test = to_binary_label(test_df)
 
    # Keep an untouched copy of the test set (minus the giveaway label
    # columns) so simulate_detector.py can print readable rows later.
    raw_test_display = test_df.drop(columns=["label", "difficulty"]).copy()
 
    X_train_raw = train_df.drop(columns=["label", "difficulty"])
    X_test_raw = test_df.drop(columns=["label", "difficulty"])
 
    # One-hot encode categorical columns, then align train/test columns
    # (the test set may not contain every service value seen in train).
    X_train_enc = pd.get_dummies(X_train_raw, columns=CATEGORICAL_COLS)
    X_test_enc = pd.get_dummies(X_test_raw, columns=CATEGORICAL_COLS)
    X_test_enc = X_test_enc.reindex(columns=X_train_enc.columns, fill_value=0)
 
    feature_columns = list(X_train_enc.columns)
 
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_enc)
    X_test_scaled = scaler.transform(X_test_enc)
 
    np.save(os.path.join(ARTIFACT_DIR, "X_train.npy"), X_train_scaled)
    np.save(os.path.join(ARTIFACT_DIR, "X_test.npy"), X_test_scaled)
    np.save(os.path.join(ARTIFACT_DIR, "y_train.npy"), y_train.values)
    np.save(os.path.join(ARTIFACT_DIR, "y_test.npy"), y_test.values)
 
    joblib.dump(scaler, os.path.join(ARTIFACT_DIR, "scaler.joblib"))
    joblib.dump(feature_columns, os.path.join(ARTIFACT_DIR, "feature_columns.joblib"))
    joblib.dump(raw_test_display, os.path.join(ARTIFACT_DIR, "raw_test.joblib"))
 
    print(f"Train set: {X_train_scaled.shape[0]} rows, {X_train_scaled.shape[1]} features")
    print(f"Test set:  {X_test_scaled.shape[0]} rows")
    print(f"Attack rate in train: {y_train.mean():.2%}")
    print(f"Attack rate in test:  {y_test.mean():.2%}")
    print(f"Artifacts saved to ./{ARTIFACT_DIR}/")
 
 
if __name__ == "__main__":
    preprocess()
 