# 🚀 TrendScope Pro - Complete Implementation Guide

## Overview
This comprehensive guide provides step-by-step instructions for implementing the TrendScope Pro AI marketing platform, including technical architecture, deployment strategies, and operational procedures.

## 🏗️ System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                       │
│  React.js + TypeScript + Next.js + Material-UI         │
├─────────────────────────────────────────────────────────┤
│                    API Gateway                          │
│  Express.js + GraphQL + REST + Authentication          │
├─────────────────────────────────────────────────────────┤
│                    Business Logic                       │
│  Trend Analysis + Consumer Insights + Predictions      │
├─────────────────────────────────────────────────────────┤
│                    AI/ML Services                       │
│  Python + TensorFlow + PyTorch + scikit-learn          │
├─────────────────────────────────────────────────────────┤
│                    Data Layer                           │
│  PostgreSQL + Redis + TimescaleDB + Message Queue      │
├─────────────────────────────────────────────────────────┤
│                    External APIs                        │
│  Social Media + News + Search + Analytics APIs         │
└─────────────────────────────────────────────────────────┘
```

## 🛠️ Technical Implementation

### 1. Frontend Development

#### Project Setup
```bash
# Create Next.js project
npx create-next-app@latest trendscope-frontend --typescript --tailwind --eslint

# Install additional dependencies
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material @mui/x-data-grid
npm install recharts d3 plotly.js
npm install @reduxjs/toolkit react-redux
npm install socket.io-client
npm install axios react-query
```

#### Core Components Structure
```
src/
├── components/
│   ├── Dashboard/
│   │   ├── TrendOverview.tsx
│   │   ├── ConsumerInsights.tsx
│   │   ├── PredictiveAnalytics.tsx
│   │   └── IndustryDashboard.tsx
│   ├── Trends/
│   │   ├── TrendList.tsx
│   │   ├── TrendDetail.tsx
│   │   ├── TrendComparison.tsx
│   │   └── TrendAlerts.tsx
│   ├── Analytics/
│   │   ├── Charts/
│   │   │   ├── LineChart.tsx
│   │   │   ├── BarChart.tsx
│   │   │   └── HeatmapChart.tsx
│   │   ├── Reports/
│   │   │   ├── ReportGenerator.tsx
│   │   │   └── ReportViewer.tsx
│   │   └── Exports/
│   │       ├── DataExporter.tsx
│   │       └── ScheduledExports.tsx
│   └── Settings/
│       ├── UserProfile.tsx
│       ├── Notifications.tsx
│       └── Integrations.tsx
├── services/
│   ├── api.ts
│   ├── auth.ts
│   ├── websocket.ts
│   └── analytics.ts
├── hooks/
│   ├── useTrends.ts
│   ├── useConsumerInsights.ts
│   └── usePredictions.ts
├── store/
│   ├── index.ts
│   ├── trendsSlice.ts
│   ├── userSlice.ts
│   └── analyticsSlice.ts
└── utils/
    ├── helpers.ts
    ├── constants.ts
    └── validators.ts
```

#### Key Component Implementation
```typescript
// components/Dashboard/TrendOverview.tsx
import React, { useEffect, useState } from 'react';
import { Card, CardContent, Typography, Grid, Box } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useTrends } from '../../hooks/useTrends';

interface TrendOverviewProps {
  industry?: string;
  timeframe?: string;
}

const TrendOverview: React.FC<TrendOverviewProps> = ({ industry, timeframe }) => {
  const { trends, loading, error } = useTrends({ industry, timeframe });
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    if (trends) {
      const formattedData = trends.map(trend => ({
        date: trend.date,
        score: trend.score,
        volume: trend.volume,
        sentiment: trend.sentiment
      }));
      setChartData(formattedData);
    }
  }, [trends]);

  if (loading) return <div>Loading trends...</div>;
  if (error) return <div>Error loading trends: {error}</div>;

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Trend Performance Over Time
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="score" stroke="#8884d8" strokeWidth={2} />
                <Line type="monotone" dataKey="volume" stroke="#82ca9d" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Top Trending Topics
            </Typography>
            {trends?.slice(0, 5).map((trend, index) => (
              <Box key={trend.id} sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  #{index + 1} {trend.title}
                </Typography>
                <Typography variant="caption" color="primary">
                  Score: {trend.score.toFixed(2)}
                </Typography>
              </Box>
            ))}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default TrendOverview;
