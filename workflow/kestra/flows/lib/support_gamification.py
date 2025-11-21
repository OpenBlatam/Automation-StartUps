"""
Sistema de Gamificación para Agentes.

Implementa puntos, badges, niveles y rankings para motivar agentes.
"""
import logging
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class BadgeType(Enum):
    """Tipos de badges."""
    RESOLUTION = "resolution"
    SPEED = "speed"
    SATISFACTION = "satisfaction"
    VOLUME = "volume"
    CONSISTENCY = "consistency"
    COLLABORATION = "collaboration"
    SPECIAL = "special"


class AchievementLevel(Enum):
    """Niveles de logro."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


@dataclass
class Badge:
    """Badge de logro."""
    badge_id: str
    name: str
    description: str
    badge_type: BadgeType
    icon_url: Optional[str] = None
    points_required: int = 0
    rarity: str = "common"  # common, rare, epic, legendary


@dataclass
class AgentScore:
    """Puntuación de agente."""
    agent_id: str
    agent_name: str
    
    # Puntos totales
    total_points: int = 0
    current_level: int = 1
    
    # Métricas
    tickets_resolved: int = 0
    avg_resolution_time: float = 0.0
    avg_satisfaction: float = 0.0
    tickets_this_week: int = 0
    tickets_this_month: int = 0
    
    # Badges
    badges: List[str] = field(default_factory=list)
    achievements: Dict[str, AchievementLevel] = field(default_factory=dict)
    
    # Rankings
    weekly_rank: int = 0
    monthly_rank: int = 0
    all_time_rank: int = 0
    
    # Metadata
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ScoringRule:
    """Regla de puntuación."""
    rule_id: str
    name: str
    description: str
    points: int
    condition: callable  # Función que evalúa si se cumple
    cooldown_hours: int = 0  # Tiempo entre aplicaciones
    max_per_day: int = 0  # Máximo por día (0 = ilimitado)


class GamificationEngine:
    """Motor de gamificación."""
    
    def __init__(self):
        """Inicializa motor de gamificación."""
        self.agent_scores: Dict[str, AgentScore] = {}
        self.badges: Dict[str, Badge] = {}
        self.scoring_rules: List[ScoringRule] = []
        self.last_scores: Dict[str, Dict[str, datetime]] = {}  # Agent -> Rule -> Last applied
        
        self._initialize_default_badges()
        self._initialize_default_rules()
    
    def _initialize_default_badges(self):
        """Inicializa badges por defecto."""
        default_badges = [
            Badge("first-ticket", "Primer Ticket", "Resolvió su primer ticket", BadgeType.RESOLUTION, points_required=1),
            Badge("speed-demon", "Demonio de Velocidad", "Resolvió 10 tickets en menos de 1 hora", BadgeType.SPEED, points_required=100, rarity="rare"),
            Badge("satisfaction-master", "Maestro de Satisfacción", "Promedio de satisfacción > 4.5", BadgeType.SATISFACTION, points_required=200, rarity="epic"),
            Badge("volume-king", "Rey del Volumen", "Resolvió 100 tickets en un mes", BadgeType.VOLUME, points_required=500, rarity="legendary"),
            Badge("collaborator", "Colaborador", "Colaboró en 20 tickets", BadgeType.COLLABORATION, points_required=150),
        ]
        
        for badge in default_badges:
            self.badges[badge.badge_id] = badge
    
    def _initialize_default_rules(self):
        """Inicializa reglas de puntuación por defecto."""
        rules = [
            ScoringRule(
                "resolve-ticket",
                "Resolver Ticket",
                "Puntos por resolver un ticket",
                10,
                lambda event: event.get("action") == "resolve",
                max_per_day=50
            ),
            ScoringRule(
                "fast-resolution",
                "Resolución Rápida",
                "Puntos por resolver rápido (< 1 hora)",
                20,
                lambda event: event.get("action") == "resolve" and event.get("resolution_time_minutes", 999) < 60,
                max_per_day=20
            ),
            ScoringRule(
                "high-satisfaction",
                "Alta Satisfacción",
                "Puntos por satisfacción alta (>= 5)",
                15,
                lambda event: event.get("action") == "resolve" and event.get("satisfaction_score", 0) >= 5,
                max_per_day=30
            ),
            ScoringRule(
                "collaboration",
                "Colaboración",
                "Puntos por colaborar en ticket",
                5,
                lambda event: event.get("action") == "collaborate",
                max_per_day=10
            ),
        ]
        
        self.scoring_rules = rules
    
    def register_badge(self, badge: Badge):
        """Registra un badge."""
        self.badges[badge.badge_id] = badge
    
    def register_rule(self, rule: ScoringRule):
        """Registra una regla de puntuación."""
        self.scoring_rules.append(rule)
    
    def process_event(self, event: Dict[str, Any]):
        """
        Procesa evento y actualiza puntuación.
        
        Args:
            event: Evento con información (action, agent_id, ticket_id, etc.)
        """
        agent_id = event.get("agent_id")
        if not agent_id:
            return
        
        # Obtener o crear score
        if agent_id not in self.agent_scores:
            self.agent_scores[agent_id] = AgentScore(
                agent_id=agent_id,
                agent_name=event.get("agent_name", "Unknown")
            )
        
        score = self.agent_scores[agent_id]
        
        # Aplicar reglas de puntuación
        points_earned = 0
        for rule in self.scoring_rules:
            if self._should_apply_rule(rule, agent_id, event):
                points_earned += rule.points
                score.total_points += rule.points
                
                # Registrar aplicación
                if agent_id not in self.last_scores:
                    self.last_scores[agent_id] = {}
                self.last_scores[agent_id][rule.rule_id] = datetime.now()
        
        # Actualizar métricas
        self._update_metrics(score, event)
        
        # Verificar badges
        self._check_badges(score, event)
        
        # Actualizar nivel
        self._update_level(score)
        
        # Actualizar timestamp
        score.last_updated = datetime.now()
        
        logger.info(f"Agent {agent_id} earned {points_earned} points")
    
    def _should_apply_rule(
        self,
        rule: ScoringRule,
        agent_id: str,
        event: Dict[str, Any]
    ) -> bool:
        """Verifica si se debe aplicar una regla."""
        # Verificar condición
        if not rule.condition(event):
            return False
        
        # Verificar cooldown
        if agent_id in self.last_scores:
            last_applied = self.last_scores[agent_id].get(rule.rule_id)
            if last_applied:
                if rule.cooldown_hours > 0:
                    hours_since = (datetime.now() - last_applied).total_seconds() / 3600
                    if hours_since < rule.cooldown_hours:
                        return False
        
        # Verificar máximo por día
        if rule.max_per_day > 0:
            today = datetime.now().date()
            today_applications = sum(
                1 for applied in self.last_scores.get(agent_id, {}).values()
                if applied.date() == today
            )
            if today_applications >= rule.max_per_day:
                return False
        
        return True
    
    def _update_metrics(self, score: AgentScore, event: Dict[str, Any]):
        """Actualiza métricas del agente."""
        action = event.get("action")
        
        if action == "resolve":
            score.tickets_resolved += 1
            
            resolution_time = event.get("resolution_time_minutes", 0)
            # Actualizar promedio
            total_time = score.avg_resolution_time * (score.tickets_resolved - 1) + resolution_time
            score.avg_resolution_time = total_time / score.tickets_resolved
            
            satisfaction = event.get("satisfaction_score")
            if satisfaction:
                # Actualizar promedio de satisfacción
                current_avg = score.avg_satisfaction or 0
                count = score.tickets_resolved
                score.avg_satisfaction = ((current_avg * (count - 1)) + satisfaction) / count
        
        # Actualizar contadores semanales/mensuales
        event_date = event.get("timestamp", datetime.now())
        if isinstance(event_date, str):
            event_date = datetime.fromisoformat(event_date)
        
        if event_date >= datetime.now() - timedelta(days=7):
            score.tickets_this_week += 1
        
        if event_date >= datetime.now() - timedelta(days=30):
            score.tickets_this_month += 1
    
    def _check_badges(self, score: AgentScore, event: Dict[str, Any]):
        """Verifica y otorga badges."""
        for badge_id, badge in self.badges.items():
            if badge_id in score.badges:
                continue  # Ya tiene el badge
            
            # Verificar si cumple requisitos
            if self._meets_badge_requirements(badge, score, event):
                score.badges.append(badge_id)
                logger.info(f"Agent {score.agent_id} earned badge: {badge.name}")
    
    def _meets_badge_requirements(
        self,
        badge: Badge,
        score: AgentScore,
        event: Dict[str, Any]
    ) -> bool:
        """Verifica si cumple requisitos de badge."""
        if badge.badge_type == BadgeType.RESOLUTION:
            if badge.badge_id == "first-ticket":
                return score.tickets_resolved >= 1
        
        elif badge.badge_type == BadgeType.SPEED:
            if badge.badge_id == "speed-demon":
                # Lógica compleja - verificar últimos 10 tickets
                return False  # Implementar lógica
        
        elif badge.badge_type == BadgeType.SATISFACTION:
            if badge.badge_id == "satisfaction-master":
                return score.avg_satisfaction >= 4.5
        
        elif badge.badge_type == BadgeType.VOLUME:
            if badge.badge_id == "volume-king":
                return score.tickets_this_month >= 100
        
        # Verificar por puntos
        if badge.points_required > 0:
            return score.total_points >= badge.points_required
        
        return False
    
    def _update_level(self, score: AgentScore):
        """Actualiza nivel basado en puntos."""
        # 100 puntos por nivel
        new_level = (score.total_points // 100) + 1
        if new_level > score.current_level:
            score.current_level = new_level
            logger.info(f"Agent {score.agent_id} leveled up to {new_level}")
    
    def get_leaderboard(
        self,
        period: str = "all_time",
        limit: int = 10
    ) -> List[AgentScore]:
        """
        Obtiene leaderboard.
        
        Args:
            period: 'weekly', 'monthly', 'all_time'
            limit: Número de agentes a retornar
            
        Returns:
            Lista de scores ordenados
        """
        scores = list(self.agent_scores.values())
        
        if period == "weekly":
            scores = [s for s in scores if s.tickets_this_week > 0]
            scores.sort(key=lambda s: s.tickets_this_week, reverse=True)
        elif period == "monthly":
            scores = [s for s in scores if s.tickets_this_month > 0]
            scores.sort(key=lambda s: s.tickets_this_month, reverse=True)
        else:
            scores.sort(key=lambda s: s.total_points, reverse=True)
        
        # Actualizar rankings
        for i, score in enumerate(scores[:limit], 1):
            if period == "weekly":
                score.weekly_rank = i
            elif period == "monthly":
                score.monthly_rank = i
            else:
                score.all_time_rank = i
        
        return scores[:limit]
    
    def get_agent_score(self, agent_id: str) -> Optional[AgentScore]:
        """Obtiene score de un agente."""
        return self.agent_scores.get(agent_id)
    
    def get_agent_badges(self, agent_id: str) -> List[Badge]:
        """Obtiene badges de un agente."""
        score = self.agent_scores.get(agent_id)
        if not score:
            return []
        
        return [self.badges[badge_id] for badge_id in score.badges if badge_id in self.badges]

