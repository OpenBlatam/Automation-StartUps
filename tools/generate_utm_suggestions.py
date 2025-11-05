#!/usr/bin/env python3
"""
Genera sugerencias de UTMs para nuevos creativos basado en mejores prácticas
"""
import sys
from pathlib import Path

def suggest_utm_content(producto, formato, angulo, cta, is_carousel=False, slide_num=None):
    """
    Genera sugerencia de utm_content basado en convenciones
    """
    parts = []
    
    # Prefix por formato
    if formato == '1080x1080':
        parts.append('sq')  # square
    elif formato == '1080x1920':
        parts.append('vt')  # vertical
    elif is_carousel:
        parts.append('carousel')
        if slide_num:
            parts.append(f'slide{slide_num}')
    
    # Ángulo
    if angulo == 'metrics':
        parts.append('metrics')
    elif angulo == 'socialproof':
        parts.append('socialproof')
    elif angulo == 'urgency':
        parts.append('urgency')
    
    # CTA
    parts.append(f'cta_{cta}')
    
    # Versión
    parts.append('v1')
    
    return '_'.join(parts)

def suggest_utm_campaign(producto, objetivo, canal, fecha=None):
    """Genera sugerencia de utm_campaign"""
    from datetime import datetime
    
    if fecha is None:
        fecha = datetime.now().strftime('%Y-%m')
    
    return f"{producto}_{objetivo}_{canal}_{fecha}"

def generate_suggestions():
    """Genera sugerencias para diferentes escenarios"""
    
    scenarios = [
        {
            'name': 'LinkedIn Ad - Metrics - Desktop',
            'producto': 'iabulk',
            'formato': '1200x627',
            'angulo': 'metrics',
            'cta': 'demo',
            'utm_source': 'linkedin',
            'utm_medium': 'cpc'
        },
        {
            'name': 'LinkedIn Ad - Social Proof - Mobile Square',
            'producto': 'cursoia',
            'formato': '1080x1080',
            'angulo': 'socialproof',
            'cta': 'registro',
            'utm_source': 'linkedin',
            'utm_medium': 'cpc'
        },
        {
            'name': 'LinkedIn Ad - Urgency - Stories',
            'producto': 'saasia',
            'formato': '1080x1920',
            'angulo': 'urgency',
            'cta': 'trial',
            'utm_source': 'linkedin',
            'utm_medium': 'cpc'
        },
        {
            'name': 'Carousel Slide 1 - Hook',
            'producto': 'iabulk',
            'formato': 'carousel',
            'angulo': 'hook',
            'cta': 'demo',
            'is_carousel': True,
            'slide_num': 1,
            'utm_source': 'linkedin',
            'utm_medium': 'cpc'
        },
        {
            'name': 'Webinar Preroll - Social Proof',
            'producto': 'cursoia',
            'formato': 'preroll',
            'angulo': 'socialproof',
            'cta': 'registro',
            'utm_source': 'email',
            'utm_medium': 'email'
        }
    ]
    
    print("=" * 80)
    print("💡 Sugerencias de UTMs por Escenario")
    print("=" * 80)
    print()
    
    for scenario in scenarios:
        print(f"📋 {scenario['name']}")
        print("-" * 80)
        
        # Generar utm_content
        utm_content = suggest_utm_content(
            scenario['producto'],
            scenario.get('formato', '1200x627'),
            scenario.get('angulo', 'base'),
            scenario['cta'],
            scenario.get('is_carousel', False),
            scenario.get('slide_num')
        )
        
        # Generar utm_campaign
        objetivo_map = {
            'demo': 'demo',
            'registro': 'registro',
            'trial': 'trial'
        }
        utm_campaign = suggest_utm_campaign(
            scenario['producto'],
            objetivo_map.get(scenario['cta'], scenario['cta']),
            'linkedin' if scenario['utm_source'] == 'linkedin' else 'email'
        )
        
        print(f"  utm_source:      {scenario['utm_source']}")
        print(f"  utm_medium:      {scenario['utm_medium']}")
        print(f"  utm_campaign:    {utm_campaign}")
        print(f"  utm_content:     {utm_content}")
        print(f"  utm_term:        [rol]_[region] (ej: cmo_mx)")
        print()
        
        # Generar ejemplo de final_url
        from urllib.parse import urlencode
        landing = f"https://tusitio.com/{scenario['cta']}"
        params = {
            'utm_source': scenario['utm_source'],
            'utm_medium': scenario['utm_medium'],
            'utm_campaign': utm_campaign,
            'utm_content': utm_content,
            'utm_term': 'cmo_mx'
        }
        final_url = f"{landing}?{urlencode(params)}"
        print(f"  final_url:       {final_url}")
        print()
    
    print("=" * 80)
    print()
    print("💡 Convenciones:")
    print("   • Formato square (1080×1080): Prefijo 'sq_'")
    print("   • Formato vertical (1080×1920): Prefijo 'vt_'")
    print("   • Carousel: Prefijo 'carousel_' + slide número")
    print("   • Ángulos: metrics, socialproof, urgency, base")
    print("   • CTAs: demo, registro, trial")
    print("   • Versión: v1, v2, v3...")
    print()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Modo interactivo: generar sugerencia personalizada
        producto = sys.argv[1] if len(sys.argv) > 1 else 'iabulk'
        formato = sys.argv[2] if len(sys.argv) > 2 else '1200x627'
        angulo = sys.argv[3] if len(sys.argv) > 3 else 'base'
        cta = sys.argv[4] if len(sys.argv) > 4 else 'demo'
        
        utm_content = suggest_utm_content(producto, formato, angulo, cta)
        utm_campaign = suggest_utm_campaign(producto, cta, 'linkedin')
        
        print(f"Sugerencia para: {producto} - {formato} - {angulo} - {cta}")
        print(f"  utm_content:  {utm_content}")
        print(f"  utm_campaign: {utm_campaign}")
    else:
        generate_suggestions()