```

### 2. Backend Development

#### Project Setup
```bash
# Create Node.js project
mkdir trendscope-backend
cd trendscope-backend
npm init -y

# Install dependencies
npm install express cors helmet morgan
npm install @apollo/server graphql
npm install jsonwebtoken bcryptjs
npm install pg redis
npm install dotenv
npm install joi express-rate-limit
npm install socket.io
npm install axios node-cron
```

#### Core Backend Structure
```
src/
├── controllers/
│   ├── trendController.js
│   ├── userController.js
│   ├── analyticsController.js
│   └── alertController.js
├── services/
│   ├── trendAnalysisService.js
│   ├── consumerInsightsService.js
│   ├── predictionService.js
│   └── notificationService.js
├── models/
│   ├── User.js
│   ├── Trend.js
│   ├── Alert.js
│   └── Report.js
├── middleware/
│   ├── auth.js
│   ├── validation.js
│   └── rateLimiting.js
├── routes/
│   ├── auth.js
│   ├── trends.js
│   ├── analytics.js
│   └── alerts.js
├── utils/
│   ├── database.js
│   ├── redis.js
│   └── helpers.js
└── config/
    ├── database.js
    ├── redis.js
    └── environment.js
```

#### Key Service Implementation
```javascript
// services/trendAnalysisService.js
const axios = require('axios');
const { Trend } = require('../models/Trend');
const { redis } = require('../utils/redis');

class TrendAnalysisService {
  constructor() {
    this.dataSources = {
      twitter: process.env.TWITTER_API_URL,
      reddit: process.env.REDDIT_API_URL,
      news: process.env.NEWS_API_URL,
      googleTrends: process.env.GOOGLE_TRENDS_API_URL
    };
  }

  async collectTrendData(sources = Object.keys(this.dataSources)) {
    const dataPromises = sources.map(source => this.fetchFromSource(source));
    const results = await Promise.allSettled(dataPromises);
    
    return results
      .filter(result => result.status === 'fulfilled')
      .map(result => result.value)
      .flat();
  }

  async fetchFromSource(source) {
    try {
      const response = await axios.get(this.dataSources[source], {
        timeout: 10000,
        headers: {
          'Authorization': `Bearer ${process.env[`${source.toUpperCase()}_API_KEY`]}`,
          'Content-Type': 'application/json'
        }
      });
      
      return this.processSourceData(source, response.data);
    } catch (error) {
      console.error(`Error fetching from ${source}:`, error.message);
      return [];
    }
  }

  processSourceData(source, data) {
    switch (source) {
      case 'twitter':
        return this.processTwitterData(data);
      case 'reddit':
        return this.processRedditData(data);
      case 'news':
        return this.processNewsData(data);
      case 'googleTrends':
        return this.processGoogleTrendsData(data);
      default:
        return [];
    }
  }

  async analyzeTrends(rawData) {
    // Cache check
    const cacheKey = `trends:${Date.now()}`;
    const cached = await redis.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }

    // Process and analyze data
    const processedData = await this.processTrendData(rawData);
    const trends = await this.identifyTrends(processedData);
    const enrichedTrends = await this.enrichTrends(trends);

    // Cache results for 5 minutes
    await redis.setex(cacheKey, 300, JSON.stringify(enrichedTrends));

