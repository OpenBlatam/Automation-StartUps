#!/usr/bin/env python3
"""
Creador de Guía de Instalación
Genera una guía completa de instalación y configuración
"""

import os
from pathlib import Path
from datetime import datetime

def generar_guia_instalacion() -> str:
    """Genera la guía de instalación"""
    guia = "# 🚀 Guía de Instalación - Firmas de Email\n\n"
    guia += f"**Versión:** 4.5 | **Fecha:** {datetime.now().strftime('%d de %B de %Y')}\n\n"
    guia += "Esta guía te ayudará a instalar y configurar el proyecto de firmas de email.\n\n"
    
    guia += "## 📋 Tabla de Contenidos\n\n"
    guia += "1. [Requisitos del Sistema](#requisitos-del-sistema)\n"
    guia += "2. [Instalación](#instalación)\n"
    guia += "3. [Configuración Inicial](#configuración-inicial)\n"
    guia += "4. [Verificación](#verificación)\n"
    guia += "5. [Primeros Pasos](#primeros-pasos)\n"
    guia += "6. [Solución de Problemas](#solución-de-problemas)\n\n"
    
    guia += "## 💻 Requisitos del Sistema\n\n"
    
    guia += "### Requisitos Mínimos\n\n"
    guia += "- **Python:** 3.6 o superior\n"
    guia += "- **Sistema Operativo:** Windows, macOS, o Linux\n"
    guia += "- **Navegador:** Cualquier navegador moderno (Chrome, Firefox, Safari, Edge)\n"
    guia += "- **Espacio en Disco:** ~5 MB\n"
    guia += "- **Memoria:** Mínimo 512 MB RAM\n\n"
    
    guia += "### Verificar Instalación de Python\n\n"
    guia += "```bash\n"
    guia += "# Verificar versión de Python\n"
    guia += "python --version\n\n"
    guia += "# O en algunos sistemas\n"
    guia += "python3 --version\n"
    guia += "```\n\n"
    guia += "**Salida esperada:** `Python 3.6.x` o superior\n\n"
    
    guia += "### Instalar Python (si no está instalado)\n\n"
    guia += "#### Windows\n"
    guia += "1. Descarga Python desde [python.org](https://www.python.org/downloads/)\n"
    guia += "2. Ejecuta el instalador\n"
    guia += "3. Marca la opción \"Add Python to PATH\"\n"
    guia += "4. Completa la instalación\n\n"
    
    guia += "#### macOS\n"
    guia += "```bash\n"
    guia += "# Usando Homebrew\n"
    guia += "brew install python3\n\n"
    guia += "# O descarga desde python.org\n"
    guia += "```\n\n"
    
    guia += "#### Linux\n"
    guia += "```bash\n"
    guia += "# Ubuntu/Debian\n"
    guia += "sudo apt-get update\n"
    guia += "sudo apt-get install python3\n\n"
    guia += "# Fedora\n"
    guia += "sudo dnf install python3\n"
    guia += "```\n\n"
    
    guia += "## 📥 Instalación\n\n"
    
    guia += "### Método 1: Descarga Directa\n\n"
    guia += "1. Descarga o clona el proyecto\n"
    guia += "2. Navega al directorio del proyecto\n"
    guia += "3. No se requieren dependencias adicionales\n"
    guia += "4. ¡Listo para usar!\n\n"
    
    guia += "### Método 2: Git Clone\n\n"
    guia += "```bash\n"
    guia += "# Clonar el repositorio\n"
    guia += "git clone [URL_DEL_REPOSITORIO]\n\n"
    guia += "# Navegar al directorio\n"
    guia += "cd email_signatures\n"
    guia += "```\n\n"
    
    guia += "### Estructura del Proyecto\n\n"
    guia += "```
