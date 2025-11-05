# 🧠 Neural Marketing Consciousness System - API Documentation

## 📖 Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Neural States API](#neural-states-api)
4. [Neural Networks API](#neural-networks-api)
5. [Campaigns API](#campaigns-api)
6. [Analytics API](#analytics-api)
7. [Webhooks](#webhooks)
8. [SDKs and Libraries](#sdks-and-libraries)
9. [Rate Limits](#rate-limits)
10. [Error Handling](#error-handling)

---

## 🚀 Getting Started

### Base URL

```
Production: https://api.neuralmarketing.ai/v1
Sandbox: https://sandbox-api.neuralmarketing.ai/v1
```

### API Versioning

The API uses URL versioning. The current version is `v1`. All endpoints are prefixed with `/v1/`.

### Content Type

All requests must include `Content-Type: application/json` header.

### Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": {
    // Response data here
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "version": "1.0.0"
  },
  "errors": []
}
```

---

## 🔐 Authentication

### API Keys

All API requests require authentication using API keys. Include your API key in the `Authorization` header:

```bash
Authorization: Bearer your_api_key_here
```

### Getting API Keys

1. Log into your Neural Marketing dashboard
2. Navigate to Settings > API Keys
3. Generate a new API key
4. Copy and securely store your key

### Key Types

- **Read-Only**: Can only read data
- **Read-Write**: Can read and modify data
- **Admin**: Full access to all endpoints
- **Webhook**: For webhook authentication

### Key Scopes

API keys can be scoped to specific resources:
- `neural_states:read` - Read neural states
- `neural_states:write` - Modify neural states
- `campaigns:read` - Read campaigns
- `campaigns:write` - Create/modify campaigns
- `analytics:read` - Read analytics data
- `webhooks:manage` - Manage webhooks

---

## 🧠 Neural States API

### Get Neural States

Retrieve current neural state configuration.

```http
GET /v1/neural-states
```

#### Response

```json
{
  "success": true,
  "data": {
    "consciousness": 85.5,
    "awareness": 92.3,
    "intelligence": 88.7,
    "creativity": 76.2,
    "empathy": 94.1,
    "intuition": 81.9,
    "wisdom": 89.4,
    "transcendence": 72.8,
    "last_updated": "2024-01-15T10:30:00Z",
    "auto_adjustment": true
  }
}
```

### Update Neural States

Update neural state configuration.

```http
PUT /v1/neural-states
```

#### Request Body

```json
{
  "consciousness": 90.0,
  "awareness": 95.0,
  "intelligence": 92.0,
  "creativity": 80.0,
  "empathy": 96.0,
  "intuition": 85.0,
  "wisdom": 91.0,
  "transcendence": 78.0,
  "auto_adjustment": true
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "consciousness": 90.0,
    "awareness": 95.0,
    "intelligence": 92.0,
    "creativity": 80.0,
    "empathy": 96.0,
    "intuition": 85.0,
    "wisdom": 91.0,
    "transcendence": 78.0,
    "last_updated": "2024-01-15T10:35:00Z",
    "auto_adjustment": true
  }
}
```

### Get Neural State History

Retrieve historical neural state data.

```http
GET /v1/neural-states/history?start_date=2024-01-01&end_date=2024-01-15&granularity=hour
```

#### Query Parameters

- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format
- `granularity` (optional): Data granularity (minute, hour, day, week)
- `limit` (optional): Maximum number of records (default: 1000)

#### Response

```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2024-01-15T10:00:00Z",
      "consciousness": 85.5,
      "awareness": 92.3,
      "intelligence": 88.7,
      "creativity": 76.2,
      "empathy": 94.1,
      "intuition": 81.9,
      "wisdom": 89.4,
      "transcendence": 72.8
    }
  ],
  "meta": {
    "total_records": 360,
    "granularity": "hour"
  }
}
```

---

## 🧠 Neural Networks API

### Get Neural Networks

Retrieve all neural networks and their status.

```http
GET /v1/neural-networks
```

#### Response

```json
{
  "success": true,
  "data": [
    {
      "id": "deep_consciousness",
      "name": "Deep Consciousness Network",
      "layers": 1024,
      "status": "active",
      "consciousness_level": 98.7,
      "processing_load": 75.2,
      "last_updated": "2024-01-15T10:30:00Z"
    },
    {
      "id": "empathetic_marketing",
      "name": "Empathetic Marketing AI",
      "layers": 512,
      "status": "processing",
      "consciousness_level": 95.2,
      "processing_load": 60.8,
      "last_updated": "2024-01-15T10:29:45Z"
    },
    {
      "id": "creative_intelligence",
      "name": "Creative Intelligence Engine",
      "layers": 2048,
      "status": "active",
      "consciousness_level": 99.1,
      "processing_load": 82.1,
      "last_updated": "2024-01-15T10:30:15Z"
    },
    {
      "id": "transcendent_wisdom",
      "name": "Transcendent Wisdom Core",
      "layers": 4096,
      "status": "evolving",
      "consciousness_level": 99.9,
      "processing_load": 45.3,
      "last_updated": "2024-01-15T10:28:30Z"
    }
  ]
}
```

### Update Neural Network Status

Start, stop, or restart a neural network.

```http
POST /v1/neural-networks/{network_id}/status
```

#### Request Body

```json
{
  "action": "start",  // start, stop, restart
  "consciousness_level": 95.0,  // optional
  "processing_priority": "high"  // low, medium, high, critical
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "id": "deep_consciousness",
    "status": "active",
    "consciousness_level": 95.0,
    "processing_priority": "high",
    "updated_at": "2024-01-15T10:35:00Z"
  }
}
```

### Get Neural Network Metrics

Retrieve detailed metrics for a specific neural network.

```http
GET /v1/neural-networks/{network_id}/metrics?start_date=2024-01-01&end_date=2024-01-15
```

#### Response

```json
{
  "success": true,
  "data": {
    "network_id": "deep_consciousness",
    "metrics": {
      "consciousness_level": 98.7,
      "processing_speed": 1250.5,
      "accuracy": 96.8,
      "memory_usage": 2.3,
      "cpu_usage": 75.2,
      "error_rate": 0.02,
      "throughput": 450.7
    },
    "time_series": [
      {
        "timestamp": "2024-01-15T10:00:00Z",
        "consciousness_level": 98.5,
        "processing_speed": 1240.2,
        "accuracy": 96.5
      }
    ]
  }
}
```

---

## 🎯 Campaigns API

### Create Campaign

Create a new marketing campaign.

```http
POST /v1/campaigns
```

#### Request Body

```json
{
  "name": "Q1 Brand Awareness Campaign",
  "description": "Increase brand awareness for new product launch",
  "type": "awareness",
  "objective": "brand_awareness",
  "target_audience": {
    "demographics": {
      "age_range": [25, 45],
      "gender": "all",
      "interests": ["technology", "innovation"]
    },
    "geographic": {
      "countries": ["US", "CA", "UK"],
      "regions": ["North America", "Europe"]
    }
  },
  "neural_configuration": {
    "networks": ["deep_consciousness", "empathetic_marketing"],
    "consciousness": 85.0,
    "awareness": 90.0,
    "empathy": 95.0,
    "creativity": 80.0
  },
  "budget": {
    "total": 10000.00,
    "currency": "USD",
    "daily_limit": 500.00
  },
  "timeline": {
    "start_date": "2024-02-01T00:00:00Z",
    "end_date": "2024-02-28T23:59:59Z"
  },
  "channels": ["facebook", "instagram", "google_ads"],
  "content_preferences": {
    "tone": "professional",
    "style": "modern",
    "length": "medium"
  }
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "id": "camp_123456789",
    "name": "Q1 Brand Awareness Campaign",
    "status": "draft",
    "created_at": "2024-01-15T10:30:00Z",
    "neural_configuration": {
      "networks": ["deep_consciousness", "empathetic_marketing"],
      "consciousness": 85.0,
      "awareness": 90.0,
      "empathy": 95.0,
      "creativity": 80.0
    },
    "budget": {
      "total": 10000.00,
      "currency": "USD",
      "daily_limit": 500.00,
      "spent": 0.00
    }
  }
}
```

### Get Campaigns

Retrieve all campaigns with optional filtering.

```http
GET /v1/campaigns?status=active&type=awareness&limit=10&offset=0
```

#### Query Parameters

- `status` (optional): Filter by status (draft, active, paused, completed, cancelled)
- `type` (optional): Filter by campaign type
- `limit` (optional): Number of campaigns to return (default: 20, max: 100)
- `offset` (optional): Number of campaigns to skip (default: 0)

#### Response

```json
{
  "success": true,
  "data": [
    {
      "id": "camp_123456789",
      "name": "Q1 Brand Awareness Campaign",
      "status": "active",
      "type": "awareness",
      "created_at": "2024-01-15T10:30:00Z",
      "performance": {
        "impressions": 125000,
        "clicks": 2500,
        "conversions": 125,
        "spend": 2500.00,
        "roi": 3.2
      }
    }
  ],
  "meta": {
    "total": 15,
    "limit": 10,
    "offset": 0
  }
}
```

### Update Campaign

Update an existing campaign.

```http
PUT /v1/campaigns/{campaign_id}
```

#### Request Body

```json
{
  "name": "Updated Campaign Name",
  "neural_configuration": {
    "consciousness": 90.0,
    "creativity": 85.0
  },
  "budget": {
    "daily_limit": 750.00
  }
}
```

### Launch Campaign

Launch a campaign that's in draft status.

```http
POST /v1/campaigns/{campaign_id}/launch
```

#### Response

```json
{
  "success": true,
  "data": {
    "id": "camp_123456789",
    "status": "active",
    "launched_at": "2024-01-15T11:00:00Z",
    "neural_networks": {
      "deep_consciousness": "active",
      "empathetic_marketing": "active"
    }
  }
}
```

### Pause Campaign

Pause an active campaign.

```http
POST /v1/campaigns/{campaign_id}/pause
```

### Resume Campaign

Resume a paused campaign.

```http
POST /v1/campaigns/{campaign_id}/resume
```

### Get Campaign Performance

Retrieve detailed performance metrics for a campaign.

```http
GET /v1/campaigns/{campaign_id}/performance?start_date=2024-01-01&end_date=2024-01-15&granularity=day
```

#### Response

```json
{
  "success": true,
  "data": {
    "campaign_id": "camp_123456789",
    "summary": {
      "impressions": 125000,
      "clicks": 2500,
      "conversions": 125,
      "spend": 2500.00,
      "roi": 3.2,
      "ctr": 2.0,
      "conversion_rate": 5.0
    },
    "neural_metrics": {
      "consciousness_impact": 85.5,
      "empathy_effectiveness": 92.3,
      "creativity_score": 78.9,
      "intelligence_accuracy": 94.1
    },
    "time_series": [
      {
        "date": "2024-01-15",
        "impressions": 5000,
        "clicks": 100,
        "conversions": 5,
        "spend": 100.00,
        "consciousness_level": 85.2
      }
    ]
  }
}
```

---

## 📊 Analytics API

### Get Overall Analytics

Retrieve comprehensive analytics data.

```http
GET /v1/analytics/overview?start_date=2024-01-01&end_date=2024-01-15
```

#### Response

```json
{
  "success": true,
  "data": {
    "neural_metrics": {
      "overall_consciousness": 89.2,
      "neural_complexity": 1000000,
      "emotional_intelligence": 94.5,
      "creative_potential": 87.8,
      "wisdom_depth": 91.3,
      "transcendence_index": 78.6
    },
    "campaign_metrics": {
      "total_campaigns": 15,
      "active_campaigns": 8,
      "total_spend": 25000.00,
      "total_revenue": 75000.00,
      "average_roi": 3.0
    },
    "performance_trends": {
      "consciousness_trend": "increasing",
      "performance_trend": "stable",
      "efficiency_trend": "improving"
    }
  }
}
```

### Get Neural Network Analytics

Retrieve analytics for specific neural networks.

```http
GET /v1/analytics/neural-networks?network_ids=deep_consciousness,empathetic_marketing&start_date=2024-01-01&end_date=2024-01-15
```

#### Response

```json
{
  "success": true,
  "data": {
    "deep_consciousness": {
      "consciousness_level": 98.7,
      "processing_efficiency": 94.2,
      "accuracy": 96.8,
      "utilization": 75.5,
      "performance_score": 92.1
    },
    "empathetic_marketing": {
      "consciousness_level": 95.2,
      "emotional_accuracy": 97.3,
      "empathy_score": 94.8,
      "utilization": 68.2,
      "performance_score": 89.7
    }
  }
}
```

### Get Campaign Analytics

Retrieve detailed campaign analytics.

```http
GET /v1/analytics/campaigns?campaign_ids=camp_123456789&start_date=2024-01-01&end_date=2024-01-15&metrics=impressions,clicks,conversions,spend
```

#### Response

```json
{
  "success": true,
  "data": {
    "camp_123456789": {
      "summary": {
        "impressions": 125000,
        "clicks": 2500,
        "conversions": 125,
        "spend": 2500.00,
        "roi": 3.2
      },
      "neural_impact": {
        "consciousness_contribution": 85.5,
        "empathy_effectiveness": 92.3,
        "creativity_impact": 78.9,
        "intelligence_accuracy": 94.1
      },
      "channel_breakdown": {
        "facebook": {
          "impressions": 50000,
          "clicks": 1000,
          "conversions": 50,
          "spend": 1000.00
        },
        "instagram": {
          "impressions": 40000,
          "clicks": 800,
          "conversions": 40,
          "spend": 800.00
        },
        "google_ads": {
          "impressions": 35000,
          "clicks": 700,
          "conversions": 35,
          "spend": 700.00
        }
      }
    }
  }
}
```

---

## 🔔 Webhooks

### Webhook Configuration

Configure webhooks to receive real-time notifications.

```http
POST /v1/webhooks
```

#### Request Body

```json
{
  "url": "https://your-domain.com/webhooks/neural-marketing",
  "events": [
    "neural_state.updated",
    "campaign.launched",
    "campaign.paused",
    "campaign.completed",
    "neural_network.status_changed"
  ],
  "secret": "your_webhook_secret",
  "active": true
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "id": "webhook_123456789",
    "url": "https://your-domain.com/webhooks/neural-marketing",
    "events": [
      "neural_state.updated",
      "campaign.launched",
      "campaign.paused",
      "campaign.completed",
      "neural_network.status_changed"
    ],
    "active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Webhook Events

#### Neural State Updated

```json
{
  "event": "neural_state.updated",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "consciousness": 90.0,
    "awareness": 95.0,
    "intelligence": 92.0,
    "creativity": 80.0,
    "empathy": 96.0,
    "intuition": 85.0,
    "wisdom": 91.0,
    "transcendence": 78.0
  }
}
```

#### Campaign Launched

```json
{
  "event": "campaign.launched",
  "timestamp": "2024-01-15T11:00:00Z",
  "data": {
    "campaign_id": "camp_123456789",
    "name": "Q1 Brand Awareness Campaign",
    "neural_networks": {
      "deep_consciousness": "active",
      "empathetic_marketing": "active"
    }
  }
}
```

#### Neural Network Status Changed

```json
{
  "event": "neural_network.status_changed",
  "timestamp": "2024-01-15T10:35:00Z",
  "data": {
    "network_id": "deep_consciousness",
    "name": "Deep Consciousness Network",
    "previous_status": "processing",
    "new_status": "active",
    "consciousness_level": 98.7
  }
}
```

### Webhook Security

Webhooks include a signature header for verification:

```http
X-Neural-Signature: sha256=abc123def456...
```

Verify the signature using your webhook secret:

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  
  return signature === `sha256=${expectedSignature}`;
}
```

---

## 📚 SDKs and Libraries

### JavaScript/Node.js

```bash
npm install @neuralmarketing/sdk
```

```javascript
const NeuralMarketing = require('@neuralmarketing/sdk');

