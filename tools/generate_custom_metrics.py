#!/usr/bin/env python3
"""
Generador de Métricas Personalizadas
Permite definir y calcular KPIs personalizados basados en necesidades específicas
"""
import csv
import sys
import json
from pathlib import Path
from datetime import datetime

def load_creatives():
    """Carga creativos desde CSV Master"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    csv_path = root_dir / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
    
    if not csv_path.exists():
        return None
    
    creatives = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            creatives.append(row)
    
    return creatives

def calculate_custom_metric(creative, metric_definition):
    """Calcula una métrica personalizada"""
    metric_type = metric_definition['type']
    
    if metric_type == 'simple':
        # Métrica simple: operación aritmética básica
        formula = metric_definition['formula']
        # Reemplazar variables
        for key, value in creative.items():
            try:
                numeric_value = float(value or 0)
                formula = formula.replace(f"{{{key}}}", str(numeric_value))
            except:
                pass
        
        try:
            result = eval(formula)
            return float(result)
        except:
            return None
    
    elif metric_type == 'ratio':
        # Ratio entre dos métricas
        numerator = float(creative.get(metric_definition['numerator'], 0) or 0)
        denominator = float(creative.get(metric_definition['denominator'], 0) or 0)
        
        if denominator == 0:
            return None
        
        return (numerator / denominator) * metric_definition.get('multiplier', 100)
    
    elif metric_type == 'composite':
        # Métrica compuesta: combinación de múltiples métricas
        components = metric_definition['components']
        weights = metric_definition.get('weights', [1.0] * len(components))
        
        total = 0
        total_weight = 0
        
        for component, weight in zip(components, weights):
            value = calculate_custom_metric(creative, component)
            if value is not None:
                total += value * weight
                total_weight += weight
        
        if total_weight == 0:
            return None
        
        return total / total_weight
    
    return None

def define_built_in_metrics():
    """Define métricas pre-construidas comunes"""
    return {
        'engagement_rate': {
            'name': 'Tasa de Engagement',
            'type': 'ratio',
            'numerator': 'clicks',
            'denominator': 'impressions',
            'multiplier': 100,
            'description': 'Porcentaje de impresiones que generan clics'
        },
        'conversion_rate': {
            'name': 'Tasa de Conversión',
            'type': 'ratio',
            'numerator': 'conversions',
            'denominator': 'clicks',
            'multiplier': 100,
            'description': 'Porcentaje de clics que se convierten'
        },
        'efficiency_score': {
            'name': 'Score de Eficiencia',
            'type': 'composite',
            'components': [
                {
                    'type': 'ratio',
                    'numerator': 'clicks',
                    'denominator': 'impressions',
                    'multiplier': 100
                },
                {
                    'type': 'ratio',
                    'numerator': 'conversions',
                    'denominator': 'clicks',
                    'multiplier': 100
                }
            ],
            'weights': [0.5, 0.5],
            'description': 'Score combinado de CTR y CVR (0-100)'
        },
        'revenue_per_impression': {
            'name': 'Revenue por Impresión',
            'type': 'simple',
            'formula': '({conversions} * 500) / {impressions}',
            'description': 'Revenue estimado por cada 1000 impresiones (asumiendo LTV=500)'
        },
        'roi_per_dollar': {
            'name': 'ROI por Dólar',
            'type': 'simple',
            'formula': '(({conversions} * 500) - {spend}) / {spend}',
            'description': 'ROI calculado (asumiendo LTV=500)'
        }
    }

def calculate_all_metrics(creatives, metrics_config):
    """Calcula todas las métricas personalizadas"""
    results = []
    
    for creative in creatives:
        creative_metrics = {
            'creative_file': creative.get('creative_file', ''),
            'utm_content': creative.get('utm_content', ''),
            'formato': creative.get('formato', ''),
            'producto': creative.get('producto', '')
        }
        
        for metric_name, metric_def in metrics_config.items():
            value = calculate_custom_metric(creative, metric_def)
            if value is not None:
                creative_metrics[metric_name] = value
        
        results.append(creative_metrics)
    
    return results

def generate_metrics_report(results, metrics_config):
    """Genera reporte de métricas"""
    print("=" * 80)
    print("📊 Reporte de Métricas Personalizadas")
    print("=" * 80)
    print()
    
    # Estadísticas por métrica
    for metric_name, metric_def in metrics_config.items():
        metric_values = [r.get(metric_name) for r in results if r.get(metric_name) is not None]
        
        if not metric_values:
            continue
        
        avg = sum(metric_values) / len(metric_values)
        min_val = min(metric_values)
        max_val = max(metric_values)
        
        print(f"📈 {metric_def['name']} ({metric_name})")
        print(f"   {metric_def.get('description', 'Sin descripción')}")
        print(f"   Promedio: {avg:.2f}")
        print(f"   Mínimo: {min_val:.2f}")
        print(f"   Máximo: {max_val:.2f}")
        print(f"   Creativos con datos: {len(metric_values)}/{len(results)}")
        print()
        
        # Top 5
        top_5 = sorted(
            [(r['creative_file'], r.get(metric_name)) for r in results if r.get(metric_name) is not None],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        if top_5:
            print(f"   🏆 Top 5:")
            for i, (creative_file, value) in enumerate(top_5, 1):
                print(f"      {i}. {creative_file}: {value:.2f}")
            print()

def main():
    print("=" * 80)
    print("📊 Generador de Métricas Personalizadas")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Cargados {len(creatives)} creativos")
    print()
    
    # Cargar métricas pre-construidas o personalizadas
    metrics_config = define_built_in_metrics()
    
    # Opción de cargar métricas personalizadas desde archivo
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    custom_metrics_path = root_dir / 'custom_metrics.json'
    
    if custom_metrics_path.exists():
        print("📝 Cargando métricas personalizadas...")
        with open(custom_metrics_path, 'r', encoding='utf-8') as f:
            custom_metrics = json.load(f)
            metrics_config.update(custom_metrics)
        print(f"✅ {len(custom_metrics)} métrica(s) personalizada(s) cargada(s)")
        print()
    
    print(f"📊 Calculando {len(metrics_config)} métrica(s)...")
    
    # Calcular métricas
    results = calculate_all_metrics(creatives, metrics_config)
    
    # Generar reporte
    generate_metrics_report(results, metrics_config)
    
    # Guardar resultados
    reports_dir = root_dir / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_path = reports_dir / f'custom_metrics_{timestamp}.csv'
    
    if results:
        fieldnames = list(results[0].keys())
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"📄 Resultados guardados: {csv_path}")
        print()
    
    # Crear template de métricas personalizadas si no existe
    if not custom_metrics_path.exists():
        template = {
            "my_custom_metric": {
                "name": "Mi Métrica Personalizada",
                "type": "simple",
                "formula": "({clicks} / {impressions}) * 100",
                "description": "Ejemplo de métrica personalizada"
            }
        }
        
        with open(custom_metrics_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2)
        
        print(f"💡 Template de métricas personalizadas creado: {custom_metrics_path}")
        print("   Edita el archivo para añadir tus propias métricas")

if __name__ == '__main__':
    main()

