from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
import os
import logging
from fastapi import Request

# optional http client for upstream API
try:
    import httpx
except Exception:
    httpx = None

app = FastAPI(title="Cybersecurity Graph Analysis Client API")

# Middleware to log any attempts to call removed /files endpoint so we can identify clients
logger = logging.getLogger("poc_graphvizualiser.files")
logger.setLevel(logging.INFO)


@app.middleware("http")
async def log_files_requests(request: Request, call_next):
    try:
        if request.url.path == "/files":
            headers = {k: v for k, v in request.headers.items()}
            client = request.client.host if request.client else 'unknown'
            info = f"/files requested from {client} referer={headers.get('referer')} ua={headers.get('user-agent')}"
            logger.info(info)
            # Also print to stdout so it appears in uvicorn/livereload console
            print(info)
    except Exception:
        logger.exception("Error in log_files_requests middleware")
    response = await call_next(request)
    return response


@app.on_event("startup")
async def startup_event():
    """Initialize default upstream on startup. Priority: ENV UPSTREAM_API, otherwise default to http://127.0.0.1:8000"""
    env_up = os.environ.get("UPSTREAM_API")
    if env_up:
        app.state.upstream = env_up.rstrip('/')
    else:
        app.state.upstream = "http://127.0.0.1:8000"

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chemin vers le dossier data
DATA_DIR = Path(__file__).parent.parent / "data"
SCHEMA_PATH = Path(__file__).parent.parent / "response_schema.json"
USE_CASES_PATH = DATA_DIR / "use_cases.json"


def require_upstream() -> str:
    """Return the configured upstream URL set via /config/upstream by the frontend.
    Raises HTTPException(400) if not set.
    """
    upstream = getattr(app.state, "upstream", None)
    if not upstream:
        raise HTTPException(status_code=400, detail=(
            "UPSTREAM_API non configuré via l'API. Configurez-le depuis le frontend avec POST /config/upstream {\"upstream\": \"http://127.0.0.1:8000\"}"
        ))
    return upstream.rstrip('/')


@app.post("/config/upstream")
async def set_upstream(cfg: Dict[str, str]):
    """Set the upstream API base URL from the frontend. Body: { "upstream": "http://127.0.0.1:8000" }"""
    url = cfg.get("upstream")
    if not url:
        raise HTTPException(status_code=400, detail="Champ 'upstream' requis")
    # basic validation
    if not (url.startswith("http://") or url.startswith("https://")):
        raise HTTPException(status_code=400, detail="L'URL doit commencer par http:// ou https://")
    app.state.upstream = url.rstrip('/')
    return {"message": "upstream configuré", "upstream": app.state.upstream}


@app.get("/config/upstream")
async def get_upstream_config():
    upstream = getattr(app.state, "upstream", None)
    if not upstream:
        return {"upstream": None}
    return {"upstream": upstream}


# Modèles Pydantic basés sur le schéma de réponse
class StatusEnum(str, Enum):
    success = "success"
    error = "error"
    warning = "warning"


class ThreatLevelEnum(str, Enum):
    critical = "Critical"
    high = "High"
    medium = "Medium"
    low = "Low"
    info = "Info"


class ConfidenceEnum(str, Enum):
    high = "High"
    medium = "Medium"
    low = "Low"


class ImpactEnum(str, Enum):
    high = "High"
    medium = "Medium"
    low = "Low"


class RecommendationWithImpact(BaseModel):
    recommendation: str
    impact: Optional[ImpactEnum] = None
    effort: Optional[ImpactEnum] = None
    priority: Optional[int] = Field(None, ge=1)


class DataRecord(BaseModel):
    type: Optional[str] = None
    id: Optional[Union[str, int]] = None
    labels: Optional[List[str]] = None
    relationship_type: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    from_: Optional[str] = Field(None, alias="from")
    to: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None
    score: Optional[float] = None

    class Config:
        populate_by_name = True


class CybersecurityAnalysisResponse(BaseModel):
    status: StatusEnum
    summary: str
    technical_analysis: str
    recommendations: Union[List[str], str]
    recommendations_with_impact: Optional[List[RecommendationWithImpact]] = None
    confidence: Optional[ConfidenceEnum] = None
    threat_level: Optional[ThreatLevelEnum] = None
    next_steps: Optional[Union[List[str], str]] = None
    data_summary: Optional[str] = None
    insights: Optional[Union[List[str], str]] = None
    risk_assessment: Optional[Union[str, Dict[str, Any]]] = None
    timestamp: Optional[str] = None
    original_question: Optional[str] = None
    original_intent: Optional[str] = None
    query: Optional[str] = None
    query_rationale: Optional[str] = None
    query_status: Optional[str] = None
    record_count: Optional[int] = Field(None, ge=0)
    iterations_used: Optional[int] = Field(None, ge=0)
    execution_time: Optional[float] = Field(None, ge=0)
    system_info: Optional[Dict[str, Any]] = None
    data: Optional[List[DataRecord]] = None
    provenance: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    empty_results_details: Optional[Dict[str, Any]] = None


