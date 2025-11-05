---
title: "Api Reference"
category: "06_documentation"
tags: []
created: "2025-10-29"
path: "06_documentation/Other/Api_docs/api_reference.md"
---

# 🔌 API Reference - IA Bulk Referral Contest System

> **Complete API Documentation for AI-Powered Referral Marketing Platform**

## 🎯 Overview

This API reference provides comprehensive documentation for all endpoints in the IA Bulk Referral Contest System. The API is built on RESTful principles with JSON responses and supports real-time updates via WebSocket connections.

## 🔐 Authentication

### API Key Authentication
```http
Authorization: Bearer <your-api-key>
```

### JWT Token Authentication
```http
Authorization: Bearer <jwt-token>
```

### Rate Limiting
- **Standard endpoints:** 100 requests per 15 minutes
- **Sensitive endpoints:** 10 requests per 15 minutes
- **Bulk operations:** 5 requests per 15 minutes

## 📊 Base URL
```
Production: https://api.iabulk.com/v1
Staging: https://staging-api.iabulk.com/v1
Development: http://localhost:8080/api/v1
```

## 🏗️ Core Endpoints

### Users API

#### Get User Profile
```http
GET /users/{userId}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "tier": "premium",
    "join_date": "2023-01-15T10:30:00Z",
    "last_login": "2023-12-01T14:22:00Z",
    "referral_count": 15,
    "engagement_score": 0.85,
    "preferences": {
      "email_frequency": "weekly",
      "preferred_time": "morning",
      "content_types": ["newsletter", "promotions"]
    },
    "metadata": {
      "industry": "technology",
      "company_size": "50-200",
      "location": "San Francisco, CA"
    }
  }
}
```

#### Update User Profile
```http
PUT /users/{userId}
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "preferences": {
    "email_frequency": "daily",
    "preferred_time": "afternoon"
  }
}
```

#### Get User Statistics
```http
GET /users/{userId}/stats
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "contests_participated": 5,
    "total_referrals": 23,
    "total_points": 1150,
    "avg_open_rate": 0.42,
    "avg_click_rate": 0.15,
    "conversion_rate": 0.08,
    "revenue_generated": 2500.00
  }
}
```

### Contests API

#### Create Contest
```http
POST /contests
```

**Request Body:**
```json
{
  "name": "Holiday Referral Contest",
  "description": "Win amazing prizes by referring friends",
  "benefit": "$500 cash prize + premium features",
  "duration": 14,
  "start_date": "2023-12-01T00:00:00Z",
  "settings": {
    "max_participants": 1000,
    "referral_limit": 10,
    "points_per_referral": 100,
    "bonus_points": {
      "first_referral": 50,
      "milestone_5": 200,
      "milestone_10": 500
    },
    "notifications": {
      "email": true,
      "sms": false,
      "push": true
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "contest": {
    "id": "contest-uuid",
    "name": "Holiday Referral Contest",
    "description": "Win amazing prizes by referring friends",
    "benefit": "$500 cash prize + premium features",
    "duration": 14,
    "start_date": "2023-12-01T00:00:00Z",
    "end_date": "2023-12-15T00:00:00Z",
    "status": "active",
    "settings": { /* contest settings */ },
    "created_at": "2023-11-25T10:00:00Z",
    "updated_at": "2023-11-25T10:00:00Z"
  }
}
```

#### Get Contest Details
```http
GET /contests/{contestId}
```

#### Update Contest
```http
PUT /contests/{contestId}
```

#### Delete Contest
```http
DELETE /contests/{contestId}
```

#### Get Contest Statistics
```http
GET /contests/{contestId}/stats
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "contest": {
      "id": "contest-uuid",
      "name": "Holiday Referral Contest",
      "status": "active",
      "total_participants": 247,
      "total_referrals": 1234,
      "total_points": 123400,
      "avg_referrals_per_participant": 5.0
    },
    "top_participants": [
      {
        "user_id": "user-uuid",
        "first_name": "Sarah",
        "last_name": "Johnson",
        "referrals_made": 15,
        "points_earned": 1500,
        "position": 1
      }
    ],
    "performance_metrics": {
      "participation_rate": 0.65,
      "referral_rate": 0.12,
      "conversion_rate": 0.08,
      "viral_coefficient": 1.2
    }
  }
}
```

### Contest Participants API

#### Add Participant
```http
POST /contests/{contestId}/participants
```

**Request Body:**
```json
{
  "user_id": "user-uuid"
}
```

