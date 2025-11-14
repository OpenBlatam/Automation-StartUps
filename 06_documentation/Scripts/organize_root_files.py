#!/usr/bin/env python3
"""
Script para organizar archivos del directorio raíz en carpetas apropiadas
"""
import os
import shutil
from pathlib import Path

# Directorio base
BASE_DIR = Path(__file__).parent

# Mapeo de patrones de archivos a carpetas destino
FILE_MAPPINGS = {
    # Email seguimiento -> 01_marketing/Sequences o 04_email_marketing
    '00_EMAIL_SEGUIMIENTO': '01_marketing/Sequences',
    '00_EMAIL_SUBJECT': '01_marketing/Sequences',
    '00_EMAILS_TRANSACCIONALES': '01_marketing/04_email_marketing',
    '00_guia_rapida_secuencias_email': '01_marketing/Sequences',
    '13_secuencias_email_completas': '01_marketing/Sequences',
    
    # Marketing/Webinars (01_, 02_, 03_)
    '01_brainstorm_posts': '01_marketing',
    '01_captions_instagram': '01_marketing',
    '01_captions_repost': '01_marketing',
    '01_dm_curso_ia_webinars': '01_marketing',
    '01_hooks_tiktok': '01_marketing',
    '01_polls': '01_marketing',
    '01_POST_CURSO_IA_WEBINARS': '01_marketing',
    '01_post_mito_realidad': '01_marketing',
    '01_propuesta_valor': '01_marketing',
    '01_secuencia_course_webinars': '01_marketing/Sequences',
    '01_webinar_campaign': '01_webinar_campaign',
    
    '02_brainstorm_posts': '01_marketing',
    '02_captions_instagram': '01_marketing',
    '02_captions_repost': '01_marketing',
    '02_DM_SAAS_IA_MARKETING': '01_marketing',
    '02_hooks_tiktok': '01_marketing',
    '02_polls': '01_marketing',
    '02_post_mito_realidad': '01_marketing',
    '02_POST_SAAS_IA_MARKETING': '01_marketing',
    '02_propuesta_valor': '01_marketing',
    '02_secuencia_saas_ia_marketing': '01_marketing/Sequences',
    
    '03_brainstorm_posts': '01_marketing',
    '03_captions_instagram': '01_marketing',
    '03_captions_repost': '01_marketing',
    '03_dm_ia_bulk_documentos': '01_marketing',
    '03_hooks_tiktok': '01_marketing',
    '03_polls': '01_marketing',
    '03_POST_IA_BULK_DOCUMENTOS': '01_marketing',
    '03_post_mito_realidad': '01_marketing',
    '03_propuesta_valor': '01_marketing',
    '03_secuencia_ia_bulk_documentos': '01_marketing/Sequences',
    
    # AI related
    '00_FRONTEND_IA': '08_ai_artificial_intelligence',
    '00_EMAIL_SEGUIMIENTO_IA': '01_marketing/Sequences',
    
    # Sales
    '15_playbook_closing': '09_sales',
    '22_call_scripts': '09_sales',
    'INDICE_MAESTRO_VENTAS': '09_sales',
    'RESUMEN_EJECUTIVO_VENTAS': '09_sales',
    'ANALISIS_PROCESO_VENTAS': '09_sales',
    'SALES_ENABLEMENT': '09_sales',
    '27_SALES_ENABLEMENT': '09_sales',
    
    # Documentation
    '00_README': '06_documentation',
    '00_QUICK_START': '06_documentation',
    '00_GUIA_DIRECCION': '06_documentation',
    '00_DEPLOY': '06_documentation',
    '00_FIRST_RUN': '06_documentation',
    '00_HARDENING': '06_documentation',
    '00_HEALTH_CHECKS': '06_documentation',
    '00_CHECKLIST_OPERATIVO': '06_documentation',
    '00_PRE_DEMO': '06_documentation',
    '00_MAKE_IMPLEMENTATION': '06_documentation',
    '00_MAKE_SCENARIO': '06_documentation',
    '00_INTEGRATIONS_SLACK': '06_documentation',
    '00_LOOKER_STUDIO': '06_documentation',
    '00_NOTION_PACK': '06_documentation',
    '00_PROMPTS_BLOCKS': '06_documentation',
    '00_PROMPTS_GTM': '06_documentation',
    '00_DASHBOARD_TEMPLATE': '06_documentation',
    '00_DATA_DICTIONARY': '06_documentation',
    '00_CRM_PROPERTIES': '06_documentation',
    '00_HUBSPOT_PROPERTY': '06_documentation',
    '00_CSV_IMPORT': '06_documentation',
    '00_SAMPLE_LEADS': '06_documentation',
    '00_ENV_EXAMPLE': '06_documentation',
    '00_BUNDLE_MANIFEST': '06_documentation',
    '00_ZIP_BUNDLE': '06_documentation',
    '00_VERSION_MANAGEMENT': '00_version_management',
    '00_version_management': '00_version_management',
    'api_documentation': '06_documentation',
    'code_of_conduct': '06_documentation',
    'readme_ig_dms': '06_documentation',
    'README_Sheets_Import': '06_documentation',
    
    # Strategy
    '00_ESTRATEGIA_INNOVACION': '06_strategy',
    '00_ONE_PAGER_EJECUTIVO': '06_strategy',
    '00_README_INNOVACION': '06_strategy',
    '06_RECURSOS_AVANZADOS_STRATEGY': '06_strategy',
    '17_analisis_competencia_strategy': '06_strategy',
    '25_INDUSTRY_SPECIFIC_PLAYBOOKS': '06_strategy',
    'PLAYBOOKS_POR_INDUSTRIA': '06_strategy',
    
    # Analytics/Dashboards
    '00_CALCULADORA_ROI': '16_data_analytics',
    '14_calculadoras_formulas_roi': '16_data_analytics',
    '00_EXPERIMENTS_AB_TEST': '16_data_analytics',
    '19_analytics_dashboard_templates': '16_data_analytics',
    '39_EXECUTIVE_DASHBOARD_SPEC': '16_data_analytics',
    '11_library_metricas_publicas': '16_data_analytics',
    '36_KPI_BENCHMARKS': '16_data_analytics',
    'METRICAS_AVANZADAS_ANALISIS': '16_data_analytics',
    'KPI_Data_Dictionary': '16_data_analytics',
    'Data_Dictionary': '16_data_analytics',
    'google_sheets_dashboard_guia': '16_data_analytics',
    'roi_snapshot_guia': '16_data_analytics',
    'advanced_analyzer.py': '16_data_analytics',
    'advanced_dashboard.html': '16_data_analytics',
    'advanced_analysis.json': '16_data_analytics',
    
    # Legal/Compliance
    '00_CONTRATO_OUTCOME': '13_legal_compliance',
    '00_EMAIL_SEGUIMIENTO_COMPLIANCE': '13_legal_compliance',
    '00_KIT_OBJECIONES_INDUSTRIA': '13_legal_compliance',
    '00_SCRIPT_OBJECCION': '13_legal_compliance',
    'LEGAL_PRIVACY_CHECKLIST': '13_legal_compliance',
    '35_OUTREACH_COMPLIANCE_LEGAL_GUIDE': '13_legal_compliance',
    'SECTORES_REGULADOS_DM': '13_legal_compliance',
    'ANTI_PATTERNS_OUTREACH': '13_legal_compliance',
    
    # Operations
    '00_AUTOMATIONS_BLUEPRINTS': '04_operations',
    '00_SCALING_PLAN': '04_operations',
    '00_DM_STARTER': '04_operations',
    '00_MICRO_DMS': '04_operations',
    '00_SECUENCIA_WHATSAPP': '04_operations',
    '00_indice_dms_completos': '04_operations',
    '04_automatizacion_escalamiento_dms': '04_operations',
    '26_ADVANCED_AUTOMATION_WORKFLOWS': '04_operations',
    'ZAPS_MAPPINGS': '04_operations',
    'MULTILINGUAL_DM_GENERATOR_PROMPTS': '04_operations',
    'guia_rapida_personalizacion_dm': '04_operations',
    'AB_TEST_MATRIX_DM': '04_operations',
    
    # Business Strategy
    '00_BRAND_STYLE_GUIDE': '04_business_strategy',
    '00_PROPUESTA_AUTOFILL': '04_business_strategy',
    '00_EMAIL_OUTREACH_PYME': '04_business_strategy',
    'MANIFEST_ESCALERA_VALOR': '04_business_strategy',
    'ESTRATEGIAS_POR_CANAL': '04_business_strategy',
    
    # Customer Service
    '00_EMAIL_SEGUIMIENTO_RECURSOS_SOPORTE': '10_customer_service',
    '00_EMAIL_SEGUIMIENTO_FEEDBACK': '10_customer_service',
    'troubleshooting': '10_customer_service',
    'troubleshooting_rapido': '10_customer_service',
    'troubleshooting_recomendaciones': '10_customer_service',
    
    # Quality Assurance
    '00_EMAIL_SEGUIMIENTO_TESTING': '12_quality_assurance',
    'checklist_calidad_pre_envio': '12_quality_assurance',
    'qa_checklist_sequences': '12_quality_assurance',
    '23_qa_rubric_dm_copy': '12_quality_assurance',
    'Minimal_Test_Run_Checklist': '12_quality_assurance',
    
    # Product Management
    '00_EMAIL_SEGUIMIENTO_PRICING': '14_product_management',
    '29_PRICING_PACKAGING_STRATEGY': '14_product_management',
    
    # Customer Experience
    '00_EMAIL_SEGUIMIENTO_EXITO_CLIENTE': '15_customer_experience',
    '00_EMAIL_SEGUIMIENTO_ONBOARDING': '15_customer_experience',
    '00_EMAIL_SEGUIMIENTO_RE_ENGAGEMENT': '15_customer_experience',
    '00_EMAIL_SEGUIMIENTO_RETENCION': '15_customer_experience',
    'Reactivacion_30_60_90': '15_customer_experience',
    
    # Innovation
    '00_EMAIL_SEGUIMIENTO_TRANSFORMACION': '17_innovation',
    '00_EMAIL_SEGUIMIENTO_ESCALAMIENTO': '17_innovation',
    '00_EMAIL_SEGUIMIENTO_MONETIZACION': '17_innovation',
    
    # Crisis Management
    '18_crisis_communication_playbook': '07_risk_management',
    '00_EMAIL_SEGUIMIENTO_CRISIS': '07_risk_management',
    
    # Templates
    '00_EMAIL_SEGUIMIENTO_TEMPLATES': '06_documentation/Templates',
    '00_templates_respuestas_rapidas': '06_documentation/Templates',
    '08_templates_respuestas_rapidas': '06_documentation/Templates',
    '10_templates_visuales_presentaciones': '06_documentation/Templates',
    'templates_prompts_recomendaciones': '06_documentation/Templates',
    'templates_visuales_videos': '06_documentation/Templates',
    'TEMPLATES_SEGUIMIENTO_LINKEDIN_EMAIL': '06_documentation/Templates',
    'WA_Templates_Index': '06_documentation/Templates',
    
    # Guides
    '00_EMAIL_SEGUIMIENTO_PLAYBOOK': '06_documentation',
    '00_EMAIL_SEGUIMIENTO_GUIA': '06_documentation',
    'guia_implementacion_paso_a_paso': '06_documentation',
    '12_guia_investigacion_leads': '09_sales',
    '16_quick_reference_guide': '06_documentation',
    '30_GOVERNANCE_VERSIONING_GUIDE': '06_documentation',
    '31_ONBOARDING_IMPLEMENTATION_GUIDE': '06_documentation',
    '32_CUSTOMER_SUCCESS_PLAYBOOK': '15_customer_experience',
    '33_REENGAGEMENT_NURTURE_ENGINE': '15_customer_experience',
    '34_SECURITY_PROCUREMENT_PACK': '13_legal_compliance',
    '37_GOOGLE_SHEETS_IMPLEMENTATION_GUIDE': '06_documentation',
    '38_APPS_SCRIPT_ALERTS': '06_documentation',
    'GUIA_COACHING_MANAGERS': '06_documentation',
    
    # Lead Magnets
    '51_LEAD_MAGNET': '01_marketing/05_lead_generation',
    '52_LEAD_MAGNET': '01_marketing/05_lead_generation',
    'LEAD_MAGNET_2': '01_marketing/05_lead_generation',
    
    # Other specific files
    '00_EMAIL_SEGUIMIENTO_INDICE_MAESTRO': '01_marketing/Sequences',
    'indice_completo': '06_documentation',
    '00_EMAIL_SEGUIMIENTO_ANALYTICS': '16_data_analytics',
    '00_EMAIL_SEGUIMIENTO_REPORTING': '16_data_analytics',
    '00_EMAIL_SEGUIMIENTO_ROI_ANALYSIS': '16_data_analytics',
    '00_EMAIL_SEGUIMIENTO_SCORING_LEADS': '09_sales',
    '00_EMAIL_SEGUIMIENTO_OPTIMIZACION': '01_marketing',
    '00_EMAIL_SEGUIMIENTO_MARKETING': '01_marketing',
    '00_EMAIL_SEGUIMIENTO_LANDING_PAGES': '01_marketing',
    '00_EMAIL_SEGUIMIENTO_FORMULARIOS': '01_marketing',
    '00_EMAIL_SEGUIMIENTO_CONTENIDO_SOCIAL': '01_marketing',
    '00_EMAIL_SEGUIMIENTO_COPYWRITING': '01_marketing',
    '00_EMAIL_SEGUIMIENTO_DISENO_VISUAL': '01_marketing',
    '00_EMAIL_SEGUIMIENTO_VIDEO_TUTORIALES': '06_documentation',
    '00_EMAIL_SEGUIMIENTO_PRESENTACIONES': '06_documentation',
    '00_EMAIL_SEGUIMIENTO_DOCUMENTACION': '06_documentation',
    '00_EMAIL_SEGUIMIENTO_CASOS_USO': '06_documentation',
    '00_EMAIL_SEGUIMIENTO_CASOS_EXITO': '06_documentation',
    '00_EMAIL_SEGUIMIENTO_MEJORES_PRACTICAS': '06_documentation',
    '00_EMAIL_SEGUIMIENTO_INTEGRACIONES': '06_documentation',
    '00_EMAIL_SEGUIMIENTO_MIGRACION': '06_documentation',
    '00_EMAIL_SEGUIMIENTO_SEGURIDAD': '13_legal_compliance',
    '00_EMAIL_SEGUIMIENTO_BACKUP': '04_operations',
    '00_EMAIL_SEGUIMIENTO_MANTENIMIENTO': '04_operations',
    '00_EMAIL_SEGUIMIENTO_OPTIMIZACION_COSTOS': '02_finance',
    '00_EMAIL_SEGUIMIENTO_INTERNACIONALIZACION': '19_international_business',
    '00_EMAIL_SEGUIMIENTO_PARTNERSHIPS': '04_business_strategy',
    '00_EMAIL_SEGUIMIENTO_COMMUNITY': '01_marketing',
    '00_EMAIL_SEGUIMIENTO_GAMIFICACION': '01_marketing',
    '00_EMAIL_SEGUIMIENTO_VIRALIZACION': '01_marketing',
    '00_EMAIL_SEGUIMIENTO_GO_TO_MARKET': '04_business_strategy',
    '00_EMAIL_SEGUIMIENTO_OBJECIONES': '09_sales',
    '00_EMAIL_SEGUIMIENTO_UPSELL': '09_sales',
    '00_EMAIL_SEGUIMIENTO_POST_CONVERSION': '09_sales',
    '00_EMAIL_SEGUIMIENTO_APRENDIZAJE': '06_documentation',
    '00_EMAIL_SEGUIMIENTO_CERTIFICACION': '06_documentation',
    '00_EMAIL_SEGUIMIENTO_CHECKLISTS': '06_documentation',
    '00_EMAIL_SEGUIMIENTO_SCRIPTS': '04_operations',
    '00_EMAIL_SEGUIMIENTO_TROUBLESHOOTING': '10_customer_service',
    '00_EMAIL_SEGUIMIENTO_DELIVERABILITY': '01_marketing',
    '00_EMAIL_SEGUIMIENTO_ANALISIS_COMPETENCIA': '06_strategy',
    '00_EMAIL_SEGUIMIENTO_COMPETENCIA': '06_strategy',
    '00_EMAIL_SEGUIMIENTO_ESCALAMIENTO_MASIVO': '17_innovation',
    '00_EMAIL_SEGUIMIENTO_ESCALAMIENTO_EMPRESARIAL': '17_innovation',
    '00_EMAIL_SEGUIMIENTO_RECURSOS_ADICIONALES': '06_documentation',
    '00_EMAIL_SEGUIMIENTO_OPTIMIZACION_CONTINUA': '01_marketing',
    '00_EMAIL_SEGUIMIENTO_OPTIMIZACION_CONVERSION': '01_marketing',
    
    # Video announcements
    'ANUNCIO_VIDEO': '01_marketing',
    'webinar-preroll': '01_marketing',
    'webinar-square': '01_marketing',
    'webinar-vertical': '01_marketing',
    
    # Analysis files
    'analisis_deal_estancado': '09_sales',
    'analisis_competitivo': '06_strategy',
    'analisis_competencia': '06_strategy',
    
    # Scripts and automation
    'script_': '04_operations',
    'organize_': '04_operations',
    'cleanup_': '04_operations',
    'maintenance_': '04_operations',
    'AUTO_DMS': '04_operations',
    'AUTOMATION_PLAYBOOK': '04_operations',
    'automatizacion_': '04_operations',
    
    # Prompts and personalization
    '21_prompts_personalizacion': '08_ai_artificial_intelligence',
    'PROMPTS_PERSONALIZACION': '08_ai_artificial_intelligence',
    'prompts_': '08_ai_artificial_intelligence',
    
    # Brand and tone
    '28_BRAND_TONE': '04_business_strategy',
    'BRAND_TONE': '04_business_strategy',
    'emoji_strategy': '01_marketing',
    
    # CRM integrations
    '20_crm_integrations': '09_sales',
    'CRM_': '09_sales',
    'INTEGRACION_LINKEDIN': '09_sales',
    
    # Cases and use cases
    '05_casos_uso': '06_documentation',
    'CASOS_USO': '06_documentation',
    'CASOS_EXITO': '06_documentation',
    'casos_estudio': '06_documentation',
    
    # Checklists
    '07_checklists': '06_documentation/Checklists',
    'checklist_': '06_documentation/Checklists',
    'CHECKLIST_': '06_documentation/Checklists',
    
    # Resumen ejecutivo
    '09_resumen_ejecutivo': '06_documentation',
    'resumen_ejecutivo': '06_documentation',
    'RESUMEN_EJECUTIVO': '06_documentation',
    
    # Guides
    'ad_copy_guide': '01_marketing',
    'advanced_ab_testing': '16_data_analytics',
    'guia_': '06_documentation',
    'GUIA_': '06_documentation',
    
    # Anti-spam
    'AntiSpam_': '04_operations',
    
    # Accessibility
    'Accesibilidad_': '06_documentation',
    
    # Alerts
    'Alerts_': '06_documentation',
    
    # Team roles
    'TEAM_ROLES': '06_documentation',
    
    # Lead magnets
    'LEAD_MAGNET': '01_marketing/05_lead_generation',
    'ESQUEMA_LEAD_MAGNET': '01_marketing/05_lead_generation',
    
    # Sequences (already in Sequences folder)
    '01_secuencia_': '01_marketing/Sequences',
    '02_secuencia_': '01_marketing/Sequences',
    '03_secuencia_': '01_marketing/Sequences',
    
    # Other specific patterns
    'onepager-': '06_documentation',
    'curso-ia-': '01_webinar_campaign',
    'saas-ia-': '01_marketing',
    'ia-bulk-': '01_marketing',
    'runbook-': '06_documentation',
    'quickstart': '06_documentation',
    'QuickStart': '06_documentation',
    'start_here': '06_documentation',
    'README': '06_documentation',
    'readme': '06_documentation',
    'contributing': '06_documentation',
    'changelog': '06_documentation',
    'CHANGELOG': '06_documentation',
    'license': '06_documentation',
    'attributions': '06_documentation',
    'INDEX': '06_documentation',
    'indice_': '06_documentation',
}

