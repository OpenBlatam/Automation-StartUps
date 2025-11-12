#!/usr/bin/env python3
"""
Script de Mantenimiento para Chatbots
Limpieza, optimización y mantenimiento automático
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
import sys

# Agregar path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from chatbot_curso_ia_webinars import CursoIAWebinarChatbot
    from chatbot_saas_ia_marketing import SaaSIAMarketingChatbot
    from chatbot_ia_bulk_documentos import IABulkDocumentosChatbot
    CHATBOTS_AVAILABLE = True
except ImportError:
    CHATBOTS_AVAILABLE = False
    print("⚠️  Chatbots no disponibles")


class ChatbotMaintenance:
    """Gestor de mantenimiento para chatbots"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.conversation_dir = self.base_dir / "chatbot_conversations"
        self.logs_dir = self.base_dir / "logs"
        self.exports_dir = self.base_dir / "exports"
    
    def cleanup_old_conversations(self, days: int = 30) -> int:
        """
        Limpia conversaciones antiguas.
        
        Args:
            days: Días de antigüedad para eliminar
        
        Returns:
            Número de archivos eliminados
        """
        if not self.conversation_dir.exists():
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted = 0
        
        for conv_file in self.conversation_dir.glob("*.json"):
            try:
                with open(conv_file, 'r') as f:
                    data = json.load(f)
                
                created_at = datetime.fromisoformat(data.get('created_at', ''))
                if created_at < cutoff_date:
                    conv_file.unlink()
                    deleted += 1
            except Exception:
                continue
        
        return deleted
    
    def cleanup_old_logs(self, days: int = 7, keep_latest: int = 5) -> int:
        """
        Limpia logs antiguos, manteniendo los más recientes.
        
        Args:
            days: Días de antigüedad
            keep_latest: Número de logs más recientes a mantener
        
        Returns:
            Número de archivos eliminados
        """
        if not self.logs_dir.exists():
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted = 0
        
        log_files = sorted(
            self.logs_dir.glob("chatbot_*.log"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        # Mantener los más recientes
        for log_file in log_files[keep_latest:]:
            if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                log_file.unlink()
                deleted += 1
        
        return deleted
    
    def cleanup_old_exports(self, days: int = 90) -> int:
        """Limpia exports antiguos"""
        if not self.exports_dir.exists():
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted = 0
        
        for export_file in self.exports_dir.glob("chatbot_*_metrics_*.*"):
            if datetime.fromtimestamp(export_file.stat().st_mtime) < cutoff_date:
                export_file.unlink()
                deleted += 1
        
        return deleted
    
    def optimize_cache(self, chatbot_instance) -> Dict:
        """
        Optimiza el cache del chatbot.
        
        Returns:
            Dict con estadísticas de optimización
        """
        if not hasattr(chatbot_instance, 'response_cache'):
            return {"error": "Cache no disponible"}
        
        cache_size_before = len(chatbot_instance.response_cache)
        
        # Limpiar cache si está muy lleno
        if cache_size_before > chatbot_instance.cache_max_size * 0.9:
            # Eliminar 20% más antiguos
            to_remove = int(cache_size_before * 0.2)
            keys_to_remove = list(chatbot_instance.response_cache.keys())[:to_remove]
            for key in keys_to_remove:
                del chatbot_instance.response_cache[key]
        
        cache_size_after = len(chatbot_instance.response_cache)
        
        return {
            "cache_size_before": cache_size_before,
            "cache_size_after": cache_size_after,
            "entries_removed": cache_size_before - cache_size_after,
            "optimization_percent": ((cache_size_before - cache_size_after) / cache_size_before * 100) if cache_size_before > 0 else 0
        }
    
    def get_storage_stats(self) -> Dict:
        """Obtiene estadísticas de almacenamiento"""
        stats = {
            "conversations": {
                "count": 0,
                "total_size_mb": 0
            },
            "logs": {
                "count": 0,
                "total_size_mb": 0
            },
            "exports": {
                "count": 0,
                "total_size_mb": 0
            }
        }
        
        # Conversaciones
        if self.conversation_dir.exists():
            conv_files = list(self.conversation_dir.glob("*.json"))
            stats["conversations"]["count"] = len(conv_files)
            stats["conversations"]["total_size_mb"] = sum(
                f.stat().st_size for f in conv_files
            ) / (1024 * 1024)
        
        # Logs
        if self.logs_dir.exists():
            log_files = list(self.logs_dir.glob("*.log"))
            stats["logs"]["count"] = len(log_files)
            stats["logs"]["total_size_mb"] = sum(
                f.stat().st_size for f in log_files
            ) / (1024 * 1024)
        
        # Exports
        if self.exports_dir.exists():
            export_files = list(self.exports_dir.glob("chatbot_*_metrics_*.*"))
            stats["exports"]["count"] = len(export_files)
            stats["exports"]["total_size_mb"] = sum(
                f.stat().st_size for f in export_files
            ) / (1024 * 1024)
        
        stats["total_size_mb"] = (
            stats["conversations"]["total_size_mb"] +
            stats["logs"]["total_size_mb"] +
            stats["exports"]["total_size_mb"]
        )
        
        return stats
    
    def run_full_maintenance(self, conversation_days: int = 30, log_days: int = 7, 
                           export_days: int = 90) -> Dict:
        """
        Ejecuta mantenimiento completo.
        
        Returns:
            Dict con resultados del mantenimiento
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "conversations_deleted": self.cleanup_old_conversations(conversation_days),
            "logs_deleted": self.cleanup_old_logs(log_days),
            "exports_deleted": self.cleanup_old_exports(export_days),
            "storage_stats_after": self.get_storage_stats()
        }
        
        return results


def main():
    """Función principal"""
    print("=" * 60)
    print("🔧 Mantenimiento de Chatbots")
    print("=" * 60)
    print()
    
    maintenance = ChatbotMaintenance()
    
    # Estadísticas antes
    print("📊 Estadísticas de almacenamiento:")
    stats_before = maintenance.get_storage_stats()
    print(f"   • Conversaciones: {stats_before['conversations']['count']} archivos "
          f"({stats_before['conversations']['total_size_mb']:.2f} MB)")
    print(f"   • Logs: {stats_before['logs']['count']} archivos "
          f"({stats_before['logs']['total_size_mb']:.2f} MB)")
    print(f"   • Exports: {stats_before['exports']['count']} archivos "
          f"({stats_before['exports']['total_size_mb']:.2f} MB)")
    print(f"   • Total: {stats_before['total_size_mb']:.2f} MB")
    print()
    
    # Ejecutar mantenimiento
    print("🧹 Ejecutando limpieza...")
    results = maintenance.run_full_maintenance()
    
    print(f"   ✅ Conversaciones eliminadas: {results['conversations_deleted']}")
    print(f"   ✅ Logs eliminados: {results['logs_deleted']}")
    print(f"   ✅ Exports eliminados: {results['exports_deleted']}")
    print()
    
    # Estadísticas después
    print("📊 Estadísticas después de limpieza:")
    stats_after = results['storage_stats_after']
    print(f"   • Total: {stats_after['total_size_mb']:.2f} MB")
    print(f"   • Espacio liberado: {stats_before['total_size_mb'] - stats_after['total_size_mb']:.2f} MB")
    print()
    
    print("✅ Mantenimiento completado")


if __name__ == "__main__":
    main()





