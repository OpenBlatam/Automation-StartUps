#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de IA Generativa para Contenido de Marketing
===================================================
Genera automáticamente contenido de marketing personalizado usando IA avanzada.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import random
import re
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class AIContentGenerator:
    def __init__(self, campaigns_file='enhanced_1000_ai_marketing_campaigns.json'):
        """Inicializa el generador de contenido con IA"""
        with open(campaigns_file, 'r', encoding='utf-8') as f:
            self.campaigns = json.load(f)
        
        self.df = pd.DataFrame(self.campaigns)
        
        # Plantillas de contenido por tipo
        self.content_templates = {
            'email_marketing': {
                'asunto': [
                    "🚀 {producto} - {descuento}% OFF - Solo hoy",
                    "¡{producto} que cambiará tu {industria}!",
                    "Última oportunidad: {producto} con {descuento}% descuento",
                    "Descubre el secreto de {producto}",
                    "¿Por qué {competencia} no quiere que sepas esto sobre {producto}?"
                ],
                'cuerpo': [
                    "Hola {nombre},\n\n¿Sabías que {estadistica}?\n\nCon {producto}, puedes {beneficio1} y {beneficio2}.\n\n¡No esperes más! Obtén {descuento}% de descuento solo por tiempo limitado.\n\n{call_to_action}\n\nSaludos,\n{empresa}",
                    "Estimado {nombre},\n\n{producto} está revolucionando la {industria}.\n\nBeneficios clave:\n• {beneficio1}\n• {beneficio2}\n• {beneficio3}\n\n¡Oferta especial: {descuento}% OFF!\n\n{call_to_action}",
                    "¡Hola {nombre}!\n\n{producto} ha ayudado a {numero} personas a {resultado}.\n\n¿Quieres ser el siguiente?\n\n{call_to_action}\n\nP.D.: Esta oferta expira en {tiempo_limite}."
                ]
            },
            'social_media': {
                'facebook': [
                    "🔥 {producto} está cambiando el juego en {industria}!\n\n{beneficio1}\n{beneficio2}\n\n¿Listo para unirte? {call_to_action}",
                    "💡 Consejo del día: {consejo}\n\nCon {producto}, puedes {beneficio1}.\n\n{call_to_action}",
                    "🎯 {estadistica}\n\n{producto} te ayuda a {resultado}.\n\n{call_to_action}"
                ],
                'instagram': [
                    "✨ {producto} ✨\n\n{beneficio1}\n{beneficio2}\n\n{call_to_action}\n\n#{hashtag1} #{hashtag2} #{hashtag3}",
                    "🚀 {estadistica}\n\n{producto} = {resultado}\n\n{call_to_action}\n\n#{hashtag1} #{hashtag2}",
                    "💎 {producto} 💎\n\n{beneficio1}\n\n{call_to_action}\n\n#{hashtag1} #{hashtag2} #{hashtag3} #{hashtag4}"
                ],
                'twitter': [
                    "{producto} está revolucionando {industria}! {beneficio1} {call_to_action} #{hashtag1}",
                    "💡 {consejo}\n\n{producto} te ayuda a {resultado}. {call_to_action}",
                    "🔥 {estadistica}\n\n{producto} = {beneficio1} {call_to_action} #{hashtag1} #{hashtag2}"
                ],
                'linkedin': [
                    "¿Sabías que {estadistica}?\n\n{producto} está transformando la {industria} al permitir que las empresas {beneficio1} y {beneficio2}.\n\n{call_to_action}\n\n#{hashtag1} #{hashtag2} #{hashtag3}",
                    "En la era digital, {producto} se ha convertido en una herramienta esencial para {industria}.\n\nBeneficios clave:\n• {beneficio1}\n• {beneficio2}\n• {beneficio3}\n\n{call_to_action}",
                    "La {industria} está evolucionando, y {producto} está liderando el cambio.\n\n{estadistica}\n\n{call_to_action}\n\n#{hashtag1} #{hashtag2}"
                ]
            },
            'blog_posts': {
                'titulo': [
                    "Cómo {producto} está revolucionando la {industria} en 2024",
                    "10 razones por las que {producto} es esencial para tu {industria}",
                    "La guía completa de {producto}: Todo lo que necesitas saber",
                    "¿Por qué {competencia} no quiere que sepas sobre {producto}?",
                    "El futuro de la {industria}: {producto} y sus beneficios"
                ],
                'introduccion': [
                    "En el mundo actual de la {industria}, {producto} se ha convertido en una herramienta indispensable. Con {estadistica}, no es de extrañar que cada vez más empresas estén adoptando esta tecnología innovadora.",
                    "¿Te has preguntado cómo algunas empresas en {industria} logran resultados excepcionales? La respuesta podría estar en {producto}, una solución que está transformando la forma en que trabajamos.",
                    "La {industria} está en constante evolución, y {producto} está liderando esta transformación. En este artículo, exploraremos por qué esta herramienta es crucial para el éxito moderno."
                ],
                'contenido': [
                    "## ¿Qué es {producto}?\n\n{producto} es una solución innovadora que permite a las empresas {beneficio1} y {beneficio2}. Con {estadistica}, se ha convertido en una herramienta esencial para la {industria}.\n\n## Beneficios clave\n\n1. **{beneficio1}**: {descripcion1}\n2. **{beneficio2}**: {descripcion2}\n3. **{beneficio3}**: {descripcion3}\n\n## Cómo implementar {producto}\n\nLa implementación de {producto} es sencilla y puede comenzar inmediatamente. {call_to_action}",
                    "## La revolución de {producto} en {industria}\n\n{producto} está cambiando las reglas del juego en la {industria}. Con {estadistica}, las empresas que adoptan esta tecnología obtienen ventajas significativas.\n\n### Ventajas competitivas\n\n- **{beneficio1}**: {descripcion1}\n- **{beneficio2}**: {descripcion2}\n- **{beneficio3}**: {descripcion3}\n\n### Casos de éxito\n\nEmpresas líderes en {industria} ya están utilizando {producto} para {resultado}. {call_to_action}"
                ]
            },
            'landing_pages': {
                'headline': [
                    "Descubre cómo {producto} puede {beneficio1} en tu {industria}",
                    "La solución definitiva para {problema} en {industria}",
                    "Transforma tu {industria} con {producto}",
                    "¿Listo para {resultado}? {producto} te ayuda a lograrlo",
                    "La herramienta que {industria} estaba esperando: {producto}"
                ],
                'subheadline': [
                    "Con {estadistica}, {producto} está ayudando a empresas como la tuya a {beneficio1} y {beneficio2}.",
                    "Únete a {numero} empresas que ya están usando {producto} para {resultado}.",
                    "No más {problema}. Con {producto}, puedes {beneficio1} en solo {tiempo}.",
                    "La tecnología que está revolucionando {industria}: {producto}.",
                    "¿Por qué esperar? {producto} está disponible ahora y puede {beneficio1}."
                ],
                'beneficios': [
                    "✅ {beneficio1}\n✅ {beneficio2}\n✅ {beneficio3}",
                    "🚀 {beneficio1}\n💡 {beneficio2}\n⚡ {beneficio3}",
                    "• {beneficio1}\n• {beneficio2}\n• {beneficio3}",
                    "🎯 {beneficio1}\n🔥 {beneficio2}\n✨ {beneficio3}"
                ],
                'call_to_action': [
                    "Obtener {producto} ahora",
                    "Comenzar gratis",
                    "Solicitar demo",
                    "Descargar guía",
                    "Agendar consulta"
                ]
            }
        }
        
        # Diccionarios de datos para personalización
        self.data_dictionaries = {
            'industrias': [
                'tecnología', 'marketing', 'ventas', 'finanzas', 'salud', 'educación',
                'retail', 'manufactura', 'servicios', 'consultoría', 'bienes raíces',
                'turismo', 'alimentación', 'moda', 'automotriz', 'energía', 'logística'
            ],
            'beneficios': [
                'aumentar las ventas', 'mejorar la eficiencia', 'reducir costos',
                'optimizar procesos', 'mejorar la experiencia del cliente',
                'automatizar tareas', 'aumentar la productividad', 'mejorar la calidad',
                'acelerar el crecimiento', 'reducir errores', 'mejorar la comunicación',
                'aumentar la satisfacción', 'optimizar recursos', 'mejorar la toma de decisiones'
            ],
            'estadisticas': [
                'el 85% de las empresas', 'más del 90% de los usuarios', 'el 75% de los casos',
                'en promedio, las empresas', 'estudios recientes muestran que',
                'según datos de la industria', 'investigaciones demuestran que',
                'las estadísticas revelan que', 'un estudio reciente indica que'
            ],
            'call_to_actions': [
                '¡Comienza ahora!', 'Descúbrelo aquí', 'Prueba gratis',
                'Obtén más información', 'Solicita una demo', 'Únete hoy',
                'Regístrate gratis', 'Descarga ahora', 'Contacta con nosotros',
                'Aprende más', 'Explora las opciones', 'Conoce más'
            ],
            'hashtags': [
                'marketing', 'tecnologia', 'innovacion', 'productividad', 'eficiencia',
                'crecimiento', 'exito', 'negocios', 'digital', 'automatizacion',
                'optimizacion', 'resultados', 'transformacion', 'futuro', 'tendencias'
            ],
            'consejos': [
                'La clave del éxito está en la consistencia',
                'La automatización es el futuro del marketing',
                'Los datos son la nueva moneda del marketing',
                'La personalización es esencial para el éxito',
                'La innovación constante es la clave del crecimiento'
            ]
        }
    
    def generate_content(self, campaign_id: int, content_type: str, 
                        custom_data: Dict = None) -> Dict[str, Any]:
        """Genera contenido personalizado para una campaña"""
        campaign = next((c for c in self.campaigns if c['id'] == campaign_id), None)
        if not campaign:
            return {"error": f"Campaña {campaign_id} no encontrada"}
        
        # Preparar datos de personalización
        personalization_data = self._prepare_personalization_data(campaign, custom_data)
        
        # Generar contenido según el tipo
        if content_type == 'email_marketing':
            content = self._generate_email_content(personalization_data)
        elif content_type == 'social_media':
            content = self._generate_social_media_content(personalization_data)
        elif content_type == 'blog_post':
            content = self._generate_blog_content(personalization_data)
        elif content_type == 'landing_page':
            content = self._generate_landing_page_content(personalization_data)
        else:
            return {"error": f"Tipo de contenido '{content_type}' no soportado"}
        
        return {
            'campaign_id': campaign_id,
            'campaign_name': campaign['name'],
            'content_type': content_type,
            'content': content,
            'personalization_data': personalization_data,
            'generated_at': datetime.now().isoformat()
        }
    
    def _prepare_personalization_data(self, campaign: Dict, custom_data: Dict = None) -> Dict[str, Any]:
        """Prepara datos de personalización para el contenido"""
        # Datos base de la campaña
        base_data = {
            'producto': campaign['name'],
            'industria': random.choice(self.data_dictionaries['industrias']),
            'empresa': 'Tu Empresa',
            'nombre': 'Cliente',
            'descuento': random.randint(10, 50),
            'numero': random.randint(100, 10000),
            'tiempo_limite': random.choice(['24 horas', '48 horas', '1 semana']),
            'competencia': random.choice(['la competencia', 'otras empresas', 'el mercado'])
        }
        
        # Agregar datos personalizados si se proporcionan
        if custom_data:
            base_data.update(custom_data)
        
        # Generar beneficios específicos
        beneficios = random.sample(self.data_dictionaries['beneficios'], 3)
        base_data.update({
            'beneficio1': beneficios[0],
            'beneficio2': beneficios[1],
            'beneficio3': beneficios[2],
            'descripcion1': f"Permite {beneficios[0]} de manera eficiente",
            'descripcion2': f"Ayuda a {beneficios[1]} con resultados comprobados",
            'descripcion3': f"Facilita {beneficios[2]} de forma automática"
        })
        
        # Generar estadísticas
        estadistica = random.choice(self.data_dictionaries['estadisticas'])
        base_data['estadistica'] = f"{estadistica} que {random.choice(self.data_dictionaries['beneficios'])}"
        
        # Generar call to action
        base_data['call_to_action'] = random.choice(self.data_dictionaries['call_to_actions'])
        
        # Generar hashtags
        hashtags = random.sample(self.data_dictionaries['hashtags'], 4)
        base_data.update({
            'hashtag1': hashtags[0],
            'hashtag2': hashtags[1],
            'hashtag3': hashtags[2],
            'hashtag4': hashtags[3]
        })
        
        # Generar consejo
        base_data['consejo'] = random.choice(self.data_dictionaries['consejos'])
        
        # Generar resultado
        base_data['resultado'] = random.choice(self.data_dictionaries['beneficios'])
        
        # Generar problema
        problemas = [
            'pérdida de tiempo', 'baja productividad', 'costos elevados',
            'procesos ineficientes', 'falta de automatización', 'errores frecuentes'
        ]
        base_data['problema'] = random.choice(problemas)
        
        # Generar tiempo
        base_data['tiempo'] = random.choice(['30 días', '2 semanas', '1 mes', '3 meses'])
        
        return base_data
    
    def _generate_email_content(self, data: Dict) -> Dict[str, Any]:
        """Genera contenido de email marketing"""
        templates = self.content_templates['email_marketing']
        
        # Generar múltiples variantes
        asuntos = []
        cuerpos = []
        
        for i in range(3):  # Generar 3 variantes
            asunto_template = random.choice(templates['asunto'])
            cuerpo_template = random.choice(templates['cuerpo'])
            
            asunto = self._replace_placeholders(asunto_template, data)
            cuerpo = self._replace_placeholders(cuerpo_template, data)
            
            asuntos.append(asunto)
            cuerpos.append(cuerpo)
        
        return {
            'asuntos': asuntos,
            'cuerpos': cuerpos,
            'variantes': [
                {
                    'asunto': asuntos[i],
                    'cuerpo': cuerpos[i],
                    'longitud_asunto': len(asuntos[i]),
                    'longitud_cuerpo': len(cuerpos[i])
                }
                for i in range(3)
            ]
        }
    
    def _generate_social_media_content(self, data: Dict) -> Dict[str, Any]:
        """Genera contenido para redes sociales"""
        platforms = ['facebook', 'instagram', 'twitter', 'linkedin']
        content = {}
        
        for platform in platforms:
            templates = self.content_templates['social_media'][platform]
            posts = []
            
            for i in range(3):  # Generar 3 posts por plataforma
                template = random.choice(templates)
                post = self._replace_placeholders(template, data)
                
                posts.append({
                    'contenido': post,
                    'longitud': len(post),
                    'hashtags': self._extract_hashtags(post),
                    'emojis': self._count_emojis(post)
                })
            
            content[platform] = posts
        
        return content
    
    def _generate_blog_content(self, data: Dict) -> Dict[str, Any]:
        """Genera contenido de blog"""
        templates = self.content_templates['blog_posts']
        
        # Generar múltiples variantes
        titulos = []
        introducciones = []
        contenidos = []
        
        for i in range(3):
            titulo_template = random.choice(templates['titulo'])
            intro_template = random.choice(templates['introduccion'])
            contenido_template = random.choice(templates['contenido'])
            
            titulo = self._replace_placeholders(titulo_template, data)
            introduccion = self._replace_placeholders(intro_template, data)
            contenido = self._replace_placeholders(contenido_template, data)
            
            titulos.append(titulo)
            introducciones.append(introduccion)
            contenidos.append(contenido)
        
        return {
            'titulos': titulos,
            'introducciones': introducciones,
            'contenidos': contenidos,
            'variantes': [
                {
                    'titulo': titulos[i],
                    'introduccion': introducciones[i],
                    'contenido': contenidos[i],
                    'longitud_total': len(titulos[i]) + len(introducciones[i]) + len(contenidos[i]),
                    'palabras_clave': self._extract_keywords(contenidos[i])
                }
                for i in range(3)
            ]
        }
    
    def _generate_landing_page_content(self, data: Dict) -> Dict[str, Any]:
        """Genera contenido para landing page"""
        templates = self.content_templates['landing_pages']
        
        # Generar múltiples variantes
        headlines = []
        subheadlines = []
        beneficios = []
        ctas = []
        
        for i in range(3):
            headline_template = random.choice(templates['headline'])
            subheadline_template = random.choice(templates['subheadline'])
            beneficios_template = random.choice(templates['beneficios'])
            cta_template = random.choice(templates['call_to_action'])
            
            headline = self._replace_placeholders(headline_template, data)
            subheadline = self._replace_placeholders(subheadline_template, data)
            beneficios_text = self._replace_placeholders(beneficios_template, data)
            cta = self._replace_placeholders(cta_template, data)
            
            headlines.append(headline)
            subheadlines.append(subheadline)
            beneficios.append(beneficios_text)
            ctas.append(cta)
        
        return {
            'headlines': headlines,
            'subheadlines': subheadlines,
            'beneficios': beneficios,
            'call_to_actions': ctas,
            'variantes': [
                {
                    'headline': headlines[i],
                    'subheadline': subheadlines[i],
                    'beneficios': beneficios[i],
                    'call_to_action': ctas[i],
                    'score_conversion': self._calculate_conversion_score(
                        headlines[i], subheadlines[i], ctas[i]
                    )
                }
                for i in range(3)
            ]
        }
    
    def _replace_placeholders(self, template: str, data: Dict) -> str:
        """Reemplaza placeholders en las plantillas"""
        result = template
        for key, value in data.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, str(value))
        return result
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extrae hashtags del texto"""
        hashtags = re.findall(r'#\w+', text)
        return hashtags
    
    def _count_emojis(self, text: str) -> int:
        """Cuenta emojis en el texto"""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "]+", flags=re.UNICODE)
        return len(emoji_pattern.findall(text))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrae palabras clave del texto"""
        # Palabras comunes a excluir
        stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'como', 'más', 'pero', 'sus', 'le', 'ha', 'me', 'si', 'sin', 'sobre', 'este', 'ya', 'entre', 'cuando', 'todo', 'esta', 'ser', 'son', 'dos', 'también', 'fue', 'había', 'era', 'muy', 'años', 'hasta', 'desde', 'está', 'mi', 'porque', 'qué', 'sólo', 'han', 'yo', 'hay', 'vez', 'puede', 'todos', 'así', 'nos', 'ni', 'parte', 'tiene', 'él', 'uno', 'donde', 'bien', 'tiempo', 'mismo', 'ahora', 'cada', 'e', 'vida', 'otro', 'después', 'te', 'otros', 'aunque', 'esa', 'esos', 'estas', 'estos', 'otra', 'otras', 'otros', 'otro', 'mismo', 'misma', 'mismos', 'mismas', 'todo', 'toda', 'todos', 'todas', 'cual', 'cuales', 'cuando', 'donde', 'como', 'quien', 'quienes', 'que', 'quien', 'quienes', 'cual', 'cuales', 'cuando', 'donde', 'como', 'quien', 'quienes'}
        
        # Limpiar y dividir texto
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filtrar palabras comunes y palabras cortas
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Contar frecuencia
        word_count = defaultdict(int)
        for word in keywords:
            word_count[word] += 1
        
        # Retornar las 10 palabras más frecuentes
        return sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def _calculate_conversion_score(self, headline: str, subheadline: str, cta: str) -> float:
        """Calcula un score de conversión para el contenido"""
        score = 0.0
        
        # Score por longitud del headline (óptimo entre 30-60 caracteres)
        headline_len = len(headline)
        if 30 <= headline_len <= 60:
            score += 0.3
        elif 20 <= headline_len <= 80:
            score += 0.2
        
        # Score por palabras de poder en headline
        power_words = ['descubre', 'secreto', 'revolucionario', 'exclusivo', 'gratis', 'ahora', 'última', 'oportunidad', 'solo', 'limitado']
        headline_lower = headline.lower()
        for word in power_words:
            if word in headline_lower:
                score += 0.1
        
        # Score por call to action
        cta_lower = cta.lower()
        if any(word in cta_lower for word in ['ahora', 'gratis', 'descargar', 'obtener', 'comenzar']):
            score += 0.2
        
        # Score por urgencia
        urgency_words = ['ahora', 'urgente', 'limitado', 'solo', 'última', 'oportunidad']
        if any(word in headline_lower for word in urgency_words):
            score += 0.2
        
        # Score por beneficio claro
        benefit_words = ['aumentar', 'mejorar', 'reducir', 'optimizar', 'acelerar', 'maximizar']
        if any(word in headline_lower for word in benefit_words):
            score += 0.1
        
        return min(1.0, score)
    
    def generate_content_campaign(self, campaign_ids: List[int], 
                                content_types: List[str]) -> Dict[str, Any]:
        """Genera contenido para múltiples campañas"""
        results = {
            'total_campaigns': len(campaign_ids),
            'content_types': content_types,
            'campaigns_content': [],
            'summary': {
                'total_variants': 0,
                'average_conversion_score': 0,
                'most_effective_type': None
            }
        }
        
        all_scores = []
        type_scores = defaultdict(list)
        
        for campaign_id in campaign_ids:
            campaign_content = {
                'campaign_id': campaign_id,
                'content_by_type': {}
            }
            
            for content_type in content_types:
                content = self.generate_content(campaign_id, content_type)
                
                if 'error' not in content:
                    campaign_content['content_by_type'][content_type] = content['content']
                    
                    # Calcular scores si es landing page
                    if content_type == 'landing_page':
                        for variant in content['content']['variantes']:
                            score = variant['score_conversion']
                            all_scores.append(score)
                            type_scores[content_type].append(score)
            
            results['campaigns_content'].append(campaign_content)
        
        # Calcular resumen
        if all_scores:
            results['summary']['total_variants'] = len(all_scores)
            results['summary']['average_conversion_score'] = np.mean(all_scores)
            
            # Encontrar tipo más efectivo
            if type_scores:
                avg_scores = {content_type: np.mean(scores) for content_type, scores in type_scores.items()}
                results['summary']['most_effective_type'] = max(avg_scores.keys(), key=lambda x: avg_scores[x])
        
        return results
    
    def optimize_content(self, content: str, target_metric: str = 'conversion') -> Dict[str, Any]:
        """Optimiza contenido existente"""
        optimizations = []
        
        # Optimizaciones para conversión
        if target_metric == 'conversion':
            # Verificar longitud del headline
            if len(content) > 60:
                optimizations.append({
                    'type': 'headline_length',
                    'issue': 'Headline muy largo',
                    'suggestion': 'Reducir a 30-60 caracteres para mejor legibilidad',
                    'priority': 'high'
                })
            
            # Verificar palabras de poder
            power_words = ['descubre', 'secreto', 'revolucionario', 'gratis', 'ahora']
            if not any(word in content.lower() for word in power_words):
                optimizations.append({
                    'type': 'power_words',
                    'issue': 'Falta de palabras de poder',
                    'suggestion': 'Agregar palabras que generen urgencia y emoción',
                    'priority': 'medium'
                })
            
            # Verificar call to action
            cta_words = ['ahora', 'descargar', 'obtener', 'comenzar', 'gratis']
            if not any(word in content.lower() for word in cta_words):
                optimizations.append({
                    'type': 'call_to_action',
                    'issue': 'Call to action débil',
                    'suggestion': 'Incluir acción clara y urgente',
                    'priority': 'high'
                })
        
        # Optimizaciones para engagement
        elif target_metric == 'engagement':
            # Verificar emojis
            emoji_count = self._count_emojis(content)
            if emoji_count == 0:
                optimizations.append({
                    'type': 'emojis',
                    'issue': 'Sin emojis',
                    'suggestion': 'Agregar emojis para aumentar engagement',
                    'priority': 'medium'
                })
            
            # Verificar hashtags
            hashtags = self._extract_hashtags(content)
            if len(hashtags) < 3:
                optimizations.append({
                    'type': 'hashtags',
                    'issue': 'Pocos hashtags',
                    'suggestion': 'Agregar 3-5 hashtags relevantes',
                    'priority': 'medium'
                })
        
        return {
            'original_content': content,
            'target_metric': target_metric,
            'optimizations': optimizations,
            'optimization_score': max(0, 1 - len(optimizations) * 0.2),
            'optimized_at': datetime.now().isoformat()
        }

