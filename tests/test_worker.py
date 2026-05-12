import pytest
import fakeredis
from unittest.mock import patch

#We import the exact functions we want to interrogate
from engine.worker import apply_risk_momentum

#speed layer
@pytest.fixture
def mock_redis():
    """
    Creates a completely isolated, fake Redis database in RAM for each test.
    This prevents test data from polluting actual live system.
    """
    return fakeredis.FakeRedis(decode_responses=True)



def test_permanent_lock_for_critical_threats(mock_redis):
    """
    Proves that if an account ever hits a score >= 0.85,they are permanently
    locked,regardless of how much time passes or how 'clean' their next transaction is.
    """
    account_id = "cartel_mule_001"
    current_time = 100000.0
    
    #the adversary commits a critical offense
    first_score = apply_risk_momentum(account_id, 0.88, current_time, mock_redis)
    assert first_score == 0.88
    
    #fast forward time by a massive amount
    future_time = current_time + (86400 * 730)
    
    #the adversary attempts a completely benign transaction
    second_score = apply_risk_momentum(account_id, 0.10, future_time, mock_redis)
    
    #the Ratchet must remember and enforce the permanent lock
    assert second_score == 0.88, "Vulnerability: The permanent lock failed to hold."



def test_risk_ratchet_decay_mechanics(mock_redis):
    """
    Proves the mathematical decay of a high-risk score. 
    It must not decay for the first 30 days. On day 35, it should decay by exactly 0.05.
    """
    account_id = "sleeper_cell_002"
    base_time = 1600000000.0
    
    #the account triggers a high, but non critical alert
    peak_risk = 0.75
    apply_risk_momentum(account_id, peak_risk, base_time, mock_redis)
    
    #attempt a transaction on Day 15 (Inside Probation)
    day_15_time = base_time + (86400 * 15)
    day_15_score = apply_risk_momentum(account_id, 0.10, day_15_time, mock_redis)
    assert day_15_score == 0.75, "Vulnerability: Score decayed during the 30-day probation window."
    
    #attempt a transaction on Day 35 (5 days into the decay phase)
    #decay math: 5 days * 0.01 = 0.05 reduction, Expected score is 0.70
    day_35_time = base_time + (86400 * 35)
    day_35_score = apply_risk_momentum(account_id, 0.10, day_35_time, mock_redis)
    assert round(day_35_score, 2) == 0.70, "Vulnerability: The mathematical decay rate is incorrect."



def test_new_high_water_mark_resets_probation(mock_redis):
    """
    Proves that if an account under probation commits a worse offense,
    the score increases and the probation timer is reset based on the new peak.
    """
    account_id = "escalating_threat_003"
    base_time = 100000.0
    
    #initial moderate offense
    apply_risk_momentum(account_id, 0.60, base_time, mock_redis)
    
    #on Day 20, they commit a significantly worse offense
    day_20_time = base_time + (86400 * 20)
    escalated_score = apply_risk_momentum(account_id, 0.80, day_20_time, mock_redis)
    assert escalated_score == 0.80
    
    #check the Redis shadow to ensure the high-water mark and timestamp updated
    shadow = mock_redis.hgetall(f"risk_shadow:{account_id}")
    assert float(shadow["max_score"]) == 0.80
    assert float(shadow["last_flag_time"]) == day_20_time, "Vulnerability: Probation clock did not reset."



@patch('engine.worker.redis_client') 
def test_update_multi_window_velocity(mock_live_redis, mock_redis):
    """
    Intercepts the live redis_client in worker.py and replaces it with our fakeredis.
    Proves that the 3D matrix correctly tallies transaction counts and amounts.
    """
    #force the worker to use our fake RAM database
    import engine.worker
    engine.worker.redis_client = mock_redis 
    
    account_id = "volume_tester_004"
    
    #inject 3 separate $500 outbound transactions
    for _ in range(3):
        profile = engine.worker.update_multi_window_velocity(account_id, 500.0, "out")
        
    #verify the 24h window captured all 3 events and the total volume
    assert profile["24h"]["out_count"] == 3
    assert profile["24h"]["total_out"] == 1500.0
    
    #verify the 30-day window matches, as the events occurred simultaneously
    assert profile["30d"]["out_count"] == 3
    assert profile["30d"]["total_out"] == 1500.0