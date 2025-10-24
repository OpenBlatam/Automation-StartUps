# 🛠️ Herramientas Prácticas Mejoradas

## 🚀 Calculadoras Avanzadas

### 1. **Calculadora de ROI Completa**
```python
# calculadora_roi_completa.py
class CalculadoraROICompleta:
    def __init__(self):
        self.metricas = {}
        self.escenarios = {}
    
    def calcular_roi_completo(self, datos_empresa):
        """Calcula ROI completo con múltiples escenarios"""
        # Escenario Base
        escenario_base = self._calcular_escenario_base(datos_empresa)
        
        # Escenario Optimista
        escenario_optimista = self._calcular_escenario_optimista(datos_empresa)
        
        # Escenario Pesimista
        escenario_pesimista = self._calcular_escenario_pesimista(datos_empresa)
        
        # Análisis de Sensibilidad
        sensibilidad = self._analizar_sensibilidad(datos_empresa)
        
        return {
            'escenario_base': escenario_base,
            'escenario_optimista': escenario_optimista,
            'escenario_pesimista': escenario_pesimista,
            'sensibilidad': sensibilidad,
            'recomendaciones': self._generar_recomendaciones(escenario_base)
        }
    
    def _calcular_escenario_base(self, datos):
        """Calcula escenario base"""
        inversion = datos['inversion_inicial']
        ahorro_mensual = datos['ahorro_mensual']
        meses = datos['periodo_analisis']
        
        beneficio_total = ahorro_mensual * meses
        roi = ((beneficio_total - inversion) / inversion) * 100
        payback = inversion / ahorro_mensual
        
        return {
            'inversion': inversion,
            'beneficio_total': beneficio_total,
            'roi': roi,
            'payback_meses': payback,
            'van': self._calcular_van(inversion, ahorro_mensual, meses, 0.1)
        }
    
    def _calcular_van(self, inversion, flujo_mensual, meses, tasa_descuento):
        """Calcula Valor Actual Neto"""
        van = -inversion
        for mes in range(1, meses + 1):
            van += flujo_mensual / ((1 + tasa_descuento/12) ** mes)
        return van
    
    def _analizar_sensibilidad(self, datos):
        """Analiza sensibilidad de variables clave"""
        variables = ['churn_rate', 'ltv', 'cac', 'retention_rate']
        sensibilidad = {}
        
        for variable in variables:
            if variable in datos:
                valor_base = datos[variable]
                variaciones = [-0.2, -0.1, 0, 0.1, 0.2]  # ±20%, ±10%
                impactos = []
                
                for variacion in variaciones:
                    nuevo_valor = valor_base * (1 + variacion)
                    datos_temp = datos.copy()
                    datos_temp[variable] = nuevo_valor
                    
                    escenario = self._calcular_escenario_base(datos_temp)
                    impactos.append({
                        'variacion': variacion * 100,
                        'nuevo_valor': nuevo_valor,
                        'roi': escenario['roi']
                    })
                
                sensibilidad[variable] = impactos
        
        return sensibilidad
```

