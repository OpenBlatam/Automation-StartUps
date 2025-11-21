# 🔒 Seguridad - Documentos BLATAM

Guía de mejores prácticas de seguridad para usar y contribuir a Documentos BLATAM.

---

## 📋 Tabla de Contenidos

- [Información Sensible](#información-sensible)
- [API Keys y Credenciales](#api-keys-y-credenciales)
- [Variables de Entorno](#variables-de-entorno)
- [Git y Versionado](#git-y-versionado)
- [Scripts y Código](#scripts-y-código)
- [Comunicación](#comunicación)

---

## 🔐 Información Sensible

### ❌ Nunca Incluir

- **API Keys** completas
- **Passwords** o contraseñas
- **Tokens de acceso** (OAuth, JWT, etc.)
- **Claves privadas** (SSH, GPG, etc.)
- **Información personal** de clientes
- **Datos financieros** reales
- **Números de tarjeta** o información bancaria
- **Secretos de aplicación**

### ✅ Usar en su Lugar

- **Variables de entorno** (`.env`)
- **Placeholders** (`{{api_key}}`)
- **Ejemplos genéricos**
- **Datos de prueba** (test data)
- **Configuración local** (no commitear)

---

## 🔑 API Keys y Credenciales

### Manejo Seguro

**❌ Incorrecto**:
```python
# NUNCA hacer esto
API_KEY = "sk_live_1234567890abcdef"
```

**✅ Correcto**:
```python
# Usar variables de entorno
import os
API_KEY = os.getenv("API_KEY")
```

### Configuración

**Archivo `.env`** (no commitear):
```bash
# .env
OPENAI_API_KEY=sk-tu-key-aqui
GOOGLE_API_KEY=tu-google-key
DATABASE_URL=postgresql://user:pass@localhost/db
```

**`.gitignore`**:
```gitignore
# Variables de entorno
.env
.env.local
.env.*.local

# Credenciales
*.key
*.pem
*.secret
config.local.*
secrets/
```

---

## 🌍 Variables de Entorno

### Configuración Local

**Crear `.env` desde template**:
```bash
# Copiar template
cp env.example .env

# Editar con tus credenciales
nano .env
```

**Template `env.example`**:
```bash
# API Keys
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Secrets
SECRET_KEY=your_secret_key_here
```

### Uso en Código

**Python**:
```python
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY no configurada")
```

**Node.js**:
```javascript
require('dotenv').config();

const apiKey = process.env.OPENAI_API_KEY;
if (!apiKey) {
    throw new Error('OPENAI_API_KEY no configurada');
}
```

**Bash**:
```bash
# Cargar variables
source .env

# Usar
echo $API_KEY
```

---

## 📦 Git y Versionado

### .gitignore Completo

```gitignore
# Variables de entorno
.env
.env.local
.env.*.local

# Credenciales y secretos
*.key
*.pem
*.secret
*.token
secrets/
credentials/

# Archivos de configuración local
config.local.*
settings.local.*

# Logs con información sensible
*.log
logs/

# Backups con datos sensibles
backups/
*.backup

# Archivos temporales
*.tmp
*.temp
__pycache__/
node_modules/

# IDEs
.vscode/
.idea/
*.swp
*.swo
```

### Verificar Antes de Commit

```bash
# Ver qué se va a commitear
git status

# Ver diferencias
git diff

# Buscar posibles secretos
git diff | grep -i "api_key\|password\|secret\|token"

# Si encuentras algo, NO hacer commit
```

### Si Accidentalmente Commiteaste Secretos

**Acción Inmediata**:

1. **Rotar credenciales** (más importante)
   - Cambiar todas las API keys
   - Revocar tokens
   - Actualizar passwords

2. **Remover del historial**:
```bash
# Usar git filter-branch o BFG Repo-Cleaner
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch archivo_con_secretos" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (cuidado!)
git push origin --force --all
```

3. **Notificar al equipo**

---

## 💻 Scripts y Código

### Validación de Entrada

**Sanitizar Inputs**:
```python
import re

def sanitize_input(user_input):
    # Remover caracteres peligrosos
    sanitized = re.sub(r'[<>"\']', '', user_input)
    return sanitized.strip()
```

### Validación de Permisos

**Verificar antes de ejecutar**:
```python
import os

def check_permissions():
    # Verificar que el usuario tiene permisos
    if os.geteuid() != 0:
        print("No se requieren permisos de root")
    else:
        print("Advertencia: Ejecutando como root")
```

### Manejo de Errores Seguro

**No exponer información sensible**:
```python
# ❌ Incorrecto
try:
    connect_to_api()
except Exception as e:
    print(f"Error: {e}")  # Puede exponer información sensible

# ✅ Correcto
try:
    connect_to_api()
except Exception as e:
    logger.error("Error al conectar con API")
    # No exponer detalles internos
```

---

## 📧 Comunicación

### Compartir Credenciales

**❌ Nunca**:
- Por email sin encriptar
- En mensajes de Slack/Teams públicos
- En documentos compartidos
- En código commitado

**✅ Seguro**:
- Usar gestores de secretos (1Password, LastPass)
- Encriptar antes de enviar
- Usar canales privados y seguros
- Rotar después de compartir

### Reportar Vulnerabilidades

**Proceso**:
1. **NO** abrir issue público
2. Contactar directamente al mantenedor
3. Proporcionar detalles del problema
4. Esperar confirmación antes de disclosure

**Template de Reporte**:
```markdown
## Vulnerabilidad de Seguridad

**Tipo**: [ej. Exposición de credenciales, XSS, etc.]
**Severidad**: [Alta/Media/Baja]
**Descripción**: [Descripción clara]
**Pasos para reproducir**: [Si aplica]
**Impacto potencial**: [Qué puede pasar]
```

---

## 🔍 Auditoría de Seguridad

### Checklist Regular

**Mensual**:
- [ ] Revisar variables de entorno
- [ ] Verificar .gitignore
- [ ] Rotar credenciales antiguas
- [ ] Revisar permisos de archivos
- [ ] Auditar logs de acceso

**Trimestral**:
- [ ] Revisar dependencias por vulnerabilidades
- [ ] Actualizar librerías
- [ ] Revisar configuración de APIs
- [ ] Auditar acceso a recursos

### Herramientas de Auditoría

```bash
# Verificar secretos en código
grep -r "api_key\|password\|secret" . --exclude-dir=node_modules

# Verificar permisos de archivos
find . -type f -perm /o+w  # Archivos writables por otros

# Verificar dependencias (Python)
pip-audit

# Verificar dependencias (Node.js)
npm audit
```

---

## 🛡️ Mejores Prácticas

### General

1. **Principio de Menor Privilegio**
   - Usar solo los permisos necesarios
   - No usar root/admin innecesariamente

2. **Defensa en Profundidad**
   - Múltiples capas de seguridad
   - Validación en cada nivel

3. **Actualización Regular**
   - Mantener dependencias actualizadas
   - Aplicar parches de seguridad

4. **Monitoreo**
   - Logs de acceso
   - Alertas de actividad sospechosa
   - Revisión regular

### Específicas

**Para Desarrolladores**:
- Nunca commitear credenciales
- Usar variables de entorno
- Validar inputs
- Manejar errores apropiadamente

**Para Usuarios**:
- No compartir credenciales
- Usar passwords fuertes
- Rotar credenciales regularmente
- Reportar problemas de seguridad

---

## 📚 Recursos Adicionales

- [`BEST_PRACTICES.md`](BEST_PRACTICES.md) - Mejores prácticas generales
- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) - Solución de problemas
- [`INTEGRATIONS.md`](INTEGRATIONS.md) - Integraciones seguras

---

## 🆘 Si Encuentras un Problema de Seguridad

1. **NO** abrir issue público
2. Contactar directamente: [email o método seguro]
3. Proporcionar detalles del problema
4. Esperar respuesta antes de disclosure público

---

**Última actualización**: 2025-01-XX

