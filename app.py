"""
app.py — FinAI Advisor Backend (Final Version)
-----------------------------------------------
Handles:
- Fraud Detection
- Budget Prediction
- Investment Suggestion
- Live Crypto Ticker (from crypto_data.csv)
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import load_model

# ============================================================
# FLASK APP INITIALIZATION
# ============================================================
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# ============================================================
# LOAD MODELS
# ============================================================
try:
    fraud_bundle = joblib.load("models/fraud_model.pkl")
    fraud_model = fraud_bundle["model"]
    fraud_encoder = fraud_bundle["encoder"]
    print("✅ Fraud model loaded.")
except Exception as e:
    fraud_model = None
    fraud_encoder = LabelEncoder()
    print("⚠️ Could not load fraud model:", e)

try:
    budget_model = joblib.load("models/budget_model.pkl")
    print("✅ Budget model loaded.")
except Exception as e:
    budget_model = None
    print("⚠️ Could not load budget model:", e)

try:
    invest_model = load_model("models/investment_model.keras")
    invest_scaler = joblib.load("models/scaler.pkl")
    print("✅ LSTM Investment model loaded.")
except Exception as e:
    invest_model = None
    invest_scaler = None
    print("⚠️ Could not load LSTM investment model:", e)


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():
    """Frontend dashboard"""
    return render_template("index.html")


# ------------------------------------------------------------
# 1. FRAUD DETECTION
# ------------------------------------------------------------
@app.route("/predict_fraud", methods=["POST"])
def predict_fraud():
    if fraud_model is None:
        return jsonify({"error": "Fraud model not loaded"}), 500

    try:
        data = request.get_json()
        df = pd.DataFrame([data])

        # Ensure categorical encoding
        df["type_enc"] = fraud_encoder.transform([df["type"].iloc[0].lower()])

        features = [
            "type_enc", "amount", "oldbalanceOrg", "newbalanceOrig",
            "oldbalanceDest", "newbalanceDest", "balance_diff_orig",
            "balance_diff_dest", "error_balance_orig", "error_balance_dest"
        ]
        X = df[features]
        prediction = fraud_model.predict(X)[0]
        proba = fraud_model.predict_proba(X)[0][1]

        return jsonify({
            "is_fraud": bool(prediction),
            "fraud_probability": round(float(proba), 4)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ------------------------------------------------------------
# 2. BUDGET ANALYSIS
# ------------------------------------------------------------
@app.route("/predict_budget", methods=["POST"])
def predict_budget():
    if budget_model is None:
        return jsonify({"error": "Budget model not loaded"}), 500

    try:
        data = request.get_json()
        df = pd.DataFrame([data])

        features = ["amount", "oldbalanceOrg", "newbalanceOrig", "balance_diff_orig"]
        X = df[features]
        pred = budget_model.predict(X)[0]

        return jsonify({
            "predicted_spending_change": round(float(pred), 2),
            "message": "Higher value indicates increased spending trend."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ------------------------------------------------------------
# 3. INVESTMENT SUGGESTION
# ------------------------------------------------------------
@app.route("/suggest_investment", methods=["POST"])
def suggest_investment():
    if invest_model is None or invest_scaler is None:
        return jsonify({"error": "Investment model not loaded"}), 500

    try:
        data = request.get_json()
        df = pd.DataFrame([data])
        df = df.apply(pd.to_numeric, errors='coerce')
        
        if df.isnull().any().any():
            return jsonify({"error": "All features must be numeric."}), 400
        
        if df.shape[1] != invest_scaler.n_features_in_:
            return jsonify({"error": f"Expected {invest_scaler.n_features_in_} features, got {df.shape[1]}"}), 400

        # Scale input
        X_scaled = invest_scaler.transform(df)

        # Prepare sequence for LSTM (single-step prediction)
        seq_length = 10
        # If input < seq_length, pad with zeros
        if len(X_scaled) < seq_length:
            pad = np.zeros((seq_length - len(X_scaled), X_scaled.shape[1]))
            X_seq = np.vstack([pad, X_scaled])
        else:
            X_seq = X_scaled[-seq_length:]
        X_seq = X_seq[np.newaxis, :, :]  # shape: (1, seq_length, features)

        # Predict next-step values
        y_pred = invest_model.predict(X_seq, verbose=0)[0]

        # Simple scoring logic: compare predicted vs current
        diff = y_pred - X_scaled[-1]
        growth_score = diff.mean()

        if growth_score > 0.01:
            recommendation = "Market Expected to Grow — Consider Investing 🟢"
        elif growth_score < -0.01:
            recommendation = "Market Expected to Decline — Hold Off 🔴"
        else:
            recommendation = "Stable Market — Monitor Closely 🟡"

        return jsonify({
            "predicted_features": {col: float(val) for col, val in zip(df.columns, y_pred)},
            "growth_score": round(float(growth_score), 4),
            "recommendation": recommendation
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ------------------------------------------------------------
# 4. LIVE CRYPTO TICKER
# ------------------------------------------------------------
@app.route("/crypto_ticker", methods=["GET"])
def crypto_ticker():
    """Returns the latest crypto close & volume data"""
    try:
        df = pd.read_csv("data/crypto_data.csv")
        latest = df.tail(1).to_dict(orient="records")[0]

        return jsonify({
            "Date": latest["Date"],
            "BTC_Close": latest["Close (BTC)"],
            "BTC_Volume": latest["Volume (BTC)"],
            "ETH_Close": latest["Close (ETH)"],
            "ETH_Volume": latest["Volume (ETH)"],
            "USDT_Close": latest["Close (USDT)"],
            "USDT_Volume": latest["Volume (USDT)"],
            "BNB_Close": latest["Close (BNB)"],
            "BNB_Volume": latest["Volume (BNB)"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# RUN SERVER
# ============================================================
if __name__ == "__main__":
    app.run(debug=True, port=5000)
