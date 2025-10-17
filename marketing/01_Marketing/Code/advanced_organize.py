#!/usr/bin/env python3
"""
Script de Organización Avanzada para Proyecto Frontier
Optimiza la organización con análisis semántico y categorización inteligente
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
from datetime import datetime
import hashlib

class AdvancedOrganizer:
    def __init__(self, root_path: str = "/Users/adan/frontier"):
        self.root_path = Path(root_path)
        self.organization_rules = self._load_organization_rules()
        self.file_analysis = {}
        self.optimization_log = []
        
    def _load_organization_rules(self) -> Dict:
        """Carga reglas avanzadas de organización"""
        return {
            "semantic_patterns": {
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
            },
            "content_analysis": {
                "keywords_threshold": 3,
                "confidence_threshold": 0.7,
                "min_file_size": 100
            }
        }
    
    def analyze_file_content(self, file_path: Path) -> Dict:
        """Analiza el contenido de un archivo para categorización semántica"""
        try:
            if file_path.suffix.lower() not in ['.md', '.txt', '.py', '.js', '.ts']:
                return {"confidence": 0.0, "categories": []}
            
            content = file_path.read_text(encoding='utf-8', errors='ignore').lower()
            
            # Análisis de palabras clave
            keyword_scores = {}
            for category, keywords in self.organization_rules["semantic_patterns"].items():
                score = 0
                for keyword in keywords:
                    score += content.count(keyword)
                keyword_scores[category] = score
            
            # Calcular confianza
            total_keywords = sum(keyword_scores.values())
            if total_keywords == 0:
                return {"confidence": 0.0, "categories": []}
            
            # Normalizar scores
            normalized_scores = {
                cat: score / total_keywords 
                for cat, score in keyword_scores.items()
            }
            
            # Filtrar por umbral de confianza
            confident_categories = [
                cat for cat, score in normalized_scores.items()
                if score >= self.organization_rules["content_analysis"]["confidence_threshold"]
            ]
            
            max_confidence = max(normalized_scores.values()) if normalized_scores else 0
            
            return {
                "confidence": max_confidence,
                "categories": confident_categories,
                "keyword_scores": normalized_scores,
                "file_size": file_path.stat().st_size
            }
            
        except Exception as e:
            return {"confidence": 0.0, "categories": [], "error": str(e)}
    
    def get_optimal_category(self, file_path: Path, content_analysis: Dict) -> Tuple[str, str]:
        """Determina la categoría óptima para un archivo"""
        filename = file_path.name.lower()
        
        # Mapeo directo por nombre de archivo
        direct_mapping = {
            "marketing": ["marketing", "campaign", "ad", "promo", "brand"],
            "ai": ["ai", "ml", "neural", "deep", "algorithm"],
            "technology": ["api", "code", "system", "tech", "dev"],
            "business": ["business", "strategy", "plan", "roi", "kpi"],
            "legal": ["legal", "compliance", "policy", "agreement", "contract"]
        }
        
        # Verificar mapeo directo
        for category, patterns in direct_mapping.items():
            if any(pattern in filename for pattern in patterns):
                return self._get_category_path(category), "direct_match"
        
        # Usar análisis de contenido
        if content_analysis["confidence"] > 0.5:
            best_category = max(
                content_analysis["keyword_scores"].items(),
                key=lambda x: x[1]
            )[0]
            return self._get_category_path(best_category), "content_analysis"
        
        # Fallback por tipo de archivo
        file_type = self.organization_rules["file_type_mapping"].get(
            file_path.suffix.lower(), "documentation"
        )
        
        if file_type == "code":
            return self._get_category_path("technology"), "file_type"
        elif file_type == "documentation":
            return self._get_category_path("business"), "file_type"
        else:
            return self._get_category_path("business"), "fallback"
    
    def _get_category_path(self, category: str) -> str:
        """Obtiene la ruta de categoría correspondiente"""
        category_mapping = {
            "marketing": "01_Marketing",
            "ai": "08_AI_Artificial_Intelligence",
            "technology": "05_Technology",
            "business": "06_Strategy",
            "legal": "13_Legal_Compliance"
        }
        return category_mapping.get(category, "06_Documentation")
    
    def organize_with_analysis(self) -> Dict:
        """Organiza archivos con análisis semántico avanzado"""
        print("🔍 Iniciando organización avanzada con análisis semántico...")
        
        results = {
            "analyzed": 0,
            "organized": 0,
            "errors": 0,
            "improvements": [],
            "analysis_details": {}
        }
        
        # Buscar archivos para organizar
        files_to_organize = []
        for file_path in self.root_path.rglob('*'):
            if (file_path.is_file() and 
                file_path.suffix.lower() in ['.md', '.py', '.js', '.ts', '.html', '.pdf', '.docx'] and
                not any(file_path.parts[i].startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_', '11_', '12_', '13_', '14_', '15_', '16_', '17_', '18_', '19_', '20_')) for i in range(len(file_path.parts)))):
                files_to_organize.append(file_path)
        
        print(f"📁 Encontrados {len(files_to_organize)} archivos para organizar...")
        
        for file_path in files_to_organize:
            try:
                # Analizar contenido
                content_analysis = self.analyze_file_content(file_path)
                results["analyzed"] += 1
                
                # Determinar categoría óptima
                target_category, method = self.get_optimal_category(file_path, content_analysis)
                
                # Crear directorio si no existe
                target_path = self.root_path / target_category
                target_path.mkdir(parents=True, exist_ok=True)
                
                # Mover archivo
                new_path = target_path / file_path.name
                if new_path.exists():
                    # Generar nombre único
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
                    "confidence": content_analysis.get("confidence", 0),
                    "categories": content_analysis.get("categories", [])
                }
                results["improvements"].append(improvement)
                
                print(f"✅ {file_path.name} → {target_category} ({method})")
                
            except Exception as e:
                results["errors"] += 1
                print(f"❌ Error organizando {file_path.name}: {e}")
        
        # Guardar análisis detallado
        results["analysis_details"] = {
            "total_files_analyzed": results["analyzed"],
            "organization_methods": {
                "direct_match": len([i for i in results["improvements"] if i["method"] == "direct_match"]),
                "content_analysis": len([i for i in results["improvements"] if i["method"] == "content_analysis"]),
                "file_type": len([i for i in results["improvements"] if i["method"] == "file_type"]),
                "fallback": len([i for i in results["improvements"] if i["method"] == "fallback"])
            },
            "confidence_distribution": self._calculate_confidence_distribution(results["improvements"])
        }
        
        return results
    
    def _calculate_confidence_distribution(self, improvements: List[Dict]) -> Dict:
        """Calcula distribución de confianza en las mejoras"""
        if not improvements:
            return {}
        
        confidences = [i.get("confidence", 0) for i in improvements]
        
        return {
            "high_confidence": len([c for c in confidences if c >= 0.8]),
            "medium_confidence": len([c for c in confidences if 0.5 <= c < 0.8]),
            "low_confidence": len([c for c in confidences if c < 0.5]),
            "average_confidence": sum(confidences) / len(confidences) if confidences else 0
        }
    
    def optimize_existing_structure(self) -> Dict:
        """Optimiza la estructura existente reorganizando archivos mal categorizados"""
        print("🔧 Optimizando estructura existente...")
        
        results = {
            "analyzed": 0,
            "reorganized": 0,
            "improvements": []
        }
        
        # Analizar archivos en categorías existentes
        for category_dir in self.root_path.glob("[0-9][0-9]_*"):
            if not category_dir.is_dir():
                continue
                
            for file_path in category_dir.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in ['.md', '.py', '.js', '.ts', '.html']:
                    try:
                        # Analizar contenido
                        content_analysis = self.analyze_file_content(file_path)
                        results["analyzed"] += 1
                        
                        # Determinar si necesita reorganización
                        current_category = category_dir.name
                        optimal_category, method = self.get_optimal_category(file_path, content_analysis)
                        
                        # Verificar si necesita reorganización
                        if (optimal_category != current_category and 
                            content_analysis.get("confidence", 0) > 0.7):
                            
                            # Mover a categoría óptima
                            target_path = self.root_path / optimal_category
                            target_path.mkdir(parents=True, exist_ok=True)
                            
                            new_path = target_path / file_path.name
                            if new_path.exists():
                                stem = file_path.stem
                                suffix = file_path.suffix
                                timestamp = int(datetime.now().timestamp())
                                new_path = target_path / f"{stem}_{timestamp}{suffix}"
                            
                            file_path.rename(new_path)
                            results["reorganized"] += 1
                            
                            improvement = {
                                "file": file_path.name,
                                "from": current_category,
                                "to": optimal_category,
                                "confidence": content_analysis.get("confidence", 0),
                                "reason": "Better semantic match"
                            }
                            results["improvements"].append(improvement)
                            
                            print(f"🔄 {file_path.name}: {current_category} → {optimal_category}")
                    
                    except Exception as e:
                        print(f"❌ Error analizando {file_path.name}: {e}")
        
        return results
    
    def generate_optimization_report(self, results: Dict) -> str:
        """Genera reporte de optimización"""
        report = f"""# 🚀 REPORTE DE OPTIMIZACIÓN AVANZADA
