# MLflow Configuration Changelog

## v2.0 (2025-01)

### ✨ Nuevas Características
- ✅ Configuración production-ready completa
- ✅ Soporte multi-cloud (AWS S3, Azure ADLS)
- ✅ Auto-scaling con HPA configurado
- ✅ High Availability con Pod Disruption Budget
- ✅ ServiceMonitor para Prometheus
- ✅ Network Policies configurables
- ✅ Rate limiting en Ingress
- ✅ Security headers y TLS
- ✅ Connection pooling optimizado
- ✅ Data retention y cleanup automático
- ✅ Integraciones con Airflow, KServe, Kubeflow

### 🔧 Mejoras
- 📈 Recursos optimizados para producción
- 🔒 Security contexts y ServiceAccount con IRSA/Workload Identity
- 📊 Logging estructurado JSON para Loki
- 🚀 Health checks mejorados (liveness + readiness)
- 🔐 TLS con cert-manager
- 📝 Documentación inline mejorada

### 🐛 Fixes
- Corregida configuración de variables de entorno
- Mejorada configuración de timeouts para uploads grandes
- Ajustada configuración de connection pool

### 📚 Documentación
- Agregado README completo con ejemplos
- Creado values-dev.yaml para desarrollo
- Agregadas validaciones y checks pre-deployment

## v1.0 (2024-12)
- Configuración inicial básica
- PostgreSQL backend
- S3 artifact store
- Ingress básico

