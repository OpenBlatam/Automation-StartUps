from datetime import datetime, timedelta
from app import db
from models import Product, InventoryRecord, SalesRecord
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import json
import os
import uuid
from enum import Enum

class RiskLevel(Enum):
    """Nivel de riesgo"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskCategory(Enum):
    """Categoría de riesgo"""
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    COMPLIANCE = "compliance"
    REPUTATIONAL = "reputational"
    STRATEGIC = "strategic"
    TECHNOLOGICAL = "technological"
    ENVIRONMENTAL = "environmental"
    SUPPLY_CHAIN = "supply_chain"

class ComplianceStatus(Enum):
    """Estado de cumplimiento"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    NOT_APPLICABLE = "not_applicable"

class RiskMitigationStatus(Enum):
    """Estado de mitigación de riesgo"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

@dataclass
class RiskAssessment:
    """Evaluación de riesgo"""
    id: str
    risk_name: str
    description: str
    category: RiskCategory
    risk_level: RiskLevel
    probability: float  # 0-1
    impact: float  # 0-1
    risk_score: float  # probability * impact
    affected_areas: List[str]
    identified_date: datetime
    last_reviewed: datetime
    next_review: datetime
    owner: str
    status: str  # 'active', 'mitigated', 'closed'
    mitigation_actions: List[str] = None

@dataclass
class ComplianceRequirement:
    """Requisito de cumplimiento"""
    id: str
    name: str
    description: str
    regulation: str  # ISO, FDA, OSHA, etc.
    category: str  # 'quality', 'safety', 'environmental', 'financial'
    applicable_products: List[int]
    applicable_processes: List[str]
    check_frequency: int  # days
    last_check: Optional[datetime] = None
    next_check: Optional[datetime] = None
    compliance_status: ComplianceStatus = ComplianceStatus.UNDER_REVIEW
    evidence_required: List[str] = None
    penalties: List[str] = None

@dataclass
class RiskMitigationAction:
    """Acción de mitigación de riesgo"""
    id: str
    risk_id: str
    action_name: str
    description: str
    mitigation_status: RiskMitigationStatus
    assigned_to: str
    due_date: datetime
    completion_date: Optional[datetime] = None
    effectiveness: float = 0.0  # 0-1
    cost: float = 0.0
    resources_required: List[str] = None
    dependencies: List[str] = None

@dataclass
class ComplianceAudit:
    """Auditoría de cumplimiento"""
    id: str
    requirement_id: str
    audit_date: datetime
    auditor: str
    audit_type: str  # 'internal', 'external', 'regulatory'
    findings: List[str]
    non_conformities: List[str]
    observations: List[str]
    recommendations: List[str]
    compliance_score: float  # 0-100
    status: str  # 'passed', 'failed', 'conditional', 'pending'
    corrective_actions: List[str] = None
    follow_up_date: Optional[datetime] = None

class RiskComplianceService:
    """Servicio de gestión de riesgos y cumplimiento"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.risk_assessments = {}
        self.compliance_requirements = {}
        self.risk_mitigation_actions = {}
        self.compliance_audits = {}
        
        # Configurar requisitos de cumplimiento por defecto
        self._setup_default_compliance_requirements()
        self._setup_default_risk_assessments()
    
    def _setup_default_compliance_requirements(self):
        """Configura requisitos de cumplimiento por defecto"""
        requirements = [
            ComplianceRequirement(
                id="COMP_001",
                name="ISO 9001:2015 - Sistema de Gestión de Calidad",
                description="Requisitos para sistemas de gestión de calidad",
                regulation="ISO 9001:2015",
                category="quality",
                applicable_products=[1, 2, 3, 4, 5],
                applicable_processes=["manufacturing", "storage", "distribution"],
                check_frequency=365,
                evidence_required=["quality_manual", "procedures", "records", "training_certificates"],
                penalties=["certification_loss", "customer_penalties", "regulatory_fines"]
            ),
            ComplianceRequirement(
                id="COMP_002",
                name="FDA 21 CFR Part 11 - Registros Electrónicos",
                description="Requisitos para registros electrónicos y firmas electrónicas",
                regulation="FDA 21 CFR Part 11",
                category="quality",
                applicable_products=[1, 2, 3],
                applicable_processes=["manufacturing", "quality_control"],
                check_frequency=180,
                evidence_required=["electronic_records", "audit_trails", "access_controls"],
                penalties=["regulatory_action", "product_recall", "facility_shutdown"]
            ),
            ComplianceRequirement(
                id="COMP_003",
                name="OSHA 1910 - Seguridad Ocupacional",
                description="Estándares de seguridad y salud ocupacional",
                regulation="OSHA 1910",
                category="safety",
                applicable_products=[1, 2, 3, 4, 5],
                applicable_processes=["manufacturing", "warehousing", "maintenance"],
                check_frequency=90,
                evidence_required=["safety_procedures", "training_records", "incident_reports"],
                penalties=["fines", "workplace_shutdown", "criminal_charges"]
            ),
            ComplianceRequirement(
                id="COMP_004",
                name="ISO 14001 - Gestión Ambiental",
                description="Sistema de gestión ambiental",
                regulation="ISO 14001:2015",
                category="environmental",
                applicable_products=[1, 2, 3, 4, 5],
                applicable_processes=["manufacturing", "waste_management", "energy_use"],
                check_frequency=365,
                evidence_required=["environmental_policy", "impact_assessments", "monitoring_data"],
                penalties=["environmental_fines", "permit_revocation", "public_relations_damage"]
            ),
            ComplianceRequirement(
                id="COMP_005",
                name="SOX 404 - Control Interno Financiero",
                description="Control interno sobre reportes financieros",
                regulation="Sarbanes-Oxley Act",
                category="financial",
                applicable_products=[1, 2, 3, 4, 5],
                applicable_processes=["financial_reporting", "inventory_valuation", "cost_accounting"],
                check_frequency=365,
                evidence_required=["control_documentation", "testing_results", "remediation_plans"],
                penalties=["sec_fines", "delisting", "criminal_charges"]
            )
        ]
        
        for req in requirements:
            self.compliance_requirements[req.id] = req
    
    def _setup_default_risk_assessments(self):
        """Configura evaluaciones de riesgo por defecto"""
        risks = [
            RiskAssessment(
                id="RISK_001",
                risk_name="Interrupción de Cadena de Suministro",
                description="Riesgo de interrupción en la cadena de suministro debido a problemas de proveedores",
                category=RiskCategory.SUPPLY_CHAIN,
                risk_level=RiskLevel.HIGH,
                probability=0.7,
                impact=0.8,
                risk_score=0.56,
                affected_areas=["procurement", "production", "customer_service"],
                identified_date=datetime.utcnow() - timedelta(days=30),
                last_reviewed=datetime.utcnow() - timedelta(days=7),
                next_review=datetime.utcnow() + timedelta(days=30),
                owner="Supply Chain Manager",
                status="active",
                mitigation_actions=["diversify_suppliers", "increase_safety_stock", "develop_alternatives"]
            ),
            RiskAssessment(
                id="RISK_002",
                risk_name="Fluctuaciones de Precios de Materias Primas",
                description="Riesgo de fluctuaciones significativas en precios de materias primas",
                category=RiskCategory.FINANCIAL,
                risk_level=RiskLevel.MEDIUM,
                probability=0.6,
                impact=0.6,
                risk_score=0.36,
                affected_areas=["cost_management", "pricing", "profitability"],
                identified_date=datetime.utcnow() - timedelta(days=45),
                last_reviewed=datetime.utcnow() - timedelta(days=14),
                next_review=datetime.utcnow() + timedelta(days=45),
                owner="Finance Manager",
                status="active",
                mitigation_actions=["hedging_contracts", "long_term_agreements", "cost_monitoring"]
            ),
            RiskAssessment(
                id="RISK_003",
                risk_name="Incumplimiento Regulatorio",
                description="Riesgo de incumplimiento con regulaciones aplicables",
                category=RiskCategory.COMPLIANCE,
                risk_level=RiskLevel.HIGH,
                probability=0.4,
                impact=0.9,
                risk_score=0.36,
                affected_areas=["quality", "safety", "environmental", "financial"],
                identified_date=datetime.utcnow() - timedelta(days=60),
                last_reviewed=datetime.utcnow() - timedelta(days=21),
                next_review=datetime.utcnow() + timedelta(days=60),
                owner="Compliance Officer",
                status="active",
                mitigation_actions=["regular_audits", "training_programs", "monitoring_systems"]
            ),
            RiskAssessment(
                id="RISK_004",
                risk_name="Ciberataques y Brechas de Seguridad",
                description="Riesgo de ciberataques y brechas de seguridad de datos",
                category=RiskCategory.TECHNOLOGICAL,
                risk_level=RiskLevel.CRITICAL,
                probability=0.3,
                impact=0.95,
                risk_score=0.285,
                affected_areas=["it_systems", "data_privacy", "operations"],
                identified_date=datetime.utcnow() - timedelta(days=15),
                last_reviewed=datetime.utcnow() - timedelta(days=3),
                next_review=datetime.utcnow() + timedelta(days=15),
                owner="IT Security Manager",
                status="active",
                mitigation_actions=["security_updates", "employee_training", "incident_response_plan"]
            ),
            RiskAssessment(
                id="RISK_005",
                risk_name="Daño a la Reputación",
                description="Riesgo de daño a la reputación de la empresa",
                category=RiskCategory.REPUTATIONAL,
                risk_level=RiskLevel.MEDIUM,
                probability=0.5,
                impact=0.7,
                risk_score=0.35,
                affected_areas=["brand_image", "customer_trust", "market_position"],
                identified_date=datetime.utcnow() - timedelta(days=90),
                last_reviewed=datetime.utcnow() - timedelta(days=30),
                next_review=datetime.utcnow() + timedelta(days=90),
                owner="Marketing Manager",
                status="active",
                mitigation_actions=["crisis_management_plan", "stakeholder_communication", "quality_improvements"]
            )
        ]
        
        for risk in risks:
            self.risk_assessments[risk.id] = risk
    
    def create_risk_assessment(self, risk_name: str, description: str, category: RiskCategory,
                             probability: float, impact: float, affected_areas: List[str],
                             owner: str) -> Dict:
        """Crea evaluación de riesgo"""
        try:
            risk_id = f"RISK_{uuid.uuid4().hex[:8].upper()}"
            
            # Calcular puntuación de riesgo
            risk_score = probability * impact
            
            # Determinar nivel de riesgo
            if risk_score >= 0.8:
                risk_level = RiskLevel.CRITICAL
            elif risk_score >= 0.6:
                risk_level = RiskLevel.HIGH
            elif risk_score >= 0.4:
                risk_level = RiskLevel.MEDIUM
            elif risk_score >= 0.2:
                risk_level = RiskLevel.LOW
            else:
                risk_level = RiskLevel.VERY_LOW
            
            risk_assessment = RiskAssessment(
                id=risk_id,
                risk_name=risk_name,
                description=description,
                category=category,
                risk_level=risk_level,
                probability=probability,
                impact=impact,
                risk_score=risk_score,
                affected_areas=affected_areas,
                identified_date=datetime.utcnow(),
                last_reviewed=datetime.utcnow(),
                next_review=datetime.utcnow() + timedelta(days=90),
                owner=owner,
                status="active"
            )
            
            self.risk_assessments[risk_id] = risk_assessment
            
            return {
                'success': True,
                'risk_assessment': {
                    'id': risk_assessment.id,
                    'risk_name': risk_assessment.risk_name,
                    'description': risk_assessment.description,
                    'category': risk_assessment.category.value,
                    'risk_level': risk_assessment.risk_level.value,
                    'probability': risk_assessment.probability,
                    'impact': risk_assessment.impact,
                    'risk_score': risk_assessment.risk_score,
                    'affected_areas': risk_assessment.affected_areas,
                    'identified_date': risk_assessment.identified_date.isoformat(),
                    'owner': risk_assessment.owner,
                    'status': risk_assessment.status
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error creando evaluación de riesgo: {str(e)}')
            return {'error': str(e)}
    
    def create_mitigation_action(self, risk_id: str, action_name: str, description: str,
                               assigned_to: str, due_date: datetime, cost: float = 0.0,
                               resources_required: List[str] = None) -> Dict:
        """Crea acción de mitigación de riesgo"""
        try:
            if risk_id not in self.risk_assessments:
                return {'error': 'Evaluación de riesgo no encontrada'}
            
            action_id = f"MIT_{uuid.uuid4().hex[:8].upper()}"
            
            mitigation_action = RiskMitigationAction(
                id=action_id,
                risk_id=risk_id,
                action_name=action_name,
                description=description,
                mitigation_status=RiskMitigationStatus.NOT_STARTED,
                assigned_to=assigned_to,
                due_date=due_date,
                cost=cost,
                resources_required=resources_required or []
            )
            
            self.risk_mitigation_actions[action_id] = mitigation_action
            
            return {
                'success': True,
                'mitigation_action': {
                    'id': mitigation_action.id,
                    'risk_id': mitigation_action.risk_id,
                    'action_name': mitigation_action.action_name,
                    'description': mitigation_action.description,
                    'mitigation_status': mitigation_action.mitigation_status.value,
                    'assigned_to': mitigation_action.assigned_to,
                    'due_date': mitigation_action.due_date.isoformat(),
                    'cost': mitigation_action.cost,
                    'resources_required': mitigation_action.resources_required
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error creando acción de mitigación: {str(e)}')
            return {'error': str(e)}
    
    def create_compliance_audit(self, requirement_id: str, auditor: str, audit_type: str,
                              findings: List[str], non_conformities: List[str],
                              observations: List[str], recommendations: List[str]) -> Dict:
        """Crea auditoría de cumplimiento"""
        try:
            if requirement_id not in self.compliance_requirements:
                return {'error': 'Requisito de cumplimiento no encontrado'}
            
            audit_id = f"AUDIT_{uuid.uuid4().hex[:8].upper()}"
            
            # Calcular puntuación de cumplimiento
            total_issues = len(findings) + len(non_conformities)
            if total_issues == 0:
                compliance_score = 100.0
            elif len(non_conformities) == 0:
                compliance_score = 90.0 - (len(findings) * 5)
            else:
                compliance_score = max(0, 70.0 - (len(non_conformities) * 15) - (len(findings) * 5))
            
            # Determinar estado
            if compliance_score >= 90:
                status = "passed"
            elif compliance_score >= 70:
                status = "conditional"
            else:
                status = "failed"
            
            audit = ComplianceAudit(
                id=audit_id,
                requirement_id=requirement_id,
                audit_date=datetime.utcnow(),
                auditor=auditor,
                audit_type=audit_type,
                findings=findings,
                non_conformities=non_conformities,
                observations=observations,
                recommendations=recommendations,
                compliance_score=compliance_score,
                status=status
            )
            
            self.compliance_audits[audit_id] = audit
            
            return {
                'success': True,
                'audit': {
                    'id': audit.id,
                    'requirement_id': audit.requirement_id,
                    'audit_date': audit.audit_date.isoformat(),
                    'auditor': audit.auditor,
                    'audit_type': audit.audit_type,
                    'findings': audit.findings,
                    'non_conformities': audit.non_conformities,
                    'observations': audit.observations,
                    'recommendations': audit.recommendations,
                    'compliance_score': audit.compliance_score,
                    'status': audit.status
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error creando auditoría de cumplimiento: {str(e)}')
            return {'error': str(e)}
    
    def get_risk_dashboard(self) -> Dict:
        """Obtiene datos para dashboard de riesgos"""
        try:
            # Estadísticas de riesgos
            total_risks = len(self.risk_assessments)
            active_risks = len([r for r in self.risk_assessments.values() if r.status == "active"])
            
            # Distribución por nivel de riesgo
            risk_distribution = {}
            for risk in self.risk_assessments.values():
                level = risk.risk_level.value
                risk_distribution[level] = risk_distribution.get(level, 0) + 1
            
            # Distribución por categoría
            category_distribution = {}
            for risk in self.risk_assessments.values():
                category = risk.category.value
                category_distribution[category] = category_distribution.get(category, 0) + 1
            
            # Riesgos críticos y altos
            critical_high_risks = [
                risk for risk in self.risk_assessments.values()
                if risk.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH] and risk.status == "active"
            ]
            
            # Estadísticas de mitigación
            total_mitigations = len(self.risk_mitigation_actions)
            completed_mitigations = len([
                m for m in self.risk_mitigation_actions.values()
                if m.mitigation_status == RiskMitigationStatus.COMPLETED
            ])
            
            return {
                'success': True,
                'dashboard': {
                    'risks': {
                        'total': total_risks,
                        'active': active_risks,
                        'distribution_by_level': risk_distribution,
                        'distribution_by_category': category_distribution,
                        'critical_high_count': len(critical_high_risks)
                    },
                    'mitigations': {
                        'total': total_mitigations,
                        'completed': completed_mitigations,
                        'completion_rate': (completed_mitigations / total_mitigations * 100) if total_mitigations > 0 else 0
                    },
                    'critical_high_risks': [
                        {
                            'id': risk.id,
                            'risk_name': risk.risk_name,
                            'risk_level': risk.risk_level.value,
                            'risk_score': risk.risk_score,
                            'owner': risk.owner,
                            'next_review': risk.next_review.isoformat()
                        } for risk in critical_high_risks
                    ]
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo dashboard de riesgos: {str(e)}')
            return {'error': str(e)}
    
    def get_compliance_dashboard(self) -> Dict:
        """Obtiene datos para dashboard de cumplimiento"""
        try:
            # Estadísticas de cumplimiento
            total_requirements = len(self.compliance_requirements)
            compliant_requirements = len([
                r for r in self.compliance_requirements.values()
                if r.compliance_status == ComplianceStatus.COMPLIANT
            ])
            
            # Requisitos que necesitan revisión
            needs_review = []
            for req in self.compliance_requirements.values():
                if req.next_check and req.next_check <= datetime.utcnow():
                    needs_review.append(req)
            
            # Estadísticas de auditorías
            total_audits = len(self.compliance_audits)
            recent_audits = len([
                a for a in self.compliance_audits.values()
                if a.audit_date > datetime.utcnow() - timedelta(days=30)
            ])
            
            # Distribución por estado de cumplimiento
            compliance_distribution = {}
            for req in self.compliance_requirements.values():
                status = req.compliance_status.value
                compliance_distribution[status] = compliance_distribution.get(status, 0) + 1
            
            # Distribución por categoría
            category_distribution = {}
            for req in self.compliance_requirements.values():
                category = req.category
                category_distribution[category] = category_distribution.get(category, 0) + 1
            
            return {
                'success': True,
                'dashboard': {
                    'requirements': {
                        'total': total_requirements,
                        'compliant': compliant_requirements,
                        'compliance_rate': (compliant_requirements / total_requirements * 100) if total_requirements > 0 else 0,
                        'needs_review': len(needs_review),
                        'distribution_by_status': compliance_distribution,
                        'distribution_by_category': category_distribution
                    },
                    'audits': {
                        'total': total_audits,
                        'recent_30_days': recent_audits
                    },
                    'requirements_needing_review': [
                        {
                            'id': req.id,
                            'name': req.name,
                            'regulation': req.regulation,
                            'category': req.category,
                            'next_check': req.next_check.isoformat() if req.next_check else None,
                            'compliance_status': req.compliance_status.value
                        } for req in needs_review
                    ]
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo dashboard de cumplimiento: {str(e)}')
            return {'error': str(e)}
    
    def generate_risk_report(self, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """Genera reporte de riesgos"""
        try:
            if start_date is None:
                start_date = datetime.utcnow() - timedelta(days=90)
            if end_date is None:
                end_date = datetime.utcnow()
            
            # Filtrar riesgos por período
            filtered_risks = [
                risk for risk in self.risk_assessments.values()
                if start_date <= risk.identified_date <= end_date
            ]
            
            # Calcular métricas
            total_risks = len(filtered_risks)
            avg_risk_score = sum(risk.risk_score for risk in filtered_risks) / total_risks if total_risks > 0 else 0
            
            # Top riesgos por puntuación
            top_risks = sorted(filtered_risks, key=lambda r: r.risk_score, reverse=True)[:5]
            
            # Distribución por categoría
            category_distribution = {}
            for risk in filtered_risks:
                category = risk.category.value
                category_distribution[category] = category_distribution.get(category, 0) + 1
            
            # Distribución por nivel
            level_distribution = {}
            for risk in filtered_risks:
                level = risk.risk_level.value
                level_distribution[level] = level_distribution.get(level, 0) + 1
            
            return {
                'success': True,
                'report': {
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    },
                    'summary': {
                        'total_risks': total_risks,
                        'average_risk_score': avg_risk_score,
                        'critical_risks': len([r for r in filtered_risks if r.risk_level == RiskLevel.CRITICAL]),
                        'high_risks': len([r for r in filtered_risks if r.risk_level == RiskLevel.HIGH])
                    },
                    'top_risks': [
                        {
                            'id': risk.id,
                            'risk_name': risk.risk_name,
                            'risk_score': risk.risk_score,
                            'risk_level': risk.risk_level.value,
                            'category': risk.category.value,
                            'owner': risk.owner
                        } for risk in top_risks
                    ],
                    'category_distribution': category_distribution,
                    'level_distribution': level_distribution,
                    'generated_at': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error generando reporte de riesgos: {str(e)}')
            return {'error': str(e)}

# Instancia global del servicio de gestión de riesgos y cumplimiento
risk_compliance_service = RiskComplianceService()



