#!/usr/bin/env python3
"""
Advanced File Organization Script
Organizes files into appropriate business area folders with subcategories
"""

import os
import shutil
import re
from pathlib import Path
from datetime import datetime

class AdvancedFileOrganizer:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.organization_log = []
        
        # Define file patterns and their target folders
        self.file_patterns = {
            # Marketing related files
            'marketing': {
                'patterns': [
                    r'.*marketing.*', r'.*anchor.*text.*', r'.*seo.*', r'.*sem.*',
                    r'.*social.*media.*', r'.*content.*marketing.*', r'.*digital.*marketing.*',
                    r'.*email.*marketing.*', r'.*campaign.*', r'.*lead.*generation.*',
                    r'.*analytics.*', r'.*automation.*', r'.*ai.*marketing.*'
                ],
                'main_folder': '01_Marketing',
                'subcategories': {
                    'anchor_texts': ['anchor.*text', 'anchor.*texts'],
                    'seo_sem': ['seo', 'sem', 'search.*engine'],
                    'social_media': ['social.*media', 'facebook', 'instagram', 'twitter', 'linkedin'],
                    'content_marketing': ['content.*marketing', 'blog', 'article'],
                    'email_marketing': ['email.*marketing', 'newsletter', 'mailchimp'],
                    'analytics': ['analytics', 'metrics', 'dashboard', 'report'],
                    'automation': ['automation', 'automated', 'workflow'],
                    'ai_marketing': ['ai.*marketing', 'artificial.*intelligence.*marketing']
                }
            },
            
            # Technology related files
            'technology': {
                'patterns': [
                    r'.*technology.*', r'.*tech.*', r'.*software.*', r'.*development.*',
                    r'.*programming.*', r'.*code.*', r'.*api.*', r'.*database.*',
                    r'.*cloud.*', r'.*ai.*', r'.*machine.*learning.*', r'.*data.*science.*',
                    r'.*blockchain.*', r'.*quantum.*', r'.*iot.*', r'.*edge.*computing.*',
                    r'.*devops.*', r'.*cybersecurity.*'
                ],
                'main_folder': '05_Technology',
                'subcategories': {
                    'ai_ml': ['ai', 'artificial.*intelligence', 'machine.*learning', 'neural.*network'],
                    'cloud_computing': ['cloud', 'aws', 'azure', 'google.*cloud'],
                    'data_science': ['data.*science', 'data.*analysis', 'big.*data'],
                    'software_development': ['software.*development', 'programming', 'code', 'api'],
                    'cybersecurity': ['cybersecurity', 'security', 'cyber.*security'],
                    'devops': ['devops', 'deployment', 'ci.*cd'],
                    'blockchain': ['blockchain', 'cryptocurrency', 'crypto'],
                    'quantum_computing': ['quantum', 'quantum.*computing'],
                    'iot': ['iot', 'internet.*of.*things', 'sensors'],
                    'edge_computing': ['edge.*computing', 'edge.*computing']
                }
            },
            
            # Finance related files
            'finance': {
                'patterns': [
                    r'.*finance.*', r'.*financial.*', r'.*investment.*', r'.*budget.*',
                    r'.*accounting.*', r'.*fintech.*', r'.*cryptocurrency.*', r'.*crypto.*',
                    r'.*risk.*management.*', r'.*compliance.*', r'.*audit.*', r'.*reporting.*'
                ],
                'main_folder': '02_Finance',
                'subcategories': {
                    'financial_planning': ['financial.*planning', 'budget', 'planning'],
                    'investment_analysis': ['investment', 'portfolio', 'trading'],
                    'risk_management': ['risk.*management', 'risk', 'compliance'],
                    'accounting': ['accounting', 'bookkeeping', 'financial.*statements'],
                    'fintech': ['fintech', 'financial.*technology'],
                    'cryptocurrency': ['cryptocurrency', 'crypto', 'bitcoin', 'ethereum'],
                    'financial_modeling': ['financial.*modeling', 'model', 'forecast'],
                    'compliance': ['compliance', 'regulatory', 'audit'],
                    'reporting': ['reporting', 'reports', 'financial.*reports']
                }
            },
            
            # Sales related files
            'sales': {
                'patterns': [
                    r'.*sales.*', r'.*ventas.*', r'.*selling.*', r'.*closing.*',
                    r'.*pitch.*', r'.*proposal.*', r'.*customer.*', r'.*client.*',
                    r'.*revenue.*', r'.*conversion.*', r'.*leads.*'
                ],
                'main_folder': '09_Sales',
                'subcategories': {
                    'sales_strategy': ['sales.*strategy', 'strategy'],
                    'closing_techniques': ['closing', 'close.*sales', 'techniques'],
                    'customer_management': ['customer', 'client', 'crm'],
                    'lead_generation': ['lead.*generation', 'leads', 'prospects'],
                    'sales_automation': ['sales.*automation', 'automation'],
                    'sales_analytics': ['sales.*analytics', 'metrics', 'kpi']
                }
            },
            
            # Operations related files
            'operations': {
                'patterns': [
                    r'.*operations.*', r'.*operational.*', r'.*process.*', r'.*workflow.*',
                    r'.*efficiency.*', r'.*optimization.*', r'.*management.*', r'.*administration.*'
                ],
                'main_folder': '04_Operations',
                'subcategories': {
                    'process_optimization': ['process', 'optimization', 'efficiency'],
                    'workflow_management': ['workflow', 'process.*management'],
                    'operational_excellence': ['operational.*excellence', 'best.*practices'],
                    'supply_chain': ['supply.*chain', 'logistics', 'procurement'],
                    'quality_management': ['quality.*management', 'quality.*assurance']
                }
            },
            
            # Human Resources related files
            'hr': {
                'patterns': [
                    r'.*human.*resources.*', r'.*hr.*', r'.*employee.*', r'.*staff.*',
                    r'.*recruitment.*', r'.*training.*', r'.*performance.*', r'.*talent.*'
                ],
                'main_folder': '03_Human_Resources',
                'subcategories': {
                    'recruitment': ['recruitment', 'hiring', 'talent.*acquisition'],
                    'training_development': ['training', 'development', 'learning'],
                    'performance_management': ['performance', 'evaluation', 'review'],
                    'employee_relations': ['employee.*relations', 'engagement'],
                    'compensation_benefits': ['compensation', 'benefits', 'payroll']
                }
            }
        }
    
    def log_organization(self, action, source, destination):
        """Log organization actions"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {action}: {source} -> {destination}"
        self.organization_log.append(log_entry)
        print(log_entry)
    
    def get_file_category(self, filename):
        """Determine the category for a file based on its name"""
        filename_lower = filename.lower()
        
        for category, config in self.file_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, filename_lower):
                    return category, config
        return None, None
    
    def get_subcategory(self, filename, category_config):
        """Determine the subcategory for a file"""
        filename_lower = filename.lower()
        
        for subcategory, patterns in category_config['subcategories'].items():
            for pattern in patterns:
                if re.search(pattern, filename_lower):
                    return subcategory
        return 'general'
    
    def organize_file(self, file_path):
        """Organize a single file into appropriate folder"""
        filename = file_path.name
        category, category_config = self.get_file_category(filename)
        
        if not category:
            return False
        
        # Determine subcategory
        subcategory = self.get_subcategory(filename, category_config)
        
        # Create target path
        main_folder = category_config['main_folder']
        target_dir = self.base_path / main_folder / f"{subcategory}"
        
        # Create target directory if it doesn't exist
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Move file
        target_path = target_dir / filename
        
        try:
            if file_path.exists() and not target_path.exists():
                shutil.move(str(file_path), str(target_path))
                self.log_organization("MOVED", str(file_path), str(target_path))
                return True
            elif target_path.exists():
                self.log_organization("SKIPPED (exists)", str(file_path), str(target_path))
                return False
        except Exception as e:
            self.log_organization("ERROR", str(file_path), f"Error: {str(e)}")
            return False
    
    def organize_directory(self):
        """Organize all files in the base directory"""
        print("Starting advanced file organization...")
        print(f"Base path: {self.base_path}")
        
        # Get all files in the base directory (not in subdirectories)
        files_to_organize = []
        for item in self.base_path.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                files_to_organize.append(item)
        
        print(f"Found {len(files_to_organize)} files to organize")
        
        organized_count = 0
        for file_path in files_to_organize:
            if self.organize_file(file_path):
                organized_count += 1
        
        print(f"Successfully organized {organized_count} files")
        
        # Save organization log
        log_file = self.base_path / "organization_log.txt"
        with open(log_file, 'w', encoding='utf-8') as f:
            for entry in self.organization_log:
                f.write(entry + '\n')
        
        print(f"Organization log saved to: {log_file}")
    
    def create_organization_summary(self):
        """Create a summary of the organization structure"""
        summary_file = self.base_path / "ORGANIZATION_SUMMARY.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# Advanced File Organization Summary\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Business Areas and Subcategories\n\n")
            
            for category, config in self.file_patterns.items():
                f.write(f"### {config['main_folder']}\n")
                f.write(f"**Category**: {category.title()}\n\n")
                f.write("**Subcategories**:\n")
                for subcategory in config['subcategories'].keys():
                    f.write(f"- {subcategory}\n")
                f.write("\n")
            
            f.write("## Organization Log\n\n")
            for entry in self.organization_log:
                f.write(f"- {entry}\n")
        
        print(f"Organization summary saved to: {summary_file}")

def main():
    # Initialize organizer
    base_path = r"C:\Users\blatam\documentos_blatam"
    organizer = AdvancedFileOrganizer(base_path)
    
    # Organize files
    organizer.organize_directory()
    
    # Create summary
    organizer.create_organization_summary()
    
    print("\nAdvanced file organization completed!")

if __name__ == "__main__":
    main()