**Response:**
```json
{
  "success": true,
  "participant": {
    "id": "participant-uuid",
    "contest_id": "contest-uuid",
    "user_id": "user-uuid",
    "referral_link": "https://app.iabulk.com/contest/contest-uuid/ref/user-uuid?token=abc123",
    "referrals_made": 0,
    "points_earned": 0,
    "joined_at": "2023-12-01T10:00:00Z",
    "last_activity": "2023-12-01T10:00:00Z",
    "status": "active"
  }
}
```

#### Get Contest Participants
```http
GET /contests/{contestId}/participants
```

**Query Parameters:**
- `limit` (optional): Number of results (default: 50, max: 100)
- `offset` (optional): Number of results to skip (default: 0)
- `sort` (optional): Sort field (referrals_made, points_earned, joined_at)
- `order` (optional): Sort order (asc, desc)

**Response:**
```json
{
  "success": true,
  "participants": [
    {
      "id": "participant-uuid",
      "user": {
        "id": "user-uuid",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
      },
      "referrals_made": 8,
      "points_earned": 800,
      "joined_at": "2023-12-01T10:00:00Z",
      "last_activity": "2023-12-05T14:30:00Z",
      "position": 3
    }
  ],
  "pagination": {
    "total": 247,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

#### Update Participant
```http
PUT /contests/{contestId}/participants/{participantId}
```

#### Remove Participant
```http
DELETE /contests/{contestId}/participants/{participantId}
```

### Email Campaigns API

#### Create Email Campaign
```http
POST /email-campaigns
```

**Request Body:**
```json
{
  "contest_id": "contest-uuid",
  "name": "Contest Invitation Campaign",
  "template_id": "referral-contest-invitation",
  "subject_line": "🎉 {first_name}, You're Invited to Win {benefit}!",
  "settings": {
    "personalization_level": "high",
    "send_time_optimization": true,
    "ab_testing": {
      "enabled": true,
      "variants": [
        {
          "name": "variant_a",
          "subject_line": "🎉 {first_name}, You're Invited to Win {benefit}!",
          "weight": 50
        },
        {
          "name": "variant_b",
          "subject_line": "{first_name}, Exclusive Contest - {benefit} Awaits!",
          "weight": 50
        }
      ]
    }
  }
}
```

#### Send Campaign
```http
POST /email-campaigns/{campaignId}/send
```

**Request Body:**
```json
{
  "user_ids": ["user-uuid-1", "user-uuid-2"],
  "send_immediately": false,
  "scheduled_time": "2023-12-01T10:00:00Z",
  "batch_size": 100,
  "delay_between_batches": 30
}
```

**Response:**
```json
{
  "success": true,
  "campaign": {
    "id": "campaign-uuid",
    "status": "sending",
    "total_recipients": 150,
    "sent_count": 0,
    "scheduled_time": "2023-12-01T10:00:00Z"
  },
  "results": {
    "queued": 150,
    "errors": 0,
    "estimated_completion": "2023-12-01T10:05:00Z"
  }
}
```

#### Get Campaign Statistics
```http
GET /email-campaigns/{campaignId}/stats
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "campaign": {
      "id": "campaign-uuid",
      "name": "Contest Invitation Campaign",
      "status": "completed",
      "sent_at": "2023-12-01T10:00:00Z"
    },
    "performance": {
      "total_sent": 150,
      "total_opened": 63,
      "total_clicked": 18,
      "total_converted": 12,
      "open_rate": 0.42,
      "click_rate": 0.12,
      "conversion_rate": 0.08,
      "bounce_rate": 0.02,
      "unsubscribe_rate": 0.01
    },
    "ab_test_results": {
      "variant_a": {
        "sent": 75,
        "opened": 32,
        "clicked": 10,
        "converted": 7,
        "open_rate": 0.43,
        "click_rate": 0.13,
        "conversion_rate": 0.09
      },
      "variant_b": {
        "sent": 75,
        "opened": 31,
        "clicked": 8,
        "converted": 5,
        "open_rate": 0.41,
        "click_rate": 0.11,
        "conversion_rate": 0.07
      },
      "winner": "variant_a",
      "confidence": 0.85
    }
  }
}
```

### AI Personalization API

#### Generate Personalized Content
```http
POST /ai/personalize
```

**Request Body:**
```json
{
  "user_id": "user-uuid",
  "contest_id": "contest-uuid",
  "content_type": "email",
  "template_id": "referral-contest-invitation",
  "personalization_level": "high",
  "context": {
    "campaign_type": "referral_contest",
    "urgency": "medium",
    "time_of_day": "morning"
  }
}
```

**Response:**
```json
{
  "success": true,
  "personalized_content": {
    "subject": "🎉 John, You're Invited to Win $500 Cash Prize!",
    "greeting": "Good morning John,",
    "body": "As one of our valued premium users, you're automatically invited to our exclusive referral contest...",
    "cta": "Start Referring Now",
    "personalization_data": {
      "user_tier": "premium",
      "referral_count": 15,
      "engagement_score": 0.85,
      "optimal_timing": "morning",
      "preferred_tone": "enthusiastic",
      "benefit_personalization": "Exclusive premium features + $200 cash"
    },
    "engagement_score": 0.87,
    "confidence": 0.92
  }
}
```

#### Predict User Engagement
```http
POST /ai/predict-engagement
```

**Request Body:**
```json
{
  "user_id": "user-uuid",
  "content": {
    "subject": "Contest invitation",
    "body": "Email content...",
    "cta": "Join Now"
  },
  "send_time": "2023-12-01T10:00:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "open_probability": 0.78,
    "click_probability": 0.23,
    "conversion_probability": 0.12,
    "engagement_score": 0.85,
    "confidence": 0.89,
    "recommendations": [
      {
        "type": "subject_optimization",
        "message": "Consider adding urgency to subject line",
        "expected_improvement": 0.05
      },
      {
        "type": "timing_optimization",
        "message": "Optimal send time is 2 hours later",
        "expected_improvement": 0.08
      }
    ]
  }
}
```

#### Segment Users
```http
POST /ai/segment-users
```

**Request Body:**
```json
{
  "user_ids": ["user-uuid-1", "user-uuid-2"],
  "segmentation_criteria": {
    "behavioral": true,
    "demographic": true,
    "engagement": true,
    "preferences": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "segments": {
    "power_users": {
      "count": 45,
      "criteria": "high_engagement + high_referrals",
      "users": ["user-uuid-1", "user-uuid-2"]
    },
    "new_users": {
      "count": 23,
      "criteria": "joined_last_30_days",
      "users": ["user-uuid-3"]
    },
    "inactive_users": {
      "count": 12,
      "criteria": "no_activity_30_days",
      "users": ["user-uuid-4"]
    }
  }
}
```

### Analytics API

#### Get Real-Time Analytics
```http
GET /analytics/real-time/{contestId}
```

**Response:**
```json
{
  "success": true,
  "analytics": {
    "timestamp": "2023-12-01T15:30:00Z",
    "metrics": {
      "emails_sent": 1250,
      "emails_opened": 525,
      "emails_clicked": 150,
      "referrals_generated": 89,
      "conversions": 23,
      "revenue": 11500.00
    },
    "rates": {
      "open_rate": 0.42,
      "click_rate": 0.12,
      "conversion_rate": 0.08,
      "referral_rate": 0.07
    },
    "trends": {
      "emails_sent": "increasing",
      "open_rate": "stable",
      "click_rate": "increasing",
      "conversion_rate": "increasing"
    }
  }
}
```

#### Get Performance Analytics
```http
GET /analytics/performance/{contestId}
```

**Query Parameters:**
- `start_date`: Start date (ISO 8601)
- `end_date`: End date (ISO 8601)
- `granularity`: hourly, daily, weekly, monthly
- `metrics`: Comma-separated list of metrics

**Response:**
```json
{
  "success": true,
  "analytics": {
    "period": {
      "start_date": "2023-12-01T00:00:00Z",
      "end_date": "2023-12-07T23:59:59Z",
      "granularity": "daily"
    },
    "data": [
      {
        "date": "2023-12-01",
        "emails_sent": 200,
        "emails_opened": 84,
        "emails_clicked": 24,
        "referrals_generated": 15,
        "conversions": 8,
        "revenue": 2000.00,
        "open_rate": 0.42,
        "click_rate": 0.12,
        "conversion_rate": 0.10
      }
    ],
    "summary": {
      "total_emails_sent": 1400,
      "total_emails_opened": 588,
      "total_emails_clicked": 168,
      "total_referrals_generated": 105,
      "total_conversions": 56,
      "total_revenue": 14000.00,
      "avg_open_rate": 0.42,
      "avg_click_rate": 0.12,
      "avg_conversion_rate": 0.10
    }
  }
}
```

#### Get User Analytics
```http
GET /analytics/users/{userId}
```

**Response:**
```json
{
  "success": true,
  "analytics": {
    "user_id": "user-uuid",
    "period": "last_30_days",
    "engagement": {
      "emails_received": 12,
      "emails_opened": 8,
      "emails_clicked": 3,
      "open_rate": 0.67,
      "click_rate": 0.25,
      "avg_time_to_open": "2.5 hours",
      "avg_time_to_click": "15 minutes"
    },
    "referral_activity": {
      "referrals_made": 5,
      "referrals_converted": 3,
      "conversion_rate": 0.60,
      "revenue_generated": 750.00
    },
    "behavioral_insights": {
      "preferred_send_time": "10:00 AM",
      "preferred_day": "Tuesday",
      "engagement_trend": "increasing",
      "churn_risk": "low"
    }
  }
}
```

### Webhooks API

#### Register Webhook
```http
POST /webhooks
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhooks/iabulk",
  "events": [
    "email.sent",
    "email.opened",
    "email.clicked",
    "referral.created",
    "referral.converted",
    "contest.completed"
  ],
  "secret": "your-webhook-secret",
  "active": true
}
```

#### Webhook Events

**Email Sent Event:**
```json
{
  "event": "email.sent",
  "timestamp": "2023-12-01T10:00:00Z",
  "data": {
    "email_id": "email-uuid",
    "campaign_id": "campaign-uuid",
    "user_id": "user-uuid",
    "contest_id": "contest-uuid",
    "recipient": "user@example.com",
    "subject": "Contest invitation",
    "sent_at": "2023-12-01T10:00:00Z"
  }
}
```

**Email Opened Event:**
```json
{
  "event": "email.opened",
  "timestamp": "2023-12-01T10:15:00Z",
  "data": {
    "email_id": "email-uuid",
    "user_id": "user-uuid",
    "opened_at": "2023-12-01T10:15:00Z",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "location": {
      "country": "US",
      "city": "San Francisco"
    }
  }
}
```

**Referral Created Event:**
```json
{
  "event": "referral.created",
  "timestamp": "2023-12-01T11:00:00Z",
  "data": {
    "referral_id": "referral-uuid",
    "referrer_id": "user-uuid",
    "contest_id": "contest-uuid",
    "referral_link": "https://app.iabulk.com/ref/abc123",
    "created_at": "2023-12-01T11:00:00Z"
  }
}
```

## 🔧 SDKs and Libraries

### JavaScript SDK
```javascript
import { IABulkClient } from '@iabulk/sdk';

