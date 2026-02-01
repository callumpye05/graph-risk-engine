from pyvis.network import Network

net = Network(height="600px", width="100%", directed=True)

net.add_node(1, label="Account 1")
net.add_node(2, label="Account 2")

net.add_edge(1, 2, label="Transfer")

net.show("test_graph.html", notebook=False)
