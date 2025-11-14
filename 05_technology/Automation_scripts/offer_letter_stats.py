#!/usr/bin/env python3
"""
Sistema de Estadísticas y Reportes para Cartas de Oferta
Analiza y genera reportes sobre ofertas generadas
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Dict
from collections import defaultdict
import sys


def analyze_offer_file(file_path: str) -> Dict:
    """Analiza un archivo de carta de oferta y extrae estadísticas."""
    stats = {
        'file': os.path.basename(file_path),
        'size': os.path.getsize(file_path),
        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Extraer información básica
            stats['has_company_details'] = 'COMPANY OVERVIEW' in content
            stats['has_equity'] = 'Equity' in content or 'Stock Options' in content
            stats['has_bonus'] = 'Bonus' in content or 'bonus' in content
            stats['has_sign_on'] = 'Sign-on' in content or 'sign-on' in content
            stats['word_count'] = len(content.split())
            stats['line_count'] = len(content.split('\n'))
            
            # Intentar extraer salario
            import re
            salary_match = re.search(r'\$([\d,]+\.?\d*)', content)
            if salary_match:
                stats['salary'] = float(salary_match.group(1).replace(',', ''))
            
    except Exception as e:
        stats['error'] = str(e)
    
    return stats


def analyze_directory(directory: str = "offer_letters") -> Dict:
    """Analiza todos los archivos de ofertas en un directorio."""
    if not os.path.exists(directory):
        return {'error': f'Directory {directory} does not exist'}
    
    stats = {
        'directory': directory,
        'total_files': 0,
        'total_size': 0,
        'files': [],
        'summary': {
            'with_company_details': 0,
            'with_equity': 0,
            'with_bonus': 0,
            'with_sign_on': 0,
            'total_word_count': 0,
            'total_salary': 0,
            'salary_count': 0,
            'avg_salary': 0,
            'min_salary': float('inf'),
            'max_salary': 0
        }
    }
    
    for filename in os.listdir(directory):
        if filename.endswith(('.txt', '.html')):
            file_path = os.path.join(directory, filename)
            file_stats = analyze_offer_file(file_path)
            stats['files'].append(file_stats)
            stats['total_files'] += 1
            stats['total_size'] += file_stats.get('size', 0)
            
            # Actualizar resumen
            summary = stats['summary']
            if file_stats.get('has_company_details'):
                summary['with_company_details'] += 1
            if file_stats.get('has_equity'):
                summary['with_equity'] += 1
            if file_stats.get('has_bonus'):
                summary['with_bonus'] += 1
            if file_stats.get('has_sign_on'):
                summary['with_sign_on'] += 1
            
            summary['total_word_count'] += file_stats.get('word_count', 0)
            
            if 'salary' in file_stats:
                salary = file_stats['salary']
                summary['total_salary'] += salary
                summary['salary_count'] += 1
                summary['min_salary'] = min(summary['min_salary'], salary)
                summary['max_salary'] = max(summary['max_salary'], salary)
    
    # Calcular promedio
    if stats['summary']['salary_count'] > 0:
        stats['summary']['avg_salary'] = stats['summary']['total_salary'] / stats['summary']['salary_count']
    
    if stats['summary']['min_salary'] == float('inf'):
        stats['summary']['min_salary'] = 0
    
    return stats


def generate_report(stats: Dict, output_file: str = "offer_report.txt"):
    """Genera un reporte de texto con las estadísticas."""
    report = f"""
{'='*70}
  REPORTE DE ESTADÍSTICAS - CARTAS DE OFERTA
{'='*70}

Directorio analizado: {stats.get('directory', 'N/A')}
Fecha del reporte: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

RESUMEN GENERAL
{'-'*70}
Total de archivos: {stats.get('total_files', 0)}
Tamaño total: {stats.get('total_size', 0):,} bytes ({stats.get('total_size', 0) / 1024:.2f} KB)

CARACTERÍSTICAS DE LAS OFERTAS
{'-'*70}
Ofertas con descripción de empresa: {stats['summary'].get('with_company_details', 0)}
Ofertas con equity/stock options: {stats['summary'].get('with_equity', 0)}
Ofertas con bonos: {stats['summary'].get('with_bonus', 0)}
Ofertas con sign-on bonus: {stats['summary'].get('with_sign_on', 0)}

ESTADÍSTICAS DE CONTENIDO
{'-'*70}
Total de palabras: {stats['summary'].get('total_word_count', 0):,}
Promedio de palabras por oferta: {stats['summary'].get('total_word_count', 0) / max(stats.get('total_files', 1), 1):.0f}

ESTADÍSTICAS DE SALARIOS
{'-'*70}
"""
    
    if stats['summary'].get('salary_count', 0) > 0:
        report += f"""Ofertas con salario especificado: {stats['summary']['salary_count']}
Salario promedio: ${stats['summary'].get('avg_salary', 0):,.2f}
Salario mínimo: ${stats['summary'].get('min_salary', 0):,.2f}
Salario máximo: ${stats['summary'].get('max_salary', 0):,.2f}
"""
    else:
        report += "No se encontraron salarios en las ofertas analizadas.\n"
    
    report += f"""
DETALLE DE ARCHIVOS
{'-'*70}
"""
    
    for file_stat in stats.get('files', [])[:10]:  # Mostrar primeros 10
        report += f"\n📄 {file_stat.get('file', 'N/A')}\n"
        report += f"   Tamaño: {file_stat.get('size', 0):,} bytes\n"
        report += f"   Palabras: {file_stat.get('word_count', 0):,}\n"
        if 'salary' in file_stat:
            report += f"   Salario: ${file_stat['salary']:,.2f}\n"
    
    if len(stats.get('files', [])) > 10:
        report += f"\n... y {len(stats.get('files', [])) - 10} archivos más\n"
    
    report += f"""
{'='*70}
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✓ Reporte generado: {output_file}")
    return report


def generate_json_report(stats: Dict, output_file: str = "offer_report.json"):
    """Genera un reporte en formato JSON."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"✓ Reporte JSON generado: {output_file}")


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analiza y genera reportes de cartas de oferta')
    parser.add_argument('--directory', '-d', default='offer_letters',
                       help='Directorio a analizar (default: offer_letters)')
    parser.add_argument('--output', '-o', default='offer_report.txt',
                       help='Archivo de salida del reporte (default: offer_report.txt)')
    parser.add_argument('--json', action='store_true',
                       help='Generar también reporte en JSON')
    parser.add_argument('--print', action='store_true',
                       help='Imprimir reporte en consola')
    
    args = parser.parse_args()
    
    print(f"📊 Analizando directorio: {args.directory}")
    stats = analyze_directory(args.directory)
    
    if 'error' in stats:
        print(f"❌ Error: {stats['error']}", file=sys.stderr)
        sys.exit(1)
    
    # Generar reporte de texto
    report = generate_report(stats, args.output)
    
    # Generar reporte JSON si se solicita
    if args.json:
        json_output = args.output.replace('.txt', '.json')
        generate_json_report(stats, json_output)
    
    # Imprimir si se solicita
    if args.print:
        print(report)


if __name__ == '__main__':
    main()





