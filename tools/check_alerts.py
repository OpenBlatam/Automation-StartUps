#!/usr/bin/env python3
"""
Sistema de alertas para monitoreo de creativos
Detecta problemas y genera alertas prioritizadas
"""
import csv
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

ALERT_LEVELS = {
    'critical': {'icon': '🔴', 'priority': 1},
    'high': {'icon': '🟠', 'priority': 2},
    'medium': {'icon': '🟡', 'priority': 3},
    'low': {'icon': '🔵', 'priority': 4},
    'info': {'icon': 'ℹ️', 'priority': 5}
}

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

def check_utms(creatives):
    """Verifica problemas con UTMs"""
    alerts = []
    
    for i, creative in enumerate(creatives, start=2):
        issues = []
        
        # Verificar final_url tiene UTMs
        final_url = creative.get('final_url', '')
        if not final_url:
            issues.append("Sin final_url")
        elif 'utm_source=' not in final_url:
            issues.append("final_url sin UTMs")
        
        # Verificar utm_content válido
        utm_content = creative.get('utm_content', '')
        if not utm_content:
            issues.append("utm_content vacío")
        elif not utm_content.replace('_', '').replace('-', '').isalnum():
            issues.append(f"utm_content inválido: {utm_content}")
        
        if issues:
            alerts.append({
                'level': 'high',
                'type': 'utm_validation',
                'creative': creative.get('creative_file', f'Row {i}'),
                'issues': issues
            })
    
    return alerts

def check_format_balance(creatives):
    """Verifica balance de formatos"""
    alerts = []
    
    by_format = defaultdict(int)
    for creative in creatives:
        formato = creative.get('formato', 'unknown')
        by_format[formato] += 1
    
    total = len(creatives)
    if total == 0:
        return alerts
    
    # Targets ideales
    ideal_distribution = {
        '1200x627': 0.30,
        '1080x1080': 0.30,
        '1080x1920': 0.20,
        'carousel': 0.20
    }
    
    for formato, ideal_pct in ideal_distribution.items():
        actual_count = by_format.get(formato, 0)
        actual_pct = (actual_count / total) if total > 0 else 0
        gap = ideal_pct - actual_pct
        
        if gap > 0.15:  # Más de 15% de diferencia
            alerts.append({
                'level': 'medium',
                'type': 'format_balance',
                'message': f"Formato {formato} sub-representado",
                'detail': f"{formato}: {actual_pct:.1%} (ideal: {ideal_pct:.1%})",
                'action': f"Crear ~{int(gap * total)} creativos adicionales en formato {formato}"
            })
    
    return alerts

def check_missing_assets(creatives):
    """Verifica que los assets existan"""
    alerts = []
    
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    assets_dir = root_dir / 'assets'
    
    missing_count = 0
    missing_files = []
    
    for creative in creatives:
        creative_file = creative.get('creative_file', '')
        if not creative_file:
            continue
        
        # Buscar en diferentes ubicaciones
        found = False
        for base_dir in [assets_dir / 'linkedin', assets_dir]:
            file_path = base_dir / creative_file
            if file_path.exists():
                found = True
                break
        
        if not found:
            missing_count += 1
            missing_files.append(creative_file)
    
    if missing_count > 0:
        level = 'critical' if missing_count > 5 else 'high'
        alerts.append({
            'level': level,
            'type': 'missing_assets',
            'message': f"{missing_count} asset(s) no encontrado(s)",
            'detail': f"Archivos: {', '.join(missing_files[:5])}" + (f"... y {missing_count - 5} más" if missing_count > 5 else ""),
            'action': 'Verificar rutas de archivos en CSV o crear assets faltantes'
        })
    
    return alerts

def check_data_quality(creatives):
    """Verifica calidad de datos"""
    alerts = []
    
    empty_fields = defaultdict(int)
    duplicates = {}
    
    seen_files = {}
    
    for i, creative in enumerate(creatives, start=2):
        creative_file = creative.get('creative_file', '')
        
        # Verificar campos vacíos críticos
        for field in ['formato', 'producto', 'utm_content']:
            if not creative.get(field):
                empty_fields[field] += 1
        
        # Verificar duplicados
        if creative_file:
            if creative_file in seen_files:
                duplicates[creative_file] = [seen_files[creative_file], i]
            else:
                seen_files[creative_file] = i
    
    # Alertas de campos vacíos
    for field, count in empty_fields.items():
        if count > 0:
            alerts.append({
                'level': 'high' if count > len(creatives) * 0.1 else 'medium',
                'type': 'data_quality',
                'message': f"{count} registro(s) sin {field}",
                'action': f"Completar campo {field} en CSV Master"
            })
    
    # Alertas de duplicados
    if duplicates:
        alerts.append({
            'level': 'high',
            'type': 'duplicates',
            'message': f"{len(duplicates)} duplicado(s) detectado(s)",
            'detail': f"Ejemplos: {list(duplicates.keys())[:3]}",
            'action': 'Ejecutar: python3 tools/optimize_csv_master.py'
        })
    
    return alerts

