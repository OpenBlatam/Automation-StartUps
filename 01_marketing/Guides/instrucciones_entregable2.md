---
title: "Instrucciones Entregable2"
category: "01_marketing"
tags: ["business", "marketing"]
created: "2025-10-29"
path: "01_marketing/Guides/instrucciones_entregable2.md"
---

# INSTRUCCIONES PARA EL EJERCICIO 8 - SERIE DE FOURIER

## Código para SageMath Cell

Para obtener las 10 gráficas de las primeras 10 aproximaciones por serie de Fourier, debes:

1. Ir a https://sagecell.sagemath.org/
2. Copiar y pegar el siguiente código en la celda:

```sage
f = piecewise([((-pi,0), 0), ((0,pi), x)])
n = 1  # Cambiar este valor de 1 a 10
s = f.fourier_series_partial_sum(n)
plot(f,(-2*pi,2*pi), thickness=3) + plot(s,(x,-2*pi,2*pi), color='red', thickness=1)
```

3. Cambiar el valor de `n` de 1 a 10, evaluando cada vez para obtener las 10 gráficas solicitadas.

## Resultados Esperados

Las gráficas mostrarán:
- La función original $f(x)$ en azul (línea gruesa)
- Las aproximaciones por serie de Fourier en rojo (línea delgada)
- A medida que aumenta $n$, la aproximación roja se acercará más a la función original azul

---

# FORMATO DE ENTREGA

## Nombre del Archivo
El archivo Word debe llamarse: `Entregable2_[Apellido]_[Nombre].docx`

**Ejemplos:**
- `Entregable2_Garcia_Maria.docx`
- `Entregable2_Rodriguez_Juan.docx`
- `Entregable2_Lopez_Ana.docx`

## Estructura del Documento Word

### PARTE A: Reporte de Investigación
1. **Portada** (con todos los datos solicitados)
2. **Introducción** (mínimo 1 párrafo)
3. **Aplicaciones a la ingeniería en general y a tu carrera en particular** (mínimo 2 párrafos)
4. **Conclusiones** (mínimo 1 párrafo)

**Total mínimo: 3 cuartillas**

### PARTE B: Ejercicios
1. **Ejercicios de Métodos Anteriores** (7 ejercicios)
   - Ejercicio 1: Separación de Variables
   - Ejercicio 2: Ecuaciones Diferenciales Homogéneas
   - Ejercicio 3: Ecuaciones Diferenciales Exactas y Factor Integrante
   - Ejercicio 4: Ecuaciones Diferenciales Lineales de Primer Orden
   - Ejercicio 5: Lineales de Orden Superior Homogéneas
   - Ejercicio 6: Lineales de Orden Superior No Homogéneas
   - Ejercicio 7: Solución de EDO usando Transformada de Laplace

2. **Ejercicios Adicionales de Esta Semana** (3 ejercicios)
   - Ejercicio 8: Serie de Fourier (con las 10 gráficas)
   - Ejercicio 9: Ecuación Diferencial con Condiciones Iniciales
   - Ejercicio 10: Ecuación Diferencial Parcial

## Formato de Cada Ejercicio

Para cada ejercicio incluir:
1. **Enunciado** del problema
2. **Desarrollo** paso a paso de la solución
3. **Respuesta final** claramente marcada
4. **Gráficas** (para el ejercicio 8)

---

# NOTAS IMPORTANTES

## Personalización del Reporte
- **IMPORTANTE**: Necesitas especificar tu carrera para personalizar la sección "Aplicaciones específicas"
- Reemplaza `[TU CARRERA]` con tu carrera específica (Ingeniería Mecánica, Eléctrica, Química, Civil, etc.)

## Datos Personales
- Reemplaza todos los campos entre corchetes `[ ]` con tu información personal
- Incluye tu nombre completo, matrícula, nombre de la universidad, etc.

## Entrega
- Subir el archivo Word completo en la sección "7. Entregables y Test" → "ENTREGABLE 2"
- Asegúrate de que el archivo contenga ambas partes (A y B) en un solo documento

---

# RÚBRICA DE EVALUACIÓN

**Total: 30% de la calificación del curso**

### Criterios de Evaluación:
1. **Contenido del reporte** (calidad de la investigación)
2. **Resolución correcta de ejercicios** (métodos aplicados correctamente)
3. **Presentación y formato** (organización, claridad, ortografía)
4. **Aplicaciones específicas** (relevancia para tu carrera)
5. **Conclusiones** (reflexión personal sobre la importancia del tema)

### Puntos Clave:
- Cada ejercicio debe estar resuelto individualmente
- Las gráficas del ejercicio 8 deben ser incluidas
- El reporte debe ser específico para tu carrera
- El formato debe seguir las especificaciones dadas
