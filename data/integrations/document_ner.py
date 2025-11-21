"""
Reconocimiento de Entidades Nombradas (NER)
============================================

Extrae entidades nombradas de documentos (personas, organizaciones, lugares, etc.)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EntityType(Enum):
    """Tipos de entidades"""
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    LOCATION = "LOCATION"
    DATE = "DATE"
    MONEY = "MONEY"
    PERCENT = "PERCENT"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    TAX_ID = "TAX_ID"
    OTHER = "OTHER"


@dataclass
class NamedEntity:
    """Entidad nombrada"""
    text: str
    entity_type: EntityType
    start_pos: int
    end_pos: int
    confidence: float
    metadata: Dict[str, Any] = None


class NamedEntityRecognizer:
    """Reconocedor de entidades nombradas"""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Carga modelo NER"""
        try:
            import spacy
            self.model = spacy.load(self.model_name or "es_core_news_sm")
            self.logger.info(f"Modelo NER cargado: {self.model_name or 'es_core_news_sm'}")
        except ImportError:
            self.logger.warning(
                "spaCy no disponible. Instala con: pip install spacy && python -m spacy download es_core_news_sm"
            )
        except Exception as e:
            self.logger.error(f"Error cargando modelo NER: {e}")
    
    def extract_entities(self, text: str) -> List[NamedEntity]:
        """Extrae entidades nombradas del texto"""
        if not self.model:
            return self._extract_entities_regex(text)
        
        try:
            doc = self.model(text)
            entities = []
            
            for ent in doc.ents:
                entity_type = self._map_spacy_label(ent.label_)
                
                entities.append(NamedEntity(
                    text=ent.text,
                    entity_type=entity_type,
                    start_pos=ent.start_char,
                    end_pos=ent.end_char,
                    confidence=0.9,  # spaCy no proporciona confianza directa
                    metadata={"label": ent.label_}
                ))
            
            return entities
        except Exception as e:
            self.logger.error(f"Error extrayendo entidades: {e}")
            return self._extract_entities_regex(text)
    
    def _extract_entities_regex(self, text: str) -> List[NamedEntity]:
        """Extracción básica usando regex (fallback)"""
        import re
        entities = []
        
        # Emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entities.append(NamedEntity(
                text=match.group(),
                entity_type=EntityType.EMAIL,
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.95
            ))
        
        # Teléfonos
        phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        for match in re.finditer(phone_pattern, text):
            entities.append(NamedEntity(
                text=match.group(),
                entity_type=EntityType.PHONE,
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.85
            ))
        
        # Fechas
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        for match in re.finditer(date_pattern, text):
            entities.append(NamedEntity(
                text=match.group(),
                entity_type=EntityType.DATE,
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.9
            ))
        
        # Montos
        money_pattern = r'\$\s*\d+[,.]?\d*'
        for match in re.finditer(money_pattern, text):
            entities.append(NamedEntity(
                text=match.group(),
                entity_type=EntityType.MONEY,
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.9
            ))
        
        return entities
    
    def _map_spacy_label(self, label: str) -> EntityType:
        """Mapea etiquetas de spaCy a EntityType"""
        mapping = {
            "PER": EntityType.PERSON,
            "ORG": EntityType.ORGANIZATION,
            "LOC": EntityType.LOCATION,
            "MISC": EntityType.OTHER,
            "DATE": EntityType.DATE,
            "MONEY": EntityType.MONEY,
            "PERCENT": EntityType.PERCENT,
        }
        return mapping.get(label, EntityType.OTHER)
    
    def extract_entities_by_type(
        self,
        text: str,
        entity_type: EntityType
    ) -> List[str]:
        """Extrae entidades de un tipo específico"""
        entities = self.extract_entities(text)
        return [e.text for e in entities if e.entity_type == entity_type]
    
    def get_entity_summary(self, entities: List[NamedEntity]) -> Dict[str, Any]:
        """Genera resumen de entidades extraídas"""
        by_type = {}
        for entity in entities:
            if entity.entity_type not in by_type:
                by_type[entity.entity_type] = []
            by_type[entity.entity_type].append(entity.text)
        
        return {
            "total_entities": len(entities),
            "by_type": {
                k.value: {
                    "count": len(v),
                    "values": list(set(v))  # Únicos
                }
                for k, v in by_type.items()
            }
        }

