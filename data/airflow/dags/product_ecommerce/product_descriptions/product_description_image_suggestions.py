"""
Generación de sugerencias de imágenes con IA para productos.

Incluye:
- Descripciones de imágenes sugeridas
- Prompts para generación con DALL-E/Midjourney
- Análisis de imágenes existentes
- Optimización de imágenes para e-commerce
"""

import logging
from typing import Dict, List, Optional
from product_description_generator import LLMClient

logger = logging.getLogger(__name__)


class ImageSuggestionGenerator:
    """Generador de sugerencias de imágenes con IA."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def generate_image_suggestions(
        self,
        description_data: Dict,
        num_suggestions: int = 5,
        image_types: List[str] = None
    ) -> Dict:
        """
        Genera sugerencias de imágenes para un producto.
        
        Args:
            description_data: Datos de la descripción
            num_suggestions: Número de sugerencias
            image_types: Tipos de imágenes (hero, lifestyle, detail, etc.)
        
        Returns:
            Dict con sugerencias de imágenes
        """
        if image_types is None:
            image_types = ['hero', 'lifestyle', 'detail', 'benefit', 'comparison']
        
        product_name = description_data.get('product_name', '')
        product_type = description_data.get('product_type', '')
        key_benefits = description_data.get('key_benefits', [])
        description = description_data.get('description', '')
        
        suggestions = {}
        
        for img_type in image_types[:num_suggestions]:
            suggestion = self._generate_image_suggestion(
                product_name,
                product_type,
                key_benefits,
                description,
                img_type
            )
            suggestions[img_type] = suggestion
        
        return {
            'product_name': product_name,
            'suggestions': suggestions,
            'total_suggestions': len(suggestions),
            'generated_at': __import__('datetime').datetime.now().isoformat()
        }
    
    def _generate_image_suggestion(
        self,
        product_name: str,
        product_type: str,
        key_benefits: List[str],
        description: str,
        image_type: str
    ) -> Dict:
        """Genera una sugerencia específica de imagen."""
        
        type_prompts = {
            'hero': 'Imagen principal del producto destacado, fondo limpio, iluminación profesional',
            'lifestyle': 'Producto en uso real, contexto natural, personas usando el producto',
            'detail': 'Close-up de características específicas, texturas, materiales',
            'benefit': 'Imagen que demuestra un beneficio clave del producto',
            'comparison': 'Comparación visual con productos similares o antes/después',
            'packaging': 'Producto en su empaque, diseño de packaging',
            'infographic': 'Infografía con datos y beneficios del producto'
        }
        
        base_prompt = type_prompts.get(image_type, 'Imagen del producto')
        
        system_prompt = """Eres un experto en fotografía de productos y generación de imágenes para e-commerce.
Genera descripciones detalladas de imágenes que:
1. Sean visualmente atractivas y profesionales
2. Destaquen las características del producto
3. Generen deseo de compra
4. Sean optimizadas para conversión
5. Incluyan detalles técnicos (iluminación, composición, estilo)
"""
        
        prompt = f"""Genera una descripción detallada para una imagen de tipo "{image_type}" del siguiente producto:

**Producto**: {product_name}
**Tipo**: {product_type}
**Beneficios clave**: {', '.join(key_benefits[:3])}
**Descripción**: {description[:300]}

Tipo de imagen: {base_prompt}

Proporciona:
1. Descripción detallada de la imagen (qué mostrar)
2. Estilo y estética recomendada
3. Composición y encuadre
4. Iluminación y colores
5. Elementos a incluir/excluir
6. Prompt optimizado para DALL-E/Midjourney
"""
        
        try:
            result = self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            content = result['content'].strip()
            
            # Extraer prompt para generación
            dalle_prompt = self._extract_dalle_prompt(content, product_name, image_type)
            
            return {
                'image_type': image_type,
                'description': content,
                'dalle_prompt': dalle_prompt,
                'midjourney_prompt': self._generate_midjourney_prompt(dalle_prompt),
                'priority': 'high' if image_type == 'hero' else 'medium',
                'use_cases': self._get_use_cases(image_type)
            }
        except Exception as e:
            logger.error(f"Error generando sugerencia de imagen: {str(e)}")
            return {
                'image_type': image_type,
                'error': str(e)
            }
    
    def _extract_dalle_prompt(self, description: str, product_name: str, image_type: str) -> str:
        """Extrae o genera prompt optimizado para DALL-E."""
        # Buscar prompt en la descripción
        if 'prompt:' in description.lower() or 'dalle' in description.lower():
            lines = description.split('\n')
            for line in lines:
                if 'prompt' in line.lower() or 'dalle' in line.lower():
                    return line.split(':', 1)[-1].strip()
        
        # Generar prompt básico
        prompt = f"Professional product photography of {product_name}"
        
        if image_type == 'hero':
            prompt += ", white background, studio lighting, high quality"
        elif image_type == 'lifestyle':
            prompt += ", in natural setting, people using product, lifestyle photography"
        elif image_type == 'detail':
            prompt += ", close-up, macro photography, detailed textures"
        
        return prompt
    
    def _generate_midjourney_prompt(self, dalle_prompt: str) -> str:
        """Convierte prompt de DALL-E a formato Midjourney."""
        # Midjourney usa formato similar pero con parámetros específicos
        mj_prompt = dalle_prompt
        
        # Agregar parámetros comunes de Midjourney
        mj_prompt += " --ar 16:9 --v 6 --style raw"
        
        return mj_prompt
    
    def _get_use_cases(self, image_type: str) -> List[str]:
        """Obtiene casos de uso para un tipo de imagen."""
        use_cases_map = {
            'hero': ['Página de producto principal', 'Thumbnail en catálogo', 'Banner promocional'],
            'lifestyle': ['Marketing en redes sociales', 'Email marketing', 'Landing pages'],
            'detail': ['Zoom de producto', 'Galería de detalles', 'Especificaciones visuales'],
            'benefit': ['Marketing de beneficios', 'Comparativas', 'Educación del cliente'],
            'comparison': ['Páginas de comparación', 'Guías de compra', 'Contenido educativo']
        }
        
        return use_cases_map.get(image_type, ['Uso general'])






