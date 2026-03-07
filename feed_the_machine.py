import random
import time
import requests




API_URL = "http://localhost:8000/api/v1/score-batch"

NUM_TRANSACTIONS = 1000
print("Generating synthetic transaction data")

transactions = []
base_time = 1709751600.0

for i in range(NUM_TRANSACTIONS):
    sender =f"ACC_USER_{random.randint(1,200)}"
    receiver = f"ACC_USER_{random.randint(1, 200)}"
    
    while receiver == sender:
        receiver =f"ACC_USER_{random.randint(1, 200)}"

    tx = {"from_account":sender,"to_account": receiver,"amount": round(random.uniform(10.0, 500.0), 2), "timestamp": base_time + (i * 3600),"tx_type": "TRANSFER","is_fraud": 0}
    transactions.append(tx)

fraud_accounts = ["ACC_DIRTY_1", "ACC_DIRTY_2","ACC_DIRTY_3", "ACC_DIRTY_4", "ACC_DIRTY_5"]
for i in range(5):
    tx = {"from_account": fraud_accounts[i], "to_account": fraud_accounts[(i + 1) % 5],"amount": 9900.0, "timestamp": base_time + (NUM_TRANSACTIONS * 3600) + (i * 10), "tx_type": "TRANSFER","is_fraud": 1}
    transactions.append(tx)


random.shuffle(transactions)
batch_size =100
print(f" Injecting {len(transactions)} transactions into the Engine")

for i in range(0, len(transactions), batch_size):
    batch = transactions[i:i + batch_size]
    response = requests.post(API_URL, json=batch)
    
    if response.status_code == 200:
        print(f" Batch {i//batch_size +1} injected successfully")
    else:
        print(f" Error in the batch: {response.text}")
        break

print("Injection complete")