#!/usr/bin/env python3
"""
Health check completo del sistema TikTok Auto Edit
Verifica que todos los componentes estén funcionando correctamente
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemHealthCheck:
    """Verificación de salud del sistema"""
    
    def __init__(self):
        """Inicializa el health check"""
        self.checks = []
        self.errors = []
        self.warnings = []
    
    def check_python(self) -> bool:
        """Verifica Python"""
        try:
            import sys
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                self.checks.append({
                    'name': 'Python',
                    'status': 'ok',
                    'message': f'Python {version.major}.{version.minor}.{version.micro}'
                })
                return True
            else:
                self.errors.append({
                    'name': 'Python',
                    'message': f'Python 3.8+ requerido, encontrado {version.major}.{version.minor}'
                })
                return False
        except Exception as e:
            self.errors.append({'name': 'Python', 'message': str(e)})
            return False
    
    def check_ffmpeg(self) -> bool:
        """Verifica FFmpeg"""
        try:
            import subprocess
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                self.checks.append({
                    'name': 'FFmpeg',
                    'status': 'ok',
                    'message': version
                })
                return True
            else:
                self.errors.append({
                    'name': 'FFmpeg',
                    'message': 'FFmpeg no encontrado o no funciona'
                })
                return False
        except FileNotFoundError:
            self.errors.append({
                'name': 'FFmpeg',
                'message': 'FFmpeg no está instalado'
            })
            return False
        except Exception as e:
            self.errors.append({'name': 'FFmpeg', 'message': str(e)})
            return False
    
    def check_dependencies(self) -> bool:
        """Verifica dependencias Python"""
        required = [
            'yt_dlp',
            'cv2',
            'numpy',
            'moviepy',
            'openai',
            'flask',
            'requests',
            'psutil'
        ]
        
        missing = []
        for dep in required:
            try:
                __import__(dep)
                self.checks.append({
                    'name': f'Dependency: {dep}',
                    'status': 'ok'
                })
            except ImportError:
                missing.append(dep)
                self.errors.append({
                    'name': f'Dependency: {dep}',
                    'message': 'No instalado'
                })
        
        return len(missing) == 0
    
    def check_openai_key(self) -> bool:
        """Verifica OpenAI API Key"""
        key = os.getenv('OPENAI_API_KEY')
        if key:
            if key.startswith('sk-'):
                self.checks.append({
                    'name': 'OpenAI API Key',
                    'status': 'ok',
                    'message': 'Configurada'
                })
                return True
            else:
                self.warnings.append({
                    'name': 'OpenAI API Key',
                    'message': 'Formato puede ser incorrecto'
                })
                return False
        else:
            self.warnings.append({
                'name': 'OpenAI API Key',
                'message': 'No configurada (requerida para análisis con IA)'
            })
            return False
    
    def check_directories(self) -> bool:
        """Verifica directorios necesarios"""
        dirs = [
            Path.home() / '.tiktok_cache',
            Path.home() / '.tiktok_templates',
            Path('/tmp/tiktok_downloads'),
            Path('/tmp/tiktok_edited')
        ]
        
        all_ok = True
        for dir_path in dirs:
            if dir_path.exists() and dir_path.is_dir():
                self.checks.append({
                    'name': f'Directory: {dir_path}',
                    'status': 'ok'
                })
            else:
                self.warnings.append({
                    'name': f'Directory: {dir_path}',
                    'message': 'No existe (se creará automáticamente)'
                })
                all_ok = False
        
        return all_ok
    
    def check_scripts(self) -> bool:
        """Verifica que los scripts principales existan"""
        scripts_dir = Path(__file__).parent
        required_scripts = [
            'tiktok_downloader.py',
            'video_script_generator.py',
            'video_editor.py'
        ]
        
        missing = []
        for script in required_scripts:
            script_path = scripts_dir / script
            if script_path.exists():
                self.checks.append({
                    'name': f'Script: {script}',
                    'status': 'ok'
                })
            else:
                missing.append(script)
                self.errors.append({
                    'name': f'Script: {script}',
                    'message': 'No encontrado'
                })
        
        return len(missing) == 0
    
    def check_disk_space(self) -> bool:
        """Verifica espacio en disco"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            free_gb = free / (1024**3)
            
            if free_gb > 10:
                self.checks.append({
                    'name': 'Disk Space',
                    'status': 'ok',
                    'message': f'{free_gb:.1f} GB disponibles'
                })
                return True
            elif free_gb > 5:
                self.warnings.append({
                    'name': 'Disk Space',
                    'message': f'Solo {free_gb:.1f} GB disponibles'
                })
                return True
            else:
                self.errors.append({
                    'name': 'Disk Space',
                    'message': f'Muy poco espacio: {free_gb:.1f} GB'
                })
                return False
        except Exception as e:
            self.warnings.append({
                'name': 'Disk Space',
                'message': f'No se pudo verificar: {e}'
            })
            return False
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Ejecuta todos los checks"""
        logger.info("Iniciando health check del sistema...")
        
        self.check_python()
        self.check_ffmpeg()
        self.check_dependencies()
        self.check_openai_key()
        self.check_directories()
        self.check_scripts()
        self.check_disk_space()
        
        total_checks = len(self.checks) + len(self.errors) + len(self.warnings)
        passed = len(self.checks)
        
        health_status = 'healthy'
        if len(self.errors) > 0:
            health_status = 'unhealthy'
        elif len(self.warnings) > 0:
            health_status = 'degraded'
        
        return {
            'status': health_status,
            'total_checks': total_checks,
            'passed': passed,
            'errors': len(self.errors),
            'warnings': len(self.warnings),
            'checks': self.checks,
            'errors_list': self.errors,
            'warnings_list': self.warnings
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Health check del sistema TikTok Auto Edit')
    parser.add_argument('-j', '--json', action='store_true', help='Salida en JSON')
    parser.add_argument('-v', '--verbose', action='store_true', help='Modo verbose')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    checker = SystemHealthCheck()
    result = checker.run_all_checks()
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("\n" + "="*60)
        print("🎬 TikTok Auto Edit - Health Check")
        print("="*60)
        print(f"\nEstado: {result['status'].upper()}")
        print(f"Checks pasados: {result['passed']}/{result['total_checks']}")
        print(f"Errores: {result['errors']}")
        print(f"Advertencias: {result['warnings']}")
        
        if result['errors_list']:
            print("\n❌ ERRORES:")
            for error in result['errors_list']:
                print(f"  • {error['name']}: {error['message']}")
        
        if result['warnings_list']:
            print("\n⚠️  ADVERTENCIAS:")
            for warning in result['warnings_list']:
                print(f"  • {warning['name']}: {warning['message']}")
        
        if result['checks']:
            print("\n✅ CHECKS EXITOSOS:")
            for check in result['checks'][:10]:  # Mostrar primeros 10
                print(f"  • {check['name']}")
            if len(result['checks']) > 10:
                print(f"  ... y {len(result['checks']) - 10} más")
        
        print("\n" + "="*60)
    
    # Exit code
    sys.exit(0 if result['status'] == 'healthy' else 1)


if __name__ == '__main__':
    main()


