import random
from datetime import datetime,timedelta

def random_timestamp(start: datetime , end : datetime) -> datetime : 
    delta = end - start 
    random_sec = random.randint(0 , int(delta.total_seconds()))
    return start + timedelta(seconds=random_sec)
