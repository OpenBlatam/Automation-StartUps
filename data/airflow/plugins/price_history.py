"""
Sistema de Historial de Cambios de Precios

Registra y analiza cambios históricos de precios
"""

import logging
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class PriceHistory:
    """Gestiona historial de cambios de precios"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.history_dir = Path(config.get('history_dir', '/tmp/price_history'))
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = config.get('history_retention_days', 90)
    
    def _get_history_file(self, date: datetime) -> Path:
        """Obtiene archivo de historial para una fecha"""
        date_str = date.strftime('%Y-%m-%d')
        return self.history_dir / f"prices_{date_str}.json"
    
    def record_price_change(
        self,
        product_id: str,
        product_name: str,
        old_price: float,
        new_price: float,
        change_percent: float,
        reason: str,
        execution_date: datetime
    ):
        """
        Registra un cambio de precio
        
        Args:
            product_id: ID del producto
            product_name: Nombre del producto
            old_price: Precio anterior
            new_price: Precio nuevo
            change_percent: Porcentaje de cambio
            reason: Razón del cambio
            execution_date: Fecha de ejecución
        """
        try:
            history_file = self._get_history_file(execution_date)
            
            # Cargar historial existente
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = {
                    'date': execution_date.strftime('%Y-%m-%d'),
                    'changes': []
                }
            
            # Agregar cambio
            change_record = {
                'product_id': product_id,
                'product_name': product_name,
                'old_price': old_price,
                'new_price': new_price,
                'change_percent': change_percent,
                'reason': reason,
                'timestamp': execution_date.isoformat(),
            }
            
            history['changes'].append(change_record)
            
            # Guardar
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Cambio de precio registrado: {product_name}")
            
        except Exception as e:
            logger.error(f"Error registrando cambio de precio: {e}")
    
    def get_product_history(
        self,
        product_id: str,
        days: int = 30
    ) -> List[Dict]:
        """
        Obtiene historial de cambios para un producto
        
        Args:
            product_id: ID del producto
            days: Días de historial a obtener
        
        Returns:
            Lista de cambios históricos
        """
        changes = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        current_date = start_date
        while current_date <= end_date:
            history_file = self._get_history_file(current_date)
            
            if history_file.exists():
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                    
                    # Filtrar cambios del producto
                    product_changes = [
                        change for change in history.get('changes', [])
                        if change.get('product_id') == product_id
                    ]
                    changes.extend(product_changes)
                    
                except Exception as e:
                    logger.warning(f"Error leyendo historial {history_file}: {e}")
            
            current_date += timedelta(days=1)
        
        # Ordenar por timestamp
        changes.sort(key=lambda x: x.get('timestamp', ''))
        
        return changes
    
    def get_price_trends(self, days: int = 30) -> Dict:
        """
        Analiza tendencias de precios
        
        Args:
            days: Días a analizar
        
        Returns:
            Diccionario con análisis de tendencias
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        all_changes = []
        current_date = start_date
        
        while current_date <= end_date:
            history_file = self._get_history_file(current_date)
            
            if history_file.exists():
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                    all_changes.extend(history.get('changes', []))
                except Exception as e:
                    logger.warning(f"Error leyendo historial {history_file}: {e}")
            
            current_date += timedelta(days=1)
        
        # Análisis
        total_changes = len(all_changes)
        increases = sum(1 for c in all_changes if c.get('change_percent', 0) > 0)
        decreases = sum(1 for c in all_changes if c.get('change_percent', 0) < 0)
        
        avg_change = (
            sum(c.get('change_percent', 0) for c in all_changes) / total_changes
            if total_changes > 0 else 0
        )
        
        # Cambios por producto
        changes_by_product = defaultdict(list)
        for change in all_changes:
            product_id = change.get('product_id')
            if product_id:
                changes_by_product[product_id].append(change)
        
        most_volatile = sorted(
            changes_by_product.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]
        
        return {
            'period_days': days,
            'total_changes': total_changes,
            'increases': increases,
            'decreases': decreases,
            'avg_change_percent': round(avg_change, 2),
            'most_volatile_products': [
                {
                    'product_id': pid,
                    'change_count': len(changes),
                    'product_name': changes[0].get('product_name') if changes else 'Unknown'
                }
                for pid, changes in most_volatile
            ],
        }
    
    def cleanup_old_history(self):
        """Elimina historial más antiguo que retention_days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            for history_file in self.history_dir.glob("prices_*.json"):
                try:
                    # Extraer fecha del nombre del archivo
                    date_str = history_file.stem.replace('prices_', '')
                    file_date = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    if file_date < cutoff_date:
                        history_file.unlink()
                        logger.info(f"Historial antiguo eliminado: {history_file.name}")
                        
                except Exception as e:
                    logger.warning(f"Error procesando {history_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error limpiando historial: {e}")








