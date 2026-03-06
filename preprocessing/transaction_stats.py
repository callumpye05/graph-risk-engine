from collections import defaultdict
import numpy as np


def compute_features(transaction_list : list) : 

    features = {
        "node" :defaultdict(lambda : {
            "in_count" : 0.0,
            "out_count" : 0.0,
            "total_out" : 0.0,
            "total_in" : 0.0,
            'out_amounts' : [],
            "in_amounts" : [],
            "timestamps" : []
        }), 
        "edges": defaultdict(lambda : {
           "count" : 0,
           "total_amount" : 0.0
        }),
        "global" :{
            "total_transactions" : 0,
            "total_amount" : 0.0

        }
    }

    for tx in transaction_list : 
        u = tx.from_account
        v = tx.to_account
        amt = tx.amount
        ts = tx.timestamp

        #for the sender
        features["node"][u]["out_count"] +=1
        features["node"][u]["total_out"] += amt 
        features["node"][u]["out_amounts"].append(amt)
        features["node"][u]["timestamps"].append(ts)

        #for the receiver 
        features["node"][v]["in_count"] += 1
        features["node"][v]["total_in"] +=amt
        features["node"][v]["in_amounts"].append(amt)
        features["node"][v]["timestamps"].append(ts)

        #edge level
        features["edges"][(u,v)]["count"] += 1
        features["edges"][(u, v)]["total_amount"] +=amt

        #global stats
        features["global"]["total_transactions"]+=1
        features["global"]["total_amount"] += amt

    return features



def compute_global_out_amount_stats(features):
    all_out_amounts = []
    for node_stats in features["node"].values():
        all_out_amounts.extend(node_stats["out_amounts"])
    if not all_out_amounts:
        return {"mean": 0.0, "std": 0.0}
    mean = float(np.mean(all_out_amounts))
    std = float(np.std(all_out_amounts))
    return {"mean": mean, "std": std}
        



