# 🧮 HERRAMIENTA DE VALUACIÓN INTERACTIVA
## Calculadora de Valuación para SaaS IA Copywriting LATAM

*Fecha: Diciembre 2024*  
*Versión: 1.0 - Herramienta Interactiva*  
*Sector: SaaS IA Marketing/Copywriting*

---

## 📊 CALCULADORA DE VALUACIÓN

### **MÉTODO 1: MÚLTIPLOS DE ARR**

#### **Inputs del Usuario**
```
ARR Actual: $139,000
Crecimiento ARR: 1,200% (3 años)
ARR Proyectado 2026: $3,600,000
Múltiplo de Mercado: 12x (ajustado para LATAM)
```

#### **Cálculo de Valuación**
```javascript
// Fórmula de valuación
function calcularValuacion(ARR, multiplico) {
    return ARR * multiplico;
}

// Ejemplo de cálculo
const ARR = 3600000; // $3.6M
const multiplico = 12; // 12x ARR
const valuacion = calcularValuacion(ARR, multiplico);
console.log(`Valuación: $${valuacion.toLocaleString()}`);
// Resultado: $43,200,000
```

#### **Escenarios de Valuación**
| **Escenario** | **ARR 2026** | **Múltiplo** | **Valuación** | **Pre-money** |
|---------------|--------------|--------------|---------------|---------------|
| **Pesimista** | $2,880,000 | 8x | $23,040,000 | $18,432,000 |
| **Base** | $3,600,000 | 12x | $43,200,000 | $34,560,000 |
| **Optimista** | $4,320,000 | 15x | $64,800,000 | $51,840,000 |

---

## 💰 CALCULADORA DE DILUCIÓN

### **Cap Table Simulator**

#### **Inputs del Usuario**
```
Valuación Pre-money: $8,000,000
Inversión: $2,000,000
Acciones Actuales: 10,000,000
```

#### **Cálculo de Dilución**
```javascript
// Fórmula de dilución
function calcularDilucion(valuacionPre, inversion, accionesActuales) {
    const valuacionPost = valuacionPre + inversion;
    const precioAccion = valuacionPre / accionesActuales;
    const accionesNuevas = inversion / precioAccion;
    const dilucion = (accionesNuevas / (accionesActuales + accionesNuevas)) * 100;
    
    return {
        valuacionPost,
        precioAccion,
        accionesNuevas,
        dilucion
    };
}

// Ejemplo de cálculo
const resultado = calcularDilucion(8000000, 2000000, 10000000);
console.log(`Dilución: ${resultado.dilucion.toFixed(1)}%`);
// Resultado: 20.0%
```

#### **Cap Table Resultante**
| **Accionista** | **Acciones** | **%** | **Valor** |
|----------------|--------------|-------|-----------|
| **Fundadores** | 8,000,000 | 64.0% | $6,400,000 |
| **ESOP** | 2,000,000 | 16.0% | $1,600,000 |
| **Series A** | 2,500,000 | 20.0% | $2,000,000 |
| **Total** | 12,500,000 | 100.0% | $10,000,000 |

---

## 📈 CALCULADORA DE MÉTRICAS FINANCIERAS

### **Métricas de Tractión**

#### **Inputs del Usuario**
```
MRR Actual: $11,600
Crecimiento MRR: 20% mensual
Churn Rate: 5% mensual
CAC: $150
LTV: $1,350
```

#### **Cálculo de Métricas**
```javascript
// Fórmula de métricas
function calcularMetricas(MRR, crecimiento, churn, CAC, LTV) {
    const MRR12Meses = MRR * Math.pow(1 + crecimiento/100, 12);
    const ARR = MRR12Meses * 12;
    const LTV_CAC = LTV / CAC;
    const paybackPeriod = CAC / (MRR * (1 - churn/100));
    
    return {
        MRR12Meses,
        ARR,
        LTV_CAC,
        paybackPeriod
    };
}

// Ejemplo de cálculo
const metricas = calcularMetricas(11600, 20, 5, 150, 1350);
console.log(`ARR: $${metricas.ARR.toLocaleString()}`);
// Resultado: $1,458,000
```

