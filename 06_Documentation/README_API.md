# 🚀 API REST - Sistema de Organización de Documentos

## 📋 Descripción

API REST completa para el Sistema de Organización de Documentos Enterprise, que proporciona endpoints para gestión de documentos, búsqueda avanzada con IA, colaboración en tiempo real, analytics y respaldos automáticos.

## 🛠️ Características Principales

### 🔐 Autenticación y Seguridad
- **Registro de usuarios** con validación
- **Autenticación JWT** con tokens seguros
- **Roles de usuario** (admin, user, viewer)
- **Protección de endpoints** con decoradores

### 📁 Gestión de Documentos
- **Subida de archivos** con validación
- **Descarga segura** de documentos
- **Listado con filtros** avanzados
- **Metadatos** automáticos

### 🔍 Búsqueda Avanzada con IA
- **Búsqueda semántica** inteligente
- **Sugerencias automáticas** de términos
- **Filtros por categoría** y tipo
- **Resultados ordenados** por relevancia

### 📊 Analytics y Métricas
- **Métricas de uso** en tiempo real
- **Archivos más accedidos**
- **Búsquedas populares**
- **Tendencias de uso**
- **Recomendaciones** del sistema

### 💾 Sistema de Respaldos
- **Respaldos automáticos** programados
- **Respaldos manuales** bajo demanda
- **Restauración** de respaldos
- **Verificación de integridad**

### 🤝 Colaboración en Tiempo Real
- **WebSockets** para comunicación en vivo
- **Salas de colaboración** por documento
- **Notificaciones** de edición
- **Indicadores** de escritura

## 🚀 Instalación y Configuración

### 1. Instalar Dependencias

```bash
cd api
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
export SECRET_KEY=tu_clave_secreta_aqui
```

### 3. Iniciar el Servidor

```bash
python start_server.py
```

O directamente:

```bash
python app.py
```

## 📡 Endpoints de la API

### 🔐 Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/register` | Registro de nuevos usuarios |
| POST | `/api/auth/login` | Inicio de sesión |

### 📁 Documentos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/documents` | Listar documentos con filtros |
| POST | `/api/documents/upload` | Subir nuevo documento |
| GET | `/api/documents/<path>` | Descargar documento |

### 🔍 Búsqueda

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/search` | Búsqueda avanzada con IA |
| GET | `/api/search/suggestions` | Obtener sugerencias |

### 📊 Analytics

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/analytics/overview` | Resumen de métricas |
| GET | `/api/analytics/recommendations` | Recomendaciones del sistema |

### 💾 Respaldos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/backups` | Listar respaldos |
| POST | `/api/backups/create` | Crear respaldo manual |
| POST | `/api/backups/<name>/restore` | Restaurar respaldo |

### ⚙️ Sistema

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/system/status` | Estado del sistema |
| POST | `/api/system/maintenance` | Ejecutar mantenimiento |

### 🔧 Configuración

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/config` | Obtener configuración |
| PUT | `/api/config/<name>` | Actualizar configuración |

## 🔌 WebSockets para Colaboración

### Eventos Disponibles

- `join_room` - Unirse a sala de colaboración
- `leave_room` - Salir de sala
- `document_edit` - Notificar edición de documento
- `user_typing` - Indicar que usuario está escribiendo

### Ejemplo de Uso (JavaScript)

```javascript
const socket = io('http://localhost:5000');

// Unirse a sala
socket.emit('join_room', { room: 'documento_123' });

// Escuchar actualizaciones
socket.on('document_updated', (data) => {
    console.log('Documento actualizado:', data);
});

// Notificar edición
socket.emit('document_edit', {
    room: 'documento_123',
    document: 'archivo.md',
    changes: { line: 10, text: 'nuevo contenido' }
});
```

## 📝 Ejemplos de Uso

### 1. Registro de Usuario

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario_test",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 2. Inicio de Sesión

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario_test",
    "password": "password123"
  }'
```

### 3. Búsqueda de Documentos

```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer tu_token_aqui" \
  -d '{
    "query": "marketing digital",
    "limit": 10
  }'
```

### 4. Subir Documento

```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -H "Authorization: Bearer tu_token_aqui" \
  -F "file=@documento.pdf" \
  -F "category=marketing"
```

## 🔒 Seguridad

### Autenticación JWT

Todos los endpoints protegidos requieren un token JWT válido en el header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Validación de Archivos

- **Tamaño máximo**: 100MB por archivo
- **Tipos permitidos**: Configurables en el sistema
- **Nombres seguros**: Sanitización automática

### Rate Limiting

- **Búsquedas**: 100 por minuto por usuario
- **Subidas**: 10 por minuto por usuario
- **API calls**: 1000 por hora por usuario

## 📊 Monitoreo y Logs

### Logs del Sistema

Los logs se guardan en:
- `logs/api.log` - Logs generales de la API
- `logs/errors.log` - Logs de errores
- `logs/access.log` - Logs de acceso

### Métricas Disponibles

- **Requests por segundo**
- **Tiempo de respuesta promedio**
- **Errores por endpoint**
- **Usuarios activos**
- **Uso de memoria y CPU**

## 🚀 Despliegue en Producción

### 1. Configurar Variables de Entorno

```bash
export FLASK_ENV=production
export SECRET_KEY=clave_super_secreta_produccion
export DATABASE_URL=sqlite:///prod.db
```

### 2. Usar Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 3. Configurar Nginx (Opcional)

```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🛠️ Desarrollo

### Estructura del Proyecto

```
api/
├── app.py                 # Aplicación principal
├── start_server.py        # Script de inicio
├── requirements.txt       # Dependencias
├── README_API.md         # Documentación
└── logs/                 # Directorio de logs
```

### Agregar Nuevos Endpoints

1. **Definir la ruta** en `app.py`
2. **Agregar autenticación** si es necesario
3. **Implementar lógica** de negocio
4. **Agregar documentación** en este README
5. **Escribir tests** unitarios

### Testing

```bash
# Ejecutar tests
python -m pytest tests/

# Tests con cobertura
python -m pytest --cov=app tests/
```

## 📞 Soporte

Para soporte técnico o reportar bugs:

1. **Revisar logs** en el directorio `logs/`
2. **Verificar configuración** en `config.json`
3. **Consultar documentación** de endpoints
4. **Contactar administrador** del sistema

## 🔄 Actualizaciones

### Versión 1.0
- ✅ API REST completa
- ✅ Autenticación JWT
- ✅ Búsqueda con IA
- ✅ Analytics en tiempo real
- ✅ Sistema de respaldos
- ✅ Colaboración WebSocket
- ✅ Documentación completa

### Próximas Versiones
- 🔄 Cache Redis para mejor rendimiento
- 🔄 Integración con servicios en la nube
- 🔄 API GraphQL adicional
- 🔄 Aplicación móvil nativa
- 🔄 Machine Learning avanzado

---

**Sistema de Organización de Documentos Enterprise**  
*Desarrollado con ❤️ para máxima eficiencia y productividad*


