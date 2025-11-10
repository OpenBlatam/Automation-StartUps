"""
Módulo de Análisis y Ajuste de Precios

Analiza precios actuales vs mercado y calcula ajustes estratégicos
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import statistics

from price_config import PriceConfig
from price_history import PriceHistory

logger = logging.getLogger(__name__)


class PriceAnalyzer:
    """Analiza precios y calcula ajustes estratégicos"""
    
    def __init__(self, config: PriceConfig, history: Optional[PriceHistory] = None):
        self.config = config
        self.strategy = config.get('pricing_strategy', 'competitive')
        self.history = history
    
    def calculate_price_adjustments(
        self,
        current_prices: List[Dict],
        competitor_prices: List[Dict]
    ) -> List[Dict]:
        """
        Calcula ajustes de precios basados en análisis de mercado
        
        Args:
            current_prices: Lista de precios actuales del catálogo
            competitor_prices: Lista de precios de competencia
        
        Returns:
            Lista de ajustes recomendados para cada producto
        """
        adjustments = []
        
        # Crear diccionario de precios de competencia para búsqueda rápida
        competitor_dict = {}
        for comp_price in competitor_prices:
            product_name = comp_price.get('product_name', '').lower().strip()
            competitor_dict[product_name] = comp_price
        
        # Analizar cada producto del catálogo actual
        for current_product in current_prices:
            product_name = current_product.get('product_name', '').lower().strip()
            current_price = current_product.get('current_price', 0)
            product_id = current_product.get('product_id')
            
            if not product_name or current_price <= 0:
                continue
            
            # Buscar precios de competencia para este producto
            competitor_data = competitor_dict.get(product_name)
            
            if not competitor_data:
                # Si no hay datos de competencia, mantener precio actual
                adjustments.append({
                    'product_id': product_id,
                    'product_name': product_name,
                    'current_price': current_price,
                    'new_price': current_price,
                    'price_change': 0,
                    'price_change_percent': 0,
                    'reason': 'no_competitor_data',
                    'strategy': self.strategy,
                })
                continue
            
            # Calcular nuevo precio según estrategia
            new_price = self._calculate_new_price(
                current_price=current_price,
                competitor_data=competitor_data,
                product_data=current_product
            )
            
            price_change = new_price - current_price
            price_change_percent = (price_change / current_price * 100) if current_price > 0 else 0
            
            adjustments.append({
                'product_id': product_id,
                'product_name': product_name,
                'current_price': current_price,
                'new_price': new_price,
                'price_change': price_change,
                'price_change_percent': price_change_percent,
                'competitor_avg': competitor_data.get('avg_competitor_price'),
                'competitor_min': competitor_data.get('min_competitor_price'),
                'competitor_max': competitor_data.get('max_competitor_price'),
                'reason': self._get_adjustment_reason(current_price, new_price, competitor_data),
                'strategy': self.strategy,
                'calculated_at': datetime.now().isoformat(),
            })
        
        logger.info(f"Calculados {len(adjustments)} ajustes de precio")
        return adjustments
    
    def _calculate_new_price(
        self,
        current_price: float,
        competitor_data: Dict,
        product_data: Dict
    ) -> float:
        """
        Calcula el nuevo precio según la estrategia configurada
        """
        avg_competitor = competitor_data.get('avg_competitor_price', 0)
        min_competitor = competitor_data.get('min_competitor_price', 0)
        max_competitor = competitor_data.get('max_competitor_price', 0)
        
        if avg_competitor <= 0:
            return current_price
        
        # Estrategia: Competitivo (mismo precio que promedio de competencia)
        if self.strategy == 'competitive':
            new_price = avg_competitor
        
        # Estrategia: Líder (más barato que competencia)
        elif self.strategy == 'price_leader':
            margin = self.config.get('price_leader_margin', 0.05)  # 5% más barato
            new_price = avg_competitor * (1 - margin)
        
        # Estrategia: Premium (más caro que competencia)
        elif self.strategy == 'premium':
            margin = self.config.get('premium_margin', 0.10)  # 10% más caro
            new_price = avg_competitor * (1 + margin)
        
        # Estrategia: Dinámico (ajusta según posición)
        elif self.strategy == 'dynamic':
            if current_price > max_competitor:
                # Muy caro, reducir hacia promedio
                new_price = (current_price + avg_competitor) / 2
            elif current_price < min_competitor:
                # Muy barato, aumentar hacia promedio
                new_price = (current_price + avg_competitor) / 2
            else:
                # En rango, ajustar sutilmente hacia promedio
                adjustment_factor = self.config.get('dynamic_adjustment_factor', 0.1)
                new_price = current_price + (avg_competitor - current_price) * adjustment_factor
        
        # Estrategia: Mínimo (siempre el más barato)
        elif self.strategy == 'minimum':
            new_price = min_competitor * 0.99  # 1% más barato que el mínimo
        
        # Estrategia: Personalizada
        elif self.strategy == 'custom':
            new_price = self._calculate_custom_price(
                current_price, competitor_data, product_data
            )
        
        else:
            # Por defecto, mantener precio actual
            new_price = current_price
        
        # Aplicar límites de cambio
        new_price = self._apply_price_limits(current_price, new_price)
        
        # Redondear según configuración
        rounding = self.config.get('price_rounding', 'cent')
        new_price = self._round_price(new_price, rounding)
        
        return new_price
    
    def _calculate_custom_price(
        self,
        current_price: float,
        competitor_data: Dict,
        product_data: Dict
    ) -> float:
        """Calcula precio usando lógica personalizada"""
        # Implementar lógica personalizada según necesidades
        # Por ejemplo, considerar margen de ganancia, costos, etc.
        avg_competitor = competitor_data.get('avg_competitor_price', 0)
        
        # Ejemplo: mantener margen mínimo del 20%
        cost = product_data.get('cost', 0)
        min_margin = self.config.get('min_margin', 0.20)
        
        if cost > 0:
            min_price = cost * (1 + min_margin)
            return max(min_price, avg_competitor * 0.95)  # 5% más barato o margen mínimo
        
        return avg_competitor
    
    def _apply_price_limits(self, current_price: float, new_price: float) -> float:
        """Aplica límites de cambio de precio"""
        max_change_percent = self.config.get('max_price_change_percent', 20)  # 20% máximo
        min_price = self.config.get('min_price', 0)
        max_price = self.config.get('max_price', float('inf'))
        
        # Limitar cambio máximo
        max_change = current_price * (max_change_percent / 100)
        if abs(new_price - current_price) > max_change:
            if new_price > current_price:
                new_price = current_price + max_change
            else:
                new_price = current_price - max_change
        
        # Aplicar límites absolutos
        new_price = max(min_price, min(max_price, new_price))
        
        return new_price
    
    def _round_price(self, price: float, rounding: str) -> float:
        """Redondea el precio según configuración"""
        if rounding == 'cent':
            # Redondear a centavos
            return round(price, 2)
        elif rounding == 'dollar':
            # Redondear a dólares
            return round(price)
        elif rounding == 'five_cents':
            # Redondear a múltiplos de 5 centavos
            return round(price * 20) / 20
        elif rounding == 'ten_cents':
            # Redondear a múltiplos de 10 centavos
            return round(price * 10) / 10
        else:
            return round(price, 2)
    
    def _get_adjustment_reason(
        self,
        current_price: float,
        new_price: float,
        competitor_data: Dict
    ) -> str:
        """Genera razón del ajuste"""
        if new_price == current_price:
            return 'no_change_needed'
        
        avg_competitor = competitor_data.get('avg_competitor_price', 0)
        
        if new_price > current_price:
            if current_price < avg_competitor:
                return 'below_market_increase'
            else:
                return 'strategy_increase'
        else:
            if current_price > avg_competitor:
                return 'above_market_decrease'
            else:
                return 'strategy_decrease'
    
    def validate_adjustments(self, adjustments: List[Dict]) -> List[Dict]:
        """
        Valida los ajustes antes de aplicarlos
        
        Args:
            adjustments: Lista de ajustes calculados
        
        Returns:
            Lista de ajustes validados
        """
        validated = []
        
        for adjustment in adjustments:
            # Validaciones básicas
            if not adjustment.get('product_id'):
                logger.warning(f"Ajuste sin product_id, omitiendo: {adjustment.get('product_name')}")
                continue
            
            if adjustment.get('new_price', 0) <= 0:
                logger.warning(f"Precio nuevo inválido para {adjustment.get('product_name')}")
                continue
            
            # Validar cambios extremos
            change_percent = abs(adjustment.get('price_change_percent', 0))
            max_allowed_change = self.config.get('max_price_change_percent', 20)
            
            if change_percent > max_allowed_change:
                logger.warning(
                    f"Cambio de precio muy grande ({change_percent:.2f}%) para "
                    f"{adjustment.get('product_name')}. Limitando a {max_allowed_change}%"
                )
                current_price = adjustment.get('current_price', 0)
                if adjustment.get('price_change', 0) > 0:
                    adjustment['new_price'] = current_price * (1 + max_allowed_change / 100)
                else:
                    adjustment['new_price'] = current_price * (1 - max_allowed_change / 100)
                adjustment['price_change'] = adjustment['new_price'] - current_price
                adjustment['price_change_percent'] = max_allowed_change if adjustment.get('price_change', 0) > 0 else -max_allowed_change
            
            validated.append(adjustment)
            
            # Registrar en historial si está disponible
            if self.history and adjustment.get('price_change', 0) != 0:
                try:
                    self.history.record_price_change(
                        product_id=str(adjustment.get('product_id', '')),
                        product_name=adjustment.get('product_name', ''),
                        old_price=adjustment.get('current_price', 0),
                        new_price=adjustment.get('new_price', 0),
                        change_percent=adjustment.get('price_change_percent', 0),
                        reason=adjustment.get('reason', 'unknown'),
                        execution_date=datetime.now()
                    )
                except Exception as e:
                    logger.warning(f"Error registrando en historial: {e}")
        
        logger.info(f"Validados {len(validated)} de {len(adjustments)} ajustes")
        return validated
    
    def generate_analysis_report(self, adjustments: List[Dict]) -> Dict:
        """Genera reporte de análisis de precios"""
        if not adjustments:
            return {}
        
        total_products = len(adjustments)
        products_with_changes = sum(1 for a in adjustments if a.get('price_change', 0) != 0)
        price_changes = [a.get('price_change_percent', 0) for a in adjustments]
        
        avg_change = statistics.mean(price_changes) if price_changes else 0
        median_change = statistics.median(price_changes) if price_changes else 0
        
        increases = sum(1 for a in adjustments if a.get('price_change', 0) > 0)
        decreases = sum(1 for a in adjustments if a.get('price_change', 0) < 0)
        
        report = {
            'total_products': total_products,
            'products_with_changes': products_with_changes,
            'products_unchanged': total_products - products_with_changes,
            'price_increases': increases,
            'price_decreases': decreases,
            'avg_price_change_percent': avg_change,
            'median_price_change_percent': median_change,
            'strategy': self.strategy,
            'generated_at': datetime.now().isoformat(),
        }
        
        return report





