# 💻 Neural Marketing Consciousness System - Developer Resources

## 📋 Overview

This document provides comprehensive developer resources, SDKs, code examples, and integration guides for the Neural Marketing Consciousness System. Use these resources to build applications, integrations, and custom solutions.

## 🚀 Quick Start

### Installation

#### Python SDK
```bash
pip install neural-marketing-consciousness
```

#### JavaScript SDK
```bash
npm install neural-marketing-consciousness
```

#### PHP SDK
```bash
composer require neural-marketing-consciousness/php-sdk
```

#### Ruby SDK
```bash
gem install neural-marketing-consciousness
```

### Basic Usage

#### Python Example
```python
from neural_marketing_consciousness import ConsciousnessClient

# Initialize client
client = ConsciousnessClient(api_key="your_api_key")

# Start consciousness assessment
assessment = client.assessment.start(user_id="user123")

# Submit assessment responses
result = client.assessment.submit(
    session_id=assessment.session_id,
    responses=[
        {"question_id": "q1", "answer": "option_a", "confidence": 8},
        {"question_id": "q2", "answer": "option_b", "confidence": 7}
    ]
)

print(f"Consciousness Level: {result.consciousness_level}")
print(f"Archetype: {result.archetype}")
```

#### JavaScript Example
```javascript
import { ConsciousnessClient } from 'neural-marketing-consciousness';

// Initialize client
const client = new ConsciousnessClient('your_api_key');

// Start consciousness assessment
const assessment = await client.assessment.start('user123');

// Submit assessment responses
const result = await client.assessment.submit(assessment.session_id, [
    { question_id: 'q1', answer: 'option_a', confidence: 8 },
    { question_id: 'q2', answer: 'option_b', confidence: 7 }
]);

console.log(`Consciousness Level: ${result.consciousness_level}`);
console.log(`Archetype: ${result.archetype}`);
```

## 🔧 SDK Documentation

### Python SDK

#### Installation
```bash
pip install neural-marketing-consciousness
```

#### Authentication
```python
from neural_marketing_consciousness import ConsciousnessClient

# Initialize with API key
client = ConsciousnessClient(api_key="your_api_key")

# Or use environment variable
import os
client = ConsciousnessClient(api_key=os.getenv("NMC_API_KEY"))
```

#### Consciousness Assessment
```python
# Start assessment
assessment = client.assessment.start(
    user_id="user123",
    assessment_type="full",
    language="en"
)

# Get questions
questions = assessment.questions
for question in questions:
    print(f"Question: {question['question']}")
    print(f"Options: {question['options']}")

# Submit responses
responses = [
    {"question_id": "q1", "answer": "option_a", "confidence": 8},
    {"question_id": "q2", "answer": "option_b", "confidence": 7}
]

result = client.assessment.submit(
    session_id=assessment.session_id,
    responses=responses
)

print(f"Consciousness Level: {result.consciousness_level}")
print(f"Archetype: {result.archetype}")
print(f"Recommendations: {result.recommendations}")
```

#### Learning Management
```python
# Get learning path
learning_path = client.learning.get_path(user_id="user123")
print(f"Current Tier: {learning_path.current_tier}")
print(f"Modules: {len(learning_path.modules)}")

# Update progress
progress = client.learning.update_progress(
    user_id="user123",
    module_id="module_123",
    progress_percentage=75,
    time_spent=90
)

print(f"Updated Progress: {progress.progress_percentage}%")
```

#### Tool Integration
```python
# Get available tools
tools = client.tools.list(category="content_creation")
for tool in tools:
    print(f"Tool: {tool.name}")
    print(f"Required Level: {tool.consciousness_level_required}")

# Execute tool
result = client.tools.execute(
    user_id="user123",
    tool_id="gpt4-integration",
    parameters={
        "prompt": "Write a marketing email for our new product",
        "tone": "professional",
        "length": "medium"
    }
)

print(f"Generated Content: {result.result['content']}")
print(f"Consciousness Impact: {result.consciousness_impact}")
```

