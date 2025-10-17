# 📊 Real-Time Analytics Engine - IA Bulk Platform

> **Complete Real-Time Analytics and Business Intelligence System**

## 🎯 Overview

This guide provides comprehensive instructions for building and deploying a real-time analytics engine in the IA Bulk Platform, including streaming data processing, real-time dashboards, and advanced business intelligence capabilities.

## 🏗️ Real-Time Analytics Architecture

### Streaming Data Pipeline

```python
# Real-Time Analytics Engine Architecture
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from kafka import KafkaProducer, KafkaConsumer
from redis import Redis
import psycopg2
from elasticsearch import Elasticsearch
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass
import logging

@dataclass
class AnalyticsEvent:
    event_type: str
    user_id: str
    timestamp: datetime
    properties: Dict[str, Any]
    session_id: str
    campaign_id: Optional[str] = None

class RealTimeAnalyticsEngine:
    def __init__(self):
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.kafka_consumer = KafkaConsumer(
            'analytics-events',
            bootstrap_servers=['kafka:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        self.redis_client = Redis(host='redis', port=6379, db=0)
        self.elasticsearch_client = Elasticsearch(['elasticsearch:9200'])
        self.postgres_client = psycopg2.connect(
            host='postgres',
            database='ia_bulk_analytics',
            user='analytics_user',
            password='analytics_password'
        )
        
        self.event_processors = {
            'user_registration': UserRegistrationProcessor(),
            'email_sent': EmailSentProcessor(),
            'email_opened': EmailOpenedProcessor(),
            'email_clicked': EmailClickedProcessor(),
            'referral_made': ReferralMadeProcessor(),
            'contest_joined': ContestJoinedProcessor(),
            'conversion': ConversionProcessor()
        }
        
        self.metrics_calculators = {
            'engagement_rate': EngagementRateCalculator(),
            'conversion_rate': ConversionRateCalculator(),
            'revenue_metrics': RevenueMetricsCalculator(),
            'user_behavior': UserBehaviorCalculator()
        }
    
    async def start_analytics_engine(self):
        """Start the real-time analytics engine"""
        logging.info("Starting Real-Time Analytics Engine...")
        
        # Start event processing
        asyncio.create_task(self.process_events())
        
        # Start metrics calculation
        asyncio.create_task(self.calculate_metrics())
        
        # Start dashboard updates
        asyncio.create_task(self.update_dashboards())
        
        logging.info("Real-Time Analytics Engine started successfully")
    
    async def process_events(self):
        """Process incoming analytics events in real-time"""
        for message in self.kafka_consumer:
            try:
                event_data = message.value
                event = AnalyticsEvent(**event_data)
                
                # Process event with appropriate processor
                processor = self.event_processors.get(event.event_type)
                if processor:
                    await processor.process(event)
                
                # Store event in multiple systems
                await self.store_event(event)
                
                # Update real-time metrics
                await self.update_realtime_metrics(event)
                
            except Exception as e:
                logging.error(f"Error processing event: {e}")
    
    async def store_event(self, event: AnalyticsEvent):
        """Store event in multiple storage systems"""
        
        # Store in Redis for real-time access
        await self.store_in_redis(event)
        
        # Store in Elasticsearch for search and analytics
        await self.store_in_elasticsearch(event)
        
        # Store in PostgreSQL for structured queries
        await self.store_in_postgresql(event)
    
    async def store_in_redis(self, event: AnalyticsEvent):
        """Store event in Redis for real-time metrics"""
        key = f"event:{event.event_type}:{event.timestamp.strftime('%Y%m%d%H%M')}"
        self.redis_client.incr(key)
        self.redis_client.expire(key, 3600)  # Expire after 1 hour
        
        # Store user-specific metrics
        user_key = f"user:{event.user_id}:{event.event_type}"
        self.redis_client.incr(user_key)
        self.redis_client.expire(user_key, 86400)  # Expire after 24 hours
    
    async def store_in_elasticsearch(self, event: AnalyticsEvent):
        """Store event in Elasticsearch for search and analytics"""
        index_name = f"analytics-events-{event.timestamp.strftime('%Y.%m.%d')}"
        
        document = {
            'event_type': event.event_type,
            'user_id': event.user_id,
            'timestamp': event.timestamp.isoformat(),
            'properties': event.properties,
            'session_id': event.session_id,
            'campaign_id': event.campaign_id
        }
        
        self.elasticsearch_client.index(
            index=index_name,
            body=document
        )
    
    async def store_in_postgresql(self, event: AnalyticsEvent):
        """Store event in PostgreSQL for structured queries"""
        cursor = self.postgres_client.cursor()
        
        query = """
            INSERT INTO analytics_events 
            (event_type, user_id, timestamp, properties, session_id, campaign_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            event.event_type,
            event.user_id,
            event.timestamp,
            json.dumps(event.properties),
            event.session_id,
            event.campaign_id
        ))
        
        self.postgres_client.commit()
        cursor.close()
```

