"""
Sistema de Simulaciones y Testing.

Permite simular escenarios y probar el sistema antes de producción.
"""
import logging
import uuid
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class SimulationType(Enum):
    """Tipos de simulación."""
    VOLUME_TEST = "volume_test"
    STRESS_TEST = "stress_test"
    SCENARIO_TEST = "scenario_test"
    LOAD_TEST = "load_test"
    INTEGRATION_TEST = "integration_test"


@dataclass
class SimulationResult:
    """Resultado de simulación."""
    simulation_id: str
    simulation_type: SimulationType
    tickets_created: int
    tickets_processed: int
    tickets_resolved: int
    average_response_time: float
    average_resolution_time: float
    chatbot_resolution_rate: float
    errors: List[str]
    warnings: List[str]
    duration_seconds: float
    started_at: datetime
    completed_at: datetime


class SimulationEngine:
    """Motor de simulación."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa motor de simulación.
        
        Args:
            db_connection: Conexión a BD (opcional)
        """
        self.db = db_connection
        self.simulation_results: List[SimulationResult] = []
    
    def simulate_volume_test(
        self,
        ticket_count: int,
        duration_minutes: int = 60,
        use_chatbot: bool = True
    ) -> SimulationResult:
        """
        Simula prueba de volumen.
        
        Args:
            ticket_count: Número de tickets a crear
            duration_minutes: Duración de la prueba
            use_chatbot: Usar chatbot en simulación
            
        Returns:
            Resultado de simulación
        """
        simulation_id = f"sim-{uuid.uuid4().hex[:12]}"
        started_at = datetime.now()
        
        errors = []
        warnings = []
        tickets_processed = 0
        tickets_resolved = 0
        response_times = []
        resolution_times = []
        chatbot_resolved = 0
        
        logger.info(f"Starting volume test: {ticket_count} tickets over {duration_minutes} minutes")
        
        try:
            # Simular creación de tickets
            for i in range(ticket_count):
                try:
                    # Simular ticket
                    ticket_data = self._generate_random_ticket()
                    
                    # Simular procesamiento
                    if use_chatbot and random.random() < 0.4:  # 40% chatbot
                        chatbot_success = random.random() < 0.6  # 60% éxito
                        if chatbot_success:
                            chatbot_resolved += 1
                            tickets_resolved += 1
                            resolution_times.append(random.uniform(5, 15))  # 5-15 minutos
                        else:
                            # Pasar a agente
                            response_times.append(random.uniform(30, 120))
                            resolution_times.append(random.uniform(60, 240))
                            tickets_resolved += 1
                    else:
                        # Procesamiento manual
                        response_times.append(random.uniform(30, 180))
                        resolution_times.append(random.uniform(60, 480))
                        tickets_resolved += 1
                    
                    tickets_processed += 1
                    
                except Exception as e:
                    errors.append(f"Error processing ticket {i}: {str(e)}")
            
            # Calcular promedios
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
            avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0.0
            chatbot_rate = (chatbot_resolved / tickets_processed * 100) if tickets_processed > 0 else 0.0
            
            completed_at = datetime.now()
            duration = (completed_at - started_at).total_seconds()
            
            result = SimulationResult(
                simulation_id=simulation_id,
                simulation_type=SimulationType.VOLUME_TEST,
                tickets_created=ticket_count,
                tickets_processed=tickets_processed,
                tickets_resolved=tickets_resolved,
                average_response_time=avg_response_time,
                average_resolution_time=avg_resolution_time,
                chatbot_resolution_rate=chatbot_rate,
                errors=errors,
                warnings=warnings,
                duration_seconds=duration,
                started_at=started_at,
                completed_at=completed_at
            )
            
            self.simulation_results.append(result)
            logger.info(f"Volume test completed: {tickets_processed} tickets processed")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in volume test: {e}")
            errors.append(str(e))
            
            return SimulationResult(
                simulation_id=simulation_id,
                simulation_type=SimulationType.VOLUME_TEST,
                tickets_created=ticket_count,
                tickets_processed=tickets_processed,
                tickets_resolved=tickets_resolved,
                average_response_time=0.0,
                average_resolution_time=0.0,
                chatbot_resolution_rate=0.0,
                errors=errors,
                warnings=warnings,
                duration_seconds=(datetime.now() - started_at).total_seconds(),
                started_at=started_at,
                completed_at=datetime.now()
            )
    
    def simulate_stress_test(
        self,
        peak_tickets_per_minute: int,
        duration_minutes: int = 10
    ) -> SimulationResult:
        """
        Simula prueba de estrés.
        
        Args:
            peak_tickets_per_minute: Pico de tickets por minuto
            duration_minutes: Duración de la prueba
            
        Returns:
            Resultado de simulación
        """
        simulation_id = f"sim-{uuid.uuid4().hex[:12]}"
        started_at = datetime.now()
        
        total_tickets = peak_tickets_per_minute * duration_minutes
        logger.info(f"Starting stress test: {peak_tickets_per_minute} tickets/min for {duration_minutes} minutes")
        
        # Simular distribución de carga
        tickets_per_minute = []
        for i in range(duration_minutes):
            # Simular pico gradual
            if i < duration_minutes / 2:
                load = peak_tickets_per_minute * (i / (duration_minutes / 2))
            else:
                load = peak_tickets_per_minute * (1 - (i - duration_minutes / 2) / (duration_minutes / 2))
            tickets_per_minute.append(int(load))
        
        return self.simulate_volume_test(
            ticket_count=total_tickets,
            duration_minutes=duration_minutes,
            use_chatbot=True
        )
    
    def simulate_scenario(
        self,
        scenario_name: str,
        scenario_config: Dict[str, Any]
    ) -> SimulationResult:
        """
        Simula un escenario específico.
        
        Args:
            scenario_name: Nombre del escenario
            scenario_config: Configuración del escenario
            
        Returns:
            Resultado de simulación
        """
        simulation_id = f"sim-{uuid.uuid4().hex[:12]}"
        started_at = datetime.now()
        
        logger.info(f"Starting scenario test: {scenario_name}")
        
        # Escenarios predefinidos
        scenarios = {
            "vip_customer_spike": {
                "ticket_count": 50,
                "priority_distribution": {"critical": 0.3, "urgent": 0.4, "high": 0.3},
                "customer_tier": "vip"
            },
            "technical_issue_outbreak": {
                "ticket_count": 100,
                "category_distribution": {"technical": 0.8, "general": 0.2},
                "tags": ["bug", "error", "crash"]
            },
            "billing_peak": {
                "ticket_count": 75,
                "category_distribution": {"billing": 0.9, "general": 0.1},
                "time_of_day": "9-10am"
            }
        }
        
        config = scenarios.get(scenario_name, scenario_config)
        ticket_count = config.get("ticket_count", 50)
        
        return self.simulate_volume_test(
            ticket_count=ticket_count,
            duration_minutes=30,
            use_chatbot=True
        )
    
    def _generate_random_ticket(self) -> Dict[str, Any]:
        """Genera un ticket aleatorio para simulación."""
        priorities = ["low", "normal", "high", "urgent", "critical"]
        categories = ["technical", "billing", "account", "general", "feature_request"]
        statuses = ["open", "assigned", "in_progress"]
        
        return {
            "ticket_id": f"ticket-{uuid.uuid4().hex[:12]}",
            "subject": f"Test ticket {random.randint(1000, 9999)}",
            "description": "Simulated ticket for testing",
            "priority": random.choice(priorities),
            "category": random.choice(categories),
            "status": random.choice(statuses),
            "customer_email": f"test{random.randint(1, 1000)}@example.com",
            "created_at": datetime.now()
        }
    
    def get_simulation_report(self) -> Dict[str, Any]:
        """
        Genera reporte de todas las simulaciones.
        
        Returns:
            Reporte de simulaciones
        """
        if not self.simulation_results:
            return {"message": "No simulations run yet"}
        
        total_simulations = len(self.simulation_results)
        total_tickets = sum(r.tickets_created for r in self.simulation_results)
        total_processed = sum(r.tickets_processed for r in self.simulation_results)
        total_errors = sum(len(r.errors) for r in self.simulation_results)
        
        avg_response_time = sum(r.average_response_time for r in self.simulation_results) / total_simulations
        avg_resolution_time = sum(r.average_resolution_time for r in self.simulation_results) / total_simulations
        avg_chatbot_rate = sum(r.chatbot_resolution_rate for r in self.simulation_results) / total_simulations
        
        return {
            "total_simulations": total_simulations,
            "total_tickets_created": total_tickets,
            "total_tickets_processed": total_processed,
            "total_errors": total_errors,
            "average_metrics": {
                "response_time_minutes": avg_response_time,
                "resolution_time_minutes": avg_resolution_time,
                "chatbot_resolution_rate": avg_chatbot_rate
            },
            "recent_simulations": [
                {
                    "id": r.simulation_id,
                    "type": r.simulation_type.value,
                    "tickets": r.tickets_created,
                    "processed": r.tickets_processed,
                    "resolved": r.tickets_resolved,
                    "errors": len(r.errors),
                    "duration_seconds": r.duration_seconds
                }
                for r in self.simulation_results[-10:]
            ]
        }

