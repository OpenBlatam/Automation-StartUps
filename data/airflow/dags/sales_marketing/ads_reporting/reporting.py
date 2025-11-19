"""
Utilidades para generación y exportación de reportes.

Incluye:
- Formateo de reportes
- Exportación a diferentes formatos
- Plantillas de reportes
- Visualización de datos
"""

from __future__ import annotations

import csv
import json
import logging
from datetime import datetime
from io import StringIO
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def format_report_summary(
    summary: Dict[str, Any],
    format_type: str = "text"
) -> str:
    """
    Formatea un resumen de reporte en diferentes formatos.
    
    Args:
        summary: Diccionario con resumen de métricas
        format_type: Tipo de formato ("text", "markdown", "html")
        
    Returns:
        String formateado
    """
    if format_type == "text":
        lines = [
            "=" * 60,
            "REPORTE DE RENDIMIENTO",
            "=" * 60,
            f"Período: {summary.get('period', {}).get('start', 'N/A')} a {summary.get('period', {}).get('stop', 'N/A')}",
            f"Días: {summary.get('period', {}).get('days', 0)}",
            "",
            "RESUMEN GENERAL:",
            f"  Total de registros: {summary.get('total_records', 0):,}",
            f"  Total de campañas: {summary.get('total_campaigns', 0)}",
            "",
            "MÉTRICAS:",
            f"  Impresiones: {summary.get('total_impressions', 0):,}",
            f"  Clics: {summary.get('total_clicks', 0):,}",
            f"  Gasto: ${summary.get('total_spend', 0):,.2f}",
            f"  Conversiones: {summary.get('total_conversions', 0):,.2f}",
            f"  Ingresos: ${summary.get('total_revenue', 0):,.2f}",
            "",
            "PROMEDIOS:",
            f"  CTR: {summary.get('avg_ctr', 0):.2f}%",
            f"  CPC: ${summary.get('avg_cpc', 0):.4f}",
            f"  CPA: ${summary.get('avg_cpa', 0):.2f}",
            f"  ROAS: {summary.get('roas', 0):.4f}",
            f"  Tasa de conversión: {summary.get('conversion_rate', 0):.2f}%",
            "=" * 60
        ]
        return "\n".join(lines)
    
    elif format_type == "markdown":
        lines = [
            "# Reporte de Rendimiento",
            "",
            f"**Período:** {summary.get('period', {}).get('start', 'N/A')} a {summary.get('period', {}).get('stop', 'N/A')}",
            f"**Días:** {summary.get('period', {}).get('days', 0)}",
            "",
            "## Resumen General",
            "",
            "| Métrica | Valor |",
            "|---------|-------|",
            f"| Total de registros | {summary.get('total_records', 0):,} |",
            f"| Total de campañas | {summary.get('total_campaigns', 0)} |",
            "",
            "## Métricas",
            "",
            "| Métrica | Valor |",
            "|---------|-------|",
            f"| Impresiones | {summary.get('total_impressions', 0):,} |",
            f"| Clics | {summary.get('total_clicks', 0):,} |",
            f"| Gasto | ${summary.get('total_spend', 0):,.2f} |",
            f"| Conversiones | {summary.get('total_conversions', 0):,.2f} |",
            f"| Ingresos | ${summary.get('total_revenue', 0):,.2f} |",
            "",
            "## Promedios",
            "",
            "| Métrica | Valor |",
            "|---------|-------|",
            f"| CTR | {summary.get('avg_ctr', 0):.2f}% |",
            f"| CPC | ${summary.get('avg_cpc', 0):.4f} |",
            f"| CPA | ${summary.get('avg_cpa', 0):.2f} |",
            f"| ROAS | {summary.get('roas', 0):.4f} |",
            f"| Tasa de conversión | {summary.get('conversion_rate', 0):.2f}% |",
        ]
        return "\n".join(lines)
    
    elif format_type == "html":
        html = f"""
        <html>
        <head>
            <title>Reporte de Rendimiento</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
            </style>
        </head>
        <body>
            <h1>Reporte de Rendimiento</h1>
            <p><strong>Período:</strong> {summary.get('period', {}).get('start', 'N/A')} a {summary.get('period', {}).get('stop', 'N/A')}</p>
            <p><strong>Días:</strong> {summary.get('period', {}).get('days', 0)}</p>
            
            <h2>Resumen General</h2>
            <table>
                <tr><th>Métrica</th><th>Valor</th></tr>
                <tr><td>Total de registros</td><td>{summary.get('total_records', 0):,}</td></tr>
                <tr><td>Total de campañas</td><td>{summary.get('total_campaigns', 0)}</td></tr>
            </table>
            
            <h2>Métricas</h2>
            <table>
                <tr><th>Métrica</th><th>Valor</th></tr>
                <tr><td>Impresiones</td><td>{summary.get('total_impressions', 0):,}</td></tr>
                <tr><td>Clics</td><td>{summary.get('total_clicks', 0):,}</td></tr>
                <tr><td>Gasto</td><td>${summary.get('total_spend', 0):,.2f}</td></tr>
                <tr><td>Conversiones</td><td>{summary.get('total_conversions', 0):,.2f}</td></tr>
                <tr><td>Ingresos</td><td>${summary.get('total_revenue', 0):,.2f}</td></tr>
            </table>
            
            <h2>Promedios</h2>
            <table>
                <tr><th>Métrica</th><th>Valor</th></tr>
                <tr><td>CTR</td><td>{summary.get('avg_ctr', 0):.2f}%</td></tr>
                <tr><td>CPC</td><td>${summary.get('avg_cpc', 0):.4f}</td></tr>
                <tr><td>CPA</td><td>${summary.get('avg_cpa', 0):.2f}</td></tr>
                <tr><td>ROAS</td><td>{summary.get('roas', 0):.4f}</td></tr>
                <tr><td>Tasa de conversión</td><td>{summary.get('conversion_rate', 0):.2f}%</td></tr>
            </table>
        </body>
        </html>
        """
        return html
    
    else:
        return json.dumps(summary, indent=2)