### Real-Time Metrics Calculation

```python
# Real-Time Metrics Calculation System
class RealTimeMetricsCalculator:
    def __init__(self):
        self.redis_client = Redis(host='redis', port=6379, db=1)
        self.metrics_cache = {}
        self.calculation_intervals = {
            'realtime': 1,      # 1 second
            'minute': 60,       # 1 minute
            'hour': 3600,       # 1 hour
            'day': 86400        # 1 day
        }
    
    async def calculate_realtime_metrics(self):
        """Calculate real-time metrics continuously"""
        while True:
            try:
                # Calculate engagement metrics
                engagement_metrics = await self.calculate_engagement_metrics()
                
                # Calculate conversion metrics
                conversion_metrics = await self.calculate_conversion_metrics()
                
                # Calculate revenue metrics
                revenue_metrics = await self.calculate_revenue_metrics()
                
                # Calculate user behavior metrics
                behavior_metrics = await self.calculate_behavior_metrics()
                
                # Store metrics in cache
                await self.store_metrics({
                    'engagement': engagement_metrics,
                    'conversion': conversion_metrics,
                    'revenue': revenue_metrics,
                    'behavior': behavior_metrics,
                    'timestamp': datetime.now().isoformat()
                })
                
                await asyncio.sleep(self.calculation_intervals['realtime'])
                
            except Exception as e:
                logging.error(f"Error calculating real-time metrics: {e}")
                await asyncio.sleep(5)
    
    async def calculate_engagement_metrics(self):
        """Calculate real-time engagement metrics"""
        current_time = datetime.now()
        
        # Email engagement metrics
        email_opens_1h = await self.get_event_count('email_opened', current_time - timedelta(hours=1))
        email_sends_1h = await self.get_event_count('email_sent', current_time - timedelta(hours=1))
        email_clicks_1h = await self.get_event_count('email_clicked', current_time - timedelta(hours=1))
        
        # Calculate rates
        open_rate = (email_opens_1h / max(email_sends_1h, 1)) * 100
        click_rate = (email_clicks_1h / max(email_sends_1h, 1)) * 100
        click_to_open_rate = (email_clicks_1h / max(email_opens_1h, 1)) * 100
        
        return {
            'email_open_rate_1h': round(open_rate, 2),
            'email_click_rate_1h': round(click_rate, 2),
            'click_to_open_rate_1h': round(click_to_open_rate, 2),
            'total_opens_1h': email_opens_1h,
            'total_clicks_1h': email_clicks_1h,
            'total_sends_1h': email_sends_1h
        }
    
    async def calculate_conversion_metrics(self):
        """Calculate real-time conversion metrics"""
        current_time = datetime.now()
        
        # Conversion metrics
        conversions_1h = await self.get_event_count('conversion', current_time - timedelta(hours=1))
        referrals_1h = await self.get_event_count('referral_made', current_time - timedelta(hours=1))
        contest_joins_1h = await self.get_event_count('contest_joined', current_time - timedelta(hours=1))
        
        # Calculate rates
        referral_conversion_rate = (conversions_1h / max(referrals_1h, 1)) * 100
        contest_conversion_rate = (conversions_1h / max(contest_joins_1h, 1)) * 100
        
        return {
            'conversions_1h': conversions_1h,
            'referrals_1h': referrals_1h,
            'contest_joins_1h': contest_joins_1h,
            'referral_conversion_rate_1h': round(referral_conversion_rate, 2),
            'contest_conversion_rate_1h': round(contest_conversion_rate, 2)
        }
    
    async def calculate_revenue_metrics(self):
        """Calculate real-time revenue metrics"""
        current_time = datetime.now()
        
        # Revenue metrics
        revenue_1h = await self.get_revenue_sum(current_time - timedelta(hours=1))
        revenue_24h = await self.get_revenue_sum(current_time - timedelta(hours=24))
        
        # Calculate growth
        revenue_growth_24h = await self.calculate_revenue_growth()
        
        return {
            'revenue_1h': revenue_1h,
            'revenue_24h': revenue_24h,
            'revenue_growth_24h': round(revenue_growth_24h, 2),
            'revenue_per_conversion': revenue_1h / max(await self.get_event_count('conversion', current_time - timedelta(hours=1)), 1)
        }
    
    async def get_event_count(self, event_type: str, since: datetime) -> int:
        """Get count of events since specified time"""
        key = f"event_count:{event_type}:{since.strftime('%Y%m%d%H%M')}"
        return int(self.redis_client.get(key) or 0)
    
    async def get_revenue_sum(self, since: datetime) -> float:
        """Get total revenue since specified time"""
        key = f"revenue_sum:{since.strftime('%Y%m%d%H%M')}"
        return float(self.redis_client.get(key) or 0)
```

