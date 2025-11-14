#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Multilenguaje - Anchor Texts IA Marketing
=================================================

Este script genera anchor texts en múltiples idiomas con adaptación cultural
y localización específica para diferentes mercados.

Funcionalidades:
- Generación en 11 idiomas principales
- Adaptación cultural por región
- Localización de palabras clave
- Análisis de tendencias por idioma
- Optimización por mercado específico
"""

import random
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple

class GeneradorMultilenguajeAnchorTexts:
    def __init__(self):
        self.palabras_clave_base = [
            "curso IA marketing", "inteligencia artificial marketing", "marketing digital IA",
            "curso marketing automatizado", "IA aplicada marketing", "machine learning marketing"
        ]
        
        # Configuración de idiomas
        self.idiomas = {
            'es': {
                'nombre': 'Español',
                'region': 'España',
                'palabras_clave': [
                    'curso IA marketing', 'inteligencia artificial marketing', 'marketing digital IA',
                    'curso marketing automatizado', 'IA aplicada marketing', 'machine learning marketing'
                ],
                'plantillas': [
                    'Curso {palabra_clave} - {beneficio}',
                    'Aprende {palabra_clave} en {tiempo}',
                    'Domina {palabra_clave} - {garantia}',
                    'Masterclass {palabra_clave} {año}',
                    'Certificación {palabra_clave} - {modalidad}'
                ],
                'beneficios': ['Resultados garantizados', 'Éxito asegurado', 'ROI comprobado', 'Efectividad probada'],
                'tiempos': ['30 días', '6 meses', '1 año', '90 días'],
                'garantias': ['100% efectivo', 'Sin riesgo', 'Satisfacción garantizada', 'Resultados comprobados'],
                'modalidades': ['Online', 'Presencial', 'Híbrido', 'Intensivo']
            },
            'en': {
                'nombre': 'English',
                'region': 'United States',
                'palabras_clave': [
                    'AI marketing course', 'artificial intelligence marketing', 'digital marketing AI',
                    'automated marketing course', 'AI applied marketing', 'machine learning marketing'
                ],
                'plantillas': [
                    'Course {palabra_clave} - {beneficio}',
                    'Learn {palabra_clave} in {tiempo}',
                    'Master {palabra_clave} - {garantia}',
                    'Masterclass {palabra_clave} {año}',
                    'Certification {palabra_clave} - {modalidad}'
                ],
                'beneficios': ['Guaranteed results', 'Assured success', 'Proven ROI', 'Proven effectiveness'],
                'tiempos': ['30 days', '6 months', '1 year', '90 days'],
                'garantias': ['100% effective', 'No risk', 'Satisfaction guaranteed', 'Proven results'],
                'modalidades': ['Online', 'In-person', 'Hybrid', 'Intensive']
            },
            'fr': {
                'nombre': 'Français',
                'region': 'France',
                'palabras_clave': [
                    'cours marketing IA', 'intelligence artificielle marketing', 'marketing digital IA',
                    'cours marketing automatisé', 'IA appliquée marketing', 'machine learning marketing'
                ],
                'plantillas': [
                    'Cours {palabra_clave} - {beneficio}',
                    'Apprenez {palabra_clave} en {tiempo}',
                    'Maîtrisez {palabra_clave} - {garantia}',
                    'Masterclass {palabra_clave} {año}',
                    'Certification {palabra_clave} - {modalidad}'
                ],
                'beneficios': ['Résultats garantis', 'Succès assuré', 'ROI prouvé', 'Efficacité prouvée'],
                'tiempos': ['30 jours', '6 mois', '1 an', '90 jours'],
                'garantias': ['100% efficace', 'Sans risque', 'Satisfaction garantie', 'Résultats prouvés'],
                'modalidades': ['En ligne', 'Présentiel', 'Hybride', 'Intensif']
            },
            'de': {
                'nombre': 'Deutsch',
                'region': 'Germany',
                'palabras_clave': [
                    'KI Marketing Kurs', 'Künstliche Intelligenz Marketing', 'Digitales Marketing KI',
                    'Automatisiertes Marketing Kurs', 'KI angewandt Marketing', 'Machine Learning Marketing'
                ],
                'plantillas': [
                    'Kurs {palabra_clave} - {beneficio}',
                    'Lernen Sie {palabra_clave} in {tiempo}',
                    'Meistern Sie {palabra_clave} - {garantia}',
                    'Masterclass {palabra_clave} {año}',
                    'Zertifizierung {palabra_clave} - {modalidad}'
                ],
                'beneficios': ['Garantierte Ergebnisse', 'Gesicherter Erfolg', 'Bewiesener ROI', 'Bewiesene Wirksamkeit'],
                'tiempos': ['30 Tage', '6 Monate', '1 Jahr', '90 Tage'],
                'garantias': ['100% effektiv', 'Kein Risiko', 'Zufriedenheit garantiert', 'Bewiesene Ergebnisse'],
                'modalidades': ['Online', 'Präsenz', 'Hybrid', 'Intensiv']
            },
            'it': {
                'nombre': 'Italiano',
                'region': 'Italy',
                'palabras_clave': [
                    'corso marketing IA', 'intelligenza artificiale marketing', 'marketing digitale IA',
                    'corso marketing automatizzato', 'IA applicata marketing', 'machine learning marketing'
                ],
                'plantillas': [
                    'Corso {palabra_clave} - {beneficio}',
                    'Impara {palabra_clave} in {tiempo}',
                    'Domina {palabra_clave} - {garantia}',
                    'Masterclass {palabra_clave} {año}',
                    'Certificazione {palabra_clave} - {modalidad}'
                ],
                'beneficios': ['Risultati garantiti', 'Successo assicurato', 'ROI comprovato', 'Efficacia comprovata'],
                'tiempos': ['30 giorni', '6 mesi', '1 anno', '90 giorni'],
                'garantias': ['100% efficace', 'Senza rischio', 'Soddisfazione garantita', 'Risultati comprovati'],
                'modalidades': ['Online', 'In presenza', 'Ibrido', 'Intensivo']
            },
            'pt': {
                'nombre': 'Português',
                'region': 'Brazil',
                'palabras_clave': [
                    'curso marketing IA', 'inteligência artificial marketing', 'marketing digital IA',
                    'curso marketing automatizado', 'IA aplicada marketing', 'machine learning marketing'
                ],
                'plantillas': [
                    'Curso {palabra_clave} - {beneficio}',
                    'Aprenda {palabra_clave} em {tiempo}',
                    'Domine {palabra_clave} - {garantia}',
                    'Masterclass {palabra_clave} {año}',
                    'Certificação {palabra_clave} - {modalidad}'
                ],
                'beneficios': ['Resultados garantidos', 'Sucesso assegurado', 'ROI comprovado', 'Eficácia comprovada'],
                'tiempos': ['30 dias', '6 meses', '1 ano', '90 dias'],
                'garantias': ['100% eficaz', 'Sem risco', 'Satisfação garantida', 'Resultados comprovados'],
                'modalidades': ['Online', 'Presencial', 'Híbrido', 'Intensivo']
            },
            'ru': {
                'nombre': 'Русский',
                'region': 'Russia',
                'palabras_clave': [
                    'курс маркетинг ИИ', 'искусственный интеллект маркетинг', 'цифровой маркетинг ИИ',
                    'курс автоматизированный маркетинг', 'ИИ прикладной маркетинг', 'машинное обучение маркетинг'
                ],
                'plantillas': [
                    'Курс {palabra_clave} - {beneficio}',
                    'Изучите {palabra_clave} за {tiempo}',
                    'Освойте {palabra_clave} - {garantia}',
                    'Мастер-класс {palabra_clave} {año}',
                    'Сертификация {palabra_clave} - {modalidad}'
                ],
                'beneficios': ['Гарантированные результаты', 'Обеспеченный успех', 'Доказанный ROI', 'Доказанная эффективность'],
                'tiempos': ['30 дней', '6 месяцев', '1 год', '90 дней'],
                'garantias': ['100% эффективно', 'Без риска', 'Гарантированное удовлетворение', 'Доказанные результаты'],
                'modalidades': ['Онлайн', 'Очно', 'Гибридный', 'Интенсивный']
            },
            'ja': {
                'nombre': '日本語',
                'region': 'Japan',
                'palabras_clave': [
                    'AIマーケティングコース', '人工知能マーケティング', 'デジタルマーケティングAI',
                    '自動化マーケティングコース', 'AI応用マーケティング', '機械学習マーケティング'
                ],
                'plantillas': [
                    'コース {palabra_clave} - {beneficio}',
                    '{tiempo}で{palabra_clave}を学ぶ',
                    '{palabra_clave}をマスター - {garantia}',
                    'マスタークラス {palabra_clave} {año}',
                    '認定 {palabra_clave} - {modalidad}'
                ],
                'beneficios': ['保証された結果', '確実な成功', '実証されたROI', '実証された効果'],
                'tiempos': ['30日', '6ヶ月', '1年', '90日'],
                'garantias': ['100%効果的', 'リスクなし', '満足保証', '実証された結果'],
                'modalidades': ['オンライン', '対面', 'ハイブリッド', '集中']
            },
            'ko': {
                'nombre': '한국어',
                'region': 'South Korea',
                'palabras_clave': [
                    'AI 마케팅 코스', '인공지능 마케팅', '디지털 마케팅 AI',
                    '자동화 마케팅 코스', 'AI 적용 마케팅', '머신러닝 마케팅'
                ],
                'plantillas': [
                    '코스 {palabra_clave} - {beneficio}',
                    '{tiempo}에 {palabra_clave} 배우기',
                    '{palabra_clave} 마스터 - {garantia}',
                    '마스터클래스 {palabra_clave} {año}',
                    '인증 {palabra_clave} - {modalidad}'
                ],
                'beneficios': ['보장된 결과', '확실한 성공', '입증된 ROI', '입증된 효과'],
                'tiempos': ['30일', '6개월', '1년', '90일'],
                'garantias': ['100% 효과적', '위험 없음', '만족 보장', '입증된 결과'],
                'modalidades': ['온라인', '대면', '하이브리드', '집중']
            },
            'zh': {
                'nombre': '中文',
                'region': 'China',
                'palabras_clave': [
                    'AI营销课程', '人工智能营销', '数字营销AI',
                    '自动化营销课程', 'AI应用营销', '机器学习营销'
                ],
                'plantillas': [
                    '课程 {palabra_clave} - {beneficio}',
                    '在{tiempo}内学习{palabra_clave}',
                    '掌握 {palabra_clave} - {garantia}',
                    '大师班 {palabra_clave} {año}',
                    '认证 {palabra_clave} - {modalidad}'
                ],
                'beneficios': ['保证结果', '确保成功', '验证ROI', '验证效果'],
                'tiempos': ['30天', '6个月', '1年', '90天'],
                'garantias': ['100%有效', '无风险', '满意保证', '验证结果'],
                'modalidades': ['在线', '面对面', '混合', '强化']
            },
            'ar': {
                'nombre': 'العربية',
                'region': 'Saudi Arabia',
                'palabras_clave': [
                    'دورة تسويق الذكاء الاصطناعي', 'التسويق بالذكاء الاصطناعي', 'التسويق الرقمي بالذكاء الاصطناعي',
                    'دورة التسويق الآلي', 'تطبيق الذكاء الاصطناعي في التسويق', 'تسويق التعلم الآلي'
                ],
                'plantillas': [
                    'دورة {palabra_clave} - {beneficio}',
                    'تعلم {palabra_clave} في {tiempo}',
                    'أتقن {palabra_clave} - {garantia}',
                    'فصل رئيسي {palabra_clave} {año}',
                    'شهادة {palabra_clave} - {modalidad}'
                ],
                'beneficios': ['نتائج مضمونة', 'نجاح مضمون', 'عائد استثمار مثبت', 'فعالية مثبتة'],
                'tiempos': ['30 يوم', '6 أشهر', 'سنة واحدة', '90 يوم'],
                'garantias': ['100% فعال', 'بدون مخاطر', 'ضمان الرضا', 'نتائج مثبتة'],
                'modalidades': ['عبر الإنترنت', 'حضوري', 'مختلط', 'مكثف']
            }
        }
        
        # Adaptaciones culturales por región
        self.adaptaciones_culturales = {
            'es': {
                'tono': 'directo',
                'urgencia': 'moderada',
                'formalidad': 'media',
                'elementos_culturales': ['resultados', 'éxito', 'garantía']
            },
            'en': {
                'tono': 'profesional',
                'urgencia': 'alta',
                'formalidad': 'baja',
                'elementos_culturales': ['results', 'success', 'guaranteed']
            },
            'fr': {
                'tono': 'elegante',
                'urgencia': 'baja',
                'formalidad': 'alta',
                'elementos_culturales': ['résultats', 'succès', 'garanti']
            },
            'de': {
                'tono': 'técnico',
                'urgencia': 'moderada',
                'formalidad': 'alta',
                'elementos_culturales': ['ergebnisse', 'erfolg', 'garantiert']
            },
            'it': {
                'tono': 'apasionado',
                'urgencia': 'alta',
                'formalidad': 'media',
                'elementos_culturales': ['risultati', 'successo', 'garantito']
            },
            'pt': {
                'tono': 'cálido',
                'urgencia': 'moderada',
                'formalidad': 'media',
                'elementos_culturales': ['resultados', 'sucesso', 'garantido']
            },
            'ru': {
                'tono': 'autoritario',
                'urgencia': 'moderada',
                'formalidad': 'alta',
                'elementos_culturales': ['результаты', 'успех', 'гарантировано']
            },
            'ja': {
                'tono': 'respetuoso',
                'urgencia': 'baja',
                'formalidad': 'muy alta',
                'elementos_culturales': ['結果', '成功', '保証']
            },
            'ko': {
                'tono': 'dinámico',
                'urgencia': 'alta',
                'formalidad': 'media',
                'elementos_culturales': ['결과', '성공', '보장']
            },
            'zh': {
                'tono': 'directo',
                'urgencia': 'alta',
                'formalidad': 'media',
                'elementos_culturales': ['结果', '成功', '保证']
            },
            'ar': {
                'tono': 'formal',
                'urgencia': 'moderada',
                'formalidad': 'alta',
                'elementos_culturales': ['النتائج', 'النجاح', 'مضمون']
            }
        }

    def generar_anchor_texts_idioma(self, idioma: str, cantidad: int = 20) -> List[Dict[str, Any]]:
        """Genera anchor texts en un idioma específico"""
        if idioma not in self.idiomas:
            raise ValueError(f"Idioma '{idioma}' no soportado")
        
        config_idioma = self.idiomas[idioma]
        adaptacion_cultural = self.adaptaciones_culturales[idioma]
        
        anchor_texts = []
        
        for i in range(cantidad):
            # Seleccionar palabra clave
            palabra_clave = random.choice(config_idioma['palabras_clave'])
            
            # Seleccionar plantilla
            plantilla = random.choice(config_idioma['plantillas'])
            
            # Seleccionar elementos
            beneficio = random.choice(config_idioma['beneficios'])
            tiempo = random.choice(config_idioma['tiempos'])
            garantia = random.choice(config_idioma['garantias'])
            modalidad = random.choice(config_idioma['modalidades'])
            año = '2024'
            
            # Generar anchor text
            anchor_text = plantilla.replace('{palabra_clave}', palabra_clave)
            anchor_text = anchor_text.replace('{beneficio}', beneficio)
            anchor_text = anchor_text.replace('{tiempo}', tiempo)
            anchor_text = anchor_text.replace('{garantia}', garantia)
            anchor_text = anchor_text.replace('{modalidad}', modalidad)
            anchor_text = anchor_text.replace('{año}', año)
            
            # Aplicar adaptación cultural
            anchor_text_adaptado = self._aplicar_adaptacion_cultural(anchor_text, adaptacion_cultural)
            
            # Analizar características
            caracteristicas = self._analizar_caracteristicas_idioma(
                anchor_text_adaptado, idioma, adaptacion_cultural
            )
            
            anchor_texts.append({
                'id': f"{idioma}_{i+1:03d}",
                'anchor_text': anchor_text_adaptado,
                'idioma': idioma,
                'region': config_idioma['region'],
                'palabra_clave': palabra_clave,
                'caracteristicas': caracteristicas,
                'fecha_generacion': datetime.now().isoformat()
            })
        
        return anchor_texts

    def _aplicar_adaptacion_cultural(self, anchor_text: str, adaptacion: Dict[str, Any]) -> str:
        """Aplica adaptación cultural al anchor text"""
        # Aplicar tono
        if adaptacion['tono'] == 'elegante' and 'fantástico' in anchor_text.lower():
            anchor_text = anchor_text.replace('fantástico', 'exquisito')
        elif adaptacion['tono'] == 'técnico' and 'increíble' in anchor_text.lower():
            anchor_text = anchor_text.replace('increíble', 'avanzado')
        
        # Aplicar urgencia
        if adaptacion['urgencia'] == 'alta' and 'ahora' not in anchor_text.lower():
            anchor_text += ' - ¡Ahora!'
        elif adaptacion['urgencia'] == 'baja' and 'ahora' in anchor_text.lower():
            anchor_text = anchor_text.replace(' - ¡Ahora!', '')
        
        # Aplicar formalidad
        if adaptacion['formalidad'] == 'alta':
            anchor_text = anchor_text.replace('!', '.')
        elif adaptacion['formalidad'] == 'baja':
            anchor_text = anchor_text.replace('.', '!')
        
        return anchor_text

    def _analizar_caracteristicas_idioma(self, anchor_text: str, idioma: str, 
                                       adaptacion: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza las características del anchor text en el idioma específico"""
        return {
            'longitud': len(anchor_text),
            'idioma': idioma,
            'tono': adaptacion['tono'],
            'urgencia': adaptacion['urgencia'],
            'formalidad': adaptacion['formalidad'],
            'elementos_culturales': adaptacion['elementos_culturales'],
            'score_adaptacion': self._calcular_score_adaptacion(anchor_text, adaptacion)
        }

    def _calcular_score_adaptacion(self, anchor_text: str, adaptacion: Dict[str, Any]) -> float:
        """Calcula el score de adaptación cultural"""
        score = 50  # Base
        
        # Ajustar por longitud (óptimo 30-60 caracteres)
        longitud = len(anchor_text)
        if 30 <= longitud <= 60:
            score += 20
        elif 20 <= longitud < 30 or 60 < longitud <= 80:
            score += 10
        
        # Ajustar por elementos culturales
        elementos_presentes = sum(1 for elemento in adaptacion['elementos_culturales'] 
                                if elemento.lower() in anchor_text.lower())
        score += elementos_presentes * 10
        
        # Ajustar por urgencia
        if adaptacion['urgencia'] == 'alta' and any(palabra in anchor_text.lower() 
                                                   for palabra in ['ahora', 'urgente', 'hoy']):
            score += 15
        elif adaptacion['urgencia'] == 'baja' and not any(palabra in anchor_text.lower() 
                                                         for palabra in ['ahora', 'urgente', 'hoy']):
            score += 15
        
        return min(100, max(0, score))

    def generar_anchor_texts_multilenguaje(self, idiomas: List[str] = None, 
                                         cantidad_por_idioma: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Genera anchor texts en múltiples idiomas"""
        if idiomas is None:
            idiomas = list(self.idiomas.keys())
        
        resultados = {}
        
        for idioma in idiomas:
            if idioma in self.idiomas:
                print(f"Generando anchor texts en {self.idiomas[idioma]['nombre']}...")
                anchor_texts = self.generar_anchor_texts_idioma(idioma, cantidad_por_idioma)
                resultados[idioma] = anchor_texts
        
        return resultados

    def analizar_tendencias_por_idioma(self, idioma: str) -> Dict[str, Any]:
        """Analiza tendencias específicas por idioma"""
        if idioma not in self.idiomas:
            raise ValueError(f"Idioma '{idioma}' no soportado")
        
        config_idioma = self.idiomas[idioma]
        adaptacion = self.adaptaciones_culturales[idioma]
        
        # Simular análisis de tendencias
        tendencias = {
            'palabras_trending': random.sample(config_idioma['beneficios'], 3),
            'tono_preferido': adaptacion['tono'],
            'urgencia_optima': adaptacion['urgencia'],
            'formalidad_optima': adaptacion['formalidad'],
            'elementos_culturales_activos': adaptacion['elementos_culturales'],
            'score_adaptacion_promedio': random.uniform(70, 90)
        }
        
        return {
            'idioma': idioma,
            'region': config_idioma['region'],
            'fecha_analisis': datetime.now().isoformat(),
            'tendencias': tendencias,
            'recomendaciones': self._generar_recomendaciones_idioma(idioma, tendencias)
        }

    def _generar_recomendaciones_idioma(self, idioma: str, tendencias: Dict[str, Any]) -> List[Dict[str, str]]:
        """Genera recomendaciones específicas por idioma"""
        recomendaciones = []
        
        config_idioma = self.idiomas[idioma]
        
        recomendaciones.append({
            'categoria': 'cultural',
            'prioridad': 'Alta',
            'recomendacion': f'Adapta el contenido a la cultura de {config_idioma["region"]}',
            'accion': f'Usa tono {tendencias["tono_preferido"]} y formalidad {tendencias["formalidad_optima"]}'
        })
        
        recomendaciones.append({
            'categoria': 'lingüística',
            'prioridad': 'Media',
            'recomendacion': f'Optimiza para el mercado {idioma}',
            'accion': f'Incluye palabras trending: {", ".join(tendencias["palabras_trending"])}'
        })
        
        if tendencias['urgencia_optima'] == 'alta':
            recomendaciones.append({
                'categoria': 'urgencia',
                'prioridad': 'Media',
                'recomendacion': 'El mercado responde bien a la urgencia',
                'accion': 'Incluye elementos de urgencia en tus anchor texts'
            })
        
        return recomendaciones

    def exportar_multilenguaje(self, resultados: Dict[str, List[Dict[str, Any]]], 
                             formato: str = "json") -> str:
        """Exporta los resultados multilenguaje"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"anchor_texts_multilenguaje_{timestamp}"
        
        if formato == "json":
            filename = f"{base_filename}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=4)
            return filename
        elif formato == "txt":
            filename = f"{base_filename}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"--- ANCHOR TEXTS MULTILENGUAJE - IA MARKETING ---\n")
                f.write(f"Fecha: {datetime.now().isoformat()}\n\n")
                
                for idioma, anchor_texts in resultados.items():
                    config = self.idiomas[idioma]
                    f.write(f"IDIOMA: {config['nombre']} ({config['region']})\n")
                    f.write(f"Total anchor texts: {len(anchor_texts)}\n\n")
                    
                    for i, at in enumerate(anchor_texts[:5], 1):  # Mostrar solo los primeros 5
                        f.write(f"{i}. {at['anchor_text']}\n")
                        f.write(f"   Score: {at['caracteristicas']['score_adaptacion']}/100\n")
                        f.write(f"   Tono: {at['caracteristicas']['tono']}\n\n")
                    
                    f.write("-" * 50 + "\n\n")
            
            return filename
        else:
            raise ValueError("Formato no soportado. Use 'json' o 'txt'.")

def main():
    generador = GeneradorMultilenguajeAnchorTexts()
    
    print("🌍 GENERADOR MULTILENGUAJE - ANCHOR TEXTS IA MARKETING")
    print("====================================================\n")
    
    # Seleccionar idiomas para generar
    idiomas_seleccionados = ['es', 'en', 'fr', 'de', 'pt']
    
    print(f"🔄 Generando anchor texts en {len(idiomas_seleccionados)} idiomas...")
    print(f"Idiomas: {', '.join([generador.idiomas[idioma]['nombre'] for idioma in idiomas_seleccionados])}\n")
    
    resultados = generador.generar_anchor_texts_multilenguaje(idiomas_seleccionados, 15)
    
    print("🔄 Analizando tendencias por idioma...\n")
    tendencias_por_idioma = {}
    for idioma in idiomas_seleccionados:
        tendencias = generador.analizar_tendencias_por_idioma(idioma)
        tendencias_por_idioma[idioma] = tendencias
        print(f"• {generador.idiomas[idioma]['nombre']}: Score {tendencias['tendencias']['score_adaptacion_promedio']:.1f}/100")
    
    print("\n💾 Exportando resultados...")
    json_file = generador.exportar_multilenguaje(resultados, "json")
    txt_file = generador.exportar_multilenguaje(resultados, "txt")
    
    print("\n✅ Generación completada:")
    total_anchor_texts = sum(len(anchor_texts) for anchor_texts in resultados.values())
    print(f"   • Total anchor texts generados: {total_anchor_texts}")
    print(f"   • Idiomas procesados: {len(idiomas_seleccionados)}")
    
    print(f"\n📊 ESTADÍSTICAS POR IDIOMA:")
    for idioma, anchor_texts in resultados.items():
        config = generador.idiomas[idioma]
        scores = [at['caracteristicas']['score_adaptacion'] for at in anchor_texts]
        score_promedio = sum(scores) / len(scores) if scores else 0
        print(f"   • {config['nombre']}: {len(anchor_texts)} textos, score promedio {score_promedio:.1f}/100")
    
    print(f"\n📁 Archivos generados:")
    print(f"   • JSON: {json_file}")
    print(f"   • TXT: {txt_file}")
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print("1. Revisa los anchor texts generados por idioma")
    print("2. Analiza las tendencias específicas de cada mercado")
    print("3. Implementa los anchor texts en las campañas locales")
    print("4. Monitorea el rendimiento por idioma y región")
    print("5. Ajusta la estrategia según los resultados locales")

if __name__ == "__main__":
    main()