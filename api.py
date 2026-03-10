


import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from confluent_kafka import Producer

app = FastAPI(title="Graph Risk Engine API - The Gateway",description="V2: A real-time data ingestion gateway pushing to Kafka",version="2.0.0")

#KAFKA prod config 
producer_config = {
    'bootstrap.servers': 'kafka:29092',
    'client.id': 'fastapi-gateway',
    'acks': '1'
}

try:
    producer = Producer(producer_config)
    print("Kafka Producer initialized successfully")
except Exception as e:
    print(f" Failed to initialize Kafka Producer : {e}")

def delivery_report(err, msg):
    """ Callback triggered by Kafka once the message is safely stored on the 'tablet'. """
    if err is not None:
        print(f" Message delivery failed: {err}")
    else:  
        print(f" Transaction queued to topic [{msg.topic()}]")


#PYDANTIC MODELS
class TransactionInput(BaseModel):
    from_account: str
    to_account: str
    amount: float
    timestamp: float
    tx_type: str
    is_fraud: int = 0


@app.get("/")
def health_check():
    """Simple check to see if the gateway is alive"""
    return {"status": "healthy", "service": "Graph Risk Engine Gateway"}


#THE  ENDPOINT ---
@app.post("/api/v1/score-batch")
def score_transaction_batch(transactions: List[TransactionInput]):
    try:
        for tx in transactions:
            tx_json = json.dumps(tx.model_dump())
            producer.produce(topic='incoming-transactions',value=tx_json.encode('utf-8'),callback=delivery_report)
            producer.poll(0)
        producer.flush()
        return {"status": "queued","message": f"Successfully pushed {len(transactions)} transactions to the Kafka stream.","queued_count": len(transactions)}

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Kafka Producer Error: {str(e)}")