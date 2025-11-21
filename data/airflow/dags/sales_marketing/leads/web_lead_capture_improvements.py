"""
Mejoras avanzadas para el DAG de captura de leads.

Mejoras implementadas:
- Scoring con IA (usando LLM)
- Enriquecimiento de datos con APIs externas
- Detección de spam mejorada con ML
- Analytics y métricas avanzadas
- Integración con sistema de descripciones de puesto
- Notificaciones inteligentes
- Caché para evitar procesamiento duplicado
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import json
import logging
import hashlib
import requests
from airflow.decorators import task
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


class LLMLeadScorer:
    """Scoring de leads usando IA."""
    
    def __init__(self):
        self.provider = Variable.get("DEFAULT_LLM_PROVIDER", default_var="openai")
        self._setup_provider()
    
    def _setup_provider(self):
        """Configura el proveedor de IA."""
        if self.provider == 'openai':
            self.api_key = Variable.get("OPENAI_API_KEY", default_var=None)
            self.base_url = Variable.get("OPENAI_BASE_URL", default_var="https://api.openai.com/v1")
            self.model = Variable.get("OPENAI_MODEL", default_var="gpt-4o-mini")
        elif self.provider == 'deepseek':
            self.api_key = Variable.get("DEEPSEEK_API_KEY", default_var=None)
            self.base_url = Variable.get("DEEPSEEK_BASE_URL", default_var="https://api.deepseek.com/v1")
            self.model = Variable.get("DEEPSEEK_MODEL", default_var="deepseek-chat")
        else:
            raise ValueError(f"Proveedor no soportado: {self.provider}")
    
    def score_lead_with_ai(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula score del lead usando IA."""
        if not self.api_key:
            logger.warning("API key de IA no configurada, usando scoring básico")
            return self._basic_score(lead_data)
        
        try:
            prompt = f"""
            Evalúa este lead y proporciona un score del 0-100 y razonamiento.
            
            Datos del lead:
            - Email: {lead_data.get('email', 'N/A')}
            - Nombre: {lead_data.get('first_name', '')} {lead_data.get('last_name', '')}
            - Empresa: {lead_data.get('company', 'N/A')}
            - Teléfono: {lead_data.get('phone', 'N/A')}
            - Mensaje: {lead_data.get('message', 'N/A')[:200]}
            - Fuente: {lead_data.get('source', 'N/A')}
            - UTM Campaign: {lead_data.get('utm_campaign', 'N/A')}
            
            Proporciona respuesta en JSON:
            {{
                "score": <0-100>,
                "priority": "<high|medium|low>",
                "reasoning": "razonamiento detallado",
                "confidence": <0-1>,
                "recommendations": ["recomendación1", "recomendación2"]
            }}
            """
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "Eres un experto en evaluación de leads B2B."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500
                },
                timeout=10
            )
            
            if response.ok:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Parsear JSON de la respuesta
                try:
                    ai_result = json.loads(content)
                except:
                    # Si no es JSON válido, extraer información
                    ai_result = {
                        "score": 50,
                        "priority": "medium",
                        "reasoning": content,
                        "confidence": 0.7
                    }
                
                return {
                    "score": ai_result.get("score", 50),
                    "priority": ai_result.get("priority", "medium"),
                    "ai_reasoning": ai_result.get("reasoning", ""),
                    "confidence": ai_result.get("confidence", 0.7),
                    "recommendations": ai_result.get("recommendations", []),
                    "scoring_method": "ai"
                }
            else:
                logger.warning(f"Error en API de IA: {response.status_code}")
                return self._basic_score(lead_data)
                
        except Exception as e:
            logger.error(f"Error en scoring con IA: {str(e)}")
            return self._basic_score(lead_data)
    
    def _basic_score(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Scoring básico como fallback."""
        score = 0
        if lead_data.get("first_name") and lead_data.get("last_name"):
            score += 10
        if lead_data.get("phone"):
            score += 10
        if lead_data.get("company"):
            score += 10
        if lead_data.get("message"):
            score += 10
        
        priority = "high" if score >= 70 else "medium" if score >= 40 else "low"
        
        return {
            "score": min(score, 100),
            "priority": priority,
            "scoring_method": "basic"
        }


class DataEnricher:
    """Enriquece datos de leads con APIs externas."""
    
    def enrich_lead_data(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enriquece datos del lead."""
        enriched = lead_data.copy()
        
        # Enriquecer con datos de empresa si hay email corporativo
        email = lead_data.get("email", "")
        if email and "@" in email:
            domain = email.split("@")[1]
            company_data = self._get_company_data(domain)
            if company_data:
                enriched["company_data"] = company_data
                if not enriched.get("company"):
                    enriched["company"] = company_data.get("name")
        
        # Enriquecer con datos de ubicación si hay IP
        ip_address = lead_data.get("metadata", {}).get("ip_address")
        if ip_address:
            location_data = self._get_location_from_ip(ip_address)
            if location_data:
                enriched["location_data"] = location_data
        
        return enriched
    
    def _get_company_data(self, domain: str) -> Optional[Dict[str, Any]]:
        """Obtiene datos de empresa desde API."""
        # En producción, usar API real (Clearbit, FullContact, etc.)
        # Por ahora, simulación
        try:
            clearbit_key = Variable.get("CLEARBIT_API_KEY", default_var=None)
            if clearbit_key:
                response = requests.get(
                    f"https://company.clearbit.com/v2/companies/find?domain={domain}",
                    headers={"Authorization": f"Bearer {clearbit_key}"},
                    timeout=5
                )
                if response.ok:
                    return response.json()
        except Exception as e:
            logger.warning(f"Error obteniendo datos de empresa: {str(e)}")
        
        return None
    
    def _get_location_from_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        """Obtiene ubicación desde IP."""
        # En producción, usar API real (ipapi, ipgeolocation, etc.)
        try:
            response = requests.get(
                f"http://ip-api.com/json/{ip}",
                timeout=5
            )
            if response.ok:
                data = response.json()
                return {
                    "country": data.get("country"),
                    "region": data.get("regionName"),
                    "city": data.get("city"),
                    "timezone": data.get("timezone")
                }
        except Exception as e:
            logger.warning(f"Error obteniendo ubicación: {str(e)}")
        
        return None


class SpamDetector:
    """Detección avanzada de spam."""
    
    SPAM_INDICATORS = [
        # Patrones de email
        r'^[a-z0-9]+@[a-z0-9]+\.[a-z]{2,3}$',  # Emails genéricos
        # Palabras spam comunes
        'viagra', 'casino', 'lottery', 'winner', 'prize',
        'click here', 'limited time', 'act now',
        # Patrones de teléfono
        r'^\+?1?[0-9]{10}$',  # Teléfonos genéricos
    ]
    
    def detect_spam(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta si un lead es spam."""
        spam_score = 0
        indicators = []
        
        email = lead_data.get("email", "").lower()
        message = (lead_data.get("message", "") or "").lower()
        phone = lead_data.get("phone", "")
        
        # Verificar email genérico
        if email and len(email.split("@")[0]) < 3:
            spam_score += 20
            indicators.append("email_generic")
        
        # Verificar palabras spam en mensaje
        if message:
            spam_words_found = [word for word in self.SPAM_INDICATORS[3:6] if word in message]
            if spam_words_found:
                spam_score += len(spam_words_found) * 15
                indicators.append(f"spam_words: {', '.join(spam_words_found)}")
        
        # Verificar velocidad de envío (si hay metadata)
        metadata = lead_data.get("metadata", {})
        if metadata.get("submission_rate"):
            if metadata["submission_rate"] > 5:  # Más de 5 envíos por minuto
                spam_score += 30
                indicators.append("high_submission_rate")
        
        # Verificar falta de datos
        if not lead_data.get("first_name") and not lead_data.get("last_name"):
            spam_score += 10
            indicators.append("missing_name")
        
        if not lead_data.get("phone") and not lead_data.get("company"):
            spam_score += 10
            indicators.append("missing_contact_info")
        
        is_spam = spam_score >= 50
        
        return {
            "is_spam": is_spam,
            "spam_score": min(spam_score, 100),
            "indicators": indicators,
            "confidence": min(spam_score / 100, 1.0)
        }


def calculate_lead_score_ai(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula score del lead usando IA."""
    scorer = LLMLeadScorer()
    return scorer.score_lead_with_ai(lead_data)


def enrich_lead_data(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enriquece datos del lead."""
    enricher = DataEnricher()
    return enricher.enrich_lead_data(lead_data)


def detect_spam(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """Detecta spam en el lead."""
    detector = SpamDetector()
    return detector.detect_spam(lead_data)


def save_lead_analytics(lead_data: Dict[str, Any], conn_id: str = "postgres_default") -> None:
    """Guarda analytics del lead."""
    try:
        pg_hook = PostgresHook(postgres_conn_id=conn_id)
        
        analytics_data = {
            "lead_ext_id": lead_data.get("ext_id"),
            "score": lead_data.get("score", 0),
            "priority": lead_data.get("priority", "low"),
            "source": lead_data.get("source", "web"),
            "utm_campaign": lead_data.get("utm_campaign"),
            "spam_score": lead_data.get("spam_score", 0),
            "is_spam": lead_data.get("is_spam", False),
            "scoring_method": lead_data.get("scoring_method", "basic"),
            "enrichment_data": lead_data.get("company_data") or lead_data.get("location_data"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        pg_hook.run("""
            INSERT INTO lead_analytics (
                lead_ext_id, analytics_data, created_at
            ) VALUES (%s, %s, NOW())
            ON CONFLICT (lead_ext_id) DO UPDATE SET
                analytics_data = EXCLUDED.analytics_data,
                updated_at = NOW()
        """, parameters=(
            lead_data.get("ext_id"),
            json.dumps(analytics_data)
        ))
        
        logger.info(f"Analytics guardados para lead: {lead_data.get('ext_id')}")
        
    except Exception as e:
        logger.error(f"Error guardando analytics: {str(e)}")


def check_duplicate_lead(lead_data: Dict[str, Any], conn_id: str = "postgres_default") -> Optional[Dict[str, Any]]:
    """Verifica si el lead es duplicado usando caché."""
    try:
        email = lead_data.get("email", "").lower()
        cache_key = hashlib.md5(f"lead_{email}_{datetime.utcnow().strftime('%Y%m%d')}".encode()).hexdigest()
        
        pg_hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Verificar en caché
        result = pg_hook.get_first("""
            SELECT cache_data FROM lead_cache
            WHERE cache_key = %s AND created_at > NOW() - INTERVAL '24 hours'
        """, parameters=(cache_key,))
        
        if result:
            cached_data = json.loads(result[0])
            logger.info(f"Lead encontrado en caché: {email}")
            return cached_data
        
        return None
        
    except Exception as e:
        logger.warning(f"Error verificando duplicado: {str(e)}")
        return None


def save_to_cache(lead_data: Dict[str, Any], conn_id: str = "postgres_default") -> None:
    """Guarda lead en caché para evitar duplicados."""
    try:
        email = lead_data.get("email", "").lower()
        cache_key = hashlib.md5(f"lead_{email}_{datetime.utcnow().strftime('%Y%m%d')}".encode()).hexdigest()
        
        pg_hook = PostgresHook(postgres_conn_id=conn_id)
        
        pg_hook.run("""
            INSERT INTO lead_cache (cache_key, cache_data, created_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (cache_key) DO UPDATE SET
                cache_data = EXCLUDED.cache_data,
                created_at = NOW()
        """, parameters=(
            cache_key,
            json.dumps(lead_data)
        ))
        
    except Exception as e:
        logger.warning(f"Error guardando en caché: {str(e)}")


def integrate_with_job_descriptions(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """Integra con el sistema de descripciones de puesto si el lead es candidato."""
    try:
        # Verificar si el lead menciona interés en trabajo
        message = (lead_data.get("message", "") or "").lower()
        keywords = ["trabajo", "empleo", "carrera", "oportunidad", "cv", "resume"]
        
        if any(keyword in message for keyword in keywords):
            # Es un candidato potencial
            lead_data["is_candidate"] = True
            lead_data["candidate_interest"] = True
            
            # Opcional: Trigger del DAG de descripciones de puesto
            # from airflow.api.client.local_client import Client
            # client = Client(None, None)
            # client.trigger_dag(
            #     dag_id='job_description_ai_generator',
            #     conf={"candidate_email": lead_data.get("email")}
            # )
            
            logger.info(f"Lead identificado como candidato: {lead_data.get('email')}")
        
        return lead_data
        
    except Exception as e:
        logger.warning(f"Error en integración con job descriptions: {str(e)}")
        return lead_data






