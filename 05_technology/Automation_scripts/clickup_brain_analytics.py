#!/usr/bin/env python3
"""
ClickUp Brain Analytics System
=============================

Advanced analytics and business intelligence system with data processing,
machine learning insights, and predictive analytics.
"""

import asyncio
import json
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
from enum import Enum
import threading
from contextlib import asynccontextmanager
import sqlite3
from collections import defaultdict, deque
import hashlib
import pickle

ROOT = Path(__file__).parent

class AnalyticsType(Enum):
    """Analytics types."""
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"

class DataSource(Enum):
    """Data source types."""
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    CACHE = "cache"

class MetricType(Enum):
    """Metric calculation types."""
    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    STANDARD_DEVIATION = "std"
    VARIANCE = "variance"

@dataclass
class DataPoint:
    """Data point structure."""
    timestamp: datetime
    value: float
    dimensions: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsQuery:
    """Analytics query structure."""
    name: str
    data_source: str
    dimensions: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    time_range: Optional[Tuple[datetime, datetime]] = None
    group_by: List[str] = field(default_factory=list)
    order_by: List[str] = field(default_factory=list)
    limit: Optional[int] = None

@dataclass
class AnalyticsResult:
    """Analytics result structure."""
    query_name: str
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    row_count: int = 0
    columns: List[str] = field(default_factory=list)

@dataclass
class MLModel:
    """Machine learning model structure."""
    name: str
    model_type: str
    version: str
    accuracy: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    last_trained: Optional[datetime] = None
    features: List[str] = field(default_factory=list)
    target: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)

