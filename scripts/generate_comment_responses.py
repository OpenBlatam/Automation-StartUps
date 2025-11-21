#!/usr/bin/env python3
"""
Script para generar respuestas a comentarios típicos en publicaciones de redes sociales.
Genera respuestas amigables que fomentan más conversación y mencionan al usuario.
"""

import json
import sys
import argparse
import re
import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum


class TipoComentario(Enum):
    """Tipos de comentarios que se pueden detectar."""
    INTERES = "interes"
    COMO_EMPEZAR = "como_empezar"
    DIFICULTAD = "dificultad"
    PRECIO = "precio"
    COMPARACION = "comparacion"
    TESTIMONIAL = "testimonial"
    DUDA_TECNICA = "duda_tecnica"
    OBJECION = "objecion"
    COMPARTIR_EXPERIENCIA = "compartir_experiencia"
    GENERICO = "generico"


class CommentResponseGenerator:
    """Generador de respuestas a comentarios con tono amigable de marca."""
    
    def __init__(self, tema: str, tono_marca: str = "amigable y cercano", usar_nombre_usuario: bool = True):
        """
        Inicializa el generador de respuestas.
        
        Args:
            tema: Tema de las publicaciones (ej: "videos de IA", "tecnología", etc.)
            tono_marca: Tono de la marca (default: "amigable y cercano")
            usar_nombre_usuario: Si True, incluye menciones genéricas al usuario
        """
        self.tema = tema
        self.tono_marca = tono_marca
        self.usar_nombre_usuario = usar_nombre_usuario
        self._inicializar_patrones()
    
    def generar_respuestas(self, comentarios_tipicos: Optional[List[str]] = None, variar_respuestas: bool = True) -> List[Dict[str, str]]:
        """
        Genera respuestas a comentarios típicos.
        
        Args:
            comentarios_tipicos: Lista de comentarios típicos. Si es None, usa comentarios por defecto.
            variar_respuestas: Si True, usa diferentes variaciones de respuestas (default: True)
        
        Returns:
            Lista de diccionarios con comentario y respuesta
        """
        if comentarios_tipicos is None:
            comentarios_tipicos = self._obtener_comentarios_tipicos()
        
        respuestas = []
        indice_variacion = 0
        for comentario in comentarios_tipicos:
            respuesta = self._generar_respuesta(comentario, indice_variacion if variar_respuestas else 0)
            tipo_detectado, confianza = self._detectar_tipo_comentario(comentario)
            contexto = self._extraer_contexto(comentario)
            
            respuestas.append({
                "comentario": comentario,
                "respuesta": respuesta,
                "tipo_detectado": tipo_detectado.value,
                "confianza": round(confianza, 2),
                "tema": self.tema,
                "tono": self.tono_marca,
                "contexto": contexto,
                "generado_en": datetime.now().isoformat()
            })
            indice_variacion += 1
        
        return respuestas
    
    def _inicializar_patrones(self):
        """Inicializa los patrones de detección de tipos de comentarios."""
        self.patrones = {
            TipoComentario.INTERES: [
                r"interesante", r"genial", r"increíble", r"wow", r"me gusta", r"me encanta",
                r"impresionante", r"fantástico", r"excelente", r"buen", r"buena", r"cool",
                r"increíble", r"asombroso", r"top", r"perfecto"
            ],
            TipoComentario.COMO_EMPEZAR: [
                r"cómo empezar", r"cómo puedo", r"quiero empezar", r"empezar", r"comenzar",
                r"iniciar", r"dar el primer paso", r"por dónde", r"por donde", r"guía",
                r"tutorial", r"aprender", r"empezar a usar"
            ],
            TipoComentario.DIFICULTAD: [
                r"difícil", r"difícil", r"principiante", r"experiencia", r"nivel", r"fácil",
                r"complicado", r"complejo", r"simple", r"sencillo", r"avanzado", r"básico",
                r"sin experiencia", r"nuevo en", r"no sé", r"no entiendo"
            ],
            TipoComentario.PRECIO: [
                r"precio", r"cuesta", r"costo", r"pagar", r"gratis", r"gratuito", r"caro",
                r"barato", r"económico", r"plan", r"tarifa", r"subscription", r"suscripción",
                r"cuánto", r"cuanto", r"dólares", r"dolares", r"€", r"$"
            ],
            TipoComentario.COMPARACION: [
                r"vs", r"versus", r"comparar", r"diferencia", r"mejor que", r"peor que",
                r"alternativa", r"similar a", r"como", r"igual que"
            ],
            TipoComentario.TESTIMONIAL: [
                r"funciona", r"resultados", r"lo probé", r"lo usé", r"recomiendo",
                r"recomendación", r"vale la pena", r"me ayudó", r"me ayudó", r"exitoso"
            ],
            TipoComentario.DUDA_TECNICA: [
                r"cómo funciona", r"qué es", r"que es", r"explicar", r"entender",
                r"funciona con", r"compatible", r"requisitos", r"necesito", r"requiere",
                r"saber programar", r"conocimientos técnicos", r"programación", r"código",
                r"técnico", r"técnica", r"necesito saber", r"tengo que saber"
            ],
            TipoComentario.OBJECION: [
                r"pero", r"sin embargo", r"aunque", r"no estoy seguro", r"duda",
                r"preocupado", r"miedo", r"riesgo", r"no funciona", r"no sirve"
            ],
            TipoComentario.COMPARTIR_EXPERIENCIA: [
                r"yo uso", r"yo hago", r"mi experiencia", r"en mi caso", r"yo tengo",
                r"he probado", r"he usado", r"mi opinión", r"creo que"
            ]
        }
    
    def _obtener_comentarios_tipicos(self) -> List[str]:
        """Obtiene comentarios típicos según el tema."""
        comentarios_base = [
            "¡Muy interesante! ¿Cómo funciona esto?",
            "¿Cómo puedo empezar?",
            "¿Esto funciona para principiantes?",
            "¿Cuánto cuesta?",
            "¿Qué diferencia tiene con otras opciones?",
            "Lo probé y me encantó",
            "¿Necesito conocimientos técnicos?",
            "Tengo dudas sobre si funcionará para mí"
        ]
        
        # Personalizar según el tema si es necesario
        if "video" in self.tema.lower() or "ia" in self.tema.lower():
            comentarios_base = [
                "¡Muy interesante! ¿Cómo funciona esto?",
                "¿Cómo puedo empezar a crear videos con IA?",
                "¿Esto es difícil de usar para alguien sin experiencia técnica?",
                "¿Cuánto cuesta usar esta herramienta?",
                "¿Qué diferencia tiene con otras herramientas de IA?",
                "Lo probé y los resultados fueron increíbles",
                "¿Necesito saber programar para usarlo?",
                "Me preocupa que sea muy complicado para mí"
            ]
        
        return comentarios_base
    
    def _detectar_tipo_comentario(self, comentario: str) -> Tuple[TipoComentario, float]:
        """
        Detecta el tipo de comentario usando patrones.
        
        Args:
            comentario: El comentario a analizar
        
        Returns:
            Tupla con (tipo_comentario, confianza)
        """
        comentario_lower = comentario.lower()
        puntuaciones = {}
        
        for tipo, patrones in self.patrones.items():
            puntuacion = 0
            for patron in patrones:
                matches = len(re.findall(patron, comentario_lower, re.IGNORECASE))
                puntuacion += matches
            puntuaciones[tipo] = puntuacion
        
        # Priorizar ciertos tipos si tienen puntuación similar
        # Encontrar el tipo con mayor puntuación
        max_puntuacion = max(puntuaciones.values())
        
        if max_puntuacion == 0:
            return TipoComentario.GENERICO, 0.5
        
        # Si hay empate, priorizar tipos más específicos
        tipos_prioritarios = [
            TipoComentario.DUDA_TECNICA,
            TipoComentario.PRECIO,
            TipoComentario.OBJECION,
            TipoComentario.COMPARACION
        ]
        
        candidatos = [tipo for tipo, punt in puntuaciones.items() if punt == max_puntuacion]
        
        # Priorizar tipos más específicos
        for tipo_prioritario in tipos_prioritarios:
            if tipo_prioritario in candidatos:
                tipo_detectado = tipo_prioritario
                break
        else:
            tipo_detectado = candidatos[0]
        
        confianza = min(max_puntuacion / 3.0, 1.0)  # Normalizar confianza
        return tipo_detectado, confianza
    
    def _extraer_contexto(self, comentario: str) -> Dict[str, str]:
        """Extrae contexto relevante del comentario."""
        contexto = {
            "menciona_experiencia": any(palabra in comentario.lower() for palabra in ["experiencia", "probé", "usé", "he usado"]),
            "es_pregunta": "?" in comentario,
            "tiene_objeccion": any(palabra in comentario.lower() for palabra in ["pero", "sin embargo", "aunque", "pero"]),
            "menciona_precio": any(palabra in comentario.lower() for palabra in ["precio", "cuesta", "costo", "gratis"])
        }
        return contexto
    
    def _generar_respuesta(self, comentario: str, variacion: int = 0) -> str:
        """
        Genera una respuesta personalizada a un comentario.
        
        Args:
            comentario: El comentario original
            variacion: Índice de variación para usar diferentes respuestas (0, 1, 2)
        
        Returns:
            Respuesta generada
        """
        tipo_comentario, confianza = self._detectar_tipo_comentario(comentario)
        contexto = self._extraer_contexto(comentario)
        
        # Generar respuesta según el tipo detectado
        if tipo_comentario == TipoComentario.INTERES:
            return self._respuesta_interes(variacion % 3, contexto)
        elif tipo_comentario == TipoComentario.COMO_EMPEZAR:
            return self._respuesta_como_empezar(variacion % 3, contexto)
        elif tipo_comentario == TipoComentario.DIFICULTAD:
            return self._respuesta_nivel(variacion % 3, contexto)
        elif tipo_comentario == TipoComentario.PRECIO:
            return self._respuesta_precio(variacion % 3, contexto)
        elif tipo_comentario == TipoComentario.COMPARACION:
            return self._respuesta_comparacion(variacion % 3, contexto)
        elif tipo_comentario == TipoComentario.TESTIMONIAL:
            return self._respuesta_testimonial(variacion % 3, contexto)
        elif tipo_comentario == TipoComentario.DUDA_TECNICA:
            return self._respuesta_duda_tecnica(variacion % 3, contexto)
        elif tipo_comentario == TipoComentario.OBJECION:
            return self._respuesta_objecion(variacion % 3, contexto)
        elif tipo_comentario == TipoComentario.COMPARTIR_EXPERIENCIA:
            return self._respuesta_compartir_experiencia(variacion % 3, contexto)
        else:
            return self._respuesta_generica(contexto)
    
    def _mencion_usuario(self) -> str:
        """Genera una mención genérica al usuario."""
        if not self.usar_nombre_usuario:
            return ""
        menciones = ["", "¡Hola! ", "¡Ey! "]
        return random.choice(menciones)
    
    def _respuesta_interes(self, variacion: int = 0, contexto: Optional[Dict] = None) -> str:
        """Genera respuesta para comentarios de interés."""
        contexto = contexto or {}
        mencion = self._mencion_usuario()
        
        respuestas = [
            f"{mencion}¡Gracias por tu interés! Nos encanta saber que te gusta nuestro contenido sobre {self.tema}. ¿Hay algo específico que te gustaría saber más? Estamos aquí para ayudarte. 😊",
            
            f"{mencion}¡Qué bien que te haya llamado la atención! Sobre {self.tema} hay mucho que explorar. ¿Te gustaría que profundicemos en algún aspecto en particular? Tu opinión nos ayuda mucho. 💬",
            
            f"{mencion}¡Nos alegra mucho leer esto! Si quieres, podemos compartirte más detalles sobre {self.tema}. ¿Qué parte te resultó más interesante? Nos encantaría conocer tu perspectiva. 🤔",
            
            f"{mencion}¡Genial que te haya gustado! Sobre {self.tema} tenemos mucho contenido que puede interesarte. ¿Hay algún tema específico que te gustaría que cubramos? Tu feedback es súper valioso para nosotros. 🌟"
        ]
        return respuestas[variacion % len(respuestas)]
    
    def _respuesta_como_empezar(self, variacion: int = 0, contexto: Optional[Dict] = None) -> str:
        """Genera respuesta para preguntas sobre cómo empezar."""
        contexto = contexto or {}
        mencion = self._mencion_usuario()
        
        respuestas = [
            f"{mencion}¡Excelente pregunta! Para empezar con {self.tema}, te recomendamos comenzar paso a paso. ¿Tienes alguna experiencia previa o eres completamente nuevo? Con esa info podemos darte una guía más personalizada. 🚀",
            
            f"{mencion}¡Nos encanta tu entusiasmo! Empezar con {self.tema} puede ser más fácil de lo que piensas. ¿Qué te gustaría lograr específicamente? Con eso en mente, podemos sugerirte los mejores recursos para comenzar. 💡",
            
            f"{mencion}¡Perfecto! Para iniciarte en {self.tema}, lo mejor es empezar con lo básico. ¿Tienes alguna meta específica en mente? Compártela con nosotros y te ayudamos a crear un plan que se ajuste a ti. ✨",
            
            f"{mencion}¡Genial que quieras empezar! Te podemos ayudar a dar tus primeros pasos con {self.tema}. ¿Qué es lo que más te interesa lograr? Así podemos orientarte mejor hacia los recursos que más te servirán. 🎯"
        ]
        return respuestas[variacion % len(respuestas)]
    
    def _respuesta_nivel(self, variacion: int = 0, contexto: Optional[Dict] = None) -> str:
        """Genera respuesta para preguntas sobre nivel de dificultad."""
        contexto = contexto or {}
        mencion = self._mencion_usuario()
        
        respuestas = [
            f"{mencion}¡Buena pregunta! Sobre {self.tema}, la buena noticia es que hay opciones para todos los niveles. Si eres principiante, podemos guiarte paso a paso. ¿Qué nivel de experiencia tienes actualmente? Así te damos recomendaciones más precisas. 📚",
            
            f"{mencion}¡No te preocupes por eso! {self.tema.capitalize()} puede adaptarse a cualquier nivel. Lo importante es empezar y aprender a tu ritmo. ¿Hay algo específico que te preocupe o te gustaría saber? Estamos aquí para ayudarte en cada paso. 🌟",
            
            f"{mencion}¡Excelente que lo preguntes! La verdad es que {self.tema} puede ser accesible para principiantes con las herramientas y recursos adecuados. ¿Te gustaría que te compartamos algunos tips para empezar? Tu experiencia previa nos ayudaría a personalizar mejor la respuesta. 🎯"
        ]
        return respuestas[variacion % len(respuestas)]
    
    def _respuesta_precio(self, variacion: int = 0, contexto: Optional[Dict] = None) -> str:
        """Genera respuesta para preguntas sobre precio."""
        contexto = contexto or {}
        mencion = self._mencion_usuario()
        
        respuestas = [
            f"{mencion}¡Entendemos tu interés! Sobre el precio de {self.tema}, tenemos diferentes opciones que se adaptan a distintas necesidades. ¿Te gustaría que te compartamos más detalles sobre nuestros planes? Podemos encontrar la opción que mejor se ajuste a lo que buscas. 💰",
            
            f"{mencion}¡Buena pregunta! En cuanto a {self.tema}, tenemos opciones para diferentes presupuestos. ¿Qué es lo que más te interesa lograr? Con esa información podemos recomendarte la mejor opción para ti. 📊",
            
            f"{mencion}¡Claro! Sobre {self.tema} tenemos varias opciones disponibles. ¿Te gustaría que te expliquemos las diferencias entre nuestros planes? Así puedes elegir el que mejor se adapte a tus necesidades y presupuesto. 💡"
        ]
        return respuestas[variacion % len(respuestas)]
    
    def _respuesta_comparacion(self, variacion: int = 0, contexto: Optional[Dict] = None) -> str:
        """Genera respuesta para preguntas de comparación."""
        contexto = contexto or {}
        mencion = self._mencion_usuario()
        
        respuestas = [
            f"{mencion}¡Excelente pregunta! Para comparar {self.tema} con otras opciones, lo mejor es entender qué es lo que más valoras. ¿Qué características son más importantes para ti? Con eso podemos ayudarte a ver qué opción se ajusta mejor a tus necesidades. 🔍",
            
            f"{mencion}¡Entendemos que quieras comparar! Cada opción tiene sus ventajas. Con {self.tema}, nos enfocamos en [característica clave]. ¿Qué es lo que más buscas en una solución? Así te podemos dar una comparación más precisa. ⚖️",
            
            f"{mencion}¡Buena pregunta! La mejor forma de comparar es ver qué se ajusta mejor a lo que necesitas. ¿Qué es lo más importante para ti en {self.tema}? Con esa info podemos ayudarte a tomar la mejor decisión. 🎯"
        ]
        return respuestas[variacion % len(respuestas)]
    
    def _respuesta_testimonial(self, variacion: int = 0, contexto: Optional[Dict] = None) -> str:
        """Genera respuesta para testimonios positivos."""
        contexto = contexto or {}
        mencion = self._mencion_usuario()
        
        respuestas = [
            f"{mencion}¡Nos alegra mucho saber que {self.tema} te haya funcionado tan bien! Tu experiencia es súper valiosa. ¿Te gustaría compartir más detalles sobre cómo lo estás usando? Eso puede ayudar a otros que están considerando empezar. 🙌",
            
            f"{mencion}¡Qué genial que lo hayas probado y te haya gustado! Nos encanta escuchar experiencias como la tuya. ¿Hay algún consejo o tip que quieras compartir con la comunidad? Tu perspectiva es muy valiosa. 💬",
            
            f"{mencion}¡Excelente! Nos emociona saber que {self.tema} te está dando buenos resultados. ¿Qué es lo que más te ha gustado hasta ahora? Y si tienes alguna sugerencia de mejora, siempre estamos abiertos a escucharla. 🌟"
        ]
        return respuestas[variacion % len(respuestas)]
    
    def _respuesta_duda_tecnica(self, variacion: int = 0, contexto: Optional[Dict] = None) -> str:
        """Genera respuesta para dudas técnicas."""
        contexto = contexto or {}
        mencion = self._mencion_usuario()
        
        respuestas = [
            f"{mencion}¡Claro que sí! Te explico cómo funciona {self.tema} de forma sencilla: [explicación básica]. ¿Hay algún aspecto específico que te gustaría que profundicemos más? Estamos aquí para resolver todas tus dudas. 🔧",
            
            f"{mencion}¡Por supuesto! {self.tema.capitalize()} funciona de la siguiente manera: [concepto clave]. ¿Tienes alguna pregunta específica sobre cómo implementarlo o usarlo? Con gusto te ayudamos. 💡",
            
            f"{mencion}¡Excelente pregunta! Te explico: {self.tema} [explicación]. ¿Hay algo en particular que te gustaría entender mejor? Puedo darte más detalles sobre cualquier aspecto que te interese. 📚"
        ]
        return respuestas[variacion % len(respuestas)]
    
    def _respuesta_objecion(self, variacion: int = 0, contexto: Optional[Dict] = None) -> str:
        """Genera respuesta para objeciones o preocupaciones."""
        contexto = contexto or {}
        mencion = self._mencion_usuario()
        
        respuestas = [
            f"{mencion}¡Entendemos tu preocupación! Es normal tener dudas al empezar con {self.tema}. ¿Qué es lo que más te preocupa específicamente? Podemos ayudarte a resolver esas dudas y mostrarte cómo otros han superado desafíos similares. 🤝",
            
            f"{mencion}¡Comprendemos perfectamente! Es válido tener dudas sobre {self.tema}. ¿Te gustaría que te compartamos algunos casos de éxito o testimonios de personas que tenían preocupaciones similares? A veces ver ejemplos reales ayuda mucho. 💪",
            
            f"{mencion}¡Es normal tener esas dudas! Sobre {self.tema}, muchas personas han tenido preocupaciones similares y las hemos ayudado a resolverlas. ¿Qué es lo que más te inquieta? Con gusto te ayudamos a encontrar la solución. 🌟"
        ]
        return respuestas[variacion % len(respuestas)]
    
    def _respuesta_compartir_experiencia(self, variacion: int = 0, contexto: Optional[Dict] = None) -> str:
        """Genera respuesta cuando alguien comparte su experiencia."""
        contexto = contexto or {}
        mencion = self._mencion_usuario()
        
        respuestas = [
            f"{mencion}¡Gracias por compartir tu experiencia! Es súper valioso escuchar cómo otros están usando {self.tema}. ¿Te gustaría que profundicemos en algún aspecto de lo que compartiste? O si tienes alguna pregunta, estamos aquí para ayudarte. 💬",
            
            f"{mencion}¡Nos encanta que compartas! Tu experiencia con {self.tema} es muy interesante. ¿Hay algo específico que te gustaría mejorar o algún consejo que quieras compartir con la comunidad? Tu perspectiva es muy valiosa. 🙌",
            
            f"{mencion}¡Excelente que compartas! Es genial ver cómo diferentes personas usan {self.tema} de formas distintas. ¿Hay algún aspecto en el que te gustaría profundizar más o alguna duda que tengas? Estamos aquí para ayudarte. 🌟"
        ]
        return respuestas[variacion % len(respuestas)]
    
    def _respuesta_generica(self, contexto: Optional[Dict] = None) -> str:
        """Genera respuesta genérica amigable."""
        contexto = contexto or {}
        mencion = self._mencion_usuario()
        
        return f"{mencion}¡Gracias por tu comentario! Nos encanta saber tu opinión sobre {self.tema}. ¿Hay algo específico en lo que podamos ayudarte o sobre lo que te gustaría saber más? Estamos aquí para conversar contigo. 💬"


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Genera respuestas a comentarios típicos en publicaciones de redes sociales"
    )
    parser.add_argument(
        "tema",
        help="Tema de las publicaciones (ej: 'videos de IA', 'tecnología', 'marketing digital')"
    )
    parser.add_argument(
        "--comentarios",
        nargs="+",
        help="Comentarios específicos a los que responder (opcional)"
    )
    parser.add_argument(
        "--tono",
        default="amigable y cercano",
        help="Tono de la marca (default: 'amigable y cercano')"
    )
    parser.add_argument(
        "--output",
        choices=["json", "text"],
        default="json",
        help="Formato de salida (default: json)"
    )
    parser.add_argument(
        "--archivo",
        help="Archivo JSON con comentarios personalizados"
    )
    parser.add_argument(
        "--sin-mencion-usuario",
        action="store_true",
        help="No incluir menciones genéricas al usuario en las respuestas"
    )
    parser.add_argument(
        "--mostrar-detalles",
        action="store_true",
        help="Mostrar detalles de detección (tipo, confianza, contexto)"
    )
    
    args = parser.parse_args()
    
    # Cargar comentarios desde archivo si se proporciona
    comentarios = args.comentarios
    if args.archivo:
        try:
            with open(args.archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
                comentarios = data.get('comentarios', comentarios)
        except Exception as e:
            print(f"Error al cargar archivo: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Generar respuestas
    generador = CommentResponseGenerator(
        tema=args.tema, 
        tono_marca=args.tono,
        usar_nombre_usuario=not getattr(args, 'sin_mention_usuario', False)
    )
    respuestas = generador.generar_respuestas(comentarios_tipicos=comentarios)
    
    # Mostrar resultados
    if args.output == "json":
        output_data = {
            "tema": args.tema,
            "tono": args.tono,
            "respuestas": respuestas,
            "total": len(respuestas)
        }
        if not args.mostrar_detalles:
            # Simplificar respuestas si no se quieren detalles
            output_data["respuestas"] = [
                {
                    "comentario": r["comentario"],
                    "respuesta": r["respuesta"]
                }
                for r in respuestas
            ]
        print(json.dumps(output_data, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*70}")
        print(f"RESPUESTAS A COMENTARIOS - TEMA: {args.tema.upper()}")
        print(f"{'='*70}\n")
        for i, item in enumerate(respuestas, 1):
            print(f"\n[{i}] COMENTARIO:")
            print(f"    {item['comentario']}")
            print(f"\n    RESPUESTA:")
            print(f"    {item['respuesta']}")
            if args.mostrar_detalles:
                print(f"\n    [Detalles] Tipo: {item.get('tipo_detectado', 'N/A')} | "
                      f"Confianza: {item.get('confianza', 0):.2f}")
            print(f"\n    {'-'*70}")


if __name__ == "__main__":
    main()

