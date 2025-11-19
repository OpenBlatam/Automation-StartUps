#!/usr/bin/env python3
"""
Campaign Content Generator with AI
Genera contenido optimizado para campañas usando IA
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any


class CampaignContentGenerator:
    """
    Generador de contenido para campañas usando IA
    Genera captions, hashtags y variaciones optimizadas
    """
    
    def __init__(self, openai_api_key: str, n8n_base_url: str = ""):
        self.openai_api_key = openai_api_key
        self.n8n_base_url = n8n_base_url.rstrip('/')
        self.openai_base_url = "https://api.openai.com/v1"
    
    def generate_teaser_content(
        self,
        product_config: Dict[str, Any],
        style: str = "engaging"
    ) -> Dict[str, Any]:
        """
        Genera contenido para Día 1 (Teaser)
        
        Args:
            product_config: Configuración del producto
            style: Estilo del contenido (engaging, professional, casual)
        
        Returns:
            Dict con caption, hashtags y variaciones
        """
        prompt = self._build_teaser_prompt(product_config, style)
        content = self._call_openai(prompt)
        
        return {
            "day": 1,
            "type": "teaser",
            "caption": content.get("caption", ""),
            "hashtags": content.get("hashtags", []),
            "variations": content.get("variations", []),
            "style": style,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_demo_content(
        self,
        product_config: Dict[str, Any],
        style: str = "informative"
    ) -> Dict[str, Any]:
        """
        Genera contenido para Día 2 (Demo)
        
        Args:
            product_config: Configuración del producto
            style: Estilo del contenido
        
        Returns:
            Dict con caption, hashtags y variaciones
        """
        prompt = self._build_demo_prompt(product_config, style)
        content = self._call_openai(prompt)
        
        return {
            "day": 2,
            "type": "demo",
            "caption": content.get("caption", ""),
            "hashtags": content.get("hashtags", []),
            "variations": content.get("variations", []),
            "cta": content.get("cta", ""),
            "style": style,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_offer_content(
        self,
        product_config: Dict[str, Any],
        style: str = "urgent"
    ) -> Dict[str, Any]:
        """
        Genera contenido para Día 3 (Oferta)
        
        Args:
            product_config: Configuración del producto
            style: Estilo del contenido
        
        Returns:
            Dict con caption, hashtags y variaciones
        """
        prompt = self._build_offer_prompt(product_config, style)
        content = self._call_openai(prompt)
        
        return {
            "day": 3,
            "type": "offer",
            "caption": content.get("caption", ""),
            "hashtags": content.get("hashtags", []),
            "variations": content.get("variations", []),
            "urgency": content.get("urgency", "high"),
            "style": style,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_ab_variations(
        self,
        base_content: Dict[str, Any],
        num_variations: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Genera variaciones A/B del contenido base
        
        Args:
            base_content: Contenido base
            num_variations: Número de variaciones
        
        Returns:
            Lista de variaciones
        """
        variations = []
        
        for i in range(num_variations):
            prompt = f"""Genera una variación del siguiente contenido para A/B testing.
Mantén el mismo mensaje pero cambia el tono, estructura o enfoque.

Contenido original:
{base_content.get('caption', '')}

Variación {i+1}:"""
            
            variation_content = self._call_openai(prompt)
            
            variations.append({
                "variation": i + 1,
                "caption": variation_content.get("caption", ""),
                "hashtags": base_content.get("hashtags", []),
                "differences": variation_content.get("differences", [])
            })
        
        return variations
    
    def optimize_hashtags(
        self,
        base_hashtags: List[str],
        platform: str = "instagram",
        max_hashtags: int = 20
    ) -> List[str]:
        """
        Optimiza hashtags para máxima visibilidad
        
        Args:
            base_hashtags: Hashtags base
            platform: Plataforma objetivo
            max_hashtags: Máximo de hashtags
        
        Returns:
            Lista optimizada de hashtags
        """
        prompt = f"""Optimiza los siguientes hashtags para {platform}.
Incluye hashtags trending, específicos y de nicho.
Máximo {max_hashtags} hashtags.

Hashtags base:
{', '.join(base_hashtags)}

Hashtags optimizados:"""
        
        response = self._call_openai(prompt)
        optimized = response.get("hashtags", base_hashtags)
        
        # Limitar cantidad
        return optimized[:max_hashtags]
    
    def _build_teaser_prompt(self, product_config: Dict[str, Any], style: str) -> str:
        """Construye prompt para teaser"""
        return f"""Genera un caption de Instagram para un teaser de lanzamiento de producto.
Estilo: {style}
Producto: {product_config.get('name', 'Nuevo Producto')}
Problema que resuelve: {product_config.get('problem', 'Problema específico')}
Beneficios: {', '.join(product_config.get('benefits', []))}

El caption debe:
- Crear FOMO (Fear Of Missing Out)
- Generar curiosidad
- Incluir un CTA para comentar "SÍ"
- Ser entre 150-250 palabras
- Incluir emojis estratégicos
- Terminar con un hook

Genera también:
- 15-20 hashtags relevantes
- 2 variaciones del caption"""
    
    def _build_demo_prompt(self, product_config: Dict[str, Any], style: str) -> str:
        """Construye prompt para demo"""
        return f"""Genera un caption de Instagram para mostrar un demo del producto.
Estilo: {style}
Producto: {product_config.get('name', 'Nuevo Producto')}
Beneficios principales: {', '.join(product_config.get('benefits', []))}
Link CTA: {product_config.get('cta_link', 'https://yoursite.com')}

El caption debe:
- Explicar claramente qué es el producto
- Destacar los beneficios principales
- Incluir un CTA claro al link
- Ser entre 200-300 palabras
- Incluir emojis
- Invitar a hacer preguntas

Genera también:
- 15-20 hashtags relevantes
- 2 variaciones del caption
- Un CTA optimizado"""
    
    def _build_offer_prompt(self, product_config: Dict[str, Any], style: str) -> str:
        """Construye prompt para oferta"""
        discount = product_config.get('discount_percentage', 20)
        return f"""Genera un caption de Instagram para una oferta de lanzamiento.
Estilo: {style} (con urgencia)
Producto: {product_config.get('name', 'Nuevo Producto')}
Descuento: {discount}%
Precio normal: ${product_config.get('normal_price', 0)}
Precio especial: ${product_config.get('special_price', 0)}
Bonuses: {', '.join(product_config.get('bonuses', []))}
Unidades disponibles: {product_config.get('units_available', 100)}
Link CTA: {product_config.get('cta_link', 'https://yoursite.com')}

El caption debe:
- Crear urgencia (tiempo limitado, unidades limitadas)
- Destacar el descuento y valor
- Incluir todos los bonuses
- Tener un CTA muy claro
- Ser entre 200-250 palabras
- Usar emojis de urgencia (⚡, 🔥, ⏰)
- Generar FOMO máximo

Genera también:
- 15-20 hashtags relevantes
- 2 variaciones del caption
- Nivel de urgencia (high/medium/low)"""
    
    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """
        Llama a la API de OpenAI para generar contenido
        
        Nota: En producción, esto usaría la API real de OpenAI
        Por ahora, retorna contenido de ejemplo estructurado
        """
        # En producción, esto haría una llamada real a OpenAI
        # Por ahora, retornamos estructura de ejemplo
        
        headers = {
            'Authorization': f'Bearer {self.openai_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un experto en copywriting para redes sociales, especializado en marketing de lanzamiento de productos."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.8,
            "max_tokens": 1000
        }
        
        try:
            # Llamada real a OpenAI (descomentar en producción)
            # response = requests.post(
            #     f"{self.openai_base_url}/chat/completions",
            #     headers=headers,
            #     json=payload
            # )
            # response.raise_for_status()
            # content = response.json()["choices"][0]["message"]["content"]
            
            # Por ahora, retornamos estructura de ejemplo
            content = self._parse_ai_response(prompt)
            
            return content
        except Exception as e:
            # Fallback a contenido de ejemplo
            return self._parse_ai_response(prompt)
    
    def _parse_ai_response(self, prompt: str) -> Dict[str, Any]:
        """Parsea respuesta de IA (simplificado)"""
        # En producción, esto parsearía la respuesta real de OpenAI
        # Por ahora, retornamos estructura de ejemplo
        
        if "teaser" in prompt.lower():
            return {
                "caption": "🔮 Algo revolucionario está por llegar...\n\n¿Te has preguntado alguna vez por qué [PROBLEMA] sigue siendo tan complicado?\n\nDespués de meses trabajando en esto, finalmente encontramos la solución.\n\nEn 48 horas te mostraremos cómo puedes transformar tu [ÁREA].\n\n¿Estás listo para el cambio? 👇\nComenta \"SÍ\" si quieres ser de los primeros 🔔",
                "hashtags": ["#Lanzamiento", "#NuevoProducto", "#Próximamente", "#Innovación"],
                "variations": [
                    "Variación 1 del caption...",
                    "Variación 2 del caption..."
                ]
            }
        elif "demo" in prompt.lower():
            return {
                "caption": "🎉 ¡Ya está aquí! Te presentamos [PRODUCTO]\n\nDespués de meses de desarrollo, finalmente puedes:\n\n✨ Beneficio 1\n✨ Beneficio 2\n✨ Beneficio 3\n\n👉 Mira cómo funciona en el video 👆\n\n🔗 Link para ver más detalles\n\n💬 ¿Preguntas? Comenta abajo 👇",
                "hashtags": ["#Demo", "#ProductoNuevo", "#Lanzamiento"],
                "variations": [
                    "Variación 1 del caption...",
                    "Variación 2 del caption..."
                ],
                "cta": "🔗 Ver más detalles aquí: [LINK]"
            }
        else:  # offer
            return {
                "caption": "⚡ OFERTA DE PRE-LANZAMIENTO ⚡\n\n💰 Precio especial: [DESCUENTO]% de descuento\n\n✨ Incluye:\n• [PRODUCTO]\n• Bonus exclusivo\n• Acceso anticipado\n\n⏰ Solo por 48 horas\n⏰ Solo [NÚMERO] unidades disponibles\n\n🔗 [LINK] para aprovechar ahora",
                "hashtags": ["#Oferta", "#Descuento", "#Lanzamiento"],
                "variations": [
                    "Variación 1 del caption...",
                    "Variación 2 del caption..."
                ],
                "urgency": "high"
            }


