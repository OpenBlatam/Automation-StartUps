# 🔌 COPYCAR.AI ULTIMATE API DOCUMENTATION
## Documentación Completa de API CopyCar.ai Ultimate ABM

---

## 📋 RESUMEN EJECUTIVO ULTIMATE

**Versión API:** v2.0 Ultimate
**Base URL:** `https://api.copycarai.com/v2/ultimate`
**Autenticación:** Bearer Token + API Key
**Rate Limits:** 10,000 requests/hour (Ultimate tier)
**Formato:** JSON
**Encoding:** UTF-8
**Soporte:** 24/7 technical support

---

## 🔐 AUTENTICACIÓN COPYCAR.AI ULTIMATE

### **Métodos de Autenticación:**

#### **1. Bearer Token (Recomendado):**
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "X-API-Key: YOUR_API_KEY" \
     https://api.copycarai.com/v2/ultimate/accounts
```

#### **2. API Key + Secret:**
```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     -H "X-API-Secret: YOUR_API_SECRET" \
     https://api.copycarai.com/v2/ultimate/accounts
```

#### **3. OAuth 2.0:**
```bash
curl -H "Authorization: Bearer YOUR_OAUTH_TOKEN" \
     https://api.copycarai.com/v2/ultimate/accounts
```

### **Obtener Access Token:**
```javascript
const response = await fetch('https://api.copycarai.com/v2/ultimate/auth/token', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'YOUR_API_KEY'
  },
  body: JSON.stringify({
    grant_type: 'client_credentials',
    client_id: 'YOUR_CLIENT_ID',
    client_secret: 'YOUR_CLIENT_SECRET',
    scope: 'ultimate:read ultimate:write'
  })
});

