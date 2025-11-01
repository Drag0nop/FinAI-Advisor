"""
train_investment.py — AI-powered Investment Advisor
---------------------------------------------------------
Combines crypto trends + stock metadata to rank assets by stability & growth.
"""

import pandas as pd
import os
import numpy as np
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
import joblib

DATA_CRYPTO = "data/processed/crypto_processed.csv"
DATA_STOCK = "data/processed/stock_processed.csv"
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "investment_model.keras")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

def load_data():
    crypto = pd.read_csv(DATA_CRYPTO)
    stock = pd.read_csv(DATA_STOCK)
    return crypto, stock

def prepare_crypto_features(crypto):
    crypto = crypto.dropna()
    features = ["Close_BTC", "Close_ETH", "Close_BNB", "Close_BTC_SMA7", "Close_BTC_SMA30"]
    return crypto[features]

def create_sequences(X, seq_length=10):
    sequences = []
    for i in range(len(X) - seq_length):
        sequences.append(X[i:i+seq_length])
    return np.array(sequences)

def train_investment_model():
    crypto, stock = load_data()
    X = prepare_crypto_features(crypto).values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, SCALER_PATH)

    seq_length = 10
    X_seq = create_sequences(X_scaled, seq_length)
    y_seq = X_scaled[seq_length:]  # predict next step in sequence

    model = Sequential()
    model.add(LSTM(64, input_shape=(X_seq.shape[1], X_seq.shape[2]), return_sequences=False))
    model.add(Dense(X_seq.shape[2]))
    model.compile(optimizer='adam', loss='mse')

    early_stop = EarlyStopping(monitor='loss', patience=5, restore_best_weights=True)
    model.fit(X_seq, y_seq, epochs=50, batch_size=16, callbacks=[early_stop], verbose=1)

    model.save(MODEL_PATH)
    print(f"✅ LSTM investment model trained and saved → {MODEL_PATH}")

if __name__ == "__main__":
    train_investment_model()
