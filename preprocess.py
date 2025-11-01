"""
preprocess.py — Unified Preprocessing Script
---------------------------------------------------------
Handles:
1. transactions.csv  -> Fraud Detection
2. crypto_data.csv   -> Crypto Trend Analysis
3. stock_data.csv    -> Stock Metadata
"""

import pandas as pd
import os

DATA_DIR = "data"
OUTPUT_DIR = os.path.join(DATA_DIR, "processed")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========  TRANSACTION DATA PREPROCESSING ==========
def preprocess_transactions():
    path = os.path.join(DATA_DIR, "transactions.csv")
    if not os.path.exists(path):
        print("⚠️ transactions.csv not found, skipping...")
        return None

    df = pd.read_csv(path)
    print(f"Loaded transactions: {len(df)} rows")

    df = df.dropna()
    df["type"] = df["type"].astype(str).str.lower()

    # Feature Engineering
    df["balance_diff_orig"] = df["oldbalanceOrg"] - df["newbalanceOrig"]
    df["balance_diff_dest"] = df["newbalanceDest"] - df["oldbalanceDest"]
    df["error_balance_orig"] = df["oldbalanceOrg"] - df["newbalanceOrig"] - df["amount"]
    df["error_balance_dest"] = df["newbalanceDest"] + df["amount"] - df["oldbalanceDest"]

    df = df.drop(columns=["nameOrig", "nameDest"])
    output = os.path.join(OUTPUT_DIR, "transactions_processed.csv")
    df.to_csv(output, index=False)
    print(f"✅ Transactions processed → {output}")
    return df


# ==========  CRYPTO DATA PREPROCESSING ==========
def preprocess_crypto():
    path = os.path.join(DATA_DIR, "crypto_data.csv")
    if not os.path.exists(path):
        print("⚠️ crypto_data.csv not found, skipping...")
        return None

    df = pd.read_csv(path)
    print(f"Loaded crypto data: {len(df)} rows")

    # Clean column names
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    # Fill missing values
    df = df.ffill()

    # Add moving averages for trends
    for col in ["Close_BTC", "Close_ETH", "Close_BNB"]:
        df[f"{col}_SMA7"] = df[col].rolling(window=7).mean()
        df[f"{col}_SMA30"] = df[col].rolling(window=30).mean()

    output = os.path.join(OUTPUT_DIR, "crypto_processed.csv")
    df.to_csv(output, index=False)
    print(f"✅ Crypto processed → {output}")
    return df


# ==========  STOCK DATA PREPROCESSING ==========
def preprocess_stocks():
    path = os.path.join(DATA_DIR, "stock_data.csv")
    if not os.path.exists(path):
        print("⚠️ stock_data.csv not found, skipping...")
        return None

    df = pd.read_csv(path)
    print(f"Loaded stock data: {len(df)} rows")

    # Keep relevant columns only
    keep_cols = ["Symbol", "Security Name", "Listing Exchange", "Market Category", "ETF", "Financial Status"]
    df = df[keep_cols].dropna().drop_duplicates()

    # Convert ETF to boolean
    df["ETF"] = df["ETF"].astype(str).map({"Y": 1, "N": 0})

    output = os.path.join(OUTPUT_DIR, "stock_processed.csv")
    df.to_csv(output, index=False)
    print(f"✅ Stock processed → {output}")
    return df


if __name__ == "__main__":
    preprocess_transactions()
    preprocess_crypto()
    preprocess_stocks()
