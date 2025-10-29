#!/usr/bin/env python3
"""
Simulador de Escenarios Financieros Interactivo
Pivote 3: Licensing Technology
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json

class SimuladorFinanciero:
    def __init__(self):
        self.scenarios = {
            'conservador': {
                'growth_rate': 0.15,
                'churn_rate': 0.08,
                'cac': 200,
                'ltv': 4000,
                'gross_margin': 0.90,
                'opex_ratio': 0.60
            },
            'base': {
                'growth_rate': 0.25,
                'churn_rate': 0.05,
                'cac': 150,
                'ltv': 5000,
                'gross_margin': 0.92,
                'opex_ratio': 0.55
            },
            'optimista': {
                'growth_rate': 0.35,
                'churn_rate': 0.03,
                'cac': 120,
                'ltv': 6000,
                'gross_margin': 0.95,
                'opex_ratio': 0.50
            }
        }
        
    def simular_escenario(self, scenario_name, years=3, initial_customers=100):
        """Simula un escenario financiero completo"""
        params = self.scenarios[scenario_name]
        
        # Inicializar arrays
        months = years * 12
        customers = np.zeros(months)
        revenue = np.zeros(months)
        costs = np.zeros(months)
        profit = np.zeros(months)
        cumulative_profit = np.zeros(months)
        
        # Valores iniciales
        customers[0] = initial_customers
        monthly_growth = params['growth_rate'] / 12
        monthly_churn = params['churn_rate'] / 12
        
        # Simular mes a mes
        for month in range(1, months):
            # Nuevos clientes
            new_customers = customers[month-1] * monthly_growth
            
            # Pérdida de clientes
            lost_customers = customers[month-1] * monthly_churn
            
            # Clientes totales
            customers[month] = customers[month-1] + new_customers - lost_customers
            
            # Revenue (asumiendo $100/mes por cliente)
            revenue[month] = customers[month] * 100
            
            # Costs
            acquisition_cost = new_customers * params['cac']
            opex_cost = revenue[month] * params['opex_ratio']
            costs[month] = acquisition_cost + opex_cost
            
            # Profit
            profit[month] = revenue[month] * params['gross_margin'] - costs[month]
            cumulative_profit[month] = cumulative_profit[month-1] + profit[month]
        
        return {
            'customers': customers,
            'revenue': revenue,
            'costs': costs,
            'profit': profit,
            'cumulative_profit': cumulative_profit,
            'params': params
        }
    
    def calcular_metricas(self, data):
        """Calcula métricas clave del escenario"""
        final_revenue = data['revenue'][-1]
        total_profit = data['cumulative_profit'][-1]
        final_customers = data['customers'][-1]
        
        # ROI
        initial_investment = 200000  # $200K
        roi = (total_profit / initial_investment) * 100
        
        # Payback period
        payback_month = None
        for month, cum_profit in enumerate(data['cumulative_profit']):
            if cum_profit >= initial_investment:
                payback_month = month
                break
        
        payback_period = payback_month / 12 if payback_month else None
        
        # LTV/CAC
        ltv_cac = data['params']['ltv'] / data['params']['cac']
        
        return {
            'final_revenue': final_revenue,
            'total_profit': total_profit,
            'final_customers': final_customers,
            'roi': roi,
            'payback_period': payback_period,
            'ltv_cac': ltv_cac,
            'gross_margin': data['params']['gross_margin']
        }
    
    def generar_comparacion(self):
        """Genera comparación de los 3 escenarios"""
        print("=" * 80)
        print("SIMULADOR DE ESCENARIOS FINANCIEROS - PIVOTE 3")
        print("=" * 80)
        print()
        
        resultados = {}
        
        for scenario_name in self.scenarios.keys():
            data = self.simular_escenario(scenario_name)
            metricas = self.calcular_metricas(data)
            resultados[scenario_name] = metricas
            
            print(f"📊 ESCENARIO {scenario_name.upper()}")
            print("-" * 40)
            print(f"Revenue Final (Año 3): ${metricas['final_revenue']:,.0f}")
            print(f"Profit Total:           ${metricas['total_profit']:,.0f}")
            print(f"Clientes Finales:       {metricas['final_customers']:,.0f}")
            print(f"ROI:                    {metricas['roi']:,.0f}%")
            print(f"Payback Period:         {metricas['payback_period']:.1f} años" if metricas['payback_period'] else "Payback Period:         No alcanzado")
            print(f"LTV/CAC Ratio:          {metricas['ltv_cac']:.1f}:1")
            print(f"Gross Margin:           {metricas['gross_margin']:.1%}")
            print()
        
        # Comparación
        print("📈 COMPARACIÓN DE ESCENARIOS")
        print("-" * 40)
        print(f"{'Métrica':<20} {'Conservador':<12} {'Base':<12} {'Optimista':<12}")
        print("-" * 60)
        
        for metrica in ['final_revenue', 'total_profit', 'roi', 'ltv_cac']:
            valores = [resultados[s][metrica] for s in self.scenarios.keys()]
            print(f"{metrica:<20} {valores[0]:<12,.0f} {valores[1]:<12,.0f} {valores[2]:<12,.0f}")
        
        return resultados
    
    def analisis_sensibilidad(self, parameter, values):
        """Análisis de sensibilidad para un parámetro"""
        print(f"\n🔍 ANÁLISIS DE SENSIBILIDAD: {parameter.upper()}")
        print("-" * 50)
        
        base_scenario = self.scenarios['base'].copy()
        
        for value in values:
            base_scenario[parameter] = value
            temp_scenarios = {'test': base_scenario}
            temp_sim = SimuladorFinanciero()
            temp_sim.scenarios = temp_scenarios
            
            data = temp_sim.simular_escenario('test')
            metricas = temp_sim.calcular_metricas(data)
            
            print(f"{parameter} = {value:<8} | ROI: {metricas['roi']:,.0f}% | Revenue: ${metricas['final_revenue']:,.0f}")
    
    def generar_recomendaciones(self, resultados):
        """Genera recomendaciones basadas en los resultados"""
        print("\n🎯 RECOMENDACIONES ESTRATÉGICAS")
        print("=" * 50)
        
        # Mejor escenario
        mejor_roi = max(resultados.keys(), key=lambda x: resultados[x]['roi'])
        print(f"✅ Escenario Recomendado: {mejor_roi.upper()}")
        print(f"   ROI: {resultados[mejor_roi]['roi']:,.0f}%")
        print(f"   Revenue: ${resultados[mejor_roi]['final_revenue']:,.0f}")
        
        # Análisis de riesgo
        print(f"\n⚠️  Análisis de Riesgo:")
        conservador_roi = resultados['conservador']['roi']
        optimista_roi = resultados['optimista']['roi']
        diferencia = optimista_roi - conservador_roi
        
        print(f"   Diferencia ROI (Optimista vs Conservador): {diferencia:,.0f}%")
        
        if diferencia > 1000:
            print("   🔴 Alto riesgo - Gran variabilidad en resultados")
        elif diferencia > 500:
            print("   🟡 Riesgo medio - Variabilidad moderada")
        else:
            print("   🟢 Bajo riesgo - Resultados predecibles")
        
        # Recomendaciones específicas
        print(f"\n📋 Acciones Recomendadas:")
        print(f"   1. Enfocar en escenario {mejor_roi}")
        print(f"   2. Monitorear métricas clave mensualmente")
        print(f"   3. Preparar planes de contingencia")
        print(f"   4. Optimizar CAC y LTV continuamente")

def main():
    simulador = SimuladorFinanciero()
    
    # Generar comparación principal
    resultados = simulador.generar_comparacion()
    
    # Análisis de sensibilidad
    print("\n" + "=" * 80)
    simulador.analisis_sensibilidad('growth_rate', [0.15, 0.20, 0.25, 0.30, 0.35])
    simulador.analisis_sensibilidad('churn_rate', [0.03, 0.05, 0.08, 0.10, 0.12])
    simulador.analisis_sensibilidad('cac', [100, 120, 150, 200, 250])
    
    # Generar recomendaciones
    simulador.generar_recomendaciones(resultados)
    
    print("\n" + "=" * 80)
    print("✅ Simulación completada exitosamente")
    print("=" * 80)

if __name__ == "__main__":
    main()

