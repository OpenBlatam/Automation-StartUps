#!/usr/bin/env python3
"""
Generador de Plantilla Personalizada
Genera plantillas HTML personalizadas basándose en parámetros del usuario.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json

class GeneradorPlantillaPersonalizada:
    def __init__(self):
        self.plantilla_base = self._cargar_plantilla_base()
        self.colores_disponibles = {
            'azul': {'principal': '#1a73e8', 'secundario': '#1557b0', 'fondo': '#e8f0fe'},
            'rojo': {'principal': '#ea4335', 'secundario': '#c5221f', 'fondo': '#fce8e6'},
            'verde': {'principal': '#34a853', 'secundario': '#137333', 'fondo': '#e6f4ea'},
            'púrpura': {'principal': '#9c27b0', 'secundario': '#7b1fa2', 'fondo': '#f3e5f5'},
            'naranja': {'principal': '#f59e0b', 'secundario': '#d97706', 'fondo': '#fffbeb'},
            'cian': {'principal': '#0284c7', 'secundario': '#0369a1', 'fondo': '#e0f2fe'},
            'rosa': {'principal': '#ec4899', 'secundario': '#db2777', 'fondo': '#fce7f3'},
            'gris': {'principal': '#6b7280', 'secundario': '#4b5563', 'fondo': '#f3f4f6'},
        }
    
    def _cargar_plantilla_base(self) -> str:
        """Carga la plantilla base HTML."""
        return """<!DOCTYPE html>
<html lang="es" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Firma Personalizada</title>
    <!--[if mso]>
    <style type="text/css">
        body, table, td {font-family: Arial, sans-serif !important;}
    </style>
    <![endif]-->
    <style type="text/css">
        @media only screen and (max-width: 600px) {
            .mobile-stack { display: block !important; width: 100% !important; }
        }
    </style>
</head>
<body style="margin: 0; padding: 0; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14px; line-height: 1.6; color: #333333; background-color: #ffffff;">
    <!--[if mso]>
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
        <tr>
            <td style="padding: 20px;">
    <![endif]-->
    <!-- Email Signature Template - Personalizada -->
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="max-width: 550px; margin: 0 auto; background-color: #ffffff;">
        <tr>
            <td style="padding: 20px 15px;">
                <!-- Header -->
                {header}
                
                <!-- Badge -->
                {badge}
                
                <!-- Información -->
                {informacion}
                
                <!-- CTAs -->
                {ctas}
                
                <!-- Contact Information -->
                {contacto}
            </td>
        </tr>
    </table>
    <!--[if mso]>
            </td>
        </tr>
    </table>
    <![endif]-->
