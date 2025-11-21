"""
Sistema de Gamificación para Programa de Referidos

Añade niveles, puntos, badges y leaderboards para motivar
a los referidores y aumentar engagement.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


class GamificationSystem:
    """
    Sistema de gamificación para referidos.
    """
    
    def __init__(self, db_hook=None):
        """
        Inicializa el sistema de gamificación.
        
        Args:
            db_hook: Hook de base de datos
        """
        self.db_hook = db_hook
        self.levels = [
            {"level": 1, "name": "Novato", "points_required": 0, "badge": "🥉", "benefits": []},
            {"level": 2, "name": "Bronce", "points_required": 10, "badge": "🥉", "benefits": ["5% bonus"]},
            {"level": 3, "name": "Plata", "points_required": 25, "badge": "🥈", "benefits": ["10% bonus", "Badge exclusivo"]},
            {"level": 4, "name": "Oro", "points_required": 50, "badge": "🥇", "benefits": ["15% bonus", "Badge exclusivo", "Soporte prioritario"]},
            {"level": 5, "name": "Platino", "points_required": 100, "badge": "💎", "benefits": ["20% bonus", "Badge exclusivo", "Soporte prioritario", "Acceso VIP"]},
            {"level": 6, "name": "Diamante", "points_required": 250, "badge": "💠", "benefits": ["25% bonus", "Badge exclusivo", "Soporte prioritario", "Acceso VIP", "Recompensas especiales"]}
        ]
    
    def award_points(
        self,
        lead_id: str,
        action: str,
        points: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Otorga puntos por una acción.
        
        Args:
            lead_id: ID del lead
            action: Tipo de acción (referral, engagement, etc.)
            points: Puntos a otorgar
            metadata: Metadata adicional
        
        Returns:
            Dict con resultado
        """
        if not self.db_hook:
            return {"error": "No hay conexión a base de datos"}
        
        try:
            # Obtener puntos actuales
            current = self.db_hook.get_first(
                "SELECT points, level FROM gamification_points WHERE lead_id = %s",
                parameters=(lead_id,)
            )
            
            current_points = current[0] if current else 0
            current_level = current[1] if current else 1
            new_points = current_points + points
            
            # Calcular nuevo nivel
            new_level = self._calculate_level(new_points)
            level_up = new_level > current_level
            
            # Guardar puntos
            if current:
                self.db_hook.run(
                    """
                    UPDATE gamification_points
                    SET 
                        points = %s,
                        level = %s,
                        updated_at = NOW()
                    WHERE lead_id = %s
                    """,
                    parameters=(new_points, new_level, lead_id)
                )
            else:
                self.db_hook.run(
                    """
                    INSERT INTO gamification_points (
                        lead_id, points, level, created_at, updated_at
                    ) VALUES (%s, %s, %s, NOW(), NOW())
                    """,
                    parameters=(lead_id, new_points, new_level)
                )
            
            # Registrar acción
            self.db_hook.run(
                """
                INSERT INTO gamification_actions (
                    lead_id, action, points, metadata, created_at
                ) VALUES (%s, %s, %s, %s, NOW())
                """,
                parameters=(lead_id, action, points, json.dumps(metadata or {}))
            )
            
            result = {
                "success": True,
                "points_awarded": points,
                "total_points": new_points,
                "level": new_level,
                "level_up": level_up
            }
            
            if level_up:
                level_info = self.levels[new_level - 1] if new_level <= len(self.levels) else self.levels[-1]
                result["level_info"] = level_info
                result["message"] = f"¡Subiste al nivel {new_level}: {level_info['name']} {level_info['badge']}!"
            
            return result
            
        except Exception as e:
            logger.error(f"Error otorgando puntos: {e}")
            return {"error": str(e)}
    
    def _calculate_level(self, points: int) -> int:
        """Calcula nivel basado en puntos."""
        for level in reversed(self.levels):
            if points >= level["points_required"]:
                return level["level"]
        return 1
    
    def get_leaderboard(
        self,
        limit: int = 10,
        period: str = "all_time"
    ) -> List[Dict[str, Any]]:
        """
        Obtiene leaderboard de referidores.
        
        Args:
            limit: Número de top referidores
            period: Período (all_time, monthly, weekly)
        
        Returns:
            Lista de referidores ordenados por puntos
        """
        if not self.db_hook:
            return []
        
        try:
            if period == "all_time":
                query = """
                    SELECT 
                        gp.lead_id,
                        ol.email,
                        ol.first_name,
                        gp.points,
                        gp.level,
                        COUNT(r.referral_id) as total_referrals
                    FROM gamification_points gp
                    JOIN organic_leads ol ON gp.lead_id = ol.lead_id
                    LEFT JOIN referrals r ON r.referrer_lead_id = gp.lead_id
                    GROUP BY gp.lead_id, ol.email, ol.first_name, gp.points, gp.level
                    ORDER BY gp.points DESC
                    LIMIT %s
                """
            elif period == "monthly":
                query = """
                    SELECT 
                        gp.lead_id,
                        ol.email,
                        ol.first_name,
                        SUM(ga.points) as points,
                        gp.level,
                        COUNT(r.referral_id) as total_referrals
                    FROM gamification_points gp
                    JOIN organic_leads ol ON gp.lead_id = ol.lead_id
                    LEFT JOIN gamification_actions ga ON gp.lead_id = ga.lead_id
                    AND ga.created_at >= NOW() - INTERVAL '30 days'
                    LEFT JOIN referrals r ON r.referrer_lead_id = gp.lead_id
                    AND r.created_at >= NOW() - INTERVAL '30 days'
                    GROUP BY gp.lead_id, ol.email, ol.first_name, gp.level
                    ORDER BY points DESC
                    LIMIT %s
                """
            else:  # weekly
                query = """
                    SELECT 
                        gp.lead_id,
                        ol.email,
                        ol.first_name,
                        SUM(ga.points) as points,
                        gp.level,
                        COUNT(r.referral_id) as total_referrals
                    FROM gamification_points gp
                    JOIN organic_leads ol ON gp.lead_id = ol.lead_id
                    LEFT JOIN gamification_actions ga ON gp.lead_id = ga.lead_id
                    AND ga.created_at >= NOW() - INTERVAL '7 days'
                    LEFT JOIN referrals r ON r.referrer_lead_id = gp.lead_id
                    AND r.created_at >= NOW() - INTERVAL '7 days'
                    GROUP BY gp.lead_id, ol.email, ol.first_name, gp.level
                    ORDER BY points DESC
                    LIMIT %s
                """
            
            results = self.db_hook.get_records(query, parameters=(limit,))
            
            leaderboard = []
            for rank, row in enumerate(results, 1):
                lead_id, email, first_name, points, level, referrals = row
                level_info = self.levels[level - 1] if level <= len(self.levels) else self.levels[-1]
                
                leaderboard.append({
                    "rank": rank,
                    "lead_id": lead_id,
                    "email": email,
                    "first_name": first_name,
                    "points": int(points or 0),
                    "level": level,
                    "level_name": level_info["name"],
                    "badge": level_info["badge"],
                    "total_referrals": referrals or 0
                })
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error obteniendo leaderboard: {e}")
            return []
    
    def get_user_stats(self, lead_id: str) -> Dict[str, Any]:
        """Obtiene estadísticas de un usuario."""
        if not self.db_hook:
            return {"error": "No hay conexión"}
        
        try:
            # Puntos y nivel
            points_data = self.db_hook.get_first(
                "SELECT points, level FROM gamification_points WHERE lead_id = %s",
                parameters=(lead_id,)
            )
            
            if not points_data:
                return {"error": "Usuario no encontrado"}
            
            points, level = points_data
            level_info = self.levels[level - 1] if level <= len(self.levels) else self.levels[-1]
            
            # Próximo nivel
            next_level = None
            if level < len(self.levels):
                next_level_info = self.levels[level]
                points_needed = next_level_info["points_required"] - points
                next_level = {
                    "level": next_level_info["level"],
                    "name": next_level_info["name"],
                    "points_needed": points_needed,
                    "badge": next_level_info["badge"]
                }
            
            # Referidos
            referrals_count = self.db_hook.get_first(
                """
                SELECT COUNT(*) FROM referrals
                WHERE referrer_lead_id = %s AND status = 'validated'
                """,
                parameters=(lead_id,)
            )[0] or 0
            
            # Recompensas
            rewards_total = self.db_hook.get_first(
                """
                SELECT COALESCE(SUM(reward_amount), 0) FROM referral_rewards
                WHERE referrer_lead_id = %s AND status = 'paid'
                """,
                parameters=(lead_id,)
            )[0] or 0
            
            return {
                "lead_id": lead_id,
                "points": int(points),
                "level": level,
                "level_name": level_info["name"],
                "badge": level_info["badge"],
                "benefits": level_info["benefits"],
                "next_level": next_level,
                "total_referrals": referrals_count,
                "total_rewards": float(rewards_total)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo stats: {e}")
            return {"error": str(e)}


# Schema SQL para gamificación
GAMIFICATION_SCHEMA = """
-- Tabla de puntos de gamificación
CREATE TABLE IF NOT EXISTS gamification_points (
    lead_id VARCHAR(128) PRIMARY KEY REFERENCES organic_leads(lead_id) ON DELETE CASCADE,
    points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Tabla de acciones de gamificación
CREATE TABLE IF NOT EXISTS gamification_actions (
    action_id SERIAL PRIMARY KEY,
    lead_id VARCHAR(128) NOT NULL REFERENCES organic_leads(lead_id) ON DELETE CASCADE,
    action VARCHAR(64) NOT NULL,
    points INTEGER NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gamification_points_level ON gamification_points(level DESC);
CREATE INDEX IF NOT EXISTS idx_gamification_points_points ON gamification_points(points DESC);
CREATE INDEX IF NOT EXISTS idx_gamification_actions_lead ON gamification_actions(lead_id);
CREATE INDEX IF NOT EXISTS idx_gamification_actions_created ON gamification_actions(created_at DESC);
"""