### Real-Time Dashboard System

```python
# Real-Time Dashboard System
class RealTimeDashboard:
    def __init__(self):
        self.redis_client = Redis(host='redis', port=6379, db=2)
        self.metrics_calculator = RealTimeMetricsCalculator()
        self.alerting_system = AlertingSystem()
    
    def create_executive_dashboard(self):
        """Create executive-level real-time dashboard"""
        st.set_page_config(
            page_title="IA Bulk - Executive Dashboard",
            page_icon="📊",
            layout="wide"
        )
        
        st.title("🚀 IA Bulk - Real-Time Executive Dashboard")
        
        # Key Performance Indicators
        self.display_kpis()
        
        # Real-time metrics
        self.display_realtime_metrics()
        
        # Revenue and conversion trends
        self.display_revenue_trends()
        
        # User engagement metrics
        self.display_engagement_metrics()
        
        # Campaign performance
        self.display_campaign_performance()
        
        # Alerts and notifications
        self.display_alerts()
    
    def display_kpis(self):
        """Display key performance indicators"""
        st.subheader("📈 Key Performance Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            revenue_24h = self.get_metric('revenue_24h')
            st.metric(
                label="Revenue (24h)",
                value=f"${revenue_24h:,.2f}",
                delta=f"{self.get_metric('revenue_growth_24h'):.1f}%"
            )
        
        with col2:
            conversions_24h = self.get_metric('conversions_24h')
            st.metric(
                label="Conversions (24h)",
                value=f"{conversions_24h:,}",
                delta=f"{self.get_metric('conversion_growth_24h'):.1f}%"
            )
        
        with col3:
            active_users_24h = self.get_metric('active_users_24h')
            st.metric(
                label="Active Users (24h)",
                value=f"{active_users_24h:,}",
                delta=f"{self.get_metric('user_growth_24h'):.1f}%"
            )
        
        with col4:
            engagement_rate = self.get_metric('engagement_rate_24h')
            st.metric(
                label="Engagement Rate (24h)",
                value=f"{engagement_rate:.1f}%",
                delta=f"{self.get_metric('engagement_growth_24h'):.1f}%"
            )
    
    def display_realtime_metrics(self):
        """Display real-time metrics"""
        st.subheader("⚡ Real-Time Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Real-time activity chart
            activity_data = self.get_realtime_activity_data()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=activity_data['timestamps'],
                y=activity_data['activity'],
                mode='lines',
                name='Activity',
                line=dict(color='#1f77b4')
            ))
            fig.update_layout(
                title="Real-Time Activity (Last Hour)",
                xaxis_title="Time",
                yaxis_title="Events per Minute"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Real-time conversion funnel
            funnel_data = self.get_conversion_funnel_data()
            fig = go.Figure(go.Funnel(
                y=funnel_data['stages'],
                x=funnel_data['values'],
                textinfo="value+percent initial"
            ))
            fig.update_layout(
                title="Real-Time Conversion Funnel",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def display_revenue_trends(self):
        """Display revenue trends"""
        st.subheader("💰 Revenue Trends")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue over time
            revenue_data = self.get_revenue_trend_data()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=revenue_data['timestamps'],
                y=revenue_data['revenue'],
                mode='lines+markers',
                name='Revenue',
                line=dict(color='#2ca02c')
            ))
            fig.update_layout(
                title="Revenue Trend (Last 24 Hours)",
                xaxis_title="Time",
                yaxis_title="Revenue ($)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Revenue by campaign
            campaign_revenue = self.get_campaign_revenue_data()
            fig = go.Figure(data=[
                go.Bar(
                    x=campaign_revenue['campaigns'],
                    y=campaign_revenue['revenue'],
                    marker_color='#ff7f0e'
                )
            ])
            fig.update_layout(
                title="Revenue by Campaign (Last 24 Hours)",
                xaxis_title="Campaign",
                yaxis_title="Revenue ($)"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def display_engagement_metrics(self):
        """Display user engagement metrics"""
        st.subheader("👥 User Engagement Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Email engagement rates
            email_metrics = self.get_email_engagement_data()
            fig = go.Figure(data=[
                go.Bar(
                    x=['Open Rate', 'Click Rate', 'Click-to-Open Rate'],
                    y=[email_metrics['open_rate'], email_metrics['click_rate'], email_metrics['cto_rate']],
                    marker_color=['#1f77b4', '#ff7f0e', '#2ca02c']
                )
            ])
            fig.update_layout(
                title="Email Engagement Rates (Last 24 Hours)",
                yaxis_title="Rate (%)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # User behavior heatmap
            behavior_data = self.get_user_behavior_heatmap()
            fig = go.Figure(data=go.Heatmap(
                z=behavior_data['values'],
                x=behavior_data['hours'],
                y=behavior_data['days'],
                colorscale='Viridis'
            ))
            fig.update_layout(
                title="User Activity Heatmap (Last 7 Days)",
                xaxis_title="Hour of Day",
                yaxis_title="Day of Week"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def display_campaign_performance(self):
        """Display campaign performance metrics"""
        st.subheader("📧 Campaign Performance")
        
        campaign_data = self.get_campaign_performance_data()
        
        # Campaign performance table
        df = pd.DataFrame(campaign_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # Campaign performance chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Campaign'],
            y=df['Open Rate'],
            mode='markers',
            name='Open Rate',
            marker=dict(size=df['Sends'], sizemode='diameter', sizeref=2)
        ))
        fig.update_layout(
            title="Campaign Performance (Bubble Size = Send Volume)",
            xaxis_title="Campaign",
            yaxis_title="Open Rate (%)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def display_alerts(self):
        """Display alerts and notifications"""
        st.subheader("🚨 Alerts & Notifications")
        
        alerts = self.get_active_alerts()
        
        for alert in alerts:
            if alert['severity'] == 'critical':
                st.error(f"🔴 {alert['message']}")
            elif alert['severity'] == 'warning':
                st.warning(f"🟡 {alert['message']}")
            else:
                st.info(f"🔵 {alert['message']}")
    
    def get_metric(self, metric_name: str):
        """Get metric value from cache"""
        return self.redis_client.get(f"metric:{metric_name}") or 0
```

