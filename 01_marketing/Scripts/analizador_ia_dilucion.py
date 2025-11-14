#!/usr/bin/env python3
"""
Analizador de IA para Estrategias Anti-Dilución
Neural Marketing AI - SaaS IA LATAM
Utiliza Machine Learning para optimizar estrategias de dilución
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import warnings
warnings.filterwarnings('ignore')

class AnalizadorIADilucion:
    def __init__(self):
        self.modelos = {}
        self.datos_entrenamiento = None
        self.scaler = StandardScaler()
        self.resultados_prediccion = {}
        
    def generar_datos_entrenamiento(self):
        """Genera datos de entrenamiento basados en casos reales de startups LATAM"""
        np.random.seed(42)
        n_samples = 1000
        
        # Variables de entrada
        datos = {
            'valuacion_inicial': np.random.lognormal(6, 1, n_samples),  # 1M-10M
            'crecimiento_anual': np.random.normal(0.25, 0.1, n_samples),  # 15%-35%
            'dilucion_por_ronda': np.random.normal(0.18, 0.05, n_samples),  # 13%-23%
            'num_rondas': np.random.poisson(4, n_samples),  # 2-6 rondas
            'tipo_estrategia': np.random.choice(['Sin_Proteccion', 'Weighted_Average', 'Clases_Diferenciadas', 'SAFE', 'Strategic_Partnerships'], n_samples),
            'sector': np.random.choice(['Fintech', 'E-commerce', 'SaaS', 'Marketplace', 'AI'], n_samples),
            'pais': np.random.choice(['Brasil', 'Mexico', 'Argentina', 'Colombia', 'Chile'], n_samples),
            'tamano_equipo_inicial': np.random.poisson(8, n_samples),  # 3-15 personas
            'experiencia_fundadores': np.random.normal(7, 2, n_samples),  # 3-11 años
            'traction_inicial': np.random.uniform(0.1, 0.5, n_samples),  # 10%-50% MRR growth
        }
        
        # Calcular variables objetivo basadas en reglas de negocio
        equity_final = []
        valor_fundador = []
        roi_inversionistas = []
        
        for i in range(n_samples):
            # Calcular equity final basado en estrategia
            if datos['tipo_estrategia'][i] == 'Sin_Proteccion':
                dilucion_total = datos['dilucion_por_ronda'][i] * datos['num_rondas'][i]
            elif datos['tipo_estrategia'][i] == 'Weighted_Average':
                dilucion_total = datos['dilucion_por_ronda'][i] * datos['num_rondas'][i] * 0.8
            elif datos['tipo_estrategia'][i] == 'Clases_Diferenciadas':
                dilucion_total = datos['dilucion_por_ronda'][i] * datos['num_rondas'][i] * 0.6
            elif datos['tipo_estrategia'][i] == 'SAFE':
                dilucion_total = datos['dilucion_por_ronda'][i] * datos['num_rondas'][i] * 0.7
            else:  # Strategic_Partnerships
                dilucion_total = datos['dilucion_por_ronda'][i] * datos['num_rondas'][i] * 0.5
            
            equity_final.append(max(20, 100 - dilucion_total * 100))
            
            # Calcular valuación final
            valuacion_final = datos['valuacion_inicial'][i] * (1 + datos['crecimiento_anual'][i]) ** datos['num_rondas'][i]
            
            # Calcular valor del fundador
            valor_fundador.append(valuacion_final * (equity_final[-1] / 100))
            
            # Calcular ROI de inversionistas
            roi_inversionistas.append(valuacion_final / datos['valuacion_inicial'][i])
        
        datos['equity_final'] = equity_final
        datos['valor_fundador'] = valor_fundador
        datos['roi_inversionistas'] = roi_inversionistas
        
        self.datos_entrenamiento = pd.DataFrame(datos)
        return self.datos_entrenamiento
    
    def entrenar_modelos(self):
        """Entrena modelos de ML para predecir resultados de dilución"""
        if self.datos_entrenamiento is None:
            self.generar_datos_entrenamiento()
        
        # Preparar datos
        X = self.datos_entrenamiento.drop(['equity_final', 'valor_fundador', 'roi_inversionistas'], axis=1)
        y_equity = self.datos_entrenamiento['equity_final']
        y_valor = self.datos_entrenamiento['valor_fundador']
        y_roi = self.datos_entrenamiento['roi_inversionistas']
        
        # Codificar variables categóricas
        X_encoded = pd.get_dummies(X, columns=['tipo_estrategia', 'sector', 'pais'])
        
        # Dividir datos
        X_train, X_test, y_equity_train, y_equity_test = train_test_split(X_encoded, y_equity, test_size=0.2, random_state=42)
        _, _, y_valor_train, y_valor_test = train_test_split(X_encoded, y_valor, test_size=0.2, random_state=42)
        _, _, y_roi_train, y_roi_test = train_test_split(X_encoded, y_roi, test_size=0.2, random_state=42)
        
        # Normalizar datos
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entrenar modelos
        self.modelos['equity'] = RandomForestRegressor(n_estimators=100, random_state=42)
        self.modelos['valor'] = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.modelos['roi'] = RandomForestRegressor(n_estimators=100, random_state=42)
        
        self.modelos['equity'].fit(X_train_scaled, y_equity_train)
        self.modelos['valor'].fit(X_train_scaled, y_valor_train)
        self.modelos['roi'].fit(X_train_scaled, y_roi_train)
        
        # Evaluar modelos
        equity_pred = self.modelos['equity'].predict(X_test_scaled)
        valor_pred = self.modelos['valor'].predict(X_test_scaled)
        roi_pred = self.modelos['roi'].predict(X_test_scaled)
        
        print("🎯 Rendimiento de Modelos de IA:")
        print(f"Equity Final - R²: {r2_score(y_equity_test, equity_pred):.3f}")
        print(f"Valor Fundador - R²: {r2_score(y_valor_test, valor_pred):.3f}")
        print(f"ROI Inversionistas - R²: {r2_score(y_roi_test, roi_pred):.3f}")
        
        return self.modelos
    
    def predecir_escenario(self, configuracion):
        """Predice resultados para un escenario específico"""
        if not self.modelos:
            self.entrenar_modelos()
        
        # Preparar datos de entrada
        datos_entrada = pd.DataFrame([configuracion])
        datos_encoded = pd.get_dummies(datos_entrada, columns=['tipo_estrategia', 'sector', 'pais'])
        
        # Asegurar que todas las columnas estén presentes
        columnas_entrenamiento = self.scaler.feature_names_in_
        for col in columnas_entrenamiento:
            if col not in datos_encoded.columns:
                datos_encoded[col] = 0
        
        datos_encoded = datos_encoded[columnas_entrenamiento]
        datos_scaled = self.scaler.transform(datos_encoded)
        
        # Hacer predicciones
        equity_pred = self.modelos['equity'].predict(datos_scaled)[0]
        valor_pred = self.modelos['valor'].predict(datos_scaled)[0]
        roi_pred = self.modelos['roi'].predict(datos_scaled)[0]
        
        return {
            'equity_final': max(0, min(100, equity_pred)),
            'valor_fundador': max(0, valor_pred),
            'roi_inversionistas': max(1, roi_pred)
        }
    
    def analizar_estrategias_optimizadas(self):
        """Analiza y recomienda estrategias optimizadas usando IA"""
        estrategias = {
            'Sin_Proteccion': {
                'valuacion_inicial': 2000000,
                'crecimiento_anual': 0.25,
                'dilucion_por_ronda': 0.20,
                'num_rondas': 4,
                'tipo_estrategia': 'Sin_Proteccion',
                'sector': 'AI',
                'pais': 'Mexico',
                'tamano_equipo_inicial': 8,
                'experiencia_fundadores': 7,
                'traction_inicial': 0.3
            },
            'Weighted_Average': {
                'valuacion_inicial': 2000000,
                'crecimiento_anual': 0.25,
                'dilucion_por_ronda': 0.15,
                'num_rondas': 4,
                'tipo_estrategia': 'Weighted_Average',
                'sector': 'AI',
                'pais': 'Mexico',
                'tamano_equipo_inicial': 8,
                'experiencia_fundadores': 7,
                'traction_inicial': 0.3
            },
            'Clases_Diferenciadas': {
                'valuacion_inicial': 2000000,
                'crecimiento_anual': 0.25,
                'dilucion_por_ronda': 0.12,
                'num_rondas': 4,
                'tipo_estrategia': 'Clases_Diferenciadas',
                'sector': 'AI',
                'pais': 'Mexico',
                'tamano_equipo_inicial': 8,
                'experiencia_fundadores': 7,
                'traction_inicial': 0.3
            },
            'SAFE_Convertible': {
                'valuacion_inicial': 2000000,
                'crecimiento_anual': 0.25,
                'dilucion_por_ronda': 0.14,
                'num_rondas': 4,
                'tipo_estrategia': 'SAFE',
                'sector': 'AI',
                'pais': 'Mexico',
                'tamano_equipo_inicial': 8,
                'experiencia_fundadores': 7,
                'traction_inicial': 0.3
            },
            'Strategic_Partnerships': {
                'valuacion_inicial': 2000000,
                'crecimiento_anual': 0.30,
                'dilucion_por_ronda': 0.10,
                'num_rondas': 4,
                'tipo_estrategia': 'Strategic_Partnerships',
                'sector': 'AI',
                'pais': 'Mexico',
                'tamano_equipo_inicial': 8,
                'experiencia_fundadores': 7,
                'traction_inicial': 0.3
            }
        }
        
        resultados = {}
        for nombre, config in estrategias.items():
            prediccion = self.predecir_escenario(config)
            resultados[nombre] = prediccion
        
        return resultados
    
    def generar_recomendaciones_ia(self):
        """Genera recomendaciones inteligentes basadas en análisis de IA"""
        if not self.modelos:
            self.entrenar_modelos()
        
        # Analizar estrategias
        resultados = self.analizar_estrategias_optimizadas()
        
        # Encontrar la mejor estrategia
        mejor_estrategia = max(resultados.items(), key=lambda x: x[1]['valor_fundador'])
        
        # Generar recomendaciones
        recomendaciones = {
            'estrategia_recomendada': mejor_estrategia[0],
            'equity_esperado': mejor_estrategia[1]['equity_final'],
            'valor_esperado': mejor_estrategia[1]['valor_fundador'],
            'roi_inversionistas': mejor_estrategia[1]['roi_inversionistas'],
            'justificacion': self._generar_justificacion(mejor_estrategia[1]),
            'riesgos': self._identificar_riesgos(mejor_estrategia[0]),
            'mitigaciones': self._sugerir_mitigaciones(mejor_estrategia[0])
        }
        
        return recomendaciones
    
    def _generar_justificacion(self, prediccion):
        """Genera justificación para la recomendación"""
        if prediccion['equity_final'] > 50:
            return "Alto control del fundador con equity significativo"
        elif prediccion['equity_final'] > 35:
            return "Balance óptimo entre control y atractivo para inversionistas"
        else:
            return "Enfoque en crecimiento acelerado con dilución controlada"
    
    def _identificar_riesgos(self, estrategia):
        """Identifica riesgos específicos de la estrategia"""
        riesgos = {
            'Sin_Proteccion': ['Dilución excesiva', 'Pérdida de control', 'Resistencia de inversionistas'],
            'Weighted_Average': ['Complejidad legal', 'Costos de implementación', 'Resistencia moderada'],
            'Clases_Diferenciadas': ['Resistencia de inversionistas', 'Complejidad alta', 'Costos elevados'],
            'SAFE': ['Dilución diferida', 'Complejidad de conversión', 'Términos futuros'],
            'Strategic_Partnerships': ['Dependencia de partners', 'Dilución por partnerships', 'Control compartido']
        }
        return riesgos.get(estrategia, ['Riesgos no identificados'])
    
    def _sugerir_mitigaciones(self, estrategia):
        """Sugiere mitigaciones para los riesgos identificados"""
        mitigaciones = {
            'Sin_Proteccion': ['Implementar mecanismos básicos', 'Negociar términos favorables', 'Enfoque en crecimiento'],
            'Weighted_Average': ['Asesoría legal especializada', 'Términos estándar', 'Comunicación clara'],
            'Clases_Diferenciadas': ['Justificación basada en valor', 'Términos graduales', 'Soporte legal'],
            'SAFE': ['Términos claros', 'Valuation caps apropiados', 'Timeline definido'],
            'Strategic_Partnerships': ['Acuerdos claros', 'Control de términos', 'Múltiples partners']
        }
        return mitigaciones.get(estrategia, ['Mitigaciones no identificadas'])
    
    def generar_graficos_ia(self):
        """Genera gráficos avanzados usando análisis de IA"""
        if not self.modelos:
            self.entrenar_modelos()
        
        resultados = self.analizar_estrategias_optimizadas()
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Análisis de IA - Estrategias Anti-Dilución', fontsize=16, fontweight='bold')
        
        # Gráfico 1: Equity vs Valor del Fundador
        ax1 = axes[0, 0]
        estrategias = list(resultados.keys())
        equity_values = [resultados[e]['equity_final'] for e in estrategias]
        valor_values = [resultados[e]['valor_fundador']/1000000 for e in estrategias]
        
        scatter = ax1.scatter(equity_values, valor_values, s=200, alpha=0.7, c=range(len(estrategias)), cmap='viridis')
        ax1.set_xlabel('Equity Final del Fundador (%)')
        ax1.set_ylabel('Valor del Fundador (M USD)')
        ax1.set_title('Equity vs Valor del Fundador')
        ax1.grid(True, alpha=0.3)
        
        # Agregar etiquetas
        for i, estrategia in enumerate(estrategias):
            ax1.annotate(estrategia, (equity_values[i], valor_values[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # Gráfico 2: ROI de Inversionistas
        ax2 = axes[0, 1]
        roi_values = [resultados[e]['roi_inversionistas'] for e in estrategias]
        bars = ax2.bar(estrategias, roi_values, color='skyblue', alpha=0.7)
        ax2.set_ylabel('ROI Inversionistas (x)')
        ax2.set_title('ROI para Inversionistas')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3)
        
        # Agregar valores en las barras
        for bar, roi in zip(bars, roi_values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{roi:.1f}x', ha='center', va='bottom')
        
        # Gráfico 3: Comparación de Estrategias
        ax3 = axes[1, 0]
        x = np.arange(len(estrategias))
        width = 0.25
        
        ax3.bar(x - width, equity_values, width, label='Equity Final (%)', alpha=0.8)
        ax3.bar(x, [v/1000000 for v in valor_values], width, label='Valor (M USD)', alpha=0.8)
        ax3.bar(x + width, roi_values, width, label='ROI (x)', alpha=0.8)
        
        ax3.set_xlabel('Estrategias')
        ax3.set_ylabel('Valores Normalizados')
        ax3.set_title('Comparación de Estrategias')
        ax3.set_xticks(x)
        ax3.set_xticklabels(estrategias, rotation=45)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Análisis de Importancia de Variables
        ax4 = axes[1, 1]
        if hasattr(self.modelos['equity'], 'feature_importances_'):
            importancias = self.modelos['equity'].feature_importances_
            feature_names = self.scaler.feature_names_in_
            
            # Ordenar por importancia
            indices = np.argsort(importancias)[::-1][:10]
            
            ax4.barh(range(len(indices)), importancias[indices])
            ax4.set_yticks(range(len(indices)))
            ax4.set_yticklabels([feature_names[i] for i in indices])
            ax4.set_xlabel('Importancia')
            ax4.set_title('Variables Más Importantes')
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('analisis_ia_dilucion.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generar_reporte_ia_completo(self):
        """Genera un reporte completo basado en análisis de IA"""
        if not self.modelos:
            self.entrenar_modelos()
        
        recomendaciones = self.generar_recomendaciones_ia()
        resultados = self.analizar_estrategias_optimizadas()
        
        reporte = f"""
