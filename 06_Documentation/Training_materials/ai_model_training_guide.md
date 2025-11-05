---
title: "Ai Model Training Guide"
category: "06_documentation"
tags: ["guide"]
created: "2025-10-29"
path: "06_documentation/Training_materials/ai_model_training_guide.md"
---

# 🤖 AI Model Training Guide - IA Bulk Platform

> **Complete Guide to Training and Deploying AI Models for Marketing Optimization**

## 🎯 Overview

This guide provides comprehensive instructions for training, optimizing, and deploying AI models that power the IA Bulk Referral Contest System. Learn how to build models that achieve 95%+ accuracy in predicting user behavior, personalizing content, and optimizing campaign performance.

## 🧠 AI Model Architecture

### Model Ecosystem Overview

```python
# AI Model Architecture
class AIModelEcosystem:
    def __init__(self):
        self.models = {
            'user_segmentation': UserSegmentationModel(),
            'engagement_prediction': EngagementPredictionModel(),
            'content_optimization': ContentOptimizationModel(),
            'timing_optimization': TimingOptimizationModel(),
            'churn_prediction': ChurnPredictionModel(),
            'revenue_prediction': RevenuePredictionModel()
        }
        
        self.feature_engineering = FeatureEngineeringPipeline()
        self.model_training = ModelTrainingPipeline()
        self.model_deployment = ModelDeploymentPipeline()
        self.model_monitoring = ModelMonitoringPipeline()
    
    def train_all_models(self, training_data):
        """Train all models in the ecosystem"""
        results = {}
        
        for model_name, model in self.models.items():
            print(f"Training {model_name}...")
            
            # Prepare features
            features = self.feature_engineering.prepare_features(
                training_data, 
                model_name
            )
            
            # Train model
            trained_model = self.model_training.train_model(
                model, 
                features
            )
            
            # Evaluate model
            evaluation = self.model_training.evaluate_model(
                trained_model, 
                features
            )
            
            results[model_name] = {
                'model': trained_model,
                'evaluation': evaluation
            }
        
        return results
```

## 📊 Data Preparation & Feature Engineering

### Feature Engineering Pipeline

```python
# Advanced Feature Engineering
class FeatureEngineeringPipeline:
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.feature_selectors = {}
        
    def prepare_user_features(self, user_data):
        """Prepare features for user segmentation model"""
        features = {}
        
        # Demographics
        features['age'] = self.encode_age(user_data['age'])
        features['location'] = self.encode_location(user_data['location'])
        features['industry'] = self.encode_industry(user_data['industry'])
        
        # Behavioral features
        features['email_open_rate'] = user_data['email_opens'] / user_data['emails_sent']
        features['click_rate'] = user_data['clicks'] / user_data['emails_sent']
        features['referral_rate'] = user_data['referrals_made'] / user_data['days_active']
        features['engagement_score'] = self.calculate_engagement_score(user_data)
        
        # Temporal features
        features['days_since_join'] = (datetime.now() - user_data['join_date']).days
        features['days_since_last_activity'] = (datetime.now() - user_data['last_activity']).days
        features['peak_activity_hour'] = self.extract_peak_hour(user_data['activity_log'])
        features['activity_frequency'] = self.calculate_activity_frequency(user_data['activity_log'])
        
        # Content preferences
        features['preferred_content_types'] = self.encode_content_preferences(
            user_data['content_interactions']
        )
        features['subject_line_preferences'] = self.analyze_subject_preferences(
            user_data['email_interactions']
        )
        
        # Social features
        features['network_size'] = len(user_data['connections'])
        features['influence_score'] = self.calculate_influence_score(user_data)
        
        return features
    
    def prepare_engagement_features(self, user_data, email_data):
        """Prepare features for engagement prediction"""
        features = {}
        
        # User features
        user_features = self.prepare_user_features(user_data)
        features.update(user_features)
        
        # Email features
        features['subject_length'] = len(email_data['subject'])
        features['subject_emoji_count'] = self.count_emojis(email_data['subject'])
        features['subject_urgency_words'] = self.count_urgency_words(email_data['subject'])
        features['email_length'] = len(email_data['body'])
        features['cta_count'] = self.count_ctas(email_data['body'])
        features['personalization_level'] = self.calculate_personalization_level(email_data)
        
        # Timing features
        features['send_hour'] = email_data['send_time'].hour
        features['send_day_of_week'] = email_data['send_time'].weekday()
        features['send_day_of_month'] = email_data['send_time'].day
        features['time_since_last_email'] = self.calculate_time_since_last_email(
            user_data, 
            email_data['send_time']
        )
        
        # Context features
        features['campaign_type'] = self.encode_campaign_type(email_data['campaign_type'])
        features['user_tier'] = self.encode_user_tier(user_data['tier'])
        features['seasonality'] = self.calculate_seasonality(email_data['send_time'])
        
        return features
    
    def calculate_engagement_score(self, user_data):
        """Calculate comprehensive engagement score"""
        weights = {
            'email_opens': 0.3,
            'clicks': 0.4,
            'referrals': 0.2,
            'social_shares': 0.1
        }
        
        score = 0
        for metric, weight in weights.items():
            normalized_metric = self.normalize_metric(user_data[metric])
            score += normalized_metric * weight
        
        return min(1.0, max(0.0, score))
    
    def extract_peak_hour(self, activity_log):
        """Extract peak activity hour from user activity log"""
        hour_counts = {}
        for activity in activity_log:
            hour = activity['timestamp'].hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        return max(hour_counts, key=hour_counts.get) if hour_counts else 12
```

