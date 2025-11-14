# 📬 Optimización de Deliverability

## 🎯 Factores de Deliverability

### 1. Autenticación de Email

**SPF (Sender Policy Framework):**
```
TXT record en DNS:
v=spf1 include:_spf.google.com ~all
```

**DKIM (DomainKeys Identified Mail):**
```
TXT record en DNS:
v=DKIM1; k=rsa; p={public_key}
```

**DMARC (Domain-based Message Authentication):**
```
TXT record en DNS:
v=DMARC1; p=quarantine; rua=mailto:dmarc@tudominio.com
```

---

### 2. Reputación del Dominio

**Factores:**
```
- Historial de envíos
- Tasa de bounces
- Tasa de spam complaints
- Engagement rate
- Lista negra status
```

**Mejores Prácticas:**
```
✅ Enviar desde dominio propio
✅ Warm-up gradual del dominio
✅ Lista limpia (sin emails inválidos)
✅ Monitorear reputación
✅ Responder a bounces rápidamente
```

---

### 3. Contenido del Email

**Factores que Afectan:**
```
❌ Palabras spam (FREE, CLICK HERE, etc.)
❌ Demasiados enlaces
❌ Imágenes grandes sin texto
❌ HTML mal formado
❌ Enlaces acortados sospechosos
```

**Mejores Prácticas:**
```
✅ Texto balanceado con imágenes
✅ Enlaces naturales (no acortados)
✅ HTML limpio y validado
✅ Palabras naturales, no spam
✅ Ratio texto/imagen: 60/40
```

---

### 4. Lista de Envío

**Hygiene de Lista:**
```
✅ Verificar emails antes de agregar
✅ Remover bounces inmediatamente
✅ Procesar unsubscribes rápidamente
✅ Limpiar lista regularmente
✅ Segmentar por engagement
```

**Herramientas:**
```
- Email verification: ZeroBounce, NeverBounce
- List cleaning: Mailchimp, ConvertKit
- Bounce handling: Automatizado
```

---

## 🔧 Configuración Técnica

### 1. SPF Record

**Configuración:**
```
Tipo: TXT
Host: @
Valor: v=spf1 include:_spf.google.com ~all
```

**Verificación:**
```
nslookup -type=TXT tudominio.com
```

---

### 2. DKIM Record

**Configuración:**
```
1. Generar par de claves (en plataforma de email)
2. Agregar TXT record en DNS:
   Host: {selector}._domainkey
   Valor: {public_key}
```

**Verificación:**
```
nslookup -type=TXT {selector}._domainkey.tudominio.com
```

---

### 3. DMARC Record

**Configuración:**
```
Tipo: TXT
Host: _dmarc
Valor: v=DMARC1; p=quarantine; rua=mailto:dmarc@tudominio.com
```

**Políticas:**
```
- none: Solo monitorear
- quarantine: Poner en spam
- reject: Rechazar completamente
```

---

## 📊 Monitoreo de Deliverability

### Métricas Clave:

**1. Bounce Rate:**
```
Objetivo: <2%
Hard Bounces: Eliminar inmediatamente
Soft Bounces: Reintentar 3 veces
```

**2. Spam Complaint Rate:**
```
Objetivo: <0.1%
Si >0.1%: Revisar contenido y lista
```

**3. Open Rate:**
```
Objetivo: 40-50%
Si <30%: Revisar subject line y timing
```

**4. Reputación del Dominio:**
```
Herramientas:
- Sender Score (Return Path)
- Google Postmaster Tools
- Microsoft SNDS
```

---

## 🚀 Warm-up del Dominio

### Proceso de 30 Días:

**Semana 1:**
```
Día 1-2: 10 emails/día
Día 3-4: 20 emails/día
Día 5-7: 30 emails/día
```

**Semana 2:**
```
Día 8-10: 50 emails/día
Día 11-14: 100 emails/día
```

**Semana 3:**
```
Día 15-17: 200 emails/día
Día 18-21: 500 emails/día
```

**Semana 4:**
```
Día 22-24: 1,000 emails/día
Día 25-30: Escalar gradualmente
```

---

## ✅ Checklist de Deliverability

### Pre-Envío:
- [ ] SPF configurado
- [ ] DKIM configurado
- [ ] DMARC configurado
- [ ] Dominio verificado
- [ ] Lista limpia
- [ ] Contenido optimizado
- [ ] HTML validado

### Post-Envío:
- [ ] Monitorear bounces
- [ ] Procesar unsubscribes
- [ ] Revisar spam complaints
- [ ] Monitorear reputación
- [ ] Ajustar según resultados

---

**Optimización completa de deliverability para máxima llegada.** 📬

