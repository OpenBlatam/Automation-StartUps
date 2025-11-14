#!/usr/bin/env python3
"""
Motor de Búsqueda Avanzado con IA
================================

Sistema inteligente de búsqueda que utiliza procesamiento de lenguaje natural
para encontrar documentos de manera semántica y contextual.

Características:
- Búsqueda semántica por contenido
- Análisis de relevancia con IA
- Sugerencias inteligentes
- Clasificación automática
- Búsqueda por similitud

Autor: Sistema de Organización Inteligente
Versión: 1.0
Fecha: 2024
"""

import os
import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import difflib
from collections import Counter
import math

class BuscadorIA:
    def __init__(self, base_path="/Users/adan/frontier/docuementos"):
        self.base_path = Path(base_path)
        self.indice_invertido = {}
        self.vectores_documentos = {}
        self.metadatos = {}
        self.sinonimos = self._cargar_sinonimos()
        self.stop_words = self._cargar_stop_words()
        
    def _cargar_sinonimos(self) -> Dict[str, List[str]]:
        """Carga diccionario de sinónimos para búsqueda semántica"""
        return {
            'marketing': ['publicidad', 'promoción', 'ventas', 'comercial', 'mercadeo'],
            'financiero': ['dinero', 'económico', 'presupuesto', 'gastos', 'ingresos'],
            'técnico': ['tecnología', 'programación', 'desarrollo', 'código', 'software'],
            'curso': ['aprendizaje', 'educación', 'formación', 'capacitación', 'entrenamiento'],
            'webinar': ['seminario', 'presentación', 'conferencia', 'charla', 'evento'],
            'análisis': ['estudio', 'evaluación', 'revisión', 'examen', 'investigación'],
            'sistema': ['plataforma', 'herramienta', 'aplicación', 'programa', 'software'],
            'optimización': ['mejora', 'perfeccionamiento', 'optimización', 'refinamiento'],
            'implementación': ['instalación', 'despliegue', 'configuración', 'setup'],
            'documentación': ['manual', 'guía', 'instrucciones', 'referencia', 'ayuda']
        }
    
    def _cargar_stop_words(self) -> set:
        """Carga palabras vacías para filtrar en búsquedas"""
        return {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le',
            'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'unos',
            'unas', 'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas', 'aquel',
            'aquella', 'aquellos', 'aquellas', 'me', 'mi', 'mis', 'tu', 'tus', 'su', 'sus',
            'nuestro', 'nuestra', 'nuestros', 'nuestras', 'vuestro', 'vuestra', 'vuestros',
            'vuestras', 'muy', 'más', 'menos', 'mucho', 'poco', 'todo', 'toda', 'todos',
            'todas', 'alguno', 'alguna', 'algunos', 'algunas', 'ninguno', 'ninguna',
            'ningunos', 'ningunas', 'otro', 'otra', 'otros', 'otras', 'cada', 'cual',
            'cuáles', 'quien', 'quién', 'quienes', 'qué', 'cuál', 'cuáles', 'cuando',
            'cuándo', 'donde', 'dónde', 'como', 'cómo', 'porque', 'por qué', 'si', 'sí',
            'no', 'sino', 'pero', 'aunque', 'mientras', 'después', 'antes', 'durante',
            'hasta', 'desde', 'hacia', 'sobre', 'bajo', 'entre', 'contra', 'sin', 'con'
        }
    
    def _preprocesar_texto(self, texto: str) -> List[str]:
        """Preprocesa texto para búsqueda: normaliza, tokeniza y filtra"""
        if not texto:
            return []
        
        # Normalizar texto
        texto = texto.lower()
        texto = re.sub(r'[^\w\s]', ' ', texto)
        texto = re.sub(r'\s+', ' ', texto)
        
        # Tokenizar
        tokens = texto.split()
        
        # Filtrar stop words y tokens muy cortos
        tokens = [token for token in tokens 
                 if len(token) > 2 and token not in self.stop_words]
        
        return tokens
    
    def _calcular_tf_idf(self, termino: str, documento: str, documentos: List[str]) -> float:
        """Calcula TF-IDF para un término en un documento"""
        # TF (Term Frequency)
        tokens_doc = self._preprocesar_texto(documento)
        tf = tokens_doc.count(termino) / len(tokens_doc) if tokens_doc else 0
        
        # IDF (Inverse Document Frequency)
        docs_con_termino = sum(1 for doc in documentos if termino in self._preprocesar_texto(doc))
        idf = math.log(len(documentos) / docs_con_termino) if docs_con_termino > 0 else 0
        
        return tf * idf
    
    def _expandir_consulta(self, consulta: str) -> List[str]:
        """Expande la consulta con sinónimos y términos relacionados"""
        tokens = self._preprocesar_texto(consulta)
        consulta_expandida = set(tokens)
        
        # Agregar sinónimos
        for token in tokens:
            for categoria, sinonimos in self.sinonimos.items():
                if token in sinonimos:
                    consulta_expandida.add(categoria)
                elif categoria == token:
                    consulta_expandida.update(sinonimos)
        
        return list(consulta_expandida)
    
    def _calcular_similitud_coseno(self, vector1: Dict[str, float], vector2: Dict[str, float]) -> float:
        """Calcula similitud coseno entre dos vectores"""
        # Obtener términos comunes
        terminos_comunes = set(vector1.keys()) & set(vector2.keys())
        
        if not terminos_comunes:
            return 0.0
        
        # Calcular producto punto
        producto_punto = sum(vector1[termino] * vector2[termino] for termino in terminos_comunes)
        
        # Calcular magnitudes
        magnitud1 = math.sqrt(sum(valor ** 2 for valor in vector1.values()))
        magnitud2 = math.sqrt(sum(valor ** 2 for valor in vector2.values()))
        
        if magnitud1 == 0 or magnitud2 == 0:
            return 0.0
        
        return producto_punto / (magnitud1 * magnitud2)
    
    def indexar_documentos(self):
        """Indexa todos los documentos para búsqueda rápida"""
        print("🔍 Indexando documentos para búsqueda IA...")
        
        documentos = []
        self.metadatos = {}
        
        # Recopilar todos los archivos de texto
        for archivo in self.base_path.rglob("*.md"):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Extraer metadatos
                self.metadatos[str(archivo)] = {
                    'nombre': archivo.name,
                    'ruta': str(archivo.relative_to(self.base_path)),
                    'tamaño': archivo.stat().st_size,
                    'modificado': datetime.fromtimestamp(archivo.stat().st_mtime),
                    'contenido': contenido[:1000]  # Primeros 1000 caracteres
                }
                
                documentos.append(contenido)
                
            except Exception as e:
                print(f"⚠️  Error indexando {archivo}: {e}")
        
        # Construir índice invertido
        self.indice_invertido = {}
        for i, doc in enumerate(documentos):
            tokens = self._preprocesar_texto(doc)
            for token in tokens:
                if token not in self.indice_invertido:
                    self.indice_invertido[token] = []
                self.indice_invertido[token].append(i)
        
        # Calcular vectores TF-IDF
        for i, doc in enumerate(documentos):
            vector = {}
            tokens = self._preprocesar_texto(doc)
            for token in set(tokens):
                vector[token] = self._calcular_tf_idf(token, doc, documentos)
            self.vectores_documentos[i] = vector
        
        print(f"✅ Indexación completada: {len(documentos)} documentos, {len(self.indice_invertido)} términos únicos")
    
    def buscar_semantica(self, consulta: str, limite: int = 10) -> List[Dict]:
        """Realiza búsqueda semántica avanzada"""
        if not self.indice_invertido:
            self.indexar_documentos()
        
        # Expandir consulta
        consulta_expandida = self._expandir_consulta(consulta)
        
        # Crear vector de consulta
        vector_consulta = {}
        for termino in consulta_expandida:
            # Simular TF-IDF para la consulta
            vector_consulta[termino] = 1.0 / len(consulta_expandida)
        
        # Calcular similitudes
        similitudes = []
        for doc_id, vector_doc in self.vectores_documentos.items():
            similitud = self._calcular_similitud_coseno(vector_consulta, vector_doc)
            if similitud > 0:
                similitudes.append((doc_id, similitud))
        
        # Ordenar por similitud
        similitudes.sort(key=lambda x: x[1], reverse=True)
        
        # Preparar resultados
        resultados = []
        for doc_id, similitud in similitudes[:limite]:
            ruta_archivo = list(self.metadatos.keys())[doc_id]
            metadatos = self.metadatos[ruta_archivo]
            
            resultados.append({
                'archivo': metadatos['nombre'],
                'ruta': metadatos['ruta'],
                'similitud': round(similitud, 3),
                'relevancia': self._calcular_relevancia(consulta, metadatos['contenido']),
                'snippet': self._generar_snippet(consulta, metadatos['contenido']),
                'tamaño': metadatos['tamaño'],
                'modificado': metadatos['modificado'].strftime('%Y-%m-%d %H:%M')
            })
        
        return resultados
    
    def _calcular_relevancia(self, consulta: str, contenido: str) -> float:
        """Calcula relevancia basada en múltiples factores"""
        consulta_tokens = self._preprocesar_texto(consulta)
        contenido_tokens = self._preprocesar_texto(contenido)
        
        if not consulta_tokens or not contenido_tokens:
            return 0.0
        
        # Factor 1: Coincidencias exactas
        coincidencias = sum(1 for token in consulta_tokens if token in contenido_tokens)
        factor_coincidencias = coincidencias / len(consulta_tokens)
        
        # Factor 2: Similitud de secuencias
        similitud_secuencias = difflib.SequenceMatcher(None, consulta.lower(), contenido.lower()).ratio()
        
        # Factor 3: Posición de coincidencias (más relevante al inicio)
        posicion_promedio = 0
        if coincidencias > 0:
            posiciones = []
            for token in consulta_tokens:
                if token in contenido_tokens:
                    pos = contenido_tokens.index(token)
                    posiciones.append(pos / len(contenido_tokens))
            posicion_promedio = 1 - (sum(posiciones) / len(posiciones))
        
        # Combinar factores
        relevancia = (factor_coincidencias * 0.4 + 
                     similitud_secuencias * 0.4 + 
                     posicion_promedio * 0.2)
        
        return min(relevancia, 1.0)
    
    def _generar_snippet(self, consulta: str, contenido: str, longitud: int = 200) -> str:
        """Genera snippet relevante del contenido"""
        consulta_tokens = self._preprocesar_texto(consulta)
        
        # Buscar la mejor posición para el snippet
        mejor_posicion = 0
        mejor_puntuacion = 0
        
        for i in range(0, len(contenido) - longitud, 50):
            snippet = contenido[i:i + longitud]
            snippet_tokens = self._preprocesar_texto(snippet)
            
            # Contar coincidencias en el snippet
            coincidencias = sum(1 for token in consulta_tokens if token in snippet_tokens)
            puntuacion = coincidencias / len(consulta_tokens) if consulta_tokens else 0
            
            if puntuacion > mejor_puntuacion:
                mejor_puntuacion = puntuacion
                mejor_posicion = i
        
        # Generar snippet
        snippet = contenido[mejor_posicion:mejor_posicion + longitud]
        
        # Limpiar y formatear
        snippet = re.sub(r'\s+', ' ', snippet).strip()
        if mejor_posicion > 0:
            snippet = "..." + snippet
        if mejor_posicion + longitud < len(contenido):
            snippet = snippet + "..."
        
        return snippet
    
    def sugerir_terminos(self, consulta: str) -> List[str]:
        """Sugiere términos relacionados para mejorar la búsqueda"""
        if not consulta:
            return []
        
        consulta_tokens = self._preprocesar_texto(consulta)
        sugerencias = set()
        
        # Sugerencias basadas en sinónimos
        for token in consulta_tokens:
            for categoria, sinonimos in self.sinonimos.items():
                if token in sinonimos:
                    sugerencias.update(sinonimos)
                elif categoria == token:
                    sugerencias.update(sinonimos)
        
        # Sugerencias basadas en términos similares en el índice
        for token in consulta_tokens:
            for termino_indice in self.indice_invertido.keys():
                if difflib.SequenceMatcher(None, token, termino_indice).ratio() > 0.7:
                    sugerencias.add(termino_indice)
        
        return list(sugerencias)[:10]
    
    def clasificar_documento(self, ruta_archivo: str) -> Dict[str, float]:
        """Clasifica un documento en diferentes categorías"""
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
        except:
            return {}
        
        tokens = self._preprocesar_texto(contenido)
        clasificacion = {}
        
        # Definir categorías y sus palabras clave
        categorias = {
            'marketing': ['marketing', 'publicidad', 'ventas', 'promoción', 'cliente', 'mercado'],
            'financiero': ['dinero', 'presupuesto', 'gastos', 'ingresos', 'financiero', 'económico'],
            'técnico': ['código', 'programación', 'software', 'técnico', 'desarrollo', 'api'],
            'educativo': ['curso', 'aprendizaje', 'educación', 'formación', 'tutorial', 'guía'],
            'estratégico': ['estrategia', 'plan', 'objetivo', 'meta', 'visión', 'misión']
        }
        
        for categoria, palabras_clave in categorias.items():
            coincidencias = sum(1 for palabra in palabras_clave if palabra in tokens)
            clasificacion[categoria] = coincidencias / len(palabras_clave)
        
        return clasificacion
    
    def generar_reporte_busqueda(self, consulta: str, resultados: List[Dict]) -> str:
        """Genera reporte detallado de la búsqueda"""
        reporte = f"""# 🔍 Reporte de Búsqueda IA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 Consulta
**Término buscado:** {consulta}
**Resultados encontrados:** {len(resultados)}

## 📊 Análisis de Resultados
"""
        
        if resultados:
            # Estadísticas generales
            similitudes = [r['similitud'] for r in resultados]
            relevancias = [r['relevancia'] for r in resultados]
            
            reporte += f"""
- **Similitud promedio:** {sum(similitudes) / len(similitudes):.3f}
- **Relevancia promedio:** {sum(relevancias) / len(relevancias):.3f}
- **Mejor resultado:** {resultados[0]['similitud']:.3f} de similitud

## 📁 Resultados Detallados
"""
            
            for i, resultado in enumerate(resultados[:10], 1):
                reporte += f"""
### {i}. {resultado['archivo']}
- **Ruta:** {resultado['ruta']}
- **Similitud:** {resultado['similitud']:.3f}
- **Relevancia:** {resultado['relevancia']:.3f}
- **Tamaño:** {resultado['tamaño']:,} bytes
- **Modificado:** {resultado['modificado']}
- **Snippet:** {resultado['snippet']}

---
"""
        else:
            reporte += """
## ❌ No se encontraron resultados

### 💡 Sugerencias:
- Verifica la ortografía
- Intenta términos más generales
- Usa sinónimos
- Revisa los filtros aplicados
"""
        
        return reporte

