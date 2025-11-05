#!/usr/bin/env python3
"""
Script to organize remaining files by content analysis
"""

import os
import shutil
import re

# Extended business area mappings for remaining files
BUSINESS_AREAS = {
    '01_Marketing': [
        'resumen', 'ejecutivo', 'curso', 'premium', 'webinar', 'content', 'copy', 'copywriting', 'social', 'media',
        'seo', 'sem', 'ppc', 'email', 'digital', 'growth', 'conversion', 'analytics', 'anchor', 'ab_test', 'analisis',
        'sentimientos', 'tendencias', 'competencia', 'casos_uso', 'personalizados', 'multilenguaje', 'neuro_marketing',
        'viral', 'omnichannel', 'customer_experience', 'customer_success', 'lifetime_value', 'personalization',
        'marketing', 'advertising', 'brand', 'campaign', 'content', 'social', 'seo', 'sem', 'ppc', 'email', 'digital',
        'growth', 'conversion', 'analytics', 'anchor', 'ab_test', 'analisis', 'sentimientos', 'tendencias',
        'competencia', 'casos_uso', 'personalizados', 'multilenguaje', 'neuro_marketing', 'viral', 'omnichannel',
        'customer_experience', 'customer_success', 'lifetime_value', 'personalization', 'frases', 'populares',
        'busqueda', 'google', 'mejoras', 'finales', 'ultra', 'revolucionario', 'transformador', 'evolutivo',
        'consciente', 'iluminado', 'divino', 'trascendental', 'prediccion', 'trayectorias', 'profesionales',
        'singularidad', 'implementacion', 'tipo', 'organizacion', 'ejecutivo', 'curso', 'premium'
    ],
    '02_Finance': [
        'financial', 'finance', 'budget', 'revenue', 'profit', 'cost', 'investment', 'roi', 'wealth', 'money',
        'accounting', 'tax', 'audit', 'treasury', 'capital', 'funding', 'valuation', 'pricing', 'billing',
        'presupuesto', 'costos', 'realistas', 'modelo', 'financiero', 'startup', 'definitivo'
    ],
    '03_Human_Resources': [
        'hr', 'human', 'talent', 'recruitment', 'hiring', 'employee', 'staff', 'workforce', 'training', 'development',
        'performance', 'compensation', 'benefits', 'culture', 'leadership', 'team', 'skills', 'career', 'onboarding',
        'capacitacion', 'vendedores', 'avanzado', 'satisfaction', 'survey', 'guia', 'deteccion', 'talento'
    ],
    '04_Operations': [
        'operations', 'operational', 'process', 'workflow', 'efficiency', 'productivity', 'optimization', 'supply',
        'logistics', 'procurement', 'vendor', 'quality', 'compliance', 'safety', 'maintenance', 'facilities',
        'cvr', 'optimization', 'estrategias', 'security', 'compliance', 'guia', 'manual', 'regulaciones', 'fintech'
    ],
    '05_Technology': [
        'technology', 'tech', 'digital', 'software', 'hardware', 'it', 'infrastructure', 'system', 'platform',
        'development', 'programming', 'coding', 'database', 'security', 'cyber', 'cloud', 'api', 'integration',
        'sistema', 'ia', 'consciente', 'integracion', 'crm', 'avanzado', 'automatizacion', 'sistemas', 'checklist',
        'implementacion', 'rapida', 'guia', 'por', 'roles', 'responsabilidades', 'metricas', 'kpis', 'ia'
    ],
    '06_Strategy': [
        'strategy', 'strategic', 'planning', 'business', 'management', 'leadership', 'decision', 'innovation',
        'transformation', 'change', 'crisis', 'communication', 'negotiation', 'public_speaking', 'problem_solving',
        'time_management', 'productivity', 'agile', 'project', 'implementation', 'improvement', 'international',
        'expansion', 'partnerships', 'sustainability', 'resumen', 'mejoras', 'singularidad', 'implementacion',
        'tipo', 'organizacion', 'ejecutivo', 'curso', 'premium', 'guia', 'escalabilidad', 'crecimiento'
    ],
    '07_Risk_Management': [
        'risk', 'security', 'compliance', 'audit', 'governance', 'policy', 'assessment', 'monitoring', 'response',
        'crisis', 'emergency', 'disaster', 'insurance', 'legal', 'regulatory', 'fraud', 'threat', 'vulnerability'
    ],
    '08_AI_Artificial_Intelligence': [
        'ai', 'artificial', 'intelligence', 'machine_learning', 'ml', 'deep_learning', 'neural', 'algorithm',
        'automation', 'robotics', 'chatbot', 'nlp', 'computer_vision', 'predictive', 'analytics', 'data_science',
        'blockchain', 'cryptocurrency', 'defi', 'nft', 'quantum', 'consciousness', 'transcendent', 'infinite',
        'consciente', 'artificial', 'suprema', 'ultra', 'avanzada', 'implementacion', 'practica', 'consciencia'
    ],
    '09_Sales': [
        'sales', 'selling', 'revenue', 'conversion', 'leads', 'prospects', 'pipeline', 'crm', 'customer',
        'client', 'deal', 'negotiation', 'closing', 'upselling', 'cross_selling', 'retention', 'acquisition',
        'vendedores', 'avanzado', 'capacitacion', 'sistema', 'integracion', 'crm', 'avanzado', 'reporte', 'final',
        'pipeline', 'mejoras', 'universales', 'omniversales', 'infinitas'
    ],
    '10_Customer_Service': [
        'customer_service', 'support', 'service', 'help', 'ticket', 'resolution', 'satisfaction', 'feedback',
        'complaint', 'escalation', 'knowledge_base', 'faq', 'chat', 'phone', 'email_support', 'sistema',
        'neurofeedback', 'aprendizaje'
    ],
    '11_Research_Development': [
        'research', 'development', 'rd', 'innovation', 'patent', 'intellectual', 'property', 'prototype',
        'testing', 'experiment', 'discovery', 'invention', 'scientific', 'academic', 'study', 'analysis',
        'laboratorio', 'innovacion', 'rd', 'testing', 'qa', 'guia'
    ],
    '12_Quality_Assurance': [
        'quality', 'assurance', 'qa', 'testing', 'validation', 'verification', 'standards', 'certification',
        'iso', 'compliance', 'audit', 'inspection', 'defect', 'bug', 'performance', 'reliability', 'consultant',
        'advisor', 'guia', 'certificacion', 'framework', 'avanzado'
    ],
    '13_Legal_Compliance': [
        'legal', 'compliance', 'law', 'regulation', 'policy', 'contract', 'agreement', 'terms', 'privacy',
        'gdpr', 'intellectual_property', 'patent', 'trademark', 'copyright', 'litigation', 'dispute',
        'influencer', 'contract', 'templates'
    ],
    '14_Procurement': [
        'procurement', 'purchasing', 'vendor', 'supplier', 'contract', 'sourcing', 'negotiation', 'rfp',
        'rfq', 'tender', 'bid', 'acquisition', 'supply_chain', 'logistics', 'inventory'
    ],
    '15_Logistics': [
        'logistics', 'shipping', 'transportation', 'warehouse', 'inventory', 'distribution', 'supply_chain',
        'delivery', 'fulfillment', 'freight', 'cargo', 'storage', 'packaging', 'tracking'
    ],
    '16_Data_Analytics': [
        'data', 'analytics', 'analysis', 'reporting', 'dashboard', 'kpi', 'metrics', 'statistics', 'bi',
        'business_intelligence', 'visualization', 'chart', 'graph', 'insight', 'trend', 'forecast', 'prediction',
        'metricas', 'kpis', 'ia', 'guia', 'por', 'roles', 'responsabilidades', 'ia', 'avanzadas', 'kpis',
        'analytics', 'data', 'science', 'insights', 'engine', 'avanzado', 'consumidor', 'metricas', 'avanzadas',
        'kpis', 'guia', 'escalabilidad', 'crecimiento', 'seguimiento', 'impacto', 'global', 'dashboard', 'impacto',
        'global', 'tiempo', 'real', 'metricas', 'avanzadas', 'kpis', 'guia', 'contenido', 'evergreen', 'ia'
    ],
    '17_Innovation': [
        'innovation', 'creativity', 'invention', 'disruption', 'breakthrough', 'cutting_edge', 'pioneer',
        'revolutionary', 'transformative', 'next_generation', 'future', 'emerging', 'trending', 'ecosistema',
        'innovacion', 'integral', 'future', 'ready', 'index'
    ],
    '18_Sustainability': [
        'sustainability', 'environmental', 'green', 'eco', 'carbon', 'renewable', 'energy', 'waste', 'recycling',
        'conservation', 'climate', 'sustainable', 'esg', 'csr', 'social_responsibility', 'guia', 'contenido',
        'evergreen', 'ia', 'ecosistema', 'innovacion', 'integral'
    ],
    '19_International_Business': [
        'international', 'global', 'multinational', 'cross_cultural', 'localization', 'translation', 'export',
        'import', 'trade', 'foreign', 'overseas', 'regional', 'worldwide', 'geographic', 'red', 'global', 'alumni',
        'seguimiento', 'impacto', 'global'
    ],
    '20_Project_Management': [
        'project', 'management', 'pm', 'pmp', 'agile', 'scrum', 'kanban', 'waterfall', 'milestone', 'deliverable',
        'timeline', 'schedule', 'resource', 'stakeholder', 'scope', 'budget', 'risk', 'quality', 'communication'
    ]
}