### 2. **Simulador de Escenarios de Retención**
```python
# simulador_escenarios_retencion.py
class SimuladorEscenariosRetencion:
    def __init__(self):
        self.escenarios = {
            'conservador': {'mejora_churn': 0.1, 'mejora_ltv': 0.15},
            'moderado': {'mejora_churn': 0.2, 'mejora_ltv': 0.25},
            'agresivo': {'mejora_churn': 0.3, 'mejora_ltv': 0.35}
        }
    
    def simular_escenarios(self, datos_base):
        """Simula diferentes escenarios de retención"""
        resultados = {}
        
        for nombre, config in self.escenarios.items():
            # Aplicar mejoras
            churn_nuevo = datos_base['churn_rate'] * (1 - config['mejora_churn'])
            ltv_nuevo = datos_base['ltv'] * (1 + config['mejora_ltv'])
            
            # Calcular métricas
            clientes_retidos = datos_base['clientes_totales'] * (1 - churn_nuevo)
            ingresos_nuevos = clientes_retidos * ltv_nuevo
            ingresos_actuales = datos_base['clientes_totales'] * datos_base['ltv']
            
            mejora_ingresos = ((ingresos_nuevos - ingresos_actuales) / ingresos_actuales) * 100
            
            resultados[nombre] = {
                'churn_rate': churn_nuevo,
                'ltv': ltv_nuevo,
                'clientes_retidos': clientes_retidos,
                'ingresos_nuevos': ingresos_nuevos,
                'mejora_ingresos': mejora_ingresos,
                'roi_estimado': self._calcular_roi_escenario(config, datos_base)
            }
        
        return resultados
    
    def _calcular_roi_escenario(self, config, datos):
        """Calcula ROI para un escenario específico"""
        inversion_requerida = datos['inversion_estimada'] * (1 + config['mejora_churn'])
        beneficio_anual = datos['ingresos_actuales'] * (config['mejora_churn'] + config['mejora_ltv'])
        
        return (beneficio_anual - inversion_requerida) / inversion_requerida * 100
```

### 3. **Optimizador de Campañas de Email**
```python
# optimizador_campanas_email.py
class OptimizadorCampanasEmail:
    def __init__(self):
        self.templates = {
            'bienvenida': {
                'asunto': 'Bienvenido a {producto}',
                'contenido': 'Hola {nombre}, bienvenido...',
                'cta': 'Comenzar ahora'
            },
            'seguimiento': {
                'asunto': '¿Cómo va tu experiencia?',
                'contenido': 'Hola {nombre}, ¿cómo va...',
                'cta': 'Explorar funciones'
            },
            'win_back': {
                'asunto': 'Te extrañamos en {producto}',
                'contenido': 'Hola {nombre}, notamos que...',
                'cta': 'Volver ahora'
            }
        }
    
    def optimizar_campana(self, tipo_campana, datos_audiencia):
        """Optimiza una campaña de email"""
        template = self.templates[tipo_campana]
        
        # Generar variaciones de asunto
        asuntos = self._generar_variaciones_asunto(template['asunto'], datos_audiencia)
        
        # Generar variaciones de contenido
        contenidos = self._generar_variaciones_contenido(template['contenido'], datos_audiencia)
        
        # Generar variaciones de CTA
        ctas = self._generar_variaciones_cta(template['cta'])
        
        # Combinar variaciones
        combinaciones = self._combinar_variaciones(asuntos, contenidos, ctas)
        
        # Predecir rendimiento
        predicciones = self._predecir_rendimiento(combinaciones, datos_audiencia)
        
        # Seleccionar mejores
        mejores = sorted(predicciones, key=lambda x: x['score'], reverse=True)[:5]
        
        return {
            'mejores_combinaciones': mejores,
            'metricas_esperadas': self._calcular_metricas_esperadas(mejores),
            'recomendaciones': self._generar_recomendaciones(mejores)
        }
    
    def _generar_variaciones_asunto(self, asunto_base, audiencia):
        """Genera variaciones de asunto"""
        variaciones = [asunto_base]
        
        # Agregar emojis
        variaciones.append(f"🚀 {asunto_base}")
        variaciones.append(f"✨ {asunto_base}")
        
        # Agregar urgencia
        variaciones.append(f"¡{asunto_base}!")
        variaciones.append(f"{asunto_base} - Solo hoy")
        
        # Personalizar por audiencia
        if audiencia['segmento'] == 'nuevos':
            variaciones.append(f"¡{asunto_base} - Tu guía completa!")
        elif audiencia['segmento'] == 'en_riesgo':
            variaciones.append(f"¡{asunto_base} - Última oportunidad!")
        
        return variaciones
    
    def _predecir_rendimiento(self, combinaciones, audiencia):
        """Predice rendimiento de combinaciones"""
        predicciones = []
        
        for combo in combinaciones:
            # Factores de predicción
            factor_asunto = self._calcular_factor_asunto(combo['asunto'])
            factor_contenido = self._calcular_factor_contenido(combo['contenido'])
            factor_cta = self._calcular_factor_cta(combo['cta'])
            factor_audiencia = self._calcular_factor_audiencia(audiencia)
            
            # Score combinado
            score = (factor_asunto * 0.3 + 
                    factor_contenido * 0.4 + 
                    factor_cta * 0.2 + 
                    factor_audiencia * 0.1)
            
            predicciones.append({
                'asunto': combo['asunto'],
                'contenido': combo['contenido'],
                'cta': combo['cta'],
                'score': score,
                'open_rate_esperado': score * 0.3,
                'click_rate_esperado': score * 0.1,
                'conversion_rate_esperado': score * 0.05
            })
        
        return predicciones
```

