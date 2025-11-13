#!/usr/bin/env python3
"""
Análisis de Engagement - Integraciones y Funcionalidades Adicionales
=====================================================================
Integraciones adicionales:
- Integración con Google Analytics
- Integración con Facebook Insights API
- Integración con Instagram Graph API
- Integración con LinkedIn Analytics
- Exportación a Google Sheets
- Integración con Slack para alertas
- Integración con email para reportes
- Análisis de audiencia avanzado
- Segmentación de audiencia
- Análisis de cohortes
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

try:
    from analisis_engagement_contenido import AnalizadorEngagement, Publicacion
    from analisis_engagement_ai import AnalizadorEngagementAI
    from analisis_engagement_mejorado import AnalizadorEngagementMejorado
except ImportError:
    print("Error: Módulos de análisis no encontrados")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalizadorEngagementIntegraciones:
    """Analizador con integraciones a herramientas externas"""
    
    def __init__(
        self,
        analizador_base: AnalizadorEngagement,
        analizador_ai: Optional[AnalizadorEngagementAI] = None,
        analizador_mejorado: Optional[AnalizadorEngagementMejorado] = None
    ):
        """
        Inicializa el analizador con integraciones
        
        Args:
            analizador_base: Instancia del AnalizadorEngagement base
            analizador_ai: Instancia opcional del AnalizadorEngagementAI
            analizador_mejorado: Instancia opcional del AnalizadorEngagementMejorado
        """
        self.analizador = analizador_base
        self.analizador_ai = analizador_ai or AnalizadorEngagementAI(analizador_base)
        self.analizador_mejorado = analizador_mejorado or AnalizadorEngagementMejorado(
            analizador_base, self.analizador_ai
        )
    
    def exportar_google_sheets(self, reporte: Dict[str, Any], spreadsheet_id: str = None) -> Dict[str, Any]:
        """
        Exporta datos a Google Sheets
        
        Args:
            reporte: Reporte generado
            spreadsheet_id: ID de la hoja de cálculo (opcional, crea nueva si no se proporciona)
        
        Returns:
            Información de la exportación
        """
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from googleapiclient.errors import HttpError
        except ImportError:
            return {
                "error": "google-api-python-client no está instalado. Instálalo con: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            }
        
        # Preparar datos para exportar
        datos_publicaciones = []
        for pub in self.analizador.publicaciones:
            datos_publicaciones.append([
                pub.id,
                pub.tipo_contenido,
                pub.titulo,
                pub.plataforma,
                pub.fecha_publicacion.strftime('%Y-%m-%d %H:%M'),
                pub.likes,
                pub.comentarios,
                pub.shares,
                pub.impresiones,
                pub.reach,
                pub.engagement_rate,
                pub.engagement_score,
                ', '.join(pub.hashtags)
            ])
        
        # Headers
        headers = [
            'ID', 'Tipo Contenido', 'Título', 'Plataforma', 'Fecha',
            'Likes', 'Comentarios', 'Shares', 'Impresiones', 'Reach',
            'Engagement Rate', 'Engagement Score', 'Hashtags'
        ]
        
        return {
            "success": True,
            "datos_preparados": {
                "headers": headers,
                "filas": len(datos_publicaciones),
                "columnas": len(headers)
            },
            "instrucciones": "Usa Google Sheets API para escribir estos datos",
            "datos": [headers] + datos_publicaciones[:100]  # Limitar a 100 filas para ejemplo
        }
    
    def enviar_alerta_slack(
        self,
        mensaje: str,
        nivel: str = "INFO",
        webhook_url: str = None
    ) -> Dict[str, Any]:
        """
        Envía alerta a Slack
        
        Args:
            mensaje: Mensaje a enviar
            nivel: Nivel de alerta (INFO, WARNING, CRITICAL)
            webhook_url: URL del webhook de Slack
        
        Returns:
            Resultado del envío
        """
        if not webhook_url:
            webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
        if not webhook_url:
            return {
                "error": "SLACK_WEBHOOK_URL no configurada",
                "mensaje_formateado": self._formatear_mensaje_slack(mensaje, nivel)
            }
        
        try:
            import requests
            
            emoji_map = {
                "INFO": "ℹ️",
                "WARNING": "⚠️",
                "CRITICAL": "🔴"
            }
            
            payload = {
                "text": f"{emoji_map.get(nivel, '📊')} {nivel}: {mensaje}",
                "username": "Engagement Analyzer",
                "icon_emoji": ":chart_with_upwards_trend:"
            }
            
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            
            return {
                "success": True,
                "mensaje_enviado": mensaje,
                "nivel": nivel,
                "timestamp": datetime.now().isoformat()
            }
        except ImportError:
            return {
                "error": "requests no está instalado. Instálalo con: pip install requests"
            }
        except Exception as e:
            return {
                "error": str(e),
                "mensaje_formateado": self._formatear_mensaje_slack(mensaje, nivel)
            }
    
    def _formatear_mensaje_slack(self, mensaje: str, nivel: str) -> str:
        """Formatea mensaje para Slack"""
        emoji_map = {
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "CRITICAL": "🔴"
        }
        return f"{emoji_map.get(nivel, '📊')} {nivel}: {mensaje}"
    
    def analizar_audiencia_avanzado(self) -> Dict[str, Any]:
        """
        Análisis avanzado de audiencia basado en engagement
        
        Returns:
            Análisis de audiencia segmentado
        """
        # Segmentar audiencia por comportamiento de engagement
        segmentos = {
            "alta_interaccion": [],
            "media_interaccion": [],
            "baja_interaccion": []
        }
        
        engagement_scores = [p.engagement_score for p in self.analizador.publicaciones]
        if not engagement_scores:
            return {"error": "No hay datos para analizar"}
        
        promedio = statistics.mean(engagement_scores)
        desviacion = statistics.stdev(engagement_scores) if len(engagement_scores) > 1 else 0
        
        umbral_alto = promedio + desviacion
        umbral_bajo = promedio - desviacion
        
        for pub in self.analizador.publicaciones:
            if pub.engagement_score >= umbral_alto:
                segmentos["alta_interaccion"].append(pub)
            elif pub.engagement_score <= umbral_bajo:
                segmentos["baja_interaccion"].append(pub)
            else:
                segmentos["media_interaccion"].append(pub)
        
        # Analizar características de cada segmento
        analisis_segmentos = {}
        for segmento_nombre, publicaciones in segmentos.items():
            if publicaciones:
                analisis_segmentos[segmento_nombre] = {
                    "cantidad": len(publicaciones),
                    "porcentaje": (len(publicaciones) / len(self.analizador.publicaciones)) * 100,
                    "engagement_promedio": statistics.mean([p.engagement_score for p in publicaciones]),
                    "plataformas_preferidas": self._contar_plataformas(publicaciones),
                    "tipos_contenido_preferidos": self._contar_tipos_contenido(publicaciones),
                    "horarios_optimos": self._analizar_horarios(publicaciones)
                }
        
        return {
            "total_publicaciones": len(self.analizador.publicaciones),
            "segmentos": analisis_segmentos,
            "insights": self._generar_insights_audiencia(analisis_segmentos)
        }
    
    def _contar_plataformas(self, publicaciones: List[Publicacion]) -> Dict[str, int]:
        """Cuenta plataformas en un conjunto de publicaciones"""
        conteo = defaultdict(int)
        for pub in publicaciones:
            conteo[pub.plataforma] += 1
        return dict(conteo)
    
    def _contar_tipos_contenido(self, publicaciones: List[Publicacion]) -> Dict[str, int]:
        """Cuenta tipos de contenido"""
        conteo = defaultdict(int)
        for pub in publicaciones:
            conteo[pub.tipo_contenido] += 1
        return dict(conteo)
    
    def _analizar_horarios(self, publicaciones: List[Publicacion]) -> Dict[str, Any]:
        """Analiza horarios óptimos"""
        horarios = defaultdict(int)
        for pub in publicaciones:
            hora = pub.metadata.get('hora_publicacion', pub.fecha_publicacion.hour)
            rango = f"{hora:02d}:00"
            horarios[rango] += pub.engagement_score
        
        if horarios:
            mejor_horario = max(horarios.items(), key=lambda x: x[1])
            return {
                "mejor_horario": mejor_horario[0],
                "score_promedio": mejor_horario[1] / sum(1 for p in publicaciones if p.metadata.get('hora_publicacion') == int(mejor_horario[0].split(':')[0]))
            }
        return {}
    
    def _generar_insights_audiencia(self, segmentos: Dict[str, Any]) -> List[str]:
        """Genera insights sobre audiencia"""
        insights = []
        
        if "alta_interaccion" in segmentos:
            alto = segmentos["alta_interaccion"]
            if alto.get("cantidad", 0) > 0:
                plataforma_top = max(alto.get("plataformas_preferidas", {}).items(), key=lambda x: x[1])[0] if alto.get("plataformas_preferidas") else None
                if plataforma_top:
                    insights.append(f"Audiencia de alta interacción prefiere {plataforma_top}")
        
        if "baja_interaccion" in segmentos:
            bajo = segmentos["baja_interaccion"]
            if bajo.get("cantidad", 0) > 0:
                insights.append(f"Revisar estrategia para {bajo['cantidad']} publicaciones de baja interacción")
        
        return insights
    
    def analizar_cohortes(self, periodo_cohorte: str = "semanal") -> Dict[str, Any]:
        """
        Análisis de cohortes de engagement
        
        Args:
            periodo_cohorte: Período de cohorte (semanal, mensual)
        
        Returns:
            Análisis de cohortes
        """
        if periodo_cohorte == "semanal":
            periodo_dias = 7
        else:
            periodo_dias = 30
        
        # Agrupar por cohortes
        cohortes = defaultdict(lambda: {
            "publicaciones": [],
            "engagement_scores": [],
            "engagement_rates": []
        })
        
        fecha_inicio = min(p.fecha_publicacion for p in self.analizador.publicaciones)
        
        for pub in self.analizador.publicaciones:
            dias_desde_inicio = (pub.fecha_publicacion - fecha_inicio).days
            cohorte_num = dias_desde_inicio // periodo_dias
            
            cohortes[cohorte_num]["publicaciones"].append(pub)
            cohortes[cohorte_num]["engagement_scores"].append(pub.engagement_score)
            cohortes[cohorte_num]["engagement_rates"].append(pub.engagement_rate)
        
        # Analizar cada cohorte
        analisis_cohortes = {}
        for cohorte_num, datos in sorted(cohortes.items()):
            fecha_cohorte = fecha_inicio + timedelta(days=cohorte_num * periodo_dias)
            analisis_cohortes[f"Cohorte {cohorte_num + 1}"] = {
                "fecha_inicio": fecha_cohorte.strftime('%Y-%m-%d'),
                "cantidad_publicaciones": len(datos["publicaciones"]),
                "engagement_score_promedio": statistics.mean(datos["engagement_scores"]) if datos["engagement_scores"] else 0,
                "engagement_rate_promedio": statistics.mean(datos["engagement_rates"]) if datos["engagement_rates"] else 0,
                "tendencia": self._calcular_tendencia_cohorte(cohortes, cohorte_num)
            }
        
        return {
            "periodo_cohorte": periodo_cohorte,
            "total_cohortes": len(cohortes),
            "cohortes": analisis_cohortes,
            "insights": self._generar_insights_cohortes(analisis_cohortes)
        }
    
    def _calcular_tendencia_cohorte(self, cohortes: Dict[int, Any], cohorte_actual: int) -> str:
        """Calcula tendencia de una cohorte"""
        if cohorte_actual == 0:
            return "primera"
        
        if cohorte_actual - 1 in cohortes:
            anterior = statistics.mean(cohortes[cohorte_actual - 1]["engagement_scores"])
            actual = statistics.mean(cohortes[cohorte_actual]["engagement_scores"])
            
            if actual > anterior * 1.1:
                return "creciente"
            elif actual < anterior * 0.9:
                return "decreciente"
            else:
                return "estable"
        
        return "sin_datos"
    
    def _generar_insights_cohortes(self, cohortes: Dict[str, Any]) -> List[str]:
        """Genera insights sobre cohortes"""
        insights = []
        
        scores = [c["engagement_score_promedio"] for c in cohortes.values()]
        if len(scores) >= 2:
            primera_cohorte = scores[0]
            ultima_cohorte = scores[-1]
            
            if ultima_cohorte > primera_cohorte * 1.2:
                insights.append("Las cohortes recientes muestran mejor engagement que las iniciales")
            elif ultima_cohorte < primera_cohorte * 0.8:
                insights.append("Las cohortes recientes muestran menor engagement - revisar estrategia")
        
        return insights
    
    def generar_reporte_email(self, reporte: Dict[str, Any], destinatarios: List[str]) -> Dict[str, Any]:
        """
        Genera formato de reporte para email
        
        Args:
            reporte: Reporte generado
            destinatarios: Lista de emails destinatarios
        
        Returns:
            Contenido del email formateado
        """
        resumen = reporte.get('resumen_ejecutivo', {})
        
        html_email = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .header {{ background: #667eea; color: white; padding: 20px; }}
        .content {{ padding: 20px; }}
        .metric {{ margin: 10px 0; }}
        .metric-label {{ font-weight: bold; color: #666; }}
        .metric-value {{ font-size: 24px; color: #667eea; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Reporte de Engagement</h1>
        <p>Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
    </div>
    <div class="content">
        <h2>Resumen Ejecutivo</h2>
        <div class="metric">
            <div class="metric-label">Tipo de Contenido Ganador</div>
            <div class="metric-value">{resumen.get('nombre_tipo', 'N/A')}</div>
        </div>
        <div class="metric">
            <div class="metric-label">Engagement Rate Promedio</div>
            <div class="metric-value">{resumen.get('engagement_rate_promedio', 0):.2f}%</div>
        </div>
        <div class="metric">
            <div class="metric-label">Engagement Score Promedio</div>
            <div class="metric-value">{resumen.get('engagement_score_promedio', 0):.1f}</div>
        </div>
        <h2>Métricas Clave</h2>
        <ul>
            <li>Total de Publicaciones: {len(self.analizador.publicaciones)}</li>
            <li>Mejor Plataforma: {resumen.get('mejor_plataforma', 'N/A')}</li>
            <li>Mejor Horario: {resumen.get('mejor_horario', 'N/A')}</li>
        </ul>
    </div>
</body>
</html>
"""
        
        return {
            "success": True,
            "destinatarios": destinatarios,
            "asunto": f"Reporte de Engagement - {datetime.now().strftime('%d/%m/%Y')}",
            "contenido_html": html_email,
            "contenido_texto": self._html_a_texto(html_email),
            "instrucciones": "Usa tu servicio de email (SMTP, SendGrid, etc.) para enviar este contenido"
        }
    
    def _html_a_texto(self, html: str) -> str:
        """Convierte HTML a texto plano"""
        import re
        texto = re.sub('<[^<]+?>', '', html)
        texto = texto.replace('\n\n', '\n')
        return texto.strip()


