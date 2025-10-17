#!/usr/bin/env python3
"""
Generador de Casos de Uso Específicos para Anchor Texts IA Marketing
Crea variantes personalizadas para situaciones específicas del negocio
"""

import json
import random
from datetime import datetime
from typing import List, Dict, Any, Tuple
import os

class GeneradorCasosUsoAnchorTexts:
    def __init__(self):
        self.casos_uso = {
            'lanzamiento_producto': {
                'contexto': 'Nuevo curso de IA marketing',
                'objetivo': 'Generar expectativa y conversión',
                'tono': 'Urgente y emocional',
                'palabras_clave': ['nuevo', 'lanzamiento', 'exclusivo', 'limitado', 'revolucionario']
            },
            'recuperacion_carrito': {
                'contexto': 'Usuario abandonó el proceso de compra',
                'objetivo': 'Recuperar la venta perdida',
                'tono': 'Urgente y persuasivo',
                'palabras_clave': ['última oportunidad', 'descuento', 'oferta especial', 'no te pierdas']
            },
            'upselling': {
                'contexto': 'Cliente ya compró un curso básico',
                'objetivo': 'Vender curso avanzado',
                'tono': 'Educativo y motivacional',
                'palabras_clave': ['siguiente nivel', 'avanzado', 'masterclass', 'certificación']
            },
            'retargeting': {
                'contexto': 'Usuario visitó pero no compró',
                'objetivo': 'Reactivar el interés',
                'tono': 'Persuasivo y social',
                'palabras_clave': ['testimonios', 'casos de éxito', 'garantía', 'satisfacción']
            },
            'email_marketing': {
                'contexto': 'Campaña de email marketing',
                'objetivo': 'Aumentar apertura y clics',
                'tono': 'Personal y directo',
                'palabras_clave': ['personalizado', 'solo para ti', 'exclusivo', 'privado']
            },
            'redes_sociales': {
                'contexto': 'Contenido para redes sociales',
                'objetivo': 'Generar engagement y tráfico',
                'tono': 'Casual y viral',
                'palabras_clave': ['viral', 'trending', 'compartir', 'comunidad']
            },
            'webinar': {
                'contexto': 'Promoción de webinar gratuito',
                'objetivo': 'Generar leads calificados',
                'tono': 'Educativo y autoridad',
                'palabras_clave': ['gratis', 'expertos', 'insights', 'valor']
            },
            'black_friday': {
                'contexto': 'Evento de descuentos especiales',
                'objetivo': 'Maximizar ventas en tiempo limitado',
                'tono': 'Urgente y emocional',
                'palabras_clave': ['black friday', 'descuento', 'oferta', 'limitado']
            },
            'temporada_alta': {
                'contexto': 'Época de mayor demanda',
                'objetivo': 'Capitalizar el interés estacional',
                'tono': 'Oportunista y motivacional',
                'palabras_clave': ['temporada', 'momento perfecto', 'oportunidad', 'ahora']
            },
            'crisis_economica': {
                'contexto': 'Situación económica difícil',
                'objetivo': 'Posicionar como inversión inteligente',
                'tono': 'Empático y solucionador',
                'palabras_clave': ['inversión', 'futuro', 'seguridad', 'crecimiento']
            }
        }
        
        self.audiencias_especificas = {
            'principiantes': {
                'nivel': 'Básico',
                'dolor': 'No saben por dónde empezar',
                'solucion': 'Guía paso a paso',
                'tono': 'Paciente y educativo'
            },
            'intermedios': {
                'nivel': 'Intermedio',
                'dolor': 'Estancados en su crecimiento',
                'solucion': 'Técnicas avanzadas',
                'tono': 'Motivacional y técnico'
            },
            'avanzados': {
                'nivel': 'Avanzado',
                'dolor': 'Necesitan innovación',
                'solucion': 'Estrategias de vanguardia',
                'tono': 'Autoridad y exclusividad'
            },
            'empresarios': {
                'nivel': 'Ejecutivo',
                'dolor': 'Necesitan ROI inmediato',
                'solucion': 'Resultados medibles',
                'tono': 'Profesional y directo'
            },
            'freelancers': {
                'nivel': 'Independiente',
                'dolor': 'Necesitan diferenciarse',
                'solucion': 'Ventaja competitiva',
                'tono': 'Práctico y motivacional'
            }
        }
        
        self.industrias_especificas = {
            'ecommerce': {
                'dolor': 'Bajas conversiones online',
                'solucion': 'IA que convierte visitantes en clientes',
                'metricas': ['conversión', 'ROI', 'ventas']
            },
            'salud': {
                'dolor': 'Dificultad para llegar a pacientes',
                'solucion': 'IA para marketing médico ético',
                'metricas': ['leads', 'citas', 'pacientes']
            },
            'inmobiliaria': {
                'dolor': 'Lento proceso de ventas',
                'solucion': 'IA para acelerar ventas inmobiliarias',
                'metricas': ['leads', 'ventas', 'comisiones']
            },
            'educacion': {
                'dolor': 'Baja retención de estudiantes',
                'solucion': 'IA para engagement educativo',
                'metricas': ['matrículas', 'retención', 'satisfacción']
            },
            'servicios_profesionales': {
                'dolor': 'Dificultad para generar leads',
                'solucion': 'IA para atraer clientes ideales',
                'metricas': ['leads', 'consultas', 'clientes']
            }
        }

    def generar_anchor_por_caso_uso(self, caso_uso: str, cantidad: int = 10) -> List[Dict[str, Any]]:
        """Genera anchor texts específicos para un caso de uso"""
        if caso_uso not in self.casos_uso:
            raise ValueError(f"Caso de uso '{caso_uso}' no encontrado")
        
        caso = self.casos_uso[caso_uso]
        anchors = []
        
        formulas = [
            f"{{palabra_clave}} {{accion}} {{beneficio}} - {{urgencia}}",
            f"{{problema}} → {{solucion}} con {{palabra_clave}}",
            f"{{autoridad}} {{palabra_clave}} {{beneficio}} - {{garantia}}",
            f"{{urgencia}} {{palabra_clave}} {{beneficio}} - {{limitacion}}",
            f"{{social_proof}} {{palabra_clave}} {{transformacion}} - {{call_to_action}}"
        ]
        
        acciones = ['Domina', 'Aprende', 'Implementa', 'Revoluciona', 'Transforma', 'Multiplica']
        beneficios = ['ventas', 'conversiones', 'ingresos', 'resultados', 'crecimiento', 'éxito']
        urgencias = ['AHORA', 'HOY', 'YA', 'INMEDIATAMENTE', 'URGENTE']
        problemas = ['¿Estancado?', '¿Bajas ventas?', '¿Sin resultados?', '¿Perdiendo clientes?']
        soluciones = ['IA Marketing', 'Inteligencia Artificial', 'Marketing Automatizado']
        autoridades = ['Ex-Google', 'Ex-Facebook', 'Ex-Amazon', '10+ años experiencia']
        garantias = ['Garantía 100%', 'Sin riesgo', 'Devolución total', 'Satisfacción garantizada']
        limitaciones = ['Solo 24h', 'Últimas plazas', 'Edición limitada', 'Solo para miembros']
        social_proofs = ['50,000+ estudiantes', '10,000+ empresas', '95% de éxito', 'Miles de testimonios']
        transformaciones = ['de 0 a 100', 'de principiante a experto', 'de fracaso a éxito']
        call_to_actions = ['¡ÚNETE AHORA!', '¡EMPEZAR YA!', '¡NO TE PIERDAS!']
        
        for i in range(cantidad):
            formula = random.choice(formulas)
            
            # Reemplazar placeholders
            anchor = formula.format(
                palabra_clave=random.choice(caso['palabras_clave']),
                accion=random.choice(acciones),
                beneficio=random.choice(beneficios),
                urgencia=random.choice(urgencias),
                problema=random.choice(problemas),
                solucion=random.choice(soluciones),
                autoridad=random.choice(autoridades),
                garantia=random.choice(garantias),
                limitacion=random.choice(limitaciones),
                social_proof=random.choice(social_proofs),
                transformacion=random.choice(transformaciones),
                call_to_action=random.choice(call_to_actions)
            )
            
            anchors.append({
                'anchor_text': anchor,
                'caso_uso': caso_uso,
                'contexto': caso['contexto'],
                'objetivo': caso['objetivo'],
                'tono': caso['tono'],
                'longitud': len(anchor),
                'palabras_poder': self.contar_palabras_poder(anchor),
                'urgencia': self.calcular_urgencia(anchor),
                'beneficio': self.calcular_beneficio(anchor),
                'autoridad': self.calcular_autoridad(anchor)
            })
        
        return anchors

    def generar_anchor_por_audiencia(self, audiencia: str, cantidad: int = 10) -> List[Dict[str, Any]]:
        """Genera anchor texts específicos para una audiencia"""
        if audiencia not in self.audiencias_especificas:
            raise ValueError(f"Audiencia '{audiencia}' no encontrada")
        
        aud = self.audiencias_especificas[audiencia]
        anchors = []
        
        formulas_audiencia = {
            'principiantes': [
                "{{accion_basica}} {{concepto}} {{resultado_simple}} - {{guia}}",
                "{{problema_principiante}} → {{solucion_facil}} con {{herramienta}}",
                "{{empezar}} {{tema}} {{paso_a_paso}} - {{soporte}}"
            ],
            'intermedios': [
                "{{nivelar}} {{técnica_avanzada}} {{resultado_medible}} - {{metodologia}}",
                "{{problema_intermedio}} → {{solucion_profesional}} {{herramienta_avanzada}}",
                "{{optimizar}} {{proceso}} {{eficiencia}} - {{framework}}"
            ],
            'avanzados': [
                "{{innovar}} {{estrategia_cutting_edge}} {{ventaja_competitiva}} - {{exclusividad}}",
                "{{problema_complejo}} → {{solucion_revolucionaria}} {{tecnologia_avanzada}}",
                "{{liderar}} {{industria}} {{transformacion}} - {{autoridad}}"
            ],
            'empresarios': [
                "{{roi}} {{inversion}} {{retorno_medible}} - {{metodologia_probada}}",
                "{{problema_ejecutivo}} → {{solucion_estrategica}} {{impacto_negocio}}",
                "{{escalar}} {{operaciones}} {{crecimiento}} - {{sistema}}"
            ],
            'freelancers': [
                "{{diferenciarse}} {{servicio}} {{clientes_ideales}} - {{estrategia}}",
                "{{problema_freelancer}} → {{solucion_practica}} {{herramienta}}",
                "{{crecer}} {{negocio}} {{independencia}} - {{metodologia}}"
            ]
        }
        
        formulas = formulas_audiencia.get(audiencia, formulas_audiencia['principiantes'])
        
        # Palabras específicas por audiencia
        palabras_audiencia = {
            'principiantes': {
                'accion_basica': ['Aprende', 'Descubre', 'Comienza', 'Inicia'],
                'concepto': ['IA Marketing', 'Marketing Digital', 'Automatización'],
                'resultado_simple': ['desde cero', 'paso a paso', 'fácil'],
                'guia': ['Guía completa', 'Tutorial', 'Curso básico'],
                'problema_principiante': ['¿No sabes por dónde empezar?', '¿Confundido?', '¿Abrumado?'],
                'solucion_facil': ['IA Marketing simple', 'Solución fácil', 'Método probado'],
                'herramienta': ['herramientas', 'plataformas', 'software'],
                'empezar': ['Empieza', 'Comienza', 'Inicia'],
                'tema': ['con IA Marketing', 'en Marketing Digital', 'con Automatización'],
                'paso_a_paso': ['paso a paso', 'desde cero', 'sin complicaciones'],
                'soporte': ['Soporte 24/7', 'Comunidad', 'Mentoría']
            },
            'intermedios': {
                'nivelar': ['Nivela', 'Optimiza', 'Mejora', 'Acelera'],
                'técnica_avanzada': ['técnicas avanzadas', 'estrategias profesionales', 'métodos probados'],
                'resultado_medible': ['resultados medibles', 'ROI comprobado', 'crecimiento real'],
                'metodologia': ['Metodología probada', 'Framework', 'Sistema'],
                'problema_intermedio': ['¿Estancado?', '¿Sin crecimiento?', '¿Necesitas más?'],
                'solucion_profesional': ['IA Marketing avanzado', 'Estrategias profesionales', 'Técnicas expertas'],
                'herramienta_avanzada': ['herramientas avanzadas', 'plataformas profesionales', 'software especializado'],
                'optimizar': ['Optimiza', 'Mejora', 'Acelera'],
                'proceso': ['tu proceso', 'tu estrategia', 'tu operación'],
                'eficiencia': ['eficiencia', 'productividad', 'rendimiento'],
                'framework': ['Framework', 'Metodología', 'Sistema']
            },
            'avanzados': {
                'innovar': ['Innovar', 'Revolucionar', 'Transformar', 'Liderar'],
                'estrategia_cutting_edge': ['estrategias de vanguardia', 'técnicas cutting-edge', 'métodos innovadores'],
                'ventaja_competitiva': ['ventaja competitiva', 'diferenciación', 'liderazgo'],
                'exclusividad': ['Exclusivo', 'Limitado', 'VIP', 'Premium'],
                'problema_complejo': ['¿Necesitas innovación?', '¿Quieres liderar?', '¿Buscas exclusividad?'],
                'solucion_revolucionaria': ['IA Marketing revolucionario', 'Estrategias de vanguardia', 'Técnicas exclusivas'],
                'tecnologia_avanzada': ['tecnología avanzada', 'IA de última generación', 'herramientas exclusivas'],
                'liderar': ['Lidera', 'Domina', 'Revoluciona', 'Transforma'],
                'industria': ['tu industria', 'el mercado', 'la competencia'],
                'transformacion': ['transformación', 'revolución', 'innovación'],
                'autoridad': ['Autoridad', 'Liderazgo', 'Expertise', 'Mastery']
            },
            'empresarios': {
                'roi': ['ROI', 'Retorno', 'Inversión', 'Rentabilidad'],
                'inversion': ['inversión inteligente', 'inversión estratégica', 'inversión rentable'],
                'retorno_medible': ['retorno medible', 'ROI comprobado', 'rentabilidad real'],
                'metodologia_probada': ['Metodología probada', 'Sistema validado', 'Framework empresarial'],
                'problema_ejecutivo': ['¿Necesitas ROI?', '¿Buscas crecimiento?', '¿Quieres escalar?'],
                'solucion_estrategica': ['IA Marketing estratégico', 'Solución empresarial', 'Estrategia corporativa'],
                'impacto_negocio': ['impacto en el negocio', 'crecimiento empresarial', 'escalabilidad'],
                'escalar': ['Escala', 'Crecimiento', 'Expansión', 'Desarrollo'],
                'operaciones': ['tus operaciones', 'tu negocio', 'tu empresa'],
                'crecimiento': ['crecimiento', 'escalabilidad', 'expansión'],
                'sistema': ['Sistema', 'Framework', 'Metodología', 'Estrategia']
            },
            'freelancers': {
                'diferenciarse': ['Diferenciarse', 'Destacar', 'Sobresalir', 'Competir'],
                'servicio': ['tu servicio', 'tu oferta', 'tu propuesta'],
                'clientes_ideales': ['clientes ideales', 'clientes premium', 'clientes de alto valor'],
                'estrategia': ['Estrategia', 'Método', 'Sistema', 'Framework'],
                'problema_freelancer': ['¿Necesitas diferenciarte?', '¿Quieres más clientes?', '¿Buscas crecimiento?'],
                'solucion_practica': ['IA Marketing práctico', 'Solución real', 'Método efectivo'],
                'herramienta': ['herramientas', 'plataformas', 'software'],
                'crecer': ['Crecer', 'Desarrollar', 'Expandir', 'Escalar'],
                'negocio': ['tu negocio', 'tu práctica', 'tu servicio'],
                'independencia': ['independencia', 'libertad', 'autonomía'],
                'metodologia': ['Metodología', 'Sistema', 'Framework', 'Estrategia']
            }
        }
        
        palabras = palabras_audiencia.get(audiencia, palabras_audiencia['principiantes'])
        
        for i in range(cantidad):
            formula = random.choice(formulas)
            
            # Reemplazar placeholders con palabras específicas de la audiencia
            anchor = formula
            for placeholder, opciones in palabras.items():
                if f"{{{{{placeholder}}}}}" in anchor:
                    anchor = anchor.replace(f"{{{{{placeholder}}}}}", random.choice(opciones))
            
            anchors.append({
                'anchor_text': anchor,
                'audiencia': audiencia,
                'nivel': aud['nivel'],
                'dolor': aud['dolor'],
                'solucion': aud['solucion'],
                'tono': aud['tono'],
                'longitud': len(anchor),
                'palabras_poder': self.contar_palabras_poder(anchor),
                'urgencia': self.calcular_urgencia(anchor),
                'beneficio': self.calcular_beneficio(anchor),
                'autoridad': self.calcular_autoridad(anchor)
            })
        
        return anchors

    def generar_anchor_por_industria(self, industria: str, cantidad: int = 10) -> List[Dict[str, Any]]:
        """Genera anchor texts específicos para una industria"""
        if industria not in self.industrias_especificas:
            raise ValueError(f"Industria '{industria}' no encontrada")
        
        ind = self.industrias_especificas[industria]
        anchors = []
        
        formulas_industria = {
            'ecommerce': [
                "{{accion}} {{conversion}} {{ecommerce}} {{resultado}} - {{herramienta}}",
                "{{problema_ecommerce}} → {{solucion_ia}} {{metricas}}",
                "{{multiplicar}} {{ventas}} {{online}} {{estrategia}} - {{garantia}}"
            ],
            'salud': [
                "{{accion}} {{marketing_medico}} {{pacientes}} {{resultado}} - {{etica}}",
                "{{problema_salud}} → {{solucion_ia}} {{compliance}}",
                "{{atraer}} {{leads_medicos}} {{calificados}} {{metodologia}} - {{experiencia}}"
            ],
            'inmobiliaria': [
                "{{accion}} {{ventas_inmobiliarias}} {{propiedades}} {{resultado}} - {{tecnologia}}",
                "{{problema_inmobiliaria}} → {{solucion_ia}} {{aceleracion}}",
                "{{vender}} {{más_rapido}} {{propiedades}} {{estrategia}} - {{sistema}}"
            ],
            'educacion': [
                "{{accion}} {{engagement_educativo}} {{estudiantes}} {{resultado}} - {{metodologia}}",
                "{{problema_educacion}} → {{solucion_ia}} {{retencion}}",
                "{{mejorar}} {{experiencia_estudiante}} {{satisfaccion}} {{estrategia}} - {{herramienta}}"
            ],
            'servicios_profesionales': [
                "{{accion}} {{leads}} {{profesionales}} {{resultado}} - {{herramienta}}",
                "{{problema_profesional}} → {{solucion_ia}} {{metodologia}}",
                "{{crecer}} {{negocio}} {{profesional}} {{estrategia}} - {{sistema}}"
            ]
        }
        
        formulas = formulas_industria.get(industria, formulas_industria['ecommerce'])
        
        # Palabras específicas por industria
        palabras_industria = {
            'ecommerce': {
                'accion': ['Multiplica', 'Aumenta', 'Optimiza', 'Mejora'],
                'conversion': ['conversiones', 'ventas', 'ingresos', 'ROI'],
                'ecommerce': ['e-commerce', 'tienda online', 'comercio electrónico'],
                'resultado': ['exponencialmente', 'significativamente', 'drásticamente'],
                'herramienta': ['IA Marketing', 'Automatización', 'Inteligencia Artificial'],
                'problema_ecommerce': ['¿Bajas conversiones?', '¿Pocas ventas?', '¿Carrito abandonado?'],
                'solucion_ia': ['IA Marketing', 'Automatización', 'Inteligencia Artificial'],
                'metricas': ['conversión', 'ROI', 'ventas'],
                'multiplicar': ['Multiplica', 'Aumenta', 'Optimiza'],
                'ventas': ['ventas', 'conversiones', 'ingresos'],
                'online': ['online', 'digital', 'e-commerce'],
                'estrategia': ['Estrategia', 'Sistema', 'Metodología'],
                'garantia': ['Garantía', 'Sin riesgo', 'Satisfacción']
            },
            'salud': {
                'accion': ['Atrae', 'Genera', 'Convierte', 'Multiplica'],
                'marketing_medico': ['marketing médico', 'marketing sanitario', 'marketing de salud'],
                'pacientes': ['pacientes', 'clientes', 'usuarios'],
                'resultado': ['calificados', 'ideales', 'de alto valor'],
                'etica': ['Ético', 'Compliant', 'Regulatorio'],
                'problema_salud': ['¿Dificultad para llegar a pacientes?', '¿Bajos leads?', '¿Poca visibilidad?'],
                'solucion_ia': ['IA Marketing', 'Automatización', 'Inteligencia Artificial'],
                'compliance': ['Compliance', 'Regulatorio', 'Ético'],
                'atraer': ['Atrae', 'Genera', 'Convierte'],
                'leads_medicos': ['leads médicos', 'pacientes', 'clientes'],
                'calificados': ['calificados', 'ideales', 'de alto valor'],
                'metodologia': ['Metodología', 'Sistema', 'Framework'],
                'experiencia': ['Experiencia', 'Expertise', 'Conocimiento']
            },
            'inmobiliaria': {
                'accion': ['Acelera', 'Optimiza', 'Mejora', 'Multiplica'],
                'ventas_inmobiliarias': ['ventas inmobiliarias', 'ventas de propiedades', 'transacciones'],
                'propiedades': ['propiedades', 'inmuebles', 'casas'],
                'resultado': ['más rápido', 'eficientemente', 'exitosamente'],
                'tecnologia': ['Tecnología', 'IA', 'Automatización'],
                'problema_inmobiliaria': ['¿Lento proceso de ventas?', '¿Pocas transacciones?', '¿Bajos leads?'],
                'solucion_ia': ['IA Marketing', 'Automatización', 'Inteligencia Artificial'],
                'aceleracion': ['Aceleración', 'Eficiencia', 'Optimización'],
                'vender': ['Vende', 'Transacciona', 'Comercializa'],
                'más_rapido': ['más rápido', 'eficientemente', 'exitosamente'],
                'estrategia': ['Estrategia', 'Sistema', 'Metodología'],
                'sistema': ['Sistema', 'Framework', 'Metodología']
            },
            'educacion': {
                'accion': ['Mejora', 'Optimiza', 'Aumenta', 'Multiplica'],
                'engagement_educativo': ['engagement educativo', 'participación', 'interacción'],
                'estudiantes': ['estudiantes', 'alumnos', 'usuarios'],
                'resultado': ['significativamente', 'drásticamente', 'exponencialmente'],
                'metodologia': ['Metodología', 'Sistema', 'Framework'],
                'problema_educacion': ['¿Baja retención?', '¿Poco engagement?', '¿Abandono?'],
                'solucion_ia': ['IA Marketing', 'Automatización', 'Inteligencia Artificial'],
                'retencion': ['Retención', 'Engagement', 'Participación'],
                'mejorar': ['Mejora', 'Optimiza', 'Aumenta'],
                'experiencia_estudiante': ['experiencia del estudiante', 'satisfacción', 'engagement'],
                'satisfaccion': ['satisfacción', 'retención', 'éxito'],
                'estrategia': ['Estrategia', 'Sistema', 'Metodología'],
                'herramienta': ['Herramienta', 'Plataforma', 'Sistema']
            },
            'servicios_profesionales': {
                'accion': ['Atrae', 'Genera', 'Convierte', 'Multiplica'],
                'leads': ['leads', 'clientes', 'consultas', 'oportunidades'],
                'profesionales': ['profesionales', 'servicios', 'consultoría', 'asesoría'],
                'resultado': ['calificados', 'ideales', 'de alto valor', 'premium'],
                'herramienta': ['IA Marketing', 'Automatización', 'Inteligencia Artificial'],
                'problema_profesional': ['¿Necesitas más clientes?', '¿Buscas leads?', '¿Quieres crecer?'],
                'solucion_ia': ['IA Marketing', 'Automatización', 'Inteligencia Artificial'],
                'metodologia': ['Metodología', 'Sistema', 'Framework', 'Estrategia']
            }
        }
        
        palabras = palabras_industria.get(industria, palabras_industria['ecommerce'])
        
        for i in range(cantidad):
            formula = random.choice(formulas)
            
            # Reemplazar placeholders con palabras específicas de la industria
            anchor = formula
            for placeholder, opciones in palabras.items():
                if f"{{{{{placeholder}}}}}" in anchor:
                    anchor = anchor.replace(f"{{{{{placeholder}}}}}", random.choice(opciones))
            
            anchors.append({
                'anchor_text': anchor,
                'industria': industria,
                'dolor': ind['dolor'],
                'solucion': ind['solucion'],
                'metricas': ind['metricas'],
                'longitud': len(anchor),
                'palabras_poder': self.contar_palabras_poder(anchor),
                'urgencia': self.calcular_urgencia(anchor),
                'beneficio': self.calcular_beneficio(anchor),
                'autoridad': self.calcular_autoridad(anchor)
            })
        
        return anchors

    def contar_palabras_poder(self, texto: str) -> int:
        """Cuenta las palabras de poder en el texto"""
        palabras_poder = [
            'gratis', 'nuevo', 'exclusivo', 'limitado', 'urgente', 'ahora', 'ya',
            'revolucionario', 'innovador', 'avanzado', 'profesional', 'experto',
            'garantía', 'sin riesgo', 'resultados', 'éxito', 'crecimiento',
            'multiplica', 'aumenta', 'optimiza', 'mejora', 'domina', 'aprende'
        ]
        return sum(1 for palabra in palabras_poder if palabra.lower() in texto.lower())

    def calcular_urgencia(self, texto: str) -> int:
        """Calcula el nivel de urgencia del texto (0-10)"""
        palabras_urgencia = ['ahora', 'ya', 'urgente', 'inmediatamente', 'hoy', 'rápido', 'pronto']
        return min(10, sum(1 for palabra in palabras_urgencia if palabra.lower() in texto.lower()) * 2)

    def calcular_beneficio(self, texto: str) -> int:
        """Calcula el nivel de beneficio del texto (0-10)"""
        palabras_beneficio = ['resultados', 'éxito', 'crecimiento', 'ventas', 'conversiones', 'ingresos', 'roi']
        return min(10, sum(1 for palabra in palabras_beneficio if palabra.lower() in texto.lower()) * 2)

    def calcular_autoridad(self, texto: str) -> int:
        """Calcula el nivel de autoridad del texto (0-10)"""
        palabras_autoridad = ['expert', 'profesional', 'avanzado', 'certificado', 'oficial', 'autoridad']
        return min(10, sum(1 for palabra in palabras_autoridad if palabra.lower() in texto.lower()) * 2)

    def generar_casos_uso_completos(self) -> Dict[str, Any]:
        """Genera todos los casos de uso con sus respectivos anchor texts"""
        resultados = {
            'casos_uso': {},
            'audiencias': {},
            'industrias': {},
            'resumen': {
                'total_casos_uso': len(self.casos_uso),
                'total_audiencias': len(self.audiencias_especificas),
                'total_industrias': len(self.industrias_especificas),
                'fecha_generacion': datetime.now().isoformat()
            }
        }
        
        # Generar por casos de uso
        for caso_uso in self.casos_uso.keys():
            resultados['casos_uso'][caso_uso] = self.generar_anchor_por_caso_uso(caso_uso, 15)
        
        # Generar por audiencias
        for audiencia in self.audiencias_especificas.keys():
            resultados['audiencias'][audiencia] = self.generar_anchor_por_audiencia(audiencia, 15)
        
        # Generar por industrias
        for industria in self.industrias_especificas.keys():
            resultados['industrias'][industria] = self.generar_anchor_por_industria(industria, 15)
        
        return resultados

    def exportar_casos_uso(self, resultados: Dict[str, Any]) -> str:
        """Exporta los casos de uso en JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"casos_uso_anchor_texts_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        
        return filename

    def generar_documentacion_casos_uso(self, resultados: Dict[str, Any]) -> str:
        """Genera documentación en Markdown para los casos de uso"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"documentacion_casos_uso_{timestamp}.md"
        
        md_content = f"""# 📋 DOCUMENTACIÓN COMPLETA - CASOS DE USO ANCHOR TEXTS IA MARKETING

## 📊 **RESUMEN EJECUTIVO**
- **Total de Casos de Uso**: {resultados['resumen']['total_casos_uso']}
- **Total de Audiencias**: {resultados['resumen']['total_audiencias']}
- **Total de Industrias**: {resultados['resumen']['total_industrias']}
- **Fecha de Generación**: {resultados['resumen']['fecha_generacion']}

---

## 🎯 **CASOS DE USO ESPECÍFICOS**

"""
        
        # Documentar casos de uso
        for caso_uso, anchors in resultados['casos_uso'].items():
            caso_info = self.casos_uso[caso_uso]
            md_content += f"""### **{caso_uso.upper().replace('_', ' ')}**
- **Contexto**: {caso_info['contexto']}
- **Objetivo**: {caso_info['objetivo']}
- **Tono**: {caso_info['tono']}
- **Palabras Clave**: {', '.join(caso_info['palabras_clave'])}

**Anchor Texts Generados:**
"""
            for i, anchor in enumerate(anchors, 1):
                md_content += f"{i}. {anchor['anchor_text']}\n"
            
            md_content += "\n---\n\n"
        
        # Documentar audiencias
        md_content += "## 👥 **AUDIENCIAS ESPECÍFICAS**\n\n"
        for audiencia, anchors in resultados['audiencias'].items():
            aud_info = self.audiencias_especificas[audiencia]
            md_content += f"""### **{audiencia.upper()}**
- **Nivel**: {aud_info['nivel']}
- **Dolor**: {aud_info['dolor']}
- **Solución**: {aud_info['solucion']}
- **Tono**: {aud_info['tono']}

**Anchor Texts Generados:**
"""
            for i, anchor in enumerate(anchors, 1):
                md_content += f"{i}. {anchor['anchor_text']}\n"
            
            md_content += "\n---\n\n"
        
        # Documentar industrias
        md_content += "## 🏭 **INDUSTRIAS ESPECÍFICAS**\n\n"
        for industria, anchors in resultados['industrias'].items():
            ind_info = self.industrias_especificas[industria]
            md_content += f"""### **{industria.upper()}**
- **Dolor**: {ind_info['dolor']}
- **Solución**: {ind_info['solucion']}
- **Métricas**: {', '.join(ind_info['metricas'])}

**Anchor Texts Generados:**
"""
            for i, anchor in enumerate(anchors, 1):
                md_content += f"{i}. {anchor['anchor_text']}\n"
            
            md_content += "\n---\n\n"
        
        md_content += """## 🎯 **INSTRUCCIONES DE USO**

### **1. Para Casos de Uso Específicos**
- Usa los anchor texts según el contexto de tu campaña
- Adapta el tono a tu audiencia objetivo
- Personaliza las palabras clave según tu marca

### **2. Para Audiencias Específicas**
- Selecciona el nivel de experiencia apropiado
- Adapta el lenguaje al dolor específico
- Enfócate en la solución que necesitan

### **3. Para Industrias Específicas**
- Usa la terminología de la industria
- Enfócate en las métricas relevantes
- Adapta el beneficio al contexto específico

## 🚀 **PRÓXIMOS PASOS**
1. **Selecciona** los casos de uso más relevantes para tu negocio
2. **Personaliza** los anchor texts según tu marca y audiencia
3. **Implementa** en tus campañas de marketing
4. **Monitorea** el rendimiento y optimiza continuamente
5. **Escala** los casos de uso más exitosos

---

*Documentación generada automáticamente por el Sistema de Anchor Texts IA Marketing*
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return filename

def main():
    """Función principal"""
    print("📋 GENERADOR DE CASOS DE USO ESPECÍFICOS - ANCHOR TEXTS IA MARKETING")
    print("=" * 70)
    
    generador = GeneradorCasosUsoAnchorTexts()
    
    print("🔄 Generando casos de uso específicos...")
    resultados = generador.generar_casos_uso_completos()
    
    print("💾 Exportando resultados en JSON...")
    json_file = generador.exportar_casos_uso(resultados)
    
    print("📚 Generando documentación...")
    md_file = generador.generar_documentacion_casos_uso(resultados)
    
    print(f"\n✅ Generación completada:")
    print(f"   • Casos de uso: {resultados['resumen']['total_casos_uso']}")
    print(f"   • Audiencias: {resultados['resumen']['total_audiencias']}")
    print(f"   • Industrias: {resultados['resumen']['total_industrias']}")
    
    print(f"\n📁 Archivos generados:")
    print(f"   • JSON: {json_file}")
    print(f"   • Documentación: {md_file}")
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Revisa la documentación para entender los casos de uso")
    print("2. Selecciona los casos más relevantes para tu negocio")
    print("3. Personaliza los anchor texts según tu marca")
    print("4. Implementa en tus campañas de marketing")
    print("5. Monitorea el rendimiento y optimiza")

if __name__ == "__main__":
    main()
