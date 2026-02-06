from datetime import datetime, timedelta

from heuristics.frequency import FrequencyHeuristic
from heuristics.high_amount import HighAmountHeuristic
from scoring.risk_score import compute_risk_scores



def test_risk_score_structure():
    stats = {
        "out_timestamps": {
            1: [datetime.now()]
        },
        "out_amounts": {
            1: [100]
        }
    }

    heuristics = [
        FrequencyHeuristic(window_scale=timedelta(minutes=5), scale=5),
        HighAmountHeuristic(saturation_amount=1000)
    ]

    results = compute_risk_scores(heuristics, stats)

    assert 1 in results
    assert "risk" in results[1]
    assert "signals" in results[1]



def test_risk_score_contains_all_signals():
    now = datetime.now()

    stats = {
        "out_timestamps": {
            1: [now, now + timedelta(seconds=10)]
        },
        "out_amounts": {
            1: [500]
        }
    }

    heuristics = [
        FrequencyHeuristic(window_scale=timedelta(minutes=1), scale=2),
        HighAmountHeuristic(saturation_amount=1000)
    ]

    results = compute_risk_scores(heuristics, stats)

    signals = results[1]["signals"]

    assert "FrequencyHeuristic" in signals
    assert "HighAmountHeuristic" in signals




def test_risk_score_is_mean_of_signals():
    now = datetime.now()

    stats = {
        "out_timestamps": {
            1: [now, now + timedelta(seconds=5)]
        },
        "out_amounts": {
            1: [1000]
        }
    }

    heuristics = [
        FrequencyHeuristic(window_scale=timedelta(minutes=1), scale=2),  # signal = 1.0
        HighAmountHeuristic(saturation_amount=2000)  # signal = 0.5
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
        HighAmountHeuristic(saturation_amount=1000)
    ]

    results = compute_risk_scores(heuristics, stats)

    assert results[1]["risk"] != results[2]["risk"]


def test_risk_score_bounds():
    now = datetime.now()

    stats = {
        "out_timestamps": {
            1: [now, now + timedelta(seconds=1)]
        },
        "out_amounts": {
            1: [500]
        }
    }

    heuristics = [
        FrequencyHeuristic(window_scale=timedelta(minutes=1), scale=10),
        HighAmountHeuristic(saturation_amount=1000)
    ]

    results = compute_risk_scores(heuristics, stats)

    risk = results[1]["risk"]
    assert 0.0 <= risk <= 1.0
