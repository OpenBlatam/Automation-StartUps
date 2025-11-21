#!/usr/bin/env python3
"""
Ejemplo de Uso de Templates de Troubleshooting.

Demuestra cómo usar los templates empáticos y resolutivos para guiar
a clientes a través de procesos de troubleshooting paso a paso.
"""
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from workflow.kestra.flows.lib.support_troubleshooting_templates import (
    get_troubleshooting_start_template,
    get_troubleshooting_step_template,
    get_troubleshooting_resolved_template,
    get_troubleshooting_escalation_template,
    TechnicalLevel,
    ProblemComplexity
)


def example_start_troubleshooting():
    """Ejemplo: Iniciar sesión de troubleshooting."""
    print("=" * 80)
    print("EJEMPLO 1: Iniciar Sesión de Troubleshooting")
    print("=" * 80)
    
    ticket_data = {
        "ticket_id": "TKT-20241215-TS001",
        "customer_name": "María González",
        "customer_email": "maria.gonzalez@example.com",
        "session_id": "TSESS-abc123"
    }
    
    detected_problem = {
        "title": "Error de conexión a la base de datos",
        "estimated_steps": 5,
        "estimated_time_minutes": 15
    }
    
    response = get_troubleshooting_start_template(
        ticket_data=ticket_data,
        problem_description="No puedo conectarme a la base de datos",
        detected_problem=detected_problem,
        technical_level=TechnicalLevel.INTERMEDIATE,
        complexity=ProblemComplexity.MODERATE,
        language="es"
    )
    
    print(f"\n📧 Asunto: {response['subject']}")
    print(f"\n🎯 Nivel técnico: {response['metadata']['technical_level']}")
    print(f"📊 Complejidad: {response['metadata']['complexity']}")
    print(f"⏱️  Tiempo estimado: {response['metadata']['estimated_time_minutes']} minutos")
    print(f"📝 Pasos estimados: {response['metadata']['estimated_steps']}")
    print(f"\n📄 Respuesta (primeros 600 caracteres):")
    print(response['text_body'][:600] + "...")
    print("\n" + "=" * 80)


def example_troubleshooting_step():
    """Ejemplo: Paso de troubleshooting."""
    print("\n" + "=" * 80)
    print("EJEMPLO 2: Paso de Troubleshooting")
    print("=" * 80)
    
    ticket_data = {
        "ticket_id": "TKT-20241215-TS001",
        "customer_name": "Juan Pérez",
        "customer_email": "juan.perez@example.com",
        "session_id": "TSESS-abc123"
    }
    
    response = get_troubleshooting_step_template(
        ticket_data=ticket_data,
        step_number=2,
        step_title="Verificar configuración de conexión",
        step_instructions="""
1. Abre el archivo de configuración de tu aplicación
2. Busca la sección de conexión a base de datos
3. Verifica que las credenciales sean correctas
4. Asegúrate de que el host y puerto sean los correctos
        """.strip(),
        step_verification="""
Para verificar que este paso funcionó:
- El archivo de configuración debe estar abierto
- Las credenciales deben ser visibles (aunque estén enmascaradas)
- El host debe ser el correcto según tu entorno
        """.strip(),
        warnings=[
            "No compartas tus credenciales con nadie",
            "Asegúrate de estar en el entorno correcto (desarrollo/producción)"
        ],
        resources=[
            {"title": "Documentación de configuración", "url": "https://docs.example.com/config"},
            {"title": "Guía de seguridad", "url": "https://docs.example.com/security"}
        ],
        language="es"
    )
    
    print(f"\n📧 Asunto: {response['subject']}")
    print(f"\n📝 Paso: {response['metadata']['step_number']}")
    print(f"\n📄 Respuesta (primeros 800 caracteres):")
    print(response['text_body'][:800] + "...")
    print("\n" + "=" * 80)


def example_troubleshooting_resolved():
    """Ejemplo: Problema resuelto."""
    print("\n" + "=" * 80)
    print("EJEMPLO 3: Problema Resuelto")
    print("=" * 80)
    
    ticket_data = {
        "ticket_id": "TKT-20241215-TS001",
        "customer_name": "Ana Martínez",
        "customer_email": "ana.martinez@example.com"
    }
    
    response = get_troubleshooting_resolved_template(
        ticket_data=ticket_data,
        resolution_summary="""
El problema era una configuración incorrecta en el archivo de conexión. 
Hemos actualizado las credenciales y ahora la conexión funciona correctamente.
        """.strip(),
        steps_completed=5,
        total_duration_minutes=12,
        language="es"
    )
    
    print(f"\n📧 Asunto: {response['subject']}")
    print(f"\n✅ Pasos completados: {response['metadata']['steps_completed']}")
    print(f"\n📄 Respuesta (primeros 600 caracteres):")
    print(response['text_body'][:600] + "...")
    print("\n" + "=" * 80)


