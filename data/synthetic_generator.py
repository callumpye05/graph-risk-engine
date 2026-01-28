from datetime import datetime,timedelta
import random

MIN_FRAUD_BURST = 5

def create_transaction(
    from_account: int,
    to_account: int,
    amount: float,
    timestamp: datetime,
    tx_type: str,
    is_fraud : bool 
) ->dict:
    return {
        "from_account": from_account,
        "to_account": to_account,
        "amount": amount,
        "timestamp": timestamp,
        "tx_type": tx_type,
        "is_fraud": is_fraud
    }

#helper method designed to create a timestamp from an interval passed in parameter
def random_timestamp(start: datetime , end : datetime) -> datetime : 
    delta = end - start 
    random_sec = random.randint(0 , int(delta.total_seconds()))
    return start + timedelta(seconds=random_sec)


def master_data_generator (n_accounts : int , n_transactions : int , n_days : int , fraud_probability : float) -> list :
    
    if n_accounts < 2 :
        raise ValueError("At least two accounts are required for data generation")
     
    transactions = []
    end_time = datetime.now()
    start_time = end_time - timedelta(days= n_days)
    

    while len(transactions) < n_transactions : 
        remaining = n_transactions - len(transactions)
        is_fraud = random.random() < fraud_probability

        if not is_fraud : 
            nb_tx_for_iteration = random.randint(1, max(1, remaining // 4))
            newTx = generate_healthy_transaction_data(nb_tx_for_iteration, n_accounts , start_time, end_time)
        else : 
            max_burst_possible = remaining // 8
            if max_burst_possible < MIN_FRAUD_BURST  :
                nb_tx_for_iteration = random.randint(1, max(1, remaining // 4))
                newTx = generate_healthy_transaction_data(nb_tx_for_iteration, n_accounts, start_time, end_time)
            else:
                burst_size = random.randint(MIN_FRAUD_BURST , max_burst_possible)
                if random.random() < 1/3 :  
                    newTx = generate_repeated_fraudulent_data(burst_size, n_accounts , start_time , end_time)
                else : 
                    newTx = generate_largeamount_fraudulent_data(burst_size , n_accounts , start_time , end_time  )

        transactions.extend(newTx[:remaining]) 

    return transactions 


    
def generate_healthy_transaction_data(n_transactions : int , n_accounts , start_time :datetime , end_time : datetime) -> list: 
    transactions = []
    for _ in range (n_transactions) : 
        from_account = random.randint(0 , n_accounts - 1)
        to_account = random.randint(0 , n_accounts - 1)

        while from_account == to_account  :
            to_account = random.randint(0, n_accounts - 1)
         
        amount = round(random.uniform(5 , 300) , 2)
        timestamp = random_timestamp(start_time , end_time)

        tx = create_transaction(from_account , to_account , amount , timestamp , "transfer" , False )
        transactions.append(tx)
    
    return transactions

def generate_repeated_fraudulent_data(n_transactions : int  , n_accounts : int , start_time : datetime , end_time : datetime) : 
    transactions = []
    chosen_to_account = random.randint(0 , n_accounts-1)
    chosen_from_account = random.randint(0 , n_accounts-1)
    base_time = random_timestamp(start_time, end_time)
    while chosen_to_account == chosen_from_account : 
        chosen_to_account = random.randint(0 , n_accounts -1) 

    for _ in range(n_transactions) :
        
        amount = round(random.uniform(75 , 1000) , 2)
        timestamp = base_time + timedelta(minutes=random.randint(0, 30))
        tx = create_transaction(chosen_from_account , chosen_to_account , amount , timestamp , "transaction" , True)
        transactions.append(tx)
    
    return transactions 

def generate_largeamount_fraudulent_data( n_transactions : int , n_accounts : int , start_time : datetime , end_time : datetime) :
    transactions = []

    for _ in range(n_transactions) :

        amount = round(random.uniform(1000 , 10000) , 2)
        timestamp = random_timestamp(start_time , end_time)
        from_account = random.randint(0 , n_accounts - 1)
        to_account = random.randint(0 , n_accounts - 1)

        while from_account == to_account  :
            to_account = random.randint(0, n_accounts - 1) 

        tx = create_transaction(from_account , to_account , amount , timestamp , "transfer" , True)
        transactions.append(tx)
    return transactions




#Quick test case to check if data is generating 
if __name__ == "__main__":
    txs = master_data_generator( n_accounts=50,n_transactions=200, n_days=7,fraud_probability=0.125)
    txs_sorted = sorted(txs, key=lambda tx: tx["amount"], reverse=True)

    print("Top 10 transactions by amount:\n")
    for tx in txs_sorted[:10]:
        print(tx)

