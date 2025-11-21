# 🔄 Flujo de Trabajo Visual del Chatbot

## Diagrama de Flujo Principal

```
┌─────────────────────────────────────────────────────────────────┐
│                    USUARIO ENVÍA MENSAJE                        │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              RECEPCIÓN Y PREPROCESAMIENTO                        │
│  • Detectar canal (Web/WhatsApp/Email)                          │
│  • Detectar idioma                                              │
│  • Obtener/crear sesión                                         │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              ANÁLISIS DE MENSAJE                                │
│  • Análisis de sentimiento (Positivo/Negativo/Neutral/Frustrado)│
│  • Detección de intención (Pregunta/Queja/Solicitud/etc.)       │
│  • Guardar en historial de conversación                         │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
        ┌───────────────────┐  ┌───────────────────┐
        │  ¿REQUIERE        │  │  ¿ES SALUDO/      │
        │  ESCALAMIENTO?    │  │  DESPEDIDA?       │
        └─────────┬─────────┘  └─────────┬─────────┘
                  │                     │
        ┌─────────┴─────────┐           │
        │                   │           │
        ▼                   ▼           ▼
┌───────────────┐  ┌──────────────────────────────┐
│ SÍ - CRÍTICO  │  │ NO - BUSCAR EN FAQs          │
│               │  │                              │
│ • Crear ticket│  │ • Matching semántico         │
│ • Prioridad   │  │ • Calcular confianza         │
│   CRÍTICA     │  │ • Buscar mejor coincidencia  │
│ • Notificar   │  └────────────┬─────────────────┘
│   CRM         │               │
└───────┬───────┘               │
        │                       │
        │                       ▼
        │              ┌─────────────────┐
        │              │ ¿ENCONTRÓ FAQ?  │
        │              └────────┬─────────┘
        │                       │
        │           ┌───────────┴───────────┐
        │           │                       │
        │           ▼                       ▼
        │   ┌───────────────┐      ┌───────────────┐
        │   │ SÍ - FAQ      │      │ NO - RESPUESTA│
        │   │ ENCONTRADA    │      │ POR DEFECTO   │
        │   │               │      │               │
        │   │ • Aplicar A/B │      │ • Sugerir     │
        │   │   Testing     │      │   opciones    │
        │   │ • Personalizar│      │ • Ofrecer     │
        │   │   según       │      │   escalar     │
        │   │   sentimiento │      │               │
        │   └───────┬───────┘      └───────┬───────┘
        │           │                       │
        └───────────┴───────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              FORMATO DE RESPUESTA                                │
│  • Agregar emojis (si está habilitado)                          │
│  • Aplicar tono personalizado                                    │
│  • Incluir acciones sugeridas                                   │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              ENVÍO DE RESPUESTA                                  │
│  • Enviar por canal original                                    │
│  • Registrar métricas                                           │
│  • Actualizar contexto de conversación                          │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              INTEGRACIONES                                       │
│  • Sincronizar con CRM (si aplica)                              │
│  • Enviar webhook a Zapier (si aplica)                          │
│  • Registrar en dashboard                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Flujo de Escalamiento

```
┌─────────────────────────────────────────────────────────────────┐
│              DETECCIÓN DE ESCALAMIENTO                           │
│  • Palabras clave críticas detectadas                          │
│  • Sentimiento muy negativo/frustrado                            │
│  • Múltiples intentos sin resolución                           │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              CREAR TICKET                                        │
│  • Generar ID único                                             │
│  • Asignar prioridad (Crítica/Alta/Media)                      │
│  • Incluir contexto completo                                    │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
        ┌───────────────────┐  ┌───────────────────┐
        │  ¿CRM CONFIGURADO?│  │  ¿ZAPIER ACTIVO?  │
        └─────────┬─────────┘  └─────────┬─────────┘
                  │                     │
        ┌─────────┴─────────┐  ┌─────────┴─────────┐
        │                   │  │                   │
        ▼                   ▼  ▼                   ▼
