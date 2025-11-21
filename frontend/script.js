// Configuration de l'URL de l'API
const API_URL = 'http://localhost:8001';

// Debug helper: intercept any client-side request to /files and log stack trace + block it.
(function(){
    try {
        const origFetch = window.fetch;
        window.fetch = function(input, init){
            try {
                const url = (typeof input === 'string') ? input : (input && input.url);
                if (url && url.indexOf('/files') !== -1) {
                    console.warn('[debug] Blocked fetch to /files ->', url);
                    console.trace();
                    return Promise.resolve(new Response(JSON.stringify({detail: 'blocked by client interceptor'}), {status:404, headers: {'Content-Type':'application/json'}}));
                }
            } catch (e) { console.error('fetch interceptor error', e); }
            return origFetch.apply(this, arguments);
        };

        const origXOpen = XMLHttpRequest.prototype.open;
        const origXSend = XMLHttpRequest.prototype.send;
        XMLHttpRequest.prototype.open = function(method, url){
            this.__openedUrl = url;
            return origXOpen.apply(this, arguments);
        };
        XMLHttpRequest.prototype.send = function(body){
            try {
                if (this.__openedUrl && String(this.__openedUrl).indexOf('/files') !== -1) {
                    console.warn('[debug] Blocked XHR to /files ->', this.__openedUrl);
                    console.trace();
                    // simulate async 404 response
                    const self = this;
                    setTimeout(() => {
                        try { self.readyState = 4; self.status = 404; } catch(e){}
                        if (typeof self.onreadystatechange === 'function') try{ self.onreadystatechange(); }catch(e){}
                        if (typeof self.onload === 'function') try{ self.onload(); }catch(e){}
                    }, 0);
                    return;
                }
            } catch(e){ console.error('XHR interceptor error', e); }
            return origXSend.apply(this, arguments);
        };
    } catch (e) {
        console.error('Error installing /files interceptor', e);
    }
})();

console.log('Loaded script.js v3 (D3)');

// Variables globales pour rendu D3
let svg = null;
let simulation = null;
let linkGroup = null;
let nodeGroup = null;
let linkElements = null;
let nodeElements = null;
let currentAnalysisData = null;

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    initNetwork();
    loadUpstreamConfig();
});


// Charge la configuration de l'upstream depuis le backend
async function loadUpstreamConfig() {
    try {
        const resp = await fetch(`${API_URL}/config/upstream`);
        const data = await resp.json();
        const input = document.getElementById('upstreamInput');
        const status = document.getElementById('upstreamStatus');
        if (data && data.upstream) {
            if (input) input.value = data.upstream;
            if (status) status.textContent = `(configuré: ${data.upstream})`;
        } else {
            if (input) input.value = '';
            if (status) status.textContent = '(non configuré)';
        }
    } catch (e) {
        console.warn('Impossible de charger la config upstream:', e.message);
    }
}

