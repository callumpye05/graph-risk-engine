
from datetime import datetime, timedelta
from preprocessing.transaction_stats import compute_features
from heuristics.frequency import FrequencyHeuristic
from data.transaction import Transaction


def make_transactions(account_id, offsets_seconds, now=None):
    if now is None:
        now = datetime.now()
    return [
        Transaction(account_id,account_id + 1,10.0,now + timedelta(seconds=o), "transfer",False)
        for o in offsets_seconds
    ]

# Helper: convert compute_features output to what FrequencyHeuristic expects
def features_to_heuristic_stats(features):
    return {
        "out_timestamps": {
            acc: node["timestamps"] for acc, node in features["node"].items()
        }
    }

# ------------------------
# Tests
# ------------------------

def test_frequency_no_transactions():
    transactions = []
    features = compute_features(transactions)
    stats = features_to_heuristic_stats(features)

    heuristic = FrequencyHeuristic(window_scale=timedelta(minutes=5), scale=5)
    score = heuristic.evaluate(account_id=1, stats=stats)
    assert score == 0.0


def test_frequency_sparse_activity():
    now = datetime.now()
    transactions = make_transactions(1, [0, 600, 1200], now)
    features = compute_features(transactions)
    stats = features_to_heuristic_stats(features)

    heuristic = FrequencyHeuristic(window_scale=timedelta(minutes=5), scale=5)
    score = heuristic.evaluate(account_id=1, stats=stats)
    assert 0.0 < score < 1.0


def test_frequency_burst_detected():
    now = datetime.now()
    transactions = make_transactions(1, [0, 10, 20, 30, 40], now)
    features = compute_features(transactions)
    stats = features_to_heuristic_stats(features)

    heuristic = FrequencyHeuristic(window_scale=timedelta(minutes=2), scale=5)
    score = heuristic.evaluate(account_id=1, stats=stats)
    assert score == 1.0


def test_frequency_saturates():
    now = datetime.now()
    transactions = make_transactions(1, [0, 5, 10, 15, 20, 25, 30], now)
    features = compute_features(transactions)
    stats = features_to_heuristic_stats(features)

    heuristic = FrequencyHeuristic(window_scale=timedelta(minutes=1), scale=3)
    score = heuristic.evaluate(account_id=1, stats=stats)
    assert score == 1.0


def test_frequency_score_bounds():
    now = datetime.now()
    transactions = make_transactions(1, [0, 1, 2], now)
    features = compute_features(transactions)
    stats = features_to_heuristic_stats(features)

    heuristic = FrequencyHeuristic(window_scale=timedelta(minutes=1), scale=10)
    score = heuristic.evaluate(account_id=1, stats=stats)
    assert 0.0 <= score <= 1.0