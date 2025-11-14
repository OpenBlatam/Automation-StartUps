#!/usr/bin/env python3
"""
Generador de Reportes y Analytics para Publicaciones de Testimonios
Incluye comparación con benchmarks, análisis competitivo y exportación
"""

import json
import csv
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkComparison:
    """Comparación con benchmarks de la industria"""
    industry_average: float
    top_percentile: float
    your_score: float
    percentile: float
    performance_level: str  # "excellent", "good", "average", "below_average"
    improvement_potential: float


@dataclass
class CompetitiveAnalysis:
    """Análisis competitivo"""
    competitor_scores: Dict[str, float]
    your_position: int
    market_share_estimate: float
    differentiation_factors: List[str]
    competitive_advantages: List[str]


class AnalyticsReporter:
    """Generador de reportes y analytics avanzados"""
    
    # Benchmarks de engagement por industria y plataforma
    INDUSTRY_BENCHMARKS = {
        'testimonials': {
            'instagram': {'average': 3.5, 'top_10': 8.0, 'top_1': 15.0},
            'linkedin': {'average': 2.8, 'top_10': 6.5, 'top_1': 12.0},
            'facebook': {'average': 2.5, 'top_10': 6.0, 'top_1': 10.0},
            'twitter': {'average': 1.5, 'top_10': 4.0, 'top_1': 8.0},
            'tiktok': {'average': 5.0, 'top_10': 12.0, 'top_1': 25.0}
        },
        'customer_success': {
            'instagram': {'average': 4.0, 'top_10': 9.0, 'top_1': 18.0},
            'linkedin': {'average': 3.5, 'top_10': 8.0, 'top_1': 15.0},
            'facebook': {'average': 3.0, 'top_10': 7.0, 'top_1': 12.0},
            'twitter': {'average': 2.0, 'top_10': 5.0, 'top_1': 10.0},
            'tiktok': {'average': 6.0, 'top_10': 15.0, 'top_1': 30.0}
        }
    }
    
    def __init__(self, industry: str = 'testimonials'):
        """
        Inicializa el generador de reportes
        
        Args:
            industry: Industria para benchmarks ('testimonials' o 'customer_success')
        """
        self.industry = industry
        self.benchmarks = self.INDUSTRY_BENCHMARKS.get(industry, self.INDUSTRY_BENCHMARKS['testimonials'])
    
    def compare_with_benchmark(
        self,
        engagement_rate: float,
        platform: str
    ) -> BenchmarkComparison:
        """
        Compara el engagement rate con benchmarks de la industria
        
        Args:
            engagement_rate: Engagement rate de la publicación
            platform: Plataforma objetivo
        
        Returns:
            BenchmarkComparison con análisis comparativo
        """
        platform_benchmarks = self.benchmarks.get(platform.lower(), self.benchmarks.get('instagram', {}))
        industry_avg = platform_benchmarks.get('average', 3.0)
        top_percentile = platform_benchmarks.get('top_10', 8.0)
        
        # Calcular percentil
        if engagement_rate >= top_percentile:
            percentile = 90 + min(10, ((engagement_rate - top_percentile) / (top_percentile * 0.5)) * 10)
        elif engagement_rate >= industry_avg:
            percentile = 50 + ((engagement_rate - industry_avg) / (top_percentile - industry_avg)) * 40
        else:
            percentile = (engagement_rate / industry_avg) * 50
        
        percentile = min(99, max(1, percentile))
        
        # Determinar nivel de rendimiento
        if engagement_rate >= top_percentile:
            performance_level = "excellent"
        elif engagement_rate >= industry_avg * 1.2:
            performance_level = "good"
        elif engagement_rate >= industry_avg * 0.8:
            performance_level = "average"
        else:
            performance_level = "below_average"
        
        # Potencial de mejora
        improvement_potential = max(0, top_percentile - engagement_rate)
        
        return BenchmarkComparison(
            industry_average=industry_avg,
            top_percentile=top_percentile,
            your_score=engagement_rate,
            percentile=round(percentile, 1),
            performance_level=performance_level,
            improvement_potential=round(improvement_potential, 2)
        )
    
    def generate_competitive_analysis(
        self,
        your_engagement_rate: float,
        platform: str,
        competitor_data: Optional[List[Dict[str, float]]] = None
    ) -> CompetitiveAnalysis:
        """
        Genera análisis competitivo
        
        Args:
            your_engagement_rate: Tu engagement rate
            platform: Plataforma objetivo
            competitor_data: Datos de competidores (opcional)
        
        Returns:
            CompetitiveAnalysis con análisis competitivo
        """
        # Si no hay datos de competidores, usar benchmarks como referencia
        if not competitor_data:
            platform_benchmarks = self.benchmarks.get(platform.lower(), {})
            competitor_data = [
                {'name': 'Top 1%', 'rate': platform_benchmarks.get('top_1', 15.0)},
                {'name': 'Top 10%', 'rate': platform_benchmarks.get('top_10', 8.0)},
                {'name': 'Promedio Industria', 'rate': platform_benchmarks.get('average', 3.0)}
            ]
        
        competitor_scores = {comp['name']: comp['rate'] for comp in competitor_data}
        
        # Ordenar competidores por engagement rate
        sorted_competitors = sorted(competitor_data, key=lambda x: x['rate'], reverse=True)
        
        # Determinar posición
        your_position = 1
        for i, comp in enumerate(sorted_competitors):
            if your_engagement_rate < comp['rate']:
                your_position = i + 1
                break
            your_position = i + 1
        
        # Estimar market share (simplificado)
        total_engagement = sum(comp['rate'] for comp in competitor_data) + your_engagement_rate
        market_share_estimate = (your_engagement_rate / total_engagement) * 100 if total_engagement > 0 else 0
        
        # Factores de diferenciación
        differentiation_factors = []
        if your_engagement_rate > platform_benchmarks.get('average', 3.0) * 1.5:
            differentiation_factors.append("Engagement significativamente superior al promedio")
        if your_engagement_rate >= platform_benchmarks.get('top_10', 8.0):
            differentiation_factors.append("En el top 10% de la industria")
        
        # Ventajas competitivas
        competitive_advantages = []
        avg_competitor = sum(comp['rate'] for comp in competitor_data) / len(competitor_data) if competitor_data else 0
        if your_engagement_rate > avg_competitor:
            advantage_pct = ((your_engagement_rate - avg_competitor) / avg_competitor) * 100
            competitive_advantages.append(f"Engagement {advantage_pct:.1f}% superior al promedio de competidores")
        
        return CompetitiveAnalysis(
            competitor_scores=competitor_scores,
            your_position=your_position,
            market_share_estimate=round(market_share_estimate, 2),
            differentiation_factors=differentiation_factors,
            competitive_advantages=competitive_advantages
        )
    
    def generate_comprehensive_report(
        self,
        post_data: Dict[str, Any],
        platform: str,
        include_benchmarks: bool = True,
        include_competitive: bool = True
    ) -> Dict[str, Any]:
        """
        Genera un reporte completo de analytics
        
        Args:
            post_data: Datos de la publicación generada
            platform: Plataforma objetivo
            include_benchmarks: Incluir comparación con benchmarks
            include_competitive: Incluir análisis competitivo
        
        Returns:
            Dict con reporte completo
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'platform': platform,
            'post_summary': {
                'length': post_data.get('length', 0),
                'hashtags_count': len(post_data.get('hashtags', [])),
                'has_cta': bool(post_data.get('call_to_action')),
                'has_sentiment_analysis': 'sentiment_analysis' in post_data,
                'has_keyword_analysis': 'keyword_analysis' in post_data
            }
        }
        
        # Agregar predicción de engagement si está disponible
        if 'engagement_prediction' in post_data:
            pred = post_data['engagement_prediction']
            report['engagement_prediction'] = pred
            
            # Comparación con benchmarks
            if include_benchmarks:
                benchmark = self.compare_with_benchmark(
                    pred['predicted_engagement_rate'],
                    platform
                )
                report['benchmark_comparison'] = asdict(benchmark)
            
            # Análisis competitivo
            if include_competitive:
                competitive = self.generate_competitive_analysis(
                    pred['predicted_engagement_rate'],
                    platform
                )
                report['competitive_analysis'] = asdict(competitive)
        
        # Agregar optimizaciones si están disponibles
        if 'engagement_optimization' in post_data:
            report['optimizations'] = post_data['engagement_optimization']
        
        # Agregar análisis de sentimiento si está disponible
        if 'sentiment_analysis' in post_data:
            report['sentiment_analysis'] = post_data['sentiment_analysis']
        
        # Agregar análisis de keywords si está disponible
        if 'keyword_analysis' in post_data:
            report['keyword_analysis'] = post_data['keyword_analysis']
        
        # Calcular score general
        report['overall_score'] = self._calculate_overall_score(post_data)
        
        return report
    
    def _calculate_overall_score(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula un score general de calidad"""
        score = 0
        max_score = 0
        factors = []
        
        # Score de engagement prediction (40 puntos)
        if 'engagement_prediction' in post_data:
            pred_score = post_data['engagement_prediction']['predicted_score']
            score += pred_score * 0.4
            max_score += 40
            factors.append(f"Predicción engagement: {pred_score:.1f}/100")
        
        # Score de optimización (20 puntos)
        if 'engagement_optimization' in post_data:
            opt = post_data['engagement_optimization']
            opt_score = 20
            if opt.get('length_optimization'):
                opt_score -= 5
            if not opt.get('hashtag_suggestions'):
                opt_score -= 5
            score += max(0, opt_score)
            max_score += 20
            factors.append(f"Optimización: {opt_score}/20")
        
        # Score de análisis (20 puntos)
        analysis_score = 0
        if 'sentiment_analysis' in post_data:
            analysis_score += 10
        if 'keyword_analysis' in post_data:
            analysis_score += 10
        score += analysis_score
        max_score += 20
        if analysis_score > 0:
            factors.append(f"Análisis completo: {analysis_score}/20")
        
        # Score de contenido (20 puntos)
        content_score = 20
        if post_data.get('length', 0) < 50:
            content_score -= 10
        if not post_data.get('hashtags'):
            content_score -= 5
        if not post_data.get('call_to_action'):
            content_score -= 5
        score += max(0, content_score)
        max_score += 20
        factors.append(f"Calidad contenido: {content_score}/20")
        
        overall_percentage = (score / max_score * 100) if max_score > 0 else 0
        
        return {
            'score': round(score, 1),
            'max_score': max_score,
            'percentage': round(overall_percentage, 1),
            'grade': self._get_grade(overall_percentage),
            'factors': factors
        }
    
    def _get_grade(self, percentage: float) -> str:
        """Convierte porcentaje a calificación"""
        if percentage >= 90:
            return "A+"
        elif percentage >= 80:
            return "A"
        elif percentage >= 70:
            return "B"
        elif percentage >= 60:
            return "C"
        else:
            return "D"
    
    def export_report_json(
        self,
        report: Dict[str, Any],
        output_file: str
    ):
        """Exporta reporte a JSON"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Reporte exportado a JSON: {output_file}")
    
    def export_report_csv(
        self,
        report: Dict[str, Any],
        output_file: str
    ):
        """Exporta reporte resumido a CSV"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        rows = []
        
        # Datos básicos
        rows.append({
            'Métrica': 'Plataforma',
            'Valor': report.get('platform', 'N/A')
        })
        
        # Engagement prediction
        if 'engagement_prediction' in report:
            pred = report['engagement_prediction']
            rows.append({
                'Métrica': 'Score Predicho',
                'Valor': pred.get('predicted_score', 0)
            })
            rows.append({
                'Métrica': 'Engagement Rate Estimado (%)',
                'Valor': pred.get('predicted_engagement_rate', 0)
            })
            rows.append({
                'Métrica': 'Confianza',
                'Valor': pred.get('confidence', 0)
            })
        
        # Benchmark comparison
        if 'benchmark_comparison' in report:
            bench = report['benchmark_comparison']
            rows.append({
                'Métrica': 'Percentil Industria',
                'Valor': bench.get('percentile', 0)
            })
            rows.append({
                'Métrica': 'Nivel Rendimiento',
                'Valor': bench.get('performance_level', 'N/A')
            })
        
        # Overall score
        if 'overall_score' in report:
            score = report['overall_score']
            rows.append({
                'Métrica': 'Score General',
                'Valor': score.get('score', 0)
            })
            rows.append({
                'Métrica': 'Calificación',
                'Valor': score.get('grade', 'N/A')
            })
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Métrica', 'Valor'])
            writer.writeheader()
            writer.writerows(rows)
        
        logger.info(f"Reporte exportado a CSV: {output_file}")
    
    def generate_summary_text(self, report: Dict[str, Any]) -> str:
        """Genera un resumen en texto del reporte"""
        lines = []
        lines.append("=" * 60)
        lines.append("REPORTE DE ANALYTICS - PUBLICACIÓN DE TESTIMONIO")
        lines.append("=" * 60)
        lines.append(f"\nPlataforma: {report.get('platform', 'N/A').upper()}")
        lines.append(f"Generado: {report.get('generated_at', 'N/A')}")
        
        # Engagement prediction
        if 'engagement_prediction' in report:
            pred = report['engagement_prediction']
            lines.append(f"\n--- PREDICCIÓN DE ENGAGEMENT ---")
            lines.append(f"Score Predicho: {pred.get('predicted_score', 0)}/100")
            lines.append(f"Engagement Rate Estimado: {pred.get('predicted_engagement_rate', 0)}%")
            lines.append(f"Confianza: {pred.get('confidence', 0)}")
            lines.append(f"Horario Óptimo: {pred.get('optimal_posting_time', 'N/A')}")
            
            if pred.get('recommendations'):
                lines.append("\nRecomendaciones:")
                for rec in pred['recommendations'][:5]:
                    lines.append(f"  • {rec}")
        
        # Benchmark comparison
        if 'benchmark_comparison' in report:
            bench = report['benchmark_comparison']
            lines.append(f"\n--- COMPARACIÓN CON BENCHMARKS ---")
            lines.append(f"Promedio Industria: {bench.get('industry_average', 0)}%")
            lines.append(f"Top 10%: {bench.get('top_percentile', 0)}%")
            lines.append(f"Tu Score: {bench.get('your_score', 0)}%")
            lines.append(f"Percentil: {bench.get('percentile', 0)}")
            lines.append(f"Nivel: {bench.get('performance_level', 'N/A').upper()}")
            lines.append(f"Potencial de Mejora: +{bench.get('improvement_potential', 0)}%")
        
        # Competitive analysis
        if 'competitive_analysis' in report:
            comp = report['competitive_analysis']
            lines.append(f"\n--- ANÁLISIS COMPETITIVO ---")
            lines.append(f"Posición Estimada: #{comp.get('your_position', 0)}")
            lines.append(f"Market Share Estimado: {comp.get('market_share_estimate', 0)}%")
            
            if comp.get('competitive_advantages'):
                lines.append("\nVentajas Competitivas:")
                for adv in comp['competitive_advantages']:
                    lines.append(f"  • {adv}")
        
        # Overall score
        if 'overall_score' in report:
            score = report['overall_score']
            lines.append(f"\n--- SCORE GENERAL ---")
            lines.append(f"Score: {score.get('score', 0)}/{score.get('max_score', 100)}")
            lines.append(f"Porcentaje: {score.get('percentage', 0)}%")
            lines.append(f"Calificación: {score.get('grade', 'N/A')}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)



