# DÉMARRAGE RAPIDE - Mode développement

Ce fichier est un aide-mémoire pour redémarrer rapidement le projet en mode *dev* (sans la partie setup/installation).

Notes rapides :
- Le projet attend généralement un environnement virtuel `.venv` activé contenant `uvicorn` et `livereload`.
- Les URLs par défaut : backend → `http://localhost:8001`, frontend → `http://localhost:3000`.

---

## Option A — Commande unique (Windows PowerShell)
Si vous avez le helper `run_dev.ps1` (recommandé sur Windows) :

```powershell
# depuis la racine du projet
.\run_dev.ps1
```

Ce script active/valide `.venv` si nécessaire et lance le backend + le serveur frontend (livereload).

Arrêt : Ctrl+C dans la console.

---

## Option B — Un terminal (après activation du venv)
Si vous préférez lancer manuellement en un seul terminal (venv déjà activé) :

```powershell
# activer le venv si ce n'est pas déjà fait
.\.venv\Scripts\Activate.ps1

# lancer le backend
uvicorn backend.main:app --reload --port 8001 &

# lancer le serveur frontend (livereload)
python frontend/serve.py
```

Note : sur PowerShell, le `&` exécute la commande en arrière-plan dans la même session ; vous pouvez aussi ouvrir un second terminal.

---

## Option C — Deux terminaux séparés (simple et clair)
Terminal 1 (backend) :

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --port 8001
```

Terminal 2 (frontend) :

```powershell
.\.venv\Scripts\Activate.ps1
python frontend/serve.py
```

---

## Vérifications rapides si quelque chose échoue
- Si `uvicorn` n'est pas trouvé : vérifiez que le venv est activé et que `pip install -r backend/requirements.txt` a été exécuté dans ce venv.
- Si le frontend ne se recharge pas : vérifiez que `frontend/serve.py` fonctionne et que le navigateur est ouvert sur `http://localhost:3000`.
- Logs : regardez la console où `uvicorn` et `serve.py` tournent pour messages d'erreur.

---

Rappel : ce fichier ne couvre pas l'installation initiale (création du venv, installation des requirements). Si vous avez besoin, lancez les commandes d'installation depuis le README principal.
