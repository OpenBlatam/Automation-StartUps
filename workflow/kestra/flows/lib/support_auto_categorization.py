"""
Módulo de Categorización Automática Avanzada de Tickets.

Características:
- Categorización usando análisis de texto y NLP
- Detección de subcategorías
- ML-based classification (opcional)
- Integración con base de conocimiento
- Cache para performance
- Analytics y tracking de precisión
- Retry automático con exponential backoff
"""
import re
import logging
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import lru_cache
from collections import defaultdict

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Cache global para categorización (en memoria)
_categorization_cache = {}
_cache_ttl = timedelta(hours=1)


@dataclass
class CategoryResult:
    """Resultado de categorización."""
    category: str
    subcategory: Optional[str]
    confidence: float
    reasoning: str
    keywords_matched: List[str]


class SupportAutoCategorizer:
    """Categorizador automático de tickets."""
    
    # Patrones de categorías principales
    CATEGORY_PATTERNS = {
        "billing": {
            "keywords": [
                "pago", "payment", "factura", "invoice", "cobro", "tarjeta", "card",
                "refund", "reembolso", "devolución", "charge", "cargo", "billing",
                "subscription", "suscripción", "plan", "precio", "price", "cost",
                "pagado", "paid", "no me cobraron", "cobro incorrecto"
            ],
            "subcategories": {
                "payment_issue": ["no puedo pagar", "pago fallido", "payment failed", "error de pago"],
                "refund_request": ["reembolso", "refund", "devolución", "quiero mi dinero"],
                "invoice_issue": ["factura", "invoice", "recibo", "bill"],
                "billing_question": ["precio", "price", "costo", "plan", "subscription"]
            }
        },
        "technical": {
            "keywords": [
                "error", "bug", "falla", "no funciona", "broken", "crash", "caído",
                "lento", "slow", "problema técnico", "technical issue", "bug report",
                "no carga", "no se abre", "no inicia", "error de conexión", "connection error",
                "api", "integration", "sincronización", "sync", "webhook"
            ],
            "subcategories": {
                "bug_report": ["bug", "error", "falla", "no funciona", "broken"],
                "performance": ["lento", "slow", "performance", "rendimiento", "tarda mucho"],
                "integration": ["api", "integration", "sincronización", "sync", "webhook", "connector"],
                "access_issue": ["no puedo acceder", "access denied", "login", "contraseña", "password"]
            }
        },
        "sales": {
            "keywords": [
                "demo", "demostración", "prueba", "trial", "precio", "price", "plan",
                "características", "features", "funcionalidades", "comparar", "compare",
                "upgrade", "downgrade", "cambiar plan", "quiero comprar", "quiero contratar"
            ],
            "subcategories": {
                "demo_request": ["demo", "demostración", "prueba", "trial"],
                "pricing_question": ["precio", "price", "costo", "plan", "tarifa"],
                "feature_inquiry": ["características", "features", "funcionalidades", "qué puede hacer"],
                "upgrade_request": ["upgrade", "downgrade", "cambiar plan", "mejor plan"]
            }
        },
        "account": {
            "keywords": [
                "cuenta", "account", "perfil", "profile", "login", "logout", "acceso",
                "contraseña", "password", "reset", "cambiar", "update", "editar",
                "eliminar cuenta", "delete account", "cerrar cuenta", "close account"
            ],
            "subcategories": {
                "login_issue": ["login", "acceso", "no puedo entrar", "no puedo acceder"],
                "password_reset": ["contraseña", "password", "reset", "olvidé", "forgot"],
                "profile_update": ["perfil", "profile", "editar", "update", "cambiar"],
                "account_deletion": ["eliminar", "delete", "cerrar", "close", "cancelar"]
            }
        },
        "security": {
            "keywords": [
                "seguridad", "security", "hack", "brecha", "breach", "phishing",
                "sospechoso", "suspicious", "no autorizado", "unauthorized", "violación",
                "datos", "data", "privacidad", "privacy", "vulnerabilidad", "vulnerability"
            ],
            "subcategories": {
                "security_breach": ["brecha", "breach", "hack", "comprometido", "compromised"],
                "suspicious_activity": ["sospechoso", "suspicious", "no autorizado", "unauthorized"],
                "privacy_concern": ["privacidad", "privacy", "datos", "data", "información personal"],
                "vulnerability_report": ["vulnerabilidad", "vulnerability", "fallo de seguridad"]
            }
        },
        "general": {
            "keywords": [
                "pregunta", "question", "ayuda", "help", "información", "information",
                "cómo", "how", "tutorial", "guía", "guide", "documentación", "documentation"
            ],
            "subcategories": {
                "general_question": ["pregunta", "question", "ayuda", "help"],
                "how_to": ["cómo", "how", "tutorial", "guía", "guide"],
                "documentation": ["documentación", "documentation", "información", "information"]
            }
        }
    }
    
    # Prioridad de categorías (si hay conflicto)
    CATEGORY_PRIORITY = {
        "security": 100,
        "billing": 80,
        "technical": 60,
        "account": 50,
        "sales": 40,
        "general": 10
    }
    
    def __init__(
        self,
        db_connection: Any = None,
        use_ml: bool = False,
        ml_api_url: Optional[str] = None,
        enable_cache: bool = True,
        enable_analytics: bool = True,
        min_confidence_threshold: float = 0.5
    ):
        """
        Inicializa el categorizador.
        
        Args:
            db_connection: Conexión a BD para consultar historial
            use_ml: Usar clasificación ML (requiere API)
            ml_api_url: URL de API de ML para clasificación
            enable_cache: Habilitar cache de categorizaciones
            enable_analytics: Habilitar tracking de analytics
            min_confidence_threshold: Umbral mínimo de confianza (0.0-1.0)
        """
        self.db_connection = db_connection
        self.use_ml = use_ml and ml_api_url and REQUESTS_AVAILABLE
        self.ml_api_url = ml_api_url
        self.enable_cache = enable_cache
        self.enable_analytics = enable_analytics
        self.min_confidence_threshold = min_confidence_threshold
        
        # Configurar sesión HTTP con retry si está disponible
        if self.use_ml and REQUESTS_AVAILABLE:
            self.session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["POST"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
        else:
            self.session = None
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para análisis."""
        if not text:
            return ""
        # Convertir a minúsculas y eliminar caracteres especiales excesivos
        text = text.lower().strip()
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _calculate_category_score(
        self,
        category: str,
        patterns: Dict[str, Any],
        text: str
    ) -> Tuple[float, List[str]]:
        """Calcula score de una categoría."""
        score = 0.0
        keywords_matched = []
        
        # Buscar keywords
        for keyword in patterns["keywords"]:
            if keyword in text:
                score += 1.0
                keywords_matched.append(keyword)
        
        # Normalizar score (máximo 10 puntos por keyword)
        score = min(10.0, score)
        
        return score, keywords_matched
    
    def _detect_subcategory(
        self,
        category: str,
        text: str
    ) -> Optional[Tuple[str, float]]:
        """Detecta subcategoría."""
        if category not in self.CATEGORY_PATTERNS:
            return None
        
        patterns = self.CATEGORY_PATTERNS[category]
        subcategories = patterns.get("subcategories", {})
        
        best_subcategory = None
        best_score = 0.0
        
        for subcat, keywords in subcategories.items():
            matches = sum(1 for kw in keywords if kw in text)
            if matches > best_score:
                best_score = matches
                best_subcategory = subcategory
        
        if best_score > 0:
            return (best_subcategory, best_score / len(subcategories))
        
        return None
    
    def _classify_with_ml(self, subject: str, description: str) -> Optional[Dict[str, Any]]:
        """Clasifica usando ML API (opcional) con retry."""
        if not self.use_ml or not self.ml_api_url:
            return None
        
        try:
            if self.session:
                response = self.session.post(
                    self.ml_api_url,
                    json={
                        "subject": subject or "",
                        "description": description
                    },
                    timeout=10
                )
            else:
                response = requests.post(
                    self.ml_api_url,
                    json={
                        "subject": subject or "",
                        "description": description
                    },
                    timeout=10
                )
            
            response.raise_for_status()
            result = response.json()
            
            # Validar respuesta
            if not isinstance(result, dict) or "category" not in result:
                logger.warning(f"Respuesta ML inválida: {result}")
                return None
            
            return result
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout en clasificación ML para ticket")
            return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error en clasificación ML: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado en clasificación ML: {e}", exc_info=True)
            return None
    
    def _get_cache_key(
        self,
        subject: Optional[str],
        description: str
    ) -> str:
        """Genera clave de cache para categorización."""
        text = f"{subject or ''} {description}".lower().strip()
        return hashlib.md5(text.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[CategoryResult]:
        """Verifica cache de categorización."""
        if cache_key in _categorization_cache:
            result, timestamp = _categorization_cache[cache_key]
            if datetime.now() - timestamp < _cache_ttl:
                logger.debug(f"Cache hit para categorización: {cache_key[:8]}")
                return result
            else:
                # Cache expirado
                del _categorization_cache[cache_key]
        return None
    
    def _store_cache(self, cache_key: str, result: CategoryResult):
        """Almacena resultado en cache."""
        # Limitar tamaño del cache (mantener solo los últimos 1000)
        if len(_categorization_cache) > 1000:
            # Eliminar entradas más antiguas
            sorted_items = sorted(
                _categorization_cache.items(),
                key=lambda x: x[1][1]  # Ordenar por timestamp
            )
            for key, _ in sorted_items[:100]:  # Eliminar 100 más antiguos
                del _categorization_cache[key]
        
        _categorization_cache[cache_key] = (result, datetime.now())
    
    def categorize(
        self,
        subject: Optional[str],
        description: str,
        existing_category: Optional[str] = None,
        customer_email: Optional[str] = None,
        use_cache: bool = True,
        track_analytics: bool = True,
        ticket_id: Optional[str] = None
    ) -> CategoryResult:
        """
        Categoriza un ticket automáticamente.
        
        Args:
            subject: Asunto del ticket
            description: Descripción
            existing_category: Categoría existente (si hay)
            customer_email: Email del cliente
            use_cache: Usar cache si está disponible
            track_analytics: Trackear para analytics
            ticket_id: ID del ticket (para tracking)
            
        Returns:
            CategoryResult con categoría, subcategoría y confianza
        """
        # Verificar cache primero
        if use_cache and self.enable_cache:
            cache_key = self._get_cache_key(subject, description)
            cached_result = self._check_cache(cache_key)
            if cached_result:
                logger.debug(f"Usando categorización desde cache para ticket {ticket_id}")
                return cached_result
        
        # Normalizar texto
        full_text = self._normalize_text(f"{subject or ''} {description or ''}")
        
        if not full_text:
            result = CategoryResult(
                category=existing_category or "general",
                subcategory=None,
                confidence=0.0,
                reasoning="Texto vacío",
                keywords_matched=[]
            )
            if use_cache and self.enable_cache:
                cache_key = self._get_cache_key(subject, description)
                self._store_cache(cache_key, result)
            return result
        
        # Intentar clasificación ML si está disponible
        ml_result = None
        if self.use_ml:
            try:
                ml_result = self._classify_with_ml(subject or "", description)
            except Exception as e:
                logger.warning(f"Error en ML classification, usando fallback: {e}")
        
        # Si ML tiene alta confianza, usarlo
        if ml_result and ml_result.get("confidence", 0) > 0.8:
            result = CategoryResult(
                category=ml_result.get("category", "general"),
                subcategory=ml_result.get("subcategory"),
                confidence=ml_result.get("confidence", 0.0),
                reasoning="Clasificación ML",
                keywords_matched=ml_result.get("keywords", [])
            )
            # Guardar en cache y trackear
            if use_cache and self.enable_cache:
                cache_key = self._get_cache_key(subject, description)
                self._store_cache(cache_key, result)
            if track_analytics and self.enable_analytics and ticket_id and self.db_connection:
                try:
                    from support_categorization_analytics import SupportCategorizationAnalytics
                    analytics = SupportCategorizationAnalytics(db_connection=self.db_connection)
                    analytics.track_categorization(
                        ticket_id=ticket_id,
                        auto_category=result.category,
                        auto_subcategory=result.subcategory,
                        confidence=result.confidence,
                        final_category=None,
                        final_subcategory=None,
                        manually_corrected=False
                    )
                except Exception as e:
                    logger.debug(f"No se pudo trackear analytics: {e}")
            return result
        
        # Clasificación basada en patrones
        category_scores = {}
        all_keywords = []
        
        for category, patterns in self.CATEGORY_PATTERNS.items():
            score, keywords = self._calculate_category_score(category, patterns, full_text)
            if score > 0:
                category_scores[category] = {
                    "score": score,
                    "keywords": keywords,
                    "priority": self.CATEGORY_PRIORITY.get(category, 0)
                }
                all_keywords.extend(keywords)
        
        # Si no hay matches, usar categoría existente o general
        if not category_scores:
            return CategoryResult(
                category=existing_category or "general",
                subcategory=None,
                confidence=0.3,
                reasoning="Sin matches de keywords, usando categoría por defecto",
                keywords_matched=[]
            )
        
        # Seleccionar categoría con mejor score (priorizando por prioridad si hay empate)
        best_category = max(
            category_scores.items(),
            key=lambda x: (x[1]["score"], x[1]["priority"])
        )[0]
        
        best_data = category_scores[best_category]
        
        # Calcular confianza
        confidence = min(1.0, best_data["score"] / 10.0)
        
        # Si hay múltiples categorías con score similar, reducir confianza
        similar_scores = [
            s["score"] for c, s in category_scores.items()
            if c != best_category and abs(s["score"] - best_data["score"]) < 2.0
        ]
        if similar_scores:
            confidence *= 0.7
        
        # Detectar subcategoría
        subcategory_result = self._detect_subcategory(best_category, full_text)
        subcategory = subcategory_result[0] if subcategory_result else None
        
        # Construir reasoning
        reasoning_parts = [f"Score: {best_data['score']:.1f}"]
        if best_data["keywords"]:
            reasoning_parts.append(f"Keywords: {', '.join(best_data['keywords'][:5])}")
        if subcategory:
            reasoning_parts.append(f"Subcategoría: {subcategory}")
        
        reasoning = "; ".join(reasoning_parts)
        
        result = CategoryResult(
            category=best_category,
            subcategory=subcategory,
            confidence=confidence,
            reasoning=reasoning,
            keywords_matched=best_data["keywords"]
        )
        
        # Guardar en cache
        if use_cache and self.enable_cache:
            cache_key = self._get_cache_key(subject, description)
            self._store_cache(cache_key, result)
        
        # Trackear analytics
        if track_analytics and self.enable_analytics and ticket_id and self.db_connection:
            try:
                from support_categorization_analytics import SupportCategorizationAnalytics
                analytics = SupportCategorizationAnalytics(db_connection=self.db_connection)
                analytics.track_categorization(
                    ticket_id=ticket_id,
                    auto_category=result.category,
                    auto_subcategory=result.subcategory,
                    confidence=result.confidence,
                    final_category=None,
                    final_subcategory=None,
                    manually_corrected=False
                )
            except Exception as e:
                logger.debug(f"No se pudo trackear analytics: {e}")
        
        return result

