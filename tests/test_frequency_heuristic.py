import pytest
from heuristics.frequency import FrequencyHeuristic


#Stream Processing tests
#


def test_frequency_no_transactions():
    """Test a brand new user making their first transaction."""
    heuristic = FrequencyHeuristic(max_tx_per_hour=5)
    history = {"avg_amount": 0.0, "std_amount": 1.0, "recent_count": 0}
    score = heuristic.evaluate(history)
    assert score == 0.2


def test_frequency_sparse_activity():
    """Test normal, sparse activity"""
    heuristic = FrequencyHeuristic(max_tx_per_hour=5)
    history = {"avg_amount": 100.0, "std_amount": 10.0, "recent_count": 2}
    
    score = heuristic.evaluate(history)
    assert 0.0 < score < 1.0
    assert score == 0.6


def test_frequency_burst_detected():
    """Test when the user exactly crosses the threshold"""
    heuristic = FrequencyHeuristic(max_tx_per_hour=5)

    history = {"avg_amount": 100.0, "std_amount": 10.0, "recent_count": 5}
    score = heuristic.evaluate(history)
    assert score == 1.0


def test_frequency_saturates():
    """Test when the user is completely spamming the network"""
    heuristic = FrequencyHeuristic(max_tx_per_hour=5)    
    history = {"avg_amount": 100.0, "std_amount": 10.0, "recent_count": 20}
    score = heuristic.evaluate(history)
    assert score == 1.0


def test_frequency_score_bounds():
    """Prove the heuristic never returns a score outside [0.0, 1.0]."""
    heuristic = FrequencyHeuristic(max_tx_per_hour=10)
    for count in [0, 1, 9, 10, 100, 1000]:
        history = {"recent_count": count}
        score = heuristic.evaluate(history)
        assert 0.0 <= score <= 1.0