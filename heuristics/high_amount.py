from heuristics.base import Heuristic 

class HighAmountHeuristic:
    def __init__(self, std_threshold=3.0):
        self.std_threshold = std_threshold

    def evaluate(self, current_amount: float, history: dict) -> float:
        avg = history['avg_amount']
        std = history['std_amount']
        
        if std == 0.0: std = 1.0 # Math safety
            
        z_score = (current_amount - avg) / std
        
        if z_score > self.std_threshold:
            return 1.0
        elif z_score > 1.0:
            return min(z_score / self.std_threshold, 0.9)
        return 0.1

