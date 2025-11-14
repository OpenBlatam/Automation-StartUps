#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGPT Queue Marketing Plan PDF Generator
Creates a comprehensive PDF marketing plan based on Diffusion of Innovations theory
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
from datetime import datetime

def create_marketing_plan_pdf():
    """Create the comprehensive marketing plan PDF for ChatGPT Queue"""
    
    # Create PDF document
    filename = "ChatGPT_Queue_Marketing_Plan_Enhanced.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2E86AB')
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#A23B72')
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=12,
        textColor=colors.HexColor('#F18F01')
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=6,
        spaceBefore=8,
        textColor=colors.HexColor('#C73E1D')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=4,
        leftIndent=20,
        bulletIndent=10
    )
    
    # Build content
    story = []
    
    # Title Page
    story.append(Paragraph("🚀 Plan de Marketing Mejorado para ChatGPT Queue", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Extensión de Chrome - Teoría de Difusión de Innovaciones", heading1_style))
    story.append(Spacer(1, 30))
    
    # Executive Summary
    story.append(Paragraph("📋 Resumen Ejecutivo", heading1_style))
    story.append(Paragraph(
        "Este plan de marketing está diseñado específicamente para ChatGPT Queue, una extensión de Chrome que permite a los usuarios hacer cola de mensajes para ChatGPT, ahorrando tiempo significativo. El plan se basa en la Teoría de Difusión de Innovaciones de Everett Rogers, segmentando el mercado en cinco categorías de adoptantes con estrategias específicas para cada grupo.",
        body_style
    ))
    story.append(Spacer(1, 20))
    
    # Table of Contents
    story.append(Paragraph("📋 Tabla de Contenidos", heading1_style))
    
    toc_data = [
        ['Sección', 'Página', 'Descripción'],
        ['1. Innovadores', '3', 'Estrategias de Lanzamiento y Comunidad Tech'],
        ['2. Primeros Adoptantes', '8', 'Marketing de Influencia y Contenido Educativo'],
        ['3. Mayoría Temprana', '15', 'Crecimiento Orgánico y Conversión'],
        ['4. Mayoría Tardía', '22', 'Marketing Masivo y Validación Social'],
        ['5. Rezagados', '28', 'Educación y Adopción Gradual'],
        ['Métricas y KPIs', '33', 'Indicadores de Éxito por Segmento'],
        ['Cronograma', '35', 'Fases de Implementación'],
        ['Presupuesto', '37', 'Inversión por Fase']
    ]
    
    toc_table = Table(toc_data, colWidths=[2*inch, 1*inch, 3*inch])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(toc_table)
    story.append(PageBreak())
    
    # Section 1: Innovadores
    story.append(Paragraph("1. 🎯 INNOVADORES (2.5% del mercado)", heading1_style))
    
    story.append(Paragraph("Perfil Demográfico Detallado", heading2_style))
    innovadores_profile = [
        "• Edad: 25-40 años",
        "• Ingresos: $75K+ anuales", 
        "• Profesión: Desarrolladores, emprendedores tech, early adopters de IA",
        "• Comportamiento: Activos en GitHub, Reddit, Hacker News, Discord tech"
    ]
    
    for item in innovadores_profile:
        story.append(Paragraph(item, bullet_style))
    
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Estrategias Específicas Mejoradas", heading2_style))
    
    story.append(Paragraph("1.1 Lanzamiento en Product Hunt (Día 0)", heading3_style))
    story.append(Paragraph("Objetivo: Top 5 del día, 500+ votos", body_style))
    
    ph_strategies = [
        "Pre-lanzamiento (2 semanas antes): Crear teaser en redes sociales con countdown",
        "Reclutar 20+ 'hunters' de confianza",
        "Preparar assets: GIFs, videos, screenshots HD",
        "Escribir pitch perfecto (máximo 60 caracteres)",
        "Día del lanzamiento: Publicar a las 12:01 AM PST (hora óptima)",
        "Activar red personal inmediatamente",
        "Monitorear en tiempo real y responder comentarios",
        "Compartir en 10+ comunidades simultáneamente"
    ]
    
    for item in ph_strategies:
        story.append(Paragraph(f"• {item}", bullet_style))
    
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("1.2 Estrategia Reddit Multi-Subreddit", heading3_style))
    story.append(Paragraph("Subreddits objetivo con horarios óptimos:", body_style))
    
    reddit_data = [
        ['Subreddit', 'Miembros', 'Horario Óptimo'],
        ['r/ChatGPT', '2M+', 'Martes 10 AM EST'],
        ['r/ProductivityApps', '150K+', 'Miércoles 2 PM EST'],
        ['r/ChromeExtensions', '50K+', 'Jueves 11 AM EST'],
        ['r/entrepreneur', '1M+', 'Viernes 9 AM EST'],
        ['r/AI', '500K+', 'Lunes 3 PM EST']
    ]
    
    reddit_table = Table(reddit_data, colWidths=[1.5*inch, 1*inch, 1.5*inch])
    reddit_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A23B72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(reddit_table)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("1.3 Estrategia Hacker News", heading3_style))
    hn_strategies = [
        "Título optimizado: 'Show HN: ChatGPT Queue - Chrome extension that queues messages to save time'",
        "Timing: Martes-Jueves, 8-10 AM PST",
        "Contenido: Enfoque técnico, código abierto parcial, métricas de rendimiento"
    ]
    
    for item in hn_strategies:
        story.append(Paragraph(f"• {item}", bullet_style))
    
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("1.4 Programa Beta Exclusivo", heading3_style))
    beta_structure = [
        "50 beta testers seleccionados de comunidades tech",
        "Acceso gratuito por 3 meses",
        "Feedback semanal obligatorio",
        "Recompensas: Descuento 50% permanente + mención en créditos"
    ]
    
    for item in beta_structure:
        story.append(Paragraph(f"• {item}", bullet_style))
    
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("1.5 Pricing Strategy Innovadores", heading3_style))
    pricing_data = [
        ['Estrategia', 'Precio', 'Condiciones'],
        ['Precio inicial', '$29.99', 'Premium positioning'],
        ['Early bird', '$19.99', 'Primeros 100 usuarios'],
        ['Beta testers', '$9.99', 'Precio especial permanente'],
        ['Bundle', '$49.99', 'ChatGPT Queue + 2 extensiones complementarias']
    ]
    
    pricing_table = Table(pricing_data, colWidths=[1.5*inch, 1*inch, 2*inch])
    pricing_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F18F01')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(pricing_table)
    story.append(PageBreak())
    
    # Section 2: Early Adopters
    story.append(Paragraph("2. ⚡ PRIMEROS ADOPTANTES (13.5% del mercado)", heading1_style))
    
    story.append(Paragraph("Perfil Demográfico Detallado", heading2_style))
    early_adopters_profile = [
        "• Edad: 30-45 años",
        "• Ingresos: $60K+ anuales",
        "• Profesión: Consultores, coaches, content creators, managers",
        "• Comportamiento: Influencers en LinkedIn, activos en podcasts, lectores de newsletters"
    ]
    
    for item in early_adopters_profile:
        story.append(Paragraph(item, bullet_style))
    
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Estrategias Específicas Mejoradas", heading2_style))
    
    story.append(Paragraph("2.1 Programa de Influencers Micro y Macro", heading3_style))
    
    influencer_data = [
        ['Tipo', 'Presupuesto', 'Target', 'Compensación', 'Deliverables'],
        ['Micro (10K-100K)', '$2,000/mes', '20 influencers', '$100 + 20%', '1 post + 3 stories'],
        ['Macro (100K+)', '$5,000/mes', '5 influencers', '$500 + 15%', '1 video + 1 post + 1 story']
    ]
    
    influencer_table = Table(influencer_data, colWidths=[1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    influencer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A23B72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(influencer_table)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("2.2 Estrategia de Contenido Educativo", heading3_style))
    story.append(Paragraph("Blog Content Calendar (3 posts/semana):", body_style))
    
    content_calendar = [
        "Lunes: '5 formas de maximizar ChatGPT con colas de mensajes'",
        "Miércoles: 'Caso de estudio: Cómo [empresa] ahorró 10 horas/semana'",
        "Viernes: 'Comparativa: ChatGPT Queue vs alternativas'"
    ]
    
    for item in content_calendar:
        story.append(Paragraph(f"• {item}", bullet_style))
    
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("YouTube Strategy:", body_style))
    youtube_strategy = [
        "Canal propio: 2 videos/semana",
        "Colaboraciones: 1 video/semana con influencers",
        "SEO: Optimizar para 'ChatGPT productivity', 'AI time management'"
    ]
    
    for item in youtube_strategy:
        story.append(Paragraph(f"• {item}", bullet_style))
    
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("2.3 Programa de Referidos Avanzado", heading3_style))
    referral_structure = [
        "Nivel 1: 30% comisión por referido directo",
        "Nivel 2: 10% comisión por referido de referido",
        "Bonificaciones: $50 bonus por cada 10 referidos",
        "Herramientas: Landing pages personalizadas, códigos de tracking"
    ]
    
    for item in referral_structure:
        story.append(Paragraph(f"• {item}", bullet_style))
    
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("2.4 Webinar Series 'AI Productivity Masterclass'", heading3_style))
    webinar_structure = [
        "Frecuencia: 2 webinars/mes",
        "Duración: 45 minutos",
        "Formato: 30 min presentación + 15 min Q&A",
        "Temas: 'Maximizando ChatGPT para profesionales', 'Automatización de tareas con IA', 'ROI de herramientas de productividad'"
    ]
    
    for item in webinar_structure:
        story.append(Paragraph(f"• {item}", bullet_style))
    
    story.append(PageBreak())
    
    # Section 3: Early Majority
    story.append(Paragraph("3. 📈 MAYORÍA TEMPRANA (34% del mercado)", heading1_style))
    
    story.append(Paragraph("Perfil Demográfico Detallado", heading2_style))
    early_majority_profile = [
        "• Edad: 25-50 años",
        "• Ingresos: $40K+ anuales",
        "• Profesión: Profesionales, small business owners, freelancers",
        "• Comportamiento: Buscan en Google, leen reviews, comparan precios"
    ]
    
    for item in early_majority_profile:
        story.append(Paragraph(item, bullet_style))
    
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Estrategias Específicas Mejoradas", heading2_style))
    
    story.append(Paragraph("3.1 Estrategia SEO Avanzada", heading3_style))
    story.append(Paragraph("Keywords objetivo (volumen mensual):", body_style))
    
    seo_keywords = [
        "'ChatGPT productivity tools' (8,100 búsquedas)",
        "'Chrome extension queue messages' (1,300 búsquedas)",
        "'AI time management tools' (2,900 búsquedas)",
        "'ChatGPT automation' (4,400 búsquedas)"
    ]
    
    for item in seo_keywords:
        story.append(Paragraph(f"• {item}", bullet_style))
    
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("Content Strategy:", body_style))
    content_strategy = [
        "Pillar content: 'Guía completa de productividad con ChatGPT' (5,000 palabras)",
        "Cluster content: 20 artículos de 1,500 palabras cada uno",
        "Long-tail keywords: 50 artículos de 800 palabras"
    ]
    
    for item in content_strategy:
        story.append(Paragraph(f"• {item}", bullet_style))
    
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("3.2 Modelo Freemium Optimizado", heading3_style))
    
    freemium_data = [
        ['Tier', 'Precio', 'Características'],
        ['Free', '$0', '5 mensajes/día, funciones básicas, soporte email'],
        ['Pro', '$9.99/mes', 'Mensajes ilimitados, programación avanzada, analytics'],
        ['Lifetime', '$49.99', 'Todas las funciones Pro, actualizaciones de por vida']
    ]
    
    freemium_table = Table(freemium_data, colWidths=[1*inch, 1*inch, 3*inch])
    freemium_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F18F01')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(freemium_table)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("3.3 Estrategia de Paid Advertising", heading3_style))
    
    ad_strategies = [
        "Google Ads (Presupuesto: $3,000/mes): Search campaigns, Display campaigns, YouTube ads",
        "Facebook/Instagram Ads (Presupuesto: $2,000/mes): Lookalike audiences, Interest targeting, Retargeting"
    ]
    
    for item in ad_strategies:
        story.append(Paragraph(f"• {item}", bullet_style))
    
    story.append(PageBreak())
    
    # Section 4: Late Majority
    story.append(Paragraph("4. 🏢 MAYORÍA TARDÍA (34% del mercado)", heading1_style))
    
    story.append(Paragraph("Perfil Demográfico Detallado", heading2_style))
    late_majority_profile = [
        "• Edad: 35-60 años",
        "• Ingresos: $30K+ anuales",
        "• Profesión: Empleados corporativos, managers, small business owners",
        "• Comportamiento: Prefieren marcas establecidas, buscan garantías, sensibles al precio"
    ]
    
    for item in late_majority_profile:
        story.append(Paragraph(item, bullet_style))
    
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Estrategias Específicas Mejoradas", heading2_style))
    
    story.append(Paragraph("4.1 Estrategia de Validación Social Masiva", heading3_style))
    validation_strategies = [
        "Video testimonials: 50+ videos de 30 segundos",
        "Case studies: 20+ estudios detallados con métricas",
        "User count: Destacar '50,000+ usuarios satisfechos'",
        "Awards: Buscar premios de productividad/tech"
    ]
    
    for item in validation_strategies:
        story.append(Paragraph(f"• {item}", bullet_style))
    
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("4.2 Marketing Tradicional Digital", heading3_style))
    
    traditional_marketing = [
        "Podcast Sponsorships: Target business, productivity, technology podcasts ($5,000/mes)",
        "Newsletter Sponsorships: Target business, productivity, tech newsletters ($3,000/mes)",
        "Trade Shows: Exhibit at business productivity and technology conferences",
        "Direct Mail: Target business owners and professionals"
    ]
    
    for item in traditional_marketing:
        story.append(Paragraph(f"• {item}", bullet_style))
    
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("4.3 Estrategia de Precios Competitivos", heading3_style))
    
    competitive_pricing = [
        "Basic: $4.99/mes (funciones esenciales)",
        "Pro: $9.99/mes (funciones completas)",
        "Business: $19.99/mes (equipos hasta 10 usuarios)",
        "Enterprise: $49.99/mes (equipos ilimitados + soporte dedicado)"
    ]
    
    for item in competitive_pricing:
        story.append(Paragraph(f"• {item}", bullet_style))
    
    story.append(PageBreak())
    
    # Section 5: Laggards
    story.append(Paragraph("5. 🔄 REZAGADOS (16% del mercado)", heading1_style))
    
    story.append(Paragraph("Perfil Demográfico Detallado", heading2_style))
    laggards_profile = [
        "• Edad: 45+ años",
        "• Ingresos: $25K+ anuales",
        "• Profesión: Empleados tradicionales, administradores, usuarios básicos",
        "• Comportamiento: Resistentes al cambio, prefieren métodos tradicionales"
    ]
    
    for item in laggards_profile:
        story.append(Paragraph(item, bullet_style))
    
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Estrategias Específicas Mejoradas", heading2_style))
    
    story.append(Paragraph("5.1 Estrategia de Educación Gradual", heading3_style))
    story.append(Paragraph("Programa de Onboarding Extendido:", body_style))
    
    onboarding_program = [
        "Semana 1: Email de bienvenida + video introductorio",
        "Semana 2: Tutorial básico + caso de uso simple",
        "Semana 3: Funciones intermedias + tips de productividad",
        "Semana 4: Funciones avanzadas + optimización"
    ]
    
    for item in onboarding_program:
        story.append(Paragraph(f"• {item}", bullet_style))
    
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("Contenido Educativo Simplificado:", body_style))
    educational_content = [
        "Glosario de términos: IA, cola, programación, etc.",
        "Comparaciones: 'Es como programar emails, pero para ChatGPT'",
        "Analogías: 'Como tener un asistente que envía mensajes por ti'"
    ]
    
    for item in educational_content:
        story.append(Paragraph(f"• {item}", bullet_style))
    
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("5.2 Estrategia de Precios Mínimos", heading3_style))
    minimal_pricing = [
        "Free forever: Versión básica sin límites de tiempo",
        "Premium: $2.99/mes (precio mínimo)",
        "Lifetime: $19.99 (precio único, sin suscripción)",
        "Family: $39.99 (hasta 5 usuarios)"
    ]
    
    for item in minimal_pricing:
        story.append(Paragraph(f"• {item}", bullet_style))
    
    story.append(PageBreak())
    
    # Metrics and KPIs Section
    story.append(Paragraph("📊 Métricas de Éxito por Segmento", heading1_style))
    
    metrics_data = [
        ['Segmento', 'Métrica Clave', 'Objetivo', 'Medición'],
        ['Innovadores', 'Product Hunt ranking', 'Top 5 del día', 'Ranking diario'],
        ['Innovadores', 'Tech media coverage', '10+ artículos en 30 días', 'Conteo de menciones'],
        ['Primeros Adoptantes', 'Influencer partnerships', '25+ colaboraciones activas', 'Número de partnerships'],
        ['Primeros Adoptantes', 'Content engagement', '10%+ engagement rate', 'Analytics de redes'],
        ['Mayoría Temprana', 'Organic traffic', '50%+ del tráfico total', 'Google Analytics'],
        ['Mayoría Temprana', 'Conversion rate', '5%+ de visitantes a usuarios', 'Funnel de conversión'],
        ['Mayoría Tardía', 'Brand recognition', '60%+ awareness en target', 'Encuestas de marca'],
        ['Mayoría Tardía', 'Customer acquisition cost', '<$25', 'Costo por adquisición'],
        ['Rezagados', 'Adoption rate', '20%+ después de 12 meses', 'Tasa de adopción']
    ]
    
    metrics_table = Table(metrics_data, colWidths=[1.2*inch, 1.5*inch, 1.2*inch, 1.1*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 20))
    
    # Implementation Timeline
    story.append(Paragraph("🗓️ Cronograma de Implementación Mejorado", heading1_style))
    
    timeline_data = [
        ['Fase', 'Duración', 'Enfoque', 'Actividades Clave'],
        ['Fase 1: Lanzamiento', 'Meses 1-3', 'Innovadores + Primeros Adoptantes', 'Product Hunt, Reddit, Influencers'],
        ['Fase 2: Crecimiento', 'Meses 4-9', 'Mayoría Temprana', 'SEO, Freemium, Paid Ads'],
        ['Fase 3: Escala', 'Meses 10-18', 'Mayoría Tardía', 'Mass Marketing, Partnerships'],
        ['Fase 4: Madurez', 'Meses 19-24', 'Rezagados + Retención', 'Education, Support Scaling']
    ]
    
    timeline_table = Table(timeline_data, colWidths=[1*inch, 1*inch, 1.5*inch, 2*inch])
    timeline_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A23B72')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(timeline_table)
    story.append(Spacer(1, 20))
    
    # Budget Section
    story.append(Paragraph("💰 Presupuesto Total por Fase", heading1_style))
    
    budget_data = [
        ['Fase', 'Presupuesto', 'ROI Esperado', 'Actividades Principales'],
        ['Fase 1: Lanzamiento', '$15,000', '300%', 'Product Hunt, Influencers, Content'],
        ['Fase 2: Crecimiento', '$35,000', '250%', 'Paid Ads, SEO, Affiliate Program'],
        ['Fase 3: Escala', '$50,000', '200%', 'Mass Marketing, PR, Partnerships'],
        ['Fase 4: Madurez', '$25,000', '150%', 'Education, Support, Research'],
        ['TOTAL', '$125,000', '300%+', '24 meses de implementación']
    ]
    
    budget_table = Table(budget_data, colWidths=[1*inch, 1*inch, 1*inch, 2*inch])
    budget_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F18F01')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(budget_table)
    story.append(Spacer(1, 20))
    
    # Conclusion
    story.append(Paragraph("🎯 Conclusión", heading1_style))
    story.append(Paragraph(
        "Este plan de marketing mejorado proporciona estrategias específicas, métricas claras y un cronograma detallado para maximizar la adopción de ChatGPT Queue en cada segmento del mercado. Con un enfoque particular en la propuesta de valor única de ahorro de tiempo a través de la cola de mensajes de ChatGPT, el plan está diseñado para generar un ROI del 300%+ en 24 meses.",
        body_style
    ))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Generado el: {datetime.now().strftime('%d de %B de %Y')}", body_style))
    story.append(Paragraph("© 2024 - ChatGPT Queue Marketing Plan. Todos los derechos reservados.", body_style))
    
    # Build PDF
    doc.build(story)
    print(f"✅ PDF creado exitosamente: {filename}")
    return filename

if __name__ == "__main__":
    create_marketing_plan_pdf()