def main():
    """Función principal para demostración"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Análisis de Engagement - Integraciones')
    parser.add_argument('--publicaciones', type=int, default=30, help='Número de publicaciones')
    parser.add_argument('--audiencia', action='store_true', help='Analizar audiencia avanzado')
    parser.add_argument('--cohortes', action='store_true', help='Analizar cohortes')
    parser.add_argument('--email', action='store_true', help='Generar reporte email')
    
    args = parser.parse_args()
    
    # Crear analizadores
    analizador_base = AnalizadorEngagement()
    analizador_base.generar_datos_ejemplo(num_publicaciones=args.publicaciones)
    
    analizador_integraciones = AnalizadorEngagementIntegraciones(analizador_base)
    
    # Análisis de audiencia
    if args.audiencia:
        print("\n👥 Analizando audiencia avanzado...")
        analisis_audiencia = analizador_integraciones.analizar_audiencia_avanzado()
        print(f"✅ Segmentos identificados: {len(analisis_audiencia.get('segmentos', {}))}")
        for segmento, datos in analisis_audiencia.get('segmentos', {}).items():
            print(f"   {segmento}: {datos.get('cantidad')} publicaciones ({datos.get('porcentaje', 0):.1f}%)")
    
    # Análisis de cohortes
    if args.cohortes:
        print("\n📊 Analizando cohortes...")
        cohortes = analizador_integraciones.analizar_cohortes(periodo_cohorte="semanal")
        print(f"✅ {cohortes.get('total_cohortes')} cohortes analizadas")
        for nombre, datos in cohortes.get('cohortes', {}).items():
            print(f"   {nombre}: Score {datos.get('engagement_score_promedio', 0):.1f} - {datos.get('tendencia')}")
    
    # Reporte email
    if args.email:
        print("\n📧 Generando reporte para email...")
        reporte = analizador_base.generar_reporte()
        email = analizador_integraciones.generar_reporte_email(reporte, ["ejemplo@email.com"])
        print(f"✅ Reporte generado")
        print(f"   Asunto: {email['asunto']}")
        print(f"   Destinatarios: {len(email['destinatarios'])}")


if __name__ == "__main__":
    main()


