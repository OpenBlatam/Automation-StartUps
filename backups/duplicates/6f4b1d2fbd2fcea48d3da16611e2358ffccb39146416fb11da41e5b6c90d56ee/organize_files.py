#!/usr/bin/env python3
"""
Script to organize files by business area based on filename patterns
"""

import os
import shutil
import re

# Define business area mappings
BUSINESS_AREAS = {
    '01_Marketing': [
        'marketing', 'marketing', 'advertising', 'brand', 'campaign', 'content', 'social', 'seo', 'sem', 'ppc',
        'email', 'digital', 'growth', 'conversion', 'analytics', 'anchor', 'ab_test', 'analisis', 'sentimientos',
        'tendencias', 'competencia', 'casos_uso', 'personalizados', 'multilenguaje', 'neuro_marketing', 'viral',
        'omnichannel', 'customer_experience', 'customer_success', 'lifetime_value', 'personalization'
    ],
    '02_Finance': [
        'financial', 'finance', 'budget', 'revenue', 'profit', 'cost', 'investment', 'roi', 'wealth', 'money',
        'accounting', 'tax', 'audit', 'treasury', 'capital', 'funding', 'valuation', 'pricing', 'billing'
    ],
    '03_Human_Resources': [
        'hr', 'human', 'talent', 'recruitment', 'hiring', 'employee', 'staff', 'workforce', 'training', 'development',
        'performance', 'compensation', 'benefits', 'culture', 'leadership', 'team', 'skills', 'career', 'onboarding'
    ],
    '04_Operations': [
        'operations', 'operational', 'process', 'workflow', 'efficiency', 'productivity', 'optimization', 'supply',
        'logistics', 'procurement', 'vendor', 'quality', 'compliance', 'safety', 'maintenance', 'facilities'
    ],
    '05_Technology': [
        'technology', 'tech', 'digital', 'software', 'hardware', 'it', 'infrastructure', 'system', 'platform',
        'development', 'programming', 'coding', 'database', 'security', 'cyber', 'cloud', 'api', 'integration'
    ],
    '06_Strategy': [
        'strategy', 'strategic', 'planning', 'business', 'management', 'leadership', 'decision', 'innovation',
        'transformation', 'change', 'crisis', 'communication', 'negotiation', 'public_speaking', 'problem_solving',
        'time_management', 'productivity', 'agile', 'project', 'implementation', 'improvement', 'international',
        'expansion', 'partnerships', 'sustainability'
    ],
    '07_Risk_Management': [
        'risk', 'security', 'compliance', 'audit', 'governance', 'policy', 'assessment', 'monitoring', 'response',
        'crisis', 'emergency', 'disaster', 'insurance', 'legal', 'regulatory', 'fraud', 'threat', 'vulnerability'
    ],
    '08_AI_Artificial_Intelligence': [
        'ai', 'artificial', 'intelligence', 'machine_learning', 'ml', 'deep_learning', 'neural', 'algorithm',
        'automation', 'robotics', 'chatbot', 'nlp', 'computer_vision', 'predictive', 'analytics', 'data_science',
        'blockchain', 'cryptocurrency', 'defi', 'nft', 'quantum', 'consciousness', 'transcendent', 'infinite'
    ],
    '09_Sales': [
        'sales', 'selling', 'revenue', 'conversion', 'leads', 'prospects', 'pipeline', 'crm', 'customer',
        'client', 'deal', 'negotiation', 'closing', 'upselling', 'cross_selling', 'retention', 'acquisition'
    ],
    '10_Customer_Service': [
        'customer_service', 'support', 'service', 'help', 'ticket', 'resolution', 'satisfaction', 'feedback',
        'complaint', 'escalation', 'knowledge_base', 'faq', 'chat', 'phone', 'email_support'
    ],
    '11_Research_Development': [
        'research', 'development', 'rd', 'innovation', 'patent', 'intellectual', 'property', 'prototype',
        'testing', 'experiment', 'discovery', 'invention', 'scientific', 'academic', 'study', 'analysis'
    ],
    '12_Quality_Assurance': [
        'quality', 'assurance', 'qa', 'testing', 'validation', 'verification', 'standards', 'certification',
        'iso', 'compliance', 'audit', 'inspection', 'defect', 'bug', 'performance', 'reliability'
    ],
    '13_Legal_Compliance': [
        'legal', 'compliance', 'law', 'regulation', 'policy', 'contract', 'agreement', 'terms', 'privacy',
        'gdpr', 'intellectual_property', 'patent', 'trademark', 'copyright', 'litigation', 'dispute'
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
        'business_intelligence', 'visualization', 'chart', 'graph', 'insight', 'trend', 'forecast', 'prediction'
    ],
    '17_Innovation': [
        'innovation', 'creativity', 'invention', 'disruption', 'breakthrough', 'cutting_edge', 'pioneer',
        'revolutionary', 'transformative', 'next_generation', 'future', 'emerging', 'trending'
    ],
    '18_Sustainability': [
        'sustainability', 'environmental', 'green', 'eco', 'carbon', 'renewable', 'energy', 'waste', 'recycling',
        'conservation', 'climate', 'sustainable', 'esg', 'csr', 'social_responsibility'
    ],
    '19_International_Business': [
        'international', 'global', 'multinational', 'cross_cultural', 'localization', 'translation', 'export',
        'import', 'trade', 'foreign', 'overseas', 'regional', 'worldwide', 'geographic'
    ],
    '20_Project_Management': [
        'project', 'management', 'pm', 'pmp', 'agile', 'scrum', 'kanban', 'waterfall', 'milestone', 'deliverable',
        'timeline', 'schedule', 'resource', 'stakeholder', 'scope', 'budget', 'risk', 'quality', 'communication'
    ]
}

def categorize_file(filename):
    """Categorize a file based on its name"""
    filename_lower = filename.lower()
    
    for area, keywords in BUSINESS_AREAS.items():
        for keyword in keywords:
            if keyword.lower() in filename_lower:
                return area
    
    return None

def organize_files():
    """Organize files into appropriate business area folders"""
    current_dir = os.getcwd()
    
    # Get all markdown files
    files = [f for f in os.listdir(current_dir) if f.endswith('.md') and os.path.isfile(f)]
    
    print(f"Found {len(files)} markdown files to organize")
    
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
    organize_files()




