# 🔗 Template UTMs para LinkedIn Ads

## Estructura UTM

```
https://tudominio.com/landing-page?
utm_source=linkedin&
utm_medium=cpc&
utm_campaign=[CAMPAÑA]&
utm_content=[CREATIVO]&
utm_term=[AUDIENCIA]
```

---

## 📋 Template por Servicio

### Curso de IA + Webinars

```bash
# Base
https://tudominio.com/curso-ia?
utm_source=linkedin&utm_medium=cpc&utm_campaign=curso_ia_tofu&utm_content=base_1200x627&utm_term=directores_marketing

# Con Métricas
https://tudominio.com/curso-ia?
utm_source=linkedin&utm_medium=cpc&utm_campaign=curso_ia_tofu&utm_content=metrics_1200x627&utm_term=directores_marketing

# Light
https://tudominio.com/curso-ia?
utm_source=linkedin&utm_medium=cpc&utm_campaign=curso_ia_tofu&utm_content=light_1200x627&utm_term=directores_marketing

# Social Proof
https://tudominio.com/curso-ia?
utm_source=linkedin&utm_medium=cpc&utm_campaign=curso_ia_mofu&utm_content=social_proof_1200x627&utm_term=directores_marketing

# Urgency
https://tudominio.com/curso-ia?
utm_source=linkedin&utm_medium=cpc&utm_campaign=curso_ia_bofu&utm_content=urgency_1200x627&utm_term=directores_marketing

# Carrusel
https://tudominio.com/curso-ia?
utm_source=linkedin&utm_medium=cpc&utm_campaign=curso_ia_tofu&utm_content=carousel_5slides&utm_term=directores_marketing
```

### SaaS de IA para Marketing

```bash
# Base
https://tudominio.com/saas-ia?
utm_source=linkedin&utm_medium=cpc&utm_campaign=saas_ia_tofu&utm_content=base_1200x627&utm_term=cmos_enterprise

# Con Métricas
https://tudominio.com/saas-ia?
utm_source=linkedin&utm_medium=cpc&utm_campaign=saas_ia_tofu&utm_content=metrics_1200x627&utm_term=cmos_enterprise

# Light
https://tudominio.com/saas-ia?
utm_source=linkedin&utm_medium=cpc&utm_campaign=saas_ia_tofu&utm_content=light_1200x627&utm_term=cmos_enterprise

# Social Proof
https://tudominio.com/saas-ia?
utm_source=linkedin&utm_medium=cpc&utm_campaign=saas_ia_mofu&utm_content=social_proof_1200x627&utm_term=cmos_enterprise

# Urgency (Demo)
https://tudominio.com/saas-ia?
utm_source=linkedin&utm_medium=cpc&utm_campaign=saas_ia_bofu&utm_content=urgency_1200x627&utm_term=cmos_enterprise
```

### IA Bulk (Documentos)

```bash
# Base
https://tudominio.com/ia-bulk?
utm_source=linkedin&utm_medium=cpc&utm_campaign=ia_bulk_tofu&utm_content=base_1200x627&utm_term=equipos_marketing

# Con Métricas
https://tudominio.com/ia-bulk?
utm_source=linkedin&utm_medium=cpc&utm_campaign=ia_bulk_tofu&utm_content=metrics_1200x627&utm_term=equipos_marketing

# Light
https://tudominio.com/ia-bulk?
utm_source=linkedin&utm_medium=cpc&utm_campaign=ia_bulk_tofu&utm_content=light_1200x627&utm_term=equipos_marketing

# Social Proof
https://tudominio.com/ia-bulk?
utm_source=linkedin&utm_medium=cpc&utm_campaign=ia_bulk_mofu&utm_content=social_proof_1200x627&utm_term=equipos_marketing

# Urgency
https://tudominio.com/ia-bulk?
utm_source=linkedin&utm_medium=cpc&utm_campaign=ia_bulk_bofu&utm_content=urgency_1200x627&utm_term=equipos_marketing
```

