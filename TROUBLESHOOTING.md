# 🔧 Troubleshooting - Documentos BLATAM

Guía completa para resolver problemas comunes al usar Documentos BLATAM.

---

## 📋 Tabla de Contenidos

- [Problemas Comunes](#problemas-comunes)
- [Scripts y Herramientas](#scripts-y-herramientas)
- [Documentación](#documentación)
- [Integraciones](#integraciones)
- [Performance](#performance)
- [Soporte](#soporte)

---

## 🐛 Problemas Comunes

### Enlaces Rotos

**Síntoma**: Los enlaces en la documentación no funcionan o dan error 404.

**Solución**:
```bash
# 1. Verificar enlaces rotos
python 06_documentation/Scripts/find_broken_links.py

# 2. Revisar el reporte generado
cat exports/broken_links_report.txt

# 3. Corregir enlaces manualmente o usar script de corrección
```

**Prevención**:
- Usar rutas relativas en lugar de absolutas
- Validar enlaces antes de commit
- Ejecutar validación regularmente

---

### Frontmatter Inválido

**Síntoma**: Errores al procesar documentos Markdown, falta de metadatos.

**Síntomas**:
- Documentos sin categoría
- Tags faltantes
- Fechas incorrectas

**Solución**:
```bash
# 1. Validar frontmatter
python 06_documentation/Scripts/frontmatter_validator.py

# 2. Ver errores específicos
cat exports/frontmatter_errors.txt

# 3. Corregir manualmente o usar script de corrección automática
python 06_documentation/Scripts/add_frontmatter_min.py
```

**Formato Correcto**:
```yaml
---
title: "Título del Documento"
category: "categoria"
tags: ["tag1", "tag2"]
created: "2025-01-15"
updated: "2025-01-20"
path: "ruta/al/archivo.md"
---
```

---

### Archivos No Encontrados

**Síntoma**: No puedo encontrar un archivo o documento específico.

**Soluciones**:

1. **Usar búsqueda**:
```bash
# Buscar en todo el proyecto
grep -r "término_buscado" .

# O usar el índice
open 06_documentation/INDEX.md
```

2. **Navegar por estructura**:
```bash
# Ver estructura completa
tree -L 2

# O usar el script de organización
python organize_root_files.py --list
```

3. **Consultar glosario**:
```bash
open GLOSSARY.md
```

---

### Variables No Reemplazadas

**Síntoma**: Las variables `{{variable}}` no se reemplazan en templates.

**Solución**:
```bash
# 1. Verificar que el archivo de tokens existe
ls tokens.json

# 2. Verificar formato del archivo de tokens
cat tokens.json | python -m json.tool

# 3. Ejecutar script de reemplazo
node tools/apply_tokens.js

# 4. Verificar resultado
grep -r "{{" archivo_procesado.md
```

**Formato Correcto de tokens.json**:
```json
{
  "nombre": "María",
  "fecha": "15 de enero",
  "hora": "7:00 PM",
  "link": "https://ejemplo.com"
}
```

---

## 🔧 Scripts y Herramientas

### Scripts No Ejecutan

**Síntoma**: Error "command not found" o "permission denied".

**Soluciones**:

#### Python Scripts
```bash
# Verificar Python instalado
python3 --version

# Dar permisos de ejecución
chmod +x script.py

# Ejecutar con Python explícito
python3 script.py

# O instalar dependencias
pip install -r requirements.txt
```

#### Node.js Scripts
```bash
# Verificar Node.js instalado
node --version

# Instalar dependencias
npm install

# Ejecutar script
node script.js
```

#### Bash Scripts
```bash
# Dar permisos de ejecución
chmod +x script.sh

# Ejecutar
bash script.sh
# o
./script.sh
```

---

### Errores de Dependencias

**Síntoma**: "Module not found" o "Package not found".

**Solución**:
```bash
# Python
pip install -r requirements.txt
# o
pip3 install nombre_paquete

# Node.js
npm install
# o
npm install nombre_paquete

# Verificar instalación
pip list | grep nombre_paquete
npm list | grep nombre_paquete
```

---

### Scripts Lentos

**Síntoma**: Los scripts tardan mucho en ejecutarse.

**Optimizaciones**:
```bash
# 1. Usar modo verbose para ver qué hace
python script.py --verbose

# 2. Procesar en lotes más pequeños
python script.py --batch-size 100

# 3. Usar cache si está disponible
python script.py --use-cache

# 4. Procesar solo archivos modificados
python script.py --only-changed
```

---

## 📚 Documentación

### No Encuentro la Información

**Soluciones**:

1. **Usar el índice**:
```bash
open 06_documentation/INDEX.md
```

2. **Buscar en FAQ**:
```bash
open FAQ.md
# Buscar con Ctrl+F / Cmd+F
```

3. **Consultar glosario**:
```bash
open GLOSSARY.md
```

4. **Buscar en ejemplos**:
```bash
open EXAMPLES.md
```

---

### Documentación Desactualizada

**Síntoma**: La documentación no refleja el estado actual del proyecto.

**Solución**:
```bash
# 1. Verificar última actualización
grep "Última actualización" README.md

# 2. Revisar CHANGELOG
open CHANGELOG.md

# 3. Verificar fecha en frontmatter
grep "updated:" archivo.md

# 4. Actualizar si es necesario
# Editar campo "updated" en frontmatter
```

---

## 🔗 Integraciones

### Google Sheets No Funciona

**Síntoma**: Error al importar o conectar con Google Sheets.

**Soluciones**:

1. **Verificar permisos**:
   - Asegurar que la cuenta tiene acceso
   - Verificar permisos de la hoja de cálculo

2. **Verificar formato CSV**:
```bash
# Validar formato
head -5 archivo.csv

# Verificar encoding
file -I archivo.csv
```

3. **Revisar guía**:
```bash
open 06_documentation/README_Sheets_Import.md
```

---

### APIs No Responden

**Síntoma**: Errores al conectar con APIs externas.

**Soluciones**:

1. **Verificar API keys**:
```bash
# Verificar variables de entorno
echo $API_KEY

# O en archivo .env
cat .env | grep API_KEY
```

2. **Verificar límites de rate**:
   - Revisar límites de la API
   - Implementar retry con backoff
   - Usar cache cuando sea posible

3. **Verificar conectividad**:
```bash
# Test de conexión
curl https://api.ejemplo.com/health

# Verificar DNS
nslookup api.ejemplo.com
```

---

## ⚡ Performance

### Procesamiento Lento

**Síntoma**: Scripts o herramientas tardan mucho.

**Optimizaciones**:

1. **Procesar en paralelo**:
```python
from multiprocessing import Pool

def process_file(file):
    # Procesar archivo
    pass

with Pool(processes=4) as pool:
    pool.map(process_file, files)
```

2. **Usar cache**:
```python
import functools
import hashlib

@functools.lru_cache(maxsize=128)
def expensive_function(arg):
    # Función costosa
    pass
```

3. **Procesar solo cambios**:
```bash
# Usar git para detectar cambios
git diff --name-only HEAD

# Procesar solo archivos modificados
python script.py --only-changed
```

---

### Archivos Muy Grandes

**Síntoma**: Archivos muy grandes causan problemas de memoria.

**Soluciones**:

1. **Procesar en chunks**:
```python
def process_large_file(filename, chunk_size=1000):
    with open(filename, 'r') as f:
        while True:
            chunk = f.readlines(chunk_size)
            if not chunk:
                break
            process_chunk(chunk)
```

2. **Comprimir archivos**:
```bash
# Comprimir
gzip archivo.csv

# Descomprimir al leer
zcat archivo.csv.gz | python script.py
```

---

## 🆘 Soporte

### No Encuentro la Solución

**Pasos a seguir**:

1. **Buscar en documentación**:
   - [`FAQ.md`](FAQ.md)
   - [`Troubleshooting/`](06_documentation/Troubleshooting/)
   - [`BEST_PRACTICES.md`](BEST_PRACTICES.md)

2. **Revisar issues existentes**:
   - Buscar en el repositorio
   - Ver si alguien ya reportó el problema

3. **Crear un issue**:
   - Describe el problema claramente
   - Incluye pasos para reproducir
   - Agrega logs o mensajes de error
   - Especifica tu entorno (OS, versiones)

4. **Consultar la comunidad**:
   - Revisar discusiones
   - Preguntar en issues

---

### Reportar un Bug

**Template para reportar**:

```markdown
## Descripción del Problema
[Descripción clara del problema]

## Pasos para Reproducir
1. Paso 1
2. Paso 2
3. Paso 3

## Comportamiento Esperado
[Qué debería pasar]

## Comportamiento Actual
[Qué está pasando]

## Entorno
- OS: [macOS/Windows/Linux]
- Versión: [versión]
- Python/Node: [versión]

## Logs/Errores
```
[Pegar logs aquí]
```

## Información Adicional
[Cualquier otra información relevante]
```

---

## 🔍 Comandos Útiles de Diagnóstico

### Verificar Estado del Sistema

```bash
# Verificar estructura
tree -L 2 -d

# Verificar archivos importantes
ls -la README.md CONTRIBUTING.md

# Verificar scripts
ls -la *.py *.js *.sh

# Verificar dependencias
pip list
npm list
```

### Verificar Integridad

```bash
# Validar todos los documentos
python 06_documentation/Scripts/frontmatter_validator.py

# Verificar enlaces
python 06_documentation/Scripts/find_broken_links.py

# Analizar contenido
python 06_documentation/Scripts/analyze_content.py
```

### Limpiar y Resetear

```bash
# Limpiar archivos temporales
find . -name "*.tmp" -delete
find . -name "__pycache__" -type d -exec rm -r {} +

# Resetear configuración
rm .env
cp env.example .env

# Limpiar node_modules (si es necesario)
rm -rf node_modules
npm install
```

---

## 📚 Recursos Adicionales

- [`FAQ.md`](FAQ.md) - Preguntas frecuentes
- [`BEST_PRACTICES.md`](BEST_PRACTICES.md) - Mejores prácticas
- [`SETUP.md`](SETUP.md) - Configuración
- [`ARCHITECTURE.md`](ARCHITECTURE.md) - Estructura del proyecto

---

**¿No encuentras la solución?** 

Abre un issue con la información del problema y te ayudaremos.

---

**Última actualización**: 2025-01-XX

