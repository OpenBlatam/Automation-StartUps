#!/usr/bin/env python3
"""
Recommendation System - Sistema de Recomendaciones Inteligente
Genera recomendaciones personalizadas basadas en el análisis de contenido
"""

import os
import json
import re
from datetime import datetime
from collections import defaultdict, Counter
import argparse

class RecommendationSystem:
    def __init__(self, root_path="."):
        self.root_path = root_path
        self.recommendations = {
            "timestamp": datetime.now().isoformat(),
            "user_profile": {},
            "content_recommendations": [],
            "optimization_recommendations": [],
            "organization_recommendations": [],
            "collaboration_recommendations": [],
            "priority_scores": {}
        }
    
    def analyze_user_behavior(self, file_paths):
        """Analiza el comportamiento del usuario basado en archivos accedidos"""
        user_profile = {
            "preferred_categories": defaultdict(int),
            "preferred_file_types": defaultdict(int),
            "working_patterns": {},
            "expertise_areas": []
        }
        
        for file_path in file_paths:
            # Analizar categoría
            category = self.detect_category(file_path)
            user_profile["preferred_categories"][category] += 1
            
            # Analizar tipo de archivo
            file_type = self.detect_file_type(file_path)
            user_profile["preferred_file_types"][file_type] += 1
        
        # Determinar áreas de expertise
        top_categories = Counter(user_profile["preferred_categories"]).most_common(3)
        user_profile["expertise_areas"] = [cat for cat, count in top_categories]
        
        return user_profile
    
    def detect_category(self, file_path):
        """Detecta la categoría del archivo"""
        path_lower = file_path.lower()
        
        if 'vc' in path_lower or 'venture' in path_lower:
            return 'vc'
        elif 'marketing' in path_lower:
            return 'marketing'
        elif 'ai' in path_lower or 'technology' in path_lower:
            return 'ai_technology'
        elif 'business' in path_lower or 'strategy' in path_lower:
            return 'business_strategy'
        elif 'finance' in path_lower:
            return 'finance'
        elif 'operations' in path_lower or 'hr' in path_lower:
            return 'operations'
        elif 'sales' in path_lower or 'customer' in path_lower:
            return 'sales'
        elif 'research' in path_lower or 'development' in path_lower:
            return 'research'
        elif 'legal' in path_lower or 'compliance' in path_lower:
            return 'legal'
        else:
            return 'general'
    
    def detect_file_type(self, file_path):
        """Detecta el tipo de archivo"""
        filename = os.path.basename(file_path).lower()
        
        if 'strategy' in filename:
            return 'strategy'
        elif 'template' in filename:
            return 'template'
        elif 'analysis' in filename:
            return 'analysis'
        elif 'guide' in filename:
            return 'guide'
        elif 'checklist' in filename:
            return 'checklist'
        elif 'tool' in filename or 'script' in filename:
            return 'tool'
        elif 'report' in filename:
            return 'report'
        else:
            return 'document'
    
    def generate_content_recommendations(self, user_profile, all_files):
        """Genera recomendaciones de contenido basadas en el perfil del usuario"""
        recommendations = []
        
        # Recomendaciones basadas en categorías preferidas
        for category in user_profile["expertise_areas"]:
            category_files = [f for f in all_files if self.detect_category(f) == category]
            
            if len(category_files) > 10:
                recommendations.append({
                    "type": "content_organization",
                    "priority": "medium",
                    "title": f"Organizar categoría {category}",
                    "description": f"La categoría {category} tiene {len(category_files)} archivos",
                    "action": f"Considerar crear subcarpetas en {category}",
                    "category": category,
                    "score": 0.7
                })
        
        # Recomendaciones basadas en tipos de archivo
        for file_type, count in user_profile["preferred_file_types"].items():
            if count > 5:
                recommendations.append({
                    "type": "content_creation",
                    "priority": "high",
                    "title": f"Crear más {file_type}s",
                    "description": f"Tienes {count} archivos de tipo {file_type}",
                    "action": f"Considerar crear templates para {file_type}",
                    "file_type": file_type,
                    "score": 0.8
                })
        
        return recommendations
    
    def generate_optimization_recommendations(self, file_analysis):
        """Genera recomendaciones de optimización"""
        recommendations = []
        
        # Archivos grandes
        large_files = file_analysis.get("large_files", [])
        if large_files:
            recommendations.append({
                "type": "optimization",
                "priority": "high",
                "title": "Optimizar archivos grandes",
                "description": f"Se encontraron {len(large_files)} archivos grandes",
                "action": "Considerar dividir archivos grandes en secciones",
                "files": large_files[:5],  # Top 5
                "score": 0.9
            })
        
        # Archivos sin metadatos
        missing_metadata = file_analysis.get("missing_metadata", [])
        if missing_metadata:
            recommendations.append({
                "type": "metadata",
                "priority": "medium",
                "title": "Agregar metadatos",
                "description": f"Se encontraron {len(missing_metadata)} archivos sin metadatos",
                "action": "Agregar metadatos YAML a archivos principales",
                "files": missing_metadata[:10],
                "score": 0.6
            })
        
        # Duplicados
        duplicates = file_analysis.get("duplicates", [])
        if duplicates:
            recommendations.append({
                "type": "cleanup",
                "priority": "high",
                "title": "Eliminar duplicados",
                "description": f"Se encontraron {len(duplicates)} grupos de duplicados",
                "action": "Revisar y eliminar archivos duplicados",
                "duplicates": duplicates[:5],
                "score": 0.8
            })
        
        return recommendations
    
    def generate_organization_recommendations(self, file_analysis):
        """Genera recomendaciones de organización"""
        recommendations = []
        
        categories = file_analysis.get("categories", {})
        
        # Categorías desbalanceadas
        total_files = sum(categories.values())
        for category, count in categories.items():
            percentage = (count / total_files) * 100
            
            if percentage > 30:
                recommendations.append({
                    "type": "organization",
                    "priority": "medium",
                    "title": f"Categoría {category} muy grande",
                    "description": f"{category} representa el {percentage:.1f}% de todos los archivos",
                    "action": f"Considerar dividir {category} en subcategorías",
                    "category": category,
                    "percentage": percentage,
                    "score": 0.6
                })
            elif percentage < 5 and count > 0:
                recommendations.append({
                    "type": "organization",
                    "priority": "low",
                    "title": f"Categoría {category} pequeña",
                    "description": f"{category} solo tiene {count} archivos",
                    "action": f"Considerar consolidar {category} con otra categoría",
                    "category": category,
                    "count": count,
                    "score": 0.3
                })
        
        return recommendations
    
    def generate_collaboration_recommendations(self, user_profile, file_analysis):
        """Genera recomendaciones de colaboración"""
        recommendations = []
        
        # Recomendaciones basadas en expertise
        expertise_areas = user_profile.get("expertise_areas", [])
        
        for area in expertise_areas:
            recommendations.append({
                "type": "collaboration",
                "priority": "medium",
                "title": f"Compartir expertise en {area}",
                "description": f"Tienes experiencia en {area}",
                "action": f"Considerar crear guías o mentorías en {area}",
                "area": area,
                "score": 0.7
            })
        
        # Recomendaciones de documentación
        if file_analysis.get("content_stats", {}).get("files_with_metadata", 0) < 50:
            recommendations.append({
                "type": "documentation",
                "priority": "high",
                "title": "Mejorar documentación",
                "description": "Muchos archivos carecen de documentación adecuada",
                "action": "Crear templates de documentación estándar",
                "score": 0.8
            })
        
        return recommendations
    
    def calculate_priority_scores(self, recommendations):
        """Calcula puntuaciones de prioridad"""
        priority_scores = {}
        
        for rec in recommendations:
            base_score = rec.get("score", 0.5)
            
            # Ajustar por tipo
            type_multipliers = {
                "optimization": 1.2,
                "cleanup": 1.1,
                "metadata": 0.9,
                "organization": 0.8,
                "collaboration": 0.7,
                "documentation": 1.0
            }
            
            type_multiplier = type_multipliers.get(rec["type"], 1.0)
            final_score = base_score * type_multiplier
            
            priority_scores[rec["title"]] = final_score
        
        return priority_scores
    
    def generate_recommendations(self, file_analysis=None, user_files=None):
        """Genera todas las recomendaciones"""
        print("🤖 Generando recomendaciones inteligentes...")
        
        # Analizar comportamiento del usuario
        if user_files:
            self.recommendations["user_profile"] = self.analyze_user_behavior(user_files)
        else:
            # Usar archivos recientes como proxy
            recent_files = self.get_recent_files()
            self.recommendations["user_profile"] = self.analyze_user_behavior(recent_files)
        
        # Generar recomendaciones por categoría
        self.recommendations["content_recommendations"] = self.generate_content_recommendations(
            self.recommendations["user_profile"], 
            self.get_all_files()
        )
        
        if file_analysis:
            self.recommendations["optimization_recommendations"] = self.generate_optimization_recommendations(file_analysis)
            self.recommendations["organization_recommendations"] = self.generate_organization_recommendations(file_analysis)
        
        self.recommendations["collaboration_recommendations"] = self.generate_collaboration_recommendations(
            self.recommendations["user_profile"],
            file_analysis or {}
        )
        
        # Calcular puntuaciones de prioridad
        all_recommendations = (
            self.recommendations["content_recommendations"] +
            self.recommendations["optimization_recommendations"] +
            self.recommendations["organization_recommendations"] +
            self.recommendations["collaboration_recommendations"]
        )
        
        self.recommendations["priority_scores"] = self.calculate_priority_scores(all_recommendations)
        
        print("✅ Recomendaciones generadas")
        return self.recommendations
    
    def get_recent_files(self, days=30):
        """Obtiene archivos modificados recientemente"""
        recent_files = []
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    if os.path.getmtime(file_path) > cutoff_time:
                        recent_files.append(file_path)
        
        return recent_files
    
    def get_all_files(self):
        """Obtiene todos los archivos markdown"""
        all_files = []
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                if file.endswith('.md'):
                    all_files.append(os.path.join(root, file))
        return all_files
    
    def save_recommendations(self, output_file="recommendations.json"):
        """Guarda las recomendaciones"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.recommendations, f, indent=2, ensure_ascii=False)
        
        print(f"💡 Recomendaciones guardadas en {output_file}")
    
    def print_recommendations(self, limit=10):
        """Imprime las recomendaciones principales"""
        all_recommendations = (
            self.recommendations["content_recommendations"] +
            self.recommendations["optimization_recommendations"] +
            self.recommendations["organization_recommendations"] +
            self.recommendations["collaboration_recommendations"]
        )
        
        # Ordenar por puntuación de prioridad
        sorted_recommendations = sorted(
            all_recommendations,
            key=lambda x: self.recommendations["priority_scores"].get(x["title"], 0),
            reverse=True
        )
        
        print("\n" + "="*60)
        print("💡 RECOMENDACIONES INTELIGENTES")
        print("="*60)
        
        for i, rec in enumerate(sorted_recommendations[:limit], 1):
            priority = rec.get("priority", "medium")
            score = self.recommendations["priority_scores"].get(rec["title"], 0)
            
            print(f"\n{i}. {rec['title']} ({priority.upper()}) - Score: {score:.2f}")
            print(f"   📝 {rec['description']}")
            print(f"   🎯 Acción: {rec['action']}")
            
            if rec.get("files"):
                print(f"   📁 Archivos afectados: {len(rec['files'])}")
            
            if rec.get("category"):
                print(f"   📂 Categoría: {rec['category']}")

def main():
    parser = argparse.ArgumentParser(description='Sistema de recomendaciones inteligente')
    parser.add_argument('--path', default='.', help='Ruta del directorio a analizar')
    parser.add_argument('--output', default='recommendations.json', help='Archivo de salida')
    parser.add_argument('--analysis', help='Archivo de análisis de contenido')
    parser.add_argument('--limit', type=int, default=10, help='Número de recomendaciones a mostrar')
    
    args = parser.parse_args()
    
    # Cargar análisis de contenido si está disponible
    file_analysis = None
    if args.analysis and os.path.exists(args.analysis):
        with open(args.analysis, 'r', encoding='utf-8') as f:
            file_analysis = json.load(f)
    
    # Generar recomendaciones
    recommender = RecommendationSystem(args.path)
    recommendations = recommender.generate_recommendations(file_analysis)
    
    # Guardar y mostrar
    recommender.save_recommendations(args.output)
    recommender.print_recommendations(args.limit)

if __name__ == "__main__":
    main()














