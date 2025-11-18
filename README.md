# HetioNet Project 1 – Big Data Technologies

## Overview
This project integrates **MongoDB** and **Neo4j** (via Docker) to explore biological relationships in the **HetioNet** dataset. This dataset is a network connecting diseases, genes, drugs, and anatomical locations.

Two main queries were implemented using Python to extract and analyze biological insights:

1. **Query 1 – Disease Information**  
   Given a disease ID, find:
   - The disease name  
   - Drugs that treat or palliate it (`CtD`, `CpD`)  
   - Genes affected by the disease (`DdG`, `DuG`)  
   - Where the disease occurs (`DlA`)

2. **Query 2 – Predict New Drugs**  
   Predict new compound–disease pairs by analyzing opposite gene regulation patterns:  
   - A compound up/down-regulates a gene (`CuG`, `CdG`)  
   - A disease’s location up/down-regulates the same gene in the *opposite* direction (`AdG`, `AuG`)  
   - Disease occurs at that location (`DlA`)  
   - Exclude already known drug–disease edges (`CtD`)

---

## Tech Stack
| Component | Purpose |
|------------|----------|
| **Docker** | Runs MongoDB and Neo4j containers |
| **MongoDB** | Stores node data (`nodes.tsv`) with attributes like `id`, `name`, and `kind` |
| **Neo4j** | Stores edge data (`edges.tsv`) representing biological relationships |
| **Python** | Handles data loading and querying |
| **pymongo** | Connects Python to MongoDB |
| **neo4j-driver** | Connects Python to Neo4j |

---
# Design Diagram
```SCSS
nodes.tsv ───────────► MongoDB (node info: id, name)
edges.tsv ───────────► Neo4j (relationships: CtD, CuG, etc.)
                             │
                             ▼
                      Python Queries
              ┌──────────────────────────────┐
              │ get_disease_info()           │──► Query 1
              │ predict_new_drugs()          │──► Query 2
              └──────────────────────────────┘

```
## Setup Instructions

### 1. Start Docker Containers
Launch MongoDB and Neo4j:
`docker-compose up -d`

### 2. Install Python dependencies
 `pip install pymongo neo4j tqdm pandas`


### 3. Load data
```python 
python src/mongo_loader.py
python src/neo4j_loader.py 
```

### 4. Run the CLI
`python src/cli.py`

## You’ll see:
```bash
=== HetioNet CLI ===
1) Query disease info
2) Predict new drugs
q) Quit
```

---

## Project 2: MapReduce Analysis

This project extends the HetioNet analysis with **MapReduce** implementations to answer three specific questions about drugs, genes, and diseases.

### MapReduce Questions Answered

1. **Q1 - Drug-Gene and Drug-Disease Associations**: For each drug, calculate (a) how many genes are associated with it and (b) how many diseases are associated with it. Return top 5 sorted by gene count.

2. **Q2 - Disease Distribution by Drug Count**: Determine how many diseases are linked to exactly 1 drug, exactly 2 drugs, exactly 3 drugs, etc. Return top 5 sorted by number of diseases.

3. **Q3 - Top Drugs by Gene Association**: Identify the drugs with the highest number of associated genes and return the top 5 drug names.

### Running MapReduce Analysis

```bash
# Run MapReduce jobs and generate report
python generate_report.py
```

This will create `PROJECT2_REPORT.md` with detailed analysis results.

### New Files Added (Project 2)

- **`src/mapreduce_jobs.py`**: Core MapReduce implementation with map/reduce functions for each question
- **`generate_report.py`**: Script to execute all MapReduce jobs and generate comprehensive report

### MapReduce Implementation

The MapReduce pattern is implemented with three phases:
1. **Map Phase**: Process each edge and emit (key, value) pairs
2. **Shuffle Phase**: Group values by key
3. **Reduce Phase**: Aggregate values for each key

See `PROJECT2_REPORT.md` for detailed results and analysis.

---

## Acknowledgements
This project was completed independently, with assistance from ChatGPT and Cursor AI for conceptual explanation and debugging guidance.