def find_destination_folder(filename):
    """Encuentra la carpeta destino para un archivo basado en su nombre"""
    filename_upper = filename.upper()
    
    # Buscar coincidencias en orden de especificidad (más específico primero)
    for pattern, folder in sorted(FILE_MAPPINGS.items(), key=lambda x: -len(x[0])):
        if pattern.upper() in filename_upper:
            return folder
    
    # Si no hay coincidencia específica, usar reglas generales
    filename_lower = filename.lower()
    
    if filename.startswith('00_EMAIL_SEGUIMIENTO'):
        return '01_marketing/Sequences'
    elif filename.startswith('00_EMAIL'):
        return '01_marketing/Sequences'
    elif filename.startswith('01_') or filename.startswith('02_') or filename.startswith('03_'):
        if 'webinar' in filename_lower or 'curso_ia' in filename_lower:
            return '01_webinar_campaign'
        else:
            return '01_marketing'
    elif filename.startswith('00_') and 'IA' in filename:
        return '08_ai_artificial_intelligence'
    elif 'sales' in filename_lower or 'ventas' in filename_lower or 'closing' in filename_lower:
        return '09_sales'
    elif 'documentation' in filename_lower or 'documentacion' in filename_lower or 'guia' in filename_lower or 'guide' in filename_lower:
        return '06_documentation'
    elif 'analytics' in filename_lower or 'dashboard' in filename_lower or 'metricas' in filename_lower or 'kpi' in filename_lower:
        return '16_data_analytics'
    elif 'compliance' in filename_lower or 'legal' in filename_lower or 'privacy' in filename_lower:
        return '13_legal_compliance'
    elif 'template' in filename_lower or 'plantilla' in filename_lower:
        return '06_documentation/Templates'
    elif 'checklist' in filename_lower:
        return '06_documentation/Checklists'
    elif 'script' in filename_lower and (filename.endswith('.py') or filename.endswith('.js') or filename.endswith('.sh')):
        return '04_operations'
    elif filename.endswith('.svg') or filename.endswith('.zip'):
        return '06_documentation/Data_Files'
    elif filename.endswith('.csv') or filename.endswith('.json') or filename.endswith('.yaml') or filename.endswith('.env'):
        return '06_documentation/Data_Files'
    elif filename.endswith('.py') or filename.endswith('.js') or filename.endswith('.gs'):
        return '04_operations'
    elif filename.endswith('.html') or filename.endswith('.md'):
        # Try to infer from content keywords
        if 'marketing' in filename_lower or 'campaign' in filename_lower or 'outreach' in filename_lower:
            return '01_marketing'
        elif 'sales' in filename_lower or 'ventas' in filename_lower:
            return '09_sales'
        elif 'strategy' in filename_lower or 'estrategia' in filename_lower:
            return '06_strategy'
        elif 'ai' in filename_lower or 'ia' in filename_lower:
            return '08_ai_artificial_intelligence'
        else:
            return '06_documentation'
    
    return None

