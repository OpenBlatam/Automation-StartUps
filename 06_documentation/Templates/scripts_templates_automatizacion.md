---
title: "Scripts Templates Automatizacion"
category: "06_documentation"
tags: ["script", "template"]
created: "2025-10-29"
path: "06_documentation/Templates/scripts_templates_automatizacion.md"
---

# 🤖 SCRIPTS Y TEMPLATES DE AUTOMATIZACIÓN

## 🎯 RESUMEN EJECUTIVO

**Fecha:** Enero 2025  
**Empresa:** BLATAM  
**Documento:** Scripts y Templates de Automatización  
**Versión:** 1.0  
**Estado:** ✅ SCRIPTS LISTOS PARA USO

### **Objetivo**
Crear scripts ejecutables, templates reutilizables y herramientas de automatización listas para implementar inmediatamente en los procesos críticos identificados.

---

## 🔧 SCRIPTS DE AUTOMATIZACIÓN LISTOS

### **1. AUTOMATIZACIÓN DE LEAD SCORING**

```python
# lead_scoring_automation.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import requests

class LeadScoringAutomation:
    def __init__(self):
        self.scoring_weights = {
            'company_size': 0.25,
            'job_title': 0.25,
            'pain_points': 0.25,
            'timeline': 0.25
        }
        self.scoring_rules = self.load_scoring_rules()
    
    def load_scoring_rules(self):
        return {
            'company_size': {
                'enterprise': 25,
                'mid_market': 20,
                'smb': 15,
                'startup': 10
            },
            'job_title': {
                'c_level': 25,
                'vp_director': 20,
                'manager': 15,
                'coordinator': 10,
                'other': 5
            },
            'pain_points': {
                'high': 25,
                'medium': 15,
                'low': 5
            },
            'timeline': {
                'immediate': 25,
                '30_days': 20,
                '90_days': 15,
                '6_months': 10,
                'long_term': 5
            }
        }
    
    def score_company_size(self, company_size):
        """Score basado en tamaño de empresa"""
        size_mapping = {
            'enterprise': ['enterprise', 'large', 'fortune 500'],
            'mid_market': ['mid-market', 'medium', 'mid'],
            'smb': ['small', 'sme', 'small business'],
            'startup': ['startup', 'early stage', 'seed']
        }
        
        company_size_lower = company_size.lower()
        
        for category, keywords in size_mapping.items():
            if any(keyword in company_size_lower for keyword in keywords):
                return self.scoring_rules['company_size'][category]
        
        return 10  # Default score
    
    def score_job_title(self, job_title):
        """Score basado en título del trabajo"""
        job_title_lower = job_title.lower()
        
        if any(title in job_title_lower for title in ['ceo', 'cto', 'cfo', 'president', 'founder']):
            return self.scoring_rules['job_title']['c_level']
        elif any(title in job_title_lower for title in ['vp', 'vice president', 'director', 'head']):
            return self.scoring_rules['job_title']['vp_director']
        elif 'manager' in job_title_lower:
            return self.scoring_rules['job_title']['manager']
        elif any(title in job_title_lower for title in ['coordinator', 'specialist', 'analyst']):
            return self.scoring_rules['job_title']['coordinator']
        else:
            return self.scoring_rules['job_title']['other']
    
    def score_pain_points(self, pain_points_text):
        """Score basado en pain points"""
        if not pain_points_text:
            return 5
        
        pain_points_lower = pain_points_text.lower()
        
        # Keywords que indican alta urgencia
        high_urgency_keywords = [
            'urgent', 'critical', 'emergency', 'immediate', 'asap',
            'losing money', 'revenue loss', 'competitive disadvantage',
            'compliance issues', 'security breach', 'system down'
        ]
        
        # Keywords que indican necesidad media
        medium_urgency_keywords = [
            'important', 'needed', 'required', 'should', 'better',
            'improve', 'optimize', 'efficiency', 'cost reduction'
        ]
        
        high_count = sum(1 for keyword in high_urgency_keywords if keyword in pain_points_lower)
        medium_count = sum(1 for keyword in medium_urgency_keywords if keyword in pain_points_lower)
        
        if high_count >= 2:
            return self.scoring_rules['pain_points']['high']
        elif medium_count >= 2 or high_count >= 1:
            return self.scoring_rules['pain_points']['medium']
        else:
            return self.scoring_rules['pain_points']['low']
    
    def score_timeline(self, timeline_text):
        """Score basado en timeline"""
        if not timeline_text:
            return 5
        
        timeline_lower = timeline_text.lower()
        
        if any(word in timeline_lower for word in ['immediate', 'asap', 'urgent', 'now']):
            return self.scoring_rules['timeline']['immediate']
        elif any(word in timeline_lower for word in ['30 days', 'month', 'this month']):
            return self.scoring_rules['timeline']['30_days']
        elif any(word in timeline_lower for word in ['90 days', 'quarter', '3 months']):
            return self.scoring_rules['timeline']['90_days']
        elif any(word in timeline_lower for word in ['6 months', 'half year', 'next year']):
            return self.scoring_rules['timeline']['6_months']
        else:
            return self.scoring_rules['timeline']['long_term']
    
    def calculate_lead_score(self, lead_data):
        """Calcular score total del lead"""
        scores = {}
        
        # Score por tamaño de empresa
        scores['company_size'] = self.score_company_size(lead_data.get('company_size', ''))
        
        # Score por título del trabajo
        scores['job_title'] = self.score_job_title(lead_data.get('job_title', ''))
        
        # Score por pain points
        scores['pain_points'] = self.score_pain_points(lead_data.get('pain_points', ''))
        
        # Score por timeline
        scores['timeline'] = self.score_timeline(lead_data.get('timeline', ''))
        
        # Calcular score total ponderado
        total_score = sum(scores[category] * self.scoring_weights[category] 
                         for category in scores.keys())
        
        # Categorizar lead
        if total_score >= 80:
            category = 'HOT'
        elif total_score >= 60:
            category = 'WARM'
        elif total_score >= 40:
            category = 'COLD'
        else:
            category = 'INACTIVE'
        
        return {
            'total_score': round(total_score, 2),
            'category': category,
            'scores_breakdown': scores,
            'recommended_actions': self.get_recommended_actions(category, total_score)
        }
    
    def get_recommended_actions(self, category, score):
        """Obtener acciones recomendadas basadas en categoría y score"""
        actions = {
            'HOT': [
                'Contactar inmediatamente',
                'Programar demo personalizada',
                'Enviar propuesta preliminar',
                'Involucrar ejecutivo senior'
            ],
            'WARM': [
                'Enviar información adicional',
                'Programar llamada de seguimiento',
                'Incluir en nurturing sequence',
                'Enviar case studies relevantes'
            ],
            'COLD': [
                'Incluir en email marketing',
                'Enviar contenido educativo',
                'Seguimiento mensual',
                'Re-evaluar en 30 días'
            ],
            'INACTIVE': [
                'Archivar temporalmente',
                'Re-evaluar en 90 días',
                'Enviar newsletter mensual',
                'Considerar para remarketing'
            ]
        }
        
        return actions.get(category, [])
    
    def process_leads_batch(self, leads_data):
        """Procesar múltiples leads en lote"""
        results = []
        
        for lead in leads_data:
            scoring_result = self.calculate_lead_score(lead)
            
            result = {
                'lead_id': lead.get('id'),
                'email': lead.get('email'),
                'company': lead.get('company'),
                'scoring_result': scoring_result,
                'processed_at': datetime.now().isoformat()
            }
            
            results.append(result)
        
        return results
    
    def export_results(self, results, filename='lead_scoring_results.json'):
        """Exportar resultados a archivo"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ Resultados exportados a {filename}")
    
    def generate_report(self, results):
        """Generar reporte de scoring"""
        total_leads = len(results)
        hot_leads = len([r for r in results if r['scoring_result']['category'] == 'HOT'])
        warm_leads = len([r for r in results if r['scoring_result']['category'] == 'WARM'])
        cold_leads = len([r for r in results if r['scoring_result']['category'] == 'COLD'])
        inactive_leads = len([r for r in results if r['scoring_result']['category'] == 'INACTIVE'])
        
        avg_score = np.mean([r['scoring_result']['total_score'] for r in results])
        
        report = {
            'summary': {
                'total_leads': total_leads,
                'hot_leads': hot_leads,
                'warm_leads': warm_leads,
                'cold_leads': cold_leads,
                'inactive_leads': inactive_leads,
                'average_score': round(avg_score, 2)
            },
            'distribution': {
                'hot_percentage': round((hot_leads / total_leads) * 100, 2),
                'warm_percentage': round((warm_leads / total_leads) * 100, 2),
                'cold_percentage': round((cold_leads / total_leads) * 100, 2),
                'inactive_percentage': round((inactive_leads / total_leads) * 100, 2)
            },
            'recommendations': self.get_recommendations(hot_leads, warm_leads, total_leads)
        }
        
        return report
    
    def get_recommendations(self, hot_leads, warm_leads, total_leads):
        """Obtener recomendaciones basadas en resultados"""
        recommendations = []
        
        hot_percentage = (hot_leads / total_leads) * 100
        
        if hot_percentage < 10:
            recommendations.append("Aumentar calidad de leads - revisar fuentes de generación")
        
        if hot_percentage > 30:
            recommendations.append("Excelente calidad de leads - considerar aumentar capacidad de ventas")
        
        warm_percentage = (warm_leads / total_leads) * 100
        
        if warm_percentage > 40:
            recommendations.append("Muchos leads tibios - mejorar nurturing sequence")
        
        recommendations.append("Implementar seguimiento automático por categoría")
        recommendations.append("Revisar criterios de scoring mensualmente")
        
        return recommendations

# Ejemplo de uso
if __name__ == "__main__":
    # Datos de ejemplo
    sample_leads = [
        {
            'id': 1,
            'email': 'ceo@techcorp.com',
            'company': 'TechCorp',
            'company_size': 'enterprise',
            'job_title': 'CEO',
            'pain_points': 'urgent need to reduce costs and improve efficiency',
            'timeline': 'immediate'
        },
        {
            'id': 2,
            'email': 'manager@startup.com',
            'company': 'StartupXYZ',
            'company_size': 'startup',
            'job_title': 'Marketing Manager',
            'pain_points': 'looking for better tools',
            'timeline': '6 months'
        }
    ]
    
    # Inicializar sistema
    scoring_system = LeadScoringAutomation()
    
    # Procesar leads
    results = scoring_system.process_leads_batch(sample_leads)
    
    # Generar reporte
    report = scoring_system.generate_report(results)
    
    # Exportar resultados
    scoring_system.export_results(results)
    
    print("📊 Reporte de Lead Scoring:")
    print(json.dumps(report, indent=2))
```

