# 🔧 Troubleshooting - SaaS de IA para Marketing

## 🚨 Problemas Comunes y Soluciones

### 🔐 Problemas de Autenticación

#### Error: "Invalid JWT Token"
**Síntomas:**
- Error 401 al hacer requests
- Mensaje "Invalid JWT Token"
- Usuario no puede acceder a la plataforma

**Soluciones:**
```bash
# 1. Verificar token en localStorage
localStorage.getItem('accessToken')

# 2. Limpiar storage y re-login
localStorage.clear()
sessionStorage.clear()

# 3. Verificar configuración del servidor
# En .env
JWT_SECRET=tu_secret_super_seguro
JWT_REFRESH_SECRET=tu_refresh_secret_super_seguro

# 4. Regenerar token
POST /auth/refresh
{
  "refreshToken": "tu_refresh_token"
}
```

#### Error: "Token Expired"
**Síntomas:**
- Error 401 con mensaje "Token Expired"
- Usuario es redirigido al login

**Soluciones:**
```javascript
// Implementar refresh automático
const refreshToken = async () => {
  try {
    const response = await fetch('/api/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refreshToken: getRefreshToken() })
    });
    
    if (response.ok) {
      const data = await response.json();
      setAccessToken(data.accessToken);
    } else {
      redirectToLogin();
    }
  } catch (error) {
    redirectToLogin();
  }
};
```

### 🤖 Problemas con APIs de IA

#### Error: "OpenAI API Key Invalid"
**Síntomas:**
- Error al generar contenido
- Mensaje "Invalid API Key"
- Contenido no se genera

**Soluciones:**
```bash
# 1. Verificar API key en .env
OPENAI_API_KEY=sk-proj-...

# 2. Verificar formato de la key
# Debe empezar con sk-proj- o sk-

# 3. Verificar límites de uso
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/usage

# 4. Regenerar API key en OpenAI Dashboard
```

#### Error: "Rate Limit Exceeded"
**Síntomas:**
- Error 429 en requests
- Mensaje "Rate limit exceeded"
- Contenido no se genera

**Soluciones:**
```javascript
// Implementar retry con backoff
const retryWithBackoff = async (fn, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (error.status === 429 && i < maxRetries - 1) {
        const delay = Math.pow(2, i) * 1000; // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, delay));
      } else {
        throw error;
      }
    }
  }
};
```

#### Error: "Insufficient Credits"
**Síntomas:**
- Error al generar contenido
- Mensaje "Insufficient credits"
- Usuario no puede usar la plataforma

**Soluciones:**
```bash
# 1. Verificar créditos del usuario
GET /api/users/credits

# 2. Actualizar plan de suscripción
POST /api/users/subscription/upgrade

# 3. Comprar créditos adicionales
POST /api/users/credits/purchase
{
  "amount": 100,
  "paymentMethod": "card_1234567890"
}
```

### 🗄️ Problemas de Base de Datos

#### Error: "Connection Refused"
**Síntomas:**
- Error al conectar a PostgreSQL
- Aplicación no inicia
- Mensaje "Connection refused"

**Soluciones:**
```bash
# 1. Verificar que PostgreSQL esté corriendo
sudo systemctl status postgresql

# 2. Iniciar PostgreSQL
sudo systemctl start postgresql

# 3. Verificar configuración de conexión
# En .env
DATABASE_URL=postgresql://usuario:password@localhost:5432/ia_marketing

# 4. Verificar que la base de datos existe
psql -h localhost -U usuario -d ia_marketing

# 5. Crear base de datos si no existe
createdb ia_marketing
```

#### Error: "Table doesn't exist"
**Síntomas:**
- Error al hacer queries
- Mensaje "relation does not exist"
- Funcionalidades no funcionan

**Soluciones:**
```bash
# 1. Ejecutar migraciones
npm run migrate

# 2. Verificar estado de migraciones
npm run migrate:status

# 3. Revertir y re-ejecutar migraciones
npm run migrate:rollback
npm run migrate

# 4. Verificar esquema de la base de datos
psql -h localhost -U usuario -d ia_marketing -c "\dt"
```

#### Error: "Deadlock detected"
**Síntomas:**
- Error en operaciones de base de datos
- Mensaje "deadlock detected"
- Transacciones fallan

**Soluciones:**
```javascript
// Implementar retry para deadlocks
const retryOnDeadlock = async (fn, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (error.code === '40P01' && i < maxRetries - 1) {
        const delay = Math.random() * 1000; // Random delay
        await new Promise(resolve => setTimeout(resolve, delay));
      } else {
        throw error;
      }
    }
  }
};
```

### 🚀 Problemas de Performance

#### Lento: "Slow API Response"
**Síntomas:**
- APIs responden lentamente
- Timeouts en requests
- Usuarios reportan lentitud

