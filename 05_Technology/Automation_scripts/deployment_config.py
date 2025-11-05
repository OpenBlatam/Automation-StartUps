#!/usr/bin/env python3
"""
Configuración de Despliegue y Gestión de Entornos para Neural Marketing Consciousness Platform
"""

import json
import os
import yaml
from typing import Dict, List, Optional, Any
from datetime import datetime

class DeploymentConfig:
    def __init__(self):
        self.environments = self.load_environment_configs()
        self.services = self.load_service_configs()
        self.infrastructure = self.load_infrastructure_configs()
    
    def load_environment_configs(self):
        """Cargar configuraciones de entornos"""
        return {
            'development': {
                'name': 'Development',
                'description': 'Entorno de desarrollo local',
                'url': 'http://localhost:3000',
                'api_url': 'http://localhost:8000',
                'database': {
                    'host': 'localhost',
                    'port': 5432,
                    'name': 'neural_marketing_dev',
                    'user': 'dev_user',
                    'password': 'dev_password'
                },
                'redis': {
                    'host': 'localhost',
                    'port': 6379,
                    'db': 0
                },
                'ai_models': {
                    'openai': {
                        'api_key': 'dev_openai_key',
                        'model': 'gpt-3.5-turbo',
                        'max_tokens': 1000
                    },
                    'claude': {
                        'api_key': 'dev_claude_key',
                        'model': 'claude-3-sonnet',
                        'max_tokens': 1000
                    }
                },
                'monitoring': {
                    'enabled': True,
                    'log_level': 'DEBUG',
                    'metrics_interval': 30
                },
                'security': {
                    'jwt_secret': 'dev_jwt_secret_key',
                    'encryption_key': 'dev_encryption_key',
                    'rate_limiting': {
                        'enabled': True,
                        'requests_per_minute': 1000
                    }
                }
            },
            'staging': {
                'name': 'Staging',
                'description': 'Entorno de pruebas y validación',
                'url': 'https://staging.neuralmarketing.com',
                'api_url': 'https://api-staging.neuralmarketing.com',
                'database': {
                    'host': 'staging-db.neuralmarketing.com',
                    'port': 5432,
                    'name': 'neural_marketing_staging',
                    'user': 'staging_user',
                    'password': 'staging_password'
                },
                'redis': {
                    'host': 'staging-redis.neuralmarketing.com',
                    'port': 6379,
                    'db': 0
                },
                'ai_models': {
                    'openai': {
                        'api_key': 'staging_openai_key',
                        'model': 'gpt-4',
                        'max_tokens': 2000
                    },
                    'claude': {
                        'api_key': 'staging_claude_key',
                        'model': 'claude-3-opus',
                        'max_tokens': 2000
                    }
                },
                'monitoring': {
                    'enabled': True,
                    'log_level': 'INFO',
                    'metrics_interval': 60
                },
                'security': {
                    'jwt_secret': 'staging_jwt_secret_key',
                    'encryption_key': 'staging_encryption_key',
                    'rate_limiting': {
                        'enabled': True,
                        'requests_per_minute': 500
                    }
                }
            },
            'production': {
                'name': 'Production',
                'description': 'Entorno de producción',
                'url': 'https://neuralmarketing.com',
                'api_url': 'https://api.neuralmarketing.com',
                'database': {
                    'host': 'prod-db-cluster.neuralmarketing.com',
                    'port': 5432,
                    'name': 'neural_marketing_prod',
                    'user': 'prod_user',
                    'password': 'prod_password'
                },
                'redis': {
                    'host': 'prod-redis-cluster.neuralmarketing.com',
                    'port': 6379,
                    'db': 0
                },
                'ai_models': {
                    'openai': {
                        'api_key': 'prod_openai_key',
                        'model': 'gpt-4',
                        'max_tokens': 4000
                    },
                    'claude': {
                        'api_key': 'prod_claude_key',
                        'model': 'claude-3-opus',
                        'max_tokens': 4000
                    },
                    'gemini': {
                        'api_key': 'prod_gemini_key',
                        'model': 'gemini-pro',
                        'max_tokens': 4000
                    }
                },
                'monitoring': {
                    'enabled': True,
                    'log_level': 'WARNING',
                    'metrics_interval': 30
                },
                'security': {
                    'jwt_secret': 'prod_jwt_secret_key',
                    'encryption_key': 'prod_encryption_key',
                    'rate_limiting': {
                        'enabled': True,
                        'requests_per_minute': 100
                    }
                }
            }
        }
    
    def load_service_configs(self):
        """Cargar configuraciones de servicios"""
        return {
            'frontend': {
                'name': 'Neural Marketing Frontend',
                'type': 'react',
                'port': 3000,
                'build_command': 'npm run build',
                'start_command': 'npm start',
                'dependencies': [
                    'react', 'next.js', 'typescript', 'tailwindcss',
                    'zustand', 'react-query', 'recharts'
                ],
                'environment_variables': [
                    'NEXT_PUBLIC_API_URL',
                    'NEXT_PUBLIC_APP_ENV',
                    'NEXT_PUBLIC_ANALYTICS_ID'
                ]
            },
            'backend': {
                'name': 'Neural Marketing Backend',
                'type': 'nodejs',
                'port': 8000,
                'build_command': 'npm run build',
                'start_command': 'npm start',
                'dependencies': [
                    'express', 'typescript', 'prisma', 'redis',
                    'jsonwebtoken', 'bcrypt', 'cors'
                ],
                'environment_variables': [
                    'DATABASE_URL', 'REDIS_URL', 'JWT_SECRET',
                    'OPENAI_API_KEY', 'CLAUDE_API_KEY'
                ]
            },
            'ai_service': {
                'name': 'AI Processing Service',
                'type': 'python',
                'port': 8001,
                'build_command': 'pip install -r requirements.txt',
                'start_command': 'python ai_service.py',
                'dependencies': [
                    'openai', 'anthropic', 'google-generativeai',
                    'transformers', 'torch', 'numpy'
                ],
                'environment_variables': [
                    'OPENAI_API_KEY', 'CLAUDE_API_KEY', 'GEMINI_API_KEY',
                    'AI_MODEL_CACHE_SIZE', 'AI_RATE_LIMIT'
                ]
            },
            'analytics_service': {
                'name': 'Analytics Service',
                'type': 'python',
                'port': 8002,
                'build_command': 'pip install -r requirements.txt',
                'start_command': 'python analytics_service.py',
                'dependencies': [
                    'pandas', 'numpy', 'scikit-learn', 'plotly',
                    'sqlalchemy', 'redis'
                ],
                'environment_variables': [
                    'DATABASE_URL', 'REDIS_URL', 'ANALYTICS_BATCH_SIZE'
                ]
            }
        }
    
    def load_infrastructure_configs(self):
        """Cargar configuraciones de infraestructura"""
        return {
            'kubernetes': {
                'namespace': 'neural-marketing',
                'replicas': {
                    'frontend': 3,
                    'backend': 5,
                    'ai_service': 3,
                    'analytics_service': 2
                },
                'resources': {
                    'frontend': {
                        'requests': {'cpu': '100m', 'memory': '256Mi'},
                        'limits': {'cpu': '500m', 'memory': '512Mi'}
                    },
                    'backend': {
                        'requests': {'cpu': '200m', 'memory': '512Mi'},
                        'limits': {'cpu': '1000m', 'memory': '1Gi'}
                    },
                    'ai_service': {
                        'requests': {'cpu': '500m', 'memory': '1Gi'},
                        'limits': {'cpu': '2000m', 'memory': '4Gi'}
                    }
                },
                'ingress': {
                    'host': 'neuralmarketing.com',
                    'tls': True,
                    'cert_manager': True
                }
            },
            'docker': {
                'base_images': {
                    'frontend': 'node:18-alpine',
                    'backend': 'node:18-alpine',
                    'ai_service': 'python:3.11-slim',
                    'analytics_service': 'python:3.11-slim'
                },
                'multi_stage_build': True,
                'optimization': {
                    'minify': True,
                    'tree_shaking': True,
                    'layer_caching': True
                }
            },
            'monitoring': {
                'prometheus': {
                    'enabled': True,
                    'port': 9090,
                    'retention': '30d'
                },
                'grafana': {
                    'enabled': True,
                    'port': 3001,
                    'dashboards': [
                        'neural-marketing-overview',
                        'ai-performance',
                        'user-engagement'
                    ]
                },
                'jaeger': {
                    'enabled': True,
                    'port': 16686,
                    'sampling_rate': 0.1
                }
            },
            'security': {
                'network_policies': True,
                'pod_security_standards': 'restricted',
                'rbac': True,
                'secrets_management': 'vault',
                'image_scanning': True
            }
        }
    
    def generate_environment_config(self, environment: str) -> Dict:
        """Generar configuración para un entorno específico"""
        if environment not in self.environments:
            raise ValueError(f"Environment {environment} not found")
        
        env_config = self.environments[environment]
        
        return {
            'environment': environment,
            'config': env_config,
            'services': self.services,
            'infrastructure': self.infrastructure,
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_docker_compose(self, environment: str = 'development') -> str:
        """Generar archivo docker-compose.yml"""
        env_config = self.environments[environment]
        
        compose = f"""version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV={environment}
      - NEXT_PUBLIC_API_URL={env_config['api_url']}
    depends_on:
      - backend
    networks:
      - neural-marketing

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV={environment}
      - DATABASE_URL=postgresql://{env_config['database']['user']}:{env_config['database']['password']}@{env_config['database']['host']}:{env_config['database']['port']}/{env_config['database']['name']}
      - REDIS_URL=redis://{env_config['redis']['host']}:{env_config['redis']['port']}
      - JWT_SECRET={env_config['security']['jwt_secret']}
      - OPENAI_API_KEY={env_config['ai_models']['openai']['api_key']}
      - CLAUDE_API_KEY={env_config['ai_models']['claude']['api_key']}
    depends_on:
      - postgres
      - redis
    networks:
      - neural-marketing

  ai-service:
    build:
      context: ./ai-service
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - OPENAI_API_KEY={env_config['ai_models']['openai']['api_key']}
      - CLAUDE_API_KEY={env_config['ai_models']['claude']['api_key']}
      - GEMINI_API_KEY={env_config['ai_models'].get('gemini', {}).get('api_key', '')}
    networks:
      - neural-marketing

  analytics-service:
    build:
      context: ./analytics-service
      dockerfile: Dockerfile
    ports:
      - "8002:8002"
    environment:
      - DATABASE_URL=postgresql://{env_config['database']['user']}:{env_config['database']['password']}@{env_config['database']['host']}:{env_config['database']['port']}/{env_config['database']['name']}
      - REDIS_URL=redis://{env_config['redis']['host']}:{env_config['redis']['port']}
    depends_on:
      - postgres
      - redis
    networks:
      - neural-marketing

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB={env_config['database']['name']}
      - POSTGRES_USER={env_config['database']['user']}
      - POSTGRES_PASSWORD={env_config['database']['password']}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - neural-marketing

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - neural-marketing

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    networks:
      - neural-marketing

volumes:
  postgres_data:
  redis_data:

networks:
  neural-marketing:
    driver: bridge
"""
        return compose
    
    def generate_kubernetes_manifests(self, environment: str = 'production') -> Dict[str, str]:
        """Generar manifiestos de Kubernetes"""
        env_config = self.environments[environment]
        infra_config = self.infrastructure['kubernetes']
        
        manifests = {}
        
        # Namespace
        manifests['namespace.yaml'] = f"""apiVersion: v1
kind: Namespace
metadata:
  name: {infra_config['namespace']}
  labels:
    app: neural-marketing
    environment: {environment}
"""
        
        # Frontend Deployment
        manifests['frontend-deployment.yaml'] = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: {infra_config['namespace']}
spec:
  replicas: {infra_config['replicas']['frontend']}
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: neural-marketing/frontend:latest
        ports:
        - containerPort: 3000
        resources:
          requests:
            cpu: {infra_config['resources']['frontend']['requests']['cpu']}
            memory: {infra_config['resources']['frontend']['requests']['memory']}
          limits:
            cpu: {infra_config['resources']['frontend']['limits']['cpu']}
            memory: {infra_config['resources']['frontend']['limits']['memory']}
        env:
        - name: NODE_ENV
          value: "{environment}"
        - name: NEXT_PUBLIC_API_URL
          value: "{env_config['api_url']}"
"""
        
        # Backend Deployment
        manifests['backend-deployment.yaml'] = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: {infra_config['namespace']}
spec:
  replicas: {infra_config['replicas']['backend']}
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: neural-marketing/backend:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: {infra_config['resources']['backend']['requests']['cpu']}
            memory: {infra_config['resources']['backend']['requests']['memory']}
          limits:
            cpu: {infra_config['resources']['backend']['limits']['cpu']}
            memory: {infra_config['resources']['backend']['limits']['memory']}
        env:
        - name: NODE_ENV
          value: "{environment}"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: jwt-secret
"""
        
        # Service
        manifests['services.yaml'] = f"""apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: {infra_config['namespace']}
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 3000
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: {infra_config['namespace']}
spec:
  selector:
    app: backend
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
"""
        
        # Ingress
        manifests['ingress.yaml'] = f"""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: neural-marketing-ingress
  namespace: {infra_config['namespace']}
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - {infra_config['ingress']['host']}
    secretName: neural-marketing-tls
  rules:
  - host: {infra_config['ingress']['host']}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
"""
        
        return manifests
    
    def generate_ci_cd_pipeline(self) -> str:
        """Generar pipeline de CI/CD"""
        return """name: Neural Marketing CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: neural-marketing

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: |
        cd frontend && npm ci
        cd ../backend && npm ci
    
    - name: Run tests
      run: |
        cd frontend && npm test
        cd ../backend && npm test
    
    - name: Run linting
      run: |
        cd frontend && npm run lint
        cd ../backend && npm run lint

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push frontend
      uses: docker/build-push-action@v4
      with:
        context: ./frontend
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:latest
    
    - name: Build and push backend
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Kubernetes
      uses: azure/k8s-deploy@v1
      with:
        manifests: |
          k8s/namespace.yaml
          k8s/frontend-deployment.yaml
          k8s/backend-deployment.yaml
          k8s/services.yaml
          k8s/ingress.yaml
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
"""
    
    def generate_monitoring_config(self) -> Dict[str, str]:
        """Generar configuraciones de monitoreo"""
        configs = {}
        
        # Prometheus Config
        configs['prometheus.yml'] = """global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "neural_marketing_rules.yml"

scrape_configs:
  - job_name: 'neural-marketing-backend'
    static_configs:
      - targets: ['backend-service:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'neural-marketing-ai-service'
    static_configs:
      - targets: ['ai-service:8001']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'neural-marketing-analytics'
    static_configs:
      - targets: ['analytics-service:8002']
    metrics_path: '/metrics'
    scrape_interval: 30s
"""
        
        # Grafana Dashboard
        configs['grafana-dashboard.json'] = json.dumps({
            "dashboard": {
                "title": "Neural Marketing Overview",
                "panels": [
                    {
                        "title": "API Response Time",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
                            }
                        ]
                    },
                    {
                        "title": "AI Model Performance",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(ai_model_processing_seconds_total[5m])"
                            }
                        ]
                    },
                    {
                        "title": "User Consciousness Levels",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "avg(consciousness_level)"
                            }
                        ]
                    }
                ]
            }
        }, indent=2)
        
        return configs
    
    def generate_environment_file(self, environment: str) -> str:
        """Generar archivo .env para un entorno"""
        env_config = self.environments[environment]
        
        env_content = f"""# Neural Marketing Environment Configuration
# Environment: {environment}
# Generated: {datetime.now().isoformat()}

# Application
NODE_ENV={environment}
APP_URL={env_config['url']}
API_URL={env_config['api_url']}

# Database
DATABASE_URL=postgresql://{env_config['database']['user']}:{env_config['database']['password']}@{env_config['database']['host']}:{env_config['database']['port']}/{env_config['database']['name']}

# Redis
REDIS_URL=redis://{env_config['redis']['host']}:{env_config['redis']['port']}

# Security
JWT_SECRET={env_config['security']['jwt_secret']}
ENCRYPTION_KEY={env_config['security']['encryption_key']}

# AI Models
OPENAI_API_KEY={env_config['ai_models']['openai']['api_key']}
CLAUDE_API_KEY={env_config['ai_models']['claude']['api_key']}
"""
        
        if 'gemini' in env_config['ai_models']:
            env_content += f"GEMINI_API_KEY={env_config['ai_models']['gemini']['api_key']}\n"
        
        env_content += f"""
# Monitoring
LOG_LEVEL={env_config['monitoring']['log_level']}
METRICS_ENABLED={str(env_config['monitoring']['enabled']).lower()}
METRICS_INTERVAL={env_config['monitoring']['metrics_interval']}

# Rate Limiting
RATE_LIMIT_ENABLED={str(env_config['security']['rate_limiting']['enabled']).lower()}
RATE_LIMIT_RPM={env_config['security']['rate_limiting']['requests_per_minute']}
"""
        
        return env_content