### Data Preprocessing

```python
# Data Preprocessing Pipeline
class DataPreprocessingPipeline:
    def __init__(self):
        self.scalers = {
            'standard': StandardScaler(),
            'minmax': MinMaxScaler(),
            'robust': RobustScaler()
        }
        self.encoders = {
            'label': LabelEncoder(),
            'onehot': OneHotEncoder(),
            'target': TargetEncoder()
        }
        self.imputers = {
            'mean': SimpleImputer(strategy='mean'),
            'median': SimpleImputer(strategy='median'),
            'mode': SimpleImputer(strategy='most_frequent'),
            'knn': KNNImputer()
        }
    
    def preprocess_training_data(self, data, target_column):
        """Preprocess training data for model training"""
        processed_data = data.copy()
        
        # Handle missing values
        processed_data = self.handle_missing_values(processed_data)
        
        # Encode categorical variables
        processed_data = self.encode_categorical_variables(processed_data)
        
        # Scale numerical features
        processed_data = self.scale_numerical_features(processed_data)
        
        # Feature selection
        processed_data = self.select_features(processed_data, target_column)
        
        # Handle outliers
        processed_data = self.handle_outliers(processed_data)
        
        return processed_data
    
    def handle_missing_values(self, data):
        """Handle missing values in the dataset"""
        for column in data.columns:
            if data[column].dtype in ['int64', 'float64']:
                # Use KNN imputation for numerical features
                data[column] = self.imputers['knn'].fit_transform(
                    data[[column]]
                ).flatten()
            else:
                # Use mode imputation for categorical features
                data[column] = self.imputers['mode'].fit_transform(
                    data[[column]]
                ).flatten()
        
        return data
    
    def encode_categorical_variables(self, data):
        """Encode categorical variables"""
        categorical_columns = data.select_dtypes(include=['object']).columns
        
        for column in categorical_columns:
            if data[column].nunique() <= 10:
                # Use one-hot encoding for low cardinality
                encoded = self.encoders['onehot'].fit_transform(
                    data[[column]]
                )
                encoded_df = pd.DataFrame(
                    encoded.toarray(),
                    columns=[f"{column}_{cat}" for cat in self.encoders['onehot'].categories_[0]]
                )
                data = pd.concat([data.drop(columns=[column]), encoded_df], axis=1)
            else:
                # Use target encoding for high cardinality
                data[column] = self.encoders['target'].fit_transform(
                    data[column], 
                    data['target'] if 'target' in data.columns else None
                )
        
        return data
```

## 🎯 Model Training

### User Segmentation Model

```python
# User Segmentation Model
class UserSegmentationModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_selector = SelectKBest(score_func=f_classif, k=20)
        
    def train(self, X, y):
        """Train user segmentation model"""
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Select best features
        X_selected = self.feature_selector.fit_transform(X_scaled, y)
        
        # Train ensemble model
        self.model = VotingClassifier([
            ('rf', RandomForestClassifier(n_estimators=100, random_state=42)),
            ('gb', GradientBoostingClassifier(n_estimators=100, random_state=42)),
            ('svm', SVC(probability=True, random_state=42)),
            ('xgb', XGBClassifier(n_estimators=100, random_state=42))
        ])
        
        self.model.fit(X_selected, y)
        
        return self.model
    
    def predict(self, X):
        """Predict user segments"""
        X_scaled = self.scaler.transform(X)
        X_selected = self.feature_selector.transform(X_scaled)
        
        return self.model.predict(X_selected)
    
    def predict_proba(self, X):
        """Predict segment probabilities"""
        X_scaled = self.scaler.transform(X)
        X_selected = self.feature_selector.transform(X_scaled)
        
        return self.model.predict_proba(X_selected)
    
    def get_feature_importance(self):
        """Get feature importance scores"""
        feature_names = self.feature_selector.get_feature_names_out()
        importances = {}
        
        for estimator_name, estimator in self.model.named_estimators_.items():
            if hasattr(estimator, 'feature_importances_'):
                importances[estimator_name] = dict(zip(
                    feature_names, 
                    estimator.feature_importances_
                ))
        
        return importances
```