## 📊 Dashboards Interactivos

### 1. **Dashboard de Retención en Tiempo Real**
```python
# dashboard_retencion_tiempo_real.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta

class DashboardRetencionTiempoReal:
    def __init__(self):
        self.metricas = {}
        self.alertas = []
    
    def crear_dashboard(self, datos):
        """Crea dashboard interactivo de retención"""
        # Calcular métricas
        self._calcular_metricas(datos)
        
        # Crear subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Tasa de Churn en Tiempo Real',
                'Distribución de Salud de Clientes',
                'Ingresos por Segmento',
                'Tendencia de Retención',
                'Análisis de Cohortes',
                'Alertas y Recomendaciones'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "histogram"}],
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "heatmap"}, {"type": "table"}]
            ]
        )
        
        # Agregar gráficos
        self._agregar_grafico_churn(fig, datos, 1, 1)
        self._agregar_grafico_salud(fig, datos, 1, 2)
        self._agregar_grafico_ingresos(fig, datos, 2, 1)
        self._agregar_grafico_tendencia(fig, datos, 2, 2)
        self._agregar_grafico_cohortes(fig, datos, 3, 1)
        self._agregar_tabla_alertas(fig, 3, 2)
        
        # Actualizar layout
        fig.update_layout(
            height=1200,
            title_text="Dashboard de Retención en Tiempo Real",
            showlegend=False
        )
        
        return fig
    
    def _calcular_metricas(self, datos):
        """Calcula métricas clave"""
        self.metricas = {
            'churn_rate': datos['churn_rate'].mean(),
            'retention_rate': 1 - datos['churn_rate'].mean(),
            'ltv_promedio': datos['ltv'].mean(),
            'nps_promedio': datos['nps'].mean(),
            'clientes_activos': len(datos[datos['activo'] == True]),
            'ingresos_mensuales': datos['ingresos_mensuales'].sum()
        }
    
    def _agregar_grafico_churn(self, fig, datos, row, col):
        """Agrega gráfico de churn en tiempo real"""
        # Agrupar por día
        datos_diarios = datos.groupby('fecha')['churn_rate'].mean()
        
        fig.add_trace(
            go.Scatter(
                x=datos_diarios.index,
                y=datos_diarios.values,
                mode='lines+markers',
                name='Churn Rate',
                line=dict(color='red', width=3)
            ),
            row=row, col=col
        )
    
    def _agregar_grafico_salud(self, fig, datos, row, col):
        """Agrega gráfico de distribución de salud"""
        fig.add_trace(
            go.Histogram(
                x=datos['health_score'],
                nbinsx=20,
                name='Distribución de Salud',
                marker_color='lightblue'
            ),
            row=row, col=col
        )
    
    def _agregar_grafico_ingresos(self, fig, datos, row, col):
        """Agrega gráfico de ingresos por segmento"""
        ingresos_por_segmento = datos.groupby('segmento')['ingresos_mensuales'].sum()
        
        fig.add_trace(
            go.Bar(
                x=ingresos_por_segmento.index,
                y=ingresos_por_segmento.values,
                name='Ingresos por Segmento',
                marker_color='green'
            ),
            row=row, col=col
        )
    
    def _agregar_grafico_tendencia(self, fig, datos, row, col):
        """Agrega gráfico de tendencia de retención"""
        tendencia = datos.groupby('fecha')['retention_rate'].mean()
        
        fig.add_trace(
            go.Scatter(
                x=tendencia.index,
                y=tendencia.values,
                mode='lines+markers',
                name='Tendencia de Retención',
                line=dict(color='blue', width=3)
            ),
            row=row, col=col
        )
    
    def _agregar_grafico_cohortes(self, fig, datos, row, col):
        """Agrega gráfico de análisis de cohortes"""
        # Crear matriz de cohortes
        cohortes = self._calcular_cohortes(datos)
        
        fig.add_trace(
            go.Heatmap(
                z=cohortes.values,
                x=cohortes.columns,
                y=cohortes.index,
                colorscale='Blues',
                name='Análisis de Cohortes'
            ),
            row=row, col=col
        )
    
    def _agregar_tabla_alertas(self, fig, row, col):
        """Agrega tabla de alertas y recomendaciones"""
        alertas = self._generar_alertas()
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Tipo', 'Mensaje', 'Prioridad', 'Acción']),
                cells=dict(values=[
                    [alerta['tipo'] for alerta in alertas],
                    [alerta['mensaje'] for alerta in alertas],
                    [alerta['prioridad'] for alerta in alertas],
                    [alerta['accion'] for alerta in alertas]
                ])
            ),
            row=row, col=col
        )
    
    def _calcular_cohortes(self, datos):
        """Calcula análisis de cohortes"""
        # Implementar lógica de cohortes
        pass
    
    def _generar_alertas(self):
        """Genera alertas basadas en métricas"""
        alertas = []
        
        if self.metricas['churn_rate'] > 0.1:
            alertas.append({
                'tipo': 'Crítico',
                'mensaje': 'Tasa de churn alta',
                'prioridad': 'Alta',
                'accion': 'Revisar estrategias inmediatamente'
            })
        
        if self.metricas['nps_promedio'] < 7:
            alertas.append({
                'tipo': 'Advertencia',
                'mensaje': 'NPS bajo',
                'prioridad': 'Media',
                'accion': 'Mejorar satisfacción del cliente'
            })
        
        return alertas
```

