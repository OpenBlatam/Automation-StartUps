# Guía de Troubleshooting: Prompt Perplexity v3

## Resumen

Esta guía proporciona soluciones sistemáticas para problemas comunes al implementar y usar el prompt Perplexity v3. Incluye diagnóstico, soluciones paso a paso, y prevención de problemas futuros.

---

## Problemas Comunes y Soluciones

### Problema 1: Respuestas que no siguen el formato correcto

**Síntomas:**
- Respuestas comienzan con headers
- Falta de citaciones apropiadas
- Formato inconsistente
- Listas anidadas incorrectamente

**Diagnóstico:**
1. Verificar que el prompt completo esté incluido
2. Revisar que todas las secciones estén presentes
3. Confirmar que no hay modificaciones no intencionales

**Soluciones:**

**Solución A: Verificación del Prompt**
```
1. Asegúrate de incluir TODAS las secciones:
   - <goal>
   - <core_capabilities>
   - <format_rules>
   - <restrictions>
   - <query_type>
   - <planning_rules>
   - <output>
   - <personalization>

2. Verifica que no haya caracteres especiales corruptos
3. Confirma que el formato XML de las secciones sea correcto
```

**Solución B: Refuerzo de Instrucciones**
- Añadir recordatorios explícitos al inicio del prompt
- Usar ejemplos en las instrucciones
- Incluir validación de formato en el output

**Solución C: Post-procesamiento**
- Implementar validación automática de formato
- Corregir headers incorrectos automáticamente
- Validar citaciones antes de mostrar respuesta

---

### Problema 2: Citaciones incorrectas o faltantes

**Síntomas:**
- Citas en formato incorrecto: [12, 13] en lugar de [12][13]
- Falta de espacios antes de citas
- Citas a fuentes no utilizadas
- Falta de citas en información parafraseada

**Diagnóstico:**
1. Revisar sección de Citations en format_rules
2. Verificar ejemplos proporcionados
3. Confirmar que las fuentes estén correctamente indexadas

**Soluciones:**

**Solución A: Clarificación de Instrucciones**
```
En la sección Citations, añadir:
- Ejemplos más explícitos
- Casos edge clarificados
- Validación de formato requerida
```

**Solución B: Validación Automática**
```python
def validate_citations(text):
    """Valida formato de citaciones"""
    import re
    # Buscar formato incorrecto [12, 13]
    incorrect = re.findall(r'\[\d+,\s*\d+\]', text)
    if incorrect:
        return False, f"Formato incorrecto encontrado: {incorrect}"
    
    # Verificar espacio antes de cita
    no_space = re.findall(r'\w\[', text)
    if no_space:
        return False, "Falta espacio antes de cita"
    
    return True, "Formato correcto"
```

**Solución C: Post-procesamiento de Citas**
- Corregir formato automáticamente
- Añadir espacios faltantes
- Validar índices de fuentes

---

### Problema 3: Respuestas demasiado largas o cortas

**Síntomas:**
- Respuestas excesivamente verbosas
- Respuestas demasiado breves
- No se ajusta a la complejidad de la consulta

**Diagnóstico:**
1. Revisar sección Answer Quality en core_capabilities
2. Verificar instrucciones de Content Density
3. Confirmar que el tipo de consulta esté identificado correctamente

**Soluciones:**

**Solución A: Ajuste de Instrucciones**
```
En Answer Quality, especificar:
- Longitud mínima por tipo de consulta
- Longitud máxima recomendada
- Criterios para expandir/contraer
```

**Solución B: Validación de Longitud**
```python
def validate_answer_length(text, query_type):
    """Valida longitud de respuesta según tipo"""
    word_count = len(text.split())
    
    limits = {
        'weather': (10, 50),
        'people': (100, 500),
        'academic': (500, 2000),
        'news': (200, 800),
        'coding': (50, 1000)
    }
    
    min_words, max_words = limits.get(query_type, (100, 1000))
    
    if word_count < min_words:
        return False, f"Respuesta muy corta: {word_count} palabras (mín: {min_words})"
    if word_count > max_words:
        return False, f"Respuesta muy larga: {word_count} palabras (máx: {max_words})"
    
    return True, f"Longitud apropiada: {word_count} palabras"
```

