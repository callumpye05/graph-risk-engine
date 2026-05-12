# Autonomous Fraud Engine (V2)

A real time, stateful streaming engine designed to detect and isolate multi dimensional financial fraud, sleeper cells, and obfuscation syndicates. 

this engine utilizes continuous $O(1)$ temporal memory and additive component scoring to evaluate risk across three simultaneous time dimensions (24h, 7d, 30d).

## System Architecture

1. **The Generator (`feed_the_machine.py`):** Simulates a live financial ecosystem containing retail users, legitimate merchants, and adversarial cartels. Injects transactions into a Kafka stream.
2. **The Speed Layer (Redis):** Maintains a high-throughput, 3D velocity matrix for every account, eliminating database read-bottlenecks.
3. **The Matrix (`worker.py`):** Consumes the Kafka stream, calculates pass-through ratios and volume spikes, enforces a stateful Risk Ratchet, and commits the intelligence to Neo4j.
4. **The External Cortex (Julia):** A dynamically triggered optimization container that extracts pure historical data from Neo4j to continuously fine-tune the engine's lethal thresholds.

---

## Quick Start (how to use the engine)

### 1. Provision the Infrastructure
Ensure Docker is running on your machine. We must first build the isolated containers (Kafka, Redis, Neo4j, and the Julia Optimizer) and start the network.

```bash
docker-compose build --no-cache
docker-compose up -d
```

this will most likely take a few minutes to complete, since julia requires a lot of different libraries.Once this is done, you should open up 4 distinct terminals to follow the entire process. One of them will be used for Vite, another for uvicorn, another for worker.py and the final terminal for injecting the data, in this order : 

1. **Vite :** npm run dev from /command-center 
2. **uvicorn :** uvicorn api.main:app --reload from root
3. **worker.py :** python -m engine.worker.py from root
4. **feed_the_machine.py:** python -m simulation.feed_the_machine.py

Afterwards, you should be able to see in the terminal every transaction be fed and analysed by the engine. You can also change the parameters if you wish, for example run the simulation over seven days. In your terminal, you will see Julia activate in order to recalculate optimal parameters, you can also see this in the UI using the URL that Vite provides you with, albeit right now the UI is very basic. 

To halt the simulation, simply Ctrl+c on your terminal executing **worker.py** followed by the terminal with **uvicorn** followed by the terminal using **Vite**. 


## Test unit execution 

You will need **fakeredis** and **pytest** in order to execute the tests. Once you have these in your virtual environment, run the command : **pytest tests/ -v**


