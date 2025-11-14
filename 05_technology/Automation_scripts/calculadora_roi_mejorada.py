#!/usr/bin/env python3
"""
Calculadora de ROI Mejorada
Calcula ROI, Payback Period, NPV y otras métricas financieras
"""

import math
from typing import List, Dict, Tuple

class ROICalculator:
    def __init__(self):
        self.scenarios = {}
        
    def calculate_roi(self, investment: float, returns: float) -> float:
        """
        Calcula ROI básico
        
        Args:
            investment: Inversión inicial
            returns: Retornos totales
            
        Returns:
            ROI como porcentaje
        """
        if investment == 0:
            return 0
        return ((returns - investment) / investment) * 100
    
    def calculate_payback_period(self, investment: float, monthly_cash_flow: float) -> float:
        """
        Calcula periodo de payback
        
        Args:
            investment: Inversión inicial
            monthly_cash_flow: Flujo de caja mensual
            
        Returns:
            Meses para recuperar inversión
        """
        if monthly_cash_flow == 0:
            return float('inf')
        return investment / monthly_cash_flow
    
    def calculate_npv(self, investment: float, cash_flows: List[float], discount_rate: float = 0.1) -> float:
        """
        Calcula Net Present Value
        
        Args:
            investment: Inversión inicial
            cash_flows: Lista de flujos de caja futuros
            discount_rate: Tasa de descuento (default 10%)
            
        Returns:
            NPV
        """
        npv = -investment
        for i, cf in enumerate(cash_flows):
            npv += cf / (1 + discount_rate) ** (i + 1)
        return npv
    
    def calculate_ltv_cac_ratio(self, ltv: float, cac: float) -> float:
        """
        Calcula ratio LTV/CAC
        
        Args:
            ltv: Lifetime Value
            cac: Customer Acquisition Cost
            
        Returns:
            Ratio LTV/CAC
        """
        if cac == 0:
            return float('inf')
        return ltv / cac
    
    def calculate_irr(self, investment: float, cash_flows: List[float], max_iterations: int = 100) -> float:
        """
        Calcula Internal Rate of Return
        
        Args:
            investment: Inversión inicial
            cash_flows: Lista de flujos de caja futuros
            max_iterations: Máximo de iteraciones
            
        Returns:
            IRR como decimal
        """
        def npv_for_irr(rate):
            npv = -investment
            for i, cf in enumerate(cash_flows):
                npv += cf / (1 + rate) ** (i + 1)
            return npv
        
        # Método de Newton-Raphson
        rate = 0.1  # Estimación inicial
        for _ in range(max_iterations):
            npv = npv_for_irr(rate)
            npv_derivative = -investment / (1 + rate) ** 2
            for i, cf in enumerate(cash_flows):
                npv_derivative -= (i + 1) * cf / (1 + rate) ** (i + 2)
            
            new_rate = rate - npv / npv_derivative
            
            if abs(new_rate - rate) < 1e-6:
                return new_rate
            
            rate = new_rate
        
        return rate
    
    def calculate_gross_margin(self, revenue: float, cogs: float) -> float:
        """
        Calcula gross margin
        
        Args:
            revenue: Revenue total
            cogs: Cost of goods sold
            
        Returns:
            Gross margin como porcentaje
        """
        if revenue == 0:
            return 0
        return ((revenue - cogs) / revenue) * 100
    
    def analyze_pivote(self, pivote_name: str, investment: float, 
                       monthly_revenue: Dict[int, float], 
                       monthly_costs: Dict[int, float],
                       ltv: float, cac: float) -> Dict:
        """
        Analiza un pivote completo
        
        Args:
            pivote_name: Nombre del pivote
            investment: Inversión inicial
            monthly_revenue: Revenue por mes
            monthly_costs: Costos por mes
            ltv: Lifetime Value
            cac: Customer Acquisition Cost
            
        Returns:
            Diccionario con todas las métricas
        """
        # Calcular cash flows
        cash_flows = []
        for month in sorted(monthly_revenue.keys()):
            revenue = monthly_revenue.get(month, 0)
            costs = monthly_costs.get(month, 0)
            cash_flows.append(revenue - costs)
        
        total_returns = sum(cash_flows)
        years = len(cash_flows) / 12
        
        # Calcular todas las métricas
        roi = self.calculate_roi(investment, total_returns)
        avg_monthly_cash_flow = total_returns / len(cash_flows)
        payback = self.calculate_payback_period(investment, avg_monthly_cash_flow)
        npv = self.calculate_npv(investment, cash_flows)
        irr = self.calculate_irr(investment, cash_flows)
        ltv_cac = self.calculate_ltv_cac_ratio(ltv, cac)
        
        return {
            'pivote': pivote_name,
            'investment': investment,
            'total_returns': total_returns,
            'roi': roi,
            'payback_months': payback,
            'npv': npv,
            'irr': irr * 100,
            'ltv_cac': ltv_cac,
            'ltv': ltv,
            'cac': cac,
            'years': years
        }
    
    def compare_pivotes(self, pivotes: List[Dict]) -> str:
        """
        Compara múltiples pivotes
        
        Args:
            pivotes: Lista de análisis de pivotes
            
        Returns:
            String con comparación formateada
        """
        output = "\n" + "=" * 100 + "\n"
        output += "COMPARACIÓN DE PIVOTES\n"
        output += "=" * 100 + "\n\n"
        
        # Sort por ROI
        pivotes_sorted = sorted(pivotes, key=lambda x: x['roi'], reverse=True)
        
        # Header
        output += f"{'Pivote':<30} {'Inversión':>15} {'ROI %':>12} {'Payback':>12} {'NPV':>15} {'LTV/CAC':>12}\n"
        output += "-" * 100 + "\n"
        
        for p in pivotes_sorted:
            output += f"{p['pivote']:<30} ${p['investment']:>14,.0f} {p['roi']:>11.1f}% "
            output += f"{p['payback_months']:>10.1f}m ${p['npv']:>13,.0f} {p['ltv_cac']:>10.1f}:1\n"
        
        output += "\n" + "=" * 100 + "\n"
        output += "RECOMENDACIÓN\n"
        output += "=" * 100 + "\n\n"
        
        best = pivotes_sorted[0]
        output += f"⭐ MEJOR OPCIÓN: {best['pivote']}\n\n"
        output += f"ROI: {best['roi']:.1f}%\n"
        output += f"Payback Period: {best['payback_months']:.1f} meses\n"
        output += f"NPV: ${best['npv']:,.0f}\n"
        output += f"IRR: {best['irr']:.1f}%\n"
        output += f"LTV/CAC: {best['ltv_cac']:.1f}:1\n"
        
        return output


