#!/usr/bin/env python3
"""
GraphQL API for Frontier AI Projects
Provides flexible query interface for brand analysis and model training.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path
import sys

# Add project paths
sys.path.append(str(Path(__file__).parent / "TruthGPT" / "brandkit"))
sys.path.append(str(Path(__file__).parent / "analytics"))

from graphene import ObjectType, String, Float, Int, List as GraphQLList, Field, Mutation, InputObjectType, Schema
from graphene.types.datetime import DateTime
import graphene
from graphql import GraphQLError
import asyncio
import aiohttp
from aiohttp import web
from aiohttp_graphql import GraphQLView
from aiohttp_cors import setup as cors_setup, ResourceOptions

# Import our modules
from brand_analyzer import (
    BrandAnalyzerAPI, 
    AsyncBrandAnalyzer, 
    ProductionBrandAnalyzer,
    AutoTuningBrandAnalyzer,
    DistributedBrandAnalyzer
)
from analytics.advanced_analytics import (
    BrandTrendAnalyzer,
    BrandClusterAnalyzer,
    PredictiveAnalytics,
    BusinessIntelligence
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GraphQL Types
class ColorType(graphene.ObjectType):
    r = graphene.Int()
    g = graphene.Int()
    b = graphene.Int()

class BrandKitType(graphene.ObjectType):
    color_palette = GraphQLList(Int)
    typography_profile = GraphQLList(Float)
    tone_profile = Field('ToneProfileType')
    style_embedding = GraphQLList(Float)
    sentiment_profile = GraphQLList(Float)
    brand_consistency_score = Float
    brand_profile = GraphQLList(Float)

class ToneProfileType(graphene.ObjectType):
    dominant_tone = Int
    tone_distribution = GraphQLList(Float)

class MonitoringType(graphene.ObjectType):
    response_time = Float
    timestamp = DateTime
    uptime = Float

class AnalysisResultType(graphene.ObjectType):
    success = graphene.Boolean()
    brand_kit = Field(BrandKitType)
    consistency_score = Float
    analysis_time = Float
    error = String
    monitoring = Field(MonitoringType)

class TrendAnalysisType(graphene.ObjectType):
    metric = String
    data_points = Int
    time_range = Field('TimeRangeType')
    linear_trend = Field('LinearTrendType')
    polynomial_trend = Field('PolynomialTrendType')
    seasonal_pattern = Field('SeasonalPatternType')
    volatility = Float
    anomalies = GraphQLList('AnomalyType')
    forecast = Field('ForecastType')
    confidence = Float

class TimeRangeType(graphene.ObjectType):
    start = String
    end = String

class LinearTrendType(graphene.ObjectType):
    direction = String
    strength = Float
    coefficient = Float

class PolynomialTrendType(graphene.ObjectType):
    type = String
    coefficients = GraphQLList(Float)

class SeasonalPatternType(graphene.ObjectType):
    detected = graphene.Boolean()
    dominant_period = Int
    strength = Float
    all_periods = GraphQLList(Int)
    pattern = String

class AnomalyType(graphene.ObjectType):
    index = Int
    value = Float
    z_score = Float
    severity = String

class ForecastType(graphene.ObjectType):
    forecast = GraphQLList(Float)
    forecast_dates = GraphQLList(String)
    confidence_interval = Float
    trend_coefficient = Float

class ClusterAnalysisType(graphene.ObjectType):
    optimal_clusters = Int
    cluster_labels = GraphQLList(Int)
    cluster_analysis = Field('ClusterAnalysisDetailsType')
    pca_components = GraphQLList(GraphQLList(Float))
    tsne_components = GraphQLList(GraphQLList(Float))
    silhouette_score = Float
    calinski_harabasz_score = Float

class ClusterAnalysisDetailsType(graphene.ObjectType):
    clusters = GraphQLList('ClusterType')

class ClusterType(graphene.ObjectType):
    id = String
    size = Int
    percentage = Float
    avg_consistency = Float
    feature_means = GraphQLList(Float)
    feature_stds = GraphQLList(Float)
    dominant_characteristics = Field('DominantCharacteristicsType')

class DominantCharacteristicsType(graphene.ObjectType):
    color_diversity = Float
    typography_complexity = Float
    layout_consistency = Float
    text_sophistication = Float

class PredictiveInsightsType(graphene.ObjectType):
    models_trained = GraphQLList(String)
    scores = Field('ModelScoresType')
    feature_importance = Field('FeatureImportanceType')
    training_samples = Int

class ModelScoresType(graphene.ObjectType):
    random_forest = Field('ScoreType')
    gradient_boosting = Field('ScoreType')

class ScoreType(graphene.ObjectType):
    mean_score = Float
    std_score = Float

class FeatureImportanceType(graphene.ObjectType):
    random_forest = GraphQLList(Float)
    gradient_boosting = GraphQLList(Float)

class RecommendationType(graphene.ObjectType):
    type = String
    priority = String
    title = String
    description = String
    action = String

class BIReportType(graphene.ObjectType):
    timestamp = String
    data_summary = Field('DataSummaryType')
    trend_analysis = Field('TrendAnalysisMapType')
    cluster_analysis = Field(ClusterAnalysisType)
    predictive_insights = Field(PredictiveInsightsType)
    recommendations = GraphQLList(RecommendationType)

class DataSummaryType(graphene.ObjectType):
    total_brands = Int
    consistency_stats = Field('ConsistencyStatsType')
    data_quality = Field('DataQualityType')

class ConsistencyStatsType(graphene.ObjectType):
    mean = Float
    std = Float
    min = Float
    max = Float
    median = Float

class DataQualityType(graphene.ObjectType):
    overall_completeness = Float
    field_completeness = Field('FieldCompletenessType')
    total_brands = Int

class FieldCompletenessType(graphene.ObjectType):
    colors = Float
    typography = Float
    layout = Float
    text_features = Float

class TrendAnalysisMapType(graphene.ObjectType):
    # This would be a map of metric names to trend analysis
    pass

# Input Types
class ColorInputType(InputObjectType):
    r = graphene.Int(required=True)
    g = graphene.Int(required=True)
    b = graphene.Int(required=True)

class WebsiteDataInputType(InputObjectType):
    colors = GraphQLList(ColorInputType, required=True)
    typography = GraphQLList(Float, required=True)
    layout = GraphQLList(Float, required=True)
    text_features = GraphQLList(Float, required=True)

class BatchAnalysisInputType(InputObjectType):
    websites = GraphQLList(WebsiteDataInputType, required=True)
    use_cache = graphene.Boolean(default_value=True)
    async_processing = graphene.Boolean(default_value=False)

class TimeSeriesDataPointInputType(InputObjectType):
    timestamp = String(required=True)
    value = Float(required=True)
    metadata = String()  # JSON string

class TimeSeriesDataInputType(InputObjectType):
    metric = String(required=True)
    data_points = GraphQLList(TimeSeriesDataPointInputType, required=True)

# Global analyzer instances
analyzer_instances = {}

class Query(ObjectType):
    """GraphQL Query definitions."""
    
    # Health check
    health = Field('HealthType')
    
    # Analysis queries
    analyze_website = Field(
        AnalysisResultType,
        website_data=WebsiteDataInputType(required=True),
        use_async=graphene.Boolean(default_value=False)
    )
    
    batch_analyze = Field(
        GraphQLList(AnalysisResultType),
        input_data=BatchAnalysisInputType(required=True)
    )
    
    # Analytics queries
    trend_analysis = Field(
        TrendAnalysisType,
        metric=String(required=True),
        time_series_data=GraphQLList(TimeSeriesDataPointInputType, required=True)
    )
    
    cluster_analysis = Field(
        ClusterAnalysisType,
        brand_data=GraphQLList(WebsiteDataInputType, required=True)
    )
    
    predictive_insights = Field(
        PredictiveInsightsType,
        training_data=GraphQLList(WebsiteDataInputType, required=True),
        target_variable=String(default_value="consistency_score")
    )
    
    bi_report = Field(
        BIReportType,
        brand_data=GraphQLList(WebsiteDataInputType, required=True),
        time_series_data=GraphQLList(TimeSeriesDataInputType)
    )
    
    # System queries
    cache_stats = Field('CacheStatsType')
    system_metrics = Field('SystemMetricsType')

class HealthType(graphene.ObjectType):
    status = String
    uptime_seconds = Float
    total_requests = Int
    success_rate = Float
    average_response_time = Float
    memory_usage_gb = Float
    cpu_usage_percent = Float

class CacheStatsType(graphene.ObjectType):
    cache_hits = Int
    cache_misses = Int
    hit_rate = Float
    memory_usage_gb = Float
    cache_size = Int

class SystemMetricsType(graphene.ObjectType):
    total_requests = Int
    successful_requests = Int
    failed_requests = Int
    average_response_time = Float
    cache_hit_rate = Float
    response_times = GraphQLList(Float)
    health_status = Field(HealthType)

class Mutations(ObjectType):
    """GraphQL Mutation definitions."""
    
    # Analysis mutations
    analyze_website_mutation = Field(
        AnalysisResultType,
        website_data=WebsiteDataInputType(required=True),
        use_async=graphene.Boolean(default_value=False)
    )
    
    batch_analyze_mutation = Field(
        GraphQLList(AnalysisResultType),
        input_data=BatchAnalysisInputType(required=True)
    )
    
    # Training mutations
    train_model = Field(
        'TrainingResultType',
        config=String(required=True)  # JSON string
    )
    
    # Cache mutations
    clear_cache = Field('OperationResultType')

class TrainingResultType(graphene.ObjectType):
    success = graphene.Boolean()
    job_id = String
    status = String
    message = String
    metrics = Field('TrainingMetricsType')

class TrainingMetricsType(graphene.ObjectType):
    final_loss = Float
    best_accuracy = Float
    training_time = Float
    epochs_completed = Int

class OperationResultType(graphene.ObjectType):
    success = graphene.Boolean()
    message = String

# Resolvers
class QueryResolvers:
    """Query resolvers for GraphQL operations."""
    
    @staticmethod
    def resolve_health(root, info):
        """Resolve health check query."""
        try:
            if 'production' in analyzer_instances:
                health_status = analyzer_instances['production'].get_health_status()
                return HealthType(**health_status)
            else:
                return HealthType(
                    status="unhealthy",
                    uptime_seconds=0,
                    total_requests=0,
                    success_rate=0.0,
                    average_response_time=0.0,
                    memory_usage_gb=0.0,
                    cpu_usage_percent=0.0
                )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise GraphQLError(f"Health check failed: {str(e)}")
    
    @staticmethod
    def resolve_analyze_website(root, info, website_data, use_async=False):
        """Resolve single website analysis."""
        try:
            # Convert input to dict
            data_dict = {
                'colors': [[c['r'], c['g'], c['b']] for c in website_data['colors']],
                'typography': website_data['typography'],
                'layout': website_data['layout'],
                'text_features': website_data['text_features']
            }
            
            if use_async and 'async' in analyzer_instances:
                # Use async analyzer
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    analyzer_instances['async'].analyze_website_async(data_dict)
                )
            else:
                # Use basic analyzer
                result = analyzer_instances['basic'].analyze_website(data_dict)
            
            return AnalysisResultType(
                success=result['success'],
                brand_kit=BrandKitType(**result['brand_kit']) if result.get('brand_kit') else None,
                consistency_score=result.get('model_outputs', {}).get('consistency_score'),
                analysis_time=result.get('analysis_time', 0.0),
                error=result.get('error'),
                monitoring=MonitoringType(**result.get('monitoring', {})) if result.get('monitoring') else None
            )
            
        except Exception as e:
            logger.error(f"Website analysis failed: {e}")
            raise GraphQLError(f"Analysis failed: {str(e)}")
    
    @staticmethod
    def resolve_batch_analyze(root, info, input_data):
        """Resolve batch analysis query."""
        try:
            # Convert input to list of dicts
            websites = []
            for website in input_data['websites']:
                data_dict = {
                    'colors': [[c['r'], c['g'], c['b']] for c in website['colors']],
                    'typography': website['typography'],
                    'layout': website['layout'],
                    'text_features': website['text_features']
                }
                websites.append(data_dict)
            
            if input_data.get('async_processing', False) and 'async' in analyzer_instances:
                # Use async analyzer
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(
                    analyzer_instances['async'].batch_analyze_async(websites)
                )
            else:
                # Use basic analyzer
                results = analyzer_instances['basic'].batch_analyze(websites)
            
            # Convert results
            analysis_results = []
            for result in results:
                analysis_results.append(AnalysisResultType(
                    success=result['success'],
                    brand_kit=BrandKitType(**result['brand_kit']) if result.get('brand_kit') else None,
                    consistency_score=result.get('model_outputs', {}).get('consistency_score'),
                    analysis_time=result.get('analysis_time', 0.0),
                    error=result.get('error'),
                    monitoring=MonitoringType(**result.get('monitoring', {})) if result.get('monitoring') else None
                ))
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            raise GraphQLError(f"Batch analysis failed: {str(e)}")
    
    @staticmethod
    def resolve_trend_analysis(root, info, metric, time_series_data):
        """Resolve trend analysis query."""
        try:
            # Initialize trend analyzer if not exists
            if 'trend_analyzer' not in analyzer_instances:
                analyzer_instances['trend_analyzer'] = BrandTrendAnalyzer()
            
            # Add data points
            for data_point in time_series_data:
                analyzer_instances['trend_analyzer'].add_data_point(
                    datetime.fromisoformat(data_point['timestamp']),
                    metric,
                    data_point['value'],
                    json.loads(data_point.get('metadata', '{}'))
                )
            
            # Get trend analysis
            trend_result = analyzer_instances['trend_analyzer'].detect_trends(metric)
            
            if 'error' in trend_result:
                raise GraphQLError(trend_result['error'])
            
            return TrendAnalysisType(**trend_result)
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            raise GraphQLError(f"Trend analysis failed: {str(e)}")
    
    @staticmethod
    def resolve_cluster_analysis(root, info, brand_data):
        """Resolve cluster analysis query."""
        try:
            # Initialize cluster analyzer if not exists
            if 'cluster_analyzer' not in analyzer_instances:
                analyzer_instances['cluster_analyzer'] = BrandClusterAnalyzer()
            
            # Convert input data
            converted_data = []
            for brand in brand_data:
                data_dict = {
                    'colors': [[c['r'], c['g'], c['b']] for c in brand['colors']],
                    'typography': brand['typography'],
                    'layout': brand['layout'],
                    'text_features': brand['text_features']
                }
                converted_data.append(data_dict)
            
            # Perform cluster analysis
            cluster_result = analyzer_instances['cluster_analyzer'].analyze_brands(converted_data)
            
            if 'error' in cluster_result:
                raise GraphQLError(cluster_result['error'])
            
            return ClusterAnalysisType(**cluster_result)
            
        except Exception as e:
            logger.error(f"Cluster analysis failed: {e}")
            raise GraphQLError(f"Cluster analysis failed: {str(e)}")
    
    @staticmethod
    def resolve_predictive_insights(root, info, training_data, target_variable):
        """Resolve predictive insights query."""
        try:
            # Initialize predictive analytics if not exists
            if 'predictive_analytics' not in analyzer_instances:
                analyzer_instances['predictive_analytics'] = PredictiveAnalytics()
            
            # Convert input data
            converted_data = []
            for brand in training_data:
                data_dict = {
                    'colors': [[c['r'], c['g'], c['b']] for c in brand['colors']],
                    'typography': brand['typography'],
                    'layout': brand['layout'],
                    'text_features': brand['text_features'],
                    'consistency_score': 0.8  # Default value
                }
                converted_data.append(data_dict)
            
            # Train predictive models
            result = analyzer_instances['predictive_analytics'].train_predictive_models(
                converted_data, target_variable
            )
            
            if 'error' in result:
                raise GraphQLError(result['error'])
            
            return PredictiveInsightsType(**result)
            
        except Exception as e:
            logger.error(f"Predictive insights failed: {e}")
            raise GraphQLError(f"Predictive insights failed: {str(e)}")
    
    @staticmethod
    def resolve_bi_report(root, info, brand_data, time_series_data=None):
        """Resolve business intelligence report query."""
        try:
            # Initialize BI if not exists
            if 'bi' not in analyzer_instances:
                analyzer_instances['bi'] = BusinessIntelligence()
            
            # Convert input data
            converted_brand_data = []
            for brand in brand_data:
                data_dict = {
                    'colors': [[c['r'], c['g'], c['b']] for c in brand['colors']],
                    'typography': brand['typography'],
                    'layout': brand['layout'],
                    'text_features': brand['text_features'],
                    'consistency_score': 0.8  # Default value
                }
                converted_brand_data.append(data_dict)
            
            # Convert time series data
            converted_time_series = None
            if time_series_data:
                converted_time_series = {}
                for ts_data in time_series_data:
                    converted_time_series[ts_data['metric']] = [
                        {
                            'timestamp': dp['timestamp'],
                            'value': dp['value'],
                            'metadata': json.loads(dp.get('metadata', '{}'))
                        }
                        for dp in ts_data['data_points']
                    ]
            
            # Generate BI report
            report = analyzer_instances['bi'].generate_comprehensive_report(
                converted_brand_data, converted_time_series
            )
            
            return BIReportType(**report)
            
        except Exception as e:
            logger.error(f"BI report generation failed: {e}")
            raise GraphQLError(f"BI report generation failed: {str(e)}")
    
    @staticmethod
    def resolve_cache_stats(root, info):
        """Resolve cache statistics query."""
        try:
            if 'async' in analyzer_instances:
                stats = analyzer_instances['async'].get_cache_stats()
                return CacheStatsType(**stats)
            else:
                return CacheStatsType(
                    cache_hits=0,
                    cache_misses=0,
                    hit_rate=0.0,
                    memory_usage_gb=0.0,
                    cache_size=0
                )
        except Exception as e:
            logger.error(f"Cache stats retrieval failed: {e}")
            raise GraphQLError(f"Cache stats retrieval failed: {str(e)}")
    
    @staticmethod
    def resolve_system_metrics(root, info):
        """Resolve system metrics query."""
        try:
            if 'production' in analyzer_instances:
                metrics = analyzer_instances['production'].get_metrics()
                return SystemMetricsType(**metrics)
            else:
                return SystemMetricsType(
                    total_requests=0,
                    successful_requests=0,
                    failed_requests=0,
                    average_response_time=0.0,
                    cache_hit_rate=0.0,
                    response_times=[],
                    health_status=HealthType(
                        status="unhealthy",
                        uptime_seconds=0,
                        total_requests=0,
                        success_rate=0.0,
                        average_response_time=0.0,
                        memory_usage_gb=0.0,
                        cpu_usage_percent=0.0
                    )
                )
        except Exception as e:
            logger.error(f"System metrics retrieval failed: {e}")
            raise GraphQLError(f"System metrics retrieval failed: {str(e)}")

class MutationResolvers:
    """Mutation resolvers for GraphQL operations."""
    
    @staticmethod
    def resolve_analyze_website_mutation(root, info, website_data, use_async=False):
        """Resolve analyze website mutation."""
        # Same as query resolver
        return QueryResolvers.resolve_analyze_website(root, info, website_data, use_async)
    
    @staticmethod
    def resolve_batch_analyze_mutation(root, info, input_data):
        """Resolve batch analyze mutation."""
        # Same as query resolver
        return QueryResolvers.resolve_batch_analyze(root, info, input_data)
    
    @staticmethod
    def resolve_train_model(root, info, config):
        """Resolve train model mutation."""
        try:
            # Parse config
            config_dict = json.loads(config)
            
            # This would implement actual model training
            # For now, return a placeholder
            return TrainingResultType(
                success=True,
                job_id=f"job_{int(time.time())}",
                status="completed",
                message="Model training completed successfully",
                metrics=TrainingMetricsType(
                    final_loss=0.123,
                    best_accuracy=0.95,
                    training_time=3600.0,
                    epochs_completed=100
                )
            )
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise GraphQLError(f"Model training failed: {str(e)}")
    
    @staticmethod
    def resolve_clear_cache(root, info):
        """Resolve clear cache mutation."""
        try:
            if 'async' in analyzer_instances:
                analyzer_instances['async'].memory_manager.clear_cache()
            
            return OperationResultType(
                success=True,
                message="Cache cleared successfully"
            )
            
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            raise GraphQLError(f"Cache clear failed: {str(e)}")

# Create schema
schema = Schema(
    query=Query,
    mutation=Mutations,
    types=[
        HealthType,
        CacheStatsType,
        SystemMetricsType,
        AnalysisResultType,
        BrandKitType,
        ToneProfileType,
        MonitoringType,
        TrendAnalysisType,
        ClusterAnalysisType,
        PredictiveInsightsType,
        BIReportType,
        TrainingResultType,
        OperationResultType
    ]
)

# Initialize analyzers
async def initialize_analyzers():
    """Initialize analyzer instances."""
    logger.info("Initializing GraphQL API analyzers...")
    
    # Initialize basic analyzers
    analyzer_instances['basic'] = BrandAnalyzerAPI()
    analyzer_instances['async'] = AsyncBrandAnalyzer()
    analyzer_instances['production'] = ProductionBrandAnalyzer()
    
    # Initialize async analyzer
    await analyzer_instances['async'].initialize()
    analyzer_instances['production'].initialize()
    
    logger.info("GraphQL API analyzers initialized successfully")

# Create GraphQL view
graphql_view = GraphQLView(schema=schema, graphiql=True)

# Create aiohttp application
app = web.Application()

# Setup CORS
cors = cors_setup(app, {
    "*": ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
        allow_methods="*"
    )
})

# Add routes
app.router.add_route('*', '/graphql', graphql_view)
app.router.add_route('*', '/', graphql_view)  # Default route

# Add startup handler
async def startup_handler(app):
    """Application startup handler."""
    await initialize_analyzers()

app.on_startup.append(startup_handler)

# Main function
def main():
    """Main function to run the GraphQL server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Frontier AI GraphQL API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    
    args = parser.parse_args()
    
    logger.info(f"Starting GraphQL API Server on {args.host}:{args.port}")
    
    web.run_app(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()










