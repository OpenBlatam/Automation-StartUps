# Variantes de Gestión de Crisis y Contingencias

## Variante 1: Plan de Contingencia Básico
```json
{
  "contingencia_basica": {
    "nombre": "Plan de Contingencia Básico",
    "descripcion": "Plan básico para manejar problemas comunes",
    "escenarios": [
      {
        "escenario": "Problemas de Conectividad",
        "probabilidad": "Alta",
        "impacto": "Medio",
        "soluciones": [
          "Backup de internet móvil",
          "Plataforma alternativa",
          "Grabación para envío posterior",
          "Comunicación inmediata a participantes"
        ],
        "tiempo_respuesta": "2-5 minutos"
      },
      {
        "escenario": "Falla de Plataforma",
        "probabilidad": "Media",
        "impacto": "Alto",
        "soluciones": [
          "Plataforma de respaldo",
          "Migración automática",
          "Notificación a participantes",
          "Reagendamiento si es necesario"
        ],
        "tiempo_respuesta": "5-10 minutos"
      },
      {
        "escenario": "Problemas de Audio/Video",
        "probabilidad": "Media",
        "impacto": "Medio",
        "soluciones": [
          "Troubleshooting rápido",
          "Cambio de hardware",
          "Instrucciones a participantes",
          "Continuación con audio solo"
        ],
        "tiempo_respuesta": "1-3 minutos"
      }
    ],
    "aplicable_para": "Webinars básicos con riesgos mínimos"
  }
}
```

## Variante 2: Plan de Crisis Técnica
```json
{
  "crisis_tecnica": {
    "nombre": "Plan de Crisis Técnica",
    "descripcion": "Plan detallado para crisis técnicas complejas",
    "niveles": [
      {
        "nivel": "Nivel 1 - Problemas Menores",
        "descripcion": "Problemas que no afectan la continuidad",
        "ejemplos": [
          "Audio con eco",
          "Video de baja calidad",
          "Chat lento",
          "Compartir pantalla intermitente"
        ],
        "acciones": [
          "Troubleshooting automático",
          "Ajustes en tiempo real",
          "Comunicación a participantes",
          "Continuación normal"
        ],
        "tiempo_respuesta": "1-2 minutos"
      },
      {
        "nivel": "Nivel 2 - Problemas Moderados",
        "descripcion": "Problemas que afectan la experiencia",
        "ejemplos": [
          "Pérdida de audio",
          "Video congelado",
          "Plataforma lenta",
          "Participantes desconectados"
        ],
        "acciones": [
          "Cambio de hardware/software",
          "Migración a plataforma backup",
          "Pausa del webinar",
          "Comunicación de estado"
        ],
        "tiempo_respuesta": "3-5 minutos"
      },
      {
        "nivel": "Nivel 3 - Crisis Mayor",
        "descripcion": "Problemas que impiden continuar",
        "ejemplos": [
          "Falla total de plataforma",
          "Pérdida de internet",
          "Hardware dañado",
          "Corte de energía"
        ],
        "acciones": [
          "Activación de plan de respaldo",
          "Notificación inmediata",
          "Reagendamiento",
          "Compensación a participantes"
        ],
        "tiempo_respuesta": "5-10 minutos"
      }
    ],
    "aplicable_para": "Webinars técnicos con alta complejidad"
  }
}
```

