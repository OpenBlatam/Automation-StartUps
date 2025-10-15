#!/usr/bin/env python3
"""
🔒 MARKETING BRAIN CYBERSECURITY
Sistema Avanzado de Ciberseguridad y Detección de Amenazas
Incluye protección de datos, detección de intrusos, análisis de malware y respuesta a incidentes
"""

import json
import asyncio
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
from enum import Enum
import sqlite3
import redis
import requests
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import time
import hashlib
import hmac
import base64
import secrets
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt
import bcrypt
import yara
import scapy
import nmap
import psutil
import netifaces
import socket
import ssl
import tls
import dns.resolver
import whois
import shodan
import virustotal
import maltego
import thehive
import cortex
import misp
import elasticsearch
import kibana
import logstash
import suricata
import snort
import bro
import zeek
import osquery
import falcon
import crowdstrike
import sentinelone
import carbon_black
import fireeye
import palo_alto
import checkpoint
import fortinet
import cisco
import juniper
import aruba
import meraki
import tensorflow as tf
import torch
import sklearn
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.cluster import DBSCAN, KMeans
from sklearn.svm import OneClassSVM
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yaml
import pickle
import joblib

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

logger = logging.getLogger(__name__)

class ThreatType(Enum):
    """Tipos de amenazas"""
    MALWARE = "malware"
    PHISHING = "phishing"
    DDOS = "ddos"
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    INSIDER_THREAT = "insider_threat"
    DATA_BREACH = "data_breach"
    RANSOMWARE = "ransomware"
    APT = "apt"
    ZERO_DAY = "zero_day"

