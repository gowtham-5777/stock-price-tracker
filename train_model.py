import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os
import glob

def load_and_prepare_data():
    all_files = glob.glob("data/*.csv")
    dfs = []

    for file in all_files:
        df = pd.read_csv(file)
        df['Company'] = os.path.basename(file).split('.')[0]
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)

    # Adjust this to match your dataset's columns
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.dropna(inplace=True)
    return df

def train_and_save_model():
    df = load_and_prepare_data()

    X = df[['Open', 'High', 'Low', 'Volume']]
    y = df['Close']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)

    model = RandomForestRegressor()
    model.fit(X_train, y_train)

    joblib.dump(model, "models/model.pkl")
    print("✅ Model trained and saved as models/model.pkl")

if __name__ == "__main__":
    train_and_save_model()
