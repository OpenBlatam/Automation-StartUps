"""
Generación de contenido para redes sociales basado en descripciones de productos.

Incluye:
- Posts para Instagram
- Tweets para Twitter/X
- Posts para Facebook
- Contenido para LinkedIn
- Hashtags optimizados
"""

import logging
from typing import Dict, List, Optional
from product_description_generator import LLMClient

logger = logging.getLogger(__name__)


class SocialContentGenerator:
    """Generador de contenido para redes sociales."""
    
    PLATFORM_SPECS = {
        'instagram': {
            'max_length': 2200,
            'hashtags_count': 10,
            'tone': 'visual, engaging, aspirational',
            'format': 'caption'
        },
        'twitter': {
            'max_length': 280,
            'hashtags_count': 2,
            'tone': 'concise, witty, engaging',
            'format': 'tweet'
        },
        'facebook': {
            'max_length': 5000,
            'hashtags_count': 5,
            'tone': 'conversational, friendly',
            'format': 'post'
        },
        'linkedin': {
            'max_length': 3000,
            'hashtags_count': 5,
            'tone': 'professional, informative',
            'format': 'post'
        }
    }
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def generate_social_content(
        self,
        description_data: Dict,
        platform: str,
        content_type: str = 'post',
        include_hashtags: bool = True
    ) -> Dict:
        """
        Genera contenido para redes sociales.
        
        Args:
            description_data: Datos de la descripción del producto
            platform: Plataforma ('instagram', 'twitter', 'facebook', 'linkedin')
            content_type: Tipo de contenido ('post', 'story', 'reel')
            include_hashtags: Incluir hashtags optimizados
        
        Returns:
            Dict con contenido generado
        """
        if platform not in self.PLATFORM_SPECS:
            raise ValueError(f"Plataforma no soportada: {platform}")
        
        specs = self.PLATFORM_SPECS[platform]
        product_name = description_data.get('product_name', '')
        description = description_data.get('description', '')
        key_benefits = description_data.get('key_benefits', [])
        
        # Generar contenido
        system_prompt = f"""Eres un experto en marketing de redes sociales especializado en {platform}.
Genera contenido {specs['format']} que:
1. Sea {specs['tone']}
2. Destaque los beneficios clave del producto
3. Genere engagement y conversión
4. Se adapte al formato de {platform}
5. Máximo {specs['max_length']} caracteres
"""
        
        prompt = f"""Genera un {specs['format']} para {platform} sobre este producto:

**Producto**: {product_name}
**Descripción**: {description[:500]}
**Beneficios clave**: {', '.join(key_benefits[:3])}

Genera contenido que sea {specs['tone']} y optimizado para {platform}.
"""
        
        try:
            result = self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.8,
                max_tokens=min(specs['max_length'] // 2, 500)
            )
            
            content = result['content'].strip()
            
            # Generar hashtags si se requiere
            hashtags = []
            if include_hashtags:
                hashtags = self._generate_hashtags(
                    description_data,
                    platform,
                    specs['hashtags_count']
                )
            
            return {
                'platform': platform,
                'content_type': content_type,
                'content': content,
                'hashtags': hashtags,
                'hashtags_text': ' '.join(hashtags) if hashtags else '',
                'full_text': f"{content}\n\n{' '.join(hashtags)}" if hashtags else content,
                'character_count': len(content),
                'with_hashtags_count': len(f"{content}\n\n{' '.join(hashtags)}") if hashtags else len(content),
                'metadata': {
                    'generated_at': __import__('datetime').datetime.now().isoformat(),
                    'provider': result.get('provider'),
                    'model': result.get('model')
                }
            }
        except Exception as e:
            logger.error(f"Error generando contenido social: {str(e)}")
            raise
    
    def generate_multiple_platforms(self, description_data: Dict, platforms: List[str] = None) -> Dict:
        """
        Genera contenido para múltiples plataformas.
        
        Args:
            description_data: Datos de la descripción
            platforms: Lista de plataformas (None para todas)
        
        Returns:
            Dict con contenido por plataforma
        """
        if platforms is None:
            platforms = list(self.PLATFORM_SPECS.keys())
        
        results = {}
        for platform in platforms:
            try:
                results[platform] = self.generate_social_content(description_data, platform)
            except Exception as e:
                logger.error(f"Error generando para {platform}: {str(e)}")
                results[platform] = {'error': str(e)}
        
        return results
    
    def _generate_hashtags(self, description_data: Dict, platform: str, count: int) -> List[str]:
        """Genera hashtags optimizados."""
        keywords = description_data.get('seo_keywords', [])
        product_type = description_data.get('product_type', '')
        product_name = description_data.get('product_name', '')
        
        hashtags = []
        
        # Agregar keywords principales
        for keyword in keywords[:count//2]:
            hashtag = '#' + keyword.replace(' ', '').replace('-', '')
            if len(hashtag) <= 30:  # Límite razonable
                hashtags.append(hashtag)
        
        # Agregar hashtags genéricos según plataforma
        generic_hashtags = {
            'instagram': ['#producto', '#nuevo', '#oferta'],
            'twitter': ['#producto', '#nuevo'],
            'facebook': ['#producto', '#nuevo'],
            'linkedin': ['#producto', '#innovación']
        }
        
        remaining = count - len(hashtags)
        if remaining > 0:
            hashtags.extend(generic_hashtags.get(platform, [])[:remaining])
        
        return hashtags[:count]


class CompetitorScraper:
    """Scraper básico para análisis de competencia."""
    
    @staticmethod
    def extract_competitor_data(url: str) -> Optional[Dict]:
        """
        Extrae datos básicos de un producto competidor.
        
        Args:
            url: URL del producto competidor
        
        Returns:
            Dict con datos extraídos o None
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer título
            title = None
            title_tag = soup.find('h1') or soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
            
            # Extraer descripción
            description = None
            desc_selectors = [
                'meta[name="description"]',
                '.product-description',
                '#product-description',
                '[class*="description"]'
            ]
            
            for selector in desc_selectors:
                element = soup.select_one(selector)
                if element:
                    if element.name == 'meta':
                        description = element.get('content', '').strip()
                    else:
                        description = element.get_text().strip()
                    if description:
                        break
            
            # Extraer precio
            price = None
            price_selectors = [
                '.price',
                '[class*="price"]',
                '[data-price]'
            ]
            
            for selector in price_selectors:
                element = soup.select_one(selector)
                if element:
                    price_text = element.get_text().strip()
                    # Extraer números
                    import re
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_match:
                        price = price_match.group()
                    break
            
            return {
                'url': url,
                'title': title,
                'description': description[:1000] if description else None,
                'price': price,
                'extracted_at': __import__('datetime').datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de {url}: {str(e)}")
            return None
    
    @staticmethod
    def analyze_competitor_descriptions(competitor_urls: List[str]) -> Dict:
        """
        Analiza múltiples competidores.
        
        Args:
            competitor_urls: Lista de URLs de competidores
        
        Returns:
            Dict con análisis agregado
        """
        competitor_data = []
        
        for url in competitor_urls:
            data = CompetitorScraper.extract_competitor_data(url)
            if data:
                competitor_data.append(data)
        
        if not competitor_data:
            return {
                'competitors_analyzed': 0,
                'message': 'No se pudieron extraer datos de competidores'
            }
        
        # Análisis agregado
        all_titles = [c['title'] for c in competitor_data if c.get('title')]
        all_descriptions = [c['description'] for c in competitor_data if c.get('description')]
        
        return {
            'competitors_analyzed': len(competitor_data),
            'competitor_data': competitor_data,
            'common_keywords': CompetitorScraper._extract_common_keywords(all_titles + all_descriptions),
            'avg_description_length': sum(len(d) for d in all_descriptions) / len(all_descriptions) if all_descriptions else 0,
            'price_range': CompetitorScraper._get_price_range(competitor_data)
        }
    
    @staticmethod
    def _extract_common_keywords(texts: List[str]) -> List[str]:
        """Extrae keywords comunes."""
        from collections import Counter
        import re
        
        all_words = []
        for text in texts:
            if text:
                words = re.findall(r'\b\w{4,}\b', text.lower())
                all_words.extend(words)
        
        counter = Counter(all_words)
        return [word for word, count in counter.most_common(10)]
    
    @staticmethod
    def _get_price_range(competitor_data: List[Dict]) -> Dict:
        """Obtiene rango de precios."""
        prices = []
        for data in competitor_data:
            if data.get('price'):
                try:
                    price = float(data['price'].replace(',', ''))
                    prices.append(price)
                except:
                    pass
        
        if prices:
            return {
                'min': min(prices),
                'max': max(prices),
                'avg': sum(prices) / len(prices)
            }
        return {}






