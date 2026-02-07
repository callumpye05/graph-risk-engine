from datetime import datetime

class Account():
    def __init__(self, account_id : int , role : str , creation_time : datetime ) : 
        self.account_id = account_id
        self.role = role
        self.creation_time = creation_time 

    
