import matplotlib.pyplot as plt
import networkx as nx


def plot_transaction_graph(G: nx.MultiDiGraph,min_out_degree: int = 3,highlight_fraud: bool = True):

    fraud_nodes = set()
    for u, v, data in G.edges(data=True):
        if data.get("is_fraud", False):
            fraud_nodes.add(u)
            fraud_nodes.add(v)

    nodes = {n for n in G.nodes() if G.out_degree(n) >= min_out_degree}.union(fraud_nodes)
    G_vis = G.subgraph(nodes)
    pos = nx.spring_layout(G_vis, seed=42)
    normal_edges =[]
    fraud_edges = []
    normal_widths = []
    fraud_widths =[]

    for u,v, data in G_vis.edges(data=True):
        widthHealthy = data.get("amount",100) / 500
        widthFraudulent = data.get("amount",100)/700
        if highlight_fraud and data.get("is_fraud", False):
            fraud_edges.append((u, v))
            fraud_widths.append(widthFraudulent)
        else:
            normal_edges.append((u, v))
            normal_widths.append(widthHealthy)
    plt.figure(figsize=(10, 8))
    nx.draw_networkx_nodes(G_vis, pos,node_size=700,node_color="lightblue")
    nx.draw_networkx_labels(G_vis, pos,font_size=9)
    nx.draw_networkx_edges(G_vis, pos,edgelist=normal_edges,width=normal_widths,edge_color="green",alpha=0.5,arrows=True,arrowsize=15,connectionstyle="arc3,rad=0.15")

    if highlight_fraud:
        nx.draw_networkx_edges(G_vis, pos,edgelist=fraud_edges,width=fraud_widths,edge_color="red",alpha=0.9,arrows=True,arrowsize=15)

    plt.title("Transactional Graph")
    plt.axis("off")
    plt.show()