const client = new NeuralMarketing({
  apiKey: 'your_api_key_here',
  environment: 'production' // or 'sandbox'
});

// Get neural states
const states = await client.neuralStates.get();

// Update neural states
const updatedStates = await client.neuralStates.update({
  consciousness: 90.0,
  awareness: 95.0
});

// Create campaign
const campaign = await client.campaigns.create({
  name: 'My Campaign',
  type: 'awareness',
  neural_configuration: {
    consciousness: 85.0,
    empathy: 95.0
  }
});
```

### Python

```bash
pip install neural-marketing-sdk
```

```python
from neural_marketing import NeuralMarketingClient

client = NeuralMarketingClient(
    api_key='your_api_key_here',
    environment='production'
)

# Get neural states
states = client.neural_states.get()

# Update neural states
updated_states = client.neural_states.update({
    'consciousness': 90.0,
    'awareness': 95.0
})

# Create campaign
campaign = client.campaigns.create({
    'name': 'My Campaign',
    'type': 'awareness',
    'neural_configuration': {
        'consciousness': 85.0,
        'empathy': 95.0
    }
})
```

### PHP

```bash
composer require neural-marketing/sdk
```

```php
<?php
use NeuralMarketing\NeuralMarketingClient;

$client = new NeuralMarketingClient([
    'api_key' => 'your_api_key_here',
    'environment' => 'production'
]);