### Engagement Prediction Model

```python
# Engagement Prediction Model
class EngagementPredictionModel:
    def __init__(self):
        self.models = {
            'open': None,
            'click': None,
            'convert': None
        }
        self.scalers = {
            'open': StandardScaler(),
            'click': StandardScaler(),
            'convert': StandardScaler()
        }
        
    def train(self, X, y_open, y_click, y_convert):
        """Train engagement prediction models"""
        results = {}
        
        # Train open rate model
        X_open_scaled = self.scalers['open'].fit_transform(X)
        self.models['open'] = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.models['open'].fit(X_open_scaled, y_open)
        
        # Train click rate model (only on opened emails)
        open_mask = y_open == 1
        X_click = X[open_mask]
        y_click_filtered = y_click[open_mask]
        
        if len(X_click) > 0:
            X_click_scaled = self.scalers['click'].fit_transform(X_click)
            self.models['click'] = XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            self.models['click'].fit(X_click_scaled, y_click_filtered)
        
        # Train conversion model (only on clicked emails)
        click_mask = y_click == 1
        X_convert = X[click_mask]
        y_convert_filtered = y_convert[click_mask]
        
        if len(X_convert) > 0:
            X_convert_scaled = self.scalers['convert'].fit_transform(X_convert)
            self.models['convert'] = XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            self.models['convert'].fit(X_convert_scaled, y_convert_filtered)
        
        return self.models
    
    def predict_engagement_funnel(self, X):
        """Predict full engagement funnel"""
        # Predict open probability
        X_open_scaled = self.scalers['open'].transform(X)
        open_proba = self.models['open'].predict_proba(X_open_scaled)[:, 1]
        
        # Predict click probability (conditional on open)
        click_proba = np.zeros(len(X))
        if self.models['click'] is not None:
            X_click_scaled = self.scalers['click'].transform(X)
            click_proba = self.models['click'].predict_proba(X_click_scaled)[:, 1]
        
        # Predict conversion probability (conditional on click)
        convert_proba = np.zeros(len(X))
        if self.models['convert'] is not None:
            X_convert_scaled = self.scalers['convert'].transform(X)
            convert_proba = self.models['convert'].predict_proba(X_convert_scaled)[:, 1]
        
        # Calculate overall engagement score
        engagement_score = open_proba * click_proba * convert_proba
        
        return {
            'open_probability': open_proba,
            'click_probability': click_proba,
            'conversion_probability': convert_proba,
            'engagement_score': engagement_score
        }
```

### Content Optimization Model

```python
# Content Optimization Model
class ContentOptimizationModel:
    def __init__(self):
        self.nlp_model = None
        self.optimization_model = None
        self.content_analyzer = ContentAnalyzer()
        
    def train(self, content_data, performance_data):
        """Train content optimization model"""
        # Extract content features
        content_features = []
        for content in content_data:
            features = self.content_analyzer.extract_features(content)
            content_features.append(features)
        
        X = np.array(content_features)
        y = performance_data['engagement_score']
        
        # Train NLP model for content understanding
        self.nlp_model = self.train_nlp_model(content_data, y)
        
        # Train optimization model
        self.optimization_model = XGBRegressor(
            n_estimators=300,
            max_depth=8,
            learning_rate=0.05,
            random_state=42
        )
        self.optimization_model.fit(X, y)
        
        return self.optimization_model
    
    def optimize_content(self, content, user_profile):
        """Optimize content for specific user"""
        # Get base content features
        base_features = self.content_analyzer.extract_features(content)
        
        # Generate optimization suggestions
        suggestions = []
        
        # Subject line optimization
        subject_suggestions = self.optimize_subject_line(
            content['subject'], 
            user_profile
        )
        suggestions.extend(subject_suggestions)
        
        # Body content optimization
        body_suggestions = self.optimize_body_content(
            content['body'], 
            user_profile
        )
        suggestions.extend(body_suggestions)
        
        # CTA optimization
        cta_suggestions = self.optimize_cta(
            content['cta'], 
            user_profile
        )
        suggestions.extend(cta_suggestions)
        
        return suggestions
    
    def optimize_subject_line(self, subject, user_profile):
        """Optimize subject line for user"""
        suggestions = []
        
        # Analyze current subject
        current_features = self.content_analyzer.analyze_subject(subject)
        
        # Generate variations
        variations = self.generate_subject_variations(subject, user_profile)
        
        # Score variations
        for variation in variations:
            features = self.content_analyzer.analyze_subject(variation)
            score = self.optimization_model.predict([features])[0]
            
            suggestions.append({
                'type': 'subject_line',
                'original': subject,
                'optimized': variation,
                'score': score,
                'improvement': score - self.optimization_model.predict([current_features])[0]
            })
        
        return sorted(suggestions, key=lambda x: x['score'], reverse=True)
```

