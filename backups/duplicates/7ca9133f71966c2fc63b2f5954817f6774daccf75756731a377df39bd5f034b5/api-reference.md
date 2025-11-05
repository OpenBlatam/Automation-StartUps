# 🔌 API Reference
## Complete API Documentation for AI Marketing Course & SaaS Platform

This document provides comprehensive API documentation for the AI Marketing Course & SaaS Platform.

---

## 📋 Table of Contents

- [Authentication](#authentication)
- [Content Generation](#content-generation)
- [Sales Policy Framework](#sales-policy-framework)
- [Template Management](#template-management)
- [User Management](#user-management)
- [Course Management](#course-management)
- [Analytics](#analytics)
- [Error Handling](#error-handling)

---

## 🔐 Authentication

### **Base URL**
```
https://api.ai-marketing-saas.com/v1
```

### **Authentication Methods**
- **JWT Bearer Token**: Required for all authenticated endpoints
- **API Key**: For server-to-server communication

### **Login**
```http
POST /auth/login
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
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "plan": "pro",
      "permissions": ["read", "write", "admin"]
    },
    "expiresIn": 3600
  }
}
```

### **Register**
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe",
  "company": "Tech Solutions Inc."
}
```

### **Refresh Token**
```http
POST /auth/refresh
Authorization: Bearer <token>
```

---

## 📝 Content Generation

### **Generate Marketing Content**
```http
POST /content/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "type": "email",
  "template": "welcome",
  "data": {
    "userName": "John Doe",
    "company": "Tech Solutions Inc.",
    "industry": "SaaS"
  },
  "options": {
    "tone": "professional",
    "length": "medium",
    "includeCTA": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "content_123",
    "type": "email",
    "content": {
      "subject": "Welcome to Tech Solutions Inc.!",
      "body": "Dear John Doe,\n\nWelcome to our platform...",
      "html": "<html>...</html>"
    },
    "metadata": {
      "wordCount": 150,
      "generatedAt": "2024-01-15T10:30:00Z",
      "template": "welcome",
      "aiModel": "copy-ai"
    }
  }
}
```

### **Content Types**

#### **Email Marketing**
```json
{
  "type": "email",
  "templates": ["welcome", "followup", "newsletter", "promotional"],
  "requiredFields": ["userName", "company"],
  "optionalFields": ["industry", "customMessage"]
}
```

#### **Social Media**
```json
{
  "type": "social",
  "platforms": ["linkedin", "twitter", "facebook", "instagram"],
  "formats": ["post", "story", "ad", "thread"],
  "maxLength": 280
}
```

#### **Blog Content**
```json
{
  "type": "blog",
  "formats": ["article", "how-to", "case-study", "news"],
  "lengths": ["short", "medium", "long"],
  "topics": ["marketing", "ai", "sales", "business"]
}
```

### **Generate Sales Policy**
```http
POST /content/sales-policy
Authorization: Bearer <token>
Content-Type: application/json

{
  "companyName": "Tech Solutions Inc.",
  "industry": "SaaS",
  "templateType": "basic",
  "customizations": {
    "includeCompliance": true,
    "includeTraining": true,
    "includePerformance": true
  },
  "requirements": {
    "regulations": ["GDPR", "CCPA"],
    "industryStandards": ["ISO 27001"],
    "customPolicies": ["Remote Work Policy"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "policy_123",
    "companyName": "Tech Solutions Inc.",
    "industry": "SaaS",
    "templateType": "basic",
    "content": {
      "title": "Sales Policy Framework - Tech Solutions Inc.",
      "sections": [
        {
          "title": "Sales Process Overview",
          "content": "Our sales process consists of...",
          "subsections": [...]
        }
      ],
      "compliance": {
        "gdpr": true,
        "ccpa": true,
        "iso27001": false
      }
    },
    "metadata": {
      "wordCount": 2500,
      "generatedAt": "2024-01-15T10:30:00Z",
      "aiModel": "copy-ai",
      "complianceScore": 95
    }
  }
}
```

---

## 📋 Sales Policy Framework

### **Get Available Templates**
```http
GET /sales-policy/templates
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "basic",
      "name": "Basic Sales Policy",
      "description": "Standard sales policy template",
      "sections": ["process", "service", "refunds", "privacy"],
      "industries": ["all"],
      "compliance": ["basic"]
    },
    {
      "id": "healthcare",
      "name": "Healthcare Sales Policy",
      "description": "HIPAA-compliant sales policy",
      "sections": ["process", "service", "refunds", "privacy", "hipaa"],
      "industries": ["healthcare", "medical"],
      "compliance": ["hipaa", "fda", "hitech"]
    }
  ]
}
```

### **Create Custom Template**
```http
POST /sales-policy/templates
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Custom Sales Policy",
  "description": "Custom template for our company",
  "prompt": "Create a sales policy for {companyName} that includes...",
  "variables": ["companyName", "industry", "size"],
  "sections": ["process", "service", "compliance"],
  "isPublic": false
}
```

### **Generate Policy from Template**
```http
POST /sales-policy/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "templateId": "basic",
  "companyData": {
    "name": "Tech Solutions Inc.",
    "industry": "SaaS",
    "size": "50-200 employees",
    "targetMarket": "SMBs"
  },
  "customizations": {
    "includeCompliance": true,
    "includeTraining": true,
    "customSections": ["Remote Work Policy"]
  }
}
```

---

## 🎨 Template Management

### **Get Templates**
```http
GET /templates
Authorization: Bearer <token>
Query Parameters:
  - category: string (optional)
  - type: string (optional)
  - isPublic: boolean (optional)
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "template_123",
      "name": "Welcome Email Template",
      "category": "email",
      "type": "welcome",
      "description": "Professional welcome email template",
      "prompt": "Create a welcome email for {userName}...",
      "variables": ["userName", "company", "industry"],
      "isPublic": true,
      "createdBy": "system",
      "createdAt": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

### **Create Template**
```http
POST /templates
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Custom Email Template",
  "category": "email",
  "type": "custom",
  "description": "Custom email template for our needs",
  "prompt": "Create an email about {topic} for {audience}...",
  "variables": ["topic", "audience", "tone"],
  "isPublic": false,
  "tags": ["marketing", "custom"]
}
```

### **Update Template**
```http
PUT /templates/{templateId}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Template Name",
  "description": "Updated description",
  "prompt": "Updated prompt...",
  "variables": ["new", "variables"]
}
```

### **Delete Template**
```http
DELETE /templates/{templateId}
Authorization: Bearer <token>
```

---

## 👥 User Management

### **Get User Profile**
```http
GET /users/profile
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "company": "Tech Solutions Inc.",
    "plan": "pro",
    "permissions": ["read", "write", "admin"],
    "subscription": {
      "status": "active",
      "currentPeriodEnd": "2024-02-15T10:30:00Z",
      "cancelAtPeriodEnd": false
    },
    "usage": {
      "contentGenerations": 150,
      "templatesCreated": 5,
      "policiesGenerated": 3
    }
  }
}
```

### **Update User Profile**
```http
PUT /users/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "John Smith",
  "company": "New Company Inc.",
  "preferences": {
    "defaultTone": "professional",
    "defaultLength": "medium",
    "notifications": true
  }
}
```

### **Get Team Members** (Pro/Enterprise)
```http
GET /users/team
Authorization: Bearer <token>
```

### **Invite Team Member**
```http
POST /users/team/invite
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newmember@example.com",
  "role": "editor",
  "permissions": ["read", "write"]
}
```

---

## 🎓 Course Management

### **Get Course Progress**
```http
GET /courses/progress
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "currentModule": 2,
    "overallProgress": 45,
    "modules": [
      {
        "id": 1,
        "name": "AI Marketing Fundamentals",
        "progress": 100,
        "completed": true,
        "score": 95,
        "completedAt": "2024-01-10T10:30:00Z"
      },
      {
        "id": 2,
        "name": "Advanced Copy.ai Techniques",
        "progress": 60,
        "completed": false,
        "score": null,
        "currentLesson": 3
      }
    ]
  }
}
```

### **Get Module Content**
```http
GET /courses/modules/{moduleId}
Authorization: Bearer <token>
```

### **Submit Lesson Completion**
```http
POST /courses/lessons/{lessonId}/complete
Authorization: Bearer <token>
Content-Type: application/json

{
  "score": 95,
  "timeSpent": 1800,
  "answers": {
    "question1": "answer1",
    "question2": "answer2"
  }
}
```

### **Get Certificates**
```http
GET /courses/certificates
Authorization: Bearer <token>
```

---

## 📊 Analytics

### **Get Usage Analytics**
```http
GET /analytics/usage
Authorization: Bearer <token>
Query Parameters:
  - startDate: string (ISO date)
  - endDate: string (ISO date)
  - granularity: string (day, week, month)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "contentGenerations": {
      "total": 150,
      "byType": {
        "email": 50,
        "social": 30,
        "blog": 40,
        "policy": 30
      },
      "trend": [
        {"date": "2024-01-01", "count": 10},
        {"date": "2024-01-02", "count": 15}
      ]
    },
    "performance": {
      "averageResponseTime": 1.2,
      "successRate": 98.5,
      "errorRate": 1.5
    }
  }
}
```

### **Get Content Performance**
```http
GET /analytics/content/{contentId}
Authorization: Bearer <token>
```

---

## ❌ Error Handling

### **Error Response Format**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req_123456"
  }
}
```

### **Common Error Codes**

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid input data |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `COPY_AI_ERROR` | 502 | Copy.ai service error |

### **Rate Limiting**
- **Free Plan**: 100 requests/hour
- **Pro Plan**: 1000 requests/hour
- **Enterprise Plan**: 10000 requests/hour

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

---

## 🔧 SDK Examples

### **JavaScript/Node.js**
```javascript
const AIMarketingAPI = require('ai-marketing-saas-sdk');

