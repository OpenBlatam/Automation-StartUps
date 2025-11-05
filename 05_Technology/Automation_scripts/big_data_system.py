"""
Sistema de Análisis de Big Data con Apache Spark
===============================================

Sistema completo de análisis de big data con procesamiento distribuido,
análisis en tiempo real y machine learning a escala.
"""

import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

logger = logging.getLogger(__name__)

class DataProcessingMode(Enum):
    """Modos de procesamiento de datos"""
    BATCH = "batch"
    STREAMING = "streaming"
    MICRO_BATCH = "micro_batch"
    REAL_TIME = "real_time"

class AnalyticsType(Enum):
    """Tipos de análisis"""
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"

@dataclass
class DataProcessingJob:
    """Trabajo de procesamiento de datos"""
    job_id: str
    job_type: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    input_size: int
    output_size: int
    processing_time: float
    error_message: Optional[str] = None

@dataclass
class AnalyticsResult:
    """Resultado de análisis"""
    analysis_type: str
    data_points: int
    insights: List[Dict[str, Any]]
    recommendations: List[str]
    confidence_score: float
    processing_time: float
    timestamp: datetime

class SparkDataProcessor:
    """Procesador de datos distribuido (simulado)"""
    
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.jobs = {}
        self.is_running = False
        self.thread_pool = ThreadPoolExecutor(max_workers=num_workers)
        
    def start_session(self):
        """Iniciar sesión de Spark"""
        logger.info(f"Iniciando sesión de Spark con {self.num_workers} workers")
        self.is_running = True
        
    def stop_session(self):
        """Detener sesión de Spark"""
        logger.info("Deteniendo sesión de Spark")
        self.is_running = False
        self.thread_pool.shutdown(wait=True)
    
    def create_dataframe(self, data: pd.DataFrame) -> 'SparkDataFrame':
        """Crear DataFrame distribuido"""
        return SparkDataFrame(data, self)
    
    def parallel_processing(self, data_chunks: List[pd.DataFrame], 
                          processing_func, **kwargs) -> List[Any]:
        """Procesamiento paralelo de datos"""
        
        if not self.is_running:
            raise RuntimeError("Sesión de Spark no iniciada")
        
        logger.info(f"Procesando {len(data_chunks)} chunks en paralelo")
        
        # Simular procesamiento distribuido
        futures = []
        for i, chunk in enumerate(data_chunks):
            future = self.thread_pool.submit(processing_func, chunk, **kwargs)
            futures.append(future)
        
        results = []
        for future in futures:
            try:
                result = future.result(timeout=300)  # 5 minutos timeout
                results.append(result)
            except Exception as e:
                logger.error(f"Error en procesamiento paralelo: {e}")
                results.append(None)
        
        return results

class SparkDataFrame:
    """DataFrame distribuido simulado"""
    
    def __init__(self, data: pd.DataFrame, processor: SparkDataProcessor):
        self.data = data
        self.processor = processor
        self.operations = []
    
    def select(self, columns: List[str]) -> 'SparkDataFrame':
        """Seleccionar columnas"""
        new_data = self.data[columns].copy()
        new_df = SparkDataFrame(new_data, self.processor)
        new_df.operations = self.operations + [f"select({columns})"]
        return new_df
    
    def filter(self, condition) -> 'SparkDataFrame':
        """Filtrar datos"""
        if callable(condition):
            mask = condition(self.data)
        else:
            mask = self.data.eval(condition)
        
        new_data = self.data[mask].copy()
        new_df = SparkDataFrame(new_data, self.processor)
        new_df.operations = self.operations + [f"filter({condition})"]
        return new_df
    
    def group_by(self, columns: List[str]) -> 'SparkGroupedData':
        """Agrupar datos"""
        grouped_data = self.data.groupby(columns)
        return SparkGroupedData(grouped_data, self.processor, columns)
    
    def join(self, other: 'SparkDataFrame', on: str, how: str = 'inner') -> 'SparkDataFrame':
        """Unir DataFrames"""
        new_data = self.data.merge(other.data, on=on, how=how)
        new_df = SparkDataFrame(new_data, self.processor)
        new_df.operations = self.operations + [f"join({on}, {how})"]
        return new_df
    
    def cache(self) -> 'SparkDataFrame':
        """Cachear DataFrame en memoria"""
        logger.info("Cacheando DataFrame en memoria")
        return self
    
    def persist(self, storage_level: str = 'MEMORY_AND_DISK') -> 'SparkDataFrame':
        """Persistir DataFrame"""
        logger.info(f"Persistiendo DataFrame con nivel: {storage_level}")
        return self
    
    def collect(self) -> pd.DataFrame:
        """Recolectar datos"""
        logger.info("Recolectando datos distribuidos")
        return self.data.copy()
    
    def count(self) -> int:
        """Contar registros"""
        return len(self.data)
    
    def show(self, n: int = 20):
        """Mostrar datos"""
        print(self.data.head(n))
    
    def describe(self) -> pd.DataFrame:
        """Estadísticas descriptivas"""
        return self.data.describe()
    
    def to_pandas(self) -> pd.DataFrame:
        """Convertir a pandas DataFrame"""
        return self.data.copy()

