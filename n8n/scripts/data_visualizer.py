#!/usr/bin/env python3
"""
Data Visualizer - Generador de visualizaciones de datos
Crea gráficos y dashboards visuales de métricas
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import pandas as pd
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False
    print("Warning: matplotlib/pandas not installed. Visualization disabled.")

class DataVisualizer:
    """Visualizador de datos de automatización"""
    
    def __init__(self, api_base_url: str, api_key: str):
        self.api_base_url = api_base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def fetch_metrics_timeseries(self, period: str = '30d') -> Dict:
        """Obtiene métricas en serie temporal"""
        url = f"{self.api_base_url}/analytics/timeseries"
        params = {"period": period}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
    
    def create_recovery_rate_chart(self, data: Dict, output_file: str = None) -> str:
        """Crea gráfico de tasa de recuperación"""
        if not HAS_VISUALIZATION:
            return None
        
        if not output_file:
            output_file = f"recovery_rate_{datetime.now().strftime('%Y%m%d')}.png"
        
        dates = [datetime.fromisoformat(d['date']) for d in data.get('daily', [])]
        recovery_rates = [d.get('recoveryRate', 0) for d in data.get('daily', [])]
        
        plt.figure(figsize=(12, 6))
        plt.plot(dates, recovery_rates, marker='o', linewidth=2, markersize=6)
        plt.title('Cart Recovery Rate Over Time', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Recovery Rate (%)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def create_conversion_funnel(self, data: Dict, output_file: str = None) -> str:
        """Crea gráfico de embudo de conversión"""
        if not HAS_VISUALIZATION:
            return None
        
        if not output_file:
            output_file = f"conversion_funnel_{datetime.now().strftime('%Y%m%d')}.png"
        
        stages = ['Visitors', 'Cart Added', 'Checkout Started', 'Purchase Completed']
        values = [
            data.get('totalVisitors', 0),
            data.get('cartAdded', 0),
            data.get('checkoutStarted', 0),
            data.get('purchasesCompleted', 0)
        ]
        
        # Calcular porcentajes
        percentages = [(v / values[0] * 100) if values[0] > 0 else 0 for v in values]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Gráfico de barras
        ax1.barh(stages, values, color=['#4CAF50', '#2196F3', '#FF9800', '#F44336'])
        ax1.set_xlabel('Count', fontsize=12)
        ax1.set_title('Conversion Funnel - Absolute Values', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Gráfico de porcentajes
        ax2.barh(stages, percentages, color=['#4CAF50', '#2196F3', '#FF9800', '#F44336'])
        ax2.set_xlabel('Percentage (%)', fontsize=12)
        ax2.set_title('Conversion Funnel - Percentages', fontsize=14, fontweight='bold')
        ax2.set_xlim(0, 100)
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Agregar valores en barras
        for i, (val, pct) in enumerate(zip(values, percentages)):
            ax1.text(val, i, f' {val:,}', va='center', fontsize=10)
            ax2.text(pct, i, f' {pct:.1f}%', va='center', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def create_segment_distribution(self, data: Dict, output_file: str = None) -> str:
        """Crea gráfico de distribución de segmentos"""
        if not HAS_VISUALIZATION:
            return None
        
        if not output_file:
            output_file = f"segment_distribution_{datetime.now().strftime('%Y%m%d')}.png"
        
        segments = data.get('segments', {})
        labels = list(segments.keys())
        sizes = list(segments.values())
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        
        plt.figure(figsize=(10, 8))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        plt.title('Customer Segment Distribution', fontsize=16, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def create_roi_timeline(self, data: Dict, output_file: str = None) -> str:
        """Crea gráfico de ROI en el tiempo"""
        if not HAS_VISUALIZATION:
            return None
        
        if not output_file:
            output_file = f"roi_timeline_{datetime.now().strftime('%Y%m%d')}.png"
        
        dates = [datetime.fromisoformat(d['date']) for d in data.get('daily', [])]
        roi_values = [d.get('roi', 0) for d in data.get('daily', [])]
        revenue = [d.get('revenue', 0) for d in data.get('daily', [])]
        costs = [d.get('costs', 0) for d in data.get('daily', [])]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # ROI
        ax1.plot(dates, roi_values, marker='o', linewidth=2, color='#4CAF50', label='ROI %')
        ax1.axhline(y=100, color='r', linestyle='--', alpha=0.5, label='Break-even')
        ax1.set_title('ROI Over Time', fontsize=14, fontweight='bold')
        ax1.set_ylabel('ROI (%)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=7))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # Revenue vs Costs
        ax2.plot(dates, revenue, marker='o', linewidth=2, color='#2196F3', label='Revenue')
        ax2.plot(dates, costs, marker='s', linewidth=2, color='#F44336', label='Costs')
        ax2.fill_between(dates, revenue, costs, where=[r > c for r, c in zip(revenue, costs)], 
                        alpha=0.3, color='green', label='Profit')
        ax2.set_title('Revenue vs Costs', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Amount ($)', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax2.xaxis.set_major_locator(mdates.DayLocator(interval=7))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def generate_dashboard(self, period: str = '30d', output_dir: str = 'charts') -> Dict:
        """Genera dashboard completo con múltiples gráficos"""
        if not HAS_VISUALIZATION:
            print("Visualization libraries not available. Install: pip install matplotlib pandas")
            return {}
        
        # Crear directorio si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Obtener datos
        timeseries_data = self.fetch_metrics_timeseries(period)
        
        files = {}
        
        # Recovery rate chart
        try:
            recovery_file = self.create_recovery_rate_chart(
                timeseries_data,
                f"{output_dir}/recovery_rate_{datetime.now().strftime('%Y%m%d')}.png"
            )
            if recovery_file:
                files['recovery_rate'] = recovery_file
        except Exception as e:
            print(f"Error creating recovery rate chart: {e}")
        
        # Conversion funnel
        try:
            funnel_file = self.create_conversion_funnel(
                timeseries_data,
                f"{output_dir}/conversion_funnel_{datetime.now().strftime('%Y%m%d')}.png"
            )
            if funnel_file:
                files['conversion_funnel'] = funnel_file
        except Exception as e:
            print(f"Error creating conversion funnel: {e}")
        
        # Segment distribution
        try:
            segment_file = self.create_segment_distribution(
                timeseries_data,
                f"{output_dir}/segment_distribution_{datetime.now().strftime('%Y%m%d')}.png"
            )
            if segment_file:
                files['segment_distribution'] = segment_file
        except Exception as e:
            print(f"Error creating segment distribution: {e}")
        
        # ROI timeline
        try:
            roi_file = self.create_roi_timeline(
                timeseries_data,
                f"{output_dir}/roi_timeline_{datetime.now().strftime('%Y%m%d')}.png"
            )
            if roi_file:
                files['roi_timeline'] = roi_file
        except Exception as e:
            print(f"Error creating ROI timeline: {e}")
        
        return {
            'generatedAt': datetime.now().isoformat(),
            'period': period,
            'files': files
        }


def main():
    """Ejemplo de uso"""
    api_url = os.getenv("API_BASE_URL", "https://api.yourdomain.com")
    api_key = os.getenv("API_KEY", "your_api_key_here")
    
    visualizer = DataVisualizer(api_url, api_key)
    
    # Generar dashboard
    result = visualizer.generate_dashboard('30d', 'charts')
    
    print("=" * 50)
    print("DASHBOARD GENERATED")
    print("=" * 50)
    print(f"\nPeriod: {result.get('period', 'N/A')}")
    print(f"\nCharts Generated:")
    for chart_type, file_path in result.get('files', {}).items():
        print(f"  {chart_type}: {file_path}")


if __name__ == "__main__":
    main()