const client = new AIMarketingAPI({
  apiKey: 'your_api_key',
  baseURL: 'https://api.ai-marketing-saas.com/v1'
});

// Generate content
const content = await client.content.generate({
  type: 'email',
  template: 'welcome',
  data: {
    userName: 'John Doe',
    company: 'Tech Solutions Inc.'
  }
});

// Generate sales policy
const policy = await client.salesPolicy.generate({
  companyName: 'Tech Solutions Inc.',
  industry: 'SaaS',
  templateType: 'basic'
});
```

### **Python**
```python
from ai_marketing_saas import Client

client = Client(api_key='your_api_key')

# Generate content
content = client.content.generate(
    type='email',
    template='welcome',
    data={
        'userName': 'John Doe',
        'company': 'Tech Solutions Inc.'
    }
)

# Generate sales policy
policy = client.sales_policy.generate(
    company_name='Tech Solutions Inc.',
    industry='SaaS',
    template_type='basic'
)
```

---

## 📞 Support

For API support:
- **Email**: api-support@ai-marketing-saas.com
- **Documentation**: [Full API docs](https://docs.ai-marketing-saas.com/api)
- **Status Page**: [API Status](https://status.ai-marketing-saas.com)

---

*This API reference is regularly updated. Last updated: December 2024*