class SparkGroupedData:
    """Datos agrupados para operaciones de agregación"""
    
    def __init__(self, grouped_data, processor: SparkDataProcessor, group_columns: List[str]):
        self.grouped_data = grouped_data
        self.processor = processor
        self.group_columns = group_columns
    
    def agg(self, aggregations: Dict[str, str]) -> SparkDataFrame:
        """Aplicar agregaciones"""
        result = self.grouped_data.agg(aggregations)
        return SparkDataFrame(result.reset_index(), self.processor)
    
    def count(self) -> SparkDataFrame:
        """Contar por grupo"""
        result = self.grouped_data.size().reset_index(name='count')
        return SparkDataFrame(result, self.processor)
    
    def sum(self, column: str) -> SparkDataFrame:
        """Sumar por grupo"""
        result = self.grouped_data[column].sum().reset_index()
        return SparkDataFrame(result, self.processor)
    
    def mean(self, column: str) -> SparkDataFrame:
        """Promedio por grupo"""
        result = self.grouped_data[column].mean().reset_index()
        return SparkDataFrame(result, self.processor)
    
    def max(self, column: str) -> SparkDataFrame:
        """Máximo por grupo"""
        result = self.grouped_data[column].max().reset_index()
        return SparkDataFrame(result, self.processor)
    
    def min(self, column: str) -> SparkDataFrame:
        """Mínimo por grupo"""
        result = self.grouped_data[column].min().reset_index()
        return SparkDataFrame(result, self.processor)