class AnalysisQuery(BaseModel):
    """Modèle pour envoyer une requête d'analyse"""
    query: str = Field(..., description="Question ou requête d'analyse à envoyer au service")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexte additionnel pour l'analyse")


class JsonData(BaseModel):
    """Modèle pour recevoir des données JSON"""
    data: Dict[str, Any]
    filename: str = "data.json"


@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "Cybersecurity Graph Analysis Client API",
        "description": "POC client pour visualiser les résultats d'analyse de graphes de cybersécurité",
        "endpoints": {
            "POST /analysis/mock": "Génère un résultat d'analyse mock pour test (proxy vers upstream)",
            "POST /upstream/analyze": "Proxy vers l'upstream /analyze/ (retourne analysis + optional graph)",
            "GET /upstream/last_query": "DEPRECATED: /analyze/last_query is decommissioned; use POST /upstream/analyze with include_data=true",
            "POST /data": "Proxy pour envoyer des données au backend upstream",
            "POST /config/upstream": "Configurer l'URL de l'upstream au runtime",
            "GET /config/upstream": "Récupérer la configuration actuelle de l'upstream",
            "GET /schema": "Récupère le schéma JSON de réponse",
            "GET /use-cases": "Liste tous les use cases disponibles",
            "GET /use-cases/{use_case_id}": "Charge les données pré-enregistrées d'un use case spécifique"
        }
    }


@app.get("/schema")
async def get_schema():
    """Récupère le schéma JSON de réponse attendu"""
    try:
        if SCHEMA_PATH.exists():
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema = json.load(f)
            return schema
        else:
            raise HTTPException(status_code=404, detail="Schéma non trouvé")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files")
async def list_files():
    # Removed: listing local/upstream files is not supported in this POC.
    raise HTTPException(status_code=404, detail="Endpoint removed: file listing is unsupported. Use POST /upstream/analyze or POST /analysis/mock to obtain analysis results.")


@app.get("/analysis/{filename}")
async def get_analysis(filename: str):
    # Removed: fetching analysis by filename is not supported. Use POST /upstream/analyze instead.
    raise HTTPException(status_code=404, detail="Endpoint removed: per-file analysis retrieval is unsupported. Use POST /upstream/analyze.")


@app.post("/analysis/mock")
async def create_mock_analysis(query: AnalysisQuery):
    """Génère un résultat d'analyse mock pour tester le système"""
    upstream = require_upstream()

    if httpx is None:
        raise HTTPException(status_code=500, detail="httpx requis pour interroger l'API upstream mais n'est pas installé")

    url = f"{upstream}/analysis/mock"
    payload = {"query": query.query, "context": query.context or {}}
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur upstream: {e}")


