from collections import defaultdict

def computeData (transaction_list : list ) : 
    stats = {
        "out_timestamps" : defaultdict(list),
        "out_amounts" : defaultdict(list),
        "out_count" : defaultdict(int),
        "pair_events_count" : defaultdict(int)
    }

    for tx in transaction_list : 
        u = tx["from_account"]
        v = tx["to_account"]
        ts = tx["timestamp"]
        amt = tx["amount"]

        stats["out_amounts"][u].append(amt)
        stats["out_timestamps"][u].append(ts)
        stats["out_count"][u] += 1
        stats["pair_events_count"][(u,v)] += 1
    
    return stats 

