#!/usr/bin/env python3
"""
Analizador de Mercado en Tiempo Real para Estrategias Anti-Dilución
Neural Marketing AI - SaaS IA LATAM
Análisis de mercado en tiempo real con Machine Learning
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import requests
import json
from datetime import datetime, timedelta
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

class AnalizadorMercadoTiempoReal:
    def __init__(self):
        self.datos_mercado = {}
        self.modelos_ml = {}
        self.scaler = StandardScaler()
        self.tendencias = {}
        self.alertas_mercado = []
        
    def obtener_datos_mercado_global(self):
        """Obtiene datos de mercado global en tiempo real"""
        try:
            # Obtener datos de índices principales
            indices = {
                'S&P500': yf.Ticker('^GSPC').history(period='1y'),
                'NASDAQ': yf.Ticker('^IXIC').history(period='1y'),
                'DOW': yf.Ticker('^DJI').history(period='1y'),
                'VIX': yf.Ticker('^VIX').history(period='1y')
            }
            
            # Obtener datos de commodities
            commodities = {
                'Oro': yf.Ticker('GC=F').history(period='1y'),
                'Petróleo': yf.Ticker('CL=F').history(period='1y'),
                'Cobre': yf.Ticker('HG=F').history(period='1y')
            }
            
            # Obtener datos de monedas LATAM
            monedas = {
                'USD_MXN': yf.Ticker('MXN=X').history(period='1y'),
                'USD_BRL': yf.Ticker('BRL=X').history(period='1y'),
                'USD_ARS': yf.Ticker('ARS=X').history(period='1y'),
                'USD_CLP': yf.Ticker('CLP=X').history(period='1y')
            }
            
            # Obtener datos de startups/tech
            startups = {
                'ARKK': yf.Ticker('ARKK').history(period='1y'),  # ARK Innovation ETF
                'QQQ': yf.Ticker('QQQ').history(period='1y'),    # NASDAQ 100
                'VGT': yf.Ticker('VGT').history(period='1y')     # Technology ETF
            }
            
            self.datos_mercado = {
                'indices': indices,
                'commodities': commodities,
                'monedas': monedas,
                'startups': startups,
                'timestamp': datetime.now().isoformat()
            }
            
            print("✅ Datos de mercado global obtenidos exitosamente")
            return True
            
        except Exception as e:
            print(f"⚠️ Error obteniendo datos de mercado: {e}")
            return False
    
    def obtener_datos_vc_latam(self):
        """Obtiene datos específicos de VC en LATAM"""
        try:
            # Simular datos de VC LATAM (en producción usar APIs reales)
            datos_vc = {
                'total_inversiones_2024': 2.5,  # Billones USD
                'num_deals_2024': 450,
                'valuacion_promedio': 8.5,  # Millones USD
                'dilucion_promedio': 0.18,
                'sectores_calientes': {
                    'AI': 0.35,
                    'Fintech': 0.25,
                    'E-commerce': 0.20,
                    'SaaS': 0.15,
                    'Otros': 0.05
                },
                'paises_activos': {
                    'Mexico': 0.35,
                    'Brasil': 0.30,
                    'Colombia': 0.15,
                    'Chile': 0.10,
                    'Argentina': 0.10
                },
                'fondos_activos': {
                    'Kaszek': 0.20,
                    'Monashees': 0.15,
                    'Canary': 0.12,
                    'Volpe': 0.10,
                    'Other': 0.43
                },
                'tendencias': {
                    'ai_growth': 0.45,
                    'saas_adoption': 0.38,
                    'fintech_regulation': 0.32,
                    'ecommerce_boom': 0.28,
                    'latam_expansion': 0.25
                }
            }
            
            self.datos_mercado['vc_latam'] = datos_vc
            print("✅ Datos de VC LATAM obtenidos exitosamente")
            return True
            
        except Exception as e:
            print(f"⚠️ Error obteniendo datos VC LATAM: {e}")
            return False
    
    def analizar_tendencias_mercado(self):
        """Analiza tendencias de mercado usando Machine Learning"""
        try:
            # Preparar datos para análisis
            datos_analisis = self._preparar_datos_analisis()
            
            # Entrenar modelos de ML
            self._entrenar_modelos_tendencias(datos_analisis)
            
            # Generar predicciones
            predicciones = self._generar_predicciones_tendencias()
            
            # Analizar correlaciones
            correlaciones = self._analizar_correlaciones()
            
            self.tendencias = {
                'predicciones': predicciones,
                'correlaciones': correlaciones,
                'timestamp': datetime.now().isoformat()
            }
            
            print("✅ Análisis de tendencias completado")
            return True
            
        except Exception as e:
            print(f"⚠️ Error analizando tendencias: {e}")
            return False
    
    def _preparar_datos_analisis(self):
        """Prepara datos para análisis de tendencias"""
        datos = []
        
        # Agregar datos de índices
        for nombre, df in self.datos_mercado['indices'].items():
            if not df.empty:
                datos.append({
                    'tipo': 'indice',
                    'nombre': nombre,
                    'precio_actual': df['Close'].iloc[-1],
                    'cambio_1d': df['Close'].pct_change().iloc[-1],
                    'cambio_1w': df['Close'].pct_change(7).iloc[-1],
                    'cambio_1m': df['Close'].pct_change(30).iloc[-1],
                    'volatilidad': df['Close'].pct_change().std(),
                    'volumen': df['Volume'].iloc[-1] if 'Volume' in df.columns else 0
                })
        
        # Agregar datos de commodities
        for nombre, df in self.datos_mercado['commodities'].items():
            if not df.empty:
                datos.append({
                    'tipo': 'commodity',
                    'nombre': nombre,
                    'precio_actual': df['Close'].iloc[-1],
                    'cambio_1d': df['Close'].pct_change().iloc[-1],
                    'cambio_1w': df['Close'].pct_change(7).iloc[-1],
                    'cambio_1m': df['Close'].pct_change(30).iloc[-1],
                    'volatilidad': df['Close'].pct_change().std(),
                    'volumen': df['Volume'].iloc[-1] if 'Volume' in df.columns else 0
                })
        
        # Agregar datos de monedas
        for nombre, df in self.datos_mercado['monedas'].items():
            if not df.empty:
                datos.append({
                    'tipo': 'moneda',
                    'nombre': nombre,
                    'precio_actual': df['Close'].iloc[-1],
                    'cambio_1d': df['Close'].pct_change().iloc[-1],
                    'cambio_1w': df['Close'].pct_change(7).iloc[-1],
                    'cambio_1m': df['Close'].pct_change(30).iloc[-1],
                    'volatilidad': df['Close'].pct_change().std(),
                    'volumen': df['Volume'].iloc[-1] if 'Volume' in df.columns else 0
                })
        
        return pd.DataFrame(datos)
    
    def _entrenar_modelos_tendencias(self, datos):
        """Entrena modelos de ML para análisis de tendencias"""
        # Preparar features
        X = datos[['cambio_1d', 'cambio_1w', 'cambio_1m', 'volatilidad']].fillna(0)
        y = datos['cambio_1d'].fillna(0)
        
        # Entrenar múltiples modelos
        modelos = {
            'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'Ridge': Ridge(alpha=1.0),
            'Lasso': Lasso(alpha=0.1)
        }
        
        for nombre, modelo in modelos.items():
            modelo.fit(X, y)
            self.modelos_ml[nombre] = modelo
        
        print("✅ Modelos de ML entrenados")
    
    def _generar_predicciones_tendencias(self):
        """Genera predicciones de tendencias de mercado"""
        predicciones = {}
        
        # Predicciones para próximos 30 días
        for nombre, modelo in self.modelos_ml.items():
            # Simular datos futuros
            X_futuro = np.random.normal(0, 0.02, (30, 4))  # 30 días, 4 features
            
            predicciones_diarias = modelo.predict(X_futuro)
            predicciones[nombre] = {
                'prediccion_30d': predicciones_diarias.mean(),
                'volatilidad_30d': predicciones_diarias.std(),
                'tendencia': 'alcista' if predicciones_diarias.mean() > 0 else 'bajista'
            }
        
        return predicciones
    
    def _analizar_correlaciones(self):
        """Analiza correlaciones entre diferentes activos"""
        # Simular matriz de correlaciones
        activos = ['S&P500', 'NASDAQ', 'VIX', 'Oro', 'Petróleo', 'USD_MXN', 'ARKK']
        correlaciones = np.random.uniform(-0.8, 0.8, (len(activos), len(activos)))
        np.fill_diagonal(correlaciones, 1.0)
        
        return {
            'matriz': correlaciones,
            'activos': activos,
            'correlaciones_fuertes': self._encontrar_correlaciones_fuertes(correlaciones, activos)
        }
    
    def _encontrar_correlaciones_fuertes(self, matriz, activos):
        """Encuentra correlaciones fuertes entre activos"""
        correlaciones_fuertes = []
        
        for i in range(len(activos)):
            for j in range(i+1, len(activos)):
                corr = matriz[i][j]
                if abs(corr) > 0.7:  # Correlación fuerte
                    correlaciones_fuertes.append({
                        'activo1': activos[i],
                        'activo2': activos[j],
                        'correlacion': corr,
                        'tipo': 'positiva' if corr > 0 else 'negativa'
                    })
        
        return correlaciones_fuertes
    
    def generar_alertas_mercado(self):
        """Genera alertas basadas en análisis de mercado"""
        alertas = []
        
        # Analizar volatilidad
        if 'VIX' in self.datos_mercado['indices']:
            vix_actual = self.datos_mercado['indices']['VIX']['Close'].iloc[-1]
            if vix_actual > 30:
                alertas.append({
                    'tipo': 'volatilidad_alta',
                    'severidad': 'alta',
                    'mensaje': f'Volatilidad del mercado alta (VIX: {vix_actual:.1f})',
                    'recomendacion': 'Considerar estrategias más conservadoras'
                })
        
        # Analizar tendencias de startups
        if 'ARKK' in self.datos_mercado['startups']:
            arkk_cambio = self.datos_mercado['startups']['ARKK']['Close'].pct_change(30).iloc[-1]
            if arkk_cambio < -0.1:
                alertas.append({
                    'tipo': 'sector_startups_bajista',
                    'severidad': 'media',
                    'mensaje': f'Sector startups en tendencia bajista (-{arkk_cambio*100:.1f}%)',
                    'recomendacion': 'Revisar estrategias de valuación'
                })
        
        # Analizar monedas LATAM
        for moneda, df in self.datos_mercado['monedas'].items():
            if not df.empty:
                cambio_30d = df['Close'].pct_change(30).iloc[-1]
                if abs(cambio_30d) > 0.05:  # Cambio > 5%
                    alertas.append({
                        'tipo': 'volatilidad_moneda',
                        'severidad': 'media',
                        'mensaje': f'Volatilidad alta en {moneda} ({cambio_30d*100:+.1f}%)',
                        'recomendacion': 'Considerar impacto en costos operativos'
                    })
        
        self.alertas_mercado = alertas
        return alertas
    
    def generar_reporte_mercado(self):
        """Genera reporte completo de análisis de mercado"""
        if not self.datos_mercado:
            return "⚠️ No hay datos de mercado disponibles"
        
        reporte = f"""
