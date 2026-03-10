import json
import time
from confluent_kafka import Consumer, KafkaError
import numpy as np
from datetime import datetime, timedelta

from graph.build_graph import build_transaction_graph
from scoring.risk_score import compute_risk_scores
from heuristics.frequency import FrequencyHeuristic
from heuristics.high_amount import HighAmountHeuristic
from data.transaction import Transaction as InternalTransaction
from preprocessing.transaction_stats import compute_features
from database import db
from scoring.risk_score import compute_single_risk_score


print(" Activating Engine worker..")

# KAFKA CONSUMER SETUP
consumer_config = {
    'bootstrap.servers': 'kafka:29092',
    'group.id':'fraud-scoring-group', #group ID
    'auto.offset.reset': 'earliest'     #start from oldest unread message if crash
}
consumer = Consumer(consumer_config)

consumer.subscribe(['incoming-transactions'])
print("listening to topic [incoming-transactions]...")


amount_brain = HighAmountHeuristic(std_threshold=3.0)
freq_brain = FrequencyHeuristic(max_tx_per_hour=5)

def process_batch(messages):
    transactions_data = [json.loads(m.value().decode('utf-8')) for m in messages if not m.error()]
    
    for tx in transactions_data:
        account_id = tx['from_account']
        current_amount = tx['amount']
        current_time = tx['timestamp']

        #read first to prevent fraudsters slipping under the radar 
        history = db.get_account_history(account_id, current_time)
        amount_risk = amount_brain.evaluate(current_amount, history)
        freq_risk =freq_brain.evaluate(history)
        final_risk = compute_single_risk_score(amount_brain, freq_brain, current_amount, history)
        db.update_risk_score(account_id, final_risk)
        db.add_transaction(account_id,tx['to_account'], current_amount, current_time)

        print(f" Scored {account_id} |Risk: {final_risk:.2f} |(AmtRisk: {amount_risk:.2f}, FreqRisk:{freq_risk:.2f})")

#the loop
try:
    while True:
        msgs = consumer.consume(num_messages=100, timeout=1.0)
        if msgs is None or len(msgs) == 0:
            continue 
        process_batch(msgs)
except KeyboardInterrupt:
    print("Stopping worker")
finally:
    consumer.close()