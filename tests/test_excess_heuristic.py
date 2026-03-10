import pytest
from heuristics.high_amount import HighAmountHeuristic

def test_high_amount_above_threshold():
    
    heuristic = HighAmountHeuristic(std_threshold=3.0)
    
    history = {"avg_amount": 100.0, "std_amount": 10.0, "recent_count": 5}
    
   
    score = heuristic.evaluate(200.0, history)
    assert score == 1.0

def test_high_amount_below_mean():
    heuristic = HighAmountHeuristic(std_threshold=3.0)
    history = {"avg_amount": 100.0,"std_amount": 10.0, "recent_count": 5}
    
    score = heuristic.evaluate(105.0, history)
    assert score <= 0.2


def test_high_amount_suspicious_middle():
    """Test the linear scaling when z-score is between 1.0 and the threshold."""
    heuristic = HighAmountHeuristic(std_threshold=3.0)
    history = {"avg_amount": 100.0, "std_amount": 10.0, "recent_count": 5}
    
    score = heuristic.evaluate(120.0, history)
    
    assert 0.6 < score < 0.7 

def test_high_amount_exactly_at_threshold():
    """Test the exact boundary condition."""
    heuristic = HighAmountHeuristic(std_threshold=3.0)
    history = {"avg_amount": 100.0, "std_amount": 10.0, "recent_count": 5}
    
    score = heuristic.evaluate(130.0, history)
    
    assert score == 0.9 

def test_high_amount_zero_std_protection():
    """Prove the engine doesn't crash with a ZeroDivisionError if history is identical."""
    heuristic = HighAmountHeuristic(std_threshold=3.0)
    history = {"avg_amount": 50.0, "std_amount": 0.0, "recent_count": 5}
    
   
    score = heuristic.evaluate(53.0, history)
    
    assert score == 0.9 

def test_high_amount_under_spender():
    """Prove that spending WAY less than usual doesn't trigger fraud."""
    heuristic = HighAmountHeuristic(std_threshold=3.0)
    history = {"avg_amount": 1000.0, "std_amount": 100.0, "recent_count": 5}
    
    score = heuristic.evaluate(2.0, history)
    
    assert score == 0.1 








