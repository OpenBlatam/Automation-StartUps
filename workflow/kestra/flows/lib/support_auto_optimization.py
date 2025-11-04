"""
Sistema de Auto-optimización.

Optimiza automáticamente el sistema basándose en métricas y patrones.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Tipos de optimización."""
    ROUTING = "routing"
    PRIORITY = "priority"
    SLAs = "slas"
    RESOURCE_ALLOCATION = "resource_allocation"
    CACHE = "cache"
    CONFIGURATION = "configuration"


@dataclass
class OptimizationResult:
    """Resultado de optimización."""
    optimization_id: str
    optimization_type: OptimizationType
    description: str
    changes: Dict[str, Any]
    expected_impact: str
    confidence: float  # 0.0 a 1.0
    applied: bool = False
    applied_at: Optional[datetime] = None
    actual_impact: Optional[Dict[str, Any]] = None


class AutoOptimizer:
    """Motor de auto-optimización."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa optimizador.
        
        Args:
            db_connection: Conexión a BD (opcional)
        """
        self.db = db_connection
        self.optimization_history: List[OptimizationResult] = []
        self.active_optimizations: Dict[str, OptimizationResult] = {}
    
    def analyze_and_optimize(self) -> List[OptimizationResult]:
        """
        Analiza el sistema y genera optimizaciones.
        
        Returns:
            Lista de optimizaciones sugeridas
        """
        optimizations = []
        
        # Optimizar routing
        routing_opt = self._optimize_routing()
        if routing_opt:
            optimizations.append(routing_opt)
        
        # Optimizar priorización
        priority_opt = self._optimize_priority()
        if priority_opt:
            optimizations.append(priority_opt)
        
        # Optimizar SLAs
        sla_opt = self._optimize_slas()
        if sla_opt:
            optimizations.append(sla_opt)
        
        # Optimizar asignación de recursos
        resource_opt = self._optimize_resource_allocation()
        if resource_opt:
            optimizations.append(resource_opt)
        
        return optimizations
    
    def _optimize_routing(self) -> Optional[OptimizationResult]:
        """Optimiza reglas de enrutamiento."""
        if not self.db:
            return None
        
        try:
            with self.db.cursor() as cur:
                # Analizar distribución de tickets por departamento
                cur.execute("""
                    SELECT 
                        assigned_department,
                        COUNT(*) as ticket_count,
                        AVG(time_to_resolution_minutes) as avg_resolution,
                        AVG(customer_satisfaction_score) as avg_satisfaction
                    FROM support_tickets
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                    AND assigned_department IS NOT NULL
                    GROUP BY assigned_department
                """)
                
                departments = cur.fetchall()
                
                # Identificar desbalances
                if len(departments) < 2:
                    return None
                
                # Calcular promedio de carga
                avg_load = sum(d[1] for d in departments) / len(departments)
                
                # Encontrar departamento sobrecargado
                overloaded = max(departments, key=lambda x: x[1])
                underloaded = min(departments, key=lambda x: x[1])
                
                if overloaded[1] > avg_load * 1.5:
                    return OptimizationResult(
                        optimization_id=f"opt-routing-{datetime.now().timestamp()}",
                        optimization_type=OptimizationType.ROUTING,
                        description=f"Re-balancear carga: {overloaded[0]} tiene {overloaded[1]:.0f} tickets vs promedio {avg_load:.0f}",
                        changes={
                            "from_department": overloaded[0],
                            "to_department": underloaded[0],
                            "suggested_redistribution": int((overloaded[1] - avg_load) / 2)
                        },
                        expected_impact="Reducir tiempo de respuesta en departamento sobrecargado",
                        confidence=0.75
                    )
        except Exception as e:
            logger.error(f"Error optimizing routing: {e}")
        
        return None
    
    def _optimize_priority(self) -> Optional[OptimizationResult]:
        """Optimiza reglas de priorización."""
        if not self.db:
            return None
        
        try:
            with self.db.cursor() as cur:
                # Analizar distribución de prioridades vs satisfacción
                cur.execute("""
                    SELECT 
                        priority,
                        COUNT(*) as count,
                        AVG(customer_satisfaction_score) as avg_satisfaction,
                        AVG(time_to_resolution_minutes) as avg_resolution
                    FROM support_tickets
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                    AND customer_satisfaction_score IS NOT NULL
                    GROUP BY priority
                """)
                
                priorities = cur.fetchall()
                
                # Identificar si hay prioridades con baja satisfacción
                for priority_data in priorities:
                    priority, count, avg_satisfaction, avg_resolution = priority_data
                    
                    if avg_satisfaction and avg_satisfaction < 3.0 and count > 10:
                        return OptimizationResult(
                            optimization_id=f"opt-priority-{datetime.now().timestamp()}",
                            optimization_type=OptimizationType.PRIORITY,
                            description=f"Prioridad {priority} tiene satisfacción baja ({avg_satisfaction:.1f}/5) con {count} tickets",
                            changes={
                                "priority": priority,
                                "suggested_action": "Revisar reglas de priorización para esta prioridad",
                                "current_satisfaction": float(avg_satisfaction),
                                "current_resolution_time": float(avg_resolution) if avg_resolution else None
                            },
                            expected_impact="Mejorar satisfacción y tiempo de resolución",
                            confidence=0.70
                        )
        except Exception as e:
            logger.error(f"Error optimizing priority: {e}")
        
        return None
    
    def _optimize_slas(self) -> Optional[OptimizationResult]:
        """Optimiza SLAs."""
        if not self.db:
            return None
        
        try:
            with self.db.cursor() as cur:
                # Analizar cumplimiento de SLAs
                cur.execute("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE sla_breached = true) as breached,
                        AVG(sla_compliance_score) as avg_compliance
                    FROM support_tickets
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                    AND sla_target_hours IS NOT NULL
                """)
                
                row = cur.fetchone()
                if row and row[0] > 0:
                    total, breached, avg_compliance = row
                    breach_rate = (breached / total) * 100 if total > 0 else 0
                    
                    if breach_rate > 10 and avg_compliance:
                        return OptimizationResult(
                            optimization_id=f"opt-sla-{datetime.now().timestamp()}",
                            optimization_type=OptimizationType.SLAs,
                            description=f"Tasa de incumplimiento de SLA: {breach_rate:.1f}% ({breached}/{total} tickets)",
                            changes={
                                "breach_rate": breach_rate,
                                "avg_compliance": float(avg_compliance) if avg_compliance else None,
                                "suggested_action": "Ajustar SLAs o mejorar tiempo de respuesta"
                            },
                            expected_impact="Reducir incumplimiento de SLAs",
                            confidence=0.80
                        )
        except Exception as e:
            logger.error(f"Error optimizing SLAs: {e}")
        
        return None
    
    def _optimize_resource_allocation(self) -> Optional[OptimizationResult]:
        """Optimiza asignación de recursos."""
        if not self.db:
            return None
        
        try:
            with self.db.cursor() as cur:
                # Analizar carga de agentes
                cur.execute("""
                    SELECT 
                        assigned_agent_id,
                        COUNT(*) as active_tickets,
                        AVG(time_to_resolution_minutes) as avg_resolution
                    FROM support_tickets
                    WHERE status IN ('open', 'assigned', 'in_progress')
                    AND assigned_agent_id IS NOT NULL
                    GROUP BY assigned_agent_id
                """)
                
                agents = cur.fetchall()
                
                if len(agents) < 2:
                    return None
                
                # Calcular promedio de carga
                avg_load = sum(a[1] for a in agents) / len(agents)
                
                # Encontrar agentes sobrecargados
                overloaded = [a for a in agents if a[1] > avg_load * 1.5]
                
                if overloaded:
                    max_overloaded = max(overloaded, key=lambda x: x[1])
                    return OptimizationResult(
                        optimization_id=f"opt-resource-{datetime.now().timestamp()}",
                        optimization_type=OptimizationType.RESOURCE_ALLOCATION,
                        description=f"Agente {max_overloaded[0]} tiene {max_overloaded[1]:.0f} tickets activos vs promedio {avg_load:.0f}",
                        changes={
                            "agent_id": max_overloaded[0],
                            "current_load": max_overloaded[1],
                            "avg_load": avg_load,
                            "suggested_action": "Redistribuir tickets o asignar más recursos"
                        },
                        expected_impact="Mejorar balance de carga y tiempo de respuesta",
                        confidence=0.85
                    )
        except Exception as e:
            logger.error(f"Error optimizing resource allocation: {e}")
        
        return None
    
    def apply_optimization(self, optimization: OptimizationResult) -> bool:
        """
        Aplica una optimización.
        
        Args:
            optimization: Optimización a aplicar
            
        Returns:
            True si se aplicó correctamente
        """
        try:
            if optimization.optimization_type == OptimizationType.ROUTING:
                # Implementar redistribución
                logger.info(f"Applying routing optimization: {optimization.description}")
                # Aquí iría la lógica real de redistribución
            
            elif optimization.optimization_type == OptimizationType.PRIORITY:
                # Ajustar reglas de priorización
                logger.info(f"Applying priority optimization: {optimization.description}")
            
            elif optimization.optimization_type == OptimizationType.SLAs:
                # Ajustar SLAs
                logger.info(f"Applying SLA optimization: {optimization.description}")
            
            elif optimization.optimization_type == OptimizationType.RESOURCE_ALLOCATION:
                # Redistribuir recursos
                logger.info(f"Applying resource allocation optimization: {optimization.description}")
            
            optimization.applied = True
            optimization.applied_at = datetime.now()
            self.active_optimizations[optimization.optimization_id] = optimization
            self.optimization_history.append(optimization)
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying optimization: {e}")
            return False
    
    def get_optimization_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Genera reporte de optimizaciones.
        
        Args:
            days: Días a analizar
            
        Returns:
            Reporte de optimizaciones
        """
        recent_optimizations = [
            opt for opt in self.optimization_history
            if opt.applied_at and opt.applied_at >= datetime.now() - timedelta(days=days)
        ]
        
        applied_count = sum(1 for opt in recent_optimizations if opt.applied)
        
        by_type = {}
        for opt in recent_optimizations:
            opt_type = opt.optimization_type.value
            if opt_type not in by_type:
                by_type[opt_type] = {"total": 0, "applied": 0}
            by_type[opt_type]["total"] += 1
            if opt.applied:
                by_type[opt_type]["applied"] += 1
        
        return {
            "period_days": days,
            "total_optimizations": len(recent_optimizations),
            "applied_optimizations": applied_count,
            "by_type": by_type,
            "recent_optimizations": [
                {
                    "id": opt.optimization_id,
                    "type": opt.optimization_type.value,
                    "description": opt.description,
                    "applied": opt.applied,
                    "confidence": opt.confidence
                }
                for opt in recent_optimizations[-10:]  # Últimas 10
            ]
        }

