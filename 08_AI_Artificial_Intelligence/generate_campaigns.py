#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Simplificado de 1000 Campañas de Marketing con IA
"""

import json
import random
from datetime import datetime, timedelta

def generate_campaigns():
    """Genera 1000 campañas de marketing con IA"""
    
    categories = [
        "Personalización con IA", "Análisis Predictivo", "Chatbots y Asistentes Virtuales",
        "Generación de Contenido", "Optimización de Conversión", "Segmentación Avanzada",
        "Automatización de Marketing", "Análisis de Sentimientos", "Recomendaciones Inteligentes",
        "Marketing Visual con IA"
    ]
    
    channels = [
        "Redes Sociales", "Email Marketing", "SEM/PPC", "Display Advertising",
        "Content Marketing", "Influencer Marketing", "Video Marketing",
        "Mobile Marketing", "E-commerce", "Marketing Automation"
    ]
    
    technologies = [
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "Predictive Analytics", "Neural Networks", "Reinforcement Learning",
        "Generative AI", "Sentiment Analysis", "Recommendation Engines"
    ]
    
    objectives = [
        "Aumentar conversiones", "Mejorar engagement", "Generar leads",
        "Aumentar ventas", "Mejorar retención", "Optimizar ROI",
        "Expandir alcance", "Mejorar experiencia de usuario",
        "Reducir costos", "Aumentar brand awareness"
    ]
    
    verticals = [
        "E-commerce", "Fintech", "Healthcare", "Education", "Real Estate",
        "Travel & Tourism", "Food & Beverage", "Fashion", "Technology",
        "Automotive", "Entertainment", "Fitness & Wellness"
    ]
    
    campaigns = []
    
    for i in range(1, 1001):
        category = random.choice(categories)
        channel = random.choice(channels)
        tech = random.choice(technologies)
        objective = random.choice(objectives)
        vertical = random.choice(verticals)
        
        # Generar nombre de campaña
        prefixes = ["Smart", "AI-Powered", "Intelligent", "Predictive", "Automated", "Dynamic", "Adaptive", "Cognitive", "Neural", "Deep"]
        actions = ["Boost", "Enhance", "Maximize", "Optimize", "Transform", "Revolutionize", "Accelerate", "Amplify", "Streamline", "Elevate"]
        suffixes = ["Campaign", "Strategy", "Initiative", "Program", "Solution", "Experience", "Journey", "Optimization", "Engagement", "Conversion"]
        
        name = f"{random.choice(prefixes)} {random.choice(actions)} {random.choice(suffixes)}"
        
        # Generar descripción
        descriptions = [
            f"Implementa algoritmos de {tech} para personalizar experiencias únicas en {channel}, adaptando contenido y ofertas en tiempo real según el comportamiento del usuario.",
            f"Utiliza {tech} para crear experiencias hiper-personalizadas en {channel} que aumentan la relevancia y engagement del contenido.",
            f"Aplica {tech} para predecir tendencias de mercado y comportamiento del consumidor en {channel}, permitiendo decisiones estratégicas basadas en datos.",
            f"Desarrolla chatbots inteligentes con {tech} para {channel} que proporcionan soporte 24/7 y guían a los usuarios a través del embudo de conversión.",
            f"Utiliza {tech} para generar automáticamente contenido personalizado y relevante para {channel}, incluyendo textos, imágenes y videos.",
            f"Aplica {tech} para optimizar continuamente la tasa de conversión en {channel} mediante testing automático y ajustes en tiempo real.",
            f"Implementa algoritmos de {tech} que identifican y corrigen puntos de fricción en el embudo de conversión de {channel}.",
            f"Utiliza {tech} para crear experiencias de conversión personalizadas que maximizan el ROI en {channel}.",
            f"Desarrolla un sistema de personalización inteligente con {tech} que analiza patrones de comportamiento en {channel}.",
            f"Implementa modelos predictivos con {tech} que anticipan necesidades del cliente en {channel}."
        ]
        
        description = random.choice(descriptions)
        
        # Generar métricas
        metrics = {
            "conversion_rate": round(random.uniform(2.5, 15.0), 2),
            "click_through_rate": round(random.uniform(1.8, 8.5), 2),
            "engagement_rate": round(random.uniform(3.2, 12.8), 2),
            "cost_per_acquisition": round(random.uniform(15, 85), 2),
            "return_on_ad_spend": round(random.uniform(3.2, 8.7), 2),
            "customer_lifetime_value": round(random.uniform(120, 850), 2)
        }
        
        # Generar presupuesto
        budget_tiers = [
            {"min": 1000, "max": 5000, "tier": "Básico"},
            {"min": 5000, "max": 15000, "tier": "Intermedio"},
            {"min": 15000, "max": 50000, "tier": "Avanzado"},
            {"min": 50000, "max": 150000, "tier": "Enterprise"}
        ]
        
        tier = random.choice(budget_tiers)
        budget = random.randint(tier["min"], tier["max"])
        
        # Generar timeline
        start_date = datetime.now() + timedelta(days=random.randint(1, 30))
        duration_weeks = random.randint(4, 16)
        end_date = start_date + timedelta(weeks=duration_weeks)
        
        campaign = {
            "id": i,
            "name": name,
            "category": category,
            "technology": tech,
            "channel": channel,
            "objective": objective,
            "vertical": vertical,
            "description": description,
            "budget": {
                "amount": budget,
                "tier": tier["tier"],
                "currency": "USD"
            },
            "timeline": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "duration_weeks": duration_weeks
            },
            "metrics": metrics,
            "success_probability": round(random.uniform(0.65, 0.95), 2),
            "complexity": random.choice(["Baja", "Media", "Alta"]),
            "priority": random.choice(["Baja", "Media", "Alta", "Crítica"]),
            "tags": [category, tech, channel, vertical],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        campaigns.append(campaign)
        
        if i % 100 == 0:
            print(f"Generadas {i}/1000 campañas...")
    
    return campaigns

def save_campaigns(campaigns):
    """Guarda las campañas en diferentes formatos"""
    
    # JSON completo
    with open('ai_marketing_campaigns.json', 'w', encoding='utf-8') as f:
        json.dump(campaigns, f, ensure_ascii=False, indent=2)
    
    # CSV para análisis
    csv_content = "ID,Nombre,Categoría,Tecnología,Canal,Objetivo,Presupuesto,Probabilidad_Éxito,Complejidad,Prioridad\n"
    for campaign in campaigns:
        csv_content += f"{campaign['id']},{campaign['name']},{campaign['category']},{campaign['technology']},{campaign['channel']},{campaign['objective']},{campaign['budget']['amount']},{campaign['success_probability']},{campaign['complexity']},{campaign['priority']}\n"
    
    with open('ai_marketing_campaigns.csv', 'w', encoding='utf-8') as f:
        f.write(csv_content)
    
    # Resumen por categorías
    categories_summary = {}
    for campaign in campaigns:
        category = campaign['category']
        if category not in categories_summary:
            categories_summary[category] = []
        categories_summary[category].append({
            'id': campaign['id'],
            'name': campaign['name'],
            'budget': campaign['budget']['amount'],
            'success_probability': campaign['success_probability']
        })
    
    with open('campaigns_by_category.json', 'w', encoding='utf-8') as f:
        json.dump(categories_summary, f, ensure_ascii=False, indent=2)
    
    print("Archivos guardados:")
    print("- ai_marketing_campaigns.json (completo)")
    print("- ai_marketing_campaigns.csv (para análisis)")
    print("- campaigns_by_category.json (por categorías)")

if __name__ == "__main__":
    print("Generando 1000 campañas de marketing con IA...")
    campaigns = generate_campaigns()
    save_campaigns(campaigns)
    
    print(f"\n¡Completado! Se generaron {len(campaigns)} campañas exitosamente.")
    
    # Estadísticas
    total_budget = sum(campaign['budget']['amount'] for campaign in campaigns)
    print(f"Presupuesto total estimado: ${total_budget:,} USD")
    print(f"Presupuesto promedio por campaña: ${total_budget/len(campaigns):,.2f} USD")
    
    # Estadísticas por categoría
    categories = {}
    for campaign in campaigns:
        cat = campaign['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nCampañas por categoría:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")


