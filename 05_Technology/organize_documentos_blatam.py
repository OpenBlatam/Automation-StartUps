#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Organización de Documentos Blatam
Organiza automáticamente los archivos en las carpetas correspondientes según su contenido y propósito.
"""

import os
import shutil
import re
from pathlib import Path
from typing import Dict, List, Tuple
import json

class DocumentosBlatamOrganizer:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.organization_rules = self._load_organization_rules()
        self.moved_files = []
        self.errors = []
        
    def _load_organization_rules(self) -> Dict[str, Dict]:
        """Define las reglas de organización basadas en patrones de archivos"""
        return {
            # MARKETING Y VENTAS
            'marketing': {
                'patterns': [
                    r'.*marketing.*', r'.*marketing.*', r'.*marketing.*',
                    r'.*copy.*', r'.*copywriting.*', r'.*content.*',
                    r'.*campaign.*', r'.*advertising.*', r'.*promotion.*',
                    r'.*brand.*', r'.*social.*', r'.*viral.*',
                    r'.*growth.*', r'.*lead.*', r'.*conversion.*',
                    r'.*ab_test.*', r'.*analytics.*', r'.*roi.*',
                    r'.*anchor_text.*', r'.*seo.*', r'.*sem.*'
                ],
                'target_folder': '01_Marketing',
                'subfolders': {
                    'digital_marketing': [r'.*digital.*', r'.*online.*', r'.*web.*'],
                    'ai_marketing': [r'.*ai.*marketing.*', r'.*neural.*', r'.*consciousness.*'],
                    'content_marketing': [r'.*content.*', r'.*copy.*', r'.*copywriting.*'],
                    'analytics': [r'.*analytics.*', r'.*metrics.*', r'.*dashboard.*', r'.*roi.*'],
                    'campaigns': [r'.*campaign.*', r'.*ab_test.*', r'.*anchor_text.*']
                }
            },
            
            # TECNOLOGÍA E IA
            'technology': {
                'patterns': [
                    r'.*tech.*', r'.*technology.*', r'.*ai.*', r'.*artificial.*',
                    r'.*machine.*learning.*', r'.*ml.*', r'.*neural.*',
                    r'.*quantum.*', r'.*blockchain.*', r'.*web3.*',
                    r'.*api.*', r'.*software.*', r'.*development.*',
                    r'.*code.*', r'.*programming.*', r'.*system.*',
                    r'.*automation.*', r'.*integration.*', r'.*deployment.*',
                    r'.*docker.*', r'.*kubernetes.*', r'.*cloud.*',
                    r'.*database.*', r'.*server.*', r'.*frontend.*', r'.*backend.*'
                ],
                'target_folder': '05_Technology',
                'subfolders': {
                    'ai_ml': [r'.*ai.*', r'.*ml.*', r'.*neural.*', r'.*consciousness.*'],
                    'blockchain': [r'.*blockchain.*', r'.*web3.*', r'.*crypto.*'],
                    'quantum': [r'.*quantum.*', r'.*quantum.*computing.*'],
                    'automation': [r'.*automation.*', r'.*workflow.*', r'.*integration.*'],
                    'development': [r'.*code.*', r'.*programming.*', r'.*api.*', r'.*software.*']
                }
            },
            
            # FINANZAS
            'finance': {
                'patterns': [
                    r'.*finance.*', r'.*financial.*', r'.*money.*', r'.*revenue.*',
                    r'.*profit.*', r'.*investment.*', r'.*funding.*', r'.*fundraising.*',
                    r'.*valuation.*', r'.*roi.*', r'.*budget.*', r'.*cost.*',
                    r'.*fintech.*', r'.*payment.*', r'.*billing.*', r'.*invoice.*'
                ],
                'target_folder': '02_Finance',
                'subfolders': {
                    'financial_planning': [r'.*planning.*', r'.*budget.*', r'.*forecast.*'],
                    'investment': [r'.*investment.*', r'.*funding.*', r'.*valuation.*'],
                    'fintech': [r'.*fintech.*', r'.*payment.*', r'.*billing.*']
                }
            },
            
            # RECURSOS HUMANOS
            'hr': {
                'patterns': [
                    r'.*hr.*', r'.*human.*resources.*', r'.*employee.*', r'.*staff.*',
                    r'.*recruitment.*', r'.*hiring.*', r'.*training.*', r'.*development.*',
                    r'.*performance.*', r'.*management.*', r'.*leadership.*',
                    r'.*culture.*', r'.*team.*', r'.*workforce.*'
                ],
                'target_folder': '03_Human_Resources',
                'subfolders': {
                    'recruitment': [r'.*recruitment.*', r'.*hiring.*', r'.*talent.*'],
                    'training': [r'.*training.*', r'.*development.*', r'.*learning.*'],
                    'management': [r'.*management.*', r'.*leadership.*', r'.*performance.*']
                }
            },
            
            # ESTRATEGIA DE NEGOCIO
            'strategy': {
                'patterns': [
                    r'.*strategy.*', r'.*strategic.*', r'.*business.*', r'.*plan.*',
                    r'.*roadmap.*', r'.*framework.*', r'.*methodology.*',
                    r'.*competitive.*', r'.*market.*', r'.*positioning.*',
                    r'.*growth.*', r'.*expansion.*', r'.*scaling.*'
                ],
                'target_folder': '04_Business_Strategy',
                'subfolders': {
                    'strategic_planning': [r'.*planning.*', r'.*roadmap.*', r'.*framework.*'],
                    'competitive_analysis': [r'.*competitive.*', r'.*analysis.*', r'.*market.*'],
                    'growth_strategy': [r'.*growth.*', r'.*expansion.*', r'.*scaling.*']
                }
            },
            
            # OPERACIONES
            'operations': {
                'patterns': [
                    r'.*operation.*', r'.*operational.*', r'.*process.*', r'.*workflow.*',
                    r'.*efficiency.*', r'.*optimization.*', r'.*productivity.*',
                    r'.*supply.*chain.*', r'.*logistics.*', r'.*procurement.*',
                    r'.*quality.*', r'.*compliance.*', r'.*governance.*'
                ],
                'target_folder': '04_Operations',
                'subfolders': {
                    'process_optimization': [r'.*process.*', r'.*optimization.*', r'.*efficiency.*'],
                    'supply_chain': [r'.*supply.*chain.*', r'.*logistics.*', r'.*procurement.*'],
                    'quality_compliance': [r'.*quality.*', r'.*compliance.*', r'.*governance.*']
                }
            },
            
            # DOCUMENTACIÓN
            'documentation': {
                'patterns': [
                    r'.*doc.*', r'.*documentation.*', r'.*guide.*', r'.*manual.*',
                    r'.*tutorial.*', r'.*instruction.*', r'.*help.*', r'.*faq.*',
                    r'.*readme.*', r'.*index.*', r'.*overview.*', r'.*summary.*',
                    r'.*specification.*', r'.*requirements.*', r'.*changelog.*'
                ],
                'target_folder': '06_Documentation',
                'subfolders': {
                    'user_guides': [r'.*guide.*', r'.*manual.*', r'.*tutorial.*'],
                    'technical_docs': [r'.*specification.*', r'.*requirements.*', r'.*api.*'],
                    'overview': [r'.*overview.*', r'.*summary.*', r'.*readme.*']
                }
            },
            
            # GESTIÓN DE RIESGOS
            'risk_management': {
                'patterns': [
                    r'.*risk.*', r'.*security.*', r'.*safety.*', r'.*compliance.*',
                    r'.*governance.*', r'.*audit.*', r'.*control.*', r'.*mitigation.*',
                    r'.*cyber.*', r'.*privacy.*', r'.*protection.*'
                ],
                'target_folder': '07_Risk_Management',
                'subfolders': {
                    'risk_assessment': [r'.*assessment.*', r'.*analysis.*', r'.*evaluation.*'],
                    'security': [r'.*security.*', r'.*cyber.*', r'.*privacy.*'],
                    'compliance': [r'.*compliance.*', r'.*governance.*', r'.*audit.*']
                }
            },
            
            # VENTAS
            'sales': {
                'patterns': [
                    r'.*sales.*', r'.*selling.*', r'.*pitch.*', r'.*proposal.*',
                    r'.*negotiation.*', r'.*closing.*', r'.*conversion.*',
                    r'.*customer.*', r'.*client.*', r'.*prospect.*', r'.*lead.*',
                    r'.*crm.*', r'.*pipeline.*', r'.*revenue.*'
                ],
                'target_folder': '09_Sales',
                'subfolders': {
                    'sales_strategy': [r'.*strategy.*', r'.*planning.*', r'.*approach.*'],
                    'pitch_proposals': [r'.*pitch.*', r'.*proposal.*', r'.*presentation.*'],
                    'crm_management': [r'.*crm.*', r'.*pipeline.*', r'.*management.*']
                }
            },
            
            # ATENCIÓN AL CLIENTE
            'customer_service': {
                'patterns': [
                    r'.*customer.*service.*', r'.*support.*', r'.*help.*', r'.*service.*',
                    r'.*experience.*', r'.*satisfaction.*', r'.*feedback.*',
                    r'.*complaint.*', r'.*resolution.*', r'.*ticket.*'
                ],
                'target_folder': '10_Customer_Service',
                'subfolders': {
                    'support': [r'.*support.*', r'.*help.*', r'.*ticket.*'],
                    'experience': [r'.*experience.*', r'.*satisfaction.*', r'.*feedback.*']
                }
            },
            
            # I+D E INNOVACIÓN
            'rd_innovation': {
                'patterns': [
                    r'.*research.*', r'.*development.*', r'.*innovation.*', r'.*r&d.*',
                    r'.*experiment.*', r'.*prototype.*', r'.*testing.*', r'.*validation.*',
                    r'.*discovery.*', r'.*invention.*', r'.*patent.*'
                ],
                'target_folder': '11_Research_Development',
                'subfolders': {
                    'research': [r'.*research.*', r'.*study.*', r'.*analysis.*'],
                    'development': [r'.*development.*', r'.*prototype.*', r'.*testing.*'],
                    'innovation': [r'.*innovation.*', r'.*invention.*', r'.*patent.*']
                }
            },
            
            # ARQUITECTURA DE SISTEMAS
            'system_architecture': {
                'patterns': [
                    r'.*architecture.*', r'.*system.*', r'.*infrastructure.*', r'.*platform.*',
                    r'.*microservice.*', r'.*api.*', r'.*database.*', r'.*server.*',
                    r'.*deployment.*', r'.*devops.*', r'.*ci.*cd.*'
                ],
                'target_folder': '11_System_Architecture',
                'subfolders': {
                    'architecture': [r'.*architecture.*', r'.*design.*', r'.*structure.*'],
                    'infrastructure': [r'.*infrastructure.*', r'.*platform.*', r'.*server.*'],
                    'devops': [r'.*devops.*', r'.*deployment.*', r'.*ci.*cd.*']
                }
            },
            
            # ASEGURAMIENTO DE CALIDAD
            'quality_assurance': {
                'patterns': [
                    r'.*quality.*', r'.*testing.*', r'.*qa.*', r'.*test.*',
                    r'.*validation.*', r'.*verification.*', r'.*inspection.*',
                    r'.*standard.*', r'.*certification.*', r'.*audit.*'
                ],
                'target_folder': '12_Quality_Assurance',
                'subfolders': {
                    'testing': [r'.*testing.*', r'.*test.*', r'.*validation.*'],
                    'standards': [r'.*standard.*', r'.*certification.*', r'.*compliance.*'],
                    'audit': [r'.*audit.*', r'.*inspection.*', r'.*review.*']
                }
            },
            
            # GUÍAS DE USUARIO
            'user_guides': {
                'patterns': [
                    r'.*user.*', r'.*guide.*', r'.*tutorial.*', r'.*manual.*',
                    r'.*instruction.*', r'.*how.*to.*', r'.*step.*by.*step.*',
                    r'.*walkthrough.*', r'.*demo.*', r'.*example.*'
                ],
                'target_folder': '12_User_Guides',
                'subfolders': {
                    'tutorials': [r'.*tutorial.*', r'.*how.*to.*', r'.*step.*by.*step.*'],
                    'manuals': [r'.*manual.*', r'.*instruction.*', r'.*guide.*'],
                    'demos': [r'.*demo.*', r'.*example.*', r'.*walkthrough.*']
                }
            },
            
            # CUMPLIMIENTO LEGAL
            'legal_compliance': {
                'patterns': [
                    r'.*legal.*', r'.*law.*', r'.*regulation.*', r'.*compliance.*',
                    r'.*policy.*', r'.*terms.*', r'.*privacy.*', r'.*gdpr.*',
                    r'.*contract.*', r'.*agreement.*', r'.*license.*'
                ],
                'target_folder': '13_Legal_Compliance',
                'subfolders': {
                    'legal_docs': [r'.*legal.*', r'.*law.*', r'.*regulation.*'],
                    'policies': [r'.*policy.*', r'.*terms.*', r'.*privacy.*'],
                    'contracts': [r'.*contract.*', r'.*agreement.*', r'.*license.*']
                }
            },
            
            # COMPRAS Y ADQUISICIONES
            'procurement': {
                'patterns': [
                    r'.*procurement.*', r'.*purchase.*', r'.*buying.*', r'.*acquisition.*',
                    r'.*vendor.*', r'.*supplier.*', r'.*contract.*', r'.*rfp.*',
                    r'.*tender.*', r'.*sourcing.*', r'.*negotiation.*'
                ],
                'target_folder': '14_Procurement',
                'subfolders': {
                    'sourcing': [r'.*sourcing.*', r'.*vendor.*', r'.*supplier.*'],
                    'contracts': [r'.*contract.*', r'.*agreement.*', r'.*rfp.*'],
                    'negotiation': [r'.*negotiation.*', r'.*tender.*', r'.*bidding.*']
                }
            },
            
            # GESTIÓN DE PRODUCTOS
            'product_management': {
                'patterns': [
                    r'.*product.*', r'.*feature.*', r'.*roadmap.*', r'.*backlog.*',
                    r'.*requirement.*', r'.*specification.*', r'.*design.*',
                    r'.*launch.*', r'.*release.*', r'.*version.*'
                ],
                'target_folder': '14_Product_Management',
                'subfolders': {
                    'product_strategy': [r'.*strategy.*', r'.*roadmap.*', r'.*planning.*'],
                    'requirements': [r'.*requirement.*', r'.*specification.*', r'.*design.*'],
                    'releases': [r'.*release.*', r'.*launch.*', r'.*version.*']
                }
            },
            
            # LIDERAZGO DE PENSAMIENTO
            'thought_leadership': {
                'patterns': [
                    r'.*thought.*leadership.*', r'.*expert.*', r'.*authority.*',
                    r'.*insight.*', r'.*opinion.*', r'.*perspective.*',
                    r'.*trend.*', r'.*future.*', r'.*vision.*'
                ],
                'target_folder': '14_Thought_Leadership',
                'subfolders': {
                    'insights': [r'.*insight.*', r'.*analysis.*', r'.*research.*'],
                    'opinions': [r'.*opinion.*', r'.*perspective.*', r'.*viewpoint.*'],
                    'trends': [r'.*trend.*', r'.*future.*', r'.*prediction.*']
                }
            },
            
            # EXPERIENCIA DEL CLIENTE
            'customer_experience': {
                'patterns': [
                    r'.*customer.*experience.*', r'.*cx.*', r'.*journey.*',
                    r'.*touchpoint.*', r'.*interaction.*', r'.*engagement.*',
                    r'.*satisfaction.*', r'.*loyalty.*', r'.*retention.*'
                ],
                'target_folder': '15_Customer_Experience',
                'subfolders': {
                    'journey_mapping': [r'.*journey.*', r'.*mapping.*', r'.*flow.*'],
                    'engagement': [r'.*engagement.*', r'.*interaction.*', r'.*touchpoint.*'],
                    'satisfaction': [r'.*satisfaction.*', r'.*loyalty.*', r'.*retention.*']
                }
            },
            
            # ANÁLISIS DE DATOS
            'data_analytics': {
                'patterns': [
                    r'.*data.*', r'.*analytics.*', r'.*analysis.*', r'.*insight.*',
                    r'.*metrics.*', r'.*kpi.*', r'.*dashboard.*', r'.*report.*',
                    r'.*statistics.*', r'.*trend.*', r'.*prediction.*'
                ],
                'target_folder': '16_Data_Analytics',
                'subfolders': {
                    'data_analysis': [r'.*analysis.*', r'.*insight.*', r'.*statistics.*'],
                    'dashboards': [r'.*dashboard.*', r'.*visualization.*', r'.*chart.*'],
                    'reporting': [r'.*report.*', r'.*kpi.*', r'.*metrics.*']
                }
            },
            
            # INNOVACIÓN
            'innovation': {
                'patterns': [
                    r'.*innovation.*', r'.*creative.*', r'.*disruptive.*', r'.*breakthrough.*',
                    r'.*invention.*', r'.*patent.*', r'.*ip.*', r'.*intellectual.*property.*',
                    r'.*lab.*', r'.*experiment.*', r'.*pilot.*'
                ],
                'target_folder': '17_Innovation',
                'subfolders': {
                    'innovation_lab': [r'.*lab.*', r'.*experiment.*', r'.*pilot.*'],
                    'ip_management': [r'.*ip.*', r'.*patent.*', r'.*intellectual.*property.*'],
                    'disruptive_tech': [r'.*disruptive.*', r'.*breakthrough.*', r'.*revolutionary.*']
                }
            },
            
            # SOSTENIBILIDAD
            'sustainability': {
                'patterns': [
                    r'.*sustainability.*', r'.*sustainable.*', r'.*green.*', r'.*environment.*',
                    r'.*esg.*', r'.*carbon.*', r'.*climate.*', r'.*renewable.*',
                    r'.*social.*responsibility.*', r'.*csr.*'
                ],
                'target_folder': '18_Sustainability',
                'subfolders': {
                    'environmental': [r'.*environment.*', r'.*green.*', r'.*carbon.*', r'.*climate.*'],
                    'esg': [r'.*esg.*', r'.*sustainable.*', r'.*renewable.*'],
                    'csr': [r'.*csr.*', r'.*social.*responsibility.*', r'.*community.*']
                }
            },
            
            # NEGOCIOS INTERNACIONALES
            'international_business': {
                'patterns': [
                    r'.*international.*', r'.*global.*', r'.*multinational.*', r'.*cross.*cultural.*',
                    r'.*export.*', r'.*import.*', r'.*trade.*', r'.*localization.*',
                    r'.*translation.*', r'.*currency.*', r'.*exchange.*'
                ],
                'target_folder': '19_International_Business',
                'subfolders': {
                    'global_strategy': [r'.*global.*', r'.*international.*', r'.*multinational.*'],
                    'trade': [r'.*trade.*', r'.*export.*', r'.*import.*'],
                    'localization': [r'.*localization.*', r'.*translation.*', r'.*cultural.*']
                }
            },
            
            # GESTIÓN DE PROYECTOS
            'project_management': {
                'patterns': [
                    r'.*project.*', r'.*pm.*', r'.*agile.*', r'.*scrum.*', r'.*kanban.*',
                    r'.*milestone.*', r'.*deliverable.*', r'.*timeline.*', r'.*schedule.*',
                    r'.*resource.*', r'.*budget.*', r'.*scope.*'
                ],
                'target_folder': '20_Project_Management',
                'subfolders': {
                    'methodologies': [r'.*agile.*', r'.*scrum.*', r'.*kanban.*', r'.*waterfall.*'],
                    'planning': [r'.*planning.*', r'.*timeline.*', r'.*schedule.*', r'.*milestone.*'],
                    'execution': [r'.*execution.*', r'.*deliverable.*', r'.*resource.*']
                }
            },
            
            # CADENA DE SUMINISTRO
            'supply_chain': {
                'patterns': [
                    r'.*supply.*chain.*', r'.*logistics.*', r'.*inventory.*', r'.*warehouse.*',
                    r'.*distribution.*', r'.*shipping.*', r'.*transport.*', r'.*delivery.*',
                    r'.*procurement.*', r'.*sourcing.*', r'.*vendor.*'
                ],
                'target_folder': '21_Supply_Chain',
                'subfolders': {
                    'logistics': [r'.*logistics.*', r'.*shipping.*', r'.*transport.*', r'.*delivery.*'],
                    'inventory': [r'.*inventory.*', r'.*warehouse.*', r'.*storage.*'],
                    'sourcing': [r'.*sourcing.*', r'.*procurement.*', r'.*vendor.*']
                }
            },
            
            # BIENES RAÍCES
            'real_estate': {
                'patterns': [
                    r'.*real.*estate.*', r'.*property.*', r'.*building.*', r'.*construction.*',
                    r'.*development.*', r'.*investment.*', r'.*valuation.*', r'.*lease.*',
                    r'.*rental.*', r'.*commercial.*', r'.*residential.*'
                ],
                'target_folder': '22_Real_Estate',
                'subfolders': {
                    'development': [r'.*development.*', r'.*construction.*', r'.*building.*'],
                    'investment': [r'.*investment.*', r'.*valuation.*', r'.*finance.*'],
                    'management': [r'.*management.*', r'.*lease.*', r'.*rental.*']
                }
            },
            
            # SALUD
            'healthcare': {
                'patterns': [
                    r'.*health.*', r'.*medical.*', r'.*healthcare.*', r'.*patient.*',
                    r'.*treatment.*', r'.*diagnosis.*', r'.*therapy.*', r'.*clinical.*',
                    r'.*pharmaceutical.*', r'.*drug.*', r'.*medicine.*'
                ],
                'target_folder': '23_Healthcare',
                'subfolders': {
                    'clinical': [r'.*clinical.*', r'.*medical.*', r'.*patient.*'],
                    'pharmaceutical': [r'.*pharmaceutical.*', r'.*drug.*', r'.*medicine.*'],
                    'healthcare_tech': [r'.*health.*tech.*', r'.*digital.*health.*', r'.*telemedicine.*']
                }
            },
            
            # EDUCACIÓN
            'education': {
                'patterns': [
                    r'.*education.*', r'.*learning.*', r'.*training.*', r'.*course.*',
                    r'.*curriculum.*', r'.*student.*', r'.*teacher.*', r'.*academic.*',
                    r'.*university.*', r'.*school.*', r'.*institute.*'
                ],
                'target_folder': '24_Education',
                'subfolders': {
                    'curriculum': [r'.*curriculum.*', r'.*course.*', r'.*syllabus.*'],
                    'learning': [r'.*learning.*', r'.*training.*', r'.*education.*'],
                    'institutions': [r'.*university.*', r'.*school.*', r'.*institute.*']
                }
            },
            
            # GOBIERNO
            'government': {
                'patterns': [
                    r'.*government.*', r'.*public.*', r'.*policy.*', r'.*regulation.*',
                    r'.*compliance.*', r'.*governance.*', r'.*administration.*',
                    r'.*citizen.*', r'.*service.*', r'.*digital.*government.*'
                ],
                'target_folder': '25_Government',
                'subfolders': {
                    'policy': [r'.*policy.*', r'.*regulation.*', r'.*governance.*'],
                    'public_services': [r'.*public.*service.*', r'.*citizen.*', r'.*administration.*'],
                    'digital_government': [r'.*digital.*government.*', r'.*e.*government.*']
                }
            },
            
            # SIN FINES DE LUCRO
            'non_profit': {
                'patterns': [
                    r'.*non.*profit.*', r'.*ngo.*', r'.*charity.*', r'.*foundation.*',
                    r'.*donation.*', r'.*fundraising.*', r'.*volunteer.*', r'.*community.*',
                    r'.*social.*impact.*', r'.*mission.*', r'.*cause.*'
                ],
                'target_folder': '26_Non_Profit',
                'subfolders': {
                    'fundraising': [r'.*fundraising.*', r'.*donation.*', r'.*grant.*'],
                    'volunteer': [r'.*volunteer.*', r'.*community.*', r'.*engagement.*'],
                    'impact': [r'.*impact.*', r'.*mission.*', r'.*cause.*']
                }
            },
            
            # ENTRETENIMIENTO
            'entertainment': {
                'patterns': [
                    r'.*entertainment.*', r'.*media.*', r'.*content.*', r'.*production.*',
                    r'.*film.*', r'.*movie.*', r'.*tv.*', r'.*streaming.*', r'.*music.*',
                    r'.*gaming.*', r'.*sports.*', r'.*event.*'
                ],
                'target_folder': '27_Entertainment',
                'subfolders': {
                    'content_production': [r'.*production.*', r'.*content.*', r'.*media.*'],
                    'gaming': [r'.*gaming.*', r'.*game.*', r'.*interactive.*'],
                    'events': [r'.*event.*', r'.*concert.*', r'.*show.*']
                }
            },
            
            # DEPORTES
            'sports': {
                'patterns': [
                    r'.*sport.*', r'.*athletic.*', r'.*fitness.*', r'.*training.*',
                    r'.*competition.*', r'.*league.*', r'.*team.*', r'.*player.*',
                    r'.*coach.*', r'.*performance.*', r'.*analytics.*'
                ],
                'target_folder': '28_Sports',
                'subfolders': {
                    'training': [r'.*training.*', r'.*fitness.*', r'.*coaching.*'],
                    'competition': [r'.*competition.*', r'.*league.*', r'.*tournament.*'],
                    'analytics': [r'.*analytics.*', r'.*performance.*', r'.*statistics.*']
                }
            },
            
            # MEDIOS
            'media': {
                'patterns': [
                    r'.*media.*', r'.*journalism.*', r'.*news.*', r'.*publishing.*',
                    r'.*broadcast.*', r'.*radio.*', r'.*television.*', r'.*digital.*media.*',
                    r'.*social.*media.*', r'.*content.*', r'.*editorial.*'
                ],
                'target_folder': '29_Media',
                'subfolders': {
                    'journalism': [r'.*journalism.*', r'.*news.*', r'.*editorial.*'],
                    'broadcasting': [r'.*broadcast.*', r'.*radio.*', r'.*television.*'],
                    'digital_media': [r'.*digital.*media.*', r'.*social.*media.*', r'.*online.*']
                }
            },
            
            # CONSULTORÍA
            'consulting': {
                'patterns': [
                    r'.*consulting.*', r'.*consultant.*', r'.*advisory.*', r'.*expert.*',
                    r'.*strategy.*', r'.*transformation.*', r'.*change.*', r'.*improvement.*',
                    r'.*assessment.*', r'.*analysis.*', r'.*recommendation.*'
                ],
                'target_folder': '30_Consulting',
                'subfolders': {
                    'strategy_consulting': [r'.*strategy.*', r'.*advisory.*', r'.*planning.*'],
                    'transformation': [r'.*transformation.*', r'.*change.*', r'.*improvement.*'],
                    'assessment': [r'.*assessment.*', r'.*analysis.*', r'.*evaluation.*']
                }
            },
            
            # SERVICIOS PROFESIONALES
            'professional_services': {
                'patterns': [
                    r'.*professional.*service.*', r'.*service.*', r'.*client.*', r'.*delivery.*',
                    r'.*expertise.*', r'.*specialist.*', r'.*practitioner.*', r'.*advisor.*',
                    r'.*support.*', r'.*assistance.*', r'.*solution.*'
                ],
                'target_folder': '31_Professional_Services',
                'subfolders': {
                    'service_delivery': [r'.*delivery.*', r'.*service.*', r'.*support.*'],
                    'expertise': [r'.*expertise.*', r'.*specialist.*', r'.*practitioner.*'],
                    'solutions': [r'.*solution.*', r'.*assistance.*', r'.*help.*']
                }
            },
            
            # MANUFACTURA
            'manufacturing': {
                'patterns': [
                    r'.*manufacturing.*', r'.*production.*', r'.*factory.*', r'.*assembly.*',
                    r'.*quality.*control.*', r'.*process.*', r'.*equipment.*', r'.*machinery.*',
                    r'.*automation.*', r'.*efficiency.*', r'.*optimization.*'
                ],
                'target_folder': '32_Manufacturing',
                'subfolders': {
                    'production': [r'.*production.*', r'.*assembly.*', r'.*factory.*'],
                    'quality_control': [r'.*quality.*control.*', r'.*inspection.*', r'.*testing.*'],
                    'automation': [r'.*automation.*', r'.*robotics.*', r'.*machinery.*']
                }
            },
            
            # RETAIL
            'retail': {
                'patterns': [
                    r'.*retail.*', r'.*store.*', r'.*shop.*', r'.*merchandise.*', r'.*inventory.*',
                    r'.*customer.*', r'.*sales.*', r'.*point.*of.*sale.*', r'.*pos.*',
                    r'.*supply.*chain.*', r'.*distribution.*', r'.*logistics.*'
                ],
                'target_folder': '33_Retail',
                'subfolders': {
                    'store_operations': [r'.*store.*', r'.*shop.*', r'.*merchandise.*'],
                    'sales': [r'.*sales.*', r'.*pos.*', r'.*point.*of.*sale.*'],
                    'inventory': [r'.*inventory.*', r'.*stock.*', r'.*supply.*chain.*']
                }
            },
            
            # COMERCIO ELECTRÓNICO
            'ecommerce': {
                'patterns': [
                    r'.*ecommerce.*', r'.*e.*commerce.*', r'.*online.*shop.*', r'.*digital.*store.*',
                    r'.*marketplace.*', r'.*platform.*', r'.*payment.*', r'.*checkout.*',
                    r'.*shopping.*cart.*', r'.*order.*', r'.*fulfillment.*'
                ],
                'target_folder': '34_E_Commerce',
                'subfolders': {
                    'platform': [r'.*platform.*', r'.*marketplace.*', r'.*digital.*store.*'],
                    'payments': [r'.*payment.*', r'.*checkout.*', r'.*billing.*'],
                    'fulfillment': [r'.*fulfillment.*', r'.*shipping.*', r'.*delivery.*']
                }
            }
        }
    
    def organize_files(self):
        """Organiza todos los archivos según las reglas definidas"""
        print("🚀 Iniciando organización de documentos Blatam...")
        
        # Obtener todos los archivos en el directorio raíz
        root_files = [f for f in self.base_path.iterdir() if f.is_file()]
        
        for file_path in root_files:
            try:
                self._organize_file(file_path)
            except Exception as e:
                error_msg = f"Error procesando {file_path.name}: {str(e)}"
                self.errors.append(error_msg)
                print(f"❌ {error_msg}")
        
        # Generar reporte
        self._generate_report()
    
    def _organize_file(self, file_path: Path):
        """Organiza un archivo individual según las reglas"""
        file_name = file_path.name.lower()
        
        # Buscar la categoría más apropiada
        best_match = self._find_best_category(file_name)
        
        if best_match:
            category, subfolder = best_match
            self._move_file(file_path, category, subfolder)
        else:
            # Si no encuentra categoría específica, mover a documentación general
            self._move_file(file_path, 'documentation', 'overview')
    
    def _find_best_category(self, file_name: str) -> Tuple[str, str]:
        """Encuentra la mejor categoría para un archivo basado en su nombre"""
        best_score = 0
        best_category = None
        best_subfolder = None
        
        for category, rules in self.organization_rules.items():
            # Verificar patrones principales
            for pattern in rules['patterns']:
                if re.search(pattern, file_name, re.IGNORECASE):
                    score = len(pattern)  # Puntuación basada en longitud del patrón
                    if score > best_score:
                        best_score = score
                        best_category = category
                        best_subfolder = None
                        
                        # Verificar subcarpetas
                        if 'subfolders' in rules:
                            for subfolder, subpatterns in rules['subfolders'].items():
                                for subpattern in subpatterns:
                                    if re.search(subpattern, file_name, re.IGNORECASE):
                                        best_subfolder = subfolder
                                        break
        
        return (best_category, best_subfolder) if best_category else None
    
    def _move_file(self, file_path: Path, category: str, subfolder: str = None):
        """Mueve un archivo a su ubicación correspondiente"""
        target_folder = self.base_path / self.organization_rules[category]['target_folder']
        
        if subfolder:
            target_folder = target_folder / subfolder
        
        # Crear directorio si no existe
        target_folder.mkdir(parents=True, exist_ok=True)
        
        # Mover archivo
        target_path = target_folder / file_path.name
        
        # Si el archivo ya existe, agregar sufijo
        counter = 1
        while target_path.exists():
            name_parts = file_path.stem, counter, file_path.suffix
            target_path = target_folder / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
            counter += 1
        
        shutil.move(str(file_path), str(target_path))
        
        # Registrar movimiento
        self.moved_files.append({
            'original': str(file_path),
            'new_location': str(target_path),
            'category': category,
            'subfolder': subfolder
        })
        
        print(f"✅ Movido: {file_path.name} → {target_path.relative_to(self.base_path)}")
    
    def _generate_report(self):
        """Genera un reporte de la organización"""
        report = {
            'total_files_moved': len(self.moved_files),
            'errors': self.errors,
            'files_by_category': {},
            'summary': {}
        }
        
        # Agrupar por categoría
        for file_info in self.moved_files:
            category = file_info['category']
            if category not in report['files_by_category']:
                report['files_by_category'][category] = []
            report['files_by_category'][category].append(file_info)
        
        # Generar resumen
        for category, files in report['files_by_category'].items():
            report['summary'][category] = len(files)
        
        # Guardar reporte
        report_path = self.base_path / 'organization_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Mostrar resumen
        print("\n📊 RESUMEN DE ORGANIZACIÓN:")
        print("=" * 50)
        print(f"Total de archivos organizados: {report['total_files_moved']}")
        print(f"Errores encontrados: {len(report['errors'])}")
        print("\nArchivos por categoría:")
        for category, count in report['summary'].items():
            print(f"  {category}: {count} archivos")
        
        if report['errors']:
            print("\n❌ Errores:")
            for error in report['errors']:
                print(f"  - {error}")
        
        print(f"\n📄 Reporte detallado guardado en: {report_path}")

def main():
    """Función principal"""
    base_path = r"C:\Users\blatam\Documents\documentos_blatam"
    
    if not os.path.exists(base_path):
        print(f"❌ Error: El directorio {base_path} no existe")
        return
    
    organizer = DocumentosBlatamOrganizer(base_path)
    organizer.organize_files()

if __name__ == "__main__":
    main()
