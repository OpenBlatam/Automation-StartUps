#!/usr/bin/env python3
"""
Creador de Guía Completa
Genera una guía completa y exhaustiva del proyecto
"""

import os
from pathlib import Path
from datetime import datetime

def generar_guia_completa(directorio: Path) -> str:
    """Genera la guía completa"""
    guia = "# 📚 Guía Completa - Firmas de Email\n\n"
    guia += f"**Última actualización:** {datetime.now().strftime('%d de %B de %Y')}\n\n"
    
    guia += "## 🎯 Introducción\n\n"
    guia += "Esta guía completa te ayudará a entender y utilizar todo el proyecto de firmas de email profesional.\n\n"
    
    guia += "## 📋 Tabla de Contenidos\n\n"
    guia += "1. [Inicio Rápido](#inicio-rápido)\n"
    guia += "2. [Selección de Plantillas](#selección-de-plantillas)\n"
    guia += "3. [Personalización](#personalización)\n"
    guia += "4. [Herramientas Disponibles](#herramientas-disponibles)\n"
    guia += "5. [Validación y Testing](#validación-y-testing)\n"
    guia += "6. [Mejores Prácticas](#mejores-prácticas)\n"
    guia += "7. [Solución de Problemas](#solución-de-problemas)\n"
    guia += "8. [Recursos Adicionales](#recursos-adicionales)\n\n"
    
    guia += "## 🚀 Inicio Rápido\n\n"
    guia += "### Paso 1: Seleccionar Plantilla\n"
    guia += "1. Revisa las plantillas disponibles en el directorio\n"
    guia += "2. Usa `buscar_plantilla.py` para encontrar por criterios\n"
    guia += "3. Consulta `GUIA_RAPIDA_PLANTILLAS.md` para recomendaciones\n\n"
    
    guia += "### Paso 2: Personalizar\n"
    guia += "1. Abre la plantilla seleccionada\n"
    guia += "2. Reemplaza los placeholders `[Tu Nombre]`, `[tu-email@ejemplo.com]`, etc.\n"
    guia += "3. O usa `personalizar_firma.py` para automatizar\n\n"
    
    guia += "### Paso 3: Validar\n"
    guia += "1. Ejecuta `validar_firma.py` en tu plantilla\n"
    guia += "2. Revisa el reporte de validación\n"
    guia += "3. Corrige cualquier problema encontrado\n\n"
    
    guia += "### Paso 4: Probar\n"
    guia += "1. Abre `test_compatibilidad.html` en tu navegador\n"
    guia += "2. Pega tu HTML y prueba\n"
    guia += "3. Envía un email de prueba a ti mismo\n\n"
    
    guia += "### Paso 5: Implementar\n"
    guia += "1. Copia el HTML final\n"
    guia += "2. Pégalo en la configuración de tu cliente de email\n"
    guia += "3. Guarda y envía un email de prueba\n\n"
    
    guia += "## 📧 Selección de Plantillas\n\n"
    guia += "### Por Industria\n"
    guia += "- **Salud:** `firma_salud.html`\n"
    guia += "- **Educación:** `firma_educacion.html`\n"
    guia += "- **Finanzas:** `firma_finanzas.html`\n"
    guia += "- **Tecnología:** `firma_tecnologia.html`\n"
    guia += "- **Ventas:** `firma_ventas.html`\n"
    guia += "- **RRHH:** `firma_recursos_humanos.html`\n"
    guia += "- **Marketing:** `firma_marketing.html`\n"
    guia += "- **Legal:** `firma_legal.html`\n"
    guia += "- **Diseño:** `firma_diseno.html`\n"
    guia += "- **Consultoría:** `firma_consultoria.html`\n"
    guia += "- **Y muchas más...**\n\n"
    
    guia += "### Por Estilo\n"
    guia += "- **Completa:** Todas las características\n"
    guia += "- **Compacta:** Diseño horizontal, información esencial\n"
    guia += "- **Simple:** HTML básico, máxima compatibilidad\n"
    guia += "- **Minimalista:** Diseño limpio, mucho espacio\n"
    guia += "- **Premium:** Badges, gradientes, destacados\n\n"
    
    guia += "## 🛠️ Personalización\n\n"
    guia += "### Método Manual\n"
    guia += "1. Abre la plantilla en un editor de texto\n"
    guia += "2. Busca y reemplaza todos los placeholders\n"
    guia += "3. Guarda el archivo\n\n"
    
    guia += "### Método Automático\n"
    guia += "1. Ejecuta `personalizar_firma.py`\n"
    guia += "2. Sigue las instrucciones\n"
    guia += "3. Revisa el resultado\n\n"
    
    guia += "### Método Avanzado\n"
    guia += "1. Usa `personalizar_firma_avanzado.py`\n"
    guia += "2. Crea un archivo JSON con tu configuración\n"
    guia += "3. Procesa múltiples plantillas a la vez\n\n"
    
    guia += "## 🔧 Herramientas Disponibles\n\n"
    guia += "### Personalización\n"
    guia += "- `personalizar_firma.py` - Personalización básica\n"
    guia += "- `personalizar_firma_avanzado.py` - Personalización avanzada con validación\n"
    guia += "- `procesar_lote.py` - Procesamiento por lotes\n\n"
    
    guia += "### Validación y Análisis\n"
    guia += "- `validar_firma.py` - Validación de una plantilla\n"
    guia += "- `validar_todas.py` - Validación de todas las plantillas\n"
    guia += "- `analizar_rendimiento.py` - Análisis de rendimiento\n"
    guia += "- `verificar_compatibilidad.py` - Verificación de compatibilidad\n"
    guia += "- `verificar_enlaces.py` - Verificación de enlaces\n\n"
    
    guia += "### Optimización\n"
    guia += "- `optimizar_firma.py` - Optimización automática\n"
    guia += "- `limpiar_plantillas.py` - Limpieza y normalización\n\n"
    
    guia += "### Conversión y Exportación\n"
    guia += "- `converter_formatos.py` - Conversión entre formatos\n"
    guia += "- `exportar_firmas.py` - Exportación a múltiples formatos\n"
    guia += "- `exportar_paquete.py` - Exportación de paquetes ZIP\n\n"
    
    guia += "### Análisis y Reportes\n"
    guia += "- `estadisticas_proyecto.py` - Estadísticas del proyecto\n"
    guia += "- `analizar_estadisticas_avanzadas.py` - Análisis avanzado\n"
    guia += "- `generar_reporte_completo.py` - Reporte completo\n"
    guia += "- `generar_documentacion.py` - Documentación automática\n\n"
    
    guia += "### Utilidades\n"
    guia += "- `buscar_plantilla.py` - Buscador de plantillas\n"
    guia += "- `comparar_versiones.py` - Comparador de versiones\n"
    guia += "- `generar_variaciones.py` - Generador de variaciones\n"
    guia += "- `cambiar_colores.py` - Cambiador de colores\n"
    guia += "- `generar_qr.py` - Generador de QR codes\n"
    guia += "- `backup_restore.py` - Backup y restore\n\n"
    
    guia += "## ✅ Validación y Testing\n\n"
    guia += "### Checklist de Validación\n"
    guia += "- [ ] Estructura HTML correcta\n"
    guia += "- [ ] Todos los placeholders reemplazados\n"
    guia += "- [ ] Enlaces funcionan correctamente\n"
    guia += "- [ ] Compatible con Outlook\n"
    guia += "- [ ] Responsive en móvil\n"
    guia += "- [ ] Accesibilidad (ARIA, alt text)\n"
    guia += "- [ ] Sin JavaScript\n"
    guia += "- [ ] Estilos inline presentes\n\n"
    
    guia += "### Testing\n"
    guia += "1. Usa `test_compatibilidad.html` para pruebas básicas\n"
    guia += "2. Envía emails de prueba a diferentes clientes\n"
    guia += "3. Prueba en dispositivos móviles\n"
    guia += "4. Verifica en diferentes navegadores\n\n"
    
    guia += "## 💡 Mejores Prácticas\n\n"
    guia += "### Diseño\n"
    guia += "- Usa tablas para estructura (no divs)\n"
    guia += "- Mantén el ancho máximo en 600px\n"
    guia += "- Usa estilos inline\n"
    guia += "- Evita JavaScript y CSS externo\n"
    guia += "- Prueba en múltiples clientes\n\n"
    
    guia += "### Contenido\n"
    guia += "- Mantén el mensaje claro y conciso\n"
    guia += "- Incluye información de contacto esencial\n"
    guia += "- Agrega enlaces a redes sociales relevantes\n"
    guia += "- Usa CTAs cuando sea apropiado\n\n"
    
    guia += "### Rendimiento\n"
    guia += "- Optimiza imágenes (tamaño y formato)\n"
    guia += "- Minimiza el tamaño del HTML\n"
    guia += "- Usa URLs absolutas para imágenes\n"
    guia += "- Evita recursos externos bloqueantes\n\n"
    
    guia += "## 🔧 Solución de Problemas\n\n"
    guia += "### Problemas Comunes\n\n"
    guia += "**Problema:** La firma no se ve bien en Outlook\n"
    guia += "**Solución:** Verifica que tenga VML y comentarios MSO\n\n"
    
    guia += "**Problema:** Los colores no se ven correctamente\n"
    guia += "**Solución:** Usa códigos hexadecimales completos (#RRGGBB)\n\n"
    
    guia += "**Problema:** Los botones no funcionan\n"
    guia += "**Solución:** Verifica que tengan VML roundrect para Outlook\n\n"
    
    guia += "**Problema:** El diseño se rompe en móvil\n"
    guia += "**Solución:** Verifica que tenga media queries y clases mobile-stack\n\n"
    
    guia += "## 📚 Recursos Adicionales\n\n"
    guia += "- `README.md` - Documentación principal\n"
    guia += "- `INICIO_RAPIDO.md` - Guía de inicio rápido\n"
    guia += "- `GUIA_PERSONALIZACION_AVANZADA.md` - Personalización avanzada\n"
    guia += "- `EJEMPLOS_USO.md` - Ejemplos prácticos\n"
    guia += "- `PLANTILLAS_POR_INDUSTRIA.md` - Guía por industria\n"
    guia += "- `FAQs.md` - Preguntas frecuentes\n"
    guia += "- `CHECKLIST_FINAL.md` - Checklist antes de usar\n"
    guia += "- `MATRIZ_DECISION.md` - Matriz de decisión\n\n"
    
    guia += "## 🎓 Aprende Más\n\n"
    guia += "### Conceptos Clave\n"
    guia += "- **HTML para Email:** Diferente a HTML web\n"
    guia += "- **Tablas:** Estructura principal en emails\n"
    guia += "- **Estilos Inline:** Necesarios para compatibilidad\n"
    guia += "- **VML/MSO:** Para compatibilidad con Outlook\n"
    guia += "- **Media Queries:** Para diseño responsive\n\n"
    
    guia += "### Recursos Externos\n"
    guia += "- [Can I Email](https://www.caniemail.com/) - Compatibilidad de CSS\n"
    guia += "- [Email on Acid](https://www.emailonacid.com/) - Testing de emails\n"
    guia += "- [Litmus](https://www.litmus.com/) - Testing y previews\n\n"
    
    guia += "---\n\n"
    guia += f"*Guía generada el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    guia += "*Para actualizar, ejecuta `crear_guia_completa.py`*\n"
    
    return guia

def main():
    """Función principal"""
    print("=" * 70)
    print("📚 Creador de Guía Completa")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Generando guía completa...")
    print()
    
    guia = generar_guia_completa(directorio_actual)
    
    # Guardar
    archivo_guia = directorio_actual / "GUIA_COMPLETA.md"
    with open(archivo_guia, 'w', encoding='utf-8') as f:
        f.write(guia)
    
    print("=" * 70)
    print("✅ Guía completa generada exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_guia.name}")
    print()
    print("💡 La guía incluye:")
    print("   - Inicio rápido paso a paso")
    print("   - Selección de plantillas")
    print("   - Personalización")
    print("   - Todas las herramientas")
    print("   - Validación y testing")
    print("   - Mejores prácticas")
    print("   - Solución de problemas")
    print("   - Recursos adicionales")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()






