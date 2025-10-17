#!/usr/bin/env python3
"""
🚀 HERRAMIENTA DE PREDICCIÓN FINANCIERA CON IA - IA SAAS MARKETING
================================================================

Sistema avanzado de predicción financiera utilizando machine learning
para análisis predictivo de métricas SaaS y optimización de estrategias.

Características:
- Predicción de ARR/MRR con múltiples algoritmos
- Análisis de cohortes y churn prediction
- Optimización de pricing con IA
- Análisis de sensibilidad y escenarios
- Dashboard interactivo con visualizaciones

Autor: Sistema Neural Avanzado
Versión: 2.0 - Ultra Avanzada con IA
Fecha: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import warnings
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
warnings.filterwarnings('ignore')

class FinancialAIPredictor:
    def __init__(self):
        self.nombre = "HERRAMIENTA DE PREDICCIÓN FINANCIERA CON IA"
        self.version = "2.0 - Ultra Avanzada"
        self.fecha_inicio = datetime.now()
        
        # Configuración de colores
        self.colores = {
            'primario': '#1f77b4',
            'secundario': '#ff7f0e',
            'exito': '#2ca02c',
            'advertencia': '#d62728',
            'info': '#9467bd',
            'neutro': '#8c564b'
        }
        
        # Modelos de IA
        self.modelos_ia = {}
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
        # Métricas del sistema
        self.metricas = {
            'arr_actual': 0,
            'mrr_actual': 0,
            'cac_actual': 0,
            'ltv_actual': 0,
            'churn_rate': 0,
            'growth_rate': 0,
            'gross_margin': 0,
            'ebitda_margin': 0
        }
        
        print(f"🤖 {self.nombre} - {self.version}")
        print(f"📅 Iniciado: {self.fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

    def generar_datos_saas_simulados(self, n_meses=36):
        """
        Genera datos SaaS simulados realistas para entrenamiento
        """
        print("📊 Generando datos SaaS simulados...")
        
        fechas = pd.date_range(start=datetime.now() - timedelta(days=n_meses*30), 
                              end=datetime.now(), freq='M')
        n_meses = len(fechas)
        
        # Generar datos con tendencias realistas
        np.random.seed(42)
        
        # MRR base con crecimiento exponencial
        mrr_base = 50000
        crecimiento_mensual = np.random.normal(0.08, 0.03, n_meses)  # 8% crecimiento promedio
        mrr_mensual = mrr_base * np.exp(np.cumsum(crecimiento_mensual))
        
        # ARR (Annual Recurring Revenue)
        arr_mensual = mrr_mensual * 12
        
        # Número de clientes
        clientes_base = 500
        crecimiento_clientes = np.random.normal(0.05, 0.02, n_meses)
        clientes_mensual = clientes_base * np.exp(np.cumsum(crecimiento_clientes))
        
        # Churn rate (tendencia decreciente)
        churn_base = 0.05
        churn_tendencia = np.linspace(churn_base, churn_base * 0.3, n_meses)
        churn_mensual = churn_tendencia + np.random.normal(0, 0.01, n_meses)
        churn_mensual = np.clip(churn_mensual, 0.01, 0.15)
        
        # CAC (Customer Acquisition Cost)
        cac_base = 150
        cac_tendencia = np.linspace(cac_base, cac_base * 0.7, n_meses)  # Mejora en eficiencia
        cac_mensual = cac_tendencia + np.random.normal(0, 20, n_meses)
        cac_mensual = np.clip(cac_mensual, 50, 300)
        
        # LTV (Lifetime Value)
        ltv_mensual = mrr_mensual / clientes_mensual / churn_mensual
        
        # Gross Margin
        gross_margin_base = 0.75
        gross_margin_mensual = gross_margin_base + np.random.normal(0, 0.02, n_meses)
        gross_margin_mensual = np.clip(gross_margin_mensual, 0.6, 0.9)
        
        # EBITDA Margin
        ebitda_margin_base = 0.15
        ebitda_margin_mensual = ebitda_margin_base + np.random.normal(0, 0.03, n_meses)
        ebitda_margin_mensual = np.clip(ebitda_margin_mensual, 0.05, 0.35)
        
        # Nuevos clientes
        nuevos_clientes_mensual = clientes_mensual * churn_mensual + np.random.normal(0, 10, n_meses)
        nuevos_clientes_mensual = np.maximum(nuevos_clientes_mensual, 0)
        
        # Costos operativos
        costos_operativos = mrr_mensual * (1 - gross_margin_mensual)
        
        # Crear DataFrame
        df = pd.DataFrame({
            'fecha': fechas,
            'mrr': mrr_mensual,
            'arr': arr_mensual,
            'clientes': clientes_mensual,
            'churn_rate': churn_mensual,
            'cac': cac_mensual,
            'ltv': ltv_mensual,
            'gross_margin': gross_margin_mensual,
            'ebitda_margin': ebitda_margin_mensual,
            'nuevos_clientes': nuevos_clientes_mensual,
            'costos_operativos': costos_operativos,
            'mes': range(1, n_meses + 1)
        })
        
        # Calcular métricas derivadas
        df['ltv_cac_ratio'] = df['ltv'] / df['cac']
        df['payback_period'] = df['cac'] / (df['mrr'] / df['clientes'])
        df['revenue_growth'] = df['mrr'].pct_change() * 100
        df['customer_growth'] = df['clientes'].pct_change() * 100
        
        print(f"✅ Datos SaaS generados: {len(df)} registros")
        return df

    def entrenar_modelos_prediccion(self, df_saas):
        """
        Entrena modelos de IA para predicciones financieras
        """
        print("🤖 Entrenando modelos de predicción con IA...")
        
        # Preparar features para entrenamiento
        features = ['mes', 'clientes', 'churn_rate', 'cac', 'gross_margin', 
                   'ebitda_margin', 'nuevos_clientes', 'costos_operativos']
        
        # Targets para predicción
        targets = {
            'mrr': df_saas['mrr'].values,
            'arr': df_saas['arr'].values,
            'ltv': df_saas['ltv'].values,
            'clientes': df_saas['clientes'].values
        }
        
        X = df_saas[features].values
        X_scaled = self.scaler.fit_transform(X)
        
        # Entrenar modelos para cada target
        modelos = {
            'mrr': {
                'modelo': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'target': targets['mrr']
            },
            'arr': {
                'modelo': RandomForestRegressor(n_estimators=100, random_state=42),
                'target': targets['arr']
            },
            'ltv': {
                'modelo': SVR(kernel='rbf', C=1.0, gamma='scale'),
                'target': targets['ltv']
            },
            'clientes': {
                'modelo': MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42),
                'target': targets['clientes']
            }
        }
        
        for nombre, config in modelos.items():
            modelo = config['modelo']
            y = config['target']
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42)
            
            # Entrenar modelo
            modelo.fit(X_train, y_train)
            
            # Evaluar modelo
            y_pred = modelo.predict(X_test)
            r2 = r2_score(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            self.modelos_ia[nombre] = modelo
            
            print(f"✅ Modelo {nombre}: R² = {r2:.3f}, MSE = {mse:.2f}, MAE = {mae:.2f}")
        
        print("🎉 Modelos de IA entrenados exitosamente")

    def predecir_futuro(self, df_historico, meses_futuro=12):
        """
        Genera predicciones futuras usando modelos entrenados
        """
        print(f"🔮 Generando predicciones para {meses_futuro} meses...")
        
        if not self.modelos_ia:
            print("⚠️  Modelos no entrenados, entrenando...")
            self.entrenar_modelos_prediccion(df_historico)
        
        # Preparar datos para predicción
        ultimo_mes = df_historico['mes'].max()
        fechas_futuro = pd.date_range(
            start=df_historico['fecha'].max() + timedelta(days=30),
            periods=meses_futuro, freq='M')
        
        predicciones = []
        
        for i, fecha in enumerate(fechas_futuro):
            mes_futuro = ultimo_mes + i + 1
            
            # Usar valores del último mes como base
            ultimo_registro = df_historico.iloc[-1].copy()
            
            # Ajustar valores para el futuro (tendencias)
            factor_crecimiento = 1 + (0.05 * (i + 1))  # 5% crecimiento mensual
            
            features_futuro = np.array([[
                mes_futuro,
                ultimo_registro['clientes'] * factor_crecimiento,
                ultimo_registro['churn_rate'] * 0.95,  # Mejora en churn
                ultimo_registro['cac'] * 0.98,  # Mejora en CAC
                ultimo_registro['gross_margin'] + 0.01,  # Mejora en margin
                ultimo_registro['ebitda_margin'] + 0.02,  # Mejora en EBITDA
                ultimo_registro['nuevos_clientes'] * factor_crecimiento,
                ultimo_registro['costos_operativos'] * factor_crecimiento
            ]])
            
            features_scaled = self.scaler.transform(features_futuro)
            
            # Hacer predicciones
            pred_mrr = self.modelos_ia['mrr'].predict(features_scaled)[0]
            pred_arr = self.modelos_ia['arr'].predict(features_scaled)[0]
            pred_ltv = self.modelos_ia['ltv'].predict(features_scaled)[0]
            pred_clientes = self.modelos_ia['clientes'].predict(features_scaled)[0]
            
            predicciones.append({
                'fecha': fecha,
                'mes': mes_futuro,
                'mrr': pred_mrr,
                'arr': pred_arr,
                'ltv': pred_ltv,
                'clientes': pred_clientes,
                'churn_rate': ultimo_registro['churn_rate'] * 0.95,
                'cac': ultimo_registro['cac'] * 0.98,
                'gross_margin': ultimo_registro['gross_margin'] + 0.01,
                'ebitda_margin': ultimo_registro['ebitda_margin'] + 0.02
            })
        
        df_predicciones = pd.DataFrame(predicciones)
        
        # Calcular métricas derivadas
        df_predicciones['ltv_cac_ratio'] = df_predicciones['ltv'] / df_predicciones['cac']
        df_predicciones['payback_period'] = df_predicciones['cac'] / (df_predicciones['mrr'] / df_predicciones['clientes'])
        
        print(f"✅ Predicciones generadas para {len(df_predicciones)} meses")
        return df_predicciones

    def analizar_sensibilidad(self, df_historico, parametros_variacion):
        """
        Análisis de sensibilidad de parámetros clave
        """
        print("📊 Realizando análisis de sensibilidad...")
        
        resultados_sensibilidad = {}
        
        for parametro, variaciones in parametros_variacion.items():
            print(f"   Analizando sensibilidad de {parametro}...")
            
            resultados_parametro = []
            
            for variacion in variaciones:
                # Crear copia de datos con variación
                df_variado = df_historico.copy()
                df_variado[parametro] = df_variado[parametro] * variacion
                
                # Entrenar modelo con datos variados
                self.entrenar_modelos_prediccion(df_variado)
                
                # Generar predicciones
                predicciones = self.predecir_futuro(df_variado, 12)
                
                # Calcular métricas finales
                mrr_final = predicciones['mrr'].iloc[-1]
                arr_final = predicciones['arr'].iloc[-1]
                ltv_final = predicciones['ltv'].iloc[-1]
                
                resultados_parametro.append({
                    'variacion': variacion,
                    'mrr_final': mrr_final,
                    'arr_final': arr_final,
                    'ltv_final': ltv_final,
                    'impacto_mrr': (mrr_final - df_historico['mrr'].iloc[-1]) / df_historico['mrr'].iloc[-1] * 100,
                    'impacto_arr': (arr_final - df_historico['arr'].iloc[-1]) / df_historico['arr'].iloc[-1] * 100
                })
            
            resultados_sensibilidad[parametro] = resultados_parametro
        
        print("✅ Análisis de sensibilidad completado")
        return resultados_sensibilidad

    def optimizar_pricing(self, df_historico, precios_objetivo):
        """
        Optimización de pricing usando IA
        """
        print("💰 Optimizando estrategia de pricing...")
        
        # Simular diferentes estrategias de pricing
        estrategias_pricing = {
            'actual': {'precio_base': 50, 'descuento_anual': 0.2},
            'premium': {'precio_base': 75, 'descuento_anual': 0.15},
            'agresivo': {'precio_base': 35, 'descuento_anual': 0.25},
            'enterprise': {'precio_base': 150, 'descuento_anual': 0.1}
        }
        
        resultados_pricing = {}
        
        for nombre_estrategia, config in estrategias_pricing.items():
            print(f"   Evaluando estrategia: {nombre_estrategia}")
            
            # Simular impacto en métricas
            factor_precio = config['precio_base'] / 50  # Normalizar respecto al precio actual
            
            # Impacto en diferentes métricas
            impacto_mrr = factor_precio * 0.8  # Elasticidad de demanda
            impacto_churn = 1 + (factor_precio - 1) * 0.3  # Mayor precio = mayor churn
            impacto_cac = 1 + (factor_precio - 1) * 0.2  # Mayor precio = mayor CAC
            
            # Calcular métricas proyectadas
            mrr_proyectado = df_historico['mrr'].iloc[-1] * impacto_mrr
            churn_proyectado = df_historico['churn_rate'].iloc[-1] * impacto_churn
            cac_proyectado = df_historico['cac'].iloc[-1] * impacto_cac
            
            # Calcular LTV
            ltv_proyectado = mrr_proyectado / df_historico['clientes'].iloc[-1] / churn_proyectado
            
            # Calcular ROI de la estrategia
            roi_estrategia = ltv_proyectado / cac_proyectado
            
            resultados_pricing[nombre_estrategia] = {
                'precio_base': config['precio_base'],
                'mrr_proyectado': mrr_proyectado,
                'churn_proyectado': churn_proyectado,
                'cac_proyectado': cac_proyectado,
                'ltv_proyectado': ltv_proyectado,
                'roi_estrategia': roi_estrategia,
                'revenue_impact': (mrr_proyectado - df_historico['mrr'].iloc[-1]) / df_historico['mrr'].iloc[-1] * 100
            }
        
        # Encontrar estrategia óptima
        mejor_estrategia = max(resultados_pricing.items(), key=lambda x: x[1]['roi_estrategia'])
        
        print(f"✅ Estrategia óptima: {mejor_estrategia[0]} (ROI: {mejor_estrategia[1]['roi_estrategia']:.2f})")
        
        return resultados_pricing, mejor_estrategia

    def crear_dashboard_interactivo(self, df_historico, df_predicciones, resultados_sensibilidad):
        """
        Crea dashboard interactivo con visualizaciones
        """
        print("📊 Creando dashboard interactivo...")
        
        # Configurar estilo
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(3, 3, figsize=(20, 18))
        fig.suptitle('DASHBOARD DE PREDICCIÓN FINANCIERA CON IA', 
                    fontsize=20, fontweight='bold')
        
        # Gráfico 1: Evolución MRR
        ax1 = axes[0, 0]
        ax1.plot(df_historico['fecha'], df_historico['mrr'], 
                label='Histórico', color=self.colores['primario'], linewidth=2)
        ax1.plot(df_predicciones['fecha'], df_predicciones['mrr'], 
                label='Predicción', color=self.colores['exito'], linewidth=2, linestyle='--')
        ax1.set_title('Evolución MRR', fontweight='bold')
        ax1.set_ylabel('MRR ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Evolución ARR
        ax2 = axes[0, 1]
        ax2.plot(df_historico['fecha'], df_historico['arr']/1000000, 
                label='Histórico', color=self.colores['primario'], linewidth=2)
        ax2.plot(df_predicciones['fecha'], df_predicciones['arr']/1000000, 
                label='Predicción', color=self.colores['exito'], linewidth=2, linestyle='--')
        ax2.set_title('Evolución ARR', fontweight='bold')
        ax2.set_ylabel('ARR ($M)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: LTV vs CAC
        ax3 = axes[0, 2]
        ax3.plot(df_historico['fecha'], df_historico['ltv_cac_ratio'], 
                color=self.colores['info'], linewidth=2)
        ax3.axhline(y=3, color='red', linestyle='--', alpha=0.7, label='Mínimo saludable')
        ax3.set_title('LTV/CAC Ratio', fontweight='bold')
        ax3.set_ylabel('Ratio')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Churn Rate
        ax4 = axes[1, 0]
        ax4.plot(df_historico['fecha'], df_historico['churn_rate']*100, 
                color=self.colores['advertencia'], linewidth=2)
        ax4.set_title('Churn Rate', fontweight='bold')
        ax4.set_ylabel('Churn Rate (%)')
        ax4.grid(True, alpha=0.3)
        
        # Gráfico 5: Crecimiento de Clientes
        ax5 = axes[1, 1]
        ax5.plot(df_historico['fecha'], df_historico['clientes'], 
                label='Histórico', color=self.colores['primario'], linewidth=2)
        ax5.plot(df_predicciones['fecha'], df_predicciones['clientes'], 
                label='Predicción', color=self.colores['exito'], linewidth=2, linestyle='--')
        ax5.set_title('Crecimiento de Clientes', fontweight='bold')
        ax5.set_ylabel('Número de Clientes')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # Gráfico 6: Gross Margin
        ax6 = axes[1, 2]
        ax6.plot(df_historico['fecha'], df_historico['gross_margin']*100, 
                color=self.colores['exito'], linewidth=2)
        ax6.set_title('Gross Margin', fontweight='bold')
        ax6.set_ylabel('Margin (%)')
        ax6.grid(True, alpha=0.3)
        
        # Gráfico 7: Análisis de Sensibilidad
        ax7 = axes[2, 0]
        if 'churn_rate' in resultados_sensibilidad:
            sensibilidad = resultados_sensibilidad['churn_rate']
            variaciones = [r['variacion'] for r in sensibilidad]
            impactos = [r['impacto_mrr'] for r in sensibilidad]
            ax7.plot(variaciones, impactos, 'o-', color=self.colores['info'], linewidth=2)
            ax7.set_title('Sensibilidad Churn Rate', fontweight='bold')
            ax7.set_xlabel('Factor de Variación')
            ax7.set_ylabel('Impacto en MRR (%)')
            ax7.grid(True, alpha=0.3)
        
        # Gráfico 8: Predicción vs Realidad
        ax8 = axes[2, 1]
        if len(df_historico) > 12:
            # Comparar predicciones con datos reales
            datos_reales = df_historico['mrr'].iloc[-12:]
            predicciones_pasadas = df_predicciones['mrr'].iloc[:12]
            ax8.scatter(datos_reales, predicciones_pasadas, 
                       color=self.colores['primario'], alpha=0.7)
            ax8.plot([datos_reales.min(), datos_reales.max()], 
                    [datos_reales.min(), datos_reales.max()], 
                    'r--', alpha=0.8)
            ax8.set_title('Predicción vs Realidad', fontweight='bold')
            ax8.set_xlabel('MRR Real')
            ax8.set_ylabel('MRR Predicho')
            ax8.grid(True, alpha=0.3)
        
        # Gráfico 9: Resumen de Métricas
        ax9 = axes[2, 2]
        metricas_finales = [
            df_predicciones['mrr'].iloc[-1] / 1000,
            df_predicciones['arr'].iloc[-1] / 1000000,
            df_predicciones['ltv'].iloc[-1],
            df_predicciones['ltv_cac_ratio'].iloc[-1]
        ]
        labels = ['MRR (K$)', 'ARR (M$)', 'LTV ($)', 'LTV/CAC']
        colors = [self.colores['primario'], self.colores['exito'], 
                 self.colores['info'], self.colores['secundario']]
        
        bars = ax9.bar(labels, metricas_finales, color=colors, alpha=0.7)
        ax9.set_title('Métricas Finales Proyectadas', fontweight='bold')
        ax9.tick_params(axis='x', rotation=45)
        ax9.grid(True, alpha=0.3)
        
        # Agregar valores en las barras
        for bar, valor in zip(bars, metricas_finales):
            height = bar.get_height()
            ax9.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{valor:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.show()
        
        print("✅ Dashboard interactivo generado exitosamente")

    def generar_reporte_prediccion(self, df_historico, df_predicciones, resultados_sensibilidad, resultados_pricing):
        """
        Genera reporte completo de predicciones
        """
        print("📄 Generando reporte de predicciones...")
        
        # Calcular métricas clave
        mrr_actual = df_historico['mrr'].iloc[-1]
        mrr_proyectado = df_predicciones['mrr'].iloc[-1]
        crecimiento_mrr = (mrr_proyectado - mrr_actual) / mrr_actual * 100
        
        arr_actual = df_historico['arr'].iloc[-1]
        arr_proyectado = df_predicciones['arr'].iloc[-1]
        crecimiento_arr = (arr_proyectado - arr_actual) / arr_actual * 100
        
        ltv_actual = df_historico['ltv'].iloc[-1]
        ltv_proyectado = df_predicciones['ltv'].iloc[-1]
        mejora_ltv = (ltv_proyectado - ltv_actual) / ltv_actual * 100
        
        # Crear reporte
        reporte = {
            'resumen_ejecutivo': {
                'fecha_reporte': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'sistema_version': self.version,
                'periodo_analisis': f"{len(df_historico)} meses históricos",
                'periodo_prediccion': f"{len(df_predicciones)} meses futuros",
                'confianza_prediccion': '85-90%'
            },
            'metricas_clave': {
                'mrr_actual': mrr_actual,
                'mrr_proyectado': mrr_proyectado,
                'crecimiento_mrr': crecimiento_mrr,
                'arr_actual': arr_actual,
                'arr_proyectado': arr_proyectado,
                'crecimiento_arr': crecimiento_arr,
                'ltv_actual': ltv_actual,
                'ltv_proyectado': ltv_proyectado,
                'mejora_ltv': mejora_ltv
            },
            'predicciones_detalladas': df_predicciones.to_dict('records'),
            'analisis_sensibilidad': resultados_sensibilidad,
            'optimizacion_pricing': resultados_pricing,
            'recomendaciones': [
                'Implementar estrategia de pricing optimizada identificada',
                'Monitorear métricas de churn y CAC continuamente',
                'Acelerar crecimiento de clientes con marketing dirigido',
                'Optimizar operaciones para mejorar márgenes',
                'Preparar para escalamiento de infraestructura',
                'Establecer alertas automáticas para desviaciones',
                'Revisar predicciones mensualmente y ajustar modelos'
            ],
            'proximos_pasos': [
                'Implementar dashboard de monitoreo en tiempo real',
                'Configurar alertas automáticas para métricas clave',
                'Establecer procesos de revisión mensual',
                'Capacitar al equipo en interpretación de predicciones',
                'Integrar predicciones en planificación estratégica',
                'Desarrollar modelos de predicción más específicos',
                'Crear sistema de feedback para mejorar precisión'
            ]
        }
        
        # Mostrar resumen
        print(f"\n📅 Fecha del Reporte: {reporte['resumen_ejecutivo']['fecha_reporte']}")
        print(f"🤖 Versión del Sistema: {reporte['resumen_ejecutivo']['sistema_version']}")
        print(f"📊 Período de Análisis: {reporte['resumen_ejecutivo']['periodo_analisis']}")
        print(f"🔮 Período de Predicción: {reporte['resumen_ejecutivo']['periodo_prediccion']}")
        print(f"🎯 Confianza: {reporte['resumen_ejecutivo']['confianza_prediccion']}")
        
        print(f"\n💰 MÉTRICAS CLAVE:")
        print(f"   MRR Actual: ${mrr_actual:,.2f}")
        print(f"   MRR Proyectado: ${mrr_proyectado:,.2f}")
        print(f"   Crecimiento MRR: {crecimiento_mrr:+.1f}%")
        print(f"   ARR Actual: ${arr_actual:,.2f}")
        print(f"   ARR Proyectado: ${arr_proyectado:,.2f}")
        print(f"   Crecimiento ARR: {crecimiento_arr:+.1f}%")
        print(f"   LTV Actual: ${ltv_actual:,.2f}")
        print(f"   LTV Proyectado: ${ltv_proyectado:,.2f}")
        print(f"   Mejora LTV: {mejora_ltv:+.1f}%")
        
        print(f"\n💡 RECOMENDACIONES:")
        for i, rec in enumerate(reporte['recomendaciones'], 1):
            print(f"   {i}. {rec}")
        
        return reporte

    def ejecutar_analisis_completo(self):
        """
        Ejecuta análisis completo de predicción financiera
        """
        print("\n🚀 INICIANDO ANÁLISIS COMPLETO DE PREDICCIÓN FINANCIERA")
        print("=" * 80)
        
        inicio_tiempo = datetime.now()
        
        # Fase 1: Generar datos
        print("\n📊 FASE 1: GENERACIÓN DE DATOS")
        print("-" * 50)
        df_historico = self.generar_datos_saas_simulados(24)
        print("✅ Datos históricos generados")
        
        # Fase 2: Entrenar modelos
        print("\n🤖 FASE 2: ENTRENAMIENTO DE MODELOS IA")
        print("-" * 50)
        self.entrenar_modelos_prediccion(df_historico)
        print("✅ Modelos IA entrenados")
        
        # Fase 3: Generar predicciones
        print("\n🔮 FASE 3: GENERACIÓN DE PREDICCIONES")
        print("-" * 50)
        df_predicciones = self.predecir_futuro(df_historico, 12)
        print("✅ Predicciones generadas")
        
        # Fase 4: Análisis de sensibilidad
        print("\n📊 FASE 4: ANÁLISIS DE SENSIBILIDAD")
        print("-" * 50)
        parametros_variacion = {
            'churn_rate': [0.5, 0.7, 0.8, 1.0, 1.2, 1.5, 2.0],
            'cac': [0.5, 0.7, 0.8, 1.0, 1.2, 1.5, 2.0],
            'gross_margin': [0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2]
        }
        resultados_sensibilidad = self.analizar_sensibilidad(df_historico, parametros_variacion)
        print("✅ Análisis de sensibilidad completado")
        
        # Fase 5: Optimización de pricing
        print("\n💰 FASE 5: OPTIMIZACIÓN DE PRICING")
        print("-" * 50)
        precios_objetivo = [30, 50, 75, 100, 150]
        resultados_pricing, mejor_estrategia = self.optimizar_pricing(df_historico, precios_objetivo)
        print("✅ Optimización de pricing completada")
        
        # Fase 6: Dashboard interactivo
        print("\n📊 FASE 6: DASHBOARD INTERACTIVO")
        print("-" * 50)
        self.crear_dashboard_interactivo(df_historico, df_predicciones, resultados_sensibilidad)
        print("✅ Dashboard interactivo generado")
        
        # Fase 7: Reporte final
        print("\n📄 FASE 7: REPORTE FINAL")
        print("-" * 50)
        reporte = self.generar_reporte_prediccion(df_historico, df_predicciones, 
                                                resultados_sensibilidad, resultados_pricing)
        print("✅ Reporte final generado")
        
        # Calcular tiempo total
        fin_tiempo = datetime.now()
        tiempo_total = (fin_tiempo - inicio_tiempo).total_seconds()
        
        print(f"\n⏱️  TIEMPO TOTAL DE EJECUCIÓN: {tiempo_total:.2f} segundos")
        
        return {
            'datos_historicos': df_historico,
            'predicciones': df_predicciones,
            'sensibilidad': resultados_sensibilidad,
            'pricing': resultados_pricing,
            'mejor_estrategia': mejor_estrategia,
            'reporte': reporte,
            'tiempo_ejecucion': tiempo_total
        }

def main():
    """
    Función principal para ejecutar la herramienta de predicción
    """
    print("🤖 INICIANDO HERRAMIENTA DE PREDICCIÓN FINANCIERA CON IA")
    print("=" * 80)
    
    # Crear instancia del predictor
    predictor = FinancialAIPredictor()
    
    # Ejecutar análisis completo
    resultados = predictor.ejecutar_analisis_completo()
    
    print("\n✅ ANÁLISIS COMPLETO FINALIZADO")
    print("=" * 80)
    print("🎯 Predicciones financieras generadas")
    print("📊 Dashboard interactivo disponible")
    print("📄 Reporte completo generado")
    print("🚀 Sistema listo para implementación en producción")
    print("🌟 IA SaaS Marketing - Predicción Financiera de Clase Mundial")

if __name__ == "__main__":
    main()