#### Community Features
```python
# Get community posts
posts = client.community.get_posts(limit=10)
for post in posts:
    print(f"Title: {post.title}")
    print(f"Author: {post.username}")
    print(f"Likes: {post.likes}")

# Create post
new_post = client.community.create_post(
    user_id="user123",
    title="Best practices for AI content creation",
    content="I've been using GPT-4 for content creation...",
    category="content_creation",
    tags=["gpt4", "content", "best_practices"]
)

print(f"Post Created: {new_post.post_id}")
```

### JavaScript SDK

#### Installation
```bash
npm install neural-marketing-consciousness
```

#### Authentication
```javascript
import { ConsciousnessClient } from 'neural-marketing-consciousness';

// Initialize with API key
const client = new ConsciousnessClient('your_api_key');

// Or use environment variable
const client = new ConsciousnessClient(process.env.NMC_API_KEY);
```

#### Consciousness Assessment
```javascript
// Start assessment
const assessment = await client.assessment.start('user123', {
    assessment_type: 'full',
    language: 'en'
});

// Get questions
const questions = assessment.questions;
questions.forEach(question => {
    console.log(`Question: ${question.question}`);
    console.log(`Options: ${question.options}`);
});

// Submit responses
const responses = [
    { question_id: 'q1', answer: 'option_a', confidence: 8 },
    { question_id: 'q2', answer: 'option_b', confidence: 7 }
];

const result = await client.assessment.submit(assessment.session_id, responses);

console.log(`Consciousness Level: ${result.consciousness_level}`);
console.log(`Archetype: ${result.archetype}`);
```

#### Learning Management
```javascript
// Get learning path
const learningPath = await client.learning.getPath('user123');
console.log(`Current Tier: ${learningPath.current_tier}`);
console.log(`Modules: ${learningPath.modules.length}`);

// Update progress
const progress = await client.learning.updateProgress('user123', {
    module_id: 'module_123',
    progress_percentage: 75,
    time_spent: 90
});

console.log(`Updated Progress: ${progress.progress_percentage}%`);
```

#### Tool Integration
```javascript
// Get available tools
const tools = await client.tools.list({ category: 'content_creation' });
tools.forEach(tool => {
    console.log(`Tool: ${tool.name}`);
    console.log(`Required Level: ${tool.consciousness_level_required}`);
});

// Execute tool
const result = await client.tools.execute('user123', 'gpt4-integration', {
    prompt: 'Write a marketing email for our new product',
    tone: 'professional',
    length: 'medium'
});

console.log(`Generated Content: ${result.result.content}`);
console.log(`Consciousness Impact: ${result.consciousness_impact}`);
```

## 🔌 API Integration Examples

### Webhook Integration

#### Setting Up Webhooks
```python
# Configure webhook
webhook = client.webhooks.create(
    url="https://your-app.com/webhooks/consciousness",
    events=["assessment.completed", "consciousness.level_changed"],
    secret="your_webhook_secret"
)

print(f"Webhook ID: {webhook.id}")
```

#### Webhook Handler
```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

@app.route('/webhooks/consciousness', methods=['POST'])
def handle_webhook():
    # Verify webhook signature
    signature = request.headers.get('X-NMC-Signature')
    payload = request.get_data()
    
    expected_signature = hmac.new(
        b'your_webhook_secret',
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Process webhook event
    event = request.json
    event_type = event['event']
    
    if event_type == 'assessment.completed':
        user_id = event['data']['user_id']
        consciousness_level = event['data']['consciousness_level']
        
        # Update user's learning path
        update_learning_path(user_id, consciousness_level)
        
    elif event_type == 'consciousness.level_changed':
        user_id = event['data']['user_id']
        new_level = event['data']['consciousness_level']
        
        # Send notification to user
        send_notification(user_id, f"Your consciousness level is now {new_level}%")
    
    return jsonify({'status': 'success'})
```

### Database Integration

