#!/usr/bin/env python3
"""
Script para organizar archivos de la raíz del proyecto en carpetas apropiadas
basado en la estructura definida en ORGANIZACION_MAESTRA.md
"""

import os
import shutil
from pathlib import Path

# Definir el directorio raíz
ROOT_DIR = Path(__file__).parent

# Definir patrones de archivos y sus destinos
FILE_PATTERNS = {
    # Marketing - CTAs, DMs, Blogs, Secuencias
    '01_Marketing': [
        'ctas_', 'CTA', 'dm_', 'DM_', 'DMs_', 'blog_', 'secuencia_', 'email_',
        'calendario_', 'checklist_curso', 'checklist_saas', 'checklist_ia',
        'ganchos_', 'plantillas_', 'plantilla_', 'Templates_', 'version_',
        'OUTREACH', 'LEAD_MAGNET', 'AB_TEST', 'BEST_PRACTICES', 'variantes_',
        'Variantes_', 'CHANNEL', 'SUBJECT', 'SNIPPETS', 'LOCALISMOS',
        'WORKFLOW_VISUAL', 'GLOSSARY_OUTREACH', 'FAQ_EXPANDIDO', 'CHANGELOG_OUTREACH',
        'INDEX_DM', 'CHECKLIST_OUTREACH', 'CALENDAR_TEMPLATE', 'CALENDARIO_OUTREACH',
        'CASOS_EXITO_OUTREACH', 'ANTI_PATTERNS_OUTREACH', 'TROUBLESHOOTING_OUTREACH',
        'GUIA_RAPIDA_PERSONALIZACION', 'SISTEMA_SEGUIMIENTO_DM', 'PLANTILLAS_RESPUESTAS_DM',
        'OUTREACH_MESSAGES', 'MULTILINGUAL_DM', 'SCRIPTS_DM', 'SECTORES_REGULADOS_DM',
        'secuencias_automatizacion_dm', 'follow_up_sequence', 'email_nurture_sequences',
        'email_sequence_', 'EMAIL_SHARE', 'Bumps_', 'content_calendar_', 'SEO_',
        'seo_', 'Ideas_', 'ideas_', 'Viral_', 'viral_', 'post_linkedin_', 'ENTREGABLE2',
        'Entregable2_', '01_DM_', '02_DM_', '03_DM_', '02_secuencia', '03_secuencia',
        '53_LEAD_MAGNET', '53_CHECKLIST', 'ESQUEMA_LEAD_MAGNET', 'COPY_PASTE_READY_DMS',
        'AUTO_DMS_', '00_INDICE_DMS', 'ACTIVECAMPAIGN', 'CRM_OUTREACH', 'MAILCHIMP_EXPORT',
        'SAMPLE_LEADS', 'DM_Variants'
    ],
    
    # Technology - Código, APIs, Arquitectura
    '05_Technology': [
        '.js', '.py', '.ts', 'API_', 'server.js', 'Dockerfile', 'docker-compose',
        'ARCHITECTURE', 'ARCHITECT', 'API_DOCUMENTATION', 'DEPLOY', 'SETUP_GUIDE',
        'DEVOPS', 'INFRASTRUCTURE', 'MICROSERVICES', 'QUANTUM_COMPUTING', 'BLOCKCHAIN',
        'EDGE_COMPUTING', 'IOT_', 'AR_VR', 'METAVERSE', 'WEB3', 'SPACE_TECH',
        'INDUSTRY_4_0', 'FUTURE_TECH', 'DATA_ENGINEERING', 'DATA_GOVERNANCE',
        'DATA_SCIENCE', 'MLOPS', 'MONITORING', 'PERFORMANCE', 'OPTIMIZATION',
        'REMOTE_WORK', 'package.json', 'tsconfig.json', 'jest.config', '.babelrc',
        '.eslintrc', '.prettierrc', '.nvmrc', '.gitignore', '.dockerignore',
        '.editorconfig', '.gitattributes', 'requirements.txt', 'Makefile',
        'swagger.json', 'nginx.conf', 'robots.txt', 'sitemap.xml', 'vercel.json',
        'env.example', 'config.json', 'CFDI_', 'Automatizacion_IA_CFDI',
        'API_CFDI', 'Validador_CFDI', 'Integracion_ERP_CFDI', 'Guia_Tecnica_CFDI',
        'Guia_Completa_CFDI', 'README_CFDI', 'Ejemplos_Uso_CFDI', 'Dashboard_CFDI',
        'requisitos_sat_cfdi', 'especificaciones_tecnicas', 'Validador_DM.py',
        'SCRIPT_GENERADOR_DM.py', 'install.sh', 'nvm-setup.sh'
    ],
    
    # Documentation - READMEs, Índices, Guías Generales
    '06_Documentation': [
        'README', 'INDEX', 'INDICE', 'MASTER_QUICK_REFERENCE', 'START_HERE',
        'QUICK_START', 'QuickStart', 'INICIO_RAPIDO', 'ACCESO_RAPIDO',
        'DOCUMENTACION', 'ORGANIZACION', 'PROJECT_STRUCTURE', 'ATTRIBUTIONS',
        'CODE_OF_CONDUCT', 'CONTRIBUTING', 'LICENSE', 'CHANGELOG', 'GLOSSARY',
        'FAQ', 'TROUBLESHOOTING', 'NOTION_IMPORT', 'VENDOR_MANAGEMENT',
        'PROJECT_STATUS', 'ESTADO_FINAL', 'EXITO_FINAL', 'IMPLEMENTACION_COMPLETADA',
        'ESTADO_FINAL', 'RESUMEN_FINAL', 'RESUMEN_EJECUTIVO', 'FINAL_SUMMARY',
        'ACTUALIZACIONES_COMPLETADAS'
    ],
    
    # Business Strategy - Estrategias, Análisis, Planes
    '04_Business_Strategy': [
        'ESTRATEGIA_', 'estrategia_', 'Business_Model', 'business_overview',
        'business_plan', 'comprehensive_business_plan', 'go_to_market',
        'Competitive_', 'competitive_', 'Market_Intelligence', 'market_research',
        'market_timing', 'SWOT', 'swot_', 'ANALISIS_', 'analisis_', 'analisis_',
        'Business_Impact', 'business_intelligence', 'Strategic_Planning',
        'STRATEGIC_PLANNING', 'ANALISIS_MERCADO', 'ANALISIS_OPERATIVO',
        'ANALISIS_RIESGOS', 'DECISION_FINAL', 'Investment_Thesis',
        'INVESTOR_PRESENTATION', 'investor_pitch', 'pitch_deck', 'vc_pitch',
        'INVESTOR_', 'FUNDRAISING', 'FUNDING', 'TERM_SHEET', 'due_diligence',
        'Executive_Dashboard', 'executive_summary', 'PRESENTATION', 'proposal',
        'comprehensive_vc', 'master_vc', 'ultimate_vc', 'most_advanced_pitch',
        'most_comprehensive_pitch', 'FINAL_PRESENTATION', 'vc_evaluation',
        'vc_objection', 'vc_screening', 'INVESTOR_DATA_ROOM', 'INVESTOR_RELATIONSHIP',
        'INVESTOR_FAQ', 'LEAD_READINESS', 'dashboard_ejecutivo', 'Enhanced_Market',
        'INTERACTIVE_VC', 'mobile_vc'
    ],
    
    # Finance - ROI, Calculadoras, Modelos Financieros
    '02_Finance': [
        'ROI_', 'roi_', 'calculadora_roi', 'ltv_', 'Budget_', 'cost_analysis',
        'Financial_', 'financial_', 'Financial_Model', 'Financial_Projection',
        'Revenue_', 'revenue_', 'Pricing_', 'pricing_', 'PRICING', 'monetizacion',
        'costos_', 'modelos_financieros', 'modelo_prediccion', 'Investment_Thesis',
        'valuation', 'VALUATION', '12_Month_Financial', 'COST', 'BUDGET'
    ],
    
    # AI & Automation - IA, Automatización
    '08_AI_Artificial_Intelligence': [
        'automatizacion_', 'automation_', 'AUTOMATION', 'ia_', 'IA_', 'AI_',
        'artificial_intelligence', 'inteligencia_artificial', 'neural_',
        'machine_learning', 'MOTOR_PREDICCION', 'ai_', 'AI_Course', 'ai_course',
        'MORNINGSCORE_OMNIPOTENCE', 'NEURAL_COMPETITIVE', 'personalizacion_ia',
        'quantum_computing', 'autonomous_systems', 'advanced_ai', 'ai_features',
        'ai_models', 'ai_technology', 'ai_ethics', 'ai_analytics', 'ai_testimonial',
        'automated_scoring', 'automation_workflow', 'automatizaciones_ia',
        'inteligencia_artificial_transformadora', 'inteligencia_mercado',
        'ia_avanzada_automatizacion', 'ia_analisis_datos', 'OPORTUNIDADES_AUTOMATIZACION',
        'AUDITORIA_AUTOMATIZACION', 'AUTOMATION_PLAYBOOK', 'Scripts_Automatizacion'
    ],
    
    # Sales - Ventas, Playbooks
    '09_Sales': [
        'SALES_', 'sales_', 'ventas_', 'psicologia_ventas', 'scripts_ventas',
        'SALES_EXCELLENCE', 'product_demo', 'conversion_optimization',
        'optimizacion_conversion', 'conversion_optimization_strategies',
        'Playbook_Objections', 'objection_handling', 'OBJECTION_HANDLING',
        'retention_loyalty', 'revenue_optimization', 'upselling', 'social_proof',
        'triggers_psicologicos', 'elementos_persuasion', 'elementos_persuasivos',
        'elementos_tecnicos_conversion', 'optimizacion_final_conversion',
        'optimizacion_conversion_avanzada', 'optimizacion_conversion_linkedin',
        'variantes_ab_testing_ctas', 'resumen_ctas_ia_optimizadas'
    ],
    
    # Risk Management & Compliance
    '07_Risk_Management': [
        'RISK_', 'risk_', 'riesgo', 'riesgos', 'COMPLIANCE', 'compliance_',
        'Legal_', 'legal_', 'LEGAL_', 'Audit_', 'auditoria_', 'AUDITORIA_',
        'Disaster_Recovery', 'DISASTER_RECOVERY', 'crisis_management', 'CRISIS_',
        'Crisis_', 'business_continuity', 'contingency', 'stakeholder_engagement',
        'Stakeholder_', 'Emergency_', 'Recovery_', 'matriz_gestion_riesgos',
        'matriz_riesgos_operativos', 'ANALISIS_RIESGOS', 'Compliance_Legal',
        'legal_compliance', 'global_regulatory', 'marco_legal', 'gobernanza_compliance',
        'LEGAL_PRIVACY', 'REGTECH_COMPLIANCE', 'Regulatory_Updates'
    ],
    
    # Operations & Project Management
    '20_Project_Management': [
        'PROJECT_MANAGEMENT', 'project_management', 'PLAN_', 'plan_', 'PLAN_MAESTRO',
        'PLAN_IMPLEMENTACION', 'plan_implementacion', 'plan_lanzamiento',
        'plan_contable', 'plan_sostenibilidad', 'plan_transformacion',
        'plan_internacionalizacion', 'plan_accion', 'plan_continuidad',
        'plan_crisis', 'Timeline_', 'Resource_Management', 'OPERATIONS_',
        'operations_', 'operational_', 'OPERATIONAL', 'Manual_Operativo',
        'MAPA_PROCESOS', 'DIAGRAMA_PROCESOS', 'EJECUCION_SEGUIMIENTO',
        'HERRAMIENTAS_IMPLEMENTACION', 'KIT_IMPLEMENTACION', 'PRACTICAL_IMPLEMENTATION',
        'TACTICAL_IMPLEMENTATION', 'implementation_playbook', 'Playbook_',
        'PLAYBOOKS_', 'guide_', 'GUIDE_', 'WORKFLOW', 'workflow_', 'PROCESS_',
        'process_', 'procedures', 'Procedures', 'SOP', 'manual_', 'Manual_',
        'OPERATIONS_MANAGEMENT', 'Change_Management', 'CHANGE_MANAGEMENT',
        'change_management', 'gestion_cambio', 'gestion_conocimiento'
    ],
    
    # Advanced Features
    '07_Advanced_Features': [
        'ADVANCED_', 'advanced_', 'Ultra_', 'SUPREMO', 'MAESTRO', 'MASTER_',
        'REVOLUCIONARIO', 'REVOLUTIONARY', 'Features', 'FEATURES', 'ULTRA_',
        'SOFISTICADAS', 'HYPER_', 'MEJORADOS', 'MEJORADAS', 'OPTIMIZADAS',
        'COMPLETOS', 'COMPLETAS', 'DEFINITIVOS', 'DEFINITIVAS', 'FINAL_',
        'FINALES', 'Enhanced_', 'MASTER_DEFINITIVO', 'ECO_MASTER'
    ],
    
    # Research & Development
    '11_Research_Development': [
        'R&D', 'RESEARCH', 'research_', 'Innovation_', 'INNOVATION', 'innovation_',
        'innovacion_', 'R&D_Projects', 'Innovation_Labs', 'Research_Papers',
        'laboratorio_innovacion', 'INVESTIGACION', 'investigacion_', 'market_research',
        'competitive_intelligence', 'benchmarking', 'INDUSTRY_BENCHMARKS'
    ],
    
    # Customer Service
    '10_Customer_Service': [
        'CUSTOMER_', 'customer_', 'ONBOARDING', 'onboarding_', 'Customer_Journey',
        'customer_journey', 'Customer_Success', 'customer_success', 'Support_',
        'support_', 'retention', 'anti_churn', 'churn', 'customer_experience',
        'CUSTOMER_EXPERIENCE', 'CUSTOMER_SERVICE', 'atencion_cliente',
        'automatizacion_atencion_cliente'
    ],
    
    # Human Resources
    '03_Human_Resources': [
        'HR_', 'TALENT_', 'talent_', 'Hiring_', 'hiring_', 'onboarding_playbook',
        'TALENT_MANAGEMENT', 'TALENT_ACQUISITION', 'Human_Resources', 'RRHH',
        'rrhh', 'RECURSOS_HUMANOS', 'Team_Talent', 'TEAM_ROLES', 'LEADERSHIP_',
        'leadership_', 'LIDERAZGO_', 'cultura_organizacional', 'gestion_talento',
        'performance_management', 'employee_engagement', 'Team_Management',
        'PLAN_CAPACITACION', 'programas_capacitacion', 'TRAINING_', 'training_',
        'LEADERSHIP_DEVELOPMENT', 'PLAN_LIDERAZGO', 'PLAN_COMUNICACION'
    ],
    
    # System Architecture
    '11_System_Architecture': [
        'SYSTEM_ARCHITECTURE', 'System_Architecture', 'System_Design',
        'Infrastructure', 'Deployment', 'technical_architecture',
        'enterprise_architecture', 'technical_specifications'
    ],
    
    # Quality Assurance
    '12_Quality_Assurance': [
        'QA_', 'QUALITY_', 'quality_', 'Testing_', 'testing_', 'Quality_Standards',
        'QA_Processes', 'Quality_Management', 'Testing_Validation'
    ],
    
    # Analytics & Data
    '16_Data_Analytics': [
        'analytics_', 'ANALYTICS', 'analytics', 'metricas_', 'METRICAS_', 'KPIs',
        'kpi', 'KPI', 'dashboard_', 'DASHBOARD_', 'Dashboard_', 'Executive_Dashboard',
        'Enhanced_Market_Analysis_Dashboard', 'KPI_DASHBOARD', 'KPIs_Dashboard',
        'dashboard_ejecutivo', 'dashboard_monitoreo', 'dashboard_metricas',
        'data_', 'DATA_', 'Business_Intelligence', 'business_intelligence',
        'competitive_intelligence', 'inteligencia_mercado', 'benchmarking_',
        'BENCHMARKS', 'indice_completo_kpis', 'metricas_kpis', 'METRICAS_KPIS',
        'METRICAS_AVANZADAS', 'metricas_kpis_seguimiento'
    ],
    
    # Sustainability & ESG
    '18_Sustainability': [
        'SUSTAINABLE', 'sustainable', 'SUSTAINABILITY', 'sustainability_',
        'sostenibilidad_', 'ESG_', 'esg_', 'green_', 'carbon_footprint',
        'economia_circular', 'SOSTENIBILIDAD', 'plan_sostenibilidad'
    ],
    
    # International Business
    '19_International_Business': [
        'INTERNATIONAL', 'international_', 'GLOBAL_', 'global_', 'GLOBAL_EXPANSION',
        'internacionalizacion', 'expansion_internacional', 'international_expansion',
        'GLOBAL_EXPANSION_MASTERY', 'EXPANSION_INTERNACIONAL', 'mercados_globales'
    ]
}

