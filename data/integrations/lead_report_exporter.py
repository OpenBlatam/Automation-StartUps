"""
Exportador de Reportes de Leads
================================

Exporta reportes de leads en diferentes formatos (CSV, Excel, PDF).
"""
import csv
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from io import StringIO

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

logger = logging.getLogger(__name__)


class LeadReportExporter:
    """Exporta reportes de leads en diferentes formatos"""
    
    def __init__(self, db_connection_string: Optional[str] = None):
        """
        Args:
            db_connection_string: String de conexión PostgreSQL
        """
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 es requerido")
        
        self.db_conn_str = db_connection_string or os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/sales_db"
        )
    
    def get_db_connection(self):
        """Obtiene conexión a la base de datos"""
        return psycopg2.connect(self.db_conn_str)
    
    def export_to_csv(
        self,
        output_path: str,
        days: int = 30,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Exporta leads a CSV"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT 
                        lead_ext_id,
                        email,
                        first_name,
                        last_name,
                        company,
                        phone,
                        score,
                        priority,
                        stage,
                        assigned_to,
                        estimated_value,
                        probability_pct,
                        qualified_at,
                        last_contact_at,
                        next_followup_at,
                        created_at
                    FROM sales_pipeline
                    WHERE created_at >= NOW() - INTERVAL '%s days'
                """
                params = [days]
                
                if filters:
                    if filters.get("stage"):
                        query += " AND stage = %s"
                        params.append(filters["stage"])
                    if filters.get("priority"):
                        query += " AND priority = %s"
                        params.append(filters["priority"])
                    if filters.get("assigned_to"):
                        query += " AND assigned_to = %s"
                        params.append(filters["assigned_to"])
                
                query += " ORDER BY created_at DESC"
                
                cur.execute(query, params)
                rows = [dict(row) for row in cur.fetchall()]
        
        if PANDAS_AVAILABLE:
            df = pd.DataFrame(rows)
            df.to_csv(output_path, index=False)
        else:
            # Fallback sin pandas
            with open(output_path, 'w', newline='') as f:
                if rows:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
        
        logger.info(f"Exportado {len(rows)} leads a CSV: {output_path}")
        return output_path
    
    def export_to_excel(
        self,
        output_path: str,
        days: int = 30,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Exporta leads a Excel"""
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas es requerido para exportar a Excel")
        
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT 
                        lead_ext_id,
                        email,
                        first_name,
                        last_name,
                        company,
                        phone,
                        score,
                        priority,
                        stage,
                        assigned_to,
                        estimated_value,
                        probability_pct,
                        qualified_at,
                        last_contact_at,
                        next_followup_at,
                        created_at
                    FROM sales_pipeline
                    WHERE created_at >= NOW() - INTERVAL '%s days'
                """
                params = [days]
                
                if filters:
                    if filters.get("stage"):
                        query += " AND stage = %s"
                        params.append(filters["stage"])
                
                query += " ORDER BY created_at DESC"
                
                cur.execute(query, params)
                rows = [dict(row) for row in cur.fetchall()]
        
        df = pd.DataFrame(rows)
        
        # Crear Excel con múltiples hojas
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Leads', index=False)
            
            # Agregar resumen
            summary = {
                "Total Leads": [len(df)],
                "Por Stage": [df['stage'].value_counts().to_dict()],
                "Por Prioridad": [df['priority'].value_counts().to_dict()],
                "Pipeline Value": [df['estimated_value'].sum()],
                "Avg Score": [df['score'].mean()]
            }
            summary_df = pd.DataFrame(summary)
            summary_df.to_excel(writer, sheet_name='Resumen', index=False)
        
        logger.info(f"Exportado {len(rows)} leads a Excel: {output_path}")
        return output_path
    
    def export_to_pdf(
        self,
        output_path: str,
        days: int = 30,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Exporta reporte a PDF"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab es requerido para exportar a PDF")
        
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT 
                        lead_ext_id,
                        email,
                        first_name,
                        last_name,
                        company,
                        score,
                        priority,
                        stage,
                        assigned_to,
                        estimated_value,
                        qualified_at
                    FROM sales_pipeline
                    WHERE created_at >= NOW() - INTERVAL '%s days'
                """
                params = [days]
                
                if filters:
                    if filters.get("stage"):
                        query += " AND stage = %s"
                        params.append(filters["stage"])
                
                query += " ORDER BY score DESC LIMIT 100"
                
                cur.execute(query, params)
                rows = [dict(row) for row in cur.fetchall()]
        
        # Crear PDF
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        title = Paragraph("Reporte de Leads", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Fecha
        date_text = f"Generado: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
        date_para = Paragraph(date_text, styles['Normal'])
        elements.append(date_para)
        elements.append(Spacer(1, 12))
        
        # Tabla de datos
        if rows:
            data = [["ID", "Email", "Nombre", "Score", "Stage", "Valor"]]
            for row in rows:
                data.append([
                    row.get('lead_ext_id', '')[:10],
                    row.get('email', '')[:30],
                    f"{row.get('first_name', '')} {row.get('last_name', '')}"[:20],
                    str(row.get('score', 0)),
                    row.get('stage', ''),
                    f"${row.get('estimated_value', 0) or 0:.2f}"
                ])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
        
        # Generar PDF
        doc.build(elements)
        
        logger.info(f"Exportado reporte a PDF: {output_path}")
        return output_path


# Función de utilidad para exportar desde CLI
def export_report(
    format_type: str,
    output_path: str,
    days: int = 30,
    filters: Optional[Dict[str, Any]] = None
) -> str:
    """
    Exporta reporte en el formato especificado.
    
    Args:
        format_type: 'csv', 'excel', o 'pdf'
        output_path: Ruta de salida
        days: Días de datos a incluir
        filters: Filtros opcionales
    
    Returns:
        Ruta del archivo generado
    """
    exporter = LeadReportExporter()
    
    if format_type.lower() == 'csv':
        return exporter.export_to_csv(output_path, days, filters)
    elif format_type.lower() in ['excel', 'xlsx']:
        return exporter.export_to_excel(output_path, days, filters)
    elif format_type.lower() == 'pdf':
        return exporter.export_to_pdf(output_path, days, filters)
    else:
        raise ValueError(f"Formato no soportado: {format_type}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Uso: python lead_report_exporter.py <format> <output_path> [days]")
        print("Formatos: csv, excel, pdf")
        sys.exit(1)
    
    format_type = sys.argv[1]
    output_path = sys.argv[2]
    days = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    try:
        result = export_report(format_type, output_path, days)
        print(f"Reporte exportado exitosamente: {result}")
    except Exception as e:
        print(f"Error exportando reporte: {e}")
        sys.exit(1)

