import networkx as nx
from data.synthetic_generator import master_data_generator
from graph.build_graph import build_transaction_graph



def test_graph_edge_count_matches_transactions():
    txs = master_data_generator(
        n_accounts=20,
        n_transactions=100,
        n_days=5,
        fraud_probability=0.2
    )

    G = build_transaction_graph(txs)

    assert isinstance(G, nx.MultiDiGraph)
    assert G.number_of_edges() == len(txs)


def test_edges_have_expected_attributes():
    txs = master_data_generator(
        n_accounts=10,
        n_transactions=20,
        n_days=3,
        fraud_probability=0.3
    )

    G = build_transaction_graph(txs)

    for _, _, data in G.edges(data=True):
        assert "amount" in data
        assert "timestamp" in data
        assert "tx_type" in data