├── firma_*.html          # Plantillas HTML
├── *.py                  # Scripts Python
├── *.md                  # Documentación
├── *.html                # Herramientas HTML
└── *.json                # Archivos de configuración
```\n\n"
    
    guia += "## ⚙️ Configuración Inicial\n\n"
    
    guia += "### 1. Verificar Permisos\n\n"
    guia += "```bash\n"
    guia += "# Verificar que tienes permisos de lectura/escritura\n"
    guia += "ls -la\n\n"
    guia += "# En Windows\n"
    guia += "dir\n"
    guia += "```\n\n"
    
    guia += "### 2. Probar un Script\n\n"
    guia += "```bash\n"
    guia += "# Probar script de estadísticas\n"
    guia += "python estadisticas_proyecto.py\n\n"
    guia += "# O en algunos sistemas\n"
    guia += "python3 estadisticas_proyecto.py\n"
    guia += "```\n\n"
    
    guia += "### 3. Abrir Herramientas HTML\n\n"
    guia += "1. Abre `generador_interactivo.html` en tu navegador\n"
    guia += "2. Verifica que funcione correctamente\n"
    guia += "3. Prueba otras herramientas HTML\n\n"
    
    guia += "## ✅ Verificación\n\n"
    
    guia += "### Checklist de Verificación\n\n"
    guia += "- [ ] Python 3.6+ instalado y funcionando\n"
    guia += "- [ ] Proyecto descargado/clonado\n"
    guia += "- [ ] Permisos de lectura/escritura verificados\n"
    guia += "- [ ] Scripts Python ejecutan sin errores\n"
    guia += "- [ ] Herramientas HTML abren en navegador\n"
    guia += "- [ ] Documentación accesible\n\n"
    
    guia += "### Comandos de Verificación\n\n"
    guia += "```bash\n"
    guia += "# Verificar Python\n"
    guia += "python --version\n\n"
    guia += "# Verificar estructura del proyecto\n"
    guia += "ls -la\n\n"
    guia += "# Probar script\n"
    guia += "python estadisticas_proyecto.py\n\n"
    guia += "# Generar dashboard\n"
    guia += "python generar_dashboard.py\n"
    guia += "```\n\n"
    
    guia += "## 🎯 Primeros Pasos\n\n"
    
    guia += "### 1. Explorar Plantillas\n\n"
    guia += "```bash\n"
    guia += "# Listar todas las plantillas\n"
    guia += "ls firma_*.html\n\n"
    guia += "# Buscar plantilla específica\n"
    guia += "python buscar_plantilla.py\n"
    guia += "```\n\n"
    
    guia += "### 2. Personalizar una Plantilla\n\n"
    guia += "```bash\n"
    guia += "# Personalización básica\n"
    guia += "python personalizar_firma.py\n\n"
    guia += "# O usar generador interactivo\n"
    guia += "# Abre generador_interactivo.html en navegador\n"
    guia += "```\n\n"
    
    guia += "### 3. Validar Plantilla\n\n"
    guia += "```bash\n"
    guia += "# Validar plantilla personalizada\n"
    guia += "python validar_firma.py firma_personalizada.html\n"
    guia += "```\n\n"
    
    guia += "### 4. Generar Documentación\n\n"
    guia += "```bash\n"
    guia += "# Generar dashboard\n"
    guia += "python generar_dashboard.py\n\n"
    guia += "# Generar estadísticas visuales\n"
    guia += "python generar_estadisticas_visuales.py\n"
    guia += "```\n\n"
    
    guia += "## 🔧 Solución de Problemas\n\n"
    
    guia += "### Problema: Python no encontrado\n\n"
    guia += "**Síntomas:**\n"
    guia += "- `python: command not found`\n"
    guia += "- `python3: command not found`\n\n"
    guia += "**Solución:**\n"
    guia += "1. Verifica que Python esté instalado\n"
    guia += "2. Verifica que esté en el PATH\n"
    guia += "3. Usa `python3` en lugar de `python` si es necesario\n"
    guia += "4. Reinstala Python si es necesario\n\n"
    
    guia += "### Problema: Permisos denegados\n\n"
    guia += "**Síntomas:**\n"
    guia += "- `Permission denied`\n"
    guia += "- No se pueden crear archivos\n\n"
    guia += "**Solución:**\n"
    guia += "1. Verifica permisos del directorio\n"
    guia += "2. Usa `chmod` en Linux/macOS si es necesario\n"
    guia += "3. Ejecuta como administrador si es necesario\n\n"
    
    guia += "### Problema: Scripts no ejecutan\n\n"
    guia += "**Síntomas:**\n"
    guia += "- Scripts no responden\n"
    guia += "- Errores al ejecutar\n\n"
    guia += "**Solución:**\n"
    guia += "1. Verifica que estés en el directorio correcto\n"
    guia += "2. Verifica que los archivos existan\n"
    guia += "3. Revisa mensajes de error\n"
    guia += "4. Verifica versión de Python\n\n"
    
    guia += "### Problema: Herramientas HTML no funcionan\n\n"
    guia += "**Síntomas:**\n"
    guia += "- No se abren en navegador\n"
    guia += "- Errores en consola del navegador\n\n"
    guia += "**Solución:**\n"
    guia += "1. Verifica que el archivo exista\n"
    guia += "2. Abre con doble clic o arrastra al navegador\n"
    guia += "3. Verifica consola del navegador para errores\n"
    guia += "4. Prueba en otro navegador\n\n"
    
    guia += "## 📚 Recursos Adicionales\n\n"
    guia += "- `README.md` - Documentación principal\n"
    guia += "- `INICIO_RAPIDO.md` - Guía de inicio rápido\n"
    guia += "- `MANUAL_USUARIO.md` - Manual completo\n"
    guia += "- `GUIA_TROUBLESHOOTING.md` - Solución de problemas\n\n"
    
    guia += "## 🎓 Siguiente Paso\n\n"
    guia += "Una vez completada la instalación:\n\n"
    guia += "1. Lee `INICIO_RAPIDO.md` para comenzar\n"
    guia += "2. Explora las plantillas disponibles\n"
    guia += "3. Personaliza tu primera firma\n"
    guia += "4. Valida y prueba tu firma\n\n"
    
    guia += "---\n\n"
    guia += f"*Guía generada el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    guia += "*Para actualizar, ejecuta `crear_guia_instalacion.py`*\n"
    
    return guia

def main():
    """Función principal"""
    print("=" * 70)
    print("🚀 Creador de Guía de Instalación")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Generando guía de instalación...")
    print()
    
    guia = generar_guia_instalacion()
    
    # Guardar
    archivo_guia = directorio_actual / "GUIA_INSTALACION.md"
    with open(archivo_guia, 'w', encoding='utf-8') as f:
        f.write(guia)
    
    print("=" * 70)
    print("✅ Guía de instalación generada exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_guia.name}")
    print()
    print("💡 La guía incluye:")
    print("   - Requisitos del sistema")
    print("   - Instalación paso a paso")
    print("   - Configuración inicial")
    print("   - Verificación")
    print("   - Primeros pasos")
    print("   - Solución de problemas")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()






