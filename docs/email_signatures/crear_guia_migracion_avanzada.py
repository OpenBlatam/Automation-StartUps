#!/usr/bin/env python3
"""
Creador de Guía de Migración Avanzada
Genera una guía detallada para migrar entre versiones y estilos
"""

import os
from pathlib import Path
from datetime import datetime

def generar_guia_migracion_avanzada() -> str:
    """Genera la guía de migración avanzada"""
    guia = "# 🔄 Guía de Migración Avanzada - Firmas de Email\n\n"
    guia += f"**Versión:** 4.3 | **Fecha:** {datetime.now().strftime('%d de %B de %Y')}\n\n"
    guia += "Esta guía te ayudará a migrar entre diferentes versiones, estilos y funcionalidades de las plantillas.\n\n"
    
    guia += "## 📋 Tabla de Contenidos\n\n"
    guia += "1. [Migración entre Versiones](#migración-entre-versiones)\n"
    guia += "2. [Migración entre Estilos](#migración-entre-estilos)\n"
    guia += "3. [Migración entre Plantillas](#migración-entre-plantillas)\n"
    guia += "4. [Migración de Datos](#migración-de-datos)\n"
    guia += "5. [Migración de Cliente de Email](#migración-de-cliente-de-email)\n"
    guia += "6. [Herramientas de Migración](#herramientas-de-migración)\n"
    guia += "7. [Checklist de Migración](#checklist-de-migración)\n\n"
    
    guia += "## 🔄 Migración entre Versiones\n\n"
    
    guia += "### De Versión Simple a Completa\n\n"
    guia += "**Cuándo migrar:**\n"
    guia += "- Necesitas más funcionalidades\n"
    guia += "- Quieres mejor compatibilidad con Outlook\n"
    guia += "- Necesitas más elementos visuales\n\n"
    guia += "**Pasos:**\n"
    guia += "1. Identifica la plantilla simple actual (`firma_*_simple.html`)\n"
    guia += "2. Encuentra la versión completa correspondiente (`firma_*.html`)\n"
    guia += "3. Copia tus datos personalizados de la versión simple\n"
    guia += "4. Usa `personalizar_firma.py` en la versión completa\n"
    guia += "5. Valida con `validar_firma.py`\n"
    guia += "6. Prueba en tu cliente de email\n\n"
    
    guia += "### De Versión Completa a Compacta\n\n"
    guia += "**Cuándo migrar:**\n"
    guia += "- Necesitas reducir el tamaño\n"
    guia += "- Quieres un diseño más horizontal\n"
    guia += "- Tienes limitaciones de espacio\n\n"
    guia += "**Pasos:**\n"
    guia += "1. Identifica la plantilla completa actual\n"
    guia += "2. Encuentra la versión compacta (`firma_*_compacta.html`)\n"
    guia += "3. Extrae información esencial de la versión completa\n"
    guia += "4. Personaliza la versión compacta con datos esenciales\n"
    guia += "5. Valida y prueba\n\n"
    
    guia += "### De Versión Estándar a Premium\n\n"
    guia += "**Cuándo migrar:**\n"
    guia += "- Quieres elementos destacados (badges, gradientes)\n"
    guia += "- Necesitas más impacto visual\n"
    guia += "- Quieres certificaciones y logros visibles\n\n"
    guia += "**Pasos:**\n"
    guia += "1. Identifica la plantilla estándar actual\n"
    guia += "2. Encuentra la versión premium (`firma_*_premium.html`)\n"
    guia += "3. Agrega información de certificaciones y logros\n"
    guia += "4. Personaliza badges y elementos destacados\n"
    guia += "5. Valida y prueba\n\n"
    
    guia += "## 🎨 Migración entre Estilos\n\n"
    
    guia += "### De Estilo Completo a Minimalista\n\n"
    guia += "**Cuándo migrar:**\n"
    guia += "- Prefieres diseño limpio y simple\n"
    guia += "- Quieres reducir elementos visuales\n"
    guia += "- Necesitas más espacio en blanco\n\n"
    guia += "**Pasos:**\n"
    guia += "1. Identifica elementos esenciales de tu firma actual\n"
    guia += "2. Encuentra versión minimalista (`firma_*_minimalista.html`)\n"
    guia += "3. Conserva solo información esencial\n"
    guia += "4. Elimina elementos decorativos\n"
    guia += "5. Personaliza con datos esenciales\n\n"
    
    guia += "### De Estilo Claro a Oscuro\n\n"
    guia += "**Cuándo migrar:**\n"
    guia += "- Tu cliente de email soporta modo oscuro\n"
    guia += "- Prefieres colores oscuros\n"
    guia += "- Quieres mejor contraste\n\n"
    guia += "**Pasos:**\n"
    guia += "1. Identifica la plantilla clara actual\n"
    guia += "2. Encuentra versión oscura (`firma_*_tema_oscuro.html`)\n"
    guia += "3. Copia tus datos personalizados\n"
    guia += "4. Personaliza la versión oscura\n"
    guia += "5. Prueba en modo oscuro\n\n"
    
    guia += "## 📧 Migración entre Plantillas\n\n"
    
    guia += "### Cambiar de Industria\n\n"
    guia += "**Ejemplo:** De tecnología a salud\n\n"
    guia += "**Pasos:**\n"
    guia += "1. Identifica elementos específicos de industria actual\n"
    guia += "2. Encuentra plantilla de nueva industria (`firma_salud.html`)\n"
    guia += "3. Extrae información genérica (nombre, email, teléfono)\n"
    guia += "4. Adapta información específica a nueva industria\n"
    guia += "5. Actualiza enlaces y CTAs relevantes\n"
    guia += "6. Valida y prueba\n\n"
    
    guia += "### Cambiar de Rol\n\n"
    guia += "**Ejemplo:** De consultor a desarrollador\n\n"
    guia += "**Pasos:**\n"
    guia += "1. Identifica plantilla actual (`firma_consultor_ia.html`)\n"
    guia += "2. Encuentra plantilla de nuevo rol (`firma_desarrollador_ia.html`)\n"
    guia += "3. Copia información de contacto\n"
    guia += "4. Actualiza información profesional específica del rol\n"
    guia += "5. Actualiza enlaces (GitHub, portfolio, etc.)\n"
    guia += "6. Valida y prueba\n\n"
    
    guia += "## 💾 Migración de Datos\n\n"
    
    guia += "### Extraer Datos de una Plantilla\n\n"
    guia += "**Herramientas:**\n"
    guia += "1. Usa `converter_formatos.py` para extraer a JSON\n"
    guia += "2. O busca manualmente los placeholders\n"
    guia += "3. Crea un archivo de configuración JSON\n\n"
    
    guia += "### Importar Datos a Nueva Plantilla\n\n"
    guia += "**Herramientas:**\n"
    guia += "1. Usa `personalizar_firma_avanzado.py` con archivo JSON\n"
    guia += "2. O usa `procesar_lote.py` para múltiples plantillas\n"
    guia += "3. Valida que todos los datos se hayan importado correctamente\n\n"
    
    guia += "## 📮 Migración de Cliente de Email\n\n"
    
    guia += "### De Gmail a Outlook\n\n"
    guia += "**Consideraciones:**\n"
    guia += "- Outlook requiere VML/MSO\n"
    guia += "- Usa versión completa de plantilla\n"
    guia += "- Verifica compatibilidad con `verificar_compatibilidad.py`\n\n"
    
    guia += "### De Outlook a Gmail\n\n"
    guia += "**Consideraciones:**\n"
    guia += "- Gmail elimina algunos estilos\n"
    guia += "- Verifica que los colores se vean correctamente\n"
    guia += "- Prueba en Gmail Web y App\n\n"
    
    guia += "### A Apple Mail\n\n"
    guia += "**Consideraciones:**\n"
    guia += "- Apple Mail tiene buen soporte HTML\n"
    guia += "- Verifica en macOS e iOS\n"
    guia += "- Prueba en modo claro y oscuro\n\n"
    
    guia += "## 🛠️ Herramientas de Migración\n\n"
    
    guia += "### Comparación\n\n"
    guia += "```bash\n"
    guia += "# Comparar versiones de una plantilla\n"
    guia += "python comparar_versiones.py\n\n"
    guia += "# Comparar todas las plantillas\n"
    guia += "python comparar_plantillas.py\n"
    guia += "```\n\n"
    
    guia += "### Conversión\n\n"
    guia += "```bash\n"
    guia += "# Convertir a JSON para extraer datos\n"
    guia += "python converter_formatos.py\n\n"
    guia += "# Exportar a múltiples formatos\n"
    guia += "python exportar_firmas.py\n"
    guia += "```\n\n"
    
    guia += "### Validación Post-Migración\n\n"
    guia += "```bash\n"
    guia += "# Validar plantilla migrada\n"
    guia += "python validar_firma.py firma_migrada.html\n\n"
    guia += "# Verificar compatibilidad\n"
    guia += "python verificar_compatibilidad.py firma_migrada.html\n\n"
    guia += "# Verificar enlaces\n"
    guia += "python verificar_enlaces.py firma_migrada.html\n"
    guia += "```\n\n"
    
    guia += "## ✅ Checklist de Migración\n\n"
    guia += "### Antes de Migrar\n\n"
    guia += "- [ ] Backup de plantilla actual\n"
    guia += "- [ ] Identificar datos a conservar\n"
    guia += "- [ ] Identificar datos a actualizar\n"
    guia += "- [ ] Elegir plantilla destino\n"
    guia += "- [ ] Verificar compatibilidad de plantilla destino\n\n"
    
    guia += "### Durante la Migración\n\n"
    guia += "- [ ] Extraer datos de plantilla origen\n"
    guia += "- [ ] Personalizar plantilla destino\n"
    guia += "- [ ] Validar estructura HTML\n"
    guia += "- [ ] Verificar todos los placeholders reemplazados\n"
    guia += "- [ ] Verificar enlaces funcionan\n\n"
    
    guia += "### Después de Migrar\n\n"
    guia += "- [ ] Validar con `validar_firma.py`\n"
    guia += "- [ ] Verificar compatibilidad con `verificar_compatibilidad.py`\n"
    guia += "- [ ] Probar en cliente de email\n"
    guia += "- [ ] Probar en móvil\n"
    guia += "- [ ] Enviar email de prueba\n"
    guia += "- [ ] Verificar que se vea correctamente\n"
    guia += "- [ ] Actualizar en configuración de email\n\n"
    
    guia += "## 🔧 Solución de Problemas en Migración\n\n"
    guia += "### Problema: Datos no se migraron correctamente\n\n"
    guia += "**Solución:**\n"
    guia += "1. Verifica que todos los placeholders se reemplazaron\n"
    guia += "2. Usa `buscar_plantilla.py` para encontrar placeholders faltantes\n"
    guia += "3. Revisa manualmente la plantilla\n\n"
    
    guia += "### Problema: Diseño se ve diferente\n\n"
    guia += "**Solución:**\n"
    guia += "1. Verifica que estés usando la versión correcta\n"
    guia += "2. Compara con `comparar_versiones.py`\n"
    guia += "3. Verifica compatibilidad con `verificar_compatibilidad.py`\n\n"
    
    guia += "### Problema: Enlaces no funcionan\n\n"
    guia += "**Solución:**\n"
    guia += "1. Usa `verificar_enlaces.py` para verificar todos los enlaces\n"
    guia += "2. Verifica que las URLs estén completas (http:// o https://)\n"
    guia += "3. Prueba los enlaces en un navegador\n\n"
    
    guia += "## 📚 Recursos Adicionales\n\n"
    guia += "- `GUIA_MIGRACION.md` - Guía básica de migración\n"
    guia += "- `GUIA_TROUBLESHOOTING.md` - Solución de problemas\n"
    guia += "- `MANUAL_USUARIO.md` - Manual completo\n"
    guia += "- `CHEATSHEET.md` - Referencia rápida\n\n"
    
    guia += "---\n\n"
    guia += f"*Guía generada el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    guia += "*Para actualizar, ejecuta `crear_guia_migracion_avanzada.py`*\n"
    
    return guia

def main():
    """Función principal"""
    print("=" * 70)
    print("🔄 Creador de Guía de Migración Avanzada")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Generando guía de migración avanzada...")
    print()
    
    guia = generar_guia_migracion_avanzada()
    
    # Guardar
    archivo_guia = directorio_actual / "GUIA_MIGRACION_AVANZADA.md"
    with open(archivo_guia, 'w', encoding='utf-8') as f:
        f.write(guia)
    
    print("=" * 70)
    print("✅ Guía de migración avanzada generada exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_guia.name}")
    print()
    print("💡 La guía incluye:")
    print("   - Migración entre versiones")
    print("   - Migración entre estilos")
    print("   - Migración entre plantillas")
    print("   - Migración de datos")
    print("   - Migración de cliente de email")
    print("   - Herramientas de migración")
    print("   - Checklist completo")
    print("   - Solución de problemas")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()






