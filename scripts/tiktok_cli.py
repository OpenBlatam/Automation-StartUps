#!/usr/bin/env python3
"""
CLI interactivo para TikTok Auto Edit
Interfaz de línea de comandos amigable para todas las funcionalidades
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TikTokCLI:
    """CLI interactivo para el sistema"""
    
    def __init__(self):
        """Inicializa el CLI"""
        self.scripts_dir = Path(__file__).parent
    
    def process_single(self, url: str, output_dir: Optional[str] = None):
        """Procesa un solo video"""
        import subprocess
        
        print(f"\n🎬 Procesando video: {url}\n")
        
        # 1. Descargar
        print("📥 Descargando video...")
        cmd = [
            sys.executable,
            str(self.scripts_dir / "tiktok_downloader.py"),
            url,
            "-o", output_dir or "/tmp/tiktok_downloads",
            "-j"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        download_data = json.loads(result.stdout)
        
        if not download_data.get('success'):
            print(f"❌ Error: {download_data.get('message')}")
            return False
        
        video_path = download_data['file_path']
        print(f"✅ Video descargado: {video_path}")
        
        # 2. Generar script
        print("\n🤖 Generando script de edición con IA...")
        cmd = [
            sys.executable,
            str(self.scripts_dir / "video_script_generator.py"),
            video_path,
            "-n", "10",
            "-o", "/tmp/video_script.json"
        ]
        subprocess.run(cmd, capture_output=True)
        print("✅ Script generado")
        
        # 3. Editar
        print("\n🎬 Editando video...")
        cmd = [
            sys.executable,
            str(self.scripts_dir / "video_editor.py"),
            video_path,
            "/tmp/video_script.json",
            "-o", "video_edited.mp4",
            "-d", output_dir or "/tmp/tiktok_edited"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        edit_data = json.loads(result.stdout)
        
        if not edit_data.get('success'):
            print(f"❌ Error: {edit_data.get('message')}")
            return False
        
        print(f"✅ Video editado: {edit_data.get('output_path')}")
        print(f"\n📊 Tamaño: {edit_data.get('file_size', 0) / 1024 / 1024:.2f} MB")
        print(f"⏱️  Duración: {edit_data.get('duration', 0):.2f}s")
        
        return True
    
    def interactive_menu(self):
        """Menú interactivo"""
        while True:
            print("\n" + "="*60)
            print("🎬 TikTok Auto Edit - Menú Principal")
            print("="*60)
            print("1. Procesar video individual")
            print("2. Procesar múltiples videos (batch)")
            print("3. Ver estadísticas")
            print("4. Ver top URLs")
            print("5. Gestionar templates")
            print("6. Optimizar sistema")
            print("7. Health check")
            print("8. Ver cola de trabajos")
            print("9. Salir")
            print("="*60)
            
            choice = input("\nSelecciona una opción: ").strip()
            
            if choice == "1":
                url = input("Ingresa URL de TikTok: ").strip()
                if url:
                    self.process_single(url)
            
            elif choice == "2":
                file_path = input("Ruta al archivo con URLs: ").strip()
                if file_path and os.path.exists(file_path):
                    import subprocess
                    workers = input("Número de workers (default 3): ").strip() or "3"
                    cmd = [
                        sys.executable,
                        str(self.scripts_dir / "tiktok_batch_processor.py"),
                        file_path,
                        "-w", workers
                    ]
                    subprocess.run(cmd)
            
            elif choice == "3":
                days = input("Días a analizar (default 7): ").strip() or "7"
                import subprocess
                cmd = [
                    sys.executable,
                    str(self.scripts_dir / "tiktok_analytics.py"),
                    "stats",
                    "-d", days
                ]
                subprocess.run(cmd)
            
            elif choice == "4":
                limit = input("Límite (default 10): ").strip() or "10"
                import subprocess
                cmd = [
                    sys.executable,
                    str(self.scripts_dir / "tiktok_analytics.py"),
                    "top",
                    "-l", limit
                ]
                subprocess.run(cmd)
            
            elif choice == "5":
                print("\n1. Listar templates")
                print("2. Inicializar templates")
                sub_choice = input("Opción: ").strip()
                import subprocess
                if sub_choice == "1":
                    cmd = [sys.executable, str(self.scripts_dir / "tiktok_templates.py"), "list"]
                else:
                    cmd = [sys.executable, str(self.scripts_dir / "tiktok_templates.py"), "init"]
                subprocess.run(cmd)
            
            elif choice == "6":
                import subprocess
                cmd = [sys.executable, str(self.scripts_dir / "tiktok_optimizer.py"), "analyze"]
                subprocess.run(cmd)
            
            elif choice == "7":
                import subprocess
                cmd = [sys.executable, str(self.scripts_dir / "health_check.py")]
                subprocess.run(cmd)
            
            elif choice == "8":
                import subprocess
                cmd = [sys.executable, str(self.scripts_dir / "tiktok_queue_manager.py"), "stats"]
                subprocess.run(cmd)
            
            elif choice == "9":
                print("\n👋 ¡Hasta luego!")
                break
            
            else:
                print("❌ Opción inválida")


def main():
    parser = argparse.ArgumentParser(description='CLI interactivo para TikTok Auto Edit')
    parser.add_argument('command', nargs='?', choices=['process', 'menu'], default='menu',
                       help='Comando a ejecutar')
    parser.add_argument('-u', '--url', help='URL de TikTok (para process)')
    parser.add_argument('-o', '--output', help='Directorio de salida')
    
    args = parser.parse_args()
    
    cli = TikTokCLI()
    
    if args.command == 'process':
        if not args.url:
            print("Error: URL requerida para procesar")
            sys.exit(1)
        success = cli.process_single(args.url, args.output)
        sys.exit(0 if success else 1)
    
    elif args.command == 'menu':
        cli.interactive_menu()


if __name__ == '__main__':
    main()


