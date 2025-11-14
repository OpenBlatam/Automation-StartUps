#!/usr/bin/env python3
"""
Script avanzado para organizar archivos en subcarpetas específicas
Mejora la organización moviendo archivos desde las carpetas principales a subcarpetas más específicas
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict

ROOT_DIR = Path(__file__).parent

# Mapeo de patrones a subcarpetas específicas
SUB_FOLDER_MAPPING = {
    '01_Marketing': {
        'CTAs/': ['ctas_', 'CTA', 'CTAs_'],
        'Blog_Posts/': ['blog_', 'ideas_blog', 'ideas_posts'],
        'Sequences/': ['secuencia_', 'email_sequence', 'email_nurture', 'follow_up', 'sequence_'],
        'Checklists/': ['checklist_', 'CHECKLIST_'],
        'Guides/': ['GUIA_', 'guia_', 'guide_', 'GUIDE_', 'Instrucciones'],
        'Templates/': ['plantilla_', 'plantillas_', 'Templates_', 'template_', 'version_', 'Entregable'],
        '04_Email_Marketing/': ['email', 'Email', 'EMAIL', 'mailing'],
        '03_Social_Media/': ['social_', 'linkedin_', 'post_linkedin', 'instagram', 'viral_', 'youtube'],
        '01_Digital_Marketing/': ['digital_', 'DIGITAL_'],
        '02_Content_Marketing/': ['content_', 'contenido_', 'Content_', 'ContentGenerator'],
        '05_Lead_Generation/': ['lead_', 'LEAD_', 'outreach', 'OUTREACH', 'LOCALISMOS', 'SECTORES_REGULADOS', 'SNIPPETS'],
        '06_Analytics/': ['seo_', 'SEO_', 'analytics', 'keyword'],
        '07_Campaign_Management/': ['campaign', 'CAMPAIGN', 'CALENDARIO', 'calendario_'],
        '08_AI_Marketing/': ['ai_marketing', 'AI_Marketing', 'DM_', 'DMs_', 'DM_Variants'],
        '10_Affiliate_Marketing/': ['affiliate', 'Affiliate', 'AFFILIATE'],
        'Data_Files/': ['.csv', '.json', 'ACTIVECAMPAIGN', 'CRM_OUTREACH', 'MAILCHIMP'],
        'Scripts/': ['script_', 'SCRIPT_', '.py', '.js'],
        'Presentations/': ['.pptx', '.ppt', '.docx'],
        'Other/': ['variantes_', 'Variantes_', 'AB_TEST', 'ganchos_']
    },
    
    '05_Technology': {
        'API_Documentation/': ['API_', 'api_', 'API_DOCUMENTATION', 'API_REFERENCE', 'swagger'],
        'CFDI_Files/': ['CFDI_', 'cfdi_', '.xml'],
        'Code_Scripts/': ['.js', '.py', '.ts', 'Automatizacion_IA_CFDI', 'API_CFDI', 'Validador_CFDI'],
        'System_Architecture/': ['ARCHITECTURE', 'architect', 'enterprise_architecture', 'technical_architecture'],
        'Implementation_Guides/': ['DEPLOY', 'SETUP', 'QUICK_START', 'installation', 'setup_'],
        'Technical_Docs/': ['TECHNICAL', 'technical_', 'especificaciones', 'requisitos']
    },
    
    '04_Business_Strategy': {
        'Competitive_Analysis/': ['competitive_', 'Competitive_', 'ANALISIS_COMPETITIVO', 'benchmarking'],
        'Market_Research/': ['market_', 'Market_', 'ANALISIS_MERCADO', 'market_research', 'market_timing'],
        'Business_Plans/': ['business_plan', 'Business_Model', 'comprehensive_business_plan', 'strategy', 'Strategy', 'roadmap'],
        'Investor_Materials/': ['investor_', 'INVESTOR_', 'pitch_deck', 'vc_pitch', 'funding', 'FUNDRAISING', 'TERM_SHEET', 'due_diligence', 'venture_capital'],
        'Strategic_Plans/': ['ESTRATEGIA_', 'estrategia_', 'Strategic_Planning', 'STRATEGIC_PLANNING', 'crecimiento', 'sustainability', 'esg'],
        'Executive_Summaries/': ['Executive_Summary', 'executive_summary', 'RESUMEN_EJECUTIVO', 'FINAL_SUMMARY'],
        'Analysis_Reports/': ['ANALISIS_', 'analisis_', 'Analysis_', 'Report_'],
        'SWOT_Analysis/': ['swot', 'SWOT'],
        'Implementation_Strategies/': ['implementacion', 'implementation', 'enhanced_launch', 'reddit-quora', 'topic-cluster'],
        'Revenue_Strategies/': ['revenue_', 'Revenue_']
    },
    
    '06_Documentation': {
        'Master_Indexes/': ['INDICE', 'INDEX', 'indice_', 'INDEX_', 'INDICE_', 'INDICE_COMPLETO', 'INDICE_MAESTRO'],
        'Organization_Guides/': ['ORGANIZACION', 'RESUMEN_ORGANIZACION'],
        'Project_Overview/': ['PROJECT_STRUCTURE', 'ESTADO_FINAL', 'EXITO_FINAL', 'IMPLEMENTACION_COMPLETADA'],
        'User_Guides/': ['QUICK_START', 'START_HERE', 'INICIO_RAPIDO', 'ACCESO_RAPIDO', 'QuickStart'],
        'Technical_Docs/': ['DOCUMENTACION', 'DOCUMENTATION', 'TECHNICAL', 'technical'],
        'Resumes/': ['RESUMEN_', 'resumen_', 'FINAL_SUMMARY', 'Final_Summary']
    },
    
    '08_AI_Artificial_Intelligence': {
        'Automation/': ['automatizacion_', 'automation_', 'AUTOMATION', 'Automatizacion_'],
        'AI_Systems/': ['ia_', 'IA_', 'ai_', 'AI_', 'artificial_intelligence', 'inteligencia_artificial'],
        'Neural_Networks/': ['neural_', 'NEURAL_'],
        'Machine_Learning/': ['machine_learning', 'ML_', 'prediction_', 'MOTOR_PREDICCION'],
        'Quantum_Computing/': ['quantum', 'QUANTUM'],
        'Advanced_AI/': ['advanced_ai', 'ADVANCED_AI', 'Ultra_AI']
    },
    
    '02_Finance': {
        'ROI_Calculations/': ['roi_', 'ROI_', 'calculadora_roi'],
        'Financial_Models/': ['Financial_Model', 'Financial_Projection', 'modelos_financieros', '.xlsx'],
        'Budget_Analysis/': ['Budget_', 'cost_analysis', 'costos_'],
        'Pricing_Strategy/': ['Pricing_', 'pricing_', 'monetizacion']
    },
    
    '09_Sales': {
        'Sales_Playbooks/': ['Playbook_', 'PLAYBOOKS_', 'playbook'],
        'Conversion_Optimization/': ['conversion_optimization', 'optimizacion_conversion'],
        'Sales_Strategies/': ['sales_', 'SALES_', 'ventas_', 'psicologia_ventas'],
        'Objection_Handling/': ['objection', 'OBJECTION', 'objeciones']
    },
    
    '20_Project_Management': {
        'Implementation_Plans/': ['PLAN_IMPLEMENTACION', 'plan_implementacion', 'implementation_plan'],
        'Operational_Manuals/': ['Manual_Operativo', 'manual_operativo', 'Operational'],
        'Process_Maps/': ['MAPA_PROCESOS', 'DIAGRAMA_PROCESOS'],
        'Playbooks/': ['Playbook_', 'PLAYBOOKS_', 'workflow_', 'WORKFLOW'],
        'SOPs/': ['SOP', 'Procedures', 'procedures']
    },
    
    '07_Risk_Management': {
        'Risk_Assessments/': ['risk_', 'RISK_', 'riesgo', 'ANALISIS_RIESGOS'],
        'Compliance_Docs/': ['compliance', 'COMPLIANCE', 'Legal_', 'LEGAL_'],
        'Crisis_Management/': ['crisis_', 'CRISIS_', 'Crisis_']
    },
    
    '16_Data_Analytics': {
        'Dashboards/': ['dashboard_', 'DASHBOARD_', 'Dashboard_'],
        'KPIs_Metrics/': ['KPI', 'kpi', 'METRICAS_', 'metricas_', 'KPIs_'],
        'Analytics_Reports/': ['analytics', 'ANALYTICS', 'BENCHMARKS']
    }
}

def ensure_subfolder_exists(base_folder, subfolder):
    """Asegura que una subcarpeta existe"""
    subfolder_path = ROOT_DIR / base_folder / subfolder
    subfolder_path.mkdir(parents=True, exist_ok=True)
    return subfolder_path

def find_matching_subfolder(filename, base_folder):
    """Encuentra la subcarpeta apropiada para un archivo"""
    if base_folder not in SUB_FOLDER_MAPPING:
        return None
    
    filename_lower = filename.lower()
    
    # Buscar coincidencias por orden de prioridad (subcarpetas más específicas primero)
    for subfolder, patterns in SUB_FOLDER_MAPPING[base_folder].items():
        for pattern in patterns:
            pattern_lower = pattern.lower()
            if pattern_lower in filename_lower or filename_lower.startswith(pattern_lower) or filename_lower.endswith(pattern_lower.replace('_', '')):
                return subfolder
    
    return None

def organize_files_in_subfolders():
    """Organiza archivos desde carpetas principales a subcarpetas específicas"""
    
    stats = defaultdict(lambda: defaultdict(int))
    moved_files = []
    skipped_files = []
    
    # Procesar cada carpeta principal
    for base_folder in SUB_FOLDER_MAPPING.keys():
        base_path = ROOT_DIR / base_folder
        
        if not base_path.exists() or not base_path.is_dir():
            continue
        
        print(f"\nProcesando {base_folder}...")
        
        # Obtener todos los archivos directamente en la carpeta principal (no en subcarpetas)
        files_in_folder = []
        for item in base_path.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                files_in_folder.append(item)
        
        # Organizar cada archivo
        for filepath in files_in_folder:
            filename = filepath.name
            subfolder = find_matching_subfolder(filename, base_folder)
            
            if subfolder:
                dest_path = ensure_subfolder_exists(base_folder, subfolder)
                target = dest_path / filename
                
                # Evitar sobrescribir
                if target.exists():
                    # Crear nombre único
                    counter = 1
                    name_parts = filepath.stem, filepath.suffix
                    while target.exists():
                        new_name = f"{name_parts[0]}_{counter}{name_parts[1]}"
                        target = dest_path / new_name
                        counter += 1
                
                try:
                    shutil.move(str(filepath), str(target))
                    moved_files.append((filename, base_folder, subfolder))
                    stats[base_folder][subfolder] += 1
                    print(f"  ✓ {filename} → {base_folder}/{subfolder}")
                except Exception as e:
                    skipped_files.append(f"{filename} (error: {str(e)})")
            else:
                # Si no hay subcarpeta específica, dejar en la carpeta principal
                stats[base_folder]['_root'] += 1
    
    # Mostrar resumen
    print("\n" + "="*80)
    print("RESUMEN DE ORGANIZACIÓN MEJORADA")
    print("="*80 + "\n")
    
    total_moved = len(moved_files)
    print(f"Total de archivos reorganizados: {total_moved}\n")
    
    for base_folder in sorted(stats.keys()):
        print(f"{base_folder}:")
        folder_stats = stats[base_folder]
        total_in_folder = sum(folder_stats.values())
        
        for subfolder in sorted(folder_stats.keys()):
            if subfolder == '_root':
                print(f"  [Raíz]: {folder_stats[subfolder]} archivos")
            else:
                print(f"  {subfolder}: {folder_stats[subfolder]} archivos")
        
        print(f"  Total: {total_in_folder} archivos\n")
    
    if skipped_files:
        print(f"\nArchivos omitidos: {len(skipped_files)}")
        for f in skipped_files[:5]:
            print(f"  - {f}")
        if len(skipped_files) > 5:
            print(f"  ... y {len(skipped_files) - 5} más")
    
    print("\n" + "="*80)
    print("ORGANIZACIÓN MEJORADA COMPLETADA")
    print("="*80 + "\n")
    
    return moved_files, stats

if __name__ == '__main__':
    print("Iniciando organización mejorada de archivos en subcarpetas...")
    organize_files_in_subfolders()

