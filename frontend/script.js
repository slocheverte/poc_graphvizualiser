// Configuration de l'URL de l'API
const API_URL = 'http://localhost:8000';

// Variables globales
let network = null;
let currentAnalysisData = null;

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    initNetwork();
    refreshFileList();
});

// Initialise le réseau vis.js avec configuration pour cybersécurité
function initNetwork() {
    const container = document.getElementById('network');
    const data = {
        nodes: [],
        edges: []
    };
    
    const options = {
        nodes: {
            shape: 'box',
            margin: 10,
            widthConstraint: {
                maximum: 200
            },
            font: {
                size: 14,
                face: 'Arial',
                color: '#ecf0f1'
            },
            borderWidth: 2,
            shadow: true
        },
        edges: {
            arrows: {
                to: { enabled: true, scaleFactor: 0.8 }
            },
            smooth: {
                type: 'cubicBezier',
                roundness: 0.5
            },
            font: {
                size: 12,
                color: '#95a5a6',
                background: '#16213e'
            },
            width: 2,
            shadow: true
        },
        physics: {
            enabled: true,
            hierarchicalRepulsion: {
                nodeDistance: 180
            },
            solver: 'hierarchicalRepulsion'
        },
        layout: {
            hierarchical: {
                direction: 'UD',
                sortMethod: 'directed',
                nodeSpacing: 200,
                levelSeparation: 200
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 100,
            navigationButtons: true,
            keyboard: true
        }
    };
    
    network = new vis.Network(container, data, options);
    
    // Événement de clic sur un nœud
    network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const nodeData = network.body.data.nodes.get(nodeId);
            displayNodeDetails(nodeData);
        }
    });
}

// Affiche les détails d'un nœud sélectionné
function displayNodeDetails(nodeData) {
    const detailsDiv = document.getElementById('nodeDetails');
    
    let html = `<h4 style="color: #3498db; margin-bottom: 10px;">${nodeData.label}</h4>`;
    
    if (nodeData.labels && nodeData.labels.length > 0) {
        html += `<p><strong>Labels:</strong> ${nodeData.labels.join(', ')}</p>`;
    }
    
    if (nodeData.type) {
        html += `<p><strong>Type:</strong> ${nodeData.type}</p>`;
    }
    
    if (nodeData.properties) {
        html += `<p><strong>Propriétés:</strong></p><ul style="margin-left: 20px;">`;
        for (const [key, value] of Object.entries(nodeData.properties)) {
            html += `<li><strong>${key}:</strong> ${JSON.stringify(value)}</li>`;
        }
        html += `</ul>`;
    }
    
    detailsDiv.innerHTML = html;
}

// Rafraîchit la liste des fichiers d'analyse
async function refreshFileList() {
    try {
        const response = await fetch(`${API_URL}/files`);
        const data = await response.json();
        
        const select = document.getElementById('fileSelect');
        select.innerHTML = '<option value="">-- Sélectionner un fichier --</option>';
        
        data.files.forEach(file => {
            const option = document.createElement('option');
            option.value = file;
            option.textContent = file;
            select.appendChild(option);
        });
        
        showMessage(`${data.count} fichier(s) d'analyse trouvé(s)`, 'success');
    } catch (error) {
        showMessage('Erreur lors de la récupération des fichiers: ' + error.message, 'error');
    }
}

// Charge une analyse sélectionnée
async function loadAnalysis() {
    const select = document.getElementById('fileSelect');
    const filename = select.value;
    
    if (!filename) {
        showMessage('Veuillez sélectionner un fichier', 'warning');
        return;
    }
    
    try {
        // Récupère l'analyse complète
        const analysisResponse = await fetch(`${API_URL}/analysis/${filename}`);
        const analysisResult = await analysisResponse.json();
        currentAnalysisData = analysisResult.data;
        
        // Met à jour la barre de statut
        updateStatusBar(currentAnalysisData);
        
        // Affiche le résumé
        displaySummary(currentAnalysisData);
        
        // Affiche les recommandations
        displayRecommendations(currentAnalysisData);
        
        // Affiche l'analyse technique
        displayTechnicalAnalysis(currentAnalysisData);
        
        // Affiche le JSON brut
        document.getElementById('jsonDisplay').textContent = JSON.stringify(currentAnalysisData, null, 2);
        
        // Récupère les données du graphe
        const graphResponse = await fetch(`${API_URL}/graph/${filename}`);
        const graphData = await graphResponse.json();
        
        // Applique les couleurs selon la criticité
        graphData.nodes.forEach(node => {
            node.color = getNodeColor(node);
        });
        
        // Met à jour le réseau
        network.setData({
            nodes: graphData.nodes,
            edges: graphData.edges
        });
        
        showMessage(`Analyse "${filename}" chargée avec succès`, 'success');
    } catch (error) {
        showMessage('Erreur lors du chargement de l\'analyse: ' + error.message, 'error');
        console.error(error);
    }
}

// Met à jour la barre de statut
function updateStatusBar(data) {
    const statusEl = document.getElementById('analysisStatus');
    statusEl.textContent = data.status || '-';
    statusEl.className = 'badge ' + (data.status || '').toLowerCase();
    
    const threatEl = document.getElementById('threatLevel');
    threatEl.textContent = data.threat_level || '-';
    threatEl.className = 'badge ' + (data.threat_level || '').toLowerCase();
    
    const confEl = document.getElementById('confidenceLevel');
    confEl.textContent = data.confidence || '-';
    confEl.className = 'badge ' + (data.confidence || '').toLowerCase();
    
    document.getElementById('recordCount').textContent = data.record_count || 0;
}

