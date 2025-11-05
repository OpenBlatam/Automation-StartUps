# Nomenclatura y Sistema de Tagging

Sistema consistente para nombrar y etiquetar leads, campañas, y métricas.

---

## 🏷️ Tags para Leads en CRM

### Por Producto
- `producto_curso_ia`
- `producto_saas_marketing`
- `producto_bulk_documentos`

### Por Industria
- `industria_saas`
- `industria_ecommerce`
- `industria_fintech`
- `industria_health`
- `industria_education`
- `industria_retail`
- `industria_manufacturing`
- `industria_consulting`

### Por Rol
- `rol_ceo`
- `rol_cmo`
- `rol_coo`
- `rol_cto`
- `rol_cfo`
- `rol_marketing_manager`
- `rol_sales_director`
- `rol_operations_manager`

### Por Estado del Lead
- `estado_nuevo` — Lead nuevo, sin contactar
- `estado_dm_enviado` — DM inicial enviado
- `estado_seguimiento_1` — Primer seguimiento enviado
- `estado_seguimiento_2` — Segundo seguimiento enviado
- `estado_seguimiento_3` — Tercer seguimiento enviado
- `estado_respuesta_positiva` — Respondió positivamente
- `estado_respuesta_neutra` — Respondió neutro/pregunta
- `estado_objecion` — Tiene objeción específica
- `estado_cualificado` — Pasó BANT
- `estado_demo_agendada` — Demo/llamada agendada
- `estado_convertido` — Cliente
- `estado_nurture` — Guardado para futuro
- `estado_cerrado` — Cerró conversación

### Por Versión de DM Usada
- `dm_version_vip`
- `dm_version_roi`
- `dm_version_equipo`
- `dm_version_inovacion`
- `dm_version_resistente`
- `dm_version_estandar`

### Por Origen
- `origen_linkedin_search`
- `origen_evento_[NOMBRE]`
- `origen_recomendacion`
- `origen_conexion_mutual`
- `origen_contenido_post`
- `origen_noticia_medios`
- `origen_webinar`
- `origen_cold_email`

### Por Score/Prioridad
- `prioridad_alta` — Score 4-5
- `prioridad_media` — Score 2-3
- `prioridad_baja` — Score 0-1
- `prioridad_caliente` — Evento reciente o señal fuerte

### Por Canal
- `canal_linkedin_inmail`
- `canal_linkedin_connection`
- `canal_email_cold`
- `canal_email_warm`

### Por Región/País
- `pais_mexico`
- `pais_colombia`
- `pais_argentina`
- `pais_chile`
- `pais_espana`
- `pais_usa`
- `pais_brasil`

---

## 📁 Nomenclatura de Archivos

### DMs Generados
Formato: `DM_[PRODUCTO]_[LEAD]_[FECHA].txt`
Ejemplo: `DM_saas_marketing_Ana_Rodriguez_2024-01-15.txt`

### Leads CSV
Formato: `LEADS_[ORIGEN]_[FECHA].csv`
Ejemplo: `LEADS_evento_webinar_ia_2024-01-15.csv`

### Reportes
Formato: `REPORTE_[TIPO]_[PERIODO].md`
Ejemplos:
- `REPORTE_MENSUAL_2024-01.md`
- `REPORTE_TRIMESTRAL_Q1_2024.md`

### A/B Tests
Formato: `AB_TEST_[OBJETIVO]_[FECHA_INICIO].md`
Ejemplo: `AB_TEST_subject_line_2024-01-15.md`

---

## 🎯 Nomenclatura de Campañas/UTM

### UTM Campaign (utm_campaign)
Formato: `[PRODUCTO]_[CANAL]_[OBJETIVO]_[FECHA]`

Ejemplos:
- `saas_marketing_linkedin_demo_2024-01`
- `curso_ia_email_lead_2024-01`
- `bulk_documentos_linkedin_conversion_2024-01`

### UTM Source (utm_source)
- `linkedin_inmail`
- `linkedin_connection`
- `email_cold`
- `email_warm`
- `webinar`
- `evento_live`
- `contenido_blog`

### UTM Medium (utm_medium)
- `social`
- `email`
- `paid_social` (si aplica)
- `referral`
- `direct`

### UTM Content (utm_content)
Formato: `[VERSION_DM]_[INDUSTRIA]`

Ejemplos:
- `version_vip_saas`
- `version_roi_ecommerce`
- `version_equipo_fintech`

### UTM Term (utm_term)
Formato: `[ROL]_[PAIS]`

Ejemplos:
- `cmo_mexico`
- `ceo_colombia`
- `coo_argentina`

