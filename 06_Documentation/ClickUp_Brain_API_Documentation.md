# ClickUp Brain API Documentation
## Complete Technical Integration Guide

---

## 📋 API Overview

The ClickUp Brain API provides comprehensive programmatic access to all ClickUp Brain functionality, enabling seamless integration with existing systems and custom application development. This documentation covers all API endpoints, authentication, data models, and integration patterns.

---

## 🔐 Authentication & Security

### Authentication Methods

#### API Key Authentication
```http
GET /api/v1/endpoint
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

#### OAuth 2.0 Authentication
```http
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&
client_id=YOUR_CLIENT_ID&
client_secret=YOUR_CLIENT_SECRET&
scope=read write
```

#### JWT Token Authentication
```http
GET /api/v1/endpoint
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Security Best Practices
- **HTTPS Only:** All API calls must use HTTPS
- **Rate Limiting:** 1000 requests per hour per API key
- **IP Whitelisting:** Restrict API access to specific IP addresses
- **Token Rotation:** Rotate API keys every 90 days
- **Audit Logging:** All API calls are logged for security monitoring

---

## 📊 Core API Endpoints

### 1. Legal Compliance API

#### Document Processing
```http
POST /api/v1/compliance/documents
Content-Type: multipart/form-data

{
  "file": "document.pdf",
  "jurisdiction": "US",
  "document_type": "regulation",
  "metadata": {
    "source": "SEC",
    "date": "2024-01-15",
    "category": "financial"
  }
}
```

**Response:**
```json
{
  "document_id": "doc_123456",
  "status": "processed",
  "extracted_data": {
    "deadlines": ["2024-12-31"],
    "requirements": ["GDPR compliance", "Data protection"],
    "penalties": ["$50,000", "$100,000"],
    "entities": ["Company", "Customer", "Data"]
  },
  "compliance_score": 0.85,
  "risk_level": "medium",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Compliance Monitoring
```http
GET /api/v1/compliance/monitoring
Authorization: Bearer YOUR_API_KEY

{
  "jurisdiction": "EU",
  "status": "active",
  "risk_level": "high",
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  }
}
```

**Response:**
```json
{
  "compliance_items": [
    {
      "id": "comp_123",
      "title": "GDPR Data Processing",
      "deadline": "2024-06-30",
      "status": "pending",
      "risk_level": "high",
      "jurisdiction": "EU",
      "requirements": ["Data protection", "Consent management"],
      "penalties": ["€20M or 4% of revenue"]
    }
  ],
  "total_count": 15,
  "high_risk_count": 3,
  "overdue_count": 1
}
```

#### Regulatory Updates
```http
GET /api/v1/compliance/updates
Authorization: Bearer YOUR_API_KEY

{
  "jurisdiction": "US",
  "update_type": "new_regulation",
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  }
}
```

**Response:**
```json
{
  "updates": [
    {
      "id": "update_456",
      "title": "New SEC Disclosure Requirements",
      "date": "2024-01-15",
      "jurisdiction": "US",
      "impact_level": "high",
      "summary": "New requirements for financial disclosures",
      "affected_industries": ["finance", "technology"],
      "deadline": "2024-07-01",
      "source": "SEC.gov"
    }
  ],
  "total_count": 5,
  "high_impact_count": 2
}
```

### 2. Marketing Optimization API

#### Campaign Analysis
```http
POST /api/v1/marketing/campaigns/analyze
Content-Type: application/json

{
  "campaign_id": "camp_789",
  "platform": "google_ads",
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "metrics": ["impressions", "clicks", "conversions", "cost"]
}
```

**Response:**
```json
{
  "campaign_id": "camp_789",
  "analysis": {
    "performance_score": 0.75,
    "roi": 2.8,
    "conversion_rate": 0.045,
    "cost_per_conversion": 25.50,
    "recommendations": [
      {
        "type": "budget_optimization",
        "description": "Increase budget by 20% for high-performing keywords",
        "expected_impact": "15% increase in conversions"
      },
      {
        "type": "targeting_optimization",
        "description": "Expand targeting to similar audiences",
        "expected_impact": "25% increase in reach"
      }
    ]
  },
  "regional_analysis": {
    "US": {"performance": 0.85, "recommendations": 3},
    "EU": {"performance": 0.65, "recommendations": 5},
    "APAC": {"performance": 0.70, "recommendations": 4}
  }
}
```

#### Localization Optimization
```http
POST /api/v1/marketing/localization/optimize
Content-Type: application/json

