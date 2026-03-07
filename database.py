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
        
db = GraphDB()