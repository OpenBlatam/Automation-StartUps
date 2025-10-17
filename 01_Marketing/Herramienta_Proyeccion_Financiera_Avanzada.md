# 📈 HERRAMIENTA DE PROYECCIÓN FINANCIERA AVANZADA
## Sistema de Modelado Financiero para SaaS IA Copywriting LATAM

*Fecha: Diciembre 2024*  
*Versión: 1.0 - Proyección Avanzada*  
*Sector: SaaS IA Marketing/Copywriting*

---

## 🧮 MODELO FINANCIERO INTEGRADO

### **Proyección de Ingresos y Costos**

```javascript
// Herramienta de proyección financiera avanzada
class AdvancedFinancialProjectionTool {
    constructor() {
        this.metrics = {
            // Métricas actuales
            ARR: 139000,
            MRR: 11600,
            usuarios: 500,
            churn: 0.05,
            CAC: 150,
            LTV: 1350,
            crecimiento: 1.2, // 120% anual
            
            // Proyecciones base
            ARR_2025: 1200000,
            ARR_2026: 3600000,
            ARR_2027: 8500000,
            
            // Parámetros del modelo
            margenBruto: 0.85,
            gastosOperativos: 0.60,
            tasaImpositiva: 0.25,
            capex: 0.05,
            workingCapital: 0.02
        };
        
        this.escenarios = {
            conservador: { factor: 0.7, probabilidad: 0.2 },
            realista: { factor: 1.0, probabilidad: 0.6 },
            optimista: { factor: 1.3, probabilidad: 0.2 }
        };
    }
    
    generarProyeccion(escenario = 'realista', años = 5) {
        const factor = this.escenarios[escenario].factor;
        const proyeccion = [];
        
        for (let año = 1; año <= años; año++) {
            const añoData = this.calcularAño(año, factor);
            proyeccion.push(añoData);
        }
        
        const analisis = this.analizarProyeccion(proyeccion);
        const metricas = this.calcularMetricas(proyeccion);
        const sensibilidad = this.analizarSensibilidad(proyeccion);
        
        return {
            escenario,
            proyeccion,
            analisis,
            metricas,
            sensibilidad
        };
    }
    
    calcularAño(año, factor) {
        // Crecimiento de usuarios
        const crecimientoUsuarios = this.calcularCrecimientoUsuarios(año, factor);
        const usuarios = this.metrics.usuarios * Math.pow(1 + crecimientoUsuarios, año);
        
        // Crecimiento de ARR
        const crecimientoARR = this.calcularCrecimientoARR(año, factor);
        const ARR = this.metrics.ARR * Math.pow(1 + crecimientoARR, año);
        
        // Cálculo de ingresos
        const ingresos = this.calcularIngresos(ARR, usuarios, año);
        
        // Cálculo de costos
        const costos = this.calcularCostos(ARR, usuarios, año);
        
        // Cálculo de EBITDA
        const EBITDA = ingresos.ARR * this.metrics.margenBruto - costos.operativos;
        
        // Cálculo de impuestos
        const impuestos = EBITDA * this.metrics.tasaImpositiva;
        
        // Cálculo de capex
        const capex = ARR * this.metrics.capex;
        
        // Cálculo de working capital
        const workingCapital = ARR * this.metrics.workingCapital;
        
        // Cálculo de flujo de caja libre
        const FCF = EBITDA - impuestos - capex - workingCapital;
        
        return {
            año,
            usuarios: Math.round(usuarios),
            ARR: Math.round(ARR),
            MRR: Math.round(ARR / 12),
            ingresos,
            costos,
            EBITDA: Math.round(EBITDA),
            impuestos: Math.round(impuestos),
            capex: Math.round(capex),
            workingCapital: Math.round(workingCapital),
            FCF: Math.round(FCF),
            margenEBITDA: Math.round((EBITDA / ARR) * 100) / 100
        };
    }
    
    calcularCrecimientoUsuarios(año, factor) {
        const baseGrowth = this.metrics.crecimiento;
        const decayFactor = Math.pow(0.8, año - 1); // Decaimiento del crecimiento
        let growth = baseGrowth * decayFactor * factor;
        
        // Ajustar por saturación del mercado
        if (año > 3) {
            growth *= 0.7; // Reducir crecimiento por saturación
        }
        
        return Math.min(growth, 2.0); // Máximo 200% anual
    }
    
    calcularCrecimientoARR(año, factor) {
        const baseGrowth = this.metrics.crecimiento;
        const decayFactor = Math.pow(0.85, año - 1);
        let growth = baseGrowth * decayFactor * factor;
        
        // Ajustar por madurez del mercado
        if (año > 4) {
            growth *= 0.8; // Reducir crecimiento por madurez
        }
        
        return Math.min(growth, 1.5); // Máximo 150% anual
    }
    
    calcularIngresos(ARR, usuarios, año) {
        const ARPU = ARR / usuarios;
        const churnRate = this.metrics.churn * (1 - año * 0.01); // Mejorar churn con el tiempo
        
        return {
            ARR: ARR,
            MRR: ARR / 12,
            ARPU: Math.round(ARPU),
            churnRate: Math.round(churnRate * 100) / 100,
            usuarios: Math.round(usuarios)
        };
    }
    
    calcularCostos(ARR, usuarios, año) {
        const costos = {
            // Costos de adquisición
            marketing: ARR * 0.25, // 25% del ARR
            ventas: ARR * 0.15,    // 15% del ARR
            
            // Costos operativos
            desarrollo: ARR * 0.20,  // 20% del ARR
            soporte: ARR * 0.10,     // 10% del ARR
            administracion: ARR * 0.15, // 15% del ARR
            
            // Costos fijos
            infraestructura: 50000 + (año * 10000), // Crecimiento de infraestructura
            personal: 200000 + (año * 50000) // Crecimiento de personal
        };
        
        costos.operativos = Object.values(costos).reduce((sum, costo) => sum + costo, 0);
        
        return costos;
    }
    
    analizarProyeccion(proyeccion) {
        const ultimoAño = proyeccion[proyeccion.length - 1];
        const primerAño = proyeccion[0];
        
        return {
            crecimientoARR: ((ultimoAño.ARR - primerAño.ARR) / primerAño.ARR) * 100,
            crecimientoUsuarios: ((ultimoAño.usuarios - primerAño.usuarios) / primerAño.usuarios) * 100,
            breakEven: this.calcularBreakEven(proyeccion),
            paybackPeriod: this.calcularPaybackPeriod(proyeccion),
            roi: this.calcularROI(proyeccion),
            tendencias: this.analizarTendencias(proyeccion)
        };
    }
    
    calcularBreakEven(proyeccion) {
        for (let i = 0; i < proyeccion.length; i++) {
            if (proyeccion[i].FCF > 0) {
                return {
                    año: i + 1,
                    trimestre: this.estimarTrimestre(proyeccion, i)
                };
            }
        }
        return { año: 'No alcanzado', trimestre: 'N/A' };
    }
    
    estimarTrimestre(proyeccion, año) {
        if (año === 0) return 'Q4';
        
        const fcfAnterior = proyeccion[año - 1].FCF;
        const fcfActual = proyeccion[año].FCF;
        
        if (fcfAnterior < 0 && fcfActual > 0) {
            const ratio = Math.abs(fcfAnterior) / (Math.abs(fcfAnterior) + fcfActual);
            if (ratio < 0.25) return 'Q1';
            if (ratio < 0.5) return 'Q2';
            if (ratio < 0.75) return 'Q3';
            return 'Q4';
        }
        
        return 'Q4';
    }
    
    calcularPaybackPeriod(proyeccion) {
        const inversionInicial = 2000000; // Inversión inicial
        let acumulado = 0;
        
        for (let i = 0; i < proyeccion.length; i++) {
            acumulado += proyeccion[i].FCF;
            if (acumulado >= inversionInicial) {
                return {
                    año: i + 1,
                    trimestre: this.estimarTrimestre(proyeccion, i)
                };
            }
        }
        
        return { año: 'No alcanzado', trimestre: 'N/A' };
    }
    
    calcularROI(proyeccion) {
        const inversionInicial = 2000000;
        const fcfTotal = proyeccion.reduce((sum, año) => sum + año.FCF, 0);
        const roi = (fcfTotal / inversionInicial) * 100;
        
        return {
            roi: Math.round(roi * 100) / 100,
            fcfTotal: Math.round(fcfTotal),
            inversionInicial: inversionInicial
        };
    }
    
    analizarTendencias(proyeccion) {
        const tendencias = {
            crecimientoARR: this.calcularTendencia(proyeccion, 'ARR'),
            crecimientoUsuarios: this.calcularTendencia(proyeccion, 'usuarios'),
            margenEBITDA: this.calcularTendencia(proyeccion, 'margenEBITDA'),
            FCF: this.calcularTendencia(proyeccion, 'FCF')
        };
        
        return tendencias;
    }
    
    calcularTendencia(proyeccion, metrica) {
        const valores = proyeccion.map(año => año[metrica]);
        const n = valores.length;
        const x = Array.from({length: n}, (_, i) => i);
        const sumX = x.reduce((a, b) => a + b, 0);
        const sumY = valores.reduce((a, b) => a + b, 0);
        const sumXY = x.reduce((sum, xi, i) => sum + xi * valores[i], 0);
        const sumXX = x.reduce((sum, xi) => sum + xi * xi, 0);
        
        const pendiente = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
        
        if (pendiente > 0) return 'Creciente';
        if (pendiente < 0) return 'Decreciente';
        return 'Estable';
    }
    
    calcularMetricas(proyeccion) {
        const metricas = {
            arr: proyeccion.map(año => año.ARR),
            usuarios: proyeccion.map(año => año.usuarios),
            ebitda: proyeccion.map(año => año.EBITDA),
            fcf: proyeccion.map(año => año.FCF),
            margen: proyeccion.map(año => año.margenEBITDA)
        };
        
        return {
            metricas,
            proyecciones: this.generarProyecciones(metricas),
            comparaciones: this.compararConBenchmarks(metricas)
        };
    }
    
    generarProyecciones(metricas) {
        const proyecciones = {};
        
        Object.keys(metricas).forEach(metrica => {
            const valores = metricas[metrica];
            const ultimo = valores[valores.length - 1];
            const penultimo = valores[valores.length - 2];
            const crecimiento = (ultimo - penultimo) / penultimo;
            
            proyecciones[metrica] = {
                actual: ultimo,
                crecimiento: Math.round(crecimiento * 100) / 100,
                proyeccion: Math.round(ultimo * (1 + crecimiento))
            };
        });
        
        return proyecciones;
    }
    
    compararConBenchmarks(metricas) {
        const benchmarks = {
            saas: {
                crecimientoARR: 0.5,
                margenEBITDA: 0.25,
                churn: 0.05
            },
            ia: {
                crecimientoARR: 0.8,
                margenEBITDA: 0.30,
                churn: 0.03
            },
            latam: {
                crecimientoARR: 0.6,
                margenEBITDA: 0.20,
                churn: 0.07
            }
        };
        
        const comparaciones = {};
        
        Object.keys(benchmarks).forEach(benchmark => {
            comparaciones[benchmark] = {
                crecimientoARR: this.compararMetrica(metricas.arr, benchmarks[benchmark].crecimientoARR),
                margenEBITDA: this.compararMetrica(metricas.margen, benchmarks[benchmark].margenEBITDA),
                churn: this.compararChurn(metricas.arr, benchmarks[benchmark].churn)
            };
        });
        
        return comparaciones;
    }
    
    compararMetrica(valores, benchmark) {
        const ultimo = valores[valores.length - 1];
        const penultimo = valores[valores.length - 2];
        const crecimiento = (ultimo - penultimo) / penultimo;
        
        if (crecimiento > benchmark * 1.2) return 'Superior';
        if (crecimiento > benchmark * 0.8) return 'Similar';
        return 'Inferior';
    }
    
    compararChurn(valores, benchmark) {
        // Simular cálculo de churn basado en crecimiento
        const ultimo = valores[valores.length - 1];
        const penultimo = valores[valores.length - 2];
        const crecimiento = (ultimo - penultimo) / penultimo;
        
        // Churn estimado basado en crecimiento
        const churnEstimado = Math.max(0.02, 0.1 - crecimiento * 0.05);
        
        if (churnEstimado < benchmark * 0.8) return 'Superior';
        if (churnEstimado < benchmark * 1.2) return 'Similar';
        return 'Inferior';
    }
    
    analizarSensibilidad(proyeccion) {
        const sensibilidad = {
            crecimiento: this.analizarSensibilidadCrecimiento(),
            churn: this.analizarSensibilidadChurn(),
            pricing: this.analizarSensibilidadPricing(),
            costos: this.analizarSensibilidadCostos()
        };
        
        return sensibilidad;
    }
    
    analizarSensibilidadCrecimiento() {
        const variaciones = [-0.2, -0.1, 0, 0.1, 0.2];
        const resultados = {};
        
        variaciones.forEach(variacion => {
            const factor = 1 + variacion;
            const proyeccion = this.generarProyeccion('realista', 3);
            const ultimoAño = proyeccion.proyeccion[proyeccion.proyeccion.length - 1];
            resultados[`${(variacion * 100).toFixed(0)}%`] = Math.round(ultimoAño.ARR);
        });
        
        return resultados;
    }
    
    analizarSensibilidadChurn() {
        const variaciones = [0.02, 0.03, 0.05, 0.07, 0.10];
        const resultados = {};
        
        variaciones.forEach(churn => {
            const proyeccion = this.generarProyeccion('realista', 3);
            const ultimoAño = proyeccion.proyeccion[proyeccion.proyeccion.length - 1];
            resultados[`${(churn * 100).toFixed(0)}%`] = Math.round(ultimoAño.ARR);
        });
        
        return resultados;
    }
    
    analizarSensibilidadPricing() {
        const variaciones = [0.8, 0.9, 1.0, 1.1, 1.2];
        const resultados = {};
        
        variaciones.forEach(factor => {
            const proyeccion = this.generarProyeccion('realista', 3);
            const ultimoAño = proyeccion.proyeccion[proyeccion.proyeccion.length - 1];
            resultados[`${(factor * 100).toFixed(0)}%`] = Math.round(ultimoAño.ARR * factor);
        });
        
        return resultados;
    }
    
    analizarSensibilidadCostos() {
        const variaciones = [0.8, 0.9, 1.0, 1.1, 1.2];
        const resultados = {};
        
        variaciones.forEach(factor => {
            const proyeccion = this.generarProyeccion('realista', 3);
            const ultimoAño = proyeccion.proyeccion[proyeccion.proyeccion.length - 1];
            resultados[`${(factor * 100).toFixed(0)}%`] = Math.round(ultimoAño.ARR * (1 - (1 - factor) * 0.3));
        });
        
        return resultados;
    }
}

// Ejemplo de uso
const projectionTool = new AdvancedFinancialProjectionTool();
const proyeccion = projectionTool.generarProyeccion('realista', 5);
console.log('Proyección Financiera:', proyeccion);
```

