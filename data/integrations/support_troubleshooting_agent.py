"""
Agente de Soporte Técnico Automatizado - Sistema de Troubleshooting
Autor: Sistema de Automatización
Versión: 1.0.0

Este módulo proporciona un agente de soporte técnico que guía a los clientes
paso a paso para resolver problemas comunes, con instrucciones simples,
precauciones y enlaces a recursos. Si el problema no se resuelve, sugiere
escalar el ticket.

Características:
- Guía paso a paso para resolver problemas
- Instrucciones simples y accesibles para no técnicos
- Precauciones y advertencias de seguridad
- Enlaces a recursos y documentación
- Detección automática de problemas
- Sugerencia de escalación si no se resuelve
- Integración con sistema de tickets
"""

import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid

# Importar módulos opcionales
try:
    from .support_troubleshooting_webhooks import TroubleshootingWebhookManager, WebhookEvent
    WEBHOOKS_AVAILABLE = True
except ImportError:
    WEBHOOKS_AVAILABLE = False
    logger.warning("Webhooks module not available")

try:
    from .support_troubleshooting_templates import TroubleshootingTemplateManager
    TEMPLATES_AVAILABLE = True
except ImportError:
    TEMPLATES_AVAILABLE = False
    logger.warning("Templates module not available")

try:
    from .support_troubleshooting_validator import TroubleshootingValidator
    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False
    logger.warning("Validator module not available")

try:
    from .support_troubleshooting_error_handler import TroubleshootingErrorHandler, ErrorSeverity, ErrorCategory
    ERROR_HANDLER_AVAILABLE = True
except ImportError:
    ERROR_HANDLER_AVAILABLE = False
    logger.warning("Error handler module not available")

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProblemCategory(Enum):
    """Categorías de problemas"""
    INSTALLATION = "instalación"
    CONFIGURATION = "configuración"
    CONNECTIVITY = "conectividad"
    PERFORMANCE = "rendimiento"
    ERROR = "error"
    BILLING = "facturación"
    ACCOUNT = "cuenta"
    FEATURE = "funcionalidad"
    SECURITY = "seguridad"
    OTHER = "otro"