const { access_token, expires_in, token_type } = await response.json();
```

---

## 🏢 ACCOUNT MANAGEMENT API ULTIMATE

### **1. Research Account Ultimate**

#### **Endpoint:**
```
POST /v2/ultimate/accounts/research
```

#### **Request Body:**
```json
{
  "company": {
    "name": "TechCorp Solutions",
    "domain": "techcorp.com",
    "industry": "Software Development",
    "size": "200-500 employees",
    "revenue": "$10M-$50M",
    "location": "San Francisco, CA",
    "technologies": ["AWS", "React", "Node.js"]
  },
  "research_config": {
    "depth": "comprehensive",
    "include_competitors": true,
    "include_news": true,
    "include_social": true,
    "include_financials": true
  },
  "personalization": {
    "level": "ultimate",
    "include_ai_insights": true,
    "include_predictions": true,
    "include_recommendations": true
  }
}
```

#### **Response:**
```json
{
  "success": true,
  "data": {
    "account_id": "acc_123456789",
    "research_id": "res_987654321",
    "profile": {
      "basic_info": {
        "name": "TechCorp Solutions",
        "domain": "techcorp.com",
        "industry": "Software Development",
        "size": "350 employees",
        "revenue": "$25M",
        "location": "San Francisco, CA",
        "founded": "2018",
        "website": "https://techcorp.com"
      },
      "decision_makers": [
        {
          "name": "Sarah Johnson",
          "title": "CTO",
          "email": "sarah.johnson@techcorp.com",
          "linkedin": "https://linkedin.com/in/sarahjohnson",
          "influence_score": 95,
          "pain_points": ["Infrastructure scaling", "Cost optimization"],
          "communication_preferences": {
            "channels": ["email", "linkedin"],
            "timing": "Tuesday-Thursday, 10-11 AM PST",
            "tone": "Technical, consultative"
          }
        }
      ],
      "pain_points": [
        {
          "category": "Infrastructure",
          "description": "AWS costs growing 300% with rapid scaling",
          "urgency": "high",
          "impact": "financial",
          "solutions": ["Auto-scaling optimization", "Cost monitoring"]
        }
      ],
      "opportunities": [
        {
          "type": "Cost Reduction",
          "description": "Potential 40% reduction in AWS costs",
          "value": "$150,000 annually",
          "timeline": "3-6 months",
          "probability": 85
        }
      ],
      "ai_insights": {
        "engagement_score": 87,
        "conversion_probability": 73,
        "optimal_approach": "Technical consultation",
        "recommended_content": ["Case studies", "Technical whitepapers"],
        "timing_insights": "Best engagement Tuesday-Thursday 10-11 AM"
      },
      "competitors": [
        {
          "name": "CloudScale Inc",
          "relationship": "Current vendor",
          "strengths": ["Pricing", "Support"],
          "weaknesses": ["Scalability", "Features"]
        }
      ],
      "news_insights": [
        {
          "title": "TechCorp raises $50M Series B",
          "date": "2024-01-15",
          "relevance": "high",
          "impact": "positive",
          "summary": "Funding round indicates growth phase and infrastructure needs"
        }
      ]
    },
    "generated_at": "2024-01-20T10:30:00Z",
    "processing_time": 2.3,
    "confidence_score": 94
  },
  "usage": {
    "api_calls": 1,
    "tokens_used": 2500,
    "remaining_quota": 97500
  }
}
```

### **2. Generate Personalized Content Ultimate**

#### **Endpoint:**
```
POST /v2/ultimate/content/generate
```

#### **Request Body:**
```json
{
  "account_id": "acc_123456789",
  "content_type": "email_outreach",
  "target_persona": {
    "name": "Sarah Johnson",
    "title": "CTO",
    "role": "decision_maker",
    "influence_score": 95
  },
  "campaign_config": {
    "objective": "schedule_demo",
    "urgency": "medium",
    "tone": "consultative",
    "length": "medium"
  },
  "personalization": {
    "level": "ultimate",
    "include_company_insights": true,
    "include_industry_context": true,
    "include_competitor_mentions": true,
    "include_social_proof": true
  },
  "channels": ["email", "linkedin"],
  "ai_enhancement": {
    "use_gpt4": true,
    "use_claude": true,
    "optimize_for_conversion": true,
    "a_b_test_variants": 3
  }
}
```

#### **Response:**
```json
{
  "success": true,
  "data": {
    "content_id": "cnt_456789123",
    "variants": [
      {
        "variant_id": "var_1",
        "channel": "email",
        "subject": "AWS costs growing 300%? Here's how TechCorp can scale smarter",
        "content": {
          "html": "<html>...</html>",
          "text": "Hi Sarah,\n\nI noticed TechCorp's impressive 200% growth...",
          "preview": "I noticed TechCorp's impressive 200% growth over the past 2 years..."
        },
        "personalization_score": 96,
        "conversion_prediction": 28,
        "ai_insights": {
          "strengths": ["Personal reference", "Specific pain point", "Clear value prop"],
          "optimizations": ["Add more social proof", "Include specific numbers"],
          "recommended_timing": "Tuesday 10:30 AM PST"
        }
      },
      {
        "variant_id": "var_2",
        "channel": "linkedin",
        "content": {
          "connection_request": "Hi Sarah, I'd love to connect and share some insights about AWS cost optimization for fast-growing dev teams like TechCorp.",
          "follow_up_message": "Thanks for connecting! I noticed TechCorp's impressive growth trajectory. Most React/Node.js teams I work with face similar infrastructure scaling challenges...",
          "post_content": "Just helped a React/Node.js team like TechCorp reduce AWS costs by 40% while improving performance. The key was smarter auto-scaling. What's your biggest infrastructure challenge right now?"
        },
        "personalization_score": 94,
        "conversion_prediction": 24
      }
    ],
    "recommendations": {
      "best_variant": "var_1",
      "optimal_timing": "Tuesday 10:30 AM PST",
      "follow_up_strategy": "Send LinkedIn connection request 2 days after email",
      "content_optimizations": [
        "Add specific AWS cost reduction numbers",
        "Include case study from similar company",
        "Mention specific TechCorp technologies"
      ]
    },
    "generated_at": "2024-01-20T10:35:00Z",
    "processing_time": 1.8,
    "confidence_score": 92
  },
  "usage": {
    "api_calls": 1,
    "tokens_used": 3200,
    "remaining_quota": 96800
  }
}
```

### **3. Create Campaign Ultimate**

#### **Endpoint:**
```
POST /v2/ultimate/campaigns/create
```

#### **Request Body:**
```json
{
  "campaign_name": "TechCorp Infrastructure Optimization Campaign",
  "account_id": "acc_123456789",
  "campaign_type": "multi_channel_abm",
  "objective": "schedule_demo",
  "target_personas": [
    {
      "name": "Sarah Johnson",
      "title": "CTO",
      "influence_score": 95
    },
    {
      "name": "Michael Chen",
      "title": "VP Engineering",
      "influence_score": 85
    }
  ],
  "channels": ["email", "linkedin", "website", "direct_mail"],
  "timeline": {
    "start_date": "2024-01-22",
    "duration_weeks": 4,
    "frequency": "weekly"
  },
  "content_strategy": {
    "week_1": {
      "theme": "Introduction & Value",
      "channels": ["email", "linkedin"],
      "content_types": ["insight_email", "connection_request"]
    },
    "week_2": {
      "theme": "Social Proof & Case Studies",
      "channels": ["email", "linkedin", "website"],
      "content_types": ["case_study_email", "social_proof_post", "landing_page"]
    },
    "week_3": {
      "theme": "Relationship Building",
      "channels": ["email", "linkedin", "direct_mail"],
      "content_types": ["personal_story_email", "engagement_post", "physical_mail"]
    },
    "week_4": {
      "theme": "Conversion & Demo Request",
      "channels": ["email", "linkedin", "phone"],
      "content_types": ["demo_request_email", "social_proof_post", "call_script"]
    }
  },
  "personalization": {
    "level": "ultimate",
    "include_ai_insights": true,
    "dynamic_content": true,
    "behavioral_triggers": true
  },
  "automation": {
    "enabled": true,
    "triggers": ["email_open", "link_click", "response_received"],
    "optimization": true,
    "a_b_testing": true
  }
}
```

#### **Response:**
```json
{
  "success": true,
  "data": {
    "campaign_id": "cmp_789123456",
    "campaign_name": "TechCorp Infrastructure Optimization Campaign",
    "status": "active",
    "timeline": {
      "start_date": "2024-01-22T00:00:00Z",
      "end_date": "2024-02-19T23:59:59Z",
      "duration_weeks": 4
    },
    "content_schedule": [
      {
        "week": 1,
        "date": "2024-01-22",
        "content": [
          {
            "id": "cnt_week1_email",
            "type": "email",
            "subject": "AWS costs growing 300%? Here's how TechCorp can scale smarter",
            "status": "scheduled",
            "send_time": "2024-01-22T10:30:00Z"
          },
          {
            "id": "cnt_week1_linkedin",
            "type": "linkedin_connection",
            "message": "Hi Sarah, I'd love to connect and share some insights about AWS cost optimization...",
            "status": "scheduled",
            "send_time": "2024-01-22T14:00:00Z"
          }
        ]
      }
    ],
    "automation_rules": [
      {
        "trigger": "email_open",
        "action": "send_linkedin_connection",
        "delay": "2 hours",
        "enabled": true
      },
      {
        "trigger": "link_click",
        "action": "send_follow_up_email",
        "delay": "1 hour",
        "enabled": true
      }
    ],
    "tracking": {
      "tracking_pixel": "https://api.copycarai.com/v2/ultimate/track/cmp_789123456",
      "webhook_url": "https://your-domain.com/webhooks/copycar",
      "analytics_dashboard": "https://dashboard.copycarai.com/campaigns/cmp_789123456"
    },
    "created_at": "2024-01-20T10:40:00Z",
    "estimated_performance": {
      "expected_response_rate": 28,
      "expected_meeting_conversion": 18,
      "expected_roi": 340
    }
  },
  "usage": {
    "api_calls": 1,
    "tokens_used": 4500,
    "remaining_quota": 95500
  }
}
```

---

## 📊 ANALYTICS & REPORTING API ULTIMATE

### **1. Get Campaign Performance Ultimate**

#### **Endpoint:**
```
GET /v2/ultimate/campaigns/{campaign_id}/performance
```

#### **Query Parameters:**
```
?start_date=2024-01-01&end_date=2024-01-31&granularity=daily&include_predictions=true
```

#### **Response:**
```json
{
  "success": true,
  "data": {
    "campaign_id": "cmp_789123456",
    "period": {
      "start_date": "2024-01-01T00:00:00Z",
      "end_date": "2024-01-31T23:59:59Z",
      "granularity": "daily"
    },
    "metrics": {
      "overall": {
        "emails_sent": 28,
        "emails_delivered": 27,
        "emails_opened": 19,
        "emails_clicked": 12,
        "emails_replied": 8,
        "meetings_scheduled": 5,
        "meetings_completed": 4,
        "conversions": 2
      },
      "rates": {
        "delivery_rate": 96.4,
        "open_rate": 70.4,
        "click_rate": 44.4,
        "reply_rate": 29.6,
        "meeting_rate": 18.5,
        "conversion_rate": 14.8
      },
      "engagement": {
        "average_engagement_score": 87,
        "high_engagement_accounts": 12,
        "medium_engagement_accounts": 8,
        "low_engagement_accounts": 7
      }
    },
    "daily_breakdown": [
      {
        "date": "2024-01-22",
        "emails_sent": 2,
        "emails_opened": 2,
        "emails_clicked": 1,
        "emails_replied": 1,
        "engagement_score": 92
      }
    ],
    "ai_insights": {
      "performance_analysis": "Campaign is performing 23% above average for similar accounts",
      "optimization_opportunities": [
        "Increase email frequency on Tuesdays and Thursdays",
        "Add more technical content for CTO persona",
        "Include specific AWS cost reduction numbers"
      ],
      "predictions": {
        "expected_final_response_rate": 32,
        "expected_final_conversion_rate": 18,
        "confidence_level": 89
      }
    },
    "generated_at": "2024-01-31T15:30:00Z"
  }
}
```

### **2. Get Account Insights Ultimate**

#### **Endpoint:**
```
GET /v2/ultimate/accounts/{account_id}/insights
```

#### **Response:**
```json
{
  "success": true,
  "data": {
    "account_id": "acc_123456789",
    "insights": {
      "engagement_trends": {
        "overall_score": 87,
        "trend": "increasing",
        "change_percentage": 15,
        "peak_engagement_days": ["Tuesday", "Wednesday", "Thursday"],
        "peak_engagement_times": ["10:00-11:00", "14:00-15:00"]
      },
      "content_preferences": {
        "preferred_content_types": ["Technical case studies", "Industry insights", "ROI calculators"],
        "preferred_channels": ["Email", "LinkedIn"],
        "optimal_content_length": "Medium (200-400 words)",
        "preferred_tone": "Technical, consultative"
      },
      "behavioral_patterns": {
        "response_likelihood": 73,
        "decision_timeline": "2-4 weeks",
        "influence_factors": ["Cost savings", "Technical expertise", "Social proof"],
        "objection_patterns": ["Budget constraints", "Timing concerns", "Vendor evaluation"]
      },
      "ai_predictions": {
        "conversion_probability": 68,
        "optimal_next_action": "Send technical case study",
        "recommended_timing": "Tuesday 10:30 AM PST",
        "risk_factors": ["Competitor evaluation", "Budget approval process"],
        "success_factors": ["Technical credibility", "Cost justification", "Implementation timeline"]
      }
    },
    "recommendations": [
      {
        "type": "content",
        "description": "Send AWS cost optimization case study",
        "priority": "high",
        "expected_impact": "Increase engagement by 25%"
      },
      {
        "type": "timing",
        "description": "Schedule next touchpoint for Tuesday 10:30 AM",
        "priority": "medium",
        "expected_impact": "Increase response rate by 15%"
      }
    ],
    "generated_at": "2024-01-31T15:35:00Z"
  }
}
```

---

## 🔄 WEBHOOKS COPYCAR.AI ULTIMATE

### **1. Campaign Events Webhook**

#### **Endpoint Configuration:**
```
POST https://your-domain.com/webhooks/copycar/campaigns
```

#### **Webhook Payload:**
```json
{
  "event_type": "campaign.engagement.detected",
  "timestamp": "2024-01-22T10:35:00Z",
  "campaign_id": "cmp_789123456",
  "account_id": "acc_123456789",
  "contact_id": "ctc_456789123",
  "data": {
    "engagement_type": "email_open",
    "content_id": "cnt_week1_email",
    "engagement_score": 92,
    "user_agent": "Mozilla/5.0...",
    "ip_address": "192.168.1.100",
    "location": {
      "city": "San Francisco",
      "state": "CA",
      "country": "US"
    }
  },
  "triggered_actions": [
    {
      "action_type": "send_linkedin_connection",
      "scheduled_time": "2024-01-22T12:35:00Z",
      "status": "scheduled"
    }
  ]
}
```

### **2. Account Research Webhook**

#### **Webhook Payload:**
```json
{
  "event_type": "account.research.completed",
  "timestamp": "2024-01-22T10:30:00Z",
  "account_id": "acc_123456789",
  "research_id": "res_987654321",
  "data": {
    "research_score": 94,
    "processing_time": 2.3,
    "insights_generated": 15,
    "decision_makers_found": 3,
    "pain_points_identified": 5,
    "opportunities_discovered": 4
  },
  "next_actions": [
    {
      "action_type": "create_personalized_campaign",
      "priority": "high",
      "estimated_completion": "2024-01-22T10:45:00Z"
    }
  ]
}
```

---

## 🚨 ERROR HANDLING COPYCAR.AI ULTIMATE

### **Error Response Format:**
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Maximum 10,000 requests per hour.",
    "details": {
      "limit": 10000,
      "remaining": 0,
      "reset_time": "2024-01-22T11:00:00Z"
    },
    "documentation_url": "https://docs.copycarai.com/errors/rate-limit-exceeded",
    "support_url": "https://support.copycarai.com/tickets/new"
  },
  "request_id": "req_123456789",
  "timestamp": "2024-01-22T10:30:00Z"
}
```

