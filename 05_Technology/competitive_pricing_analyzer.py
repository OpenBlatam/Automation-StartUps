#!/usr/bin/env python3
"""
Competitive Pricing Analysis System
===================================

This system facilitates competitive pricing strategies by automatically:
1. Collecting pricing data from multiple sources
2. Compiling tabular and narrative data
3. Analyzing pricing differences and advantages
4. Generating actionable insights for pricing strategies

Features:
- Automated data collection from web sources
- Tabular data processing and analysis
- Narrative data summarization
- Competitive advantage detection
- Real-time pricing monitoring
- Strategic pricing recommendations
"""

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import json
import sqlite3
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional, Any
import re
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import yaml
import schedule
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pricing_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataSource(Enum):
    """Enumeration of data sources for pricing information"""
    WEB_SCRAPING = "web_scraping"
    API = "api"
    MANUAL_INPUT = "manual_input"
    CSV_IMPORT = "csv_import"
    DATABASE = "database"

@dataclass
class PricingData:
    """Data structure for pricing information"""
    product_id: str
    product_name: str
    competitor: str
    price: float
    currency: str
    date_collected: datetime
    source: DataSource
    additional_data: Dict[str, Any] = None

@dataclass
class CompetitiveInsight:
    """Data structure for competitive insights"""
    insight_type: str
    description: str
    impact_score: float
    recommendation: str
    confidence: float
    supporting_data: Dict[str, Any]

