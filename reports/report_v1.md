# Graph-Based Risk Engine (v1.0)

##  Overview
A stateful, real-time transaction scoring engine designed to detect complex money laundering typologies (such as structuring and circular looping). 

Unlike traditional relational databases that struggle with multi-hop relationships, this engine maps financial networks in real-time, instantly identifying suspicious clusters and assigning mathematical risk scores using Python-based heuristics.

## Architecture & Tech Stack
This updated version of the project is built on a containerized, three-tier architecture:

* **Gateway (FastAPI & Pydantic):** A strictly-typed, high-performance REST API that acts as the ingestion layer for batch transaction data.
* **Brain (Python 3):** A custom rules engine utilizing statistical heuristics (e.g., standard deviation over batch amounts, velocity checks) to calculate dynamic risk scores. Includes zero-division safety for uniform data batches.
* **Memory (Neo4j & Cypher):** A graph database that permanently records transaction paths (`TRANSFERRED_TO`) and persists the computed `risk_score` directly onto `Account` nodes for instant visual querying.
* **Infrastructure (Docker Compose):** Fully containerized local environment ensuring perfect parity between the API and the Graph network.

## Core Features
* **Real-Time Batch Scoring:** Ingests JSON arrays of transactions and returns risk assessments in milliseconds.
* **Graph-Native Persistence:** Automatically converts tabular transaction data into a connected graph network.
* **Typology Detection:** Successfully identifies "Structuring" (smurfing) by flagging high-value, high-velocity circular transactions.

## The Test
To prove the engine's viability, I built a synthetic data generator (`feed_the_machine.py`) to simulate a live financial network:
1. **The Noise:** Generated 1,000 normal transactions across 200 regular users (amounts ranging from $10 to $500).
2. **The Anomaly:** Injected a 5 node money laundering ring executing rapid-fire $9,900 transfers to evade reporting limits.
3. **The Result:** The Engine successfully isolated the 5 criminal accounts, assigning them the highest risk scores in the database (`0.5`), filtering out the 200 normal users.

#### What comes next? 

So far on this project , I've tried to create a basic skeleton structure, followed by fixing logical errors. My previous mistakes in my v0 were trying to achieve a perfect , compact skeleton, without any logic to scale. Right now my goal is to first master how data will be handled, whilst upgrading current scoring logic. 

this would mean : 

1. **Event-driven streaming:**  We need data to be read in real time, somewhat like a river, if you throw a stone into a river, it interacts with water. Instantaneously , the stone is now within the river. We require the same thought process for our data. Whenever a transaction takes place, the database is instantly updated and risk scores are updated. This prevents the need for a user to manuallty add transactions themselves. To do this we could use the likes of Apache Kafka. 

2. **Improved scoring logic:** It's necessary to further increase scoring logic specifically in the area of communities. this means that an individual with a high risk score, who interacts with another individual with a low risk score, should still see their risk score be increased, despite the transaction being somewhat normal. 
I pull this from the idea that if a person interacts with another person, who is alrealdy deemed suspicious, then by extension this person can be given slight suspicion too. This idea reinforces our likelihood of detecting fraudulent rings. To pull this off , we could use Neo4j's GDS library and shfit from relying simply on mathematical logic, to logic rooted in graph theory with network algorithms. 


3. **A robust front end:** As it stands, in order for this project to be not only functionable but usable, we need a dynamic, manageable and efficient front end allowing for query execution and graph visualisation. If we're to imagine a banker using our technology, we must put ourselves in his shoes, he may not be a master of technology or our product, which is why we need to develop a front end allowing him to perofrm necessary human checks on the data to flag potentially fraudulent activity. For this the likes of React will be used. 

4. **Cloud Deployment**
Right now, development is conducted on an **Apple MacBook Air M1**  which is effective for small-scale testing.  However, we plan to scale to a high-tier cloud infrastructure. To meet these expectations, it is crucial to scale our current **1000-entry dataset** into a production-ready system capable of processing **hundreds of thousands of transactions per day**.


### In conclusion of what's to come 

Most of what we're trying to implement in the upcoming weeks will focus on Architecture, more than plain logic. Essentially the software needs to shift from logic, to a **self-learning machine equipped with a neurological brain**. The difficulties that lie ahead serve as a means for us to develop critical and creative thinking. By the end of V2 , we should have a **Saas Ready Financial Intelligence Platform** ready for client testing in the finance industry.




### Visualizing the Fraud Ring (Cypher)
```cypher
MATCH path = (a:Account)-[r:TRANSFERRED_TO]->(b:Account)
WHERE a.id CONTAINS 'DIRTY'
RETURN path