def export_to_csv(
    data: List[Dict[str, Any]],
    filepath: Optional[str] = None,
    fields: Optional[List[str]] = None
) -> str:
    """
    Exporta datos a CSV.
    
    Args:
        data: Lista de datos a exportar
        filepath: Ruta del archivo (opcional, si no se proporciona retorna string)
        fields: Campos a incluir (opcional, usa todos si no se especifica)
        
    Returns:
        String CSV si filepath no se proporciona, sino None
    """
    if not data:
        return ""
    
    # Determinar campos
    if fields is None:
        fields = list(data[0].keys())
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    
    for record in data:
        row = {field: record.get(field, "") for field in fields}
        writer.writerow(row)
    
    csv_string = output.getvalue()
    output.close()
    
    if filepath:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(csv_string)
        return filepath
    else:
        return csv_string


def export_to_json(
    data: List[Dict[str, Any]],
    filepath: Optional[str] = None,
    indent: int = 2
) -> Optional[str]:
    """
    Exporta datos a JSON.
    
    Args:
        data: Lista de datos a exportar
        filepath: Ruta del archivo (opcional)
        indent: Indentación del JSON
        
    Returns:
        String JSON si filepath no se proporciona, sino None
    """
    json_string = json.dumps(data, indent=indent, default=str, ensure_ascii=False)
    
    if filepath:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_string)
        return filepath
    else:
        return json_string


def export_to_dataframe(
    data: List[Dict[str, Any]]
) -> Optional[Any]:
    """
    Convierte datos a pandas DataFrame.
    
    Args:
        data: Lista de datos a convertir
        
    Returns:
        DataFrame de pandas o None si pandas no está disponible
    """
    if not PANDAS_AVAILABLE:
        logger.warning("pandas no disponible, no se puede convertir a DataFrame")
        return None
    
    if not data:
        return pd.DataFrame()
    
    return pd.DataFrame(data)


