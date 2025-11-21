"""
Sistema de Costos y Facturación.

Calcula costos operativos y genera facturación para clientes.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class CostItem:
    """Item de costo."""
    item_id: str
    category: str  # "agent_time", "chatbot", "infrastructure", "third_party"
    description: str
    quantity: float
    unit_cost: float
    total_cost: float
    period_start: datetime
    period_end: datetime
    
    def __post_init__(self):
        if self.total_cost == 0:
            self.total_cost = self.quantity * self.unit_cost


@dataclass
class BillingItem:
    """Item de facturación."""
    billing_id: str
    customer_id: str
    customer_name: str
    period_start: datetime
    period_end: datetime
    tickets_handled: int
    agent_hours: float
    chatbot_interactions: int
    total_cost: float
    billing_rate: float  # Costo por ticket o por hora
    items: List[CostItem]
    generated_at: datetime = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now()


class CostBillingManager:
    """Gestor de costos y facturación."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa gestor.
        
        Args:
            db_connection: Conexión a BD (opcional)
        """
        self.db = db_connection
        self.cost_items: List[CostItem] = []
        self.billing_items: List[BillingItem] = []
        
        # Configuración de costos
        self.cost_config = {
            "agent_hourly_rate": 25.0,
            "chatbot_cost_per_interaction": 0.001,
            "infrastructure_cost_per_day": 50.0,
            "third_party_cost_per_month": 100.0
        }
    
    def calculate_operational_costs(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """
        Calcula costos operativos del período.
        
        Args:
            period_start: Inicio del período
            period_end: Fin del período
            
        Returns:
            Desglose de costos
        """
        if not self.db:
            return {"error": "No database connection"}
        
        costs = {
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat()
            },
            "categories": {},
            "total_cost": 0.0
        }
        
        try:
            with self.db.cursor() as cur:
                # Costos de agentes
                cur.execute("""
                    SELECT 
                        COUNT(*) as tickets,
                        SUM(time_to_resolution_minutes) / 60.0 as total_hours
                    FROM support_tickets
                    WHERE created_at >= %s AND created_at <= %s
                    AND chatbot_resolved = false
                    AND status = 'resolved'
                """, (period_start, period_end))
                
                row = cur.fetchone()
                agent_tickets = row[0] if row[0] else 0
                agent_hours = float(row[1]) if row[1] else 0.0
                
                agent_cost = agent_hours * self.cost_config["agent_hourly_rate"]
                costs["categories"]["agent_time"] = {
                    "tickets": agent_tickets,
                    "hours": agent_hours,
                    "hourly_rate": self.cost_config["agent_hourly_rate"],
                    "total_cost": agent_cost
                }
                
                # Costos de chatbot
                cur.execute("""
                    SELECT COUNT(*) FROM support_chatbot_interactions
                    WHERE created_at >= %s AND created_at <= %s
                """, (period_start, period_end))
                
                chatbot_interactions = cur.fetchone()[0] or 0
                chatbot_cost = chatbot_interactions * self.cost_config["chatbot_cost_per_interaction"]
                
                costs["categories"]["chatbot"] = {
                    "interactions": chatbot_interactions,
                    "cost_per_interaction": self.cost_config["chatbot_cost_per_interaction"],
                    "total_cost": chatbot_cost
                }
                
                # Costos de infraestructura
                days = (period_end - period_start).days
                infrastructure_cost = days * self.cost_config["infrastructure_cost_per_day"]
                
                costs["categories"]["infrastructure"] = {
                    "days": days,
                    "cost_per_day": self.cost_config["infrastructure_cost_per_day"],
                    "total_cost": infrastructure_cost
                }
                
                # Calcular total
                costs["total_cost"] = (
                    agent_cost +
                    chatbot_cost +
                    infrastructure_cost +
                    self.cost_config["third_party_cost_per_month"]
                )
                
                costs["categories"]["third_party"] = {
                    "total_cost": self.cost_config["third_party_cost_per_month"]
                }
                
        except Exception as e:
            logger.error(f"Error calculating costs: {e}")
            costs["error"] = str(e)
        
        return costs
    
    def generate_customer_billing(
        self,
        customer_id: str,
        customer_name: str,
        period_start: datetime,
        period_end: datetime,
        billing_rate: float = 10.0  # Por ticket
    ) -> BillingItem:
        """
        Genera facturación para un cliente.
        
        Args:
            customer_id: ID del cliente
            customer_name: Nombre del cliente
            period_start: Inicio del período
            period_end: Fin del período
            billing_rate: Tarifa de facturación
            
        Returns:
            Item de facturación
        """
        if not self.db:
            return None
        
        try:
            with self.db.cursor() as cur:
                # Tickets del cliente
                cur.execute("""
                    SELECT 
                        COUNT(*) as tickets,
                        SUM(time_to_resolution_minutes) / 60.0 as agent_hours
                    FROM support_tickets
                    WHERE customer_email = %s
                    AND created_at >= %s AND created_at <= %s
                    AND status = 'resolved'
                """, (customer_id, period_start, period_end))
                
                row = cur.fetchone()
                tickets_handled = row[0] if row[0] else 0
                agent_hours = float(row[1]) if row[1] else 0.0
                
                # Interacciones de chatbot
                cur.execute("""
                    SELECT COUNT(*) FROM support_chatbot_interactions
                    WHERE ticket_id IN (
                        SELECT ticket_id FROM support_tickets
                        WHERE customer_email = %s
                        AND created_at >= %s AND created_at <= %s
                    )
                """, (customer_id, period_start, period_end))
                
                chatbot_interactions = cur.fetchone()[0] or 0
                
                # Calcular costo total
                total_cost = tickets_handled * billing_rate
                
                # Crear items de costo
                cost_items = [
                    CostItem(
                        item_id=f"cost-{customer_id}-tickets",
                        category="tickets",
                        description=f"Tickets procesados: {tickets_handled}",
                        quantity=tickets_handled,
                        unit_cost=billing_rate,
                        total_cost=total_cost,
                        period_start=period_start,
                        period_end=period_end
                    )
                ]
                
                billing_item = BillingItem(
                    billing_id=f"bill-{customer_id}-{period_end.strftime('%Y%m%d')}",
                    customer_id=customer_id,
                    customer_name=customer_name,
                    period_start=period_start,
                    period_end=period_end,
                    tickets_handled=tickets_handled,
                    agent_hours=agent_hours,
                    chatbot_interactions=chatbot_interactions,
                    total_cost=total_cost,
                    billing_rate=billing_rate,
                    items=cost_items
                )
                
                self.billing_items.append(billing_item)
                
                logger.info(f"Generated billing for {customer_name}: ${total_cost:.2f}")
                
                return billing_item
                
        except Exception as e:
            logger.error(f"Error generating billing: {e}")
            return None
    
    def get_cost_breakdown(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """
        Obtiene desglose de costos.
        
        Args:
            period_start: Inicio del período
            period_end: Fin del período
            
        Returns:
            Desglose de costos
        """
        costs = self.calculate_operational_costs(period_start, period_end)
        
        if "error" in costs:
            return costs
        
        # Calcular porcentajes
        total = costs["total_cost"]
        breakdown = {}
        
        for category, data in costs["categories"].items():
            category_cost = data.get("total_cost", 0)
            percentage = (category_cost / total * 100) if total > 0 else 0
            breakdown[category] = {
                **data,
                "percentage": percentage
            }
        
        return {
            "period": costs["period"],
            "total_cost": total,
            "breakdown": breakdown,
            "cost_per_ticket": total / costs["categories"]["agent_time"]["tickets"] if costs["categories"]["agent_time"]["tickets"] > 0 else 0
        }
    
    def get_customer_billing_history(
        self,
        customer_id: str,
        months: int = 6
    ) -> List[BillingItem]:
        """
        Obtiene historial de facturación de un cliente.
        
        Args:
            customer_id: ID del cliente
            months: Meses hacia atrás
            
        Returns:
            Lista de items de facturación
        """
        cutoff = datetime.now() - timedelta(days=months * 30)
        
        return [
            bill for bill in self.billing_items
            if bill.customer_id == customer_id
            and bill.period_start >= cutoff
        ]
    
    def update_cost_config(self, config: Dict[str, float]):
        """Actualiza configuración de costos."""
        self.cost_config.update(config)
        logger.info(f"Updated cost configuration: {config}")

