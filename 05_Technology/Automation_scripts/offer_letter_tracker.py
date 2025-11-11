#!/usr/bin/env python3
"""
Sistema de Tracking para Cartas de Oferta
Registra y rastrea ofertas generadas
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


TRACKER_FILE = "offer_letter_tracker.json"


def load_tracker() -> Dict:
    """Carga el archivo de tracking."""
    if os.path.exists(TRACKER_FILE):
        try:
            with open(TRACKER_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {'offers': [], 'stats': {}}
    return {'offers': [], 'stats': {}}


def save_tracker(data: Dict):
    """Guarda el archivo de tracking."""
    with open(TRACKER_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def track_offer(
    position_title: str,
    candidate_name: str,
    salary_amount: str,
    output_file: str,
    offer_type: str = "text",
    template_used: Optional[str] = None,
    **kwargs
) -> Dict:
    """Registra una nueva oferta en el tracker."""
    tracker = load_tracker()
    
    offer_record = {
        'id': len(tracker['offers']) + 1,
        'timestamp': datetime.now().isoformat(),
        'position_title': position_title,
        'candidate_name': candidate_name,
        'salary_amount': salary_amount,
        'output_file': output_file,
        'offer_type': offer_type,  # text, html, pdf
        'template_used': template_used,
        'metadata': kwargs
    }
    
    tracker['offers'].append(offer_record)
    
    # Actualizar estadísticas
    update_stats(tracker)
    
    save_tracker(tracker)
    return offer_record


def update_stats(tracker: Dict):
    """Actualiza las estadísticas del tracker."""
    offers = tracker.get('offers', [])
    
    stats = {
        'total_offers': len(offers),
        'by_type': {},
        'by_template': {},
        'total_salary': 0,
        'salary_count': 0,
        'recent_offers': len([o for o in offers if is_recent(o['timestamp'])])
    }
    
    for offer in offers:
        # Por tipo
        offer_type = offer.get('offer_type', 'text')
        stats['by_type'][offer_type] = stats['by_type'].get(offer_type, 0) + 1
        
        # Por plantilla
        template = offer.get('template_used')
        if template:
            stats['by_template'][template] = stats['by_template'].get(template, 0) + 1
        
        # Salarios
        try:
            salary = float(offer.get('salary_amount', '0').replace('$', '').replace(',', ''))
            if salary > 0:
                stats['total_salary'] += salary
                stats['salary_count'] += 1
        except:
            pass
    
    if stats['salary_count'] > 0:
        stats['avg_salary'] = stats['total_salary'] / stats['salary_count']
    else:
        stats['avg_salary'] = 0
    
    tracker['stats'] = stats


def is_recent(timestamp: str, days: int = 7) -> bool:
    """Verifica si una oferta es reciente."""
    try:
        offer_date = datetime.fromisoformat(timestamp)
        days_diff = (datetime.now() - offer_date).days
        return days_diff <= days
    except:
        return False


def get_offers(filters: Optional[Dict] = None) -> List[Dict]:
    """Obtiene ofertas con filtros opcionales."""
    tracker = load_tracker()
    offers = tracker.get('offers', [])
    
    if not filters:
        return offers
    
    filtered = []
    for offer in offers:
        match = True
        for key, value in filters.items():
            if offer.get(key) != value:
                match = False
                break
        if match:
            filtered.append(offer)
    
    return filtered


def get_stats() -> Dict:
    """Obtiene estadísticas del tracker."""
    tracker = load_tracker()
    return tracker.get('stats', {})


def generate_tracker_report(output_file: str = "tracker_report.txt"):
    """Genera un reporte del tracker."""
    tracker = load_tracker()
    stats = tracker.get('stats', {})
    offers = tracker.get('offers', [])
    
    report = f"""
{'='*70}
  REPORTE DE TRACKING - CARTAS DE OFERTA
{'='*70}

Fecha del reporte: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ESTADÍSTICAS GENERALES
{'-'*70}
Total de ofertas generadas: {stats.get('total_offers', 0)}
Ofertas recientes (últimos 7 días): {stats.get('recent_offers', 0)}

POR TIPO DE ARCHIVO
{'-'*70}
"""
    
    for offer_type, count in stats.get('by_type', {}).items():
        report += f"  {offer_type}: {count}\n"
    
    report += f"""
POR PLANTILLA
{'-'*70}
"""
    
    for template, count in stats.get('by_template', {}).items():
        report += f"  {template}: {count}\n"
    
    if not stats.get('by_template'):
        report += "  (ninguna plantilla usada)\n"
    
    report += f"""
ESTADÍSTICAS DE SALARIOS
{'-'*70}
"""
    
    if stats.get('salary_count', 0) > 0:
        report += f"""Salario promedio: ${stats.get('avg_salary', 0):,.2f}
Total de ofertas con salario: {stats.get('salary_count', 0)}
"""
    else:
        report += "No hay datos de salario disponibles.\n"
    
    report += f"""
ÚLTIMAS 10 OFERTAS
{'-'*70}
"""
    
    recent_offers = sorted(offers, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]
    for offer in recent_offers:
        timestamp = offer.get('timestamp', '')[:10]  # Solo fecha
        report += f"""
  [{offer.get('id', 'N/A')}] {timestamp} - {offer.get('position_title', 'N/A')}
     Candidato: {offer.get('candidate_name', 'N/A')}
     Salario: {offer.get('salary_amount', 'N/A')}
     Archivo: {offer.get('output_file', 'N/A')}
     Tipo: {offer.get('offer_type', 'N/A')}
"""
    
    report += f"""
{'='*70}
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✓ Reporte de tracking generado: {output_file}")
    return report


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de tracking de cartas de oferta')
    parser.add_argument('--stats', action='store_true',
                       help='Mostrar estadísticas')
    parser.add_argument('--report', dest='report_file',
                       help='Generar reporte (especificar archivo de salida)')
    parser.add_argument('--list', action='store_true',
                       help='Listar todas las ofertas')
    parser.add_argument('--filter', dest='filter_key',
                       help='Filtrar por campo (requiere --value)')
    parser.add_argument('--value', dest='filter_value',
                       help='Valor para filtrar')
    parser.add_argument('--recent', type=int, default=7,
                       help='Mostrar ofertas recientes (días, default: 7)')
    
    args = parser.parse_args()
    
    if args.stats:
        stats = get_stats()
        print("\n📊 Estadísticas de Tracking:\n")
        print(f"Total de ofertas: {stats.get('total_offers', 0)}")
        print(f"Ofertas recientes: {stats.get('recent_offers', 0)}")
        print(f"\nPor tipo:")
        for offer_type, count in stats.get('by_type', {}).items():
            print(f"  {offer_type}: {count}")
        if stats.get('avg_salary', 0) > 0:
            print(f"\nSalario promedio: ${stats.get('avg_salary', 0):,.2f}")
    
    elif args.report_file:
        generate_tracker_report(args.report_file)
    
    elif args.list:
        filters = {}
        if args.filter_key and args.filter_value:
            filters[args.filter_key] = args.filter_value
        
        offers = get_offers(filters) if filters else get_offers()
        
        print(f"\n📋 Ofertas registradas: {len(offers)}\n")
        for offer in offers[-20:]:  # Últimas 20
            print(f"[{offer.get('id')}] {offer.get('timestamp', '')[:10]} - {offer.get('position_title')} - {offer.get('candidate_name')}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()