# Archivos que deben quedarse en la raíz (configuración del proyecto)
KEEP_IN_ROOT = [
    '.git', '.gitignore', '.gitattributes', '.DS_Store',
    'package.json', 'tsconfig.json', 'jest.config.js', '.babelrc.js',
    '.eslintrc.js', '.prettierrc', '.prettierrc.js', '.nvmrc',
    '.dockerignore', '.editorconfig', 'requirements.txt', 'Makefile',
    'swagger.json', 'docker-compose.yml', 'Dockerfile', 'nginx.conf',
    'robots.txt', 'sitemap.xml', 'vercel.json', 'env.example', 'config.json',
    'LICENSE', 'README.md', 'CHANGELOG.md', 'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md',
    'ATTRIBUTIONS.md', 'PROJECT_STRUCTURE.md', 'install.sh', 'nvm-setup.sh'
]

def organize_files():
    """Organiza los archivos de la raíz a las carpetas apropiadas"""
    
    moved_files = {}
    skipped_files = []
    
    # Obtener todos los archivos en la raíz (solo archivos, no directorios)
    root_files = [f for f in os.listdir(ROOT_DIR) 
                  if os.path.isfile(os.path.join(ROOT_DIR, f))]
    
    for filename in root_files:
        # Saltar archivos que deben quedarse en la raíz
        if filename in KEEP_IN_ROOT:
            continue
        
        # Determinar a qué carpeta mover el archivo
        destination = None
        
        for folder, patterns in FILE_PATTERNS.items():
            folder_path = ROOT_DIR / folder
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
            
            # Verificar si el archivo coincide con alguno de los patrones
            for pattern in patterns:
                if pattern.lower() in filename.lower():
                    destination = folder_path
                    break
            
            if destination:
                break
        
        # Si no se encontró destino, mover a Documentation por defecto
        if not destination:
            destination = ROOT_DIR / '06_Documentation'
            if not destination.exists():
                destination.mkdir(parents=True, exist_ok=True)
        
        # Mover el archivo
        try:
            source = ROOT_DIR / filename
            target = destination / filename
            
            # Si ya existe en el destino, no mover
            if target.exists():
                skipped_files.append(f"{filename} (ya existe en {destination.name})")
                continue
            
            shutil.move(str(source), str(target))
            
            if destination.name not in moved_files:
                moved_files[destination.name] = []
            moved_files[destination.name].append(filename)
            
        except Exception as e:
            skipped_files.append(f"{filename} (error: {str(e)})")
    
    # Mostrar resumen
    print("\n" + "="*80)
    print("RESUMEN DE ORGANIZACIÓN DE ARCHIVOS")
    print("="*80 + "\n")
    
    total_moved = sum(len(files) for files in moved_files.values())
    print(f"Total de archivos movidos: {total_moved}\n")
    
    for folder, files in sorted(moved_files.items()):
        print(f"{folder}: {len(files)} archivos")
        if len(files) <= 10:
            for f in files:
                print(f"  - {f}")
        else:
            for f in files[:5]:
                print(f"  - {f}")
            print(f"  ... y {len(files) - 5} archivos más")
        print()
    
    if skipped_files:
        print(f"\nArchivos omitidos: {len(skipped_files)}")
        for f in skipped_files[:10]:
            print(f"  - {f}")
        if len(skipped_files) > 10:
            print(f"  ... y {len(skipped_files) - 10} más")
    
    print("\n" + "="*80)
    print("ORGANIZACIÓN COMPLETADA")
    print("="*80 + "\n")

if __name__ == '__main__':
    print("Iniciando organización de archivos...")
    organize_files()

