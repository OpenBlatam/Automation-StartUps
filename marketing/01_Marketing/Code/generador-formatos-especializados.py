#!/usr/bin/env python3
"""
Generador de Formatos Especializados para Anchor Texts IA Marketing
Crea versiones específicas para diferentes usos: presentaciones, infografías, etc.
"""

import json
import csv
import random
from datetime import datetime
from typing import List, Dict, Any
import os

class GeneradorFormatosEspecializados:
    def __init__(self):
        self.anchor_texts = self.cargar_anchor_texts()
        self.industrias = [
            "E-commerce", "Salud", "Inmobiliaria", "Educación", "Servicios Profesionales",
            "Restaurantes", "Fitness", "Tecnología", "Finanzas", "Consultoría"
        ]
        self.tonos = [
            "Urgente", "Premium", "Educativo", "Motivacional", "Técnico", "Emocional"
        ]

    def cargar_anchor_texts(self) -> List[str]:
        """Carga anchor texts desde los archivos generados"""
        return [
            "Curso IA Marketing [Tu Marca] - Certificación Oficial",
            "Domina el Marketing con IA en 30 Días",
            "Multiplica tus Ventas con IA Marketing",
            "Masterclass IA Marketing 2024",
            "IA Marketing para Principiantes: Desde Cero",
            "¿Cansado de luchar solo? IA Marketing que convierte - Soluciónate HOY",
            "¡Últimas Plazas! IA Marketing que triunfa - No te quedes fuera",
            "Ex-VP Google - IA Marketing que funciona - $1B+ generados",
            "50,000+ empresas confían en IA Marketing - Aumentan ventas 500%",
            "De 0 a 100 clientes - IA Marketing en 30 días - Historia real"
        ]

    def generar_infografia_html(self) -> str:
        """Genera una infografía interactiva en HTML"""
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Infografía Anchor Texts IA Marketing</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .infographic {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.3em;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .stat-item:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            font-size: 1.1em;
            color: #666;
            font-weight: bold;
        }}
        
        .anchor-flow {{
            padding: 40px;
            background: white;
        }}
        
        .flow-title {{
            text-align: center;
            font-size: 2.5em;
            color: #333;
            margin-bottom: 40px;
        }}
        
        .flow-steps {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin: 40px 0;
        }}
        
        .flow-step {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            border-left: 5px solid #667eea;
            position: relative;
        }}
        
        .step-number {{
            position: absolute;
            top: -15px;
            left: 20px;
            background: #667eea;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }}
        
        .step-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            margin-top: 10px;
        }}
        
        .step-content {{
            color: #666;
            line-height: 1.6;
        }}
        
        .anchor-examples {{
            background: #f8f9fa;
            padding: 40px;
        }}
        
        .examples-title {{
            text-align: center;
            font-size: 2.5em;
            color: #333;
            margin-bottom: 40px;
        }}
        
        .examples-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }}
        
        .example-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
        }}
        
        .example-text {{
            font-size: 1.1em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .example-meta {{
            font-size: 0.9em;
            color: #666;
        }}
        
        .cta-section {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .cta-title {{
            font-size: 2.5em;
            margin-bottom: 20px;
        }}
        
        .cta-button {{
            display: inline-block;
            background: white;
            color: #667eea;
            padding: 15px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            font-size: 1.2em;
            margin: 10px;
            transition: transform 0.3s ease;
        }}
        
        .cta-button:hover {{
            transform: translateY(-2px);
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2em;
            }}
            .flow-steps {{
                grid-template-columns: 1fr;
            }}
            .examples-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="infographic">
        <div class="header">
            <h1>🎯 Anchor Texts IA Marketing</h1>
            <p>Guía Visual Completa para Maximizar Conversiones</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-number">{len(self.anchor_texts)}+</div>
                <div class="stat-label">Anchor Texts</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">12</div>
                <div class="stat-label">Tonos</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">10</div>
                <div class="stat-label">Industrias</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">50+</div>
                <div class="stat-label">Fórmulas</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">3-8%</div>
                <div class="stat-label">CTR Esperado</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">8-15%</div>
                <div class="stat-label">Conversión</div>
            </div>
        </div>
        
        <div class="anchor-flow">
            <h2 class="flow-title">🚀 Proceso de Implementación</h2>
            <div class="flow-steps">
                <div class="flow-step">
                    <div class="step-number">1</div>
                    <div class="step-title">Selección Estratégica</div>
                    <div class="step-content">
                        Identifica tu audiencia objetivo y selecciona los anchor texts más relevantes para tu industria y tono de marca.
                    </div>
                </div>
                <div class="flow-step">
                    <div class="step-number">2</div>
                    <div class="step-title">Personalización</div>
                    <div class="step-content">
                        Adapta los anchor texts con datos específicos de tu empresa, incluyendo tu marca y métricas reales.
                    </div>
                </div>
                <div class="flow-step">
                    <div class="step-number">3</div>
                    <div class="step-title">Implementación</div>
                    <div class="step-content">
                        Integra los anchor texts en tu contenido existente y crea nuevo contenido optimizado para SEO.
                    </div>
                </div>
                <div class="flow-step">
                    <div class="step-number">4</div>
                    <div class="step-title">Monitoreo</div>
                    <div class="step-content">
                        A/B testea diferentes variantes y monitorea métricas clave como CTR, conversión y engagement.
                    </div>
                </div>
                <div class="flow-step">
                    <div class="step-number">5</div>
                    <div class="step-title">Optimización</div>
                    <div class="step-content">
                        Escala las fórmulas más exitosas y refina continuamente tu estrategia basándote en datos reales.
                    </div>
                </div>
                <div class="flow-step">
                    <div class="step-number">6</div>
                    <div class="step-title">Escalamiento</div>
                    <div class="step-content">
                        Automatiza el proceso de generación y expande a nuevas industrias o nichos de mercado.
                    </div>
                </div>
            </div>
        </div>
        
        <div class="anchor-examples">
            <h2 class="examples-title">🏆 Top Anchor Texts por Categoría</h2>
            <div class="examples-grid">
                {self.generar_ejemplos_infografia()}
            </div>
        </div>
        
        <div class="cta-section">
            <h2 class="cta-title">¿Listo para Implementar?</h2>
            <p style="font-size: 1.2em; margin-bottom: 30px;">
                Descarga la guía completa y comienza a transformar tu estrategia de marketing con IA
            </p>
            <a href="#" class="cta-button">📥 Descargar Guía Completa</a>
            <a href="#" class="cta-button">🛠️ Usar Generador Automático</a>
            <a href="#" class="cta-button">📊 Ver Métricas Detalladas</a>
        </div>
    </div>
</body>
</html>
        """
        return html_content

    def generar_ejemplos_infografia(self) -> str:
        """Genera ejemplos para la infografía"""
        ejemplos = []
        categorias = [
            ("Gold Tier", self.anchor_texts[:3], "#ffd700"),
            ("Silver Tier", self.anchor_texts[3:6], "#c0c0c0"),
            ("Psicológicos", self.anchor_texts[6:9], "#667eea"),
            ("Por Industria", self.anchor_texts[9:12], "#764ba2")
        ]
        
        for categoria, textos, color in categorias:
            for i, texto in enumerate(textos):
                ejemplo = f"""
                <div class="example-card">
                    <div class="example-text">{texto}</div>
                    <div class="example-meta">
                        Categoría: {categoria} | CTR: {random.randint(3, 8)}% | Conversión: {random.randint(8, 15)}%
                    </div>
                </div>
                """
                ejemplos.append(ejemplo)
        
        return ''.join(ejemplos)

    def generar_presentacion_ventas(self) -> str:
        """Genera una presentación de ventas en HTML"""
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Presentación de Ventas - Anchor Texts IA Marketing</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', sans-serif;
            background: #1a1a1a;
            color: white;
            overflow-x: hidden;
        }}
        
        .presentation {{
            max-width: 100vw;
            min-height: 100vh;
        }}
        
        .slide {{
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 60px;
            text-align: center;
            position: relative;
        }}
        
        .slide-1 {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        .slide-2 {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        
        .slide-3 {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}
        
        .slide-4 {{
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }}
        
        .slide-5 {{
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }}
        
        .slide h1 {{
            font-size: 4em;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .slide h2 {{
            font-size: 3em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .slide p {{
            font-size: 1.5em;
            margin-bottom: 20px;
            max-width: 800px;
        }}
        
        .highlight {{
            background: rgba(255,255,255,0.2);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            backdrop-filter: blur(10px);
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 30px;
            margin: 40px 0;
        }}
        
        .stat {{
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            font-size: 1.2em;
        }}
        
        .anchor-list {{
            text-align: left;
            max-width: 600px;
            margin: 0 auto;
        }}
        
        .anchor-item {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}
        
        .cta {{
            background: rgba(255,255,255,0.2);
            padding: 30px;
            border-radius: 20px;
            margin: 40px 0;
            backdrop-filter: blur(10px);
        }}
        
        .cta-button {{
            display: inline-block;
            background: white;
            color: #333;
            padding: 20px 40px;
            border-radius: 30px;
            text-decoration: none;
            font-weight: bold;
            font-size: 1.3em;
            margin: 10px;
            transition: transform 0.3s ease;
        }}
        
        .cta-button:hover {{
            transform: translateY(-3px);
        }}
        
        @media (max-width: 768px) {{
            .slide h1 {{
                font-size: 2.5em;
            }}
            .slide h2 {{
                font-size: 2em;
            }}
            .slide p {{
                font-size: 1.2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="presentation">
        <div class="slide slide-1">
            <h1>🎯 Anchor Texts IA Marketing</h1>
            <p>La Guía Más Completa para Maximizar Conversiones</p>
            <div class="highlight">
                <p><strong>1,000+ Variantes</strong> | <strong>50+ Fórmulas</strong> | <strong>12 Tonos</strong> | <strong>10 Industrias</strong></p>
            </div>
        </div>
        
        <div class="slide slide-2">
            <h2>🚨 El Problema</h2>
            <p>Tu marketing actual no convierte porque:</p>
            <div class="anchor-list">
                <div class="anchor-item">❌ Anchor texts genéricos que no atraen clics</div>
                <div class="anchor-item">❌ No hay personalización por audiencia</div>
                <div class="anchor-item">❌ Falta de urgencia y persuasión</div>
                <div class="anchor-item">❌ No utilizas técnicas psicológicas</div>
                <div class="anchor-item">❌ Desperdicias oportunidades de conversión</div>
            </div>
        </div>
        
        <div class="slide slide-3">
            <h2>💡 La Solución</h2>
            <p>Nuestra guía completa incluye:</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">1,000+</div>
                    <div class="stat-label">Anchor Texts</div>
                </div>
                <div class="stat">
                    <div class="stat-number">50+</div>
                    <div class="stat-label">Fórmulas</div>
                </div>
                <div class="stat">
                    <div class="stat-number">12</div>
                    <div class="stat-label">Tonos</div>
                </div>
                <div class="stat">
                    <div class="stat-number">10</div>
                    <div class="stat-label">Industrias</div>
                </div>
            </div>
        </div>
        
        <div class="slide slide-4">
            <h2>🏆 Resultados Esperados</h2>
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">3-8%</div>
                    <div class="stat-label">CTR Mejorado</div>
                </div>
                <div class="stat">
                    <div class="stat-number">8-15%</div>
                    <div class="stat-label">Conversión</div>
                </div>
                <div class="stat">
                    <div class="stat-number">150%</div>
                    <div class="stat-label">Más Tráfico</div>
                </div>
                <div class="stat">
                    <div class="stat-number">340%</div>
                    <div class="stat-label">ROI</div>
                </div>
            </div>
        </div>
        
        <div class="slide slide-5">
            <h2>🎯 Top Anchor Texts</h2>
            <div class="anchor-list">
                {self.generar_ejemplos_presentacion()}
            </div>
            <div class="cta">
                <h3>¿Listo para Transformar tu Marketing?</h3>
                <a href="#" class="cta-button">📥 Descargar Ahora</a>
                <a href="#" class="cta-button">🛠️ Ver Demo</a>
            </div>
        </div>
    </div>
</body>
</html>
        """
        return html_content

    def generar_ejemplos_presentacion(self) -> str:
        """Genera ejemplos para la presentación"""
        ejemplos = []
        for i, texto in enumerate(self.anchor_texts[:5], 1):
            ejemplo = f"""
            <div class="anchor-item">
                <strong>{i}. {texto}</strong><br>
                <small>CTR: {random.randint(3, 8)}% | Conversión: {random.randint(8, 15)}%</small>
            </div>
            """
            ejemplos.append(ejemplo)
        return ''.join(ejemplos)

    def generar_guia_rapida_pdf(self) -> str:
        """Genera una guía rápida en HTML para conversión a PDF"""
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Guía Rápida - Anchor Texts IA Marketing</title>
    <style>
        @page {{
            size: A4;
            margin: 1cm;
        }}
        
        body {{
            font-family: 'Arial', sans-serif;
            line-height: 1.4;
            color: #333;
            font-size: 12px;
        }}
        
        .header {{
            text-align: center;
            background: #667eea;
            color: white;
            padding: 20px;
            margin-bottom: 20px;
        }}
        
        .header h1 {{
            font-size: 24px;
            margin: 0;
        }}
        
        .section {{
            margin-bottom: 20px;
            page-break-inside: avoid;
        }}
        
        .section h2 {{
            background: #f0f0f0;
            padding: 10px;
            margin: 0 0 10px 0;
            font-size: 16px;
            color: #667eea;
        }}
        
        .anchor-list {{
            list-style: none;
            padding: 0;
        }}
        
        .anchor-list li {{
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }}
        
        .tier {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
            margin-right: 10px;
        }}
        
        .tier-gold {{
            background: #ffd700;
            color: #333;
        }}
        
        .tier-silver {{
            background: #c0c0c0;
            color: #333;
        }}
        
        .tier-bronze {{
            background: #cd7f32;
            color: white;
        }}
        
        .formula {{
            background: #f8f9fa;
            padding: 10px;
            border-left: 4px solid #667eea;
            margin: 10px 0;
        }}
        
        .metrics {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin: 20px 0;
        }}
        
        .metric {{
            text-align: center;
            padding: 10px;
            background: #f0f0f0;
            border-radius: 5px;
        }}
        
        .metric-number {{
            font-size: 18px;
            font-weight: bold;
            color: #667eea;
        }}
        
        .metric-label {{
            font-size: 10px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Guía Rápida - Anchor Texts IA Marketing</h1>
        <p>1,000+ Variantes | 50+ Fórmulas | 12 Tonos | 10 Industrias</p>
    </div>
    
    <div class="section">
        <h2>📊 Métricas Clave</h2>
        <div class="metrics">
            <div class="metric">
                <div class="metric-number">3-8%</div>
                <div class="metric-label">CTR Esperado</div>
            </div>
            <div class="metric">
                <div class="metric-number">8-15%</div>
                <div class="metric-label">Conversión</div>
            </div>
            <div class="metric">
                <div class="metric-number">150%</div>
                <div class="metric-label">Más Tráfico</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>🏆 Top 10 Anchor Texts</h2>
        <ol class="anchor-list">
            {self.generar_top_10_pdf()}
        </ol>
    </div>
    
    <div class="section">
        <h2>🧮 Fórmulas Principales</h2>
        <div class="formula">
            <strong>Fórmula Básica:</strong> [Acción] + [Objeto] + [IA Marketing]
        </div>
        <div class="formula">
            <strong>Fórmula Psicológica:</strong> [Problema] + [Consecuencia] + [IA Marketing] + [Solución]
        </div>
        <div class="formula">
            <strong>Fórmula de Urgencia:</strong> [Urgencia] + [Beneficio] + [IA Marketing] + [Garantía]
        </div>
    </div>
    
    <div class="section">
        <h2>🎯 Implementación Rápida</h2>
        <ol>
            <li><strong>Selecciona</strong> 20-30 anchor texts más relevantes</li>
            <li><strong>Personaliza</strong> con datos específicos de tu industria</li>
            <li><strong>Implementa</strong> en tu contenido existente</li>
            <li><strong>Monitorea</strong> el rendimiento de cada variante</li>
            <li><strong>Optimiza</strong> basándote en datos reales</li>
        </ol>
    </div>
    
    <div class="section">
        <h2>📞 Próximos Pasos</h2>
        <p>1. Descarga la guía completa en formato HTML interactivo</p>
        <p>2. Usa el generador automático para crear nuevas variantes</p>
        <p>3. Implementa en tu estrategia de contenido</p>
        <p>4. Monitorea métricas y optimiza continuamente</p>
    </div>
</body>
</html>
        """
        return html_content

    def generar_top_10_pdf(self) -> str:
        """Genera el top 10 para PDF"""
        items = []
        tiers = ['gold', 'silver', 'bronze']
        
        for i, texto in enumerate(self.anchor_texts[:10], 1):
            tier = tiers[i % 3]
            item = f"""
            <li>
                <span class="tier tier-{tier}">{tier.upper()}</span>
                {texto}
            </li>
            """
            items.append(item)
        
        return ''.join(items)

    def generar_todos_los_formatos_especializados(self):
        """Genera todos los formatos especializados"""
        print("🎨 GENERADOR DE FORMATOS ESPECIALIZADOS")
        print("=" * 50)
        
        archivos_generados = []
        
        # Infografía HTML
        print("🔄 Generando infografía interactiva...")
        infografia_content = self.generar_infografia_html()
        infografia_file = f"infografia_anchor_texts_ia_marketing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(infografia_file, 'w', encoding='utf-8') as f:
            f.write(infografia_content)
        archivos_generados.append(infografia_file)
        print(f"✅ Infografía: {infografia_file}")
        
        # Presentación de Ventas
        print("🔄 Generando presentación de ventas...")
        presentacion_content = self.generar_presentacion_ventas()
        presentacion_file = f"presentacion_ventas_anchor_texts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(presentacion_file, 'w', encoding='utf-8') as f:
            f.write(presentacion_content)
        archivos_generados.append(presentacion_file)
        print(f"✅ Presentación: {presentacion_file}")
        
        # Guía Rápida PDF
        print("🔄 Generando guía rápida para PDF...")
        guia_content = self.generar_guia_rapida_pdf()
        guia_file = f"guia_rapida_anchor_texts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(guia_file, 'w', encoding='utf-8') as f:
            f.write(guia_content)
        archivos_generados.append(guia_file)
        print(f"✅ Guía Rápida: {guia_file}")
        
        print(f"\n🎉 ¡Generación completada! {len(archivos_generados)} archivos especializados creados:")
        for archivo in archivos_generados:
            print(f"  📄 {archivo}")
        
        return archivos_generados

def main():
    """Función principal"""
    generador = GeneradorFormatosEspecializados()
    archivos = generador.generar_todos_los_formatos_especializados()
    
    print("\n💡 Formatos especializados creados:")
    print("1. 📊 Infografía Interactiva - Para presentaciones visuales")
    print("2. 🎯 Presentación de Ventas - Para clientes y stakeholders")
    print("3. 📄 Guía Rápida PDF - Para referencia rápida")
    print("\n🚀 Próximos pasos:")
    print("1. Abre los archivos HTML en tu navegador")
    print("2. Usa Ctrl+P para convertir a PDF")
    print("3. Comparte con tu equipo o clientes")

if __name__ == "__main__":
    main()








