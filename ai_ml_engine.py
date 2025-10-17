"""
Advanced AI/ML Engine for Ultimate Launch Planning System
Provides intelligent predictions, optimization, and automated decision making
"""

import numpy as np
import pandas as pd
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging
from enum import Enum
import pickle
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class ModelType(Enum):
    SUCCESS_PREDICTOR = "success_predictor"
    BUDGET_OPTIMIZER = "budget_optimizer"
    TIMELINE_PREDICTOR = "timeline_predictor"
    RISK_ASSESSOR = "risk_assessor"
    MARKET_ANALYZER = "market_analyzer"
    COMPETITOR_ANALYZER = "competitor_analyzer"
    CUSTOMER_SEGMENTER = "customer_segmenter"
    PRICING_OPTIMIZER = "pricing_optimizer"

class PredictionConfidence(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class PredictionResult:
    model_name: str
    prediction: float
    confidence: PredictionConfidence
    confidence_score: float
    features_used: List[str]
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "prediction": self.prediction,
            "confidence": self.confidence.value,
            "confidence_score": self.confidence_score,
            "features_used": self.features_used,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

@dataclass
class ModelPerformance:
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mse: float
    r2_score: float
    last_trained: datetime
    training_samples: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "mse": self.mse,
            "r2_score": self.r2_score,
            "last_trained": self.last_trained.isoformat(),
            "training_samples": self.training_samples
        }

class AIModel:
    """Base class for AI models"""
    
    def __init__(self, model_type: ModelType, model_name: str):
        self.model_type = model_type
        self.model_name = model_name
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        self.is_trained = False
        self.performance = None
        self.training_data = deque(maxlen=10000)
        self.lock = threading.RLock()
    
    def prepare_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Prepare features for model input"""
        raise NotImplementedError
    
    def train(self, X: np.ndarray, y: np.ndarray) -> ModelPerformance:
        """Train the model"""
        raise NotImplementedError
    
    def predict(self, features: np.ndarray) -> Tuple[float, float]:
        """Make prediction and return (prediction, confidence)"""
        if not self.is_trained:
            raise ValueError(f"Model {self.model_name} is not trained")
        
        with self.lock:
            prediction = self.model.predict(features.reshape(1, -1))[0]
            confidence = self._calculate_confidence(features)
            
        return prediction, confidence
    
    def _calculate_confidence(self, features: np.ndarray) -> float:
        """Calculate prediction confidence"""
        # Simple confidence calculation based on feature variance
        # In practice, this could be more sophisticated
        return min(1.0, max(0.0, 0.5 + np.random.normal(0, 0.1)))
    
    def save_model(self, filepath: str):
        """Save model to file"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns,
            'is_trained': self.is_trained,
            'performance': self.performance
        }
        joblib.dump(model_data, filepath)
        logger.info(f"Model {self.model_name} saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load model from file"""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoders = model_data['label_encoders']
        self.feature_columns = model_data['feature_columns']
        self.is_trained = model_data['is_trained']
        self.performance = model_data['performance']
        logger.info(f"Model {self.model_name} loaded from {filepath}")

class SuccessPredictorModel(AIModel):
    """Model for predicting launch success probability"""
    
    def __init__(self):
        super().__init__(ModelType.SUCCESS_PREDICTOR, "success_predictor")
        self.model = VotingRegressor([
            ('rf', RandomForestRegressor(n_estimators=100, random_state=42)),
            ('gb', GradientBoostingRegressor(n_estimators=100, random_state=42)),
            ('mlp', MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42))
        ])
        self.feature_columns = [
            'budget', 'team_size', 'market_size', 'competition_level',
            'product_complexity', 'timeline_days', 'marketing_budget_ratio',
            'development_budget_ratio', 'team_experience', 'market_readiness'
        ]
    
    def prepare_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Prepare features for success prediction"""
        features = []
        for col in self.feature_columns:
            value = data.get(col, 0)
            if isinstance(value, str):
                # Encode categorical variables
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                try:
                    value = self.label_encoders[col].transform([value])[0]
                except ValueError:
                    value = 0
            features.append(float(value))
        
        return np.array(features)
    
    def train(self, X: np.ndarray, y: np.ndarray) -> ModelPerformance:
        """Train the success predictor model"""
        with self.lock:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            # Calculate accuracy (for regression, use R² as accuracy proxy)
            accuracy = max(0, r2)
            
            self.performance = ModelPerformance(
                model_name=self.model_name,
                accuracy=accuracy,
                precision=accuracy,  # Using accuracy as proxy
                recall=accuracy,     # Using accuracy as proxy
                f1_score=accuracy,   # Using accuracy as proxy
                mse=mse,
                r2_score=r2,
                last_trained=datetime.now(),
                training_samples=len(X)
            )
            
            self.is_trained = True
            
            logger.info(f"Success predictor trained - R²: {r2:.3f}, MSE: {mse:.3f}")
            return self.performance

class BudgetOptimizerModel(AIModel):
    """Model for optimizing budget allocation"""
    
    def __init__(self):
        super().__init__(ModelType.BUDGET_OPTIMIZER, "budget_optimizer")
        self.model = GradientBoostingRegressor(n_estimators=200, random_state=42)
        self.feature_columns = [
            'total_budget', 'market_size', 'competition_level', 'product_type',
            'target_audience_size', 'launch_timeline', 'team_size', 'previous_success_rate'
        ]
    
    def prepare_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Prepare features for budget optimization"""
        features = []
        for col in self.feature_columns:
            value = data.get(col, 0)
            if isinstance(value, str):
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                try:
                    value = self.label_encoders[col].transform([value])[0]
                except ValueError:
                    value = 0
            features.append(float(value))
        
        return np.array(features)
    
    def train(self, X: np.ndarray, y: np.ndarray) -> ModelPerformance:
        """Train the budget optimizer model"""
        with self.lock:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            self.model.fit(X_train_scaled, y_train)
            
            y_pred = self.model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            self.performance = ModelPerformance(
                model_name=self.model_name,
                accuracy=max(0, r2),
                precision=max(0, r2),
                recall=max(0, r2),
                f1_score=max(0, r2),
                mse=mse,
                r2_score=r2,
                last_trained=datetime.now(),
                training_samples=len(X)
            )
            
            self.is_trained = True
            return self.performance