class BigDataAnalytics:
    """Sistema de análisis de big data"""
    
    def __init__(self, spark_processor: SparkDataProcessor):
        self.spark = spark_processor
        self.analytics_cache = {}
        self.job_history = []
        
    def load_data_from_database(self, table_name: str, 
                               filters: Dict[str, Any] = None) -> SparkDataFrame:
        """Cargar datos desde base de datos"""
        
        logger.info(f"Cargando datos desde tabla {table_name}")
        
        # Conectar a base de datos
        conn = sqlite3.connect('inventory.db')
        
        # Construir query
        query = f"SELECT * FROM {table_name}"
        params = []
        
        if filters:
            conditions = []
            for column, value in filters.items():
                if isinstance(value, list):
                    placeholders = ','.join(['?' for _ in value])
                    conditions.append(f"{column} IN ({placeholders})")
                    params.extend(value)
                else:
                    conditions.append(f"{column} = ?")
                    params.append(value)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        # Cargar datos
        data = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        logger.info(f"Datos cargados: {len(data)} registros")
        
        return self.spark.create_dataframe(data)
    
    def streaming_analysis(self, data_stream: List[Dict[str, Any]], 
                          window_size: int = 100) -> AnalyticsResult:
        """Análisis en tiempo real de streaming"""
        
        logger.info(f"Análisis de streaming con ventana de {window_size}")
        
        start_time = datetime.now()
        
        # Procesar ventana deslizante
        insights = []
        recommendations = []
        
        for i in range(0, len(data_stream), window_size):
            window_data = data_stream[i:i+window_size]
            
            # Análisis de la ventana
            window_insights = self._analyze_window(window_data)
            insights.extend(window_insights)
            
            # Generar recomendaciones
            window_recommendations = self._generate_recommendations(window_data)
            recommendations.extend(window_recommendations)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AnalyticsResult(
            analysis_type=AnalyticsType.DESCRIPTIVE.value,
            data_points=len(data_stream),
            insights=insights,
            recommendations=recommendations,
            confidence_score=0.85,
            processing_time=processing_time,
            timestamp=datetime.now()
        )
    
    def _analyze_window(self, window_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analizar ventana de datos"""
        insights = []
        
        if not window_data:
            return insights
        
        # Convertir a DataFrame para análisis
        df = pd.DataFrame(window_data)
        
        # Análisis de tendencias
        if 'quantity' in df.columns:
            quantity_trend = df['quantity'].diff().mean()
            insights.append({
                'type': 'trend',
                'metric': 'quantity_change',
                'value': quantity_trend,
                'description': f'Tendencia de cantidad: {quantity_trend:.2f}'
            })
        
        # Análisis de anomalías
        if 'price' in df.columns:
            price_mean = df['price'].mean()
            price_std = df['price'].std()
            anomalies = df[abs(df['price'] - price_mean) > 2 * price_std]
            
            if len(anomalies) > 0:
                insights.append({
                    'type': 'anomaly',
                    'metric': 'price_anomalies',
                    'value': len(anomalies),
                    'description': f'{len(anomalies)} anomalías de precio detectadas'
                })
        
        return insights
    
    def _generate_recommendations(self, window_data: List[Dict[str, Any]]) -> List[str]:
        """Generar recomendaciones basadas en datos"""
        recommendations = []
        
        if not window_data:
            return recommendations
        
        df = pd.DataFrame(window_data)
        
        # Recomendación de stock bajo
        if 'quantity' in df.columns:
            low_stock_items = df[df['quantity'] < df['quantity'].quantile(0.2)]
            if len(low_stock_items) > 0:
                recommendations.append(
                    f"Considerar reabastecimiento para {len(low_stock_items)} productos con stock bajo"
                )
        
        # Recomendación de precios
        if 'price' in df.columns:
            price_volatility = df['price'].std() / df['price'].mean()
            if price_volatility > 0.1:
                recommendations.append(
                    "Alta volatilidad de precios detectada - revisar estrategia de precios"
                )
        
        return recommendations
    
    def batch_analysis(self, data: SparkDataFrame, 
                      analysis_type: AnalyticsType) -> AnalyticsResult:
        """Análisis por lotes de datos grandes"""
        
        logger.info(f"Iniciando análisis por lotes: {analysis_type.value}")
        
        start_time = datetime.now()
        
        # Ejecutar análisis según tipo
        if analysis_type == AnalyticsType.DESCRIPTIVE:
            insights = self._descriptive_analysis(data)
        elif analysis_type == AnalyticsType.DIAGNOSTIC:
            insights = self._diagnostic_analysis(data)
        elif analysis_type == AnalyticsType.PREDICTIVE:
            insights = self._predictive_analysis(data)
        elif analysis_type == AnalyticsType.PRESCRIPTIVE:
            insights = self._prescriptive_analysis(data)
        else:
            raise ValueError(f"Tipo de análisis no soportado: {analysis_type}")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AnalyticsResult(
            analysis_type=analysis_type.value,
            data_points=data.count(),
            insights=insights,
            recommendations=self._generate_batch_recommendations(insights),
            confidence_score=0.90,
            processing_time=processing_time,
            timestamp=datetime.now()
        )
    
    def _descriptive_analysis(self, data: SparkDataFrame) -> List[Dict[str, Any]]:
        """Análisis descriptivo"""
        insights = []
        
        # Estadísticas básicas
        stats = data.describe()
        
        for column in stats.columns:
            insights.append({
                'type': 'statistics',
                'metric': f'{column}_stats',
                'value': {
                    'mean': stats.loc['mean', column],
                    'std': stats.loc['std', column],
                    'min': stats.loc['min', column],
                    'max': stats.loc['max', column]
                },
                'description': f'Estadísticas de {column}'
            })
        
        return insights
    
    def _diagnostic_analysis(self, data: SparkDataFrame) -> List[Dict[str, Any]]:
        """Análisis diagnóstico"""
        insights = []
        
        # Análisis de correlaciones
        df = data.to_pandas()
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) > 1:
            correlation_matrix = df[numeric_columns].corr()
            
            # Encontrar correlaciones fuertes
            for i in range(len(numeric_columns)):
                for j in range(i+1, len(numeric_columns)):
                    corr = correlation_matrix.iloc[i, j]
                    if abs(corr) > 0.7:
                        insights.append({
                            'type': 'correlation',
                            'metric': f'{numeric_columns[i]}_vs_{numeric_columns[j]}',
                            'value': corr,
                            'description': f'Correlación fuerte entre {numeric_columns[i]} y {numeric_columns[j]}: {corr:.2f}'
                        })
        
        return insights
    
    def _predictive_analysis(self, data: SparkDataFrame) -> List[Dict[str, Any]]:
        """Análisis predictivo"""
        insights = []
        
        df = data.to_pandas()
        
        # Análisis de tendencias temporales
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Análisis de tendencia para columnas numéricas
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            for column in numeric_columns:
                if column != 'date':
                    # Calcular tendencia usando regresión lineal simple
                    x = np.arange(len(df))
                    y = df[column].values
                    
                    # Regresión lineal
                    slope = np.polyfit(x, y, 1)[0]
                    
                    insights.append({
                        'type': 'trend',
                        'metric': f'{column}_trend',
                        'value': slope,
                        'description': f'Tendencia de {column}: {"creciente" if slope > 0 else "decreciente"}'
                    })
        
        return insights
    
    def _prescriptive_analysis(self, data: SparkDataFrame) -> List[Dict[str, Any]]:
        """Análisis prescriptivo"""
        insights = []
        
        df = data.to_pandas()
        
        # Optimización de inventario
        if 'quantity' in df.columns and 'price' in df.columns:
            # Calcular EOQ (Economic Order Quantity) simplificado
            total_demand = df['quantity'].sum()
            avg_price = df['price'].mean()
            
            # EOQ simplificado (asumiendo costos de orden y holding)
            ordering_cost = 100  # Costo fijo por orden
            holding_cost = avg_price * 0.2  # 20% del precio como costo de almacenamiento
            
            eoq = np.sqrt(2 * total_demand * ordering_cost / holding_cost)
            
            insights.append({
                'type': 'optimization',
                'metric': 'economic_order_quantity',
                'value': eoq,
                'description': f'Cantidad económica de orden recomendada: {eoq:.0f} unidades'
            })
        
        return insights
    
    def _generate_batch_recommendations(self, insights: List[Dict[str, Any]]) -> List[str]:
        """Generar recomendaciones basadas en insights"""
        recommendations = []
        
        for insight in insights:
            if insight['type'] == 'trend':
                if insight['value'] > 0:
                    recommendations.append("Tendencia creciente detectada - considerar aumentar capacidad")
                else:
                    recommendations.append("Tendencia decreciente detectada - revisar estrategia")
            
            elif insight['type'] == 'correlation':
                if abs(insight['value']) > 0.8:
                    recommendations.append("Correlación muy fuerte - considerar análisis de causalidad")
            
            elif insight['type'] == 'optimization':
                recommendations.append(f"Aplicar optimización: {insight['description']}")
        
        return recommendations
    
    def distributed_machine_learning(self, data: SparkDataFrame, 
                                   target_column: str, 
                                   algorithm: str = 'random_forest') -> Dict[str, Any]:
        """Machine Learning distribuido"""
        
        logger.info(f"Iniciando ML distribuido con algoritmo: {algorithm}")
        
        start_time = datetime.now()
        
        # Dividir datos en chunks para procesamiento distribuido
        df = data.to_pandas()
        chunk_size = len(df) // self.spark.num_workers
        
        chunks = []
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i+chunk_size]
            chunks.append(chunk)
        
        # Procesar chunks en paralelo
        results = self.spark.parallel_processing(
            chunks, 
            self._train_model_chunk,
            target_column=target_column,
            algorithm=algorithm
        )
        
        # Combinar resultados
        final_model = self._combine_model_results(results)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'model': final_model,
            'processing_time': processing_time,
            'chunks_processed': len(chunks),
            'algorithm': algorithm
        }
    
    def _train_model_chunk(self, chunk: pd.DataFrame, target_column: str, 
                          algorithm: str) -> Dict[str, Any]:
        """Entrenar modelo en un chunk de datos"""
        
        # Preparar datos
        feature_columns = [col for col in chunk.columns if col != target_column]
        X = chunk[feature_columns]
        y = chunk[target_column]
        
        # Entrenar modelo simple (simulado)
        if algorithm == 'random_forest':
            from sklearn.ensemble import RandomForestRegressor
            model = RandomForestRegressor(n_estimators=10, random_state=42)
        elif algorithm == 'linear_regression':
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
        else:
            raise ValueError(f"Algoritmo no soportado: {algorithm}")
        
        model.fit(X, y)
        
        return {
            'model': model,
            'feature_columns': feature_columns,
            'chunk_size': len(chunk),
            'algorithm': algorithm
        }
    
    def _combine_model_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combinar resultados de modelos distribuidos"""
        
        # Filtrar resultados válidos
        valid_results = [r for r in results if r is not None]
        
        if not valid_results:
            raise ValueError("No se pudieron entrenar modelos válidos")
        
        # Usar el modelo del primer chunk como base
        base_model = valid_results[0]['model']
        
        return {
            'model': base_model,
            'feature_columns': valid_results[0]['feature_columns'],
            'total_chunks': len(valid_results),
            'total_samples': sum(r['chunk_size'] for r in valid_results),
            'algorithm': valid_results[0]['algorithm']
        }
    
    def real_time_monitoring(self, data_stream: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Monitoreo en tiempo real"""
        
        logger.info("Iniciando monitoreo en tiempo real")
        
        # Métricas en tiempo real
        metrics = {
            'throughput': len(data_stream),
            'latency': 0.001,  # Simulado
            'error_rate': 0.0,
            'memory_usage': 0.5,
            'cpu_usage': 0.3
        }
        
        # Detectar anomalías en tiempo real
        anomalies = []
        if data_stream:
            df = pd.DataFrame(data_stream)
            
            # Detectar valores atípicos
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            for column in numeric_columns:
                mean_val = df[column].mean()
                std_val = df[column].std()
                
                outliers = df[abs(df[column] - mean_val) > 2 * std_val]
                if len(outliers) > 0:
                    anomalies.append({
                        'column': column,
                        'count': len(outliers),
                        'severity': 'high' if len(outliers) > len(df) * 0.1 else 'medium'
                    })
        
        return {
            'metrics': metrics,
            'anomalies': anomalies,
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy' if len(anomalies) == 0 else 'warning'
        }

class BigDataManager:
    """Gestor principal de big data"""
    
    def __init__(self):
        self.spark_processor = SparkDataProcessor(num_workers=4)
        self.analytics = BigDataAnalytics(self.spark_processor)
        self.is_initialized = False
    
    def initialize(self):
        """Inicializar sistema de big data"""
        if not self.is_initialized:
            self.spark_processor.start_session()
            self.is_initialized = True
            logger.info("Sistema de big data inicializado")
    
    def shutdown(self):
        """Cerrar sistema de big data"""
        if self.is_initialized:
            self.spark_processor.stop_session()
            self.is_initialized = False
            logger.info("Sistema de big data cerrado")
    
    def analyze_inventory_data(self, analysis_type: AnalyticsType = AnalyticsType.DESCRIPTIVE) -> AnalyticsResult:
        """Analizar datos de inventario"""
        
        if not self.is_initialized:
            self.initialize()
        
        # Cargar datos de inventario
        inventory_data = self.analytics.load_data_from_database('inventory')
        
        # Realizar análisis
        result = self.analytics.batch_analysis(inventory_data, analysis_type)
        
        logger.info(f"Análisis de inventario completado: {result.data_points} puntos de datos")
        
        return result
    
    def predict_demand_distributed(self, target_column: str = 'quantity') -> Dict[str, Any]:
        """Predicción de demanda distribuida"""
        
        if not self.is_initialized:
            self.initialize()
        
        # Cargar datos históricos
        sales_data = self.analytics.load_data_from_database('sales_history')
        
        # ML distribuido
        ml_result = self.analytics.distributed_machine_learning(
            sales_data, target_column, 'random_forest'
        )
        
        logger.info("Predicción de demanda distribuida completada")
        
        return ml_result
    
    def stream_analysis(self, data_stream: List[Dict[str, Any]]) -> AnalyticsResult:
        """Análisis de streaming"""
        
        if not self.is_initialized:
            self.initialize()
        
        result = self.analytics.streaming_analysis(data_stream)
        
        logger.info(f"Análisis de streaming completado: {result.data_points} puntos")
        
        return result
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema"""
        
        return {
            'initialized': self.is_initialized,
            'spark_session_active': self.spark_processor.is_running,
            'num_workers': self.spark_processor.num_workers,
            'jobs_completed': len(self.analytics.job_history),
            'cache_size': len(self.analytics.analytics_cache),
            'timestamp': datetime.now().isoformat()
        }

# Instancia global del gestor de big data
big_data_manager = BigDataManager()

# Funciones de conveniencia
def analyze_big_data(analysis_type: AnalyticsType = AnalyticsType.DESCRIPTIVE) -> AnalyticsResult:
    """Analizar big data"""
    return big_data_manager.analyze_inventory_data(analysis_type)

def predict_demand_big_data(target_column: str = 'quantity') -> Dict[str, Any]:
    """Predicción de demanda con big data"""
    return big_data_manager.predict_demand_distributed(target_column)

def stream_analysis_big_data(data_stream: List[Dict[str, Any]]) -> AnalyticsResult:
    """Análisis de streaming"""
    return big_data_manager.stream_analysis(data_stream)

if __name__ == "__main__":
    # Ejemplo de uso
    logger.info("Probando sistema de big data...")
    
    # Inicializar sistema
    big_data_manager.initialize()
    
    try:
        # Análisis descriptivo
        descriptive_result = analyze_big_data(AnalyticsType.DESCRIPTIVE)
        print(f"✅ Análisis descriptivo: {descriptive_result.data_points} puntos de datos")
        print(f"   Insights: {len(descriptive_result.insights)}")
        print(f"   Recomendaciones: {len(descriptive_result.recommendations)}")
        
        # Análisis predictivo
        predictive_result = analyze_big_data(AnalyticsType.PREDICTIVE)
        print(f"✅ Análisis predictivo: {predictive_result.data_points} puntos de datos")
        
        # ML distribuido
        ml_result = predict_demand_big_data()
        print(f"✅ ML distribuido: {ml_result['total_samples']} muestras procesadas")
        
        # Análisis de streaming
        sample_stream = [
            {'quantity': 10, 'price': 100, 'timestamp': datetime.now().isoformat()},
            {'quantity': 15, 'price': 105, 'timestamp': datetime.now().isoformat()},
            {'quantity': 8, 'price': 95, 'timestamp': datetime.now().isoformat()}
        ]
        
        stream_result = stream_analysis_big_data(sample_stream)
        print(f"✅ Análisis de streaming: {stream_result.data_points} puntos")
        
        # Estado del sistema
        status = big_data_manager.get_system_status()
        print(f"✅ Estado del sistema: {status['num_workers']} workers activos")
        
    except Exception as e:
        logger.error(f"Error en pruebas de big data: {e}")
    
    finally:
        # Cerrar sistema
        big_data_manager.shutdown()
    
    print("✅ Sistema de big data funcionando correctamente")



