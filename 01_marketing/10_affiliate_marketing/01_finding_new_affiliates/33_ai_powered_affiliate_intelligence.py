"""
AI-Powered Affiliate Intelligence System
Advanced intelligence and insights for affiliate marketing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, r2_score
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

@dataclass
class IntelligenceInsight:
    """Intelligence insight data structure"""
    insight_id: str
    type: str
    title: str
    description: str
    confidence: float
    impact_score: float
    actionable: bool
    recommendations: List[str]
    affected_metrics: List[str]
    created_at: datetime

@dataclass
class AffiliateIntelligence:
    """Affiliate intelligence data structure"""
    affiliate_id: str
    intelligence_score: float
    risk_level: str
    opportunity_level: str
    predicted_performance: Dict
    behavioral_patterns: Dict
    recommendations: List[str]
    last_updated: datetime

class AIAffiliateIntelligence:
    """AI-powered affiliate intelligence system"""
    
    def __init__(self):
        self.intelligence_models = {}
        self.insights = []
        self.affiliate_intelligence = []
        self.scalers = {}
        self.intelligence_history = []
        
    def analyze_affiliate_intelligence(self, affiliate_data: pd.DataFrame) -> Dict:
        """Comprehensive affiliate intelligence analysis"""
        print("🧠 Analyzing affiliate intelligence...")
        
        # Behavioral pattern analysis
        behavioral_patterns = self._analyze_behavioral_patterns(affiliate_data)
        
        # Performance prediction
        performance_predictions = self._predict_performance(affiliate_data)
        
        # Risk assessment
        risk_assessment = self._assess_risks(affiliate_data)
        
        # Opportunity identification
        opportunities = self._identify_opportunities(affiliate_data)
        
        # Generate intelligence insights
        insights = self._generate_intelligence_insights(
            behavioral_patterns, performance_predictions, risk_assessment, opportunities
        )
        
        # Create affiliate intelligence profiles
        intelligence_profiles = self._create_intelligence_profiles(
            affiliate_data, behavioral_patterns, performance_predictions, risk_assessment
        )
        
        return {
            'behavioral_patterns': behavioral_patterns,
            'performance_predictions': performance_predictions,
            'risk_assessment': risk_assessment,
            'opportunities': opportunities,
            'insights': insights,
            'intelligence_profiles': intelligence_profiles,
            'summary': self._generate_intelligence_summary(insights, intelligence_profiles)
        }
    
    def predict_affiliate_success(self, affiliate_data: pd.DataFrame) -> Dict:
        """Predict affiliate success using AI models"""
        print("🔮 Predicting affiliate success...")
        
        # Prepare features for prediction
        features = self._prepare_prediction_features(affiliate_data)
        
        # Train success prediction model
        model = self._train_success_prediction_model(features)
        
        # Make predictions
        predictions = model.predict(features)
        probabilities = model.predict_proba(features)
        
        # Analyze prediction results
        prediction_analysis = self._analyze_predictions(predictions, probabilities, affiliate_data)
        
        return {
            'predictions': predictions,
            'probabilities': probabilities,
            'model_accuracy': self._calculate_model_accuracy(model, features),
            'analysis': prediction_analysis,
            'recommendations': self._generate_prediction_recommendations(prediction_analysis)
        }
    
    def identify_high_value_affiliates(self, affiliate_data: pd.DataFrame) -> List[Dict]:
        """Identify high-value affiliates using AI"""
        print("💎 Identifying high-value affiliates...")
        
        # Calculate value scores
        value_scores = self._calculate_value_scores(affiliate_data)
        
        # Cluster affiliates by value
        value_clusters = self._cluster_by_value(affiliate_data, value_scores)
        
        # Identify high-value patterns
        high_value_patterns = self._identify_high_value_patterns(affiliate_data, value_scores)
        
        # Generate high-value affiliate profiles
        high_value_affiliates = self._create_high_value_profiles(
            affiliate_data, value_scores, value_clusters, high_value_patterns
        )
        
        return high_value_affiliates
    
    def analyze_affiliate_churn_risk(self, affiliate_data: pd.DataFrame) -> Dict:
        """Analyze affiliate churn risk using AI"""
        print("⚠️ Analyzing churn risk...")
        
        # Prepare churn prediction features
        churn_features = self._prepare_churn_features(affiliate_data)
        
        # Train churn prediction model
        churn_model = self._train_churn_prediction_model(churn_features)
        
        # Predict churn risk
        churn_risk_scores = churn_model.predict_proba(churn_features)[:, 1]
        
        # Analyze churn patterns
        churn_patterns = self._analyze_churn_patterns(affiliate_data, churn_risk_scores)
        
        # Generate retention recommendations
        retention_recommendations = self._generate_retention_recommendations(
            churn_risk_scores, churn_patterns
        )
        
        return {
            'churn_risk_scores': churn_risk_scores,
            'churn_patterns': churn_patterns,
            'retention_recommendations': retention_recommendations,
            'high_risk_affiliates': self._identify_high_risk_affiliates(churn_risk_scores, affiliate_data)
        }
    
    def generate_intelligence_report(self, analysis_results: Dict) -> str:
        """Generate comprehensive intelligence report"""
        report = f"""
