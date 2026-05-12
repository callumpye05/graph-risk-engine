import random
from datetime import datetime
from simulation.data.base_account import BaseAccount 

class SmurfBot(BaseAccount):
    """
    the evolution of REPEATED_BURST.
    Designed to evade amount-based thresholds by structuring large capital flights
    into hundreds of micro-transactions.
    """
    def __init__(self, account_id: str, creation_time: datetime):
        #usually pre-funded mules. 
        super().__init__(account_id, creation_time, starting_balance=random.uniform(5000, 15000))
        self.is_active =False
        self.target_account = None

    def step_time(self, current_time: datetime, ecosystem: list):
        transactions = []
        
        #Target acquisition (only once)
        if not self.target_account and self.balance > 0:
            #Smurf selects a single target from the ecosystem
            self.target_account = random.choice(ecosystem)
            self.is_active = True

        
        #operate in the dead of night to avoid human detection
        if self.is_active and 2 <= current_time.hour <= 4 and self.balance > 0:
            
            #do a burst of 3 to 7 micro-transactions in this single hour
            burst_size = random.randint(3, 7)
            base_amount = random.uniform(200, 800) # Your original mathematical signature
            
            for _ in range(burst_size):
                if self.balance <=0:
                    break
                    
                #use Gaussian distribution to mask the amounts
                amount = round(random.gauss(base_amount, base_amount * 0.05), 2)
                transfer_amount = min(self.balance, amount)
                
                tx = self.send_funds(self.target_account, transfer_amount, current_time, is_fraud=1)
                if tx:
                    transactions.append(tx)
                    
        return transactions


class BlitzNode(BaseAccount):
    """
    the evolution of LARGE_AMOUNT.
    represents an Account Takeover or a panicked exit scam. 
    it favors speed attempting to drain maximum liquidity instantly.
    """
    def __init__(self, account_id: str, creation_time: datetime):
        #compromised corporate or high-net-worth retail account
        super().__init__(account_id, creation_time, starting_balance=random.uniform(50000, 150000))

    def step_time(self, current_time: datetime, ecosystem: list):
        transactions = []
        
        #usually blitz attacks are random and violent.5% chance to trigger any given hour
        if self.balance > 0 and random.random() < 0.05:
            
            #pick a random victim for this attack
            target = random.choice(ecosystem)
            
        
            base_amount = random.uniform(2000, 30000)
            amount = round(random.gauss(base_amount, base_amount * 0.05), 2)
            transfer_amount = min(self.balance, amount)
            
            tx = self.send_funds(target, transfer_amount, current_time, is_fraud=1)
            if tx:
                transactions.append(tx)
                
        return transactions
    




import random
from datetime import datetime
from simulation.data.base_account import BaseAccount

class ObfuscationRelay(BaseAccount):
    """
    the evolution of CIRCULAR_LAUNDERING.
    Operates strictly as a pass-through node in a multi-hop network.
    It does not possess the full network topology
    to its immediate downstream target to obfuscate the origin of funds.
    """
    def __init__(self, account_id: str,creation_time: datetime):
        #relays start uncapitalized. They act as transit infrastructure.
        super().__init__(account_id, creation_time, starting_balance=0.0)
        
        #the pointer to the next vertex in the directed graph
        self.downstream_target =None 

    def step_time(self, current_time: datetime,ecosystem: list):
        transactions =[]
        
        #relay only executes if it is holding an active payload
        if self.balance > 10.0 and self.downstream_target:
            
            #Delay 80% execution probability per clock tick.
            #prevents the entire chain from executing in the same millisecond
            if random.random() < 0.8:
                
                #alters the exact numeric value 
                #to break static amount-matching heuristics.
                pass_amount = self.balance * random.uniform(0.95, 0.99)
                
                #forward the payload to the next node
                tx = self.send_funds(self.downstream_target, pass_amount, current_time, is_fraud=1)
                if tx:
                    transactions.append(tx)
                    
        return transactions