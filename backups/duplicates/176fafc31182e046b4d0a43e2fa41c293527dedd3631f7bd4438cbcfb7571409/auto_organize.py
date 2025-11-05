#!/usr/bin/env python3
"""
Sistema de automatización para organización de nuevos archivos
"""

import os
import shutil
import time
from datetime import datetime
import json
import re

class AutoOrganizer:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.watch_path = base_path
        self.log_file = os.path.join(base_path, "organization_log.json")
        self.business_areas = {
            '01_Marketing': [
                'marketing', 'marketing', 'advertising', 'brand', 'campaign', 'content', 'social', 'seo', 'sem', 'ppc',
                'email', 'digital', 'growth', 'conversion', 'analytics', 'anchor', 'ab_test', 'analisis', 'sentimientos',
                'tendencias', 'competencia', 'casos_uso', 'personalizados', 'multilenguaje', 'neuro_marketing', 'viral',
                'omnichannel', 'customer_experience', 'customer_success', 'lifetime_value', 'personalization',
                'webinar', 'copy', 'copywriting', 'storytelling', 'engagement', 'traffic', 'leads', 'funnel'
            ],
            '02_Finance': [
                'financial', 'finance', 'budget', 'revenue', 'profit', 'cost', 'investment', 'roi', 'wealth', 'money',
                'accounting', 'tax', 'audit', 'treasury', 'capital', 'funding', 'valuation', 'pricing', 'billing',
                'presupuesto', 'costos', 'modelo', 'financiero', 'startup', 'cashflow', 'ebitda', 'margins'
            ],
            '03_Human_Resources': [
                'hr', 'human', 'talent', 'recruitment', 'hiring', 'employee', 'staff', 'workforce', 'training', 'development',
                'performance', 'compensation', 'benefits', 'culture', 'leadership', 'team', 'skills', 'career', 'onboarding',
                'capacitacion', 'vendedores', 'satisfaction', 'survey', 'guia', 'deteccion', 'talento', 'people', 'personnel'
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
                'implementacion', 'rapida', 'guia', 'por', 'roles', 'responsabilidades', 'metricas', 'kpis', 'ia',
                'devops', 'deployment', 'monitoring', 'logging', 'scalability', 'performance'
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
                'crisis', 'emergency', 'disaster', 'insurance', 'legal', 'regulatory', 'fraud', 'threat', 'vulnerability',
                'seguridad', 'cumplimiento', 'auditoria', 'politica', 'evaluacion', 'monitoreo', 'respuesta'
            ],
            '08_AI_Artificial_Intelligence': [
                'ai', 'artificial', 'intelligence', 'machine_learning', 'ml', 'deep_learning', 'neural', 'algorithm',
                'automation', 'robotics', 'chatbot', 'nlp', 'computer_vision', 'predictive', 'analytics', 'data_science',
                'blockchain', 'cryptocurrency', 'defi', 'nft', 'quantum', 'consciousness', 'transcendent', 'infinite',
                'consciente', 'artificial', 'suprema', 'ultra', 'avanzada', 'implementacion', 'practica', 'consciencia',
                'machine', 'learning', 'neural', 'network', 'automation', 'intelligent', 'smart', 'cognitive'
            ],
            '09_Sales': [
                'sales', 'selling', 'revenue', 'conversion', 'leads', 'prospects', 'pipeline', 'crm', 'customer',
                'client', 'deal', 'negotiation', 'closing', 'upselling', 'cross_selling', 'retention', 'acquisition',
                'vendedores', 'avanzado', 'capacitacion', 'sistema', 'integracion', 'crm', 'avanzado', 'reporte', 'final',
                'pipeline', 'mejoras', 'universales', 'omniversales', 'infinitas', 'selling', 'revenue', 'conversion'
            ],
            '10_Customer_Service': [
                'customer_service', 'support', 'service', 'help', 'ticket', 'resolution', 'satisfaction', 'feedback',
                'complaint', 'escalation', 'knowledge_base', 'faq', 'chat', 'phone', 'email_support', 'sistema',
                'neurofeedback', 'aprendizaje', 'customer', 'support', 'service', 'help', 'ticket', 'resolution'
            ],
            '11_Research_Development': [
                'research', 'development', 'rd', 'innovation', 'patent', 'intellectual', 'property', 'prototype',
                'testing', 'experiment', 'discovery', 'invention', 'scientific', 'academic', 'study', 'analysis',
                'laboratorio', 'innovacion', 'rd', 'testing', 'qa', 'guia', 'research', 'development', 'innovation'
            ],
            '12_Quality_Assurance': [
                'quality', 'assurance', 'qa', 'testing', 'validation', 'verification', 'standards', 'certification',
                'iso', 'compliance', 'audit', 'inspection', 'defect', 'bug', 'performance', 'reliability', 'consultant',
                'advisor', 'guia', 'certificacion', 'framework', 'avanzado', 'quality', 'assurance', 'testing'
            ],
            '13_Legal_Compliance': [
                'legal', 'compliance', 'law', 'regulation', 'policy', 'contract', 'agreement', 'terms', 'privacy',
                'gdpr', 'intellectual_property', 'patent', 'trademark', 'copyright', 'litigation', 'dispute',
                'influencer', 'contract', 'templates', 'legal', 'compliance', 'law', 'regulation', 'policy'
            ],
            '14_Procurement': [
                'procurement', 'purchasing', 'vendor', 'supplier', 'contract', 'sourcing', 'negotiation', 'rfp',
                'rfq', 'tender', 'bid', 'acquisition', 'supply_chain', 'logistics', 'inventory', 'procurement',
                'purchasing', 'vendor', 'supplier', 'contract', 'sourcing'
            ],
            '15_Logistics': [
                'logistics', 'shipping', 'transportation', 'warehouse', 'inventory', 'distribution', 'supply_chain',
                'delivery', 'fulfillment', 'freight', 'cargo', 'storage', 'packaging', 'tracking', 'logistics',
                'shipping', 'transportation', 'warehouse', 'inventory', 'distribution'
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
                'innovacion', 'integral', 'future', 'ready', 'index', 'innovation', 'creativity', 'invention'
            ],
            '18_Sustainability': [
                'sustainability', 'environmental', 'green', 'eco', 'carbon', 'renewable', 'energy', 'waste', 'recycling',
                'conservation', 'climate', 'sustainable', 'esg', 'csr', 'social_responsibility', 'guia', 'contenido',
                'evergreen', 'ia', 'ecosistema', 'innovacion', 'integral', 'sustainability', 'environmental', 'green'
            ],
            '19_International_Business': [
                'international', 'global', 'multinational', 'cross_cultural', 'localization', 'translation', 'export',
                'import', 'trade', 'foreign', 'overseas', 'regional', 'worldwide', 'geographic', 'red', 'global', 'alumni',
                'seguimiento', 'impacto', 'global', 'international', 'global', 'multinational', 'cross_cultural'
            ],
            '20_Project_Management': [
                'project', 'management', 'pm', 'pmp', 'agile', 'scrum', 'kanban', 'waterfall', 'milestone', 'deliverable',
                'timeline', 'schedule', 'resource', 'stakeholder', 'scope', 'budget', 'risk', 'quality', 'communication',
                'project', 'management', 'pm', 'pmp', 'agile', 'scrum', 'kanban'
            ]
        }
    
    def categorize_file(self, filename):
        """Categorizar archivo basado en su nombre"""
        filename_lower = filename.lower()
        
        for area, keywords in self.business_areas.items():
            for keyword in keywords:
                if keyword.lower() in filename_lower:
                    return area
        
        return None
    
    def log_organization(self, filename, source_path, target_path, success=True, error_msg=None):
        """Registrar actividad de organización"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'filename': filename,
            'source_path': source_path,
            'target_path': target_path,
            'success': success,
            'error': error_msg
        }
        
        # Cargar log existente
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        # Guardar log actualizado
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def organize_new_files(self):
        """Organizar archivos nuevos en el directorio raíz"""
        organized_count = 0
        errors = []
        
        # Buscar archivos .md en el directorio raíz
        for filename in os.listdir(self.watch_path):
            if filename.endswith('.md') and os.path.isfile(os.path.join(self.watch_path, filename)):
                source_path = os.path.join(self.watch_path, filename)
                target_area = self.categorize_file(filename)
                
                if target_area:
                    target_path = os.path.join(self.base_path, target_area, filename)
                    
                    try:
                        shutil.move(source_path, target_path)
                        self.log_organization(filename, source_path, target_path, success=True)
                        print(f"✅ Organizado: {filename} → {target_area}")
                        organized_count += 1
                    except Exception as e:
                        error_msg = str(e)
                        self.log_organization(filename, source_path, target_path, success=False, error_msg=error_msg)
                        errors.append(f"❌ Error organizando {filename}: {error_msg}")
                else:
                    print(f"⚠️  No categorizado: {filename}")
        
        return organized_count, errors
    
    def get_organization_stats(self):
        """Obtener estadísticas de organización"""
        stats = {}
        total_files = 0
        
        for area_code, area_name in self.business_areas.items():
            area_path = os.path.join(self.base_path, area_code)
            if os.path.exists(area_path):
                file_count = 0
                for root, dirs, files in os.walk(area_path):
                    file_count += len([f for f in files if f.endswith('.md')])
                
                stats[area_name] = {
                    'code': area_code,
                    'files': file_count,
                    'path': area_path
                }
                total_files += file_count
        
        stats['total_files'] = total_files
        return stats
    
    def run_auto_organization(self):
        """Ejecutar organización automática"""
        print("🤖 Iniciando organización automática...")
        print("=" * 50)
        
        # Organizar archivos nuevos
        organized_count, errors = self.organize_new_files()
        
        # Mostrar resultados
        print(f"\n📊 Resultados:")
        print(f"✅ Archivos organizados: {organized_count}")
        print(f"❌ Errores: {len(errors)}")
        
        if errors:
            print("\n🚨 Errores encontrados:")
            for error in errors:
                print(f"  {error}")
        
        # Mostrar estadísticas
        stats = self.get_organization_stats()
        print(f"\n📈 Estadísticas del sistema:")
        print(f"📁 Total de archivos: {stats['total_files']}")
        
        # Mostrar top 5 áreas
        sorted_areas = sorted([(name, data['files']) for name, data in stats.items() if name != 'total_files'], 
                             key=lambda x: x[1], reverse=True)
        
        print(f"\n🏆 Top 5 áreas con más archivos:")
        for i, (area, count) in enumerate(sorted_areas[:5], 1):
            print(f"  {i}. {area}: {count} archivos")
        
        return organized_count, errors

def main():
    organizer = AutoOrganizer()
    
    print("🤖 Sistema de Organización Automática")
    print("=" * 40)
    print("1. Organizar archivos nuevos")
    print("2. Ver estadísticas")
    print("3. Ver log de actividades")
    print("4. Salir")
    
    choice = input("\nSeleccione una opción (1-4): ").strip()
    
    if choice == '1':
        organized_count, errors = organizer.run_auto_organization()
        if organized_count > 0:
            print(f"\n🎉 ¡Organización completada! {organized_count} archivos organizados.")
        else:
            print("\n📋 No se encontraron archivos nuevos para organizar.")
    
    elif choice == '2':
        stats = organizer.get_organization_stats()
        print(f"\n📊 Estadísticas del Sistema:")
        print(f"📁 Total de archivos: {stats['total_files']}")
        print("\n📋 Distribución por área:")
        for area_name, data in sorted(stats.items(), key=lambda x: x[1].get('files', 0), reverse=True):
            if area_name != 'total_files':
                print(f"  📁 {area_name}: {data['files']} archivos")
    
    elif choice == '3':
        if os.path.exists(organizer.log_file):
            with open(organizer.log_file, 'r') as f:
                logs = json.load(f)
            print(f"\n📋 Log de actividades (últimas 10):")
            for log in logs[-10:]:
                status = "✅" if log['success'] else "❌"
                print(f"  {status} {log['timestamp']}: {log['filename']}")
        else:
            print("\n📋 No hay log de actividades disponible.")
    
    elif choice == '4':
        print("👋 ¡Hasta luego!")
    
    else:
        print("❌ Opción no válida.")

if __name__ == "__main__":
    main()



