# 🎯 FRAMEWORK DE TOMA DE DECISIONES VC
## Sistema de Evaluación y Decisión para Negociaciones de Inversión

*Fecha: Diciembre 2024*  
*Versión: 1.0 - Framework de Decisión*  
*Sector: SaaS IA Marketing/Copywriting*

---

## 🧠 SISTEMA DE DECISIÓN ESTRATÉGICA

### **Matriz de Evaluación Multi-Criterio**

```javascript
// Framework de toma de decisiones para negociación VC
class VCDecisionFramework {
    constructor() {
        this.criterios = {
            financiero: {
                peso: 0.30,
                subcriterios: {
                    valuacion: 0.40,
                    dilution: 0.30,
                    liquidation: 0.30
                }
            },
            control: {
                peso: 0.25,
                subcriterios: {
                    consejo: 0.40,
                    veto: 0.35,
                    operaciones: 0.25
                }
            },
            estrategico: {
                peso: 0.20,
                subcriterios: {
                    valorAgregado: 0.40,
                    redContactos: 0.30,
                    experiencia: 0.30
                }
            },
            riesgo: {
                peso: 0.15,
                subcriterios: {
                    reputacion: 0.40,
                    trackRecord: 0.35,
                    conflictos: 0.25
                }
            },
            temporal: {
                peso: 0.10,
                subcriterios: {
                    urgencia: 0.50,
                    alternativas: 0.50
                }
            }
        };
    }
    
    evaluarOpcion(terminos, vcProfile) {
        const scores = this.calcularScores(terminos, vcProfile);
        const scoreTotal = this.calcularScoreTotal(scores);
        const recomendacion = this.generarRecomendacion(scoreTotal, scores);
        
        return {
            scoreTotal,
            scores,
            recomendacion,
            analisis: this.analizarFortalezasDebilidades(scores),
            acciones: this.generarAcciones(recomendacion, scores)
        };
    }
    
    calcularScores(terminos, vcProfile) {
        return {
            financiero: this.calcularScoreFinanciero(terminos),
            control: this.calcularScoreControl(terminos),
            estrategico: this.calcularScoreEstrategico(vcProfile),
            riesgo: this.calcularScoreRiesgo(vcProfile),
            temporal: this.calcularScoreTemporal(terminos)
        };
    }
    
    calcularScoreFinanciero(terminos) {
        let score = 0;
        
        // Score de valuación (0-100)
        const valuacionScore = this.evaluarValuacion(terminos.valuacion);
        score += valuacionScore * this.criterios.financiero.subcriterios.valuacion;
        
        // Score de dilución (0-100)
        const dilutionScore = this.evaluarDilucion(terminos.dilution);
        score += dilutionScore * this.criterios.financiero.subcriterios.dilution;
        
        // Score de liquidation preference (0-100)
        const liquidationScore = this.evaluarLiquidation(terminos.liquidation);
        score += liquidationScore * this.criterios.financiero.subcriterios.liquidation;
        
        return Math.round(score);
    }
    
    evaluarValuacion(valuacion) {
        if (valuacion >= 12000000) return 100;
        if (valuacion >= 10000000) return 90;
        if (valuacion >= 8000000) return 80;
        if (valuacion >= 6000000) return 60;
        if (valuacion >= 4000000) return 40;
        return 20;
    }
    
    evaluarDilucion(dilution) {
        if (dilution <= 15) return 100;
        if (dilution <= 20) return 90;
        if (dilution <= 25) return 80;
        if (dilution <= 30) return 60;
        if (dilution <= 40) return 40;
        return 20;
    }
    
    evaluarLiquidation(liquidation) {
        if (liquidation === '1x_non_participating') return 100;
        if (liquidation === '1x_participating_cap3x') return 90;
        if (liquidation === '1x_participating') return 70;
        if (liquidation === '1.5x_participating') return 50;
        if (liquidation === '2x_participating') return 30;
        return 10;
    }
    
    calcularScoreControl(terminos) {
        let score = 0;
        
        // Score de consejo (0-100)
        const consejoScore = this.evaluarConsejo(terminos.consejo);
        score += consejoScore * this.criterios.control.subcriterios.consejo;
        
        // Score de veto (0-100)
        const vetoScore = this.evaluarVeto(terminos.veto);
        score += vetoScore * this.criterios.control.subcriterios.veto;
        
        // Score de operaciones (0-100)
        const operacionesScore = this.evaluarOperaciones(terminos.operaciones);
        score += operacionesScore * this.criterios.control.subcriterios.operaciones;
        
        return Math.round(score);
    }
    
    evaluarConsejo(consejo) {
        if (consejo === '2-2-1') return 100;
        if (consejo === '2-3-0') return 70;
        if (consejo === '1-3-1') return 50;
        if (consejo === '1-4-0') return 30;
        return 10;
    }
    
    evaluarVeto(veto) {
        if (veto === 'solo_criticas') return 100;
        if (veto === 'criticas_estrategicas') return 80;
        if (veto === 'criticas_estrategicas_operativas') return 50;
        if (veto === 'todas') return 20;
        return 0;
    }
    
    evaluarOperaciones(operaciones) {
        if (operaciones === 'fundadores_completo') return 100;
        if (operaciones === 'fundadores_mayoria') return 80;
        if (operaciones === 'compartido') return 60;
        if (operaciones === 'vc_mayoria') return 30;
        return 10;
    }
    
    calcularScoreEstrategico(vcProfile) {
        let score = 0;
        
        // Score de valor agregado (0-100)
        const valorAgregadoScore = this.evaluarValorAgregado(vcProfile.valorAgregado);
        score += valorAgregadoScore * this.criterios.estrategico.subcriterios.valorAgregado;
        
        // Score de red de contactos (0-100)
        const redContactosScore = this.evaluarRedContactos(vcProfile.redContactos);
        score += redContactosScore * this.criterios.estrategico.subcriterios.redContactos;
        
        // Score de experiencia (0-100)
        const experienciaScore = this.evaluarExperiencia(vcProfile.experiencia);
        score += experienciaScore * this.criterios.estrategico.subcriterios.experiencia;
        
        return Math.round(score);
    }
    
    evaluarValorAgregado(valorAgregado) {
        let score = 0;
        
        if (valorAgregado.mentoring) score += 20;
        if (valorAgregado.redContactos) score += 25;
        if (valorAgregado.experiencia) score += 20;
        if (valorAgregado.recursos) score += 15;
        if (valorAgregado.reputacion) score += 20;
        
        return Math.min(score, 100);
    }
    
    evaluarRedContactos(redContactos) {
        if (redContactos === 'excelente') return 100;
        if (redContactos === 'muy_buena') return 80;
        if (redContactos === 'buena') return 60;
        if (redContactos === 'regular') return 40;
        return 20;
    }
    
    evaluarExperiencia(experiencia) {
        if (experiencia >= 10) return 100;
        if (experiencia >= 7) return 80;
        if (experiencia >= 5) return 60;
        if (experiencia >= 3) return 40;
        return 20;
    }
    
    calcularScoreRiesgo(vcProfile) {
        let score = 0;
        
        // Score de reputación (0-100)
        const reputacionScore = this.evaluarReputacion(vcProfile.reputacion);
        score += reputacionScore * this.criterios.riesgo.subcriterios.reputacion;
        
        // Score de track record (0-100)
        const trackRecordScore = this.evaluarTrackRecord(vcProfile.trackRecord);
        score += trackRecordScore * this.criterios.riesgo.subcriterios.trackRecord;
        
        // Score de conflictos (0-100)
        const conflictosScore = this.evaluarConflictos(vcProfile.conflictos);
        score += conflictosScore * this.criterios.riesgo.subcriterios.conflictos;
        
        return Math.round(score);
    }
    
    evaluarReputacion(reputacion) {
        if (reputacion === 'excelente') return 100;
        if (reputacion === 'muy_buena') return 80;
        if (reputacion === 'buena') return 60;
        if (reputacion === 'regular') return 40;
        return 20;
    }
    
    evaluarTrackRecord(trackRecord) {
        if (trackRecord.exitos >= 0.7) return 100;
        if (trackRecord.exitos >= 0.5) return 80;
        if (trackRecord.exitos >= 0.3) return 60;
        if (trackRecord.exitos >= 0.2) return 40;
        return 20;
    }
    
    evaluarConflictos(conflictos) {
        if (conflictos === 'ninguno') return 100;
        if (conflictos === 'menores') return 80;
        if (conflictos === 'moderados') return 60;
        if (conflictos === 'mayores') return 40;
        return 20;
    }
    
    calcularScoreTemporal(terminos) {
        let score = 0;
        
        // Score de urgencia (0-100)
        const urgenciaScore = this.evaluarUrgencia(terminos.urgencia);
        score += urgenciaScore * this.criterios.temporal.subcriterios.urgencia;
        
        // Score de alternativas (0-100)
        const alternativasScore = this.evaluarAlternativas(terminos.alternativas);
        score += alternativasScore * this.criterios.temporal.subcriterios.alternativas;
        
        return Math.round(score);
    }
    
    evaluarUrgencia(urgencia) {
        if (urgencia === 'baja') return 100;
        if (urgencia === 'media') return 70;
        if (urgencia === 'alta') return 40;
        return 20;
    }
    
    evaluarAlternativas(alternativas) {
        if (alternativas >= 5) return 100;
        if (alternativas >= 3) return 80;
        if (alternativas >= 2) return 60;
        if (alternativas >= 1) return 40;
        return 20;
    }
    
    calcularScoreTotal(scores) {
        let scoreTotal = 0;
        
        Object.keys(scores).forEach(criterio => {
            scoreTotal += scores[criterio] * this.criterios[criterio].peso;
        });
        
        return Math.round(scoreTotal);
    }
    
    generarRecomendacion(scoreTotal, scores) {
        if (scoreTotal >= 90) {
            return {
                accion: 'Aceptar Inmediatamente',
                confianza: 'Muy Alta',
                razon: 'Excelente combinación de términos y perfil del VC'
            };
        } else if (scoreTotal >= 80) {
            return {
                accion: 'Aceptar con Pequeñas Mejoras',
                confianza: 'Alta',
                razon: 'Buenos términos con oportunidades de mejora menores'
            };
        } else if (scoreTotal >= 70) {
            return {
                accion: 'Negociar Mejoras Moderadas',
                confianza: 'Media',
                razon: 'Términos aceptables pero con áreas de mejora significativas'
            };
        } else if (scoreTotal >= 60) {
            return {
                accion: 'Negociar Mejoras Significativas',
                confianza: 'Baja',
                razon: 'Términos problemáticos que requieren cambios importantes'
            };
        } else if (scoreTotal >= 50) {
            return {
                accion: 'Considerar Alternativas',
                confianza: 'Muy Baja',
                razon: 'Términos desfavorables, buscar otras opciones'
            };
        } else {
            return {
                accion: 'Rechazar',
                confianza: 'Nula',
                razon: 'Términos inaceptables, no proceder'
            };
        }
    }
    
    analizarFortalezasDebilidades(scores) {
        const fortalezas = [];
        const debilidades = [];
        
        Object.keys(scores).forEach(criterio => {
            if (scores[criterio] >= 80) {
                fortalezas.push(`${criterio}: ${scores[criterio]}/100`);
            } else if (scores[criterio] < 60) {
                debilidades.push(`${criterio}: ${scores[criterio]}/100`);
            }
        });
        
        return { fortalezas, debilidades };
    }
    
    generarAcciones(recomendacion, scores) {
        const acciones = [];
        
        if (recomendacion.accion.includes('Negociar')) {
            if (scores.financiero < 70) {
                acciones.push('Negociar mejoras en términos financieros');
            }
            if (scores.control < 70) {
                acciones.push('Negociar mejoras en estructura de control');
            }
            if (scores.estrategico < 70) {
                acciones.push('Evaluar valor agregado del VC');
            }
            if (scores.riesgo < 70) {
                acciones.push('Investigar más sobre el VC');
            }
        }
        
        if (recomendacion.accion.includes('Considerar Alternativas')) {
            acciones.push('Buscar otros VCs');
            acciones.push('Evaluar opciones de financiamiento alternativo');
            acciones.push('Considerar bootstrapping temporal');
        }
        
        return acciones;
    }
}

// Ejemplo de uso
const framework = new VCDecisionFramework();

const terminos = {
    valuacion: 10000000,
    dilution: 20,
    liquidation: '1x_participating_cap3x',
    consejo: '2-2-1',
    veto: 'solo_criticas',
    operaciones: 'fundadores_mayoria',
    urgencia: 'media',
    alternativas: 3
};

const vcProfile = {
    valorAgregado: {
        mentoring: true,
        redContactos: true,
        experiencia: true,
        recursos: true,
        reputacion: true
    },
    redContactos: 'muy_buena',
    experiencia: 8,
    reputacion: 'muy_buena',
    trackRecord: { exitos: 0.6 },
    conflictos: 'menores'
};

const evaluacion = framework.evaluarOpcion(terminos, vcProfile);
console.log('Evaluación de Decisión:', evaluacion);
```

