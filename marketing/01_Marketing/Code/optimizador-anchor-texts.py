#!/usr/bin/env python3
"""
Optimizador Avanzado de Anchor Texts IA Marketing
Analiza, optimiza y mejora automáticamente los anchor texts existentes
"""

import json
import random
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
import os

class OptimizadorAnchorTexts:
    def __init__(self):
        self.anchor_texts = self.cargar_anchor_texts()
        self.metricas_objetivo = {
            'ctr_min': 3.0,
            'ctr_max': 8.0,
            'conversion_min': 8.0,
            'conversion_max': 15.0,
            'longitud_optima': (20, 60),
            'palabras_clave_min': 2,
            'palabras_clave_max': 5
        }
        
        self.palabras_poder = [
            'gratis', 'exclusivo', 'limitado', 'urgente', 'ahora', 'ya',
            'revoluciona', 'domina', 'triunfa', 'conquista', 'supera',
            'garantizado', 'comprobado', 'efectivo', 'exitoso', 'probado'
        ]
        
        self.industrias = [
            'E-commerce', 'Salud', 'Inmobiliaria', 'Educación', 'Servicios Profesionales',
            'Restaurantes', 'Fitness', 'Tecnología', 'Finanzas', 'Consultoría'
        ]
        
        self.tonos = [
            'Urgente', 'Premium', 'Educativo', 'Motivacional', 'Técnico', 'Emocional',
            'Profesional', 'Casual', 'Formal', 'Innovador', 'Tradicional', 'Moderno'
        ]

    def cargar_anchor_texts(self) -> List[str]:
        """Carga anchor texts desde archivos existentes"""
        return [
            "Curso IA Marketing [Tu Marca] - Certificación Oficial",
            "Domina el Marketing con IA en 30 Días",
            "Multiplica tus Ventas con IA Marketing",
            "Masterclass IA Marketing 2024",
            "IA Marketing para Principiantes: Desde Cero",
            "¿Cansado de luchar solo? IA Marketing que convierte - Soluciónate HOY",
            "¡Últimas Plazas! IA Marketing que triunfa - No te quedes fuera",
            "Ex-VP Google - IA Marketing que funciona - $1B+ generados",
            "50,000+ empresas confían en IA Marketing - Aumentan ventas 500%",
            "De 0 a 100 clientes - IA Marketing en 30 días - Historia real"
        ]

    def analizar_anchor_text(self, text: str) -> Dict[str, Any]:
        """Analiza un anchor text y devuelve métricas detalladas"""
        analisis = {
            'texto_original': text,
            'longitud': len(text),
            'palabras': len(text.split()),
            'palabras_poder': self.contar_palabras_poder(text),
            'palabras_clave': self.extraer_palabras_clave(text),
            'tono_detectado': self.detectar_tono(text),
            'industria_detectada': self.detectar_industria(text),
            'puntuacion_urgencia': self.calcular_urgencia(text),
            'puntuacion_beneficio': self.calcular_beneficio(text),
            'puntuacion_autoridad': self.calcular_autoridad(text),
            'puntuacion_total': 0,
            'recomendaciones': []
        }
        
        # Calcular puntuación total
        analisis['puntuacion_total'] = self.calcular_puntuacion_total(analisis)
        
        # Generar recomendaciones
        analisis['recomendaciones'] = self.generar_recomendaciones(analisis)
        
        return analisis

    def contar_palabras_poder(self, text: str) -> int:
        """Cuenta las palabras de poder en el texto"""
        text_lower = text.lower()
        return sum(1 for palabra in self.palabras_poder if palabra in text_lower)

    def extraer_palabras_clave(self, text: str) -> List[str]:
        """Extrae palabras clave relevantes del texto"""
        palabras_clave = []
        text_lower = text.lower()
        
        # Palabras clave de IA Marketing
        keywords_ia = ['ia marketing', 'inteligencia artificial', 'marketing digital', 'automatización']
        for keyword in keywords_ia:
            if keyword in text_lower:
                palabras_clave.append(keyword)
        
        # Palabras clave de acción
        keywords_accion = ['domina', 'aprende', 'descubre', 'conquista', 'triunfa', 'supera']
        for keyword in keywords_accion:
            if keyword in text_lower:
                palabras_clave.append(keyword)
        
        return palabras_clave

    def detectar_tono(self, text: str) -> str:
        """Detecta el tono del anchor text"""
        text_lower = text.lower()
        
        if any(palabra in text_lower for palabra in ['¡', 'urgente', 'ahora', 'ya', 'última']):
            return 'Urgente'
        elif any(palabra in text_lower for palabra in ['exclusivo', 'premium', 'elite', 'vip']):
            return 'Premium'
        elif any(palabra in text_lower for palabra in ['aprende', 'descubre', 'conoce', 'entiende']):
            return 'Educativo'
        elif any(palabra in text_lower for palabra in ['supera', 'conquista', 'triunfa', 'domina']):
            return 'Motivacional'
        elif any(palabra in text_lower for palabra in ['optimiza', 'automatiza', 'análisis', 'datos']):
            return 'Técnico'
        elif any(palabra in text_lower for palabra in ['¿', 'cansado', 'frustrado', 'sueñas']):
            return 'Emocional'
        else:
            return 'Neutral'

    def detectar_industria(self, text: str) -> str:
        """Detecta la industria del anchor text"""
        text_lower = text.lower()
        
        industria_keywords = {
            'E-commerce': ['e-commerce', 'tienda online', 'ventas online'],
            'Salud': ['salud', 'médico', 'clínica', 'hospital'],
            'Inmobiliaria': ['inmobiliaria', 'propiedad', 'casa', 'vivienda'],
            'Educación': ['educación', 'curso', 'aprende', 'estudia'],
            'Servicios Profesionales': ['abogado', 'consultor', 'contador', 'profesional']
        }
        
        for industria, keywords in industria_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return industria
        
        return 'General'

    def calcular_urgencia(self, text: str) -> float:
        """Calcula la puntuación de urgencia (0-10)"""
        text_lower = text.lower()
        urgencia_keywords = ['¡', 'urgente', 'ahora', 'ya', 'última', 'limitado', 'solo']
        puntuacion = sum(2 for keyword in urgencia_keywords if keyword in text_lower)
        return min(puntuacion, 10.0)

    def calcular_beneficio(self, text: str) -> float:
        """Calcula la puntuación de beneficio (0-10)"""
        text_lower = text.lower()
        beneficio_keywords = ['aumenta', 'multiplica', 'mejora', 'optimiza', 'maximiza', 'incrementa']
        puntuacion = sum(1.5 for keyword in beneficio_keywords if keyword in text_lower)
        return min(puntuacion, 10.0)

    def calcular_autoridad(self, text: str) -> float:
        """Calcula la puntuación de autoridad (0-10)"""
        text_lower = text.lower()
        autoridad_keywords = ['ex-', 'ceo', 'director', 'profesor', 'doctor', 'experto', 'master']
        puntuacion = sum(2 for keyword in autoridad_keywords if keyword in text_lower)
        return min(puntuacion, 10.0)

    def calcular_puntuacion_total(self, analisis: Dict[str, Any]) -> float:
        """Calcula la puntuación total del anchor text (0-100)"""
        puntuacion = 0
        
        # Longitud óptima (20 puntos)
        longitud = analisis['longitud']
        if self.metricas_objetivo['longitud_optima'][0] <= longitud <= self.metricas_objetivo['longitud_optima'][1]:
            puntuacion += 20
        else:
            puntuacion += max(0, 20 - abs(longitud - 40) * 0.5)
        
        # Palabras de poder (20 puntos)
        palabras_poder = analisis['palabras_poder']
        puntuacion += min(palabras_poder * 5, 20)
        
        # Palabras clave (20 puntos)
        palabras_clave = len(analisis['palabras_clave'])
        puntuacion += min(palabras_clave * 4, 20)
        
        # Urgencia (15 puntos)
        puntuacion += analisis['puntuacion_urgencia'] * 1.5
        
        # Beneficio (15 puntos)
        puntuacion += analisis['puntuacion_beneficio'] * 1.5
        
        # Autoridad (10 puntos)
        puntuacion += analisis['puntuacion_autoridad']
        
        return min(puntuacion, 100.0)

    def generar_recomendaciones(self, analisis: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones de mejora para el anchor text"""
        recomendaciones = []
        
        # Longitud
        if analisis['longitud'] < self.metricas_objetivo['longitud_optima'][0]:
            recomendaciones.append("Considera agregar más detalles para aumentar la longitud")
        elif analisis['longitud'] > self.metricas_objetivo['longitud_optima'][1]:
            recomendaciones.append("Considera acortar el texto para mejor legibilidad")
        
        # Palabras de poder
        if analisis['palabras_poder'] < 2:
            recomendaciones.append("Agrega más palabras de poder para aumentar el impacto")
        
        # Palabras clave
        if len(analisis['palabras_clave']) < 2:
            recomendaciones.append("Incluye más palabras clave relevantes")
        
        # Urgencia
        if analisis['puntuacion_urgencia'] < 5:
            recomendaciones.append("Considera agregar elementos de urgencia")
        
        # Beneficio
        if analisis['puntuacion_beneficio'] < 5:
            recomendaciones.append("Incluye más beneficios específicos")
        
        # Autoridad
        if analisis['puntuacion_autoridad'] < 3:
            recomendaciones.append("Considera agregar elementos de autoridad o credibilidad")
        
        return recomendaciones

    def optimizar_anchor_text(self, text: str) -> str:
        """Optimiza un anchor text basándose en el análisis"""
        analisis = self.analizar_anchor_text(text)
        
        # Si la puntuación es alta, no modificar mucho
        if analisis['puntuacion_total'] > 80:
            return text
        
        texto_optimizado = text
        
        # Agregar palabras de poder si faltan
        if analisis['palabras_poder'] < 2:
            palabras_agregar = random.sample(self.palabras_poder, 1)
            if 'gratis' in palabras_agregar:
                texto_optimizado = f"Gratis: {texto_optimizado}"
            elif 'exclusivo' in palabras_agregar:
                texto_optimizado = f"Exclusivo: {texto_optimizado}"
        
        # Agregar urgencia si falta
        if analisis['puntuacion_urgencia'] < 5:
            urgencia_phrases = ["¡Última oportunidad!", "Solo por tiempo limitado", "¡No te quedes fuera!"]
            texto_optimizado = f"{random.choice(urgencia_phrases)} {texto_optimizado}"
        
        # Agregar beneficio si falta
        if analisis['puntuacion_beneficio'] < 5:
            beneficio_phrases = ["- Aumenta ventas 300%", "- Resultados garantizados", "- Sin riesgo"]
            texto_optimizado = f"{texto_optimizado} {random.choice(beneficio_phrases)}"
        
        return texto_optimizado

    def generar_variantes_optimizadas(self, text: str, cantidad: int = 5) -> List[str]:
        """Genera variantes optimizadas de un anchor text"""
        variantes = [text]
        
        for _ in range(cantidad - 1):
            variante = self.optimizar_anchor_text(text)
            if variante not in variantes:
                variantes.append(variante)
        
        return variantes

    def analizar_lote(self, textos: List[str]) -> Dict[str, Any]:
        """Analiza un lote de anchor texts"""
        resultados = {
            'total_textos': len(textos),
            'analisis_individual': [],
            'estadisticas_generales': {},
            'top_performers': [],
            'necesitan_mejora': [],
            'recomendaciones_generales': []
        }
        
        # Analizar cada texto
        for texto in textos:
            analisis = self.analizar_anchor_text(texto)
            resultados['analisis_individual'].append(analisis)
        
        # Calcular estadísticas generales
        puntuaciones = [a['puntuacion_total'] for a in resultados['analisis_individual']]
        resultados['estadisticas_generales'] = {
            'puntuacion_promedio': sum(puntuaciones) / len(puntuaciones),
            'puntuacion_maxima': max(puntuaciones),
            'puntuacion_minima': min(puntuaciones),
            'textos_optimizados': len([p for p in puntuaciones if p > 80]),
            'textos_mejora': len([p for p in puntuaciones if p < 60])
        }
        
        # Identificar top performers
        resultados['top_performers'] = sorted(
            resultados['analisis_individual'],
            key=lambda x: x['puntuacion_total'],
            reverse=True
        )[:3]
        
        # Identificar textos que necesitan mejora
        resultados['necesitan_mejora'] = [
            a for a in resultados['analisis_individual']
            if a['puntuacion_total'] < 60
        ]
        
        # Generar recomendaciones generales
        resultados['recomendaciones_generales'] = self.generar_recomendaciones_generales(resultados)
        
        return resultados

    def generar_recomendaciones_generales(self, resultados: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones generales para el lote"""
        recomendaciones = []
        stats = resultados['estadisticas_generales']
        total_textos = resultados['total_textos']
        
        if stats['puntuacion_promedio'] < 70:
            recomendaciones.append("La puntuación promedio es baja. Considera optimizar la mayoría de los textos")
        
        if stats['textos_mejora'] > total_textos * 0.5:
            recomendaciones.append("Más del 50% de los textos necesitan mejora. Revisa las recomendaciones individuales")
        
        if stats['puntuacion_maxima'] - stats['puntuacion_minima'] > 40:
            recomendaciones.append("Hay mucha variación en la calidad. Estandariza el nivel de los textos")
        
        return recomendaciones

    def exportar_analisis(self, resultados: Dict[str, Any], formato: str = "json") -> str:
        """Exporta el análisis en diferentes formatos"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if formato == "json":
            filename = f"analisis_anchor_texts_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
        
        elif formato == "txt":
            filename = f"analisis_anchor_texts_{timestamp}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("ANÁLISIS DE ANCHOR TEXTS IA MARKETING\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"Total de textos analizados: {resultados['total_textos']}\n")
                f.write(f"Puntuación promedio: {resultados['estadisticas_generales']['puntuacion_promedio']:.1f}\n")
                f.write(f"Textos optimizados: {resultados['estadisticas_generales']['textos_optimizados']}\n")
                f.write(f"Textos que necesitan mejora: {resultados['estadisticas_generales']['textos_mejora']}\n\n")
                
                f.write("TOP PERFORMERS:\n")
                f.write("-" * 30 + "\n")
                for i, texto in enumerate(resultados['top_performers'], 1):
                    f.write(f"{i}. {texto['texto_original']} (Puntuación: {texto['puntuacion_total']:.1f})\n")
                
                f.write("\nRECOMENDACIONES GENERALES:\n")
                f.write("-" * 30 + "\n")
                for rec in resultados['recomendaciones_generales']:
                    f.write(f"• {rec}\n")
        
        return filename

    def optimizar_lote_completo(self, textos: List[str]) -> Dict[str, Any]:
        """Optimiza un lote completo de anchor texts"""
        print("🔍 ANALIZANDO ANCHOR TEXTS...")
        analisis = self.analizar_lote(textos)
        
        print("⚡ OPTIMIZANDO TEXTOS...")
        textos_optimizados = []
        for texto in textos:
            variantes = self.generar_variantes_optimizadas(texto, 3)
            textos_optimizados.extend(variantes)
        
        print("📊 GENERANDO REPORTE...")
        reporte = {
            'analisis_original': analisis,
            'textos_optimizados': textos_optimizados,
            'mejoras_aplicadas': len(textos_optimizados) - len(textos),
            'timestamp': datetime.now().isoformat()
        }
        
        return reporte

def main():
    """Función principal"""
    print("🚀 OPTIMIZADOR AVANZADO DE ANCHOR TEXTS IA MARKETING")
    print("=" * 60)
    
    optimizador = OptimizadorAnchorTexts()
    
    # Analizar anchor texts existentes
    print("🔄 Analizando anchor texts existentes...")
    analisis = optimizador.analizar_lote(optimizador.anchor_texts)
    
    print(f"✅ Análisis completado:")
    print(f"   • Total de textos: {analisis['total_textos']}")
    print(f"   • Puntuación promedio: {analisis['estadisticas_generales']['puntuacion_promedio']:.1f}")
    print(f"   • Textos optimizados: {analisis['estadisticas_generales']['textos_optimizados']}")
    print(f"   • Necesitan mejora: {analisis['estadisticas_generales']['textos_mejora']}")
    
    # Optimizar lote completo
    print("\n🔄 Optimizando lote completo...")
    reporte = optimizador.optimizar_lote_completo(optimizador.anchor_texts)
    
    print(f"✅ Optimización completada:")
    print(f"   • Textos originales: {len(optimizador.anchor_texts)}")
    print(f"   • Textos optimizados: {len(reporte['textos_optimizados'])}")
    print(f"   • Mejoras aplicadas: {reporte['mejoras_aplicadas']}")
    
    # Exportar resultados
    print("\n📁 Exportando resultados...")
    json_file = optimizador.exportar_analisis(analisis, "json")
    txt_file = optimizador.exportar_analisis(analisis, "txt")
    
    print(f"✅ Archivos exportados:")
    print(f"   • JSON: {json_file}")
    print(f"   • TXT: {txt_file}")
    
    # Mostrar ejemplos de optimización
    print("\n🎯 EJEMPLOS DE OPTIMIZACIÓN:")
    print("-" * 40)
    
    for i, texto in enumerate(optimizador.anchor_texts[:3], 1):
        print(f"\n{i}. ORIGINAL: {texto}")
        analisis_individual = optimizador.analizar_anchor_text(texto)
        print(f"   Puntuación: {analisis_individual['puntuacion_total']:.1f}/100")
        
        optimizado = optimizador.optimizar_anchor_text(texto)
        print(f"   OPTIMIZADO: {optimizado}")
        
        if analisis_individual['recomendaciones']:
            print(f"   Recomendaciones: {', '.join(analisis_individual['recomendaciones'][:2])}")
    
    print("\n🎉 ¡Optimización completada exitosamente!")
    print("\n💡 Próximos pasos:")
    print("1. Revisa el análisis detallado en los archivos exportados")
    print("2. Implementa los textos optimizados en tu estrategia")
    print("3. Monitorea el rendimiento de las mejoras")
    print("4. Usa las recomendaciones para futuros anchor texts")

if __name__ == "__main__":
    main()