### Advanced Analytics Queries

```python
# Advanced Analytics Query Engine
class AdvancedAnalyticsQueries:
    def __init__(self):
        self.elasticsearch_client = Elasticsearch(['elasticsearch:9200'])
        self.postgres_client = psycopg2.connect(
            host='postgres',
            database='ia_bulk_analytics',
            user='analytics_user',
            password='analytics_password'
        )
    
    async def cohort_analysis(self, cohort_type: str, time_range: str):
        """Perform cohort analysis"""
        
        if cohort_type == 'user_registration':
            return await self.user_registration_cohort_analysis(time_range)
        elif cohort_type == 'email_engagement':
            return await self.email_engagement_cohort_analysis(time_range)
        elif cohort_type == 'referral_behavior':
            return await self.referral_behavior_cohort_analysis(time_range)
    
    async def user_registration_cohort_analysis(self, time_range: str):
        """Analyze user registration cohorts"""
        
        query = """
            WITH user_cohorts AS (
                SELECT 
                    DATE_TRUNC('month', created_at) as cohort_month,
                    user_id,
                    created_at
                FROM users
                WHERE created_at >= NOW() - INTERVAL %s
            ),
            user_activity AS (
                SELECT 
                    uc.cohort_month,
                    uc.user_id,
                    DATE_TRUNC('month', ua.activity_date) as activity_month,
                    COUNT(*) as activity_count
                FROM user_cohorts uc
                JOIN user_activities ua ON uc.user_id = ua.user_id
                WHERE ua.activity_date >= uc.created_at
                GROUP BY uc.cohort_month, uc.user_id, DATE_TRUNC('month', ua.activity_date)
            )
            SELECT 
                cohort_month,
                activity_month,
                COUNT(DISTINCT user_id) as active_users,
                AVG(activity_count) as avg_activity
            FROM user_activity
            GROUP BY cohort_month, activity_month
            ORDER BY cohort_month, activity_month
        """
        
        cursor = self.postgres_client.cursor()
        cursor.execute(query, (time_range,))
        results = cursor.fetchall()
        cursor.close()
        
        return self.format_cohort_results(results)
    
    async def funnel_analysis(self, funnel_type: str, time_range: str):
        """Perform funnel analysis"""
        
        if funnel_type == 'email_conversion':
            return await self.email_conversion_funnel(time_range)
        elif funnel_type == 'referral_conversion':
            return await self.referral_conversion_funnel(time_range)
        elif funnel_type == 'user_onboarding':
            return await self.user_onboarding_funnel(time_range)
    
    async def email_conversion_funnel(self, time_range: str):
        """Analyze email conversion funnel"""
        
        query = """
            WITH email_funnel AS (
                SELECT 
                    user_id,
                    MAX(CASE WHEN event_type = 'email_sent' THEN 1 ELSE 0 END) as email_sent,
                    MAX(CASE WHEN event_type = 'email_opened' THEN 1 ELSE 0 END) as email_opened,
                    MAX(CASE WHEN event_type = 'email_clicked' THEN 1 ELSE 0 END) as email_clicked,
                    MAX(CASE WHEN event_type = 'conversion' THEN 1 ELSE 0 END) as converted
                FROM analytics_events
                WHERE timestamp >= NOW() - INTERVAL %s
                AND event_type IN ('email_sent', 'email_opened', 'email_clicked', 'conversion')
                GROUP BY user_id
            )
            SELECT 
                'Email Sent' as stage,
                SUM(email_sent) as count,
                100.0 as percentage
            FROM email_funnel
            UNION ALL
            SELECT 
                'Email Opened' as stage,
                SUM(email_opened) as count,
                (SUM(email_opened)::float / SUM(email_sent) * 100) as percentage
            FROM email_funnel
            UNION ALL
            SELECT 
                'Email Clicked' as stage,
                SUM(email_clicked) as count,
                (SUM(email_clicked)::float / SUM(email_sent) * 100) as percentage
            FROM email_funnel
            UNION ALL
            SELECT 
                'Converted' as stage,
                SUM(converted) as count,
                (SUM(converted)::float / SUM(email_sent) * 100) as percentage
            FROM email_funnel
            ORDER BY 
                CASE stage
                    WHEN 'Email Sent' THEN 1
                    WHEN 'Email Opened' THEN 2
                    WHEN 'Email Clicked' THEN 3
                    WHEN 'Converted' THEN 4
                END
        """
        
        cursor = self.postgres_client.cursor()
        cursor.execute(query, (time_range,))
        results = cursor.fetchall()
        cursor.close()
        
        return {
            'funnel_stages': [row[0] for row in results],
            'stage_counts': [row[1] for row in results],
            'stage_percentages': [round(row[2], 2) for row in results]
        }
    
    async def user_segmentation_analysis(self, segmentation_type: str):
        """Perform user segmentation analysis"""
        
        if segmentation_type == 'behavioral':
            return await self.behavioral_segmentation()
        elif segmentation_type == 'demographic':
            return await self.demographic_segmentation()
        elif segmentation_type == 'engagement':
            return await self.engagement_segmentation()
    
    async def behavioral_segmentation(self):
        """Segment users based on behavior"""
        
        query = """
            WITH user_behavior AS (
                SELECT 
                    user_id,
                    COUNT(CASE WHEN event_type = 'email_opened' THEN 1 END) as email_opens,
                    COUNT(CASE WHEN event_type = 'email_clicked' THEN 1 END) as email_clicks,
                    COUNT(CASE WHEN event_type = 'referral_made' THEN 1 END) as referrals,
                    COUNT(CASE WHEN event_type = 'conversion' THEN 1 END) as conversions,
                    MAX(timestamp) as last_activity
                FROM analytics_events
                WHERE timestamp >= NOW() - INTERVAL '30 days'
                GROUP BY user_id
            )
            SELECT 
                CASE 
                    WHEN email_opens >= 10 AND email_clicks >= 3 AND referrals >= 2 THEN 'Power Users'
                    WHEN email_opens >= 5 AND email_clicks >= 1 THEN 'Active Users'
                    WHEN email_opens >= 1 THEN 'Engaged Users'
                    ELSE 'Inactive Users'
                END as segment,
                COUNT(*) as user_count,
                AVG(conversions) as avg_conversions,
                AVG(referrals) as avg_referrals
            FROM user_behavior
            GROUP BY 
                CASE 
                    WHEN email_opens >= 10 AND email_clicks >= 3 AND referrals >= 2 THEN 'Power Users'
                    WHEN email_opens >= 5 AND email_clicks >= 1 THEN 'Active Users'
                    WHEN email_opens >= 1 THEN 'Engaged Users'
                    ELSE 'Inactive Users'
                END
            ORDER BY user_count DESC
        """
        
        cursor = self.postgres_client.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        
        return {
            'segments': [row[0] for row in results],
            'user_counts': [row[1] for row in results],
            'avg_conversions': [round(row[2], 2) for row in results],
            'avg_referrals': [round(row[3], 2) for row in results]
        }
```