class CompetitivePricingAnalyzer:
    """
    Main class for competitive pricing analysis
    """
    
    def __init__(self, config_file: str = "pricing_config.yaml"):
        """Initialize the pricing analyzer with configuration"""
        self.config = self._load_config(config_file)
        self.db_path = self.config.get('database_path', 'pricing_analysis.db')
        self.data_sources = self.config.get('data_sources', {})
        self.products = self.config.get('products', [])
        self.competitors = self.config.get('competitors', [])
        
        # Initialize database
        self._init_database()
        
        # Initialize data collection modules
        self.web_scraper = WebScrapingModule(self.config.get('web_scraping', {}))
        self.api_client = APIClientModule(self.config.get('api_sources', {}))
        self.data_processor = DataProcessingModule()
        self.insight_generator = InsightGenerator()
        
        logger.info("Competitive Pricing Analyzer initialized successfully")
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'database_path': 'pricing_analysis.db',
            'data_sources': {
                'web_scraping': {
                    'enabled': True,
                    'delay_between_requests': 1,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                'api_sources': {
                    'enabled': True,
                    'rate_limit': 100
                }
            },
            'products': [],
            'competitors': [],
            'analysis_settings': {
                'price_change_threshold': 0.05,
                'confidence_threshold': 0.7,
                'update_frequency': 'daily'
            }
        }
    
    def _init_database(self):
        """Initialize SQLite database for storing pricing data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pricing_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                competitor TEXT NOT NULL,
                price REAL NOT NULL,
                currency TEXT NOT NULL,
                date_collected TIMESTAMP NOT NULL,
                source TEXT NOT NULL,
                additional_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competitive_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT NOT NULL,
                description TEXT NOT NULL,
                impact_score REAL NOT NULL,
                recommendation TEXT NOT NULL,
                confidence REAL NOT NULL,
                supporting_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pricing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                competitor TEXT NOT NULL,
                price REAL NOT NULL,
                price_change REAL,
                date_collected TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    async def collect_pricing_data(self) -> List[PricingData]:
        """Collect pricing data from all configured sources"""
        logger.info("Starting pricing data collection...")
        
        all_data = []
        
        # Collect from web scraping
        if self.data_sources.get('web_scraping', {}).get('enabled', False):
            web_data = await self.web_scraper.collect_data(self.products, self.competitors)
            all_data.extend(web_data)
        
        # Collect from APIs
        if self.data_sources.get('api_sources', {}).get('enabled', False):
            api_data = await self.api_client.collect_data(self.products, self.competitors)
            all_data.extend(api_data)
        
        # Store data in database
        self._store_pricing_data(all_data)
        
        logger.info(f"Collected {len(all_data)} pricing data points")
        return all_data
    
    def _store_pricing_data(self, data: List[PricingData]):
        """Store pricing data in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for item in data:
            cursor.execute('''
                INSERT INTO pricing_data 
                (product_id, product_name, competitor, price, currency, date_collected, source, additional_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.product_id,
                item.product_name,
                item.competitor,
                item.price,
                item.currency,
                item.date_collected,
                item.source.value,
                json.dumps(item.additional_data) if item.additional_data else None
            ))
        
        conn.commit()
        conn.close()
    
    def analyze_pricing_differences(self) -> List[CompetitiveInsight]:
        """Analyze pricing differences and generate insights"""
        logger.info("Analyzing pricing differences...")
        
        # Get latest pricing data
        pricing_data = self._get_latest_pricing_data()
        
        if not pricing_data:
            logger.warning("No pricing data available for analysis")
            return []
        
        insights = []
        
        # Analyze price gaps
        price_gap_insights = self._analyze_price_gaps(pricing_data)
        insights.extend(price_gap_insights)
        
        # Analyze price trends
        trend_insights = self._analyze_price_trends()
        insights.extend(trend_insights)
        
        # Analyze competitive positioning
        positioning_insights = self._analyze_competitive_positioning(pricing_data)
        insights.extend(positioning_insights)
        
        # Store insights
        self._store_insights(insights)
        
        logger.info(f"Generated {len(insights)} competitive insights")
        return insights
    
    def _get_latest_pricing_data(self) -> pd.DataFrame:
        """Get latest pricing data from database"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT product_id, product_name, competitor, price, currency, date_collected, source
            FROM pricing_data
            WHERE date_collected >= date('now', '-7 days')
            ORDER BY date_collected DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def _analyze_price_gaps(self, data: pd.DataFrame) -> List[CompetitiveInsight]:
        """Analyze price gaps between competitors"""
        insights = []
        
        for product in data['product_id'].unique():
            product_data = data[data['product_id'] == product]
            
            if len(product_data) < 2:
                continue
            
            prices = product_data['price'].values
            competitors = product_data['competitor'].values
            
            # Calculate price statistics
            min_price = np.min(prices)
            max_price = np.max(prices)
            avg_price = np.mean(prices)
            price_range = max_price - min_price
            price_variance = np.var(prices)
            
            # Identify price leaders and followers
            min_competitor = competitors[np.argmin(prices)]
            max_competitor = competitors[np.argmax(prices)]
            
            # Generate insights based on price gaps
            if price_range / avg_price > 0.2:  # Significant price variation
                insight = CompetitiveInsight(
                    insight_type="price_gap",
                    description=f"Significant price gap detected for {product_data.iloc[0]['product_name']}. "
                               f"Price range: {min_price:.2f} - {max_price:.2f} ({price_range:.2f} difference)",
                    impact_score=0.8,
                    recommendation=f"Consider pricing strategy between {min_competitor} (lowest) and {max_competitor} (highest)",
                    confidence=0.9,
                    supporting_data={
                        'product_id': product,
                        'price_range': price_range,
                        'price_variance': price_variance,
                        'min_competitor': min_competitor,
                        'max_competitor': max_competitor
                    }
                )
                insights.append(insight)
        
        return insights
    
    def _analyze_price_trends(self) -> List[CompetitiveInsight]:
        """Analyze price trends over time"""
        insights = []
        
        conn = sqlite3.connect(self.db_path)
        
        # Get historical data
        query = '''
            SELECT product_id, competitor, price, date_collected
            FROM pricing_data
            WHERE date_collected >= date('now', '-30 days')
            ORDER BY product_id, competitor, date_collected
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return insights
        
        # Analyze trends for each product-competitor combination
        for (product_id, competitor), group in df.groupby(['product_id', 'competitor']):
            if len(group) < 3:  # Need at least 3 data points for trend analysis
                continue
            
            prices = group['price'].values
            dates = pd.to_datetime(group['date_collected']).values
            
            # Calculate price change trend
            price_changes = np.diff(prices)
            avg_change = np.mean(price_changes)
            change_volatility = np.std(price_changes)
            
            # Determine trend direction
            if avg_change > 0.05:
                trend = "increasing"
                recommendation = "Monitor for potential price increase opportunity"
            elif avg_change < -0.05:
                trend = "decreasing"
                recommendation = "Consider competitive response or value differentiation"
            else:
                trend = "stable"
                recommendation = "Maintain current pricing strategy"
            
            insight = CompetitiveInsight(
                insight_type="price_trend",
                description=f"{competitor} shows {trend} price trend for {product_id} "
                           f"(avg change: {avg_change:.2f} per period)",
                impact_score=0.6,
                recommendation=recommendation,
                confidence=0.7,
                supporting_data={
                    'product_id': product_id,
                    'competitor': competitor,
                    'trend': trend,
                    'avg_change': avg_change,
                    'volatility': change_volatility
                }
            )
            insights.append(insight)
        
        return insights
    
    def _analyze_competitive_positioning(self, data: pd.DataFrame) -> List[CompetitiveInsight]:
        """Analyze competitive positioning based on pricing"""
        insights = []
        
        # Group by product and analyze positioning
        for product in data['product_id'].unique():
            product_data = data[data['product_id'] == product]
            
            if len(product_data) < 2:
                continue
            
            # Calculate market position metrics
            prices = product_data['price'].values
            competitors = product_data['competitor'].values
            
            # Sort by price
            sorted_indices = np.argsort(prices)
            sorted_competitors = competitors[sorted_indices]
            sorted_prices = prices[sorted_indices]
            
            # Identify market segments
            low_price_segment = sorted_competitors[:len(sorted_competitors)//3]
            mid_price_segment = sorted_competitors[len(sorted_competitors)//3:2*len(sorted_competitors)//3]
            high_price_segment = sorted_competitors[2*len(sorted_competitors)//3:]
            
            # Generate positioning insights
            insight = CompetitiveInsight(
                insight_type="competitive_positioning",
                description=f"Market positioning for {product_data.iloc[0]['product_name']}: "
                           f"Low-price: {', '.join(low_price_segment)}, "
                           f"Mid-price: {', '.join(mid_price_segment)}, "
                           f"High-price: {', '.join(high_price_segment)}",
                impact_score=0.7,
                recommendation="Consider positioning strategy based on target market segment",
                confidence=0.8,
                supporting_data={
                    'product_id': product,
                    'low_price_segment': list(low_price_segment),
                    'mid_price_segment': list(mid_price_segment),
                    'high_price_segment': list(high_price_segment),
                    'price_distribution': dict(zip(sorted_competitors, sorted_prices))
                }
            )
            insights.append(insight)
        
        return insights
    
    def _store_insights(self, insights: List[CompetitiveInsight]):
        """Store insights in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for insight in insights:
            cursor.execute('''
                INSERT INTO competitive_insights 
                (insight_type, description, impact_score, recommendation, confidence, supporting_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                insight.insight_type,
                insight.description,
                insight.impact_score,
                insight.recommendation,
                insight.confidence,
                json.dumps(insight.supporting_data)
            ))
        
        conn.commit()
        conn.close()
    
    def generate_pricing_report(self) -> Dict[str, Any]:
        """Generate comprehensive pricing analysis report"""
        logger.info("Generating pricing analysis report...")
        
        # Get latest data and insights
        pricing_data = self._get_latest_pricing_data()
        insights = self._get_latest_insights()
        
        # Calculate summary statistics
        summary_stats = self._calculate_summary_statistics(pricing_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(insights)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary_statistics': summary_stats,
            'insights': [
                {
                    'type': insight.insight_type,
                    'description': insight.description,
                    'impact_score': insight.impact_score,
                    'recommendation': insight.recommendation,
                    'confidence': insight.confidence
                }
                for insight in insights
            ],
            'recommendations': recommendations,
            'data_quality': self._assess_data_quality(pricing_data)
        }
        
        return report
    
    def _get_latest_insights(self) -> List[CompetitiveInsight]:
        """Get latest insights from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT insight_type, description, impact_score, recommendation, confidence, supporting_data
            FROM competitive_insights
            WHERE created_at >= date('now', '-7 days')
            ORDER BY impact_score DESC, confidence DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        insights = []
        for row in rows:
            insight = CompetitiveInsight(
                insight_type=row[0],
                description=row[1],
                impact_score=row[2],
                recommendation=row[3],
                confidence=row[4],
                supporting_data=json.loads(row[5]) if row[5] else {}
            )
            insights.append(insight)
        
        return insights
    
    def _calculate_summary_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate summary statistics for pricing data"""
        if data.empty:
            return {}
        
        stats = {
            'total_products': data['product_id'].nunique(),
            'total_competitors': data['competitor'].nunique(),
            'total_data_points': len(data),
            'average_price': data['price'].mean(),
            'price_range': {
                'min': data['price'].min(),
                'max': data['price'].max(),
                'std': data['price'].std()
            },
            'data_freshness': {
                'latest_collection': data['date_collected'].max(),
                'oldest_collection': data['date_collected'].min()
            }
        }
        
        return stats
    
    def _generate_recommendations(self, insights: List[CompetitiveInsight]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on insights"""
        recommendations = []
        
        # Group insights by type
        insight_groups = {}
        for insight in insights:
            if insight.insight_type not in insight_groups:
                insight_groups[insight.insight_type] = []
            insight_groups[insight.insight_type].append(insight)
        
        # Generate recommendations for each insight type
        for insight_type, type_insights in insight_groups.items():
            if insight_type == "price_gap":
                recommendations.append({
                    'category': 'Pricing Strategy',
                    'priority': 'High',
                    'action': 'Review pricing gaps and consider competitive positioning',
                    'details': f"Found {len(type_insights)} significant price gaps that require attention"
                })
            elif insight_type == "price_trend":
                recommendations.append({
                    'category': 'Market Monitoring',
                    'priority': 'Medium',
                    'action': 'Monitor competitor price trends and adjust strategy accordingly',
                    'details': f"Identified {len(type_insights)} price trend patterns"
                })
            elif insight_type == "competitive_positioning":
                recommendations.append({
                    'category': 'Strategic Positioning',
                    'priority': 'High',
                    'action': 'Analyze market positioning and consider segment targeting',
                    'details': f"Market positioning analysis completed for {len(type_insights)} products"
                })
        
        return recommendations
    
    def _assess_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Assess the quality of collected pricing data"""
        if data.empty:
            return {'score': 0, 'issues': ['No data available']}
        
        issues = []
        score = 100
        
        # Check for missing data
        missing_data = data.isnull().sum()
        if missing_data.any():
            issues.append(f"Missing data in columns: {missing_data[missing_data > 0].to_dict()}")
            score -= 20
        
        # Check data recency
        latest_date = pd.to_datetime(data['date_collected']).max()
        days_old = (datetime.now() - latest_date).days
        if days_old > 7:
            issues.append(f"Data is {days_old} days old")
            score -= 30
        
        # Check data completeness
        expected_combinations = len(data['product_id'].unique()) * len(data['competitor'].unique())
        actual_combinations = len(data.groupby(['product_id', 'competitor']))
        completeness = actual_combinations / expected_combinations if expected_combinations > 0 else 0
        
        if completeness < 0.8:
            issues.append(f"Data completeness: {completeness:.1%}")
            score -= 25
        
        return {
            'score': max(0, score),
            'issues': issues,
            'completeness': completeness,
            'data_age_days': days_old
        }
    
    def export_to_excel(self, filename: str = None):
        """Export pricing analysis to Excel file"""
        if filename is None:
            filename = f"pricing_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Export pricing data
            pricing_data = self._get_latest_pricing_data()
            if not pricing_data.empty:
                pricing_data.to_excel(writer, sheet_name='Pricing Data', index=False)
            
            # Export insights
            insights = self._get_latest_insights()
            if insights:
                insights_df = pd.DataFrame([
                    {
                        'Type': insight.insight_type,
                        'Description': insight.description,
                        'Impact Score': insight.impact_score,
                        'Recommendation': insight.recommendation,
                        'Confidence': insight.confidence
                    }
                    for insight in insights
                ])
                insights_df.to_excel(writer, sheet_name='Insights', index=False)
            
            # Export summary report
            report = self.generate_pricing_report()
            summary_df = pd.DataFrame([
                {'Metric': k, 'Value': v} for k, v in report['summary_statistics'].items()
            ])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        logger.info(f"Report exported to {filename}")
        return filename

class WebScrapingModule:
    """Module for web scraping pricing data"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        })
    
    async def collect_data(self, products: List[str], competitors: List[str]) -> List[PricingData]:
        """Collect pricing data through web scraping"""
        # This is a simplified implementation
        # In practice, you would implement specific scrapers for each competitor's website
        
        data = []
        
        # Example implementation for demonstration
        for product in products:
            for competitor in competitors:
                try:
                    # Simulate price collection (replace with actual scraping logic)
                    price = await self._scrape_price(product, competitor)
                    
                    if price:
                        pricing_data = PricingData(
                            product_id=product,
                            product_name=product,
                            competitor=competitor,
                            price=price,
                            currency='USD',
                            date_collected=datetime.now(),
                            source=DataSource.WEB_SCRAPING,
                            additional_data={'scraped_from': f"{competitor}_website"}
                        )
                        data.append(pricing_data)
                        
                        # Respect rate limits
                        await asyncio.sleep(self.config.get('delay_between_requests', 1))
                        
                except Exception as e:
                    logger.error(f"Error scraping {product} from {competitor}: {e}")
        
        return data
    
    async def _scrape_price(self, product: str, competitor: str) -> Optional[float]:
        """Scrape price for a specific product from a competitor"""
        # This is a placeholder implementation
        # In practice, you would implement specific scraping logic for each competitor
        
        # Simulate price data (replace with actual scraping)
        import random
        base_price = random.uniform(10, 1000)
        return round(base_price, 2)

class APIClientModule:
    """Module for API-based data collection"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.api_keys = config.get('api_keys', {})
    
    async def collect_data(self, products: List[str], competitors: List[str]) -> List[PricingData]:
        """Collect pricing data through APIs"""
        data = []
        
        # Example implementation for demonstration
        for product in products:
            for competitor in competitors:
                try:
                    # Simulate API call (replace with actual API integration)
                    price = await self._fetch_price_from_api(product, competitor)
                    
                    if price:
                        pricing_data = PricingData(
                            product_id=product,
                            product_name=product,
                            competitor=competitor,
                            price=price,
                            currency='USD',
                            date_collected=datetime.now(),
                            source=DataSource.API,
                            additional_data={'api_source': f"{competitor}_api"}
                        )
                        data.append(pricing_data)
                        
                except Exception as e:
                    logger.error(f"Error fetching {product} from {competitor} API: {e}")
        
        return data
    
    async def _fetch_price_from_api(self, product: str, competitor: str) -> Optional[float]:
        """Fetch price from competitor API"""
        # This is a placeholder implementation
        # In practice, you would implement specific API calls for each competitor
        
        # Simulate API response (replace with actual API call)
        import random
        base_price = random.uniform(10, 1000)
        return round(base_price, 2)

class DataProcessingModule:
    """Module for processing and cleaning pricing data"""
    
    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize pricing data"""
        # Remove duplicates
        data = data.drop_duplicates()
        
        # Standardize currency
        data['currency'] = data['currency'].str.upper()
        
        # Convert prices to standard currency (USD)
        data = self._convert_currency(data)
        
        # Remove outliers
        data = self._remove_outliers(data)
        
        return data
    
    def _convert_currency(self, data: pd.DataFrame) -> pd.DataFrame:
        """Convert all prices to USD"""
        # This is a simplified implementation
        # In practice, you would use a real currency conversion API
        
        conversion_rates = {
            'EUR': 1.1,
            'GBP': 1.3,
            'JPY': 0.007,
            'CAD': 0.75
        }
        
        for currency, rate in conversion_rates.items():
            mask = data['currency'] == currency
            data.loc[mask, 'price'] = data.loc[mask, 'price'] * rate
            data.loc[mask, 'currency'] = 'USD'
        
        return data
    
    def _remove_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """Remove price outliers using IQR method"""
        for product in data['product_id'].unique():
            product_data = data[data['product_id'] == product]
            
            if len(product_data) < 4:  # Need at least 4 points for IQR
                continue
            
            Q1 = product_data['price'].quantile(0.25)
            Q3 = product_data['price'].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Remove outliers
            outlier_mask = (product_data['price'] < lower_bound) | (product_data['price'] > upper_bound)
            data = data.drop(product_data[outlier_mask].index)
        
        return data

class InsightGenerator:
    """Module for generating competitive insights"""
    
    def generate_insights(self, data: pd.DataFrame) -> List[CompetitiveInsight]:
        """Generate insights from pricing data"""
        insights = []
        
        # Price gap analysis
        price_gap_insights = self._analyze_price_gaps(data)
        insights.extend(price_gap_insights)
        
        # Market positioning analysis
        positioning_insights = self._analyze_market_positioning(data)
        insights.extend(positioning_insights)
        
        # Competitive advantage analysis
        advantage_insights = self._analyze_competitive_advantages(data)
        insights.extend(advantage_insights)
        
        return insights
    
    def _analyze_price_gaps(self, data: pd.DataFrame) -> List[CompetitiveInsight]:
        """Analyze price gaps between competitors"""
        insights = []
        
        for product in data['product_id'].unique():
            product_data = data[data['product_id'] == product]
            
            if len(product_data) < 2:
                continue
            
            prices = product_data['price'].values
            competitors = product_data['competitor'].values
            
            # Calculate price statistics
            min_price = np.min(prices)
            max_price = np.max(prices)
            avg_price = np.mean(prices)
            price_range = max_price - min_price
            
            # Generate insight if significant gap exists
            if price_range / avg_price > 0.2:
                insight = CompetitiveInsight(
                    insight_type="price_gap",
                    description=f"Significant price gap of {price_range:.2f} ({price_range/avg_price:.1%}) for {product}",
                    impact_score=0.8,
                    recommendation="Consider pricing strategy to capture market share",
                    confidence=0.9,
                    supporting_data={
                        'product_id': product,
                        'price_range': price_range,
                        'price_gap_percentage': price_range/avg_price
                    }
                )
                insights.append(insight)
        
        return insights
    
    def _analyze_market_positioning(self, data: pd.DataFrame) -> List[CompetitiveInsight]:
        """Analyze market positioning based on pricing"""
        insights = []
        
        for product in data['product_id'].unique():
            product_data = data[data['product_id'] == product]
            
            if len(product_data) < 3:
                continue
            
            prices = product_data['price'].values
            competitors = product_data['competitor'].values
            
            # Calculate market position
            sorted_indices = np.argsort(prices)
            sorted_competitors = competitors[sorted_indices]
            
            # Identify market segments
            n = len(sorted_competitors)
            low_price = sorted_competitors[:n//3]
            mid_price = sorted_competitors[n//3:2*n//3]
            high_price = sorted_competitors[2*n//3:]
            
            insight = CompetitiveInsight(
                insight_type="market_positioning",
                description=f"Market segments for {product}: Low-price ({', '.join(low_price)}), "
                           f"Mid-price ({', '.join(mid_price)}), High-price ({', '.join(high_price)})",
                impact_score=0.7,
                recommendation="Consider targeting specific market segment based on value proposition",
                confidence=0.8,
                supporting_data={
                    'product_id': product,
                    'low_price_segment': list(low_price),
                    'mid_price_segment': list(mid_price),
                    'high_price_segment': list(high_price)
                }
            )
            insights.append(insight)
        
        return insights
    
    def _analyze_competitive_advantages(self, data: pd.DataFrame) -> List[CompetitiveInsight]:
        """Analyze competitive advantages based on pricing"""
        insights = []
        
        # This is a simplified implementation
        # In practice, you would analyze more complex competitive factors
        
        for product in data['product_id'].unique():
            product_data = data[data['product_id'] == product]
            
            if len(product_data) < 2:
                continue
            
            # Find the most competitive price
            min_price = product_data['price'].min()
            min_competitor = product_data[product_data['price'] == min_price]['competitor'].iloc[0]
            
            insight = CompetitiveInsight(
                insight_type="competitive_advantage",
                description=f"{min_competitor} offers the most competitive price for {product} at {min_price:.2f}",
                impact_score=0.6,
                recommendation="Monitor {min_competitor}'s pricing strategy and consider competitive response",
                confidence=0.8,
                supporting_data={
                    'product_id': product,
                    'most_competitive': min_competitor,
                    'competitive_price': min_price
                }
            )
            insights.append(insight)
        
        return insights

def main():
    """Main function to run the competitive pricing analyzer"""
    # Initialize analyzer
    analyzer = CompetitivePricingAnalyzer()
    
    # Run analysis
    print("Starting Competitive Pricing Analysis...")
    
    # Collect data
    asyncio.run(analyzer.collect_pricing_data())
    
    # Analyze pricing differences
    insights = analyzer.analyze_pricing_differences()
    
    # Generate report
    report = analyzer.generate_pricing_report()
    
    # Export to Excel
    filename = analyzer.export_to_excel()
    
    print(f"Analysis complete! Report exported to {filename}")
    print(f"Generated {len(insights)} insights")
    
    # Print summary
    print("\n=== PRICING ANALYSIS SUMMARY ===")
    print(f"Products analyzed: {report['summary_statistics'].get('total_products', 0)}")
    print(f"Competitors tracked: {report['summary_statistics'].get('total_competitors', 0)}")
    print(f"Data points collected: {report['summary_statistics'].get('total_data_points', 0)}")
    print(f"Average price: ${report['summary_statistics'].get('average_price', 0):.2f}")
    
    print("\n=== TOP INSIGHTS ===")
    for i, insight in enumerate(insights[:5], 1):
        print(f"{i}. {insight.description}")
        print(f"   Recommendation: {insight.recommendation}")
        print(f"   Impact Score: {insight.impact_score:.2f}")
        print()

if __name__ == "__main__":
    main()






