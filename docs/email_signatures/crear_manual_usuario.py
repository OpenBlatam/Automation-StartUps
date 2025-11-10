#!/usr/bin/env python3
"""
Creador de Manual de Usuario
Genera un manual de usuario completo y detallado
"""

import os
from pathlib import Path
from datetime import datetime

def generar_manual_usuario() -> str:
    """Genera el manual de usuario completo"""
    manual = "# 📖 Manual de Usuario - Firmas de Email\n\n"
    manual += f"**Versión:** 4.1 | **Fecha:** {datetime.now().strftime('%d de %B de %Y')}\n\n"
    
    manual += "## 📋 Tabla de Contenidos\n\n"
    manual += "1. [Introducción](#introducción)\n"
    manual += "2. [Instalación y Configuración](#instalación-y-configuración)\n"
    manual += "3. [Uso Básico](#uso-básico)\n"
    manual += "4. [Uso Avanzado](#uso-avanzado)\n"
    manual += "5. [Herramientas Disponibles](#herramientas-disponibles)\n"
    manual += "6. [Personalización](#personalización)\n"
    manual += "7. [Validación y Testing](#validación-y-testing)\n"
    manual += "8. [Solución de Problemas](#solución-de-problemas)\n"
    manual += "9. [Preguntas Frecuentes](#preguntas-frecuentes)\n"
    manual += "10. [Apéndices](#apéndices)\n\n"
    
    manual += "## 🎯 Introducción\n\n"
    manual += "### ¿Qué es este proyecto?\n\n"
    manual += "Este proyecto proporciona una solución completa para crear, personalizar y gestionar firmas de email profesionales. Incluye más de 50 plantillas HTML optimizadas para diferentes industrias, roles y estilos.\n\n"
    
    manual += "### ¿Para quién es?\n\n"
    manual += "- **Individuos:** Profesionales que quieren una firma de email profesional\n"
    manual += "- **Equipos:** Empresas que necesitan firmas estandarizadas\n"
    manual += "- **Agencias:** Creadores de firmas para clientes\n"
    manual += "- **Desarrolladores:** Integración en sistemas de email\n\n"
    
    manual += "### Características Principales\n\n"
    manual += "- ✅ Más de 50 plantillas profesionales\n"
    manual += "- ✅ Compatible con todos los clientes de email\n"
    manual += "- ✅ Diseño responsive para móviles\n"
    manual += "- ✅ Herramientas de personalización automática\n"
    manual += "- ✅ Validación y testing integrados\n"
    manual += "- ✅ Documentación completa\n\n"
    
    manual += "## ⚙️ Instalación y Configuración\n\n"
    manual += "### Requisitos\n\n"
    manual += "- Python 3.6 o superior (para scripts)\n"
    manual += "- Navegador moderno (para herramientas HTML)\n"
    manual += "- Editor de texto (para edición manual)\n\n"
    
    manual += "### Instalación\n\n"
    manual += "1. Descarga o clona el proyecto\n"
    manual += "2. Navega al directorio del proyecto\n"
    manual += "3. No se requieren dependencias adicionales\n"
    manual += "4. ¡Listo para usar!\n\n"
    
    manual += "## 🚀 Uso Básico\n\n"
    manual += "### Método 1: Personalización Manual\n\n"
    manual += "1. Abre una plantilla HTML en tu editor\n"
    manual += "2. Busca y reemplaza los placeholders:\n"
    manual += "   - `[Tu Nombre]` → Tu nombre completo\n"
    manual += "   - `[tu-email@ejemplo.com]` → Tu email\n"
    manual += "   - `[URL_WEBSITE]` → Tu sitio web\n"
    manual += "   - Y otros placeholders según corresponda\n"
    manual += "3. Guarda el archivo\n"
    manual += "4. Copia el HTML completo\n"
    manual += "5. Pégalo en tu cliente de email\n\n"
    
    manual += "### Método 2: Personalización Automática\n\n"
    manual += "1. Ejecuta `python personalizar_firma.py`\n"
    manual += "2. Selecciona la plantilla\n"
    manual += "3. Ingresa tus datos cuando se solicite\n"
    manual += "4. El script generará la firma personalizada\n"
    manual += "5. Copia y usa el resultado\n\n"
    
    manual += "### Método 3: Generador Interactivo\n\n"
    manual += "1. Abre `generador_interactivo.html` en tu navegador\n"
    manual += "2. Completa el formulario\n"
    manual += "3. Previsualiza en tiempo real\n"
    manual += "4. Descarga el HTML final\n\n"
    
    manual += "## 🔧 Uso Avanzado\n\n"
    manual += "### Procesamiento por Lotes\n\n"
    manual += "1. Crea un archivo `configuraciones_lote.json`\n"
    manual += "2. Define los datos de cada usuario\n"
    manual += "3. Ejecuta `python procesar_lote.py`\n"
    manual += "4. Las firmas se generarán automáticamente\n\n"
    
    manual += "### Validación Completa\n\n"
    manual += "1. Ejecuta `python validar_todas.py`\n"
    manual += "2. Revisa el reporte generado\n"
    manual += "3. Corrige problemas encontrados\n\n"
    
    manual += "### Optimización\n\n"
    manual += "1. Ejecuta `python optimizar_firma.py`\n"
    manual += "2. Las plantillas se optimizarán automáticamente\n"
    manual += "3. Revisa las versiones optimizadas\n\n"
    
    manual += "## 🛠️ Herramientas Disponibles\n\n"
    manual += "### Categorías de Herramientas\n\n"
    manual += "#### Personalización\n"
    manual += "- `personalizar_firma.py` - Personalización básica\n"
    manual += "- `personalizar_firma_avanzado.py` - Personalización avanzada\n"
    manual += "- `procesar_lote.py` - Procesamiento por lotes\n"
    manual += "- `generar_variaciones.py` - Generador de variaciones\n\n"
    
    manual += "#### Validación\n"
    manual += "- `validar_firma.py` - Validación individual\n"
    manual += "- `validar_todas.py` - Validación completa\n"
    manual += "- `verificar_compatibilidad.py` - Verificación de compatibilidad\n"
    manual += "- `verificar_enlaces.py` - Verificación de enlaces\n\n"
    
    manual += "#### Análisis\n"
    manual += "- `analizar_rendimiento.py` - Análisis de rendimiento\n"
    manual += "- `analizar_estadisticas_avanzadas.py` - Estadísticas avanzadas\n"
    manual += "- `analizar_uso_placeholders.py` - Análisis de placeholders\n"
    manual += "- `estadisticas_proyecto.py` - Estadísticas del proyecto\n\n"
    
    manual += "#### Optimización\n"
    manual += "- `optimizar_firma.py` - Optimización automática\n"
    manual += "- `limpiar_plantillas.py` - Limpieza y normalización\n"
    manual += "- `comparar_versiones.py` - Comparación de versiones\n\n"
    
    manual += "#### Conversión\n"
    manual += "- `converter_formatos.py` - Conversión entre formatos\n"
    manual += "- `exportar_firmas.py` - Exportación a múltiples formatos\n"
    manual += "- `exportar_paquete.py` - Exportación de paquetes ZIP\n\n"
    
    manual += "#### Utilidades\n"
    manual += "- `buscar_plantilla.py` - Buscador de plantillas\n"
    manual += "- `cambiar_colores.py` - Cambiador de colores\n"
    manual += "- `generar_qr.py` - Generador de QR codes\n"
    manual += "- `backup_restore.py` - Backup y restore\n\n"
    
    manual += "#### Documentación\n"
    manual += "- `generar_documentacion.py` - Documentación automática\n"
    manual += "- `generar_reporte_completo.py` - Reporte completo\n"
    manual += "- `crear_resumen_ejecutivo.py` - Resumen ejecutivo\n"
    manual += "- `crear_guia_rapida_plantillas.py` - Guía rápida\n"
    manual += "- `crear_matriz_decision.py` - Matriz de decisión\n"
    manual += "- `generar_dashboard.py` - Dashboard HTML\n"
    manual += "- `crear_guia_completa.py` - Guía completa\n\n"
    
    manual += "## 🎨 Personalización\n\n"
    manual += "### Placeholders Comunes\n\n"
    manual += "| Placeholder | Descripción | Ejemplo |\n"
    manual += "|-------------|-------------|----------|\n"
    manual += "| `[Tu Nombre]` | Nombre completo | Juan Pérez |\n"
    manual += "| `[Tu Cargo]` | Posición o cargo | Director de Marketing |\n"
    manual += "| `[tu-email@ejemplo.com]` | Dirección de email | juan@empresa.com |\n"
    manual += "| `[URL_WEBSITE]` | Sitio web | https://www.empresa.com |\n"
    manual += "| `[URL_LINKEDIN]` | Perfil de LinkedIn | https://linkedin.com/in/juan |\n"
    manual += "| `[URL_TWITTER]` | Perfil de Twitter | https://twitter.com/juan |\n\n"
    
    manual += "### Agregar Logos\n\n"
    manual += "1. Sube tu logo a un servidor web\n"
    manual += "2. Obtén la URL absoluta del logo\n"
    manual += "3. Reemplaza `[URL_LOGO]` con la URL\n"
    manual += "4. Ajusta el tamaño si es necesario\n\n"
    
    manual += "### Cambiar Colores\n\n"
    manual += "1. Usa `cambiar_colores.py` para cambiar esquemas\n"
    manual += "2. O edita manualmente los códigos hexadecimales\n"
    manual += "3. Usa códigos completos (#RRGGBB)\n\n"
    
    manual += "## ✅ Validación y Testing\n\n"
    manual += "### Checklist de Validación\n\n"
    manual += "Antes de usar tu firma en producción:\n\n"
    manual += "- [ ] Todos los placeholders reemplazados\n"
    manual += "- [ ] Enlaces funcionan correctamente\n"
    manual += "- [ ] Probado en Gmail (Web y App)\n"
    manual += "- [ ] Probado en Outlook (Desktop y Web)\n"
    manual += "- [ ] Probado en Apple Mail\n"
    manual += "- [ ] Probado en dispositivo móvil\n"
    manual += "- [ ] Validación ejecutada sin errores críticos\n"
    manual += "- [ ] Tamaño del archivo razonable (<50KB)\n\n"
    
    manual += "### Herramientas de Testing\n\n"
    manual += "1. **test_compatibilidad.html** - Testing básico en navegador\n"
    manual += "2. **validar_firma.py** - Validación automática\n"
    manual += "3. **Envío de prueba** - Envía email a ti mismo\n\n"
    
    manual += "## 🔧 Solución de Problemas\n\n"
    manual += "### Problema: La firma no se ve en Outlook\n\n"
    manual += "**Causa:** Falta soporte VML/MSO\n"
    manual += "**Solución:**\n"
    manual += "1. Verifica que la plantilla tenga `xmlns:v=` y comentarios MSO\n"
    manual += "2. Usa `verificar_compatibilidad.py` para diagnosticar\n"
    manual += "3. Considera usar una versión simple si el problema persiste\n\n"
    
    manual += "### Problema: Los colores no se ven correctamente\n\n"
    manual += "**Causa:** Códigos de color incorrectos\n"
    manual += "**Solución:**\n"
    manual += "1. Usa códigos hexadecimales completos (#RRGGBB)\n"
    manual += "2. Evita colores con transparencia\n"
    manual += "3. Prueba en diferentes clientes\n\n"
    
    manual += "### Problema: El diseño se rompe en móvil\n\n"
    manual += "**Causa:** Falta diseño responsive\n"
    manual += "**Solución:**\n"
    manual += "1. Verifica que tenga media queries\n"
    manual += "2. Asegúrate de usar clases `mobile-stack`\n"
    manual += "3. Prueba en un dispositivo real\n\n"
    
    manual += "### Problema: Los botones no funcionan\n\n"
    manual += "**Causa:** Falta VML roundrect para Outlook\n"
    manual += "**Solución:**\n"
    manual += "1. Verifica que los botones tengan VML\n"
    manual += "2. Usa la versión completa de la plantilla\n"
    manual += "3. Prueba en diferentes clientes\n\n"
    
    manual += "## ❓ Preguntas Frecuentes\n\n"
    manual += "### ¿Puedo usar estas plantillas comercialmente?\n\n"
    manual += "Sí, las plantillas están diseñadas para uso comercial. Personaliza con tu información y úsalas libremente.\n\n"
    
    manual += "### ¿Necesito saber programar?\n\n"
    manual += "No necesariamente. Puedes usar el generador interactivo HTML o los scripts Python que guían el proceso paso a paso.\n\n"
    
    manual += "### ¿Funciona con todos los clientes de email?\n\n"
    manual += "Las plantillas están optimizadas para compatibilidad máxima con Gmail, Outlook, Apple Mail, Yahoo Mail y otros clientes principales.\n\n"
    
    manual += "### ¿Puedo modificar las plantillas?\n\n"
    manual += "Sí, puedes modificar las plantillas libremente. Solo asegúrate de mantener la estructura de tablas para compatibilidad.\n\n"
    
    manual += "### ¿Cómo agrego mi logo?\n\n"
    manual += "1. Sube tu logo a un servidor web\n"
    manual += "2. Obtén la URL absoluta\n"
    manual += "3. Reemplaza el placeholder `[URL_LOGO]` con la URL\n"
    manual += "4. Ajusta el tamaño en el atributo `width` si es necesario\n\n"
    
    manual += "## 📚 Apéndices\n\n"
    manual += "### Recursos Adicionales\n\n"
    manual += "- `README.md` - Documentación principal\n"
    manual += "- `INICIO_RAPIDO.md` - Guía de inicio rápido\n"
    manual += "- `GUIA_COMPLETA.md` - Guía completa\n"
    manual += "- `FAQs.md` - Preguntas frecuentes\n"
    manual += "- `CHECKLIST_FINAL.md` - Checklist antes de usar\n"
    manual += "- `MATRIZ_DECISION.md` - Matriz de decisión\n\n"
    
    manual += "### Enlaces Útiles\n\n"
    manual += "- [Can I Email](https://www.caniemail.com/) - Compatibilidad de CSS\n"
    manual += "- [Email on Acid](https://www.emailonacid.com/) - Testing de emails\n"
    manual += "- [Litmus](https://www.litmus.com/) - Testing y previews\n\n"
    
    manual += "### Soporte\n\n"
    manual += "Si tienes problemas o preguntas:\n\n"
    manual += "1. Revisa la documentación disponible\n"
    manual += "2. Consulta las FAQs\n"
    manual += "3. Usa las herramientas de validación para diagnosticar\n"
    manual += "4. Revisa los ejemplos de uso\n\n"
    
    manual += "---\n\n"
    manual += f"*Manual generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    manual += "*Para actualizar, ejecuta `crear_manual_usuario.py`*\n"
    
    return manual

def main():
    """Función principal"""
    print("=" * 70)
    print("📖 Creador de Manual de Usuario")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Generando manual de usuario...")
    print()
    
    manual = generar_manual_usuario()
    
    # Guardar
    archivo_manual = directorio_actual / "MANUAL_USUARIO.md"
    with open(archivo_manual, 'w', encoding='utf-8') as f:
        f.write(manual)
    
    print("=" * 70)
    print("✅ Manual de usuario generado exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_manual.name}")
    print()
    print("💡 El manual incluye:")
    print("   - Introducción y características")
    print("   - Instalación y configuración")
    print("   - Uso básico y avanzado")
    print("   - Todas las herramientas")
    print("   - Personalización detallada")
    print("   - Validación y testing")
    print("   - Solución de problemas")
    print("   - Preguntas frecuentes")
    print("   - Apéndices y recursos")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()






