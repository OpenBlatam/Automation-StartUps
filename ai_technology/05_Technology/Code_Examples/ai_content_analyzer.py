#!/usr/bin/env python3
"""
Sistema de IA para análisis de contenido y categorización inteligente
"""

import os
import json
import re
from datetime import datetime
from collections import Counter, defaultdict
import hashlib

class AIContentAnalyzer:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.analysis_file = os.path.join(base_path, "ai_analysis.json")
        self.business_areas = {
            '01_Marketing': {
                'keywords': ['marketing', 'advertising', 'brand', 'campaign', 'content', 'social', 'seo', 'sem', 'ppc', 'email', 'digital', 'growth', 'conversion', 'analytics', 'anchor', 'ab_test', 'analisis', 'sentimientos', 'tendencias', 'competencia', 'casos_uso', 'personalizados', 'multilenguaje', 'neuro_marketing', 'viral', 'omnichannel', 'customer_experience', 'customer_success', 'lifetime_value', 'personalization', 'webinar', 'copy', 'copywriting', 'storytelling', 'engagement', 'traffic', 'leads', 'funnel'],
                'weight': 1.0
            },
            '02_Finance': {
                'keywords': ['financial', 'finance', 'budget', 'revenue', 'profit', 'cost', 'investment', 'roi', 'wealth', 'money', 'accounting', 'tax', 'audit', 'treasury', 'capital', 'funding', 'valuation', 'pricing', 'billing', 'presupuesto', 'costos', 'modelo', 'financiero', 'startup', 'cashflow', 'ebitda', 'margins'],
                'weight': 1.0
            },
            '03_Human_Resources': {
                'keywords': ['hr', 'human', 'talent', 'recruitment', 'hiring', 'employee', 'staff', 'workforce', 'training', 'development', 'performance', 'compensation', 'benefits', 'culture', 'leadership', 'team', 'skills', 'career', 'onboarding', 'capacitacion', 'vendedores', 'satisfaction', 'survey', 'guia', 'deteccion', 'talento', 'people', 'personnel'],
                'weight': 1.0
            },
            '04_Operations': {
                'keywords': ['operations', 'operational', 'process', 'workflow', 'efficiency', 'productivity', 'optimization', 'supply', 'logistics', 'procurement', 'vendor', 'quality', 'compliance', 'safety', 'maintenance', 'facilities', 'cvr', 'optimization', 'estrategias', 'security', 'compliance', 'guia', 'manual', 'regulaciones', 'fintech'],
                'weight': 1.0
            },
            '05_Technology': {
                'keywords': ['technology', 'tech', 'digital', 'software', 'hardware', 'it', 'infrastructure', 'system', 'platform', 'development', 'programming', 'coding', 'database', 'security', 'cyber', 'cloud', 'api', 'integration', 'sistema', 'ia', 'consciente', 'integracion', 'crm', 'avanzado', 'automatizacion', 'sistemas', 'checklist', 'implementacion', 'rapida', 'guia', 'por', 'roles', 'responsabilidades', 'metricas', 'kpis', 'ia', 'devops', 'deployment', 'monitoring', 'logging', 'scalability', 'performance'],
                'weight': 1.0
            },
            '06_Strategy': {
                'keywords': ['strategy', 'strategic', 'planning', 'business', 'management', 'leadership', 'decision', 'innovation', 'transformation', 'change', 'crisis', 'communication', 'negotiation', 'public_speaking', 'problem_solving', 'time_management', 'productivity', 'agile', 'project', 'implementation', 'improvement', 'international', 'expansion', 'partnerships', 'sustainability', 'resumen', 'mejoras', 'singularidad', 'implementacion', 'tipo', 'organizacion', 'ejecutivo', 'curso', 'premium', 'guia', 'escalabilidad', 'crecimiento'],
                'weight': 1.0
            },
            '07_Risk_Management': {
                'keywords': ['risk', 'security', 'compliance', 'audit', 'governance', 'policy', 'assessment', 'monitoring', 'response', 'crisis', 'emergency', 'disaster', 'insurance', 'legal', 'regulatory', 'fraud', 'threat', 'vulnerability', 'seguridad', 'cumplimiento', 'auditoria', 'politica', 'evaluacion', 'monitoreo', 'respuesta'],
                'weight': 1.0
            },
            '08_AI_Artificial_Intelligence': {
                'keywords': ['ai', 'artificial', 'intelligence', 'machine_learning', 'ml', 'deep_learning', 'neural', 'algorithm', 'automation', 'robotics', 'chatbot', 'nlp', 'computer_vision', 'predictive', 'analytics', 'data_science', 'blockchain', 'cryptocurrency', 'defi', 'nft', 'quantum', 'consciousness', 'transcendent', 'infinite', 'consciente', 'artificial', 'suprema', 'ultra', 'avanzada', 'implementacion', 'practica', 'consciencia', 'machine', 'learning', 'neural', 'network', 'automation', 'intelligent', 'smart', 'cognitive'],
                'weight': 1.0
            },
            '09_Sales': {
                'keywords': ['sales', 'selling', 'revenue', 'conversion', 'leads', 'prospects', 'pipeline', 'crm', 'customer', 'client', 'deal', 'negotiation', 'closing', 'upselling', 'cross_selling', 'retention', 'acquisition', 'vendedores', 'avanzado', 'capacitacion', 'sistema', 'integracion', 'crm', 'avanzado', 'reporte', 'final', 'pipeline', 'mejoras', 'universales', 'omniversales', 'infinitas', 'selling', 'revenue', 'conversion'],
                'weight': 1.0
            },
            '10_Customer_Service': {
                'keywords': ['customer_service', 'support', 'service', 'help', 'ticket', 'resolution', 'satisfaction', 'feedback', 'complaint', 'escalation', 'knowledge_base', 'faq', 'chat', 'phone', 'email_support', 'sistema', 'neurofeedback', 'aprendizaje', 'customer', 'support', 'service', 'help', 'ticket', 'resolution'],
                'weight': 1.0
            }
        }
    
    def extract_content_features(self, content):
        """Extraer características del contenido para análisis"""
        features = {
            'word_count': len(content.split()),
            'char_count': len(content),
            'sentence_count': len(re.findall(r'[.!?]+', content)),
            'paragraph_count': len(content.split('\n\n')),
            'keywords': re.findall(r'\b\w{4,}\b', content.lower()),
            'technical_terms': [],
            'business_terms': [],
            'emotion_indicators': [],
            'action_words': [],
            'numbers': re.findall(r'\b\d+\b', content),
            'percentages': re.findall(r'\d+%', content),
            'dates': re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', content),
            'emails': re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content),
            'urls': re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        }
        
        # Clasificar palabras por tipo
        technical_terms = ['api', 'database', 'algorithm', 'framework', 'architecture', 'integration', 'deployment', 'scalability', 'performance', 'optimization', 'automation', 'machine_learning', 'artificial_intelligence', 'blockchain', 'cloud', 'devops', 'microservices', 'containerization', 'kubernetes', 'docker']
        business_terms = ['strategy', 'management', 'leadership', 'stakeholder', 'roi', 'kpi', 'metrics', 'analytics', 'dashboard', 'reporting', 'budget', 'revenue', 'profit', 'cost', 'investment', 'valuation', 'market', 'customer', 'client', 'sales', 'marketing', 'brand', 'campaign']
        emotion_indicators = ['excellent', 'amazing', 'outstanding', 'terrible', 'awful', 'disappointing', 'exciting', 'frustrating', 'satisfying', 'challenging', 'innovative', 'revolutionary', 'breakthrough', 'cutting_edge', 'state_of_the_art']
        action_words = ['implement', 'execute', 'develop', 'create', 'build', 'design', 'optimize', 'improve', 'enhance', 'upgrade', 'transform', 'revolutionize', 'disrupt', 'innovate', 'pioneer', 'lead', 'manage', 'coordinate', 'facilitate', 'enable', 'empower']
        
        features['technical_terms'] = [word for word in features['keywords'] if word in technical_terms]
        features['business_terms'] = [word for word in features['keywords'] if word in business_terms]
        features['emotion_indicators'] = [word for word in features['keywords'] if word in emotion_indicators]
        features['action_words'] = [word for word in features['keywords'] if word in action_words]
        
        return features
    
    def calculate_content_score(self, content, area_keywords):
        """Calcular puntuación de contenido para un área específica"""
        features = self.extract_content_features(content)
        score = 0
        
        # Puntuación por coincidencia de palabras clave
        content_lower = content.lower()
        for keyword in area_keywords:
            if keyword.lower() in content_lower:
                score += 1
        
        # Puntuación por densidad de palabras clave
        keyword_density = len([word for word in features['keywords'] if word in area_keywords])
        if features['word_count'] > 0:
            density_score = (keyword_density / features['word_count']) * 100
            score += density_score * 0.1
        
        # Puntuación por características específicas del área
        if 'marketing' in area_keywords[0].lower():
            if features['emotion_indicators']:
                score += len(features['emotion_indicators']) * 0.5
            if features['action_words']:
                score += len(features['action_words']) * 0.3
        
        if 'technology' in area_keywords[0].lower():
            if features['technical_terms']:
                score += len(features['technical_terms']) * 0.8
            if features['urls']:
                score += len(features['urls']) * 0.5
        
        if 'finance' in area_keywords[0].lower():
            if features['numbers']:
                score += len(features['numbers']) * 0.2
            if features['percentages']:
                score += len(features['percentages']) * 0.5
        
        return score
    
    def analyze_document(self, file_path):
        """Analizar un documento individual"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            filename = os.path.basename(file_path)
            features = self.extract_content_features(content)
            
            # Calcular puntuaciones para cada área
            area_scores = {}
            for area_code, area_data in self.business_areas.items():
                score = self.calculate_content_score(content, area_data['keywords'])
                area_scores[area_code] = score
            
            # Determinar área más probable
            best_area = max(area_scores, key=area_scores.get)
            confidence = area_scores[best_area] / max(area_scores.values()) if max(area_scores.values()) > 0 else 0
            
            analysis = {
                'filename': filename,
                'path': file_path,
                'features': features,
                'area_scores': area_scores,
                'predicted_area': best_area,
                'confidence': confidence,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e), 'filename': os.path.basename(file_path)}
    
    def analyze_all_documents(self):
        """Analizar todos los documentos del sistema"""
        print("🤖 Iniciando análisis de IA de todos los documentos...")
        
        all_analyses = []
        total_files = 0
        analyzed_files = 0
        
        for area_code, area_name in self.business_areas.items():
            area_path = os.path.join(self.base_path, area_code)
            if not os.path.exists(area_path):
                continue
            
            print(f"📁 Analizando área: {area_name}")
            
            for root, dirs, files in os.walk(area_path):
                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        total_files += 1
                        
                        analysis = self.analyze_document(file_path)
                        if 'error' not in analysis:
                            analyzed_files += 1
                            all_analyses.append(analysis)
                        
                        if analyzed_files % 10 == 0:
                            print(f"   ✅ Analizados: {analyzed_files}/{total_files}")
        
        # Guardar análisis completo
        analysis_data = {
            'timestamp': datetime.now().isoformat(),
            'total_files': total_files,
            'analyzed_files': analyzed_files,
            'analyses': all_analyses,
            'summary': self.generate_analysis_summary(all_analyses)
        }
        
        with open(self.analysis_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"\n✅ Análisis completado: {analyzed_files}/{total_files} archivos")
        print(f"📊 Datos guardados en: {self.analysis_file}")
        
        return analysis_data
    
    def generate_analysis_summary(self, analyses):
        """Generar resumen del análisis"""
        summary = {
            'total_documents': len(analyses),
            'area_distribution': Counter(),
            'confidence_stats': {'high': 0, 'medium': 0, 'low': 0},
            'content_insights': {},
            'misclassified_documents': []
        }
        
        for analysis in analyses:
            # Distribución por área
            summary['area_distribution'][analysis['predicted_area']] += 1
            
            # Estadísticas de confianza
            confidence = analysis['confidence']
            if confidence >= 0.8:
                summary['confidence_stats']['high'] += 1
            elif confidence >= 0.5:
                summary['confidence_stats']['medium'] += 1
            else:
                summary['confidence_stats']['low'] += 1
            
            # Documentos posiblemente mal clasificados
            if confidence < 0.3:
                summary['misclassified_documents'].append({
                    'filename': analysis['filename'],
                    'predicted_area': analysis['predicted_area'],
                    'confidence': confidence
                })
        
        # Insights de contenido
        all_features = [analysis['features'] for analysis in analyses]
        summary['content_insights'] = {
            'avg_word_count': sum(f['word_count'] for f in all_features) / len(all_features),
            'most_common_technical_terms': Counter([term for f in all_features for term in f['technical_terms']]).most_common(10),
            'most_common_business_terms': Counter([term for f in all_features for term in f['business_terms']]).most_common(10),
            'documents_with_emails': len([f for f in all_features if f['emails']]),
            'documents_with_urls': len([f for f in all_features if f['urls']])
        }
        
        return summary
    
    def get_content_recommendations(self):
        """Obtener recomendaciones basadas en análisis de contenido"""
        if not os.path.exists(self.analysis_file):
            print("❌ No hay análisis disponible. Ejecute el análisis primero.")
            return
        
        with open(self.analysis_file, 'r') as f:
            data = json.load(f)
        
        summary = data['summary']
        recommendations = []
        
        # Recomendaciones basadas en confianza
        low_confidence_count = summary['confidence_stats']['low']
        if low_confidence_count > 0:
            recommendations.append(f"Revisar {low_confidence_count} documentos con baja confianza de clasificación")
        
        # Recomendaciones basadas en distribución
        area_dist = summary['area_distribution']
        if len(area_dist) > 0:
            most_common_area = max(area_dist, key=area_dist.get)
            least_common_area = min(area_dist, key=area_dist.get)
            
            if area_dist[most_common_area] > area_dist[least_common_area] * 3:
                recommendations.append(f"Considerar balancear contenido entre áreas (más contenido en {least_common_area})")
        
        # Recomendaciones basadas en contenido
        insights = summary['content_insights']
        if insights['documents_with_emails'] < len(data['analyses']) * 0.1:
            recommendations.append("Considerar agregar más información de contacto en documentos")
        
        if insights['documents_with_urls'] < len(data['analyses']) * 0.2:
            recommendations.append("Considerar agregar más enlaces y referencias externas")
        
        return recommendations
    
    def print_analysis_report(self):
        """Imprimir reporte de análisis"""
        if not os.path.exists(self.analysis_file):
            print("❌ No hay análisis disponible. Ejecute el análisis primero.")
            return
        
        with open(self.analysis_file, 'r') as f:
            data = json.load(f)
        
        summary = data['summary']
        
        print("🤖 REPORTE DE ANÁLISIS DE IA")
        print("=" * 50)
        
        print(f"\n📊 ESTADÍSTICAS GENERALES:")
        print(f"📁 Total de documentos analizados: {summary['total_documents']}")
        print(f"🎯 Confianza alta (≥80%): {summary['confidence_stats']['high']}")
        print(f"⚠️  Confianza media (50-79%): {summary['confidence_stats']['medium']}")
        print(f"❌ Confianza baja (<50%): {summary['confidence_stats']['low']}")
        
        print(f"\n📈 DISTRIBUCIÓN POR ÁREA:")
        for area, count in summary['area_distribution'].most_common():
            area_name = self.business_areas.get(area, {}).get('keywords', [area])[0].title()
            print(f"  • {area_name}: {count} documentos")
        
        print(f"\n📝 INSIGHTS DE CONTENIDO:")
        insights = summary['content_insights']
        print(f"  📊 Promedio de palabras por documento: {insights['avg_word_count']:.0f}")
        print(f"  📧 Documentos con emails: {insights['documents_with_emails']}")
        print(f"  🔗 Documentos con URLs: {insights['documents_with_urls']}")
        
        if insights['most_common_technical_terms']:
            print(f"\n🔧 Términos técnicos más comunes:")
            for term, count in insights['most_common_technical_terms'][:5]:
                print(f"  • {term}: {count}")
        
        if insights['most_common_business_terms']:
            print(f"\n💼 Términos de negocio más comunes:")
            for term, count in insights['most_common_business_terms'][:5]:
                print(f"  • {term}: {count}")
        
        # Recomendaciones
        recommendations = self.get_content_recommendations()
        if recommendations:
            print(f"\n💡 RECOMENDACIONES:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")

def main():
    analyzer = AIContentAnalyzer()
    
    print("🤖 Sistema de Análisis de Contenido con IA")
    print("=" * 50)
    print("1. Analizar todos los documentos")
    print("2. Ver reporte de análisis")
    print("3. Obtener recomendaciones")
    print("4. Salir")
    
    choice = input("\nSeleccione una opción (1-4): ").strip()
    
    if choice == '1':
        analyzer.analyze_all_documents()
    
    elif choice == '2':
        analyzer.print_analysis_report()
    
    elif choice == '3':
        recommendations = analyzer.get_content_recommendations()
        if recommendations:
            print("\n💡 RECOMENDACIONES BASADAS EN IA:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print("\n✅ No hay recomendaciones específicas en este momento")
    
    elif choice == '4':
        print("👋 ¡Hasta luego!")
    
    else:
        print("❌ Opción no válida")

if __name__ == "__main__":
    main()



