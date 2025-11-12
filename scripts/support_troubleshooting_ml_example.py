#!/usr/bin/env python3
"""
Ejemplo de Uso de Integración ML con Schema de Troubleshooting.

Demuestra cómo usar todas las funciones avanzadas del schema:
- Predicción de resultados
- Detección de anomalías
- Generación de alertas
- Búsqueda de problemas similares
- Reportes ejecutivos
- Analytics avanzadas
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Nota: En producción, usar conexión real a BD
# from workflow.kestra.flows.lib.support_troubleshooting_ml_integration import (
#     TroubleshootingMLIntegration
# )


def example_predict_outcome():
    """Ejemplo: Predicción de resultado."""
    print("=" * 80)
    print("EJEMPLO 1: Predicción de Resultado de Troubleshooting")
    print("=" * 80)
    
    print("""
# En producción:
ml = TroubleshootingMLIntegration(db_connection=db_conn)

prediction = ml.predict_outcome(
    problem_description="No puedo conectarme a la base de datos",
    customer_email="cliente@example.com",
    detected_problem_id="connection_error"
)

print(f"Resultado predicho: {prediction['predicted_outcome']}")
print(f"Confianza: {prediction['confidence']:.2%}")
print(f"Tiempo estimado: {prediction['estimated_duration_minutes']} minutos")
print(f"Pasos estimados: {prediction['estimated_steps']}")
print(f"Casos similares: {prediction['similar_cases_count']}")
""")
    
    print("\n💡 Esta función usa ML para predecir si el problema se resolverá,")
    print("   se escalará o será abandonado, basándose en casos históricos similares.")
    print("\n" + "=" * 80)


def example_detect_anomalies():
    """Ejemplo: Detección de anomalías."""
    print("\n" + "=" * 80)
    print("EJEMPLO 2: Detección de Anomalías")
    print("=" * 80)
    
    print("""
# En producción:
ml = TroubleshootingMLIntegration(db_connection=db_conn)

anomalies = ml.detect_anomalies(
    date_from=datetime.now() - timedelta(days=7),
    date_to=datetime.now()
)

for anomaly in anomalies:
    print(f"Tipo: {anomaly['anomaly_type']}")
    print(f"Severidad: {anomaly['severity']}")
    print(f"Descripción: {anomaly['description']}")
    print(f"Sesión: {anomaly['session_id']}")
    print("-" * 40)
""")
    
    print("\n💡 Detecta automáticamente sesiones con:")
    print("   - Duración anormalmente larga")
    print("   - Demasiados pasos fallidos")
    print("   - Tasa de fallo inusual")
    print("   - Patrones sospechosos")
    print("\n" + "=" * 80)


def example_generate_alerts():
    """Ejemplo: Generación de alertas."""
    print("\n" + "=" * 80)
    print("EJEMPLO 3: Generación Automática de Alertas")
    print("=" * 80)
    
    print("""
# En producción:
ml = TroubleshootingMLIntegration(db_connection=db_conn)

alerts = ml.generate_alerts(
    alert_types=["high_escalation_rate", "low_resolution_rate"],
    severity_threshold="medium"
)

for alert in alerts:
    print(f"Alerta: {alert['title']}")
    print(f"Tipo: {alert['alert_type']}")
    print(f"Severidad: {alert['severity']}")
    print(f"Descripción: {alert['description']}")
    print(f"Acción recomendada: {alert['recommended_action']}")
    print("-" * 40)
""")
    
    print("\n💡 Genera alertas automáticas para:")
    print("   - Tasa de escalación alta")
    print("   - Tasa de resolución baja")
    print("   - Problemas recurrentes")
    print("   - Degradación de performance")
    print("\n" + "=" * 80)


def example_find_similar_problems():
    """Ejemplo: Búsqueda de problemas similares."""
    print("\n" + "=" * 80)
    print("EJEMPLO 4: Búsqueda de Problemas Similares")
    print("=" * 80)
    
    print("""