## Variante 3: Plan de Crisis de Contenido
```json
{
  "crisis_contenido": {
    "nombre": "Plan de Crisis de Contenido",
    "descripcion": "Plan para manejar crisis relacionadas con contenido",
    "escenarios": [
      {
        "escenario": "Contenido Inapropiado",
        "descripcion": "Participante comparte contenido inapropiado",
        "acciones": [
          "Remoción inmediata",
          "Advertencia al participante",
          "Continuación del webinar",
          "Reporte si es necesario"
        ],
        "prevencion": [
          "Términos y condiciones claros",
          "Moderación activa",
          "Controles de participación"
        ]
      },
      {
        "escenario": "Información Sensible",
        "descripcion": "Accidental exposición de información sensible",
        "acciones": [
          "Pausa inmediata",
          "Remoción de contenido",
          "Notificación a participantes",
          "Revisión de seguridad"
        ],
        "prevencion": [
          "Revisión previa de contenido",
          "Controles de acceso",
          "Capacitación del equipo"
        ]
      },
      {
        "escenario": "Contenido Político",
        "descripcion": "Discusión política no deseada",
        "acciones": [
          "Redirección del tema",
          "Recordatorio de reglas",
          "Continuación profesional",
          "Seguimiento post-webinar"
        ],
        "prevencion": [
          "Reglas claras",
          "Moderación activa",
          "Temas predefinidos"
        ]
      }
    ],
    "aplicable_para": "Webinars con contenido sensible"
  }
}
```

## Variante 4: Plan de Crisis de Seguridad
```json
{
  "crisis_seguridad": {
    "nombre": "Plan de Crisis de Seguridad",
    "descripcion": "Plan para manejar crisis de seguridad",
    "escenarios": [
      {
        "escenario": "Bombing de Webinar",
        "descripcion": "Participantes no autorizados interrumpen",
        "acciones": [
          "Expulsión inmediata",
          "Bloqueo de acceso",
          "Verificación de participantes",
          "Continuación segura"
        ],
        "prevencion": [
          "Contraseñas de acceso",
          "Verificación de identidad",
          "Moderación activa",
          "Controles de participación"
        ]
      },
      {
        "escenario": "Fuga de Información",
        "descripcion": "Información confidencial es compartida",
        "acciones": [
          "Pausa inmediata",
          "Evaluación de daños",
          "Notificación a stakeholders",
          "Medidas correctivas"
        ],
        "prevencion": [
          "Controles de acceso",
          "Capacitación en seguridad",
          "Auditorías regulares",
          "Políticas claras"
        ]
      },
      {
        "escenario": "Ataque Cibernético",
        "descripcion": "Ataque a la plataforma o datos",
        "acciones": [
          "Activación de protocolos de seguridad",
          "Notificación a autoridades",
          "Protección de datos",
          "Comunicación transparente"
        ],
        "prevencion": [
          "Seguridad robusta",
          "Monitoreo continuo",
          "Capacitación del equipo",
          "Protocolos de respuesta"
        ]
      }
    ],
    "aplicable_para": "Webinars con información sensible"
  }
}
```

## Variante 5: Plan de Crisis de Comunicación
```json
{
  "crisis_comunicacion": {
    "nombre": "Plan de Crisis de Comunicación",
    "descripcion": "Plan para manejar crisis de comunicación",
    "elementos": [
      {
        "elemento": "Comunicación Inmediata",
        "descripcion": "Comunicación rápida durante la crisis",
        "canales": [
          "Email de emergencia",
          "Notificación en plataforma",
          "Redes sociales",
          "Sitio web"
        ],
        "mensaje": [
          "Reconocimiento del problema",
          "Acciones tomadas",
          "Tiempo estimado de resolución",
          "Próximos pasos"
        ]
      },
      {
        "elemento": "Comunicación de Seguimiento",
        "descripcion": "Comunicación después de la crisis",
        "canales": [
          "Email de seguimiento",
          "Actualización en plataforma",
          "Redes sociales",
          "Sitio web"
        ],
        "mensaje": [
          "Resumen de la crisis",
          "Acciones tomadas",
          "Medidas preventivas",
          "Disculpas si es necesario"
        ]
      },
      {
        "elemento": "Comunicación Interna",
        "descripcion": "Comunicación con el equipo interno",
        "canales": [
          "Chat interno",
          "Email interno",
          "Reunión de emergencia",
          "Documentación"
        ],
        "mensaje": [
          "Estado de la crisis",
          "Acciones requeridas",
          "Roles y responsabilidades",
          "Próximos pasos"
        ]
      }
    ],
    "aplicable_para": "Webinars con alta visibilidad"
  }
}
```

