"""
Utilitaires communs pour tester les use cases
"""
import requests
import json
from datetime import datetime
import time
import sys
from pathlib import Path

# Configuration
BACKEND_API_URL = "http://localhost:8001"
REQUEST_TIMEOUT = 300  # 5 minutes pour les requêtes longues
RETRY_ATTEMPTS = 2
RETRY_DELAY = 5

# Chemins
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"


def check_backend_status():
    """Vérifie que le backend est accessible"""
    try:
        response = requests.get(f"{BACKEND_API_URL}/", timeout=5)
        if response.status_code == 200:
            print("✓ Backend accessible")
            return True
        else:
            print(f"✗ Backend répond avec le code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Backend non accessible: {e}")
        return False


def check_upstream_configured():
    """Vérifie que l'upstream est configuré"""
    try:
        response = requests.get(f"{BACKEND_API_URL}/config/upstream", timeout=5)
        data = response.json()
        if data.get("upstream"):
            print(f"✓ Upstream configuré: {data['upstream']}")
            return True
        else:
            print("✗ Upstream non configuré")
            print("  Pour configurer: POST /config/upstream avec {\"upstream\": \"http://your-api-url\"}")
            return False
    except Exception as e:
        print(f"✗ Erreur lors de la vérification de l'upstream: {e}")
        return False


def send_question(question, description="", max_retries=RETRY_ATTEMPTS):
    """
    Envoie une question via /upstream/analyze
    
    Args:
        question: La question à envoyer
        description: Description pour l'affichage
        max_retries: Nombre maximum de tentatives
    
    Returns:
        dict: La réponse de l'API ou None en cas d'erreur
    """
    print("\n" + "="*80)
    if description:
        print(f"Test: {description}")
    print("="*80)
    print(f"Question: {question[:100]}{'...' if len(question) > 100 else ''}")
    
    payload = {
        "question": question,
        "include_data": True
    }
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n[Tentative {attempt}/{max_retries}]")
            print(f"Envoi de la requête... (timeout: {REQUEST_TIMEOUT}s)")
            
            start_time = time.time()
            
            response = requests.post(
                f"{BACKEND_API_URL}/upstream/analyze",
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            
            elapsed_time = time.time() - start_time
            print(f"Réponse reçue en {elapsed_time:.2f}s")
            
            if response.status_code == 200:
                data = response.json()
                print("✓ Requête réussie")
                
                # Afficher quelques stats
                if isinstance(data, dict):
                    if 'analysis' in data:
                        analysis = data['analysis']
                        if isinstance(analysis, dict):
                            print(f"  Status: {analysis.get('status', 'N/A')}")
                            print(f"  Record count: {analysis.get('record_count', 'N/A')}")
                    
                    if 'graph' in data and data.get('graph'):
                        graph = data['graph']
                        if isinstance(graph, dict):
                            node_count = len(graph.get('nodes', []))
                            edge_count = len(graph.get('edges', []))
                            print(f"  Nodes: {node_count}, Edges: {edge_count}")
                
                return data
            
            elif response.status_code == 400:
                error_data = response.json()
                print(f"✗ Erreur 400: {error_data.get('detail', 'Erreur inconnue')}")
                if "UPSTREAM_API non configuré" in str(error_data.get('detail', '')):
                    print("\n⚠️  L'upstream n'est pas configuré!")
                    print("   Configurez-le avec: POST http://localhost:8001/config/upstream")
                    print('   Body: {"upstream": "http://votre-api-csg"}')
                return None
            
            elif response.status_code == 502:
                error_data = response.json()
                print(f"✗ Erreur 502 (upstream): {error_data.get('detail', 'Erreur upstream')}")
                if attempt < max_retries:
                    print(f"   Nouvelle tentative dans {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY)
                    continue
                return None
            
            else:
                print(f"✗ Erreur HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Détails: {error_data}")
                except:
                    print(f"   Réponse: {response.text[:200]}")
                return None
        
        except requests.exceptions.Timeout:
            print(f"✗ Timeout après {REQUEST_TIMEOUT}s")
            if attempt < max_retries:
                print(f"   Nouvelle tentative dans {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
                continue
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Erreur de connexion: {e}")
            if attempt < max_retries:
                print(f"   Nouvelle tentative dans {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
                continue
            return None
        
        except Exception as e:
            print(f"✗ Erreur inattendue: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    return None


def save_response(data, use_case_id, use_case_name):
    """
    Sauvegarde la réponse dans un fichier JSON
    
    Args:
        data: Les données à sauvegarder
        use_case_id: ID du use case
        use_case_name: Nom du use case
    
    Returns:
        str: Chemin du fichier sauvegardé ou None
    """
    try:
        # Créer le dossier data s'il n'existe pas
        DATA_DIR.mkdir(exist_ok=True)
        
        # Nom du fichier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{use_case_id}_response.json"
        filepath = DATA_DIR / filename
        
        # Sauvegarder les données
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Réponse sauvegardée: {filepath}")
        
        # Afficher la taille du fichier
        file_size = filepath.stat().st_size
        if file_size > 1024 * 1024:
            print(f"  Taille: {file_size / (1024 * 1024):.2f} MB")
        elif file_size > 1024:
            print(f"  Taille: {file_size / 1024:.2f} KB")
        else:
            print(f"  Taille: {file_size} bytes")
        
        return str(filepath)
    
    except Exception as e:
        print(f"\n✗ Erreur lors de la sauvegarde: {e}")
        import traceback
        traceback.print_exc()
        return None


def print_summary(success, use_case_name, filepath=None):
    """Affiche un résumé du test"""
    print("\n" + "="*80)
    print("RÉSUMÉ")
    print("="*80)
    print(f"Use case: {use_case_name}")
    print(f"Status: {'✓ SUCCÈS' if success else '✗ ÉCHEC'}")
    if filepath:
        print(f"Fichier: {filepath}")
    print("="*80)


def run_use_case_test(use_case_id, use_case_name, question, description=""):
    """
    Fonction principale pour tester un use case
    
    Args:
        use_case_id: ID du use case (ex: "uc1_exposed_to_device")
        use_case_name: Nom du use case
        question: Question à envoyer
        description: Description détaillée
    
    Returns:
        bool: True si le test a réussi
    """
    print("\n" + "🔬" * 40)
    print(f"TEST USE CASE: {use_case_name}")
    print("🔬" * 40)
    
    # Vérifications préalables
    if not check_backend_status():
        print("\n⚠️  Assurez-vous que le backend est démarré (python backend/main.py)")
        return False
    
    if not check_upstream_configured():
        print("\n⚠️  Configurez l'upstream avant de continuer")
        return False
    
    # Envoyer la question
    response_data = send_question(question, description)
    
    if not response_data:
        print_summary(False, use_case_name)
        return False
    
    # Sauvegarder la réponse
    filepath = save_response(response_data, use_case_id, use_case_name)
    
    if filepath:
        print_summary(True, use_case_name, filepath)
        return True
    else:
        print_summary(False, use_case_name)
        return False


if __name__ == "__main__":
    print("Module d'utilitaires pour tester les use cases")
    print("Ce module doit être importé, pas exécuté directement")
