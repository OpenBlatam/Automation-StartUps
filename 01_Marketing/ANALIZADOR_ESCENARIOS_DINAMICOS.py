#!/usr/bin/env python3
"""
Analizador de Escenarios Dinámicos para CopyCar.ai
Neural Marketing AI - SaaS IA LATAM
Análisis de escenarios dinámicos con Monte Carlo
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.optimize import minimize
import warnings
from datetime import datetime, timedelta
import json
warnings.filterwarnings('ignore')

class AnalizadorEscenariosDinamicos:
    def __init__(self):
        self.escenarios = {}
        self.simulaciones = {}
        self.analisis_sensibilidad = {}
        self.optimizaciones = {}
        
    def definir_escenarios_base(self):
        """Define escenarios base para análisis"""
        self.escenarios = {
            'conservador': {
                'nombre': 'Conservador',
                'descripcion': 'Crecimiento lento, alta competencia, mercado difícil',
                'parametros': {
                    'crecimiento_anual_valuation': 0.20,  # 20%
                    'crecimiento_anual_mrr': 0.15,  # 15%
                    'crecimiento_anual_users': 0.25,  # 25%
                    'dilucion_por_ronda': 0.25,  # 25%
                    'probabilidad_exito': 0.60,  # 60%
                    'competencia_intensidad': 0.80,  # 80%
                    'regulaciones_restrictivas': 0.70,  # 70%
                    'recesion_probabilidad': 0.30  # 30%
                }
            },
            'base': {
                'nombre': 'Base',
                'descripcion': 'Crecimiento moderado, competencia normal, mercado estable',
                'parametros': {
                    'crecimiento_anual_valuation': 0.40,  # 40%
                    'crecimiento_anual_mrr': 0.30,  # 30%
                    'crecimiento_anual_users': 0.35,  # 35%
                    'dilucion_por_ronda': 0.20,  # 20%
                    'probabilidad_exito': 0.75,  # 75%
                    'competencia_intensidad': 0.50,  # 50%
                    'regulaciones_restrictivas': 0.30,  # 30%
                    'recesion_probabilidad': 0.15  # 15%
                }
            },
            'optimista': {
                'nombre': 'Optimista',
                'descripcion': 'Crecimiento acelerado, baja competencia, mercado favorable',
                'parametros': {
                    'crecimiento_anual_valuation': 0.60,  # 60%
                    'crecimiento_anual_mrr': 0.45,  # 45%
                    'crecimiento_anual_users': 0.50,  # 50%
                    'dilucion_por_ronda': 0.15,  # 15%
                    'probabilidad_exito': 0.90,  # 90%
                    'competencia_intensidad': 0.20,  # 20%
                    'regulaciones_restrictivas': 0.10,  # 10%
                    'recesion_probabilidad': 0.05  # 5%
                }
            },
            'disruptivo': {
                'nombre': 'Disruptivo',
                'descripcion': 'Crecimiento exponencial, innovación disruptiva, mercado revolucionado',
                'parametros': {
                    'crecimiento_anual_valuation': 1.00,  # 100%
                    'crecimiento_anual_mrr': 0.80,  # 80%
                    'crecimiento_anual_users': 0.90,  # 90%
                    'dilucion_por_ronda': 0.10,  # 10%
                    'probabilidad_exito': 0.95,  # 95%
                    'competencia_intensidad': 0.10,  # 10%
                    'regulaciones_restrictivas': 0.05,  # 5%
                    'recesion_probabilidad': 0.02  # 2%
                }
            }
        }
        
        print("✅ Escenarios base definidos")
        return self.escenarios
    
    def simular_monte_carlo(self, n_simulaciones=1000):
        """Simula escenarios usando Monte Carlo"""
        if not self.escenarios:
            self.definir_escenarios_base()
        
        # Parámetros base
        valuation_inicial = 2000000
        mrr_inicial = 50000
        users_inicial = 1000
        equity_inicial = 60
        
        # Simulaciones para cada escenario
        for nombre_escenario, escenario in self.escenarios.items():
            simulaciones = []
            
            for i in range(n_simulaciones):
                # Generar valores aleatorios basados en parámetros
                params = escenario['parametros']
                
                # Simular crecimiento con variabilidad
                crecimiento_valuation = np.random.normal(
                    params['crecimiento_anual_valuation'], 
                    params['crecimiento_anual_valuation'] * 0.2
                )
                crecimiento_mrr = np.random.normal(
                    params['crecimiento_anual_mrr'], 
                    params['crecimiento_anual_mrr'] * 0.2
                )
                crecimiento_users = np.random.normal(
                    params['crecimiento_anual_users'], 
                    params['crecimiento_anual_users'] * 0.2
                )
                
                # Simular dilución
                dilucion = np.random.normal(
                    params['dilucion_por_ronda'], 
                    params['dilucion_por_ronda'] * 0.1
                )
                
                # Simular probabilidad de éxito
                exito = np.random.random() < params['probabilidad_exito']
                
                if exito:
                    # Calcular métricas finales
                    valuation_final = valuation_inicial * (1 + crecimiento_valuation)
                    mrr_final = mrr_inicial * (1 + crecimiento_mrr)
                    users_final = int(users_inicial * (1 + crecimiento_users))
                    equity_final = max(equity_inicial - dilucion * 100, 10)
                    valor_fundador = valuation_final * equity_final / 100
                    
                    simulaciones.append({
                        'simulacion': i,
                        'exito': True,
                        'valuation_final': valuation_final,
                        'mrr_final': mrr_final,
                        'users_final': users_final,
                        'equity_final': equity_final,
                        'valor_fundador': valor_fundador,
                        'dilucion_total': dilucion * 100,
                        'crecimiento_valuation': crecimiento_valuation,
                        'crecimiento_mrr': crecimiento_mrr,
                        'crecimiento_users': crecimiento_users
                    })
                else:
                    # Simulación fallida
                    simulaciones.append({
                        'simulacion': i,
                        'exito': False,
                        'valuation_final': valuation_inicial * 0.5,
                        'mrr_final': mrr_inicial * 0.3,
                        'users_final': int(users_inicial * 0.2),
                        'equity_final': equity_inicial * 0.8,
                        'valor_fundador': valuation_inicial * 0.5 * equity_inicial * 0.8 / 100,
                        'dilucion_total': dilucion * 100,
                        'crecimiento_valuation': -0.5,
                        'crecimiento_mrr': -0.7,
                        'crecimiento_users': -0.8
                    })
            
            self.simulaciones[nombre_escenario] = pd.DataFrame(simulaciones)
        
        print(f"✅ Simulaciones Monte Carlo completadas: {n_simulaciones} por escenario")
        return self.simulaciones
    
    def analizar_sensibilidad(self):
        """Analiza sensibilidad de variables clave"""
        if not self.simulaciones:
            self.simular_monte_carlo()
        
        # Variables para análisis de sensibilidad
        variables = [
            'crecimiento_valuation', 'crecimiento_mrr', 'crecimiento_users',
            'dilucion_total', 'probabilidad_exito'
        ]
        
        self.analisis_sensibilidad = {}
        
        for escenario, df in self.simulaciones.items():
            # Filtrar solo simulaciones exitosas
            df_exitosas = df[df['exito'] == True]
            
            if len(df_exitosas) == 0:
                continue
            
            sensibilidad = {}
            
            for variable in variables:
                if variable in df_exitosas.columns:
                    # Calcular correlación con valor del fundador
                    correlacion = df_exitosas[variable].corr(df_exitosas['valor_fundador'])
                    
                    # Calcular estadísticas
                    media = df_exitosas[variable].mean()
                    std = df_exitosas[variable].std()
                    percentil_25 = df_exitosas[variable].quantile(0.25)
                    percentil_75 = df_exitosas[variable].quantile(0.75)
                    
                    sensibilidad[variable] = {
                        'correlacion': correlacion,
                        'media': media,
                        'std': std,
                        'percentil_25': percentil_25,
                        'percentil_75': percentil_75,
                        'impacto': abs(correlacion)
                    }
            
            self.analisis_sensibilidad[escenario] = sensibilidad
        
        print("✅ Análisis de sensibilidad completado")
        return self.analisis_sensibilidad
    
    def optimizar_estrategias(self):
        """Optimiza estrategias para cada escenario"""
        if not self.simulaciones:
            self.simular_monte_carlo()
        
        self.optimizaciones = {}
        
        for escenario, df in self.simulaciones.items():
            # Filtrar solo simulaciones exitosas
            df_exitosas = df[df['exito'] == True]
            
            if len(df_exitosas) == 0:
                continue
            
            # Función objetivo: maximizar valor del fundador
            def objetivo(x):
                # x[0] = inversión en anti-dilución (0-1)
                # x[1] = inversión en crecimiento (0-1)
                # x[2] = inversión en partnerships (0-1)
                
                # Simular impacto de estrategias
                factor_anti_dilucion = 1 - x[0] * 0.3  # Reduce dilución
                factor_crecimiento = 1 + x[1] * 0.5   # Aumenta crecimiento
                factor_partnerships = 1 + x[2] * 0.3  # Aumenta valor
                
                # Calcular valor esperado
                valor_base = df_exitosas['valor_fundador'].mean()
                valor_optimizado = valor_base * factor_anti_dilucion * factor_crecimiento * factor_partnerships
                
                return -valor_optimizado  # Minimizar (negativo)
            
            # Restricciones
            constraints = [
                {'type': 'ineq', 'fun': lambda x: x[0]},  # x[0] >= 0
                {'type': 'ineq', 'fun': lambda x: 1 - x[0]},  # x[0] <= 1
                {'type': 'ineq', 'fun': lambda x: x[1]},  # x[1] >= 0
                {'type': 'ineq', 'fun': lambda x: 1 - x[1]},  # x[1] <= 1
                {'type': 'ineq', 'fun': lambda x: x[2]},  # x[2] >= 0
                {'type': 'ineq', 'fun': lambda x: 1 - x[2]},  # x[2] <= 1
                {'type': 'eq', 'fun': lambda x: x[0] + x[1] + x[2] - 1}  # Suma = 1
            ]
            
            # Optimización
            resultado = minimize(
                objetivo,
                x0=[0.33, 0.33, 0.34],
                method='SLSQP',
                constraints=constraints,
                bounds=[(0, 1), (0, 1), (0, 1)]
            )
            
            if resultado.success:
                self.optimizaciones[escenario] = {
                    'inversion_anti_dilucion': resultado.x[0],
                    'inversion_crecimiento': resultado.x[1],
                    'inversion_partnerships': resultado.x[2],
                    'valor_optimizado': -resultado.fun,
                    'mejora_porcentual': (-resultado.fun / df_exitosas['valor_fundador'].mean() - 1) * 100
                }
            else:
                self.optimizaciones[escenario] = {
                    'inversion_anti_dilucion': 0.33,
                    'inversion_crecimiento': 0.33,
                    'inversion_partnerships': 0.34,
                    'valor_optimizado': df_exitosas['valor_fundador'].mean(),
                    'mejora_porcentual': 0
                }
        
        print("✅ Optimización de estrategias completada")
        return self.optimizaciones
    
    def generar_reporte_escenarios(self):
        """Genera reporte completo de escenarios"""
        if not self.simulaciones:
            self.simular_monte_carlo()
        
        if not self.analisis_sensibilidad:
            self.analizar_sensibilidad()
        
        if not self.optimizaciones:
            self.optimizar_estrategias()
        
        reporte = f"""
