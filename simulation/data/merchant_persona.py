import random
from datetime import datetime
from simulation.data.base_account import BaseAccount

class MerchantPersona(BaseAccount):
    def __init__(self, account_id: str, creation_time: datetime):
        #merchants often require a larger operational baseline than retail
        super().__init__(account_id, creation_time, starting_balance=random.uniform(10000, 50000))
        
        #every merchant keeps a baseline reserve to operate, sweeping the rest to a supplier
        self.reserve_target = random.uniform(5000, 15000)

    def step_time(self, current_time: datetime, ecosystem: list):
        transactions =[]
        hour = current_time.hour
        
        # NOTE: merchants are entirely passive during the day for me. 
        #they do not initiate purchases, the RetailPersonas initiate transfers towards them.
        #The merchant's only active behavior is the end-of-day supplier sweep
        
        #we execute batch payment to a supplier at the end of the business day(11:00 PM)
        if hour ==23:
            if self.balance > self.reserve_target:
                #sweep the excess daily profits to a corporate supplier
                sweep_amount = self.balance - self.reserve_target
                
                #locate a Corporate node to act as the B2B supplier
                suppliers =[acc for acc in ecosystem if acc.role =="CorporatePersona"]
                
                #if we haven't loaded Corporate accounts yet, fallback to a random entity
                target_supplier = random.choice(suppliers) if suppliers else random.choice(ecosystem)
                
                #execute the massive, legitimate outbound wire
                tx =self.send_funds(target_supplier, sweep_amount, current_time, is_fraud=0)
                if tx: 
                    transactions.append(tx)
                    
        return transactions