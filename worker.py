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


def process_batch(messages):
    """ run the V1 Heuristics on a smaller batvh of messages from Kafka """
    transactions_data = []
    for msg in messages:
        if msg.error():
            continue
        #decode to string then parse json
        raw_data = json.loads(msg.value().decode('utf-8'))
        transactions_data.append(raw_data)

    if not transactions_data:
        return

    try:
        internal_txs = []
        # add to Neo4j and format for the  Engine
        for tx in transactions_data:
            db.add_transaction(from_id=tx['from_account'],to_id=tx['to_account'],amount=tx['amount'],timestamp=tx['timestamp'])
            internal_txs.append(
                InternalTransaction(from_account_id=tx['from_account'],to_account_id=tx['to_account'],amount=tx['amount'],timestamp=datetime.fromtimestamp(tx['timestamp']),tx_type=tx['tx_type'],is_fraud=bool(tx.get('is_fraud', 0)))
            )

        #math same as before
        raw_features =compute_features(internal_txs)
        all_amounts = [tx.amount for tx in internal_txs]
        raw_std =float(np.std(all_amounts)) if all_amounts else 1.0
        safe_std = raw_std if raw_std > 0.0 else 1.0
        global_stats ={"mean": float(np.mean(all_amounts)) if all_amounts else 0.0, "std": safe_std}

        formatted_stats = {
            "out_timestamps":{acc: data["timestamps"] for acc, data in raw_features["node"].items()},"out_amounts": {acc: data["out_amounts"] for acc, data in raw_features["node"].items()}
            }

        heuristics_list = [
            FrequencyHeuristic(window_scale=timedelta(minutes=5), scale=10),HighAmountHeuristic(global_stats=global_stats, std_factor=2.0)
        ]

        results =compute_risk_scores(heuristics_list, formatted_stats)

    
        for account_id, score_data in results.items():
            db.update_risk_score(account_id=account_id, risk_score=score_data["risk"])

        print(f" Scored and stored micro-batch of {len(transactions_data)} transactions.")

    except Exception as e:
        import traceback
        print(f" Worker Error processing batch: {e}")
        print(traceback.format_exc())

#infinite loop
try:
    while True:
        # Ask for 100 msgs 
        msgs = consumer.consume(num_messages=100, timeout=1.0)
        if msgs is None or len(msgs) == 0:
            continue 
            
        process_batch(msgs)
except KeyboardInterrupt:
    print("Stopping worker...")
finally:
    
    consumer.close()