"""
Módulo para generar emails transaccionales personalizados y optimizados.
"""
import logging
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class TransactionalEmailType(Enum):
    """Tipos de emails transaccionales"""
    CONFIRMACION_COMPRA = 'confirmacion_compra'
    ENVIO_PEDIDO = 'envio_pedido'
    ENTREGA_COMPLETADA = 'entrega_completada'
    RESET_PASSWORD = 'reset_password'
    BIENVENIDA_CUENTA = 'bienvenida_cuenta'


@dataclass
class TransactionalEmailConfig:
    """Configuración para email transaccional"""
    tipo: TransactionalEmailType
    prioridad: str
    timing: str
    objetivo: str


class TransactionalEmailGenerator:
    """
    Genera emails transaccionales personalizados y optimizados.
    
    Attributes:
        tipos_transaccionales: Configuración de tipos de emails transaccionales
    """
    
    def __init__(self):
        """Inicializa el generador de emails transaccionales"""
        self.tipos_transaccionales = {
            TransactionalEmailType.CONFIRMACION_COMPRA: TransactionalEmailConfig(
                tipo=TransactionalEmailType.CONFIRMACION_COMPRA,
                prioridad='alta',
                timing='inmediato',
                objetivo='confirmar_y_educar'
            ),
            TransactionalEmailType.ENVIO_PEDIDO: TransactionalEmailConfig(
                tipo=TransactionalEmailType.ENVIO_PEDIDO,
                prioridad='alta',
                timing='inmediato',
                objetivo='informar_y_upsell'
            ),
            TransactionalEmailType.ENTREGA_COMPLETADA: TransactionalEmailConfig(
                tipo=TransactionalEmailType.ENTREGA_COMPLETADA,
                prioridad='media',
                timing='inmediato',
                objetivo='solicitar_review'
            ),
            TransactionalEmailType.RESET_PASSWORD: TransactionalEmailConfig(
                tipo=TransactionalEmailType.RESET_PASSWORD,
                prioridad='critica',
                timing='inmediato',
                objetivo='seguridad'
            ),
            TransactionalEmailType.BIENVENIDA_CUENTA: TransactionalEmailConfig(
                tipo=TransactionalEmailType.BIENVENIDA_CUENTA,
                prioridad='alta',
                timing='inmediato',
                objetivo='onboarding'
            )
        }
        logger.info("TransactionalEmailGenerator inicializado")
    
    def generar_email_transaccional(self, tipo: TransactionalEmailType, datos: Dict) -> str:
        """
        Genera email transaccional según tipo.
        
        Args:
            tipo: Tipo de email transaccional
            datos: Diccionario con datos para el email
        
        Returns:
            String con el contenido del email
        
        Raises:
            ValueError: Si el tipo no es válido
        """
        if not isinstance(tipo, TransactionalEmailType):
            raise ValueError(f"Tipo debe ser TransactionalEmailType, recibido: {type(tipo)}")
        
        templates = {
            TransactionalEmailType.CONFIRMACION_COMPRA: self._generar_confirmacion_compra,
            TransactionalEmailType.ENVIO_PEDIDO: self._generar_envio_pedido,
            TransactionalEmailType.ENTREGA_COMPLETADA: self._generar_entrega_completada,
            TransactionalEmailType.RESET_PASSWORD: self._generar_reset_password,
            TransactionalEmailType.BIENVENIDA_CUENTA: self._generar_bienvenida_cuenta
        }
        
        generator = templates.get(tipo)
        if not generator:
            logger.error(f"Template no encontrado para tipo {tipo}")
            return ""
        
        try:
            return generator(datos)
        except Exception as e:
            logger.error(f"Error generando email {tipo}: {e}")
            return ""
    
    def _generar_confirmacion_compra(self, datos: Dict) -> str:
        """Genera email de confirmación de compra"""
        nombre = datos.get('nombre_cliente', '')
        numero_pedido = datos.get('numero_pedido', '')
        fecha = datos.get('fecha', '')
        total = datos.get('total', 0)
        empresa = datos.get('empresa', 'El Equipo')
        productos = self._formatear_productos_pedido(datos.get('productos', []))
        
        return f"""Asunto: ✅ Confirmación de compra #{numero_pedido}

Hola {nombre},

¡Gracias por tu compra!

---

**Detalles del Pedido:**

Número de pedido: #{numero_pedido}
Fecha: {fecha}
Total: ${total:,.2f}

**Productos:**
{productos}

---

**Próximos Pasos:**

1. Recibirás un email cuando tu pedido sea enviado
2. Puedes rastrear tu pedido en: [LINK_RASTREO]
3. Accede a recursos exclusivos: [LINK_RECURSOS]

---

**Mientras tanto:**

¿Sabías que puedes obtener un 20% de descuento en tu próxima compra?

[🔗 Ver Ofertas Especiales]

---

¿Preguntas? Responde a este email.

{empresa}
"""
    
    def _generar_envio_pedido(self, datos: Dict) -> str:
        """Genera email de envío de pedido"""
        nombre = datos.get('nombre_cliente', '')
        numero_pedido = datos.get('numero_pedido', '')
        numero_rastreo = datos.get('numero_rastreo', '')
        transportista = datos.get('transportista', '')
        fecha_entrega = datos.get('fecha_entrega', '')
        empresa = datos.get('empresa', 'El Equipo')
        productos = self._formatear_productos_pedido(datos.get('productos', []))
        
        return f"""Asunto: 📦 Tu pedido #{numero_pedido} ha sido enviado

Hola {nombre},

¡Buenas noticias! Tu pedido ha sido enviado.

---

**Información de Envío:**

Número de rastreo: {numero_rastreo}
Transportista: {transportista}
Fecha estimada de entrega: {fecha_entrega}

[🔗 Rastrear Mi Pedido]

---

**Productos Enviados:**

{productos}

---

**¿Necesitas algo más?**

Mientras esperas tu pedido, echa un vistazo a estos productos complementarios:

[🔗 Ver Productos Relacionados]

---

{empresa}
"""
    
    def _generar_entrega_completada(self, datos: Dict) -> str:
        """Genera email de entrega completada"""
        nombre = datos.get('nombre_cliente', '')
        numero_pedido = datos.get('numero_pedido', '')
        fecha_entrega = datos.get('fecha_entrega', '')
        direccion = datos.get('direccion_entrega', '')
        empresa = datos.get('empresa', 'El Equipo')
        
        return f"""Asunto: ✅ Tu pedido #{numero_pedido} ha sido entregado

Hola {nombre},

¡Tu pedido ha sido entregado exitosamente!

---

**Detalles de Entrega:**

Fecha de entrega: {fecha_entrega}
Dirección: {direccion}

---

**¿Cómo te está yendo con tu compra?**

Nos encantaría saber tu opinión. Por dejarnos un review, recibirás:

🎁 15% de descuento en tu próxima compra
🎁 Acceso a recursos exclusivos

[🔗 Dejar Review]

---

**¿Necesitas ayuda?**

Si tienes alguna pregunta o problema, responde a este email.

{empresa}
"""
    
    def _generar_reset_password(self, datos: Dict) -> str:
        """Genera email de reset de contraseña"""
        nombre = datos.get('nombre', '')
        empresa = datos.get('empresa', 'El Equipo')
        
        return f"""Asunto: 🔐 Restablecer tu contraseña

Hola {nombre},

Recibimos una solicitud para restablecer tu contraseña.

---

**Para restablecer tu contraseña:**

[🔗 Restablecer Contraseña]

Este link expira en 1 hora por seguridad.

---

**¿No solicitaste esto?**

Si no solicitaste restablecer tu contraseña, puedes ignorar este email.

Tu cuenta está segura.

---

**Consejos de Seguridad:**

- Usa una contraseña única y segura
- No compartas tu contraseña
- Activa la autenticación de dos factores

{empresa}
"""
    
    def _generar_bienvenida_cuenta(self, datos: Dict) -> str:
        """Genera email de bienvenida de cuenta"""
        nombre = datos.get('nombre', '')
        empresa = datos.get('empresa', 'El Equipo')
        
        return f"""Asunto: 🎉 ¡Bienvenido/a, {nombre}!

Hola {nombre},

¡Gracias por crear tu cuenta!

---

**Para empezar:**

1. Completa tu perfil: [LINK_PERFIL]
2. Explora nuestros productos: [LINK_PRODUCTOS]
3. Descarga tu guía gratuita: [LINK_GUIA]

---

**Recursos Exclusivos:**

🎁 Guía de inicio rápido
🎁 Video tutorial
🎁 Comunidad de soporte

[🔗 Acceder a Recursos]

---

**¿Preguntas?**

Responde a este email y te ayudamos.

¡Bienvenido/a a la familia!

{empresa}
"""
    
    def _formatear_productos_pedido(self, productos: List[Dict]) -> str:
        """Formatea productos del pedido"""
        if not productos:
            return "No hay productos"
        
        texto = ""
        for producto in productos:
            nombre = producto.get('nombre', '')
            cantidad = producto.get('cantidad', 1)
            precio = producto.get('precio', 0)
            texto += f"• {nombre} x{cantidad} - ${precio:,.2f}\n"
        
        return texto




