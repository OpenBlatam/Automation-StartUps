#!/usr/bin/env python3
"""
Generador de PDFs con guías de replicación de videos de IA en español
Crea PDFs profesionales con instrucciones paso a paso para replicar videos
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("reportlab no está instalado. Instálalo con: pip install reportlab")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai no está instalado. La traducción automática no estará disponible.")


class PDFReplicationGuideGenerator:
    """Generador de PDFs con guías de replicación"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Inicializa el generador de PDFs
        
        Args:
            openai_api_key: API key de OpenAI para traducción (opcional)
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab es requerido. Instálalo con: pip install reportlab")
        
        self.openai_client = None
        if openai_api_key:
            self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
            if OPENAI_AVAILABLE and self.openai_api_key:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                logger.info("Cliente OpenAI inicializado para traducción")
    
    def translate_to_spanish(self, text: str) -> str:
        """
        Traduce texto a español usando OpenAI
        
        Args:
            text: Texto a traducir
            
        Returns:
            Texto traducido al español
        """
        if not self.openai_client:
            logger.warning("OpenAI no disponible, devolviendo texto original")
            return text
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un traductor profesional especializado en contenido técnico de IA. Traduce el texto al español manteniendo el significado técnico y el tono profesional."
                    },
                    {
                        "role": "user",
                        "content": f"Traduce el siguiente texto al español:\n\n{text}"
                    }
                ],
                temperature=0.3
            )
            
            translated = response.choices[0].message.content.strip()
            logger.info("Texto traducido exitosamente")
            return translated
            
        except Exception as e:
            logger.error(f"Error en traducción: {e}")
            return text
    
    def generate_replication_guide(
        self,
        transcript: str,
        video_info: Dict[str, Any],
        output_path: str,
        translate: bool = True
    ) -> str:
        """
        Genera una guía de replicación en PDF
        
        Args:
            transcript: Transcripción del video
            video_info: Información del video (título, URL, etc.)
            output_path: Ruta donde guardar el PDF
            translate: Si traducir el contenido al español
            
        Returns:
            Ruta del PDF generado
        """
        # Traducir contenido si es necesario
        if translate and self.openai_client:
            logger.info("Traduciendo contenido al español...")
            video_title = self.translate_to_spanish(video_info.get('title', 'Video sin título'))
            video_description = self.translate_to_spanish(video_info.get('description', ''))
            transcript_es = self.translate_to_spanish(transcript)
        else:
            video_title = video_info.get('title', 'Video sin título')
            video_description = video_info.get('description', '')
            transcript_es = transcript
        
        # Crear documento PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=1,  # Centrado
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            textColor=HexColor('#333333'),
            spaceAfter=12,
            leading=16,
            fontName='Helvetica'
        )
        
        code_style = ParagraphStyle(
            'CustomCode',
            parent=styles['Code'],
            fontSize=10,
            textColor=HexColor('#2c3e50'),
            backColor=HexColor('#f8f9fa'),
            borderColor=HexColor('#dee2e6'),
            borderWidth=1,
            borderPadding=8,
            spaceAfter=12,
            fontName='Courier'
        )
        
        # Construir contenido
        story = []
        
        # Portada
        story.append(Spacer(1, 3*cm))
        story.append(Paragraph("Guía de Replicación", title_style))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("Video de Inteligencia Artificial", styles['Normal']))
        story.append(PageBreak())
        
        # Información del video
        story.append(Paragraph("Información del Video", heading_style))
        
        video_data = [
            ['<b>Título:</b>', video_title],
            ['<b>URL:</b>', video_info.get('url', 'N/A')],
            ['<b>Canal:</b>', video_info.get('channel', 'N/A')],
            ['<b>Visualizaciones:</b>', f"{video_info.get('view_count', 0):,}"],
            ['<b>Me gusta:</b>', f"{video_info.get('like_count', 0):,}"],
            ['<b>Idioma original:</b>', video_info.get('language', 'Desconocido')],
            ['<b>Fecha de publicación:</b>', video_info.get('published_at', 'N/A')[:10] if video_info.get('published_at') else 'N/A'],
        ]
        
        video_table = Table(video_data, colWidths=[4*cm, 12*cm])
        video_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdc3c7')),
        ]))
        story.append(video_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Descripción
        if video_description:
            story.append(Paragraph("Descripción", subheading_style))
            story.append(Paragraph(video_description[:500] + ('...' if len(video_description) > 500 else ''), body_style))
            story.append(Spacer(1, 0.3*cm))
        
        story.append(PageBreak())
        
        # Transcripción completa
        story.append(Paragraph("Transcripción Completa del Video", heading_style))
        story.append(Paragraph("A continuación encontrarás la transcripción completa del video traducida al español:", body_style))
        story.append(Spacer(1, 0.3*cm))
        
        # Dividir transcripción en párrafos
        paragraphs = transcript_es.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
                story.append(Spacer(1, 0.2*cm))
        
        story.append(PageBreak())
        
        # Guía de replicación paso a paso
        story.append(Paragraph("Guía de Replicación Paso a Paso", heading_style))
        story.append(Paragraph("Sigue estos pasos para replicar este video en español:", body_style))
        story.append(Spacer(1, 0.3*cm))
        
        # Generar pasos usando IA si está disponible
        replication_steps = self._generate_replication_steps(transcript_es, video_info)
        
        for i, step in enumerate(replication_steps, 1):
            story.append(Paragraph(f"Paso {i}: {step['title']}", subheading_style))
            story.append(Paragraph(step['description'], body_style))
            if step.get('code'):
                story.append(Paragraph(step['code'], code_style))
            story.append(Spacer(1, 0.3*cm))
        
        story.append(PageBreak())
        
        # Recursos adicionales
        story.append(Paragraph("Recursos Adicionales", heading_style))
        resources = [
            "Herramientas mencionadas en el video",
            "Enlaces de referencia",
            "Documentación relacionada",
            "Comunidades y foros de soporte"
        ]
        
        for resource in resources:
            story.append(Paragraph(f"• {resource}", body_style))
        
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(f"<i>Guía generada el {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>", styles['Normal']))
        
        # Generar PDF
        doc.build(story)
        logger.info(f"PDF generado exitosamente: {output_path}")
        
        return output_path
    
    def _generate_replication_steps(self, transcript: str, video_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Genera pasos de replicación usando IA
        
        Args:
            transcript: Transcripción del video
            video_info: Información del video
            
        Returns:
            Lista de pasos de replicación
        """
        if not self.openai_client:
            # Pasos genéricos si no hay IA
            return [
                {
                    'title': 'Preparar el entorno',
                    'description': 'Configura el entorno necesario según el contenido del video.',
                    'code': None
                },
                {
                    'title': 'Revisar la transcripción',
                    'description': 'Lee cuidadosamente la transcripción completa para entender el proceso.',
                    'code': None
                },
                {
                    'title': 'Adaptar al español',
                    'description': 'Traduce y adapta el contenido al contexto español.',
                    'code': None
                },
                {
                    'title': 'Crear el video',
                    'description': 'Produce el video siguiendo los pasos descritos.',
                    'code': None
                }
            ]
        
        try:
            prompt = f"""Basándote en la siguiente transcripción de un video sobre IA, genera una guía paso a paso detallada para replicar el contenido en español. 

Transcripción:
{transcript[:2000]}

Genera entre 5-8 pasos claros y específicos. Cada paso debe tener:
- Un título descriptivo
- Una descripción detallada de qué hacer
- Código o comandos si es relevante

Responde en formato JSON con esta estructura:
{{
  "steps": [
    {{
      "title": "Título del paso",
      "description": "Descripción detallada",
      "code": "código o comandos si aplica"
    }}
  ]
}}
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en crear guías técnicas paso a paso. Genera contenido claro, específico y accionable."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7
            )
            
            import json
            result_text = response.choices[0].message.content.strip()
            # Limpiar markdown si existe
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            
            result = json.loads(result_text)
            steps = result.get('steps', [])
            
            logger.info(f"Generados {len(steps)} pasos de replicación")
            return steps
            
        except Exception as e:
            logger.error(f"Error generando pasos: {e}")
            # Retornar pasos genéricos
            return [
                {
                    'title': 'Revisar contenido original',
                    'description': 'Estudia el video original y su transcripción para entender el concepto.',
                    'code': None
                },
                {
                    'title': 'Adaptar al contexto español',
                    'description': 'Traduce y adapta el contenido manteniendo el significado técnico.',
                    'code': None
                }
            ]


