"""
Sistema de Conversión de Monedas para Precios

Soporta múltiples monedas y conversión automática
"""

import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


class CurrencyConverter:
    """Convierte precios entre diferentes monedas"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.base_currency = config.get('base_currency', 'USD')
        self.target_currency = config.get('target_currency', 'USD')
        self.exchange_rates: Dict[str, float] = {}
        self.last_update: Optional[datetime] = None
        self.cache_ttl = config.get('exchange_rate_cache_ttl', 3600)  # 1 hora
        self.api_key = config.get('exchange_rate_api_key')
        self.api_url = config.get(
            'exchange_rate_api_url',
            'https://api.exchangerate-api.com/v4/latest/'
        )
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Obtiene tasa de cambio entre monedas
        
        Args:
            from_currency: Moneda origen
            to_currency: Moneda destino
        
        Returns:
            Tasa de cambio
        """
        if from_currency == to_currency:
            return 1.0
        
        # Verificar si necesitamos actualizar tasas
        if self._should_update_rates():
            self._update_exchange_rates()
        
        # Obtener tasa desde caché
        key = f"{from_currency}_{to_currency}"
        if key in self.exchange_rates:
            return self.exchange_rates[key]
        
        # Calcular tasa indirecta si es necesario
        if from_currency == self.base_currency:
            # Directo desde base
            rate = self.exchange_rates.get(f"{from_currency}_{to_currency}", 1.0)
        elif to_currency == self.base_currency:
            # Inverso
            rate = 1.0 / self.exchange_rates.get(f"{to_currency}_{from_currency}", 1.0)
        else:
            # Indirecto: from -> base -> to
            from_base = self.exchange_rates.get(f"{self.base_currency}_{from_currency}", 1.0)
            base_to = self.exchange_rates.get(f"{self.base_currency}_{to_currency}", 1.0)
            rate = base_to / from_base if from_base != 0 else 1.0
        
        return rate
    
    def convert_price(
        self,
        price: float,
        from_currency: str,
        to_currency: str,
        round_to: int = 2
    ) -> float:
        """
        Convierte un precio entre monedas
        
        Args:
            price: Precio a convertir
            from_currency: Moneda origen
            to_currency: Moneda destino
            round_to: Decimales para redondear
        
        Returns:
            Precio convertido
        """
        if from_currency == to_currency:
            return round(price, round_to)
        
        rate = self.get_exchange_rate(from_currency, to_currency)
        converted = price * rate
        
        # Redondear
        decimal_places = Decimal(10) ** round_to
        rounded = float(
            Decimal(str(converted)).quantize(
                Decimal('0.1') ** round_to,
                rounding=ROUND_HALF_UP
            )
        )
        
        return rounded
    
    def normalize_prices(
        self,
        prices: List[Dict],
        target_currency: Optional[str] = None
    ) -> List[Dict]:
        """
        Normaliza precios a una moneda objetivo
        
        Args:
            prices: Lista de precios con campo 'currency'
            target_currency: Moneda objetivo (None = usar config)
        
        Returns:
            Lista de precios normalizados
        """
        target = target_currency or self.target_currency
        normalized = []
        
        for price_data in prices:
            original_price = price_data.get('price', 0)
            original_currency = price_data.get('currency', self.base_currency)
            
            if original_currency == target:
                normalized_price = original_price
            else:
                normalized_price = self.convert_price(
                    original_price,
                    original_currency,
                    target
                )
            
            normalized_data = price_data.copy()
            normalized_data['price'] = normalized_price
            normalized_data['original_price'] = original_price
            normalized_data['original_currency'] = original_currency
            normalized_data['normalized_currency'] = target
            normalized_data['exchange_rate'] = self.get_exchange_rate(
                original_currency,
                target
            )
            
            normalized.append(normalized_data)
        
        return normalized
    
    def _should_update_rates(self) -> bool:
        """Verifica si se deben actualizar las tasas"""
        if not self.last_update:
            return True
        
        elapsed = (datetime.now() - self.last_update).total_seconds()
        return elapsed > self.cache_ttl
    
    def _update_exchange_rates(self):
        """Actualiza tasas de cambio desde API"""
        try:
            url = f"{self.api_url}{self.base_currency}"
            params = {}
            
            if self.api_key:
                params['access_key'] = self.api_key
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Procesar tasas
            rates = data.get('rates', {})
            for currency, rate in rates.items():
                key = f"{self.base_currency}_{currency}"
                self.exchange_rates[key] = float(rate)
            
            self.last_update = datetime.now()
            logger.info(f"Tasas de cambio actualizadas: {len(self.exchange_rates)} monedas")
            
        except Exception as e:
            logger.warning(f"Error actualizando tasas de cambio: {e}")
            # Usar tasas en caché si están disponibles
            if not self.exchange_rates:
                logger.error("No hay tasas de cambio disponibles")
    
    def get_supported_currencies(self) -> List[str]:
        """Obtiene lista de monedas soportadas"""
        currencies = set([self.base_currency])
        
        for key in self.exchange_rates.keys():
            parts = key.split('_')
            if len(parts) == 2:
                currencies.add(parts[1])
        
        return sorted(list(currencies))








