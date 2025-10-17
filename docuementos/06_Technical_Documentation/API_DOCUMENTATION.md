# 📚 IA Marketing SaaS API Documentation

## Complete API Reference for IA Marketing Platform V4.0

---

## 🔗 Base URLs

- **Development**: `http://localhost:3001`
- **Production**: `https://api.ia-marketing.com`
- **Staging**: `https://staging-api.ia-marketing.com`

---

## 🔐 Authentication

### JWT Token Authentication

All API endpoints (except public ones) require authentication using JWT tokens.

```http
Authorization: Bearer <your-jwt-token>
```

### Getting a Token

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "user-123",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "admin"
    },
    "expiresIn": "7d"
  }
}
```

---

## 📊 Content Generation API

### Generate Text Content

```http
POST /api/ai/generate/text
Authorization: Bearer <token>
Content-Type: application/json

{
  "prompt": "Write a blog post about AI in marketing",
  "type": "blog_post",
  "settings": {
    "model": "gpt-4-turbo",
    "temperature": 0.7,
    "maxTokens": 2000,
    "style": "professional",
    "brand": "TechCorp",
    "audience": "marketers"
  },
  "brandVoice": {
    "tone": "professional",
    "style": "modern",
    "personality": "friendly",
    "values": ["innovation", "quality"],
    "keywords": ["AI", "marketing", "technology"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "content": "# The Future of AI in Marketing\n\nArtificial Intelligence is revolutionizing...",
    "metadata": {
      "model": "gpt-4-turbo",
      "tokens": 1250,
      "processingTime": 2.3,
      "timestamp": "2025-01-15T10:30:00Z"
    },
    "suggestions": [
      "Add more specific examples",
      "Include statistics",
      "Add a call-to-action"
    ],
    "seoScore": 85,
    "readabilityScore": 78
  }
}
```

### Generate Images

```http
POST /api/ai/generate/image
Authorization: Bearer <token>
Content-Type: application/json

{
  "prompt": "Modern marketing dashboard with AI elements",
  "style": "realistic",
  "brand": "TechCorp",
  "size": "1024x1024",
  "quality": "hd"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "imageUrl": "https://api.ia-marketing.com/images/generated/abc123.jpg",
    "prompt": "Modern marketing dashboard with AI elements",
    "variations": [
      "https://api.ia-marketing.com/images/generated/abc123-v1.jpg",
      "https://api.ia-marketing.com/images/generated/abc123-v2.jpg"
    ],
    "metadata": {
      "model": "dall-e-3",
      "size": "1024x1024",
      "processingTime": 5.2
    }
  }
}
```

### Batch Content Generation

```http
POST /api/ai/generate/batch
Authorization: Bearer <token>
Content-Type: application/json

