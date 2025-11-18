# Project 2: MapReduce Implementation - Summary

## Overview

This document summarizes the MapReduce implementation added to the HetioNet project. The implementation uses the MapReduce programming model to analyze the biological network and answer three specific questions about drug-gene-disease relationships.

## New Files Added

### 1. `src/mapreduce_jobs.py`
**Purpose**: Core MapReduce implementation for analyzing HetioNet edges data.

**Key Components**:
- Generic `run_mapreduce()` function implementing the MapReduce pattern
- Map and Reduce functions for each analysis question:
  - **Q1**: `map_q1_drug_genes()`, `map_q1_drug_diseases()`, `reduce_q1_collect_unique()` - Drug associations
  - **Q2**: `map_q2_disease_drugs()`, `reduce_q2_collect_drugs()` - Disease distribution
  - **Q3**: Uses Q1's drug-gene mapping - Top drugs by genes
- Three question-specific analysis functions:
  - `question1_drug_associations()` - Drug-gene and drug-disease counts
  - `question2_diseases_by_drug_count()` - Disease distribution by drug count
  - `question3_top_drugs_by_genes()` - Top drugs by gene associations

### 2. `generate_report.py`
**Purpose**: Execute all MapReduce jobs and generate a comprehensive markdown report.

**Features**:
- Runs all three MapReduce analysis questions
- Integrates with MongoDB to fetch node names for readable output
- Formats results into tables and structured markdown
- Generates `PROJECT2_REPORT.md` with complete analysis

## MapReduce Questions Answered

### Question 1: Drug Associations (Genes and Diseases)
**Objective**: For each drug, calculate:
- (a) How many genes are associated with it
- (b) How many diseases are associated with it

**Requirements**: 
- Return results sorted by number of associated genes (descending)
- Show only the top 5

**MapReduce Strategy**:
- **Map**: Extract `(drug_id, gene_id)` pairs from `CuG` and `CdG` relationships
- **Map**: Extract `(drug_id, disease_id)` pairs from `CtD` and `CpD` relationships
- **Reduce**: Collect unique genes and diseases for each drug

**Relationship Types Used**:
- `CuG`: Compound up-regulates gene
- `CdG`: Compound down-regulates gene
- `CtD`: Compound treats disease
- `CpD`: Compound palliates disease

**Output**: Top 5 drugs with gene_count and disease_count, sorted by gene_count

### Question 2: Disease Distribution by Drug Count
**Objective**: Determine how many diseases are linked to exactly 1 drug, exactly 2 drugs, exactly 3 drugs, and so on.

**Requirements**:
- Return counts sorted by number of diseases (descending)
- Show the top 5

**MapReduce Strategy**:
- **Map**: Extract `(disease_id, drug_id)` pairs from `CtD` and `CpD` relationships
- **Reduce**: Count unique drugs for each disease
- **Aggregate**: Count how many diseases have exactly N drugs

**Output**: Top 5 drug count categories (e.g., "5 drugs: 100 diseases" means 100 diseases have exactly 5 drugs)

### Question 3: Top Drugs by Gene Associations
**Objective**: Identify the drugs with the highest number of associated genes and return the top 5 drug names.

**MapReduce Strategy**:
- **Map**: Extract `(drug_id, gene_id)` pairs from `CuG` and `CdG` relationships
- **Reduce**: Collect unique genes for each drug
- **Sort**: Rank drugs by number of associated genes (descending)

**Output**: Top 5 drugs with their names and gene counts

## MapReduce Pattern Implementation

The implementation follows the classic MapReduce pattern:

```python
def run_mapreduce(edges_df, map_func, reduce_func):
    # 1. Map Phase: Process each edge
    mapped_results = []
    for row in edges_df.iterrows():
        mapped_results.extend(map_func(row))
    
    # 2. Shuffle Phase: Group by key
    shuffled = defaultdict(list)
    for key, value in mapped_results:
        shuffled[key].append(value)
    
    # 3. Reduce Phase: Aggregate values
    results = {}
    for key, values in shuffled.items():
        results[key] = reduce_func(key, values)
    
    return results
```

## Usage

### Run MapReduce Analysis and Generate Report

```bash
python generate_report.py
```

This will:
1. Execute all three MapReduce analysis questions
2. Query MongoDB for node names to make output readable
3. Generate `PROJECT2_REPORT.md` with detailed results

### Run Individual MapReduce Jobs

```python
from src.mapreduce_jobs import (
    question1_drug_associations,
    question2_diseases_by_drug_count,
    question3_top_drugs_by_genes
)

# Run Question 1
results = question1_drug_associations(top_n=5)
for result in results:
    print(f"{result['drug_id']}: {result['gene_count']} genes, {result['disease_count']} diseases")

# Run Question 2
results = question2_diseases_by_drug_count(top_n=5)
for drug_count, disease_count in results:
    print(f"{drug_count} drugs: {disease_count} diseases")

# Run Question 3
results = question3_top_drugs_by_genes(top_n=5)
for result in results:
    print(f"{result['drug_id']}: {result['gene_count']} genes")
```

## Key Insights

1. **Drug-Gene Connectivity**: Drugs vary significantly in the number of genes they affect, with some drugs having hundreds of gene associations.

2. **Disease-Drug Distribution**: The distribution of diseases by drug count reveals patterns in treatment availability and drug repurposing opportunities.

3. **Highly Connected Drugs**: Drugs with many gene associations may have broad biological effects and could be candidates for further research.

4. **Network Heterogeneity**: The analysis reveals the heterogeneous nature of drug-disease-gene relationships in biological networks.

## Integration with Existing Project

The MapReduce implementation complements the existing Neo4j/MongoDB queries:
- **Project 1**: Uses Neo4j graph queries for specific disease lookups
- **Project 2**: Uses MapReduce for large-scale network analysis and aggregation

Both approaches provide different perspectives on the same HetioNet dataset.

## Technical Details

- **Language**: Python 3
- **Dependencies**: pandas, pymongo
- **Data Source**: `data/edges.tsv` (1.3M+ edges)
- **Pattern**: Custom MapReduce implementation (not using Hadoop/Spark)
- **Scalability**: Can be extended to distributed processing frameworks
