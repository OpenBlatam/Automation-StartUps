# 💰 CALCULADORA ROI AVANZADA VC
## Herramienta de Análisis Financiero y Retorno de Inversión para SaaS IA Copywriting LATAM

*Fecha: Diciembre 2024*  
*Versión: 1.0 - Calculadora ROI Avanzada*  
*Sector: SaaS IA Marketing/Copywriting*

---

## 🧮 CALCULADORA ROI INTERACTIVA

### **Modelo de Cálculo de ROI**

```javascript
// Calculadora ROI avanzada para negociación VC
class ROICalculator {
    constructor() {
        this.metrics = {
            // Métricas actuales
            ARR: 139000,
            MRR: 11600,
            usuarios: 500,
            churn: 0.05,
            CAC: 150,
            LTV: 1350,
            
            // Proyecciones
            crecimientoAnual: 1200,
            margenBruto: 0.85,
            gastosOperativos: 0.60,
            
            // Términos de inversión
            inversion: 2000000,
            valuacionPre: 10000000,
            valuacionPost: 12000000,
            dilution: 0.167,
            
            // Escenarios de salida
            exitYears: [3, 5, 7],
            exitMultiples: [8, 12, 15, 20]
        };
    }
    
    calcularROI(escenario) {
        const proyeccion = this.generarProyeccion(escenario);
        const exitValues = this.calcularExitValues(proyeccion, escenario);
        const roi = this.calcularROIValues(exitValues, escenario);
        
        return {
            proyeccion,
            exitValues,
            roi,
            analisis: this.analizarROI(roi),
            recomendaciones: this.generarRecomendacionesROI(roi)
        };
    }
    
    generarProyeccion(escenario) {
        const años = 7;
        const proyeccion = [];
        let ARR = this.metrics.ARR;
        let usuarios = this.metrics.usuarios;
        
        for (let año = 1; año <= años; año++) {
            // Crecimiento de usuarios
            const crecimientoUsuarios = this.calcularCrecimientoUsuarios(año, escenario);
            usuarios = usuarios * (1 + crecimientoUsuarios);
            
            // Crecimiento de ARR
            const crecimientoARR = this.calcularCrecimientoARR(año, escenario);
            ARR = ARR * (1 + crecimientoARR);
            
            // Cálculo de costos
            const costos = this.calcularCostos(ARR, usuarios, año);
            
            // Cálculo de EBITDA
            const EBITDA = ARR * this.metrics.margenBruto - costos.operativos;
            
            proyeccion.push({
                año,
                ARR: Math.round(ARR),
                usuarios: Math.round(usuarios),
                MRR: Math.round(ARR / 12),
                costos,
                EBITDA: Math.round(EBITDA),
                margenEBITDA: Math.round((EBITDA / ARR) * 100) / 100
            });
        }
        
        return proyeccion;
    }
    
    calcularCrecimientoUsuarios(año, escenario) {
        const baseGrowth = this.metrics.crecimientoAnual / 100;
        const decayFactor = Math.pow(0.8, año - 1); // Decaimiento del crecimiento
        
        let growth = baseGrowth * decayFactor;
        
        // Ajustar por escenario
        switch (escenario) {
            case 'conservador':
                growth *= 0.7;
                break;
            case 'realista':
                growth *= 1.0;
                break;
            case 'optimista':
                growth *= 1.3;
                break;
            case 'agresivo':
                growth *= 1.6;
                break;
        }
        
        return Math.min(growth, 2.0); // Máximo 200% anual
    }
    
    calcularCrecimientoARR(año, escenario) {
        const baseGrowth = this.metrics.crecimientoAnual / 100;
        const decayFactor = Math.pow(0.85, año - 1);
        
        let growth = baseGrowth * decayFactor;
        
        // Ajustar por escenario
        switch (escenario) {
            case 'conservador':
                growth *= 0.6;
                break;
            case 'realista':
                growth *= 1.0;
                break;
            case 'optimista':
                growth *= 1.2;
                break;
            case 'agresivo':
                growth *= 1.5;
                break;
        }
        
        return Math.min(growth, 1.5); // Máximo 150% anual
    }
    
    calcularCostos(ARR, usuarios, año) {
        const costos = {
            // Costos de adquisición
            marketing: ARR * 0.25, // 25% del ARR en marketing
            ventas: ARR * 0.15,    // 15% del ARR en ventas
            
            // Costos operativos
            desarrollo: ARR * 0.20,  // 20% del ARR en desarrollo
            soporte: ARR * 0.10,     // 10% del ARR en soporte
            administracion: ARR * 0.15, // 15% del ARR en administración
            
            // Costos fijos
            infraestructura: 50000 + (año * 10000), // Crecimiento de infraestructura
            personal: 200000 + (año * 50000) // Crecimiento de personal
        };
        
        costos.operativos = Object.values(costos).reduce((sum, costo) => sum + costo, 0);
        
        return costos;
    }
    
    calcularExitValues(proyeccion, escenario) {
        const exitValues = [];
        
        this.metrics.exitYears.forEach(exitYear => {
            const añoData = proyeccion[exitYear - 1];
            if (!añoData) return;
            
            this.metrics.exitMultiples.forEach(multiple => {
                const exitValue = añoData.ARR * multiple;
                const equityValue = exitValue * (1 - this.metrics.dilution);
                const roi = (equityValue / this.metrics.inversion) - 1;
                
                exitValues.push({
                    año: exitYear,
                    multiple: multiple,
                    ARR: añoData.ARR,
                    exitValue: Math.round(exitValue),
                    equityValue: Math.round(equityValue),
                    roi: Math.round(roi * 100) / 100,
                    roiAnualizado: Math.round(Math.pow(1 + roi, 1 / exitYear) * 100) / 100
                });
            });
        });
        
        return exitValues;
    }
    
    calcularROIValues(exitValues, escenario) {
        const roi = {
            escenario,
            mejorCaso: this.encontrarMejorCaso(exitValues),
            peorCaso: this.encontrarPeorCaso(exitValues),
            promedio: this.calcularPromedio(exitValues),
            percentiles: this.calcularPercentiles(exitValues),
            probabilidades: this.calcularProbabilidades(exitValues, escenario)
        };
        
        return roi;
    }
    
    encontrarMejorCaso(exitValues) {
        return exitValues.reduce((mejor, actual) => 
            actual.roi > mejor.roi ? actual : mejor
        );
    }
    
    encontrarPeorCaso(exitValues) {
        return exitValues.reduce((peor, actual) => 
            actual.roi < peor.roi ? actual : peor
        );
    }
    
    calcularPromedio(exitValues) {
        const rois = exitValues.map(e => e.roi);
        const promedio = rois.reduce((sum, roi) => sum + roi, 0) / rois.length;
        return Math.round(promedio * 100) / 100;
    }
    
    calcularPercentiles(exitValues) {
        const rois = exitValues.map(e => e.roi).sort((a, b) => a - b);
        const n = rois.length;
        
        return {
            p25: rois[Math.floor(n * 0.25)],
            p50: rois[Math.floor(n * 0.50)],
            p75: rois[Math.floor(n * 0.75)],
            p90: rois[Math.floor(n * 0.90)]
        };
    }
    
    calcularProbabilidades(exitValues, escenario) {
        const probabilidades = {
            exit3años: 0,
            exit5años: 0,
            exit7años: 0,
            roiPositivo: 0,
            roiAlto: 0
        };
        
        // Probabilidades por año de salida
        const exitsPorAño = exitValues.reduce((acc, e) => {
            if (!acc[e.año]) acc[e.año] = [];
            acc[e.año].push(e);
            return acc;
        }, {});
        
        Object.keys(exitsPorAño).forEach(año => {
            const exits = exitsPorAño[año];
            const promedio = exits.reduce((sum, e) => sum + e.roi, 0) / exits.length;
            probabilidades[`exit${año}años`] = Math.round(promedio * 100) / 100;
        });
        
        // Probabilidades de ROI
        const roisPositivos = exitValues.filter(e => e.roi > 0).length;
        const roisAltos = exitValues.filter(e => e.roi > 5).length;
        
        probabilidades.roiPositivo = Math.round((roisPositivos / exitValues.length) * 100);
        probabilidades.roiAlto = Math.round((roisAltos / exitValues.length) * 100);
        
        return probabilidades;
    }
    
    analizarROI(roi) {
        const analisis = {
            atractivo: this.evaluarAtractivo(roi),
            riesgo: this.evaluarRiesgo(roi),
            comparacion: this.compararConBenchmarks(roi),
            sensibilidad: this.analizarSensibilidad(roi)
        };
        
        return analisis;
    }
    
    evaluarAtractivo(roi) {
        const promedio = roi.promedio;
        
        if (promedio >= 10) return 'Muy Atractivo';
        if (promedio >= 5) return 'Atractivo';
        if (promedio >= 2) return 'Moderadamente Atractivo';
        if (promedio >= 0) return 'Poco Atractivo';
        return 'No Atractivo';
    }
    
    evaluarRiesgo(roi) {
        const desviacion = this.calcularDesviacion(roi);
        
        if (desviacion >= 5) return 'Alto';
        if (desviacion >= 3) return 'Medio';
        return 'Bajo';
    }
    
    calcularDesviacion(roi) {
        const rois = [roi.mejorCaso.roi, roi.peorCaso.roi];
        const promedio = rois.reduce((sum, r) => sum + r, 0) / rois.length;
        const varianza = rois.reduce((sum, r) => sum + Math.pow(r - promedio, 2), 0) / rois.length;
        return Math.sqrt(varianza);
    }
    
    compararConBenchmarks(roi) {
        const benchmarks = {
            saas: 8.5,
            ia: 12.3,
            latam: 6.8,
            early_stage: 15.2
        };
        
        const comparacion = {};
        Object.keys(benchmarks).forEach(benchmark => {
            const diferencia = roi.promedio - benchmarks[benchmark];
            comparacion[benchmark] = {
                diferencia: Math.round(diferencia * 100) / 100,
                superior: diferencia > 0
            };
        });
        
        return comparacion;
    }
    
    analizarSensibilidad(roi) {
        return {
            crecimiento: this.analizarSensibilidadCrecimiento(),
            multiple: this.analizarSensibilidadMultiple(),
            dilution: this.analizarSensibilidadDilution()
        };
    }
    
    analizarSensibilidadCrecimiento() {
        const escenarios = ['conservador', 'realista', 'optimista', 'agresivo'];
        const resultados = {};
        
        escenarios.forEach(escenario => {
            const roi = this.calcularROI(escenario);
            resultados[escenario] = roi.promedio;
        });
        
        return resultados;
    }
    
    analizarSensibilidadMultiple() {
        const multiples = [5, 8, 12, 15, 20];
        const resultados = {};
        
        multiples.forEach(multiple => {
            // Simular cambio de múltiplo
            const roi = this.calcularROI('realista');
            const exitValues = roi.exitValues.filter(e => e.multiple === multiple);
            if (exitValues.length > 0) {
                resultados[multiple] = exitValues[0].roi;
            }
        });
        
        return resultados;
    }
    
    analizarSensibilidadDilution() {
        const dilutions = [0.10, 0.15, 0.20, 0.25, 0.30];
        const resultados = {};
        
        dilutions.forEach(dilution => {
            // Simular cambio de dilución
            const roi = this.calcularROI('realista');
            const exitValues = roi.exitValues.map(e => ({
                ...e,
                equityValue: e.exitValue * (1 - dilution),
                roi: (e.exitValue * (1 - dilution) / this.metrics.inversion) - 1
            }));
            
            const promedio = exitValues.reduce((sum, e) => sum + e.roi, 0) / exitValues.length;
            resultados[dilution] = Math.round(promedio * 100) / 100;
        });
        
        return resultados;
    }
    
    generarRecomendacionesROI(roi) {
        const recomendaciones = [];
        
        if (roi.promedio < 5) {
            recomendaciones.push('Considerar negociar mejor valuación');
            recomendaciones.push('Evaluar términos de dilución');
        }
        
        if (roi.analisis.riesgo === 'Alto') {
            recomendaciones.push('Implementar estrategias de mitigación de riesgo');
            recomendaciones.push('Diversificar fuentes de financiamiento');
        }
        
        if (roi.analisis.atractivo === 'Muy Atractivo') {
            recomendaciones.push('Proceder con la inversión');
            recomendaciones.push('Preparar para escalamiento rápido');
        }
        
        return recomendaciones;
    }
}

// Ejemplo de uso
const calculator = new ROICalculator();
const roi = calculator.calcularROI('realista');
console.log('Análisis ROI:', roi);
```

