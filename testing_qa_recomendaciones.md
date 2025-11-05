---
title: "Testing Qa Recomendaciones"
category: "testing_qa_recomendaciones.md"
tags: []
created: "2025-10-29"
path: "testing_qa_recomendaciones.md"
---

# 🧪 **TESTING Y QA - SISTEMA DE RECOMENDACIONES**

## **ÍNDICE**
1. [Estrategia de Testing](#estrategia)
2. [Testing Unitario](#unitario)
3. [Testing de Integración](#integracion)
4. [Testing de Performance](#performance)
5. [Testing de Usuario](#usuario)
6. [Testing de Seguridad](#seguridad)
7. [Testing de Datos](#datos)
8. [Testing A/B](#ab)
9. [Automatización](#automatizacion)
10. [Monitoreo de Calidad](#monitoreo)
11. [Mejores Prácticas](#mejores)
12. [Troubleshooting](#troubleshooting)

---

## **1. ESTRATEGIA DE TESTING** {#estrategia}

### **Pirámide de Testing**
```python
# Estrategia de testing para recomendaciones
class TestingStrategy:
    def __init__(self):
        self.testing_pyramid = {
            'unit_tests': {
                'percentage': 70,
                'focus': 'Algoritmos individuales, funciones puras',
                'tools': ['pytest', 'unittest', 'nose2']
            },
            'integration_tests': {
                'percentage': 20,
                'focus': 'Interacción entre servicios, APIs',
                'tools': ['pytest', 'requests', 'testcontainers']
            },
            'e2e_tests': {
                'percentage': 10,
                'focus': 'Flujos completos, experiencia de usuario',
                'tools': ['selenium', 'playwright', 'cypress']
            }
        }
        
        self.testing_types = {
            'functional': ['unit', 'integration', 'e2e'],
            'non_functional': ['performance', 'security', 'usability'],
            'specialized': ['recommendation_quality', 'a_b_testing', 'data_validation']
        }
    
    def create_test_plan(self, feature):
        """Crear plan de testing para una funcionalidad"""
        test_plan = {
            'feature': feature,
            'test_cases': [],
            'test_data': [],
            'environments': ['dev', 'staging', 'prod'],
            'timeline': '2 weeks'
        }
        
        # Agregar casos de prueba específicos
        if feature == 'collaborative_filtering':
            test_plan['test_cases'].extend([
                'test_user_similarity_calculation',
                'test_recommendation_generation',
                'test_cold_start_handling',
                'test_sparse_data_handling'
            ])
        
        return test_plan
```

### **Criterios de Aceptación**
```python
# Criterios de aceptación para recomendaciones
class AcceptanceCriteria:
    def __init__(self):
        self.criteria = {
            'recommendation_quality': {
                'precision_at_5': 0.15,  # 15% de precisión en top 5
                'recall_at_10': 0.25,   # 25% de recall en top 10
                'diversity_score': 0.7,  # 70% de diversidad
                'novelty_score': 0.6    # 60% de novedad
            },
            'performance': {
                'response_time_p95': 2.0,  # 95% de respuestas < 2s
                'throughput': 1000,        # 1000 req/s
                'availability': 0.999      # 99.9% de disponibilidad
            },
            'usability': {
                'click_through_rate': 0.05,  # 5% CTR
                'conversion_rate': 0.02,     # 2% conversión
                'user_satisfaction': 4.0     # 4/5 satisfacción
            }
        }
    
    def validate_recommendations(self, recommendations, user_id):
        """Validar calidad de recomendaciones"""
        validation_results = {}
        
        # Validar precisión
        validation_results['precision'] = self.calculate_precision(
            recommendations, user_id
        )
        
        # Validar diversidad
        validation_results['diversity'] = self.calculate_diversity(
            recommendations
        )
        
        # Validar novedad
        validation_results['novelty'] = self.calculate_novelty(
            recommendations, user_id
        )
        
        return validation_results
```

---

## **2. TESTING UNITARIO** {#unitario}

### **Tests para Algoritmos de Recomendación**
```python
# Tests unitarios para algoritmos
import pytest
import numpy as np
from unittest.mock import Mock, patch

class TestRecommendationAlgorithms:
    def setup_method(self):
        """Configurar datos de prueba"""
        self.sample_data = {
            'user_item_matrix': np.array([
                [5, 3, 0, 1],
                [4, 0, 0, 1],
                [1, 1, 0, 5],
                [1, 0, 0, 4],
                [0, 1, 5, 4]
            ]),
            'user_id': 1,
            'expected_recommendations': [2, 3]
        }
    
    def test_collaborative_filtering(self):
        """Test filtrado colaborativo"""
        from recommendation_engine import CollaborativeFiltering
        
        cf = CollaborativeFiltering()
        recommendations = cf.get_recommendations(
            self.sample_data['user_item_matrix'],
            self.sample_data['user_id'],
            n_recommendations=2
        )
        
        assert len(recommendations) == 2
        assert recommendations[0] in self.sample_data['expected_recommendations']
        assert recommendations[1] in self.sample_data['expected_recommendations']
    
    def test_content_based_filtering(self):
        """Test filtrado basado en contenido"""
        from recommendation_engine import ContentBasedFiltering
        
        cb = ContentBasedFiltering()
        user_profile = np.array([0.5, 0.3, 0.2])
        item_features = np.array([
            [0.8, 0.1, 0.1],
            [0.2, 0.6, 0.2],
            [0.1, 0.1, 0.8]
        ])
        
        recommendations = cb.get_recommendations(
            user_profile, item_features, n_recommendations=2
        )
        
        assert len(recommendations) == 2
        assert all(0 <= rec < len(item_features) for rec in recommendations)
    
    def test_hybrid_recommendation(self):
        """Test recomendación híbrida"""
        from recommendation_engine import HybridRecommendation
        
        hybrid = HybridRecommendation()
        recommendations = hybrid.get_recommendations(
            user_id=self.sample_data['user_id'],
            n_recommendations=3
        )
        
        assert len(recommendations) == 3
        assert all(isinstance(rec, dict) for rec in recommendations)
        assert all('item_id' in rec for rec in recommendations)
        assert all('score' in rec for rec in recommendations)
    
    def test_cold_start_handling(self):
        """Test manejo de cold start"""
        from recommendation_engine import RecommendationEngine
        
        engine = RecommendationEngine()
        
        # Usuario nuevo sin historial
        new_user_recommendations = engine.get_recommendations(
            user_id='new_user',
            n_recommendations=5
        )
        
        assert len(new_user_recommendations) == 5
        assert all(rec['score'] > 0 for rec in new_user_recommendations)
    
    def test_sparse_data_handling(self):
        """Test manejo de datos dispersos"""
        from recommendation_engine import CollaborativeFiltering
        
        cf = CollaborativeFiltering()
        
        # Matriz muy dispersa
        sparse_matrix = np.array([
            [5, 0, 0, 0, 0],
            [0, 4, 0, 0, 0],
            [0, 0, 3, 0, 0],
            [0, 0, 0, 2, 0],
            [0, 0, 0, 0, 1]
        ])
        
        recommendations = cf.get_recommendations(
            sparse_matrix, user_id=0, n_recommendations=3
        )
        
        assert len(recommendations) == 3
        assert all(0 <= rec < sparse_matrix.shape[1] for rec in recommendations)
```

### **Tests para Validación de Datos**
```python
# Tests para validación de datos
class TestDataValidation:
    def test_user_data_validation(self):
        """Test validación de datos de usuario"""
        from data_validator import UserDataValidator
        
        validator = UserDataValidator()
        
        # Datos válidos
        valid_data = {
            'user_id': 'user123',
            'age': 25,
            'gender': 'M',
            'preferences': ['action', 'comedy']
        }
        
        assert validator.validate(valid_data) == True
        
        # Datos inválidos
        invalid_data = {
            'user_id': '',  # ID vacío
            'age': -5,      # Edad negativa
            'gender': 'X',  # Género inválido
            'preferences': []  # Preferencias vacías
        }
        
        assert validator.validate(invalid_data) == False
    
    def test_product_data_validation(self):
        """Test validación de datos de producto"""
        from data_validator import ProductDataValidator
        
        validator = ProductDataValidator()
        
        # Producto válido
        valid_product = {
            'product_id': 'prod123',
            'title': 'Product Title',
            'category': 'Electronics',
            'price': 99.99,
            'availability': True
        }
        
        assert validator.validate(valid_product) == True
        
        # Producto inválido
        invalid_product = {
            'product_id': '',  # ID vacío
            'title': '',       # Título vacío
            'category': '',    # Categoría vacía
            'price': -10.0,    # Precio negativo
            'availability': None  # Disponibilidad nula
        }
        
        assert validator.validate(invalid_product) == False
```

---

## **3. TESTING DE INTEGRACIÓN** {#integracion}

### **Tests de API**
```python
# Tests de integración para APIs
import requests
import json

class TestRecommendationAPI:
    def setup_method(self):
        """Configurar cliente de API"""
        self.base_url = 'http://localhost:5000/api/v1'
        self.headers = {'Content-Type': 'application/json'}
    
    def test_get_recommendations(self):
        """Test obtener recomendaciones"""
        response = requests.get(
            f'{self.base_url}/recommendations/user123',
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'recommendations' in data
        assert 'user_id' in data
        assert 'timestamp' in data
        assert len(data['recommendations']) > 0
    
    def test_get_recommendations_with_context(self):
        """Test obtener recomendaciones con contexto"""
        context = {
            'current_product': 'prod456',
            'category': 'electronics',
            'price_range': [50, 200]
        }
        
        response = requests.get(
            f'{self.base_url}/recommendations/user123',
            params={'context': json.dumps(context)},
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que las recomendaciones son relevantes al contexto
        recommendations = data['recommendations']
        assert all(rec['category'] == 'electronics' for rec in recommendations)
    
    def test_batch_recommendations(self):
        """Test recomendaciones en lote"""
        user_ids = ['user1', 'user2', 'user3']
        
        response = requests.post(
            f'{self.base_url}/recommendations/batch',
            json={'user_ids': user_ids},
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'results' in data
        assert len(data['results']) == len(user_ids)
        assert all('recommendations' in result for result in data['results'])
    
    def test_recommendation_quality_metrics(self):
        """Test métricas de calidad de recomendaciones"""
        response = requests.get(
            f'{self.base_url}/recommendations/user123/metrics',
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'precision' in data
        assert 'recall' in data
        assert 'diversity' in data
        assert 'novelty' in data
        
        # Verificar que las métricas están en rango válido
        assert 0 <= data['precision'] <= 1
        assert 0 <= data['recall'] <= 1
        assert 0 <= data['diversity'] <= 1
        assert 0 <= data['novelty'] <= 1
```

### **Tests de Base de Datos**
```python
# Tests de integración con base de datos
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class TestDatabaseIntegration:
    def setup_method(self):
        """Configurar base de datos de prueba"""
        self.engine = create_engine('sqlite:///:memory:')
        self.Session = sessionmaker(bind=self.engine)
        self.create_tables()
    
    def test_user_data_persistence(self):
        """Test persistencia de datos de usuario"""
        from models import User, UserInteraction
        
        session = self.Session()
        
        # Crear usuario
        user = User(
            user_id='test_user',
            age=25,
            gender='M',
            preferences=['action', 'comedy']
        )
        session.add(user)
        
        # Crear interacción
        interaction = UserInteraction(
            user_id='test_user',
            product_id='prod123',
            action='view',
            rating=5
        )
        session.add(interaction)
        
        session.commit()
        
        # Verificar persistencia
        saved_user = session.query(User).filter_by(user_id='test_user').first()
        assert saved_user is not None
        assert saved_user.age == 25
        
        saved_interaction = session.query(UserInteraction).filter_by(
            user_id='test_user'
        ).first()
        assert saved_interaction is not None
        assert saved_interaction.rating == 5
    
    def test_recommendation_generation_with_db(self):
        """Test generación de recomendaciones con base de datos"""
        from recommendation_engine import RecommendationEngine
        from models import User, UserInteraction
        
        # Crear datos de prueba
        session = self.Session()
        
        # Usuarios
        users = [
            User(user_id='user1', age=25, gender='M'),
            User(user_id='user2', age=30, gender='F'),
            User(user_id='user3', age=35, gender='M')
        ]
        session.add_all(users)
        
        # Interacciones
        interactions = [
            UserInteraction(user_id='user1', product_id='prod1', rating=5),
            UserInteraction(user_id='user1', product_id='prod2', rating=4),
            UserInteraction(user_id='user2', product_id='prod1', rating=3),
            UserInteraction(user_id='user2', product_id='prod3', rating=5),
            UserInteraction(user_id='user3', product_id='prod2', rating=4),
            UserInteraction(user_id='user3', product_id='prod3', rating=5)
        ]
        session.add_all(interactions)
        session.commit()
        
        # Generar recomendaciones
        engine = RecommendationEngine(session)
        recommendations = engine.get_recommendations('user1', n_recommendations=2)
        
        assert len(recommendations) == 2
        assert all('product_id' in rec for rec in recommendations)
        assert all('score' in rec for rec in recommendations)
```

---

## **4. TESTING DE PERFORMANCE** {#performance}

### **Tests de Carga**
```python
# Tests de performance y carga
import time
import concurrent.futures
from locust import HttpUser, task, between

class RecommendationLoadTest(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Configurar usuario de prueba"""
        self.user_id = f"test_user_{self.client.user_id}"
        self.headers = {'Content-Type': 'application/json'}
    
    @task(3)
    def test_get_recommendations(self):
        """Test obtener recomendaciones"""
        response = self.client.get(
            f'/api/v1/recommendations/{self.user_id}',
            headers=self.headers
        )
        
        assert response.status_code == 200
        assert response.elapsed.total_seconds() < 2.0  # < 2 segundos
    
    @task(1)
    def test_batch_recommendations(self):
        """Test recomendaciones en lote"""
        user_ids = [f"user_{i}" for i in range(10)]
        
        response = self.client.post(
            '/api/v1/recommendations/batch',
            json={'user_ids': user_ids},
            headers=self.headers
        )
        
        assert response.status_code == 200
        assert response.elapsed.total_seconds() < 5.0  # < 5 segundos
    
    @task(1)
    def test_recommendation_metrics(self):
        """Test métricas de recomendaciones"""
        response = self.client.get(
            f'/api/v1/recommendations/{self.user_id}/metrics',
            headers=self.headers
        )
        
        assert response.status_code == 200
        assert response.elapsed.total_seconds() < 1.0  # < 1 segundo
```

### **Tests de Estrés**
```python
# Tests de estrés para recomendaciones
class StressTestRecommendations:
    def __init__(self):
        self.base_url = 'http://localhost:5000/api/v1'
        self.results = []
    
    def test_concurrent_requests(self, num_requests=1000, max_workers=50):
        """Test requests concurrentes"""
        import requests
        from concurrent.futures import ThreadPoolExecutor
        
        def make_request(user_id):
            start_time = time.time()
            response = requests.get(f'{self.base_url}/recommendations/{user_id}')
            end_time = time.time()
            
            return {
                'user_id': user_id,
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'success': response.status_code == 200
            }
        
        # Ejecutar requests concurrentes
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            user_ids = [f'user_{i}' for i in range(num_requests)]
            futures = [executor.submit(make_request, user_id) for user_id in user_ids]
            results = [future.result() for future in futures]
        
        # Analizar resultados
        self.analyze_stress_results(results)
        return results
    
    def analyze_stress_results(self, results):
        """Analizar resultados del test de estrés"""
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r['success'])
        response_times = [r['response_time'] for r in results]
        
        success_rate = successful_requests / total_requests
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        p95_response_time = sorted(response_times)[int(0.95 * len(response_times))]
        
        print(f"Total requests: {total_requests}")
        print(f"Success rate: {success_rate:.2%}")
        print(f"Average response time: {avg_response_time:.2f}s")
        print(f"Max response time: {max_response_time:.2f}s")
        print(f"95th percentile: {p95_response_time:.2f}s")
        
        # Verificar criterios de aceptación
        assert success_rate >= 0.95, f"Success rate {success_rate:.2%} below 95%"
        assert p95_response_time <= 2.0, f"95th percentile {p95_response_time:.2f}s above 2s"
```

---

## **5. TESTING DE USUARIO** {#usuario}

### **Tests de Usabilidad**
```python
# Tests de usabilidad para recomendaciones
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class UsabilityTestRecommendations:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
    
    def test_recommendation_display(self):
        """Test visualización de recomendaciones"""
        # Navegar a página de recomendaciones
        self.driver.get('http://localhost:3000/recommendations')
        
        # Verificar que las recomendaciones se muestran
        recommendations = self.wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'recommendation-item'))
        )
        
        assert len(recommendations) > 0, "No recommendations displayed"
        
        # Verificar que cada recomendación tiene elementos requeridos
        for rec in recommendations:
            assert rec.find_element(By.CLASS_NAME, 'product-title'), "Missing product title"
            assert rec.find_element(By.CLASS_NAME, 'product-price'), "Missing product price"
            assert rec.find_element(By.CLASS_NAME, 'product-image'), "Missing product image"
    
    def test_recommendation_interaction(self):
        """Test interacción con recomendaciones"""
        # Navegar a página de recomendaciones
        self.driver.get('http://localhost:3000/recommendations')
        
        # Hacer clic en primera recomendación
        first_recommendation = self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'recommendation-item'))
        )
        first_recommendation.click()
        
        # Verificar que se navega a página del producto
        assert 'product' in self.driver.current_url, "Did not navigate to product page"
        
        # Verificar que se registra la interacción
        # (Esto requeriría verificar en base de datos o logs)
    
    def test_recommendation_refresh(self):
        """Test actualización de recomendaciones"""
        # Navegar a página de recomendaciones
        self.driver.get('http://localhost:3000/recommendations')
        
        # Obtener recomendaciones iniciales
        initial_recommendations = self.driver.find_elements(By.CLASS_NAME, 'recommendation-item')
        initial_titles = [rec.find_element(By.CLASS_NAME, 'product-title').text for rec in initial_recommendations]
        
        # Hacer clic en botón de actualizar
        refresh_button = self.driver.find_element(By.ID, 'refresh-recommendations')
        refresh_button.click()
        
        # Esperar a que se actualicen las recomendaciones
        self.wait.until(lambda driver: len(driver.find_elements(By.CLASS_NAME, 'recommendation-item')) > 0)
        
        # Verificar que las recomendaciones han cambiado
        updated_recommendations = self.driver.find_elements(By.CLASS_NAME, 'recommendation-item')
        updated_titles = [rec.find_element(By.CLASS_NAME, 'product-title').text for rec in updated_recommendations]
        
        # Al menos algunas recomendaciones deberían ser diferentes
        assert not all(title in initial_titles for title in updated_titles), "Recommendations did not refresh"
    
    def test_mobile_responsiveness(self):
        """Test responsividad móvil"""
        # Configurar tamaño de pantalla móvil
        self.driver.set_window_size(375, 667)  # iPhone 6/7/8
        
        # Navegar a página de recomendaciones
        self.driver.get('http://localhost:3000/recommendations')
        
        # Verificar que las recomendaciones se muestran correctamente
        recommendations = self.driver.find_elements(By.CLASS_NAME, 'recommendation-item')
        
        for rec in recommendations:
            # Verificar que el elemento es visible
            assert rec.is_displayed(), "Recommendation not visible on mobile"
            
            # Verificar que el texto es legible
            title = rec.find_element(By.CLASS_NAME, 'product-title')
            assert title.is_displayed(), "Product title not visible on mobile"
            
            # Verificar que el botón es clickeable
            button = rec.find_element(By.CLASS_NAME, 'recommendation-button')
            assert button.is_displayed(), "Recommendation button not visible on mobile"
```

---

## **6. TESTING DE SEGURIDAD** {#seguridad}

### **Tests de Seguridad de API**
```python
# Tests de seguridad para APIs de recomendaciones
import requests
import json

class SecurityTestRecommendations:
    def __init__(self):
        self.base_url = 'http://localhost:5000/api/v1'
        self.headers = {'Content-Type': 'application/json'}
    
    def test_authentication_required(self):
        """Test que se requiere autenticación"""
        response = requests.get(f'{self.base_url}/recommendations/user123')
        
        # Debería requerir autenticación
        assert response.status_code == 401, "API should require authentication"
    
    def test_authorization_bypass(self):
        """Test intento de bypass de autorización"""
        # Intentar acceder a recomendaciones de otro usuario
        headers = {'Authorization': 'Bearer valid_token_user1'}
        response = requests.get(
            f'{self.base_url}/recommendations/user2',
            headers=headers
        )
        
        # Debería ser rechazado
        assert response.status_code == 403, "Should not access other user's recommendations"
    
    def test_sql_injection(self):
        """Test inyección SQL"""
        malicious_user_id = "user123'; DROP TABLE users; --"
        
        response = requests.get(
            f'{self.base_url}/recommendations/{malicious_user_id}',
            headers=self.headers
        )
        
        # Debería manejar la entrada maliciosa sin fallar
        assert response.status_code in [400, 404], "Should handle SQL injection attempt"
    
    def test_xss_protection(self):
        """Test protección XSS"""
        malicious_user_id = "<script>alert('XSS')</script>"
        
        response = requests.get(
            f'{self.base_url}/recommendations/{malicious_user_id}',
            headers=self.headers
        )
        
        # Debería escapar el contenido malicioso
        assert response.status_code in [400, 404], "Should handle XSS attempt"
    
    def test_rate_limiting(self):
        """Test límites de velocidad"""
        # Hacer muchas requests rápidamente
        for i in range(100):
            response = requests.get(
                f'{self.base_url}/recommendations/user123',
                headers=self.headers
            )
            
            if response.status_code == 429:  # Too Many Requests
                break
        
        # Debería activar rate limiting
        assert response.status_code == 429, "Should implement rate limiting"
    
    def test_data_validation(self):
        """Test validación de datos"""
        # Enviar datos maliciosos
        malicious_data = {
            'user_id': None,
            'n_recommendations': -1,
            'context': {'malicious': '<script>alert("XSS")</script>'}
        }
        
        response = requests.post(
            f'{self.base_url}/recommendations/batch',
            json=malicious_data,
            headers=self.headers
        )
        
        # Debería rechazar datos maliciosos
        assert response.status_code == 400, "Should reject malicious data"
```

---

## **7. TESTING DE DATOS** {#datos}

### **Tests de Calidad de Datos**
```python
# Tests de calidad de datos para recomendaciones
import pandas as pd
import numpy as np

class DataQualityTestRecommendations:
    def __init__(self):
        self.data_validator = DataValidator()
        self.quality_metrics = QualityMetrics()
    
    def test_data_completeness(self):
        """Test completitud de datos"""
        # Cargar datos de prueba
        user_data = pd.read_csv('test_data/users.csv')
        interaction_data = pd.read_csv('test_data/interactions.csv')
        product_data = pd.read_csv('test_data/products.csv')
        
        # Verificar completitud de datos de usuario
        user_completeness = self.data_validator.check_completeness(
            user_data, required_columns=['user_id', 'age', 'gender']
        )
        assert user_completeness > 0.95, f"User data completeness {user_completeness:.2%} below 95%"
        
        # Verificar completitud de datos de interacción
        interaction_completeness = self.data_validator.check_completeness(
            interaction_data, required_columns=['user_id', 'product_id', 'rating']
        )
        assert interaction_completeness > 0.98, f"Interaction data completeness {interaction_completeness:.2%} below 98%"
        
        # Verificar completitud de datos de producto
        product_completeness = self.data_validator.check_completeness(
            product_data, required_columns=['product_id', 'title', 'category', 'price']
        )
        assert product_completeness > 0.99, f"Product data completeness {product_completeness:.2%} below 99%"
    
    def test_data_consistency(self):
        """Test consistencia de datos"""
        # Verificar consistencia de IDs
        user_ids = set(pd.read_csv('test_data/users.csv')['user_id'])
        interaction_user_ids = set(pd.read_csv('test_data/interactions.csv')['user_id'])
        
        # Todos los user_ids en interacciones deben existir en usuarios
        orphaned_users = interaction_user_ids - user_ids
        assert len(orphaned_users) == 0, f"Found {len(orphaned_users)} orphaned user IDs"
        
        # Verificar consistencia de ratings
        interaction_data = pd.read_csv('test_data/interactions.csv')
        valid_ratings = interaction_data['rating'].between(1, 5)
        assert valid_ratings.all(), "Found invalid ratings outside 1-5 range"
    
    def test_data_accuracy(self):
        """Test precisión de datos"""
        # Verificar que los precios son positivos
        product_data = pd.read_csv('test_data/products.csv')
        assert (product_data['price'] > 0).all(), "Found non-positive prices"
        
        # Verificar que las edades son razonables
        user_data = pd.read_csv('test_data/users.csv')
        valid_ages = user_data['age'].between(13, 120)
        assert valid_ages.all(), "Found invalid ages outside 13-120 range"
        
        # Verificar que los géneros son válidos
        valid_genders = user_data['gender'].isin(['M', 'F', 'Other', 'Prefer not to say'])
        assert valid_genders.all(), "Found invalid gender values"
    
    def test_data_freshness(self):
        """Test frescura de datos"""
        # Verificar que los datos no son demasiado antiguos
        interaction_data = pd.read_csv('test_data/interactions.csv')
        interaction_data['timestamp'] = pd.to_datetime(interaction_data['timestamp'])
        
        max_age_days = 365  # 1 año
        current_time = pd.Timestamp.now()
        data_age = (current_time - interaction_data['timestamp'].max()).days
        
        assert data_age <= max_age_days, f"Data is {data_age} days old, exceeds {max_age_days} days"
    
    def test_recommendation_quality_metrics(self):
        """Test métricas de calidad de recomendaciones"""
        # Generar recomendaciones de prueba
        recommendations = self.generate_test_recommendations()
        
        # Calcular métricas de calidad
        precision = self.quality_metrics.calculate_precision(recommendations)
        recall = self.quality_metrics.calculate_recall(recommendations)
        diversity = self.quality_metrics.calculate_diversity(recommendations)
        novelty = self.quality_metrics.calculate_novelty(recommendations)
        
        # Verificar que las métricas están en rango válido
        assert 0 <= precision <= 1, f"Precision {precision:.3f} outside valid range"
        assert 0 <= recall <= 1, f"Recall {recall:.3f} outside valid range"
        assert 0 <= diversity <= 1, f"Diversity {diversity:.3f} outside valid range"
        assert 0 <= novelty <= 1, f"Novelty {novelty:.3f} outside valid range"
        
        # Verificar que las métricas cumplen criterios mínimos
        assert precision >= 0.15, f"Precision {precision:.3f} below minimum 0.15"
        assert recall >= 0.25, f"Recall {recall:.3f} below minimum 0.25"
        assert diversity >= 0.7, f"Diversity {diversity:.3f} below minimum 0.7"
        assert novelty >= 0.6, f"Novelty {novelty:.3f} below minimum 0.6"
```

---

## **8. TESTING A/B** {#ab}

### **Framework de A/B Testing**
```python
# Framework de A/B testing para recomendaciones
import random
import numpy as np
from scipy import stats

class ABTestingFramework:
    def __init__(self):
        self.experiments = {}
        self.results = {}
    
    def create_experiment(self, experiment_name, variants, traffic_split=None):
        """Crear experimento A/B"""
        if traffic_split is None:
            traffic_split = [1.0 / len(variants)] * len(variants)
        
        experiment = {
            'name': experiment_name,
            'variants': variants,
            'traffic_split': traffic_split,
            'status': 'active',
            'start_date': datetime.now(),
            'metrics': []
        }
        
        self.experiments[experiment_name] = experiment
        return experiment
    
    def assign_user_to_variant(self, user_id, experiment_name):
        """Asignar usuario a variante"""
        if experiment_name not in self.experiments:
            raise ValueError(f"Experiment {experiment_name} not found")
        
        experiment = self.experiments[experiment_name]
        
        # Usar hash del user_id para consistencia
        hash_value = hash(user_id) % 100
        cumulative_split = 0
        
        for i, split in enumerate(experiment['traffic_split']):
            cumulative_split += split * 100
            if hash_value < cumulative_split:
                return experiment['variants'][i]
        
        return experiment['variants'][-1]  # Fallback
    
    def track_event(self, user_id, experiment_name, event_name, event_value=1):
        """Rastrear evento en experimento"""
        variant = self.assign_user_to_variant(user_id, experiment_name)
        
        event = {
            'user_id': user_id,
            'experiment': experiment_name,
            'variant': variant,
            'event': event_name,
            'value': event_value,
            'timestamp': datetime.now()
        }
        
        if experiment_name not in self.results:
            self.results[experiment_name] = []
        
        self.results[experiment_name].append(event)
    
    def analyze_experiment(self, experiment_name, metric_name, confidence_level=0.95):
        """Analizar experimento A/B"""
        if experiment_name not in self.results:
            raise ValueError(f"No results found for experiment {experiment_name}")
        
        results = self.results[experiment_name]
        experiment = self.experiments[experiment_name]
        
        # Agrupar por variante
        variant_metrics = {}
        for variant in experiment['variants']:
            variant_events = [r for r in results if r['variant'] == variant and r['event'] == metric_name]
            variant_metrics[variant] = [r['value'] for r in variant_events]
        
        # Calcular estadísticas
        analysis = {}
        for variant, values in variant_metrics.items():
            if values:
                analysis[variant] = {
                    'count': len(values),
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'confidence_interval': self.calculate_confidence_interval(values, confidence_level)
                }
        
        # Comparar variantes
        if len(analysis) >= 2:
            variants = list(analysis.keys())
            values1 = variant_metrics[variants[0]]
            values2 = variant_metrics[variants[1]]
            
            if values1 and values2:
                t_stat, p_value = stats.ttest_ind(values1, values2)
                analysis['comparison'] = {
                    't_statistic': t_stat,
                    'p_value': p_value,
                    'significant': p_value < (1 - confidence_level)
                }
        
        return analysis
    
    def calculate_confidence_interval(self, values, confidence_level):
        """Calcular intervalo de confianza"""
        n = len(values)
        mean = np.mean(values)
        std = np.std(values, ddof=1)
        
        # Usar distribución t para muestras pequeñas
        if n < 30:
            t_value = stats.t.ppf(1 - (1 - confidence_level) / 2, n - 1)
        else:
            t_value = stats.norm.ppf(1 - (1 - confidence_level) / 2)
        
        margin_error = t_value * (std / np.sqrt(n))
        
        return {
            'lower': mean - margin_error,
            'upper': mean + margin_error,
            'mean': mean
        }
```

### **Tests de A/B para Recomendaciones**
```python
# Tests A/B específicos para recomendaciones
class RecommendationABTests:
    def __init__(self):
        self.ab_framework = ABTestingFramework()
        self.setup_recommendation_experiments()
    
    def setup_recommendation_experiments(self):
        """Configurar experimentos de recomendaciones"""
        # Experimento 1: Algoritmo de recomendación
        self.ab_framework.create_experiment(
            'recommendation_algorithm',
            ['collaborative_filtering', 'content_based', 'hybrid'],
            [0.33, 0.33, 0.34]
        )
        
        # Experimento 2: Número de recomendaciones
        self.ab_framework.create_experiment(
            'recommendation_count',
            ['5_recommendations', '10_recommendations', '15_recommendations'],
            [0.33, 0.33, 0.34]
        )
        
        # Experimento 3: Presentación visual
        self.ab_framework.create_experiment(
            'recommendation_layout',
            ['grid_layout', 'list_layout', 'carousel_layout'],
            [0.33, 0.33, 0.34]
        )
    
    def test_algorithm_performance(self):
        """Test performance de algoritmos"""
        # Simular datos de experimento
        for user_id in range(1000):
            variant = self.ab_framework.assign_user_to_variant(
                f'user_{user_id}', 'recommendation_algorithm'
            )
            
            # Simular métricas de recomendación
            if variant == 'collaborative_filtering':
                ctr = np.random.normal(0.05, 0.01)  # 5% CTR
                conversion = np.random.normal(0.02, 0.005)  # 2% conversión
            elif variant == 'content_based':
                ctr = np.random.normal(0.06, 0.01)  # 6% CTR
                conversion = np.random.normal(0.025, 0.005)  # 2.5% conversión
            else:  # hybrid
                ctr = np.random.normal(0.07, 0.01)  # 7% CTR
                conversion = np.random.normal(0.03, 0.005)  # 3% conversión
            
            # Rastrear eventos
            self.ab_framework.track_event(
                f'user_{user_id}', 'recommendation_algorithm', 'ctr', ctr
            )
            self.ab_framework.track_event(
                f'user_{user_id}', 'recommendation_algorithm', 'conversion', conversion
            )
        
        # Analizar resultados
        ctr_analysis = self.ab_framework.analyze_experiment(
            'recommendation_algorithm', 'ctr'
        )
        conversion_analysis = self.ab_framework.analyze_experiment(
            'recommendation_algorithm', 'conversion'
        )
        
        # Verificar que hay diferencias significativas
        assert 'comparison' in ctr_analysis, "No comparison data available"
        assert 'comparison' in conversion_analysis, "No comparison data available"
        
        return ctr_analysis, conversion_analysis
    
    def test_recommendation_count_impact(self):
        """Test impacto del número de recomendaciones"""
        # Simular datos de experimento
        for user_id in range(1000):
            variant = self.ab_framework.assign_user_to_variant(
                f'user_{user_id}', 'recommendation_count'
            )
            
            # Simular métricas basadas en número de recomendaciones
            if variant == '5_recommendations':
                engagement = np.random.normal(0.8, 0.1)  # 80% engagement
                scroll_depth = np.random.normal(0.6, 0.1)  # 60% scroll depth
            elif variant == '10_recommendations':
                engagement = np.random.normal(0.85, 0.1)  # 85% engagement
                scroll_depth = np.random.normal(0.7, 0.1)  # 70% scroll depth
            else:  # 15_recommendations
                engagement = np.random.normal(0.75, 0.1)  # 75% engagement
                scroll_depth = np.random.normal(0.65, 0.1)  # 65% scroll depth
            
            # Rastrear eventos
            self.ab_framework.track_event(
                f'user_{user_id}', 'recommendation_count', 'engagement', engagement
            )
            self.ab_framework.track_event(
                f'user_{user_id}', 'recommendation_count', 'scroll_depth', scroll_depth
            )
        
        # Analizar resultados
        engagement_analysis = self.ab_framework.analyze_experiment(
            'recommendation_count', 'engagement'
        )
        scroll_analysis = self.ab_framework.analyze_experiment(
            'recommendation_count', 'scroll_depth'
        )
        
        return engagement_analysis, scroll_analysis
```

---

## **9. AUTOMATIZACIÓN** {#automatizacion}

### **Pipeline de CI/CD**
```yaml
# .github/workflows/recommendation-tests.yml
name: Recommendation System Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=recommendation_engine --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db

  performance-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Start application
      run: |
        python app.py &
        sleep 30
    
    - name: Run performance tests
      run: |
        pytest tests/performance/ -v --html=performance_report.html
    
    - name: Upload performance report
      uses: actions/upload-artifact@v2
      with:
        name: performance-report
        path: performance_report.html

  security-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run security tests
      run: |
        pytest tests/security/ -v
        bandit -r recommendation_engine/
        safety check

  e2e-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Install Playwright
      run: |
        pip install playwright
        playwright install
    
    - name: Start application
      run: |
        python app.py &
        sleep 30
    
    - name: Run E2E tests
      run: |
        pytest tests/e2e/ -v --html=e2e_report.html
    
    - name: Upload E2E report
      uses: actions/upload-artifact@v2
      with:
        name: e2e-report
        path: e2e_report.html
```

### **Automatización de Tests**
```python
# Automatización de tests para recomendaciones
import subprocess
import sys
import os
from datetime import datetime

class TestAutomation:
    def __init__(self):
        self.test_suites = {
            'unit': 'tests/unit/',
            'integration': 'tests/integration/',
            'performance': 'tests/performance/',
            'security': 'tests/security/',
            'e2e': 'tests/e2e/'
        }
        self.results = {}
    
    def run_all_tests(self):
        """Ejecutar todos los tests"""
        print("🚀 Starting comprehensive test suite...")
        
        for suite_name, suite_path in self.test_suites.items():
            print(f"\n📋 Running {suite_name} tests...")
            result = self.run_test_suite(suite_name, suite_path)
            self.results[suite_name] = result
            
            if result['success']:
                print(f"✅ {suite_name} tests passed")
            else:
                print(f"❌ {suite_name} tests failed")
                print(f"   Error: {result['error']}")
        
        # Generar reporte
        self.generate_test_report()
        
        return all(result['success'] for result in self.results.values())
    
    def run_test_suite(self, suite_name, suite_path):
        """Ejecutar suite de tests específica"""
        try:
            # Comando base de pytest
            cmd = ['pytest', suite_path, '-v', '--tb=short']
            
            # Agregar opciones específicas por suite
            if suite_name == 'unit':
                cmd.extend(['--cov=recommendation_engine', '--cov-report=xml'])
            elif suite_name == 'performance':
                cmd.extend(['--html=performance_report.html', '--self-contained-html'])
            elif suite_name == 'e2e':
                cmd.extend(['--html=e2e_report.html', '--self-contained-html'])
            
            # Ejecutar tests
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Test suite {suite_name} timed out',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'returncode': -1
            }
    
    def generate_test_report(self):
        """Generar reporte de tests"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_suites': len(self.test_suites),
                'passed_suites': sum(1 for r in self.results.values() if r['success']),
                'failed_suites': sum(1 for r in self.results.values() if not r['success'])
            },
            'details': self.results
        }
        
        # Guardar reporte
        with open('test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Test report saved to test_report.json")
        print(f"   Total suites: {report['summary']['total_suites']}")
        print(f"   Passed: {report['summary']['passed_suites']}")
        print(f"   Failed: {report['summary']['failed_suites']}")
    
    def run_specific_test(self, test_path):
        """Ejecutar test específico"""
        try:
            result = subprocess.run(
                ['pytest', test_path, '-v'],
                capture_output=True,
                text=True
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
```

---

## **10. MONITOREO DE CALIDAD** {#monitoreo}

### **Dashboard de Calidad**
```python
# Dashboard de monitoreo de calidad
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

class QualityMonitoringDashboard:
    def __init__(self):
        self.metrics_collector = QualityMetricsCollector()
        self.alert_manager = AlertManager()
    
    def create_dashboard(self):
        """Crear dashboard de calidad"""
        st.set_page_config(
            page_title="Recommendation Quality Dashboard",
            page_icon="📊",
            layout="wide"
        )
        
        st.title("📊 Recommendation Quality Dashboard")
        
        # Métricas en tiempo real
        self.display_real_time_metrics()
        
        # Gráficos de tendencias
        self.display_trend_charts()
        
        # Alertas de calidad
        self.display_quality_alerts()
        
        # Métricas de performance
        self.display_performance_metrics()
    
    def display_real_time_metrics(self):
        """Mostrar métricas en tiempo real"""
        st.subheader("🔴 Real-time Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            precision = self.metrics_collector.get_current_precision()
            st.metric(
                "Precision@5",
                f"{precision:.3f}",
                delta=f"{precision - 0.15:.3f}" if precision else None
            )
        
        with col2:
            recall = self.metrics_collector.get_current_recall()
            st.metric(
                "Recall@10",
                f"{recall:.3f}",
                delta=f"{recall - 0.25:.3f}" if recall else None
            )
        
        with col3:
            diversity = self.metrics_collector.get_current_diversity()
            st.metric(
                "Diversity",
                f"{diversity:.3f}",
                delta=f"{diversity - 0.7:.3f}" if diversity else None
            )
        
        with col4:
            novelty = self.metrics_collector.get_current_novelty()
            st.metric(
                "Novelty",
                f"{novelty:.3f}",
                delta=f"{novelty - 0.6:.3f}" if novelty else None
            )
    
    def display_trend_charts(self):
        """Mostrar gráficos de tendencias"""
        st.subheader("📈 Quality Trends")
        
        # Obtener datos históricos
        historical_data = self.metrics_collector.get_historical_metrics(
            days=30
        )
        
        if historical_data:
            # Gráfico de precisión y recall
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=historical_data['date'],
                y=historical_data['precision'],
                mode='lines+markers',
                name='Precision@5',
                line=dict(color='blue')
            ))
            
            fig.add_trace(go.Scatter(
                x=historical_data['date'],
                y=historical_data['recall'],
                mode='lines+markers',
                name='Recall@10',
                line=dict(color='red')
            ))
            
            fig.update_layout(
                title="Precision and Recall Trends",
                xaxis_title="Date",
                yaxis_title="Score",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico de diversidad y novedad
            fig2 = go.Figure()
            
            fig2.add_trace(go.Scatter(
                x=historical_data['date'],
                y=historical_data['diversity'],
                mode='lines+markers',
                name='Diversity',
                line=dict(color='green')
            ))
            
            fig2.add_trace(go.Scatter(
                x=historical_data['date'],
                y=historical_data['novelty'],
                mode='lines+markers',
                name='Novelty',
                line=dict(color='orange')
            ))
            
            fig2.update_layout(
                title="Diversity and Novelty Trends",
                xaxis_title="Date",
                yaxis_title="Score",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig2, use_container_width=True)
    
    def display_quality_alerts(self):
        """Mostrar alertas de calidad"""
        st.subheader("🚨 Quality Alerts")
        
        alerts = self.alert_manager.get_active_alerts()
        
        if alerts:
            for alert in alerts:
                if alert['severity'] == 'high':
                    st.error(f"🔴 {alert['message']}")
                elif alert['severity'] == 'medium':
                    st.warning(f"🟡 {alert['message']}")
                else:
                    st.info(f"🔵 {alert['message']}")
        else:
            st.success("✅ No active quality alerts")
    
    def display_performance_metrics(self):
        """Mostrar métricas de performance"""
        st.subheader("⚡ Performance Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de tiempo de respuesta
            response_times = self.metrics_collector.get_response_times()
            
            if response_times:
                fig = px.histogram(
                    response_times,
                    x='response_time',
                    title="Response Time Distribution",
                    labels={'response_time': 'Response Time (ms)'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gráfico de throughput
            throughput_data = self.metrics_collector.get_throughput_data()
            
            if throughput_data:
                fig = px.line(
                    throughput_data,
                    x='timestamp',
                    y='requests_per_second',
                    title="Throughput Over Time",
                    labels={'requests_per_second': 'Requests/Second'}
                )
                st.plotly_chart(fig, use_container_width=True)
```

---

## **11. MEJORES PRÁCTICAS** {#mejores}

### **Principios de Testing**
1. **Test Pyramid**: Más tests unitarios, menos tests E2E
2. **Test Isolation**: Tests independientes y aislados
3. **Test Data**: Datos de prueba realistas y consistentes
4. **Test Coverage**: Cobertura de código adecuada
5. **Test Maintenance**: Tests fáciles de mantener

### **Estrategias de Testing**
```python
# Estrategias de testing para recomendaciones
class TestingStrategies:
    def __init__(self):
        self.strategies = {
            'unit_testing': {
                'focus': 'Algoritmos individuales',
                'tools': ['pytest', 'unittest'],
                'coverage_target': 90
            },
            'integration_testing': {
                'focus': 'Interacción entre servicios',
                'tools': ['pytest', 'testcontainers'],
                'coverage_target': 80
            },
            'performance_testing': {
                'focus': 'Rendimiento y escalabilidad',
                'tools': ['locust', 'pytest-benchmark'],
                'coverage_target': 70
            },
            'security_testing': {
                'focus': 'Vulnerabilidades de seguridad',
                'tools': ['bandit', 'safety'],
                'coverage_target': 85
            },
            'usability_testing': {
                'focus': 'Experiencia de usuario',
                'tools': ['selenium', 'playwright'],
                'coverage_target': 60
            }
        }
    
    def get_testing_plan(self, feature_complexity):
        """Obtener plan de testing basado en complejidad"""
        if feature_complexity == 'low':
            return {
                'unit_tests': 80,
                'integration_tests': 15,
                'e2e_tests': 5
            }
        elif feature_complexity == 'medium':
            return {
                'unit_tests': 70,
                'integration_tests': 20,
                'e2e_tests': 10
            }
        else:  # high
            return {
                'unit_tests': 60,
                'integration_tests': 25,
                'e2e_tests': 15
            }
```

---

## **12. TROUBLESHOOTING** {#troubleshooting}

### **Problemas Comunes de Testing**

#### **Tests Flaky**
```python
# Solución para tests flaky
def fix_flaky_tests():
    """Solucionar tests flaky"""
    # 1. Usar datos determinísticos
    random.seed(42)
    np.random.seed(42)
    
    # 2. Esperar condiciones específicas
    from selenium.webdriver.support import expected_conditions as EC
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "recommendations"))
    )
    
    # 3. Usar timeouts apropiados
    time.sleep(1)  # Evitar
    WebDriverWait(driver, 10).until(...)  # Mejor
    
    # 4. Limpiar estado entre tests
    def setup_method(self):
        self.cleanup_test_data()
```

#### **Tests Lentos**
```python
# Solución para tests lentos
def optimize_slow_tests():
    """Optimizar tests lentos"""
    # 1. Usar mocks para operaciones lentas
    @patch('recommendation_engine.external_api_call')
    def test_recommendation_generation(self, mock_api):
        mock_api.return_value = {'data': 'test'}
        # Test rápido
    
    # 2. Usar base de datos en memoria
    engine = create_engine('sqlite:///:memory:')
    
    # 3. Paralelizar tests
    pytest -n auto  # Usar pytest-xdist
    
    # 4. Cachear datos de prueba
    @pytest.fixture(scope='session')
    def test_data():
        return load_test_data()
```

#### **Tests de Performance Inconsistentes**
```python
# Solución para tests de performance inconsistentes
def fix_performance_tests():
    """Solucionar tests de performance inconsistentes"""
    # 1. Usar percentiles en lugar de promedios
    assert response_time_p95 < 2000  # 95% < 2s
    
    # 2. Ejecutar múltiples iteraciones
    response_times = []
    for _ in range(10):
        start = time.time()
        make_request()
        response_times.append(time.time() - start)
    
    # 3. Usar warmup
    for _ in range(5):  # Warmup
        make_request()
    
    # 4. Aislar tests de performance
    @pytest.mark.performance
    def test_recommendation_performance():
        pass
```

---

## **🎯 PRÓXIMOS PASOS**

1. **Configurar Pipeline**: Implementar CI/CD
2. **Escribir Tests**: Comenzar con tests unitarios
3. **Automatizar**: Configurar ejecución automática
4. **Monitorear**: Implementar dashboard de calidad
5. **Mejorar Continuamente**: Optimizar basándose en métricas

---

## **📞 SOPORTE**

- **Consultoría de Testing**: [Especialistas en QA]
- **Herramientas de Testing**: [Frameworks y librerías]
- **Automatización**: [Servicios de CI/CD]
- **Soporte Técnico**: [Asistencia para testing]

---

**¡Con esta estrategia completa de testing y QA, tu sistema de recomendaciones estará completamente validado y libre de errores!** 🧪



