#!/usr/bin/env python3
"""
Monitor continuo del sistema TikTok Auto Edit
Monitorea servicios, métricas y envía alertas
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemMonitor:
    """Monitor continuo del sistema"""
    
    def __init__(self, check_interval: int = 60):
        """
        Inicializa el monitor
        
        Args:
            check_interval: Intervalo de verificación en segundos
        """
        self.check_interval = check_interval
        self.services = {
            'api': os.getenv('TIKTOK_API_URL', 'http://localhost:5000'),
            'webhook': os.getenv('TIKTOK_WEBHOOK_URL', 'http://localhost:5001'),
            'dashboard': os.getenv('TIKTOK_DASHBOARD_URL', 'http://localhost:5002')
        }
        self.alerts_sent = set()
    
    def check_service_health(self, name: str, url: str) -> Dict[str, Any]:
        """
        Verifica salud de un servicio
        
        Args:
            name: Nombre del servicio
            url: URL del servicio
            
        Returns:
            Estado del servicio
        """
        try:
            health_url = f"{url}/health" if '/health' not in url else url
            response = requests.get(health_url, timeout=5)
            
            if response.status_code == 200:
                return {
                    'name': name,
                    'status': 'healthy',
                    'url': url,
                    'response_time': response.elapsed.total_seconds(),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'name': name,
                    'status': 'unhealthy',
                    'url': url,
                    'error': f"HTTP {response.status_code}",
                    'timestamp': datetime.now().isoformat()
                }
        except requests.exceptions.Timeout:
            return {
                'name': name,
                'status': 'timeout',
                'url': url,
                'error': 'Timeout',
                'timestamp': datetime.now().isoformat()
            }
        except requests.exceptions.ConnectionError:
            return {
                'name': name,
                'status': 'down',
                'url': url,
                'error': 'Connection refused',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'name': name,
                'status': 'error',
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_all_services(self) -> List[Dict[str, Any]]:
        """Verifica todos los servicios"""
        results = []
        
        for name, url in self.services.items():
            result = self.check_service_health(name, url)
            results.append(result)
            
            if result['status'] != 'healthy':
                logger.warning(f"⚠️  {name}: {result['status']} - {result.get('error', '')}")
            else:
                logger.info(f"✅ {name}: {result['status']} ({result.get('response_time', 0):.2f}s)")
        
        return results
    
    def check_queue_status(self) -> Dict[str, Any]:
        """Verifica estado de la cola"""
        try:
            from tiktok_queue_manager import TikTokQueueManager
            manager = TikTokQueueManager()
            stats = manager.get_queue_stats()
            
            # Alertar si hay muchos pendientes
            if stats.get('pending', 0) > 20:
                alert_key = 'queue_pending_high'
                if alert_key not in self.alerts_sent:
                    logger.warning(f"⚠️  Cola con muchos trabajos pendientes: {stats['pending']}")
                    self.alerts_sent.add(alert_key)
            
            return {
                'status': 'ok',
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_disk_space(self) -> Dict[str, Any]:
        """Verifica espacio en disco"""
        import shutil
        
        total, used, free = shutil.disk_usage('/')
        free_gb = free / (1024**3)
        usage_percent = (used / total) * 100
        
        status = 'ok'
        if free_gb < 5:
            status = 'critical'
        elif free_gb < 10:
            status = 'warning'
        
        return {
            'status': status,
            'free_gb': round(free_gb, 2),
            'usage_percent': round(usage_percent, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def run_monitoring_loop(self):
        """Ejecuta loop de monitoreo continuo"""
        logger.info("="*60)
        logger.info("🔍 Iniciando monitor del sistema")
        logger.info(f"Intervalo de verificación: {self.check_interval}s")
        logger.info("="*60)
        
        try:
            while True:
                logger.info(f"\n📊 Verificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Verificar servicios
                services_status = self.check_all_services()
                
                # Verificar cola
                queue_status = self.check_queue_status()
                
                # Verificar disco
                disk_status = self.check_disk_space()
                
                # Resumen
                healthy_services = sum(1 for s in services_status if s['status'] == 'healthy')
                total_services = len(services_status)
                
                logger.info(f"\n📈 Resumen:")
                logger.info(f"  Servicios: {healthy_services}/{total_services} saludables")
                logger.info(f"  Cola: {queue_status.get('stats', {}).get('pending', 0)} pendientes")
                logger.info(f"  Disco: {disk_status['free_gb']} GB libres ({disk_status['usage_percent']}% usado)")
                
                # Esperar antes de siguiente verificación
                time.sleep(self.check_interval)
        
        except KeyboardInterrupt:
            logger.info("\n🛑 Monitor detenido por usuario")
        except Exception as e:
            logger.error(f"Error en monitor: {e}", exc_info=True)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor continuo del sistema')
    parser.add_argument('-i', '--interval', type=int, default=60,
                       help='Intervalo de verificación en segundos (default: 60)')
    parser.add_argument('-j', '--json', action='store_true',
                       help='Una verificación en JSON y salir')
    
    args = parser.parse_args()
    
    monitor = SystemMonitor(check_interval=args.interval)
    
    if args.json:
        # Una verificación y salir
        services = monitor.check_all_services()
        queue = monitor.check_queue_status()
        disk = monitor.check_disk_space()
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'services': services,
            'queue': queue,
            'disk': disk
        }
        
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # Loop continuo
        monitor.run_monitoring_loop()


if __name__ == '__main__':
    main()