    return enrichedTrends;
  }

  async identifyTrends(data) {
    // Group data by keywords and topics
    const groupedData = this.groupDataByTopics(data);
    
    // Calculate trend scores
    const trends = Object.entries(groupedData).map(([topic, data]) => ({
      topic,
      score: this.calculateTrendScore(data),
      volume: data.length,
      sentiment: this.calculateSentiment(data),
      sources: [...new Set(data.map(item => item.source))],
      timestamp: new Date()
    }));

    // Sort by score and return top trends
    return trends
      .sort((a, b) => b.score - a.score)
      .slice(0, 100);
  }

  calculateTrendScore(data) {
    const volume = data.length;
    const recency = this.calculateRecency(data);
    const engagement = this.calculateEngagement(data);
    const sentiment = this.calculateSentiment(data);
    
    // Weighted score calculation
    return (volume * 0.3) + (recency * 0.3) + (engagement * 0.2) + (sentiment * 0.2);
  }

  async saveTrends(trends) {
    try {
      await Trend.bulkCreate(trends, {
        updateOnDuplicate: ['score', 'volume', 'sentiment', 'updatedAt']
      });
    } catch (error) {
      console.error('Error saving trends:', error);
      throw error;
    }
  }
}

module.exports = new TrendAnalysisService();
```

### 3. AI/ML Services

#### Python ML Service Setup
```bash
# Create Python virtual environment
python -m venv trendscope-ml
source trendscope-ml/bin/activate  # On Windows: trendscope-ml\Scripts\activate

# Install dependencies
pip install fastapi uvicorn
pip install pandas numpy scikit-learn
pip install tensorflow torch
pip install transformers spacy nltk
pip install redis psycopg2-binary
pip install requests aiohttp
```

#### ML Service Structure
```
ml_services/
├── app/
│   ├── main.py
│   ├── models/
│   │   ├── trend_detector.py
│   │   ├── sentiment_analyzer.py
│   │   ├── consumer_insights.py
│   │   └── prediction_engine.py
│   ├── services/
│   │   ├── data_processor.py
│   │   ├── model_trainer.py
│   │   └── inference_service.py
│   ├── utils/
│   │   ├── helpers.py
│   │   └── config.py
│   └── api/
│       ├── routes.py
│       └── schemas.py
├── models/
│   ├── trend_model.pkl
│   ├── sentiment_model.pkl
│   └── consumer_model.pkl
└── data/
    ├── training/
    ├── validation/
    └── test/
```

#### Key ML Model Implementation
```python
# app/models/trend_detector.py
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from transformers import pipeline
import joblib
from typing import List, Dict, Any

class TrendDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.clusterer = KMeans(n_clusters=20, random_state=42)
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest"
        )
        
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text data"""
        import re
        
        # Remove URLs, mentions, hashtags
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'@\w+|#\w+', '', text)
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = text.lower().strip()
        
        return text
    
    def extract_features(self, texts: List[str]) -> np.ndarray:
        """Extract features from text data"""
        processed_texts = [self.preprocess_text(text) for text in texts]
        tfidf_matrix = self.vectorizer.fit_transform(processed_texts)
        return tfidf_matrix.toarray()
    
    def detect_trends(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Main method to detect trending topics"""
        # Extract text data
        texts = [item.get('text', '') for item in data]
        
        # Extract features
        features = self.extract_features(texts)
        
        # Cluster similar topics
        clusters = self.clusterer.fit_predict(features)
        
        # Analyze each cluster
        trends = []
        for cluster_id in np.unique(clusters):
            cluster_data = [data[i] for i, c in enumerate(clusters) if c == cluster_id]
            
            if len(cluster_data) < 5:  # Skip small clusters
                continue
                
            trend = self.analyze_cluster(cluster_id, cluster_data)
            trends.append(trend)
        
        # Sort by trend score
        trends.sort(key=lambda x: x['score'], reverse=True)
        
        return trends[:50]  # Return top 50 trends
    
    def analyze_cluster(self, cluster_id: int, cluster_data: List[Dict]) -> Dict[str, Any]:
        """Analyze a cluster to determine if it's a trend"""
        # Calculate trend metrics
        volume = len(cluster_data)
        recency = self.calculate_recency(cluster_data)
        engagement = self.calculate_engagement(cluster_data)
        sentiment = self.calculate_sentiment(cluster_data)
        
        # Calculate trend score
        score = (volume * 0.3) + (recency * 0.3) + (engagement * 0.2) + (sentiment * 0.2)
        
        # Extract keywords
        keywords = self.extract_keywords(cluster_data)
        
        return {
            'cluster_id': cluster_id,
            'score': score,
            'volume': volume,
            'recency': recency,
            'engagement': engagement,
            'sentiment': sentiment,
            'keywords': keywords,
            'sources': list(set([item.get('source', 'unknown') for item in cluster_data])),
            'timestamp': pd.Timestamp.now()
        }
    
    def calculate_recency(self, data: List[Dict]) -> float:
        """Calculate recency score based on timestamps"""
        if not data:
            return 0.0
            
        timestamps = [item.get('timestamp', pd.Timestamp.now()) for item in data]
        if isinstance(timestamps[0], str):
            timestamps = [pd.to_datetime(ts) for ts in timestamps]
            
        now = pd.Timestamp.now()
        time_diffs = [(now - ts).total_seconds() / 3600 for ts in timestamps]  # Hours
        
        # Recent data gets higher score
        avg_hours_ago = np.mean(time_diffs)
        recency_score = max(0, 1 - (avg_hours_ago / 168))  # Decay over 1 week
        
        return recency_score
    
    def calculate_engagement(self, data: List[Dict]) -> float:
        """Calculate engagement score"""
        if not data:
            return 0.0
            
        engagement_metrics = []
        for item in data:
            likes = item.get('likes', 0)
            shares = item.get('shares', 0)
            comments = item.get('comments', 0)
            
            # Weighted engagement score
            engagement = (likes * 1) + (shares * 3) + (comments * 2)
            engagement_metrics.append(engagement)
        
        # Normalize engagement score
        max_engagement = max(engagement_metrics) if engagement_metrics else 1
        normalized_engagement = np.mean([e / max_engagement for e in engagement_metrics])
        
        return normalized_engagement
    
    def calculate_sentiment(self, data: List[Dict]) -> float:
        """Calculate sentiment score"""
        if not data:
            return 0.0
            
        texts = [item.get('text', '') for item in data if item.get('text')]
        if not texts:
            return 0.0
            
        # Analyze sentiment
        sentiments = self.sentiment_analyzer(texts)
        
        # Convert to numeric scores
        sentiment_scores = []
        for sentiment in sentiments:
            if sentiment['label'] == 'LABEL_0':  # Negative
                score = -sentiment['score']
            elif sentiment['label'] == 'LABEL_1':  # Neutral
                score = 0
            else:  # Positive
                score = sentiment['score']
            sentiment_scores.append(score)
        
        return np.mean(sentiment_scores)
    
    def extract_keywords(self, data: List[Dict]) -> List[str]:
        """Extract top keywords from cluster data"""
        texts = [item.get('text', '') for item in data if item.get('text')]
        if not texts:
            return []
            
        # Use TF-IDF to find important keywords
        processed_texts = [self.preprocess_text(text) for text in texts]
        tfidf_matrix = self.vectorizer.fit_transform(processed_texts)
        
        # Get top keywords
        feature_names = self.vectorizer.get_feature_names_out()
        mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
        
        # Sort by importance
        keyword_scores = list(zip(feature_names, mean_scores))
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [keyword for keyword, score in keyword_scores[:10] if score > 0]
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        model_data = {
            'vectorizer': self.vectorizer,
            'clusterer': self.clusterer,
            'classifier': self.classifier
        }
        joblib.dump(model_data, filepath)
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        model_data = joblib.load(filepath)
        self.vectorizer = model_data['vectorizer']
        self.clusterer = model_data['clusterer']
        self.classifier = model_data['classifier']
```

### 4. Database Setup

#### PostgreSQL Schema
```sql
-- Create database
CREATE DATABASE trendscope_pro;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company_name VARCHAR(255),
    industry VARCHAR(100),
    subscription_tier VARCHAR(50) DEFAULT 'starter',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Trends table
