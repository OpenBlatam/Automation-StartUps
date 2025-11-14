#!/usr/bin/env python3
"""
AI-Powered Affiliate Neural Network System
Advanced neural network implementation for affiliate marketing optimization
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, callbacks
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class AffiliateNeuralNetwork:
    """Advanced neural network system for affiliate marketing optimization"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.models = {}
        self.history = {}
        
    def create_affiliate_prediction_model(self, input_shape, num_classes):
        """Create advanced neural network for affiliate performance prediction"""
        model = models.Sequential([
            # Input layer
            layers.Dense(512, activation='relu', input_shape=(input_shape,)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Hidden layers
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            # Output layer
            layers.Dense(num_classes, activation='softmax')
        ])
        
        # Compile model
        model.compile(
            optimizer=optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        return model
    
    def create_commission_optimization_model(self, input_shape):
        """Create neural network for commission rate optimization"""
        model = models.Sequential([
            layers.Dense(256, activation='relu', input_shape=(input_shape,)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            layers.Dense(32, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            layers.Dense(1, activation='sigmoid')  # Commission rate between 0 and 1
        ])
        
        model.compile(
            optimizer=optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae', 'mse']
        )
        
        return model
    
    def create_conversion_prediction_model(self, input_shape):
        """Create LSTM model for conversion prediction"""
        model = models.Sequential([
            layers.LSTM(128, return_sequences=True, input_shape=(input_shape, 1)),
            layers.Dropout(0.3),
            
            layers.LSTM(64, return_sequences=True),
            layers.Dropout(0.3),
            
            layers.LSTM(32),
            layers.Dropout(0.3),
            
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        return model
    
    def create_affiliate_segmentation_model(self, input_shape, num_segments):
        """Create autoencoder for affiliate segmentation"""
        # Encoder
        encoder = models.Sequential([
            layers.Dense(256, activation='relu', input_shape=(input_shape,)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            layers.Dense(32, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            layers.Dense(num_segments, activation='softmax')
        ])
        
        # Decoder
        decoder = models.Sequential([
            layers.Dense(32, activation='relu', input_shape=(num_segments,)),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(input_shape, activation='sigmoid')
        ])
        
        # Autoencoder
        autoencoder = models.Sequential([encoder, decoder])
        autoencoder.compile(
            optimizer=optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return autoencoder, encoder, decoder
    
    def prepare_data(self, data, target_column=None, is_sequence=False):
        """Prepare data for neural network training"""
        # Handle missing values
        data = data.fillna(data.mean())
        
        # Encode categorical variables
        categorical_columns = data.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if col != target_column:
                le = LabelEncoder()
                data[col] = le.fit_transform(data[col].astype(str))
                self.label_encoders[col] = le
        
        if target_column and target_column in data.columns:
            # Separate features and target
            X = data.drop(columns=[target_column])
            y = data[target_column]
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            if is_sequence:
                # Reshape for LSTM
                X_scaled = X_scaled.reshape(X_scaled.shape[0], X_scaled.shape[1], 1)
            
            return X_scaled, y
        else:
            # Scale all features
            X_scaled = self.scaler.fit_transform(data)
            
            if is_sequence:
                X_scaled = X_scaled.reshape(X_scaled.shape[0], X_scaled.shape[1], 1)
            
            return X_scaled
    
    def train_model(self, model, X_train, y_train, X_val, y_val, model_name, epochs=100):
        """Train neural network model"""
        # Callbacks
        callbacks_list = [
            callbacks.EarlyStopping(patience=10, restore_best_weights=True),
            callbacks.ReduceLROnPlateau(factor=0.5, patience=5),
            callbacks.ModelCheckpoint(f'{model_name}_best.h5', save_best_only=True)
        ]
        
        # Train model
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=32,
            callbacks=callbacks_list,
            verbose=1
        )
        
        self.history[model_name] = history
        return history
    
    def predict_affiliate_performance(self, affiliate_data):
        """Predict affiliate performance using neural network"""
        if 'affiliate_prediction' not in self.models:
            raise ValueError("Model not trained. Please train the model first.")
        
        # Prepare data
        X = self.prepare_data(affiliate_data)
        
        # Make predictions
        predictions = self.models['affiliate_prediction'].predict(X)
        
        return predictions
    
    def optimize_commission_rates(self, affiliate_data):
        """Optimize commission rates using neural network"""
        if 'commission_optimization' not in self.models:
            raise ValueError("Model not trained. Please train the model first.")
        
        # Prepare data
        X = self.prepare_data(affiliate_data)
        
        # Make predictions
        optimal_rates = self.models['commission_optimization'].predict(X)
        
        return optimal_rates
    
    def predict_conversions(self, sequence_data):
        """Predict conversions using LSTM model"""
        if 'conversion_prediction' not in self.models:
            raise ValueError("Model not trained. Please train the model first.")
        
        # Prepare data
        X = self.prepare_data(sequence_data, is_sequence=True)
        
        # Make predictions
        predictions = self.models['conversion_prediction'].predict(X)
        
        return predictions
    
    def segment_affiliates(self, affiliate_data, num_segments=5):
        """Segment affiliates using autoencoder"""
        if 'affiliate_segmentation' not in self.models:
            raise ValueError("Model not trained. Please train the model first.")
        
        # Prepare data
        X = self.prepare_data(affiliate_data)
        
        # Get segment predictions
        segments = self.models['affiliate_segmentation'].predict(X)
        
        return segments
    
    def plot_training_history(self, model_name):
        """Plot training history for a model"""
        if model_name not in self.history:
            raise ValueError(f"No training history found for {model_name}")
        
        history = self.history[model_name]
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Loss
        axes[0, 0].plot(history.history['loss'], label='Training Loss')
        axes[0, 0].plot(history.history['val_loss'], label='Validation Loss')
        axes[0, 0].set_title('Model Loss')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        
        # Accuracy
        axes[0, 1].plot(history.history['accuracy'], label='Training Accuracy')
        axes[0, 1].plot(history.history['val_accuracy'], label='Validation Accuracy')
        axes[0, 1].set_title('Model Accuracy')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Accuracy')
        axes[0, 1].legend()
        
        # Precision
        axes[1, 0].plot(history.history['precision'], label='Training Precision')
        axes[1, 0].plot(history.history['val_precision'], label='Validation Precision')
        axes[1, 0].set_title('Model Precision')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Precision')
        axes[1, 0].legend()
        
        # Recall
        axes[1, 1].plot(history.history['recall'], label='Training Recall')
        axes[1, 1].plot(history.history['val_recall'], label='Validation Recall')
        axes[1, 1].set_title('Model Recall')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Recall')
        axes[1, 1].legend()
        
        plt.tight_layout()
        plt.show()
    
    def evaluate_model(self, model, X_test, y_test, model_name):
        """Evaluate model performance"""
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        if model_name == 'affiliate_prediction':
            # Classification metrics
            y_pred_classes = np.argmax(y_pred, axis=1)
            y_test_classes = np.argmax(y_test, axis=1)
            
            print(f"\n{model_name} Performance:")
            print(classification_report(y_test_classes, y_pred_classes))
            
            # Confusion matrix
            cm = confusion_matrix(y_test_classes, y_pred_classes)
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
            plt.title(f'{model_name} Confusion Matrix')
            plt.xlabel('Predicted')
            plt.ylabel('Actual')
            plt.show()
            
        else:
            # Regression metrics
            mse = np.mean((y_test - y_pred) ** 2)
            mae = np.mean(np.abs(y_test - y_pred))
            rmse = np.sqrt(mse)
            
            print(f"\n{model_name} Performance:")
            print(f"MSE: {mse:.4f}")
            print(f"MAE: {mae:.4f}")
            print(f"RMSE: {rmse:.4f}")
    
    def save_model(self, model, model_name):
        """Save trained model"""
        model.save(f'{model_name}_model.h5')
        print(f"Model {model_name} saved successfully!")
    
    def load_model(self, model_name):
        """Load trained model"""
        model = tf.keras.models.load_model(f'{model_name}_model.h5')
        self.models[model_name] = model
        print(f"Model {model_name} loaded successfully!")
        return model

def main():
    """Main function to demonstrate the neural network system"""
    print("AI-Powered Affiliate Neural Network System")
    print("=" * 50)
    
    # Initialize system
    nn_system = AffiliateNeuralNetwork()
    
    # Generate sample data
    np.random.seed(42)
    n_samples = 1000
    
    # Sample affiliate data
    affiliate_data = pd.DataFrame({
        'affiliate_id': range(n_samples),
        'traffic_volume': np.random.normal(1000, 300, n_samples),
        'conversion_rate': np.random.beta(2, 8, n_samples),
        'avg_order_value': np.random.normal(50, 15, n_samples),
        'geographic_region': np.random.choice(['US', 'EU', 'APAC', 'LATAM'], n_samples),
        'industry': np.random.choice(['Tech', 'E-commerce', 'Finance', 'Health'], n_samples),
        'social_media_followers': np.random.poisson(10000, n_samples),
        'email_list_size': np.random.poisson(5000, n_samples),
        'years_experience': np.random.randint(1, 10, n_samples),
        'performance_score': np.random.normal(75, 20, n_samples)
    })
    
    # Create performance categories
    affiliate_data['performance_category'] = pd.cut(
        affiliate_data['performance_score'],
        bins=[0, 50, 70, 85, 100],
        labels=['Low', 'Medium', 'High', 'Excellent']
    )
    
    print("Sample Data Generated:")
    print(affiliate_data.head())
    print(f"\nData Shape: {affiliate_data.shape}")
    
    # Prepare data for different models
    print("\nPreparing data for neural network training...")
    
    # 1. Affiliate Performance Prediction
    print("\n1. Training Affiliate Performance Prediction Model...")
    X_perf, y_perf = nn_system.prepare_data(
        affiliate_data, 
        target_column='performance_category'
    )
    
    # Encode target variable
    le_perf = LabelEncoder()
    y_perf_encoded = to_categorical(le_perf.fit_transform(y_perf))
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_perf, y_perf_encoded, test_size=0.2, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42
    )
    
    # Create and train model
    perf_model = nn_system.create_affiliate_prediction_model(
        X_train.shape[1], y_perf_encoded.shape[1]
    )
    nn_system.models['affiliate_prediction'] = perf_model
    
    # Train model
    history = nn_system.train_model(
        perf_model, X_train, y_train, X_val, y_val, 'affiliate_prediction', epochs=50
    )
    
    # Evaluate model
    nn_system.evaluate_model(perf_model, X_test, y_test, 'affiliate_prediction')
    
    # 2. Commission Rate Optimization
    print("\n2. Training Commission Rate Optimization Model...")
    X_comm, y_comm = nn_system.prepare_data(
        affiliate_data, 
        target_column='conversion_rate'
    )
    
    # Split data
    X_train_comm, X_test_comm, y_train_comm, y_test_comm = train_test_split(
        X_comm, y_comm, test_size=0.2, random_state=42
    )
    X_train_comm, X_val_comm, y_train_comm, y_val_comm = train_test_split(
        X_train_comm, y_train_comm, test_size=0.2, random_state=42
    )
    
    # Create and train model
    comm_model = nn_system.create_commission_optimization_model(X_train_comm.shape[1])
    nn_system.models['commission_optimization'] = comm_model
    
    # Train model
    history_comm = nn_system.train_model(
        comm_model, X_train_comm, y_train_comm, X_val_comm, y_val_comm, 
        'commission_optimization', epochs=50
    )
    
    # Evaluate model
    nn_system.evaluate_model(comm_model, X_test_comm, y_test_comm, 'commission_optimization')
    
    # 3. Conversion Prediction (LSTM)
    print("\n3. Training Conversion Prediction Model...")
    X_conv, y_conv = nn_system.prepare_data(
        affiliate_data, 
        target_column='conversion_rate',
        is_sequence=True
    )
    
    # Split data
    X_train_conv, X_test_conv, y_train_conv, y_test_conv = train_test_split(
        X_conv, y_conv, test_size=0.2, random_state=42
    )
    X_train_conv, X_val_conv, y_train_conv, y_val_conv = train_test_split(
        X_train_conv, y_train_conv, test_size=0.2, random_state=42
    )
    
    # Create and train model
    conv_model = nn_system.create_conversion_prediction_model(X_train_conv.shape[1])
    nn_system.models['conversion_prediction'] = conv_model
    
    # Train model
    history_conv = nn_system.train_model(
        conv_model, X_train_conv, y_train_conv, X_val_conv, y_val_conv, 
        'conversion_prediction', epochs=50
    )
    
    # Evaluate model
    nn_system.evaluate_model(conv_model, X_test_conv, y_test_conv, 'conversion_prediction')
    
    # 4. Affiliate Segmentation
    print("\n4. Training Affiliate Segmentation Model...")
    X_seg = nn_system.prepare_data(affiliate_data)
    
    # Split data
    X_train_seg, X_test_seg = train_test_split(X_seg, test_size=0.2, random_state=42)
    X_train_seg, X_val_seg = train_test_split(X_train_seg, test_size=0.2, random_state=42)
    
    # Create and train model
    autoencoder, encoder, decoder = nn_system.create_affiliate_segmentation_model(
        X_train_seg.shape[1], 5
    )
    nn_system.models['affiliate_segmentation'] = autoencoder
    
    # Train model
    history_seg = nn_system.train_model(
        autoencoder, X_train_seg, X_train_seg, X_val_seg, X_val_seg, 
        'affiliate_segmentation', epochs=50
    )
    
    # Plot training histories
    print("\nPlotting training histories...")
    nn_system.plot_training_history('affiliate_prediction')
    nn_system.plot_training_history('commission_optimization')
    nn_system.plot_training_history('conversion_prediction')
    nn_system.plot_training_history('affiliate_segmentation')
    
    # Save models
    print("\nSaving trained models...")
    nn_system.save_model(perf_model, 'affiliate_prediction')
    nn_system.save_model(comm_model, 'commission_optimization')
    nn_system.save_model(conv_model, 'conversion_prediction')
    nn_system.save_model(autoencoder, 'affiliate_segmentation')
    
    print("\nNeural Network System Training Complete!")
    print("All models have been trained and saved successfully.")

if __name__ == "__main__":
    main()