## 🚀 Model Deployment

### Model Deployment Pipeline

```python
# Model Deployment Pipeline
class ModelDeploymentPipeline:
    def __init__(self):
        self.model_registry = ModelRegistry()
        self.deployment_manager = DeploymentManager()
        self.monitoring = ModelMonitoring()
        
    def deploy_model(self, model, model_name, version):
        """Deploy model to production"""
        # Save model to registry
        model_path = self.model_registry.save_model(
            model, 
            model_name, 
            version
        )
        
        # Create deployment configuration
        deployment_config = {
            'model_name': model_name,
            'version': version,
            'model_path': model_path,
            'replicas': 3,
            'resources': {
                'cpu': '1000m',
                'memory': '2Gi'
            },
            'scaling': {
                'min_replicas': 1,
                'max_replicas': 10,
                'target_cpu': 70
            }
        }
        
        # Deploy model
        deployment = self.deployment_manager.deploy(deployment_config)
        
        # Set up monitoring
        self.monitoring.setup_monitoring(model_name, version)
        
        return deployment
    
    def create_model_endpoint(self, model_name, version):
        """Create API endpoint for model"""
        endpoint_config = {
            'name': f"{model_name}-{version}",
            'model_name': model_name,
            'version': version,
            'endpoint_type': 'REST',
            'authentication': 'API_KEY',
            'rate_limiting': {
                'requests_per_minute': 1000,
                'burst_size': 100
            }
        }
        
        endpoint = self.deployment_manager.create_endpoint(endpoint_config)
        return endpoint
```

### Model Serving

