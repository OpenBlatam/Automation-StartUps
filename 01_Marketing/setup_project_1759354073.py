#!/usr/bin/env python3
"""
Sistema de Configuración Inicial para Proyecto Frontier
Configura la organización inicial del proyecto
"""

import os
import json
from pathlib import Path
from datetime import datetime
from organize_project import FrontierOrganizer

class ProjectSetup:
    def __init__(self, root_path: str = "/Users/adan/frontier"):
        self.root_path = Path(root_path)
        self.organizer = FrontierOrganizer(root_path)
    
    def setup_initial_organization(self):
        """Configura la organización inicial del proyecto"""
        print("🚀 Configurando organización inicial del proyecto Frontier...")
        
        # Crear estructura de directorios
        self.create_directory_structure()
        
        # Crear archivos de configuración
        self.create_config_files()
        
        # Configurar scripts
        self.setup_scripts()
        
        # Crear archivos índice
        self.create_index_files()
        
        # Organizar archivos existentes
        self.organize_existing_files()
        
        print("✅ Configuración inicial completada!")
    
    def create_directory_structure(self):
        """Crea la estructura de directorios"""
        print("📁 Creando estructura de directorios...")
        
        for category_id, category_info in self.organizer.config["categories"].items():
            category_path = self.root_path / category_id
            category_path.mkdir(exist_ok=True)
            
            # Crear subcategorías
            for subcategory in category_info["subcategories"]:
                subcategory_path = category_path / subcategory
                subcategory_path.mkdir(exist_ok=True)
            
            print(f"  ✅ {category_id}: {category_info['name']}")
    
    def create_config_files(self):
        """Crea archivos de configuración"""
        print("⚙️ Creando archivos de configuración...")
        
        # Guardar configuración
        config_file = self.root_path / "organization_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.organizer.config, f, indent=2, ensure_ascii=False)
        
        # Crear .gitignore para organización
        gitignore_content = """# Archivos de organización
organization_config.json
ORGANIZATION_REPORT.md
WEEKLY_MAINTENANCE_REPORT.md
MONTHLY_MAINTENANCE_REPORT.md
logs/

# Archivos temporales
*.tmp
*.temp
*.bak
*.old

# Archivos de sistema
.DS_Store
Thumbs.db
"""
        
        gitignore_file = self.root_path / ".organization_gitignore"
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        
        print("  ✅ Archivos de configuración creados")
    
    def setup_scripts(self):
        """Configura los scripts"""
        print("🔧 Configurando scripts...")
        
        scripts_dir = self.root_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        # Hacer scripts ejecutables
        script_files = [
            "organize_project.py",
            "maintain_project.py",
            "setup_project.py"
        ]
        
        for script_file in script_files:
            script_path = scripts_dir / script_file
            if script_path.exists():
                os.chmod(script_path, 0o755)
        
        print("  ✅ Scripts configurados")
    
    def create_index_files(self):
        """Crea archivos índice"""
        print("📝 Creando archivos índice...")
        
        self.organizer.create_index_files()
        print("  ✅ Archivos índice creados")
    
    def organize_existing_files(self):
        """Organiza archivos existentes"""
        print("📁 Organizando archivos existentes...")
        
        results = self.organizer.organize_files()
        print(f"  ✅ {results['organized']} archivos organizados")
    
    def create_master_index(self):
        """Crea índice maestro del proyecto"""
        print("📚 Creando índice maestro...")
        
        master_index = f"""# 🏗️ ÍNDICE MAESTRO DEL PROYECTO FRONTIER

## 📋 DESCRIPCIÓN GENERAL

Este es el índice maestro del proyecto Frontier, un sistema integral de IA Marketing que combina tecnologías avanzadas con estrategias de marketing innovadoras.

## 🏗️ ESTRUCTURA ORGANIZACIONAL

### 📚 **CATEGORÍAS PRINCIPALES**

"""
        
        for category_id, category_info in self.organizer.config["categories"].items():
            master_index += f"#### {category_id}: {category_info['name']}\n"
            master_index += f"**Descripción**: {category_info['description']}\n"
            master_index += f"**Subcategorías**: {len(category_info['subcategories'])}\n\n"
        
        master_index += f"""
## 🛠️ HERRAMIENTAS DE ORGANIZACIÓN

### 📝 **Scripts Disponibles**
- **`organize_project.py`**: Organización automática de archivos
- **`maintain_project.py`**: Mantenimiento automático del proyecto
- **`setup_project.py`**: Configuración inicial del proyecto

### 🔧 **Comandos Útiles**
```bash
# Organizar archivos
python3 scripts/organize_project.py --mode organize

# Verificar organización
python3 scripts/organize_project.py --mode verify

# Mantenimiento diario
python3 scripts/maintain_project.py --mode daily

# Mantenimiento semanal
python3 scripts/maintain_project.py --mode weekly

# Mantenimiento mensual
python3 scripts/maintain_project.py --mode monthly
```

## 📊 **MÉTRICAS DEL PROYECTO**

- **Categorías principales**: {len(self.organizer.config['categories'])}
- **Subcategorías totales**: {sum(len(cat['subcategories']) for cat in self.organizer.config['categories'].values())}
- **Tipos de archivo soportados**: {len(self.organizer.config['settings']['file_types'])}
- **Versión del sistema**: {self.organizer.config['version']}

## 🚀 **PRÓXIMOS PASOS**

1. **Explorar categorías** para familiarizarse con la estructura
2. **Ejecutar organización** para archivos nuevos
3. **Configurar mantenimiento** automático
4. **Personalizar configuración** según necesidades

## 📞 **SOPORTE**

- **Documentación**: READMEs en cada categoría
- **Logs**: Directorio `logs/` para registros del sistema
- **Configuración**: Archivo `organization_config.json`
- **Reportes**: Archivos de reporte generados automáticamente

---
*Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Versión: {self.organizer.config['version']}*
*Mantenido por: Sistema de Organización Permanente*
"""
        
        master_index_file = self.root_path / "PROJECT_MASTER_INDEX.md"
        with open(master_index_file, 'w', encoding='utf-8') as f:
            f.write(master_index)
        
        print(f"  ✅ Índice maestro creado: {master_index_file}")
    
    def generate_setup_report(self):
        """Genera reporte de configuración"""
        print("📊 Generando reporte de configuración...")
        
        report = f"""# 📋 REPORTE DE CONFIGURACIÓN INICIAL
**Proyecto**: Frontier  
**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Versión**: {self.organizer.config['version']}

## 🏗️ ESTRUCTURA CONFIGURADA

### Categorías Principales
"""
        
        for category_id, category_info in self.organizer.config["categories"].items():
            report += f"#### {category_id}: {category_info['name']}\n"
            report += f"**Descripción**: {category_info['description']}\n"
            report += f"**Subcategorías**: {len(category_info['subcategories'])}\n"
            report += f"**Patrones de archivo**: {len(category_info['file_patterns'])}\n\n"
        
        report += f"""
## ⚙️ CONFIGURACIÓN

### Configuración General
- **Organización automática**: {'✅' if self.organizer.config['settings']['auto_organize'] else '❌'}
- **Crear archivos índice**: {'✅' if self.organizer.config['settings']['create_index_files'] else '❌'}
- **Verificar organización**: {'✅' if self.organizer.config['settings']['verify_organization'] else '❌'}
- **Umbral de confianza**: {self.organizer.config['settings']['confidence_threshold']}
- **Umbral de organización**: {self.organizer.config['settings']['organization_threshold']}/100

### Tipos de archivo soportados
{', '.join(self.organizer.config['settings']['file_types'])}

### Patrones excluidos
{', '.join(self.organizer.config['settings']['exclude_patterns'])}

## 🚀 PRÓXIMOS PASOS

1. **Ejecutar organización inicial**: `python3 scripts/organize_project.py --mode organize`
2. **Verificar organización**: `python3 scripts/organize_project.py --mode verify`
3. **Configurar mantenimiento**: `python3 scripts/maintain_project.py --mode schedule`
4. **Revisar reportes**: Consultar archivos de reporte generados

## 📊 MÉTRICAS DE CONFIGURACIÓN

- **Total de categorías**: {len(self.organizer.config['categories'])}
- **Total de subcategorías**: {sum(len(cat['subcategories']) for cat in self.organizer.config['categories'].values())}
- **Patrones de archivo**: {sum(len(cat['file_patterns']) for cat in self.organizer.config['categories'].values())}
- **Configuración completa**: ✅

---
*Reporte generado automáticamente por el Sistema de Configuración Inicial*
"""
        
        report_file = self.root_path / "SETUP_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"  ✅ Reporte guardado en: {report_file}")

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Configurador del Proyecto Frontier')
    parser.add_argument('--mode', choices=['setup', 'index', 'report'], 
                       default='setup', help='Modo de ejecución')
    parser.add_argument('--root', default='/Users/adan/frontier', 
                       help='Ruta raíz del proyecto')
    
    args = parser.parse_args()
    
    setup = ProjectSetup(args.root)
    
    if args.mode == 'setup':
        setup.setup_initial_organization()
        setup.create_master_index()
        setup.generate_setup_report()
    elif args.mode == 'index':
        setup.create_master_index()
    elif args.mode == 'report':
        setup.generate_setup_report()

if __name__ == "__main__":
    main()
