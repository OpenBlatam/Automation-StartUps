# API Documentation - AI Testimonial SaaS Platform

## Overview

The AI Testimonial SaaS Platform provides a comprehensive REST API for generating, managing, and analyzing AI-powered testimonials. This API supports multiple AI models, batch processing, and advanced analytics.

**Base URL**: `https://api.aitestimonial.com/v1`  
**Authentication**: Bearer Token (JWT)  
**Rate Limiting**: 100 requests per 15 minutes per IP

## Authentication

### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123",
  "firstName": "John",
  "lastName": "Doe",
  "company": "Acme Corp"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "64f1a2b3c4d5e6f7g8h9i0j1",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "subscription": {
        "plan": "starter",
        "status": "active"
      }
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

### Refresh Token
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Testimonials API

### Generate Single Testimonial

```http
POST /api/testimonials/generate
Authorization: Bearer {token}
Content-Type: application/json

{
  "templateType": "distinctiveQualities",
  "productName": "AI Marketing Platform",
  "productCategory": "SaaS",
  "targetAudience": "Marketing professionals",
  "keyBenefits": ["Increased efficiency", "Better ROI", "Time savings"],
  "useCase": "Streamlining marketing campaigns",
  "industry": "Technology",
  "tone": "professional",
  "length": "medium",
  "model": "gpt-4",
  "additionalContext": "Focus on enterprise features"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "test_64f1a2b3c4d5e6f7g8h9i0j1",
    "templateType": "distinctiveQualities",
    "productName": "AI Marketing Platform",
    "content": "As a marketing professional with over 10 years of experience, I can confidently say that the AI Marketing Platform has revolutionized how we approach campaign management. The distinctive qualities that set this platform apart include its intuitive interface, advanced automation capabilities, and unparalleled ROI tracking. What truly makes it an unparalleled solution in the commerce industry is its ability to predict customer behavior with 95% accuracy, resulting in a 40% increase in our conversion rates. The platform's seamless integration with existing tools and real-time analytics have transformed our marketing strategy from reactive to proactive. I wholeheartedly recommend this platform to any business serious about scaling their marketing efforts efficiently.",
    "alternatives": [
      "The AI Marketing Platform stands out in the crowded SaaS market through its innovative approach to customer segmentation and predictive analytics...",
      "Having tested numerous marketing platforms over the years, the AI Marketing Platform's unique value proposition lies in its machine learning capabilities..."
    ],
    "metadata": {
      "prompt": "Could you kindly produce a testimonial regarding the distinctive qualities that set AI Marketing Platform apart as an unparalleled solution within the realm of the commerce industry?",
      "tokensUsed": 245,
      "generationTime": 1250,
      "qualityScore": 87
    },
    "status": "generated",
    "createdAt": "2024-01-15T10:30:00Z"
  },
  "usage": {
    "remaining": 99,
    "resetDate": "2024-02-01T00:00:00Z"
  }
}
```

### Generate Batch Testimonials

```http
POST /api/testimonials/generate-batch
Authorization: Bearer {token}
Content-Type: application/json

{
  "requests": [
    {
      "templateType": "recommendation",
      "productName": "Product A",
      "productCategory": "Software",
      "targetAudience": "Developers",
      "tone": "technical",
      "length": "short"
    },
    {
      "templateType": "efficiencyImprovement",
      "productName": "Product B",
      "productCategory": "Tool",
      "targetAudience": "Business owners",
      "tone": "professional",
      "length": "medium"
    }
  ],
  "options": {
    "model": "gpt-4",
    "parallel": true
  }
}
```

### Get User Testimonials

```http
GET /api/testimonials?page=1&limit=10&category=distinctiveQualities&status=generated
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "testimonials": [
      {
        "id": "test_64f1a2b3c4d5e6f7g8h9i0j1",
        "templateType": "distinctiveQualities",
        "productName": "AI Marketing Platform",
        "content": "As a marketing professional...",
        "status": "generated",
        "createdAt": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 25,
    "page": 1,
    "limit": 10,
    "totalPages": 3
  }
}
```

### Get Specific Testimonial

```http
GET /api/testimonials/{id}
Authorization: Bearer {token}
```

### Update Testimonial

```http
PUT /api/testimonials/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "approved",
  "notes": "Great testimonial, ready for publication",
  "tags": ["marketing", "saas", "enterprise"]
}
```

### Regenerate Testimonial

```http
POST /api/testimonials/{id}/regenerate
Authorization: Bearer {token}
Content-Type: application/json

{
  "model": "claude-3",
  "options": {
    "tone": "casual",
    "length": "long"
  }
}
```

### Delete Testimonial

```http
DELETE /api/testimonials/{id}
Authorization: Bearer {token}
```

### Export Testimonials

```http
POST /api/testimonials/export
Authorization: Bearer {token}
Content-Type: application/json

{
  "format": "csv",
  "filters": {
    "status": "approved",
    "templateType": "recommendation"
  }
}
```

## Analytics API

### Get Overview Analytics

