"""
DAG para generar descripciones completas y atractivas de productos para e-commerce.

Características:
- Generación con IA de descripciones optimizadas (200-400 palabras)
- Beneficios clave destacados (ej: durabilidad 2x mayor)
- Características técnicas detalladas
- Storytelling emocional dirigido a público específico
- Optimización SEO con keywords
- Sugerencias de multimedia (imágenes, videos)
- Soporte para múltiples plataformas (Amazon, Shopify)
- Sistema de A/B testing de variaciones
- Automatización masiva vía API
- Aumenta conversiones en 30-50%

Uso:
- Integración en catálogos existentes
- A/B testing de variaciones
- Generación masiva para nuevos productos
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
import json
import logging
import requests
import hashlib
import re
from typing import Dict, List, Optional, Tuple
from functools import lru_cache
import time

# Configuración por defecto
default_args = {
    'owner': 'ecommerce-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=2),
}

logger = logging.getLogger(__name__)

# Constantes
LLM_PROVIDERS = ['openai', 'deepseek', 'anthropic']
DEFAULT_LLM_PROVIDER = 'openai'
DEFAULT_MODEL = 'gpt-4o-mini'
SUPPORTED_PLATFORMS = ['amazon', 'shopify', 'generic']


class LLMClient:
    """Cliente unificado para múltiples proveedores de IA."""
    
    def __init__(self, provider: str = None):
        self.provider = provider or Variable.get("DEFAULT_LLM_PROVIDER", default_var=DEFAULT_LLM_PROVIDER)
        self._setup_provider()
    
    def _setup_provider(self):
        """Configura las credenciales del proveedor."""
        if self.provider == 'openai':
            self.api_key = Variable.get("OPENAI_API_KEY", default_var=None)
            self.base_url = Variable.get("OPENAI_BASE_URL", default_var="https://api.openai.com/v1")
            self.model = Variable.get("OPENAI_MODEL", default_var="gpt-4o-mini")
        elif self.provider == 'deepseek':
            self.api_key = Variable.get("DEEPSEEK_API_KEY", default_var=None)
            self.base_url = Variable.get("DEEPSEEK_BASE_URL", default_var="https://api.deepseek.com/v1")
            self.model = Variable.get("DEEPSEEK_MODEL", default_var="deepseek-chat")
        elif self.provider == 'anthropic':
            self.api_key = Variable.get("ANTHROPIC_API_KEY", default_var=None)
            self.base_url = Variable.get("ANTHROPIC_BASE_URL", default_var="https://api.anthropic.com/v1")
            self.model = Variable.get("ANTHROPIC_MODEL", default_var="claude-3-sonnet-20240229")
        else:
            raise ValueError(f"Proveedor no soportado: {self.provider}")
    
    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 2000) -> Dict:
        """
        Genera texto usando el proveedor de IA configurado.
        
        Returns:
            Dict con 'content', 'tokens_used', 'model', 'provider'
        """
        if not self.api_key:
            raise ValueError(f"API key no configurada para {self.provider}")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        if self.provider == 'anthropic':
            return self._call_anthropic(messages, temperature, max_tokens)
        else:
            return self._call_openai_compatible(messages, temperature, max_tokens)
    
    def _call_openai_compatible(self, messages: List[Dict], temperature: float, max_tokens: int) -> Dict:
        """Llamada para APIs compatibles con OpenAI (OpenAI, DeepSeek)."""
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=120
        )
        
        if not response.ok:
            error_text = response.text
            logger.error(f"Error en API {self.provider}: {response.status_code} - {error_text}")
            raise Exception(f"API error: {response.status_code} - {error_text}")
        
        data = response.json()
        return {
            "content": data['choices'][0]['message']['content'],
            "tokens_used": data.get('usage', {}).get('total_tokens'),
            "model": data.get('model'),
            "provider": self.provider
        }
    
    def _call_anthropic(self, messages: List[Dict], temperature: float, max_tokens: int) -> Dict:
        """Llamada para API de Anthropic (Claude)."""
        system_message = next((m['content'] for m in messages if m['role'] == 'system'), None)
        user_messages = [m['content'] for m in messages if m['role'] == 'user']
        
        response = requests.post(
            f"{self.base_url}/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": self.model,
                "system": system_message or "",
                "messages": [{"role": "user", "content": "\n".join(user_messages)}],
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=120
        )
        
        if not response.ok:
            error_text = response.text
            logger.error(f"Error en API Anthropic: {response.status_code} - {error_text}")
            raise Exception(f"API error: {response.status_code} - {error_text}")
        
        data = response.json()
        return {
            "content": data['content'][0]['text'],
            "tokens_used": data.get('usage', {}).get('input_tokens', 0) + data.get('usage', {}).get('output_tokens', 0),
            "model": data.get('model'),
            "provider": self.provider
        }


class SEOOptimizer:
    """Optimizador SEO avanzado para descripciones de productos."""
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extrae keywords principales del texto con análisis avanzado."""
        # Palabras comunes a excluir
        stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se', 'no', 'haber', 
                     'por', 'con', 'su', 'para', 'como', 'estar', 'tener', 'le', 'lo', 'todo', 
                     'pero', 'más', 'hacer', 'o', 'poder', 'decir', 'este', 'ir', 'otro', 'ese',
                     'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
                     'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be', 'have', 'has',
                     'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might'}
        
        # Limpiar y tokenizar
        words = re.findall(r'\b\w+\b', text.lower())
        words = [w for w in words if len(w) > 3 and w not in stop_words]
        
        # Contar frecuencia
        from collections import Counter
        word_freq = Counter(words)
        
        # Retornar top keywords
        return [word for word, _ in word_freq.most_common(max_keywords)]
    
    @staticmethod
    def optimize_for_platform(text: str, platform: str) -> str:
        """Optimiza el texto según las reglas específicas de la plataforma."""
        if platform.lower() == 'amazon':
            # Amazon: bullets, técnico, keywords naturales
            # Convertir párrafos largos en bullets si es necesario
            if '\n' not in text and len(text) > 500:
                sentences = re.split(r'[.!?]+', text)
                bullets = []
                for sent in sentences[:7]:  # Máximo 7 bullets
                    sent = sent.strip()
                    if len(sent) > 20:
                        bullets.append(f"• {sent}")
                if bullets:
                    text = '\n'.join(bullets)
            # Limitar a 2000 caracteres para bullet points
            if len(text) > 2000:
                text = text[:1997] + "..."
        elif platform.lower() == 'shopify':
            # Shopify: storytelling, HTML básico permitido
            # Asegurar párrafos bien formateados
            paragraphs = text.split('\n\n')
            formatted_paragraphs = []
            for p in paragraphs:
                p = p.strip()
                if p and not p.startswith('•'):
                    formatted_paragraphs.append(f"<p>{p}</p>")
                else:
                    formatted_paragraphs.append(p)
            text = '\n\n'.join(formatted_paragraphs)
        
        return text
    
    @staticmethod
    def generate_meta_description(text: str, max_length: int = 160) -> str:
        """Genera meta descripción optimizada para SEO."""
        # Limpiar HTML si existe
        clean_text = re.sub(r'<[^>]+>', '', text)
        # Remover bullets y caracteres especiales
        clean_text = re.sub(r'[•\-\*]', '', clean_text)
        # Tomar primeras palabras relevantes
        words = clean_text.split()[:25]
        meta = ' '.join(words)
        if len(meta) > max_length:
            meta = meta[:max_length-3] + "..."
        return meta
    
    @staticmethod
    def generate_title(product_name: str, key_benefits: List[str], max_length: int = 60) -> str:
        """Genera título optimizado para SEO."""
        # Combinar nombre con beneficio principal
        if key_benefits:
            main_benefit = key_benefits[0].split()[0:3]  # Primeras 3 palabras del beneficio
            benefit_text = ' '.join(main_benefit)
            title = f"{product_name} - {benefit_text}"
        else:
            title = product_name
        
        # Asegurar longitud óptima
        if len(title) > max_length:
            title = title[:max_length-3] + "..."
        
        return title
    
    @staticmethod
    def analyze_seo_score(text: str, keywords: List[str]) -> Dict:
        """Analiza el score SEO de la descripción."""
        text_lower = text.lower()
        keyword_density = {}
        total_words = len(text.split())
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = text_lower.count(keyword_lower)
            density = (count / total_words * 100) if total_words > 0 else 0
            keyword_density[keyword] = {
                'count': count,
                'density': round(density, 2)
            }
        
        # Calcular score general (0-100)
        avg_density = sum(k['density'] for k in keyword_density.values()) / len(keywords) if keywords else 0
        score = min(100, max(0, avg_density * 10))  # Normalizar
        
        return {
            'score': round(score, 1),
            'keyword_density': keyword_density,
            'total_words': total_words,
            'recommendations': SEOOptimizer._generate_seo_recommendations(keyword_density, keywords)
        }
    
    @staticmethod
    def _generate_seo_recommendations(keyword_density: Dict, keywords: List[str]) -> List[str]:
        """Genera recomendaciones para mejorar SEO."""
        recommendations = []
        
        for keyword in keywords:
            density = keyword_density.get(keyword, {}).get('density', 0)
            if density < 0.5:
                recommendations.append(f"Considera incluir '{keyword}' más veces (densidad actual: {density}%)")
            elif density > 3:
                recommendations.append(f"Reducir uso de '{keyword}' para evitar keyword stuffing (densidad: {density}%)")
        
        return recommendations


