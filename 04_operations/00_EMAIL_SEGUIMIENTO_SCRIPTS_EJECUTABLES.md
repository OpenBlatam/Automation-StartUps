# 💻 Scripts Ejecutables Completos

## 🎯 Scripts Python Listos para Usar

### 1. Calculadora de ROI Personalizada

```python
#!/usr/bin/env python3
"""
Calculadora de ROI Personalizada para Prospectos
Uso: python calcular_roi.py --horas 15 --tarifa 25 --porcentaje 80
"""

import argparse
from datetime import datetime

def calcular_roi(horas_semanales, tarifa_hora, tareas_automatizables, precio_producto=100):
    """
    Calcula ROI personalizado para prospecto
    
    Args:
        horas_semanales: Horas que pasa en tareas automatizables
        tarifa_hora: Tarifa por hora del prospecto
        tareas_automatizables: % de tareas que se pueden automatizar
        precio_producto: Precio mensual del producto
    
    Returns:
        dict con cálculos de ROI
    """
    horas_mes = horas_semanales * 4
    horas_automatizables = horas_mes * (tareas_automatizables / 100)
    costo_actual = horas_automatizables * tarifa_hora
    
    # Con IA: 70% de reducción
    horas_ia = horas_automatizables * 0.3
    costo_ia = horas_ia * tarifa_hora
    
    ahorro_mensual = costo_actual - costo_ia
    ahorro_anual = ahorro_mensual * 12
    
    # ROI sobre inversión
    roi_mensual = (ahorro_mensual / precio_producto) * 100
    roi_anual = (ahorro_anual / (precio_producto * 12)) * 100
    
    # Tiempo de recuperación
    meses_recuperacion = precio_producto / ahorro_mensual
    
    return {
        'horas_actuales_mes': round(horas_automatizables, 2),
        'costo_actual_mes': round(costo_actual, 2),
        'horas_con_ia_mes': round(horas_ia, 2),
        'costo_con_ia_mes': round(costo_ia, 2),
        'ahorro_mensual': round(ahorro_mensual, 2),
        'ahorro_anual': round(ahorro_anual, 2),
        'roi_mensual': round(roi_mensual, 1),
        'roi_anual': round(roi_anual, 1),
        'meses_recuperacion': round(meses_recuperacion, 1)
    }

def generar_reporte_roi(resultado, nombre_prospecto):
    """
    Genera reporte de ROI formateado
    """
    reporte = f"""
╔══════════════════════════════════════════════════════════╗
║       REPORTE DE ROI PERSONALIZADO                      ║
║       Para: {nombre_prospecto:<30}    ║
╚══════════════════════════════════════════════════════════╝

📊 SITUACIÓN ACTUAL:
   • Horas/mes en tareas automatizables: {resultado['horas_actuales_mes']}h
   • Costo mensual actual: ${resultado['costo_actual_mes']:,.2f}

🤖 CON IA:
   • Horas/mes necesarias: {resultado['horas_con_ia_mes']}h
   • Costo mensual con IA: ${resultado['costo_con_ia_mes']:,.2f}

💰 AHORRO:
   • Mensual: ${resultado['ahorro_mensual']:,.2f}
   • Anual: ${resultado['ahorro_anual']:,.2f}

📈 ROI:
   • Mensual: {resultado['roi_mensual']:.1f}%
   • Anual: {resultado['roi_anual']:.1f}%

⏱️  RECUPERACIÓN:
   • El producto se paga solo en: {resultado['meses_recuperacion']:.1f} meses

═══════════════════════════════════════════════════════════
"""
    return reporte

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculadora de ROI Personalizada')
    parser.add_argument('--horas', type=float, required=True, help='Horas semanales en tareas automatizables')
    parser.add_argument('--tarifa', type=float, required=True, help='Tarifa por hora')
    parser.add_argument('--porcentaje', type=float, default=80, help='Porcentaje de tareas automatizables (default: 80)')
    parser.add_argument('--precio', type=float, default=100, help='Precio mensual del producto (default: 100)')
    parser.add_argument('--nombre', type=str, default='Prospecto', help='Nombre del prospecto')
    
    args = parser.parse_args()
    
    resultado = calcular_roi(args.horas, args.tarifa, args.porcentaje, args.precio)
    reporte = generar_reporte_roi(resultado, args.nombre)
    
    print(reporte)
    
    # Guardar en archivo
    with open(f'roi_{args.nombre.replace(" ", "_")}.txt', 'w') as f:
        f.write(reporte)
    
    print(f"✅ Reporte guardado en: roi_{args.nombre.replace(' ', '_')}.txt")
```