class StepStatus(Enum):
    """Estado de un paso de troubleshooting"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TroubleshootingStatus(Enum):
    """Estado del proceso de troubleshooting"""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    NEEDS_ESCALATION = "needs_escalation"
    ESCALATED = "escalated"


@dataclass
class TroubleshootingStep:
    """Un paso individual en el proceso de troubleshooting"""
    step_number: int
    title: str
    description: str
    instructions: List[str]  # Lista de instrucciones paso a paso
    expected_result: str  # Qué debería pasar si funciona
    warnings: List[str] = None  # Precauciones importantes
    resources: List[Dict[str, str]] = None  # Enlaces a recursos
    status: StepStatus = StepStatus.PENDING
    notes: str = ""  # Notas del usuario sobre este paso
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.resources is None:
            self.resources = []


@dataclass
class TroubleshootingGuide:
    """Guía completa de troubleshooting para un problema"""
    problem_id: str
    problem_title: str
    problem_description: str
    category: ProblemCategory
    estimated_time: str  # Tiempo estimado para resolver
    difficulty: str  # "fácil", "medio", "avanzado"
    prerequisites: List[str] = None  # Requisitos previos
    steps: List[TroubleshootingStep] = None
    common_issues: List[str] = None  # Problemas comunes durante el proceso
    escalation_criteria: List[str] = None  # Cuándo escalar
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
        if self.steps is None:
            self.steps = []
        if self.common_issues is None:
            self.common_issues = []
        if self.escalation_criteria is None:
            self.escalation_criteria = []


@dataclass
class TroubleshootingSession:
    """Sesión de troubleshooting en curso"""
    session_id: str
    ticket_id: Optional[str]
    customer_email: str
    customer_name: Optional[str]
    problem_description: str
    detected_problem: Optional[TroubleshootingGuide]
    current_step: int = 0
    status: TroubleshootingStatus = TroubleshootingStatus.STARTED
    started_at: datetime = None
    resolved_at: Optional[datetime] = None
    notes: List[str] = None
    attempted_steps: List[Dict] = None
    
    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.now()
        if self.notes is None:
            self.notes = []
        if self.attempted_steps is None:
            self.attempted_steps = []


class TroubleshootingAgent:
    """
    Agente de soporte técnico que guía a los clientes paso a paso
    para resolver problemas técnicos.
    """
    
    def __init__(self, knowledge_base_path: str = None, use_llm: bool = False, openai_api_key: str = None):
        """
        Inicializa el agente de troubleshooting.
        
        Args:
            knowledge_base_path: Ruta al archivo JSON con la base de conocimiento
            use_llm: Si usar LLM para mejorar detección y respuestas
            openai_api_key: API key de OpenAI (opcional, para LLM)
        """
        if knowledge_base_path is None:
            # Ruta por defecto
            kb_path = Path(__file__).parent / "support_troubleshooting_kb.json"
        else:
            kb_path = Path(knowledge_base_path)
        
        self.knowledge_base_path = kb_path
        self.knowledge_base: Dict[str, TroubleshootingGuide] = {}
        self.active_sessions: Dict[str, TroubleshootingSession] = {}
        self.use_llm = use_llm
        self.openai_api_key = openai_api_key
        
        # Inicializar módulos opcionales
        self.webhook_manager = None
        if WEBHOOKS_AVAILABLE:
            self.webhook_manager = TroubleshootingWebhookManager()
        
        self.template_manager = None
        if TEMPLATES_AVAILABLE:
            self.template_manager = TroubleshootingTemplateManager()
        
        # Inicializar validador y error handler
        self.validator = None
        if VALIDATOR_AVAILABLE:
            self.validator = TroubleshootingValidator()
        
        self.error_handler = None
        if ERROR_HANDLER_AVAILABLE:
            self.error_handler = TroubleshootingErrorHandler()
        
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Carga la base de conocimiento desde el archivo JSON"""
        try:
            if self.knowledge_base_path.exists():
                with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                    kb_data = json.load(f)
                
                for problem_id, problem_data in kb_data.items():
                    guide = self._parse_guide_from_dict(problem_id, problem_data)
                    self.knowledge_base[problem_id] = guide
                
                logger.info(f"Cargada base de conocimiento con {len(self.knowledge_base)} problemas")
            else:
                logger.warning(f"Base de conocimiento no encontrada en {self.knowledge_base_path}")
                # Crear base de conocimiento básica
                self._create_default_knowledge_base()
        except Exception as e:
            logger.error(f"Error cargando base de conocimiento: {e}")
            self._create_default_knowledge_base()
    
    def _parse_guide_from_dict(self, problem_id: str, data: Dict) -> TroubleshootingGuide:
        """Parsea un diccionario a un objeto TroubleshootingGuide"""
        steps = []
        for step_data in data.get("steps", []):
            step = TroubleshootingStep(
                step_number=step_data["step_number"],
                title=step_data["title"],
                description=step_data["description"],
                instructions=step_data["instructions"],
                expected_result=step_data["expected_result"],
                warnings=step_data.get("warnings", []),
                resources=step_data.get("resources", [])
            )
            steps.append(step)
        
        return TroubleshootingGuide(
            problem_id=problem_id,
            problem_title=data["problem_title"],
            problem_description=data["problem_description"],
            category=ProblemCategory(data.get("category", "otro")),
            estimated_time=data.get("estimated_time", "15 minutos"),
            difficulty=data.get("difficulty", "medio"),
            prerequisites=data.get("prerequisites", []),
            steps=steps,
            common_issues=data.get("common_issues", []),
            escalation_criteria=data.get("escalation_criteria", [])
        )
    
    def _create_default_knowledge_base(self):
        """Crea una base de conocimiento básica por defecto"""
        logger.info("Creando base de conocimiento por defecto")
        # Se creará con el archivo JSON
    
    def detect_problem(self, description: str) -> Optional[TroubleshootingGuide]:
        """
        Detecta el problema basándose en la descripción del usuario.
        
        Args:
            description: Descripción del problema por el usuario
            
        Returns:
            TroubleshootingGuide si se detecta un problema conocido, None en caso contrario
        """
        description_lower = description.lower()
        
        # Buscar coincidencias por palabras clave
        best_match = None
        best_score = 0
        
        for problem_id, guide in self.knowledge_base.items():
            score = self._calculate_match_score(description_lower, guide)
            if score > best_score:
                best_score = score
                best_match = guide
        
        # Si hay LLM disponible, intentar mejorar la detección
        if self.use_llm and self.openai_api_key and best_score < 0.5:
            enhanced_match = self._enhance_detection_with_llm(description, best_match, best_score)
            if enhanced_match:
                return enhanced_match
        
        # Umbral mínimo de confianza (30% sin LLM, 25% con LLM)
        threshold = 0.25 if self.use_llm else 0.3
        if best_score >= threshold:
            logger.info(f"Problema detectado: {best_match.problem_id} (confianza: {best_score:.2%})")
            return best_match
        
        logger.info(f"No se detectó un problema conocido (mejor match: {best_score:.2%})")
        return None
    
    def _enhance_detection_with_llm(self, description: str, best_match: Optional[TroubleshootingGuide], score: float) -> Optional[TroubleshootingGuide]:
        """Usa LLM para mejorar la detección de problemas"""
        if not self.openai_api_key or not best_match:
            return None
        
        try:
            import requests
            
            # Preparar contexto de problemas disponibles
            problems_context = "\n".join([
                f"- {pid}: {guide.problem_title} ({guide.problem_description[:100]})"
                for pid, guide in list(self.knowledge_base.items())[:10]
            ])
            
            prompt = f"""Eres un asistente de soporte técnico. Analiza la siguiente descripción de problema y determina cuál de los problemas conocidos es el más relevante.

Problemas conocidos:
{problems_context}

Descripción del usuario: "{description}"

Responde SOLO con el ID del problema más relevante (ej: "instalacion_software") o "ninguno" si ninguno aplica. No incluyas explicaciones."""

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 50
                },
                timeout=5
            )
            
            if response.ok:
                result = response.json()
                llm_suggestion = result["choices"][0]["message"]["content"].strip().lower()
                
                # Si el LLM sugiere un problema diferente y tiene más confianza
                if llm_suggestion in self.knowledge_base and llm_suggestion != best_match.problem_id:
                    logger.info(f"LLM sugiere problema diferente: {llm_suggestion}")
                    return self.knowledge_base[llm_suggestion]
                elif llm_suggestion == best_match.problem_id and score < 0.4:
                    # LLM confirma el match, aumentar confianza
                    logger.info(f"LLM confirma problema: {best_match.problem_id}")
                    return best_match
                    
        except Exception as e:
            logger.warning(f"Error usando LLM para detección: {e}")
        
        return None
    
    def _calculate_match_score(self, description: str, guide: TroubleshootingGuide) -> float:
        """Calcula un score de coincidencia entre la descripción y la guía"""
        # Método mejorado: combinación de keywords y similitud semántica
        
        # 1. Score por keywords (método original mejorado)
        keywords = [
            guide.problem_title.lower(),
            guide.problem_description.lower()
        ]
        
        matches = 0
        total_keywords = 0
        
        for keyword_phrase in keywords:
            words = keyword_phrase.split()
            total_keywords += len(words)
            for word in words:
                if len(word) > 3 and word in description:
                    matches += 1
        
        keyword_score = matches / total_keywords if total_keywords > 0 else 0.0
        
        # 2. Score por similitud de términos importantes
        important_words = set()
        for phrase in keywords:
            # Extraer palabras importantes (más de 4 caracteres, no artículos/preposiciones)
            stop_words = {'el', 'la', 'los', 'las', 'de', 'del', 'en', 'con', 'por', 'para', 'que', 'como'}
            words = [w for w in phrase.split() if len(w) > 4 and w not in stop_words]
            important_words.update(words)
        
        description_words = set(description.lower().split())
        common_words = important_words.intersection(description_words)
        semantic_score = len(common_words) / len(important_words) if important_words else 0.0
        
        # 3. Score por frases completas
        phrase_score = 0.0
        for phrase in keywords:
            if len(phrase) > 10:  # Solo frases significativas
                # Verificar si la frase o parte de ella aparece
                phrase_words = phrase.split()
                if len(phrase_words) >= 3:
                    # Verificar si al menos 2 palabras de la frase aparecen juntas
                    for i in range(len(description_words) - 1):
                        word_pair = f"{list(description_words)[i]} {list(description_words)[i+1]}"
                        if any(f"{w1} {w2}" in phrase for w1, w2 in zip(phrase_words, phrase_words[1:])):
                            phrase_score = 0.3
                            break
        
        # Combinar scores (peso: keywords 40%, semántico 40%, frases 20%)
        final_score = (keyword_score * 0.4) + (semantic_score * 0.4) + (phrase_score * 0.2)
        
        return min(final_score, 1.0)  # Asegurar que no exceda 1.0
    
    def start_troubleshooting(
        self,
        problem_description: str,
        customer_email: str,
        customer_name: Optional[str] = None,
        ticket_id: Optional[str] = None,
        validate: bool = True
    ) -> TroubleshootingSession:
        """
        Inicia una sesión de troubleshooting.
        
        Args:
            problem_description: Descripción del problema
            customer_email: Email del cliente
            customer_name: Nombre del cliente (opcional)
            ticket_id: ID del ticket asociado (opcional)
            validate: Si validar inputs (default: True)
            
        Returns:
            TroubleshootingSession iniciada
        """
        # Validar inputs si está habilitado
        if validate and self.validator:
            request_data = {
                "problem_description": problem_description,
                "customer_email": customer_email,
                "ticket_id": ticket_id
            }
            is_valid, errors = self.validator.validate_troubleshooting_request(request_data)
            if not is_valid:
                error_msg = f"Validación fallida: {', '.join(errors)}"
                if self.error_handler:
                    self.error_handler.handle_error(
                        ValueError(error_msg),
                        severity=ErrorSeverity.MEDIUM,
                        category=ErrorCategory.VALIDATION
                    )
                raise ValueError(error_msg)
        
        # Sanitizar inputs
        if self.validator:
            problem_description = self.validator.sanitize_text(problem_description)
            customer_email = customer_email.strip().lower()
            if customer_name:
                customer_name = self.validator.sanitize_text(customer_name)
        
        session_id = str(uuid.uuid4())
        
        # Detectar problema
        detected_problem = self.detect_problem(problem_description)
        
        session = TroubleshootingSession(
            session_id=session_id,
            ticket_id=ticket_id,
            customer_email=customer_email,
            customer_name=customer_name,
            problem_description=problem_description,
            detected_problem=detected_problem,
            status=TroubleshootingStatus.STARTED if detected_problem else TroubleshootingStatus.NEEDS_ESCALATION
        )
        
        self.active_sessions[session_id] = session
        logger.info(f"Sesión de troubleshooting iniciada: {session_id}")
        
        # Disparar webhook si está disponible
        if self.webhook_manager:
            try:
                self.webhook_manager.trigger_webhook(
                    WebhookEvent.SESSION_STARTED,
                    {
                        "session_id": session_id,
                        "ticket_id": ticket_id,
                        "customer_email": customer_email,
                        "problem_description": problem_description,
                        "detected_problem": detected_problem.problem_id if detected_problem else None
                    }
                )
            except Exception as e:
                if self.error_handler:
                    self.error_handler.handle_error(
                        e,
                        severity=ErrorSeverity.LOW,
                        category=ErrorCategory.EXTERNAL_API,
                        context={"action": "trigger_webhook", "event": "SESSION_STARTED"}
                    )
                logger.warning(f"Error disparando webhook: {e}")
        
        return session
    
    def get_current_step(self, session_id: str) -> Optional[Dict]:
        """
        Obtiene el paso actual de troubleshooting para una sesión.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Diccionario con información del paso actual o None si no hay sesión
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        if not session.detected_problem:
            return {
                "status": "no_problem_detected",
                "message": "No se pudo detectar un problema conocido. Se recomienda escalar el ticket.",
                "suggest_escalation": True
            }
        
        if session.current_step >= len(session.detected_problem.steps):
            return {
                "status": "completed",
                "message": "Todos los pasos han sido completados.",
                "suggest_escalation": True if session.status != TroubleshootingStatus.RESOLVED else False
            }
        
        step = session.detected_problem.steps[session.current_step]
        
        return {
            "session_id": session_id,
            "step_number": step.step_number,
            "title": step.title,
            "description": step.description,
            "instructions": step.instructions,
            "expected_result": step.expected_result,
            "warnings": step.warnings,
            "resources": step.resources,
            "total_steps": len(session.detected_problem.steps),
            "current_step": session.current_step + 1,
            "estimated_time": session.detected_problem.estimated_time,
            "difficulty": session.detected_problem.difficulty
        }
    
    def complete_step(
        self,
        session_id: str,
        success: bool,
        notes: Optional[str] = None,
        validate: bool = True
    ) -> Dict:
        """
        Marca un paso como completado y avanza al siguiente.
        
        Args:
            session_id: ID de la sesión
            success: Si el paso fue exitoso
            notes: Notas adicionales del usuario
            validate: Si validar inputs (default: True)
            
        Returns:
            Diccionario con el siguiente paso o resultado final
        """
        # Validar inputs
        if validate and self.validator:
            request_data = {
                "session_id": session_id,
                "success": success,
                "notes": notes
            }
            is_valid, errors = self.validator.validate_step_completion(request_data)
            if not is_valid:
                error_msg = f"Validación fallida: {', '.join(errors)}"
                if self.error_handler:
                    self.error_handler.handle_error(
                        ValueError(error_msg),
                        severity=ErrorSeverity.MEDIUM,
                        category=ErrorCategory.VALIDATION,
                        session_id=session_id
                    )
                return {"error": error_msg}
        
        # Sanitizar notes si existe
        if notes and self.validator:
            notes = self.validator.sanitize_text(notes, self.validator.MAX_NOTES_LENGTH)
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Sesión no encontrada"}
        
        if not session.detected_problem:
            return {"error": "No hay problema detectado para esta sesión"}
        
        if session.current_step >= len(session.detected_problem.steps):
            return {"error": "No hay más pasos"}
        
        # Registrar intento del paso
        step = session.detected_problem.steps[session.current_step]
        attempt = {
            "step_number": step.step_number,
            "success": success,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        session.attempted_steps.append(attempt)
        
            if success:
                step.status = StepStatus.COMPLETED
                session.current_step += 1
                
                # Disparar webhook de paso completado
                if self.webhook_manager:
                    try:
                        self.webhook_manager.trigger_webhook(
                            WebhookEvent.STEP_COMPLETED,
                            {
                                "session_id": session_id,
                                "step_number": step.step_number,
                                "success": True
                            }
                        )
                    except Exception as e:
                        if self.error_handler:
                            self.error_handler.handle_error(
                                e,
                                severity=ErrorSeverity.LOW,
                                category=ErrorCategory.EXTERNAL_API
                            )
                
                # Verificar si se completaron todos los pasos
                if session.current_step >= len(session.detected_problem.steps):
                    session.status = TroubleshootingStatus.RESOLVED
                    session.resolved_at = datetime.now()
                    
                    # Disparar webhook de resolución
                    if self.webhook_manager:
                        try:
                            self.webhook_manager.trigger_webhook(
                                WebhookEvent.SESSION_RESOLVED,
                                {
                                    "session_id": session_id,
                                    "ticket_id": session.ticket_id,
                                    "total_steps": len(session.detected_problem.steps)
                                }
                            )
                        except Exception as e:
                            if self.error_handler:
                                self.error_handler.handle_error(
                                    e,
                                    severity=ErrorSeverity.LOW,
                                    category=ErrorCategory.EXTERNAL_API
                                )
                    
                    return {
                        "status": "resolved",
                        "message": "¡Excelente! Has completado todos los pasos. El problema debería estar resuelto.",
                        "suggest_escalation": False,
                        "next_action": "Verificar que el problema esté completamente resuelto"
                    }
                else:
                    return {
                        "status": "next_step",
                        "message": "Paso completado exitosamente. Continuando con el siguiente paso.",
                        "next_step": self.get_current_step(session_id)
                    }
        else:
            step.status = StepStatus.FAILED
            
            # Disparar webhook de paso fallido
            if self.webhook_manager:
                try:
                    self.webhook_manager.trigger_webhook(
                        WebhookEvent.STEP_FAILED,
                        {
                            "session_id": session_id,
                            "step_number": step.step_number,
                            "notes": notes
                        }
                    )
                except Exception as e:
                    if self.error_handler:
                        self.error_handler.handle_error(
                            e,
                            severity=ErrorSeverity.LOW,
                            category=ErrorCategory.EXTERNAL_API
                        )
            
            # Verificar criterios de escalación
            should_escalate = self._should_escalate(session)
            
            if should_escalate:
                session.status = TroubleshootingStatus.NEEDS_ESCALATION
                
                # Disparar webhook de escalación
                if self.webhook_manager:
                    try:
                        self.webhook_manager.trigger_webhook(
                            WebhookEvent.SESSION_ESCALATED,
                            {
                                "session_id": session_id,
                                "ticket_id": session.ticket_id,
                                "reason": self._get_escalation_reason(session)
                            }
                        )
                    except Exception as e:
                        if self.error_handler:
                            self.error_handler.handle_error(
                                e,
                                severity=ErrorSeverity.LOW,
                                category=ErrorCategory.EXTERNAL_API
                            )
                
                return {
                    "status": "needs_escalation",
                    "message": "El paso no se completó exitosamente. Basándome en los intentos, recomiendo escalar este ticket a un agente humano.",
                    "suggest_escalation": True,
                    "escalation_reason": self._get_escalation_reason(session)
                }
            else:
                return {
                    "status": "step_failed",
                    "message": "El paso no se completó exitosamente. Revisa las instrucciones y los recursos proporcionados.",
                    "suggest_escalation": False,
                    "current_step": self.get_current_step(session_id),
                    "common_issues": session.detected_problem.common_issues
                }
    
    def _should_escalate(self, session: TroubleshootingSession) -> bool:
        """Determina si una sesión debe ser escalada"""
        if not session.detected_problem:
            return True
        
        # Escalar si hay más de 2 pasos fallidos
        failed_steps = sum(1 for attempt in session.attempted_steps if not attempt.get("success", False))
        if failed_steps >= 2:
            return True
        
        # Escalar si se han intentado todos los pasos sin éxito
        if session.current_step >= len(session.detected_problem.steps):
            all_failed = all(not attempt.get("success", False) for attempt in session.attempted_steps)
            if all_failed:
                return True
        
        return False
    
    def _get_escalation_reason(self, session: TroubleshootingSession) -> str:
        """Obtiene la razón de escalación"""
        if not session.detected_problem:
            return "Problema no identificado en la base de conocimiento"
        
        failed_steps = sum(1 for attempt in session.attempted_steps if not attempt.get("success", False))
        if failed_steps >= 2:
            return f"Múltiples pasos fallidos ({failed_steps} de {len(session.attempted_steps)})"
        
        return "Problema no resuelto después de seguir todos los pasos"
    
    def escalate_ticket(self, session_id: str, reason: Optional[str] = None) -> Dict:
        """
        Escala un ticket a un agente humano.
        
        Args:
            session_id: ID de la sesión
            reason: Razón de la escalación
            
        Returns:
            Información sobre la escalación
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Sesión no encontrada"}
        
        session.status = TroubleshootingStatus.ESCALATED
        
        escalation_info = {
            "session_id": session_id,
            "ticket_id": session.ticket_id,
            "customer_email": session.customer_email,
            "customer_name": session.customer_name,
            "problem_description": session.problem_description,
            "detected_problem": session.detected_problem.problem_id if session.detected_problem else None,
            "attempted_steps": len(session.attempted_steps),
            "failed_steps": sum(1 for attempt in session.attempted_steps if not attempt.get("success", False)),
            "reason": reason or self._get_escalation_reason(session),
            "notes": session.notes,
            "escalated_at": datetime.now().isoformat()
        }
        
        logger.info(f"Ticket escalado: {session_id} - {reason}")
        
        return escalation_info
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Obtiene un resumen de la sesión de troubleshooting"""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        return {
            "session_id": session_id,
            "ticket_id": session.ticket_id,
            "status": session.status.value,
            "problem_detected": session.detected_problem.problem_title if session.detected_problem else None,
            "current_step": session.current_step,
            "total_steps": len(session.detected_problem.steps) if session.detected_problem else 0,
            "started_at": session.started_at.isoformat(),
            "resolved_at": session.resolved_at.isoformat() if session.resolved_at else None,
            "attempted_steps": len(session.attempted_steps),
            "successful_steps": sum(1 for attempt in session.attempted_steps if attempt.get("success", False))
        }
    
    def format_step_response(self, step_info: Dict, use_llm_enhancement: bool = False) -> str:
        """
        Formatea la información de un paso en un mensaje legible para el cliente.
        
        Args:
            step_info: Información del paso obtenida de get_current_step()
            use_llm_enhancement: Si usar LLM para personalizar la respuesta
            
        Returns:
            Mensaje formateado
        """
        if step_info.get("status") == "no_problem_detected":
            base_message = (
                "🔍 No pude identificar un problema conocido en tu descripción.\n\n"
                "Para ayudarte mejor, recomiendo escalar tu ticket a un agente humano "
                "que podrá asistirte de manera personalizada.\n\n"
                "¿Te gustaría que escale tu ticket ahora?"
            )
            
            # Mejorar con LLM si está disponible
            if use_llm_enhancement and self.use_llm and self.openai_api_key:
                return self._enhance_message_with_llm(base_message, step_info)
            return base_message
        
        if step_info.get("status") == "completed":
            base_message = (
                "✅ ¡Excelente! Has completado todos los pasos.\n\n"
                "Si el problema persiste, por favor escálalo para que un agente pueda ayudarte."
            )
            if use_llm_enhancement and self.use_llm and self.openai_api_key:
                return self._enhance_message_with_llm(base_message, step_info)
            return base_message
        
        messages = []
        messages.append(f"📋 **Paso {step_info['current_step']} de {step_info['total_steps']}**")
        messages.append(f"**{step_info['title']}**\n")
        messages.append(f"{step_info['description']}\n")
        
        messages.append("**Instrucciones:**")
        for i, instruction in enumerate(step_info['instructions'], 1):
            messages.append(f"{i}. {instruction}")
        
        if step_info.get('warnings'):
            messages.append("\n⚠️ **Precauciones importantes:**")
            for warning in step_info['warnings']:
                messages.append(f"• {warning}")
        
        if step_info.get('resources'):
            messages.append("\n📚 **Recursos útiles:**")
            for resource in step_info['resources']:
                messages.append(f"• {resource.get('title', 'Recurso')}: {resource.get('url', '')}")
        
        messages.append(f"\n**Resultado esperado:** {step_info['expected_result']}")
        messages.append(f"\n⏱️ Tiempo estimado: {step_info.get('estimated_time', 'N/A')}")
        
        base_message = "\n".join(messages)
        
        # Mejorar con LLM si está disponible
        if use_llm_enhancement and self.use_llm and self.openai_api_key:
            return self._enhance_message_with_llm(base_message, step_info)
        
        return base_message
    
    def _enhance_message_with_llm(self, base_message: str, step_info: Dict) -> str:
        """Usa LLM para mejorar y personalizar el mensaje"""
        try:
            import requests
            
            prompt = f"""Eres un asistente de soporte técnico amigable y profesional. 