def organize_files():
    """Organiza los archivos del directorio raíz"""
    import json
    from datetime import datetime
    
    moved_files = []
    skipped_files = []
    errors = []
    already_exists = []
    
    # Obtener todos los archivos en el directorio raíz
    root_files = [f for f in BASE_DIR.iterdir() if f.is_file()]
    
    print(f"Encontrados {len(root_files)} archivos en el directorio raíz\n")
    
    for file_path in root_files:
        filename = file_path.name
        
        # Saltar archivos del sistema y este script
        if filename.startswith('.') or filename == 'organize_root_files.py':
            continue
        
        # Encontrar carpeta destino
        dest_folder = find_destination_folder(filename)
        
        if dest_folder is None:
            skipped_files.append(filename)
            print(f"⚠️  Saltado (sin destino claro): {filename}")
            continue
        
        # Crear ruta completa
        dest_path = BASE_DIR / dest_folder
        dest_file = dest_path / filename
        
        # Crear carpeta si no existe
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Verificar si el archivo ya existe en destino
        if dest_file.exists():
            already_exists.append((filename, dest_folder))
            print(f"⚠️  Ya existe en destino: {filename} -> {dest_folder}")
            continue
        
        try:
            # Mover archivo
            shutil.move(str(file_path), str(dest_file))
            moved_files.append((filename, dest_folder))
            print(f"✓ Movido: {filename} -> {dest_folder}")
        except Exception as e:
            errors.append((filename, str(e)))
            print(f"✗ Error moviendo {filename}: {e}")
    
    # Resumen mejorado
    print("\n" + "="*80)
    print("RESUMEN DE ORGANIZACIÓN")
    print("="*80)
    print(f"✓ Archivos movidos exitosamente: {len(moved_files)}")
    print(f"⚠️  Archivos saltados (sin destino): {len(skipped_files)}")
    print(f"⚠️  Archivos que ya existían en destino: {len(already_exists)}")
    print(f"✗ Errores: {len(errors)}")
    
    # Estadísticas por carpeta
    folder_stats = {}
    for filename, folder in moved_files:
        folder_stats[folder] = folder_stats.get(folder, 0) + 1
    
    if folder_stats:
        print("\n📊 Archivos movidos por carpeta:")
        for folder, count in sorted(folder_stats.items(), key=lambda x: -x[1]):
            print(f"  {folder}: {count} archivos")
    
    if skipped_files:
        print(f"\n⚠️  Archivos saltados ({len(skipped_files)}):")
        for f in skipped_files[:20]:
            print(f"  - {f}")
        if len(skipped_files) > 20:
            print(f"  ... y {len(skipped_files) - 20} más")
    
    if already_exists:
        print(f"\n⚠️  Archivos que ya existían ({len(already_exists)}):")
        for f, folder in already_exists[:10]:
            print(f"  - {f} -> {folder}")
        if len(already_exists) > 10:
            print(f"  ... y {len(already_exists) - 10} más")
    
    if errors:
        print("\n✗ Errores:")
        for f, e in errors:
            print(f"  - {f}: {e}")
    
    # Guardar reporte JSON
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_files_found': len(root_files),
        'moved': len(moved_files),
        'skipped': len(skipped_files),
        'already_exists': len(already_exists),
        'errors': len(errors),
        'moved_files': moved_files,
        'folder_stats': folder_stats,
        'skipped_files': skipped_files[:50],  # Limitar a 50
        'errors_list': errors
    }
    
    report_path = BASE_DIR / '06_documentation' / 'organizacion_raiz_report.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Reporte guardado en: {report_path}")
    
    return report

if __name__ == '__main__':
    organize_files()

