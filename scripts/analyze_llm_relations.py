"""Quick analysis of LLM-extracted relations in Neo4j."""
import sys
sys.path.insert(0, "/app/src")

from alejandria.knowledge.neo4j_client import Neo4jClient
from alejandria.config import Settings

s = Settings()
neo = Neo4jClient(s.neo4j_uri, s.neo4j_user, s.neo4j_password)
driver = neo._driver

def run(cypher):
    with driver.session() as session:
        return [dict(r) for r in session.run(cypher)]

print("=== Relations by confidence ===")
for rec in run("MATCH ()-[r]->() WHERE r.confidence IS NOT NULL RETURN r.confidence AS confidence, count(r) AS cnt ORDER BY cnt DESC"):
    print(f"  {rec['confidence']}: {rec['cnt']:,}")

print("\n=== LLM relations by type (top 25) ===")
for rec in run("MATCH ()-[r]->() WHERE r.confidence IN ['llm_high', 'llm_low'] RETURN type(r) AS rel_type, count(r) AS cnt ORDER BY cnt DESC LIMIT 25"):
    print(f"  {rec['rel_type']}: {rec['cnt']:,}")

total = run("MATCH ()-[r]->() WHERE r.confidence IN ['llm_high', 'llm_low'] RETURN count(r) AS total")[0]["total"]
print(f"\nTotal LLM relations: {total:,}")

print("\n=== Sample LLM relations (non-HAS_TITLE) ===")
for rec in run("MATCH (a)-[r]->(b) WHERE r.confidence IN ['llm_high', 'llm_low'] AND type(r) <> 'HAS_TITLE' RETURN a.name AS f, type(r) AS rel, b.name AS t, r.source_ref AS ref ORDER BY rand() LIMIT 15"):
    ref = rec["ref"] or ""
    print(f"  {rec['f']} --[{rec['rel']}]--> {rec['t']}  ({ref})")

print("\n=== HAS_TITLE ratio ===")
for rec in run("MATCH ()-[r]->() WHERE r.confidence IN ['llm_high', 'llm_low'] RETURN type(r) = 'HAS_TITLE' AS is_title, count(r) AS cnt"):
    label = "HAS_TITLE" if rec["is_title"] else "Other"
    print(f"  {label}: {rec['cnt']:,}")

neo.close()
