from data.synthetic_generator import master_data_generator


def test_transaction_count():
    txs = master_data_generator(
        n_accounts=20,
        n_transactions=100,
        n_days=5,
        fraud_probability=0.2
    )
    assert len(txs) == 100


def test_no_self_transfers():
    txs = master_data_generator(
        n_accounts=20,
        n_transactions=100,
        n_days=5,
        fraud_probability=0.2
    )
    for tx in txs:
        assert tx["from_account"] != tx["to_account"]