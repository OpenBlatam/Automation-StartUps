#!/usr/bin/env python3
"""
SISTEMA DE SEGUIMIENTO COPYCAR - MONITOREO CONTINUO ANTI-DILUCIÓN
================================================================

Sistema de seguimiento continuo para estrategias anti-dilución con:
- Monitoreo en tiempo real de métricas clave
- Alertas automáticas de dilución
- Dashboard de seguimiento ejecutivo
- Análisis de tendencias y patrones
- Reportes automáticos programados
- Integración con sistemas externos

Autor: Sistema Neural Avanzado
Versión: 2.0 - Ultra Avanzada
Fecha: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import schedule
import time
import json
import warnings
warnings.filterwarnings('ignore')

class SistemaSeguimientoCopycar:
    def __init__(self):
        self.nombre = "SISTEMA DE SEGUIMIENTO COPYCAR"
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
        
        # Métricas de seguimiento
        self.metricas_historicas = []
        self.alertas_activas = []
        self.tendencias = {}
        
        # Umbrales de alerta
        self.umbrales = {
            'dilucion_critica': 20,
            'dilucion_alta': 15,
            'dilucion_media': 10,
            'dilucion_baja': 5,
            'volatilidad_alta': 0.3,
            'volatilidad_media': 0.2
        }
        
        print(f"🔍 {self.nombre} - {self.version}")
        print(f"📅 Iniciado: {self.fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

    def capturar_metricas_tiempo_real(self, datos_empresa):
        """
        Captura métricas en tiempo real para monitoreo continuo
        """
        timestamp = datetime.now()
        
        # Simular captura de datos reales
        valoracion_actual = datos_empresa.get('valoracion_actual', 1000000)
        inversion_actual = datos_empresa.get('inversion_actual', 100000)
        acciones_totales = datos_empresa.get('acciones_totales', 1000000)
        
        # Calcular métricas clave
        valor_por_accion = valoracion_actual / acciones_totales
        porcentaje_actual = (inversion_actual / valoracion_actual) * 100
        
        # Simular variaciones de mercado
        variacion_mercado = np.random.normal(0, 0.05)  # 5% de volatilidad
        nueva_valoracion = valoracion_actual * (1 + variacion_mercado)
        
        # Simular dilución potencial
        dilucion_potencial = np.random.uniform(0, 25)
        
        # Calcular impacto de dilución
        if dilucion_potencial > 0:
            nuevas_acciones = acciones_totales * (1 + dilucion_potencial/100)
            nuevo_valor_por_accion = nueva_valoracion / nuevas_acciones
            perdida_valor = ((valor_por_accion - nuevo_valor_por_accion) / valor_por_accion) * 100
        else:
            perdida_valor = 0
        
        # Crear registro de métricas
        metricas = {
            'timestamp': timestamp,
            'valoracion_actual': nueva_valoracion,
            'valor_por_accion': valor_por_accion,
            'porcentaje_actual': porcentaje_actual,
            'dilucion_potencial': dilucion_potencial,
            'perdida_valor': perdida_valor,
            'volatilidad': abs(variacion_mercado),
            'tendencia': 'ALCISTA' if variacion_mercado > 0 else 'BAJISTA'
        }
        
        # Agregar a historial
        self.metricas_historicas.append(metricas)
        
        return metricas

    def analizar_tendencias(self, ventana_dias=30):
        """
        Analiza tendencias en las métricas históricas
        """
        if len(self.metricas_historicas) < 2:
            return {}
        
        # Convertir a DataFrame
        df = pd.DataFrame(self.metricas_historicas)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filtrar últimos N días
        fecha_limite = datetime.now() - timedelta(days=ventana_dias)
        df_reciente = df[df['timestamp'] >= fecha_limite]
        
        if len(df_reciente) < 2:
            return {}
        
        # Calcular tendencias
        tendencias = {}
        
        # Tendencia de valoración
        valoracion_tendencia = np.polyfit(range(len(df_reciente)), df_reciente['valoracion_actual'], 1)[0]
        tendencias['valoracion'] = {
            'pendiente': valoracion_tendencia,
            'direccion': 'ALCISTA' if valoracion_tendencia > 0 else 'BAJISTA',
            'fuerza': abs(valoracion_tendencia)
        }
        
        # Tendencia de dilución
        dilucion_tendencia = np.polyfit(range(len(df_reciente)), df_reciente['dilucion_potencial'], 1)[0]
        tendencias['dilucion'] = {
            'pendiente': dilucion_tendencia,
            'direccion': 'AUMENTANDO' if dilucion_tendencia > 0 else 'DISMINUYENDO',
            'fuerza': abs(dilucion_tendencia)
        }
        
        # Volatilidad promedio
        volatilidad_promedio = df_reciente['volatilidad'].mean()
        tendencias['volatilidad'] = {
            'promedio': volatilidad_promedio,
            'nivel': 'ALTA' if volatilidad_promedio > self.umbrales['volatilidad_alta'] else 
                    'MEDIA' if volatilidad_promedio > self.umbrales['volatilidad_media'] else 'BAJA'
        }
        
        # Frecuencia de alertas
        alertas_recientes = len([m for m in self.metricas_historicas 
                               if m['dilucion_potencial'] > self.umbrales['dilucion_media']])
        tendencias['alertas'] = {
            'frecuencia': alertas_recientes,
            'nivel': 'ALTA' if alertas_recientes > 5 else 'MEDIA' if alertas_recientes > 2 else 'BAJA'
        }
        
        self.tendencias = tendencias
        return tendencias

    def evaluar_alertas(self, metricas):
        """
        Evalúa si se deben generar alertas basadas en las métricas actuales
        """
        alertas = []
        
        # Alerta por dilución crítica
        if metricas['dilucion_potencial'] >= self.umbrales['dilucion_critica']:
            alertas.append({
                'tipo': 'DILUCIÓN CRÍTICA',
                'nivel': 'CRÍTICO',
                'mensaje': f'Dilución crítica detectada: {metricas["dilucion_potencial"]:.2f}%',
                'accion': 'ACCIÓN INMEDIATA REQUERIDA',
                'timestamp': metricas['timestamp']
            })
        
        # Alerta por dilución alta
        elif metricas['dilucion_potencial'] >= self.umbrales['dilucion_alta']:
            alertas.append({
                'tipo': 'DILUCIÓN ALTA',
                'nivel': 'ALTO',
                'mensaje': f'Dilución alta detectada: {metricas["dilucion_potencial"]:.2f}%',
                'accion': 'REVISIÓN URGENTE',
                'timestamp': metricas['timestamp']
            })
        
        # Alerta por volatilidad alta
        if metricas['volatilidad'] >= self.umbrales['volatilidad_alta']:
            alertas.append({
                'tipo': 'VOLATILIDAD ALTA',
                'nivel': 'MEDIO',
                'mensaje': f'Volatilidad alta detectada: {metricas["volatilidad"]:.2f}',
                'accion': 'MONITOREO AUMENTADO',
                'timestamp': metricas['timestamp']
            })
        
        # Alerta por pérdida de valor significativa
        if metricas['perdida_valor'] > 10:
            alertas.append({
                'tipo': 'PÉRDIDA DE VALOR',
                'nivel': 'ALTO',
                'mensaje': f'Pérdida de valor significativa: {metricas["perdida_valor"]:.2f}%',
                'accion': 'ANÁLISIS INMEDIATO',
                'timestamp': metricas['timestamp']
            })
        
        # Agregar alertas a la lista activa
        for alerta in alertas:
            self.alertas_activas.append(alerta)
        
        return alertas

    def crear_dashboard_seguimiento(self):
        """
        Crea un dashboard de seguimiento en tiempo real
        """
        if len(self.metricas_historicas) < 2:
            print("⚠️  Insuficientes datos para crear dashboard")
            return
        
        # Configurar el estilo
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('DASHBOARD DE SEGUIMIENTO - MONITOREO CONTINUO', fontsize=16, fontweight='bold')
        
        # Convertir a DataFrame
        df = pd.DataFrame(self.metricas_historicas)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Gráfico 1: Evolución de valoración
        ax1 = axes[0, 0]
        ax1.plot(df['timestamp'], df['valoracion_actual'], 
                marker='o', linewidth=2, markersize=4, color=self.colores['primario'])
        ax1.set_title('Evolución de Valoración', fontweight='bold')
        ax1.set_xlabel('Tiempo')
        ax1.set_ylabel('Valoración ($)')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Dilución potencial
        ax2 = axes[0, 1]
        colores_dilucion = [self.colores['exito'] if x < self.umbrales['dilucion_media'] else 
                           self.colores['advertencia'] if x < self.umbrales['dilucion_alta'] else 
                           self.colores['advertencia'] for x in df['dilucion_potencial']]
        ax2.bar(range(len(df)), df['dilucion_potencial'], color=colores_dilucion, alpha=0.7)
        ax2.set_title('Dilución Potencial', fontweight='bold')
        ax2.set_xlabel('Mediciones')
        ax2.set_ylabel('Dilución (%)')
        ax2.axhline(y=self.umbrales['dilucion_media'], color='orange', linestyle='--', alpha=0.7, label='Umbral Medio')
        ax2.axhline(y=self.umbrales['dilucion_alta'], color='red', linestyle='--', alpha=0.7, label='Umbral Alto')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Pérdida de valor
        ax3 = axes[1, 0]
        ax3.plot(df['timestamp'], df['perdida_valor'], 
                marker='s', linewidth=2, markersize=4, color=self.colores['advertencia'])
        ax3.set_title('Pérdida de Valor por Dilución', fontweight='bold')
        ax3.set_xlabel('Tiempo')
        ax3.set_ylabel('Pérdida de Valor (%)')
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, alpha=0.3)
        ax3.fill_between(df['timestamp'], df['perdida_valor'], alpha=0.3, color=self.colores['advertencia'])
        
        # Gráfico 4: Volatilidad
        ax4 = axes[1, 1]
        ax4.plot(df['timestamp'], df['volatilidad'], 
                marker='^', linewidth=2, markersize=4, color=self.colores['info'])
        ax4.set_title('Volatilidad del Mercado', fontweight='bold')
        ax4.set_xlabel('Tiempo')
        ax4.set_ylabel('Volatilidad')
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(True, alpha=0.3)
        ax4.axhline(y=self.umbrales['volatilidad_media'], color='orange', linestyle='--', alpha=0.7)
        ax4.axhline(y=self.umbrales['volatilidad_alta'], color='red', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.show()
        
        print("✅ Dashboard de seguimiento generado exitosamente")

    def generar_reporte_seguimiento(self):
        """
        Genera un reporte de seguimiento con análisis de tendencias
        """
        print("\n📊 GENERANDO REPORTE DE SEGUIMIENTO")
        print("=" * 50)
        
        # Analizar tendencias
        tendencias = self.analizar_tendencias()
        
        # Calcular métricas del reporte
        if self.metricas_historicas:
            ultima_metrica = self.metricas_historicas[-1]
            total_mediciones = len(self.metricas_historicas)
            alertas_activas = len(self.alertas_activas)
            
            # Calcular promedios
            df = pd.DataFrame(self.metricas_historicas)
            dilucion_promedio = df['dilucion_potencial'].mean()
            volatilidad_promedio = df['volatilidad'].mean()
            perdida_promedio = df['perdida_valor'].mean()
        else:
            ultima_metrica = {}
            total_mediciones = 0
            alertas_activas = 0
            dilucion_promedio = 0
            volatilidad_promedio = 0
            perdida_promedio = 0
        
        # Crear reporte
        reporte = {
            'resumen_ejecutivo': {
                'fecha_reporte': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_mediciones': total_mediciones,
                'alertas_activas': alertas_activas,
                'estado_general': 'NORMAL' if alertas_activas == 0 else 'ATENCIÓN' if alertas_activas < 3 else 'CRÍTICO'
            },
            'metricas_actuales': ultima_metrica,
            'tendencias': tendencias,
            'estadisticas': {
                'dilucion_promedio': dilucion_promedio,
                'volatilidad_promedio': volatilidad_promedio,
                'perdida_promedio': perdida_promedio
            },
            'alertas_activas': self.alertas_activas[-5:] if self.alertas_activas else [],
            'recomendaciones': self._generar_recomendaciones_seguimiento(tendencias)
        }
        
        # Mostrar resumen
        print(f"📅 Fecha del Reporte: {reporte['resumen_ejecutivo']['fecha_reporte']}")
        print(f"📊 Total de Mediciones: {reporte['resumen_ejecutivo']['total_mediciones']}")
        print(f"🚨 Alertas Activas: {reporte['resumen_ejecutivo']['alertas_activas']}")
        print(f"⚡ Estado General: {reporte['resumen_ejecutivo']['estado_general']}")
        
        if tendencias:
            print(f"\n📈 Tendencias Detectadas:")
            for key, value in tendencias.items():
                if isinstance(value, dict) and 'direccion' in value:
                    print(f"   {key.upper()}: {value['direccion']}")
        
        return reporte

    def _generar_recomendaciones_seguimiento(self, tendencias):
        """
        Genera recomendaciones basadas en las tendencias detectadas
        """
        recomendaciones = []
        
        if not tendencias:
            return recomendaciones
        
        # Recomendación basada en tendencia de dilución
        if 'dilucion' in tendencias and tendencias['dilucion']['direccion'] == 'AUMENTANDO':
            recomendaciones.append({
                'tipo': 'DILUCIÓN CRECIENTE',
                'mensaje': 'La dilución potencial está aumentando. Considerar activar cláusulas anti-dilución.',
                'prioridad': 'ALTA'
            })
        
        # Recomendación basada en volatilidad
        if 'volatilidad' in tendencias and tendencias['volatilidad']['nivel'] == 'ALTA':
            recomendaciones.append({
                'tipo': 'VOLATILIDAD ALTA',
                'mensaje': 'Alta volatilidad detectada. Aumentar frecuencia de monitoreo.',
                'prioridad': 'MEDIA'
            })
        
        # Recomendación basada en alertas
        if 'alertas' in tendencias and tendencias['alertas']['nivel'] == 'ALTA':
            recomendaciones.append({
                'tipo': 'FRECUENCIA DE ALERTAS',
                'mensaje': 'Alta frecuencia de alertas. Revisar umbrales y estrategias.',
                'prioridad': 'ALTA'
            })
        
        return recomendaciones

    def ejecutar_ciclo_monitoreo(self, datos_empresa):
        """
        Ejecuta un ciclo completo de monitoreo
        """
        print(f"\n🔄 CICLO DE MONITOREO - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)
        
        # Capturar métricas
        metricas = self.capturar_metricas_tiempo_real(datos_empresa)
        
        # Evaluar alertas
        alertas = self.evaluar_alertas(metricas)
        
        # Mostrar métricas actuales
        print(f"💰 Valoración: ${metricas['valoracion_actual']:,.2f}")
        print(f"📊 Dilución Potencial: {metricas['dilucion_potencial']:.2f}%")
        print(f"📉 Pérdida de Valor: {metricas['perdida_valor']:.2f}%")
        print(f"📈 Volatilidad: {metricas['volatilidad']:.4f}")
        
        # Mostrar alertas si las hay
        if alertas:
            print(f"\n🚨 ALERTAS DETECTADAS ({len(alertas)}):")
            for alerta in alertas:
                print(f"   ⚠️  {alerta['tipo']}: {alerta['mensaje']}")
        else:
            print("✅ Sin alertas - Situación normal")
        
        return metricas, alertas

    def iniciar_monitoreo_continuo(self, datos_empresa, intervalo_minutos=5):
        """
        Inicia el monitoreo continuo del sistema
        """
        print(f"\n🚀 INICIANDO MONITOREO CONTINUO")
        print(f"⏱️  Intervalo: {intervalo_minutos} minutos")
        print("=" * 80)
        
        def ciclo_monitoreo():
            try:
                self.ejecutar_ciclo_monitoreo(datos_empresa)
            except Exception as e:
                print(f"❌ Error en ciclo de monitoreo: {e}")
        
        # Programar ejecución
        schedule.every(intervalo_minutos).minutes.do(ciclo_monitoreo)
        
        print("✅ Monitoreo continuo iniciado")
        print("💡 Presiona Ctrl+C para detener")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Monitoreo detenido por el usuario")
            self.generar_reporte_seguimiento()

def main():
    """
    Función principal para ejecutar el sistema de seguimiento
    """
    print("🔍 INICIANDO SISTEMA DE SEGUIMIENTO COPYCAR")
    print("=" * 80)
    
    # Crear instancia del sistema
    sistema = SistemaSeguimientoCopycar()
    
    # Datos de ejemplo de la empresa
    datos_empresa = {
        'valoracion_actual': 5000000,  # $5M
        'inversion_actual': 500000,    # $500K
        'acciones_totales': 1000000    # 1M acciones
    }
    
    # Ejecutar algunos ciclos de monitoreo
    print("\n🔄 Ejecutando ciclos de monitoreo de prueba...")
    for i in range(5):
        sistema.ejecutar_ciclo_monitoreo(datos_empresa)
        time.sleep(1)  # Pausa de 1 segundo entre ciclos
    
    # Generar reporte final
    sistema.generar_reporte_seguimiento()
    
    # Crear dashboard
    sistema.crear_dashboard_seguimiento()
    
    print("\n✅ SISTEMA DE SEGUIMIENTO COPYCAR COMPLETADO")
    print("=" * 80)

if __name__ == "__main__":
    main()