**Proyecto**: Frontier  
**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Tipo**: Organización Avanzada con Análisis Semántico

## 📊 RESULTADOS GENERALES

- **Archivos analizados**: {results['analyzed']}
- **Archivos organizados**: {results['organized']}
- **Errores**: {results['errors']}
- **Tasa de éxito**: {(results['organized'] / max(results['analyzed'], 1)) * 100:.1f}%

## 🔍 MÉTODOS DE ORGANIZACIÓN

"""
        
        if "analysis_details" in results:
            methods = results["analysis_details"]["organization_methods"]
            report += f"""
### Distribución por Método
- **Coincidencia directa**: {methods.get('direct_match', 0)} archivos
- **Análisis de contenido**: {methods.get('content_analysis', 0)} archivos
- **Tipo de archivo**: {methods.get('file_type', 0)} archivos
- **Fallback**: {methods.get('fallback', 0)} archivos

### Distribución de Confianza
- **Alta confianza (≥80%)**: {results['analysis_details']['confidence_distribution'].get('high_confidence', 0)} archivos
- **Confianza media (50-79%)**: {results['analysis_details']['confidence_distribution'].get('medium_confidence', 0)} archivos
- **Baja confianza (<50%)**: {results['analysis_details']['confidence_distribution'].get('low_confidence', 0)} archivos
- **Confianza promedio**: {results['analysis_details']['confidence_distribution'].get('average_confidence', 0):.2f}

