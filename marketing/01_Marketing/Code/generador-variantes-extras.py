#!/usr/bin/env python3
"""
Generador de Variantes Extras para Anchor Texts IA Marketing
Crea variantes adicionales con fórmulas especializadas y categorías únicas
"""

import json
import random
from datetime import datetime
from typing import List, Dict, Any, Tuple
import os

class GeneradorVariantesExtras:
    def __init__(self):
        self.categorias_especiales = {
            'estacionales': {
                'primavera': ['renovación', 'crecimiento', 'florecimiento', 'nuevo comienzo'],
                'verano': ['energía', 'calor', 'intensidad', 'vitalidad'],
                'otoño': ['cosecha', 'madurez', 'transformación', 'cambio'],
                'invierno': ['reflexión', 'planificación', 'preparación', 'fortaleza']
            },
            'emocionales': {
                'miedo': ['no te quedes atrás', 'pierdes oportunidades', 'competencia te supera'],
                'alegria': ['celebra el éxito', 'disfruta los resultados', 'vive la transformación'],
                'curiosidad': ['descubre el secreto', 'explora nuevas posibilidades', 'desvela el misterio'],
                'orgullo': ['sé el mejor', 'destaca entre todos', 'demuestra tu excelencia']
            },
            'temporales': {
                'inmediato': ['ahora mismo', 'inmediatamente', 'sin demora', 'ya'],
                'corto_plazo': ['en 7 días', 'esta semana', 'próximamente', 'muy pronto'],
                'mediano_plazo': ['en 30 días', 'este mes', 'en un mes', 'próximo mes'],
                'largo_plazo': ['en 90 días', 'este trimestre', 'en 3 meses', 'próximo trimestre']
            },
            'geograficas': {
                'local': ['en tu ciudad', 'en tu región', 'localmente', 'cerca de ti'],
                'nacional': ['en tu país', 'nacionalmente', 'en toda España', 'en México'],
                'internacional': ['globalmente', 'en todo el mundo', 'internacionalmente', 'mundialmente']
            },
            'demograficas': {
                'edad': ['jóvenes', 'adultos', 'mayores', 'todas las edades'],
                'genero': ['hombres', 'mujeres', 'todos', 'cualquier persona'],
                'profesion': ['empresarios', 'freelancers', 'estudiantes', 'profesionales']
            }
        }
        
        self.formulas_especiales = {
            'storytelling': [
                "{{personaje}} {{problema}} → {{transformacion}} con {{solucion}}",
                "De {{situacion_inicial}} a {{situacion_final}} en {{tiempo}}",
                "La historia de {{persona}} que {{accion}} {{resultado}}",
                "{{conflicto}} → {{resolucion}} → {{triunfo}}"
            ],
            'contraste': [
                "{{antes}} vs {{despues}} - {{diferencia}}",
                "De {{problema}} a {{solucion}} en {{tiempo}}",
                "{{situacion_negativa}} → {{situacion_positiva}}",
                "No más {{problema}}, ahora {{beneficio}}"
            ],
            'numeros': [
                "{{numero}} {{unidad}} para {{objetivo}}",
                "{{numero}} {{elemento}} que {{accion}} {{resultado}}",
                "En {{numero}} {{tiempo}} {{transformacion}}",
                "{{numero}} {{metodo}} {{garantia}} {{resultado}}"
            ],
            'preguntas': [
                "¿{{pregunta_problema}}? {{solucion}} {{beneficio}}",
                "¿{{pregunta_curiosidad}}? {{respuesta}} {{valor}}",
                "¿{{pregunta_desafio}}? {{metodo}} {{garantia}}",
                "¿{{pregunta_urgencia}}? {{accion}} {{resultado}}"
            ],
            'comandos': [
                "{{verbo_imperativo}} {{objeto}} {{beneficio}} {{urgencia}}",
                "{{accion_directa}} {{resultado}} {{garantia}}",
                "{{instruccion}} {{metodo}} {{tiempo}}",
                "{{orden}} {{transformacion}} {{confirmacion}}"
            ]
        }
        
        self.palabras_especiales = {
            'personajes': ['Juan', 'María', 'Carlos', 'Ana', 'Luis', 'Laura', 'Pedro', 'Carmen'],
            'problemas': ['estancado', 'frustrado', 'perdido', 'confundido', 'desesperado', 'agotado'],
            'transformaciones': ['triunfó', 'se transformó', 'logró el éxito', 'alcanzó sus metas'],
            'soluciones': ['IA Marketing', 'Inteligencia Artificial', 'Automatización', 'Marketing Digital'],
            'situaciones_iniciales': ['cero', 'nada', 'fracaso', 'estancamiento', 'confusión'],
            'situaciones_finales': ['éxito', 'triunfo', 'prosperidad', 'libertad', 'realización'],
            'tiempos': ['7 días', '30 días', '3 meses', '6 meses', '1 año'],
            'conflictos': ['luchaba', 'sufría', 'fracasaba', 'perdía tiempo', 'gastaba dinero'],
            'resoluciones': ['descubrió', 'implementó', 'aplicó', 'dominó', 'conquistó'],
            'triunfos': ['triunfó', 'ganó', 'logró', 'alcanzó', 'conquistó'],
            'numeros': ['1', '3', '5', '7', '10', '21', '30', '90', '365'],
            'unidades': ['días', 'semanas', 'meses', 'años', 'pasos', 'técnicas', 'estrategias'],
            'elementos': ['técnicas', 'estrategias', 'métodos', 'herramientas', 'secretos'],
            'metodos': ['método', 'sistema', 'estrategia', 'técnica', 'fórmula'],
            'preguntas_problema': ['Estancado en tu negocio', 'Sin resultados', 'Perdiendo dinero', 'Sin clientes'],
            'preguntas_curiosidad': ['Quieres saber el secreto', 'Te preguntas cómo', 'Quieres descubrir'],
            'preguntas_desafio': ['Puedes lograrlo', 'Estás listo', 'Quieres cambiar'],
            'preguntas_urgencia': ['Es el momento', 'No puedes esperar', 'La oportunidad es ahora'],
            'respuestas': ['Aquí está', 'Te lo revelo', 'Te muestro', 'Te enseño'],
            'valores': ['valor', 'beneficio', 'ventaja', 'oportunidad'],
            'garantias': ['garantía', 'promesa', 'compromiso', 'aseguro'],
            'verbos_imperativos': ['Domina', 'Aprende', 'Implementa', 'Conquista', 'Transforma'],
            'objetos': ['IA Marketing', 'Marketing Digital', 'Automatización', 'Inteligencia Artificial'],
            'beneficios': ['ventas', 'conversiones', 'ingresos', 'resultados', 'éxito'],
            'urgencias': ['AHORA', 'YA', 'HOY', 'INMEDIATAMENTE'],
            'acciones_directas': ['Multiplica', 'Aumenta', 'Optimiza', 'Mejora', 'Revoluciona'],
            'resultados': ['ventas', 'conversiones', 'ingresos', 'clientes', 'éxito'],
            'instrucciones': ['Sigue', 'Aplica', 'Usa', 'Implementa', 'Ejecuta'],
            'tiempos': ['7 días', '30 días', '3 meses', 'ahora', 'ya'],
            'ordenes': ['Haz', 'Crea', 'Construye', 'Desarrolla', 'Genera'],
            'confirmaciones': ['¡SÍ!', '¡FUNCIONA!', '¡GARANTIZADO!', '¡COMPROBADO!']
        }

    def generar_variantes_estacionales(self, cantidad: int = 20) -> List[Dict[str, Any]]:
        """Genera variantes estacionales de anchor texts"""
        variantes = []
        
        for estacion, palabras in self.categorias_especiales['estacionales'].items():
            for i in range(cantidad // 4):  # Dividir entre las 4 estaciones
                formula = random.choice([
                    f"{{palabra_estacional}} {{accion}} {{beneficio}} - {{urgencia}}",
                    f"{{palabra_estacional}} {{transformacion}} {{resultado}} - {{garantia}}",
                    f"{{palabra_estacional}} {{oportunidad}} {{solucion}} - {{limitacion}}"
                ])
                
                anchor = formula.format(
                    palabra_estacional=random.choice(palabras),
                    accion=random.choice(['Domina', 'Aprende', 'Implementa', 'Revoluciona']),
                    beneficio=random.choice(['IA Marketing', 'Marketing Digital', 'Automatización']),
                    urgencia=random.choice(['AHORA', 'YA', 'HOY']),
                    transformacion=random.choice(['Transforma', 'Revoluciona', 'Cambia']),
                    resultado=random.choice(['tu negocio', 'tus ventas', 'tu marketing']),
                    garantia=random.choice(['Garantía 100%', 'Sin riesgo', 'Satisfacción']),
                    oportunidad=random.choice(['Oportunidad', 'Momento perfecto', 'Chance']),
                    solucion=random.choice(['IA Marketing', 'Inteligencia Artificial']),
                    limitacion=random.choice(['Solo este mes', 'Edición limitada', 'Últimas plazas'])
                )
                
                variantes.append({
                    'anchor_text': anchor,
                    'categoria': 'estacional',
                    'subcategoria': estacion,
                    'palabra_clave': random.choice(palabras),
                    'longitud': len(anchor),
                    'palabras_poder': self.contar_palabras_poder(anchor)
                })
        
        return variantes

    def generar_variantes_emocionales(self, cantidad: int = 20) -> List[Dict[str, Any]]:
        """Genera variantes emocionales de anchor texts"""
        variantes = []
        
        for emocion, frases in self.categorias_especiales['emocionales'].items():
            for i in range(cantidad // 4):  # Dividir entre las 4 emociones
                formula = random.choice([
                    f"{{frase_emocional}} - {{solucion}} {{beneficio}}",
                    f"{{frase_emocional}} → {{transformacion}} con {{metodo}}",
                    f"{{frase_emocional}} {{urgencia}} {{accion}} {{resultado}}"
                ])
                
                anchor = formula.format(
                    frase_emocional=random.choice(frases),
                    solucion=random.choice(['IA Marketing', 'Inteligencia Artificial', 'Automatización']),
                    beneficio=random.choice(['te salva', 'te ayuda', 'te transforma']),
                    transformacion=random.choice(['Transforma', 'Revoluciona', 'Cambia']),
                    metodo=random.choice(['IA Marketing', 'Marketing Digital']),
                    urgencia=random.choice(['AHORA', 'YA', 'HOY']),
                    accion=random.choice(['Domina', 'Aprende', 'Implementa']),
                    resultado=random.choice(['ventas', 'conversiones', 'éxito'])
                )
                
                variantes.append({
                    'anchor_text': anchor,
                    'categoria': 'emocional',
                    'subcategoria': emocion,
                    'frase_clave': random.choice(frases),
                    'longitud': len(anchor),
                    'palabras_poder': self.contar_palabras_poder(anchor)
                })
        
        return variantes

    def generar_variantes_storytelling(self, cantidad: int = 20) -> List[Dict[str, Any]]:
        """Genera variantes de storytelling"""
        variantes = []
        
        for i in range(cantidad):
            formula = random.choice(self.formulas_especiales['storytelling'])
            
            anchor = formula.format(
                personaje=random.choice(self.palabras_especiales['personajes']),
                problema=random.choice(self.palabras_especiales['problemas']),
                transformacion=random.choice(self.palabras_especiales['transformaciones']),
                solucion=random.choice(self.palabras_especiales['soluciones']),
                situacion_inicial=random.choice(self.palabras_especiales['situaciones_iniciales']),
                situacion_final=random.choice(self.palabras_especiales['situaciones_finales']),
                tiempo=random.choice(self.palabras_especiales['tiempos']),
                conflicto=random.choice(self.palabras_especiales['conflictos']),
                resolucion=random.choice(self.palabras_especiales['resoluciones']),
                triunfo=random.choice(self.palabras_especiales['triunfos'])
            )
            
            variantes.append({
                'anchor_text': anchor,
                'categoria': 'storytelling',
                'formula': formula,
                'longitud': len(anchor),
                'palabras_poder': self.contar_palabras_poder(anchor)
            })
        
        return variantes

    def generar_variantes_numeros(self, cantidad: int = 20) -> List[Dict[str, Any]]:
        """Genera variantes con números específicos"""
        variantes = []
        
        for i in range(cantidad):
            formula = random.choice(self.formulas_especiales['numeros'])
            
            anchor = formula.format(
                numero=random.choice(self.palabras_especiales['numeros']),
                unidad=random.choice(self.palabras_especiales['unidades']),
                objetivo=random.choice(['dominar IA Marketing', 'aumentar ventas', 'mejorar conversiones']),
                elemento=random.choice(self.palabras_especiales['elementos']),
                accion=random.choice(['transforman', 'revolucionan', 'cambian']),
                resultado=random.choice(['tu negocio', 'tus ventas', 'tu marketing']),
                tiempo=random.choice(self.palabras_especiales['tiempos']),
                transformacion=random.choice(['transformación', 'revolución', 'cambio']),
                metodo=random.choice(self.palabras_especiales['metodos']),
                garantia=random.choice(['garantía', 'promesa', 'compromiso'])
            )
            
            variantes.append({
                'anchor_text': anchor,
                'categoria': 'numeros',
                'formula': formula,
                'numero': random.choice(self.palabras_especiales['numeros']),
                'longitud': len(anchor),
                'palabras_poder': self.contar_palabras_poder(anchor)
            })
        
        return variantes

    def generar_variantes_preguntas(self, cantidad: int = 20) -> List[Dict[str, Any]]:
        """Genera variantes con preguntas"""
        variantes = []
        
        for i in range(cantidad):
            formula = random.choice(self.formulas_especiales['preguntas'])
            
            anchor = formula.format(
                pregunta_problema=random.choice(self.palabras_especiales['preguntas_problema']),
                solucion=random.choice(['IA Marketing', 'Inteligencia Artificial', 'Automatización']),
                beneficio=random.choice(['te salva', 'te ayuda', 'te transforma']),
                pregunta_curiosidad=random.choice(self.palabras_especiales['preguntas_curiosidad']),
                respuesta=random.choice(self.palabras_especiales['respuestas']),
                valor=random.choice(self.palabras_especiales['valores']),
                pregunta_desafio=random.choice(self.palabras_especiales['preguntas_desafio']),
                metodo=random.choice(self.palabras_especiales['metodos']),
                garantia=random.choice(self.palabras_especiales['garantias']),
                pregunta_urgencia=random.choice(self.palabras_especiales['preguntas_urgencia']),
                accion=random.choice(['Domina', 'Aprende', 'Implementa']),
                resultado=random.choice(['ventas', 'conversiones', 'éxito'])
            )
            
            variantes.append({
                'anchor_text': anchor,
                'categoria': 'preguntas',
                'formula': formula,
                'longitud': len(anchor),
                'palabras_poder': self.contar_palabras_poder(anchor)
            })
        
        return variantes

    def generar_variantes_comandos(self, cantidad: int = 20) -> List[Dict[str, Any]]:
        """Genera variantes con comandos imperativos"""
        variantes = []
        
        for i in range(cantidad):
            formula = random.choice(self.formulas_especiales['comandos'])
            
            anchor = formula.format(
                verbo_imperativo=random.choice(self.palabras_especiales['verbos_imperativos']),
                objeto=random.choice(self.palabras_especiales['objetos']),
                beneficio=random.choice(self.palabras_especiales['beneficios']),
                urgencia=random.choice(self.palabras_especiales['urgencias']),
                accion_directa=random.choice(self.palabras_especiales['acciones_directas']),
                resultado=random.choice(self.palabras_especiales['resultados']),
                garantia=random.choice(self.palabras_especiales['garantias']),
                instruccion=random.choice(self.palabras_especiales['instrucciones']),
                metodo=random.choice(self.palabras_especiales['metodos']),
                tiempo=random.choice(self.palabras_especiales['tiempos']),
                orden=random.choice(self.palabras_especiales['ordenes']),
                transformacion=random.choice(['tu negocio', 'tus ventas', 'tu marketing']),
                confirmacion=random.choice(self.palabras_especiales['confirmaciones'])
            )
            
            variantes.append({
                'anchor_text': anchor,
                'categoria': 'comandos',
                'formula': formula,
                'longitud': len(anchor),
                'palabras_poder': self.contar_palabras_poder(anchor)
            })
        
        return variantes

    def generar_variantes_geograficas(self, cantidad: int = 20) -> List[Dict[str, Any]]:
        """Genera variantes geográficas"""
        variantes = []
        
        for ubicacion, frases in self.categorias_especiales['geograficas'].items():
            for i in range(cantidad // 3):  # Dividir entre las 3 ubicaciones
                formula = random.choice([
                    f"{{frase_geografica}} {{accion}} {{beneficio}} - {{urgencia}}",
                    f"{{frase_geografica}} {{oportunidad}} {{solucion}} - {{limitacion}}",
                    f"{{frase_geografica}} {{transformacion}} {{resultado}} - {{garantia}}"
                ])
                
                anchor = formula.format(
                    frase_geografica=random.choice(frases),
                    accion=random.choice(['Domina', 'Aprende', 'Implementa']),
                    beneficio=random.choice(['IA Marketing', 'Marketing Digital', 'Automatización']),
                    urgencia=random.choice(['AHORA', 'YA', 'HOY']),
                    oportunidad=random.choice(['Oportunidad', 'Momento perfecto', 'Chance']),
                    solucion=random.choice(['IA Marketing', 'Inteligencia Artificial']),
                    limitacion=random.choice(['Solo este mes', 'Edición limitada', 'Últimas plazas']),
                    transformacion=random.choice(['Transforma', 'Revoluciona', 'Cambia']),
                    resultado=random.choice(['tu negocio', 'tus ventas', 'tu marketing']),
                    garantia=random.choice(['Garantía 100%', 'Sin riesgo', 'Satisfacción'])
                )
                
                variantes.append({
                    'anchor_text': anchor,
                    'categoria': 'geografica',
                    'subcategoria': ubicacion,
                    'frase_clave': random.choice(frases),
                    'longitud': len(anchor),
                    'palabras_poder': self.contar_palabras_poder(anchor)
                })
        
        return variantes

    def generar_variantes_demograficas(self, cantidad: int = 20) -> List[Dict[str, Any]]:
        """Genera variantes demográficas"""
        variantes = []
        
        for demografia, opciones in self.categorias_especiales['demograficas'].items():
            for i in range(cantidad // 3):  # Dividir entre las 3 demografías
                formula = random.choice([
                    f"{{opcion_demografica}} {{accion}} {{beneficio}} - {{urgencia}}",
                    f"{{opcion_demografica}} {{oportunidad}} {{solucion}} - {{limitacion}}",
                    f"{{opcion_demografica}} {{transformacion}} {{resultado}} - {{garantia}}"
                ])
                
                anchor = formula.format(
                    opcion_demografica=random.choice(opciones),
                    accion=random.choice(['Domina', 'Aprende', 'Implementa']),
                    beneficio=random.choice(['IA Marketing', 'Marketing Digital', 'Automatización']),
                    urgencia=random.choice(['AHORA', 'YA', 'HOY']),
                    oportunidad=random.choice(['Oportunidad', 'Momento perfecto', 'Chance']),
                    solucion=random.choice(['IA Marketing', 'Inteligencia Artificial']),
                    limitacion=random.choice(['Solo este mes', 'Edición limitada', 'Últimas plazas']),
                    transformacion=random.choice(['Transforma', 'Revoluciona', 'Cambia']),
                    resultado=random.choice(['tu negocio', 'tus ventas', 'tu marketing']),
                    garantia=random.choice(['Garantía 100%', 'Sin riesgo', 'Satisfacción'])
                )
                
                variantes.append({
                    'anchor_text': anchor,
                    'categoria': 'demografica',
                    'subcategoria': demografia,
                    'opcion_clave': random.choice(opciones),
                    'longitud': len(anchor),
                    'palabras_poder': self.contar_palabras_poder(anchor)
                })
        
        return variantes

    def contar_palabras_poder(self, texto: str) -> int:
        """Cuenta las palabras de poder en el texto"""
        palabras_poder = [
            'gratis', 'nuevo', 'exclusivo', 'limitado', 'urgente', 'ahora', 'ya',
            'revolucionario', 'innovador', 'avanzado', 'profesional', 'experto',
            'garantía', 'sin riesgo', 'resultados', 'éxito', 'crecimiento',
            'multiplica', 'aumenta', 'optimiza', 'mejora', 'domina', 'aprende'
        ]
        return sum(1 for palabra in palabras_poder if palabra.lower() in texto.lower())

    def generar_todas_las_variantes(self) -> Dict[str, Any]:
        """Genera todas las variantes extras"""
        print("🔄 Generando variantes estacionales...")
        estacionales = self.generar_variantes_estacionales(20)
        
        print("🔄 Generando variantes emocionales...")
        emocionales = self.generar_variantes_emocionales(20)
        
        print("🔄 Generando variantes de storytelling...")
        storytelling = self.generar_variantes_storytelling(20)
        
        print("🔄 Generando variantes con números...")
        numeros = self.generar_variantes_numeros(20)
        
        print("🔄 Generando variantes con preguntas...")
        preguntas = self.generar_variantes_preguntas(20)
        
        print("🔄 Generando variantes con comandos...")
        comandos = self.generar_variantes_comandos(20)
        
        print("🔄 Generando variantes geográficas...")
        geograficas = self.generar_variantes_geograficas(20)
        
        print("🔄 Generando variantes demográficas...")
        demograficas = self.generar_variantes_demograficas(20)
        
        # Consolidar todas las variantes
        todas_las_variantes = {
            'estacionales': estacionales,
            'emocionales': emocionales,
            'storytelling': storytelling,
            'numeros': numeros,
            'preguntas': preguntas,
            'comandos': comandos,
            'geograficas': geograficas,
            'demograficas': demograficas
        }
        
        # Calcular estadísticas
        total_variantes = sum(len(variantes) for variantes in todas_las_variantes.values())
        
        resultados = {
            'timestamp': datetime.now().isoformat(),
            'total_variantes': total_variantes,
            'categorias': len(todas_las_variantes),
            'variantes_por_categoria': {cat: len(vars) for cat, vars in todas_las_variantes.items()},
            'variantes': todas_las_variantes,
            'estadisticas': {
                'longitud_promedio': sum(
                    sum(v['longitud'] for v in variantes) 
                    for variantes in todas_las_variantes.values()
                ) / total_variantes,
                'palabras_poder_promedio': sum(
                    sum(v['palabras_poder'] for v in variantes) 
                    for variantes in todas_las_variantes.values()
                ) / total_variantes
            }
        }
        
        return resultados

    def exportar_variantes_extras(self, resultados: Dict[str, Any]) -> str:
        """Exporta las variantes extras en JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"variantes_extras_anchor_texts_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        
        return filename

    def generar_documentacion_variantes(self, resultados: Dict[str, Any]) -> str:
        """Genera documentación de las variantes extras"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"documentacion_variantes_extras_{timestamp}.md"
        
        md_content = f"""# 🎨 DOCUMENTACIÓN - VARIANTES EXTRAS ANCHOR TEXTS IA MARKETING

## 📊 **RESUMEN EJECUTIVO**
- **Total de Variantes**: {resultados['total_variantes']}
- **Categorías**: {resultados['categorias']}
- **Fecha de Generación**: {resultados['timestamp']}

---

## 🎯 **VARIANTES POR CATEGORÍA**

"""
        
        for categoria, variantes in resultados['variantes'].items():
            md_content += f"""### **{categoria.upper().replace('_', ' ')}**
- **Cantidad**: {len(variantes)} variantes
- **Descripción**: Variantes especializadas en {categoria}

**Ejemplos:**
"""
            for i, variante in enumerate(variantes[:5], 1):  # Mostrar solo los primeros 5
                md_content += f"{i}. {variante['anchor_text']}\n"
            
            if len(variantes) > 5:
                md_content += f"... y {len(variantes) - 5} más\n"
            
            md_content += "\n---\n\n"
        
        md_content += f"""## 📈 **ESTADÍSTICAS**

- **Longitud Promedio**: {resultados['estadisticas']['longitud_promedio']:.1f} caracteres
- **Palabras de Poder Promedio**: {resultados['estadisticas']['palabras_poder_promedio']:.1f} palabras

## 🎯 **INSTRUCCIONES DE USO**

### **1. Para Variantes Estacionales**
- Usa según la época del año
- Adapta el mensaje a la estación
- Aprovecha el contexto emocional

### **2. Para Variantes Emocionales**
- Selecciona según la emoción objetivo
- Adapta el tono a tu audiencia
- Usa para crear conexión emocional

### **3. Para Variantes de Storytelling**
- Cuenta una historia
- Crea conexión emocional
- Usa personajes y situaciones

### **4. Para Variantes con Números**
- Usa números específicos
- Crea sensación de concreción
- Aprovecha la psicología de los números

### **5. Para Variantes con Preguntas**
- Genera curiosidad
- Crea engagement
- Invita a la acción

### **6. Para Variantes con Comandos**
- Usa verbos imperativos
- Crea urgencia
- Dirige la acción

### **7. Para Variantes Geográficas**
- Adapta a la ubicación
- Crea relevancia local
- Aprovecha el contexto geográfico

### **8. Para Variantes Demográficas**
- Dirige a audiencias específicas
- Crea personalización
- Aprovecha el contexto demográfico

## 🚀 **PRÓXIMOS PASOS**

1. **Selecciona** las categorías más relevantes para tu negocio
2. **Personaliza** las variantes según tu marca
3. **Implementa** en tus campañas de marketing
4. **Monitorea** el rendimiento y optimiza
5. **Combina** diferentes categorías para mayor impacto

---

*Documentación generada automáticamente por el Generador de Variantes Extras*
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return filename

def main():
    """Función principal"""
    print("🎨 GENERADOR DE VARIANTES EXTRAS - ANCHOR TEXTS IA MARKETING")
    print("=" * 70)
    
    generador = GeneradorVariantesExtras()
    
    print("🔄 Generando todas las variantes extras...")
    resultados = generador.generar_todas_las_variantes()
    
    print("💾 Exportando variantes en JSON...")
    json_file = generador.exportar_variantes_extras(resultados)
    
    print("📚 Generando documentación...")
    md_file = generador.generar_documentacion_variantes(resultados)
    
    print(f"\n✅ Generación completada:")
    print(f"   • Total de variantes: {resultados['total_variantes']}")
    print(f"   • Categorías: {resultados['categorias']}")
    print(f"   • Longitud promedio: {resultados['estadisticas']['longitud_promedio']:.1f} caracteres")
    print(f"   • Palabras de poder promedio: {resultados['estadisticas']['palabras_poder_promedio']:.1f}")
    
    print(f"\n📁 Archivos generados:")
    print(f"   • JSON: {json_file}")
    print(f"   • Documentación: {md_file}")
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Revisa la documentación para entender las categorías")
    print("2. Selecciona las variantes más relevantes para tu negocio")
    print("3. Personaliza según tu marca y audiencia")
    print("4. Implementa en tus campañas de marketing")
    print("5. Monitorea el rendimiento y optimiza")

if __name__ == "__main__":
    main()






