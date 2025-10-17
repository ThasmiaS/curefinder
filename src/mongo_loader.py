# src/mongo_loader.py
from pymongo import MongoClient, UpdateOne, InsertOne
import pandas as pd
import sys

BATCH_SIZE = 5000

def load_nodes(mongo_uri="mongodb://localhost:27017/", db_name="hetio", path="data/nodes.tsv"):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    db.nodes.create_index("id", unique=True)
    db.nodes.create_index("kind")

    nodes = pd.read_csv(path, sep="\t")
    ops = []
    total = 0
    for _, row in nodes.iterrows():
        doc_id = row.get("id") or row.get("Id")
        if not doc_id:
            continue
        doc = {"id": doc_id, "name": row.get("name", ""), "kind": row.get("kind", "")}
        ops.append(UpdateOne({"id": doc_id}, {"$set": doc}, upsert=True))
        if len(ops) >= BATCH_SIZE:
            db.nodes.bulk_write(ops, ordered=False)
            total += len(ops)
            ops = []
    if ops:
        db.nodes.bulk_write(ops, ordered=False)
        total += len(ops)
    print(f"✅ Loaded/updated {total} nodes into MongoDB '{db_name}.nodes'")


if __name__ == "__main__":
    load_nodes()
