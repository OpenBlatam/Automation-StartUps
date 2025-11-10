#!/usr/bin/env python3
"""
Chatbot para SaaS de IA Aplicado al Marketing
Proporciona respuestas automáticas sobre el SaaS de IA para marketing.
Escala consultas complejas a agentes humanos cuando es necesario.

Mejoras incluidas:
- Logging estructurado
- Persistencia de conversaciones
- Métricas y estadísticas
- Manejo avanzado de errores
- Contexto de historial de conversación
- Validación mejorada de entrada
"""

import re
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import traceback


class IntentType(Enum):
    """Tipos de intenciones detectadas"""
    INFO_PRODUCTO = "info_producto"
    FUNCIONALIDADES = "funcionalidades"
    PRECIO = "precio"
    PRUEBA_GRATIS = "prueba_gratis"
    REGISTRO = "registro"
    INTEGRACIONES = "integraciones"
    CASOS_USO = "casos_uso"
    SEGURIDAD = "seguridad"
    SOPORTE_TECNICO = "soporte_tecnico"
    FACTURACION = "facturacion"
    ACTUALIZACION = "actualizacion"
    API = "api"
    OTRO = "otro"


@dataclass
class ChatbotResponse:
    """Respuesta del chatbot"""
    message: str
    confidence: float
    intent: str
    requires_escalation: bool
    escalation_reason: Optional[str] = None
    suggested_actions: Optional[List[str]] = None
    faq_matched: Optional[str] = None
    processing_time: Optional[float] = None


@dataclass
class ChatbotMetrics:
    """Métricas del chatbot"""
    total_messages: int = 0
    total_escalations: int = 0
    intent_counts: Dict[str, int] = None
    average_confidence: float = 0.0
    average_processing_time: float = 0.0
    faq_matches: int = 0
    
    def __post_init__(self):
        if self.intent_counts is None:
            self.intent_counts = defaultdict(int)


