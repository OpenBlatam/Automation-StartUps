"""
Pipeline de Machine Learning Avanzado con AutoML
Sistema de ML automatizado con selección de modelos, feature engineering y optimización
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import joblib
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.feature_selection import SelectKBest, RFE, SelectFromModel
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import optuna
from optuna.samplers import TPESampler
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor

class ModelType(Enum):
    LINEAR = "linear"
    TREE = "tree"
    ENSEMBLE = "ensemble"
    NEURAL = "neural"
    SVM = "svm"
    BOOSTING = "boosting"

class FeatureEngineeringType(Enum):
    POLYNOMIAL = "polynomial"
    INTERACTION = "interaction"
    LOGARITHMIC = "logarithmic"
    BINNING = "binning"
    ENCODING = "encoding"
    SCALING = "scaling"

@dataclass
class MLModel:
    name: str
    model_type: ModelType
    model: Any
    hyperparameters: Dict[str, Any]
    performance_metrics: Dict[str, float]
    feature_importance: Optional[Dict[str, float]] = None
    training_time: float = 0.0
    prediction_time: float = 0.0

@dataclass
class FeatureEngineeringStep:
    name: str
    step_type: FeatureEngineeringType
    parameters: Dict[str, Any]
    transformer: Any
    feature_names: List[str]

class AdvancedMLPipeline:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.feature_engineering_steps = []
        self.preprocessing_pipeline = None
        self.best_model = None
        self.performance_history = []
        self.auto_ml_config = {
            "max_trials": 100,
            "timeout": 3600,
            "cv_folds": 5,
            "scoring": "neg_mean_squared_error",
            "n_jobs": -1
        }
        
    async def create_ml_pipeline(self, data: pd.DataFrame, target_column: str, 
                               task_type: str = "regression") -> Dict[str, Any]:
        """Crear pipeline de ML completo"""
        try:
            start_time = datetime.now()
            
            # Preparar datos
            X, y = await self._prepare_data(data, target_column)
            
            # Feature Engineering automático
            X_engineered = await self._perform_automatic_feature_engineering(X, y)
            
            # División de datos
            X_train, X_test, y_train, y_test = train_test_split(
                X_engineered, y, test_size=0.2, random_state=42
            )
            
            # Preprocesamiento
            X_train_scaled, X_test_scaled = await self._preprocess_data(X_train, X_test)
            
            # AutoML - Selección y optimización de modelos
            best_models = await self._automated_model_selection(
                X_train_scaled, y_train, X_test_scaled, y_test
            )
            
            # Ensemble de mejores modelos
            ensemble_model = await self._create_ensemble_model(best_models, X_train_scaled, y_train)
            
            # Evaluación final
            final_evaluation = await self._evaluate_final_model(
                ensemble_model, X_test_scaled, y_test
            )
            
            # Generar reporte
            pipeline_report = await self._generate_pipeline_report(
                best_models, ensemble_model, final_evaluation, start_time
            )
            
            return pipeline_report
            
        except Exception as e:
            self.logger.error(f"Error creating ML pipeline: {e}")
            raise
    
    async def _prepare_data(self, data: pd.DataFrame, target_column: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Preparar datos para ML"""
        try:
            # Separar características y objetivo
            X = data.drop(columns=[target_column])
            y = data[target_column]
            
            # Limpiar datos
            X = X.select_dtypes(include=[np.number])
            X = X.fillna(X.mean())
            
            # Eliminar características con varianza cero
            X = X.loc[:, X.var() > 0]
            
            return X, y
            
        except Exception as e:
            self.logger.error(f"Error preparing data: {e}")
            raise
    
    async def _perform_automatic_feature_engineering(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """Realizar feature engineering automático"""
        try:
            X_engineered = X.copy()
            
            # 1. Características polinomiales
            polynomial_features = await self._create_polynomial_features(X_engineered)
            if polynomial_features is not None:
                X_engineered = pd.concat([X_engineered, polynomial_features], axis=1)
            
            # 2. Características de interacción
            interaction_features = await self._create_interaction_features(X_engineered)
            if interaction_features is not None:
                X_engineered = pd.concat([X_engineered, interaction_features], axis=1)
            
            # 3. Características logarítmicas
            log_features = await self._create_logarithmic_features(X_engineered)
            if log_features is not None:
                X_engineered = pd.concat([X_engineered, log_features], axis=1)
            
            # 4. Binning de características numéricas
            binned_features = await self._create_binned_features(X_engineered)
            if binned_features is not None:
                X_engineered = pd.concat([X_engineered, binned_features], axis=1)
            
            # 5. Selección de características
            X_engineered = await self._select_best_features(X_engineered, y)
            
            return X_engineered
            
        except Exception as e:
            self.logger.error(f"Error in feature engineering: {e}")
            raise
    
    async def _create_polynomial_features(self, X: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Crear características polinomiales"""
        try:
            from sklearn.preprocessing import PolynomialFeatures
            
            # Seleccionar características numéricas
            numeric_cols = X.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) < 2:
                return None
            
            # Crear características polinomiales de grado 2
            poly = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
            poly_features = poly.fit_transform(X[numeric_cols])
            
            # Crear nombres de características
            feature_names = poly.get_feature_names_out(numeric_cols)
            
            # Crear DataFrame
            poly_df = pd.DataFrame(poly_features, columns=feature_names, index=X.index)
            
            # Filtrar características con varianza > 0
            poly_df = poly_df.loc[:, poly_df.var() > 0]
            
            return poly_df
            
        except Exception as e:
            self.logger.error(f"Error creating polynomial features: {e}")
            return None
    
    async def _create_interaction_features(self, X: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Crear características de interacción"""
        try:
            numeric_cols = X.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) < 2:
                return None
            
            interaction_features = []
            feature_names = []
            
            # Crear interacciones entre las 5 características más importantes
            for i in range(min(5, len(numeric_cols))):
                for j in range(i + 1, min(5, len(numeric_cols))):
                    col1, col2 = numeric_cols[i], numeric_cols[j]
                    interaction = X[col1] * X[col2]
                    interaction_features.append(interaction)
                    feature_names.append(f"{col1}_x_{col2}")
            
            if interaction_features:
                interaction_df = pd.DataFrame(
                    np.column_stack(interaction_features),
                    columns=feature_names,
                    index=X.index
                )
                return interaction_df
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating interaction features: {e}")
            return None
    
    async def _create_logarithmic_features(self, X: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Crear características logarítmicas"""
        try:
            numeric_cols = X.select_dtypes(include=[np.number]).columns
            log_features = []
            feature_names = []
            
            for col in numeric_cols:
                # Solo para valores positivos
                if (X[col] > 0).all():
                    log_feature = np.log1p(X[col])  # log(1 + x)
                    log_features.append(log_feature)
                    feature_names.append(f"log_{col}")
            
            if log_features:
                log_df = pd.DataFrame(
                    np.column_stack(log_features),
                    columns=feature_names,
                    index=X.index
                )
                return log_df
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating logarithmic features: {e}")
            return None
    
    async def _create_binned_features(self, X: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Crear características binning"""
        try:
            from sklearn.preprocessing import KBinsDiscretizer
            
            numeric_cols = X.select_dtypes(include=[np.number]).columns
            binned_features = []
            feature_names = []
            
            for col in numeric_cols:
                # Solo para características con suficientes valores únicos
                if X[col].nunique() > 10:
                    discretizer = KBinsDiscretizer(n_bins=5, encode='ordinal', strategy='quantile')
                    binned_feature = discretizer.fit_transform(X[[col]])
                    binned_features.append(binned_feature.flatten())
                    feature_names.append(f"binned_{col}")
            
            if binned_features:
                binned_df = pd.DataFrame(
                    np.column_stack(binned_features),
                    columns=feature_names,
                    index=X.index
                )
                return binned_df
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating binned features: {e}")
            return None
    
    async def _select_best_features(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """Seleccionar mejores características"""
        try:
            # Usar SelectKBest con f_regression
            selector = SelectKBest(k=min(50, X.shape[1]))
            X_selected = selector.fit_transform(X, y)
            
            # Obtener nombres de características seleccionadas
            selected_features = X.columns[selector.get_support()]
            
            return pd.DataFrame(X_selected, columns=selected_features, index=X.index)
            
        except Exception as e:
            self.logger.error(f"Error selecting best features: {e}")
            return X
    
    async def _preprocess_data(self, X_train: pd.DataFrame, X_test: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocesar datos"""
        try:
            # Escalado robusto
            scaler = RobustScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            return X_train_scaled, X_test_scaled
            
        except Exception as e:
            self.logger.error(f"Error preprocessing data: {e}")
            raise
    
    async def _automated_model_selection(self, X_train: np.ndarray, y_train: pd.Series,
                                       X_test: np.ndarray, y_test: pd.Series) -> List[MLModel]:
        """Selección automática de modelos con AutoML"""
        try:
            models_to_test = [
                ("Linear Regression", LinearRegression(), {}),
                ("Ridge", Ridge(), {"alpha": [0.1, 1.0, 10.0]}),
                ("Lasso", Lasso(), {"alpha": [0.1, 1.0, 10.0]}),
                ("ElasticNet", ElasticNet(), {"alpha": [0.1, 1.0, 10.0], "l1_ratio": [0.1, 0.5, 0.9]}),
                ("Random Forest", RandomForestRegressor(random_state=42), 
                 {"n_estimators": [100, 200], "max_depth": [10, 20, None]}),
                ("Gradient Boosting", GradientBoostingRegressor(random_state=42),
                 {"n_estimators": [100, 200], "learning_rate": [0.1, 0.2]}),
                ("XGBoost", xgb.XGBRegressor(random_state=42),
                 {"n_estimators": [100, 200], "learning_rate": [0.1, 0.2]}),
                ("LightGBM", lgb.LGBMRegressor(random_state=42),
                 {"n_estimators": [100, 200], "learning_rate": [0.1, 0.2]}),
                ("CatBoost", CatBoostRegressor(random_state=42, verbose=False),
                 {"iterations": [100, 200], "learning_rate": [0.1, 0.2]}),
                ("SVR", SVR(), {"C": [0.1, 1.0, 10.0], "gamma": ["scale", "auto"]}),
                ("MLP", MLPRegressor(random_state=42, max_iter=1000),
                 {"hidden_layer_sizes": [(100,), (100, 50)], "alpha": [0.001, 0.01]})
            ]
            
            best_models = []
            
            for name, model, param_grid in models_to_test:
                try:
                    start_time = datetime.now()
                    
                    # Optimización de hiperparámetros
                    if param_grid:
                        grid_search = GridSearchCV(
                            model, param_grid, cv=5, scoring='neg_mean_squared_error',
                            n_jobs=-1, verbose=0
                        )
                        grid_search.fit(X_train, y_train)
                        best_model = grid_search.best_estimator_
                        best_params = grid_search.best_params_
                    else:
                        best_model = model
                        best_model.fit(X_train, y_train)
                        best_params = {}
                    
                    # Evaluación
                    y_pred = best_model.predict(X_test)
                    mse = mean_squared_error(y_test, y_pred)
                    mae = mean_absolute_error(y_test, y_pred)
                    r2 = r2_score(y_test, y_pred)
                    
                    # Feature importance si está disponible
                    feature_importance = None
                    if hasattr(best_model, 'feature_importances_'):
                        feature_importance = dict(zip(
                            range(len(best_model.feature_importances_)),
                            best_model.feature_importances_
                        ))
                    elif hasattr(best_model, 'coef_'):
                        feature_importance = dict(zip(
                            range(len(best_model.coef_)),
                            np.abs(best_model.coef_)
                        ))
                    
                    training_time = (datetime.now() - start_time).total_seconds()
                    
                    ml_model = MLModel(
                        name=name,
                        model_type=self._get_model_type(name),
                        model=best_model,
                        hyperparameters=best_params,
                        performance_metrics={
                            "mse": mse,
                            "mae": mae,
                            "r2": r2,
                            "rmse": np.sqrt(mse)
                        },
                        feature_importance=feature_importance,
                        training_time=training_time
                    )
                    
                    best_models.append(ml_model)
                    
                except Exception as e:
                    self.logger.warning(f"Error training {name}: {e}")
                    continue
            
            # Ordenar por R²
            best_models.sort(key=lambda x: x.performance_metrics["r2"], reverse=True)
            
            return best_models[:5]  # Retornar top 5 modelos
            
        except Exception as e:
            self.logger.error(f"Error in automated model selection: {e}")
            raise
    
    def _get_model_type(self, model_name: str) -> ModelType:
        """Determinar tipo de modelo"""
        if "Linear" in model_name or "Ridge" in model_name or "Lasso" in model_name or "ElasticNet" in model_name:
            return ModelType.LINEAR
        elif "Random Forest" in model_name:
            return ModelType.TREE
        elif "Gradient" in model_name or "XGBoost" in model_name or "LightGBM" in model_name or "CatBoost" in model_name:
            return ModelType.BOOSTING
        elif "MLP" in model_name:
            return ModelType.NEURAL
        elif "SVR" in model_name:
            return ModelType.SVM
        else:
            return ModelType.ENSEMBLE
    
    async def _create_ensemble_model(self, best_models: List[MLModel], 
                                   X_train: np.ndarray, y_train: pd.Series) -> MLModel:
        """Crear modelo ensemble de los mejores modelos"""
        try:
            # Seleccionar top 3 modelos
            top_models = best_models[:3]
            
            # Crear VotingRegressor
            estimators = [(model.name, model.model) for model in top_models]
            ensemble = VotingRegressor(estimators)
            
            # Entrenar ensemble
            start_time = datetime.now()
            ensemble.fit(X_train, y_train)
            training_time = (datetime.now() - start_time).total_seconds()
            
            # Crear MLModel para ensemble
            ensemble_model = MLModel(
                name="Ensemble Model",
                model_type=ModelType.ENSEMBLE,
                model=ensemble,
                hyperparameters={"base_models": [model.name for model in top_models]},
                performance_metrics={},
                training_time=training_time
            )
            
            return ensemble_model
            
        except Exception as e:
            self.logger.error(f"Error creating ensemble model: {e}")
            raise
    
    async def _evaluate_final_model(self, model: MLModel, X_test: np.ndarray, 
                                  y_test: pd.Series) -> Dict[str, Any]:
        """Evaluar modelo final"""
        try:
            start_time = datetime.now()
            y_pred = model.model.predict(X_test)
            prediction_time = (datetime.now() - start_time).total_seconds()
            
            # Métricas de evaluación
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            # Métricas adicionales
            mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
            max_error = np.max(np.abs(y_test - y_pred))
            
            evaluation = {
                "mse": mse,
                "mae": mae,
                "r2": r2,
                "rmse": rmse,
                "mape": mape,
                "max_error": max_error,
                "prediction_time": prediction_time,
                "predictions": y_pred.tolist(),
                "actual": y_test.tolist()
            }
            
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Error evaluating final model: {e}")
            raise
    
    async def _generate_pipeline_report(self, best_models: List[MLModel], 
                                      ensemble_model: MLModel, final_evaluation: Dict[str, Any],
                                      start_time: datetime) -> Dict[str, Any]:
        """Generar reporte del pipeline"""
        try:
            total_time = (datetime.now() - start_time).total_seconds()
            
            report = {
                "pipeline_summary": {
                    "total_execution_time": total_time,
                    "models_tested": len(best_models),
                    "best_model": best_models[0].name if best_models else None,
                    "ensemble_performance": final_evaluation
                },
                "model_performance": [
                    {
                        "name": model.name,
                        "type": model.model_type.value,
                        "metrics": model.performance_metrics,
                        "training_time": model.training_time,
                        "hyperparameters": model.hyperparameters
                    }
                    for model in best_models
                ],
                "feature_engineering": {
                    "steps_applied": len(self.feature_engineering_steps),
                    "final_feature_count": len(best_models[0].feature_importance) if best_models and best_models[0].feature_importance else 0
                },
                "recommendations": await self._generate_recommendations(best_models, final_evaluation),
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "pipeline_version": "1.0",
                    "auto_ml_config": self.auto_ml_config
                }
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating pipeline report: {e}")
            raise
    
    async def _generate_recommendations(self, best_models: List[MLModel], 
                                      final_evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generar recomendaciones basadas en resultados"""
        recommendations = []
        
        # Recomendación de modelo
        if best_models:
            best_model = best_models[0]
            recommendations.append({
                "type": "model_selection",
                "priority": "high",
                "message": f"Use {best_model.name} as primary model",
                "reason": f"Best R² score: {best_model.performance_metrics['r2']:.3f}",
                "confidence": 0.9
            })
        
        # Recomendación de ensemble
        if final_evaluation["r2"] > 0.8:
            recommendations.append({
                "type": "ensemble",
                "priority": "medium",
                "message": "Consider using ensemble model for production",
                "reason": "High performance achieved with ensemble",
                "confidence": 0.8
            })
        
        # Recomendación de feature engineering
        if final_evaluation["r2"] < 0.7:
            recommendations.append({
                "type": "feature_engineering",
                "priority": "high",
                "message": "Consider additional feature engineering",
                "reason": "Model performance could be improved",
                "confidence": 0.7
            })
        
        return recommendations
    
    async def predict(self, model: MLModel, X: np.ndarray) -> np.ndarray:
        """Realizar predicciones con modelo entrenado"""
        try:
            start_time = datetime.now()
            predictions = model.model.predict(X)
            prediction_time = (datetime.now() - start_time).total_seconds()
            
            model.prediction_time = prediction_time
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error making predictions: {e}")
            raise
    
    async def save_model(self, model: MLModel, filepath: str) -> None:
        """Guardar modelo entrenado"""
        try:
            model_data = {
                "name": model.name,
                "model_type": model.model_type.value,
                "hyperparameters": model.hyperparameters,
                "performance_metrics": model.performance_metrics,
                "feature_importance": model.feature_importance,
                "training_time": model.training_time
            }
            
            # Guardar modelo
            joblib.dump(model.model, f"{filepath}_model.pkl")
            
            # Guardar metadatos
            with open(f"{filepath}_metadata.json", "w") as f:
                json.dump(model_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
            raise
    
    async def load_model(self, filepath: str) -> MLModel:
        """Cargar modelo guardado"""
        try:
            # Cargar modelo
            model = joblib.load(f"{filepath}_model.pkl")
            
            # Cargar metadatos
            with open(f"{filepath}_metadata.json", "r") as f:
                model_data = json.load(f)
            
            ml_model = MLModel(
                name=model_data["name"],
                model_type=ModelType(model_data["model_type"]),
                model=model,
                hyperparameters=model_data["hyperparameters"],
                performance_metrics=model_data["performance_metrics"],
                feature_importance=model_data.get("feature_importance"),
                training_time=model_data.get("training_time", 0.0)
            )
            
            return ml_model
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            raise
    
    async def get_pipeline_insights(self) -> Dict[str, Any]:
        """Obtener insights del pipeline"""
        insights = {
            "total_models_trained": len(self.models),
            "best_performance": 0.0,
            "average_training_time": 0.0,
            "model_types_used": {},
            "feature_engineering_steps": len(self.feature_engineering_steps)
        }
        
        if self.models:
            # Análisis de rendimiento
            performances = [model.performance_metrics.get("r2", 0) for model in self.models.values()]
            insights["best_performance"] = max(performances) if performances else 0.0
            
            # Tiempo promedio de entrenamiento
            training_times = [model.training_time for model in self.models.values()]
            insights["average_training_time"] = np.mean(training_times) if training_times else 0.0
            
            # Tipos de modelos usados
            for model in self.models.values():
                model_type = model.model_type.value
                insights["model_types_used"][model_type] = insights["model_types_used"].get(model_type, 0) + 1
        
        return insights

# Función principal para inicializar el pipeline
async def initialize_ml_pipeline() -> AdvancedMLPipeline:
    """Inicializar pipeline de ML avanzado"""
    pipeline = AdvancedMLPipeline()
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    return pipeline

if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        pipeline = await initialize_ml_pipeline()
        
        # Crear datos de ejemplo
        np.random.seed(42)
        n_samples = 1000
        
        data = pd.DataFrame({
            'feature_1': np.random.normal(0, 1, n_samples),
            'feature_2': np.random.normal(0, 1, n_samples),
            'feature_3': np.random.normal(0, 1, n_samples),
            'target': np.random.normal(0, 1, n_samples)
        })
        
        # Crear pipeline de ML
        report = await pipeline.create_ml_pipeline(data, 'target')
        print("ML Pipeline Report:", json.dumps(report, indent=2, default=str))
        
        # Obtener insights
        insights = await pipeline.get_pipeline_insights()
        print("Pipeline Insights:", json.dumps(insights, indent=2, default=str))
    
    asyncio.run(main())



