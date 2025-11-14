---
title: "Troubleshooting"
category: "06_documentation"
tags: []
created: "2025-10-29"
path: "06_documentation/Troubleshooting/troubleshooting.md"
---

# 🔧 Guía de Troubleshooting - ClickUp Brain

## Visión General

Esta guía proporciona soluciones a problemas comunes que pueden surgir durante la implementación, configuración y uso de ClickUp Brain.

## 🚨 Problemas Comunes

### 1. Problemas de Conectividad

#### Error: "Cannot connect to database"
```bash
# Síntomas
ERROR: could not connect to server: Connection refused
Is the server running on host "localhost" and accepting TCP/IP connections on port 5432?

# Diagnóstico
# 1. Verificar estado del servicio de base de datos
systemctl status postgresql
# o para Docker
docker ps | grep postgres

# 2. Verificar conectividad de red
telnet localhost 5432
# o
nc -zv localhost 5432

# 3. Verificar configuración de firewall
sudo ufw status
# o
sudo iptables -L

# Soluciones
# 1. Iniciar servicio de base de datos
sudo systemctl start postgresql
# o para Docker
docker-compose up -d postgres

# 2. Verificar configuración de PostgreSQL
sudo -u postgres psql -c "SHOW listen_addresses;"
sudo -u postgres psql -c "SHOW port;"

# 3. Configurar PostgreSQL para aceptar conexiones
# Editar /etc/postgresql/*/main/postgresql.conf
listen_addresses = '*'
port = 5432

# Editar /etc/postgresql/*/main/pg_hba.conf
host    all             all             0.0.0.0/0               md5

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

#### Error: "Redis connection failed"
```bash
# Síntomas
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.

# Diagnóstico
# 1. Verificar estado de Redis
systemctl status redis
# o para Docker
docker ps | grep redis

# 2. Verificar conectividad
redis-cli ping
# o
telnet localhost 6379

# Soluciones
# 1. Iniciar Redis
sudo systemctl start redis
# o para Docker
docker-compose up -d redis

# 2. Verificar configuración de Redis
redis-cli config get bind
redis-cli config get port

# 3. Configurar Redis para aceptar conexiones
# Editar /etc/redis/redis.conf
bind 0.0.0.0
port 6379

# Reiniciar Redis
sudo systemctl restart redis
```

### 2. Problemas de Autenticación

#### Error: "Invalid JWT token"
```python
# Síntomas
jwt.exceptions.InvalidTokenError: Invalid token
HTTP 401 Unauthorized

# Diagnóstico
import jwt
from datetime import datetime

# Verificar configuración JWT
JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

# Verificar token
try:
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    print(f"Token válido: {payload}")
except jwt.ExpiredSignatureError:
    print("Token expirado")
except jwt.InvalidTokenError:
    print("Token inválido")

# Soluciones
# 1. Verificar variable de entorno JWT_SECRET
echo $JWT_SECRET

# 2. Generar nuevo JWT_SECRET
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 3. Actualizar configuración
export JWT_SECRET="nuevo_secret_generado"

# 4. Verificar algoritmo JWT
# Asegurar que el algoritmo sea consistente en toda la aplicación
```

#### Error: "User not found or inactive"
```python
# Síntomas
HTTP 401 Unauthorized: User not found or inactive

# Diagnóstico
# 1. Verificar usuario en base de datos
from app.database import get_user_by_email

user = get_user_by_email("user@example.com")
if user:
    print(f"Usuario encontrado: {user.email}")
    print(f"Activo: {user.is_active}")
    print(f"Último login: {user.last_login}")
else:
    print("Usuario no encontrado")

# 2. Verificar estado de la cuenta
if user and not user.is_active:
    print("Usuario inactivo - verificar activación")

# Soluciones
# 1. Activar usuario
from app.database import activate_user
activate_user(user.id)

# 2. Verificar proceso de registro
# Asegurar que el usuario se active correctamente después del registro

# 3. Reenviar email de activación
from app.services.email import send_activation_email
send_activation_email(user.email, user.activation_token)
```

### 3. Problemas de Performance

#### Error: "Slow query performance"
```python
# Síntomas
Query took 5.2 seconds to execute
Database connection timeout

# Diagnóstico
# 1. Analizar queries lentas
import logging
logging.basicConfig(level=logging.DEBUG)