# 🎯 ANALIZADOR DE ESCENARIOS DINÁMICOS - CopyCar.ai
## Neural Marketing AI - SaaS IA LATAM
### {datetime.now().strftime('%d de %B de %Y - %H:%M:%S')}

## 🎯 RESUMEN EJECUTIVO

### Análisis de Escenarios
- **Escenarios Analizados**: {len(self.escenarios)}
- **Simulaciones por Escenario**: 1,000
- **Total Simulaciones**: {len(self.escenarios) * 1000:,}
- **Método**: Monte Carlo con análisis de sensibilidad

## 📊 RESULTADOS POR ESCENARIO

### Escenarios Simulados
"""
        
        # Agregar resultados por escenario
        for escenario, df in self.simulaciones.items():
            df_exitosas = df[df['exito'] == True]
            probabilidad_exito = len(df_exitosas) / len(df) * 100
            
            if len(df_exitosas) > 0:
                valuation_promedio = df_exitosas['valuation_final'].mean()
                mrr_promedio = df_exitosas['mrr_final'].mean()
                users_promedio = df_exitosas['users_final'].mean()
                equity_promedio = df_exitosas['equity_final'].mean()
                valor_fundador_promedio = df_exitosas['valor_fundador'].mean()
                
                reporte += f"""
#### {escenario.title()}
- **Probabilidad de Éxito**: {probabilidad_exito:.1f}%
- **Valuación Promedio**: ${valuation_promedio/1000000:.1f}M
- **MRR Promedio**: ${mrr_promedio/1000:.0f}K
- **Usuarios Promedio**: {users_promedio:,.0f}
- **Equity Fundador Promedio**: {equity_promedio:.1f}%
- **Valor Fundador Promedio**: ${valor_fundador_promedio/1000000:.1f}M
"""
            else:
                reporte += f"""
