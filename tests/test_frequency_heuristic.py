from datetime import datetime, timedelta
from heuristics.frequency import FrequencyHeuristic
from preprocessing.transaction_stats import computeData




def make_timestamps(start, offsets_seconds):
    return[start + timedelta(seconds=o) for o in offsets_seconds]

def test_frequency_no_transactions():
    stats = {"out_timestamps": {}}
    heuristic = FrequencyHeuristic(window_scale=timedelta(minutes=5),scale=5)
    score = heuristic.evaluate(account_id=1, stats=stats)
    assert score == 0.0



def test_frequency_sparse_activity():
    now = datetime.now()
    stats = {"out_timestamps": {1: make_timestamps(now, [0, 600, 1200])}}
    heuristic = FrequencyHeuristic(window_scale=timedelta(minutes=5),scale=5)

    score = heuristic.evaluate(account_id=1, stats=stats)
    assert 0.0 < score < 1.0


def test_frequency_burst_detected():
    now = datetime.now()
    stats ={"out_timestamps": {1: make_timestamps(now, [0, 10, 20, 30, 40])}}

    heuristic = FrequencyHeuristic(window_scale=timedelta(minutes=2),scale=5)
    score = heuristic.evaluate(account_id=1, stats=stats)
    assert score == 1.0



def test_frequency_saturates():
    now = datetime.now()

    stats = {"out_timestamps": {1: make_timestamps(now, [0, 5, 10, 15, 20, 25, 30])}}
    heuristic = FrequencyHeuristic(window_scale=timedelta(minutes=1),scale=3)
    score = heuristic.evaluate(account_id=1, stats=stats)
    assert score == 1.0




def test_frequency_score_bounds():
    now = datetime.now()
    stats={"out_timestamps": {1: make_timestamps(now, [0, 1, 2])}}

    heuristic = FrequencyHeuristic(window_scale=timedelta(minutes=1),scale=10)
    score = heuristic.evaluate(account_id=1, stats=stats)
    assert 0.0 <= score <= 1.0




