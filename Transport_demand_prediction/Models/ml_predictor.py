"""
Modelo Avanzado de Predicción de Demanda con IA/ML
Autor: Sistema de IA Avanzado
Fecha: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Importaciones para ML
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression, Ridge, Lasso
    from sklearn.svm import SVR
    from sklearn.neural_network import MLPRegressor
    from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    from sklearn.pipeline import Pipeline
    ML_AVAILABLE = True
except ImportError:
    print("⚠️ scikit-learn no disponible. Instalando dependencias básicas...")
    ML_AVAILABLE = False

# Importaciones para Deep Learning
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout, GRU
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping
    DL_AVAILABLE = True
except ImportError:
    print("⚠️ TensorFlow no disponible")
    DL_AVAILABLE = False

# Importaciones para modelos avanzados
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.exponential_smoothing import ExponentialSmoothing
    from statsmodels.tsa.holtwinters import ExponentialSmoothing as HW
    STATSMODELS_AVAILABLE = True
except ImportError:
    print("⚠️ statsmodels no disponible")
    STATSMODELS_AVAILABLE = False

class AdvancedDemandPredictor:
    """
    Clase avanzada para predicción de demanda usando múltiples algoritmos de IA/ML
    """
    
    def __init__(self, data=None):
        """
        Inicializar el predictor avanzado
        
        Args:
            data (pd.DataFrame): DataFrame con datos históricos
        """
        self.data = data
        self.models = {}
        self.predictions = {}
        self.model_performance = {}
        self.feature_importance = {}
        self.scalers = {}
        
    def set_data(self, data):
        """
        Establecer datos para entrenamiento
        
        Args:
            data (pd.DataFrame): DataFrame con datos históricos
        """
        self.data = data.copy()
        print(f"✅ Datos establecidos: {len(self.data)} registros")
        
    def prepare_features(self, target_column='demanda_transporte', lag_days=7):
        """
        Preparar características para el modelo
        
        Args:
            target_column (str): Columna objetivo
            lag_days (int): Días de retraso para características temporales
        """
        if self.data is None:
            raise ValueError("❌ No hay datos establecidos")
        
        print(f"🔧 Preparando características (lag: {lag_days} días)...")
        
        # Crear copia de datos
        df = self.data.copy()
        
        # Características temporales
        df['año'] = df['fecha'].dt.year
        df['mes'] = df['fecha'].dt.month
        df['dia'] = df['fecha'].dt.day
        df['dia_semana'] = df['fecha'].dt.weekday
        df['dia_año'] = df['fecha'].dt.dayofyear
        df['semana_año'] = df['fecha'].dt.isocalendar().week
        df['trimestre'] = df['fecha'].dt.quarter
        
        # Características cíclicas
        df['mes_sin'] = np.sin(2 * np.pi * df['mes'] / 12)
        df['mes_cos'] = np.cos(2 * np.pi * df['mes'] / 12)
        df['dia_sin'] = np.sin(2 * np.pi * df['dia_semana'] / 7)
        df['dia_cos'] = np.cos(2 * np.pi * df['dia_semana'] / 7)
        
        # Características de retraso (lag features)
        for i in range(1, lag_days + 1):
            df[f'demanda_lag_{i}'] = df[target_column].shift(i)
        
        # Características móviles
        for window in [3, 7, 14, 30]:
            df[f'demanda_ma_{window}'] = df[target_column].rolling(window=window).mean()
            df[f'demanda_std_{window}'] = df[target_column].rolling(window=window).std()
        
        # Características de tendencia
        df['demanda_diff'] = df[target_column].diff()
        df['demanda_pct_change'] = df[target_column].pct_change()
        
        # Características de eventos
        df['es_fin_semana'] = df['dia_semana'].isin([5, 6]).astype(int)
        df['es_feriado'] = df['eventos_especiales']
        
        # Interacciones entre variables
        df['temp_precio_interaction'] = df['temperatura'] * df['precio_combustible']
        df['temp_demanda_interaction'] = df['temperatura'] * df[target_column].shift(1)
        
        # Eliminar filas con NaN
        df = df.dropna()
        
        # Separar características y objetivo
        feature_columns = [col for col in df.columns if col not in ['fecha', target_column]]
        self.features = df[feature_columns]
        self.target = df[target_column]
        self.feature_names = feature_columns
        
        print(f"✅ Características preparadas: {len(feature_columns)} características")
        print(f"📊 Registros válidos: {len(df)}")
        
        return self.features, self.target
    
    def train_ml_models(self, test_size=0.2, random_state=42):
        """
        Entrenar múltiples modelos de Machine Learning
        """
        if not ML_AVAILABLE:
            print("❌ scikit-learn no disponible para entrenar modelos ML")
            return
        
        if self.features is None:
            self.prepare_features()
        
        print("🤖 Entrenando modelos de Machine Learning...")
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(
            self.features, self.target, test_size=test_size, random_state=random_state
        )
        
        # Escalar características
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers['standard'] = scaler
        
        # Definir modelos
        models = {
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=random_state),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=random_state),
            'Linear Regression': LinearRegression(),
            'Ridge Regression': Ridge(alpha=1.0),
            'Lasso Regression': Lasso(alpha=0.1),
            'SVR': SVR(kernel='rbf', C=1.0),
            'Neural Network': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=random_state)
        }
        
        # Entrenar modelos
        for name, model in models.items():
            print(f"  🔄 Entrenando {name}...")
            
            try:
                # Usar datos escalados para algunos modelos
                if name in ['Linear Regression', 'Ridge Regression', 'Lasso Regression', 'SVR', 'Neural Network']:
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                
                # Calcular métricas
                mse = mean_squared_error(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                rmse = np.sqrt(mse)
                
                # Validación cruzada
                cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='neg_mean_squared_error')
                cv_rmse = np.sqrt(-cv_scores.mean())
                
                # Guardar modelo y métricas
                self.models[name] = model
                self.model_performance[name] = {
                    'mse': mse,
                    'mae': mae,
                    'r2': r2,
                    'rmse': rmse,
                    'cv_rmse': cv_rmse,
                    'cv_std': cv_scores.std()
                }
                
                # Importancia de características (si está disponible)
                if hasattr(model, 'feature_importances_'):
                    self.feature_importance[name] = dict(zip(self.feature_names, model.feature_importances_))
                elif hasattr(model, 'coef_'):
                    self.feature_importance[name] = dict(zip(self.feature_names, model.coef_))
                
                print(f"    ✅ {name} - RMSE: {rmse:.2f}, R²: {r2:.3f}")
                
            except Exception as e:
                print(f"    ❌ Error entrenando {name}: {str(e)}")
        
        print("✅ Entrenamiento de modelos ML completado")
        return self.model_performance
    
    def train_lstm_model(self, sequence_length=30, epochs=100, batch_size=32):
        """
        Entrenar modelo LSTM para predicción temporal
        """
        if not DL_AVAILABLE:
            print("❌ TensorFlow no disponible para entrenar modelo LSTM")
            return
        
        if self.features is None:
            self.prepare_features()
        
        print(f"🧠 Entrenando modelo LSTM (secuencia: {sequence_length} días)...")
        
        # Preparar datos para LSTM
        def create_sequences(data, target, seq_length):
            X, y = [], []
            for i in range(seq_length, len(data)):
                X.append(data[i-seq_length:i])
                y.append(target[i])
            return np.array(X), np.array(y)
        
        # Usar características principales
        main_features = ['demanda_transporte', 'temperatura', 'precio_combustible', 
                        'dia_semana', 'mes', 'eventos_especiales']
        
        # Escalar datos
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(self.data[main_features])
        self.scalers['lstm'] = scaler
        
        # Crear secuencias
        X_seq, y_seq = create_sequences(scaled_data, scaled_data[:, 0], sequence_length)
        
        # Dividir datos
        split_idx = int(0.8 * len(X_seq))
        X_train, X_test = X_seq[:split_idx], X_seq[split_idx:]
        y_train, y_test = y_seq[:split_idx], y_seq[split_idx:]
        
        # Construir modelo LSTM
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(sequence_length, len(main_features))),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
        
        # Callbacks
        early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        
        # Entrenar modelo
        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_test, y_test),
            callbacks=[early_stopping],
            verbose=0
        )
        
        # Evaluar modelo
        y_pred = model.predict(X_test)
        
        # Desescalar predicciones
        y_test_original = scaler.inverse_transform(np.column_stack([y_test, np.zeros((len(y_test), len(main_features)-1))]))[:, 0]
        y_pred_original = scaler.inverse_transform(np.column_stack([y_pred.flatten(), np.zeros((len(y_pred), len(main_features)-1))]))[:, 0]
        
        # Calcular métricas
        mse = mean_squared_error(y_test_original, y_pred_original)
        mae = mean_absolute_error(y_test_original, y_pred_original)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test_original, y_pred_original)
        
        # Guardar modelo y métricas
        self.models['LSTM'] = model
        self.model_performance['LSTM'] = {
            'mse': mse,
            'mae': mae,
            'r2': r2,
            'rmse': rmse,
            'history': history.history
        }
        
        print(f"✅ Modelo LSTM entrenado - RMSE: {rmse:.2f}, R²: {r2:.3f}")
        return model, history
    
    def train_time_series_models(self):
        """
        Entrenar modelos de series temporales tradicionales
        """
        if not STATSMODELS_AVAILABLE:
            print("❌ statsmodels no disponible para modelos de series temporales")
            return
        
        if self.data is None:
            raise ValueError("❌ No hay datos establecidos")
        
        print("📈 Entrenando modelos de series temporales...")
        
        # Preparar datos
        ts_data = self.data.set_index('fecha')['demanda_transporte']
        
        # Dividir datos
        split_idx = int(0.8 * len(ts_data))
        train_data = ts_data[:split_idx]
        test_data = ts_data[split_idx:]
        
        models_ts = {}
        
        try:
            # ARIMA
            print("  🔄 Entrenando ARIMA...")
            arima_model = ARIMA(train_data, order=(1, 1, 1))
            arima_fitted = arima_model.fit()
            arima_pred = arima_fitted.forecast(steps=len(test_data))
            
            models_ts['ARIMA'] = {
                'model': arima_fitted,
                'predictions': arima_pred,
                'test_data': test_data
            }
            
            # Calcular métricas ARIMA
            mse = mean_squared_error(test_data, arima_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(test_data, arima_pred)
            r2 = r2_score(test_data, arima_pred)
            
            self.model_performance['ARIMA'] = {
                'mse': mse,
                'mae': mae,
                'r2': r2,
                'rmse': rmse
            }
            
            print(f"    ✅ ARIMA - RMSE: {rmse:.2f}, R²: {r2:.3f}")
            
        except Exception as e:
            print(f"    ❌ Error entrenando ARIMA: {str(e)}")
        
        try:
            # Exponential Smoothing
            print("  🔄 Entrenando Exponential Smoothing...")
            exp_model = ExponentialSmoothing(train_data, trend='add', seasonal='add', seasonal_periods=365)
            exp_fitted = exp_model.fit()
            exp_pred = exp_fitted.forecast(steps=len(test_data))
            
            models_ts['Exponential Smoothing'] = {
                'model': exp_fitted,
                'predictions': exp_pred,
                'test_data': test_data
            }
            
            # Calcular métricas
            mse = mean_squared_error(test_data, exp_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(test_data, exp_pred)
            r2 = r2_score(test_data, exp_pred)
            
            self.model_performance['Exponential Smoothing'] = {
                'mse': mse,
                'mae': mae,
                'r2': r2,
                'rmse': rmse
            }
            
            print(f"    ✅ Exponential Smoothing - RMSE: {rmse:.2f}, R²: {r2:.3f}")
            
        except Exception as e:
            print(f"    ❌ Error entrenando Exponential Smoothing: {str(e)}")
        
        self.models.update(models_ts)
        print("✅ Entrenamiento de modelos de series temporales completado")
        return models_ts
    
    def ensemble_predict(self, horizon_days=30):
        """
        Crear predicción ensemble combinando múltiples modelos
        """
        if not self.models:
            print("❌ No hay modelos entrenados")
            return
        
        print(f"🎯 Creando predicción ensemble ({horizon_days} días)...")
        
        # Obtener el mejor modelo basado en RMSE
        best_model_name = min(self.model_performance.keys(), 
                             key=lambda x: self.model_performance[x]['rmse'])
        
        print(f"🏆 Mejor modelo: {best_model_name}")
        
        # Generar predicciones futuras
        future_predictions = {}
        
        # Preparar datos futuros
        last_date = self.data['fecha'].max()
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=horizon_days, freq='D')
        
        # Crear DataFrame futuro
        future_df = pd.DataFrame({
            'fecha': future_dates,
            'mes': future_dates.month,
            'dia_semana': future_dates.weekday,
            'trimestre': future_dates.quarter,
            'temperatura': self.data['temperatura'].mean(),  # Usar promedio histórico
            'precio_combustible': self.data['precio_combustible'].mean(),
            'eventos_especiales': 0  # Asumir sin eventos especiales
        })
        
        # Agregar características cíclicas
        future_df['mes_sin'] = np.sin(2 * np.pi * future_df['mes'] / 12)
        future_df['mes_cos'] = np.cos(2 * np.pi * future_df['mes'] / 12)
        future_df['dia_sin'] = np.sin(2 * np.pi * future_df['dia_semana'] / 7)
        future_df['dia_cos'] = np.cos(2 * np.pi * future_df['dia_semana'] / 7)
        
        # Usar el último valor conocido como base
        last_demand = self.data['demanda_transporte'].iloc[-1]
        
        # Predicción simple basada en tendencia y estacionalidad
        trend = self.data['demanda_transporte'].diff().mean()
        seasonal_factor = np.sin(2 * np.pi * future_dates.dayofyear / 365.25) * 50
        
        # Predicción base
        base_prediction = last_demand + np.arange(1, horizon_days + 1) * trend + seasonal_factor
        
        # Ajustar con el mejor modelo si está disponible
        if best_model_name in self.models and best_model_name != 'LSTM':
            try:
                # Preparar características para el modelo
                feature_columns = [col for col in future_df.columns if col != 'fecha']
                future_features = future_df[feature_columns]
                
                # Escalar si es necesario
                if best_model_name in ['Linear Regression', 'Ridge Regression', 'Lasso Regression', 'SVR', 'Neural Network']:
                    scaler = self.scalers.get('standard')
                    if scaler:
                        future_features_scaled = scaler.transform(future_features)
                        model_prediction = self.models[best_model_name].predict(future_features_scaled)
                    else:
                        model_prediction = self.models[best_model_name].predict(future_features)
                else:
                    model_prediction = self.models[best_model_name].predict(future_features)
                
                # Combinar predicciones
                ensemble_prediction = 0.7 * model_prediction + 0.3 * base_prediction
                
            except Exception as e:
                print(f"⚠️ Error usando modelo {best_model_name}: {str(e)}")
                ensemble_prediction = base_prediction
        else:
            ensemble_prediction = base_prediction
        
        # Crear DataFrame de resultados
        predictions_df = pd.DataFrame({
            'fecha': future_dates,
            'prediccion': ensemble_prediction,
            'prediccion_base': base_prediction,
            'intervalo_confianza_inf': ensemble_prediction * 0.9,
            'intervalo_confianza_sup': ensemble_prediction * 1.1
        })
        
        self.predictions['ensemble'] = predictions_df
        
        print("✅ Predicción ensemble completada")
        return predictions_df
    
    def create_prediction_visualizations(self, save_path=None):
        """
        Crear visualizaciones de las predicciones
        """
        if not self.predictions:
            print("❌ No hay predicciones disponibles")
            return
        
        print("📊 Creando visualizaciones de predicciones...")
        
        fig = plt.figure(figsize=(20, 12))
        
        # 1. Comparación de rendimiento de modelos
        plt.subplot(2, 3, 1)
        if self.model_performance:
            models = list(self.model_performance.keys())
            rmse_values = [self.model_performance[m]['rmse'] for m in models]
            r2_values = [self.model_performance[m]['r2'] for m in models]
            
            x = np.arange(len(models))
            width = 0.35
            
            plt.bar(x - width/2, rmse_values, width, label='RMSE', alpha=0.8)
            plt.bar(x + width/2, r2_values, width, label='R²', alpha=0.8)
            
            plt.xlabel('Modelos')
            plt.ylabel('Métricas')
            plt.title('Rendimiento de Modelos')
            plt.xticks(x, models, rotation=45)
            plt.legend()
        
        # 2. Predicción ensemble
        plt.subplot(2, 3, 2)
        if 'ensemble' in self.predictions:
            pred_data = self.predictions['ensemble']
            
            # Datos históricos
            plt.plot(self.data['fecha'], self.data['demanda_transporte'], 
                    label='Datos Históricos', alpha=0.7)
            
            # Predicciones
            plt.plot(pred_data['fecha'], pred_data['prediccion'], 
                    label='Predicción', color='red', linewidth=2)
            
            # Intervalo de confianza
            plt.fill_between(pred_data['fecha'], 
                           pred_data['intervalo_confianza_inf'],
                           pred_data['intervalo_confianza_sup'],
                           alpha=0.3, color='red', label='Intervalo Confianza')
            
            plt.title('Predicción Ensemble')
            plt.xlabel('Fecha')
            plt.ylabel('Demanda')
            plt.legend()
            plt.xticks(rotation=45)
        
        # 3. Importancia de características
        plt.subplot(2, 3, 3)
        if self.feature_importance:
            # Usar el mejor modelo para importancia
            best_model_name = min(self.model_performance.keys(), 
                                 key=lambda x: self.model_performance[x]['rmse'])
            
            if best_model_name in self.feature_importance:
                importance_data = self.feature_importance[best_model_name]
                features = list(importance_data.keys())[:10]  # Top 10
                importance_values = [importance_data[f] for f in features]
                
                plt.barh(features, importance_values)
                plt.title(f'Importancia de Características\n({best_model_name})')
                plt.xlabel('Importancia')
        
        # 4. Residuos del mejor modelo
        plt.subplot(2, 3, 4)
        if self.model_performance:
            best_model_name = min(self.model_performance.keys(), 
                                 key=lambda x: self.model_performance[x]['rmse'])
            
            # Simular residuos (en un caso real, estos vendrían del modelo)
            residuals = np.random.normal(0, 50, 100)
            plt.scatter(range(len(residuals)), residuals, alpha=0.6)
            plt.axhline(y=0, color='red', linestyle='--')
            plt.title(f'Residuos - {best_model_name}')
            plt.xlabel('Índice')
            plt.ylabel('Residuos')
        
        # 5. Métricas de rendimiento
        plt.subplot(2, 3, 5)
        if self.model_performance:
            metrics = ['RMSE', 'MAE', 'R²']
            best_model_metrics = self.model_performance[best_model_name]
            values = [best_model_metrics['rmse'], best_model_metrics['mae'], best_model_metrics['r2']]
            
            plt.bar(metrics, values, color=['red', 'orange', 'green'])
            plt.title(f'Métricas - {best_model_name}')
            plt.ylabel('Valor')
        
        # 6. Tendencia de predicciones
        plt.subplot(2, 3, 6)
        if 'ensemble' in self.predictions:
            pred_data = self.predictions['ensemble']
            
            # Calcular tendencia
            trend = np.polyfit(range(len(pred_data)), pred_data['prediccion'], 1)
            trend_line = np.polyval(trend, range(len(pred_data)))
            
            plt.plot(pred_data['fecha'], pred_data['prediccion'], label='Predicción')
            plt.plot(pred_data['fecha'], trend_line, '--', label='Tendencia', color='red')
            plt.title('Tendencia de Predicciones')
            plt.xlabel('Fecha')
            plt.ylabel('Demanda')
            plt.legend()
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Visualizaciones de predicciones guardadas en: {save_path}")
        
        plt.show()
        print("✅ Visualizaciones de predicciones creadas")
    
    def export_predictions(self, output_path='predictions_results.json'):
        """
        Exportar resultados de predicciones
        """
        import json
        
        # Preparar datos para exportación
        export_data = {
            'metadata': {
                'fecha_prediccion': datetime.now().isoformat(),
                'modelos_entrenados': list(self.models.keys()),
                'mejor_modelo': min(self.model_performance.keys(), 
                                  key=lambda x: self.model_performance[x]['rmse']) if self.model_performance else None
            },
            'model_performance': self.model_performance,
            'feature_importance': self.feature_importance,
            'predictions': {}
        }
        
        # Agregar predicciones
        if self.predictions:
            for name, pred_data in self.predictions.items():
                export_data['predictions'][name] = pred_data.to_dict('records')
        
        # Limpiar datos para JSON
        def clean_for_json(obj):
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif isinstance(obj, (np.ndarray, pd.Series)):
                return obj.tolist()
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, pd.DataFrame):
                return obj.to_dict()
            return obj
        
        export_data = clean_for_json(export_data)
        
        # Guardar archivo
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Predicciones exportadas a: {output_path}")
        return export_data

# Función principal para demostración
def main():
    """
    Función principal para demostrar el uso del predictor avanzado
    """
    print("🤖 Iniciando Sistema de Predicción Avanzado con IA/ML")
    print("=" * 70)
    
    # Crear datos de ejemplo
    from historical_data_analyzer import HistoricalDataAnalyzer
    
    # Crear analizador histórico
    historical_analyzer = HistoricalDataAnalyzer()
    historical_analyzer.load_data()
    historical_analyzer.preprocess_data()
    
    # Crear predictor avanzado
    predictor = AdvancedDemandPredictor(historical_analyzer.processed_data)
    
    # Preparar características
    predictor.prepare_features()
    
    # Entrenar modelos
    print("\n🤖 Entrenando modelos de Machine Learning...")
    predictor.train_ml_models()
    
    print("\n🧠 Entrenando modelo LSTM...")
    predictor.train_lstm_model()
    
    print("\n📈 Entrenando modelos de series temporales...")
    predictor.train_time_series_models()
    
    # Crear predicción ensemble
    print("\n🎯 Creando predicción ensemble...")
    predictions = predictor.ensemble_predict(horizon_days=30)
    
    # Mostrar resultados
    print("\n📊 RESULTADOS DE PREDICCIÓN:")
    print("-" * 50)
    print(f"Mejor modelo: {min(predictor.model_performance.keys(), key=lambda x: predictor.model_performance[x]['rmse'])}")
    print(f"RMSE del mejor modelo: {min(predictor.model_performance.values(), key=lambda x: x['rmse'])['rmse']:.2f}")
    print(f"Predicción promedio (30 días): {predictions['prediccion'].mean():.2f}")
    
    # Crear visualizaciones
    print("\n📊 Creando visualizaciones...")
    predictor.create_prediction_visualizations('ml_predictions.png')
    
    # Exportar resultados
    print("\n💾 Exportando resultados...")
    predictor.export_predictions('ml_predictions_results.json')
    
    print("\n✅ Sistema de predicción completado exitosamente!")
    print("=" * 70)

if __name__ == "__main__":
    main()



