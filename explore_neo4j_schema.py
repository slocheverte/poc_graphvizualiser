"""
Script pour explorer le schéma réel de la base Neo4j
"""
from neo4j import GraphDatabase
import json

# Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4jdb111"
NEO4J_DATABASE = "neo4j"


def explore_schema():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    print("="*70)
    print("NEO4J SCHEMA EXPLORATION")
    print("="*70)
    
    with driver.session(database=NEO4J_DATABASE) as session:
        
        # 1. Compter les nœuds
        print("\n📊 NODE COUNT:")
        result = session.run("MATCH (n) RETURN count(n) as count")
        node_count = result.single()["count"]
        print(f"   Total nodes: {node_count}")
        
        # 2. Labels des nœuds
        print("\n🏷️  NODE LABELS:")
        result = session.run("CALL db.labels()")
        labels = [record["label"] for record in result]
        for label in labels:
            count_result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
            count = count_result.single()["count"]
            print(f"   - {label}: {count} nodes")
        
        # 3. Types de relations
        print("\n🔗 RELATIONSHIP TYPES:")
        result = session.run("CALL db.relationshipTypes()")
        rel_types = [record["relationshipType"] for record in result]
        for rel_type in rel_types:
            count_result = session.run(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count")
            count = count_result.single()["count"]
            print(f"   - {rel_type}: {count} relationships")
        
        # 4. Exemples de nœuds pour chaque label
        print("\n📝 SAMPLE NODES (first 2 of each type):")
        for label in labels[:5]:  # Limiter aux 5 premiers labels
            print(f"\n   {label}:")
            result = session.run(f"MATCH (n:{label}) RETURN n LIMIT 2")
            for i, record in enumerate(result, 1):
                node = record["n"]
                props = dict(node)
                print(f"      #{i}: {json.dumps(props, indent=8, default=str)[:200]}...")
        
        # 5. Schéma des relations (quels labels connectés par quelles relations)
        print("\n🌐 RELATIONSHIP PATTERNS:")
        result = session.run("""
            MATCH (a)-[r]->(b)
            WITH labels(a)[0] as fromLabel, type(r) as relType, labels(b)[0] as toLabel, count(*) as count
            RETURN fromLabel, relType, toLabel, count
            ORDER BY count DESC
            LIMIT 20
        """)
        for record in result:
            print(f"   ({record['fromLabel']})-[:{record['relType']}]->({record['toLabel']}) : {record['count']} times")
        
        # 6. Chercher les devices spécifiques mentionnés dans les requêtes
        print("\n🔍 SEARCHING FOR SPECIFIC DEVICES:")
        devices_to_find = [
            "w1clictxxa2301.aepc.com",
            "s1clisgbd60434.aepc.com",
            "VwLogibecDCR01",
            "DEV3"
        ]
        for device in devices_to_find:
            result = session.run(f"""
                MATCH (n)
                WHERE n.label = $device OR n.id = $device OR n.name = $device
                RETURN labels(n) as labels, properties(n) as props
                LIMIT 1
            """, device=device)
            record = result.single()
            if record:
                print(f"   ✅ Found {device}: {record['labels']} - {str(record['props'])[:100]}")
            else:
                print(f"   ❌ Not found: {device}")
        
        # 7. Vérifier les labels Internet, VIP, Subnet, Policy
        print("\n🎯 CHECKING KEY LABELS:")
        key_labels = ["Internet", "VIP", "Subnet", "Policy", "Device"]
        for label in key_labels:
            result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
            count = result.single()["count"]
            status = "✅" if count > 0 else "❌"
            print(f"   {status} {label}: {count} nodes")
    
    driver.close()
    print("\n" + "="*70)
    print("EXPLORATION COMPLETE")
    print("="*70)


if __name__ == "__main__":
    explore_schema()