**Uso:**
```bash
python calcular_roi.py --horas 15 --tarifa 25 --porcentaje 80 --precio 100 --nombre "Juan Pérez"
```

---

### 2. Asignador Inteligente de Testimonios

```python
#!/usr/bin/env python3
"""
Asignador Inteligente de Testimonios
Asigna el mejor testimonial basado en similitud con prospecto
"""

import json
from typing import Dict, List

class Testimonial:
    def __init__(self, id, nombre, industria, rol, tamaño_empresa, 
                 disponible_charlas, tiene_video, conversion_historica):
        self.id = id
        self.nombre = nombre
        self.industria = industria
        self.rol = rol
        self.tamaño_empresa = tamaño_empresa
        self.disponible_charlas = disponible_charlas
        self.tiene_video = tiene_video
        self.conversion_historica = conversion_historica

class Prospecto:
    def __init__(self, nombre, industria, rol, tamaño_empresa):
        self.nombre = nombre
        self.industria = industria
        self.rol = rol
        self.tamaño_empresa = tamaño_empresa

def asignar_testimonial(prospecto: Prospecto, testimonios: List[Testimonial]) -> List[Testimonial]:
    """
    Asigna los mejores testimonios basado en similitud
    Retorna top 3 testimonios
    """
    scores = {}
    
    for testimonial in testimonios:
        score = 0
        
        # Match de industria (30 puntos)
        if testimonial.industria == prospecto.industria:
            score += 30
        
        # Match de rol (25 puntos)
        if testimonial.rol == prospecto.rol:
            score += 25
        
        # Match de tamaño empresa (20 puntos)
        if testimonial.tamaño_empresa == prospecto.tamaño_empresa:
            score += 20
        
        # Disponible para charlas (15 puntos)
        if testimonial.disponible_charlas:
            score += 15
        
        # Tiene video (10 puntos)
        if testimonial.tiene_video:
            score += 10
        
        # Conversión histórica (10 puntos máx)
        score += min(testimonial.conversion_historica * 10, 10)
        
        scores[testimonial.id] = (score, testimonial)
    
    # Ordenar por score
    sorted_testimonials = sorted(scores.values(), key=lambda x: x[0], reverse=True)
    
    # Retornar top 3
    return [t[1] for t in sorted_testimonials[:3]]

# Ejemplo de uso
if __name__ == "__main__":
    # Cargar testimonios (en producción, desde base de datos)
    testimonios = [
        Testimonial(1, "María García", "Marketing", "Director", "50-100", True, True, 0.18),
        Testimonial(2, "Carlos López", "Consultoría", "Freelancer", "1-10", False, True, 0.15),
        Testimonial(3, "Ana Martínez", "Tech", "Emprendedor", "10-50", True, False, 0.20),
    ]
    
    # Prospecto
    prospecto = Prospecto("Juan Pérez", "Marketing", "Director", "50-100")
    
    # Asignar
    mejores = asignar_testimonial(prospecto, testimonios)
    
    print(f"✅ Testimonios asignados para {prospecto.nombre}:")
    for i, testimonial in enumerate(mejores, 1):
        print(f"\n{i}. {testimonial.nombre} ({testimonial.industria}, {testimonial.rol})")
        print(f"   Disponible para charlas: {'Sí' if testimonial.disponible_charlas else 'No'}")
        print(f"   Video: {'Sí' if testimonial.tiene_video else 'No'}")
```

