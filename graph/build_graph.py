import networkx as nx



def build_transaction_graph (transactions : list) -> nx.DiGraph : 
    G = nx.MultiDiGraph()
    for tx in transactions : 
        G.add_edge(tx["from_account"], tx["to_account"], 
                   amount =tx["amount"],
                   timestamp = tx["timestamp"],
                   tx_type = tx["tx_type"], 
                   is_fraud = tx["is_fraud"])
    return G 





        