**Soluciones:**
```javascript
// 1. Implementar caching
const redis = require('redis');
const client = redis.createClient();

const getCachedData = async (key) => {
  const cached = await client.get(key);
  return cached ? JSON.parse(cached) : null;
};

const setCachedData = async (key, data, ttl = 3600) => {
  await client.setex(key, ttl, JSON.stringify(data));
};

// 2. Optimizar queries de base de datos
// Usar índices apropiados
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_projects_user_id ON copywriting_projects(user_id);

// 3. Implementar paginación
const getProjects = async (page = 1, limit = 20) => {
  const offset = (page - 1) * limit;
  return await db.project.findMany({
    skip: offset,
    take: limit,
    orderBy: { createdAt: 'desc' }
  });
};
```

#### Lento: "Slow AI Generation"
**Síntomas:**
- Generación de contenido lenta
- Timeouts en IA
- Usuarios esperan mucho tiempo

**Soluciones:**
```javascript
// 1. Implementar streaming para respuestas largas
const streamResponse = async (prompt) => {
  const stream = await openai.chat.completions.create({
    model: 'gpt-4',
    messages: [{ role: 'user', content: prompt }],
    stream: true
  });

  for await (const chunk of stream) {
    const content = chunk.choices[0]?.delta?.content;
    if (content) {
      // Enviar chunk al cliente
      res.write(content);
    }
  }
  res.end();
};

// 2. Usar modelos más rápidos para tareas simples
const selectModel = (taskType) => {
  switch (taskType) {
    case 'simple_copy':
      return 'gpt-3.5-turbo';
    case 'complex_analysis':
      return 'gpt-4';
    default:
      return 'gpt-3.5-turbo';
  }
};

// 3. Implementar queue para tareas pesadas
const Queue = require('bull');
const aiQueue = new Queue('AI processing');

aiQueue.process(async (job) => {
  const { prompt, options } = job.data;
  return await generateContent(prompt, options);
});
```

### 💾 Problemas de Almacenamiento

#### Error: "Disk Space Full"
**Síntomas:**
- Error al guardar archivos
- Aplicación no responde
- Logs muestran "No space left"

**Soluciones:**
```bash
# 1. Verificar espacio en disco
df -h

# 2. Limpiar logs antiguos
find /var/log -name "*.log" -mtime +30 -delete

# 3. Limpiar archivos temporales
rm -rf /tmp/*

# 4. Limpiar Docker
docker system prune -a

# 5. Configurar rotación de logs
# En /etc/logrotate.d/ia-marketing
/var/log/ia-marketing/*.log {
  daily
  rotate 7
  compress
  delaycompress
  missingok
  notifempty
}
```

#### Error: "File Upload Failed"
**Síntomas:**
- Error al subir archivos
- Mensaje "Upload failed"
- Archivos no se guardan

**Soluciones:**
```javascript
// 1. Verificar límites de tamaño
const multer = require('multer');
const upload = multer({
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Tipo de archivo no permitido'));
    }
  }
});

// 2. Implementar validación de archivos
const validateFile = (file) => {
  if (!file) {
    throw new Error('No se proporcionó archivo');
  }
  
  if (file.size > 10 * 1024 * 1024) {
    throw new Error('Archivo demasiado grande');
  }
  
  const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
  if (!allowedTypes.includes(file.mimetype)) {
    throw new Error('Tipo de archivo no permitido');
  }
};
```

### 🌐 Problemas de Red

#### Error: "Network Timeout"
**Síntomas:**
- Requests fallan por timeout
- Conexiones se cierran
- APIs no responden

**Soluciones:**
```javascript
// 1. Configurar timeouts apropiados
const axios = require('axios');

const api = axios.create({
  timeout: 30000, // 30 segundos
  retry: 3,
  retryDelay: (retryCount) => {
    return retryCount * 1000; // 1s, 2s, 3s
  }
});

// 2. Implementar circuit breaker
const CircuitBreaker = require('opossum');

const options = {
  timeout: 3000,
  errorThresholdPercentage: 50,
  resetTimeout: 30000
};

const breaker = new CircuitBreaker(aiService.generateContent, options);

// 3. Configurar keep-alive
const http = require('http');
const agent = new http.Agent({
  keepAlive: true,
  keepAliveMsecs: 30000,
  maxSockets: 10
});
```

#### Error: "DNS Resolution Failed"
**Síntomas:**
- Error al conectar a APIs externas
- Mensaje "DNS resolution failed"
- Servicios externos no disponibles

**Soluciones:**
```bash
# 1. Verificar DNS
nslookup api.openai.com

# 2. Configurar DNS alternativo
# En /etc/resolv.conf
nameserver 8.8.8.8
nameserver 8.8.4.4

# 3. Verificar conectividad
ping api.openai.com

# 4. Configurar fallback DNS
const dns = require('dns');
dns.setServers(['8.8.8.8', '8.8.4.4']);
```