{
  "requests": [
    {
      "prompt": "Write a social media post about AI",
      "type": "social_media"
    },
    {
      "prompt": "Create an email subject line for AI marketing",
      "type": "email_subject"
    }
  ],
  "settings": {
    "model": "gpt-4-turbo",
    "temperature": 0.7
  }
}
```

---

## 🎯 Campaign Management API

### Create Campaign

```http
POST /api/campaigns
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "AI Marketing Campaign Q1 2025",
  "description": "Comprehensive AI marketing campaign",
  "type": "multi_channel",
  "budget": 50000,
  "startDate": "2025-02-01T00:00:00Z",
  "endDate": "2025-04-30T23:59:59Z",
  "channels": ["social_media", "email", "search", "display"],
  "targetAudience": {
    "ageRange": [25, 45],
    "interests": ["technology", "marketing", "AI"],
    "location": "United States",
    "demographics": {
      "profession": "marketing_professionals"
    }
  },
  "goals": {
    "primary": "brand_awareness",
    "secondary": "lead_generation",
    "kpis": ["impressions", "clicks", "conversions"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "campaign-123",
    "name": "AI Marketing Campaign Q1 2025",
    "status": "draft",
    "createdAt": "2025-01-15T10:30:00Z",
    "updatedAt": "2025-01-15T10:30:00Z",
    "budget": 50000,
    "spent": 0,
    "performance": {
      "impressions": 0,
      "clicks": 0,
      "conversions": 0,
      "roi": 0
    }
  }
}
```

### Get Campaigns

```http
GET /api/campaigns?page=1&limit=10&status=active&sortBy=createdAt&order=desc
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "campaigns": [
      {
        "id": "campaign-123",
        "name": "AI Marketing Campaign Q1 2025",
        "status": "active",
        "budget": 50000,
        "spent": 12500,
        "performance": {
          "impressions": 150000,
          "clicks": 3500,
          "conversions": 125,
          "roi": 2.5
        }
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 25,
      "pages": 3
    }
  }
}
```

### Update Campaign

```http
PUT /api/campaigns/campaign-123
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Campaign Name",
  "budget": 75000,
  "status": "active"
}
```

### Delete Campaign

```http
DELETE /api/campaigns/campaign-123
Authorization: Bearer <token>
```

---

## 📈 Analytics API

### Get Dashboard Metrics

```http
GET /api/analytics/dashboard?period=30d&granularity=day
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "revenue": {
      "current": 125000,
      "previous": 98000,
      "change": 27.6,
      "trend": "up"
    },
    "campaigns": {
      "active": 12,
      "total": 45,
      "performance": 8.5
    },
    "content": {
      "generated": 1250,
      "published": 980,
      "engagement": 4.2
    },
    "ai": {
      "generations": 5670,
      "tokensUsed": 1250000,
      "cost": 125.50
    },
    "charts": {
      "revenue": [
        {"date": "2025-01-01", "value": 5000},
        {"date": "2025-01-02", "value": 5500}
      ],
      "campaigns": [
        {"name": "Campaign A", "impressions": 100000, "clicks": 2500},
        {"name": "Campaign B", "impressions": 80000, "clicks": 2000}
      ]
    }
  }
}
```

### Get Campaign Analytics

```http
GET /api/analytics/campaigns/campaign-123?period=7d&metrics=impressions,clicks,conversions
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "campaignId": "campaign-123",
    "period": "7d",
    "metrics": {
      "impressions": {
        "total": 150000,
        "daily": [20000, 22000, 21000, 23000, 25000, 24000, 25000],
        "change": 15.2
      },
      "clicks": {
        "total": 3500,
        "daily": [450, 500, 480, 520, 580, 560, 580],
        "change": 12.8
      },
      "conversions": {
        "total": 125,
        "daily": [15, 18, 16, 20, 22, 21, 22],
        "change": 18.5
      }
    },
    "insights": [
      "Campaign performing 15% above average",
      "Peak performance on weekends",
      "Mobile traffic converting 25% better"
    ],
    "recommendations": [
      "Increase budget for weekend campaigns",
      "Optimize for mobile devices",
      "Test new creative variations"
    ]
  }
}
```

### Get AI Usage Analytics

```http
GET /api/analytics/ai-usage?period=30d&groupBy=day
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "totalGenerations": 5670,
    "totalTokens": 1250000,
    "totalCost": 125.50,
    "byType": {
      "text": 3200,
      "image": 1800,
      "video": 500,
      "audio": 170
    },
    "byModel": {
      "gpt-4-turbo": 4000,
      "dall-e-3": 1800,
      "claude-3": 1200
    },
    "dailyUsage": [
      {"date": "2025-01-01", "generations": 150, "tokens": 35000, "cost": 3.50},
      {"date": "2025-01-02", "generations": 180, "tokens": 42000, "cost": 4.20}
    ],
    "topPrompts": [
      {"prompt": "Write a blog post about...", "count": 45},
      {"prompt": "Create social media content...", "count": 38}
    ]
  }
}
```

---

## 👥 User Management API

### Get User Profile

```http
GET /api/users/profile
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user-123",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "admin",
    "avatar": "https://api.ia-marketing.com/avatars/user-123.jpg",
    "preferences": {
      "theme": "dark",
      "language": "en",
      "notifications": true
    },
    "subscription": {
      "plan": "pro",
      "status": "active",
      "expiresAt": "2025-12-31T23:59:59Z"
    },
    "usage": {
      "generations": 1250,
      "tokens": 250000,
      "campaigns": 15
    }
  }
}
```

### Update User Profile

```http
PUT /api/users/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "John Smith",
  "preferences": {
    "theme": "light",
    "language": "es"
  }
}
```

### Get Team Members

```http
GET /api/users/team?page=1&limit=10
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "members": [
      {
        "id": "user-123",
        "email": "john@example.com",
        "name": "John Doe",
        "role": "admin",
        "status": "active",
        "joinedAt": "2025-01-01T00:00:00Z",
        "lastActive": "2025-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  }
}
```

---

## 🔧 Settings API

### Get AI Settings

```http
GET /api/settings/ai
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "defaultModel": "gpt-4-turbo",
    "temperature": 0.7,
    "maxTokens": 2000,
    "creativity": "balanced",
    "language": "en",
    "includeSEO": true,
    "includeCTA": true,
    "brandVoice": {
      "tone": "professional",
      "style": "modern",
      "personality": "friendly"
    }
  }
}
```

### Update AI Settings

```http
PUT /api/settings/ai
Authorization: Bearer <token>
Content-Type: application/json

{
  "defaultModel": "gpt-4-turbo",
  "temperature": 0.8,
  "maxTokens": 3000,
  "creativity": "high"
}
```

### Get Brand Voice

```http
GET /api/settings/brand-voice
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "tone": "professional",
    "style": "modern",
    "personality": "friendly",
    "values": ["innovation", "quality", "trust"],
    "keywords": ["AI", "marketing", "technology"],
    "avoidWords": ["cheap", "free", "guaranteed"],
    "examples": [
      "Our AI-powered solutions help marketers achieve better results",
      "Innovation drives everything we do at TechCorp"
    ]
  }
}
```

---

## 🔔 Webhooks API

### Register Webhook

```http
POST /api/webhooks
Authorization: Bearer <token>
Content-Type: application/json