def main():
    """Función principal para demostrar el motor de búsqueda"""
    print("🤖 Motor de Búsqueda Avanzado con IA")
    print("====================================")
    
    buscador = BuscadorIA()
    
    # Indexar documentos
    buscador.indexar_documentos()
    
    # Ejemplo de búsqueda
    consulta = "marketing IA curso"
    print(f"\n🔍 Buscando: '{consulta}'")
    
    resultados = buscador.buscar_semantica(consulta, limite=5)
    
    if resultados:
        print(f"\n✅ Encontrados {len(resultados)} resultados:")
        for i, resultado in enumerate(resultados, 1):
            print(f"\n{i}. {resultado['archivo']}")
            print(f"   Similitud: {resultado['similitud']:.3f}")
            print(f"   Relevancia: {resultado['relevancia']:.3f}")
            print(f"   Snippet: {resultado['snippet'][:100]}...")
    else:
        print("❌ No se encontraron resultados")
    
    # Generar reporte
    reporte = buscador.generar_reporte_busqueda(consulta, resultados)
    
    # Guardar reporte
    reporte_path = buscador.base_path / "REPORTE_BUSQUEDA_IA.md"
    with open(reporte_path, 'w', encoding='utf-8') as f:
        f.write(reporte)
    
    print(f"\n📊 Reporte guardado en: {reporte_path}")

if __name__ == "__main__":
    main()






