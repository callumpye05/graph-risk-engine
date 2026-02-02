from heuristics.base import Heuristic 
from datetime import datetime,timedelta


class FrequencyHeuristic(Heuristic) : 
    
    def __init__(self , window_scale , scale) :
        self._window_scale = window_scale
        self._scale = scale
    

    def evaluate(self , account_id , stats) -> float : 
        timestamps = stats["out_timestamps"].get(account_id ,[])
        sorted_timestamps = sorted(timestamps)
        i = 0
        max_burst_size = 0 

        if len(timestamps) < 2:
            return 0.0

        for j in range(len(sorted_timestamps)):
            while i <= j and(sorted_timestamps[j] - sorted_timestamps[i])> self._window_scale:
                i = i+1 
                
            current_burst = j - i+1 
            max_burst_size = max(current_burst , max_burst_size)
        
        signal= min(1.0, max_burst_size /self._scale)
        return signal
         