---

## 🎯 Parámetros UTM

### utm_source
- Siempre: `linkedin`

### utm_medium
- Siempre: `cpc` (Cost Per Click)

### utm_campaign
Formato: `[servicio]_[etapa_funnel]`

**Servicios:**
- `curso_ia`
- `saas_ia`
- `ia_bulk`

**Etapas del Funnel:**
- `tofu` - Top of Funnel (awareness)
- `mofu` - Middle of Funnel (consideration)
- `bofu` - Bottom of Funnel (conversion)

**Ejemplos:**
- `curso_ia_tofu`
- `saas_ia_mofu`
- `ia_bulk_bofu`

### utm_content
Formato: `[variante]_[formato]`

**Variantes:**
- `base` - Versión base
- `v2` - Versión mejorada
- `metrics` - Con métricas
- `light` - Fondo claro
- `social_proof` - Prueba social
- `urgency` - Urgencia
- `carousel_5slides` - Carrusel completo

**Formatos:**
- `1200x627` - Feed principal
- `1080x1080` - Cuadrado
- `1080x1920` - Stories/vertical

**Ejemplos:**
- `metrics_1200x627`
- `social_proof_1080x1080`
- `urgency_1080x1920`

### utm_term
Audiencia o palabra clave

**Ejemplos:**
- `directores_marketing`
- `cmos_enterprise`
- `equipos_marketing`
- `empresas_medianas`
- `startups`

---

## 📊 Tracking y Análisis

### Google Analytics 4

**Dimensiones personalizadas:**
- `utm_campaign` → Agrupa por campaña
- `utm_content` → Compara creativos
- `utm_term` → Analiza audiencias

**Métricas a trackear:**
- Sessions por `utm_content`
- Conversion Rate por `utm_campaign`
- Bounce Rate por creativo
- Time on Site por variante

### LinkedIn Ads Manager

**Reportes:**
- Performance por ad (ya incluye UTM)
- Comparar creativos
- Analizar por formato

---

## 🔄 Uso en LinkedIn Ads Manager

1. **Crear Campaña**
   - Nombre: Ej. "Curso IA - TOFU"

2. **Configurar URL de destino**
   - Copiar template UTM correspondiente
   - Reemplazar `tudominio.com` con dominio real

3. **Subir Creativos**
   - Seleccionar PNG exportado
   - El UTM ya está en la URL

4. **Tracking**
   - LinkedIn rastrea clicks automáticamente
   - GA4 rastrea conversiones con UTMs

---

## 💡 Best Practices

1. **Consistencia**: Usa mismos parámetros para misma variante
2. **Claridad**: Nombres descriptivos en `utm_campaign`
3. **Minúsculas**: Todo en lowercase para evitar duplicados
4. **Sin espacios**: Usa guiones bajos o guiones
5. **Documentación**: Mantén lista de UTMs activos

---

## 📝 Checklist Pre-Publicación

- [ ] UTMs configurados en todas las URLs
- [ ] Landing pages preparadas para recibir UTMs
- [ ] Google Analytics configurado para tracking
- [ ] Testing de URLs antes de publicar
- [ ] Documentación de UTMs actualizada
- [ ] Equipo informado sobre parámetros

---

## 🔗 Generador Rápido

```
Servicio: [curso_ia|saas_ia|ia_bulk]
Etapa: [tofu|mofu|bofu]
Variante: [base|v2|metrics|light|social_proof|urgency]
Formato: [1200x627|1080x1080|1080x1920]
Audiencia: [directores_marketing|cmos_enterprise|equipos_marketing]

URL generada:
https://tudominio.com/[servicio]?
utm_source=linkedin&
utm_medium=cpc&
utm_campaign=[servicio]_[etapa]&
utm_content=[variante]_[formato]&
utm_term=[audiencia]
```

---

**Nota**: Reemplaza `tudominio.com` y las rutas con tus URLs reales antes de usar.


