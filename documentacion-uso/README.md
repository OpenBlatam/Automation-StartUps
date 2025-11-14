# 📚 Guía de Uso Completa del Proyecto

> Documentación centralizada para usar todos los componentes de la Plataforma de Automatización Empresarial

## 🎯 Propósito

Esta carpeta contiene toda la documentación necesaria para **usar** el proyecto completo. Aquí encontrarás guías paso a paso, ejemplos prácticos, y referencias rápidas para cada componente del sistema.

## 📋 Índice General

### 🚀 Inicio Rápido
- [Guía de Inicio Rápido](./01-inicio-rapido/README.md) - Empieza en 5 minutos
- [Instalación y Configuración](./01-inicio-rapido/instalacion.md) - Setup completo del entorno
- [Primeros Pasos](./01-inicio-rapido/primeros-pasos.md) - Tu primer workflow/automatización

### 🏗️ Componentes Principales

#### Workflows y Orquestación
- [Kestra - Workflows Declarativos](./02-componentes/kestra.md) - Crear workflows con YAML
- [Flowable - Procesos BPMN](./02-componentes/flowable.md) - Procesos de negocio formales
- [Camunda - BPMN Enterprise](./02-componentes/camunda.md) - BPMN avanzado
- [n8n - Automatizaciones](./02-componentes/n8n.md) - Workflows visuales y automatizaciones

#### Automatización de Datos
- [Airflow - Pipelines ETL](./02-componentes/airflow.md) - ETL y procesamiento de datos
- [Integraciones de Datos](./02-componentes/integraciones-datos.md) - Conectar con fuentes externas
- [Procesamiento de Documentos](./02-componentes/procesamiento-documentos.md) - OCR, clasificación, extracción

#### RPA y Automatización
- [OpenRPA - Automatización UI](./02-componentes/openrpa.md) - Bots para tareas repetitivas
- [Automatización TikTok](./02-componentes/tiktok-automation.md) - Sistema completo de edición automática

#### Machine Learning
- [MLflow - Tracking de Modelos](./02-componentes/mlflow.md) - Gestión del ciclo de vida ML
- [Kubeflow - Pipelines ML](./02-componentes/kubeflow.md) - Pipelines de machine learning
- [KServe - Model Serving](./02-componentes/kserve.md) - Servir modelos en producción

#### Observabilidad y Monitoreo
- [Grafana - Dashboards](./02-componentes/grafana.md) - Visualización y métricas
- [Prometheus - Métricas](./02-componentes/prometheus.md) - Recolección de métricas
- [Sistema de KPIs](./02-componentes/kpis.md) - Dashboards y reportes automáticos

### 🎯 Casos de Uso Prácticos

- [Automatización de Campañas de Marketing](./03-casos-uso/campanas-marketing.md)
- [Rastreo de Pedidos y Chatbot](./03-casos-uso/rastreo-pedidos.md)
- [Customer Journey Mapping](./03-casos-uso/customer-journey.md)
- [Análisis de Engagement en Redes Sociales](./03-casos-uso/analisis-engagement.md)
- [Procesamiento Masivo de Documentos](./03-casos-uso/procesamiento-documentos.md)
- [Sistema de Reportes Automáticos](./03-casos-uso/reportes-automaticos.md)

### 🔧 Operación y Mantenimiento

- [Despliegue en Producción](./04-operacion/despliegue.md) - Guía completa de deployment
- [Configuración de Entornos](./04-operacion/entornos.md) - Dev, Staging, Producción
- [Backups y Restauración](./04-operacion/backups.md) - Estrategias de backup
- [Monitoreo y Alertas](./04-operacion/monitoreo.md) - Configurar alertas
- [Escalado y Performance](./04-operacion/escalado.md) - Optimizar rendimiento
- [Troubleshooting Común](./04-operacion/troubleshooting.md) - Solución de problemas frecuentes

### 🔐 Seguridad

- [Configuración de Seguridad](./05-seguridad/configuracion.md) - Setup inicial de seguridad
- [Gestión de Secretos](./05-seguridad/secretos.md) - External Secrets, Vault
- [Network Policies](./05-seguridad/network-policies.md) - Políticas de red
- [RBAC y Permisos](./05-seguridad/rbac.md) - Control de acceso
- [Auditoría y Logging](./05-seguridad/auditoria.md) - Logs de seguridad

### 📊 Integraciones

- [APIs y Webhooks](./06-integraciones/apis-webhooks.md) - Exponer y consumir APIs
- [Integración con Servicios Cloud](./06-integraciones/cloud-services.md) - AWS, Azure, GCP
- [Integración con Plataformas Comerciales](./06-integraciones/plataformas-comerciales.md) - UiPath, ServiceNow
- [Bases de Datos](./06-integraciones/bases-datos.md) - PostgreSQL, MongoDB, etc.
- [Message Queues](./06-integraciones/message-queues.md) - Kafka, RabbitMQ

### 🎓 Guías por Rol

- [Guía para Desarrolladores](./07-por-rol/desarrolladores.md)
- [Guía para DevOps](./07-por-rol/devops.md)
- [Guía para Data Engineers](./07-por-rol/data-engineers.md)
- [Guía para Analistas de Negocio](./07-por-rol/analistas-negocio.md)
- [Guía para Arquitectos](./07-por-rol/arquitectos.md)

### 📖 Referencias Rápidas

- [Comandos Útiles](./08-referencias/comandos.md) - Cheat sheet de comandos
- [Estructura del Proyecto](./08-referencias/estructura.md) - Mapa del código
- [Variables de Entorno](./08-referencias/variables-entorno.md) - Configuración
- [FAQ](./08-referencias/faq.md) - Preguntas frecuentes
- [Glosario](./08-referencias/glosario.md) - Términos y conceptos

## 🗺️ Rutas de Aprendizaje

### Para Principiantes
1. Lee [Inicio Rápido](./01-inicio-rapido/README.md)
2. Configura tu entorno con [Instalación](./01-inicio-rapido/instalacion.md)
3. Crea tu primer workflow con [Primeros Pasos](./01-inicio-rapido/primeros-pasos.md)
4. Explora [Casos de Uso](./03-casos-uso/) según tu necesidad

### Para Usuarios Intermedios
1. Revisa los [Componentes Principales](./02-componentes/)
2. Implementa un [Caso de Uso Completo](./03-casos-uso/)
3. Configura [Monitoreo y Alertas](./04-operacion/monitoreo.md)
4. Aprende sobre [Seguridad](./05-seguridad/)

### Para Usuarios Avanzados
1. Optimiza con [Escalado y Performance](./04-operacion/escalado.md)
2. Integra [Plataformas Comerciales](./06-integraciones/plataformas-comerciales.md)
3. Implementa [MLOps Avanzado](./02-componentes/mlflow.md)
4. Personaliza según [Guía de Arquitectos](./07-por-rol/arquitectos.md)

## 🔗 Enlaces Rápidos

- [README Principal del Proyecto](../README.md)
- [Documentación Técnica](../docs/)
- [Código Fuente](../)

## 📝 Contribuir a la Documentación

Si encuentras errores o quieres mejorar la documentación:
1. Edita el archivo correspondiente
2. Asegúrate de seguir el formato Markdown
3. Incluye ejemplos prácticos cuando sea posible

## ❓ ¿Necesitas Ayuda?

- Revisa el [FAQ](./08-referencias/faq.md)
- Consulta [Troubleshooting](./04-operacion/troubleshooting.md)
- Busca en la [Documentación Técnica](../docs/)

---

**Última actualización**: 2024
**Versión del Proyecto**: Ver [README.md](../README.md)