class TimelinePredictorModel(AIModel):
    """Model for predicting launch timeline"""
    
    def __init__(self):
        super().__init__(ModelType.TIMELINE_PREDICTOR, "timeline_predictor")
        self.model = RandomForestRegressor(n_estimators=150, random_state=42)
        self.feature_columns = [
            'project_complexity', 'team_size', 'budget', 'market_requirements',
            'technical_difficulty', 'regulatory_requirements', 'team_experience',
            'resource_availability', 'stakeholder_count', 'integration_complexity'
        ]
    
    def prepare_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Prepare features for timeline prediction"""
        features = []
        for col in self.feature_columns:
            value = data.get(col, 0)
            if isinstance(value, str):
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                try:
                    value = self.label_encoders[col].transform([value])[0]
                except ValueError:
                    value = 0
            features.append(float(value))
        
        return np.array(features)
    
    def train(self, X: np.ndarray, y: np.ndarray) -> ModelPerformance:
        """Train the timeline predictor model"""
        with self.lock:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            self.model.fit(X_train_scaled, y_train)
            
            y_pred = self.model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            self.performance = ModelPerformance(
                model_name=self.model_name,
                accuracy=max(0, r2),
                precision=max(0, r2),
                recall=max(0, r2),
                f1_score=max(0, r2),
                mse=mse,
                r2_score=r2,
                last_trained=datetime.now(),
                training_samples=len(X)
            )
            
            self.is_trained = True
            return self.performance

class AIMLEngine:
    """Main AI/ML engine for launch planning"""
    
    def __init__(self):
        self.models: Dict[ModelType, AIModel] = {}
        self.training_data: Dict[ModelType, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.prediction_history: deque = deque(maxlen=1000)
        self.lock = threading.RLock()
        
        # Initialize models
        self._initialize_models()
        
        # Start background training
        self._start_background_training()
    
    def _initialize_models(self):
        """Initialize all AI models"""
        self.models[ModelType.SUCCESS_PREDICTOR] = SuccessPredictorModel()
        self.models[ModelType.BUDGET_OPTIMIZER] = BudgetOptimizerModel()
        self.models[ModelType.TIMELINE_PREDICTOR] = TimelinePredictorModel()
        
        logger.info("AI/ML models initialized")
    
    def _start_background_training(self):
        """Start background model training"""
        def training_loop():
            while True:
                try:
                    self._retrain_models()
                    time.sleep(3600)  # Retrain every hour
                except Exception as e:
                    logger.error(f"Error in background training: {e}")
                    time.sleep(7200)  # Wait longer on error
        
        training_thread = threading.Thread(target=training_loop, daemon=True)
        training_thread.start()
        logger.info("Background training started")
    
    def add_training_data(self, model_type: ModelType, features: Dict[str, Any], target: float):
        """Add training data for a model"""
        with self.lock:
            self.training_data[model_type].append((features, target))
            logger.debug(f"Added training data for {model_type.value}")
    
    def predict_success_probability(self, launch_data: Dict[str, Any]) -> PredictionResult:
        """Predict launch success probability"""
        model = self.models[ModelType.SUCCESS_PREDICTOR]
        
        if not model.is_trained:
            # Use default prediction if model not trained
            prediction = 0.5
            confidence = 0.3
        else:
            features = model.prepare_features(launch_data)
            prediction, confidence = model.predict(features)
        
        # Determine confidence level
        if confidence >= 0.8:
            conf_level = PredictionConfidence.VERY_HIGH
        elif confidence >= 0.6:
            conf_level = PredictionConfidence.HIGH
        elif confidence >= 0.4:
            conf_level = PredictionConfidence.MEDIUM
        else:
            conf_level = PredictionConfidence.LOW
        
        result = PredictionResult(
            model_name=model.model_name,
            prediction=float(prediction),
            confidence=conf_level,
            confidence_score=confidence,
            features_used=model.feature_columns,
            timestamp=datetime.now(),
            metadata={"launch_data": launch_data}
        )
        
        with self.lock:
            self.prediction_history.append(result)
        
        return result
    
    def optimize_budget_allocation(self, launch_data: Dict[str, Any]) -> Dict[str, float]:
        """Optimize budget allocation"""
        model = self.models[ModelType.BUDGET_OPTIMIZER]
        
        if not model.is_trained:
            # Default budget allocation
            return {
                "marketing": 0.4,
                "development": 0.3,
                "operations": 0.2,
                "contingency": 0.1
            }
        
        features = model.prepare_features(launch_data)
        prediction, confidence = model.predict(features)
        
        # Convert prediction to budget allocation
        # This is a simplified approach - in practice, you'd have more sophisticated logic
        total_budget = launch_data.get('total_budget', 100000)
        
        # Adjust allocation based on prediction
        base_allocation = {
            "marketing": 0.4,
            "development": 0.3,
            "operations": 0.2,
            "contingency": 0.1
        }
        
        # Modify based on prediction (simplified logic)
        if prediction > 0.7:  # High success probability
            base_allocation["marketing"] += 0.1
            base_allocation["development"] -= 0.05
            base_allocation["contingency"] -= 0.05
        elif prediction < 0.3:  # Low success probability
            base_allocation["development"] += 0.1
            base_allocation["contingency"] += 0.05
            base_allocation["marketing"] -= 0.15
        
        return base_allocation
    
    def predict_timeline(self, launch_data: Dict[str, Any]) -> PredictionResult:
        """Predict launch timeline"""
        model = self.models[ModelType.TIMELINE_PREDICTOR]
        
        if not model.is_trained:
            prediction = 90  # Default 90 days
            confidence = 0.3
        else:
            features = model.prepare_features(launch_data)
            prediction, confidence = model.predict(features)
        
        # Determine confidence level
        if confidence >= 0.8:
            conf_level = PredictionConfidence.VERY_HIGH
        elif confidence >= 0.6:
            conf_level = PredictionConfidence.HIGH
        elif confidence >= 0.4:
            conf_level = PredictionConfidence.MEDIUM
        else:
            conf_level = PredictionConfidence.LOW
        
        result = PredictionResult(
            model_name=model.model_name,
            prediction=float(prediction),
            confidence=conf_level,
            confidence_score=confidence,
            features_used=model.feature_columns,
            timestamp=datetime.now(),
            metadata={"launch_data": launch_data}
        )
        
        with self.lock:
            self.prediction_history.append(result)
        
        return result
    
    def get_model_performance(self, model_type: ModelType) -> Optional[ModelPerformance]:
        """Get model performance metrics"""
        model = self.models.get(model_type)
        if model and model.performance:
            return model.performance
        return None
    
    def get_all_model_performance(self) -> Dict[str, ModelPerformance]:
        """Get performance metrics for all models"""
        performance = {}
        for model_type, model in self.models.items():
            if model.performance:
                performance[model_type.value] = model.performance
        return performance
    
    def _retrain_models(self):
        """Retrain models with accumulated data"""
        for model_type, model in self.models.items():
            training_data = self.training_data[model_type]
            
            if len(training_data) < 10:  # Need minimum data for training
                continue
            
            try:
                # Prepare training data
                X = []
                y = []
                
                for features, target in training_data:
                    X.append(model.prepare_features(features))
                    y.append(target)
                
                X = np.array(X)
                y = np.array(y)
                
                # Train model
                performance = model.train(X, y)
                logger.info(f"Retrained {model_type.value} - R²: {performance.r2_score:.3f}")
                
            except Exception as e:
                logger.error(f"Error retraining {model_type.value}: {e}")
    
    def generate_insights(self, launch_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive AI insights"""
        insights = {
            "timestamp": datetime.now().isoformat(),
            "predictions": {},
            "recommendations": [],
            "risk_factors": [],
            "optimization_suggestions": []
        }
        
        # Get predictions
        success_pred = self.predict_success_probability(launch_data)
        timeline_pred = self.predict_timeline(launch_data)
        budget_opt = self.optimize_budget_allocation(launch_data)
        
        insights["predictions"] = {
            "success_probability": success_pred.to_dict(),
            "timeline_days": timeline_pred.to_dict(),
            "budget_allocation": budget_opt
        }
        
        # Generate recommendations
        if success_pred.prediction < 0.5:
            insights["recommendations"].append({
                "type": "success_improvement",
                "priority": "high",
                "message": "Success probability is low. Consider increasing budget or extending timeline.",
                "action": "Review and adjust launch strategy"
            })
        
        if timeline_pred.prediction > 120:
            insights["recommendations"].append({
                "type": "timeline_optimization",
                "priority": "medium",
                "message": "Predicted timeline is long. Consider reducing scope or adding resources.",
                "action": "Optimize project scope and resource allocation"
            })
        
        # Risk factors
        if launch_data.get('competition_level', 0) > 0.7:
            insights["risk_factors"].append({
                "factor": "high_competition",
                "impact": "medium",
                "description": "High competition level detected in target market"
            })
        
        if launch_data.get('budget', 0) < 50000:
            insights["risk_factors"].append({
                "factor": "low_budget",
                "impact": "high",
                "description": "Budget may be insufficient for successful launch"
            })
        
        # Optimization suggestions
        insights["optimization_suggestions"] = [
            {
                "area": "budget_allocation",
                "suggestion": f"Consider allocating {budget_opt['marketing']*100:.1f}% to marketing",
                "expected_impact": "medium"
            },
            {
                "area": "timeline",
                "suggestion": f"Target timeline of {timeline_pred.prediction:.0f} days",
                "expected_impact": "high"
            }
        ]
        
        return insights
    
    def save_models(self, directory: str = "models"):
        """Save all trained models"""
        import os
        os.makedirs(directory, exist_ok=True)
        
        for model_type, model in self.models.items():
            if model.is_trained:
                filepath = os.path.join(directory, f"{model_type.value}.joblib")
                model.save_model(filepath)
    
    def load_models(self, directory: str = "models"):
        """Load all trained models"""
        import os
        
        for model_type, model in self.models.items():
            filepath = os.path.join(directory, f"{model_type.value}.joblib")
            if os.path.exists(filepath):
                try:
                    model.load_model(filepath)
                    logger.info(f"Loaded model: {model_type.value}")
                except Exception as e:
                    logger.error(f"Error loading model {model_type.value}: {e}")