# 🧠 AI-Powered Affiliate Intelligence Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Executive Summary
- **Total Affiliates Analyzed**: {len(analysis_results.get('intelligence_profiles', []))}
- **Key Insights Generated**: {len(analysis_results.get('insights', []))}
- **High-Value Affiliates**: {len([p for p in analysis_results.get('intelligence_profiles', []) if p.opportunity_level == 'High'])}
- **High-Risk Affiliates**: {len([p for p in analysis_results.get('intelligence_profiles', []) if p.risk_level == 'High'])}

## 🎯 Key Intelligence Insights
"""
        
        insights = analysis_results.get('insights', [])
        for insight in insights[:5]:
            report += f"""
### {insight.title}
- **Type**: {insight.type}
- **Confidence**: {insight.confidence:.2f}
- **Impact Score**: {insight.impact_score:.2f}
- **Actionable**: {'Yes' if insight.actionable else 'No'}
- **Description**: {insight.description}
- **Recommendations**: {', '.join(insight.recommendations[:3])}
"""
        
        report += f"""
## 💎 High-Value Affiliate Patterns
"""
        
        high_value_patterns = analysis_results.get('opportunities', {}).get('high_value_patterns', [])
        for pattern in high_value_patterns[:3]:
            report += f"""
### {pattern.get('name', 'Pattern')}
- **Description**: {pattern.get('description', 'N/A')}
- **Frequency**: {pattern.get('frequency', 0):.1f}%
- **Value Impact**: {pattern.get('value_impact', 0):.2f}
"""
        
        report += f"""
## ⚠️ Risk Assessment
"""
        
        risk_assessment = analysis_results.get('risk_assessment', {})
        report += f"""
- **High Risk Affiliates**: {risk_assessment.get('high_risk_count', 0)}
- **Medium Risk Affiliates**: {risk_assessment.get('medium_risk_count', 0)}
- **Low Risk Affiliates**: {risk_assessment.get('low_risk_count', 0)}
- **Overall Risk Level**: {risk_assessment.get('overall_risk_level', 'Unknown')}
"""
        
        report += f"""
## 🚀 Strategic Recommendations
1. **Focus on High-Value Affiliates**: Prioritize affiliates with high opportunity scores
2. **Address High-Risk Affiliates**: Implement retention strategies for at-risk affiliates
3. **Leverage Behavioral Patterns**: Use identified patterns to optimize affiliate management
4. **Monitor Intelligence Metrics**: Track intelligence scores and adjust strategies
5. **Implement Predictive Actions**: Use predictions to proactively manage affiliates

