#!/usr/bin/env python3
"""
Chatbot para IA Bulk - Generación de Documentos con una Sola Consulta
Proporciona respuestas automáticas sobre la IA Bulk que genera documentos completos.
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
    COMO_FUNCIONA = "como_funciona"
    TIPOS_DOCUMENTOS = "tipos_documentos"
    PRECIO = "precio"
    PRUEBA = "prueba"
    REGISTRO = "registro"
    CALIDAD = "calidad"
    FORMATOS = "formatos"
    PERSONALIZACION = "personalizacion"
    LIMITES = "limites"
    API = "api"
    SOPORTE = "soporte"
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


class IABulkDocumentosChatbot:
    """
    Chatbot especializado en responder preguntas sobre IA Bulk para generación de documentos.
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
        self.document_types = self._load_document_types()
        self.formats = self._load_formats()
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
        """Carga las preguntas frecuentes sobre IA Bulk"""
        return [
            {
                "id": "faq_001",
                "category": "informacion_general",
                "question": "¿Qué es IA Bulk para documentos?",
                "answer": "IA Bulk es una herramienta de inteligencia artificial revolucionaria que genera documentos completos y profesionales con una sola consulta. En lugar de escribir manualmente, simplemente describes lo que necesitas y nuestra IA crea el documento completo en segundos.\n\n🎯 Características principales:\n• Generación instantánea de documentos completos\n• Una sola consulta genera todo el documento\n• Múltiples tipos de documentos soportados\n• Calidad profesional lista para usar\n• Personalización y edición posterior\n• Exportación a múltiples formatos\n\n💡 Ejemplo: 'Crea un plan de marketing para una startup de tecnología' → Genera un documento completo de 10-15 páginas con estructura, contenido y formato profesional.",
                "keywords": ["qué es", "información", "producto", "ia bulk", "documentos"]
            },
            {
                "id": "faq_002",
                "category": "como_funciona",
                "question": "¿Cómo funciona? ¿Cómo genero un documento?",
                "answer": "El proceso es extremadamente simple:\n\n1️⃣ Escribe tu consulta:\n   Ejemplo: 'Crea un plan de negocios para una cafetería artesanal en el centro de la ciudad'\n\n2️⃣ La IA procesa tu solicitud:\n   • Analiza tu consulta\n   • Identifica el tipo de documento\n   • Genera estructura completa\n   • Crea contenido relevante y profesional\n\n3️⃣ Recibe tu documento:\n   • Documento completo en segundos\n   • Estructurado y formateado\n   • Listo para revisar y editar\n\n4️⃣ Personaliza (opcional):\n   • Edita secciones específicas\n   • Ajusta el tono y estilo\n   • Agrega información adicional\n   • Regenera partes si es necesario\n\n⏱️ Tiempo promedio: 10-30 segundos por documento\n📄 Longitud: 5-50 páginas según el tipo\n✨ Calidad: Profesional, lista para usar",
                "keywords": ["cómo funciona", "cómo usar", "proceso", "generar", "crear documento"]
            },
            {
                "id": "faq_003",
                "category": "tipos_documentos",
                "question": "¿Qué tipos de documentos puedo generar?",
                "answer": "Puedes generar más de 50 tipos diferentes de documentos:\n\n📋 Documentos de Negocio:\n• Planes de negocios\n• Propuestas comerciales\n• Informes ejecutivos\n• Análisis de mercado\n• Estrategias de marketing\n• Planes financieros\n\n📝 Documentos Académicos:\n• Ensayos y trabajos de investigación\n• Tesis y disertaciones\n• Resúmenes ejecutivos\n• Análisis de casos\n• Papers académicos\n\n📄 Documentos Legales:\n• Contratos básicos\n• Términos y condiciones\n• Políticas de privacidad\n• Acuerdos de servicio\n• Documentos corporativos\n\n📊 Documentos Técnicos:\n• Documentación técnica\n• Manuales de usuario\n• Guías de implementación\n• Especificaciones\n• Reportes técnicos\n\n📰 Contenido:\n• Artículos de blog\n• White papers\n• E-books\n• Guías y tutoriales\n• Contenido para redes sociales\n\n💼 Recursos Humanos:\n• Descripciones de puestos\n• Evaluaciones de desempeño\n• Planes de capacitación\n• Políticas de empresa",
                "keywords": ["tipos", "documentos", "qué puedo crear", "ejemplos", "categorías"]
            },
            {
                "id": "faq_004",
                "category": "precio",
                "question": "¿Cuánto cuesta? ¿Cómo funciona el precio?",
                "answer": "Ofrecemos planes flexibles basados en uso:\n\n🆓 Plan Gratuito:\n• 5 documentos/mes\n• Documentos hasta 10 páginas\n• Formatos básicos (PDF, DOCX)\n• Sin marca de agua\n\n💼 Plan Básico - $19/mes:\n• 50 documentos/mes\n• Documentos hasta 30 páginas\n• Todos los formatos\n• Prioridad en generación\n• Soporte por email\n\n🚀 Plan Pro - $49/mes:\n• 200 documentos/mes\n• Documentos ilimitados en longitud\n• Generación prioritaria\n• API access\n• Personalización avanzada\n• Soporte prioritario\n\n🏢 Plan Enterprise - Personalizado:\n• Documentos ilimitados\n• Generación en masa (bulk)\n• API completa\n• Integraciones personalizadas\n• SLA garantizado\n• Soporte dedicado 24/7\n• Onboarding personalizado\n\n💡 También ofrecemos créditos por uso (pay-as-you-go) para usuarios ocasionales.",
                "keywords": ["precio", "costo", "tarifa", "plan", "pago", "cuánto"]
            },
            {
                "id": "faq_005",
                "category": "prueba",
                "question": "¿Puedo probarlo antes de pagar?",
                "answer": "¡Por supuesto! Ofrecemos varias opciones para que pruebes el servicio:\n\n🎁 Plan Gratuito:\n• 5 documentos completamente gratis\n• Sin tarjeta de crédito\n• Acceso a todas las funcionalidades básicas\n• Sin límite de tiempo\n\n🆓 Prueba del Plan Pro:\n• 7 días gratis del plan Pro\n• 200 documentos durante la prueba\n• Todas las funcionalidades premium\n• Cancela cuando quieras\n\n💡 Demo Interactiva:\n• Prueba en nuestra página web sin registro\n• Genera 1 documento de ejemplo\n• Ve la calidad antes de registrarte\n\nPara comenzar tu prueba gratuita:\n1. Visita: www.ejemplo.com/trial\n2. Crea tu cuenta (solo email)\n3. ¡Comienza a generar documentos inmediatamente!\n\nNo se requiere tarjeta de crédito para el plan gratuito ni para la prueba.",
                "keywords": ["prueba", "gratis", "trial", "demo", "test", "gratuito"]
            },
            {
                "id": "faq_006",
                "category": "registro",
                "question": "¿Cómo me registro?",
                "answer": "Registrarse es muy rápido y sencillo:\n\n1. Visita: www.ejemplo.com/signup\n2. Completa el formulario:\n   • Email\n   • Contraseña\n   • Nombre (opcional)\n3. Verifica tu email (revisa tu bandeja de entrada)\n4. ¡Comienza a usar inmediatamente!\n\n⏱️ Tiempo total: Menos de 2 minutos\n✅ Sin tarjeta de crédito requerida para el plan gratuito\n🎁 Acceso inmediato a 5 documentos gratis\n\nSi tienes problemas durante el registro, contacta a registro@ejemplo.com y te ayudaremos en menos de 1 hora.",
                "keywords": ["registro", "registrar", "crear cuenta", "signup", "inscripción"]
            },
            {
                "id": "faq_007",
                "category": "calidad",
                "question": "¿Qué tan buena es la calidad de los documentos generados?",
                "answer": "La calidad de nuestros documentos es profesional y lista para usar:\n\n✨ Características de calidad:\n• Contenido relevante y coherente\n• Estructura profesional\n• Gramática y ortografía perfectas\n• Formato consistente\n• Estilo apropiado según el tipo de documento\n• Información actualizada\n\n📊 Métricas de calidad:\n• 95% de satisfacción de usuarios\n• 4.8/5 estrellas promedio\n• 90% de documentos usados sin edición\n• Revisión humana opcional disponible\n\n🎯 Garantía de calidad:\n• Si no estás satisfecho, regeneramos gratis\n• Revisión y edición ilimitadas\n• Mejora continua basada en feedback\n• Actualizaciones regulares del modelo\n\n💡 Tipos de documentos con mayor calidad:\n• Planes de negocios\n• Propuestas comerciales\n• Documentación técnica\n• Contenido de marketing\n• Documentos académicos\n\nLos documentos son generados usando modelos de IA de última generación y son revisados por nuestro sistema de control de calidad.",
                "keywords": ["calidad", "bueno", "profesional", "precisión", "exactitud"]
            },
            {
                "id": "faq_008",
                "category": "formatos",
                "question": "¿En qué formatos puedo exportar los documentos?",
                "answer": "Ofrecemos exportación a múltiples formatos profesionales:\n\n📄 Formatos de Documento:\n• PDF (recomendado para impresión)\n• DOCX (Microsoft Word)\n• ODT (OpenDocument)\n• TXT (texto plano)\n• HTML (para web)\n\n📊 Formatos de Presentación:\n• PPTX (PowerPoint)\n• ODP (OpenOffice)\n\n📋 Otros Formatos:\n• Markdown (.md)\n• LaTeX (.tex)\n• JSON (para integraciones)\n\n🎨 Opciones de Formato:\n• Estilos predefinidos (profesional, académico, creativo)\n• Personalización de fuentes y colores\n• Encabezados y pies de página personalizados\n• Numeración automática\n• Tabla de contenidos\n• Índice de figuras\n\n💡 Todos los formatos mantienen:\n• Formato y estructura\n• Imágenes y gráficos\n• Tablas y listas\n• Referencias y citas\n\nLos documentos se pueden exportar en múltiples formatos simultáneamente.",
                "keywords": ["formatos", "exportar", "pdf", "word", "docx", "descargar"]
            },
            {
                "id": "faq_009",
                "category": "personalizacion",
                "question": "¿Puedo personalizar los documentos generados?",
                "answer": "¡Absolutamente! Ofrecemos múltiples opciones de personalización:\n\n✏️ Edición Directa:\n• Edita cualquier sección del documento\n• Agrega, elimina o modifica contenido\n• Cambia el tono y estilo\n• Ajusta la longitud\n\n🎨 Personalización de Estilo:\n• Selecciona el tono (formal, casual, técnico)\n• Elige el nivel de detalle\n• Personaliza formato y diseño\n• Agrega tu marca personal\n\n🔄 Regeneración Selectiva:\n• Regenera secciones específicas\n• Mejora partes del documento\n• Ajusta contenido según feedback\n• Mantén lo que te gusta, cambia lo demás\n\n📝 Instrucciones Avanzadas:\n• Proporciona contexto adicional\n• Especifica requisitos detallados\n• Incluye ejemplos o referencias\n• Define el público objetivo\n\n💼 Plantillas Personalizadas:\n• Crea tus propias plantillas\n• Guarda estilos favoritos\n• Reutiliza configuraciones\n• Comparte con tu equipo\n\nLos documentos son completamente editables y personalizables según tus necesidades.",
                "keywords": ["personalizar", "editar", "modificar", "ajustar", "customizar"]
            },
            {
                "id": "faq_010",
                "category": "limites",
                "question": "¿Hay límites en la longitud o complejidad de los documentos?",
                "answer": "Los límites varían según tu plan:\n\n📏 Límites de Longitud:\n• Plan Gratuito: Hasta 10 páginas\n• Plan Básico: Hasta 30 páginas\n• Plan Pro: Longitud ilimitada\n• Plan Enterprise: Longitud ilimitada + procesamiento en masa\n\n⚡ Límites de Generación:\n• Plan Gratuito: 5 documentos/mes\n• Plan Básico: 50 documentos/mes\n• Plan Pro: 200 documentos/mes\n• Plan Enterprise: Ilimitado\n\n🔧 Complejidad:\n• No hay límites en complejidad del contenido\n• Soporta documentos técnicos complejos\n• Maneja múltiples secciones y subsecciones\n• Incluye tablas, listas y gráficos\n• Referencias y citas automáticas\n\n⏱️ Tiempo de Procesamiento:\n• Documentos simples (<10 páginas): 10-20 segundos\n• Documentos medianos (10-30 páginas): 20-40 segundos\n• Documentos largos (>30 páginas): 40-90 segundos\n• Planes Pro y Enterprise: Procesamiento prioritario (50% más rápido)\n\n💡 Si necesitas documentos más largos o complejos, puedes actualizar tu plan en cualquier momento.",
                "keywords": ["límites", "longitud", "complejidad", "páginas", "restricciones"]
            },
            {
                "id": "faq_011",
                "category": "api",
                "question": "¿Tienen API para integrar en mi aplicación?",
                "answer": "Sí, ofrecemos una API REST completa para integraciones:\n\n🔌 Características de la API:\n• RESTful API con JSON\n• Autenticación mediante API keys\n• Rate limiting según el plan\n• Webhooks para notificaciones\n• SDKs para Python, JavaScript, PHP, Ruby, Go\n\n📚 Documentación:\n• Documentación interactiva completa\n• Ejemplos de código en múltiples lenguajes\n• Guías de integración paso a paso\n• Sandbox para pruebas\n\n🎯 Casos de Uso:\n• Integración en aplicaciones web\n• Automatización de generación de documentos\n• Procesamiento en masa (bulk)\n• Integración con workflows\n• Sincronización con sistemas existentes\n\n💼 Disponibilidad:\n• Incluida en planes Pro y Enterprise\n• Límites según el plan contratado\n• Soporte técnico para integraciones\n• Consultoría de integración (Enterprise)\n\n📊 Límites de API:\n• Plan Pro: 1000 requests/día\n• Plan Enterprise: Ilimitado\n\nAccede a la documentación completa: api.ejemplo.com/docs",
                "keywords": ["api", "rest", "integración", "webhook", "sdk", "desarrollador"]
            },
            {
                "id": "faq_012",
                "category": "soporte",
                "question": "¿Qué tipo de soporte ofrecen?",
                "answer": "Ofrecemos soporte completo en múltiples canales:\n\n📚 Recursos de Autoayuda:\n• Base de conocimiento con 200+ artículos\n• Video tutoriales paso a paso\n• Guías de mejores prácticas\n• Ejemplos y plantillas\n• FAQ extensiva\n\n💬 Soporte Directo:\n• Chat en vivo (Lun-Vie, 9:00-18:00 GMT)\n• Email: soporte@ejemplo.com\n  - Plan Gratuito/Básico: Respuesta en 24h\n  - Plan Pro: Respuesta en 4h\n  - Plan Enterprise: Respuesta en 1h\n• Soporte 24/7 (Plan Enterprise)\n\n🎓 Onboarding y Capacitación:\n• Guía de inicio rápido\n• Sesión de onboarding (Enterprise)\n• Webinars semanales\n• Casos de uso y ejemplos\n\n🐛 Soporte Técnico:\n• Resolución de problemas\n• Asistencia con integraciones\n• Optimización de consultas\n• Mejora de resultados\n\n👥 Comunidad:\n• Foro de usuarios\n• Compartir plantillas\n• Mejores prácticas\n• Feedback y sugerencias",
                "keywords": ["soporte", "ayuda", "asistencia", "problema", "contacto", "técnico"]
            }
        ]
    
    def _load_document_types(self) -> List[str]:
        """Carga lista de tipos de documentos"""
        return [
            "Planes de negocios", "Propuestas comerciales", "Informes ejecutivos",
            "Documentos académicos", "Contratos", "Documentación técnica",
            "Artículos de blog", "White papers", "Manuales"
        ]
    
    def _load_formats(self) -> List[str]:
        """Carga lista de formatos de exportación"""
        return [
            "PDF", "DOCX", "ODT", "TXT", "HTML", "PPTX", "Markdown", "LaTeX"
        ]
    
    def _setup_logging(self):
        """Configura logging estructurado"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('chatbot_ia_bulk_documentos.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('IABulkDocumentosChatbot')
    
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
                r"qué es", r"información", r"sobre.*producto", r"ia bulk"
            ],
            IntentType.COMO_FUNCIONA: [
                r"cómo funciona", r"cómo usar", r"proceso", r"generar", r"crear documento"
            ],
            IntentType.TIPOS_DOCUMENTOS: [
                r"tipos", r"documentos", r"qué puedo crear", r"ejemplos", r"categorías"
            ],
            IntentType.PRECIO: [
                r"precio", r"costo", r"cuánto", r"tarifa", r"plan", r"pago"
            ],
            IntentType.PRUEBA: [
                r"prueba", r"gratis", r"trial", r"demo", r"test"
            ],
            IntentType.REGISTRO: [
                r"registro", r"registrar", r"crear cuenta", r"signup"
            ],
            IntentType.CALIDAD: [
                r"calidad", r"bueno", r"profesional", r"precisión", r"exactitud"
            ],
            IntentType.FORMATOS: [
                r"formatos", r"exportar", r"pdf", r"word", r"docx", r"descargar"
            ],
            IntentType.PERSONALIZACION: [
                r"personalizar", r"editar", r"modificar", r"ajustar", r"customizar"
            ],
            IntentType.LIMITES: [
                r"límites", r"longitud", r"complejidad", r"páginas", r"restricciones"
            ],
            IntentType.API: [
                r"api", r"rest", r"integración", r"webhook", r"sdk"
            ],
            IntentType.SOPORTE: [
                r"soporte", r"ayuda", r"problema", r"contacto", r"técnico"
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
            r"urgente", r"emergencia", r"crítico", r"datos.*perdidos",
            r"documento.*perdido", r"no.*genera", r"error.*generación"
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
                if intent == IntentType.TIPOS_DOCUMENTOS:
                    response_message += "\n\n💡 ¿Te gustaría ver ejemplos de algún tipo de documento específico?"
                elif intent == IntentType.COMO_FUNCIONA:
                    response_message += "\n\n🚀 ¿Quieres probar generando un documento ahora? ¡Es gratis!"
                
                return ChatbotResponse(
                    message=response_message,
                    confidence=0.85,
                    intent=intent.value,
                    requires_escalation=False,
                    suggested_actions=[
                        "¿Te ayudó esta respuesta?",
                        "Probar generando un documento",
                        "Ver tipos de documentos",
                        "Contactar con agente humano"
                    ],
                    faq_matched=faq_match.get('id'),
                    processing_time=processing_time
                )
            
            return ChatbotResponse(
                message=(
                    "Gracias por tu consulta. Puedo ayudarte con:\n\n"
                    "• Información sobre IA Bulk para documentos\n"
                    "• Cómo generar documentos con una sola consulta\n"
                    "• Tipos de documentos disponibles\n"
                    "• Precios, planes y prueba gratuita\n"
                    "• Formatos de exportación y personalización\n"
                    "• API e integraciones\n"
                    "• Soporte técnico\n\n"
                    "Si tu consulta es más específica o compleja, puedo conectarte con un agente "
                    "humano que podrá ayudarte mejor. ¿Te gustaría que te conecte con nuestro equipo?"
                ),
                confidence=0.5,
                intent=intent.value,
                requires_escalation=False,
                suggested_actions=[
                    "Ver cómo funciona",
                    "Probar gratis",
                    "Ver tipos de documentos",
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
    chatbot = IABulkDocumentosChatbot(enable_logging=True, persist_conversations=True)
    
    print("=" * 60)
    print("🤖 Chatbot - IA Bulk para Documentos")
    print("=" * 60)
    print("\n¡Hola! Soy tu asistente virtual. Puedo ayudarte con:")
    print("• Información sobre IA Bulk para generación de documentos")
    print("• Cómo generar documentos con una sola consulta")
    print("• Tipos de documentos disponibles")
    print("• Precios, planes y prueba gratuita")
    print("• Formatos, personalización y API")
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