# Habilitar query logging en SQLAlchemy
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# 2. Usar EXPLAIN ANALYZE para queries problemáticas
from sqlalchemy import text

query = text("""
    EXPLAIN ANALYZE 
    SELECT * FROM strategic_opportunities 
    WHERE created_at > '2024-01-01' 
    AND market_segment = 'ai'
""")

result = db.execute(query)
print(result.fetchall())

# Soluciones
# 1. Agregar índices
from sqlalchemy import Index

# Crear índice compuesto
index = Index('idx_opportunities_created_market', 
              'created_at', 'market_segment')
index.create(db.engine)

# 2. Optimizar query
# Usar paginación
from sqlalchemy.orm import Query

def get_opportunities_paginated(page=1, per_page=20):
    query = Opportunity.query.filter(
        Opportunity.created_at > '2024-01-01',
        Opportunity.market_segment == 'ai'
    )
    
    return query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )

# 3. Usar cache para queries frecuentes
from flask_caching import Cache

@cache.memoize(timeout=300)  # Cache por 5 minutos
def get_market_opportunities(market_segment):
    return Opportunity.query.filter_by(
        market_segment=market_segment
    ).all()
```

#### Error: "High memory usage"
```python
# Síntomas
Memory usage: 85% (8.5GB / 10GB)
OutOfMemoryError: Java heap space

# Diagnóstico
# 1. Monitorear uso de memoria
import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    memory_percent = process.memory_percent()
    
    print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
    print(f"Porcentaje: {memory_percent:.2f}%")

# 2. Identificar memory leaks
import tracemalloc

tracemalloc.start()

# ... código que puede tener memory leak ...

current, peak = tracemalloc.get_traced_memory()
print(f"Memoria actual: {current / 1024 / 1024:.2f} MB")
print(f"Memoria pico: {peak / 1024 / 1024:.2f} MB")

# Soluciones
# 1. Optimizar procesamiento de datos
# Usar generadores en lugar de listas
def process_large_dataset():
    # ❌ Malo - carga todo en memoria
    data = [process_item(item) for item in large_dataset]
    
    # ✅ Bueno - usa generador
    for item in large_dataset:
        yield process_item(item)

# 2. Implementar paginación
def get_data_paginated(offset=0, limit=1000):
    return db.query(Model).offset(offset).limit(limit).all()

# 3. Limpiar cache periódicamente
import gc
gc.collect()  # Forzar garbage collection
```

### 4. Problemas de AI Services

#### Error: "AI model not responding"
```python
# Síntomas
AI service timeout after 30 seconds
Model prediction failed

# Diagnóstico
# 1. Verificar estado del servicio AI
import requests

