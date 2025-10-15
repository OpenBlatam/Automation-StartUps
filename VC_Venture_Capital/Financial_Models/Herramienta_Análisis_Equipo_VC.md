# 👥 HERRAMIENTA DE ANÁLISIS DE EQUIPO VC
## Sistema de Evaluación de Equipo y Liderazgo para SaaS IA Copywriting LATAM

*Fecha: Diciembre 2024*  
*Versión: 1.0 - Análisis de Equipo*  
*Sector: SaaS IA Marketing/Copywriting*

---

## 🎯 SISTEMA DE ANÁLISIS DE EQUIPO

### **Evaluación Integral de Liderazgo**

```javascript
// Herramienta de análisis de equipo VC
class TeamAnalysisTool {
    constructor() {
        this.equipo = {
            fundadores: [
                {
                    nombre: 'CEO',
                    experiencia: 8,
                    sector: 'SaaS',
                    educacion: 'MBA',
                    trackRecord: 'Exitoso',
                    liderazgo: 'Fuerte',
                    vision: 'Clara',
                    ejecucion: 'Excelente'
                },
                {
                    nombre: 'CTO',
                    experiencia: 10,
                    sector: 'IA',
                    educacion: 'PhD',
                    trackRecord: 'Exitoso',
                    liderazgo: 'Técnico',
                    vision: 'Técnica',
                    ejecucion: 'Excelente'
                }
            ],
            equipo: {
                total: 12,
                senior: 8,
                junior: 4,
                rotacion: 0.05,
                satisfaccion: 0.85,
                productividad: 0.90
            },
            advisors: [
                {
                    nombre: 'Advisor 1',
                    experiencia: 15,
                    sector: 'SaaS',
                    rol: 'Estratégico',
                    valor: 'Alto'
                },
                {
                    nombre: 'Advisor 2',
                    experiencia: 12,
                    sector: 'IA',
                    rol: 'Técnico',
                    valor: 'Alto'
                }
            ]
        };
        
        this.criterios = {
            liderazgo: {
                peso: 0.30,
                subcriterios: {
                    vision: 0.25,
                    ejecucion: 0.25,
                    comunicacion: 0.20,
                    decision: 0.15,
                    motivacion: 0.15
                }
            },
            experiencia: {
                peso: 0.25,
                subcriterios: {
                    sector: 0.30,
                    años: 0.25,
                    trackRecord: 0.25,
                    educacion: 0.20
                }
            },
            equipo: {
                peso: 0.25,
                subcriterios: {
                    talento: 0.30,
                    retencion: 0.25,
                    productividad: 0.25,
                    cultura: 0.20
                }
            },
            advisors: {
                peso: 0.20,
                subcriterios: {
                    experiencia: 0.30,
                    red: 0.25,
                    valor: 0.25,
                    compromiso: 0.20
                }
            }
        };
    }
    
    analizarEquipo() {
        const analisis = {
            fundadores: this.analizarFundadores(),
            equipo: this.analizarEquipo(),
            advisors: this.analizarAdvisors(),
            fortalezas: this.identificarFortalezas(),
            debilidades: this.identificarDebilidades(),
            recomendaciones: this.generarRecomendaciones(),
            score: this.calcularScoreTotal()
        };
        
        return analisis;
    }
    
    analizarFundadores() {
        const fundadores = this.equipo.fundadores;
        
        return {
            total: fundadores.length,
            experiencia: this.calcularExperiencia(fundadores),
            liderazgo: this.calcularLiderazgo(fundadores),
            complementariedad: this.calcularComplementariedad(fundadores),
            fortalezas: this.identificarFortalezasFundadores(fundadores),
            debilidades: this.identificarDebilidadesFundadores(fundadores),
            recomendaciones: this.generarRecomendacionesFundadores(fundadores)
        };
    }
    
    analizarEquipo() {
        const equipo = this.equipo.equipo;
        
        return {
            total: equipo.total,
            composicion: this.analizarComposicion(equipo),
            retencion: this.analizarRetencion(equipo),
            productividad: this.analizarProductividad(equipo),
            cultura: this.analizarCultura(equipo),
            fortalezas: this.identificarFortalezasEquipo(equipo),
            debilidades: this.identificarDebilidadesEquipo(equipo),
            recomendaciones: this.generarRecomendacionesEquipo(equipo)
        };
    }
    
    analizarAdvisors() {
        const advisors = this.equipo.advisors;
        
        return {
            total: advisors.length,
            experiencia: this.calcularExperienciaAdvisors(advisors),
            red: this.calcularRed(advisors),
            valor: this.calcularValor(advisors),
            compromiso: this.calcularCompromiso(advisors),
            fortalezas: this.identificarFortalezasAdvisors(advisors),
            debilidades: this.identificarDebilidadesAdvisors(advisors),
            recomendaciones: this.generarRecomendacionesAdvisors(advisors)
        };
    }
    
    calcularExperiencia(fundadores) {
        const experiencia = fundadores.reduce((sum, f) => sum + f.experiencia, 0);
        const promedio = experiencia / fundadores.length;
        
        return {
            total: experiencia,
            promedio: Math.round(promedio * 10) / 10,
            nivel: promedio >= 8 ? 'Alto' : promedio >= 5 ? 'Medio' : 'Bajo'
        };
    }
    
    calcularLiderazgo(fundadores) {
        const liderazgo = fundadores.map(f => {
            let score = 0;
            if (f.liderazgo === 'Fuerte') score += 40;
            else if (f.liderazgo === 'Técnico') score += 30;
            else if (f.liderazgo === 'Moderado') score += 20;
            
            if (f.vision === 'Clara') score += 30;
            else if (f.vision === 'Técnica') score += 20;
            else if (f.vision === 'Básica') score += 10;
            
            if (f.ejecucion === 'Excelente') score += 30;
            else if (f.ejecucion === 'Buena') score += 20;
            else if (f.ejecucion === 'Regular') score += 10;
            
            return Math.min(score, 100);
        });
        
        const promedio = liderazgo.reduce((sum, score) => sum + score, 0) / liderazgo.length;
        
        return {
            scores: liderazgo,
            promedio: Math.round(promedio),
            nivel: promedio >= 80 ? 'Excelente' : promedio >= 60 ? 'Bueno' : 'Regular'
        };
    }
    
    calcularComplementariedad(fundadores) {
        const ceo = fundadores.find(f => f.nombre === 'CEO');
        const cto = fundadores.find(f => f.nombre === 'CTO');
        
        if (!ceo || !cto) return { score: 0, nivel: 'Bajo' };
        
        let score = 0;
        
        // Complementariedad de habilidades
        if (ceo.sector === 'SaaS' && cto.sector === 'IA') score += 30;
        if (ceo.liderazgo === 'Fuerte' && cto.liderazgo === 'Técnico') score += 25;
        if (ceo.vision === 'Clara' && cto.vision === 'Técnica') score += 25;
        if (ceo.ejecucion === 'Excelente' && cto.ejecucion === 'Excelente') score += 20;
        
        return {
            score: Math.min(score, 100),
            nivel: score >= 80 ? 'Excelente' : score >= 60 ? 'Bueno' : 'Regular'
        };
    }
    
    analizarComposicion(equipo) {
        const ratio = equipo.senior / equipo.junior;
        
        return {
            senior: equipo.senior,
            junior: equipo.junior,
            ratio: Math.round(ratio * 10) / 10,
            nivel: ratio >= 2 ? 'Excelente' : ratio >= 1.5 ? 'Bueno' : 'Regular'
        };
    }
    
    analizarRetencion(equipo) {
        const rotacion = equipo.rotacion;
        const satisfaccion = equipo.satisfaccion;
        
        return {
            rotacion: rotacion,
            satisfaccion: satisfaccion,
            nivel: rotacion < 0.05 && satisfaccion > 0.8 ? 'Excelente' : 
                   rotacion < 0.1 && satisfaccion > 0.7 ? 'Bueno' : 'Regular'
        };
    }
    
    analizarProductividad(equipo) {
        const productividad = equipo.productividad;
        
        return {
            score: productividad,
            nivel: productividad >= 0.9 ? 'Excelente' : 
                   productividad >= 0.8 ? 'Bueno' : 'Regular'
        };
    }
    
    analizarCultura(equipo) {
        const satisfaccion = equipo.satisfaccion;
        const productividad = equipo.productividad;
        const rotacion = equipo.rotacion;
        
        const score = (satisfaccion + productividad + (1 - rotacion)) / 3;
        
        return {
            score: Math.round(score * 100) / 100,
            nivel: score >= 0.85 ? 'Excelente' : 
                   score >= 0.75 ? 'Bueno' : 'Regular'
        };
    }
    
    calcularExperienciaAdvisors(advisors) {
        const experiencia = advisors.reduce((sum, a) => sum + a.experiencia, 0);
        const promedio = experiencia / advisors.length;
        
        return {
            total: experiencia,
            promedio: Math.round(promedio * 10) / 10,
            nivel: promedio >= 12 ? 'Alto' : promedio >= 8 ? 'Medio' : 'Bajo'
        };
    }
    
    calcularRed(advisors) {
        const red = advisors.map(a => {
            let score = 0;
            if (a.experiencia >= 15) score += 40;
            else if (a.experiencia >= 10) score += 30;
            else if (a.experiencia >= 5) score += 20;
            
            if (a.sector === 'SaaS' || a.sector === 'IA') score += 30;
            else if (a.sector === 'Tech') score += 20;
            else score += 10;
            
            if (a.rol === 'Estratégico') score += 30;
            else if (a.rol === 'Técnico') score += 20;
            else score += 10;
            
            return Math.min(score, 100);
        });
        
        const promedio = red.reduce((sum, score) => sum + score, 0) / red.length;
        
        return {
            scores: red,
            promedio: Math.round(promedio),
            nivel: promedio >= 80 ? 'Excelente' : promedio >= 60 ? 'Bueno' : 'Regular'
        };
    }
    
    calcularValor(advisors) {
        const valor = advisors.map(a => {
            let score = 0;
            if (a.valor === 'Alto') score += 50;
            else if (a.valor === 'Medio') score += 30;
            else score += 10;
            
            if (a.experiencia >= 15) score += 30;
            else if (a.experiencia >= 10) score += 20;
            else score += 10;
            
            if (a.rol === 'Estratégico') score += 20;
            else if (a.rol === 'Técnico') score += 15;
            else score += 10;
            
            return Math.min(score, 100);
        });
        
        const promedio = valor.reduce((sum, score) => sum + score, 0) / valor.length;
        
        return {
            scores: valor,
            promedio: Math.round(promedio),
            nivel: promedio >= 80 ? 'Excelente' : promedio >= 60 ? 'Bueno' : 'Regular'
        };
    }
    
    calcularCompromiso(advisors) {
        // Simulación basada en experiencia y valor
        const compromiso = advisors.map(a => {
            let score = 0;
            if (a.experiencia >= 15) score += 40;
            else if (a.experiencia >= 10) score += 30;
            else score += 20;
            
            if (a.valor === 'Alto') score += 40;
            else if (a.valor === 'Medio') score += 30;
            else score += 20;
            
            if (a.rol === 'Estratégico') score += 20;
            else if (a.rol === 'Técnico') score += 15;
            else score += 10;
            
            return Math.min(score, 100);
        });
        
        const promedio = compromiso.reduce((sum, score) => sum + score, 0) / compromiso.length;
        
        return {
            scores: compromiso,
            promedio: Math.round(promedio),
            nivel: promedio >= 80 ? 'Excelente' : promedio >= 60 ? 'Bueno' : 'Regular'
        };
    }
    
    identificarFortalezasFundadores(fundadores) {
        const fortalezas = [];
        
        if (fundadores.some(f => f.experiencia >= 8)) {
            fortalezas.push('Experiencia sólida');
        }
        if (fundadores.some(f => f.trackRecord === 'Exitoso')) {
            fortalezas.push('Track record exitoso');
        }
        if (fundadores.some(f => f.liderazgo === 'Fuerte')) {
            fortalezas.push('Liderazgo fuerte');
        }
        if (fundadores.some(f => f.vision === 'Clara')) {
            fortalezas.push('Visión clara');
        }
        if (fundadores.some(f => f.ejecucion === 'Excelente')) {
            fortalezas.push('Ejecución excelente');
        }
        
        return fortalezas;
    }
    
    identificarDebilidadesFundadores(fundadores) {
        const debilidades = [];
        
        if (fundadores.length < 2) {
            debilidades.push('Equipo de fundadores limitado');
        }
        if (fundadores.some(f => f.experiencia < 5)) {
            debilidades.push('Experiencia limitada en algunos fundadores');
        }
        if (fundadores.some(f => f.trackRecord === 'Limitado')) {
            debilidades.push('Track record limitado');
        }
        if (fundadores.some(f => f.liderazgo === 'Débil')) {
            debilidades.push('Liderazgo débil');
        }
        if (fundadores.some(f => f.vision === 'Confusa')) {
            debilidades.push('Visión confusa');
        }
        
        return debilidades;
    }
    
    identificarFortalezasEquipo(equipo) {
        const fortalezas = [];
        
        if (equipo.total >= 10) {
            fortalezas.push('Equipo numeroso');
        }
        if (equipo.senior / equipo.junior >= 2) {
            fortalezas.push('Ratio senior/junior excelente');
        }
        if (equipo.rotacion < 0.05) {
            fortalezas.push('Baja rotación');
        }
        if (equipo.satisfaccion >= 0.8) {
            fortalezas.push('Alta satisfacción');
        }
        if (equipo.productividad >= 0.9) {
            fortalezas.push('Alta productividad');
        }
        
        return fortalezas;
    }
    
    identificarDebilidadesEquipo(equipo) {
        const debilidades = [];
        
        if (equipo.total < 10) {
            debilidades.push('Equipo pequeño');
        }
        if (equipo.senior / equipo.junior < 1.5) {
            debilidades.push('Ratio senior/junior bajo');
        }
        if (equipo.rotacion >= 0.1) {
            debilidades.push('Alta rotación');
        }
        if (equipo.satisfaccion < 0.7) {
            debilidades.push('Baja satisfacción');
        }
        if (equipo.productividad < 0.8) {
            debilidades.push('Baja productividad');
        }
        
        return debilidades;
    }
    
    identificarFortalezasAdvisors(advisors) {
        const fortalezas = [];
        
        if (advisors.length >= 2) {
            fortalezas.push('Múltiples advisors');
        }
        if (advisors.some(a => a.experiencia >= 15)) {
            fortalezas.push('Advisors con experiencia');
        }
        if (advisors.some(a => a.sector === 'SaaS' || a.sector === 'IA')) {
            fortalezas.push('Advisors del sector');
        }
        if (advisors.some(a => a.valor === 'Alto')) {
            fortalezas.push('Advisors de alto valor');
        }
        if (advisors.some(a => a.rol === 'Estratégico')) {
            fortalezas.push('Advisors estratégicos');
        }
        
        return fortalezas;
    }
    
    identificarDebilidadesAdvisors(advisors) {
        const debilidades = [];
        
        if (advisors.length < 2) {
            debilidades.push('Pocos advisors');
        }
        if (advisors.some(a => a.experiencia < 10)) {
            debilidades.push('Advisors con poca experiencia');
        }
        if (advisors.some(a => a.sector !== 'SaaS' && a.sector !== 'IA')) {
            debilidades.push('Advisors fuera del sector');
        }
        if (advisors.some(a => a.valor === 'Bajo')) {
            debilidades.push('Advisors de bajo valor');
        }
        if (advisors.some(a => a.rol === 'Limitado')) {
            debilidades.push('Advisors con rol limitado');
        }
        
        return debilidades;
    }
    
    generarRecomendacionesFundadores(fundadores) {
        const recomendaciones = [];
        
        if (fundadores.length < 2) {
            recomendaciones.push('Agregar co-fundador');
        }
        if (fundadores.some(f => f.experiencia < 5)) {
            recomendaciones.push('Desarrollar experiencia');
        }
        if (fundadores.some(f => f.trackRecord === 'Limitado')) {
            recomendaciones.push('Construir track record');
        }
        if (fundadores.some(f => f.liderazgo === 'Débil')) {
            recomendaciones.push('Desarrollar liderazgo');
        }
        if (fundadores.some(f => f.vision === 'Confusa')) {
            recomendaciones.push('Clarificar visión');
        }
        
        return recomendaciones;
    }
    
    generarRecomendacionesEquipo(equipo) {
        const recomendaciones = [];
        
        if (equipo.total < 10) {
            recomendaciones.push('Expandir equipo');
        }
        if (equipo.senior / equipo.junior < 1.5) {
            recomendaciones.push('Contratar más seniors');
        }
        if (equipo.rotacion >= 0.1) {
            recomendaciones.push('Mejorar retención');
        }
        if (equipo.satisfaccion < 0.7) {
            recomendaciones.push('Mejorar satisfacción');
        }
        if (equipo.productividad < 0.8) {
            recomendaciones.push('Mejorar productividad');
        }
        
        return recomendaciones;
    }
    
    generarRecomendacionesAdvisors(advisors) {
        const recomendaciones = [];
        
        if (advisors.length < 2) {
            recomendaciones.push('Agregar más advisors');
        }
        if (advisors.some(a => a.experiencia < 10)) {
            recomendaciones.push('Buscar advisors con más experiencia');
        }
        if (advisors.some(a => a.sector !== 'SaaS' && a.sector !== 'IA')) {
            recomendaciones.push('Buscar advisors del sector');
        }
        if (advisors.some(a => a.valor === 'Bajo')) {
            recomendaciones.push('Buscar advisors de mayor valor');
        }
        if (advisors.some(a => a.rol === 'Limitado')) {
            recomendaciones.push('Definir roles más claros');
        }
        
        return recomendaciones;
    }
    
    identificarFortalezas() {
        const fortalezas = [];
        
        // Fortalezas de fundadores
        const fundadores = this.analizarFundadores();
        fortalezas.push(...fundadores.fortalezas);
        
        // Fortalezas de equipo
        const equipo = this.analizarEquipo();
        fortalezas.push(...equipo.fortalezas);
        
        // Fortalezas de advisors
        const advisors = this.analizarAdvisors();
        fortalezas.push(...advisors.fortalezas);
        
        return [...new Set(fortalezas)]; // Eliminar duplicados
    }
    
    identificarDebilidades() {
        const debilidades = [];
        
        // Debilidades de fundadores
        const fundadores = this.analizarFundadores();
        debilidades.push(...fundadores.debilidades);
        
        // Debilidades de equipo
        const equipo = this.analizarEquipo();
        debilidades.push(...equipo.debilidades);
        
        // Debilidades de advisors
        const advisors = this.analizarAdvisors();
        debilidades.push(...advisors.debilidades);
        
        return [...new Set(debilidades)]; // Eliminar duplicados
    }
    
    generarRecomendaciones() {
        const recomendaciones = [];
        
        // Recomendaciones de fundadores
        const fundadores = this.analizarFundadores();
        recomendaciones.push(...fundadores.recomendaciones);
        
        // Recomendaciones de equipo
        const equipo = this.analizarEquipo();
        recomendaciones.push(...equipo.recomendaciones);
        
        // Recomendaciones de advisors
        const advisors = this.analizarAdvisors();
        recomendaciones.push(...advisors.recomendaciones);
        
        return [...new Set(recomendaciones)]; // Eliminar duplicados
    }
    
    calcularScoreTotal() {
        const fundadores = this.analizarFundadores();
        const equipo = this.analizarEquipo();
        const advisors = this.analizarAdvisors();
        
        let score = 0;
        let peso = 0;
        
        // Score de fundadores
        const scoreFundadores = (fundadores.experiencia.nivel === 'Alto' ? 30 : 
                                fundadores.experiencia.nivel === 'Medio' ? 20 : 10) +
                               (fundadores.liderazgo.nivel === 'Excelente' ? 30 : 
                                fundadores.liderazgo.nivel === 'Bueno' ? 20 : 10) +
                               (fundadores.complementariedad.nivel === 'Excelente' ? 40 : 
                                fundadores.complementariedad.nivel === 'Bueno' ? 30 : 20);
        
        score += scoreFundadores * this.criterios.liderazgo.peso;
        peso += this.criterios.liderazgo.peso;
        
        // Score de equipo
        const scoreEquipo = (equipo.composicion.nivel === 'Excelente' ? 30 : 
                            equipo.composicion.nivel === 'Bueno' ? 20 : 10) +
                           (equipo.retencion.nivel === 'Excelente' ? 30 : 
                            equipo.retencion.nivel === 'Bueno' ? 20 : 10) +
                           (equipo.productividad.nivel === 'Excelente' ? 40 : 
                            equipo.productividad.nivel === 'Bueno' ? 30 : 20);
        
        score += scoreEquipo * this.criterios.equipo.peso;
        peso += this.criterios.equipo.peso;
        
        // Score de advisors
        const scoreAdvisors = (advisors.experiencia.nivel === 'Alto' ? 30 : 
                              advisors.experiencia.nivel === 'Medio' ? 20 : 10) +
                             (advisors.red.nivel === 'Excelente' ? 30 : 
                              advisors.red.nivel === 'Bueno' ? 20 : 10) +
                             (advisors.valor.nivel === 'Excelente' ? 40 : 
                              advisors.valor.nivel === 'Bueno' ? 30 : 20);
        
        score += scoreAdvisors * this.criterios.advisors.peso;
        peso += this.criterios.advisors.peso;
        
        return {
            score: Math.round(score / peso),
            nivel: score / peso >= 80 ? 'Excelente' : 
                   score / peso >= 60 ? 'Bueno' : 'Regular'
        };
    }
}

// Ejemplo de uso
const teamTool = new TeamAnalysisTool();
const analisis = teamTool.analizarEquipo();
console.log('Análisis de Equipo:', analisis);
```

---

*Herramienta de análisis de equipo preparada para SaaS IA Copywriting LATAM*  
*Versión 1.0 - Diciembre 2024*

