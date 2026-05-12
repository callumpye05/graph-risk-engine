import json
import time
from kafka import KafkaProducer
from simulation.data.master_generator import run_simulation

#Initialize kafka
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

TOPIC_NAME ="incoming-transactions"

def execute_chaos_pipeline():
    print("Initiating Data Engine ")
    raw_dataset = run_simulation(days=1)
    
    #secure the truth
    truth_file = "v2_ground_truth.json"
    with open(truth_file, "w") as f:
        json.dump(raw_dataset, f, indent=4)
    print(f" Ground Truth secured in {truth_file}. (Total: {len(raw_dataset)} records)")
    
    print("\n Initiating Live Stream to Kafka")
    
    #sanitize and stream
    for tx in raw_dataset:
        #create a copy of the transaction so we don't destroylocal data
        sanitized_tx = tx.copy()
        
        #rip the label out
        if "is_fraud" in sanitized_tx:
            del sanitized_tx["is_fraud"]
            
        producer.send(TOPIC_NAME, sanitized_tx)
        
        #micro-sleep to simulate realtime 
        time.sleep(0.01) 
        
    producer.flush()
    print("All transactions deployed to the network, the board is live.")

if __name__ == "__main__":
    execute_chaos_pipeline()