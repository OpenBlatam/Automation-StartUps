"""
Módulo para generar emails interactivos usando AMP (Accelerated Mobile Pages).
"""
import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class AMPComponentType(Enum):
    """Tipos de componentes AMP disponibles"""
    FORM = 'form'
    CAROUSEL = 'carousel'
    ACCORDION = 'accordion'
    LIGHTBOX = 'lightbox'
    LIVE_LIST = 'live_list'
    DATE_PICKER = 'date_picker'


class AMPEmailGenerator:
    """
    Genera emails interactivos usando AMP (Accelerated Mobile Pages).
    
    Attributes:
        componentes_amp: Diccionario con componentes AMP disponibles
    """
    
    def __init__(self):
        """Inicializa el generador de emails AMP"""
        self.componentes_amp = {
            'formulario': 'amp-form',
            'carousel': 'amp-carousel',
            'acordeon': 'amp-accordion',
            'lightbox': 'amp-lightbox',
            'live_list': 'amp-live-list',
            'date_picker': 'amp-date-picker'
        }
        logger.info("AMPEmailGenerator inicializado")
    
    def generar_email_interactivo(self, tipo: str, contenido: Dict) -> str:
        """
        Genera email AMP interactivo según el tipo especificado.
        
        Args:
            tipo: Tipo de email ('encuesta', 'carrito', 'calendario', 'productos')
            contenido: Diccionario con el contenido del email
        
        Returns:
            String con el HTML del email AMP
        
        Raises:
            ValueError: Si el tipo no es válido
        """
        if not tipo or not isinstance(tipo, str):
            raise ValueError("Tipo de email debe ser un string no vacío")
        
        templates = {
            'encuesta': self._generar_encuesta_amp,
            'carrito': self._generar_carrito_amp,
            'calendario': self._generar_calendario_amp,
            'productos': self._generar_productos_amp
        }
        
        generator = templates.get(tipo)
        if not generator:
            logger.warning(f"Tipo {tipo} no encontrado, usando template básico")
            return self._generar_basico_amp(contenido)
        
        try:
            return generator(contenido)
        except Exception as e:
            logger.error(f"Error generando email {tipo}: {e}")
            return self._generar_basico_amp(contenido)
    
    def _generar_encuesta_amp(self, contenido: Dict) -> str:
        """
        Genera email con encuesta interactiva.
        
        Args:
            contenido: Diccionario con contenido de la encuesta
        
        Returns:
            String con HTML del email AMP
        """
        titulo = contenido.get('titulo', 'Encuesta Rápida')
        pregunta = contenido.get('pregunta', '¿Cómo calificarías nuestro servicio?')
        endpoint = contenido.get('endpoint', '/api/encuesta')
        
        return f"""<!doctype html>
<html ⚡4email>
<head>
    <meta charset="utf-8">
    <script async src="https://cdn.ampproject.org/v0.js"></script>
    <script async custom-element="amp-form" src="https://cdn.ampproject.org/v0/amp-form-0.1.js"></script>
    <style amp4email-boilerplate>body{{visibility:hidden}}</style>
</head>
<body>
    <h1>{titulo}</h1>
    
    <form method="post" action-xhr="{endpoint}" target="_top">
        <p>{pregunta}</p>
        
        <label>
            <input type="radio" name="rating" value="5" required> ⭐⭐⭐⭐⭐ Excelente
        </label>
        <label>
            <input type="radio" name="rating" value="4" required> ⭐⭐⭐⭐ Muy bueno
        </label>
        <label>
            <input type="radio" name="rating" value="3" required> ⭐⭐⭐ Bueno
        </label>
        <label>
            <input type="radio" name="rating" value="2" required> ⭐⭐ Regular
        </label>
        <label>
            <input type="radio" name="rating" value="1" required> ⭐ Malo
        </label>
        
        <input type="submit" value="Enviar Respuesta">
        
        <div submit-success>
            <template type="amp-mustache">
                ¡Gracias por tu respuesta! {{message}}
            </template>
        </div>
        
        <div submit-error>
            <template type="amp-mustache">
                Error: {{message}}
            </template>
        </div>
    </form>
</body>
</html>"""
    
    def _generar_carrito_amp(self, contenido: Dict) -> str:
        """
        Genera email con carrito interactivo.
        
        Args:
            contenido: Diccionario con productos del carrito
        
        Returns:
            String con HTML del email AMP
        """
        productos_html = ""
        productos = contenido.get('productos', [])
        
        for producto in productos:
            nombre = producto.get('nombre', '')
            precio = producto.get('precio', 0)
            productos_html += f"""
            <div class="producto">
                <h3>{nombre}</h3>
                <p>${precio:,.2f}</p>
                <button on="tap:AMP.setState({{cantidad: cantidad + 1}})">Agregar</button>
            </div>
            """
        
        return f"""<!doctype html>
<html ⚡4email>
<head>
    <meta charset="utf-8">
    <script async src="https://cdn.ampproject.org/v0.js"></script>
    <script async custom-element="amp-bind" src="https://cdn.ampproject.org/v0/amp-bind-0.1.js"></script>
    <style amp4email-boilerplate>body{{visibility:hidden}}</style>
</head>
<body>
    <h1>Tu Carrito</h1>
    
    <div [text]="'Total: $' + (precio * cantidad).toFixed(2)">
        Total: $0.00
    </div>
    
    {productos_html}
    
    <button on="tap:AMP.setState({{cantidad: 0}})">
        Limpiar Carrito
    </button>
</body>
</html>"""
    
    def _generar_calendario_amp(self, contenido: Dict) -> str:
        """
        Genera email con calendario para agendar.
        
        Args:
            contenido: Diccionario con configuración del calendario
        
        Returns:
            String con HTML del email AMP
        """
        endpoint = contenido.get('endpoint', '/api/agendar')
        
        return f"""<!doctype html>
<html ⚡4email>
<head>
    <meta charset="utf-8">
    <script async src="https://cdn.ampproject.org/v0.js"></script>
    <script async custom-element="amp-date-picker" src="https://cdn.ampproject.org/v0/amp-date-picker-0.1.js"></script>
    <style amp4email-boilerplate>body{{visibility:hidden}}</style>
</head>
<body>
    <h1>Agenda una Cita</h1>
    
    <amp-date-picker
        type="single"
        mode="overlay"
        layout="container"
        on="select:AMP.setState({{fecha: event.date}})">
    </amp-date-picker>
    
    <p>Fecha seleccionada: <span [text]="fecha || 'Ninguna'">Ninguna</span></p>
    
    <form method="post" action-xhr="{endpoint}">
        <input type="hidden" name="fecha" [value]="fecha">
        <input type="submit" value="Confirmar Cita">
    </form>
</body>
</html>"""
    
    def _generar_productos_amp(self, contenido: Dict) -> str:
        """
        Genera email con productos interactivos.
        
        Args:
            contenido: Diccionario con productos a mostrar
        
        Returns:
            String con HTML del email AMP
        """
        slides = self._generar_slides_productos(contenido.get('productos', []))
        
        return f"""<!doctype html>
<html ⚡4email>
<head>
    <meta charset="utf-8">
    <script async src="https://cdn.ampproject.org/v0.js"></script>
    <script async custom-element="amp-carousel" src="https://cdn.ampproject.org/v0/amp-carousel-0.1.js"></script>
    <style amp4email-boilerplate>body{{visibility:hidden}}</style>
</head>
<body>
    <h1>Productos Destacados</h1>
    
    <amp-carousel width="400" height="300" layout="responsive" type="slides">
        {slides}
    </amp-carousel>
</body>
</html>"""
    
    def _generar_slides_productos(self, productos: List[Dict]) -> str:
        """
        Genera slides de productos para el carousel.
        
        Args:
            productos: Lista de diccionarios con información de productos
        
        Returns:
            String con HTML de los slides
        """
        slides = ""
        for producto in productos:
            nombre = producto.get('nombre', '')
            precio = producto.get('precio', 0)
            imagen = producto.get('imagen', '')
            link = producto.get('link', '#')
            
            slides += f"""
            <div class="slide">
                <img src="{imagen}" alt="{nombre}">
                <h3>{nombre}</h3>
                <p>${precio:,.2f}</p>
                <a href="{link}">Ver Producto</a>
            </div>
            """
        return slides
    
    def _generar_basico_amp(self, contenido: Dict) -> str:
        """
        Genera email AMP básico.
        
        Args:
            contenido: Diccionario con contenido básico
        
        Returns:
            String con HTML del email AMP básico
        """
        titulo = contenido.get('titulo', 'Email Interactivo')
        mensaje = contenido.get('mensaje', '')
        
        return f"""<!doctype html>
<html ⚡4email>
<head>
    <meta charset="utf-8">
    <script async src="https://cdn.ampproject.org/v0.js"></script>
    <style amp4email-boilerplate>body{{visibility:hidden}}</style>
</head>
<body>
    <h1>{titulo}</h1>
    <p>{mensaje}</p>
</body>
</html>"""




