"""
Módulo para análisis de atribución multi-touch de conversiones.
"""
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class AttributionModel(Enum):
    """Modelos de atribución disponibles"""
    FIRST_TOUCH = 'first_touch'
    LAST_TOUCH = 'last_touch'
    LINEAR = 'linear'
    TIME_DECAY = 'time_decay'
    POSITION_BASED = 'position_based'


@dataclass
class AttributionResult:
    """Resultado de atribución para un touchpoint"""
    touchpoint: str
    attribution: float
    model: AttributionModel


@dataclass
class AttributionReport:
    """Reporte completo de atribución"""
    by_channel: Dict[str, float]
    by_model: Dict[str, Dict[str, float]]
    avg_touchpoints: float
    most_effective_channel: Optional[str]


class AttributionAnalyzer:
    """
    Analiza atribución de conversiones en múltiples touchpoints.
    
    Attributes:
        modelos_atribucion: Configuración de modelos de atribución
    """
    
    def __init__(self):
        """Inicializa el analizador de atribución"""
        self.modelos_atribucion = {
            AttributionModel.FIRST_TOUCH: {
                'peso_primero': 1.0,
                'peso_otros': 0.0
            },
            AttributionModel.LAST_TOUCH: {
                'peso_primero': 0.0,
                'peso_ultimo': 1.0,
                'peso_otros': 0.0
            },
            AttributionModel.LINEAR: {
                'peso_igual': True
            },
            AttributionModel.TIME_DECAY: {
                'decay_factor': 0.5
            },
            AttributionModel.POSITION_BASED: {
                'peso_primero': 0.4,
                'peso_ultimo': 0.4,
                'peso_otros': 0.2
            }
        }
        logger.info("AttributionAnalyzer inicializado")
    
    def calcular_atribucion(self, 
                           touchpoints: List[str], 
                           modelo: AttributionModel = AttributionModel.POSITION_BASED) -> Dict[str, float]:
        """
        Calcula atribución de conversión según el modelo especificado.
        
        Args:
            touchpoints: Lista de touchpoints en orden cronológico
            modelo: Modelo de atribución a usar
        
        Returns:
            Diccionario con atribución por touchpoint
        """
        if not touchpoints:
            logger.warning("Lista de touchpoints vacía")
            return {}
        
        config = self.modelos_atribucion.get(modelo, self.modelos_atribucion[AttributionModel.POSITION_BASED])
        
        try:
            if modelo == AttributionModel.FIRST_TOUCH:
                return self._atribucion_first_touch(touchpoints)
            elif modelo == AttributionModel.LAST_TOUCH:
                return self._atribucion_last_touch(touchpoints)
            elif modelo == AttributionModel.LINEAR:
                return self._atribucion_linear(touchpoints)
            elif modelo == AttributionModel.TIME_DECAY:
                return self._atribucion_time_decay(touchpoints, config['decay_factor'])
            else:  # POSITION_BASED
                return self._atribucion_position_based(touchpoints, config)
        except Exception as e:
            logger.error(f"Error calculando atribución: {e}")
            return {}
    
    def _atribucion_first_touch(self, touchpoints: List[str]) -> Dict[str, float]:
        """Atribuye 100% al primer touchpoint"""
        atribucion = {tp: 0.0 for tp in touchpoints}
        atribucion[touchpoints[0]] = 1.0
        return atribucion
    
    def _atribucion_last_touch(self, touchpoints: List[str]) -> Dict[str, float]:
        """Atribuye 100% al último touchpoint"""
        atribucion = {tp: 0.0 for tp in touchpoints}
        atribucion[touchpoints[-1]] = 1.0
        return atribucion
    
    def _atribucion_linear(self, touchpoints: List[str]) -> Dict[str, float]:
        """Atribuye igualmente a todos los touchpoints"""
        peso = 1.0 / len(touchpoints)
        return {tp: peso for tp in touchpoints}
    
    def _atribucion_time_decay(self, touchpoints: List[str], decay_factor: float) -> Dict[str, float]:
        """Atribuye más peso a touchpoints más recientes"""
        pesos = []
        total = 0
        
        for i, tp in enumerate(touchpoints):
            peso = decay_factor ** (len(touchpoints) - i - 1)
            pesos.append(peso)
            total += peso
        
        return {tp: peso / total for tp, peso in zip(touchpoints, pesos)}
    
    def _atribucion_position_based(self, touchpoints: List[str], config: Dict) -> Dict[str, float]:
        """Atribuye 40% al primero, 40% al último, 20% a los demás"""
        if len(touchpoints) == 1:
            return {touchpoints[0]: 1.0}
        
        atribucion = {}
        atribucion[touchpoints[0]] = config['peso_primero']
        atribucion[touchpoints[-1]] = config['peso_ultimo']
        
        peso_medio = config['peso_otros'] / max(len(touchpoints) - 2, 1)
        for tp in touchpoints[1:-1]:
            atribucion[tp] = peso_medio
        
        return atribucion
    
    def generar_reporte_atribucion(self, conversiones: List[Dict]) -> AttributionReport:
        """
        Genera reporte completo de atribución.
        
        Args:
            conversiones: Lista de diccionarios con información de conversiones
        
        Returns:
            AttributionReport con el análisis completo
        """
        if not conversiones:
            logger.warning("Lista de conversiones vacía")
            return AttributionReport(
                by_channel={},
                by_model={},
                avg_touchpoints=0.0,
                most_effective_channel=None
            )
        
        reporte_por_modelo: Dict[str, Dict[str, float]] = {}
        total_touchpoints = 0
        
        for conversion in conversiones:
            touchpoints = conversion.get('touchpoints', [])
            valor = conversion.get('valor', 0)
            total_touchpoints += len(touchpoints)
            
            # Atribución por modelo
            for modelo in AttributionModel:
                atribucion = self.calcular_atribucion(touchpoints, modelo)
                modelo_key = modelo.value
                
                if modelo_key not in reporte_por_modelo:
                    reporte_por_modelo[modelo_key] = {}
                
                for canal, peso in atribucion.items():
                    if canal not in reporte_por_modelo[modelo_key]:
                        reporte_por_modelo[modelo_key][canal] = 0
                    reporte_por_modelo[modelo_key][canal] += peso * valor
        
        # Calcular promedio de touchpoints
        avg_touchpoints = total_touchpoints / len(conversiones) if conversiones else 0
        
        # Determinar canal más efectivo (usando position_based)
        most_effective_channel = None
        if AttributionModel.POSITION_BASED.value in reporte_por_modelo:
            canales = reporte_por_modelo[AttributionModel.POSITION_BASED.value]
            if canales:
                most_effective_channel = max(canales.items(), key=lambda x: x[1])[0]
        
        # Consolidar por canal (usando position_based como default)
        by_channel = reporte_por_modelo.get(
            AttributionModel.POSITION_BASED.value,
            {}
        )
        
        return AttributionReport(
            by_channel=by_channel,
            by_model=reporte_por_modelo,
            avg_touchpoints=avg_touchpoints,
            most_effective_channel=most_effective_channel
        )