CREATE TABLE trends (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    industry VARCHAR(100),
    keywords TEXT[],
    sentiment_score DECIMAL(3,2),
    engagement_score DECIMAL(5,2),
    authenticity_score DECIMAL(3,2),
    momentum_score DECIMAL(3,2),
    longevity_prediction INTEGER,
    source_urls JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_trends_category ON trends(category);
CREATE INDEX idx_trends_industry ON trends(industry);
CREATE INDEX idx_trends_created_at ON trends(created_at);
CREATE INDEX idx_trends_sentiment ON trends(sentiment_score);
CREATE INDEX idx_trends_keywords ON trends USING GIN(keywords);

-- Consumer insights table
CREATE TABLE consumer_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trend_id UUID REFERENCES trends(id) ON DELETE CASCADE,
    demographic_data JSONB,
    psychographic_data JSONB,
    behavioral_data JSONB,
    preference_data JSONB,
    segment_id UUID,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,
    criteria JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered TIMESTAMP,
    trigger_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Reports table
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    data JSONB,
    generated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- API usage tracking
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    endpoint VARCHAR(255),
    method VARCHAR(10),
    response_time INTEGER,
    status_code INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for API usage
CREATE INDEX idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX idx_api_usage_created_at ON api_usage(created_at);
```

### 5. Deployment Configuration

#### Docker Configuration
```dockerfile
# Dockerfile for backend
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

```dockerfile
# Dockerfile for ML service
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: trendscope_pro
      POSTGRES_USER: trendscope
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    environment:
      NODE_ENV: production
      DATABASE_URL: postgresql://trendscope:${DB_PASSWORD}@postgres:5432/trendscope_pro
      REDIS_URL: redis://redis:6379
    ports:
      - "3000:3000"
    depends_on:
      - postgres
      - redis

  ml-service:
    build: ./ml-services
    environment:
      DATABASE_URL: postgresql://trendscope:${DB_PASSWORD}@postgres:5432/trendscope_pro
      REDIS_URL: redis://redis:6379
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    ports:
      - "80:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

### 6. Monitoring and Analytics

#### Application Monitoring
```javascript
// utils/monitoring.js
const prometheus = require('prom-client');

// Create metrics
const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code']
});

const httpRequestTotal = new prometheus.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

const activeConnections = new prometheus.Gauge({
  name: 'active_connections',
  help: 'Number of active connections'
});

const trendAnalysisDuration = new prometheus.Histogram({
  name: 'trend_analysis_duration_seconds',
  help: 'Duration of trend analysis in seconds',
  labelNames: ['source', 'industry']
});

module.exports = {
  httpRequestDuration,
  httpRequestTotal,
  activeConnections,
  trendAnalysisDuration
};
```

### 7. Security Implementation

#### Authentication Middleware
```javascript
// middleware/auth.js
const jwt = require('jsonwebtoken');
const { promisify } = require('util');

const verifyToken = promisify(jwt.verify);

const authenticateToken = async (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  try {
    const decoded = await verifyToken(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(403).json({ error: 'Invalid or expired token' });
  }
};

const requireRole = (roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
};

module.exports = {
  authenticateToken,
  requireRole
};
```

### 8. Performance Optimization

#### Caching Strategy
```javascript
// utils/cache.js
const redis = require('redis');
const client = redis.createClient(process.env.REDIS_URL);

class CacheManager {
  constructor() {
    this.client = client;
    this.defaultTTL = 300; // 5 minutes
  }

  async get(key) {
    try {
      const value = await this.client.get(key);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      console.error('Cache get error:', error);
      return null;
    }
  }

  async set(key, value, ttl = this.defaultTTL) {
    try {
      await this.client.setex(key, ttl, JSON.stringify(value));
    } catch (error) {
      console.error('Cache set error:', error);
    }
  }

  async del(key) {
    try {
      await this.client.del(key);
    } catch (error) {
      console.error('Cache delete error:', error);
    }
  }

  async invalidatePattern(pattern) {
    try {
      const keys = await this.client.keys(pattern);
      if (keys.length > 0) {
        await this.client.del(...keys);
      }
    } catch (error) {
      console.error('Cache pattern invalidation error:', error);
    }
  }
}

module.exports = new CacheManager();
```

This comprehensive implementation guide provides all the necessary components to build and deploy the TrendScope Pro AI marketing platform. The guide covers frontend development, backend services, AI/ML implementation, database setup, deployment configuration, monitoring, security, and performance optimization.



