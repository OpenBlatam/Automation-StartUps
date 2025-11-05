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

class QualityStatus(Enum):
    """Estado de calidad"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    REJECTED = "rejected"

class TraceabilityEvent(Enum):
    """Eventos de trazabilidad"""
    MANUFACTURED = "manufactured"
    RECEIVED = "received"
    STORED = "stored"
    MOVED = "moved"
    QUALITY_CHECK = "quality_check"
    SOLD = "sold"
    RETURNED = "returned"
    DISPOSED = "disposed"

class ComplianceStatus(Enum):
    """Estado de cumplimiento"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    UNDER_INVESTIGATION = "under_investigation"

@dataclass
class QualityCheck:
    """Verificación de calidad"""
    id: str
    product_id: int
    batch_number: str
    check_date: datetime
    inspector_id: str
    quality_status: QualityStatus
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    weight: Optional[float] = None
    dimensions: Optional[Dict] = None
    defects: List[str] = None
    notes: str = ""
    compliance_status: ComplianceStatus = ComplianceStatus.COMPLIANT

@dataclass
class TraceabilityRecord:
    """Registro de trazabilidad"""
    id: str
    product_id: int
    batch_number: str
    event_type: TraceabilityEvent
    timestamp: datetime
    location: str
    actor_id: str
    actor_type: str  # 'person', 'system', 'machine'
    metadata: Dict
    previous_location: Optional[str] = None
    next_location: Optional[str] = None

@dataclass
class ComplianceRequirement:
    """Requisito de cumplimiento"""
    id: str
    name: str
    description: str
    category: str  # 'safety', 'environmental', 'quality', 'regulatory'
    applicable_products: List[int]
    check_frequency: int  # days
    last_check: Optional[datetime] = None
    next_check: Optional[datetime] = None
    is_active: bool = True

@dataclass
class SupplierAudit:
    """Auditoría de proveedor"""
    id: str
    supplier_id: str
    audit_date: datetime
    auditor_id: str
    audit_type: str  # 'initial', 'periodic', 'follow_up', 'special'
    score: float  # 0-100
    findings: List[str]
    recommendations: List[str]
    status: str  # 'passed', 'failed', 'conditional', 'pending'
    next_audit_date: Optional[datetime] = None