┌───────────────┐  ┌──────────────────────────────┐
│ Sincronizar   │  │ Enviar webhook                │
│ con Salesforce│  │ a Zapier                       │
│               │  │                                │
│ • Crear caso  │  │ • Trigger automatización      │
│ • Asignar     │  │ • Notificar equipo            │
│ • Notificar   │  │ • Crear tarea                 │
└───────┬───────┘  └────────────┬───────────────────┘
        │                       │
        └───────────┬───────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│              NOTIFICAR AL USUARIO                                │
│  • Enviar mensaje con número de ticket                          │
│  • Informar tiempo estimado de respuesta                         │
│  • Ofrecer contacto directo si es urgente                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Flujo de A/B Testing

```
┌─────────────────────────────────────────────────────────────────┐
│              MENSAJE RECIBIDO                                    │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              ¿A/B TESTING HABILITADO?                            │
└────────────────────────────┬────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
        ┌───────────────────┐  ┌───────────────────┐
        │ SÍ                │  │ NO                │
        │                   │  │                   │
        │ • Obtener variante │  │ • Usar respuesta │
        │   basada en user_id│  │   estándar        │
        │ • A = 50%          │  │                   │
        │ • B = 50%          │  └───────────────────┘
        └─────────┬─────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌───────────────┐  ┌───────────────────┐
│ VARIANTE A    │  │ VARIANTE B        │
│               │  │                   │
│ • Tono formal │  │ • Tono casual     │
│ • Sin emojis  │  │ • Con emojis      │
│ • Respuesta   │  │ • Respuesta       │
│   estándar    │  │   personalizada   │
└───────┬───────┘  └─────────┬─────────┘
        │                     │
        └───────────┬─────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│              ENVIAR RESPUESTA                                    │
│  • Registrar variante usada                                     │
│  • Registrar métricas (satisfacción, resolución)                │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              ANÁLISIS PERIÓDICO                                  │
│  • Comparar métricas entre variantes                            │
│  • Identificar variante ganadora                                │
│  • Implementar variante óptima                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Flujo de Análisis de Sentimientos

```
┌─────────────────────────────────────────────────────────────────┐
│              MENSAJE RECIBIDO                                    │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              ANÁLISIS DE SENTIMIENTO                             │
│  • Buscar palabras positivas/negativas                          │
│  • Detectar frustración (mayúsculas, múltiples !)               │
│  • Calcular score                                               │
└────────────────────────────┬────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
        ┌───────────────────┐  ┌───────────────────┐
        │ POSITIVO/NEUTRAL  │  │ NEGATIVO/        │
        │                   │  │ FRUSTRADO        │
        └─────────┬─────────┘  └─────────┬─────────┘
                  │                     │
        ┌─────────┴─────────┐  ┌─────────┴─────────┐
        │                   │  │                   │
        ▼                   ▼  ▼                   ▼
┌───────────────┐  ┌──────────────────────────────┐
│ Respuesta     │  │ • Personalizar respuesta      │
│ estándar      │  │ • Considerar escalamiento     │
│               │  │ • Tono empático               │
│ • Tono normal │  │ • Ofrecer ayuda adicional    │
│ • Sin cambios │  └────────────┬──────────────────┘
└───────────────┘               │
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
        ┌───────────────────┐  ┌───────────────────┐
        │ ¿MÚLTIPLES        │  │ ESCALAR          │
        │ NEGATIVOS?        │  │ AUTOMÁTICAMENTE  │
        └─────────┬─────────┘  └─────────┬────────┘
                  │                     │
        ┌─────────┴─────────┐           │
        │                   │           │
        ▼                   ▼           │
