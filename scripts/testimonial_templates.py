#!/usr/bin/env python3
"""
Sistema de Templates para Testimonios
Permite crear y usar plantillas personalizadas para diferentes tipos de testimonios
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class TestimonialTemplate:
    """Clase para manejar templates de testimonios"""
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Inicializa el sistema de templates
        
        Args:
            templates_dir: Directorio donde se guardan los templates
        """
        self.templates_dir = templates_dir
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """Carga templates desde archivos JSON"""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
            self._create_default_templates()
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                template_path = os.path.join(self.templates_dir, filename)
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = json.load(f)
                    self.templates[template['id']] = template
    
    def _create_default_templates(self):
        """Crea templates por defecto"""
        default_templates = [
            {
                "id": "b2b_success",
                "name": "Éxito B2B",
                "description": "Para testimonios de empresas B2B con métricas de éxito",
                "platform": "linkedin",
                "tone": "profesional y empático",
                "structure": {
                    "hook": "Problema/Resultado destacado",
                    "body": "Narrativa con métricas",
                    "cta": "Llamada profesional"
                },
                "keywords": ["productividad", "ROI", "crecimiento", "equipo", "resultados"],
                "hashtags_template": ["#B2B", "#Éxito", "#Productividad", "#ROI", "#Crecimiento"]
            },
            {
                "id": "product_transformation",
                "name": "Transformación de Producto",
                "description": "Para testimonios sobre transformación personal con productos",
                "platform": "instagram",
                "tone": "cálido e inspirador",
                "structure": {
                    "hook": "Antes/Después",
                    "body": "Resultado visible",
                    "cta": "Llamada emocional"
                },
                "keywords": ["transformación", "resultado", "cambio", "mejora", "satisfacción"],
                "hashtags_template": ["#Transformación", "#Resultados", "#Testimonio", "#Éxito"]
            },
            {
                "id": "service_recommendation",
                "name": "Recomendación de Servicio",
                "description": "Para testimonios recomendando servicios",
                "platform": "facebook",
                "tone": "cálido y confiable",
                "structure": {
                    "hook": "Problema resuelto",
                    "body": "Experiencia positiva",
                    "cta": "Recomendación"
                },
                "keywords": ["recomiendo", "excelente", "satisfecho", "servicio", "calidad"],
                "hashtags_template": ["#Recomendación", "#Servicio", "#Calidad", "#Satisfacción"]
            },
            {
                "id": "course_education",
                "name": "Curso/Educación",
                "description": "Para testimonios sobre cursos y educación",
                "platform": "general",
                "tone": "inspirador y motivador",
                "structure": {
                    "hook": "Aprendizaje logrado",
                    "body": "Habilidades adquiridas",
                    "cta": "Invitación a aprender"
                },
                "keywords": ["aprendí", "curso", "habilidades", "conocimiento", "desarrollo"],
                "hashtags_template": ["#Educación", "#Aprendizaje", "#Desarrollo", "#Curso"]
            },
            {
                "id": "quick_result",
                "name": "Resultado Rápido",
                "description": "Para testimonios con resultados rápidos y visibles",
                "platform": "tiktok",
                "tone": "energético y directo",
                "structure": {
                    "hook": "Resultado en tiempo récord",
                    "body": "Métricas impresionantes",
                    "cta": "Llamada urgente"
                },
                "keywords": ["rápido", "inmediato", "resultado", "impacto", "cambio"],
                "hashtags_template": ["#ResultadosRápidos", "#Éxito", "#Transformación"]
            }
        ]
        
        for template in default_templates:
            template_path = os.path.join(self.templates_dir, f"{template['id']}.json")
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un template por ID"""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """Lista todos los templates disponibles"""
        return [
            {
                "id": t["id"],
                "name": t["name"],
                "description": t["description"],
                "platform": t.get("platform", "general")
            }
            for t in self.templates.values()
        ]
    
    def create_template(
        self,
        template_id: str,
        name: str,
        description: str,
        platform: str = "general",
        tone: str = "cálido y profesional",
        structure: Optional[Dict[str, str]] = None,
        keywords: Optional[List[str]] = None,
        hashtags_template: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Crea un nuevo template"""
        template = {
            "id": template_id,
            "name": name,
            "description": description,
            "platform": platform,
            "tone": tone,
            "structure": structure or {
                "hook": "Hook inicial",
                "body": "Cuerpo narrativo",
                "cta": "Llamada a la acción"
            },
            "keywords": keywords or [],
            "hashtags_template": hashtags_template or [],
            "created_at": datetime.now().isoformat()
        }
        
        self.templates[template_id] = template
        
        # Guardar en archivo
        template_path = os.path.join(self.templates_dir, f"{template_id}.json")
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        return template
    
    def suggest_template(self, testimonial: str, target_audience: str) -> Optional[str]:
        """Sugiere un template basado en el contenido del testimonio"""
        testimonial_lower = testimonial.lower()
        audience_lower = target_audience.lower()
        
        scores = {}
        
        for template_id, template in self.templates.items():
            score = 0
            
            # Verificar keywords
            for keyword in template.get("keywords", []):
                if keyword.lower() in testimonial_lower or keyword.lower() in audience_lower:
                    score += 2
            
            # Verificar palabras clave comunes
            if any(word in testimonial_lower for word in ["curso", "aprendí", "educación"]):
                if template_id == "course_education":
                    score += 5
            
            if any(word in testimonial_lower for word in ["empresa", "equipo", "productividad", "ROI"]):
                if template_id == "b2b_success":
                    score += 5
            
            if any(word in testimonial_lower for word in ["transformación", "cambio", "antes", "después"]):
                if template_id == "product_transformation":
                    score += 5
            
            if any(word in testimonial_lower for word in ["recomiendo", "servicio", "excelente"]):
                if template_id == "service_recommendation":
                    score += 5
            
            if any(word in testimonial_lower for word in ["rápido", "inmediato", "días", "semanas"]):
                if template_id == "quick_result":
                    score += 5
            
            scores[template_id] = score
        
        if scores:
            best_template = max(scores.items(), key=lambda x: x[1])
            if best_template[1] > 0:
                return best_template[0]
        
        return None
    
    def apply_template(
        self,
        template_id: str,
        testimonial: str,
        target_audience: str,
        converter
    ) -> Dict[str, Any]:
        """
        Aplica un template a un testimonio usando el convertidor
        
        Args:
            template_id: ID del template a aplicar
            testimonial: Texto del testimonio
            target_audience: Público objetivo
            converter: Instancia de TestimonialToSocialPostConverterV2
        
        Returns:
            Resultado de la conversión con el template aplicado
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template '{template_id}' no encontrado")
        
        return converter.convert_testimonial(
            testimonial=testimonial,
            target_audience_problem=target_audience,
            platform=template.get("platform", "general"),
            tone=template.get("tone", "cálido y profesional"),
            generate_hooks=True,
            analyze_quality=True
        )


def main():
    """Función principal para gestión de templates"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gestión de Templates para Testimonios")
    parser.add_argument(
        "action",
        choices=["list", "create", "suggest", "show"],
        help="Acción a realizar"
    )
    parser.add_argument(
        "--template-id",
        help="ID del template (para create, show)"
    )
    parser.add_argument(
        "--testimonial",
        help="Testimonio para sugerir template"
    )
    parser.add_argument(
        "--target-audience",
        help="Público objetivo para sugerir template"
    )
    parser.add_argument(
        "--templates-dir",
        default="templates",
        help="Directorio de templates"
    )
    
    args = parser.parse_args()
    
    template_manager = TestimonialTemplate(templates_dir=args.templates_dir)
    
    if args.action == "list":
        templates = template_manager.list_templates()
        print("\n📋 Templates Disponibles:\n")
        for t in templates:
            print(f"  • {t['id']}: {t['name']}")
            print(f"    {t['description']}")
            print(f"    Plataforma: {t['platform']}\n")
    
    elif args.action == "show":
        if not args.template_id:
            print("Error: --template-id requerido")
            return
        
        template = template_manager.get_template(args.template_id)
        if template:
            print(f"\n📄 Template: {template['name']}\n")
            print(json.dumps(template, indent=2, ensure_ascii=False))
        else:
            print(f"Error: Template '{args.template_id}' no encontrado")
    
    elif args.action == "suggest":
        if not args.testimonial or not args.target_audience:
            print("Error: --testimonial y --target-audience requeridos")
            return
        
        suggested = template_manager.suggest_template(args.testimonial, args.target_audience)
        if suggested:
            template = template_manager.get_template(suggested)
            print(f"\n💡 Template Sugerido: {template['name']} ({suggested})")
            print(f"   {template['description']}\n")
        else:
            print("\n⚠️  No se encontró un template específico. Usa 'general'.\n")
    
    elif args.action == "create":
        print("Para crear un template, usa la función create_template() programáticamente")
        print("o edita directamente los archivos JSON en el directorio de templates.")


if __name__ == "__main__":
    main()