{
  "url": "https://your-app.com/webhooks/ia-marketing",
  "events": ["campaign.created", "content.generated", "analytics.updated"],
  "secret": "your-webhook-secret"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "webhook-123",
    "url": "https://your-app.com/webhooks/ia-marketing",
    "events": ["campaign.created", "content.generated", "analytics.updated"],
    "status": "active",
    "createdAt": "2025-01-15T10:30:00Z"
  }
}
```

### Webhook Events

#### Campaign Created
```json
{
  "event": "campaign.created",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "id": "campaign-123",
    "name": "AI Marketing Campaign",
    "userId": "user-123",
    "budget": 50000
  }
}
```

#### Content Generated
```json
{
  "event": "content.generated",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "id": "content-123",
    "type": "text",
    "userId": "user-123",
    "model": "gpt-4-turbo",
    "tokens": 1250,
    "cost": 0.125
  }
}
```

---

## 📊 Real-time API (WebSocket)

### Connection

```javascript
const socket = io('wss://api.ia-marketing.com', {
  auth: {
    token: 'your-jwt-token'
  }
});
```

### Events

#### Join User Room
```javascript
socket.emit('join-user-room', 'user-123');
```

#### Subscribe to Analytics
```javascript
socket.emit('subscribe-analytics', 'campaign-123');
```

#### AI Generation Progress
```javascript
socket.emit('subscribe-ai-generation', 'task-123');

socket.on('ai-generation-progress', (data) => {
  console.log(`Progress: ${data.progress}%`);
});
```

---

## 🚨 Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Email is required"
      }
    ]
  },
  "timestamp": "2025-01-15T10:30:00Z",
  "requestId": "req-123"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

### Error Codes

- `VALIDATION_ERROR` - Input validation failed
- `AUTHENTICATION_ERROR` - Invalid credentials
- `AUTHORIZATION_ERROR` - Insufficient permissions
- `RATE_LIMIT_ERROR` - Too many requests
- `AI_SERVICE_ERROR` - AI service unavailable
- `PAYMENT_ERROR` - Payment processing failed
- `QUOTA_EXCEEDED` - Usage quota exceeded

---

## 🔒 Rate Limiting

### Limits

- **Free Plan**: 100 requests/hour
- **Pro Plan**: 1000 requests/hour
- **Enterprise Plan**: 10000 requests/hour

### Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

---

## 📝 SDKs and Libraries

### JavaScript/Node.js

```bash
npm install @ia-marketing/sdk
```

```javascript
import { IAMarketingClient } from '@ia-marketing/sdk';

const client = new IAMarketingClient({
  apiKey: 'your-api-key',
  baseURL: 'https://api.ia-marketing.com'
});

// Generate content
const content = await client.ai.generateText({
  prompt: 'Write a blog post about AI',
  type: 'blog_post'
});
```

### Python

```bash
pip install ia-marketing-sdk
```

```python
from ia_marketing import IAMarketingClient

client = IAMarketingClient(
    api_key='your-api-key',
    base_url='https://api.ia-marketing.com'
)

# Generate content
content = client.ai.generate_text(
    prompt='Write a blog post about AI',
    type='blog_post'
)
```

### PHP

```bash
composer require ia-marketing/sdk
```

```php
use IAMarketing\Client;

$client = new Client([
    'api_key' => 'your-api-key',
    'base_url' => 'https://api.ia-marketing.com'
]);

// Generate content
$content = $client->ai->generateText([
    'prompt' => 'Write a blog post about AI',
    'type' => 'blog_post'
]);
```

---

## 🧪 Testing

### Test Environment

- **Base URL**: `https://test-api.ia-marketing.com`
- **Test API Key**: `test_sk_1234567890abcdef`

### Postman Collection

Download our Postman collection: [IA Marketing API.postman_collection.json](https://api.ia-marketing.com/docs/postman-collection.json)

### cURL Examples

```bash
# Generate text content
curl -X POST https://api.ia-marketing.com/api/ai/generate/text \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a blog post about AI in marketing",
    "type": "blog_post"
  }'

# Get campaigns
curl -X GET https://api.ia-marketing.com/api/campaigns \
  -H "Authorization: Bearer your-token"
```

---

## 📞 Support

- **API Documentation**: https://docs.ia-marketing.com/api
- **Status Page**: https://status.ia-marketing.com
- **Support Email**: api-support@ia-marketing.com
- **Discord**: https://discord.gg/ia-marketing

---

**🎯 Ready to integrate? Start building amazing AI-powered marketing applications today!**