### 🔍 Problemas de Logging

#### Error: "Log Files Too Large"
**Síntomas:**
- Archivos de log muy grandes
- Aplicación lenta
- Disco lleno

**Soluciones:**
```javascript
// 1. Configurar rotación de logs
const winston = require('winston');
const DailyRotateFile = require('winston-daily-rotate-file');

const logger = winston.createLogger({
  transports: [
    new DailyRotateFile({
      filename: 'logs/application-%DATE%.log',
      datePattern: 'YYYY-MM-DD',
      maxSize: '20m',
      maxFiles: '14d',
      zippedArchive: true
    })
  ]
});

// 2. Configurar niveles de log
const logLevel = process.env.NODE_ENV === 'production' ? 'info' : 'debug';

// 3. Implementar log aggregation
const { createLogger, format, transports } = require('winston');
const { combine, timestamp, json } = format;

const logger = createLogger({
  level: 'info',
  format: combine(
    timestamp(),
    json()
  ),
  transports: [
    new transports.Console(),
    new transports.File({ filename: 'error.log', level: 'error' }),
    new transports.File({ filename: 'combined.log' })
  ]
});
```

## 🛠️ Herramientas de Diagnóstico

### Comandos Útiles
```bash
# Verificar estado de la aplicación
kubectl get pods -n ia-marketing
kubectl logs -f deployment/ia-marketing-app

# Verificar recursos del sistema
kubectl top pods -n ia-marketing
kubectl describe pod <pod-name> -n ia-marketing

# Verificar conectividad de base de datos
kubectl exec -it <pod-name> -n ia-marketing -- psql -h db -U user -d ia_marketing

# Verificar logs de la aplicación
kubectl logs -f deployment/ia-marketing-app -n ia-marketing --tail=100

# Reiniciar deployment
kubectl rollout restart deployment/ia-marketing-app -n ia-marketing
```

### Scripts de Diagnóstico
```bash
#!/bin/bash
# diagnostic.sh

echo "🔍 Diagnóstico del Sistema IA Marketing"
echo "========================================"

# Verificar estado de pods
echo "📦 Estado de Pods:"
kubectl get pods -n ia-marketing

# Verificar recursos
echo "💾 Recursos del Sistema:"
kubectl top pods -n ia-marketing

# Verificar logs de errores
echo "🚨 Errores Recientes:"
kubectl logs deployment/ia-marketing-app -n ia-marketing --tail=50 | grep -i error

# Verificar conectividad de base de datos
echo "🗄️ Conectividad de Base de Datos:"
kubectl exec -it deployment/ia-marketing-app -n ia-marketing -- \
  psql -h db -U user -d ia_marketing -c "SELECT 1;"

# Verificar APIs externas
echo "🌐 Conectividad de APIs:"
kubectl exec -it deployment/ia-marketing-app -n ia-marketing -- \
  curl -s -o /dev/null -w "%{http_code}" https://api.openai.com/v1/models

echo "✅ Diagnóstico completado"
```

## 📞 Escalación de Problemas

### Niveles de Severidad

#### P0 - Crítico
- Aplicación completamente inaccesible
- Pérdida de datos
- Seguridad comprometida

**Acción:** Contactar inmediatamente al equipo de DevOps
**Tiempo de respuesta:** <15 minutos

#### P1 - Alto
- Funcionalidad principal no funciona
- Performance severamente degradada
- Múltiples usuarios afectados

**Acción:** Contactar al equipo de desarrollo
**Tiempo de respuesta:** <1 hora

#### P2 - Medio
- Funcionalidad secundaria no funciona
- Performance ligeramente degradada
- Pocos usuarios afectados

**Acción:** Crear ticket de soporte
**Tiempo de respuesta:** <4 horas

#### P3 - Bajo
- Problema cosmético
- Mejora de funcionalidad
- No afecta usuarios

**Acción:** Crear issue en GitHub
**Tiempo de respuesta:** <24 horas

### Contactos de Emergencia
- **DevOps**: devops@ia-marketing.com
- **Desarrollo**: dev@ia-marketing.com
- **Soporte**: soporte@ia-marketing.com
- **Emergencias**: +1 (555) 911-HELP

---

## 🎯 Prevención de Problemas

### Monitoreo Proactivo
- Configurar alertas para métricas clave
- Monitorear logs en tiempo real
- Implementar health checks
- Configurar backups automáticos

### Pruebas Regulares
- Tests de carga semanales
- Tests de integración diarios
- Tests de seguridad mensuales
- Disaster recovery trimestral

### Documentación
- Mantener runbooks actualizados
- Documentar procedimientos de recuperación
- Crear guías de troubleshooting
- Capacitar al equipo regularmente

---

*"Un sistema robusto es aquel que se recupera rápidamente de los problemas y aprende de ellos."* 🔧✨

