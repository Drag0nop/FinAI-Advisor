"""
train_budget.py — Predicts user spending trends from transaction data
---------------------------------------------------------
Uses Kaggle transactions_processed.csv for budget forecasting.
"""

import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib


DATA_PATH = "data/processed/transactions_processed.csv"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "budget_model.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

def load_data():
    df = pd.read_csv(DATA_PATH)
    df = df[df["amount"] > 0]  # Filter invalid or negative transactions
    return df

def prepare_data(df):
    features = ["amount", "oldbalanceOrg", "newbalanceOrig", "balance_diff_orig"]
    X = df[features]
    y = df["balance_diff_orig"].abs()  # Predict absolute spending change
    return X, y

def train_budget_model():
    df = load_data()
    X, y = prepare_data(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = GradientBoostingRegressor(
        n_estimators=150, 
        max_depth=5, 
        random_state=42
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    print(f"✅ Budget Model Trained Successfully")
    print(f"   MAE: {mae:.2f}")
    print(f"   R² Score: {r2:.3f}")

    joblib.dump(model, MODEL_PATH)
    print(f"💾 Model saved → {MODEL_PATH}")

if __name__ == "__main__":
    train_budget_model()
