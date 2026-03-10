import pytest
from heuristics.frequency import FrequencyHeuristic
from heuristics.high_amount import HighAmountHeuristic # Or HighAmountHeuristic if you didn't rename
from scoring.risk_score import compute_single_risk_score

@pytest.fixture
def brains():
    """Pytest fixture to provide initialized heuristics for our tests."""
    amount_brain = HighAmountHeuristic(std_threshold=3.0)
    freq_brain = FrequencyHeuristic(max_tx_per_hour=5)
    return amount_brain, freq_brain

def test_risk_score_structure(brains):
    amount_brain, freq_brain = brains
    history = {"avg_amount": 100.0, "std_amount": 10.0, "recent_count": 2}
    
    results = compute_single_risk_score(amount_brain, freq_brain, 105.0, history)

    assert "risk" in results
    assert "signals" in results
    assert isinstance(results["risk"], float)

def test_risk_score_contains_all_signals(brains):
    amount_brain, freq_brain = brains
    history = {"avg_amount": 100.0, "std_amount": 10.0, "recent_count": 2}
    
    results = compute_single_risk_score(amount_brain, freq_brain, 105.0, history)
    signals = results["signals"]

    assert "FrequencyHeuristic" in signals
    assert "HighAmountHeuristic" in signals

def test_risk_score_takes_max_not_mean(brains):
    amount_brain, freq_brain = brains
    
   
    history = {"avg_amount": 100.0, "std_amount": 10.0, "recent_count": 6}
    
    results = compute_single_risk_score(amount_brain, freq_brain, 105.0, history)
    
    assert results["risk"] == 1.0

def test_risk_score_bounds(brains):
    amount_brain, freq_brain = brains
    
    # Test a massive outlier
    history = {"avg_amount": 100.0, "std_amount": 10.0, "recent_count": 100}
    results = compute_single_risk_score(amount_brain, freq_brain, 50000.0, history)
    
    assert 0.0 <= results["risk"] <= 1.0