#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE PROYECCIONES FINANCIERAS CON IA PREDICTIVA
Frontier AI Marketing - Sistema Ultra Avanzado
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuración de estilo
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ProyeccionesFinancierasIA:
    """
    Sistema de Proyecciones Financieras con IA Predictiva
    para empresas de IA Marketing como Frontier AI
    """
    
    def __init__(self):
        self.modelos_ia = {}
        self.datos_historicos = {}
        self.proyecciones = {}
        self.metricas_ia = {}
        
    def generar_datos_historicos_simulados(self, meses=24):
        """Genera datos históricos simulados para entrenamiento"""
        fechas = pd.date_range(start='2022-01-01', periods=meses, freq='M')
        
        # Simulación de crecimiento exponencial con variaciones
        np.random.seed(42)
        base_revenue = 50000
        growth_rate = 0.15
        
        datos = {
            'fecha': fechas,
            'ingresos_saas': [],
            'ingresos_cursos': [],
            'usuarios_activos': [],
            'churn_rate': [],
            'cac': [],
            'ltv': [],
            'mrr': [],
            'arr': [],
            'ai_accuracy': [],
            'content_generation_speed': [],
            'api_calls': [],
            'customer_satisfaction': []
        }
        
        for i in range(meses):
            # Crecimiento con variaciones estacionales
            seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * i / 12)
            growth_factor = (1 + growth_rate) ** (i / 12)
            noise = np.random.normal(1, 0.05)
            
            # Ingresos SaaS
            saas_revenue = base_revenue * growth_factor * seasonal_factor * noise
            datos['ingresos_saas'].append(saas_revenue)
            
            # Ingresos Cursos (más estacionales)
            course_revenue = base_revenue * 0.3 * growth_factor * seasonal_factor * noise * (1 + 0.2 * np.sin(2 * np.pi * i / 6))
            datos['ingresos_cursos'].append(course_revenue)
            
            # Usuarios activos
            usuarios = 1000 * growth_factor * seasonal_factor * noise
            datos['usuarios_activos'].append(int(usuarios))
            
            # Métricas de negocio
            datos['churn_rate'].append(max(0.02, 0.05 - 0.001 * i + np.random.normal(0, 0.005)))
            datos['cac'].append(150 + np.random.normal(0, 20))
            datos['ltv'].append(2500 + np.random.normal(0, 200))
            datos['mrr'].append(saas_revenue / 12)
            datos['arr'].append(saas_revenue)
            
            # Métricas de IA
            datos['ai_accuracy'].append(min(0.98, 0.85 + 0.001 * i + np.random.normal(0, 0.01)))
            datos['content_generation_speed'].append(2.5 + 0.1 * i + np.random.normal(0, 0.2))
            datos['api_calls'].append(int(100000 * growth_factor * seasonal_factor * noise))
            datos['customer_satisfaction'].append(min(5.0, 4.2 + 0.01 * i + np.random.normal(0, 0.1)))
        
        self.datos_historicos = pd.DataFrame(datos)
        return self.datos_historicos
    
    def entrenar_modelos_ia(self):
        """Entrena modelos de IA para predicciones"""
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
        from sklearn.linear_model import Ridge
        from sklearn.svm import SVR
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import train_test_split
        
        # Preparar datos para entrenamiento
        X = self.datos_historicos[['usuarios_activos', 'churn_rate', 'cac', 'ltv', 
                                  'ai_accuracy', 'content_generation_speed', 'api_calls', 
                                  'customer_satisfaction']].values
        
        # Entrenar modelos para diferentes métricas
        metricas = ['ingresos_saas', 'ingresos_cursos', 'mrr', 'arr']
        
        for metrica in metricas:
            y = self.datos_historicos[metrica].values
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Escalar datos
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Entrenar múltiples modelos
            modelos = {
                'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
                'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'Ridge': Ridge(alpha=1.0),
                'SVR': SVR(kernel='rbf', C=1.0, gamma='scale')
            }
            
            mejores_modelos = {}
            for nombre, modelo in modelos.items():
                if nombre == 'SVR':
                    modelo.fit(X_train_scaled, y_train)
                    score = modelo.score(X_test_scaled, y_test)
                else:
                    modelo.fit(X_train, y_train)
                    score = modelo.score(X_test, y_test)
                
                mejores_modelos[nombre] = {
                    'modelo': modelo,
                    'score': score,
                    'scaler': scaler if nombre == 'SVR' else None
                }
            
            # Seleccionar mejor modelo
            mejor_modelo = max(mejores_modelos.items(), key=lambda x: x[1]['score'])
            self.modelos_ia[metrica] = mejor_modelo[1]
            
            print(f"Mejor modelo para {metrica}: {mejor_modelo[0]} (Score: {mejor_modelo[1]['score']:.4f})")
    
    def generar_proyecciones(self, meses_futuro=12):
        """Genera proyecciones futuras usando IA"""
        if not self.modelos_ia:
            print("Primero debe entrenar los modelos de IA")
            return None
        
        # Generar fechas futuras
        ultima_fecha = self.datos_historicos['fecha'].max()
        fechas_futuro = pd.date_range(start=ultima_fecha + timedelta(days=1), 
                                    periods=meses_futuro, freq='M')
        
        # Proyecciones base (tendencia)
        ultimos_datos = self.datos_historicos.iloc[-1]
        
        proyecciones = {
            'fecha': fechas_futuro,
            'ingresos_saas': [],
            'ingresos_cursos': [],
            'mrr': [],
            'arr': [],
            'usuarios_activos': [],
            'churn_rate': [],
            'cac': [],
            'ltv': [],
            'ai_accuracy': [],
            'content_generation_speed': [],
            'api_calls': [],
            'customer_satisfaction': []
        }
        
        # Proyecciones usando IA
        for i in range(meses_futuro):
            # Calcular valores base para predicción
            growth_factor = 1.15 ** ((i + 1) / 12)  # 15% anual
            seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * (i + 24) / 12)
            
            # Usuarios activos (crecimiento exponencial)
            usuarios_futuro = ultimos_datos['usuarios_activos'] * growth_factor * seasonal_factor
            proyecciones['usuarios_activos'].append(int(usuarios_futuro))
            
            # Churn rate (mejora con el tiempo)
            churn_futuro = max(0.01, ultimos_datos['churn_rate'] - 0.001 * (i + 1))
            proyecciones['churn_rate'].append(churn_futuro)
            
            # CAC (optimización)
            cac_futuro = max(100, ultimos_datos['cac'] - 2 * (i + 1))
            proyecciones['cac'].append(cac_futuro)
            
            # LTV (mejora)
            ltv_futuro = ultimos_datos['ltv'] + 50 * (i + 1)
            proyecciones['ltv'].append(ltv_futuro)
            
            # Métricas de IA (mejora continua)
            ai_accuracy_futuro = min(0.99, ultimos_datos['ai_accuracy'] + 0.001 * (i + 1))
            proyecciones['ai_accuracy'].append(ai_accuracy_futuro)
            
            content_speed_futuro = ultimos_datos['content_generation_speed'] + 0.1 * (i + 1)
            proyecciones['content_generation_speed'].append(content_speed_futuro)
            
            api_calls_futuro = int(ultimos_datos['api_calls'] * growth_factor * seasonal_factor)
            proyecciones['api_calls'].append(api_calls_futuro)
            
            customer_sat_futuro = min(5.0, ultimos_datos['customer_satisfaction'] + 0.01 * (i + 1))
            proyecciones['customer_satisfaction'].append(customer_sat_futuro)
            
            # Preparar datos para predicción de ingresos
            X_pred = np.array([[
                usuarios_futuro, churn_futuro, cac_futuro, ltv_futuro,
                ai_accuracy_futuro, content_speed_futuro, api_calls_futuro, customer_sat_futuro
            ]])
            
            # Predicciones usando modelos entrenados
            for metrica in ['ingresos_saas', 'ingresos_cursos', 'mrr', 'arr']:
                modelo_info = self.modelos_ia[metrica]
                modelo = modelo_info['modelo']
                scaler = modelo_info['scaler']
                
                if scaler:
                    X_pred_scaled = scaler.transform(X_pred)
                    prediccion = modelo.predict(X_pred_scaled)[0]
                else:
                    prediccion = modelo.predict(X_pred)[0]
                
                proyecciones[metrica].append(max(0, prediccion))
        
        self.proyecciones = pd.DataFrame(proyecciones)
        return self.proyecciones
    
    def analizar_escenarios(self):
        """Analiza diferentes escenarios de crecimiento"""
        escenarios = {
            'Optimista': {'growth_rate': 1.25, 'churn_reduction': 0.002, 'ai_improvement': 0.002},
            'Base': {'growth_rate': 1.15, 'churn_reduction': 0.001, 'ai_improvement': 0.001},
            'Conservador': {'growth_rate': 1.08, 'churn_reduction': 0.0005, 'ai_improvement': 0.0005},
            'Pesimista': {'growth_rate': 1.05, 'churn_reduction': 0.0002, 'ai_improvement': 0.0002}
        }
        
        resultados_escenarios = {}
        
        for nombre, params in escenarios.items():
            # Simular proyecciones con diferentes parámetros
            ultimos_datos = self.datos_historicos.iloc[-1]
            
            escenario_data = {
                'ingresos_saas_12m': ultimos_datos['ingresos_saas'] * (params['growth_rate'] ** 1),
                'ingresos_cursos_12m': ultimos_datos['ingresos_cursos'] * (params['growth_rate'] ** 1),
                'usuarios_12m': int(ultimos_datos['usuarios_activos'] * (params['growth_rate'] ** 1)),
                'churn_12m': max(0.005, ultimos_datos['churn_rate'] - params['churn_reduction'] * 12),
                'ai_accuracy_12m': min(0.99, ultimos_datos['ai_accuracy'] + params['ai_improvement'] * 12),
                'ltv_12m': ultimos_datos['ltv'] + 50 * 12,
                'cac_12m': max(80, ultimos_datos['cac'] - 2 * 12)
            }
            
            # Calcular métricas derivadas
            escenario_data['arr_12m'] = escenario_data['ingresos_saas_12m']
            escenario_data['mrr_12m'] = escenario_data['arr_12m'] / 12
            escenario_data['ltv_cac_ratio'] = escenario_data['ltv_12m'] / escenario_data['cac_12m']
            escenario_data['payback_period'] = escenario_data['cac_12m'] / (escenario_data['mrr_12m'] * 0.7)  # 70% gross margin
            
            resultados_escenarios[nombre] = escenario_data
        
        return resultados_escenarios
    
    def calcular_valuacion_proyectada(self, multiples_mercado=None):
        """Calcula valuación proyectada usando múltiples métodos"""
        if multiples_mercado is None:
            multiples_mercado = {
                'saas_revenue': 15,  # 15x ARR
                'total_revenue': 12,  # 12x Total Revenue
                'users': 2000,  # $2000 por usuario
                'ai_accuracy': 1000000  # $1M por punto de accuracy
            }
        
        ultimos_datos = self.datos_historicos.iloc[-1]
        proyecciones_12m = self.proyecciones.iloc[-1] if not self.proyecciones.empty else ultimos_datos
        
        # Método 1: Múltiplo de ARR
        valuacion_arr = proyecciones_12m['arr'] * multiples_mercado['saas_revenue']
        
        # Método 2: Múltiplo de Revenue Total
        revenue_total = proyecciones_12m['ingresos_saas'] + proyecciones_12m['ingresos_cursos']
        valuacion_revenue = revenue_total * multiples_mercado['total_revenue']
        
        # Método 3: Múltiplo de Usuarios
        valuacion_usuarios = proyecciones_12m['usuarios_activos'] * multiples_mercado['users']
        
        # Método 4: Múltiplo de IA Accuracy
        valuacion_ia = proyecciones_12m['ai_accuracy'] * multiples_mercado['ai_accuracy']
        
        # Promedio ponderado
        valuacion_promedio = (valuacion_arr * 0.4 + valuacion_revenue * 0.3 + 
                             valuacion_usuarios * 0.2 + valuacion_ia * 0.1)
        
        return {
            'valuacion_arr': valuacion_arr,
            'valuacion_revenue': valuacion_revenue,
            'valuacion_usuarios': valuacion_usuarios,
            'valuacion_ia': valuacion_ia,
            'valuacion_promedio': valuacion_promedio,
            'multiples_usados': multiples_mercado
        }
    
    def generar_reporte_ejecutivo(self):
        """Genera reporte ejecutivo completo"""
        if self.proyecciones.empty:
            print("Primero debe generar las proyecciones")
            return None
        
        # Análisis de escenarios
        escenarios = self.analizar_escenarios()
        
        # Valuación proyectada
        valuacion = self.calcular_valuacion_proyectada()
        
        # Métricas clave
        ultimos_datos = self.datos_historicos.iloc[-1]
        proyecciones_12m = self.proyecciones.iloc[-1]
        
        reporte = {
            'resumen_ejecutivo': {
                'fecha_analisis': datetime.now().strftime('%Y-%m-%d'),
                'empresa': 'Frontier AI Marketing',
                'modelo_negocio': 'AI Course + SaaS Marketing Platform',
                'valuacion_proyectada': valuacion['valuacion_promedio'],
                'crecimiento_anual_proyectado': ((proyecciones_12m['ingresos_saas'] / ultimos_datos['ingresos_saas']) - 1) * 100
            },
            'metricas_actuales': {
                'arr_actual': ultimos_datos['arr'],
                'mrr_actual': ultimos_datos['mrr'],
                'usuarios_activos': ultimos_datos['usuarios_activos'],
                'churn_rate': ultimos_datos['churn_rate'],
                'ltv': ultimos_datos['ltv'],
                'cac': ultimos_datos['cac'],
                'ai_accuracy': ultimos_datos['ai_accuracy']
            },
            'proyecciones_12_meses': {
                'arr_proyectado': proyecciones_12m['arr'],
                'mrr_proyectado': proyecciones_12m['mrr'],
                'usuarios_proyectados': proyecciones_12m['usuarios_activos'],
                'churn_proyectado': proyecciones_12m['churn_rate'],
                'ltv_proyectado': proyecciones_12m['ltv'],
                'cac_proyectado': proyecciones_12m['cac'],
                'ai_accuracy_proyectada': proyecciones_12m['ai_accuracy']
            },
            'escenarios': escenarios,
            'valuacion': valuacion,
            'recomendaciones': [
                'Mantener crecimiento de usuarios >15% anual',
                'Reducir churn rate a <2%',
                'Optimizar CAC manteniendo LTV/CAC >3',
                'Mejorar AI accuracy a >95%',
                'Expandir modelo de cursos para diversificar ingresos'
            ]
        }
        
        return reporte
    
    def visualizar_proyecciones(self):
        """Crea visualizaciones de las proyecciones"""
        if self.proyecciones.empty:
            print("Primero debe generar las proyecciones")
            return None
        
        # Combinar datos históricos y proyecciones
        datos_completos = pd.concat([self.datos_historicos, self.proyecciones], ignore_index=True)
        
        # Crear figura con subplots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Proyecciones Financieras con IA - Frontier AI Marketing', fontsize=16, fontweight='bold')
        
        # 1. Ingresos SaaS
        axes[0, 0].plot(datos_completos['fecha'], datos_completos['ingresos_saas'], 
                       label='Histórico', color='blue', linewidth=2)
        axes[0, 0].axvline(x=self.datos_historicos['fecha'].max(), color='red', linestyle='--', alpha=0.7)
        axes[0, 0].set_title('Ingresos SaaS (ARR)')
        axes[0, 0].set_ylabel('Ingresos ($)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Ingresos Cursos
        axes[0, 1].plot(datos_completos['fecha'], datos_completos['ingresos_cursos'], 
                       label='Histórico', color='green', linewidth=2)
        axes[0, 1].axvline(x=self.datos_historicos['fecha'].max(), color='red', linestyle='--', alpha=0.7)
        axes[0, 1].set_title('Ingresos Cursos')
        axes[0, 1].set_ylabel('Ingresos ($)')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Usuarios Activos
        axes[0, 2].plot(datos_completos['fecha'], datos_completos['usuarios_activos'], 
                       label='Histórico', color='purple', linewidth=2)
        axes[0, 2].axvline(x=self.datos_historicos['fecha'].max(), color='red', linestyle='--', alpha=0.7)
        axes[0, 2].set_title('Usuarios Activos')
        axes[0, 2].set_ylabel('Usuarios')
        axes[0, 2].legend()
        axes[0, 2].grid(True, alpha=0.3)
        
        # 4. Churn Rate
        axes[1, 0].plot(datos_completos['fecha'], datos_completos['churn_rate'] * 100, 
                       label='Histórico', color='orange', linewidth=2)
        axes[1, 0].axvline(x=self.datos_historicos['fecha'].max(), color='red', linestyle='--', alpha=0.7)
        axes[1, 0].set_title('Churn Rate')
        axes[1, 0].set_ylabel('Churn Rate (%)')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 5. AI Accuracy
        axes[1, 1].plot(datos_completos['fecha'], datos_completos['ai_accuracy'] * 100, 
                       label='Histórico', color='red', linewidth=2)
        axes[1, 1].axvline(x=self.datos_historicos['fecha'].max(), color='red', linestyle='--', alpha=0.7)
        axes[1, 1].set_title('AI Accuracy')
        axes[1, 1].set_ylabel('Accuracy (%)')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        # 6. LTV vs CAC
        axes[1, 2].plot(datos_completos['fecha'], datos_completos['ltv'], 
                       label='LTV', color='blue', linewidth=2)
        axes[1, 2].plot(datos_completos['fecha'], datos_completos['cac'], 
                       label='CAC', color='red', linewidth=2)
        axes[1, 2].axvline(x=self.datos_historicos['fecha'].max(), color='red', linestyle='--', alpha=0.7)
        axes[1, 2].set_title('LTV vs CAC')
        axes[1, 2].set_ylabel('Valor ($)')
        axes[1, 2].legend()
        axes[1, 2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        return fig

def main():
    """Función principal para demostrar el sistema"""
    print("🚀 SISTEMA DE PROYECCIONES FINANCIERAS CON IA PREDICTIVA")
    print("=" * 60)
    
    # Inicializar sistema
    sistema = ProyeccionesFinancierasIA()
    
    # Generar datos históricos
    print("\n📊 Generando datos históricos simulados...")
    datos_historicos = sistema.generar_datos_historicos_simulados()
    print(f"✅ Datos históricos generados: {len(datos_historicos)} meses")
    
    # Entrenar modelos de IA
    print("\n🤖 Entrenando modelos de IA...")
    sistema.entrenar_modelos_ia()
    print("✅ Modelos de IA entrenados exitosamente")
    
    # Generar proyecciones
    print("\n🔮 Generando proyecciones futuras...")
    proyecciones = sistema.generar_proyecciones(meses_futuro=12)
    print(f"✅ Proyecciones generadas: {len(proyecciones)} meses")
    
    # Analizar escenarios
    print("\n📈 Analizando escenarios...")
    escenarios = sistema.analizar_escenarios()
    print("✅ Escenarios analizados")
    
    # Calcular valuación
    print("\n💰 Calculando valuación proyectada...")
    valuacion = sistema.calcular_valuacion_proyectada()
    print("✅ Valuación calculada")
    
    # Generar reporte ejecutivo
    print("\n📋 Generando reporte ejecutivo...")
    reporte = sistema.generar_reporte_ejecutivo()
    print("✅ Reporte ejecutivo generado")
    
    # Mostrar resultados clave
    print("\n" + "=" * 60)
    print("📊 RESULTADOS CLAVE")
    print("=" * 60)
    
    print(f"\n💰 VALUACIÓN PROYECTADA: ${valuacion['valuacion_promedio']:,.0f}")
    print(f"📈 CRECIMIENTO ANUAL: {reporte['resumen_ejecutivo']['crecimiento_anual_proyectado']:.1f}%")
    print(f"👥 USUARIOS ACTUALES: {reporte['metricas_actuales']['usuarios_activos']:,}")
    print(f"🎯 AI ACCURACY: {reporte['metricas_actuales']['ai_accuracy']:.1%}")
    
    print(f"\n📊 PROYECCIONES 12 MESES:")
    print(f"   • ARR: ${reporte['proyecciones_12_meses']['arr_proyectado']:,.0f}")
    print(f"   • Usuarios: {reporte['proyecciones_12_meses']['usuarios_proyectados']:,}")
    print(f"   • Churn Rate: {reporte['proyecciones_12_meses']['churn_proyectado']:.1%}")
    print(f"   • LTV: ${reporte['proyecciones_12_meses']['ltv_proyectado']:,.0f}")
    
    print(f"\n🎯 ESCENARIOS:")
    for nombre, datos in escenarios.items():
        print(f"   • {nombre}: ARR ${datos['ingresos_saas_12m']:,.0f}, Usuarios {datos['usuarios_12m']:,}")
    
    print(f"\n💡 RECOMENDACIONES:")
    for i, rec in enumerate(reporte['recomendaciones'], 1):
        print(f"   {i}. {rec}")
    
    # Crear visualizaciones
    print(f"\n📊 Creando visualizaciones...")
    sistema.visualizar_proyecciones()
    print("✅ Visualizaciones creadas")
    
    print(f"\n🎉 SISTEMA COMPLETADO EXITOSAMENTE!")
    print("=" * 60)

if __name__ == "__main__":
    main()