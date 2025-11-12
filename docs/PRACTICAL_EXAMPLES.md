# 🎯 Ejemplos Prácticos Completos - Sistema de Troubleshooting

## Ejemplos por Escenario

### Ejemplo 1: Integración Completa con Sistema de Tickets

```python
"""
Integración completa del sistema de troubleshooting con un sistema de tickets existente
"""

from data.integrations.support_troubleshooting_agent import TroubleshootingAgent
from data.integrations.support_troubleshooting_notifications import (
    TroubleshootingNotificationManager,
    NotificationConfig,
    NotificationChannel
)
from data.integrations.support_troubleshooting_webhooks import (
    TroubleshootingWebhookManager,
    WebhookConfig,
    WebhookEvent
)

class TicketTroubleshootingIntegration:
    def __init__(self):
        self.agent = TroubleshootingAgent(use_llm=True)
        self.notification_manager = TroubleshootingNotificationManager()
        self.webhook_manager = TroubleshootingWebhookManager()
        self._setup_webhooks()
    
    def _setup_webhooks(self):
        """Configurar webhooks para eventos importantes"""
        # Webhook para Slack cuando se escala
        slack_config = WebhookConfig(
            url=os.getenv("SLACK_WEBHOOK_URL"),
            events=[WebhookEvent.SESSION_ESCALATED],
            secret=os.getenv("WEBHOOK_SECRET")
        )
        self.webhook_manager.register_webhook("slack-escalations", slack_config)
    
    def handle_new_ticket(self, ticket):
        """Procesar nuevo ticket"""
        # Intentar troubleshooting automático
        session = self.agent.start_troubleshooting(
            problem_description=ticket.description,
            customer_email=ticket.customer_email,
            customer_name=ticket.customer_name,
            ticket_id=ticket.id
        )
        
        if session.detected_problem:
            # Enviar primer paso al cliente
            step = self.agent.get_current_step(session.session_id)
            self._send_step_to_customer(ticket, step)
            
            # Notificar al equipo
            self._notify_team(ticket, session)
        else:
            # No se detectó problema, escalar inmediatamente
            self._escalate_ticket(ticket, "Problema no identificado automáticamente")
    
    def _send_step_to_customer(self, ticket, step):
        """Enviar paso al cliente"""
        config = NotificationConfig(
            channel=NotificationChannel.EMAIL,
            recipient=ticket.customer_email,
            template="step_instructions"
        )
        
        self.notification_manager.send_notification(config, {
            "customer_name": ticket.customer_name,
            "step": step,
            "ticket_id": ticket.id
        })
    
    def handle_step_completion(self, session_id, success, notes):
        """Procesar completación de paso"""
        result = self.agent.complete_step(session_id, success, notes)
        
        if result.get("status") == "resolved":
            # Problema resuelto
            self._mark_ticket_resolved(session_id)
            self._send_resolution_confirmation(session_id)
        elif result.get("suggest_escalation"):
            # Escalar ticket
            self._escalate_ticket_from_session(session_id)
    
    def _escalate_ticket_from_session(self, session_id):
        """Escalar ticket desde sesión"""
        escalation_info = self.agent.escalate_ticket(
            session_id,
            reason="Múltiples pasos fallidos"
        )
        
        # Notificar al equipo
        self.webhook_manager.trigger_webhook(
            WebhookEvent.SESSION_ESCALATED,
            escalation_info
        )
```

### Ejemplo 2: Dashboard de Métricas en Tiempo Real

```python
"""
Sistema de monitoreo y alertas basado en métricas
"""

from data.integrations.support_troubleshooting_agent import TroubleshootingAgent
import time

class TroubleshootingMonitor:
    def __init__(self):
        self.agent = TroubleshootingAgent()
        self.alert_thresholds = {
            "resolution_rate": 0.7,  # Alerta si baja de 70%
            "avg_rating": 4.0,  # Alerta si baja de 4.0
            "escalation_rate": 0.3  # Alerta si sube de 30%
        }
    
    def monitor_continuously(self, interval_seconds=300):
        """Monitorear continuamente"""
        while True:
            try:
                analytics = self.agent.get_analytics(days=1)
                self._check_thresholds(analytics)
                time.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error en monitoreo: {e}")
                time.sleep(interval_seconds)
    
    def _check_thresholds(self, analytics):
        """Verificar umbrales y enviar alertas"""
        resolution_rate = analytics.get("resolution_rate", 0) / 100
        
        if resolution_rate < self.alert_thresholds["resolution_rate"]:
            self._send_alert(
                "ALERTA: Tasa de resolución baja",
                f"Tasa actual: {resolution_rate:.2%}, Umbral: {self.alert_thresholds['resolution_rate']:.2%}"
            )
        
        avg_rating = analytics.get("average_rating", 0)
        if avg_rating < self.alert_thresholds["avg_rating"]:
            self._send_alert(
                "ALERTA: Rating promedio bajo",
                f"Rating actual: {avg_rating:.2f}, Umbral: {self.alert_thresholds['avg_rating']:.2f}"
            )
    
    def _send_alert(self, title, message):
        """Enviar alerta"""
        # Implementar según tu sistema de alertas
        print(f"🚨 {title}: {message}")
```