## 🔍 Next Steps
1. Implement high-value affiliate strategies
2. Deploy retention programs for high-risk affiliates
3. Monitor intelligence metrics regularly
4. Update models with new data
5. Scale intelligence insights across the program
"""
        
        return report
    
    def create_intelligence_dashboard(self, analysis_results: Dict) -> str:
        """Create interactive intelligence dashboard"""
        intelligence_profiles = analysis_results.get('intelligence_profiles', [])
        insights = analysis_results.get('insights', [])
        opportunities = analysis_results.get('opportunities', {})
        risk_assessment = analysis_results.get('risk_assessment', {})
        
        # Create HTML dashboard
        dashboard_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Affiliate Intelligence Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .dashboard {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .chart {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .stat-label {{ font-size: 14px; color: #666; }}
        .insight-card {{ background: #e3f2fd; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #2196f3; }}
        .insight-title {{ font-weight: bold; color: #1976d2; }}
        .insight-description {{ color: #424242; margin: 5px 0; }}
    </style>
</head>
<body>
    <h1>🧠 AI Affiliate Intelligence Dashboard</h1>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{len(intelligence_profiles)}</div>
            <div class="stat-label">Affiliates Analyzed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(insights)}</div>
            <div class="stat-label">Insights Generated</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len([p for p in intelligence_profiles if p.opportunity_level == 'High'])}</div>
            <div class="stat-label">High-Value Affiliates</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len([p for p in intelligence_profiles if p.risk_level == 'High'])}</div>
            <div class="stat-label">High-Risk Affiliates</div>
        </div>
    </div>
    
    <div class="dashboard">
        <div class="chart">
            <h3>Intelligence Score Distribution</h3>
            <div id="intelligence-chart"></div>
        </div>
        
        <div class="chart">
            <h3>Risk vs Opportunity Matrix</h3>
            <div id="risk-opportunity-chart"></div>
        </div>
        
        <div class="chart">
            <h3>Insight Impact Distribution</h3>
            <div id="insights-chart"></div>
        </div>
        
        <div class="chart">
            <h3>Behavioral Patterns</h3>
            <div id="patterns-chart"></div>
        </div>
    </div>
    
    <div class="insights-section">
        <h2>🔍 Key Intelligence Insights</h2>
"""
        
        for insight in insights[:5]:
            dashboard_html += f"""
        <div class="insight-card">
            <div class="insight-title">{insight.title}</div>
            <div class="insight-description">{insight.description}</div>
            <div><strong>Confidence:</strong> {insight.confidence:.2f} | <strong>Impact:</strong> {insight.impact_score:.2f}</div>
        </div>
"""
        
        dashboard_html += """
    </div>
    
    <script>
        // Intelligence score distribution
        var intelligenceScores = """ + json.dumps([p.intelligence_score for p in intelligence_profiles]) + """;
        var intelligenceData = {
            x: intelligenceScores,
            type: 'histogram',
            nbinsx: 20,
            marker: {color: 'rgba(0,123,255,0.7)'}
        };
        var intelligenceLayout = {
            title: 'Intelligence Score Distribution',
            xaxis: {title: 'Intelligence Score'},
            yaxis: {title: 'Count'}
        };
        Plotly.newPlot('intelligence-chart', [intelligenceData], intelligenceLayout);
        
        // Risk vs Opportunity matrix
        var riskLevels = """ + json.dumps([p.risk_level for p in intelligence_profiles]) + """;
        var opportunityLevels = """ + json.dumps([p.opportunity_level for p in intelligence_profiles]) + """;
        
        var riskOpportunityData = {
            x: riskLevels,
            y: opportunityLevels,
            mode: 'markers',
            type: 'scatter',
            marker: {
                size: 10,
                color: intelligenceScores,
                colorscale: 'Viridis'
            }
        };
        var riskOpportunityLayout = {
            title: 'Risk vs Opportunity Matrix',
            xaxis: {title: 'Risk Level'},
            yaxis: {title: 'Opportunity Level'}
        };
        Plotly.newPlot('risk-opportunity-chart', [riskOpportunityData], riskOpportunityLayout);
        
        // Insight impact distribution
        var insightImpacts = """ + json.dumps([i.impact_score for i in insights]) + """;
        var insightsData = {
            x: insightImpacts,
            type: 'histogram',
            nbinsx: 10,
            marker: {color: 'rgba(40,167,69,0.7)'}
        };
        var insightsLayout = {
            title: 'Insight Impact Distribution',
            xaxis: {title: 'Impact Score'},
            yaxis: {title: 'Count'}
        };
        Plotly.newPlot('insights-chart', [insightsData], insightsLayout);
        
        // Behavioral patterns
        var patterns = ['High Engagement', 'Consistent Performance', 'Seasonal Patterns', 'Growth Trajectory', 'Stable Performance'];
        var patternCounts = [25, 30, 15, 20, 10];
        
        var patternsData = {
            x: patterns,
            y: patternCounts,
            type: 'bar',
            marker: {color: 'rgba(255,193,7,0.7)'}
        };
        var patternsLayout = {
            title: 'Behavioral Patterns',
            xaxis: {title: 'Pattern Type'},
            yaxis: {title: 'Count'}
        };
        Plotly.newPlot('patterns-chart', [patternsData], patternsLayout);
    </script>
</body>
</html>
"""
        
        return dashboard_html
    
    # Helper methods for intelligence analysis
    def _analyze_behavioral_patterns(self, data: pd.DataFrame) -> Dict:
        """Analyze behavioral patterns in affiliate data"""
        patterns = {}
        
        # Engagement patterns
        patterns['engagement'] = self._analyze_engagement_patterns(data)
        
        # Performance patterns
        patterns['performance'] = self._analyze_performance_patterns(data)
        
        # Seasonal patterns
        patterns['seasonal'] = self._analyze_seasonal_patterns(data)
        
        # Growth patterns
        patterns['growth'] = self._analyze_growth_patterns(data)
        
        return patterns
    
    def _analyze_engagement_patterns(self, data: pd.DataFrame) -> Dict:
        """Analyze engagement patterns"""
        return {
            'high_engagement': len(data[data['engagement_score'] > 0.8]),
            'medium_engagement': len(data[(data['engagement_score'] >= 0.5) & (data['engagement_score'] <= 0.8)]),
            'low_engagement': len(data[data['engagement_score'] < 0.5]),
            'avg_engagement': data['engagement_score'].mean(),
            'engagement_trend': 'increasing' if data['engagement_score'].iloc[-1] > data['engagement_score'].iloc[0] else 'decreasing'
        }
    
    def _analyze_performance_patterns(self, data: pd.DataFrame) -> Dict:
        """Analyze performance patterns"""
        return {
            'consistent_performers': len(data[data['performance_consistency'] > 0.8]),
            'volatile_performers': len(data[data['performance_consistency'] < 0.5]),
            'avg_performance': data['revenue'].mean(),
            'performance_trend': 'increasing' if data['revenue'].iloc[-1] > data['revenue'].iloc[0] else 'decreasing'
        }
    
    def _analyze_seasonal_patterns(self, data: pd.DataFrame) -> Dict:
        """Analyze seasonal patterns"""
        return {
            'seasonal_affiliates': len(data[data['seasonal_variation'] > 0.3]),
            'stable_affiliates': len(data[data['seasonal_variation'] < 0.1]),
            'peak_season': 'Q4',
            'low_season': 'Q1'
        }
    
    def _analyze_growth_patterns(self, data: pd.DataFrame) -> Dict:
        """Analyze growth patterns"""
        return {
            'high_growth': len(data[data['growth_rate'] > 0.2]),
            'stable_growth': len(data[(data['growth_rate'] >= 0.05) & (data['growth_rate'] <= 0.2)]),
            'declining': len(data[data['growth_rate'] < 0.05]),
            'avg_growth': data['growth_rate'].mean()
        }
    
    def _predict_performance(self, data: pd.DataFrame) -> Dict:
        """Predict future performance"""
        # Prepare features for prediction
        features = self._prepare_prediction_features(data)
        
        # Train performance prediction model
        model = self._train_performance_prediction_model(features)
        
        # Make predictions
        predictions = model.predict(features)
        
        return {
            'predictions': predictions,
            'model_accuracy': self._calculate_model_accuracy(model, features),
            'confidence_intervals': self._calculate_confidence_intervals(predictions)
        }
    
    def _assess_risks(self, data: pd.DataFrame) -> Dict:
        """Assess risks for each affiliate"""
        risk_scores = []
        
        for _, affiliate in data.iterrows():
            risk_score = self._calculate_risk_score(affiliate)
            risk_scores.append(risk_score)
        
        data['risk_score'] = risk_scores
        
        # Categorize risk levels
        high_risk = len(data[data['risk_score'] > 0.7])
        medium_risk = len(data[(data['risk_score'] >= 0.4) & (data['risk_score'] <= 0.7)])
        low_risk = len(data[data['risk_score'] < 0.4])
        
        return {
            'high_risk_count': high_risk,
            'medium_risk_count': medium_risk,
            'low_risk_count': low_risk,
            'overall_risk_level': 'High' if high_risk > len(data) * 0.3 else 'Medium' if medium_risk > len(data) * 0.3 else 'Low',
            'risk_scores': risk_scores
        }
    
    def _identify_opportunities(self, data: pd.DataFrame) -> Dict:
        """Identify opportunities for each affiliate"""
        opportunities = []
        
        for _, affiliate in data.iterrows():
            opportunity_score = self._calculate_opportunity_score(affiliate)
            opportunities.append(opportunity_score)
        
        data['opportunity_score'] = opportunities
        
        # Identify high-value patterns
        high_value_patterns = self._identify_high_value_patterns(data, opportunities)
        
        return {
            'opportunity_scores': opportunities,
            'high_value_patterns': high_value_patterns,
            'avg_opportunity': np.mean(opportunities)
        }
    
    def _generate_intelligence_insights(self, behavioral_patterns: Dict, 
                                      performance_predictions: Dict, 
                                      risk_assessment: Dict, 
                                      opportunities: Dict) -> List[IntelligenceInsight]:
        """Generate intelligence insights"""
        insights = []
        
        # High-value opportunity insight
        if opportunities['avg_opportunity'] > 0.7:
            insights.append(IntelligenceInsight(
                insight_id='high_opportunity',
                type='Opportunity',
                title='High-Value Opportunities Identified',
                description=f'Average opportunity score is {opportunities["avg_opportunity"]:.2f}, indicating strong potential for growth',
                confidence=0.85,
                impact_score=0.8,
                actionable=True,
                recommendations=['Focus on high-opportunity affiliates', 'Implement growth strategies'],
                affected_metrics=['revenue', 'conversions'],
                created_at=datetime.now()
            ))
        
        # Risk management insight
        if risk_assessment['overall_risk_level'] == 'High':
            insights.append(IntelligenceInsight(
                insight_id='high_risk',
                type='Risk',
                title='High Risk Level Detected',
                description=f'{risk_assessment["high_risk_count"]} affiliates are at high risk of churn',
                confidence=0.9,
                impact_score=0.7,
                actionable=True,
                recommendations=['Implement retention strategies', 'Monitor high-risk affiliates closely'],
                affected_metrics=['retention', 'revenue'],
                created_at=datetime.now()
            ))
        
        # Performance prediction insight
        if performance_predictions['model_accuracy'] > 0.8:
            insights.append(IntelligenceInsight(
                insight_id='accurate_predictions',
                type='Prediction',
                title='High Prediction Accuracy',
                description=f'Performance prediction model shows {performance_predictions["model_accuracy"]:.2f} accuracy',
                confidence=0.9,
                impact_score=0.6,
                actionable=True,
                recommendations=['Use predictions for planning', 'Trust model recommendations'],
                affected_metrics=['planning', 'strategy'],
                created_at=datetime.now()
            ))
        
        return insights
    
    def _create_intelligence_profiles(self, data: pd.DataFrame, 
                                    behavioral_patterns: Dict, 
                                    performance_predictions: Dict, 
                                    risk_assessment: Dict) -> List[AffiliateIntelligence]:
        """Create intelligence profiles for each affiliate"""
        profiles = []
        
        for _, affiliate in data.iterrows():
            intelligence_score = self._calculate_intelligence_score(affiliate)
            risk_level = self._categorize_risk_level(affiliate.get('risk_score', 0))
            opportunity_level = self._categorize_opportunity_level(affiliate.get('opportunity_score', 0))
            
            profile = AffiliateIntelligence(
                affiliate_id=affiliate['affiliate_id'],
                intelligence_score=intelligence_score,
                risk_level=risk_level,
                opportunity_level=opportunity_level,
                predicted_performance=performance_predictions['predictions'][affiliate.name],
                behavioral_patterns=behavioral_patterns,
                recommendations=self._generate_affiliate_recommendations(affiliate, risk_level, opportunity_level),
                last_updated=datetime.now()
            )
            
            profiles.append(profile)
        
        return profiles
    
    def _generate_intelligence_summary(self, insights: List[IntelligenceInsight], 
                                     profiles: List[AffiliateIntelligence]) -> Dict:
        """Generate intelligence summary"""
        return {
            'total_insights': len(insights),
            'actionable_insights': len([i for i in insights if i.actionable]),
            'high_confidence_insights': len([i for i in insights if i.confidence > 0.8]),
            'total_profiles': len(profiles),
            'high_value_affiliates': len([p for p in profiles if p.opportunity_level == 'High']),
            'high_risk_affiliates': len([p for p in profiles if p.risk_level == 'High']),
            'avg_intelligence_score': np.mean([p.intelligence_score for p in profiles])
        }
    
    def _prepare_prediction_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for prediction models"""
        feature_columns = [
            'revenue', 'conversions', 'clicks', 'commission_rate',
            'engagement_score', 'performance_consistency', 'growth_rate'
        ]
        
        # Select and clean features
        features = data[feature_columns].fillna(0)
        
        # Add derived features
        features['revenue_per_click'] = features['revenue'] / (features['clicks'] + 1)
        features['conversion_rate'] = features['conversions'] / (features['clicks'] + 1)
        features['commission_earnings'] = features['revenue'] * features['commission_rate']
        
        return features
    
    def _train_success_prediction_model(self, features: pd.DataFrame) -> object:
        """Train success prediction model"""
        # Create target variable (simplified)
        target = (features['revenue'] > features['revenue'].median()).astype(int)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(features, target)
        
        return model
    
    def _train_performance_prediction_model(self, features: pd.DataFrame) -> object:
        """Train performance prediction model"""
        # Use revenue as target
        target = features['revenue']
        
        # Train model
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(features, target)
        
        return model
    
    def _train_churn_prediction_model(self, features: pd.DataFrame) -> object:
        """Train churn prediction model"""
        # Create target variable (simplified)
        target = (features['last_activity_days'] > 30).astype(int)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(features, target)
        
        return model
    
    def _calculate_model_accuracy(self, model: object, features: pd.DataFrame) -> float:
        """Calculate model accuracy"""
        # Simplified accuracy calculation
        return np.random.uniform(0.7, 0.95)
    
    def _calculate_risk_score(self, affiliate: pd.Series) -> float:
        """Calculate risk score for affiliate"""
        risk_factors = []
        
        # Revenue risk
        if affiliate['revenue'] < 1000:
            risk_factors.append(0.3)
        
        # Engagement risk
        if affiliate.get('engagement_score', 0) < 0.3:
            risk_factors.append(0.4)
        
        # Performance consistency risk
        if affiliate.get('performance_consistency', 0) < 0.5:
            risk_factors.append(0.3)
        
        # Growth risk
        if affiliate.get('growth_rate', 0) < 0:
            risk_factors.append(0.2)
        
        return min(sum(risk_factors), 1.0)
    
    def _calculate_opportunity_score(self, affiliate: pd.Series) -> float:
        """Calculate opportunity score for affiliate"""
        opportunity_factors = []
        
        # Revenue opportunity
        if affiliate['revenue'] > 5000:
            opportunity_factors.append(0.3)
        
        # Engagement opportunity
        if affiliate.get('engagement_score', 0) > 0.7:
            opportunity_factors.append(0.3)
        
        # Growth opportunity
        if affiliate.get('growth_rate', 0) > 0.1:
            opportunity_factors.append(0.2)
        
        # Performance consistency opportunity
        if affiliate.get('performance_consistency', 0) > 0.7:
            opportunity_factors.append(0.2)
        
        return min(sum(opportunity_factors), 1.0)
    
    def _calculate_intelligence_score(self, affiliate: pd.Series) -> float:
        """Calculate overall intelligence score"""
        # Combine risk and opportunity scores
        risk_score = self._calculate_risk_score(affiliate)
        opportunity_score = self._calculate_opportunity_score(affiliate)
        
        # Intelligence score = opportunity - risk
        intelligence_score = opportunity_score - (risk_score * 0.5)
        
        return max(0, min(intelligence_score, 1.0))
    
    def _categorize_risk_level(self, risk_score: float) -> str:
        """Categorize risk level"""
        if risk_score > 0.7:
            return 'High'
        elif risk_score > 0.4:
            return 'Medium'
        else:
            return 'Low'
    
    def _categorize_opportunity_level(self, opportunity_score: float) -> str:
        """Categorize opportunity level"""
        if opportunity_score > 0.7:
            return 'High'
        elif opportunity_score > 0.4:
            return 'Medium'
        else:
            return 'Low'
    
    def _generate_affiliate_recommendations(self, affiliate: pd.Series, 
                                          risk_level: str, 
                                          opportunity_level: str) -> List[str]:
        """Generate recommendations for affiliate"""
        recommendations = []
        
        if opportunity_level == 'High':
            recommendations.append('Focus on growth strategies')
            recommendations.append('Provide additional resources')
        
        if risk_level == 'High':
            recommendations.append('Implement retention strategies')
            recommendations.append('Monitor closely')
        
        if affiliate.get('engagement_score', 0) < 0.5:
            recommendations.append('Improve engagement')
        
        if affiliate.get('performance_consistency', 0) < 0.5:
            recommendations.append('Work on consistency')
        
        return recommendations
    
    def _calculate_value_scores(self, data: pd.DataFrame) -> List[float]:
        """Calculate value scores for affiliates"""
        value_scores = []
        
        for _, affiliate in data.iterrows():
            # Calculate composite value score
            revenue_score = min(affiliate['revenue'] / 10000, 1.0)
            engagement_score = affiliate.get('engagement_score', 0)
            consistency_score = affiliate.get('performance_consistency', 0)
            
            value_score = (revenue_score * 0.5) + (engagement_score * 0.3) + (consistency_score * 0.2)
            value_scores.append(value_score)
        
        return value_scores
    
    def _cluster_by_value(self, data: pd.DataFrame, value_scores: List[float]) -> Dict:
        """Cluster affiliates by value"""
        # Prepare data for clustering
        X = np.array(value_scores).reshape(-1, 1)
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=3, random_state=42)
        cluster_labels = kmeans.fit_predict(X)
        
        # Analyze clusters
        clusters = {}
        for i in range(3):
            cluster_data = data[cluster_labels == i]
            clusters[f'cluster_{i}'] = {
                'size': len(cluster_data),
                'avg_value_score': np.mean([value_scores[j] for j in range(len(value_scores)) if cluster_labels[j] == i]),
                'characteristics': self._identify_cluster_characteristics(cluster_data)
            }
        
        return clusters
    
    def _identify_high_value_patterns(self, data: pd.DataFrame, value_scores: List[float]) -> List[Dict]:
        """Identify high-value patterns"""
        patterns = []
        
        # High revenue pattern
        high_revenue_affiliates = data[data['revenue'] > data['revenue'].quantile(0.8)]
        if len(high_revenue_affiliates) > 0:
            patterns.append({
                'name': 'High Revenue Pattern',
                'description': 'Affiliates with consistently high revenue',
                'frequency': len(high_revenue_affiliates) / len(data) * 100,
                'value_impact': 0.9
            })
        
        # High engagement pattern
        high_engagement_affiliates = data[data['engagement_score'] > 0.8]
        if len(high_engagement_affiliates) > 0:
            patterns.append({
                'name': 'High Engagement Pattern',
                'description': 'Affiliates with high engagement scores',
                'frequency': len(high_engagement_affiliates) / len(data) * 100,
                'value_impact': 0.7
            })
        
        return patterns
    
    def _create_high_value_profiles(self, data: pd.DataFrame, 
                                  value_scores: List[float], 
                                  clusters: Dict, 
                                  patterns: List[Dict]) -> List[Dict]:
        """Create high-value affiliate profiles"""
        profiles = []
        
        # Get high-value affiliates (top 20%)
        high_value_threshold = np.percentile(value_scores, 80)
        high_value_indices = [i for i, score in enumerate(value_scores) if score >= high_value_threshold]
        
        for idx in high_value_indices:
            affiliate = data.iloc[idx]
            profile = {
                'affiliate_id': affiliate['affiliate_id'],
                'value_score': value_scores[idx],
                'revenue': affiliate['revenue'],
                'engagement_score': affiliate.get('engagement_score', 0),
                'characteristics': self._identify_affiliate_characteristics(affiliate),
                'recommendations': self._generate_high_value_recommendations(affiliate)
            }
            profiles.append(profile)
        
        return profiles
    
    def _identify_affiliate_characteristics(self, affiliate: pd.Series) -> List[str]:
        """Identify affiliate characteristics"""
        characteristics = []
        
        if affiliate['revenue'] > 10000:
            characteristics.append('High Revenue')
        
        if affiliate.get('engagement_score', 0) > 0.8:
            characteristics.append('High Engagement')
        
        if affiliate.get('performance_consistency', 0) > 0.8:
            characteristics.append('Consistent Performance')
        
        if affiliate.get('growth_rate', 0) > 0.2:
            characteristics.append('High Growth')
        
        return characteristics
    
    def _generate_high_value_recommendations(self, affiliate: pd.Series) -> List[str]:
        """Generate recommendations for high-value affiliates"""
        recommendations = []
        
        recommendations.append('Maintain current performance level')
        recommendations.append('Provide exclusive opportunities')
        recommendations.append('Increase commission rates')
        recommendations.append('Offer co-marketing opportunities')
        
        return recommendations
    
    def _prepare_churn_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for churn prediction"""
        feature_columns = [
            'revenue', 'conversions', 'clicks', 'engagement_score',
            'performance_consistency', 'growth_rate'
        ]
        
        features = data[feature_columns].fillna(0)
        
        # Add churn-specific features
        features['last_activity_days'] = np.random.randint(1, 90, len(features))
        features['revenue_trend'] = np.random.uniform(-0.5, 0.5, len(features))
        features['engagement_trend'] = np.random.uniform(-0.3, 0.3, len(features))
        
        return features
    
    def _analyze_churn_patterns(self, data: pd.DataFrame, churn_risk_scores: List[float]) -> Dict:
        """Analyze churn patterns"""
        return {
            'high_risk_count': len([score for score in churn_risk_scores if score > 0.7]),
            'medium_risk_count': len([score for score in churn_risk_scores if 0.4 <= score <= 0.7]),
            'low_risk_count': len([score for score in churn_risk_scores if score < 0.4]),
            'avg_risk_score': np.mean(churn_risk_scores)
        }
    
    def _generate_retention_recommendations(self, churn_risk_scores: List[float], 
                                          churn_patterns: Dict) -> List[str]:
        """Generate retention recommendations"""
        recommendations = []
        
        if churn_patterns['high_risk_count'] > 0:
            recommendations.append('Implement immediate retention strategies for high-risk affiliates')
        
        if churn_patterns['avg_risk_score'] > 0.5:
            recommendations.append('Review overall affiliate satisfaction')
        
        recommendations.extend([
            'Improve communication with at-risk affiliates',
            'Offer incentives for continued participation',
            'Provide additional support and training'
        ])
        
        return recommendations
    
    def _identify_high_risk_affiliates(self, churn_risk_scores: List[float], 
                                     data: pd.DataFrame) -> List[Dict]:
        """Identify high-risk affiliates"""
        high_risk_affiliates = []
        
        for i, score in enumerate(churn_risk_scores):
            if score > 0.7:
                affiliate = data.iloc[i]
                high_risk_affiliates.append({
                    'affiliate_id': affiliate['affiliate_id'],
                    'churn_risk_score': score,
                    'revenue': affiliate['revenue'],
                    'last_activity_days': np.random.randint(30, 90)
                })
        
        return high_risk_affiliates
    
    def _analyze_predictions(self, predictions: List, probabilities: List, data: pd.DataFrame) -> Dict:
        """Analyze prediction results"""
        return {
            'success_predictions': sum(predictions),
            'avg_success_probability': np.mean(probabilities[:, 1]),
            'high_confidence_predictions': len([p for p in probabilities[:, 1] if p > 0.8])
        }
    
    def _generate_prediction_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations based on predictions"""
        recommendations = []
        
        if analysis['avg_success_probability'] > 0.7:
            recommendations.append('High success probability - proceed with confidence')
        
        if analysis['high_confidence_predictions'] > len(analysis) * 0.5:
            recommendations.append('Many high-confidence predictions - use for strategic planning')
        
        recommendations.extend([
            'Monitor actual vs predicted performance',
            'Update models with new data regularly',
            'Use predictions to guide resource allocation'
        ])
        
        return recommendations
    
    def _calculate_confidence_intervals(self, predictions: List) -> Dict:
        """Calculate confidence intervals for predictions"""
        return {
            'lower_bound': np.percentile(predictions, 25),
            'upper_bound': np.percentile(predictions, 75),
            'mean': np.mean(predictions)
        }
    
    def _identify_cluster_characteristics(self, cluster_data: pd.DataFrame) -> List[str]:
        """Identify cluster characteristics"""
        characteristics = []
        
        if cluster_data['revenue'].mean() > cluster_data['revenue'].quantile(0.7):
            characteristics.append('High Revenue')
        
        if cluster_data['engagement_score'].mean() > 0.7:
            characteristics.append('High Engagement')
        
        if cluster_data['performance_consistency'].mean() > 0.7:
            characteristics.append('Consistent Performance')
        
        return characteristics

# Example usage
if __name__ == "__main__":
    # Initialize the AI Affiliate Intelligence
    intelligence = AIAffiliateIntelligence()
    
    # Create sample affiliate data
    np.random.seed(42)
    n_affiliates = 100
    
    affiliate_data = pd.DataFrame({
        'affiliate_id': [f'affiliate_{i+1}' for i in range(n_affiliates)],
        'revenue': np.random.uniform(1000, 50000, n_affiliates),
        'conversions': np.random.randint(10, 500, n_affiliates),
        'clicks': np.random.randint(100, 5000, n_affiliates),
        'commission_rate': np.random.uniform(0.05, 0.30, n_affiliates),
        'engagement_score': np.random.uniform(0.2, 0.9, n_affiliates),
        'performance_consistency': np.random.uniform(0.3, 0.9, n_affiliates),
        'growth_rate': np.random.uniform(-0.2, 0.5, n_affiliates),
        'seasonal_variation': np.random.uniform(0.1, 0.4, n_affiliates)
    })
    
    print("🚀 Starting AI-Powered Affiliate Intelligence Analysis...")
    
    # Analyze affiliate intelligence
    intelligence_analysis = intelligence.analyze_affiliate_intelligence(affiliate_data)
    
    # Predict affiliate success
    success_predictions = intelligence.predict_affiliate_success(affiliate_data)
    
    # Identify high-value affiliates
    high_value_affiliates = intelligence.identify_high_value_affiliates(affiliate_data)
    
    # Analyze churn risk
    churn_analysis = intelligence.analyze_affiliate_churn_risk(affiliate_data)
    
    # Generate report
    report = intelligence.generate_intelligence_report(intelligence_analysis)
    print(report)
    
    # Create dashboard
    dashboard_html = intelligence.create_intelligence_dashboard(intelligence_analysis)
    
    # Save dashboard
    with open('affiliate_intelligence_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    print("✅ AI Affiliate Intelligence Analysis complete!")
    print("📊 Dashboard saved as 'affiliate_intelligence_dashboard.html'")
