# Scripts y Utilidades

Esta carpeta contiene scripts de utilidad para operaciones comunes y automatizaciones de la plataforma.

## Estructura

```
scripts/
├── onboarding_runs_cli.py      # CLI para consultar progreso de onboarding en Airflow (legacy)
├── onboarding_manager.py        # CLI completo para gestión de onboarding en Kestra
└── onboarding_maintenance.py   # Scripts de mantenimiento (limpieza, integridad, archivado)
```

## Scripts Disponibles

### onboarding_manager.py

CLI completo de Python para gestionar onboarding de empleados en Kestra.

**Instalación**:
```bash
pip install psycopg requests
```

**Uso**:

#### Ver estado de un empleado
```bash
python scripts/onboarding_manager.py status \
  --email empleado@empresa.com \
  --db-url jdbc:postgresql://db:5432/onboarding \
  --db-user onboarding_user \
  --db-password your_password
```

#### Listar onboarding recientes
```bash
python scripts/onboarding_manager.py list \
  --limit 20 \
  --db-url jdbc:postgresql://db:5432/onboarding \
  --db-user onboarding_user \
  --db-password your_password
```

#### Ver estadísticas
```bash
python scripts/onboarding_manager.py stats \
  --db-url jdbc:postgresql://db:5432/onboarding \
  --db-user onboarding_user \
  --db-password your_password
```

#### Disparar onboarding manualmente
```bash
python scripts/onboarding_manager.py trigger \
  --kestra-url https://kestra.example.com \
  --kestra-token YOUR_TOKEN \
  --payload-file payload.json
```

**Ejemplo de payload.json**:
```json
{
  "employee_email": "nuevo@empresa.com",
  "full_name": "Nuevo Empleado",
  "start_date": "2025-02-01",
  "manager_email": "manager@empresa.com",
  "department": "Engineering",
  "role": "Developer"
}
```

### onboarding_maintenance.py

Scripts de mantenimiento para el sistema de onboarding.

**Uso**:

#### Limpiar datos antiguos
```bash
python scripts/onboarding_maintenance.py cleanup \
  --db-url jdbc:postgresql://db:5432/onboarding \
  --db-user onboarding_user \
  --db-password your_password \
  --retention-days 365
```

#### Verificar integridad de datos
```bash
python scripts/onboarding_maintenance.py integrity \
  --db-url jdbc:postgresql://db:5432/onboarding \
  --db-user onboarding_user \
  --db-password your_password
```

#### Archivar onboarding completados
```bash
python scripts/onboarding_maintenance.py archive \
  --db-url jdbc:postgresql://db:5432/onboarding \
  --db-user onboarding_user \
  --db-password your_password \
  --archive-days 90
```

### onboarding_runs_cli.py (Legacy)

CLI de Python para consultar el progreso de onboarding desde Airflow Variables (legacy, usar onboarding_manager.py para Kestra).

## Desarrollo de Nuevos Scripts

### Convenciones

1. **Shebang**: Usa `#!/usr/bin/env python3` para scripts ejecutables
2. **Type hints**: Usa type hints para mejor mantenibilidad
3. **Argumentos**: Usa `argparse` para CLI
4. **Logging**: Usa `logging` en lugar de `print`
5. **Manejo de errores**: Maneja excepciones apropiadamente
6. **Permisos**: Ejecutables deben tener `chmod +x`

### Plantilla de Script

```python
#!/usr/bin/env python3
"""Descripción breve del script."""

import argparse
import logging
import sys
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description="Descripción del script")
    # Agregar argumentos aquí
    
    args = parser.parse_args()
    
    try:
        # Lógica del script
        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
```

## Testing

Los scripts pueden tener tests asociados. Ver `workflow/kestra/flows/tests/` para ejemplos.

## Integración con CI/CD

Los scripts de mantenimiento pueden integrarse en pipelines:

```yaml
# Ejemplo GitHub Actions
- name: Cleanup old onboarding data
  run: |
    python scripts/onboarding_maintenance.py cleanup \
      --db-url ${{ secrets.DB_URL }} \
      --db-user ${{ secrets.DB_USER }} \
      --db-password ${{ secrets.DB_PASSWORD }} \
      --retention-days 365
```

## Seguridad

⚠️ **IMPORTANTE**: Nunca hardcodees credenciales en scripts. Usa:
- Variables de entorno
- Secrets de Kubernetes
- Secret managers (Vault, AWS Secrets Manager, etc.)

---

**Última actualización**: 2025-01-20