---

### 3. Optimizador de Timing de Emails

```python
#!/usr/bin/env python3
"""
Optimizador de Timing de Emails
Analiza datos históricos y recomienda mejor hora/día para enviar
"""

import pandas as pd
from datetime import datetime, timedelta
import json

def analizar_timing_optimo(datos_historicos: pd.DataFrame) -> Dict:
    """
    Analiza datos históricos y determina mejor timing
    """
    # Análisis por día de semana
    datos_historicos['dia_semana'] = pd.to_datetime(datos_historicos['fecha_envio']).dt.day_name()
    datos_historicos['hora'] = pd.to_datetime(datos_historicos['fecha_envio']).dt.hour
    
    # Performance por día
    performance_dia = datos_historicos.groupby('dia_semana').agg({
        'open_rate': 'mean',
        'ctr': 'mean',
        'conversion': 'mean'
    }).sort_values('conversion', ascending=False)
    
    # Performance por hora
    performance_hora = datos_historicos.groupby('hora').agg({
        'open_rate': 'mean',
        'ctr': 'mean',
        'conversion': 'mean'
    }).sort_values('conversion', ascending=False)
    
    # Mejor combinación
    mejor_dia = performance_dia.index[0]
    mejor_hora = performance_hora.index[0]
    
    return {
        'mejor_dia': mejor_dia,
        'mejor_hora': mejor_hora,
        'performance_dia': performance_dia.to_dict(),
        'performance_hora': performance_hora.to_dict(),
        'recomendacion': f"Enviar los {mejor_dia}s a las {mejor_hora}:00"
    }

if __name__ == "__main__":
    # Ejemplo de datos (en producción, desde base de datos)
    datos = pd.DataFrame({
        'fecha_envio': pd.date_range('2024-01-01', periods=100, freq='D'),
        'open_rate': [0.35 + (i % 7) * 0.05 for i in range(100)],
        'ctr': [0.15 + (i % 7) * 0.03 for i in range(100)],
        'conversion': [0.10 + (i % 7) * 0.02 for i in range(100)]
    })
    
    resultado = analizar_timing_optimo(datos)
    
    print("✅ Análisis de Timing Óptimo:")
    print(f"\n📅 Mejor día: {resultado['mejor_dia']}")
    print(f"🕐 Mejor hora: {resultado['mejor_hora']}:00")
    print(f"\n💡 Recomendación: {resultado['recomendacion']}")
```

---

### 4. Generador Automático de Emails Personalizados

