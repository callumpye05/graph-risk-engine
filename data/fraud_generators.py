from data.fraud_type import FraudType 
import random
from data.account import Account
from datetime import datetime,timedelta
from data.transaction import Transaction
from data.time_utilities import random_timestamp




def generate_repeated_fraudulent_data(n_transactions : int , accounts : list[Account], start_time : datetime , end_time : datetime) : 
    
    transactions = []
    to_account = random.choice(accounts)
    from_account = random.choice(accounts)

    while to_account == from_account : 
        to_account = random.choice(accounts)
    
    tx_start = max(start_time , to_account.creation_time , from_account.creation_time)
    base_time = random_timestamp(tx_start,end_time - timedelta(minutes=30))
    base_amount = random.uniform(200, 800)


    for _ in range(n_transactions) :
        amount = round(random.gauss(base_amount,base_amount *0.05), 2)
        timestamp = base_time + timedelta(minutes=random.randint(0, 30))
        tx = Transaction(from_account.account_id ,to_account.account_id, amount , timestamp , "transfer" , True)
        transactions.append(tx)
    
    return transactions 

def generate_largeamount_fraudulent_data( n_transactions : int , accounts : list[Account], start_time : datetime , end_time : datetime) :
    
    transactions = []
    for _ in range(n_transactions) :

        from_account = random.choice(accounts)
        to_account = random.choice(accounts)
        
        while from_account == to_account  :
            to_account = random.choice(accounts)
        
        base_amount = random.uniform(2000, 30000)
        amount = round(random.gauss(base_amount, base_amount * 0.05), 2)
        tx_start = max(start_time , from_account.creation_time , to_account.creation_time)
        timestamp = random_timestamp(tx_start , end_time)

        tx = Transaction(from_account.account_id ,to_account.account_id, amount , timestamp , "transfer" , True)
        transactions.append(tx)
    return transactions


def generate_circular_laundering_data( n_transactions : int , accounts : list[Account] , start_time : datetime , end_time : datetime) : 
    transactions = []
    k=random.randint(3,10)
    account_cycle = random.sample(accounts , k)
    base_amount = random.uniform(2000, 30000)
    nb_cycles = n_transactions // k
    max_start_acc = start_time 

    for acc in account_cycle : 
        if acc.creation_time > max_start_acc : 
            max_start_acc = acc.creation_time
    
    tx_start = max(start_time , max_start_acc)
    base_time = random_timestamp(tx_start,end_time - timedelta(minutes=30))


    for _ in range(nb_cycles) : 
        for j in range(k) :
            amount = round(random.gauss(base_amount, base_amount * 0.05), 2)
            timestamp = base_time + timedelta(minutes=random.randint(0, 30))
            tx = Transaction(account_cycle[j].account_id , account_cycle[(j + 1 )  % k ].account_id , amount , timestamp ,"transfer" , True)
            transactions.append(tx)
            base_time = timestamp
        
    
    return transactions 




FRAUD_GENERATORS = {
    FraudType.REPEATED_BURST:generate_repeated_fraudulent_data,
    FraudType.LARGE_AMOUNT: generate_largeamount_fraudulent_data,
    FraudType.CIRCULAR_LAUNDERING: generate_circular_laundering_data,
}

FRAUD_WEIGHTS = {
    FraudType.REPEATED_BURST: 0.4,
    FraudType.LARGE_AMOUNT: 0.35,
    FraudType.CIRCULAR_LAUNDERING:0.25,
}