### Real-Time Alerting System

```python
# Real-Time Alerting System
class RealTimeAlertingSystem:
    def __init__(self):
        self.redis_client = Redis(host='redis', port=6379, db=3)
        self.notification_service = NotificationService()
        self.alert_rules = self.load_alert_rules()
    
    def load_alert_rules(self):
        """Load alert rules configuration"""
        return {
            'low_engagement_rate': {
                'threshold': 0.15,  # 15%
                'time_window': '1h',
                'severity': 'warning',
                'message': 'Email engagement rate below 15%'
            },
            'high_bounce_rate': {
                'threshold': 0.05,  # 5%
                'time_window': '1h',
                'severity': 'critical',
                'message': 'Email bounce rate above 5%'
            },
            'low_conversion_rate': {
                'threshold': 0.02,  # 2%
                'time_window': '24h',
                'severity': 'warning',
                'message': 'Conversion rate below 2%'
            },
            'high_error_rate': {
                'threshold': 0.01,  # 1%
                'time_window': '5m',
                'severity': 'critical',
                'message': 'System error rate above 1%'
            }
        }
    
    async def check_alerts(self):
        """Check all alert rules continuously"""
        while True:
            try:
                for rule_name, rule_config in self.alert_rules.items():
                    await self.check_alert_rule(rule_name, rule_config)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logging.error(f"Error checking alerts: {e}")
                await asyncio.sleep(60)
    
    async def check_alert_rule(self, rule_name: str, rule_config: dict):
        """Check individual alert rule"""
        
        current_value = await self.get_metric_value(rule_name, rule_config['time_window'])
        threshold = rule_config['threshold']
        
        if self.should_trigger_alert(rule_name, current_value, threshold):
            await self.trigger_alert(rule_name, rule_config, current_value)
    
    async def get_metric_value(self, rule_name: str, time_window: str) -> float:
        """Get current metric value for alert rule"""
        
        if rule_name == 'low_engagement_rate':
            return await self.calculate_engagement_rate(time_window)
        elif rule_name == 'high_bounce_rate':
            return await self.calculate_bounce_rate(time_window)
        elif rule_name == 'low_conversion_rate':
            return await self.calculate_conversion_rate(time_window)
        elif rule_name == 'high_error_rate':
            return await self.calculate_error_rate(time_window)
        
        return 0.0
    
    async def calculate_engagement_rate(self, time_window: str) -> float:
        """Calculate email engagement rate"""
        current_time = datetime.now()
        since = current_time - timedelta(**self.parse_time_window(time_window))
        
        opens = await self.get_event_count('email_opened', since)
        sends = await self.get_event_count('email_sent', since)
        
        return opens / max(sends, 1)
    
    async def calculate_bounce_rate(self, time_window: str) -> float:
        """Calculate email bounce rate"""
        current_time = datetime.now()
        since = current_time - timedelta(**self.parse_time_window(time_window))
        
        bounces = await self.get_event_count('email_bounced', since)
        sends = await self.get_event_count('email_sent', since)
        
        return bounces / max(sends, 1)
    
    async def calculate_conversion_rate(self, time_window: str) -> float:
        """Calculate conversion rate"""
        current_time = datetime.now()
        since = current_time - timedelta(**self.parse_time_window(time_window))
        
        conversions = await self.get_event_count('conversion', since)
        total_users = await self.get_active_user_count(since)
        
        return conversions / max(total_users, 1)
    
    async def calculate_error_rate(self, time_window: str) -> float:
        """Calculate system error rate"""
        current_time = datetime.now()
        since = current_time - timedelta(**self.parse_time_window(time_window))
        
        errors = await self.get_event_count('error', since)
        total_requests = await self.get_event_count('api_request', since)
        
        return errors / max(total_requests, 1)
    
    def should_trigger_alert(self, rule_name: str, current_value: float, threshold: float) -> bool:
        """Determine if alert should be triggered"""
        
        if rule_name in ['low_engagement_rate', 'low_conversion_rate']:
            return current_value < threshold
        elif rule_name in ['high_bounce_rate', 'high_error_rate']:
            return current_value > threshold
        
        return False
    
    async def trigger_alert(self, rule_name: str, rule_config: dict, current_value: float):
        """Trigger alert notification"""
        
        alert = {
            'rule_name': rule_name,
            'severity': rule_config['severity'],
            'message': rule_config['message'],
            'current_value': current_value,
            'threshold': rule_config['threshold'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Store alert in Redis
        alert_key = f"alert:{rule_name}:{datetime.now().strftime('%Y%m%d%H%M')}"
        self.redis_client.setex(alert_key, 3600, json.dumps(alert))
        
        # Send notification
        await self.notification_service.send_alert(alert)
        
        logging.warning(f"Alert triggered: {rule_name} - {rule_config['message']}")
```