```python
# Model Serving API
from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

class ModelServer:
    def __init__(self):
        self.models = {}
        self.load_models()
    
    def load_models(self):
        """Load all deployed models"""
        model_configs = [
            {'name': 'user_segmentation', 'version': '1.0'},
            {'name': 'engagement_prediction', 'version': '1.0'},
            {'name': 'content_optimization', 'version': '1.0'}
        ]
        
        for config in model_configs:
            model_path = f"models/{config['name']}_{config['version']}.pkl"
            self.models[config['name']] = joblib.load(model_path)
    
    def predict_user_segment(self, user_features):
        """Predict user segment"""
        model = self.models['user_segmentation']
        prediction = model.predict([user_features])
        probabilities = model.predict_proba([user_features])
        
        return {
            'segment': prediction[0],
            'probabilities': probabilities[0].tolist()
        }
    
    def predict_engagement(self, user_features, email_features):
        """Predict email engagement"""
        model = self.models['engagement_prediction']
        combined_features = np.concatenate([user_features, email_features])
        
        prediction = model.predict_engagement_funnel([combined_features])
        
        return {
            'open_probability': float(prediction['open_probability'][0]),
            'click_probability': float(prediction['click_probability'][0]),
            'conversion_probability': float(prediction['conversion_probability'][0]),
            'engagement_score': float(prediction['engagement_score'][0])
        }

model_server = ModelServer()

@app.route('/predict/segment', methods=['POST'])
def predict_segment():
    """API endpoint for user segmentation"""
    data = request.json
    user_features = data['features']
    
    result = model_server.predict_user_segment(user_features)
    return jsonify(result)

@app.route('/predict/engagement', methods=['POST'])
def predict_engagement():
    """API endpoint for engagement prediction"""
    data = request.json
    user_features = data['user_features']
    email_features = data['email_features']
    
    result = model_server.predict_engagement(user_features, email_features)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 📊 Model Monitoring & Evaluation

### Model Performance Monitoring

```python
# Model Performance Monitoring
class ModelMonitoring:
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alerting = AlertingSystem()
        self.drift_detector = DriftDetector()
        
    def monitor_model_performance(self, model_name, predictions, actuals):
        """Monitor model performance in production"""
        # Calculate performance metrics
        metrics = self.calculate_metrics(predictions, actuals)
        
        # Check for performance degradation
        baseline_metrics = self.get_baseline_metrics(model_name)
        performance_drift = self.detect_performance_drift(metrics, baseline_metrics)
        
        if performance_drift:
            self.alerting.send_alert(
                f"Performance drift detected for {model_name}",
                {
                    'current_metrics': metrics,
                    'baseline_metrics': baseline_metrics,
                    'drift_score': performance_drift
                }
            )
        
        # Check for data drift
        data_drift = self.drift_detector.detect_drift(
            model_name, 
            predictions
        )
        
        if data_drift:
            self.alerting.send_alert(
                f"Data drift detected for {model_name}",
                {
                    'drift_score': data_drift,
                    'affected_features': data_drift['features']
                }
            )
        
        return {
            'metrics': metrics,
            'performance_drift': performance_drift,
            'data_drift': data_drift
        }
    
    def calculate_metrics(self, predictions, actuals):
        """Calculate model performance metrics"""
        if isinstance(predictions[0], (int, float)):
            # Regression metrics
            return {
                'mse': mean_squared_error(actuals, predictions),
                'rmse': np.sqrt(mean_squared_error(actuals, predictions)),
                'mae': mean_absolute_error(actuals, predictions),
                'r2': r2_score(actuals, predictions)
            }
        else:
            # Classification metrics
            return {
                'accuracy': accuracy_score(actuals, predictions),
                'precision': precision_score(actuals, predictions, average='weighted'),
                'recall': recall_score(actuals, predictions, average='weighted'),
                'f1': f1_score(actuals, predictions, average='weighted'),
                'auc': roc_auc_score(actuals, predictions, multi_class='ovr')
            }
```

### Model Retraining Pipeline

```python
# Model Retraining Pipeline
class ModelRetrainingPipeline:
    def __init__(self):
        self.data_pipeline = DataPipeline()
        self.training_pipeline = ModelTrainingPipeline()
        self.deployment_pipeline = ModelDeploymentPipeline()
        self.evaluation = ModelEvaluation()
        
    def retrain_model(self, model_name, trigger='scheduled'):
        """Retrain model with new data"""
        print(f"Starting retraining for {model_name} (trigger: {trigger})")
        
        # Collect new training data
        new_data = self.data_pipeline.collect_training_data(model_name)
        
        # Prepare features
        features = self.data_pipeline.prepare_features(new_data, model_name)
        
        # Train new model
        new_model = self.training_pipeline.train_model(model_name, features)
        
        # Evaluate new model
        evaluation = self.evaluation.evaluate_model(new_model, features)
        
        # Compare with current model
        current_model = self.get_current_model(model_name)
        current_evaluation = self.evaluation.evaluate_model(current_model, features)
        
        # Check if new model is better
        if self.is_model_improvement(evaluation, current_evaluation):
            print(f"New model shows improvement. Deploying...")
            
            # Deploy new model
            version = self.increment_version(model_name)
            deployment = self.deployment_pipeline.deploy_model(
                new_model, 
                model_name, 
                version
            )
            
            # Update model registry
            self.update_model_registry(model_name, version, evaluation)
            
            return {
                'status': 'deployed',
                'version': version,
                'evaluation': evaluation,
                'improvement': self.calculate_improvement(evaluation, current_evaluation)
            }
        else:
            print(f"New model does not show improvement. Keeping current model.")
            return {
                'status': 'rejected',
                'reason': 'no_improvement',
                'evaluation': evaluation
            }
    
    def is_model_improvement(self, new_eval, current_eval):
        """Check if new model is an improvement"""
        improvement_threshold = 0.02  # 2% improvement required
        
        # Compare primary metric (e.g., accuracy, F1 score)
        primary_metric = 'accuracy' if 'accuracy' in new_eval else 'f1'
        
        improvement = (new_eval[primary_metric] - current_eval[primary_metric]) / current_eval[primary_metric]
        
        return improvement > improvement_threshold
