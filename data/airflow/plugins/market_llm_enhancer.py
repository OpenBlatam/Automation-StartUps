"""
Integración con LLM para Insights Mejorados

Usa LLMs (OpenAI, Anthropic, etc.) para generar insights más contextuales
y recomendaciones más inteligentes basadas en análisis de mercado.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class MarketLLMEnhancer:
    """Mejora insights usando LLMs."""
    
    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Inicializa el enhancer LLM.
        
        Args:
            provider: Proveedor LLM ("openai", "anthropic", "local")
            api_key: API key (opcional, usa env var si no se proporciona)
            model: Modelo específico (opcional)
        """
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv(f"{self.provider.upper()}_API_KEY")
        self.model = model or self._get_default_model()
        self.http_client = httpx.Client(timeout=60.0)
    
    def _get_default_model(self) -> str:
        """Obtiene modelo por defecto según proveedor."""
        defaults = {
            "openai": "gpt-4-turbo-preview",
            "anthropic": "claude-3-opus-20240229",
            "local": "llama2"
        }
        return defaults.get(self.provider, "gpt-4-turbo-preview")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def enhance_insights(
        self,
        insights: List[Dict[str, Any]],
        market_context: Dict[str, Any],
        industry: str
    ) -> List[Dict[str, Any]]:
        """
        Mejora insights usando LLM.
        
        Args:
            insights: Lista de insights originales
            market_context: Contexto del mercado
            industry: Industria objetivo
            
        Returns:
            Insights mejorados con análisis LLM
        """
        if not self.api_key:
            logger.warning("LLM API key not configured, returning original insights")
            return insights
        
        enhanced_insights = []
        
        for insight in insights:
            try:
                enhanced = self._enhance_single_insight(insight, market_context, industry)
                enhanced_insights.append(enhanced)
            except Exception as e:
                logger.error(f"Error enhancing insight: {e}")
                enhanced_insights.append(insight)  # Fallback a original
        
        return enhanced_insights
    
    def _enhance_single_insight(
        self,
        insight: Dict[str, Any],
        market_context: Dict[str, Any],
        industry: str
    ) -> Dict[str, Any]:
        """Mejora un insight individual."""
        prompt = self._build_enhancement_prompt(insight, market_context, industry)
        enhanced_text = self._call_llm(prompt)
        
        # Parsear respuesta del LLM
        enhanced_data = self._parse_llm_response(enhanced_text)
        
        # Combinar con insight original
        enhanced_insight = {
            **insight,
            "llm_enhanced": True,
            "llm_analysis": enhanced_data.get("analysis", ""),
            "llm_recommendations": enhanced_data.get("recommendations", []),
            "llm_risk_assessment": enhanced_data.get("risk_assessment", ""),
            "llm_opportunity_score": enhanced_data.get("opportunity_score", insight.get("confidence_score", 0.5)),
            "enhanced_at": datetime.utcnow().isoformat()
        }
        
        return enhanced_insight
    
    def _build_enhancement_prompt(
        self,
        insight: Dict[str, Any],
        market_context: Dict[str, Any],
        industry: str
    ) -> str:
        """Construye prompt para LLM."""
        return f"""Eres un experto en análisis de mercado y estrategia empresarial.

Analiza el siguiente insight de mercado para la industria {industry}:

**Insight:**
- Título: {insight.get('title', 'N/A')}
- Descripción: {insight.get('description', 'N/A')}
- Categoría: {insight.get('category', 'N/A')}
- Prioridad: {insight.get('priority', 'N/A')}
- Pasos Accionables: {', '.join(insight.get('actionable_steps', []))}
- Impacto Esperado: {insight.get('expected_impact', 'N/A')}

**Contexto de Mercado:**
- Tendencias: {len(market_context.get('trends', []))} tendencias analizadas
- Oportunidades: {len(market_context.get('opportunities', []))} oportunidades
- Riesgos: {len(market_context.get('risks', []))} riesgos

Proporciona un análisis mejorado en formato JSON con:
1. "analysis": Análisis profundo del insight (2-3 párrafos)
2. "recommendations": Lista de 3-5 recomendaciones estratégicas específicas
3. "risk_assessment": Evaluación de riesgos asociados
4. "opportunity_score": Score de oportunidad (0-1) basado en tu análisis

Responde SOLO con JSON válido, sin markdown ni texto adicional."""

    def _call_llm(self, prompt: str) -> str:
        """Llama al LLM según proveedor."""
        if self.provider == "openai":
            return self._call_openai(prompt)
        elif self.provider == "anthropic":
            return self._call_anthropic(prompt)
        else:
            logger.warning(f"Provider {self.provider} not fully implemented, using mock")
            return self._mock_llm_response()
    
    def _call_openai(self, prompt: str) -> str:
        """Llama a OpenAI API."""
        try:
            response = self.http_client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a market research expert. Always respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling OpenAI: {e}")
            return self._mock_llm_response()
    
    def _call_anthropic(self, prompt: str) -> str:
        """Llama a Anthropic API."""
        try:
            response = self.http_client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "max_tokens": 1000,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"]
        except Exception as e:
            logger.error(f"Error calling Anthropic: {e}")
            return self._mock_llm_response()
    
    def _mock_llm_response(self) -> str:
        """Respuesta mock cuando LLM no está disponible."""
        return json.dumps({
            "analysis": "Análisis mejorado basado en tendencias de mercado actuales. Este insight representa una oportunidad significativa que requiere atención estratégica.",
            "recommendations": [
                "Desarrollar plan de acción específico para capitalizar esta oportunidad",
                "Asignar recursos adecuados para implementación",
                "Establecer métricas de seguimiento",
                "Revisar competencia y diferenciación"
            ],
            "risk_assessment": "Riesgos moderados asociados. Requiere monitoreo continuo.",
            "opportunity_score": 0.75
        })
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parsea respuesta del LLM."""
        try:
            # Limpiar respuesta (remover markdown si existe)
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return {
                "analysis": response,
                "recommendations": [],
                "risk_assessment": "Unable to parse",
                "opportunity_score": 0.5
            }
    
    def generate_executive_summary(
        self,
        market_analysis: Dict[str, Any],
        insights: List[Dict[str, Any]],
        industry: str
    ) -> str:
        """
        Genera resumen ejecutivo usando LLM.
        
        Args:
            market_analysis: Análisis completo de mercado
            insights: Lista de insights
            industry: Industria
            
        Returns:
            Resumen ejecutivo generado por LLM
        """
        if not self.api_key:
            return self._generate_basic_summary(market_analysis, insights, industry)
        
        prompt = f"""Genera un resumen ejecutivo profesional para investigación de mercado.

