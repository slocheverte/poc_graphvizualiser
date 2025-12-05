# Scripts de Test des Use Cases

Ce dossier contient les scripts pour tester chaque use case et capturer les réponses de l'API CSG.

## Prérequis

1. **Backend démarré**: Le backend doit être en cours d'exécution
   ```powershell
   python backend/main.py
   # ou
   .\run_dev.ps1
   ```

2. **Upstream configuré**: L'API CSG upstream doit être configurée
   - Via le frontend: entrer l'URL et cliquer sur "Configurer"
   - Via API: `POST http://localhost:8001/config/upstream` avec `{"upstream": "http://votre-api-csg"}`

3. **Dépendances Python**: Installer `requests` si nécessaire
   ```powershell
   pip install requests
   ```

## Structure des fichiers

- `test_utils.py` - Module utilitaire commun (gestion des requêtes, sauvegarde, etc.)
- `test_uc1_exposed_to_device.py` - Test du Use Case 1
- `test_uc2_path_between_nodes.py` - Test du Use Case 2
- `test_uc3_vpn_to_critical.py` - Test du Use Case 3
- `test_uc4_ssl_vpn_broad_reach.py` - Test du Use Case 4
- `test_uc5_top_subnets.py` - Test du Use Case 5
- `test_uc6_path_between_devices.py` - Test du Use Case 6
- `run_all_tests.py` - Script pour exécuter tous les tests séquentiellement

## Commandes pour exécuter les fetch des Use Cases individuellement

### Use Case 1: Exposed Device vers Device spécifique
```powershell
cd test_scripts
python test_uc1_exposed_to_device.py
```

### Use Case 2: Chemins entre MTL_VPN_SSL_RANGE et VwLogibecDCR01
```powershell
cd test_scripts
python test_uc2_path_between_nodes.py
```

### Use Case 3: VPN SSL Range vers Appareils Critiques
```powershell
cd test_scripts
python test_uc3_vpn_to_critical.py
```

### Use Case 4: SSL VPN Ranges avec large portée
```powershell
cd test_scripts
python test_uc4_ssl_vpn_broad_reach.py
```

### Use Case 5: Top Subnets par nombre d'appareils
```powershell
cd test_scripts
python test_uc5_top_subnets.py
```

### Use Case 6: Chemin entre deux appareils spécifiques
```powershell
cd test_scripts
python test_uc6_path_between_devices.py
```

## Exécuter tous les fecth en une fois

```powershell
cd test_scripts
python run_all_tests.py
```

## Résultats

Les réponses JSON sont sauvegardées automatiquement dans le dossier `data/` avec les noms:
- `uc1_exposed_to_device_response.json`
- `uc2_path_between_nodes_response.json`
- `uc3_vpn_to_critical_response.json`
- `uc4_ssl_vpn_broad_reach_response.json`
- `uc5_top_subnets_response.json`
- `uc6_path_between_devices_response.json`

Ces fichiers écrasent les fichiers d'exemple existants et seront utilisés par le frontend pour charger les use cases en mode test.

## Notes importantes

- ⏱️ **Temps d'exécution**: Chaque requête peut prendre plusieurs minutes selon la complexité
- 🔄 **Retry**: Le script réessaie automatiquement 2 fois en cas d'échec
- ⏰ **Timeout**: 300 secondes (5 minutes) par requête
- 🔍 **Logs**: Tous les détails sont affichés dans la console

## Dépannage

### "Backend non accessible"
- Vérifiez que le backend est démarré sur le port 8001
- Vérifiez qu'aucun firewall ne bloque la connexion

### "Upstream non configuré"
- Configurez l'upstream via le frontend ou l'API
- Vérifiez que l'URL de l'API CSG est correcte

### "Timeout"
- L'API CSG peut être lente, le timeout est déjà à 5 minutes
- Vous pouvez augmenter `REQUEST_TIMEOUT` dans `test_utils.py`

### "Erreur 502"
- L'API upstream n'est pas accessible
- Vérifiez l'URL de l'upstream
- Vérifiez que l'API CSG est démarrée et accessible
