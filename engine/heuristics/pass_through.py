class VelocityMatrixHeuristic:
    """
    evaluates risk using an additive, multi dimensional matrix
    weighs pass through velocity, sleeper cell spikes, and outright volume
    """
    def __init__(self, spike_threshold: float = 5.0, pass_through_threshold: float = 0.85):
        self.spike_threshold = spike_threshold
        self.pass_through_threshold = pass_through_threshold

    def evaluate(self, velocity_profile: dict) -> dict:
        #safety checks
        if not velocity_profile or "24h" not in velocity_profile:
            return {"risk": 0.0, "reason": "insufficient_data"}

        v_24h= velocity_profile["24h"]
        v_30d = velocity_profile.get("30d", {"total_in": 0,"total_out": 0})

        #Sleeper Cell spike (max 0.40)
        spike_risk =0.0
        
        #isolate the pure 29 day history to prevent the current burst from damaging the baseline
        pure_29d_out =max(0, v_30d["total_out"] - v_24h["total_out"])
        
        #We enforce a $50 minimum floor to prevent dividing by zero or 
        #triggering massive multipliers on accounts that usually spend $1
        daily_avg = max(50.0,pure_29d_out / 29.0)
        
        if v_24h["total_out"] > daily_avg:
            #calculate how many times over they exceeded the average
            multiplier = v_24h["total_out"] / daily_avg
            
            if multiplier >= self.spike_threshold:
                #proportional scaling: thehigher the multiplier, the closer it gets to the 0.40 cap
                #a 5x spike gives a partial score, a 20x spike maxes out the score
                scaling_factor = min(1.0, (multiplier - self.spike_threshold) / 15.0) 
                spike_risk = 0.15 + (0.25 * scaling_factor) # Base tilt of 0.15, maxes at 0.40

        #Pass Through Signature (max 0.45) 
        pass_through_risk = 0.0
        
        if v_24h["total_in"] > 0:
            ratio = v_24h["total_out"] / v_24h["total_in"]
            
            #They are spending exactly what they receive
            if ratio >= self.pass_through_threshold and ratio <= 1.05:
                #scale the risk based on how close they are to a perfect 1.0 ratio
                closeness = 1.0 - abs(1.0 - ratio) 
                pass_through_risk = 0.45 * closeness

        #Volume Weight (max 0.15)
        #99% pass through on $10 is nothing , but fir  $10,000  it is much worse
        volume_risk = 0.0
        if v_24h["total_out"] > 5000:
            volume_risk = min(0.15,(v_24h["total_out"] - 5000) / 20000 * 0.15)

        #final synthesis
        total_risk = min(1.0,spike_risk + pass_through_risk +volume_risk)

        return {
            "risk": round(total_risk, 3),
            "spike_score": round(spike_risk, 3),
            "pass_through_score": round(pass_through_risk, 3),
            "volume_score": round(volume_risk, 3)
        }