# tests/test_compute_features_simple.py
from datetime import datetime, timedelta
from collections import defaultdict
from data.transaction import Transaction
from preprocessing.transaction_stats import compute_features

def test_feature_node_counts_and_totals():
    now = datetime.now()
    transactions = [
        Transaction(1, 2, 100.0, now, "transfer", False),
        Transaction(1, 3, 200.0, now + timedelta(minutes=5), "transfer", False),
        Transaction(2, 3, 50.0, now + timedelta(minutes=10), "transfer", False),
    ]

    features = compute_features(transactions)

    # Node 1
    assert features["node"][1]["out_count"] == 2
    assert features["node"][1]["total_out"] == 300.0
    assert features["node"][1]["in_count"] == 0
    assert features["node"][1]["total_in"] == 0.0

    # Node 2
    assert features["node"][2]["out_count"] == 1
    assert features["node"][2]["total_out"] == 50.0
    assert features["node"][2]["in_count"] == 1
    assert features["node"][2]["total_in"] == 100.0

    # Node 3
    assert features["node"][3]["out_count"] == 0
    assert features["node"][3]["total_out"] == 0.0
    assert features["node"][3]["in_count"] == 2
    assert features["node"][3]["total_in"] == 250.0


def test_feature_edge_counts_and_totals():
    now = datetime.now()
    transactions = [
        Transaction(1, 2, 100.0, now, "transfer", False),
        Transaction(1, 3, 200.0, now + timedelta(minutes=5), "transfer", False),
        Transaction(2, 3, 50.0, now + timedelta(minutes=10), "transfer", False),
    ]

    features = compute_features(transactions)

    assert features["edges"][(1, 2)]["count"] == 1
    assert features["edges"][(1, 2)]["total_amount"] == 100.0

    assert features["edges"][(1, 3)]["count"] == 1
    assert features["edges"][(1, 3)]["total_amount"] == 200.0

    assert features["edges"][(2, 3)]["count"] == 1
    assert features["edges"][(2, 3)]["total_amount"] == 50.0


def test_feature_global_totals():
    now = datetime.now()
    transactions = [
        Transaction(1, 2, 100.0, now, "transfer", False),
        Transaction(1, 3, 200.0, now + timedelta(minutes=5), "transfer", False),
        Transaction(2, 3, 50.0, now + timedelta(minutes=10), "transfer", False),
    ]

    features = compute_features(transactions)

    assert features["global"]["total_transactions"] == 3
    assert features["global"]["total_amount"] == 350.0