def check_recent_activity(creatives):
    """Verifica actividad reciente"""
    alerts = []
    
    # Intentar detectar fechas de modificación
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    assets_dir = root_dir / 'assets'
    
    recent_count = 0
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    
    for creative in creatives:
        creative_file = creative.get('creative_file', '')
        if not creative_file:
            continue
        
        for base_dir in [assets_dir / 'linkedin', assets_dir]:
            file_path = base_dir / creative_file
            if file_path.exists():
                try:
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime >= thirty_days_ago:
                        recent_count += 1
                except:
                    pass
                break
    
    if recent_count == 0:
        alerts.append({
            'level': 'medium',
            'type': 'activity',
            'message': 'Sin actividad reciente en últimos 30 días',
            'action': 'Considerar crear nuevos creativos'
        })
    
    return alerts

def generate_alert_summary(all_alerts):
    """Genera resumen de alertas"""
    by_level = defaultdict(list)
    
    for alert in all_alerts:
        level = alert.get('level', 'info')
        by_level[level].append(alert)
    
    summary = {
        'total': len(all_alerts),
        'by_level': {level: len(alerts) for level, alerts in by_level.items()},
        'critical_count': len(by_level.get('critical', [])),
        'high_count': len(by_level.get('high', [])),
        'medium_count': len(by_level.get('medium', [])),
        'low_count': len(by_level.get('low', [])),
        'info_count': len(by_level.get('info', []))
    }
    
    return summary, by_level

def main():
    print("=" * 80)
    print("🚨 Sistema de Alertas de Creativos")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        sys.exit(1)
    
    print(f"✅ Analizando {len(creatives)} creativos...")
    print()
    
    # Ejecutar checks
    print("🔍 Ejecutando verificaciones...")
    all_alerts = []
    
    all_alerts.extend(check_utms(creatives))
    all_alerts.extend(check_format_balance(creatives))
    all_alerts.extend(check_missing_assets(creatives))
    all_alerts.extend(check_data_quality(creatives))
    all_alerts.extend(check_recent_activity(creatives))
    
    # Generar resumen
    summary, by_level = generate_alert_summary(all_alerts)
    
    # Mostrar resumen
    print()
    print("=" * 80)
    print("📊 Resumen de Alertas")
    print("=" * 80)
    print(f"Total alertas: {summary['total']}")
    print(f"🔴 Críticas: {summary['critical_count']}")
    print(f"🟠 Altas: {summary['high_count']}")
    print(f"🟡 Medias: {summary['medium_count']}")
    print(f"🔵 Bajas: {summary['low_count']}")
    print(f"ℹ️  Info: {summary['info_count']}")
    print()
    
    # Mostrar alertas por prioridad
    if all_alerts:
        # Ordenar por prioridad
        sorted_alerts = sorted(
            all_alerts,
            key=lambda a: ALERT_LEVELS.get(a.get('level', 'info'), {}).get('priority', 99)
        )
        
        print("=" * 80)
        print("🚨 Alertas Detalladas")
        print("=" * 80)
        print()
        
        for i, alert in enumerate(sorted_alerts[:20], 1):  # Mostrar top 20
            level_info = ALERT_LEVELS.get(alert.get('level', 'info'), {})
            icon = level_info.get('icon', '•')
            
            print(f"{i}. {icon} [{alert.get('level', 'info').upper()}] {alert.get('message', 'Sin mensaje')}")
            
            if 'detail' in alert:
                print(f"   {alert['detail']}")
            
            if 'creative' in alert:
                print(f"   Creative: {alert['creative']}")
            
            if 'issues' in alert:
                print(f"   Issues: {', '.join(alert['issues'])}")
            
            if 'action' in alert:
                print(f"   💡 Acción: {alert['action']}")
            
            print()
        
        if len(sorted_alerts) > 20:
            print(f"... y {len(sorted_alerts) - 20} alerta(s) más")
            print()
    else:
        print("✅ No se detectaron alertas. Todo está en orden.")
        print()
    
    # Código de salida basado en alertas críticas
    exit_code = 0
    if summary['critical_count'] > 0:
        exit_code = 2
    elif summary['high_count'] > 0:
        exit_code = 1
    
    # Guardar reporte si se solicita
    if '--save-report' in sys.argv:
        script_dir = Path(__file__).parent
        root_dir = script_dir.parent
        reports_dir = root_dir / 'reports'
        reports_dir.mkdir(exist_ok=True)
        
        report_path = reports_dir / f'alerts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"Reporte de Alertas - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Total alertas: {summary['total']}\n")
            f.write(f"Críticas: {summary['critical_count']}\n")
            f.write(f"Altas: {summary['high_count']}\n")
            f.write(f"Medias: {summary['medium_count']}\n\n")
            
            for alert in sorted_alerts:
                level_info = ALERT_LEVELS.get(alert.get('level', 'info'), {})
                icon = level_info.get('icon', '•')
                f.write(f"{icon} [{alert.get('level', 'info').upper()}] {alert.get('message', 'Sin mensaje')}\n")
                if 'action' in alert:
                    f.write(f"   Acción: {alert['action']}\n")
                f.write("\n")
        
        print(f"📄 Reporte guardado: {report_path}")
        print()
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()

