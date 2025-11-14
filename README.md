# 🔒 Cybersecurity Graph Analysis Client - POC

## 📋 Description

POC léger pour visualiser et explorer des résultats d'analyse de graphes de cybersécurité (backend FastAPI + frontend D3). Le dépôt fournit :

- un serveur API simple (validation Pydantic, endpoints pour fichiers/mock/graph/stats),
- un frontend HTML/JS qui affiche un graphe interactif et des panneaux de synthèse.

Cas d'usage typiques : inspection de la surface d'attaque, identification d'éléments critiques et priorisation des actions.

## Table des matières

- [Description](#description)
- [Architecture](#architecture)
  - [Backend (FastAPI)](#backend-fastapi)
  - [Frontend (HTML/CSS/JavaScript)](#frontend-htmlcssjavascript)
- [Installation & démarrage (recommandé)](#installation-demarrage-recommande)
- [Guide d'utilisation](#guide-dutilisation)
- [Fonctionnalités principales](#fonctionnalites-principales)
- [Structure du projet](#structure-du-projet)
- [API Endpoints](#api-endpoints)
- [Technologies utilisées](#technologies-utilisees)
- [Tests et Développement](#tests-et-developpement)
- [Déploiement](#deploiement)
- [Roadmap / Améliorations futures](#roadmap-ameliorations-futures)
- [Dépannage](#depannage)
- [Contribution](#contribution)
- [Licence](#licence)

<a id="architecture"></a>
## 🏗️ Architecture

<a id="backend-fastapi"></a>
### Backend (FastAPI)
Le backend agit comme un **client API** pour recevoir et traiter les résultats d'analyse :

- **Modèles Pydantic** : Validation stricte basée sur `response_schema.json`
- **Endpoints REST** :
  - `/schema` : Récupère le schéma JSON de réponse attendu
  - `/analysis/{filename}` : Charge et valide une analyse avec statut de validation
  - `/analysis/mock` : Génère des analyses de test pour développement
  - `/graph/{filename}` : Convertit les données en format graphe (nœuds/liens)
  - `/stats/{filename}` : Extrait les statistiques clés (threat level, confidence, etc.)
- **Support Neo4j** : Gestion native des structures nœuds/relations
- **CORS activé** : Permet les requêtes cross-origin en développement

<a id="frontend-htmlcssjavascript"></a>
### Frontend (HTML/CSS/JavaScript)
Interface web moderne et professionnelle pour la visualisation :

- **Dashboard de sécurité** :
  - Barre de statut en temps réel (Status, Threat Level, Confidence, Records)
  - Graphe interactif avec D3.js pour exploration visuelle
  - Code couleur intuitif selon la criticité (Critical=Rouge, High=Orange, etc.)
  
- **Panneaux d'analyse** :
  - **Résumé exécutif** : Vue d'ensemble rapide de l'analyse
  - **Recommandations** : Actions priorisées avec badges impact/effort/priorité
  - **Analyse technique** : Détails approfondis et insights
  - **Détails des nœuds** : Inspection interactive des dispositifs/vulnérabilités
  
- **Thème dark** : Design professionnel adapté aux SOC (Security Operations Center)
- **Responsive** : Adapté aux différentes tailles d'écran

<a id="installation-demarrage-recommande"></a>
## 🚀 Installation & démarrage (rapide)

Recommandé : créer un venv projet-local `.venv` et activer avant d'installer les dépendances.

Commandes minimales (PowerShell) :

```powershell
# depuis la racine
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

Démarrage rapide :

- Méthode recommandée (Windows) : lancez le helper `run_dev.ps1` qui automatise la création/activation du venv, l'installation minimale et le démarrage du backend+frontend :

```powershell
.\run_dev.ps1
```

- Méthode manuelle (après activation du venv) :

```powershell
uvicorn backend.main:app --reload --port 8001
python frontend/serve.py
```

Le frontend sera servi sur `http://localhost:3000`, le backend sur `http://localhost:8001`.

Option pratique : lancer backend + frontend ensemble
-------------------------------------------------

Le projet fournit deux helpers pour le développement :

- `run_dev.ps1` (Windows PowerShell) — recommandée pour les utilisateurs Windows. Elle crée/active `.venv` si nécessaire, installe les dépendances et démarre le backend et le frontend avec reload.
- `dev.py` (cross-platform Python) — lance `uvicorn backend.main:app --reload` et `python frontend/serve.py` en parallèle. Si vous utilisez `dev.py`, assurez-vous d'avoir activé `.venv` qui contient `uvicorn` et `livereload`.

Exemples :

```powershell
# Windows (recommandé)
.\run_dev.ps1

# ou, manuellement dans un venv activé
python dev.py
```

Arrêt : Ctrl+C dans la console arrête proprement les deux serveurs.

<a id="guide-dutilisation"></a>
## 📖 Guide d'utilisation (résumé)

- Démarrage : lancer backend + frontend (voir section Installation).
- Charger une analyse : sélectionner un fichier et cliquer sur "Charger".
- Générer un mock : utiliser `POST /analysis/mock` depuis curl ou l'UI.
- Exploration : cliquer pour voir détails, utiliser la molette pour zoom et cliquer-glisser pour pan.
- Codes couleur : Critical=rouge, High=orange, Medium=jaune, Low=bleu, Safe=vert.

<a id="fonctionnalites-principales"></a>
## 🎨 Fonctionnalités principales (aperçu)

- Graphe interactif D3 : sélection, zoom, pan, et inspection des nœuds.
- Dashboard minimal : statut, threat level, confidence, record count.
- Validation Pydantic côté backend et génération de mocks pour tests.
- Helpers de dev : `frontend/serve.py` (livereload), `dev.py` / `run_dev.ps1` pour l'environnement local.

<a id="structure-du-projet"></a>
## 📁 Structure du projet

```
poc_graphvizualiser/
├── backend/
│   ├── main.py                      # API Client FastAPI
│   ├── requirements.txt             # Dépendances Python
│   └── venv/                       # Environnement virtuel
├── frontend/
│   ├── index.html                  # Interface de visualisation
│   ├── style.css                   # Styles avec code couleur sécurité
│   └── script.js                   # Logique de visualisation de graphe
├── data/
│   ├── example.json                # Exemple générique
│   └── cybersec_analysis_example.json  # Exemple d'analyse complète
├── response_schema.json            # Schéma JSON de réponse d'analyse
├── .gitignore
└── README.md
```

<a id="api-endpoints"></a>
## 🔧 API Endpoints

- `GET /` - Informations sur l'API
- `GET /schema` - Récupère le schéma JSON de réponse
- `GET /files` - Liste des résultats d'analyse disponibles
- `GET /analysis/{filename}` - Récupère un résultat d'analyse avec validation
- `POST /analysis/mock` - Génère une analyse mock pour test
- `GET /graph/{filename}` - Convertit l'analyse en format graphe pour visualisation
- `GET /stats/{filename}` - Statistiques d'une analyse (threat level, confidence, etc.)
- `POST /data` - Enregistre des données JSON

<a id="technologies-utilisees"></a>
## 🛠️ Technologies utilisées

### Backend
- FastAPI - Framework web moderne et rapide
- Uvicorn - Serveur ASGI
- Pydantic - Validation des données

### Frontend

- HTML5 / CSS3
- JavaScript (ES6+)
- D3.js — bibliothèque de visualisation (utilisée pour le rendu du graphe)
- Optionnel : `livereload` pour un serveur de développement avec rechargement automatique

Si vous développez activement le frontend, utilisez `frontend/serve.py` (basé sur `livereload`) pour recharger automatiquement la page quand `index.html`, `script.js` ou `style.css` changent.
### Structure de base
```json
{
  "status": "success|error|warning",
  "summary": "Résumé exécutif en 2-3 phrases",
  "technical_analysis": "Analyse technique détaillée",
  "recommendations": ["Action 1", "Action 2", "..."],
  "threat_level": "Critical|High|Medium|Low|Info",
  "confidence": "High|Medium|Low",
  "record_count": 8,
  "data": [...]
}
```

### Champs obligatoires
- `status` : État global de l'analyse (success/error/warning)
- `summary` : Résumé exécutif pour prise de décision rapide
- `technical_analysis` : Détails techniques pour l'équipe SOC
- `recommendations` : Actions recommandées (array ou string)

### Métadonnées importantes
- `threat_level` : Niveau de menace détecté
- `confidence` : Niveau de confiance de l'analyse
- `timestamp` : Date/heure de l'analyse
- `record_count` : Nombre d'éléments trouvés
- `execution_time` : Durée de l'analyse en secondes

### Structure des données Neo4j
```json
"data": [
  {
    "type": "node",
    "id": "device-123",
    "labels": ["Device", "Server"],
    "properties": {
      "ip": "192.168.1.10",
      "criticality": "High",
      "os": "Windows Server 2019"
    }
  },
  {
    "type": "relationship",
    "relationship_type": "CONNECTS_TO",
    "from": "device-123",
    "to": "device-124",
    "properties": {
      "port": 445,
      "protocol": "SMB"
    }
  }
]
```

### Recommandations enrichies
```json
"recommendations_with_impact": [
  {
    "recommendation": "Isoler les devices critiques",
    "impact": "High",
    "effort": "Medium",
    "priority": 1
  }
]
```

### Exemple complet
Consultez `data/cybersec_analysis_example.json` pour un exemple réaliste avec :
- 3 dispositifs (serveurs finance, RH, workstation admin)
- 1 vulnérabilité CVE-2017-0144 (EternalBlue)
- 5 relations de connexion SMB/NetBIOS
- Recommandations priorisées avec métadonnées
- Risk assessment détaillé

## 🔗 Intégration avec Service d'Analyse

Le backend est conçu comme un **client** pour recevoir des analyses d'un service externe.

### Architecture d'intégration

```
┌─────────────────┐      HTTP/REST      ┌──────────────────┐
│   Service       │ ──────────────────> │  Backend Client  │
│   d'Analyse     │  (response_schema)  │    (FastAPI)     │
│   (Neo4j)       │                     │                  │
└─────────────────┘                     └──────────────────┘
                                              │
                                              │ WebSocket/HTTP
                                              │
                                              ▼
                                        ┌──────────────────┐
                                        │    Frontend      │
                                        │  (Visualisation) │
                                        └──────────────────┘
```

### Exemple d'intégration Python

```python
# Dans votre service d'analyse
import requests
import json

# 1. Effectuer l'analyse dans Neo4j
def analyze_critical_devices():
    query = """
    MATCH (d:Device {criticality: 'High'})-[r:CONNECTS_TO]->(target)
    WHERE r.port IN [445, 139]
    RETURN d, r, target
    """
    # ... exécution Neo4j ...
    
    # 2. Formater selon response_schema.json
    analysis_result = {
        "status": "success",
        "summary": "3 dispositifs critiques avec SMB exposé détectés",
        "technical_analysis": "Analyse détaillée...",
        "recommendations": ["Isoler les devices", "Appliquer patches"],
        "threat_level": "High",
        "confidence": "High",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "record_count": 3,
        "data": [
            # Nœuds et relations extraits de Neo4j
        ]
    }
    
    # 3. Envoyer au backend client
    response = requests.post(
        "http://localhost:8000/data",
        json={
            "data": analysis_result,
            "filename": "analysis_2025-11-07.json"
        }
    )
    
    return response.json()
```

### Intégration directe (future)

```python
# À implémenter dans backend/main.py
@app.post("/analyze")
async def request_analysis(query: AnalysisQuery):
    """Envoie une requête au service d'analyse externe"""
    
    # Appel au service d'analyse
    response = requests.post(
        "http://analysis-service:8080/analyze",
        json={"query": query.query, "context": query.context}
    )
    
    # Validation de la réponse
    analysis_data = response.json()
    validated = CybersecurityAnalysisResponse(**analysis_data)
    
    # Sauvegarde et retour
    filename = save_analysis(validated)
    return {"filename": filename, "data": validated}
```

### Configuration du service externe

```python
# config.py (à créer)
ANALYSIS_SERVICE_URL = "http://analysis-service:8080"
ANALYSIS_SERVICE_API_KEY = "votre-clé-api"
TIMEOUT_SECONDS = 30
```

<a id="tests-et-developpement"></a>
## 🧪 Tests et Développement

### Tester avec les données d'exemple

1. **Exemple complet** : `cybersec_analysis_example.json`
   - Scénario : 3 serveurs critiques avec vulnérabilité EternalBlue
   - Contient : Nœuds, relations, recommandations, métadonnées
   - Utilisation : Charger via l'interface pour tester toutes les fonctionnalités

2. **Générer des mocks** :
   ```bash
   curl -X POST http://localhost:8000/analysis/mock \
     -H "Content-Type: application/json" \
     -d '{"query": "Test de dispositifs exposés"}'
   ```

3. **Valider un schéma** :
   ```bash
   curl http://localhost:8000/schema
   ```

### Structure de test recommandée

```python
# tests/test_analysis.py (à créer)
import pytest
from backend.main import CybersecurityAnalysisResponse

def test_valid_analysis():
    """Test de validation d'une analyse valide"""
    data = {
        "status": "success",
        "summary": "Test summary",
        "technical_analysis": "Test analysis",
        "recommendations": ["Action 1"]
    }
    result = CybersecurityAnalysisResponse(**data)
    assert result.status == "success"

def test_invalid_threat_level():
    """Test de rejet d'un threat level invalide"""
    with pytest.raises(ValueError):
        data = {
            "status": "success",
            "threat_level": "Invalid"  # Doit être Critical/High/Medium/Low/Info
        }
        CybersecurityAnalysisResponse(**data)
```

<a id="deploiement"></a>
## 🚀 Déploiement

### Mode production

1. **Backend** :
   ```bash
   # Utiliser gunicorn pour production
   pip install gunicorn
   gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

2. **Frontend** :
   - Héberger sur un serveur web (Nginx, Apache)
   - Ou utiliser un CDN pour les assets statiques
   - Mettre à jour `API_URL` dans `script.js` avec l'URL de production

3. **Docker** (à créer) :
   ```dockerfile
   # Dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY backend/requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

<a id="roadmap-ameliorations-futures"></a>
## 📝 Roadmap / Améliorations futures

### Phase 1 : Intégration (Prioritaire)
- [ ] **Endpoint `/analyze`** : Requêtes directes au service d'analyse
- [ ] **WebSocket** : Mises à jour en temps réel des analyses
- [ ] **Authentification** : JWT/OAuth pour sécuriser l'accès
- [ ] **Rate limiting** : Protection contre les abus

### Phase 2 : Fonctionnalités avancées
- [ ] **Export** : Graphes en PNG/SVG/PDF
- [ ] **Filtres dynamiques** : Par threat level, confidence, date
- [ ] **Recherche** : Trouver des nœuds par IP, hostname, CVE
- [ ] **Comparaison** : Diff entre deux analyses
- [ ] **Timeline** : Historique et évolution dans le temps

### Phase 3 : Dashboard et alertes
- [ ] **Tableaux de bord** : Métriques agrégées multi-analyses
- [ ] **Alertes** : Notifications selon seuils (Critical → Email)
- [ ] **Rapports** : Génération automatique PDF/HTML
- [ ] **API publique** : Webhooks pour intégrations externes

### Phase 4 : Intelligence
- [ ] **ML/AI** : Détection d'anomalies dans les patterns
- [ ] **Recommandations auto** : Suggestions basées sur l'historique
- [ ] **Scoring** : Calcul automatique de risk scores
- [ ] **Prédiction** : Anticipation de propagation de vulnérabilités

<a id="depannage"></a>
## 🐛 Dépannage

### Le backend ne démarre pas
```bash
# Vérifier la version de Python (3.9+)
python --version

# Réinstaller les dépendances
pip install -r backend/requirements.txt --force-reinstall
```

### Le graphe ne s'affiche pas
- Vérifier que le backend est lancé (`http://localhost:8000`)
- Ouvrir la console navigateur (F12) pour voir les erreurs
- Vérifier les CORS dans `backend/main.py`

### Erreur de validation
- Consulter le schéma : `http://localhost:8000/schema`
- Vérifier que tous les champs obligatoires sont présents
- Utiliser `/analysis/{filename}` pour voir les erreurs de validation

<a id="contribution"></a>
## 🤝 Contribution

### Workflow de contribution
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Standards de code
- **Python** : PEP 8, type hints, docstrings
- **JavaScript** : ESLint, commentaires explicatifs
- **Git** : Commits atomiques avec messages clairs

<a id="licence"></a>
## 📄 Licence

Projet éducatif - IFT697 AUT25
