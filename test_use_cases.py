"""
Script pour tester les use cases et sauvegarder les réponses JSON
Ce script envoie les requêtes via notre backend local qui communique avec l'API CSG upstream
"""
import requests
import json
from datetime import datetime
import os
import time
import sys

# Configuration
BACKEND_API_URL = "http://localhost:8001"  # Notre backend local
REQUEST_TIMEOUT = 300  # 5 minutes timeout pour les requêtes longues
RETRY_ATTEMPTS = 2
RETRY_DELAY = 5  # secondes entre les tentatives

# Définition des use cases
USE_CASES = [
    {
        "id": "uc1_exposed_to_device",
        "name": "Exposed Device that can reach a specific Device",
        "description": "Find every Internet Exposed Device that has a reachable path to the device whose id is VwLogibecDCR01",
        "cypher": """MATCH full_path = (i:Internet)-[:EXPOSES]->(vip:VIP)-[:MAPPED_TO]->(sourceDevice:Device)-[:IS_SOURCE_OF|HAS_SOURCE|HAS_TARGET|TARGETED_BY*1..6]-(target:Device {id:'VwLogibecDCR01'}) 
RETURN DISTINCT sourceDevice AS InternetExposedDevice, nodes(full_path) AS PathNodes, relationships(full_path) AS PathRelationships, full_path AS path"""
    },
    {
        "id": "uc2_path_between_nodes",
        "name": "Paths between 2 Nodes: MTL_VPN_SSL_RANGE & VwLogibecDCR01",
        "description": "Find paths between the MTL_VPN_SSL_RANGE and the device with id VwLogibecDCR01",
        "cypher": """MATCH full_path = shortestPath((src:IPRange {id: 'MTL_VPN_SSL_RANGE'})-[:IS_SOURCE_OF|HAS_SOURCE|HAS_TARGET|TARGETED_BY|MEMBER_OF|HAS_MEMBER|IPSEC_TUNNEL|IPSEC_TUNNEL_INVERSE*1..6]-(dst:Device {id: 'VwLogibecDCR01'})) 
RETURN full_path AS path"""
    },
    {
        "id": "uc3_vpn_to_critical",
        "name": "VPN_SSL_RANGE to Critical Devices",
        "description": "Return network paths that originate at all VPN SSL RANGE and lead to nodes classified as Critical",
        "cypher": """MATCH full_path = (src:IPRange)-[:IS_SOURCE_OF|HAS_TARGET*1..5]-(target:Device) 
WHERE (src.id CONTAINS 'VPN_SSL_RANGE' OR src.label CONTAINS 'VPN_SSL_RANGE') 
  AND target.criticality_level = '2.0' 
RETURN DISTINCT full_path, src.id AS source_range, target.criticality_level AS criticality, target.category AS target_category, full_path AS path 
LIMIT 50"""
    },
    {
        "id": "uc4_ssl_vpn_broad_reach",
        "name": "SSL VPN ranges with broad reach",
        "description": "SSL pools that can reach many targets (potential lateral-movement risk)",
        "cypher": """MATCH full_path = (ssl:SSLrange)-[:IS_SOURCE_OF]->(p:Policy)-[:HAS_TARGET]->(t)   
WHERE (t:Device OR t:Subnet OR t:Group OR t:IPRange OR t:VIP OR t:VIPGroup)   
WITH ssl, collect(DISTINCT t) AS reachable_targets, count(DISTINCT t) AS reach_count, collect(DISTINCT full_path) AS paths   
RETURN ssl.label AS ssl_range, reach_count, [n IN reachable_targets | labels(n)[0]] AS target_types, paths AS path   
ORDER BY reach_count DESC"""
    },
    {
        "id": "uc5_top_subnets",
        "name": "Top N subnets with the most devices",
        "description": "Top 10 subnets ordered by device count",
        "cypher": """MATCH p = (s:Subnet)-[:HAS_DEVICE]->(d:Device) 
RETURN s AS subnet, COUNT(d) AS device_count, p AS path 
ORDER BY device_count DESC 
LIMIT 10"""
    },
    {
        "id": "uc6_path_between_devices",
        "name": "Path between 2 Devices",
        "description": "Shortest path between two specific devices",
        "cypher": """MATCH full_path = shortestPath((start:Device {label:'w1clictxxa2301.aepc.com'})-[:BELONGS_TO|MEMBER_OF|IS_SOURCE_OF|HAS_SOURCE|HAS_TARGET|TARGETED_BY|IPSEC_TUNNEL|IPSEC_TUNNEL_INVERSE*..10]-(end:Device {label:'s1clisgbd60434.aepc.com'})) 
RETURN full_path AS path"""
    }
]


def test_use_case(use_case):
    """
    Teste un use case en envoyant la requête Cypher à l'API CSG
    """
    print(f"\n{'='*80}")
    print(f"Testing: {use_case['name']}")
    print(f"{'='*80}")
    print(f"Description: {use_case['description']}")
    print(f"Cypher: {use_case['cypher'][:100]}...")
    
    try:
        # Préparer la requête
        headers = {
            "Authorization": f"Bearer {CSG_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": use_case['cypher']
        }
        
        # Envoyer la requête
        print(f"\nSending request to {CSG_API_URL}...")
        response = requests.post(
            f"{CSG_API_URL}/query",  # Adapter l'endpoint selon l'API
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        
        # Récupérer la réponse
        data = response.json()
        
        # Sauvegarder la réponse
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/{use_case['id']}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Success! Response saved to: {filename}")
        print(f"  Records returned: {len(data.get('results', []))}")
        
        return {
            "success": True,
            "filename": filename,
            "record_count": len(data.get('results', []))
        }
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """
    Teste tous les use cases
    """
    print("="*80)
    print("USE CASE TESTING SCRIPT")
    print("="*80)
    print(f"Total use cases to test: {len(USE_CASES)}")
    
    # Créer le dossier data s'il n'existe pas
    os.makedirs("data", exist_ok=True)
    
    # Tester chaque use case
    results = []
    for i, use_case in enumerate(USE_CASES, 1):
        print(f"\n\n[{i}/{len(USE_CASES)}]")
        result = test_use_case(use_case)
        results.append({
            "use_case": use_case,
            "result": result
        })
    
    # Résumé
    print("\n\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    successful = sum(1 for r in results if r['result']['success'])
    failed = len(results) - successful
    
    print(f"Total: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\nFailed use cases:")
        for r in results:
            if not r['result']['success']:
                print(f"  - {r['use_case']['name']}: {r['result'].get('error', 'Unknown error')}")
    
    # Sauvegarder le résumé
    summary_file = f"data/test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": len(results),
            "successful": successful,
            "failed": failed,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nSummary saved to: {summary_file}")


if __name__ == "__main__":
    # Instructions pour l'utilisateur
    print("""
    ⚠️  CONFIGURATION REQUIRED ⚠️
    
    Before running this script, please update the following variables:
    - CSG_API_URL: The base URL of your CSG API
    - CSG_API_TOKEN: Your authentication token
    
    You may also need to adjust the endpoint path in the test_use_case() function.
    
    Press Ctrl+C to cancel, or Enter to continue...
    """)
    
    try:
        input()
        main()
    except KeyboardInterrupt:
        print("\n\nScript cancelled by user.")