---

### Problema 4: Tono inconsistente o inapropiado

**Síntomas:**
- Uso de lenguaje de hedging
- Tono demasiado formal o casual
- Falta de neutralidad en temas controvertidos
- Uso de emojis o lenguaje informal

**Diagnóstico:**
1. Revisar sección restrictions
2. Verificar ejemplos de tono
3. Confirmar que las restricciones sean claras

**Soluciones:**

**Solución A: Refuerzo de Restricciones**
```
Añadir lista expandida de frases prohibidas:
- "It is important to..."
- "It is inappropriate..."
- "It is subjective..."
- "One might argue..."
- "It should be noted..."
```

**Solución B: Validación de Tono**
```python
def validate_tone(text):
    """Valida tono de la respuesta"""
    prohibited_phrases = [
        "it is important to",
        "it is inappropriate",
        "it is subjective",
        "one might argue",
        "it should be noted"
    ]
    
    text_lower = text.lower()
    violations = []
    
    for phrase in prohibited_phrases:
        if phrase in text_lower:
            violations.append(phrase)
    
    # Verificar emojis
    import re
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map
        u"\U0001F1E0-\U0001F1FF"  # flags
        "]+", flags=re.UNICODE)
    
    if emoji_pattern.search(text):
        violations.append("emojis encontrados")
    
    return len(violations) == 0, violations
```

---

### Problema 5: Manejo incorrecto de tipos de consulta

**Síntomas:**
- Respuestas académicas demasiado breves
- Noticias sin agrupación por temas
- Código sin bloques apropiados
- Traducciones con citas

**Diagnóstico:**
1. Verificar identificación del tipo de consulta
2. Revisar instrucciones específicas del tipo
3. Confirmar que las reglas especiales se apliquen

**Soluciones:**

**Solución A: Mejora en Identificación**
```
Añadir lógica explícita para identificar tipos:
- Palabras clave por tipo
- Patrones de consulta
- Contexto de la pregunta
```

**Solución B: Validación por Tipo**
```python
def validate_by_query_type(text, query_type, query):
    """Valida respuesta según tipo de consulta"""
    
    if query_type == 'academic':
        # Debe tener secciones, citas detalladas
        if '##' not in text:
            return False, "Falta estructura de secciones"
        if text.count('[') < 5:
            return False, "Faltan citas suficientes"
    
    elif query_type == 'news':
        # Debe tener listas con títulos
        if '- **' not in text and '##' not in text:
            return False, "Falta formato de lista con títulos"
    
    elif query_type == 'coding':
        # Debe tener bloques de código
        if '```' not in text:
            return False, "Falta bloque de código"
    
    elif query_type == 'translation':
        # No debe tener citas
        if '[' in text and ']' in text:
            return False, "Traducción no debe tener citas"
    
    return True, "Formato correcto para tipo"
```

---

### Problema 6: Problemas con expresiones matemáticas

**Síntomas:**
- Uso de $ en lugar de \(
- Expresiones en Unicode
- Faltan citas en fórmulas
- Formato inconsistente

**Diagnóstico:**
1. Verificar sección Mathematical Expressions
2. Confirmar ejemplos proporcionados
3. Revisar validación de formato

**Soluciones:**

**Solución A: Validación de LaTeX**
```python
def validate_latex(text):
    """Valida formato LaTeX"""
    import re
    
    # Buscar $ o $$
    dollar_pattern = r'\$[^$]+\$'
    if re.search(dollar_pattern, text):
        return False, "Encontrado $ en lugar de \\( o \\["
    
    # Verificar formato correcto
    inline_pattern = r'\\\([^)]+\\\)'
    block_pattern = r'\\\[[^\]]+\\\]'
    
    # Buscar expresiones matemáticas sin formato
    math_keywords = ['sin', 'cos', 'tan', 'log', 'exp', 'sqrt', 'sum', 'int']
    for keyword in math_keywords:
        if keyword in text.lower():
            # Verificar que esté en formato LaTeX
            if not re.search(inline_pattern, text) and not re.search(block_pattern, text):
                return False, f"Expresión matemática '{keyword}' sin formato LaTeX"
    
    return True, "Formato LaTeX correcto"
