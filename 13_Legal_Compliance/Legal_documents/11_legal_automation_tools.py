#!/usr/bin/env python3
"""
Herramientas de Automatización Legal Avanzadas
Sistema completo para automatizar la generación de documentos legales
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from jinja2 import Template, Environment, FileSystemLoader
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CompanyData:
    """Datos de la empresa"""
    name: str
    jurisdiction: str
    incorporation_date: str
    business_type: str
    industry: str
    stage: str
    revenue: float
    growth_rate: float
    employees: int
    valuation: float
    existing_investors: List[str]
    legal_structure: str

@dataclass
class InvestorData:
    """Datos del inversor"""
    name: str
    type: str  # VC, Corporate VC, Angel, PE
    stage_focus: str
    check_size: float
    portfolio_size: int
    investment_criteria: Dict[str, Any]
    preferred_terms: Dict[str, Any]
    risk_tolerance: str

@dataclass
class MarketData:
    """Datos de mercado"""
    market_size: float
    growth_rate: float
    competition_level: str
    regulatory_environment: str
    economic_conditions: str
    comparable_transactions: List[Dict[str, Any]]
    market_multiples: Dict[str, float]

class LegalTemplateEngine:
    """Motor de templates legales avanzado"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        self.env = Environment(loader=FileSystemLoader(str(self.templates_dir)))
        self.templates = {}
        self.load_templates()
    
    def load_templates(self):
        """Carga todos los templates disponibles"""
        template_files = {
            'term_sheet': 'term_sheet_template.md',
            'investment_agreement': 'investment_agreement_template.md',
            'shareholders_agreement': 'shareholders_agreement_template.md',
            'articles_incorporation': 'articles_incorporation_template.md',
            'due_diligence': 'due_diligence_template.md',
            'legal_opinion': 'legal_opinion_template.md'
        }
        
        for template_name, filename in template_files.items():
            template_path = self.templates_dir / filename
            if template_path.exists():
                self.templates[template_name] = self.env.get_template(filename)
                logger.info(f"Template cargado: {template_name}")
    
    def generate_document(self, template_name: str, data: Dict[str, Any]) -> str:
        """Genera un documento usando un template específico"""
        if template_name not in self.templates:
            raise ValueError(f"Template {template_name} no encontrado")
        
        template = self.templates[template_name]
        return template.render(**data)
    
    def generate_all_documents(self, company_data: CompanyData, 
                             investor_data: InvestorData, 
                             market_data: MarketData) -> Dict[str, str]:
        """Genera todos los documentos legales"""
        documents = {}
        
        # Preparar datos para templates
        template_data = {
            'company': asdict(company_data),
            'investor': asdict(investor_data),
            'market': asdict(market_data),
            'generation_date': datetime.now().strftime('%Y-%m-%d'),
            'transaction_id': f"TXN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        # Generar cada documento
        for template_name in self.templates.keys():
            try:
                documents[template_name] = self.generate_document(template_name, template_data)
                logger.info(f"Documento generado: {template_name}")
            except Exception as e:
                logger.error(f"Error generando {template_name}: {str(e)}")
        
        return documents

class ValuationCalculator:
    """Calculadora de valoración avanzada"""
    
    def __init__(self):
        self.methods = {
            'dcf': self.calculate_dcf,
            'comparable': self.calculate_comparable,
            'precedent': self.calculate_precedent,
            'asset_based': self.calculate_asset_based
        }
    
    def calculate_dcf(self, company_data: CompanyData, 
                     projections: Dict[str, List[float]], 
                     discount_rate: float = 0.12) -> float:
        """Calcula valoración usando DCF"""
        try:
            # Proyecciones de flujo de caja libre
            fcf_projections = projections.get('free_cash_flow', [])
            if not fcf_projections:
                return 0.0
            
            # Calcular valor presente
            pv_fcf = []
            for i, fcf in enumerate(fcf_projections):
                pv = fcf / ((1 + discount_rate) ** (i + 1))
                pv_fcf.append(pv)
            
            # Valor terminal (usando crecimiento perpetuo)
            terminal_growth = 0.03
            terminal_value = (fcf_projections[-1] * (1 + terminal_growth)) / (discount_rate - terminal_growth)
            pv_terminal = terminal_value / ((1 + discount_rate) ** len(fcf_projections))
            
            # Valor de la empresa
            enterprise_value = sum(pv_fcf) + pv_terminal
            
            # Ajustar por deuda neta (simplificado)
            net_debt = 0  # Asumir sin deuda para simplificar
            equity_value = enterprise_value - net_debt
            
            return max(0, equity_value)
            
        except Exception as e:
            logger.error(f"Error en cálculo DCF: {str(e)}")
            return 0.0
    
    def calculate_comparable(self, company_data: CompanyData, 
                           market_data: MarketData) -> float:
        """Calcula valoración usando comparables"""
        try:
            # Obtener múltiplos de mercado
            multiples = market_data.market_multiples
            
            # Usar múltiplo de revenue (P/S)
            if 'price_to_sales' in multiples and company_data.revenue > 0:
                ps_multiple = multiples['price_to_sales']
                valuation = company_data.revenue * ps_multiple
                return valuation
            
            # Usar múltiplo de EBITDA (P/E)
            if 'price_to_ebitda' in multiples:
                # Asumir margen EBITDA del 20% (típico para SaaS)
                ebitda = company_data.revenue * 0.20
                pe_multiple = multiples['price_to_ebitda']
                valuation = ebitda * pe_multiple
                return valuation
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error en cálculo comparable: {str(e)}")
            return 0.0
    
    def calculate_precedent(self, company_data: CompanyData, 
                          market_data: MarketData) -> float:
        """Calcula valoración usando transacciones precedentes"""
        try:
            if not market_data.comparable_transactions:
                return 0.0
            
            # Filtrar transacciones similares
            similar_transactions = []
            for transaction in market_data.comparable_transactions:
                if (transaction.get('industry') == company_data.industry and
                    transaction.get('stage') == company_data.stage):
                    similar_transactions.append(transaction)
            
            if not similar_transactions:
                return 0.0
            
            # Calcular múltiplo promedio
            multiples = []
            for transaction in similar_transactions:
                if transaction.get('revenue') and transaction.get('valuation'):
                    multiple = transaction['valuation'] / transaction['revenue']
                    multiples.append(multiple)
            
            if multiples:
                avg_multiple = np.mean(multiples)
                valuation = company_data.revenue * avg_multiple
                return valuation
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error en cálculo precedente: {str(e)}")
            return 0.0
    
    def calculate_asset_based(self, company_data: CompanyData) -> float:
        """Calcula valoración basada en activos"""
        try:
            # Valoración simplificada basada en activos
            # En la práctica, esto requeriría un balance detallado
            
            # Asumir activos tangibles e intangibles
            tangible_assets = company_data.revenue * 0.5  # 50% del revenue
            intangible_assets = company_data.revenue * 2.0  # 200% del revenue (IP, marca, etc.)
            
            total_assets = tangible_assets + intangible_assets
            
            # Ajustar por pasivos (simplificado)
            liabilities = company_data.revenue * 0.3  # 30% del revenue
            
            net_asset_value = total_assets - liabilities
            
            return max(0, net_asset_value)
            
        except Exception as e:
            logger.error(f"Error en cálculo basado en activos: {str(e)}")
            return 0.0
    
    def calculate_valuation(self, company_data: CompanyData, 
                          market_data: MarketData,
                          method: str = 'weighted_average',
                          projections: Optional[Dict[str, List[float]]] = None) -> Dict[str, float]:
        """Calcula valoración usando múltiples métodos"""
        valuations = {}
        
        # Calcular usando cada método
        for method_name, method_func in self.methods.items():
            if method_name == 'dcf' and projections:
                valuations[method_name] = method_func(company_data, projections)
            elif method_name in ['comparable', 'precedent', 'asset_based']:
                valuations[method_name] = method_func(company_data, market_data)
        
        # Calcular promedio ponderado
        if method == 'weighted_average':
            weights = {
                'dcf': 0.4,
                'comparable': 0.3,
                'precedent': 0.2,
                'asset_based': 0.1
            }
            
            weighted_valuation = 0
            total_weight = 0
            
            for method_name, valuation in valuations.items():
                if valuation > 0:
                    weight = weights.get(method_name, 0)
                    weighted_valuation += valuation * weight
                    total_weight += weight
            
            if total_weight > 0:
                valuations['weighted_average'] = weighted_valuation / total_weight
        
        return valuations

class RiskAnalyzer:
    """Analizador de riesgo avanzado"""
    
    def __init__(self):
        self.risk_factors = {
            'financial': ['revenue_concentration', 'cash_burn', 'debt_levels'],
            'operational': ['key_personnel', 'technology', 'market_position'],
            'regulatory': ['compliance', 'licenses', 'regulatory_changes'],
            'market': ['competition', 'market_size', 'customer_adoption']
        }
    
    def analyze_financial_risk(self, company_data: CompanyData) -> Dict[str, Any]:
        """Analiza riesgo financiero"""
        risk_score = 0
        risk_factors = {}
        
        # Análisis de concentración de revenue
        # (Simplificado - en la práctica requeriría datos detallados)
        revenue_concentration_risk = 0.3  # 30% de riesgo
        risk_factors['revenue_concentration'] = {
            'score': revenue_concentration_risk,
            'description': 'Riesgo de concentración de revenue en pocos clientes'
        }
        risk_score += revenue_concentration_risk * 0.3
        
        # Análisis de burn rate
        # (Simplificado - asumir burn rate del 20% del revenue)
        burn_rate = company_data.revenue * 0.20
        runway_months = (company_data.revenue * 0.5) / burn_rate  # Asumir 50% cash
        
        if runway_months < 12:
            burn_risk = 0.8
        elif runway_months < 18:
            burn_risk = 0.5
        else:
            burn_risk = 0.2
        
        risk_factors['cash_burn'] = {
            'score': burn_risk,
            'description': f'Runway de {runway_months:.1f} meses',
            'runway_months': runway_months
        }
        risk_score += burn_risk * 0.4
        
        # Análisis de niveles de deuda
        debt_risk = 0.1  # Asumir bajo nivel de deuda
        risk_factors['debt_levels'] = {
            'score': debt_risk,
            'description': 'Niveles de deuda bajos'
        }
        risk_score += debt_risk * 0.3
        
        return {
            'overall_score': min(1.0, risk_score),
            'risk_level': self._get_risk_level(risk_score),
            'factors': risk_factors
        }
    
    def analyze_operational_risk(self, company_data: CompanyData) -> Dict[str, Any]:
        """Analiza riesgo operacional"""
        risk_score = 0
        risk_factors = {}
        
        # Análisis de personal clave
        key_personnel_risk = 0.4  # Riesgo medio
        risk_factors['key_personnel'] = {
            'score': key_personnel_risk,
            'description': 'Dependencia de personal clave'
        }
        risk_score += key_personnel_risk * 0.4
        
        # Análisis de tecnología
        technology_risk = 0.2  # Riesgo bajo
        risk_factors['technology'] = {
            'score': technology_risk,
            'description': 'Tecnología estable y escalable'
        }
        risk_score += technology_risk * 0.3
        
        # Análisis de posición de mercado
        market_position_risk = 0.3  # Riesgo medio
        risk_factors['market_position'] = {
            'score': market_position_risk,
            'description': 'Posición de mercado estable'
        }
        risk_score += market_position_risk * 0.3
        
        return {
            'overall_score': min(1.0, risk_score),
            'risk_level': self._get_risk_level(risk_score),
            'factors': risk_factors
        }
    
    def analyze_regulatory_risk(self, company_data: CompanyData, 
                              market_data: MarketData) -> Dict[str, Any]:
        """Analiza riesgo regulatorio"""
        risk_score = 0
        risk_factors = {}
        
        # Análisis de cumplimiento
        compliance_risk = 0.2  # Riesgo bajo
        risk_factors['compliance'] = {
            'score': compliance_risk,
            'description': 'Cumplimiento regulatorio adecuado'
        }
        risk_score += compliance_risk * 0.4
        
        # Análisis de licencias
        licenses_risk = 0.3  # Riesgo medio
        risk_factors['licenses'] = {
            'score': licenses_risk,
            'description': 'Licencias requeridas obtenidas'
        }
        risk_score += licenses_risk * 0.3
        
        # Análisis de cambios regulatorios
        regulatory_changes_risk = 0.4  # Riesgo medio-alto
        risk_factors['regulatory_changes'] = {
            'score': regulatory_changes_risk,
            'description': 'Riesgo de cambios regulatorios'
        }
        risk_score += regulatory_changes_risk * 0.3
        
        return {
            'overall_score': min(1.0, risk_score),
            'risk_level': self._get_risk_level(risk_score),
            'factors': risk_factors
        }
    
    def analyze_market_risk(self, company_data: CompanyData, 
                          market_data: MarketData) -> Dict[str, Any]:
        """Analiza riesgo de mercado"""
        risk_score = 0
        risk_factors = {}
        
        # Análisis de competencia
        competition_risk = 0.4  # Riesgo medio
        risk_factors['competition'] = {
            'score': competition_risk,
            'description': 'Competencia moderada en el mercado'
        }
        risk_score += competition_risk * 0.4
        
        # Análisis de tamaño de mercado
        market_size_risk = 0.2  # Riesgo bajo
        risk_factors['market_size'] = {
            'score': market_size_risk,
            'description': 'Mercado de tamaño adecuado'
        }
        risk_score += market_size_risk * 0.3
        
        # Análisis de adopción de clientes
        customer_adoption_risk = 0.3  # Riesgo medio
        risk_factors['customer_adoption'] = {
            'score': customer_adoption_risk,
            'description': 'Adopción de clientes en crecimiento'
        }
        risk_score += customer_adoption_risk * 0.3
        
        return {
            'overall_score': min(1.0, risk_score),
            'risk_level': self._get_risk_level(risk_score),
            'factors': risk_factors
        }
    
    def _get_risk_level(self, score: float) -> str:
        """Convierte score de riesgo a nivel"""
        if score < 0.3:
            return "BAJO"
        elif score < 0.6:
            return "MEDIO"
        else:
            return "ALTO"
    
    def comprehensive_risk_analysis(self, company_data: CompanyData, 
                                  market_data: MarketData) -> Dict[str, Any]:
        """Análisis de riesgo comprehensivo"""
        analysis = {
            'financial': self.analyze_financial_risk(company_data),
            'operational': self.analyze_operational_risk(company_data),
            'regulatory': self.analyze_regulatory_risk(company_data, market_data),
            'market': self.analyze_market_risk(company_data, market_data)
        }
        
        # Calcular score general
        overall_score = np.mean([cat['overall_score'] for cat in analysis.values()])
        analysis['overall'] = {
            'score': overall_score,
            'risk_level': self._get_risk_level(overall_score)
        }
        
        return analysis

class LegalDocumentGenerator:
    """Generador de documentos legales completo"""
    
    def __init__(self):
        self.template_engine = LegalTemplateEngine()
        self.valuation_calculator = ValuationCalculator()
        self.risk_analyzer = RiskAnalyzer()
    
    def generate_complete_package(self, company_data: CompanyData, 
                                investor_data: InvestorData, 
                                market_data: MarketData) -> Dict[str, Any]:
        """Genera paquete completo de documentos legales"""
        
        # Calcular valoración
        projections = {
            'free_cash_flow': [company_data.revenue * 0.1, 
                              company_data.revenue * 0.15, 
                              company_data.revenue * 0.20]
        }
        valuations = self.valuation_calculator.calculate_valuation(
            company_data, market_data, projections=projections
        )
        
        # Análisis de riesgo
        risk_analysis = self.risk_analyzer.comprehensive_risk_analysis(
            company_data, market_data
        )
        
        # Generar documentos
        documents = self.template_engine.generate_all_documents(
            company_data, investor_data, market_data
        )
        
        # Crear paquete completo
        package = {
            'metadata': {
                'generation_date': datetime.now().isoformat(),
                'transaction_id': f"TXN_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'version': '2.0'
            },
            'company_data': asdict(company_data),
            'investor_data': asdict(investor_data),
            'market_data': asdict(market_data),
            'valuations': valuations,
            'risk_analysis': risk_analysis,
            'documents': documents
        }
        
        return package
    
    def save_package(self, package: Dict[str, Any], output_dir: str = "output"):
        """Guarda el paquete completo"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Guardar metadata
        metadata_file = output_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(package['metadata'], f, indent=2)
        
        # Guardar datos
        data_file = output_path / "data.json"
        with open(data_file, 'w') as f:
            json.dump({
                'company_data': package['company_data'],
                'investor_data': package['investor_data'],
                'market_data': package['market_data']
            }, f, indent=2)
        
        # Guardar valoraciones
        valuations_file = output_path / "valuations.json"
        with open(valuations_file, 'w') as f:
            json.dump(package['valuations'], f, indent=2)
        
        # Guardar análisis de riesgo
        risk_file = output_path / "risk_analysis.json"
        with open(risk_file, 'w') as f:
            json.dump(package['risk_analysis'], f, indent=2)
        
        # Guardar documentos
        documents_dir = output_path / "documents"
        documents_dir.mkdir(exist_ok=True)
        
        for doc_name, doc_content in package['documents'].items():
            doc_file = documents_dir / f"{doc_name}.md"
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(doc_content)
        
        logger.info(f"Paquete guardado en: {output_path}")
        return output_path

def main():
    """Función principal de demostración"""
    print("🚀 HERRAMIENTAS DE AUTOMATIZACIÓN LEGAL AVANZADAS")
    print("=" * 60)
    
    # Datos de ejemplo
    company_data = CompanyData(
        name="TechStartup Inc.",
        jurisdiction="Delaware",
        incorporation_date="2022-01-15",
        business_type="SaaS",
        industry="Technology",
        stage="Series A",
        revenue=5000000.0,
        growth_rate=0.75,
        employees=50,
        valuation=0.0,  # Se calculará
        existing_investors=["Angel Investor 1", "Angel Investor 2"],
        legal_structure="Corporation"
    )
    
    investor_data = InvestorData(
        name="Venture Capital Fund",
        type="VC",
        stage_focus="Series A",
        check_size=15000000.0,
        portfolio_size=25,
        investment_criteria={
            "min_revenue": 1000000,
            "min_growth_rate": 0.50,
            "max_employees": 100
        },
        preferred_terms={
            "liquidation_preference": 1.0,
            "dividend_rate": 0.08,
            "board_seats": 2
        },
        risk_tolerance="Medium"
    )
    
    market_data = MarketData(
        market_size=50000000000.0,
        growth_rate=0.15,
        competition_level="High",
        regulatory_environment="Moderate",
        economic_conditions="Favorable",
        comparable_transactions=[
            {
                "company": "Similar Company 1",
                "industry": "Technology",
                "stage": "Series A",
                "revenue": 4000000,
                "valuation": 40000000
            },
            {
                "company": "Similar Company 2",
                "industry": "Technology",
                "stage": "Series A",
                "revenue": 6000000,
                "valuation": 60000000
            }
        ],
        market_multiples={
            "price_to_sales": 8.0,
            "price_to_ebitda": 25.0
        }
    )
    
    # Crear generador
    generator = LegalDocumentGenerator()
    
    # Generar paquete completo
    print("📋 Generando paquete completo de documentos legales...")
    package = generator.generate_complete_package(company_data, investor_data, market_data)
    
    # Guardar paquete
    print("💾 Guardando paquete...")
    output_path = generator.save_package(package)
    
    # Mostrar resumen
    print("\n🎉 PAQUETE GENERADO EXITOSAMENTE")
    print(f"📁 Ubicación: {output_path}")
    print(f"📊 Valoración promedio: ${package['valuations'].get('weighted_average', 0):,.0f}")
    print(f"⚠️ Nivel de riesgo: {package['risk_analysis']['overall']['risk_level']}")
    print(f"📄 Documentos generados: {len(package['documents'])}")
    
    print("\n📋 ARCHIVOS GENERADOS:")
    for file_path in output_path.rglob("*"):
        if file_path.is_file():
            print(f"   - {file_path.relative_to(output_path)}")

if __name__ == "__main__":
    main()







