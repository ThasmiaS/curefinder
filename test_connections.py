# test_connections.py
from pymongo import MongoClient
from neo4j import GraphDatabase
import pandas as pd

# MongoDB test
mongo_client = MongoClient("mongodb://localhost:27017/")
print("MongoDB Databases:", mongo_client.list_database_names())

# Neo4j test
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))
print("Neo4j connection successful!")

# Pandas test
df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["A", "B", "C"]})
print(df)
