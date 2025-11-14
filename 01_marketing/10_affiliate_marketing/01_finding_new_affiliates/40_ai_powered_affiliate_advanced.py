#!/usr/bin/env python3
"""
AI-Powered Advanced Affiliate Marketing System
Ultra-advanced AI system with cutting-edge features for affiliate marketing
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, callbacks
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class AdvancedAffiliateAI:
    """Ultra-advanced AI system for affiliate marketing optimization"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.models = {}
        self.history = {}
        self.performance_metrics = {}
        
    def create_transformer_model(self, input_shape, num_classes):
        """Create Transformer model for affiliate analysis"""
        # Input layer
        inputs = layers.Input(shape=(input_shape,))
        
        # Embedding layer
        embedding = layers.Dense(128, activation='relu')(inputs)
        embedding = layers.Dropout(0.1)(embedding)
        
        # Multi-head attention
        attention = layers.MultiHeadAttention(
            num_heads=8, key_dim=64, dropout=0.1
        )(embedding, embedding)
        
        # Add & Norm
        attention = layers.Add()([embedding, attention])
        attention = layers.LayerNormalization()(attention)
        
        # Feed forward
        ffn = layers.Dense(256, activation='relu')(attention)
        ffn = layers.Dropout(0.1)(ffn)
        ffn = layers.Dense(128, activation='relu')(ffn)
        
        # Add & Norm
        ffn = layers.Add()([attention, ffn])
        ffn = layers.LayerNormalization()(ffn)
        
        # Global average pooling
        pooled = layers.GlobalAveragePooling1D()(ffn)
        
        # Classification head
        outputs = layers.Dense(64, activation='relu')(pooled)
        outputs = layers.Dropout(0.3)(outputs)
        outputs = layers.Dense(num_classes, activation='softmax')(outputs)
        
        model = models.Model(inputs, outputs)
        
        # Compile model
        model.compile(
            optimizer=optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        return model
    
    def create_gan_model(self, input_shape, noise_dim=100):
        """Create GAN model for generating synthetic affiliate data"""
        # Generator
        generator = models.Sequential([
            layers.Dense(256, activation='relu', input_shape=(noise_dim,)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(1024, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(input_shape, activation='tanh')
        ])
        
        # Discriminator
        discriminator = models.Sequential([
            layers.Dense(512, activation='relu', input_shape=(input_shape,)),
            layers.Dropout(0.3),
            
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            
            layers.Dense(1, activation='sigmoid')
        ])
        
        # Compile discriminator
        discriminator.compile(
            optimizer=optimizers.Adam(learning_rate=0.0002),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        # GAN
        gan_input = layers.Input(shape=(noise_dim,))
        generated_data = generator(gan_input)
        gan_output = discriminator(generated_data)
        
        gan = models.Model(gan_input, gan_output)
        gan.compile(
            optimizer=optimizers.Adam(learning_rate=0.0002),
            loss='binary_crossentropy'
        )
        
        return generator, discriminator, gan
    
    def create_reinforcement_learning_model(self, state_size, action_size):
        """Create DQN model for reinforcement learning"""
        model = models.Sequential([
            layers.Dense(128, activation='relu', input_shape=(state_size,)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(32, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            layers.Dense(action_size, activation='linear')
        ])
        
        model.compile(
            optimizer=optimizers.Adam(learning_rate=0.001),
            loss='mse'
        )
        
        return model
    
    def create_attention_model(self, input_shape, num_classes):
        """Create attention-based model for affiliate analysis"""
        # Input layer
        inputs = layers.Input(shape=(input_shape,))
        
        # Embedding
        embedding = layers.Dense(128, activation='relu')(inputs)
        embedding = layers.Dropout(0.1)(embedding)
        
        # Self-attention
        attention = layers.MultiHeadAttention(
            num_heads=4, key_dim=32, dropout=0.1
        )(embedding, embedding)
        
        # Add & Norm
        attention = layers.Add()([embedding, attention])
        attention = layers.LayerNormalization()(attention)
        
        # Global attention pooling
        attention_weights = layers.Dense(1, activation='softmax')(attention)
        pooled = layers.Multiply()([attention, attention_weights])
        pooled = layers.GlobalAveragePooling1D()(pooled)
        
        # Classification head
        outputs = layers.Dense(64, activation='relu')(pooled)
        outputs = layers.Dropout(0.3)(outputs)
        outputs = layers.Dense(num_classes, activation='softmax')(outputs)
        
        model = models.Model(inputs, outputs)
        
        # Compile model
        model.compile(
            optimizer=optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        return model
    
    def create_ensemble_model(self, input_shape, num_classes):
        """Create ensemble model combining multiple architectures"""
        # Model 1: Dense network
        dense_input = layers.Input(shape=(input_shape,), name='dense_input')
        dense = layers.Dense(256, activation='relu')(dense_input)
        dense = layers.BatchNormalization()(dense)
        dense = layers.Dropout(0.3)(dense)
        dense = layers.Dense(128, activation='relu')(dense)
        dense = layers.BatchNormalization()(dense)
        dense = layers.Dropout(0.3)(dense)
        dense = layers.Dense(64, activation='relu')(dense)
        dense = layers.Dropout(0.2)(dense)
        dense_output = layers.Dense(num_classes, activation='softmax')(dense)
        
        # Model 2: LSTM
        lstm_input = layers.Input(shape=(input_shape, 1), name='lstm_input')
        lstm = layers.LSTM(128, return_sequences=True)(lstm_input)
        lstm = layers.Dropout(0.3)(lstm)
        lstm = layers.LSTM(64)(lstm)
        lstm = layers.Dropout(0.3)(lstm)
        lstm = layers.Dense(64, activation='relu')(lstm)
        lstm = layers.Dropout(0.2)(lstm)
        lstm_output = layers.Dense(num_classes, activation='softmax')(lstm)
        
        # Model 3: CNN
        cnn_input = layers.Input(shape=(input_shape, 1), name='cnn_input')
        cnn = layers.Conv1D(64, 3, activation='relu')(cnn_input)
        cnn = layers.BatchNormalization()(cnn)
        cnn = layers.Dropout(0.3)(cnn)
        cnn = layers.Conv1D(128, 3, activation='relu')(cnn)
        cnn = layers.BatchNormalization()(cnn)
        cnn = layers.Dropout(0.3)(cnn)
        cnn = layers.GlobalMaxPooling1D()(cnn)
        cnn = layers.Dense(64, activation='relu')(cnn)
        cnn = layers.Dropout(0.2)(cnn)
        cnn_output = layers.Dense(num_classes, activation='softmax')(cnn)
        
        # Ensemble
        ensemble = layers.Average()([dense_output, lstm_output, cnn_output])
        
        model = models.Model(
            inputs=[dense_input, lstm_input, cnn_input],
            outputs=ensemble
        )
        
        # Compile model
        model.compile(
            optimizer=optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        return model
    
    def create_autoencoder_model(self, input_shape, encoding_dim=32):
        """Create autoencoder for anomaly detection"""
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
            
            layers.Dense(encoding_dim, activation='relu')
        ])
        
        # Decoder
        decoder = models.Sequential([
            layers.Dense(64, activation='relu', input_shape=(encoding_dim,)),
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
                # Reshape for LSTM/CNN
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
            callbacks.EarlyStopping(patience=15, restore_best_weights=True),
            callbacks.ReduceLROnPlateau(factor=0.5, patience=7),
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
    
    def train_gan(self, generator, discriminator, gan, real_data, epochs=1000, batch_size=32):
        """Train GAN model"""
        real_labels = np.ones((batch_size, 1))
        fake_labels = np.zeros((batch_size, 1))
        
        for epoch in range(epochs):
            # Train discriminator
            idx = np.random.randint(0, real_data.shape[0], batch_size)
            real_batch = real_data[idx]
            
            noise = np.random.normal(0, 1, (batch_size, 100))
            fake_batch = generator.predict(noise)
            
            d_loss_real = discriminator.train_on_batch(real_batch, real_labels)
            d_loss_fake = discriminator.train_on_batch(fake_batch, fake_labels)
            d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)
            
            # Train generator
            noise = np.random.normal(0, 1, (batch_size, 100))
            g_loss = gan.train_on_batch(noise, real_labels)
            
            if epoch % 100 == 0:
                print(f"Epoch {epoch}, D Loss: {d_loss[0]:.4f}, G Loss: {g_loss:.4f}")
    
    def predict_affiliate_performance(self, affiliate_data):
        """Predict affiliate performance using advanced models"""
        if 'transformer' not in self.models:
            raise ValueError("Model not trained. Please train the model first.")
        
        # Prepare data
        X = self.prepare_data(affiliate_data)
        
        # Make predictions
        predictions = self.models['transformer'].predict(X)
        
        return predictions
    
    def generate_synthetic_data(self, num_samples=1000):
        """Generate synthetic affiliate data using GAN"""
        if 'gan' not in self.models:
            raise ValueError("GAN model not trained. Please train the model first.")
        
        noise = np.random.normal(0, 1, (num_samples, 100))
        synthetic_data = self.models['gan'].predict(noise)
        
        return synthetic_data
    
    def detect_anomalies(self, affiliate_data, threshold=0.1):
        """Detect anomalies using autoencoder"""
        if 'autoencoder' not in self.models:
            raise ValueError("Autoencoder model not trained. Please train the model first.")
        
        # Prepare data
        X = self.prepare_data(affiliate_data)
        
        # Reconstruct data
        reconstructed = self.models['autoencoder'].predict(X)
        
        # Calculate reconstruction error
        reconstruction_error = np.mean(np.square(X - reconstructed), axis=1)
        
        # Identify anomalies
        anomalies = reconstruction_error > threshold
        
        return anomalies, reconstruction_error
    
    def optimize_affiliate_strategy(self, state):
        """Optimize affiliate strategy using reinforcement learning"""
        if 'rl_model' not in self.models:
            raise ValueError("RL model not trained. Please train the model first.")
        
        # Predict Q-values for all actions
        q_values = self.models['rl_model'].predict(state.reshape(1, -1))
        
        # Select best action
        best_action = np.argmax(q_values[0])
        
        return best_action, q_values[0]
    
    def plot_model_performance(self, model_name):
        """Plot model performance metrics"""
        if model_name not in self.history:
            raise ValueError(f"No training history found for {model_name}")
        
        history = self.history[model_name]
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Loss
        axes[0, 0].plot(history.history['loss'], label='Training Loss')
        axes[0, 0].plot(history.history['val_loss'], label='Validation Loss')
        axes[0, 0].set_title(f'{model_name} - Model Loss')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        
        # Accuracy
        axes[0, 1].plot(history.history['accuracy'], label='Training Accuracy')
        axes[0, 1].plot(history.history['val_accuracy'], label='Validation Accuracy')
        axes[0, 1].set_title(f'{model_name} - Model Accuracy')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Accuracy')
        axes[0, 1].legend()
        
        # Precision
        axes[1, 0].plot(history.history['precision'], label='Training Precision')
        axes[1, 0].plot(history.history['val_precision'], label='Validation Precision')
        axes[1, 0].set_title(f'{model_name} - Model Precision')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Precision')
        axes[1, 0].legend()
        
        # Recall
        axes[1, 1].plot(history.history['recall'], label='Training Recall')
        axes[1, 1].plot(history.history['val_recall'], label='Validation Recall')
        axes[1, 1].set_title(f'{model_name} - Model Recall')
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
        if 'categorical_crossentropy' in model.loss:
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
    """Main function to demonstrate the advanced AI system"""
    print("AI-Powered Advanced Affiliate Marketing System")
    print("=" * 60)
    
    # Initialize system
    ai_system = AdvancedAffiliateAI()
    
    # Generate sample data
    np.random.seed(42)
    n_samples = 2000
    
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
        'performance_score': np.random.normal(75, 20, n_samples),
        'engagement_rate': np.random.beta(3, 7, n_samples),
        'click_through_rate': np.random.beta(2, 8, n_samples),
        'bounce_rate': np.random.beta(3, 7, n_samples),
        'time_on_site': np.random.normal(120, 30, n_samples),
        'pages_per_session': np.random.poisson(3, n_samples)
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
    print("\nPreparing data for advanced AI training...")
    
    # 1. Transformer Model
    print("\n1. Training Transformer Model...")
    X_trans, y_trans = ai_system.prepare_data(
        affiliate_data, 
        target_column='performance_category'
    )
    
    # Encode target variable
    le_trans = LabelEncoder()
    y_trans_encoded = tf.keras.utils.to_categorical(le_trans.fit_transform(y_trans))
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_trans, y_trans_encoded, test_size=0.2, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42
    )
    
    # Create and train model
    transformer_model = ai_system.create_transformer_model(
        X_train.shape[1], y_trans_encoded.shape[1]
    )
    ai_system.models['transformer'] = transformer_model
    
    # Train model
    history = ai_system.train_model(
        transformer_model, X_train, y_train, X_val, y_val, 'transformer', epochs=50
    )
    
    # Evaluate model
    ai_system.evaluate_model(transformer_model, X_test, y_test, 'transformer')
    
    # 2. GAN Model
    print("\n2. Training GAN Model...")
    X_gan = ai_system.prepare_data(affiliate_data)
    
    # Create and train GAN
    generator, discriminator, gan = ai_system.create_gan_model(X_gan.shape[1])
    ai_system.models['generator'] = generator
    ai_system.models['discriminator'] = discriminator
    ai_system.models['gan'] = gan
    
    # Train GAN
    ai_system.train_gan(generator, discriminator, gan, X_gan, epochs=500)
    
    # 3. Attention Model
    print("\n3. Training Attention Model...")
    attention_model = ai_system.create_attention_model(
        X_train.shape[1], y_trans_encoded.shape[1]
    )
    ai_system.models['attention'] = attention_model
    
    # Train model
    history_att = ai_system.train_model(
        attention_model, X_train, y_train, X_val, y_val, 'attention', epochs=50
    )
    
    # Evaluate model
    ai_system.evaluate_model(attention_model, X_test, y_test, 'attention')
    
    # 4. Ensemble Model
    print("\n4. Training Ensemble Model...")
    ensemble_model = ai_system.create_ensemble_model(
        X_train.shape[1], y_trans_encoded.shape[1]
    )
    ai_system.models['ensemble'] = ensemble_model
    
    # Prepare data for ensemble (multiple input formats)
    X_train_dense = X_train
    X_train_lstm = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
    X_train_cnn = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
    
    X_test_dense = X_test
    X_test_lstm = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)
    X_test_cnn = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)
    
    X_val_dense = X_val
    X_val_lstm = X_val.reshape(X_val.shape[0], X_val.shape[1], 1)
    X_val_cnn = X_val.reshape(X_val.shape[0], X_val.shape[1], 1)
    
    # Train ensemble
    history_ens = ensemble_model.fit(
        [X_train_dense, X_train_lstm, X_train_cnn], y_train,
        validation_data=([X_val_dense, X_val_lstm, X_val_cnn], y_val),
        epochs=50, batch_size=32, verbose=1
    )
    
    # Evaluate ensemble
    ensemble_pred = ensemble_model.predict([X_test_dense, X_test_lstm, X_test_cnn])
    ensemble_pred_classes = np.argmax(ensemble_pred, axis=1)
    y_test_classes = np.argmax(y_test, axis=1)
    
    print("\nEnsemble Model Performance:")
    print(classification_report(y_test_classes, ensemble_pred_classes))
    
    # 5. Autoencoder for Anomaly Detection
    print("\n5. Training Autoencoder for Anomaly Detection...")
    autoencoder, encoder, decoder = ai_system.create_autoencoder_model(X_gan.shape[1])
    ai_system.models['autoencoder'] = autoencoder
    
    # Train autoencoder
    history_ae = autoencoder.fit(
        X_gan, X_gan,
        epochs=50, batch_size=32, validation_split=0.2, verbose=1
    )
    
    # Detect anomalies
    anomalies, reconstruction_error = ai_system.detect_anomalies(affiliate_data)
    print(f"\nAnomalies detected: {np.sum(anomalies)} out of {len(anomalies)}")
    
    # 6. Reinforcement Learning Model
    print("\n6. Training Reinforcement Learning Model...")
    state_size = X_train.shape[1]
    action_size = 4  # 4 different strategies
    
    rl_model = ai_system.create_reinforcement_learning_model(state_size, action_size)
    ai_system.models['rl_model'] = rl_model
    
    # Simulate RL training (simplified)
    for episode in range(100):
        state = X_train[np.random.randint(0, len(X_train))]
        action, q_values = ai_system.optimize_affiliate_strategy(state)
        # Simulate reward based on performance
        reward = np.random.normal(0, 1)
        
        # Update Q-values (simplified)
        target = reward + 0.95 * np.max(q_values)
        target_f = q_values.copy()
        target_f[action] = target
        
        rl_model.fit(state.reshape(1, -1), target_f.reshape(1, -1), epochs=1, verbose=0)
    
    print("Reinforcement Learning training completed!")
    
    # Plot training histories
    print("\nPlotting training histories...")
    ai_system.plot_model_performance('transformer')
    ai_system.plot_model_performance('attention')
    
    # Save models
    print("\nSaving trained models...")
    ai_system.save_model(transformer_model, 'transformer')
    ai_system.save_model(attention_model, 'attention')
    ai_system.save_model(ensemble_model, 'ensemble')
    ai_system.save_model(autoencoder, 'autoencoder')
    ai_system.save_model(rl_model, 'rl_model')
    
    print("\nAdvanced AI System Training Complete!")
    print("All models have been trained and saved successfully.")
    
    # Generate synthetic data
    print("\nGenerating synthetic affiliate data...")
    synthetic_data = ai_system.generate_synthetic_data(100)
    print(f"Generated {len(synthetic_data)} synthetic samples")

if __name__ == "__main__":
    main()