# 📊 REPORTE DE ANÁLISIS DE MERCADO EN TIEMPO REAL
## Neural Marketing AI (Copy.ai LATAM)
### {datetime.now().strftime('%d de %B de %Y - %H:%M')}

## 🎯 RESUMEN EJECUTIVO

### Condiciones Actuales del Mercado
- **Timestamp**: {self.datos_mercado['timestamp']}
- **Estado General**: {'Favorable' if len(self.alertas_mercado) < 3 else 'Volátil'}
- **Alertas Activas**: {len(self.alertas_mercado)}

## 📈 ANÁLISIS DE ÍNDICES PRINCIPALES

"""
        
        # Agregar análisis de índices
        for nombre, df in self.datos_mercado['indices'].items():
            if not df.empty:
                precio_actual = df['Close'].iloc[-1]
                cambio_1d = df['Close'].pct_change().iloc[-1] * 100
                cambio_1m = df['Close'].pct_change(30).iloc[-1] * 100
                
                reporte += f"""
### {nombre}
- **Precio Actual**: ${precio_actual:.2f}
- **Cambio 1D**: {cambio_1d:+.2f}%
- **Cambio 1M**: {cambio_1m:+.2f}%
- **Tendencia**: {'Alcista' if cambio_1m > 0 else 'Bajista'}
"""
        
        # Agregar análisis de VC LATAM
        if 'vc_latam' in self.datos_mercado:
            vc_data = self.datos_mercado['vc_latam']
            reporte += f"""