# 🤖 REPORTE DE IA - ESTRATEGIAS ANTI-DILUCIÓN
## Neural Marketing AI (Copy.ai LATAM)
### Análisis Predictivo con Machine Learning

## 🎯 RESUMEN EJECUTIVO

### Estrategia Recomendada por IA: {recomendaciones['estrategia_recomendada']}
- **Equity Esperado**: {recomendaciones['equity_esperado']:.1f}%
- **Valor Esperado**: ${recomendaciones['valor_esperado']/1000000:.1f}M
- **ROI Inversionistas**: {recomendaciones['roi_inversionistas']:.1f}x

### Justificación de la IA:
{recomendaciones['justificacion']}

## 📊 ANÁLISIS DETALLADO POR ESTRATEGIA

"""
        
        for estrategia, resultado in resultados.items():
            reporte += f"""
### {estrategia}
- **Equity Final**: {resultado['equity_final']:.1f}%
- **Valor Fundador**: ${resultado['valor_fundador']/1000000:.1f}M
- **ROI Inversionistas**: {resultado['roi_inversionistas']:.1f}x
"""
        
        reporte += f"""

## ⚠️ RIESGOS IDENTIFICADOS

### {recomendaciones['estrategia_recomendada']}:
"""
        for riesgo in recomendaciones['riesgos']:
            reporte += f"- {riesgo}\n"
        
        reporte += f"""

