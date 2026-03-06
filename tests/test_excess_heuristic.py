from heuristics.high_amount import HighAmountHeuristic



def make_heuristic(mean=100.0, std=20.0, std_factor=2.0):
    global_stats = {"mean": mean, "std": std}
    return HighAmountHeuristic(global_stats, std_factor=std_factor)

def test_high_amount_no_transactions():
    stats = {
        "out_amounts": {}
    }
    heuristic = make_heuristic()
    score = heuristic.evaluate(account_id=1, stats=stats)
    assert score == 0.0

def test_high_amount_below_mean():
    stats = {
        "out_amounts": {
            1: [50]
        }
    }
    heuristic = make_heuristic()
    score = heuristic.evaluate(account_id=1, stats=stats)
    assert score == 0.0

def test_high_amount_at_threshold():
    stats = {
        "out_amounts": {
            1: [140]  # mean + 2*std = 100 + 2*20 = 140
        }
    }
    heuristic = make_heuristic()
    score = heuristic.evaluate(account_id=1, stats=stats)
    assert score == 1.0

def test_high_amount_above_threshold():
    stats = {
        "out_amounts": {
            1: [200]
        }
    }
    heuristic = make_heuristic()
    score = heuristic.evaluate(account_id=1, stats=stats)
    assert score == 1.0

def test_high_amount_between_mean_and_threshold():
    stats = {
        "out_amounts": {
            1: [120]  # between mean (100) and threshold (140)
        }
    }
    heuristic = make_heuristic()
    score = heuristic.evaluate(account_id=1, stats=stats)
    assert 0.0 < score < 1.0

def test_high_amount_score_bounds():
    stats = {
        "out_amounts": {
            1: [1, 10, 100]
        }
    }
    heuristic = make_heuristic()
    score = heuristic.evaluate(account_id=1, stats=stats)
    assert 0.0 <= score <= 1.0