class QualityTraceabilityService:
    """Servicio de calidad y trazabilidad"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.quality_checks = {}
        self.traceability_records = {}
        self.compliance_requirements = {}
        self.supplier_audits = {}
        
        # Configurar requisitos de cumplimiento por defecto
        self._setup_default_compliance_requirements()
    
    def _setup_default_compliance_requirements(self):
        """Configura requisitos de cumplimiento por defecto"""
        requirements = [
            ComplianceRequirement(
                id="COMP_001",
                name="Verificación de Temperatura",
                description="Verificar que los productos se mantengan dentro del rango de temperatura especificado",
                category="quality",
                applicable_products=[1, 2, 3, 4, 5],
                check_frequency=1,  # Diario
                is_active=True
            ),
            ComplianceRequirement(
                id="COMP_002",
                name="Inspección Visual",
                description="Inspección visual para detectar defectos físicos",
                category="quality",
                applicable_products=[1, 2, 3, 4, 5],
                check_frequency=7,  # Semanal
                is_active=True
            ),
            ComplianceRequirement(
                id="COMP_003",
                name="Verificación de Peso",
                description="Verificar que el peso esté dentro de las especificaciones",
                category="quality",
                applicable_products=[1, 2, 3, 4, 5],
                check_frequency=3,  # Cada 3 días
                is_active=True
            ),
            ComplianceRequirement(
                id="COMP_004",
                name="Cumplimiento Ambiental",
                description="Verificar cumplimiento con regulaciones ambientales",
                category="environmental",
                applicable_products=[1, 2, 3, 4, 5],
                check_frequency=30,  # Mensual
                is_active=True
            ),
            ComplianceRequirement(
                id="COMP_005",
                name="Seguridad del Producto",
                description="Verificar que el producto cumple con estándares de seguridad",
                category="safety",
                applicable_products=[1, 2, 3, 4, 5],
                check_frequency=14,  # Quincenal
                is_active=True
            )
        ]
        
        for req in requirements:
            self.compliance_requirements[req.id] = req
    
    def create_quality_check(self, product_id: int, batch_number: str, 
                           inspector_id: str, quality_status: QualityStatus,
                           temperature: float = None, humidity: float = None,
                           weight: float = None, dimensions: Dict = None,
                           defects: List[str] = None, notes: str = "") -> Dict:
        """Crea verificación de calidad"""
        try:
            check_id = f"QC_{uuid.uuid4().hex[:8].upper()}"
            
            quality_check = QualityCheck(
                id=check_id,
                product_id=product_id,
                batch_number=batch_number,
                check_date=datetime.utcnow(),
                inspector_id=inspector_id,
                quality_status=quality_status,
                temperature=temperature,
                humidity=humidity,
                weight=weight,
                dimensions=dimensions,
                defects=defects or [],
                notes=notes,
                compliance_status=ComplianceStatus.COMPLIANT if quality_status != QualityStatus.REJECTED else ComplianceStatus.NON_COMPLIANT
            )
            
            self.quality_checks[check_id] = quality_check
            
            # Crear registro de trazabilidad
            self._create_traceability_record(
                product_id=product_id,
                batch_number=batch_number,
                event_type=TraceabilityEvent.QUALITY_CHECK,
                location="Quality Control",
                actor_id=inspector_id,
                actor_type="person",
                metadata={
                    'quality_status': quality_status.value,
                    'check_id': check_id,
                    'temperature': temperature,
                    'humidity': humidity,
                    'weight': weight,
                    'defects': defects or []
                }
            )
            
            return {
                'success': True,
                'quality_check': {
                    'id': quality_check.id,
                    'product_id': quality_check.product_id,
                    'batch_number': quality_check.batch_number,
                    'check_date': quality_check.check_date.isoformat(),
                    'inspector_id': quality_check.inspector_id,
                    'quality_status': quality_check.quality_status.value,
                    'temperature': quality_check.temperature,
                    'humidity': quality_check.humidity,
                    'weight': quality_check.weight,
                    'dimensions': quality_check.dimensions,
                    'defects': quality_check.defects,
                    'notes': quality_check.notes,
                    'compliance_status': quality_check.compliance_status.value
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error creando verificación de calidad: {str(e)}')
            return {'error': str(e)}
    
    def _create_traceability_record(self, product_id: int, batch_number: str,
                                  event_type: TraceabilityEvent, location: str,
                                  actor_id: str, actor_type: str, metadata: Dict,
                                  previous_location: str = None, next_location: str = None):
        """Crea registro de trazabilidad"""
        try:
            record_id = f"TR_{uuid.uuid4().hex[:8].upper()}"
            
            traceability_record = TraceabilityRecord(
                id=record_id,
                product_id=product_id,
                batch_number=batch_number,
                event_type=event_type,
                timestamp=datetime.utcnow(),
                location=location,
                actor_id=actor_id,
                actor_type=actor_type,
                metadata=metadata,
                previous_location=previous_location,
                next_location=next_location
            )
            
            self.traceability_records[record_id] = traceability_record
            
        except Exception as e:
            self.logger.error(f'Error creando registro de trazabilidad: {str(e)}')
    
    def get_product_traceability(self, product_id: int, batch_number: str = None) -> Dict:
        """Obtiene trazabilidad de un producto"""
        try:
            records = []
            
            for record_id, record in self.traceability_records.items():
                if record.product_id == product_id:
                    if batch_number is None or record.batch_number == batch_number:
                        records.append({
                            'id': record.id,
                            'product_id': record.product_id,
                            'batch_number': record.batch_number,
                            'event_type': record.event_type.value,
                            'timestamp': record.timestamp.isoformat(),
                            'location': record.location,
                            'actor_id': record.actor_id,
                            'actor_type': record.actor_type,
                            'metadata': record.metadata,
                            'previous_location': record.previous_location,
                            'next_location': record.next_location
                        })
            
            # Ordenar por timestamp
            records.sort(key=lambda x: x['timestamp'])
            
            return {
                'success': True,
                'product_id': product_id,
                'batch_number': batch_number,
                'traceability_records': records,
                'total_records': len(records)
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo trazabilidad: {str(e)}')
            return {'error': str(e)}
    
    def get_quality_history(self, product_id: int = None, batch_number: str = None) -> Dict:
        """Obtiene historial de calidad"""
        try:
            checks = []
            
            for check_id, check in self.quality_checks.items():
                if product_id is None or check.product_id == product_id:
                    if batch_number is None or check.batch_number == batch_number:
                        checks.append({
                            'id': check.id,
                            'product_id': check.product_id,
                            'batch_number': check.batch_number,
                            'check_date': check.check_date.isoformat(),
                            'inspector_id': check.inspector_id,
                            'quality_status': check.quality_status.value,
                            'temperature': check.temperature,
                            'humidity': check.humidity,
                            'weight': check.weight,
                            'dimensions': check.dimensions,
                            'defects': check.defects,
                            'notes': check.notes,
                            'compliance_status': check.compliance_status.value
                        })
            
            # Ordenar por fecha
            checks.sort(key=lambda x: x['check_date'], reverse=True)
            
            return {
                'success': True,
                'quality_checks': checks,
                'total_checks': len(checks)
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo historial de calidad: {str(e)}')
            return {'error': str(e)}
    
    def create_supplier_audit(self, supplier_id: str, auditor_id: str,
                            audit_type: str, score: float, findings: List[str],
                            recommendations: List[str], status: str) -> Dict:
        """Crea auditoría de proveedor"""
        try:
            audit_id = f"AUDIT_{uuid.uuid4().hex[:8].upper()}"
            
            # Calcular próxima auditoría basada en el tipo
            next_audit_days = {
                'initial': 365,
                'periodic': 180,
                'follow_up': 90,
                'special': 30
            }
            
            next_audit_date = datetime.utcnow() + timedelta(days=next_audit_days.get(audit_type, 180))
            
            audit = SupplierAudit(
                id=audit_id,
                supplier_id=supplier_id,
                audit_date=datetime.utcnow(),
                auditor_id=auditor_id,
                audit_type=audit_type,
                score=score,
                findings=findings,
                recommendations=recommendations,
                status=status,
                next_audit_date=next_audit_date
            )
            
            self.supplier_audits[audit_id] = audit
            
            return {
                'success': True,
                'audit': {
                    'id': audit.id,
                    'supplier_id': audit.supplier_id,
                    'audit_date': audit.audit_date.isoformat(),
                    'auditor_id': audit.auditor_id,
                    'audit_type': audit.audit_type,
                    'score': audit.score,
                    'findings': audit.findings,
                    'recommendations': audit.recommendations,
                    'status': audit.status,
                    'next_audit_date': audit.next_audit_date.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error creando auditoría de proveedor: {str(e)}')
            return {'error': str(e)}
    
    def get_compliance_status(self, product_id: int = None) -> Dict:
        """Obtiene estado de cumplimiento"""
        try:
            compliance_data = []
            
            for req_id, requirement in self.compliance_requirements.items():
                if not requirement.is_active:
                    continue
                
                if product_id is None or product_id in requirement.applicable_products:
                    # Verificar si necesita revisión
                    needs_review = False
                    if requirement.next_check and requirement.next_check <= datetime.utcnow():
                        needs_review = True
                    
                    compliance_data.append({
                        'id': requirement.id,
                        'name': requirement.name,
                        'description': requirement.description,
                        'category': requirement.category,
                        'check_frequency': requirement.check_frequency,
                        'last_check': requirement.last_check.isoformat() if requirement.last_check else None,
                        'next_check': requirement.next_check.isoformat() if requirement.next_check else None,
                        'needs_review': needs_review,
                        'is_active': requirement.is_active
                    })
            
            return {
                'success': True,
                'compliance_requirements': compliance_data,
                'total_requirements': len(compliance_data),
                'pending_reviews': len([req for req in compliance_data if req['needs_review']])
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo estado de cumplimiento: {str(e)}')
            return {'error': str(e)}
    
    def get_quality_dashboard(self) -> Dict:
        """Obtiene datos para dashboard de calidad"""
        try:
            # Estadísticas de verificaciones de calidad
            total_checks = len(self.quality_checks)
            recent_checks = len([
                check for check in self.quality_checks.values()
                if check.check_date > datetime.utcnow() - timedelta(days=7)
            ])
            
            # Distribución por estado de calidad
            quality_distribution = {}
            for check in self.quality_checks.values():
                status = check.quality_status.value
                quality_distribution[status] = quality_distribution.get(status, 0) + 1
            
            # Estadísticas de cumplimiento
            total_requirements = len(self.compliance_requirements)
            active_requirements = len([req for req in self.compliance_requirements.values() if req.is_active])
            pending_reviews = len([
                req for req in self.compliance_requirements.values()
                if req.next_check and req.next_check <= datetime.utcnow()
            ])
            
            # Estadísticas de auditorías
            total_audits = len(self.supplier_audits)
            recent_audits = len([
                audit for audit in self.supplier_audits.values()
                if audit.audit_date > datetime.utcnow() - timedelta(days=30)
            ])
            
            # Calcular puntuación promedio de auditorías
            avg_audit_score = 0
            if total_audits > 0:
                avg_audit_score = sum(audit.score for audit in self.supplier_audits.values()) / total_audits
            
            return {
                'success': True,
                'dashboard': {
                    'quality_checks': {
                        'total': total_checks,
                        'recent_7_days': recent_checks,
                        'distribution': quality_distribution
                    },
                    'compliance': {
                        'total_requirements': total_requirements,
                        'active_requirements': active_requirements,
                        'pending_reviews': pending_reviews
                    },
                    'audits': {
                        'total': total_audits,
                        'recent_30_days': recent_audits,
                        'average_score': avg_audit_score
                    },
                    'traceability': {
                        'total_records': len(self.traceability_records),
                        'recent_records': len([
                            record for record in self.traceability_records.values()
                            if record.timestamp > datetime.utcnow() - timedelta(days=7)
                        ])
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo dashboard de calidad: {str(e)}')
            return {'error': str(e)}
    
    def generate_quality_report(self, product_id: int = None, start_date: datetime = None, 
                              end_date: datetime = None) -> Dict:
        """Genera reporte de calidad"""
        try:
            if start_date is None:
                start_date = datetime.utcnow() - timedelta(days=30)
            if end_date is None:
                end_date = datetime.utcnow()
            
            # Filtrar verificaciones de calidad
            filtered_checks = []
            for check in self.quality_checks.values():
                if product_id is None or check.product_id == product_id:
                    if start_date <= check.check_date <= end_date:
                        filtered_checks.append(check)
            
            # Calcular métricas
            total_checks = len(filtered_checks)
            passed_checks = len([check for check in filtered_checks if check.quality_status != QualityStatus.REJECTED])
            failed_checks = len([check for check in filtered_checks if check.quality_status == QualityStatus.REJECTED])
            
            # Distribución por estado
            quality_distribution = {}
            for check in filtered_checks:
                status = check.quality_status.value
                quality_distribution[status] = quality_distribution.get(status, 0) + 1
            
            # Defectos más comunes
            defect_counts = {}
            for check in filtered_checks:
                for defect in check.defects:
                    defect_counts[defect] = defect_counts.get(defect, 0) + 1
            
            # Top defectos
            top_defects = sorted(defect_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                'success': True,
                'report': {
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    },
                    'product_id': product_id,
                    'summary': {
                        'total_checks': total_checks,
                        'passed_checks': passed_checks,
                        'failed_checks': failed_checks,
                        'pass_rate': (passed_checks / total_checks * 100) if total_checks > 0 else 0
                    },
                    'quality_distribution': quality_distribution,
                    'top_defects': top_defects,
                    'generated_at': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f'Error generando reporte de calidad: {str(e)}')
            return {'error': str(e)}

# Instancia global del servicio de calidad y trazabilidad
quality_traceability_service = QualityTraceabilityService()



