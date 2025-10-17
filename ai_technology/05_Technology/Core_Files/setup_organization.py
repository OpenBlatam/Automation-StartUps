#!/usr/bin/env python3
"""
Script de Configuración de Organización para Proyecto Frontier
Configura y optimiza la organización del proyecto
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

class OrganizationSetup:
    def __init__(self, root_path: str = "/Users/adan/frontier"):
        self.root_path = Path(root_path)
        self.config_file = self.root_path / "organization_config.json"
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        """Carga la configuración de organización"""
        default_config = {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "categories": {
                "01_Marketing": {
                    "name": "Marketing",
                    "description": "Estrategias, cursos y herramientas de marketing con IA",
                    "subcategories": [
                        "AI_Marketing_Courses",
                        "Consciousness_Marketing", 
                        "Neural_Marketing",
                        "CopyAI_Integration",
                        "ABM_Strategy",
                        "Gamification",
                        "VIP_Programs"
                    ],
                    "file_patterns": [
                        "*AI_Marketing*", "*Neural*", "*Consciousness*", "*CopyAI*",
                        "*ABM*", "*Gamification*", "*Course*", "*CURSO*", "*Workshop*",
                        "*Case*", "*Casos*", "*EXAMPLES*", "*Complete*", "*Ultimate*",
                        "*Enhanced*", "*Ecosistema*", "*Playbook*", "*Playbooks*",
                        "*Materials*", "*Training*", "*Assessment*", "*Certification*"
                    ]
                },
                "02_Consciousness_Systems": {
                    "name": "Consciousness Systems",
                    "description": "Sistemas de consciencia artificial y trascendencia",
                    "subcategories": [
                        "Consciousness_Systems",
                        "Transcendent_AI",
                        "Quantum_Computing",
                        "Neural_Networks"
                    ],
                    "file_patterns": [
                        "*Sistema*", "*Spiritual*", "*Universal*", "*Divine*",
                        "*Transcendent*", "*Conscious*", "*Infinite*", "*Cosmic*"
                    ]
                },
                "08_AI_Artificial_Intelligence": {
                    "name": "AI & Artificial Intelligence",
                    "description": "Sistemas de IA y algoritmos",
                    "subcategories": [
                        "Advanced_AI",
                        "Consciousness_Systems",
                        "Neural_Networks",
                        "Quantum_Computing",
                        "Transcendent_AI"
                    ],
                    "file_patterns": [
                        "*Advanced_AI*", "*ai-marketing*", "*Artificial*", "*Blockchain*",
                        "*Quantum*", "*Neural*", "*Machine*", "*Deep*", "*Algorithm*"
                    ]
                },
                "05_Technology": {
                    "name": "Technology",
                    "description": "Documentación técnica y arquitectura",
                    "subcategories": [
                        "API_Documentation",
                        "System_Architecture",
                        "Implementation_Guides",
                        "Technical_Specs"
                    ],
                    "file_patterns": [
                        "*API*", "*ARCHITECTURE*", "*Implementation*", "*DOCUMENTATION*",
                        "*Guide*", "*Changelog*", "*CONTRIBUTING*", "*README*",
                        "*DASHBOARD*", "*ENTERPRISE*", "*DEVELOPER*", "*Demo*",
                        "*Checklist*", "*Summary*", "*Templates*", "*Technical*"
                    ]
                }
            },
            "settings": {
                "auto_organize": True,
                "create_index_files": True,
                "verify_organization": True,
                "maintenance_schedule": {
                    "daily": "02:00",
                    "weekly": "sunday:03:00",
                    "monthly": "first_day"
                },
                "file_types": [".md", ".py", ".html", ".pdf", ".docx"],
                "exclude_patterns": ["*.tmp", "*.temp", "*.bak", "*.old"],
                "organization_threshold": 80
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Actualizar configuración con valores por defecto
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except:
                return default_config
        else:
            return default_config
    
    def save_config(self):
        """Guarda la configuración"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def setup_organization(self):
        """Configura la organización del proyecto"""
        print("🚀 Configurando organización del proyecto Frontier...")
        
        # Crear estructura de directorios
        self._create_directory_structure()
        
        # Crear archivos de configuración
        self._create_config_files()
        
        # Configurar scripts
        self._setup_scripts()
        
        # Crear archivos índice
        self._create_index_files()
        
        # Configurar mantenimiento automático
        self._setup_automated_maintenance()
        
        print("✅ Configuración completada exitosamente!")
    
    def _create_directory_structure(self):
        """Crea la estructura de directorios"""
        print("📁 Creando estructura de directorios...")
        
        for category_id, category_info in self.config["categories"].items():
            category_path = self.root_path / category_id
            category_path.mkdir(exist_ok=True)
            
            # Crear subcategorías
            for subcategory in category_info["subcategories"]:
                subcategory_path = category_path / subcategory
                subcategory_path.mkdir(exist_ok=True)
            
            print(f"  ✅ {category_id}: {category_info['name']}")
    
    def _create_config_files(self):
        """Crea archivos de configuración"""
        print("⚙️ Creando archivos de configuración...")
        
        # Guardar configuración principal
        self.save_config()
        
        # Crear .gitignore para organización
        gitignore_content = """# Archivos de organización
organization_config.json
ORGANIZACION_VERIFICATION_REPORT.md
WEEKLY_ORGANIZATION_REPORT.md
MONTHLY_ORGANIZATION_REPORT.md
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
    
    def _setup_scripts(self):
        """Configura los scripts de organización"""
        print("🔧 Configurando scripts...")
        
        scripts_dir = self.root_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        # Hacer scripts ejecutables
        script_files = [
            "auto_organize.py",
            "verify_organization.py", 
            "maintain_organization.py",
            "setup_organization.py"
        ]
        
        for script_file in script_files:
            script_path = scripts_dir / script_file
            if script_path.exists():
                os.chmod(script_path, 0o755)
        
        print("  ✅ Scripts configurados")
    
    def _create_index_files(self):
        """Crea archivos índice para cada categoría"""
        print("📝 Creando archivos índice...")
        
        for category_id, category_info in self.config["categories"].items():
            category_path = self.root_path / category_id
            index_file = category_path / "README.md"
            
            if not index_file.exists():
                content = self._generate_category_index(category_id, category_info)
                with open(index_file, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        print("  ✅ Archivos índice creados")
    
    def _generate_category_index(self, category_id: str, category_info: dict) -> str:
        """Genera contenido para archivo índice de categoría"""
        return f"""# {category_info['name']}

