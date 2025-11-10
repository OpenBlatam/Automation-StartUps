#!/usr/bin/env python3
"""
Creador de Matriz de Decisión
Genera una matriz de decisión para ayudar a elegir la plantilla adecuada
"""

import os
from pathlib import Path
from datetime import datetime

def generar_matriz_decision() -> str:
    """Genera matriz de decisión"""
    matriz = "# 🎯 Matriz de Decisión - Selección de Plantillas\n\n"
    matriz += "Esta matriz te ayuda a elegir la plantilla adecuada según tus necesidades.\n\n"
    
    matriz += "## 📊 Matriz por Criterio\n\n"
    
    # Por industria
    matriz += "### 🏢 Por Industria\n\n"
    matriz += "| Industria | Plantilla Recomendada | Características |\n"
    matriz += "|-----------|----------------------|-----------------|\n"
    matriz += "| Salud/Medicina | `firma_salud.html` | Información médica, horarios, aviso confidencialidad |\n"
    matriz += "| Educación | `firma_educacion.html` | Campus, horarios de clases, acceso a plataforma |\n"
    matriz += "| Finanzas | `firma_finanzas.html` | Certificaciones, avisos legales, información financiera |\n"
    matriz += "| Tecnología | `firma_tecnologia.html` | Stack tecnológico, GitHub, portfolio |\n"
    matriz += "| Ventas | `firma_ventas.html` | CTAs de agendamiento, catálogo, territorio |\n"
    matriz += "| RRHH | `firma_recursos_humanos.html` | Contratación, oportunidades, información de oficina |\n"
    matriz += "| Marketing | `firma_marketing.html` | Blog, casos de éxito, redes sociales |\n"
    matriz += "| Legal | `firma_legal.html` | Despacho, colegio/barra, avisos legales |\n"
    matriz += "| Diseño | `firma_diseno.html` | Portfolio, Behance, Dribbble |\n"
    matriz += "| Consultoría | `firma_consultoria.html` | Servicios, agendamiento, especialización |\n"
    matriz += "| Medios | `firma_medios.html` | Portfolio, YouTube, redes sociales |\n"
    matriz += "| Investigación | `firma_investigacion.html` | Publicaciones, ORCID, Google Scholar |\n"
    matriz += "| Coaching | `firma_coaching.html` | Sesiones, agendamiento, certificación |\n"
    matriz += "| Bienes Raíces | `firma_bienes_raices.html` | Propiedades, visitas, zona/región |\n"
    matriz += "| Gastronomía | `firma_gastronomia.html` | Reservas, menú, TripAdvisor |\n"
    matriz += "| Turismo | `firma_turismo.html` | Paquetes, reservas, destinos |\n"
    matriz += "| Fitness | `firma_fitness.html` | Clases, planes, agendamiento |\n"
    matriz += "| Arte | `firma_arte.html` | Galería, exposiciones, plataformas artísticas |\n"
    matriz += "\n"
    
    # Por tipo de empresa
    matriz += "### 🏛️ Por Tipo de Empresa\n\n"
    matriz += "| Tipo | Plantilla | Cuándo Usar |\n"
    matriz += "|------|-----------|-------------|\n"
    matriz += "| Startup | `firma_empresa_startup.html` | Empresas nuevas, tech, innovadoras |\n"
    matriz += "| Corporativa | `firma_empresa_corporativa.html` | Grandes empresas, formal, tradicional |\n"
    matriz += "\n"
    
    # Por estilo
    matriz += "### 🎨 Por Estilo\n\n"
    matriz += "| Estilo | Características | Cuándo Usar |\n"
    matriz += "|--------|-----------------|-------------|\n"
    matriz += "| Completa | Todas las características | Uso general, máximo contenido |\n"
    matriz += "| Compacta | Diseño horizontal, información esencial | Espacios limitados |\n"
    matriz += "| Simple | HTML básico, máxima compatibilidad | Clientes antiguos |\n"
    matriz += "| Minimalista | Diseño limpio, mucho espacio | Estilo moderno |\n"
    matriz += "| Premium | Badges, gradientes, destacados | Impresión profesional |\n"
    matriz += "\n"
    
    # Por tema
    matriz += "### 🎨 Por Tema de Color\n\n"
    matriz += "| Tema | Plantilla | Cuándo Usar |\n"
    matriz += "|------|-----------|-------------|\n"
    matriz += "| Oscuro | `*_tema_oscuro.html` | Modo oscuro, diseño moderno |\n"
    matriz += "| Azul | `*_tema_azul.html` | Profesional, corporativo |\n"
    matriz += "| Rojo | `*_tema_rojo.html` | Energético, llamativo |\n"
    matriz += "| Púrpura | `*_tema_purpura.html` | Creativo, innovador |\n"
    matriz += "\n"
    
    # Por funcionalidad especial
    matriz += "### ⭐ Por Funcionalidad Especial\n\n"
    matriz += "| Funcionalidad | Plantilla | Cuándo Usar |\n"
    matriz += "|---------------|-----------|-------------|\n"
    matriz += "| Con QR Code | `*_qr.html` | Compartir información rápida |\n"
    matriz += "| Con Calendario | `*_calendario.html` | Agendar eventos, reuniones |\n"
    matriz += "| Bilingüe | `*_bilingue.html` | Audiencia internacional |\n"
    matriz += "| Para Eventos | `firma_evento_especial.html` | Eventos, lanzamientos |\n"
    matriz += "\n"
    
    # Por estación
    matriz += "### 🎄 Por Estación\n\n"
    matriz += "| Estación | Plantilla | Cuándo Usar |\n"
    matriz += "|----------|-----------|-------------|\n"
    matriz += "| Navidad | `firma_navidad.html` | Diciembre, temporada navideña |\n"
    matriz += "| Verano | `firma_verano.html` | Verano, horarios reducidos |\n"
    matriz += "| Año Nuevo | `firma_ano_nuevo.html` | Enero, nuevos objetivos |\n"
    matriz += "\n"
    
    # Flujo de decisión
    matriz += "## 🔄 Flujo de Decisión\n\n"
    matriz += "1. **¿Qué industria/sector?** → Selecciona plantilla por industria\n"
    matriz += "2. **¿Qué tipo de empresa?** → Startup o Corporativa\n"
    matriz += "3. **¿Qué estilo prefieres?** → Completa, Compacta, Simple, Minimalista, Premium\n"
    matriz += "4. **¿Necesitas funcionalidades especiales?** → QR, Calendario, Bilingüe\n"
    matriz += "5. **¿Es temporada especial?** → Navidad, Verano, Año Nuevo\n"
    matriz += "\n"
    
    # Recomendaciones rápidas
    matriz += "## ⚡ Recomendaciones Rápidas\n\n"
    matriz += "### Para Uso General\n"
    matriz += "- `firma_curso_ia_webinars.html` (versión completa)\n"
    matriz += "- `firma_saas_ia_marketing.html` (versión completa)\n"
    matriz += "\n"
    
    matriz += "### Para Espacios Limitados\n"
    matriz += "- Cualquier versión `*_compacta.html`\n"
    matriz += "- Versión `*_simple.html`\n"
    matriz += "\n"
    
    matriz += "### Para Máxima Compatibilidad\n"
    matriz += "- Versión `*_simple.html`\n"
    matriz += "- Versión `*_compacta.html`\n"
    matriz += "\n"
    
    matriz += "### Para Diseño Moderno\n"
    matriz += "- Versión `*_minimalista.html`\n"
    matriz += "- Versión `*_premium.html`\n"
    matriz += "\n"
    
    matriz += "---\n\n"
    matriz += f"*Matriz generada el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    
    return matriz

def main():
    """Función principal"""
    print("=" * 70)
    print("🎯 Creador de Matriz de Decisión")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Generando matriz de decisión...")
    print()
    
    matriz = generar_matriz_decision()
    
    # Guardar
    archivo_matriz = directorio_actual / "MATRIZ_DECISION.md"
    with open(archivo_matriz, 'w', encoding='utf-8') as f:
        f.write(matriz)
    
    print("=" * 70)
    print("✅ Matriz de decisión generada exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_matriz.name}")
    print()
    print("💡 La matriz incluye:")
    print("   - Selección por industria")
    print("   - Selección por tipo de empresa")
    print("   - Selección por estilo")
    print("   - Selección por tema")
    print("   - Funcionalidades especiales")
    print("   - Estaciones")
    print("   - Flujo de decisión")
    print("   - Recomendaciones rápidas")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()






