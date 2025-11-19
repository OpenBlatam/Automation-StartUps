"""
Templates predefinidos por categoría de producto para acelerar la generación.

Incluye templates optimizados para:
- Electrónica
- Moda y ropa
- Hogar y jardín
- Belleza y cuidado personal
- Deportes y fitness
- Alimentos y bebidas
- Juguetes y juegos
- Libros y medios
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ProductCategoryTemplates:
    """Templates predefinidos por categoría de producto."""
    
    TEMPLATES = {
        'electronics': {
            'key_benefits_template': [
                'Tecnología de última generación',
                'Rendimiento superior y eficiencia energética',
                'Diseño moderno y funcional',
                'Garantía extendida y soporte técnico'
            ],
            'technical_focus': [
                'Especificaciones técnicas detalladas',
                'Compatibilidad y conectividad',
                'Certificaciones y estándares',
                'Rendimiento y durabilidad'
            ],
            'tone': 'técnico y profesional',
            'target_keywords': ['tecnología', 'innovación', 'rendimiento', 'calidad'],
            'storytelling_angle': 'Innovación tecnológica que mejora la vida diaria'
        },
        'fashion': {
            'key_benefits_template': [
                'Diseño exclusivo y tendencia actual',
                'Calidad premium en materiales',
                'Comodidad y versatilidad',
                'Estilo único que refleja personalidad'
            ],
            'technical_focus': [
                'Composición de materiales',
                'Cuidado y mantenimiento',
                'Tallas y medidas',
                'Proceso de fabricación'
            ],
            'tone': 'elegante y aspiracional',
            'target_keywords': ['moda', 'estilo', 'diseño', 'tendencia'],
            'storytelling_angle': 'Expresión personal y estilo de vida'
        },
        'home_garden': {
            'key_benefits_template': [
                'Funcionalidad práctica para el hogar',
                'Durabilidad y resistencia',
                'Fácil instalación y mantenimiento',
                'Mejora la calidad de vida en el hogar'
            ],
            'technical_focus': [
                'Materiales y construcción',
                'Dimensiones y capacidad',
                'Instalación y uso',
                'Mantenimiento y cuidado'
            ],
            'tone': 'práctico y acogedor',
            'target_keywords': ['hogar', 'decoración', 'organización', 'confort'],
            'storytelling_angle': 'Transforma tu espacio en un hogar perfecto'
        },
        'beauty': {
            'key_benefits_template': [
                'Resultados visibles y comprobados',
                'Ingredientes naturales y seguros',
                'Fórmula avanzada y probada',
                'Cuidado personalizado para tu tipo de piel'
            ],
            'technical_focus': [
                'Ingredientes activos',
                'Tipo de piel recomendada',
                'Modo de uso y aplicación',
                'Certificaciones y pruebas'
            ],
            'tone': 'cuidado y empoderador',
            'target_keywords': ['belleza', 'cuidado personal', 'natural', 'resultados'],
            'storytelling_angle': 'Cuida tu piel y realza tu belleza natural'
        },
        'sports': {
            'key_benefits_template': [
                'Mejora el rendimiento deportivo',
                'Diseño ergonómico y cómodo',
                'Resistencia y durabilidad',
                'Tecnología deportiva avanzada'
            ],
            'technical_focus': [
                'Especificaciones técnicas',
                'Materiales y construcción',
                'Rendimiento y características',
                'Uso y mantenimiento'
            ],
            'tone': 'energético y motivador',
            'target_keywords': ['deporte', 'fitness', 'rendimiento', 'actividad'],
            'storytelling_angle': 'Supera tus límites y alcanza tus objetivos'
        },
        'food_beverage': {
            'key_benefits_template': [
                'Sabor auténtico y delicioso',
                'Ingredientes de calidad premium',
                'Beneficios nutricionales',
                'Frescura y calidad garantizada'
            ],
            'technical_focus': [
                'Ingredientes y origen',
                'Valor nutricional',
                'Proceso de elaboración',
                'Conservación y caducidad'
            ],
            'tone': 'apetitoso y saludable',
            'target_keywords': ['sabor', 'natural', 'nutritivo', 'calidad'],
            'storytelling_angle': 'Disfruta de sabores auténticos y nutritivos'
        },
        'toys_games': {
            'key_benefits_template': [
                'Diversión y entretenimiento garantizado',
                'Educativo y desarrolla habilidades',
                'Seguro y certificado',
                'Diseño atractivo y colorido'
            ],
            'technical_focus': [
                'Edad recomendada',
                'Materiales y seguridad',
                'Características y funciones',
                'Dimensiones y peso'
            ],
            'tone': 'divertido y educativo',
            'target_keywords': ['juguete', 'diversión', 'educativo', 'seguro'],
            'storytelling_angle': 'Acompaña el crecimiento y desarrollo de los niños'
        },
        'books_media': {
            'key_benefits_template': [
                'Contenido valioso y enriquecedor',
                'Autor reconocido y experto',
                'Formato práctico y accesible',
                'Aprendizaje y entretenimiento'
            ],
            'technical_focus': [
                'Información del autor',
                'Contenido y estructura',
                'Formato y edición',
                'Idioma y disponibilidad'
            ],
            'tone': 'inspirador e informativo',
            'target_keywords': ['libro', 'aprendizaje', 'conocimiento', 'lectura'],
            'storytelling_angle': 'Descubre nuevas perspectivas y conocimientos'
        },
        'eco_sustainable': {
            'key_benefits_template': [
                '100% sostenible y ecológico',
                'Impacto positivo en el medio ambiente',
                'Calidad premium sin compromiso',
                'Contribuye a un futuro mejor'
            ],
            'technical_focus': [
                'Materiales ecológicos',
                'Proceso de fabricación sostenible',
                'Certificaciones ambientales',
                'Impacto y beneficios ambientales'
            ],
            'tone': 'consciente y responsable',
            'target_keywords': ['ecológico', 'sostenible', 'verde', 'responsable'],
            'storytelling_angle': 'Elige productos que cuidan el planeta'
        }
    }
    
    @classmethod
    def get_template(cls, category: str) -> Optional[Dict]:
        """
        Obtiene el template para una categoría específica.
        
        Args:
            category: Categoría del producto
        
        Returns:
            Dict con template o None si no existe
        """
        category_lower = category.lower().replace(' ', '_')
        return cls.TEMPLATES.get(category_lower)
    
    @classmethod
    def get_suggested_benefits(cls, category: str, custom_benefits: List[str] = None) -> List[str]:
        """
        Obtiene beneficios sugeridos para una categoría, combinando template y beneficios personalizados.
        
        Args:
            category: Categoría del producto
            custom_benefits: Beneficios personalizados del usuario
        
        Returns:
            Lista de beneficios sugeridos
        """
        template = cls.get_template(category)
        if not template:
            return custom_benefits or []
        
        template_benefits = template.get('key_benefits_template', [])
        
        if custom_benefits:
            # Combinar: primeros 2 personalizados + 2 del template
            return custom_benefits[:2] + template_benefits[:2]
        
        return template_benefits
    
    @classmethod
    def get_suggested_keywords(cls, category: str, custom_keywords: List[str] = None) -> List[str]:
        """
        Obtiene keywords sugeridas para una categoría.
        
        Args:
            category: Categoría del producto
            custom_keywords: Keywords personalizados
        
        Returns:
            Lista de keywords sugeridas
        """
        template = cls.get_template(category)
        if not template:
            return custom_keywords or []
        
        template_keywords = template.get('target_keywords', [])
        
        if custom_keywords:
            return list(set(custom_keywords + template_keywords))
        
        return template_keywords
    
    @classmethod
    def get_storytelling_angle(cls, category: str) -> Optional[str]:
        """
        Obtiene el ángulo de storytelling sugerido para una categoría.
        
        Args:
            category: Categoría del producto
        
        Returns:
            Ángulo de storytelling o None
        """
        template = cls.get_template(category)
        if not template:
            return None
        
        return template.get('storytelling_angle')
    
    @classmethod
    def get_recommended_tone(cls, category: str) -> Optional[str]:
        """
        Obtiene el tono recomendado para una categoría.
        
        Args:
            category: Categoría del producto
        
        Returns:
            Tono recomendado o None
        """
        template = cls.get_template(category)
        if not template:
            return None
        
        return template.get('tone')
    
    @classmethod
    def list_categories(cls) -> List[str]:
        """
        Lista todas las categorías disponibles.
        
        Returns:
            Lista de categorías
        """
        return list(cls.TEMPLATES.keys())
    
    @classmethod
    def enhance_product_data(cls, product_data: Dict, category: str) -> Dict:
        """
        Enriquece los datos del producto con sugerencias del template.
        
        Args:
            product_data: Dict con datos del producto
            category: Categoría del producto
        
        Returns:
            Dict enriquecido con sugerencias del template
        """
        template = cls.get_template(category)
        if not template:
            return product_data
        
        enhanced = product_data.copy()
        
        # Agregar beneficios sugeridos si no existen
        if not enhanced.get('key_benefits'):
            enhanced['key_benefits'] = cls.get_suggested_benefits(category)
        
        # Agregar keywords sugeridas
        existing_keywords = enhanced.get('keywords', [])
        enhanced['keywords'] = cls.get_suggested_keywords(category, existing_keywords)
        
        # Agregar storytelling angle
        if not enhanced.get('brand_story'):
            enhanced['storytelling_angle'] = cls.get_storytelling_angle(category)
        
        # Agregar tono recomendado
        enhanced['recommended_tone'] = cls.get_recommended_tone(category)
        
        return enhanced






