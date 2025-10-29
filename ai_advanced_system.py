"""
Sistema de Inteligencia Artificial Avanzado
==========================================

Sistema completo de IA con deep learning, redes neuronales,
análisis predictivo avanzado y automatización inteligente.
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AIModelType(Enum):
    """Tipos de modelos de IA"""
    LSTM_FORECASTING = "lstm_forecasting"
    CNN_CLASSIFICATION = "cnn_classification"
    TRANSFORMER_PREDICTION = "transformer_prediction"
    GAN_SYNTHETIC_DATA = "gan_synthetic_data"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    TRANSFER_LEARNING = "transfer_learning"

class DeepLearningFramework(Enum):
    """Frameworks de deep learning"""
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    KERAS = "keras"

@dataclass
class AIModelPerformance:
    """Rendimiento del modelo de IA"""
    model_name: str
    model_type: str
    framework: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mae: float
    mse: float
    rmse: float
    r2_score: float
    training_time: float
    inference_time: float
    model_size_mb: float
    parameters_count: int
    timestamp: datetime

@dataclass
class AIPrediction:
    """Predicción de IA"""
    model_name: str
    prediction: Any
    confidence: float
    uncertainty: float
    features_used: List[str]
    model_explanation: Dict[str, Any]
    timestamp: datetime
    metadata: Dict[str, Any]

class LSTMForecastingModel:
    """Modelo LSTM para predicción de series temporales"""
    
    def __init__(self, sequence_length: int = 60, features: int = 10):
        self.sequence_length = sequence_length
        self.features = features
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def build_model(self):
        """Construir arquitectura LSTM"""
        model = keras.Sequential([
            layers.LSTM(128, return_sequences=True, input_shape=(self.sequence_length, self.features)),
            layers.Dropout(0.2),
            layers.LSTM(64, return_sequences=False),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(1, activation='linear')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae', 'mse']
        )
        
        self.model = model
        return model
    
    def prepare_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Preparar secuencias para LSTM"""
        X, y = [], []
        
        for i in range(self.sequence_length, len(data)):
            X.append(data[i-self.sequence_length:i])
            y.append(data[i])
        
        return np.array(X), np.array(y)
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              X_val: np.ndarray = None, y_val: np.ndarray = None,
              epochs: int = 100, batch_size: int = 32) -> Dict[str, Any]:
        """Entrenar modelo LSTM"""
        
        if self.model is None:
            self.build_model()
        
        # Preparar datos de validación
        validation_data = None
        if X_val is not None and y_val is not None:
            validation_data = (X_val, y_val)
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5),
            keras.callbacks.ModelCheckpoint('best_lstm_model.h5', save_best_only=True)
        ]
        
        # Entrenar
        start_time = datetime.now()
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        training_time = (datetime.now() - start_time).total_seconds()
        
        self.is_trained = True
        
        return {
            'history': history.history,
            'training_time': training_time,
            'final_loss': history.history['loss'][-1],
            'final_val_loss': history.history.get('val_loss', [None])[-1]
        }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Hacer predicciones"""
        if not self.is_trained:
            raise ValueError("Modelo no entrenado")
        
        return self.model.predict(X)
    
    def predict_future(self, last_sequence: np.ndarray, steps: int = 30) -> np.ndarray:
        """Predecir valores futuros"""
        predictions = []
        current_sequence = last_sequence.copy()
        
        for _ in range(steps):
            pred = self.model.predict(current_sequence.reshape(1, self.sequence_length, self.features))
            predictions.append(pred[0, 0])
            
            # Actualizar secuencia
            current_sequence = np.roll(current_sequence, -1, axis=0)
            current_sequence[-1, 0] = pred[0, 0]  # Asumir que la primera característica es el target
        
        return np.array(predictions)

class CNNClassificationModel:
    """Modelo CNN para clasificación de imágenes de productos"""
    
    def __init__(self, input_shape: Tuple[int, int, int] = (224, 224, 3), num_classes: int = 10):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = None
        self.is_trained = False
    
    def build_model(self):
        """Construir arquitectura CNN"""
        model = keras.Sequential([
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=self.input_shape),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dropout(0.5),
            layers.Dense(512, activation='relu'),
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        return model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray = None, y_val: np.ndarray = None,
              epochs: int = 50, batch_size: int = 32) -> Dict[str, Any]:
        """Entrenar modelo CNN"""
        
        if self.model is None:
            self.build_model()
        
        # Data augmentation
        datagen = keras.preprocessing.image.ImageDataGenerator(
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            zoom_range=0.2
        )
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5),
            keras.callbacks.ModelCheckpoint('best_cnn_model.h5', save_best_only=True)
        ]
        
        # Entrenar
        start_time = datetime.now()
        history = self.model.fit(
            datagen.flow(X_train, y_train, batch_size=batch_size),
            validation_data=(X_val, y_val) if X_val is not None else None,
            epochs=epochs,
            callbacks=callbacks,
            verbose=1
        )
        training_time = (datetime.now() - start_time).total_seconds()
        
        self.is_trained = True
        
        return {
            'history': history.history,
            'training_time': training_time,
            'final_accuracy': history.history['accuracy'][-1],
            'final_val_accuracy': history.history.get('val_accuracy', [None])[-1]
        }

class TransformerPredictionModel:
    """Modelo Transformer para predicción avanzada"""
    
    def __init__(self, d_model: int = 128, num_heads: int = 8, num_layers: int = 4):
        self.d_model = d_model
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.model = None
        self.is_trained = False
    
    def build_model(self, input_shape: Tuple[int, int]):
        """Construir arquitectura Transformer"""
        
        # Input layer
        inputs = keras.Input(shape=input_shape)
        
        # Positional encoding
        x = layers.Dense(self.d_model)(inputs)
        
        # Transformer blocks
        for _ in range(self.num_layers):
            # Multi-head attention
            attention_output = layers.MultiHeadAttention(
                num_heads=self.num_heads,
                key_dim=self.d_model // self.num_heads
            )(x, x)
            
            # Add & Norm
            x = layers.Add()([x, attention_output])
            x = layers.LayerNormalization()(x)
            
            # Feed forward
            ffn = keras.Sequential([
                layers.Dense(self.d_model * 4, activation='relu'),
                layers.Dense(self.d_model)
            ])
            ffn_output = ffn(x)
            
            # Add & Norm
            x = layers.Add()([x, ffn_output])
            x = layers.LayerNormalization()(x)
        
        # Global average pooling and output
        x = layers.GlobalAveragePooling1D()(x)
        outputs = layers.Dense(1, activation='linear')(x)
        
        model = keras.Model(inputs, outputs)
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        self.model = model
        return model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray = None, y_val: np.ndarray = None,
              epochs: int = 100, batch_size: int = 32) -> Dict[str, Any]:
        """Entrenar modelo Transformer"""
        
        if self.model is None:
            self.build_model(X_train.shape[1:])
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(patience=15, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5),
            keras.callbacks.ModelCheckpoint('best_transformer_model.h5', save_best_only=True)
        ]
        
        # Entrenar
        start_time = datetime.now()
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val) if X_val is not None else None,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        training_time = (datetime.now() - start_time).total_seconds()
        
        self.is_trained = True
        
        return {
            'history': history.history,
            'training_time': training_time,
            'final_loss': history.history['loss'][-1],
            'final_val_loss': history.history.get('val_loss', [None])[-1]
        }

class GANSyntheticDataGenerator:
    """Generador de datos sintéticos usando GAN"""
    
    def __init__(self, noise_dim: int = 100, data_dim: int = 10):
        self.noise_dim = noise_dim
        self.data_dim = data_dim
        self.generator = None
        self.discriminator = None
        self.gan = None
        self.is_trained = False
    
    def build_generator(self):
        """Construir generador"""
        model = keras.Sequential([
            layers.Dense(256, activation='relu', input_shape=(self.noise_dim,)),
            layers.BatchNormalization(),
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dense(1024, activation='relu'),
            layers.BatchNormalization(),
            layers.Dense(self.data_dim, activation='tanh')
        ])
        
        self.generator = model
        return model
    
    def build_discriminator(self):
        """Construir discriminador"""
        model = keras.Sequential([
            layers.Dense(1024, activation='relu', input_shape=(self.data_dim,)),
            layers.Dropout(0.3),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.0002),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        self.discriminator = model
        return model
    
    def build_gan(self):
        """Construir GAN completo"""
        if self.generator is None:
            self.build_generator()
        if self.discriminator is None:
            self.build_discriminator()
        
        # Hacer el discriminador no entrenable
        self.discriminator.trainable = False
        
        # Construir GAN
        noise = keras.Input(shape=(self.noise_dim,))
        generated_data = self.generator(noise)
        validity = self.discriminator(generated_data)
        
        self.gan = keras.Model(noise, validity)
        self.gan.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.0002),
            loss='binary_crossentropy'
        )
        
        # Restaurar entrenabilidad del discriminador
        self.discriminator.trainable = True
    
    def train(self, real_data: np.ndarray, epochs: int = 1000, batch_size: int = 32) -> Dict[str, Any]:
        """Entrenar GAN"""
        
        if self.gan is None:
            self.build_gan()
        
        # Normalizar datos reales
        real_data = (real_data - np.mean(real_data, axis=0)) / (np.std(real_data, axis=0) + 1e-8)
        
        # Etiquetas
        valid = np.ones((batch_size, 1))
        fake = np.zeros((batch_size, 1))
        
        d_losses = []
        g_losses = []
        
        start_time = datetime.now()
        
        for epoch in range(epochs):
            # Entrenar discriminador
            idx = np.random.randint(0, real_data.shape[0], batch_size)
            real_batch = real_data[idx]
            
            noise = np.random.normal(0, 1, (batch_size, self.noise_dim))
            fake_batch = self.generator.predict(noise, verbose=0)
            
            d_loss_real = self.discriminator.train_on_batch(real_batch, valid)
            d_loss_fake = self.discriminator.train_on_batch(fake_batch, fake)
            d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)
            
            # Entrenar generador
            noise = np.random.normal(0, 1, (batch_size, self.noise_dim))
            g_loss = self.gan.train_on_batch(noise, valid)
            
            d_losses.append(d_loss[0])
            g_losses.append(g_loss)
            
            if epoch % 100 == 0:
                print(f"Epoch {epoch}, D Loss: {d_loss[0]:.4f}, G Loss: {g_loss:.4f}")
        
        training_time = (datetime.now() - start_time).total_seconds()
        self.is_trained = True
        
        return {
            'training_time': training_time,
            'd_losses': d_losses,
            'g_losses': g_losses,
            'final_d_loss': d_losses[-1],
            'final_g_loss': g_losses[-1]
        }
    
    def generate_synthetic_data(self, num_samples: int = 1000) -> np.ndarray:
        """Generar datos sintéticos"""
        if not self.is_trained:
            raise ValueError("GAN no entrenado")
        
        noise = np.random.normal(0, 1, (num_samples, self.noise_dim))
        synthetic_data = self.generator.predict(noise, verbose=0)
        
        return synthetic_data

class ReinforcementLearningAgent:
    """Agente de aprendizaje por refuerzo para optimización de inventario"""
    
    def __init__(self, state_size: int = 10, action_size: int = 5):
        self.state_size = state_size
        self.action_size = action_size
        self.q_network = None
        self.target_network = None
        self.memory = []
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.gamma = 0.95
        self.batch_size = 32
        self.is_trained = False
    
    def build_q_network(self):
        """Construir red Q"""
        model = keras.Sequential([
            layers.Dense(64, activation='relu', input_shape=(self.state_size,)),
            layers.Dense(64, activation='relu'),
            layers.Dense(32, activation='relu'),
            layers.Dense(self.action_size, activation='linear')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='mse'
        )
        
        self.q_network = model
        self.target_network = keras.models.clone_model(model)
        self.target_network.set_weights(model.get_weights())
        
        return model
    
    def remember(self, state, action, reward, next_state, done):
        """Almacenar experiencia en memoria"""
        self.memory.append((state, action, reward, next_state, done))
        
        if len(self.memory) > 10000:  # Limitar tamaño de memoria
            self.memory.pop(0)
    
    def act(self, state):
        """Seleccionar acción usando epsilon-greedy"""
        if np.random.random() <= self.epsilon:
            return np.random.choice(self.action_size)
        
        q_values = self.q_network.predict(state.reshape(1, -1), verbose=0)
        return np.argmax(q_values[0])
    
    def replay(self):
        """Entrenar la red con experiencias aleatorias"""
        if len(self.memory) < self.batch_size:
            return
        
        batch = np.random.choice(len(self.memory), self.batch_size, replace=False)
        states = np.array([self.memory[i][0] for i in batch])
        actions = np.array([self.memory[i][1] for i in batch])
        rewards = np.array([self.memory[i][2] for i in batch])
        next_states = np.array([self.memory[i][3] for i in batch])
        dones = np.array([self.memory[i][4] for i in batch])
        
        targets = self.q_network.predict(states, verbose=0)
        next_q_values = self.target_network.predict(next_states, verbose=0)
        
        for i in range(self.batch_size):
            if dones[i]:
                targets[i][actions[i]] = rewards[i]
            else:
                targets[i][actions[i]] = rewards[i] + self.gamma * np.max(next_q_values[i])
        
        self.q_network.fit(states, targets, epochs=1, verbose=0)
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def update_target_network(self):
        """Actualizar red objetivo"""
        self.target_network.set_weights(self.q_network.get_weights())
    
    def train(self, env, episodes: int = 1000) -> Dict[str, Any]:
        """Entrenar agente"""
        
        if self.q_network is None:
            self.build_q_network()
        
        scores = []
        start_time = datetime.now()
        
        for episode in range(episodes):
            state = env.reset()
            total_reward = 0
            
            while True:
                action = self.act(state)
                next_state, reward, done, _ = env.step(action)
                
                self.remember(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward
                
                if done:
                    break
            
            scores.append(total_reward)
            
            if episode % 10 == 0:
                self.replay()
                self.update_target_network()
            
            if episode % 100 == 0:
                avg_score = np.mean(scores[-100:])
                print(f"Episode {episode}, Average Score: {avg_score:.2f}")
        
        training_time = (datetime.now() - start_time).total_seconds()
        self.is_trained = True
        
        return {
            'training_time': training_time,
            'scores': scores,
            'final_avg_score': np.mean(scores[-100:]),
            'epsilon_final': self.epsilon
        }

class AIModelManager:
    """Gestor de modelos de IA"""
    
    def __init__(self, models_dir: str = "ai_models"):
        self.models_dir = models_dir
        self.models = {}
        self.model_performance = {}
        
        # Crear directorio si no existe
        import os
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
    
    def train_lstm_model(self, data: pd.DataFrame, target_column: str,
                        sequence_length: int = 60, epochs: int = 100) -> str:
        """Entrenar modelo LSTM"""
        
        logger.info("Entrenando modelo LSTM para predicción de series temporales")
        
        # Preparar datos
        values = data[target_column].values.reshape(-1, 1)
        scaled_values = StandardScaler().fit_transform(values)
        
        # Crear secuencias
        lstm_model = LSTMForecastingModel(sequence_length, 1)
        X, y = lstm_model.prepare_sequences(scaled_values)
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Entrenar modelo
        training_results = lstm_model.train(X_train, y_train, X_test, y_test, epochs=epochs)
        
        # Evaluar modelo
        predictions = lstm_model.predict(X_test)
        
        mae = np.mean(np.abs(predictions - y_test))
        mse = np.mean((predictions - y_test) ** 2)
        rmse = np.sqrt(mse)
        r2 = 1 - (np.sum((y_test - predictions) ** 2) / np.sum((y_test - np.mean(y_test)) ** 2))
        
        # Guardar modelo
        model_name = f"lstm_forecasting_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = f"{self.models_dir}/{model_name}.h5"
        lstm_model.model.save(model_path)
        
        # Guardar información del modelo
        model_info = {
            'model_name': model_name,
            'model_type': AIModelType.LSTM_FORECASTING.value,
            'framework': DeepLearningFramework.TENSORFLOW.value,
            'model_path': model_path,
            'sequence_length': sequence_length,
            'created_at': datetime.now().isoformat(),
            'performance': {
                'mae': mae,
                'mse': mse,
                'rmse': rmse,
                'r2_score': r2,
                'training_time': training_results['training_time']
            }
        }
        
        self.models[model_name] = model_info
        
        logger.info(f"Modelo LSTM {model_name} entrenado. MAE: {mae:.2f}, R²: {r2:.2f}")
        
        return model_name
    
    def train_cnn_model(self, images: np.ndarray, labels: np.ndarray,
                       num_classes: int, epochs: int = 50) -> str:
        """Entrenar modelo CNN"""
        
        logger.info("Entrenando modelo CNN para clasificación de imágenes")
        
        # Preparar datos
        X_train, X_test, y_train, y_test = train_test_split(
            images, labels, test_size=0.2, random_state=42
        )
        
        # Convertir etiquetas a categóricas
        y_train_cat = keras.utils.to_categorical(y_train, num_classes)
        y_test_cat = keras.utils.to_categorical(y_test, num_classes)
        
        # Crear y entrenar modelo
        cnn_model = CNNClassificationModel(num_classes=num_classes)
        training_results = cnn_model.train(
            X_train, y_train_cat, X_test, y_test_cat, epochs=epochs
        )
        
        # Evaluar modelo
        predictions = cnn_model.model.predict(X_test)
        predicted_classes = np.argmax(predictions, axis=1)
        accuracy = np.mean(predicted_classes == y_test)
        
        # Guardar modelo
        model_name = f"cnn_classification_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = f"{self.models_dir}/{model_name}.h5"
        cnn_model.model.save(model_path)
        
        # Guardar información del modelo
        model_info = {
            'model_name': model_name,
            'model_type': AIModelType.CNN_CLASSIFICATION.value,
            'framework': DeepLearningFramework.TENSORFLOW.value,
            'model_path': model_path,
            'num_classes': num_classes,
            'created_at': datetime.now().isoformat(),
            'performance': {
                'accuracy': accuracy,
                'training_time': training_results['training_time']
            }
        }
        
        self.models[model_name] = model_info
        
        logger.info(f"Modelo CNN {model_name} entrenado. Accuracy: {accuracy:.2f}")
        
        return model_name
    
    def train_transformer_model(self, data: pd.DataFrame, target_column: str,
                               epochs: int = 100) -> str:
        """Entrenar modelo Transformer"""
        
        logger.info("Entrenar modelo Transformer para predicción avanzada")
        
        # Preparar datos
        feature_columns = [col for col in data.columns if col != target_column]
        X = data[feature_columns].values
        y = data[target_column].values
        
        # Escalar características
        scaler_X = StandardScaler()
        scaler_y = StandardScaler()
        
        X_scaled = scaler_X.fit_transform(X)
        y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_scaled, test_size=0.2, random_state=42
        )
        
        # Crear y entrenar modelo
        transformer_model = TransformerPredictionModel()
        training_results = transformer_model.train(
            X_train, y_train, X_test, y_test, epochs=epochs
        )
        
        # Evaluar modelo
        predictions_scaled = transformer_model.model.predict(X_test)
        predictions = scaler_y.inverse_transform(predictions_scaled.reshape(-1, 1)).flatten()
        y_test_original = scaler_y.inverse_transform(y_test.reshape(-1, 1)).flatten()
        
        mae = np.mean(np.abs(predictions - y_test_original))
        mse = np.mean((predictions - y_test_original) ** 2)
        rmse = np.sqrt(mse)
        r2 = 1 - (np.sum((y_test_original - predictions) ** 2) / 
                 np.sum((y_test_original - np.mean(y_test_original)) ** 2))
        
        # Guardar modelo
        model_name = f"transformer_prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = f"{self.models_dir}/{model_name}.h5"
        transformer_model.model.save(model_path)
        
        # Guardar scalers
        joblib.dump(scaler_X, f"{self.models_dir}/{model_name}_scaler_X.joblib")
        joblib.dump(scaler_y, f"{self.models_dir}/{model_name}_scaler_y.joblib")
        
        # Guardar información del modelo
        model_info = {
            'model_name': model_name,
            'model_type': AIModelType.TRANSFORMER_PREDICTION.value,
            'framework': DeepLearningFramework.TENSORFLOW.value,
            'model_path': model_path,
            'feature_columns': feature_columns,
            'created_at': datetime.now().isoformat(),
            'performance': {
                'mae': mae,
                'mse': mse,
                'rmse': rmse,
                'r2_score': r2,
                'training_time': training_results['training_time']
            }
        }
        
        self.models[model_name] = model_info
        
        logger.info(f"Modelo Transformer {model_name} entrenado. MAE: {mae:.2f}, R²: {r2:.2f}")
        
        return model_name
    
    def generate_synthetic_data(self, real_data: np.ndarray, num_samples: int = 1000) -> np.ndarray:
        """Generar datos sintéticos usando GAN"""
        
        logger.info("Generando datos sintéticos usando GAN")
        
        # Crear y entrenar GAN
        gan = GANSyntheticDataGenerator(data_dim=real_data.shape[1])
        training_results = gan.train(real_data, epochs=500)
        
        # Generar datos sintéticos
        synthetic_data = gan.generate_synthetic_data(num_samples)
        
        logger.info(f"Datos sintéticos generados: {num_samples} muestras")
        
        return synthetic_data
    
    def get_model_performance_summary(self) -> Dict[str, Any]:
        """Obtener resumen del rendimiento de todos los modelos de IA"""
        
        summary = {
            'total_models': len(self.models),
            'models': {},
            'best_performing_model': None,
            'average_performance': {},
            'model_types': {}
        }
        
        if not self.models:
            return summary
        
        # Agrupar por tipo de modelo
        for model_name, model_info in self.models.items():
            model_type = model_info['model_type']
            if model_type not in summary['model_types']:
                summary['model_types'][model_type] = 0
            summary['model_types'][model_type] += 1
        
        # Calcular métricas promedio
        mae_scores = []
        r2_scores = []
        accuracies = []
        
        for model_name, model_info in self.models.items():
            performance = model_info.get('performance', {})
            summary['models'][model_name] = {
                'model_type': model_info['model_type'],
                'framework': model_info['framework'],
                'created_at': model_info['created_at'],
                'performance': performance
            }
            
            if 'mae' in performance:
                mae_scores.append(performance['mae'])
            if 'r2_score' in performance:
                r2_scores.append(performance['r2_score'])
            if 'accuracy' in performance:
                accuracies.append(performance['accuracy'])
        
        # Calcular promedios
        if mae_scores:
            summary['average_performance']['mae'] = np.mean(mae_scores)
        if r2_scores:
            summary['average_performance']['r2_score'] = np.mean(r2_scores)
        if accuracies:
            summary['average_performance']['accuracy'] = np.mean(accuracies)
        
        # Encontrar mejor modelo
        if mae_scores:
            best_model = min(self.models.keys(), 
                            key=lambda x: self.models[x]['performance'].get('mae', float('inf')))
            summary['best_performing_model'] = best_model
        
        return summary

# Instancia global del gestor de IA
ai_manager = AIModelManager()

# Funciones de conveniencia
def train_lstm_model(data: pd.DataFrame, target_column: str) -> str:
    """Entrenar modelo LSTM"""
    return ai_manager.train_lstm_model(data, target_column)

def train_transformer_model(data: pd.DataFrame, target_column: str) -> str:
    """Entrenar modelo Transformer"""
    return ai_manager.train_transformer_model(data, target_column)

def generate_synthetic_data(real_data: np.ndarray, num_samples: int = 1000) -> np.ndarray:
    """Generar datos sintéticos"""
    return ai_manager.generate_synthetic_data(real_data, num_samples)

if __name__ == "__main__":
    # Ejemplo de uso
    logger.info("Probando sistema de IA avanzado...")
    
    # Crear datos de ejemplo para LSTM
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    
    df = pd.DataFrame({
        'date': dates,
        'quantity': np.random.poisson(50, len(dates)) + np.sin(np.arange(len(dates)) * 2 * np.pi / 365) * 10,
        'price': np.random.normal(100, 10, len(dates)),
        'category': np.random.choice(['A', 'B', 'C'], len(dates))
    })
    
    # Entrenar modelo LSTM
    try:
        lstm_model_name = train_lstm_model(df, 'quantity')
        print(f"✅ Modelo LSTM entrenado: {lstm_model_name}")
    except Exception as e:
        print(f"⚠️ Error entrenando LSTM: {e}")
    
    # Entrenar modelo Transformer
    try:
        transformer_model_name = train_transformer_model(df, 'quantity')
        print(f"✅ Modelo Transformer entrenado: {transformer_model_name}")
    except Exception as e:
        print(f"⚠️ Error entrenando Transformer: {e}")
    
    # Generar datos sintéticos
    try:
        real_data = df[['quantity', 'price']].values
        synthetic_data = generate_synthetic_data(real_data, 100)
        print(f"✅ Datos sintéticos generados: {synthetic_data.shape}")
    except Exception as e:
        print(f"⚠️ Error generando datos sintéticos: {e}")
    
    # Resumen de rendimiento
    summary = ai_manager.get_model_performance_summary()
    print(f"📊 Resumen de modelos de IA: {summary['total_models']} modelos entrenados")
    
    print("✅ Sistema de IA avanzado funcionando")



