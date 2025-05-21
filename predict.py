import joblib
import numpy as np

def make_prediction(data):
    model = joblib.load("models/model.pkl")
    input_data = np.array(data['features']).reshape(1, -1)
    return model.predict(input_data)[0]