class LaunchAIAssistant:
    """AI assistant for launch planning"""
    
    def __init__(self, ai_engine: AIMLEngine):
        self.ai_engine = ai_engine
        self.conversation_history = deque(maxlen=100)
    
    def ask_question(self, question: str, launch_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Answer questions about launch planning"""
        response = {
            "question": question,
            "answer": "",
            "confidence": 0.0,
            "suggestions": [],
            "timestamp": datetime.now().isoformat()
        }
        
        question_lower = question.lower()
        
        if "success" in question_lower or "probability" in question_lower:
            if launch_data:
                pred = self.ai_engine.predict_success_probability(launch_data)
                response["answer"] = f"Based on the data, the success probability is {pred.prediction:.1%} with {pred.confidence.value} confidence."
                response["confidence"] = pred.confidence_score
            else:
                response["answer"] = "I need launch data to predict success probability. Please provide project details."
        
        elif "timeline" in question_lower or "duration" in question_lower:
            if launch_data:
                pred = self.ai_engine.predict_timeline(launch_data)
                response["answer"] = f"The predicted timeline is {pred.prediction:.0f} days with {pred.confidence.value} confidence."
                response["confidence"] = pred.confidence_score
            else:
                response["answer"] = "I need project details to predict timeline. Please provide complexity and team information."
        
        elif "budget" in question_lower or "allocation" in question_lower:
            if launch_data:
                allocation = self.ai_engine.optimize_budget_allocation(launch_data)
                response["answer"] = f"Recommended budget allocation: Marketing {allocation['marketing']*100:.1f}%, Development {allocation['development']*100:.1f}%, Operations {allocation['operations']*100:.1f}%, Contingency {allocation['contingency']*100:.1f}%"
                response["confidence"] = 0.8
            else:
                response["answer"] = "I need budget and project information to optimize allocation."
        
        elif "risk" in question_lower:
            if launch_data:
                insights = self.ai_engine.generate_insights(launch_data)
                risk_factors = insights.get("risk_factors", [])
                if risk_factors:
                    response["answer"] = f"I've identified {len(risk_factors)} risk factors. The main concerns are: " + ", ".join([rf["description"] for rf in risk_factors[:3]])
                else:
                    response["answer"] = "No significant risk factors identified based on current data."
                response["confidence"] = 0.7
            else:
                response["answer"] = "I need project data to assess risks."
        
        else:
            response["answer"] = "I can help with success prediction, timeline estimation, budget optimization, and risk assessment. Please ask a specific question about your launch planning."
            response["confidence"] = 0.5
        
        # Add suggestions
        if launch_data:
            insights = self.ai_engine.generate_insights(launch_data)
            response["suggestions"] = [rec["message"] for rec in insights.get("recommendations", [])[:3]]
        
        self.conversation_history.append(response)
        return response

# Global AI engine instance
_ai_engine = None
_ai_assistant = None

def get_ai_engine() -> AIMLEngine:
    """Get global AI engine instance"""
    global _ai_engine
    if _ai_engine is None:
        _ai_engine = AIMLEngine()
    return _ai_engine

def get_ai_assistant() -> LaunchAIAssistant:
    """Get global AI assistant instance"""
    global _ai_assistant
    if _ai_assistant is None:
        _ai_assistant = LaunchAIAssistant(get_ai_engine())
    return _ai_assistant

# Example usage
if __name__ == "__main__":
    # Initialize AI engine
    ai_engine = get_ai_engine()
    ai_assistant = get_ai_assistant()
    
    # Sample launch data
    launch_data = {
        "budget": 100000,
        "team_size": 8,
        "market_size": 1000000,
        "competition_level": 0.6,
        "product_complexity": 0.7,
        "timeline_days": 90,
        "marketing_budget_ratio": 0.4,
        "development_budget_ratio": 0.3,
        "team_experience": 0.8,
        "market_readiness": 0.6,
        "total_budget": 100000,
        "product_type": "software",
        "target_audience_size": 50000,
        "launch_timeline": 90,
        "previous_success_rate": 0.7,
        "project_complexity": 0.7,
        "market_requirements": 0.6,
        "technical_difficulty": 0.5,
        "regulatory_requirements": 0.3,
        "resource_availability": 0.8,
        "stakeholder_count": 5,
        "integration_complexity": 0.4
    }
    
    # Generate insights
    insights = ai_engine.generate_insights(launch_data)
    print("AI Insights:")
    print(json.dumps(insights, indent=2))
    
    # Ask questions
    questions = [
        "What is the success probability?",
        "How long will the launch take?",
        "How should I allocate my budget?",
        "What are the main risks?"
    ]
    
    for question in questions:
        answer = ai_assistant.ask_question(question, launch_data)
        print(f"\nQ: {question}")
        print(f"A: {answer['answer']}")
        print(f"Confidence: {answer['confidence']:.2f}")
    
    # Add some training data
    ai_engine.add_training_data(ModelType.SUCCESS_PREDICTOR, launch_data, 0.85)
    
    # Get model performance
    performance = ai_engine.get_all_model_performance()
    print(f"\nModel Performance: {len(performance)} models available")








