"""
Script principal pour exécuter tous les tests de use cases
"""
import sys
import time
from pathlib import Path

# Importer tous les tests
from test_uc1_exposed_to_device import USE_CASE_ID as UC1_ID, USE_CASE_NAME as UC1_NAME, QUESTION as UC1_Q, DESCRIPTION as UC1_DESC
from test_uc2_path_between_nodes import USE_CASE_ID as UC2_ID, USE_CASE_NAME as UC2_NAME, QUESTION as UC2_Q, DESCRIPTION as UC2_DESC
from test_uc3_vpn_to_critical import USE_CASE_ID as UC3_ID, USE_CASE_NAME as UC3_NAME, QUESTION as UC3_Q, DESCRIPTION as UC3_DESC
from test_uc4_ssl_vpn_broad_reach import USE_CASE_ID as UC4_ID, USE_CASE_NAME as UC4_NAME, QUESTION as UC4_Q, DESCRIPTION as UC4_DESC
from test_uc5_top_subnets import USE_CASE_ID as UC5_ID, USE_CASE_NAME as UC5_NAME, QUESTION as UC5_Q, DESCRIPTION as UC5_DESC
from test_uc6_path_between_devices import USE_CASE_ID as UC6_ID, USE_CASE_NAME as UC6_NAME, QUESTION as UC6_Q, DESCRIPTION as UC6_DESC
from test_utils import run_use_case_test, check_backend_status, check_upstream_configured

# Liste de tous les use cases
USE_CASES = [
    (UC1_ID, UC1_NAME, UC1_Q, UC1_DESC),
    (UC2_ID, UC2_NAME, UC2_Q, UC2_DESC),
    (UC3_ID, UC3_NAME, UC3_Q, UC3_DESC),
    (UC4_ID, UC4_NAME, UC4_Q, UC4_DESC),
    (UC5_ID, UC5_NAME, UC5_Q, UC5_DESC),
    (UC6_ID, UC6_NAME, UC6_Q, UC6_DESC),
]


def print_header():
    """Affiche l'en-tête du script"""
    print("\n")
    print("=" * 80)
    print(" " * 20 + "🧪 TEST DE TOUS LES USE CASES 🧪")
    print("=" * 80)
    print(f"\nNombre total de use cases: {len(USE_CASES)}")
    print("\nCe script va tester chaque use case séquentiellement.")
    print("Les réponses seront sauvegardées dans le dossier 'data/'.")
    print("\n⚠️  ATTENTION: Chaque requête peut prendre plusieurs minutes!")
    print("=" * 80)


def print_progress(current, total):
    """Affiche la progression"""
    percentage = (current / total) * 100
    bar_length = 40
    filled = int(bar_length * current / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"\n[{bar}] {percentage:.1f}% ({current}/{total})")


def main():
    """Fonction principale"""
    print_header()
    
    # Vérifications préalables
    print("\n📋 Vérifications préalables...")
    if not check_backend_status():
        print("\n❌ Backend non accessible!")
        print("   Démarrez le backend avec: python backend/main.py")
        return 1
    
    if not check_upstream_configured():
        print("\n❌ Upstream non configuré!")
        print("   Configurez l'upstream depuis le frontend ou avec:")
        print('   POST http://localhost:8001/config/upstream {"upstream": "http://your-api"}')
        return 1
    
    print("\n✅ Tous les prérequis sont satisfaits")
    
    # Demander confirmation
    print("\n" + "=" * 80)
    response = input("Voulez-vous continuer? (o/N): ").strip().lower()
    if response not in ['o', 'oui', 'y', 'yes']:
        print("Test annulé par l'utilisateur.")
        return 0
    
    # Exécuter les tests
    results = []
    start_time = time.time()
    
    for i, (uc_id, uc_name, question, description) in enumerate(USE_CASES, 1):
        print_progress(i - 1, len(USE_CASES))
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(USE_CASES)}")
        print(f"{'='*80}")
        
        success = run_use_case_test(uc_id, uc_name, question, description)
        results.append({
            'id': uc_id,
            'name': uc_name,
            'success': success
        })
        
        # Pause entre les tests (sauf pour le dernier)
        if i < len(USE_CASES):
            print("\n⏸️  Pause de 3 secondes avant le prochain test...")
            time.sleep(3)
    
    # Afficher le résumé final
    print_progress(len(USE_CASES), len(USE_CASES))
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    print(" " * 25 + "📊 RÉSUMÉ FINAL 📊")
    print("=" * 80)
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"\nTotal: {len(results)}")
    print(f"✅ Réussis: {successful}")
    print(f"❌ Échoués: {failed}")
    print(f"⏱️  Temps total: {elapsed_time / 60:.2f} minutes")
    
    if failed > 0:
        print("\n❌ Use cases échoués:")
        for r in results:
            if not r['success']:
                print(f"   - {r['name']} ({r['id']})")
    
    if successful > 0:
        print("\n✅ Use cases réussis:")
        for r in results:
            if r['success']:
                print(f"   - {r['name']} ({r['id']})")
        
        print(f"\n📁 Fichiers sauvegardés dans: {Path(__file__).parent.parent / 'data'}")
    
    print("\n" + "=" * 80)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrompu par l'utilisateur (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
