# src/mapreduce_jobs.py
"""
MapReduce jobs for analyzing HetioNet data.
These jobs process the edges.tsv file to answer specific questions about drugs, genes, and diseases.
"""

from collections import defaultdict
from typing import Dict, List, Tuple
import pandas as pd


def run_mapreduce(edges_df: pd.DataFrame, map_func, reduce_func) -> Dict:
    """
    Execute a MapReduce job on the edges dataframe.
    
    Args:
        edges_df: DataFrame with edges data
        map_func: Map function that takes a row and returns list of (key, value) tuples
        reduce_func: Reduce function that takes (key, list of values) and returns result
        
    Returns:
        Dictionary mapping keys to reduced values
    """
    # Map phase: Apply map function to each row
    mapped_results = []
    for _, row in edges_df.iterrows():
        mapped_results.extend(map_func(row))
    
    # Shuffle phase: Group by key
    shuffled = defaultdict(list)
    for key, value in mapped_results:
        shuffled[key].append(value)
    
    # Reduce phase: Apply reduce function to each key-value group
    results = {}
    for key, values in shuffled.items():
        result = reduce_func(key, values)
        if isinstance(result, tuple) and len(result) == 2:
            results[result[0]] = result[1]
        else:
            results[key] = result
    
    return results


# ============================================================================
# Question 1: For each drug, calculate (a) genes and (b) diseases associated
# ============================================================================

def map_q1_drug_genes(edge_row: pd.Series) -> List[Tuple[str, str]]:
    """
    Map function for Q1 part (a): Extract drug-gene relationships.
    Emits (drug_id, gene_id) for CuG and CdG relationships.
    
    Args:
        edge_row: A row from edges.tsv with columns: source, metaedge, target
        
    Returns:
        List of (drug_id, gene_id) tuples if relationship is CuG or CdG
    """
    results = []
    rel_type = edge_row['metaedge']
    source = edge_row['source']
    target = edge_row['target']
    
    # Check if this is a compound-gene relationship (CuG or CdG)
    if rel_type in ['CuG', 'CdG']:
        # Source is compound/drug, target is gene
        if source.startswith('Compound::'):
            results.append((source, target))
    
    return results


def map_q1_drug_diseases(edge_row: pd.Series) -> List[Tuple[str, str]]:
    """
    Map function for Q1 part (b): Extract drug-disease relationships.
    Emits (drug_id, disease_id) for CtD and CpD relationships.
    
    Args:
        edge_row: A row from edges.tsv
        
    Returns:
        List of (drug_id, disease_id) tuples if relationship is CtD or CpD
    """
    results = []
    rel_type = edge_row['metaedge']
    source = edge_row['source']
    target = edge_row['target']
    
    # Check if this is a compound-disease relationship (CtD or CpD)
    if rel_type in ['CtD', 'CpD']:
        # Source is compound/drug, target is disease
        if source.startswith('Compound::'):
            results.append((source, target))
    
    return results


def reduce_q1_collect_unique(key: str, values: List[str]) -> Tuple[str, List[str]]:
    """
    Reduce function for Q1: Collect unique genes or diseases for each drug.
    
    Args:
        key: Drug ID
        values: List of gene IDs or disease IDs
        
    Returns:
        (drug_id, list of unique associated IDs)
    """
    unique_ids = list(set(values))
    return (key, unique_ids)


def question1_drug_associations(edges_path: str = "data/edges.tsv", top_n: int = 5) -> List[Dict]:
    """
    Question 1: For each drug, calculate:
    (a) how many genes are associated with it
    (b) how many diseases are associated with it
    
    Return results sorted by number of associated genes (descending), top N.
    
    Args:
        edges_path: Path to edges.tsv file
        top_n: Number of top results to return
        
    Returns:
        List of dictionaries with drug_id, gene_count, disease_count
    """
    print("Question 1: Calculating drug associations (genes and diseases)...")
    edges_df = pd.read_csv(edges_path, sep="\t")
    
    # Part (a): Get drug-gene associations
    drug_genes = run_mapreduce(edges_df, map_q1_drug_genes, reduce_q1_collect_unique)
    
    # Part (b): Get drug-disease associations
    drug_diseases = run_mapreduce(edges_df, map_q1_drug_diseases, reduce_q1_collect_unique)
    
    # Combine results for all drugs
    all_drugs = set(drug_genes.keys()) | set(drug_diseases.keys())
    
    results = []
    for drug_id in all_drugs:
        gene_count = len(drug_genes.get(drug_id, []))
        disease_count = len(drug_diseases.get(drug_id, []))
        results.append({
            'drug_id': drug_id,
            'gene_count': gene_count,
            'disease_count': disease_count
        })
    
    # Sort by gene_count descending and return top N
    results.sort(key=lambda x: x['gene_count'], reverse=True)
    return results[:top_n]


# ============================================================================
# Question 2: Count diseases by number of associated drugs
# ============================================================================