---

### **2. AUTOMATIZACIÓN DE GENERACIÓN DE CONTENIDO**

```python
# content_generation_automation.py
import openai
import requests
import json
from datetime import datetime, timedelta
import schedule
import time
import pandas as pd

class ContentGenerationAutomation:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key="tu_openai_api_key")
        self.buffer_token = "tu_buffer_token"
        self.industries = [
            'technology', 'healthcare', 'finance', 'retail', 'education',
            'manufacturing', 'real_estate', 'consulting', 'non_profit', 'government'
        ]
        self.content_templates = self.load_content_templates()
        self.optimal_times = self.load_optimal_times()
    
    def load_content_templates(self):
        return {
            'linkedin_post': {
                'template': """
                🚀 [INDUSTRY] Innovation Alert!
                
                [CONTENT]
                
                💡 Key insights:
                • [INSIGHT_1]
                • [INSIGHT_2]
                • [INSIGHT_3]
                
                🔥 What's your take on this trend?
                
                #AI #Innovation #[INDUSTRY] #Technology #FutureOfWork
                """,
                'max_length': 300
            },
            'email_newsletter': {
                'template': """
                Subject: [INDUSTRY] Weekly Insights - [DATE]
                
                Hi [FIRST_NAME],
                
                This week in [INDUSTRY]:
                
                [CONTENT]
                
                📈 Trending Topics:
                [TOPIC_1]
                [TOPIC_2]
                [TOPIC_3]
                
                🎯 Action Items:
                [ACTION_1]
                [ACTION_2]
                
                Best regards,
                BLATAM Team
                """,
                'max_length': 500
            },
            'blog_post': {
                'template': """
                # [TITLE]
                
                ## Introduction
                [INTRODUCTION]
                
                ## Main Content
                [MAIN_CONTENT]
                
                ## Key Takeaways
                1. [TAKEAWAY_1]
                2. [TAKEAWAY_2]
                3. [TAKEAWAY_3]
                
                ## Conclusion
                [CONCLUSION]
                
                ## Meta Description
                [META_DESCRIPTION]
                """,
                'max_length': 1000
            }
        }
    
    def load_optimal_times(self):
        return {
            'linkedin': {
                'monday': '09:00',
                'tuesday': '09:00',
                'wednesday': '09:00',
                'thursday': '09:00',
                'friday': '09:00'
            },
            'twitter': {
                'monday': '12:00',
                'tuesday': '12:00',
                'wednesday': '12:00',
                'thursday': '12:00',
                'friday': '12:00'
            },
            'facebook': {
                'monday': '15:00',
                'tuesday': '15:00',
                'wednesday': '15:00',
                'thursday': '15:00',
                'friday': '15:00'
            }
        }
    
    def generate_industry_content(self, industry, content_type, topic=None):
        """Generar contenido específico para industria"""
        if not topic:
            topic = f"tendencias actuales en {industry}"
        
        prompt = f"""
        Eres un experto en marketing de contenido para la industria {industry}.
        
        Crea contenido de tipo {content_type} sobre: {topic}
        
        El contenido debe ser:
        - Profesional pero accesible
        - Específico para {industry}
        - Incluir insights accionables
        - Usar lenguaje que resuene con profesionales de {industry}
        - Incluir estadísticas o datos relevantes cuando sea apropiado
        
        Formato: {content_type}
        Longitud máxima: {self.content_templates[content_type]['max_length']} caracteres
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Eres un experto en marketing de contenido y copywriting."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Error generando contenido: {e}")
            return None
    
    def format_content_with_template(self, content, content_type, industry, **kwargs):
        """Formatear contenido usando template"""
        template = self.content_templates[content_type]['template']
        
        # Reemplazar placeholders
        formatted_content = template.replace('[INDUSTRY]', industry.title())
        formatted_content = formatted_content.replace('[CONTENT]', content)
        formatted_content = formatted_content.replace('[DATE]', datetime.now().strftime('%B %d, %Y'))
        
        # Reemplazar placeholders adicionales
        for key, value in kwargs.items():
            placeholder = f'[{key.upper()}]'
            formatted_content = formatted_content.replace(placeholder, str(value))
        
        return formatted_content
    
    def schedule_content_buffer(self, content, platforms, scheduled_time=None):
        """Programar contenido en Buffer"""
        if not scheduled_time:
            scheduled_time = datetime.now() + timedelta(hours=1)
        
        for platform in platforms:
            profile_id = self.get_buffer_profile_id(platform)
            
            if profile_id:
                schedule_data = {
                    'text': content,
                    'profile_ids': [profile_id],
                    'scheduled_at': scheduled_time.isoformat(),
                    'media': self.generate_media_if_needed(content, platform)
                }
                
                try:
                    response = requests.post(
                        'https://api.bufferapp.com/v1/updates/create.json',
                        headers={'Authorization': f'Bearer {self.buffer_token}'},
                        data=schedule_data
                    )
                    
                    if response.status_code == 200:
                        print(f"✅ Contenido programado en {platform} para {scheduled_time}")
                    else:
                        print(f"❌ Error programando en {platform}: {response.text}")
                        
                except Exception as e:
                    print(f"❌ Error programando contenido: {e}")
    
    def get_buffer_profile_id(self, platform):
        """Obtener ID del perfil de Buffer"""
        profile_ids = {
            'linkedin': 'tu_linkedin_profile_id',
            'twitter': 'tu_twitter_profile_id',
            'facebook': 'tu_facebook_profile_id',
            'instagram': 'tu_instagram_profile_id'
        }
        return profile_ids.get(platform)
    
    def generate_media_if_needed(self, content, platform):
        """Generar media si es necesario"""
        # Implementar generación de imágenes con DALL-E o similar
        return None
    
    def create_content_calendar(self, days_ahead=30):
        """Crear calendario de contenido automático"""
        calendar = []
        current_date = datetime.now()
        
        for day in range(days_ahead):
            date = current_date + timedelta(days=day)
            weekday = date.strftime('%A').lower()
            
            # Generar contenido para cada industria (rotar)
            industry_index = day % len(self.industries)
            industry = self.industries[industry_index]
            
            # Generar diferentes tipos de contenido
            content_types = ['linkedin_post', 'email_newsletter']
            
            for content_type in content_types:
                content = self.generate_industry_content(
                    industry=industry,
                    content_type=content_type,
                    topic=f"tendencias {industry} {date.strftime('%B %Y')}"
                )
                
                if content:
                    formatted_content = self.format_content_with_template(
                        content, content_type, industry
                    )
                    
                    calendar.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'weekday': weekday,
                        'industry': industry,
                        'content_type': content_type,
                        'content': formatted_content,
                        'platforms': ['linkedin'] if content_type == 'linkedin_post' else ['email'],
                        'status': 'scheduled'
                    })
        
        return calendar
    
    def export_content_calendar(self, calendar, filename='content_calendar.json'):
        """Exportar calendario de contenido"""
        with open(filename, 'w') as f:
            json.dump(calendar, f, indent=2)
        
        print(f"✅ Calendario exportado a {filename}")
    
    def generate_daily_content(self):
        """Generar contenido diario automático"""
        print("🚀 Generando contenido diario...")
        
        # Obtener industria del día
        day_of_year = datetime.now().timetuple().tm_yday
        industry = self.industries[day_of_year % len(self.industries)]
        
        # Generar LinkedIn post
        linkedin_content = self.generate_industry_content(
            industry=industry,
            content_type='linkedin_post'
        )
        
        if linkedin_content:
            formatted_content = self.format_content_with_template(
                linkedin_content, 'linkedin_post', industry
            )
            
            # Programar para horario óptimo
            optimal_time = self.get_optimal_time('linkedin')
            self.schedule_content_buffer(
                content=formatted_content,
                platforms=['linkedin'],
                scheduled_time=optimal_time
            )
        
        print(f"✅ Contenido generado para {industry}")
    
    def get_optimal_time(self, platform):
        """Obtener horario óptimo para plataforma"""
        weekday = datetime.now().strftime('%A').lower()
        time_str = self.optimal_times[platform].get(weekday, '09:00')
        
        # Convertir a datetime
        today = datetime.now().date()
        optimal_datetime = datetime.combine(today, datetime.strptime(time_str, '%H:%M').time())
        
        return optimal_datetime
    
    def run_content_automation(self):
        """Ejecutar automatización de contenido"""
        print("🤖 Iniciando automatización de contenido...")
        
        # Generar contenido diario
        self.generate_daily_content()
        
        # Crear calendario semanal
        weekly_calendar = self.create_content_calendar(days_ahead=7)
        
        # Exportar calendario
        self.export_content_calendar(weekly_calendar)
        
        print("✅ Automatización de contenido completada")

# Configurar tareas programadas
def setup_content_schedule():
    content_system = ContentGenerationAutomation()
    
    # Programar generación diaria a las 8:00 AM
    schedule.every().day.at("08:00").do(content_system.generate_daily_content)
    
    # Programar generación semanal de blog posts los lunes
    schedule.every().monday.at("09:00").do(
        lambda: content_system.generate_industry_content('technology', 'blog_post')
    )
    
    print("📅 Tareas de contenido programadas")
    
    # Ejecutar tareas programadas
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # Ejecutar una vez
    content_system = ContentGenerationAutomation()
    content_system.run_content_automation()
    
    # O ejecutar con schedule
    # setup_content_schedule()
```

