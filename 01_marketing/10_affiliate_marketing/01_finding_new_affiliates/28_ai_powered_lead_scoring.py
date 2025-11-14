"""
AI-Powered Lead Scoring System for Affiliate Marketing
Advanced lead qualification and scoring using machine learning
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib
import warnings
warnings.filterwarnings('ignore')

@dataclass
class LeadProfile:
    """Lead profile data structure"""
    lead_id: str
    name: str
    email: str
    company: str
    industry: str
    website: str
    social_profiles: Dict
    engagement_metrics: Dict
    demographic_data: Dict
    behavioral_data: Dict
    lead_source: str
    lead_score: float
    qualification_status: str
    conversion_probability: float
    next_best_action: str
    created_at: datetime
    last_updated: datetime

class AILeadScorer:
    """AI-powered lead scoring system"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_importance = {}
        self.scoring_rules = {}
        self.lead_database = []
        
    def train_scoring_models(self, historical_data: pd.DataFrame) -> Dict:
        """Train AI models for lead scoring"""
        print("🤖 Training AI lead scoring models...")
        
        # Prepare features
        X, y = self._prepare_training_data(historical_data)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train multiple models
        models = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'logistic_regression': LogisticRegression(random_state=42, max_iter=1000)
        }
        
        model_scores = {}
        
        for name, model in models.items():
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
            
            # Calculate metrics
            auc_score = roc_auc_score(y_test, y_pred_proba)
            accuracy = model.score(X_test_scaled, y_test)
            
            model_scores[name] = {
                'auc': auc_score,
                'accuracy': accuracy,
                'model': model
            }
            
            # Store model
            self.models[name] = model
        
        # Store scaler
        self.scalers['main'] = scaler
        
        # Get feature importance
        self.feature_importance = self._get_feature_importance(models['random_forest'], X.columns)
        
        # Select best model
        best_model_name = max(model_scores.keys(), key=lambda x: model_scores[x]['auc'])
        best_model = model_scores[best_model_name]['model']
        
        print(f"✅ Best model: {best_model_name} (AUC: {model_scores[best_model_name]['auc']:.3f})")
        
        return {
            'model_scores': model_scores,
            'best_model': best_model_name,
            'feature_importance': self.feature_importance
        }
    
    def score_lead(self, lead_data: Dict) -> LeadProfile:
        """Score a single lead using AI models"""
        # Extract features
        features = self._extract_lead_features(lead_data)
        
        # Scale features
        if 'main' in self.scalers:
            features_scaled = self.scalers['main'].transform([features])
        else:
            features_scaled = [features]
        
        # Get predictions from all models
        predictions = {}
        for name, model in self.models.items():
            pred_proba = model.predict_proba(features_scaled)[0]
            predictions[name] = pred_proba[1]  # Probability of conversion
        
        # Calculate ensemble score
        lead_score = np.mean(list(predictions.values()))
        
        # Determine qualification status
        qualification_status = self._determine_qualification_status(lead_score)
        
        # Calculate conversion probability
        conversion_probability = self._calculate_conversion_probability(lead_score, lead_data)
        
        # Determine next best action
        next_best_action = self._determine_next_best_action(lead_score, lead_data)
        
        # Create lead profile
        lead_profile = LeadProfile(
            lead_id=lead_data.get('lead_id', f"lead_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            name=lead_data.get('name', 'Unknown'),
            email=lead_data.get('email', ''),
            company=lead_data.get('company', ''),
            industry=lead_data.get('industry', ''),
            website=lead_data.get('website', ''),
            social_profiles=lead_data.get('social_profiles', {}),
            engagement_metrics=lead_data.get('engagement_metrics', {}),
            demographic_data=lead_data.get('demographic_data', {}),
            behavioral_data=lead_data.get('behavioral_data', {}),
            lead_source=lead_data.get('lead_source', 'Unknown'),
            lead_score=lead_score,
            qualification_status=qualification_status,
            conversion_probability=conversion_probability,
            next_best_action=next_best_action,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        # Store in database
        self.lead_database.append(lead_profile)
        
        return lead_profile
    
    def batch_score_leads(self, leads_data: List[Dict]) -> List[LeadProfile]:
        """Score multiple leads in batch"""
        print(f"📊 Batch scoring {len(leads_data)} leads...")
        
        lead_profiles = []
        for lead_data in leads_data:
            profile = self.score_lead(lead_data)
            lead_profiles.append(profile)
        
        return lead_profiles
    
    def update_lead_score(self, lead_id: str, new_data: Dict) -> LeadProfile:
        """Update lead score with new data"""
        # Find existing lead
        existing_lead = None
        for i, lead in enumerate(self.lead_database):
            if lead.lead_id == lead_id:
                existing_lead = lead
                break
        
        if not existing_lead:
            raise ValueError(f"Lead {lead_id} not found")
        
        # Update lead data
        updated_data = {
            'lead_id': lead_id,
            'name': existing_lead.name,
            'email': existing_lead.email,
            'company': existing_lead.company,
            'industry': existing_lead.industry,
            'website': existing_lead.website,
            'social_profiles': {**existing_lead.social_profiles, **new_data.get('social_profiles', {})},
            'engagement_metrics': {**existing_lead.engagement_metrics, **new_data.get('engagement_metrics', {})},
            'demographic_data': {**existing_lead.demographic_data, **new_data.get('demographic_data', {})},
            'behavioral_data': {**existing_lead.behavioral_data, **new_data.get('behavioral_data', {})},
            'lead_source': existing_lead.lead_source
        }
        
        # Re-score lead
        updated_profile = self.score_lead(updated_data)
        updated_profile.created_at = existing_lead.created_at
        
        # Update in database
        self.lead_database[i] = updated_profile
        
        return updated_profile
    
    def get_lead_insights(self, lead_id: str) -> Dict:
        """Get detailed insights for a specific lead"""
        lead = self._find_lead_by_id(lead_id)
        if not lead:
            raise ValueError(f"Lead {lead_id} not found")
        
        # Analyze lead characteristics
        characteristics = self._analyze_lead_characteristics(lead)
        
        # Predict conversion timeline
        conversion_timeline = self._predict_conversion_timeline(lead)
        
        # Recommend engagement strategy
        engagement_strategy = self._recommend_engagement_strategy(lead)
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(lead)
        
        # Calculate lead value
        lead_value = self._calculate_lead_value(lead)
        
        return {
            'lead_profile': lead,
            'characteristics': characteristics,
            'conversion_timeline': conversion_timeline,
            'engagement_strategy': engagement_strategy,
            'risk_factors': risk_factors,
            'lead_value': lead_value,
            'recommendations': self._generate_lead_recommendations(lead)
        }
    
    def generate_lead_scoring_report(self) -> str:
        """Generate comprehensive lead scoring report"""
        if not self.lead_database:
            return "No leads in database"
        
        # Calculate statistics
        total_leads = len(self.lead_database)
        avg_score = np.mean([lead.lead_score for lead in self.lead_database])
        qualified_leads = len([lead for lead in self.lead_database if lead.qualification_status == 'Qualified'])
        high_value_leads = len([lead for lead in self.lead_database if lead.lead_score > 0.7])
        
        # Analyze by source
        source_analysis = self._analyze_by_source()
        
        # Analyze by industry
        industry_analysis = self._analyze_by_industry()
        
        # Analyze by score distribution
        score_distribution = self._analyze_score_distribution()
        
        report = f"""
# 🎯 AI-Powered Lead Scoring Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Executive Summary
- **Total Leads**: {total_leads:,}
- **Average Score**: {avg_score:.3f}
- **Qualified Leads**: {qualified_leads:,} ({qualified_leads/total_leads*100:.1f}%)
- **High-Value Leads**: {high_value_leads:,} ({high_value_leads/total_leads*100:.1f}%)

## 🏆 Top Performing Lead Sources
"""
        
        for source, stats in source_analysis.items():
            report += f"""
### {source}
- **Count**: {stats['count']:,}
- **Avg Score**: {stats['avg_score']:.3f}
- **Qualification Rate**: {stats['qualification_rate']:.1f}%
"""
        
        report += f"""
## 🏭 Industry Analysis
"""
        
        for industry, stats in industry_analysis.items():
            report += f"""
### {industry}
- **Count**: {stats['count']:,}
- **Avg Score**: {stats['avg_score']:.3f}
- **Conversion Probability**: {stats['conversion_probability']:.1f}%
"""
        
        report += f"""
## 📈 Score Distribution
- **0.0-0.2**: {score_distribution['low']:,} leads ({score_distribution['low']/total_leads*100:.1f}%)
- **0.2-0.5**: {score_distribution['medium']:,} leads ({score_distribution['medium']/total_leads*100:.1f}%)
- **0.5-0.8**: {score_distribution['high']:,} leads ({score_distribution['high']/total_leads*100:.1f}%)
- **0.8-1.0**: {score_distribution['very_high']:,} leads ({score_distribution['very_high']/total_leads*100:.1f}%)

## 🎯 Recommendations
1. **Focus on High-Scoring Leads**: Prioritize leads with scores above 0.7
2. **Improve Low-Scoring Sources**: Investigate and optimize low-performing lead sources
3. **Industry Targeting**: Focus on industries with higher conversion probabilities
4. **Lead Nurturing**: Implement targeted nurturing campaigns for medium-scoring leads
5. **Model Retraining**: Regularly retrain models with new data for better accuracy

## 🔍 Next Steps
1. Implement automated lead routing based on scores
2. Set up lead nurturing workflows
3. Monitor model performance and retrain as needed
4. A/B test different engagement strategies
5. Track conversion rates by lead score ranges
"""
        
        return report
    
    def create_lead_scoring_dashboard(self) -> str:
        """Create interactive lead scoring dashboard"""
        if not self.lead_database:
            return "<h1>No leads in database</h1>"
        
        # Prepare data for visualization
        leads_data = []
        for lead in self.lead_database:
            leads_data.append({
                'lead_id': lead.lead_id,
                'name': lead.name,
                'company': lead.company,
                'industry': lead.industry,
                'lead_source': lead.lead_source,
                'lead_score': lead.lead_score,
                'qualification_status': lead.qualification_status,
                'conversion_probability': lead.conversion_probability,
                'created_at': lead.created_at
            })
        
        df = pd.DataFrame(leads_data)
        
        # Create HTML dashboard
        dashboard_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Lead Scoring Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .dashboard {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .chart {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .stat-label {{ font-size: 14px; color: #666; }}
    </style>
</head>
<body>
    <h1>🎯 AI Lead Scoring Dashboard</h1>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{len(df):,}</div>
            <div class="stat-label">Total Leads</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{df['lead_score'].mean():.3f}</div>
            <div class="stat-label">Avg Score</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(df[df['qualification_status'] == 'Qualified']):,}</div>
            <div class="stat-label">Qualified</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(df[df['lead_score'] > 0.7]):,}</div>
            <div class="stat-label">High-Value</div>
        </div>
    </div>
    
    <div class="dashboard">
        <div class="chart">
            <h3>Lead Score Distribution</h3>
            <div id="score-distribution"></div>
        </div>
        
        <div class="chart">
            <h3>Qualification Status</h3>
            <div id="qualification-status"></div>
        </div>
        
        <div class="chart">
            <h3>Score by Lead Source</h3>
            <div id="score-by-source"></div>
        </div>
        
        <div class="chart">
            <h3>Score by Industry</h3>
            <div id="score-by-industry"></div>
        </div>
    </div>
    
    <script>
        // Score distribution histogram
        var scoreData = {df['lead_score'].tolist()};
        var scoreTrace = {{
            x: scoreData,
            type: 'histogram',
            nbinsx: 20,
            marker: {{color: 'rgba(0,123,255,0.7)'}}
        }};
        var scoreLayout = {{
            title: 'Lead Score Distribution',
            xaxis: {{title: 'Lead Score'}},
            yaxis: {{title: 'Count'}}
        }};
        Plotly.newPlot('score-distribution', [scoreTrace], scoreLayout);
        
        // Qualification status pie chart
        var qualData = {df['qualification_status'].value_counts().to_dict()};
        var qualTrace = {{
            labels: Object.keys(qualData),
            values: Object.values(qualData),
            type: 'pie',
            marker: {{colors: ['#28a745', '#ffc107', '#dc3545']}}
        }};
        var qualLayout = {{
            title: 'Qualification Status Distribution'
        }};
        Plotly.newPlot('qualification-status', [qualTrace], qualLayout);
        
        // Score by source box plot
        var sourceData = [];
        var sources = {df['lead_source'].unique().tolist()};
        sources.forEach(function(source) {{
            var scores = df[df['lead_source'] == source]['lead_score'].tolist();
            sourceData.push({{
                y: scores,
                name: source,
                type: 'box'
            }});
        }});
        var sourceLayout = {{
            title: 'Lead Score by Source',
            yaxis: {{title: 'Lead Score'}}
        }};
        Plotly.newPlot('score-by-source', sourceData, sourceLayout);
        
        // Score by industry box plot
        var industryData = [];
        var industries = {df['industry'].unique().tolist()};
        industries.forEach(function(industry) {{
            var scores = df[df['industry'] == industry]['lead_score'].tolist();
            industryData.push({{
                y: scores,
                name: industry,
                type: 'box'
            }});
        }});
        var industryLayout = {{
            title: 'Lead Score by Industry',
            yaxis: {{title: 'Lead Score'}}
        }};
        Plotly.newPlot('score-by-industry', industryData, industryLayout);
    </script>
</body>
</html>
"""
        
        return dashboard_html
    
    def export_lead_data(self, filename: str = None) -> str:
        """Export lead data to CSV"""
        if not self.lead_database:
            return "No leads to export"
        
        # Prepare data for export
        export_data = []
        for lead in self.lead_database:
            export_data.append({
                'lead_id': lead.lead_id,
                'name': lead.name,
                'email': lead.email,
                'company': lead.company,
                'industry': lead.industry,
                'website': lead.website,
                'lead_source': lead.lead_source,
                'lead_score': lead.lead_score,
                'qualification_status': lead.qualification_status,
                'conversion_probability': lead.conversion_probability,
                'next_best_action': lead.next_best_action,
                'created_at': lead.created_at,
                'last_updated': lead.last_updated
            })
        
        # Create DataFrame and export
        df = pd.DataFrame(export_data)
        
        if filename is None:
            filename = f"lead_scoring_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        df.to_csv(filename, index=False)
        return f"Lead data exported to {filename}"
    
    def save_models(self, filepath: str = "lead_scoring_models.pkl"):
        """Save trained models to file"""
        model_data = {
            'models': self.models,
            'scalers': self.scalers,
            'encoders': self.encoders,
            'feature_importance': self.feature_importance
        }
        joblib.dump(model_data, filepath)
        return f"Models saved to {filepath}"
    
    def load_models(self, filepath: str = "lead_scoring_models.pkl"):
        """Load trained models from file"""
        model_data = joblib.load(filepath)
        self.models = model_data['models']
        self.scalers = model_data['scalers']
        self.encoders = model_data['encoders']
        self.feature_importance = model_data['feature_importance']
        return "Models loaded successfully"
    
    # Helper methods
    def _prepare_training_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare training data for model training"""
        # Select features
        feature_columns = [
            'company_size', 'industry', 'lead_source', 'website_traffic',
            'social_engagement', 'email_opens', 'email_clicks', 'page_views',
            'time_on_site', 'form_submissions', 'downloads', 'webinar_attendance'
        ]
        
        # Create dummy variables for categorical features
        X = pd.get_dummies(data[feature_columns], columns=['industry', 'lead_source'])
        
        # Target variable (conversion)
        y = data['converted'].astype(int)
        
        return X, y
    
    def _extract_lead_features(self, lead_data: Dict) -> List[float]:
        """Extract features from lead data"""
        features = []
        
        # Company size (encoded)
        company_size = lead_data.get('demographic_data', {}).get('company_size', 'Unknown')
        size_mapping = {'Unknown': 0, 'Startup': 1, 'Small': 2, 'Medium': 3, 'Large': 4, 'Enterprise': 5}
        features.append(size_mapping.get(company_size, 0))
        
        # Industry (encoded)
        industry = lead_data.get('industry', 'Unknown')
        industry_mapping = {'Technology': 1, 'Healthcare': 2, 'Finance': 3, 'Education': 4, 'Other': 0}
        features.append(industry_mapping.get(industry, 0))
        
        # Lead source (encoded)
        lead_source = lead_data.get('lead_source', 'Unknown')
        source_mapping = {'Website': 1, 'Social Media': 2, 'Email': 3, 'Referral': 4, 'Other': 0}
        features.append(source_mapping.get(lead_source, 0))
        
        # Website traffic
        features.append(lead_data.get('engagement_metrics', {}).get('website_traffic', 0))
        
        # Social engagement
        features.append(lead_data.get('engagement_metrics', {}).get('social_engagement', 0))
        
        # Email metrics
        features.append(lead_data.get('engagement_metrics', {}).get('email_opens', 0))
        features.append(lead_data.get('engagement_metrics', {}).get('email_clicks', 0))
        
        # Website behavior
        features.append(lead_data.get('behavioral_data', {}).get('page_views', 0))
        features.append(lead_data.get('behavioral_data', {}).get('time_on_site', 0))
        features.append(lead_data.get('behavioral_data', {}).get('form_submissions', 0))
        features.append(lead_data.get('behavioral_data', {}).get('downloads', 0))
        features.append(lead_data.get('behavioral_data', {}).get('webinar_attendance', 0))
        
        return features
    
    def _determine_qualification_status(self, lead_score: float) -> str:
        """Determine lead qualification status based on score"""
        if lead_score >= 0.8:
            return "Hot Lead"
        elif lead_score >= 0.6:
            return "Qualified"
        elif lead_score >= 0.4:
            return "Warm Lead"
        else:
            return "Cold Lead"
    
    def _calculate_conversion_probability(self, lead_score: float, lead_data: Dict) -> float:
        """Calculate conversion probability based on lead score and additional factors"""
        base_probability = lead_score
        
        # Adjust based on lead source
        source = lead_data.get('lead_source', 'Unknown')
        source_multipliers = {
            'Referral': 1.2,
            'Website': 1.0,
            'Social Media': 0.9,
            'Email': 0.8,
            'Other': 0.7
        }
        base_probability *= source_multipliers.get(source, 1.0)
        
        # Adjust based on engagement level
        engagement = lead_data.get('engagement_metrics', {})
        if engagement.get('email_opens', 0) > 5:
            base_probability *= 1.1
        if engagement.get('social_engagement', 0) > 10:
            base_probability *= 1.05
        
        return min(base_probability, 1.0)
    
    def _determine_next_best_action(self, lead_score: float, lead_data: Dict) -> str:
        """Determine next best action for the lead"""
        if lead_score >= 0.8:
            return "Schedule demo call immediately"
        elif lead_score >= 0.6:
            return "Send personalized email with case study"
        elif lead_score >= 0.4:
            return "Add to nurturing sequence"
        else:
            return "Continue general marketing outreach"
    
    def _find_lead_by_id(self, lead_id: str) -> Optional[LeadProfile]:
        """Find lead by ID"""
        for lead in self.lead_database:
            if lead.lead_id == lead_id:
                return lead
        return None
    
    def _analyze_lead_characteristics(self, lead: LeadProfile) -> Dict:
        """Analyze lead characteristics"""
        return {
            'engagement_level': self._calculate_engagement_level(lead),
            'company_profile': self._analyze_company_profile(lead),
            'behavioral_patterns': self._analyze_behavioral_patterns(lead),
            'communication_preferences': self._analyze_communication_preferences(lead)
        }
    
    def _predict_conversion_timeline(self, lead: LeadProfile) -> Dict:
        """Predict conversion timeline"""
        base_timeline = 30  # days
        
        # Adjust based on lead score
        if lead.lead_score > 0.8:
            timeline = base_timeline * 0.5
        elif lead.lead_score > 0.6:
            timeline = base_timeline * 0.7
        elif lead.lead_score > 0.4:
            timeline = base_timeline * 1.2
        else:
            timeline = base_timeline * 2.0
        
        return {
            'estimated_days': int(timeline),
            'confidence': min(lead.lead_score * 1.2, 1.0),
            'factors': ['Lead score', 'Engagement level', 'Company size']
        }
    
    def _recommend_engagement_strategy(self, lead: LeadProfile) -> Dict:
        """Recommend engagement strategy"""
        strategies = {
            'email': {
                'frequency': 'Weekly' if lead.lead_score > 0.6 else 'Bi-weekly',
                'content_type': 'Case studies' if lead.lead_score > 0.7 else 'Educational content',
                'personalization': 'High' if lead.lead_score > 0.8 else 'Medium'
            },
            'social_media': {
                'platforms': ['LinkedIn'] if lead.industry in ['Technology', 'Finance'] else ['LinkedIn', 'Twitter'],
                'content_focus': 'Industry insights' if lead.lead_score > 0.6 else 'General content'
            },
            'direct_outreach': {
                'method': 'Phone call' if lead.lead_score > 0.8 else 'Email',
                'timing': 'Immediate' if lead.lead_score > 0.8 else 'Within 24 hours'
            }
        }
        
        return strategies
    
    def _identify_risk_factors(self, lead: LeadProfile) -> List[str]:
        """Identify risk factors for the lead"""
        risk_factors = []
        
        if lead.lead_score < 0.3:
            risk_factors.append("Very low engagement")
        
        if lead.engagement_metrics.get('email_opens', 0) == 0:
            risk_factors.append("No email engagement")
        
        if lead.behavioral_data.get('time_on_site', 0) < 30:
            risk_factors.append("Low website engagement")
        
        if lead.company == '':
            risk_factors.append("Missing company information")
        
        return risk_factors
    
    def _calculate_lead_value(self, lead: LeadProfile) -> float:
        """Calculate estimated lead value"""
        base_value = 1000  # Base value
        
        # Adjust based on lead score
        value_multiplier = lead.lead_score
        
        # Adjust based on company size
        company_size = lead.demographic_data.get('company_size', 'Unknown')
        size_multipliers = {
            'Startup': 0.5,
            'Small': 0.8,
            'Medium': 1.2,
            'Large': 1.5,
            'Enterprise': 2.0
        }
        value_multiplier *= size_multipliers.get(company_size, 1.0)
        
        return base_value * value_multiplier
    
    def _generate_lead_recommendations(self, lead: LeadProfile) -> List[str]:
        """Generate specific recommendations for the lead"""
        recommendations = []
        
        if lead.lead_score > 0.8:
            recommendations.append("Prioritize this lead for immediate follow-up")
            recommendations.append("Schedule a demo call within 24 hours")
            recommendations.append("Prepare personalized proposal")
        
        elif lead.lead_score > 0.6:
            recommendations.append("Add to high-priority nurturing sequence")
            recommendations.append("Send relevant case studies")
            recommendations.append("Schedule follow-up in 3-5 days")
        
        elif lead.lead_score > 0.4:
            recommendations.append("Continue nurturing with educational content")
            recommendations.append("Monitor engagement metrics closely")
            recommendations.append("Consider retargeting campaigns")
        
        else:
            recommendations.append("Focus on general brand awareness")
            recommendations.append("Use broad targeting for similar prospects")
            recommendations.append("Consider lead scoring model updates")
        
        return recommendations
    
    def _get_feature_importance(self, model, feature_names) -> Dict:
        """Get feature importance from model"""
        if hasattr(model, 'feature_importances_'):
            importance_dict = dict(zip(feature_names, model.feature_importances_))
            return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
        return {}
    
    def _analyze_by_source(self) -> Dict:
        """Analyze leads by source"""
        source_stats = {}
        
        for lead in self.lead_database:
            source = lead.lead_source
            if source not in source_stats:
                source_stats[source] = {
                    'count': 0,
                    'scores': [],
                    'qualified': 0
                }
            
            source_stats[source]['count'] += 1
            source_stats[source]['scores'].append(lead.lead_score)
            if lead.qualification_status in ['Qualified', 'Hot Lead']:
                source_stats[source]['qualified'] += 1
        
        # Calculate averages
        for source in source_stats:
            stats = source_stats[source]
            stats['avg_score'] = np.mean(stats['scores'])
            stats['qualification_rate'] = (stats['qualified'] / stats['count']) * 100
        
        return source_stats
    
    def _analyze_by_industry(self) -> Dict:
        """Analyze leads by industry"""
        industry_stats = {}
        
        for lead in self.lead_database:
            industry = lead.industry
            if industry not in industry_stats:
                industry_stats[industry] = {
                    'count': 0,
                    'scores': [],
                    'conversion_probabilities': []
                }
            
            industry_stats[industry]['count'] += 1
            industry_stats[industry]['scores'].append(lead.lead_score)
            industry_stats[industry]['conversion_probabilities'].append(lead.conversion_probability)
        
        # Calculate averages
        for industry in industry_stats:
            stats = industry_stats[industry]
            stats['avg_score'] = np.mean(stats['scores'])
            stats['conversion_probability'] = np.mean(stats['conversion_probabilities']) * 100
        
        return industry_stats
    
    def _analyze_score_distribution(self) -> Dict:
        """Analyze score distribution"""
        scores = [lead.lead_score for lead in self.lead_database]
        
        return {
            'low': len([s for s in scores if 0.0 <= s < 0.2]),
            'medium': len([s for s in scores if 0.2 <= s < 0.5]),
            'high': len([s for s in scores if 0.5 <= s < 0.8]),
            'very_high': len([s for s in scores if 0.8 <= s <= 1.0])
        }
    
    def _calculate_engagement_level(self, lead: LeadProfile) -> str:
        """Calculate engagement level"""
        total_engagement = (
            lead.engagement_metrics.get('email_opens', 0) +
            lead.engagement_metrics.get('social_engagement', 0) +
            lead.behavioral_data.get('page_views', 0)
        )
        
        if total_engagement > 20:
            return "High"
        elif total_engagement > 10:
            return "Medium"
        else:
            return "Low"
    
    def _analyze_company_profile(self, lead: LeadProfile) -> Dict:
        """Analyze company profile"""
        return {
            'size': lead.demographic_data.get('company_size', 'Unknown'),
            'industry': lead.industry,
            'website': lead.website,
            'social_presence': len(lead.social_profiles)
        }
    
    def _analyze_behavioral_patterns(self, lead: LeadProfile) -> Dict:
        """Analyze behavioral patterns"""
        return {
            'website_engagement': lead.behavioral_data.get('time_on_site', 0),
            'content_consumption': lead.behavioral_data.get('page_views', 0),
            'form_interactions': lead.behavioral_data.get('form_submissions', 0),
            'download_activity': lead.behavioral_data.get('downloads', 0)
        }
    
    def _analyze_communication_preferences(self, lead: LeadProfile) -> Dict:
        """Analyze communication preferences"""
        return {
            'email_responsiveness': lead.engagement_metrics.get('email_opens', 0),
            'social_engagement': lead.engagement_metrics.get('social_engagement', 0),
            'preferred_content': 'Technical' if lead.industry in ['Technology'] else 'General'
        }

# Example usage
if __name__ == "__main__":
    # Initialize the AI Lead Scorer
    scorer = AILeadScorer()
    
    # Create sample historical data for training
    np.random.seed(42)
    n_samples = 1000
    
    historical_data = pd.DataFrame({
        'company_size': np.random.choice(['Startup', 'Small', 'Medium', 'Large', 'Enterprise'], n_samples),
        'industry': np.random.choice(['Technology', 'Healthcare', 'Finance', 'Education', 'Other'], n_samples),
        'lead_source': np.random.choice(['Website', 'Social Media', 'Email', 'Referral', 'Other'], n_samples),
        'website_traffic': np.random.randint(100, 10000, n_samples),
        'social_engagement': np.random.randint(0, 50, n_samples),
        'email_opens': np.random.randint(0, 20, n_samples),
        'email_clicks': np.random.randint(0, 10, n_samples),
        'page_views': np.random.randint(1, 100, n_samples),
        'time_on_site': np.random.randint(30, 1800, n_samples),
        'form_submissions': np.random.randint(0, 5, n_samples),
        'downloads': np.random.randint(0, 10, n_samples),
        'webinar_attendance': np.random.randint(0, 3, n_samples),
        'converted': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    })
    
    print("🚀 Training AI Lead Scoring Models...")
    
    # Train models
    training_results = scorer.train_scoring_models(historical_data)
    
    # Create sample lead data
    sample_lead = {
        'lead_id': 'lead_001',
        'name': 'John Smith',
        'email': 'john.smith@example.com',
        'company': 'TechCorp Inc',
        'industry': 'Technology',
        'website': 'https://techcorp.com',
        'lead_source': 'Website',
        'social_profiles': {
            'linkedin': 'https://linkedin.com/in/johnsmith',
            'twitter': 'https://twitter.com/johnsmith'
        },
        'engagement_metrics': {
            'website_traffic': 5000,
            'social_engagement': 25,
            'email_opens': 8,
            'email_clicks': 3
        },
        'demographic_data': {
            'company_size': 'Medium',
            'location': 'San Francisco, CA'
        },
        'behavioral_data': {
            'page_views': 15,
            'time_on_site': 600,
            'form_submissions': 2,
            'downloads': 3,
            'webinar_attendance': 1
        }
    }
    
    print("📊 Scoring sample lead...")
    
    # Score the lead
    lead_profile = scorer.score_lead(sample_lead)
    
    print(f"✅ Lead scored: {lead_profile.lead_score:.3f}")
    print(f"📋 Qualification: {lead_profile.qualification_status}")
    print(f"🎯 Next action: {lead_profile.next_best_action}")
    
    # Generate report
    report = scorer.generate_lead_scoring_report()
    print("\n" + report)
    
    # Create dashboard
    dashboard_html = scorer.create_lead_scoring_dashboard()
    
    # Save dashboard
    with open('lead_scoring_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    print("✅ AI Lead Scoring System ready!")
    print("📊 Dashboard saved as 'lead_scoring_dashboard.html'")
