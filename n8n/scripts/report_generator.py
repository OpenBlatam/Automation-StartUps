#!/usr/bin/env python3
"""
Report Generator - Generador avanzado de reportes ejecutivos
Crea reportes completos en múltiples formatos
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import csv

class ReportGenerator:
    """Generador de reportes ejecutivos"""
    
    def __init__(self, api_base_url: str, api_key: str):
        self.api_base_url = api_base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def fetch_all_metrics(self, period: str = '30d') -> Dict:
        """Obtiene todas las métricas consolidadas"""
        metrics = {}
        
        # Cart abandonment
        try:
            response = requests.get(
                f"{self.api_base_url}/analytics/cart-abandonment",
                headers=self.headers,
                params={"period": period}
            )
            metrics['cartAbandonment'] = response.json()
        except:
            metrics['cartAbandonment'] = {}
        
        # Email performance
        try:
            response = requests.get(
                f"{self.api_base_url}/analytics/email-performance",
                headers=self.headers,
                params={"period": period}
            )
            metrics['email'] = response.json()
        except:
            metrics['email'] = {}
        
        # Conversion
        try:
            response = requests.get(
                f"{self.api_base_url}/analytics/conversion",
                headers=self.headers,
                params={"period": period}
            )
            metrics['conversion'] = response.json()
        except:
            metrics['conversion'] = {}
        
        # A/B Testing
        try:
            response = requests.get(
                f"{self.api_base_url}/analytics/ab-test",
                headers=self.headers,
                params={"period": period}
            )
            metrics['abTesting'] = response.json()
        except:
            metrics['abTesting'] = {}
        
        return metrics
    
    def generate_executive_summary(self, metrics: Dict) -> Dict:
        """Genera resumen ejecutivo"""
        cart = metrics.get('cartAbandonment', {})
        email = metrics.get('email', {})
        conversion = metrics.get('conversion', {})
        ab = metrics.get('abTesting', {})
        
        summary = {
            'period': '30d',
            'generatedAt': datetime.now().isoformat(),
            'keyMetrics': {
                'cartAbandonmentRate': cart.get('cartAbandonmentRate', 0),
                'recoveryRate': cart.get('recoveryRate', 0),
                'recoveredValue': cart.get('recoveredValue', 0),
                'emailOpenRate': email.get('openRate', 0),
                'emailClickRate': email.get('clickRate', 0),
                'conversionRate': conversion.get('conversionRate', 0),
                'revenue': conversion.get('revenue', 0),
                'averageOrderValue': conversion.get('averageOrderValue', 0)
            },
            'insights': [],
            'recommendations': []
        }
        
        # Insights
        if summary['keyMetrics']['recoveryRate'] > 40:
            summary['insights'].append({
                'type': 'positive',
                'message': 'Excellent cart recovery rate - above industry average'
            })
        
        if summary['keyMetrics']['emailOpenRate'] < 25:
            summary['insights'].append({
                'type': 'warning',
                'message': 'Email open rate below target - consider optimizing subject lines'
            })
        
        if summary['keyMetrics']['conversionRate'] > 15:
            summary['insights'].append({
                'type': 'positive',
                'message': 'Strong conversion rate - automation working effectively'
            })
        
        # Recommendations
        if summary['keyMetrics']['cartAbandonmentRate'] > 70:
            summary['recommendations'].append({
                'priority': 'high',
                'action': 'Review checkout process',
                'reason': 'High abandonment rate indicates potential friction'
            })
        
        if summary['keyMetrics']['emailClickRate'] < 8:
            summary['recommendations'].append({
                'priority': 'medium',
                'action': 'Improve email CTAs',
                'reason': 'Low click rate suggests CTAs need optimization'
            })
        
        return summary
    
    def generate_csv_report(self, metrics: Dict, output_file: str = None) -> str:
        """Genera reporte en formato CSV"""
        if not output_file:
            output_file = f"report_{datetime.now().strftime('%Y%m%d')}.csv"
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Metric', 'Value', 'Category'])
            
            # Cart abandonment
            cart = metrics.get('cartAbandonment', {})
            writer.writerow(['Cart Abandonment Rate', cart.get('cartAbandonmentRate', 0), 'Cart'])
            writer.writerow(['Recovery Rate', cart.get('recoveryRate', 0), 'Cart'])
            writer.writerow(['Recovered Value', cart.get('recoveredValue', 0), 'Cart'])
            
            # Email
            email = metrics.get('email', {})
            writer.writerow(['Email Open Rate', email.get('openRate', 0), 'Email'])
            writer.writerow(['Email Click Rate', email.get('clickRate', 0), 'Email'])
            writer.writerow(['Email Bounce Rate', email.get('bounceRate', 0), 'Email'])
            
            # Conversion
            conversion = metrics.get('conversion', {})
            writer.writerow(['Conversion Rate', conversion.get('conversionRate', 0), 'Conversion'])
            writer.writerow(['Revenue', conversion.get('revenue', 0), 'Conversion'])
            writer.writerow(['Average Order Value', conversion.get('averageOrderValue', 0), 'Conversion'])
        
        return output_file
    
    def generate_html_report(self, summary: Dict, output_file: str = None) -> str:
        """Genera reporte en formato HTML"""
        if not output_file:
            output_file = f"report_{datetime.now().strftime('%Y%m%d')}.html"
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Executive Report - {summary['period']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .metric {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .positive {{ color: green; }}
        .warning {{ color: orange; }}
        .critical {{ color: red; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>Executive Report - {summary['period']}</h1>
    <p><strong>Generated:</strong> {summary['generatedAt']}</p>
    
    <h2>Key Metrics</h2>
    <table>
        <tr>
            <th>Metric</th>
            <th>Value</th>
        </tr>
        <tr>
            <td>Cart Abandonment Rate</td>
            <td>{summary['keyMetrics']['cartAbandonmentRate']:.2f}%</td>
        </tr>
        <tr>
            <td>Recovery Rate</td>
            <td>{summary['keyMetrics']['recoveryRate']:.2f}%</td>
        </tr>
        <tr>
            <td>Recovered Value</td>
            <td>${summary['keyMetrics']['recoveredValue']:,.2f}</td>
        </tr>
        <tr>
            <td>Email Open Rate</td>
            <td>{summary['keyMetrics']['emailOpenRate']:.2f}%</td>
        </tr>
        <tr>
            <td>Email Click Rate</td>
            <td>{summary['keyMetrics']['emailClickRate']:.2f}%</td>
        </tr>
        <tr>
            <td>Conversion Rate</td>
            <td>{summary['keyMetrics']['conversionRate']:.2f}%</td>
        </tr>
        <tr>
            <td>Revenue</td>
            <td>${summary['keyMetrics']['revenue']:,.2f}</td>
        </tr>
        <tr>
            <td>Average Order Value</td>
            <td>${summary['keyMetrics']['averageOrderValue']:.2f}</td>
        </tr>
    </table>
    
    <h2>Insights</h2>
    <ul>
        {''.join([f"<li class='{insight['type']}'>{insight['message']}</li>" for insight in summary['insights']])}
    </ul>
    
    <h2>Recommendations</h2>
    <ul>
        {''.join([f"<li><strong>[{rec['priority'].upper()}]</strong> {rec['action']}: {rec['reason']}</li>" for rec in summary['recommendations']])}
    </ul>
</body>
</html>
"""
        
        with open(output_file, 'w') as f:
            f.write(html)
        
        return output_file
    
    def generate_complete_report(self, period: str = '30d', formats: List[str] = ['json', 'csv', 'html']) -> Dict:
        """Genera reporte completo en múltiples formatos"""
        print(f"Generating report for period: {period}")
        
        # Fetch metrics
        metrics = self.fetch_all_metrics(period)
        
        # Generate summary
        summary = self.generate_executive_summary(metrics)
        
        # Generate files
        files = {}
        
        if 'json' in formats:
            json_file = f"report_{datetime.now().strftime('%Y%m%d')}.json"
            with open(json_file, 'w') as f:
                json.dump(summary, f, indent=2)
            files['json'] = json_file
        
        if 'csv' in formats:
            files['csv'] = self.generate_csv_report(metrics)
        
        if 'html' in formats:
            files['html'] = self.generate_html_report(summary)
        
        return {
            'summary': summary,
            'files': files,
            'generatedAt': datetime.now().isoformat()
        }


def main():
    """Ejemplo de uso"""
    api_url = os.getenv("API_BASE_URL", "https://api.yourdomain.com")
    api_key = os.getenv("API_KEY", "your_api_key_here")
    
    generator = ReportGenerator(api_url, api_key)
    
    # Generar reporte completo
    result = generator.generate_complete_report('30d', ['json', 'csv', 'html'])
    
    print("=" * 50)
    print("REPORT GENERATED")
    print("=" * 50)
    print(f"\nPeriod: {result['summary']['period']}")
    print(f"\nKey Metrics:")
    for key, value in result['summary']['keyMetrics'].items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    print(f"\nFiles Generated:")
    for format_type, file_path in result['files'].items():
        print(f"  {format_type.upper()}: {file_path}")
    
    print(f"\nInsights: {len(result['summary']['insights'])}")
    print(f"Recommendations: {len(result['summary']['recommendations'])}")


if __name__ == "__main__":
    main()