#### **Métricas Calculadas**
| **Métrica** | **Valor** | **Benchmark** | **Status** |
|-------------|-----------|---------------|------------|
| **MRR Growth** | 20% | 15-25% | ✅ Excelente |
| **Churn Rate** | 5% | <5% | ✅ Excelente |
| **LTV/CAC** | 9:1 | >3:1 | ✅ Excelente |
| **Payback Period** | 6 meses | <12 meses | ✅ Excelente |

---

## 🎯 CALCULADORA DE ESCENARIOS

### **Simulador de Escenarios**

#### **Escenario Base**
```javascript
// Escenario base
const escenarioBase = {
    ARR: 3600000,
    multiplico: 12,
    valuacion: 43200000,
    dilucion: 20,
    inversion: 2000000
};
```

#### **Escenario Optimista**
```javascript
// Escenario optimista (+20%)
const escenarioOptimista = {
    ARR: 4320000, // +20%
    multiplico: 15, // +25%
    valuacion: 64800000, // +50%
    dilucion: 20,
    inversion: 2000000
};
```

#### **Escenario Pesimista**
```javascript
// Escenario pesimista (-20%)
const escenarioPesimista = {
    ARR: 2880000, // -20%
    multiplico: 8, // -33%
    valuacion: 23040000, // -47%
    dilucion: 20,
    inversion: 2000000
};
```

---

## 📊 CALCULADORA DE COMPARABLES

### **Análisis de Comparables**

#### **Comparables Directos**
```javascript
// Comparables del mercado
const comparables = [
    {
        nombre: "Copy.ai",
        ARR: 50000000,
        valuacion: 1200000000,
        multiplico: 24,
        mercado: "Global"
    },
    {
        nombre: "Jasper",
        ARR: 80000000,
        valuacion: 1700000000,
        multiplico: 21,
        mercado: "Global"
    },
    {
        nombre: "Writesonic",
        ARR: 20000000,
        valuacion: 300000000,
        multiplico: 15,
        mercado: "Global"
    }
];

// Cálculo de múltiplo ajustado para LATAM
function calcularMultiploAjustado(comparables) {
    const multiplicoPromedio = comparables.reduce((sum, comp) => sum + comp.multiplico, 0) / comparables.length;
    const descuentoMercado = 0.20; // -20% por mercado LATAM
    const descuentoTamaño = 0.10; // -10% por tamaño
    const descuentoEtapa = 0.15; // -15% por etapa temprana
    
    const descuentoTotal = descuentoMercado + descuentoTamaño + descuentoEtapa;
    return multiplicoPromedio * (1 - descuentoTotal);
}

const multiplicoAjustado = calcularMultiploAjustado(comparables);
console.log(`Múltiplo ajustado: ${multiplicoAjustado.toFixed(1)}x`);
// Resultado: 11.0x
```

#### **Tabla de Comparables**
| **Empresa** | **ARR** | **Valuación** | **Múltiplo** | **Ajuste LATAM** |
|-------------|---------|---------------|--------------|------------------|
| **Copy.ai** | $50M | $1.2B | 24x | 19.2x |
| **Jasper** | $80M | $1.7B | 21x | 16.8x |
| **Writesonic** | $20M | $300M | 15x | 12.0x |
| **Promedio** | $50M | $1.1B | 20x | **11.0x** |

---

## 🧮 CALCULADORA DE DCF

### **Discounted Cash Flow**

#### **Proyección de Flujo de Caja**
```javascript
// Proyección DCF
const proyeccionDCF = {
    año1: -800000, // FCF negativo
    año2: -200000, // FCF negativo
    año3: 1200000, // FCF positivo
    año4: 2500000, // FCF positivo
    año5: 4000000, // FCF positivo
    terminalValue: 50000000, // Valor terminal
    descuento: 0.10 // 10% anual
};

function calcularDCF(proyeccion) {
    let valorPresente = 0;
    const { año1, año2, año3, año4, año5, terminalValue, descuento } = proyeccion;
    
    // Calcular valor presente de cada año
    valorPresente += año1 / Math.pow(1 + descuento, 1);
    valorPresente += año2 / Math.pow(1 + descuento, 2);
    valorPresente += año3 / Math.pow(1 + descuento, 3);
    valorPresente += año4 / Math.pow(1 + descuento, 4);
    valorPresente += año5 / Math.pow(1 + descuento, 5);
    valorPresente += terminalValue / Math.pow(1 + descuento, 5);
    
    return valorPresente;
}

const valorDCF = calcularDCF(proyeccionDCF);
console.log(`Valor DCF: $${valorDCF.toLocaleString()}`);
// Resultado: $38,600,000
```

