"""
Módulo de emails avanzados para marketing automation.
Incluye generadores de emails AMP, transaccionales, análisis de atribución,
contenido dinámico y optimización de frecuencia.
"""
__version__ = '1.0.0'
__author__ = 'Marketing Automation Team'

# Importaciones principales
from .amp_email_generator import (
    AMPEmailGenerator,
    AMPComponentType
)

from .attribution_analyzer import (
    AttributionAnalyzer,
    AttributionModel
)

from .dynamic_content_generator import (
    DynamicContentGenerator,
    ContentType
)

from .transactional_email_generator import (
    TransactionalEmailGenerator,
    TransactionalEmailType
)

from .frequency_optimizer import (
    FrequencyOptimizer,
    EngagementLevel
)

# Exportar todo
__all__ = [
    # Generadores
    'AMPEmailGenerator',
    'TransactionalEmailGenerator',
    'DynamicContentGenerator',
    
    # Analizadores
    'AttributionAnalyzer',
    'FrequencyOptimizer',
    
    # Enums
    'AMPComponentType',
    'AttributionModel',
    'ContentType',
    'TransactionalEmailType',
    'EngagementLevel',
    
    # Metadata
    '__version__',
    '__author__'
]




