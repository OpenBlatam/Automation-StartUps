#!/usr/bin/env python3
"""
Monitor Continuo de Salud del Sistema
Ejecuta verificaciones continuas y notifica cuando detecta problemas
"""
import time
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def run_health_check():
    """Ejecuta health check rápido"""
    script_dir = Path(__file__).parent
    quick_status = script_dir / 'quick_status.py'
    
    if quick_status.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(quick_status)],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout
        except:
            return False, None
    return False, None

def check_alerts():
    """Verifica alertas del sistema"""
    script_dir = Path(__file__).parent
    check_alerts = script_dir / 'check_alerts.py'
    
    if check_alerts.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(check_alerts)],
                capture_output=True,
                text=True,
                timeout=60
            )
            # Exit code 0 = OK, 1 = warnings, 2 = critical
            return result.returncode, result.stdout
        except:
            return 2, None
    return 2, None

def monitor_loop(interval_seconds=300, max_iterations=None):
    """Loop de monitoreo continuo"""
    print("=" * 80)
    print("🔍 Monitor Continuo de Salud")
    print("=" * 80)
    print()
    print(f"⏱️  Intervalo: {interval_seconds}s ({interval_seconds/60:.1f} minutos)")
    if max_iterations:
        print(f"🔄 Iteraciones máximas: {max_iterations}")
    print()
    print("💡 Presiona Ctrl+C para detener")
    print()
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"[{timestamp}] Iteración {iteration}")
            print("-" * 80)
            
            # Health check rápido
            health_ok, health_output = run_health_check()
            if health_ok and health_output:
                print(f"✅ Health: {health_output.strip()}")
            else:
                print("⚠️  Health check falló")
            
            # Verificar alertas
            alerts_code, alerts_output = check_alerts()
            if alerts_code == 0:
                print("✅ Sin alertas críticas")
            elif alerts_code == 1:
                print("🟡 Alertas de alta prioridad detectadas")
                if alerts_output:
                    lines = alerts_output.split('\n')[:3]
                    for line in lines:
                        if line.strip():
                            print(f"   {line}")
            elif alerts_code == 2:
                print("🔴 Alertas críticas detectadas")
                if alerts_output:
                    lines = alerts_output.split('\n')[:5]
                    for line in lines:
                        if line.strip():
                            print(f"   {line}")
                print()
                print("⚠️  ACCIÓN REQUERIDA: Revisar alertas críticas")
            
            print()
            
            if max_iterations and iteration >= max_iterations:
                print(f"✅ Completadas {max_iterations} iteraciones")
                break
            
            # Esperar antes de siguiente iteración
            if max_iterations is None or iteration < max_iterations:
                time.sleep(interval_seconds)
    
    except KeyboardInterrupt:
        print()
        print("⏹️  Monitor detenido por usuario")
        print()

def main():
    interval = 300  # 5 minutos por defecto
    max_iterations = None
    
    if '--interval' in sys.argv:
        idx = sys.argv.index('--interval')
        if idx + 1 < len(sys.argv):
            try:
                interval = int(sys.argv[idx + 1])
            except:
                print("⚠️  Intervalo inválido, usando default: 300s")
    
    if '--iterations' in sys.argv:
        idx = sys.argv.index('--iterations')
        if idx + 1 < len(sys.argv):
            try:
                max_iterations = int(sys.argv[idx + 1])
            except:
                pass
    
    monitor_loop(interval, max_iterations)

if __name__ == '__main__':
    main()

