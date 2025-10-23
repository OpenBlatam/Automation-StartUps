#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Alertas Inteligentes para Campañas de Marketing con IA
================================================================
Sistema avanzado de monitoreo y alertas basado en IA para campañas de marketing.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import logging

class IntelligentAlertsSystem:
    def __init__(self, campaigns_file='enhanced_1000_ai_marketing_campaigns.json'):
        """Inicializa el sistema de alertas inteligentes"""
        with open(campaigns_file, 'r', encoding='utf-8') as f:
            self.campaigns = json.load(f)
        
        self.df = pd.DataFrame(self.campaigns)
        
        # Configuración de alertas
        self.alert_rules = {
            'roi_threshold': 3.0,  # ROI mínimo esperado
            'success_probability_threshold': 0.7,  # Probabilidad de éxito mínima
            'budget_utilization_threshold': 0.8,  # Utilización de presupuesto
            'conversion_rate_threshold': 5.0,  # Tasa de conversión mínima
            'cost_per_acquisition_threshold': 100,  # CPA máximo
            'timeline_delay_threshold': 0.2,  # Retraso máximo en timeline
            'performance_degradation_threshold': 0.15  # Degradación de rendimiento
        }
        
        # Configuración de notificaciones
        self.notification_channels = {
            'email': True,
            'dashboard': True,
            'api': True,
            'sms': False
        }
        
        # Historial de alertas
        self.alert_history = []
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def analyze_campaign_performance(self, campaign_id: int, 
                                   current_metrics: Dict = None) -> Dict[str, Any]:
        """Analiza el rendimiento de una campaña y detecta anomalías"""
        campaign = next((c for c in self.campaigns if c['id'] == campaign_id), None)
        if not campaign:
            return {"error": f"Campaña {campaign_id} no encontrada"}
        
        # Usar métricas actuales si se proporcionan, sino usar las predeterminadas
        if current_metrics is None:
            current_metrics = campaign['metrics']
        
        expected_metrics = campaign['metrics']
        
        # Detectar anomalías
        anomalies = self._detect_anomalies(expected_metrics, current_metrics, campaign)
        
        # Calcular score de salud
        health_score = self._calculate_health_score(expected_metrics, current_metrics, campaign)
        
        # Generar alertas
        alerts = self._generate_alerts(anomalies, health_score, campaign)
        
        # Calcular recomendaciones
        recommendations = self._generate_performance_recommendations(
            anomalies, health_score, campaign, current_metrics
        )
        
        return {
            'campaign_id': campaign_id,
            'campaign_name': campaign['name'],
            'analysis_timestamp': datetime.now().isoformat(),
            'health_score': health_score,
            'anomalies_detected': len(anomalies),
            'anomalies': anomalies,
            'alerts': alerts,
            'recommendations': recommendations,
            'current_metrics': current_metrics,
            'expected_metrics': expected_metrics
        }
    
    def _detect_anomalies(self, expected: Dict, current: Dict, campaign: Dict) -> List[Dict]:
        """Detecta anomalías en el rendimiento de la campaña"""
        anomalies = []
        
        # Anomalía 1: ROI por debajo del umbral
        expected_roi = expected.get('return_on_ad_spend', 0)
        current_roi = current.get('return_on_ad_spend', 0)
        
        if current_roi < self.alert_rules['roi_threshold']:
            anomalies.append({
                'type': 'low_roi',
                'severity': 'high',
                'description': f'ROI actual ({current_roi:.2f}) está por debajo del umbral ({self.alert_rules["roi_threshold"]})',
                'expected_value': expected_roi,
                'current_value': current_roi,
                'deviation_percent': ((current_roi - expected_roi) / expected_roi * 100) if expected_roi > 0 else 0
            })
        
        # Anomalía 2: Tasa de conversión baja
        expected_conversion = expected.get('conversion_rate', 0)
        current_conversion = current.get('conversion_rate', 0)
        
        if current_conversion < self.alert_rules['conversion_rate_threshold']:
            anomalies.append({
                'type': 'low_conversion_rate',
                'severity': 'medium',
                'description': f'Tasa de conversión actual ({current_conversion:.2f}%) está por debajo del umbral ({self.alert_rules["conversion_rate_threshold"]}%)',
                'expected_value': expected_conversion,
                'current_value': current_conversion,
                'deviation_percent': ((current_conversion - expected_conversion) / expected_conversion * 100) if expected_conversion > 0 else 0
            })
        
        # Anomalía 3: CPA alto
        expected_cpa = expected.get('cost_per_acquisition', 0)
        current_cpa = current.get('cost_per_acquisition', 0)
        
        if current_cpa > self.alert_rules['cost_per_acquisition_threshold']:
            anomalies.append({
                'type': 'high_cpa',
                'severity': 'medium',
                'description': f'CPA actual (${current_cpa:.2f}) está por encima del umbral (${self.alert_rules["cost_per_acquisition_threshold"]})',
                'expected_value': expected_cpa,
                'current_value': current_cpa,
                'deviation_percent': ((current_cpa - expected_cpa) / expected_cpa * 100) if expected_cpa > 0 else 0
            })
        
        # Anomalía 4: Degradación de rendimiento
        performance_degradation = self._calculate_performance_degradation(expected, current)
        if performance_degradation > self.alert_rules['performance_degradation_threshold']:
            anomalies.append({
                'type': 'performance_degradation',
                'severity': 'high',
                'description': f'Degradación de rendimiento del {performance_degradation:.1%} detectada',
                'expected_value': 1.0,
                'current_value': 1.0 - performance_degradation,
                'deviation_percent': performance_degradation * 100
            })
        
        # Anomalía 5: Probabilidad de éxito baja
        success_prob = campaign['success_probability']
        if success_prob < self.alert_rules['success_probability_threshold']:
            anomalies.append({
                'type': 'low_success_probability',
                'severity': 'high',
                'description': f'Probabilidad de éxito ({success_prob:.1%}) está por debajo del umbral ({self.alert_rules["success_probability_threshold"]:.1%})',
                'expected_value': self.alert_rules['success_probability_threshold'],
                'current_value': success_prob,
                'deviation_percent': ((success_prob - self.alert_rules['success_probability_threshold']) / self.alert_rules['success_probability_threshold'] * 100)
            })
        
        return anomalies
    
    def _calculate_performance_degradation(self, expected: Dict, current: Dict) -> float:
        """Calcula la degradación de rendimiento general"""
        metrics_to_compare = ['return_on_ad_spend', 'conversion_rate', 'engagement_rate']
        
        total_degradation = 0
        valid_metrics = 0
        
        for metric in metrics_to_compare:
            if metric in expected and metric in current and expected[metric] > 0:
                degradation = max(0, (expected[metric] - current[metric]) / expected[metric])
                total_degradation += degradation
                valid_metrics += 1
        
        return total_degradation / valid_metrics if valid_metrics > 0 else 0
    
    def _calculate_health_score(self, expected: Dict, current: Dict, campaign: Dict) -> float:
        """Calcula un score de salud general de la campaña (0-100)"""
        score = 100
        
        # Penalizar por anomalías
        anomalies = self._detect_anomalies(expected, current, campaign)
        
        for anomaly in anomalies:
            if anomaly['severity'] == 'high':
                score -= 20
            elif anomaly['severity'] == 'medium':
                score -= 10
            elif anomaly['severity'] == 'low':
                score -= 5
        
        # Ajustar por probabilidad de éxito
        success_prob = campaign['success_probability']
        score *= success_prob
        
        # Ajustar por complejidad
        complexity_penalty = {'Baja': 0, 'Media': 5, 'Alta': 10}
        score -= complexity_penalty.get(campaign['complexity'], 0)
        
        return max(0, min(100, score))
    
    def _generate_alerts(self, anomalies: List[Dict], health_score: float, campaign: Dict) -> List[Dict]:
        """Genera alertas basadas en anomalías y score de salud"""
        alerts = []
        
        # Alerta de salud general
        if health_score < 50:
            alerts.append({
                'type': 'critical_health',
                'severity': 'critical',
                'title': 'Salud Crítica de Campaña',
                'message': f'La campaña {campaign["name"]} tiene un score de salud crítico ({health_score:.1f}/100)',
                'action_required': 'Revisión inmediata y posible pausa de campaña',
                'timestamp': datetime.now().isoformat()
            })
        elif health_score < 70:
            alerts.append({
                'type': 'warning_health',
                'severity': 'warning',
                'title': 'Advertencia de Salud',
                'message': f'La campaña {campaign["name"]} tiene un score de salud bajo ({health_score:.1f}/100)',
                'action_required': 'Monitoreo intensivo y optimización',
                'timestamp': datetime.now().isoformat()
            })
        
        # Alertas por anomalías específicas
        for anomaly in anomalies:
            if anomaly['severity'] == 'high':
                alerts.append({
                    'type': f'high_{anomaly["type"]}',
                    'severity': 'high',
                    'title': f'Alerta Alta: {anomaly["type"].replace("_", " ").title()}',
                    'message': anomaly['description'],
                    'action_required': self._get_action_for_anomaly(anomaly['type']),
                    'timestamp': datetime.now().isoformat()
                })
            elif anomaly['severity'] == 'medium':
                alerts.append({
                    'type': f'medium_{anomaly["type"]}',
                    'severity': 'medium',
                    'title': f'Advertencia: {anomaly["type"].replace("_", " ").title()}',
                    'message': anomaly['description'],
                    'action_required': self._get_action_for_anomaly(anomaly['type']),
                    'timestamp': datetime.now().isoformat()
                })
        
        return alerts
    
    def _get_action_for_anomaly(self, anomaly_type: str) -> str:
        """Obtiene la acción recomendada para un tipo de anomalía"""
        actions = {
            'low_roi': 'Revisar estrategia de targeting y optimizar creativos',
            'low_conversion_rate': 'Mejorar landing pages y call-to-actions',
            'high_cpa': 'Optimizar pujas y segmentación de audiencia',
            'performance_degradation': 'Análisis completo de rendimiento y ajustes',
            'low_success_probability': 'Reconsiderar implementación o reducir complejidad'
        }
        return actions.get(anomaly_type, 'Revisar métricas y ajustar estrategia')
    
    def _generate_performance_recommendations(self, anomalies: List[Dict], 
                                            health_score: float, campaign: Dict, 
                                            current_metrics: Dict) -> List[str]:
        """Genera recomendaciones de optimización basadas en el análisis"""
        recommendations = []
        
        # Recomendaciones generales basadas en score de salud
        if health_score < 50:
            recommendations.append("🚨 **Acción inmediata requerida**: La campaña necesita intervención urgente")
        elif health_score < 70:
            recommendations.append("⚠️ **Optimización necesaria**: Implementar mejoras para aumentar el rendimiento")
        else:
            recommendations.append("✅ **Rendimiento aceptable**: Mantener monitoreo y ajustes menores")
        
        # Recomendaciones específicas por anomalías
        for anomaly in anomalies:
            if anomaly['type'] == 'low_roi':
                recommendations.append("💰 **Optimizar ROI**: Revisar targeting, creativos y pujas para mejorar retorno")
            elif anomaly['type'] == 'low_conversion_rate':
                recommendations.append("🎯 **Mejorar conversiones**: Optimizar landing pages, CTAs y experiencia de usuario")
            elif anomaly['type'] == 'high_cpa':
                recommendations.append("💸 **Reducir CPA**: Ajustar segmentación, pujas y calidad de audiencia")
            elif anomaly['type'] == 'performance_degradation':
                recommendations.append("📉 **Detener degradación**: Análisis profundo de causas y implementar correcciones")
            elif anomaly['type'] == 'low_success_probability':
                recommendations.append("🛡️ **Reducir riesgo**: Simplificar implementación o aumentar recursos")
        
        # Recomendaciones basadas en la categoría de campaña
        category = campaign['category']
        if category == 'Personalización con IA' and health_score < 80:
            recommendations.append("🤖 **Mejorar personalización**: Revisar algoritmos de IA y datos de entrada")
        elif category == 'Optimización de Conversión' and health_score < 80:
            recommendations.append("🔄 **Optimizar embudo**: Analizar puntos de fricción y mejorar flujo de conversión")
        elif category == 'Análisis Predictivo' and health_score < 80:
            recommendations.append("📊 **Mejorar predicciones**: Validar modelos y actualizar datos de entrenamiento")
        
        return recommendations
    
    def monitor_portfolio(self, campaign_ids: List[int]) -> Dict[str, Any]:
        """Monitorea un portafolio completo de campañas"""
        portfolio_analysis = {
            'total_campaigns': len(campaign_ids),
            'healthy_campaigns': 0,
            'warning_campaigns': 0,
            'critical_campaigns': 0,
            'total_alerts': 0,
            'campaign_analyses': [],
            'portfolio_health_score': 0,
            'recommendations': []
        }
        
        health_scores = []
        all_alerts = []
        
        for campaign_id in campaign_ids:
            analysis = self.analyze_campaign_performance(campaign_id)
            
            if 'error' not in analysis:
                portfolio_analysis['campaign_analyses'].append(analysis)
                
                health_score = analysis['health_score']
                health_scores.append(health_score)
                
                # Categorizar por salud
                if health_score >= 80:
                    portfolio_analysis['healthy_campaigns'] += 1
                elif health_score >= 50:
                    portfolio_analysis['warning_campaigns'] += 1
                else:
                    portfolio_analysis['critical_campaigns'] += 1
                
                # Contar alertas
                portfolio_analysis['total_alerts'] += len(analysis['alerts'])
                all_alerts.extend(analysis['alerts'])
        
        # Calcular salud del portafolio
        if health_scores:
            portfolio_analysis['portfolio_health_score'] = np.mean(health_scores)
        
        # Generar recomendaciones del portafolio
        portfolio_analysis['recommendations'] = self._generate_portfolio_recommendations(portfolio_analysis)
        
        # Agregar alertas críticas del portafolio
        critical_alerts = [alert for alert in all_alerts if alert['severity'] in ['critical', 'high']]
        portfolio_analysis['critical_alerts'] = critical_alerts
        
        return portfolio_analysis
    
    def _generate_portfolio_recommendations(self, portfolio_analysis: Dict) -> List[str]:
        """Genera recomendaciones para el portafolio completo"""
        recommendations = []
        
        total_campaigns = portfolio_analysis['total_campaigns']
        healthy = portfolio_analysis['healthy_campaigns']
        warning = portfolio_analysis['warning_campaigns']
        critical = portfolio_analysis['critical_campaigns']
        portfolio_health = portfolio_analysis['portfolio_health_score']
        
        # Recomendaciones basadas en distribución de salud
        if critical > total_campaigns * 0.3:
            recommendations.append("🚨 **Portafolio crítico**: Más del 30% de campañas están en estado crítico. Revisión urgente requerida.")
        elif warning > total_campaigns * 0.5:
            recommendations.append("⚠️ **Portafolio en riesgo**: Más del 50% de campañas necesitan optimización.")
        elif healthy > total_campaigns * 0.8:
            recommendations.append("✅ **Portafolio saludable**: Más del 80% de campañas están funcionando bien.")
        
        # Recomendaciones basadas en salud general
        if portfolio_health < 50:
            recommendations.append("📉 **Salud del portafolio crítica**: Implementar estrategia de recuperación inmediata")
        elif portfolio_health < 70:
            recommendations.append("📊 **Salud del portafolio moderada**: Plan de optimización recomendado")
        else:
            recommendations.append("🎯 **Portafolio exitoso**: Mantener estrategia actual con monitoreo continuo")
        
        # Recomendaciones basadas en alertas
        total_alerts = portfolio_analysis['total_alerts']
        if total_alerts > total_campaigns * 2:
            recommendations.append("🔔 **Alto volumen de alertas**: Revisar procesos y automatización")
        
        return recommendations
    
    def send_alert_notification(self, alert: Dict, recipient_email: str = None) -> bool:
        """Envía notificación de alerta por email"""
        if not self.notification_channels['email'] or not recipient_email:
            return False
        
        try:
            # Configurar email (esto requeriría configuración SMTP real)
            msg = MimeMultipart()
            msg['From'] = "alerts@ai-marketing.com"
            msg['To'] = recipient_email
            msg['Subject'] = f"🚨 Alerta de Marketing IA: {alert['title']}"
            
            body = f"""
            {alert['message']}
            
            Acción requerida: {alert['action_required']}
            
            Timestamp: {alert['timestamp']}
            
            ---
            Sistema de Alertas Inteligentes
            Campañas de Marketing con IA
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Aquí iría la lógica real de envío de email
            self.logger.info(f"Alerta enviada a {recipient_email}: {alert['title']}")
            
            # Guardar en historial
            self.alert_history.append({
                'alert': alert,
                'recipient': recipient_email,
                'sent_at': datetime.now().isoformat(),
                'status': 'sent'
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error enviando alerta: {str(e)}")
            return False
    
    def get_alert_dashboard_data(self) -> Dict[str, Any]:
        """Obtiene datos para el dashboard de alertas"""
        return {
            'total_alerts_today': len([a for a in self.alert_history if 
                                     datetime.fromisoformat(a['sent_at']).date() == datetime.now().date()]),
            'critical_alerts': len([a for a in self.alert_history if 
                                  a['alert']['severity'] == 'critical']),
            'alerts_by_severity': {
                'critical': len([a for a in self.alert_history if a['alert']['severity'] == 'critical']),
                'high': len([a for a in self.alert_history if a['alert']['severity'] == 'high']),
                'medium': len([a for a in self.alert_history if a['alert']['severity'] == 'medium']),
                'low': len([a for a in self.alert_history if a['alert']['severity'] == 'low'])
            },
            'recent_alerts': self.alert_history[-10:],  # Últimas 10 alertas
            'dashboard_timestamp': datetime.now().isoformat()
        }

def main():
    """Función principal de demostración"""
    print("=== SISTEMA DE ALERTAS INTELIGENTES ===")
    
    # Inicializar sistema de alertas
    alerts_system = IntelligentAlertsSystem()
    
    # Analizar campaña individual
    print("Analizando campaña individual...")
    campaign_analysis = alerts_system.analyze_campaign_performance(1)
    
    if 'error' not in campaign_analysis:
        print(f"\n📊 ANÁLISIS DE CAMPAÑA")
        print(f"Campaña: {campaign_analysis['campaign_name']}")
        print(f"Score de salud: {campaign_analysis['health_score']:.1f}/100")
        print(f"Anomalías detectadas: {campaign_analysis['anomalies_detected']}")
        print(f"Alertas generadas: {len(campaign_analysis['alerts'])}")
        
        print(f"\n🚨 ALERTAS")
        for alert in campaign_analysis['alerts']:
            print(f"• [{alert['severity'].upper()}] {alert['title']}")
            print(f"  {alert['message']}")
            print(f"  Acción: {alert['action_required']}")
        
        print(f"\n💡 RECOMENDACIONES")
        for recommendation in campaign_analysis['recommendations']:
            print(f"• {recommendation}")
    
    # Monitorear portafolio
    print(f"\n🔄 MONITOREANDO PORTAFOLIO...")
    portfolio_campaigns = [1, 2, 3, 4, 5, 10, 15, 20]
    portfolio_analysis = alerts_system.monitor_portfolio(portfolio_campaigns)
    
    print(f"\n📈 ANÁLISIS DE PORTAFOLIO")
    print(f"Total de campañas: {portfolio_analysis['total_campaigns']}")
    print(f"Saludables: {portfolio_analysis['healthy_campaigns']}")
    print(f"Con advertencias: {portfolio_analysis['warning_campaigns']}")
    print(f"Críticas: {portfolio_analysis['critical_campaigns']}")
    print(f"Total de alertas: {portfolio_analysis['total_alerts']}")
    print(f"Salud del portafolio: {portfolio_analysis['portfolio_health_score']:.1f}/100")
    
    print(f"\n💡 RECOMENDACIONES DEL PORTAFOLIO")
    for recommendation in portfolio_analysis['recommendations']:
        print(f"• {recommendation}")
    
    # Dashboard de alertas
    print(f"\n📊 DASHBOARD DE ALERTAS")
    dashboard_data = alerts_system.get_alert_dashboard_data()
    print(f"Alertas hoy: {dashboard_data['total_alerts_today']}")
    print(f"Alertas críticas: {dashboard_data['critical_alerts']}")
    
    print(f"\n✅ Sistema de alertas configurado y funcionando")

if __name__ == "__main__":
    main()
