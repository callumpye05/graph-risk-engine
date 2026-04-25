from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from confluent_kafka import Producer
import asyncio
import json
import os
import redis.asyncio as aioredis

app = FastAPI()

# 🛡️ The CORS Shield (Allows React to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 The Nervous System Connections
# Using getenv so it works locally OR inside Docker
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

redis_async = aioredis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

# Set up Kafka Producer for the incoming data
producer_config = {'bootstrap.servers': KAFKA_BOOTSTRAP}
producer = Producer(producer_config)

# --- DATA MODELS ---
class Transaction(BaseModel):
    from_account: str
    to_account: str
    amount: float
    timestamp: float
    tx_type: str
    is_fraud: int = 0

# --- ROUTE 1: INGESTION (The Front Door for 'Feed the Machine') ---
@app.post("/api/v1/score-batch")
async def score_batch(transactions: List[Transaction]):
    for tx in transactions:
        tx_dict = tx.model_dump()
        producer.produce(
            'incoming-transactions', 
            key=tx_dict['from_account'], 
            value=json.dumps(tx_dict)
        )
    producer.flush()
    return {"status": "success", "message": f"Injected {len(transactions)} transactions to Kafka"}


# --- ROUTE 2: BROADCAST (The Transmission Tower for React) ---
@app.websocket("/ws/pulse")
async def websocket_pulse(websocket: WebSocket):
    await websocket.accept()
    print("UI Connected to Live Pulse.") # Console verification
    
    pubsub = redis_async.pubsub()
    await pubsub.subscribe("live_transactions")
    
    try:
        while True:
            # Listen to messages on the channel
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message is not None:
                await websocket.send_text(message["data"])
            await asyncio.sleep(0.01)
            
    except WebSocketDisconnect:
        print("UI Disconnected from Live Pulse.")
    finally:
        await pubsub.unsubscribe("live_transactions")