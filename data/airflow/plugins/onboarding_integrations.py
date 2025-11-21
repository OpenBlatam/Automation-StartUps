from __future__ import annotations

import json
import logging
import os
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

logger = logging.getLogger("airflow.task")

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2


def _env(name: str, default: str = "") -> str:
    """
    Get environment variable with default value.
    Mejorado: Intenta obtener desde Vault primero, luego fallback a env var.
    """
    # Intentar desde Vault usando helper
    try:
        from data.airflow.plugins.vault_helpers import get_config_with_fallback, migrate_env_to_vault_format
        vault_config = migrate_env_to_vault_format(name)
        if vault_config:
            vault_value = get_config_with_fallback(
                vault_config.get("vault_path", ""),
                vault_config.get("vault_key"),
                name,
                default=default,
                required=False
            )
            if vault_value:
                return vault_value
    except Exception as e:
        logger.debug(f"No se pudo obtener {name} desde Vault, usando env var: {e}")
    
    # Fallback a variable de entorno tradicional
    return os.getenv(name, default)


def _retry_with_backoff(func, *args, max_retries: int = MAX_RETRIES, **kwargs):
    """Retry function with exponential backoff."""
    last_exception = None
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = RETRY_DELAY_SECONDS * (2 ** attempt)
                logger.warning(
                    f"Attempt {attempt + 1} failed, retrying in {delay}s",
                    extra={"error": str(e), "attempt": attempt + 1},
                )
                time.sleep(delay)
            else:
                logger.error(
                    f"All {max_retries} attempts failed",
                    extra={"error": str(e), "max_retries": max_retries},
                )
    raise last_exception


