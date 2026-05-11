import random
import uuid
from datetime import datetime, timedelta

from simulation.data.corporate_persona import CorporatePersona
from simulation.data.merchant_persona import MerchantPersona
from simulation.data.retail_persona import RetailPersona 
from simulation.data.adversarial import SmurfBot, BlitzNode, ObfuscationRelay

def generate_account_id(prefix: str) -> str:
    """Generates a clean, readable ID for the simulation."""
    return f"{prefix}-{uuid.uuid4().hex[:6].upper()}"

def run_simulation(days: int = 7):
    print("Initializing data engine")
    
    #create an ecosystem
    ecosystem = []
    start_time = datetime.now() - timedelta(days=days)
    
    print("making legitimate ecosystem...")
    for _ in range(1000):
        ecosystem.append(RetailPersona(generate_account_id("RET"), start_time))
    
    for _ in range(50):
        ecosystem.append(MerchantPersona(generate_account_id("MER"), start_time))
        
    for _ in range(5):
        ecosystem.append(CorporatePersona(generate_account_id("CORP"), start_time))

    print("creating threat actors...")
    for _ in range(10):
        ecosystem.append(SmurfBot(generate_account_id("SMRF"), start_time))
        
    for _ in range(5):
        ecosystem.append(BlitzNode(generate_account_id("BLTZ"), start_time))

    
    #instantiate the relays and manually link them into a blind circle
    ring_size =5
    relays =[ObfuscationRelay(generate_account_id("TUMB"), start_time) for _ in range(ring_size)]
    
    for i in range(ring_size):
        #point each relay to the next one in the list, then wrapping
        relays[i].downstream_target =relays[(i + 1) % ring_size]
    
    #inject initial illicit capital
    relays[0].balance +=75000.0 
    
    
    ecosystem.extend(relays)
    print(f"Starting clock ({days} Days)")
    current_time =start_time
    end_time= datetime.now()
    
    all_transactions = []
    
    #go through the simulation hour by hour
    while current_time <end_time:
        
        #every node in ecosystem gets a chance to act during the hour
        for account in ecosystem:
            #the accounts decide if they should transact
            new_txs = account.step_time(current_time, ecosystem)
            
            if new_txs:
                all_transactions.extend(new_txs)
                
        #advance clock
        current_time +=timedelta(hours=1)

    print(f" Simulation is complete, generated {len(all_transactions)} transactions.")
    
    #sort chronologically
    all_transactions.sort(key=lambda x: x["timestamp"])
    
    return all_transactions

if __name__ == "__main__":
    dataset = run_simulation(days=14)
    
    # From here, you can stream 'dataset' directly to your Kafka producer
    # or write it to a JSON/CSV file for your Julia optimizer to ingest.
    print(f"First 5 transactions preview: {dataset[:5]}")