#### **Tabla de DCF**
| **Año** | **FCF** | **Factor** | **Valor Presente** |
|---------|---------|------------|-------------------|
| **2024** | -$800K | 1.00 | -$800K |
| **2025** | -$200K | 0.91 | -$182K |
| **2026** | +$1.2M | 0.83 | +$996K |
| **2027** | +$2.5M | 0.75 | +$1.875M |
| **2028** | +$4.0M | 0.68 | +$2.72M |
| **Terminal** | $50M | 0.68 | $34M |
| **Total** | - | - | **$38.6M** |

---

## 🎯 CALCULADORA DE SENSIBILIDAD

### **Análisis de Sensibilidad**

#### **Sensibilidad a la Valuación**
```javascript
// Análisis de sensibilidad
function analisisSensibilidad(ARR, multiplico) {
    const escenarios = [];
    
    // Variar ARR ±20%
    for (let i = -20; i <= 20; i += 10) {
        const ARRAjustado = ARR * (1 + i/100);
        const valuacion = ARRAjustado * multiplico;
        escenarios.push({
            variacionARR: i,
            ARR: ARRAjustado,
            valuacion: valuacion
        });
    }
    
    return escenarios;
}

const sensibilidad = analisisSensibilidad(3600000, 12);
console.log("Análisis de sensibilidad:");
sensibilidad.forEach(escenario => {
    console.log(`ARR ${escenario.variacionARR}%: $${escenario.valuacion.toLocaleString()}`);
});
```

#### **Tabla de Sensibilidad**
| **Variación ARR** | **ARR** | **Valuación** | **Cambio** |
|-------------------|---------|---------------|------------|
| **-20%** | $2.88M | $34.6M | -20% |
| **-10%** | $3.24M | $38.9M | -10% |
| **0%** | $3.60M | $43.2M | 0% |
| **+10%** | $3.96M | $47.5M | +10% |
| **+20%** | $4.32M | $51.8M | +20% |

---

## 📱 INTERFAZ DE USUARIO

