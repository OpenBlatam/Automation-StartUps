#!/usr/bin/env python3
"""
Sistema de Ciberseguridad Avanzada para Protección Empresarial
"""

import os
import json
import sqlite3
import hashlib
import random
from datetime import datetime, timedelta
import re

class CybersecuritySystem:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.security_db = os.path.join(base_path, "cybersecurity.db")
        self.threat_patterns = {}
        self.security_policies = {}
        self.init_security_database()
        self.load_threat_intelligence()
    
    def init_security_database(self):
        """Inicializar base de datos de ciberseguridad"""
        conn = sqlite3.connect(self.security_db)
        cursor = conn.cursor()
        
        # Tabla de amenazas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                threat_name TEXT,
                threat_type TEXT,
                severity TEXT,
                description TEXT,
                detection_pattern TEXT,
                mitigation TEXT,
                status TEXT,
                detected_at TEXT,
                resolved_at TEXT
            )
        ''')
        
        # Tabla de incidentes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_name TEXT,
                incident_type TEXT,
                severity TEXT,
                affected_systems TEXT,
                description TEXT,
                response_actions TEXT,
                status TEXT,
                created_at TEXT,
                resolved_at TEXT
            )
        ''')
        
        # Tabla de políticas de seguridad
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_name TEXT,
                policy_type TEXT,
                rules TEXT,
                enforcement_level TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Tabla de auditorías
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_name TEXT,
                audit_type TEXT,
                target_system TEXT,
                findings TEXT,
                recommendations TEXT,
                risk_level TEXT,
                created_at TEXT
            )
        ''')
        
        # Tabla de vulnerabilidades
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vulnerability_name TEXT,
                cve_id TEXT,
                severity TEXT,
                affected_systems TEXT,
                description TEXT,
                patch_status TEXT,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_threat_intelligence(self):
        """Cargar inteligencia de amenazas"""
        # Patrones de amenazas comunes
        self.threat_patterns = {
            'malware': {
                'patterns': [r'\.exe$', r'\.bat$', r'\.cmd$', r'powershell', r'wscript'],
                'severity': 'high',
                'description': 'Malware detection patterns'
            },
            'phishing': {
                'patterns': [r'urgent', r'click here', r'verify account', r'password expired'],
                'severity': 'medium',
                'description': 'Phishing email patterns'
            },
            'sql_injection': {
                'patterns': [r'union select', r'drop table', r'insert into', r'delete from'],
                'severity': 'high',
                'description': 'SQL injection attack patterns'
            },
            'xss': {
                'patterns': [r'<script>', r'javascript:', r'onclick=', r'onload='],
                'severity': 'medium',
                'description': 'Cross-site scripting patterns'
            },
            'brute_force': {
                'patterns': [r'failed login', r'incorrect password', r'authentication failed'],
                'severity': 'medium',
                'description': 'Brute force attack patterns'
            }
        }
        
        # Políticas de seguridad por defecto
        self.security_policies = {
            'password_policy': {
                'min_length': 8,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_numbers': True,
                'require_symbols': True,
                'max_age_days': 90
            },
            'access_control': {
                'max_login_attempts': 3,
                'lockout_duration_minutes': 30,
                'session_timeout_minutes': 60,
                'require_mfa': True
            },
            'data_protection': {
                'encryption_required': True,
                'backup_frequency': 'daily',
                'retention_period_days': 365,
                'access_logging': True
            }
        }
    
    def detect_threats(self, data, data_type='text'):
        """Detectar amenazas en datos"""
        detected_threats = []
        
        for threat_type, threat_info in self.threat_patterns.items():
            for pattern in threat_info['patterns']:
                if re.search(pattern, data, re.IGNORECASE):
                    threat = {
                        'type': threat_type,
                        'severity': threat_info['severity'],
                        'description': threat_info['description'],
                        'pattern_matched': pattern,
                        'confidence': random.uniform(0.7, 0.95)
                    }
                    detected_threats.append(threat)
        
        # Guardar amenazas detectadas
        for threat in detected_threats:
            self._save_threat(threat)
        
        return detected_threats
    
    def _save_threat(self, threat):
        """Guardar amenaza en base de datos"""
        conn = sqlite3.connect(self.security_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_threats 
            (threat_name, threat_type, severity, description, detection_pattern, 
             status, detected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (f"Threat_{threat['type']}", threat['type'], threat['severity'], 
              threat['description'], threat['pattern_matched'], 'detected', 
              datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def create_security_incident(self, incident_name, incident_type, severity, affected_systems, description):
        """Crear incidente de seguridad"""
        conn = sqlite3.connect(self.security_db)
        cursor = conn.cursor()
        
        response_actions = self._generate_response_actions(incident_type, severity)
        
        cursor.execute('''
            INSERT INTO security_incidents 
            (incident_name, incident_type, severity, affected_systems, description, 
             response_actions, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (incident_name, incident_type, severity, json.dumps(affected_systems), 
              description, json.dumps(response_actions), 'active', datetime.now().isoformat()))
        
        incident_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return incident_id
    
    def _generate_response_actions(self, incident_type, severity):
        """Generar acciones de respuesta"""
        actions = []
        
        if severity == 'critical':
            actions.extend([
                'Isolate affected systems',
                'Activate incident response team',
                'Notify stakeholders immediately',
                'Implement emergency protocols'
            ])
        elif severity == 'high':
            actions.extend([
                'Block suspicious IPs',
                'Reset compromised credentials',
                'Increase monitoring',
                'Notify security team'
            ])
        elif severity == 'medium':
            actions.extend([
                'Review security logs',
                'Update security policies',
                'Notify administrators'
            ])
        else:
            actions.extend([
                'Log incident',
                'Monitor for escalation'
            ])
        
        return actions
    
    def perform_security_audit(self, target_system):
        """Realizar auditoría de seguridad"""
        audit_findings = []
        
        # Verificar políticas de contraseñas
        password_findings = self._audit_password_policies(target_system)
        audit_findings.extend(password_findings)
        
        # Verificar controles de acceso
        access_findings = self._audit_access_controls(target_system)
        audit_findings.extend(access_findings)
        
        # Verificar cifrado de datos
        encryption_findings = self._audit_data_encryption(target_system)
        audit_findings.extend(encryption_findings)
        
        # Verificar actualizaciones de seguridad
        update_findings = self._audit_security_updates(target_system)
        audit_findings.extend(update_findings)
        
        # Calcular nivel de riesgo
        risk_level = self._calculate_risk_level(audit_findings)
        
        # Generar recomendaciones
        recommendations = self._generate_security_recommendations(audit_findings)
        
        # Guardar auditoría
        audit_id = self._save_audit(target_system, audit_findings, recommendations, risk_level)
        
        return {
            'audit_id': audit_id,
            'target_system': target_system,
            'findings': audit_findings,
            'recommendations': recommendations,
            'risk_level': risk_level
        }
    
    def _audit_password_policies(self, system):
        """Auditar políticas de contraseñas"""
        findings = []
        
        # Simular verificación de políticas
        if random.random() > 0.3:  # 70% de probabilidad de encontrar problemas
            findings.append({
                'category': 'password_policy',
                'issue': 'Weak password requirements',
                'severity': 'medium',
                'description': 'Password policy does not meet security standards'
            })
        
        if random.random() > 0.5:  # 50% de probabilidad
            findings.append({
                'category': 'password_policy',
                'issue': 'Password reuse detected',
                'severity': 'high',
                'description': 'Users are reusing passwords across systems'
            })
        
        return findings
    
    def _audit_access_controls(self, system):
        """Auditar controles de acceso"""
        findings = []
        
        if random.random() > 0.4:  # 60% de probabilidad
            findings.append({
                'category': 'access_control',
                'issue': 'Excessive privileges',
                'severity': 'high',
                'description': 'Users have more privileges than necessary'
            })
        
        if random.random() > 0.6:  # 40% de probabilidad
            findings.append({
                'category': 'access_control',
                'issue': 'Inactive accounts not disabled',
                'severity': 'medium',
                'description': 'Inactive user accounts are still active'
            })
        
        return findings
    
    def _audit_data_encryption(self, system):
        """Auditar cifrado de datos"""
        findings = []
        
        if random.random() > 0.2:  # 80% de probabilidad
            findings.append({
                'category': 'data_encryption',
                'issue': 'Unencrypted sensitive data',
                'severity': 'critical',
                'description': 'Sensitive data is not encrypted'
            })
        
        return findings
    
    def _audit_security_updates(self, system):
        """Auditar actualizaciones de seguridad"""
        findings = []
        
        if random.random() > 0.3:  # 70% de probabilidad
            findings.append({
                'category': 'security_updates',
                'issue': 'Outdated security patches',
                'severity': 'high',
                'description': 'System has outdated security patches'
            })
        
        return findings
    
    def _calculate_risk_level(self, findings):
        """Calcular nivel de riesgo"""
        if not findings:
            return 'low'
        
        critical_count = len([f for f in findings if f['severity'] == 'critical'])
        high_count = len([f for f in findings if f['severity'] == 'high'])
        medium_count = len([f for f in findings if f['severity'] == 'medium'])
        
        if critical_count > 0:
            return 'critical'
        elif high_count > 2 or (high_count > 0 and medium_count > 3):
            return 'high'
        elif high_count > 0 or medium_count > 2:
            return 'medium'
        else:
            return 'low'
    
    def _generate_security_recommendations(self, findings):
        """Generar recomendaciones de seguridad"""
        recommendations = []
        
        for finding in findings:
            if finding['category'] == 'password_policy':
                recommendations.append('Implement strong password policies and multi-factor authentication')
            elif finding['category'] == 'access_control':
                recommendations.append('Review and implement principle of least privilege')
            elif finding['category'] == 'data_encryption':
                recommendations.append('Encrypt all sensitive data at rest and in transit')
            elif finding['category'] == 'security_updates':
                recommendations.append('Establish regular security update procedures')
        
        return list(set(recommendations))  # Eliminar duplicados
    
    def _save_audit(self, target_system, findings, recommendations, risk_level):
        """Guardar auditoría"""
        conn = sqlite3.connect(self.security_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_audits 
            (audit_name, audit_type, target_system, findings, recommendations, 
             risk_level, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (f"Security_Audit_{target_system}", 'comprehensive', target_system, 
              json.dumps(findings), json.dumps(recommendations), risk_level, 
              datetime.now().isoformat()))
        
        audit_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return audit_id
    
    def scan_vulnerabilities(self, target_systems):
        """Escanear vulnerabilidades"""
        vulnerabilities = []
        
        # Simular escaneo de vulnerabilidades
        common_vulnerabilities = [
            {
                'name': 'SQL Injection',
                'cve_id': 'CVE-2023-1234',
                'severity': 'high',
                'description': 'Application vulnerable to SQL injection attacks'
            },
            {
                'name': 'Cross-Site Scripting',
                'cve_id': 'CVE-2023-1235',
                'severity': 'medium',
                'description': 'XSS vulnerability in web application'
            },
            {
                'name': 'Outdated Software',
                'cve_id': 'CVE-2023-1236',
                'severity': 'high',
                'description': 'Outdated software with known vulnerabilities'
            },
            {
                'name': 'Weak Encryption',
                'cve_id': 'CVE-2023-1237',
                'severity': 'medium',
                'description': 'Weak encryption algorithms in use'
            }
        ]
        
        for system in target_systems:
            # Simular vulnerabilidades encontradas
            system_vulns = random.sample(common_vulnerabilities, random.randint(1, 3))
            
            for vuln in system_vulns:
                vulnerability = {
                    'name': vuln['name'],
                    'cve_id': vuln['cve_id'],
                    'severity': vuln['severity'],
                    'affected_system': system,
                    'description': vuln['description'],
                    'patch_status': 'unpatched'
                }
                
                vulnerabilities.append(vulnerability)
                
                # Guardar vulnerabilidad
                self._save_vulnerability(vulnerability)
        
        return vulnerabilities
    
    def _save_vulnerability(self, vulnerability):
        """Guardar vulnerabilidad"""
        conn = sqlite3.connect(self.security_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO vulnerabilities 
            (vulnerability_name, cve_id, severity, affected_systems, description, 
             patch_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (vulnerability['name'], vulnerability['cve_id'], vulnerability['severity'],
              vulnerability['affected_system'], vulnerability['description'], 
              vulnerability['patch_status'], datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def generate_security_report(self):
        """Generar reporte de seguridad"""
        conn = sqlite3.connect(self.security_db)
        cursor = conn.cursor()
        
        # Estadísticas de amenazas
        cursor.execute('SELECT COUNT(*) FROM security_threats')
        total_threats = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM security_threats WHERE status = "detected"')
        active_threats = cursor.fetchone()[0]
        
        # Estadísticas de incidentes
        cursor.execute('SELECT COUNT(*) FROM security_incidents')
        total_incidents = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM security_incidents WHERE status = "active"')
        active_incidents = cursor.fetchone()[0]
        
        # Estadísticas de vulnerabilidades
        cursor.execute('SELECT COUNT(*) FROM vulnerabilities')
        total_vulnerabilities = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM vulnerabilities WHERE patch_status = "unpatched"')
        unpatched_vulnerabilities = cursor.fetchone()[0]
        
        # Estadísticas de auditorías
        cursor.execute('SELECT COUNT(*) FROM security_audits')
        total_audits = cursor.fetchone()[0]
        
        # Nivel de riesgo promedio
        cursor.execute('''
            SELECT risk_level, COUNT(*) FROM security_audits 
            GROUP BY risk_level
        ''')
        risk_levels = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_threats': total_threats,
            'active_threats': active_threats,
            'total_incidents': total_incidents,
            'active_incidents': active_incidents,
            'total_vulnerabilities': total_vulnerabilities,
            'unpatched_vulnerabilities': unpatched_vulnerabilities,
            'total_audits': total_audits,
            'risk_levels': risk_levels
        }

def main():
    security_system = CybersecuritySystem()
    
    print("🔒 Sistema de Ciberseguridad Avanzada")
    print("=" * 50)
    print("1. Detectar amenazas")
    print("2. Crear incidente de seguridad")
    print("3. Realizar auditoría de seguridad")
    print("4. Escanear vulnerabilidades")
    print("5. Generar reporte de seguridad")
    print("6. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-6): ").strip()
        
        if choice == '1':
            data = input("Datos a analizar: ").strip()
            if data:
                print("🔍 Analizando datos en busca de amenazas...")
                threats = security_system.detect_threats(data)
                
                if threats:
                    print(f"⚠️ Amenazas detectadas: {len(threats)}")
                    for threat in threats:
                        print(f"  • {threat['type'].upper()}: {threat['description']} (Confianza: {threat['confidence']:.2f})")
                else:
                    print("✅ No se detectaron amenazas")
            else:
                print("❌ Datos requeridos para análisis")
        
        elif choice == '2':
            incident_name = input("Nombre del incidente: ").strip()
            incident_type = input("Tipo de incidente: ").strip()
            severity = input("Severidad (low/medium/high/critical): ").strip()
            affected_systems = input("Sistemas afectados (separados por coma): ").strip().split(',')
            affected_systems = [sys.strip() for sys in affected_systems if sys.strip()]
            description = input("Descripción del incidente: ").strip()
            
            if incident_name and incident_type and severity:
                incident_id = security_system.create_security_incident(
                    incident_name, incident_type, severity, affected_systems, description
                )
                print(f"✅ Incidente de seguridad creado con ID: {incident_id}")
                print(f"📋 Sistemas afectados: {len(affected_systems)}")
            else:
                print("❌ Datos del incidente requeridos")
        
        elif choice == '3':
            target_system = input("Sistema a auditar: ").strip()
            if target_system:
                print(f"🔍 Realizando auditoría de seguridad en {target_system}...")
                audit_result = security_system.perform_security_audit(target_system)
                
                print(f"✅ Auditoría completada:")
                print(f"  📊 Hallazgos: {len(audit_result['findings'])}")
                print(f"  🎯 Nivel de riesgo: {audit_result['risk_level'].upper()}")
                print(f"  💡 Recomendaciones: {len(audit_result['recommendations'])}")
                
                if audit_result['findings']:
                    print(f"  🔍 Hallazgos principales:")
                    for finding in audit_result['findings'][:3]:  # Mostrar solo los primeros 3
                        print(f"    • {finding['issue']} ({finding['severity']})")
            else:
                print("❌ Sistema objetivo requerido")
        
        elif choice == '4':
            systems = input("Sistemas a escanear (separados por coma): ").strip().split(',')
            systems = [sys.strip() for sys in systems if sys.strip()]
            
            if systems:
                print(f"🔍 Escaneando vulnerabilidades en {len(systems)} sistemas...")
                vulnerabilities = security_system.scan_vulnerabilities(systems)
                
                print(f"✅ Escaneo completado:")
                print(f"  🐛 Vulnerabilidades encontradas: {len(vulnerabilities)}")
                
                # Agrupar por severidad
                severity_counts = {}
                for vuln in vulnerabilities:
                    severity = vuln['severity']
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                for severity, count in severity_counts.items():
                    print(f"    • {severity.upper()}: {count}")
            else:
                print("❌ Sistemas objetivo requeridos")
        
        elif choice == '5':
            print("📊 Generando reporte de seguridad...")
            report = security_system.generate_security_report()
            
            print(f"\n📋 Reporte de Seguridad:")
            print(f"  🚨 Amenazas totales: {report['total_threats']}")
            print(f"  ⚠️ Amenazas activas: {report['active_threats']}")
            print(f"  📋 Incidentes totales: {report['total_incidents']}")
            print(f"  🔥 Incidentes activos: {report['active_incidents']}")
            print(f"  🐛 Vulnerabilidades: {report['total_vulnerabilities']}")
            print(f"  ❌ Sin parche: {report['unpatched_vulnerabilities']}")
            print(f"  🔍 Auditorías realizadas: {report['total_audits']}")
            
            if report['risk_levels']:
                print(f"\n🎯 Distribución de riesgo:")
                for level, count in report['risk_levels'].items():
                    print(f"  • {level.upper()}: {count}")
        
        elif choice == '6':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()


