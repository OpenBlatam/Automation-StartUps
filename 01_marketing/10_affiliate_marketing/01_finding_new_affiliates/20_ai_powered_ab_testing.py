#!/usr/bin/env python3
"""
AI-Powered A/B Testing System for Affiliate Marketing
====================================================

This module provides intelligent A/B testing capabilities for affiliate marketing,
including automated test design, statistical analysis, and optimization.

Author: AI Marketing System
Version: 2.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime, timedelta
import asyncio
import aiohttp
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from scipy import stats
from scipy.stats import chi2_contingency, ttest_ind, mannwhitneyu
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestStatus(Enum):
    """A/B test status"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TestType(Enum):
    """A/B test types"""
    CONVERSION = "conversion"
    CLICK_THROUGH = "click_through"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    EMAIL_OPEN = "email_open"
    LANDING_PAGE = "landing_page"

@dataclass
class TestVariant:
    """A/B test variant"""
    variant_id: str
    name: str
    description: str
    content: Dict
    traffic_percentage: float
    is_control: bool = False

@dataclass
class TestResult:
    """A/B test result"""
    test_id: str
    variant_id: str
    metric_value: float
    sample_size: int
    confidence_interval: Tuple[float, float]
    p_value: float
    is_significant: bool
    effect_size: float

@dataclass
class ABTest:
    """A/B test data structure"""
    test_id: str
    name: str
    description: str
    test_type: TestType
    variants: List[TestVariant]
    status: TestStatus
    start_date: datetime
    end_date: Optional[datetime]
    target_audience: str
    success_metric: str
    minimum_detectable_effect: float
    significance_level: float
    power: float
    created_at: datetime

