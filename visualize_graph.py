from data.synthetic_generator import master_data_generator
from graph.build_graph import build_transaction_graph
from visualize.plot_graph import plot_transaction_graph


def main():
    txs = master_data_generator(
        n_accounts=15,
        n_transactions=40,
        n_days=5,
        fraud_probability=0.2
    )

    G = build_transaction_graph(txs)

    plot_transaction_graph(
        G,
        min_out_degree=2,
        highlight_fraud=True
    )


if __name__ == "__main__":
    main()
