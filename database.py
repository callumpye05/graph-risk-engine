from neo4j import GraphDatabase
import os



URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password123"))

class GraphDB:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=AUTH)

    def close(self):
        self.driver.close()

    def add_transaction(self, from_id, to_id, amount, timestamp):
        with self.driver.session() as session:
            query = """
            MERGE (a:Account {id: $from_id})
            MERGE (b:Account {id: $to_id})
            CREATE (a)-[:TRANSFERRED_TO {amount: $amount, time: $timestamp}]->(b)
            """
            session.run(query, from_id=from_id, to_id=to_id, 
                        amount=amount, timestamp=str(timestamp))
    
    def update_risk_score(self, account_id: str, risk_score: float):
        """Updates the risk_score property on an Account node."""
        query = """
        MERGE (a:Account {id: $account_id})
        SET a.risk_score = $score
        """
        try:
            with self.driver.session() as session:
                session.run(query, account_id=account_id, score=risk_score)
        except Exception as e:
            print(f"Failed to update risk score for {account_id}: {e}")
    
    def get_account_history(self, account_id: str, current_timestamp: float, window_seconds: int = 3600):
        """
        Enterprise V2: Single-pass aggregation. 
        Calculates lifetime stats AND recent velocity in one database hit.
        """
        window_start = current_timestamp - window_seconds
        
        query = """
        MATCH (a:Account {id: $account_id})-[r:TRANSFERRED_TO]->()
        RETURN 
            avg(r.amount) AS avg_amount, 
            stDev(r.amount) AS std_amount,
            sum(CASE WHEN r.timestamp >= $window_start THEN 1 ELSE 0 END) AS recent_count
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, account_id=account_id, window_start=window_start)
                record = result.single()

                # If the user is brand new and has no history
                if not record or record["avg_amount"] is None:
                    return {"avg_amount": 0.0, "std_amount": 1.0, "recent_count": 0}
                
                # Protect against nulls for single-transaction history
                return {
                    "avg_amount": record["avg_amount"],
                    "std_amount": record["std_amount"] if record["std_amount"] is not None else 1.0,
                    "recent_count": record["recent_count"]
                }
        except Exception as e:
            print(f"❌ DB Error getting history for {account_id}: {e}")
            return {"avg_amount": 0.0, "std_amount": 1.0, "recent_count": 0}
        
db = GraphDB()