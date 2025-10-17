# ⚖️ DASHBOARD DE ANÁLISIS REGULATORIO VC
## Interfaz Visual para Análisis Regulatorio SaaS IA Copywriting LATAM

*Fecha: Diciembre 2024*  
*Versión: 1.0 - Dashboard Regulatorio*  
*Sector: SaaS IA Marketing/Copywriting*

---

## 🎨 INTERFAZ VISUAL COMPLETA

### **Dashboard HTML Interactivo**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard de Análisis Regulatorio</title>
    <style>
        .regulatory-dashboard {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            font-family: Arial, sans-serif;
        }
        .dashboard-header {
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
            margin: 10px 0;
        }
        .metric-label {
            color: #6c757d;
            font-size: 0.9em;
        }
        .regulatory-section {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .regulatory-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .regulatory-card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .regulatory-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .regulatory-name {
            font-size: 1.2em;
            font-weight: bold;
            color: #007bff;
        }
        .regulatory-score {
            background: #e9ecef;
            color: #495057;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
        }
        .regulatory-details {
            margin: 15px 0;
        }
        .regulatory-detail {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 10px;
            margin: 5px 0;
        }
        .regulatory-list {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin: 10px 0;
        }
        .regulation-tag {
            background: #007bff;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }
        .risk-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .risk-low { background-color: #28a745; }
        .risk-medium { background-color: #ffc107; }
        .risk-high { background-color: #dc3545; }
        .tabs {
            display: flex;
            margin: 20px 0;
        }
        .tab {
            padding: 10px 20px;
            background: #e9ecef;
            border: 1px solid #ddd;
            cursor: pointer;
            margin-right: 5px;
        }
        .tab.active {
            background: #007bff;
            color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .chart-container {
            height: 400px;
            margin: 20px 0;
        }
        .score-bar {
            background: #e9ecef;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin: 10px 0;
        }
        .score-fill {
            height: 100%;
            background: linear-gradient(90deg, #dc3545, #ffc107, #28a745);
            transition: width 0.3s ease;
        }
        .recommendations {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .recommendation-item {
            background: white;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 10px;
            margin: 5px 0;
        }
        .ranking-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .ranking-table th, .ranking-table td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        .ranking-table th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        .ranking-table tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .compliance-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .compliance-card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .compliance-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #007bff;
            margin: 10px 0;
        }
        .compliance-label {
            color: #6c757d;
            font-size: 0.9em;
        }
        .cost-breakdown {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .cost-item {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        .cost-value {
            font-size: 1.2em;
            font-weight: bold;
            color: #dc3545;
            margin: 5px 0;
        }
        .cost-label {
            color: #6c757d;
            font-size: 0.9em;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="regulatory-dashboard">
        <h1>⚖️ Dashboard de Análisis Regulatorio</h1>
        
        <div class="tabs">
            <div class="tab active" onclick="showTab('overview')">Resumen</div>
            <div class="tab" onclick="showTab('latam')">LATAM</div>
            <div class="tab" onclick="showTab('internacional')">Internacional</div>
            <div class="tab" onclick="showTab('sector')">Sector</div>
            <div class="tab" onclick="showTab('cumplimiento')">Cumplimiento</div>
            <div class="tab" onclick="showTab('costos')">Costos</div>
        </div>
        
        <div id="overview" class="tab-content active">
            <div class="dashboard-header">
                <h2>📊 Resumen Regulatorio</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">82</div>
                        <div class="metric-label">Score Regulatorio</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">5</div>
                        <div class="metric-label">Países LATAM</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">3</div>
                        <div class="metric-label">Regulaciones Internacionales</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">3</div>
                        <div class="metric-label">Sectores</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">$85K</div>
                        <div class="metric-label">Costo Total</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">Medio</div>
                        <div class="metric-label">Riesgo General</div>
                    </div>
                </div>
            </div>
            
            <div class="chart-container">
                <canvas id="overviewChart"></canvas>
            </div>
        </div>
        
        <div id="latam" class="tab-content">
            <h2>🌎 Regulaciones LATAM</h2>
            <div class="regulatory-grid">
                <div class="regulatory-card">
                    <div class="regulatory-header">
                        <div class="regulatory-name">México</div>
                        <div class="regulatory-score">85</div>
                    </div>
                    <div class="regulatory-details">
                        <div class="regulatory-detail">
                            <strong>Cumplimiento:</strong> 85%
                            <span class="risk-indicator risk-medium"></span>Medio
                        </div>
                        <div class="regulatory-detail">
                            <strong>Costo:</strong> $15,000
                        </div>
                        <div class="regulatory-detail">
                            <strong>Nivel:</strong> Excelente
                        </div>
                    </div>
                    <div class="regulatory-list">
                        <div class="regulation-tag">LFPDPPP</div>
                        <div class="regulation-tag">LFCE</div>
                        <div class="regulation-tag">Código Civil</div>
                        <div class="regulation-tag">Ley Fintech</div>
                    </div>
                </div>
                
                <div class="regulatory-card">
                    <div class="regulatory-header">
                        <div class="regulatory-name">Colombia</div>
                        <div class="regulatory-score">80</div>
                    </div>
                    <div class="regulatory-details">
                        <div class="regulatory-detail">
                            <strong>Cumplimiento:</strong> 80%
                            <span class="risk-indicator risk-medium"></span>Medio
                        </div>
                        <div class="regulatory-detail">
                            <strong>Costo:</strong> $12,000
                        </div>
                        <div class="regulatory-detail">
                            <strong>Nivel:</strong> Excelente
                        </div>
                    </div>
                    <div class="regulatory-list">
                        <div class="regulation-tag">Ley 1581</div>
                        <div class="regulation-tag">Circular Externa 100</div>
                        <div class="regulation-tag">Decreto 1377</div>
                        <div class="regulation-tag">Ley Fintech</div>
                    </div>
                </div>
                
                <div class="regulatory-card">
                    <div class="regulatory-header">
                        <div class="regulatory-name">Argentina</div>
                        <div class="regulatory-score">75</div>
                    </div>
                    <div class="regulatory-details">
                        <div class="regulatory-detail">
                            <strong>Cumplimiento:</strong> 75%
                            <span class="risk-indicator risk-high"></span>Alto
                        </div>
                        <div class="regulatory-detail">
                            <strong>Costo:</strong> $18,000
                        </div>
                        <div class="regulatory-detail">
                            <strong>Nivel:</strong> Bueno
                        </div>
                    </div>
                    <div class="regulatory-list">
                        <div class="regulation-tag">Ley 25.326</div>
                        <div class="regulation-tag">Resolución 4/2019</div>
                        <div class="regulation-tag">Código Civil</div>
                        <div class="regulation-tag">Ley Fintech</div>
                    </div>
                </div>
                
                <div class="regulatory-card">
                    <div class="regulatory-header">
                        <div class="regulatory-name">Chile</div>
                        <div class="regulatory-score">90</div>
                    </div>
                    <div class="regulatory-details">
                        <div class="regulatory-detail">
                            <strong>Cumplimiento:</strong> 90%
                            <span class="risk-indicator risk-low"></span>Bajo
                        </div>
                        <div class="regulatory-detail">
                            <strong>Costo:</strong> $10,000
                        </div>
                        <div class="regulatory-detail">
                            <strong>Nivel:</strong> Excelente
                        </div>
                    </div>
                    <div class="regulatory-list">
                        <div class="regulation-tag">Ley 19.628</div>
                        <div class="regulation-tag">Ley 20.575</div>
                        <div class="regulation-tag">Código Civil</div>
                        <div class="regulation-tag">Ley Fintech</div>
                    </div>
                </div>
                
                <div class="regulatory-card">
                    <div class="regulatory-header">
                        <div class="regulatory-name">Perú</div>
                        <div class="regulatory-score">78</div>
                    </div>
                    <div class="regulatory-details">
                        <div class="regulatory-detail">
                            <strong>Cumplimiento:</strong> 78%
                            <span class="risk-indicator risk-medium"></span>Medio
                        </div>
                        <div class="regulatory-detail">
                            <strong>Costo:</strong> $13,000
                        </div>
                        <div class="regulatory-detail">
                            <strong>Nivel:</strong> Bueno
                        </div>
                    </div>
                    <div class="regulatory-list">
                        <div class="regulation-tag">Ley 29733</div>
                        <div class="regulation-tag">Decreto Supremo 003-2013</div>
                        <div class="regulation-tag">Código Civil</div>
                        <div class="regulation-tag">Ley Fintech</div>
                    </div>
                </div>
            </div>
            
            <div class="regulatory-section">
                <h3>📊 Ranking LATAM</h3>
                <table class="ranking-table">
                    <thead>
                        <tr>
                            <th>Posición</th>
                            <th>País</th>
                            <th>Score</th>
                            <th>Nivel</th>
                            <th>Cumplimiento</th>
                            <th>Costo</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>1</td>
                            <td>Chile</td>
                            <td>90</td>
                            <td>Excelente</td>
                            <td>90%</td>
                            <td>$10,000</td>
                        </tr>
                        <tr>
                            <td>2</td>
                            <td>México</td>
                            <td>85</td>
                            <td>Excelente</td>
                            <td>85%</td>
                            <td>$15,000</td>
                        </tr>
                        <tr>
                            <td>3</td>
                            <td>Colombia</td>
                            <td>80</td>
                            <td>Excelente</td>
                            <td>80%</td>
                            <td>$12,000</td>
                        </tr>
                        <tr>
                            <td>4</td>
                            <td>Perú</td>
                            <td>78</td>
                            <td>Bueno</td>
                            <td>78%</td>
                            <td>$13,000</td>
                        </tr>
                        <tr>
                            <td>5</td>
                            <td>Argentina</td>
                            <td>75</td>
                            <td>Bueno</td>
                            <td>75%</td>
                            <td>$18,000</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <div id="internacional" class="tab-content">
            <h2>🌍 Regulaciones Internacionales</h2>
            <div class="regulatory-grid">
                <div class="regulatory-card">
                    <div class="regulatory-header">
                        <div class="regulatory-name">GDPR (Europa)</div>
                        <div class="regulatory-score">70</div>
                    </div>
                    <div class="regulatory-details">
                        <div class="regulatory-detail">
                            <strong>Aplicable:</strong> Sí
                        </div>
                        <div class="regulatory-detail">
                            <strong>Cumplimiento:</strong> 70%
                            <span class="risk-indicator risk-high"></span>Alto
                        </div>
                        <div class="regulatory-detail">
                            <strong>Costo:</strong> $25,000
                        </div>
                        <div class="regulatory-detail">
                            <strong>Nivel:</strong> Bueno
                        </div>
                    </div>
                </div>
                
                <div class="regulatory-card">
                    <div class="regulatory-header">
                        <div class="regulatory-name">CCPA (California)</div>
                        <div class="regulatory-score">75</div>
                    </div>
                    <div class="regulatory-details">
                        <div class="regulatory-detail">
                            <strong>Aplicable:</strong> Sí
                        </div>
                        <div class="regulatory-detail">
                            <strong>Cumplimiento:</strong> 75%
                            <span class="risk-indicator risk-medium"></span>Medio
                        </div>
                        <div class="regulatory-detail">
                            <strong>Costo:</strong> $20,000
                        </div>
                        <div class="regulatory-detail">
                            <strong>Nivel:</strong> Bueno
                        </div>
                    </div>
                </div>
                
                <div class="regulatory-card">
                    <div class="regulatory-header">
                        <div class="regulatory-name">PIPEDA (Canadá)</div>
                        <div class="regulatory-score">60</div>
                    </div>
                    <div class="regulatory-details">
                        <div class="regulatory-detail">
                            <strong>Aplicable:</strong> No
                        </div>
                        <div class="regulatory-detail">
                            <strong>Cumplimiento:</strong> 60%
                            <span class="risk-indicator risk-low"></span>Bajo
                        </div>
                        <div class="regulatory-detail">
                            <strong>Costo:</strong> $15,000
                        </div>
                        <div class="regulatory-detail">
                            <strong>Nivel:</strong> Regular
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="sector" class="tab-content">
            <h2>🏭 Regulaciones Sectoriales</h2>
            <div class="regulatory-grid">
                <div class="regulatory-card">
                    <div class="regulatory-header">
                        <div class="regulatory-name">Inteligencia Artificial</div>
                        <div class="regulatory-score">65</div>
                    </div>
                    <div class="regulatory-details">
                        <div class="regulatory-detail">
                            <strong>Cumplimiento:</strong> 65%
                            <span class="risk-indicator risk-high"></span>Alto
                        </div>
                        <div class="regulatory-detail">
                            <strong>Costo:</strong> $30,000
                        </div>
                        <div class="regulatory-detail">
                            <strong>Nivel:</strong> Regular
                        </div>
                    </div>
                    <div class="regulatory-list">
                        <div class="regulation-tag">AI Act (Europa)</div>
                        <div class="regulation-tag">Ley de IA (España)</div>
                        <div class="regulation-tag">Directrices IA (OCDE)</div>
                    </div>
                </div>
                
                <div class="regulatory-card">
                    <div class="regulatory-header">
                        <div class="regulatory-name">Fintech</div>
                        <div class="regulatory-score">80</div>
                    </div>
                    <div class="regulatory-details">
                        <div class="regulatory-detail">
                            <strong>Cumplimiento:</strong> 80%
                            <span class="risk-indicator risk-medium"></span>Medio
                        </div>
                        <div class="regulatory-detail">
                            <strong>Costo:</strong> $20,000
                        </div>
                        <div class="regulatory-detail">
                            <strong>Nivel:</strong> Excelente
                        </div>
                    </div>
                    <div class="regulatory-list">
                        <div class="regulation-tag">Ley Fintech (México)</div>
                        <div class="regulation-tag">Ley Fintech (Colombia)</div>
                        <div class="regulation-tag">Ley Fintech (Argentina)</div>
                    </div>
                </div>
                
                <div class="regulatory-card">
                    <div class="regulatory-header">
                        <div class="regulatory-name">Marketing</div>
                        <div class="regulatory-score">85</div>
                    </div>
                    <div class="regulatory-details">
                        <div class="regulatory-detail">
                            <strong>Cumplimiento:</strong> 85%
                            <span class="risk-indicator risk-low"></span>Bajo
                        </div>
                        <div class="regulatory-detail">
                            <strong>Costo:</strong> $10,000
                        </div>
                        <div class="regulatory-detail">
                            <strong>Nivel:</strong> Excelente
                        </div>
                    </div>
                    <div class="regulatory-list">
                        <div class="regulation-tag">CAN-SPAM</div>
                        <div class="regulation-tag">CASL</div>
                        <div class="regulation-tag">Ley de Publicidad</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="cumplimiento" class="tab-content">
            <h2>✅ Análisis de Cumplimiento</h2>
            <div class="compliance-grid">
                <div class="compliance-card">
                    <div class="compliance-value">82%</div>
                    <div class="compliance-label">Cumplimiento General</div>
                </div>
                <div class="compliance-card">
                    <div class="compliance-value">83%</div>
                    <div class="compliance-label">Cumplimiento LATAM</div>
                </div>
                <div class="compliance-card">
                    <div class="compliance-value">68%</div>
                    <div class="compliance-label">Cumplimiento Internacional</div>
                </div>
                <div class="compliance-card">
                    <div class="compliance-value">77%</div>
                    <div class="compliance-label">Cumplimiento Sectorial</div>
                </div>
            </div>
            
            <div class="chart-container">
                <canvas id="cumplimientoChart"></canvas>
            </div>
        </div>
        
        <div id="costos" class="tab-content">
            <h2>💰 Análisis de Costos</h2>
            <div class="cost-breakdown">
                <div class="cost-item">
                    <div class="cost-value">$68,000</div>
                    <div class="cost-label">LATAM</div>
                </div>
                <div class="cost-item">
                    <div class="cost-value">$45,000</div>
                    <div class="cost-label">Internacional</div>
                </div>
                <div class="cost-item">
                    <div class="cost-value">$60,000</div>
                    <div class="cost-label">Sectorial</div>
                </div>
                <div class="cost-item">
                    <div class="cost-value">$173,000</div>
                    <div class="cost-label">Total</div>
                </div>
            </div>
            
            <div class="chart-container">
                <canvas id="costosChart"></canvas>
            </div>
            
            <div class="recommendations">
                <h3>💡 Recomendaciones</h3>
                <div class="recommendation-item">Mejorar cumplimiento regulatorio general</div>
                <div class="recommendation-item">Fortalecer cumplimiento en LATAM</div>
                <div class="recommendation-item">Mejorar cumplimiento internacional</div>
                <div class="recommendation-item">Fortalecer cumplimiento sectorial</div>
                <div class="recommendation-item">Reducir riesgo regulatorio general</div>
                <div class="recommendation-item">Mitigar riesgos en LATAM</div>
                <div class="recommendation-item">Reducir riesgos internacionales</div>
                <div class="recommendation-item">Mitigar riesgos sectoriales</div>
                <div class="recommendation-item">Optimizar costos regulatorios</div>
                <div class="recommendation-item">Reducir costos en LATAM</div>
                <div class="recommendation-item">Optimizar costos internacionales</div>
                <div class="recommendation-item">Reducir costos sectoriales</div>
                <div class="recommendation-item">Explotar oportunidades regulatorias</div>
                <div class="recommendation-item">Usar cumplimiento como diferenciador</div>
                <div class="recommendation-item">Construir confianza regulatoria</div>
                <div class="recommendation-item">Facilitar expansión regulatoria</div>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            // Ocultar todos los tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Remover clase active de todos los tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Mostrar el tab seleccionado
            document.getElementById(tabName).classList.add('active');
            
            // Agregar clase active al tab clickeado
            event.target.classList.add('active');
        }
        
        // Crear gráfico de resumen
        const ctx1 = document.getElementById('overviewChart').getContext('2d');
        new Chart(ctx1, {
            type: 'radar',
            data: {
                labels: ['Cumplimiento', 'Riesgo', 'Costo', 'Oportunidad', 'LATAM'],
                datasets: [{
                    label: 'Score Regulatorio',
                    data: [82, 70, 75, 85, 83],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20
                        }
                    }
                }
            }
        });
        
        // Crear gráfico de cumplimiento
        const ctx2 = document.getElementById('cumplimientoChart').getContext('2d');
        new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: ['General', 'LATAM', 'Internacional', 'Sectorial'],
                datasets: [{
                    label: 'Cumplimiento (%)',
                    data: [82, 83, 68, 77],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(220, 53, 69, 0.8)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(40, 167, 69, 1)',
                        'rgba(255, 193, 7, 1)',
                        'rgba(220, 53, 69, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Cumplimiento (%)'
                        }
                    }
                }
            }
        });
        
        // Crear gráfico de costos
        const ctx3 = document.getElementById('costosChart').getContext('2d');
        new Chart(ctx3, {
            type: 'doughnut',
            data: {
                labels: ['LATAM', 'Internacional', 'Sectorial'],
                datasets: [{
                    data: [68000, 45000, 60000],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(220, 53, 69, 0.8)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 193, 7, 1)',
                        'rgba(220, 53, 69, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    </script>
</body>
</html>
```

---

*Dashboard de análisis regulatorio preparado para SaaS IA Copywriting LATAM*  
*Versión 1.0 - Diciembre 2024*






