# 🔧 Documentación Técnica Avanzada

## 🏗️ Arquitectura del Sistema

### Diagrama de Arquitectura:

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  Email   │  │ Landing  │  │ Forms    │            │
│  │ Templates│  │  Pages   │  │          │            │
│  └──────────┘  └──────────┘  └──────────┘            │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    BACKEND                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  Email   │  │ Analytics│  │  ML/AI   │            │
│  │ Platform │  │  Engine  │  │  Engine  │            │
│  └──────────┘  └──────────┘  └──────────┘            │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    DATABASE                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │Contacts  │  │  Events  │  │ Analytics│            │
│  │  DB      │  │   DB     │  │    DB    │            │
│  └──────────┘  └──────────┘  └──────────┘            │
└─────────────────────────────────────────────────────────┘
```

---

## 🔌 APIs y Endpoints

### API de Email Marketing:

**Endpoint: Enviar Email**
```
POST /api/v1/emails/send
Headers:
  Authorization: Bearer {token}
  Content-Type: application/json

Body:
{
  "to": "prospecto@email.com",
  "template": "email_1_roi",
  "variables": {
    "nombre": "Juan Pérez",
    "industria": "Marketing",
    "link_calendly": "https://..."
  }
}

Response:
{
  "status": "success",
  "email_id": "email_123",
  "sent_at": "2024-01-15T10:00:00Z"
}
```

**Endpoint: Trackear Evento**
```
POST /api/v1/events/track
Body:
{
  "email_id": "email_123",
  "event_type": "opened|clicked|converted",
  "timestamp": "2024-01-15T10:05:00Z"
}
```

---

## 🗄️ Esquema de Base de Datos

### Tabla: contacts

```sql
CREATE TABLE contacts (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    industry VARCHAR(50),
    role VARCHAR(50),
    company VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    email_followup_status VARCHAR(50),
    email_1_sent BOOLEAN DEFAULT FALSE,
    email_1_opened BOOLEAN DEFAULT FALSE,
    email_1_clicked BOOLEAN DEFAULT FALSE,
    email_2_sent BOOLEAN DEFAULT FALSE,
    email_2_opened BOOLEAN DEFAULT FALSE,
    email_2_clicked BOOLEAN DEFAULT FALSE,
    email_3_sent BOOLEAN DEFAULT FALSE,
    email_3_opened BOOLEAN DEFAULT FALSE,
    email_3_clicked BOOLEAN DEFAULT FALSE,
    converted BOOLEAN DEFAULT FALSE,
    converted_at TIMESTAMP,
    score INTEGER DEFAULT 0
);
```

### Tabla: emails

```sql
CREATE TABLE emails (
    id UUID PRIMARY KEY,
    contact_id UUID REFERENCES contacts(id),
    template VARCHAR(50),
    subject VARCHAR(255),
    sent_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    converted_at TIMESTAMP,
    status VARCHAR(50)
);
```

### Tabla: events

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY,
    email_id UUID REFERENCES emails(id),
    event_type VARCHAR(50),
    event_data JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

---

## 🔐 Seguridad

### Autenticación:

**JWT Tokens:**
```python
import jwt
from datetime import datetime, timedelta

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
```

### Encriptación:

**Datos Sensibles:**
```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

encrypted_email = cipher.encrypt(email.encode())
decrypted_email = cipher.decrypt(encrypted_email).decode()
```

---

## 📊 Logging y Monitoreo

### Sistema de Logs:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Uso
logger.info(f"Email sent: {email_id}")
logger.error(f"Error sending email: {error}")
```

---

## 🚀 Deployment

### Docker Compose:

```yaml
version: '3.8'

services:
  email-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/emaildb
    depends_on:
      - db
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=emaildb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## ✅ Checklist Técnico

### Pre-Deployment:
- [ ] Tests unitarios pasando
- [ ] Tests de integración pasando
- [ ] Security audit completo
- [ ] Performance testing
- [ ] Documentation actualizada

### Deployment:
- [ ] Backup de datos
- [ ] Deploy a staging
- [ ] Tests en staging
- [ ] Deploy a production
- [ ] Monitoreo activo

### Post-Deployment:
- [ ] Verificar métricas
- [ ] Monitorear logs
- [ ] Verificar funcionalidad
- [ ] Documentar issues

---

**Documentación técnica completa para desarrolladores.** 🔧

