import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import joblib
import os

DATA_PATH = '../data'
MODEL_PATH = '../model'

# Ensure model directory exists
os.makedirs(MODEL_PATH, exist_ok=True)

# List of stock CSV filenames (without extension)
stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK']

for stock in stocks:
    print(f"🔄 Training model for {stock}...")
    filepath = os.path.join(DATA_PATH, f"{stock}.csv")

    # Read and clean column names
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip()
    df.rename(columns=lambda x: x.upper(), inplace=True)

    print(f"📊 Columns in {filepath}: {df.columns.tolist()}")

    if 'DATE' not in df.columns:
        raise KeyError(f"'DATE' column not found in {filepath}. Check CSV format.")

    df['DATE'] = pd.to_datetime(df['DATE'], format="%d-%b-%Y", errors='coerce')
    df.sort_values('DATE', inplace=True)
    df.dropna(subset=['DATE'], inplace=True)

    # Required columns
    required_columns = ['OPEN', 'HIGH', 'LOW', 'VOLUME', 'CLOSE']
    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"Missing column '{col}' in {filepath}. Found: {df.columns.tolist()}")

    # Clean numeric columns
    for col in required_columns:
        df[col] = df[col].astype(str).str.replace(',', '')
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(subset=required_columns, inplace=True)

    # Feature & target
    X = df[['OPEN', 'HIGH', 'LOW', 'VOLUME']]
    y = df['CLOSE']

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)

    # Train
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Save
    model_filename = os.path.join(MODEL_PATH, f"{stock}.pkl")
    joblib.dump(model, model_filename)
    print(f"✅ {stock} model saved to {model_filename}")

print("🏁 Training complete for all stocks.")