### 2. **Dashboard de Análisis Predictivo**
```python
# dashboard_analisis_predictivo.py
class DashboardAnalisisPredictivo:
    def __init__(self):
        self.modelos = {}
        self.predicciones = {}
    
    def crear_dashboard_predictivo(self, datos_historicos, horizonte_meses=6):
        """Crea dashboard de análisis predictivo"""
        # Entrenar modelos
        self._entrenar_modelos(datos_historicos)
        
        # Generar predicciones
        predicciones = self._generar_predicciones(horizonte_meses)
        
        # Crear visualizaciones
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Predicción de Churn',
                'Predicción de LTV',
                'Predicción de Ingresos',
                'Análisis de Riesgo'
            )
        )
        
        # Agregar gráficos predictivos
        self._agregar_prediccion_churn(fig, predicciones, 1, 1)
        self._agregar_prediccion_ltv(fig, predicciones, 1, 2)
        self._agregar_prediccion_ingresos(fig, predicciones, 2, 1)
        self._agregar_analisis_riesgo(fig, predicciones, 2, 2)
        
        return fig
    
    def _entrenar_modelos(self, datos):
        """Entrena modelos de predicción"""
        # Implementar entrenamiento de modelos
        pass
    
    def _generar_predicciones(self, horizonte):
        """Genera predicciones para el horizonte especificado"""
        # Implementar generación de predicciones
        pass
```

## 🎯 Herramientas de Automatización