const client = new IABulkClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.iabulk.com/v1'
});

// Create contest
const contest = await client.contests.create({
  name: 'Holiday Contest',
  benefit: '$500 prize',
  duration: 14
});

// Send personalized email
const email = await client.emails.send({
  campaignId: 'campaign-uuid',
  userIds: ['user-uuid-1', 'user-uuid-2']
});
```

### Python SDK
```python
from iabulk import IABulkClient

client = IABulkClient(
    api_key='your-api-key',
    base_url='https://api.iabulk.com/v1'
)

# Create contest
contest = client.contests.create({
    'name': 'Holiday Contest',
    'benefit': '$500 prize',
    'duration': 14
})

# Get analytics
analytics = client.analytics.get_performance(
    contest_id='contest-uuid',
    start_date='2023-12-01',
    end_date='2023-12-07'
)
```

### PHP SDK
```php
<?php
use IABulk\IABulkClient;

$client = new IABulkClient([
    'api_key' => 'your-api-key',
    'base_url' => 'https://api.iabulk.com/v1'
]);

// Create contest
$contest = $client->contests->create([
    'name' => 'Holiday Contest',
    'benefit' => '$500 prize',
    'duration' => 14
]);

// Get real-time analytics
$analytics = $client->analytics->getRealTime('contest-uuid');
?>
```

## 🚨 Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    },
    "request_id": "req-uuid",
    "timestamp": "2023-12-01T10:00:00Z"
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Invalid request parameters
- `AUTHENTICATION_ERROR`: Invalid or missing API key
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `INTERNAL_SERVER_ERROR`: Server error

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1701432000
```

## 📊 Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

## 🔄 Pagination

### Request Format
```http
GET /contests/{contestId}/participants?limit=50&offset=100
```

### Response Format
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "total": 1000,
    "limit": 50,
    "offset": 100,
    "has_more": true,
    "next_url": "/contests/contest-uuid/participants?limit=50&offset=150"
  }
}
```

## 📝 Changelog

### Version 1.2.0 (2023-12-01)
- Added AI personalization endpoints
- Enhanced analytics with real-time data
- Improved webhook system
- Added batch operations support

### Version 1.1.0 (2023-11-15)
- Added contest statistics endpoints
- Enhanced email campaign management
- Improved error handling
- Added rate limiting

### Version 1.0.0 (2023-11-01)
- Initial API release
- Core contest management
- Basic email functionality
- User management

---

**🔌 This API reference is part of the IA Bulk Platform. For more information, visit our [Complete Documentation](./README.md) or [Enroll in the AI Marketing Mastery Course](../AI_Marketing_Course_Curriculum.md).**
