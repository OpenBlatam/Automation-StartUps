#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import HexColor
from datetime import datetime

def create_blockchain_system():
    """Genera un sistema de blockchain para Bioclones"""
    
    # Configuración del documento de blockchain
    doc = SimpleDocTemplate(
        "sistema_blockchain_bioclones.pdf", 
        pagesize=A4,
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=3*cm, 
        bottomMargin=2.5*cm,
        title="Sistema de Blockchain - Bioclones",
        author="Sistema de Blockchain Automático",
        subject="Ciencia Ficción - Blockchain - Web3 - NFT",
        creator="Sistema de Blockchain Digital",
        keywords="blockchain, web3, nft, ciencia ficción, bioclones, criptomonedas"
    )
    
    styles = getSampleStyleSheet()
    
    # Paleta de colores blockchain
    primary_color = HexColor('#1e40af')      # Azul blockchain
    secondary_color = HexColor('#dc2626')    # Rojo vibrante
    accent_color = HexColor('#f59e0b')      # Dorado
    light_gray = HexColor('#f8fafc')        # Gris claro
    text_gray = HexColor('#374151')         # Gris texto
    
    # Estilos de blockchain
    title_style = ParagraphStyle(
        'BlockchainTitle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=50,
        spaceBefore=30,
        alignment=TA_CENTER,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        leading=34,
        borderWidth=3,
        borderColor=accent_color,
        borderPadding=20,
        backColor=light_gray
    )
    
    subtitle_style = ParagraphStyle(
        'BlockchainSubtitle',
        parent=styles['Heading2'],
        fontSize=20,
        spaceAfter=40,
        spaceBefore=25,
        alignment=TA_CENTER,
        textColor=secondary_color,
        fontName='Helvetica-Bold',
        leading=26
    )
    
    section_style = ParagraphStyle(
        'BlockchainSection',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=30,
        spaceBefore=35,
        alignment=TA_LEFT,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        leading=24,
        borderWidth=2,
        borderColor=accent_color,
        borderPadding=15,
        backColor=light_gray,
        leftIndent=15
    )
    
    body_style = ParagraphStyle(
        'BlockchainBody',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=15,
        spaceBefore=8,
        alignment=TA_JUSTIFY,
        leftIndent=0,
        rightIndent=0,
        fontName='Times-Roman',
        leading=17,
        textColor=text_gray
    )
    
    blockchain_style = ParagraphStyle(
        'BlockchainStyle',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=20,
        spaceBefore=15,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        textColor=secondary_color,
        leftIndent=20,
        leading=20
    )
    
    # Contenido del documento
    story = []
    
    # Portada de blockchain
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph("⛓️ SISTEMA DE BLOCKCHAIN", title_style))
    story.append(Paragraph("Bioclones - Web3 y NFT Completo", subtitle_style))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 1*inch))
    
    # Información del documento
    info_text = """
    <para align="center" fontSize="14" fontName="Helvetica" textColor="#374151">
    <b>Sistema de Blockchain Automático</b><br/>
    <br/>
    <i>Bioclones en la Web3 y blockchain</i><br/>
    """ + datetime.now().strftime("%B %Y") + """<br/>
    <br/>
    <b>Una novela de ciencia ficción en blockchain</b><br/>
    <br/>
    <font size="12" color="#6b7280">
    Tecnología: Blockchain | Web3: Completa | NFT: Avanzado
    </font>
    </para>
    """
    story.append(Paragraph(info_text, body_style))
    story.append(PageBreak())
    
    # Arquitectura blockchain
    story.append(Paragraph("ARQUITECTURA BLOCKCHAIN", section_style))
    
    arquitectura_text = """
    El sistema de blockchain para Bioclones debe ser descentralizado, seguro y escalable, permitiendo la propiedad digital, la monetización y la gobernanza comunitaria.
    """
    story.append(Paragraph(arquitectura_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Componentes del Sistema", subtitle_style))
    componentes = [
        "Blockchain principal para transacciones",
        "Smart contracts para automatización",
        "Sistema de tokens nativos",
        "Marketplace de NFT",
        "Gobernanza descentralizada",
        "Sistema de reputación"
    ]
    
    for componente in componentes:
        story.append(Paragraph(f"• {componente}", blockchain_style))
    
    story.append(PageBreak())
    
    # Tokens y criptomonedas
    story.append(Paragraph("TOKENS Y CRIPTOMONEDAS", section_style))
    
    tokens_text = """
    El ecosistema de tokens de Bioclones debe incluir múltiples tipos de tokens para diferentes funciones y casos de uso.
    """
    story.append(Paragraph(tokens_text, body_style))
    story.append(Spacer(1, 20))
    
    # Tabla de tokens
    tokens_data = [
        ['Token', 'Función', 'Suministro', 'Utilidad'],
        ['BIO', 'Token principal', '1,000,000,000', 'Transacciones y gobernanza'],
        ['BIO-ART', 'Arte y creatividad', '100,000,000', 'NFTs y contenido'],
        ['BIO-READ', 'Lectura y acceso', '500,000,000', 'Acceso a contenido'],
        ['BIO-VOTE', 'Gobernanza', '50,000,000', 'Votación y decisiones'],
        ['BIO-REWARD', 'Recompensas', '200,000,000', 'Incentivos y participación'],
        ['BIO-STAKING', 'Staking', '150,000,000', 'Validación y seguridad']
    ]
    
    tokens_table = Table(tokens_data, colWidths=[2*cm, 3*cm, 2.5*cm, 3.5*cm])
    tokens_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR', (0, 0), (-1, -1), text_gray),
        ('LINEBELOW', (0, 0), (-1, 0), 2, accent_color),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [light_gray, HexColor('#ffffff')]),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
    ]))
    
    story.append(tokens_table)
    story.append(PageBreak())
    
    # NFTs y propiedad digital
    story.append(Paragraph("NFTs Y PROPIEDAD DIGITAL", section_style))
    
    nfts_text = """
    Los NFTs de Bioclones deben representar propiedad digital única, incluyendo personajes, objetos, tierras virtuales y contenido exclusivo.
    """
    story.append(Paragraph(nfts_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Tipos de NFTs", subtitle_style))
    tipos_nfts = [
        "Personajes únicos de Bioclones",
        "Objetos y artefactos de la historia",
        "Tierras virtuales en el metaverso",
        "Contenido exclusivo y ediciones limitadas",
        "Arte generativo basado en la historia",
        "Experiencias y eventos únicos"
    ]
    
    for tipo in tipos_nfts:
        story.append(Paragraph(f"• {tipo}", blockchain_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Características de los NFTs", subtitle_style))
    caracteristicas = [
        "Propiedad digital verificable",
        "Metadatos enriquecidos",
        "Interoperabilidad entre plataformas",
        "Programabilidad con smart contracts",
        "Escasez y rareza verificable",
        "Transferibilidad y comerciabilidad"
    ]
    
    for caracteristica in caracteristicas:
        story.append(Paragraph(f"• {caracteristica}", blockchain_style))
    
    story.append(PageBreak())
    
    # Smart contracts
    story.append(Paragraph("SMART CONTRACTS", section_style))
    
    smart_contracts_text = """
    Los smart contracts de Bioclones deben automatizar procesos, facilitar transacciones y habilitar funcionalidades avanzadas del ecosistema.
    """
    story.append(Paragraph(smart_contracts_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Funcionalidades de Smart Contracts", subtitle_style))
    funcionalidades = [
        "Minting automático de NFTs",
        "Distribución de recompensas",
        "Gobernanza descentralizada",
        "Staking y yield farming",
        "Marketplace automatizado",
        "Sistema de reputación"
    ]
    
    for funcionalidad in funcionalidades:
        story.append(Paragraph(f"• {funcionalidad}", blockchain_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Casos de Uso Específicos", subtitle_style))
    casos_uso = [
        "Venta automática de contenido digital",
        "Distribución de royalties a creadores",
        "Sistema de votación para decisiones",
        "Recompensas por participación",
        "Gestión de derechos de autor",
        "Sistema de licencias y permisos"
    ]
    
    for caso in casos_uso:
        story.append(Paragraph(f"• {caso}", blockchain_style))
    
    story.append(PageBreak())
    
    # Gobernanza descentralizada
    story.append(Paragraph("GOBERNANZA DESCENTRALIZADA", section_style))
    
    gobernanza_text = """
    La gobernanza descentralizada de Bioclones debe permitir que la comunidad tome decisiones sobre el desarrollo, las características y la dirección del proyecto.
    """
    story.append(Paragraph(gobernanza_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Mecanismos de Gobernanza", subtitle_style))
    mecanismos = [
        "Votación por tokens de gobernanza",
        "Propuestas comunitarias",
        "Sistema de delegación de votos",
        "Períodos de votación estructurados",
        "Transparencia en las decisiones",
        "Implementación automática de cambios"
    ]
    
    for mecanismo in mecanismos:
        story.append(Paragraph(f"• {mecanismo}", blockchain_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Áreas de Decisión", subtitle_style))
    areas = [
        "Desarrollo de nuevas características",
        "Distribución de fondos del tesoro",
        "Cambios en la economía de tokens",
        "Asociaciones y colaboraciones",
        "Políticas de contenido y moderación",
        "Estrategias de marketing y crecimiento"
    ]
    
    for area in areas:
        story.append(Paragraph(f"• {area}", blockchain_style))
    
    story.append(PageBreak())
    
    # DeFi y yield farming
    story.append(Paragraph("DeFi Y YIELD FARMING", section_style))
    
    defi_text = """
    El ecosistema DeFi de Bioclones debe incluir yield farming, staking y otras funcionalidades financieras descentralizadas.
    """
    story.append(Paragraph(defi_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Funcionalidades DeFi", subtitle_style))
    funcionalidades_defi = [
        "Staking de tokens BIO",
        "Yield farming con recompensas",
        "Lending y borrowing de activos",
        "Liquidity pools para trading",
        "Sistema de seguros descentralizado",
        "Predicción markets para eventos"
    ]
    
    for funcionalidad in funcionalidades_defi:
        story.append(Paragraph(f"• {funcionalidad}", blockchain_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Incentivos y Recompensas", subtitle_style))
    incentivos = [
        "Recompensas por staking a largo plazo",
        "Yield farming con tokens BIO",
        "Recompensas por participación activa",
        "Bonificaciones por holding de NFTs",
        "Incentivos por contribución al desarrollo",
        "Programas de referidos y afiliados"
    ]
    
    for incentivo in incentivos:
        story.append(Paragraph(f"• {incentivo}", blockchain_style))
    
    story.append(Spacer(1, 30))
    
    # Información de cierre
    cierre_text = """
    <para align="center" fontSize="12" fontName="Helvetica" textColor="#6b7280">
    — Sistema de blockchain generado automáticamente —<br/>
    <br/>
    <b>Web3 y blockchain completo</b><br/>
    <i>Bioclones en la blockchain</i><br/>
    <br/>
    <font size="10" color="#9ca3af">
    Fecha: """ + datetime.now().strftime("%B %Y") + """<br/>
    Sistema: Blockchain Digital Automática
    </font>
    </para>
    """
    story.append(Paragraph(cierre_text, body_style))
    
    # Función para numerar páginas
    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 10)
        page_num = canvas.getPageNumber()
        text = f"Página {page_num}"
        canvas.drawRightString(200*cm, 20*cm, text)
        canvas.restoreState()
    
    # Construir el PDF
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print("Sistema de blockchain creado exitosamente: sistema_blockchain_bioclones.pdf")

if __name__ == "__main__":
    create_blockchain_system()