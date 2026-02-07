# Project Report — v0

## 1. Project Goal

The objective of this project is to develop a system capable of analysing financial transaction data in order to assess whether an entity exhibits patterns consistent with illicit activity. The system is not designed to act as a judge or to determine guilt. Instead, its sole purpose is to identify and flag entities whose transactional behaviour warrants further scrutiny. Any final judgment remains outside the scope of the system and must be made by human experts or appropriate authorities.
The motivation for this project originates from a broader reflection on how large-scale platforms and institutions address illicit behaviour. In particular, it became apparent that many existing approaches rely heavily on reactive or manual methods, such as decoys or post-factum investigations, rather than on proactive pattern analysis. Given the scale and complexity of modern data, this reliance appears increasingly insufficient.
Rather than addressing this issue directly, this project adopts an analogous and well-defined domain: financial fraud detection. Fraudulent transaction analysis is a mature field with real-world relevance, existing industry applications, and well documented challenges, making it an ideal domain for rigorous experimentation and learning.
At its core, the project is not only an applied system, but also a learning exercise. Its primary goals are to deepen foundational computer science knowledge, explore new programming languages and libraries, and apply theoretical concepts such as graph theory, heuristics, and pattern recognition in a self-directed and meaningful context. Unlike academic exercises with predefined outcomes, this project is intentionally open-ended and exploratory.
By the end of development, the system aims to provide a functional pipeline capable of identifying potentially illicit transactions with a high degree of accuracy and a low false-positive rate. Multiple data representations will be employed, including two-dimensional and three-dimensional visualisations, in order to enhance interpretability and analytical depth. Ultimately, the system organises and evaluates transactional data through a set of dynamically defined heuristics, enabling the detection of anomalous behaviours and potential bad actors.

## 2. Current State (v0)

At its current stage (v0), the project consists of a functional skeleton in which all major components of the system have been implemented at a foundational level. While these components are intentionally minimal, they collectively form a coherent end-to-end pipeline. The core aspects included in v0 are: heuristics definition, scoring mechanisms, data generation, preprocessing, and graph-based representation.
It is important to clarify the development methodology adopted for this project. As this represents my first ambitious solo system-level project, I intentionally chose an iterative, version-based approach inspired by real-world software development practices. Rather than fully developing one subsystem in isolation before moving on to the next, the project is structured around successive versions, each implementing the minimum viable functionality required across all components.
This approach allows for early integration, continuous validation of design decisions, and progressive refinement of the system as a whole. Each version is defined by clear objectives and constraints, serving as a stable foundation upon which subsequent improvements can be built.
As of the completion of v0 developed over approximately one week alongside academic coursework—the system provides a simple but functional implementation of the intended logic. The heuristics are represented accurately for this phase, the scoring mechanism reflects their outputs coherently, and the overall pipeline behaves as expected given the current level of abstraction. While performance,robustness, and sophistication are limited at this stage, the core architecture and conceptual logic are in place, validating the feasibility of the design.

## 3. Architecture Overview

3. Architecture Overview
The architecture of the system is centred around the definition and evaluation of heuristics. While heuristics form the analytical core, the system relies on a complete pipeline that begins with data generation and ends with risk scoring. Each component plays a distinct role within this pipeline.

## 3.1 Data Generation
The system begins with synthetic data generation. Each transaction is represented as a dictionary containing a set of attributes, including: sender, receiver, timestamp, amount, transaction type, and a fraud label.
The fraud label is included at this stage solely as a ground-truth reference, with the long term objective of enabling evaluation of false positives and false negatives in later versions of the system.

## 3.2 Graph Representations
Two types of graph representations are currently implemented, both operating directly on the generated transaction data.
The first graph is constructed using the NetworkX library. This graph provides a basic network-based representation of interactions between entities. At this stage, it is neither optimised nor fully aligned with the intended long-term design, and some inaccuracies remain. Its purpose in v0 is primarily exploratory and educational, serving as an initial exposure to graph-based modelling.
The second graph is a three-dimensional visualisation implemented using PyVis. While still under development, this representation has proven more effective for visually exploring relationships between entities and transactions. At present, both graph types are used exclusively for visualisation purposes and do not influence heuristic evaluation or scoring logic.