def main():
    deployment = DeploymentConfig()
    
    print("🚀 Configuración de Despliegue - Neural Marketing Platform")
    print("=" * 60)
    print("1. Generar configuración de entorno")
    print("2. Generar docker-compose")
    print("3. Generar manifiestos de Kubernetes")
    print("4. Generar pipeline de CI/CD")
    print("5. Generar configuración de monitoreo")
    print("6. Generar archivo .env")
    print("7. Generar todas las configuraciones")
    print("8. Salir")
    
    while True:
        choice = input("\nSeleccione una opción (1-8): ").strip()
        
        if choice == '1':
            environment = input("Entorno (development/staging/production): ").strip() or 'development'
            config = deployment.generate_environment_config(environment)
            
            filename = f"config_{environment}.json"
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Configuración generada: {filename}")
        
        elif choice == '2':
            environment = input("Entorno (development/staging/production): ").strip() or 'development'
            compose = deployment.generate_docker_compose(environment)
            
            filename = f"docker-compose_{environment}.yml"
            with open(filename, 'w') as f:
                f.write(compose)
            
            print(f"✅ Docker Compose generado: {filename}")
        
        elif choice == '3':
            environment = input("Entorno (development/staging/production): ").strip() or 'production'
            manifests = deployment.generate_kubernetes_manifests(environment)
            
            os.makedirs('k8s', exist_ok=True)
            for filename, content in manifests.items():
                with open(f'k8s/{filename}', 'w') as f:
                    f.write(content)
            
            print(f"✅ Manifiestos de Kubernetes generados en k8s/")
        
        elif choice == '4':
            pipeline = deployment.generate_ci_cd_pipeline()
            
            with open('.github/workflows/ci-cd.yml', 'w') as f:
                os.makedirs('.github/workflows', exist_ok=True)
                f.write(pipeline)
            
            print("✅ Pipeline de CI/CD generado: .github/workflows/ci-cd.yml")
        
        elif choice == '5':
            monitoring_configs = deployment.generate_monitoring_config()
            
            os.makedirs('monitoring', exist_ok=True)
            for filename, content in monitoring_configs.items():
                with open(f'monitoring/{filename}', 'w') as f:
                    f.write(content)
            
            print("✅ Configuraciones de monitoreo generadas en monitoring/")
        
        elif choice == '6':
            environment = input("Entorno (development/staging/production): ").strip() or 'development'
            env_content = deployment.generate_environment_file(environment)
            
            filename = f".env.{environment}"
            with open(filename, 'w') as f:
                f.write(env_content)
            
            print(f"✅ Archivo .env generado: {filename}")
        
        elif choice == '7':
            print("🚀 Generando todas las configuraciones...")
            
            # Generar configuraciones para todos los entornos
            for env in ['development', 'staging', 'production']:
                print(f"\n📁 Generando configuraciones para {env}...")
                
                # Configuración de entorno
                config = deployment.generate_environment_config(env)
                with open(f"config_{env}.json", 'w') as f:
                    json.dump(config, f, indent=2)
                
                # Docker Compose
                compose = deployment.generate_docker_compose(env)
                with open(f"docker-compose_{env}.yml", 'w') as f:
                    f.write(compose)
                
                # Archivo .env
                env_content = deployment.generate_environment_file(env)
                with open(f".env.{env}", 'w') as f:
                    f.write(env_content)
            
            # Generar manifiestos de Kubernetes
            manifests = deployment.generate_kubernetes_manifests('production')
            os.makedirs('k8s', exist_ok=True)
            for filename, content in manifests.items():
                with open(f'k8s/{filename}', 'w') as f:
                    f.write(content)
            
            # Generar pipeline de CI/CD
            pipeline = deployment.generate_ci_cd_pipeline()
            os.makedirs('.github/workflows', exist_ok=True)
            with open('.github/workflows/ci-cd.yml', 'w') as f:
                f.write(pipeline)
            
            # Generar configuraciones de monitoreo
            monitoring_configs = deployment.generate_monitoring_config()
            os.makedirs('monitoring', exist_ok=True)
            for filename, content in monitoring_configs.items():
                with open(f'monitoring/{filename}', 'w') as f:
                    f.write(content)
            
            print("\n✅ Todas las configuraciones generadas exitosamente!")
            print("📁 Archivos creados:")
            print("   • config_*.json (configuraciones de entorno)")
            print("   • docker-compose_*.yml (configuraciones Docker)")
            print("   • .env.* (archivos de entorno)")
            print("   • k8s/ (manifiestos de Kubernetes)")
            print("   • .github/workflows/ (pipeline de CI/CD)")
            print("   • monitoring/ (configuraciones de monitoreo)")
        
        elif choice == '8':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()


