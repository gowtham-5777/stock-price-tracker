from flask import Flask, request, jsonify
from predict import make_prediction

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    prediction = make_prediction(data)
    return jsonify({"prediction": prediction})

if __name__ == '__main__':
    app.run(debug=True, port=5000)