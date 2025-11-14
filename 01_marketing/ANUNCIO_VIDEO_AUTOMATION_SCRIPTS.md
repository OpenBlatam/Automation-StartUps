# Scripts de Automatización — Generación de Variantes

> Scripts Python/JavaScript para automatizar la generación de variantes de anuncios, batch processing y exportación.

---

## 🐍 Python Scripts

### 1. Generador de Variantes de Guiones

```python
#!/usr/bin/env python3
"""
Genera variantes de guiones VO basado en templates y hooks.
"""

import json
from datetime import datetime
from typing import Dict, List

# Configuración
PRODUCTOS = {
    "curso_ia": {
        "nombre": "[NOMBRE DEL PRODUCTO - Curso]",
        "hooks": [
            "IA aplicable en 4 semanas",
            "¿IA confusa? Método claro",
            "Webinar en vivo incluido",
            "Cupos limitados, entra hoy"
        ],
        "ctas": ["Inscríbete hoy", "Compra ahora", "Reserva tu lugar"],
        "slogan": "[ESLOGAN]"
    },
    "saas_marketing": {
        "nombre": "[NOMBRE DEL PRODUCTO - SaaS]",
        "hooks": [
            "30 piezas en 5 min",
            "-60% tiempo | +ROI",
            "Publica con 1 clic",
            "Sin retrabajo, sin inconsistencias"
        ],
        "ctas": ["Probar gratis", "Solicitar demo", "Empieza hoy"],
        "slogan": "[ESLOGAN]"
    },
    "ia_bulk": {
        "nombre": "[NOMBRE DEL PRODUCTO - Bulk]",
        "hooks": [
            "¿100 docs? 1 consulta.",
            "Plantillas + variables",
            "Exporta al instante",
            "Sin trabajo repetitivo"
        ],
        "ctas": ["Compra ahora", "Empieza hoy", "Solicitar demo"],
        "slogan": "[ESLOGAN]"
    }
}

TEMPLATES_VO = {
    "directo": """¿Listo para {beneficio}? {producto} te guía con {proceso}. {valor_extra}. {cta}. {slogan}.""",
    "inspiracional": """Menos {dolor}, más {resultado}. {proceso_corto}. Empieza hoy con {producto}. {slogan}.""",
    "ugc": """Probé {producto}. {testimonio_corto}. {beneficio_clave}. {cta}. {slogan}."""
}

def generar_guion_vo(producto: str, hook: str, cta: str, tono: str = "directo") -> str:
    """Genera guion VO completo."""
    config = PRODUCTOS[producto]
    template = TEMPLATES_VO[tono]
    
    # Mapeo de variables según producto
    variables = {
        "curso_ia": {
            "beneficio": "dominar IA en semanas, no meses",
            "proceso": "clases prácticas, proyectos reales y webinar en vivo",
            "valor_extra": "Certificado y acceso de por vida",
            "dolor": "duda",
            "resultado": "práctica",
            "proceso_corto": "De cero a resultados con mentoría",
            "testimonio_corto": "En 2 semanas ya aplicaba IA",
            "beneficio_clave": "El webinar me despejó todo"
        },
        "saas_marketing": {
            "beneficio": "crear campañas completas en minutos",
            "proceso": "brief a copies, creativos y calendario",
            "valor_extra": "Integra y publica con 1 clic",
            "dolor": "fricción",
            "resultado": "impacto",
            "proceso_corto": "Del brief a campañas listas",
            "testimonio_corto": "En 5 minutos tenía 30 piezas",
            "beneficio_clave": "Publiqué desde la app"
        },
        "ia_bulk": {
            "beneficio": "generar 100 documentos con una consulta",
            "proceso": "plantillas, variables y validación",
            "valor_extra": "Exporta y comparte al instante",
            "dolor": "repetición",
            "resultado": "escala",
            "proceso_corto": "Estandariza y valida",
            "testimonio_corto": "Pegué una consulta y listo",
            "beneficio_clave": "Revisé solo 3 campos"
        }
    }
    
    params = variables[producto].copy()
    params.update({
        "producto": config["nombre"],
        "cta": cta,
        "slogan": config["slogan"],
        "hook": hook
    })
    
    guion = template.format(**params)
    return guion

def generar_combinaciones(producto: str) -> List[Dict]:
    """Genera todas las combinaciones Hook × CTA."""
    config = PRODUCTOS[producto]
    combinaciones = []
    
    for hook in config["hooks"]:
        for cta in config["ctas"]:
            for tono in ["directo", "inspiracional", "ugc"]:
                guion = generar_guion_vo(producto, hook, cta, tono)
                combinaciones.append({
                    "producto": producto,
                    "hook": hook,
                    "cta": cta,
                    "tono": tono,
                    "guion_vo": guion,
                    "palabras": len(guion.split()),
                    "duracion_estimada": len(guion.split()) / 2.5  # ~2.5 palabras/segundo
                })
    
    return combinaciones

def exportar_markdown(combinaciones: List[Dict], producto: str, output_file: str):
    """Exporta combinaciones a markdown."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Guiones VO Generados — {PRODUCTOS[producto]['nombre']}\n\n")
        f.write(f"**Generado**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("---\n\n")
        
        for i, combo in enumerate(combinaciones, 1):
            f.write(f"## Variante {i}\n\n")
            f.write(f"- **Hook**: {combo['hook']}\n")
            f.write(f"- **CTA**: {combo['cta']}\n")
            f.write(f"- **Tono**: {combo['tono']}\n")
            f.write(f"- **Palabras**: {combo['palabras']}\n")
            f.write(f"- **Duración estimada**: ~{combo['duracion_estimada']:.1f}s\n\n")
            f.write(f"### Guion VO\n\n```\n{combo['guion_vo']}\n```\n\n")
            f.write("---\n\n")

if __name__ == "__main__":
    # Generar para todos los productos
    for producto in PRODUCTOS.keys():
        combinaciones = generar_combinaciones(producto)
        output_file = f"guiones_vo_{producto}_{datetime.now().strftime('%Y%m%d')}.md"
        exportar_markdown(combinaciones, producto, output_file)
        print(f"✅ Generado: {output_file} ({len(combinaciones)} variantes)")

```