## 🚀 Real-Time Analytics Deployment

### Kubernetes Real-Time Analytics Deployment

```yaml
# Real-Time Analytics Kubernetes Deployment
apiVersion: v1
kind: ConfigMap
metadata:
  name: analytics-config
  namespace: ia-bulk-analytics
data:
  analytics_config.yaml: |
    kafka:
      bootstrap_servers: ["kafka:9092"]
      topics:
        - analytics-events
        - user-actions
        - email-events
        - conversion-events
    
    redis:
      host: redis
      port: 6379
      databases:
        events: 0
        metrics: 1
        cache: 2
        alerts: 3
    
    elasticsearch:
      hosts: ["elasticsearch:9200"]
      index_prefix: "analytics-events"
      index_pattern: "analytics-events-*"
    
    postgresql:
      host: postgres
      database: ia_bulk_analytics
      user: analytics_user
      password: analytics_password
    
    metrics:
      calculation_interval: 60  # seconds
      retention_period: 30      # days
      aggregation_levels:
        - realtime
        - minute
        - hour
        - day
    
    alerts:
      check_interval: 60        # seconds
      notification_channels:
        - email
        - slack
        - webhook
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: analytics-engine
  namespace: ia-bulk-analytics
spec:
  replicas: 3
  selector:
    matchLabels:
      app: analytics-engine
  template:
    metadata:
      labels:
        app: analytics-engine
    spec:
      containers:
      - name: analytics-engine
        image: ia-bulk/analytics-engine:latest
        ports:
        - containerPort: 8080
        env:
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "kafka:9092"
        - name: REDIS_HOST
          value: "redis"
        - name: ELASTICSEARCH_HOSTS
          value: "elasticsearch:9200"
        - name: POSTGRES_HOST
          value: "postgres"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: config
          mountPath: /app/config
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config
        configMap:
          name: analytics-config
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: analytics-dashboard
  namespace: ia-bulk-analytics
spec:
  replicas: 2
  selector:
    matchLabels:
      app: analytics-dashboard
  template:
    metadata:
      labels:
        app: analytics-dashboard
    spec:
      containers:
      - name: dashboard
        image: ia-bulk/analytics-dashboard:latest
        ports:
        - containerPort: 8501
        env:
        - name: REDIS_HOST
          value: "redis"
        - name: ELASTICSEARCH_HOSTS
          value: "elasticsearch:9200"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: analytics-dashboard-service
  namespace: ia-bulk-analytics
spec:
  selector:
    app: analytics-dashboard
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8501
  type: LoadBalancer
```

---

**📊 This Real-Time Analytics Engine provides comprehensive business intelligence and real-time insights for the IA Bulk Platform. For implementation support, refer to our [Complete Implementation Guide](./complete-implementation-guide.md) or [Enroll in the AI Marketing Mastery Course](../AI_Marketing_Course_Curriculum.md).**

*Master real-time analytics to create data-driven marketing systems that provide instant insights and enable rapid decision-making for maximum business impact.*