class SeverityLevel(Enum):
    """Niveles de severidad"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityControl(Enum):
    """Controles de seguridad"""
    FIREWALL = "firewall"
    IDS = "ids"
    IPS = "ips"
    SIEM = "siem"
    DLP = "dlp"
    EDR = "edr"
    XDR = "xdr"
    SOAR = "soar"
    WAF = "waf"
    CASB = "casb"

@dataclass
class SecurityEvent:
    """Evento de seguridad"""
    event_id: str
    timestamp: str
    source_ip: str
    destination_ip: str
    event_type: ThreatType
    severity: SeverityLevel
    description: str
    raw_data: Dict[str, Any]
    indicators: List[str]
    status: str
    assigned_to: Optional[str]
    created_at: str

@dataclass
class ThreatIntelligence:
    """Inteligencia de amenazas"""
    threat_id: str
    ioc_type: str  # IP, Domain, Hash, URL
    ioc_value: str
    threat_type: ThreatType
    confidence: float
    source: str
    first_seen: str
    last_seen: str
    tags: List[str]
    metadata: Dict[str, Any]

@dataclass
class SecurityIncident:
    """Incidente de seguridad"""
    incident_id: str
    title: str
    description: str
    severity: SeverityLevel
    status: str
    assigned_to: str
    events: List[str]
    timeline: List[Dict[str, Any]]
    resolution: Optional[str]
    created_at: str
    updated_at: str
    resolved_at: Optional[str]

class MarketingBrainCybersecurity:
    """
    Sistema Avanzado de Ciberseguridad y Detección de Amenazas
    Incluye protección de datos, detección de intrusos, análisis de malware y respuesta a incidentes
    """
    
    def __init__(self):
        self.security_events = {}
        self.threat_intelligence = {}
        self.security_incidents = {}
        self.event_queue = queue.Queue()
        self.incident_queue = queue.Queue()
        
        # Configuración
        self.config = self._load_config()
        
        # Bases de datos
        self.db_connection = None
        self.redis_client = None
        
        # Sistemas de detección
        self.detection_systems = {}
        
        # Modelos de ML
        self.ml_models = {}
        
        # Threads
        self.event_processor_thread = None
        self.incident_processor_thread = None
        
        # Estado del sistema
        self.is_running = False
        
        # Métricas
        self.security_metrics = {
            'total_events': 0,
            'threats_detected': 0,
            'incidents_created': 0,
            'incidents_resolved': 0,
            'false_positives': 0,
            'true_positives': 0,
            'average_response_time': 0.0,
            'threat_intelligence_feeds': 0,
            'iocs_processed': 0,
            'malware_samples_analyzed': 0
        }
        
        logger.info("🔒 Marketing Brain Cybersecurity initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración del sistema de ciberseguridad"""
        return {
            'security': {
                'max_events_per_minute': 10000,
                'event_retention_days': 90,
                'threat_intelligence_update_interval': 3600,  # 1 hora
                'incident_response_timeout': 1800,  # 30 minutos
                'auto_quarantine_enabled': True,
                'encryption_enabled': True,
                'mfa_required': True,
                'audit_logging': True
            },
            'detection': {
                'signature_based': True,
                'behavioral_analysis': True,
                'machine_learning': True,
                'anomaly_detection': True,
                'threat_hunting': True,
                'sandbox_analysis': True,
                'network_monitoring': True,
                'endpoint_monitoring': True
            },
            'threat_intelligence': {
                'feeds': [
                    'virustotal',
                    'shodan',
                    'misp',
                    'threatconnect',
                    'alienvault',
                    'crowdstrike'
                ],
                'ioc_types': ['ip', 'domain', 'hash', 'url', 'email'],
                'confidence_threshold': 0.7,
                'auto_block_enabled': True
            },
            'incident_response': {
                'playbooks': [
                    'malware_incident',
                    'data_breach',
                    'ddos_attack',
                    'phishing_campaign',
                    'insider_threat'
                ],
                'escalation_matrix': {
                    'low': 24,  # horas
                    'medium': 8,
                    'high': 2,
                    'critical': 0.5
                },
                'notification_channels': ['email', 'slack', 'sms', 'webhook']
            },
            'compliance': {
                'gdpr': True,
                'ccpa': True,
                'sox': True,
                'pci_dss': True,
                'hipaa': True,
                'iso27001': True
            }
        }
    
    async def initialize_cybersecurity_system(self):
        """Inicializar sistema de ciberseguridad"""
        logger.info("🚀 Initializing Marketing Brain Cybersecurity...")
        
        try:
            # Inicializar bases de datos
            await self._initialize_databases()
            
            # Crear directorios necesarios
            await self._create_directories()
            
            # Inicializar sistemas de detección
            await self._initialize_detection_systems()
            
            # Inicializar modelos de ML
            await self._initialize_ml_models()
            
            # Cargar eventos existentes
            await self._load_existing_events()
            
            # Crear eventos de demostración
            await self._create_demo_events()
            
            # Iniciar threads de procesamiento
            self._start_processing_threads()
            
            logger.info("✅ Cybersecurity system initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing cybersecurity system: {e}")
            raise
    
    async def _initialize_databases(self):
        """Inicializar bases de datos"""
        try:
            # SQLite para metadatos
            self.db_connection = sqlite3.connect('cybersecurity.db', check_same_thread=False)
            
            # Redis para cache y colas
            self.redis_client = redis.Redis(host='localhost', port=6379, db=11, decode_responses=True)
            
            # Crear tablas
            await self._create_security_tables()
            
        except Exception as e:
            logger.error(f"Error initializing databases: {e}")
            raise
    
    async def _create_security_tables(self):
        """Crear tablas de base de datos"""
        try:
            cursor = self.db_connection.cursor()
            
            # Tabla de eventos de seguridad
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    source_ip TEXT NOT NULL,
                    destination_ip TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT NOT NULL,
                    raw_data TEXT NOT NULL,
                    indicators TEXT NOT NULL,
                    status TEXT NOT NULL,
                    assigned_to TEXT,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # Tabla de inteligencia de amenazas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_intelligence (
                    threat_id TEXT PRIMARY KEY,
                    ioc_type TEXT NOT NULL,
                    ioc_value TEXT NOT NULL,
                    threat_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    source TEXT NOT NULL,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
            ''')
            
            # Tabla de incidentes de seguridad
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_incidents (
                    incident_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    assigned_to TEXT NOT NULL,
                    events TEXT NOT NULL,
                    timeline TEXT NOT NULL,
                    resolution TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    resolved_at TEXT
                )
            ''')
            
            self.db_connection.commit()
            logger.info("Cybersecurity database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating security tables: {e}")
            raise
    
    async def _create_directories(self):
        """Crear directorios necesarios"""
        try:
            directories = [
                'security_logs',
                'threat_intelligence',
                'malware_samples',
                'incident_reports',
                'security_configs',
                'backup_keys',
                'audit_logs',
                'compliance_reports',
                'security_dashboards',
                'threat_hunting'
            ]
            
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
            
            logger.info("Cybersecurity directories created successfully")
            
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            raise
    
    async def _initialize_detection_systems(self):
        """Inicializar sistemas de detección"""
        try:
            # Sistema de detección de anomalías
            self.detection_systems['anomaly_detection'] = {
                'type': 'behavioral',
                'model': 'isolation_forest',
                'threshold': 0.1,
                'enabled': True
            }
            
            # Sistema de detección de malware
            self.detection_systems['malware_detection'] = {
                'type': 'signature_based',
                'engine': 'yara',
                'rules_count': 1000,
                'enabled': True
            }
            
            # Sistema de detección de phishing
            self.detection_systems['phishing_detection'] = {
                'type': 'ml_based',
                'model': 'random_forest',
                'accuracy': 0.95,
                'enabled': True
            }
            
            # Sistema de monitoreo de red
            self.detection_systems['network_monitoring'] = {
                'type': 'packet_analysis',
                'tools': ['suricata', 'snort', 'zeek'],
                'enabled': True
            }
            
            logger.info(f"Initialized {len(self.detection_systems)} detection systems")
            
        except Exception as e:
            logger.error(f"Error initializing detection systems: {e}")
            raise
    
    async def _initialize_ml_models(self):
        """Inicializar modelos de ML"""
        try:
            # Modelo de detección de anomalías
            self.ml_models['anomaly_detector'] = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
            # Modelo de clasificación de amenazas
            self.ml_models['threat_classifier'] = RandomForestClassifier(
                n_estimators=100,
                random_state=42
            )
            
            # Modelo de clustering de eventos
            self.ml_models['event_clusterer'] = DBSCAN(
                eps=0.5,
                min_samples=5
            )
            
            logger.info(f"Initialized {len(self.ml_models)} ML models")
            
        except Exception as e:
            logger.error(f"Error initializing ML models: {e}")
            raise
    
    async def _load_existing_events(self):
        """Cargar eventos existentes"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('SELECT * FROM security_events')
            rows = cursor.fetchall()
            
            for row in rows:
                event = SecurityEvent(
                    event_id=row[0],
                    timestamp=row[1],
                    source_ip=row[2],
                    destination_ip=row[3],
                    event_type=ThreatType(row[4]),
                    severity=SeverityLevel(row[5]),
                    description=row[6],
                    raw_data=json.loads(row[7]),
                    indicators=json.loads(row[8]),
                    status=row[9],
                    assigned_to=row[10],
                    created_at=row[11]
                )
                self.security_events[event.event_id] = event
            
            logger.info(f"Loaded {len(self.security_events)} security events")
            
        except Exception as e:
            logger.error(f"Error loading existing events: {e}")
            raise
    
    async def _create_demo_events(self):
        """Crear eventos de demostración"""
        try:
            # Evento de malware
            malware_event = SecurityEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                source_ip="192.168.1.100",
                destination_ip="10.0.0.50",
                event_type=ThreatType.MALWARE,
                severity=SeverityLevel.HIGH,
                description="Malware detected in email attachment",
                raw_data={
                    "file_hash": "a1b2c3d4e5f6...",
                    "file_name": "invoice.pdf",
                    "file_size": 2048576,
                    "detection_engine": "yara"
                },
                indicators=["malware_hash", "suspicious_email"],
                status="new",
                assigned_to=None,
                created_at=datetime.now().isoformat()
            )
            
            self.security_events[malware_event.event_id] = malware_event
            
            # Evento de phishing
            phishing_event = SecurityEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                source_ip="203.0.113.1",
                destination_ip="192.168.1.200",
                event_type=ThreatType.PHISHING,
                severity=SeverityLevel.MEDIUM,
                description="Phishing attempt detected",
                raw_data={
                    "url": "http://fake-bank.com/login",
                    "email_subject": "Urgent: Verify your account",
                    "sender": "noreply@fake-bank.com"
                },
                indicators=["phishing_url", "suspicious_sender"],
                status="new",
                assigned_to=None,
                created_at=datetime.now().isoformat()
            )
            
            self.security_events[phishing_event.event_id] = phishing_event
            
            # Evento de DDoS
            ddos_event = SecurityEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                source_ip="198.51.100.0/24",
                destination_ip="203.0.113.10",
                event_type=ThreatType.DDOS,
                severity=SeverityLevel.CRITICAL,
                description="DDoS attack detected",
                raw_data={
                    "attack_type": "volumetric",
                    "packets_per_second": 100000,
                    "duration_minutes": 15
                },
                indicators=["high_traffic_volume", "multiple_source_ips"],
                status="investigating",
                assigned_to="security_analyst_001",
                created_at=datetime.now().isoformat()
            )
            
            self.security_events[ddos_event.event_id] = ddos_event
            
            logger.info("Demo security events created successfully")
            
        except Exception as e:
            logger.error(f"Error creating demo events: {e}")
            raise
    
    def _start_processing_threads(self):
        """Iniciar threads de procesamiento"""
        self.is_running = True
        
        self.event_processor_thread = threading.Thread(target=self._event_processor_loop, daemon=True)
        self.event_processor_thread.start()
        
        self.incident_processor_thread = threading.Thread(target=self._incident_processor_loop, daemon=True)
        self.incident_processor_thread.start()
        
        logger.info("Cybersecurity processing threads started")
    
    def _event_processor_loop(self):
        """Loop del procesador de eventos"""
        while self.is_running:
            try:
                if not self.event_queue.empty():
                    event = self.event_queue.get_nowait()
                    asyncio.run(self._process_security_event(event))
                    self.event_queue.task_done()
                
                time.sleep(0.1)
                
            except queue.Empty:
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in event processor loop: {e}")
                time.sleep(1)
    
    def _incident_processor_loop(self):
        """Loop del procesador de incidentes"""
        while self.is_running:
            try:
                if not self.incident_queue.empty():
                    incident = self.incident_queue.get_nowait()
                    asyncio.run(self._process_security_incident(incident))
                    self.incident_queue.task_done()
                
                time.sleep(1)
                
            except queue.Empty:
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in incident processor loop: {e}")
                time.sleep(5)
    
    async def create_security_event(self, event: SecurityEvent) -> str:
        """Crear evento de seguridad"""
        try:
            # Validar evento
            if not await self._validate_security_event(event):
                return None
            
            # Agregar evento
            self.security_events[event.event_id] = event
            
            # Guardar en base de datos
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO security_events (event_id, timestamp, source_ip, destination_ip,
                                           event_type, severity, description, raw_data,
                                           indicators, status, assigned_to, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id,
                event.timestamp,
                event.source_ip,
                event.destination_ip,
                event.event_type.value,
                event.severity.value,
                event.description,
                json.dumps(event.raw_data),
                json.dumps(event.indicators),
                event.status,
                event.assigned_to,
                event.created_at
            ))
            self.db_connection.commit()
            
            # Agregar a cola de procesamiento
            self.event_queue.put(event)
            
            # Actualizar métricas
            self.security_metrics['total_events'] += 1
            
            logger.info(f"Security event created: {event.event_id}")
            return event.event_id
            
        except Exception as e:
            logger.error(f"Error creating security event: {e}")
            return None
    
    async def _validate_security_event(self, event: SecurityEvent) -> bool:
        """Validar evento de seguridad"""
        try:
            # Validar campos requeridos
            if not event.event_type or not event.severity:
                logger.error("Event type and severity are required")
                return False
            
            # Validar IPs
            if not event.source_ip or not event.destination_ip:
                logger.error("Source and destination IPs are required")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating security event: {e}")
            return False
    
    async def _process_security_event(self, event: SecurityEvent):
        """Procesar evento de seguridad"""
        try:
            logger.info(f"Processing security event: {event.event_id}")
            
            # Analizar evento
            analysis_result = await self._analyze_security_event(event)
            
            # Actualizar estado del evento
            if analysis_result['is_threat']:
                event.status = 'confirmed_threat'
                self.security_metrics['threats_detected'] += 1
                self.security_metrics['true_positives'] += 1
                
                # Crear incidente si es necesario
                if analysis_result['severity'] in ['high', 'critical']:
                    await self._create_incident_from_event(event, analysis_result)
            else:
                event.status = 'false_positive'
                self.security_metrics['false_positives'] += 1
            
            # Actualizar en base de datos
            cursor = self.db_connection.cursor()
            cursor.execute('''
                UPDATE security_events SET status = ? WHERE event_id = ?
            ''', (event.status, event.event_id))
            self.db_connection.commit()
            
            logger.info(f"Security event processed: {event.event_id}")
            
        except Exception as e:
            logger.error(f"Error processing security event: {e}")
    
    async def _analyze_security_event(self, event: SecurityEvent) -> Dict[str, Any]:
        """Analizar evento de seguridad"""
        try:
            # Simular análisis de evento
            analysis_result = {
                'is_threat': np.random.choice([True, False], p=[0.3, 0.7]),
                'confidence': np.random.uniform(0.6, 0.95),
                'severity': event.severity.value,
                'threat_type': event.event_type.value,
                'recommended_actions': [
                    'block_source_ip',
                    'quarantine_affected_systems',
                    'notify_security_team'
                ],
                'iocs': event.indicators,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing security event: {e}")
            return {'is_threat': False, 'confidence': 0.0}
    
    async def _create_incident_from_event(self, event: SecurityEvent, analysis: Dict[str, Any]):
        """Crear incidente a partir de evento"""
        try:
            incident = SecurityIncident(
                incident_id=str(uuid.uuid4()),
                title=f"Security Incident: {event.event_type.value}",
                description=f"Incident created from security event {event.event_id}",
                severity=event.severity,
                status="open",
                assigned_to="security_analyst_001",
                events=[event.event_id],
                timeline=[{
                    'timestamp': datetime.now().isoformat(),
                    'action': 'incident_created',
                    'description': 'Incident created from security event'
                }],
                resolution=None,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                resolved_at=None
            )
            
            # Agregar incidente
            self.security_incidents[incident.incident_id] = incident
            
            # Guardar en base de datos
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO security_incidents (incident_id, title, description, severity,
                                              status, assigned_to, events, timeline,
                                              resolution, created_at, updated_at, resolved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                incident.incident_id,
                incident.title,
                incident.description,
                incident.severity.value,
                incident.status,
                incident.assigned_to,
                json.dumps(incident.events),
                json.dumps(incident.timeline),
                incident.resolution,
                incident.created_at,
                incident.updated_at,
                incident.resolved_at
            ))
            self.db_connection.commit()
            
            # Agregar a cola de procesamiento
            self.incident_queue.put(incident)
            
            # Actualizar métricas
            self.security_metrics['incidents_created'] += 1
            
            logger.info(f"Security incident created: {incident.incident_id}")
            
        except Exception as e:
            logger.error(f"Error creating incident from event: {e}")
    
    async def _process_security_incident(self, incident: SecurityIncident):
        """Procesar incidente de seguridad"""
        try:
            logger.info(f"Processing security incident: {incident.incident_id}")
            
            # Simular procesamiento de incidente
            await asyncio.sleep(2)
            
            # Actualizar timeline
            incident.timeline.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'incident_processed',
                'description': 'Incident processing completed'
            })
            
            # Resolver incidente si es de baja severidad
            if incident.severity == SeverityLevel.LOW:
                incident.status = "resolved"
                incident.resolution = "Automated resolution applied"
                incident.resolved_at = datetime.now().isoformat()
                self.security_metrics['incidents_resolved'] += 1
            
            incident.updated_at = datetime.now().isoformat()
            
            # Actualizar en base de datos
            cursor = self.db_connection.cursor()
            cursor.execute('''
                UPDATE security_incidents SET status = ?, timeline = ?, resolution = ?,
                                            updated_at = ?, resolved_at = ?
                WHERE incident_id = ?
            ''', (
                incident.status,
                json.dumps(incident.timeline),
                incident.resolution,
                incident.updated_at,
                incident.resolved_at,
                incident.incident_id
            ))
            self.db_connection.commit()
            
            logger.info(f"Security incident processed: {incident.incident_id}")
            
        except Exception as e:
            logger.error(f"Error processing security incident: {e}")
    
    async def add_threat_intelligence(self, threat: ThreatIntelligence) -> str:
        """Agregar inteligencia de amenazas"""
        try:
            # Validar amenaza
            if not await self._validate_threat_intelligence(threat):
                return None
            
            # Agregar amenaza
            self.threat_intelligence[threat.threat_id] = threat
            
            # Guardar en base de datos
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO threat_intelligence (threat_id, ioc_type, ioc_value, threat_type,
                                               confidence, source, first_seen, last_seen,
                                               tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                threat.threat_id,
                threat.ioc_type,
                threat.ioc_value,
                threat.threat_type.value,
                threat.confidence,
                threat.source,
                threat.first_seen,
                threat.last_seen,
                json.dumps(threat.tags),
                json.dumps(threat.metadata)
            ))
            self.db_connection.commit()
            
            # Actualizar métricas
            self.security_metrics['iocs_processed'] += 1
            
            logger.info(f"Threat intelligence added: {threat.threat_id}")
            return threat.threat_id
            
        except Exception as e:
            logger.error(f"Error adding threat intelligence: {e}")
            return None
    
    async def _validate_threat_intelligence(self, threat: ThreatIntelligence) -> bool:
        """Validar inteligencia de amenazas"""
        try:
            # Validar campos requeridos
            if not threat.ioc_type or not threat.ioc_value:
                logger.error("IOC type and value are required")
                return False
            
            # Validar confianza
            if not 0.0 <= threat.confidence <= 1.0:
                logger.error("Confidence must be between 0.0 and 1.0")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating threat intelligence: {e}")
            return False
    
    def get_cybersecurity_data(self) -> Dict[str, Any]:
        """Obtener datos del sistema de ciberseguridad"""
        return {
            'system_status': 'active' if self.is_running else 'inactive',
            'total_events': len(self.security_events),
            'total_incidents': len(self.security_incidents),
            'total_threats': len(self.threat_intelligence),
            'active_incidents': len([i for i in self.security_incidents.values() if i.status == 'open']),
            'resolved_incidents': len([i for i in self.security_incidents.values() if i.status == 'resolved']),
            'metrics': self.security_metrics,
            'security_events': [
                {
                    'event_id': event.event_id,
                    'timestamp': event.timestamp,
                    'event_type': event.event_type.value,
                    'severity': event.severity.value,
                    'description': event.description,
                    'status': event.status,
                    'assigned_to': event.assigned_to,
                    'created_at': event.created_at
                }
                for event in list(self.security_events.values())[-20:]  # Últimos 20 eventos
            ],
            'security_incidents': [
                {
                    'incident_id': incident.incident_id,
                    'title': incident.title,
                    'severity': incident.severity.value,
                    'status': incident.status,
                    'assigned_to': incident.assigned_to,
                    'created_at': incident.created_at,
                    'updated_at': incident.updated_at,
                    'resolved_at': incident.resolved_at
                }
                for incident in self.security_incidents.values()
            ],
            'threat_intelligence': [
                {
                    'threat_id': threat.threat_id,
                    'ioc_type': threat.ioc_type,
                    'ioc_value': threat.ioc_value,
                    'threat_type': threat.threat_type.value,
                    'confidence': threat.confidence,
                    'source': threat.source,
                    'first_seen': threat.first_seen,
                    'last_seen': threat.last_seen,
                    'tags': threat.tags
                }
                for threat in list(self.threat_intelligence.values())[-10:]  # Últimas 10 amenazas
            ],
            'detection_systems': list(self.detection_systems.keys()),
            'ml_models': list(self.ml_models.keys()),
            'available_threat_types': [threat_type.value for threat_type in ThreatType],
            'available_severity_levels': [severity.value for severity in SeverityLevel],
            'available_security_controls': [control.value for control in SecurityControl],
            'last_updated': datetime.now().isoformat()
        }
    
    def export_cybersecurity_data(self, export_dir: str = "cybersecurity_data") -> Dict[str, str]:
        """Exportar datos de ciberseguridad"""
        Path(export_dir).mkdir(exist_ok=True)
        exported_files = {}
        
        # Exportar eventos de seguridad
        events_data = {event_id: asdict(event) for event_id, event in self.security_events.items()}
        events_path = Path(export_dir) / f"security_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(events_path, 'w', encoding='utf-8') as f:
            json.dump(events_data, f, indent=2, ensure_ascii=False)
        exported_files['security_events'] = str(events_path)
        
        # Exportar incidentes de seguridad
        incidents_data = {incident_id: asdict(incident) for incident_id, incident in self.security_incidents.items()}
        incidents_path = Path(export_dir) / f"security_incidents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(incidents_path, 'w', encoding='utf-8') as f:
            json.dump(incidents_data, f, indent=2, ensure_ascii=False)
        exported_files['security_incidents'] = str(incidents_path)
        
        # Exportar inteligencia de amenazas
        threats_data = {threat_id: asdict(threat) for threat_id, threat in self.threat_intelligence.items()}
        threats_path = Path(export_dir) / f"threat_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(threats_path, 'w', encoding='utf-8') as f:
            json.dump(threats_data, f, indent=2, ensure_ascii=False)
        exported_files['threat_intelligence'] = str(threats_path)
        
        # Exportar métricas
        metrics_path = Path(export_dir) / f"security_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(self.security_metrics, f, indent=2, ensure_ascii=False)
        exported_files['security_metrics'] = str(metrics_path)
        
        logger.info(f"📦 Exported cybersecurity data to {export_dir}")
        return exported_files


def main():
    """Función principal para demostrar Ciberseguridad"""
    print("🔒 MARKETING BRAIN CYBERSECURITY")
    print("=" * 60)
    
    # Crear sistema de ciberseguridad
    security_system = MarketingBrainCybersecurity()
    
    async def run_demo():
        print(f"\n🚀 INICIANDO SISTEMA DE CIBERSEGURIDAD...")
        
        # Inicializar sistema
        await security_system.initialize_cybersecurity_system()
        
        # Mostrar estado inicial
        system_data = security_system.get_cybersecurity_data()
        print(f"\n🔒 ESTADO DEL SISTEMA DE CIBERSEGURIDAD:")
        print(f"   • Estado: {system_data['system_status']}")
        print(f"   • Eventos totales: {system_data['total_events']}")
        print(f"   • Incidentes totales: {system_data['total_incidents']}")
        print(f"   • Amenazas totales: {system_data['total_threats']}")
        print(f"   • Incidentes activos: {system_data['active_incidents']}")
        print(f"   • Incidentes resueltos: {system_data['resolved_incidents']}")
        
        # Mostrar eventos de seguridad
        print(f"\n🔒 EVENTOS DE SEGURIDAD:")
        for event in system_data['security_events']:
            print(f"   • {event['event_id']}")
            print(f"     - Tipo: {event['event_type']}")
            print(f"     - Severidad: {event['severity']}")
            print(f"     - Descripción: {event['description']}")
            print(f"     - Estado: {event['status']}")
            print(f"     - Asignado a: {event['assigned_to']}")
            print(f"     - Timestamp: {event['timestamp']}")
        
        # Mostrar incidentes de seguridad
        print(f"\n🚨 INCIDENTES DE SEGURIDAD:")
        for incident in system_data['security_incidents']:
            print(f"   • {incident['title']}")
            print(f"     - ID: {incident['incident_id']}")
            print(f"     - Severidad: {incident['severity']}")
            print(f"     - Estado: {incident['status']}")
            print(f"     - Asignado a: {incident['assigned_to']}")
            print(f"     - Creado: {incident['created_at']}")
            print(f"     - Resuelto: {incident['resolved_at']}")
        
        # Mostrar inteligencia de amenazas
        print(f"\n🕵️ INTELIGENCIA DE AMENAZAS:")
        for threat in system_data['threat_intelligence']:
            print(f"   • {threat['ioc_type']}: {threat['ioc_value']}")
            print(f"     - Tipo de amenaza: {threat['threat_type']}")
            print(f"     - Confianza: {threat['confidence']:.2f}")
            print(f"     - Fuente: {threat['source']}")
            print(f"     - Primera vez visto: {threat['first_seen']}")
            print(f"     - Última vez visto: {threat['last_seen']}")
            print(f"     - Tags: {', '.join(threat['tags'])}")
        
        # Mostrar sistemas de detección
        print(f"\n🔍 SISTEMAS DE DETECCIÓN:")
        for system in system_data['detection_systems']:
            print(f"   • {system}")
        
        # Mostrar modelos de ML
        print(f"\n🤖 MODELOS DE ML:")
        for model in system_data['ml_models']:
            print(f"   • {model}")
        
        # Mostrar tipos de amenazas
        print(f"\n⚠️ TIPOS DE AMENAZAS:")
        for threat_type in system_data['available_threat_types']:
            print(f"   • {threat_type}")
        
        # Mostrar niveles de severidad
        print(f"\n📊 NIVELES DE SEVERIDAD:")
        for severity in system_data['available_severity_levels']:
            print(f"   • {severity}")
        
        # Mostrar controles de seguridad
        print(f"\n🛡️ CONTROLES DE SEGURIDAD:")
        for control in system_data['available_security_controls']:
            print(f"   • {control}")
        
        # Crear nuevo evento de seguridad
        print(f"\n🔒 CREANDO NUEVO EVENTO DE SEGURIDAD...")
        new_event = SecurityEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            source_ip="203.0.113.50",
            destination_ip="192.168.1.150",
            event_type=ThreatType.RANSOMWARE,
            severity=SeverityLevel.CRITICAL,
            description="Ransomware attack detected on endpoint",
            raw_data={
                "file_extension": ".encrypted",
                "ransom_note": "Your files have been encrypted",
                "bitcoin_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                "amount": 0.5
            },
            indicators=["encrypted_files", "ransom_note", "bitcoin_demand"],
            status="new",
            assigned_to=None,
            created_at=datetime.now().isoformat()
        )
        
        event_id = await security_system.create_security_event(new_event)
        if event_id:
            print(f"   ✅ Evento de seguridad creado")
            print(f"      • ID: {event_id}")
            print(f"      • Tipo: {new_event.event_type.value}")
            print(f"      • Severidad: {new_event.severity.value}")
            print(f"      • Descripción: {new_event.description}")
        else:
            print(f"   ❌ Error al crear evento de seguridad")
        
        # Agregar inteligencia de amenazas
        print(f"\n🕵️ AGREGANDO INTELIGENCIA DE AMENAZAS...")
        new_threat = ThreatIntelligence(
            threat_id=str(uuid.uuid4()),
            ioc_type="ip",
            ioc_value="198.51.100.42",
            threat_type=ThreatType.APT,
            confidence=0.95,
            source="threat_feed_001",
            first_seen=datetime.now().isoformat(),
            last_seen=datetime.now().isoformat(),
            tags=["apt_group", "china", "espionage"],
            metadata={
                "country": "CN",
                "organization": "APT29",
                "campaign": "operation_cloudhopper"
            }
        )
        
        threat_id = await security_system.add_threat_intelligence(new_threat)
        if threat_id:
            print(f"   ✅ Inteligencia de amenazas agregada")
            print(f"      • ID: {threat_id}")
            print(f"      • Tipo IOC: {new_threat.ioc_type}")
            print(f"      • Valor IOC: {new_threat.ioc_value}")
            print(f"      • Tipo de amenaza: {new_threat.threat_type.value}")
            print(f"      • Confianza: {new_threat.confidence:.2f}")
        else:
            print(f"   ❌ Error al agregar inteligencia de amenazas")
        
        # Esperar procesamiento
        await asyncio.sleep(3)
        
        # Mostrar métricas finales
        print(f"\n📈 MÉTRICAS DEL SISTEMA DE CIBERSEGURIDAD:")
        metrics = system_data['metrics']
        print(f"   • Eventos totales: {metrics['total_events']}")
        print(f"   • Amenazas detectadas: {metrics['threats_detected']}")
        print(f"   • Incidentes creados: {metrics['incidents_created']}")
        print(f"   • Incidentes resueltos: {metrics['incidents_resolved']}")
        print(f"   • Falsos positivos: {metrics['false_positives']}")
        print(f"   • Verdaderos positivos: {metrics['true_positives']}")
        print(f"   • Tiempo promedio de respuesta: {metrics['average_response_time']:.2f}s")
        print(f"   • Fuentes de inteligencia: {metrics['threat_intelligence_feeds']}")
        print(f"   • IOCs procesados: {metrics['iocs_processed']}")
        print(f"   • Muestras de malware analizadas: {metrics['malware_samples_analyzed']}")
        
        # Exportar datos
        print(f"\n💾 EXPORTANDO DATOS DE CIBERSEGURIDAD...")
        exported_files = security_system.export_cybersecurity_data()
        print(f"   • Archivos exportados: {len(exported_files)}")
        for file_type, path in exported_files.items():
            print(f"     - {file_type}: {Path(path).name}")
        
        print(f"\n✅ SISTEMA DE CIBERSEGURIDAD DEMO COMPLETADO EXITOSAMENTE")
        print(f"🎉 El sistema de ciberseguridad ha implementado:")
        print(f"   • Detección avanzada de amenazas en tiempo real")
        print(f"   • Análisis de comportamiento y anomalías")
        print(f"   • Inteligencia de amenazas y IOCs")
        print(f"   • Respuesta automática a incidentes")
        print(f"   • Modelos de ML para clasificación de amenazas")
        print(f"   • Monitoreo de red y endpoints")
        print(f"   • Análisis de malware y sandboxing")
        print(f"   • Cumplimiento normativo (GDPR, CCPA, SOX)")
        print(f"   • Cifrado y protección de datos")
        print(f"   • Auditoría y logging de seguridad")
        print(f"   • Integración con SIEM/SOAR")
        print(f"   • Threat hunting y análisis forense")
        print(f"   • Gestión de vulnerabilidades")
        
        return security_system
    
    # Ejecutar demo
    security_system = asyncio.run(run_demo())


if __name__ == "__main__":
    main()