</body>
</html>"""
    
    def generar_header(self, nombre: str, titulo: str, empresa: str, credenciales: Optional[str] = None, emoji: Optional[str] = None, color: str = '#1a73e8') -> str:
        """Genera el header de la firma."""
        emoji_text = f"{emoji} " if emoji else ""
        credenciales_text = f"<br><td style=\"font-size: 12px; color: #80868b; margin: 0; padding: 0; line-height: 1.4;\">{credenciales}</td>" if credenciales else ""
        
        return f"""<table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                    <tr>
                        <td style="padding-bottom: 15px;">
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td style="vertical-align: middle;">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                            <tr>
                                                <td style="font-size: 18px; font-weight: 700; color: {color}; margin: 0; padding: 0; padding-bottom: 5px; line-height: 1.3;">
                                                    {emoji_text}{nombre}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size: 14px; color: #5f6368; margin: 0; padding: 0; padding-bottom: 3px; line-height: 1.4;">
                                                    {titulo} | {empresa}
                                                </td>
                                            </tr>
                                            {credenciales_text}
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>"""
    
    def generar_badge(self, texto: str, email: str, color_principal: str, color_secundario: str, emoji: Optional[str] = None) -> str:
        """Genera el badge destacado."""
        emoji_text = f"{emoji} " if emoji else ""
        
        return f"""<table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-bottom: 15px; padding: 12px; background: linear-gradient(135deg, {color_principal} 0%, {color_secundario} 100%); border-radius: 6px;">
                    <tr>
                        <td style="text-align: center;">
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td style="font-size: 13px; color: #ffffff; font-weight: 600; margin: 0; padding: 0; line-height: 1.4;">
                                        {emoji_text}{texto} | 📧 {email}
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>"""
    
    def generar_informacion(self, items: List[Dict[str, str]], color: str, color_fondo: str) -> str:
        """Genera la sección de información."""
        items_html = ""
        for item in items:
            items_html += f"<strong style=\"color: {color};\">{item['label']}</strong> {item['valor']}<br>\n                                        "
        
        return f"""<table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-top: 15px; padding: 12px; background-color: {color_fondo}; border-left: 4px solid {color}; border-radius: 4px;">
                    <tr>
                        <td>
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td style="font-size: 12px; color: #333333; line-height: 1.7; margin: 0; padding: 0;">
                                        {items_html}
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>"""
    
    def generar_ctas(self, botones: List[Dict[str, str]], color_principal: str, color_secundario: str) -> str:
        """Genera los botones CTA."""
        if not botones:
            return ""
        
        botones_html = ""
        for i, boton in enumerate(botones):
            color_btn = color_principal if i == 0 else color_secundario
            botones_html += f"""<td style="padding-right: 10px; padding-bottom: 10px;" class="mobile-stack">
                                        <a href="{boton['url']}" style="display: inline-block; padding: 12px 24px; background-color: {color_btn}; color: #ffffff !important; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 13px; line-height: 1.4; text-align: center; min-width: 160px;" target="_blank" rel="noopener noreferrer">
                                            {boton['texto']}
                                        </a>
                                    </td>"""
        
        return f"""<table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-top: 15px;">
                    <tr>
                        <td class="mobile-center">
                            <!--[if mso]>
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    {botones_html.replace('class="mobile-stack"', '')}
                                </tr>
                            </table>
                            <![endif]-->
                            <!--[if !mso]><!-->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" class="mobile-stack">
                                <tr>
                                    {botones_html}
                                </tr>
                            </table>
                            <!--<![endif]-->
                        </td>
                    </tr>
                </table>"""
    
    def generar_contacto(self, email: str, telefono: str, color: str) -> str:
        """Genera la sección de contacto."""
        return f"""<table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #e8eaed;">
                    <tr>
                        <td>
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td style="padding: 5px 0; line-height: 1.6;">
                                        <a href="mailto:{email}" style="color: {color}; text-decoration: none; font-size: 13px; line-height: 1.6;">
                                            📧 {email}
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 5px 0; line-height: 1.6;">
                                        <a href="tel:{telefono}" style="color: {color}; text-decoration: none; font-size: 13px; line-height: 1.6;">
                                            📱 {telefono}
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>"""
    
    def generar_plantilla(self, config: Dict) -> str:
        """Genera una plantilla completa basándose en la configuración."""
        # Obtener colores
        tema = config.get('tema', 'azul')
        colores = self.colores_disponibles.get(tema, self.colores_disponibles['azul'])
        
        # Generar secciones
        header = self.generar_header(
            nombre=config.get('nombre', '[Tu Nombre]'),
            titulo=config.get('titulo', '[Tu Título]'),
            empresa=config.get('empresa', '[Nombre de la Empresa]'),
            credenciales=config.get('credenciales'),
            emoji=config.get('emoji'),
            color=colores['principal']
        )
        
        badge = self.generar_badge(
            texto=config.get('badge_texto', 'Profesional'),
            email=config.get('email', '[email@ejemplo.com]'),
            color_principal=colores['principal'],
            color_secundario=colores['secundario'],
            emoji=config.get('emoji')
        )
        
        informacion = self.generar_informacion(
            items=config.get('informacion', []),
            color=colores['principal'],
            color_fondo=colores['fondo']
        )
        
        ctas = self.generar_ctas(
            botones=config.get('botones', []),
            color_principal=colores['principal'],
            color_secundario=colores['secundario']
        )
        
        contacto = self.generar_contacto(
            email=config.get('email', '[email@ejemplo.com]'),
            telefono=config.get('telefono', '[+1 234 567 890]'),
            color=colores['principal']
        )
        
        # Reemplazar en plantilla base
        plantilla = self.plantilla_base.format(
            header=header,
            badge=badge,
            informacion=informacion,
            ctas=ctas,
            contacto=contacto
        )
        
        return plantilla
    
    def generar_desde_json(self, archivo_json: str, archivo_salida: str) -> None:
        """Genera una plantilla desde un archivo JSON de configuración."""
        with open(archivo_json, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        plantilla = self.generar_plantilla(config)
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(plantilla)
        
        print(f"✅ Plantilla generada: {archivo_salida}")
    
    def generar_interactivo(self) -> None:
        """Genera una plantilla de forma interactiva."""
        print("\n" + "="*60)
        print("GENERADOR DE PLANTILLA PERSONALIZADA")
        print("="*60 + "\n")
        
        config = {}
        
        # Información básica
        config['nombre'] = input("Nombre completo: ").strip() or "[Tu Nombre]"
        config['titulo'] = input("Título profesional: ").strip() or "[Tu Título]"
        config['empresa'] = input("Nombre de la empresa: ").strip() or "[Nombre de la Empresa]"
        config['credenciales'] = input("Credenciales (ej: Número de Colegio, Universidad) [opcional]: ").strip() or None
        config['emoji'] = input("Emoji para la firma [opcional]: ").strip() or None
        
        # Contacto
        config['email'] = input("Email: ").strip() or "[email@ejemplo.com]"
        config['telefono'] = input("Teléfono: ").strip() or "[+1 234 567 890]"
        
        # Badge
        config['badge_texto'] = input("Texto del badge: ").strip() or "Profesional"
        
        # Tema
        print("\nTemas disponibles:", ", ".join(self.colores_disponibles.keys()))
        tema = input("Tema de color (default: azul): ").strip().lower() or "azul"
        config['tema'] = tema if tema in self.colores_disponibles else "azul"
        
        # Información adicional
        print("\nInformación adicional (dejar vacío para terminar):")
        config['informacion'] = []
        while True:
            label = input("  Label (ej: 📍 Clínica): ").strip()
            if not label:
                break
            valor = input("  Valor: ").strip()
            config['informacion'].append({'label': label, 'valor': valor})
        
        # Botones CTA
        print("\nBotones CTA (dejar vacío para terminar):")
        config['botones'] = []
        while True:
            texto = input("  Texto del botón: ").strip()
            if not texto:
                break
            url = input("  URL: ").strip()
            config['botones'].append({'texto': texto, 'url': url})
        
        # Generar plantilla
        plantilla = self.generar_plantilla(config)
        
        # Guardar
        nombre_archivo = input("\nNombre del archivo (default: firma_personalizada.html): ").strip() or "firma_personalizada.html"
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(plantilla)
        
        print(f"\n✅ Plantilla generada: {nombre_archivo}")

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Genera plantillas personalizadas')
    parser.add_argument('-i', '--interactivo', action='store_true',
                       help='Modo interactivo')
    parser.add_argument('-j', '--json', type=str,
                       help='Archivo JSON de configuración')
    parser.add_argument('-o', '--output', type=str, default='firma_personalizada.html',
                       help='Archivo de salida')
    
    args = parser.parse_args()
    
    generador = GeneradorPlantillaPersonalizada()
    
    if args.interactivo:
        generador.generar_interactivo()
    elif args.json:
        generador.generar_desde_json(args.json, args.output)
    else:
        # Ejemplo de uso
        config_ejemplo = {
            'nombre': 'Dr. Juan Pérez',
            'titulo': 'Médico Especialista',
            'empresa': 'Clínica San José',
            'credenciales': '📋 12345 | 🎓 Universidad Nacional',
            'emoji': '🏥',
            'email': 'juan.perez@clinica.com',
            'telefono': '+1 234 567 890',
            'badge_texto': 'Cuidado Integral de la Salud',
            'tema': 'azul',
            'informacion': [
                {'label': '📍 Clínica:', 'valor': 'Calle Principal 123'},
                {'label': '🕐 Horario:', 'valor': 'Lun-Vie 9:00-18:00'}
            ],
            'botones': [
                {'texto': '📅 Agendar Cita', 'url': 'https://calendly.com/juan'},
                {'texto': '📋 Ver Servicios', 'url': 'https://clinica.com/servicios'}
            ]
        }
        
        plantilla = generador.generar_plantilla(config_ejemplo)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(plantilla)
        
        print(f"✅ Plantilla de ejemplo generada: {args.output}")

if __name__ == "__main__":
    main()