## 📋 Descripción
{category_info['description']}

## 📁 Subcategorías
"""
        + "\n".join([f"- **{subcat}**: {subcat.replace('_', ' ').title()}" 
                    for subcat in category_info['subcategories']]) + f"""

## 🔍 Cómo usar
1. Navega por las subcategorías para encontrar documentos específicos
2. Usa la búsqueda para encontrar contenido específico
3. Consulta el índice maestro para una visión general

## 📊 Estadísticas
- **Total de archivos**: {len(list((self.root_path / category_id).rglob('*')))}
- **Última actualización**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*Categoría: {category_info['name']}*
*Mantenido por: Sistema de Organización Automática*
"""
    
    def _setup_automated_maintenance(self):
        """Configura mantenimiento automático"""
        print("🤖 Configurando mantenimiento automático...")
        
        # Crear directorio de logs
        logs_dir = self.root_path / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Crear script de cron
        cron_script = self.root_path / "scripts" / "setup_cron.sh"
        cron_content = f"""#!/bin/bash
# Script de configuración de cron para mantenimiento automático

# Agregar tareas de mantenimiento al crontab
(crontab -l 2>/dev/null; echo "0 2 * * * cd {self.root_path} && python3 scripts/maintain_organization.py --mode daily") | crontab -
(crontab -l 2>/dev/null; echo "0 3 * * 0 cd {self.root_path} && python3 scripts/maintain_organization.py --mode weekly") | crontab -
(crontab -l 2>/dev/null; echo "0 4 1 * * cd {self.root_path} && python3 scripts/maintain_organization.py --mode monthly") | crontab -