#### {escenario.title()}
- **Probabilidad de Éxito**: 0.0%
- **Estado**: Escenario fallido
"""
        
        # Agregar análisis de sensibilidad
        reporte += f"""

## 📈 ANÁLISIS DE SENSIBILIDAD

### Variables Más Impactantes
"""
        
        for escenario, sensibilidad in self.analisis_sensibilidad.items():
            if sensibilidad:
                reporte += f"""
#### {escenario.title()}
"""
                # Ordenar por impacto
                variables_ordenadas = sorted(
                    sensibilidad.items(),
                    key=lambda x: x[1]['impacto'],
                    reverse=True
                )
                
                for variable, datos in variables_ordenadas[:3]:
                    reporte += f"""
- **{variable.replace('_', ' ').title()}**: Correlación = {datos['correlacion']:.3f}, Impacto = {datos['impacto']:.3f}
"""
        
        # Agregar optimizaciones
        reporte += f"""

## 🚀 OPTIMIZACIÓN DE ESTRATEGIAS

### Estrategias Optimizadas por Escenario
"""
        
        for escenario, optimizacion in self.optimizaciones.items():
            reporte += f"""
#### {escenario.title()}
- **Inversión Anti-Dilución**: {optimizacion['inversion_anti_dilucion']*100:.1f}%
- **Inversión Crecimiento**: {optimizacion['inversion_crecimiento']*100:.1f}%
- **Inversión Partnerships**: {optimizacion['inversion_partnerships']*100:.1f}%
- **Valor Optimizado**: ${optimizacion['valor_optimizado']/1000000:.1f}M
- **Mejora Porcentual**: {optimizacion['mejora_porcentual']:+.1f}%
"""
        
        # Agregar recomendaciones
        reporte += f"""

