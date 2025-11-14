#!/usr/bin/env python3
"""
Analizador avanzado: duplicados, archivos temporales, métricas y optimizaciones
"""

import os
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import mimetypes

class AdvancedAnalyzer:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.duplicates = []
        self.temp_files = []
        self.metrics = {}
        self.optimization_suggestions = []
        
    def find_duplicates(self):
        """Encuentra archivos duplicados por hash MD5"""
        print("🔍 Buscando duplicados...")
        hash_map = defaultdict(list)
        
        for file_path in self.base_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    hash_map[file_hash].append(file_path)
                except (PermissionError, OSError):
                    continue
        
        self.duplicates = [files for files in hash_map.values() if len(files) > 1]
        return len(self.duplicates)
    
    def find_temp_files(self):
        """Encuentra archivos temporales y obsoletos"""
        print("🗑️  Buscando archivos temporales...")
        temp_patterns = [
            '*.tmp', '*.temp', '*.bak', '*.backup', '*.old',
            '~*', '*.swp', '*.swo', '*.log', '*.cache'
        ]
        
        # Archivos más antiguos que 6 meses sin modificar
        cutoff_date = datetime.now() - timedelta(days=180)
        
        for file_path in self.base_dir.rglob("*"):
            if file_path.is_file():
                is_temp = False
                
                # Patrones de nombres
                for pattern in temp_patterns:
                    if file_path.match(pattern):
                        is_temp = True
                        break
                
                # Archivos muy antiguos
                try:
                    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mod_time < cutoff_date and file_path.suffix.lower() in ['.log', '.cache', '.tmp']:
                        is_temp = True
                except OSError:
                    continue
                
                if is_temp:
                    self.temp_files.append(file_path)
        
        return len(self.temp_files)
    
    def calculate_metrics(self):
        """Calcula métricas avanzadas de organización"""
        print("📊 Calculando métricas...")
        
        total_files = 0
        organized_files = 0
        folder_stats = {}
        extension_stats = Counter()
        size_stats = {'total_size': 0, 'avg_size': 0}
        
        for folder in self.base_dir.iterdir():
            if folder.is_dir() and not folder.name.startswith('.'):
                folder_files = list(folder.rglob("*"))
                files_only = [f for f in folder_files if f.is_file()]
                
                folder_stats[folder.name] = {
                    'total_files': len(files_only),
                    'subfolders': len([f for f in folder_files if f.is_dir()]),
                    'size_mb': sum(f.stat().st_size for f in files_only if f.is_file()) / (1024*1024)
                }
                
                total_files += len(files_only)
                
                # Archivos en subcarpetas = organizados
                subfolder_files = [f for f in files_only if f.parent != folder]
                organized_files += len(subfolder_files)
                
                # Estadísticas por extensión
                for file_path in files_only:
                    extension_stats[file_path.suffix.lower()] += 1
                    try:
                        size_stats['total_size'] += file_path.stat().st_size
                    except OSError:
                        continue
        
        size_stats['avg_size'] = size_stats['total_size'] / total_files if total_files > 0 else 0
        size_stats['total_size_mb'] = size_stats['total_size'] / (1024*1024)
        
        self.metrics = {
            'total_files': total_files,
            'organized_files': organized_files,
            'organization_rate': (organized_files / total_files * 100) if total_files > 0 else 0,
            'folder_stats': folder_stats,
            'extension_stats': dict(extension_stats.most_common(10)),
            'size_stats': size_stats,
            'duplicates_count': len(self.duplicates),
            'temp_files_count': len(self.temp_files)
        }
        
        return self.metrics
    
    def generate_optimization_suggestions(self):
        """Genera sugerencias de optimización"""
        print("💡 Generando sugerencias de optimización...")
        
        suggestions = []
        
        # Sugerencias basadas en duplicados
        if self.duplicates:
            suggestions.append({
                'type': 'duplicates',
                'priority': 'high',
                'title': f'Eliminar {len(self.duplicates)} grupos de duplicados',
                'description': f'Se encontraron {sum(len(group) for group in self.duplicates)} archivos duplicados',
                'action': 'review_duplicates'
            })
        
        # Sugerencias basadas en archivos temporales
        if self.temp_files:
            suggestions.append({
                'type': 'cleanup',
                'priority': 'medium',
                'title': f'Limpiar {len(self.temp_files)} archivos temporales',
                'description': 'Archivos .tmp, .log, .cache y archivos antiguos',
                'action': 'cleanup_temp'
            })
        
        # Sugerencias basadas en métricas
        if self.metrics.get('organization_rate', 0) < 90:
            suggestions.append({
                'type': 'organization',
                'priority': 'high',
                'title': 'Mejorar tasa de organización',
                'description': f'Tasa actual: {self.metrics.get("organization_rate", 0):.1f}%',
                'action': 'improve_organization'
            })
        
        # Sugerencias de carpetas con muchos archivos
        for folder, stats in self.metrics.get('folder_stats', {}).items():
            if stats['total_files'] > 50 and stats['subfolders'] < 5:
                suggestions.append({
                    'type': 'structure',
                    'priority': 'medium',
                    'title': f'Reorganizar carpeta {folder}',
                    'description': f'{stats["total_files"]} archivos, solo {stats["subfolders"]} subcarpetas',
                    'action': 'reorganize_folder',
                    'target': folder
                })
        
        self.optimization_suggestions = suggestions
        return suggestions
    
    def generate_dashboard_data(self):
        """Genera datos para dashboard interactivo"""
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics,
            'duplicates': [
                {
                    'hash': hashlib.md5(str(group[0]).encode()).hexdigest()[:8],
                    'files': [str(f.relative_to(self.base_dir)) for f in group],
                    'size_mb': group[0].stat().st_size / (1024*1024) if group[0].exists() else 0
                }
                for group in self.duplicates
            ],
            'temp_files': [
                {
                    'path': str(f.relative_to(self.base_dir)),
                    'size_mb': f.stat().st_size / (1024*1024) if f.exists() else 0,
                    'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat() if f.exists() else None
                }
                for f in self.temp_files
            ],
            'suggestions': self.optimization_suggestions
        }
        
        return dashboard_data
    
    def generate_html_dashboard(self, output_path):
        """Genera dashboard HTML interactivo"""
        dashboard_data = self.generate_dashboard_data()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Organización - BLATAM</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f7; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
        .section {{ background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .suggestion {{ background: #f8f9fa; border-left: 4px solid #667eea; padding: 15px; margin: 10px 0; border-radius: 0 8px 8px 0; }}
        .priority-high {{ border-left-color: #dc3545; }}
        .priority-medium {{ border-left-color: #ffc107; }}
        .priority-low {{ border-left-color: #28a745; }}
        .duplicate-group {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 5px 0; border-radius: 4px; }}
        .temp-file {{ background: #f8d7da; border: 1px solid #f5c6cb; padding: 8px; margin: 3px 0; border-radius: 4px; }}
        .btn {{ background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }}
        .btn:hover {{ background: #5a6fd8; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Dashboard de Organización BLATAM</h1>
            <p>Análisis avanzado del sistema de archivos - {dashboard_data['timestamp'][:19]}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{dashboard_data['metrics']['total_files']:,}</div>
                <div class="metric-label">Total Archivos</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{dashboard_data['metrics']['organization_rate']:.1f}%</div>
                <div class="metric-label">Tasa de Organización</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{dashboard_data['metrics']['size_stats']['total_size_mb']:.1f} MB</div>
                <div class="metric-label">Tamaño Total</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(dashboard_data['duplicates'])}</div>
                <div class="metric-label">Grupos Duplicados</div>
            </div>
        </div>
        
        <div class="section">
            <h2>💡 Sugerencias de Optimización</h2>
            {''.join([f'<div class="suggestion priority-{s["priority"]}"><strong>{s["title"]}</strong><br>{s["description"]}</div>' for s in dashboard_data['suggestions']])}
        </div>
        
        <div class="section">
            <h2>🔄 Archivos Duplicados</h2>
            {''.join([f'<div class="duplicate-group"><strong>Grupo {i+1}</strong> ({len(group["files"])} archivos, {group["size_mb"]:.2f} MB)<br>' + '<br>'.join(group["files"]) + '</div>' for i, group in enumerate(dashboard_data['duplicates'][:10])])}
        </div>
        
        <div class="section">
            <h2>🗑️ Archivos Temporales</h2>
            {''.join([f'<div class="temp-file">{file["path"]} ({file["size_mb"]:.2f} MB)</div>' for file in dashboard_data['temp_files'][:20]])}
        </div>
        
        <div class="section">
            <h2>📈 Estadísticas por Extensión</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                {''.join([f'<div style="background: #e9ecef; padding: 10px; border-radius: 4px;"><strong>{ext or "Sin extensión"}</strong>: {count}</div>' for ext, count in list(dashboard_data['metrics']['extension_stats'].items())[:10]])}
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path

def main():
    base_dir = Path(__file__).parent
    analyzer = AdvancedAnalyzer(base_dir)
    
    print("🚀 Iniciando análisis avanzado...")
    
    # Ejecutar análisis
    duplicates_count = analyzer.find_duplicates()
    temp_count = analyzer.find_temp_files()
    metrics = analyzer.calculate_metrics()
    suggestions = analyzer.generate_optimization_suggestions()
    
    # Generar dashboard
    dashboard_path = base_dir / "advanced_dashboard.html"
    analyzer.generate_dashboard_data()
    dashboard_file = analyzer.generate_html_dashboard(dashboard_path)
    
    # Guardar datos JSON
    json_path = base_dir / "advanced_analysis.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analyzer.generate_dashboard_data(), f, indent=2, ensure_ascii=False)
    
    print(f"✅ Análisis completado:")
    print(f"   📊 Archivos totales: {metrics['total_files']:,}")
    print(f"   📈 Tasa de organización: {metrics['organization_rate']:.1f}%")
    print(f"   🔄 Duplicados: {duplicates_count} grupos")
    print(f"   🗑️  Archivos temporales: {temp_count}")
    print(f"   💡 Sugerencias: {len(suggestions)}")
    print(f"   📄 Dashboard: {dashboard_file}")
    print(f"   📄 Datos JSON: {json_path}")

if __name__ == "__main__":
    main()



