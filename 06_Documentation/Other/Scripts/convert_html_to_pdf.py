#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML to PDF Converter for ChatGPT Queue Marketing Plan
Simple script to convert HTML to PDF using weasyprint or similar
"""

import os
import sys

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import weasyprint
        return True
    except ImportError:
        print("WeasyPrint no está instalado. Instalando...")
        try:
            os.system("pip install weasyprint")
            import weasyprint
            return True
        except:
            print("No se pudo instalar WeasyPrint. Usando alternativa...")
            return False

def convert_with_weasyprint():
    """Convert HTML to PDF using WeasyPrint"""
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        
        # Read HTML file
        with open('ChatGPT_Queue_Marketing_Plan_Enhanced.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Create PDF
        font_config = FontConfiguration()
        html_doc = HTML(string=html_content)
        html_doc.write_pdf('ChatGPT_Queue_Marketing_Plan_Enhanced.pdf', font_config=font_config)
        
        print("✅ PDF creado exitosamente con WeasyPrint: ChatGPT_Queue_Marketing_Plan_Enhanced.pdf")
        return True
        
    except Exception as e:
        print(f"❌ Error con WeasyPrint: {e}")
        return False

def convert_with_alternative():
    """Alternative conversion method"""
    try:
        # Try using pdfkit if available
        import pdfkit
        
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        
        pdfkit.from_file('ChatGPT_Queue_Marketing_Plan_Enhanced.html', 
                        'ChatGPT_Queue_Marketing_Plan_Enhanced.pdf', 
                        options=options)
        
        print("✅ PDF creado exitosamente con pdfkit: ChatGPT_Queue_Marketing_Plan_Enhanced.pdf")
        return True
        
    except ImportError:
        print("pdfkit no está disponible")
        return False
    except Exception as e:
        print(f"❌ Error con pdfkit: {e}")
        return False

def create_simple_pdf():
    """Create a simple PDF using basic HTML to PDF conversion"""
    print("📄 Creando PDF usando método alternativo...")
    
    # Create a simple HTML file optimized for PDF
    simple_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Plan de Marketing ChatGPT Queue</title>
        <style>
            @page { size: A4; margin: 2cm; }
            body { font-family: Arial, sans-serif; line-height: 1.6; }
            h1 { color: #2E86AB; text-align: center; }
            h2 { color: #A23B72; border-bottom: 2px solid #A23B72; }
            h3 { color: #F18F01; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .highlight { background-color: #fff3cd; padding: 10px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>🚀 Plan de Marketing Mejorado para ChatGPT Queue</h1>
        <p style="text-align: center; font-size: 1.2em; color: #666;">
            Extensión de Chrome - Teoría de Difusión de Innovaciones
        </p>
        
        <h2>📋 Resumen Ejecutivo</h2>
        <p>Este plan de marketing está diseñado específicamente para <strong>ChatGPT Queue</strong>, una extensión de Chrome que permite a los usuarios hacer cola de mensajes para ChatGPT, ahorrando tiempo significativo. El plan se basa en la <strong>Teoría de Difusión de Innovaciones de Everett Rogers</strong>, segmentando el mercado en cinco categorías de adoptantes con estrategias específicas para cada grupo.</p>
        
        <div class="highlight">
            <p><strong>Objetivo:</strong> Generar un ROI del 300%+ en 24 meses con una inversión total de $125,000.</p>
        </div>
        
        <h2>1. 🎯 INNOVADORES (2.5% del mercado)</h2>
        <h3>Perfil Demográfico</h3>
        <ul>
            <li><strong>Edad:</strong> 25-40 años</li>
            <li><strong>Ingresos:</strong> $75K+ anuales</li>
            <li><strong>Profesión:</strong> Desarrolladores, emprendedores tech, early adopters de IA</li>
            <li><strong>Comportamiento:</strong> Activos en GitHub, Reddit, Hacker News, Discord tech</li>
        </ul>
        
        <h3>Estrategias Clave</h3>
        <ul>
            <li><strong>Product Hunt Launch:</strong> Top 5 del día, 500+ votos</li>
            <li><strong>Reddit Strategy:</strong> Multi-subreddit con horarios óptimos</li>
            <li><strong>Beta Program:</strong> 50 testers exclusivos</li>
            <li><strong>Pricing:</strong> $29.99 inicial, $19.99 early bird</li>
        </ul>
        
        <h2>2. ⚡ PRIMEROS ADOPTANTES (13.5% del mercado)</h2>
        <h3>Perfil Demográfico</h3>
        <ul>
            <li><strong>Edad:</strong> 30-45 años</li>
            <li><strong>Ingresos:</strong> $60K+ anuales</li>
            <li><strong>Profesión:</strong> Consultores, coaches, content creators, managers</li>
        </ul>
        
        <h3>Estrategias Clave</h3>
        <ul>
            <li><strong>Influencer Program:</strong> Micro y macro influencers</li>
            <li><strong>Content Marketing:</strong> Blog, YouTube, newsletters</li>
            <li><strong>Referral Program:</strong> 30% comisión nivel 1</li>
            <li><strong>Webinar Series:</strong> AI Productivity Masterclass</li>
        </ul>
        
        <h2>3. 📈 MAYORÍA TEMPRANA (34% del mercado)</h2>
        <h3>Perfil Demográfico</h3>
        <ul>
            <li><strong>Edad:</strong> 25-50 años</li>
            <li><strong>Ingresos:</strong> $40K+ anuales</li>
            <li><strong>Profesión:</strong> Profesionales, small business owners, freelancers</li>
        </ul>
        
        <h3>Estrategias Clave</h3>
        <ul>
            <li><strong>SEO Strategy:</strong> Keywords objetivo, content pillar</li>
            <li><strong>Freemium Model:</strong> Free tier + Pro tier</li>
            <li><strong>Paid Advertising:</strong> Google, Facebook, LinkedIn ads</li>
            <li><strong>Affiliate Program:</strong> 40% comisión bloggers</li>
        </ul>
        
        <h2>4. 🏢 MAYORÍA TARDÍA (34% del mercado)</h2>
        <h3>Perfil Demográfico</h3>
        <ul>
            <li><strong>Edad:</strong> 35-60 años</li>
            <li><strong>Ingresos:</strong> $30K+ anuales</li>
            <li><strong>Profesión:</strong> Empleados corporativos, managers, small business owners</li>
        </ul>
        
        <h3>Estrategias Clave</h3>
        <ul>
            <li><strong>Social Proof:</strong> Testimonials masivos, case studies</li>
            <li><strong>Traditional Marketing:</strong> Podcasts, newsletters, trade shows</li>
            <li><strong>Competitive Pricing:</strong> $4.99-$49.99/mes</li>
            <li><strong>Guarantees:</strong> 30-day money-back, free trials</li>
        </ul>
        
        <h2>5. 🔄 REZAGADOS (16% del mercado)</h2>
        <h3>Perfil Demográfico</h3>
        <ul>
            <li><strong>Edad:</strong> 45+ años</li>
            <li><strong>Ingresos:</strong> $25K+ anuales</li>
            <li><strong>Profesión:</strong> Empleados tradicionales, administradores</li>
        </ul>
        
        <h3>Estrategias Clave</h3>
        <ul>
            <li><strong>Education:</strong> Onboarding extendido, contenido simplificado</li>
            <li><strong>Minimal Pricing:</strong> $2.99/mes, $19.99 lifetime</li>
            <li><strong>Personal Support:</strong> Setup calls, training sessions</li>
            <li><strong>Social Pressure:</strong> "Todos lo están usando"</li>
        </ul>
        
        <h2>📊 MÉTRICAS DE ÉXITO</h2>
        <table>
            <tr>
                <th>Segmento</th>
                <th>Métrica Clave</th>
                <th>Objetivo</th>
            </tr>
            <tr>
                <td>Innovadores</td>
                <td>Product Hunt ranking</td>
                <td>Top 5 del día</td>
            </tr>
            <tr>
                <td>Primeros Adoptantes</td>
                <td>Influencer partnerships</td>
                <td>25+ colaboraciones</td>
            </tr>
            <tr>
                <td>Mayoría Temprana</td>
                <td>Organic traffic</td>
                <td>50%+ del tráfico total</td>
            </tr>
            <tr>
                <td>Mayoría Tardía</td>
                <td>Brand recognition</td>
                <td>60%+ awareness</td>
            </tr>
            <tr>
                <td>Rezagados</td>
                <td>Adoption rate</td>
                <td>20%+ después de 12 meses</td>
            </tr>
        </table>
        
        <h2>🗓️ CRONOGRAMA DE IMPLEMENTACIÓN</h2>
        <table>
            <tr>
                <th>Fase</th>
                <th>Duración</th>
                <th>Enfoque</th>
                <th>Actividades Clave</th>
            </tr>
            <tr>
                <td>Fase 1: Lanzamiento</td>
                <td>Meses 1-3</td>
                <td>Innovadores + Primeros Adoptantes</td>
                <td>Product Hunt, Reddit, Influencers</td>
            </tr>
            <tr>
                <td>Fase 2: Crecimiento</td>
                <td>Meses 4-9</td>
                <td>Mayoría Temprana</td>
                <td>SEO, Freemium, Paid Ads</td>
            </tr>
            <tr>
                <td>Fase 3: Escala</td>
                <td>Meses 10-18</td>
                <td>Mayoría Tardía</td>
                <td>Mass Marketing, Partnerships</td>
            </tr>
            <tr>
                <td>Fase 4: Madurez</td>
                <td>Meses 19-24</td>
                <td>Rezagados + Retención</td>
                <td>Education, Support Scaling</td>
            </tr>
        </table>
        
        <h2>💰 PRESUPUESTO TOTAL</h2>
        <table>
            <tr>
                <th>Fase</th>
                <th>Presupuesto</th>
                <th>ROI Esperado</th>
            </tr>
            <tr>
                <td>Fase 1: Lanzamiento</td>
                <td>$15,000</td>
                <td>300%</td>
            </tr>
            <tr>
                <td>Fase 2: Crecimiento</td>
                <td>$35,000</td>
                <td>250%</td>
            </tr>
            <tr>
                <td>Fase 3: Escala</td>
                <td>$50,000</td>
                <td>200%</td>
            </tr>
            <tr>
                <td>Fase 4: Madurez</td>
                <td>$25,000</td>
                <td>150%</td>
            </tr>
            <tr style="font-weight: bold; background-color: #f2f2f2;">
                <td>TOTAL</td>
                <td>$125,000</td>
                <td>300%+</td>
            </tr>
        </table>
        
        <div class="highlight">
            <h2>🚀 PRÓXIMOS PASOS INMEDIATOS</h2>
            <h3>Semana 1-2: Preparación</h3>
            <ul>
                <li>✅ Crear assets para Product Hunt</li>
                <li>✅ Identificar y contactar hunters</li>
                <li>✅ Preparar contenido para Reddit</li>
                <li>✅ Configurar analytics y tracking</li>
                <li>✅ Crear landing page de pre-lanzamiento</li>
            </ul>
            
            <h3>Semana 3-4: Lanzamiento</h3>
            <ul>
                <li>✅ Ejecutar lanzamiento en Product Hunt</li>
                <li>✅ Publicar en subreddits objetivo</li>
                <li>✅ Activar campañas de pago</li>
                <li>✅ Contactar medios tech</li>
                <li>✅ Monitorear y optimizar</li>
            </ul>
        </div>
        
        <p style="text-align: center; margin-top: 50px; color: #666;">
            <em>© 2024 - ChatGPT Queue Marketing Plan. Plan de marketing mejorado basado en la Teoría de Difusión de Innovaciones.</em>
        </p>
    </body>
    </html>
    """
    
    # Write simple HTML file
    with open('ChatGPT_Queue_Marketing_Plan_Simple.html', 'w', encoding='utf-8') as f:
        f.write(simple_html)
    
    print("✅ Archivo HTML simple creado: ChatGPT_Queue_Marketing_Plan_Simple.html")
    print("📄 Para convertir a PDF, abre el archivo en tu navegador y usa Ctrl+P > Guardar como PDF")
    return True

def main():
    """Main function to convert HTML to PDF"""
    print("🚀 Iniciando conversión de HTML a PDF...")
    
    # Check if HTML file exists
    if not os.path.exists('ChatGPT_Queue_Marketing_Plan_Enhanced.html'):
        print("❌ No se encontró el archivo HTML. Creando versión simple...")
        return create_simple_pdf()
    
    # Try different conversion methods
    if check_dependencies():
        if convert_with_weasyprint():
            return True
    
    if convert_with_alternative():
        return True
    
    # Fallback to simple HTML
    print("📄 Creando versión HTML simple para conversión manual...")
    return create_simple_pdf()

if __name__ == "__main__":
    main()