class AIPoweredABTesting:
    """
    AI-Powered A/B Testing System for Affiliate Marketing
    """
    
    def __init__(self):
        self.tests = []
        self.test_results = []
        self.optimization_rules = []
        self.statistical_models = {}
        
        # Initialize testing parameters
        self.default_params = {
            'significance_level': 0.05,
            'power': 0.8,
            'minimum_detectable_effect': 0.1,
            'max_test_duration': 30,  # days
            'min_sample_size': 1000
        }
    
    def create_test(self, name: str, description: str, test_type: TestType, 
                   variants: List[TestVariant], target_audience: str, 
                   success_metric: str, **kwargs) -> ABTest:
        """
        Create new A/B test
        """
        # Generate test ID
        test_id = f"test_{len(self.tests)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Set default parameters
        params = {**self.default_params, **kwargs}
        
        # Create test
        test = ABTest(
            test_id=test_id,
            name=name,
            description=description,
            test_type=test_type,
            variants=variants,
            status=TestStatus.DRAFT,
            start_date=datetime.now(),
            end_date=None,
            target_audience=target_audience,
            success_metric=success_metric,
            minimum_detectable_effect=params['minimum_detectable_effect'],
            significance_level=params['significance_level'],
            power=params['power'],
            created_at=datetime.now()
        )
        
        self.tests.append(test)
        logger.info(f"Created A/B test: {name} ({test_id})")
        
        return test
    
    def start_test(self, test_id: str) -> bool:
        """
        Start A/B test
        """
        test = self._get_test(test_id)
        if not test:
            logger.error(f"Test {test_id} not found")
            return False
        
        if test.status != TestStatus.DRAFT:
            logger.error(f"Test {test_id} is not in draft status")
            return False
        
        # Validate test
        if not self._validate_test(test):
            logger.error(f"Test {test_id} validation failed")
            return False
        
        # Start test
        test.status = TestStatus.RUNNING
        test.start_date = datetime.now()
        
        logger.info(f"Started A/B test: {test.name}")
        return True
    
    def _validate_test(self, test: ABTest) -> bool:
        """
        Validate A/B test before starting
        """
        # Check if test has at least 2 variants
        if len(test.variants) < 2:
            logger.error("Test must have at least 2 variants")
            return False
        
        # Check if traffic percentages sum to 100%
        total_traffic = sum(v.traffic_percentage for v in test.variants)
        if abs(total_traffic - 100.0) > 0.01:
            logger.error("Traffic percentages must sum to 100%")
            return False
        
        # Check if there's exactly one control variant
        control_variants = [v for v in test.variants if v.is_control]
        if len(control_variants) != 1:
            logger.error("Test must have exactly one control variant")
            return False
        
        return True
    
    def _get_test(self, test_id: str) -> Optional[ABTest]:
        """
        Get test by ID
        """
        for test in self.tests:
            if test.test_id == test_id:
                return test
        return None
    
    def add_test_result(self, test_id: str, variant_id: str, 
                       metric_value: float, sample_size: int) -> TestResult:
        """
        Add test result data
        """
        test = self._get_test(test_id)
        if not test:
            logger.error(f"Test {test_id} not found")
            return None
        
        # Calculate statistical metrics
        confidence_interval = self._calculate_confidence_interval(
            metric_value, sample_size, test.significance_level
        )
        
        p_value = self._calculate_p_value(test, variant_id, metric_value, sample_size)
        
        is_significant = p_value < test.significance_level
        
        effect_size = self._calculate_effect_size(test, variant_id, metric_value)
        
        # Create test result
        result = TestResult(
            test_id=test_id,
            variant_id=variant_id,
            metric_value=metric_value,
            sample_size=sample_size,
            confidence_interval=confidence_interval,
            p_value=p_value,
            is_significant=is_significant,
            effect_size=effect_size
        )
        
        self.test_results.append(result)
        logger.info(f"Added result for test {test_id}, variant {variant_id}")
        
        return result
    
    def _calculate_confidence_interval(self, metric_value: float, sample_size: int, 
                                     significance_level: float) -> Tuple[float, float]:
        """
        Calculate confidence interval
        """
        # Standard error
        se = np.sqrt(metric_value * (1 - metric_value) / sample_size)
        
        # Z-score for significance level
        z_score = stats.norm.ppf(1 - significance_level / 2)
        
        # Margin of error
        margin_error = z_score * se
        
        return (metric_value - margin_error, metric_value + margin_error)
    
    def _calculate_p_value(self, test: ABTest, variant_id: str, 
                          metric_value: float, sample_size: int) -> float:
        """
        Calculate p-value for test
        """
        # Get control variant
        control_variant = next((v for v in test.variants if v.is_control), None)
        if not control_variant:
            return 1.0
        
        # Get control results
        control_results = [r for r in self.test_results 
                          if r.test_id == test.test_id and r.variant_id == control_variant.variant_id]
        
        if not control_results:
            return 1.0
        
        control_metric = np.mean([r.metric_value for r in control_results])
        control_sample_size = sum([r.sample_size for r in control_results])
        
        # Perform statistical test
        if test.test_type == TestType.CONVERSION:
            # Chi-square test for conversion rates
            return self._chi_square_test(control_metric, control_sample_size, 
                                       metric_value, sample_size)
        else:
            # T-test for continuous metrics
            return self._t_test(control_metric, control_sample_size, 
                              metric_value, sample_size)
    
    def _chi_square_test(self, control_metric: float, control_sample_size: int,
                        variant_metric: float, variant_sample_size: int) -> float:
        """
        Perform chi-square test
        """
        # Create contingency table
        control_conversions = int(control_metric * control_sample_size)
        control_non_conversions = control_sample_size - control_conversions
        
        variant_conversions = int(variant_metric * variant_sample_size)
        variant_non_conversions = variant_sample_size - variant_conversions
        
        contingency_table = np.array([
            [control_conversions, control_non_conversions],
            [variant_conversions, variant_non_conversions]
        ])
        
        # Perform chi-square test
        chi2, p_value, dof, expected = chi2_contingency(contingency_table)
        
        return p_value
    
    def _t_test(self, control_metric: float, control_sample_size: int,
                variant_metric: float, variant_sample_size: int) -> float:
        """
        Perform t-test
        """
        # Generate sample data (simplified)
        control_data = np.random.normal(control_metric, 0.1, control_sample_size)
        variant_data = np.random.normal(variant_metric, 0.1, variant_sample_size)
        
        # Perform t-test
        t_stat, p_value = ttest_ind(control_data, variant_data)
        
        return p_value
    
    def _calculate_effect_size(self, test: ABTest, variant_id: str, 
                              metric_value: float) -> float:
        """
        Calculate effect size (Cohen's d)
        """
        # Get control variant
        control_variant = next((v for v in test.variants if v.is_control), None)
        if not control_variant:
            return 0.0
        
        # Get control results
        control_results = [r for r in self.test_results 
                          if r.test_id == test.test_id and r.variant_id == control_variant.variant_id]
        
        if not control_results:
            return 0.0
        
        control_metric = np.mean([r.metric_value for r in control_results])
        control_std = np.std([r.metric_value for r in control_results])
        
        # Calculate Cohen's d
        if control_std > 0:
            effect_size = (metric_value - control_metric) / control_std
        else:
            effect_size = 0.0
        
        return effect_size
    
    def analyze_test_results(self, test_id: str) -> Dict:
        """
        Analyze A/B test results
        """
        test = self._get_test(test_id)
        if not test:
            return {}
        
        # Get results for this test
        results = [r for r in self.test_results if r.test_id == test_id]
        
        if not results:
            return {}
        
        # Group results by variant
        variant_results = {}
        for result in results:
            if result.variant_id not in variant_results:
                variant_results[result.variant_id] = []
            variant_results[result.variant_id].append(result)
        
        # Calculate statistics for each variant
        variant_stats = {}
        for variant_id, variant_result_list in variant_results.items():
            metrics = [r.metric_value for r in variant_result_list]
            sample_sizes = [r.sample_size for r in variant_result_list]
            
            variant_stats[variant_id] = {
                'mean_metric': np.mean(metrics),
                'std_metric': np.std(metrics),
                'total_sample_size': sum(sample_sizes),
                'confidence_interval': self._calculate_confidence_interval(
                    np.mean(metrics), sum(sample_sizes), test.significance_level
                ),
                'p_value': np.mean([r.p_value for r in variant_result_list]),
                'is_significant': any(r.is_significant for r in variant_result_list),
                'effect_size': np.mean([r.effect_size for r in variant_result_list])
            }
        
        # Find winning variant
        winning_variant = self._find_winning_variant(test, variant_stats)
        
        # Calculate test power
        test_power = self._calculate_test_power(test, variant_stats)
        
        # Generate recommendations
        recommendations = self._generate_test_recommendations(test, variant_stats, winning_variant)
        
        return {
            'test_id': test_id,
            'test_name': test.name,
            'test_type': test.test_type.value,
            'status': test.status.value,
            'variant_stats': variant_stats,
            'winning_variant': winning_variant,
            'test_power': test_power,
            'recommendations': recommendations,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _find_winning_variant(self, test: ABTest, variant_stats: Dict) -> Optional[str]:
        """
        Find winning variant
        """
        # Get control variant
        control_variant = next((v for v in test.variants if v.is_control), None)
        if not control_variant:
            return None
        
        control_stats = variant_stats.get(control_variant.variant_id)
        if not control_stats:
            return None
        
        # Find variant with highest metric that's statistically significant
        winning_variant = None
        best_metric = control_stats['mean_metric']
        
        for variant_id, stats in variant_stats.items():
            if variant_id == control_variant.variant_id:
                continue
            
            if (stats['is_significant'] and 
                stats['mean_metric'] > best_metric):
                best_metric = stats['mean_metric']
                winning_variant = variant_id
        
        return winning_variant
    
    def _calculate_test_power(self, test: ABTest, variant_stats: Dict) -> float:
        """
        Calculate test power
        """
        # Simplified power calculation
        # In practice, use more sophisticated methods
        
        # Get control variant
        control_variant = next((v for v in test.variants if v.is_control), None)
        if not control_variant:
            return 0.0
        
        control_stats = variant_stats.get(control_variant.variant_id)
        if not control_stats:
            return 0.0
        
        # Calculate power based on effect size and sample size
        total_sample_size = sum(stats['total_sample_size'] for stats in variant_stats.values())
        
        # Simplified power calculation
        power = min(1.0, total_sample_size / 10000)  # Assume 10k samples = 100% power
        
        return power
    
    def _generate_test_recommendations(self, test: ABTest, variant_stats: Dict, 
                                     winning_variant: Optional[str]) -> List[str]:
        """
        Generate test recommendations
        """
        recommendations = []
        
        # Check test power
        test_power = self._calculate_test_power(test, variant_stats)
        if test_power < 0.8:
            recommendations.append("Test power is below 80%. Consider increasing sample size or test duration.")
        
        # Check for significant results
        significant_variants = [vid for vid, stats in variant_stats.items() if stats['is_significant']]
        if not significant_variants:
            recommendations.append("No significant differences found. Consider running test longer or increasing sample size.")
        
        # Check for winning variant
        if winning_variant:
            recommendations.append(f"Variant {winning_variant} is the winner. Consider implementing it.")
        else:
            recommendations.append("No clear winner found. Consider running test longer or testing different variants.")
        
        # Check effect size
        for variant_id, stats in variant_stats.items():
            if stats['effect_size'] > 0.5:
                recommendations.append(f"Variant {variant_id} has a large effect size. Consider implementing it.")
        
        return recommendations
    
    def stop_test(self, test_id: str, reason: str = "Manual stop") -> bool:
        """
        Stop A/B test
        """
        test = self._get_test(test_id)
        if not test:
            logger.error(f"Test {test_id} not found")
            return False
        
        if test.status != TestStatus.RUNNING:
            logger.error(f"Test {test_id} is not running")
            return False
        
        # Stop test
        test.status = TestStatus.COMPLETED
        test.end_date = datetime.now()
        
        logger.info(f"Stopped A/B test: {test.name} - {reason}")
        return True
    
    def get_test_summary(self, test_id: str) -> Dict:
        """
        Get test summary
        """
        test = self._get_test(test_id)
        if not test:
            return {}
        
        # Get results
        results = [r for r in self.test_results if r.test_id == test_id]
        
        # Calculate summary statistics
        total_results = len(results)
        total_sample_size = sum(r.sample_size for r in results)
        
        # Get analysis
        analysis = self.analyze_test_results(test_id)
        
        return {
            'test_id': test_id,
            'test_name': test.name,
            'test_type': test.test_type.value,
            'status': test.status.value,
            'start_date': test.start_date.isoformat(),
            'end_date': test.end_date.isoformat() if test.end_date else None,
            'duration_days': (test.end_date - test.start_date).days if test.end_date else None,
            'total_results': total_results,
            'total_sample_size': total_sample_size,
            'analysis': analysis
        }
    
    def get_all_tests_summary(self) -> List[Dict]:
        """
        Get summary of all tests
        """
        summaries = []
        
        for test in self.tests:
            summary = self.get_test_summary(test.test_id)
            summaries.append(summary)
        
        return summaries
    
    def export_test_data(self, test_id: str, format: str = 'json') -> str:
        """
        Export test data
        """
        test = self._get_test(test_id)
        if not test:
            return ""
        
        # Get test data
        test_data = {
            'test': asdict(test),
            'results': [asdict(r) for r in self.test_results if r.test_id == test_id],
            'analysis': self.analyze_test_results(test_id)
        }
        
        if format == 'json':
            return json.dumps(test_data, indent=2, default=str)
        elif format == 'csv':
            # Export results as CSV
            if test_data['results']:
                df = pd.DataFrame(test_data['results'])
                return df.to_csv(index=False)
            else:
                return ""
        else:
            raise ValueError(f"Unsupported format: {format}")

# Example usage
def main():
    """
    Example usage of AI-Powered A/B Testing
    """
    # Initialize A/B testing system
    ab_testing = AIPoweredABTesting()
    
    # Create test variants
    variants = [
        TestVariant('variant_a', 'Control', 'Original email subject', 
                   {'subject': 'Original Subject'}, 50.0, is_control=True),
        TestVariant('variant_b', 'Test A', 'New email subject with emoji', 
                   {'subject': '🚀 New Subject with Emoji'}, 50.0),
        TestVariant('variant_c', 'Test B', 'New email subject with urgency', 
                   {'subject': 'Limited Time: New Subject'}, 0.0)  # Will be updated
    ]
    
    # Create A/B test
    test = ab_testing.create_test(
        name="Email Subject Line Test",
        description="Testing different email subject lines for affiliate emails",
        test_type=TestType.EMAIL_OPEN,
        variants=variants,
        target_audience="Affiliate Partners",
        success_metric="open_rate",
        minimum_detectable_effect=0.05
    )
    
    # Start test
    ab_testing.start_test(test.test_id)
    
    # Add test results (simulated)
    ab_testing.add_test_result(test.test_id, 'variant_a', 0.25, 1000)
    ab_testing.add_test_result(test.test_id, 'variant_b', 0.28, 1000)
    ab_testing.add_test_result(test.test_id, 'variant_c', 0.30, 1000)
    
    # Analyze results
    analysis = ab_testing.analyze_test_results(test.test_id)
    print(f"Test analysis: {analysis}")
    
    # Get test summary
    summary = ab_testing.get_test_summary(test.test_id)
    print(f"Test summary: {summary}")
    
    # Stop test
    ab_testing.stop_test(test.test_id, "Analysis complete")
    
    # Export data
    json_data = ab_testing.export_test_data(test.test_id, 'json')
    print(f"Exported test data: {len(json_data)} characters")

if __name__ == "__main__":
    main()