# En producción:
ml = TroubleshootingMLIntegration(db_connection=db_conn)

similar = ml.find_similar_problems(
    problem_description="Error al conectarse a la base de datos",
    limit=10
)

for problem in similar:
    print(f"Problema: {problem['detected_problem_title']}")
    print(f"Similitud: {problem['similarity_score']:.2%}")
    print(f"Estado: {problem['status']}")
    print(f"Resuelto: {problem['resolved_at']}")
    print("-" * 40)
""")
    
    print("\n💡 Usa búsqueda full-text para encontrar problemas similares")
    print("   y aprender de soluciones previas.")
    print("\n" + "=" * 80)


def example_executive_report():
    """Ejemplo: Reporte ejecutivo."""
    print("\n" + "=" * 80)
    print("EJEMPLO 5: Reporte Ejecutivo Completo")
    print("=" * 80)
    
    print("""
# En producción:
ml = TroubleshootingMLIntegration(db_connection=db_conn)

report = ml.get_executive_report(
    date_from=datetime.now() - timedelta(days=30),
    date_to=datetime.now(),
    include_trends=True
)

print("RESUMEN:")
print(f"  Total sesiones: {report['summary']['total_sessions']}")
print(f"  Resueltas: {report['summary']['resolved_sessions']}")
print(f"  Escaladas: {report['summary']['escalated_sessions']}")

print("\\nMÉTRICAS:")
print(f"  Tasa de resolución: {report['metrics']['resolution_rate']:.1f}%")
print(f"  Tiempo promedio: {report['metrics']['avg_duration_minutes']:.1f} min")
print(f"  Satisfacción: {report['metrics']['avg_satisfaction']:.1f}/5.0")

print("\\nPROBLEMAS TOP:")
for problem in report['top_problems'][:5]:
    print(f"  - {problem['title']}: {problem['count']} casos")

print("\\nRECOMENDACIONES:")
for rec in report['recommendations']:
    print(f"  - {rec}")
""")
    
    print("\n💡 Reporte completo con estadísticas, tendencias y recomendaciones")
    print("   para toma de decisiones ejecutivas.")
    print("\n" + "=" * 80)


def example_realtime_metrics():
    """Ejemplo: Métricas en tiempo real."""
    print("\n" + "=" * 80)
    print("EJEMPLO 6: Métricas en Tiempo Real")
    print("=" * 80)
    
    print("""
# En producción:
ml = TroubleshootingMLIntegration(db_connection=db_conn)

metrics = ml.get_realtime_metrics()

print("MÉTRICAS EN TIEMPO REAL:")
print(f"  Sesiones activas: {metrics['active_sessions']}")
print(f"  Sesiones hoy: {metrics['sessions_today']}")
print(f"  Resueltas hoy: {metrics['resolved_today']}")
print(f"  Escaladas hoy: {metrics['escalated_today']}")
print(f"  Tiempo promedio: {metrics['avg_resolution_time_minutes']:.1f} min")
print(f"  Tasa de resolución: {metrics['resolution_rate']:.1f}%")

print("\\nPROBLEMAS TOP:")
for problem in metrics['top_problems'][:5]:
    print(f"  - {problem['title']}: {problem['count']}")
""")
    
    print("\n💡 Vista materializada optimizada para consultas rápidas")
    print("   de métricas en tiempo real.")
    print("\n" + "=" * 80)


def example_daily_stats():
    """Ejemplo: Estadísticas diarias."""
    print("\n" + "=" * 80)
    print("EJEMPLO 7: Estadísticas Diarias (Vista Materializada)")
    print("=" * 80)
    
    print("""
# En producción:
ml = TroubleshootingMLIntegration(db_connection=db_conn)

stats = ml.get_daily_stats(days=30, refresh=True)

for day in stats[:7]:  # Últimos 7 días
    print(f"Fecha: {day['date']}")
    print(f"  Sesiones: {day['total_sessions']}")
    print(f"  Resueltas: {day['resolved_sessions']}")
    print(f"  Tiempo promedio: {day['avg_duration_seconds']/60:.1f} min")
    print(f"  Clientes únicos: {day['unique_customers']}")
    print("-" * 40)
