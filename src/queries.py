# src/queries.py
from neo4j import GraphDatabase
from pymongo import MongoClient

NEO_URI = "bolt://localhost:7687"
NEO_USER = "neo4j"
NEO_PASS = "password"
MONGO_URI = "mongodb://localhost:27017/"

def get_disease_info(disease_id):
    """
    Given a disease ID get:
      - disease name
      - drugs that treat/ palliate it
      - genes involved (up/down regulated)
      - locations where it occurs

    Uses:
      CtD = Compound treats disease
      CpD = Compound palliates disease
      DdG = Disease down regs gene
      DuG = Disease up regs gene
      DlA = Disease localizes to anatomy
    """

    #connect to MongoDB
    mongo = MongoClient(MONGO_URI)
    db = mongo["hetio"]

    #get disease name
    disease_doc = db.nodes.find_one({"id": disease_id}) or {}
    disease_name = disease_doc.get("name", "Unknown")

    # connect to Neo4j
    driver = GraphDatabase.driver(NEO_URI, auth=(NEO_USER, NEO_PASS))

    # 1 combined Cypher query
    query = """
    MATCH (d:Entity {id: $d_id})
    OPTIONAL MATCH (c1:Entity)-[:CtD]->(d)
    OPTIONAL MATCH (c2:Entity)-[:CpD]->(d)
    OPTIONAL MATCH (d)-[:DdG|DuG]->(g:Entity)
    OPTIONAL MATCH (d)-[:DlA]->(a:Entity)
    RETURN 
      collect(DISTINCT c1.id) + collect(DISTINCT c2.id) AS drug_ids,
      collect(DISTINCT g.id) AS gene_ids,
      collect(DISTINCT a.id) AS location_ids
    """

    with driver.session() as s:
        rec = s.run(query, d_id=disease_id).single()
    driver.close()

    # get ID lists 
    drug_ids = rec["drug_ids"] or []
    gene_ids = rec["gene_ids"] or []
    loc_ids  = rec["location_ids"] or []

    # helper fx to get names from MongoDB
    def get_names(ids):
        if not ids:
            return []
        return [doc["name"] for doc in db.nodes.find({"id": {"$in": ids}}, {"name": 1})]

    # convert IDs to names
    drugs = get_names(drug_ids)
    genes = get_names(gene_ids)
    locations = get_names(loc_ids)

    return {
        "disease_id": disease_id,
        "disease_name": disease_name,
        "drugs": drugs,
        "genes": genes,
        "locations": locations
    }


def predict_new_drugs():
    """Predict new compound–disease pairs based on opposite gene regulation."""
    driver = GraphDatabase.driver(NEO_URI, auth=(NEO_USER, NEO_PASS))
    q = """
    MATCH (d:Entity)-[:DlA]->(loc:Entity)
    MATCH (loc)-[lg:AdG|AuG]->(g:Entity)
    MATCH (c:Entity)-[cg:CuG|CdG]->(g)
    WHERE 
        ((type(cg) = 'CuG' AND type(lg) = 'AdG') OR
        (type(cg) = 'CdG' AND type(lg) = 'AuG'))
        AND NOT (c)-[:CtD]->(d)
    RETURN DISTINCT 
        d.id AS disease, 
        c.id AS compound, 
        collect(DISTINCT g.id) AS genes

    LIMIT 5
    """
    results = []
    with driver.session() as s:
        for r in s.run(q):
            results.append({
                "compound": r["compound"],
                "disease": r["disease"],
                "genes": r["genes"]
            })
    driver.close()
    return results