{
  "content": "Buy now for 50% off!",
  "target_markets": ["DE", "FR", "ES"],
  "campaign_type": "ecommerce",
  "brand_voice": "friendly"
}
```

**Response:**
```json
{
  "localized_content": {
    "DE": {
      "translation": "Jetzt kaufen mit 50% Rabatt!",
      "cultural_adaptations": {
        "color_preferences": ["blue", "white"],
        "seasonal_context": "winter_sales",
        "payment_preferences": ["credit_card", "paypal"]
      },
      "performance_prediction": 0.82
    },
    "FR": {
      "translation": "Achetez maintenant avec 50% de réduction !",
      "cultural_adaptations": {
        "color_preferences": ["blue", "red", "white"],
        "seasonal_context": "soldes_hiver",
        "payment_preferences": ["carte_bancaire", "paypal"]
      },
      "performance_prediction": 0.78
    },
    "ES": {
      "translation": "¡Compra ahora con 50% de descuento!",
      "cultural_adaptations": {
        "color_preferences": ["red", "yellow"],
        "seasonal_context": "rebajas_invierno",
        "payment_preferences": ["tarjeta_credito", "paypal"]
      },
      "performance_prediction": 0.80
    }
  }
}
```

#### Budget Optimization
```http
POST /api/v1/marketing/budget/optimize
Content-Type: application/json

{
  "total_budget": 100000,
  "campaigns": [
    {
      "id": "camp_1",
      "current_budget": 30000,
      "performance": 0.85,
      "roi": 3.2
    },
    {
      "id": "camp_2",
      "current_budget": 40000,
      "performance": 0.65,
      "roi": 2.1
    },
    {
      "id": "camp_3",
      "current_budget": 30000,
      "performance": 0.90,
      "roi": 4.1
    }
  ]
}
```

**Response:**
```json
{
  "optimized_allocation": {
    "camp_1": {
      "recommended_budget": 35000,
      "change": "+5000",
      "expected_roi": 3.4,
      "reasoning": "High performance, room for growth"
    },
    "camp_2": {
      "recommended_budget": 25000,
      "change": "-15000",
      "expected_roi": 2.3,
      "reasoning": "Lower performance, reallocate budget"
    },
    "camp_3": {
      "recommended_budget": 40000,
      "change": "+10000",
      "expected_roi": 4.3,
      "reasoning": "Highest ROI, maximize investment"
    }
  },
  "expected_total_roi": 3.2,
  "roi_improvement": 0.3
}
```

### 3. User Feedback API

#### Feedback Collection
```http
POST /api/v1/feedback/collect
Content-Type: application/json

{
  "source": "app_store",
  "content": "Great app but needs dark mode",
  "user_id": "user_123",
  "metadata": {
    "rating": 4,
    "version": "2.1.0",
    "platform": "ios",
    "language": "en"
  }
}
```

**Response:**
```json
{
  "feedback_id": "fb_456",
  "status": "processed",
  "analysis": {
    "sentiment": "positive",
    "sentiment_score": 0.75,
    "category": "feature_request",
    "priority": "medium",
    "themes": ["dark_mode", "ui_improvement"],
    "entities": ["app", "dark_mode", "user_interface"]
  },
  "recommendations": [
    {
      "action": "add_to_roadmap",
      "priority": "medium",
      "estimated_effort": "2 weeks",
      "expected_impact": "high"
    }
  ],
  "created_at": "2024-01-15T14:30:00Z"
}
```

#### Feedback Analysis
```http
GET /api/v1/feedback/analysis
Authorization: Bearer YOUR_API_KEY