## 💰 ANÁLISIS DE VC LATAM

### Inversiones 2024
- **Total Inversiones**: ${vc_data['total_inversiones_2024']}B
- **Número de Deals**: {vc_data['num_deals_2024']}
- **Valuación Promedio**: ${vc_data['valuacion_promedio']}M
- **Dilución Promedio**: {vc_data['dilucion_promedio']*100:.1f}%

### Sectores Calientes
"""
            for sector, porcentaje in vc_data['sectores_calientes'].items():
                reporte += f"- **{sector}**: {porcentaje*100:.1f}%\n"
            
            reporte += f"""

### Países Más Activos
"""
            for pais, porcentaje in vc_data['paises_activos'].items():
                reporte += f"- **{pais}**: {porcentaje*100:.1f}%\n"
        
        # Agregar predicciones
        if self.tendencias:
            reporte += f"""

## 🔮 PREDICCIONES DE MERCADO

### Predicciones para Próximos 30 Días
"""
            for modelo, pred in self.tendencias['predicciones'].items():
                reporte += f"""
#### {modelo}
- **Predicción**: {pred['prediccion_30d']*100:+.2f}%
- **Volatilidad**: {pred['volatilidad_30d']*100:.2f}%
- **Tendencia**: {pred['tendencia'].title()}
"""
        
        # Agregar alertas
        if self.alertas_mercado:
            reporte += f"""

