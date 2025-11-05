#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from collections import Counter
from datetime import datetime
import json

def analyze_sentiment():
    """Analiza el sentimiento y las emociones del texto de Bioclones"""
    
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
    
    # Diccionarios de sentimientos y emociones
    positive_words = [
        'calidez', 'entusiasmo', 'curiosidad', 'emoción', 'fantasía', 'plenitud', 
        'positivas', 'gratificación', 'brillar', 'naturalidad', 'sorprendía', 
        'enamoraba', 'sonrisa', 'genuina', 'música', 'gozosos', 'amor', 'corazón'
    ]
    
    negative_words = [
        'restricción', 'restringida', 'breve', 'servidumbre', 'error', 'despedida',
        'morbo', 'celosos', 'secreta', 'murmullo', 'rumorear', 'filosóficos',
        'existencialistas', 'eternidad', 'nada', 'lucha', 'guerra', 'melancolía',
        'lesión', 'miedo', 'genuino', 'volatil', 'ataques', 'nucleares', 'depresión',
        'autodestruimos', 'disgustaba', 'rabia', 'sucio', 'cansados', 'gris',
        'frágil', 'desesperanzas', 'frustraciones', 'encerrado', 'defectos'
    ]
    
    neutral_words = [
        'dna', 'genética', 'complejo', 'credenciales', 'sophie', 'roger',
        'técnicos', 'sistema', 'protocolo', 'plataforma', 'anthony', 'francisco',
        'trabajo', 'experimentos', 'conversaciones', 'tiempo', 'mundo', 'ojos'
    ]
    
    # Análisis de emociones específicas
    emotions = {
        'miedo': ['miedo', 'temor', 'ansiedad', 'preocupación', 'angustia'],
        'amor': ['amor', 'enamoraba', 'corazón', 'sentimiento', 'cariño'],
        'tristeza': ['tristeza', 'melancolía', 'depresión', 'desesperanza', 'frustración'],
        'alegría': ['alegría', 'felicidad', 'gozo', 'placer', 'satisfacción'],
        'ira': ['ira', 'rabia', 'enojo', 'frustración', 'resentimiento'],
        'sorpresa': ['sorpresa', 'asombro', 'sorprendía', 'sorprendente', 'inesperado'],
        'nostalgia': ['nostalgia', 'recuerdo', 'pasado', 'memoria', 'añoranza']
    }
    
    # Análisis de sentimiento general
    words = re.findall(r'\b\w+\b', text.lower())
    
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    neutral_count = sum(1 for word in words if word in neutral_words)
    
    total_words = len(words)
    
    # Cálculo de sentimiento
    sentiment_score = (positive_count - negative_count) / total_words if total_words > 0 else 0
    
    # Análisis de emociones
    emotion_analysis = {}
    for emotion, emotion_words in emotions.items():
        count = sum(1 for word in words if word in emotion_words)
        emotion_analysis[emotion] = count
    
    # Análisis de intensidad emocional
    intensity_words = ['muy', 'mucho', 'extremadamente', 'completamente', 'totalmente']
    intensity_count = sum(1 for word in words if word in intensity_words)
    
    # Análisis de diálogos emocionales
    dialogues = re.findall(r'–[^–]+', text)
    emotional_dialogues = []
    for dialogue in dialogues:
        if any(word in dialogue.lower() for word in positive_words + negative_words):
            emotional_dialogues.append(dialogue.strip())
    
    # Análisis de cambios emocionales
    sentences = re.split(r'[.!?]+', text)
    emotional_sentences = []
    for sentence in sentences:
        if any(word in sentence.lower() for word in positive_words + negative_words):
            emotional_sentences.append(sentence.strip())
    
    # Crear análisis completo
    analysis = {
        'fecha_analisis': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sentimiento_general': {
            'score': round(sentiment_score, 3),
            'interpretacion': 'Positivo' if sentiment_score > 0 else 'Negativo' if sentiment_score < 0 else 'Neutral',
            'palabras_positivas': positive_count,
            'palabras_negativas': negative_count,
            'palabras_neutrales': neutral_count,
            'total_palabras': total_words
        },
        'emociones_detectadas': emotion_analysis,
        'intensidad_emocional': {
            'palabras_intensidad': intensity_count,
            'nivel_intensidad': 'Alto' if intensity_count > 10 else 'Medio' if intensity_count > 5 else 'Bajo'
        },
        'dialogos_emocionales': {
            'total_dialogos': len(dialogues),
            'dialogos_emocionales': len(emotional_dialogues),
            'porcentaje_emocional': round(len(emotional_dialogues) / len(dialogues) * 100, 2) if dialogues else 0
        },
        'oraciones_emocionales': {
            'total_oraciones': len(sentences),
            'oraciones_emocionales': len(emotional_sentences),
            'porcentaje_emocional': round(len(emotional_sentences) / len(sentences) * 100, 2) if sentences else 0
        },
        'palabras_mas_emocionales': dict(Counter([word for word in words if word in positive_words + negative_words]).most_common(10))
    }
    
    # Guardar análisis
    with open('analisis_sentimientos_bioclones.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    # Generar reporte
    reporte = f"""
# 📊 ANÁLISIS DE SENTIMIENTOS - BIOCLONES

## 🎭 Sentimiento General
- **Score de sentimiento:** {analysis['sentimiento_general']['score']}
- **Interpretación:** {analysis['sentimiento_general']['interpretacion']}
- **Palabras positivas:** {analysis['sentimiento_general']['palabras_positivas']}
- **Palabras negativas:** {analysis['sentimiento_general']['palabras_negativas']}
- **Palabras neutrales:** {analysis['sentimiento_general']['palabras_neutrales']}

## 😊 Emociones Detectadas
"""
    
    for emotion, count in analysis['emociones_detectadas'].items():
        reporte += f"- **{emotion.title()}:** {count} menciones\n"
    
    reporte += f"""
## 🔥 Intensidad Emocional
- **Palabras de intensidad:** {analysis['intensidad_emocional']['palabras_intensidad']}
- **Nivel de intensidad:** {analysis['intensidad_emocional']['nivel_intensidad']}

## 💬 Diálogos Emocionales
- **Total de diálogos:** {analysis['dialogos_emocionales']['total_dialogos']}
- **Diálogos emocionales:** {analysis['dialogos_emocionales']['dialogos_emocionales']}
- **Porcentaje emocional:** {analysis['dialogos_emocionales']['porcentaje_emocional']}%

## 📝 Oraciones Emocionales
- **Total de oraciones:** {analysis['oraciones_emocionales']['total_oraciones']}
- **Oraciones emocionales:** {analysis['oraciones_emocionales']['oraciones_emocionales']}
- **Porcentaje emocional:** {analysis['oraciones_emocionales']['porcentaje_emocional']}%

## 🎯 Palabras Más Emocionales
"""
    
    for palabra, frecuencia in list(analysis['palabras_mas_emocionales'].items())[:10]:
        reporte += f"- **{palabra}:** {frecuencia} veces\n"
    
    reporte += f"""
---
*Análisis de sentimientos generado automáticamente el {analysis['fecha_analisis']}*
"""
    
    with open('reporte_sentimientos.md', 'w', encoding='utf-8') as f:
        f.write(reporte)
    
    print("✅ Análisis de sentimientos completado exitosamente")
    print(f"📊 Sentimiento general: {analysis['sentimiento_general']['interpretacion']}")
    print(f"😊 Emociones detectadas: {len(analysis['emociones_detectadas'])} tipos")
    print(f"💬 Diálogos emocionales: {analysis['dialogos_emocionales']['dialogos_emocionales']}")
    print(f"📄 Reporte guardado: reporte_sentimientos.md")
    print(f"📋 Datos JSON guardados: analisis_sentimientos_bioclones.json")
    
    return analysis

if __name__ == "__main__":
    analyze_sentiment()


















