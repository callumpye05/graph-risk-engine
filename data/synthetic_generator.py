from datetime import datetime,timedelta
import random

def create_transaction(
    from_account: int,
    to_account: int,
    amount: float,
    timestamp: datetime,
    tx_type: str
) ->dict:
    return {
        "from_account": from_account,
        "to_account": to_account,
        "amount": amount,
        "timestamp": timestamp,
        "tx_type": tx_type
    }

#helper method designed to create a timestamp from an interval passed in parameter
def random_timestamp(start: datetime , end : datetime) -> datetime : 
    delta = end - start 
    random_sec = random.randint(0 , int(delta.total_seconds()))
    return start + timedelta(seconds=random_sec)


def generate_transaction_data(n_accounts : int , 
                              n_transactions : int , 
                              n_days : int = 7
                            ) -> list: 
    transactions = []
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)

    for _ in range (n_transactions) : 
        from_account = random.randint(0 , n_accounts)
        to_account = random.randint(0 , n_accounts)

        if from_account == to_account :
            continue 

        amount = round(random.uniform(5 , 300) , 2)
        timestamp = random_timestamp(start_time , end_time)

        tx = create_transaction(from_account , to_account , amount , timestamp , "transfer" )
        transactions.append(tx)
    
    return transactions