## Variante 6: Plan de Crisis de Reputación
```json
{
  "crisis_reputacion": {
    "nombre": "Plan de Crisis de Reputación",
    "descripcion": "Plan para manejar crisis de reputación",
    "escenarios": [
      {
        "escenario": "Feedback Negativo",
        "descripcion": "Feedback negativo masivo",
        "acciones": [
          "Reconocimiento inmediato",
          "Investigación del problema",
          "Respuesta pública",
          "Medidas correctivas"
        ],
        "comunicacion": [
          "Transparencia total",
          "Disculpas si es necesario",
          "Plan de mejora",
          "Seguimiento continuo"
        ]
      },
      {
        "escenario": "Escándalo Público",
        "descripcion": "Escándalo que afecta la reputación",
        "acciones": [
          "Evaluación de daños",
          "Respuesta estratégica",
          "Comunicación de crisis",
          "Recuperación de reputación"
        ],
        "comunicacion": [
          "Declaración oficial",
          "Transparencia total",
          "Acciones correctivas",
          "Monitoreo de medios"
        ]
      },
      {
        "escenario": "Competencia Negativa",
        "descripcion": "Ataques de competencia",
        "acciones": [
          "Evaluación de la situación",
          "Respuesta profesional",
          "Enfoque en fortalezas",
          "Diferenciación positiva"
        ],
        "comunicacion": [
          "Mensaje positivo",
          "Evidencia de calidad",
          "Testimonios de clientes",
          "Diferenciación clara"
        ]
      }
    ],
    "aplicable_para": "Webinars con alta visibilidad pública"
  }
}
```

## Variante 7: Plan de Crisis de Recursos
```json
{
  "crisis_recursos": {
    "nombre": "Plan de Crisis de Recursos",
    "descripcion": "Plan para manejar crisis de recursos",
    "escenarios": [
      {
        "escenario": "Falta de Personal",
        "descripcion": "Personal clave no disponible",
        "acciones": [
          "Activación de personal de respaldo",
          "Redistribución de roles",
          "Capacitación de emergencia",
          "Simplificación de procesos"
        ],
        "prevencion": [
          "Personal de respaldo",
          "Capacitación cruzada",
          "Documentación completa",
          "Protocolos de emergencia"
        ]
      },
      {
        "escenario": "Falta de Equipos",
        "descripcion": "Equipos técnicos no disponibles",
        "acciones": [
          "Uso de equipos alternativos",
          "Préstamo de equipos",
          "Simplificación técnica",
          "Reagendamiento si es necesario"
        ],
        "prevencion": [
          "Equipos de respaldo",
          "Mantenimiento preventivo",
          "Contratos de servicio",
          "Inventario actualizado"
        ]
      },
      {
        "escenario": "Falta de Presupuesto",
        "descripcion": "Recursos financieros limitados",
        "acciones": [
          "Priorización de recursos",
          "Búsqueda de financiamiento",
          "Simplificación de servicios",
          "Negociación con proveedores"
        ],
        "prevencion": [
          "Presupuesto de emergencia",
          "Múltiples fuentes de financiamiento",
          "Contratos flexibles",
          "Monitoreo financiero"
        ]
      }
    ],
    "aplicable_para": "Webinars con recursos limitados"
  }
}
```