def main():
    parser = argparse.ArgumentParser(description='Genera PDF con guía de replicación de video')
    parser.add_argument('transcript_file', help='Archivo JSON con la transcripción')
    parser.add_argument('video_info_file', help='Archivo JSON con información del video')
    parser.add_argument('--output', '-o', help='Archivo PDF de salida')
    parser.add_argument('--no-translate', action='store_true', help='No traducir contenido')
    parser.add_argument('--openai-api-key', help='API key de OpenAI (o usar OPENAI_API_KEY env var)')
    
    args = parser.parse_args()
    
    # Cargar transcripción
    with open(args.transcript_file, 'r', encoding='utf-8') as f:
        transcript_data = json.load(f)
    
    # Cargar información del video
    with open(args.video_info_file, 'r', encoding='utf-8') as f:
        video_info = json.load(f)
    
    # Determinar ruta de salida
    if args.output:
        output_path = args.output
    else:
        video_id = video_info.get('id', 'video')
        output_path = f"replication_guide_{video_id}.pdf"
    
    # Generar PDF
    generator = PDFReplicationGuideGenerator(openai_api_key=args.openai_api_key)
    
    transcript_text = transcript_data.get('text', '')
    if not transcript_text:
        logger.error("No se encontró texto en la transcripción")
        return 1
    
    try:
        pdf_path = generator.generate_replication_guide(
            transcript=transcript_text,
            video_info=video_info,
            output_path=output_path,
            translate=not args.no_translate
        )
        
        logger.info(f"PDF generado exitosamente: {pdf_path}")
        return 0
        
    except Exception as e:
        logger.error(f"Error generando PDF: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())