```python
#!/usr/bin/env python3
"""
Generador Automático de Emails Personalizados
Genera emails usando templates y datos del prospecto
"""

import json
from typing import Dict

class EmailGenerator:
    def __init__(self):
        self.templates = {
            'roi': {
                'asunto': '{nombre}, el cálculo que nadie hace con IA',
                'cuerpo': self._template_roi
            },
            'social_proof': {
                'asunto': '{nombre}, esto es lo que dicen nuestros clientes',
                'cuerpo': self._template_social_proof
            },
            'urgencia': {
                'asunto': '{nombre}, última oportunidad: {dias_restantes} días',
                'cuerpo': self._template_urgencia
            }
        }
    
    def _template_roi(self, prospecto: Dict) -> str:
        return f"""
Hola {prospecto['nombre']},

Sé que recibiste mi propuesta anterior y probablemente estás evaluando varias opciones.

**Pero hay algo que tal vez no mencioné antes** — y es el cálculo que nadie hace cuando evalúa invertir en IA.

**ROI PERSONALIZADO PARA {prospecto['industria'].upper()}:**

Sin IA:
- {prospecto.get('horas_mes', 60)} horas/mes = ${prospecto.get('costo_actual', 1200):,.2f}/mes

Con IA:
- {prospecto.get('horas_ia', 20)} horas/mes = ${prospecto.get('costo_ia', 400):,.2f}/mes

**Ahorro: ${prospecto.get('ahorro_mes', 800):,.2f}/mes = ${prospecto.get('ahorro_anual', 9600):,.2f}/año**

¿Quieres ver tu cálculo personalizado?
[Agendar llamada de 15 min]

Saludos,
{prospecto.get('tu_nombre', 'Tu nombre')}
"""
    
    def _template_social_proof(self, prospecto: Dict) -> str:
        return f"""
Hola {prospecto['nombre']},

Sé que estás evaluando opciones. Completamente comprensible.

**Pero déjame compartirte algo que tal vez cambie tu perspectiva:**

{prospecto.get('testimonial_nombre', 'María')}, {prospecto.get('testimonial_rol', 'Directora')} en {prospecto.get('testimonial_empresa', 'Empresa')}:

"{prospecto.get('testimonial_texto', 'Testimonial aquí')}"

**Resultados específicos:**
- {prospecto.get('resultado_1', 'Resultado 1')}
- {prospecto.get('resultado_2', 'Resultado 2')}
- {prospecto.get('resultado_3', 'Resultado 3')}

¿Quieres hablar con {prospecto.get('testimonial_nombre', 'María')} directamente?
[Agendar llamada]

Saludos,
{prospecto.get('tu_nombre', 'Tu nombre')}
"""
    
    def _template_urgencia(self, prospecto: Dict) -> str:
        return f"""
Hola {prospecto['nombre']},

Sé que estás evaluando opciones. Completamente comprensible.

**Pero hay algo que tal vez no mencioné antes:**

La oferta early bird cierra en {prospecto.get('dias_restantes', 3)} días.

**Lo que significa:**
- Descuento: {prospecto.get('descuento', 20)}% OFF
- Ahorro: ${prospecto.get('ahorro', 200):,.2f}
- Plazas restantes: {prospecto.get('plazas_restantes', 5)}

**Costo de esperar:**
Si esperas, perderás:
- ${prospecto.get('costo_esperar', 100):,.2f} en descuento
- {prospecto.get('dias_esperar', 30)} días de implementación
- Ventaja competitiva

[Agendar llamada ahora - Solo {prospecto.get('dias_restantes', 3)} días restantes]

Saludos,
{prospecto.get('tu_nombre', 'Tu nombre')}
"""
    
    def generar(self, tipo: str, prospecto: Dict) -> Dict:
        """
        Genera email personalizado
        """
        if tipo not in self.templates:
            raise ValueError(f"Tipo de email no válido: {tipo}")
        
        template = self.templates[tipo]
        
        # Generar asunto
        asunto = template['asunto'].format(**prospecto)
        
        # Generar cuerpo
        cuerpo = template['cuerpo'](prospecto)
        
        return {
            'asunto': asunto,
            'cuerpo': cuerpo,
            'tipo': tipo,
            'prospecto': prospecto['nombre']
        }

# Ejemplo de uso
if __name__ == "__main__":
    generator = EmailGenerator()
    
    prospecto = {
        'nombre': 'Juan Pérez',
        'industria': 'Marketing',
        'horas_mes': 60,
        'costo_actual': 1200,
        'horas_ia': 20,
        'costo_ia': 400,
        'ahorro_mes': 800,
        'ahorro_anual': 9600,
        'tu_nombre': 'Tu Nombre'
    }
    
    email = generator.generar('roi', prospecto)
    
    print("✅ Email generado:")
    print(f"\n📧 Asunto: {email['asunto']}")
    print(f"\n📝 Cuerpo:\n{email['cuerpo']}")
```

---

### 5. Analizador de Performance de Emails

