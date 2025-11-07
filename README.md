# 🔒 Cybersecurity Graph Analysis Client - POC

## 📋 Description

**POC d'un client d'analyse de graphe de cybersécurité** avec architecture backend-frontend moderne. Ce projet permet de visualiser et analyser les résultats d'un service d'analyse de graphes de sécurité (basé sur Neo4j) sous forme interactive et intuitive.

### Objectifs du projet
- ✅ Recevoir et valider des réponses JSON d'un service d'analyse de graphe
- ✅ Visualiser les dispositifs, vulnérabilités et relations de sécurité
- ✅ Afficher les recommandations priorisées avec impact/effort
- ✅ Analyser les niveaux de menace et la criticité des éléments
- ✅ Interface professionnelle pour équipes de cybersécurité

### Cas d'usage
- Analyse de la surface d'attaque d'une infrastructure
- Identification de dispositifs critiques exposés
- Visualisation des vulnérabilités et de leur propagation
- Priorisation des actions de remédiation selon l'impact

## 🏗️ Architecture

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

### Frontend (HTML/CSS/JavaScript)
Interface web moderne et professionnelle pour la visualisation :

- **Dashboard de sécurité** :
  - Barre de statut en temps réel (Status, Threat Level, Confidence, Records)
  - Graphe interactif avec vis.js pour exploration visuelle
  - Code couleur intuitif selon la criticité (Critical=Rouge, High=Orange, etc.)
  
- **Panneaux d'analyse** :
  - **Résumé exécutif** : Vue d'ensemble rapide de l'analyse
  - **Recommandations** : Actions priorisées avec badges impact/effort/priorité
  - **Analyse technique** : Détails approfondis et insights
  - **Détails des nœuds** : Inspection interactive des dispositifs/vulnérabilités
  
- **Thème dark** : Design professionnel adapté aux SOC (Security Operations Center)
- **Responsive** : Adapté aux différentes tailles d'écran

## 🚀 Installation

### 1. Backend

```powershell
# Créer un environnement virtuel
cd backend
python -m venv venv

# Activer l'environnement (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Frontend

Aucune installation nécessaire - ouvrez simplement `frontend/index.html` dans un navigateur.

## ▶️ Démarrage

### 1. Lancer le backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python main.py
```

Le backend sera accessible sur `http://localhost:8000`

### 2. Ouvrir le frontend

Deux options :
- Ouvrir directement `frontend/index.html` dans un navigateur
- Utiliser un serveur HTTP local :

```powershell
cd frontend
python -m http.server 3000
```

Puis accéder à `http://localhost:3000`

## 📖 Guide d'utilisation

### Démarrage rapide
1. **Lancez le backend** (voir section Installation)
2. **Ouvrez `frontend/index.html`** dans votre navigateur
3. **Cliquez sur 🔄** pour rafraîchir la liste des analyses disponibles

### Workflow typique

#### Option 1 : Charger une analyse existante
1. **Sélectionner** un fichier dans le menu déroulant (ex: `cybersec_analysis_example.json`)
2. **Cliquer sur "Charger"**
3. Le système affiche :
   - ✅ Barre de statut avec métriques clés
   - ✅ Graphe interactif des nœuds et relations
   - ✅ Résumé exécutif
   - ✅ Recommandations priorisées
   - ✅ Analyse technique détaillée

#### Option 2 : Générer une analyse mock pour test
1. **Entrer une requête** (ex: "Dispositifs critiques avec SMB exposé")
2. **Cliquer sur "Générer Mock"**
3. Une analyse simulée est créée et automatiquement chargée
4. Parfait pour tester l'interface sans service d'analyse réel

### Exploration du graphe
- **Cliquer sur un nœud** : Affiche les détails (IP, criticité, OS, etc.)
- **Hover sur un nœud** : Tooltip avec infos rapides
- **Zoom** : Molette de la souris
- **Pan** : Cliquer-glisser pour déplacer
- **Navigation** : Boutons de contrôle en bas à droite

### Comprendre les codes couleur
- 🔴 **Rouge (Critical)** : Menace critique, action immédiate requise
- 🟠 **Orange (High)** : Risque élevé, attention prioritaire
- 🟡 **Jaune (Medium)** : Risque moyen, à surveiller
- 🔵 **Bleu (Low)** : Risque faible, information
- 🟢 **Vert (Safe)** : Élément sécurisé

## 🎨 Fonctionnalités principales

### Visualisation avancée
- ✅ **Graphe interactif** : Visualisation hiérarchique des dispositifs, vulnérabilités et connexions
- ✅ **Code couleur intelligent** : Attribution automatique selon la criticité
- ✅ **Navigation fluide** : Zoom, pan, sélection, boutons de contrôle
- ✅ **Légende dynamique** : Référence visuelle des niveaux de criticité
- ✅ **Layout hiérarchique** : Organisation automatique pour clarté maximale

### Analyse de sécurité
- ✅ **Dashboard de métriques** : Status, Threat Level, Confidence, Record Count
- ✅ **Recommandations enrichies** : Priorisation par impact, effort et priorité
- ✅ **Analyse technique** : Détails approfondis avec insights automatiques
- ✅ **Inspection de nœuds** : Propriétés complètes (IP, OS, criticité, CVE, etc.)
- ✅ **Résumé exécutif** : Vue d'ensemble en 2-3 phrases

### Technique
- ✅ **Validation stricte** : Conformité au schéma JSON avec rapport d'erreurs
- ✅ **Support Neo4j natif** : Gestion des nœuds, relations et propriétés
- ✅ **Génération de mocks** : Création d'analyses de test réalistes
- ✅ **API REST complète** : 8 endpoints pour toutes les opérations
- ✅ **Statistiques détaillées** : Extraction de métriques clés par analyse

### Interface utilisateur
- ✅ **Thème dark professionnel** : Design moderne pour SOC
- ✅ **Responsive design** : Adapté desktop/tablette
- ✅ **Toast notifications** : Feedback visuel des actions
- ✅ **Toggle JSON** : Affichage/masquage des données brutes
- ✅ **Performance optimisée** : Gestion efficace de graphes complexes

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

## 🔧 API Endpoints

- `GET /` - Informations sur l'API
- `GET /schema` - Récupère le schéma JSON de réponse
- `GET /files` - Liste des résultats d'analyse disponibles
- `GET /analysis/{filename}` - Récupère un résultat d'analyse avec validation
- `POST /analysis/mock` - Génère une analyse mock pour test
- `GET /graph/{filename}` - Convertit l'analyse en format graphe pour visualisation
- `GET /stats/{filename}` - Statistiques d'une analyse (threat level, confidence, etc.)
- `POST /data` - Enregistre des données JSON

## 🛠️ Technologies utilisées

### Backend
- FastAPI - Framework web moderne et rapide
- Uvicorn - Serveur ASGI
- Pydantic - Validation des données

### Frontend
- HTML5/CSS3
- JavaScript (ES6+)
- vis.js - Bibliothèque de visualisation de graphes

## 📝 Schéma de Réponse (`response_schema.json`)

Le système est conçu pour recevoir des analyses conformes au schéma JSON défini :

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

## 📄 Licence

Projet éducatif - IFT697 AUT25