---

## 📊 DASHBOARD DE PROYECCIÓN FINANCIERA

### **Interfaz Visual**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Proyección Financiera Avanzada</title>
    <style>
        .projection-dashboard {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            font-family: Arial, sans-serif;
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
        .chart-container {
            height: 400px;
            margin: 20px 0;
        }
        .projection-table {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .projection-table table {
            width: 100%;
            border-collapse: collapse;
        }
        .projection-table th,
        .projection-table td {
            padding: 10px;
            text-align: right;
            border-bottom: 1px solid #ddd;
        }
        .projection-table th {
            background: #f8f9fa;
            font-weight: bold;
        }
        .analysis {
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .sensitivity {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .sensitivity-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .sensitivity-item {
            background: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
        }
        .sensitivity-title {
            font-weight: bold;
            margin-bottom: 10px;
            color: #495057;
        }
        .sensitivity-values {
            font-size: 0.9em;
            color: #6c757d;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="projection-dashboard">
        <h1>📈 Proyección Financiera Avanzada</h1>
        
        <div class="scenario-tabs">
            <div class="scenario-tab active" onclick="selectScenario('conservador')">Conservador</div>
            <div class="scenario-tab" onclick="selectScenario('realista')">Realista</div>
            <div class="scenario-tab" onclick="selectScenario('optimista')">Optimista</div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value" id="arr2027">$8.5M</div>
                <div class="metric-label">ARR 2027</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="usuarios2027">10,000</div>
                <div class="metric-label">Usuarios 2027</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="ebitda2027">$2.1M</div>
                <div class="metric-label">EBITDA 2027</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="fcf2027">$1.6M</div>
                <div class="metric-label">FCF 2027</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="margen2027">25%</div>
                <div class="metric-label">Margen EBITDA</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="breakEven">Q2 2025</div>
                <div class="metric-label">Break Even</div>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="projectionChart"></canvas>
        </div>
        
        <div class="projection-table">
            <h3>📊 Proyección Detallada (5 Años)</h3>
            <table>
                <thead>
                    <tr>
                        <th>Año</th>
                        <th>Usuarios</th>
                        <th>ARR</th>
                        <th>MRR</th>
                        <th>EBITDA</th>
                        <th>FCF</th>
                        <th>Margen EBITDA</th>
                    </tr>
                </thead>
                <tbody id="projectionTableBody">
                    <!-- Datos se generan dinámicamente -->
                </tbody>
            </table>
        </div>
        
        <div class="analysis">
            <h3>📈 Análisis de Proyección</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">1,200%</div>
                    <div class="metric-label">Crecimiento ARR</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">1,900%</div>
                    <div class="metric-label">Crecimiento Usuarios</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">Q2 2025</div>
                    <div class="metric-label">Break Even</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">Q3 2025</div>
                    <div class="metric-label">Payback Period</div>
                </div>
            </div>
        </div>
        
        <div class="sensitivity">
            <h3>🔍 Análisis de Sensibilidad</h3>
            <div class="sensitivity-grid">
                <div class="sensitivity-item">
                    <div class="sensitivity-title">Crecimiento</div>
                    <div class="sensitivity-values">
                        -20%: $6.8M<br>
                        -10%: $7.7M<br>
                        Base: $8.5M<br>
                        +10%: $9.4M<br>
                        +20%: $10.2M
                    </div>
                </div>
                <div class="sensitivity-item">
                    <div class="sensitivity-title">Churn</div>
                    <div class="sensitivity-values">
                        2%: $9.1M<br>
                        3%: $8.8M<br>
                        5%: $8.5M<br>
                        7%: $8.1M<br>
                        10%: $7.6M
                    </div>
                </div>
                <div class="sensitivity-item">
                    <div class="sensitivity-title">Pricing</div>
                    <div class="sensitivity-values">
                        80%: $6.8M<br>
                        90%: $7.7M<br>
                        100%: $8.5M<br>
                        110%: $9.4M<br>
                        120%: $10.2M
                    </div>
                </div>
                <div class="sensitivity-item">
                    <div class="sensitivity-title">Costos</div>
                    <div class="sensitivity-values">
                        80%: $9.4M<br>
                        90%: $8.9M<br>
                        100%: $8.5M<br>
                        110%: $8.1M<br>
                        120%: $7.6M
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentScenario = 'realista';
        
        function selectScenario(scenario) {
            currentScenario = scenario;
            
            // Actualizar tabs
            document.querySelectorAll('.scenario-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Actualizar datos
            updateProjection();
        }
        
        function updateProjection() {
            // Simular actualización de datos
            const data = {
                conservador: {
                    arr2027: '$6.0M',
                    usuarios2027: '7,000',
                    ebitda2027: '$1.5M',
                    fcf2027: '$1.1M',
                    margen2027: '25%',
                    breakEven: 'Q3 2025'
                },
                realista: {
                    arr2027: '$8.5M',
                    usuarios2027: '10,000',
                    ebitda2027: '$2.1M',
                    fcf2027: '$1.6M',
                    margen2027: '25%',
                    breakEven: 'Q2 2025'
                },
                optimista: {
                    arr2027: '$11.0M',
                    usuarios2027: '13,000',
                    ebitda2027: '$2.7M',
                    fcf2027: '$2.1M',
                    margen2027: '25%',
                    breakEven: 'Q1 2025'
                }
            };
            
            const scenarioData = data[currentScenario];
            
            // Actualizar métricas
            document.getElementById('arr2027').textContent = scenarioData.arr2027;
            document.getElementById('usuarios2027').textContent = scenarioData.usuarios2027;
            document.getElementById('ebitda2027').textContent = scenarioData.ebitda2027;
            document.getElementById('fcf2027').textContent = scenarioData.fcf2027;
            document.getElementById('margen2027').textContent = scenarioData.margen2027;
            document.getElementById('breakEven').textContent = scenarioData.breakEven;
            
            // Actualizar gráfico
            updateChart();
        }
        
        function updateChart() {
            const ctx = document.getElementById('projectionChart').getContext('2d');
            
            // Destruir gráfico anterior si existe
            if (window.projectionChart) {
                window.projectionChart.destroy();
            }
            
            // Datos de ejemplo
            const data = {
                conservador: {
                    arr: [139, 600, 1200, 2400, 3600, 4800],
                    usuarios: [500, 2000, 4000, 6000, 8000, 10000]
                },
                realista: {
                    arr: [139, 800, 1600, 3200, 4800, 6400],
                    usuarios: [500, 2500, 5000, 7500, 10000, 12500]
                },
                optimista: {
                    arr: [139, 1000, 2000, 4000, 6000, 8000],
                    usuarios: [500, 3000, 6000, 9000, 12000, 15000]
                }
            };
            
            const scenarioData = data[currentScenario];
            
            window.projectionChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['2024', '2025', '2026', '2027', '2028', '2029'],
                    datasets: [{
                        label: 'ARR (K)',
                        data: scenarioData.arr,
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y'
                    }, {
                        label: 'Usuarios (K)',
                        data: scenarioData.usuarios,
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'ARR (K)'
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Usuarios (K)'
                            },
                            grid: {
                                drawOnChartArea: false,
                            },
                        }
                    }
                }
            });
        }
        
        // Inicializar
        updateProjection();
    </script>
</body>
</html>
```

---

*Herramienta de proyección financiera avanzada preparada para SaaS IA Copywriting LATAM*  
*Versión 1.0 - Diciembre 2024*






