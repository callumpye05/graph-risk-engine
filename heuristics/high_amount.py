from heuristics.base import Heuristic 

class HighAmountHeuristic(Heuristic):
    def __init__(self, global_stats, std_factor=3.0):
        #global_stats: dict with global mean and std for out_amounts
        self.global_mean = global_stats["mean"]
        self.global_std = global_stats["std"]
        self.std_factor = std_factor

    def evaluate(self, account_id, stats) -> float:
        amounts = stats["out_amounts"].get(account_id, [])
        if not amounts:
            return 0.0

        largest_amount = max(amounts)
        threshold = self.global_mean + self.std_factor * self.global_std
        if threshold == 0:
            return 0.0
        score = (largest_amount - self.global_mean) / (self.std_factor * self.global_std)
        return min(1.0, max(0.0, score))

    