def map_q2_disease_drugs(edge_row: pd.Series) -> List[Tuple[str, str]]:
    """
    Map function for Q2: Extract disease-drug relationships.
    Emits (disease_id, drug_id) for CtD and CpD relationships.
    
    Args:
        edge_row: A row from edges.tsv
        
    Returns:
        List of (disease_id, drug_id) tuples if relationship is CtD or CpD
    """
    results = []
    rel_type = edge_row['metaedge']
    source = edge_row['source']
    target = edge_row['target']
    
    # Check if this is a compound-disease relationship (CtD or CpD)
    if rel_type in ['CtD', 'CpD']:
        # Source is compound/drug, target is disease
        if source.startswith('Compound::') and target.startswith('Disease::'):
            results.append((target, source))  # (disease, drug)
    
    return results


def reduce_q2_collect_drugs(key: str, values: List[str]) -> Tuple[str, int]:
    """
    Reduce function for Q2: Count unique drugs for each disease.
    
    Args:
        key: Disease ID
        values: List of drug IDs
        
    Returns:
        (disease_id, count of unique drugs)
    """
    unique_drugs = set(values)
    return (key, len(unique_drugs))


def question2_diseases_by_drug_count(edges_path: str = "data/edges.tsv", top_n: int = 5) -> List[Tuple[int, int]]:
    """
    Question 2: Determine how many diseases are linked to exactly 1 drug, 
    exactly 2 drugs, exactly 3 drugs, and so on.
    
    Return counts sorted by number of diseases (descending), top N.
    
    Args:
        edges_path: Path to edges.tsv file
        top_n: Number of top results to return
        
    Returns:
        List of (drug_count, disease_count) tuples
    """
    print("Question 2: Counting diseases by number of associated drugs...")
    edges_df = pd.read_csv(edges_path, sep="\t")
    
    # Get drug count for each disease
    disease_drug_counts = run_mapreduce(edges_df, map_q2_disease_drugs, reduce_q2_collect_drugs)
    
    # Count how many diseases have exactly N drugs
    # Key: number of drugs, Value: count of diseases with that many drugs
    drug_count_distribution = defaultdict(int)
    for disease_id, drug_count in disease_drug_counts.items():
        drug_count_distribution[drug_count] += 1
    
    # Convert to list of tuples and sort by disease_count descending
    results = [(drug_count, disease_count) 
               for drug_count, disease_count in drug_count_distribution.items()]
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results[:top_n]


# ============================================================================
# Question 3: Drugs with highest number of associated genes (names)
# ============================================================================

def question3_top_drugs_by_genes(edges_path: str = "data/edges.tsv", top_n: int = 5) -> List[Dict]:
    """
    Question 3: Identify drugs with highest number of associated genes.
    Return top N drug names.
    
    Args:
        edges_path: Path to edges.tsv file
        top_n: Number of top results to return
        
    Returns:
        List of dictionaries with drug_id, drug_name, gene_count
    """
    print("Question 3: Finding drugs with highest number of associated genes...")
    edges_df = pd.read_csv(edges_path, sep="\t")
    
    # Get drug-gene associations (same as Q1 part a)
    drug_genes = run_mapreduce(edges_df, map_q1_drug_genes, reduce_q1_collect_unique)
    
    # Calculate gene counts and sort
    drug_gene_counts = []
    for drug_id, genes in drug_genes.items():
        drug_gene_counts.append({
            'drug_id': drug_id,
            'gene_count': len(genes)
        })
    
    # Sort by gene_count descending
    drug_gene_counts.sort(key=lambda x: x['gene_count'], reverse=True)
    
    return drug_gene_counts[:top_n]


if __name__ == "__main__":
    # Run all questions
    print("=" * 60)
    print("HetioNet MapReduce Analysis - Project 2")
    print("=" * 60)
    
    # Question 1
    q1_results = question1_drug_associations(top_n=5)
    print("\nQ1: Top 5 drugs by number of associated genes:")
    print(f"{'Rank':<6} {'Drug ID':<30} {'Genes':<10} {'Diseases':<10}")
    print("-" * 60)
    for rank, result in enumerate(q1_results, 1):
        print(f"{rank:<6} {result['drug_id']:<30} {result['gene_count']:<10} {result['disease_count']:<10}")
    
    # Question 2
    q2_results = question2_diseases_by_drug_count(top_n=5)
    print("\nQ2: Top 5 drug count categories (by number of diseases):")
    print(f"{'Rank':<6} {'Drug Count':<15} {'Disease Count':<15}")
    print("-" * 40)
    for rank, (drug_count, disease_count) in enumerate(q2_results, 1):
        print(f"{rank:<6} {drug_count:<15} {disease_count:<15}")
    
    # Question 3
    q3_results = question3_top_drugs_by_genes(top_n=5)
    print("\nQ3: Top 5 drugs by number of associated genes:")
    print(f"{'Rank':<6} {'Drug ID':<30} {'Gene Count':<15}")
    print("-" * 55)
    for rank, result in enumerate(q3_results, 1):
        print(f"{rank:<6} {result['drug_id']:<30} {result['gene_count']:<15}")
