from datetime import datetime,timedelta
import random
from data.transaction import Transaction 
from data.account import Account
from data.account_role import AccountRole 
from data.fraud_generators import FRAUD_GENERATORS , FRAUD_WEIGHTS
from data.fraud_selection import choose_fraud_type
from data.time_utilities import random_timestamp

MIN_FRAUD_BURST = 5





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
        else:
            max_burst_possible = remaining //8
            if max_burst_possible <MIN_FRAUD_BURST:
                nb_tx_for_iteration = random.randint(1, max(1,remaining // 4))
                newTx =generate_healthy_transaction_data(nb_tx_for_iteration,eligible_accounts,start_time,end_time)
            else:
                burst_size =random.randint(MIN_FRAUD_BURST, max_burst_possible)
                fraud_generator = choose_fraud_type()
                newTx = fraud_generator(burst_size,eligible_accounts,start_time,end_time)

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
   
