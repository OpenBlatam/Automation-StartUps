#!/usr/bin/env python3
"""
Ultra Organizador Inteligente para Proyecto Frontier
Sistema avanzado de organización con IA y análisis semántico profundo
"""

import os
import re
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Set
from datetime import datetime
import hashlib

class UltraOrganizer:
    def __init__(self, root_path: str = "/Users/adan/frontier"):
        self.root_path = Path(root_path)
        self.config = self._load_advanced_config()
        self.analysis_cache = {}
        self.organization_log = self.root_path / "logs" / "ultra_organization.log"
        
        # Crear directorio de logs
        self.organization_log.parent.mkdir(exist_ok=True)
    
    def _load_advanced_config(self) -> Dict:
        """Carga configuración avanzada del sistema"""
        return {
            "version": "3.0",
            "created": datetime.now().isoformat(),
            "categories": {
                "01_Marketing": {
                    "name": "Marketing",
                    "description": "Estrategias, cursos y herramientas de marketing con IA",
                    "subcategories": [
                        "AI_Marketing_Courses", "Consciousness_Marketing", "Neural_Marketing",
                        "CopyAI_Integration", "ABM_Strategy", "Gamification", "VIP_Programs",
                        "Content_Generation", "Campaign_Management", "Analytics_Reports",
                        "Social_Media", "Email_Marketing", "SEO_Optimization", "PPC_Campaigns"
                    ],
                    "keywords": [
                        "marketing", "campaign", "advertising", "promotion", "brand", "customer",
                        "conversion", "lead", "sales", "revenue", "social", "content", "email",
                        "seo", "ppc", "analytics", "course", "curso", "workshop", "training",
                        "neural", "consciousness", "copyai", "abm", "gamification", "vip",
                        "premium", "strategy", "plan", "content", "social", "media"
                    ],
                    "file_patterns": [
                        "*marketing*", "*campaign*", "*advertising*", "*promotion*", "*brand*",
                        "*customer*", "*conversion*", "*lead*", "*sales*", "*revenue*",
                        "*social*", "*content*", "*email*", "*seo*", "*ppc*", "*analytics*",
                        "*course*", "*curso*", "*workshop*", "*training*", "*neural*",
                        "*consciousness*", "*copyai*", "*abm*", "*gamification*", "*vip*"
                    ]
                },
                "05_Technology": {
                    "name": "Technology",
                    "description": "Documentación técnica, código y arquitectura",
                    "subcategories": [
                        "API_Documentation", "System_Architecture", "Implementation_Guides",
                        "Technical_Specs", "Code_Examples", "System_Components", "Utilities",
                        "Prototypes", "Testing", "Deployment", "DevOps", "Infrastructure",
                        "Security", "Performance", "Monitoring"
                    ],
                    "keywords": [
                        "api", "architecture", "system", "tech", "code", "programming",
                        "development", "software", "implementation", "guide", "documentation",
                        "spec", "technical", "backend", "frontend", "database", "server",
                        "client", "deployment", "testing", "devops", "infrastructure"
                    ],
                    "file_patterns": [
                        "*api*", "*architecture*", "*system*", "*tech*", "*code*",
                        "*programming*", "*development*", "*software*", "*implementation*",
                        "*guide*", "*documentation*", "*spec*", "*technical*", "*backend*",
                        "*frontend*", "*database*", "*server*", "*client*", "*deployment*"
                    ]
                },
                "08_AI_Artificial_Intelligence": {
                    "name": "AI & Artificial Intelligence",
                    "description": "Sistemas de IA, algoritmos y tecnologías avanzadas",
                    "subcategories": [
                        "Consciousness_Systems", "Advanced_AI", "Neural_Networks",
                        "Quantum_Computing", "Transcendent_AI", "Machine_Learning",
                        "Deep_Learning", "Natural_Language_Processing", "Computer_Vision",
                        "Robotics", "Automation", "Predictive_Analytics", "Data_Science",
                        "Algorithm_Development", "Model_Training"
                    ],
                    "keywords": [
                        "ai", "artificial", "intelligence", "machine", "learning", "neural",
                        "deep", "algorithm", "model", "prediction", "automation", "chatbot",
                        "nlp", "computer", "vision", "quantum", "consciousness", "transcendent",
                        "divine", "automation", "predictive", "analytics", "data", "science"
                    ],
                    "file_patterns": [
                        "*ai*", "*artificial*", "*intelligence*", "*machine*", "*learning*",
                        "*neural*", "*deep*", "*algorithm*", "*model*", "*prediction*",
                        "*automation*", "*chatbot*", "*nlp*", "*computer*", "*vision*",
                        "*quantum*", "*consciousness*", "*transcendent*", "*divine*"
                    ]
                },
                "13_Legal_Compliance": {
                    "name": "Legal & Compliance",
                    "description": "Documentos legales, compliance y gestión de riesgos",
                    "subcategories": [
                        "Legal_Documents", "Compliance_Guides", "Risk_Assessments",
                        "VIP_Programs", "Commission_Agreements", "Privacy_Policies",
                        "Terms_Conditions", "Security_Protocols", "Regulatory_Compliance",
                        "Contract_Management", "Intellectual_Property", "Data_Protection"
                    ],
                    "keywords": [
                        "legal", "compliance", "policy", "agreement", "contract", "terms",
                        "privacy", "security", "risk", "audit", "regulation", "governance",
                        "liability", "commission", "vip", "privacy", "gdpr", "ccpa"
                    ],
                    "file_patterns": [
                        "*legal*", "*compliance*", "*policy*", "*agreement*", "*contract*",
                        "*terms*", "*privacy*", "*security*", "*risk*", "*audit*",
                        "*regulation*", "*governance*", "*liability*", "*commission*", "*vip*"
                    ]
                },
                "06_Strategy": {
                    "name": "Business Strategy",
                    "description": "Estrategias de negocio, planes y análisis",
                    "subcategories": [
                        "Business_Plans", "Competitive_Analysis", "Market_Research",
                        "ROI_Calculations", "Strategic_Planning", "Performance_Metrics",
                        "Growth_Strategies", "Innovation_Plans", "Financial_Analysis",
                        "Market_Entry", "Partnership_Strategies", "Exit_Strategies"
                    ],
                    "keywords": [
                        "strategy", "plan", "business", "management", "process", "workflow",
                        "efficiency", "productivity", "roi", "kpi", "metrics", "analysis",
                        "report", "dashboard", "competitive", "market", "research", "growth"
                    ],
                    "file_patterns": [
                        "*strategy*", "*plan*", "*business*", "*management*", "*process*",
                        "*workflow*", "*efficiency*", "*productivity*", "*roi*", "*kpi*",
                        "*metrics*", "*analysis*", "*report*", "*dashboard*", "*competitive*"
                    ]
                },
                "06_Documentation": {
                    "name": "Documentation",
                    "description": "Documentación general del proyecto",
                    "subcategories": [
                        "Project_Overview", "User_Guides", "Technical_Documentation",
                        "API_References", "Tutorials", "FAQs", "Changelog", "Roadmap",
                        "Contributing_Guide", "Code_Standards", "Architecture_Decisions"
                    ],
                    "keywords": [
                        "documentation", "guide", "tutorial", "faq", "changelog", "roadmap",
                        "overview", "reference", "standard", "architecture", "decision",
                        "contributing", "readme", "index", "summary"
                    ],
                    "file_patterns": [
                        "*documentation*", "*guide*", "*tutorial*", "*faq*", "*changelog*",
                        "*roadmap*", "*overview*", "*reference*", "*standard*", "*readme*",
                        "*index*", "*summary*", "*contributing*"
                    ]
                }
            },
            "settings": {
                "confidence_threshold": 0.7,
                "semantic_weight": 0.6,
                "pattern_weight": 0.4,
                "file_types": [".md", ".py", ".js", ".ts", ".html", ".pdf", ".docx", ".txt"],
                "exclude_patterns": ["*.tmp", "*.temp", "*.bak", "*.old", "*.log"],
                "min_file_size": 50,
                "max_analysis_size": 1000000  # 1MB
            }
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Registra mensaje en log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.organization_log, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        print(f"[{level}] {message}")
    
    def analyze_file_ultra(self, file_path: Path) -> Dict:
        """Análisis ultra avanzado de archivo"""
        try:
            # Verificar si ya está en cache
            file_hash = hashlib.md5(str(file_path).encode()).hexdigest()
            if file_hash in self.analysis_cache:
                return self.analysis_cache[file_hash]
            
            filename = file_path.name.lower()
            file_size = file_path.stat().st_size
            
            # Verificar tamaño del archivo
            if file_size < self.config["settings"]["min_file_size"]:
                return {"confidence": 0.0, "categories": [], "method": "too_small"}
            
            if file_size > self.config["settings"]["max_analysis_size"]:
                return {"confidence": 0.0, "categories": [], "method": "too_large"}
            
            # Análisis de contenido si es posible
            content_analysis = {"confidence": 0.0, "keywords": {}}
            if file_path.suffix.lower() in ['.md', '.txt', '.py', '.js', '.ts']:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore').lower()
                    content_analysis = self._analyze_content_semantic(content)
                except:
                    pass
            
            # Análisis de nombre de archivo
            filename_analysis = self._analyze_filename(filename)
            
            # Combinar análisis
            combined_analysis = self._combine_analysis(
                content_analysis, filename_analysis, filename
            )
            
            # Guardar en cache
            self.analysis_cache[file_hash] = combined_analysis
            return combined_analysis
            
        except Exception as e:
            return {"confidence": 0.0, "categories": [], "method": "error", "error": str(e)}
    
    def _analyze_content_semantic(self, content: str) -> Dict:
        """Análisis semántico del contenido"""
        keyword_scores = {}
        total_keywords = 0
        
        for category_id, category_info in self.config["categories"].items():
            score = 0
            for keyword in category_info["keywords"]:
                count = content.count(keyword)
                score += count
                total_keywords += count
            keyword_scores[category_id] = score
        
        if total_keywords == 0:
            return {"confidence": 0.0, "keywords": {}}
        
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
            "keywords": normalized_scores,
            "best_category": best_category[0]
        }
    
    def _analyze_filename(self, filename: str) -> Dict:
        """Análisis del nombre de archivo"""
        pattern_scores = {}
        
        for category_id, category_info in self.config["categories"].items():
            score = 0
            for pattern in category_info["file_patterns"]:
                if self._match_pattern(filename, pattern):
                    score += 1
            pattern_scores[category_id] = score
        
        if not any(pattern_scores.values()):
            return {"confidence": 0.0, "patterns": {}}
        
        # Normalizar scores
        total_patterns = sum(pattern_scores.values())
        normalized_scores = {
            cat: score / total_patterns 
            for cat, score in pattern_scores.items()
        }
        
        best_category = max(normalized_scores.items(), key=lambda x: x[1])
        confidence = best_category[1]
        
        return {
            "confidence": confidence,
            "patterns": normalized_scores,
            "best_category": best_category[0]
        }
    
    def _combine_analysis(self, content_analysis: Dict, filename_analysis: Dict, filename: str) -> Dict:
        """Combina análisis de contenido y nombre de archivo"""
        semantic_weight = self.config["settings"]["semantic_weight"]
        pattern_weight = self.config["settings"]["pattern_weight"]
        
        # Combinar confianzas
        content_confidence = content_analysis.get("confidence", 0)
        pattern_confidence = filename_analysis.get("confidence", 0)
        
        combined_confidence = (content_confidence * semantic_weight + 
                             pattern_confidence * pattern_weight)
        
        # Determinar mejor categoría
        if content_confidence > pattern_confidence:
            best_category = content_analysis.get("best_category", "06_Documentation")
            method = "semantic_analysis"
        else:
            best_category = filename_analysis.get("best_category", "06_Documentation")
            method = "pattern_analysis"
        
        # Verificar umbral de confianza
        if combined_confidence < self.config["settings"]["confidence_threshold"]:
            # Fallback por tipo de archivo
            file_type = self._get_file_type_category(filename)
            return {
                "confidence": 0.5,
                "categories": [file_type],
                "method": "file_type_fallback"
            }
        
        return {
            "confidence": combined_confidence,
            "categories": [best_category],
            "method": method,
            "content_confidence": content_confidence,
            "pattern_confidence": pattern_confidence
        }
    
    def _get_file_type_category(self, filename: str) -> str:
        """Determina categoría por tipo de archivo"""
        if filename.endswith(('.py', '.js', '.ts')):
            return "05_Technology"
        elif filename.endswith(('.md', '.txt')):
            return "06_Documentation"
        elif filename.endswith(('.html', '.css')):
            return "05_Technology"
        else:
            return "06_Documentation"
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """Verifica si archivo coincide con patrón"""
        pattern = pattern.replace("*", ".*")
        return bool(re.search(pattern, filename, re.IGNORECASE))
    
    def organize_ultra(self) -> Dict:
        """Organización ultra avanzada"""
        self.log("Iniciando organización ultra avanzada...")
        
        results = {
            "processed": 0,
            "organized": 0,
            "errors": 0,
            "improvements": [],
            "analysis_details": {}
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
                # Análisis ultra avanzado
                analysis = self.analyze_file_ultra(file_path)
                results["processed"] += 1
                
                # Determinar categoría objetivo
                target_category = analysis["categories"][0] if analysis["categories"] else "06_Documentation"
                
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
                    "method": analysis.get("method", "unknown"),
                    "confidence": analysis.get("confidence", 0),
                    "content_confidence": analysis.get("content_confidence", 0),
                    "pattern_confidence": analysis.get("pattern_confidence", 0)
                }
                results["improvements"].append(improvement)
                
                self.log(f"Organizado: {file_path.name} → {target_category} ({analysis.get('method', 'unknown')}) - Confianza: {analysis.get('confidence', 0):.2f}")
                
            except Exception as e:
                results["errors"] += 1
                self.log(f"Error organizando {file_path.name}: {e}", "ERROR")
        
        # Análisis detallado
        results["analysis_details"] = self._analyze_results(results)
        
        self.log(f"Organización ultra completada: {results['organized']} archivos organizados")
        return results
    
    def _analyze_results(self, results: Dict) -> Dict:
        """Analiza resultados de la organización"""
        if not results["improvements"]:
            return {}
        
        methods = {}
        confidences = []
        
        for improvement in results["improvements"]:
            method = improvement.get("method", "unknown")
            methods[method] = methods.get(method, 0) + 1
            
            confidence = improvement.get("confidence", 0)
            confidences.append(confidence)
        
        return {
            "methods_distribution": methods,
            "average_confidence": sum(confidences) / len(confidences) if confidences else 0,
            "high_confidence": len([c for c in confidences if c >= 0.8]),
            "medium_confidence": len([c for c in confidences if 0.5 <= c < 0.8]),
            "low_confidence": len([c for c in confidences if c < 0.5])
        }
    
    def verify_ultra_organization(self) -> Dict:
        """Verificación ultra de la organización"""
        self.log("Verificando organización ultra...")
        
        results = {
            "total_files": 0,
            "organized_files": 0,
            "loose_files": 0,
            "categories": {},
            "score": 0,
            "quality_metrics": {}
        }
        
        # Contar archivos organizados por categoría
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
        
        # Métricas de calidad
        results["quality_metrics"] = {
            "organization_rate": f"{(results['organized_files'] / max(results['total_files'], 1)) * 100:.1f}%",
            "loose_files_rate": f"{(results['loose_files'] / max(results['total_files'], 1)) * 100:.1f}%",
            "categories_used": len([c for c in results["categories"].values() if c > 0]),
            "average_files_per_category": results["organized_files"] / max(len([c for c in results["categories"].values() if c > 0]), 1)
        }
        
        self.log(f"Verificación ultra completada: {results['score']}/100 puntos")
        return results
    
    def generate_ultra_report(self, results: Dict) -> str:
        """Genera reporte ultra detallado"""
        report = f"""# 🚀 REPORTE ULTRA DE ORGANIZACIÓN
**Proyecto**: Frontier  
**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Versión**: {self.config['version']}  
**Sistema**: Ultra Organizador Inteligente

## 📈 RESULTADOS ULTRA

- **Archivos procesados**: {results.get('processed', 0)}
- **Archivos organizados**: {results.get('organized', 0)}
- **Errores**: {results.get('errors', 0)}
- **Tasa de éxito**: {(results.get('organized', 0) / max(results.get('processed', 1), 1)) * 100:.1f}%

## 🧠 ANÁLISIS INTELIGENTE

"""
        
        if "analysis_details" in results and results["analysis_details"]:
            details = results["analysis_details"]
            report += f"""
### Distribución por Método
"""
            for method, count in details.get("methods_distribution", {}).items():
                report += f"- **{method.replace('_', ' ').title()}**: {count} archivos\n"
            
            report += f"""
### Distribución de Confianza
- **Alta confianza (≥80%)**: {details.get('high_confidence', 0)} archivos
- **Confianza media (50-79%)**: {details.get('medium_confidence', 0)} archivos
- **Baja confianza (<50%)**: {details.get('low_confidence', 0)} archivos
- **Confianza promedio**: {details.get('average_confidence', 0):.2f}

"""
        
        report += f"""
## 📁 DISTRIBUCIÓN POR CATEGORÍAS

"""
        
        for category_id, file_count in results.get('categories', {}).items():
            category_name = self.config['categories'][category_id]['name']
            report += f"- **{category_name}**: {file_count} archivos\n"
        
        report += f"""
## 🎯 MÉTRICAS DE CALIDAD

- **Archivos organizados**: {results.get('organized_files', 0)}
- **Archivos sueltos**: {results.get('loose_files', 0)}
- **Puntaje total**: {results.get('score', 0)}/100
- **Tasa de organización**: {results.get('quality_metrics', {}).get('organization_rate', 'N/A')}
- **Categorías utilizadas**: {results.get('quality_metrics', {}).get('categories_used', 0)}

## 🚀 PRÓXIMOS PASOS

1. **Revisar archivos de baja confianza** para optimización manual
2. **Validar categorizaciones** de alta confianza
3. **Ejecutar mantenimiento** regular del sistema
4. **Optimizar reglas** basándose en resultados

---
*Reporte generado por el Ultra Organizador Inteligente v{self.config['version']}*
"""
        
        return report

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ultra Organizador del Proyecto Frontier')
    parser.add_argument('--mode', choices=['organize', 'verify', 'both'], 
                       default='both', help='Modo de ejecución')
    parser.add_argument('--root', default='/Users/adan/frontier', 
                       help='Ruta raíz del proyecto')
    
    args = parser.parse_args()
    
    organizer = UltraOrganizer(args.root)
    
    if args.mode in ['organize', 'both']:
        print("🚀 Iniciando organización ultra avanzada...")
        results = organizer.organize_ultra()
        
        # Generar reporte
        report = organizer.generate_ultra_report(results)
        report_file = Path(args.root) / "ULTRA_ORGANIZATION_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Reporte ultra guardado en: {report_file}")
    
    if args.mode in ['verify', 'both']:
        print("🔍 Verificando organización ultra...")
        verification = organizer.verify_ultra_organization()
        
        print(f"📊 Puntaje ultra: {verification['score']}/100")
        print(f"📁 Archivos organizados: {verification['organized_files']}")
        print(f"📄 Archivos sueltos: {verification['loose_files']}")
        print(f"🎯 Tasa de organización: {verification['quality_metrics']['organization_rate']}")

if __name__ == "__main__":
    main()