// Affiche le résumé
function displaySummary(data) {
    const summaryDiv = document.getElementById('summaryContent');
    
    let html = `<p style="margin-bottom: 15px;">${data.summary || 'Aucun résumé disponible'}</p>`;
    
    if (data.data_summary) {
        html += `<p style="color: #95a5a6; font-size: 0.9em;"><strong>Données:</strong> ${data.data_summary}</p>`;
    }
    
    if (data.timestamp) {
        const date = new Date(data.timestamp);
        html += `<p style="color: #95a5a6; font-size: 0.85em; margin-top: 10px;">📅 ${date.toLocaleString()}</p>`;
    }
    
    summaryDiv.innerHTML = html;
}

// Affiche les recommandations
function displayRecommendations(data) {
    const recDiv = document.getElementById('recommendationsContent');
    
    if (data.recommendations_with_impact && data.recommendations_with_impact.length > 0) {
        let html = '';
        data.recommendations_with_impact.forEach(rec => {
            const priority = rec.priority || 999;
            html += `
                <div class="recommendation-item priority-${Math.min(priority, 3)}">
                    <div class="rec-text">${rec.recommendation}</div>
                    <div class="rec-meta">
                        ${rec.impact ? `<span>Impact: ${rec.impact}</span>` : ''}
                        ${rec.effort ? `<span>Effort: ${rec.effort}</span>` : ''}
                        ${rec.priority ? `<span>Priorité: ${rec.priority}</span>` : ''}
                    </div>
                </div>
            `;
        });
        recDiv.innerHTML = html;
    } else if (data.recommendations) {
        const recs = Array.isArray(data.recommendations) ? data.recommendations : [data.recommendations];
        let html = '<ul style="margin-left: 20px;">';
        recs.forEach(rec => {
            html += `<li style="margin-bottom: 10px;">${rec}</li>`;
        });
        html += '</ul>';
        recDiv.innerHTML = html;
    } else {
        recDiv.innerHTML = '<p style="color: #95a5a6;">Aucune recommandation disponible</p>';
    }
}

// Affiche l'analyse technique
function displayTechnicalAnalysis(data) {
    const techDiv = document.getElementById('technicalAnalysis');
    techDiv.innerHTML = `<p>${data.technical_analysis || 'Aucune analyse technique disponible'}</p>`;
    
    if (data.insights) {
        const insights = Array.isArray(data.insights) ? data.insights : [data.insights];
        let html = '<h4 style="color: #3498db; margin-top: 15px;">🔍 Insights:</h4><ul style="margin-left: 20px;">';
        insights.forEach(insight => {
            html += `<li style="margin-bottom: 8px;">${insight}</li>`;
        });
        html += '</ul>';
        techDiv.innerHTML += html;
    }
}

// Génère une analyse mock
async function generateMockAnalysis() {
    const query = document.getElementById('mockQuery').value || 'Test de requête par défaut';
    
    try {
        const response = await fetch(`${API_URL}/analysis/mock`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                context: {}
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            showMessage(`Analyse mock générée: ${result.filename}`, 'success');
            await refreshFileList();
            
            // Sélectionne automatiquement le fichier créé
            document.getElementById('fileSelect').value = result.filename;
            await loadAnalysis();
        } else {
            throw new Error('Erreur lors de la génération');
        }
    } catch (error) {
        showMessage('Erreur: ' + error.message, 'error');
        console.error(error);
    }
}

// Retourne une couleur selon le type et la criticité du nœud
function getNodeColor(node) {
    // Priorité à la criticité si présente dans les propriétés
    if (node.properties && node.properties.criticality) {
        const crit = node.properties.criticality.toLowerCase();
        if (crit === 'critical') return '#ff6b6b';
        if (crit === 'high') return '#ee5a6f';
        if (crit === 'medium') return '#feca57';
        if (crit === 'low') return '#48dbfb';
    }
    
    // Couleur selon les labels
    if (node.labels) {
        if (node.labels.includes('Vulnerability') || node.labels.includes('CVE')) {
            return '#e74c3c';
        }
        if (node.labels.includes('Device') || node.labels.includes('Server')) {
            return '#3498db';
        }
        if (node.labels.includes('User') || node.labels.includes('Account')) {
            return '#9b59b6';
        }
        if (node.labels.includes('Network') || node.labels.includes('Subnet')) {
            return '#1abc9c';
        }
    }
    
    // Couleur selon le type
    const colors = {
        'device': '#3498db',
        'vulnerability': '#e74c3c',
        'user': '#9b59b6',
        'network': '#1abc9c',
        'object': '#95a5a6',
        'array': '#f39c12',
        'string': '#27ae60',
        'number': '#8e44ad'
    };
    
    return colors[node.type] || '#7f8c8d';
}

// Toggle l'affichage du JSON
function toggleJsonView() {
    const jsonEl = document.getElementById('jsonDisplay');
    jsonEl.style.display = jsonEl.style.display === 'none' ? 'block' : 'none';
}

// Affiche un message temporaire (toast notification)
function showMessage(message, type = 'info') {
    const toast = document.createElement('div');
    toast.textContent = message;
    
    const colors = {
        success: '#27ae60',
        error: '#e74c3c',
        warning: '#f39c12',
        info: '#3498db'
    };
    
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${colors[type] || colors.info};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        font-weight: bold;
        animation: slideIn 0.3s ease-out;
        max-width: 400px;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Ajoute les animations CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);