---

## 🔢 Nomenclatura de Métricas en Dashboard

### Nombres de Columnas (Sheets/Excel)
- `fecha_envio`
- `lead_nombre`
- `lead_empresa`
- `lead_industria`
- `lead_rol`
- `producto`
- `canal`
- `version_dm`
- `utm_campaign`
- `respuesta` — Sí/No/Pendiente
- `fecha_respuesta`
- `tipo_respuesta` — Positiva/Objeción/Neutra
- `objeción` — Tipo de objeción si aplica
- `cualificado` — Sí/No (BANT)
- `demo_agendada` — Sí/No
- `convertido` — Sí/No
- `fecha_conversion`
- `revenue`
- `cac`

### Nombres de Métricas Calculadas
- `tasa_respuesta` — Respuestas / Enviados
- `tasa_conversion` — Conversiones / Respuestas
- `cac_promedio` — Costo total / Conversiones
- `roi` — Revenue / Costo
- `tiempo_respuesta_promedio` — Días entre envío y respuesta

---

## 📋 Estructura de Notas en CRM

### Nota de DM Enviado
```
[FECHA] - DM Enviado
Producto: [PRODUCTO]
Versión: [VERSION]
Canal: [CANAL]
Logro mencionado: [LOGRO]
CTA: [CTA]
UTM: [LINK_UTM]
Próximo seguimiento: [FECHA]
```

### Nota de Respuesta
```
[FECHA] - Respuesta Recibida
Tipo: Positiva/Neutra/Objeción
Contenido: [RESUMEN]
Acción tomada: [ACCION]
Próximo paso: [PASO]
```

### Nota de Cualificación
```
[FECHA] - Lead Cualificado (BANT)
Budget: [SÍ/NO/CONOCIDO]
Authority: [SÍ/NO]
Need: [SÍ/NO/DESCRIPCIÓN]
Timeline: [SÍ/NO/ESTIMADO]
Score: [X]/5
```

---

## 🗂️ Estructura de Carpetas (Opcional)

Si organizas archivos localmente:

```
outreach/
├── dms/
│   ├── curso_ia/
│   ├── saas_marketing/
│   └── bulk_documentos/
├── leads/
│   ├── nuevos/
│   ├── en_proceso/
│   ├── cualificados/
│   └── convertidos/
├── reportes/
│   ├── mensuales/
│   └── trimestrales/
├── ab_tests/
└── templates/
```

---

## 🔍 Búsquedas Rápidas en CRM

### Buscar Leads Activos
Tags: `estado_dm_enviado` OR `estado_seguimiento_1` OR `estado_seguimiento_2`

### Buscar Leads de Alta Prioridad
Tags: `prioridad_alta` OR `prioridad_caliente`

### Buscar Leads por Producto
Tags: `producto_[PRODUCTO]`

### Buscar Leads Necesitando Seguimiento
Tags: `estado_dm_enviado` AND fecha_enviado > [FECHA_4_DIAS_ATRAS]

### Buscar Leads Convertidos Este Mes
Tags: `estado_convertido` AND fecha_conversion >= [INICIO_MES]

---

## 📊 Convenciones para Dashboards

### Colores Sugeridos (si aplica)
- 🟢 Verde: Conversión/Éxito
- 🟡 Amarillo: En Proceso/Pendiente
- 🔴 Rojo: Necesita Atención/Cerrado
- 🔵 Azul: Información/Data

### Formato de Fechas
- Internacional: `YYYY-MM-DD` (ej: 2024-01-15)
- Alternativo: `DD/MM/YYYY` (ej: 15/01/2024)

### Formato de Números
- Decimales: 2 decimales (ej: 12.34%)
- Porcentajes: Con % (ej: 12.34%)
- Moneda: Prefijo $ (ej: $1,234.56)

---

## ✅ Checklist de Consistencia

Antes de crear nuevo lead o campaña, verifica:

- [ ] Tags siguen nomenclatura estándar
- [ ] UTM parameters siguen formato establecido
- [ ] Nombre de archivo sigue convención
- [ ] Notas en CRM siguen estructura
- [ ] Datos en dashboard siguen formato

---

## 📚 Referencias

- `CRM_OUTREACH_FIELDS.csv` — Campos estándar para CRM
- `UTM_GUIDE_OUTREACH.md` — Guía completa de UTM
- `KPI_DASHBOARD_TEMPLATE.md` — Estructura de dashboard

---

**💡 Pro Tip**: La consistencia en nomenclatura ahorra horas de búsqueda y análisis. Mantén este documento actualizado si agregas nuevas categorías.

