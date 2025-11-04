"""
Sistema de Internacionalización (i18n) Completo.

Soporte multi-idioma completo con localización.
"""
import logging
import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class Locale(Enum):
    """Locales soportados."""
    ES_ES = "es_ES"
    ES_MX = "es_MX"
    ES_AR = "es_AR"
    EN_US = "en_US"
    EN_GB = "en_GB"
    PT_BR = "pt_BR"
    PT_PT = "pt_PT"
    FR_FR = "fr_FR"
    DE_DE = "de_DE"
    IT_IT = "it_IT"


@dataclass
class TranslationString:
    """String traducido."""
    key: str
    locale: str
    translation: str
    context: Optional[str] = None


class I18nManager:
    """Gestor de internacionalización."""
    
    def __init__(self, default_locale: Locale = Locale.ES_ES):
        """
        Inicializa gestor de i18n.
        
        Args:
            default_locale: Locale por defecto
        """
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_default_translations()
    
    def _load_default_translations(self):
        """Carga traducciones por defecto."""
        # Traducciones básicas del sistema
        translations = {
            "es_ES": {
                "ticket.created": "Ticket creado",
                "ticket.resolved": "Ticket resuelto",
                "ticket.assigned": "Ticket asignado",
                "ticket.escalated": "Ticket escalado",
                "priority.critical": "Crítico",
                "priority.urgent": "Urgente",
                "priority.high": "Alto",
                "priority.normal": "Normal",
                "priority.low": "Bajo",
                "status.open": "Abierto",
                "status.assigned": "Asignado",
                "status.in_progress": "En progreso",
                "status.resolved": "Resuelto",
                "status.closed": "Cerrado",
                "email.ticket_resolved.subject": "Tu ticket ha sido resuelto",
                "email.ticket_resolved.body": "Hola {customer_name}, tu ticket #{ticket_id} ha sido resuelto.",
                "notification.new_ticket": "Nuevo ticket: {subject}",
                "dashboard.title": "Dashboard de Soporte",
                "dashboard.tickets_open": "Tickets Abiertos",
                "dashboard.satisfaction": "Satisfacción",
                "chatbot.greeting": "Hola, ¿en qué puedo ayudarte?",
                "chatbot.no_answer": "No encontré una respuesta específica. ¿Puedes proporcionar más detalles?",
                "chatbot.resolved": "Parece que tu consulta ha sido resuelta. ¿Hay algo más en lo que pueda ayudarte?"
            },
            "en_US": {
                "ticket.created": "Ticket created",
                "ticket.resolved": "Ticket resolved",
                "ticket.assigned": "Ticket assigned",
                "ticket.escalated": "Ticket escalated",
                "priority.critical": "Critical",
                "priority.urgent": "Urgent",
                "priority.high": "High",
                "priority.normal": "Normal",
                "priority.low": "Low",
                "status.open": "Open",
                "status.assigned": "Assigned",
                "status.in_progress": "In Progress",
                "status.resolved": "Resolved",
                "status.closed": "Closed",
                "email.ticket_resolved.subject": "Your ticket has been resolved",
                "email.ticket_resolved.body": "Hello {customer_name}, your ticket #{ticket_id} has been resolved.",
                "notification.new_ticket": "New ticket: {subject}",
                "dashboard.title": "Support Dashboard",
                "dashboard.tickets_open": "Open Tickets",
                "dashboard.satisfaction": "Satisfaction",
                "chatbot.greeting": "Hello, how can I help you?",
                "chatbot.no_answer": "I didn't find a specific answer. Can you provide more details?",
                "chatbot.resolved": "It seems your query has been resolved. Is there anything else I can help you with?"
            },
            "pt_BR": {
                "ticket.created": "Ticket criado",
                "ticket.resolved": "Ticket resolvido",
                "priority.critical": "Crítico",
                "priority.urgent": "Urgente",
                "status.open": "Aberto",
                "status.resolved": "Resolvido",
                "chatbot.greeting": "Olá, como posso ajudá-lo?",
                "dashboard.title": "Painel de Suporte"
            }
        }
        
        self.translations = translations
    
    def translate(
        self,
        key: str,
        locale: Optional[Locale] = None,
        **kwargs
    ) -> str:
        """
        Traduce una clave.
        
        Args:
            key: Clave de traducción
            locale: Locale (usa current si no se proporciona)
            **kwargs: Variables para interpolación
            
        Returns:
            String traducido
        """
        locale_str = (locale or self.current_locale).value
        
        # Obtener traducción
        translation = self.translations.get(locale_str, {}).get(key)
        
        if not translation:
            # Fallback a default locale
            translation = self.translations.get(self.default_locale.value, {}).get(key)
        
        if not translation:
            # Fallback a key
            translation = key
        
        # Interpolar variables
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except KeyError:
                logger.warning(f"Missing variables for translation key {key}")
        
        return translation
    
    def t(self, key: str, **kwargs) -> str:
        """Alias corto para translate."""
        return self.translate(key, **kwargs)
    
    def set_locale(self, locale: Locale):
        """Establece locale actual."""
        self.current_locale = locale
        logger.info(f"Locale set to {locale.value}")
    
    def get_locale(self) -> Locale:
        """Obtiene locale actual."""
        return self.current_locale
    
    def detect_locale_from_request(self, headers: Dict[str, str]) -> Locale:
        """
        Detecta locale desde headers HTTP.
        
        Args:
            headers: Headers HTTP
            
        Returns:
            Locale detectado
        """
        accept_language = headers.get("Accept-Language", "")
        
        # Parsear Accept-Language header
        if "es" in accept_language.lower():
            if "mx" in accept_language.lower():
                return Locale.ES_MX
            elif "ar" in accept_language.lower():
                return Locale.ES_AR
            return Locale.ES_ES
        elif "pt" in accept_language.lower():
            if "br" in accept_language.lower():
                return Locale.PT_BR
            return Locale.PT_PT
        elif "en" in accept_language.lower():
            if "gb" in accept_language.lower():
                return Locale.EN_GB
            return Locale.EN_US
        elif "fr" in accept_language.lower():
            return Locale.FR_FR
        elif "de" in accept_language.lower():
            return Locale.DE_DE
        elif "it" in accept_language.lower():
            return Locale.IT_IT
        
        return self.default_locale
    
    def load_translations_from_file(self, file_path: str, locale: Locale):
        """
        Carga traducciones desde archivo JSON.
        
        Args:
            file_path: Ruta del archivo
            locale: Locale
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                translations = json.load(f)
                self.translations[locale.value] = translations
                logger.info(f"Loaded translations from {file_path} for {locale.value}")
        except Exception as e:
            logger.error(f"Error loading translations: {e}")
    
    def add_translation(self, key: str, translation: str, locale: Locale):
        """Agrega una traducción."""
        if locale.value not in self.translations:
            self.translations[locale.value] = {}
        
        self.translations[locale.value][key] = translation
    
    def get_available_locales(self) -> List[str]:
        """Obtiene lista de locales disponibles."""
        return list(self.translations.keys())
    
    def format_date(self, date: datetime, locale: Optional[Locale] = None) -> str:
        """
        Formatea fecha según locale.
        
        Args:
            date: Fecha a formatear
            locale: Locale (opcional)
            
        Returns:
            Fecha formateada
        """
        locale_str = (locale or self.current_locale).value
        
        # Formatos por locale
        formats = {
            "es_ES": "%d/%m/%Y %H:%M",
            "es_MX": "%d/%m/%Y %H:%M",
            "en_US": "%m/%d/%Y %I:%M %p",
            "en_GB": "%d/%m/%Y %H:%M",
            "pt_BR": "%d/%m/%Y %H:%M"
        }
        
        date_format = formats.get(locale_str, "%Y-%m-%d %H:%M")
        return date.strftime(date_format)
    
    def format_currency(self, amount: float, locale: Optional[Locale] = None) -> str:
        """
        Formatea moneda según locale.
        
        Args:
            amount: Cantidad
            locale: Locale (opcional)
            
        Returns:
            Moneda formateada
        """
        locale_str = (locale or self.current_locale).value
        
        # Símbolos y formatos por locale
        currencies = {
            "es_ES": ("EUR", "€", "{:,.2f} €"),
            "es_MX": ("MXN", "$", "${:,.2f}"),
            "es_AR": ("ARS", "$", "${:,.2f}"),
            "en_US": ("USD", "$", "${:,.2f}"),
            "en_GB": ("GBP", "£", "£{:,.2f}"),
            "pt_BR": ("BRL", "R$", "R$ {:,.2f}")
        }
        
        currency_code, symbol, format_str = currencies.get(locale_str, ("USD", "$", "${:,.2f}"))
        return format_str.format(amount)

