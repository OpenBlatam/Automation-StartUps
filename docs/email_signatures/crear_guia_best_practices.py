#!/usr/bin/env python3
"""
Creador de Guía de Best Practices
Genera una guía completa de mejores prácticas para firmas de email
"""

import os
from pathlib import Path
from datetime import datetime

def generar_guia_best_practices() -> str:
    """Genera la guía de best practices"""
    guia = "# ⭐ Guía de Best Practices - Firmas de Email\n\n"
    guia += f"**Versión:** 4.4 | **Fecha:** {datetime.now().strftime('%d de %B de %Y')}\n\n"
    guia += "Esta guía recopila las mejores prácticas para crear, personalizar y usar firmas de email profesionales.\n\n"
    
    guia += "## 📋 Tabla de Contenidos\n\n"
    guia += "1. [Diseño y Estructura](#diseño-y-estructura)\n"
    guia += "2. [Contenido](#contenido)\n"
    guia += "3. [Compatibilidad](#compatibilidad)\n"
    guia += "4. [Rendimiento](#rendimiento)\n"
    guia += "5. [Accesibilidad](#accesibilidad)\n"
    guia += "6. [Seguridad](#seguridad)\n"
    guia += "7. [Personalización](#personalización)\n"
    guia += "8. [Testing](#testing)\n"
    guia += "9. [Mantenimiento](#mantenimiento)\n\n"
    
    guia += "## 🎨 Diseño y Estructura\n\n"
    
    guia += "### ✅ Hacer\n\n"
    guia += "1. **Usar tablas para estructura**\n"
    guia += "   - Las tablas son la base del diseño de emails\n"
    guia += "   - Proporcionan estructura consistente en todos los clientes\n"
    guia += "   - Usa `role=\"presentation\"` para accesibilidad\n\n"
    
    guia += "2. **Mantener ancho máximo de 600px**\n"
    guia += "   - Ancho óptimo para la mayoría de clientes\n"
    guia += "   - Evita problemas de visualización\n"
    guia += "   - Funciona bien en móvil y desktop\n\n"
    
    guia += "3. **Usar estilos inline**\n"
    guia += "   - Máxima compatibilidad\n"
    guia += "   - Evita problemas con CSS externo\n"
    guia += "   - Funciona en todos los clientes\n\n"
    
    guia += "4. **Incluir VML para Outlook**\n"
    guia += "   - Usa comentarios `<!--[if mso]>`\n"
    guia += "   - Incluye VML roundrect para botones\n"
    guia += "   - Verifica compatibilidad con Outlook\n\n"
    
    guia += "5. **Diseño responsive**\n"
    guia += "   - Usa media queries en `<head>`\n"
    guia += "   - Implementa clases `mobile-stack`\n"
    guia += "   - Prueba en dispositivos móviles reales\n\n"
    
    guia += "### ❌ Evitar\n\n"
    guia += "1. **No usar divs para layout**\n"
    guia += "   - Los divs no funcionan bien en emails\n"
    guia += "   - Usa tablas en su lugar\n\n"
    
    guia += "2. **No usar JavaScript**\n"
    guia += "   - La mayoría de clientes bloquean JavaScript\n"
    guia += "   - Puede causar problemas de seguridad\n\n"
    
    guia += "3. **No usar CSS externo**\n"
    guia += "   - Muchos clientes bloquean CSS externo\n"
    guia += "   - Usa estilos inline\n\n"
    
    guia += "4. **No usar colores con transparencia**\n"
    guia += "   - `rgba()` no funciona en todos los clientes\n"
    guia += "   - Usa códigos hexadecimales completos\n\n"
    
    guia += "## 📝 Contenido\n\n"
    
    guia += "### ✅ Hacer\n\n"
    guia += "1. **Mantener información esencial**\n"
    guia += "   - Nombre completo\n"
    guia += "   - Cargo o posición\n"
    guia += "   - Email de contacto\n"
    guia += "   - Teléfono (opcional)\n"
    guia += "   - Sitio web (opcional)\n\n"
    
    guia += "2. **Incluir enlaces relevantes**\n"
    guia += "   - LinkedIn para profesionales\n"
    guia += "   - Portfolio para creativos\n"
    guia += "   - Redes sociales relevantes\n"
    guia += "   - Calendario para agendamiento\n\n"
    
    guia += "3. **Usar CTAs cuando sea apropiado**\n"
    guia += "   - Agendar consulta\n"
    guia += "   - Ver portfolio\n"
    guia += "   - Contactar\n"
    guia += "   - Mantener CTAs relevantes y claros\n\n"
    
    guia += "4. **Mantener mensaje claro y conciso**\n"
    guia += "   - Evita información excesiva\n"
    guia += "   - Enfócate en lo esencial\n"
    guia += "   - Usa lenguaje profesional\n\n"
    
    guia += "### ❌ Evitar\n\n"
    guia += "1. **No incluir información personal excesiva**\n"
    guia += "   - Evita datos sensibles\n"
    guia += "   - No incluyas información privada\n\n"
    
    guia += "2. **No usar emojis excesivos**\n"
    guia += "   - Usa emojis con moderación\n"
    guia += "   - Considera el contexto profesional\n\n"
    
    guia += "3. **No incluir imágenes grandes**\n"
    guia += "   - Optimiza imágenes antes de usar\n"
    guia += "   - Mantén tamaño razonable\n\n"
    
    guia += "## 🔄 Compatibilidad\n\n"
    
    guia += "### ✅ Hacer\n\n"
    guia += "1. **Probar en múltiples clientes**\n"
    guia += "   - Gmail (Web y App)\n"
    guia += "   - Outlook (Desktop y Web)\n"
    guia += "   - Apple Mail\n"
    guia += "   - Yahoo Mail\n\n"
    
    guia += "2. **Probar en dispositivos móviles**\n"
    guia += "   - iOS (iPhone, iPad)\n"
    guia += "   - Android\n"
    guia += "   - Diferentes tamaños de pantalla\n\n"
    
    guia += "3. **Usar herramientas de validación**\n"
    guia += "   - `validar_firma.py`\n"
    guia += "   - `verificar_compatibilidad.py`\n"
    guia += "   - `test_compatibilidad.html`\n\n"
    
    guia += "4. **Consultar recursos de compatibilidad**\n"
    guia += "   - [Can I Email](https://www.caniemail.com/)\n"
    guia += "   - [Email on Acid](https://www.emailonacid.com/)\n"
    guia += "   - [Litmus](https://www.litmus.com/)\n\n"
    
    guia += "### ❌ Evitar\n\n"
    guia += "1. **No asumir compatibilidad**\n"
    guia += "   - Siempre prueba antes de usar\n"
    guia += "   - No asumas que funciona en todos los clientes\n\n"
    
    guia += "2. **No usar características modernas sin verificar**\n"
    guia += "   - Verifica soporte antes de usar\n"
    guia += "   - Usa fallbacks cuando sea necesario\n\n"
    
    guia += "## ⚡ Rendimiento\n\n"
    
    guia += "### ✅ Hacer\n\n"
    guia += "1. **Optimizar tamaño del archivo**\n"
    guia += "   - Usa `optimizar_firma.py`\n"
    guia += "   - Elimina espacios innecesarios\n"
    guia += "   - Remueve comentarios si es necesario\n\n"
    
    guia += "2. **Optimizar imágenes**\n"
    guia += "   - Comprime imágenes antes de usar\n"
    guia += "   - Usa formatos apropiados (JPG, PNG)\n"
    guia += "   - Mantén tamaño razonable\n\n"
    
    guia += "3. **Usar URLs absolutas**\n"
    guia += "   - Para imágenes y enlaces\n"
    guia += "   - Evita rutas relativas\n\n"
    
    guia += "4. **Minimizar recursos externos**\n"
    guia += "   - Evita recursos bloqueantes\n"
    guia += "   - Usa recursos locales cuando sea posible\n\n"
    
    guia += "### ❌ Evitar\n\n"
    guia += "1. **No usar imágenes muy grandes**\n"
    guia += "   - Afecta tiempo de carga\n"
    guia += "   - Puede causar problemas de visualización\n\n"
    
    guia += "2. **No incluir código innecesario**\n"
    guia += "   - Elimina código no utilizado\n"
    guia += "   - Mantén solo lo esencial\n\n"
    
    guia += "## ♿ Accesibilidad\n\n"
    
    guia += "### ✅ Hacer\n\n"
    guia += "1. **Usar atributos ARIA**\n"
    guia += "   - `aria-label` para enlaces\n"
    guia += "   - `role=\"presentation\"` para tablas\n\n"
    
    guia += "2. **Proporcionar texto alternativo**\n"
    guia += "   - `alt` para imágenes\n"
    guia += "   - Texto descriptivo para enlaces\n\n"
    
    guia += "3. **Mantener contraste adecuado**\n"
    guia += "   - Contraste mínimo 4.5:1 para texto\n"
    guia += "   - Verifica con herramientas de contraste\n\n"
    
    guia += "4. **Usar estructura semántica**\n"
    guia += "   - Tablas para estructura\n"
    guia += "   - Encabezados cuando sea apropiado\n\n"
    
    guia += "## 🔒 Seguridad\n\n"
    
    guia += "### ✅ Hacer\n\n"
    guia += "1. **Validar enlaces**\n"
    guia += "   - Usa `verificar_enlaces.py`\n"
    guia += "   - Verifica que todos los enlaces funcionen\n"
    guia += "   - Evita enlaces a sitios no seguros\n\n"
    
    guia += "2. **Usar HTTPS para recursos**\n"
    guia += "   - Imágenes desde servidores seguros\n"
    guia += "   - Enlaces a sitios seguros\n\n"
    
    guia += "3. **Evitar información sensible**\n"
    guia += "   - No incluyas datos personales sensibles\n"
    guia += "   - Considera privacidad\n\n"
    
    guia += "### ❌ Evitar\n\n"
    guia += "1. **No usar enlaces no verificados**\n"
    guia += "   - Verifica todos los enlaces\n"
    guia += "   - Evita enlaces sospechosos\n\n"
    
    guia += "2. **No incluir JavaScript**\n"
    guia += "   - Puede causar problemas de seguridad\n"
    guia += "   - Muchos clientes lo bloquean\n\n"
    
    guia += "## ✏️ Personalización\n\n"
    
    guia += "### ✅ Hacer\n\n"
    guia += "1. **Reemplazar todos los placeholders**\n"
    guia += "   - Usa `personalizar_firma.py`\n"
    guia += "   - Verifica que no queden placeholders\n"
    guia += "   - Consulta `PLACEHOLDERS.md`\n\n"
    
    guia += "2. **Validar datos ingresados**\n"
    guia += "   - Verifica formato de email\n"
    guia += "   - Valida URLs\n"
    guia += "   - Usa `personalizar_firma_avanzado.py`\n\n"
    
    guia += "3. **Mantener consistencia**\n"
    guia += "   - Usa mismo formato en toda la firma\n"
    guia += "   - Mantén estilo consistente\n\n"
    
    guia += "### ❌ Evitar\n\n"
    guia += "1. **No dejar placeholders sin reemplazar**\n"
    guia += "   - Revisa toda la plantilla\n"
    guia += "   - Usa herramientas de validación\n\n"
    
    guia += "2. **No usar datos incorrectos**\n"
    guia += "   - Verifica emails y URLs\n"
    guia += "   - Valida información antes de usar\n\n"
    
    guia += "## 🧪 Testing\n\n"
    
    guia += "### ✅ Hacer\n\n"
    guia += "1. **Validar antes de usar**\n"
    guia += "   - Usa `validar_firma.py`\n"
    guia += "   - Revisa reporte de validación\n"
    guia += "   - Corrige problemas encontrados\n\n"
    
    guia += "2. **Probar en cliente real**\n"
    guia += "   - Envía email de prueba a ti mismo\n"
    guia += "   - Prueba en diferentes clientes\n"
    guia += "   - Verifica en móvil\n\n"
    
    guia += "3. **Usar herramientas de testing**\n"
    guia += "   - `test_compatibilidad.html`\n"
    guia += "   - `verificar_compatibilidad.py`\n"
    guia += "   - Servicios online de testing\n\n"
    
    guia += "### Checklist de Testing\n\n"
    guia += "- [ ] Validación ejecutada sin errores críticos\n"
    guia += "- [ ] Probado en Gmail (Web y App)\n"
    guia += "- [ ] Probado en Outlook (Desktop y Web)\n"
    guia += "- [ ] Probado en Apple Mail\n"
    guia += "- [ ] Probado en dispositivo móvil\n"
    guia += "- [ ] Todos los enlaces funcionan\n"
    guia += "- [ ] Imágenes se cargan correctamente\n"
    guia += "- [ ] Diseño se ve correctamente\n\n"
    
    guia += "## 🔧 Mantenimiento\n\n"
    
    guia += "### ✅ Hacer\n\n"
    guia += "1. **Actualizar información regularmente**\n"
    guia += "   - Revisa información de contacto\n"
    guia += "   - Actualiza enlaces si es necesario\n"
    guia += "   - Mantén información actualizada\n\n"
    
    guia += "2. **Verificar enlaces periódicamente**\n"
    guia += "   - Usa `verificar_enlaces.py`\n"
    guia += "   - Corrige enlaces rotos\n\n"
    
    guia += "3. **Mantener backups**\n"
    guia += "   - Usa `backup_restore.py`\n"
    guia += "   - Guarda versiones anteriores\n\n"
    
    guia += "4. **Revisar compatibilidad**\n"
    guia += "   - Verifica compatibilidad periódicamente\n"
    guia += "   - Actualiza si es necesario\n\n"
    
    guia += "## 📚 Recursos Adicionales\n\n"
    guia += "- `MANUAL_USUARIO.md` - Manual completo\n"
    guia += "- `GUIA_TROUBLESHOOTING.md` - Solución de problemas\n"
    guia += "- `CHECKLIST_FINAL.md` - Checklist antes de usar\n"
    guia += "- `CHEATSHEET.md` - Referencia rápida\n\n"
    
    guia += "---\n\n"
    guia += f"*Guía generada el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    guia += "*Para actualizar, ejecuta `crear_guia_best_practices.py`*\n"
    
    return guia

def main():
    """Función principal"""
    print("=" * 70)
    print("⭐ Creador de Guía de Best Practices")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Generando guía de best practices...")
    print()
    
    guia = generar_guia_best_practices()
    
    # Guardar
    archivo_guia = directorio_actual / "GUIA_BEST_PRACTICES.md"
    with open(archivo_guia, 'w', encoding='utf-8') as f:
        f.write(guia)
    
    print("=" * 70)
    print("✅ Guía de best practices generada exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_guia.name}")
    print()
    print("💡 La guía incluye:")
    print("   - Diseño y estructura")
    print("   - Contenido")
    print("   - Compatibilidad")
    print("   - Rendimiento")
    print("   - Accesibilidad")
    print("   - Seguridad")
    print("   - Personalización")
    print("   - Testing")
    print("   - Mantenimiento")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()






