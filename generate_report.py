# generate_report.py
"""
Generate a comprehensive report from MapReduce analysis of HetioNet data.
Answers the three specific questions from Project 2.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mapreduce_jobs import (
    question1_drug_associations,
    question2_diseases_by_drug_count,
    question3_top_drugs_by_genes
)
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017/"


def get_node_name(node_id: str) -> str:
    """Get the name of a node from MongoDB."""
    try:
        mongo = MongoClient(MONGO_URI)
        db = mongo["hetio"]
        doc = db.nodes.find_one({"id": node_id})
        if doc:
            return doc.get("name", node_id)
        return node_id
    except Exception as e:
        # If MongoDB is not available, just return the ID
        return node_id


def generate_report(output_file: str = "PROJECT2_REPORT.md"):
    """Generate a comprehensive report of the MapReduce analysis."""
    
    print("Generating MapReduce analysis report...")
    print("=" * 60)
    
    report_lines = []
    report_lines.append("# HetioNet MapReduce Analysis Report - Project 2")
    report_lines.append("")
    report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Project Overview
    report_lines.append("## Project Overview")
    report_lines.append("")
    report_lines.append("This project implements **MapReduce** algorithms to analyze the HetioNet biological network dataset. ")
    report_lines.append("HetioNet is a heterogeneous network connecting diseases, genes, compounds (drugs), and anatomical locations.")
    report_lines.append("")
    report_lines.append("### Technology Stack")
    report_lines.append("- **MapReduce**: Custom Python implementation for distributed data processing")
    report_lines.append("- **Data Source**: HetioNet edges.tsv file (1.3M+ edges)")
    report_lines.append("- **MongoDB**: Node metadata storage (names, types)")
    report_lines.append("- **Python**: pandas for data processing")
    report_lines.append("")
    report_lines.append("### MapReduce Implementation")
    report_lines.append("")
    report_lines.append("The MapReduce pattern is implemented with three phases:")
    report_lines.append("1. **Map Phase**: Process each edge and emit (key, value) pairs")
    report_lines.append("2. **Shuffle Phase**: Group values by key")
    report_lines.append("3. **Reduce Phase**: Aggregate values for each key")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Question 1
    report_lines.append("## Question 1: Drug Associations (Genes and Diseases)")
    report_lines.append("")
    report_lines.append("**Objective**: For each drug, calculate:")
    report_lines.append("- (a) How many genes are associated with it")
    report_lines.append("- (b) How many diseases are associated with it")
    report_lines.append("")
    report_lines.append("**MapReduce Strategy**:")
    report_lines.append("- **Map**: Extract drug-gene pairs from `CuG` and `CdG` relationships")
    report_lines.append("- **Map**: Extract drug-disease pairs from `CtD` and `CpD` relationships")
    report_lines.append("- **Reduce**: Collect unique genes and diseases for each drug")
    report_lines.append("")
    report_lines.append("**Relationship Types Used**:")
    report_lines.append("- `CuG`: Compound up-regulates gene")
    report_lines.append("- `CdG`: Compound down-regulates gene")
    report_lines.append("- `CtD`: Compound treats disease")
    report_lines.append("- `CpD`: Compound palliates disease")
    report_lines.append("")
    
    q1_results = question1_drug_associations(top_n=5)
    report_lines.append("### Results (Top 5 sorted by number of associated genes):")
    report_lines.append("")
    report_lines.append("| Rank | Drug ID | Drug Name | Genes | Diseases |")
    report_lines.append("|------|---------|-----------|-------|----------|")
    for rank, result in enumerate(q1_results, 1):
        drug_id = result['drug_id']
        drug_name = get_node_name(drug_id)
        gene_count = result['gene_count']
        disease_count = result['disease_count']
        report_lines.append(f"| {rank} | {drug_id} | {drug_name} | {gene_count} | {disease_count} |")
    report_lines.append("")
    
    # Question 2
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## Question 2: Disease Distribution by Drug Count")
    report_lines.append("")
    report_lines.append("**Objective**: Determine how many diseases are linked to exactly 1 drug, ")
    report_lines.append("exactly 2 drugs, exactly 3 drugs, and so on.")
    report_lines.append("")
    report_lines.append("**MapReduce Strategy**:")
    report_lines.append("- **Map**: Extract disease-drug pairs from `CtD` and `CpD` relationships")
    report_lines.append("- **Reduce**: Count unique drugs for each disease")
    report_lines.append("- **Aggregate**: Count how many diseases have exactly N drugs")
    report_lines.append("")
    
    q2_results = question2_diseases_by_drug_count(top_n=5)
    report_lines.append("### Results (Top 5 sorted by number of diseases):")
    report_lines.append("")
    report_lines.append("| Rank | Number of Drugs | Number of Diseases |")
    report_lines.append("|------|----------------|-------------------|")
    for rank, (drug_count, disease_count) in enumerate(q2_results, 1):
        report_lines.append(f"| {rank} | {drug_count} | {disease_count} |")
    report_lines.append("")
    report_lines.append("**Interpretation**: This shows the distribution of diseases by how many drugs are associated with them. ")
    report_lines.append("For example, if rank 1 shows '5 drugs: 100 diseases', it means 100 diseases are linked to exactly 5 drugs.")
    report_lines.append("")
    
    # Question 3
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## Question 3: Top Drugs by Gene Associations")
    report_lines.append("")
    report_lines.append("**Objective**: Identify the drugs with the highest number of associated genes ")
    report_lines.append("and return the top 5 drug names.")
    report_lines.append("")
    report_lines.append("**MapReduce Strategy**:")
    report_lines.append("- **Map**: Extract drug-gene pairs from `CuG` and `CdG` relationships")
    report_lines.append("- **Reduce**: Collect unique genes for each drug")
    report_lines.append("- **Sort**: Rank drugs by number of associated genes (descending)")
    report_lines.append("")
    
    q3_results = question3_top_drugs_by_genes(top_n=5)
    report_lines.append("### Results (Top 5 drugs by number of associated genes):")
    report_lines.append("")
    report_lines.append("| Rank | Drug ID | Drug Name | Gene Count |")
    report_lines.append("|------|---------|----------|------------|")
    for rank, result in enumerate(q3_results, 1):
        drug_id = result['drug_id']
        drug_name = get_node_name(drug_id)
        gene_count = result['gene_count']
        report_lines.append(f"| {rank} | {drug_id} | {drug_name} | {gene_count} |")
    report_lines.append("")
    
    # Implementation Details
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## Implementation Details")
    report_lines.append("")
    report_lines.append("### New Files Added")
    report_lines.append("")
    report_lines.append("1. **`src/mapreduce_jobs.py`**: Core MapReduce implementation")
    report_lines.append("   - Map and Reduce functions for each question")
    report_lines.append("   - Generic `run_mapreduce()` function for executing jobs")
    report_lines.append("   - Three question-specific analysis functions:")
    report_lines.append("     - `question1_drug_associations()`")
    report_lines.append("     - `question2_diseases_by_drug_count()`")
    report_lines.append("     - `question3_top_drugs_by_genes()`")
    report_lines.append("")
    report_lines.append("2. **`generate_report.py`**: Report generation script")
    report_lines.append("   - Executes all MapReduce jobs")
    report_lines.append("   - Formats results into markdown report")
    report_lines.append("   - Integrates with MongoDB to fetch node names")
    report_lines.append("")
    report_lines.append("### MapReduce Pattern")
    report_lines.append("")
    report_lines.append("```python")
    report_lines.append("def run_mapreduce(edges_df, map_func, reduce_func):")
    report_lines.append("    # Map phase")
    report_lines.append("    mapped_results = []")
    report_lines.append("    for row in edges_df.iterrows():")
    report_lines.append("        mapped_results.extend(map_func(row))")
    report_lines.append("    ")
    report_lines.append("    # Shuffle phase")
    report_lines.append("    shuffled = defaultdict(list)")
    report_lines.append("    for key, value in mapped_results:")
    report_lines.append("        shuffled[key].append(value)")
    report_lines.append("    ")
    report_lines.append("    # Reduce phase")
    report_lines.append("    results = {}")
    report_lines.append("    for key, values in shuffled.items():")
    report_lines.append("        results[key] = reduce_func(key, values)")
    report_lines.append("    return results")
    report_lines.append("```")
    report_lines.append("")
    
    # Key Insights
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## Key Insights")
    report_lines.append("")
    
    # Insights from Q1
    if q1_results:
        top_drug = q1_results[0]
        report_lines.append(f"1. **Drug-Gene Connectivity**: The top drug ({top_drug['drug_id']}) is associated with {top_drug['gene_count']} genes, ")
        report_lines.append(f"   indicating high biological activity across multiple gene pathways.")
        report_lines.append("")
    
    # Insights from Q2
    if q2_results:
        top_category = q2_results[0]
        report_lines.append(f"2. **Disease-Drug Distribution**: {top_category[1]} diseases are linked to exactly {top_category[0]} drug(s), ")
        report_lines.append(f"   showing the most common drug count category in the network.")
        report_lines.append("")
    
    # Insights from Q3
    if q3_results:
        top_drug_q3 = q3_results[0]
        drug_name = get_node_name(top_drug_q3['drug_id'])
        report_lines.append(f"3. **Top Drug by Genes**: {drug_name} ({top_drug_q3['drug_id']}) has the highest number of gene associations ")
        report_lines.append(f"   with {top_drug_q3['gene_count']} genes, suggesting it may have broad biological effects.")
        report_lines.append("")
    
    report_lines.append("4. **Network Characteristics**: The analysis reveals the heterogeneous nature of drug-disease-gene ")
    report_lines.append("   relationships, with significant variation in connectivity patterns across the network.")
    report_lines.append("")
    
    # Conclusion
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## Conclusion")
    report_lines.append("")
    report_lines.append("The MapReduce implementation successfully analyzes the HetioNet network, providing insights into:")
    report_lines.append("- Drug-gene and drug-disease association patterns")
    report_lines.append("- Distribution of diseases by drug count")
    report_lines.append("- Identification of highly connected drugs in the network")
    report_lines.append("")
    report_lines.append("This analysis demonstrates the power of MapReduce for processing large-scale biological networks ")
    report_lines.append("and extracting meaningful patterns from heterogeneous data.")
    report_lines.append("")
    
    # Write report
    report_content = "\n".join(report_lines)
    with open(output_file, 'w') as f:
        f.write(report_content)
    
    print(f"\n✅ Report generated: {output_file}")
    print(f"   Total lines: {len(report_lines)}")
    
    return output_file


if __name__ == "__main__":
    generate_report()
