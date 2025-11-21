# Automatización de Actualización de Precios en Catálogos

Sistema automatizado que extrae precios de competencia/mercado, analiza y ajusta precios propios, y publica actualizaciones del catálogo diariamente.

## 📋 Descripción

Este sistema ejecuta un flujo completo de automatización de precios:

1. **Extracción de Precios**: Obtiene precios de competencia desde múltiples fuentes (APIs, web scraping, bases de datos)
2. **Análisis y Ajuste**: Compara precios actuales vs mercado y calcula ajustes estratégicos
3. **Publicación**: Actualiza y publica el catálogo con los nuevos precios

## 🚀 Características

- ✅ Extracción desde múltiples fuentes (APIs, web scraping, bases de datos)
- ✅ Múltiples estrategias de precios (competitivo, líder, premium, dinámico)
- ✅ Validación y límites de cambio de precios
- ✅ Publicación a múltiples destinos (API, base de datos, archivo)
- ✅ Sistema de auditoría y logging
- ✅ Configuración flexible mediante YAML
- ✅ Rate limiting y manejo de errores

## 📁 Estructura de Archivos

```
data/airflow/
├── dags/
│   └── price_automation.py          # DAG principal
├── plugins/
│   ├── __init__.py
│   ├── price_config.py             # Configuración
│   ├── price_extraction.py         # Extracción de precios
│   ├── price_analyzer.py           # Análisis y ajuste
│   └── catalog_publisher.py        # Publicación
└── config/
    └── price_automation_config.yaml.example  # Ejemplo de configuración
```

## ⚙️ Configuración

### 1. Crear archivo de configuración

Copia el ejemplo y personaliza según tus necesidades:

```bash
cp data/airflow/config/price_automation_config.yaml.example \
   data/airflow/config/price_automation_config.yaml
```

### 2. Configurar variables de entorno (opcional)

```bash
export PRICE_AUTOMATION_CONFIG=/path/to/price_automation_config.yaml
export PRICING_STRATEGY=competitive
export CATALOG_API_URL=http://localhost:8000/api/catalog
export PUBLISH_API_URL=http://localhost:8000/api/catalog/update
```

### 3. Editar configuración YAML

Ajusta los siguientes aspectos:

#### Estrategia de Precios

```yaml
pricing_strategy: competitive  # competitive, price_leader, premium, dynamic, minimum, custom
```

- **competitive**: Mismo precio que promedio de competencia
- **price_leader**: Más barato que competencia (configurable)
- **premium**: Más caro que competencia (configurable)
- **dynamic**: Ajusta dinámicamente según posición relativa
- **minimum**: Siempre el precio más bajo
- **custom**: Lógica personalizada

#### Fuentes de Competencia

**APIs de competidores:**
```yaml
competitor_apis:
  - name: Competitor A
    url: https://api.competitor-a.com/v1/products
    headers:
      Authorization: Bearer YOUR_TOKEN
    parser_config:
      data_path: data.products
      name_field: name
      price_field: price
```

**Web Scraping:**
```yaml
scraping_sources:
  - name: Competitor Website
    url: https://www.competitor.com/products
    selectors:
      product_container: .product-item
      name: .product-name
      price: .product-price
```

#### Destino de Publicación

**API:**
```yaml
publish_target:
  type: api
  url: http://localhost:8000/api/catalog/update
  method: POST
  data_format: full_catalog  # full_catalog, products_only, price_updates_only
```

**Archivo:**
```yaml
publish_target:
  type: file
  path: /data/catalog_updated.json
  format: json  # json, csv, excel
  backup: true
```

**Múltiples destinos:**
```yaml
publish_target:
  type: multiple
  targets:
    - name: API Principal
      type: api
      url: http://localhost:8000/api/catalog/update
    - name: Backup File
      type: file
      path: /data/catalog_backup.json
```

## 🎯 Uso

### Ejecución Automática

El DAG se ejecuta automáticamente cada día a las 2:00 AM (configurable en `schedule_interval`).

### Ejecución Manual

Desde la UI de Airflow o mediante CLI:

```bash
airflow dags trigger price_automation_daily
```

### Seguimiento

- **Logs**: Revisa los logs en la UI de Airflow para cada tarea
- **Auditoría**: Los resultados se registran en `/tmp/price_automation_audit.log` (configurable)
- **XComs**: Los datos intermedios se almacenan en XComs para debugging

## 🔧 Estrategias de Precios

### Competitive (Competitivo)
Mantiene precios alineados con el promedio del mercado.

```yaml
pricing_strategy: competitive
```

### Price Leader (Líder de Precios)
Ofrece precios más bajos que la competencia.