### **Common Error Codes:**
```javascript
const errorCodes = {
  // Authentication Errors
  'INVALID_API_KEY': 'API key is invalid or expired',
  'INVALID_TOKEN': 'Access token is invalid or expired',
  'INSUFFICIENT_PERMISSIONS': 'Insufficient permissions for this operation',
  
  // Rate Limiting
  'RATE_LIMIT_EXCEEDED': 'Rate limit exceeded for your tier',
  'QUOTA_EXCEEDED': 'Monthly quota exceeded',
  
  // Validation Errors
  'INVALID_REQUEST': 'Request validation failed',
  'MISSING_REQUIRED_FIELD': 'Required field is missing',
  'INVALID_FIELD_VALUE': 'Field value is invalid',
  
  // Resource Errors
  'ACCOUNT_NOT_FOUND': 'Account not found',
  'CAMPAIGN_NOT_FOUND': 'Campaign not found',
  'CONTENT_NOT_FOUND': 'Content not found',
  
  // Processing Errors
  'PROCESSING_FAILED': 'Content processing failed',
  'AI_SERVICE_UNAVAILABLE': 'AI service temporarily unavailable',
  'TIMEOUT': 'Request processing timeout'
};
```

---

## 📚 SDKs COPYCAR.AI ULTIMATE

