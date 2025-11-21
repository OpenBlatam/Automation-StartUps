# 🎯 Guía de Análisis Avanzado - Sistema de Troubleshooting

## Herramientas de Análisis

### 1. Análisis de Tendencias

Identifica tendencias temporales en el sistema.

```sql
-- Análisis de tendencias diarias
SELECT * FROM analyze_troubleshooting_trends(30, 'day');

-- Análisis semanal
SELECT * FROM analyze_troubleshooting_trends(90, 'week');

-- Análisis mensual
SELECT * FROM analyze_troubleshooting_trends(365, 'month');
```

**Desde Python**:
```python
from scripts.troubleshooting_analyzer import TroubleshootingAnalyzer

analyzer = TroubleshootingAnalyzer(db_url)
analyzer.connect()

trends = analyzer.analyze_trends(days=30, group_by='day')
for trend in trends:
    print(f"{trend['period_start']}: {trend['resolution_rate']:.2f}% - {trend['trend_direction']}")

analyzer.close()
```

### 2. Identificar Problemas que Necesitan Mejora

Encuentra problemas con baja tasa de resolución.

```sql
SELECT * FROM identify_problems_needing_improvement(5, 70.0);
```

**Desde Python**:
```python
improvements = analyzer.identify_improvements(min_sessions=5, max_resolution_rate=70.0)

for problem in improvements:
    print(f"⚠️ {problem['problem_title']}")
    print(f"   Tasa de resolución: {problem['resolution_rate']:.2f}%")
    print(f"   Recomendación: {problem['recommendation']}")
    print()
```

### 3. Análisis de Satisfacción

Analiza satisfacción del cliente por problema.

```sql
SELECT * FROM analyze_customer_satisfaction(30);
```

**Desde Python**:
```python
satisfaction = analyzer.analyze_satisfaction(days=30)

for item in satisfaction:
    print(f"{item['problem_title']}:")
    print(f"  Rating promedio: {item['avg_rating']:.2f}")
    print(f"  NPS Score: {item['nps_score']:.2f}")
    print(f"  Prioridad de mejora: {item['improvement_priority']}")
```

### 4. Reporte Ejecutivo

Genera reporte ejecutivo completo.

```sql
SELECT generate_executive_report(
    NOW() - INTERVAL '30 days',
    NOW()
);
```

**Desde Python**:
```python
report = analyzer.generate_executive_report(days=30)

print("📊 Reporte Ejecutivo")
print(f"Período: {report['period']['start']} a {report['period']['end']}")
print(f"\nResumen:")
print(f"  Total sesiones: {report['summary']['total_sessions']}")
print(f"  Tasa de resolución: {report['summary']['resolution_rate']:.2f}%")
print(f"  Tiempo promedio: {report['summary']['avg_duration_minutes']:.2f} min")
```

### 5. Resumen Ejecutivo Rápido

Vista pre-calculada para acceso rápido.

```sql
SELECT * FROM vw_executive_summary;
```

**Desde Python**:
```python
summary = analyzer.get_executive_summary()

print("📈 Resumen Ejecutivo (30 días)")
print(f"Sesiones totales: {summary['total_sessions_30d']}")
print(f"Resueltas: {summary['resolved_30d']}")
print(f"Escaladas: {summary['escalated_30d']}")
print(f"Tasa de resolución: {summary['resolution_rate_30d']:.2f}%")
print(f"Rating promedio: {summary['avg_rating_30d']:.2f}")
```

### 6. Optimización Automática

Optimiza tablas y vistas automáticamente.

```sql
SELECT * FROM optimize_troubleshooting_tables();
```

**Desde Python**:
```python
optimizations = analyzer.optimize_tables()

for opt in optimizations:
    print(f"{opt['table_name']}: {opt['action_taken']} - {opt['execution_time_ms']:.2f}ms")
```

## Uso de Scripts

### Análisis de Tendencias

```bash
python3 scripts/troubleshooting_analyzer.py \
  --db-url $DATABASE_URL \
  --command trends \
  --days 30 \
  --group-by day \
  --output trends.json
```

### Identificar Mejoras

```bash
python3 scripts/troubleshooting_analyzer.py \
  --db-url $DATABASE_URL \
  --command improvements \
  --output improvements.json
```

### Reporte Ejecutivo

```bash
python3 scripts/troubleshooting_analyzer.py \
  --db-url $DATABASE_URL \
  --command executive \
  --days 30 \
  --output executive_report.json
```

### Optimización

```bash
python3 scripts/troubleshooting_analyzer.py \
  --db-url $DATABASE_URL \
  --command optimize
```

## Casos de Uso

### Caso 1: Revisión Semanal

```python
# Generar reporte semanal
report = analyzer.generate_executive_report(days=7)

# Identificar problemas que necesitan atención
improvements = analyzer.identify_improvements(min_sessions=3, max_resolution_rate=75.0)

# Analizar satisfacción
satisfaction = analyzer.analyze_satisfaction(days=7)

# Enviar reporte por email
send_weekly_report(report, improvements, satisfaction)
```

### Caso 2: Optimización Mensual

```python
# Optimizar tablas
optimizations = analyzer.optimize_tables()

# Analizar tendencias mensuales
trends = analyzer.analyze_trends(days=30, group_by='day')

# Identificar problemas críticos
critical = [
    p for p in analyzer.identify_improvements()
    if p['resolution_rate'] < 50
]

# Crear plan de acción
create_action_plan(critical, trends)
```

### Caso 3: Dashboard en Tiempo Real

```python
# Obtener resumen ejecutivo (rápido)
summary = analyzer.get_executive_summary()

# Actualizar dashboard
update_dashboard(summary)

# Alertar si hay problemas
if summary['resolution_rate_30d'] < 70:
    send_alert("Tasa de resolución baja", summary)
```

## Métricas Clave a Monitorear

1. **Tasa de Resolución**: > 70%
2. **Tiempo Promedio**: < 20 minutos
3. **Rating Promedio**: > 4.0
4. **Tasa de Escalación**: < 30%
5. **NPS Score**: > 50

## Alertas Recomendadas

- Tasa de resolución < 65%
- Rating promedio < 3.5
- Tasa de escalación > 35%
- Tiempo promedio > 30 minutos
- Problema específico con resolución < 50%

---

**Versión**: 1.0.0  
**Última actualización**: 2025-01-27



