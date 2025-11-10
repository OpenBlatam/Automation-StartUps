#!/usr/bin/env python3
"""
Configuración Centralizada para Chatbots
Permite configurar todos los chatbots desde un solo archivo
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class ChatbotConfig:
    """Configuración para un chatbot"""
    # Configuración básica
    enable_logging: bool = True
    persist_conversations: bool = True
    conversation_dir: str = "chatbot_conversations"
    
    # Funcionalidades avanzadas
    enable_rate_limiting: bool = True
    enable_feedback: bool = True
    
    # Rate limiting
    rate_limit_max_requests: int = 60
    rate_limit_time_window: int = 60  # segundos
    rate_limit_block_duration: int = 300  # segundos
    
    # Cache
    cache_enabled: bool = True
    cache_max_size: int = 100
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Seguridad
    max_message_length: int = 2000
    enable_security_validation: bool = True
    
    # Métricas
    enable_metrics: bool = True
    metrics_export_dir: str = "."
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ChatbotConfig':
        """Crea configuración desde un diccionario"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario"""
        return asdict(self)
    
    @classmethod
    def from_env(cls) -> 'ChatbotConfig':
        """Crea configuración desde variables de entorno"""
        return cls(
            enable_logging=os.getenv('CHATBOT_ENABLE_LOGGING', 'true').lower() == 'true',
            persist_conversations=os.getenv('CHATBOT_PERSIST_CONVERSATIONS', 'true').lower() == 'true',
            conversation_dir=os.getenv('CHATBOT_CONVERSATION_DIR', 'chatbot_conversations'),
            enable_rate_limiting=os.getenv('CHATBOT_ENABLE_RATE_LIMITING', 'true').lower() == 'true',
            enable_feedback=os.getenv('CHATBOT_ENABLE_FEEDBACK', 'true').lower() == 'true',
            rate_limit_max_requests=int(os.getenv('CHATBOT_RATE_LIMIT_MAX', '60')),
            rate_limit_time_window=int(os.getenv('CHATBOT_RATE_LIMIT_WINDOW', '60')),
            cache_enabled=os.getenv('CHATBOT_CACHE_ENABLED', 'true').lower() == 'true',
            cache_max_size=int(os.getenv('CHATBOT_CACHE_SIZE', '100')),
            log_level=os.getenv('CHATBOT_LOG_LEVEL', 'INFO'),
            max_message_length=int(os.getenv('CHATBOT_MAX_MESSAGE_LENGTH', '2000')),
        )


class ConfigManager:
    """Gestor de configuración para chatbots"""
    
    def __init__(self, config_file: str = "chatbot_config.json"):
        self.config_file = Path(config_file)
        self.configs: Dict[str, ChatbotConfig] = {}
        self._load_config()
    
    def _load_config(self):
        """Carga configuración desde archivo o crea una por defecto"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.configs = {
                        name: ChatbotConfig.from_dict(config_data)
                        for name, config_data in data.get('chatbots', {}).items()
                    }
            except Exception:
                self._create_default_config()
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """Crea configuración por defecto"""
        default_config = ChatbotConfig()
        self.configs = {
            "curso_ia": default_config,
            "saas_marketing": default_config,
            "ia_bulk": default_config
        }
        self.save_config()
    
    def get_config(self, chatbot_name: str) -> ChatbotConfig:
        """Obtiene configuración para un chatbot"""
        # Primero intentar desde archivo
        if chatbot_name in self.configs:
            return self.configs[chatbot_name]
        
        # Luego desde variables de entorno
        env_config = ChatbotConfig.from_env()
        
        # Finalmente, configuración por defecto
        return env_config or ChatbotConfig()
    
    def set_config(self, chatbot_name: str, config: ChatbotConfig):
        """Establece configuración para un chatbot"""
        self.configs[chatbot_name] = config
        self.save_config()
    
    def save_config(self):
        """Guarda configuración a archivo"""
        data = {
            "version": "1.0",
            "chatbots": {
                name: config.to_dict()
                for name, config in self.configs.items()
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def update_config(self, chatbot_name: str, **kwargs):
        """Actualiza configuración parcialmente"""
        config = self.get_config(chatbot_name)
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        self.set_config(chatbot_name, config)


# Instancia global del gestor de configuración
config_manager = ConfigManager()


def get_chatbot_config(chatbot_name: str) -> ChatbotConfig:
    """Función helper para obtener configuración"""
    return config_manager.get_config(chatbot_name)






