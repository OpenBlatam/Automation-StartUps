# Comparación de Workflows n8n

## 📋 Workflows Disponibles

### 1. Workflow Original (Comandos Directos)
**Archivo**: `n8n_workflow_tiktok_auto_edit.json`

**Características:**
- ✅ Ejecuta scripts Python directamente
- ✅ Control total del proceso
- ✅ No requiere API REST
- ✅ Más rápido (sin overhead HTTP)

**Uso:**
- Ideal para instalaciones locales
- Cuando no necesitas API REST
- Procesamiento directo

### 2. Workflow con API REST
**Archivo**: `n8n_workflow_tiktok_auto_edit_api.json`

**Características:**
- ✅ Usa API REST
- ✅ Más escalable
- ✅ Mejor para múltiples instancias
- ✅ Separación de concerns

**Uso:**
- Ideal para producción
- Múltiples instancias de n8n
- Cuando API REST ya está corriendo

## 🔄 Diferencias Principales

| Aspecto | Workflow Original | Workflow API |
|---------|------------------|--------------|
| **Ejecución** | Comandos directos | HTTP requests |
| **Requisitos** | Scripts locales | API REST corriendo |
| **Escalabilidad** | Media | Alta |
| **Velocidad** | Más rápido | Ligeramente más lento |
| **Mantenimiento** | Más simple | Más complejo |
| **Ideal para** | Desarrollo/Local | Producción |

## 🚀 Cuándo Usar Cada Uno

### Usa Workflow Original si:
- ✅ Instalación local
- ✅ n8n y scripts en mismo servidor
- ✅ No necesitas escalar
- ✅ Quieres simplicidad

### Usa Workflow API si:
- ✅ Producción
- ✅ Múltiples instancias
- ✅ API REST ya disponible
- ✅ Necesitas escalabilidad

## 📝 Configuración

### Workflow Original

1. Importa `n8n_workflow_tiktok_auto_edit.json`
2. Ajusta rutas de scripts si es necesario
3. Configura credenciales de Telegram
4. Listo para usar

### Workflow API

1. Inicia API REST: `python3 tiktok_api_server.py -p 5000`
2. Importa `n8n_workflow_tiktok_auto_edit_api.json`
3. Configura `TIKTOK_API_URL` en n8n
4. Configura credenciales
5. Listo para usar

## 🔧 Migración

### De Original a API

1. Inicia API REST
2. Verifica que funciona: `curl http://localhost:5000/health`
3. Importa workflow API
4. Configura URL de API
5. Prueba con un video

### De API a Original

1. Importa workflow original
2. Ajusta rutas de scripts
3. Prueba con un video

---

**Recomendación**: Usa workflow API para producción, workflow original para desarrollo.