def example_troubleshooting_escalation():
    """Ejemplo: Escalación a especialista."""
    print("\n" + "=" * 80)
    print("EJEMPLO 4: Escalación a Especialista")
    print("=" * 80)
    
    ticket_data = {
        "ticket_id": "TKT-20241215-TS001",
        "customer_name": "Carlos Rodríguez",
        "customer_email": "carlos.rodriguez@example.com"
    }
    
    response = get_troubleshooting_escalation_template(
        ticket_data=ticket_data,
        escalation_reason="""
Hemos intentado los pasos de troubleshooting estándar, pero el problema 
persiste y requiere acceso a configuración del servidor que solo un 
especialista puede modificar.
        """.strip(),
        steps_attempted=6,
        next_steps=[
            "Revisar logs del servidor para identificar el problema raíz",
            "Verificar configuración del servidor de base de datos",
            "Probar conexión desde diferentes ubicaciones",
            "Contactar al cliente con una solución específica"
        ],
        language="es"
    )
    
    print(f"\n📧 Asunto: {response['subject']}")
    print(f"\n📝 Pasos intentados: {response['metadata']['steps_attempted']}")
    print(f"\n📄 Respuesta (primeros 700 caracteres):")
    print(response['text_body'][:700] + "...")
    print("\n" + "=" * 80)


def example_multi_language():
    """Ejemplo: Soporte multi-idioma."""
    print("\n" + "=" * 80)
    print("EJEMPLO 5: Soporte Multi-idioma")
    print("=" * 80)
    
    ticket_data = {
        "ticket_id": "TKT-20241215-TS001",
        "customer_name": "John Smith",
        "customer_email": "john.smith@example.com",
        "session_id": "TSESS-abc123"
    }
    
    languages = ["es", "en"]
    
    for lang in languages:
        print(f"\n🌍 Idioma: {lang.upper()}")
        print("-" * 80)
        
        response = get_troubleshooting_start_template(
            ticket_data=ticket_data,
            problem_description="Connection error" if lang == "en" else "Error de conexión",
            detected_problem={
                "title": "Database connection error" if lang == "en" else "Error de conexión a base de datos",
                "estimated_steps": 5,
                "estimated_time_minutes": 15
            },
            technical_level=TechnicalLevel.INTERMEDIATE,
            complexity=ProblemComplexity.MODERATE,
            language=lang
        )
        
        print(f"Asunto: {response['subject']}")
        print(f"Respuesta (primeros 300 caracteres):")
        print(response['text_body'][:300] + "...")
    
    print("\n" + "=" * 80)


def example_technical_levels():
    """Ejemplo: Diferentes niveles técnicos."""
    print("\n" + "=" * 80)
    print("EJEMPLO 6: Diferentes Niveles Técnicos")
    print("=" * 80)
    
    ticket_data = {
        "ticket_id": "TKT-20241215-TS001",
        "customer_name": "Usuario",
        "customer_email": "usuario@example.com",
        "session_id": "TSESS-abc123"
    }
    
    levels = [
        (TechnicalLevel.BEGINNER, "Cliente sin conocimientos técnicos"),
        (TechnicalLevel.INTERMEDIATE, "Cliente con conocimientos básicos"),
        (TechnicalLevel.ADVANCED, "Cliente con conocimientos avanzados"),
        (TechnicalLevel.EXPERT, "Cliente experto técnico")
    ]
    
    for level, description in levels:
        print(f"\n👤 {description}")
        print("-" * 80)
        
        response = get_troubleshooting_start_template(
            ticket_data=ticket_data,
            problem_description="Error de conexión",
            detected_problem={
                "title": "Error de conexión",
                "estimated_steps": 5,
                "estimated_time_minutes": 15
            },
            technical_level=level,
            complexity=ProblemComplexity.MODERATE,
            language="es"
        )
        
        print(f"Nivel: {level.value}")
        print(f"Respuesta (primeros 200 caracteres):")
        print(response['text_body'][:200] + "...")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("EJEMPLOS: Templates de Troubleshooting")
    print("=" * 80)
    
    # Ejecutar todos los ejemplos
    example_start_troubleshooting()
    example_troubleshooting_step()
    example_troubleshooting_resolved()
    example_troubleshooting_escalation()
    example_multi_language()
    example_technical_levels()
    
    print("\n✅ Todos los ejemplos completados")
    print("\n💡 Para usar en producción:")
    print("   1. Integra con el sistema de troubleshooting existente")
    print("   2. Personaliza según el nivel técnico del cliente")
    print("   3. Adapta el tono según la complejidad del problema")
    print("   4. Envía emails automáticamente en cada paso")
    print("   5. Monitorea métricas de resolución")
    print("\n")