def categorize_file(filename):
    """Categorize a file based on its name with extended patterns"""
    filename_lower = filename.lower()
    
    for area, keywords in BUSINESS_AREAS.items():
        for keyword in keywords:
            if keyword.lower() in filename_lower:
                return area
    
    return None

def organize_remaining_files():
    """Organize remaining files into appropriate business area folders"""
    current_dir = os.getcwd()
    
    # Get all remaining markdown files
    files = [f for f in os.listdir(current_dir) if f.endswith('.md') and os.path.isfile(f)]
    
    print(f"Found {len(files)} remaining markdown files to organize")
    
    organized_count = 0
    unorganized_files = []
    
    for filename in files:
        target_area = categorize_file(filename)
        
        if target_area:
            source_path = os.path.join(current_dir, filename)
            target_path = os.path.join(current_dir, target_area, filename)
            
            try:
                shutil.move(source_path, target_path)
                print(f"Moved {filename} to {target_area}")
                organized_count += 1
            except Exception as e:
                print(f"Error moving {filename}: {e}")
        else:
            unorganized_files.append(filename)
    
    print(f"\nOrganized {organized_count} files")
    print(f"Unorganized files ({len(unorganized_files)}):")
    for file in unorganized_files[:10]:  # Show first 10
        print(f"  - {file}")
    if len(unorganized_files) > 10:
        print(f"  ... and {len(unorganized_files) - 10} more")

if __name__ == "__main__":
    organize_remaining_files()