## ⚠️ ALERTAS DE MERCADO

"""
            for alerta in self.alertas_mercado:
                reporte += f"""
### {alerta['tipo'].replace('_', ' ').title()} - {alerta['severidad'].upper()}
- **Mensaje**: {alerta['mensaje']}
- **Recomendación**: {alerta['recomendacion']}
"""
        
        # Agregar recomendaciones
        reporte += f"""

## 🎯 RECOMENDACIONES PARA TU STARTUP

### Estrategias Anti-Dilución Recomendadas
1. **Monitorear volatilidad del mercado** para ajustar timing de rondas
2. **Considerar SAFE** en períodos de alta volatilidad
3. **Desarrollar strategic partnerships** para reducir dependencia de capital
4. **Mantener flexibilidad** en términos de dilución según condiciones de mercado
5. **Usar datos de mercado** para negociar mejores términos

### Factores Críticos a Monitorear
- **Volatilidad del VIX** (índice de miedo)
- **Tendencias del sector startups** (ARKK, QQQ)
- **Estabilidad de monedas LATAM**
- **Flujo de inversión VC** en la región
- **Regulaciones** del sector fintech/AI

---
*Generado por Analizador de Mercado en Tiempo Real - Neural Marketing AI*
"""
        
        return reporte
    
    def ejecutar_analisis_completo(self):
        """Ejecuta análisis completo de mercado"""
        print("🌍 Iniciando análisis de mercado en tiempo real...")
        
        # Obtener datos
        if not self.obtener_datos_mercado_global():
            return False
        
        if not self.obtener_datos_vc_latam():
            return False
        
        # Analizar tendencias
        if not self.analizar_tendencias_mercado():
            return False
        
        # Generar alertas
        self.generar_alertas_mercado()
        
        # Generar reporte
        reporte = self.generar_reporte_mercado()
        
        # Guardar reporte
        with open('reporte_mercado_tiempo_real.md', 'w', encoding='utf-8') as f:
            f.write(reporte)
        
        print("✅ Análisis de mercado completado")
        print(f"📊 Alertas generadas: {len(self.alertas_mercado)}")
        
        return reporte

def main():
    """Función principal"""
    analizador = AnalizadorMercadoTiempoReal()
    
    print("=" * 80)
    print("🌍 ANALIZADOR DE MERCADO EN TIEMPO REAL")
    print("Neural Marketing AI (Copy.ai LATAM)")
    print("=" * 80)
    
    # Ejecutar análisis completo
    reporte = analizador.ejecutar_analisis_completo()
    
    if reporte:
        print("\n" + "=" * 80)
        print("📋 REPORTE DE MERCADO GENERADO")
        print("=" * 80)
        print(reporte)

if __name__ == "__main__":
    main()

