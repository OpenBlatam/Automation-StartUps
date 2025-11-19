#!/bin/bash
# 🎨 Generador de Template para Nuevos DAGs

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🎨 Generador de Template para Nuevo DAG${NC}\n"

# Solicitar información
read -p "Nombre del DAG (snake_case): " DAG_NAME
read -p "Descripción del DAG: " DAG_DESCRIPTION
read -p "Área (sales_marketing/hr_talent/finance_billing/product_ecommerce/customer_success/data_analytics/operations/integrations): " AREA
read -p "Subcarpeta (o Enter para raíz del área): " SUBFOLDER
read -p "Schedule (@daily/@weekly/@monthly/@hourly o cron): " SCHEDULE
read -p "Tags (separados por comas): " TAGS
read -p "Owner (default: data-team): " OWNER
OWNER=${OWNER:-data-team}

# Validar área
VALID_AREAS=("sales_marketing" "hr_talent" "finance_billing" "product_ecommerce" "customer_success" "data_analytics" "operations" "integrations")
if [[ ! " ${VALID_AREAS[@]} " =~ " ${AREA} " ]]; then
    echo -e "${RED}❌ Área inválida${NC}"
    exit 1
fi

# Determinar ruta
if [ -z "$SUBFOLDER" ]; then
    TARGET_DIR="$AREA"
else
    TARGET_DIR="$AREA/$SUBFOLDER"
    mkdir -p "$TARGET_DIR"
fi

# Crear archivo
FILE_PATH="$TARGET_DIR/${DAG_NAME}.py"

if [ -f "$FILE_PATH" ]; then
    echo -e "${YELLOW}⚠️  El archivo ya existe. ¿Sobrescribir? (y/n)${NC}"
    read -p "> " OVERWRITE
    if [ "$OVERWRITE" != "y" ]; then
        echo "Cancelado."
        exit 0
    fi
fi

# Generar template
cat > "$FILE_PATH" << EOF
#!/usr/bin/env python3
"""
${DAG_DESCRIPTION}

Este DAG ${DAG_DESCRIPTION,,}
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, List, Optional
import logging

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context

logger = logging.getLogger(__name__)

default_args = {
    'owner': '${OWNER}',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

@dag(
    dag_id='${DAG_NAME}',
    default_args=default_args,
    description='${DAG_DESCRIPTION}',
    schedule_interval='${SCHEDULE}',
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=[${TAGS//,/\', \'}],
    params={
        # Agregar parámetros aquí si es necesario
    },
)
def ${DAG_NAME}():
    """
    ${DAG_DESCRIPTION}
    """
    
    @task(task_id='extract')
    def extract() -> Dict[str, Any]:
        """
        Extrae datos de la fuente.
        
        Returns:
            Dict con los datos extraídos
        """
        logger.info("Iniciando extracción de datos")
        # TODO: Implementar extracción
        return {}
    
    @task(task_id='transform')
    def transform(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforma los datos.
        
        Args:
            data: Datos extraídos
            
        Returns:
            Dict con los datos transformados
        """
        logger.info("Iniciando transformación de datos")
        # TODO: Implementar transformación
        return data
    
    @task(task_id='load')
    def load(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Carga los datos al destino.
        
        Args:
            data: Datos transformados
            
        Returns:
            Dict con resultado de la carga
        """
        logger.info("Iniciando carga de datos")
        # TODO: Implementar carga
        return {"status": "success", "records_processed": 0}
    
    # Definir flujo de tareas
    extracted_data = extract()
    transformed_data = transform(extracted_data)
    result = load(transformed_data)
    
    return result

# Instanciar el DAG
${DAG_NAME}()
EOF

echo -e "\n${GREEN}✅ DAG creado en: ${FILE_PATH}${NC}"
echo -e "\n${YELLOW}📝 Próximos pasos:${NC}"
echo "  1. Implementar las funciones extract(), transform(), load()"
echo "  2. Agregar documentación adicional si es necesario"
echo "  3. Configurar conexiones y variables de Airflow"
echo "  4. Probar en ambiente de desarrollo"
echo "  5. Agregar a QUICK_REFERENCE.md si es común"

