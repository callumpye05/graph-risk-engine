def compute_single_risk_score(amount_brain, freq_brain, current_amount: float, history: dict) -> dict:
    """
    Takes the max risk score (loudest alarm wins).
    """
    amount_risk = amount_brain.evaluate(current_amount, history)
    freq_risk = freq_brain.evaluate(history)
    
    signals = {
        "HighAmountHeuristic": amount_risk,
        "FrequencyHeuristic": freq_risk
    }
    
    # choose the biggest of the two ,  any suspicious behaviour should be flagged
    final_risk = max(signals.values())
    
    return {
        "risk": final_risk,
        "signals": signals
    }

            