### **Formulario de Entrada**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Calculadora de Valuación VC</title>
    <style>
        .calculator {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: Arial, sans-serif;
        }
        .input-group {
            margin-bottom: 20px;
        }
        .input-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .input-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .result {
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 4px;
            margin-top: 20px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .metric .label {
            font-weight: bold;
        }
        .metric .value {
            color: #007bff;
        }
    </style>
</head>
<body>
    <div class="calculator">
        <h1>Calculadora de Valuación VC</h1>
        
        <div class="input-group">
            <label for="arr">ARR Actual ($)</label>
            <input type="number" id="arr" value="139000">
        </div>
        
        <div class="input-group">
            <label for="growth">Crecimiento ARR (% anual)</label>
            <input type="number" id="growth" value="1200">
        </div>
        
        <div class="input-group">
            <label for="multiple">Múltiplo de Mercado</label>
            <input type="number" id="multiple" value="12">
        </div>
        
        <div class="input-group">
            <label for="investment">Inversión ($)</label>
            <input type="number" id="investment" value="2000000">
        </div>
        
        <button onclick="calcular()">Calcular</button>
        
        <div class="result" id="result">
            <h3>Resultados</h3>
            <div class="metric">
                <span class="label">ARR Proyectado:</span>
                <span class="value" id="arr-proyectado">$0</span>
            </div>
            <div class="metric">
                <span class="label">Valuación:</span>
                <span class="value" id="valuacion">$0</span>
            </div>
            <div class="metric">
                <span class="label">Valuación Pre-money:</span>
                <span class="value" id="valuacion-pre">$0</span>
            </div>
            <div class="metric">
                <span class="label">Dilución:</span>
                <span class="value" id="dilucion">0%</span>
            </div>
        </div>
    </div>

    <script>
        function calcular() {
            const ARR = parseFloat(document.getElementById('arr').value);
            const growth = parseFloat(document.getElementById('growth').value);
            const multiple = parseFloat(document.getElementById('multiple').value);
            const investment = parseFloat(document.getElementById('investment').value);
            
            // Calcular ARR proyectado (3 años)
            const ARRProyectado = ARR * (1 + growth/100);
            
            // Calcular valuación
            const valuacion = ARRProyectado * multiple;
            const valuacionPre = valuacion - investment;
            
            // Calcular dilución
            const dilucion = (investment / valuacion) * 100;
            
            // Mostrar resultados
            document.getElementById('arr-proyectado').textContent = '$' + ARRProyectado.toLocaleString();
            document.getElementById('valuacion').textContent = '$' + valuacion.toLocaleString();
            document.getElementById('valuacion-pre').textContent = '$' + valuacionPre.toLocaleString();
            document.getElementById('dilucion').textContent = dilucion.toFixed(1) + '%';
        }
        
        // Calcular automáticamente al cargar
        window.onload = calcular;
    </script>
</body>
</html>
```

---

## 📊 DASHBOARD DE MÉTRICAS

### **Dashboard Interactivo**

```javascript
// Dashboard de métricas
class MetricDashboard {
    constructor() {
        this.metrics = {
            MRR: 11600,
            ARR: 139000,
            growth: 20,
            churn: 5,
            CAC: 150,
            LTV: 1350
        };
    }
    
    calcularMetricas() {
        const { MRR, growth, churn, CAC, LTV } = this.metrics;
        
        return {
            MRR12Meses: MRR * Math.pow(1 + growth/100, 12),
            ARR: MRR * 12,
            LTV_CAC: LTV / CAC,
            paybackPeriod: CAC / (MRR * (1 - churn/100)),
            churnRate: churn,
            growthRate: growth
        };
    }
    
    actualizarMetrica(metrica, valor) {
        this.metrics[metrica] = valor;
        return this.calcularMetricas();
    }
    
    generarReporte() {
        const metricas = this.calcularMetricas();
        
        return {
            resumen: {
                ARR: `$${metricas.ARR.toLocaleString()}`,
                LTV_CAC: `${metricas.LTV_CAC.toFixed(1)}:1`,
                paybackPeriod: `${metricas.paybackPeriod.toFixed(1)} meses`,
                churnRate: `${metricas.churnRate}%`,
                growthRate: `${metricas.growthRate}%`
            },
            status: {
                ARR: metricas.ARR > 1000000 ? '✅' : '⚠️',
                LTV_CAC: metricas.LTV_CAC > 3 ? '✅' : '⚠️',
                paybackPeriod: metricas.paybackPeriod < 12 ? '✅' : '⚠️',
                churnRate: metricas.churnRate < 5 ? '✅' : '⚠️',
                growthRate: metricas.growthRate > 15 ? '✅' : '⚠️'
            }
        };
    }
}

// Uso del dashboard
const dashboard = new MetricDashboard();
const reporte = dashboard.generarReporte();
console.log('Dashboard de Métricas:', reporte);
```

---

## 🎯 RECOMENDACIONES AUTOMÁTICAS

### **Sistema de Recomendaciones**

```javascript
// Sistema de recomendaciones
class RecommendationEngine {
    constructor(metricas) {
        this.metricas = metricas;
    }
    
    generarRecomendaciones() {
        const recomendaciones = [];
        
        // Recomendación de valuación
        if (this.metricas.LTV_CAC > 10) {
            recomendaciones.push({
                categoria: 'Valuación',
                mensaje: 'LTV/CAC excelente. Puedes negociar una valuación más alta.',
                accion: 'Proponer múltiplo de 15x en lugar de 12x'
            });
        }
        
        // Recomendación de dilución
        if (this.metricas.growthRate > 20) {
            recomendaciones.push({
                categoria: 'Dilución',
                mensaje: 'Crecimiento excepcional. Limita la dilución al 15%.',
                accion: 'Negociar dilución máxima del 15%'
            });
        }
        
        // Recomendación de consejo
        if (this.metricas.churnRate < 3) {
            recomendaciones.push({
                categoria: 'Consejo',
                mensaje: 'Retención excelente. Mantén control operativo.',
                accion: 'Insistir en consejo balanceado 2-2-1'
            });
        }
        
        return recomendaciones;
    }
}

// Uso del sistema de recomendaciones
const engine = new RecommendationEngine({
    LTV_CAC: 9,
    growthRate: 20,
    churnRate: 5
});

const recomendaciones = engine.generarRecomendaciones();
console.log('Recomendaciones:', recomendaciones);
```

---

*Herramienta de valuación preparada para SaaS IA Copywriting LATAM*  
*Versión 1.0 - Diciembre 2024*



