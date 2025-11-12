#!/usr/bin/env python3
"""
Análisis de Engagement de Contenido
====================================
Analiza publicaciones del último mes y sugiere qué tipo de contenido
obtuvo más engagement y por qué, además de recomendar nuevas ideas.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict
from dataclasses import dataclass, asdict
import statistics


@dataclass
class Publicacion:
    """Estructura de una publicación."""
    id: str
    tipo_contenido: str  # X, Y, Z u otros tipos
    titulo: str
    plataforma: str
    fecha_publicacion: datetime
    likes: int
    comentarios: int
    shares: int
    impresiones: int
    reach: int
    hashtags: List[str]
    tiene_media: bool
    duracion_video: int = 0  # segundos, 0 si no es video
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def engagement_total(self) -> int:
        """Calcula el engagement total."""
        return self.likes + self.comentarios + self.shares
    
    @property
    def engagement_rate(self) -> float:
        """Calcula la tasa de engagement."""
        if self.impresiones == 0:
            return 0.0
        return (self.engagement_total / self.impresiones) * 100
    
    @property
    def engagement_score(self) -> float:
        """Score ponderado de engagement."""
        # Ponderación: likes (1x), comentarios (3x), shares (5x)
        return self.likes + (self.comentarios * 3) + (self.shares * 5)


class AnalizadorEngagement:
    """Analizador de engagement de contenido."""
    
    def __init__(self):
        self.publicaciones: List[Publicacion] = []
    
    def generar_datos_ejemplo(self, num_publicaciones: int = 30):
        """
        Genera datos de ejemplo simulando publicaciones del último mes.
        Tipos de contenido:
        - X: Tutoriales/Educativos (alto engagement esperado)
        - Y: Entretenimiento/Viral (engagement medio-alto)
        - Z: Promocional/Producto (engagement bajo-medio)
        """
        tipos_contenido = {
            'X': {
                'nombre': 'Tutoriales/Educativos',
                'prob_alto_engagement': 0.7,
                'hashtags_tipicos': ['#tutorial', '#aprende', '#educacion', '#tips'],
                'tiene_media_prob': 0.9,
                'duracion_promedio': 180
            },
            'Y': {
                'nombre': 'Entretenimiento/Viral',
                'prob_alto_engagement': 0.5,
                'hashtags_tipicos': ['#viral', '#entretenimiento', '#diversion', '#trending'],
                'tiene_media_prob': 0.95,
                'duracion_promedio': 60
            },
            'Z': {
                'nombre': 'Promocional/Producto',
                'prob_alto_engagement': 0.3,
                'hashtags_tipicos': ['#producto', '#oferta', '#nuevo', '#promocion'],
                'tiene_media_prob': 0.8,
                'duracion_promedio': 30
            }
        }
        
        plataformas = ['Instagram', 'LinkedIn', 'Twitter', 'Facebook', 'TikTok']
        fecha_inicio = datetime.now() - timedelta(days=30)
        
        for i in range(num_publicaciones):
            # Distribución: 40% X, 35% Y, 25% Z
            tipo_key = random.choices(
                ['X', 'Y', 'Z'],
                weights=[40, 35, 25]
            )[0]
            
            tipo_info = tipos_contenido[tipo_key]
            
            # Generar fecha aleatoria en el último mes
            dias_aleatorios = random.randint(0, 30)
            fecha = fecha_inicio + timedelta(days=dias_aleatorios)
            
            # Generar métricas según el tipo de contenido
            base_impresiones = random.randint(500, 5000)
            base_reach = int(base_impresiones * random.uniform(0.6, 0.9))
            
            # Engagement varía según tipo
            if tipo_key == 'X':  # Tutoriales tienen mejor engagement
                factor_engagement = random.uniform(0.08, 0.15)
                likes_base = int(base_impresiones * factor_engagement * random.uniform(0.7, 1.3))
                comentarios_base = int(likes_base * random.uniform(0.15, 0.25))
                shares_base = int(likes_base * random.uniform(0.10, 0.20))
            elif tipo_key == 'Y':  # Entretenimiento tiene engagement medio-alto
                factor_engagement = random.uniform(0.05, 0.12)
                likes_base = int(base_impresiones * factor_engagement * random.uniform(0.6, 1.2))
                comentarios_base = int(likes_base * random.uniform(0.10, 0.18))
                shares_base = int(likes_base * random.uniform(0.08, 0.15))
            else:  # Z: Promocional tiene engagement más bajo
                factor_engagement = random.uniform(0.02, 0.08)
                likes_base = int(base_impresiones * factor_engagement * random.uniform(0.5, 1.0))
                comentarios_base = int(likes_base * random.uniform(0.05, 0.12))
                shares_base = int(likes_base * random.uniform(0.03, 0.10))
            
            # Añadir variabilidad
            likes = max(0, int(likes_base + random.randint(-50, 50)))
            comentarios = max(0, int(comentarios_base + random.randint(-10, 10)))
            shares = max(0, int(shares_base + random.randint(-5, 5)))
            
            # Generar hashtags
            num_hashtags = random.randint(3, 7)
            hashtags = random.sample(tipo_info['hashtags_tipicos'], 
                                    min(num_hashtags, len(tipo_info['hashtags_tipicos'])))
            
            # Generar título según tipo
            titulos = {
                'X': [
                    f"Cómo hacer {random.choice(['X', 'Y', 'Z'])} en 5 pasos",
                    f"Tutorial completo: {random.choice(['Guía', 'Método', 'Técnica'])}",
                    f"5 tips para mejorar tu {random.choice(['productividad', 'habilidad', 'resultado'])}",
                    f"Aprende {random.choice(['esto', 'aquello'])} en minutos"
                ],
                'Y': [
                    f"Esto te va a {random.choice(['sorprender', 'encantar', 'divertir'])}",
                    f"Viral: {random.choice(['Momento', 'Situación', 'Historia'])} increíble",
                    f"No vas a creer lo que pasó",
                    f"Trending: {random.choice(['Lo último', 'Lo nuevo', 'Lo mejor'])}"
                ],
                'Z': [
                    f"Nuevo producto disponible",
                    f"Oferta especial: {random.randint(10, 50)}% descuento",
                    f"Descubre nuestra {random.choice(['novedad', 'oferta', 'promoción'])}",
                    f"Lanzamiento: {random.choice(['Producto', 'Servicio', 'Solución'])}"
                ]
            }
            
            publicacion = Publicacion(
                id=f"post_{i+1:03d}",
                tipo_contenido=tipo_key,
                titulo=random.choice(titulos[tipo_key]),
                plataforma=random.choice(plataformas),
                fecha_publicacion=fecha,
                likes=likes,
                comentarios=comentarios,
                shares=shares,
                impresiones=base_impresiones,
                reach=base_reach,
                hashtags=hashtags,
                tiene_media=random.random() < tipo_info['tiene_media_prob'],
                duracion_video=random.randint(15, tipo_info['duracion_promedio']) if tipo_info['tiene_media_prob'] > 0.5 else 0,
                metadata={
                    'tipo_nombre': tipo_info['nombre'],
                    'hora_publicacion': fecha.hour,
                    'dia_semana': fecha.strftime('%A')
                }
            )
            
            self.publicaciones.append(publicacion)
    
    def analizar_por_tipo(self) -> Dict[str, Any]:
        """Analiza el engagement por tipo de contenido."""
        analisis = defaultdict(lambda: {
            'publicaciones': [],
            'total_likes': 0,
            'total_comentarios': 0,
            'total_shares': 0,
            'total_impresiones': 0,
            'total_reach': 0,
            'engagement_scores': [],
            'engagement_rates': [],
            'plataformas': defaultdict(int),
            'con_media': 0,
            'sin_media': 0
        })
        
        for pub in self.publicaciones:
            tipo = pub.tipo_contenido
            analisis[tipo]['publicaciones'].append(pub)
            analisis[tipo]['total_likes'] += pub.likes
            analisis[tipo]['total_comentarios'] += pub.comentarios
            analisis[tipo]['total_shares'] += pub.shares
            analisis[tipo]['total_impresiones'] += pub.impresiones
            analisis[tipo]['total_reach'] += pub.reach
            analisis[tipo]['engagement_scores'].append(pub.engagement_score)
            analisis[tipo]['engagement_rates'].append(pub.engagement_rate)
            analisis[tipo]['plataformas'][pub.plataforma] += 1
            
            if pub.tiene_media:
                analisis[tipo]['con_media'] += 1
            else:
                analisis[tipo]['sin_media'] += 1
        
        # Calcular promedios y estadísticas
        resultado = {}
        for tipo, datos in analisis.items():
            num_pubs = len(datos['publicaciones'])
            if num_pubs == 0:
                continue
            
            total_engagement = datos['total_likes'] + datos['total_comentarios'] + datos['total_shares']
            
            resultado[tipo] = {
                'nombre': datos['publicaciones'][0].metadata.get('tipo_nombre', tipo),
                'cantidad_publicaciones': num_pubs,
                'engagement_total': total_engagement,
                'engagement_promedio': total_engagement / num_pubs,
                'engagement_score_promedio': statistics.mean(datos['engagement_scores']),
                'engagement_rate_promedio': statistics.mean(datos['engagement_rates']),
                'likes_promedio': datos['total_likes'] / num_pubs,
                'comentarios_promedio': datos['total_comentarios'] / num_pubs,
                'shares_promedio': datos['total_shares'] / num_pubs,
                'impresiones_promedio': datos['total_impresiones'] / num_pubs,
                'reach_promedio': datos['total_reach'] / num_pubs,
                'porcentaje_con_media': (datos['con_media'] / num_pubs) * 100,
                'plataformas_mas_usadas': dict(sorted(
                    datos['plataformas'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )),
                'mejor_publicacion': max(
                    datos['publicaciones'],
                    key=lambda p: p.engagement_score
                )
            }
        
        return resultado
    
    def identificar_mejor_tipo(self) -> Dict[str, Any]:
        """Identifica el tipo de contenido con mejor engagement."""
        analisis = self.analizar_por_tipo()
        
        if not analisis:
            return {}
        
        # Ordenar por engagement_score_promedio
        tipos_ordenados = sorted(
            analisis.items(),
            key=lambda x: x[1]['engagement_score_promedio'],
            reverse=True
        )
        
        mejor_tipo_key, mejor_tipo_data = tipos_ordenados[0]
        
        # Analizar por qué es mejor
        razones = []
        
        # Comparar con otros tipos
        otros_tipos = {k: v for k, v in analisis.items() if k != mejor_tipo_key}
        
        for otro_tipo_key, otro_tipo_data in otros_tipos.items():
            diferencia_score = mejor_tipo_data['engagement_score_promedio'] - otro_tipo_data['engagement_score_promedio']
            diferencia_rate = mejor_tipo_data['engagement_rate_promedio'] - otro_tipo_data['engagement_rate_promedio']
            
            if diferencia_score > 0:
                razones.append(
                    f"Supera a {otro_tipo_data['nombre']} por {diferencia_score:.1f} puntos "
                    f"en engagement score ({diferencia_rate:.2f}% más en engagement rate)"
                )
        
        # Analizar características específicas
        caracteristicas = []
        if mejor_tipo_data['comentarios_promedio'] > mejor_tipo_data['likes_promedio'] * 0.2:
            caracteristicas.append("Genera alta participación en comentarios (más del 20% de likes)")
        if mejor_tipo_data['shares_promedio'] > mejor_tipo_data['likes_promedio'] * 0.15:
            caracteristicas.append("Alto índice de compartidos (más del 15% de likes)")
        if mejor_tipo_data['porcentaje_con_media'] > 85:
            caracteristicas.append("Mayoría de publicaciones incluyen contenido multimedia")
        
        return {
            'tipo': mejor_tipo_key,
            'datos': mejor_tipo_data,
            'razones_superioridad': razones,
            'caracteristicas_clave': caracteristicas,
            'comparacion_con_otros': otros_tipos
        }
    
    def generar_recomendaciones(self, mejor_tipo: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera 5 recomendaciones basadas en el patrón del mejor tipo."""
        tipo_key = mejor_tipo['tipo']
        datos = mejor_tipo['datos']
        
        recomendaciones = []
        
        # Basadas en las características del mejor tipo
        if tipo_key == 'X':  # Tutoriales/Educativos
            recomendaciones = [
                {
                    'titulo': 'Serie de Tutoriales Paso a Paso',
                    'descripcion': 'Crear una serie semanal de tutoriales cortos (5-10 min) sobre temas específicos',
                    'razon': 'Los tutoriales generan alto engagement porque proporcionan valor inmediato',
                    'formato_sugerido': 'Video corto con capturas de pantalla y narración',
                    'hashtags_sugeridos': ['#tutorial', '#aprende', '#pasoapaso', '#tips'],
                    'frecuencia': '1-2 veces por semana'
                },
                {
                    'titulo': 'Tips Rápidos en Formato Carousel',
                    'descripcion': 'Publicaciones tipo carousel con 5-7 tips visuales y concisos',
                    'razon': 'El formato carousel mantiene a la audiencia comprometida y genera más tiempo de visualización',
                    'formato_sugerido': 'Carousel de Instagram/LinkedIn con imágenes/texto',
                    'hashtags_sugeridos': ['#tips', '#consejos', '#productividad', '#aprende'],
                    'frecuencia': '2-3 veces por semana'
                },
                {
                    'titulo': 'Casos de Estudio con Resultados',
                    'descripcion': 'Mostrar casos reales de cómo aplicar conocimientos con resultados medibles',
                    'razon': 'Los casos de estudio generan credibilidad y comentarios de personas que quieren replicar',
                    'formato_sugerido': 'Post largo con imágenes antes/después o métricas',
                    'hashtags_sugeridos': ['#casoestudio', '#resultados', '#exito', '#aprende'],
                    'frecuencia': '1 vez por semana'
                },
                {
                    'titulo': 'Preguntas y Respuestas en Vivo',
                    'descripcion': 'Sesiones de Q&A donde respondes preguntas frecuentes de tu audiencia',
                    'razon': 'El formato interactivo genera alta participación en comentarios y shares',
                    'formato_sugerido': 'Video en vivo o Stories con preguntas',
                    'hashtags_sugeridos': ['#preguntas', '#respuestas', '#live', '#comunidad'],
                    'frecuencia': '1 vez cada 2 semanas'
                },
                {
                    'titulo': 'Guías Descargables Gratuitas',
                    'descripcion': 'Crear PDFs o recursos descargables que complementen tus publicaciones',
                    'razon': 'Los recursos descargables generan saves y shares, aumentando el engagement',
                    'formato_sugerido': 'Post con link a descarga + preview del contenido',
                    'hashtags_sugeridos': ['#descarga', '#gratis', '#recurso', '#guia'],
                    'frecuencia': '1 vez por semana'
                }
            ]
        
        elif tipo_key == 'Y':  # Entretenimiento/Viral
            recomendaciones = [
                {
                    'titulo': 'Contenido Behind-the-Scenes',
                    'descripcion': 'Mostrar el proceso detrás de tus proyectos o trabajo diario',
                    'razon': 'El contenido auténtico y personal genera conexión emocional',
                    'formato_sugerido': 'Stories o posts cortos con videos casuales',
                    'hashtags_sugeridos': ['#behindthescenes', '#proceso', '#real', '#autentico'],
                    'frecuencia': '2-3 veces por semana'
                },
                {
                    'titulo': 'Desafíos o Trends Populares',
                    'descripcion': 'Adaptar trends virales del momento a tu nicho o industria',
                    'razon': 'Los trends tienen alto potencial de alcance orgánico',
                    'formato_sugerido': 'Video corto siguiendo el formato del trend',
                    'hashtags_sugeridos': ['#trending', '#viral', '#challenge', '#moda'],
                    'frecuencia': '1-2 veces por semana'
                },
                {
                    'titulo': 'Memes Relacionados con tu Industria',
                    'descripcion': 'Crear memes divertidos pero relevantes para tu audiencia',
                    'razon': 'Los memes generan shares rápidos y engagement emocional',
                    'formato_sugerido': 'Imagen con texto o formato meme estándar',
                    'hashtags_sugeridos': ['#meme', '#humor', '#divertido', '#relatable'],
                    'frecuencia': '1-2 veces por semana'
                },
                {
                    'titulo': 'Historias Inspiradoras o Motivacionales',
                    'descripcion': 'Compartir historias personales o de clientes que inspiren',
                    'razon': 'El contenido emocional genera comentarios y conexión profunda',
                    'formato_sugerido': 'Post largo con texto o video narrado',
                    'hashtags_sugeridos': ['#inspiracion', '#motivacion', '#historia', '#exito'],
                    'frecuencia': '1 vez por semana'
                },
                {
                    'titulo': 'Contenido Interactivo (Polls, Quizzes)',
                    'descripcion': 'Usar features interactivas de las plataformas (encuestas, preguntas)',
                    'razon': 'La interacción directa aumenta el engagement y tiempo en plataforma',
                    'formato_sugerido': 'Stories con polls o posts con preguntas',
                    'hashtags_sugeridos': ['#interactivo', '#encuesta', '#comunidad', '#participa'],
                    'frecuencia': '2-3 veces por semana'
                }
            ]
        
        else:  # Z: Promocional/Producto
            recomendaciones = [
                {
                    'titulo': 'Educación sobre el Producto',
                    'descripcion': 'Convertir promociones en contenido educativo sobre beneficios y uso',
                    'razon': 'El contenido educativo genera más engagement que promociones directas',
                    'formato_sugerido': 'Video tutorial mostrando el producto en uso',
                    'hashtags_sugeridos': ['#tutorial', '#producto', '#beneficios', '#como'],
                    'frecuencia': '1-2 veces por semana'
                },
                {
                    'titulo': 'Testimonios y Reviews de Clientes',
                    'descripcion': 'Mostrar resultados reales de clientes usando tu producto/servicio',
                    'razon': 'La prueba social genera credibilidad y engagement orgánico',
                    'formato_sugerido': 'Video testimonial o post con imágenes de resultados',
                    'hashtags_sugeridos': ['#testimonial', '#review', '#cliente', '#resultados'],
                    'frecuencia': '1 vez por semana'
                },
                {
                    'titulo': 'Comparativas y Demostraciones',
                    'descripcion': 'Mostrar comparaciones antes/después o vs competencia',
                    'razon': 'Las comparativas ayudan a la decisión y generan comentarios',
                    'formato_sugerido': 'Carousel o video con comparación visual',
                    'hashtags_sugeridos': ['#comparacion', '#demo', '#antesydespues', '#mejor'],
                    'frecuencia': '1 vez cada 2 semanas'
                },
                {
                    'titulo': 'Contenido de Valor Gratuito',
                    'descripcion': 'Ofrecer valor primero (consejos, herramientas) antes de promocionar',
                    'razon': 'El contenido de valor genera confianza y aumenta el engagement',
                    'formato_sugerido': 'Post educativo con call-to-action suave al final',
                    'hashtags_sugeridos': ['#gratis', '#valor', '#consejo', '#herramienta'],
                    'frecuencia': '2-3 veces por semana'
                },
                {
                    'titulo': 'Lanzamientos con Anticipación',
                    'descripcion': 'Crear expectativa con contenido de "próximamente" y detrás de escena',
                    'razon': 'La anticipación genera engagement antes del lanzamiento',
                    'formato_sugerido': 'Serie de posts contando la historia del desarrollo',
                    'hashtags_sugeridos': ['#proximamente', '#lanzamiento', '#nuevo', '#exclusivo'],
                    'frecuencia': 'Durante campañas de lanzamiento'
                }
            ]
        
        return recomendaciones
    
    def generar_reporte(self) -> Dict[str, Any]:
        """Genera un reporte completo del análisis."""
        mejor_tipo = self.identificar_mejor_tipo()
        recomendaciones = self.generar_recomendaciones(mejor_tipo)
        analisis_completo = self.analizar_por_tipo()
        
        return {
            'fecha_analisis': datetime.now().isoformat(),
            'periodo_analizado': 'Últimos 30 días',
            'total_publicaciones': len(self.publicaciones),
            'mejor_tipo_contenido': mejor_tipo,
            'analisis_por_tipo': analisis_completo,
            'recomendaciones': recomendaciones,
            'resumen_ejecutivo': {
                'tipo_ganador': mejor_tipo['tipo'],
                'nombre_tipo': mejor_tipo['datos']['nombre'],
                'engagement_rate_promedio': mejor_tipo['datos']['engagement_rate_promedio'],
                'engagement_score_promedio': mejor_tipo['datos']['engagement_score_promedio'],
                'razones_principales': mejor_tipo['razones_superioridad'][:3],
                'caracteristicas_clave': mejor_tipo['caracteristicas_clave']
            }
        }


