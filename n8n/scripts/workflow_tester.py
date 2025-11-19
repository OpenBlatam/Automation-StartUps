#!/usr/bin/env python3
"""
Workflow Tester - Script para testing y validación de workflows
Proporciona funciones para probar workflows antes de producción
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class WorkflowTester:
    """Tester para workflows de automatización"""
    
    def __init__(self, api_base_url: str, api_key: str):
        self.api_base_url = api_base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
        self.test_results = []
    
    def test_cart_abandonment_webhook(self, test_data: Optional[Dict] = None) -> Dict:
        """Prueba el webhook de carrito abandonado"""
        webhook_url = f"{self.api_base_url}/webhook/cart-abandonment"
        
        default_data = {
            "eventType": "cart_abandonment",
            "customerId": "test_customer_001",
            "email": "test@example.com",
            "firstName": "Test",
            "lastName": "User",
            "cartId": "test_cart_001",
            "cartValue": 150.00,
            "cartItems": [
                {
                    "name": "Test Product",
                    "price": 75.00,
                    "quantity": 2,
                    "category": "test"
                }
            ],
            "sessionId": "test_session_001"
        }
        
        payload = test_data or default_data
        
        try:
            response = requests.post(webhook_url, json=payload, headers=self.headers, timeout=30)
            result = {
                'test': 'cart_abandonment_webhook',
                'status': 'success' if response.status_code == 200 else 'failed',
                'status_code': response.status_code,
                'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            result = {
                'test': 'cart_abandonment_webhook',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        
        self.test_results.append(result)
        return result
    
    def test_page_visit_webhook(self, test_data: Optional[Dict] = None) -> Dict:
        """Prueba el webhook de visita a página"""
        webhook_url = f"{self.api_base_url}/webhook/page-visit"
        
        default_data = {
            "eventType": "page_visit",
            "customerId": "test_customer_001",
            "email": "test@example.com",
            "pageUrl": "https://example.com/product/test",
            "pageCategory": "product",
            "productName": "Test Product",
            "sessionId": "test_session_001"
        }
        
        payload = test_data or default_data
        
        try:
            response = requests.post(webhook_url, json=payload, headers=self.headers, timeout=30)
            result = {
                'test': 'page_visit_webhook',
                'status': 'success' if response.status_code == 200 else 'failed',
                'status_code': response.status_code,
                'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            result = {
                'test': 'page_visit_webhook',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        
        self.test_results.append(result)
        return result
    
    def test_purchase_completed_webhook(self, test_data: Optional[Dict] = None) -> Dict:
        """Prueba el webhook de compra completada"""
        webhook_url = f"{self.api_base_url}/webhook/purchase-completed"
        
        default_data = {
            "customerId": "test_customer_001",
            "email": "test@example.com",
            "firstName": "Test",
            "orderId": "test_order_001",
            "orderValue": 200.00,
            "items": [
                {
                    "name": "Test Product",
                    "price": 100.00,
                    "quantity": 2
                }
            ],
            "purchaseDate": datetime.now().isoformat(),
            "estimatedDelivery": (datetime.now().timestamp() + 86400 * 3) * 1000
        }
        
        payload = test_data or default_data
        
        try:
            response = requests.post(webhook_url, json=payload, headers=self.headers, timeout=30)
            result = {
                'test': 'purchase_completed_webhook',
                'status': 'success' if response.status_code == 200 else 'failed',
                'status_code': response.status_code,
                'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            result = {
                'test': 'purchase_completed_webhook',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        
        self.test_results.append(result)
        return result
    
    def validate_webhook_response(self, response: Dict) -> Dict:
        """Valida que la respuesta del webhook sea correcta"""
        validation = {
            'valid': True,
            'errors': []
        }
        
        # Verificar que tiene success
        if 'success' not in response.get('response', {}):
            validation['valid'] = False
            validation['errors'].append('Missing success field')
        
        # Verificar que success es true
        if response.get('response', {}).get('success') != True:
            validation['valid'] = False
            validation['errors'].append('Success is not true')
        
        # Verificar que tiene customerId
        if 'customerId' not in response.get('response', {}):
            validation['valid'] = False
            validation['errors'].append('Missing customerId field')
        
        return validation
    
    def run_all_tests(self) -> Dict:
        """Ejecuta todos los tests"""
        print("Running all workflow tests...")
        print("=" * 50)
        
        # Test cart abandonment
        print("\n1. Testing Cart Abandonment Webhook...")
        cart_result = self.test_cart_abandonment_webhook()
        print(f"   Status: {cart_result['status']}")
        if cart_result['status'] == 'success':
            validation = self.validate_webhook_response(cart_result)
            print(f"   Validation: {'✓ Valid' if validation['valid'] else '✗ Invalid'}")
            if validation['errors']:
                print(f"   Errors: {', '.join(validation['errors'])}")
        
        # Test page visit
        print("\n2. Testing Page Visit Webhook...")
        page_result = self.test_page_visit_webhook()
        print(f"   Status: {page_result['status']}")
        if page_result['status'] == 'success':
            validation = self.validate_webhook_response(page_result)
            print(f"   Validation: {'✓ Valid' if validation['valid'] else '✗ Invalid'}")
        
        # Test purchase completed
        print("\n3. Testing Purchase Completed Webhook...")
        purchase_result = self.test_purchase_completed_webhook()
        print(f"   Status: {purchase_result['status']}")
        if purchase_result['status'] == 'success':
            validation = self.validate_webhook_response(purchase_result)
            print(f"   Validation: {'✓ Valid' if validation['valid'] else '✗ Invalid'}")
        
        # Resumen
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        
        total = len(self.test_results)
        passed = len([r for r in self.test_results if r['status'] == 'success'])
        failed = len([r for r in self.test_results if r['status'] == 'failed'])
        errors = len([r for r in self.test_results if r['status'] == 'error'])
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✓")
        print(f"Failed: {failed} ✗")
        print(f"Errors: {errors} ⚠")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'success_rate': (passed/total*100) if total > 0 else 0,
            'results': self.test_results
        }
    
    def generate_test_report(self, output_file: str = None) -> str:
        """Genera reporte de tests"""
        if not output_file:
            output_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': len(self.test_results),
                'passed': len([r for r in self.test_results if r['status'] == 'success']),
                'failed': len([r for r in self.test_results if r['status'] == 'failed']),
                'errors': len([r for r in self.test_results if r['status'] == 'error'])
            },
            'results': self.test_results
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return output_file


def main():
    """Ejemplo de uso"""
    api_url = os.getenv("API_BASE_URL", "https://api.yourdomain.com")
    api_key = os.getenv("API_KEY", "your_api_key_here")
    
    tester = WorkflowTester(api_url, api_key)
    
    # Ejecutar todos los tests
    summary = tester.run_all_tests()
    
    # Generar reporte
    report_file = tester.generate_test_report()
    print(f"\nTest report saved to: {report_file}")
    
    # Exit code basado en resultados
    if summary['failed'] > 0 or summary['errors'] > 0:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()










