#!/usr/bin/env python3
"""
Machine Learning Pricing Optimizer
==================================

Advanced ML-based pricing optimization and prediction system for competitive pricing analysis.
Uses machine learning algorithms to predict optimal pricing strategies and market responses.

Features:
- Price prediction using multiple ML models
- Market response modeling
- Optimal pricing recommendations
- Competitive response prediction
- Price elasticity analysis
- Revenue optimization
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import warnings
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import sqlite3
import json

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

@dataclass
class PricingPrediction:
    """Data structure for pricing predictions"""
    product_id: str
    predicted_price: float
    confidence: float
    model_used: str
    features_used: List[str]
    prediction_date: datetime
    market_conditions: Dict[str, Any]

@dataclass
class OptimizationResult:
    """Data structure for pricing optimization results"""
    product_id: str
    current_price: float
    optimal_price: float
    expected_revenue_change: float
    market_share_impact: float
    competitive_response_probability: float
    recommendation: str
    confidence: float

class MLPricingOptimizer:
    """
    Machine Learning-based pricing optimizer
    """
    
    def __init__(self, db_path: str = "pricing_analysis.db"):
        """Initialize the ML pricing optimizer"""
        self.db_path = db_path
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.feature_importance = {}
        
        # Initialize models
        self._initialize_models()
        
        logger.info("ML Pricing Optimizer initialized successfully")
    
    def _initialize_models(self):
        """Initialize machine learning models"""
        self.models = {
            'price_prediction': {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'linear_regression': LinearRegression(),
                'ridge': Ridge(alpha=1.0),
                'lasso': Lasso(alpha=1.0)
            },
            'market_response': {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
            },
            'competitive_response': {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
            }
        }
        
        # Initialize scalers
        self.scalers = {
            'price_prediction': StandardScaler(),
            'market_response': StandardScaler(),
            'competitive_response': StandardScaler()
        }
        
        # Initialize label encoders
        self.label_encoders = {
            'competitor': LabelEncoder(),
            'product_category': LabelEncoder(),
            'currency': LabelEncoder()
        }
    
    def prepare_training_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare training data for price prediction models"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get historical pricing data
            query = '''
                SELECT 
                    product_id,
                    product_name,
                    competitor,
                    price,
                    currency,
                    date_collected,
                    source
                FROM pricing_data
                WHERE date_collected >= date('now', '-365 days')
                ORDER BY date_collected
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                logger.warning("No historical data available for training")
                return pd.DataFrame(), pd.Series()
            
            # Feature engineering
            df = self._engineer_features(df)
            
            # Prepare features and target
            feature_columns = [
                'competitor_encoded', 'product_category_encoded', 'currency_encoded',
                'days_since_start', 'price_trend_7d', 'price_trend_30d',
                'market_volatility', 'competitor_count', 'price_rank'
            ]
            
            X = df[feature_columns].fillna(0)
            y = df['price']
            
            logger.info(f"Prepared training data: {len(X)} samples, {len(feature_columns)} features")
            return X, y
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return pd.DataFrame(), pd.Series()
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for machine learning models"""
        # Encode categorical variables
        df['competitor_encoded'] = self.label_encoders['competitor'].fit_transform(df['competitor'])
        df['product_category_encoded'] = self.label_encoders['product_category'].fit_transform(df['product_name'])
        df['currency_encoded'] = self.label_encoders['currency'].fit_transform(df['currency'])
        
        # Convert date to datetime
        df['date_collected'] = pd.to_datetime(df['date_collected'])
        
        # Calculate days since start
        start_date = df['date_collected'].min()
        df['days_since_start'] = (df['date_collected'] - start_date).dt.days
        
        # Calculate price trends
        df = df.sort_values(['product_id', 'competitor', 'date_collected'])
        df['price_trend_7d'] = df.groupby(['product_id', 'competitor'])['price'].rolling(7, min_periods=1).mean().reset_index(0, drop=True)
        df['price_trend_30d'] = df.groupby(['product_id', 'competitor'])['price'].rolling(30, min_periods=1).mean().reset_index(0, drop=True)
        
        # Calculate market volatility
        df['market_volatility'] = df.groupby(['product_id', 'date_collected'])['price'].transform('std')
        
        # Calculate competitor count per product
        df['competitor_count'] = df.groupby('product_id')['competitor'].transform('nunique')
        
        # Calculate price rank
        df['price_rank'] = df.groupby(['product_id', 'date_collected'])['price'].rank(ascending=True)
        
        return df
    
    def train_price_prediction_models(self) -> Dict[str, float]:
        """Train price prediction models"""
        try:
            X, y = self.prepare_training_data()
            
            if X.empty or y.empty:
                logger.warning("No training data available")
                return {}
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scalers['price_prediction'].fit_transform(X_train)
            X_test_scaled = self.scalers['price_prediction'].transform(X_test)
            
            model_scores = {}
            
            # Train each model
            for model_name, model in self.models['price_prediction'].items():
                try:
                    # Train model
                    model.fit(X_train_scaled, y_train)
                    
                    # Make predictions
                    y_pred = model.predict(X_test_scaled)
                    
                    # Calculate metrics
                    mse = mean_squared_error(y_test, y_pred)
                    r2 = r2_score(y_test, y_pred)
                    mae = mean_absolute_error(y_test, y_pred)
                    
                    model_scores[model_name] = {
                        'mse': mse,
                        'r2': r2,
                        'mae': mae,
                        'rmse': np.sqrt(mse)
                    }
                    
                    # Store feature importance for tree-based models
                    if hasattr(model, 'feature_importances_'):
                        self.feature_importance[model_name] = dict(zip(X.columns, model.feature_importances_))
                    
                    logger.info(f"Trained {model_name}: R² = {r2:.3f}, RMSE = {np.sqrt(mse):.2f}")
                    
                except Exception as e:
                    logger.error(f"Error training {model_name}: {e}")
                    continue
            
            # Select best model
            best_model = max(model_scores.keys(), key=lambda x: model_scores[x]['r2'])
            logger.info(f"Best model: {best_model} (R² = {model_scores[best_model]['r2']:.3f})")
            
            return model_scores
            
        except Exception as e:
            logger.error(f"Error training price prediction models: {e}")
            return {}
    
    def predict_optimal_price(self, product_id: str, current_price: float, 
                            market_conditions: Dict[str, Any] = None) -> OptimizationResult:
        """Predict optimal price for a product"""
        try:
            if not self.models['price_prediction']:
                logger.warning("No trained models available")
                return None
            
            # Get current market data
            market_data = self._get_current_market_data(product_id)
            
            if market_data.empty:
                logger.warning(f"No market data available for product {product_id}")
                return None
            
            # Prepare features for prediction
            features = self._prepare_prediction_features(product_id, market_data, market_conditions)
            
            if features is None:
                return None
            
            # Scale features
            features_scaled = self.scalers['price_prediction'].transform([features])
            
            # Get predictions from all models
            predictions = {}
            for model_name, model in self.models['price_prediction'].items():
                try:
                    pred = model.predict(features_scaled)[0]
                    predictions[model_name] = pred
                except Exception as e:
                    logger.error(f"Error predicting with {model_name}: {e}")
                    continue
            
            if not predictions:
                return None
            
            # Calculate ensemble prediction
            optimal_price = np.mean(list(predictions.values()))
            
            # Calculate confidence based on prediction variance
            confidence = 1.0 - (np.std(list(predictions.values())) / optimal_price) if optimal_price > 0 else 0.0
            
            # Calculate expected revenue change
            revenue_change = self._calculate_revenue_change(current_price, optimal_price, product_id)
            
            # Calculate market share impact
            market_share_impact = self._calculate_market_share_impact(current_price, optimal_price, product_id)
            
            # Calculate competitive response probability
            competitive_response_prob = self._calculate_competitive_response_probability(
                current_price, optimal_price, product_id
            )
            
            # Generate recommendation
            recommendation = self._generate_pricing_recommendation(
                current_price, optimal_price, revenue_change, market_share_impact, competitive_response_prob
            )
            
            return OptimizationResult(
                product_id=product_id,
                current_price=current_price,
                optimal_price=optimal_price,
                expected_revenue_change=revenue_change,
                market_share_impact=market_share_impact,
                competitive_response_probability=competitive_response_prob,
                recommendation=recommendation,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error predicting optimal price: {e}")
            return None
    
    def _get_current_market_data(self, product_id: str) -> pd.DataFrame:
        """Get current market data for a product"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT 
                    product_id,
                    product_name,
                    competitor,
                    price,
                    currency,
                    date_collected
                FROM pricing_data
                WHERE product_id = ? 
                AND date_collected >= date('now', '-7 days')
                ORDER BY date_collected DESC
            '''
            
            df = pd.read_sql_query(query, conn, params=[product_id])
            conn.close()
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting current market data: {e}")
            return pd.DataFrame()
    
    def _prepare_prediction_features(self, product_id: str, market_data: pd.DataFrame, 
                                   market_conditions: Dict[str, Any] = None) -> Optional[List[float]]:
        """Prepare features for price prediction"""
        try:
            if market_data.empty:
                return None
            
            # Get product info
            product_name = market_data['product_name'].iloc[0]
            currency = market_data['currency'].iloc[0]
            
            # Encode categorical variables
            competitor_encoded = self.label_encoders['competitor'].transform([market_data['competitor'].iloc[0]])[0]
            product_category_encoded = self.label_encoders['product_category'].transform([product_name])[0]
            currency_encoded = self.label_encoders['currency'].transform([currency])[0]
            
            # Calculate market metrics
            competitor_count = market_data['competitor'].nunique()
            price_rank = market_data['price'].rank(ascending=True).iloc[0]
            market_volatility = market_data['price'].std()
            
            # Calculate trends
            price_trend_7d = market_data['price'].mean()
            price_trend_30d = market_data['price'].mean()  # Simplified for current data
            
            # Days since start (simplified)
            days_since_start = 365  # Assume 1 year of data
            
            features = [
                competitor_encoded,
                product_category_encoded,
                currency_encoded,
                days_since_start,
                price_trend_7d,
                price_trend_30d,
                market_volatility,
                competitor_count,
                price_rank
            ]
            
            return features
            
        except Exception as e:
            logger.error(f"Error preparing prediction features: {e}")
            return None
    
    def _calculate_revenue_change(self, current_price: float, optimal_price: float, 
                                product_id: str) -> float:
        """Calculate expected revenue change from price optimization"""
        try:
            # Simplified revenue calculation
            # In practice, you would use historical sales data and price elasticity
            
            price_change_pct = (optimal_price - current_price) / current_price
            
            # Assume price elasticity of -1.5 (typical for software products)
            elasticity = -1.5
            quantity_change_pct = elasticity * price_change_pct
            
            # Calculate revenue change
            revenue_change = (1 + price_change_pct) * (1 + quantity_change_pct) - 1
            
            return revenue_change
            
        except Exception as e:
            logger.error(f"Error calculating revenue change: {e}")
            return 0.0
    
    def _calculate_market_share_impact(self, current_price: float, optimal_price: float, 
                                     product_id: str) -> float:
        """Calculate expected market share impact"""
        try:
            # Simplified market share calculation
            # In practice, you would use competitive analysis and market data
            
            price_change_pct = (optimal_price - current_price) / current_price
            
            # Assume market share sensitivity to price changes
            if price_change_pct < 0:  # Price decrease
                market_share_impact = abs(price_change_pct) * 0.5  # Positive impact
            else:  # Price increase
                market_share_impact = -abs(price_change_pct) * 0.3  # Negative impact
            
            return market_share_impact
            
        except Exception as e:
            logger.error(f"Error calculating market share impact: {e}")
            return 0.0
    
    def _calculate_competitive_response_probability(self, current_price: float, 
                                                  optimal_price: float, product_id: str) -> float:
        """Calculate probability of competitive response"""
        try:
            price_change_pct = abs((optimal_price - current_price) / current_price)
            
            # Higher price changes increase probability of competitive response
            if price_change_pct < 0.05:  # Less than 5% change
                probability = 0.2
            elif price_change_pct < 0.15:  # 5-15% change
                probability = 0.5
            else:  # More than 15% change
                probability = 0.8
            
            return probability
            
        except Exception as e:
            logger.error(f"Error calculating competitive response probability: {e}")
            return 0.5
    
    def _generate_pricing_recommendation(self, current_price: float, optimal_price: float,
                                       revenue_change: float, market_share_impact: float,
                                       competitive_response_prob: float) -> str:
        """Generate pricing recommendation based on analysis"""
        try:
            price_change_pct = (optimal_price - current_price) / current_price
            
            if abs(price_change_pct) < 0.02:  # Less than 2% change
                return "Maintain current pricing strategy - minimal optimization opportunity"
            
            if price_change_pct > 0:  # Price increase
                if revenue_change > 0.1 and competitive_response_prob < 0.5:
                    return f"Recommended price increase to ${optimal_price:.2f} - high revenue potential with low competitive risk"
                elif revenue_change > 0.05:
                    return f"Consider moderate price increase to ${optimal_price:.2f} - positive revenue impact expected"
                else:
                    return "Price increase not recommended - limited revenue benefit"
            
            else:  # Price decrease
                if market_share_impact > 0.1 and competitive_response_prob < 0.6:
                    return f"Recommended price decrease to ${optimal_price:.2f} - significant market share opportunity"
                elif market_share_impact > 0.05:
                    return f"Consider price decrease to ${optimal_price:.2f} - moderate market share gain expected"
                else:
                    return "Price decrease not recommended - limited market share benefit"
            
        except Exception as e:
            logger.error(f"Error generating pricing recommendation: {e}")
            return "Unable to generate recommendation - insufficient data"
    
    def analyze_price_elasticity(self, product_id: str) -> Dict[str, Any]:
        """Analyze price elasticity for a product"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get historical data for elasticity analysis
            query = '''
                SELECT 
                    price,
                    date_collected,
                    competitor
                FROM pricing_data
                WHERE product_id = ?
                AND date_collected >= date('now', '-90 days')
                ORDER BY date_collected
            '''
            
            df = pd.read_sql_query(query, conn, params=[product_id])
            conn.close()
            
            if df.empty or len(df) < 10:
                return {'error': 'Insufficient data for elasticity analysis'}
            
            # Calculate price elasticity
            # This is a simplified calculation - in practice, you'd need sales volume data
            
            price_changes = df['price'].pct_change().dropna()
            market_volatility = price_changes.std()
            
            # Estimate elasticity based on price volatility and market response
            # Higher volatility suggests lower elasticity (less price-sensitive market)
            estimated_elasticity = -1.0 / (1.0 + market_volatility * 10)
            
            return {
                'product_id': product_id,
                'estimated_elasticity': estimated_elasticity,
                'price_volatility': market_volatility,
                'data_points': len(df),
                'analysis_period': '90 days',
                'elasticity_interpretation': self._interpret_elasticity(estimated_elasticity)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing price elasticity: {e}")
            return {'error': str(e)}
    
    def _interpret_elasticity(self, elasticity: float) -> str:
        """Interpret price elasticity value"""
        if elasticity < -2.0:
            return "Highly elastic - very sensitive to price changes"
        elif elasticity < -1.0:
            return "Elastic - sensitive to price changes"
        elif elasticity < -0.5:
            return "Moderately elastic - somewhat sensitive to price changes"
        else:
            return "Inelastic - not very sensitive to price changes"
    
    def save_models(self, filepath: str = "ml_pricing_models.pkl"):
        """Save trained models to file"""
        try:
            model_data = {
                'models': self.models,
                'scalers': self.scalers,
                'label_encoders': self.label_encoders,
                'feature_importance': self.feature_importance
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"Models saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def load_models(self, filepath: str = "ml_pricing_models.pkl"):
        """Load trained models from file"""
        try:
            model_data = joblib.load(filepath)
            
            self.models = model_data['models']
            self.scalers = model_data['scalers']
            self.label_encoders = model_data['label_encoders']
            self.feature_importance = model_data['feature_importance']
            
            logger.info(f"Models loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get model performance metrics"""
        try:
            X, y = self.prepare_training_data()
            
            if X.empty or y.empty:
                return {'error': 'No training data available'}
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scalers['price_prediction'].fit_transform(X_train)
            X_test_scaled = self.scalers['price_prediction'].transform(X_test)
            
            performance = {}
            
            for model_name, model in self.models['price_prediction'].items():
                try:
                    # Cross-validation scores
                    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
                    
                    performance[model_name] = {
                        'cv_mean': cv_scores.mean(),
                        'cv_std': cv_scores.std(),
                        'cv_scores': cv_scores.tolist()
                    }
                    
                except Exception as e:
                    logger.error(f"Error evaluating {model_name}: {e}")
                    continue
            
            return performance
            
        except Exception as e:
            logger.error(f"Error getting model performance: {e}")
            return {'error': str(e)}

def main():
    """Main function to demonstrate ML pricing optimizer"""
    # Initialize optimizer
    optimizer = MLPricingOptimizer()
    
    # Train models
    print("Training price prediction models...")
    scores = optimizer.train_price_prediction_models()
    
    if scores:
        print("\nModel Performance:")
        for model_name, metrics in scores.items():
            print(f"{model_name}: R² = {metrics['r2']:.3f}, RMSE = {metrics['rmse']:.2f}")
    
    # Example: Predict optimal price for a product
    product_id = "product_001"
    current_price = 299.99
    
    print(f"\nPredicting optimal price for {product_id}...")
    result = optimizer.predict_optimal_price(product_id, current_price)
    
    if result:
        print(f"Current Price: ${result.current_price:.2f}")
        print(f"Optimal Price: ${result.optimal_price:.2f}")
        print(f"Expected Revenue Change: {result.expected_revenue_change:.1%}")
        print(f"Market Share Impact: {result.market_share_impact:.1%}")
        print(f"Competitive Response Probability: {result.competitive_response_probability:.1%}")
        print(f"Recommendation: {result.recommendation}")
        print(f"Confidence: {result.confidence:.1%}")
    
    # Analyze price elasticity
    print(f"\nAnalyzing price elasticity for {product_id}...")
    elasticity_analysis = optimizer.analyze_price_elasticity(product_id)
    
    if 'error' not in elasticity_analysis:
        print(f"Estimated Elasticity: {elasticity_analysis['estimated_elasticity']:.2f}")
        print(f"Price Volatility: {elasticity_analysis['price_volatility']:.3f}")
        print(f"Interpretation: {elasticity_analysis['elasticity_interpretation']}")
    
    # Save models
    optimizer.save_models()

if __name__ == "__main__":
    main()






