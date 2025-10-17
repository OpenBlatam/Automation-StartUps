#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Mejorado de 1000 Campañas de Marketing con IA
=======================================================
Versión mejorada con métricas más realistas, casos de uso específicos
y herramientas de análisis avanzadas.
"""

import json
import random
from datetime import datetime, timedelta
import math

class EnhancedAICampaignGenerator:
    def __init__(self):
        # Configuración mejorada con más variedad y realismo
        self.categories = {
            "Personalización con IA": {
                "technologies": ["Machine Learning", "Deep Learning", "Neural Networks", "Recommendation Engines"],
                "channels": ["Redes Sociales", "Email Marketing", "E-commerce", "Mobile Marketing"],
                "objectives": ["Aumentar conversiones", "Mejorar engagement", "Mejorar experiencia de usuario"],
                "complexity_weights": {"Baja": 0.2, "Media": 0.5, "Alta": 0.3},
                "priority_weights": {"Baja": 0.1, "Media": 0.3, "Alta": 0.4, "Crítica": 0.2},
                "avg_budget_range": (15000, 45000),
                "success_probability_range": (0.75, 0.95)
            },
            "Análisis Predictivo": {
                "technologies": ["Deep Learning", "Predictive Analytics", "Machine Learning", "Neural Networks"],
                "channels": ["Email Marketing", "Marketing Automation", "SEM/PPC", "Display Advertising"],
                "objectives": ["Mejorar engagement", "Generar leads", "Optimizar ROI"],
                "complexity_weights": {"Baja": 0.1, "Media": 0.3, "Alta": 0.6},
                "priority_weights": {"Baja": 0.05, "Media": 0.25, "Alta": 0.4, "Crítica": 0.3},
                "avg_budget_range": (25000, 75000),
                "success_probability_range": (0.80, 0.98)
            },
            "Chatbots y Asistentes Virtuales": {
                "technologies": ["NLP", "Machine Learning", "Deep Learning", "Computer Vision"],
                "channels": ["E-commerce", "Website", "Mobile Marketing", "Social Media"],
                "objectives": ["Generar leads", "Mejorar experiencia de usuario", "Mejorar retención"],
                "complexity_weights": {"Baja": 0.3, "Media": 0.5, "Alta": 0.2},
                "priority_weights": {"Baja": 0.1, "Media": 0.2, "Alta": 0.5, "Crítica": 0.2},
                "avg_budget_range": (12000, 35000),
                "success_probability_range": (0.70, 0.92)
            },
            "Generación de Contenido": {
                "technologies": ["Generative AI", "NLP", "Computer Vision", "Deep Learning"],
                "channels": ["Content Marketing", "Blog", "Social Media", "Video Marketing"],
                "objectives": ["Aumentar ventas", "Mejorar engagement", "Aumentar brand awareness"],
                "complexity_weights": {"Baja": 0.2, "Media": 0.4, "Alta": 0.4},
                "priority_weights": {"Baja": 0.2, "Media": 0.4, "Alta": 0.3, "Crítica": 0.1},
                "avg_budget_range": (18000, 50000),
                "success_probability_range": (0.72, 0.90)
            },
            "Optimización de Conversión": {
                "technologies": ["Reinforcement Learning", "Machine Learning", "Deep Learning", "Neural Networks"],
                "channels": ["SEM/PPC", "Landing Pages", "E-commerce", "Display Advertising"],
                "objectives": ["Mejorar retención", "Optimizar ROI", "Aumentar conversiones"],
                "complexity_weights": {"Baja": 0.1, "Media": 0.3, "Alta": 0.6},
                "priority_weights": {"Baja": 0.05, "Media": 0.2, "Alta": 0.35, "Crítica": 0.4},
                "avg_budget_range": (30000, 80000),
                "success_probability_range": (0.85, 0.98)
            },
            "Segmentación Avanzada": {
                "technologies": ["Neural Networks", "Machine Learning", "Deep Learning", "Clustering"],
                "channels": ["Display Advertising", "Facebook Ads", "Email Marketing", "Social Media"],
                "objectives": ["Optimizar ROI", "Expandir alcance", "Mejorar engagement"],
                "complexity_weights": {"Baja": 0.3, "Media": 0.5, "Alta": 0.2},
                "priority_weights": {"Baja": 0.15, "Media": 0.35, "Alta": 0.35, "Crítica": 0.15},
                "avg_budget_range": (15000, 40000),
                "success_probability_range": (0.75, 0.90)
            },
            "Automatización de Marketing": {
                "technologies": ["Computer Vision", "Machine Learning", "NLP", "Deep Learning"],
                "channels": ["Mobile Marketing", "Email Marketing", "Social Media", "Marketing Automation"],
                "objectives": ["Reducir costos", "Mejorar retención", "Expandir alcance"],
                "complexity_weights": {"Baja": 0.2, "Media": 0.4, "Alta": 0.4},
                "priority_weights": {"Baja": 0.1, "Media": 0.3, "Alta": 0.4, "Crítica": 0.2},
                "avg_budget_range": (20000, 60000),
                "success_probability_range": (0.78, 0.94)
            },
            "Análisis de Sentimientos": {
                "technologies": ["Sentiment Analysis", "NLP", "Machine Learning", "Deep Learning"],
                "channels": ["Influencer Marketing", "Social Media", "Review Platforms", "Community Management"],
                "objectives": ["Mejorar experiencia de usuario", "Mejorar engagement", "Aumentar brand awareness"],
                "complexity_weights": {"Baja": 0.4, "Media": 0.4, "Alta": 0.2},
                "priority_weights": {"Baja": 0.2, "Media": 0.4, "Alta": 0.3, "Crítica": 0.1},
                "avg_budget_range": (10000, 30000),
                "success_probability_range": (0.70, 0.88)
            },
            "Recomendaciones Inteligentes": {
                "technologies": ["Recommendation Engines", "Machine Learning", "Deep Learning", "Collaborative Filtering"],
                "channels": ["Video Marketing", "E-commerce", "Mobile Apps", "Content Platforms"],
                "objectives": ["Mejorar retención", "Aumentar ventas", "Mejorar experiencia de usuario"],
                "complexity_weights": {"Baja": 0.2, "Media": 0.5, "Alta": 0.3},
                "priority_weights": {"Baja": 0.1, "Media": 0.3, "Alta": 0.4, "Crítica": 0.2},
                "avg_budget_range": (25000, 55000),
                "success_probability_range": (0.80, 0.95)
            },
            "Marketing Visual con IA": {
                "technologies": ["Computer Vision", "Deep Learning", "Generative AI", "Image Recognition"],
                "channels": ["Social Media", "Instagram", "Video Marketing", "Display Advertising"],
                "objectives": ["Aumentar brand awareness", "Mejorar engagement", "Aumentar ventas"],
                "complexity_weights": {"Baja": 0.3, "Media": 0.4, "Alta": 0.3},
                "priority_weights": {"Baja": 0.15, "Media": 0.35, "Alta": 0.35, "Crítica": 0.15},
                "avg_budget_range": (20000, 45000),
                "success_probability_range": (0.75, 0.92)
            }
        }
        
        self.verticals = {
            "E-commerce": {"budget_multiplier": 1.0, "success_boost": 0.05, "complexity_boost": 0.0},
            "Fintech": {"budget_multiplier": 1.5, "success_boost": 0.08, "complexity_boost": 0.1},
            "Healthcare": {"budget_multiplier": 1.3, "success_boost": 0.06, "complexity_boost": 0.15},
            "Education": {"budget_multiplier": 0.8, "success_boost": 0.03, "complexity_boost": -0.05},
            "Real Estate": {"budget_multiplier": 1.2, "success_boost": 0.04, "complexity_boost": 0.05},
            "Travel & Tourism": {"budget_multiplier": 1.1, "success_boost": 0.02, "complexity_boost": 0.0},
            "Food & Beverage": {"budget_multiplier": 0.9, "success_boost": 0.01, "complexity_boost": -0.05},
            "Fashion": {"budget_multiplier": 1.1, "success_boost": 0.03, "complexity_boost": 0.0},
            "Technology": {"budget_multiplier": 1.4, "success_boost": 0.07, "complexity_boost": 0.1},
            "Automotive": {"budget_multiplier": 1.3, "success_boost": 0.05, "complexity_boost": 0.08},
            "Entertainment": {"budget_multiplier": 1.0, "success_boost": 0.02, "complexity_boost": 0.0},
            "Fitness & Wellness": {"budget_multiplier": 0.9, "success_boost": 0.01, "complexity_boost": -0.02},
            "Retail": {"budget_multiplier": 0.95, "success_boost": 0.02, "complexity_boost": 0.0},
            "Banking": {"budget_multiplier": 1.6, "success_boost": 0.09, "complexity_boost": 0.2},
            "Insurance": {"budget_multiplier": 1.4, "success_boost": 0.06, "complexity_boost": 0.12},
            "Telecommunications": {"budget_multiplier": 1.2, "success_boost": 0.04, "complexity_boost": 0.05},
            "Manufacturing": {"budget_multiplier": 1.1, "success_boost": 0.03, "complexity_boost": 0.03},
            "Consulting": {"budget_multiplier": 1.0, "success_boost": 0.02, "complexity_boost": 0.0},
            "Non-profit": {"budget_multiplier": 0.6, "success_boost": 0.01, "complexity_boost": -0.1},
            "Government": {"budget_multiplier": 1.8, "success_boost": 0.10, "complexity_boost": 0.25}
        }
        
        self.prefixes = [
            "Smart", "AI-Powered", "Intelligent", "Predictive", "Automated",
            "Dynamic", "Adaptive", "Cognitive", "Neural", "Deep", "Advanced",
            "Next-Gen", "Hyper", "Ultra", "Pro", "Elite", "Prime", "Max",
            "Turbo", "Quantum", "Revolutionary", "Intelligent", "Precision",
            "Optimized", "Enhanced", "Supercharged", "Accelerated", "Streamlined"
        ]
        
        self.actions = [
            "Boost", "Enhance", "Maximize", "Optimize", "Transform",
            "Revolutionize", "Accelerate", "Amplify", "Streamline", "Elevate",
            "Supercharge", "Unlock", "Drive", "Scale", "Grow", "Expand",
            "Improve", "Refine", "Perfect", "Amplify", "Catalyze", "Ignite",
            "Propel", "Advance", "Innovate", "Disrupt", "Reinvent"
        ]
        
        self.suffixes = [
            "Campaign", "Strategy", "Initiative", "Program", "Solution",
            "Experience", "Journey", "Optimization", "Engagement", "Conversion",
            "System", "Platform", "Engine", "Hub", "Network", "Ecosystem",
            "Framework", "Methodology", "Approach", "Technique", "Model",
            "Architecture", "Infrastructure", "Pipeline", "Workflow"
        ]

    def weighted_choice(self, choices, weights):
        """Selecciona una opción basada en pesos"""
        total = sum(weights.values())
        r = random.uniform(0, total)
        upto = 0
        for choice, weight in weights.items():
            if upto + weight >= r:
                return choice
            upto += weight
        return list(choices.keys())[0]

    def generate_enhanced_metrics(self, category, vertical, complexity):
        """Genera métricas más realistas basadas en categoría, vertical y complejidad"""
        base_metrics = {
            "conversion_rate": random.uniform(2.0, 25.0),
            "click_through_rate": random.uniform(1.0, 15.0),
            "engagement_rate": random.uniform(2.0, 22.0),
            "cost_per_acquisition": random.uniform(10, 150),
            "return_on_ad_spend": random.uniform(2.0, 15.0),
            "customer_lifetime_value": random.uniform(80, 1500),
            "email_open_rate": random.uniform(15, 40),
            "social_media_reach": random.randint(30000, 800000),
            "website_traffic_increase": random.uniform(20, 250),
            "lead_generation_increase": random.uniform(30, 300),
            "brand_awareness_lift": random.uniform(15, 85),
            "customer_satisfaction_score": random.uniform(3.5, 4.8),
            "retention_rate": random.uniform(60, 95),
            "time_to_implement_weeks": random.randint(3, 24),
            "team_size_required": random.randint(2, 15)
        }
        
        # Ajustes por complejidad
        complexity_multipliers = {
            "Baja": {"conversion_rate": 0.8, "cost_per_acquisition": 1.2, "time_to_implement_weeks": 0.6},
            "Media": {"conversion_rate": 1.0, "cost_per_acquisition": 1.0, "time_to_implement_weeks": 1.0},
            "Alta": {"conversion_rate": 1.3, "cost_per_acquisition": 0.8, "time_to_implement_weeks": 1.5}
        }
        
        # Ajustes por vertical
        vertical_boost = self.verticals.get(vertical, {"success_boost": 0, "complexity_boost": 0})
        
        # Aplicar ajustes
        for metric, multiplier in complexity_multipliers[complexity].items():
            if metric in base_metrics:
                base_metrics[metric] *= multiplier
        
        # Aplicar boost del vertical
        base_metrics["conversion_rate"] *= (1 + vertical_boost["success_boost"])
        base_metrics["return_on_ad_spend"] *= (1 + vertical_boost["success_boost"])
        
        # Redondear métricas
        for key, value in base_metrics.items():
            if isinstance(value, float):
                base_metrics[key] = round(value, 2)
            else:
                base_metrics[key] = int(value)
        
        return base_metrics

    def generate_enhanced_budget(self, category, vertical, complexity):
        """Genera presupuesto más realista basado en categoría, vertical y complejidad"""
        category_config = self.categories[category]
        vertical_config = self.verticals[vertical]
        
        # Presupuesto base por complejidad
        base_budgets = {
            "Baja": (5000, 25000),
            "Media": (15000, 60000),
            "Alta": (40000, 150000)
        }
        
        min_budget, max_budget = base_budgets[complexity]
        
        # Ajustar por vertical
        min_budget *= vertical_config["budget_multiplier"]
        max_budget *= vertical_config["budget_multiplier"]
        
        budget = random.randint(int(min_budget), int(max_budget))
        
        # Determinar tier
        if budget < 15000:
            tier = "Básico"
        elif budget < 40000:
            tier = "Intermedio"
        elif budget < 100000:
            tier = "Avanzado"
        else:
            tier = "Enterprise"
        
        return {
            "amount": budget,
            "tier": tier,
            "currency": "USD",
            "breakdown": {
                "technology_licensing": round(budget * 0.25),
                "development_team": round(budget * 0.40),
                "marketing_execution": round(budget * 0.20),
                "analytics_tools": round(budget * 0.10),
                "contingency": round(budget * 0.05)
            }
        }

    def generate_enhanced_timeline(self, complexity, category):
        """Genera cronograma más detallado y realista"""
        base_weeks = {
            "Baja": random.randint(3, 8),
            "Media": random.randint(6, 14),
            "Alta": random.randint(10, 24)
        }
        
        duration_weeks = base_weeks[complexity]
        start_date = datetime.now() + timedelta(days=random.randint(1, 30))
        end_date = start_date + timedelta(weeks=duration_weeks)
        
        # Fases detalladas
        phases = []
        phase_percentages = [0.15, 0.35, 0.25, 0.25]  # Planning, Development, Testing, Launch
        
        for i, (phase_name, percentage) in enumerate(zip(
            ["Planificación y Análisis", "Desarrollo e Implementación", "Testing y Optimización", "Lanzamiento y Monitoreo"],
            phase_percentages
        )):
            phase_weeks = max(1, int(duration_weeks * percentage))
            phase_start = start_date + timedelta(weeks=sum(phase_percentages[:i]) * duration_weeks)
            phase_end = phase_start + timedelta(weeks=phase_weeks)
            
            phases.append({
                "name": phase_name,
                "start_date": phase_start.strftime("%Y-%m-%d"),
                "end_date": phase_end.strftime("%Y-%m-%d"),
                "duration_weeks": phase_weeks,
                "milestones": self.generate_milestones(phase_name, phase_weeks)
            })
        
        return {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "duration_weeks": duration_weeks,
            "phases": phases,
            "critical_path": self.generate_critical_path(phases)
        }

    def generate_milestones(self, phase_name, duration_weeks):
        """Genera hitos específicos para cada fase"""
        milestones = {
            "Planificación y Análisis": [
                "Análisis de datos históricos completado",
                "Definición de objetivos y KPIs",
                "Selección de tecnologías y herramientas",
                "Aprobación del plan de proyecto"
            ],
            "Desarrollo e Implementación": [
                "Configuración del entorno de desarrollo",
                "Implementación del algoritmo base",
                "Integración con sistemas existentes",
                "Desarrollo de interfaz de usuario"
            ],
            "Testing y Optimización": [
                "Pruebas unitarias completadas",
                "Pruebas de integración exitosas",
                "Optimización de rendimiento",
                "Pruebas de usuario finalizadas"
            ],
            "Lanzamiento y Monitoreo": [
                "Despliegue en producción",
                "Configuración de monitoreo",
                "Capacitación del equipo",
                "Primer reporte de resultados"
            ]
        }
        
        phase_milestones = milestones.get(phase_name, [])
        return random.sample(phase_milestones, min(len(phase_milestones), max(1, duration_weeks // 2)))

    def generate_critical_path(self, phases):
        """Genera la ruta crítica del proyecto"""
        critical_tasks = []
        for phase in phases:
            if phase["name"] in ["Desarrollo e Implementación", "Testing y Optimización"]:
                critical_tasks.append({
                    "task": f"Completar {phase['name']}",
                    "deadline": phase["end_date"],
                    "dependencies": "Fase anterior completada"
                })
        return critical_tasks

    def generate_enhanced_description(self, category, tech, channel, vertical):
        """Genera descripciones más detalladas y específicas"""
        descriptions = {
            "Personalización con IA": [
                f"Implementa un sistema avanzado de {tech} para personalizar experiencias únicas en {channel} en el sector {vertical}. La solución adapta contenido, ofertas y mensajes en tiempo real según el comportamiento del usuario, historial de compras y preferencias demográficas, generando un aumento promedio del 35% en conversiones.",
                f"Desarrolla una plataforma de personalización inteligente con {tech} que analiza patrones de comportamiento en {channel} para el sector {vertical}. El sistema utiliza machine learning para crear segmentos dinámicos y ofrecer recomendaciones precisas, mejorando el engagement en un 45% y reduciendo el costo de adquisición en un 28%.",
                f"Crea un ecosistema de personalización con {tech} en {channel} específicamente diseñado para {vertical}. La solución incluye análisis predictivo de comportamiento, generación automática de contenido personalizado y optimización continua de la experiencia del usuario, resultando en un ROI promedio de 6.2x."
            ],
            "Análisis Predictivo": [
                f"Implementa modelos avanzados de {tech} para análisis predictivo en {channel} en el sector {vertical}. La solución predice tendencias de mercado, comportamiento del consumidor y oportunidades de crecimiento, permitiendo decisiones estratégicas basadas en datos que aumentan la eficiencia de marketing en un 40%.",
                f"Desarrolla un sistema de {tech} que anticipa necesidades del cliente en {channel} para {vertical}. El modelo utiliza datos históricos, variables externas y patrones de comportamiento para predecir el valor de vida del cliente (LTV) y optimizar estrategias de retención, generando un aumento del 30% en la retención de clientes.",
                f"Crea una plataforma de análisis predictivo con {tech} en {channel} que transforma datos en insights accionables para {vertical}. El sistema incluye predicción de churn, análisis de sentimientos en tiempo real y recomendaciones automáticas de acciones de marketing, resultando en una mejora del 25% en el ROI de campañas."
            ]
        }
        
        base_descriptions = descriptions.get(category, [
            f"Implementa una solución innovadora de {tech} en {channel} para el sector {vertical}. La campaña utiliza inteligencia artificial para optimizar procesos de marketing, mejorar la experiencia del cliente y generar resultados medibles con un ROI promedio de 4.8x.",
            f"Desarrolla una estrategia de marketing inteligente con {tech} en {channel} específicamente diseñada para {vertical}. La solución combina análisis avanzado de datos, automatización inteligente y personalización dinámica para maximizar el impacto de las campañas de marketing.",
            f"Crea un ecosistema de marketing con {tech} en {channel} que transforma la forma en que {vertical} se conecta con sus clientes. La plataforma incluye herramientas de análisis predictivo, automatización de procesos y optimización continua para generar resultados excepcionales."
        ])
        
        return random.choice(base_descriptions)

    def generate_use_cases(self, category, vertical):
        """Genera casos de uso específicos para cada campaña"""
        use_cases = {
            "Personalización con IA": [
                f"Personalización de emails en {vertical} basada en historial de navegación",
                f"Recomendaciones de productos en tiempo real para usuarios de {vertical}",
                f"Adaptación dinámica de landing pages según perfil demográfico",
                f"Personalización de ofertas promocionales en {vertical}",
                f"Optimización de contenido de redes sociales por audiencia"
            ],
            "Análisis Predictivo": [
                f"Predicción de tendencias de compra en {vertical}",
                f"Análisis de riesgo de churn de clientes en {vertical}",
                f"Pronóstico de demanda estacional en {vertical}",
                f"Predicción de valor de vida del cliente en {vertical}",
                f"Análisis de impacto de campañas en {vertical}"
            ],
            "Chatbots y Asistentes Virtuales": [
                f"Soporte 24/7 para clientes de {vertical}",
                f"Asistencia en proceso de compra en {vertical}",
                f"Resolución automática de consultas frecuentes en {vertical}",
                f"Programación de citas y servicios en {vertical}",
                f"Recolección de feedback de clientes en {vertical}"
            ]
        }
        
        category_use_cases = use_cases.get(category, [
            f"Optimización de procesos en {vertical}",
            f"Mejora de experiencia del cliente en {vertical}",
            f"Automatización de tareas repetitivas en {vertical}",
            f"Análisis de datos en {vertical}",
            f"Generación de insights en {vertical}"
        ])
        
        return random.sample(category_use_cases, min(3, len(category_use_cases)))

    def generate_enhanced_campaign(self, campaign_id):
        """Genera una campaña mejorada con todos los detalles"""
        category = random.choice(list(self.categories.keys()))
        category_config = self.categories[category]
        
        tech = random.choice(category_config["technologies"])
        channel = random.choice(category_config["channels"])
        objective = random.choice(category_config["objectives"])
        vertical = random.choice(list(self.verticals.keys()))
        
        # Seleccionar complejidad y prioridad basado en pesos
        complexity = self.weighted_choice(
            category_config["complexity_weights"], 
            category_config["complexity_weights"]
        )
        priority = self.weighted_choice(
            category_config["priority_weights"], 
            category_config["priority_weights"]
        )
        
        # Generar nombre
        prefix = random.choice(self.prefixes)
        action = random.choice(self.actions)
        suffix = random.choice(self.suffixes)
        name = f"{prefix} {action} {suffix}"
        
        # Generar métricas mejoradas
        metrics = self.generate_enhanced_metrics(category, vertical, complexity)
        
        # Generar presupuesto mejorado
        budget = self.generate_enhanced_budget(category, vertical, complexity)
        
        # Generar timeline mejorado
        timeline = self.generate_enhanced_timeline(complexity, category)
        
        # Generar descripción mejorada
        description = self.generate_enhanced_description(category, tech, channel, vertical)
        
        # Generar casos de uso
        use_cases = self.generate_use_cases(category, vertical)
        
        # Calcular probabilidad de éxito mejorada
        base_success = random.uniform(*category_config["success_probability_range"])
        vertical_boost = self.verticals[vertical]["success_boost"]
        complexity_penalty = {"Baja": 0.05, "Media": 0.0, "Alta": -0.03}[complexity]
        success_probability = min(0.98, base_success + vertical_boost + complexity_penalty)
        
        return {
            "id": campaign_id,
            "name": name,
            "category": category,
            "technology": tech,
            "channel": channel,
            "objective": objective,
            "vertical": vertical,
            "description": description,
            "use_cases": use_cases,
            "budget": budget,
            "timeline": timeline,
            "metrics": metrics,
            "success_probability": round(success_probability, 2),
            "complexity": complexity,
            "priority": priority,
            "tags": [category, tech, channel, vertical, complexity, priority],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Draft",
            "team_requirements": {
                "data_scientists": random.randint(1, 5),
                "ai_engineers": random.randint(1, 4),
                "marketing_specialists": random.randint(2, 8),
                "project_managers": random.randint(1, 2)
            },
            "dependencies": self.generate_dependencies(category, tech),
            "risks": self.generate_risks(complexity, category),
            "success_factors": self.generate_success_factors(category, vertical)
        }

    def generate_dependencies(self, category, tech):
        """Genera dependencias del proyecto"""
        common_deps = [
            "Acceso a datos históricos de clientes",
            "Infraestructura de cloud computing",
            "Herramientas de análisis de datos",
            "Equipo técnico especializado"
        ]
        
        tech_deps = {
            "Machine Learning": ["Librerías ML (scikit-learn, TensorFlow)", "Entorno de desarrollo Python"],
            "Deep Learning": ["GPUs para entrenamiento", "Frameworks de deep learning"],
            "NLP": ["Corpus de texto en el idioma objetivo", "Herramientas de procesamiento de lenguaje"],
            "Computer Vision": ["Dataset de imágenes etiquetadas", "Herramientas de procesamiento de imágenes"]
        }
        
        return common_deps + tech_deps.get(tech, [])

    def generate_risks(self, complexity, category):
        """Genera riesgos del proyecto"""
        base_risks = [
            "Calidad insuficiente de datos",
            "Resistencia al cambio organizacional",
            "Limitaciones técnicas de integración"
        ]
        
        complexity_risks = {
            "Baja": ["Retrasos menores en implementación"],
            "Media": ["Complejidad de integración con sistemas existentes", "Curva de aprendizaje del equipo"],
            "Alta": ["Riesgos técnicos significativos", "Dependencias externas críticas", "Escalabilidad de la solución"]
        }
        
        return base_risks + complexity_risks[complexity]

    def generate_success_factors(self, category, vertical):
        """Genera factores de éxito"""
        return [
            f"Compromiso ejecutivo en {vertical}",
            f"Calidad de datos en {category}",
            f"Capacitación adecuada del equipo",
            f"Monitoreo continuo de métricas",
            f"Flexibilidad para ajustes iterativos"
        ]

    def generate_all_enhanced_campaigns(self, total=1000):
        """Genera todas las campañas mejoradas"""
        campaigns = []
        
        print(f"Generando {total} campañas de marketing con IA mejoradas...")
        
        for i in range(1, total + 1):
            campaign = self.generate_enhanced_campaign(i)
            campaigns.append(campaign)
            
            if i % 100 == 0:
                print(f"Progreso: {i}/{total} campañas generadas")
        
        print(f"¡Completado! Se generaron {len(campaigns)} campañas mejoradas exitosamente.")
        return campaigns

    def save_enhanced_campaigns(self, campaigns):
        """Guarda las campañas mejoradas en múltiples formatos"""
        
        # JSON completo mejorado
        with open('enhanced_1000_ai_marketing_campaigns.json', 'w', encoding='utf-8') as f:
            json.dump(campaigns, f, ensure_ascii=False, indent=2)
        
        # CSV mejorado con más columnas
        csv_content = "ID,Nombre,Categoría,Tecnología,Canal,Objetivo,Vertical,Presupuesto,Probabilidad_Éxito,Complejidad,Prioridad,ROI_Esperado,CPA,Equipo_Requerido,Descripción\n"
        for campaign in campaigns:
            csv_content += f"{campaign['id']},\"{campaign['name']}\",\"{campaign['category']}\",\"{campaign['technology']}\",\"{campaign['channel']}\",\"{campaign['objective']}\",\"{campaign['vertical']}\",{campaign['budget']['amount']},{campaign['success_probability']},\"{campaign['complexity']}\",\"{campaign['priority']}\",{campaign['metrics']['return_on_ad_spend']},{campaign['metrics']['cost_per_acquisition']},{campaign['team_requirements']['data_scientists'] + campaign['team_requirements']['ai_engineers']},\"{campaign['description']}\"\n"
        
        with open('enhanced_1000_ai_marketing_campaigns.csv', 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        # Resumen por categorías mejorado
        categories_summary = {}
        for campaign in campaigns:
            category = campaign['category']
            if category not in categories_summary:
                categories_summary[category] = {
                    'campaigns': [],
                    'total_budget': 0,
                    'avg_success_probability': 0,
                    'complexity_distribution': {'Baja': 0, 'Media': 0, 'Alta': 0},
                    'priority_distribution': {'Baja': 0, 'Media': 0, 'Alta': 0, 'Crítica': 0}
                }
            
            categories_summary[category]['campaigns'].append({
                'id': campaign['id'],
                'name': campaign['name'],
                'budget': campaign['budget']['amount'],
                'success_probability': campaign['success_probability'],
                'complexity': campaign['complexity'],
                'priority': campaign['priority'],
                'roi': campaign['metrics']['return_on_ad_spend']
            })
            
            categories_summary[category]['total_budget'] += campaign['budget']['amount']
            categories_summary[category]['complexity_distribution'][campaign['complexity']] += 1
            categories_summary[category]['priority_distribution'][campaign['priority']] += 1
        
        # Calcular promedios
        for category in categories_summary:
            campaigns_list = categories_summary[category]['campaigns']
            categories_summary[category]['avg_success_probability'] = round(
                sum(c['success_probability'] for c in campaigns_list) / len(campaigns_list), 2
            )
        
        with open('enhanced_campaigns_by_category.json', 'w', encoding='utf-8') as f:
            json.dump(categories_summary, f, ensure_ascii=False, indent=2)
        
        # Dashboard de métricas
        dashboard_data = {
            "summary": {
                "total_campaigns": len(campaigns),
                "total_budget": sum(c['budget']['amount'] for c in campaigns),
                "avg_success_probability": round(sum(c['success_probability'] for c in campaigns) / len(campaigns), 2),
                "avg_roi": round(sum(c['metrics']['return_on_ad_spend'] for c in campaigns) / len(campaigns), 2)
            },
            "by_complexity": {},
            "by_priority": {},
            "by_vertical": {},
            "top_performers": sorted(campaigns, key=lambda x: x['success_probability'], reverse=True)[:20]
        }
        
        # Análisis por complejidad
        for complexity in ['Baja', 'Media', 'Alta']:
            comp_campaigns = [c for c in campaigns if c['complexity'] == complexity]
            dashboard_data["by_complexity"][complexity] = {
                "count": len(comp_campaigns),
                "avg_budget": round(sum(c['budget']['amount'] for c in comp_campaigns) / len(comp_campaigns), 2) if comp_campaigns else 0,
                "avg_success": round(sum(c['success_probability'] for c in comp_campaigns) / len(comp_campaigns), 2) if comp_campaigns else 0
            }
        
        with open('enhanced_campaigns_dashboard.json', 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
        
        print("Archivos mejorados guardados:")
        print("- enhanced_1000_ai_marketing_campaigns.json (completo)")
        print("- enhanced_1000_ai_marketing_campaigns.csv (para análisis)")
        print("- enhanced_campaigns_by_category.json (por categorías)")
        print("- enhanced_campaigns_dashboard.json (dashboard de métricas)")

def main():
    """Función principal"""
    print("=== GENERADOR MEJORADO DE 1000 CAMPAÑAS DE MARKETING CON IA ===")
    generator = EnhancedAICampaignGenerator()
    campaigns = generator.generate_all_enhanced_campaigns(1000)
    generator.save_enhanced_campaigns(campaigns)
    
    # Estadísticas mejoradas
    print(f"\n=== ESTADÍSTICAS MEJORADAS ===")
    print(f"Total de campañas: {len(campaigns)}")
    
    total_budget = sum(campaign['budget']['amount'] for campaign in campaigns)
    avg_success = sum(campaign['success_probability'] for campaign in campaigns) / len(campaigns)
    avg_roi = sum(campaign['metrics']['return_on_ad_spend'] for campaign in campaigns) / len(campaigns)
    
    print(f"Presupuesto total: ${total_budget:,} USD")
    print(f"Presupuesto promedio: ${total_budget/len(campaigns):,.2f} USD")
    print(f"Probabilidad de éxito promedio: {avg_success:.2%}")
    print(f"ROI promedio: {avg_roi:.1f}x")
    
    # Top 10 campañas por ROI
    top_roi = sorted(campaigns, key=lambda x: x['metrics']['return_on_ad_spend'], reverse=True)[:10]
    print(f"\nTop 10 campañas por ROI:")
    for i, campaign in enumerate(top_roi, 1):
        print(f"{i:2d}. {campaign['name']} - ROI: {campaign['metrics']['return_on_ad_spend']:.1f}x - {campaign['category']}")
    
    print("\n¡Proceso completado exitosamente!")

if __name__ == "__main__":
    main()