def main():
    """
    Función principal - Demo de uso
    """
    calculator = ROICalculator()
    
    # Datos de ejemplo para los 3 pivotes
    print("Calculando métricas para los 3 pivotes...\n")
    
    # Pivote 1: Nuevos Segmentos
    pivote1 = calculator.analyze_pivote(
        pivote_name="Pivote 1: Nuevos Segmentos",
        investment=500_000,
        monthly_revenue={
            1: 45_000, 2: 60_000, 3: 75_000, 4: 90_000, 5: 105_000, 6: 120_000,
            7: 135_000, 8: 150_000, 9: 165_000, 10: 180_000, 11: 195_000, 12: 210_000,
            13: 225_000, 14: 240_000, 15: 255_000, 16: 270_000, 17: 285_000, 18: 300_000,
            19: 315_000, 20: 330_000, 21: 345_000, 22: 360_000, 23: 375_000, 24: 390_000,
            25: 405_000, 26: 420_000, 27: 435_000, 28: 450_000, 29: 465_000, 30: 480_000,
            31: 495_000, 32: 510_000, 33: 525_000, 34: 540_000, 35: 555_000, 36: 570_000
        },
        monthly_costs={month: 25_000 for month in range(1, 37)},
        ltv=45_000,
        cac=4_200
    )
    
    # Pivote 2: Nuevos Casos de Uso
    pivote2 = calculator.analyze_pivote(
        pivote_name="Pivote 2: Nuevos Casos de Uso",
        investment=400_000,
        monthly_revenue={
            1: 50_000, 2: 70_000, 3: 90_000, 4: 110_000, 5: 130_000, 6: 150_000,
            7: 170_000, 8: 190_000, 9: 210_000, 10: 230_000, 11: 250_000, 12: 270_000,
            13: 290_000, 14: 310_000, 15: 330_000, 16: 350_000, 17: 370_000, 18: 390_000,
            19: 410_000, 20: 430_000, 21: 450_000, 22: 470_000, 23: 490_000, 24: 510_000,
            25: 530_000, 26: 550_000, 27: 570_000, 28: 590_000, 29: 610_000, 30: 630_000,
            31: 650_000, 32: 670_000, 33: 690_000, 34: 710_000, 35: 730_000, 36: 750_000
        },
        monthly_costs={month: 30_000 for month in range(1, 37)},
        ltv=60_000,
        cac=3_500
    )
    
    # Pivote 3: Angulos Alternativos (LICENSING)
    pivote3 = calculator.analyze_pivote(
        pivote_name="Pivote 3: Licensing Technology",
        investment=200_000,
        monthly_revenue={
            1: 85_000, 2: 120_000, 3: 155_000, 4: 190_000, 5: 225_000, 6: 260_000,
            7: 295_000, 8: 330_000, 9: 365_000, 10: 400_000, 11: 435_000, 12: 470_000,
            13: 505_000, 14: 540_000, 15: 575_000, 16: 610_000, 17: 645_000, 18: 680_000,
            19: 715_000, 20: 750_000, 21: 785_000, 22: 820_000, 23: 855_000, 24: 890_000,
            25: 925_000, 26: 960_000, 27: 995_000, 28: 1_030_000, 29: 1_065_000, 30: 1_100_000,
            31: 1_135_000, 32: 1_170_000, 33: 1_205_000, 34: 1_240_000, 35: 1_275_000, 36: 1_300_000
        },
        monthly_costs={month: 15_000 for month in range(1, 37)},
        ltv=95_000,
        cac=2_875
    )
    
    # Comparar pivotes
    comparison = calculator.compare_pivotes([pivote1, pivote2, pivote3])
    print(comparison)
    
    print("\n" + "=" * 100)
    print("MÉTRICAS DETALLADAS POR PIVOTE")
    print("=" * 100 + "\n")
    
    for p in [pivote1, pivote2, pivote3]:
        print(f"\n{p['pivote']}:")
        print(f"  Inversión: ${p['investment']:,.0f}")
        print(f"  Retornos Totales: ${p['total_returns']:,.0f}")
        print(f"  ROI: {p['roi']:.1f}%")
        print(f"  Payback: {p['payback_months']:.1f} meses")
        print(f"  NPV: ${p['npv']:,.0f}")
        print(f"  IRR: {p['irr']:.1f}%")
        print(f"  LTV: ${p['ltv']:,.0f}")
        print(f"  CAC: ${p['cac']:,.0f}")
        print(f"  LTV/CAC: {p['ltv_cac']:.1f}:1")


if __name__ == "__main__":
    main()