---

### **3. AUTOMATIZACIÓN DE SOPORTE AL CLIENTE**

```python
# customer_support_automation.py
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import re

class CustomerSupportAutomation:
    def __init__(self):
        self.zendesk_config = self.load_zendesk_config()
        self.intercom_config = self.load_intercom_config()
        self.knowledge_base = self.load_knowledge_base()
        self.escalation_rules = self.load_escalation_rules()
    
    def load_zendesk_config(self):
        return {
            'subdomain': 'tu_subdomain',
            'api_token': 'tu_api_token',
            'email': 'support@blatam.com'
        }
    
    def load_intercom_config(self):
        return {
            'app_id': 'tu_app_id',
            'api_key': 'tu_api_key'
        }
    
    def load_knowledge_base(self):
        return {
            'billing': [
                'How to update payment method',
                'How to cancel subscription',
                'How to change billing cycle',
                'How to get invoice'
            ],
            'technical': [
                'How to reset password',
                'How to integrate API',
                'How to troubleshoot login',
                'How to configure settings'
            ],
            'general': [
                'What is BLATAM',
                'How to get started',
                'How to contact support',
                'How to request demo'
            ]
        }
    
    def load_escalation_rules(self):
        return {
            'urgent_keywords': ['urgent', 'critical', 'emergency', 'asap', 'down', 'broken'],
            'billing_keywords': ['billing', 'payment', 'invoice', 'charge', 'refund'],
            'technical_keywords': ['error', 'bug', 'issue', 'problem', 'not working'],
            'escalation_thresholds': {
                'response_time': 2,  # hours
                'satisfaction_score': 3,  # out of 5
                'resolution_time': 24  # hours
            }
        }
    
    def categorize_ticket(self, ticket_content):
        """Categorizar ticket automáticamente"""
        content_lower = ticket_content.lower()
        
        # Detectar categoría
        if any(keyword in content_lower for keyword in self.escalation_rules['billing_keywords']):
            category = 'billing'
        elif any(keyword in content_lower for keyword in self.escalation_rules['technical_keywords']):
            category = 'technical'
        else:
            category = 'general'
        
        # Detectar urgencia
        if any(keyword in content_lower for keyword in self.escalation_rules['urgent_keywords']):
            priority = 'urgent'
        elif 'important' in content_lower or 'asap' in content_lower:
            priority = 'high'
        else:
            priority = 'normal'
        
        return {
            'category': category,
            'priority': priority,
            'confidence': self.calculate_confidence(content_lower, category, priority)
        }
    
    def calculate_confidence(self, content, category, priority):
        """Calcular confianza en la categorización"""
        confidence = 0.5  # Base confidence
        
        # Aumentar confianza basado en keywords
        if category == 'billing':
            keyword_count = sum(1 for keyword in self.escalation_rules['billing_keywords'] 
                              if keyword in content)
            confidence += keyword_count * 0.1
        
        elif category == 'technical':
            keyword_count = sum(1 for keyword in self.escalation_rules['technical_keywords'] 
                              if keyword in content)
            confidence += keyword_count * 0.1
        
        if priority == 'urgent':
            keyword_count = sum(1 for keyword in self.escalation_rules['urgent_keywords'] 
                              if keyword in content)
            confidence += keyword_count * 0.15
        
        return min(confidence, 1.0)
    
    def generate_auto_response(self, ticket_data):
        """Generar respuesta automática"""
        category = ticket_data['category']
        priority = ticket_data['priority']
        
        # Respuestas base por categoría
        responses = {
            'billing': {
                'urgent': "Thank you for contacting us about your billing inquiry. We understand this is urgent and our billing team will respond within 1 hour.",
                'high': "Thank you for your billing inquiry. Our billing team will respond within 2 hours.",
                'normal': "Thank you for your billing inquiry. Our billing team will respond within 4 hours."
            },
            'technical': {
                'urgent': "Thank you for reporting this technical issue. We understand this is urgent and our technical team will respond within 1 hour.",
                'high': "Thank you for reporting this technical issue. Our technical team will respond within 2 hours.",
                'normal': "Thank you for reporting this technical issue. Our technical team will respond within 4 hours."
            },
            'general': {
                'urgent': "Thank you for contacting us. We understand this is urgent and will respond within 1 hour.",
                'high': "Thank you for contacting us. We will respond within 2 hours.",
                'normal': "Thank you for contacting us. We will respond within 4 hours."
            }
        }
        
        base_response = responses[category][priority]
        
        # Agregar información específica
        if category == 'billing':
            base_response += "\n\nIn the meantime, you can:\n- Update your payment method in your account settings\n- View your invoices in the billing section\n- Contact our billing team directly at billing@blatam.com"
        
        elif category == 'technical':
            base_response += "\n\nIn the meantime, you can:\n- Check our knowledge base for common solutions\n- Try refreshing your browser or clearing cache\n- Contact our technical team directly at tech@blatam.com"
        
        return base_response
    
    def suggest_solutions(self, ticket_content, category):
        """Sugerir soluciones basadas en el contenido"""
        content_lower = ticket_content.lower()
        suggestions = []
        
        if category == 'billing':
            if 'payment' in content_lower:
                suggestions.append("Check if your payment method is up to date")
            if 'invoice' in content_lower:
                suggestions.append("Download your invoice from the billing section")
            if 'cancel' in content_lower:
                suggestions.append("Review our cancellation policy")
        
        elif category == 'technical':
            if 'login' in content_lower:
                suggestions.append("Try resetting your password")
            if 'error' in content_lower:
                suggestions.append("Check our troubleshooting guide")
            if 'api' in content_lower:
                suggestions.append("Review our API documentation")
        
        return suggestions
    
    def create_zendesk_ticket(self, ticket_data):
        """Crear ticket en Zendesk"""
        url = f"https://{self.zendesk_config['subdomain']}.zendesk.com/api/v2/tickets.json"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Basic {self.zendesk_config['api_token']}"
        }
        
        ticket_payload = {
            'ticket': {
                'subject': ticket_data['subject'],
                'description': ticket_data['description'],
                'priority': ticket_data['priority'],
                'type': ticket_data['category'],
                'status': 'new',
                'requester': {
                    'name': ticket_data['requester_name'],
                    'email': ticket_data['requester_email']
                },
                'tags': ticket_data.get('tags', []),
                'custom_fields': [
                    {
                        'id': 'automated_response',
                        'value': 'true'
                    }
                ]
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=ticket_payload)
            
            if response.status_code == 201:
                ticket_id = response.json()['ticket']['id']
                print(f"✅ Ticket creado: {ticket_id}")
                return ticket_id
            else:
                print(f"❌ Error creando ticket: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creando ticket: {e}")
            return None
    
    def send_auto_response(self, ticket_id, response_text):
        """Enviar respuesta automática"""
        url = f"https://{self.zendesk_config['subdomain']}.zendesk.com/api/v2/tickets/{ticket_id}.json"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Basic {self.zendesk_config['api_token']}"
        }
        
        update_payload = {
            'ticket': {
                'comment': {
                    'body': response_text,
                    'public': True
                }
            }
        }
        
        try:
            response = requests.put(url, headers=headers, json=update_payload)
            
            if response.status_code == 200:
                print(f"✅ Respuesta automática enviada para ticket {ticket_id}")
                return True
            else:
                print(f"❌ Error enviando respuesta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error enviando respuesta: {e}")
            return False
    
    def process_support_request(self, request_data):
        """Procesar solicitud de soporte completa"""
        print("🎫 Procesando solicitud de soporte...")
        
        # Categorizar ticket
        categorization = self.categorize_ticket(request_data['description'])
        
        # Generar respuesta automática
        auto_response = self.generate_auto_response(categorization)
        
        # Sugerir soluciones
        suggestions = self.suggest_solutions(request_data['description'], categorization['category'])
        
        # Crear ticket en Zendesk
        ticket_data = {
            'subject': request_data['subject'],
            'description': request_data['description'],
            'priority': categorization['priority'],
            'category': categorization['category'],
            'requester_name': request_data['requester_name'],
            'requester_email': request_data['requester_email'],
            'tags': ['automated', categorization['category'], categorization['priority']]
        }
        
        ticket_id = self.create_zendesk_ticket(ticket_data)
        
        if ticket_id:
            # Enviar respuesta automática
            self.send_auto_response(ticket_id, auto_response)
            
            # Log del procesamiento
            self.log_support_request(ticket_id, categorization, suggestions)
        
        return {
            'ticket_id': ticket_id,
            'categorization': categorization,
            'auto_response': auto_response,
            'suggestions': suggestions
        }
    
    def log_support_request(self, ticket_id, categorization, suggestions):
        """Registrar solicitud de soporte"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ticket_id': ticket_id,
            'category': categorization['category'],
            'priority': categorization['priority'],
            'confidence': categorization['confidence'],
            'suggestions': suggestions
        }
        
        with open('support_requests.log', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def generate_support_report(self, days=7):
        """Generar reporte de soporte"""
        # Simular datos (reemplazar con datos reales de Zendesk)
        report_data = {
            'total_tickets': 150,
            'resolved_tickets': 140,
            'avg_response_time': 1.5,  # hours
            'avg_resolution_time': 8.5,  # hours
            'satisfaction_score': 4.6,
            'categories': {
                'billing': 45,
                'technical': 60,
                'general': 45
            },
            'priorities': {
                'urgent': 15,
                'high': 35,
                'normal': 100
            }
        }
        
        return report_data

# Ejemplo de uso
if __name__ == "__main__":
    # Datos de ejemplo
    sample_request = {
        'subject': 'Payment issue - urgent',
        'description': 'I am unable to process my payment and this is urgent. My subscription is about to expire.',
        'requester_name': 'John Doe',
        'requester_email': 'john@example.com'
    }
    
    # Inicializar sistema
    support_system = CustomerSupportAutomation()
    
    # Procesar solicitud
    result = support_system.process_support_request(sample_request)
    
    print("📊 Resultado del procesamiento:")
    print(json.dumps(result, indent=2))
    
    # Generar reporte
    report = support_system.generate_support_report()
    print("\n📈 Reporte de soporte:")
    print(json.dumps(report, indent=2))
```

