#!/usr/bin/env python3
"""
Analizador de Contenido con IA Avanzado
Analiza contenido usando técnicas de IA para optimización inteligente
"""

import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
import difflib

class AIContentAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.content_insights = defaultdict(dict)
        self.ai_recommendations = []
        self.content_quality_scores = {}
        self.optimization_opportunities = []
        
    def analyze_content_with_ai(self):
        """Analiza contenido usando técnicas de IA avanzadas"""
        print("🤖 Analizando contenido con IA avanzada...")
        
        # Analizar todos los archivos de texto
        text_files = []
        for file_path in self.project_root.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    text_files.append((str(file_path), content))
            except:
                continue
        
        for file_path, content in text_files:
            analysis = self._ai_analyze_content(content, file_path)
            self.content_insights[file_path] = analysis
            
            # Calcular puntuación de calidad
            quality_score = self._calculate_content_quality(content, analysis)
            self.content_quality_scores[file_path] = quality_score
    
    def generate_ai_recommendations(self):
        """Genera recomendaciones de IA para optimización"""
        print("💡 Generando recomendaciones de IA...")
        
        # Análisis de patrones de contenido
        content_patterns = self._analyze_content_patterns()
        
        # Recomendaciones de estructura
        structure_recommendations = self._generate_structure_recommendations()
        
        # Recomendaciones de optimización
        optimization_recommendations = self._generate_optimization_recommendations()
        
        # Recomendaciones de consolidación
        consolidation_recommendations = self._generate_consolidation_recommendations()
        
        self.ai_recommendations = {
            'content_patterns': content_patterns,
            'structure_recommendations': structure_recommendations,
            'optimization_recommendations': optimization_recommendations,
            'consolidation_recommendations': consolidation_recommendations,
            'timestamp': datetime.now().isoformat()
        }
    
    def create_ai_optimization_report(self):
        """Crea reporte de optimización con IA"""
        print("📊 Creando reporte de optimización con IA...")
        
        report_path = self.project_root / "97_Analysis_Reports" / "AI_Optimization_Report.md"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 🤖 Reporte de Optimización con IA\n\n")
            f.write(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Resumen ejecutivo
            f.write("## 📋 Resumen Ejecutivo\n\n")
            total_files = len(self.content_insights)
            avg_quality = sum(self.content_quality_scores.values()) / len(self.content_quality_scores) if self.content_quality_scores else 0
            f.write(f"- **Total de archivos analizados**: {total_files}\n")
            f.write(f"- **Puntuación promedio de calidad**: {avg_quality:.2f}/10\n")
            f.write(f"- **Recomendaciones generadas**: {len(self.ai_recommendations.get('optimization_recommendations', []))}\n\n")
            
            # Análisis de patrones
            f.write("## 🔍 Análisis de Patrones de Contenido\n\n")
            patterns = self.ai_recommendations.get('content_patterns', {})
            for pattern_type, details in patterns.items():
                f.write(f"### {pattern_type}\n")
                f.write(f"{details}\n\n")
            
            # Recomendaciones de estructura
            f.write("## 🏗️ Recomendaciones de Estructura\n\n")
            structure_recs = self.ai_recommendations.get('structure_recommendations', [])
            for i, rec in enumerate(structure_recs, 1):
                f.write(f"{i}. {rec}\n")
            f.write("\n")
            
            # Recomendaciones de optimización
            f.write("## ⚡ Recomendaciones de Optimización\n\n")
            opt_recs = self.ai_recommendations.get('optimization_recommendations', [])
            for i, rec in enumerate(opt_recs, 1):
                f.write(f"{i}. {rec}\n")
            f.write("\n")
            
            # Recomendaciones de consolidación
            f.write("## 🔗 Recomendaciones de Consolidación\n\n")
            cons_recs = self.ai_recommendations.get('consolidation_recommendations', [])
            for i, rec in enumerate(cons_recs, 1):
                f.write(f"{i}. {rec}\n")
            f.write("\n")
            
            # Análisis de calidad por archivo
            f.write("## 📈 Análisis de Calidad por Archivo\n\n")
            sorted_files = sorted(self.content_quality_scores.items(), key=lambda x: x[1], reverse=True)
            for file_path, score in sorted_files[:20]:  # Top 20
                f.write(f"- **{Path(file_path).name}**: {score:.2f}/10\n")
            f.write("\n")
            
            # Oportunidades de mejora
            f.write("## 🎯 Oportunidades de Mejora\n\n")
            for i, opp in enumerate(self.optimization_opportunities, 1):
                f.write(f"{i}. {opp}\n")
            f.write("\n")
    
    def create_content_intelligence_dashboard(self):
        """Crea dashboard de inteligencia de contenido"""
        print("📊 Creando dashboard de inteligencia de contenido...")
        
        dashboard_path = self.project_root / "97_Analysis_Reports" / "Content_Intelligence_Dashboard.json"
        
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_files_analyzed': len(self.content_insights),
                'average_quality_score': sum(self.content_quality_scores.values()) / len(self.content_quality_scores) if self.content_quality_scores else 0,
                'high_quality_files': len([s for s in self.content_quality_scores.values() if s >= 8]),
                'medium_quality_files': len([s for s in self.content_quality_scores.values() if 5 <= s < 8]),
                'low_quality_files': len([s for s in self.content_quality_scores.values() if s < 5])
            },
            'content_insights': dict(self.content_insights),
            'quality_scores': self.content_quality_scores,
            'ai_recommendations': self.ai_recommendations,
            'optimization_opportunities': self.optimization_opportunities
        }
        
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
        
        print(f"  💾 Dashboard guardado en: {dashboard_path}")
    
    def _ai_analyze_content(self, content, file_path):
        """Análisis de contenido usando técnicas de IA"""
        # Análisis de estructura
        structure_analysis = self._analyze_structure(content)
        
        # Análisis de complejidad
        complexity_analysis = self._analyze_complexity(content)
        
        # Análisis de coherencia
        coherence_analysis = self._analyze_coherence(content)
        
        # Análisis de completitud
        completeness_analysis = self._analyze_completeness(content)
        
        # Análisis de relevancia
        relevance_analysis = self._analyze_relevance(content, file_path)
        
        return {
            'structure': structure_analysis,
            'complexity': complexity_analysis,
            'coherence': coherence_analysis,
            'completeness': completeness_analysis,
            'relevance': relevance_analysis,
            'file_size': len(content),
            'word_count': len(content.split()),
            'line_count': len(content.splitlines())
        }
    
    def _analyze_structure(self, content):
        """Analiza la estructura del contenido"""
        lines = content.splitlines()
        
        # Detectar encabezados
        headers = [line for line in lines if line.strip().startswith('#')]
        
        # Detectar listas
        lists = [line for line in lines if line.strip().startswith(('-', '*', '+'))]
        
        # Detectar código
        code_blocks = len(re.findall(r'```', content))
        
        # Detectar enlaces
        links = len(re.findall(r'\[.*?\]\(.*?\)', content))
        
        return {
            'headers_count': len(headers),
            'lists_count': len(lists),
            'code_blocks_count': code_blocks // 2,
            'links_count': links,
            'structure_score': min(10, (len(headers) * 2 + len(lists) + code_blocks + links) / 10)
        }
    
    def _analyze_complexity(self, content):
        """Analiza la complejidad del contenido"""
        words = content.split()
        
        # Palabras largas
        long_words = [w for w in words if len(w) > 10]
        
        # Oraciones largas
        sentences = re.split(r'[.!?]+', content)
        long_sentences = [s for s in sentences if len(s.split()) > 20]
        
        # Densidad de información
        unique_words = len(set(words))
        total_words = len(words)
        vocabulary_diversity = unique_words / total_words if total_words > 0 else 0
        
        return {
            'long_words_count': len(long_words),
            'long_sentences_count': len(long_sentences),
            'vocabulary_diversity': vocabulary_diversity,
            'complexity_score': min(10, (vocabulary_diversity * 5 + len(long_words) / 10 + len(long_sentences) / 5))
        }
    
    def _analyze_coherence(self, content):
        """Analiza la coherencia del contenido"""
        # Detectar transiciones
        transitions = ['además', 'por otro lado', 'sin embargo', 'por lo tanto', 'en consecuencia', 'finalmente', 'en resumen']
        transition_count = sum(content.lower().count(t) for t in transitions)
        
        # Detectar repeticiones
        words = content.lower().split()
        word_freq = Counter(words)
        repetitions = sum(1 for count in word_freq.values() if count > 5)
        
        # Detectar párrafos
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        
        return {
            'transitions_count': transition_count,
            'repetitions_count': repetitions,
            'paragraphs_count': len(paragraphs),
            'avg_paragraph_length': avg_paragraph_length,
            'coherence_score': min(10, (transition_count * 2 + max(0, 10 - repetitions) + min(10, avg_paragraph_length / 5)))
        }
    
    def _analyze_completeness(self, content):
        """Analiza la completitud del contenido"""
        # Detectar secciones comunes
        common_sections = ['introducción', 'desarrollo', 'conclusión', 'resumen', 'objetivo', 'metodología', 'resultados']
        section_count = sum(1 for section in common_sections if section in content.lower())
        
        # Detectar información faltante
        missing_indicators = ['pendiente', 'por completar', 'tbd', 'todo', 'faltante']
        missing_count = sum(content.lower().count(indicator) for indicator in missing_indicators)
        
        # Longitud del contenido
        content_length = len(content)
        
        return {
            'sections_count': section_count,
            'missing_indicators_count': missing_count,
            'content_length': content_length,
            'completeness_score': min(10, (section_count * 2 + max(0, 10 - missing_count) + min(5, content_length / 1000)))
        }
    
    def _analyze_relevance(self, content, file_path):
        """Analiza la relevancia del contenido"""
        # Obtener categoría del archivo
        category = self._get_file_category(file_path)
        
        # Palabras clave por categoría
        category_keywords = {
            '01_Marketing': ['marketing', 'ventas', 'promoción', 'publicidad', 'cliente'],
            '02_Finance': ['financiero', 'dinero', 'inversión', 'presupuesto', 'costos'],
            '03_Human_Resources': ['recursos humanos', 'empleado', 'contratación', 'capacitación'],
            '04_Operations': ['operaciones', 'proceso', 'eficiencia', 'productividad'],
            '05_Technology': ['tecnología', 'software', 'sistema', 'digital', 'automatización'],
            '06_Strategy': ['estrategia', 'planificación', 'objetivo', 'visión', 'misión'],
            '07_Risk_Management': ['riesgo', 'seguridad', 'protección', 'prevención'],
            '08_AI_Artificial_Intelligence': ['inteligencia artificial', 'ia', 'machine learning', 'algoritmo'],
            '09_Sales': ['ventas', 'cliente', 'prospecto', 'negociación'],
            '10_Customer_Service': ['servicio al cliente', 'soporte', 'atención', 'satisfacción']
        }
        
        keywords = category_keywords.get(category, [])
        relevance_score = 0
        
        if keywords:
            content_lower = content.lower()
            keyword_matches = sum(1 for keyword in keywords if keyword in content_lower)
            relevance_score = min(10, (keyword_matches / len(keywords)) * 10)
        
        return {
            'category': category,
            'relevance_score': relevance_score,
            'keyword_matches': keyword_matches if keywords else 0
        }
    
    def _calculate_content_quality(self, content, analysis):
        """Calcula puntuación de calidad del contenido"""
        structure_score = analysis['structure']['structure_score']
        complexity_score = analysis['complexity']['complexity_score']
        coherence_score = analysis['coherence']['coherence_score']
        completeness_score = analysis['completeness']['completeness_score']
        relevance_score = analysis['relevance']['relevance_score']
        
        # Ponderación de scores
        quality_score = (
            structure_score * 0.2 +
            complexity_score * 0.2 +
            coherence_score * 0.25 +
            completeness_score * 0.2 +
            relevance_score * 0.15
        )
        
        return min(10, quality_score)
    
    def _analyze_content_patterns(self):
        """Analiza patrones en el contenido"""
        patterns = {}
        
        # Patrón de longitud
        lengths = [insight['file_size'] for insight in self.content_insights.values()]
        patterns['length_distribution'] = {
            'short_files': len([l for l in lengths if l < 1000]),
            'medium_files': len([l for l in lengths if 1000 <= l < 5000]),
            'long_files': len([l for l in lengths if l >= 5000])
        }
        
        # Patrón de estructura
        structure_scores = [insight['structure']['structure_score'] for insight in self.content_insights.values()]
        patterns['structure_quality'] = {
            'well_structured': len([s for s in structure_scores if s >= 7]),
            'moderately_structured': len([s for s in structure_scores if 4 <= s < 7]),
            'poorly_structured': len([s for s in structure_scores if s < 4])
        }
        
        return patterns
    
    def _generate_structure_recommendations(self):
        """Genera recomendaciones de estructura"""
        recommendations = []
        
        # Analizar archivos con baja puntuación de estructura
        low_structure_files = [
            path for path, insight in self.content_insights.items()
            if insight['structure']['structure_score'] < 5
        ]
        
        if low_structure_files:
            recommendations.append(f"Mejorar estructura en {len(low_structure_files)} archivos con baja puntuación")
        
        # Recomendaciones generales
        recommendations.extend([
            "Agregar más encabezados para mejorar navegación",
            "Incluir listas para organizar información",
            "Añadir enlaces internos para conectar contenido relacionado",
            "Usar bloques de código para ejemplos técnicos"
        ])
        
        return recommendations
    
    def _generate_optimization_recommendations(self):
        """Genera recomendaciones de optimización"""
        recommendations = []
        
        # Archivos con baja calidad
        low_quality_files = [
            path for path, score in self.content_quality_scores.items()
            if score < 5
        ]
        
        if low_quality_files:
            recommendations.append(f"Revisar y mejorar {len(low_quality_files)} archivos de baja calidad")
        
        # Recomendaciones específicas
        recommendations.extend([
            "Consolidar contenido duplicado o similar",
            "Estandarizar formato y estructura",
            "Agregar metadatos y descripciones",
            "Optimizar para búsqueda y navegación"
        ])
        
        return recommendations
    
    def _generate_consolidation_recommendations(self):
        """Genera recomendaciones de consolidación"""
        recommendations = []
        
        # Identificar archivos similares
        similar_files = self._find_similar_files()
        
        if similar_files:
            recommendations.append(f"Considerar consolidar {len(similar_files)} grupos de archivos similares")
        
        # Recomendaciones generales
        recommendations.extend([
            "Crear índices maestros para temas relacionados",
            "Eliminar versiones obsoletas de documentos",
            "Agrupar contenido por temas específicos",
            "Crear plantillas para contenido repetitivo"
        ])
        
        return recommendations
    
    def _find_similar_files(self):
        """Encuentra archivos similares"""
        similar_groups = []
        file_paths = list(self.content_insights.keys())
        
        for i, file1 in enumerate(file_paths):
            for file2 in file_paths[i+1:]:
                similarity = self._calculate_file_similarity(file1, file2)
                if similarity > 0.7:
                    similar_groups.append((file1, file2, similarity))
        
        return similar_groups
    
    def _calculate_file_similarity(self, file1, file2):
        """Calcula similitud entre dos archivos"""
        insight1 = self.content_insights[file1]
        insight2 = self.content_insights[file2]
        
        # Comparar características principales
        structure_diff = abs(insight1['structure']['structure_score'] - insight2['structure']['structure_score'])
        complexity_diff = abs(insight1['complexity']['complexity_score'] - insight2['complexity']['complexity_score'])
        size_diff = abs(insight1['file_size'] - insight2['file_size']) / max(insight1['file_size'], insight2['file_size'])
        
        # Calcular similitud (0-1)
        similarity = 1 - (structure_diff + complexity_diff + size_diff) / 3
        return max(0, similarity)
    
    def _get_file_category(self, file_path):
        """Obtiene la categoría de un archivo"""
        path = Path(file_path)
        for part in path.parts:
            if part.startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_', '97_', '98_', '99_')):
                return part
        return None
    
    def run_ai_analysis(self):
        """Ejecuta análisis completo con IA"""
        print("🚀 Iniciando análisis de contenido con IA...")
        
        self.analyze_content_with_ai()
        self.generate_ai_recommendations()
        self.create_ai_optimization_report()
        self.create_content_intelligence_dashboard()
        
        print(f"\n✅ Análisis con IA completado!")
        print(f"Archivos analizados: {len(self.content_insights)}")
        print(f"Recomendaciones generadas: {len(self.ai_recommendations.get('optimization_recommendations', []))}")
        
        return self.ai_recommendations

if __name__ == "__main__":
    analyzer = AIContentAnalyzer("/Users/adan/frontier")
    recommendations = analyzer.run_ai_analysis()
    
    print(f"\n📋 RESUMEN DE ANÁLISIS CON IA:")
    print(f"Recomendaciones de estructura: {len(recommendations.get('structure_recommendations', []))}")
    print(f"Recomendaciones de optimización: {len(recommendations.get('optimization_recommendations', []))}")
    print(f"Recomendaciones de consolidación: {len(recommendations.get('consolidation_recommendations', []))}")