### 1. **Automatizador de Campañas**
```python
# automatizador_campanas.py
class AutomatizadorCampanas:
    def __init__(self):
        self.campanas_activas = {}
        self.triggers = {}
        self.acciones = {}
    
    def crear_campana_automatizada(self, nombre, configuracion):
        """Crea una campaña automatizada"""
        campana = {
            'nombre': nombre,
            'triggers': configuracion['triggers'],
            'acciones': configuracion['acciones'],
            'condiciones': configuracion['condiciones'],
            'activa': True,
            'fecha_creacion': datetime.now()
        }
        
        self.campanas_activas[nombre] = campana
        return campana
    
    def ejecutar_campana(self, nombre_campana, datos_cliente):
        """Ejecuta una campaña para un cliente específico"""
        campana = self.campanas_activas.get(nombre_campana)
        if not campana or not campana['activa']:
            return False
        
        # Verificar triggers
        if self._verificar_triggers(campana['triggers'], datos_cliente):
            # Verificar condiciones
            if self._verificar_condiciones(campana['condiciones'], datos_cliente):
                # Ejecutar acciones
                return self._ejecutar_acciones(campana['acciones'], datos_cliente)
        
        return False
    
    def _verificar_triggers(self, triggers, datos_cliente):
        """Verifica si se activan los triggers"""
        for trigger in triggers:
            if trigger['tipo'] == 'churn_risk' and datos_cliente['churn_probability'] > trigger['umbral']:
                return True
            elif trigger['tipo'] == 'health_score' and datos_cliente['health_score'] < trigger['umbral']:
                return True
            elif trigger['tipo'] == 'inactivity' and datos_cliente['dias_inactivo'] > trigger['dias']:
                return True
        
        return False
    
    def _ejecutar_acciones(self, acciones, datos_cliente):
        """Ejecuta las acciones de la campaña"""
        resultados = []
        
        for accion in acciones:
            if accion['tipo'] == 'email':
                resultado = self._enviar_email(accion, datos_cliente)
            elif accion['tipo'] == 'sms':
                resultado = self._enviar_sms(accion, datos_cliente)
            elif accion['tipo'] == 'call':
                resultado = self._programar_llamada(accion, datos_cliente)
            elif accion['tipo'] == 'discount':
                resultado = self._aplicar_descuento(accion, datos_cliente)
            
            resultados.append(resultado)
        
        return resultados
```

### 2. **Optimizador de Horarios de Envío**
```python
# optimizador_horarios_envio.py
class OptimizadorHorariosEnvio:
    def __init__(self):
        self.horarios_optimos = {}
        self.datos_historicos = {}
    
    def analizar_horarios_optimos(self, datos_envios):
        """Analiza los horarios óptimos de envío"""
        # Agrupar por hora del día
        por_hora = datos_envios.groupby('hora_envio').agg({
            'open_rate': 'mean',
            'click_rate': 'mean',
            'conversion_rate': 'mean'
        })
        
        # Calcular score combinado
        por_hora['score'] = (
            por_hora['open_rate'] * 0.4 +
            por_hora['click_rate'] * 0.3 +
            por_hora['conversion_rate'] * 0.3
        )
        
        # Encontrar mejores horarios
        mejores_horarios = por_hora.nlargest(3, 'score')
        
        return {
            'mejores_horarios': mejores_horarios.index.tolist(),
            'score_promedio': mejores_horarios['score'].mean(),
            'recomendaciones': self._generar_recomendaciones_horarios(mejores_horarios)
        }
    
    def _generar_recomendaciones_horarios(self, mejores_horarios):
        """Genera recomendaciones de horarios"""
        recomendaciones = []
        
        for hora in mejores_horarios.index:
            if 9 <= hora <= 11:
                recomendaciones.append(f"Mañana temprano ({hora}:00) - Ideal para emails de trabajo")
            elif 14 <= hora <= 16:
                recomendaciones.append(f"Tarde ({hora}:00) - Bueno para seguimientos")
            elif 19 <= hora <= 21:
                recomendaciones.append(f"Noche ({hora}:00) - Perfecto para emails personales")
        
        return recomendaciones
```

## 📈 Herramientas de Análisis Avanzado