"""
        
        if results["improvements"]:
            report += "## 📈 MEJORAS IMPLEMENTADAS\n\n"
            
            # Agrupar por método
            by_method = {}
            for improvement in results["improvements"]:
                method = improvement.get("method", "unknown")
                if method not in by_method:
                    by_method[method] = []
                by_method[method].append(improvement)
            
            for method, improvements in by_method.items():
                report += f"### {method.replace('_', ' ').title()}\n"
                for improvement in improvements[:5]:  # Mostrar solo los primeros 5
                    report += f"- **{improvement['file']}**: {improvement.get('from', 'unknown')} → {improvement.get('to', 'unknown')}\n"
                if len(improvements) > 5:
                    report += f"- ... y {len(improvements) - 5} más\n"
                report += "\n"
        
        report += f"""
## 🎯 RECOMENDACIONES

### Mejoras Inmediatas
1. **Revisar archivos de baja confianza** para categorización manual
2. **Validar reorganizaciones** realizadas automáticamente
3. **Actualizar índices** de categorías afectadas
4. **Ejecutar verificación** de organización

### Mejoras a Mediano Plazo
1. **Refinar reglas semánticas** basadas en resultados
2. **Implementar aprendizaje** de patrones de organización
3. **Crear sistema de feedback** para mejoras continuas
4. **Automatizar validación** de categorización

### Mejoras a Largo Plazo
1. **Integrar IA avanzada** para análisis de contenido
2. **Implementar clustering** automático de documentos
3. **Desarrollar sistema** de recomendaciones
4. **Crear dashboard** de organización en tiempo real

## 📊 MÉTRICAS DE CALIDAD

- **Precisión de categorización**: {results['analysis_details']['confidence_distribution'].get('average_confidence', 0) * 100:.1f}%
- **Cobertura de análisis**: {(results['analyzed'] / max(results['analyzed'] + results['errors'], 1)) * 100:.1f}%
- **Eficiencia de organización**: {(results['organized'] / max(results['analyzed'], 1)) * 100:.1f}%

---
*Reporte generado automáticamente por el Sistema de Organización Avanzada*
"""
        
        return report

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Organizador Avanzado del Proyecto Frontier')
    parser.add_argument('--mode', choices=['organize', 'optimize', 'both'], 
                       default='both', help='Modo de ejecución')
    parser.add_argument('--root', default='/Users/adan/frontier', 
                       help='Ruta raíz del proyecto')
    
    args = parser.parse_args()
    
    organizer = AdvancedOrganizer(args.root)
    
    if args.mode in ['organize', 'both']:
        print("🚀 Ejecutando organización avanzada...")
        results = organizer.organize_with_analysis()
        
        # Generar reporte
        report = organizer.generate_optimization_report(results)
        report_file = Path(args.root) / "ADVANCED_ORGANIZATION_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Reporte guardado en: {report_file}")
    
    if args.mode in ['optimize', 'both']:
        print("🔧 Ejecutando optimización de estructura...")
        optimization_results = organizer.optimize_existing_structure()
        print(f"✅ Optimización completada: {optimization_results['reorganized']} archivos reorganizados")

if __name__ == "__main__":
    main()