---

## 📋 TEMPLATES DE IMPLEMENTACIÓN

### **TEMPLATE DE CONFIGURACIÓN DE HUBSPOT**

```json
{
  "hubspot_config": {
    "properties": {
      "lead_score": {
        "name": "lead_score",
        "label": "Lead Score",
        "type": "number",
        "fieldType": "number",
        "groupName": "contactinformation"
      },
      "lead_status": {
        "name": "lead_status",
        "label": "Lead Status",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "contactinformation",
        "options": [
          {"label": "HOT", "value": "hot"},
          {"label": "WARM", "value": "warm"},
          {"label": "COLD", "value": "cold"},
          {"label": "INACTIVE", "value": "inactive"}
        ]
      },
      "industry": {
        "name": "industry",
        "label": "Industry",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "contactinformation",
        "options": [
          {"label": "Technology", "value": "technology"},
          {"label": "Healthcare", "value": "healthcare"},
          {"label": "Finance", "value": "finance"},
          {"label": "Retail", "value": "retail"},
          {"label": "Education", "value": "education"}
        ]
      }
    },
    "workflows": {
      "lead_scoring": {
        "name": "Automated Lead Scoring",
        "type": "DRIP_DELAY",
        "enabled": true,
        "goal": "CONTACT_GOAL",
        "enrollmentTrigger": "contact_property_changed",
        "actions": [
          {
            "type": "calculate_score",
            "property": "lead_score",
            "criteria": "bant"
          },
          {
            "type": "update_status",
            "property": "lead_status",
            "value": "calculated"
          }
        ]
      }
    }
  }
}
```