```

## 🎯 Training Best Practices

### Data Quality Assurance

```python
# Data Quality Assurance
class DataQualityAssurance:
    def __init__(self):
        self.validators = {
            'completeness': CompletenessValidator(),
            'consistency': ConsistencyValidator(),
            'accuracy': AccuracyValidator(),
            'timeliness': TimelinessValidator()
        }
    
    def validate_training_data(self, data):
        """Validate training data quality"""
        quality_report = {}
        
        for validator_name, validator in self.validators.items():
            report = validator.validate(data)
            quality_report[validator_name] = report
        
        # Overall quality score
        quality_score = self.calculate_quality_score(quality_report)
        
        return {
            'quality_score': quality_score,
            'details': quality_report,
            'recommendations': self.generate_recommendations(quality_report)
        }
    
    def calculate_quality_score(self, quality_report):
        """Calculate overall data quality score"""
        weights = {
            'completeness': 0.3,
            'consistency': 0.3,
            'accuracy': 0.2,
            'timeliness': 0.2
        }
        
        score = 0
        for metric, weight in weights.items():
            score += quality_report[metric]['score'] * weight
        
        return score
```

### Hyperparameter Optimization

```python
# Hyperparameter Optimization
class HyperparameterOptimizer:
    def __init__(self):
        self.optimizers = {
            'grid': GridSearchCV,
            'random': RandomizedSearchCV,
            'bayesian': BayesSearchCV
        }
    
    def optimize_hyperparameters(self, model, X, y, optimization_type='bayesian'):
        """Optimize model hyperparameters"""
        if optimization_type == 'grid':
            return self.grid_search(model, X, y)
        elif optimization_type == 'random':
            return self.random_search(model, X, y)
        elif optimization_type == 'bayesian':
            return self.bayesian_search(model, X, y)
        else:
            raise ValueError(f"Unknown optimization type: {optimization_type}")
    
    def bayesian_search(self, model, X, y):
        """Bayesian hyperparameter optimization"""
        param_space = self.get_param_space(model)
        
        optimizer = BayesSearchCV(
            model,
            param_space,
            n_iter=100,
            cv=5,
            scoring='f1_weighted',
            random_state=42,
            n_jobs=-1
        )
        
        optimizer.fit(X, y)
        
        return {
            'best_params': optimizer.best_params_,
            'best_score': optimizer.best_score_,
            'best_model': optimizer.best_estimator_
        }
```

## 📈 Model Performance Metrics

### Comprehensive Evaluation Metrics

```python
# Model Evaluation Metrics
class ModelEvaluation:
    def __init__(self):
        self.metrics = {
            'classification': {
                'accuracy': accuracy_score,
                'precision': precision_score,
                'recall': recall_score,
                'f1': f1_score,
                'auc': roc_auc_score,
                'log_loss': log_loss
            },
            'regression': {
                'mse': mean_squared_error,
                'rmse': lambda y_true, y_pred: np.sqrt(mean_squared_error(y_true, y_pred)),
                'mae': mean_absolute_error,
                'r2': r2_score,
                'mape': mean_absolute_percentage_error
            }
        }
    
    def evaluate_model(self, model, X_test, y_test, model_type='classification'):
        """Comprehensive model evaluation"""
        predictions = model.predict(X_test)
        
        if model_type == 'classification':
            probabilities = model.predict_proba(X_test)
            return self.evaluate_classification(y_test, predictions, probabilities)
        else:
            return self.evaluate_regression(y_test, predictions)
    
    def evaluate_classification(self, y_true, y_pred, y_prob):
        """Evaluate classification model"""
        metrics = {}
        
        for metric_name, metric_func in self.metrics['classification'].items():
            if metric_name == 'log_loss':
                metrics[metric_name] = metric_func(y_true, y_prob)
            else:
                metrics[metric_name] = metric_func(y_true, y_pred)
        
        # Additional classification metrics
        metrics['confusion_matrix'] = confusion_matrix(y_true, y_pred).tolist()
        metrics['classification_report'] = classification_report(y_true, y_pred, output_dict=True)
        
        return metrics
```

---

**🤖 This AI Model Training Guide provides everything needed to build, train, and deploy high-performance AI models for the IA Bulk Platform. For implementation support, refer to our [Complete Implementation Guide](./complete-implementation-guide.md) or [Enroll in the AI Marketing Mastery Course](../AI_Marketing_Course_Curriculum.md).**

*Master AI model training to create systems that achieve 95%+ accuracy in predicting user behavior and optimizing marketing campaigns.*