#### PostgreSQL Integration
```python
import psycopg2
from neural_marketing_consciousness import ConsciousnessClient

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="consciousness_db",
    user="username",
    password="password"
)

# Initialize client
client = ConsciousnessClient(api_key="your_api_key")

def sync_consciousness_data():
    """Sync consciousness data to local database"""
    cursor = conn.cursor()
    
    # Get users from local database
    cursor.execute("SELECT user_id FROM users WHERE sync_consciousness = true")
    users = cursor.fetchall()
    
    for user_id in users:
        # Get consciousness data from API
        dashboard = client.dashboard.get(user_id[0])
        
        # Update local database
        cursor.execute("""
            INSERT INTO consciousness_data (user_id, consciousness_level, archetype, updated_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                consciousness_level = EXCLUDED.consciousness_level,
                archetype = EXCLUDED.archetype,
                updated_at = EXCLUDED.updated_at
        """, (
            user_id[0],
            dashboard.consciousness.current_level,
            dashboard.consciousness.archetype,
            datetime.now()
        ))
    
    conn.commit()
    cursor.close()
```

#### MongoDB Integration
```python
from pymongo import MongoClient
from neural_marketing_consciousness import ConsciousnessClient

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client.consciousness_db

# Initialize API client
api_client = ConsciousnessClient(api_key="your_api_key")

def sync_learning_progress():
    """Sync learning progress to MongoDB"""
    collection = db.learning_progress
    
    # Get users with active learning
    users = db.users.find({"learning_active": True})
    
    for user in users:
        user_id = user["_id"]
        
        # Get learning analytics from API
        analytics = api_client.learning.get_analytics(user_id)
        
        # Update MongoDB document
        collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "total_learning_time": analytics.metrics.total_learning_time,
                    "modules_completed": analytics.metrics.modules_completed,
                    "consciousness_improvement": analytics.metrics.consciousness_improvement,
                    "updated_at": datetime.now()
                }
            },
            upsert=True
        )
```

## 🎨 Frontend Integration

### React Integration

