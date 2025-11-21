"""
Validación y Sanitización Mejorada para Troubleshooting
Módulo de validación robusta para todos los inputs
"""

import re
import html
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Excepción para errores de validación"""
    pass


class TroubleshootingValidator:
    """Validador completo para inputs del sistema de troubleshooting"""
    
    # Patrones de validación
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    SESSION_ID_PATTERN = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$')
    TICKET_ID_PATTERN = re.compile(r'^TKT-[A-Z0-9-]+$')
    URL_PATTERN = re.compile(r'^https?://[^\s/$.?#].[^\s]*$')
    
    # Límites
    MAX_DESCRIPTION_LENGTH = 5000
    MAX_FEEDBACK_LENGTH = 2000
    MAX_NOTES_LENGTH = 1000
    MIN_DESCRIPTION_LENGTH = 10
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_email(self, email: str) -> Tuple[bool, Optional[str]]:
        """Valida formato de email"""
        if not email:
            return False, "Email es requerido"
        
        email = email.strip().lower()
        
        if len(email) > 254:  # RFC 5321
            return False, "Email demasiado largo (máximo 254 caracteres)"
        
        if not self.EMAIL_PATTERN.match(email):
            return False, "Formato de email inválido"
        
        # Verificar dominios comunes inválidos
        invalid_domains = ['example.com', 'test.com', 'invalid.com']
        domain = email.split('@')[1] if '@' in email else ''
        if domain in invalid_domains:
            self.warnings.append(f"Email usa dominio de prueba: {domain}")
        
        return True, None
    
    def validate_problem_description(self, description: str) -> Tuple[bool, Optional[str]]:
        """Valida descripción del problema"""
        if not description:
            return False, "Descripción del problema es requerida"
        
        description = description.strip()
        
        if len(description) < self.MIN_DESCRIPTION_LENGTH:
            return False, f"Descripción muy corta (mínimo {self.MIN_DESCRIPTION_LENGTH} caracteres)"
        
        if len(description) > self.MAX_DESCRIPTION_LENGTH:
            return False, f"Descripción muy larga (máximo {self.MAX_DESCRIPTION_LENGTH} caracteres)"
        
        # Detectar posibles spam o contenido inapropiado
        spam_keywords = ['buy now', 'click here', 'free money', 'urgent!!!']
        description_lower = description.lower()
        for keyword in spam_keywords:
            if keyword in description_lower:
                self.warnings.append(f"Posible spam detectado: {keyword}")
        
        return True, None
    
    def validate_session_id(self, session_id: str) -> Tuple[bool, Optional[str]]:
        """Valida formato de session ID"""
        if not session_id:
            return False, "Session ID es requerido"
        
        # Aceptar UUID o formato custom
        if not (self.SESSION_ID_PATTERN.match(session_id) or 
                re.match(r'^[a-zA-Z0-9_-]+$', session_id)):
            return False, "Formato de Session ID inválido"
        
        return True, None
    
    def validate_rating(self, rating: int) -> Tuple[bool, Optional[str]]:
        """Valida rating de feedback"""
        if rating is None:
            return False, "Rating es requerido"
        
        if not isinstance(rating, int):
            return False, "Rating debe ser un número entero"
        
        if rating < 1 or rating > 5:
            return False, "Rating debe estar entre 1 y 5"
        
        return True, None
    
    def validate_webhook_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """Valida URL de webhook"""
        if not url:
            return False, "URL es requerida"
        
        if not self.URL_PATTERN.match(url):
            return False, "Formato de URL inválido"
        
        # Verificar que no sea localhost en producción
        if 'localhost' in url or '127.0.0.1' in url:
            self.warnings.append("URL apunta a localhost (no accesible desde internet)")
        
        return True, None
    
    def sanitize_text(self, text: str, max_length: Optional[int] = None) -> str:
        """Sanitiza texto de entrada"""
        if not text:
            return ""
        
        # Remover caracteres de control
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Escapar HTML
        text = html.escape(text)
        
        # Truncar si es necesario
        if max_length and len(text) > max_length:
            text = text[:max_length] + "..."
            self.warnings.append(f"Texto truncado a {max_length} caracteres")
        
        return text.strip()
    
    def validate_troubleshooting_request(self, data: Dict) -> Tuple[bool, List[str]]:
        """Valida request completo de troubleshooting"""
        self.errors = []
        self.warnings = []
        
        # Validar email
        email_valid, email_error = self.validate_email(data.get('customer_email', ''))
        if not email_valid:
            self.errors.append(email_error)
        
        # Validar descripción
        desc_valid, desc_error = self.validate_problem_description(
            data.get('problem_description', '')
        )
        if not desc_valid:
            self.errors.append(desc_error)
        
        # Validar ticket_id si existe
        ticket_id = data.get('ticket_id')
        if ticket_id and not self.TICKET_ID_PATTERN.match(ticket_id):
            self.warnings.append(f"Formato de ticket_id inusual: {ticket_id}")
        
        return len(self.errors) == 0, self.errors
    
    def validate_step_completion(self, data: Dict) -> Tuple[bool, List[str]]:
        """Valida request de completar paso"""
        self.errors = []
        self.warnings = []
        
        # Validar session_id
        session_valid, session_error = self.validate_session_id(
            data.get('session_id', '')
        )
        if not session_valid:
            self.errors.append(session_error)
        
        # Validar success
        success = data.get('success')
        if success is None:
            self.errors.append("Campo 'success' es requerido")
        elif not isinstance(success, bool):
            self.errors.append("Campo 'success' debe ser booleano")
        
        # Validar notes si existe
        notes = data.get('notes')
        if notes:
            notes = self.sanitize_text(notes, self.MAX_NOTES_LENGTH)
            if len(notes) > self.MAX_NOTES_LENGTH:
                self.errors.append(f"Notes demasiado largas (máximo {self.MAX_NOTES_LENGTH} caracteres)")
        
        return len(self.errors) == 0, self.errors
    
    def validate_feedback(self, data: Dict) -> Tuple[bool, List[str]]:
        """Valida request de feedback"""
        self.errors = []
        self.warnings = []
        
        # Validar rating
        rating_valid, rating_error = self.validate_rating(data.get('rating'))
        if not rating_valid:
            self.errors.append(rating_error)
        
        # Validar feedback_text si existe
        feedback_text = data.get('feedback_text')
        if feedback_text:
            feedback_text = self.sanitize_text(feedback_text, self.MAX_FEEDBACK_LENGTH)
            if len(feedback_text) > self.MAX_FEEDBACK_LENGTH:
                self.errors.append(
                    f"Feedback text demasiado largo (máximo {self.MAX_FEEDBACK_LENGTH} caracteres)"
                )
        
        return len(self.errors) == 0, self.errors
    
    def get_validation_summary(self) -> Dict:
        """Obtiene resumen de validación"""
        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }



