#!/usr/bin/env python3
"""
Campaign Gamification System
Sistema de gamificación para aumentar engagement en campañas
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
from enum import Enum


class BadgeType(Enum):
    """Tipos de badges"""
    FIRST_COMMENT = "first_comment"
    EARLY_BIRD = "early_bird"
    SOCIAL_SHARER = "social_sharer"
    ENGAGEMENT_MASTER = "engagement_master"
    LOYAL_FAN = "loyal_fan"
    INFLUENCER = "influencer"


class CampaignGamification:
    """
    Sistema de gamificación para campañas
    Implementa puntos, niveles, badges y recompensas
    """
    
    def __init__(self, n8n_base_url: str, api_key: str):
        self.n8n_base_url = n8n_base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        # Configuración de puntos
        self.point_values = {
            "comment": 10,
            "like": 5,
            "share": 20,
            "follow": 30,
            "purchase": 100,
            "referral": 50,
            "early_bird": 25
        }
        
        # Niveles y umbrales
        self.level_thresholds = {
            1: 0,      # Novato
            2: 50,     # Principiante
            3: 150,    # Intermedio
            4: 300,    # Avanzado
            5: 500,    # Experto
            6: 1000,   # Maestro
            7: 2000,   # Leyenda
        }
    
    def award_points(
        self,
        user_id: str,
        action: str,
        campaign_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Otorga puntos por una acción
        
        Args:
            user_id: ID del usuario
            action: Tipo de acción (comment, like, share, etc.)
            campaign_id: ID de la campaña
            metadata: Metadatos adicionales
        
        Returns:
            Dict con información de puntos otorgados
        """
        points = self.point_values.get(action, 0)
        
        # Bonus por early bird (primeros 100 usuarios)
        if metadata and metadata.get("is_early_bird", False):
            points += self.point_values.get("early_bird", 0)
        
        # Obtener estado actual del usuario (en producción vendría de DB)
        user_state = self._get_user_state(user_id, campaign_id)
        
        # Actualizar puntos
        new_points = user_state.get("totalPoints", 0) + points
        new_level = self._calculate_level(new_points)
        
        # Verificar badges
        new_badges = self._check_badges(user_id, action, user_state, new_points)
        
        # Verificar recompensas desbloqueadas
        rewards = self._check_rewards(new_level, user_state.get("level", 1))
        
        return {
            "userId": user_id,
            "campaignId": campaign_id,
            "action": action,
            "pointsAwarded": points,
            "totalPoints": new_points,
            "previousLevel": user_state.get("level", 1),
            "newLevel": new_level,
            "leveledUp": new_level > user_state.get("level", 1),
            "badgesEarned": new_badges,
            "rewardsUnlocked": rewards,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_leaderboard(
        self,
        campaign_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Obtiene leaderboard de la campaña
        
        Args:
            campaign_id: ID de la campaña
            limit: Número de usuarios a retornar
        
        Returns:
            Lista de usuarios ordenados por puntos
        """
        # En producción, esto consultaría la base de datos
        # Por ahora, retornamos estructura de ejemplo
        
        leaderboard = [
            {
                "rank": i + 1,
                "userId": f"user_{i+1}",
                "username": f"Usuario {i+1}",
                "totalPoints": 1000 - (i * 50),
                "level": self._calculate_level(1000 - (i * 50)),
                "badges": self._get_user_badges(f"user_{i+1}"),
                "avatar": f"https://example.com/avatar_{i+1}.jpg"
            }
            for i in range(limit)
        ]
        
        return leaderboard
    
    def get_user_profile(
        self,
        user_id: str,
        campaign_id: str
    ) -> Dict[str, Any]:
        """
        Obtiene perfil completo del usuario
        
        Args:
            user_id: ID del usuario
            campaign_id: ID de la campaña
        
        Returns:
            Dict con perfil completo
        """
        user_state = self._get_user_state(user_id, campaign_id)
        level = self._calculate_level(user_state.get("totalPoints", 0))
        next_level_points = self._get_next_level_points(level)
        progress = self._calculate_progress(user_state.get("totalPoints", 0), level)
        
        return {
            "userId": user_id,
            "campaignId": campaign_id,
            "totalPoints": user_state.get("totalPoints", 0),
            "level": level,
            "levelName": self._get_level_name(level),
            "nextLevelPoints": next_level_points,
            "pointsToNextLevel": next_level_points - user_state.get("totalPoints", 0),
            "progress": progress,
            "badges": self._get_user_badges(user_id),
            "rank": self._get_user_rank(user_id, campaign_id),
            "stats": {
                "comments": user_state.get("commentCount", 0),
                "likes": user_state.get("likeCount", 0),
                "shares": user_state.get("shareCount", 0),
                "referrals": user_state.get("referralCount", 0)
            },
            "rewards": self._get_user_rewards(user_id, level)
        }
    
    def _get_user_state(self, user_id: str, campaign_id: str) -> Dict[str, Any]:
        """Obtiene estado actual del usuario (simplificado)"""
        # En producción, esto consultaría la base de datos
        return {
            "totalPoints": 0,
            "level": 1,
            "commentCount": 0,
            "likeCount": 0,
            "shareCount": 0,
            "referralCount": 0,
            "badges": []
        }
    
    def _calculate_level(self, points: int) -> int:
        """Calcula nivel basado en puntos"""
        for level, threshold in sorted(self.level_thresholds.items(), reverse=True):
            if points >= threshold:
                return level
        return 1
    
    def _get_level_name(self, level: int) -> str:
        """Obtiene nombre del nivel"""
        names = {
            1: "Novato",
            2: "Principiante",
            3: "Intermedio",
            4: "Avanzado",
            5: "Experto",
            6: "Maestro",
            7: "Leyenda"
        }
        return names.get(level, "Novato")
    
    def _get_next_level_points(self, current_level: int) -> int:
        """Obtiene puntos necesarios para el siguiente nivel"""
        next_level = current_level + 1
        return self.level_thresholds.get(next_level, 9999)
    
    def _calculate_progress(self, points: int, level: int) -> float:
        """Calcula progreso hacia el siguiente nivel (0-1)"""
        current_threshold = self.level_thresholds.get(level, 0)
        next_threshold = self._get_next_level_points(level)
        
        if next_threshold == current_threshold:
            return 1.0
        
        progress = (points - current_threshold) / (next_threshold - current_threshold)
        return max(0, min(1, progress))
    
    def _check_badges(
        self,
        user_id: str,
        action: str,
        user_state: Dict[str, Any],
        new_points: int
    ) -> List[Dict[str, Any]]:
        """Verifica si el usuario ganó nuevos badges"""
        new_badges = []
        
        # Badge: Primer comentario
        if action == "comment" and user_state.get("commentCount", 0) == 0:
            new_badges.append({
                "type": BadgeType.FIRST_COMMENT.value,
                "name": "Primer Comentario",
                "description": "Comentaste por primera vez",
                "icon": "💬"
            })
        
        # Badge: Early Bird
        if new_points >= 25 and "early_bird" not in [b.get("type") for b in user_state.get("badges", [])]:
            new_badges.append({
                "type": BadgeType.EARLY_BIRD.value,
                "name": "Early Bird",
                "description": "Fuiste uno de los primeros",
                "icon": "🐦"
            })
        
        # Badge: Social Sharer
        if user_state.get("shareCount", 0) >= 5:
            new_badges.append({
                "type": BadgeType.SOCIAL_SHARER.value,
                "name": "Social Sharer",
                "description": "Compartiste 5 veces",
                "icon": "📤"
            })
        
        return new_badges
    
    def _get_user_badges(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene badges del usuario"""
        # Simplificado
        return []
    
    def _get_user_rank(self, user_id: str, campaign_id: str) -> int:
        """Obtiene ranking del usuario"""
        # Simplificado
        return 0
    
    def _check_rewards(self, new_level: int, previous_level: int) -> List[Dict[str, Any]]:
        """Verifica recompensas desbloqueadas"""
        rewards = []
        
        if new_level > previous_level:
            # Recompensas por nivel
            level_rewards = {
                3: {"type": "discount", "value": 10, "description": "10% de descuento"},
                5: {"type": "discount", "value": 15, "description": "15% de descuento"},
                7: {"type": "discount", "value": 20, "description": "20% de descuento + acceso VIP"}
            }
            
            for level in range(previous_level + 1, new_level + 1):
                if level in level_rewards:
                    rewards.append(level_rewards[level])
        
        return rewards
    
    def _get_user_rewards(self, user_id: str, level: int) -> List[Dict[str, Any]]:
        """Obtiene recompensas disponibles del usuario"""
        # Simplificado
        return []


def main():
    """Ejemplo de uso"""
    gamification = CampaignGamification(
        n8n_base_url="https://your-n8n.com",
        api_key="your_api_key"
    )
    
    # Otorgar puntos
    result = gamification.award_points(
        user_id="user_123",
        action="comment",
        campaign_id="campaign_123",
        metadata={"is_early_bird": True}
    )
    
    print("=== Puntos Otorgados ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Obtener perfil
    profile = gamification.get_user_profile("user_123", "campaign_123")
    print("\n=== Perfil de Usuario ===")
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    
    # Leaderboard
    leaderboard = gamification.get_leaderboard("campaign_123", limit=5)
    print("\n=== Leaderboard ===")
    print(json.dumps(leaderboard, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