echo "✅ Tareas de mantenimiento automático configuradas"
echo "📅 Mantenimiento diario: 02:00"
echo "📅 Mantenimiento semanal: Domingo 03:00" 
echo "📅 Mantenimiento mensual: Primer día del mes 04:00"
"""
        
        with open(cron_script, 'w', encoding='utf-8') as f:
            f.write(cron_content)
        
        os.chmod(cron_script, 0o755)
        
        print("  ✅ Mantenimiento automático configurado")
        print("  💡 Ejecuta 'bash scripts/setup_cron.sh' para activar el cron")
    
    def optimize_organization(self):
        """Optimiza la organización existente"""
        print("🔧 Optimizando organización existente...")
        
        # Ejecutar organización automática
        from auto_organize import FrontierOrganizer
        organizer = FrontierOrganizer(str(self.root_path))
        results = organizer.organize_directory()
        
        print(f"  ✅ {results['moved']} archivos organizados")
        
        # Verificar organización
        from verify_organization import OrganizationVerifier
        verifier = OrganizationVerifier(str(self.root_path))
        verification = verifier.verify_organization()
        
        score = verification['stats']['organization_score']
        print(f"  📊 Puntaje de organización: {score:.1f}/100")
        
        if score < 80:
            print("  ⚠️  Considera ejecutar mantenimiento adicional")
        else:
            print("  ✅ Organización en buen estado")
    
    def generate_report(self):
        """Genera reporte de configuración"""
        print("📊 Generando reporte de configuración...")
        
        report = f"""# 📋 REPORTE DE CONFIGURACIÓN DE ORGANIZACIÓN
**Proyecto**: Frontier  
**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Versión**: {self.config['version']}

## 🏗️ ESTRUCTURA CONFIGURADA

### Categorías Principales
"""
        
        for category_id, category_info in self.config["categories"].items():
            report += f"#### {category_id}: {category_info['name']}\n"
            report += f"**Descripción**: {category_info['description']}\n"
            report += f"**Subcategorías**: {len(category_info['subcategories'])}\n"
            report += f"**Patrones de archivo**: {len(category_info['file_patterns'])}\n\n"
        
        report += f"""
## ⚙️ CONFIGURACIÓN

### Configuración General
- **Organización automática**: {'✅' if self.config['settings']['auto_organize'] else '❌'}
- **Crear archivos índice**: {'✅' if self.config['settings']['create_index_files'] else '❌'}
- **Verificar organización**: {'✅' if self.config['settings']['verify_organization'] else '❌'}
- **Umbral de organización**: {self.config['settings']['organization_threshold']}/100

### Tipos de archivo soportados
{', '.join(self.config['settings']['file_types'])}

### Patrones excluidos
{', '.join(self.config['settings']['exclude_patterns'])}

## 🚀 PRÓXIMOS PASOS

1. **Ejecutar organización inicial**: `python3 scripts/auto_organize.py`
2. **Verificar organización**: `python3 scripts/verify_organization.py`
3. **Configurar mantenimiento automático**: `bash scripts/setup_cron.sh`
4. **Revisar reportes**: Consultar archivos de reporte generados

---
*Reporte generado automáticamente por el Sistema de Configuración de Organización*
"""
        
        report_file = self.root_path / "ORGANIZATION_SETUP_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"  ✅ Reporte guardado en: {report_file}")

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Configurador de Organización del Proyecto Frontier')
    parser.add_argument('--mode', choices=['setup', 'optimize', 'report'], 
                       default='setup', help='Modo de ejecución')
    parser.add_argument('--root', default='/Users/adan/frontier', 
                       help='Ruta raíz del proyecto')
    
    args = parser.parse_args()
    
    setup = OrganizationSetup(args.root)
    
    if args.mode == 'setup':
        setup.setup_organization()
    elif args.mode == 'optimize':
        setup.optimize_organization()
    elif args.mode == 'report':
        setup.generate_report()

if __name__ == "__main__":
    main()
