import uuid
from datetime import datetime


def __init__(self, account_id: str, creation_time: datetime, starting_balance: float = 0.0):
        
    self.account_id = account_id
    self.creation_time = creation_time
        
    #dynamic state variables
    self.balance = starting_balance
    self.transaction_log = []

    @property
    def role(self) -> str:
        """Dynamically returnname of the subclass."""
        return self.__class__.__name__

    def send_funds(self, target_account, amount: float, current_time: datetime, is_fraud: int = 0):
    
        if self.balance < amount:
            return None #prevents overdrafts
        
        self.balance -= amount
        target_account.balance += amount
        
        #payload for Kafka
        tx = {
            "from_account": self.account_id,
            "to_account": target_account.account_id,
            "amount": round(amount, 2),
            "timestamp": current_time.timestamp(),
            "tx_type": "transfer",
            "role_from": self.role,
            "role_to": target_account.role,
            "is_fraud":is_fraud
        }
        self.transaction_log.append(tx)
        return tx

    def step_time(self, current_time:datetime, ecosystem:list):
        """all subclass should define how it behaves when the clock is ticking"""
        raise NotImplementedError("Behavior must be defined in the subclass.")
    

    