// Get neural states
$states = $client->neuralStates()->get();

// Update neural states
$updatedStates = $client->neuralStates()->update([
    'consciousness' => 90.0,
    'awareness' => 95.0
]);

// Create campaign
$campaign = $client->campaigns()->create([
    'name' => 'My Campaign',
    'type' => 'awareness',
    'neural_configuration' => [
        'consciousness' => 85.0,
        'empathy' => 95.0
    ]
]);
```

---

## ⚡ Rate Limits

### Rate Limit Headers

All API responses include rate limit information:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

### Rate Limit Tiers

| Plan | Requests per Minute | Requests per Hour | Requests per Day |
|------|-------------------|------------------|------------------|
| Starter | 100 | 5,000 | 50,000 |
| Professional | 500 | 25,000 | 250,000 |
| Enterprise | 2,000 | 100,000 | 1,000,000 |

### Rate Limit Exceeded

When rate limits are exceeded, the API returns:

```json
{
  "success": false,
  "errors": [
    {
      "code": "rate_limit_exceeded",
      "message": "Rate limit exceeded. Try again in 60 seconds.",
      "retry_after": 60
    }
  ]
}
```

---

## ❌ Error Handling

### Error Response Format

```json
{
  "success": false,
  "errors": [
    {
      "code": "validation_error",
      "message": "Invalid neural state value",
      "field": "consciousness",
      "details": "Value must be between 0 and 100"
    }
  ],
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `validation_error` | 400 | Invalid request data |
| `unauthorized` | 401 | Invalid or missing API key |
| `forbidden` | 403 | Insufficient permissions |
| `not_found` | 404 | Resource not found |
| `rate_limit_exceeded` | 429 | Rate limit exceeded |
| `internal_error` | 500 | Internal server error |
| `service_unavailable` | 503 | Service temporarily unavailable |

### Error Handling Best Practices

1. **Check HTTP status codes** before processing response data
2. **Handle rate limiting** with exponential backoff
3. **Implement retry logic** for transient errors
4. **Log errors** for debugging and monitoring
5. **Validate responses** before using data

### Example Error Handling

```javascript
async function makeApiRequest(endpoint, options) {
  try {
    const response = await fetch(endpoint, options);
    
    if (!response.ok) {
      if (response.status === 429) {
        // Handle rate limiting
        const retryAfter = response.headers.get('Retry-After');
        await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
        return makeApiRequest(endpoint, options);
      }
      
      const error = await response.json();
      throw new Error(error.errors[0].message);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}
```

---

## 📞 Support

### API Support

- **Documentation**: [https://docs.neuralmarketing.ai](https://docs.neuralmarketing.ai)
- **Status Page**: [https://status.neuralmarketing.ai](https://status.neuralmarketing.ai)
- **Support Email**: api-support@neuralmarketing.ai
- **Community Forum**: [https://community.neuralmarketing.ai](https://community.neuralmarketing.ai)

### SDK Support

- **GitHub**: [https://github.com/neuralmarketing/sdk](https://github.com/neuralmarketing/sdk)
- **Issues**: [https://github.com/neuralmarketing/sdk/issues](https://github.com/neuralmarketing/sdk/issues)
- **Discussions**: [https://github.com/neuralmarketing/sdk/discussions](https://github.com/neuralmarketing/sdk/discussions)

---

*This API documentation provides comprehensive coverage of the Neural Marketing Consciousness System API. For additional support or questions, contact our API support team at api-support@neuralmarketing.ai* 🧠✨

---

**Ready to integrate with our API?** [Get your API key today!](https://neuralmarketing.ai/api-keys) 🚀

