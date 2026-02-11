from data.synthetic_generator import master_data_generator
from data.fraud_generators import generate_circular_laundering_data
from data.account import Account
from data.time_utilities import random_timestamp
from datetime import datetime,timedelta




MIN_FRAUD_BURST = 5


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
        assert tx.from_account != tx.to_account





def test_fraud_presence():
    txs = master_data_generator(
        n_accounts=30,
        n_transactions=300,
        n_days=7,
        fraud_probability=0.2
    )

    fraud_txs = [tx for tx in txs if tx.is_fraud]

    assert len(fraud_txs) > 0
    assert len(fraud_txs) < len(txs)



def test_repeated_fraud_has_repeated_pairs():
    txs = master_data_generator(
        n_accounts=30,
        n_transactions=300,
        n_days=7,
        fraud_probability=0.5
    )

    fraud_pairs = {}
    for tx in txs:
        if tx.is_fraud:
            pair = (tx.from_account, tx.to_account)
            fraud_pairs[pair] = fraud_pairs.get(pair, 0) + 1

    assert any(count >= MIN_FRAUD_BURST for count in fraud_pairs.values())




def test_circular_fraud_has_closed_participant_set():
    accounts = [
        Account(i, None, datetime.now() - timedelta(days=100))
        for i in range(10)
    ]

    txs = generate_circular_laundering_data(
        n_transactions=30,
        accounts=accounts,
        start_time=datetime.now() - timedelta(days=5),
        end_time=datetime.now()
    )

    senders = {tx.from_account for tx in txs}
    receivers = {tx.to_account for tx in txs}
    participants = senders | receivers

    assert len(participants) >= 3

    for acc in participants:
        assert acc in senders
        assert acc in receivers