```yaml
pricing_strategy: price_leader
price_leader_margin: 0.05  # 5% más barato
```

### Premium
Posiciona productos con precios superiores.

```yaml
pricing_strategy: premium
premium_margin: 0.10  # 10% más caro
```

### Dynamic (Dinámico)
Ajusta precios gradualmente según posición relativa.

```yaml
pricing_strategy: dynamic
dynamic_adjustment_factor: 0.1  # Ajuste del 10%
```

### Minimum (Mínimo)
Siempre ofrece el precio más bajo del mercado.

```yaml
pricing_strategy: minimum
```

## 📊 Límites y Validaciones

```yaml
max_price_change_percent: 20  # Cambio máximo permitido (20%)
min_price: 0                  # Precio mínimo
max_price: 999999             # Precio máximo
price_rounding: cent          # Redondeo a centavos
```

## 🛠️ Desarrollo y Extensión

### Agregar nueva fuente de datos

1. **API nueva:**
```python
# En price_extraction.py, agregar al método _extract_from_api
# o usar la configuración YAML
```

2. **Web scraping nuevo:**
```yaml
# Agregar a scraping_sources en config YAML
scraping_sources:
  - name: Nueva Fuente
    url: https://ejemplo.com
    selectors:
      product_container: .product
      name: .name
      price: .price
```

### Estrategia personalizada

Modifica `price_analyzer.py` en el método `_calculate_custom_price()`:

```python
def _calculate_custom_price(self, current_price, competitor_data, product_data):
    # Tu lógica personalizada aquí
    # Considera: costos, márgenes, demanda, etc.
    return new_price
```

### Integración con base de datos

Implementa los métodos en `price_extraction.py` y `catalog_publisher.py`:

```python
def _get_prices_from_db(self, db_config):
    # Conectar a BD y obtener precios
    # Retornar lista de dicts con product_id, product_name, current_price
    pass

def _publish_to_database(self, catalog, db_config):
    # Conectar a BD y actualizar precios
    # Retornar resultado de publicación
    pass
```

## 📝 Ejemplo de Flujo Completo

1. **Extracción** (2:00 AM):
   - Consulta APIs de 3 competidores
   - Realiza scraping de 2 sitios web
   - Obtiene 500 productos con precios de mercado

2. **Análisis** (2:15 AM):
   - Compara 300 productos propios vs mercado
   - Calcula ajustes según estrategia "competitive"
   - Valida límites de cambio (máx 20%)

3. **Publicación** (2:30 AM):
   - Aplica 250 ajustes de precio
   - Publica a API principal
   - Crea backup en archivo
   - Registra en log de auditoría

4. **Notificación** (2:35 AM):
   - Envía resumen con productos actualizados

## 🔍 Troubleshooting

### Error: "No se obtuvieron precios de competencia"

- Verifica que las fuentes estén configuradas correctamente
- Revisa conectividad de red
- Verifica tokens/autenticación de APIs
- Revisa selectores de scraping

### Error: "Validación fallida"

- Revisa límites de cambio de precio
- Verifica que los precios calculados sean válidos (> 0)
- Revisa logs para errores específicos

### Error: "Error publicando catálogo"

- Verifica URL y autenticación del destino
- Revisa formato de datos esperado
- Verifica permisos de escritura si es archivo

## 📚 Dependencias

Las siguientes dependencias ya están en `requirements.txt`:
- `requests` - Para APIs y HTTP
- `beautifulsoup4` - Para web scraping (agregar si falta)
- `pandas` - Para procesamiento de datos
- `pyyaml` - Para configuración YAML

Si falta alguna, instalar:
```bash
pip install beautifulsoup4 pyyaml
```

## 🔐 Seguridad

- **Tokens y credenciales**: Usa variables de entorno o Vault
- **Rate limiting**: Configura delays en scraping para evitar bloqueos
- **Validación**: Siempre valida datos antes de publicar
- **Backups**: Habilita backups antes de sobrescribir archivos

## 📈 Monitoreo

- Revisa logs de auditoría regularmente
- Monitorea métricas de cambios de precio
- Configura alertas para cambios extremos
- Revisa tasa de éxito de extracción

## 🤝 Contribuciones

Para extender el sistema:
1. Agrega nuevos métodos en los módulos existentes
2. Documenta cambios en configuración
3. Agrega tests si es posible
4. Actualiza esta documentación

## 📞 Soporte

Para problemas o preguntas:
- Revisa logs en `/tmp/price_automation_audit.log`
- Consulta logs de Airflow en la UI
- Verifica configuración YAML
- Revisa conectividad y permisos












