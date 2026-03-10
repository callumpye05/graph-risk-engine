from heuristics.base import Heuristic 
from datetime import datetime,timedelta


class FrequencyHeuristic:
    def __init__(self, max_tx_per_hour=5):
        self.max_tx = max_tx_per_hour

    def evaluate(self, history: dict) -> float:
        
        current_burst = history['recent_count'] + 1
        
        if current_burst > self.max_tx:
            return 1.0 # immediate red flg
        
        #scale the risk based on how close they are to the limit
        return min(current_burst / self.max_tx, 0.8)