def main():
    """Función principal de demostración"""
    print("=== SISTEMA DE IA GENERATIVA PARA CONTENIDO ===")
    
    # Inicializar generador
    generator = AIContentGenerator()
    
    # Generar contenido para una campaña
    print("Generando contenido de email marketing...")
    email_content = generator.generate_content(1, 'email_marketing')
    
    if 'error' not in email_content:
        print(f"\n📧 CONTENIDO DE EMAIL GENERADO")
        print(f"Campaña: {email_content['campaign_name']}")
        print(f"Variantes generadas: {len(email_content['content']['variantes'])}")
        
        for i, variant in enumerate(email_content['content']['variantes'], 1):
            print(f"\n--- Variante {i} ---")
            print(f"Asunto: {variant['asunto']}")
            print(f"Cuerpo: {variant['cuerpo'][:100]}...")
    
    # Generar contenido para redes sociales
    print(f"\n📱 GENERANDO CONTENIDO PARA REDES SOCIALES...")
    social_content = generator.generate_content(1, 'social_media')
    
    if 'error' not in social_content:
        print(f"\n📊 CONTENIDO SOCIAL GENERADO")
        for platform, posts in social_content['content'].items():
            print(f"\n{platform.upper()}:")
            for i, post in enumerate(posts, 1):
                print(f"  {i}. {post['contenido'][:50]}...")
    
    # Generar contenido de blog
    print(f"\n📝 GENERANDO CONTENIDO DE BLOG...")
    blog_content = generator.generate_content(1, 'blog_post')
    
    if 'error' not in blog_content:
        print(f"\n📄 CONTENIDO DE BLOG GENERADO")
        for i, variant in enumerate(blog_content['content']['variantes'], 1):
            print(f"\n--- Artículo {i} ---")
            print(f"Título: {variant['titulo']}")
            print(f"Introducción: {variant['introduccion'][:100]}...")
    
    # Generar contenido para landing page
    print(f"\n🌐 GENERANDO CONTENIDO DE LANDING PAGE...")
    landing_content = generator.generate_content(1, 'landing_page')
    
    if 'error' not in landing_content:
        print(f"\n🎯 CONTENIDO DE LANDING PAGE GENERADO")
        for i, variant in enumerate(landing_content['content']['variantes'], 1):
            print(f"\n--- Variante {i} ---")
            print(f"Headline: {variant['headline']}")
            print(f"Subheadline: {variant['subheadline']}")
            print(f"CTA: {variant['call_to_action']}")
            print(f"Score de conversión: {variant['score_conversion']:.2f}")
    
    # Generar contenido para múltiples campañas
    print(f"\n🔄 GENERANDO CONTENIDO MASIVO...")
    massive_content = generator.generate_content_campaign(
        campaign_ids=[1, 2, 3, 4, 5],
        content_types=['email_marketing', 'social_media', 'landing_page']
    )
    
    print(f"\n📈 RESUMEN DE GENERACIÓN MASIVA")
    print(f"Total de campañas: {massive_content['total_campaigns']}")
    print(f"Tipos de contenido: {massive_content['content_types']}")
    print(f"Total de variantes: {massive_content['summary']['total_variants']}")
    print(f"Score promedio de conversión: {massive_content['summary']['average_conversion_score']:.2f}")
    print(f"Tipo más efectivo: {massive_content['summary']['most_effective_type']}")
    
    # Optimizar contenido existente
    print(f"\n🔧 OPTIMIZANDO CONTENIDO...")
    sample_content = "Descubre cómo nuestra herramienta puede mejorar tu negocio"
    optimization = generator.optimize_content(sample_content, 'conversion')
    
    print(f"\n⚡ OPTIMIZACIÓN DE CONTENIDO")
    print(f"Contenido original: {optimization['original_content']}")
    print(f"Score de optimización: {optimization['optimization_score']:.2f}")
    print(f"Optimizaciones sugeridas: {len(optimization['optimizations'])}")
    
    for opt in optimization['optimizations']:
        print(f"• [{opt['priority'].upper()}] {opt['issue']}: {opt['suggestion']}")
    
    print(f"\n✅ Sistema de IA generativa configurado y funcionando")

if __name__ == "__main__":
    main()