// Configure l'upstream via le backend (frontend-controlled)
async function setUpstream() {
    const input = document.getElementById('upstreamInput');
    const url = input.value.trim();
    if (!url) {
        showMessage('Veuillez renseigner une URL upstream', 'warning');
        return;
    }

    try {
        const resp = await fetch(`${API_URL}/config/upstream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ upstream: url })
        });

        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err.detail || 'Erreur lors de la configuration');
        }

        const result = await resp.json();
    const upstreamStatusEl = document.getElementById('upstreamStatus');
    if (upstreamStatusEl) upstreamStatusEl.textContent = `(configuré: ${result.upstream})`;
        showMessage('Upstream configuré', 'success');
        // La liste de fichiers a été supprimée; on ne la rafraîchit plus
    } catch (e) {
        showMessage('Erreur: ' + e.message, 'error');
    }
}

// Initialise le rendu D3 pour la visualisation du graphe (configuration cybersécurité)
function initNetwork() {
    const container = document.getElementById('network');
    // clear any previous content
    if (!container) {
        console.warn('initNetwork: #network container not found');
        return;
    }
    container.innerHTML = '';

    const width = container.clientWidth || 800;
    const height = 600;

    svg = d3.select(container)
        .append('svg')
        .attr('width', '100%')
        .attr('height', height)
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet');

    // defs for arrow markers
    const defs = svg.append('defs');
    defs.append('marker')
        .attr('id', 'arrow')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 20)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#95a5a6');

    // groups
    linkGroup = svg.append('g').attr('class', 'links');
    nodeGroup = svg.append('g').attr('class', 'nodes');

    // zoom
    const zoom = d3.zoom().on('zoom', (event) => {
        linkGroup.attr('transform', event.transform);
        nodeGroup.attr('transform', event.transform);
    });
    svg.call(zoom);

    // initial empty simulation; created on render
    simulation = null;
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
    
    if (detailsDiv) detailsDiv.innerHTML = html;
}

// La gestion des fichiers locaux a été retirée : la frontend n'interroge plus /files

// La charge d'analyses par fichier local a été supprimée.
// Désormais, les analyses sont déclenchées via `analyzeQuestion()` et le backend fournit les données à afficher.

// Met à jour la barre de statut
function updateStatusBar(data) {
    const statusEl = document.getElementById('analysisStatus');
    if (statusEl) {
        statusEl.textContent = data.status || '-';
        statusEl.className = 'badge ' + (data.status || '').toLowerCase();
    }

    const threatEl = document.getElementById('threatLevel');
    if (threatEl) {
        threatEl.textContent = data.threat_level || '-';
        threatEl.className = 'badge ' + (data.threat_level || '').toLowerCase();
    }

    const confEl = document.getElementById('confidenceLevel');
    if (confEl) {
        confEl.textContent = data.confidence || '-';
        confEl.className = 'badge ' + (data.confidence || '').toLowerCase();
    }

    const rc = document.getElementById('recordCount');
    if (rc) rc.textContent = data.record_count || 0;
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
    
    if (summaryDiv) summaryDiv.innerHTML = html;
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
    if (recDiv) recDiv.innerHTML = html;
    } else if (data.recommendations) {
        const recs = Array.isArray(data.recommendations) ? data.recommendations : [data.recommendations];
        let html = '<ul style="margin-left: 20px;">';
        recs.forEach(rec => {
            html += `<li style="margin-bottom: 10px;">${rec}</li>`;
        });
        html += '</ul>';
    if (recDiv) recDiv.innerHTML = html;
    } else {
    if (recDiv) recDiv.innerHTML = '<p style="color: #95a5a6;">Aucune recommandation disponible</p>';
    }
}

// Affiche l'analyse technique
function displayTechnicalAnalysis(data) {
    const techDiv = document.getElementById('technicalAnalysis');
    if (techDiv) techDiv.innerHTML = `<p>${data.technical_analysis || 'Aucune analyse technique disponible'}</p>`;
    
    if (data.insights) {
        const insights = Array.isArray(data.insights) ? data.insights : [data.insights];
        let html = '<h4 style="color: #3498db; margin-top: 15px;">🔍 Insights:</h4><ul style="margin-left: 20px;">';
        insights.forEach(insight => {
            html += `<li style="margin-bottom: 8px;">${insight}</li>`;
        });
        html += '</ul>';
        if (techDiv) techDiv.innerHTML += html;
    }
}

// Envoie une question vers l'endpoint analyze de l'upstream via le backend
async function analyzeQuestion() {
    const qEl = document.getElementById('questionInput');
    const question = (qEl && qEl.value) ? qEl.value : 'What are Internet-Exposed Devices?';

    try {
        const response = await fetch(`${API_URL}/upstream/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || 'Erreur lors de la requête d\'analyse');
        }

        const result = await response.json();

        // Normalise la réponse pour l'affichage
        const analysis = result.analysis || result.data || result;
        currentAnalysisData = analysis;

        updateStatusBar(analysis);
        displaySummary(analysis);
        displayRecommendations(analysis);
        displayTechnicalAnalysis(analysis);
    const jsonDisplayEl = document.getElementById('jsonDisplay');
    if (jsonDisplayEl) jsonDisplayEl.textContent = JSON.stringify(analysis, null, 2);

        // Si le backend a renvoyé un graphe, le rendre
        if (result && result.graph && Array.isArray(result.graph.nodes) && Array.isArray(result.graph.edges)) {
            const graphData = JSON.parse(JSON.stringify(result.graph));
            graphData.nodes.forEach(node => {
                node.color = getNodeColor(node);
                if (node.id === undefined || node.id === null) node.id = node.label || Math.random().toString(36).slice(2,9);
                node.id = String(node.id);
            });
            renderGraph(graphData);
            showMessage('Graphe rendu', 'success');
        }

        showMessage('Analyse reçue', 'success');
    } catch (error) {
        showMessage('Erreur: ' + error.message, 'error');
        console.error(error);
    }
}

