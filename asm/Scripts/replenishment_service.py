from datetime import datetime, timedelta
from app import db
from models import Product, InventoryRecord, ReorderRecommendation, DemandForecast, Supplier
from services.alert_service import alert_system
from services.forecasting_service import demand_forecasting_service
import logging
from typing import List, Dict, Tuple

class IntelligentReplenishmentService:
    """Servicio de reposición inteligente que combina múltiples factores"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_reorder_recommendations(self) -> List[Dict]:
        """
        Genera recomendaciones inteligentes de reposición para todos los productos
        
        Returns:
            Lista de recomendaciones con detalles de cada producto
        """
        try:
            products = Product.query.all()
            recommendations = []
            
            for product in products:
                recommendation = self._analyze_product_replenishment(product)
                if recommendation:
                    recommendations.append(recommendation)
            
            self.logger.info(f'Generadas {len(recommendations)} recomendaciones de reposición')
            return recommendations
            
        except Exception as e:
            self.logger.error(f'Error generando recomendaciones de reposición: {str(e)}')
            return []
    
    def _analyze_product_replenishment(self, product: Product) -> Dict:
        """
        Analiza un producto específico y determina si necesita reposición
        
        Args:
            product: Objeto Product a analizar
            
        Returns:
            Dict con recomendación o None si no es necesaria
        """
        try:
            # Obtener información actual del producto
            current_stock = alert_system.get_current_stock(product.id)
            lead_time_days = product.supplier.lead_time_days if product.supplier else 7
            
            # Calcular demanda esperada durante el lead time
            expected_demand_during_lead_time = self._calculate_expected_demand(
                product.id, lead_time_days
            )
            
            # Calcular punto de reposición dinámico
            dynamic_reorder_point = self._calculate_dynamic_reorder_point(
                product, expected_demand_during_lead_time
            )
            
            # Determinar si necesita reposición
            needs_reorder = current_stock <= dynamic_reorder_point
            
            if not needs_reorder:
                return None
            
            # Calcular cantidad recomendada
            recommended_quantity = self._calculate_optimal_order_quantity(
                product, current_stock, expected_demand_during_lead_time
            )
            
            # Determinar urgencia
            urgency = self._determine_urgency(current_stock, dynamic_reorder_point, product.min_stock_level)
            
            # Calcular costo estimado
            estimated_cost = recommended_quantity * product.cost_price
            
            # Generar razón de la recomendación
            reason = self._generate_reorder_reason(
                current_stock, dynamic_reorder_point, expected_demand_during_lead_time, urgency
            )
            
            # Guardar recomendación en la base de datos
            self._save_reorder_recommendation(
                product.id, recommended_quantity, reason, urgency, estimated_cost
            )
            
            return {
                'product_id': product.id,
                'product_name': product.name,
                'sku': product.sku,
                'current_stock': current_stock,
                'dynamic_reorder_point': dynamic_reorder_point,
                'recommended_quantity': recommended_quantity,
                'urgency': urgency,
                'estimated_cost': estimated_cost,
                'reason': reason,
                'supplier': product.supplier.name if product.supplier else 'No asignado',
                'lead_time_days': lead_time_days,
                'expected_demand_during_lead_time': expected_demand_during_lead_time
            }
            
        except Exception as e:
            self.logger.error(f'Error analizando reposición para producto {product.id}: {str(e)}')
            return None
    
    def _calculate_expected_demand(self, product_id: int, days: int) -> float:
        """Calcula la demanda esperada para un número específico de días"""
        try:
            # Obtener predicciones de demanda
            forecast_result = demand_forecasting_service.forecast_demand(product_id, days)
            
            if 'predictions' in forecast_result:
                return sum(forecast_result['predictions'][:days])
            
            # Fallback: usar promedio histórico
            sales_history = demand_forecasting_service.get_sales_history(product_id, 30)
            if sales_history:
                total_sales = sum(record['quantity'] for record in sales_history)
                avg_daily_sales = total_sales / len(sales_history)
                return avg_daily_sales * days
            
            return 1.0  # Valor por defecto
            
        except Exception as e:
            self.logger.error(f'Error calculando demanda esperada: {str(e)}')
            return 1.0
    
    def _calculate_dynamic_reorder_point(self, product: Product, expected_demand: float) -> int:
        """
        Calcula punto de reposición dinámico basado en demanda esperada y variabilidad
        
        Args:
            product: Producto a analizar
            expected_demand: Demanda esperada durante el lead time
            
        Returns:
            Punto de reposición calculado dinámicamente
        """
        try:
            # Factor de seguridad basado en variabilidad de demanda
            safety_factor = self._calculate_safety_factor(product.id)
            
            # Punto de reposición = Demanda esperada + Stock de seguridad
            safety_stock = expected_demand * safety_factor
            
            dynamic_reorder_point = int(expected_demand + safety_stock)
            
            # Asegurar que no sea menor que el punto mínimo configurado
            min_reorder_point = max(product.min_stock_level, 1)
            
            return max(dynamic_reorder_point, min_reorder_point)
            
        except Exception as e:
            self.logger.error(f'Error calculando punto de reposición dinámico: {str(e)}')
            return product.reorder_point
    
    def _calculate_safety_factor(self, product_id: int) -> float:
        """Calcula factor de seguridad basado en variabilidad histórica"""
        try:
            sales_history = demand_forecasting_service.get_sales_history(product_id, 30)
            
            if len(sales_history) < 7:
                return 0.2  # Factor conservador por defecto
            
            quantities = [record['quantity'] for record in sales_history]
            
            # Calcular coeficiente de variación
            mean_demand = sum(quantities) / len(quantities)
            if mean_demand == 0:
                return 0.2
            
            variance = sum((q - mean_demand) ** 2 for q in quantities) / len(quantities)
            std_deviation = variance ** 0.5
            
            coefficient_of_variation = std_deviation / mean_demand
            
            # Factor de seguridad basado en variabilidad
            if coefficient_of_variation < 0.2:
                return 0.1  # Baja variabilidad
            elif coefficient_of_variation < 0.5:
                return 0.2  # Variabilidad media
            else:
                return 0.3  # Alta variabilidad
                
        except Exception as e:
            self.logger.error(f'Error calculando factor de seguridad: {str(e)}')
            return 0.2
    
    def _calculate_optimal_order_quantity(self, product: Product, current_stock: int, 
                                        expected_demand: float) -> int:
        """
        Calcula la cantidad óptima de pedido usando modelo EOQ modificado
        
        Args:
            product: Producto
            current_stock: Stock actual
            expected_demand: Demanda esperada durante el lead time
            
        Returns:
            Cantidad óptima de pedido
        """
        try:
            # Calcular cantidad necesaria para alcanzar stock máximo
            quantity_to_max = product.max_stock_level - current_stock
            
            # Calcular cantidad basada en demanda esperada (mínimo 30 días)
            demand_based_quantity = max(int(expected_demand * 1.5), 10)
            
            # Usar el menor de los dos valores, pero asegurar mínimo
            optimal_quantity = min(quantity_to_max, demand_based_quantity)
            
            # Asegurar cantidad mínima razonable
            min_order_quantity = max(10, int(expected_demand * 0.5))
            
            return max(optimal_quantity, min_order_quantity)
            
        except Exception as e:
            self.logger.error(f'Error calculando cantidad óptima: {str(e)}')
            return 10
    
    def _determine_urgency(self, current_stock: int, reorder_point: int, min_stock: int) -> str:
        """Determina la urgencia de la reposición"""
        try:
            if current_stock <= 0:
                return 'critical'
            elif current_stock <= min_stock:
                return 'high'
            elif current_stock <= reorder_point:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            self.logger.error(f'Error determinando urgencia: {str(e)}')
            return 'medium'
    
    def _generate_reorder_reason(self, current_stock: int, reorder_point: int, 
                               expected_demand: float, urgency: str) -> str:
        """Genera una razón descriptiva para la recomendación de reposición"""
        try:
            if urgency == 'critical':
                return f"Stock agotado. Demanda esperada: {expected_demand:.1f} unidades"
            elif urgency == 'high':
                return f"Stock crítico ({current_stock} unidades). Punto de reposición: {reorder_point}"
            elif urgency == 'medium':
                return f"Alcanzado punto de reposición. Demanda esperada: {expected_demand:.1f} unidades"
            else:
                return f"Reposición preventiva recomendada"
                
        except Exception as e:
            self.logger.error(f'Error generando razón: {str(e)}')
            return "Reposición recomendada"
    
    def _save_reorder_recommendation(self, product_id: int, quantity: int, 
                                   reason: str, urgency: str, estimated_cost: float):
        """Guarda la recomendación en la base de datos"""
        try:
            # Eliminar recomendaciones anteriores no procesadas
            ReorderRecommendation.query.filter(
                ReorderRecommendation.product_id == product_id,
                ReorderRecommendation.is_processed == False
            ).delete()
            
            # Crear nueva recomendación
            recommendation = ReorderRecommendation(
                product_id=product_id,
                recommended_quantity=quantity,
                reason=reason,
                urgency=urgency,
                estimated_cost=estimated_cost
            )
            
            db.session.add(recommendation)
            db.session.commit()
            
        except Exception as e:
            self.logger.error(f'Error guardando recomendación: {str(e)}')
            db.session.rollback()
    
    def process_reorder_recommendation(self, recommendation_id: int) -> bool:
        """
        Procesa una recomendación de reposición (simula la creación de orden de compra)
        
        Args:
            recommendation_id: ID de la recomendación
            
        Returns:
            True si se procesó exitosamente
        """
        try:
            recommendation = ReorderRecommendation.query.get(recommendation_id)
            
            if not recommendation:
                return False
            
            # Marcar como procesada
            recommendation.is_processed = True
            
            # Aquí se podría integrar con un sistema de órdenes de compra
            # Por ahora solo registramos el procesamiento
            
            db.session.commit()
            
            self.logger.info(f'Recomendación {recommendation_id} procesada exitosamente')
            return True
            
        except Exception as e:
            self.logger.error(f'Error procesando recomendación {recommendation_id}: {str(e)}')
            db.session.rollback()
            return False
    
    def get_reorder_summary(self) -> Dict:
        """Obtiene resumen de recomendaciones de reposición"""
        try:
            total_recommendations = ReorderRecommendation.query.count()
            pending_recommendations = ReorderRecommendation.query.filter(
                ReorderRecommendation.is_processed == False
            ).count()
            
            # Recomendaciones por urgencia
            critical_count = ReorderRecommendation.query.filter(
                ReorderRecommendation.urgency == 'critical',
                ReorderRecommendation.is_processed == False
            ).count()
            
            high_count = ReorderRecommendation.query.filter(
                ReorderRecommendation.urgency == 'high',
                ReorderRecommendation.is_processed == False
            ).count()
            
            medium_count = ReorderRecommendation.query.filter(
                ReorderRecommendation.urgency == 'medium',
                ReorderRecommendation.is_processed == False
            ).count()
            
            # Costo total estimado de recomendaciones pendientes
            total_estimated_cost = db.session.query(
                db.func.sum(ReorderRecommendation.estimated_cost)
            ).filter(
                ReorderRecommendation.is_processed == False
            ).scalar() or 0
            
            return {
                'total_recommendations': total_recommendations,
                'pending_recommendations': pending_recommendations,
                'critical_recommendations': critical_count,
                'high_recommendations': high_count,
                'medium_recommendations': medium_count,
                'total_estimated_cost': round(total_estimated_cost, 2)
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo resumen de reposición: {str(e)}')
            return {}

# Instancia global del servicio de reposición
replenishment_service = IntelligentReplenishmentService()