```

---

## Checklist de Diagnóstico Rápido

### Antes de Implementar
- [ ] Prompt completo incluido (todas las secciones)
- [ ] Formato XML correcto en secciones
- [ ] Sin caracteres corruptos
- [ ] Ejemplos incluidos si es necesario

### Durante la Implementación
- [ ] Validación de formato activa
- [ ] Logging de respuestas habilitado
- [ ] Métricas de calidad configuradas
- [ ] Sistema de alertas funcionando

### Después de Implementar
- [ ] Pruebas con diferentes tipos de consulta
- [ ] Validación de citaciones
- [ ] Verificación de formato
- [ ] Revisión de tono y estilo

---

## Herramientas de Validación

### Script de Validación Completa

```python
class PerplexityV3Validator:
    """Validador completo para respuestas del prompt v3"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate(self, text, query_type=None, query=""):
        """Valida respuesta completa"""
        self.errors = []
        self.warnings = []
        
        # Validaciones básicas
        self._validate_structure(text)
        self._validate_citations(text)
        self._validate_tone(text)
        self._validate_format(text)
        
        # Validaciones por tipo
        if query_type:
            self._validate_by_type(text, query_type, query)
        
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings
        }
    
    def _validate_structure(self, text):
        """Valida estructura básica"""
        # No debe empezar con header
        if text.strip().startswith('##'):
            self.errors.append("Respuesta comienza con header")
        
        # Debe tener contenido sustancial
        if len(text.split()) < 50:
            self.warnings.append("Respuesta muy corta")
    
    def _validate_citations(self, text):
        """Valida formato de citaciones"""
        import re
        # Formato incorrecto [12, 13]
        if re.search(r'\[\d+,\s*\d+\]', text):
            self.errors.append("Formato de cita incorrecto: usar [12][13]")
        
        # Espacio antes de cita
        if re.search(r'\w\[', text):
            self.errors.append("Falta espacio antes de cita")
    
    def _validate_tone(self, text):
        """Valida tono apropiado"""
        prohibited = [
            "it is important to",
            "it is inappropriate",
            "it is subjective"
        ]
        
        text_lower = text.lower()
        for phrase in prohibited:
            if phrase in text_lower:
                self.errors.append(f"Frase prohibida encontrada: '{phrase}'")
    
    def _validate_format(self, text):
        """Valida formato general"""
        # Verificar emojis
        import re
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            "]+", flags=re.UNICODE)
        
        if emoji_pattern.search(text):
            self.errors.append("Emojis encontrados (prohibidos)")
    
    def _validate_by_type(self, text, query_type, query):
        """Valida según tipo de consulta"""
        if query_type == 'coding' and '```' not in text:
            self.errors.append("Tipo 'coding' requiere bloques de código")
        
        if query_type == 'translation' and '[' in text:
            self.warnings.append("Traducciones no deberían tener citas")
```

---

## Prevención de Problemas

### Mejores Prácticas

1. **Testing Exhaustivo**
   - Probar con todos los tipos de consulta
   - Validar casos edge
   - Revisar respuestas de muestra regularmente

2. **Monitoreo Continuo**
   - Implementar métricas de calidad
   - Alertas para respuestas fuera de formato
   - Revisión periódica de logs

3. **Documentación**
   - Mantener ejemplos actualizados
   - Documentar casos especiales
   - Compartir lecciones aprendidas

4. **Iteración**
   - Ajustar prompt basado en feedback
   - Mejorar validaciones
   - Actualizar ejemplos

---

## Recursos Adicionales

- `perplexity_prompt_enhanced_v3.md` - Prompt completo
- `perplexity_prompt_v3_examples.md` - Ejemplos por tipo
- `perplexity_prompt_v3_testing_suite.md` - Suite de pruebas
- `perplexity_prompt_v3_best_practices.md` - Mejores prácticas

---

**Última actualización:** 2025-05-13  
**Versión:** 1.0

