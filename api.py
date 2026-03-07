from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import numpy as np

from graph.build_graph import build_transaction_graph
from scoring.risk_score import compute_risk_scores
from heuristics.frequency import FrequencyHeuristic
from heuristics.high_amount import HighAmountHeuristic
 
from data.transaction import Transaction as InternalTransaction
from preprocessing.transaction_stats import compute_features
from datetime import datetime, timedelta
from database import db


app = FastAPI(
    title="Graph Risk Engine API",
    description="A real time fraud detection engine using NetworkX and Heuristics.",
    version="1.0.0"
)


class TransactionInput(BaseModel):
    from_account: str
    to_account: str
    amount: float
    timestamp: float
    tx_type: str
    is_fraud: int = 0 

class ScoreResponse(BaseModel):
    account_id: str
    risk_score: float
    signals: Dict[str, float]



@app.get("/")
def health_check():
    """Simple check to see if the server is ok"""
    return {"status": "healthy", "service": "Graph Risk Engine"}




@app.post("/api/v1/score-batch")
def score_transaction_batch(transactions: List[TransactionInput]):
    try:
        internal_txs = []
        for tx in transactions:
            db.add_transaction(from_id=tx.from_account,to_id=tx.to_account,amount=tx.amount,timestamp=tx.timestamp)
            internal_txs.append(
                InternalTransaction(
                    from_account_id=tx.from_account,
                    to_account_id=tx.to_account,
                    amount=tx.amount,
                    timestamp=datetime.fromtimestamp(tx.timestamp),
                    tx_type=tx.tx_type,
                    is_fraud=bool(tx.is_fraud)
                )
            )

        #compute Features using  script
        raw_features = compute_features(internal_txs)

        # global Stats for the HighAmountHeuristic
        all_amounts = [tx.amount for tx in internal_txs]
        
        raw_std = float(np.std(all_amounts)) if all_amounts else 1.0
        safe_std = raw_std if raw_std > 0.0 else 1.0
        
        global_stats = {"mean":float(np.mean(all_amounts)) if all_amounts else 0.0,"std":safe_std}

        #flatten the stats for the heuristics
        formatted_stats = {
            "out_timestamps": {acc: data["timestamps"] for acc, data in raw_features["node"].items()},
            "out_amounts": {acc:data["out_amounts"] for acc, data in raw_features["node"].items()}
        }

        #initialize heuristics with parameters
        heuristics_list = [
            FrequencyHeuristic(window_scale=timedelta(minutes=5), scale=10),
            HighAmountHeuristic(global_stats=global_stats, std_factor=2.0)
        ]

        #compute final scores
        results = compute_risk_scores(heuristics_list, formatted_stats)

        
        for account_id, score_data in results.items():
            db.update_risk_score(account_id=account_id, risk_score=score_data["risk"])
       

        return {
            "status": "success",
            "results": results
        }


    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Engine Logic Error: {str(e)}")