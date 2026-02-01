from data.synthetic_generator import master_data_generator
from graph.build_graph import build_transaction_graph
from visualize.plot_graph import plot_transaction_graph
from visualize.plot_graph_nxpyvis import plot_transaction_pyvis_graph


def main():
    txs = master_data_generator(
        n_accounts=10,
        n_transactions=40,
        n_days=5,
        fraud_probability=0.2
    )

    G = build_transaction_graph(txs)

    #plot_transaction_pyvis_graph(G)
    plot_transaction_pyvis_graph(G)


if __name__ == "__main__":
    main()
