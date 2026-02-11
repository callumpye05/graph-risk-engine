import random
from data.fraud_generators import FRAUD_GENERATORS, FRAUD_WEIGHTS

def choose_fraud_type() : 

    fraud_types = list(FRAUD_WEIGHTS.keys())
    weights = list(FRAUD_WEIGHTS.values())
    chosen_type = random.choices(fraud_types, weights=weights,k=1)[0]
    return FRAUD_GENERATORS[chosen_type]