#!/usr/bin/env python3
"""
Creador de Cheatsheet
Genera una hoja de referencia rápida con comandos y tips
"""

import os
from pathlib import Path
from datetime import datetime

def generar_cheatsheet() -> str:
    """Genera la cheatsheet"""
    cheatsheet = "# 📝 Cheatsheet - Firmas de Email\n\n"
    cheatsheet += f"**Versión:** 4.2 | **Fecha:** {datetime.now().strftime('%d de %B de %Y')}\n\n"
    cheatsheet += "Hoja de referencia rápida con los comandos y tips más útiles.\n\n"
    
    cheatsheet += "## 🚀 Comandos Rápidos\n\n"
    
    cheatsheet += "### Personalización\n\n"
    cheatsheet += "```bash\n"
    cheatsheet += "# Personalización básica\n"
    cheatsheet += "python personalizar_firma.py\n\n"
    cheatsheet += "# Personalización avanzada\n"
    cheatsheet += "python personalizar_firma_avanzado.py\n\n"
    cheatsheet += "# Procesamiento por lotes\n"
    cheatsheet += "python procesar_lote.py\n\n"
    cheatsheet += "# Generar variaciones\n"
    cheatsheet += "python generar_variaciones.py\n"
    cheatsheet += "```\n\n"
    
    cheatsheet += "### Validación\n\n"
    cheatsheet += "```bash\n"
    cheatsheet += "# Validar una plantilla\n"
    cheatsheet += "python validar_firma.py firma_ejemplo.html\n\n"
    cheatsheet += "# Validar todas\n"
    cheatsheet += "python validar_todas.py\n\n"
    cheatsheet += "# Verificar compatibilidad\n"
    cheatsheet += "python verificar_compatibilidad.py firma_ejemplo.html\n\n"
    cheatsheet += "# Verificar enlaces\n"
    cheatsheet += "python verificar_enlaces.py firma_ejemplo.html\n"
    cheatsheet += "```\n\n"
    
    cheatsheet += "### Optimización\n\n"
    cheatsheet += "```bash\n"
    cheatsheet += "# Optimizar plantilla\n"
    cheatsheet += "python optimizar_firma.py firma_ejemplo.html\n\n"
    cheatsheet += "# Limpiar plantillas\n"
    cheatsheet += "python limpiar_plantillas.py\n"
    cheatsheet += "```\n\n"
    
    cheatsheet += "### Análisis\n\n"
    cheatsheet += "```bash\n"
    cheatsheet += "# Analizar rendimiento\n"
    cheatsheet += "python analizar_rendimiento.py\n\n"
    cheatsheet += "# Estadísticas del proyecto\n"
    cheatsheet += "python estadisticas_proyecto.py\n\n"
    cheatsheet += "# Estadísticas avanzadas\n"
    cheatsheet += "python analizar_estadisticas_avanzadas.py\n"
    cheatsheet += "```\n\n"
    
    cheatsheet += "### Conversión y Exportación\n\n"
    cheatsheet += "```bash\n"
    cheatsheet += "# Convertir formatos\n"
    cheatsheet += "python converter_formatos.py\n\n"
    cheatsheet += "# Exportar firmas\n"
    cheatsheet += "python exportar_firmas.py\n\n"
    cheatsheet += "# Exportar paquete\n"
    cheatsheet += "python exportar_paquete.py\n"
    cheatsheet += "```\n\n"
    
    cheatsheet += "### Utilidades\n\n"
    cheatsheet += "```bash\n"
    cheatsheet += "# Buscar plantilla\n"
    cheatsheet += "python buscar_plantilla.py\n\n"
    cheatsheet += "# Cambiar colores\n"
    cheatsheet += "python cambiar_colores.py\n\n"
    cheatsheet += "# Generar QR\n"
    cheatsheet += "python generar_qr.py\n\n"
    cheatsheet += "# Backup/Restore\n"
    cheatsheet += "python backup_restore.py\n"
    cheatsheet += "```\n\n"
    
    cheatsheet += "### Documentación\n\n"
    cheatsheet += "```bash\n"
    cheatsheet += "# Generar documentación\n"
    cheatsheet += "python generar_documentacion.py\n\n"
    cheatsheet += "# Reporte completo\n"
    cheatsheet += "python generar_reporte_completo.py\n\n"
    cheatsheet += "# Dashboard\n"
    cheatsheet += "python generar_dashboard.py\n\n"
    cheatsheet += "# Guía completa\n"
    cheatsheet += "python crear_guia_completa.py\n\n"
    cheatsheet += "# Manual de usuario\n"
    cheatsheet += "python crear_manual_usuario.py\n\n"
    cheatsheet += "# Índice completo\n"
    cheatsheet += "python generar_indice_completo.py\n"
    cheatsheet += "```\n\n"
    
    cheatsheet += "## 🎯 Placeholders Comunes\n\n"
    cheatsheet += "| Placeholder | Reemplazar con |\n"
    cheatsheet += "|-------------|----------------|\n"
    cheatsheet += "| `[Tu Nombre]` | Tu nombre completo |\n"
    cheatsheet += "| `[Tu Cargo]` | Tu posición o cargo |\n"
    cheatsheet += "| `[tu-email@ejemplo.com]` | Tu email |\n"
    cheatsheet += "| `[URL_WEBSITE]` | Tu sitio web |\n"
    cheatsheet += "| `[URL_LINKEDIN]` | Tu perfil de LinkedIn |\n"
    cheatsheet += "| `[URL_TWITTER]` | Tu perfil de Twitter |\n"
    cheatsheet += "| `[URL_INSTAGRAM]` | Tu perfil de Instagram |\n"
    cheatsheet += "| `[URL_CALENDARIO]` | Link a tu calendario |\n"
    cheatsheet += "| `[URL_LOGO]` | URL de tu logo |\n\n"
    
    cheatsheet += "## 💡 Tips Rápidos\n\n"
    cheatsheet += "### Selección de Plantilla\n\n"
    cheatsheet += "- **Completa:** Todas las características, máxima compatibilidad\n"
    cheatsheet += "- **Compacta:** Diseño horizontal, información esencial\n"
    cheatsheet += "- **Simple:** HTML básico, máxima compatibilidad universal\n"
    cheatsheet += "- **Minimalista:** Diseño limpio, mucho espacio en blanco\n"
    cheatsheet += "- **Premium:** Badges, gradientes, elementos destacados\n\n"
    
    cheatsheet += "### Compatibilidad\n\n"
    cheatsheet += "- ✅ Usa tablas para estructura (no divs)\n"
    cheatsheet += "- ✅ Estilos inline (no CSS externo)\n"
    cheatsheet += "- ✅ VML/MSO para Outlook\n"
    cheatsheet += "- ✅ Media queries para móvil\n"
    cheatsheet += "- ✅ URLs absolutas para imágenes\n"
    cheatsheet += "- ❌ No uses JavaScript\n"
    cheatsheet += "- ❌ No uses CSS en `<head>`\n"
    cheatsheet += "- ❌ No uses divs para layout\n\n"
    
    cheatsheet += "### Validación Rápida\n\n"
    cheatsheet += "1. Ejecuta `validar_firma.py`\n"
    cheatsheet += "2. Verifica enlaces con `verificar_enlaces.py`\n"
    cheatsheet += "3. Prueba compatibilidad con `verificar_compatibilidad.py`\n"
    cheatsheet += "4. Envía email de prueba a ti mismo\n"
    cheatsheet += "5. Prueba en móvil\n\n"
    
    cheatsheet += "### Optimización\n\n"
    cheatsheet += "- Usa `optimizar_firma.py` para reducir tamaño\n"
    cheatsheet += "- Optimiza imágenes antes de usar\n"
    cheatsheet += "- Elimina comentarios innecesarios\n"
    cheatsheet += "- Usa versiones compactas si el tamaño es crítico\n\n"
    
    cheatsheet += "## 🔍 Búsqueda Rápida\n\n"
    cheatsheet += "### Por Industria\n\n"
    cheatsheet += "```bash\n"
    cheatsheet += "python buscar_plantilla.py --industria salud\n"
    cheatsheet += "python buscar_plantilla.py --industria tecnologia\n"
    cheatsheet += "python buscar_plantilla.py --industria marketing\n"
    cheatsheet += "```\n\n"
    
    cheatsheet += "### Por Estilo\n\n"
    cheatsheet += "```bash\n"
    cheatsheet += "python buscar_plantilla.py --estilo minimalista\n"
    cheatsheet += "python buscar_plantilla.py --estilo compacta\n"
    cheatsheet += "```\n\n"
    
    cheatsheet += "## 📚 Archivos Importantes\n\n"
    cheatsheet += "- `README.md` - Documentación principal\n"
    cheatsheet += "- `INICIO_RAPIDO.md` - Guía de 5 minutos\n"
    cheatsheet += "- `MANUAL_USUARIO.md` - Manual completo\n"
    cheatsheet += "- `GUIA_TROUBLESHOOTING.md` - Solución de problemas\n"
    cheatsheet += "- `PLACEHOLDERS.md` - Lista completa de placeholders\n"
    cheatsheet += "- `MATRIZ_DECISION.md` - Matriz de decisión\n"
    cheatsheet += "- `INDICE_COMPLETO.md` - Índice completo\n\n"
    
    cheatsheet += "## 🎨 Herramientas HTML\n\n"
    cheatsheet += "- `generador_interactivo.html` - Generador visual\n"
    cheatsheet += "- `test_compatibilidad.html` - Testing en navegador\n"
    cheatsheet += "- `preview_firmas.html` - Preview de todas las firmas\n"
    cheatsheet += "- `dashboard.html` - Dashboard interactivo\n\n"
    
    cheatsheet += "## ⚡ Workflow Rápido\n\n"
    cheatsheet += "```bash\n"
    cheatsheet += "# 1. Buscar plantilla\n"
    cheatsheet += "python buscar_plantilla.py\n\n"
    cheatsheet += "# 2. Personalizar\n"
    cheatsheet += "python personalizar_firma.py\n\n"
    cheatsheet += "# 3. Validar\n"
    cheatsheet += "python validar_firma.py firma_personalizada.html\n\n"
    cheatsheet += "# 4. Optimizar\n"
    cheatsheet += "python optimizar_firma.py firma_personalizada.html\n\n"
    cheatsheet += "# 5. Listo para usar\n"
    cheatsheet += "```\n\n"
    
    cheatsheet += "---\n\n"
    cheatsheet += f"*Cheatsheet generada el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    cheatsheet += "*Para actualizar, ejecuta `crear_cheatsheet.py`*\n"
    
    return cheatsheet

def main():
    """Función principal"""
    print("=" * 70)
    print("📝 Creador de Cheatsheet")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Generando cheatsheet...")
    print()
    
    cheatsheet = generar_cheatsheet()
    
    # Guardar
    archivo_cheatsheet = directorio_actual / "CHEATSHEET.md"
    with open(archivo_cheatsheet, 'w', encoding='utf-8') as f:
        f.write(cheatsheet)
    
    print("=" * 70)
    print("✅ Cheatsheet generada exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_cheatsheet.name}")
    print()
    print("💡 La cheatsheet incluye:")
    print("   - Comandos rápidos por categoría")
    print("   - Placeholders comunes")
    print("   - Tips rápidos")
    print("   - Búsqueda rápida")
    print("   - Archivos importantes")
    print("   - Workflow rápido")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()






