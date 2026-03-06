from datetime import datetime, timedelta
from heuristics.frequency import FrequencyHeuristic
from heuristics.high_amount import HighAmountHeuristic
from scoring.risk_score import compute_risk_scores

# Helper for mock global stats to keep tests clean
MOCK_GLOBAL_STATS = {"mean": 500.0, "std": 100.0}

def test_risk_score_structure():
    stats = {
        "out_timestamps": {1: [datetime.now()]},
        "out_amounts": {1: [100]}
    }

    heuristics = [
        FrequencyHeuristic(window_scale=timedelta(minutes=5), scale=5),
        # Updated to use global_stats
        HighAmountHeuristic(global_stats=MOCK_GLOBAL_STATS, std_factor=3.0)
    ]

    results = compute_risk_scores(heuristics, stats)

    assert 1 in results
    assert "risk" in results[1]
    assert "signals" in results[1]

def test_risk_score_contains_all_signals():
    now = datetime.now()
    stats = {
        "out_timestamps": {1: [now, now + timedelta(seconds=10)]},
        "out_amounts": {1: [500]}
    }

    heuristics = [
        FrequencyHeuristic(window_scale=timedelta(minutes=1), scale=2),
        HighAmountHeuristic(global_stats=MOCK_GLOBAL_STATS)
    ]

    results = compute_risk_scores(heuristics, stats)
    signals = results[1]["signals"]

    assert "FrequencyHeuristic" in signals
    assert "HighAmountHeuristic" in signals

def test_risk_score_is_mean_of_signals():
    now = datetime.now()
    # Mocking stats so Frequency = 1.0 and HighAmount = 0.5
    # HighAmount Score calculation: (amount - mean) / (std_factor * std)
    # With mean=500, std=100, std_factor=2: (600 - 500) / (2 * 100) = 0.5
    stats = {
        "out_timestamps": {1: [now, now + timedelta(seconds=5)]},
        "out_amounts": {1: [600]}
    }

    heuristics = [
        FrequencyHeuristic(window_scale=timedelta(minutes=1), scale=2), # signal = 1.0
        HighAmountHeuristic(global_stats=MOCK_GLOBAL_STATS, std_factor=2.0) # signal = 0.5
    ]

    results = compute_risk_scores(heuristics, stats)
    risk = results[1]["risk"]
    expected = (1.0 + 0.5) / 2

    assert risk == expected

def test_risk_score_multiple_accounts():
    now = datetime.now()
    stats = {
        "out_timestamps": {
            1: [now, now + timedelta(seconds=5)],
            2: [now]
        },
        "out_amounts": {
            1: [1000],
            2: [10]
        }
    }

    heuristics = [
        FrequencyHeuristic(window_scale=timedelta(minutes=1), scale=2),
        HighAmountHeuristic(global_stats=MOCK_GLOBAL_STATS)
    ]

    results = compute_risk_scores(heuristics, stats)
    assert results[1]["risk"] != results[2]["risk"]

def test_risk_score_bounds():
    now = datetime.now()
    stats = {
        "out_timestamps": {1: [now, now + timedelta(seconds=1)]},
        "out_amounts": {1: [50000]} # Very high amount to test upper bound
    }

    heuristics = [
        FrequencyHeuristic(window_scale=timedelta(minutes=1), scale=10),
        HighAmountHeuristic(global_stats=MOCK_GLOBAL_STATS)
    ]

    results = compute_risk_scores(heuristics, stats)
    risk = results[1]["risk"]
    assert 0.0 <= risk <= 1.0