---

## 📊 DASHBOARD ROI INTERACTIVO

### **Interfaz de Usuario**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Calculadora ROI Avanzada VC</title>
    <style>
        .calculator {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            font-family: Arial, sans-serif;
        }
        .input-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .input-group {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .input-group h3 {
            margin-top: 0;
            color: #007bff;
        }
        .input-group input, .input-group select {
            width: 100%;
            padding: 8px;
            margin: 5px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .results {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            text-align: center;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        .metric-label {
            color: #666;
            font-size: 0.9em;
        }
        .chart-container {
            height: 400px;
            margin: 20px 0;
        }
        .scenario-tabs {
            display: flex;
            margin: 20px 0;
        }
        .scenario-tab {
            padding: 10px 20px;
            background: #e9ecef;
            border: 1px solid #ddd;
            cursor: pointer;
            margin-right: 5px;
        }
        .scenario-tab.active {
            background: #007bff;
            color: white;
        }
        .recommendations {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .recommendations h3 {
            color: #155724;
            margin-top: 0;
        }
        .recommendation-item {
            background: white;
            border: 1px solid #c3e6cb;
            border-radius: 5px;
            padding: 10px;
            margin: 5px 0;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="calculator">
        <h1>💰 Calculadora ROI Avanzada VC</h1>
        
        <div class="scenario-tabs">
            <div class="scenario-tab active" onclick="selectScenario('conservador')">Conservador</div>
            <div class="scenario-tab" onclick="selectScenario('realista')">Realista</div>
            <div class="scenario-tab" onclick="selectScenario('optimista')">Optimista</div>
            <div class="scenario-tab" onclick="selectScenario('agresivo')">Agresivo</div>
        </div>
        
        <div class="input-grid">
            <div class="input-group">
                <h3>📊 Métricas Actuales</h3>
                <label>ARR:</label>
                <input type="number" id="arr" value="139000" step="1000">
                
                <label>Usuarios:</label>
                <input type="number" id="usuarios" value="500" step="10">
                
                <label>Churn Rate:</label>
                <input type="number" id="churn" value="5" step="0.1" min="0" max="100">
                
                <label>CAC:</label>
                <input type="number" id="cac" value="150" step="10">
            </div>
            
            <div class="input-group">
                <h3>💰 Términos de Inversión</h3>
                <label>Inversión:</label>
                <input type="number" id="inversion" value="2000000" step="100000">
                
                <label>Valuación Pre-money:</label>
                <input type="number" id="valuacionPre" value="10000000" step="100000">
                
                <label>Dilución:</label>
                <input type="number" id="dilution" value="16.7" step="0.1" min="0" max="100">
                
                <label>Valuación Post-money:</label>
                <input type="number" id="valuacionPost" value="12000000" step="100000">
            </div>
            
            <div class="input-group">
                <h3>📈 Proyecciones</h3>
                <label>Crecimiento Anual:</label>
                <input type="number" id="crecimiento" value="1200" step="50" min="0">
                
                <label>Margen Bruto:</label>
                <input type="number" id="margenBruto" value="85" step="1" min="0" max="100">
                
                <label>Gastos Operativos:</label>
                <input type="number" id="gastosOp" value="60" step="1" min="0" max="100">
                
                <label>Múltiplo de Salida:</label>
                <input type="number" id="multiple" value="12" step="1" min="1">
            </div>
        </div>
        
        <div class="results">
            <h2>📊 Resultados del Análisis ROI</h2>
            
            <div class="input-grid">
                <div class="metric-card">
                    <div class="metric-value" id="roiPromedio">8.5x</div>
                    <div class="metric-label">ROI Promedio</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-value" id="roiMejor">15.2x</div>
                    <div class="metric-label">Mejor Caso</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-value" id="roiPeor">3.1x</div>
                    <div class="metric-label">Peor Caso</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-value" id="probabilidadPositivo">85%</div>
                    <div class="metric-label">Probabilidad ROI Positivo</div>
                </div>
            </div>
            
            <div class="chart-container">
                <canvas id="roiChart"></canvas>
            </div>
        </div>
        
        <div class="recommendations">
            <h3>💡 Recomendaciones</h3>
            <div class="recommendation-item">Considerar negociar mejor valuación</div>
            <div class="recommendation-item">Evaluar términos de dilución</div>
            <div class="recommendation-item">Implementar estrategias de mitigación de riesgo</div>
            <div class="recommendation-item">Proceder con la inversión</div>
        </div>
    </div>

    <script>
        let currentScenario = 'conservador';
        
        function selectScenario(scenario) {
            currentScenario = scenario;
            
            // Actualizar tabs
            document.querySelectorAll('.scenario-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Recalcular
            calculateROI();
        }
        
        function calculateROI() {
            // Obtener valores de entrada
            const arr = parseInt(document.getElementById('arr').value);
            const usuarios = parseInt(document.getElementById('usuarios').value);
            const churn = parseInt(document.getElementById('churn').value);
            const cac = parseInt(document.getElementById('cac').value);
            const inversion = parseInt(document.getElementById('inversion').value);
            const valuacionPre = parseInt(document.getElementById('valuacionPre').value);
            const dilution = parseInt(document.getElementById('dilution').value);
            const valuacionPost = parseInt(document.getElementById('valuacionPost').value);
            const crecimiento = parseInt(document.getElementById('crecimiento').value);
            const margenBruto = parseInt(document.getElementById('margenBruto').value);
            const gastosOp = parseInt(document.getElementById('gastosOp').value);
            const multiple = parseInt(document.getElementById('multiple').value);
            
            // Simular cálculo ROI (en la implementación real usarías la clase ROICalculator)
            const roiData = simulateROICalculation(arr, usuarios, churn, cac, inversion, valuacionPre, dilution, valuacionPost, crecimiento, margenBruto, gastosOp, multiple, currentScenario);
            
            // Actualizar UI
            updateResults(roiData);
            updateChart(roiData);
        }
        
        function simulateROICalculation(arr, usuarios, churn, cac, inversion, valuacionPre, dilution, valuacionPost, crecimiento, margenBruto, gastosOp, multiple, scenario) {
            // Simulación simplificada del cálculo ROI
            const baseROI = 8.5;
            const scenarioMultiplier = {
                'conservador': 0.7,
                'realista': 1.0,
                'optimista': 1.3,
                'agresivo': 1.6
            };
            
            const roiPromedio = baseROI * scenarioMultiplier[scenario];
            const roiMejor = roiPromedio * 1.8;
            const roiPeor = roiPromedio * 0.4;
            const probabilidadPositivo = Math.min(85 + (scenarioMultiplier[scenario] - 1) * 20, 95);
            
            return {
                promedio: roiPromedio,
                mejor: roiMejor,
                peor: roiPeor,
                probabilidadPositivo: probabilidadPositivo,
                proyeccion: generateProjectionData(arr, crecimiento, scenario)
            };
        }
        
        function generateProjectionData(arr, crecimiento, scenario) {
            const años = 7;
            const proyeccion = [];
            let currentARR = arr;
            
            for (let año = 1; año <= años; año++) {
                const crecimientoAnual = crecimiento / 100 * Math.pow(0.8, año - 1);
                currentARR = currentARR * (1 + crecimientoAnual);
                
                proyeccion.push({
                    año,
                    ARR: Math.round(currentARR),
                    usuarios: Math.round(500 * Math.pow(1 + crecimientoAnual, año)),
                    EBITDA: Math.round(currentARR * 0.25)
                });
            }
            
            return proyeccion;
        }
        
        function updateResults(roiData) {
            document.getElementById('roiPromedio').textContent = roiData.promedio.toFixed(1) + 'x';
            document.getElementById('roiMejor').textContent = roiData.mejor.toFixed(1) + 'x';
            document.getElementById('roiPeor').textContent = roiData.peor.toFixed(1) + 'x';
            document.getElementById('probabilidadPositivo').textContent = Math.round(roiData.probabilidadPositivo) + '%';
        }
        
        function updateChart(roiData) {
            const ctx = document.getElementById('roiChart').getContext('2d');
            
            // Destruir gráfico anterior si existe
            if (window.roiChart) {
                window.roiChart.destroy();
            }
            
            window.roiChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: roiData.proyeccion.map(p => `Año ${p.año}`),
                    datasets: [{
                        label: 'ARR',
                        data: roiData.proyeccion.map(p => p.ARR),
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'EBITDA',
                        data: roiData.proyeccion.map(p => p.EBITDA),
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                }
                            }
                        }
                    }
                }
            });
        }
        
        // Event listeners para recálculo automático
        document.querySelectorAll('input, select').forEach(input => {
            input.addEventListener('change', calculateROI);
            input.addEventListener('input', calculateROI);
        });
        
        // Cálculo inicial
        calculateROI();
    </script>
</body>
</html>
```

---

## 📈 ANÁLISIS DE SENSIBILIDAD

### **Modelo de Sensibilidad**

```javascript
// Análisis de sensibilidad para ROI
class SensitivityAnalyzer {
    constructor() {
        this.factores = {
            crecimiento: {
                base: 1200,
                variaciones: [-50, -25, 0, 25, 50, 100]
            },
            multiple: {
                base: 12,
                variaciones: [5, 8, 12, 15, 20, 25]
            },
            dilution: {
                base: 0.167,
                variaciones: [0.10, 0.15, 0.20, 0.25, 0.30, 0.35]
            },
            churn: {
                base: 0.05,
                variaciones: [0.02, 0.03, 0.05, 0.07, 0.10, 0.15]
            }
        };
    }
    
    analizarSensibilidad() {
        const analisis = {};
        
        Object.keys(this.factores).forEach(factor => {
            analisis[factor] = this.analizarFactor(factor);
        });
        
        return {
            analisis,
            recomendaciones: this.generarRecomendacionesSensibilidad(analisis)
        };
    }
    
    analizarFactor(factor) {
        const factorData = this.factores[factor];
        const resultados = [];
        
        factorData.variaciones.forEach(variacion => {
            const valor = this.calcularValor(factor, variacion);
            const roi = this.calcularROI(factor, valor);
            
            resultados.push({
                valor,
                roi,
                impacto: this.calcularImpacto(roi, factorData.base)
            });
        });
        
        return {
            resultados,
            sensibilidad: this.calcularSensibilidad(resultados),
            recomendaciones: this.generarRecomendacionesFactor(factor, resultados)
        };
    }
    
    calcularValor(factor, variacion) {
        const factorData = this.factores[factor];
        
        switch (factor) {
            case 'crecimiento':
                return factorData.base * (1 + variacion / 100);
            case 'multiple':
                return variacion;
            case 'dilution':
                return variacion;
            case 'churn':
                return variacion;
            default:
                return factorData.base;
        }
    }
    
    calcularROI(factor, valor) {
        // Simulación simplificada del cálculo ROI
        const baseROI = 8.5;
        
        switch (factor) {
            case 'crecimiento':
                return baseROI * (valor / this.factores.crecimiento.base);
            case 'multiple':
                return baseROI * (valor / this.factores.multiple.base);
            case 'dilution':
                return baseROI * (1 - valor) / (1 - this.factores.dilution.base);
            case 'churn':
                return baseROI * (this.factores.churn.base / valor);
            default:
                return baseROI;
        }
    }
    
    calcularImpacto(roi, base) {
        return ((roi - base) / base) * 100;
    }
    
    calcularSensibilidad(resultados) {
        const rois = resultados.map(r => r.roi);
        const min = Math.min(...rois);
        const max = Math.max(...rois);
        const rango = max - min;
        
        if (rango > 10) return 'Alta';
        if (rango > 5) return 'Media';
        return 'Baja';
    }
    
    generarRecomendacionesFactor(factor, resultados) {
        const recomendaciones = [];
        const sensibilidad = this.calcularSensibilidad(resultados);
        
        if (sensibilidad === 'Alta') {
            recomendaciones.push(`Monitorear ${factor} de cerca`);
            recomendaciones.push(`Implementar controles para ${factor}`);
        }
        
        if (factor === 'crecimiento' && sensibilidad === 'Alta') {
            recomendaciones.push('Diversificar estrategias de crecimiento');
            recomendaciones.push('Implementar métricas de crecimiento tempranas');
        }
        
        if (factor === 'multiple' && sensibilidad === 'Alta') {
            recomendaciones.push('Mejorar métricas que impactan múltiplo');
            recomendaciones.push('Construir defensas competitivas');
        }
        
        if (factor === 'dilution' && sensibilidad === 'Alta') {
            recomendaciones.push('Negociar términos de dilución cuidadosamente');
            recomendaciones.push('Considerar anti-dilución provisions');
        }
        
        if (factor === 'churn' && sensibilidad === 'Alta') {
            recomendaciones.push('Implementar programas de retención robustos');
            recomendaciones.push('Monitorear métricas de churn tempranas');
        }
        
        return recomendaciones;
    }
    
    generarRecomendacionesSensibilidad(analisis) {
        const recomendaciones = [];
        
        Object.keys(analisis).forEach(factor => {
            const factorData = analisis[factor];
            if (factorData.sensibilidad === 'Alta') {
                recomendaciones.push(`Alta sensibilidad en ${factor} - requiere atención especial`);
            }
        });
        
        return recomendaciones;
    }
}

// Ejemplo de uso
const analyzer = new SensitivityAnalyzer();
const sensibilidad = analyzer.analizarSensibilidad();
console.log('Análisis de Sensibilidad:', sensibilidad);
```

---

## 🎯 RECOMENDACIONES ESTRATÉGICAS

### **Basadas en ROI**

#### **Si ROI Promedio < 5x**
- Negociar mejor valuación
- Evaluar términos de dilución
- Considerar alternativas de financiamiento

#### **Si ROI Promedio 5x - 10x**
- Aceptar con mejoras menores
- Monitorear métricas clave
- Preparar para escalamiento

#### **Si ROI Promedio > 10x**
- Proceder con la inversión
- Preparar para crecimiento acelerado
- Considerar rondas adicionales

### **Basadas en Sensibilidad**

#### **Alta Sensibilidad en Crecimiento**
- Diversificar estrategias de crecimiento
- Implementar métricas tempranas
- Crear planes de contingencia

#### **Alta Sensibilidad en Múltiplo**
- Mejorar métricas que impactan múltiplo
- Construir defensas competitivas
- Enfocarse en diferenciación

#### **Alta Sensibilidad en Dilución**
- Negociar términos cuidadosamente
- Considerar anti-dilución provisions
- Planificar rondas futuras

---

*Calculadora ROI avanzada preparada para SaaS IA Copywriting LATAM*  
*Versión 1.0 - Diciembre 2024*