#### Consciousness Dashboard Component
```jsx
import React, { useState, useEffect } from 'react';
import { ConsciousnessClient } from 'neural-marketing-consciousness';

const ConsciousnessDashboard = ({ userId }) => {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const client = new ConsciousnessClient(process.env.REACT_APP_NMC_API_KEY);
        const data = await client.dashboard.get(userId);
        setDashboard(data);
      } catch (error) {
        console.error('Error fetching dashboard:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboard();
  }, [userId]);
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div className="consciousness-dashboard">
      <div className="consciousness-level">
        <h2>Consciousness Level: {dashboard.consciousness.current_level}%</h2>
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${dashboard.consciousness.progress_percentage}%` }}
          />
        </div>
      </div>
      
      <div className="learning-progress">
        <h3>Learning Progress</h3>
        <p>Current Module: {dashboard.learning.current_module}</p>
        <p>Progress: {dashboard.learning.progress_percentage}%</p>
      </div>
      
      <div className="recent-tools">
        <h3>Recent Tool Usage</h3>
        {dashboard.tools.recent_activity.map((activity, index) => (
          <div key={index} className="tool-activity">
            <span>{activity.tool_id}</span>
            <span>{activity.action}</span>
            <span>{new Date(activity.timestamp).toLocaleDateString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ConsciousnessDashboard;
```

#### Assessment Component
```jsx
import React, { useState } from 'react';
import { ConsciousnessClient } from 'neural-marketing-consciousness';

const ConsciousnessAssessment = ({ userId, onComplete }) => {
  const [assessment, setAssessment] = useState(null);
  const [responses, setResponses] = useState({});
  const [currentQuestion, setCurrentQuestion] = useState(0);
  
  const startAssessment = async () => {
    try {
      const client = new ConsciousnessClient(process.env.REACT_APP_NMC_API_KEY);
      const assessment = await client.assessment.start(userId);
      setAssessment(assessment);
    } catch (error) {
      console.error('Error starting assessment:', error);
    }
  };
  
  const submitResponse = (questionId, answer, confidence) => {
    setResponses(prev => ({
      ...prev,
      [questionId]: { answer, confidence }
    }));
    
    if (currentQuestion < assessment.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      submitAssessment();
    }
  };
  
  const submitAssessment = async () => {
    try {
      const client = new ConsciousnessClient(process.env.REACT_APP_NMC_API_KEY);
      const result = await client.assessment.submit(assessment.session_id, responses);
      onComplete(result);
    } catch (error) {
      console.error('Error submitting assessment:', error);
    }
  };
  
  if (!assessment) {
    return (
      <div className="assessment-start">
        <h2>Consciousness Assessment</h2>
        <p>Discover your AI marketing consciousness level</p>
        <button onClick={startAssessment}>Start Assessment</button>
      </div>
    );
  }
  
  const question = assessment.questions[currentQuestion];
  
  return (
    <div className="assessment">
      <div className="progress">
        Question {currentQuestion + 1} of {assessment.questions.length}
      </div>
      
      <div className="question">
        <h3>{question.question}</h3>
        <div className="options">
          {question.options.map((option, index) => (
            <button
              key={index}
              onClick={() => submitResponse(question.id, option, 8)}
              className="option-button"
            >
              {option}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ConsciousnessAssessment;
```

### Vue.js Integration

#### Consciousness Dashboard Component
```vue
<template>
  <div class="consciousness-dashboard">
    <div v-if="loading" class="loading">Loading...</div>
    
    <div v-else class="dashboard-content">
      <div class="consciousness-level">
        <h2>Consciousness Level: {{ dashboard.consciousness.current_level }}%</h2>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${dashboard.consciousness.progress_percentage}%` }"
          />
        </div>
      </div>
      
      <div class="learning-progress">
        <h3>Learning Progress</h3>
        <p>Current Module: {{ dashboard.learning.current_module }}</p>
        <p>Progress: {{ dashboard.learning.progress_percentage }}%</p>
      </div>
      
      <div class="recent-tools">
        <h3>Recent Tool Usage</h3>
        <div 
          v-for="(activity, index) in dashboard.tools.recent_activity" 
          :key="index" 
          class="tool-activity"
        >
          <span>{{ activity.tool_id }}</span>
          <span>{{ activity.action }}</span>
          <span>{{ formatDate(activity.timestamp) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ConsciousnessClient } from 'neural-marketing-consciousness';

export default {
  name: 'ConsciousnessDashboard',
  props: {
    userId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      dashboard: null,
      loading: true
    };
  },
  async mounted() {
    await this.fetchDashboard();
  },
  methods: {
    async fetchDashboard() {
      try {
        const client = new ConsciousnessClient(process.env.VUE_APP_NMC_API_KEY);
        const data = await client.dashboard.get(this.userId);
        this.dashboard = data;
      } catch (error) {
        console.error('Error fetching dashboard:', error);
      } finally {
        this.loading = false;
      }
    },
    formatDate(timestamp) {
      return new Date(timestamp).toLocaleDateString();
    }
  }
};
</script>
```

## 🔧 Advanced Examples

### Custom Consciousness Analytics

#### Python Analytics Dashboard
```python
import pandas as pd
import matplotlib.pyplot as plt
from neural_marketing_consciousness import ConsciousnessClient

class ConsciousnessAnalytics:
    def __init__(self, api_key):
        self.client = ConsciousnessClient(api_key)
    
    def analyze_user_consciousness_trends(self, user_id, days=30):
        """Analyze consciousness development trends for a user"""
        analytics = self.client.analytics.get_consciousness_trends(
            user_id, 
            granularity="daily"
        )
        
        # Convert to DataFrame
        df = pd.DataFrame(analytics.trends)
        df['date'] = pd.to_datetime(df['date'])
        
        # Create visualization
        plt.figure(figsize=(12, 6))
        plt.plot(df['date'], df['consciousness_level'], marker='o')
        plt.title(f'Consciousness Development Trend - User {user_id}')
        plt.xlabel('Date')
        plt.ylabel('Consciousness Level (%)')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
        return df
    
    def compare_archetype_performance(self, archetype):
        """Compare performance metrics across archetypes"""
        # Get users with specific archetype
        users = self.get_users_by_archetype(archetype)
        
        metrics = []
        for user in users:
            dashboard = self.client.dashboard.get(user['user_id'])
            metrics.append({
                'user_id': user['user_id'],
                'consciousness_level': dashboard.consciousness.current_level,
                'learning_time': dashboard.learning.time_spent_today,
                'tool_usage': len(dashboard.tools.recent_activity)
            })
        
        df = pd.DataFrame(metrics)
        
        # Calculate statistics
        stats = df.describe()
        print(f"Performance Statistics for {archetype} Archetype:")
        print(stats)
        
        return df
```

### Machine Learning Integration

#### Consciousness Prediction Model
```python
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from neural_marketing_consciousness import ConsciousnessClient

class ConsciousnessPredictor:
    def __init__(self, api_key):
        self.client = ConsciousnessClient(api_key)
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    def train_model(self, user_data):
        """Train model to predict consciousness development"""
        # Prepare features
        X = []
        y = []
        
        for user in user_data:
            # Get user's learning analytics
            analytics = self.client.learning.get_analytics(user['user_id'])
            
            # Extract features
            features = [
                analytics.metrics.total_learning_time,
                analytics.metrics.modules_completed,
                analytics.metrics.average_session_duration,
                user.get('experience_years', 0),
                user.get('education_level', 0)
            ]
            
            X.append(features)
            y.append(user['consciousness_level'])
        
        # Train model
        self.model.fit(X, y)
        return self.model.score(X, y)
    
    def predict_consciousness(self, user_id):
        """Predict consciousness level for a user"""
        # Get user's current data
        analytics = self.client.learning.get_analytics(user_id)
        
        # Prepare features
        features = [
            analytics.metrics.total_learning_time,
            analytics.metrics.modules_completed,
            analytics.metrics.average_session_duration,
            0,  # experience_years (would need to be provided)
            0   # education_level (would need to be provided)
        ]
        
        # Make prediction
        prediction = self.model.predict([features])[0]
        return prediction
```

### Real-time Consciousness Monitoring

#### WebSocket Integration
```python
import asyncio
import websockets
import json
from neural_marketing_consciousness import ConsciousnessClient

class RealTimeConsciousnessMonitor:
    def __init__(self, api_key):
        self.client = ConsciousnessClient(api_key)
        self.connections = set()
    
    async def register_user(self, websocket, user_id):
        """Register user for real-time updates"""
        self.connections.add((websocket, user_id))
        
        # Start monitoring user's consciousness
        asyncio.create_task(self.monitor_user_consciousness(websocket, user_id))
    
    async def monitor_user_consciousness(self, websocket, user_id):
        """Monitor user's consciousness in real-time"""
        last_level = None
        
        while True:
            try:
                # Get current consciousness level
                dashboard = self.client.dashboard.get(user_id)
                current_level = dashboard.consciousness.current_level
                
                # Check for changes
                if last_level is None or current_level != last_level:
                    # Send update to user
                    update = {
                        'type': 'consciousness_update',
                        'user_id': user_id,
                        'consciousness_level': current_level,
                        'timestamp': dashboard.consciousness.updated_at
                    }
                    
                    await websocket.send(json.dumps(update))
                    last_level = current_level
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception as e:
                print(f"Error monitoring user {user_id}: {e}")
                break
    
    async def handle_websocket(self, websocket, path):
        """Handle WebSocket connections"""
        try:
            async for message in websocket:
                data = json.loads(message)
                
                if data['type'] == 'register':
                    user_id = data['user_id']
                    await self.register_user(websocket, user_id)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            # Clean up connection
            self.connections.discard((websocket, None))

# Start WebSocket server
async def main():
    monitor = RealTimeConsciousnessMonitor("your_api_key")
    
    server = await websockets.serve(
        monitor.handle_websocket, 
        "localhost", 
        8765
    )
    
    print("Real-time consciousness monitor started on ws://localhost:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
```

## 📚 Code Examples Repository

### GitHub Repository Structure
```
neural-marketing-consciousness-examples/
├── python/
│   ├── basic_integration.py
│   ├── advanced_analytics.py
│   ├── machine_learning/
│   └── real_time_monitoring.py
├── javascript/
│   ├── react/
│   ├── vue/
│   ├── node/
│   └── vanilla/
├── php/
│   ├── laravel/
│   ├── symfony/
│   └── vanilla/
├── ruby/
│   ├── rails/
│   └── sinatra/
├── mobile/
│   ├── react-native/
│   ├── flutter/
│   └── native/
└── docs/
    ├── api-reference.md
    ├── integration-guides.md
    └── best-practices.md
```

### Example Projects

#### 1. Consciousness Dashboard
A complete dashboard application showing consciousness development metrics.

**Features:**
- Real-time consciousness level display
- Learning progress tracking
- Tool usage analytics
- Community engagement metrics

#### 2. Assessment Platform
A custom assessment platform with advanced features.

**Features:**
- Custom question types
- Advanced scoring algorithms
- Real-time results
- Progress tracking

#### 3. Learning Management System
A comprehensive learning management system.

**Features:**
- Course management
- Progress tracking
- Certification system
- Community features

## 🛠️ Development Tools

### Testing

#### Unit Tests
```python
import unittest
from neural_marketing_consciousness import ConsciousnessClient

class TestConsciousnessClient(unittest.TestCase):
    def setUp(self):
        self.client = ConsciousnessClient("test_api_key")
    
    def test_assessment_start(self):
        """Test starting an assessment"""
        assessment = self.client.assessment.start("test_user")
        self.assertIsNotNone(assessment.session_id)
        self.assertIsNotNone(assessment.questions)
    
    def test_assessment_submit(self):
        """Test submitting assessment responses"""
        # Start assessment
        assessment = self.client.assessment.start("test_user")
        
        # Submit responses
        responses = [
            {"question_id": "q1", "answer": "option_a", "confidence": 8}
        ]
        
        result = self.client.assessment.submit(
            assessment.session_id, 
            responses
        )
        
        self.assertIsNotNone(result.consciousness_level)
        self.assertIsNotNone(result.archetype)

if __name__ == '__main__':
    unittest.main()
```

#### Integration Tests
```python
import pytest
from neural_marketing_consciousness import ConsciousnessClient

@pytest.fixture
def client():
    return ConsciousnessClient("test_api_key")

@pytest.fixture
def test_user():
    return "test_user_123"

def test_full_assessment_flow(client, test_user):
    """Test complete assessment flow"""
    # Start assessment
    assessment = client.assessment.start(test_user)
    assert assessment.session_id is not None
    
    # Submit responses
    responses = [
        {"question_id": "q1", "answer": "option_a", "confidence": 8},
        {"question_id": "q2", "answer": "option_b", "confidence": 7}
    ]
    
    result = client.assessment.submit(assessment.session_id, responses)
    assert result.consciousness_level > 0
    assert result.archetype is not None
    
    # Get learning path
    learning_path = client.learning.get_path(test_user)
    assert learning_path.current_tier is not None
```

### Debugging

#### Debug Mode
```python
from neural_marketing_consciousness import ConsciousnessClient

# Enable debug mode
client = ConsciousnessClient(
    api_key="your_api_key",
    debug=True
)

# All requests will include debug information
assessment = client.assessment.start("user123")
# Debug output: API request/response details
```

#### Logging
```python
import logging
from neural_marketing_consciousness import ConsciousnessClient

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('neural_marketing_consciousness')

# Initialize client with logging
client = ConsciousnessClient(
    api_key="your_api_key",
    logger=logger
)
```

## 📖 Best Practices

### Error Handling
```python
from neural_marketing_consciousness import ConsciousnessClient, ConsciousnessError

client = ConsciousnessClient("your_api_key")

try:
    assessment = client.assessment.start("user123")
except ConsciousnessError as e:
    if e.code == "INSUFFICIENT_CONSCIOUSNESS":
        print("User consciousness level too low")
    elif e.code == "RATE_LIMIT_EXCEEDED":
        print("Rate limit exceeded, please wait")
    else:
        print(f"Error: {e.message}")
```

### Rate Limiting
```python
import time
from neural_marketing_consciousness import ConsciousnessClient

client = ConsciousnessClient("your_api_key")

def make_request_with_retry(func, *args, **kwargs):
    """Make API request with retry logic"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except ConsciousnessError as e:
            if e.code == "RATE_LIMIT_EXCEEDED" and attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))
                continue
            raise
    
    raise Exception("Max retries exceeded")
```

### Caching
```python
from functools import lru_cache
from neural_marketing_consciousness import ConsciousnessClient

client = ConsciousnessClient("your_api_key")

@lru_cache(maxsize=100)
def get_user_dashboard(user_id):
    """Cache dashboard data"""
    return client.dashboard.get(user_id)

# Use cached version
dashboard = get_user_dashboard("user123")
```

---

*This comprehensive developer resources document provides everything needed to integrate with the Neural Marketing Consciousness System API and build custom applications.*