@app.post("/upstream/analyze")
async def upstream_analyze(payload: Dict[str, Any]):
    """Proxy POST to UPSTREAM_API/analyze/ — forward arbitrary payload (e.g. {question: ...})"""
    upstream = require_upstream()
    if httpx is None:
        raise HTTPException(status_code=500, detail="httpx requis mais non installé")

    analyze_url = f"{upstream}/analyze/"
    last_query_url = f"{upstream}/analyze/last_query"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Ensure clients request the normalized graph directly from the upstream by setting include_data=True
            if isinstance(payload, dict):
                # don't override an explicit false, but prefer to request the data when not provided
                if 'include_data' not in payload:
                    payload['include_data'] = True
            resp = await client.post(analyze_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # The upstream is expected to include normalized graph data in its POST response when include_data=true.
            # We will prefer the `data` field in the returned JSON (which should contain nodes/relationships/meta).
            analysis = data.get('analysis') if isinstance(data, dict) and 'analysis' in data else data

            graph = None
            graph_present = False

            # If the upstream returned a `data` object with nodes/relationships, normalize it to graph nodes/edges
            try:
                dat = None
                # analysis may be the full response dict or wrapped under 'analysis'
                if isinstance(analysis, dict) and 'data' in analysis and isinstance(analysis['data'], dict):
                    dat = analysis['data']
                elif isinstance(data, dict) and 'data' in data and isinstance(data['data'], dict):
                    dat = data['data']

                if isinstance(dat, dict) and 'nodes' in dat and 'relationships' in dat:
                    nodes = []
                    edges = []
                    for n in dat.get('nodes', []):
                        nid = str(n.get('id')) if n.get('id') is not None else (n.get('properties', {}).get('id') if isinstance(n.get('properties', {}), dict) else None)
                        nid = str(nid) if nid is not None else (n.get('label') or '')
                        labels = n.get('labels') if isinstance(n.get('labels'), list) else []
                        props = n.get('properties', {}) if isinstance(n.get('properties'), dict) else {}
                        label = ', '.join(labels) if labels else (props.get('name') or nid)
                        nodes.append({
                            'id': nid,
                            'label': label,
                            'labels': labels,
                            'properties': props
                        })

                    for r in dat.get('relationships', []):
                        source = r.get('start_id') or r.get('from') or r.get('start')
                        target = r.get('end_id') or r.get('to') or r.get('end')
                        reltype = r.get('type') or r.get('relationship_type') or ''
                        edges.append({
                            'from': str(source) if source is not None else None,
                            'to': str(target) if target is not None else None,
                            'label': reltype,
                            'properties': r.get('properties', {})
                        })

                    graph = {'nodes': nodes, 'edges': edges}
                    graph_present = len(nodes) > 0
                else:
                    # If there is some `data` but not in nodes/relationships shape, include it raw under graph.last_query for debugging
                    if dat is not None:
                        graph = {'last_query': dat}
                        graph_present = True
            except Exception:
                graph = None
                graph_present = False

            result = {
                'analysis': analysis,
                'graph': graph,
                'graph_present': bool(graph_present),
                'data_included': bool(graph_present)
            }

            return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur upstream: {e}")


@app.get("/upstream/last_query")
async def upstream_last_query():
    """Proxy GET to UPSTREAM_API/analyze/last_query"""
    upstream = require_upstream()
    if httpx is None:
        raise HTTPException(status_code=500, detail="httpx requis mais non installé")

    url = f"{upstream}/analyze/last_query"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur upstream: {e}")


@app.post("/data")
async def save_data(json_data: JsonData):
    """Enregistre des données JSON dans un fichier"""
    upstream = require_upstream()

    if httpx is None:
        raise HTTPException(status_code=500, detail="httpx requis pour interroger l'API upstream mais n'est pas installé")

    url = f"{upstream}/data"
    payload = {"data": json_data.data, "filename": json_data.filename}
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur upstream: {e}")


@app.get("/graph/{filename}")
async def get_graph_data(filename: str):
    """
    Récupère les données d'analyse formatées pour la visualisation en graphe de cybersécurité.
    Extrait les nœuds et relations du champ 'data' de la réponse d'analyse.
    """
    upstream = require_upstream()
    if httpx is None:
        raise HTTPException(status_code=500, detail="httpx requis pour interroger l'API upstream mais n'est pas installé")

    # Removed: per-file graph retrieval is unsupported. Use POST /upstream/analyze which may return graph data.
    raise HTTPException(status_code=404, detail="Endpoint removed: per-file graph retrieval is unsupported. Use POST /upstream/analyze.")


@app.get("/stats/{filename}")
async def get_analysis_stats(filename: str):
    # Removed: per-file stats retrieval is unsupported. Use analysis responses returned by POST /upstream/analyze.
    raise HTTPException(status_code=404, detail="Endpoint removed: per-file stats retrieval is unsupported. Use POST /upstream/analyze.")


@app.get("/use-cases")
async def get_use_cases():
    """Récupère la liste de tous les use cases disponibles"""
    try:
        if not USE_CASES_PATH.exists():
            raise HTTPException(status_code=404, detail="Fichier use_cases.json non trouvé")
        
        with open(USE_CASES_PATH, "r", encoding="utf-8") as f:
            use_cases = json.load(f)
        
        return use_cases
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la lecture des use cases: {str(e)}")


@app.get("/use-cases/{use_case_id}")
async def get_use_case_data(use_case_id: str):
    """Charge les données pré-enregistrées d'un use case spécifique"""
    try:
        # Charger la liste des use cases
        if not USE_CASES_PATH.exists():
            raise HTTPException(status_code=404, detail="Fichier use_cases.json non trouvé")
        
        with open(USE_CASES_PATH, "r", encoding="utf-8") as f:
            use_cases_data = json.load(f)
        
        # Trouver le use case demandé
        use_case = None
        for uc in use_cases_data.get("use_cases", []):
            if uc.get("id") == use_case_id:
                use_case = uc
                break
        
        if not use_case:
            raise HTTPException(status_code=404, detail=f"Use case '{use_case_id}' non trouvé")
        
        # Charger le fichier de réponse
        response_file = use_case.get("response_file")
        if not response_file:
            raise HTTPException(status_code=404, detail=f"Pas de fichier de réponse défini pour ce use case")
        
        response_path = DATA_DIR / response_file
        if not response_path.exists():
            raise HTTPException(status_code=404, detail=f"Fichier de réponse non trouvé: {response_file}")
        
        with open(response_path, "r", encoding="utf-8") as f:
            response_data = json.load(f)
        
        # Normaliser la structure de la réponse pour qu'elle soit compatible avec le frontend
        graph = None
        graph_present = False
        analysis = None
        
        try:
            # Extraire l'analyse si elle existe
            if isinstance(response_data, dict) and 'analysis' in response_data:
                analysis = response_data['analysis']
            
            # Chercher les nodes et relationships à différents endroits
            nodes_data = []
            relationships_data = []
            
            # Cas 1: directement dans response_data
            if 'nodes' in response_data and 'relationships' in response_data:
                nodes_data = response_data.get('nodes', [])
                relationships_data = response_data.get('relationships', [])
            # Cas 2: dans response_data.data
            elif isinstance(response_data, dict) and 'data' in response_data:
                data_obj = response_data['data']
                if isinstance(data_obj, dict):
                    nodes_data = data_obj.get('nodes', [])
                    relationships_data = data_obj.get('relationships', [])
            # Cas 3: dans response_data.analysis.data
            elif isinstance(analysis, dict) and 'data' in analysis:
                data_obj = analysis['data']
                if isinstance(data_obj, dict):
                    nodes_data = data_obj.get('nodes', [])
                    relationships_data = data_obj.get('relationships', [])
            
            # Normaliser les nodes et edges
            nodes = []
            edges = []
            
            for n in nodes_data if isinstance(nodes_data, list) else []:
                if not isinstance(n, dict):
                    continue
                nid = str(n.get('id')) if n.get('id') is not None else (n.get('properties', {}).get('id') if isinstance(n.get('properties', {}), dict) else None)
                nid = str(nid) if nid is not None else (n.get('label') or f'node_{len(nodes)}')
                labels = n.get('labels') if isinstance(n.get('labels'), list) else []
                props = n.get('properties', {}) if isinstance(n.get('properties'), dict) else {}
                label = ', '.join(labels) if labels else (props.get('name') or nid)
                
                nodes.append({
                    'id': nid,
                    'label': label,
                    'labels': labels,
                    'properties': props
                })
            
            for r in relationships_data if isinstance(relationships_data, list) else []:
                if not isinstance(r, dict):
                    continue
                source = r.get('start_id') or r.get('from') or r.get('start')
                target = r.get('end_id') or r.get('to') or r.get('end')
                reltype = r.get('type') or r.get('relationship_type') or ''
                
                edges.append({
                    'from': str(source) if source is not None else None,
                    'to': str(target) if target is not None else None,
                    'label': reltype,
                    'properties': r.get('properties', {})
                })
            
            graph = {'nodes': nodes, 'edges': edges}
            graph_present = len(nodes) > 0
            
        except Exception as e:
            print(f"Erreur lors de la normalisation du graphe: {e}")
            import traceback
            traceback.print_exc()
            graph = {'nodes': [], 'edges': []}
            graph_present = False
        
        # Utiliser l'analyse existante ou créer une analyse synthétique
        if not analysis:
            analysis = {
                'status': 'success',
                'summary': f"Use case: {use_case.get('name')}",
                'technical_analysis': use_case.get('description', ''),
                'recommendations': [f"Ceci est un use case pré-enregistré: {use_case.get('name')}"],
                'query': use_case.get('cypher', ''),
                'timestamp': datetime.now().isoformat(),
                'original_question': use_case.get('name'),
                'record_count': len(graph.get('nodes', [])) if isinstance(graph, dict) and 'nodes' in graph else 0
            }
        else:
            # Mettre à jour le record_count avec le nombre réel de nodes
            if isinstance(graph, dict) and 'nodes' in graph:
                analysis['record_count'] = len(graph.get('nodes', []))

        
        return {
            'use_case': use_case,
            'analysis': analysis,
            'graph': graph,
            'graph_present': graph_present,
            'data_included': graph_present
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement du use case: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
