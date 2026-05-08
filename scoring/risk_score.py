def synthesize_risk_profile(matrix_results: dict) -> dict:
    """
    translates the raw mathematical risk into a human readable intelligence profile
    """
    raw_risk = matrix_results.get("risk", 0.0)
    
    #threat labelling
    if raw_risk >= 0.85:
        threat_level = "CRITICAL"
        action = "FREEZE"
    elif raw_risk >= 0.60:
        threat_level = "SEVERE"
        action = "MANUAL_REVIEW"
    elif raw_risk >= 0.30:
        threat_level = "ELEVATED"
        action = "MONITOR"
    else:
        threat_level = "SAFE"
        action = "ALLOW"

    #Construct profile for the UI
    profile = {
        "final_risk": raw_risk,
        "threat_level": threat_level,
        "recommended_action": action,
        #xe pass through the specific component scores so the human analyst 
        #knows exactly why the alarm is ringing.
        "components": {
            "spike_score": matrix_results.get("spike_score", 0.0),
            "pass_through_score": matrix_results.get("pass_through_score", 0.0),
            "volume_score": matrix_results.get("volume_score", 0.0)
        }
    }
    
    return profile