```python
#!/usr/bin/env python3
"""
Analizador de Performance de Emails
Analiza métricas y genera insights
"""

import pandas as pd
from typing import Dict, List

def analizar_performance(datos: pd.DataFrame) -> Dict:
    """
    Analiza performance de emails y genera insights
    """
    # Métricas generales
    metricas = {
        'total_enviados': len(datos),
        'open_rate': datos['abierto'].mean() * 100,
        'ctr': (datos['click'].sum() / datos['abierto'].sum()) * 100 if datos['abierto'].sum() > 0 else 0,
        'conversion': (datos['convertido'].sum() / datos['abierto'].sum()) * 100 if datos['abierto'].sum() > 0 else 0,
    }
    
    # Análisis por email
    if 'email_id' in datos.columns:
        performance_por_email = datos.groupby('email_id').agg({
            'abierto': 'sum',
            'click': 'sum',
            'convertido': 'sum'
        })
        performance_por_email['open_rate'] = (performance_por_email['abierto'] / datos.groupby('email_id')['enviado'].sum()) * 100
        performance_por_email['ctr'] = (performance_por_email['click'] / performance_por_email['abierto']) * 100
        performance_por_email['conversion'] = (performance_por_email['convertido'] / performance_por_email['abierto']) * 100
        
        metricas['performance_por_email'] = performance_por_email.to_dict('index')
    
    # Identificar problemas
    problemas = []
    if metricas['open_rate'] < 30:
        problemas.append({
            'tipo': 'open_rate_bajo',
            'severidad': 'alta',
            'solucion': 'A/B test de asuntos, cambiar timing, limpiar lista'
        })
    
    if metricas['ctr'] < 12:
        problemas.append({
            'tipo': 'ctr_bajo',
            'severidad': 'alta',
            'solucion': 'Mejorar CTAs, optimizar copy, clarificar valor'
        })
    
    if metricas['conversion'] < 8:
        problemas.append({
            'tipo': 'conversion_baja',
            'severidad': 'critica',
            'solucion': 'Revisar proceso completo, optimizar landing page, resolver objeciones'
        })
    
    metricas['problemas'] = problemas
    
    return metricas

# Ejemplo de uso
if __name__ == "__main__":
    # Datos de ejemplo
    datos = pd.DataFrame({
        'email_id': ['email_1', 'email_2', 'email_3'] * 100,
        'enviado': [1] * 300,
        'abierto': [0.4, 0.45, 0.42] * 100,
        'click': [0.08, 0.10, 0.09] * 100,
        'convertido': [0.05, 0.06, 0.05] * 100
    })
    
    resultado = analizar_performance(datos)
    
    print("✅ Análisis de Performance:")
    print(f"\n📊 Métricas Generales:")
    print(f"   • Total enviados: {resultado['total_enviados']}")
    print(f"   • Open Rate: {resultado['open_rate']:.2f}%")
    print(f"   • CTR: {resultado['ctr']:.2f}%")
    print(f"   • Conversión: {resultado['conversion']:.2f}%")
    
    if resultado['problemas']:
        print(f"\n⚠️  Problemas Identificados:")
        for problema in resultado['problemas']:
            print(f"   • {problema['tipo']} (Severidad: {problema['severidad']})")
            print(f"     Solución: {problema['solucion']}")
```

---

## 📋 Instrucciones de Uso

### Setup Inicial:

```bash
# Crear directorio
mkdir email_scripts
cd email_scripts

# Crear archivos
touch calcular_roi.py
touch asignar_testimonial.py
touch optimizar_timing.py
touch generar_email.py
touch analizar_performance.py

# Instalar dependencias
pip install pandas numpy
```

### Ejecutar Scripts:

```bash
# Calculadora de ROI
python calcular_roi.py --horas 15 --tarifa 25 --porcentaje 80 --nombre "Juan Pérez"

# Asignador de Testimonios
python asignar_testimonial.py

# Optimizador de Timing
python optimizar_timing.py

# Generador de Emails
python generar_email.py

# Analizador de Performance
python analizar_performance.py
```

---

**Scripts ejecutables listos para usar inmediatamente.** 🚀

