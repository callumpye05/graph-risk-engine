from datetime import datetime,timedelta
import random
from data.transaction import Transaction 
from data.account import Account
from data.account_role import AccountRole 

MIN_FRAUD_BURST = 5





#helper method designed to create a timestamp from an interval passed in parameter
def random_timestamp(start: datetime , end : datetime) -> datetime : 
    delta = end - start 
    random_sec = random.randint(0 , int(delta.total_seconds()))
    return start + timedelta(seconds=random_sec)



def account_generator(n : int) -> dict[int, Account] : 
    accounts = {}
    now = datetime.now()

    for id in range(n) : 
        role = random.choices(population=[AccountRole.BUSINESS , 
                                          AccountRole.DORMANT , AccountRole.INTERMEDIATE , AccountRole.PERSONAL , AccountRole.STUDENT],
                                          weights=[0.20 , 0.10 , 0.05 , 0.35 , 0.30])[0]
        creation_time = now - timedelta(days = random.randint(30,3650))
        accounts[id] = Account(id , role , creation_time)
    
    return accounts 


def master_data_generator (n_accounts : int , n_transactions : int , n_days : int , fraud_probability : float) -> list[Transaction] :
    
    if n_accounts < 2 :
        raise ValueError("At least two accounts are required for data generation")
     
    transactions = []
    accounts = account_generator(n_accounts)

    end_time = datetime.now()
    start_time = end_time - timedelta(days= n_days)

    eligible_accounts = [
        acc for acc in accounts.values()
        if acc.creation_time < end_time
    ]

    

    

    while len(transactions) < n_transactions : 
        if len(eligible_accounts) < 2:
            break
        remaining = n_transactions - len(transactions)
        is_fraud = random.random() < fraud_probability

        if not is_fraud : 
            nb_tx_for_iteration = random.randint(1, max(1, remaining // 4))
            newTx = generate_healthy_transaction_data(nb_tx_for_iteration, eligible_accounts , start_time, end_time)
        else : 
            max_burst_possible = remaining // 8
            if max_burst_possible < MIN_FRAUD_BURST  :
                nb_tx_for_iteration = random.randint(1, max(1, remaining // 4))
                newTx = generate_healthy_transaction_data(nb_tx_for_iteration, eligible_accounts, start_time, end_time)
            else:
                burst_size = random.randint(MIN_FRAUD_BURST , max_burst_possible)
                if random.random() < 1/3 :  
                    newTx = generate_repeated_fraudulent_data(burst_size, eligible_accounts , start_time , end_time)
                else : 
                    newTx = generate_largeamount_fraudulent_data(burst_size , eligible_accounts , start_time , end_time  )

        transactions.extend(newTx[:remaining]) 

    return transactions 


def generate_healthy_transaction_data(n_transactions : int , accounts : list[Account] , start_time : datetime, end_time : datetime) -> list : 
    transactions = []

    for _ in range(n_transactions) :
        from_account = random.choice(accounts)
        to_account = random.choice(accounts)

        while from_account == to_account : 
            to_account = random.choice(accounts)
        
        tx_start = max(start_time , from_account.creation_time, to_account.creation_time)
        if tx_start > end_time:
            continue 

        base_amount = random.uniform(200, 800)
        amount = round(random.gauss(base_amount, base_amount * 0.05), 2)
        timestamp = random_timestamp(tx_start , end_time)
        tx = Transaction(from_account.account_id ,to_account.account_id , amount , timestamp , "transfer", False)

        transactions.append(tx)
    return transactions
   
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