### **TEMPLATE DE CONFIGURACIÓN DE ZENDESK**

```json
{
  "zendesk_config": {
    "ticket_forms": {
      "billing": {
        "name": "Billing Support",
        "fields": [
          {
            "name": "issue_type",
            "label": "Issue Type",
            "type": "select",
            "options": [
              "Payment Method",
              "Invoice",
              "Subscription",
              "Refund",
              "Other"
            ]
          },
          {
            "name": "urgency",
            "label": "Urgency",
            "type": "select",
            "options": [
              "Low",
              "Medium",
              "High",
              "Critical"
            ]
          }
        ]
      },
      "technical": {
        "name": "Technical Support",
        "fields": [
          {
            "name": "issue_type",
            "label": "Issue Type",
            "type": "select",
            "options": [
              "Login Issues",
              "API Problems",
              "Integration Issues",
              "Performance",
              "Other"
            ]
          },
          {
            "name": "error_message",
            "label": "Error Message",
            "type": "textarea"
          }
        ]
      }
    },
    "automation_rules": {
      "auto_assign": {
        "name": "Auto Assign Tickets",
        "conditions": [
          {
            "field": "type",
            "operator": "is",
            "value": "billing"
          }
        ],
        "actions": [
          {
            "type": "assign",
            "assignee": "billing_team"
          }
        ]
      }
    }
  }
}
```

---

## 🎯 PRÓXIMOS PASOS INMEDIATOS

### **ESTA SEMANA - IMPLEMENTACIÓN:**

1. **Lunes:** Ejecutar script de lead scoring
2. **Martes:** Configurar automatización de contenido
3. **Miércoles:** Implementar soporte automatizado
4. **Jueves:** Probar todos los scripts
5. **Viernes:** Optimizar y ajustar

### **PRÓXIMAS 2 SEMANAS - ESCALAMIENTO:**

1. **Semana 1:** Implementar en producción
2. **Semana 2:** Monitorear y optimizar
3. **Medición:** Evaluar resultados
4. **Ajustes:** Mejorar basado en datos

---

## 📞 SOPORTE TÉCNICO

**Para implementación:** tech@blatam.com  
**Para scripts:** scripts@blatam.com  
**Para soporte:** support@blatam.com  

---

*Documento creado el: 2025-01-27*  
*Versión: 1.0*  
*Próxima actualización: 2025-02-27*