```http
GET /api/analytics/overview?period=30d
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "totalGenerated": 45,
    "avgQualityScore": 82.5,
    "totalTokensUsed": 11250,
    "avgGenerationTime": 1180,
    "byTemplate": [
      {
        "template": "distinctiveQualities",
        "count": 15,
        "avgQuality": 85.2
      },
      {
        "template": "recommendation",
        "count": 12,
        "avgQuality": 79.8
      }
    ],
    "byModel": [
      {
        "model": "gpt-4",
        "count": 30,
        "avgTokens": 250
      },
      {
        "model": "claude-3",
        "count": 15,
        "avgTokens": 280
      }
    ],
    "performance": {
      "views": 1250,
      "clicks": 89,
      "conversions": 12,
      "clickThroughRate": "7.12%",
      "conversionRate": "13.48%"
    }
  }
}
```

### Get Testimonial Performance

```http
GET /api/analytics/testimonials/{id}/performance
Authorization: Bearer {token}
```

## Templates API

### Get Available Templates

```http
GET /api/templates
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "distinctiveQualities",
      "name": "Distinctive Qualities",
      "description": "Highlight unique value propositions",
      "prompt": "Could you kindly produce a testimonial regarding the distinctive qualities that set {product/service} apart as an unparalleled solution within the realm of the commerce industry?",
      "category": "Product Differentiation",
      "useCase": "Highlighting unique value propositions",
      "variables": ["product/service", "industry", "target_audience"]
    }
  ]
}
```

### Create Custom Template

```http
POST /api/templates
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Custom Template",
  "description": "Custom testimonial template",
  "prompt": "Create a testimonial for {product} that emphasizes {benefit}",
  "category": "Custom",
  "variables": ["product", "benefit"]
}
```

## Billing API

### Get Subscription Info

```http
GET /api/billing/subscription
Authorization: Bearer {token}
```

### Update Subscription

```http
PUT /api/billing/subscription
Authorization: Bearer {token}
Content-Type: application/json

{
  "plan": "professional"
}
```

### Get Usage

```http
GET /api/billing/usage
Authorization: Bearer {token}
```

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": "Validation Error",
  "message": "Product name is required",
  "details": {
    "field": "productName",
    "code": "REQUIRED"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "requestId": "req_64f1a2b3c4d5e6f7g8h9i0j1"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Rate Limited
- `500` - Internal Server Error

### Common Error Codes

- `VALIDATION_ERROR` - Input validation failed
- `AUTHENTICATION_REQUIRED` - Valid token required
- `INSUFFICIENT_PERMISSIONS` - User lacks required permissions
- `PLAN_LIMIT_EXCEEDED` - Subscription plan limit reached
- `AI_GENERATION_FAILED` - AI model generation failed
- `RATE_LIMIT_EXCEEDED` - Too many requests

## Rate Limiting

- **Free Plan**: 10 requests per hour
- **Starter Plan**: 100 requests per 15 minutes
- **Professional Plan**: 500 requests per 15 minutes
- **Enterprise Plan**: 1000 requests per 15 minutes

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

## Webhooks

### Testimonial Generated Webhook

```http
POST {your_webhook_url}
Content-Type: application/json
X-Webhook-Signature: sha256=...

{
  "event": "testimonial.generated",
  "data": {
    "id": "test_64f1a2b3c4d5e6f7g8h9i0j1",
    "userId": "user_64f1a2b3c4d5e6f7g8h9i0j1",
    "templateType": "distinctiveQualities",
    "status": "generated"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Available Webhook Events

- `testimonial.generated`
- `testimonial.updated`
- `testimonial.deleted`
- `subscription.updated`
- `usage.limit_warning`
- `usage.limit_exceeded`

## SDKs and Libraries

### JavaScript/Node.js

```bash
npm install @aitestimonial/sdk
```

```javascript
import { TestimonialClient } from '@aitestimonial/sdk';

const client = new TestimonialClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.aitestimonial.com/v1'
});

const testimonial = await client.testimonials.generate({
  templateType: 'distinctiveQualities',
  productName: 'AI Platform',
  tone: 'professional'
});
```

### Python

```bash
pip install aitestimonial-sdk
```

```python
from aitestimonial import TestimonialClient

client = TestimonialClient(api_key='your_api_key')

testimonial = client.testimonials.generate(
    template_type='distinctiveQualities',
    product_name='AI Platform',
    tone='professional'
)
```

### PHP

```bash
composer require aitestimonial/sdk
```

```php
use AITestimonial\TestimonialClient;

$client = new TestimonialClient('your_api_key');

$testimonial = $client->testimonials->generate([
    'templateType' => 'distinctiveQualities',
    'productName' => 'AI Platform',
    'tone' => 'professional'
]);
```

## Testing

### Test API Key

Use the test API key for development:
```
test_sk_64f1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7
```

### Postman Collection

Download our Postman collection: [AI Testimonial API Collection](https://api.aitestimonial.com/postman/collection.json)

### API Testing Tool

Use our interactive API testing tool: [API Explorer](https://api.aitestimonial.com/explorer)

## Support

- **Documentation**: [docs.aitestimonial.com](https://docs.aitestimonial.com)
- **API Status**: [status.aitestimonial.com](https://status.aitestimonial.com)
- **Support Email**: api-support@aitestimonial.com
- **Discord**: [Join our developer community](https://discord.gg/aitestimonial)