## Variante 8: Plan de Crisis de Tiempo
```json
{
  "crisis_tiempo": {
    "nombre": "Plan de Crisis de Tiempo",
    "descripcion": "Plan para manejar crisis de tiempo",
    "escenarios": [
      {
        "escenario": "Retraso del Presentador",
        "descripcion": "Presentador principal se retrasa",
        "acciones": [
          "Comunicación inmediata",
          "Contenido de relleno",
          "Presentador de respaldo",
          "Reagendamiento si es necesario"
        ],
        "prevencion": [
          "Presentadores de respaldo",
          "Contenido de relleno",
          "Plan de comunicación",
          "Flexibilidad en horarios"
        ]
      },
      {
        "escenario": "Sobrepaso de Tiempo",
        "descripcion": "Webinar se extiende más de lo planeado",
        "acciones": [
          "Comunicación de extensión",
          "Priorización de contenido",
          "Pausa para descanso",
          "Ajuste de agenda"
        ],
        "prevencion": [
          "Agenda flexible",
          "Contenido prioritario",
          "Tiempo de buffer",
          "Comunicación previa"
        ]
      },
      {
        "escenario": "Corte de Tiempo",
        "descripcion": "Tiempo limitado disponible",
        "acciones": [
          "Priorización de contenido",
          "Resumen ejecutivo",
          "Materiales de seguimiento",
          "Sesión de seguimiento"
        ],
        "prevencion": [
          "Agenda clara",
          "Contenido prioritario",
          "Tiempo de buffer",
          "Plan de seguimiento"
        ]
      }
    ],
    "aplicable_para": "Webinars con restricciones de tiempo"
  }
}
```

## Variante 9: Plan de Crisis de Calidad
```json
{
  "crisis_calidad": {
    "nombre": "Plan de Crisis de Calidad",
    "descripcion": "Plan para manejar crisis de calidad",
    "escenarios": [
      {
        "escenario": "Calidad Técnica Baja",
        "descripcion": "Calidad técnica por debajo de estándares",
        "acciones": [
          "Ajustes técnicos inmediatos",
          "Comunicación de problemas",
          "Mejoras en tiempo real",
          "Compensación si es necesario"
        ],
        "prevencion": [
          "Testing previo",
          "Estándares de calidad",
          "Monitoreo continuo",
          "Mejoras preventivas"
        ]
      },
      {
        "escenario": "Contenido de Baja Calidad",
        "descripcion": "Contenido no cumple expectativas",
        "acciones": [
          "Ajuste de contenido",
          "Comunicación transparente",
          "Mejoras inmediatas",
          "Seguimiento de calidad"
        ],
        "prevencion": [
          "Revisión previa",
          "Estándares de contenido",
          "Capacitación del equipo",
          "Feedback continuo"
        ]
      },
      {
        "escenario": "Experiencia del Usuario",
        "descripcion": "Experiencia del usuario por debajo de estándares",
        "acciones": [
          "Mejoras inmediatas",
          "Comunicación de mejoras",
          "Feedback de usuarios",
          "Plan de mejora continua"
        ],
        "prevencion": [
          "Testing de usuario",
          "Estándares de UX",
          "Monitoreo de satisfacción",
          "Mejoras continuas"
        ]
      }
    ],
    "aplicable_para": "Webinars con altos estándares de calidad"
  }
}
```

## Variante 10: Plan de Crisis Integral
```json
{
  "crisis_integral": {
    "nombre": "Plan de Crisis Integral",
    "descripcion": "Plan completo para manejar cualquier tipo de crisis",
    "elementos": [
      {
        "elemento": "Identificación de Crisis",
        "descripcion": "Sistema para identificar y clasificar crisis",
        "componentes": [
          "Indicadores de crisis",
          "Sistema de alertas",
          "Clasificación de severidad",
          "Protocolos de activación"
        ]
      },
      {
        "elemento": "Respuesta Inmediata",
        "descripcion": "Respuesta inmediata a cualquier crisis",
        "componentes": [
          "Activación de protocolos",
          "Comunicación inmediata",
          "Acciones de contención",
          "Evaluación de daños"
        ]
      },
      {
        "elemento": "Recuperación",
        "descripcion": "Proceso de recuperación después de la crisis",
        "componentes": [
          "Evaluación post-crisis",
          "Plan de recuperación",
          "Comunicación de seguimiento",
          "Mejoras preventivas"
        ]
      },
      {
        "elemento": "Prevención",
        "descripcion": "Medidas preventivas para evitar crisis",
        "componentes": [
          "Análisis de riesgos",
          "Medidas preventivas",
          "Capacitación del equipo",
          "Monitoreo continuo"
        ]
      }
    ],
    "aplicable_para": "Webinars con riesgo alto y alta visibilidad"
  }
}
```
