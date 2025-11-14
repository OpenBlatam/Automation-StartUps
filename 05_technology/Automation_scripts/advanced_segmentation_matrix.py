"""
Matriz de Segmentación Avanzada Multi-Criterio
Sistema de análisis de mercado y segmentación estratégica

Criterios de Segmentación:
1. Firmográficos: industria, tamaño, geografía, madurez digital
2. Comportamentales: nivel de adopción tecnológica, urgencia del problema
3. Psicográficos: apetito por innovación, aversión al riesgo

Sistema de Scoring de Atractivo:
- Tamaño del mercado
- Crecimiento potencial
- Accesibilidad
- Competencia
- Ajuste de producto
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
from collections import defaultdict
from datetime import datetime
import csv
from io import StringIO

# Intentar importar pandas (opcional)
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


# ============================================================================
# ENUMS Y DEFINICIONES
# ============================================================================

class Industria(Enum):
    """Categorías de industria"""
    TECNOLOGIA = "Tecnología"
    FINANZAS = "Servicios Financieros"
    SALUD = "Salud y Farmacéutica"
    RETAIL = "Retail y E-commerce"
    MANUFACTURA = "Manufactura"
    EDUCACION = "Educación"
    CONSULTORIA = "Consultoría y Servicios Profesionales"
    LOGISTICA = "Logística y Transporte"
    ENERGIA = "Energía y Utilities"
    REAL_ESTATE = "Real Estate y Construcción"
    MEDIOS = "Medios y Entretenimiento"
    GOBIERNO = "Gobierno y Sector Público"


class TamanoEmpresa(Enum):
    """Tamaño de empresa por número de empleados"""
    STARTUP = "Startup (1-10)"
    PEQUENA = "Pequeña (11-50)"
    MEDIANA = "Mediana (51-250)"
    GRANDE = "Grande (251-1000)"
    ENTERPRISE = "Enterprise (1000+)"


class Geografia(Enum):
    """Regiones geográficas"""
    LATAM = "Latinoamérica"
    NORTE_AMERICA = "Norte América"
    EUROPA = "Europa"
    ASIA_PACIFICO = "Asia-Pacífico"
    AFRICA = "África y Medio Oriente"
    GLOBAL = "Global/Multi-región"


class MadurezDigital(Enum):
    """Nivel de madurez digital"""
    INICIAL = "Inicial (0-2)"
    EMERGENTE = "Emergente (3-5)"
    AVANZADO = "Avanzado (6-8)"
    LIDER = "Líder (9-10)"


class AdopcionTecnologica(Enum):
    """Nivel de adopción tecnológica"""
    REZAGADO = "Rezagado (Laggard)"
    MAYORIA_TARDIA = "Mayoría Tardía"
    MAYORIA_TEMPRANA = "Mayoría Temprana"
    ADOPTADOR_TEMPRANO = "Adoptador Temprano"
    INNOVADOR = "Innovador"


class UrgenciaProblema(Enum):
    """Urgencia percibida del problema"""
    BAJA = "Baja (1-3)"
    MEDIA = "Media (4-6)"
    ALTA = "Alta (7-9)"
    CRITICA = "Crítica (10)"


class ApetitoInnovacion(Enum):
    """Apetito por innovación"""
    CONSERVADOR = "Conservador (1-3)"
    MODERADO = "Moderado (4-6)"
    ALTO = "Alto (7-8)"
    DISRUPTIVO = "Disruptivo (9-10)"


class AversionRiesgo(Enum):
    """Aversión al riesgo"""
    ALTA = "Alta (1-3)"
    MEDIA = "Media (4-6)"
    BAJA = "Baja (7-8)"
    TOLERANTE = "Tolerante al Riesgo (9-10)"


# ============================================================================
# CLASES DE DATOS
# ============================================================================

@dataclass
class CriteriosFirmograficos:
    """Criterios firmográficos de segmentación"""
    industria: Industria
    tamano: TamanoEmpresa
    geografia: Geografia
    madurez_digital: MadurezDigital
    
    def to_dict(self) -> Dict:
        return {
            "industria": self.industria.value,
            "tamano": self.tamano.value,
            "geografia": self.geografia.value,
            "madurez_digital": self.madurez_digital.value
        }


@dataclass
class CriteriosComportamentales:
    """Criterios comportamentales de segmentación"""
    adopcion_tecnologica: AdopcionTecnologica
    urgencia_problema: UrgenciaProblema
    
    def to_dict(self) -> Dict:
        return {
            "adopcion_tecnologica": self.adopcion_tecnologica.value,
            "urgencia_problema": self.urgencia_problema.value
        }


@dataclass
class CriteriosPsicograficos:
    """Criterios psicográficos de segmentación"""
    apetito_innovacion: ApetitoInnovacion
    aversion_riesgo: AversionRiesgo
    
    def to_dict(self) -> Dict:
        return {
            "apetito_innovacion": self.apetito_innovacion.value,
            "aversion_riesgo": self.aversion_riesgo.value
        }


@dataclass
class ScoringAtractivo:
    """Scoring de atractivo del segmento"""
    tamano: float  # 1-10
    crecimiento: float  # 1-10
    accesibilidad: float  # 1-10
    competencia: float  # 1-10 (invertido: 10 = baja competencia)
    ajuste_producto: float  # 1-10
    
    def calcular_score_total(self) -> float:
        """Calcula el score total ponderado"""
        pesos = {
            "tamano": 0.20,
            "crecimiento": 0.25,
            "accesibilidad": 0.15,
            "competencia": 0.20,
            "ajuste_producto": 0.20
        }
        
        return (
            self.tamano * pesos["tamano"] +
            self.crecimiento * pesos["crecimiento"] +
            self.accesibilidad * pesos["accesibilidad"] +
            self.competencia * pesos["competencia"] +
            self.ajuste_producto * pesos["ajuste_producto"]
        )
    
    def calcular_score_riesgo(self) -> float:
        """Calcula score de riesgo (inverso del atractivo en algunos aspectos)"""
        # Mayor competencia y menor accesibilidad = mayor riesgo
        riesgo_competencia = (10 - self.competencia) * 0.4
        riesgo_accesibilidad = (10 - self.accesibilidad) * 0.3
        riesgo_crecimiento = (10 - self.crecimiento) * 0.3
        return (riesgo_competencia + riesgo_accesibilidad + riesgo_crecimiento) / 10
    
    def calcular_score_oportunidad(self) -> float:
        """Calcula score de oportunidad"""
        return (self.tamano * 0.3 + self.crecimiento * 0.4 + self.ajuste_producto * 0.3) / 10
    
    def to_dict(self) -> Dict:
        return {
            "tamano": self.tamano,
            "crecimiento": self.crecimiento,
            "accesibilidad": self.accesibilidad,
            "competencia": self.competencia,
            "ajuste_producto": self.ajuste_producto,
            "score_total": self.calcular_score_total(),
            "score_riesgo": self.calcular_score_riesgo(),
            "score_oportunidad": self.calcular_score_oportunidad()
        }


@dataclass
class MetricasMercado:
    """Métricas de tamaño de mercado"""
    tam: float  # Total Addressable Market (en millones USD)
    sam: float  # Serviceable Addressable Market (en millones USD)
    som: float  # Serviceable Obtainable Market (en millones USD)
    tasa_crecimiento_anual: float  # CAGR porcentual
    penetracion_actual: float  # Porcentaje de penetración actual
    
    def calcular_potencial_crecimiento(self) -> float:
        """Calcula el potencial de crecimiento basado en penetración y CAGR"""
        return (self.som / self.sam) * 100 if self.sam > 0 else 0
    
    def to_dict(self) -> Dict:
        return {
            "tam": self.tam,
            "sam": self.sam,
            "som": self.som,
            "tasa_crecimiento_anual": self.tasa_crecimiento_anual,
            "penetracion_actual": self.penetracion_actual,
            "potencial_crecimiento": self.calcular_potencial_crecimiento()
        }


@dataclass
class AnalisisCompetencia:
    """Análisis detallado de competencia"""
    numero_competidores: int
    intensidad_competitiva: float  # 1-10
    diferenciacion_posible: float  # 1-10
    barreras_entrada: float  # 1-10 (10 = altas barreras)
    poder_negociacion_clientes: float  # 1-10
    poder_negociacion_proveedores: float  # 1-10
    
    def calcular_score_competitivo(self) -> float:
        """Calcula score competitivo (mayor = mejor posición)"""
        # Mayor diferenciación y barreras = mejor posición
        # Menor intensidad y poder de negociación = mejor posición
        return (
            self.diferenciacion_posible * 0.3 +
            self.barreras_entrada * 0.25 +
            (10 - self.intensidad_competitiva) * 0.25 +
            (10 - self.poder_negociacion_clientes) * 0.1 +
            (10 - self.poder_negociacion_proveedores) * 0.1
        ) / 10
    
    def to_dict(self) -> Dict:
        return {
            "numero_competidores": self.numero_competidores,
            "intensidad_competitiva": self.intensidad_competitiva,
            "diferenciacion_posible": self.diferenciacion_posible,
            "barreras_entrada": self.barreras_entrada,
            "poder_negociacion_clientes": self.poder_negociacion_clientes,
            "poder_negociacion_proveedores": self.poder_negociacion_proveedores,
            "score_competitivo": self.calcular_score_competitivo()
        }


@dataclass
class Segmento:
    """Representa un segmento de mercado"""
    id: str
    nombre: str
    firmograficos: CriteriosFirmograficos
    comportamentales: CriteriosComportamentales
    psicograficos: CriteriosPsicograficos
    scoring: ScoringAtractivo
    descripcion: str = ""
    caracteristicas_clave: List[str] = field(default_factory=list)
    oportunidades: List[str] = field(default_factory=list)
    desafios: List[str] = field(default_factory=list)
    metricas_mercado: Optional[MetricasMercado] = None
    analisis_competencia: Optional[AnalisisCompetencia] = None
    precio_promedio_anual: Optional[float] = None  # En USD
    ciclo_venta_dias: Optional[int] = None
    tasa_conversion_esperada: Optional[float] = None  # Porcentaje
    
    def calcular_score_segmento(self) -> float:
        """Calcula el score total del segmento"""
        return self.scoring.calcular_score_total()
    
    def calcular_score_prioridad(self) -> float:
        """Calcula score de prioridad combinando atractivo, oportunidad y riesgo"""
        score_atractivo = self.scoring.calcular_score_total()
        score_oportunidad = self.scoring.calcular_score_oportunidad()
        score_riesgo = self.scoring.calcular_score_riesgo()
        
        # Prioridad = alta oportunidad + alto atractivo - bajo riesgo
        return (score_atractivo * 0.4 + score_oportunidad * 0.4 + (1 - score_riesgo) * 0.2) * 10
    
    def calcular_roi_esperado(self) -> Optional[float]:
        """Calcula ROI esperado si hay métricas disponibles"""
        if not self.metricas_mercado or not self.precio_promedio_anual:
            return None
        
        # Estimación simplificada: SOM * precio promedio * tasa conversión
        if self.tasa_conversion_esperada:
            clientes_potenciales = (self.metricas_mercado.som / self.precio_promedio_anual) if self.precio_promedio_anual > 0 else 0
            ingresos_potenciales = clientes_potenciales * self.precio_promedio_anual * (self.tasa_conversion_esperada / 100)
            return ingresos_potenciales
        return None
    
    def to_dict(self) -> Dict:
        resultado = {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "firmograficos": self.firmograficos.to_dict(),
            "comportamentales": self.comportamentales.to_dict(),
            "psicograficos": self.psicograficos.to_dict(),
            "scoring": self.scoring.to_dict(),
            "caracteristicas_clave": self.caracteristicas_clave,
            "oportunidades": self.oportunidades,
            "desafios": self.desafios,
            "score_total": self.calcular_score_segmento(),
            "score_prioridad": self.calcular_score_prioridad()
        }
        
        if self.metricas_mercado:
            resultado["metricas_mercado"] = self.metricas_mercado.to_dict()
        if self.analisis_competencia:
            resultado["analisis_competencia"] = self.analisis_competencia.to_dict()
        if self.precio_promedio_anual:
            resultado["precio_promedio_anual"] = self.precio_promedio_anual
        if self.ciclo_venta_dias:
            resultado["ciclo_venta_dias"] = self.ciclo_venta_dias
        if self.tasa_conversion_esperada:
            resultado["tasa_conversion_esperada"] = self.tasa_conversion_esperada
        if self.calcular_roi_esperado():
            resultado["roi_esperado"] = self.calcular_roi_esperado()
        
        return resultado


# ============================================================================
# MATRIZ DE SEGMENTACIÓN
# ============================================================================

class MatrizSegmentacionAvanzada:
    """Sistema de matriz de segmentación avanzada multi-criterio"""
    
    def __init__(self):
        self.segmentos: List[Segmento] = []
        self.analisis_realizado: bool = False
        self.segmento_primario: Optional[Segmento] = None
        self.segmento_secundario: Optional[Segmento] = None
    
    def crear_segmentos_base(self) -> List[Segmento]:
        """Crea segmentos base representativos del mercado"""
        
        segmentos = []
        
        # Segmento 1: Tech Startups Innovadoras (Latam)
        segmentos.append(Segmento(
            id="SEG-001",
            nombre="Tech Startups Innovadoras - Latam",
            descripcion="Startups tecnológicas en Latinoamérica con alta adopción tecnológica y apetito por innovación",
            firmograficos=CriteriosFirmograficos(
                industria=Industria.TECNOLOGIA,
                tamano=TamanoEmpresa.STARTUP,
                geografia=Geografia.LATAM,
                madurez_digital=MadurezDigital.EMERGENTE
            ),
            comportamentales=CriteriosComportamentales(
                adopcion_tecnologica=AdopcionTecnologica.INNOVADOR,
                urgencia_problema=UrgenciaProblema.ALTA
            ),
            psicograficos=CriteriosPsicograficos(
                apetito_innovacion=ApetitoInnovacion.DISRUPTIVO,
                aversion_riesgo=AversionRiesgo.TOLERANTE
            ),
            scoring=ScoringAtractivo(
                tamano=7.5,
                crecimiento=9.0,
                accesibilidad=8.5,
                competencia=6.0,
                ajuste_producto=9.5
            ),
            caracteristicas_clave=[
                "Presupuesto limitado pero flexible",
                "Decisión rápida",
                "Open source y tecnologías modernas",
                "Equipos pequeños y ágiles"
            ],
            oportunidades=[
                "Alto potencial de crecimiento",
                "Referencias virales en ecosistema startup",
                "Casos de uso innovadores",
                "Expansión rápida si hay éxito"
            ],
            desafios=[
                "Presupuesto limitado inicial",
                "Alta tasa de mortalidad",
                "Necesidad de demostrar ROI rápido"
            ]
        ))
        
        # Segmento 2: Medianas Empresas Fintech (Global)
        segmentos.append(Segmento(
            id="SEG-002",
            nombre="Medianas Empresas Fintech - Global",
            descripcion="Empresas fintech medianas con madurez digital avanzada y alta urgencia regulatoria",
            firmograficos=CriteriosFirmograficos(
                industria=Industria.FINANZAS,
                tamano=TamanoEmpresa.MEDIANA,
                geografia=Geografia.GLOBAL,
                madurez_digital=MadurezDigital.AVANZADO
            ),
            comportamentales=CriteriosComportamentales(
                adopcion_tecnologica=AdopcionTecnologica.ADOPTADOR_TEMPRANO,
                urgencia_problema=UrgenciaProblema.CRITICA
            ),
            psicograficos=CriteriosPsicograficos(
                apetito_innovacion=ApetitoInnovacion.ALTO,
                aversion_riesgo=AversionRiesgo.MEDIA
            ),
            scoring=ScoringAtractivo(
                tamano=8.5,
                crecimiento=8.5,
                accesibilidad=7.0,
                competencia=7.5,
                ajuste_producto=9.0
            ),
            caracteristicas_clave=[
                "Presupuesto sólido para compliance",
                "Necesidad de seguridad y escalabilidad",
                "Procesos de aprobación estructurados",
                "Enfoque en ROI medible"
            ],
            oportunidades=[
                "Presupuesto significativo disponible",
                "Necesidad crítica de soluciones",
                "Contratos multi-año",
                "Expansión a múltiples mercados"
            ],
            desafios=[
                "Procesos de venta más largos",
                "Mayor competencia",
                "Requisitos de compliance estrictos"
            ],
            metricas_mercado=MetricasMercado(
                tam=8000.0,   # $8B TAM
                sam=3200.0,   # $3.2B SAM
                som=320.0,    # $320M SOM
                tasa_crecimiento_anual=22.0,
                penetracion_actual=10.0
            ),
            analisis_competencia=AnalisisCompetencia(
                numero_competidores=8,
                intensidad_competitiva=7.0,
                diferenciacion_posible=8.5,
                barreras_entrada=7.5,
                poder_negociacion_clientes=6.0,
                poder_negociacion_proveedores=5.5
            ),
            precio_promedio_anual=85000.0,
            ciclo_venta_dias=90,
            tasa_conversion_esperada=8.5
        ))
        
        # Segmento 3: Enterprise Healthcare (Norte América)
        segmentos.append(Segmento(
            id="SEG-003",
            nombre="Enterprise Healthcare - Norte América",
            descripcion="Grandes empresas de salud con necesidad crítica de digitalización post-COVID",
            firmograficos=CriteriosFirmograficos(
                industria=Industria.SALUD,
                tamano=TamanoEmpresa.ENTERPRISE,
                geografia=Geografia.NORTE_AMERICA,
                madurez_digital=MadurezDigital.AVANZADO
            ),
            comportamentales=CriteriosComportamentales(
                adopcion_tecnologica=AdopcionTecnologica.MAYORIA_TEMPRANA,
                urgencia_problema=UrgenciaProblema.CRITICA
            ),
            psicograficos=CriteriosPsicograficos(
                apetito_innovacion=ApetitoInnovacion.MODERADO,
                aversion_riesgo=AversionRiesgo.ALTA
            ),
            scoring=ScoringAtractivo(
                tamano=9.5,
                crecimiento=7.0,
                accesibilidad=5.0,
                competencia=8.0,
                ajuste_producto=7.5
            ),
            caracteristicas_clave=[
                "Presupuesto muy grande",
                "Procesos de compra complejos y largos",
                "Enfoque en compliance y seguridad",
                "Múltiples stakeholders"
            ],
            oportunidades=[
                "Contratos de gran valor",
                "Relaciones a largo plazo",
                "Oportunidades de upsell",
                "Referencias en industria regulada"
            ],
            desafios=[
                "Ciclos de venta muy largos (12-18 meses)",
                "Alta aversión al riesgo",
                "Múltiples aprobaciones requeridas",
                "Competencia de grandes vendors"
            ]
        ))
        
        # Segmento 4: Retail E-commerce Emergente (Latam)
        segmentos.append(Segmento(
            id="SEG-004",
            nombre="Retail E-commerce Emergente - Latam",
            descripcion="Empresas de retail que están digitalizando sus operaciones en Latinoamérica",
            firmograficos=CriteriosFirmograficos(
                industria=Industria.RETAIL,
                tamano=TamanoEmpresa.MEDIANA,
                geografia=Geografia.LATAM,
                madurez_digital=MadurezDigital.EMERGENTE
            ),
            comportamentales=CriteriosComportamentales(
                adopcion_tecnologica=AdopcionTecnologica.MAYORIA_TEMPRANA,
                urgencia_problema=UrgenciaProblema.ALTA
            ),
            psicograficos=CriteriosPsicograficos(
                apetito_innovacion=ApetitoInnovacion.ALTO,
                aversion_riesgo=AversionRiesgo.MEDIA
            ),
            scoring=ScoringAtractivo(
                tamano=8.0,
                crecimiento=9.5,
                accesibilidad=8.0,
                competencia=7.0,
                ajuste_producto=8.5
            ),
            caracteristicas_clave=[
                "Presupuesto creciente para digitalización",
                "Necesidad de competir con Amazon",
                "Enfoque en experiencia del cliente",
                "Decisiones relativamente rápidas"
            ],
            oportunidades=[
                "Mercado en rápido crecimiento",
                "Necesidad clara de diferenciación",
                "Presupuesto disponible",
                "Casos de uso medibles"
            ],
            desafios=[
                "Margen de error bajo",
                "Necesidad de resultados rápidos",
                "Competencia con grandes players"
            ],
            metricas_mercado=MetricasMercado(
                tam=15000.0,  # $15B TAM
                sam=4500.0,   # $4.5B SAM
                som=450.0,    # $450M SOM
                tasa_crecimiento_anual=25.0,
                penetracion_actual=10.0
            ),
            analisis_competencia=AnalisisCompetencia(
                numero_competidores=12,
                intensidad_competitiva=7.5,
                diferenciacion_posible=8.0,
                barreras_entrada=6.0,
                poder_negociacion_clientes=6.5,
                poder_negociacion_proveedores=5.0
            ),
            precio_promedio_anual=25000.0,
            ciclo_venta_dias=45,
            tasa_conversion_esperada=12.0
        ))
        
        # Segmento 5: Consultorías Digitales (Europa)
        segmentos.append(Segmento(
            id="SEG-005",
            nombre="Consultorías Digitales - Europa",
            descripcion="Consultorías que necesitan herramientas avanzadas para sus clientes",
            firmograficos=CriteriosFirmograficos(
                industria=Industria.CONSULTORIA,
                tamano=TamanoEmpresa.MEDIANA,
                geografia=Geografia.EUROPA,
                madurez_digital=MadurezDigital.AVANZADO
            ),
            comportamentales=CriteriosComportamentales(
                adopcion_tecnologica=AdopcionTecnologica.ADOPTADOR_TEMPRANO,
                urgencia_problema=UrgenciaProblema.MEDIA
            ),
            psicograficos=CriteriosPsicograficos(
                apetito_innovacion=ApetitoInnovacion.ALTO,
                aversion_riesgo=AversionRiesgo.BAJA
            ),
            scoring=ScoringAtractivo(
                tamano=6.5,
                crecimiento=7.5,
                accesibilidad=7.5,
                competencia=6.5,
                ajuste_producto=8.0
            ),
            caracteristicas_clave=[
                "Presupuesto variable por proyecto",
                "Necesidad de white-label",
                "Enfoque en valor para clientes finales",
                "Decisiones basadas en ROI claro"
            ],
            oportunidades=[
                "Acceso a múltiples clientes finales",
                "Modelo de partnership",
                "Casos de uso diversos",
                "Expansión geográfica"
            ],
            desafios=[
                "Presupuesto por proyecto",
                "Necesidad de customización",
                "Competencia con herramientas propias"
            ]
        ))
        
        # Segmento 6: Manufacturing 4.0 (Asia-Pacífico)
        segmentos.append(Segmento(
            id="SEG-006",
            nombre="Manufacturing 4.0 - Asia-Pacífico",
            descripcion="Empresas manufactureras adoptando Industria 4.0 en Asia-Pacífico",
            firmograficos=CriteriosFirmograficos(
                industria=Industria.MANUFACTURA,
                tamano=TamanoEmpresa.GRANDE,
                geografia=Geografia.ASIA_PACIFICO,
                madurez_digital=MadurezDigital.EMERGENTE
            ),
            comportamentales=CriteriosComportamentales(
                adopcion_tecnologica=AdopcionTecnologica.MAYORIA_TEMPRANA,
                urgencia_problema=UrgenciaProblema.ALTA
            ),
            psicograficos=CriteriosPsicograficos(
                apetito_innovacion=ApetitoInnovacion.MODERADO,
                aversion_riesgo=AversionRiesgo.MEDIA
            ),
            scoring=ScoringAtractivo(
                tamano=9.0,
                crecimiento=8.0,
                accesibilidad=6.0,
                competencia=7.5,
                ajuste_producto=7.0
            ),
            caracteristicas_clave=[
                "Presupuesto significativo",
                "Enfoque en eficiencia operativa",
                "Procesos de aprobación estructurados",
                "Necesidad de integración con sistemas legacy"
            ],
            oportunidades=[
                "Mercado grande y creciente",
                "Presupuesto disponible",
                "Necesidad clara de transformación",
                "Contratos multi-año"
            ],
            desafios=[
                "Integración compleja",
                "Ciclos de venta largos",
                "Necesidad de demostrar ROI operativo",
                "Competencia local fuerte"
            ]
        ))
        
        # Segmento 7: EdTech Scale-ups (Global)
        segmentos.append(Segmento(
            id="SEG-007",
            nombre="EdTech Scale-ups - Global",
            descripcion="Empresas de tecnología educativa en fase de escalamiento global",
            firmograficos=CriteriosFirmograficos(
                industria=Industria.EDUCACION,
                tamano=TamanoEmpresa.MEDIANA,
                geografia=Geografia.GLOBAL,
                madurez_digital=MadurezDigital.AVANZADO
            ),
            comportamentales=CriteriosComportamentales(
                adopcion_tecnologica=AdopcionTecnologica.ADOPTADOR_TEMPRANO,
                urgencia_problema=UrgenciaProblema.ALTA
            ),
            psicograficos=CriteriosPsicograficos(
                apetito_innovacion=ApetitoInnovacion.ALTO,
                aversion_riesgo=AversionRiesgo.BAJA
            ),
            scoring=ScoringAtractivo(
                tamano=7.0,
                crecimiento=9.0,
                accesibilidad=8.5,
                competencia=6.0,
                ajuste_producto=9.0
            ),
            caracteristicas_clave=[
                "Presupuesto de crecimiento",
                "Necesidad de escalar rápidamente",
                "Enfoque en experiencia del usuario",
                "Decisiones ágiles"
            ],
            oportunidades=[
                "Alto crecimiento del mercado",
                "Necesidad de diferenciación",
                "Presupuesto disponible",
                "Referencias en sector educativo"
            ],
            desafios=[
                "Presupuesto limitado por crecimiento",
                "Necesidad de resultados rápidos",
                "Competencia con grandes players"
            ]
        ))
        
        # Segmento 8: Enterprise Conservadoras (Global)
        segmentos.append(Segmento(
            id="SEG-008",
            nombre="Enterprise Conservadoras - Global",
            descripcion="Grandes empresas tradicionales con baja adopción tecnológica y alta aversión al riesgo",
            firmograficos=CriteriosFirmograficos(
                industria=Industria.ENERGIA,
                tamano=TamanoEmpresa.ENTERPRISE,
                geografia=Geografia.GLOBAL,
                madurez_digital=MadurezDigital.INICIAL
            ),
            comportamentales=CriteriosComportamentales(
                adopcion_tecnologica=AdopcionTecnologica.REZAGADO,
                urgencia_problema=UrgenciaProblema.BAJA
            ),
            psicograficos=CriteriosPsicograficos(
                apetito_innovacion=ApetitoInnovacion.CONSERVADOR,
                aversion_riesgo=AversionRiesgo.ALTA
            ),
            scoring=ScoringAtractivo(
                tamano=9.5,
                crecimiento=4.0,
                accesibilidad=3.0,
                competencia=5.0,
                ajuste_producto=4.0
            ),
            caracteristicas_clave=[
                "Presupuesto muy grande pero difícil de acceder",
                "Procesos extremadamente largos",
                "Múltiples capas de aprobación",
                "Enfoque en riesgo y compliance"
            ],
            oportunidades=[
                "Contratos de muy alto valor",
                "Relaciones a muy largo plazo",
                "Baja rotación una vez dentro"
            ],
            desafios=[
                "Ciclos de venta extremadamente largos (18-24 meses)",
                "Muy alta aversión al riesgo",
                "Muy difícil acceso",
                "Bajo apetito por innovación"
            ]
        ))
        
        self.segmentos = segmentos
        return segmentos
    
    def analizar_segmentos(self) -> Dict:
        """Analiza todos los segmentos y calcula rankings"""
        
        if not self.segmentos:
            self.crear_segmentos_base()
        
        # Ordenar por score total
        segmentos_ordenados = sorted(
            self.segmentos,
            key=lambda s: s.calcular_score_segmento(),
            reverse=True
        )
        
        # Identificar segmentos primario y secundario
        self.segmento_primario = segmentos_ordenados[0] if segmentos_ordenados else None
        self.segmento_secundario = segmentos_ordenados[1] if len(segmentos_ordenados) > 1 else None
        
        self.analisis_realizado = True
        
        return {
            "total_segmentos": len(self.segmentos),
            "segmento_primario": self.segmento_primario.to_dict() if self.segmento_primario else None,
            "segmento_secundario": self.segmento_secundario.to_dict() if self.segmento_secundario else None,
            "ranking_completo": [s.to_dict() for s in segmentos_ordenados]
        }
    
    def generar_justificacion_estrategica(self) -> Dict:
        """Genera justificación estratégica para segmentos primario y secundario"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        if not self.segmento_primario or not self.segmento_secundario:
            return {"error": "No hay suficientes segmentos para análisis"}
        
        primario = self.segmento_primario
        secundario = self.segmento_secundario
        
        justificacion = {
            "segmento_primario": {
                "segmento": primario.nombre,
                "score_total": primario.calcular_score_segmento(),
                "justificacion": {
                    "razones_estrategicas": [
                        f"Score de atractivo más alto ({primario.calcular_score_segmento():.2f}/10)",
                        f"Excelente ajuste de producto ({primario.scoring.ajuste_producto}/10)",
                        f"Alto crecimiento del mercado ({primario.scoring.crecimiento}/10)",
                        f"Buena accesibilidad ({primario.scoring.accesibilidad}/10)",
                        f"Competencia moderada ({primario.scoring.competencia}/10)"
                    ],
                    "ventajas_competitivas": [
                        "Alta probabilidad de éxito inicial",
                        "Ciclos de venta relativamente cortos",
                        "Alto potencial de referencias",
                        "Casos de uso claros y medibles",
                        "Alineación con perfil de cliente ideal"
                    ],
                    "estrategia_recomendada": [
                        "Enfoque en inbound marketing y contenido",
                        "Programa de early adopters con descuentos",
                        "Casos de estudio rápidos y virales",
                        "Partnerships con aceleradoras e incubadoras",
                        "Modelo de pricing flexible para startups"
                    ],
                    "metricas_clave": [
                        "Tasa de conversión objetivo: >15%",
                        "CAC objetivo: <$2,000",
                        "LTV objetivo: >$50,000",
                        "Tiempo de ciclo de venta: <60 días",
                        "NPS objetivo: >50"
                    ]
                }
            },
            "segmento_secundario": {
                "segmento": secundario.nombre,
                "score_total": secundario.calcular_score_segmento(),
                "justificacion": {
                    "razones_estrategicas": [
                        f"Segundo score más alto ({secundario.calcular_score_segmento():.2f}/10)",
                        f"Tamaño de mercado significativo ({secundario.scoring.tamano}/10)",
                        f"Presupuesto disponible ({secundario.scoring.accesibilidad}/10)",
                        f"Necesidad crítica del problema ({secundario.comportamentales.urgencia_problema.value})",
                        f"Buen ajuste de producto ({secundario.scoring.ajuste_producto}/10)"
                    ],
                    "ventajas_competitivas": [
                        "Mayor valor de contrato promedio",
                        "Relaciones más estables a largo plazo",
                        "Oportunidades de upsell significativas",
                        "Referencias en industria regulada",
                        "Menor tasa de churn"
                    ],
                    "estrategia_recomendada": [
                        "Enfoque en ventas directas y consultivas",
                        "Contenido técnico y casos de estudio profundos",
                        "Programa de pilotos y pruebas de concepto",
                        "Partnerships con consultoras especializadas",
                        "Modelo de pricing enterprise con escalamiento"
                    ],
                    "metricas_clave": [
                        "Tasa de conversión objetivo: >8%",
                        "CAC objetivo: <$15,000",
                        "LTV objetivo: >$200,000",
                        "Tiempo de ciclo de venta: <120 días",
                        "NPS objetivo: >60"
                    ]
                }
            },
            "complementariedad": {
                "sinergias": [
                    "El segmento primario genera casos de estudio para el secundario",
                    "El segmento secundario valida el producto para el primario",
                    "Diversificación de riesgo entre segmentos",
                    "Oportunidades de cross-sell entre segmentos relacionados"
                ],
                "distribucion_recomendada": {
                    "segmento_primario": "60% de recursos de ventas y marketing",
                    "segmento_secundario": "40% de recursos de ventas y marketing"
                },
                "roadmap": [
                    "Año 1: Enfoque principal en segmento primario para validación rápida",
                    "Año 1-2: Desarrollo paralelo del segmento secundario",
                    "Año 2+: Optimización y expansión en ambos segmentos",
                    "Año 3+: Considerar segmentos adicionales basados en aprendizaje"
                ]
            }
        }
        
        return justificacion
    
    def generar_matriz_visual(self) -> str:
        """Genera una representación visual de la matriz de segmentación"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        matriz = "\n" + "="*100 + "\n"
        matriz += "MATRIZ DE SEGMENTACIÓN AVANZADA - ANÁLISIS MULTI-CRITERIO\n"
        matriz += "="*100 + "\n\n"
        
        # Encabezados
        matriz += f"{'Segmento':<40} {'Score':<8} {'Tamaño':<8} {'Crec.':<8} {'Acces.':<8} {'Comp.':<8} {'Ajuste':<8}\n"
        matriz += "-"*100 + "\n"
        
        # Segmentos ordenados
        segmentos_ordenados = sorted(
            self.segmentos,
            key=lambda s: s.calcular_score_segmento(),
            reverse=True
        )
        
        for seg in segmentos_ordenados:
            score = seg.calcular_score_segmento()
            matriz += f"{seg.nombre:<40} {score:>6.2f}  {seg.scoring.tamano:>6.1f}  {seg.scoring.crecimiento:>6.1f}  "
            matriz += f"{seg.scoring.accesibilidad:>6.1f}  {seg.scoring.competencia:>6.1f}  {seg.scoring.ajuste_producto:>6.1f}\n"
        
        matriz += "\n" + "="*100 + "\n"
        
        if self.segmento_primario:
            matriz += f"\n🎯 SEGMENTO PRIMARIO: {self.segmento_primario.nombre}\n"
            matriz += f"   Score Total: {self.segmento_primario.calcular_score_segmento():.2f}/10\n"
        
        if self.segmento_secundario:
            matriz += f"\n📊 SEGMENTO SECUNDARIO: {self.segmento_secundario.nombre}\n"
            matriz += f"   Score Total: {self.segmento_secundario.calcular_score_segmento():.2f}/10\n"
        
        return matriz
    
    def generar_matriz_riesgo_oportunidad(self) -> Dict:
        """Genera matriz de riesgo-oportunidad para todos los segmentos"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        matriz = {
            "alta_oportunidad_bajo_riesgo": [],
            "alta_oportunidad_alto_riesgo": [],
            "baja_oportunidad_bajo_riesgo": [],
            "baja_oportunidad_alto_riesgo": []
        }
        
        for seg in self.segmentos:
            oportunidad = seg.scoring.calcular_score_oportunidad()
            riesgo = seg.scoring.calcular_score_riesgo()
            
            segmento_info = {
                "segmento": seg.nombre,
                "score_oportunidad": oportunidad,
                "score_riesgo": riesgo,
                "score_prioridad": seg.calcular_score_prioridad()
            }
            
            if oportunidad >= 0.7 and riesgo <= 0.4:
                matriz["alta_oportunidad_bajo_riesgo"].append(segmento_info)
            elif oportunidad >= 0.7 and riesgo > 0.4:
                matriz["alta_oportunidad_alto_riesgo"].append(segmento_info)
            elif oportunidad < 0.7 and riesgo <= 0.4:
                matriz["baja_oportunidad_bajo_riesgo"].append(segmento_info)
            else:
                matriz["baja_oportunidad_alto_riesgo"].append(segmento_info)
        
        return matriz
    
    def analisis_comparativo_segmentos(self, segmento_ids: List[str]) -> Dict:
        """Realiza análisis comparativo entre segmentos específicos"""
        
        segmentos_seleccionados = [s for s in self.segmentos if s.id in segmento_ids]
        
        if len(segmentos_seleccionados) < 2:
            return {"error": "Se necesitan al menos 2 segmentos para comparar"}
        
        comparacion = {
            "segmentos_comparados": [s.nombre for s in segmentos_seleccionados],
            "comparacion_scoring": {},
            "fortalezas_debilidades": {},
            "recomendaciones": []
        }
        
        # Comparar scores
        for seg in segmentos_seleccionados:
            comparacion["comparacion_scoring"][seg.nombre] = {
                "score_total": seg.calcular_score_segmento(),
                "score_oportunidad": seg.scoring.calcular_score_oportunidad(),
                "score_riesgo": seg.scoring.calcular_score_riesgo(),
                "score_prioridad": seg.calcular_score_prioridad()
            }
            
            comparacion["fortalezas_debilidades"][seg.nombre] = {
                "fortalezas": seg.oportunidades[:3],
                "debilidades": seg.desafios[:3]
            }
        
        # Generar recomendaciones comparativas
        mejor_score = max(segmentos_seleccionados, key=lambda s: s.calcular_score_segmento())
        mejor_oportunidad = max(segmentos_seleccionados, key=lambda s: s.scoring.calcular_score_oportunidad())
        menor_riesgo = min(segmentos_seleccionados, key=lambda s: s.scoring.calcular_score_riesgo())
        
        comparacion["recomendaciones"] = [
            f"Mejor score total: {mejor_score.nombre}",
            f"Mayor oportunidad: {mejor_oportunidad.nombre}",
            f"Menor riesgo: {menor_riesgo.nombre}",
            "Considerar estrategia dual si los segmentos son complementarios"
        ]
        
        return comparacion
    
    def analizar_canales_distribucion(self) -> Dict:
        """Analiza y recomienda canales de distribución por segmento"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        canales = {}
        
        for seg in self.segmentos:
            canales_segmento = []
            
            # Lógica de recomendación de canales basada en características del segmento
            if seg.firmograficos.tamano == TamanoEmpresa.STARTUP:
                canales_segmento.extend([
                    "Marketing digital y redes sociales",
                    "Partnerships con aceleradoras",
                    "Eventos y conferencias de startups",
                    "Content marketing y SEO"
                ])
            elif seg.firmograficos.tamano in [TamanoEmpresa.MEDIANA, TamanoEmpresa.GRANDE]:
                canales_segmento.extend([
                    "Ventas directas (inside sales)",
                    "Marketing digital B2B",
                    "Webinars y eventos virtuales",
                    "Partnerships estratégicos"
                ])
            else:  # Enterprise
                canales_segmento.extend([
                    "Ventas directas (field sales)",
                    "Partnerships con consultoras",
                    "Eventos enterprise y conferencias",
                    "Referencias y casos de estudio"
                ])
            
            # Ajustar según geografía
            if seg.firmograficos.geografia == Geografia.LATAM:
                canales_segmento.append("Expansión local con partners regionales")
            elif seg.firmograficos.geografia == Geografia.GLOBAL:
                canales_segmento.append("Modelo multi-región con hubs locales")
            
            canales[seg.nombre] = {
                "canales_recomendados": canales_segmento,
                "prioridad": "Alta" if seg.calcular_score_prioridad() >= 7.0 else "Media",
                "presupuesto_estimado_mensual": self._estimar_presupuesto_canal(seg)
            }
        
        return canales
    
    def _estimar_presupuesto_canal(self, segmento: Segmento) -> float:
        """Estima presupuesto mensual para canales de distribución"""
        base = 5000.0  # Base $5K/mes
        
        # Ajustar según tamaño
        if segmento.firmograficos.tamano == TamanoEmpresa.STARTUP:
            multiplicador = 0.5
        elif segmento.firmograficos.tamano == TamanoEmpresa.MEDIANA:
            multiplicador = 1.5
        elif segmento.firmograficos.tamano == TamanoEmpresa.GRANDE:
            multiplicador = 2.5
        else:  # Enterprise
            multiplicador = 4.0
        
        # Ajustar según geografía
        if segmento.firmograficos.geografia == Geografia.GLOBAL:
            multiplicador *= 1.5
        
        return base * multiplicador
    
    def recomendar_pricing_por_segmento(self) -> Dict:
        """Recomienda estrategias de pricing por segmento"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        recomendaciones = {}
        
        for seg in self.segmentos:
            estrategia_pricing = []
            
            # Basado en tamaño
            if seg.firmograficos.tamano == TamanoEmpresa.STARTUP:
                estrategia_pricing.extend([
                    "Modelo freemium o trial extendido",
                    "Pricing escalonado por uso",
                    "Descuentos para early adopters (30-50%)",
                    "Pago mensual flexible"
                ])
            elif seg.firmograficos.tamano == TamanoEmpresa.MEDIANA:
                estrategia_pricing.extend([
                    "Pricing anual con descuento (15-20%)",
                    "Tiers claros (Starter, Professional, Enterprise)",
                    "Opciones de pago trimestral o anual",
                    "Upsell basado en features"
                ])
            else:  # Enterprise
                estrategia_pricing.extend([
                    "Pricing enterprise personalizado",
                    "Contratos multi-año con descuentos",
                    "Modelo basado en usuarios/volumen",
                    "Negociación directa con descuentos por volumen"
                ])
            
            # Basado en urgencia
            if seg.comportamentales.urgencia_problema == UrgenciaProblema.CRITICA:
                estrategia_pricing.append("Premium pricing justificado por valor crítico")
            
            # Basado en aversión al riesgo
            if seg.psicograficos.aversion_riesgo == AversionRiesgo.ALTA:
                estrategia_pricing.append("Garantías y SLAs como parte del pricing")
            
            precio_base = seg.precio_promedio_anual if seg.precio_promedio_anual else 0
            recomendaciones[seg.nombre] = {
                "estrategia_pricing": estrategia_pricing,
                "precio_base_anual_usd": precio_base,
                "rango_recomendado": self._calcular_rango_precio(seg),
                "modelo_recomendado": self._determinar_modelo_precio(seg)
            }
        
        return recomendaciones
    
    def _calcular_rango_precio(self, segmento: Segmento) -> Dict:
        """Calcula rango de precio recomendado"""
        if segmento.precio_promedio_anual:
            base = segmento.precio_promedio_anual
            return {
                "minimo": base * 0.7,
                "promedio": base,
                "maximo": base * 1.5
            }
        return {"minimo": 0, "promedio": 0, "maximo": 0}
    
    def _determinar_modelo_precio(self, segmento: Segmento) -> str:
        """Determina el modelo de pricing más adecuado"""
        if segmento.firmograficos.tamano == TamanoEmpresa.STARTUP:
            return "SaaS mensual con escalamiento"
        elif segmento.firmograficos.tamano in [TamanoEmpresa.MEDIANA, TamanoEmpresa.GRANDE]:
            return "SaaS anual con tiers"
        else:
            return "Enterprise custom pricing"
    
    def analizar_tendencias_mercado(self) -> Dict:
        """Analiza tendencias de mercado por industria y geografía"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        tendencias = {
            "por_industria": defaultdict(list),
            "por_geografia": defaultdict(list),
            "por_tamano": defaultdict(list),
            "insights": []
        }
        
        for seg in self.segmentos:
            # Agrupar por industria
            industria = seg.firmograficos.industria.value
            tendencias["por_industria"][industria].append({
                "segmento": seg.nombre,
                "crecimiento": seg.scoring.crecimiento,
                "oportunidad": seg.scoring.calcular_score_oportunidad()
            })
            
            # Agrupar por geografía
            geografia = seg.firmograficos.geografia.value
            tendencias["por_geografia"][geografia].append({
                "segmento": seg.nombre,
                "crecimiento": seg.scoring.crecimiento,
                "accesibilidad": seg.scoring.accesibilidad
            })
            
            # Agrupar por tamaño
            tamano = seg.firmograficos.tamano.value
            tendencias["por_tamano"][tamano].append({
                "segmento": seg.nombre,
                "score_total": seg.calcular_score_segmento()
            })
        
        # Generar insights
        industria_mayor_crecimiento = max(
            tendencias["por_industria"].items(),
            key=lambda x: sum(s["crecimiento"] for s in x[1]) / len(x[1]) if x[1] else 0
        )
        
        geografia_mas_accesible = max(
            tendencias["por_geografia"].items(),
            key=lambda x: sum(s["accesibilidad"] for s in x[1]) / len(x[1]) if x[1] else 0
        )
        
        tendencias["insights"] = [
            f"Industria con mayor crecimiento promedio: {industria_mayor_crecimiento[0]}",
            f"Geografía más accesible: {geografia_mas_accesible[0]}",
            "Recomendación: Enfoque en segmentos con alta urgencia y buen ajuste de producto",
            "Oportunidad: Segmentos emergentes muestran mayor potencial de crecimiento"
        ]
        
        return tendencias
    
    def calcular_unidad_economica(self, segmento_id: str, cac: Optional[float] = None) -> Dict:
        """Calcula métricas de unidad económica para un segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {"error": "Segmento no encontrado"}
        
        # Estimar CAC si no se proporciona
        if not cac:
            cac = self._estimar_cac(segmento)
        
        # Calcular LTV basado en precio promedio y retención estimada
        precio_anual = segmento.precio_promedio_anual if segmento.precio_promedio_anual else self._estimar_precio(segmento)
        tasa_retencion = self._estimar_tasa_retencion(segmento)
        vida_media_cliente = 1 / (1 - tasa_retencion) if tasa_retencion < 1 else 5
        ltv = precio_anual * vida_media_cliente
        
        # Calcular payback period
        payback_meses = (cac / precio_anual) * 12 if precio_anual > 0 else 0
        
        # Calcular ratio LTV:CAC
        ratio_ltv_cac = ltv / cac if cac > 0 else 0
        
        # Calcular margen de contribución estimado
        costo_servicio = precio_anual * 0.3  # Asumiendo 30% de costo
        margen_contribucion = precio_anual - costo_servicio - cac
        margen_porcentaje = (margen_contribucion / precio_anual) * 100 if precio_anual > 0 else 0
        
        return {
            "segmento": segmento.nombre,
            "cac": cac,
            "ltv": ltv,
            "ratio_ltv_cac": ratio_ltv_cac,
            "payback_meses": payback_meses,
            "vida_media_cliente_anos": vida_media_cliente,
            "margen_contribucion": margen_contribucion,
            "margen_porcentaje": margen_porcentaje,
            "evaluacion": self._evaluar_unidad_economica(ratio_ltv_cac, payback_meses, margen_porcentaje)
        }
    
    def _estimar_cac(self, segmento: Segmento) -> float:
        """Estima CAC basado en características del segmento"""
        base = 1000.0
        
        # Ajustar según tamaño
        if segmento.firmograficos.tamano == TamanoEmpresa.STARTUP:
            multiplicador = 0.5
        elif segmento.firmograficos.tamano == TamanoEmpresa.MEDIANA:
            multiplicador = 2.0
        elif segmento.firmograficos.tamano == TamanoEmpresa.GRANDE:
            multiplicador = 5.0
        else:  # Enterprise
            multiplicador = 15.0
        
        # Ajustar según competencia
        multiplicador *= (10 - segmento.scoring.competencia) / 10
        
        # Ajustar según accesibilidad
        multiplicador *= (10 - segmento.scoring.accesibilidad) / 10
        
        return base * multiplicador
    
    def _estimar_precio(self, segmento: Segmento) -> float:
        """Estima precio si no está definido"""
        if segmento.precio_promedio_anual:
            return segmento.precio_promedio_anual
        
        if segmento.firmograficos.tamano == TamanoEmpresa.STARTUP:
            return 5000.0
        elif segmento.firmograficos.tamano == TamanoEmpresa.MEDIANA:
            return 25000.0
        elif segmento.firmograficos.tamano == TamanoEmpresa.GRANDE:
            return 75000.0
        else:
            return 200000.0
    
    def _estimar_tasa_retencion(self, segmento: Segmento) -> float:
        """Estima tasa de retención anual"""
        base = 0.80  # 80% base
        
        # Ajustar según urgencia (mayor urgencia = mayor retención)
        if segmento.comportamentales.urgencia_problema == UrgenciaProblema.CRITICA:
            base += 0.10
        elif segmento.comportamentales.urgencia_problema == UrgenciaProblema.ALTA:
            base += 0.05
        
        # Ajustar según tamaño (empresas grandes = mayor retención)
        if segmento.firmograficos.tamano == TamanoEmpresa.ENTERPRISE:
            base += 0.05
        
        return min(base, 0.95)  # Máximo 95%
    
    def _evaluar_unidad_economica(self, ratio_ltv_cac: float, payback_meses: float, margen: float) -> Dict:
        """Evalúa la salud de la unidad económica"""
        salud = "Excelente"
        recomendaciones = []
        
        if ratio_ltv_cac < 3:
            salud = "Crítica"
            recomendaciones.append("Ratio LTV:CAC muy bajo. Necesario reducir CAC o aumentar LTV")
        elif ratio_ltv_cac < 5:
            salud = "Mejorable"
            recomendaciones.append("Ratio LTV:CAC bajo. Considerar optimización")
        
        if payback_meses > 12:
            salud = "Crítica" if salud == "Crítica" else "Mejorable"
            recomendaciones.append(f"Payback period muy largo ({payback_meses:.1f} meses). Reducir CAC o aumentar precio")
        
        if margen < 20:
            salud = "Mejorable" if salud == "Excelente" else salud
            recomendaciones.append(f"Margen bajo ({margen:.1f}%). Optimizar costos o aumentar precio")
        
        if salud == "Excelente":
            recomendaciones.append("Unidad económica saludable. Escalar con confianza")
        
        return {
            "salud": salud,
            "recomendaciones": recomendaciones
        }
    
    def simulador_escenarios(self, segmento_id: str, variaciones: Dict) -> Dict:
        """Simula diferentes escenarios para un segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {"error": "Segmento no encontrado"}
        
        escenarios = {}
        
        # Escenario base
        escenarios["base"] = {
            "cac": self._estimar_cac(segmento),
            "precio": segmento.precio_promedio_anual or self._estimar_precio(segmento),
            "tasa_conversion": segmento.tasa_conversion_esperada or 10.0,
            "tasa_retencion": self._estimar_tasa_retencion(segmento)
        }
        
        # Escenario optimista
        escenarios["optimista"] = {
            "cac": escenarios["base"]["cac"] * 0.7,  # 30% reducción CAC
            "precio": escenarios["base"]["precio"] * 1.2,  # 20% aumento precio
            "tasa_conversion": escenarios["base"]["tasa_conversion"] * 1.3,  # 30% más conversión
            "tasa_retencion": min(escenarios["base"]["tasa_retencion"] + 0.1, 0.95)
        }
        
        # Escenario pesimista
        escenarios["pesimista"] = {
            "cac": escenarios["base"]["cac"] * 1.5,  # 50% aumento CAC
            "precio": escenarios["base"]["precio"] * 0.9,  # 10% reducción precio
            "tasa_conversion": escenarios["base"]["tasa_conversion"] * 0.7,  # 30% menos conversión
            "tasa_retencion": max(escenarios["base"]["tasa_retencion"] - 0.1, 0.6)
        }
        
        # Aplicar variaciones personalizadas si se proporcionan
        if variaciones:
            escenarios["personalizado"] = {**escenarios["base"]}
            escenarios["personalizado"].update(variaciones)
        
        # Calcular métricas para cada escenario
        resultados = {}
        for nombre, params in escenarios.items():
            ltv = params["precio"] * (1 / (1 - params["tasa_retencion"]))
            ratio = ltv / params["cac"] if params["cac"] > 0 else 0
            payback = (params["cac"] / params["precio"]) * 12 if params["precio"] > 0 else 0
            
            resultados[nombre] = {
                **params,
                "ltv": ltv,
                "ratio_ltv_cac": ratio,
                "payback_meses": payback,
                "evaluacion": self._evaluar_unidad_economica(ratio, payback, 40.0)
            }
        
        return {
            "segmento": segmento.nombre,
            "escenarios": resultados,
            "recomendacion": self._recomendar_escenario(resultados)
        }
    
    def _recomendar_escenario(self, resultados: Dict) -> str:
        """Recomienda el mejor escenario"""
        mejor_ratio = max(resultados.items(), key=lambda x: x[1]["ratio_ltv_cac"])
        return f"Escenario '{mejor_ratio[0]}' muestra mejor ratio LTV:CAC ({mejor_ratio[1]['ratio_ltv_cac']:.2f})"
    
    def analisis_predictivo_crecimiento(self, anos_proyeccion: int = 3) -> Dict:
        """Análisis predictivo de crecimiento por segmento"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        proyecciones = {}
        
        for seg in self.segmentos:
            if not seg.metricas_mercado:
                continue
            
            tam_actual = seg.metricas_mercado.sam
            crecimiento_anual = seg.metricas_mercado.tasa_crecimiento_anual / 100
            
            # Proyección de mercado
            mercado_proyectado = []
            mercado_actual = tam_actual
            for ano in range(1, anos_proyeccion + 1):
                mercado_actual *= (1 + crecimiento_anual)
                mercado_proyectado.append({
                    "ano": ano,
                    "tam_proyectado": mercado_actual,
                    "crecimiento_anual": crecimiento_anual * 100
                })
            
            # Proyección de ingresos (asumiendo penetración creciente)
            penetracion_actual = seg.metricas_mercado.penetracion_actual / 100
            ingresos_proyectados = []
            penetracion = penetracion_actual
            
            for ano in range(1, anos_proyeccion + 1):
                penetracion = min(penetracion * 1.2, 0.3)  # Crecimiento de penetración hasta 30%
                mercado_ano = tam_actual * ((1 + crecimiento_anual) ** ano)
                ingresos_ano = mercado_ano * penetracion
                crecimiento_vs_anterior = 0
                if ingresos_proyectados:
                    crecimiento_vs_anterior = ((ingresos_ano / ingresos_proyectados[-1]["ingresos_proyectados"] - 1) * 100)
                ingresos_proyectados.append({
                    "ano": ano,
                    "ingresos_proyectados": ingresos_ano,
                    "penetracion": penetracion * 100,
                    "crecimiento_vs_anterior": crecimiento_vs_anterior
                })
            
            proyecciones[seg.nombre] = {
                "mercado": mercado_proyectado,
                "ingresos": ingresos_proyectados,
                "tam_actual": tam_actual,
                "crecimiento_anual": crecimiento_anual * 100,
                "valor_presente_3anos": sum(p["ingresos_proyectados"] for p in ingresos_proyectados)
            }
        
        return proyecciones
    
    def analisis_sensibilidad(self, segmento_id: str, variables: List[str]) -> Dict:
        """Análisis de sensibilidad para variables clave"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {"error": "Segmento no encontrado"}
        
        sensibilidad = {
            "segmento": segmento.nombre,
            "variables": {}
        }
        
        for variable in variables:
            if variable == "cac":
                valores = [self._estimar_cac(segmento) * f for f in [0.5, 0.75, 1.0, 1.25, 1.5]]
                impacto = []
                precio = segmento.precio_promedio_anual or self._estimar_precio(segmento)
                retencion = self._estimar_tasa_retencion(segmento)
                
                for cac_val in valores:
                    ltv = precio * (1 / (1 - retencion))
                    ratio = ltv / cac_val if cac_val > 0 else 0
                    impacto.append({
                        "valor": cac_val,
                        "ratio_ltv_cac": ratio,
                        "impacto": "Alto" if ratio < 3 else "Bajo"
                    })
                
                sensibilidad["variables"]["cac"] = impacto
            
            elif variable == "precio":
                precio_base = segmento.precio_promedio_anual or self._estimar_precio(segmento)
                valores = [precio_base * f for f in [0.7, 0.85, 1.0, 1.15, 1.3]]
                impacto = []
                cac = self._estimar_cac(segmento)
                retencion = self._estimar_tasa_retencion(segmento)
                
                for precio_val in valores:
                    ltv = precio_val * (1 / (1 - retencion))
                    ratio = ltv / cac if cac > 0 else 0
                    impacto.append({
                        "valor": precio_val,
                        "ratio_ltv_cac": ratio,
                        "impacto": "Alto" if ratio > 5 else "Bajo"
                    })
                
                sensibilidad["variables"]["precio"] = impacto
            
            elif variable == "retencion":
                retencion_base = self._estimar_tasa_retencion(segmento)
                valores = [max(0.6, min(0.95, retencion_base + delta)) for delta in [-0.1, -0.05, 0, 0.05, 0.1]]
                impacto = []
                precio = segmento.precio_promedio_anual or self._estimar_precio(segmento)
                cac = self._estimar_cac(segmento)
                
                for ret_val in valores:
                    ltv = precio * (1 / (1 - ret_val))
                    ratio = ltv / cac if cac > 0 else 0
                    impacto.append({
                        "valor": ret_val,
                        "ratio_ltv_cac": ratio,
                        "impacto": "Alto" if ratio > 5 else "Bajo"
                    })
                
                sensibilidad["variables"]["retencion"] = impacto
        
        return sensibilidad
    
    def generar_dashboard_ejecutivo(self) -> Dict:
        """Genera dashboard ejecutivo con métricas clave"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        dashboard = {
            "resumen_ejecutivo": {
                "total_segmentos": len(self.segmentos),
                "segmento_primario": self.segmento_primario.nombre if self.segmento_primario else None,
                "segmento_secundario": self.segmento_secundario.nombre if self.segmento_secundario else None,
                "fecha_analisis": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "metricas_agregadas": {},
            "top_segmentos": [],
            "alertas": []
        }
        
        # Calcular métricas agregadas
        scores_totales = [s.calcular_score_segmento() for s in self.segmentos]
        dashboard["metricas_agregadas"] = {
            "score_promedio": sum(scores_totales) / len(scores_totales) if scores_totales else 0,
            "score_maximo": max(scores_totales) if scores_totales else 0,
            "score_minimo": min(scores_totales) if scores_totales else 0,
            "segmentos_alta_prioridad": len([s for s in self.segmentos if s.calcular_score_prioridad() >= 7.0])
        }
        
        # Top 3 segmentos
        top_segmentos = sorted(self.segmentos, key=lambda s: s.calcular_score_segmento(), reverse=True)[:3]
        dashboard["top_segmentos"] = [
            {
                "nombre": s.nombre,
                "score": s.calcular_score_segmento(),
                "oportunidad": s.scoring.calcular_score_oportunidad(),
                "riesgo": s.scoring.calcular_score_riesgo()
            }
            for s in top_segmentos
        ]
        
        # Alertas
        for seg in self.segmentos:
            if seg.scoring.calcular_score_riesgo() > 0.5:
                dashboard["alertas"].append({
                    "tipo": "Alto Riesgo",
                    "segmento": seg.nombre,
                    "mensaje": f"Segmento con alto riesgo ({seg.scoring.calcular_score_riesgo():.2f}). Requiere estrategia especial."
                })
            
            if seg.scoring.calcular_score_oportunidad() < 0.6:
                dashboard["alertas"].append({
                    "tipo": "Baja Oportunidad",
                    "segmento": seg.nombre,
                    "mensaje": f"Segmento con baja oportunidad ({seg.scoring.calcular_score_oportunidad():.2f}). Considerar baja prioridad."
                })
        
        return dashboard
    
    def analisis_competidores_detallado(self, segmento_id: str) -> Dict:
        """Análisis detallado de competidores para un segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {"error": "Segmento no encontrado"}
        
        if not segmento.analisis_competencia:
            return {"error": "Análisis de competencia no disponible para este segmento"}
        
        analisis = segmento.analisis_competencia
        
        # Clasificar posición competitiva
        score_competitivo = analisis.calcular_score_competitivo()
        if score_competitivo >= 0.7:
            posicion = "Líder"
            estrategia = "Mantener posición dominante, innovar continuamente"
        elif score_competitivo >= 0.5:
            posicion = "Competidor Fuerte"
            estrategia = "Diferenciación agresiva, mejorar barreras de entrada"
        elif score_competitivo >= 0.3:
            posicion = "Seguidor"
            estrategia = "Encontrar nichos, mejorar diferenciación"
        else:
            posicion = "Débil"
            estrategia = "Reconsiderar entrada o encontrar ventaja competitiva única"
        
        # Análisis de Porter's 5 Forces
        porter_forces = {
            "intensidad_competitiva": {
                "valor": analisis.intensidad_competitiva,
                "evaluacion": "Alta" if analisis.intensidad_competitiva >= 7 else "Media" if analisis.intensidad_competitiva >= 4 else "Baja",
                "impacto": "Negativo" if analisis.intensidad_competitiva >= 7 else "Neutral"
            },
            "poder_negociacion_clientes": {
                "valor": analisis.poder_negociacion_clientes,
                "evaluacion": "Alto" if analisis.poder_negociacion_clientes >= 7 else "Medio" if analisis.poder_negociacion_clientes >= 4 else "Bajo",
                "impacto": "Negativo" if analisis.poder_negociacion_clientes >= 7 else "Neutral"
            },
            "poder_negociacion_proveedores": {
                "valor": analisis.poder_negociacion_proveedores,
                "evaluacion": "Alto" if analisis.poder_negociacion_proveedores >= 7 else "Medio" if analisis.poder_negociacion_proveedores >= 4 else "Bajo",
                "impacto": "Negativo" if analisis.poder_negociacion_proveedores >= 7 else "Neutral"
            },
            "amenaza_sustitutos": {
                "valor": 5.0,  # Valor estimado
                "evaluacion": "Media",
                "impacto": "Neutral"
            },
            "barreras_entrada": {
                "valor": analisis.barreras_entrada,
                "evaluacion": "Altas" if analisis.barreras_entrada >= 7 else "Medias" if analisis.barreras_entrada >= 4 else "Bajas",
                "impacto": "Positivo" if analisis.barreras_entrada >= 7 else "Neutral"
            }
        }
        
        return {
            "segmento": segmento.nombre,
            "posicion_competitiva": posicion,
            "score_competitivo": score_competitivo,
            "numero_competidores": analisis.numero_competidores,
            "diferenciacion_posible": analisis.diferenciacion_posible,
            "estrategia_recomendada": estrategia,
            "porter_5_forces": porter_forces,
            "ventajas_competitivas": self._identificar_ventajas_competitivas(segmento),
            "amenazas": self._identificar_amenazas(segmento, analisis)
        }
    
    def _identificar_ventajas_competitivas(self, segmento: Segmento) -> List[str]:
        """Identifica ventajas competitivas potenciales"""
        ventajas = []
        
        if segmento.scoring.ajuste_producto >= 9.0:
            ventajas.append("Excelente ajuste producto-mercado")
        if segmento.scoring.accesibilidad >= 8.0:
            ventajas.append("Alta accesibilidad al mercado")
        if segmento.comportamentales.urgencia_problema == UrgenciaProblema.CRITICA:
            ventajas.append("Problema crítico del cliente (alta necesidad)")
        if segmento.psicograficos.apetito_innovacion == ApetitoInnovacion.DISRUPTIVO:
            ventajas.append("Cliente abierto a innovación disruptiva")
        if segmento.firmograficos.madurez_digital == MadurezDigital.AVANZADO:
            ventajas.append("Cliente con infraestructura digital lista")
        
        return ventajas
    
    def _identificar_amenazas(self, segmento: Segmento, analisis: AnalisisCompetencia) -> List[str]:
        """Identifica amenazas competitivas"""
        amenazas = []
        
        if analisis.intensidad_competitiva >= 7:
            amenazas.append("Alta intensidad competitiva")
        if analisis.numero_competidores > 10:
            amenazas.append("Mercado muy saturado")
        if analisis.barreras_entrada < 5:
            amenazas.append("Bajas barreras de entrada (fácil para nuevos competidores)")
        if segmento.scoring.competencia < 5:
            amenazas.append("Alta competencia existente")
        if analisis.poder_negociacion_clientes >= 7:
            amenazas.append("Alto poder de negociación de clientes")
        
        return amenazas
    
    def matriz_bcg_adaptada(self) -> Dict:
        """Matriz BCG adaptada para segmentos (Crecimiento vs Cuota de Mercado)"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        matriz_bcg = {
            "estrellas": [],  # Alto crecimiento, alta cuota
            "vacas_lecheras": [],  # Bajo crecimiento, alta cuota
            "interrogantes": [],  # Alto crecimiento, baja cuota
            "perros": []  # Bajo crecimiento, baja cuota
        }
        
        # Calcular cuota de mercado relativa estimada
        scores_totales = [s.calcular_score_segmento() for s in self.segmentos]
        score_maximo = max(scores_totales) if scores_totales else 1
        
        for seg in self.segmentos:
            crecimiento = seg.scoring.crecimiento
            cuota_relativa = seg.calcular_score_segmento() / score_maximo if score_maximo > 0 else 0.5
            
            # Umbrales adaptados
            alto_crecimiento = crecimiento >= 7.5
            alta_cuota = cuota_relativa >= 0.7
            
            segmento_info = {
                "nombre": seg.nombre,
                "crecimiento": crecimiento,
                "cuota_relativa": cuota_relativa,
                "score_total": seg.calcular_score_segmento()
            }
            
            if alto_crecimiento and alta_cuota:
                matriz_bcg["estrellas"].append(segmento_info)
            elif not alto_crecimiento and alta_cuota:
                matriz_bcg["vacas_lecheras"].append(segmento_info)
            elif alto_crecimiento and not alta_cuota:
                matriz_bcg["interrogantes"].append(segmento_info)
            else:
                matriz_bcg["perros"].append(segmento_info)
        
        return matriz_bcg
    
    def estrategia_go_to_market_detallada(self, segmento_id: str) -> Dict:
        """Estrategia Go-to-Market detallada para un segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {"error": "Segmento no encontrado"}
        
        estrategia = {
            "segmento": segmento.nombre,
            "fase": self._determinar_fase_mercado(segmento),
            "objetivos": self._definir_objetivos_gtm(segmento),
            "posicionamiento": self._definir_posicionamiento(segmento),
            "mensaje_clave": self._crear_mensaje_clave(segmento),
            "canales": self._definir_canales_gtm(segmento),
            "actividades_marketing": self._definir_actividades_marketing(segmento),
            "actividades_ventas": self._definir_actividades_ventas(segmento),
            "metricas_success": self._definir_metricas_success(segmento),
            "timeline": self._crear_timeline_gtm(segmento)
        }
        
        return estrategia
    
    def _determinar_fase_mercado(self, segmento: Segmento) -> str:
        """Determina la fase del mercado"""
        if segmento.comportamentales.adopcion_tecnologica == AdopcionTecnologica.INNOVADOR:
            return "Early Market"
        elif segmento.comportamentales.adopcion_tecnologica == AdopcionTecnologica.ADOPTADOR_TEMPRANO:
            return "Early Majority"
        elif segmento.comportamentales.adopcion_tecnologica == AdopcionTecnologica.MAYORIA_TEMPRANA:
            return "Majority"
        else:
            return "Late Majority"
    
    def _definir_objetivos_gtm(self, segmento: Segmento) -> List[str]:
        """Define objetivos Go-to-Market"""
        objetivos = []
        
        if segmento.firmograficos.tamano == TamanoEmpresa.STARTUP:
            objetivos.extend([
                "Adquirir primeros 10 clientes en 6 meses",
                "Validar product-market fit",
                "Generar casos de estudio iniciales"
            ])
        elif segmento.firmograficos.tamano == TamanoEmpresa.MEDIANA:
            objetivos.extend([
                f"Alcanzar ${segmento.precio_promedio_anual * 20:,.0f} ARR en 12 meses",
                "Establecer presencia en mercado objetivo",
                "Desarrollar pipeline de ventas sostenible"
            ])
        else:
            objetivos.extend([
                f"Alcanzar ${segmento.precio_promedio_anual * 5:,.0f} ARR en 12 meses",
                "Establecer relaciones estratégicas",
                "Desarrollar programa de referencias"
            ])
        
        return objetivos
    
    def _definir_posicionamiento(self, segmento: Segmento) -> str:
        """Define posicionamiento para el segmento"""
        if segmento.comportamentales.urgencia_problema == UrgenciaProblema.CRITICA:
            return f"Solución crítica para {segmento.firmograficos.industria.value} que resuelve [problema crítico]"
        elif segmento.scoring.ajuste_producto >= 9.0:
            return f"La mejor solución para {segmento.firmograficos.industria.value} que necesita [valor clave]"
        else:
            return f"Solución innovadora para {segmento.firmograficos.industria.value}"
    
    def _crear_mensaje_clave(self, segmento: Segmento) -> str:
        """Crea mensaje clave para el segmento"""
        industria = segmento.firmograficos.industria.value
        problema = "problemas críticos" if segmento.comportamentales.urgencia_problema == UrgenciaProblema.CRITICA else "desafíos clave"
        return f"Para {industria} que enfrenta {problema}, ofrecemos [solución] que [beneficio clave]"
    
    def _definir_canales_gtm(self, segmento: Segmento) -> Dict:
        """Define canales Go-to-Market"""
        canales = self.analizar_canales_distribucion()
        return canales.get(segmento.nombre, {})
    
    def _definir_actividades_marketing(self, segmento: Segmento) -> List[str]:
        """Define actividades de marketing"""
        actividades = []
        
        if segmento.firmograficos.tamano == TamanoEmpresa.STARTUP:
            actividades.extend([
                "Content marketing en LinkedIn y Twitter",
                "Webinars educativos mensuales",
                "Programa de early adopters",
                "Case studies rápidos"
            ])
        elif segmento.firmograficos.tamano == TamanoEmpresa.MEDIANA:
            actividades.extend([
                "Email marketing segmentado",
                "SEO y contenido técnico",
                "Eventos y conferencias de industria",
                "Programa de referencias"
            ])
        else:
            actividades.extend([
                "Thought leadership y white papers",
                "Eventos enterprise y cenas ejecutivas",
                "Programa de partners estratégicos",
                "Case studies profundos y ROI"
            ])
        
        return actividades
    
    def _definir_actividades_ventas(self, segmento: Segmento) -> List[str]:
        """Define actividades de ventas"""
        actividades = []
        
        if segmento.ciclo_venta_dias and segmento.ciclo_venta_dias < 60:
            actividades.extend([
                "Inside sales con enfoque en velocidad",
                "Demos rápidas y trials",
                "Onboarding acelerado"
            ])
        elif segmento.ciclo_venta_dias and segmento.ciclo_venta_dias >= 120:
            actividades.extend([
                "Field sales con enfoque consultivo",
                "Pilotos y pruebas de concepto",
                "Múltiples stakeholders y aprobaciones"
            ])
        else:
            actividades.extend([
                "Sales híbrido (inside + field)",
                "Demos personalizadas",
                "Proceso estructurado de ventas"
            ])
        
        return actividades
    
    def _definir_metricas_success(self, segmento: Segmento) -> Dict:
        """Define métricas de éxito"""
        unidad_economica = self.calcular_unidad_economica(segmento.id)
        
        return {
            "cac_objetivo": unidad_economica.get("cac", 0),
            "ltv_objetivo": unidad_economica.get("ltv", 0),
            "ratio_ltv_cac_objetivo": unidad_economica.get("ratio_ltv_cac", 0),
            "tasa_conversion_objetivo": segmento.tasa_conversion_esperada or 10.0,
            "ciclo_venta_objetivo_dias": segmento.ciclo_venta_dias or 90,
            "mrr_objetivo_6meses": (segmento.precio_promedio_anual or 25000) / 12 * 10,
            "mrr_objetivo_12meses": (segmento.precio_promedio_anual or 25000) / 12 * 50
        }
    
    def _crear_timeline_gtm(self, segmento: Segmento) -> Dict:
        """Crea timeline Go-to-Market"""
        return {
            "mes_1_3": {
                "fase": "Preparación",
                "actividades": [
                    "Desarrollar materiales de marketing",
                    "Entrenar equipo de ventas",
                    "Identificar primeros prospectos"
                ]
            },
            "mes_4_6": {
                "fase": "Lanzamiento",
                "actividades": [
                    "Campaña de lanzamiento",
                    "Primeros cierres",
                    "Generar momentum"
                ]
            },
            "mes_7_12": {
                "fase": "Escalamiento",
                "actividades": [
                    "Optimizar procesos",
                    "Escalar canales exitosos",
                    "Desarrollar referencias"
                ]
            }
        }
    
    def analisis_sinergias_segmentos(self) -> Dict:
        """Analiza sinergias entre segmentos"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        sinergias = []
        
        for i, seg1 in enumerate(self.segmentos):
            for seg2 in self.segmentos[i+1:]:
                sinergia_score = self._calcular_sinergia(seg1, seg2)
                if sinergia_score > 0.5:
                    sinergias.append({
                        "segmento_1": seg1.nombre,
                        "segmento_2": seg2.nombre,
                        "score_sinergia": sinergia_score,
                        "tipo_sinergia": self._identificar_tipo_sinergia(seg1, seg2),
                        "oportunidades": self._identificar_oportunidades_sinergia(seg1, seg2)
                    })
        
        return {
            "total_sinergias": len(sinergias),
            "sinergias": sorted(sinergias, key=lambda x: x["score_sinergia"], reverse=True)
        }
    
    def _calcular_sinergia(self, seg1: Segmento, seg2: Segmento) -> float:
        """Calcula score de sinergia entre dos segmentos"""
        score = 0.0
        
        # Misma industria = sinergia alta
        if seg1.firmograficos.industria == seg2.firmograficos.industria:
            score += 0.3
        
        # Misma geografía = sinergia media
        if seg1.firmograficos.geografia == seg2.firmograficos.geografia:
            score += 0.2
        
        # Tamaños complementarios = sinergia
        if (seg1.firmograficos.tamano == TamanoEmpresa.STARTUP and seg2.firmograficos.tamano == TamanoEmpresa.MEDIANA) or \
           (seg1.firmograficos.tamano == TamanoEmpresa.MEDIANA and seg2.firmograficos.tamano == TamanoEmpresa.GRANDE):
            score += 0.2
        
        # Misma urgencia = sinergia
        if seg1.comportamentales.urgencia_problema == seg2.comportamentales.urgencia_problema:
            score += 0.15
        
        # Ajuste producto similar = sinergia
        if abs(seg1.scoring.ajuste_producto - seg2.scoring.ajuste_producto) < 1.0:
            score += 0.15
        
        return min(score, 1.0)
    
    def _identificar_tipo_sinergia(self, seg1: Segmento, seg2: Segmento) -> str:
        """Identifica el tipo de sinergia"""
        if seg1.firmograficos.industria == seg2.firmograficos.industria:
            return "Vertical (misma industria)"
        elif seg1.firmograficos.geografia == seg2.firmograficos.geografia:
            return "Geográfica (misma región)"
        elif seg1.firmograficos.tamano != seg2.firmograficos.tamano:
            return "Escalado (diferentes tamaños)"
        else:
            return "Complementaria"
    
    def _identificar_oportunidades_sinergia(self, seg1: Segmento, seg2: Segmento) -> List[str]:
        """Identifica oportunidades de sinergia"""
        oportunidades = []
        
        if seg1.firmograficos.industria == seg2.firmograficos.industria:
            oportunidades.append("Compartir casos de estudio entre segmentos")
            oportunidades.append("Referencias cruzadas dentro de la industria")
        
        if seg1.firmograficos.geografia == seg2.firmograficos.geografia:
            oportunidades.append("Compartir recursos de marketing local")
            oportunidades.append("Eventos conjuntos en la región")
        
        if seg1.firmograficos.tamano != seg2.firmograficos.tamano:
            oportunidades.append("Upsell de segmento pequeño a grande")
            oportunidades.append("Programa de crecimiento con clientes")
        
        return oportunidades
    
    def generar_plan_accion_ejecutable(self) -> Dict:
        """Genera plan de acción ejecutable basado en análisis"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        plan = {
            "resumen": {
                "segmento_primario": self.segmento_primario.nombre if self.segmento_primario else None,
                "segmento_secundario": self.segmento_secundario.nombre if self.segmento_secundario else None,
                "prioridad_total": len([s for s in self.segmentos if s.calcular_score_prioridad() >= 7.0])
            },
            "acciones_inmediatas": [],
            "acciones_3_meses": [],
            "acciones_6_meses": [],
            "acciones_12_meses": [],
            "recursos_necesarios": {},
            "riesgos_y_mitigacion": []
        }
        
        # Acciones inmediatas (primer mes)
        if self.segmento_primario:
            plan["acciones_inmediatas"].extend([
                f"Validar product-market fit con {self.segmento_primario.nombre}",
                f"Identificar primeros 10 prospectos en {self.segmento_primario.nombre}",
                f"Desarrollar materiales de marketing para {self.segmento_primario.nombre}",
                f"Configurar tracking de métricas clave para {self.segmento_primario.nombre}"
            ])
        
        # Acciones 3 meses
        plan["acciones_3_meses"].extend([
            "Lanzar campaña de marketing inicial",
            "Cerrar primeros 5 clientes",
            "Generar primeros casos de estudio",
            "Optimizar proceso de ventas basado en feedback"
        ])
        
        # Acciones 6 meses
        plan["acciones_6_meses"].extend([
            "Escalar canales exitosos",
            "Desarrollar programa de referencias",
            "Expandir a segmento secundario",
            "Optimizar unidad económica"
        ])
        
        # Acciones 12 meses
        plan["acciones_12_meses"].extend([
            "Alcanzar objetivos de ingresos",
            "Establecer posición de mercado",
            "Desarrollar ventajas competitivas sostenibles",
            "Evaluar expansión a nuevos segmentos"
        ])
        
        # Recursos necesarios
        if self.segmento_primario:
            unidad = self.calcular_unidad_economica(self.segmento_primario.id)
            plan["recursos_necesarios"] = {
                "presupuesto_marketing_mensual": self._estimar_presupuesto_canal(self.segmento_primario),
                "equipo_ventas": "2-3 personas" if self.segmento_primario.firmograficos.tamano == TamanoEmpresa.STARTUP else "5-7 personas",
                "presupuesto_cac": unidad.get("cac", 0) * 20,  # Para 20 clientes
                "tiempo_estimado_roi": f"{unidad.get('payback_meses', 6):.0f} meses"
            }
        
        # Riesgos y mitigación
        plan["riesgos_y_mitigacion"] = [
            {
                "riesgo": "Alto CAC",
                "mitigacion": "Optimizar canales de adquisición, mejorar tasa de conversión"
            },
            {
                "riesgo": "Baja tasa de conversión",
                "mitigacion": "Mejorar mensaje, ajustar pricing, optimizar proceso de ventas"
            },
            {
                "riesgo": "Competencia intensa",
                "mitigacion": "Diferenciación clara, enfoque en nicho, mejorar producto"
            }
        ]
        
        return plan
    
    def analisis_barreras_entrada_salida(self, segmento_id: str) -> Dict:
        """Analiza barreras de entrada y salida para un segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {"error": "Segmento no encontrado"}
        
        barreras = {
            "segmento": segmento.nombre,
            "barreras_entrada": [],
            "barreras_salida": [],
            "evaluacion_general": {}
        }
        
        # Barreras de entrada
        if segmento.analisis_competencia:
            barreras_entrada_score = segmento.analisis_competencia.barreras_entrada
            
            if barreras_entrada_score >= 7:
                barreras["barreras_entrada"].extend([
                    "Altas barreras de entrada - Mercado protegido",
                    "Requiere inversión significativa para entrar",
                    "Ventaja para primeros movers"
                ])
            elif barreras_entrada_score >= 4:
                barreras["barreras_entrada"].extend([
                    "Barreras moderadas - Competencia posible",
                    "Requiere diferenciación clara",
                    "Oportunidad con producto superior"
                ])
            else:
                barreras["barreras_entrada"].extend([
                    "Bajas barreras - Mercado abierto",
                    "Fácil entrada para nuevos competidores",
                    "Necesario construir ventajas competitivas rápidamente"
                ])
        
        # Barreras específicas por características
        if segmento.firmograficos.industria in [Industria.FINANZAS, Industria.SALUD]:
            barreras["barreras_entrada"].append("Requisitos regulatorios y compliance")
        
        if segmento.firmograficos.tamano == TamanoEmpresa.ENTERPRISE:
            barreras["barreras_entrada"].append("Relaciones establecidas con grandes vendors")
        
        if segmento.scoring.competencia < 5:
            barreras["barreras_entrada"].append("Alta competencia existente")
        
        # Barreras de salida (switching costs)
        tasa_retencion = self._estimar_tasa_retencion(segmento)
        if tasa_retencion >= 0.85:
            barreras["barreras_salida"].extend([
                "Altos costos de cambio para clientes",
                "Integración profunda con sistemas del cliente",
                "Alta retención esperada"
            ])
        elif tasa_retencion >= 0.75:
            barreras["barreras_salida"].extend([
                "Costos moderados de cambio",
                "Necesario mantener valor continuo",
                "Retención media-alta"
            ])
        else:
            barreras["barreras_salida"].extend([
                "Bajos costos de cambio",
                "Riesgo de churn alto",
                "Necesario mejorar retención"
            ])
        
        # Evaluación general
        barreras["evaluacion_general"] = {
            "facilidad_entrada": "Difícil" if segmento.analisis_competencia and segmento.analisis_competencia.barreras_entrada >= 7 else "Moderada" if segmento.analisis_competencia and segmento.analisis_competencia.barreras_entrada >= 4 else "Fácil",
            "facilidad_salida": "Difícil" if tasa_retencion >= 0.85 else "Moderada" if tasa_retencion >= 0.75 else "Fácil",
            "recomendacion": self._recomendacion_barreras(segmento, tasa_retencion)
        }
        
        return barreras
    
    def _recomendacion_barreras(self, segmento: Segmento, tasa_retencion: float) -> str:
        """Genera recomendación basada en barreras"""
        if segmento.analisis_competencia and segmento.analisis_competencia.barreras_entrada >= 7:
            return "Mercado con barreras altas - Construir ventajas competitivas antes de entrar"
        elif tasa_retencion >= 0.85:
            return "Buenas barreras de salida - Enfoque en retención y valor a largo plazo"
        else:
            return "Barreras bajas - Necesario diferenciación fuerte y construcción rápida de ventajas"
    
    def analisis_cohortes_segmentos(self) -> Dict:
        """Análisis de cohortes por características de segmentos"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        cohortes = {
            "por_industria": defaultdict(list),
            "por_geografia": defaultdict(list),
            "por_tamano": defaultdict(list),
            "por_urgencia": defaultdict(list),
            "metricas_cohortes": {}
        }
        
        for seg in self.segmentos:
            # Agrupar por industria
            industria = seg.firmograficos.industria.value
            cohortes["por_industria"][industria].append({
                "nombre": seg.nombre,
                "score": seg.calcular_score_segmento(),
                "oportunidad": seg.scoring.calcular_score_oportunidad(),
                "riesgo": seg.scoring.calcular_score_riesgo()
            })
            
            # Agrupar por geografía
            geografia = seg.firmograficos.geografia.value
            cohortes["por_geografia"][geografia].append({
                "nombre": seg.nombre,
                "score": seg.calcular_score_segmento(),
                "crecimiento": seg.scoring.crecimiento
            })
            
            # Agrupar por tamaño
            tamano = seg.firmograficos.tamano.value
            cohortes["por_tamano"][tamano].append({
                "nombre": seg.nombre,
                "score": seg.calcular_score_segmento(),
                "precio": seg.precio_promedio_anual or 0
            })
            
            # Agrupar por urgencia
            urgencia = seg.comportamentales.urgencia_problema.value
            cohortes["por_urgencia"][urgencia].append({
                "nombre": seg.nombre,
                "score": seg.calcular_score_segmento(),
                "ajuste_producto": seg.scoring.ajuste_producto
            })
        
        # Calcular métricas por cohorte
        for categoria, grupos in cohortes.items():
            if categoria == "metricas_cohortes":
                continue
            
            metricas = {}
            for grupo, segmentos_lista in grupos.items():
                if segmentos_lista:
                    scores = [s["score"] for s in segmentos_lista]
                    metricas[grupo] = {
                        "cantidad": len(segmentos_lista),
                        "score_promedio": sum(scores) / len(scores),
                        "score_maximo": max(scores),
                        "score_minimo": min(scores)
                    }
            
            cohortes["metricas_cohortes"][categoria] = metricas
        
        return cohortes
    
    def recomendar_partnerships(self) -> Dict:
        """Recomienda partnerships estratégicos por segmento"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        partnerships = {}
        
        for seg in self.segmentos:
            recomendaciones = []
            
            # Partnerships por tamaño
            if seg.firmograficos.tamano == TamanoEmpresa.STARTUP:
                recomendaciones.extend([
                    "Aceleradoras e incubadoras",
                    "Venture capital firms",
                    "Comunidades de startups",
                    "Influencers del ecosistema startup"
                ])
            elif seg.firmograficos.tamano == TamanoEmpresa.MEDIANA:
                recomendaciones.extend([
                    "Consultoras especializadas en la industria",
                    "Integradores de sistemas",
                    "Agencias de marketing B2B",
                    "Plataformas de marketplace"
                ])
            else:
                recomendaciones.extend([
                    "Grandes consultoras (Big 4)",
                    "Vendors enterprise establecidos",
                    "Asociaciones de industria",
                    "Eventos y conferencias enterprise"
                ])
            
            # Partnerships por industria
            if seg.firmograficos.industria == Industria.FINANZAS:
                recomendaciones.append("Instituciones financieras y bancos")
            elif seg.firmograficos.industria == Industria.SALUD:
                recomendaciones.append("Hospitales y sistemas de salud")
            elif seg.firmograficos.industria == Industria.RETAIL:
                recomendaciones.append("Plataformas de e-commerce y marketplaces")
            
            # Partnerships por geografía
            if seg.firmograficos.geografia == Geografia.LATAM:
                recomendaciones.append("Partners locales con conocimiento regional")
            elif seg.firmograficos.geografia == Geografia.GLOBAL:
                recomendaciones.append("Partners multi-región con presencia global")
            
            partnerships[seg.nombre] = {
                "partnerships_recomendados": recomendaciones,
                "tipo_partnership": self._determinar_tipo_partnership(seg),
                "valor_esperado": self._estimar_valor_partnership(seg)
            }
        
        return partnerships
    
    def _determinar_tipo_partnership(self, segmento: Segmento) -> str:
        """Determina el tipo de partnership más adecuado"""
        if segmento.firmograficos.tamano == TamanoEmpresa.STARTUP:
            return "Ecosystem partnerships (aceleradoras, VCs)"
        elif segmento.comportamentales.urgencia_problema == UrgenciaProblema.CRITICA:
            return "Solution partnerships (integradores, consultoras)"
        elif segmento.firmograficos.geografia == Geografia.GLOBAL:
            return "Channel partnerships (distribuidores, resellers)"
        else:
            return "Strategic partnerships (complementarios)"
    
    def _estimar_valor_partnership(self, segmento: Segmento) -> str:
        """Estima el valor potencial del partnership"""
        score = segmento.calcular_score_segmento()
        if score >= 8.0:
            return "Alto - Potencial de aceleración significativa"
        elif score >= 7.0:
            return "Medio-Alto - Beneficio claro para crecimiento"
        else:
            return "Medio - Beneficio moderado"
    
    def analisis_mercado_total(self) -> Dict:
        """Análisis agregado del mercado total (TAM/SAM/SOM)"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        tam_total = 0
        sam_total = 0
        som_total = 0
        segmentos_con_metricas = 0
        
        for seg in self.segmentos:
            if seg.metricas_mercado:
                tam_total += seg.metricas_mercado.tam
                sam_total += seg.metricas_mercado.sam
                som_total += seg.metricas_mercado.som
                segmentos_con_metricas += 1
        
        crecimiento_promedio = 0
        if segmentos_con_metricas > 0:
            crecimiento_promedio = sum(
                s.metricas_mercado.tasa_crecimiento_anual 
                for s in self.segmentos 
                if s.metricas_mercado
            ) / segmentos_con_metricas
        
        return {
            "tam_total": tam_total,
            "sam_total": sam_total,
            "som_total": som_total,
            "segmentos_con_metricas": segmentos_con_metricas,
            "crecimiento_promedio": crecimiento_promedio,
            "penetracion_actual": (som_total / sam_total * 100) if sam_total > 0 else 0,
            "oportunidad_crecimiento": sam_total - som_total,
            "evaluacion": self._evaluar_mercado_total(tam_total, sam_total, som_total)
        }
    
    def _evaluar_mercado_total(self, tam: float, sam: float, som: float) -> Dict:
        """Evalúa el mercado total"""
        evaluacion = {
            "tamano_mercado": "Muy Grande" if tam > 10000 else "Grande" if tam > 5000 else "Mediano" if tam > 1000 else "Pequeño",
            "oportunidad": "Excelente" if (sam - som) > 1000 else "Buena" if (sam - som) > 500 else "Moderada",
            "recomendacion": ""
        }
        
        if (sam - som) > 1000:
            evaluacion["recomendacion"] = "Mercado con gran oportunidad de crecimiento. Enfoque en expansión agresiva."
        elif (sam - som) > 500:
            evaluacion["recomendacion"] = "Mercado con buena oportunidad. Enfoque en penetración selectiva."
        else:
            evaluacion["recomendacion"] = "Mercado con oportunidad moderada. Enfoque en optimización y diferenciación."
        
        return evaluacion
    
    def comparacion_lado_a_lado(self, segmento_ids: List[str]) -> Dict:
        """Comparación detallada lado a lado de segmentos"""
        
        segmentos_seleccionados = [s for s in self.segmentos if s.id in segmento_ids]
        
        if len(segmentos_seleccionados) < 2:
            return {"error": "Se necesitan al menos 2 segmentos para comparar"}
        
        comparacion = {
            "segmentos": [s.nombre for s in segmentos_seleccionados],
            "comparacion_detallada": {}
        }
        
        # Comparar todas las métricas clave
        metricas = [
            "score_total", "score_oportunidad", "score_riesgo", "score_prioridad",
            "tamano", "crecimiento", "accesibilidad", "competencia", "ajuste_producto"
        ]
        
        for metrica in metricas:
            valores = []
            for seg in segmentos_seleccionados:
                if metrica == "score_total":
                    valores.append(seg.calcular_score_segmento())
                elif metrica == "score_oportunidad":
                    valores.append(seg.scoring.calcular_score_oportunidad())
                elif metrica == "score_riesgo":
                    valores.append(seg.scoring.calcular_score_riesgo())
                elif metrica == "score_prioridad":
                    valores.append(seg.calcular_score_prioridad())
                else:
                    valores.append(getattr(seg.scoring, metrica, 0))
            
            comparacion["comparacion_detallada"][metrica] = {
                "valores": dict(zip([s.nombre for s in segmentos_seleccionados], valores)),
                "mejor": segmentos_seleccionados[valores.index(max(valores))].nombre if valores else None,
                "diferencia": max(valores) - min(valores) if valores else 0
            }
        
        # Comparar unidad económica
        unidades_economicas = {}
        for seg in segmentos_seleccionados:
            unidad = self.calcular_unidad_economica(seg.id)
            unidades_economicas[seg.nombre] = unidad
        
        comparacion["unidad_economica"] = unidades_economicas
        
        # Recomendación comparativa
        mejor_score = max(segmentos_seleccionados, key=lambda s: s.calcular_score_segmento())
        mejor_oportunidad = max(segmentos_seleccionados, key=lambda s: s.scoring.calcular_score_oportunidad())
        menor_riesgo = min(segmentos_seleccionados, key=lambda s: s.scoring.calcular_score_riesgo())
        
        comparacion["recomendacion"] = {
            "mejor_score_total": mejor_score.nombre,
            "mejor_oportunidad": mejor_oportunidad.nombre,
            "menor_riesgo": menor_riesgo.nombre,
            "estrategia_recomendada": f"Enfoque principal en {mejor_score.nombre} con {mejor_oportunidad.nombre} como secundario"
        }
        
        return comparacion
    
    def generar_reporte_ejecutivo(self) -> str:
        """Genera reporte ejecutivo en formato legible"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        reporte = []
        reporte.append("=" * 100)
        reporte.append("REPORTE EJECUTIVO - ANÁLISIS DE SEGMENTACIÓN DE MERCADO")
        reporte.append("=" * 100)
        reporte.append(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        reporte.append(f"Total de Segmentos Analizados: {len(self.segmentos)}\n")
        
        # Resumen ejecutivo
        reporte.append("\n" + "-" * 100)
        reporte.append("RESUMEN EJECUTIVO")
        reporte.append("-" * 100)
        
        if self.segmento_primario:
            reporte.append(f"\n🎯 Segmento Primario: {self.segmento_primario.nombre}")
            reporte.append(f"   Score Total: {self.segmento_primario.calcular_score_segmento():.2f}/10")
            reporte.append(f"   Oportunidad: {self.segmento_primario.scoring.calcular_score_oportunidad():.2f}")
            reporte.append(f"   Riesgo: {self.segmento_primario.scoring.calcular_score_riesgo():.2f}")
        
        if self.segmento_secundario:
            reporte.append(f"\n📊 Segmento Secundario: {self.segmento_secundario.nombre}")
            reporte.append(f"   Score Total: {self.segmento_secundario.calcular_score_segmento():.2f}/10")
        
        # Análisis de mercado total
        mercado_total = self.analisis_mercado_total()
        reporte.append("\n" + "-" * 100)
        reporte.append("ANÁLISIS DE MERCADO TOTAL")
        reporte.append("-" * 100)
        reporte.append(f"\nTAM Total: ${mercado_total['tam_total']:,.0f}M")
        reporte.append(f"SAM Total: ${mercado_total['sam_total']:,.0f}M")
        reporte.append(f"SOM Total: ${mercado_total['som_total']:,.0f}M")
        reporte.append(f"Crecimiento Promedio: {mercado_total['crecimiento_promedio']:.1f}%")
        reporte.append(f"Penetración Actual: {mercado_total['penetracion_actual']:.1f}%")
        reporte.append(f"Oportunidad de Crecimiento: ${mercado_total['oportunidad_crecimiento']:,.0f}M")
        
        # Top 3 segmentos
        top_segmentos = sorted(self.segmentos, key=lambda s: s.calcular_score_segmento(), reverse=True)[:3]
        reporte.append("\n" + "-" * 100)
        reporte.append("TOP 3 SEGMENTOS")
        reporte.append("-" * 100)
        for i, seg in enumerate(top_segmentos, 1):
            reporte.append(f"\n{i}. {seg.nombre}")
            reporte.append(f"   Score: {seg.calcular_score_segmento():.2f}/10")
            reporte.append(f"   Industria: {seg.firmograficos.industria.value}")
            reporte.append(f"   Geografía: {seg.firmograficos.geografia.value}")
        
        # Plan de acción
        plan = self.generar_plan_accion_ejecutable()
        reporte.append("\n" + "-" * 100)
        reporte.append("PLAN DE ACCIÓN - PRÓXIMOS PASOS")
        reporte.append("-" * 100)
        reporte.append("\nAcciones Inmediatas:")
        for accion in plan["acciones_inmediatas"][:3]:
            reporte.append(f"   • {accion}")
        
        return "\n".join(reporte)
    
    def analisis_roi_por_segmento(self, segmento_id: str, inversion_inicial: float, horizonte_anos: int = 3) -> Dict:
        """Análisis de ROI detallado para un segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {"error": "Segmento no encontrado"}
        
        unidad_economica = self.calcular_unidad_economica(segmento.id)
        cac = unidad_economica.get("cac", 0)
        ltv = unidad_economica.get("ltv", 0)
        precio_anual = segmento.precio_promedio_anual or self._estimar_precio(segmento)
        tasa_conversion = segmento.tasa_conversion_esperada or 10.0
        
        # Proyección de clientes y ingresos
        proyeccion = []
        clientes_acumulados = 0
        ingresos_acumulados = 0
        inversion_acumulada = inversion_inicial
        
        for ano in range(1, horizonte_anos + 1):
            # Estimar nuevos clientes (asumiendo crecimiento)
            nuevos_clientes_ano = (inversion_inicial / cac) * (1.2 ** (ano - 1)) if cac > 0 else 0
            nuevos_clientes_ano *= (tasa_conversion / 100)
            clientes_acumulados += nuevos_clientes_ano
            
            # Ingresos del año
            ingresos_ano = clientes_acumulados * precio_anual
            
            # Costos del año (CAC de nuevos clientes + costos operativos)
            costos_ano = nuevos_clientes_ano * cac + (clientes_acumulados * precio_anual * 0.3)  # 30% costo servicio
            
            # Flujo de caja
            flujo_caja = ingresos_ano - costos_ano
            ingresos_acumulados += ingresos_ano
            inversion_acumulada += costos_ano
            
            proyeccion.append({
                "ano": ano,
                "nuevos_clientes": nuevos_clientes_ano,
                "clientes_totales": clientes_acumulados,
                "ingresos_ano": ingresos_ano,
                "costos_ano": costos_ano,
                "flujo_caja": flujo_caja,
                "ingresos_acumulados": ingresos_acumulados,
                "inversion_acumulada": inversion_acumulada
            })
        
        # Calcular ROI
        roi_total = ((ingresos_acumulados - inversion_acumulada) / inversion_acumulada) * 100 if inversion_acumulada > 0 else 0
        roi_anualizado = ((1 + roi_total / 100) ** (1 / horizonte_anos) - 1) * 100
        
        # Payback period
        payback_ano = None
        for proy in proyeccion:
            if proy["ingresos_acumulados"] >= inversion_acumulada:
                payback_ano = proy["ano"]
                break
        
        return {
            "segmento": segmento.nombre,
            "inversion_inicial": inversion_inicial,
            "horizonte_anos": horizonte_anos,
            "proyeccion": proyeccion,
            "metricas_finales": {
                "ingresos_totales": ingresos_acumulados,
                "inversion_total": inversion_acumulada,
                "roi_total": roi_total,
                "roi_anualizado": roi_anualizado,
                "payback_ano": payback_ano,
                "clientes_finales": clientes_acumulados
            },
            "evaluacion": self._evaluar_roi(roi_total, payback_ano, horizonte_anos)
        }
    
    def _evaluar_roi(self, roi_total: float, payback_ano: Optional[int], horizonte_anos: int) -> Dict:
        """Evalúa el ROI del segmento"""
        evaluacion = {
            "calificacion": "",
            "recomendacion": ""
        }
        
        if roi_total >= 200:
            evaluacion["calificacion"] = "Excelente"
            evaluacion["recomendacion"] = "ROI excepcional. Inversión altamente recomendada."
        elif roi_total >= 100:
            evaluacion["calificacion"] = "Muy Bueno"
            evaluacion["recomendacion"] = "ROI muy positivo. Inversión recomendada."
        elif roi_total >= 50:
            evaluacion["calificacion"] = "Bueno"
            evaluacion["recomendacion"] = "ROI positivo. Considerar inversión con optimización."
        elif roi_total >= 0:
            evaluacion["calificacion"] = "Marginal"
            evaluacion["recomendacion"] = "ROI bajo. Requiere optimización antes de invertir."
        else:
            evaluacion["calificacion"] = "Negativo"
            evaluacion["recomendacion"] = "ROI negativo. No recomendar inversión sin cambios significativos."
        
        if payback_ano and payback_ano <= horizonte_anos / 2:
            evaluacion["recomendacion"] += " Payback rápido."
        
        return evaluacion
    
    def analisis_ciclo_vida_cliente(self, segmento_id: str) -> Dict:
        """Análisis del ciclo de vida del cliente por segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {"error": "Segmento no encontrado"}
        
        unidad_economica = self.calcular_unidad_economica(segmento.id)
        tasa_retencion = self._estimar_tasa_retencion(segmento)
        vida_media = unidad_economica.get("vida_media_cliente_anos", 0)
        precio_anual = segmento.precio_promedio_anual or self._estimar_precio(segmento)
        
        # Fases del ciclo de vida
        fases = {
            "adquisicion": {
                "duracion_meses": segmento.ciclo_venta_dias / 30 if segmento.ciclo_venta_dias else 3,
                "costo": unidad_economica.get("cac", 0),
                "actividades": self._actividades_fase_adquisicion(segmento)
            },
            "activacion": {
                "duracion_meses": 1,
                "costo": precio_anual * 0.1,  # 10% del precio anual
                "actividades": self._actividades_fase_activacion(segmento)
            },
            "retencion": {
                "duracion_meses": (vida_media * 12) - 4,
                "costo_mensual": precio_anual * 0.05 / 12,  # 5% del precio anual mensual
                "actividades": self._actividades_fase_retencion(segmento)
            },
            "expansion": {
                "probabilidad": 0.3 if segmento.firmograficos.tamano != TamanoEmpresa.STARTUP else 0.1,
                "valor_promedio": precio_anual * 0.5,  # 50% adicional
                "actividades": self._actividades_fase_expansion(segmento)
            },
            "referencia": {
                "probabilidad": 0.2 if tasa_retencion >= 0.85 else 0.1,
                "valor_referencia": unidad_economica.get("cac", 0) * 0.5,  # 50% del CAC
                "actividades": self._actividades_fase_referencia(segmento)
            }
        }
        
        # Valor total del ciclo de vida
        valor_retencion = precio_anual * vida_media
        valor_expansion = fases["expansion"]["valor_promedio"] * fases["expansion"]["probabilidad"]
        valor_referencia = fases["referencia"]["valor_referencia"] * fases["referencia"]["probabilidad"]
        valor_total_clv = valor_retencion + valor_expansion + valor_referencia
        
        return {
            "segmento": segmento.nombre,
            "vida_media_cliente_anos": vida_media,
            "tasa_retencion": tasa_retencion,
            "fases": fases,
            "valor_total_clv": valor_total_clv,
            "recomendaciones": self._recomendaciones_ciclo_vida(segmento, tasa_retencion, vida_media)
        }
    
    def _actividades_fase_adquisicion(self, segmento: Segmento) -> List[str]:
        """Actividades de fase de adquisición"""
        actividades = ["Prospección", "Demos", "Negociación"]
        if segmento.ciclo_venta_dias and segmento.ciclo_venta_dias >= 90:
            actividades.append("Pilotos")
            actividades.append("Aprobaciones múltiples")
        return actividades
    
    def _actividades_fase_activacion(self, segmento: Segmento) -> List[str]:
        """Actividades de fase de activación"""
        return ["Onboarding", "Configuración inicial", "Entrenamiento", "Primera implementación exitosa"]
    
    def _actividades_fase_retencion(self, segmento: Segmento) -> List[str]:
        """Actividades de fase de retención"""
        actividades = ["Soporte continuo", "Actualizaciones", "Check-ins regulares"]
        if segmento.comportamentales.urgencia_problema == UrgenciaProblema.CRITICA:
            actividades.append("SLA garantizado")
        return actividades
    
    def _actividades_fase_expansion(self, segmento: Segmento) -> List[str]:
        """Actividades de fase de expansión"""
        return ["Upsell de features", "Expansión de usuarios", "Nuevos casos de uso", "Contratos adicionales"]
    
    def _actividades_fase_referencia(self, segmento: Segmento) -> List[str]:
        """Actividades de fase de referencia"""
        return ["Case studies", "Testimonios", "Referencias", "Eventos de clientes"]
    
    def _recomendaciones_ciclo_vida(self, segmento: Segmento, tasa_retencion: float, vida_media: float) -> List[str]:
        """Recomendaciones basadas en ciclo de vida"""
        recomendaciones = []
        
        if tasa_retencion < 0.8:
            recomendaciones.append("Mejorar programas de retención - tasa de retención baja")
        
        if vida_media < 2:
            recomendaciones.append("Enfoque en aumentar vida media del cliente")
        
        if segmento.firmograficos.tamano != TamanoEmpresa.STARTUP:
            recomendaciones.append("Desarrollar programa de expansión para aumentar LTV")
        
        recomendaciones.append("Implementar programa de referencias para reducir CAC")
        
        return recomendaciones
    
    def matriz_priorizacion_mejorada(self) -> Dict:
        """Matriz de priorización mejorada con múltiples dimensiones"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        matriz = {
            "alta_prioridad": [],
            "media_alta_prioridad": [],
            "media_prioridad": [],
            "baja_prioridad": []
        }
        
        for seg in self.segmentos:
            score_prioridad = seg.calcular_score_prioridad()
            score_atractivo = seg.calcular_score_segmento()
            score_oportunidad = seg.scoring.calcular_score_oportunidad()
            score_riesgo = seg.scoring.calcular_score_riesgo()
            
            # Cálculo de prioridad mejorado
            prioridad_score = (
                score_atractivo * 0.3 +
                score_oportunidad * 0.3 +
                (1 - score_riesgo) * 0.2 +
                score_prioridad / 10 * 0.2
            ) * 10
            
            segmento_info = {
                "nombre": seg.nombre,
                "score_prioridad": prioridad_score,
                "score_atractivo": score_atractivo,
                "score_oportunidad": score_oportunidad,
                "score_riesgo": score_riesgo,
                "recomendacion": self._recomendacion_prioridad(prioridad_score)
            }
            
            if prioridad_score >= 8.0:
                matriz["alta_prioridad"].append(segmento_info)
            elif prioridad_score >= 7.0:
                matriz["media_alta_prioridad"].append(segmento_info)
            elif prioridad_score >= 6.0:
                matriz["media_prioridad"].append(segmento_info)
            else:
                matriz["baja_prioridad"].append(segmento_info)
        
        # Ordenar por score de prioridad
        for categoria in matriz:
            matriz[categoria] = sorted(matriz[categoria], key=lambda x: x["score_prioridad"], reverse=True)
        
        return matriz
    
    def _recomendacion_prioridad(self, score: float) -> str:
        """Genera recomendación basada en score de prioridad"""
        if score >= 8.0:
            return "Prioridad máxima - Enfoque inmediato"
        elif score >= 7.0:
            return "Alta prioridad - Iniciar pronto"
        elif score >= 6.0:
            return "Prioridad media - Considerar después"
        else:
            return "Baja prioridad - Revisar más adelante"
    
    def analisis_inversion_recomendada(self) -> Dict:
        """Recomienda inversión por segmento basado en ROI esperado"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        inversiones = []
        
        for seg in self.segmentos:
            # Estimar inversión inicial necesaria
            unidad_economica = self.calcular_unidad_economica(seg.id)
            cac = unidad_economica.get("cac", 0)
            
            # Inversión para adquirir primeros 20 clientes
            inversion_20_clientes = cac * 20 / (seg.tasa_conversion_esperada / 100) if seg.tasa_conversion_esperada else cac * 200
            
            # Análisis de ROI a 3 años
            roi_analisis = self.analisis_roi_por_segmento(seg.id, inversion_20_clientes, 3)
            
            inversiones.append({
                "segmento": seg.nombre,
                "inversion_recomendada": inversion_20_clientes,
                "roi_esperado_3anos": roi_analisis.get("metricas_finales", {}).get("roi_total", 0),
                "payback_ano": roi_analisis.get("metricas_finales", {}).get("payback_ano"),
                "evaluacion": roi_analisis.get("evaluacion", {}).get("calificacion", "N/A"),
                "recomendacion": self._recomendacion_inversion(roi_analisis.get("metricas_finales", {}).get("roi_total", 0))
            })
        
        # Ordenar por ROI esperado
        inversiones.sort(key=lambda x: x["roi_esperado_3anos"], reverse=True)
        
        return {
            "total_segmentos": len(inversiones),
            "inversiones_recomendadas": inversiones,
            "inversion_total_recomendada": sum(i["inversion_recomendada"] for i in inversiones),
            "top_3_inversiones": inversiones[:3]
        }
    
    def _recomendacion_inversion(self, roi: float) -> str:
        """Genera recomendación de inversión"""
        if roi >= 100:
            return "Inversión altamente recomendada - ROI excelente"
        elif roi >= 50:
            return "Inversión recomendada - ROI positivo"
        elif roi >= 0:
            return "Inversión condicional - Requiere optimización"
        else:
            return "No recomendar inversión - ROI negativo"
    
    def analisis_riesgo_financiero(self) -> Dict:
        """Análisis de riesgo financiero por segmento"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        riesgos = []
        
        for seg in self.segmentos:
            unidad_economica = self.calcular_unidad_economica(seg.id)
            ratio_ltv_cac = unidad_economica.get("ratio_ltv_cac", 0)
            payback = unidad_economica.get("payback_meses", 0)
            margen = unidad_economica.get("margen_porcentaje", 0)
            
            # Calcular score de riesgo financiero
            riesgo_score = 0
            
            # Riesgo por ratio LTV:CAC
            if ratio_ltv_cac < 3:
                riesgo_score += 3
            elif ratio_ltv_cac < 5:
                riesgo_score += 2
            elif ratio_ltv_cac < 10:
                riesgo_score += 1
            
            # Riesgo por payback
            if payback > 12:
                riesgo_score += 3
            elif payback > 6:
                riesgo_score += 2
            elif payback > 3:
                riesgo_score += 1
            
            # Riesgo por margen
            if margen < 20:
                riesgo_score += 2
            elif margen < 40:
                riesgo_score += 1
            
            # Clasificar riesgo
            if riesgo_score >= 6:
                nivel_riesgo = "Alto"
            elif riesgo_score >= 3:
                nivel_riesgo = "Medio"
            else:
                nivel_riesgo = "Bajo"
            
            riesgos.append({
                "segmento": seg.nombre,
                "nivel_riesgo": nivel_riesgo,
                "score_riesgo": riesgo_score,
                "ratio_ltv_cac": ratio_ltv_cac,
                "payback_meses": payback,
                "margen_porcentaje": margen,
                "mitigaciones": self._mitigaciones_riesgo_financiero(riesgo_score, ratio_ltv_cac, payback, margen)
            })
        
        return {
            "total_segmentos": len(riesgos),
            "riesgos": sorted(riesgos, key=lambda x: x["score_riesgo"], reverse=True),
            "resumen": {
                "alto_riesgo": len([r for r in riesgos if r["nivel_riesgo"] == "Alto"]),
                "medio_riesgo": len([r for r in riesgos if r["nivel_riesgo"] == "Medio"]),
                "bajo_riesgo": len([r for r in riesgos if r["nivel_riesgo"] == "Bajo"])
            }
        }
    
    def _mitigaciones_riesgo_financiero(self, riesgo_score: int, ratio: float, payback: float, margen: float) -> List[str]:
        """Genera mitigaciones para riesgo financiero"""
        mitigaciones = []
        
        if ratio < 3:
            mitigaciones.append("Reducir CAC o aumentar LTV para mejorar ratio")
        
        if payback > 12:
            mitigaciones.append("Acelerar payback period optimizando proceso de ventas")
        
        if margen < 20:
            mitigaciones.append("Mejorar márgenes optimizando costos o aumentando precio")
        
        if riesgo_score >= 6:
            mitigaciones.append("Considerar estrategia alternativa o segmento diferente")
        
        return mitigaciones
    
    def analisis_customer_journey(self, segmento_id: str) -> Dict:
        """Análisis del customer journey por segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {"error": "Segmento no encontrado"}
        
        journey = {
            "segmento": segmento.nombre,
            "etapas": [],
            "puntos_contacto": [],
            "momentos_verdad": [],
            "fricciones": [],
            "oportunidades_optimizacion": []
        }
        
        # Etapas del journey
        etapas = [
            {
                "nombre": "Awareness",
                "descripcion": "Cliente descubre el problema y busca soluciones",
                "actividades": self._actividades_awareness(segmento),
                "canales": self._canales_awareness(segmento),
                "duracion_estimada": "2-4 semanas"
            },
            {
                "nombre": "Consideration",
                "descripcion": "Cliente evalúa opciones y compara soluciones",
                "actividades": self._actividades_consideration(segmento),
                "canales": self._canales_consideration(segmento),
                "duracion_estimada": f"{segmento.ciclo_venta_dias // 2 if segmento.ciclo_venta_dias else 30} días"
            },
            {
                "nombre": "Decision",
                "descripcion": "Cliente toma decisión de compra",
                "actividades": self._actividades_decision(segmento),
                "canales": self._canales_decision(segmento),
                "duracion_estimada": f"{segmento.ciclo_venta_dias // 2 if segmento.ciclo_venta_dias else 30} días"
            },
            {
                "nombre": "Onboarding",
                "descripcion": "Cliente se integra y comienza a usar el producto",
                "actividades": self._actividades_onboarding(segmento),
                "canales": self._canales_onboarding(segmento),
                "duracion_estimada": "2-4 semanas"
            },
            {
                "nombre": "Adoption",
                "descripcion": "Cliente adopta el producto y obtiene valor",
                "actividades": self._actividades_adoption(segmento),
                "canales": self._canales_adoption(segmento),
                "duracion_estimada": "1-3 meses"
            },
            {
                "nombre": "Expansion",
                "descripcion": "Cliente expande uso y adopta más features",
                "actividades": self._actividades_expansion(segmento),
                "canales": self._canales_expansion(segmento),
                "duracion_estimada": "Ongoing"
            }
        ]
        
        journey["etapas"] = etapas
        
        # Puntos de contacto críticos
        journey["puntos_contacto"] = [
            "Primera interacción con contenido",
            "Demo o trial",
            "Conversación con ventas",
            "Onboarding inicial",
            "Primera implementación exitosa",
            "Check-ins regulares"
        ]
        
        # Momentos de verdad
        journey["momentos_verdad"] = [
            "Primera demo exitosa",
            "Onboarding sin fricciones",
            "Primera implementación exitosa",
            "Primer valor obtenido",
            "Primera expansión"
        ]
        
        # Fricciones identificadas
        if segmento.ciclo_venta_dias and segmento.ciclo_venta_dias > 90:
            journey["fricciones"].append("Ciclo de venta largo - múltiples aprobaciones")
        
        if segmento.firmograficos.tamano == TamanoEmpresa.ENTERPRISE:
            journey["fricciones"].append("Múltiples stakeholders - proceso complejo")
        
        if segmento.psicograficos.aversion_riesgo == AversionRiesgo.ALTA:
            journey["fricciones"].append("Alta aversión al riesgo - requiere más validación")
        
        # Oportunidades de optimización
        journey["oportunidades_optimizacion"] = [
            "Automatizar proceso de onboarding",
            "Crear contenido educativo para awareness",
            "Desarrollar casos de estudio para consideration",
            "Simplificar proceso de decisión",
            "Implementar programa de éxito del cliente"
        ]
        
        return journey
    
    def _actividades_awareness(self, segmento: Segmento) -> List[str]:
        """Actividades de etapa awareness"""
        return ["Content marketing", "SEO", "Social media", "Webinars", "Eventos"]
    
    def _canales_awareness(self, segmento: Segmento) -> List[str]:
        """Canales de etapa awareness"""
        if segmento.firmograficos.tamano == TamanoEmpresa.STARTUP:
            return ["LinkedIn", "Twitter", "Blog", "Comunidades online"]
        else:
            return ["LinkedIn", "Email marketing", "Webinars", "Eventos B2B"]
    
    def _actividades_consideration(self, segmento: Segmento) -> List[str]:
        """Actividades de etapa consideration"""
        return ["Demos", "Trials", "Case studies", "Comparaciones", "ROI calculators"]
    
    def _canales_consideration(self, segmento: Segmento) -> List[str]:
        """Canales de etapa consideration"""
        return ["Website", "Email", "Sales calls", "Webinars"]
    
    def _actividades_decision(self, segmento: Segmento) -> List[str]:
        """Actividades de etapa decision"""
        actividades = ["Negociación", "Contratos", "Aprobaciones"]
        if segmento.ciclo_venta_dias and segmento.ciclo_venta_dias >= 90:
            actividades.extend(["Pilotos", "Pruebas de concepto"])
        return actividades
    
    def _canales_decision(self, segmento: Segmento) -> List[str]:
        """Canales de etapa decision"""
        return ["Sales calls", "Email", "Contratos digitales"]
    
    def _actividades_onboarding(self, segmento: Segmento) -> List[str]:
        """Actividades de etapa onboarding"""
        return ["Setup inicial", "Configuración", "Entrenamiento", "Primera implementación"]
    
    def _canales_onboarding(self, segmento: Segmento) -> List[str]:
        """Canales de etapa onboarding"""
        return ["Email", "Video calls", "Documentación", "Support"]
    
    def _actividades_adoption(self, segmento: Segmento) -> List[str]:
        """Actividades de etapa adoption"""
        return ["Uso regular", "Implementación de features", "Obtención de valor"]
    
    def _canales_adoption(self, segmento: Segmento) -> List[str]:
        """Canales de etapa adoption"""
        return ["In-app", "Email", "Support", "Check-ins"]
    
    def _actividades_expansion(self, segmento: Segmento) -> List[str]:
        """Actividades de etapa expansion"""
        return ["Upsell", "Nuevos casos de uso", "Expansión de usuarios"]
    
    def _canales_expansion(self, segmento: Segmento) -> List[str]:
        """Canales de etapa expansion"""
        return ["Account management", "Email", "In-app prompts"]
    
    def estrategia_producto_por_segmento(self, segmento_id: str) -> Dict:
        """Recomendaciones de estrategia de producto por segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {"error": "Segmento no encontrado"}
        
        estrategia = {
            "segmento": segmento.nombre,
            "prioridades_producto": [],
            "features_criticas": [],
            "roadmap_recomendado": {},
            "metricas_producto": {},
            "recomendaciones": []
        }
        
        # Prioridades de producto basadas en características del segmento
        if segmento.comportamentales.urgencia_problema == UrgenciaProblema.CRITICA:
            estrategia["prioridades_producto"].extend([
                "Resolución rápida del problema crítico",
                "Alta confiabilidad y uptime",
                "Soporte 24/7"
            ])
        
        if segmento.firmograficos.tamano == TamanoEmpresa.ENTERPRISE:
            estrategia["prioridades_producto"].extend([
                "Escalabilidad",
                "Seguridad y compliance",
                "Integraciones enterprise",
                "White-label options"
            ])
        elif segmento.firmograficos.tamano == TamanoEmpresa.STARTUP:
            estrategia["prioridades_producto"].extend([
                "Facilidad de uso",
                "Setup rápido",
                "Pricing flexible",
                "APIs abiertas"
            ])
        
        # Features críticas
        if segmento.scoring.ajuste_producto >= 9.0:
            estrategia["features_criticas"].append("Core features que resuelven el problema principal")
        
        if segmento.comportamentales.adopcion_tecnologica == AdopcionTecnologica.INNOVADOR:
            estrategia["features_criticas"].append("Features innovadoras y diferenciadoras")
        
        if segmento.firmograficos.madurez_digital == MadurezDigital.AVANZADO:
            estrategia["features_criticas"].append("Integraciones avanzadas y APIs")
        
        # Roadmap recomendado
        estrategia["roadmap_recomendado"] = {
            "corto_plazo_3meses": [
                "Optimizar features core para mejor ajuste producto-mercado",
                "Mejorar onboarding y primera experiencia",
                "Implementar métricas de adopción"
            ],
            "medio_plazo_6meses": [
                "Desarrollar features de expansión",
                "Mejorar integraciones",
                "Optimizar para escalabilidad"
            ],
            "largo_plazo_12meses": [
                "Features avanzadas y diferenciadoras",
                "Expansión a nuevos casos de uso",
                "Plataforma y ecosistema"
            ]
        }
        
        # Métricas de producto
        estrategia["metricas_producto"] = {
            "adopcion_objetivo": "70% de usuarios activos mensuales",
            "tiempo_valor_objetivo": "< 7 días",
            "retencion_objetivo": "85%+ retención anual",
            "nps_objetivo": "50+",
            "expansion_rate_objetivo": "30% de clientes expanden en 12 meses"
        }
        
        # Recomendaciones
        estrategia["recomendaciones"] = [
            f"Enfoque en {segmento.firmograficos.industria.value} - features específicas de industria",
            "Desarrollar programa de early adopters para feedback rápido",
            "Implementar analytics de producto para entender uso",
            "Crear programa de éxito del cliente para retención"
        ]
        
        return estrategia
    
    def analisis_fit_canal(self, segmento_id: str) -> Dict:
        """Análisis de fit de canal por segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {"error": "Segmento no encontrado"}
        
        fit = {
            "segmento": segmento.nombre,
            "canales_evaluados": [],
            "mejor_fit": {},
            "recomendaciones": []
        }
        
        # Evaluar diferentes canales
        canales = {
            "self_service": {
                "nombre": "Self-Service",
                "score": 0,
                "pros": [],
                "contras": []
            },
            "inside_sales": {
                "nombre": "Inside Sales",
                "score": 0,
                "pros": [],
                "contras": []
            },
            "field_sales": {
                "nombre": "Field Sales",
                "score": 0,
                "pros": [],
                "contras": []
            },
            "partners": {
                "nombre": "Partners/Channel",
                "score": 0,
                "pros": [],
                "contras": []
            }
        }
        
        # Evaluar self-service
        if segmento.firmograficos.tamano == TamanoEmpresa.STARTUP and segmento.precio_promedio_anual and segmento.precio_promedio_anual < 10000:
            canales["self_service"]["score"] = 8
            canales["self_service"]["pros"] = ["Bajo costo", "Escalable", "Rápido"]
            canales["self_service"]["contras"] = ["Requiere producto intuitivo"]
        else:
            canales["self_service"]["score"] = 4
            canales["self_service"]["contras"] = ["Precio muy alto", "Complejidad alta"]
        
        # Evaluar inside sales
        if segmento.firmograficos.tamano in [TamanoEmpresa.MEDIANA, TamanoEmpresa.PEQUENA]:
            canales["inside_sales"]["score"] = 8
            canales["inside_sales"]["pros"] = ["Balance costo-efectividad", "Escalable"]
        else:
            canales["inside_sales"]["score"] = 6
        
        # Evaluar field sales
        if segmento.firmograficos.tamano == TamanoEmpresa.ENTERPRISE or (segmento.ciclo_venta_dias and segmento.ciclo_venta_dias >= 120):
            canales["field_sales"]["score"] = 9
            canales["field_sales"]["pros"] = ["Necesario para enterprise", "Alto valor"]
            canales["field_sales"]["contras"] = ["Alto costo", "No escalable"]
        else:
            canales["field_sales"]["score"] = 5
        
        # Evaluar partners
        if segmento.firmograficos.geografia == Geografia.GLOBAL or segmento.firmograficos.industria in [Industria.FINANZAS, Industria.SALUD]:
            canales["partners"]["score"] = 8
            canales["partners"]["pros"] = ["Acceso a mercado", "Credibilidad"]
        else:
            canales["partners"]["score"] = 6
        
        fit["canales_evaluados"] = list(canales.values())
        
        # Mejor fit
        mejor_canal = max(canales.items(), key=lambda x: x[1]["score"])
        fit["mejor_fit"] = {
            "canal": mejor_canal[1]["nombre"],
            "score": mejor_canal[1]["score"],
            "razones": mejor_canal[1]["pros"]
        }
        
        # Recomendaciones
        fit["recomendaciones"] = [
            f"Enfoque principal en {mejor_canal[1]['nombre']}",
            "Considerar modelo híbrido si múltiples canales tienen score alto",
            "Optimizar canal principal antes de expandir"
        ]
        
        return fit
    
    def analisis_contenido_messaging(self, segmento_id: str) -> Dict:
        """Análisis de contenido y messaging por segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {"error": "Segmento no encontrado"}
        
        contenido = {
            "segmento": segmento.nombre,
            "mensaje_principal": "",
            "value_propositions": [],
            "tipos_contenido": [],
            "tono_recomendado": "",
            "palabras_clave": [],
            "objetivos_contenido": []
        }
        
        # Mensaje principal
        industria = segmento.firmograficos.industria.value
        problema = "problema crítico" if segmento.comportamentales.urgencia_problema == UrgenciaProblema.CRITICA else "desafío clave"
        contenido["mensaje_principal"] = f"Para {industria} que enfrenta {problema}, [Producto] ofrece [Solución] que [Beneficio Principal]"
        
        # Value propositions
        if segmento.comportamentales.urgencia_problema == UrgenciaProblema.CRITICA:
            contenido["value_propositions"].append("Resuelve problema crítico inmediatamente")
        
        if segmento.scoring.ajuste_producto >= 9.0:
            contenido["value_propositions"].append("Ajuste perfecto producto-mercado")
        
        if segmento.firmograficos.tamano == TamanoEmpresa.ENTERPRISE:
            contenido["value_propositions"].append("Escalable y seguro para enterprise")
        elif segmento.firmograficos.tamano == TamanoEmpresa.STARTUP:
            contenido["value_propositions"].append("Rápido de implementar, perfecto para startups")
        
        # Tipos de contenido
        contenido["tipos_contenido"] = [
            "Case studies específicos de industria",
            "White papers técnicos",
            "Webinars educativos",
            "Blog posts sobre mejores prácticas",
            "Videos de producto",
            "ROI calculators",
            "Comparaciones competitivas"
        ]
        
        # Tono recomendado
        if segmento.firmograficos.tamano == TamanoEmpresa.ENTERPRISE:
            contenido["tono_recomendado"] = "Profesional, técnico, enfocado en ROI y seguridad"
        elif segmento.firmograficos.tamano == TamanoEmpresa.STARTUP:
            contenido["tono_recomendado"] = "Moderno, ágil, enfocado en velocidad e innovación"
        else:
            contenido["tono_recomendado"] = "Balanceado, práctico, enfocado en resultados"
        
        # Palabras clave
        contenido["palabras_clave"] = [
            industria.lower(),
            segmento.firmograficos.tamano.value.split()[0].lower(),
            "solución",
            "automatización" if segmento.firmograficos.madurez_digital == MadurezDigital.AVANZADO else "digitalización"
        ]
        
        # Objetivos de contenido
        contenido["objetivos_contenido"] = [
            "Generar awareness en el mercado objetivo",
            "Educar sobre el problema y solución",
            "Establecer thought leadership",
            "Generar leads cualificados",
            "Apoyar proceso de ventas"
        ]
        
        return contenido
    
    def analisis_competencia_comparativa(self) -> Dict:
        """Análisis comparativo de competencia entre segmentos"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        comparacion = {
            "segmentos_por_intensidad_competitiva": {},
            "segmentos_por_diferenciacion": {},
            "recomendaciones_competitivas": []
        }
        
        # Agrupar por intensidad competitiva
        baja_intensidad = []
        media_intensidad = []
        alta_intensidad = []
        
        for seg in self.segmentos:
            if seg.analisis_competencia:
                intensidad = seg.analisis_competencia.intensidad_competitiva
                if intensidad < 5:
                    baja_intensidad.append({
                        "segmento": seg.nombre,
                        "intensidad": intensidad,
                        "competidores": seg.analisis_competencia.numero_competidores
                    })
                elif intensidad < 7:
                    media_intensidad.append({
                        "segmento": seg.nombre,
                        "intensidad": intensidad,
                        "competidores": seg.analisis_competencia.numero_competidores
                    })
                else:
                    alta_intensidad.append({
                        "segmento": seg.nombre,
                        "intensidad": intensidad,
                        "competidores": seg.analisis_competencia.numero_competidores
                    })
        
        comparacion["segmentos_por_intensidad_competitiva"] = {
            "baja": baja_intensidad,
            "media": media_intensidad,
            "alta": alta_intensidad
        }
        
        # Agrupar por diferenciación posible
        alta_diferenciacion = []
        media_diferenciacion = []
        baja_diferenciacion = []
        
        for seg in self.segmentos:
            if seg.analisis_competencia:
                diferenciacion = seg.analisis_competencia.diferenciacion_posible
                if diferenciacion >= 8:
                    alta_diferenciacion.append({
                        "segmento": seg.nombre,
                        "diferenciacion": diferenciacion,
                        "oportunidad": "Alta oportunidad de diferenciación"
                    })
                elif diferenciacion >= 6:
                    media_diferenciacion.append({
                        "segmento": seg.nombre,
                        "diferenciacion": diferenciacion,
                        "oportunidad": "Oportunidad moderada de diferenciación"
                    })
                else:
                    baja_diferenciacion.append({
                        "segmento": seg.nombre,
                        "diferenciacion": diferenciacion,
                        "oportunidad": "Baja oportunidad - mercado commoditizado"
                    })
        
        comparacion["segmentos_por_diferenciacion"] = {
            "alta": alta_diferenciacion,
            "media": media_diferenciacion,
            "baja": baja_diferenciacion
        }
        
        # Recomendaciones competitivas
        if alta_diferenciacion:
            comparacion["recomendaciones_competitivas"].append(
                f"Enfoque en segmentos con alta diferenciación: {', '.join([s['segmento'] for s in alta_diferenciacion[:3]])}"
            )
        
        if baja_intensidad:
            comparacion["recomendaciones_competitivas"].append(
                f"Oportunidad en segmentos con baja competencia: {', '.join([s['segmento'] for s in baja_intensidad[:3]])}"
            )
        
        return comparacion
    
    def analisis_tendencias_temporales(self, anos_proyeccion: int = 5) -> Dict:
        """Análisis de tendencias temporales y evolución de segmentos"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        tendencias = {
            "proyeccion_mercado": {},
            "evolucion_segmentos": {},
            "tendencias_clave": []
        }
        
        # Proyección de mercado por año
        for ano in range(1, anos_proyeccion + 1):
            tam_proyectado = 0
            sam_proyectado = 0
            som_proyectado = 0
            
            for seg in self.segmentos:
                if seg.metricas_mercado:
                    crecimiento = seg.metricas_mercado.tasa_crecimiento_anual / 100
                    tam_proyectado += seg.metricas_mercado.tam * ((1 + crecimiento) ** ano)
                    sam_proyectado += seg.metricas_mercado.sam * ((1 + crecimiento) ** ano)
                    som_proyectado += seg.metricas_mercado.som * ((1 + crecimiento) ** ano)
            
            tendencias["proyeccion_mercado"][f"ano_{ano}"] = {
                "tam": tam_proyectado,
                "sam": sam_proyectado,
                "som": som_proyectado,
                "crecimiento_vs_anterior": 0  # Se calculará después
            }
        
        # Calcular crecimiento año sobre año
        for i in range(2, anos_proyeccion + 1):
            ano_actual = tendencias["proyeccion_mercado"][f"ano_{i}"]
            ano_anterior = tendencias["proyeccion_mercado"][f"ano_{i-1}"]
            if ano_anterior["sam"] > 0:
                ano_actual["crecimiento_vs_anterior"] = ((ano_actual["sam"] / ano_anterior["sam"]) - 1) * 100
        
        # Evolución de segmentos
        for seg in self.segmentos:
            if seg.metricas_mercado:
                crecimiento = seg.metricas_mercado.tasa_crecimiento_anual / 100
                evolucion = []
                
                for ano in range(1, anos_proyeccion + 1):
                    mercado_ano = seg.metricas_mercado.sam * ((1 + crecimiento) ** ano)
                    penetracion_ano = min(seg.metricas_mercado.penetracion_actual + (ano * 2), 30)  # Crecimiento de penetración
                    ingresos_ano = mercado_ano * (penetracion_ano / 100)
                    
                    evolucion.append({
                        "ano": ano,
                        "mercado": mercado_ano,
                        "penetracion": penetracion_ano,
                        "ingresos_potenciales": ingresos_ano
                    })
                
                tendencias["evolucion_segmentos"][seg.nombre] = evolucion
        
        # Tendencias clave
        tendencias["tendencias_clave"] = [
            "Mercado en crecimiento sostenido",
            "Penetración creciente en segmentos prioritarios",
            "Oportunidad de expansión geográfica",
            "Necesidad de diferenciación competitiva"
        ]
        
        return tendencias
    
    def estrategia_crecimiento_por_segmento(self, segmento_id: str) -> Dict:
        """Estrategia de crecimiento específica por segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {"error": "Segmento no encontrado"}
        
        estrategia = {
            "segmento": segmento.nombre,
            "fase_crecimiento": self._determinar_fase_crecimiento(segmento),
            "estrategias_recomendadas": [],
            "metricas_crecimiento": {},
            "roadmap_crecimiento": {}
        }
        
        # Determinar fase de crecimiento
        fase = estrategia["fase_crecimiento"]
        
        if fase == "Early Stage":
            estrategia["estrategias_recomendadas"].extend([
                "Enfoque en product-market fit",
                "Adquisición de primeros clientes",
                "Validación de modelo de negocio",
                "Construcción de casos de estudio"
            ])
        elif fase == "Growth Stage":
            estrategia["estrategias_recomendadas"].extend([
                "Escalamiento de adquisición",
                "Optimización de unidad económica",
                "Expansión geográfica",
                "Desarrollo de partnerships"
            ])
        elif fase == "Scale Stage":
            estrategia["estrategias_recomendadas"].extend([
                "Optimización de operaciones",
                "Expansión a segmentos relacionados",
                "Desarrollo de ecosistema",
                "Innovación continua"
            ])
        
        # Métricas de crecimiento
        unidad_economica = self.calcular_unidad_economica(segmento.id)
        estrategia["metricas_crecimiento"] = {
            "cac_objetivo": unidad_economica.get("cac", 0),
            "ltv_objetivo": unidad_economica.get("ltv", 0),
            "ratio_objetivo": unidad_economica.get("ratio_ltv_cac", 0),
            "tasa_crecimiento_mensual_objetivo": "10-15%",
            "tasa_expansion_objetivo": "30% en 12 meses"
        }
        
        # Roadmap de crecimiento
        estrategia["roadmap_crecimiento"] = {
            "trimestre_1": [
                "Validar modelo de adquisición",
                "Optimizar onboarding",
                "Establecer métricas base"
            ],
            "trimestre_2": [
                "Escalar canales exitosos",
                "Desarrollar programa de referencias",
                "Optimizar unidad económica"
            ],
            "trimestre_3": [
                "Expandir geográficamente",
                "Desarrollar partnerships",
                "Lanzar features de expansión"
            ],
            "trimestre_4": [
                "Consolidar posición",
                "Evaluar nuevos segmentos",
                "Preparar para siguiente fase"
            ]
        }
        
        return estrategia
    
    def _determinar_fase_crecimiento(self, segmento: Segmento) -> str:
        """Determina la fase de crecimiento del segmento"""
        score = segmento.calcular_score_segmento()
        
        if score >= 8.0:
            return "Growth Stage"
        elif score >= 7.0:
            return "Early Stage"
        else:
            return "Scale Stage"
    
    def analisis_customer_success(self, segmento_id: str) -> Dict:
        """Análisis de estrategia de customer success por segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {"error": "Segmento no encontrado"}
        
        success = {
            "segmento": segmento.nombre,
            "modelo_recomendado": "",
            "actividades_critical": [],
            "metricas_success": {},
            "programas_recomendados": [],
            "recomendaciones": []
        }
        
        # Determinar modelo de customer success
        if segmento.firmograficos.tamano == TamanoEmpresa.ENTERPRISE:
            success["modelo_recomendado"] = "Dedicated Customer Success Managers"
            success["actividades_critical"].extend([
                "QBRs (Quarterly Business Reviews)",
                "Account planning estratégico",
                "Soporte prioritario 24/7",
                "Programa de adopción avanzada"
            ])
        elif segmento.firmograficos.tamano == TamanoEmpresa.MEDIANA:
            success["modelo_recomendado"] = "Hybrid (CSM + Self-Service)"
            success["actividades_critical"].extend([
                "Onboarding estructurado",
                "Check-ins regulares",
                "Programa de adopción",
                "Soporte proactivo"
            ])
        else:
            success["modelo_recomendado"] = "Tech-Touch (Automated + Community)"
            success["actividades_critical"].extend([
                "Onboarding automatizado",
                "In-app guidance",
                "Comunidad de usuarios",
                "Knowledge base"
            ])
        
        # Métricas de success
        tasa_retencion = self._estimar_tasa_retencion(segmento)
        success["metricas_success"] = {
            "retencion_objetivo": tasa_retencion,
            "nps_objetivo": 50 if segmento.firmograficos.tamano == TamanoEmpresa.STARTUP else 60,
            "adopcion_objetivo": "70% de features core en uso",
            "expansion_rate_objetivo": "30% de clientes expanden",
            "time_to_value_objetivo": "< 30 días"
        }
        
        # Programas recomendados
        success["programas_recomendados"] = [
            "Programa de onboarding estructurado",
            "Programa de adopción de features",
            "Programa de expansión y upsell",
            "Programa de referencias",
            "Comunidad de usuarios"
        ]
        
        # Recomendaciones
        if segmento.comportamentales.urgencia_problema == UrgenciaProblema.CRITICA:
            success["recomendaciones"].append("Enfoque en time-to-value rápido - problema crítico")
        
        if tasa_retencion < 0.8:
            success["recomendaciones"].append("Mejorar programas de retención - tasa baja")
        
        success["recomendaciones"].append("Implementar programa de éxito del cliente desde día 1")
        
        return success
    
    def analisis_pricing_dinamico(self, segmento_id: str) -> Dict:
        """Análisis de pricing dinámico y optimización"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {"error": "Segmento no encontrado"}
        
        pricing = {
            "segmento": segmento.nombre,
            "modelo_pricing_recomendado": "",
            "estructura_precios": {},
            "optimizaciones": [],
            "estrategias_descuento": [],
            "recomendaciones": []
        }
        
        # Modelo de pricing recomendado
        precio_base = segmento.precio_promedio_anual or self._estimar_precio(segmento)
        
        if segmento.firmograficos.tamano == TamanoEmpresa.STARTUP:
            pricing["modelo_pricing_recomendado"] = "Usage-based o Seat-based"
            pricing["estructura_precios"] = {
                "starter": precio_base * 0.5,
                "growth": precio_base,
                "scale": precio_base * 2
            }
        elif segmento.firmograficos.tamano == TamanoEmpresa.MEDIANA:
            pricing["modelo_pricing_recomendado"] = "Tiered Pricing"
            pricing["estructura_precios"] = {
                "professional": precio_base * 0.8,
                "business": precio_base,
                "enterprise": precio_base * 1.5
            }
        else:
            pricing["modelo_pricing_recomendado"] = "Custom Enterprise Pricing"
            pricing["estructura_precios"] = {
                "base": precio_base,
                "custom": "Negociación basada en volumen y features"
            }
        
        # Optimizaciones
        unidad_economica = self.calcular_unidad_economica(segmento.id)
        ratio_actual = unidad_economica.get("ratio_ltv_cac", 0)
        
        if ratio_actual < 5:
            pricing["optimizaciones"].append("Aumentar precio para mejorar ratio LTV:CAC")
        
        if segmento.comportamentales.urgencia_problema == UrgenciaProblema.CRITICA:
            pricing["optimizaciones"].append("Premium pricing justificado por valor crítico")
        
        # Estrategias de descuento
        pricing["estrategias_descuento"] = [
            "Descuento por pago anual (15-20%)",
            "Descuento para early adopters (30-50%)",
            "Descuento por volumen",
            "Descuento para startups (programa especial)"
        ]
        
        # Recomendaciones
        pricing["recomendaciones"] = [
            f"Implementar {pricing['modelo_pricing_recomendado']}",
            "A/B testing de precios",
            "Monitorear elasticidad de precio",
            "Optimizar basado en datos de conversión"
        ]
        
        return pricing
    
    def generar_matriz_priorizacion_visual(self) -> str:
        """Genera matriz visual de priorización mejorada"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        matriz = matriz_priorizacion = self.matriz_priorizacion_mejorada()
        
        visual = "\n" + "="*100 + "\n"
        visual += "MATRIZ DE PRIORIZACIÓN VISUAL\n"
        visual += "="*100 + "\n\n"
        
        visual += "🔥 ALTA PRIORIDAD (Score >= 8.0):\n"
        visual += "-"*100 + "\n"
        for seg in matriz["alta_prioridad"]:
            visual += f"  ⭐ {seg['nombre']:<50} Score: {seg['score_prioridad']:>6.2f}\n"
            visual += f"     Atractivo: {seg['score_atractivo']:.2f} | Oportunidad: {seg['score_oportunidad']:.2f} | Riesgo: {seg['score_riesgo']:.2f}\n"
        
        visual += "\n⭐ MEDIA-ALTA PRIORIDAD (Score 7.0-7.9):\n"
        visual += "-"*100 + "\n"
        for seg in matriz["media_alta_prioridad"][:5]:
            visual += f"  • {seg['nombre']:<50} Score: {seg['score_prioridad']:>6.2f}\n"
        
        visual += "\n📊 MEDIA PRIORIDAD (Score 6.0-6.9):\n"
        visual += "-"*100 + "\n"
        for seg in matriz["media_prioridad"][:5]:
            visual += f"  • {seg['nombre']:<50} Score: {seg['score_prioridad']:>6.2f}\n"
        
        visual += "\n📉 BAJA PRIORIDAD (Score < 6.0):\n"
        visual += "-"*100 + "\n"
        for seg in matriz["baja_prioridad"][:5]:
            visual += f"  • {seg['nombre']:<50} Score: {seg['score_prioridad']:>6.2f}\n"
        
        visual += "\n" + "="*100 + "\n"
        
        return visual
    
    def analisis_benchmarking_competitivo(self) -> Dict:
        """Análisis de benchmarking competitivo entre segmentos"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        benchmarking = {
            "mejores_practicas_por_categoria": {},
            "benchmarks_metricas": {},
            "recomendaciones_benchmarking": []
        }
        
        # Mejores prácticas por categoría
        mejor_score = max(self.segmentos, key=lambda s: s.calcular_score_segmento())
        mejor_oportunidad = max(self.segmentos, key=lambda s: s.scoring.calcular_score_oportunidad())
        menor_riesgo = min(self.segmentos, key=lambda s: s.scoring.calcular_score_riesgo())
        
        benchmarking["mejores_practicas_por_categoria"] = {
            "mejor_score_total": {
                "segmento": mejor_score.nombre,
                "score": mejor_score.calcular_score_segmento(),
                "caracteristicas": [
                    f"Industria: {mejor_score.firmograficos.industria.value}",
                    f"Geografía: {mejor_score.firmograficos.geografia.value}",
                    f"Tamaño: {mejor_score.firmograficos.tamano.value}"
                ]
            },
            "mejor_oportunidad": {
                "segmento": mejor_oportunidad.nombre,
                "oportunidad": mejor_oportunidad.scoring.calcular_score_oportunidad(),
                "caracteristicas": [
                    f"Crecimiento: {mejor_oportunidad.scoring.crecimiento}/10",
                    f"Ajuste producto: {mejor_oportunidad.scoring.ajuste_producto}/10"
                ]
            },
            "menor_riesgo": {
                "segmento": menor_riesgo.nombre,
                "riesgo": menor_riesgo.scoring.calcular_score_riesgo(),
                "caracteristicas": [
                    f"Competencia: {menor_riesgo.scoring.competencia}/10",
                    f"Accesibilidad: {menor_riesgo.scoring.accesibilidad}/10"
                ]
            }
        }
        
        # Benchmarks de métricas
        unidades_economicas = []
        for seg in self.segmentos:
            unidad = self.calcular_unidad_economica(seg.id)
            unidades_economicas.append({
                "segmento": seg.nombre,
                "cac": unidad.get("cac", 0),
                "ltv": unidad.get("ltv", 0),
                "ratio": unidad.get("ratio_ltv_cac", 0)
            })
        
        if unidades_economicas:
            mejor_ratio = max(unidades_economicas, key=lambda x: x["ratio"])
            benchmarking["benchmarks_metricas"] = {
                "mejor_ratio_ltv_cac": {
                    "segmento": mejor_ratio["segmento"],
                    "ratio": mejor_ratio["ratio"],
                    "cac": mejor_ratio["cac"],
                    "ltv": mejor_ratio["ltv"]
                },
                "promedio_ratio": sum(u["ratio"] for u in unidades_economicas) / len(unidades_economicas),
                "promedio_cac": sum(u["cac"] for u in unidades_economicas) / len(unidades_economicas),
                "promedio_ltv": sum(u["ltv"] for u in unidades_economicas) / len(unidades_economicas)
            }
        
        # Recomendaciones de benchmarking
        benchmarking["recomendaciones_benchmarking"] = [
            f"Aplicar características de {mejor_score.nombre} a otros segmentos",
            f"Replicar estrategia de {mejor_oportunidad.nombre} para maximizar oportunidad",
            f"Mitigar riesgos usando enfoque de {menor_riesgo.nombre}"
        ]
        
        return benchmarking
    
    def analisis_roadmap_estrategico(self) -> Dict:
        """Genera roadmap estratégico completo basado en análisis"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        roadmap = {
            "vision_3anos": "",
            "objetivos_por_ano": {},
            "hitos_clave": [],
            "recursos_necesarios": {},
            "riesgos_estrategicos": []
        }
        
        # Visión a 3 años
        mercado_total = self.analisis_mercado_total()
        roadmap["vision_3anos"] = f"Liderar en segmentos prioritarios alcanzando ${mercado_total['som_total'] * 3:,.0f}M en ingresos potenciales en 3 años"
        
        # Objetivos por año
        roadmap["objetivos_por_ano"] = {
            "ano_1": {
                "objetivo_principal": "Validar y escalar en segmento primario",
                "metricas": {
                    "ingresos_objetivo": "$5M ARR",
                    "clientes_objetivo": 200,
                    "penetracion_objetivo": "15%"
                },
                "iniciativas": [
                    "Lanzar en segmento primario",
                    "Desarrollar casos de estudio",
                    "Optimizar unidad económica"
                ]
            },
            "ano_2": {
                "objetivo_principal": "Expandir a segmento secundario y optimizar",
                "metricas": {
                    "ingresos_objetivo": "$15M ARR",
                    "clientes_objetivo": 500,
                    "penetracion_objetivo": "20%"
                },
                "iniciativas": [
                    "Expandir a segmento secundario",
                    "Desarrollar partnerships",
                    "Optimizar operaciones"
                ]
            },
            "ano_3": {
                "objetivo_principal": "Consolidar posición y explorar nuevos segmentos",
                "metricas": {
                    "ingresos_objetivo": "$30M ARR",
                    "clientes_objetivo": 1000,
                    "penetracion_objetivo": "25%"
                },
                "iniciativas": [
                    "Consolidar posición de mercado",
                    "Explorar nuevos segmentos",
                    "Desarrollar ecosistema"
                ]
            }
        }
        
        # Hitos clave
        roadmap["hitos_clave"] = [
            "Mes 3: Primeros 10 clientes en segmento primario",
            "Mes 6: $1M ARR alcanzado",
            "Mes 12: Expansión a segmento secundario",
            "Mes 18: $5M ARR alcanzado",
            "Mes 24: Posición de mercado establecida",
            "Mes 36: $15M+ ARR y evaluación de nuevos segmentos"
        ]
        
        # Recursos necesarios
        inversion_total = self.analisis_inversion_recomendada()
        roadmap["recursos_necesarios"] = {
            "inversion_total_3anos": inversion_total.get("inversion_total_recomendada", 0) * 3,
            "equipo_ano_1": "10-15 personas",
            "equipo_ano_2": "25-35 personas",
            "equipo_ano_3": "50-70 personas",
            "presupuesto_marketing_anual": "$500K - $2M"
        }
        
        # Riesgos estratégicos
        roadmap["riesgos_estrategicos"] = [
            {
                "riesgo": "Competencia intensa en segmentos prioritarios",
                "probabilidad": "Media",
                "impacto": "Alto",
                "mitigacion": "Diferenciación clara y construcción de ventajas competitivas"
            },
            {
                "riesgo": "Cambios en mercado o regulación",
                "probabilidad": "Baja",
                "impacto": "Alto",
                "mitigacion": "Diversificación de segmentos y monitoreo continuo"
            },
            {
                "riesgo": "Escalamiento de operaciones",
                "probabilidad": "Media",
                "impacto": "Medio",
                "mitigacion": "Inversión en procesos y tecnología desde inicio"
            }
        ]
        
        return roadmap
    
    def analisis_metricas_operacionales(self) -> Dict:
        """Análisis de métricas operacionales por segmento"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        metricas = {
            "por_segmento": {},
            "agregadas": {},
            "recomendaciones": []
        }
        
        for seg in self.segmentos:
            unidad_economica = self.calcular_unidad_economica(seg.id)
            ciclo_vida = self.analisis_ciclo_vida_cliente(seg.id)
            
            metricas["por_segmento"][seg.nombre] = {
                "cac": unidad_economica.get("cac", 0),
                "ltv": unidad_economica.get("ltv", 0),
                "ratio_ltv_cac": unidad_economica.get("ratio_ltv_cac", 0),
                "payback_meses": unidad_economica.get("payback_meses", 0),
                "vida_media_cliente": ciclo_vida.get("vida_media_cliente_anos", 0),
                "tasa_retencion": ciclo_vida.get("tasa_retencion", 0),
                "ciclo_venta_dias": seg.ciclo_venta_dias or 90,
                "tasa_conversion": seg.tasa_conversion_esperada or 10.0
            }
        
        # Métricas agregadas
        todos_cac = [m["cac"] for m in metricas["por_segmento"].values()]
        todos_ltv = [m["ltv"] for m in metricas["por_segmento"].values()]
        todos_ratios = [m["ratio_ltv_cac"] for m in metricas["por_segmento"].values()]
        
        metricas["agregadas"] = {
            "cac_promedio": sum(todos_cac) / len(todos_cac) if todos_cac else 0,
            "ltv_promedio": sum(todos_ltv) / len(todos_ltv) if todos_ltv else 0,
            "ratio_promedio": sum(todos_ratios) / len(todos_ratios) if todos_ratios else 0,
            "mejor_segmento_ratio": max(metricas["por_segmento"].items(), key=lambda x: x[1]["ratio_ltv_cac"])[0] if metricas["por_segmento"] else None
        }
        
        # Recomendaciones
        if metricas["agregadas"]["ratio_promedio"] < 5:
            metricas["recomendaciones"].append("Ratio promedio bajo - optimizar unidad económica")
        
        mejor_seg = max(metricas["por_segmento"].items(), key=lambda x: x[1]["ratio_ltv_cac"])
        metricas["recomendaciones"].append(f"Replicar modelo de {mejor_seg[0]} en otros segmentos")
        
        return metricas
    
    def generar_resumen_ejecutivo_completo(self) -> str:
        """Genera resumen ejecutivo completo y detallado"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        resumen = []
        resumen.append("=" * 100)
        resumen.append("RESUMEN EJECUTIVO COMPLETO - ANÁLISIS DE SEGMENTACIÓN")
        resumen.append("=" * 100)
        resumen.append(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        resumen.append(f"Total Segmentos Analizados: {len(self.segmentos)}\n")
        
        # Segmentos prioritarios
        resumen.append("\n" + "-" * 100)
        resumen.append("SEGMENTOS PRIORITARIOS")
        resumen.append("-" * 100)
        
        if self.segmento_primario:
            unidad_primario = self.calcular_unidad_economica(self.segmento_primario.id)
            resumen.append(f"\n🎯 SEGMENTO PRIMARIO: {self.segmento_primario.nombre}")
            resumen.append(f"   Score Total: {self.segmento_primario.calcular_score_segmento():.2f}/10")
            resumen.append(f"   CAC: ${unidad_primario.get('cac', 0):,.0f}")
            resumen.append(f"   LTV: ${unidad_primario.get('ltv', 0):,.0f}")
            resumen.append(f"   Ratio LTV:CAC: {unidad_primario.get('ratio_ltv_cac', 0):.2f}")
        
        if self.segmento_secundario:
            unidad_secundario = self.calcular_unidad_economica(self.segmento_secundario.id)
            resumen.append(f"\n📊 SEGMENTO SECUNDARIO: {self.segmento_secundario.nombre}")
            resumen.append(f"   Score Total: {self.segmento_secundario.calcular_score_segmento():.2f}/10")
            resumen.append(f"   CAC: ${unidad_secundario.get('cac', 0):,.0f}")
            resumen.append(f"   LTV: ${unidad_secundario.get('ltv', 0):,.0f}")
        
        # Mercado total
        mercado_total = self.analisis_mercado_total()
        resumen.append("\n" + "-" * 100)
        resumen.append("OPORTUNIDAD DE MERCADO")
        resumen.append("-" * 100)
        resumen.append(f"\nTAM Total: ${mercado_total['tam_total']:,.0f}M")
        resumen.append(f"SAM Total: ${mercado_total['sam_total']:,.0f}M")
        resumen.append(f"SOM Total: ${mercado_total['som_total']:,.0f}M")
        resumen.append(f"Oportunidad de Crecimiento: ${mercado_total['oportunidad_crecimiento']:,.0f}M")
        
        # Inversión recomendada
        inversion = self.analisis_inversion_recomendada()
        resumen.append("\n" + "-" * 100)
        resumen.append("INVERSIÓN RECOMENDADA")
        resumen.append("-" * 100)
        resumen.append(f"\nInversión Total: ${inversion['inversion_total_recomendada']:,.0f}")
        resumen.append("\nTop 3 Inversiones:")
        for i, inv in enumerate(inversion["top_3_inversiones"], 1):
            resumen.append(f"   {i}. {inv['segmento']}: ROI {inv['roi_esperado_3anos']:.1f}%")
        
        # Roadmap estratégico
        roadmap = self.analisis_roadmap_estrategico()
        resumen.append("\n" + "-" * 100)
        resumen.append("ROADMAP ESTRATÉGICO")
        resumen.append("-" * 100)
        resumen.append(f"\nVisión 3 Años: {roadmap['vision_3anos']}")
        resumen.append("\nObjetivos Año 1:")
        resumen.append(f"   {roadmap['objetivos_por_ano']['ano_1']['objetivo_principal']}")
        resumen.append(f"   Ingresos Objetivo: {roadmap['objetivos_por_ano']['ano_1']['metricas']['ingresos_objetivo']}")
        
        # Recomendaciones clave
        resumen.append("\n" + "-" * 100)
        resumen.append("RECOMENDACIONES CLAVE")
        resumen.append("-" * 100)
        resumen.append("\n1. Enfoque inmediato en segmento primario para validación rápida")
        resumen.append("2. Desarrollo paralelo del segmento secundario")
        resumen.append("3. Optimización continua de unidad económica")
        resumen.append("4. Construcción de ventajas competitivas sostenibles")
        
        return "\n".join(resumen)
    
    def analisis_escenarios_mercado(self) -> Dict:
        """Análisis de escenarios de mercado (optimista, base, pesimista)"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        escenarios = {
            "escenario_base": {},
            "escenario_optimista": {},
            "escenario_pesimista": {},
            "probabilidades": {},
            "recomendaciones": []
        }
        
        mercado_total = self.analisis_mercado_total()
        inversion_total = self.analisis_inversion_recomendada()
        
        # Escenario Base
        escenarios["escenario_base"] = {
            "descripcion": "Crecimiento esperado según tendencias actuales",
            "som_3anos": mercado_total['som_total'] * 1.5,
            "penetracion_objetivo": 20,
            "ingresos_proyectados_3anos": mercado_total['som_total'] * 0.2 * 3,
            "clientes_objetivo": 500,
            "probabilidad": 60
        }
        
        # Escenario Optimista
        escenarios["escenario_optimista"] = {
            "descripcion": "Crecimiento acelerado con adopción rápida",
            "som_3anos": mercado_total['som_total'] * 2.5,
            "penetracion_objetivo": 35,
            "ingresos_proyectados_3anos": mercado_total['som_total'] * 0.35 * 3,
            "clientes_objetivo": 1000,
            "probabilidad": 20
        }
        
        # Escenario Pesimista
        escenarios["escenario_pesimista"] = {
            "descripcion": "Crecimiento lento con barreras de adopción",
            "som_3anos": mercado_total['som_total'] * 0.8,
            "penetracion_objetivo": 10,
            "ingresos_proyectados_3anos": mercado_total['som_total'] * 0.1 * 3,
            "clientes_objetivo": 200,
            "probabilidad": 20
        }
        
        # Probabilidades
        escenarios["probabilidades"] = {
            "escenario_base": 60,
            "escenario_optimista": 20,
            "escenario_pesimista": 20
        }
        
        # Recomendaciones
        escenarios["recomendaciones"] = [
            "Preparar estrategia flexible para adaptarse a diferentes escenarios",
            "Inversión inicial conservadora con capacidad de escalamiento rápido",
            "Monitoreo continuo de métricas clave para detectar cambios temprano"
        ]
        
        return escenarios
    
    def analisis_propuesta_valor_por_segmento(self, segmento_id: str) -> Dict:
        """Análisis detallado de propuesta de valor por segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {}
        
        propuesta_valor = {
            "segmento": segmento.nombre,
            "problema_principal": "",
            "solucion_propuesta": "",
            "beneficios_clave": [],
            "diferenciadores": [],
            "evidencia_valor": [],
            "mensaje_clave": ""
        }
        
        # Problema principal según características del segmento
        if segmento.comportamentales.urgencia_problema == UrgenciaProblema.ALTA:
            propuesta_valor["problema_principal"] = "Necesidad crítica inmediata que requiere solución rápida"
        else:
            propuesta_valor["problema_principal"] = "Oportunidad de mejora estratégica a largo plazo"
        
        # Solución propuesta
        propuesta_valor["solucion_propuesta"] = f"Solución adaptada para {segmento.firmograficos.industria.value} con enfoque en {segmento.comportamentales.nivel_adopcion_tecnologica.value}"
        
        # Beneficios clave
        beneficios = []
        if segmento.psicograficos.apetito_innovacion == ApetitoInnovacion.ALTO:
            beneficios.append("Innovación de vanguardia que genera ventaja competitiva")
        if segmento.firmograficos.madurez_digital == MadurezDigital.AVANZADA:
            beneficios.append("Integración seamless con infraestructura existente")
        if segmento.scoring.crecimiento >= 8:
            beneficios.append("Escalamiento rápido con potencial de crecimiento")
        
        propuesta_valor["beneficios_clave"] = beneficios if beneficios else ["Mejora operacional", "ROI medible", "Soporte especializado"]
        
        # Diferenciadores
        propuesta_valor["diferenciadores"] = [
            f"Especialización en {segmento.firmograficos.industria.value}",
            f"Modelo adaptado a {segmento.firmograficos.geografia.value}",
            "Soporte y onboarding personalizado"
        ]
        
        # Evidencia de valor
        unidad_economica = self.calcular_unidad_economica(segmento_id)
        propuesta_valor["evidencia_valor"] = [
            f"ROI esperado: {unidad_economica.get('ratio_ltv_cac', 0):.1f}x en 3 años",
            f"Payback period: {unidad_economica.get('payback_meses', 0)} meses",
            f"Margen de contribución: {unidad_economica.get('margen_contribucion', 0):.1f}%"
        ]
        
        # Mensaje clave
        propuesta_valor["mensaje_clave"] = f"La solución ideal para {segmento.nombre} que resuelve {propuesta_valor['problema_principal'].lower()} con {', '.join(propuesta_valor['beneficios_clave'][:2])}"
        
        return propuesta_valor
    
    def analisis_barreras_adopcion(self, segmento_id: str) -> Dict:
        """Análisis de barreras de adopción por segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {}
        
        barreras = {
            "segmento": segmento.nombre,
            "barreras_identificadas": [],
            "nivel_riesgo": "",
            "estrategias_mitigacion": [],
            "tiempo_adopcion_estimado": ""
        }
        
        # Identificar barreras según características
        barreras_list = []
        
        if segmento.psicograficos.aversion_riesgo == AversionRiesgo.ALTA:
            barreras_list.append({
                "barrera": "Aversión al riesgo y cambio organizacional",
                "impacto": "Alto",
                "probabilidad": "Media"
            })
        
        if segmento.firmograficos.madurez_digital == MadurezDigital.BASICA:
            barreras_list.append({
                "barrera": "Falta de infraestructura tecnológica",
                "impacto": "Alto",
                "probabilidad": "Alta"
            })
        
        if segmento.scoring.competencia >= 7:
            barreras_list.append({
                "barrera": "Competencia establecida con lealtad de clientes",
                "impacto": "Medio",
                "probabilidad": "Alta"
            })
        
        if segmento.comportamentales.nivel_adopcion_tecnologica == NivelAdopcionTecnologica.BAJO:
            barreras_list.append({
                "barrera": "Resistencia al cambio y curva de aprendizaje",
                "impacto": "Medio",
                "probabilidad": "Media"
            })
        
        barreras["barreras_identificadas"] = barreras_list if barreras_list else [{
            "barrera": "Barreras estándar de adopción",
            "impacto": "Bajo",
            "probabilidad": "Baja"
        }]
        
        # Nivel de riesgo
        riesgo_alto = sum(1 for b in barreras["barreras_identificadas"] if b["impacto"] == "Alto")
        if riesgo_alto >= 2:
            barreras["nivel_riesgo"] = "Alto"
        elif riesgo_alto == 1:
            barreras["nivel_riesgo"] = "Medio"
        else:
            barreras["nivel_riesgo"] = "Bajo"
        
        # Estrategias de mitigación
        barreras["estrategias_mitigacion"] = [
            "Programa de pilotos y pruebas de concepto",
            "Casos de estudio y testimonials de referencia",
            "Onboarding y capacitación intensiva",
            "Soporte dedicado durante primeros 90 días",
            "Garantías y modelos de pago flexibles"
        ]
        
        # Tiempo de adopción estimado
        if barreras["nivel_riesgo"] == "Alto":
            barreras["tiempo_adopcion_estimado"] = "6-12 meses"
        elif barreras["nivel_riesgo"] == "Medio":
            barreras["tiempo_adopcion_estimado"] = "3-6 meses"
        else:
            barreras["tiempo_adopcion_estimado"] = "1-3 meses"
        
        return barreras
    
    def analisis_expansion_geografica(self) -> Dict:
        """Análisis de oportunidades de expansión geográfica"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        expansion = {
            "mercados_actuales": [],
            "mercados_oportunidad": [],
            "estrategia_expansion": {},
            "riesgos_expansion": []
        }
        
        # Mercados actuales (basado en segmentos existentes)
        geografias = set(s.firmograficos.geografia for s in self.segmentos)
        expansion["mercados_actuales"] = [g.value for g in geografias]
        
        # Mercados de oportunidad
        todas_geografias = [g.value for g in Geografia]
        expansion["mercados_oportunidad"] = [g for g in todas_geografias if g not in expansion["mercados_actuales"]]
        
        # Estrategia de expansión
        expansion["estrategia_expansion"] = {
            "fase_1": {
                "mercados": expansion["mercados_oportunidad"][:2] if expansion["mercados_oportunidad"] else [],
                "tiempo": "6-12 meses",
                "enfoque": "Validación con pilotos"
            },
            "fase_2": {
                "mercados": expansion["mercados_oportunidad"][2:4] if len(expansion["mercados_oportunidad"]) > 2 else [],
                "tiempo": "12-18 meses",
                "enfoque": "Escalamiento con partnerships"
            },
            "fase_3": {
                "mercados": expansion["mercados_oportunidad"][4:] if len(expansion["mercados_oportunidad"]) > 4 else [],
                "tiempo": "18-24 meses",
                "enfoque": "Expansión completa"
            }
        }
        
        # Riesgos de expansión
        expansion["riesgos_expansion"] = [
            {
                "riesgo": "Diferencias culturales y regulatorias",
                "mitigacion": "Análisis local profundo y adaptación de producto"
            },
            {
                "riesgo": "Competencia local establecida",
                "mitigacion": "Partnerships estratégicos y diferenciación clara"
            },
            {
                "riesgo": "Costos de entrada y operación",
                "mitigacion": "Modelo escalable y validación antes de inversión completa"
            }
        ]
        
        return expansion
    
    def analisis_upsell_crosssell_potencial(self, segmento_id: str) -> Dict:
        """Análisis de potencial de upsell y cross-sell por segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {}
        
        potencial = {
            "segmento": segmento.nombre,
            "potencial_upsell": {},
            "potencial_crosssell": {},
            "ingresos_adicionales_proyectados": {},
            "estrategias": []
        }
        
        unidad_economica = self.calcular_unidad_economica(segmento_id)
        ltv_base = unidad_economica.get("ltv", 0)
        
        # Potencial de Upsell
        tasa_upsell = 0.3 if segmento.psicograficos.apetito_innovacion == ApetitoInnovacion.ALTO else 0.15
        potencial["potencial_upsell"] = {
            "tasa_esperada": tasa_upsell * 100,
            "valor_promedio_upsell": ltv_base * 0.4,
            "ltv_incrementado": ltv_base * (1 + tasa_upsell * 0.4),
            "oportunidades": [
                "Upgrade a plan premium",
                "Aumento de usuarios/volumen",
                "Features avanzadas"
            ]
        }
        
        # Potencial de Cross-sell
        tasa_crosssell = 0.2 if segmento.comportamentales.nivel_adopcion_tecnologica == NivelAdopcionTecnologica.ALTO else 0.1
        potencial["potencial_crosssell"] = {
            "tasa_esperada": tasa_crosssell * 100,
            "valor_promedio_crosssell": ltv_base * 0.3,
            "productos_complementarios": [
                "Servicios de consultoría",
                "Productos relacionados",
                "Integraciones premium"
            ]
        }
        
        # Ingresos adicionales proyectados
        potencial["ingresos_adicionales_proyectados"] = {
            "por_cliente_anual": (potencial["potencial_upsell"]["valor_promedio_upsell"] * tasa_upsell) + 
                                 (potencial["potencial_crosssell"]["valor_promedio_crosssell"] * tasa_crosssell),
            "por_100_clientes": 0,
            "impacto_ltv": ((ltv_base * (1 + tasa_upsell * 0.4)) - ltv_base) / ltv_base * 100 if ltv_base > 0 else 0
        }
        potencial["ingresos_adicionales_proyectados"]["por_100_clientes"] = \
            potencial["ingresos_adicionales_proyectados"]["por_cliente_anual"] * 100
        
        # Estrategias
        potencial["estrategias"] = [
            "Programa de adopción de features avanzadas",
            "Incentivos para upgrades tempranos",
            "Bundles de productos complementarios",
            "Programa de referidos con beneficios"
        ]
        
        return potencial
    
    def analisis_viralidad_referidos(self, segmento_id: str) -> Dict:
        """Análisis de potencial de viralidad y referidos por segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {}
        
        viralidad = {
            "segmento": segmento.nombre,
            "potencial_viralidad": "",
            "tasa_referidos_esperada": 0,
            "k_factor": 0,
            "estrategias_viralidad": [],
            "programa_referidos": {}
        }
        
        # Potencial de viralidad según características
        if segmento.psicograficos.apetito_innovacion == ApetitoInnovacion.ALTO:
            viralidad["potencial_viralidad"] = "Alto"
            viralidad["tasa_referidos_esperada"] = 0.25
            viralidad["k_factor"] = 1.3
        elif segmento.comportamentales.nivel_adopcion_tecnologica == NivelAdopcionTecnologica.ALTO:
            viralidad["potencial_viralidad"] = "Medio-Alto"
            viralidad["tasa_referidos_esperada"] = 0.15
            viralidad["k_factor"] = 1.15
        else:
            viralidad["potencial_viralidad"] = "Medio"
            viralidad["tasa_referidos_esperada"] = 0.10
            viralidad["k_factor"] = 1.10
        
        # Estrategias de viralidad
        viralidad["estrategias_viralidad"] = [
            "Programa de referidos con incentivos",
            "Casos de éxito compartibles",
            "Integraciones que exponen la marca",
            "Contenido viral y educacional",
            "Comunidad de usuarios activa"
        ]
        
        # Programa de referidos
        unidad_economica = self.calcular_unidad_economica(segmento_id)
        cac = unidad_economica.get("cac", 0)
        
        viralidad["programa_referidos"] = {
            "incentivo_referidor": cac * 0.2,
            "incentivo_referido": cac * 0.15,
            "cac_efectivo_con_referidos": cac * (1 - viralidad["tasa_referidos_esperada"]),
            "ahorro_cac": cac * viralidad["tasa_referidos_esperada"]
        }
        
        return viralidad
    
    def analisis_defensibilidad_competitiva(self, segmento_id: str) -> Dict:
        """Análisis de defensibilidad competitiva por segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {}
        
        defensibilidad = {
            "segmento": segmento.nombre,
            "score_defensibilidad": 0,
            "ventajas_competitivas": [],
            "barreras_entrada": [],
            "riesgos_competitivos": [],
            "estrategias_fortalecimiento": []
        }
        
        # Calcular score de defensibilidad
        score = 5.0  # Base
        
        # Factores positivos
        if segmento.scoring.ajuste_producto >= 8:
            score += 1.5
        if segmento.analisis_competencia.barreras_entrada >= 7:
            score += 1.0
        if segmento.psicograficos.apetito_innovacion == ApetitoInnovacion.ALTO:
            score += 0.5
        
        # Factores negativos
        if segmento.scoring.competencia >= 7:
            score -= 1.0
        if segmento.analisis_competencia.intensidad_competencia >= 7:
            score -= 0.5
        
        defensibilidad["score_defensibilidad"] = max(0, min(10, score))
        
        # Ventajas competitivas
        defensibilidad["ventajas_competitivas"] = [
            f"Especialización en {segmento.firmograficos.industria.value}",
            f"Modelo optimizado para {segmento.firmograficos.geografia.value}",
            "Red de clientes y casos de estudio",
            "Know-how y expertise acumulado"
        ]
        
        # Barreras de entrada
        defensibilidad["barreras_entrada"] = [
            "Costo de cambio para clientes",
            "Integraciones y datos históricos",
            "Relaciones y confianza establecida",
            "Efectos de red"
        ]
        
        # Riesgos competitivos
        defensibilidad["riesgos_competitivos"] = [
            "Entrada de grandes competidores",
            "Disrupción tecnológica",
            "Cambios regulatorios",
            "Commoditización del producto"
        ]
        
        # Estrategias de fortalecimiento
        defensibilidad["estrategias_fortalecimiento"] = [
            "Construir efectos de red y ecosistema",
            "Profundizar integraciones técnicas",
            "Desarrollar IP y diferenciación",
            "Crear switching costs altos"
        ]
        
        return defensibilidad
    
    def analisis_timing_mercado(self, segmento_id: str) -> Dict:
        """Análisis de timing de mercado por segmento"""
        
        segmento = next((s for s in self.segmentos if s.id == segmento_id), None)
        if not segmento:
            return {}
        
        timing = {
            "segmento": segmento.nombre,
            "momento_mercado": "",
            "madurez_mercado": "",
            "ventana_oportunidad": "",
            "recomendacion_timing": "",
            "factores_timing": []
        }
        
        # Evaluar momento del mercado
        crecimiento = segmento.scoring.crecimiento
        competencia = segmento.scoring.competencia
        urgencia = segmento.comportamentales.urgencia_problema
        
        if crecimiento >= 8 and competencia <= 5:
            timing["momento_mercado"] = "Óptimo - Mercado en crecimiento con baja competencia"
            timing["madurez_mercado"] = "Emergente"
            timing["ventana_oportunidad"] = "12-24 meses"
        elif crecimiento >= 7 and competencia <= 6:
            timing["momento_mercado"] = "Bueno - Oportunidad clara con competencia moderada"
            timing["madurez_mercado"] = "En desarrollo"
            timing["ventana_oportunidad"] = "6-18 meses"
        elif crecimiento >= 6:
            timing["momento_mercado"] = "Moderado - Mercado establecido con competencia"
            timing["madurez_mercado"] = "Maduro"
            timing["ventana_oportunidad"] = "3-12 meses"
        else:
            timing["momento_mercado"] = "Desafiante - Mercado lento o saturado"
            timing["madurez_mercado"] = "Maduro/Saturado"
            timing["ventana_oportunidad"] = "Inmediata"
        
        # Recomendación de timing
        if timing["momento_mercado"].startswith("Óptimo") or timing["momento_mercado"].startswith("Bueno"):
            timing["recomendacion_timing"] = "Entrada inmediata recomendada"
        else:
            timing["recomendacion_timing"] = "Entrada con diferenciación fuerte requerida"
        
        # Factores de timing
        timing["factores_timing"] = [
            f"Crecimiento del mercado: {crecimiento}/10",
            f"Nivel de competencia: {competencia}/10",
            f"Urgencia del problema: {urgencia.value}",
            f"Madurez digital: {segmento.firmograficos.madurez_digital.value}"
        ]
        
        return timing
    
    def analisis_recursos_por_fase(self) -> Dict:
        """Análisis detallado de recursos necesarios por fase"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        recursos = {
            "fase_validacion": {},
            "fase_crecimiento": {},
            "fase_escala": {},
            "total_3anos": {}
        }
        
        inversion_total = self.analisis_inversion_recomendada()
        inversion_base = inversion_total.get("inversion_total_recomendada", 0)
        
        # Fase de Validación (0-6 meses)
        recursos["fase_validacion"] = {
            "duracion": "0-6 meses",
            "objetivo": "Validar producto-mercado fit",
            "equipo": {
                "ventas": 2,
                "marketing": 1,
                "producto": 2,
                "soporte": 1,
                "total": 6
            },
            "presupuesto": {
                "marketing": inversion_base * 0.15,
                "ventas": inversion_base * 0.20,
                "producto": inversion_base * 0.10,
                "operaciones": inversion_base * 0.05,
                "total": inversion_base * 0.50
            },
            "metricas_objetivo": {
                "clientes": 10,
                "ingresos_mrr": 50000,
                "tasa_conversion": 5
            }
        }
        
        # Fase de Crecimiento (6-18 meses)
        recursos["fase_crecimiento"] = {
            "duracion": "6-18 meses",
            "objetivo": "Escalar operaciones y optimizar",
            "equipo": {
                "ventas": 5,
                "marketing": 3,
                "producto": 4,
                "soporte": 3,
                "total": 15
            },
            "presupuesto": {
                "marketing": inversion_base * 0.25,
                "ventas": inversion_base * 0.30,
                "producto": inversion_base * 0.15,
                "operaciones": inversion_base * 0.10,
                "total": inversion_base * 0.80
            },
            "metricas_objetivo": {
                "clientes": 200,
                "ingresos_mrr": 500000,
                "tasa_conversion": 10
            }
        }
        
        # Fase de Escala (18-36 meses)
        recursos["fase_escala"] = {
            "duracion": "18-36 meses",
            "objetivo": "Escalamiento masivo y optimización",
            "equipo": {
                "ventas": 10,
                "marketing": 5,
                "producto": 6,
                "soporte": 5,
                "total": 26
            },
            "presupuesto": {
                "marketing": inversion_base * 0.30,
                "ventas": inversion_base * 0.35,
                "producto": inversion_base * 0.20,
                "operaciones": inversion_base * 0.15,
                "total": inversion_base * 1.0
            },
            "metricas_objetivo": {
                "clientes": 1000,
                "ingresos_mrr": 2500000,
                "tasa_conversion": 15
            }
        }
        
        # Total 3 años
        recursos["total_3anos"] = {
            "equipo_total": recursos["fase_validacion"]["equipo"]["total"] + \
                           recursos["fase_crecimiento"]["equipo"]["total"] + \
                           recursos["fase_escala"]["equipo"]["total"],
            "presupuesto_total": recursos["fase_validacion"]["presupuesto"]["total"] + \
                                recursos["fase_crecimiento"]["presupuesto"]["total"] + \
                                recursos["fase_escala"]["presupuesto"]["total"]
        }
        
        return recursos
    
    def exportar_analisis(self, formato: str = "json") -> str:
        """Exporta el análisis completo en formato JSON o CSV"""
        
        if not self.analisis_realizado:
            self.analizar_segmentos()
        
        justificacion = self.generar_justificacion_estrategica()
        analisis = self.analizar_segmentos()
        
        resultado_completo = {
            "fecha_analisis": datetime.now().isoformat(),
            "total_segmentos": len(self.segmentos),
            "analisis_segmentos": analisis,
            "justificacion_estrategica": justificacion,
            "matriz_riesgo_oportunidad": self.generar_matriz_riesgo_oportunidad(),
            "canales_distribucion": self.analizar_canales_distribucion(),
            "recomendaciones_pricing": self.recomendar_pricing_por_segmento(),
            "tendencias_mercado": self.analizar_tendencias_mercado(),
            "dashboard_ejecutivo": self.generar_dashboard_ejecutivo(),
            "analisis_predictivo": self.analisis_predictivo_crecimiento(),
            "matriz_bcg": self.matriz_bcg_adaptada(),
            "analisis_sinergias": self.analisis_sinergias_segmentos(),
            "plan_accion": self.generar_plan_accion_ejecutable(),
            "analisis_cohortes": self.analisis_cohortes_segmentos(),
            "recomendaciones_partnerships": self.recomendar_partnerships(),
            "analisis_mercado_total": self.analisis_mercado_total(),
            "matriz_priorizacion_mejorada": self.matriz_priorizacion_mejorada(),
            "analisis_inversion_recomendada": self.analisis_inversion_recomendada(),
            "analisis_riesgo_financiero": self.analisis_riesgo_financiero(),
            "analisis_competencia_comparativa": self.analisis_competencia_comparativa(),
            "analisis_tendencias_temporales": self.analisis_tendencias_temporales(),
            "analisis_benchmarking_competitivo": self.analisis_benchmarking_competitivo(),
            "roadmap_estrategico": self.analisis_roadmap_estrategico(),
            "metricas_operacionales": self.analisis_metricas_operacionales(),
            "escenarios_mercado": self.analisis_escenarios_mercado(),
            "expansion_geografica": self.analisis_expansion_geografica(),
            "recursos_por_fase": self.analisis_recursos_por_fase(),
            "reporte_ejecutivo": self.generar_reporte_ejecutivo(),
            "resumen_ejecutivo_completo": self.generar_resumen_ejecutivo_completo(),
            "matriz_visual": self.generar_matriz_visual(),
            "matriz_priorizacion_visual": self.generar_matriz_priorizacion_visual()
        }
        
        # Agregar análisis específicos para segmentos principales si existen
        if self.segmento_primario:
            resultado_completo["analisis_segmento_primario"] = {
                "customer_journey": self.analisis_customer_journey(self.segmento_primario.id),
                "estrategia_producto": self.estrategia_producto_por_segmento(self.segmento_primario.id),
                "fit_canal": self.analisis_fit_canal(self.segmento_primario.id),
                "contenido_messaging": self.analisis_contenido_messaging(self.segmento_primario.id),
                "propuesta_valor": self.analisis_propuesta_valor_por_segmento(self.segmento_primario.id),
                "barreras_adopcion": self.analisis_barreras_adopcion(self.segmento_primario.id),
                "upsell_crosssell": self.analisis_upsell_crosssell_potencial(self.segmento_primario.id),
                "viralidad_referidos": self.analisis_viralidad_referidos(self.segmento_primario.id),
                "defensibilidad_competitiva": self.analisis_defensibilidad_competitiva(self.segmento_primario.id),
                "timing_mercado": self.analisis_timing_mercado(self.segmento_primario.id)
            }
        
        if self.segmento_secundario:
            resultado_completo["analisis_segmento_secundario"] = {
                "customer_journey": self.analisis_customer_journey(self.segmento_secundario.id),
                "estrategia_producto": self.estrategia_producto_por_segmento(self.segmento_secundario.id),
                "fit_canal": self.analisis_fit_canal(self.segmento_secundario.id),
                "contenido_messaging": self.analisis_contenido_messaging(self.segmento_secundario.id),
                "propuesta_valor": self.analisis_propuesta_valor_por_segmento(self.segmento_secundario.id),
                "barreras_adopcion": self.analisis_barreras_adopcion(self.segmento_secundario.id),
                "upsell_crosssell": self.analisis_upsell_crosssell_potencial(self.segmento_secundario.id),
                "viralidad_referidos": self.analisis_viralidad_referidos(self.segmento_secundario.id),
                "defensibilidad_competitiva": self.analisis_defensibilidad_competitiva(self.segmento_secundario.id),
                "timing_mercado": self.analisis_timing_mercado(self.segmento_secundario.id)
            }
        
        if formato == "json":
            return json.dumps(resultado_completo, indent=2, ensure_ascii=False)
        elif formato == "csv":
            # Crear datos para CSV
            datos = []
            for seg in self.segmentos:
                datos.append({
                    "ID": seg.id,
                    "Nombre": seg.nombre,
                    "Industria": seg.firmograficos.industria.value,
                    "Tamaño": seg.firmograficos.tamano.value,
                    "Geografía": seg.firmograficos.geografia.value,
                    "Madurez Digital": seg.firmograficos.madurez_digital.value,
                    "Adopción Tecnológica": seg.comportamentales.adopcion_tecnologica.value,
                    "Urgencia Problema": seg.comportamentales.urgencia_problema.value,
                    "Apetito Innovación": seg.psicograficos.apetito_innovacion.value,
                    "Aversión Riesgo": seg.psicograficos.aversion_riesgo.value,
                    "Score Tamaño": seg.scoring.tamano,
                    "Score Crecimiento": seg.scoring.crecimiento,
                    "Score Accesibilidad": seg.scoring.accesibilidad,
                    "Score Competencia": seg.scoring.competencia,
                    "Score Ajuste Producto": seg.scoring.ajuste_producto,
                    "Score Total": seg.calcular_score_segmento()
                })
            
            # Usar pandas si está disponible, sino usar csv estándar
            if PANDAS_AVAILABLE:
                df = pd.DataFrame(datos)
                return df.to_csv(index=False)
            else:
                # Generar CSV manualmente
                if not datos:
                    return ""
                
                output = StringIO()
                fieldnames = list(datos[0].keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(datos)
                return output.getvalue()
        else:
            return str(resultado_completo)


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal para ejecutar el análisis de segmentación"""
    
    print("\n" + "="*100)
    print("MATRIZ DE SEGMENTACIÓN AVANZADA - SISTEMA MULTI-CRITERIO")
    print("="*100 + "\n")
    
    # Crear instancia de la matriz
    matriz = MatrizSegmentacionAvanzada()
    
    # Crear segmentos base
    print("📊 Creando segmentos de mercado...")
    segmentos = matriz.crear_segmentos_base()
    print(f"✓ {len(segmentos)} segmentos creados\n")
    
    # Analizar segmentos
    print("🔍 Analizando segmentos...")
    analisis = matriz.analizar_segmentos()
    print("✓ Análisis completado\n")
    
    # Generar matriz visual
    print(matriz.generar_matriz_visual())
    
    # Generar justificación estratégica
    print("\n" + "="*100)
    print("JUSTIFICACIÓN ESTRATÉGICA - SEGMENTOS PRIMARIO Y SECUNDARIO")
    print("="*100 + "\n")
    
    justificacion = matriz.generar_justificacion_estrategica()
    
    # Mostrar justificación del segmento primario
    primario_info = justificacion["segmento_primario"]
    print(f"\n🎯 SEGMENTO PRIMARIO: {primario_info['segmento']}")
    print(f"   Score Total: {primario_info['score_total']:.2f}/10\n")
    
    print("📋 Razones Estratégicas:")
    for razon in primario_info["justificacion"]["razones_estrategicas"]:
        print(f"   • {razon}")
    
    print("\n💡 Ventajas Competitivas:")
    for ventaja in primario_info["justificacion"]["ventajas_competitivas"]:
        print(f"   • {ventaja}")
    
    print("\n🚀 Estrategia Recomendada:")
    for estrategia in primario_info["justificacion"]["estrategia_recomendada"]:
        print(f"   • {estrategia}")
    
    print("\n📈 Métricas Clave:")
    for metrica in primario_info["justificacion"]["metricas_clave"]:
        print(f"   • {metrica}")
    
    # Mostrar justificación del segmento secundario
    secundario_info = justificacion["segmento_secundario"]
    print(f"\n\n📊 SEGMENTO SECUNDARIO: {secundario_info['segmento']}")
    print(f"   Score Total: {secundario_info['score_total']:.2f}/10\n")
    
    print("📋 Razones Estratégicas:")
    for razon in secundario_info["justificacion"]["razones_estrategicas"]:
        print(f"   • {razon}")
    
    print("\n💡 Ventajas Competitivas:")
    for ventaja in secundario_info["justificacion"]["ventajas_competitivas"]:
        print(f"   • {ventaja}")
    
    print("\n🚀 Estrategia Recomendada:")
    for estrategia in secundario_info["justificacion"]["estrategia_recomendada"]:
        print(f"   • {estrategia}")
    
    print("\n📈 Métricas Clave:")
    for metrica in secundario_info["justificacion"]["metricas_clave"]:
        print(f"   • {metrica}")
    
    # Mostrar complementariedad
    complementariedad = justificacion["complementariedad"]
    print(f"\n\n🔗 COMPLEMENTARIEDAD ENTRE SEGMENTOS")
    print("\n💼 Sinergias:")
    for sinergia in complementariedad["sinergias"]:
        print(f"   • {sinergia}")
    
    print("\n📊 Distribución Recomendada de Recursos:")
    for recurso, porcentaje in complementariedad["distribucion_recomendada"].items():
        print(f"   • {recurso}: {porcentaje}")
    
    print("\n🗺️ Roadmap Estratégico:")
    for paso in complementariedad["roadmap"]:
        print(f"   • {paso}")
    
    # Matriz de Riesgo-Oportunidad
    print("\n\n" + "="*100)
    print("MATRIZ DE RIESGO-OPORTUNIDAD")
    print("="*100 + "\n")
    
    matriz_riesgo = matriz.generar_matriz_riesgo_oportunidad()
    
    print("🎯 Alta Oportunidad - Bajo Riesgo (Prioridad Máxima):")
    for seg in matriz_riesgo["alta_oportunidad_bajo_riesgo"]:
        print(f"   • {seg['segmento']} (Oportunidad: {seg['score_oportunidad']:.2f}, Riesgo: {seg['score_riesgo']:.2f})")
    
    print("\n⚡ Alta Oportunidad - Alto Riesgo (Requiere Estrategia Especial):")
    for seg in matriz_riesgo["alta_oportunidad_alto_riesgo"]:
        print(f"   • {seg['segmento']} (Oportunidad: {seg['score_oportunidad']:.2f}, Riesgo: {seg['score_riesgo']:.2f})")
    
    print("\n📊 Baja Oportunidad - Bajo Riesgo (Baja Prioridad):")
    for seg in matriz_riesgo["baja_oportunidad_bajo_riesgo"]:
        print(f"   • {seg['segmento']} (Oportunidad: {seg['score_oportunidad']:.2f}, Riesgo: {seg['score_riesgo']:.2f})")
    
    # Canales de Distribución
    print("\n\n" + "="*100)
    print("ANÁLISIS DE CANALES DE DISTRIBUCIÓN")
    print("="*100 + "\n")
    
    canales = matriz.analizar_canales_distribucion()
    for nombre_seg, info in list(canales.items())[:3]:  # Mostrar top 3
        print(f"\n📢 {nombre_seg}:")
        print(f"   Prioridad: {info['prioridad']}")
        print(f"   Presupuesto estimado mensual: ${info['presupuesto_estimado_mensual']:,.0f}")
        print("   Canales recomendados:")
        for canal in info['canales_recomendados'][:4]:
            print(f"      • {canal}")
    
    # Recomendaciones de Pricing
    print("\n\n" + "="*100)
    print("RECOMENDACIONES DE PRICING POR SEGMENTO")
    print("="*100 + "\n")
    
    pricing = matriz.recomendar_pricing_por_segmento()
    for nombre_seg, info in list(pricing.items())[:3]:  # Mostrar top 3
        if info['precio_base_anual_usd'] > 0:
            print(f"\n💰 {nombre_seg}:")
            print(f"   Modelo recomendado: {info['modelo_recomendado']}")
            print(f"   Precio base anual: ${info['precio_base_anual_usd']:,.0f}")
            if info['rango_recomendado']['minimo'] > 0:
                print(f"   Rango: ${info['rango_recomendado']['minimo']:,.0f} - ${info['rango_recomendado']['maximo']:,.0f}")
            print("   Estrategias:")
            for estrategia in info['estrategia_pricing'][:3]:
                print(f"      • {estrategia}")
    
    # Tendencias de Mercado
    print("\n\n" + "="*100)
    print("ANÁLISIS DE TENDENCIAS DE MERCADO")
    print("="*100 + "\n")
    
    tendencias = matriz.analizar_tendencias_mercado()
    print("📈 Insights Clave:")
    for insight in tendencias["insights"]:
        print(f"   • {insight}")
    
    # Dashboard Ejecutivo
    print("\n\n" + "="*100)
    print("DASHBOARD EJECUTIVO")
    print("="*100 + "\n")
    
    dashboard = matriz.generar_dashboard_ejecutivo()
    print(f"📊 Resumen Ejecutivo:")
    print(f"   Total Segmentos: {dashboard['resumen_ejecutivo']['total_segmentos']}")
    print(f"   Segmento Primario: {dashboard['resumen_ejecutivo']['segmento_primario']}")
    print(f"   Segmento Secundario: {dashboard['resumen_ejecutivo']['segmento_secundario']}")
    
    print(f"\n📈 Métricas Agregadas:")
    print(f"   Score Promedio: {dashboard['metricas_agregadas']['score_promedio']:.2f}/10")
    print(f"   Score Máximo: {dashboard['metricas_agregadas']['score_maximo']:.2f}/10")
    print(f"   Segmentos Alta Prioridad: {dashboard['metricas_agregadas']['segmentos_alta_prioridad']}")
    
    if dashboard['alertas']:
        print(f"\n⚠️ Alertas:")
        for alerta in dashboard['alertas'][:5]:  # Mostrar top 5
            print(f"   • [{alerta['tipo']}] {alerta['segmento']}: {alerta['mensaje']}")
    
    # Análisis de Unidad Económica para segmentos principales
    print("\n\n" + "="*100)
    print("ANÁLISIS DE UNIDAD ECONÓMICA - SEGMENTOS PRINCIPALES")
    print("="*100 + "\n")
    
    if matriz.segmento_primario:
        unidad_primario = matriz.calcular_unidad_economica(matriz.segmento_primario.id)
        print(f"\n💰 {unidad_primario['segmento']}:")
        print(f"   CAC: ${unidad_primario['cac']:,.0f}")
        print(f"   LTV: ${unidad_primario['ltv']:,.0f}")
        print(f"   Ratio LTV:CAC: {unidad_primario['ratio_ltv_cac']:.2f}")
        print(f"   Payback Period: {unidad_primario['payback_meses']:.1f} meses")
        print(f"   Margen: {unidad_primario['margen_porcentaje']:.1f}%")
        print(f"   Salud: {unidad_primario['evaluacion']['salud']}")
        print("   Recomendaciones:")
        for rec in unidad_primario['evaluacion']['recomendaciones']:
            print(f"      • {rec}")
    
    if matriz.segmento_secundario:
        unidad_secundario = matriz.calcular_unidad_economica(matriz.segmento_secundario.id)
        print(f"\n💰 {unidad_secundario['segmento']}:")
        print(f"   CAC: ${unidad_secundario['cac']:,.0f}")
        print(f"   LTV: ${unidad_secundario['ltv']:,.0f}")
        print(f"   Ratio LTV:CAC: {unidad_secundario['ratio_ltv_cac']:.2f}")
        print(f"   Payback Period: {unidad_secundario['payback_meses']:.1f} meses")
        print(f"   Margen: {unidad_secundario['margen_porcentaje']:.1f}%")
        print(f"   Salud: {unidad_secundario['evaluacion']['salud']}")
    
    # Análisis Predictivo
    print("\n\n" + "="*100)
    print("ANÁLISIS PREDICTIVO DE CRECIMIENTO (3 AÑOS)")
    print("="*100 + "\n")
    
    predictivo = matriz.analisis_predictivo_crecimiento()
    for nombre_seg, proyeccion in list(predictivo.items())[:2]:  # Mostrar top 2
        print(f"\n📊 {nombre_seg}:")
        print(f"   TAM Actual: ${proyeccion['tam_actual']:,.0f}M")
        print(f"   Crecimiento Anual: {proyeccion['crecimiento_anual']:.1f}%")
        print(f"   Valor Presente 3 Años: ${proyeccion['valor_presente_3anos']:,.0f}M")
        print("   Proyección de Ingresos:")
        for ingreso in proyeccion['ingresos']:
            print(f"      Año {ingreso['ano']}: ${ingreso['ingresos_proyectados']:,.0f}M (Penetración: {ingreso['penetracion']:.1f}%)")
    
    # Matriz BCG
    print("\n\n" + "="*100)
    print("MATRIZ BCG ADAPTADA")
    print("="*100 + "\n")
    
    bcg = matriz.matriz_bcg_adaptada()
    print("⭐ Estrellas (Alto crecimiento, Alta cuota):")
    for seg in bcg["estrellas"]:
        print(f"   • {seg['nombre']} (Crecimiento: {seg['crecimiento']:.1f}, Cuota: {seg['cuota_relativa']:.2f})")
    
    print("\n🐄 Vacas Lecheras (Bajo crecimiento, Alta cuota):")
    for seg in bcg["vacas_lecheras"]:
        print(f"   • {seg['nombre']} (Crecimiento: {seg['crecimiento']:.1f}, Cuota: {seg['cuota_relativa']:.2f})")
    
    print("\n❓ Interrogantes (Alto crecimiento, Baja cuota):")
    for seg in bcg["interrogantes"]:
        print(f"   • {seg['nombre']} (Crecimiento: {seg['crecimiento']:.1f}, Cuota: {seg['cuota_relativa']:.2f})")
    
    # Análisis de Sinergias
    print("\n\n" + "="*100)
    print("ANÁLISIS DE SINERGIAS ENTRE SEGMENTOS")
    print("="*100 + "\n")
    
    sinergias = matriz.analisis_sinergias_segmentos()
    print(f"Total sinergias identificadas: {sinergias['total_sinergias']}")
    for sinergia in sinergias["sinergias"][:5]:  # Top 5
        print(f"\n🔗 {sinergia['segmento_1']} ↔ {sinergia['segmento_2']}:")
        print(f"   Score Sinergia: {sinergia['score_sinergia']:.2f}")
        print(f"   Tipo: {sinergia['tipo_sinergia']}")
        print("   Oportunidades:")
        for op in sinergia['oportunidades'][:2]:
            print(f"      • {op}")
    
    # Plan de Acción Ejecutable
    print("\n\n" + "="*100)
    print("PLAN DE ACCIÓN EJECUTABLE")
    print("="*100 + "\n")
    
    plan = matriz.generar_plan_accion_ejecutable()
    print("📋 Resumen:")
    print(f"   Segmento Primario: {plan['resumen']['segmento_primario']}")
    print(f"   Segmento Secundario: {plan['resumen']['segmento_secundario']}")
    print(f"   Segmentos Alta Prioridad: {plan['resumen']['prioridad_total']}")
    
    print("\n⚡ Acciones Inmediatas (Mes 1):")
    for accion in plan["acciones_inmediatas"][:4]:
        print(f"   • {accion}")
    
    print("\n📅 Acciones 3 Meses:")
    for accion in plan["acciones_3_meses"]:
        print(f"   • {accion}")
    
    print("\n💼 Recursos Necesarios:")
    for recurso, valor in plan["recursos_necesarios"].items():
        if isinstance(valor, (int, float)):
            if recurso.startswith("presupuesto"):
                print(f"   • {recurso}: ${valor:,.0f}")
            else:
                print(f"   • {recurso}: {valor}")
        else:
            print(f"   • {recurso}: {valor}")
    
    print("\n⚠️ Riesgos y Mitigación:")
    for riesgo in plan["riesgos_y_mitigacion"]:
        print(f"   • {riesgo['riesgo']}: {riesgo['mitigacion']}")
    
    # Análisis de Mercado Total
    print("\n\n" + "="*100)
    print("ANÁLISIS DE MERCADO TOTAL (TAM/SAM/SOM)")
    print("="*100 + "\n")
    
    mercado_total = matriz.analisis_mercado_total()
    print(f"📊 TAM Total: ${mercado_total['tam_total']:,.0f}M")
    print(f"📊 SAM Total: ${mercado_total['sam_total']:,.0f}M")
    print(f"📊 SOM Total: ${mercado_total['som_total']:,.0f}M")
    print(f"📈 Crecimiento Promedio: {mercado_total['crecimiento_promedio']:.1f}%")
    print(f"📉 Penetración Actual: {mercado_total['penetracion_actual']:.1f}%")
    print(f"💰 Oportunidad de Crecimiento: ${mercado_total['oportunidad_crecimiento']:,.0f}M")
    print(f"\nEvaluación: {mercado_total['evaluacion']['tamano_mercado']} - {mercado_total['evaluacion']['oportunidad']}")
    print(f"Recomendación: {mercado_total['evaluacion']['recomendacion']}")
    
    # Análisis de Cohortes
    print("\n\n" + "="*100)
    print("ANÁLISIS DE COHORTES")
    print("="*100 + "\n")
    
    cohortes = matriz.analisis_cohortes_segmentos()
    print("📊 Métricas por Industria:")
    for industria, metricas in list(cohortes["metricas_cohortes"]["por_industria"].items())[:3]:
        print(f"   • {industria}: {metricas['cantidad']} segmentos, Score Promedio: {metricas['score_promedio']:.2f}")
    
    print("\n📊 Métricas por Geografía:")
    for geografia, metricas in list(cohortes["metricas_cohortes"]["por_geografia"].items())[:3]:
        print(f"   • {geografia}: {metricas['cantidad']} segmentos, Score Promedio: {metricas['score_promedio']:.2f}")
    
    # Recomendaciones de Partnerships
    print("\n\n" + "="*100)
    print("RECOMENDACIONES DE PARTNERSHIPS ESTRATÉGICOS")
    print("="*100 + "\n")
    
    partnerships = matriz.recomendar_partnerships()
    for nombre_seg, info in list(partnerships.items())[:3]:  # Top 3
        print(f"\n🤝 {nombre_seg}:")
        print(f"   Tipo: {info['tipo_partnership']}")
        print(f"   Valor Esperado: {info['valor_esperado']}")
        print("   Partnerships Recomendados:")
        for partner in info['partnerships_recomendados'][:4]:
            print(f"      • {partner}")
    
    # Matriz de Priorización Mejorada
    print("\n\n" + "="*100)
    print("MATRIZ DE PRIORIZACIÓN MEJORADA")
    print("="*100 + "\n")
    
    priorizacion = matriz.matriz_priorizacion_mejorada()
    print("🔥 Alta Prioridad:")
    for seg in priorizacion["alta_prioridad"][:3]:
        print(f"   • {seg['nombre']} (Score: {seg['score_prioridad']:.2f}) - {seg['recomendacion']}")
    
    print("\n⭐ Media-Alta Prioridad:")
    for seg in priorizacion["media_alta_prioridad"][:3]:
        print(f"   • {seg['nombre']} (Score: {seg['score_prioridad']:.2f}) - {seg['recomendacion']}")
    
    # Análisis de Inversión Recomendada
    print("\n\n" + "="*100)
    print("ANÁLISIS DE INVERSIÓN RECOMENDADA")
    print("="*100 + "\n")
    
    inversion = matriz.analisis_inversion_recomendada()
    print(f"💰 Inversión Total Recomendada: ${inversion['inversion_total_recomendada']:,.0f}")
    print("\n🏆 Top 3 Inversiones por ROI:")
    for inv in inversion["top_3_inversiones"]:
        print(f"\n   • {inv['segmento']}:")
        print(f"     Inversión: ${inv['inversion_recomendada']:,.0f}")
        print(f"     ROI Esperado (3 años): {inv['roi_esperado_3anos']:.1f}%")
        print(f"     Payback: Año {inv['payback_ano']}" if inv['payback_ano'] else "     Payback: No alcanzado")
        print(f"     Evaluación: {inv['evaluacion']}")
        print(f"     Recomendación: {inv['recomendacion']}")
    
    # Análisis de Riesgo Financiero
    print("\n\n" + "="*100)
    print("ANÁLISIS DE RIESGO FINANCIERO")
    print("="*100 + "\n")
    
    riesgo_financiero = matriz.analisis_riesgo_financiero()
    print(f"📊 Resumen de Riesgos:")
    print(f"   Alto Riesgo: {riesgo_financiero['resumen']['alto_riesgo']} segmentos")
    print(f"   Medio Riesgo: {riesgo_financiero['resumen']['medio_riesgo']} segmentos")
    print(f"   Bajo Riesgo: {riesgo_financiero['resumen']['bajo_riesgo']} segmentos")
    
    print("\n⚠️ Segmentos con Mayor Riesgo:")
    for riesgo in riesgo_financiero["riesgos"][:3]:
        print(f"\n   • {riesgo['segmento']}:")
        print(f"     Nivel: {riesgo['nivel_riesgo']} (Score: {riesgo['score_riesgo']})")
        print(f"     Ratio LTV:CAC: {riesgo['ratio_ltv_cac']:.2f}")
        print(f"     Payback: {riesgo['payback_meses']:.1f} meses")
        print(f"     Margen: {riesgo['margen_porcentaje']:.1f}%")
        print("     Mitigaciones:")
        for mit in riesgo['mitigaciones'][:2]:
            print(f"       - {mit}")
    
    # Análisis de Ciclo de Vida para segmentos principales
    print("\n\n" + "="*100)
    print("ANÁLISIS DE CICLO DE VIDA DEL CLIENTE")
    print("="*100 + "\n")
    
    if matriz.segmento_primario:
        ciclo_vida = matriz.analisis_ciclo_vida_cliente(matriz.segmento_primario.id)
        print(f"\n👤 {ciclo_vida['segmento']}:")
        print(f"   Vida Media Cliente: {ciclo_vida['vida_media_cliente_anos']:.1f} años")
        print(f"   Tasa Retención: {ciclo_vida['tasa_retencion']:.1%}")
        print(f"   Valor Total CLV: ${ciclo_vida['valor_total_clv']:,.0f}")
        print("\n   Fases del Ciclo de Vida:")
        print(f"     • Adquisición: {ciclo_vida['fases']['adquisicion']['duracion_meses']:.1f} meses, Costo: ${ciclo_vida['fases']['adquisicion']['costo']:,.0f}")
        print(f"     • Activación: {ciclo_vida['fases']['activacion']['duracion_meses']:.1f} meses, Costo: ${ciclo_vida['fases']['activacion']['costo']:,.0f}")
        print(f"     • Retención: {ciclo_vida['fases']['retencion']['duracion_meses']:.1f} meses")
        print(f"     • Expansión: Probabilidad {ciclo_vida['fases']['expansion']['probabilidad']:.0%}, Valor: ${ciclo_vida['fases']['expansion']['valor_promedio']:,.0f}")
        print(f"     • Referencia: Probabilidad {ciclo_vida['fases']['referencia']['probabilidad']:.0%}, Valor: ${ciclo_vida['fases']['referencia']['valor_referencia']:,.0f}")
        print("\n   Recomendaciones:")
        for rec in ciclo_vida['recomendaciones'][:3]:
            print(f"     • {rec}")
    
    # Customer Journey para segmento primario
    print("\n\n" + "="*100)
    print("ANÁLISIS DE CUSTOMER JOURNEY")
    print("="*100 + "\n")
    
    if matriz.segmento_primario:
        journey = matriz.analisis_customer_journey(matriz.segmento_primario.id)
        print(f"\n🗺️ {journey['segmento']}:")
        print("\n   Etapas del Journey:")
        for etapa in journey['etapas']:
            print(f"     • {etapa['nombre']}: {etapa['descripcion']}")
            print(f"       Duración: {etapa['duracion_estimada']}")
            print(f"       Canales: {', '.join(etapa['canales'][:3])}")
        
        print("\n   Momentos de Verdad:")
        for momento in journey['momentos_verdad'][:3]:
            print(f"     • {momento}")
        
        if journey['fricciones']:
            print("\n   Fricciones Identificadas:")
            for friccion in journey['fricciones']:
                print(f"     • {friccion}")
    
    # Estrategia de Producto
    print("\n\n" + "="*100)
    print("ESTRATEGIA DE PRODUCTO POR SEGMENTO")
    print("="*100 + "\n")
    
    if matriz.segmento_primario:
        estrategia_producto = matriz.estrategia_producto_por_segmento(matriz.segmento_primario.id)
        print(f"\n📦 {estrategia_producto['segmento']}:")
        print("\n   Prioridades de Producto:")
        for prioridad in estrategia_producto['prioridades_producto'][:4]:
            print(f"     • {prioridad}")
        
        print("\n   Features Críticas:")
        for feature in estrategia_producto['features_criticas']:
            print(f"     • {feature}")
        
        print("\n   Roadmap Recomendado (3 meses):")
        for item in estrategia_producto['roadmap_recomendado']['corto_plazo_3meses']:
            print(f"     • {item}")
    
    # Fit de Canal
    print("\n\n" + "="*100)
    print("ANÁLISIS DE FIT DE CANAL")
    print("="*100 + "\n")
    
    if matriz.segmento_primario:
        fit_canal = matriz.analisis_fit_canal(matriz.segmento_primario.id)
        print(f"\n📡 {fit_canal['segmento']}:")
        print(f"\n   Mejor Fit: {fit_canal['mejor_fit']['canal']} (Score: {fit_canal['mejor_fit']['score']}/10)")
        print("   Razones:")
        for razon in fit_canal['mejor_fit']['razones']:
            print(f"     • {razon}")
        
        print("\n   Canales Evaluados:")
        for canal in fit_canal['canales_evaluados'][:4]:
            print(f"     • {canal['nombre']}: {canal['score']}/10")
    
    # Contenido y Messaging
    print("\n\n" + "="*100)
    print("ANÁLISIS DE CONTENIDO Y MESSAGING")
    print("="*100 + "\n")
    
    if matriz.segmento_primario:
        contenido = matriz.analisis_contenido_messaging(matriz.segmento_primario.id)
        print(f"\n📝 {contenido['segmento']}:")
        print(f"\n   Mensaje Principal:")
        print(f"     {contenido['mensaje_principal']}")
        
        print("\n   Value Propositions:")
        for vp in contenido['value_propositions'][:3]:
            print(f"     • {vp}")
        
        print(f"\n   Tono Recomendado: {contenido['tono_recomendado']}")
        
        print("\n   Tipos de Contenido Recomendados:")
        for tipo in contenido['tipos_contenido'][:5]:
            print(f"     • {tipo}")
    
    # Análisis de Competencia Comparativa
    print("\n\n" + "="*100)
    print("ANÁLISIS DE COMPETENCIA COMPARATIVA")
    print("="*100 + "\n")
    
    competencia_comp = matriz.analisis_competencia_comparativa()
    print("📊 Segmentos por Intensidad Competitiva:")
    print(f"   Baja Intensidad: {len(competencia_comp['segmentos_por_intensidad_competitiva']['baja'])} segmentos")
    print(f"   Media Intensidad: {len(competencia_comp['segmentos_por_intensidad_competitiva']['media'])} segmentos")
    print(f"   Alta Intensidad: {len(competencia_comp['segmentos_por_intensidad_competitiva']['alta'])} segmentos")
    
    print("\n🎯 Segmentos con Alta Diferenciación:")
    for seg in competencia_comp['segmentos_por_diferenciacion']['alta'][:3]:
        print(f"   • {seg['segmento']}: {seg['diferenciacion']:.1f}/10")
    
    print("\n💡 Recomendaciones Competitivas:")
    for rec in competencia_comp['recomendaciones_competitivas']:
        print(f"   • {rec}")
    
    # Análisis de Tendencias Temporales
    print("\n\n" + "="*100)
    print("ANÁLISIS DE TENDENCIAS TEMPORALES (5 AÑOS)")
    print("="*100 + "\n")
    
    tendencias_temp = matriz.analisis_tendencias_temporales()
    print("📈 Proyección de Mercado:")
    for ano in range(1, 4):  # Mostrar primeros 3 años
        proy = tendencias_temp['proyeccion_mercado'][f'ano_{ano}']
        print(f"   Año {ano}:")
        print(f"     SAM: ${proy['sam']:,.0f}M")
        if proy['crecimiento_vs_anterior'] > 0:
            print(f"     Crecimiento: +{proy['crecimiento_vs_anterior']:.1f}%")
    
    # Estrategia de Crecimiento
    print("\n\n" + "="*100)
    print("ESTRATEGIA DE CRECIMIENTO POR SEGMENTO")
    print("="*100 + "\n")
    
    if matriz.segmento_primario:
        crecimiento = matriz.estrategia_crecimiento_por_segmento(matriz.segmento_primario.id)
        print(f"\n🚀 {crecimiento['segmento']}:")
        print(f"   Fase de Crecimiento: {crecimiento['fase_crecimiento']}")
        print("\n   Estrategias Recomendadas:")
        for estrategia in crecimiento['estrategias_recomendadas'][:4]:
            print(f"     • {estrategia}")
        
        print("\n   Roadmap Q1:")
        for item in crecimiento['roadmap_crecimiento']['trimestre_1']:
            print(f"     • {item}")
    
    # Customer Success
    print("\n\n" + "="*100)
    print("ANÁLISIS DE CUSTOMER SUCCESS")
    print("="*100 + "\n")
    
    if matriz.segmento_primario:
        cs = matriz.analisis_customer_success(matriz.segmento_primario.id)
        print(f"\n👥 {cs['segmento']}:")
        print(f"   Modelo Recomendado: {cs['modelo_recomendado']}")
        print("\n   Actividades Críticas:")
        for actividad in cs['actividades_critical'][:4]:
            print(f"     • {actividad}")
        
        print("\n   Métricas de Success:")
        for metrica, valor in cs['metricas_success'].items():
            print(f"     • {metrica}: {valor}")
    
    # Pricing Dinámico
    print("\n\n" + "="*100)
    print("ANÁLISIS DE PRICING DINÁMICO")
    print("="*100 + "\n")
    
    if matriz.segmento_primario:
        pricing_din = matriz.analisis_pricing_dinamico(matriz.segmento_primario.id)
        print(f"\n💰 {pricing_din['segmento']}:")
        print(f"   Modelo Recomendado: {pricing_din['modelo_pricing_recomendado']}")
        print("\n   Estructura de Precios:")
        for tier, precio in pricing_din['estructura_precios'].items():
            if isinstance(precio, (int, float)):
                print(f"     • {tier.capitalize()}: ${precio:,.0f}/año")
            else:
                print(f"     • {tier.capitalize()}: {precio}")
        
        print("\n   Optimizaciones:")
        for opt in pricing_din['optimizaciones'][:3]:
            print(f"     • {opt}")
    
    # Matriz de Priorización Visual
    print("\n\n" + matriz.generar_matriz_priorizacion_visual())
    
    # Benchmarking Competitivo
    print("\n\n" + "="*100)
    print("ANÁLISIS DE BENCHMARKING COMPETITIVO")
    print("="*100 + "\n")
    
    benchmarking = matriz.analisis_benchmarking_competitivo()
    print("🏆 Mejores Prácticas:")
    print(f"   Mejor Score Total: {benchmarking['mejores_practicas_por_categoria']['mejor_score_total']['segmento']}")
    print(f"   Mejor Oportunidad: {benchmarking['mejores_practicas_por_categoria']['mejor_oportunidad']['segmento']}")
    print(f"   Menor Riesgo: {benchmarking['mejores_practicas_por_categoria']['menor_riesgo']['segmento']}")
    
    if benchmarking['benchmarks_metricas']:
        print("\n📊 Benchmarks de Métricas:")
        print(f"   Mejor Ratio LTV:CAC: {benchmarking['benchmarks_metricas']['mejor_ratio_ltv_cac']['segmento']} ({benchmarking['benchmarks_metricas']['mejor_ratio_ltv_cac']['ratio']:.2f})")
        print(f"   Promedio Ratio: {benchmarking['benchmarks_metricas']['promedio_ratio']:.2f}")
        print(f"   Promedio CAC: ${benchmarking['benchmarks_metricas']['promedio_cac']:,.0f}")
        print(f"   Promedio LTV: ${benchmarking['benchmarks_metricas']['promedio_ltv']:,.0f}")
    
    # Roadmap Estratégico
    print("\n\n" + "="*100)
    print("ROADMAP ESTRATÉGICO (3 AÑOS)")
    print("="*100 + "\n")
    
    roadmap = matriz.analisis_roadmap_estrategico()
    print(f"🎯 Visión 3 Años:")
    print(f"   {roadmap['vision_3anos']}")
    
    print("\n📅 Objetivos por Año:")
    for ano, objetivos in roadmap['objetivos_por_ano'].items():
        print(f"\n   {ano.upper().replace('_', ' ')}:")
        print(f"     Objetivo: {objetivos['objetivo_principal']}")
        print(f"     Ingresos: {objetivos['metricas']['ingresos_objetivo']}")
        print(f"     Clientes: {objetivos['metricas']['clientes_objetivo']}")
    
    print("\n🎯 Hitos Clave:")
    for hito in roadmap['hitos_clave'][:6]:
        print(f"   • {hito}")
    
    # Métricas Operacionales
    print("\n\n" + "="*100)
    print("MÉTRICAS OPERACIONALES AGREGADAS")
    print("="*100 + "\n")
    
    metricas_op = matriz.analisis_metricas_operacionales()
    print("📊 Métricas Agregadas:")
    print(f"   CAC Promedio: ${metricas_op['agregadas']['cac_promedio']:,.0f}")
    print(f"   LTV Promedio: ${metricas_op['agregadas']['ltv_promedio']:,.0f}")
    print(f"   Ratio Promedio: {metricas_op['agregadas']['ratio_promedio']:.2f}")
    print(f"   Mejor Segmento (Ratio): {metricas_op['agregadas']['mejor_segmento_ratio']}")
    
    print("\n💡 Recomendaciones Operacionales:")
    for rec in metricas_op['recomendaciones']:
        print(f"   • {rec}")
    
    # Resumen Ejecutivo Completo
    print("\n\n" + "="*100)
    print("RESUMEN EJECUTIVO COMPLETO")
    print("="*100 + "\n")
    print(matriz.generar_resumen_ejecutivo_completo())
    
    # Escenarios de Mercado
    print("\n\n" + "="*100)
    print("ANÁLISIS DE ESCENARIOS DE MERCADO")
    print("="*100 + "\n")
    
    escenarios = matriz.analisis_escenarios_mercado()
    print("📊 Escenario Base (60% probabilidad):")
    print(f"   Ingresos 3 años: ${escenarios['escenario_base']['ingresos_proyectados_3anos']:,.0f}M")
    print(f"   Clientes objetivo: {escenarios['escenario_base']['clientes_objetivo']}")
    
    print("\n🚀 Escenario Optimista (20% probabilidad):")
    print(f"   Ingresos 3 años: ${escenarios['escenario_optimista']['ingresos_proyectados_3anos']:,.0f}M")
    print(f"   Clientes objetivo: {escenarios['escenario_optimista']['clientes_objetivo']}")
    
    print("\n⚠️ Escenario Pesimista (20% probabilidad):")
    print(f"   Ingresos 3 años: ${escenarios['escenario_pesimista']['ingresos_proyectados_3anos']:,.0f}M")
    print(f"   Clientes objetivo: {escenarios['escenario_pesimista']['clientes_objetivo']}")
    
    # Expansión Geográfica
    print("\n\n" + "="*100)
    print("ANÁLISIS DE EXPANSIÓN GEOGRÁFICA")
    print("="*100 + "\n")
    
    expansion = matriz.analisis_expansion_geografica()
    print(f"🌍 Mercados Actuales: {', '.join(expansion['mercados_actuales'])}")
    print(f"🎯 Mercados Oportunidad: {', '.join(expansion['mercados_oportunidad']) if expansion['mercados_oportunidad'] else 'Ninguno identificado'}")
    
    if expansion['estrategia_expansion']['fase_1']['mercados']:
        print("\n📅 Estrategia de Expansión:")
        print(f"   Fase 1 ({expansion['estrategia_expansion']['fase_1']['tiempo']}): {', '.join(expansion['estrategia_expansion']['fase_1']['mercados'])}")
    
    # Recursos por Fase
    print("\n\n" + "="*100)
    print("ANÁLISIS DE RECURSOS POR FASE")
    print("="*100 + "\n")
    
    recursos = matriz.analisis_recursos_por_fase()
    print("👥 Fase Validación (0-6 meses):")
    print(f"   Equipo: {recursos['fase_validacion']['equipo']['total']} personas")
    print(f"   Presupuesto: ${recursos['fase_validacion']['presupuesto']['total']:,.0f}")
    
    print("\n📈 Fase Crecimiento (6-18 meses):")
    print(f"   Equipo: {recursos['fase_crecimiento']['equipo']['total']} personas")
    print(f"   Presupuesto: ${recursos['fase_crecimiento']['presupuesto']['total']:,.0f}")
    
    print("\n🚀 Fase Escala (18-36 meses):")
    print(f"   Equipo: {recursos['fase_escala']['equipo']['total']} personas")
    print(f"   Presupuesto: ${recursos['fase_escala']['presupuesto']['total']:,.0f}")
    
    # Análisis Detallado Segmento Primario
    if matriz.segmento_primario:
        print("\n\n" + "="*100)
        print(f"ANÁLISIS DETALLADO: {matriz.segmento_primario.nombre}")
        print("="*100 + "\n")
        
        # Propuesta de Valor
        propuesta_valor = matriz.analisis_propuesta_valor_por_segmento(matriz.segmento_primario.id)
        print("💎 Propuesta de Valor:")
        print(f"   Problema: {propuesta_valor['problema_principal']}")
        print(f"   Mensaje Clave: {propuesta_valor['mensaje_clave']}")
        
        # Barreras de Adopción
        barreras = matriz.analisis_barreras_adopcion(matriz.segmento_primario.id)
        print("\n🚧 Barreras de Adopción:")
        print(f"   Nivel de Riesgo: {barreras['nivel_riesgo']}")
        print(f"   Tiempo Adopción: {barreras['tiempo_adopcion_estimado']}")
        print(f"   Barreras Identificadas: {len(barreras['barreras_identificadas'])}")
        
        # Upsell/Cross-sell
        upsell = matriz.analisis_upsell_crosssell_potencial(matriz.segmento_primario.id)
        print("\n💰 Potencial Upsell/Cross-sell:")
        print(f"   Tasa Upsell: {upsell['potencial_upsell']['tasa_esperada']:.1f}%")
        print(f"   Ingresos Adicionales/100 clientes: ${upsell['ingresos_adicionales_proyectados']['por_100_clientes']:,.0f}")
        
        # Viralidad
        viralidad = matriz.analisis_viralidad_referidos(matriz.segmento_primario.id)
        print("\n📢 Potencial de Viralidad:")
        print(f"   Nivel: {viralidad['potencial_viralidad']}")
        print(f"   K-Factor: {viralidad['k_factor']:.2f}")
        print(f"   Ahorro CAC con referidos: ${viralidad['programa_referidos']['ahorro_cac']:,.0f}")
        
        # Defensibilidad
        defensibilidad = matriz.analisis_defensibilidad_competitiva(matriz.segmento_primario.id)
        print("\n🛡️ Defensibilidad Competitiva:")
        print(f"   Score: {defensibilidad['score_defensibilidad']:.1f}/10")
        print(f"   Ventajas: {len(defensibilidad['ventajas_competitivas'])} identificadas")
        
        # Timing
        timing = matriz.analisis_timing_mercado(matriz.segmento_primario.id)
        print("\n⏰ Timing de Mercado:")
        print(f"   Momento: {timing['momento_mercado']}")
        print(f"   Ventana Oportunidad: {timing['ventana_oportunidad']}")
        print(f"   Recomendación: {timing['recomendacion_timing']}")
    
    # Exportar análisis
    print("\n\n" + "="*100)
    print("EXPORTANDO ANÁLISIS...")
    print("="*100 + "\n")
    
    # Exportar JSON
    json_output = matriz.exportar_analisis(formato="json")
    with open("analisis_segmentacion.json", "w", encoding="utf-8") as f:
        f.write(json_output)
    print("✓ Análisis exportado a: analisis_segmentacion.json")
    
    # Exportar CSV
    try:
        csv_output = matriz.exportar_analisis(formato="csv")
        with open("analisis_segmentacion.csv", "w", encoding="utf-8") as f:
            f.write(csv_output)
        print("✓ Análisis exportado a: analisis_segmentacion.csv")
    except Exception as e:
        print(f"⚠ No se pudo exportar CSV (pandas no disponible): {e}")
    
    # Exportar Reporte Ejecutivo
    reporte_ejecutivo = matriz.generar_reporte_ejecutivo()
    with open("reporte_ejecutivo_segmentacion.txt", "w", encoding="utf-8") as f:
        f.write(reporte_ejecutivo)
    print("✓ Reporte ejecutivo exportado a: reporte_ejecutivo_segmentacion.txt")
    
    print("\n" + "="*100)
    print("ANÁLISIS COMPLETADO")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()