def generate_daily_summary(
    data: List[Dict[str, Any]],
    date_field: str = "date_start"
) -> Dict[str, Dict[str, Any]]:
    """
    Genera resumen diario de datos.
    
    Args:
        data: Lista de datos
        date_field: Campo con la fecha
        
    Returns:
        Diccionario con resumen por fecha
    """
    from ads_reporting.processors import CampaignProcessor
    
    processor = CampaignProcessor()
    grouped = processor.group_by_date(data)
    
    daily_summaries = {}
    
    for date, date_data in grouped.items():
        metrics = processor.calculate_metrics(date_data)
        
        daily_summaries[date] = {
            "date": date,
            "total_records": len(date_data),
            "total_impressions": metrics.total_impressions,
            "total_clicks": metrics.total_clicks,
            "total_spend": metrics.total_spend,
            "total_conversions": metrics.total_conversions,
            "total_revenue": metrics.total_revenue,
            "avg_ctr": metrics.avg_ctr,
            "avg_cpc": metrics.avg_cpc,
            "avg_cpa": metrics.avg_cpa,
            "roas": metrics.roas,
            "conversion_rate": metrics.conversion_rate
        }
    
    return daily_summaries


def create_comparison_table(
    comparison_results: Dict[str, Any]
) -> str:
    """
    Crea tabla de comparación formateada.
    
    Args:
        comparison_results: Resultados de comparación_periodos
        
    Returns:
        String con tabla formateada
    """
    lines = [
        "COMPARACIÓN DE PERÍODOS",
        "=" * 80,
        f"{'Métrica':<20} {'Período 1':<15} {'Período 2':<15} {'Diferencia':<15} {'Cambio %':<15}",
        "-" * 80
    ]
    
    for metric_name, result in comparison_results.items():
        if isinstance(result, dict) and "baseline_value" in result:
            lines.append(
                f"{metric_name:<20} "
                f"{result['baseline_value']:<15.2f} "
                f"{result['comparison_value']:<15.2f} "
                f"{result['difference']:<15.2f} "
                f"{result['difference_percent']:<15.2f}%"
            )
    
    lines.append("=" * 80)
    return "\n".join(lines)


def export_to_excel(
    data: List[Dict[str, Any]],
    filepath: str,
    sheet_name: str = "Data"
) -> str:
    """
    Exporta datos a Excel (requiere pandas y openpyxl).
    
    Args:
        data: Lista de datos a exportar
        filepath: Ruta del archivo
        sheet_name: Nombre de la hoja
        
    Returns:
        Ruta del archivo creado
        
    Raises:
        ImportError: Si pandas o openpyxl no están disponibles
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas requerido para exportar a Excel")
    
    try:
        import openpyxl
    except ImportError:
        raise ImportError("openpyxl requerido para exportar a Excel")
    
    df = export_to_dataframe(data)
    if df is None:
        raise ValueError("No se pudo convertir datos a DataFrame")
    
    df.to_excel(filepath, sheet_name=sheet_name, index=False)
    return filepath


def format_alert_summary(
    alerts: List[Dict[str, Any]]
) -> str:
    """
    Formatea resumen de alertas.
    
    Args:
        alerts: Lista de alertas
        
    Returns:
        String formateado
    """
    if not alerts:
        return "No hay alertas."
    
    lines = [
        "ALERTAS DEL SISTEMA",
        "=" * 80,
        f"Total de alertas: {len(alerts)}",
        ""
    ]
    
    # Agrupar por nivel
    by_level = {}
    for alert in alerts:
        level = alert.get("level", "unknown")
        if level not in by_level:
            by_level[level] = []
        by_level[level].append(alert)
    
    for level, level_alerts in by_level.items():
        lines.append(f"\n{level.upper()} ({len(level_alerts)}):")
        lines.append("-" * 80)
        for alert in level_alerts[:10]:  # Limitar a 10 por nivel
            lines.append(f"  • {alert.get('title', 'N/A')}: {alert.get('message', 'N/A')}")
            if alert.get("platform"):
                lines.append(f"    Plataforma: {alert['platform']}")
        if len(level_alerts) > 10:
            lines.append(f"  ... y {len(level_alerts) - 10} más")
    
    return "\n".join(lines)

