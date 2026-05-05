import random
from datetime import datetime
from data.base_account import BaseAccount
class CorporatePersona(BaseAccount):
    def __init__(self, account_id: str, creation_time: datetime):
        #requires massive liquidity to operate
        super().__init__(account_id, creation_time, starting_balance=random.uniform(1000000, 5000000))
        
        #defining the corporate rhythm
        self.payroll_days =[15, 28] #using 28 avoids end-of-month datetime calculation errors
        self.employee_count =random.randint(50, 200)

    def step_time(self, current_time: datetime, ecosystem: list):
        transactions = []
        
        #BEHAVIOR 1:payroll event
        #triggers exactly at 8:00 AM on designated payroll days
        if current_time.day in self.payroll_days and current_time.hour == 8:
            
            #isolate the Retail worker class from the ecosystem
            retail_pool = [acc for acc in ecosystem if acc.role == "RetailPersona"]
            
            if retail_pool:
                #select our "employees" from the pool
                employees = random.sample(retail_pool, min(self.employee_count, len(retail_pool)))
                
                for employee in employees:
                    #salaries are high-value and highly repetitive
                    salary = random.uniform(3000, 8000)
                    tx = self.send_funds(employee, salary, current_time, is_fraud=0)
                    if tx:
                        transactions.append(tx)

        #BEHAVIOR 2: B2B vendor payment
        #big irregular wire transfers to other corporations
        if current_time.weekday() == 2 and current_time.hour == 14:
            #find another corporation
            corporates = [acc for acc in ecosystem if acc.role == "CorporatePersona" and acc.account_id != self.account_id]
            
            if corporates and random.random() <0.3: #30% chance to pay a vendor this week
                vendor = random.choice(corporates)
                invoice_amount =random.uniform(50000,250000)
                
                tx= self.send_funds(vendor, invoice_amount, current_time, is_fraud=0)
                if tx:
                    transactions.append(tx)

        return transactions