from data.fraud_selection import choose_fraud_type
from data.fraud_generators import FRAUD_GENERATORS
from data.fraud_generators import FRAUD_WEIGHTS

def test_choose_fraud_generator_returns_valid_function():
    fraud_generator = choose_fraud_type()

    assert callable(fraud_generator)
    assert fraud_generator in FRAUD_GENERATORS.values()
def test_fraud_weights_cover_all_generators():
    assert set(FRAUD_GENERATORS.keys()) ==set(FRAUD_WEIGHTS.keys())