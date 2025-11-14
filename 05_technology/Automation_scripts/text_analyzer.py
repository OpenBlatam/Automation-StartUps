#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from collections import Counter
from datetime import datetime
import json

def analyze_text():
    """Analiza el texto de Bioclones y genera estadísticas detalladas"""
    
    # Texto completo de Bioclones
    text = """
    Era la primera vez que visitábamos una de las donde se clonaban cultivos. Una restricción de DNA – Francisco me hizo usar área restringida para personas con sus expertises muy dedicados a la genética con alto acceso en el organismo. Con grandes pilares de color azul, minimalista y apuntalado para generar mucha altura vi la entrada del gran complejo. Nuestras credenciales fueron actualizadas de inmediato. A nuestra llegada nos esperaba Sophie, amiga de Roger, siempre me pareció muy atractiva e inteligente. ¡Bienvenida a la Capital Biológica! – exclamó con gran calidez, aunque suele tener lenguaje no verbal para expresar su entusiasmo. Estábamos con credenciales para la razón y analítica, como consecuencia de que las clásicas acerca de un tópico en lo específico. Pero eso fue muy breve.

    No traigo valijas y maletas y una misión de colas a hacer a nueva investigación. Las diferentes salas que parecen no tener fin. Con una curiosidad y emoción, caminé como la de un niño en una juguetería, recorrimos las diferentes áreas del complejo. Sophie continuaba muy bien en sus explicaciones.

    Mientras me distraía observando los trajes blancos radiactivos del personal, dejamos nuestro espacio reducido de trabajo, un lugar lleno de servidumbre a donde pones la mirada. Negros, blancos, verdes, altos, bajos, nuevos, viejos. Los técnicos de todo tipo de seguridad. Completa y racional. Un solo error que fue con su sistema, Don Entrevista, muy sofisticado. Esperando que Sophie tuviera la misma emoción que nosotros, solo dispuso su pronto despedida al llegar al lugar. Disfrutamos con el morbo de ver qué hacían que hacían las otras áreas, rápido. Descargamos las nuevas actualizaciones a la fuente matriz del sistema paladiánico y metódico, trabajando hasta casi nueve de la noche. Se sorprenden llegando al final de la jornada a sus martes, recordando que el complejo tenía los mejores salarios y ventajas competitivas de las sesiones extracurriculares que ponían muy celosos al personal, como la secreta a veces todos querían. Todos aluden en su contrato: G. R. E. E.

    Cuando me imaginaba un salario diez veces más grande, y lo multiplicaba por años que me faltaban hasta la esperanza de vida, esto sin gastar en nada, tenía un total en activos que me llevaban a una fantasía de ser alguien con dinero.

    El murmullo terminó en la sala donde se rumoraba la mayoría de los antibombas que nos protegían. Pasó más rápido el protocolo que a mi mente no le dio más oportunidades de rumorear mis pensamientos filosóficos – existencialistas. Toda esta noche no pude dormir, todo evocaba a la Eternidad. Todo fue un compartido sentimiento compartido – todo fue todo y a la vez nada.

    Los accesos que habían pasado parecía que era pequeño para la plataforma, porque no habían tenido índices en días. Los bancos y la línea educativa, tenía unos acuerdos y era un mito. La realidad era que fue la primera vez que pasaba en una misión extraordinadaria. Una lucha constante y la guerra era en la Tierra no en la especie. Se pasaba todos los días ahí, hasta las aplicaciones donde crecía de lo sucedido.

    Anthony toda la semana estuvo callado y sin melancolía como si alguien lo hubiera notado su lesión. Por la primera vez que sentía simpatía por un clon. Siempre tuve la idea de que ellos eran más neutrales que yo. Todo pasa por algo y ese algo crea suerte en una carisma, inclusive existe muchos cerebros en los medios secretos de lo sucedido. – ¡Tengo miedo de regresar a la Tierra! – exclamó Anthony.

    – Creo que todos – respondió, mientras observaba su cara blanca, pálida, que reflejaba un miedo muy genuino.

    Nuestras voluntades como profesionales extra planetarios iba hacia objetivos cada vez más extraordinarios, buscaban el origen. Nuestra economía biológica y acercarnos.

    Valía cada vez más para algún día emprender algo que nos acaudalara los bolsillos y no de nuestro pase.

    De salida a plantas más pacíficas, donde la lucha de clases lo encuentra en una balanza más neutral. Otro de nuestros antepasados más formados, radicaba en cuervos, expresados para vivir el suceso de que era ganador exitoso que ayuda a protestar la economía. Lo encuentra esa una volatil donde que los ataques nucleares se expandieron alrededor del glúteo.

    Todo apuntaba a un sube y baja constante. Lo que terminamos lo gastamos rápido. Dado el costo de vida de, sumado a los salarios nos autodestruimos fugazmente. No sé si la depresión era constante pero lo positivo y la superación personal se convirtió en una especie de culto.

    Donde un se sentía en plenitud cuando estamos junto personas muy positivas.

    Antes de terminar, nuestra bienvenida a Anthony recibió una gratificación alarmante y muy poco frecuente. Pronto nos encontrábamos en la área de Biotecnología donde se reforzaban los experimentos de DNA – Francisco y Creo cuando vemos los – hobbies como un trabajo, cambia mucho la forma de hacer las cosas. Siempre que nuestros horarios se extendían nos disgustaba, pero ahora lo vimos como algo de primera instancia.

    Sophie y yo teníamos muchas cosas en común tales que siempre salían a brillar en las conversaciones que teníamos. Todo lo que yo pensaba ella lo adivinaba con mucha naturalidad que a veces me sorprendía. No habíamos pasado mucho tiempo juntos y sentía como me enamoraba día a día.

    Nuestra idea de estar juntos todo el tiempo no salía si solo era lo que yo quería y sentía, pero observaba cómo su sonrisa era más natural y genuina al verme. Era como la música. Se sentía en la década que fue compuesta la nota musical. Es decir eso ya pasó de moda y suena antigua. Era de esos tipos de pensamiento emoción gozosos con un rastro de melancolía.

    Podría ser por rabia, ahora quiero decir. Ahora que no estoy en el mismo lugar, tengo una idea clara. Al día que llegamos después de la noche y al no haber nadie que estuviéramos Descansando, creo que el mundo es sucio.

    Ojos que parecen adivinar. Los había asistido sobre ahora, según se va o viene para el que...

    Sentí resbalarse en mis pies como las manos.
    Esos que ya no vigías, como cansados de tanto.
    Sentí esa que va siendo carnal con el tiempo.
    Una mañana gris. No frágil pero serís.
    Porque lo sabes, como son las mujeres.
    Yo creo que está bien, es este tiempo...

    – ¿Me quieres responder?
    – ¿Qué es un pasado el amor?
    – No lo sé.

    Apartó su mirada de la mía, sus ojos lucían Ven y conocen a bordo de mí.

    En dos segundos y micro segundos, recordé todos mis apegos, desesperanzas y frustraciones de lo que me construyó como Ángel hacia otros.

    Ella robó mi corazón a pasos mientras yo veía su clasismo reflejado en cómo trataba a los demás, que así me gustaba...

    No sabía que estaba encerrado hasta donde más sus defectos. Pero traté de llevar la conversación hacia un descanso, pero ella se retiró como voluntariamente lo habría

    Tomaba el desayuno y la comida con ella en las semanas siguientes. Una y otra vuelta al mismo tema, a la misma conversación.
    """
    
    # Análisis básico
    words = re.findall(r'\b\w+\b', text.lower())
    sentences = re.split(r'[.!?]+', text)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # Estadísticas básicas
    stats = {
        'fecha_analisis': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'estadisticas_basicas': {
            'total_caracteres': len(text),
            'total_palabras': len(words),
            'total_oraciones': len([s for s in sentences if s.strip()]),
            'total_parrafos': len(paragraphs),
            'promedio_palabras_por_oracion': round(len(words) / len([s for s in sentences if s.strip()]), 2),
            'promedio_caracteres_por_palabra': round(len(text) / len(words), 2)
        },
        'palabras_mas_frecuentes': dict(Counter(words).most_common(20)),
        'palabras_unicas': len(set(words)),
        'densidad_lexica': round(len(set(words)) / len(words) * 100, 2)
    }
    
    # Análisis temático
    temas = {
        'ciencia_ficcion': ['clon', 'dna', 'genética', 'biológica', 'experimento', 'tecnología'],
        'emociones': ['miedo', 'amor', 'melancolía', 'emoción', 'sentimiento', 'corazón'],
        'filosofia': ['eternidad', 'existencialista', 'filosófico', 'pensamiento', 'reflexión'],
        'relaciones': ['sophie', 'anthony', 'francisco', 'roger', 'personas', 'juntos'],
        'lugar': ['tierra', 'complejo', 'sala', 'área', 'capital', 'plataforma']
    }
    
    tema_frecuencias = {}
    for tema, palabras_clave in temas.items():
        frecuencia = sum(words.count(palabra) for palabra in palabras_clave)
        tema_frecuencias[tema] = frecuencia
    
    stats['analisis_tematico'] = tema_frecuencias
    
    # Análisis de personajes
    personajes = {
        'Sophie': text.count('Sophie'),
        'Anthony': text.count('Anthony'),
        'Francisco': text.count('Francisco'),
        'Roger': text.count('Roger')
    }
    
    stats['personajes'] = personajes
    
    # Análisis de diálogos
    dialogos = re.findall(r'–[^–]+', text)
    stats['dialogos'] = {
        'total_dialogos': len(dialogos),
        'promedio_longitud_dialogo': round(sum(len(d) for d in dialogos) / len(dialogos), 2) if dialogos else 0
    }
    
    # Análisis de repeticiones
    repeticiones = [word for word, count in Counter(words).items() if count > 3]
    stats['repeticiones_significativas'] = repeticiones
    
    # Guardar análisis
    with open('analisis_texto_bioclones.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    # Generar reporte
    reporte = f"""
# 📊 ANÁLISIS DE TEXTO - BIOCLONES

## 📈 Estadísticas Básicas
- **Total de caracteres:** {stats['estadisticas_basicas']['total_caracteres']:,}
- **Total de palabras:** {stats['estadisticas_basicas']['total_palabras']:,}
- **Total de oraciones:** {stats['estadisticas_basicas']['total_oraciones']:,}
- **Total de párrafos:** {stats['estadisticas_basicas']['total_parrafos']:,}
- **Promedio palabras por oración:** {stats['estadisticas_basicas']['promedio_palabras_por_oracion']}
- **Promedio caracteres por palabra:** {stats['estadisticas_basicas']['promedio_caracteres_por_palabra']}
- **Palabras únicas:** {stats['palabras_unicas']:,}
- **Densidad léxica:** {stats['densidad_lexica']}%

## 🔤 Palabras Más Frecuentes
"""
    
    for palabra, frecuencia in list(stats['palabras_mas_frecuentes'].items())[:10]:
        reporte += f"- **{palabra}:** {frecuencia} veces\n"
    
    reporte += f"""
## 🎭 Análisis Temático
"""
    
    for tema, frecuencia in stats['analisis_tematico'].items():
        reporte += f"- **{tema.replace('_', ' ').title()}:** {frecuencia} menciones\n"
    
    reporte += f"""
## 👥 Personajes
"""
    
    for personaje, apariciones in stats['personajes'].items():
        reporte += f"- **{personaje}:** {apariciones} menciones\n"
    
    reporte += f"""
## 💬 Diálogos
- **Total de diálogos:** {stats['dialogos']['total_dialogos']}
- **Promedio longitud:** {stats['dialogos']['promedio_longitud_dialogo']} caracteres

## 🔄 Repeticiones Significativas
"""
    
    for repeticion in stats['repeticiones_significativas'][:10]:
        reporte += f"- **{repeticion}**\n"
    
    reporte += f"""
---
*Análisis generado automáticamente el {stats['fecha_analisis']}*
"""
    
    with open('reporte_analisis_texto.md', 'w', encoding='utf-8') as f:
        f.write(reporte)
    
    print("✅ Análisis de texto completado exitosamente")
    print(f"📊 Estadísticas generadas: {len(stats)} categorías")
    print(f"📄 Reporte guardado: reporte_analisis_texto.md")
    print(f"📋 Datos JSON guardados: analisis_texto_bioclones.json")
    
    return stats

if __name__ == "__main__":
    analyze_text()



