class SaaSIAMarketingChatbot:
    """
    Chatbot especializado en responder preguntas sobre el SaaS de IA para Marketing.
    """
    
    def __init__(self, enable_logging: bool = True, persist_conversations: bool = True, 
                 conversation_dir: str = "chatbot_conversations"):
        """
        Inicializa el chatbot con base de conocimiento.
        
        Args:
            enable_logging: Habilita logging estructurado
            persist_conversations: Guarda conversaciones en archivos JSON
            conversation_dir: Directorio para guardar conversaciones
        """
        self.faqs = self._load_faqs()
        self.features = self._load_features()
        self.integrations = self._load_integrations()
        self.metrics = ChatbotMetrics()
        self.enable_logging = enable_logging
        self.persist_conversations = persist_conversations
        self.conversation_dir = Path(conversation_dir)
        
        # Configurar logging
        if enable_logging:
            self._setup_logging()
        
        # Crear directorio de conversaciones si no existe
        if persist_conversations:
            self.conversation_dir.mkdir(exist_ok=True)
        
        self.logger.info("Chatbot inicializado correctamente")
        
    def _load_faqs(self) -> List[Dict]:
        """Carga las preguntas frecuentes sobre el SaaS"""
        return [
            {
                "id": "faq_001",
                "category": "informacion_general",
                "question": "¿Qué es el SaaS de IA para Marketing?",
                "answer": "Nuestro SaaS de IA para Marketing es una plataforma integral que utiliza inteligencia artificial para optimizar todas las facetas de tu estrategia de marketing digital. La plataforma automatiza tareas, analiza datos en tiempo real, personaliza campañas y predice resultados para maximizar tu ROI.\n\n🎯 Beneficios principales:\n• Automatización inteligente de campañas\n• Análisis predictivo de audiencias\n• Personalización a escala\n• Optimización de presupuestos en tiempo real\n• Generación automática de contenido\n• Análisis de sentimiento y tendencias",
                "keywords": ["qué es", "información", "producto", "plataforma", "saaS"]
            },
            {
                "id": "faq_002",
                "category": "funcionalidades",
                "question": "¿Qué funcionalidades incluye?",
                "answer": "Nuestro SaaS incluye las siguientes funcionalidades principales:\n\n📊 Análisis y Predicción:\n• Análisis predictivo de audiencias\n• Predicción de conversión\n• Análisis de sentimiento en redes sociales\n• Identificación de tendencias\n\n🎨 Generación de Contenido:\n• Generación automática de copy para anuncios\n• Creación de imágenes con IA\n• Optimización de headlines\n• Sugerencias de contenido\n\n📈 Optimización de Campañas:\n• Optimización automática de pujas\n• Segmentación inteligente\n• A/B testing automatizado\n• Gestión multi-canal\n\n📧 Email Marketing:\n• Personalización dinámica\n• Optimización de horarios de envío\n• Predicción de engagement\n• Automatización de secuencias\n\n📱 Social Media:\n• Programación inteligente\n• Análisis de competencia\n• Recomendaciones de hashtags\n• Gestión de respuestas automatizadas",
                "keywords": ["funcionalidades", "características", "features", "qué incluye", "herramientas"]
            },
            {
                "id": "faq_003",
                "category": "precio",
                "question": "¿Cuánto cuesta el servicio?",
                "answer": "Ofrecemos planes flexibles adaptados a diferentes necesidades:\n\n🚀 Plan Starter - $99/mes:\n• Hasta 10,000 contactos\n• 5 campañas simultáneas\n• Análisis básico\n• Soporte por email\n\n💼 Plan Professional - $299/mes:\n• Hasta 50,000 contactos\n• Campañas ilimitadas\n• Análisis avanzado + IA\n• Integraciones premium\n• Soporte prioritario\n\n🏢 Plan Enterprise - Personalizado:\n• Contactos ilimitados\n• Todas las funcionalidades\n• API completa\n• Soporte 24/7 dedicado\n• Onboarding personalizado\n• SLA garantizado\n\n💡 Todos los planes incluyen prueba gratuita de 14 días sin tarjeta de crédito.",
                "keywords": ["precio", "costo", "tarifa", "plan", "pago", "cuánto"]
            },
            {
                "id": "faq_004",
                "category": "prueba_gratis",
                "question": "¿Ofrecen prueba gratuita?",
                "answer": "¡Sí! Ofrecemos una prueba gratuita de 14 días con acceso completo a todas las funcionalidades del plan que elijas. Durante la prueba podrás:\n\n✅ Probar todas las características\n✅ Importar tus datos\n✅ Crear campañas reales\n✅ Acceder a soporte completo\n✅ Sin tarjeta de crédito requerida\n\nPara comenzar tu prueba gratuita:\n1. Visita: www.ejemplo.com/trial\n2. Crea tu cuenta (solo email)\n3. Selecciona el plan que quieres probar\n4. ¡Comienza a usar la plataforma inmediatamente!\n\nAl finalizar los 14 días, puedes elegir continuar con un plan de pago o cancelar sin compromiso.",
                "keywords": ["prueba", "gratis", "trial", "demo", "test", "gratuito"]
            },
            {
                "id": "faq_005",
                "category": "registro",
                "question": "¿Cómo me registro?",
                "answer": "Registrarse es muy sencillo:\n\n1. Visita: www.ejemplo.com/signup\n2. Completa el formulario con:\n   • Nombre y apellido\n   • Email corporativo\n   • Nombre de tu empresa\n   • Contraseña segura\n3. Verifica tu email (revisa tu bandeja de entrada)\n4. Selecciona tu plan o inicia la prueba gratuita\n5. Completa el onboarding guiado (5 minutos)\n\nUna vez registrado, tendrás acceso inmediato a la plataforma. Si tienes problemas durante el registro, contacta a registro@ejemplo.com",
                "keywords": ["registro", "registrar", "crear cuenta", "signup", "inscripción"]
            },
            {
                "id": "faq_006",
                "category": "integraciones",
                "question": "¿Con qué plataformas se integra?",
                "answer": "Nuestro SaaS se integra con más de 50 plataformas populares:\n\n📧 Email Marketing:\n• Mailchimp, SendGrid, Constant Contact\n• Campaign Monitor, AWeber\n\n📱 Redes Sociales:\n• Facebook Ads, Instagram Ads\n• LinkedIn Ads, Twitter Ads\n• Google Ads, TikTok Ads\n\n🛒 E-commerce:\n• Shopify, WooCommerce\n• Magento, BigCommerce\n\n📊 Analytics:\n• Google Analytics, Adobe Analytics\n• Mixpanel, Amplitude\n\n💼 CRM:\n• Salesforce, HubSpot\n• Pipedrive, Zoho CRM\n\n🔧 Otras:\n• Zapier (1000+ apps)\n• Webhooks personalizados\n• API REST completa\n\nTodas las integraciones se configuran en menos de 5 minutos desde el panel de control.",
                "keywords": ["integración", "integraciones", "conectar", "plataformas", "apis"]
            },
            {
                "id": "faq_007",
                "category": "casos_uso",
                "question": "¿Para qué casos de uso es ideal?",
                "answer": "Nuestro SaaS es ideal para:\n\n🎯 E-commerce:\n• Optimización de campañas de productos\n• Retargeting inteligente\n• Personalización de recomendaciones\n• Análisis de abandono de carrito\n\n📱 Agencias de Marketing:\n• Gestión de múltiples clientes\n• Reportes automatizados\n• Optimización de presupuestos\n• Análisis comparativo\n\n🏢 Empresas B2B:\n• Lead nurturing automatizado\n• Scoring de leads con IA\n• Optimización de funnels\n• Análisis de pipeline\n\n📰 Medios y Contenido:\n• Optimización de headlines\n• Distribución inteligente\n• Análisis de engagement\n• Recomendaciones de contenido\n\n💼 Startups:\n• Marketing con presupuesto limitado\n• Automatización desde el día 1\n• Escalabilidad rápida\n• ROI medible",
                "keywords": ["casos de uso", "para qué", "ideal", "usos", "aplicaciones"]
            },
            {
                "id": "faq_008",
                "category": "seguridad",
                "question": "¿Es seguro? ¿Cómo protegen mis datos?",
                "answer": "La seguridad es nuestra máxima prioridad:\n\n🔒 Certificaciones:\n• SOC 2 Type II certificado\n• ISO 27001\n• GDPR compliant\n• CCPA compliant\n\n🛡️ Medidas de seguridad:\n• Encriptación end-to-end (AES-256)\n• Autenticación de dos factores (2FA)\n• Backups automáticos diarios\n• Monitoreo 24/7\n• Firewall y protección DDoS\n\n👥 Privacidad:\n• No vendemos ni compartimos tus datos\n• Control total sobre tus datos\n• Exportación de datos en cualquier momento\n• Eliminación completa al cancelar\n\n📋 Cumplimiento:\n• Acuerdos de confidencialidad (NDA)\n• Contratos de procesamiento de datos (DPA)\n• Reportes de seguridad regulares\n\nPuedes revisar nuestra política de privacidad completa en: www.ejemplo.com/privacy",
                "keywords": ["seguridad", "privacidad", "datos", "protección", "compliance", "gdpr"]
            },
            {
                "id": "faq_009",
                "category": "soporte_tecnico",
                "question": "¿Qué tipo de soporte ofrecen?",
                "answer": "Ofrecemos múltiples niveles de soporte:\n\n📚 Recursos de autoayuda:\n• Base de conocimiento con 500+ artículos\n• Video tutoriales paso a paso\n• Webinars semanales\n• Comunidad de usuarios\n\n💬 Soporte directo:\n• Chat en vivo (Lun-Vie, 9:00-18:00 GMT)\n• Email: soporte@ejemplo.com (respuesta en 4h)\n• Soporte prioritario (planes Professional+)\n• Soporte 24/7 (plan Enterprise)\n\n🎓 Onboarding:\n• Sesión de onboarding gratuita\n• Guías personalizadas\n• Consultoría estratégica (Enterprise)\n\n🐛 Soporte técnico:\n• Resolución de bugs en 24h\n• Asistencia con integraciones\n• Optimización de rendimiento\n• Consultoría técnica avanzada",
                "keywords": ["soporte", "ayuda", "asistencia", "problema", "técnico", "contacto"]
            },
            {
                "id": "faq_010",
                "category": "facturacion",
                "question": "¿Cómo funciona la facturación?",
                "answer": "Nuestra facturación es transparente y flexible:\n\n💳 Métodos de pago:\n• Tarjeta de crédito/débito (Visa, Mastercard, Amex)\n• Transferencia bancaria\n• PayPal\n• Facturación empresarial (Enterprise)\n\n📅 Ciclos de facturación:\n• Mensual (facturación el mismo día cada mes)\n• Anual (con 20% de descuento)\n\n📊 Facturación por uso:\n• Los contactos se facturan mensualmente\n• Si superas tu límite, puedes actualizar el plan\n• No hay cargos por exceso automáticos\n• Notificaciones antes de alcanzar límites\n\n🧾 Facturas:\n• Facturas automáticas por email\n• Portal de facturación con historial\n• Facturas en PDF descargables\n• Soporte para múltiples métodos de pago\n\nPara consultas de facturación: facturacion@ejemplo.com",
                "keywords": ["facturación", "pago", "billing", "factura", "cobro", "tarjeta"]
            },
            {
                "id": "faq_011",
                "category": "actualizacion",
                "question": "¿Con qué frecuencia actualizan la plataforma?",
                "answer": "Mantenemos la plataforma actualizada constantemente:\n\n🔄 Actualizaciones regulares:\n• Mejoras menores: Semanales\n• Nuevas funcionalidades: Mensuales\n• Actualizaciones de IA: Trimestrales\n• Mejoras de seguridad: Continuas\n\n📢 Comunicación:\n• Notificaciones en la plataforma\n• Email con changelog mensual\n• Webinars de nuevas funcionalidades\n• Roadmap público disponible\n\n✨ Nuevas características:\n• Basadas en feedback de usuarios\n• Tendencias del mercado\n• Avances en IA\n• Mejores prácticas de la industria\n\n🔧 Mantenimiento:\n• Ventanas de mantenimiento programadas\n• Notificación con 48h de anticipación\n• Horarios fuera de pico\n• Tiempo de inactividad mínimo (<15 min)\n\nPuedes ver el roadmap en: www.ejemplo.com/roadmap",
                "keywords": ["actualización", "update", "nuevas funciones", "mejoras", "roadmap"]
            },
            {
                "id": "faq_012",
                "category": "api",
                "question": "¿Tienen API disponible?",
                "answer": "Sí, ofrecemos una API REST completa y bien documentada:\n\n🔌 Características de la API:\n• RESTful API con JSON\n• Autenticación OAuth 2.0\n• Rate limiting: 1000 requests/minuto\n• Webhooks para eventos en tiempo real\n• SDKs para Python, JavaScript, PHP, Ruby\n\n📚 Documentación:\n• Documentación interactiva (Swagger)\n• Ejemplos de código\n• Guías de integración\n• Sandbox para pruebas\n\n🎯 Casos de uso comunes:\n• Sincronización de datos\n• Automatización personalizada\n• Integraciones custom\n• Reportes programados\n• Webhooks para notificaciones\n\n💼 Disponibilidad:\n• Incluida en planes Professional y Enterprise\n• Límites según el plan\n• Soporte técnico para integraciones\n\nAccede a la documentación: api.ejemplo.com/docs",
                "keywords": ["api", "rest", "webhook", "integración", "desarrollador", "sdk"]
            }
        ]
    
    def _load_features(self) -> List[str]:
        """Carga lista de funcionalidades principales"""
        return [
            "Análisis predictivo de audiencias",
            "Generación automática de contenido",
            "Optimización de campañas en tiempo real",
            "Personalización a escala",
            "Email marketing inteligente",
            "Gestión de redes sociales",
            "A/B testing automatizado",
            "Análisis de sentimiento",
            "Predicción de conversión",
            "Optimización de presupuestos"
        ]
    
    def _load_integrations(self) -> List[str]:
        """Carga lista de integraciones disponibles"""
        return [
            "Mailchimp", "SendGrid", "Facebook Ads", "Google Ads",
            "Shopify", "Salesforce", "HubSpot", "Zapier"
        ]
    
    def _setup_logging(self):
        """Configura logging estructurado"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('chatbot_saas_ia_marketing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SaaSIAMarketingChatbot')
    
    def _save_conversation(self, conversation_id: str, messages: List[Dict]):
        """Guarda una conversación en un archivo JSON"""
        if not self.persist_conversations:
            return
        
        try:
            conversation_file = self.conversation_dir / f"{conversation_id}.json"
            conversation_data = {
                "conversation_id": conversation_id,
                "created_at": datetime.now().isoformat(),
                "message_count": len(messages),
                "messages": messages
            }
            
            with open(conversation_file, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            self.logger.debug(f"Conversación guardada: {conversation_id}")
        except Exception as e:
            self.logger.error(f"Error guardando conversación: {e}")
    
    def get_metrics(self) -> Dict:
        """Retorna métricas del chatbot"""
        return {
            "total_messages": self.metrics.total_messages,
            "total_escalations": self.metrics.total_escalations,
            "escalation_rate": (
                self.metrics.total_escalations / self.metrics.total_messages 
                if self.metrics.total_messages > 0 else 0
            ),
            "intent_distribution": dict(self.metrics.intent_counts),
            "average_confidence": self.metrics.average_confidence,
            "average_processing_time": self.metrics.average_processing_time,
            "faq_match_rate": (
                self.metrics.faq_matches / self.metrics.total_messages 
                if self.metrics.total_messages > 0 else 0
            )
        }
    
    def reset_metrics(self):
        """Reinicia las métricas"""
        self.metrics = ChatbotMetrics()
        self.logger.info("Métricas reiniciadas")
    
    def detect_intent(self, message: str, conversation_history: Optional[List[Dict]] = None) -> IntentType:
        """
        Detecta la intención del mensaje del usuario.
        Usa el historial de conversación para mejorar la detección.
        """
        message_lower = message.lower()
        
        # Si hay historial, considerar el contexto
        context = ""
        if conversation_history:
            user_messages = [
                msg.get('content', '') for msg in conversation_history[-6:] 
                if msg.get('role') == 'user'
            ]
            context = " ".join(user_messages).lower()
        
        patterns = {
            IntentType.INFO_PRODUCTO: [
                r"qué es", r"información", r"sobre.*producto", r"plataforma"
            ],
            IntentType.FUNCIONALIDADES: [
                r"funcionalidades", r"características", r"features", r"qué incluye", r"herramientas"
            ],
            IntentType.PRECIO: [
                r"precio", r"costo", r"cuánto", r"tarifa", r"plan", r"pago"
            ],
            IntentType.PRUEBA_GRATIS: [
                r"prueba", r"gratis", r"trial", r"demo", r"test"
            ],
            IntentType.REGISTRO: [
                r"registro", r"registrar", r"crear cuenta", r"signup", r"inscripción"
            ],
            IntentType.INTEGRACIONES: [
                r"integración", r"conectar", r"plataformas", r"api", r"zapier"
            ],
            IntentType.CASOS_USO: [
                r"casos de uso", r"para qué", r"ideal", r"usos", r"aplicaciones"
            ],
            IntentType.SEGURIDAD: [
                r"seguridad", r"privacidad", r"datos", r"protección", r"gdpr"
            ],
            IntentType.SOPORTE_TECNICO: [
                r"soporte", r"ayuda", r"problema", r"error", r"técnico"
            ],
            IntentType.FACTURACION: [
                r"facturación", r"billing", r"factura", r"cobro", r"pago"
            ],
            IntentType.ACTUALIZACION: [
                r"actualización", r"update", r"nuevas funciones", r"mejoras"
            ],
            IntentType.API: [
                r"api", r"rest", r"webhook", r"desarrollador", r"sdk"
            ]
        }
        
        # Buscar coincidencias (priorizar mensaje actual, luego contexto)
        intent_scores = defaultdict(float)
        
        for intent, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, message_lower):
                    intent_scores[intent] += 2.0
                elif context and re.search(pattern, context):
                    intent_scores[intent] += 0.5
        
        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        
        return IntentType.OTRO
    
    def search_faq(self, message: str) -> Optional[Dict]:
        """Busca la FAQ más relevante para el mensaje"""
        message_lower = message.lower()
        message_words = set(re.findall(r'\b\w+\b', message_lower))
        
        best_match = None
        best_score = 0
        
        for faq in self.faqs:
            score = 0
            faq_keywords = [kw.lower() for kw in faq.get('keywords', [])]
            
            for keyword in faq_keywords:
                if keyword in message_lower:
                    score += 2
            
            faq_text = f"{faq['question']} {faq['answer']}".lower()
            faq_words = set(re.findall(r'\b\w+\b', faq_text))
            common_words = message_words.intersection(faq_words)
            score += len(common_words) * 0.5
            
            if faq['question'].lower() in message_lower:
                score += 5
            
            if score > best_score:
                best_score = score
                best_match = faq
        
        if best_score >= 2:
            return best_match
        
        return None
    
    def check_escalation_needed(self, message: str, intent: IntentType) -> Tuple[bool, Optional[str]]:
        """Verifica si la consulta necesita escalación a un agente humano"""
        message_lower = message.lower()
        
        escalation_patterns = [
            r"reembolso", r"devolución", r"cancelar", r"cancelación",
            r"queja", r"reclamo", r"problema.*pago", r"error.*pago",
            r"no.*funciona", r"no.*puedo", r"bug", r"error.*técnico",
            r"urgente", r"emergencia", r"crítico", r"datos.*perdidos"
        ]
        
        for pattern in escalation_patterns:
            if re.search(pattern, message_lower):
                return True, "Consulta requiere atención personalizada de un agente"
        
        if intent == IntentType.OTRO:
            return True, "Consulta no identificada, requiere revisión humana"
        
        negative_patterns = [
            r"no.*ayuda", r"no.*sirve", r"no.*entiendo", r"confuso", r"complejo"
        ]
        
        for pattern in negative_patterns:
            if re.search(pattern, message_lower):
                return True, "Usuario indica dificultad, mejor atención personalizada"
        
        return False, None
    
    def generate_response(self, message: str, conversation_history: Optional[List[Dict]] = None) -> ChatbotResponse:
        """
        Genera una respuesta para el mensaje del usuario.
        
        Args:
            message: Mensaje del usuario
            conversation_history: Historial de conversación para contexto
        
        Returns:
            ChatbotResponse con la respuesta generada
        """
        start_time = datetime.now()
        
        try:
            # Validar entrada
            if not message or not message.strip():
                raise ValueError("El mensaje no puede estar vacío")
            
            if len(message) > 2000:
                raise ValueError("El mensaje es demasiado largo (máximo 2000 caracteres)")
            
            intent = self.detect_intent(message, conversation_history)
            faq_match = self.search_faq(message)
            needs_escalation, escalation_reason = self.check_escalation_needed(message, intent)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if needs_escalation:
                self.metrics.total_escalations += 1
                if self.enable_logging:
                    self.logger.info(f"Escalación requerida: {escalation_reason}")
                
                return ChatbotResponse(
                message=(
                    "Entiendo tu consulta. Para brindarte la mejor asistencia y resolver tu "
                    "situación de manera personalizada, voy a conectarte con uno de nuestros "
                    "agentes especializados.\n\n"
                    "Un miembro de nuestro equipo se pondrá en contacto contigo en breve.\n\n"
                    "Mientras tanto, puedes contactarnos directamente en:\n"
                    "📧 Email: soporte@ejemplo.com\n"
                    "💬 Chat en vivo: disponible en nuestra plataforma\n"
                    "📞 Teléfono: +1 (555) 123-4567 (Lun-Vie, 9:00-18:00 GMT)\n"
                    "🆘 Soporte 24/7: Disponible para clientes Enterprise"
                ),
                confidence=0.9,
                intent=intent.value,
                requires_escalation=True,
                escalation_reason=escalation_reason,
                suggested_actions=[
                    "Contactar por email",
                    "Iniciar chat en vivo",
                    "Ver base de conocimiento",
                    "Programar llamada"
                ],
                processing_time=processing_time
            )
        
        if faq_match:
            self.metrics.faq_matches += 1
            response_message = faq_match['answer']
            
            # Agregar información adicional según el intent
            if intent == IntentType.FUNCIONALIDADES:
                response_message += "\n\n💡 ¿Te gustaría conocer más detalles sobre alguna funcionalidad específica?"
            elif intent == IntentType.INTEGRACIONES:
                response_message += "\n\n🔗 ¿Necesitas ayuda configurando alguna integración específica?"
            
            return ChatbotResponse(
                message=response_message,
                confidence=0.85,
                intent=intent.value,
                requires_escalation=False,
                suggested_actions=[
                    "¿Te ayudó esta respuesta?",
                    "¿Tienes otra pregunta?",
                    "Iniciar prueba gratuita",
                    "Contactar con agente humano"
                ],
                faq_matched=faq_match.get('id'),
                processing_time=processing_time
            )
        
        return ChatbotResponse(
            message=(
                "Gracias por tu consulta. Puedo ayudarte con:\n\n"
                "• Información sobre el SaaS de IA para Marketing\n"
                "• Funcionalidades y características\n"
                "• Precios y planes\n"
                "• Prueba gratuita de 14 días\n"
                "• Integraciones disponibles\n"
                "• Seguridad y privacidad\n"
                "• Soporte técnico\n\n"
                "Si tu consulta es más específica o compleja, puedo conectarte con un agente "
                "humano que podrá ayudarte mejor. ¿Te gustaría que te conecte con nuestro equipo?"
            ),
            confidence=0.5,
            intent=intent.value,
            requires_escalation=False,
            suggested_actions=[
                "Ver funcionalidades",
                "Iniciar prueba gratuita",
                "Ver precios",
                "Contactar con agente humano"
            ],
            processing_time=processing_time
        )
        
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Error procesando mensaje: {str(e)}"
            if self.enable_logging:
                self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            return ChatbotResponse(
                message=(
                    "Lo siento, ocurrió un error al procesar tu mensaje. "
                    "Por favor, intenta reformular tu pregunta o contacta directamente "
                    "con nuestro equipo de soporte en soporte@ejemplo.com"
                ),
                confidence=0.0,
                intent="error",
                requires_escalation=True,
                escalation_reason=error_msg,
                processing_time=processing_time
            )
    
    def process_message(self, user_message: str, conversation_history: Optional[List[Dict]] = None,
                       conversation_id: Optional[str] = None) -> Dict:
        """
        Procesa un mensaje del usuario y retorna la respuesta del chatbot.
        
        Args:
            user_message: Mensaje del usuario
            conversation_history: Historial de conversación (opcional)
            conversation_id: ID único de la conversación (opcional)
        
        Returns:
            Dict con la respuesta del chatbot
        """
        # Generar ID de conversación si no existe
        if not conversation_id:
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(user_message) % 10000}"
        
        # Validación básica
        if not user_message or not user_message.strip():
            return {
                "error": "El mensaje no puede estar vacío",
                "conversation_id": conversation_id
            }
        
        # Procesar mensaje
        response = self.generate_response(user_message, conversation_history)
        
        # Actualizar métricas
        self.metrics.total_messages += 1
        self.metrics.intent_counts[response.intent] += 1
        
        # Actualizar promedio de confianza
        total_conf = self.metrics.average_confidence * (self.metrics.total_messages - 1)
        self.metrics.average_confidence = (total_conf + response.confidence) / self.metrics.total_messages
        
        # Actualizar promedio de tiempo de procesamiento
        if response.processing_time:
            total_time = self.metrics.average_processing_time * (self.metrics.total_messages - 1)
            self.metrics.average_processing_time = (total_time + response.processing_time) / self.metrics.total_messages
        
        # Logging
        if self.enable_logging:
            self.logger.info(
                f"Mensaje procesado - Intent: {response.intent}, "
                f"Confidence: {response.confidence:.2f}, "
                f"Escalation: {response.requires_escalation}"
            )
        
        # Preparar respuesta
        result = {
            "response": response.message,
            "confidence": response.confidence,
            "intent": response.intent,
            "requires_escalation": response.requires_escalation,
            "escalation_reason": response.escalation_reason,
            "suggested_actions": response.suggested_actions,
            "faq_matched": response.faq_matched,
            "processing_time": response.processing_time,
            "timestamp": datetime.now().isoformat(),
            "conversation_id": conversation_id
        }
        
        # Guardar conversación si está habilitado
        if self.persist_conversations and conversation_history is not None:
            updated_history = conversation_history + [
                {"role": "user", "content": user_message, "timestamp": datetime.now().isoformat()},
                {"role": "assistant", "content": response.message, "timestamp": datetime.now().isoformat()}
            ]
            self._save_conversation(conversation_id, updated_history)
        
        return result


def main():
    """Función principal para pruebas interactivas"""
    chatbot = SaaSIAMarketingChatbot(enable_logging=True, persist_conversations=True)
    
    print("=" * 60)
    print("🤖 Chatbot - SaaS de IA para Marketing")
    print("=" * 60)
    print("\n¡Hola! Soy tu asistente virtual. Puedo ayudarte con:")
    print("• Información sobre el SaaS de IA para Marketing")
    print("• Funcionalidades y características")
    print("• Precios, planes y prueba gratuita")
    print("• Integraciones y casos de uso")
    print("• Soporte técnico y seguridad")
    print("\nComandos especiales:")
    print("• 'salir' - Terminar conversación")
    print("• 'métricas' - Ver estadísticas del chatbot")
    print("• 'reset métricas' - Reiniciar estadísticas")
    print("\nEscribe 'salir' para terminar la conversación.\n")
    
    conversation_history = []
    conversation_id = f"interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    while True:
        user_input = input("Tú: ").strip()
        
        if user_input.lower() in ['salir', 'exit', 'quit', 'adiós']:
            print("\n¡Gracias por usar nuestro chatbot! Que tengas un excelente día. 👋")
            # Mostrar métricas finales
            metrics = chatbot.get_metrics()
            print(f"\n📊 Resumen de la sesión:")
            print(f"   • Mensajes procesados: {metrics['total_messages']}")
            print(f"   • Escalaciones: {metrics['total_escalations']}")
            print(f"   • Tasa de escalación: {metrics['escalation_rate']:.1%}")
            print(f"   • Confianza promedio: {metrics['average_confidence']:.2f}")
            break
        
        if not user_input:
            continue
        
        # Comandos especiales
        if user_input.lower() == 'métricas':
            metrics = chatbot.get_metrics()
            print("\n📊 Métricas del Chatbot:")
            print(f"   • Total mensajes: {metrics['total_messages']}")
            print(f"   • Total escalaciones: {metrics['total_escalations']}")
            print(f"   • Tasa de escalación: {metrics['escalation_rate']:.1%}")
            print(f"   • Confianza promedio: {metrics['average_confidence']:.2f}")
            print(f"   • Tiempo promedio: {metrics['average_processing_time']:.3f}s")
            print(f"   • Tasa de match FAQ: {metrics['faq_match_rate']:.1%}")
            print(f"   • Distribución de intenciones:")
            for intent, count in metrics['intent_distribution'].items():
                print(f"     - {intent}: {count}")
            print()
            continue
        
        if user_input.lower() == 'reset métricas':
            chatbot.reset_metrics()
            print("✅ Métricas reiniciadas\n")
            continue
        
        response = chatbot.process_message(user_input, conversation_history, conversation_id)
        
        if "error" in response:
            print(f"❌ Error: {response['error']}")
            continue
        
        print(f"\n🤖 Chatbot: {response['response']}")
        
        if response.get('suggested_actions'):
            print("\n💡 Acciones sugeridas:")
            for i, action in enumerate(response['suggested_actions'], 1):
                print(f"   {i}. {action}")
        
        if response.get('requires_escalation'):
            print(f"\n⚠️  Escalación: {response.get('escalation_reason', 'N/A')}")
        
        print(f"\n[Confianza: {response['confidence']:.2f} | Intención: {response['intent']} | "
              f"Tiempo: {response.get('processing_time', 0):.3f}s]\n")
        
        conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        conversation_history.append({
            "role": "assistant",
            "content": response['response'],
            "timestamp": response['timestamp']
        })


if __name__ == "__main__":
    main()

