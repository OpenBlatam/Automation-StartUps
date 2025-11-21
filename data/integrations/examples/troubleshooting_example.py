"""
Ejemplo de uso del Sistema de Troubleshooting Automatizado

Este script demuestra cómo usar el agente de troubleshooting
para guiar a un cliente paso a paso en la resolución de problemas.
"""

import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from support_troubleshooting_agent import TroubleshootingAgent


def ejemplo_basico():
    """Ejemplo básico de uso del agente"""
    print("=" * 60)
    print("Ejemplo 1: Uso Básico del Agente de Troubleshooting")
    print("=" * 60)
    
    # Inicializar agente
    agent = TroubleshootingAgent()
    
    # Simular un problema del cliente
    problem_description = "No puedo instalar el software en mi computadora"
    customer_email = "cliente@example.com"
    customer_name = "Juan Pérez"
    
    print(f"\n📝 Problema reportado: {problem_description}")
    print(f"👤 Cliente: {customer_name} ({customer_email})")
    
    # Iniciar sesión de troubleshooting
    session = agent.start_troubleshooting(
        problem_description=problem_description,
        customer_email=customer_email,
        customer_name=customer_name
    )
    
    print(f"\n✅ Sesión iniciada: {session.session_id}")
    print(f"🔍 Problema detectado: {session.detected_problem.problem_title if session.detected_problem else 'No detectado'}")
    print(f"📊 Estado: {session.status.value}")
    
    # Obtener primer paso
    first_step = agent.get_current_step(session.session_id)
    
    if first_step and first_step.get("status") != "no_problem_detected":
        print("\n" + "=" * 60)
        print("📋 PRIMER PASO PARA EL CLIENTE:")
        print("=" * 60)
        print(agent.format_step_response(first_step))
    
    return session, agent


def ejemplo_paso_a_paso(session, agent):
    """Ejemplo de completar pasos uno por uno"""
    print("\n" + "=" * 60)
    print("Ejemplo 2: Completar Pasos Paso a Paso")
    print("=" * 60)
    
    # Simular completar pasos
    max_steps = 3  # Limitar para el ejemplo
    
    for i in range(max_steps):
        current_step_info = agent.get_current_step(session.session_id)
        
        if current_step_info.get("status") in ["completed", "no_problem_detected"]:
            print(f"\n✅ {current_step_info.get('message', 'Proceso completado')}")
            break
        
        step_number = current_step_info.get("step_number", 0)
        print(f"\n📝 Paso {step_number}: {current_step_info.get('title', 'N/A')}")
        
        # Simular que el cliente completa el paso exitosamente
        # En un caso real, esto vendría de la interacción del cliente
        success = True  # Simular éxito
        notes = f"Paso {step_number} completado correctamente"
        
        result = agent.complete_step(
            session_id=session.session_id,
            success=success,
            notes=notes
        )
        
        print(f"   Resultado: {'✅ Éxito' if success else '❌ Fallo'}")
        print(f"   Estado: {result.get('status', 'unknown')}")
        
        if result.get("status") == "resolved":
            print("\n🎉 ¡Problema resuelto!")
            break
        elif result.get("suggest_escalation"):
            print("\n⚠️ Se recomienda escalar el ticket")
            break


def ejemplo_escalacion(session, agent):
    """Ejemplo de escalación cuando no se resuelve"""
    print("\n" + "=" * 60)
    print("Ejemplo 3: Escalación de Ticket")
    print("=" * 60)
    
    # Simular que varios pasos fallan
    for i in range(2):
        current_step_info = agent.get_current_step(session.session_id)
        
        if current_step_info.get("status") in ["completed", "resolved"]:
            break
        
        # Simular fallo
        result = agent.complete_step(
            session_id=session.session_id,
            success=False,
            notes="No pude completar este paso"
        )
        
        if result.get("suggest_escalation"):
            print("\n⚠️ Múltiples pasos fallaron. Escalando ticket...")
            
            escalation_info = agent.escalate_ticket(
                session_id=session.session_id,
                reason="Múltiples pasos fallidos después de seguir las instrucciones"
            )
            
            print("\n📤 Información de escalación:")
            print(f"   Ticket ID: {escalation_info.get('ticket_id', 'N/A')}")
            print(f"   Cliente: {escalation_info.get('customer_email')}")
            print(f"   Pasos intentados: {escalation_info.get('attempted_steps', 0)}")
            print(f"   Pasos fallidos: {escalation_info.get('failed_steps', 0)}")
            print(f"   Razón: {escalation_info.get('reason', 'N/A')}")
            break


def ejemplo_resumen(session, agent):
    """Ejemplo de obtener resumen de sesión"""
    print("\n" + "=" * 60)
    print("Ejemplo 4: Resumen de Sesión")
    print("=" * 60)
    
    summary = agent.get_session_summary(session.session_id)
    
    if summary:
        print(f"\n📊 Resumen de la sesión:")
        print(f"   Session ID: {summary.get('session_id')}")
        print(f"   Ticket ID: {summary.get('ticket_id', 'N/A')}")
        print(f"   Estado: {summary.get('status')}")
        print(f"   Problema: {summary.get('problem_detected', 'N/A')}")
        print(f"   Paso actual: {summary.get('current_step')} de {summary.get('total_steps')}")
        print(f"   Pasos intentados: {summary.get('attempted_steps', 0)}")
        print(f"   Pasos exitosos: {summary.get('successful_steps', 0)}")
        print(f"   Iniciado: {summary.get('started_at')}")
        if summary.get('resolved_at'):
            print(f"   Resuelto: {summary.get('resolved_at')}")


def ejemplo_problema_no_detectado():
    """Ejemplo cuando no se detecta un problema conocido"""
    print("\n" + "=" * 60)
    print("Ejemplo 5: Problema No Detectado")
    print("=" * 60)
    
    agent = TroubleshootingAgent()
    
    # Problema que no está en la base de conocimiento
    problem_description = "Mi aplicación tiene un bug muy específico que solo ocurre los martes"
    customer_email = "cliente2@example.com"
    
    session = agent.start_troubleshooting(
        problem_description=problem_description,
        customer_email=customer_email
    )
    
    print(f"\n📝 Problema: {problem_description}")
    print(f"🔍 Problema detectado: {session.detected_problem.problem_title if session.detected_problem else 'No detectado'}")
    
    first_step = agent.get_current_step(session.session_id)
    
    if first_step.get("status") == "no_problem_detected":
        print("\n💡 Respuesta del sistema:")
        print(agent.format_step_response(first_step))
        
        # En este caso, se debería escalar inmediatamente
        escalation_info = agent.escalate_ticket(
            session_id=session.session_id,
            reason="Problema no identificado en la base de conocimiento"
        )
        print(f"\n📤 Ticket escalado: {escalation_info.get('ticket_id', 'N/A')}")


def main():
    """Función principal que ejecuta todos los ejemplos"""
    print("\n" + "=" * 60)
    print("SISTEMA DE TROUBLESHOOTING AUTOMATIZADO")
    print("Ejemplos de Uso")
    print("=" * 60)
    
    try:
        # Ejemplo 1: Uso básico
        session, agent = ejemplo_basico()
        
        # Ejemplo 2: Completar pasos
        # ejemplo_paso_a_paso(session, agent)
        
        # Ejemplo 3: Escalación
        # ejemplo_escalacion(session, agent)
        
        # Ejemplo 4: Resumen
        ejemplo_resumen(session, agent)
        
        # Ejemplo 5: Problema no detectado
        ejemplo_problema_no_detectado()
        
        print("\n" + "=" * 60)
        print("✅ Todos los ejemplos completados")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()



