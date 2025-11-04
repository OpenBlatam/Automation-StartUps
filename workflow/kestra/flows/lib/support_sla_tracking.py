"""
Sistema de Tracking Avanzado de SLA.

Monitorea y reporta cumplimiento de SLAs en tiempo real.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class SLAStatus(Enum):
    """Estado de SLA."""
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    BREACHED = "breached"
    MET = "met"
    MISSED = "missed"


@dataclass
class SLA:
    """SLA."""
    sla_id: str
    name: str
    description: str
    target_hours: float
    priority: str
    category: Optional[str] = None
    customer_tier: Optional[str] = None
    conditions: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}


@dataclass
class SLATracking:
    """Tracking de SLA."""
    tracking_id: str
    ticket_id: str
    sla_id: str
    sla_name: str
    target_hours: float
    created_at: datetime
    target_deadline: datetime
    current_status: SLAStatus
    hours_remaining: float
    hours_elapsed: float
    compliance_percentage: float  # 0-100
    breached_at: Optional[datetime] = None
    met_at: Optional[datetime] = None


class SLATracker:
    """Rastreador de SLA."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa rastreador.
        
        Args:
            db_connection: Conexión a BD (opcional)
        """
        self.db = db_connection
        self.slas: Dict[str, SLA] = {}
        self.active_trackings: Dict[str, SLATracking] = {}
        self._initialize_default_slas()
    
    def _initialize_default_slas(self):
        """Inicializa SLAs por defecto."""
        default_slas = [
            SLA(
                sla_id="sla-critical",
                name="Critical Priority SLA",
                description="SLA para tickets críticos",
                target_hours=1.0,
                priority="critical"
            ),
            SLA(
                sla_id="sla-urgent",
                name="Urgent Priority SLA",
                description="SLA para tickets urgentes",
                target_hours=4.0,
                priority="urgent"
            ),
            SLA(
                sla_id="sla-high",
                name="High Priority SLA",
                description="SLA para tickets de alta prioridad",
                target_hours=8.0,
                priority="high"
            ),
            SLA(
                sla_id="sla-normal",
                name="Normal Priority SLA",
                description="SLA para tickets normales",
                target_hours=24.0,
                priority="normal"
            ),
            SLA(
                sla_id="sla-vip",
                name="VIP Customer SLA",
                description="SLA para clientes VIP",
                target_hours=2.0,
                customer_tier="vip"
            )
        ]
        
        for sla in default_slas:
            self.slas[sla.sla_id] = sla
    
    def track_ticket(
        self,
        ticket_id: str,
        ticket_data: Dict[str, Any]
    ) -> SLATracking:
        """
        Inicia tracking de SLA para un ticket.
        
        Args:
            ticket_id: ID del ticket
            ticket_data: Datos del ticket
            
        Returns:
            Tracking de SLA
        """
        # Determinar SLA aplicable
        sla = self._determine_sla(ticket_data)
        
        if not sla:
            return None
        
        created_at = ticket_data.get("created_at", datetime.now())
        if isinstance(created_at, str):
            from dateutil import parser
            created_at = parser.parse(created_at)
        
        target_deadline = created_at + timedelta(hours=sla.target_hours)
        now = datetime.now()
        
        hours_elapsed = (now - created_at).total_seconds() / 3600
        hours_remaining = max(0, (target_deadline - now).total_seconds() / 3600)
        
        # Determinar estado
        if hours_elapsed >= sla.target_hours:
            status = SLAStatus.BREACHED
            compliance_percentage = 0.0
        elif hours_remaining < sla.target_hours * 0.2:  # Menos del 20% restante
            status = SLAStatus.AT_RISK
            compliance_percentage = (hours_remaining / sla.target_hours) * 100
        else:
            status = SLAStatus.ON_TRACK
            compliance_percentage = (hours_remaining / sla.target_hours) * 100
        
        tracking = SLATracking(
            tracking_id=f"sla-track-{ticket_id}",
            ticket_id=ticket_id,
            sla_id=sla.sla_id,
            sla_name=sla.name,
            target_hours=sla.target_hours,
            created_at=created_at,
            target_deadline=target_deadline,
            current_status=status,
            hours_remaining=hours_remaining,
            hours_elapsed=hours_elapsed,
            compliance_percentage=compliance_percentage
        )
        
        self.active_trackings[ticket_id] = tracking
        
        return tracking
    
    def _determine_sla(self, ticket_data: Dict[str, Any]) -> Optional[SLA]:
        """Determina SLA aplicable."""
        priority = ticket_data.get("priority", "normal")
        customer_tier = ticket_data.get("customer_tier")
        
        # Buscar SLA por customer tier primero
        if customer_tier == "vip":
            return self.slas.get("sla-vip")
        
        # Buscar por prioridad
        sla_key = f"sla-{priority}"
        return self.slas.get(sla_key)
    
    def update_tracking(self, ticket_id: str, ticket_data: Dict[str, Any]) -> Optional[SLATracking]:
        """Actualiza tracking de SLA."""
        if ticket_id not in self.active_trackings:
            return self.track_ticket(ticket_id, ticket_data)
        
        tracking = self.active_trackings[ticket_id]
        now = datetime.now()
        
        # Actualizar métricas
        tracking.hours_elapsed = (now - tracking.created_at).total_seconds() / 3600
        tracking.hours_remaining = max(0, (tracking.target_deadline - now).total_seconds() / 3600)
        
        # Actualizar estado
        if tracking.hours_elapsed >= tracking.target_hours:
            if tracking.current_status != SLAStatus.BREACHED:
                tracking.current_status = SLAStatus.BREACHED
                tracking.breached_at = now
                tracking.compliance_percentage = 0.0
        elif tracking.hours_remaining < tracking.target_hours * 0.2:
            tracking.current_status = SLAStatus.AT_RISK
            tracking.compliance_percentage = (tracking.hours_remaining / tracking.target_hours) * 100
        else:
            tracking.current_status = SLAStatus.ON_TRACK
            tracking.compliance_percentage = (tracking.hours_remaining / tracking.target_hours) * 100
        
        # Si está resuelto antes del deadline
        if ticket_data.get("status") == "resolved" and tracking.hours_remaining > 0:
            tracking.current_status = SLAStatus.MET
            tracking.met_at = now
            tracking.compliance_percentage = 100.0
        
        return tracking
    
    def get_sla_compliance_report(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """
        Genera reporte de cumplimiento de SLA.
        
        Args:
            period_start: Inicio del período
            period_end: Fin del período
            
        Returns:
            Reporte de cumplimiento
        """
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            with self.db.cursor() as cur:
                # Tickets en período
                cur.execute("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE sla_breached = false) as met,
                        COUNT(*) FILTER (WHERE sla_breached = true) as breached,
                        AVG(sla_compliance_score) as avg_compliance
                    FROM support_tickets
                    WHERE created_at >= %s AND created_at <= %s
                    AND sla_target_hours IS NOT NULL
                """, (period_start, period_end))
                
                row = cur.fetchone()
                total = row[0] or 0
                met = row[1] or 0
                breached = row[2] or 0
                avg_compliance = float(row[3]) if row[3] else 0.0
                
                compliance_rate = (met / total * 100) if total > 0 else 0.0
                
                # Por prioridad
                cur.execute("""
                    SELECT 
                        priority,
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE sla_breached = false) as met
                    FROM support_tickets
                    WHERE created_at >= %s AND created_at <= %s
                    AND sla_target_hours IS NOT NULL
                    GROUP BY priority
                """, (period_start, period_end))
                
                by_priority = {}
                for row in cur.fetchall():
                    priority, total_pri, met_pri = row
                    by_priority[priority] = {
                        "total": total_pri,
                        "met": met_pri,
                        "compliance_rate": (met_pri / total_pri * 100) if total_pri > 0 else 0.0
                    }
                
                return {
                    "period": {
                        "start": period_start.isoformat(),
                        "end": period_end.isoformat()
                    },
                    "summary": {
                        "total_tickets": total,
                        "sla_met": met,
                        "sla_breached": breached,
                        "compliance_rate": compliance_rate,
                        "average_compliance_score": avg_compliance
                    },
                    "by_priority": by_priority,
                    "at_risk_tickets": len([
                        t for t in self.active_trackings.values()
                        if t.current_status == SLAStatus.AT_RISK
                    ]),
                    "breached_tickets": len([
                        t for t in self.active_trackings.values()
                        if t.current_status == SLAStatus.BREACHED
                    ])
                }
        except Exception as e:
            logger.error(f"Error generating SLA compliance report: {e}")
            return {"error": str(e)}
    
    def get_at_risk_tickets(self) -> List[SLATracking]:
        """Obtiene tickets en riesgo de incumplir SLA."""
        return [
            tracking for tracking in self.active_trackings.values()
            if tracking.current_status == SLAStatus.AT_RISK
        ]
    
    def get_breached_tickets(self) -> List[SLATracking]:
        """Obtiene tickets que han incumplido SLA."""
        return [
            tracking for tracking in self.active_trackings.values()
            if tracking.current_status == SLAStatus.BREACHED
        ]
    
    def register_sla(self, sla: SLA):
        """Registra un SLA personalizado."""
        self.slas[sla.sla_id] = sla
        logger.info(f"Registered SLA: {sla.name}")

