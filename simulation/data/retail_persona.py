import random
from simulation.data.base_account import BaseAccount
from datetime import datetime

class RetailPersona(BaseAccount):
    def __init__(self, account_id: str, creation_time: datetime):
        #random retail starting balance 
        super().__init__(account_id, creation_time, starting_balance=random.uniform(1000, 5000))
        
    def step_time(self, current_time: datetime, ecosystem: list):
        transactions = []
        hour = current_time.hour
        
        #retail account sleep at night
        if 1 <= hour <=6:
            return transactions 

        #give it a15% chance to make a standard purchase during waking hours
        if random.random() <0.15: 
            target = random.choice(ecosystem) #we can pick a random entity to pay
            amount =random.uniform(10.0, 300.0)
        
            tx = self.send_funds(target, amount, current_time, is_fraud=0)
            if tx: 
                transactions.append(tx)
            
        return transactions