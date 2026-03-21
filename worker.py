import json
import time
from confluent_kafka import Consumer
import numpy as np

from heuristics.frequency import FrequencyHeuristic
from heuristics.high_amount import HighAmountHeuristic
from database import db
from scoring.risk_score import compute_single_risk_score
import redis
import os

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


consumer_config = {
    'bootstrap.servers': 'localhost:9092',  
    'group.id': 'the-mac-worker-v1',   
    'auto.offset.reset': 'earliest'        
}
consumer = Consumer(consumer_config)
consumer.subscribe(['incoming-transactions'])


amount_brain = HighAmountHeuristic(std_threshold=3.0)
freq_brain = FrequencyHeuristic(max_tx_per_hour=5)

def get_optimized_threshold():
    try:
        # Ask Redis for the number Julia pushed
        val = redis_client.get("config:std_threshold")
        if val:
            return float(val)
    except Exception:
        pass
    return 3.0

def process_batch(messages):
    transactions_data = [json.loads(m.value().decode('utf-8')) for m in messages if not m.error()]

    current_threshold = get_optimized_threshold()
    amount_brain.std_threshold = current_threshold
    
    for tx in transactions_data:
        account_id =tx['from_account']
        current_amount = tx['amount']
        current_time =tx['timestamp']
        
        #ask cache directly first 
        history =get_cached_account_history(account_id, current_time)
        amount_risk = amount_brain.evaluate(current_amount, history)
        freq_risk = freq_brain.evaluate(history)
        risk_results =compute_single_risk_score(amount_brain, freq_brain, current_amount, history)
        final_risk =risk_results['risk'] 
        
        #update Neo4j
        db.update_risk_score(account_id, final_risk)
        db.add_transaction(account_id, tx['to_account'],current_amount, current_time)

        print(f"Scored {account_id} | Risk: {final_risk:.2f} | (AmtRisk: {amount_risk:.2f}, FreqRisk: {freq_risk:.2f})")

#The loop
try:
    while True:
        msgs = consumer.consume(num_messages=100, timeout=1.0)
        if msgs is None or len(msgs) == 0:
            continue 
        process_batch(msgs)
except KeyboardInterrupt:
    print(" Stopping worker..")
finally:
    consumer.close()