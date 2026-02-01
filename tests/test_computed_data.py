from data.synthetic_generator import master_data_generator
from preprocessing.transaction_stats import computeData



def test_computeData_basic():
    txs = master_data_generator(n_accounts=10,n_transactions=50,n_days=3,fraud_probability=0.)
    stats = computeData(txs)

    #basic existence checks
    assert "out_timestamps" in stats
    assert "out_amounts" in stats
    assert "out_count" in stats
    assert "pair_events_count" in stats

    #consistency check
    for account in stats["out_count"]:
        assert stats["out_count"][account] == len(stats["out_timestamps"][account])
        assert stats["out_count"][account] == len(stats["out_amounts"][account])

    #pair counts sanity
    total_pair_events = sum(stats["pair_events_count"].values())
    assert total_pair_events ==len(txs)

    print("computeData basic test passed.")