def main():
    """Ejemplo de uso"""
    generator = CampaignContentGenerator(
        openai_api_key=os.getenv("OPENAI_API_KEY", "your_api_key"),
        n8n_base_url="https://your-n8n.com"
    )
    
    # Configuración del producto
    product_config = {
        "name": "Mi Nuevo Producto",
        "benefits": [
            "Ahorra 10 horas semanales",
            "Aumenta productividad en 300%",
            "Fácil de usar"
        ],
        "problem": "Gestión de tareas complicada",
        "discount_percentage": 25,
        "normal_price": 199,
        "special_price": 149,
        "bonuses": ["Bonus 1", "Bonus 2"],
        "units_available": 50,
        "cta_link": "https://yoursite.com/launch"
    }
    
    # Generar contenido para cada día
    print("=== Generando Contenido Día 1 (Teaser) ===")
    teaser = generator.generate_teaser_content(product_config, style="engaging")
    print(json.dumps(teaser, indent=2, ensure_ascii=False))
    
    print("\n=== Generando Contenido Día 2 (Demo) ===")
    demo = generator.generate_demo_content(product_config, style="informative")
    print(json.dumps(demo, indent=2, ensure_ascii=False))
    
    print("\n=== Generando Contenido Día 3 (Oferta) ===")
    offer = generator.generate_offer_content(product_config, style="urgent")
    print(json.dumps(offer, indent=2, ensure_ascii=False))
    
    # Generar variaciones A/B
    print("\n=== Generando Variaciones A/B ===")
    variations = generator.generate_ab_variations(teaser, num_variations=3)
    print(json.dumps(variations, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()









