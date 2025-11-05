#!/usr/bin/env python3
"""
Sistema de Organización Permanente para Proyecto Frontier
Sistema robusto y escalable para mantener la organización del proyecto
"""

import os
import re
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Set
from datetime import datetime
import hashlib

class FrontierOrganizer:
    def __init__(self, root_path: str = "/Users/adan/frontier"):
        self.root_path = Path(root_path)
        self.config = self._load_config()
        self.organization_rules = self._get_organization_rules()
        self.log_file = self.root_path / "logs" / "organization.log"
        
        # Crear directorio de logs
        self.log_file.parent.mkdir(exist_ok=True)
    
    def _load_config(self) -> Dict:
        """Carga configuración del sistema"""
        config_file = self.root_path / "organization_config.json"
        
        default_config = {
            "version": "2.0",
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
                        "VIP_Programs",
                        "Content_Generation",
                        "Campaign_Management",
                        "Analytics_Reports"
                    ],
                    "file_patterns": [
                        "*marketing*", "*campaign*", "*advertising*", "*promotion*",
                        "*brand*", "*customer*", "*conversion*", "*lead*", "*sales*",
                        "*social*", "*content*", "*email*", "*seo*", "*ppc*",
                        "*course*", "*curso*", "*workshop*", "*training*",
                        "*neural*", "*consciousness*", "*copyai*", "*abm*",
                        "*gamification*", "*vip*", "*premium*"
                    ]
                },
                "05_Technology": {
                    "name": "Technology",
                    "description": "Documentación técnica, código y arquitectura",
                    "subcategories": [
                        "API_Documentation",
                        "System_Architecture", 
                        "Implementation_Guides",
                        "Technical_Specs",
                        "Code_Examples",
                        "System_Components",
                        "Utilities",
                        "Prototypes",
                        "Testing",
                        "Deployment"
                    ],
                    "file_patterns": [
                        "*api*", "*architecture*", "*system*", "*tech*",
                        "*code*", "*programming*", "*development*", "*software*",
                        "*implementation*", "*guide*", "*documentation*",
                        "*spec*", "*technical*", "*backend*", "*frontend*",
                        "*database*", "*server*", "*client*"
                    ]
                },
                "08_AI_Artificial_Intelligence": {
                    "name": "AI & Artificial Intelligence",
                    "description": "Sistemas de IA, algoritmos y tecnologías avanzadas",
                    "subcategories": [
                        "Consciousness_Systems",
                        "Advanced_AI",
                        "Neural_Networks",
                        "Quantum_Computing",
                        "Transcendent_AI",
                        "Machine_Learning",
                        "Deep_Learning",
                        "Natural_Language_Processing",
                        "Computer_Vision",
                        "Robotics"
                    ],
                    "file_patterns": [
                        "*ai*", "*artificial*", "*intelligence*", "*machine*",
                        "*learning*", "*neural*", "*deep*", "*algorithm*",
                        "*model*", "*prediction*", "*automation*", "*chatbot*",
                        "*nlp*", "*computer*", "*vision*", "*quantum*",
                        "*consciousness*", "*transcendent*", "*divine*"
                    ]
                },
                "13_Legal_Compliance": {
                    "name": "Legal & Compliance",
                    "description": "Documentos legales, compliance y gestión de riesgos",
                    "subcategories": [
                        "Legal_Documents",
                        "Compliance_Guides",
                        "Risk_Assessments",
                        "VIP_Programs",
                        "Commission_Agreements",
                        "Privacy_Policies",
                        "Terms_Conditions",
                        "Security_Protocols"
                    ],
                    "file_patterns": [
                        "*legal*", "*compliance*", "*policy*", "*agreement*",
                        "*contract*", "*terms*", "*privacy*", "*security*",
                        "*risk*", "*audit*", "*regulation*", "*governance*",
                        "*liability*", "*commission*", "*vip*"
                    ]
                },
                "06_Strategy": {
                    "name": "Business Strategy",
                    "description": "Estrategias de negocio, planes y análisis",
                    "subcategories": [
                        "Business_Plans",
                        "Competitive_Analysis",
                        "Market_Research",
                        "ROI_Calculations",
                        "Strategic_Planning",
                        "Performance_Metrics",
                        "Growth_Strategies",
                        "Innovation_Plans"
                    ],
                    "file_patterns": [
                        "*strategy*", "*plan*", "*business*", "*management*",
                        "*process*", "*workflow*", "*efficiency*", "*productivity*",
                        "*roi*", "*kpi*", "*metrics*", "*analysis*", "*report*",
                        "*dashboard*", "*competitive*", "*market*"
                    ]
                }
            },
            "settings": {
                "auto_organize": True,
                "create_index_files": True,
                "verify_organization": True,
                "confidence_threshold": 0.6,
                "file_types": [".md", ".py", ".js", ".ts", ".html", ".pdf", ".docx"],
                "exclude_patterns": ["*.tmp", "*.temp", "*.bak", "*.old", "*.log"],
                "organization_threshold": 80
            }
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Actualizar con valores por defecto
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except:
                return default_config
        else:
            return default_config
    
    def _get_organization_rules(self) -> Dict:
        """Obtiene reglas de organización"""
        return {
            "semantic_keywords": {
                "marketing": [
                    "marketing", "campaign", "advertising", "promotion", "brand",
                    "customer", "conversion", "lead", "sales", "revenue",
                    "social", "content", "email", "seo", "ppc", "analytics"
                ],
                "ai": [
                    "ai", "artificial", "intelligence", "machine", "learning",
                    "neural", "deep", "algorithm", "model", "prediction",
                    "automation", "chatbot", "nlp", "computer", "vision"
                ],
                "technology": [
                    "api", "database", "server", "client", "frontend", "backend",
                    "code", "programming", "development", "software", "system",
                    "architecture", "infrastructure", "deployment", "testing"
                ],
                "business": [
                    "strategy", "plan", "business", "management", "process",
                    "workflow", "efficiency", "productivity", "roi", "kpi",
                    "metrics", "analysis", "report", "dashboard"
                ],
                "legal": [
                    "legal", "compliance", "policy", "agreement", "contract",
                    "terms", "privacy", "security", "risk", "audit",
                    "regulation", "governance", "liability"
                ]
            },
            "file_type_mapping": {
                ".md": "documentation",
                ".py": "code",
                ".js": "code", 
                ".ts": "code",
                ".html": "web",
                ".css": "web",
                ".json": "config",
                ".yaml": "config",
                ".yml": "config",
                ".xml": "config",
                ".pdf": "documentation",
                ".docx": "documentation",
                ".txt": "documentation"
            }
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Registra mensaje en log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        print(f"[{level}] {message}")
    
    def analyze_file(self, file_path: Path) -> Dict:
        """Analiza archivo para categorización"""
        try:
            if file_path.suffix.lower() not in ['.md', '.txt', '.py', '.js', '.ts']:
                return {"confidence": 0.0, "categories": [], "method": "file_type"}
            
            content = file_path.read_text(encoding='utf-8', errors='ignore').lower()
            filename = file_path.name.lower()
            
            # Análisis de palabras clave
            keyword_scores = {}
            for category, keywords in self.organization_rules["semantic_keywords"].items():
                score = 0
                for keyword in keywords:
                    score += content.count(keyword) + filename.count(keyword)
                keyword_scores[category] = score
            
            total_keywords = sum(keyword_scores.values())
            if total_keywords == 0:
                return {"confidence": 0.0, "categories": [], "method": "file_type"}
            
            # Normalizar scores
            normalized_scores = {
                cat: score / total_keywords 
                for cat, score in keyword_scores.items()
            }
            
            # Encontrar mejor categoría
            best_category = max(normalized_scores.items(), key=lambda x: x[1])
            confidence = best_category[1]
            
            return {
                "confidence": confidence,
                "categories": [best_category[0]],
                "method": "semantic_analysis",
                "keyword_scores": normalized_scores
            }
            
        except Exception as e:
            return {"confidence": 0.0, "categories": [], "method": "error", "error": str(e)}
    
    def get_target_category(self, file_path: Path, analysis: Dict) -> Tuple[str, str]:
        """Determina categoría objetivo para archivo"""
        filename = file_path.name.lower()
        
        # Mapeo directo por patrones de archivo
        for category_id, category_info in self.config["categories"].items():
            for pattern in category_info["file_patterns"]:
                if self._match_pattern(filename, pattern):
                    return category_id, "pattern_match"
        
        # Usar análisis semántico
        if analysis["confidence"] > self.config["settings"]["confidence_threshold"]:
            category_mapping = {
                "marketing": "01_Marketing",
                "ai": "08_AI_Artificial_Intelligence", 
                "technology": "05_Technology",
                "business": "06_Strategy",
                "legal": "13_Legal_Compliance"
            }
            target_category = category_mapping.get(analysis["categories"][0], "06_Documentation")
            return target_category, "semantic_analysis"
        
        # Fallback por tipo de archivo
        file_type = self.organization_rules["file_type_mapping"].get(
            file_path.suffix.lower(), "documentation"
        )
        
        if file_type == "code":
            return "05_Technology", "file_type"
        else:
            return "06_Documentation", "fallback"
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """Verifica si archivo coincide con patrón"""
        pattern = pattern.replace("*", ".*")
        return bool(re.search(pattern, filename, re.IGNORECASE))
    
    def organize_files(self) -> Dict:
        """Organiza archivos del proyecto"""
        self.log("Iniciando organización de archivos...")
        
        results = {
            "processed": 0,
            "organized": 0,
            "errors": 0,
            "improvements": []
        }
        
        # Buscar archivos para organizar
        files_to_organize = []
        for file_path in self.root_path.rglob('*'):
            if (file_path.is_file() and 
                file_path.suffix.lower() in self.config["settings"]["file_types"] and
                not any(file_path.parts[i].startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_', '11_', '12_', '13_', '14_', '15_', '16_', '17_', '18_', '19_', '20_')) for i in range(len(file_path.parts)))):
                files_to_organize.append(file_path)
        
        self.log(f"Encontrados {len(files_to_organize)} archivos para organizar")
        
        for file_path in files_to_organize:
            try:
                # Analizar archivo
                analysis = self.analyze_file(file_path)
                results["processed"] += 1
                
                # Determinar categoría objetivo
                target_category, method = self.get_target_category(file_path, analysis)
                
                # Crear directorio si no existe
                target_path = self.root_path / target_category
                target_path.mkdir(parents=True, exist_ok=True)
                
                # Mover archivo
                new_path = target_path / file_path.name
                if new_path.exists():
                    stem = file_path.stem
                    suffix = file_path.suffix
                    timestamp = int(datetime.now().timestamp())
                    new_path = target_path / f"{stem}_{timestamp}{suffix}"
                
                file_path.rename(new_path)
                results["organized"] += 1
                
                # Registrar mejora
                improvement = {
                    "file": file_path.name,
                    "from": str(file_path.parent),
                    "to": str(target_path),
                    "method": method,
                    "confidence": analysis.get("confidence", 0)
                }
                results["improvements"].append(improvement)
                
                self.log(f"Organizado: {file_path.name} → {target_category} ({method})")
                
            except Exception as e:
                results["errors"] += 1
                self.log(f"Error organizando {file_path.name}: {e}", "ERROR")
        
        self.log(f"Organización completada: {results['organized']} archivos organizados")
        return results
    
    def create_index_files(self):
        """Crea archivos índice para cada categoría"""
        self.log("Creando archivos índice...")
        
        for category_id, category_info in self.config["categories"].items():
            category_path = self.root_path / category_id
            if category_path.exists():
                index_file = category_path / "README.md"
                if not index_file.exists():
                    self._create_category_index(category_id, category_info, category_path)
        
        self.log("Archivos índice creados")
    
    def _create_category_index(self, category_id: str, category_info: Dict, category_path: Path):
        """Crea archivo índice para categoría"""
        content = f"""# {category_info['name']}

## 📋 Descripción
{category_info['description']}

## 📁 Subcategorías
"""
        
        # Agregar subcategorías existentes
        for subdir in category_path.iterdir():
            if subdir.is_dir():
                content += f"- **{subdir.name}**: {subdir.name.replace('_', ' ').title()}\n"
        
        content += f"""
## 🔍 Cómo usar
1. Navega por las subcategorías para encontrar documentos específicos
2. Usa la búsqueda para encontrar contenido específico
3. Consulta el índice maestro para una visión general

## 📊 Estadísticas
- **Total de archivos**: {len(list(category_path.rglob('*')))}
- **Última actualización**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*Categoría: {category_info['name']}*
*Mantenido por: Sistema de Organización Permanente*
"""
        
        with open(category_path / "README.md", 'w', encoding='utf-8') as f:
            f.write(content)
    
    def verify_organization(self) -> Dict:
        """Verifica estado de la organización"""
        self.log("Verificando organización...")
        
        results = {
            "total_files": 0,
            "organized_files": 0,
            "loose_files": 0,
            "categories": {},
            "score": 0
        }
        
        # Contar archivos organizados
        for category_id in self.config["categories"]:
            category_path = self.root_path / category_id
            if category_path.exists():
                files = list(category_path.rglob('*'))
                file_count = len([f for f in files if f.is_file()])
                results["categories"][category_id] = file_count
                results["organized_files"] += file_count
        
        # Contar archivos sueltos
        for file_path in self.root_path.rglob('*'):
            if (file_path.is_file() and 
                file_path.suffix.lower() in self.config["settings"]["file_types"] and
                not any(file_path.parts[i].startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_', '11_', '12_', '13_', '14_', '15_', '16_', '17_', '18_', '19_', '20_')) for i in range(len(file_path.parts)))):
                results["loose_files"] += 1
        
        results["total_files"] = results["organized_files"] + results["loose_files"]
        
        # Calcular puntaje
        if results["total_files"] > 0:
            organized_ratio = results["organized_files"] / results["total_files"]
            results["score"] = int(organized_ratio * 100)
        
        self.log(f"Verificación completada: {results['score']}/100 puntos")
        return results
    
    def generate_report(self, results: Dict) -> str:
        """Genera reporte de organización"""
        report = f"""# 📊 REPORTE DE ORGANIZACIÓN
**Proyecto**: Frontier  
**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Versión**: {self.config['version']}

## 📈 RESULTADOS GENERALES

- **Archivos procesados**: {results.get('processed', 0)}
- **Archivos organizados**: {results.get('organized', 0)}
- **Errores**: {results.get('errors', 0)}
- **Tasa de éxito**: {(results.get('organized', 0) / max(results.get('processed', 1), 1)) * 100:.1f}%

## 📁 DISTRIBUCIÓN POR CATEGORÍAS

"""
        
        for category_id, file_count in results.get('categories', {}).items():
            category_name = self.config['categories'][category_id]['name']
            report += f"- **{category_name}**: {file_count} archivos\n"
        
        report += f"""
## 🎯 ESTADO DE ORGANIZACIÓN

- **Archivos organizados**: {results.get('organized_files', 0)}
- **Archivos sueltos**: {results.get('loose_files', 0)}
- **Puntaje total**: {results.get('score', 0)}/100

## 🚀 PRÓXIMOS PASOS

1. **Revisar archivos sueltos** y organizarlos manualmente si es necesario
2. **Actualizar índices** de categorías con nuevos archivos
3. **Ejecutar verificación** regular para mantener organización
4. **Optimizar categorías** basándose en el uso

---
*Reporte generado automáticamente por el Sistema de Organización Permanente*
"""
        
        return report

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Organizador Permanente del Proyecto Frontier')
    parser.add_argument('--mode', choices=['organize', 'verify', 'both'], 
                       default='both', help='Modo de ejecución')
    parser.add_argument('--root', default='/Users/adan/frontier', 
                       help='Ruta raíz del proyecto')
    
    args = parser.parse_args()
    
    organizer = FrontierOrganizer(args.root)
    
    if args.mode in ['organize', 'both']:
        print("🚀 Iniciando organización...")
        results = organizer.organize_files()
        organizer.create_index_files()
        
        # Generar reporte
        report = organizer.generate_report(results)
        report_file = Path(args.root) / "ORGANIZATION_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Reporte guardado en: {report_file}")
    
    if args.mode in ['verify', 'both']:
        print("🔍 Verificando organización...")
        verification = organizer.verify_organization()
        
        print(f"📊 Puntaje de organización: {verification['score']}/100")
        print(f"📁 Archivos organizados: {verification['organized_files']}")
        print(f"📄 Archivos sueltos: {verification['loose_files']}")

if __name__ == "__main__":
    main()