""")
    
    print("\n💡 Vista materializada para analytics rápido sin impacto")
    print("   en performance de la base de datos.")
    print("\n" + "=" * 80)


def example_recommendations():
    """Ejemplo: Recomendaciones inteligentes."""
    print("\n" + "=" * 80)
    print("EJEMPLO 8: Recomendaciones Inteligentes")
    print("=" * 80)
    
    print("""
# En producción:
ml = TroubleshootingMLIntegration(db_connection=db_conn)

recommendations = ml.get_recommendations(session_id="TSESS-123")

for rec in recommendations:
    print(f"Tipo: {rec['recommendation_type']}")
    print(f"Prioridad: {rec['priority']}")
    print(f"Título: {rec['title']}")
    print(f"Descripción: {rec['description']}")
    print(f"Acción: {rec['action']}")
    print(f"Confianza: {rec['confidence']:.2%}")
    print("-" * 40)
""")
    
    print("\n💡 Recomendaciones inteligentes basadas en:")
    print("   - Historial del cliente")
    print("   - Problemas similares resueltos")
    print("   - Patrones de éxito")
    print("\n" + "=" * 80)


def example_trends():
    """Ejemplo: Detección de tendencias."""
    print("\n" + "=" * 80)
    print("EJEMPLO 9: Detección de Tendencias")
    print("=" * 80)
    
    print("""
# En producción:
ml = TroubleshootingMLIntegration(db_connection=db_conn)

trends = ml.detect_trends(problem_id="connection_error", weeks=12)

print("TENDENCIAS DETECTADAS:")
for trend in trends['trends']:
    print(f"  {trend['period']}: {trend['direction']} ({trend['percentage']:.1f}%)")

print("\\nCAMBIOS SIGNIFICATIVOS:")
for change in trends['significant_changes']:
    print(f"  {change['description']}")

print("\\nPREDICCIONES:")
print(f"  Próxima semana: {trends['predictions'].get('next_week', {})}")
""")
    
    print("\n💡 Detecta tendencias temporales y predice comportamiento futuro")
    print("   para planificación proactiva.")
    print("\n" + "=" * 80)


def example_cache():
    """Ejemplo: Sistema de cache."""
    print("\n" + "=" * 80)
    print("EJEMPLO 10: Sistema de Cache Inteligente")
    print("=" * 80)
    
    print("""
# En producción:
ml = TroubleshootingMLIntegration(db_connection=db_conn)

# Guardar en cache
ml.set_cache(
    cache_key="problem:connection_error:stats",
    cache_value={"resolution_rate": 0.85, "avg_time": 12},
    ttl_seconds=3600
)

# Obtener del cache
cached = ml.get_cache("problem:connection_error:stats")
if cached:
    print(f"Datos del cache: {cached}")
else:
    print("Cache expirado o no existe")
""")
    
    print("\n💡 Sistema de cache con TTL para optimizar queries frecuentes")
    print("   y reducir carga en la base de datos.")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("EJEMPLOS: Integración ML con Schema de Troubleshooting")
    print("=" * 80)
    
    # Ejecutar todos los ejemplos
    example_predict_outcome()
    example_detect_anomalies()
    example_generate_alerts()
    example_find_similar_problems()
    example_executive_report()
    example_realtime_metrics()
    example_daily_stats()
    example_recommendations()
    example_trends()
    example_cache()
    
    print("\n✅ Todos los ejemplos completados")
    print("\n💡 Para usar en producción:")
    print("   1. Configurar conexión a base de datos")
    print("   2. Importar TroubleshootingMLIntegration")
    print("   3. Usar las funciones según necesidad")
    print("   4. Monitorear performance y ajustar")
    print("\n📚 Ver documentación completa en:")
    print("   docs/SUPPORT_TROUBLESHOOTING_ADVANCED.md")
    print("\n")