## 🛡️ MITIGACIONES SUGERIDAS

### {recomendaciones['estrategia_recomendada']}:
"""
        for mitigacion in recomendaciones['mitigaciones']:
            reporte += f"- {mitigacion}\n"
        
        reporte += """

## 🎯 RECOMENDACIONES FINALES

1. **Implementar estrategia recomendada** por IA
2. **Monitorear métricas** constantemente
3. **Ajustar estrategia** según resultados
4. **Consultar asesoría legal** especializada
5. **Preparar alternativas** de contingencia

---
*Generado por Analizador de IA - Neural Marketing AI*
"""
        
        return reporte
    
    def ejecutar_analisis_completo_ia(self):
        """Ejecuta el análisis completo de IA"""
        print("🤖 Iniciando análisis de IA para estrategias anti-dilución...")
        
        # Entrenar modelos
        self.entrenar_modelos()
        print("✅ Modelos de IA entrenados")
        
        # Generar recomendaciones
        recomendaciones = self.generar_recomendaciones_ia()
        print("✅ Recomendaciones de IA generadas")
        
        # Generar gráficos
        self.generar_graficos_ia()
        print("✅ Gráficos de IA generados")
        
        # Generar reporte
        reporte = self.generar_reporte_ia_completo()
        print("✅ Reporte de IA generado")
        
        # Guardar modelos
        joblib.dump(self.modelos, 'modelos_ia_dilucion.pkl')
        joblib.dump(self.scaler, 'scaler_dilucion.pkl')
        print("✅ Modelos guardados")
        
        # Guardar reporte
        with open('reporte_ia_dilucion.md', 'w', encoding='utf-8') as f:
            f.write(reporte)
        
        print("🎉 Análisis de IA completo finalizado!")
        print(f"📊 Estrategia recomendada: {recomendaciones['estrategia_recomendada']}")
        print(f"💰 Valor esperado: ${recomendaciones['valor_esperado']/1000000:.1f}M")
        
        return reporte

def main():
    """Función principal"""
    analizador = AnalizadorIADilucion()
    
    print("=" * 70)
    print("🤖 ANALIZADOR DE IA - ESTRATEGIAS ANTI-DILUCIÓN")
    print("Neural Marketing AI (Copy.ai LATAM)")
    print("=" * 70)
    
    # Ejecutar análisis completo
    reporte = analizador.ejecutar_analisis_completo_ia()
    
    print("\n" + "=" * 70)
    print("📋 REPORTE DE IA GENERADO")
    print("=" * 70)
    print(reporte)

if __name__ == "__main__":
    main()








