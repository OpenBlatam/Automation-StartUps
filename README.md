# Sistema de Control de Inventario Inteligente

## Descripción

Sistema completo de control de inventario con alertas automáticas de bajo stock, previsión de demanda y reposición inteligente. Incluye KPIs avanzados y herramientas de análisis para optimizar la gestión del inventario.

## Características Principales

### 🚨 Sistema de Alertas Automáticas
- **Alertas de bajo stock**: Notificaciones automáticas cuando el inventario alcanza niveles críticos
- **Alertas de stock agotado**: Notificaciones inmediatas cuando un producto se queda sin stock
- **Alertas de punto de reorden**: Avisos cuando se alcanza el punto de reposición configurado
- **Notificaciones por email**: Sistema de notificaciones automáticas por correo electrónico
- **Severidad configurable**: Alertas clasificadas por niveles de urgencia (crítico, alto, medio, bajo)

### 📊 Previsión de Demanda Inteligente
- **Múltiples algoritmos**: Media móvil, suavizado exponencial y regresión lineal
- **Selección automática**: El sistema elige el mejor algoritmo basado en datos históricos
- **Predicciones precisas**: Análisis de tendencias y patrones de venta
- **Métricas de precisión**: Evaluación de la exactitud de las predicciones
- **Análisis de variabilidad**: Cálculo de factores de seguridad basados en la variabilidad de demanda

### 🛒 Reposición Inteligente
- **Puntos de reorden dinámicos**: Cálculo automático basado en demanda esperada y variabilidad
- **Cantidades óptimas**: Recomendaciones de cantidad de pedido usando modelos EOQ modificados
- **Análisis de urgencia**: Clasificación automática de la urgencia de reposición
- **Costos estimados**: Cálculo automático del costo estimado de las recomendaciones
- **Integración con proveedores**: Consideración de tiempos de entrega y disponibilidad

### 📈 KPIs y Métricas Avanzadas
- **Métricas de inventario**: Rotación, precisión, valor total, productos con stock bajo
- **Métricas de ventas**: Ingresos, crecimiento, productos más vendidos, valor promedio de pedido
- **Métricas financieras**: Margen de beneficio, ROI del inventario, costo de almacenamiento
- **Métricas operacionales**: Tiempo de respuesta a alertas, eficiencia de reposición, precisión de predicciones
- **Tendencias temporales**: Análisis de evolución de KPIs en el tiempo

### 🎯 Dashboard Interactivo
- **Vista general**: Resumen ejecutivo con métricas clave
- **Gráficos dinámicos**: Visualizaciones interactivas de tendencias y patrones
- **Alertas en tiempo real**: Notificaciones inmediatas de situaciones críticas
- **Acciones rápidas**: Botones para operaciones comunes
- **Interfaz responsiva**: Diseño adaptable a diferentes dispositivos

## Tecnologías Utilizadas

### Backend
- **Flask**: Framework web ligero y flexible
- **SQLAlchemy**: ORM para manejo de base de datos
- **Flask-Migrate**: Migraciones de base de datos
- **Flask-Mail**: Sistema de notificaciones por email
- **APScheduler**: Programación de tareas automáticas

### Frontend
- **Bootstrap 5**: Framework CSS para diseño responsivo
- **Chart.js**: Gráficos interactivos y visualizaciones
- **Font Awesome**: Iconografía moderna
- **JavaScript ES6**: Funcionalidades interactivas avanzadas

### Análisis de Datos
- **Pandas**: Manipulación y análisis de datos
- **NumPy**: Cálculos numéricos avanzados
- **Scikit-learn**: Algoritmos de machine learning
- **Matplotlib/Seaborn**: Visualización de datos

### Base de Datos
- **SQLite**: Base de datos ligera para desarrollo
- **PostgreSQL/MySQL**: Soporte para bases de datos de producción

## Instalación y Configuración

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (para clonar el repositorio)

### Instalación

1. **Clonar el repositorio**:
```bash
git clone <repository-url>
cd inventory-management-system
```

