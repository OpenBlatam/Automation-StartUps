"""
Sistema de A/B Testing para Estrategias de Precios

Permite probar diferentes estrategias de precios
"""

import logging
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import statistics

logger = logging.getLogger(__name__)


class PriceABTesting:
    """Sistema de A/B testing para estrategias de precios"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.tests_dir = Path(config.get('ab_tests_dir', '/tmp/price_ab_tests'))
        self.tests_dir.mkdir(parents=True, exist_ok=True)
        self.active_tests: Dict[str, Dict] = {}
    
    def create_test(
        self,
        test_name: str,
        strategy_a: str,
        strategy_b: str,
        products: List[str],
        duration_days: int = 7
    ) -> Dict:
        """
        Crea un nuevo test A/B
        
        Args:
            test_name: Nombre del test
            strategy_a: Estrategia A (control)
            strategy_b: Estrategia B (variante)
            products: Lista de IDs de productos a testear
            duration_days: Duración del test en días
        
        Returns:
            Información del test creado
        """
        test_id = f"{test_name}_{datetime.now().strftime('%Y%m%d')}"
        
        # Dividir productos en grupos A y B
        mid_point = len(products) // 2
        group_a = products[:mid_point]
        group_b = products[mid_point:]
        
        test_data = {
            'test_id': test_id,
            'test_name': test_name,
            'strategy_a': strategy_a,
            'strategy_b': strategy_b,
            'group_a_products': group_a,
            'group_b_products': group_b,
            'start_date': datetime.now().isoformat(),
            'end_date': (datetime.now() + timedelta(days=duration_days)).isoformat(),
            'status': 'active',
            'results': {
                'group_a': {'prices': [], 'revenue': 0, 'sales': 0},
                'group_b': {'prices': [], 'revenue': 0, 'sales': 0},
            }
        }
        
        self.active_tests[test_id] = test_data
        self._save_test(test_data)
        
        logger.info(f"Test A/B creado: {test_id}")
        
        return test_data
    
    def record_result(
        self,
        test_id: str,
        group: str,
        product_id: str,
        price: float,
        revenue: Optional[float] = None,
        sales: Optional[int] = None
    ):
        """
        Registra resultado de un test
        
        Args:
            test_id: ID del test
            group: Grupo ('a' o 'b')
            product_id: ID del producto
            price: Precio aplicado
            revenue: Ingresos (opcional)
            sales: Ventas (opcional)
        """
        if test_id not in self.active_tests:
            logger.warning(f"Test {test_id} no encontrado")
            return
        
        test = self.active_tests[test_id]
        group_key = f'group_{group.lower()}'
        
        if group_key not in test['results']:
            test['results'][group_key] = {'prices': [], 'revenue': 0, 'sales': 0}
        
        result = test['results'][group_key]
        result['prices'].append({
            'product_id': product_id,
            'price': price,
            'timestamp': datetime.now().isoformat()
        })
        
        if revenue:
            result['revenue'] += revenue
        
        if sales:
            result['sales'] += sales
        
        self._save_test(test)
    
    def analyze_test(self, test_id: str) -> Dict:
        """
        Analiza resultados de un test
        
        Args:
            test_id: ID del test
        
        Returns:
            Análisis del test
        """
        if test_id not in self.active_tests:
            return {'error': 'Test no encontrado'}
        
        test = self.active_tests[test_id]
        results_a = test['results']['group_a']
        results_b = test['results']['group_b']
        
        # Calcular métricas
        avg_price_a = (
            statistics.mean([p['price'] for p in results_a['prices']])
            if results_a['prices'] else 0
        )
        avg_price_b = (
            statistics.mean([p['price'] for p in results_b['prices']])
            if results_b['prices'] else 0
        )
        
        revenue_a = results_a.get('revenue', 0)
        revenue_b = results_b.get('revenue', 0)
        sales_a = results_a.get('sales', 0)
        sales_b = results_b.get('sales', 0)
        
        # Calcular diferencias
        revenue_diff = revenue_b - revenue_a
        revenue_diff_pct = (
            (revenue_diff / revenue_a * 100) if revenue_a > 0 else 0
        )
        
        sales_diff = sales_b - sales_a
        sales_diff_pct = (
            (sales_diff / sales_a * 100) if sales_a > 0 else 0
        )
        
        # Determinar ganador
        if revenue_b > revenue_a:
            winner = 'B'
            winner_strategy = test['strategy_b']
        elif revenue_a > revenue_b:
            winner = 'A'
            winner_strategy = test['strategy_a']
        else:
            winner = 'Tie'
            winner_strategy = 'No significant difference'
        
        # Calcular significancia estadística básica
        significance = self._calculate_significance(
            revenue_a, revenue_b, sales_a, sales_b
        )
        
        analysis = {
            'test_id': test_id,
            'test_name': test['test_name'],
            'status': test['status'],
            'group_a': {
                'strategy': test['strategy_a'],
                'avg_price': round(avg_price_a, 2),
                'revenue': round(revenue_a, 2),
                'sales': sales_a,
            },
            'group_b': {
                'strategy': test['strategy_b'],
                'avg_price': round(avg_price_b, 2),
                'revenue': round(revenue_b, 2),
                'sales': sales_b,
            },
            'differences': {
                'revenue_diff': round(revenue_diff, 2),
                'revenue_diff_percent': round(revenue_diff_pct, 2),
                'sales_diff': sales_diff,
                'sales_diff_percent': round(sales_diff_pct, 2),
            },
            'winner': winner,
            'winner_strategy': winner_strategy,
            'significance': significance,
            'analyzed_at': datetime.now().isoformat(),
        }
        
        return analysis
    
    def _calculate_significance(
        self,
        revenue_a: float,
        revenue_b: float,
        sales_a: int,
        sales_b: int
    ) -> str:
        """Calcula significancia estadística básica"""
        if sales_a == 0 or sales_b == 0:
            return 'insufficient_data'
        
        # Test simple: diferencia > 10% y suficiente volumen
        total_sales = sales_a + sales_b
        if total_sales < 100:
            return 'insufficient_sample'
        
        revenue_diff_pct = abs((revenue_b - revenue_a) / revenue_a * 100) if revenue_a > 0 else 0
        
        if revenue_diff_pct > 15:
            return 'highly_significant'
        elif revenue_diff_pct > 10:
            return 'significant'
        elif revenue_diff_pct > 5:
            return 'moderate'
        else:
            return 'not_significant'
    
    def get_active_tests(self) -> List[Dict]:
        """Obtiene lista de tests activos"""
        return [
            {
                'test_id': test_id,
                'test_name': test['test_name'],
                'status': test['status'],
                'start_date': test['start_date'],
                'end_date': test['end_date'],
            }
            for test_id, test in self.active_tests.items()
            if test['status'] == 'active'
        ]
    
    def end_test(self, test_id: str) -> Dict:
        """Finaliza un test"""
        if test_id not in self.active_tests:
            return {'error': 'Test no encontrado'}
        
        test = self.active_tests[test_id]
        test['status'] = 'completed'
        test['completed_at'] = datetime.now().isoformat()
        
        analysis = self.analyze_test(test_id)
        test['final_analysis'] = analysis
        
        self._save_test(test)
        
        return analysis
    
    def _save_test(self, test_data: Dict):
        """Guarda test en archivo"""
        try:
            test_file = self.tests_dir / f"{test_data['test_id']}.json"
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando test: {e}")