## 3.3 Preprocessing
Before heuristics can be evaluated efficiently, the raw transaction data undergoes a preprocessing phase. The purpose of this phase is to reorganise and clean the data in order to avoid repeated filtering operations and costly lookup patterns during heuristic evaluation.
The preprocessing step iterates through the list of transactions and constructs a dictionary of dictionaries, primarily using defaultdict structures. Some entries accumulate lists of values (e.g. transaction timestamps or amounts), while others accumulate counts or aggregated metrics. This structured representation provides a clean and organised view of the raw data, optimised for downstream analysis.
This phase was introduced after initial heuristic development revealed that repeatedly sorting and filtering raw data for each heuristic was inefficient. Centralising these operations into a single preprocessing step improves clarity, performance, and extensibility.

## 3.4 Heuristic Evaluation
The heuristics constitute the core analytical logic of the system. Each heuristic evaluates whether a specific behavioural pattern is present for a given entity. For example, one heuristic detects burst transaction behaviour by identifying unusually dense clusters of transactions within a short time window.
Each heuristic returns a signal associated with an individual entity.In v0, these signals are intentionally simple and under-optimised. For instance, the burst transaction signal is computed as the ratio between the number of transactions in a detected burst and a predefined threshold considered suspicious. Despite their simplicity, these signals accurately represent the intended logical behaviour at this stage.

## 3.5 Risk Scoring
All signals generated by the heuristics are passed to the scoring logic.The scoring component aggregates the signals associated with each entity and computes a risk score.In v0, this computation is performed using a simple aggregation strategy: the sum of signal values divided by the number of signals.
The resulting risk score is then associated with the corresponding entity. While this scoring mechanism is deliberately minimal, it provides a functional baseline that validates the end-to-end flow of the system.

## 3.6 System Flow Summary
At a high level,the system operates according to the following pipeline:
Data Generation -> Graph Construction -> Preprocessing -> Heuristic Evaluation -> Risk Scoring
This structure reflects the current state of v0 and establishes a clear foundation for future iterations, where each component can be refined independently without altering the overall architecture.


## 4. Component Breakdown

### 4.1 Data Generation

The data generation component is responsible for producing a configurable volume of synthetic transaction data. Its primary purpose is to simulate real-world transaction behaviour in order to enable controlled testing and evaluation of the system.

At its current stage, the generator supports three types of transactional patterns:
- **Normal (healthy) transactions**
- **Burst transactions**, characterised by high-frequency activity over a short time window
- **High-amount transactions**, involving anomalously large values

While functional, this component exhibits several known limitations:

1. **Limited pattern coverage**  
   Fraud manifests in a wide variety of behavioural patterns. The current generator covers only a narrow subset, limiting the diversity of scenarios that can be tested.

2. **Probability-driven generation**  
   Transaction patterns are selected based on predefined probabilities. While convenient, this approach can lead to unrealistic distributions and does not adequately capture conditional or adaptive behaviour.

3. **Lack of account identity and roles**  
   All accounts are treated uniformly. Real-world systems distinguish between high-volume accounts, inactive accounts, business entities, and personal users. The absence of such identities renders accounts overly simplistic and reduces realism.

4. **Explicit fraud labelling**  
   Fraud is currently assigned directly rather than emerging from behaviour. This choice is intentional for future evaluation of false positives and false negatives, but it does not reflect how fraud manifests in real systems.

5. **Uniform temporal distribution**  
   Transaction timestamps are generated uniformly. In reality, transactions cluster around daily cycles, weekdays versus weekends, and behavioural habits. These temporal dynamics are not yet modelled.

---

### 4.2 Preprocessing

The preprocessing component transforms raw transaction data produced by the data generation stage into structured representations optimised for heuristic evaluation.

At a basic level, the component fulfils its intended purpose. However, several important limitations remain:

1. **Missing incoming-flow statistics**  
   Preprocessing currently focuses on outgoing transactions (from_account -> statistics) and does not account for incoming transaction flows.

