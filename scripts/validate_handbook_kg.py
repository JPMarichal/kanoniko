#!/usr/bin/env python3
"""P10 Phase 3 — Validate handbook KG model integrity.

Runs Cypher queries against Neo4j to verify the handbook organizational
model is correctly loaded and structurally sound.

Usage:
  python scripts/validate_handbook_kg.py [--uri bolt://localhost:7687]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def validate(uri: str, user: str, password: str) -> dict[str, dict]:
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(uri, auth=(user, password))
    results: dict[str, dict] = {}

    with driver.session() as session:
        # 1. Every unit should have a presiding role
        result = session.run(
            "MATCH (u:Entity {type: 'unit'}) "
            "OPTIONAL MATCH (r:Entity {type: 'role'})-[:PRESIDES_OVER]->(u) "
            "RETURN u.name AS unit, r.name AS presiding_role "
            "ORDER BY u.name"
        )
        units = []
        orphan_units = []
        for rec in result:
            units.append({"unit": rec["unit"], "role": rec["presiding_role"]})
            if not rec["presiding_role"]:
                orphan_units.append(rec["unit"])
        results["units_with_presiding_role"] = {
            "total": len(units),
            "orphans": orphan_units,
            "pass": len(orphan_units) == 0,
        }

        # 2. Ordinance prerequisite chain is acyclic
        result = session.run(
            "MATCH path = (o1:Entity {type: 'ordinance'})-[:PREREQUISITE_FOR*1..10]->(o2:Entity {type: 'ordinance'}) "
            "WHERE o1 = o2 "
            "RETURN [n IN nodes(path) | n.name] AS cycle "
            "LIMIT 5"
        )
        cycles = [rec["cycle"] for rec in result]
        results["ordinance_chain_acyclic"] = {
            "cycles_found": cycles,
            "pass": len(cycles) == 0,
        }

        # 3. All roles have at least one PRESIDES_OVER or REPORTS_TO
        result = session.run(
            "MATCH (r:Entity {type: 'role'}) "
            "OPTIONAL MATCH (r)-[:PRESIDES_OVER]->() "
            "OPTIONAL MATCH (r)-[:REPORTS_TO]->() "
            "WITH r, count{ (r)-[:PRESIDES_OVER]->() } AS presides, "
            "     count{ (r)-[:REPORTS_TO]->() } AS reports "
            "WHERE presides = 0 AND reports = 0 "
            "RETURN r.name AS role ORDER BY r.name"
        )
        disconnected = [rec["role"] for rec in result]
        results["roles_connected"] = {
            "disconnected": disconnected,
            "pass": len(disconnected) == 0,
        }

        # 4. Authority chain — who can authorize what
        result = session.run(
            "MATCH (r:Entity {type: 'role'})-[:AUTHORIZED_TO_PERFORM]->(o:Entity {type: 'ordinance'}) "
            "RETURN r.name AS role, collect(o.name) AS ordinances "
            "ORDER BY r.name"
        )
        auth_chain = {rec["role"]: rec["ordinances"] for rec in result}
        results["authority_chain"] = {
            "roles_with_auth": len(auth_chain),
            "detail": auth_chain,
            "pass": len(auth_chain) > 0,
        }

        # 5. Reporting chain depth
        result = session.run(
            "MATCH path = (r1:Entity {type: 'role'})-[:REPORTS_TO*1..5]->(r2:Entity {type: 'role'}) "
            "RETURN r1.name AS from_role, r2.name AS to_role, length(path) AS depth "
            "ORDER BY depth DESC LIMIT 10"
        )
        chains = [{"from": rec["from_role"], "to": rec["to_role"], "depth": rec["depth"]} for rec in result]
        results["reporting_chains"] = {
            "longest_chains": chains,
            "pass": True,
        }

        # 6. Count summary
        for entity_type in ("role", "unit", "ordinance", "meeting", "fund", "program"):
            count = session.run(
                "MATCH (e:Entity {type: $type}) RETURN count(e) AS c",
                type=entity_type,
            ).single()["c"]
            results[f"count_{entity_type}"] = {"count": count}

        # Handbook relation counts
        for rel_type in ("PRESIDES_OVER", "REPORTS_TO", "AUTHORIZED_TO_PERFORM",
                         "PREREQUISITE_FOR", "MANAGES_FUND", "CONDUCTS_INTERVIEW", "MEMBER_OF"):
            count = session.run(
                f"MATCH ()-[r:{rel_type}]->() RETURN count(r) AS c"
            ).single()["c"]
            results[f"rel_{rel_type}"] = {"count": count}

    driver.close()
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate handbook KG model")
    parser.add_argument("--uri", default="bolt://localhost:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="alejandria")
    args = parser.parse_args()

    results = validate(args.uri, args.user, args.password)

    print("\n=== Handbook KG Validation ===\n")

    # Entity counts
    print("Entity counts:")
    for key in sorted(results):
        if key.startswith("count_"):
            name = key.replace("count_", "")
            print(f"  {name}: {results[key]['count']}")

    # Relation counts
    print("\nRelation counts:")
    for key in sorted(results):
        if key.startswith("rel_"):
            name = key.replace("rel_", "")
            print(f"  {name}: {results[key]['count']}")

    # Validation checks
    print("\nValidation checks:")
    checks = ["units_with_presiding_role", "ordinance_chain_acyclic",
              "roles_connected", "authority_chain", "reporting_chains"]
    all_pass = True
    for check in checks:
        if check in results:
            status = "✅ PASS" if results[check].get("pass") else "❌ FAIL"
            print(f"  {check}: {status}")
            if not results[check].get("pass"):
                all_pass = False
                detail = {k: v for k, v in results[check].items() if k != "pass"}
                for k, v in detail.items():
                    print(f"    {k}: {v}")

    # Authority detail
    if "authority_chain" in results and results["authority_chain"].get("detail"):
        print("\nAuthority chain:")
        for role, ords in results["authority_chain"]["detail"].items():
            print(f"  {role} → {', '.join(ords)}")

    print(f"\nOverall: {'✅ ALL PASS' if all_pass else '❌ SOME CHECKS FAILED'}")


if __name__ == "__main__":
    main()