---

### 2. Batch Processor de SRT (Subtítulos)

```python
#!/usr/bin/env python3
"""
Genera archivos SRT a partir de timecodes y textos.
"""

def generar_srt(timecodes: List[Dict], output_file: str):
    """
    Genera archivo SRT.
    
    timecodes format:
    [
        {"start": "00:00:00,000", "end": "00:00:01,000", "text": "Hook principal"},
        ...
    ]
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, tc in enumerate(timecodes, 1):
            f.write(f"{i}\n")
            f.write(f"{tc['start']} --> {tc['end']}\n")
            f.write(f"{tc['text']}\n\n")

# Ejemplo uso
timecodes_curso = [
    {"start": "00:00:00,000", "end": "00:00:01,000", "text": "Domina IA en 4 semanas"},
    {"start": "00:00:01,000", "end": "00:00:03,200", "text": "Clases prácticas con proyectos reales"},
    {"start": "00:00:03,200", "end": "00:00:05,500", "text": "Webinar en vivo con Q&A"},
    {"start": "00:00:05,500", "end": "00:00:09,000", "text": "+2,000 alumnos | Certificado"},
    {"start": "00:00:09,000", "end": "00:00:12,500", "text": "Inscríbete hoy"},
    {"start": "00:00:12,500", "end": "00:00:15,000", "text": "[ESLOGAN]"}
]

generar_srt(timecodes_curso, "subtitles_curso_ia_es.srt")
```

---

### 3. Generador de CSV Markers (Premiere)