def check_ai_service_health():
    try:
        response = requests.get('http://ai-service:8001/health', timeout=5)
        if response.status_code == 200:
            print("AI service is healthy")
            return True
        else:
            print(f"AI service unhealthy: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"AI service unreachable: {e}")
        return False

# 2. Verificar recursos del modelo
def check_model_resources():
    # Verificar GPU
    import torch
    if torch.cuda.is_available():
        print(f"GPU disponible: {torch.cuda.get_device_name()}")
        print(f"Memoria GPU: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    else:
        print("GPU no disponible")

# Soluciones
# 1. Reiniciar servicio AI
docker-compose restart ai-services

# 2. Verificar configuración del modelo
MODEL_CONFIG = {
    'model_path': '/models/strategic_analyzer',
    'batch_size': 32,
    'max_length': 512,
    'device': 'cuda' if torch.cuda.is_available() else 'cpu'
}

# 3. Implementar retry logic
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    print(f"Intento {attempt + 1} falló: {e}")
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=1)
def predict_with_ai(text):
    response = requests.post(
        'http://ai-service:8001/predict',
        json={'text': text},
        timeout=30
    )
    return response.json()
```

#### Error: "Model accuracy degraded"
```python
# Síntomas
Model accuracy dropped from 95% to 78%
Prediction confidence below threshold

# Diagnóstico
# 1. Evaluar performance del modelo
from sklearn.metrics import accuracy_score, classification_report

def evaluate_model_performance(model, test_data, test_labels):
    predictions = model.predict(test_data)
    accuracy = accuracy_score(test_labels, predictions)
    
    print(f"Accuracy: {accuracy:.4f}")
    print(classification_report(test_labels, predictions))
    
    return accuracy

# 2. Analizar drift de datos
import numpy as np
from scipy import stats

def detect_data_drift(reference_data, current_data):
    # Kolmogorov-Smirnov test
    ks_stat, p_value = stats.ks_2samp(reference_data, current_data)
    
    if p_value < 0.05:
        print("Data drift detectado")
        return True
    else:
        print("No hay data drift significativo")
        return False

# Soluciones
# 1. Retrenar modelo con datos actualizados
def retrain_model(new_data, new_labels):
    from sklearn.model_selection import train_test_split
    
    X_train, X_test, y_train, y_test = train_test_split(
        new_data, new_labels, test_size=0.2, random_state=42
    )
    
    # Entrenar nuevo modelo
    model = train_strategic_analyzer(X_train, y_train)
    
    # Evaluar performance
    accuracy = evaluate_model_performance(model, X_test, y_test)
    
    if accuracy > 0.85:  # Threshold de aceptación
        # Guardar nuevo modelo
        save_model(model, 'strategic_analyzer_v2')
        return model
    else:
        print("Nuevo modelo no cumple threshold de accuracy")
        return None

# 2. Implementar ensemble de modelos
from sklearn.ensemble import VotingClassifier

def create_ensemble_model(models):
    ensemble = VotingClassifier(
        estimators=[(f'model_{i}', model) for i, model in enumerate(models)],
        voting='soft'
    )
    return ensemble
```

### 5. Problemas de Integración

#### Error: "External API rate limit exceeded"
```python
# Síntomas
HTTP 429 Too Many Requests
Rate limit exceeded for API key

# Diagnóstico
# 1. Verificar límites de rate limiting
import requests
import time

def check_rate_limits(api_key):
    headers = {'Authorization': f'Bearer {api_key}'}
    
    # Hacer request de prueba
    response = requests.get('https://api.external-service.com/rate-limit', headers=headers)
    
    if 'X-RateLimit-Limit' in response.headers:
        limit = response.headers['X-RateLimit-Limit']
        remaining = response.headers['X-RateLimit-Remaining']
        reset_time = response.headers['X-RateLimit-Reset']
        
        print(f"Límite: {limit}")
        print(f"Restantes: {remaining}")
        print(f"Reset en: {reset_time}")

# Soluciones
# 1. Implementar rate limiting client-side
import time
from functools import wraps

class RateLimiter:
    def __init__(self, max_requests, time_window):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def is_allowed(self):
        now = time.time()
        # Limpiar requests antiguos
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False

# 2. Implementar exponential backoff
def exponential_backoff(func, max_retries=5):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    wait_time = 2 ** attempt
                    print(f"Rate limited. Esperando {wait_time} segundos...")
                    time.sleep(wait_time)
                else:
                    raise e
        raise Exception("Max retries exceeded")
    return wrapper

# 3. Usar múltiples API keys
class MultiAPIKeyManager:
    def __init__(self, api_keys):
        self.api_keys = api_keys
        self.current_key_index = 0
        self.key_limits = {key: RateLimiter(100, 3600) for key in api_keys}
    
    def get_available_key(self):
        for i, key in enumerate(self.api_keys):
            if self.key_limits[key].is_allowed():
                return key
        
        # Si no hay keys disponibles, esperar
        time.sleep(60)
        return self.get_available_key()
```

## 🔍 Herramientas de Diagnóstico

### Script de Diagnóstico Completo

```python
#!/usr/bin/env python3
# scripts/diagnostic.py

import os
import sys
import requests
import psutil
import subprocess
from datetime import datetime

class ClickUpBrainDiagnostic:
    def __init__(self):
        self.results = {}
        self.errors = []
    
    def run_full_diagnostic(self):
        """Ejecutar diagnóstico completo del sistema."""
        print("🔍 Iniciando diagnóstico de ClickUp Brain...")
        
        self.check_system_resources()
        self.check_database_connectivity()
        self.check_redis_connectivity()
        self.check_ai_services()
        self.check_external_apis()
        self.check_network_connectivity()
        self.check_logs()
        
        self.generate_report()
    
    def check_system_resources(self):
        """Verificar recursos del sistema."""
        print("📊 Verificando recursos del sistema...")
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        self.results['cpu_usage'] = cpu_percent
        
        # Memoria
        memory = psutil.virtual_memory()
        self.results['memory_usage'] = memory.percent
        self.results['memory_available'] = memory.available / 1024**3
        
        # Disco
        disk = psutil.disk_usage('/')
        self.results['disk_usage'] = disk.percent
        self.results['disk_free'] = disk.free / 1024**3
        
        # Verificar thresholds
        if cpu_percent > 80:
            self.errors.append(f"CPU usage alto: {cpu_percent}%")
        
        if memory.percent > 85:
            self.errors.append(f"Memoria usage alto: {memory.percent}%")
        
        if disk.percent > 90:
            self.errors.append(f"Disco usage alto: {disk.percent}%")
    
    def check_database_connectivity(self):
        """Verificar conectividad a base de datos."""
        print("🗄️ Verificando conectividad a base de datos...")
        
        try:
            from app.database import db
            from app.models import User
            
            # Test de conexión
            db.session.execute('SELECT 1')
            
            # Test de query
            user_count = User.query.count()
            
            self.results['database_status'] = 'healthy'
            self.results['user_count'] = user_count
            
        except Exception as e:
            self.results['database_status'] = 'error'
            self.errors.append(f"Error de base de datos: {str(e)}")
    
    def check_redis_connectivity(self):
        """Verificar conectividad a Redis."""
        print("🔴 Verificando conectividad a Redis...")
        
        try:
            import redis
            
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            
            # Test de operaciones básicas
            r.set('test_key', 'test_value', ex=10)
            value = r.get('test_key')
            r.delete('test_key')
            
            self.results['redis_status'] = 'healthy'
            
        except Exception as e:
            self.results['redis_status'] = 'error'
            self.errors.append(f"Error de Redis: {str(e)}")
    
    def check_ai_services(self):
        """Verificar servicios de AI."""
        print("🤖 Verificando servicios de AI...")
        
        ai_endpoints = [
            'http://localhost:8001/health',
            'http://localhost:8001/predict'
        ]
        
        for endpoint in ai_endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    self.results[f'ai_service_{endpoint.split("/")[-1]}'] = 'healthy'
                else:
                    self.results[f'ai_service_{endpoint.split("/")[-1]}'] = 'error'
                    self.errors.append(f"AI service error: {endpoint} - {response.status_code}")
            except Exception as e:
                self.results[f'ai_service_{endpoint.split("/")[-1]}'] = 'error'
                self.errors.append(f"AI service unreachable: {endpoint} - {str(e)}")
    
    def check_external_apis(self):
        """Verificar APIs externas."""
        print("🌐 Verificando APIs externas...")
        
        external_apis = [
            'https://api.openai.com/v1/models',
            'https://api.anthropic.com/v1/models'
        ]
        
        for api in external_apis:
            try:
                response = requests.get(api, timeout=10)
                if response.status_code == 200:
                    self.results[f'external_api_{api.split("//")[1].split("/")[0]}'] = 'healthy'
                else:
                    self.results[f'external_api_{api.split("//")[1].split("/")[0]}'] = 'error'
                    self.errors.append(f"External API error: {api} - {response.status_code}")
            except Exception as e:
                self.results[f'external_api_{api.split("//")[1].split("/")[0]}'] = 'error'
                self.errors.append(f"External API unreachable: {api} - {str(e)}")
    
    def check_network_connectivity(self):
        """Verificar conectividad de red."""
        print("🌐 Verificando conectividad de red...")
        
        # Verificar DNS
        try:
            import socket
            socket.gethostbyname('google.com')
            self.results['dns_resolution'] = 'healthy'
        except Exception as e:
            self.results['dns_resolution'] = 'error'
            self.errors.append(f"DNS resolution error: {str(e)}")
        
        # Verificar conectividad a internet
        try:
            response = requests.get('https://httpbin.org/ip', timeout=5)
            if response.status_code == 200:
                self.results['internet_connectivity'] = 'healthy'
                self.results['public_ip'] = response.json()['origin']
        except Exception as e:
            self.results['internet_connectivity'] = 'error'
            self.errors.append(f"Internet connectivity error: {str(e)}")
    
    def check_logs(self):
        """Verificar logs del sistema."""
        print("📝 Verificando logs del sistema...")
        
        log_files = [
            '/var/log/clickup-brain/app.log',
            '/var/log/clickup-brain/error.log'
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    # Verificar tamaño del log
                    size = os.path.getsize(log_file) / 1024**2  # MB
                    self.results[f'log_size_{os.path.basename(log_file)}'] = f"{size:.2f} MB"
                    
                    # Verificar errores recientes
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        recent_errors = [line for line in lines[-100:] if 'ERROR' in line]
                        self.results[f'recent_errors_{os.path.basename(log_file)}'] = len(recent_errors)
                        
                except Exception as e:
                    self.errors.append(f"Error reading log {log_file}: {str(e)}")
    
    def generate_report(self):
        """Generar reporte de diagnóstico."""
        print("\n" + "="*50)
        print("📋 REPORTE DE DIAGNÓSTICO")
        print("="*50)
        
        print(f"🕐 Timestamp: {datetime.now().isoformat()}")
        print(f"🖥️ Sistema: {os.uname().sysname} {os.uname().release}")
        
        print("\n📊 RECURSOS DEL SISTEMA:")
        print(f"  CPU Usage: {self.results.get('cpu_usage', 'N/A')}%")
        print(f"  Memory Usage: {self.results.get('memory_usage', 'N/A')}%")
        print(f"  Memory Available: {self.results.get('memory_available', 'N/A'):.2f} GB")
        print(f"  Disk Usage: {self.results.get('disk_usage', 'N/A')}%")
        print(f"  Disk Free: {self.results.get('disk_free', 'N/A'):.2f} GB")
        
        print("\n🔧 SERVICIOS:")
        print(f"  Database: {self.results.get('database_status', 'N/A')}")
        print(f"  Redis: {self.results.get('redis_status', 'N/A')}")
        print(f"  AI Services: {self.results.get('ai_service_health', 'N/A')}")
        
        print("\n🌐 CONECTIVIDAD:")
        print(f"  DNS Resolution: {self.results.get('dns_resolution', 'N/A')}")
        print(f"  Internet: {self.results.get('internet_connectivity', 'N/A')}")
        if 'public_ip' in self.results:
            print(f"  Public IP: {self.results['public_ip']}")
        
        if self.errors:
            print("\n❌ ERRORES ENCONTRADOS:")
            for error in self.errors:
                print(f"  • {error}")
        else:
            print("\n✅ No se encontraron errores críticos")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    diagnostic = ClickUpBrainDiagnostic()
    diagnostic.run_full_diagnostic()
```

### Script de Monitoreo en Tiempo Real

```python
#!/usr/bin/env python3
# scripts/monitor.py

import time
import psutil
import requests
from datetime import datetime
import json

class RealTimeMonitor:
    def __init__(self, interval=30):
        self.interval = interval
        self.metrics = []
    
    def start_monitoring(self):
        """Iniciar monitoreo en tiempo real."""
        print("🔍 Iniciando monitoreo en tiempo real...")
        print("Presiona Ctrl+C para detener")
        
        try:
            while True:
                metrics = self.collect_metrics()
                self.metrics.append(metrics)
                self.display_metrics(metrics)
                
                # Mantener solo últimos 100 registros
                if len(self.metrics) > 100:
                    self.metrics = self.metrics[-100:]
                
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoreo detenido")
            self.generate_summary()
    
    def collect_metrics(self):
        """Recolectar métricas del sistema."""
        timestamp = datetime.now()
        
        # Métricas del sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Métricas de la aplicación
        app_metrics = self.get_app_metrics()
        
        return {
            'timestamp': timestamp.isoformat(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / 1024**3,
            'disk_percent': disk.percent,
            'disk_free_gb': disk.free / 1024**3,
            'app_metrics': app_metrics
        }
    
    def get_app_metrics(self):
        """Obtener métricas de la aplicación."""
        try:
            response = requests.get('http://localhost:8000/metrics', timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return {}
    
    def display_metrics(self, metrics):
        """Mostrar métricas en consola."""
        timestamp = metrics['timestamp']
        cpu = metrics['cpu_percent']
        memory = metrics['memory_percent']
        disk = metrics['disk_percent']
        
        # Colores para alertas
        cpu_color = "🔴" if cpu > 80 else "🟡" if cpu > 60 else "🟢"
        memory_color = "🔴" if memory > 85 else "🟡" if memory > 70 else "🟢"
        disk_color = "🔴" if disk > 90 else "🟡" if disk > 80 else "🟢"
        
        print(f"\n🕐 {timestamp}")
        print(f"{cpu_color} CPU: {cpu:5.1f}% | {memory_color} Memory: {memory:5.1f}% | {disk_color} Disk: {disk:5.1f}%")
        
        if metrics['app_metrics']:
            app = metrics['app_metrics']
            print(f"📊 Requests/min: {app.get('requests_per_minute', 'N/A')} | Active users: {app.get('active_users', 'N/A')}")
    
    def generate_summary(self):
        """Generar resumen del monitoreo."""
        if not self.metrics:
            return
        
        print("\n📈 RESUMEN DEL MONITOREO:")
        print("="*40)
        
        # Estadísticas de CPU
        cpu_values = [m['cpu_percent'] for m in self.metrics]
        print(f"CPU - Promedio: {sum(cpu_values)/len(cpu_values):.1f}% | Máximo: {max(cpu_values):.1f}%")
        
        # Estadísticas de memoria
        memory_values = [m['memory_percent'] for m in self.metrics]
        print(f"Memory - Promedio: {sum(memory_values)/len(memory_values):.1f}% | Máximo: {max(memory_values):.1f}%")
        
        # Estadísticas de disco
        disk_values = [m['disk_percent'] for m in self.metrics]
        print(f"Disk - Promedio: {sum(disk_values)/len(disk_values):.1f}% | Máximo: {max(disk_values):.1f}%")
        
        # Alertas
        high_cpu = [m for m in self.metrics if m['cpu_percent'] > 80]
        high_memory = [m for m in self.metrics if m['memory_percent'] > 85]
        
        if high_cpu:
            print(f"⚠️ CPU alto detectado {len(high_cpu)} veces")
        if high_memory:
            print(f"⚠️ Memoria alta detectada {len(high_memory)} veces")

if __name__ == "__main__":
    monitor = RealTimeMonitor(interval=30)
    monitor.start_monitoring()
```

## 📞 Soporte y Escalación

### Matriz de Escalación

```yaml
escalation_matrix:
  level_1:
    description: "Soporte básico - 24/7"
    response_time: "1 hora"
    team: "Support Team"
    contact: "support@clickupbrain.ai"
    capabilities:
      - "Problemas básicos de configuración"
      - "Preguntas de uso"
      - "Problemas de conectividad simples"
  
  level_2:
    description: "Soporte técnico avanzado"
    response_time: "4 horas"
    team: "Technical Support"
    contact: "tech-support@clickupbrain.ai"
    capabilities:
      - "Problemas de integración"
      - "Problemas de performance"
      - "Configuración avanzada"
  
  level_3:
    description: "Soporte de arquitectura"
    response_time: "8 horas"
    team: "Engineering Team"
    contact: "engineering@clickupbrain.ai"
    capabilities:
      - "Problemas de arquitectura"
      - "Bugs críticos"
      - "Optimización de sistema"
  
  level_4:
    description: "Soporte ejecutivo"
    response_time: "2 horas"
    team: "Executive Team"
    contact: "executive-support@clickupbrain.ai"
    capabilities:
      - "Problemas críticos de negocio"
      - "Escalación de emergencia"
      - "SLA violations"
```

### Proceso de Reporte de Issues

```markdown
## Proceso de Reporte de Issues

### 1. Recopilar Información
- Descripción detallada del problema
- Pasos para reproducir
- Logs relevantes
- Configuración del entorno
- Impacto en el negocio

### 2. Clasificar Severidad
- **Critical**: Sistema completamente inoperativo
- **High**: Funcionalidad principal afectada
- **Medium**: Funcionalidad secundaria afectada
- **Low**: Problema menor o mejora

### 3. Crear Ticket
- Usar template de issue
- Incluir toda la información recopilada
- Asignar etiquetas apropiadas
- Establecer prioridad

### 4. Seguimiento
- Monitorear progreso del ticket
- Proporcionar información adicional si se solicita
- Confirmar resolución
- Documentar lecciones aprendidas
```

---

Esta guía de troubleshooting proporciona herramientas y procesos completos para diagnosticar y resolver problemas comunes en ClickUp Brain, asegurando un soporte efectivo y una resolución rápida de issues.



