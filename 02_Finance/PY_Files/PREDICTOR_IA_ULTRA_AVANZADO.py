#!/usr/bin/env python3
"""
PREDICTOR IA ULTRA AVANZADO COPYCAR - SISTEMA DE PREDICCIÓN INTELIGENTE
======================================================================

Sistema de predicción ultra avanzado para estrategias anti-dilución con:
- Deep Learning con redes neuronales
- Análisis de series temporales
- Predicción de tendencias de mercado
- Análisis de sentimiento
- Predicción de eventos de dilución
- Optimización de parámetros con IA

Autor: Sistema Neural Avanzado
Versión: 2.0 - Ultra Avanzada
Fecha: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import json
warnings.filterwarnings('ignore')

class PredictorIAUltraAvanzado:
    def __init__(self):
        self.nombre = "PREDICTOR IA ULTRA AVANZADO COPYCAR"
        self.version = "2.0 - Ultra Avanzada"
        self.fecha_creacion = datetime.now()
        
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
        self.scalers = {}
        self.datos_historicos = []
        self.metricas_prediccion = {}
        
        print(f"🤖 {self.nombre} - {self.version}")
        print(f"📅 Creado: {self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

    def generar_datos_historicos(self, n_dias=365):
        """
        Genera datos históricos sintéticos para entrenamiento
        """
        print(f"\n📊 GENERANDO DATOS HISTÓRICOS ({n_dias} días)")
        print("=" * 50)
        
        np.random.seed(42)
        fechas = pd.date_range(start=datetime.now() - timedelta(days=n_dias), 
                              end=datetime.now(), freq='D')
        
        # Simular tendencias de mercado
        tendencia_base = np.linspace(100, 120, n_dias)  # Tendencia alcista
        volatilidad = np.random.normal(0, 2, n_dias)
        ciclos = 5 * np.sin(2 * np.pi * np.arange(n_dias) / 30)  # Ciclos mensuales
        
        # Variables principales
        valoracion_diaria = tendencia_base + volatilidad + ciclos
        volumen_operaciones = np.random.exponential(1000000, n_dias)
        precio_accion = valoracion_diaria / 1000000  # Asumiendo 1M acciones
        
        # Variables de dilución (eventos esporádicos)
        eventos_dilucion = np.random.poisson(0.1, n_dias)  # Eventos raros
        dilucion_diaria = np.where(eventos_dilucion > 0, 
                                 np.random.uniform(0.05, 0.25, n_dias), 0)
        
        # Asegurar que todos los arrays tengan la misma longitud
        n_dias = len(fechas)
        
        # Variables de mercado
        indice_mercado = np.random.normal(100, 5, n_dias)
        volatilidad_mercado = np.random.gamma(2, 0.5, n_dias)
        sentimiento_inversion = np.random.uniform(-1, 1, n_dias)
        
        # Variables de la empresa
        crecimiento_ingresos = np.random.normal(0.02, 0.01, n_dias)  # 2% diario
        burn_rate = np.random.normal(50000, 10000, n_dias)  # $50K diario
        runway_meses = np.random.uniform(6, 24, n_dias)
        
        # Asegurar que todos los arrays tengan exactamente n_dias elementos
        valoracion_diaria = valoracion_diaria[:n_dias]
        precio_accion = precio_accion[:n_dias]
        volumen_operaciones = volumen_operaciones[:n_dias]
        dilucion_diaria = dilucion_diaria[:n_dias]
        indice_mercado = indice_mercado[:n_dias]
        volatilidad_mercado = volatilidad_mercado[:n_dias]
        sentimiento_inversion = sentimiento_inversion[:n_dias]
        crecimiento_ingresos = crecimiento_ingresos[:n_dias]
        burn_rate = burn_rate[:n_dias]
        runway_meses = runway_meses[:n_dias]
        
        # Crear DataFrame
        datos = pd.DataFrame({
            'fecha': fechas,
            'valoracion_diaria': valoracion_diaria,
            'precio_accion': precio_accion,
            'volumen_operaciones': volumen_operaciones,
            'dilucion_diaria': dilucion_diaria,
            'indice_mercado': indice_mercado,
            'volatilidad_mercado': volatilidad_mercado,
            'sentimiento_inversion': sentimiento_inversion,
            'crecimiento_ingresos': crecimiento_ingresos,
            'burn_rate': burn_rate,
            'runway_meses': runway_meses
        })
        
        # Agregar variables calculadas
        datos['cambio_valoracion'] = datos['valoracion_diaria'].pct_change()
        datos['cambio_precio'] = datos['precio_accion'].pct_change()
        datos['volatilidad_7d'] = datos['cambio_valoracion'].rolling(7).std()
        datos['media_movil_30d'] = datos['valoracion_diaria'].rolling(30).mean()
        datos['ratio_valoracion_media'] = datos['valoracion_diaria'] / datos['media_movil_30d']
        
        # Variables de predicción (targets)
        datos['dilucion_7d'] = datos['dilucion_diaria'].rolling(7).sum()
        datos['dilucion_30d'] = datos['dilucion_diaria'].rolling(30).sum()
        datos['valoracion_7d_futura'] = datos['valoracion_diaria'].shift(-7)
        datos['valoracion_30d_futura'] = datos['valoracion_diaria'].shift(-30)
        
        # Limpiar datos
        datos = datos.dropna()
        
        self.datos_historicos = datos
        
        print(f"✅ Datos históricos generados: {len(datos)} registros")
        print(f"📊 Variables: {len(datos.columns)}")
        print(f"📅 Período: {datos['fecha'].min().date()} - {datos['fecha'].max().date()}")
        
        return datos

    def entrenar_modelos_ia(self, datos):
        """
        Entrena modelos de IA avanzados
        """
        print("\n🤖 ENTRENANDO MODELOS DE IA AVANZADOS")
        print("=" * 50)
        
        # Preparar datos
        features = ['valoracion_diaria', 'precio_accion', 'volumen_operaciones',
                   'indice_mercado', 'volatilidad_mercado', 'sentimiento_inversion',
                   'crecimiento_ingresos', 'burn_rate', 'runway_meses',
                   'cambio_valoracion', 'cambio_precio', 'volatilidad_7d',
                   'ratio_valoracion_media']
        
        X = datos[features].values
        
        # Targets
        y_dilucion_7d = datos['dilucion_7d'].values
        y_dilucion_30d = datos['dilucion_30d'].values
        y_valoracion_7d = datos['valoracion_7d_futura'].values
        y_valoracion_30d = datos['valoracion_30d_futura'].values
        
        # Normalizar datos
        scaler_X = StandardScaler()
        X_scaled = scaler_X.fit_transform(X)
        
        # Dividir datos temporalmente
        split_point = int(len(X_scaled) * 0.8)
        X_train, X_test = X_scaled[:split_point], X_scaled[split_point:]
        y_dilucion_7d_train, y_dilucion_7d_test = y_dilucion_7d[:split_point], y_dilucion_7d[split_point:]
        y_dilucion_30d_train, y_dilucion_30d_test = y_dilucion_30d[:split_point], y_dilucion_30d[split_point:]
        y_valoracion_7d_train, y_valoracion_7d_test = y_valoracion_7d[:split_point], y_valoracion_7d[split_point:]
        y_valoracion_30d_train, y_valoracion_30d_test = y_valoracion_30d[:split_point], y_valoracion_30d[split_point:]
        
        # Modelo 1: Predicción de dilución 7 días
        print("🔮 Entrenando modelo de dilución 7 días...")
        modelo_dilucion_7d = MLPRegressor(
            hidden_layer_sizes=(100, 50, 25),
            activation='relu',
            solver='adam',
            alpha=0.001,
            learning_rate='adaptive',
            max_iter=1000,
            random_state=42
        )
        modelo_dilucion_7d.fit(X_train, y_dilucion_7d_train)
        
        # Modelo 2: Predicción de dilución 30 días
        print("🔮 Entrenando modelo de dilución 30 días...")
        modelo_dilucion_30d = MLPRegressor(
            hidden_layer_sizes=(100, 50, 25),
            activation='relu',
            solver='adam',
            alpha=0.001,
            learning_rate='adaptive',
            max_iter=1000,
            random_state=42
        )
        modelo_dilucion_30d.fit(X_train, y_dilucion_30d_train)
        
        # Modelo 3: Predicción de valoración 7 días
        print("💰 Entrenando modelo de valoración 7 días...")
        modelo_valoracion_7d = MLPRegressor(
            hidden_layer_sizes=(100, 50, 25),
            activation='relu',
            solver='adam',
            alpha=0.001,
            learning_rate='adaptive',
            max_iter=1000,
            random_state=42
        )
        modelo_valoracion_7d.fit(X_train, y_valoracion_7d_train)
        
        # Modelo 4: Predicción de valoración 30 días
        print("💰 Entrenando modelo de valoración 30 días...")
        modelo_valoracion_30d = MLPRegressor(
            hidden_layer_sizes=(100, 50, 25),
            activation='relu',
            solver='adam',
            alpha=0.001,
            learning_rate='adaptive',
            max_iter=1000,
            random_state=42
        )
        modelo_valoracion_30d.fit(X_train, y_valoracion_30d_train)
        
        # Evaluar modelos
        modelos_evaluados = {}
        
        for nombre, modelo, y_train, y_test in [
            ('dilucion_7d', modelo_dilucion_7d, y_dilucion_7d_train, y_dilucion_7d_test),
            ('dilucion_30d', modelo_dilucion_30d, y_dilucion_30d_train, y_dilucion_30d_test),
            ('valoracion_7d', modelo_valoracion_7d, y_valoracion_7d_train, y_valoracion_7d_test),
            ('valoracion_30d', modelo_valoracion_30d, y_valoracion_30d_train, y_valoracion_30d_test)
        ]:
            y_pred = modelo.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            modelos_evaluados[nombre] = {
                'modelo': modelo,
                'mse': mse,
                'mae': mae,
                'r2': r2
            }
        
        # Guardar modelos y scaler
        self.modelos_ia = modelos_evaluados
        self.scalers['X'] = scaler_X
        
        # Mostrar resultados
        print("\n📊 RESULTADOS DE ENTRENAMIENTO:")
        for nombre, metricas in modelos_evaluados.items():
            print(f"   {nombre}: MSE={metricas['mse']:.4f}, MAE={metricas['mae']:.4f}, R²={metricas['r2']:.4f}")
        
        return modelos_evaluados

    def predecir_dilucion(self, datos_actuales, horizonte_dias=30):
        """
        Predice la probabilidad de dilución en el futuro
        """
        print(f"\n🔮 PREDICIENDO DILUCIÓN ({horizonte_dias} días)")
        print("=" * 50)
        
        if not self.modelos_ia:
            print("❌ Modelos no entrenados. Ejecutando entrenamiento...")
            datos = self.generar_datos_historicos()
            self.entrenar_modelos_ia(datos)
        
        # Preparar datos actuales
        features = ['valoracion_diaria', 'precio_accion', 'volumen_operaciones',
                   'indice_mercado', 'volatilidad_mercado', 'sentimiento_inversion',
                   'crecimiento_ingresos', 'burn_rate', 'runway_meses',
                   'cambio_valoracion', 'cambio_precio', 'volatilidad_7d',
                   'ratio_valoracion_media']
        
        # Si no tenemos datos históricos, usar datos actuales
        if len(self.datos_historicos) == 0:
            datos_actuales_array = np.array([datos_actuales.get(f, 0) for f in features])
        else:
            # Usar los últimos datos disponibles
            datos_actuales_array = self.datos_historicos[features].iloc[-1].values
        
        # Normalizar
        X_scaled = self.scalers['X'].transform([datos_actuales_array])
        
        # Hacer predicciones
        modelo_dilucion = self.modelos_ia['dilucion_30d']['modelo']
        prediccion_dilucion = modelo_dilucion.predict(X_scaled)[0]
        
        # Calcular probabilidad de dilución
        probabilidad_dilucion = min(max(prediccion_dilucion, 0), 1)
        
        # Clasificar riesgo
        if probabilidad_dilucion < 0.1:
            nivel_riesgo = 'BAJO'
            color = self.colores['exito']
        elif probabilidad_dilucion < 0.3:
            nivel_riesgo = 'MEDIO'
            color = self.colores['info']
        elif probabilidad_dilucion < 0.5:
            nivel_riesgo = 'ALTO'
            color = self.colores['advertencia']
        else:
            nivel_riesgo = 'CRÍTICO'
            color = self.colores['advertencia']
        
        resultado = {
            'probabilidad_dilucion': probabilidad_dilucion,
            'nivel_riesgo': nivel_riesgo,
            'horizonte_dias': horizonte_dias,
            'recomendacion': self._generar_recomendacion_dilucion(probabilidad_dilucion)
        }
        
        print(f"🎯 Probabilidad de dilución: {probabilidad_dilucion:.1%}")
        print(f"⚠️  Nivel de riesgo: {nivel_riesgo}")
        print(f"💡 Recomendación: {resultado['recomendacion']}")
        
        return resultado

    def predecir_valoracion(self, datos_actuales, horizonte_dias=30):
        """
        Predice la valoración futura de la empresa
        """
        print(f"\n💰 PREDICIENDO VALORACIÓN ({horizonte_dias} días)")
        print("=" * 50)
        
        if not self.modelos_ia:
            print("❌ Modelos no entrenados. Ejecutando entrenamiento...")
            datos = self.generar_datos_historicos()
            self.entrenar_modelos_ia(datos)
        
        # Preparar datos actuales
        features = ['valoracion_diaria', 'precio_accion', 'volumen_operaciones',
                   'indice_mercado', 'volatilidad_mercado', 'sentimiento_inversion',
                   'crecimiento_ingresos', 'burn_rate', 'runway_meses',
                   'cambio_valoracion', 'cambio_precio', 'volatilidad_7d',
                   'ratio_valoracion_media']
        
        # Usar los últimos datos disponibles
        if len(self.datos_historicos) == 0:
            datos_actuales_array = np.array([datos_actuales.get(f, 0) for f in features])
        else:
            datos_actuales_array = self.datos_historicos[features].iloc[-1].values
        
        # Normalizar
        X_scaled = self.scalers['X'].transform([datos_actuales_array])
        
        # Hacer predicciones
        modelo_valoracion = self.modelos_ia['valoracion_30d']['modelo']
        prediccion_valoracion = modelo_valoracion.predict(X_scaled)[0]
        
        # Calcular cambio porcentual
        valoracion_actual = datos_actuales.get('valoracion_actual', 5000000)
        cambio_porcentual = ((prediccion_valoracion - valoracion_actual) / valoracion_actual) * 100
        
        # Clasificar tendencia
        if cambio_porcentual > 5:
            tendencia = 'ALCISTA FUERTE'
            color = self.colores['exito']
        elif cambio_porcentual > 0:
            tendencia = 'ALCISTA'
            color = self.colores['exito']
        elif cambio_porcentual > -5:
            tendencia = 'LATERAL'
            color = self.colores['neutro']
        else:
            tendencia = 'BAJISTA'
            color = self.colores['advertencia']
        
        resultado = {
            'valoracion_predicha': prediccion_valoracion,
            'valoracion_actual': valoracion_actual,
            'cambio_porcentual': cambio_porcentual,
            'tendencia': tendencia,
            'horizonte_dias': horizonte_dias
        }
        
        print(f"💰 Valoración actual: ${valoracion_actual:,.2f}")
        print(f"🔮 Valoración predicha: ${prediccion_valoracion:,.2f}")
        print(f"📈 Cambio porcentual: {cambio_porcentual:.2f}%")
        print(f"📊 Tendencia: {tendencia}")
        
        return resultado

    def analizar_sentimiento_mercado(self, datos_actuales):
        """
        Analiza el sentimiento del mercado hacia la empresa
        """
        print("\n😊 ANÁLISIS DE SENTIMIENTO DEL MERCADO")
        print("=" * 50)
        
        # Simular análisis de sentimiento
        sentimiento_base = datos_actuales.get('sentimiento_inversion', 0)
        
        # Factores que afectan el sentimiento
        factores = {
            'crecimiento_ingresos': datos_actuales.get('crecimiento_ingresos', 0.02),
            'runway_meses': datos_actuales.get('runway_meses', 12),
            'volatilidad_mercado': datos_actuales.get('volatilidad_mercado', 0.2),
            'indice_mercado': datos_actuales.get('indice_mercado', 100)
        }
        
        # Calcular sentimiento compuesto
        sentimiento_compuesto = sentimiento_base
        sentimiento_compuesto += factores['crecimiento_ingresos'] * 10  # Crecimiento positivo
        sentimiento_compuesto += (24 - factores['runway_meses']) / 24 * 0.5  # Runway más largo es mejor
        sentimiento_compuesto -= factores['volatilidad_mercado'] * 0.5  # Volatilidad negativa
        sentimiento_compuesto += (factores['indice_mercado'] - 100) / 100 * 0.3  # Mercado alcista
        
        # Normalizar entre -1 y 1
        sentimiento_compuesto = np.clip(sentimiento_compuesto, -1, 1)
        
        # Clasificar sentimiento
        if sentimiento_compuesto > 0.5:
            clasificacion = 'MUY POSITIVO'
            color = self.colores['exito']
        elif sentimiento_compuesto > 0.1:
            clasificacion = 'POSITIVO'
            color = self.colores['exito']
        elif sentimiento_compuesto > -0.1:
            clasificacion = 'NEUTRO'
            color = self.colores['neutro']
        elif sentimiento_compuesto > -0.5:
            clasificacion = 'NEGATIVO'
            color = self.colores['advertencia']
        else:
            clasificacion = 'MUY NEGATIVO'
            color = self.colores['advertencia']
        
        resultado = {
            'sentimiento_score': sentimiento_compuesto,
            'clasificacion': clasificacion,
            'factores': factores,
            'recomendacion': self._generar_recomendacion_sentimiento(sentimiento_compuesto)
        }
        
        print(f"😊 Sentimiento: {sentimiento_compuesto:.3f}")
        print(f"📊 Clasificación: {clasificacion}")
        print(f"💡 Recomendación: {resultado['recomendacion']}")
        
        return resultado

    def _generar_recomendacion_dilucion(self, probabilidad):
        """
        Genera recomendaciones basadas en la probabilidad de dilución
        """
        if probabilidad < 0.1:
            return "Situación estable. Mantener monitoreo estándar."
        elif probabilidad < 0.3:
            return "Aumentar frecuencia de monitoreo. Preparar estrategias preventivas."
        elif probabilidad < 0.5:
            return "Alto riesgo detectado. Activar cláusulas anti-dilución."
        else:
            return "Riesgo crítico. Implementar protección inmediata."

    def _generar_recomendacion_sentimiento(self, sentimiento):
        """
        Genera recomendaciones basadas en el sentimiento del mercado
        """
        if sentimiento > 0.5:
            return "Aprovechar sentimiento positivo para negociaciones favorables."
        elif sentimiento > 0.1:
            return "Mantener momentum positivo con comunicación estratégica."
        elif sentimiento > -0.1:
            return "Trabajar en mejorar percepción del mercado."
        elif sentimiento > -0.5:
            return "Implementar estrategias de comunicación de crisis."
        else:
            return "Situación crítica. Revisar estrategia de comunicación urgentemente."

    def crear_dashboard_prediccion(self, datos_empresa):
        """
        Crea un dashboard de predicciones
        """
        print("\n📊 CREANDO DASHBOARD DE PREDICCIONES")
        print("=" * 50)
        
        # Generar datos y entrenar modelos
        datos = self.generar_datos_historicos()
        modelos = self.entrenar_modelos_ia(datos)
        
        # Hacer predicciones
        prediccion_dilucion = self.predecir_dilucion(datos_empresa)
        prediccion_valoracion = self.predecir_valoracion(datos_empresa)
        sentimiento = self.analizar_sentimiento_mercado(datos_empresa)
        
        # Configurar el estilo
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(3, 2, figsize=(16, 18))
        fig.suptitle('DASHBOARD DE PREDICCIONES IA - COPYCAR', fontsize=18, fontweight='bold')
        
        # Gráfico 1: Predicción de dilución
        ax1 = axes[0, 0]
        probabilidades = [prediccion_dilucion['probabilidad_dilucion']]
        niveles = [prediccion_dilucion['nivel_riesgo']]
        colores_riesgo = [self.colores['exito'] if p < 0.1 else 
                         self.colores['info'] if p < 0.3 else 
                         self.colores['advertencia'] for p in probabilidades]
        
        ax1.bar(['Dilución 30d'], probabilidades, color=colores_riesgo, alpha=0.7)
        ax1.set_title('Predicción de Dilución', fontweight='bold')
        ax1.set_ylabel('Probabilidad')
        ax1.set_ylim(0, 1)
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Predicción de valoración
        ax2 = axes[0, 1]
        valoraciones = [prediccion_valoracion['valoracion_actual'], 
                       prediccion_valoracion['valoracion_predicha']]
        etiquetas = ['Actual', 'Predicha']
        
        ax2.bar(etiquetas, valoraciones, color=[self.colores['primario'], self.colores['secundario']], alpha=0.7)
        ax2.set_title('Predicción de Valoración', fontweight='bold')
        ax2.set_ylabel('Valoración ($)')
        ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Análisis de sentimiento
        ax3 = axes[1, 0]
        sentimiento_score = sentimiento['sentimiento_score']
        ax3.barh(['Sentimiento'], [sentimiento_score], 
                color=self.colores['exito'] if sentimiento_score > 0 else self.colores['advertencia'], 
                alpha=0.7)
        ax3.set_title('Análisis de Sentimiento', fontweight='bold')
        ax3.set_xlabel('Score (-1 a 1)')
        ax3.set_xlim(-1, 1)
        ax3.axvline(x=0, color='black', linestyle='--', alpha=0.5)
        ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Métricas de modelos ML
        ax4 = axes[1, 1]
        modelos_nombres = list(modelos.keys())
        r2_scores = [modelos[m]['r2'] for m in modelos_nombres]
        
        ax4.bar(modelos_nombres, r2_scores, color=self.colores['info'], alpha=0.7)
        ax4.set_title('Precisión de Modelos ML', fontweight='bold')
        ax4.set_ylabel('R² Score')
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(True, alpha=0.3)
        
        # Gráfico 5: Tendencias históricas
        ax5 = axes[2, 0]
        if len(datos) > 0:
            fechas = datos['fecha'][-30:]  # Últimos 30 días
            valoraciones = datos['valoracion_diaria'][-30:]
            
            ax5.plot(fechas, valoraciones, linewidth=2, color=self.colores['primario'])
            ax5.set_title('Tendencia Histórica (30 días)', fontweight='bold')
            ax5.set_xlabel('Fecha')
            ax5.set_ylabel('Valoración ($)')
            ax5.tick_params(axis='x', rotation=45)
            ax5.grid(True, alpha=0.3)
        
        # Gráfico 6: Resumen de predicciones
        ax6 = axes[2, 1]
        metricas = ['Dilución\nRiesgo', 'Valoración\nTendencia', 'Sentimiento\nMercado']
        valores = [
            prediccion_dilucion['probabilidad_dilucion'],
            abs(prediccion_valoracion['cambio_porcentual']) / 100,
            (sentimiento['sentimiento_score'] + 1) / 2
        ]
        
        ax6.bar(metricas, valores, color=[self.colores['advertencia'], 
                                        self.colores['info'], 
                                        self.colores['exito']], alpha=0.7)
        ax6.set_title('Resumen de Predicciones', fontweight='bold')
        ax6.set_ylabel('Score Normalizado')
        ax6.set_ylim(0, 1)
        ax6.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        print("✅ Dashboard de predicciones generado exitosamente")

    def generar_reporte_prediccion(self, datos_empresa):
        """
        Genera un reporte completo de predicciones
        """
        print("\n📄 GENERANDO REPORTE DE PREDICCIONES")
        print("=" * 50)
        
        # Ejecutar todas las predicciones
        datos = self.generar_datos_historicos()
        modelos = self.entrenar_modelos_ia(datos)
        prediccion_dilucion = self.predecir_dilucion(datos_empresa)
        prediccion_valoracion = self.predecir_valoracion(datos_empresa)
        sentimiento = self.analizar_sentimiento_mercado(datos_empresa)
        
        reporte = {
            'resumen_ejecutivo': {
                'fecha_reporte': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'version_predictor': self.version,
                'probabilidad_dilucion': prediccion_dilucion['probabilidad_dilucion'],
                'nivel_riesgo': prediccion_dilucion['nivel_riesgo'],
                'tendencia_valoracion': prediccion_valoracion['tendencia'],
                'sentimiento_mercado': sentimiento['clasificacion']
            },
            'prediccion_dilucion': prediccion_dilucion,
            'prediccion_valoracion': prediccion_valoracion,
            'analisis_sentimiento': sentimiento,
            'modelos_ml': {
                nombre: {
                    'r2': modelo['r2'],
                    'mse': modelo['mse'],
                    'mae': modelo['mae']
                }
                for nombre, modelo in modelos.items()
            },
            'recomendaciones_prediccion': [
                prediccion_dilucion['recomendacion'],
                f"Monitorear tendencia de valoración: {prediccion_valoracion['tendencia']}",
                sentimiento['recomendacion'],
                "Validar predicciones con datos reales semanalmente",
                "Ajustar modelos según nuevos datos de mercado"
            ]
        }
        
        # Mostrar resumen
        print(f"📅 Fecha del Reporte: {reporte['resumen_ejecutivo']['fecha_reporte']}")
        print(f"🎯 Probabilidad de Dilución: {reporte['resumen_ejecutivo']['probabilidad_dilucion']:.1%}")
        print(f"⚠️  Nivel de Riesgo: {reporte['resumen_ejecutivo']['nivel_riesgo']}")
        print(f"📈 Tendencia de Valoración: {reporte['resumen_ejecutivo']['tendencia_valoracion']}")
        print(f"😊 Sentimiento del Mercado: {reporte['resumen_ejecutivo']['sentimiento_mercado']}")
        
        print(f"\n💡 RECOMENDACIONES DE PREDICCIÓN:")
        for i, rec in enumerate(reporte['recomendaciones_prediccion'], 1):
            print(f"   {i}. {rec}")
        
        return reporte

    def ejecutar_prediccion_completa(self, datos_empresa):
        """
        Ejecuta la predicción completa del sistema
        """
        print("\n🚀 INICIANDO PREDICCIÓN COMPLETA")
        print("=" * 80)
        
        # Crear dashboard
        self.crear_dashboard_prediccion(datos_empresa)
        
        # Generar reporte
        reporte = self.generar_reporte_prediccion(datos_empresa)
        
        print("\n🎉 PREDICCIÓN COMPLETA FINALIZADA")
        print("=" * 80)
        
        return reporte

def main():
    """
    Función principal para ejecutar el predictor
    """
    print("🤖 INICIANDO PREDICTOR IA ULTRA AVANZADO COPYCAR")
    print("=" * 80)
    
    # Crear instancia del predictor
    predictor = PredictorIAUltraAvanzado()
    
    # Datos de ejemplo de la empresa
    datos_empresa = {
        'valoracion_actual': 5000000,  # $5M
        'inversion_actual': 500000,    # $500K
        'acciones_totales': 1000000,   # 1M acciones
        'porcentaje_actual': 10.0,     # 10%
        'crecimiento_ingresos': 0.02,  # 2% diario
        'runway_meses': 12,            # 12 meses
        'volatilidad_mercado': 0.2,    # 20%
        'indice_mercado': 105,         # 105
        'sentimiento_inversion': 0.3   # Positivo
    }
    
    # Ejecutar predicción completa
    reporte = predictor.ejecutar_prediccion_completa(datos_empresa)
    
    print("\n✅ PREDICTOR IA ULTRA AVANZADO COPYCAR COMPLETADO")
    print("=" * 80)

if __name__ == "__main__":
    main()