```python
#!/usr/bin/env python3
"""
Genera archivo CSV de markers para Premiere/CapCut.
"""

import csv
from typing import List, Dict

def generar_markers_csv(markers: List[Dict], output_file: str):
    """
    Genera CSV de markers.
    
    markers format:
    [
        {"name": "Hook", "start": "00:00:00:00", "duration": "00:00:01:12", "comment": "Hook principal"},
        ...
    ]
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Start", "Duration", "Comment"])
        
        for marker in markers:
            writer.writerow([
                marker["name"],
                marker["start"],
                marker["duration"],
                marker["comment"]
            ])

# Ejemplo
markers_curso = [
    {"name": "Hook", "start": "00:00:00:00", "duration": "00:00:01:12", "comment": "Domina IA en 4 semanas"},
    {"name": "Demo", "start": "00:00:01:12", "duration": "00:00:02:20", "comment": "Clases + Proyectos"},
    {"name": "Webinar", "start": "00:00:03:32", "duration": "00:00:02:16", "comment": "En vivo + Q&A"},
    {"name": "SocialProof", "start": "00:00:05:24", "duration": "00:00:03:04", "comment": "2000 alumnos"},
    {"name": "CTA_On", "start": "00:00:09:15", "duration": "00:00:03:05", "comment": "Compra ahora"},
    {"name": "Cierre", "start": "00:00:12:24", "duration": "00:00:02:06", "comment": "ESLOGAN"}
]

generar_markers_csv(markers_curso, "markers_curso_ia.csv")
```

---

## 📊 JavaScript (Node.js) — Validación de Metadatos

### 4. Validador de Metadata de Video

```javascript
/**
 * Valida metadata de video antes de exportar.
 */

const fs = require('fs');
const path = require('path');

const REQUIRED_METADATA = {
  plataforma: ['instagram', 'facebook', 'reels', 'stories'],
  producto: ['curso_ia', 'saas_marketing', 'ia_bulk'],
  version: ['v1', 'v2', 'v3'],
  formato: ['1080x1920', '1080x1080', '1080x1350'],
  duracion: 15,
  codec: 'H.264',
  audioCodec: 'AAC',
  bitrate: { min: 15, max: 20 },
  fps: 30
};

function validarMetadata(videoPath, metadata) {
  const errores = [];
  const advertencias = [];
  
  // Validar formato
  if (!REQUIRED_METADATA.formato.includes(metadata.formato)) {
    errores.push(`Formato inválido: ${metadata.formato}`);
  }
  
  // Validar duración (15s ± 0.1s)
  if (Math.abs(metadata.duracion - REQUIRED_METADATA.duracion) > 0.1) {
    errores.push(`Duración fuera de rango: ${metadata.duracion}s`);
  }
  
  // Validar bitrate
  if (metadata.bitrate < REQUIRED_METADATA.bitrate.min || 
      metadata.bitrate > REQUIRED_METADATA.bitrate.max) {
    advertencias.push(`Bitrate fuera del rango recomendado: ${metadata.bitrate} Mbps`);
  }
  
  // Validar naming
  const nombreEsperado = `${metadata.plataforma}-${metadata.producto}-15s-${metadata.version}.mp4`;
  if (!videoPath.includes(metadata.plataforma) || !videoPath.includes(metadata.producto)) {
    advertencias.push(`Nombre de archivo no sigue convención: ${nombreEsperado}`);
  }
  
  return { errores, advertencias, valido: errores.length === 0 };
}

// Ejemplo uso
const metadata = {
  plataforma: 'instagram',
  producto: 'curso_ia',
  version: 'v1',
  formato: '1080x1920',
  duracion: 15.0,
  bitrate: 18,
  fps: 30
};

const resultado = validarMetadata('instagram-curso-ia-15s-v1.mp4', metadata);
console.log(resultado);
```

---

## 🔄 Script de Batch Export (FFmpeg)

### 5. Batch Export con FFmpeg

```bash
#!/bin/bash
# batch_export_videos.sh
# Exporta todos los proyectos a video final con FFmpeg

INPUT_DIR="./proyectos"
OUTPUT_DIR="./exports"
FORMAT="1080x1920"
BITRATE="18M"
FPS=30

# Crear directorio de salida
mkdir -p "$OUTPUT_DIR"

# Procesar cada proyecto
for proyecto in "$INPUT_DIR"/*.aep "$INPUT_DIR"/*.prproj; do
    if [ -f "$proyecto" ]; then
        nombre=$(basename "$proyecto" | sed 's/\.[^.]*$//')
        output="$OUTPUT_DIR/${nombre}_${FORMAT}.mp4"
        
        echo "Exportando: $nombre"
        
        # FFmpeg export (requiere render previo)
        # Ajustar según tu pipeline
        ffmpeg -i "${proyecto%.*}_render.mov" \
            -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
            -c:v libx264 \
            -preset medium \
            -crf 23 \
            -b:v "$BITRATE" \
            -r "$FPS" \
            -c:a aac \
            -b:a 192k \
            -ar 48000 \
            "$output"
        
        echo "✅ Exportado: $output"
    fi
done

echo "✨ Batch export completado"
```

