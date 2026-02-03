from heuristics.high_amount import HighAmountHeuristic


def test_high_amount_no_transactions():
    stats = {
        "out_amounts": {}
    }

    heuristic = HighAmountHeuristic(saturation_amount=1000)

    score = heuristic.evaluate(account_id=1, stats=stats)
    assert score == 0.0




def test_high_amount_small_value():
    stats = {
        "out_amounts": {
            1: [100]
        }
    }

    heuristic = HighAmountHeuristic(saturation_amount=1000)

    score = heuristic.evaluate(account_id=1, stats=stats)
    assert score == 0.1



def test_high_amount_uses_largest_transaction():
    stats = {
        "out_amounts": {
            1: [100, 300, 700]
        }
    }

    heuristic = HighAmountHeuristic(saturation_amount=1000)

    score = heuristic.evaluate(account_id=1, stats=stats)
    assert score == 0.7


def test_high_amount_saturates():
    stats = {
        "out_amounts": {
            1: [5000]
        }
    }

    heuristic = HighAmountHeuristic(saturation_amount=1000)

    score = heuristic.evaluate(account_id=1, stats=stats)
    assert score == 1.0



def test_high_amount_score_bounds():
    stats = {
        "out_amounts": {
            1: [1, 10, 100]
        }
    }

    heuristic = HighAmountHeuristic(saturation_amount=50)

    score = heuristic.evaluate(account_id=1, stats=stats)
    assert 0.0 <= score <= 1.0