**Industria:** {industry}
**Tendencias Analizadas:** {len(market_analysis.get('trends', []))}
**Insights Generados:** {len(insights)}
**Oportunidades:** {len(market_analysis.get('opportunities', []))}
**Riesgos:** {len(market_analysis.get('risk_factors', []))}

**Top 3 Insights de Alta Prioridad:**
{chr(10).join([f"- {i.get('title', 'N/A')}: {i.get('description', 'N/A')[:100]}..." for i in insights[:3]])}

Genera un resumen ejecutivo de 3-4 párrafos que:
1. Resuma las tendencias clave del mercado
2. Destaque las oportunidades más importantes
3. Identifique los principales riesgos
4. Proporcione recomendaciones estratégicas de alto nivel

Formato: Texto profesional, sin markdown."""
        
        try:
            summary = self._call_llm(prompt)
            return summary
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return self._generate_basic_summary(market_analysis, insights, industry)
    
    def _generate_basic_summary(
        self,
        market_analysis: Dict[str, Any],
        insights: List[Dict[str, Any]],
        industry: str
    ) -> str:
        """Genera resumen básico sin LLM."""
        return f"""
RESUMEN EJECUTIVO - INVESTIGACIÓN DE MERCADO: {industry.upper()}

Análisis completado el {datetime.utcnow().strftime('%Y-%m-%d')}.

TENDENCIAS CLAVE:
- {len(market_analysis.get('trends', []))} tendencias analizadas
- {len([t for t in market_analysis.get('trends', []) if t.get('trend_direction') == 'up'])} tendencias alcistas
- {len([t for t in market_analysis.get('trends', []) if t.get('trend_direction') == 'down'])} tendencias bajistas

OPORTUNIDADES:
- {len(market_analysis.get('opportunities', []))} oportunidades identificadas
- Top oportunidad: {market_analysis.get('opportunities', [{}])[0].get('title', 'N/A') if market_analysis.get('opportunities') else 'N/A'}

RIESGOS:
- {len(market_analysis.get('risk_factors', []))} factores de riesgo detectados

INSIGHTS ACCIONABLES:
- {len(insights)} insights generados
- {len([i for i in insights if i.get('priority') == 'high'])} de alta prioridad

RECOMENDACIONES:
1. Revisar insights de alta prioridad inmediatamente
2. Desarrollar planes de acción para oportunidades top
3. Mitigar riesgos identificados
4. Monitorear tendencias continuamente
"""