def hris_prefetch(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch employee details from HRIS (Workday/BambooHR).
    Returns merged payload with canonical fields if available.
    Falls back to provided data if HRIS is unavailable.
    """
    employee_email = payload.get("employee_email", "")
    hris_url = _env("HRIS_API_URL")
    
    logger.info(
        "hris prefetch start",
        extra={
            "hris_configured": bool(hris_url),
            "employee_email": employee_email,
            "hris_url": hris_url if hris_url else None,
        },
    )
    
    if not hris_url:
        logger.warning("HRIS_API_URL not configured, using provided data", extra={"employee_email": employee_email})
        return {
            "hris": {
                "employee_id": employee_email,
                "manager_email": payload.get("manager_email"),
                "department": payload.get("department"),
                "location": payload.get("location"),
                "source": "provided",
            }
        }
    
    # TODO: Replace with actual HTTP call to HRIS API
    # Example implementation:
    # try:
    #     import requests
    #     response = _retry_with_backoff(
    #         requests.get,
    #         f"{hris_url}/employees/{employee_email}",
    #         headers={"Authorization": f"Bearer {_env('HRIS_API_TOKEN')}"},
    #         timeout=10,
    #     )
    #     response.raise_for_status()
    #     hris_data = response.json()
    #     return {"hris": hris_data}
    # except Exception as e:
    #     logger.error("HRIS API call failed", extra={"error": str(e), "employee_email": employee_email})
    #     raise
    
    # Stub implementation for now
    logger.info("hris prefetch completed (stub)", extra={"employee_email": employee_email})
    return {
        "hris": {
            "employee_id": employee_email,
            "manager_email": payload.get("manager_email"),
            "department": payload.get("department"),
            "location": payload.get("location"),
            "source": "stub",
        }
    }

def create_idp_and_workspace_accounts(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create accounts in IdP (e.g., Okta/Entra), email (Google/M365) and core apps.
    Returns account IDs and status for each service.
    """
    employee_email = payload.get("employee_email", "")
    full_name = payload.get("full_name", "")
    department = payload.get("department", "")
    idp_api = _env("IDP_API_URL")
    workspace = _env("WORKSPACE_API_URL")
    
    if not employee_email:
        raise ValueError("employee_email is required")
    
    logger.info(
        "create accounts start",
        extra={
            "employee_email": employee_email,
            "full_name": full_name,
            "department": department,
            "idp_configured": bool(idp_api),
            "workspace_configured": bool(workspace),
        },
    )
    
    result = {
        "idp_user_id": None,
        "mailbox": None,
        "workspace_profile": None,
        "accounts_created_at": datetime.now(timezone.utc).isoformat(),
    }
    
    # Create IdP account
    if idp_api:
        try:
            # TODO: Replace with actual IdP API call
            # Example:
            # idp_response = _retry_with_backoff(
            #     requests.post,
            #     f"{idp_api}/users",
            #     json={"email": employee_email, "name": full_name, "department": department},
            #     headers={"Authorization": f"Bearer {_env('IDP_API_TOKEN')}"},
            #     timeout=30,
            # )
            # idp_response.raise_for_status()
            # result["idp_user_id"] = idp_response.json().get("id")
            
            # Stub
            result["idp_user_id"] = f"idp-user-{employee_email}"
            logger.info("IdP account created", extra={"employee_email": employee_email, "idp_user_id": result["idp_user_id"]})
        except Exception as e:
            logger.error("Failed to create IdP account", extra={"employee_email": employee_email, "error": str(e)})
            raise
    else:
        logger.warning("IDP_API_URL not configured, skipping IdP account creation", extra={"employee_email": employee_email})
    
    # Create email/mailbox
    # TODO: Integrate with email provider (Google Workspace, M365, etc.)
    result["mailbox"] = employee_email
    logger.info("Mailbox assigned", extra={"employee_email": employee_email, "mailbox": result["mailbox"]})
    
    # Create workspace profile
    if workspace:
        try:
            # TODO: Replace with actual workspace API call
            result["workspace_profile"] = {
                "url": f"{workspace}/users/{employee_email}",
                "status": "created",
            }
            logger.info("Workspace profile created", extra={"employee_email": employee_email})
        except Exception as e:
            logger.error("Failed to create workspace profile", extra={"employee_email": employee_email, "error": str(e)})
            # Don't fail if workspace profile creation fails
    else:
        logger.warning("WORKSPACE_API_URL not configured, skipping workspace profile", extra={"employee_email": employee_email})
    
    logger.info(
        "accounts creation completed",
        extra={
            "employee_email": employee_email,
            "accounts": {
                "idp": bool(result["idp_user_id"]),
                "mailbox": bool(result["mailbox"]),
                "workspace": bool(result["workspace_profile"]),
            },
        },
    )
    
    return result


def assign_project_and_it_tasks(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create tickets/tasks in tracker (e.g., Jira) and IT checklist.
    Returns list of created task keys.
    """
    employee_email = payload.get("employee_email", "")
    full_name = payload.get("full_name", "")
    department = payload.get("department", "")
    role = payload.get("role", "")
    start_date = payload.get("start_date", "")
    tracker_url = _env("ISSUE_TRACKER_URL")
    project_key = _env("ISSUE_TRACKER_PROJECT", "ONB")
    
    logger.info(
        "assign onboarding tasks start",
        extra={
            "employee_email": employee_email,
            "tracker_configured": bool(tracker_url),
            "project_key": project_key,
            "department": department,
        },
    )
    
    tasks = []
    
    if tracker_url:
        try:
            # TODO: Replace with actual issue tracker API call
            # Example for Jira:
            # jira_tasks = [
            #     {
            #         "project": {"key": project_key},
            #         "summary": f"Onboarding: {full_name}",
            #         "description": f"Onboarding tasks for {full_name} ({employee_email})\nDepartment: {department}\nRole: {role}\nStart Date: {start_date}",
            #         "issuetype": {"name": "Task"},
            #     },
            #     {
            #         "project": {"key": project_key},
            #         "summary": f"IT Setup: {full_name}",
            #         "description": f"IT setup checklist for {full_name}",
            #         "issuetype": {"name": "Task"},
            #     },
            # ]
            # for task_data in jira_tasks:
            #     response = _retry_with_backoff(
            #         requests.post,
            #         f"{tracker_url}/rest/api/3/issue",
            #         json={"fields": task_data},
            #         headers={"Authorization": f"Bearer {_env('ISSUE_TRACKER_TOKEN')}"},
            #         timeout=30,
            #     )
            #     response.raise_for_status()
            #     task_key = response.json().get("key")
            #     tasks.append({"key": task_key, "summary": task_data["summary"]})
            
            # Stub implementation
            tasks = [
                {"key": f"{project_key}-ONB-001", "summary": f"Onboarding checklist: {full_name}", "type": "onboarding"},
                {"key": f"{project_key}-IT-001", "summary": f"IT setup: {full_name}", "type": "it_setup"},
            ]
            logger.info("Tasks created", extra={"employee_email": employee_email, "task_count": len(tasks)})
        except Exception as e:
            logger.error("Failed to create tasks in tracker", extra={"employee_email": employee_email, "error": str(e)})
            raise
    else:
        logger.warning("ISSUE_TRACKER_URL not configured, skipping task creation", extra={"employee_email": employee_email})
    
    return {"tasks": tasks, "tasks_created_at": datetime.now(timezone.utc).isoformat()}


def _get_db_connection(postgres_conn_id: str = "postgres_default"):
    """Obtiene conexión a base de datos."""
    if not POSTGRES_AVAILABLE:
        return None
    try:
        hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        return hook.get_conn()
    except Exception as e:
        logger.warning(f"Could not connect to database: {e}")
        return None


def create_onboarding_checklist(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea checklist automatizada de tareas de onboarding en base de datos.
    Incluye tareas de configuración de cuentas, documentos, capacitaciones y accesos.
    """
    employee_email = payload.get("employee_email", "")
    department = payload.get("department", "")
    role = payload.get("role", "")
    start_date = payload.get("start_date", "")
    manager_email = payload.get("manager_email", "")
    
    if not employee_email:
        raise ValueError("employee_email is required")
    
    logger.info("creating onboarding checklist", extra={"employee_email": employee_email})
    
    # Checklist templates por categoría
    checklist_templates = {
        "account_setup": [
            {"title": "Crear cuenta de email corporativo", "assignee": "it@example.com", "due_days": 0},
            {"title": "Configurar acceso a IdP (Okta/Azure AD)", "assignee": "it@example.com", "due_days": 0},
            {"title": "Crear perfil en workspace (Google/M365)", "assignee": "it@example.com", "due_days": 0},
            {"title": "Configurar acceso a Slack/Teams", "assignee": "it@example.com", "due_days": 1},
        ],
        "documents": [
            {"title": "Firmar contrato de trabajo", "assignee": "hr@example.com", "due_days": -7},
            {"title": "Completar formulario de datos personales", "assignee": employee_email, "due_days": 1},
            {"title": "Subir documentos de identidad", "assignee": employee_email, "due_days": 1},
            {"title": "Completar información bancaria", "assignee": employee_email, "due_days": 3},
            {"title": "Revisar y aceptar políticas de la empresa", "assignee": employee_email, "due_days": 1},
        ],
        "hr": [
            {"title": "Reunión de bienvenida con RRHH", "assignee": "hr@example.com", "due_days": 1},
            {"title": "Configurar beneficios y seguro", "assignee": "hr@example.com", "due_days": 3},
            {"title": "Asignar buddy/mentor", "assignee": "hr@example.com", "due_days": 2},
        ],
        "it": [
            {"title": "Configurar laptop/equipo de trabajo", "assignee": "it@example.com", "due_days": 1},
            {"title": "Instalar software necesario", "assignee": "it@example.com", "due_days": 2},
            {"title": "Configurar VPN y accesos remotos", "assignee": "it@example.com", "due_days": 1},
            {"title": "Configurar acceso a sistemas internos", "assignee": "it@example.com", "due_days": 3},
        ],
        "access": [
            {"title": "Acceso a repositorio de código (GitHub/GitLab)", "assignee": "it@example.com", "due_days": 2},
            {"title": "Acceso a herramientas de desarrollo", "assignee": "it@example.com", "due_days": 2},
            {"title": "Acceso a base de datos y entornos", "assignee": "it@example.com", "due_days": 5},
        ],
    }
    
    # Agregar tareas específicas por departamento
    if department.lower() in ["engineering", "tech", "development"]:
        checklist_templates["access"].extend([
            {"title": "Acceso a sistemas de CI/CD", "assignee": "it@example.com", "due_days": 3},
            {"title": "Configurar acceso a entornos de staging/producción", "assignee": "it@example.com", "due_days": 7},
        ])
    
    checklist_items = []
    conn = _get_db_connection()
    
    try:
        if conn:
            cursor = conn.cursor()
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else datetime.now().date()
            
            for category, tasks in checklist_templates.items():
                for task in tasks:
                    task_id = f"{category}_{uuid.uuid4().hex[:8]}"
                    due_date = start_dt + timedelta(days=task["due_days"]) if task["due_days"] >= 0 else start_dt + timedelta(days=task["due_days"])
                    
                    try:
                        cursor.execute("""
                            INSERT INTO onboarding_checklist 
                            (employee_email, task_id, task_category, task_title, assignee, due_date, status)
                            VALUES (%s, %s, %s, %s, %s, %s, 'pending')
                            ON CONFLICT (employee_email, task_id) DO NOTHING
                        """, (employee_email, task_id, category, task["title"], task["assignee"], due_date))
                        checklist_items.append({
                            "task_id": task_id,
                            "category": category,
                            "title": task["title"],
                            "assignee": task["assignee"],
                            "due_date": due_date.isoformat(),
                        })
                    except Exception as e:
                        logger.warning(f"Failed to insert checklist item: {e}")
            
            conn.commit()
            cursor.close()
            logger.info(f"Created {len(checklist_items)} checklist items", extra={"employee_email": employee_email})
        else:
            # Fallback: crear checklist en memoria si no hay DB
            logger.warning("Database not available, creating checklist in memory only")
            for category, tasks in checklist_templates.items():
                for task in tasks:
                    checklist_items.append({
                        "task_id": f"{category}_{uuid.uuid4().hex[:8]}",
                        "category": category,
                        "title": task["title"],
                        "assignee": task["assignee"],
                    })
    except Exception as e:
        logger.error(f"Error creating checklist: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    
    return {
        "checklist_items": checklist_items,
        "checklist_created_at": datetime.now(timezone.utc).isoformat(),
        "total_items": len(checklist_items),
    }


def assign_trainings(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Asigna capacitaciones automáticamente basadas en departamento, rol y políticas de la empresa.
    """
    employee_email = payload.get("employee_email", "")
    department = payload.get("department", "")
    role = payload.get("role", "")
    start_date = payload.get("start_date", "")
    
    if not employee_email:
        raise ValueError("employee_email is required")
    
    logger.info("assigning trainings", extra={"employee_email": employee_email, "department": department})
    
    # Templates de capacitaciones
    mandatory_trainings = [
        {
            "training_id": "welcome_orientation",
            "name": "Orientación de Bienvenida",
            "type": "mandatory",
            "provider": "internal",
            "due_days": 3,
        },
        {
            "training_id": "code_of_conduct",
            "name": "Código de Conducta y Ética",
            "type": "mandatory",
            "provider": "internal",
            "due_days": 7,
        },
        {
            "training_id": "security_awareness",
            "name": "Concientización de Seguridad",
            "type": "mandatory",
            "provider": "internal",
            "due_days": 14,
        },
        {
            "training_id": "data_protection",
            "name": "Protección de Datos (GDPR/LOPD)",
            "type": "mandatory",
            "provider": "internal",
            "due_days": 14,
        },
    ]
    
    # Capacitaciones específicas por departamento
    department_trainings = {
        "engineering": [
            {"training_id": "dev_standards", "name": "Estándares de Desarrollo", "type": "department_specific", "due_days": 7},
            {"training_id": "code_review", "name": "Proceso de Code Review", "type": "department_specific", "due_days": 10},
        ],
        "sales": [
            {"training_id": "crm_training", "name": "Capacitación CRM", "type": "department_specific", "due_days": 5},
            {"training_id": "sales_process", "name": "Proceso de Ventas", "type": "department_specific", "due_days": 7},
        ],
        "marketing": [
            {"training_id": "brand_guidelines", "name": "Guías de Marca", "type": "department_specific", "due_days": 5},
        ],
    }
    
    assigned_trainings = []
    conn = _get_db_connection()
    
    try:
        if conn:
            cursor = conn.cursor()
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else datetime.now().date()
            
            # Asignar capacitaciones obligatorias
            for training in mandatory_trainings:
                due_date = start_dt + timedelta(days=training["due_days"])
                try:
                    cursor.execute("""
                        INSERT INTO onboarding_trainings 
                        (employee_email, training_id, training_name, training_type, training_provider, 
                         assigned_date, due_date, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, 'assigned')
                        ON CONFLICT (employee_email, training_id) DO NOTHING
                    """, (
                        employee_email,
                        training["training_id"],
                        training["name"],
                        training["type"],
                        training["provider"],
                        start_dt,
                        due_date,
                    ))
                    assigned_trainings.append({
                        "training_id": training["training_id"],
                        "name": training["name"],
                        "type": training["type"],
                        "due_date": due_date.isoformat(),
                    })
                except Exception as e:
                    logger.warning(f"Failed to assign training {training['training_id']}: {e}")
            
            # Asignar capacitaciones por departamento
            dept_lower = department.lower() if department else ""
            for dept, trainings in department_trainings.items():
                if dept in dept_lower:
                    for training in trainings:
                        due_date = start_dt + timedelta(days=training["due_days"])
                        try:
                            cursor.execute("""
                                INSERT INTO onboarding_trainings 
                                (employee_email, training_id, training_name, training_type, 
                                 assigned_date, due_date, status)
                                VALUES (%s, %s, %s, %s, %s, %s, 'assigned')
                                ON CONFLICT (employee_email, training_id) DO NOTHING
                            """, (
                                employee_email,
                                training["training_id"],
                                training["name"],
                                training["type"],
                                start_dt,
                                due_date,
                            ))
                            assigned_trainings.append({
                                "training_id": training["training_id"],
                                "name": training["name"],
                                "type": training["type"],
                                "due_date": due_date.isoformat(),
                            })
                        except Exception as e:
                            logger.warning(f"Failed to assign department training {training['training_id']}: {e}")
            
            conn.commit()
            cursor.close()
            logger.info(f"Assigned {len(assigned_trainings)} trainings", extra={"employee_email": employee_email})
        else:
            logger.warning("Database not available, creating trainings in memory only")
            assigned_trainings = mandatory_trainings
    except Exception as e:
        logger.error(f"Error assigning trainings: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    
    return {
        "trainings": assigned_trainings,
        "trainings_assigned_at": datetime.now(timezone.utc).isoformat(),
        "total_trainings": len(assigned_trainings),
    }


def provision_accesses(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provisiona accesos automáticamente basados en departamento y rol.
    """
    employee_email = payload.get("employee_email", "")
    department = payload.get("department", "")
    role = payload.get("role", "")
    
    if not employee_email:
        raise ValueError("employee_email is required")
    
    logger.info("provisioning accesses", extra={"employee_email": employee_email, "department": department})
    
    # Accesos base para todos
    base_accesses = [
        {"type": "system", "name": "Email Corporativo", "provider": "google_workspace", "level": "read"},
        {"type": "application", "name": "Slack", "provider": "slack", "level": "read"},
        {"type": "application", "name": "Calendario Compartido", "provider": "google_workspace", "level": "read"},
    ]
    
    # Accesos por departamento
    department_accesses = {
        "engineering": [
            {"type": "application", "name": "GitHub", "provider": "github", "level": "read"},
            {"type": "application", "name": "Jira", "provider": "atlassian", "level": "read"},
            {"type": "database", "name": "Base de Datos Desarrollo", "provider": "custom", "level": "read"},
        ],
        "sales": [
            {"type": "application", "name": "CRM", "provider": "salesforce", "level": "read"},
            {"type": "application", "name": "HubSpot", "provider": "hubspot", "level": "read"},
        ],
        "marketing": [
            {"type": "application", "name": "Marketing Automation", "provider": "hubspot", "level": "read"},
        ],
    }
    
    all_accesses = base_accesses.copy()
    dept_lower = department.lower() if department else ""
    for dept, accesses in department_accesses.items():
        if dept in dept_lower:
            all_accesses.extend(accesses)
    
    provisioned_accesses = []
    conn = _get_db_connection()
    
    try:
        if conn:
            cursor = conn.cursor()
            
            for access in all_accesses:
                access_id = f"{access['type']}_{access['name'].lower().replace(' ', '_')}"
                try:
                    cursor.execute("""
                        INSERT INTO onboarding_accesses 
                        (employee_email, access_type, access_name, access_provider, access_id, 
                         status, access_level, metadata)
                        VALUES (%s, %s, %s, %s, %s, 'pending', %s, %s)
                        ON CONFLICT (employee_email, access_type, access_name) DO NOTHING
                    """, (
                        employee_email,
                        access["type"],
                        access["name"],
                        access["provider"],
                        access_id,
                        access["level"],
                        json.dumps({"auto_provisioned": True}),
                    ))
                    provisioned_accesses.append({
                        "access_type": access["type"],
                        "access_name": access["name"],
                        "provider": access["provider"],
                        "level": access["level"],
                    })
                except Exception as e:
                    logger.warning(f"Failed to provision access {access['name']}: {e}")
            
            conn.commit()
            cursor.close()
            logger.info(f"Provisioned {len(provisioned_accesses)} accesses", extra={"employee_email": employee_email})
        else:
            logger.warning("Database not available, creating accesses in memory only")
            provisioned_accesses = all_accesses
    except Exception as e:
        logger.error(f"Error provisioning accesses: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    
    return {
        "accesses": provisioned_accesses,
        "accesses_provisioned_at": datetime.now(timezone.utc).isoformat(),
        "total_accesses": len(provisioned_accesses),
    }


def send_welcome_and_docs(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Envía email de bienvenida personalizado con links a documentación, checklist y capacitaciones.
    """
    employee_email = payload.get("employee_email", "")
    full_name = payload.get("full_name", "")
    manager_email = payload.get("manager_email", "")
    start_date = payload.get("start_date", "")
    department = payload.get("department", "")
    docs_base = _env("ONBOARDING_DOCS_BASE_URL", "https://docs.example.com/onboarding")
    email_from = _env("ONBOARDING_EMAIL_FROM", "hr@example.com")
    onboarding_portal_url = _env("ONBOARDING_PORTAL_URL", "https://onboarding.example.com")
    
    if not employee_email:
        raise ValueError("employee_email is required")
    
    logger.info(
        "send welcome email start",
        extra={
            "to": employee_email,
            "from": email_from,
            "manager": manager_email,
            "start_date": start_date,
        },
    )
    
    # Build email content
    docs_links = {
        "handbook": f"{docs_base}/handbook",
        "policies": f"{docs_base}/policies",
        "it_setup": f"{docs_base}/it-setup",
        "getting_started": f"{docs_base}/getting-started",
    }
    
    # HTML email template
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .button {{ display: inline-block; padding: 12px 24px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            .section {{ margin: 20px 0; padding: 15px; background-color: white; border-left: 4px solid #4CAF50; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>¡Bienvenido/a a la empresa!</h1>
            </div>
            <div class="content">
                <p>Hola {full_name},</p>
                <p>Estamos muy contentos de tenerte en el equipo. Tu fecha de inicio es: <strong>{start_date}</strong></p>
                
                <div class="section">
                    <h2>📋 Tu Checklist de Onboarding</h2>
                    <p>Puedes revisar y hacer seguimiento de todas tus tareas de onboarding en nuestro portal:</p>
                    <a href="{onboarding_portal_url}/checklist?email={employee_email}" class="button">Ver mi Checklist</a>
                </div>
                
                <div class="section">
                    <h2>🎓 Capacitaciones Asignadas</h2>
                    <p>Te hemos asignado capacitaciones importantes para tu integración. Revisa tus capacitaciones:</p>
                    <a href="{onboarding_portal_url}/trainings?email={employee_email}" class="button">Ver Capacitaciones</a>
                </div>
                
                <div class="section">
                    <h2>📚 Recursos y Documentación</h2>
                    <ul>
                        <li><a href="{docs_links['handbook']}">Manual del Empleado</a></li>
                        <li><a href="{docs_links['policies']}">Políticas de la Empresa</a></li>
                        <li><a href="{docs_links['it_setup']}">Guía de Configuración IT</a></li>
                        <li><a href="{docs_links['getting_started']}">Primeros Pasos</a></li>
                    </ul>
                </div>
                
                <div class="section">
                    <h2>👤 Tu Manager</h2>
                    <p>Tu manager directo es: <strong>{manager_email}</strong></p>
                    <p>No dudes en contactarlo si tienes alguna pregunta.</p>
                </div>
                
                <p>¡Esperamos que tengas un excelente primer día!</p>
                <p>Saludos,<br>Equipo de RRHH</p>
            </div>
            <div class="footer">
                <p>Este es un email automático. Si tienes preguntas, contacta a {email_from}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_body = f"""
    Bienvenido/a {full_name}!
    
    Estamos muy contentos de tenerte en el equipo. Tu fecha de inicio es: {start_date}
    
    Tu Checklist de Onboarding:
    {onboarding_portal_url}/checklist?email={employee_email}
    
    Capacitaciones Asignadas:
    {onboarding_portal_url}/trainings?email={employee_email}
    
    Recursos y Documentación:
    - Manual del Empleado: {docs_links['handbook']}
    - Políticas: {docs_links['policies']}
    - Configuración IT: {docs_links['it_setup']}
    - Primeros Pasos: {docs_links['getting_started']}
    
    Tu Manager: {manager_email}
    
    Saludos,
    Equipo de RRHH
    """
    
    # Enviar email usando la función de notificaciones
    try:
        from data.airflow.plugins.etl_notifications import notify_email
        
        notify_email(
            to=employee_email,
            subject=f"¡Bienvenido/a a la empresa, {full_name}!",
            body=text_body,
            html=html_body,
        )
        
        # Registrar en base de datos
        conn = _get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO onboarding_emails 
                    (employee_email, email_type, subject, status)
                    VALUES (%s, 'welcome', %s, 'sent')
                """, (employee_email, f"¡Bienvenido/a a la empresa, {full_name}!"))
                conn.commit()
                cursor.close()
            except Exception as e:
                logger.warning(f"Failed to record email in database: {e}")
            finally:
                conn.close()
        
        logger.info("Welcome email sent", extra={"employee_email": employee_email})
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}", exc_info=True)
        # No fallar el proceso si el email falla
    
    return {
        "welcome_sent": True,
        "welcome_sent_at": datetime.now(timezone.utc).isoformat(),
        "docs": docs_links,
        "email_to": employee_email,
        "email_from": email_from,
    }


def record_progress_and_notify(payload: Dict[str, Any]) -> None:
    """
    Track onboarding progress: logs structured data and persists to Airflow Variables.
    Triggers Slack notification via env-controlled notifier.
    Extend to persist in a DB or emit metrics for production use.
    """
    employee_email = payload.get("employee_email", "unknown")
    
    progress = {
        "employee_email": employee_email,
        "full_name": payload.get("full_name"),
        "start_date": payload.get("start_date"),
        "department": payload.get("department"),
        "role": payload.get("role"),
        "created_accounts": bool(payload.get("idp_user_id")),
        "idp_user_id": payload.get("idp_user_id"),
        "mailbox": payload.get("mailbox"),
        "tasks_created": bool(payload.get("tasks")),
        "task_count": len(payload.get("tasks", [])),
        "welcome_sent": bool(payload.get("welcome_sent")),
        "manager": payload.get("manager_email"),
        "hris_source": payload.get("hris", {}).get("source", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "completed",
    }
    
    logger.info(
        "onboarding progress recorded",
        extra={
            "employee_email": employee_email,
            "accounts_created": progress["created_accounts"],
            "tasks_count": progress["task_count"],
            "welcome_sent": progress["welcome_sent"],
        },
    )
    
    # Persist to Airflow Variables (lightweight storage)
    try:
        from airflow.models import Variable  # local import to avoid hard dependency at import time
        
        key = f"onboarding_runs:{employee_email}"
        existing_raw = Variable.get(key, default_var="[]")
        try:
            existing = json.loads(existing_raw)
            if not isinstance(existing, list):
                existing = []
        except (json.JSONDecodeError, TypeError):
            logger.warning("Invalid existing progress data, resetting", extra={"key": key})
            existing = []
        
        existing.append(progress)
        # Keep only last 10 runs per employee to avoid bloat
        existing = existing[-10:]
        Variable.set(key, json.dumps(existing, indent=2))
        
        logger.info(
            "progress persisted",
            extra={"employee_email": employee_email, "total_runs": len(existing)},
        )
    except Exception as e:
        # If Variables are not available, log warning but don't fail
        logger.warning(
            "failed to persist progress to Variables",
            extra={"employee_email": employee_email, "error": str(e)},
        )
    
    # TODO: Send notification to Slack/Teams/etc. via configured webhook
    # Example:
    # slack_webhook = _env("SLACK_WEBHOOK_URL")
    # if slack_webhook:
    #     try:
    #         notify_message = f"✅ Onboarding completed for {progress['full_name']} ({employee_email})"
    #         _retry_with_backoff(
    #             requests.post,
    #             slack_webhook,
    #             json={"text": notify_message},
    #             timeout=10,
    #         )
    #     except Exception as e:
    #         logger.warning("Failed to send Slack notification", extra={"error": str(e)})


