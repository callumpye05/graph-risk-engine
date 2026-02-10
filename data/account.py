from datetime import datetime
from data.account_role import AccountRole

class Account():
    def __init__(self, account_id : int , role : AccountRole , creation_time : datetime ) : 
        self.account_id = account_id
        self.role = role
        self.creation_time = creation_time 

    
