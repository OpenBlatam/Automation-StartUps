# API Documentation: AI Course & SaaS Marketing Platform

## Table of Contents
1. [Authentication](#authentication)
2. [AI Course Platform APIs](#ai-course-platform-apis)
3. [SaaS Marketing Platform APIs](#saas-marketing-platform-apis)
4. [Social Media Integration APIs](#social-media-integration-apis)
5. [Analytics and Reporting APIs](#analytics-and-reporting-apis)
6. [Webhook Documentation](#webhook-documentation)
7. [SDK and Libraries](#sdk-and-libraries)

## Authentication

### API Key Authentication
```bash
# Include API key in header
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     https://api.ai-marketing-platform.com/v1/campaigns
```

### OAuth 2.0 Authentication
```javascript
// OAuth 2.0 flow implementation
const authConfig = {
  clientId: 'your_client_id',
  clientSecret: 'your_client_secret',
  redirectUri: 'https://your-app.com/callback',
  scopes: ['read', 'write', 'admin']
};

// Get authorization URL
const authUrl = `https://api.ai-marketing-platform.com/oauth/authorize?` +
  `client_id=${authConfig.clientId}&` +
  `redirect_uri=${authConfig.redirectUri}&` +
  `scope=${authConfig.scopes.join(' ')}&` +
  `response_type=code`;

// Exchange code for access token
const tokenResponse = await fetch('https://api.ai-marketing-platform.com/oauth/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    grant_type: 'authorization_code',
    code: authorizationCode,
    client_id: authConfig.clientId,
    client_secret: authConfig.clientSecret,
    redirect_uri: authConfig.redirectUri
  })
});
```

## AI Course Platform APIs

### Course Management

#### Get All Courses
```http
GET /api/v1/courses
```

**Response:**
```json
{
  "courses": [
    {
      "id": "course_001",
      "title": "AI Fundamentals",
      "description": "Comprehensive introduction to artificial intelligence",
      "duration_weeks": 4,
      "difficulty_level": "beginner",
      "instructor": "Dr. Sarah Chen",
      "enrollment_count": 1250,
      "rating": 4.8,
      "price": 299.99,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1
  }
}
```

#### Create Course
```http
POST /api/v1/courses
```

**Request Body:**
```json
{
  "title": "Advanced Machine Learning",
  "description": "Deep dive into advanced ML techniques",
  "duration_weeks": 8,
  "difficulty_level": "advanced",
  "instructor_id": "instructor_001",
  "price": 599.99,
  "modules": [
    {
      "title": "Deep Learning Fundamentals",
      "order": 1,
      "content": "Introduction to neural networks...",
      "duration_hours": 6
    }
  ]
}
```

#### Enroll in Course
```http
POST /api/v1/courses/{course_id}/enroll
```

**Request Body:**
```json
{
  "user_id": "user_123",
  "payment_method": "credit_card",
  "payment_token": "tok_123456789"
}
```

### Content Generation

#### Generate Lesson Content
```http
POST /api/v1/ai/generate-lesson
```

**Request Body:**
```json
{
  "topic": "Neural Networks",
  "level": "intermediate",
  "duration_minutes": 45,
  "learning_objectives": [
    "Understand neural network architecture",
    "Implement basic neural networks",
    "Apply neural networks to real problems"
  ],
  "format": "interactive"
}
```

**Response:**
```json
{
  "lesson": {
    "title": "Introduction to Neural Networks",
    "content": {
      "introduction": "Neural networks are computing systems...",
      "theory": "The mathematical foundation...",
      "examples": [
        {
          "title": "Perceptron Example",
          "code": "import numpy as np\n\nclass Perceptron:\n    def __init__(self, learning_rate=0.01):\n        self.learning_rate = learning_rate\n        self.weights = None\n        self.bias = None",
          "explanation": "This is a simple perceptron implementation..."
        }
      ],
      "exercises": [
        {
          "question": "What is the purpose of the activation function?",
          "type": "multiple_choice",
          "options": [
            "To normalize inputs",
            "To introduce non-linearity",
            "To reduce computation",
            "To prevent overfitting"
          ],
          "correct_answer": 1
        }
      ]
    },
    "estimated_duration": 45,
    "difficulty_score": 0.6
  }
}
```

#### Generate Quiz Questions
```http
POST /api/v1/ai/generate-quiz
```

**Request Body:**
```json
{
  "topic": "Machine Learning",
  "question_count": 10,
  "difficulty": "intermediate",
  "question_types": ["multiple_choice", "true_false", "coding"]
}
```

## SaaS Marketing Platform APIs

### Campaign Management

#### Create Campaign
```http
POST /api/v1/campaigns
```

**Request Body:**
```json
{
  "name": "Tech Talent Q1 2024",
  "description": "Recruitment campaign for software engineers",
  "platforms": ["linkedin", "facebook", "twitter"],
  "target_audience": {
    "demographics": {
      "age_range": [25, 35],
      "location": "San Francisco Bay Area",
      "education": "Bachelor's Degree",
      "experience_level": "2-5 years"
    },
    "interests": ["software development", "AI/ML", "startups"],
    "behaviors": ["job_searching", "tech_news_engagement"]
  },
  "content": {
    "template_id": "tech_recruitment_001",
    "customizations": {
      "company_name": "TechCorp",
      "position": "Senior Software Engineer",
      "unique_benefits": "Remote work, equity, learning budget"
    }
  },
  "budget": {
    "daily_budget": 100,
    "total_budget": 3000
  },
  "schedule": {
    "start_date": "2024-01-15",
    "end_date": "2024-02-15",
    "posting_times": ["09:00", "13:00", "17:00"]
  }
}
```

#### Get Campaign Analytics
```http
GET /api/v1/campaigns/{campaign_id}/analytics
```

**Query Parameters:**
- `start_date`: Start date for analytics (ISO 8601)
- `end_date`: End date for analytics (ISO 8601)
- `metrics`: Comma-separated list of metrics to include

**Response:**
```json
{
  "campaign_id": "campaign_123",
  "date_range": {
    "start": "2024-01-15",
    "end": "2024-02-15"
  },
  "metrics": {
    "reach": {
      "total_impressions": 125000,
      "total_reach": 85000,
      "unique_reach": 75000
    },
    "engagement": {
      "total_likes": 2500,
      "total_comments": 450,
      "total_shares": 320,
      "engagement_rate": 0.045
    },
    "conversions": {
      "total_clicks": 1200,
      "total_applications": 85,
      "conversion_rate": 0.071,
      "cost_per_application": 35.29
    },
    "performance": {
      "click_through_rate": 0.0096,
      "cost_per_click": 2.50,
      "return_on_ad_spend": 3.2
    }
  },
  "platform_breakdown": {
    "linkedin": {
      "impressions": 75000,
      "clicks": 800,
      "applications": 60
    },
    "facebook": {
      "impressions": 35000,
      "clicks": 300,
      "applications": 20
    },
    "twitter": {
      "impressions": 15000,
      "clicks": 100,
      "applications": 5
    }
  }
}
```

### Content Generation

#### Generate Social Media Post
```http
POST /api/v1/content/generate/social-post
```

**Request Body:**
```json
{
  "platform": "linkedin",
  "campaign_type": "recruitment",
  "target_audience": "software engineers",
  "position": "Full Stack Developer",
  "company_values": ["innovation", "collaboration", "growth"],
  "unique_selling_point": "Cutting-edge AI projects",
  "style": "conversational",
  "include_hashtags": true,
  "include_emojis": true,
  "length": "medium"
}
```

**Response:**
```json
{
  "content": {
    "text": "🚀 Ready to build the future of AI? We're looking for a Full Stack Developer to join our innovative team!\n\nAt TechCorp, you'll work on cutting-edge AI projects that are revolutionizing the industry. Our collaborative environment fosters growth and innovation every day.\n\nWhat we offer:\n✅ Remote-first culture\n✅ Equity participation\n✅ Learning and development budget\n✅ Top-tier benefits\n\nReady to make an impact? Apply now: [link]\n\n#TechJobs #AI #Innovation #CareerGrowth #TechCorp",
    "hashtags": ["#TechJobs", "#AI", "#Innovation", "#CareerGrowth", "#TechCorp"],
    "estimated_engagement": 0.045,
    "optimal_posting_time": "13:00",
    "a_b_test_variants": [
      {
        "variant": "A",
        "text": "🚀 Ready to build the future of AI? We're looking for a Full Stack Developer...",
        "changes": "Original version"
      },
      {
        "variant": "B", 
        "text": "💡 Calling all Full Stack Developers! Join our AI revolution at TechCorp...",
        "changes": "Different hook and emoji"
      }
    ]
  }
}
```

#### Generate Job Description
```http
POST /api/v1/content/generate/job-description
```

**Request Body:**
```json
{
  "position": "Data Scientist",
  "company": "AI Startup",
  "industry": "Technology",
  "requirements": [
    "Python programming",
    "Machine learning",
    "Statistics",
    "3+ years experience"
  ],
  "benefits": [
    "Competitive salary",
    "Equity package",
    "Remote work",
    "Learning budget"
  ],
  "tone": "professional",
  "length": "medium"
}
```

## Social Media Integration APIs

### LinkedIn Integration

#### Post to LinkedIn
```http
POST /api/v1/social/linkedin/post
```

**Request Body:**
```json
{
  "content": "🚀 Exciting opportunity for Data Scientists...",
  "visibility": "PUBLIC",
  "scheduling": {
    "publish_at": "2024-01-15T13:00:00Z"
  },
  "targeting": {
    "audience_network": "LINKEDIN",
    "demographics": {
      "age_range": [25, 35],
      "locations": ["San Francisco Bay Area"],
      "education": ["Bachelor's Degree"]
    }
  }
}
```

#### Get LinkedIn Analytics
```http
GET /api/v1/social/linkedin/analytics/{post_id}
```

### Facebook/Meta Integration

#### Create Facebook Ad Campaign
```http
POST /api/v1/social/facebook/campaign
```

**Request Body:**
```json
{
  "name": "Tech Recruitment Campaign",
  "objective": "LEAD_GENERATION",
  "status": "PAUSED",
  "budget": {
    "daily_budget": 50
  },
  "targeting": {
    "geo_locations": {
      "countries": ["US"],
      "regions": [{"key": "California"}]
    },
    "interests": [
      {"id": "6003107902433", "name": "Software engineering"},
      {"id": "6004037226511", "name": "Artificial intelligence"}
    ],
    "education_statuses": [3, 4, 5],
    "age_min": 25,
    "age_max": 35
  },
  "creative": {
    "title": "Join Our AI Team",
    "description": "We're looking for talented developers...",
    "image_url": "https://example.com/image.jpg",
    "call_to_action": "APPLY_NOW"
  }
}
```

### Twitter Integration

#### Tweet with Media
```http
POST /api/v1/social/twitter/tweet
```

**Request Body:**
```json
{
  "text": "🚀 We're hiring! Join our AI team and build the future. #TechJobs #AI",
  "media": {
    "type": "image",
    "url": "https://example.com/recruitment-image.jpg"
  },
  "scheduling": {
    "publish_at": "2024-01-15T14:00:00Z"
  }
}
```

## Analytics and Reporting APIs

### Real-Time Analytics

#### Get Real-Time Campaign Metrics
```http
GET /api/v1/analytics/realtime/{campaign_id}
```

**Response:**
```json
{
  "campaign_id": "campaign_123",
  "timestamp": "2024-01-15T14:30:00Z",
  "metrics": {
    "impressions": {
      "current": 1250,
      "change_1h": 0.15,
      "change_24h": 0.45
    },
    "engagement": {
      "current_rate": 0.042,
      "change_1h": -0.02,
      "change_24h": 0.08
    },
    "conversions": {
      "applications_today": 3,
      "cost_per_application": 28.50
    }
  },
  "alerts": [
    {
      "type": "performance",
      "message": "Engagement rate below threshold",
      "severity": "warning"
    }
  ]
}
```

### Custom Reports

#### Generate Custom Report
```http
POST /api/v1/analytics/reports
```

**Request Body:**
```json
{
  "name": "Q1 Recruitment Performance",
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-03-31"
  },
  "campaigns": ["campaign_123", "campaign_456"],
  "metrics": [
    "impressions",
    "engagement_rate",
    "cost_per_application",
    "conversion_rate"
  ],
  "grouping": "platform",
  "format": "pdf"
}
```

## Webhook Documentation

### Campaign Performance Webhooks

#### Webhook Configuration
```http
POST /api/v1/webhooks
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhooks/campaign-performance",
  "events": [
    "campaign.performance_threshold_exceeded",
    "campaign.budget_exhausted",
    "campaign.optimization_completed"
  ],
  "secret": "your_webhook_secret"
}
```

#### Webhook Payload Example
```json
{
  "event": "campaign.performance_threshold_exceeded",
  "timestamp": "2024-01-15T14:30:00Z",
  "data": {
    "campaign_id": "campaign_123",
    "campaign_name": "Tech Talent Q1 2024",
    "threshold": "engagement_rate",
    "current_value": 0.045,
    "threshold_value": 0.05,
    "action_taken": "automatic_optimization"
  }
}
```

### Candidate Application Webhooks

#### Application Received Webhook
```json
{
  "event": "application.received",
  "timestamp": "2024-01-15T14:30:00Z",
  "data": {
    "application_id": "app_789",
    "campaign_id": "campaign_123",
    "candidate": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "resume_url": "https://storage.example.com/resumes/app_789.pdf"
    },
    "position": "Senior Software Engineer",
    "source": "linkedin",
    "application_data": {
      "cover_letter": "I'm excited about this opportunity...",
      "salary_expectation": 120000,
      "availability": "2024-02-01"
    }
  }
}
```

## SDK and Libraries

### Python SDK

#### Installation
```bash
pip install ai-marketing-platform-sdk
```

#### Usage Example
```python
from ai_marketing_platform import Client, Campaign, ContentGenerator

# Initialize client
client = Client(api_key='your_api_key')

# Create campaign
campaign = Campaign(
    name="Tech Recruitment Q1",
    platforms=["linkedin", "facebook"],
    budget=3000
)

# Generate content
content_generator = ContentGenerator(client)
content = content_generator.generate_social_post(
    platform="linkedin",
    position="Data Scientist",
    company="TechCorp"
)

# Launch campaign
campaign.launch()

# Monitor performance
analytics = campaign.get_analytics()
print(f"Engagement rate: {analytics.engagement_rate}")
```

### JavaScript SDK

#### Installation
```bash
npm install ai-marketing-platform-sdk
```

#### Usage Example
```javascript
import { Client, Campaign, ContentGenerator } from 'ai-marketing-platform-sdk';

// Initialize client
const client = new Client({
  apiKey: 'your_api_key',
  environment: 'production'
});

// Create campaign
const campaign = new Campaign({
  name: 'Tech Recruitment Q1',
  platforms: ['linkedin', 'facebook'],
  budget: 3000
});

// Generate content
const contentGenerator = new ContentGenerator(client);
const content = await contentGenerator.generateSocialPost({
  platform: 'linkedin',
  position: 'Data Scientist',
  company: 'TechCorp'
});

// Launch campaign
await campaign.launch();

// Monitor performance
const analytics = await campaign.getAnalytics();
console.log(`Engagement rate: ${analytics.engagementRate}`);
```

### React Components

#### Campaign Dashboard Component
```jsx
import React, { useState, useEffect } from 'react';
import { useCampaign } from 'ai-marketing-platform-react';

const CampaignDashboard = ({ campaignId }) => {
  const { campaign, analytics, loading, error } = useCampaign(campaignId);
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div className="campaign-dashboard">
      <h2>{campaign.name}</h2>
      <div className="metrics">
        <div className="metric">
          <span className="label">Impressions</span>
          <span className="value">{analytics.impressions.toLocaleString()}</span>
        </div>
        <div className="metric">
          <span className="label">Engagement Rate</span>
          <span className="value">{(analytics.engagementRate * 100).toFixed(2)}%</span>
        </div>
        <div className="metric">
          <span className="label">Applications</span>
          <span className="value">{analytics.applications}</span>
        </div>
      </div>
    </div>
  );
};

export default CampaignDashboard;
```

---

## Rate Limits

| Endpoint Category | Rate Limit | Burst Limit |
|------------------|------------|-------------|
| Campaign Management | 100 requests/minute | 200 requests/minute |
| Content Generation | 50 requests/minute | 100 requests/minute |
| Analytics | 200 requests/minute | 400 requests/minute |
| Social Media Posts | 30 requests/minute | 60 requests/minute |

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "details": {
      "limit": 100,
      "remaining": 0,
      "reset_time": "2024-01-15T15:00:00Z"
    }
  }
}
```

### Common Error Codes
- `INVALID_API_KEY`: API key is missing or invalid
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `VALIDATION_ERROR`: Request validation failed
- `CAMPAIGN_NOT_FOUND`: Campaign does not exist
- `INSUFFICIENT_BUDGET`: Campaign budget is too low
- `PLATFORM_ERROR`: Social media platform error

---

*This API documentation provides comprehensive coverage of all endpoints and functionality available in our AI Course and SaaS Marketing Platform. For additional support, please contact our developer relations team.*









