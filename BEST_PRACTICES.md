# ✨ Mejores Prácticas - Documentos BLATAM

Guía de mejores prácticas para usar y contribuir a Documentos BLATAM de manera efectiva.

---

## 📋 Tabla de Contenidos

- [Uso de Templates](#uso-de-templates)
- [Personalización](#personalización)
- [Organización](#organización)
- [Contribución](#contribución)
- [Mantenimiento](#mantenimiento)
- [Seguridad](#seguridad)

---

## 📝 Uso de Templates

### ✅ Hacer

- **Lee primero** el template completo antes de usar
- **Personaliza** todas las variables `{{variable}}`
- **Valida** que los enlaces funcionen
- **Prueba** en un entorno de prueba antes de producción
- **Mantén** un backup del template original

### ❌ Evitar

- No uses templates sin personalizar
- No copies enlaces sin verificar
- No uses datos sensibles en templates
- No modifiques templates originales (usa copias)

### 💡 Ejemplo Correcto

```markdown
# Template original (NO modificar)
Hola {{nombre}}, tu webinar es el {{fecha}}.

# Tu versión personalizada (SÍ modificar)
Hola María, tu webinar es el 15 de enero a las 7 PM.
```

---

## 🎨 Personalización

### Variables Comunes

| Variable | Ejemplo | Cuándo Usar |
|----------|---------|-------------|
| `{{nombre}}` | María, Juan | Siempre personalizar |
| `{{fecha}}` | 15 de enero | Eventos, webinars |
| `{{hora}}` | 7:00 PM | Con timezone |
| `{{link}}` | URL completa | Con UTM |
| `{{empresa}}` | Nombre empresa | B2B outreach |
| `{{contexto}}` | Info relevante | Personalización avanzada |

### Niveles de Personalización

#### 🟢 Básico (5 minutos)
- Reemplazar `{{nombre}}`
- Agregar fecha/hora
- Insertar link

#### 🟡 Intermedio (15 minutos)
- Agregar contexto relevante
- Personalizar tono
- Ajustar CTA

#### 🔴 Avanzado (30+ minutos)
- Investigar perfil completo
- Crear mensaje único
- A/B testing de variantes

---

## 📁 Organización

### Estructura de Archivos

```
mi_proyecto/
├── templates/          # Templates originales (solo lectura)
├── personalizados/     # Tus versiones personalizadas
├── backups/           # Backups regulares
└── resultados/        # Resultados y métricas
```

### Convenciones de Nombres

```bash
# ✅ Bueno
dm_instagram_maria_2025-01-15.md
dashboard_ventas_q1_2025.csv
script_automation_v2.py

# ❌ Evitar
dm1.md
nuevo.md
test.md
```

### Versionado

```bash
# Usa versiones claras
template_v1.md
template_v2.md
template_v2.1.md  # Patch menor
```

---

## 🤝 Contribución

### Antes de Contribuir

1. **Lee** [`CONTRIBUTING.md`](CONTRIBUTING.md)
2. **Revisa** issues existentes
3. **Consulta** el roadmap
4. **Valida** tu contribución

### Tipos de Contribuciones

#### 📝 Documentación
- Corregir errores tipográficos
- Mejorar claridad
- Agregar ejemplos
- Traducir contenido

#### 🔧 Scripts
- Optimizar código existente
- Agregar funcionalidades
- Corregir bugs
- Mejorar documentación

#### 📊 Templates
- Crear nuevos templates
- Mejorar existentes
- Agregar variantes
- Documentar uso

### Proceso de Contribución

```bash
# 1. Fork o clona
git clone <repo>
cd documentos_blatam

# 2. Crea rama
git checkout -b feature/mi-mejora

# 3. Haz cambios
# ... edita archivos ...

# 4. Valida
python 06_documentation/Scripts/frontmatter_validator.py

# 5. Commit
git commit -m "docs: Agregar guía de X"

# 6. Push y PR
git push origin feature/mi-mejora
# Crear PR en GitHub
```

---

## 🔄 Mantenimiento

### Regular

- **Semanal**: Revisar enlaces rotos
- **Mensual**: Actualizar estadísticas
- **Trimestral**: Revisar roadmap
- **Anual**: Auditoría completa

### Herramientas de Mantenimiento

```bash
# Verificar enlaces
python 06_documentation/Scripts/find_broken_links.py

# Validar frontmatter
python 06_documentation/Scripts/frontmatter_validator.py

# Generar índices
python 06_documentation/Scripts/generate_index.py

# Analizar contenido
python 06_documentation/Scripts/analyze_content.py
```

### Backups

```bash
# Backup manual
cp -r documentos_blatam documentos_blatam_backup_$(date +%Y%m%d)

# O usar script
bash tools/auto_backup.sh
```

---

## 🔒 Seguridad

### Información Sensible

#### ❌ Nunca Incluir

- API keys
- Passwords
- Tokens de acceso
- Información personal de clientes
- Datos financieros reales

#### ✅ Usar en su Lugar

- Variables de entorno (`.env`)
- Placeholders (`{{api_key}}`)
- Ejemplos genéricos
- Datos de prueba

### Ejemplo Seguro

```bash
# ❌ MAL
API_KEY=sk_live_1234567890abcdef

# ✅ BIEN
API_KEY={{openai_api_key}}
# O en .env (no commitear)
```

### Archivos a Ignorar

```gitignore
# .gitignore
.env
*.key
*.secret
config.local.*
backups/
*.log
```

---

## 📊 Métricas y Tracking

### Qué Medir

- **Uso**: Qué templates/scripts se usan más
- **Éxito**: Tasa de conversión por template
- **Feedback**: Comentarios y sugerencias
- **Errores**: Bugs y problemas reportados

### Herramientas de Tracking

```bash
# Analizar uso
python 06_documentation/Scripts/analyze_content.py

# Generar reportes
bash tools/generate_full_report.sh

# Métricas de salud
node tools/health_score_calculator.js
```

---

## 🎯 Optimización

### Performance

- **Carga rápida**: Optimizar imágenes y assets
- **Búsqueda eficiente**: Usar índices
- **Caché**: Cachear resultados de scripts
- **Compresión**: Comprimir archivos grandes

### Calidad

- **Validación**: Validar antes de commit
- **Testing**: Probar en diferentes entornos
- **Documentación**: Documentar cambios
- **Revisión**: Code review antes de merge

---

## 📚 Recursos Adicionales

### Documentación

- [`README.md`](README.md) - Visión general
- [`ARCHITECTURE.md`](ARCHITECTURE.md) - Estructura
- [`CONTRIBUTING.md`](CONTRIBUTING.md) - Contribución
- [`SETUP.md`](SETUP.md) - Configuración

### Guías Específicas

- [`06_documentation/Best_practices/`](06_documentation/Best_practices/) - Más prácticas
- [`06_documentation/Templates/`](06_documentation/Templates/) - Templates
- [`06_documentation/Checklists/`](06_documentation/Checklists/) - Checklists

---

## ✅ Checklist de Mejores Prácticas

### Antes de Usar un Template

- [ ] He leído el template completo
- [ ] He identificado todas las variables
- [ ] He personalizado todas las variables
- [ ] He verificado los enlaces
- [ ] He probado en entorno de prueba

### Antes de Contribuir

- [ ] He leído CONTRIBUTING.md
- [ ] He seguido las convenciones
- [ ] He validado mi código/documentación
- [ ] He actualizado la documentación relacionada
- [ ] He creado un PR descriptivo

### Mantenimiento Regular

- [ ] He revisado enlaces rotos
- [ ] He actualizado estadísticas
- [ ] He hecho backup
- [ ] He validado frontmatter
- [ ] He actualizado índices

---

**Última actualización**: 2025-01-XX