{
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "sources": ["app_store", "support_tickets", "surveys"],
  "group_by": "category"
}
```

**Response:**
```json
{
  "analysis_summary": {
    "total_feedback": 1250,
    "sentiment_distribution": {
      "positive": 0.65,
      "neutral": 0.25,
      "negative": 0.10
    },
    "top_themes": [
      {"theme": "performance", "count": 180, "sentiment": 0.45},
      {"theme": "user_interface", "count": 150, "sentiment": 0.70},
      {"theme": "features", "count": 120, "sentiment": 0.80}
    ],
    "priority_distribution": {
      "high": 0.15,
      "medium": 0.45,
      "low": 0.40
    }
  },
  "category_analysis": {
    "bug_reports": {
      "count": 200,
      "avg_priority": "high",
      "top_issues": ["crash", "slow_loading", "login_error"]
    },
    "feature_requests": {
      "count": 300,
      "avg_priority": "medium",
      "top_requests": ["dark_mode", "offline_sync", "export_data"]
    },
    "general_feedback": {
      "count": 750,
      "avg_sentiment": 0.75,
      "top_themes": ["ease_of_use", "design", "functionality"]
    }
  }
}
```

#### Churn Prediction
```http
POST /api/v1/feedback/churn/predict
Content-Type: application/json

{
  "user_id": "user_123",
  "user_data": {
    "signup_date": "2023-06-15",
    "last_login": "2024-01-10",
    "feature_usage": {
      "core_features": 0.85,
      "advanced_features": 0.25,
      "support_usage": 0.10
    },
    "feedback_history": {
      "total_feedback": 5,
      "negative_feedback": 2,
      "recent_sentiment": 0.40
    }
  }
}
```

**Response:**
```json
{
  "user_id": "user_123",
  "churn_probability": 0.75,
  "risk_level": "high",
  "risk_factors": [
    {
      "factor": "low_feature_usage",
      "impact": 0.30,
      "description": "User not utilizing advanced features"
    },
    {
      "factor": "negative_feedback",
      "impact": 0.25,
      "description": "Recent negative feedback indicates dissatisfaction"
    },
    {
      "factor": "inactive_period",
      "impact": 0.20,
      "description": "User has been inactive for extended period"
    }
  ],
  "recommendations": [
    {
      "action": "personalized_onboarding",
      "description": "Send personalized tutorial for advanced features",
      "expected_impact": "Reduce churn probability by 15%"
    },
    {
      "action": "proactive_support",
      "description": "Reach out to address recent negative feedback",
      "expected_impact": "Reduce churn probability by 20%"
    }
  ]
}
```

---

## 🔧 Advanced API Features

### 1. Webhooks

#### Webhook Configuration
```http
POST /api/v1/webhooks
Content-Type: application/json

{
  "url": "https://your-app.com/webhooks/clickup-brain",
  "events": [
    "compliance.alert",
    "marketing.optimization",
    "feedback.analysis"
  ],
  "secret": "your_webhook_secret"
}
```

#### Webhook Payload Example
```json
{
  "event": "compliance.alert",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "alert_id": "alert_789",
    "type": "deadline_approaching",
    "severity": "high",
    "compliance_item": {
      "id": "comp_123",
      "title": "GDPR Data Processing",
      "deadline": "2024-06-30",
      "jurisdiction": "EU"
    }
  }
}
```

### 2. Batch Operations

#### Batch Document Processing
```http
POST /api/v1/compliance/documents/batch
Content-Type: application/json

{
  "documents": [
    {
      "file_url": "https://example.com/doc1.pdf",
      "jurisdiction": "US",
      "document_type": "regulation"
    },
    {
      "file_url": "https://example.com/doc2.pdf",
      "jurisdiction": "EU",
      "document_type": "policy"
    }
  ],
  "callback_url": "https://your-app.com/batch-complete"
}
```

#### Batch Feedback Processing
```http
POST /api/v1/feedback/batch
Content-Type: application/json

