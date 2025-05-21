from predict import make_prediction

def test_make_prediction():
    sample_input = {"features": [100.5, 200.6, 300.1]}
    result = make_prediction(sample_input)
    assert isinstance(result, float) or isinstance(result, int)