## 🎯 RECOMENDACIONES ESTRATÉGICAS

### Basadas en Análisis de Escenarios
1. **Implementar estrategias anti-dilución** en todos los escenarios
2. **Invertir en crecimiento** para maximizar valor
3. **Desarrollar partnerships** estratégicos
4. **Preparar para múltiples escenarios** simultáneamente
5. **Monitorear variables críticas** continuamente

### Estrategias Específicas por Escenario
"""
        
        for escenario, optimizacion in self.optimizaciones.items():
            if optimizacion['inversion_anti_dilucion'] > 0.4:
                reporte += f"""
- **{escenario.title()}**: Priorizar estrategias anti-dilución ({optimizacion['inversion_anti_dilucion']*100:.1f}%)
"""
            elif optimizacion['inversion_crecimiento'] > 0.4:
                reporte += f"""
- **{escenario.title()}**: Priorizar estrategias de crecimiento ({optimizacion['inversion_crecimiento']*100:.1f}%)
"""
            else:
                reporte += f"""
- **{escenario.title()}**: Estrategia balanceada
"""
        
        reporte += f"""

## 📊 PRÓXIMOS PASOS

### Implementación Inmediata
1. **Implementar estrategias optimizadas** según escenario más probable
2. **Configurar monitoreo** de variables críticas
3. **Preparar planes de contingencia** para cada escenario
4. **Actualizar análisis** con datos reales
5. **Ajustar estrategias** según resultados

---
*Generado por Analizador de Escenarios Dinámicos - Neural Marketing AI*
"""
        
        return reporte
    
    def ejecutar_analisis_completo(self):
        """Ejecuta análisis completo de escenarios"""
        print("🎯 Iniciando análisis de escenarios dinámicos...")
        
        # Definir escenarios
        self.definir_escenarios_base()
        
        # Simular Monte Carlo
        self.simular_monte_carlo()
        
        # Analizar sensibilidad
        self.analizar_sensibilidad()
        
        # Optimizar estrategias
        self.optimizar_estrategias()
        
        # Generar reporte
        reporte = self.generar_reporte_escenarios()
        
        # Guardar reporte
        with open('reporte_escenarios_dinamicos.md', 'w', encoding='utf-8') as f:
            f.write(reporte)
        
        # Guardar datos
        with open('simulaciones_escenarios.json', 'w', encoding='utf-8') as f:
            json.dump({
                'escenarios': self.escenarios,
                'simulaciones': {k: v.to_dict('records') for k, v in self.simulaciones.items()},
                'analisis_sensibilidad': self.analisis_sensibilidad,
                'optimizaciones': self.optimizaciones
            }, f, indent=2, ensure_ascii=False)
        
        print("✅ Análisis de escenarios completado")
        print(f"📊 Escenarios analizados: {len(self.escenarios)}")
        print(f"🎲 Simulaciones realizadas: {len(self.escenarios) * 1000:,}")
        
        return reporte

def main():
    """Función principal"""
    analizador = AnalizadorEscenariosDinamicos()
    
    print("=" * 80)
    print("🎯 ANALIZADOR DE ESCENARIOS DINÁMICOS")
    print("CopyCar.ai - Neural Marketing AI LATAM")
    print("=" * 80)
    
    # Ejecutar análisis completo
    reporte = analizador.ejecutar_analisis_completo()
    
    print("\n" + "=" * 80)
    print("📋 REPORTE DE ESCENARIOS GENERADO")
    print("=" * 80)
    print(reporte)

if __name__ == "__main__":
    main()