### **1. JavaScript/Node.js SDK:**

#### **Installation:**
```bash
npm install @copycarai/ultimate-sdk
```

#### **Usage:**
```javascript
const CopyCarAI = require('@copycarai/ultimate-sdk');

const client = new CopyCarAI({
  apiKey: 'your_api_key',
  environment: 'production',
  version: 'ultimate'
});

// Research account
const research = await client.accounts.research({
  company: {
    name: 'TechCorp Solutions',
    industry: 'Software Development',
    size: '200-500 employees'
  },
  research_config: {
    depth: 'comprehensive',
    include_competitors: true
  }
});

// Generate content
const content = await client.content.generate({
  account_id: research.data.account_id,
  content_type: 'email_outreach',
  target_persona: {
    name: 'Sarah Johnson',
    title: 'CTO'
  }
});

// Create campaign
const campaign = await client.campaigns.create({
  campaign_name: 'TechCorp Campaign',
  account_id: research.data.account_id,
  channels: ['email', 'linkedin'],
  timeline: {
    duration_weeks: 4
  }
});
```

### **2. Python SDK:**

#### **Installation:**
```bash
pip install copycarai-ultimate
```

#### **Usage:**
```python
from copycarai import CopyCarAI

client = CopyCarAI(
    api_key='your_api_key',
    environment='production',
    version='ultimate'
)

# Research account
research = client.accounts.research({
    'company': {
        'name': 'TechCorp Solutions',
        'industry': 'Software Development',
        'size': '200-500 employees'
    },
    'research_config': {
        'depth': 'comprehensive',
        'include_competitors': True
    }
})

# Generate content
content = client.content.generate({
    'account_id': research['data']['account_id'],
    'content_type': 'email_outreach',
    'target_persona': {
        'name': 'Sarah Johnson',
        'title': 'CTO'
    }
})

# Create campaign
campaign = client.campaigns.create({
    'campaign_name': 'TechCorp Campaign',
    'account_id': research['data']['account_id'],
    'channels': ['email', 'linkedin'],
    'timeline': {
        'duration_weeks': 4
    }
})
```

---

## 🎯 PRÓXIMOS PASOS API ULTIMATE

### **Implementación Inmediata:**
1. ✅ Obtener API keys CopyCar.ai Ultimate
2. ✅ Configurar autenticación
3. ✅ Probar endpoints básicos
4. ✅ Implementar error handling

### **Corto Plazo:**
1. 🔄 Integrar con CRM existente
2. 🔄 Implementar webhooks
3. 🔄 Configurar monitoreo
4. 🔄 Optimizar performance

### **Largo Plazo:**
1. 📈 Escalar integraciones
2. 📈 Implementar analytics avanzados
3. 📈 Optimizar automáticamente
4. 📈 Expandir funcionalidades

---

**Esta documentación API CopyCar.ai Ultimate proporciona todo lo necesario para integrar y utilizar la plataforma CopyCar.ai Ultimate ABM de manera completa y eficiente.**
