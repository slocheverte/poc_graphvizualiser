from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum

app = FastAPI(title="Cybersecurity Graph Analysis Client API")

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
            "GET /files": "Liste tous les fichiers de résultats disponibles",
            "GET /analysis/{filename}": "Récupère un résultat d'analyse",
            "POST /analysis/mock": "Génère un résultat d'analyse mock pour test",
            "GET /graph/{filename}": "Récupère les données formatées pour la visualisation",
            "GET /stats/{filename}": "Récupère les statistiques d'une analyse",
            "GET /schema": "Récupère le schéma JSON de réponse"
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
    """Liste tous les fichiers de résultats d'analyse disponibles"""
    try:
        DATA_DIR.mkdir(exist_ok=True)
        json_files = [f.name for f in DATA_DIR.glob("*.json")]
        return {"files": json_files, "count": len(json_files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analysis/{filename}")
async def get_analysis(filename: str):
    """Récupère un résultat d'analyse de cybersécurité"""
    file_path = DATA_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fichier d'analyse non trouvé")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Validation optionnelle avec Pydantic
        try:
            validated = CybersecurityAnalysisResponse(**data)
            return {"filename": filename, "data": data, "validation": "passed"}
        except Exception as validation_error:
            return {
                "filename": filename, 
                "data": data, 
                "validation": "failed",
                "validation_errors": str(validation_error)
            }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Fichier JSON invalide")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analysis/mock")
async def create_mock_analysis(query: AnalysisQuery):
    """Génère un résultat d'analyse mock pour tester le système"""
    mock_response = {
        "status": "success",
        "summary": f"Analyse mock pour la requête: '{query.query[:50]}...'",
        "technical_analysis": "Cette analyse est générée pour démonstration. Dans un système réel, "
                             "elle contiendrait les résultats détaillés de l'analyse de graphe.",
        "recommendations": [
            "Vérifier les dispositifs critiques identifiés",
            "Appliquer les correctifs de sécurité nécessaires",
            "Surveiller les connexions suspectes"
        ],
        "recommendations_with_impact": [
            {
                "recommendation": "Isoler les dispositifs à haut risque",
                "impact": "High",
                "effort": "Medium",
                "priority": 1
            },
            {
                "recommendation": "Mettre à jour les systèmes exposés",
                "impact": "High",
                "effort": "Low",
                "priority": 2
            }
        ],
        "confidence": "High",
        "threat_level": "Medium",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "original_question": query.query,
        "record_count": 5,
        "data": [
            {
                "type": "node",
                "id": "device-001",
                "labels": ["Device", "Critical"],
                "properties": {
                    "ip": "192.168.1.10",
                    "criticality": "High",
                    "os": "Windows Server 2019"
                }
            },
            {
                "type": "node",
                "id": "device-002",
                "labels": ["Device"],
                "properties": {
                    "ip": "192.168.1.20",
                    "criticality": "Medium"
                }
            },
            {
                "type": "relationship",
                "relationship_type": "CONNECTS_TO",
                "from": "device-001",
                "to": "device-002",
                "properties": {
                    "port": 445,
                    "protocol": "SMB"
                }
            }
        ]
    }
    
    # Sauvegarde optionnelle
    filename = f"mock_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    file_path = DATA_DIR / filename
    DATA_DIR.mkdir(exist_ok=True)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(mock_response, f, indent=2, ensure_ascii=False)
    
    return {
        "message": "Analyse mock générée avec succès",
        "filename": filename,
        "data": mock_response
    }


@app.post("/data")
async def save_data(json_data: JsonData):
    """Enregistre des données JSON dans un fichier"""
    file_path = DATA_DIR / json_data.filename
    
    try:
        DATA_DIR.mkdir(exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(json_data.data, f, indent=2, ensure_ascii=False)
        return {"message": "Données enregistrées avec succès", "filename": json_data.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/graph/{filename}")
async def get_graph_data(filename: str):
    """
    Récupère les données d'analyse formatées pour la visualisation en graphe de cybersécurité.
    Extrait les nœuds et relations du champ 'data' de la réponse d'analyse.
    """
    file_path = DATA_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            analysis_data = json.load(f)
        
        nodes = []
        edges = []
        node_map = {}  # Pour éviter les doublons
        
        # Si le fichier contient un champ 'data' avec des records
        if "data" in analysis_data and isinstance(analysis_data["data"], list):
            for record in analysis_data["data"]:
                record_type = record.get("type", "unknown")
                
                # Traitement des nœuds
                if record_type == "node":
                    node_id = record.get("id", f"node_{len(nodes)}")
                    if node_id not in node_map:
                        labels = record.get("labels", [])
                        properties = record.get("properties", {})
                        
                        # Construction du label d'affichage
                        display_label = ", ".join(labels) if labels else str(node_id)
                        
                        # Extraction d'informations clés pour l'affichage
                        details = []
                        if "ip" in properties:
                            details.append(f"IP: {properties['ip']}")
                        if "criticality" in properties:
                            details.append(f"Criticality: {properties['criticality']}")
                        
                        node = {
                            "id": node_id,
                            "label": display_label,
                            "title": "\n".join(details) if details else display_label,
                            "type": "device" if "Device" in labels else labels[0] if labels else "node",
                            "properties": properties,
                            "labels": labels
                        }
                        
                        nodes.append(node)
                        node_map[node_id] = len(nodes) - 1
                
                # Traitement des relations
                elif record_type == "relationship":
                    from_node = record.get("from")
                    to_node = record.get("to")
                    rel_type = record.get("relationship_type", "RELATED_TO")
                    
                    if from_node and to_node:
                        edge = {
                            "from": from_node,
                            "to": to_node,
                            "label": rel_type,
                            "title": rel_type,
                            "properties": record.get("properties", {})
                        }
                        edges.append(edge)
        
        # Si pas de données structurées, traitement générique du JSON
        else:
            def process_generic(obj, parent_id=None, parent_key="root"):
                node_id = len(nodes)
                
                if isinstance(obj, dict):
                    nodes.append({
                        "id": node_id,
                        "label": parent_key,
                        "type": "object",
                        "value": f"{{{len(obj)} keys}}",
                        "properties": obj
                    })
                    
                    if parent_id is not None:
                        edges.append({"from": parent_id, "to": node_id})
                    
                    for key, value in obj.items():
                        if key != "data":  # Éviter la récursion sur le champ data
                            process_generic(value, node_id, key)
                            
                elif isinstance(obj, list) and len(obj) > 0:
                    nodes.append({
                        "id": node_id,
                        "label": parent_key,
                        "type": "array",
                        "value": f"[{len(obj)} items]"
                    })
                    
                    if parent_id is not None:
                        edges.append({"from": parent_id, "to": node_id})
                    
                    for idx, item in enumerate(obj[:10]):  # Limiter à 10 items
                        process_generic(item, node_id, f"[{idx}]")
            
            process_generic(analysis_data)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "filename": filename,
            "metadata": {
                "status": analysis_data.get("status"),
                "threat_level": analysis_data.get("threat_level"),
                "confidence": analysis_data.get("confidence"),
                "record_count": analysis_data.get("record_count", len(nodes))
            }
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Fichier JSON invalide")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats/{filename}")
async def get_analysis_stats(filename: str):
    """Récupère les statistiques d'une analyse"""
    file_path = DATA_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        stats = {
            "filename": filename,
            "status": data.get("status"),
            "threat_level": data.get("threat_level"),
            "confidence": data.get("confidence"),
            "record_count": data.get("record_count", 0),
            "has_recommendations": bool(data.get("recommendations")),
            "recommendation_count": len(data.get("recommendations", [])) if isinstance(data.get("recommendations"), list) else 1,
            "has_data": bool(data.get("data")),
            "timestamp": data.get("timestamp"),
            "execution_time": data.get("execution_time")
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