### Ejemplo 3: Sistema de Aprendizaje Automático

```python
"""
Sistema que aprende de correcciones para mejorar detección
"""

from data.integrations.support_troubleshooting_agent import TroubleshootingAgent
import psycopg2

class TroubleshootingLearningSystem:
    def __init__(self, db_connection):
        self.agent = TroubleshootingAgent()
        self.db = db_connection
    
    def record_correction(
        self,
        session_id: str,
        actual_problem_id: str,
        corrected_by: str,
        notes: str = None
    ):
        """Registrar corrección de agente humano"""
        session = self.agent.active_sessions.get(session_id)
        if not session:
            return
        
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO support_troubleshooting_ml_training (
                problem_description,
                detected_problem_id,
                actual_problem_id,
                corrected_by,
                correction_notes
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            session.problem_description,
            session.detected_problem.problem_id if session.detected_problem else None,
            actual_problem_id,
            corrected_by,
            notes
        ))
        self.db.commit()
        cursor.close()
        
        # Analizar si hay patrones
        self._analyze_patterns()
    
    def _analyze_patterns(self):
        """Analizar patrones para mejorar detección"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT 
                detected_problem_id,
                actual_problem_id,
                COUNT(*) as correction_count
            FROM support_troubleshooting_ml_training
            WHERE used_for_training = false
            GROUP BY detected_problem_id, actual_problem_id
            HAVING COUNT(*) >= 3
        """)
        
        patterns = cursor.fetchall()
        
        for pattern in patterns:
            detected, actual, count = pattern
            if detected != actual:
                logger.info(
                    f"Patrón detectado: '{detected}' se corrige frecuentemente a '{actual}' "
                    f"({count} veces). Considerar ajustar algoritmo de detección."
                )
        
        cursor.close()
```

### Ejemplo 4: Integración con Chatbot Conversacional

```python
"""
Integración con chatbot para experiencia conversacional fluida
"""

class ConversationalTroubleshooting:
    def __init__(self):
        self.agent = TroubleshootingAgent()
        self.conversation_context = {}
    
    def handle_message(self, user_id: str, message: str) -> str:
        """Manejar mensaje del usuario en conversación"""
        # Obtener o crear contexto de conversación
        if user_id not in self.conversation_context:
            # Nueva conversación, iniciar troubleshooting
            session = self.agent.start_troubleshooting(
                problem_description=message,
                customer_email=f"{user_id}@chat.local"
            )
            self.conversation_context[user_id] = {
                "session_id": session.session_id,
                "current_step": 0
            }
            
            if session.detected_problem:
                step = self.agent.get_current_step(session.session_id)
                return self._format_conversational_response(step)
            else:
                return "No pude identificar tu problema. ¿Podrías describirlo de otra manera?"
        
        # Continuar conversación existente
        context = self.conversation_context[user_id]
        
        # Detectar si el usuario completó el paso
        if self._is_step_completed(message):
            result = self.agent.complete_step(
                context["session_id"],
                success=True,
                notes=message
            )
            
            if result.get("status") == "resolved":
                del self.conversation_context[user_id]
                return "¡Excelente! Parece que resolviste el problema. ¿Hay algo más en lo que pueda ayudarte?"
            
            step = self.agent.get_current_step(context["session_id"])
            return self._format_conversational_response(step)
        else:
            # Usuario tiene pregunta o problema
            step = self.agent.get_current_step(context["session_id"])
            return f"Entiendo. Sigamos con el paso actual:\n\n{self._format_conversational_response(step)}"
    
    def _is_step_completed(self, message: str) -> bool:
        """Detectar si el usuario indica que completó el paso"""
        completion_indicators = [
            "listo", "completado", "hecho", "terminado", "sí", "yes",
            "funciona", "resuelto", "ok", "bien"
        ]
        return any(indicator in message.lower() for indicator in completion_indicators)
    
    def _format_conversational_response(self, step_info: Dict) -> str:
        """Formatear respuesta de forma conversacional"""
        if step_info.get("status") == "no_problem_detected":
            return "No pude identificar tu problema específicamente. ¿Podrías describirlo de otra manera?"
        
        response = f"📋 **{step_info.get('title', 'Siguiente paso')}**\n\n"
        response += f"{step_info.get('description', '')}\n\n"
        
        response += "Sigue estos pasos:\n"
        for i, instruction in enumerate(step_info.get('instructions', []), 1):
            response += f"{i}. {instruction}\n"
        
        if step_info.get('warnings'):
            response += "\n⚠️ **Importante:**\n"
            for warning in step_info['warnings']:
                response += f"• {warning}\n"
        
        response += f"\nCuando termines, avísame y continuamos con el siguiente paso."
        
        return response
```