2. **Crear entorno virtual**:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Inicializar base de datos**:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. **Ejecutar la aplicación**:
```bash
python app.py
```

### Configuración de Email

Para habilitar las notificaciones por email, configura las siguientes variables en tu archivo `.env`:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-contraseña-de-aplicacion
ADMIN_EMAIL=admin@tuempresa.com
```

## Uso del Sistema

### Gestión de Productos
1. **Agregar productos**: Define productos con SKU, precios, niveles de stock y proveedores
2. **Configurar niveles**: Establece stock mínimo, máximo y punto de reorden
3. **Asignar proveedores**: Vincula productos con proveedores para reposición automática

### Control de Inventario
1. **Registrar movimientos**: Entradas, salidas y ajustes de inventario
2. **Monitorear stock**: Visualización en tiempo real del estado del inventario
3. **Alertas automáticas**: Notificaciones inmediatas de situaciones críticas

### Análisis y Predicciones
1. **Previsión de demanda**: Predicciones automáticas basadas en datos históricos
2. **Recomendaciones**: Sugerencias inteligentes de reposición
3. **KPIs**: Métricas detalladas de rendimiento del inventario

### Dashboard y Reportes
1. **Vista general**: Resumen ejecutivo con métricas clave
2. **Tendencias**: Análisis de evolución temporal
3. **Alertas**: Gestión centralizada de notificaciones

## API REST

El sistema incluye una API REST completa para integración con otros sistemas:

### Endpoints Principales

- `GET /api/products` - Listar productos
- `POST /api/products` - Crear producto
- `GET /api/inventory` - Estado del inventario
- `POST /api/inventory/movements` - Registrar movimiento
- `GET /api/alerts` - Alertas activas
- `POST /api/alerts/check` - Verificar alertas manualmente
- `GET /api/forecasts/{product_id}` - Predicción de demanda
- `GET /api/replenishment/recommendations` - Recomendaciones de reposición
- `GET /api/kpis` - KPIs del sistema

### Ejemplo de Uso de la API

```python
import requests

# Obtener productos
response = requests.get('http://localhost:5000/api/products')
products = response.json()

# Registrar una venta
sale_data = {
    'product_id': 1,
    'quantity_sold': 5,
    'sale_date': '2024-01-15T10:30:00',
    'unit_price': 25.99
}
response = requests.post('http://localhost:5000/api/sales', json=sale_data)
```

## Herramientas Recomendadas

### Para Desarrollo
- **Visual Studio Code**: Editor con excelente soporte para Python
- **Postman**: Cliente API para testing
- **DBeaver**: Cliente de base de datos universal

### Para Producción
- **Gunicorn**: Servidor WSGI para producción
- **Nginx**: Servidor web y proxy reverso
- **Redis**: Cache y cola de tareas
- **Celery**: Procesamiento de tareas asíncronas

### Para Monitoreo
- **Prometheus**: Métricas y monitoreo
- **Grafana**: Dashboards de monitoreo
- **ELK Stack**: Logs centralizados

## Mejores Prácticas

### Seguridad
- Usar HTTPS en producción
- Implementar autenticación y autorización
- Validar todas las entradas de usuario
- Mantener dependencias actualizadas

### Rendimiento
- Implementar cache para consultas frecuentes
- Optimizar consultas de base de datos
- Usar índices apropiados
- Monitorear métricas de rendimiento

### Mantenimiento
- Realizar backups regulares
- Monitorear logs del sistema
- Actualizar dependencias periódicamente
- Documentar cambios y configuraciones

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Para soporte técnico o preguntas sobre el sistema:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo
- Revisar la documentación técnica

## Roadmap

### Próximas Características
- [ ] Integración con sistemas ERP
- [ ] Análisis predictivo avanzado con IA
- [ ] App móvil nativa
- [ ] Integración con códigos de barras/QR
- [ ] Sistema de auditoría completo
- [ ] Reportes personalizables
- [ ] Integración con marketplaces
- [ ] Análisis de rentabilidad por producto

---

**Desarrollado con ❤️ para optimizar la gestión de inventarios**