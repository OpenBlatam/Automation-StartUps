#!/usr/bin/env python3
"""
Tests automatizados para el sistema TikTok Auto Edit
Verifica que todos los componentes funcionen correctamente
"""

import os
import sys
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemTester:
    """Tester del sistema completo"""
    
    def __init__(self):
        """Inicializa el tester"""
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
    
    def test_imports(self) -> bool:
        """Test: Verifica que todos los módulos se puedan importar"""
        logger.info("Test: Imports de módulos...")
        
        modules = [
            'tiktok_downloader',
            'video_script_generator',
            'video_editor',
            'tiktok_analytics',
            'tiktok_queue_manager'
        ]
        
        failed = []
        for module in modules:
            try:
                __import__(module)
                logger.info(f"  ✓ {module}")
            except ImportError as e:
                logger.error(f"  ✗ {module}: {e}")
                failed.append(module)
        
        success = len(failed) == 0
        self._record_test('imports', success, failed)
        return success
    
    def test_downloader(self) -> bool:
        """Test: Verifica que el downloader funcione"""
        logger.info("Test: TikTok Downloader...")
        
        try:
            from tiktok_downloader import TikTokDownloader
            
            downloader = TikTokDownloader()
            # No descargamos realmente, solo verificamos que se inicialice
            logger.info("  ✓ Downloader inicializado correctamente")
            
            self._record_test('downloader', True)
            return True
        except Exception as e:
            logger.error(f"  ✗ Error: {e}")
            self._record_test('downloader', False, str(e))
            return False
    
    def test_script_generator(self) -> bool:
        """Test: Verifica que el generador de scripts funcione"""
        logger.info("Test: Script Generator...")
        
        try:
            from video_script_generator import VideoScriptGenerator
            
            # Verificar que OpenAI API Key esté configurada
            if not os.getenv('OPENAI_API_KEY'):
                logger.warning("  ⚠ OpenAI API Key no configurada (test limitado)")
                self._record_test('script_generator', True, 'API key no configurada')
                return True
            
            generator = VideoScriptGenerator()
            logger.info("  ✓ Script Generator inicializado")
            
            self._record_test('script_generator', True)
            return True
        except Exception as e:
            logger.error(f"  ✗ Error: {e}")
            self._record_test('script_generator', False, str(e))
            return False
    
    def test_editor(self) -> bool:
        """Test: Verifica que el editor funcione"""
        logger.info("Test: Video Editor...")
        
        try:
            from video_editor import VideoEditor
            
            editor = VideoEditor()
            logger.info("  ✓ Video Editor inicializado")
            
            self._record_test('editor', True)
            return True
        except Exception as e:
            logger.error(f"  ✗ Error: {e}")
            self._record_test('editor', False, str(e))
            return False
    
    def test_analytics(self) -> bool:
        """Test: Verifica que analytics funcione"""
        logger.info("Test: Analytics...")
        
        try:
            from tiktok_analytics import TikTokAnalytics
            
            analytics = TikTokAnalytics()
            stats = analytics.get_stats(1)
            logger.info("  ✓ Analytics funcionando")
            
            self._record_test('analytics', True)
            return True
        except Exception as e:
            logger.error(f"  ✗ Error: {e}")
            self._record_test('analytics', False, str(e))
            return False
    
    def test_templates(self) -> bool:
        """Test: Verifica que templates funcionen"""
        logger.info("Test: Templates...")
        
        try:
            from tiktok_templates import TemplateManager
            
            manager = TemplateManager()
            templates = manager.list_templates()
            logger.info(f"  ✓ Templates: {len(templates)} disponibles")
            
            self._record_test('templates', True)
            return True
        except Exception as e:
            logger.error(f"  ✗ Error: {e}")
            self._record_test('templates', False, str(e))
            return False
    
    def test_queue_manager(self) -> bool:
        """Test: Verifica que queue manager funcione"""
        logger.info("Test: Queue Manager...")
        
        try:
            from tiktok_queue_manager import TikTokQueueManager
            
            manager = TikTokQueueManager(max_workers=1)
            stats = manager.get_queue_stats()
            logger.info("  ✓ Queue Manager funcionando")
            
            self._record_test('queue_manager', True)
            return True
        except Exception as e:
            logger.error(f"  ✗ Error: {e}")
            self._record_test('queue_manager', False, str(e))
            return False
    
    def test_ffmpeg(self) -> bool:
        """Test: Verifica que FFmpeg esté disponible"""
        logger.info("Test: FFmpeg...")
        
        try:
            import subprocess
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.info("  ✓ FFmpeg disponible")
                self._record_test('ffmpeg', True)
                return True
            else:
                logger.error("  ✗ FFmpeg no funciona correctamente")
                self._record_test('ffmpeg', False, 'FFmpeg no funciona')
                return False
        except FileNotFoundError:
            logger.error("  ✗ FFmpeg no encontrado")
            self._record_test('ffmpeg', False, 'FFmpeg no instalado')
            return False
        except Exception as e:
            logger.error(f"  ✗ Error: {e}")
            self._record_test('ffmpeg', False, str(e))
            return False
    
    def test_directories(self) -> bool:
        """Test: Verifica que los directorios necesarios existan o se puedan crear"""
        logger.info("Test: Directorios...")
        
        dirs = [
            Path.home() / '.tiktok_cache',
            Path.home() / '.tiktok_templates',
            Path('/tmp/tiktok_downloads'),
            Path('/tmp/tiktok_edited')
        ]
        
        failed = []
        for dir_path in dirs:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                if dir_path.exists():
                    logger.info(f"  ✓ {dir_path}")
                else:
                    failed.append(str(dir_path))
            except Exception as e:
                logger.error(f"  ✗ {dir_path}: {e}")
                failed.append(str(dir_path))
        
        success = len(failed) == 0
        self._record_test('directories', success, failed)
        return success
    
    def _record_test(self, name: str, passed: bool, details: Any = None):
        """Registra resultado de un test"""
        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
        
        self.results.append({
            'name': name,
            'passed': passed,
            'details': details
        })
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Ejecuta todos los tests"""
        logger.info("="*60)
        logger.info("🧪 Ejecutando Tests del Sistema")
        logger.info("="*60)
        
        self.test_imports()
        self.test_ffmpeg()
        self.test_directories()
        self.test_downloader()
        self.test_script_generator()
        self.test_editor()
        self.test_analytics()
        self.test_templates()
        self.test_queue_manager()
        
        total = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total * 100) if total > 0 else 0
        
        summary = {
            'total': total,
            'passed': self.tests_passed,
            'failed': self.tests_failed,
            'success_rate': round(success_rate, 2),
            'results': self.results
        }
        
        logger.info("="*60)
        logger.info(f"✅ Tests pasados: {self.tests_passed}/{total}")
        logger.info(f"❌ Tests fallidos: {self.tests_failed}/{total}")
        logger.info(f"📊 Tasa de éxito: {success_rate:.1f}%")
        logger.info("="*60)
        
        return summary


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Tests del sistema TikTok Auto Edit')
    parser.add_argument('-j', '--json', action='store_true', help='Salida en JSON')
    parser.add_argument('-v', '--verbose', action='store_true', help='Modo verbose')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tester = SystemTester()
    summary = tester.run_all_tests()
    
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    # Exit code basado en resultados
    sys.exit(0 if summary['failed'] == 0 else 1)


if __name__ == '__main__':
    main()

