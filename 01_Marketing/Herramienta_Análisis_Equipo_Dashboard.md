# 👥 DASHBOARD DE ANÁLISIS DE EQUIPO VC
## Interfaz Visual para Análisis de Equipo y Liderazgo SaaS IA Copywriting LATAM

*Fecha: Diciembre 2024*  
*Versión: 1.0 - Dashboard de Equipo*  
*Sector: SaaS IA Marketing/Copywriting*

---

## 🎨 INTERFAZ VISUAL COMPLETA

### **Dashboard HTML Interactivo**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard de Análisis de Equipo</title>
    <style>
        .team-dashboard {
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
        .team-section {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .team-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .team-card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .team-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .team-name {
            font-size: 1.2em;
            font-weight: bold;
            color: #007bff;
        }
        .team-role {
            background: #e9ecef;
            color: #495057;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
        }
        .team-details {
            margin: 15px 0;
        }
        .team-detail {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 10px;
            margin: 5px 0;
        }
        .strengths, .weaknesses {
            margin: 15px 0;
        }
        .strength-item, .weakness-item {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 5px;
            padding: 8px;
            margin: 5px 0;
            font-size: 0.9em;
        }
        .weakness-item {
            background: #f8d7da;
            border-color: #f5c6cb;
        }
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
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="team-dashboard">
        <h1>👥 Dashboard de Análisis de Equipo</h1>
        
        <div class="tabs">
            <div class="tab active" onclick="showTab('overview')">Resumen</div>
            <div class="tab" onclick="showTab('fundadores')">Fundadores</div>
            <div class="tab" onclick="showTab('equipo')">Equipo</div>
            <div class="tab" onclick="showTab('advisors')">Advisors</div>
            <div class="tab" onclick="showTab('analisis')">Análisis</div>
        </div>
        
        <div id="overview" class="tab-content active">
            <div class="dashboard-header">
                <h2>📊 Resumen del Equipo</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">2</div>
                        <div class="metric-label">Fundadores</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">12</div>
                        <div class="metric-label">Equipo Total</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">2</div>
                        <div class="metric-label">Advisors</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">85</div>
                        <div class="metric-label">Score Total</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">Excelente</div>
                        <div class="metric-label">Nivel</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">5%</div>
                        <div class="metric-label">Rotación</div>
                    </div>
                </div>
            </div>
            
            <div class="chart-container">
                <canvas id="overviewChart"></canvas>
            </div>
        </div>
        
        <div id="fundadores" class="tab-content">
            <h2>👑 Fundadores</h2>
            <div class="team-grid">
                <div class="team-card">
                    <div class="team-header">
                        <div class="team-name">CEO</div>
                        <div class="team-role">Liderazgo</div>
                    </div>
                    <div class="team-details">
                        <div class="team-detail">
                            <strong>Experiencia:</strong> 8 años
                        </div>
                        <div class="team-detail">
                            <strong>Sector:</strong> SaaS
                        </div>
                        <div class="team-detail">
                            <strong>Educación:</strong> MBA
                        </div>
                        <div class="team-detail">
                            <strong>Track Record:</strong> Exitoso
                        </div>
                        <div class="team-detail">
                            <strong>Liderazgo:</strong> Fuerte
                        </div>
                        <div class="team-detail">
                            <strong>Visión:</strong> Clara
                        </div>
                        <div class="team-detail">
                            <strong>Ejecución:</strong> Excelente
                        </div>
                    </div>
                    <div class="strengths">
                        <h4>✅ Fortalezas</h4>
                        <div class="strength-item">Experiencia sólida</div>
                        <div class="strength-item">Track record exitoso</div>
                        <div class="strength-item">Liderazgo fuerte</div>
                        <div class="strength-item">Visión clara</div>
                    </div>
                </div>
                
                <div class="team-card">
                    <div class="team-header">
                        <div class="team-name">CTO</div>
                        <div class="team-role">Técnico</div>
                    </div>
                    <div class="team-details">
                        <div class="team-detail">
                            <strong>Experiencia:</strong> 10 años
                        </div>
                        <div class="team-detail">
                            <strong>Sector:</strong> IA
                        </div>
                        <div class="team-detail">
                            <strong>Educación:</strong> PhD
                        </div>
                        <div class="team-detail">
                            <strong>Track Record:</strong> Exitoso
                        </div>
                        <div class="team-detail">
                            <strong>Liderazgo:</strong> Técnico
                        </div>
                        <div class="team-detail">
                            <strong>Visión:</strong> Técnica
                        </div>
                        <div class="team-detail">
                            <strong>Ejecución:</strong> Excelente
                        </div>
                    </div>
                    <div class="strengths">
                        <h4>✅ Fortalezas</h4>
                        <div class="strength-item">Experiencia técnica sólida</div>
                        <div class="strength-item">Track record exitoso</div>
                        <div class="strength-item">Liderazgo técnico</div>
                        <div class="strength-item">Ejecución excelente</div>
                    </div>
                </div>
            </div>
            
            <div class="team-section">
                <h3>📊 Análisis de Complementariedad</h3>
                <div class="score-bar">
                    <div class="score-fill" style="width: 90%"></div>
                </div>
                <p><strong>Score:</strong> 90/100 - Excelente complementariedad entre CEO y CTO</p>
            </div>
        </div>
        
        <div id="equipo" class="tab-content">
            <h2>👥 Equipo</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">12</div>
                    <div class="metric-label">Total</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">8</div>
                    <div class="metric-label">Senior</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">4</div>
                    <div class="metric-label">Junior</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">2:1</div>
                    <div class="metric-label">Ratio S/J</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">85%</div>
                    <div class="metric-label">Satisfacción</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">90%</div>
                    <div class="metric-label">Productividad</div>
                </div>
            </div>
            
            <div class="team-section">
                <h3>📊 Análisis de Equipo</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">Excelente</div>
                        <div class="metric-label">Composición</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">Excelente</div>
                        <div class="metric-label">Retención</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">Excelente</div>
                        <div class="metric-label">Productividad</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">Excelente</div>
                        <div class="metric-label">Cultura</div>
                    </div>
                </div>
            </div>
            
            <div class="chart-container">
                <canvas id="equipoChart"></canvas>
            </div>
        </div>
        
        <div id="advisors" class="tab-content">
            <h2>🎯 Advisors</h2>
            <div class="team-grid">
                <div class="team-card">
                    <div class="team-header">
                        <div class="team-name">Advisor 1</div>
                        <div class="team-role">Estratégico</div>
                    </div>
                    <div class="team-details">
                        <div class="team-detail">
                            <strong>Experiencia:</strong> 15 años
                        </div>
                        <div class="team-detail">
                            <strong>Sector:</strong> SaaS
                        </div>
                        <div class="team-detail">
                            <strong>Rol:</strong> Estratégico
                        </div>
                        <div class="team-detail">
                            <strong>Valor:</strong> Alto
                        </div>
                    </div>
                    <div class="strengths">
                        <h4>✅ Fortalezas</h4>
                        <div class="strength-item">Experiencia sólida</div>
                        <div class="strength-item">Sector relevante</div>
                        <div class="strength-item">Rol estratégico</div>
                        <div class="strength-item">Alto valor</div>
                    </div>
                </div>
                
                <div class="team-card">
                    <div class="team-header">
                        <div class="team-name">Advisor 2</div>
                        <div class="team-role">Técnico</div>
                    </div>
                    <div class="team-details">
                        <div class="team-detail">
                            <strong>Experiencia:</strong> 12 años
                        </div>
                        <div class="team-detail">
                            <strong>Sector:</strong> IA
                        </div>
                        <div class="team-detail">
                            <strong>Rol:</strong> Técnico
                        </div>
                        <div class="team-detail">
                            <strong>Valor:</strong> Alto
                        </div>
                    </div>
                    <div class="strengths">
                        <h4>✅ Fortalezas</h4>
                        <div class="strength-item">Experiencia técnica</div>
                        <div class="strength-item">Sector IA</div>
                        <div class="strength-item">Rol técnico</div>
                        <div class="strength-item">Alto valor</div>
                    </div>
                </div>
            </div>
            
            <div class="team-section">
                <h3>📊 Análisis de Advisors</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">Alto</div>
                        <div class="metric-label">Experiencia</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">Excelente</div>
                        <div class="metric-label">Red</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">Excelente</div>
                        <div class="metric-label">Valor</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">Excelente</div>
                        <div class="metric-label">Compromiso</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="analisis" class="tab-content">
            <h2>📊 Análisis Detallado</h2>
            <div class="team-section">
                <h3>Fortalezas del Equipo</h3>
                <div class="strengths">
                    <div class="strength-item">Experiencia sólida en fundadores</div>
                    <div class="strength-item">Track record exitoso</div>
                    <div class="strength-item">Liderazgo fuerte</div>
                    <div class="strength-item">Visión clara</div>
                    <div class="strength-item">Ejecución excelente</div>
                    <div class="strength-item">Equipo numeroso</div>
                    <div class="strength-item">Ratio senior/junior excelente</div>
                    <div class="strength-item">Baja rotación</div>
                    <div class="strength-item">Alta satisfacción</div>
                    <div class="strength-item">Alta productividad</div>
                    <div class="strength-item">Múltiples advisors</div>
                    <div class="strength-item">Advisors con experiencia</div>
                    <div class="strength-item">Advisors del sector</div>
                    <div class="strength-item">Advisors de alto valor</div>
                    <div class="strength-item">Advisors estratégicos</div>
                </div>
            </div>
            
            <div class="team-section">
                <h3>Debilidades del Equipo</h3>
                <div class="weaknesses">
                    <div class="weakness-item">Ninguna debilidad significativa identificada</div>
                </div>
            </div>
            
            <div class="recommendations">
                <h3>💡 Recomendaciones</h3>
                <div class="recommendation-item">Mantener el nivel actual de excelencia</div>
                <div class="recommendation-item">Continuar desarrollando el equipo</div>
                <div class="recommendation-item">Fortalecer las relaciones con advisors</div>
                <div class="recommendation-item">Mantener la cultura de excelencia</div>
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
                labels: ['Liderazgo', 'Experiencia', 'Equipo', 'Advisors', 'Cultura'],
                datasets: [{
                    label: 'Score del Equipo',
                    data: [90, 85, 95, 88, 92],
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
        
        // Crear gráfico de equipo
        const ctx2 = document.getElementById('equipoChart').getContext('2d');
        new Chart(ctx2, {
            type: 'doughnut',
            data: {
                labels: ['Senior', 'Junior'],
                datasets: [{
                    data: [8, 4],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 99, 132, 0.8)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)'
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

*Dashboard de análisis de equipo preparado para SaaS IA Copywriting LATAM*  
*Versión 1.0 - Diciembre 2024*