// Retourne une couleur selon le type et la criticité du nœud
function getNodeColor(node) {
    try {
        // Priorité à la criticité si présente dans les propriétés
        const critRaw = node?.properties?.criticality;
        if (critRaw !== undefined && critRaw !== null) {
            const crit = String(critRaw).toLowerCase();
            if (crit === 'critical') return '#ff6b6b';
            if (crit === 'high') return '#ee5a6f';
            if (crit === 'medium') return '#feca57';
            if (crit === 'low') return '#48dbfb';
        }

        // Couleur selon les labels
        if (Array.isArray(node.labels)) {
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

        return colors[String(node.type).toLowerCase()] || '#7f8c8d';
    } catch (e) {
        return '#7f8c8d';
    }
}

// Render graph with D3 (force-directed)
function renderGraph(graphData) {
    const nodes = graphData.nodes.map(n => ({
        id: String(n.id),
        label: n.label || String(n.id),
        type: n.type,
        labels: n.labels,
        properties: n.properties,
        color: n.color || getNodeColor(n)
    }));

    const links = graphData.edges.map((e, i) => ({
        id: e.id ?? `e${i}`,
        source: String(e.from ?? e.source),
        target: String(e.to ?? e.target),
        label: e.label
    }));

    // stop previous simulation
    if (simulation) {
        simulation.stop();
        simulation = null;
    }

    // clear previous elements
    linkGroup.selectAll('*').remove();
    nodeGroup.selectAll('*').remove();

    // create links
    linkElements = linkGroup.selectAll('line')
        .data(links, d => d.id)
        .enter()
        .append('line')
        .attr('stroke', '#95a5a6')
        .attr('stroke-width', 2)
        .attr('marker-end', 'url(#arrow)');

    // create nodes as groups with rect + text
    nodeElements = nodeGroup.selectAll('g')
        .data(nodes, d => d.id)
        .enter()
        .append('g')
        .attr('class', 'node')
        .call(d3.drag()
            .on('start', (event, d) => {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            })
            .on('drag', (event, d) => {
                d.fx = event.x;
                d.fy = event.y;
            })
            .on('end', (event, d) => {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            })
        )
        .on('click', (event, d) => {
            // affichage des détails
            displayNodeDetails(d);
        });

    // append rect and text
    nodeElements.append('rect')
        .attr('x', -50)
        .attr('y', -14)
        .attr('width', 100)
        .attr('height', 28)
        .attr('rx', 6)
        .attr('ry', 6)
        .attr('fill', d => d.color)
        .attr('stroke', '#222');

    nodeElements.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em')
        .attr('fill', '#ecf0f1')
        .style('pointer-events', 'none')
        .text(d => d.label);

    // adjust rect size to text width
    nodeElements.each(function(d) {
        const g = d3.select(this);
        const text = g.select('text');
        const rect = g.select('rect');
        const bbox = text.node().getBBox();
        rect.attr('width', Math.max(80, bbox.width + 20))
            .attr('x', - (Math.max(80, bbox.width + 20) / 2));
    });

    // simulation
    const width = svg.node().viewBox.baseVal.width || svg.node().clientWidth || 800;
    const height = svg.node().viewBox.baseVal.height || 600;

    simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(140).strength(1))
        .force('charge', d3.forceManyBody().strength(-400))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(d => 50))
        .on('tick', () => {
            linkElements
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            nodeElements.attr('transform', d => `translate(${d.x},${d.y})`);
        });

    // keep nodes/links references to simulation nodes/links
    simulation.nodes(nodes);
    simulation.force('link').links(links);

    // fit view
    try {
        const all = svg.node();
        // optional: center or fit - quick fit by centering
    } catch (e) {}
}

// Toggle l'affichage du JSON
function toggleJsonView() {
    const jsonEl = document.getElementById('jsonDisplay');
    if (!jsonEl) return;
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
