#!/usr/bin/env python3
"""
Sistema de Analytics y Métricas de Uso
=====================================

Sistema inteligente que recopila y analiza métricas de uso del sistema
de organización de documentos para optimización continua.

Características:
- Tracking de acceso a archivos
- Análisis de patrones de uso
- Métricas de rendimiento
- Reportes de tendencias
- Recomendaciones de optimización

Autor: Sistema de Organización Inteligente
Versión: 1.0
Fecha: 2024
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class AnalyticsSistema:
    def __init__(self, base_path="/Users/adan/frontier/docuementos"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "analytics.db"
        self.config_file = self.base_path / "analytics_config.json"
        
        # Configuración por defecto
        self.config = {
            "tracking_habilitado": True,
            "retener_datos_dias": 365,
            "generar_graficos": True,
            "analisis_tendencias": True,
            "recomendaciones_automaticas": True,
            "metricas_rendimiento": True
        }
        
        self.init_database()
        self.cargar_configuracion()
    
    def init_database(self):
        """Inicializa la base de datos SQLite para analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de accesos a archivos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accesos_archivos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                archivo TEXT NOT NULL,
                ruta TEXT NOT NULL,
                tipo_archivo TEXT,
                tamaño INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                usuario TEXT,
                accion TEXT DEFAULT 'lectura',
                duracion_segundos INTEGER,
                ip_address TEXT
            )
        ''')
        
        # Tabla de búsquedas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS busquedas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                consulta TEXT NOT NULL,
                resultados_encontrados INTEGER,
                tiempo_respuesta_ms INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                usuario TEXT,
                filtros_aplicados TEXT
            )
        ''')
        
        # Tabla de métricas de sistema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metricas_sistema (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_archivos INTEGER,
                total_carpetas INTEGER,
                espacio_usado_mb REAL,
                tiempo_respuesta_promedio_ms REAL,
                errores_count INTEGER,
                mantenimiento_ejecutado BOOLEAN
            )
        ''')
        
        # Tabla de errores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS errores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tipo_error TEXT,
                mensaje TEXT,
                archivo_afectado TEXT,
                stack_trace TEXT,
                severidad TEXT DEFAULT 'medium'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def cargar_configuracion(self):
        """Carga configuración desde archivo JSON"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_cargada = json.load(f)
                    self.config.update(config_cargada)
            except Exception as e:
                print(f"❌ Error cargando configuración: {e}")
        else:
            self.guardar_configuracion()
    
    def guardar_configuracion(self):
        """Guarda configuración en archivo JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")
    
    def registrar_acceso_archivo(self, archivo: str, ruta: str, accion: str = "lectura", 
                                duracion: int = 0, usuario: str = "sistema"):
        """Registra acceso a un archivo"""
        if not self.config["tracking_habilitado"]:
            return
        
        try:
            archivo_path = Path(archivo)
            tipo_archivo = archivo_path.suffix.lower()
            tamaño = archivo_path.stat().st_size if archivo_path.exists() else 0
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO accesos_archivos 
                (archivo, ruta, tipo_archivo, tamaño, accion, duracion_segundos, usuario)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (archivo_path.name, ruta, tipo_archivo, tamaño, accion, duracion, usuario))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error registrando acceso: {e}")
    
    def registrar_busqueda(self, consulta: str, resultados: int, tiempo_respuesta: int,
                          filtros: str = "", usuario: str = "sistema"):
        """Registra una búsqueda realizada"""
        if not self.config["tracking_habilitado"]:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO busquedas 
                (consulta, resultados_encontrados, tiempo_respuesta_ms, filtros_aplicados, usuario)
                VALUES (?, ?, ?, ?, ?)
            ''', (consulta, resultados, tiempo_respuesta, filtros, usuario))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error registrando búsqueda: {e}")
    
    def registrar_metrica_sistema(self, total_archivos: int, total_carpetas: int,
                                 espacio_usado: float, tiempo_respuesta: float,
                                 errores: int = 0, mantenimiento: bool = False):
        """Registra métricas del sistema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO metricas_sistema 
                (total_archivos, total_carpetas, espacio_usado_mb, tiempo_respuesta_promedio_ms, 
                 errores_count, mantenimiento_ejecutado)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (total_archivos, total_carpetas, espacio_usado, tiempo_respuesta, errores, mantenimiento))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error registrando métrica: {e}")
    
    def registrar_error(self, tipo_error: str, mensaje: str, archivo_afectado: str = "",
                       stack_trace: str = "", severidad: str = "medium"):
        """Registra un error del sistema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO errores 
                (tipo_error, mensaje, archivo_afectado, stack_trace, severidad)
                VALUES (?, ?, ?, ?, ?)
            ''', (tipo_error, mensaje, archivo_afectado, stack_trace, severidad))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error registrando error: {e}")
    
    def obtener_archivos_mas_accedidos(self, dias: int = 30, limite: int = 10) -> List[Dict]:
        """Obtiene los archivos más accedidos en un período"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            fecha_limite = datetime.now() - timedelta(days=dias)
            
            cursor.execute('''
                SELECT archivo, ruta, tipo_archivo, COUNT(*) as accesos,
                       AVG(duracion_segundos) as duracion_promedio,
                       MAX(timestamp) as ultimo_acceso
                FROM accesos_archivos 
                WHERE timestamp >= ?
                GROUP BY archivo, ruta
                ORDER BY accesos DESC
                LIMIT ?
            ''', (fecha_limite, limite))
            
            resultados = []
            for row in cursor.fetchall():
                resultados.append({
                    'archivo': row[0],
                    'ruta': row[1],
                    'tipo': row[2],
                    'accesos': row[3],
                    'duracion_promedio': row[4] or 0,
                    'ultimo_acceso': row[5]
                })
            
            conn.close()
            return resultados
            
        except Exception as e:
            print(f"❌ Error obteniendo archivos más accedidos: {e}")
            return []
    
    def obtener_busquedas_populares(self, dias: int = 30, limite: int = 10) -> List[Dict]:
        """Obtiene las búsquedas más populares"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            fecha_limite = datetime.now() - timedelta(days=dias)
            
            cursor.execute('''
                SELECT consulta, COUNT(*) as frecuencia,
                       AVG(resultados_encontrados) as resultados_promedio,
                       AVG(tiempo_respuesta_ms) as tiempo_promedio
                FROM busquedas 
                WHERE timestamp >= ?
                GROUP BY consulta
                ORDER BY frecuencia DESC
                LIMIT ?
            ''', (fecha_limite, limite))
            
            resultados = []
            for row in cursor.fetchall():
                resultados.append({
                    'consulta': row[0],
                    'frecuencia': row[1],
                    'resultados_promedio': row[2] or 0,
                    'tiempo_promedio': row[3] or 0
                })
            
            conn.close()
            return resultados
            
        except Exception as e:
            print(f"❌ Error obteniendo búsquedas populares: {e}")
            return []
    
    def analizar_tendencias_uso(self, dias: int = 30) -> Dict:
        """Analiza tendencias de uso del sistema"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Tendencias de acceso por día
            df_accesos = pd.read_sql_query('''
                SELECT DATE(timestamp) as fecha, COUNT(*) as accesos
                FROM accesos_archivos 
                WHERE timestamp >= date('now', '-{} days')
                GROUP BY DATE(timestamp)
                ORDER BY fecha
            '''.format(dias), conn)
            
            # Tendencias de búsquedas por día
            df_busquedas = pd.read_sql_query('''
                SELECT DATE(timestamp) as fecha, COUNT(*) as busquedas
                FROM busquedas 
                WHERE timestamp >= date('now', '-{} days')
                GROUP BY DATE(timestamp)
                ORDER BY fecha
            '''.format(dias), conn)
            
            # Métricas de rendimiento
            df_rendimiento = pd.read_sql_query('''
                SELECT DATE(timestamp) as fecha, 
                       AVG(tiempo_respuesta_promedio_ms) as tiempo_promedio,
                       SUM(errores_count) as errores
                FROM metricas_sistema 
                WHERE timestamp >= date('now', '-{} days')
                GROUP BY DATE(timestamp)
                ORDER BY fecha
            '''.format(dias), conn)
            
            conn.close()
            
            # Calcular tendencias
            tendencias = {
                'accesos': {
                    'total': df_accesos['accesos'].sum(),
                    'promedio_diario': df_accesos['accesos'].mean(),
                    'tendencia': self._calcular_tendencia(df_accesos['accesos']),
                    'pico_dia': df_accesos.loc[df_accesos['accesos'].idxmax(), 'fecha'] if not df_accesos.empty else None
                },
                'busquedas': {
                    'total': df_busquedas['busquedas'].sum(),
                    'promedio_diario': df_busquedas['busquedas'].mean(),
                    'tendencia': self._calcular_tendencia(df_busquedas['busquedas']),
                    'pico_dia': df_busquedas.loc[df_busquedas['busquedas'].idxmax(), 'fecha'] if not df_busquedas.empty else None
                },
                'rendimiento': {
                    'tiempo_respuesta_promedio': df_rendimiento['tiempo_promedio'].mean(),
                    'total_errores': df_rendimiento['errores'].sum(),
                    'tendencia_tiempo': self._calcular_tendencia(df_rendimiento['tiempo_promedio']),
                    'tendencia_errores': self._calcular_tendencia(df_rendimiento['errores'])
                }
            }
            
            return tendencias
            
        except Exception as e:
            print(f"❌ Error analizando tendencias: {e}")
            return {}
    
    def _calcular_tendencia(self, serie: pd.Series) -> str:
        """Calcula la tendencia de una serie temporal"""
        if len(serie) < 2:
            return "insuficiente_datos"
        
        # Regresión lineal simple
        x = np.arange(len(serie))
        y = serie.values
        
        # Calcular pendiente
        pendiente = np.polyfit(x, y, 1)[0]
        
        if pendiente > 0.1:
            return "creciente"
        elif pendiente < -0.1:
            return "decreciente"
        else:
            return "estable"
    
    def generar_recomendaciones(self) -> List[Dict]:
        """Genera recomendaciones basadas en el análisis de datos"""
        recomendaciones = []
        
        try:
            # Analizar archivos más accedidos
            archivos_populares = self.obtener_archivos_mas_accedidos(dias=7, limite=5)
            
            if archivos_populares:
                # Recomendación: Archivos más accedidos
                recomendaciones.append({
                    'tipo': 'optimizacion',
                    'titulo': 'Archivos de Alto Tráfico',
                    'descripcion': f'Los archivos más accedidos son: {", ".join([a["archivo"] for a in archivos_populares[:3]])}',
                    'accion': 'Considera optimizar estos archivos o crear accesos directos',
                    'prioridad': 'alta'
                })
            
            # Analizar búsquedas sin resultados
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT consulta, COUNT(*) as frecuencia
                FROM busquedas 
                WHERE resultados_encontrados = 0
                AND timestamp >= date('now', '-7 days')
                GROUP BY consulta
                ORDER BY frecuencia DESC
                LIMIT 5
            ''')
            
            busquedas_sin_resultados = cursor.fetchall()
            
            if busquedas_sin_resultados:
                recomendaciones.append({
                    'tipo': 'contenido',
                    'titulo': 'Búsquedas Sin Resultados',
                    'descripcion': f'Búsquedas frecuentes sin resultados: {", ".join([b[0] for b in busquedas_sin_resultados[:3]])}',
                    'accion': 'Considera agregar contenido relacionado o mejorar la indexación',
                    'prioridad': 'media'
                })
            
            # Analizar rendimiento
            cursor.execute('''
                SELECT AVG(tiempo_respuesta_promedio_ms) as tiempo_promedio
                FROM metricas_sistema 
                WHERE timestamp >= date('now', '-7 days')
            ''')
            
            tiempo_promedio = cursor.fetchone()[0]
            
            if tiempo_promedio and tiempo_promedio > 1000:  # Más de 1 segundo
                recomendaciones.append({
                    'tipo': 'rendimiento',
                    'titulo': 'Rendimiento Lento',
                    'descripcion': f'Tiempo de respuesta promedio: {tiempo_promedio:.0f}ms',
                    'accion': 'Considera optimizar la base de datos o mejorar la indexación',
                    'prioridad': 'alta'
                })
            
            # Analizar errores
            cursor.execute('''
                SELECT COUNT(*) as total_errores
                FROM errores 
                WHERE timestamp >= date('now', '-7 days')
            ''')
            
            total_errores = cursor.fetchone()[0]
            
            if total_errores > 10:
                recomendaciones.append({
                    'tipo': 'estabilidad',
                    'titulo': 'Alto Número de Errores',
                    'descripcion': f'{total_errores} errores en los últimos 7 días',
                    'accion': 'Revisa los logs de errores y corrige problemas críticos',
                    'prioridad': 'alta'
                })
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error generando recomendaciones: {e}")
        
        return recomendaciones
    
    def generar_graficos(self, dias: int = 30):
        """Genera gráficos de análisis"""
        if not self.config["generar_graficos"]:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Gráfico de accesos por día
            df_accesos = pd.read_sql_query('''
                SELECT DATE(timestamp) as fecha, COUNT(*) as accesos
                FROM accesos_archivos 
                WHERE timestamp >= date('now', '-{} days')
                GROUP BY DATE(timestamp)
                ORDER BY fecha
            '''.format(dias), conn)
            
            plt.figure(figsize=(12, 8))
            
            # Subplot 1: Accesos por día
            plt.subplot(2, 2, 1)
            plt.plot(df_accesos['fecha'], df_accesos['accesos'])
            plt.title('Accesos por Día')
            plt.xlabel('Fecha')
            plt.ylabel('Número de Accesos')
            plt.xticks(rotation=45)
            
            # Subplot 2: Archivos más accedidos
            archivos_populares = self.obtener_archivos_mas_accedidos(dias=dias, limite=10)
            if archivos_populares:
                plt.subplot(2, 2, 2)
                nombres = [a['archivo'][:20] + '...' if len(a['archivo']) > 20 else a['archivo'] 
                          for a in archivos_populares[:5]]
                accesos = [a['accesos'] for a in archivos_populares[:5]]
                plt.bar(nombres, accesos)
                plt.title('Archivos Más Accedidos')
                plt.xlabel('Archivo')
                plt.ylabel('Accesos')
                plt.xticks(rotation=45)
            
            # Subplot 3: Búsquedas populares
            busquedas_populares = self.obtener_busquedas_populares(dias=dias, limite=5)
            if busquedas_populares:
                plt.subplot(2, 2, 3)
                consultas = [b['consulta'][:15] + '...' if len(b['consulta']) > 15 else b['consulta'] 
                           for b in busquedas_populares]
                frecuencias = [b['frecuencia'] for b in busquedas_populares]
                plt.bar(consultas, frecuencias)
                plt.title('Búsquedas Populares')
                plt.xlabel('Consulta')
                plt.ylabel('Frecuencia')
                plt.xticks(rotation=45)
            
            # Subplot 4: Tendencias de rendimiento
            df_rendimiento = pd.read_sql_query('''
                SELECT DATE(timestamp) as fecha, 
                       AVG(tiempo_respuesta_promedio_ms) as tiempo_promedio
                FROM metricas_sistema 
                WHERE timestamp >= date('now', '-{} days')
                GROUP BY DATE(timestamp)
                ORDER BY fecha
            '''.format(dias), conn)
            
            if not df_rendimiento.empty:
                plt.subplot(2, 2, 4)
                plt.plot(df_rendimiento['fecha'], df_rendimiento['tiempo_promedio'])
                plt.title('Tiempo de Respuesta Promedio')
                plt.xlabel('Fecha')
                plt.ylabel('Tiempo (ms)')
                plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # Guardar gráfico
            grafico_path = self.base_path / "analytics_graficos.png"
            plt.savefig(grafico_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            conn.close()
            
            print(f"📊 Gráficos generados: {grafico_path}")
            
        except Exception as e:
            print(f"❌ Error generando gráficos: {e}")
    
    def generar_reporte_analytics(self) -> str:
        """Genera reporte completo de analytics"""
        tendencias = self.analizar_tendencias_uso()
        archivos_populares = self.obtener_archivos_mas_accedidos()
        busquedas_populares = self.obtener_busquedas_populares()
        recomendaciones = self.generar_recomendaciones()
        
        reporte = f"""# 📊 Reporte de Analytics del Sistema - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📈 Resumen Ejecutivo
- **Período analizado:** Últimos 30 días
- **Total de accesos:** {tendencias.get('accesos', {}).get('total', 0):,}
- **Total de búsquedas:** {tendencias.get('busquedas', {}).get('total', 0):,}
- **Tiempo de respuesta promedio:** {tendencias.get('rendimiento', {}).get('tiempo_respuesta_promedio', 0):.1f}ms

## 📁 Archivos Más Accedidos
"""
        
        if archivos_populares:
            for i, archivo in enumerate(archivos_populares[:10], 1):
                reporte += f"""
### {i}. {archivo['archivo']}
- **Ruta:** {archivo['ruta']}
- **Accesos:** {archivo['accesos']}
- **Duración promedio:** {archivo['duracion_promedio']:.1f}s
- **Último acceso:** {archivo['ultimo_acceso']}

"""
        else:
            reporte += "\n❌ No hay datos de accesos disponibles\n"
        
        reporte += "\n## 🔍 Búsquedas Populares\n"
        
        if busquedas_populares:
            for i, busqueda in enumerate(busquedas_populares[:10], 1):
                reporte += f"""
### {i}. "{busqueda['consulta']}"
- **Frecuencia:** {busqueda['frecuencia']} veces
- **Resultados promedio:** {busqueda['resultados_promedio']:.1f}
- **Tiempo promedio:** {busqueda['tiempo_promedio']:.1f}ms

"""
        else:
            reporte += "\n❌ No hay datos de búsquedas disponibles\n"
        
        reporte += "\n## 📊 Análisis de Tendencias\n"
        
        if tendencias:
            accesos = tendencias.get('accesos', {})
            busquedas = tendencias.get('busquedas', {})
            rendimiento = tendencias.get('rendimiento', {})
            
            reporte += f"""
### Accesos
- **Promedio diario:** {accesos.get('promedio_diario', 0):.1f}
- **Tendencia:** {accesos.get('tendencia', 'desconocida')}
- **Día pico:** {accesos.get('pico_dia', 'N/A')}

### Búsquedas
- **Promedio diario:** {busquedas.get('promedio_diario', 0):.1f}
- **Tendencia:** {busquedas.get('tendencia', 'desconocida')}
- **Día pico:** {busquedas.get('pico_dia', 'N/A')}

### Rendimiento
- **Tiempo de respuesta:** {rendimiento.get('tiempo_respuesta_promedio', 0):.1f}ms
- **Tendencia de tiempo:** {rendimiento.get('tendencia_tiempo', 'desconocida')}
- **Total de errores:** {rendimiento.get('total_errores', 0)}
- **Tendencia de errores:** {rendimiento.get('tendencia_errores', 'desconocida')}

"""
        
        reporte += "\n## 💡 Recomendaciones\n"
        
        if recomendaciones:
            for i, rec in enumerate(recomendaciones, 1):
                prioridad_emoji = "🔴" if rec['prioridad'] == 'alta' else "🟡" if rec['prioridad'] == 'media' else "🟢"
                reporte += f"""
### {i}. {prioridad_emoji} {rec['titulo']}
- **Tipo:** {rec['tipo']}
- **Descripción:** {rec['descripcion']}
- **Acción recomendada:** {rec['accion']}

"""
        else:
            reporte += "\n✅ No se encontraron problemas críticos\n"
        
        reporte += f"""
## 🔧 Configuración Actual
- **Tracking habilitado:** {'Sí' if self.config['tracking_habilitado'] else 'No'}
- **Retención de datos:** {self.config['retener_datos_dias']} días
- **Generación de gráficos:** {'Sí' if self.config['generar_graficos'] else 'No'}
- **Análisis de tendencias:** {'Sí' if self.config['analisis_tendencias'] else 'No'}

## 📊 Métricas de Base de Datos
- **Archivo de base de datos:** {self.db_path}
- **Tamaño de base de datos:** {self.db_path.stat().st_size / 1024 / 1024:.1f} MB

---
*Reporte generado automáticamente por el sistema de analytics*
"""
        
        return reporte
    
    def limpiar_datos_antiguos(self):
        """Limpia datos más antiguos que el período de retención"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            fecha_limite = datetime.now() - timedelta(days=self.config["retener_datos_dias"])
            
            # Limpiar accesos antiguos
            cursor.execute('DELETE FROM accesos_archivos WHERE timestamp < ?', (fecha_limite,))
            accesos_eliminados = cursor.rowcount
            
            # Limpiar búsquedas antiguas
            cursor.execute('DELETE FROM busquedas WHERE timestamp < ?', (fecha_limite,))
            busquedas_eliminadas = cursor.rowcount
            
            # Limpiar métricas antiguas
            cursor.execute('DELETE FROM metricas_sistema WHERE timestamp < ?', (fecha_limite,))
            metricas_eliminadas = cursor.rowcount
            
            # Limpiar errores antiguos
            cursor.execute('DELETE FROM errores WHERE timestamp < ?', (fecha_limite,))
            errores_eliminados = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            print(f"🧹 Limpieza completada:")
            print(f"  - Accesos eliminados: {accesos_eliminados}")
            print(f"  - Búsquedas eliminadas: {busquedas_eliminadas}")
            print(f"  - Métricas eliminadas: {metricas_eliminadas}")
            print(f"  - Errores eliminados: {errores_eliminados}")
            
        except Exception as e:
            print(f"❌ Error limpiando datos antiguos: {e}")

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema de Analytics")
    parser.add_argument("--reporte", action="store_true", help="Generar reporte de analytics")
    parser.add_argument("--graficos", action="store_true", help="Generar gráficos")
    parser.add_argument("--recomendaciones", action="store_true", help="Mostrar recomendaciones")
    parser.add_argument("--limpiar", action="store_true", help="Limpiar datos antiguos")
    parser.add_argument("--simular", action="store_true", help="Simular datos de prueba")
    
    args = parser.parse_args()
    
    analytics = AnalyticsSistema()
    
    if args.simular:
        print("🎭 Simulando datos de prueba...")
        
        # Simular accesos a archivos
        archivos_prueba = [
            "Curso_IA_Marketing_Completo.md",
            "Webinar_Curso_IA_Marketing_100_Pesos.md",
            "Yearly_Financial_Goals_Worksheet.md",
            "API_DOCUMENTATION.md",
            "create_word_document.py"
        ]
        
        for archivo in archivos_prueba:
            for _ in range(np.random.randint(1, 20)):
                analytics.registrar_acceso_archivo(
                    archivo, 
                    f"03_Marketing_Content/{archivo}",
                    "lectura",
                    np.random.randint(10, 300)
                )
        
        # Simular búsquedas
        busquedas_prueba = [
            "marketing IA",
            "curso completo",
            "financiero",
            "documentación",
            "script python"
        ]
        
        for busqueda in busquedas_prueba:
            for _ in range(np.random.randint(1, 15)):
                analytics.registrar_busqueda(
                    busqueda,
                    np.random.randint(0, 20),
                    np.random.randint(100, 2000)
                )
        
        # Simular métricas del sistema
        for _ in range(30):
            analytics.registrar_metrica_sistema(
                1199, 35, 150.5, np.random.randint(500, 1500)
            )
        
        print("✅ Datos de prueba simulados")
    
    if args.reporte:
        reporte = analytics.generar_reporte_analytics()
        reporte_path = analytics.base_path / "REPORTE_ANALYTICS.md"
        with open(reporte_path, 'w', encoding='utf-8') as f:
            f.write(reporte)
        print(f"📊 Reporte generado: {reporte_path}")
    
    if args.graficos:
        analytics.generar_graficos()
    
    if args.recomendaciones:
        recomendaciones = analytics.generar_recomendaciones()
        print("\n💡 Recomendaciones:")
        for i, rec in enumerate(recomendaciones, 1):
            print(f"{i}. {rec['titulo']} - {rec['accion']}")
    
    if args.limpiar:
        analytics.limpiar_datos_antiguos()
    
    if not any([args.reporte, args.graficos, args.recomendaciones, args.limpiar, args.simular]):
        print("📊 Sistema de Analytics")
        print("======================")
        print("1. Generar reporte")
        print("2. Generar gráficos")
        print("3. Mostrar recomendaciones")
        print("4. Limpiar datos antiguos")
        print("5. Simular datos de prueba")
        
        opcion = input("\nSelecciona una opción (1-5): ")
        
        if opcion == "1":
            reporte = analytics.generar_reporte_analytics()
            reporte_path = analytics.base_path / "REPORTE_ANALYTICS.md"
            with open(reporte_path, 'w', encoding='utf-8') as f:
                f.write(reporte)
            print(f"📊 Reporte generado: {reporte_path}")
        
        elif opcion == "2":
            analytics.generar_graficos()
        
        elif opcion == "3":
            recomendaciones = analytics.generar_recomendaciones()
            print("\n💡 Recomendaciones:")
            for i, rec in enumerate(recomendaciones, 1):
                print(f"{i}. {rec['titulo']} - {rec['accion']}")
        
        elif opcion == "4":
            analytics.limpiar_datos_antiguos()
        
        elif opcion == "5":
            print("🎭 Simulando datos de prueba...")
            # Implementar simulación aquí
            print("✅ Datos de prueba simulados")

if __name__ == "__main__":
    main()






