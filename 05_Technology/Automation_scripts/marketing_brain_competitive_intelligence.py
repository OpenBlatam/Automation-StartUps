"""
Marketing Brain Competitive Intelligence System
Sistema avanzado de inteligencia competitiva y análisis de mercado
"""

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import json
import time
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class CompetitiveIntelligenceSystem:
    def __init__(self):
        self.competitors_data = {}
        self.market_analysis = {}
        self.pricing_intelligence = {}
        self.content_analysis = {}
        self.social_media_intelligence = {}
        self.insights = {}
        
    def analyze_competitors(self, competitors_list):
        """Analizar competidores principales"""
        analysis_results = {}
        
        for competitor in competitors_list:
            competitor_data = {
                'name': competitor['name'],
                'website': competitor['website'],
                'social_media': competitor.get('social_media', {}),
                'analysis_date': datetime.now().isoformat()
            }
            
            # Análisis de website
            website_analysis = self._analyze_website(competitor['website'])
            competitor_data['website_analysis'] = website_analysis
            
            # Análisis de contenido
            content_analysis = self._analyze_content(competitor['website'])
            competitor_data['content_analysis'] = content_analysis
            
            # Análisis de pricing
            pricing_analysis = self._analyze_pricing(competitor['website'])
            competitor_data['pricing_analysis'] = pricing_analysis
            
            # Análisis de social media
            if competitor.get('social_media'):
                social_analysis = self._analyze_social_media(competitor['social_media'])
                competitor_data['social_analysis'] = social_analysis
            
            analysis_results[competitor['name']] = competitor_data
            
            # Delay para evitar rate limiting
            time.sleep(1)
        
        self.competitors_data = analysis_results
        return analysis_results
    
    def _analyze_website(self, website_url):
        """Analizar website del competidor"""
        try:
            response = requests.get(website_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Análisis básico
            analysis = {
                'page_title': soup.title.string if soup.title else 'N/A',
                'meta_description': self._get_meta_description(soup),
                'headings': self._extract_headings(soup),
                'keywords': self._extract_keywords(soup),
                'page_speed': self._estimate_page_speed(soup),
                'mobile_friendly': self._check_mobile_friendly(soup),
                'ssl_enabled': website_url.startswith('https://'),
                'social_links': self._extract_social_links(soup)
            }
            
            return analysis
        except Exception as e:
            return {'error': str(e)}
    
    def _get_meta_description(self, soup):
        """Extraer meta descripción"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content') if meta_desc else 'N/A'
    
    def _extract_headings(self, soup):
        """Extraer headings del sitio"""
        headings = {}
        for i in range(1, 7):
            h_tags = soup.find_all(f'h{i}')
            headings[f'h{i}'] = [h.get_text().strip() for h in h_tags[:5]]  # Primeros 5
        return headings
    
    def _extract_keywords(self, soup):
        """Extraer palabras clave"""
        # Extraer texto de la página
        text = soup.get_text().lower()
        
        # Palabras clave comunes en marketing
        marketing_keywords = [
            'marketing', 'digital', 'seo', 'social media', 'content',
            'strategy', 'brand', 'customer', 'engagement', 'conversion'
        ]
        
        keyword_frequency = {}
        for keyword in marketing_keywords:
            count = text.count(keyword)
            if count > 0:
                keyword_frequency[keyword] = count
        
        return keyword_frequency
    
    def _estimate_page_speed(self, soup):
        """Estimar velocidad de página"""
        # Análisis simplificado basado en elementos
        images = len(soup.find_all('img'))
        scripts = len(soup.find_all('script'))
        stylesheets = len(soup.find_all('link', rel='stylesheet'))
        
        # Score simplificado (menos elementos = mejor velocidad)
        speed_score = 100 - (images * 2) - (scripts * 1) - (stylesheets * 1)
        return max(0, min(100, speed_score))
    
    def _check_mobile_friendly(self, soup):
        """Verificar si es mobile-friendly"""
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        return viewport is not None
    
    def _extract_social_links(self, soup):
        """Extraer enlaces a redes sociales"""
        social_platforms = ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube']
        social_links = {}
        
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            for platform in social_platforms:
                if platform in href:
                    social_links[platform] = link['href']
                    break
        
        return social_links
    
    def _analyze_content(self, website_url):
        """Analizar contenido del competidor"""
        try:
            response = requests.get(website_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer contenido de texto
            text_content = soup.get_text()
            
            # Análisis de contenido
            content_analysis = {
                'word_count': len(text_content.split()),
                'paragraph_count': len(soup.find_all('p')),
                'image_count': len(soup.find_all('img')),
                'video_count': len(soup.find_all('video')),
                'blog_posts': len(soup.find_all('article')),
                'content_themes': self._identify_content_themes(text_content),
                'call_to_actions': self._extract_ctas(soup)
            }
            
            return content_analysis
        except Exception as e:
            return {'error': str(e)}
    
    def _identify_content_themes(self, text):
        """Identificar temas del contenido"""
        themes = {
            'technology': ['tech', 'digital', 'ai', 'software', 'innovation'],
            'marketing': ['marketing', 'advertising', 'promotion', 'campaign'],
            'business': ['business', 'strategy', 'growth', 'revenue', 'profit'],
            'customer': ['customer', 'client', 'user', 'experience', 'service']
        }
        
        text_lower = text.lower()
        theme_scores = {}
        
        for theme, keywords in themes.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            if score > 0:
                theme_scores[theme] = score
        
        return theme_scores
    
    def _extract_ctas(self, soup):
        """Extraer call-to-actions"""
        cta_keywords = ['buy', 'subscribe', 'download', 'learn more', 'get started', 'contact']
        ctas = []
        
        for link in soup.find_all('a', href=True):
            link_text = link.get_text().lower().strip()
            for cta in cta_keywords:
                if cta in link_text:
                    ctas.append(link_text)
                    break
        
        return list(set(ctas))  # Remover duplicados
    
    def _analyze_pricing(self, website_url):
        """Analizar pricing del competidor"""
        try:
            response = requests.get(website_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar elementos de pricing
            pricing_elements = soup.find_all(text=lambda text: text and '$' in text)
            
            prices = []
            for element in pricing_elements:
                # Extraer números de precio
                import re
                price_matches = re.findall(r'\$[\d,]+\.?\d*', element)
                prices.extend(price_matches)
            
            # Análisis de pricing
            pricing_analysis = {
                'prices_found': prices[:10],  # Primeros 10 precios
                'price_range': self._calculate_price_range(prices),
                'pricing_strategy': self._identify_pricing_strategy(prices),
                'free_trial_offered': self._check_free_trial(soup),
                'discount_offered': self._check_discounts(soup)
            }
            
            return pricing_analysis
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_price_range(self, prices):
        """Calcular rango de precios"""
        if not prices:
            return {'min': 0, 'max': 0, 'avg': 0}
        
        # Limpiar precios
        clean_prices = []
        for price in prices:
            try:
                clean_price = float(price.replace('$', '').replace(',', ''))
                clean_prices.append(clean_price)
            except:
                continue
        
        if clean_prices:
            return {
                'min': min(clean_prices),
                'max': max(clean_prices),
                'avg': np.mean(clean_prices)
            }
        return {'min': 0, 'max': 0, 'avg': 0}
    
    def _identify_pricing_strategy(self, prices):
        """Identificar estrategia de pricing"""
        if not prices:
            return 'Unknown'
        
        clean_prices = []
        for price in prices:
            try:
                clean_price = float(price.replace('$', '').replace(',', ''))
                clean_prices.append(clean_price)
            except:
                continue
        
        if not clean_prices:
            return 'Unknown'
        
        price_std = np.std(clean_prices)
        price_mean = np.mean(clean_prices)
        
        if price_std < price_mean * 0.1:
            return 'Fixed Pricing'
        elif len(set(clean_prices)) > len(clean_prices) * 0.5:
            return 'Tiered Pricing'
        else:
            return 'Variable Pricing'
    
    def _check_free_trial(self, soup):
        """Verificar si ofrecen prueba gratuita"""
        trial_keywords = ['free trial', 'trial', 'demo', 'test drive']
        text = soup.get_text().lower()
        return any(keyword in text for keyword in trial_keywords)
    
    def _check_discounts(self, soup):
        """Verificar si ofrecen descuentos"""
        discount_keywords = ['discount', 'sale', 'off', 'promo', 'coupon']
        text = soup.get_text().lower()
        return any(keyword in text for keyword in discount_keywords)
    
    def _analyze_social_media(self, social_media_data):
        """Analizar redes sociales del competidor"""
        social_analysis = {}
        
        for platform, data in social_media_data.items():
            platform_analysis = {
                'followers': data.get('followers', 0),
                'engagement_rate': data.get('engagement_rate', 0),
                'posting_frequency': data.get('posting_frequency', 0),
                'content_types': data.get('content_types', []),
                'hashtags': data.get('hashtags', [])
            }
            social_analysis[platform] = platform_analysis
        
        return social_analysis
    
    def generate_competitive_insights(self):
        """Generar insights competitivos"""
        insights = {
            'market_positioning': self._analyze_market_positioning(),
            'content_gaps': self._identify_content_gaps(),
            'pricing_opportunities': self._identify_pricing_opportunities(),
            'social_media_insights': self._analyze_social_media_insights(),
            'recommendations': self._generate_recommendations()
        }
        
        self.insights = insights
        return insights
    
    def _analyze_market_positioning(self):
        """Analizar posicionamiento de mercado"""
        positioning_analysis = {}
        
        for competitor, data in self.competitors_data.items():
            website_data = data.get('website_analysis', {})
            content_data = data.get('content_analysis', {})
            
            positioning = {
                'focus_areas': list(content_data.get('content_themes', {}).keys()),
                'content_volume': content_data.get('word_count', 0),
                'visual_content': content_data.get('image_count', 0) + content_data.get('video_count', 0),
                'seo_focus': len(website_data.get('keywords', {}))
            }
            
            positioning_analysis[competitor] = positioning
        
        return positioning_analysis
    
    def _identify_content_gaps(self):
        """Identificar gaps de contenido"""
        all_themes = set()
        competitor_themes = {}
        
        for competitor, data in self.competitors_data.items():
            themes = set(data.get('content_analysis', {}).get('content_themes', {}).keys())
            all_themes.update(themes)
            competitor_themes[competitor] = themes
        
        # Identificar temas únicos por competidor
        unique_themes = {}
        for competitor, themes in competitor_themes.items():
            other_themes = set()
            for other_competitor, other_themes_set in competitor_themes.items():
                if other_competitor != competitor:
                    other_themes.update(other_themes_set)
            
            unique_themes[competitor] = themes - other_themes
        
        return {
            'all_themes': list(all_themes),
            'unique_themes': unique_themes,
            'content_gaps': list(all_themes - set().union(*competitor_themes.values()))
        }
    
    def _identify_pricing_opportunities(self):
        """Identificar oportunidades de pricing"""
        pricing_opportunities = {}
        
        for competitor, data in self.competitors_data.items():
            pricing_data = data.get('pricing_analysis', {})
            price_range = pricing_data.get('price_range', {})
            
            opportunities = {
                'price_range': price_range,
                'strategy': pricing_data.get('pricing_strategy', 'Unknown'),
                'free_trial': pricing_data.get('free_trial_offered', False),
                'discounts': pricing_data.get('discount_offered', False)
            }
            
            pricing_opportunities[competitor] = opportunities
        
        return pricing_opportunities
    
    def _analyze_social_media_insights(self):
        """Analizar insights de redes sociales"""
        social_insights = {}
        
        for competitor, data in self.competitors_data.items():
            social_data = data.get('social_analysis', {})
            
            total_followers = sum(platform.get('followers', 0) for platform in social_data.values())
            avg_engagement = np.mean([platform.get('engagement_rate', 0) for platform in social_data.values()])
            
            social_insights[competitor] = {
                'total_followers': total_followers,
                'avg_engagement_rate': avg_engagement,
                'platforms_active': len(social_data),
                'content_diversity': len(set().union(*[platform.get('content_types', []) for platform in social_data.values()]))
            }
        
        return social_insights
    
    def _generate_recommendations(self):
        """Generar recomendaciones estratégicas"""
        recommendations = []
        
        # Análisis de contenido
        content_gaps = self._identify_content_gaps()
        if content_gaps['content_gaps']:
            recommendations.append(f"Crear contenido sobre: {', '.join(content_gaps['content_gaps'])}")
        
        # Análisis de pricing
        pricing_opportunities = self._identify_pricing_opportunities()
        free_trial_competitors = [comp for comp, data in pricing_opportunities.items() if data.get('free_trial')]
        if free_trial_competitors:
            recommendations.append(f"Considerar ofrecer prueba gratuita (competidores: {', '.join(free_trial_competitors)})")
        
        # Análisis de social media
        social_insights = self._analyze_social_media_insights()
        high_engagement_competitors = [comp for comp, data in social_insights.items() if data.get('avg_engagement_rate', 0) > 5]
        if high_engagement_competitors:
            recommendations.append(f"Estudiar estrategias de engagement de: {', '.join(high_engagement_competitors)}")
        
        return recommendations
    
    def create_competitive_dashboard(self):
        """Crear dashboard de inteligencia competitiva"""
        if not self.competitors_data:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Posicionamiento de Contenido', 'Análisis de Pricing',
                          'Presencia en Redes Sociales', 'Oportunidades de Mercado'),
            specs=[[{"type": "scatter"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "pie"}]]
        )
        
        # Gráfico de posicionamiento
        positioning_data = self._analyze_market_positioning()
        competitors = list(positioning_data.keys())
        content_volumes = [data['content_volume'] for data in positioning_data.values()]
        visual_content = [data['visual_content'] for data in positioning_data.values()]
        
        fig.add_trace(
            go.Scatter(
                x=content_volumes,
                y=visual_content,
                mode='markers+text',
                text=competitors,
                textposition="top center",
                name='Posicionamiento'
            ),
            row=1, col=1
        )
        
        # Gráfico de pricing
        pricing_data = self._identify_pricing_opportunities()
        avg_prices = [data['price_range'].get('avg', 0) for data in pricing_data.values()]
        
        fig.add_trace(
            go.Bar(x=competitors, y=avg_prices, name='Precio Promedio'),
            row=1, col=2
        )
        
        # Gráfico de redes sociales
        social_data = self._analyze_social_media_insights()
        followers = [data['total_followers'] for data in social_data.values()]
        
        fig.add_trace(
            go.Bar(x=competitors, y=followers, name='Seguidores Totales'),
            row=2, col=1
        )
        
        # Gráfico de oportunidades
        content_gaps = self._identify_content_gaps()
        gap_counts = [len(data) for data in content_gaps['unique_themes'].values()]
        
        fig.add_trace(
            go.Pie(labels=competitors, values=gap_counts, name='Temas Únicos'),
            row=2, col=2
        )
        
        fig.update_layout(
            title="Dashboard de Inteligencia Competitiva",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_competitive_analysis(self, filename='competitive_intelligence_analysis.json'):
        """Exportar análisis competitivo"""
        analysis_data = {
            'timestamp': datetime.now().isoformat(),
            'competitors_data': self.competitors_data,
            'insights': self.insights,
            'summary': {
                'total_competitors': len(self.competitors_data),
                'analysis_date': datetime.now().isoformat(),
                'key_insights': len(self.insights.get('recommendations', []))
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(analysis_data, f, indent=2, default=str)
        
        print(f"✅ Análisis competitivo exportado a {filename}")
        return analysis_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del sistema de inteligencia competitiva
    competitive_intelligence = CompetitiveIntelligenceSystem()
    
    # Lista de competidores de ejemplo
    competitors = [
        {
            'name': 'Competitor A',
            'website': 'https://example1.com',
            'social_media': {
                'facebook': {'followers': 10000, 'engagement_rate': 3.5},
                'twitter': {'followers': 5000, 'engagement_rate': 2.8}
            }
        },
        {
            'name': 'Competitor B',
            'website': 'https://example2.com',
            'social_media': {
                'instagram': {'followers': 15000, 'engagement_rate': 4.2},
                'linkedin': {'followers': 8000, 'engagement_rate': 3.1}
            }
        }
    ]
    
    # Analizar competidores
    print("🔍 Analizando competidores...")
    analysis = competitive_intelligence.analyze_competitors(competitors)
    
    # Generar insights
    print("💡 Generando insights competitivos...")
    insights = competitive_intelligence.generate_competitive_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de inteligencia competitiva...")
    dashboard = competitive_intelligence.create_competitive_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis competitivo...")
    export_data = competitive_intelligence.export_competitive_analysis()
    
    print("✅ Sistema de inteligencia competitiva completado!")