2. **Unsorted timestamps**  
   Transaction timestamps are not ordered chronologically, limiting the accuracy and efficiency of time-based heuristics.

3. **Ignored transaction types**  
   Transaction type information is not incorporated into the preprocessing structures, reducing the contextual richness available to heuristics.

---

### 4.3 Heuristics

The heuristics component evaluates predefined behavioural rules against processed data in order to detect suspicious activity. When a rule is satisfied, the heuristic emits a signal associated with the corresponding entity.

At present, two heuristics are implemented:
- **High Frequency Heuristic**
- **High Amount Heuristic**

#### Limitations of the High Amount Heuristic

1. **Absolute thresholds**  
   The heuristic relies on fixed thresholds. What constitutes a “high” amount may be normal for certain entities, such as wealthy individuals or business accounts.

2. **Single-event dominance**  
   A single large transaction can dominate the heuristic output, overshadowing broader behavioural context.

3. **Evasion through transaction splitting**  
   Large transactions can easily be divided into smaller chunks to avoid triggering the heuristic.

4. **Lack of temporal awareness**  
   The heuristic does not consider transaction timing or frequency, treating all events independently.

#### Limitations of the High Frequency Heuristic

1. **Amount-agnostic behaviour**  
   Transaction values are ignored, making no distinction between low-value and high-value bursts.

2. **Outgoing-only focus**  
   Only outgoing transactions are considered, omitting suspicious incoming patterns.

3. **Historical dominance**  
   Older bursts retain equal weight, while recent normal behaviour is not prioritised or discounted.


### 4.4 Risk Scoring

The risk scoring component aggregates heuristic signals to compute an overall risk score for each entity, representing the likelihood of involvement in fraudulent activity.

The current scoring mechanism is intentionally simple, but exhibits several known limitations:

1. **Uniform heuristic weighting**  
   All heuristics contribute equally, despite differing significance and reliability.

2. **No interaction between signals**  
  Signals are treated independently, whereas real-world fraud often emerges from combinations of weak indicators.

3. **Lack of semantic grounding**  
   The numerical risk score lacks an interpretable semantic meaning (e.g. low, medium, high risk).

4. **Outgoing-only perspective**  
   Risk scoring considers only sending behaviour, ignoring entities that primarily receive suspicious flows.



## 5. Design Choices

The design of this system intentionally prioritises structural completeness over local optimisation. The objective of v0 is not to provide a highly accurate or production-ready solution, but to establish a minimal yet coherent foundation upon which future iterations can be built.

This version lays out the essential architectural skeleton of the system, allowing core components to interact end-to-end. By doing so, design flaws, inefficiencies, and conceptual limitations can be identified early and addressed incrementally in subsequent versions. Rather than attempting to perfect individual components in isolation, the system is designed to evolve through progressive refinement.

The presence of known limitations and simplified mechanisms is therefore intentional and appropriate for v0. These simplifications enable faster iteration, clearer reasoning about system behaviour, and focused learning on fundamental concepts. Future versions will build directly on this foundation, improving realism, robustness, and analytical depth while preserving the overall architecture established in this initial design.





## 7. Roadmap

The immediate next steps of the project focus on consolidating and strengthening the existing foundation before introducing additional complexity.

The primary objective is to **individually address and correct the core limitations already identified** across each component of the system. Rather than expanding the system with deeper logic or new features prematurely, the emphasis will be on improving correctness, coherence, and realism within the current architecture.

At this stage, the goal is to transition from a minimal but functional v0 to a more robust and reliable baseline. This includes refining heuristics, improving preprocessing structures, enhancing data realism, and strengthening the scoring logic. Establishing a stable and well-understood foundation is considered essential before progressing toward more advanced analytical techniques or larger-scale experimentation.



## 8. Conclusion

This project currently exists as a functional but intentionally minimal system that demonstrates the feasibility of the proposed architecture. While numerous limitations remain, they have been explicitly identified and documented, providing clear direction for future development.

The current version serves as a foundational skeleton upon which successive iterations will build. Through incremental updates and targeted improvements, the system is expected to evolve toward greater realism, robustness, and analytical depth, while maintaining the core design principles established in v0.
