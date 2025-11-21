#!/usr/bin/env python3
"""
Creador de Guía de Troubleshooting
Genera una guía completa de solución de problemas
"""

import os
from pathlib import Path
from datetime import datetime

def generar_guia_troubleshooting() -> str:
    """Genera la guía de troubleshooting"""
    guia = "# 🔧 Guía de Troubleshooting - Firmas de Email\n\n"
    guia += f"**Versión:** 4.2 | **Fecha:** {datetime.now().strftime('%d de %B de %Y')}\n\n"
    
    guia += "Esta guía te ayudará a resolver los problemas más comunes al trabajar con firmas de email.\n\n"
    
    guia += "## 📋 Tabla de Contenidos\n\n"
    guia += "1. [Problemas de Visualización](#problemas-de-visualización)\n"
    guia += "2. [Problemas de Compatibilidad](#problemas-de-compatibilidad)\n"
    guia += "3. [Problemas de Personalización](#problemas-de-personalización)\n"
    guia += "4. [Problemas de Enlaces](#problemas-de-enlaces)\n"
    guia += "5. [Problemas de Rendimiento](#problemas-de-rendimiento)\n"
    guia += "6. [Problemas con Scripts](#problemas-con-scripts)\n"
    guia += "7. [Herramientas de Diagnóstico](#herramientas-de-diagnóstico)\n"
    guia += "8. [Solución Rápida](#solución-rápida)\n\n"
    
    guia += "## 👁️ Problemas de Visualización\n\n"
    
    guia += "### La firma no se muestra en el email\n\n"
    guia += "**Síntomas:**\n"
    guia += "- La firma no aparece al enviar emails\n"
    guia += "- Solo aparece texto plano\n\n"
    guia += "**Causas posibles:**\n"
    guia += "1. El cliente de email no soporta HTML\n"
    guia += "2. La firma no se guardó correctamente\n"
    guia += "3. El formato HTML está corrupto\n\n"
    guia += "**Soluciones:**\n"
    guia += "1. Verifica que tu cliente de email soporte HTML (Gmail, Outlook, Apple Mail sí lo hacen)\n"
    guia += "2. Copia y pega el HTML completo, no solo una parte\n"
    guia += "3. Usa `validar_firma.py` para verificar la estructura HTML\n"
    guia += "4. Prueba con una versión simple primero (`firma_*_simple.html`)\n\n"
    
    guia += "### Los colores no se ven correctamente\n\n"
    guia += "**Síntomas:**\n"
    guia += "- Los colores aparecen diferentes o no aparecen\n"
    guia += "- Algunos elementos son invisibles\n\n"
    guia += "**Causas posibles:**\n"
    guia += "1. Códigos de color incorrectos\n"
    guia += "2. El cliente de email no soporta ciertos colores\n"
    guia += "3. Modo oscuro activado\n\n"
    guia += "**Soluciones:**\n"
    guia += "1. Usa códigos hexadecimales completos (#RRGGBB, no #RGB)\n"
    guia += "2. Evita colores con transparencia (rgba)\n"
    guia += "3. Prueba en diferentes clientes de email\n"
    guia += "4. Usa `cambiar_colores.py` para cambiar esquemas predefinidos\n\n"
    
    guia += "### El diseño se ve roto o desordenado\n\n"
    guia += "**Síntomas:**\n"
    guia += "- Los elementos están fuera de lugar\n"
    guia += "- Las tablas no se alinean correctamente\n\n"
    guia += "**Causas posibles:**\n"
    guia += "1. Estilos CSS faltantes o incorrectos\n"
    guia += "2. Estructura de tablas incorrecta\n"
    guia += "3. Cliente de email no compatible\n\n"
    guia += "**Soluciones:**\n"
    guia += "1. Verifica que todos los estilos estén inline\n"
    guia += "2. Asegúrate de usar tablas para estructura (no divs)\n"
    guia += "3. Usa `verificar_compatibilidad.py` para diagnosticar\n"
    guia += "4. Prueba con una versión simple primero\n\n"
    
    guia += "## 🔄 Problemas de Compatibilidad\n\n"
    
    guia += "### La firma no funciona en Outlook\n\n"
    guia += "**Síntomas:**\n"
    guia += "- La firma se ve mal o no se muestra en Outlook\n"
    guia += "- Los botones no funcionan\n\n"
    guia += "**Causas posibles:**\n"
    guia += "1. Falta soporte VML/MSO\n"
    guia += "2. Outlook usa un motor de renderizado diferente\n\n"
    guia += "**Soluciones:**\n"
    guia += "1. Usa plantillas que incluyan VML (versiones completas)\n"
    guia += "2. Verifica que tenga comentarios `<!--[if mso]>`\n"
    guia += "3. Usa `verificar_compatibilidad.py` para diagnosticar\n"
    guia += "4. Evita CSS avanzado (gradientes, sombras complejas)\n\n"
    
    guia += "### La firma se ve mal en móvil\n\n"
    guia += "**Síntomas:**\n"
    guia += "- El diseño se rompe en dispositivos móviles\n"
    guia += "- Los elementos se superponen\n\n"
    guia += "**Causas posibles:**\n"
    guia += "1. Falta diseño responsive\n"
    guia += "2. Media queries no funcionan\n\n"
    guia += "**Soluciones:**\n"
    guia += "1. Verifica que tenga media queries en el `<head>`\n"
    guia += "2. Asegúrate de usar clases `mobile-stack`\n"
    guia += "3. Prueba en un dispositivo móvil real\n"
    guia += "4. Usa `max-width: 600px` en tablas principales\n\n"
    
    guia += "### Problemas en Gmail\n\n"
    guia += "**Síntomas:**\n"
    guia += "- La firma se ve diferente en Gmail\n"
    guia += "- Algunos estilos no se aplican\n\n"
    guia += "**Causas posibles:**\n"
    guia += "1. Gmail elimina ciertos estilos\n"
    guia += "2. Gmail tiene limitaciones de CSS\n\n"
    guia += "**Soluciones:**\n"
    guia += "1. Usa estilos inline (no CSS externo)\n"
    guia += "2. Evita JavaScript y CSS en `<head>`\n"
    guia += "3. Prueba en Gmail Web y App\n"
    guia += "4. Consulta [Can I Email](https://www.caniemail.com/) para compatibilidad\n\n"
    
    guia += "## ✏️ Problemas de Personalización\n\n"
    
    guia += "### Los placeholders no se reemplazan\n\n"
    guia += "**Síntomas:**\n"
    guia += "- Los placeholders siguen apareciendo como `[Tu Nombre]`\n\n"
    guia += "**Causas posibles:**\n"
    guia += "1. No se reemplazaron manualmente\n"
    guia += "2. El script de personalización falló\n\n"
    guia += "**Soluciones:**\n"
    guia += "1. Busca y reemplaza manualmente todos los placeholders\n"
    guia += "2. Usa `personalizar_firma.py` para automatizar\n"
    guia += "3. Verifica que no haya espacios extra en los placeholders\n"
    guia += "4. Consulta `PLACEHOLDERS.md` para lista completa\n\n"
    
    guia += "### El logo no se muestra\n\n"
    guia += "**Síntomas:**\n"
    guia += "- El logo no aparece o aparece roto\n\n"
    guia += "**Causas posibles:**\n"
    guia += "1. URL del logo incorrecta\n"
    guia += "2. El servidor bloquea hotlinking\n"
    guia += "3. El formato de imagen no es compatible\n\n"
    guia += "**Soluciones:**\n"
    guia += "1. Usa URL absoluta (https://...)\n"
    guia += "2. Sube el logo a un servidor confiable\n"
    guia += "3. Usa formatos JPG o PNG\n"
    guia += "4. Verifica que la URL sea accesible públicamente\n"
    guia += "5. Usa `verificar_enlaces.py` para verificar URLs\n\n"
    
    guia += "## 🔗 Problemas de Enlaces\n\n"
    
    guia += "### Los enlaces no funcionan\n\n"
    guia += "**Síntomas:**\n"
    guia += "- Los enlaces no son clicables\n"
    guia += "- Los enlaces llevan a páginas incorrectas\n\n"
    guia += "**Causas posibles:**\n"
    guia += "1. URLs incorrectas o mal formateadas\n"
    guia += "2. Falta `target=\"_blank\"`\n"
    guia += "3. El cliente de email bloquea enlaces\n\n"
    guia += "**Soluciones:**\n"
    guia += "1. Verifica que las URLs tengan `http://` o `https://`\n"
    guia += "2. Usa `verificar_enlaces.py` para verificar todos los enlaces\n"
    guia += "3. Prueba los enlaces en un navegador primero\n"
    guia += "4. Asegúrate de incluir `rel=\"noopener noreferrer\"`\n\n"
    
    guia += "### Los botones no funcionan en Outlook\n\n"
    guia += "**Síntomas:**\n"
    guia += "- Los botones no son clicables en Outlook\n\n"
    guia += "**Causas posibles:**\n"
    guia += "1. Falta VML roundrect para Outlook\n\n"
    guia += "**Soluciones:**\n"
    guia += "1. Usa plantillas que incluyan VML para botones\n"
    guia += "2. Verifica que tenga `<!--[if mso]>` con VML roundrect\n"
    guia += "3. Usa la versión completa de la plantilla\n\n"
    
    guia += "## ⚡ Problemas de Rendimiento\n\n"
    
    guia += "### La firma es muy grande\n\n"
    guia += "**Síntomas:**\n"
    guia += "- El archivo HTML es muy pesado\n"
    guia += "- Los emails tardan en cargar\n\n"
    guia += "**Causas posibles:**\n"
    guia += "1. Imágenes muy grandes\n"
    guia += "2. Código HTML no optimizado\n"
    guia += "3. Espacios y comentarios innecesarios\n\n"
    guia += "**Soluciones:**\n"
    guia += "1. Optimiza las imágenes antes de usar\n"
    guia += "2. Usa `optimizar_firma.py` para reducir tamaño\n"
    guia += "3. Elimina comentarios y espacios innecesarios\n"
    guia += "4. Usa versiones compactas o simples\n\n"
    
    guia += "## 🐍 Problemas con Scripts\n\n"
    
    guia += "### Error: Python no encontrado\n\n"
    guia += "**Síntomas:**\n"
    guia += "- `python: command not found`\n\n"
    guia += "**Soluciones:**\n"
    guia += "1. Instala Python 3.6 o superior\n"
    guia += "2. Usa `python3` en lugar de `python`\n"
    guia += "3. Verifica la instalación con `python --version`\n\n"
    
    guia += "### Error: Módulo no encontrado\n\n"
    guia += "**Síntomas:**\n"
    guia += "- `ModuleNotFoundError`\n\n"
    guia += "**Soluciones:**\n"
    guia += "1. Los scripts usan solo librerías estándar\n"
    guia += "2. Verifica que estés en el directorio correcto\n"
    guia += "3. Asegúrate de tener Python 3.6+\n\n"
    
    guia += "### El script no genera el archivo esperado\n\n"
    guia += "**Síntomas:**\n"
    guia += "- El script ejecuta pero no crea archivos\n\n"
    guia += "**Soluciones:**\n"
    guia += "1. Verifica permisos de escritura en el directorio\n"
    guia += "2. Revisa los mensajes de error del script\n"
    guia += "3. Asegúrate de estar en el directorio correcto\n"
    guia += "4. Verifica que los archivos fuente existan\n\n"
    
    guia += "## 🔍 Herramientas de Diagnóstico\n\n"
    guia += "### Validación\n\n"
    guia += "1. **`validar_firma.py`** - Valida una plantilla individual\n"
    guia += "2. **`validar_todas.py`** - Valida todas las plantillas\n"
    guia += "3. **`verificar_compatibilidad.py`** - Verifica compatibilidad por cliente\n"
    guia += "4. **`verificar_enlaces.py`** - Verifica que todos los enlaces funcionen\n\n"
    
    guia += "### Análisis\n\n"
    guia += "1. **`analizar_rendimiento.py`** - Analiza rendimiento y tamaño\n"
    guia += "2. **`test_compatibilidad.html`** - Testing visual en navegador\n"
    guia += "3. **`comparar_versiones.py`** - Compara diferentes versiones\n\n"
    
    guia += "### Limpieza\n\n"
    guia += "1. **`limpiar_plantillas.py`** - Limpia y normaliza plantillas\n"
    guia += "2. **`optimizar_firma.py`** - Optimiza tamaño y estructura\n\n"
    
    guia += "## ⚡ Solución Rápida\n\n"
    guia += "### Checklist de Verificación Rápida\n\n"
    guia += "Si tu firma no funciona, verifica:\n\n"
    guia += "1. ✅ Todos los placeholders reemplazados\n"
    guia += "2. ✅ Estructura HTML correcta (usa `validar_firma.py`)\n"
    guia += "3. ✅ Enlaces funcionan (usa `verificar_enlaces.py`)\n"
    guia += "4. ✅ Compatible con tu cliente de email (usa `verificar_compatibilidad.py`)\n"
    guia += "5. ✅ Probado en el cliente de email real\n"
    guia += "6. ✅ Probado en móvil\n"
    guia += "7. ✅ Tamaño razonable (<50KB)\n\n"
    
    guia += "### Comandos Rápidos\n\n"
    guia += "```bash\n"
    guia += "# Validar una plantilla\n"
    guia += "python validar_firma.py firma_ejemplo.html\n\n"
    guia += "# Verificar compatibilidad\n"
    guia += "python verificar_compatibilidad.py firma_ejemplo.html\n\n"
    guia += "# Verificar enlaces\n"
    guia += "python verificar_enlaces.py firma_ejemplo.html\n\n"
    guia += "# Optimizar\n"
    guia += "python optimizar_firma.py firma_ejemplo.html\n\n"
    guia += "# Personalizar\n"
    guia += "python personalizar_firma.py\n"
    guia += "```\n\n"
    
    guia += "## 📚 Recursos Adicionales\n\n"
    guia += "- `README.md` - Documentación principal\n"
    guia += "- `MANUAL_USUARIO.md` - Manual completo de usuario\n"
    guia += "- `FAQs.md` - Preguntas frecuentes\n"
    guia += "- `CHECKLIST_FINAL.md` - Checklist antes de usar\n"
    guia += "- [Can I Email](https://www.caniemail.com/) - Compatibilidad CSS\n"
    guia += "- [Email on Acid](https://www.emailonacid.com/) - Testing de emails\n\n"
    
    guia += "---\n\n"
    guia += f"*Guía generada el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    guia += "*Para actualizar, ejecuta `crear_guia_troubleshooting.py`*\n"
    
    return guia

def main():
    """Función principal"""
    print("=" * 70)
    print("🔧 Creador de Guía de Troubleshooting")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Generando guía de troubleshooting...")
    print()
    
    guia = generar_guia_troubleshooting()
    
    # Guardar
    archivo_guia = directorio_actual / "GUIA_TROUBLESHOOTING.md"
    with open(archivo_guia, 'w', encoding='utf-8') as f:
        f.write(guia)
    
    print("=" * 70)
    print("✅ Guía de troubleshooting generada exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_guia.name}")
    print()
    print("💡 La guía incluye:")
    print("   - Problemas de visualización")
    print("   - Problemas de compatibilidad")
    print("   - Problemas de personalización")
    print("   - Problemas de enlaces")
    print("   - Problemas de rendimiento")
    print("   - Problemas con scripts")
    print("   - Herramientas de diagnóstico")
    print("   - Solución rápida")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()






