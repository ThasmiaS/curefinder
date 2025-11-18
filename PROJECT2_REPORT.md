# HetioNet MapReduce Analysis Report - Project 2

**Generated:** 2025-11-18 15:10:29

---

## Project Overview

This project implements **MapReduce** algorithms to analyze the HetioNet biological network dataset. 
HetioNet is a heterogeneous network connecting diseases, genes, compounds (drugs), and anatomical locations.

### Technology Stack
- **MapReduce**: Custom Python implementation for distributed data processing
- **Data Source**: HetioNet edges.tsv file (1.3M+ edges)
- **MongoDB**: Node metadata storage (names, types)
- **Python**: pandas for data processing

### MapReduce Implementation

The MapReduce pattern is implemented with three phases:
1. **Map Phase**: Process each edge and emit (key, value) pairs
2. **Shuffle Phase**: Group values by key
3. **Reduce Phase**: Aggregate values for each key

---

## Question 1: Drug Associations (Genes and Diseases)

**Objective**: For each drug, calculate:
- (a) How many genes are associated with it
- (b) How many diseases are associated with it

**MapReduce Strategy**:
- **Map**: Extract drug-gene pairs from `CuG` and `CdG` relationships
- **Map**: Extract drug-disease pairs from `CtD` and `CpD` relationships
- **Reduce**: Collect unique genes and diseases for each drug

**Relationship Types Used**:
- `CuG`: Compound up-regulates gene
- `CdG`: Compound down-regulates gene
- `CtD`: Compound treats disease
- `CpD`: Compound palliates disease

### Results (Top 5 sorted by number of associated genes):

| Rank | Drug ID | Drug Name | Genes | Diseases |
|------|---------|-----------|-------|----------|
| 1 | Compound::DB01074 | Perhexiline | 500 | 0 |
| 2 | Compound::DB00441 | Gemcitabine | 500 | 6 |
| 3 | Compound::DB00390 | Digoxin | 500 | 2 |
| 4 | Compound::DB08865 | Crizotinib | 500 | 1 |
| 5 | Compound::DB06803 | Niclosamide | 500 | 0 |

---

## Question 2: Disease Distribution by Drug Count

**Objective**: Determine how many diseases are linked to exactly 1 drug, 
exactly 2 drugs, exactly 3 drugs, and so on.

**MapReduce Strategy**:
- **Map**: Extract disease-drug pairs from `CtD` and `CpD` relationships
- **Reduce**: Count unique drugs for each disease
- **Aggregate**: Count how many diseases have exactly N drugs

### Results (Top 5 sorted by number of diseases):

| Rank | Number of Drugs | Number of Diseases |
|------|----------------|-------------------|
| 1 | 1 | 10 |
| 2 | 2 | 7 |
| 3 | 11 | 6 |
| 4 | 9 | 6 |
| 5 | 3 | 6 |

**Interpretation**: This shows the distribution of diseases by how many drugs are associated with them. 
For example, if rank 1 shows '5 drugs: 100 diseases', it means 100 diseases are linked to exactly 5 drugs.

---

## Question 3: Top Drugs by Gene Associations

**Objective**: Identify the drugs with the highest number of associated genes 
and return the top 5 drug names.

**MapReduce Strategy**:
- **Map**: Extract drug-gene pairs from `CuG` and `CdG` relationships
- **Reduce**: Collect unique genes for each drug
- **Sort**: Rank drugs by number of associated genes (descending)

### Results (Top 5 drugs by number of associated genes):

| Rank | Drug ID | Drug Name | Gene Count |
|------|---------|----------|------------|
| 1 | Compound::DB08912 | Dabrafenib | 500 |
| 2 | Compound::DB02546 | Vorinostat | 500 |
| 3 | Compound::DB00445 | Epirubicin | 500 |
| 4 | Compound::DB00170 | Menadione | 500 |
| 5 | Compound::DB00947 | Fulvestrant | 500 |

---

## Implementation Details

### New Files Added

1. **`src/mapreduce_jobs.py`**: Core MapReduce implementation
   - Map and Reduce functions for each question
   - Generic `run_mapreduce()` function for executing jobs
   - Three question-specific analysis functions:
     - `question1_drug_associations()`
     - `question2_diseases_by_drug_count()`
     - `question3_top_drugs_by_genes()`

2. **`generate_report.py`**: Report generation script
   - Executes all MapReduce jobs
   - Formats results into markdown report
   - Integrates with MongoDB to fetch node names

### MapReduce Pattern

```python
def run_mapreduce(edges_df, map_func, reduce_func):
    # Map phase
    mapped_results = []
    for row in edges_df.iterrows():
        mapped_results.extend(map_func(row))
    
    # Shuffle phase
    shuffled = defaultdict(list)
    for key, value in mapped_results:
        shuffled[key].append(value)
    
    # Reduce phase
    results = {}
    for key, values in shuffled.items():
        results[key] = reduce_func(key, values)
    return results
```

---

## Key Insights

1. **Drug-Gene Connectivity**: The top drug (Compound::DB01074) is associated with 500 genes, 
   indicating high biological activity across multiple gene pathways.

2. **Disease-Drug Distribution**: 10 diseases are linked to exactly 1 drug(s), 
   showing the most common drug count category in the network.

3. **Top Drug by Genes**: Dabrafenib (Compound::DB08912) has the highest number of gene associations 
   with 500 genes, suggesting it may have broad biological effects.

4. **Network Characteristics**: The analysis reveals the heterogeneous nature of drug-disease-gene 
   relationships, with significant variation in connectivity patterns across the network.

---

## Conclusion

The MapReduce implementation successfully analyzes the HetioNet network, providing insights into:
- Drug-gene and drug-disease association patterns
- Distribution of diseases by drug count
- Identification of highly connected drugs in the network

This analysis demonstrates the power of MapReduce for processing large-scale biological networks 
and extracting meaningful patterns from heterogeneous data.
