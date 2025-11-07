# Cybersecurity Graph Analysis Client - POC

## 📋 Description

POC d'un client d'analyse de graphe de cybersécurité avec architecture backend-frontend. Permet de visualiser les résultats d'analyse de graphes Neo4j sous forme interactive, avec un focus sur les dispositifs, vulnérabilités et relations de sécurité.

## 🏗️ Architecture

### Backend (FastAPI)
- Client API pour recevoir les résultats d'analyse de graphe
- Validation des réponses selon le schéma JSON défini
- Endpoints pour visualisation et statistiques d'analyse
- Support des structures de données Neo4j (nœuds, relations)
- CORS configuré pour le développement

### Frontend (HTML/CSS/JavaScript)
- Interface de visualisation spécialisée pour la cybersécurité
- Graphe interactif pour dispositifs, vulnérabilités et connexions
- Affichage des recommandations et niveaux de menace
- Code couleur selon la criticité des éléments

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

## 📖 Utilisation

1. **Charger une analyse** : Sélectionnez un résultat d'analyse dans la liste
2. **Générer un mock** : Créez une analyse de test via l'endpoint `/analysis/mock`
3. **Visualiser le graphe** : Explorez les nœuds (dispositifs, vulnérabilités) et leurs relations
4. **Analyser les recommandations** : Consultez les actions prioritaires avec impact/effort
5. **Vérifier les statistiques** : Threat level, confidence, nombre de records

## 🎨 Fonctionnalités

- ✅ Visualisation de graphes de cybersécurité (dispositifs, vulnérabilités, relations)
- ✅ Support complet du schéma de réponse d'analyse
- ✅ Affichage des niveaux de menace (Critical, High, Medium, Low)
- ✅ Recommandations priorisées avec impact et effort
- ✅ Validation des données selon le schéma JSON
- ✅ Génération d'analyses mock pour tests
- ✅ Navigation interactive dans le graphe
- ✅ Interface responsive avec code couleur par criticité

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

## 📝 Schéma de Réponse

Le système attend des réponses au format défini dans `response_schema.json` avec :
- **Champs obligatoires** : `status`, `summary`, `technical_analysis`, `recommendations`
- **Métadonnées** : `threat_level`, `confidence`, `timestamp`
- **Données** : Array de nœuds et relations Neo4j
- **Recommandations enrichies** : Avec impact, effort et priorité

Voir `data/cybersec_analysis_example.json` pour un exemple complet.

## 🔗 Intégration avec Service d'Analyse

Le backend est conçu pour recevoir des réponses du service d'analyse de graphe :

```python
# Exemple d'intégration (à implémenter)
import requests

response = requests.post(
    "http://analysis-service:8080/analyze",
    json={"query": "Trouver dispositifs critiques exposés"}
)

# La réponse suit le schéma response_schema.json
analysis_result = response.json()
```

## 📝 TODO / Améliorations futures

- [ ] Intégration réelle avec service d'analyse de graphe
- [ ] Connexion WebSocket pour analyses en temps réel
- [ ] Export du graphe en image/PDF
- [ ] Filtres avancés par threat level et criticité
- [ ] Timeline des analyses historiques
- [ ] Tableaux de bord de métriques de sécurité
- [ ] Alertes automatiques selon le threat level

## 📄 Licence

Projet éducatif - IFT697 AUT25
