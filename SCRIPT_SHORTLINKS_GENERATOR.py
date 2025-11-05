#!/usr/bin/env python3
"""
Generador de Shortlinks desde CSV con UTM
Lee OUTREACH_MESSAGES_READY.csv y genera shortlinks automáticamente
"""

import csv
import sys
from typing import Dict, Optional

# Configuración (ajusta según tu acortador)
SHORT_DOMAIN = "go.tumarca"  # Cambiar por tu dominio
BITLY_API_KEY = None  # Opcional: si tienes Bitly API
REBRANDLY_API_KEY = None  # Opcional: si tienes Rebrandly API

def generar_slug(row: Dict[str, str]) -> str:
    """Genera slug legible desde UTM parameters"""
    campaign = row.get('utm_campaign', 'outreach')
    content = row.get('utm_content', 'general')
    term = row.get('utm_term', 'general')
    
    # Limpia y une
    slug_parts = [campaign, content, term]
    slug = '-'.join([p.replace(' ', '-').lower() for p in slug_parts if p])
    
    # Limita longitud (algunos acortadores tienen límite)
    if len(slug) > 100:
        slug = slug[:100]
    
    return slug

def generar_shortlink(row: Dict[str, str], usar_api: bool = False) -> str:
    """
    Genera shortlink
    Si usar_api=True y tienes credenciales, usa API real
    Si no, genera placeholder para copiar manualmente
    """
    utm_url = row.get('utm_url', '')
    if not utm_url:
        return ""
    
    slug = generar_slug(row)
    shortlink = f"https://{SHORT_DOMAIN}/{slug}"
    
    # Si tienes API configurada, aquí iría el llamado a la API
    # Ejemplo para Bitly:
    # if usar_api and BITLY_API_KEY:
    #     import requests
    #     response = requests.post(
    #         "https://api-ssl.bitly.com/v4/shorten",
    #         headers={"Authorization": f"Bearer {BITLY_API_KEY}"},
    #         json={"long_url": utm_url, "domain": SHORT_DOMAIN}
    #     )
    #     if response.status_code == 200:
    #         return response.json()["link"]
    
    return shortlink

def procesar_csv(archivo_csv: str, usar_api: bool = False, actualizar_csv: bool = False):
    """Lee CSV y genera shortlinks"""
    resultados = []
    
    try:
        with open(archivo_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Genera shortlinks
        for row in rows:
            shortlink = generar_shortlink(row, usar_api)
            resultados.append({
                'lead': row.get('lead_full_name', 'N/A'),
                'utm_url': row.get('utm_url', ''),
                'shortlink': shortlink,
                'slug': shortlink.replace(f"https://{SHORT_DOMAIN}/", "") if shortlink else ""
            })
            
            if actualizar_csv:
                row['short_url'] = shortlink
        
        # Muestra resultados
        print("\n" + "="*80)
        print("SHORTLINKS GENERADOS")
        print("="*80 + "\n")
        
        for r in resultados:
            print(f"Lead: {r['lead']}")
            print(f"  URL completa: {r['utm_url'][:60]}..." if len(r['utm_url']) > 60 else f"  URL completa: {r['utm_url']}")
            print(f"  Shortlink: {r['shortlink']}")
            print(f"  Slug: {r['slug']}")
            print("-" * 80)
        
        # Si se actualiza CSV, guarda
        if actualizar_csv:
            output_file = archivo_csv.replace('.csv', '_with_shortlinks.csv')
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                fieldnames = rows[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            print(f"\n✅ CSV actualizado guardado en: {output_file}")
        
        return resultados
    
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {archivo_csv}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python SCRIPT_SHORTLINKS_GENERATOR.py <archivo.csv> [--update] [--api]")
        print("\nEjemplo: python SCRIPT_SHORTLINKS_GENERATOR.py OUTREACH_MESSAGES_READY.csv --update")
        print("\nOpciones:")
        print("  --update  : Actualiza CSV con shortlinks generados")
        print("  --api     : Usa API real (requiere credenciales configuradas)")
        sys.exit(1)
    
    archivo_csv = sys.argv[1]
    actualizar = '--update' in sys.argv
    usar_api = '--api' in sys.argv
    
    procesar_csv(archivo_csv, usar_api, actualizar)




