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

## Acknowledgements
This project was completed independently, with assistance from ChatGPT and Cursor AI for conceptual explanation and debugging guidance.
