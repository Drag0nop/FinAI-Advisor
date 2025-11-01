"""
train_fraud.py — Train supervised fraud detection model
---------------------------------------------------------
Uses Kaggle 'Synthetic Financial Transactions' dataset.

Goal:
 - Predict 'isFraud' using engineered transaction features.
 - Saves model as models/fraud_model.pkl
"""

import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
import joblib

# === Directory Setup ===
DATA_DIR = "data/processed"  # updated for consistency
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

DATA_PATH = os.path.join(DATA_DIR, "transactions_processed.csv")
MODEL_PATH = os.path.join(MODEL_DIR, "fraud_model.pkl")


# === Load Data ===
def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"❌ Processed transactions not found at {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    print(f"Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


# === Feature Engineering ===
def prepare_features(df):
    le_type = LabelEncoder()
    df["type_enc"] = le_type.fit_transform(df["type"].astype(str))

    features = [
        "type_enc", "amount",
        "oldbalanceOrg", "newbalanceOrig",
        "oldbalanceDest", "newbalanceDest",
        "balance_diff_orig", "balance_diff_dest",
        "error_balance_orig", "error_balance_dest"
    ]
    X = df[features]
    y = df["isFraud"].astype(int)
    return X, y, le_type


# === Train Model ===
def train_model():
    df = load_data()
    X, y, le_type = prepare_features(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    print("🚀 Training RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        class_weight="balanced",
        random_state=42
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]

    print("\n✅ Evaluation Results:")
    print(classification_report(y_test, preds, digits=4))
    print(f"Accuracy: {accuracy_score(y_test, preds):.4f}")
    print(f"ROC-AUC: {roc_auc_score(y_test, probs):.4f}")

    # Save model and encoder
    joblib.dump({"model": model, "encoder": le_type}, MODEL_PATH)
    print(f"✅ Fraud model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train_model()
