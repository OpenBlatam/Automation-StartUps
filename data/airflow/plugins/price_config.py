"""
Módulo de Configuración de Automatización de Precios

Gestiona la configuración del sistema de automatización de precios
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class PriceConfig:
    """Gestiona configuración del sistema de automatización de precios"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa configuración
        
        Args:
            config_path: Ruta al archivo de configuración (JSON o YAML)
        """
        self.config = {}
        
        if config_path:
            self.load_from_file(config_path)
        else:
            # Cargar desde variable de entorno o usar configuración por defecto
            env_config_path = os.getenv('PRICE_AUTOMATION_CONFIG')
            if env_config_path and os.path.exists(env_config_path):
                self.load_from_file(env_config_path)
            else:
                self._load_default_config()
    
    def load_from_file(self, config_path: str):
        """Carga configuración desde archivo"""
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix.lower() == '.yaml' or path.suffix.lower() == '.yml':
                self.config = yaml.safe_load(f) or {}
            else:
                self.config = json.load(f) or {}
    
    def _load_default_config(self):
        """Carga configuración por defecto"""
        self.config = {
            # Estrategia de precios
            'pricing_strategy': os.getenv('PRICING_STRATEGY', 'competitive'),
            
            # Parámetros de estrategia
            'price_leader_margin': float(os.getenv('PRICE_LEADER_MARGIN', '0.05')),  # 5%
            'premium_margin': float(os.getenv('PREMIUM_MARGIN', '0.10')),  # 10%
            'dynamic_adjustment_factor': float(os.getenv('DYNAMIC_ADJUSTMENT_FACTOR', '0.1')),  # 10%
            'min_margin': float(os.getenv('MIN_MARGIN', '0.20')),  # 20%
            
            # Límites de cambio
            'max_price_change_percent': float(os.getenv('MAX_PRICE_CHANGE_PERCENT', '20')),  # 20%
            'min_price': float(os.getenv('MIN_PRICE', '0')),
            'max_price': float(os.getenv('MAX_PRICE', '999999')),
            
            # Redondeo
            'price_rounding': os.getenv('PRICE_ROUNDING', 'cent'),  # cent, dollar, five_cents, ten_cents
            
            # Fuente de catálogo actual
            'catalog_source': {
                'type': os.getenv('CATALOG_SOURCE_TYPE', 'api'),  # api, database, file
                'url': os.getenv('CATALOG_API_URL', 'http://localhost:8000/api/catalog'),
                'path': os.getenv('CATALOG_FILE_PATH', '/data/catalog.json'),
                'format': os.getenv('CATALOG_FILE_FORMAT', 'json'),  # json, csv, excel
            },
            
            # Fuentes de competencia
            'competitor_apis': [],
            'scraping_sources': [],
            'market_databases': [],
            
            # Configuración de scraping
            'scraping_delay': int(os.getenv('SCRAPING_DELAY', '2')),  # segundos entre requests
            
            # Destino de publicación
            'publish_target': {
                'type': os.getenv('PUBLISH_TARGET_TYPE', 'api'),  # api, database, file, multiple
                'url': os.getenv('PUBLISH_API_URL', 'http://localhost:8000/api/catalog/update'),
                'method': os.getenv('PUBLISH_API_METHOD', 'POST'),
                'data_format': os.getenv('PUBLISH_DATA_FORMAT', 'full_catalog'),  # full_catalog, products_only, price_updates_only
                'path': os.getenv('PUBLISH_FILE_PATH', '/data/catalog_updated.json'),
            },
            
            # Auditoría
            'audit_log_file': os.getenv('AUDIT_LOG_FILE', '/tmp/price_automation_audit.log'),
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene valor de configuración"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """Establece valor de configuración"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def add_competitor_api(self, api_config: Dict):
        """Agrega configuración de API de competidor"""
        if 'competitor_apis' not in self.config:
            self.config['competitor_apis'] = []
        
        self.config['competitor_apis'].append(api_config)
    
    def add_scraping_source(self, source_config: Dict):
        """Agrega configuración de fuente de scraping"""
        if 'scraping_sources' not in self.config:
            self.config['scraping_sources'] = []
        
        self.config['scraping_sources'].append(source_config)
    
    def add_market_database(self, db_config: Dict):
        """Agrega configuración de base de datos de mercado"""
        if 'market_databases' not in self.config:
            self.config['market_databases'] = []
        
        self.config['market_databases'].append(db_config)
    
    def save_to_file(self, config_path: str):
        """Guarda configuración a archivo"""
        path = Path(config_path)
        
        with open(path, 'w', encoding='utf-8') as f:
            if path.suffix.lower() == '.yaml' or path.suffix.lower() == '.yml':
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            else:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def to_dict(self) -> Dict:
        """Retorna configuración como diccionario"""
        return self.config.copy()