### 1. **Analizador de Sentimientos**
```python
# analizador_sentimientos.py
class AnalizadorSentimientos:
    def __init__(self):
        self.modelo = None
        self.entrenar_modelo()
    
    def entrenar_modelo(self):
        """Entrena modelo de análisis de sentimientos"""
        # Implementar entrenamiento del modelo
        pass
    
    def analizar_sentimiento(self, texto):
        """Analiza el sentimiento de un texto"""
        # Implementar análisis de sentimientos
        pass
    
    def analizar_feedback_clientes(self, feedbacks):
        """Analiza el sentimiento de feedbacks de clientes"""
        resultados = []
        
        for feedback in feedbacks:
            sentimiento = self.analizar_sentimiento(feedback['texto'])
            resultados.append({
                'cliente_id': feedback['cliente_id'],
                'texto': feedback['texto'],
                'sentimiento': sentimiento['sentimiento'],
                'confianza': sentimiento['confianza'],
                'accion_recomendada': self._recomendar_accion(sentimiento)
            })
        
        return resultados
    
    def _recomendar_accion(self, sentimiento):
        """Recomienda acción basada en sentimiento"""
        if sentimiento['sentimiento'] == 'negativo' and sentimiento['confianza'] > 0.8:
            return 'Contactar inmediatamente'
        elif sentimiento['sentimiento'] == 'neutral' and sentimiento['confianza'] > 0.6:
            return 'Seguimiento en 1 semana'
        elif sentimiento['sentimiento'] == 'positivo' and sentimiento['confianza'] > 0.8:
            return 'Solicitar testimonio'
        else:
            return 'Monitorear'
```

### 2. **Detector de Anomalías**
```python
# detector_anomalias.py
class DetectorAnomalias:
    def __init__(self):
        self.umbrales = {
            'churn_rate': 0.15,  # 15% churn rate
            'health_score': 30,   # Health score < 30
            'nps': 5,            # NPS < 5
            'ltv': 0.5           # LTV < 50% del promedio
        }
    
    def detectar_anomalias(self, datos):
        """Detecta anomalías en los datos"""
        anomalias = []
        
        # Anomalías en churn rate
        churn_anomalias = self._detectar_churn_anomalias(datos)
        anomalias.extend(churn_anomalias)
        
        # Anomalías en health score
        health_anomalias = self._detectar_health_anomalias(datos)
        anomalias.extend(health_anomalias)
        
        # Anomalías en NPS
        nps_anomalias = self._detectar_nps_anomalias(datos)
        anomalias.extend(nps_anomalias)
        
        # Anomalías en LTV
        ltv_anomalias = self._detectar_ltv_anomalias(datos)
        anomalias.extend(ltv_anomalias)
        
        return anomalias
    
    def _detectar_churn_anomalias(self, datos):
        """Detecta anomalías en churn rate"""
        anomalias = []
        
        churn_por_segmento = datos.groupby('segmento')['churn_rate'].mean()
        
        for segmento, churn_rate in churn_por_segmento.items():
            if churn_rate > self.umbrales['churn_rate']:
                anomalias.append({
                    'tipo': 'churn_rate',
                    'segmento': segmento,
                    'valor': churn_rate,
                    'umbral': self.umbrales['churn_rate'],
                    'severidad': 'alta' if churn_rate > 0.25 else 'media',
                    'accion': 'Revisar estrategias de retención para este segmento'
                })
        
        return anomalias
```

---

## 🚀 Implementación Rápida

### 1. **Script de Configuración Inicial**
```bash
#!/bin/bash
# setup_herramientas_mejoradas.sh

echo "🚀 Configurando Herramientas Mejoradas de Retención..."

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
python setup_database.py

# Importar datos de ejemplo
python import_sample_data.py

# Configurar modelos de IA
python setup_ai_models.py

# Iniciar dashboard
python start_dashboard.py

echo "✅ Configuración completada!"
echo "🌐 Dashboard disponible en: http://localhost:8080"
echo "📊 API disponible en: http://localhost:8000"
```

### 2. **Docker Compose para Despliegue**
```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/retention
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=retention
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6
    ports:
      - "6379:6379"
  
  dashboard:
    build: .
    ports:
      - "8080:8080"
    environment:
      - API_URL=http://web:8000
    depends_on:
      - web

volumes:
  postgres_data:
```

---

*Estas herramientas mejoradas proporcionan capacidades avanzadas de análisis, automatización y optimización para maximizar la retención de clientes en SaaS.*
