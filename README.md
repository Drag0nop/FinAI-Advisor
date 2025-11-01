# FinAI Advisor

**FinAI Advisor** is an AI-powered financial assistant that provides:  
- Fraud Detection  
- Budget Prediction  
- Investment Suggestions using LSTM models  
- Live Cryptocurrency Market Data  

It combines classical machine learning and deep learning models to offer real-time insights for individuals and businesses.

---

## 🛠 Features

### 1. Fraud Detection
- Detect potentially fraudulent transactions.
- Returns fraud probability and status.
- Uses a pre-trained ML model with categorical encoding.

### 2. Budget Prediction
- Forecasts spending trends based on transaction data.
- Helps users manage and optimize personal finances.
- Uses a regression-based ML model.

### 3. Investment Suggestion
- Uses an **LSTM model** trained on historical crypto data.
- Predicts next-step prices and computes growth trends.
- Provides actionable recommendations:  
  - Market Expected to Grow 🟢  
  - Market Expected to Decline 🔴  
  - Stable Market 🟡

### 4. Live Crypto Ticker
- Displays latest cryptocurrency prices and volumes.
- Supports BTC, ETH, USDT, and BNB.
- Data refreshed in real-time.

---

## 📁 Project Structure

FinAI_advisor/
├── app.py                      # Flask backend
├── preprocess.py               # Data preprocessing
├── train_budget.py             # Budget model training
├── train_investment.py         # Investment model training
├── train_fraud.py              # Fraud model training
├── models/                     # Trained ML models
│   ├── fraud_model.pkl
│   ├── budget_model.pkl
│   ├── investment_model.keras
│   └── scaler.pkl
├── data/           
│   ├── processed/             # Processed data  for training
│   ├── transactions.csv
│   ├── crypto_data.csv
│   └── stock_data.csv
├── templates/            
│   └── index.html              # Frontend dashboard
├── static/
│   ├── style.css
│   └── script.js
├── requirements.txt            # All Python dependencies
└── README.md                   # Quick setup & instructions

## ⚙️ Installation

1. Clone the repository:

git clone https://github.com/your-username/FinAI-Advisor.git
cd FinAI-Advisor

2. Install dependencies:

pip install -r requirements.txt

3. download dataset

https://www.kaggle.com/datasets/ealaxi/paysim1
https://www.kaggle.com/datasets/mattiuzc/stock-exchange-data
https://www.kaggle.com/datasets/bishop36/crypto-data

## Running the Application

python app.py

## 🧠 How it Works

Fraud Detection: Pre-trained classifier predicts if a transaction is fraudulent.

Budget Prediction: Regression model predicts spending trends based on input transaction data.

Investment Suggestion:

1. Input features (BTC, ETH, BNB prices & SMAs) are scaled using StandardScaler.

2. An LSTM predicts next-step crypto prices.

3. A simple growth score computes investment recommendations.

Crypto Ticker: Reads latest crypto data from CSV and displays it in a grid format.

## 🔧 Technologies Used

Backend: Python, Flask

Frontend: HTML, CSS, JavaScript

Machine Learning: Scikit-learn (fraud & budget models)

Deep Learning: TensorFlow/Keras (LSTM for investments)

Data Handling: Pandas, NumPy

## 📊 Future Enhancements

Integrate real-time API for cryptocurrency prices instead of CSV.

Add user authentication for personalized dashboards.

Expand investment recommendations to stocks and ETFs.

Improve budget forecasting with time-series models.