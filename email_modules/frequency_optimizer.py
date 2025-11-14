"""
Módulo para optimización de frecuencia de envío según engagement.
"""
import logging
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class EngagementLevel(Enum):
    """Niveles de engagement"""
    HIGH = 'alto_engagement'
    MEDIUM = 'medio_engagement'
    LOW = 'bajo_engagement'
    INACTIVE = 'inactivo'


@dataclass
class FrequencyConfig:
    """Configuración de frecuencia"""
    categoria: EngagementLevel
    frecuencia_semanal: float
    dias_recomendados: List[str]
    razon: str


@dataclass
class FrequencyAdjustment:
    """Ajuste de frecuencia"""
    accion: str  # 'reducir', 'aumentar', 'mantener'
    frecuencia_anterior: float
    frecuencia_nueva: float
    razon: str


class FrequencyOptimizer:
    """
    Optimiza frecuencia de envío según engagement.
    
    Attributes:
        frecuencias_optimas: Configuración de frecuencias óptimas por nivel
    """
    
    def __init__(self):
        """Inicializa el optimizador de frecuencia"""
        self.frecuencias_optimas = {
            EngagementLevel.HIGH: {
                'frecuencia_semanal': 3,
                'dias': ['martes', 'jueves', 'sabado']
            },
            EngagementLevel.MEDIUM: {
                'frecuencia_semanal': 2,
                'dias': ['martes', 'viernes']
            },
            EngagementLevel.LOW: {
                'frecuencia_semanal': 1,
                'dias': ['martes']
            },
            EngagementLevel.INACTIVE: {
                'frecuencia_semanal': 0.5,  # Cada 2 semanas
                'dias': ['martes']
            }
        }
        logger.info("FrequencyOptimizer inicializado")
    
    def determinar_frecuencia_optima(self, usuario: Dict) -> FrequencyConfig:
        """
        Determina frecuencia óptima para usuario.
        
        Args:
            usuario: Diccionario con datos del usuario
        
        Returns:
            FrequencyConfig con la configuración óptima
        """
        engagement = usuario.get('engagement_score', 0)
        
        if not isinstance(engagement, (int, float)):
            logger.warning(f"Engagement score inválido: {engagement}, usando default")
            engagement = 0.4
        
        # Determinar categoría
        if engagement >= 0.7:
            categoria = EngagementLevel.HIGH
        elif engagement >= 0.4:
            categoria = EngagementLevel.MEDIUM
        elif engagement >= 0.2:
            categoria = EngagementLevel.LOW
        else:
            categoria = EngagementLevel.INACTIVE
        
        config = self.frecuencias_optimas.get(
            categoria,
            self.frecuencias_optimas[EngagementLevel.MEDIUM]
        )
        
        razon = self._generar_razon(categoria, engagement)
        
        return FrequencyConfig(
            categoria=categoria,
            frecuencia_semanal=config['frecuencia_semanal'],
            dias_recomendados=config['dias'],
            razon=razon
        )
    
    def _generar_razon(self, categoria: EngagementLevel, engagement: float) -> str:
        """Genera razón para la frecuencia recomendada"""
        razones = {
            EngagementLevel.HIGH: f'Tu engagement es alto ({engagement*100:.0f}%) - puedes recibir más contenido',
            EngagementLevel.MEDIUM: f'Tu engagement es medio ({engagement*100:.0f}%) - frecuencia estándar recomendada',
            EngagementLevel.LOW: f'Tu engagement es bajo ({engagement*100:.0f}%) - reducir frecuencia para evitar spam',
            EngagementLevel.INACTIVE: f'Tu engagement es muy bajo ({engagement*100:.0f}%) - frecuencia mínima para reactivación'
        }
        
        return razones.get(categoria, 'Frecuencia estándar recomendada')
    
    def ajustar_frecuencia_dinamica(self, 
                                    usuario: Dict, 
                                    metricas_recientes: Dict) -> FrequencyAdjustment:
        """
        Ajusta frecuencia dinámicamente según métricas recientes.
        
        Args:
            usuario: Diccionario con datos del usuario
            metricas_recientes: Diccionario con métricas recientes
        
        Returns:
            FrequencyAdjustment con el ajuste recomendado
        """
        tasa_baja = metricas_recientes.get('tasa_baja', 0)
        tasa_apertura = metricas_recientes.get('tasa_apertura', 0)
        
        frecuencia_actual = self.determinar_frecuencia_optima(usuario)
        frecuencia_anterior = frecuencia_actual.frecuencia_semanal
        
        # Si tasa de baja es alta, reducir frecuencia
        if tasa_baja > 0.01:
            nueva_frecuencia = frecuencia_anterior * 0.5
            return FrequencyAdjustment(
                accion='reducir',
                frecuencia_anterior=frecuencia_anterior,
                frecuencia_nueva=nueva_frecuencia,
                razon='Tasa de baja alta - reducir frecuencia'
            )
        
        # Si tasa de apertura es muy baja, reducir frecuencia
        elif tasa_apertura < 0.10:
            nueva_frecuencia = frecuencia_anterior * 0.7
            return FrequencyAdjustment(
                accion='reducir',
                frecuencia_anterior=frecuencia_anterior,
                frecuencia_nueva=nueva_frecuencia,
                razon='Tasa de apertura baja - reducir frecuencia'
            )
        
        # Si todo va bien, mantener o aumentar ligeramente
        elif tasa_apertura > 0.30 and tasa_baja < 0.005:
            nueva_frecuencia = min(frecuencia_anterior * 1.2, 4)
            return FrequencyAdjustment(
                accion='aumentar',
                frecuencia_anterior=frecuencia_anterior,
                frecuencia_nueva=nueva_frecuencia,
                razon='Métricas excelentes - puede aumentar frecuencia'
            )
        
        return FrequencyAdjustment(
            accion='mantener',
            frecuencia_anterior=frecuencia_anterior,
            frecuencia_nueva=frecuencia_anterior,
            razon='Métricas estables - mantener frecuencia'
        )




