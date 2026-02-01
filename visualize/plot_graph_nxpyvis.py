from pyvis.network import Network
import networkx as nx


def plot_transaction_pyvis_graph(G: nx.MultiDiGraph, output_file: str = "transaction_graph.html"):

    net =Network(height="750px",width="100%", directed=True,bgcolor="#ffffff", font_color="black")
    net.barnes_hut(gravity=-30000,central_gravity=0.05, spring_length=350,spring_strength=0.006, damping=0.7)

    for node in G.nodes():
        net.add_node(node,label=f"Account {node}",color="lightblue",size=25)
    
    for u, v, data in G.edges(data=True):
        amount = data.get("amount", 0)
        is_fraud = data.get("is_fraud", False)
        net.add_edge(u,v,value=min(amount, 1200),width=max(1, amount / 600),color="red" if is_fraud else "gray", title=(f"<b>Amount:</b> {amount}<br>"f"<b>Fraud:</b> {is_fraud}<br>" f"<b>Type:</b> {data.get('tx_type')}")) 
    
    net.show(output_file,notebook=False)