---

## 📝 Generador de UTM Links

### 6. Generador de Links con UTMs

```python
#!/usr/bin/env python3
"""
Genera links con UTMs para tracking de anuncios.
"""

from urllib.parse import urlencode

def generar_utm_link(
    base_url: str,
    plataforma: str,
    producto: str,
    version: str,
    hook: str,
    cta: str,
    medio: str = "video",
    term: str = ""
) -> str:
    """Genera link con UTMs completos."""
    
    params = {
        "utm_source": plataforma,
        "utm_medium": medio,
        "utm_campaign": f"{producto}_launch",
        "utm_content": f"{version}_{hook.lower().replace(' ', '_')}",
        "utm_term": term or f"{cta.lower().replace(' ', '_')}"
    }
    
    return f"{base_url}?{urlencode(params)}"

# Ejemplo
link = generar_utm_link(
    base_url="https://tusitio.com/curso-ia",
    plataforma="instagram",
    producto="curso_ia",
    version="v1",
    hook="IA aplicable en 4 semanas",
    cta="Inscríbete hoy",
    term="mx_7d"
)

print(link)
# https://tusitio.com/curso-ia?utm_source=instagram&utm_medium=video&utm_campaign=curso_ia_launch&utm_content=v1_ia_aplicable_en_4_semanas&utm_term=inscr%C3%ADbete_hoy
```

---

## 📊 Dashboard de Métricas (Script Helper)

### 7. Calculadora de Métricas Objetivo

```python
#!/usr/bin/env python3
"""
Calcula métricas objetivo y genera reporte.
"""

METRICAS_OBJETIVO = {
    "curso_ia": {
        "vtr_15s": 0.22,
        "ctr": 0.015,
        "lead_to_compra": 0.07
    },
    "saas_marketing": {
        "vtr_15s": 0.24,
        "ctr": 0.020,
        "free_to_active": 0.30
    },
    "ia_bulk": {
        "vtr_15s": 0.24,
        "ctr": 0.020,
        "demo_to_trial": 0.12
    }
}

def evaluar_performance(producto: str, metricas_reales: dict) -> dict:
    """Evalúa performance vs objetivo."""
    objetivos = METRICAS_OBJETIVO[producto]
    resultado = {}
    
    for metrica, valor_real in metricas_reales.items():
        objetivo = objetivos.get(metrica)
        if objetivo:
            diferencia = valor_real - objetivo
            porcentaje_diff = (diferencia / objetivo) * 100
            
            resultado[metrica] = {
                "real": valor_real,
                "objetivo": objetivo,
                "diferencia": diferencia,
                "porcentaje_diff": porcentaje_diff,
                "status": "✅" if valor_real >= objetivo else "⚠️"
            }
    
    return resultado

# Ejemplo
metricas = evaluar_performance("curso_ia", {
    "vtr_15s": 0.25,
    "ctr": 0.014,
    "lead_to_compra": 0.08
})

for metrica, data in metricas.items():
    print(f"{metrica}: {data['status']} {data['real']:.3f} (objetivo: {data['objetivo']:.3f})")
```

---

## ✅ Checklist de Uso de Scripts

- [ ] Python 3.8+ instalado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Placeholders reemplazados (`[NOMBRE DEL PRODUCTO]`, `[ESLOGAN]`, etc.)
- [ ] Rutas de archivos ajustadas
- [ ] Permisos de ejecución (`chmod +x script.py`)
- [ ] Outputs verificados

---

**Última actualización**: [FECHA]  
**Versión**: 1.0  
**Requisitos**: Python 3.8+, Node.js 14+ (opcional), FFmpeg (opcional)