Mejora el siguiente mensaje de troubleshooting para que sea más claro, amigable y fácil de seguir.
Mantén toda la información técnica importante pero hazla más accesible.

Mensaje original:
{base_message}

Mejora el mensaje manteniendo:
- Todas las instrucciones técnicas
- Todas las precauciones
- Todos los recursos
- El tono profesional pero amigable

Responde SOLO con el mensaje mejorado, sin explicaciones adicionales."""

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 800
                },
                timeout=10
            )
            
            if response.ok:
                result = response.json()
                enhanced = result["choices"][0]["message"]["content"].strip()
                logger.info("Mensaje mejorado con LLM")
                return enhanced
        except Exception as e:
            logger.warning(f"Error mejorando mensaje con LLM: {e}")
        
        return base_message
    
    def collect_feedback(
        self,
        session_id: str,
        rating: int,
        feedback_text: Optional[str] = None,
        was_helpful: Optional[bool] = None
    ) -> Dict:
        """
        Recolecta feedback del cliente sobre la sesión de troubleshooting.
        
        Args:
            session_id: ID de la sesión
            rating: Calificación de 1 a 5
            feedback_text: Texto de feedback opcional
            was_helpful: Si fue útil (opcional)
            
        Returns:
            Información del feedback guardado
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Sesión no encontrada"}
        
        if not (1 <= rating <= 5):
            return {"error": "Rating debe estar entre 1 y 5"}
        
        feedback_data = {
            "session_id": session_id,
            "ticket_id": session.ticket_id,
            "customer_email": session.customer_email,
            "rating": rating,
            "feedback_text": feedback_text,
            "was_helpful": was_helpful,
            "problem_detected": session.detected_problem.problem_id if session.detected_problem else None,
            "total_steps": len(session.detected_problem.steps) if session.detected_problem else 0,
            "completed_steps": session.current_step,
            "resolved": session.status == TroubleshootingStatus.RESOLVED,
            "collected_at": datetime.now().isoformat()
        }
        
        # Guardar feedback en la sesión
        if not hasattr(session, 'feedback'):
            session.feedback = feedback_data
        else:
            session.feedback.update(feedback_data)
        
        logger.info(f"Feedback recolectado para sesión {session_id}: rating={rating}")
        
        return feedback_data
    
    def get_analytics(self, days: int = 30) -> Dict:
        """
        Obtiene analytics y métricas del sistema de troubleshooting.
        
        Args:
            days: Número de días hacia atrás para analizar
            
        Returns:
            Diccionario con métricas y estadísticas
        """
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        analytics = {
            "period_days": days,
            "total_sessions": 0,
            "resolved_sessions": 0,
            "escalated_sessions": 0,
            "resolution_rate": 0.0,
            "average_steps_to_resolution": 0.0,
            "average_rating": 0.0,
            "problem_distribution": {},
            "common_failed_steps": {},
            "feedback_summary": {
                "total_feedback": 0,
                "average_rating": 0.0,
                "helpful_percentage": 0.0
            }
        }
        
        # Analizar sesiones activas (en producción esto vendría de BD)
        resolved_count = 0
        escalated_count = 0
        total_steps = 0
        ratings = []
        helpful_count = 0
        problem_counts = {}
        failed_steps = {}
        
        for session_id, session in self.active_sessions.items():
            if session.started_at < cutoff_date:
                continue
            
            analytics["total_sessions"] += 1
            
            if session.status == TroubleshootingStatus.RESOLVED:
                resolved_count += 1
                if session.detected_problem:
                    total_steps += session.current_step
            elif session.status == TroubleshootingStatus.ESCALATED:
                escalated_count += 1
            
            # Contar problemas
            if session.detected_problem:
                problem_id = session.detected_problem.problem_id
                problem_counts[problem_id] = problem_counts.get(problem_id, 0) + 1
            
            # Analizar pasos fallidos
            for attempt in session.attempted_steps:
                if not attempt.get("success", False):
                    step_num = attempt.get("step_number", 0)
                    failed_steps[step_num] = failed_steps.get(step_num, 0) + 1
            
            # Feedback
            if hasattr(session, 'feedback') and session.feedback:
                ratings.append(session.feedback.get("rating", 0))
                if session.feedback.get("was_helpful"):
                    helpful_count += 1
        
        analytics["resolved_sessions"] = resolved_count
        analytics["escalated_sessions"] = escalated_count
        analytics["resolution_rate"] = (resolved_count / analytics["total_sessions"] * 100) if analytics["total_sessions"] > 0 else 0.0
        analytics["average_steps_to_resolution"] = (total_steps / resolved_count) if resolved_count > 0 else 0.0
        analytics["average_rating"] = sum(ratings) / len(ratings) if ratings else 0.0
        analytics["problem_distribution"] = problem_counts
        analytics["common_failed_steps"] = dict(sorted(failed_steps.items(), key=lambda x: x[1], reverse=True)[:5])
        analytics["feedback_summary"]["total_feedback"] = len(ratings)
        analytics["feedback_summary"]["average_rating"] = analytics["average_rating"]
        analytics["feedback_summary"]["helpful_percentage"] = (helpful_count / len(ratings) * 100) if ratings else 0.0
        
        return analytics

