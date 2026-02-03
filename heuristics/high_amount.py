from heuristics.base import Heuristic 

class HighAmountHeuristic(Heuristic):
    def __init__(self, saturation_amount: float):
        self._saturation_amount = saturation_amount

    
    def evaluate(self, account_id, stats) -> float:
        amounts = stats["out_amounts"].get(account_id, [])
        if not amounts:
            return 0.0

        largest_amount = max(amounts)
        return min(1.0, largest_amount / self._saturation_amount)



    