class DataProcessor:
    """Data processing and transformation engine."""
    
    def __init__(self):
        self.logger = logging.getLogger("data_processor")
        self.cache: Dict[str, Any] = {}
        self._lock = threading.RLock()
    
    def process_data(self, data: List[Dict[str, Any]], transformations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process data with transformations."""
        processed_data = data.copy()
        
        for transformation in transformations:
            transform_type = transformation.get('type')
            params = transformation.get('parameters', {})
            
            if transform_type == 'filter':
                processed_data = self._apply_filter(processed_data, params)
            elif transform_type == 'aggregate':
                processed_data = self._apply_aggregation(processed_data, params)
            elif transform_type == 'join':
                processed_data = self._apply_join(processed_data, params)
            elif transform_type == 'pivot':
                processed_data = self._apply_pivot(processed_data, params)
            elif transform_type == 'calculate':
                processed_data = self._apply_calculation(processed_data, params)
            elif transform_type == 'sort':
                processed_data = self._apply_sort(processed_data, params)
            elif transform_type == 'limit':
                processed_data = self._apply_limit(processed_data, params)
        
        return processed_data
    
    def _apply_filter(self, data: List[Dict[str, Any]], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filter transformation."""
        column = params.get('column')
        operator = params.get('operator', '==')
        value = params.get('value')
        
        if operator == '==':
            return [row for row in data if row.get(column) == value]
        elif operator == '!=':
            return [row for row in data if row.get(column) != value]
        elif operator == '>':
            return [row for row in data if row.get(column, 0) > value]
        elif operator == '<':
            return [row for row in data if row.get(column, 0) < value]
        elif operator == '>=':
            return [row for row in data if row.get(column, 0) >= value]
        elif operator == '<=':
            return [row for row in data if row.get(column, 0) <= value]
        elif operator == 'in':
            return [row for row in data if row.get(column) in value]
        elif operator == 'contains':
            return [row for row in data if str(value) in str(row.get(column, ''))]
        
        return data
    
    def _apply_aggregation(self, data: List[Dict[str, Any]], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply aggregation transformation."""
        group_by = params.get('group_by', [])
        aggregations = params.get('aggregations', {})
        
        if not group_by:
            # Global aggregation
            result = {}
            for column, operations in aggregations.items():
                values = [row.get(column) for row in data if row.get(column) is not None]
                if values:
                    for operation in operations:
                        if operation == 'sum':
                            result[f"{column}_sum"] = sum(values)
                        elif operation == 'avg':
                            result[f"{column}_avg"] = sum(values) / len(values)
                        elif operation == 'count':
                            result[f"{column}_count"] = len(values)
                        elif operation == 'min':
                            result[f"{column}_min"] = min(values)
                        elif operation == 'max':
                            result[f"{column}_max"] = max(values)
            return [result]
        
        # Group by aggregation
        groups = defaultdict(list)
        for row in data:
            key = tuple(row.get(col) for col in group_by)
            groups[key].append(row)
        
        results = []
        for group_key, group_data in groups.items():
            result = dict(zip(group_by, group_key))
            
            for column, operations in aggregations.items():
                values = [row.get(column) for row in group_data if row.get(column) is not None]
                if values:
                    for operation in operations:
                        if operation == 'sum':
                            result[f"{column}_sum"] = sum(values)
                        elif operation == 'avg':
                            result[f"{column}_avg"] = sum(values) / len(values)
                        elif operation == 'count':
                            result[f"{column}_count"] = len(values)
                        elif operation == 'min':
                            result[f"{column}_min"] = min(values)
                        elif operation == 'max':
                            result[f"{column}_max"] = max(values)
            
            results.append(result)
        
        return results
    
    def _apply_join(self, data: List[Dict[str, Any]], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply join transformation."""
        join_data = params.get('data', [])
        left_key = params.get('left_key')
        right_key = params.get('right_key')
        join_type = params.get('type', 'inner')
        
        # Create lookup for join data
        lookup = {}
        for row in join_data:
            key = row.get(right_key)
            if key not in lookup:
                lookup[key] = []
            lookup[key].append(row)
        
        results = []
        for row in data:
            key = row.get(left_key)
            if key in lookup:
                for join_row in lookup[key]:
                    merged_row = row.copy()
                    merged_row.update(join_row)
                    results.append(merged_row)
            elif join_type == 'left':
                results.append(row)
        
        return results
    
    def _apply_pivot(self, data: List[Dict[str, Any]], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply pivot transformation."""
        index = params.get('index')
        columns = params.get('columns')
        values = params.get('values')
        aggfunc = params.get('aggfunc', 'sum')
        
        # Group data by index and columns
        pivot_data = defaultdict(lambda: defaultdict(list))
        for row in data:
            index_val = row.get(index)
            col_val = row.get(columns)
            value = row.get(values)
            
            if index_val is not None and col_val is not None and value is not None:
                pivot_data[index_val][col_val].append(value)
        
        # Create pivot table
        results = []
        for index_val, cols in pivot_data.items():
            result = {index: index_val}
            for col_val, values_list in cols.items():
                if aggfunc == 'sum':
                    result[col_val] = sum(values_list)
                elif aggfunc == 'avg':
                    result[col_val] = sum(values_list) / len(values_list)
                elif aggfunc == 'count':
                    result[col_val] = len(values_list)
                elif aggfunc == 'min':
                    result[col_val] = min(values_list)
                elif aggfunc == 'max':
                    result[col_val] = max(values_list)
            results.append(result)
        
        return results
    
    def _apply_calculation(self, data: List[Dict[str, Any]], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply calculation transformation."""
        formula = params.get('formula')
        output_column = params.get('output_column', 'calculated')
        
        for row in data:
            try:
                # Simple formula evaluation (can be extended with more complex expressions)
                if '+' in formula:
                    parts = formula.split('+')
                    result = sum(float(row.get(part.strip(), 0)) for part in parts)
                elif '-' in formula:
                    parts = formula.split('-')
                    result = float(row.get(parts[0].strip(), 0)) - sum(float(row.get(part.strip(), 0)) for part in parts[1:])
                elif '*' in formula:
                    parts = formula.split('*')
                    result = 1
                    for part in parts:
                        result *= float(row.get(part.strip(), 1))
                elif '/' in formula:
                    parts = formula.split('/')
                    result = float(row.get(parts[0].strip(), 0))
                    for part in parts[1:]:
                        result /= float(row.get(part.strip(), 1))
                else:
                    result = float(row.get(formula.strip(), 0))
                
                row[output_column] = result
            except (ValueError, ZeroDivisionError):
                row[output_column] = 0
        
        return data
    
    def _apply_sort(self, data: List[Dict[str, Any]], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply sort transformation."""
        columns = params.get('columns', [])
        ascending = params.get('ascending', True)
        
        def sort_key(row):
            return tuple(row.get(col, 0) for col in columns)
        
        return sorted(data, key=sort_key, reverse=not ascending)
    
    def _apply_limit(self, data: List[Dict[str, Any]], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply limit transformation."""
        limit = params.get('limit', 100)
        return data[:limit]

class MLPredictor:
    """Machine learning prediction engine."""
    
    def __init__(self):
        self.models: Dict[str, MLModel] = {}
        self.logger = logging.getLogger("ml_predictor")
        self._lock = threading.RLock()
    
    def train_model(self, name: str, data: List[Dict[str, Any]], features: List[str], target: str, model_type: str = "linear_regression") -> MLModel:
        """Train a machine learning model."""
        try:
            # Convert data to DataFrame
            df = pd.DataFrame(data)
            
            # Prepare features and target
            X = df[features].fillna(0)
            y = df[target].fillna(0)
            
            # Train model based on type
            if model_type == "linear_regression":
                from sklearn.linear_model import LinearRegression
                model = LinearRegression()
            elif model_type == "random_forest":
                from sklearn.ensemble import RandomForestRegressor
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            elif model_type == "decision_tree":
                from sklearn.tree import DecisionTreeRegressor
                model = DecisionTreeRegressor(random_state=42)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            # Train the model
            model.fit(X, y)
            
            # Calculate accuracy (R² score)
            from sklearn.metrics import r2_score
            y_pred = model.predict(X)
            accuracy = r2_score(y, y_pred)
            
            # Create model object
            ml_model = MLModel(
                name=name,
                model_type=model_type,
                version="1.0.0",
                accuracy=accuracy,
                last_trained=datetime.now(),
                features=features,
                target=target,
                parameters=model.get_params()
            )
            
            # Store model
            with self._lock:
                self.models[name] = ml_model
                # Store the actual sklearn model
                self.models[f"{name}_sklearn"] = model
            
            self.logger.info(f"Trained model {name} with accuracy {accuracy:.4f}")
            return ml_model
            
        except Exception as e:
            self.logger.error(f"Error training model {name}: {e}")
            raise
    
    def predict(self, model_name: str, features: Dict[str, float]) -> float:
        """Make prediction using trained model."""
        with self._lock:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not found")
            
            model = self.models[f"{model_name}_sklearn"]
            ml_model = self.models[model_name]
        
        # Prepare features in correct order
        feature_values = [features.get(feature, 0) for feature in ml_model.features]
        
        # Make prediction
        prediction = model.predict([feature_values])[0]
        return float(prediction)
    
    def get_model_info(self, model_name: str) -> Optional[MLModel]:
        """Get model information."""
        with self._lock:
            return self.models.get(model_name)
    
    def list_models(self) -> List[MLModel]:
        """List all trained models."""
        with self._lock:
            return [model for name, model in self.models.items() if not name.endswith('_sklearn')]

class AnalyticsEngine:
    """Main analytics engine."""
    
    def __init__(self):
        self.data_processor = DataProcessor()
        self.ml_predictor = MLPredictor()
        self.data_sources: Dict[str, Callable] = {}
        self.queries: Dict[str, AnalyticsQuery] = {}
        self.cache: Dict[str, AnalyticsResult] = {}
        self.logger = logging.getLogger("analytics_engine")
        self._lock = threading.RLock()
    
    def register_data_source(self, name: str, source_func: Callable) -> None:
        """Register a data source."""
        self.data_sources[name] = source_func
        self.logger.info(f"Registered data source: {name}")
    
    def create_query(self, query: AnalyticsQuery) -> None:
        """Create analytics query."""
        self.queries[query.name] = query
        self.logger.info(f"Created analytics query: {query.name}")
    
    async def execute_query(self, query_name: str, use_cache: bool = True) -> AnalyticsResult:
        """Execute analytics query."""
        start_time = datetime.now()
        
        # Check cache first
        if use_cache and query_name in self.cache:
            cached_result = self.cache[query_name]
            # Check if cache is still valid (e.g., less than 1 hour old)
            if (datetime.now() - cached_result.metadata.get('cached_at', datetime.now())).total_seconds() < 3600:
                self.logger.info(f"Using cached result for query: {query_name}")
                return cached_result
        
        if query_name not in self.queries:
            raise ValueError(f"Query {query_name} not found")
        
        query = self.queries[query_name]
        
        try:
            # Get data from source
            if query.data_source not in self.data_sources:
                raise ValueError(f"Data source {query.data_source} not found")
            
            source_func = self.data_sources[query.data_source]
            raw_data = await source_func(query)
            
            # Process data
            processed_data = self.data_processor.process_data(raw_data, [])
            
            # Apply filters
            if query.filters:
                filter_transformation = {
                    'type': 'filter',
                    'parameters': query.filters
                }
                processed_data = self.data_processor.process_data(processed_data, [filter_transformation])
            
            # Apply aggregations if specified
            if query.metrics:
                aggregation_transformation = {
                    'type': 'aggregate',
                    'parameters': {
                        'group_by': query.group_by,
                        'aggregations': {metric: ['sum', 'avg', 'count'] for metric in query.metrics}
                    }
                }
                processed_data = self.data_processor.process_data(processed_data, [aggregation_transformation])
            
            # Apply sorting
            if query.order_by:
                sort_transformation = {
                    'type': 'sort',
                    'parameters': {
                        'columns': query.order_by,
                        'ascending': True
                    }
                }
                processed_data = self.data_processor.process_data(processed_data, [sort_transformation])
            
            # Apply limit
            if query.limit:
                limit_transformation = {
                    'type': 'limit',
                    'parameters': {
                        'limit': query.limit
                    }
                }
                processed_data = self.data_processor.process_data(processed_data, [limit_transformation])
            
            # Create result
            result = AnalyticsResult(
                query_name=query_name,
                data=processed_data,
                metadata={
                    'executed_at': datetime.now(),
                    'data_source': query.data_source,
                    'row_count': len(processed_data)
                },
                execution_time=(datetime.now() - start_time).total_seconds(),
                row_count=len(processed_data),
                columns=list(processed_data[0].keys()) if processed_data else []
            )
            
            # Cache result
            if use_cache:
                result.metadata['cached_at'] = datetime.now()
                with self._lock:
                    self.cache[query_name] = result
            
            self.logger.info(f"Executed query {query_name} in {result.execution_time:.3f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing query {query_name}: {e}")
            raise
    
    def get_insights(self, data: List[Dict[str, Any]], analysis_type: AnalyticsType = AnalyticsType.DESCRIPTIVE) -> Dict[str, Any]:
        """Generate insights from data."""
        if not data:
            return {}
        
        insights = {}
        
        if analysis_type == AnalyticsType.DESCRIPTIVE:
            insights = self._generate_descriptive_insights(data)
        elif analysis_type == AnalyticsType.DIAGNOSTIC:
            insights = self._generate_diagnostic_insights(data)
        elif analysis_type == AnalyticsType.PREDICTIVE:
            insights = self._generate_predictive_insights(data)
        elif analysis_type == AnalyticsType.PRESCRIPTIVE:
            insights = self._generate_prescriptive_insights(data)
        
        return insights
    
    def _generate_descriptive_insights(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate descriptive analytics insights."""
        insights = {
            'summary': {
                'total_records': len(data),
                'columns': list(data[0].keys()) if data else []
            },
            'statistics': {}
        }
        
        # Calculate statistics for numeric columns
        for column in insights['summary']['columns']:
            values = [row.get(column) for row in data if isinstance(row.get(column), (int, float))]
            if values:
                insights['statistics'][column] = {
                    'count': len(values),
                    'sum': sum(values),
                    'mean': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'median': sorted(values)[len(values) // 2]
                }
        
        return insights
    
    def _generate_diagnostic_insights(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate diagnostic analytics insights."""
        insights = {
            'correlations': {},
            'trends': {},
            'anomalies': []
        }
        
        # Find correlations between numeric columns
        numeric_columns = []
        for column in data[0].keys() if data else []:
            values = [row.get(column) for row in data if isinstance(row.get(column), (int, float))]
            if values:
                numeric_columns.append(column)
        
        # Calculate correlations
        for i, col1 in enumerate(numeric_columns):
            for col2 in numeric_columns[i+1:]:
                values1 = [row.get(col1) for row in data if isinstance(row.get(col1), (int, float))]
                values2 = [row.get(col2) for row in data if isinstance(row.get(col2), (int, float))]
                
                if len(values1) == len(values2) and len(values1) > 1:
                    correlation = np.corrcoef(values1, values2)[0, 1]
                    insights['correlations'][f"{col1}_vs_{col2}"] = correlation
        
        return insights
    
    def _generate_predictive_insights(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate predictive analytics insights."""
        insights = {
            'predictions': {},
            'forecasts': {},
            'recommendations': []
        }
        
        # Simple trend-based predictions
        for column in data[0].keys() if data else []:
            values = [row.get(column) for row in data if isinstance(row.get(column), (int, float))]
            if len(values) > 1:
                # Simple linear trend
                x = list(range(len(values)))
                slope = np.polyfit(x, values, 1)[0]
                
                # Predict next 5 values
                next_values = []
                for i in range(5):
                    next_value = values[-1] + slope * (i + 1)
                    next_values.append(next_value)
                
                insights['forecasts'][column] = {
                    'trend': 'increasing' if slope > 0 else 'decreasing',
                    'slope': slope,
                    'next_values': next_values
                }
        
        return insights
    
    def _generate_prescriptive_insights(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate prescriptive analytics insights."""
        insights = {
            'recommendations': [],
            'optimizations': {},
            'action_items': []
        }
        
        # Generate recommendations based on data patterns
        for column in data[0].keys() if data else []:
            values = [row.get(column) for row in data if isinstance(row.get(column), (int, float))]
            if values:
                mean_val = sum(values) / len(values)
                max_val = max(values)
                min_val = min(values)
                
                if max_val > mean_val * 2:
                    insights['recommendations'].append(f"High values detected in {column}, consider investigation")
                
                if min_val < mean_val * 0.5:
                    insights['recommendations'].append(f"Low values detected in {column}, consider optimization")
        
        return insights
    
    def clear_cache(self) -> None:
        """Clear analytics cache."""
        with self._lock:
            self.cache.clear()
        self.logger.info("Analytics cache cleared")

# Global analytics engine
analytics_engine = AnalyticsEngine()

def get_analytics_engine() -> AnalyticsEngine:
    """Get global analytics engine."""
    return analytics_engine

async def execute_analytics_query(query_name: str) -> AnalyticsResult:
    """Execute analytics query using global engine."""
    return await analytics_engine.execute_query(query_name)

if __name__ == "__main__":
    # Demo analytics system
    print("ClickUp Brain Analytics System Demo")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    async def demo():
        # Get analytics engine
        analytics = get_analytics_engine()
        
        # Register sample data source
        async def sample_data_source(query: AnalyticsQuery) -> List[Dict[str, Any]]:
            # Generate sample data
            data = []
            for i in range(100):
                data.append({
                    'id': i,
                    'timestamp': datetime.now() - timedelta(hours=i),
                    'value': np.random.normal(100, 20),
                    'category': ['A', 'B', 'C'][i % 3],
                    'region': ['North', 'South', 'East', 'West'][i % 4]
                })
            return data
        
        analytics.register_data_source("sample", sample_data_source)
        
        # Create analytics queries
        query1 = AnalyticsQuery(
            name="total_by_category",
            data_source="sample",
            dimensions=["category"],
            metrics=["value"],
            group_by=["category"]
        )
        analytics.create_query(query1)
        
        query2 = AnalyticsQuery(
            name="recent_data",
            data_source="sample",
            filters={"value": {"operator": ">", "value": 90}},
            limit=10
        )
        analytics.create_query(query2)
        
        # Execute queries
        result1 = await analytics.execute_query("total_by_category")
        print(f"Query 1 result: {result1.data}")
        print(f"Execution time: {result1.execution_time:.3f}s")
        
        result2 = await analytics.execute_query("recent_data")
        print(f"Query 2 result: {len(result2.data)} rows")
        
        # Generate insights
        insights = analytics.get_insights(result2.data, AnalyticsType.DESCRIPTIVE)
        print(f"Descriptive insights: {insights}")
        
        # Train ML model
        ml_model = analytics.ml_predictor.train_model(
            "value_predictor",
            result2.data,
            ["id", "value"],
            "value",
            "linear_regression"
        )
        print(f"Trained ML model: {ml_model.name} with accuracy {ml_model.accuracy:.4f}")
        
        # Make prediction
        prediction = analytics.ml_predictor.predict("value_predictor", {"id": 101, "value": 95})
        print(f"Prediction for new data point: {prediction:.2f}")
        
        print("\nAnalytics system demo completed!")
    
    asyncio.run(demo())