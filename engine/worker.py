import json
import time
from confluent_kafka import Consumer
from engine.heuristics.pass_through import VelocityMatrixHeuristic
from engine.scoring.risk_score import synthesize_risk_profile
from shared.database import db
import redis
import os
import subprocess

#learning variables
LEARNING_BATCH_SIZE = 3110

print(" Activating Engine worker..")

#speed layer
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"), 
    port=int(os.getenv("REDIS_PORT", 6379)), 
    db=0, 
    decode_responses=True 
)

def get_cached_account_history(account_id: str, current_timestamp: float):
    cache_key = f"fraud_history:{account_id}"
    start_time = time.perf_counter()#start timer
    
    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            elapsed =(time.perf_counter() -start_time) *1000
            print(f" CACHE HIT  | {account_id} | {elapsed:.2f} ms")
            return json.loads(cached_data)
    except redis.RedisError as e:
        pass
        
    #cache miss
    history =db.get_account_history(account_id,current_timestamp)
    elapsed = (time.perf_counter() - start_time)*1000
    print(f"CACHE MISS | {account_id} | {elapsed:.2f} ms (Neo4j Load)")
    try:
        redis_client.set(cache_key, json.dumps(history), ex=300)
    except redis.RedisError:
        pass
    return history




velocity_brain = VelocityMatrixHeuristic(spike_threshold=8.0)

def get_optimized_threshold():
    try:
        #ask redis number julia pushed
        val = redis_client.get("config:std_threshold")
        if val:
            return float(val)
    except Exception:
        pass
    return 3.0

def update_multi_window_velocity(account_id: str, amount: float, direction: str) -> dict:
    """
    maintains a 3d time decayed ledger of account velocity(1d, one week, one month)
    direction must be 'in' or 'out'
    """
    pipe =redis_client.pipeline()
    
    #time of windows, essentially a tracking period for our data
    windows ={
        "24h": 86400,
        "7d": 604800,
        "30d":2592000
    }
    
    #queue the atomic commands
    for window_name, ttl_seconds in windows.items():
        key= f"velocity:{window_name}:{account_id}"
        
        #increment counts and totals
        pipe.hincrby(key, f"{direction}_count", 1)
        #redis returns it as bytes so we add the exact amount
        pipe.hincrbyfloat(key, f"total_{direction}", amount)
        
        #timer
        # nx=True ensures the timer is only set upon the creation of the window
        #we prevent extesnion from micro-transactions
        pipe.expire(key, ttl_seconds,nx=True) 
        
        # Fetch the updated state for this window
        pipe.hgetall(key)
        
    #execute the entire payload instantly
    results = pipe.execute()
    
    #parse the results into a multi-dimensional dictionary
    velocity_profile = {}
    
    #in the loop we hqd queued 4 commands per window. 
    for i, window_name in enumerate(windows.keys()):
        state = results[(i * 4) +3]
        velocity_profile[window_name] = {
            "in_count": int(state.get("in_count", 0)),
            "out_count": int(state.get("out_count",0)),
            "total_in":float(state.get("total_in", 0.0)),
            "total_out": float(state.get("total_out", 0.0))
        }
        
    return velocity_profile