### Ejemplo 5: Sistema de Priorización Inteligente

```python
"""
Sistema que prioriza sesiones según múltiples factores
"""

class IntelligentPrioritization:
    def __init__(self):
        self.agent = TroubleshootingAgent()
    
    def prioritize_sessions(self) -> List[Dict]:
        """Priorizar sesiones activas"""
        active_sessions = [
            session for session in self.agent.active_sessions.values()
            if session.status in [TroubleshootingStatus.STARTED, TroubleshootingStatus.IN_PROGRESS]
        ]
        
        # Calcular prioridad para cada sesión
        prioritized = []
        for session in active_sessions:
            priority_score = self._calculate_priority_score(session)
            prioritized.append({
                "session": session,
                "priority_score": priority_score
            })
        
        # Ordenar por prioridad
        prioritized.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return prioritized
    
    def _calculate_priority_score(self, session: TroubleshootingSession) -> float:
        """Calcula score de prioridad (0.0 a 100.0)"""
        score = 0.0
        
        # Factor 1: Tiempo transcurrido (más tiempo = mayor prioridad)
        elapsed_hours = (datetime.now() - session.started_at).total_seconds() / 3600
        score += min(elapsed_hours * 10, 30)  # Máximo 30 puntos
        
        # Factor 2: Pasos fallidos (más fallos = mayor prioridad)
        failed_steps = sum(1 for a in session.attempted_steps if not a.get("success"))
        score += failed_steps * 15  # 15 puntos por fallo
        
        # Factor 3: Tipo de problema (algunos son más críticos)
        if session.detected_problem:
            critical_problems = ["error_aplicacion", "conexion_internet"]
            if session.detected_problem.problem_id in critical_problems:
                score += 20
        
        # Factor 4: Cliente VIP (si está disponible en metadata)
        # score += 25 if is_vip_customer(session.customer_email) else 0
        
        return min(score, 100.0)
```

### Ejemplo 6: Exportación y Reportes Automáticos

```python
"""
Sistema de reportes automáticos por email
"""

from data.integrations.support_troubleshooting_reports import (
    TroubleshootingReportGenerator,
    ReportConfig,
    ReportType
)
from datetime import datetime, timedelta

class AutomatedReporting:
    def __init__(self):
        self.report_generator = TroubleshootingReportGenerator()
        self.notification_manager = TroubleshootingNotificationManager()
    
    def send_daily_report(self, recipient_email: str):
        """Enviar reporte diario automático"""
        config = ReportConfig(
            report_type=ReportType.DAILY,
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now()
        )
        
        report = self.report_generator.generate_report(config)
        report_json = self.report_generator.export_report(report, format="json")
        
        # Enviar por email
        config = NotificationConfig(
            channel=NotificationChannel.EMAIL,
            recipient=recipient_email,
            subject=f"Reporte Diario de Troubleshooting - {datetime.now().strftime('%Y-%m-%d')}"
        )
        
        self.notification_manager.send_notification(config, {
            "body": f"Reporte diario adjunto.\n\nResumen:\n- Sesiones totales: {report.get('summary', {}).get('total_sessions', 0)}\n- Resueltas: {report.get('summary', {}).get('resolved_sessions', 0)}\n- Tasa de resolución: {report.get('summary', {}).get('resolution_rate', 0):.2f}%",
            "attachment": report_json
        })
    
    def schedule_reports(self):
        """Programar reportes automáticos"""
        # Usar cron o scheduler
        # Diario a las 8 AM
        # Semanal los lunes
        # Mensual el día 1
        pass
```

## Patrones de Uso Comunes

### Patrón: Retry con Exponential Backoff

```python
import time

def retry_with_backoff(func, max_retries=3, initial_delay=1):
    """Ejecutar función con retry y exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            delay = initial_delay * (2 ** attempt)
            logger.warning(f"Intento {attempt + 1} falló, reintentando en {delay}s...")
            time.sleep(delay)
```

### Patrón: Circuit Breaker

```python
class TroubleshootingCircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
```

---

**Versión**: 1.0.0  
**Última actualización**: 2025-01-27



