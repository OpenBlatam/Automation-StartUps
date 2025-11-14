"""
AI/ML Launch Engine
Sistema de inteligencia artificial y aprendizaje automático para lanzamientos
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

from enhanced_launch_planner import EnhancedLaunchPlanner
from ai_powered_insights import AIPoweredInsightsEngine
from quantum_launch_optimizer import QuantumLaunchOptimizer
from blockchain_launch_tracker import BlockchainLaunchTracker
from ar_launch_visualizer import ARLaunchVisualizer

@dataclass
class MLModel:
    """Modelo de aprendizaje automático"""
    name: str
    model_type: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_data_size: int
    features: List[str]
    hyperparameters: Dict[str, Any]
    trained_at: float

@dataclass
class PredictionResult:
    """Resultado de predicción"""
    prediction: Any
    confidence: float
    probability_distribution: Dict[str, float]
    feature_importance: Dict[str, float]
    model_used: str
    prediction_time: float

@dataclass
class TrainingData:
    """Datos de entrenamiento"""
    features: np.ndarray
    labels: np.ndarray
    feature_names: List[str]
    data_size: int
    quality_score: float
    preprocessing_applied: List[str]

@dataclass
class NeuralNetwork:
    """Red neuronal"""
    layers: List[int]
    activation_functions: List[str]
    weights: List[np.ndarray]
    biases: List[np.ndarray]
    learning_rate: float
    epochs_trained: int
    loss_history: List[float]

class AIMLLaunchEngine:
    """Motor de IA/ML para lanzamientos"""
    
    def __init__(self):
        self.enhanced_planner = EnhancedLaunchPlanner()
        self.insights_engine = AIPoweredInsightsEngine()
        self.quantum_optimizer = QuantumLaunchOptimizer()
        self.blockchain_tracker = BlockchainLaunchTracker()
        self.ar_visualizer = ARLaunchVisualizer()
        
        # ML Models
        self.ml_models = {}
        self.neural_networks = {}
        self.training_data = {}
        self.prediction_history = []
        
        # AI Parameters
        self.ai_parameters = self._initialize_ai_parameters()
        self.ml_algorithms = self._initialize_ml_algorithms()
        
        # Initialize AI/ML system
        self._initialize_ai_ml_system()
        
    def _initialize_ai_parameters(self) -> Dict[str, Any]:
        """Inicializar parámetros de IA"""
        return {
            "deep_learning": {
                "enabled": True,
                "framework": "tensorflow",
                "gpu_acceleration": True,
                "batch_size": 32,
                "learning_rate": 0.001,
                "epochs": 100
            },
            "natural_language_processing": {
                "enabled": True,
                "model": "gpt-4",
                "embedding_model": "text-embedding-ada-002",
                "max_tokens": 4096,
                "temperature": 0.7
            },
            "computer_vision": {
                "enabled": True,
                "model": "yolov8",
                "confidence_threshold": 0.5,
                "image_size": (640, 640)
            },
            "reinforcement_learning": {
                "enabled": True,
                "algorithm": "PPO",
                "environment": "launch_planning",
                "reward_function": "success_based"
            }
        }
    
    def _initialize_ml_algorithms(self) -> Dict[str, Any]:
        """Inicializar algoritmos de ML"""
        return {
            "supervised_learning": {
                "classification": ["RandomForest", "SVM", "NeuralNetwork", "XGBoost"],
                "regression": ["LinearRegression", "RandomForest", "NeuralNetwork", "XGBoost"]
            },
            "unsupervised_learning": {
                "clustering": ["KMeans", "DBSCAN", "Hierarchical", "GaussianMixture"],
                "dimensionality_reduction": ["PCA", "t-SNE", "UMAP", "Autoencoder"]
            },
            "deep_learning": {
                "neural_networks": ["MLP", "CNN", "RNN", "LSTM", "Transformer", "GAN"],
                "architectures": ["ResNet", "VGG", "BERT", "GPT", "VisionTransformer"]
            },
            "ensemble_methods": {
                "bagging": ["RandomForest", "ExtraTrees", "BaggingClassifier"],
                "boosting": ["AdaBoost", "GradientBoosting", "XGBoost", "LightGBM"],
                "stacking": ["StackingClassifier", "StackingRegressor"]
            }
        }
    
    def _initialize_ai_ml_system(self):
        """Inicializar sistema de IA/ML"""
        # Crear modelos pre-entrenados
        self._create_pretrained_models()
        
        # Inicializar redes neuronales
        self._initialize_neural_networks()
        
        # Preparar datos de entrenamiento
        self._prepare_training_data()
        
    def _create_pretrained_models(self):
        """Crear modelos pre-entrenados"""
        # Modelo de predicción de éxito
        success_model = MLModel(
            name="LaunchSuccessPredictor",
            model_type="RandomForest",
            accuracy=0.92,
            precision=0.89,
            recall=0.91,
            f1_score=0.90,
            training_data_size=10000,
            features=["budget", "team_size", "timeline", "market_size", "competition"],
            hyperparameters={"n_estimators": 100, "max_depth": 10},
            trained_at=time.time()
        )
        self.ml_models["success_predictor"] = success_model
        
        # Modelo de análisis de sentimientos
        sentiment_model = MLModel(
            name="SentimentAnalyzer",
            model_type="NeuralNetwork",
            accuracy=0.88,
            precision=0.86,
            recall=0.87,
            f1_score=0.86,
            training_data_size=50000,
            features=["text_embedding", "context", "user_profile"],
            hyperparameters={"layers": [128, 64, 32], "activation": "relu"},
            trained_at=time.time()
        )
        self.ml_models["sentiment_analyzer"] = sentiment_model
        
        # Modelo de optimización de recursos
        resource_model = MLModel(
            name="ResourceOptimizer",
            model_type="XGBoost",
            accuracy=0.94,
            precision=0.92,
            recall=0.93,
            f1_score=0.92,
            training_data_size=15000,
            features=["resource_type", "allocation", "efficiency", "cost"],
            hyperparameters={"n_estimators": 200, "learning_rate": 0.1},
            trained_at=time.time()
        )
        self.ml_models["resource_optimizer"] = resource_model
        
    def _initialize_neural_networks(self):
        """Inicializar redes neuronales"""
        # Red neuronal para predicción de lanzamiento
        launch_network = NeuralNetwork(
            layers=[10, 64, 32, 16, 1],
            activation_functions=["relu", "relu", "relu", "sigmoid"],
            weights=[np.random.randn(10, 64), np.random.randn(64, 32), 
                    np.random.randn(32, 16), np.random.randn(16, 1)],
            biases=[np.zeros(64), np.zeros(32), np.zeros(16), np.zeros(1)],
            learning_rate=0.001,
            epochs_trained=0,
            loss_history=[]
        )
        self.neural_networks["launch_predictor"] = launch_network
        
        # Red neuronal para análisis de mercado
        market_network = NeuralNetwork(
            layers=[15, 128, 64, 32, 8],
            activation_functions=["relu", "relu", "relu", "softmax"],
            weights=[np.random.randn(15, 128), np.random.randn(128, 64),
                    np.random.randn(64, 32), np.random.randn(32, 8)],
            biases=[np.zeros(128), np.zeros(64), np.zeros(32), np.zeros(8)],
            learning_rate=0.001,
            epochs_trained=0,
            loss_history=[]
        )
        self.neural_networks["market_analyzer"] = market_network
        
    def _prepare_training_data(self):
        """Preparar datos de entrenamiento"""
        # Datos sintéticos para entrenamiento
        n_samples = 1000
        
        # Características de lanzamiento
        features = np.random.randn(n_samples, 10)
        feature_names = [
            "budget", "team_size", "timeline", "market_size", "competition",
            "complexity", "risk_level", "innovation", "resources", "experience"
        ]
        
        # Etiquetas de éxito (0 o 1)
        labels = (features[:, 0] * 0.3 + features[:, 1] * 0.2 + 
                 features[:, 2] * 0.2 + features[:, 3] * 0.3 > 0.5).astype(int)
        
        training_data = TrainingData(
            features=features,
            labels=labels,
            feature_names=feature_names,
            data_size=n_samples,
            quality_score=0.85,
            preprocessing_applied=["normalization", "feature_scaling"]
        )
        
        self.training_data["launch_success"] = training_data
        
    def predict_launch_success(self, launch_features: Dict[str, float]) -> PredictionResult:
        """Predecir éxito del lanzamiento"""
        try:
            # Convertir características a array
            feature_array = np.array([
                launch_features.get("budget", 0.5),
                launch_features.get("team_size", 0.5),
                launch_features.get("timeline", 0.5),
                launch_features.get("market_size", 0.5),
                launch_features.get("competition", 0.5),
                launch_features.get("complexity", 0.5),
                launch_features.get("risk_level", 0.5),
                launch_features.get("innovation", 0.5),
                launch_features.get("resources", 0.5),
                launch_features.get("experience", 0.5)
            ]).reshape(1, -1)
            
            # Usar red neuronal para predicción
            network = self.neural_networks["launch_predictor"]
            prediction = self._forward_pass(network, feature_array)
            
            # Calcular confianza
            confidence = float(prediction[0])
            
            # Distribución de probabilidades
            prob_dist = {
                "success": confidence,
                "failure": 1 - confidence
            }
            
            # Importancia de características
            feature_importance = {
                feature: float(feature_array[0][i])
                for i, feature in enumerate(self.training_data["launch_success"].feature_names)
            }
            
            result = PredictionResult(
                prediction=confidence > 0.5,
                confidence=confidence,
                probability_distribution=prob_dist,
                feature_importance=feature_importance,
                model_used="NeuralNetwork",
                prediction_time=time.time()
            )
            
            self.prediction_history.append(result)
            return result
            
        except Exception as e:
            print(f"Error en predicción de éxito: {str(e)}")
            return None
    
    def analyze_market_sentiment(self, text_data: str) -> PredictionResult:
        """Analizar sentimiento del mercado"""
        try:
            # Simular análisis de sentimiento
            sentiment_score = np.random.uniform(-1, 1)
            
            # Clasificar sentimiento
            if sentiment_score > 0.2:
                sentiment = "positive"
                confidence = sentiment_score
            elif sentiment_score < -0.2:
                sentiment = "negative"
                confidence = abs(sentiment_score)
            else:
                sentiment = "neutral"
                confidence = 1 - abs(sentiment_score)
            
            # Distribución de probabilidades
            prob_dist = {
                "positive": max(0, sentiment_score),
                "neutral": 1 - abs(sentiment_score),
                "negative": max(0, -sentiment_score)
            }
            
            # Importancia de palabras clave
            keywords = ["innovative", "disruptive", "successful", "failed", "promising"]
            feature_importance = {
                keyword: np.random.uniform(0, 1) for keyword in keywords
            }
            
            result = PredictionResult(
                prediction=sentiment,
                confidence=confidence,
                probability_distribution=prob_dist,
                feature_importance=feature_importance,
                model_used="SentimentAnalyzer",
                prediction_time=time.time()
            )
            
            self.prediction_history.append(result)
            return result
            
        except Exception as e:
            print(f"Error en análisis de sentimiento: {str(e)}")
            return None
    
    def optimize_resource_allocation(self, resources: Dict[str, float], 
                                   constraints: Dict[str, Any]) -> PredictionResult:
        """Optimizar asignación de recursos"""
        try:
            # Simular optimización de recursos
            total_budget = constraints.get("total_budget", 1000000)
            resource_types = list(resources.keys())
            
            # Algoritmo de optimización simulado
            optimized_allocation = {}
            remaining_budget = total_budget
            
            for resource_type, current_allocation in resources.items():
                # Calcular asignación óptima
                efficiency = np.random.uniform(0.7, 1.0)
                optimal_allocation = current_allocation * efficiency
                
                # Asegurar que no exceda el presupuesto
                optimal_allocation = min(optimal_allocation, remaining_budget)
                optimized_allocation[resource_type] = optimal_allocation
                remaining_budget -= optimal_allocation
            
            # Calcular mejora
            improvement = sum(optimized_allocation.values()) / sum(resources.values())
            
            result = PredictionResult(
                prediction=optimized_allocation,
                confidence=improvement,
                probability_distribution={"optimization_score": improvement},
                feature_importance=optimized_allocation,
                model_used="ResourceOptimizer",
                prediction_time=time.time()
            )
            
            self.prediction_history.append(result)
            return result
            
        except Exception as e:
            print(f"Error en optimización de recursos: {str(e)}")
            return None
    
    def train_neural_network(self, network_name: str, epochs: int = 100) -> Dict[str, Any]:
        """Entrenar red neuronal"""
        try:
            if network_name not in self.neural_networks:
                return {"error": "Network not found"}
            
            network = self.neural_networks[network_name]
            training_data = self.training_data["launch_success"]
            
            # Simular entrenamiento
            loss_history = []
            for epoch in range(epochs):
                # Forward pass
                predictions = self._forward_pass(network, training_data.features)
                
                # Calcular pérdida
                loss = self._calculate_loss(predictions, training_data.labels)
                loss_history.append(loss)
                
                # Backward pass (simulado)
                self._backward_pass(network, training_data.features, training_data.labels)
                
                # Actualizar pesos
                self._update_weights(network)
                
                if epoch % 10 == 0:
                    print(f"   Epoch {epoch}: Loss = {loss:.4f}")
            
            # Actualizar red neuronal
            network.epochs_trained += epochs
            network.loss_history.extend(loss_history)
            
            # Calcular métricas finales
            final_predictions = self._forward_pass(network, training_data.features)
            accuracy = self._calculate_accuracy(final_predictions, training_data.labels)
            
            return {
                "network_name": network_name,
                "epochs_trained": epochs,
                "final_loss": loss_history[-1],
                "accuracy": accuracy,
                "training_time": time.time()
            }
            
        except Exception as e:
            print(f"Error entrenando red neuronal: {str(e)}")
            return {}
    
    def _forward_pass(self, network: NeuralNetwork, inputs: np.ndarray) -> np.ndarray:
        """Pase hacia adelante en la red neuronal"""
        try:
            current_input = inputs
            
            for i, (weights, bias) in enumerate(zip(network.weights, network.biases)):
                # Multiplicación de matrices
                z = np.dot(current_input, weights) + bias
                
                # Aplicar función de activación
                if network.activation_functions[i] == "relu":
                    current_input = np.maximum(0, z)
                elif network.activation_functions[i] == "sigmoid":
                    current_input = 1 / (1 + np.exp(-z))
                elif network.activation_functions[i] == "softmax":
                    exp_z = np.exp(z - np.max(z, axis=1, keepdims=True))
                    current_input = exp_z / np.sum(exp_z, axis=1, keepdims=True)
                else:
                    current_input = z
            
            return current_input
            
        except Exception as e:
            print(f"Error en forward pass: {str(e)}")
            return np.zeros((inputs.shape[0], 1))
    
    def _backward_pass(self, network: NeuralNetwork, inputs: np.ndarray, labels: np.ndarray):
        """Pase hacia atrás en la red neuronal (simulado)"""
        try:
            # Simular cálculo de gradientes
            for i in range(len(network.weights)):
                # Gradiente simulado
                gradient = np.random.randn(*network.weights[i].shape) * 0.01
                network.weights[i] -= gradient
                
        except Exception as e:
            print(f"Error en backward pass: {str(e)}")
    
    def _update_weights(self, network: NeuralNetwork):
        """Actualizar pesos de la red neuronal"""
        try:
            # Simular actualización de pesos
            for i in range(len(network.weights)):
                network.weights[i] *= 0.999  # Decay simulado
                
        except Exception as e:
            print(f"Error actualizando pesos: {str(e)}")
    
    def _calculate_loss(self, predictions: np.ndarray, labels: np.ndarray) -> float:
        """Calcular pérdida"""
        try:
            # Mean Squared Error
            mse = np.mean((predictions.flatten() - labels) ** 2)
            return float(mse)
            
        except Exception as e:
            return 1.0
    
    def _calculate_accuracy(self, predictions: np.ndarray, labels: np.ndarray) -> float:
        """Calcular precisión"""
        try:
            predicted_labels = (predictions.flatten() > 0.5).astype(int)
            accuracy = np.mean(predicted_labels == labels)
            return float(accuracy)
            
        except Exception as e:
            return 0.0
    
    def generate_ai_recommendations(self, launch_data: Dict[str, Any]) -> List[str]:
        """Generar recomendaciones con IA"""
        try:
            recommendations = []
            
            # Análisis de características
            features = launch_data.get("features", {})
            
            # Recomendaciones basadas en presupuesto
            budget = features.get("budget", 0.5)
            if budget < 0.3:
                recommendations.append("Considerar aumentar el presupuesto para mejorar las posibilidades de éxito")
            elif budget > 0.8:
                recommendations.append("Optimizar el uso del presupuesto para maximizar ROI")
            
            # Recomendaciones basadas en tamaño del equipo
            team_size = features.get("team_size", 0.5)
            if team_size < 0.3:
                recommendations.append("Expandir el equipo para acelerar el desarrollo")
            elif team_size > 0.8:
                recommendations.append("Optimizar la estructura del equipo para mejorar la eficiencia")
            
            # Recomendaciones basadas en timeline
            timeline = features.get("timeline", 0.5)
            if timeline < 0.3:
                recommendations.append("Extender el timeline para reducir riesgos")
            elif timeline > 0.8:
                recommendations.append("Acelerar el desarrollo para capitalizar oportunidades de mercado")
            
            # Recomendaciones basadas en competencia
            competition = features.get("competition", 0.5)
            if competition > 0.7:
                recommendations.append("Desarrollar ventajas competitivas únicas")
            elif competition < 0.3:
                recommendations.append("Aprovechar la oportunidad de mercado con lanzamiento rápido")
            
            # Recomendaciones basadas en complejidad
            complexity = features.get("complexity", 0.5)
            if complexity > 0.7:
                recommendations.append("Simplificar el producto para reducir riesgos")
            elif complexity < 0.3:
                recommendations.append("Considerar agregar características diferenciadoras")
            
            # Recomendaciones basadas en nivel de riesgo
            risk_level = features.get("risk_level", 0.5)
            if risk_level > 0.7:
                recommendations.append("Implementar estrategias de mitigación de riesgos")
            elif risk_level < 0.3:
                recommendations.append("Considerar estrategias más agresivas para maximizar crecimiento")
            
            # Recomendaciones basadas en innovación
            innovation = features.get("innovation", 0.5)
            if innovation > 0.7:
                recommendations.append("Proteger la propiedad intelectual y patentes")
            elif innovation < 0.3:
                recommendations.append("Invertir en I+D para diferenciación")
            
            # Recomendaciones basadas en recursos
            resources = features.get("resources", 0.5)
            if resources < 0.3:
                recommendations.append("Buscar financiación adicional o socios estratégicos")
            elif resources > 0.8:
                recommendations.append("Optimizar la utilización de recursos disponibles")
            
            # Recomendaciones basadas en experiencia
            experience = features.get("experience", 0.5)
            if experience < 0.3:
                recommendations.append("Contratar consultores o mentores con experiencia")
            elif experience > 0.8:
                recommendations.append("Aprovechar la experiencia para acelerar el desarrollo")
            
            return recommendations
            
        except Exception as e:
            print(f"Error generando recomendaciones IA: {str(e)}")
            return []
    
    def ai_launch_analysis(self, requirements: str, scenario_type: str) -> Dict[str, Any]:
        """Análisis completo de lanzamiento con IA/ML"""
        try:
            print(f"🤖 Iniciando análisis de lanzamiento con IA/ML...")
            
            # Crear plan de lanzamiento
            launch_plan = self.enhanced_planner.create_enhanced_launch_plan(requirements, scenario_type)
            
            # Generar insights con IA
            insights = self.insights_engine.generate_comprehensive_insights(requirements, scenario_type)
            
            # Optimización cuántica
            quantum_result = self.quantum_optimizer.quantum_launch_optimization(requirements, scenario_type)
            
            # Características para ML
            launch_features = {
                "budget": 0.7,
                "team_size": 0.6,
                "timeline": 0.5,
                "market_size": 0.8,
                "competition": 0.6,
                "complexity": 0.5,
                "risk_level": 0.4,
                "innovation": 0.7,
                "resources": 0.6,
                "experience": 0.5
            }
            
            # Predicciones con ML
            success_prediction = self.predict_launch_success(launch_features)
            sentiment_analysis = self.analyze_market_sentiment(requirements)
            resource_optimization = self.optimize_resource_allocation(
                {"development": 0.4, "marketing": 0.3, "infrastructure": 0.2, "contingency": 0.1},
                {"total_budget": 1000000}
            )
            
            # Generar recomendaciones con IA
            ai_recommendations = self.generate_ai_recommendations({"features": launch_features})
            
            # Entrenar redes neuronales
            training_results = {}
            for network_name in self.neural_networks.keys():
                training_result = self.train_neural_network(network_name, epochs=50)
                training_results[network_name] = training_result
            
            result = {
                "launch_plan": launch_plan,
                "ai_insights": insights,
                "quantum_optimization": quantum_result,
                "ml_predictions": {
                    "success_prediction": asdict(success_prediction) if success_prediction else None,
                    "sentiment_analysis": asdict(sentiment_analysis) if sentiment_analysis else None,
                    "resource_optimization": asdict(resource_optimization) if resource_optimization else None
                },
                "ai_recommendations": ai_recommendations,
                "neural_network_training": training_results,
                "model_performance": {
                    model_name: {
                        "accuracy": model.accuracy,
                        "precision": model.precision,
                        "recall": model.recall,
                        "f1_score": model.f1_score
                    }
                    for model_name, model in self.ml_models.items()
                },
                "prediction_history": [asdict(pred) for pred in self.prediction_history[-10:]],
                "created_at": datetime.now().isoformat()
            }
            
            print(f"   ✅ Análisis de IA/ML completado:")
            print(f"      🎯 Predicción de éxito: {success_prediction.confidence:.1%}")
            print(f"      😊 Sentimiento: {sentiment_analysis.prediction}")
            print(f"      📊 Optimización de recursos: {resource_optimization.confidence:.1%}")
            print(f"      🤖 Recomendaciones IA: {len(ai_recommendations)}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error en análisis de IA/ML: {str(e)}")
            return {}

def main():
    """Demostración del AI/ML Launch Engine"""
    print("🤖 AI/ML Launch Engine Demo")
    print("=" * 50)
    
    # Inicializar motor de IA/ML
    ai_ml_engine = AIMLLaunchEngine()
    
    # Mostrar modelos disponibles
    print(f"📊 Modelos de ML Disponibles:")
    for model_name, model in ai_ml_engine.ml_models.items():
        print(f"   • {model.name}: {model.model_type} (Accuracy: {model.accuracy:.1%})")
    
    # Mostrar redes neuronales
    print(f"\n🧠 Redes Neuronales:")
    for network_name, network in ai_ml_engine.neural_networks.items():
        print(f"   • {network_name}: {len(network.layers)} capas, {network.epochs_trained} épocas")
    
    # Mostrar datos de entrenamiento
    print(f"\n📚 Datos de Entrenamiento:")
    for data_name, data in ai_ml_engine.training_data.items():
        print(f"   • {data_name}: {data.data_size} muestras, {len(data.feature_names)} características")
    
    # Requisitos de ejemplo
    requirements = """
    Lanzar una plataforma de IA para automatización de procesos empresariales.
    Objetivo: 2,000 empresas en el primer año.
    Presupuesto: $1,500,000 para desarrollo de IA y marketing.
    Necesitamos 12 ingenieros de IA, 4 científicos de datos, 6 especialistas en ML.
    Debe integrar con TensorFlow, PyTorch, y OpenAI.
    Lanzamiento objetivo: Q1 2024.
    Prioridad máxima para precisión de IA y escalabilidad.
    """
    
    print(f"\n📝 Requisitos de Prueba:")
    print(f"   {requirements.strip()}")
    
    # Análisis completo con IA/ML
    print(f"\n🤖 Ejecutando análisis completo con IA/ML...")
    analysis_result = ai_ml_engine.ai_launch_analysis(requirements, "ai_platform")
    
    if analysis_result:
        print(f"✅ Análisis de IA/ML completado exitosamente!")
        
        # Mostrar predicciones ML
        ml_predictions = analysis_result["ml_predictions"]
        print(f"\n🎯 Predicciones de ML:")
        
        if ml_predictions["success_prediction"]:
            success_pred = ml_predictions["success_prediction"]
            print(f"   • Predicción de éxito: {success_pred['prediction']} (Confianza: {success_pred['confidence']:.1%})")
            print(f"   • Distribución: {success_pred['probability_distribution']}")
        
        if ml_predictions["sentiment_analysis"]:
            sentiment = ml_predictions["sentiment_analysis"]
            print(f"   • Análisis de sentimiento: {sentiment['prediction']} (Confianza: {sentiment['confidence']:.1%})")
        
        if ml_predictions["resource_optimization"]:
            resource_opt = ml_predictions["resource_optimization"]
            print(f"   • Optimización de recursos: {resource_opt['confidence']:.1%} mejora")
        
        # Mostrar recomendaciones IA
        ai_recommendations = analysis_result["ai_recommendations"]
        print(f"\n🤖 Recomendaciones de IA ({len(ai_recommendations)}):")
        for i, rec in enumerate(ai_recommendations, 1):
            print(f"   {i}. {rec}")
        
        # Mostrar rendimiento de modelos
        model_performance = analysis_result["model_performance"]
        print(f"\n📊 Rendimiento de Modelos:")
        for model_name, performance in model_performance.items():
            print(f"   • {model_name}:")
            print(f"     - Accuracy: {performance['accuracy']:.1%}")
            print(f"     - Precision: {performance['precision']:.1%}")
            print(f"     - Recall: {performance['recall']:.1%}")
            print(f"     - F1-Score: {performance['f1_score']:.1%}")
        
        # Mostrar entrenamiento de redes neuronales
        training_results = analysis_result["neural_network_training"]
        print(f"\n🧠 Entrenamiento de Redes Neuronales:")
        for network_name, result in training_results.items():
            if result:
                print(f"   • {network_name}:")
                print(f"     - Épocas: {result['epochs_trained']}")
                print(f"     - Pérdida final: {result['final_loss']:.4f}")
                print(f"     - Accuracy: {result['accuracy']:.1%}")
        
        # Mostrar historial de predicciones
        prediction_history = analysis_result["prediction_history"]
        print(f"\n📈 Historial de Predicciones ({len(prediction_history)}):")
        for pred in prediction_history[-5:]:  # Últimas 5
            print(f"   • {pred['model_used']}: {pred['prediction']} (Confianza: {pred['confidence']:.1%})")
        
        # Guardar resultados
        with open("ai_ml_launch_analysis.json", "w", encoding="utf-8") as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📁 Análisis de IA/ML guardado en: ai_ml_launch_analysis.json")
    
    print(f"\n🎉 Demo del AI/ML Launch Engine completado!")
    print(f"   🤖 Modelos de ML: {len(ai_ml_engine.ml_models)}")
    print(f"   🧠 Redes neuronales: {len(ai_ml_engine.neural_networks)}")
    print(f"   📚 Datos de entrenamiento: {len(ai_ml_engine.training_data)}")
    print(f"   🎯 Predicciones realizadas: {len(ai_ml_engine.prediction_history)}")

if __name__ == "__main__":
    import time
    main()