def process_batch(messages):
    

    transactions_data =[json.loads(m.value().decode('utf-8')) for m in messages if not m.error()]

    #get info from optimizer first 
    current_threshold =get_optimized_threshold()
    velocity_brain.spike_threshold = max(2.0, current_threshold)
    
    for tx in transactions_data:
        account_id = tx['from_account']
        receiver_id = tx['to_account']
        current_amount =tx['amount']
        current_time = tx['timestamp']
        is_fraud = tx.get('is_fraud' , 0)

        sender_velocity = update_multi_window_velocity(account_id, current_amount, "out")
        receiver_velocity = update_multi_window_velocity(receiver_id, current_amount, "in")
        matrix_results = velocity_brain.evaluate(sender_velocity)
        raw_risk = matrix_results["risk"]

        final_risk =apply_risk_momentum(account_id, raw_risk, current_time, redis_client)
        matrix_results["risk"] = final_risk
        profile = synthesize_risk_profile(matrix_results)
        
        db.update_risk_score(account_id,final_risk)
        db.add_transaction(account_id, tx['to_account'], current_amount,current_time , is_fraud)


        live_result = {
            "account_id": account_id,
            "to_account": tx['to_account'],
            "amount": current_amount,
            "risk": final_risk,
            "threat_level": profile["threat_level"],
            "recommended_action": profile["recommended_action"],
            "timestamp": current_time,
            "spike_score": profile["components"]["spike_score"],
            "pass_through_score": profile["components"]["pass_through_score"],
            "is_fraud_label": is_fraud
        }
        try:
            redis_client.publish("live_transactions",json.dumps(live_result))
        except Exception as e:
            pass

        print(f"Scored {account_id} | Risk: {final_risk:.2f} [{profile['threat_level']}] | Pass-Through: {profile['components']['pass_through_score']:.2f}")

    current_count = redis_client.incrby("engine:tx_count", len(transactions_data))
    
    #new data means new calculatons for optimization
    if current_count >= LEARNING_BATCH_SIZE:
        print(f"\n {LEARNING_BATCH_SIZE} entries reached, let Neo4j finish writing")
        time.sleep(2)
        try:
            print("Launching Optimizer.")
            subprocess.run("python -m simulation.extract_data",shell=True)
            subprocess.run("docker exec fraud-optimizer julia or_optimization/optimize.jl", shell=True)
        except Exception as e:
            print(f"Failed to trigger optimizer: {e}")
            
        #reset for next learning cycle 
        redis_client.set("engine:tx_count", 0)
        print("Optimizer completed, counter reset.")

def apply_risk_momentum(account_id: str, current_matrix_risk: float, current_timestamp: float, redis_client) -> float:
    """
    Enforces a locking system : permanent locks for criticals, 30-day probation, and slow decay.
    """
    key = f"risk_shadow:{account_id}"
    
    #fetch the accounts historical risk profile
    shadow = redis_client.hgetall(key)
    
    historical_max =float(shadow.get("max_score", 0.0))
    last_flag_time= float(shadow.get("last_flag_time", 0.0))
    
    # permanent lock for criticals
    if historical_max >= 0.85:
        #a human must manually delete this key in Redis/Neo4j to free them
        return historical_max

    #new high water mark
    if current_matrix_risk >= historical_max:
        #the account has hit a new high water mark, update the shadow and reset the probation clock
        redis_client.hset(key, "max_score", current_matrix_risk)
        redis_client.hset(key, "last_flag_time", current_timestamp)
        return current_matrix_risk

    #shadow enforcement 
    #if the current transaction is clean, we evaluate their shadow
    seconds_since_flag = current_timestamp - last_flag_time
    days_since_flag = seconds_since_flag /86400.0

    if days_since_flag <=30.0:
        #still not convicning enough
        return historical_max
    else:
        #month 3+ we can begin slowly dropping the score
        decay_amount = (days_since_flag - 30.0) * 0.01
        decayed_score = max(0.0, historical_max - decay_amount)
        
        #if the decayed score drops below their current baseline risk,  the current risk wins
        final_score = max(current_matrix_risk, decayed_score)
        
        #update their newly decayed max score so we don't recalculate from the original peak
        redis_client.hset(key, "max_score", final_score)
        #we don't update the flag time, so the decay continues smoothly on the next transaction
        return final_score

#loop
if __name__ == "__main__":
    
    consumer_config = {
        'bootstrap.servers': 'localhost:9092',  
        'group.id': 'the-mac-worker-v1',   
        'auto.offset.reset': 'earliest'        
    }
    consumer = Consumer(consumer_config)
    consumer.subscribe(['incoming-transactions'])

    try:
        print("worker is live, listening for transactions and ready to learn")
        while True:
            msgs = consumer.consume(num_messages=100, timeout=1.0)
            if msgs is None or len(msgs) == 0:
                continue 
            process_batch(msgs)
    except KeyboardInterrupt:
        print("Halting")
    finally:
        consumer.close()