#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Personalizado - Anchor Texts IA Marketing
==================================================

Este script genera anchor texts altamente personalizados basándose en
perfiles específicos de usuario, industria y objetivos de marketing.

Funcionalidades:
- Perfiles de usuario personalizados
- Generación por industria específica
- Adaptación por objetivo de marketing
- Personalización por audiencia
- Análisis de preferencias
"""

import random
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple
from collections import Counter

class GeneradorPersonalizadoAnchorTexts:
    def __init__(self):
        self.palabras_clave_base = [
            "curso IA marketing", "inteligencia artificial marketing", "marketing digital IA",
            "curso marketing automatizado", "IA aplicada marketing", "machine learning marketing"
        ]
        
        # Perfiles de usuario
        self.perfiles_usuario = {
            'principiante': {
                'descripcion': 'Personas sin experiencia en marketing digital',
                'caracteristicas': {
                    'nivel_experiencia': 'básico',
                    'tiempo_disponible': 'alto',
                    'presupuesto': 'bajo',
                    'objetivos': ['aprender', 'entender', 'comenzar'],
                    'dolor_points': ['confusión', 'sobrecarga', 'complejidad'],
                    'palabras_clave': ['básico', 'principiante', 'desde cero', 'fácil', 'simple'],
                    'tono_preferido': 'educativo',
                    'beneficios_prioritarios': ['aprendizaje', 'comprensión', 'fundamentos']
                }
            },
            'intermedio': {
                'descripcion': 'Personas con experiencia básica en marketing',
                'caracteristicas': {
                    'nivel_experiencia': 'intermedio',
                    'tiempo_disponible': 'medio',
                    'presupuesto': 'medio',
                    'objetivos': ['mejorar', 'optimizar', 'escalar'],
                    'dolor_points': ['estancamiento', 'ineficiencia', 'competencia'],
                    'palabras_clave': ['avanzado', 'profesional', 'optimización', 'estrategia'],
                    'tono_preferido': 'profesional',
                    'beneficios_prioritarios': ['mejora', 'optimización', 'resultados']
                }
            },
            'avanzado': {
                'descripcion': 'Profesionales experimentados en marketing',
                'caracteristicas': {
                    'nivel_experiencia': 'avanzado',
                    'tiempo_disponible': 'bajo',
                    'presupuesto': 'alto',
                    'objetivos': ['dominar', 'liderar', 'innovar'],
                    'dolor_points': ['complejidad', 'cambio', 'competencia'],
                    'palabras_clave': ['expert', 'master', 'líder', 'innovador', 'pionero'],
                    'tono_preferido': 'autoritario',
                    'beneficios_prioritarios': ['dominio', 'liderazgo', 'innovación']
                }
            },
            'empresario': {
                'descripcion': 'Dueños de negocio y empresarios',
                'caracteristicas': {
                    'nivel_experiencia': 'variado',
                    'tiempo_disponible': 'muy_bajo',
                    'presupuesto': 'alto',
                    'objetivos': ['crecer', 'escalar', 'automatizar'],
                    'dolor_points': ['tiempo', 'recursos', 'competencia'],
                    'palabras_clave': ['negocio', 'empresa', 'crecimiento', 'escalabilidad'],
                    'tono_preferido': 'directo',
                    'beneficios_prioritarios': ['crecimiento', 'ROI', 'automatización']
                }
            },
            'freelancer': {
                'descripcion': 'Freelancers y consultores independientes',
                'caracteristicas': {
                    'nivel_experiencia': 'intermedio',
                    'tiempo_disponible': 'medio',
                    'presupuesto': 'bajo',
                    'objetivos': ['clients', 'ingresos', 'reputación'],
                    'dolor_points': ['clientes', 'precios', 'competencia'],
                    'palabras_clave': ['freelancer', 'consultor', 'independiente', 'cliente'],
                    'tono_preferido': 'personal',
                    'beneficios_prioritarios': ['clientes', 'ingresos', 'reputación']
                }
            }
        }
        
        # Industrias específicas
        self.industrias = {
            'ecommerce': {
                'descripcion': 'Comercio electrónico y ventas online',
                'caracteristicas': {
                    'palabras_clave': ['ecommerce', 'ventas online', 'tienda virtual', 'conversión'],
                    'objetivos': ['ventas', 'conversión', 'tráfico', 'ROI'],
                    'dolor_points': ['abandono carrito', 'baja conversión', 'competencia'],
                    'tono_preferido': 'comercial',
                    'beneficios_prioritarios': ['ventas', 'conversión', 'ingresos']
                }
            },
            'salud': {
                'descripcion': 'Sector salud y bienestar',
                'caracteristicas': {
                    'palabras_clave': ['salud', 'bienestar', 'médico', 'paciente', 'tratamiento'],
                    'objetivos': ['pacientes', 'confianza', 'reputación', 'cuidado'],
                    'dolor_points': ['confianza', 'regulaciones', 'competencia'],
                    'tono_preferido': 'empático',
                    'beneficios_prioritarios': ['confianza', 'cuidado', 'bienestar']
                }
            },
            'educacion': {
                'descripcion': 'Educación y formación',
                'caracteristicas': {
                    'palabras_clave': ['educación', 'aprendizaje', 'curso', 'formación', 'conocimiento'],
                    'objetivos': ['estudiantes', 'aprendizaje', 'certificación', 'desarrollo'],
                    'dolor_points': ['retención', 'engagement', 'competencia'],
                    'tono_preferido': 'educativo',
                    'beneficios_prioritarios': ['aprendizaje', 'desarrollo', 'conocimiento']
                }
            },
            'tecnologia': {
                'descripcion': 'Tecnología y software',
                'caracteristicas': {
                    'palabras_clave': ['tecnología', 'software', 'innovación', 'digital', 'automatización'],
                    'objetivos': ['innovación', 'eficiencia', 'automatización', 'escalabilidad'],
                    'dolor_points': ['complejidad', 'cambio', 'integración'],
                    'tono_preferido': 'técnico',
                    'beneficios_prioritarios': ['innovación', 'eficiencia', 'automatización']
                }
            },
            'servicios_profesionales': {
                'descripcion': 'Servicios profesionales y consultoría',
                'caracteristicas': {
                    'palabras_clave': ['servicios', 'consultoría', 'profesional', 'experto', 'asesoría'],
                    'objetivos': ['clientes', 'reputación', 'ingresos', 'crecimiento'],
                    'dolor_points': ['clientes', 'competencia', 'precios'],
                    'tono_preferido': 'profesional',
                    'beneficios_prioritarios': ['clientes', 'reputación', 'crecimiento']
                }
            }
        }
        
        # Objetivos de marketing
        self.objetivos_marketing = {
            'awareness': {
                'descripcion': 'Generar conciencia de marca',
                'caracteristicas': {
                    'palabras_clave': ['descubre', 'conoce', 'explora', 'nuevo', 'innovador'],
                    'tono_preferido': 'informativo',
                    'beneficios_prioritarios': ['conocimiento', 'visibilidad', 'reconocimiento']
                }
            },
            'consideration': {
                'descripcion': 'Fomentar consideración de compra',
                'caracteristicas': {
                    'palabras_clave': ['compara', 'evalúa', 'considera', 'opciones', 'alternativas'],
                    'tono_preferido': 'persuasivo',
                    'beneficios_prioritarios': ['comparación', 'evaluación', 'decisión']
                }
            },
            'conversion': {
                'descripcion': 'Generar conversiones y ventas',
                'caracteristicas': {
                    'palabras_clave': ['compra', 'adquiere', 'obtén', 'ahora', 'urgente'],
                    'tono_preferido': 'urgente',
                    'beneficios_prioritarios': ['venta', 'conversión', 'ingreso']
                }
            },
            'retention': {
                'descripcion': 'Retener clientes existentes',
                'caracteristicas': {
                    'palabras_clave': ['fideliza', 'mantén', 'continúa', 'renueva', 'mejora'],
                    'tono_preferido': 'personal',
                    'beneficios_prioritarios': ['fidelidad', 'retención', 'satisfacción']
                }
            }
        }

    def generar_perfil_personalizado(self, perfil_usuario: str, industria: str, 
                                   objetivo: str, preferencias: Dict[str, Any] = None) -> Dict[str, Any]:
        """Genera un perfil personalizado para generación de anchor texts"""
        if perfil_usuario not in self.perfiles_usuario:
            raise ValueError(f"Perfil de usuario '{perfil_usuario}' no encontrado")
        
        if industria not in self.industrias:
            raise ValueError(f"Industria '{industria}' no encontrada")
        
        if objetivo not in self.objetivos_marketing:
            raise ValueError(f"Objetivo '{objetivo}' no encontrado")
        
        # Combinar características
        perfil = self.perfiles_usuario[perfil_usuario]
        industria_info = self.industrias[industria]
        objetivo_info = self.objetivos_marketing[objetivo]
        
        # Crear perfil personalizado
        perfil_personalizado = {
            'perfil_usuario': perfil_usuario,
            'industria': industria,
            'objetivo_marketing': objetivo,
            'caracteristicas_combinadas': {
                'palabras_clave': list(set(
                    perfil['caracteristicas']['palabras_clave'] +
                    industria_info['caracteristicas']['palabras_clave'] +
                    objetivo_info['caracteristicas']['palabras_clave']
                )),
                'objetivos': perfil['caracteristicas']['objetivos'] + industria_info['caracteristicas']['objetivos'],
                'dolor_points': perfil['caracteristicas']['dolor_points'] + industria_info['caracteristicas']['dolor_points'],
                'tono_preferido': self._determinar_tono_optimo(
                    perfil['caracteristicas']['tono_preferido'],
                    industria_info['caracteristicas']['tono_preferido'],
                    objetivo_info['caracteristicas']['tono_preferido']
                ),
                'beneficios_prioritarios': list(set(
                    perfil['caracteristicas']['beneficios_prioritarios'] +
                    industria_info['caracteristicas']['beneficios_prioritarios'] +
                    objetivo_info['caracteristicas']['beneficios_prioritarios']
                ))
            },
            'preferencias_personalizadas': preferencias or {},
            'fecha_creacion': datetime.now().isoformat()
        }
        
        return perfil_personalizado

    def _determinar_tono_optimo(self, tono_perfil: str, tono_industria: str, tono_objetivo: str) -> str:
        """Determina el tono óptimo combinando los diferentes tonos"""
        tonos = [tono_perfil, tono_industria, tono_objetivo]
        
        # Priorizar tono del objetivo de marketing
        if tono_objetivo in ['urgente', 'persuasivo']:
            return tono_objetivo
        
        # Luego priorizar tono de la industria
        if tono_industria in ['empático', 'técnico', 'comercial']:
            return tono_industria
        
        # Finalmente usar tono del perfil
        return tono_perfil

    def generar_anchor_texts_personalizados(self, perfil: Dict[str, Any], 
                                          cantidad: int = 20) -> List[Dict[str, Any]]:
        """Genera anchor texts personalizados basados en el perfil"""
        caracteristicas = perfil['caracteristicas_combinadas']
        
        # Plantillas personalizadas
        plantillas = self._generar_plantillas_personalizadas(caracteristicas)
        
        anchor_texts = []
        
        for i in range(cantidad):
            # Seleccionar palabra clave base
            palabra_clave = random.choice(self.palabras_clave_base)
            
            # Seleccionar plantilla
            plantilla = random.choice(plantillas)
            
            # Seleccionar elementos personalizados
            elemento_personalizado = random.choice(caracteristicas['palabras_clave'])
            beneficio = random.choice(caracteristicas['beneficios_prioritarios'])
            objetivo = random.choice(caracteristicas['objetivos'])
            
            # Generar anchor text
            anchor_text = plantilla.replace('{palabra_clave}', palabra_clave)
            anchor_text = anchor_text.replace('{elemento_personalizado}', elemento_personalizado)
            anchor_text = anchor_text.replace('{beneficio}', beneficio)
            anchor_text = anchor_text.replace('{objetivo}', objetivo)
            
            # Analizar características
            caracteristicas_anchor = self._analizar_caracteristicas_personalizadas(
                anchor_text, caracteristicas
            )
            
            anchor_texts.append({
                'id': f"personalizado_{i+1:03d}",
                'anchor_text': anchor_text,
                'palabra_clave': palabra_clave,
                'perfil_usuario': perfil['perfil_usuario'],
                'industria': perfil['industria'],
                'objetivo_marketing': perfil['objetivo_marketing'],
                'caracteristicas': caracteristicas_anchor,
                'fecha_generacion': datetime.now().isoformat()
            })
        
        return anchor_texts

    def _generar_plantillas_personalizadas(self, caracteristicas: Dict[str, Any]) -> List[str]:
        """Genera plantillas personalizadas basadas en las características"""
        tono = caracteristicas['tono_preferido']
        
        plantillas_base = {
            'educativo': [
                "Aprende {palabra_clave} - {elemento_personalizado}",
                "Curso {palabra_clave} para {elemento_personalizado}",
                "Guía {palabra_clave} - {beneficio}",
                "Descubre {palabra_clave} con {elemento_personalizado}"
            ],
            'profesional': [
                "Masterclass {palabra_clave} - {elemento_personalizado}",
                "Certificación {palabra_clave} {elemento_personalizado}",
                "Estrategia {palabra_clave} para {objetivo}",
                "Profesional {palabra_clave} - {beneficio}"
            ],
            'comercial': [
                "Vende más con {palabra_clave} - {elemento_personalizado}",
                "Aumenta {beneficio} con {palabra_clave}",
                "Multiplica {objetivo} - {palabra_clave}",
                "ROI garantizado: {palabra_clave} {elemento_personalizado}"
            ],
            'empático': [
                "Transforma {objetivo} con {palabra_clave}",
                "Mejora {beneficio} - {palabra_clave}",
                "Cuidado personalizado: {palabra_clave}",
                "Bienestar {elemento_personalizado} - {palabra_clave}"
            ],
            'técnico': [
                "Sistema {palabra_clave} - {elemento_personalizado}",
                "Tecnología {palabra_clave} para {objetivo}",
                "Innovación {palabra_clave} - {beneficio}",
                "Solución {elemento_personalizado} con {palabra_clave}"
            ],
            'urgente': [
                "¡Última oportunidad! {palabra_clave} - {elemento_personalizado}",
                "Solo hoy: {palabra_clave} {beneficio}",
                "¡No te pierdas! {palabra_clave} {objetivo}",
                "Oferta limitada: {palabra_clave} {elemento_personalizado}"
            ],
            'persuasivo': [
                "Descubre por qué {palabra_clave} es {elemento_personalizado}",
                "La razón #1 para usar {palabra_clave}",
                "¿Por qué {palabra_clave}? {beneficio}",
                "El secreto de {objetivo}: {palabra_clave}"
            ],
            'personal': [
                "Tu historia con {palabra_clave} - {elemento_personalizado}",
                "Personaliza {palabra_clave} para {objetivo}",
                "A tu medida: {palabra_clave} {beneficio}",
                "Exclusivo para ti: {palabra_clave} {elemento_personalizado}"
            ],
            'autoritario': [
                "Domina {palabra_clave} - {elemento_personalizado}",
                "Líder en {palabra_clave}: {beneficio}",
                "El estándar de {palabra_clave} {objetivo}",
                "Referencia en {elemento_personalizado}: {palabra_clave}"
            ],
            'directo': [
                "{palabra_clave} - {beneficio}",
                "{objetivo} con {palabra_clave}",
                "{elemento_personalizado}: {palabra_clave}",
                "{palabra_clave} {elemento_personalizado} - {beneficio}"
            ]
        }
        
        return plantillas_base.get(tono, plantillas_base['directo'])

    def _analizar_caracteristicas_personalizadas(self, anchor_text: str, 
                                               caracteristicas: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza las características del anchor text personalizado"""
        texto_lower = anchor_text.lower()
        
        # Contar palabras clave personalizadas
        palabras_clave_count = sum(1 for palabra in caracteristicas['palabras_clave'] 
                                 if palabra in texto_lower)
        
        # Contar objetivos
        objetivos_count = sum(1 for objetivo in caracteristicas['objetivos'] 
                            if objetivo in texto_lower)
        
        # Contar beneficios
        beneficios_count = sum(1 for beneficio in caracteristicas['beneficios_prioritarios'] 
                             if beneficio in texto_lower)
        
        # Calcular score de personalización
        score_personalizacion = 0
        score_personalizacion += palabras_clave_count * 10
        score_personalizacion += objetivos_count * 15
        score_personalizacion += beneficios_count * 12
        
        # Ajustar por longitud
        if 30 <= len(anchor_text) <= 60:
            score_personalizacion += 20
        elif 20 <= len(anchor_text) < 30 or 60 < len(anchor_text) <= 80:
            score_personalizacion += 10
        
        return {
            'longitud': len(anchor_text),
            'palabras_clave_personalizadas': palabras_clave_count,
            'objetivos_incluidos': objetivos_count,
            'beneficios_incluidos': beneficios_count,
            'score_personalizacion': min(100, max(0, score_personalizacion)),
            'tono_detectado': self._detectar_tono_anchor_text(anchor_text)
        }

    def _detectar_tono_anchor_text(self, anchor_text: str) -> str:
        """Detecta el tono del anchor text"""
        texto_lower = anchor_text.lower()
        
        # Palabras indicadoras de tono
        indicadores_tono = {
            'urgente': ['urgente', 'ahora', 'hoy', 'inmediato', 'última oportunidad'],
            'persuasivo': ['descubre', 'por qué', 'secreto', 'razón', 'motivo'],
            'educativo': ['aprende', 'curso', 'guía', 'tutorial', 'enseña'],
            'comercial': ['vende', 'compra', 'adquiere', 'obtén', 'roi'],
            'empático': ['transforma', 'mejora', 'cuidado', 'bienestar', 'personalizado'],
            'técnico': ['sistema', 'tecnología', 'innovación', 'solución', 'método'],
            'autoritario': ['domina', 'líder', 'estándar', 'referencia', 'experto']
        }
        
        for tono, palabras in indicadores_tono.items():
            if any(palabra in texto_lower for palabra in palabras):
                return tono
        
        return 'neutral'

    def exportar_anchor_texts_personalizados(self, anchor_texts: List[Dict[str, Any]], 
                                           perfil: Dict[str, Any], formato: str = "json") -> str:
        """Exporta los anchor texts personalizados"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"anchor_texts_personalizados_{timestamp}"
        
        if formato == "json":
            filename = f"{base_filename}.json"
            resultado = {
                'perfil': perfil,
                'anchor_texts': anchor_texts,
                'estadisticas': self._calcular_estadisticas_personalizadas(anchor_texts),
                'fecha_exportacion': datetime.now().isoformat()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, ensure_ascii=False, indent=4)
            return filename
        elif formato == "txt":
            filename = f"{base_filename}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"--- ANCHOR TEXTS PERSONALIZADOS - IA MARKETING ---\n")
                f.write(f"Fecha: {datetime.now().isoformat()}\n\n")
                
                f.write("PERFIL PERSONALIZADO:\n")
                f.write(f"• Usuario: {perfil['perfil_usuario']}\n")
                f.write(f"• Industria: {perfil['industria']}\n")
                f.write(f"• Objetivo: {perfil['objetivo_marketing']}\n")
                f.write(f"• Tono: {perfil['caracteristicas_combinadas']['tono_preferido']}\n\n")
                
                f.write("ANCHOR TEXTS GENERADOS:\n")
                for i, at in enumerate(anchor_texts, 1):
                    f.write(f"{i}. {at['anchor_text']}\n")
                    f.write(f"   Score: {at['caracteristicas']['score_personalizacion']}/100\n")
                    f.write(f"   Tono: {at['caracteristicas']['tono_detectado']}\n\n")
                
                f.write("ESTADÍSTICAS:\n")
                stats = self._calcular_estadisticas_personalizadas(anchor_texts)
                f.write(f"• Total anchor texts: {stats['total_anchor_texts']}\n")
                f.write(f"• Score promedio: {stats['score_promedio']}/100\n")
                f.write(f"• Tono más común: {stats['tono_mas_comun']}\n")
                f.write(f"• Longitud promedio: {stats['longitud_promedio']} caracteres\n")
                f.write("\n")
            
            return filename
        else:
            raise ValueError("Formato no soportado. Use 'json' o 'txt'.")

    def _calcular_estadisticas_personalizadas(self, anchor_texts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula estadísticas de los anchor texts personalizados"""
        if not anchor_texts:
            return {}
        
        scores = [at['caracteristicas']['score_personalizacion'] for at in anchor_texts]
        tonos = [at['caracteristicas']['tono_detectado'] for at in anchor_texts]
        longitudes = [at['caracteristicas']['longitud'] for at in anchor_texts]
        
        # Contar tonos
        contador_tonos = Counter(tonos)
        tono_mas_comun = contador_tonos.most_common(1)[0][0] if contador_tonos else 'neutral'
        
        return {
            'total_anchor_texts': len(anchor_texts),
            'score_promedio': round(sum(scores) / len(scores), 2),
            'score_maximo': max(scores),
            'score_minimo': min(scores),
            'tono_mas_comun': tono_mas_comun,
            'longitud_promedio': round(sum(longitudes) / len(longitudes), 2),
            'distribucion_tonos': dict(contador_tonos)
        }