def main():
    """Función principal."""
    print("=" * 80)
    print("ANÁLISIS DE ENGAGEMENT DE CONTENIDO - ÚLTIMO MES")
    print("=" * 80)
    print()
    
    # Crear analizador y generar datos
    analizador = AnalizadorEngagement()
    print("📊 Generando datos de ejemplo del último mes...")
    analizador.generar_datos_ejemplo(num_publicaciones=30)
    print(f"✅ {len(analizador.publicaciones)} publicaciones generadas")
    print()
    
    # Generar reporte
    print("🔍 Analizando engagement por tipo de contenido...")
    reporte = analizador.generar_reporte()
    print()
    
    # Mostrar resultados
    print("=" * 80)
    print("RESUMEN EJECUTIVO")
    print("=" * 80)
    print()
    
    resumen = reporte['resumen_ejecutivo']
    print(f"🏆 TIPO DE CONTENIDO CON MAYOR ENGAGEMENT: {resumen['nombre_tipo']} (Tipo {resumen['tipo_ganador']})")
    print()
    print(f"📈 Métricas Clave:")
    print(f"   • Engagement Rate Promedio: {resumen['engagement_rate_promedio']:.2f}%")
    print(f"   • Engagement Score Promedio: {resumen['engagement_score_promedio']:.1f} puntos")
    print()
    
    print("💡 ¿Por qué este tipo obtuvo más engagement?")
    for i, razon in enumerate(resumen['razones_principales'], 1):
        print(f"   {i}. {razon}")
    print()
    
    print("✨ Características Clave:")
    for i, caracteristica in enumerate(resumen['caracteristicas_clave'], 1):
        print(f"   {i}. {caracteristica}")
    print()
    
    print("=" * 80)
    print("ANÁLISIS DETALLADO POR TIPO")
    print("=" * 80)
    print()
    
    for tipo_key, datos in reporte['analisis_por_tipo'].items():
        print(f"📌 {datos['nombre']} (Tipo {tipo_key}):")
        print(f"   • Publicaciones: {datos['cantidad_publicaciones']}")
        print(f"   • Engagement Total: {datos['engagement_total']:.0f}")
        print(f"   • Engagement Promedio: {datos['engagement_promedio']:.1f}")
        print(f"   • Engagement Rate: {datos['engagement_rate_promedio']:.2f}%")
        print(f"   • Likes Promedio: {datos['likes_promedio']:.1f}")
        print(f"   • Comentarios Promedio: {datos['comentarios_promedio']:.1f}")
        print(f"   • Shares Promedio: {datos['shares_promedio']:.1f}")
        print(f"   • Con Media: {datos['porcentaje_con_media']:.1f}%")
        print()
    
    print("=" * 80)
    print("5 RECOMENDACIONES BASADAS EN EL PATRÓN GANADOR")
    print("=" * 80)
    print()
    
    for i, rec in enumerate(reporte['recomendaciones'], 1):
        print(f"{i}. {rec['titulo']}")
        print(f"   📝 Descripción: {rec['descripcion']}")
        print(f"   💭 Razón: {rec['razon']}")
        print(f"   🎬 Formato Sugerido: {rec['formato_sugerido']}")
        print(f"   🏷️  Hashtags: {', '.join(rec['hashtags_sugeridos'])}")
        print(f"   📅 Frecuencia: {rec['frecuencia']}")
        print()
    
    # Guardar reporte en JSON
    output_file = f"reporte_engagement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False, default=str)
    
    print("=" * 80)
    print(f"✅ Reporte completo guardado en: {output_file}")
    print("=" * 80)


if __name__ == '__main__':
    main()