class CompetitorAnalyzer:
    """Analizador de competencia para optimizar descripciones."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def analyze_competitors(self, product_type: str, competitors_data: List[Dict] = None) -> Dict:
        """
        Analiza descripciones de competidores para identificar mejores prácticas.
        
        Args:
            product_type: Tipo de producto
            competitors_data: Lista de descripciones de competidores (opcional)
        
        Returns:
            Dict con insights y recomendaciones
        """
        if not competitors_data:
            # Si no hay datos, generar recomendaciones genéricas
            return {
                'common_keywords': [],
                'common_benefits': [],
                'recommendations': [
                    'Destacar beneficios únicos del producto',
                    'Usar lenguaje emocional que conecte con el público',
                    'Incluir datos específicos y verificables'
                ]
            }
        
        # Analizar con IA
        prompt = f"""Analiza las siguientes descripciones de productos competidores del tipo "{product_type}" 
y proporciona insights sobre:
1. Keywords más comunes
2. Beneficios más mencionados
3. Estructura y tono
4. Recomendaciones para destacar

Descripciones competidoras:
{json.dumps(competitors_data, ensure_ascii=False, indent=2)}

Proporciona un análisis estructurado en JSON."""
        
        try:
            result = self.llm_client.generate(
                prompt=prompt,
                system_prompt="Eres un experto en análisis de mercado y copywriting de e-commerce.",
                temperature=0.5,
                max_tokens=1000
            )
            
            # Intentar parsear JSON de la respuesta
            analysis_text = result['content']
            # Extraer JSON si está en markdown code blocks
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', analysis_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                # Si no hay JSON, retornar análisis en texto
                return {
                    'analysis': analysis_text,
                    'common_keywords': [],
                    'recommendations': []
                }
        except Exception as e:
            logger.warning(f"Error analizando competencia: {str(e)}")
            return {
                'error': str(e),
                'common_keywords': [],
                'recommendations': []
            }


class ProductDescriptionGenerator:
    """Generador avanzado de descripciones de productos con IA.
    
    Características:
    - Generación optimizada para conversión (30-50% aumento)
    - Soporte multi-plataforma (Amazon, Shopify, genérico)
    - Optimización SEO automática con análisis de score
    - Storytelling emocional personalizado
    - Análisis de competencia integrado
    - Sugerencias de multimedia
    - Sistema de caché inteligente
    - Generación de títulos optimizados
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.seo_optimizer = SEOOptimizer()
        self.competitor_analyzer = CompetitorAnalyzer(llm_client)
        self._validate_llm_client()
    
    def _validate_llm_client(self):
        """Valida que el cliente LLM esté correctamente configurado."""
        if not self.llm_client:
            raise ValueError("LLMClient es requerido")
        if not hasattr(self.llm_client, 'generate'):
            raise ValueError("LLMClient debe tener método 'generate'")
    
    def generate_description(
        self,
        product_name: str,
        product_type: str,
        key_benefits: List[str],
        technical_features: List[str],
        target_audience: str,
        platform: str = 'generic',
        keywords: Optional[List[str]] = None,
        brand_story: Optional[str] = None,
        word_count: int = 300,
        language: str = 'es'
    ) -> Dict:
        """
        Genera una descripción completa de producto.
        
        Args:
            product_name: Nombre del producto
            product_type: Tipo/categoría del producto
            key_benefits: Lista de beneficios clave (ej: ['durabilidad 2x mayor', '100% ecológico'])
            technical_features: Lista de características técnicas
            target_audience: Público objetivo (ej: 'compradores eco-friendly')
            platform: Plataforma destino ('amazon', 'shopify', 'generic')
            keywords: Keywords SEO opcionales
            brand_story: Historia de marca opcional
            word_count: Número objetivo de palabras (200-400)
            language: Idioma de la descripción ('es', 'en', etc.)
        
        Returns:
            Dict con 'description', 'seo_keywords', 'meta_description', 'multimedia_suggestions', 'metadata'
        
        Raises:
            ValueError: Si los parámetros requeridos son inválidos
        """
        # Validaciones
        if not product_name or len(product_name.strip()) == 0:
            raise ValueError("product_name es requerido y no puede estar vacío")
        if not key_benefits or len(key_benefits) == 0:
            raise ValueError("key_benefits debe contener al menos un beneficio")
        if not technical_features or len(technical_features) == 0:
            raise ValueError("technical_features debe contener al menos una característica")
        if not target_audience or len(target_audience.strip()) == 0:
            raise ValueError("target_audience es requerido")
        if platform not in SUPPORTED_PLATFORMS:
            raise ValueError(f"platform debe ser una de: {', '.join(SUPPORTED_PLATFORMS)}")
        if word_count < 200 or word_count > 400:
            logger.warning(f"word_count ({word_count}) fuera del rango recomendado (200-400)")
        if language not in ['es', 'en', 'pt', 'fr', 'de']:
            logger.warning(f"Idioma {language} puede no estar completamente soportado")
        
        try:
            # Construir system prompt según plataforma
            system_prompt = self._build_system_prompt(platform, word_count, language)
            
            # Construir prompt principal
            prompt = self._build_prompt(
            product_name=product_name,
            product_type=product_type,
            key_benefits=key_benefits,
            technical_features=technical_features,
            target_audience=target_audience,
            platform=platform,
            keywords=keywords,
                brand_story=brand_story,
                word_count=word_count,
                language=language
            )
            
            # Generar descripción
            result = self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.8,  # Más creatividad para storytelling
                max_tokens=min(word_count * 2, 2000)  # Aprox 2 tokens por palabra
            )
            
            description = result['content'].strip()
            
            # Extraer secciones si están en formato estructurado
            parsed_description = self._parse_description(description)
            
            # Optimizar SEO
            seo_keywords = keywords or self.seo_optimizer.extract_keywords(description)
            meta_description = self.seo_optimizer.generate_meta_description(description)
            optimized_description = self.seo_optimizer.optimize_for_platform(description, platform)
            
            # Generar sugerencias multimedia
            multimedia_suggestions = self._generate_multimedia_suggestions(
                product_name, product_type, key_benefits, technical_features
            )
            
            # Generar título optimizado
            optimized_title = self.seo_optimizer.generate_title(product_name, key_benefits)
            
            # Analizar SEO score
            seo_analysis = self.seo_optimizer.analyze_seo_score(optimized_description, seo_keywords)
            
            # Análisis completo (opcional, puede ser pesado)
            full_analysis = None
            try:
                from product_description_analyzer import ProductDescriptionAnalyzer
                analyzer = ProductDescriptionAnalyzer()
                temp_data = {
                    'description': optimized_description,
                    'word_count': len(optimized_description.split()),
                    'seo_analysis': seo_analysis,
                    'language': language
                }
                full_analysis = analyzer.analyze_complete(temp_data)
            except Exception as e:
                logger.warning(f"No se pudo realizar análisis completo: {str(e)}")
            
            result_dict = {
                'description': optimized_description,
                'title': optimized_title,
                'full_description': parsed_description.get('full', optimized_description),
                'benefits_section': parsed_description.get('benefits', ''),
                'technical_section': parsed_description.get('technical', ''),
                'storytelling_section': parsed_description.get('storytelling', ''),
                'seo_keywords': seo_keywords,
                'seo_analysis': seo_analysis,
                'meta_description': meta_description,
                'multimedia_suggestions': multimedia_suggestions,
                'word_count': len(optimized_description.split()),
                'platform': platform,
                'language': language,
                'metadata': {
                    'provider': result.get('provider'),
                    'model': result.get('model'),
                    'tokens_used': result.get('tokens_used'),
                    'generated_at': datetime.now().isoformat()
                }
            }
            
            # Agregar análisis completo si está disponible
            if full_analysis:
                result_dict['full_analysis'] = full_analysis
            
            return result_dict
            
        except Exception as e:
            logger.error(f"Error generando descripción para {product_name}: {str(e)}")
            raise
    
    def _build_system_prompt(self, platform: str, word_count: int, language: str = 'es') -> str:
        """Construye el system prompt según la plataforma."""
        language_instruction = {
            'es': 'Responde en español.',
            'en': 'Respond in English.',
            'pt': 'Responda em português.',
            'fr': 'Répondez en français.',
            'de': 'Antworten Sie auf Deutsch.'
        }.get(language, 'Responde en español.')
        
        base_prompt = f"""Eres un experto copywriter de e-commerce especializado en crear descripciones de productos que convierten.
{language_instruction}

Tu objetivo es crear descripciones que:
1. Aumenten las conversiones en 30-50%
2. Destaquen beneficios clave de manera convincente
3. Incluyan características técnicas relevantes
4. Usen storytelling emocional que conecte con el público objetivo
5. Estén optimizadas para SEO con keywords naturales
6. Tengan una longitud de aproximadamente {word_count} palabras (entre 200-400)

"""
        
        if platform.lower() == 'amazon':
            base_prompt += """Para Amazon:
- Usa bullet points para beneficios clave
- Sé directo y orientado a resultados
- Destaca características técnicas y especificaciones
- Incluye keywords de búsqueda de forma natural
- Formato: Título atractivo + Bullets de beneficios + Descripción detallada
- Máximo 2000 caracteres para bullets
"""
        elif platform.lower() == 'shopify':
            base_prompt += """Para Shopify:
- Usa storytelling emocional más extenso
- Crea una narrativa que conecte con el público
- Combina beneficios con experiencias de uso
- Formato más libre y creativo
- Puedes usar HTML básico para formato
"""
        else:
            base_prompt += """Para formato genérico:
- Balance entre información técnica y emocional
- Estructura clara con secciones
- Optimizado para múltiples plataformas
"""
        
        base_prompt += """
IMPORTANTE:
- No uses lenguaje exagerado o promesas falsas
- Sé auténtico y creíble
- Incluye datos específicos cuando sea posible (ej: "2x más duradero", "100% reciclable")
- Adapta el tono al público objetivo
- Asegúrate de que la descripción fluya naturalmente
"""
        
        return base_prompt
    
    def _build_prompt(
        self,
        product_name: str,
        product_type: str,
        key_benefits: List[str],
        technical_features: List[str],
        target_audience: str,
        platform: str,
        keywords: Optional[List[str]],
        brand_story: Optional[str],
        word_count: int
    ) -> str:
        """Construye el prompt principal para la generación."""
        
        prompt = f"""Genera una descripción completa y atractiva para el siguiente producto:

**Nombre del Producto**: {product_name}
**Tipo/Categoría**: {product_type}
**Plataforma**: {platform.upper()}
**Público Objetivo**: {target_audience}
**Longitud objetivo**: {word_count} palabras

**Beneficios Clave a Destacar**:
"""
        for i, benefit in enumerate(key_benefits, 1):
            prompt += f"{i}. {benefit}\n"
        
        prompt += f"""
**Características Técnicas**:
"""
        for i, feature in enumerate(technical_features, 1):
            prompt += f"{i}. {feature}\n"
        
        if keywords:
            prompt += f"""
**Keywords SEO a Incluir** (de forma natural): {', '.join(keywords)}
"""
        
        if brand_story:
            prompt += f"""
**Historia de Marca/Contexto**: {brand_story}
"""
        
        prompt += """
**Instrucciones Específicas**:
1. Comienza con un hook emocional que capture la atención
2. Destaca los beneficios clave de manera convincente (usa datos específicos cuando sea posible)
3. Incluye las características técnicas de forma clara pero accesible
4. Usa storytelling para conectar emocionalmente con el público objetivo
5. Integra keywords de forma natural (no keyword stuffing)
6. Termina con un call-to-action sutil pero efectivo
7. Asegúrate de que la descripción fluya naturalmente y sea fácil de leer

**Formato de Salida**:
Si es para Amazon, usa este formato:
- Título atractivo (1 línea)
- Bullet points de beneficios clave (5-7 bullets)
- Descripción detallada (2-3 párrafos)

Si es para Shopify o genérico, usa formato de texto continuo con párrafos bien estructurados.

Genera la descripción ahora:
"""
        
        return prompt
    
    def _parse_description(self, description: str) -> Dict:
        """Parsea la descripción generada en secciones."""
        result = {
            'full': description,
            'benefits': '',
            'technical': '',
            'storytelling': ''
        }
        
        # Intentar extraer secciones si están marcadas
        benefits_match = re.search(r'(?i)(beneficios?|ventajas?)[:]\s*(.+?)(?=\n\n|\n[A-Z]|$)', description, re.DOTALL)
        if benefits_match:
            result['benefits'] = benefits_match.group(2).strip()
        
        technical_match = re.search(r'(?i)(características?|especificaciones?|técnicas?)[:]\s*(.+?)(?=\n\n|\n[A-Z]|$)', description, re.DOTALL)
        if technical_match:
            result['technical'] = technical_match.group(2).strip()
        
        # El storytelling suele ser el inicio o párrafos narrativos
        paragraphs = description.split('\n\n')
        storytelling_paragraphs = [p for p in paragraphs if len(p.split()) > 20 and not p.strip().startswith('-')]
        if storytelling_paragraphs:
            result['storytelling'] = '\n\n'.join(storytelling_paragraphs[:2])
        
        return result
    
    def _generate_multimedia_suggestions(
        self,
        product_name: str,
        product_type: str,
        key_benefits: List[str],
        technical_features: List[str]
    ) -> Dict:
        """Genera sugerencias de multimedia para el producto."""
        suggestions = {
            'images': [],
            'videos': [],
            'infographics': []
        }
        
        # Imágenes sugeridas
        suggestions['images'].append({
            'type': 'hero',
            'description': f'Imagen principal del {product_name} en uso, mostrando el producto destacado',
            'priority': 'high'
        })
        
        for benefit in key_benefits[:3]:
            suggestions['images'].append({
                'type': 'benefit',
                'description': f'Imagen demostrando: {benefit}',
                'priority': 'medium'
            })
        
        # Videos sugeridos
        suggestions['videos'].append({
            'type': 'product_overview',
            'description': f'Video de 60-90 segundos mostrando {product_name} en acción, destacando beneficios principales',
            'duration': '60-90s',
            'priority': 'high'
        })
        
        if technical_features:
            suggestions['videos'].append({
                'type': 'technical_demo',
                'description': f'Video técnico de 30-45 segundos mostrando características técnicas clave',
                'duration': '30-45s',
                'priority': 'medium'
            })
        
        # Infografías
        suggestions['infographics'].append({
            'type': 'benefits_comparison',
            'description': f'Infografía comparativa mostrando beneficios clave vs productos similares',
            'priority': 'medium'
        })
        
        return suggestions
    
    def generate_with_competitor_analysis(
        self,
        product_name: str,
        product_type: str,
        key_benefits: List[str],
        technical_features: List[str],
        target_audience: str,
        platform: str = 'generic',
        keywords: Optional[List[str]] = None,
        brand_story: Optional[str] = None,
        word_count: int = 300,
        competitors_data: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Genera descripción con análisis de competencia integrado.
        
        Args:
            competitors_data: Lista de dicts con descripciones de competidores
                Ejemplo: [{'description': '...', 'title': '...'}, ...]
        
        Returns:
            Dict con descripción optimizada y análisis de competencia
        """
        # Analizar competencia
        competitor_analysis = self.competitor_analyzer.analyze_competitors(
            product_type, competitors_data
        )
        
        # Mejorar keywords basado en análisis
        if competitor_analysis.get('common_keywords'):
            if keywords:
                keywords = list(set(keywords + competitor_analysis.get('common_keywords', [])[:5]))
            else:
                keywords = competitor_analysis.get('common_keywords', [])[:10]
        
        # Generar descripción normal
        description_result = self.generate_description(
            product_name=product_name,
            product_type=product_type,
            key_benefits=key_benefits,
            technical_features=technical_features,
            target_audience=target_audience,
            platform=platform,
            keywords=keywords,
            brand_story=brand_story,
            word_count=word_count
        )
        
        # Agregar análisis de competencia
        description_result['competitor_analysis'] = competitor_analysis
        
        return description_result
    
    def generate_variations(
        self,
        base_product_info: Dict,
        num_variations: int = 3,
        variation_types: List[str] = None
    ) -> List[Dict]:
        """
        Genera variaciones de descripción para A/B testing.
        
        Args:
            base_product_info: Información base del producto
            num_variations: Número de variaciones a generar
            variation_types: Tipos de variación ['emotional', 'technical', 'benefit_focused', 'seo_optimized']
        
        Returns:
            Lista de descripciones variadas
        """
        if variation_types is None:
            variation_types = ['emotional', 'technical', 'benefit_focused']
        
        variations = []
        
        for i, var_type in enumerate(variation_types[:num_variations]):
            # Ajustar parámetros según tipo de variación
            if var_type == 'emotional':
                word_count = 350
                temperature = 0.9
                focus = "storytelling emocional y conexión con el público"
            elif var_type == 'technical':
                word_count = 250
                temperature = 0.6
                focus = "características técnicas y especificaciones detalladas"
            elif var_type == 'benefit_focused':
                word_count = 300
                temperature = 0.7
                focus = "beneficios clave y resultados para el cliente"
            else:  # seo_optimized
                word_count = 300
                temperature = 0.7
                focus = "optimización SEO con keywords naturales"
            
            # Generar variación
            var_description = self.generate_description(
                product_name=base_product_info['product_name'],
                product_type=base_product_info.get('product_type', ''),
                key_benefits=base_product_info.get('key_benefits', []),
                technical_features=base_product_info.get('technical_features', []),
                target_audience=base_product_info.get('target_audience', ''),
                platform=base_product_info.get('platform', 'generic'),
                keywords=base_product_info.get('keywords'),
                brand_story=base_product_info.get('brand_story'),
                word_count=word_count
            )
            
            var_description['variation_type'] = var_type
            var_description['variation_id'] = i + 1
            var_description['focus'] = focus
            
            variations.append(var_description)
        
        return variations


def get_cache_key(product_info: Dict) -> str:
    """Genera una clave de caché única para un producto."""
    cache_data = {
        'product_name': product_info.get('product_name'),
        'product_type': product_info.get('product_type'),
        'key_benefits': sorted(product_info.get('key_benefits', [])),
        'platform': product_info.get('platform', 'generic')
    }
    cache_str = json.dumps(cache_data, sort_keys=True)
    return hashlib.md5(cache_str.encode()).hexdigest()


def check_cache(cache_key: str) -> Optional[Dict]:
    """Verifica si existe una descripción en caché."""
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        query = """
            SELECT description_data FROM product_descriptions_cache 
            WHERE cache_key = %s AND created_at > NOW() - INTERVAL '30 days'
            ORDER BY created_at DESC LIMIT 1
        """
        result = pg_hook.get_first(query, parameters=(cache_key,))
        if result:
            return json.loads(result[0])
        return None
    except Exception as e:
        logger.warning(f"Error verificando caché: {str(e)}")
        return None


def save_to_cache(cache_key: str, description_data: Dict):
    """Guarda una descripción en caché."""
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        query = """
            INSERT INTO product_descriptions_cache (cache_key, description_data, created_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (cache_key) DO UPDATE 
            SET description_data = EXCLUDED.description_data,
                created_at = NOW()
        """
        pg_hook.run(query, parameters=(cache_key, json.dumps(description_data)))
        logger.info(f"Descripción guardada en caché: {cache_key}")
    except Exception as e:
        logger.warning(f"Error guardando en caché: {str(e)}")


def load_product_template(**context) -> Dict:
    """Carga el template de producto desde parámetros o XCom."""
    try:
        params = context.get('params', {})
        
        # Intentar obtener desde parámetros del DAG
        if params:
            template = {
                'product_name': params.get('product_name', ''),
                'product_type': params.get('product_type', ''),
                'key_benefits': params.get('key_benefits', []),
                'technical_features': params.get('technical_features', []),
                'target_audience': params.get('target_audience', ''),
                'platform': params.get('platform', 'generic'),
                'keywords': params.get('keywords', []),
                'brand_story': params.get('brand_story'),
                'word_count': params.get('word_count', 300),
                'generate_variations': params.get('generate_variations', False),
                'num_variations': params.get('num_variations', 3)
            }
        else:
            # Fallback: usar valores por defecto de ejemplo
            template = {
                'product_name': 'Zapatos Ecológicos Modelo X',
                'product_type': 'Calzado sostenible',
                'key_benefits': [
                    'Durabilidad 2x mayor que zapatos convencionales',
                    '100% materiales reciclados y reciclables',
                    'Comfort superior con tecnología de amortiguación avanzada'
                ],
                'technical_features': [
                    'Suela de caucho reciclado con 70% de contenido reciclado',
                    'Forro interior de algodón orgánico certificado',
                    'Peso ligero: 280g por par',
                    'Resistente al agua con tratamiento ecológico'
                ],
                'target_audience': 'compradores eco-friendly conscientes del medio ambiente',
                'platform': 'amazon',
                'keywords': ['zapatos ecológicos', 'calzado sostenible', 'zapatos reciclados'],
                'word_count': 300
            }
        
        if not template.get('product_name'):
            raise ValueError("product_name es requerido")
        
        logger.info(f"Template cargado para producto: {template['product_name']}")
        return template
        
    except Exception as e:
        logger.error(f"Error cargando template: {str(e)}")
        raise


def generate_product_description_ai(**context) -> str:
    """Genera una descripción de producto usando IA con caché."""
    template = context['ti'].xcom_pull(task_ids='load_template')
    
    # Verificar caché
    cache_key = get_cache_key(template)
    cached_description = check_cache(cache_key)
    
    if cached_description:
        logger.info(f"Usando descripción desde caché para {template['product_name']}")
        context['ti'].xcom_push(key='metadata', value=cached_description.get('metadata', {}))
        return cached_description.get('description', '')
    
    try:
        # Intentar con el proveedor configurado, con fallback
        provider = Variable.get("DEFAULT_LLM_PROVIDER", default_var=DEFAULT_LLM_PROVIDER)
        llm_client = None
        last_error = None
        
        for attempt_provider in [provider] + [p for p in LLM_PROVIDERS if p != provider]:
            try:
                llm_client = LLMClient(attempt_provider)
                break
            except Exception as e:
                last_error = e
                logger.warning(f"Error con proveedor {attempt_provider}: {str(e)}")
                continue
        
        if not llm_client:
            raise Exception(f"No se pudo inicializar ningún proveedor de IA: {last_error}")
        
        # Generar descripción
        generator = ProductDescriptionGenerator(llm_client)
        
        start_time = time.time()
        result = generator.generate_description(
            product_name=template['product_name'],
            product_type=template.get('product_type', ''),
            key_benefits=template.get('key_benefits', []),
            technical_features=template.get('technical_features', []),
            target_audience=template.get('target_audience', ''),
            platform=template.get('platform', 'generic'),
            keywords=template.get('keywords'),
            brand_story=template.get('brand_story'),
            word_count=template.get('word_count', 300)
        )
        generation_time = time.time() - start_time
        
        result['metadata']['generation_time'] = generation_time
        
        # Guardar metadata
        context['ti'].xcom_push(key='metadata', value=result['metadata'])
        context['ti'].xcom_push(key='full_result', value=result)
        
        # Guardar en caché
        save_to_cache(cache_key, result)
        
        logger.info(f"Descripción generada para {template['product_name']} usando {result['metadata'].get('provider')} ({result['metadata'].get('tokens_used')} tokens)")
        return result['description']
        
    except Exception as e:
        logger.error(f"Error generando descripción: {str(e)}")
        raise


def generate_variations_for_ab_testing(**context) -> List[Dict]:
    """Genera variaciones de descripción para A/B testing."""
    template = context['ti'].xcom_pull(task_ids='load_template')
    base_result = context['ti'].xcom_pull(task_ids='generate_description', key='full_result')
    
    if not template.get('generate_variations', False):
        logger.info("Generación de variaciones deshabilitada")
        return []
    
    try:
        provider = Variable.get("DEFAULT_LLM_PROVIDER", default_var=DEFAULT_LLM_PROVIDER)
        llm_client = LLMClient(provider)
        generator = ProductDescriptionGenerator(llm_client)
        
        num_variations = template.get('num_variations', 3)
        variation_types = template.get('variation_types', ['emotional', 'technical', 'benefit_focused'])
        
        base_product_info = {
            'product_name': template['product_name'],
            'product_type': template.get('product_type', ''),
            'key_benefits': template.get('key_benefits', []),
            'technical_features': template.get('technical_features', []),
            'target_audience': template.get('target_audience', ''),
            'platform': template.get('platform', 'generic'),
            'keywords': template.get('keywords'),
            'brand_story': template.get('brand_story')
        }
        
        variations = generator.generate_variations(
            base_product_info=base_product_info,
            num_variations=num_variations,
            variation_types=variation_types
        )
        
        logger.info(f"Generadas {len(variations)} variaciones para A/B testing")
        return variations
        
    except Exception as e:
        logger.error(f"Error generando variaciones: {str(e)}")
        raise


def save_product_description_to_db(**context) -> str:
    """Guarda la descripción generada en la base de datos."""
    template = context['ti'].xcom_pull(task_ids='load_template')
    description = context['ti'].xcom_pull(task_ids='generate_description')
    full_result = context['ti'].xcom_pull(task_ids='generate_description', key='full_result')
    metadata = context['ti'].xcom_pull(task_ids='generate_description', key='metadata')
    variations = context['ti'].xcom_pull(task_ids='generate_variations', default=[])
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        query = """
            INSERT INTO product_descriptions (
                product_name, product_type, description, full_description_data,
                platform, seo_keywords, meta_description, multimedia_suggestions,
                word_count, ai_provider, ai_model, tokens_used,
                created_at, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), 'draft')
            RETURNING product_description_id
        """
        
        result = pg_hook.get_first(query, parameters=(
            template['product_name'],
            template.get('product_type', ''),
            description,
            json.dumps(full_result) if full_result else None,
            template.get('platform', 'generic'),
            json.dumps(full_result.get('seo_keywords', []) if full_result else []),
            full_result.get('meta_description', '') if full_result else '',
            json.dumps(full_result.get('multimedia_suggestions', {}) if full_result else {}),
            full_result.get('word_count', 0) if full_result else 0,
            metadata.get('provider') if metadata else None,
            metadata.get('model') if metadata else None,
            metadata.get('tokens_used') if metadata else None
        ))
        
        product_description_id = result[0] if result else None
        logger.info(f"Descripción guardada en BD con ID: {product_description_id}")
        
        # Guardar variaciones si existen
        if variations and product_description_id:
            for var in variations:
                var_query = """
                    INSERT INTO product_description_variations (
                        product_description_id, variation_type, description,
                        variation_data, created_at
                    ) VALUES (%s, %s, %s, %s, NOW())
                """
                pg_hook.run(var_query, parameters=(
                    product_description_id,
                    var.get('variation_type', 'unknown'),
                    var.get('description', ''),
                    json.dumps(var)
                ))
            logger.info(f"Guardadas {len(variations)} variaciones en BD")
        
        # Guardar ID en XCom
        context['ti'].xcom_push(key='product_description_id', value=product_description_id)
        return product_description_id
        
    except Exception as e:
        logger.error(f"Error guardando en BD: {str(e)}")
        raise


# DAG principal
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.models import Param

@dag(
    dag_id="product_description_generator",
    start_date=days_ago(1),
    schedule=None,  # Manual trigger o programado según necesidad
    catchup=False,
    default_args=default_args,
    params={
        "product_name": Param("", type="string", minLength=1, description="Nombre del producto"),
        "product_type": Param("", type="string", description="Tipo/categoría del producto"),
        "key_benefits": Param([], type="array", description="Lista de beneficios clave"),
        "technical_features": Param([], type="array", description="Lista de características técnicas"),
        "target_audience": Param("", type="string", description="Público objetivo"),
        "platform": Param("generic", type="string", enum=SUPPORTED_PLATFORMS, description="Plataforma destino"),
        "keywords": Param([], type="array", description="Keywords SEO opcionales"),
        "brand_story": Param("", type="string", description="Historia de marca opcional"),
        "word_count": Param(300, type="integer", minimum=200, maximum=400, description="Número objetivo de palabras"),
        "generate_variations": Param(False, type="boolean", description="Generar variaciones para A/B testing"),
        "num_variations": Param(3, type="integer", minimum=1, maximum=10, description="Número de variaciones"),
        "variation_types": Param(["emotional", "technical", "benefit_focused"], type="array", description="Tipos de variación")
    },
    tags=["ecommerce", "product-descriptions", "ai", "seo", "ab-testing", "marketing"],
    doc_md=__doc__
)
def product_description_generator_dag():
    """DAG para generar descripciones de productos con IA."""
    
    load_template = PythonOperator(
        task_id='load_template',
        python_callable=load_product_template,
        doc_md="Carga el template de producto desde parámetros"
    )
    
    generate_description = PythonOperator(
        task_id='generate_description',
        python_callable=generate_product_description_ai,
        doc_md="Genera la descripción del producto usando IA"
    )
    
    generate_variations = PythonOperator(
        task_id='generate_variations',
        python_callable=generate_variations_for_ab_testing,
        doc_md="Genera variaciones para A/B testing (opcional)"
    )
    
    save_to_db = PythonOperator(
        task_id='save_to_db',
        python_callable=save_product_description_to_db,
        doc_md="Guarda la descripción en la base de datos"
    )
    
    # Dependencias
    load_template >> generate_description >> [generate_variations, save_to_db]
    generate_variations >> save_to_db


# Instanciar el DAG
dag = product_description_generator_dag()




