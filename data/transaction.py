from datetime import datetime


class Transaction() : 
    def __init__(self,from_account_id : int , to_account_id : int  , amount : float , timestamp : datetime, tx_type : str, is_fraud : bool ) : 
        self.from_account = from_account_id
        self.to_account = to_account_id 
        self.amount = amount
        self.timestamp = timestamp 
        self.tx_type = tx_type 
        self.is_fraud = is_fraud
