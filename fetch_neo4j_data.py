"""
Script pour récupérer les données depuis Neo4j et générer les fichiers JSON pour les use cases
"""
import json
from neo4j import GraphDatabase
from datetime import datetime
from typing import Dict, List, Any

# === CONFIGURATION NEO4J - À REMPLIR ===
NEO4J_URI = "bolt://localhost:7687"  # ou neo4j://localhost:7687
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4jdb111"
NEO4J_DATABASE = "neo4j"  # ou autre nom de database

# Use cases à traiter avec les VRAIS labels et relations Neo4j
USE_CASES = [
    {
        "id": "uc1_exposed_to_device",
        "name": "Exposed Device to Specific Device",
        "cypher": """MATCH path = (m:Internet)<-[:HAS_TARGET]-(policy:Policy)-[:HAS_SOURCE]->(source)
WHERE source:Device OR source:IPAddress OR source:Subnet OR source:Group
RETURN m, policy, source, path
LIMIT 20""",
        "output_file": "data/uc1_exposed_to_device_response.json"
    },
    {
        "id": "uc5_top_subnets",
        "name": "Top Subnets by Device Count",
        "cypher": """MATCH (d)-[:BELONGS_TO]->(s:Subnet)
WHERE d:Device OR d:IPAddress
WITH s, count(d) AS deviceCount
ORDER BY deviceCount DESC
LIMIT 10
RETURN s, deviceCount""",
        "output_file": "data/uc5_top_subnets_response.json"
    },
    {
        "id": "uc6_path_between_devices",
        "name": "Path Between Two Specific Devices",
        "cypher": """// Stratégie: Trouver un chemin via Subnet et/ou Policies
MATCH (start:IPAddress {label: "w1clictxxa2301.aepc.com"})
MATCH (end:IPAddress {label: "s1clisgbd60434.aepc.com"})

// Option 1: Même subnet
OPTIONAL MATCH path1 = (start)-[:BELONGS_TO]->(subnet:Subnet)<-[:BELONGS_TO]-(end)

// Option 2: Via policies qui connectent les subnets
OPTIONAL MATCH path2 = (start)-[:BELONGS_TO]->(s1:Subnet)<-[:HAS_SOURCE|HAS_TARGET]-(p:Policy)-[:HAS_SOURCE|HAS_TARGET]->(s2:Subnet)<-[:BELONGS_TO]-(end)

// Option 3: Start et end dans des groupes/subnets liés par une policy
OPTIONAL MATCH path3 = (start)-[:BELONGS_TO]->(s1:Subnet)<-[:HAS_SOURCE]-(p:Policy)-[:HAS_TARGET]->(s2:Subnet)<-[:BELONGS_TO]-(end)

// Retourner tous les chemins trouvés
WITH start, end, 
     CASE WHEN path1 IS NOT NULL THEN path1 ELSE NULL END AS directPath,
     CASE WHEN path2 IS NOT NULL THEN path2 ELSE NULL END AS policyPath,
     CASE WHEN path3 IS NOT NULL THEN path3 ELSE NULL END AS sourceTargetPath

// Collecter tous les chemins non-null
WITH start, end, [p IN [directPath, policyPath, sourceTargetPath] WHERE p IS NOT NULL] AS paths

UNWIND paths AS path
RETURN start, end, path
LIMIT 10""",
        "output_file": "data/uc6_path_between_devices_response.json"
    }
]


