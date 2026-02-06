from heuristics.frequency import FrequencyHeuristic
from heuristics.high_amount import HighAmountHeuristic


def compute_risk_scores(heuristics , stats ) -> dict : 
    accounts = stats["out_timestamps"].keys()
    results = {}
    
    for acc in accounts :

        signals= {}
        for heuristic in heuristics : 
            signal = heuristic.evaluate(acc,stats)
            signals[heuristic.__class__.__name__] = signal 
        
        if signals : 
            risk = sum(signals.values()) / len(signals)
        else : 
            risk = 0.0
        results[acc] = {
            "risk": risk,
            "signals": signals
        }
    
    return results
 

            




