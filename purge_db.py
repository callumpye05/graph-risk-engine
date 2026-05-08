import redis
from neo4j import GraphDatabase

NEO4J_URI="bolt://neo4j:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password123"

REDIS_HOST = "localhost"
REDIS_PORT = 6379

def execute_purge():
    print("Beggining deletion")
    
    try:
        print("connecting to Neo4j neural graph")
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session() as session:
            #the Cypher command for delettion
            session.run("MATCH (n) DETACH DELETE n")
            
        print("Neo4j Memory Wiped The board is clear")
        driver.close()
    except Exception as e:
        print(f" Neo4j deletion failed: {e}")

    try:
        print("[*] Connecting to Redis Speed Layer...")
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        
        #annihilate all cached thresholds and histories
        r.flushall()
        
        print("Redis Cache flushed, thresholds reset.")
    except Exception as e:
        print(f"Redis Purge Failed: {e}")

    print("DELETETION COMPLETE")

if __name__ == "__main__":
    execute_purge()