┌───────────────┐  ┌───────────────────┐
│ NO - Continuar│  │ SÍ - Crear ticket │
│ normal        │  │ prioritario       │
└───────────────┘  └───────────────────┘
```

---

## Flujo de Integraciones

```
┌─────────────────────────────────────────────────────────────────┐
│              EVENTO DEL CHATBOT                                  │
│  • Mensaje procesado                                             │
│  • Ticket creado                                                 │
│  • Satisfacción registrada                                        │
└────────────────────────────┬────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
        ┌───────────────────┐  ┌───────────────────┐
        │ ¿CRM CONFIGURADO?│  │ ¿ZAPIER ACTIVO?  │
        └─────────┬─────────┘  └─────────┬─────────┘
                  │                     │
        ┌─────────┴─────────┐  ┌─────────┴─────────┐
        │                   │  │                   │
        ▼                   ▼  ▼                   ▼
┌───────────────┐  ┌──────────────────────────────┐
│ SALESFORCE    │  │ ZAPIER                       │
│               │  │                               │
│ • Crear lead  │  │ • Disparar webhook           │
│ • Crear caso  │  │ • Ejecutar automatización   │
│ • Actualizar  │  │ • Notificar sistemas        │
│   contacto    │  │ • Crear tareas               │
└───────┬───────┘  └────────────┬───────────────────┘
        │                       │
        └───────────┬───────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│              OTRAS INTEGRACIONES                                 │
│  • WhatsApp: Enviar notificación                                │
│  • Email: Enviar resumen                                        │
│  • Dashboard: Actualizar métricas                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Flujo de Métricas y Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│              EVENTOS DEL CHATBOT                                 │
│  • Interacción procesada                                         │
│  • Respuesta enviada                                            │
│  • Ticket creado                                                 │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              REGISTRO DE MÉTRICAS                                │
│  • Incrementar contadores                                       │
│  • Calcular promedios                                           │
│  • Actualizar distribuciones                                    │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              ALMACENAMIENTO                                      │
│  • Guardar en memoria (tiempo real)                             │
│  • Persistir en base de datos (opcional)                        │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              DASHBOARD                                           │
│  • Actualizar KPIs en tiempo real                                │
│  • Refrescar gráficos                                           │
│  • Mostrar alertas si no se cumplen objetivos                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estados de Conversación

```
┌─────────────────────────────────────────────────────────────────┐
│                    NUEVA CONVERSACIÓN                            │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
        ┌───────────────────┐  ┌───────────────────┐
        │ CONVERSACIÓN       │  │ CONVERSACIÓN       │
        │ ACTIVA             │  │ EN PROGRESO        │
        │                    │  │                    │
        │ • < 1 hora sin     │  │ • Mensajes         │
        │   actividad        │  │   recientes        │
        │ • Historial        │  │ • Contexto         │
        │   disponible       │  │   disponible       │
        └─────────┬─────────┘  └─────────┬─────────┘
                  │                     │
        ┌─────────┴─────────┐  ┌─────────┴─────────┐
        │                   │  │                   │
        ▼                   ▼  ▼                   ▼
┌───────────────┐  ┌──────────────────────────────┐
│ RESUELTA      │  │ ESCALADA                      │
│               │  │                               │
│ • FAQ         │  │ • Ticket creado               │
│   respondida  │  │ • Agente asignado            │
│ • Usuario     │  │ • En seguimiento             │
│   satisfecho  │  │                               │
└───────┬───────┘  └────────────┬───────────────────┘
        │                       │
        └───────────┬───────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│              CONVERSACIÓN ARCHIVADA                              │
│  • > 24 horas sin actividad                                     │
│  • Guardada para análisis                                       │
│  • Disponible para consulta histórica                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Leyenda de Símbolos

- **┌─┐**: Proceso/Acción
- **├─┤**: Decisión/Condición
- **└─┘**: Inicio/Fin
- **→**: Flujo de datos
- **▼**: Dirección del flujo

---

**Versión**: 1.0  
**Última actualización**: 2024