def main():
    generador = GeneradorPersonalizadoAnchorTexts()
    
    print("🎯 GENERADOR PERSONALIZADO - ANCHOR TEXTS IA MARKETING")
    print("====================================================\n")
    
    # Ejemplo de generación personalizada
    perfil_usuario = 'intermedio'
    industria = 'ecommerce'
    objetivo = 'conversion'
    preferencias = {
        'longitud_preferida': 'media',
        'incluir_urgencia': True,
        'incluir_numeros': True
    }
    
    print(f"🔄 Generando perfil personalizado...")
    print(f"   • Usuario: {perfil_usuario}")
    print(f"   • Industria: {industria}")
    print(f"   • Objetivo: {objetivo}")
    
    perfil = generador.generar_perfil_personalizado(perfil_usuario, industria, objetivo, preferencias)
    
    print(f"🔄 Generando anchor texts personalizados...")
    anchor_texts = generador.generar_anchor_texts_personalizados(perfil, 25)
    
    print("💾 Exportando resultados...")
    json_file = generador.exportar_anchor_texts_personalizados(anchor_texts, perfil, "json")
    txt_file = generador.exportar_anchor_texts_personalizados(anchor_texts, perfil, "txt")
    
    print("\n✅ Generación completada:")
    print(f"   • Anchor texts generados: {len(anchor_texts)}")
    print(f"   • Perfil: {perfil['perfil_usuario']} + {perfil['industria']} + {perfil['objetivo_marketing']}")
    print(f"   • Tono: {perfil['caracteristicas_combinadas']['tono_preferido']}")
    
    # Mostrar estadísticas
    stats = generador._calcular_estadisticas_personalizadas(anchor_texts)
    print(f"   • Score promedio: {stats['score_promedio']}/100")
    print(f"   • Tono más común: {stats['tono_mas_comun']}")
    print(f"   • Longitud promedio: {stats['longitud_promedio']} caracteres")
    
    print(f"\n📁 Archivos generados:")
    print(f"   • JSON: {json_file}")
    print(f"   • TXT: {txt_file}")
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print("1. Revisa los anchor texts personalizados generados")
    print("2. Ajusta el perfil según tus necesidades específicas")
    print("3. Implementa los anchor texts en tus campañas")
    print("4. Monitorea el rendimiento por perfil de usuario")
    print("5. Refina la personalización basada en los resultados")

if __name__ == "__main__":
    main()
