# Inicio Rápido - Automatización de Precios

## 🚀 Configuración en 3 Pasos

### 1. Crear archivo de configuración

```bash
cd /Users/adan/IA/data/airflow
cp config/price_automation_config.yaml.example config/price_automation_config.yaml
```

### 2. Editar configuración

Abre `config/price_automation_config.yaml` y configura:

- **Estrategia de precios**: `pricing_strategy: competitive`
- **Fuente de catálogo**: URL de tu API o ruta de archivo
- **APIs de competidores**: Agrega tus fuentes de datos
- **Destino de publicación**: Dónde publicar los precios actualizados

### 3. Instalar dependencias (si falta)

```bash
pip install beautifulsoup4 lxml
```

## ✅ Verificar

El DAG `price_automation_daily` debería aparecer en Airflow UI.

**Ejecución**: Diariamente a las 2:00 AM (configurable en el DAG)

## 📝 Ejemplo de Configuración Mínima

```yaml
pricing_strategy: competitive

catalog_source:
  type: api
  url: http://localhost:8000/api/catalog

competitor_apis:
  - name: Competitor API
    url: https://api.competitor.com/products
    headers:
      Authorization: Bearer YOUR_TOKEN
    parser_config:
      data_path: products
      name_field: name
      price_field: price

publish_target:
  type: api
  url: http://localhost:8000/api/catalog/update
  method: POST
```

## 🔍 Verificar Logs

```bash
# Logs de Airflow UI o
tail -f /tmp/price_automation_audit.log
```

## 📚 Documentación Completa

Ver `README_PRICE_AUTOMATION.md` para más detalles.