class Neo4jDataFetcher:
    def __init__(self, uri: str, user: str, password: str, database: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
    
    def close(self):
        self.driver.close()
    
    def node_to_dict(self, node) -> Dict[str, Any]:
        """Convertir un noeud Neo4j en dictionnaire"""
        return {
            "id": str(node.element_id if hasattr(node, 'element_id') else node.id),
            "labels": list(node.labels),
            "properties": dict(node)
        }
    
    def relationship_to_dict(self, rel) -> Dict[str, Any]:
        """Convertir une relation Neo4j en dictionnaire"""
        return {
            "id": str(rel.element_id if hasattr(rel, 'element_id') else rel.id),
            "type": rel.type,
            "start_id": str(rel.start_node.element_id if hasattr(rel.start_node, 'element_id') else rel.start_node.id),
            "end_id": str(rel.end_node.element_id if hasattr(rel.end_node, 'element_id') else rel.end_node.id),
            "properties": dict(rel)
        }
    
    def extract_nodes_and_relationships(self, records) -> tuple[List[Dict], List[Dict]]:
        """Extraire tous les noeuds et relations des résultats"""
        nodes_dict = {}
        relationships_dict = {}
        
        for record in records:
            for key, value in record.items():
                # Traiter les chemins (paths)
                if hasattr(value, 'nodes') and hasattr(value, 'relationships'):
                    for node in value.nodes:
                        node_id = str(node.element_id if hasattr(node, 'element_id') else node.id)
                        if node_id not in nodes_dict:
                            nodes_dict[node_id] = self.node_to_dict(node)
                    for rel in value.relationships:
                        rel_id = str(rel.element_id if hasattr(rel, 'element_id') else rel.id)
                        if rel_id not in relationships_dict:
                            relationships_dict[rel_id] = self.relationship_to_dict(rel)
                
                # Traiter les listes de noeuds
                elif isinstance(value, list):
                    for item in value:
                        if hasattr(item, 'labels'):  # C'est un noeud
                            node_id = str(item.element_id if hasattr(item, 'element_id') else item.id)
                            if node_id not in nodes_dict:
                                nodes_dict[node_id] = self.node_to_dict(item)
                        elif hasattr(item, 'type'):  # C'est une relation
                            rel_id = str(item.element_id if hasattr(item, 'element_id') else item.id)
                            if rel_id not in relationships_dict:
                                relationships_dict[rel_id] = self.relationship_to_dict(item)
                
                # Traiter un seul noeud
                elif hasattr(value, 'labels'):
                    node_id = str(value.element_id if hasattr(value, 'element_id') else value.id)
                    if node_id not in nodes_dict:
                        nodes_dict[node_id] = self.node_to_dict(value)
                
                # Traiter une seule relation
                elif hasattr(value, 'type'):
                    rel_id = str(value.element_id if hasattr(value, 'element_id') else value.id)
                    if rel_id not in relationships_dict:
                        relationships_dict[rel_id] = self.relationship_to_dict(value)
        
        return list(nodes_dict.values()), list(relationships_dict.values())
    
    def execute_query(self, cypher: str) -> tuple[List[Dict], List[Dict], int]:
        """Exécuter une requête Cypher et retourner nodes, relationships et count"""
        with self.driver.session(database=self.database) as session:
            result = session.run(cypher)
            records = list(result)
            nodes, relationships = self.extract_nodes_and_relationships(records)
            return nodes, relationships, len(records)
    
    def fetch_and_save_use_case(self, use_case: Dict) -> bool:
        """Récupérer les données pour un use case et sauvegarder en JSON"""
        print(f"\n{'='*60}")
        print(f"Processing: {use_case['name']}")
        print(f"Query: {use_case['cypher'][:100]}...")
        
        try:
            nodes, relationships, record_count = self.execute_query(use_case['cypher'])
            
            # Créer la structure JSON
            data = {
                "analysis": {
                    "status": "success",
                    "summary": f"{use_case['name']} - Retrieved from Neo4j",
                    "timestamp": datetime.now().isoformat(),
                    "record_count": record_count,
                    "node_count": len(nodes),
                    "relationship_count": len(relationships)
                },
                "data": {
                    "nodes": nodes,
                    "relationships": relationships
                }
            }
            
            # Sauvegarder
            with open(use_case['output_file'], 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Success!")
            print(f"   - Records: {record_count}")
            print(f"   - Nodes: {len(nodes)}")
            print(f"   - Relationships: {len(relationships)}")
            print(f"   - Saved to: {use_case['output_file']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            
            # Sauvegarder un fichier d'erreur
            error_data = {
                "analysis": {
                    "status": "error",
                    "summary": f"Error fetching {use_case['name']}",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                },
                "data": {
                    "nodes": [],
                    "relationships": []
                }
            }
            
            with open(use_case['output_file'], 'w', encoding='utf-8') as f:
                json.dump(error_data, f, indent=2, ensure_ascii=False)
            
            return False


def main():
    print("="*60)
    print("Neo4j Data Fetcher for POC Graph Visualizer")
    print("="*60)
    
    # Vérifier la configuration
    if NEO4J_PASSWORD == "votre_password_ici":
        print("\n⚠️  ATTENTION: Vous devez configurer NEO4J_PASSWORD dans le script!")
        print("Éditez fetch_neo4j_data.py et modifiez les variables de configuration.")
        return
    
    print(f"\nConfiguration:")
    print(f"  URI: {NEO4J_URI}")
    print(f"  User: {NEO4J_USER}")
    print(f"  Database: {NEO4J_DATABASE}")
    print(f"  Use cases: {len(USE_CASES)}")
    
    # Connexion à Neo4j
    fetcher = Neo4jDataFetcher(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE)
    
    try:
        success_count = 0
        
        for use_case in USE_CASES:
            if fetcher.fetch_and_save_use_case(use_case):
                success_count += 1
        
        print(f"\n{'='*60}")
        print(f"Summary: {success_count}/{len(USE_CASES)} use cases processed successfully")
        print(f"{'='*60}\n")
        
    finally:
        fetcher.close()


if __name__ == "__main__":
    main()