---

## 🎯 MATRIZ DE DECISIÓN VISUAL

### **Dashboard de Evaluación**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Framework de Decisión VC</title>
    <style>
        .framework {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            font-family: Arial, sans-serif;
        }
        .criteria-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .criteria-card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .criteria-score {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .score-excellent { color: #28a745; }
        .score-good { color: #17a2b8; }
        .score-fair { color: #ffc107; }
        .score-poor { color: #dc3545; }
        .recommendation {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .recommendation.accept {
            background: #d4edda;
            border-color: #c3e6cb;
        }
        .recommendation.negotiate {
            background: #fff3cd;
            border-color: #ffeaa7;
        }
        .recommendation.reject {
            background: #f8d7da;
            border-color: #f5c6cb;
        }
        .actions {
            background: #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .action-item {
            background: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin: 5px 0;
        }
        .controls {
            margin: 20px 0;
        }
        .controls input, .controls select {
            margin-right: 10px;
            padding: 5px;
        }
    </style>
</head>
<body>
    <div class="framework">
        <h1>🎯 Framework de Toma de Decisiones VC</h1>
        
        <div class="controls">
            <label>Valuación:</label>
            <input type="number" id="valuation" value="10000000" step="100000">
            
            <label>Dilución:</label>
            <input type="number" id="dilution" value="20" step="1">
            
            <label>Consejo:</label>
            <select id="board">
                <option value="2-2-1">2-2-1</option>
                <option value="2-3-0">2-3-0</option>
                <option value="1-3-1">1-3-1</option>
                <option value="1-4-0">1-4-0</option>
            </select>
            
            <button onclick="evaluate()">Evaluar</button>
        </div>
        
        <div class="criteria-grid">
            <div class="criteria-card">
                <h3>💰 Financiero</h3>
                <div class="criteria-score score-excellent" id="financialScore">85</div>
                <p>Valuación, dilución, liquidation preference</p>
            </div>
            
            <div class="criteria-card">
                <h3>🎛️ Control</h3>
                <div class="criteria-score score-good" id="controlScore">75</div>
                <p>Consejo, veto, operaciones</p>
            </div>
            
            <div class="criteria-card">
                <h3>🚀 Estratégico</h3>
                <div class="criteria-score score-excellent" id="strategicScore">90</div>
                <p>Valor agregado, red, experiencia</p>
            </div>
            
            <div class="criteria-card">
                <h3>⚠️ Riesgo</h3>
                <div class="criteria-score score-good" id="riskScore">80</div>
                <p>Reputación, track record, conflictos</p>
            </div>
            
            <div class="criteria-card">
                <h3>⏰ Temporal</h3>
                <div class="criteria-score score-fair" id="temporalScore">65</div>
                <p>Urgencia, alternativas</p>
            </div>
        </div>
        
        <div class="recommendation negotiate" id="recommendation">
            <h3>📋 Recomendación</h3>
            <p><strong>Acción:</strong> Negociar Mejoras Moderadas</p>
            <p><strong>Confianza:</strong> Media</p>
            <p><strong>Razón:</strong> Términos aceptables pero con áreas de mejora significativas</p>
        </div>
        
        <div class="actions">
            <h3>🎯 Acciones Recomendadas</h3>
            <div class="action-item">Negociar mejoras en términos financieros</div>
            <div class="action-item">Evaluar valor agregado del VC</div>
            <div class="action-item">Investigar más sobre el VC</div>
        </div>
    </div>

    <script>
        function evaluate() {
            const valuation = parseInt(document.getElementById('valuation').value);
            const dilution = parseInt(document.getElementById('dilution').value);
            const board = document.getElementById('board').value;
            
            // Simular evaluación (en la implementación real usarías el framework)
            const scores = {
                financial: calculateFinancialScore(valuation, dilution),
                control: calculateControlScore(board),
                strategic: 90,
                risk: 80,
                temporal: 65
            };
            
            const totalScore = Math.round(
                scores.financial * 0.30 +
                scores.control * 0.25 +
                scores.strategic * 0.20 +
                scores.risk * 0.15 +
                scores.temporal * 0.10
            );
            
            // Actualizar scores
            document.getElementById('financialScore').textContent = scores.financial;
            document.getElementById('controlScore').textContent = scores.control;
            document.getElementById('strategicScore').textContent = scores.strategic;
            document.getElementById('riskScore').textContent = scores.risk;
            document.getElementById('temporalScore').textContent = scores.temporal;
            
            // Actualizar clases de score
            updateScoreClasses();
            
            // Actualizar recomendación
            updateRecommendation(totalScore);
        }
        
        function calculateFinancialScore(valuation, dilution) {
            let score = 0;
            
            // Score de valuación
            if (valuation >= 12000000) score += 40;
            else if (valuation >= 10000000) score += 36;
            else if (valuation >= 8000000) score += 32;
            else if (valuation >= 6000000) score += 24;
            else if (valuation >= 4000000) score += 16;
            else score += 8;
            
            // Score de dilución
            if (dilution <= 15) score += 30;
            else if (dilution <= 20) score += 27;
            else if (dilution <= 25) score += 24;
            else if (dilution <= 30) score += 18;
            else if (dilution <= 40) score += 12;
            else score += 6;
            
            // Score de liquidation (asumiendo 1x participating con cap)
            score += 30;
            
            return Math.min(score, 100);
        }
        
        function calculateControlScore(board) {
            const scores = {
                '2-2-1': 100,
                '2-3-0': 70,
                '1-3-1': 50,
                '1-4-0': 30
            };
            return scores[board] || 50;
        }
        
        function updateScoreClasses() {
            const scoreElements = document.querySelectorAll('.criteria-score');
            scoreElements.forEach(element => {
                const score = parseInt(element.textContent);
                element.className = 'criteria-score';
                
                if (score >= 80) element.classList.add('score-excellent');
                else if (score >= 70) element.classList.add('score-good');
                else if (score >= 60) element.classList.add('score-fair');
                else element.classList.add('score-poor');
            });
        }
        
        function updateRecommendation(totalScore) {
            const recommendation = document.getElementById('recommendation');
            let action, confidence, reason, className;
            
            if (totalScore >= 90) {
                action = 'Aceptar Inmediatamente';
                confidence = 'Muy Alta';
                reason = 'Excelente combinación de términos y perfil del VC';
                className = 'accept';
            } else if (totalScore >= 80) {
                action = 'Aceptar con Pequeñas Mejoras';
                confidence = 'Alta';
                reason = 'Buenos términos con oportunidades de mejora menores';
                className = 'accept';
            } else if (totalScore >= 70) {
                action = 'Negociar Mejoras Moderadas';
                confidence = 'Media';
                reason = 'Términos aceptables pero con áreas de mejora significativas';
                className = 'negotiate';
            } else if (totalScore >= 60) {
                action = 'Negociar Mejoras Significativas';
                confidence = 'Baja';
                reason = 'Términos problemáticos que requieren cambios importantes';
                className = 'negotiate';
            } else if (totalScore >= 50) {
                action = 'Considerar Alternativas';
                confidence = 'Muy Baja';
                reason = 'Términos desfavorables, buscar otras opciones';
                className = 'reject';
            } else {
                action = 'Rechazar';
                confidence = 'Nula';
                reason = 'Términos inaceptables, no proceder';
                className = 'reject';
            }
            
            recommendation.className = `recommendation ${className}`;
            recommendation.innerHTML = `
                <h3>📋 Recomendación</h3>
                <p><strong>Acción:</strong> ${action}</p>
                <p><strong>Confianza:</strong> ${confidence}</p>
                <p><strong>Razón:</strong> ${reason}</p>
                <p><strong>Score Total:</strong> ${totalScore}/100</p>
            `;
        }
        
        // Evaluar inicialmente
        evaluate();
    </script>
</body>
</html>
```

---

## 🎯 ESCENARIOS DE DECISIÓN

### **Escenario 1: VC Agresivo**

```
Perfil: VC con reputación de ser muy agresivo
Términos: Valuación baja, control alto, liquidation preference alta
Score: 45/100
Recomendación: Rechazar
Acciones: Buscar alternativas, considerar bootstrapping
```

### **Escenario 2: VC Balanceado**

```
Perfil: VC con buena reputación y términos balanceados
Términos: Valuación justa, consejo balanceado, términos estándar
Score: 85/100
Recomendación: Aceptar con Pequeñas Mejoras
Acciones: Negociar mejoras menores, proceder
```

### **Escenario 3: VC Estratégico**

```
Perfil: VC con excelente valor agregado pero términos estrictos
Términos: Valuación media, control alto, pero gran valor agregado
Score: 75/100
Recomendación: Negociar Mejoras Moderadas
Acciones: Negociar control, evaluar valor agregado
```

### **Escenario 4: VC Emergente**

```
Perfil: VC nuevo con poca experiencia pero términos flexibles
Términos: Valuación alta, control bajo, pero poca experiencia
Score: 65/100
Recomendación: Negociar Mejoras Significativas
Acciones: Evaluar riesgo, negociar términos, considerar alternativas
```

---

## 🎯 ALGORITMO DE DECISIÓN

### **Flujo de Decisión**

```javascript
// Algoritmo de decisión paso a paso
class DecisionAlgorithm {
    constructor() {
        this.umbrales = {
            aceptar: 80,
            negociar: 60,
            considerar: 50,
            rechazar: 40
        };
    }
    
    procesarDecision(terminos, vcProfile, contexto) {
        const pasos = [];
        
        // Paso 1: Evaluación inicial
        const evaluacionInicial = this.evaluarInicial(terminos, vcProfile);
        pasos.push({
            paso: 1,
            accion: 'Evaluación Inicial',
            resultado: evaluacionInicial,
            recomendacion: this.obtenerRecomendacionInicial(evaluacionInicial)
        });
        
        // Paso 2: Análisis de riesgo
        const analisisRiesgo = this.analizarRiesgo(terminos, vcProfile);
        pasos.push({
            paso: 2,
            accion: 'Análisis de Riesgo',
            resultado: analisisRiesgo,
            recomendacion: this.obtenerRecomendacionRiesgo(analisisRiesgo)
        });
        
        // Paso 3: Evaluación de alternativas
        const alternativas = this.evaluarAlternativas(contexto);
        pasos.push({
            paso: 3,
            accion: 'Evaluación de Alternativas',
            resultado: alternativas,
            recomendacion: this.obtenerRecomendacionAlternativas(alternativas)
        });
        
        // Paso 4: Decisión final
        const decisionFinal = this.tomarDecisionFinal(evaluacionInicial, analisisRiesgo, alternativas);
        pasos.push({
            paso: 4,
            accion: 'Decisión Final',
            resultado: decisionFinal,
            recomendacion: decisionFinal.recomendacion
        });
        
        return {
            pasos,
            decisionFinal,
            confianza: this.calcularConfianza(pasos),
            proximosPasos: this.generarProximosPasos(decisionFinal)
        };
    }
    
    evaluarInicial(terminos, vcProfile) {
        const framework = new VCDecisionFramework();
        return framework.evaluarOpcion(terminos, vcProfile);
    }
    
    analizarRiesgo(terminos, vcProfile) {
        const riesgos = [];
        
        // Riesgo financiero
        if (terminos.valuacion < 8000000) {
            riesgos.push({
                tipo: 'financiero',
                descripcion: 'Valuación baja puede indicar problemas futuros',
                severidad: 'alta'
            });
        }
        
        // Riesgo de control
        if (terminos.consejo === '1-4-0') {
            riesgos.push({
                tipo: 'control',
                descripcion: 'Pérdida de control operativo',
                severidad: 'alta'
            });
        }
        
        // Riesgo de reputación
        if (vcProfile.reputacion === 'regular') {
            riesgos.push({
                tipo: 'reputacion',
                descripcion: 'VC con reputación cuestionable',
                severidad: 'media'
            });
        }
        
        return {
            riesgos,
            nivelRiesgo: this.calcularNivelRiesgo(riesgos),
            mitigaciones: this.generarMitigaciones(riesgos)
        };
    }
    
    evaluarAlternativas(contexto) {
        const alternativas = [];
        
        // Alternativa 1: Otros VCs
        if (contexto.otrosVCs > 0) {
            alternativas.push({
                tipo: 'otros_vcs',
                descripcion: `Buscar otros ${contexto.otrosVCs} VCs`,
                probabilidad: 0.7,
                tiempo: '2-3 meses',
                esfuerzo: 'alto'
            });
        }
        
        // Alternativa 2: Financiamiento alternativo
        alternativas.push({
            tipo: 'financiamiento_alternativo',
            descripcion: 'Convertible notes, RBF, etc.',
            probabilidad: 0.8,
            tiempo: '1-2 meses',
            esfuerzo: 'medio'
        });
        
        // Alternativa 3: Bootstrapping
        alternativas.push({
            tipo: 'bootstrapping',
            descripcion: 'Crecer con ingresos propios',
            probabilidad: 0.9,
            tiempo: '6-12 meses',
            esfuerzo: 'muy_alto'
        });
        
        return {
            alternativas,
            mejorAlternativa: this.seleccionarMejorAlternativa(alternativas),
            recomendacion: this.generarRecomendacionAlternativas(alternativas)
        };
    }
    
    tomarDecisionFinal(evaluacionInicial, analisisRiesgo, alternativas) {
        const score = evaluacionInicial.scoreTotal;
        const nivelRiesgo = analisisRiesgo.nivelRiesgo;
        const mejorAlternativa = alternativas.mejorAlternativa;
        
        if (score >= this.umbrales.aceptar && nivelRiesgo === 'bajo') {
            return {
                accion: 'Aceptar',
                confianza: 'alta',
                razon: 'Excelentes términos con bajo riesgo',
                proximosPasos: ['Firmar term sheet', 'Iniciar due diligence']
            };
        } else if (score >= this.umbrales.negociar) {
            return {
                accion: 'Negociar',
                confianza: 'media',
                razon: 'Términos negociables con oportunidades de mejora',
                proximosPasos: ['Preparar contrapropuesta', 'Agendar reunión de negociación']
            };
        } else if (score >= this.umbrales.considerar) {
            return {
                accion: 'Considerar Alternativas',
                confianza: 'baja',
                razon: 'Términos problemáticos, evaluar otras opciones',
                proximosPasos: ['Evaluar alternativas', 'Mantener opción abierta']
            };
        } else {
            return {
                accion: 'Rechazar',
                confianza: 'alta',
                razon: 'Términos inaceptables, no proceder',
                proximosPasos: ['Buscar otras opciones', 'Considerar bootstrapping']
            };
        }
    }
    
    calcularNivelRiesgo(riesgos) {
        const riesgosAltos = riesgos.filter(r => r.severidad === 'alta').length;
        const riesgosMedios = riesgos.filter(r => r.severidad === 'media').length;
        
        if (riesgosAltos >= 2) return 'alto';
        if (riesgosAltos >= 1 || riesgosMedios >= 3) return 'medio';
        return 'bajo';
    }
    
    generarMitigaciones(riesgos) {
        const mitigaciones = [];
        
        riesgos.forEach(riesgo => {
            switch (riesgo.tipo) {
                case 'financiero':
                    mitigaciones.push('Negociar valuación más alta');
                    break;
                case 'control':
                    mitigaciones.push('Negociar estructura de consejo balanceada');
                    break;
                case 'reputacion':
                    mitigaciones.push('Investigar más sobre el VC');
                    break;
            }
        });
        
        return mitigaciones;
    }
    
    seleccionarMejorAlternativa(alternativas) {
        return alternativas.reduce((mejor, actual) => {
            const scoreActual = actual.probabilidad * 0.5 + (1 - actual.esfuerzo) * 0.5;
            const scoreMejor = mejor.probabilidad * 0.5 + (1 - mejor.esfuerzo) * 0.5;
            return scoreActual > scoreMejor ? actual : mejor;
        });
    }
    
    calcularConfianza(pasos) {
        const scores = pasos.map(p => p.resultado.scoreTotal || 0);
        const promedio = scores.reduce((sum, score) => sum + score, 0) / scores.length;
        return Math.round(promedio);
    }
    
    generarProximosPasos(decisionFinal) {
        const pasos = [];
        
        switch (decisionFinal.accion) {
            case 'Aceptar':
                pasos.push('Firmar term sheet');
                pasos.push('Iniciar due diligence');
                pasos.push('Preparar documentación legal');
                break;
            case 'Negociar':
                pasos.push('Preparar contrapropuesta');
                pasos.push('Agendar reunión de negociación');
                pasos.push('Definir límites de negociación');
                break;
            case 'Considerar Alternativas':
                pasos.push('Evaluar otras opciones de financiamiento');
                pasos.push('Contactar otros VCs');
                pasos.push('Considerar bootstrapping temporal');
                break;
            case 'Rechazar':
                pasos.push('Buscar otras opciones de financiamiento');
                pasos.push('Considerar bootstrapping');
                pasos.push('Revisar estrategia de crecimiento');
                break;
        }
        
        return pasos;
    }
}

// Ejemplo de uso
const algorithm = new DecisionAlgorithm();
const contexto = {
    otrosVCs: 3,
    urgencia: 'media',
    alternativas: ['convertible_notes', 'rbf', 'bootstrapping']
};

const decision = algorithm.procesarDecision(terminos, vcProfile, contexto);
console.log('Proceso de Decisión:', decision);
```

---

*Framework de toma de decisiones preparado para SaaS IA Copywriting LATAM*  
*Versión 1.0 - Diciembre 2024*

