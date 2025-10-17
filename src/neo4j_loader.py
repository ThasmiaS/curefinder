from neo4j import GraphDatabase
import pandas as pd
from tqdm import tqdm
import re  #cleaning relationship names

NEO_URI = "bolt://localhost:7687"
NEO_USER = "neo4j"
NEO_PASS = "password"

def sanitize_rel(rel_name: str) -> str:
    """Replace invalid characters for Neo4j relationship types with underscores."""
    return re.sub(r"[^A-Za-z0-9_]", "_", rel_name)

def load_edges(uri=NEO_URI, user=NEO_USER, password=NEO_PASS, path="data/edges.tsv", batch_size=1000):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    edges = pd.read_csv(path, sep="\t")

    with driver.session() as session:
        unique_rels = edges["metaedge"].unique()
        print("Found relationship types:", unique_rels)

        for rel in unique_rels:
            clean_rel = sanitize_rel(rel)  # Clean name
            rel_edges = edges[edges["metaedge"] == rel]
            print(f"\nLoading {len(rel_edges)} edges of type {rel} (stored as {clean_rel}) ...")

            for i in tqdm(range(0, len(rel_edges), batch_size), desc=rel):
                batch = rel_edges.iloc[i : i + batch_size]
                data = batch.to_dict("records")

                query = f"""
                UNWIND $rows AS row
                MERGE (a:Entity {{id: row.source}})
                MERGE (b:Entity {{id: row.target}})
                MERGE (a)-[:{clean_rel}]->(b)
                """
                session.run(query, rows=data)

    driver.close()
    print("✅ All edges loaded into Neo4j.")

if __name__ == "__main__":
    load_edges()