{
  "feedback_items": [
    {
      "source": "app_store",
      "content": "Great app!",
      "user_id": "user_1"
    },
    {
      "source": "support",
      "content": "Need help with login",
      "user_id": "user_2"
    }
  ]
}
```

### 3. Real-time Streaming

#### WebSocket Connection
```javascript
const ws = new WebSocket('wss://api.clickup-brain.com/v1/stream');

ws.onopen = function() {
  // Subscribe to real-time updates
  ws.send(JSON.stringify({
    action: 'subscribe',
    channels: ['compliance.alerts', 'marketing.updates', 'feedback.analysis']
  }));
};

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};
```

#### Server-Sent Events
```http
GET /api/v1/stream/events
Authorization: Bearer YOUR_API_KEY
Accept: text/event-stream

data: {"event": "compliance.alert", "data": {...}}

data: {"event": "marketing.optimization", "data": {...}}
```

---

## 📊 Data Models & Schemas

### 1. Compliance Data Models

#### Document Schema
```json
{
  "document_id": "string",
  "title": "string",
  "content": "string",
  "jurisdiction": "string",
  "document_type": "enum[regulation, policy, guideline]",
  "metadata": {
    "source": "string",
    "date": "datetime",
    "category": "string",
    "version": "string"
  },
  "extracted_data": {
    "deadlines": ["datetime"],
    "requirements": ["string"],
    "penalties": ["string"],
    "entities": ["string"]
  },
  "compliance_score": "float",
  "risk_level": "enum[low, medium, high, critical]",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Compliance Item Schema
```json
{
  "compliance_id": "string",
  "title": "string",
  "description": "string",
  "jurisdiction": "string",
  "deadline": "datetime",
  "status": "enum[pending, in_progress, completed, overdue]",
  "risk_level": "enum[low, medium, high, critical]",
  "requirements": ["string"],
  "penalties": ["string"],
  "assigned_to": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### 2. Marketing Data Models

#### Campaign Schema
```json
{
  "campaign_id": "string",
  "name": "string",
  "platform": "string",
  "status": "enum[active, paused, completed]",
  "budget": {
    "total": "float",
    "spent": "float",
    "remaining": "float"
  },
  "performance": {
    "impressions": "integer",
    "clicks": "integer",
    "conversions": "integer",
    "cost": "float",
    "roi": "float"
  },
  "targeting": {
    "audiences": ["string"],
    "locations": ["string"],
    "demographics": "object"
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Localization Schema
```json
{
  "localization_id": "string",
  "original_content": "string",
  "target_market": "string",
  "language": "string",
  "localized_content": "string",
  "cultural_adaptations": {
    "color_preferences": ["string"],
    "seasonal_context": "string",
    "payment_preferences": ["string"],
    "cultural_taboos": ["string"]
  },
  "performance_prediction": "float",
  "created_at": "datetime"
}
```

### 3. Feedback Data Models

#### Feedback Schema
```json
{
  "feedback_id": "string",
  "source": "enum[app_store, support, survey, social]",
  "content": "string",
  "user_id": "string",
  "metadata": {
    "rating": "integer",
    "version": "string",
    "platform": "string",
    "language": "string"
  },
  "analysis": {
    "sentiment": "enum[positive, neutral, negative]",
    "sentiment_score": "float",
    "category": "enum[bug_report, feature_request, general]",
    "priority": "enum[low, medium, high, critical]",
    "themes": ["string"],
    "entities": ["string"]
  },
  "created_at": "datetime"
}
```

#### User Schema
```json
{
  "user_id": "string",
  "signup_date": "datetime",
  "last_login": "datetime",
  "feature_usage": {
    "core_features": "float",
    "advanced_features": "float",
    "support_usage": "float"
  },
  "feedback_history": {
    "total_feedback": "integer",
    "positive_feedback": "integer",
    "negative_feedback": "integer",
    "recent_sentiment": "float"
  },
  "churn_risk": {
    "probability": "float",
    "risk_level": "enum[low, medium, high, critical]",
    "risk_factors": ["string"]
  }
}
```

---

## 🚀 SDKs & Libraries

### 1. JavaScript/Node.js SDK

#### Installation
```bash
npm install @clickup-brain/sdk
```

#### Usage Example
```javascript
const ClickUpBrain = require('@clickup-brain/sdk');

const client = new ClickUpBrain({
  apiKey: 'your-api-key',
  environment: 'production'
});

// Process compliance document
const document = await client.compliance.documents.process({
  file: 'path/to/document.pdf',
  jurisdiction: 'US',
  documentType: 'regulation'
});

// Analyze marketing campaign
const analysis = await client.marketing.campaigns.analyze({
  campaignId: 'camp_123',
  platform: 'google_ads',
  dateRange: {
    start: '2024-01-01',
    end: '2024-01-31'
  }
});

// Process user feedback
const feedback = await client.feedback.process({
  source: 'app_store',
  content: 'Great app!',
  userId: 'user_123'
});
```

### 2. Python SDK

#### Installation
```bash
pip install clickup-brain-sdk
```

#### Usage Example
```python
from clickup_brain import ClickUpBrain

client = ClickUpBrain(
    api_key='your-api-key',
    environment='production'
)

# Process compliance document
document = client.compliance.documents.process(
    file_path='document.pdf',
    jurisdiction='US',
    document_type='regulation'
)

# Analyze marketing campaign
analysis = client.marketing.campaigns.analyze(
    campaign_id='camp_123',
    platform='google_ads',
    date_range={
        'start': '2024-01-01',
        'end': '2024-01-31'
    }
)

# Process user feedback
feedback = client.feedback.process(
    source='app_store',
    content='Great app!',
    user_id='user_123'
)
```

### 3. Java SDK

#### Installation
```xml
<dependency>
    <groupId>com.clickup.brain</groupId>
    <artifactId>clickup-brain-sdk</artifactId>
    <version>1.0.0</version>
</dependency>
```

#### Usage Example
```java
import com.clickup.brain.ClickUpBrain;
import com.clickup.brain.models.*;

ClickUpBrain client = new ClickUpBrain.Builder()
    .apiKey("your-api-key")
    .environment("production")
    .build();

// Process compliance document
DocumentRequest request = DocumentRequest.builder()
    .filePath("document.pdf")
    .jurisdiction("US")
    .documentType("regulation")
    .build();

DocumentResponse document = client.compliance().documents().process(request);

// Analyze marketing campaign
CampaignAnalysisRequest analysisRequest = CampaignAnalysisRequest.builder()
    .campaignId("camp_123")
    .platform("google_ads")
    .dateRange(DateRange.builder()
        .start("2024-01-01")
        .end("2024-01-31")
        .build())
    .build();

CampaignAnalysis analysis = client.marketing().campaigns().analyze(analysisRequest);
```

---

## 🔧 Integration Examples

### 1. CRM Integration

#### Salesforce Integration
```javascript
// Salesforce Apex Class
public class ClickUpBrainIntegration {
    @AuraEnabled
    public static String processComplianceDocument(String documentId) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint('https://api.clickup-brain.com/v1/compliance/documents');
        req.setMethod('POST');
        req.setHeader('Authorization', 'Bearer ' + getApiKey());
        req.setHeader('Content-Type', 'application/json');
        
        String body = JSON.serialize(new Map<String, Object>{
            'document_id' => documentId,
            'jurisdiction' => 'US',
            'document_type' => 'regulation'
        });
        req.setBody(body);
        
        Http http = new Http();
        HttpResponse res = http.send(req);
        
        return res.getBody();
    }
}
```

### 2. Marketing Platform Integration

#### Google Ads Integration
```python
from google.ads.googleads.client import GoogleAdsClient
from clickup_brain import ClickUpBrain

def optimize_google_ads_campaigns():
    # Initialize Google Ads client
    google_ads_client = GoogleAdsClient.load_from_storage()
    
    # Initialize ClickUp Brain client
    clickup_client = ClickUpBrain(api_key='your-api-key')
    
    # Get campaign data from Google Ads
    campaigns = get_google_ads_campaigns(google_ads_client)
    
    # Analyze campaigns with ClickUp Brain
    for campaign in campaigns:
        analysis = clickup_client.marketing.campaigns.analyze({
            'campaign_id': campaign.id,
            'platform': 'google_ads',
            'performance_data': campaign.performance
        })
        
        # Apply optimizations
        if analysis.recommendations:
            apply_optimizations(google_ads_client, campaign.id, analysis.recommendations)
```

### 3. Support System Integration

#### Zendesk Integration
```javascript
// Zendesk App
(function() {
    return {
        events: {
            'app.activated': function() {
                // Initialize ClickUp Brain client
                this.clickupBrain = new ClickUpBrain({
                    apiKey: this.setting('api_key')
                });
            },
            
            'ticket.created': function(data) {
                // Process ticket with ClickUp Brain
                this.clickupBrain.feedback.process({
                    source: 'support',
                    content: data.ticket.description,
                    userId: data.ticket.requester_id,
                    metadata: {
                        ticket_id: data.ticket.id,
                        priority: data.ticket.priority
                    }
                }).then(response => {
                    // Update ticket with analysis
                    this.ajax('updateTicket', {
                        ticketId: data.ticket.id,
                        analysis: response.analysis
                    });
                });
            }
        }
    };
})();
```

---

## 📊 Rate Limits & Quotas

### Rate Limiting

#### Standard Limits
- **API Requests:** 1,000 requests per hour per API key
- **Document Processing:** 100 documents per hour
- **Feedback Processing:** 500 feedback items per hour
- **Campaign Analysis:** 50 campaigns per hour

#### Burst Limits
- **Short Burst:** 200 requests per minute
- **Document Processing:** 20 documents per minute
- **Feedback Processing:** 100 feedback items per minute

#### Quota Management
```http
GET /api/v1/quotas
Authorization: Bearer YOUR_API_KEY
```

**Response:**
```json
{
  "api_requests": {
    "limit": 1000,
    "used": 250,
    "remaining": 750,
    "reset_time": "2024-01-15T11:00:00Z"
  },
  "document_processing": {
    "limit": 100,
    "used": 15,
    "remaining": 85,
    "reset_time": "2024-01-15T11:00:00Z"
  }
}
```

---

## 🚨 Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "details": {
      "limit": 1000,
      "used": 1000,
      "reset_time": "2024-01-15T11:00:00Z"
    },
    "request_id": "req_123456"
  }
}
```

### Common Error Codes
- **400 Bad Request:** Invalid request parameters
- **401 Unauthorized:** Invalid or missing API key
- **403 Forbidden:** Insufficient permissions
- **404 Not Found:** Resource not found
- **429 Too Many Requests:** Rate limit exceeded
- **500 Internal Server Error:** Server error
- **503 Service Unavailable:** Service temporarily unavailable

### Retry Logic
```javascript
async function makeRequestWithRetry(url, options, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(url, options);
            
            if (response.status === 429) {
                // Rate limited, wait and retry
                const retryAfter = response.headers.get('Retry-After');
                await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
                continue;
            }
            
            return response;
        } catch (error) {
            if (i === maxRetries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
        }
    }
}
```

---

## 📞 Support & Resources

### API Support
- **Documentation:** https://docs.clickup-brain.com/api
- **Status Page:** https://status.clickup-brain.com
- **Support Email:** api-support@clickup-brain.com
- **Developer Forum:** https://community.clickup-brain.com

### SDK Support
- **GitHub Repositories:** https://github.com/clickup-brain
- **Issue Tracking:** https://github.com/clickup-brain/sdk/issues
- **Contributing:** https://github.com/clickup-brain/sdk/blob/main/CONTRIBUTING.md

### Testing & Sandbox
- **Sandbox Environment:** https://sandbox-api.clickup-brain.com
- **Test API Keys:** Available in developer dashboard
- **Mock Data:** Pre-configured test data sets
- **Integration Testing:** Automated testing tools

---

*This comprehensive API documentation provides everything needed to integrate with ClickUp Brain. For additional support or custom integration assistance, contact our API support team.*









