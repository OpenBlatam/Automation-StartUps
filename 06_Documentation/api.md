# 🔌 API Reference - ClickUp Brain

## Visión General

La API de ClickUp Brain proporciona acceso programático a todas las funcionalidades del sistema de inteligencia estratégica. Está construida siguiendo principios RESTful y utiliza autenticación basada en tokens JWT.

## 🔐 Autenticación

### Obtener Token de Acceso

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@company.com",
  "password": "secure_password",
  "organization_id": "org_123"
}
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "token_type": "Bearer",
  "user": {
    "id": "user_123",
    "email": "user@company.com",
    "name": "John Doe",
    "role": "strategic_manager",
    "organization_id": "org_123"
  }
}
```

### Refrescar Token

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## 🧠 AI Knowledge Manager API

### Hacer Preguntas Estratégicas

```http
POST /api/v1/knowledge/query
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "question": "¿Cuáles son las principales oportunidades de mercado en el sector tecnológico?",
  "context": {
    "region": "global",
    "timeframe": "next_quarter",
    "focus_areas": ["ai", "cloud_computing", "cybersecurity"]
  },
  "response_format": "structured"
}
```

**Respuesta:**
```json
{
  "query_id": "query_123",
  "answer": {
    "summary": "Se identificaron 5 oportunidades principales en el sector tecnológico...",
    "opportunities": [
      {
        "id": "opp_001",
        "title": "AI-Powered Customer Service",
        "description": "Implementación de chatbots inteligentes...",
        "market_size": "$2.5B",
        "growth_rate": "25%",
        "confidence_score": 0.92
      }
    ],
    "insights": [
      {
        "type": "market_trend",
        "description": "El mercado de AI está creciendo 30% anualmente",
        "source": "industry_report_2024",
        "relevance_score": 0.88
      }
    ],
    "recommendations": [
      {
        "action": "investigate_ai_opportunities",
        "priority": "high",
        "timeline": "30_days",
        "resources_needed": ["ai_expert", "market_researcher"]
      }
    ]
  },
  "sources": [
    {
      "type": "internal_document",
      "title": "Strategic Plan 2024",
      "relevance": 0.95
    },
    {
      "type": "market_research",
      "title": "AI Market Analysis Q4 2024",
      "relevance": 0.87
    }
  ],
  "processing_time": 1.2
}
```

### Buscar Conocimiento

```http
GET /api/v1/knowledge/search?q=strategic+planning&filters=type:document,region:global&limit=10
Authorization: Bearer {access_token}
```

**Respuesta:**
```json
{
  "results": [
    {
      "id": "doc_123",
      "title": "Global Strategic Plan 2024",
      "type": "strategic_document",
      "content_preview": "Our strategic objectives for 2024 include...",
      "relevance_score": 0.94,
      "last_updated": "2024-01-15T10:30:00Z",
      "tags": ["strategy", "planning", "global"]
    }
  ],
  "total_results": 25,
  "page": 1,
  "per_page": 10
}
```

### Subir Documentos

```http
POST /api/v1/knowledge/documents
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

{
  "file": "strategic_plan_2024.pdf",
  "title": "Strategic Plan 2024",
  "description": "Annual strategic planning document",
  "tags": ["strategy", "planning", "2024"],
  "visibility": "organization"
}
```

## 🚀 AI Project Manager API

### Crear Proyecto Estratégico

```http
POST /api/v1/projects
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "AI Market Expansion",
  "description": "Strategic initiative to expand into AI market",
  "type": "strategic_initiative",
  "priority": "high",
  "timeline": {
    "start_date": "2024-02-01",
    "end_date": "2024-12-31"
  },
  "objectives": [
    {
      "title": "Market Research",
      "description": "Complete comprehensive market analysis",
      "due_date": "2024-03-15",
      "success_metrics": ["research_report_completed", "market_size_identified"]
    }
  ],
  "team_members": [
    {
      "user_id": "user_123",
      "role": "project_manager",
      "timezone": "EST"
    }
  ],
  "dependencies": ["market_research_completed"],
  "budget": {
    "allocated": 500000,
    "currency": "USD"
  }
}
```

**Respuesta:**
```json
{
  "project_id": "proj_123",
  "name": "AI Market Expansion",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z",
  "ai_recommendations": [
    {
      "type": "resource_optimization",
      "suggestion": "Consider adding AI specialist to team",
      "confidence": 0.87
    },
    {
      "type": "timeline_optimization",
      "suggestion": "Market research phase could be completed 2 weeks earlier",
      "confidence": 0.92
    }
  ],
  "automated_tasks": [
    {
      "id": "task_001",
      "title": "Weekly Progress Report",
      "type": "automated_report",
      "frequency": "weekly",
      "next_due": "2024-01-22T09:00:00Z"
    }
  ]
}
```

### Obtener Reportes Automáticos

```http
GET /api/v1/projects/{project_id}/reports?type=progress&period=weekly
Authorization: Bearer {access_token}
```

**Respuesta:**
```json
{
  "report_id": "report_123",
  "project_id": "proj_123",
  "type": "progress",
  "period": "weekly",
  "generated_at": "2024-01-15T09:00:00Z",
  "summary": {
    "overall_progress": 0.35,
    "on_track": true,
    "risks": ["resource_constraint"],
    "achievements": ["market_research_phase_completed"]
  },
  "detailed_metrics": {
    "budget_utilization": 0.28,
    "timeline_adherence": 0.95,
    "team_productivity": 0.87,
    "stakeholder_satisfaction": 0.92
  },
  "ai_insights": [
    {
      "type": "performance_analysis",
      "insight": "Team productivity is 15% above average for similar projects",
      "recommendation": "Consider documenting best practices for future projects"
    }
  ],
  "next_actions": [
    {
      "action": "schedule_stakeholder_review",
      "due_date": "2024-01-20",
      "assigned_to": "user_123"
    }
  ]
}
```

### Coordinación Cross-Timezone

```http
POST /api/v1/projects/{project_id}/coordination/meetings
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Strategic Review Meeting",
  "participants": [
    {
      "user_id": "user_123",
      "timezone": "EST"
    },
    {
      "user_id": "user_456",
      "timezone": "PST"
    },
    {
      "user_id": "user_789",
      "timezone": "GMT"
    }
  ],
  "duration_minutes": 60,
  "preferred_times": ["morning", "afternoon"],
  "urgency": "medium"
}
```

**Respuesta:**
```json
{
  "meeting_id": "meeting_123",
  "suggested_times": [
    {
      "start_time": "2024-01-20T14:00:00Z",
      "end_time": "2024-01-20T15:00:00Z",
      "local_times": {
        "EST": "2024-01-20T09:00:00",
        "PST": "2024-01-20T06:00:00",
        "GMT": "2024-01-20T14:00:00"
      },
      "availability_score": 0.95
    }
  ],
  "ai_recommendations": [
    {
      "type": "optimal_timing",
      "suggestion": "14:00 UTC provides best overlap for all participants",
      "reasoning": "Minimizes early morning/late evening conflicts"
    }
  ]
}
```

## ✍️ AI Writer for Work API

### Generar Documento Estratégico

```http
POST /api/v1/writer/generate
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "document_type": "strategic_proposal",
  "title": "AI Market Expansion Proposal",
  "context": {
    "audience": "executive_team",
    "purpose": "funding_approval",
    "industry": "technology",
    "region": "global"
  },
  "content_requirements": {
    "sections": ["executive_summary", "market_analysis", "financial_projections", "implementation_plan"],
    "tone": "professional",
    "length": "comprehensive"
  },
  "data_sources": [
    {
      "type": "project_data",
      "project_id": "proj_123"
    },
    {
      "type": "market_research",
      "query": "AI market trends 2024"
    }
  ],
  "customization": {
    "include_charts": true,
    "include_recommendations": true,
    "language": "en"
  }
}
```

**Respuesta:**
```json
{
  "document_id": "doc_456",
  "title": "AI Market Expansion Proposal",
  "status": "generated",
  "content": {
    "executive_summary": "This proposal outlines a strategic initiative to expand our market presence in the AI sector...",
    "sections": [
      {
        "title": "Executive Summary",
        "content": "Our analysis indicates a $2.5B market opportunity in AI-powered solutions...",
        "word_count": 250
      },
      {
        "title": "Market Analysis",
        "content": "The AI market is experiencing unprecedented growth with a CAGR of 25%...",
        "word_count": 800,
        "charts": [
          {
            "type": "market_size_projection",
            "data": "chart_data_123"
          }
        ]
      }
    ],
    "total_word_count": 2500,
    "estimated_reading_time": "10 minutes"
  },
  "ai_insights": [
    {
      "type": "content_optimization",
      "suggestion": "Consider adding competitive analysis section",
      "reasoning": "Executive audience typically expects competitive landscape overview"
    }
  ],
  "generation_metadata": {
    "data_sources_used": 15,
    "confidence_score": 0.91,
    "generation_time": 45.2
  }
}
```

### Personalizar Contenido

```http
POST /api/v1/writer/customize
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "document_id": "doc_456",
  "customizations": {
    "tone": "casual",
    "audience": "technical_team",
    "add_sections": ["technical_requirements", "implementation_timeline"],
    "remove_sections": ["financial_projections"],
    "language": "es"
  }
}
```

## 🎯 Opportunity Discovery API

### Descubrir Oportunidades

```http
POST /api/v1/opportunities/discover
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "search_criteria": {
    "market_segments": ["ai", "cloud_computing", "cybersecurity"],
    "geographic_regions": ["north_america", "europe", "asia_pacific"],
    "time_horizon": "next_12_months",
    "min_market_size": 1000000000,
    "min_growth_rate": 0.15
  },
  "analysis_depth": "comprehensive",
  "include_competitive_analysis": true,
  "include_risk_assessment": true
}
```

**Respuesta:**
```json
{
  "discovery_id": "disc_123",
  "opportunities": [
    {
      "id": "opp_001",
      "title": "AI-Powered Customer Service Solutions",
      "description": "Market opportunity in AI-driven customer service automation",
      "market_analysis": {
        "market_size": 2500000000,
        "growth_rate": 0.28,
        "competition_level": "medium",
        "barriers_to_entry": "moderate"
      },
      "fit_analysis": {
        "strategic_alignment": 0.92,
        "capability_match": 0.87,
        "resource_requirements": "high",
        "timeline_to_market": "12_months"
      },
      "financial_projections": {
        "investment_required": 5000000,
        "projected_revenue_year_1": 2000000,
        "projected_revenue_year_3": 15000000,
        "roi_timeline": "18_months"
      },
      "risk_assessment": {
        "market_risk": "low",
        "technology_risk": "medium",
        "competitive_risk": "medium",
        "overall_risk_score": 0.35
      },
      "recommendations": [
        {
          "action": "conduct_feasibility_study",
          "priority": "high",
          "timeline": "30_days",
          "resources_needed": ["market_researcher", "ai_specialist"]
        }
      ],
      "confidence_score": 0.89
    }
  ],
  "market_trends": [
    {
      "trend": "AI adoption acceleration",
      "impact": "positive",
      "confidence": 0.94,
      "timeframe": "next_6_months"
    }
  ],
  "competitive_landscape": {
    "key_players": [
      {
        "company": "TechCorp AI",
        "market_share": 0.25,
        "strengths": ["technology", "brand"],
        "weaknesses": ["pricing", "support"]
      }
    ],
    "market_gaps": [
      {
        "gap": "SMB-focused AI solutions",
        "opportunity_size": "medium",
        "difficulty": "low"
      }
    ]
  }
}
```

### Evaluar Oportunidad

```http
POST /api/v1/opportunities/{opportunity_id}/evaluate
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "evaluation_criteria": {
    "strategic_fit": 0.9,
    "market_potential": 0.85,
    "competitive_advantage": 0.75,
    "resource_availability": 0.8,
    "risk_tolerance": 0.7
  },
  "additional_analysis": {
    "include_financial_modeling": true,
    "include_scenario_analysis": true,
    "include_implementation_plan": true
  }
}
```

## 📊 Analytics y Reporting API

### Obtener Métricas Estratégicas

```http
GET /api/v1/analytics/strategic-metrics?period=quarterly&organization_id=org_123
Authorization: Bearer {access_token}
```

**Respuesta:**
```json
{
  "period": "Q4_2024",
  "organization_id": "org_123",
  "metrics": {
    "strategic_alignment_score": {
      "current": 0.87,
      "previous": 0.82,
      "trend": "improving",
      "change_percentage": 6.1
    },
    "opportunity_conversion_rate": {
      "current": 0.34,
      "previous": 0.28,
      "trend": "improving",
      "change_percentage": 21.4
    },
    "cross_team_collaboration_index": {
      "current": 0.76,
      "previous": 0.71,
      "trend": "improving",
      "change_percentage": 7.0
    },
    "innovation_velocity": {
      "current": 0.68,
      "previous": 0.65,
      "trend": "improving",
      "change_percentage": 4.6
    }
  },
  "benchmarks": {
    "industry_average": {
      "strategic_alignment_score": 0.72,
      "opportunity_conversion_rate": 0.25,
      "cross_team_collaboration_index": 0.68,
      "innovation_velocity": 0.58
    },
    "performance_vs_benchmark": {
      "strategic_alignment_score": "above_average",
      "opportunity_conversion_rate": "above_average",
      "cross_team_collaboration_index": "above_average",
      "innovation_velocity": "above_average"
    }
  },
  "ai_insights": [
    {
      "type": "performance_analysis",
      "insight": "Strategic alignment has improved significantly due to better cross-team communication",
      "recommendation": "Continue investing in collaboration tools and processes"
    }
  ]
}
```

### Generar Reporte Personalizado

```http
POST /api/v1/analytics/reports/generate
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "report_type": "executive_summary",
  "audience": "c_level",
  "time_period": {
    "start_date": "2024-01-01",
    "end_date": "2024-03-31"
  },
  "metrics": [
    "strategic_alignment_score",
    "opportunity_pipeline",
    "team_performance",
    "financial_impact"
  ],
  "format": "pdf",
  "include_charts": true,
  "include_recommendations": true
}
```

## 🔔 Notificaciones y Alertas API

### Configurar Alertas

```http
POST /api/v1/alerts/configure
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "alert_name": "Strategic Risk Alert",
  "conditions": [
    {
      "metric": "strategic_alignment_score",
      "operator": "less_than",
      "threshold": 0.7,
      "time_window": "7_days"
    }
  ],
  "notification_channels": ["email", "slack", "in_app"],
  "recipients": ["strategic_team", "executives"],
  "frequency": "immediate"
}
```

### Obtener Alertas

```http
GET /api/v1/alerts?status=active&severity=high&limit=20
Authorization: Bearer {access_token}
```

## 🌐 Colaboración Cross-Team API

### Crear Sesión de Colaboración

```http
POST /api/v1/collaboration/sessions
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "session_type": "strategic_planning",
  "title": "Q1 Strategic Review",
  "participants": [
    {
      "user_id": "user_123",
      "role": "facilitator",
      "timezone": "EST"
    },
    {
      "user_id": "user_456",
      "role": "participant",
      "timezone": "PST"
    }
  ],
  "agenda": [
    {
      "topic": "Review Q1 objectives",
      "duration_minutes": 30,
      "presenter": "user_123"
    },
    {
      "topic": "Identify new opportunities",
      "duration_minutes": 45,
      "presenter": "ai_assistant"
    }
  ],
  "tools": ["whiteboard", "ai_assistant", "real_time_editing"],
  "scheduled_time": "2024-01-20T14:00:00Z"
}
```

## 📱 Webhooks

### Configurar Webhook

```http
POST /api/v1/webhooks
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "url": "https://your-app.com/webhooks/clickup-brain",
  "events": [
    "opportunity.discovered",
    "project.status_changed",
    "alert.triggered"
  ],
  "secret": "your_webhook_secret",
  "active": true
}
```

### Payload de Webhook

```json
{
  "event_type": "opportunity.discovered",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "opportunity_id": "opp_123",
    "title": "AI Market Opportunity",
    "confidence_score": 0.89,
    "market_size": 2500000000
  },
  "organization_id": "org_123"
}
```

## 🚨 Códigos de Error

| Código | Descripción | Solución |
|--------|-------------|----------|
| 400 | Bad Request | Verificar formato de datos enviados |
| 401 | Unauthorized | Verificar token de autenticación |
| 403 | Forbidden | Verificar permisos de usuario |
| 404 | Not Found | Verificar ID de recurso |
| 429 | Rate Limited | Reducir frecuencia de requests |
| 500 | Internal Server Error | Contactar soporte técnico |

## 📚 SDKs y Librerías

### Python SDK

```python
from clickup_brain import ClickUpBrain

# Inicializar cliente
client = ClickUpBrain(
    api_key="your_api_key",
    organization_id="org_123"
)

# Hacer consulta estratégica
response = client.knowledge.query(
    question="¿Cuáles son las oportunidades de mercado?",
    context={"region": "global"}
)

# Crear proyecto
project = client.projects.create(
    name="AI Market Expansion",
    description="Strategic initiative",
    priority="high"
)
```

### JavaScript SDK

```javascript
import { ClickUpBrain } from '@clickup-brain/sdk';

// Inicializar cliente
const client = new ClickUpBrain({
  apiKey: 'your_api_key',
  organizationId: 'org_123'
});

// Hacer consulta estratégica
const response = await client.knowledge.query({
  question: 'What are the market opportunities?',
  context: { region: 'global' }
});

// Crear proyecto
const project = await client.projects.create({
  name: 'AI Market Expansion',
  description: 'Strategic initiative',
  priority: 'high'
});
```

## 🔧 Rate Limits

| Endpoint | Límite | Ventana |
|----------|--------|---------|
| `/api/v1/knowledge/query` | 100 requests | 1 hora |
| `/api/v1/projects/*` | 1000 requests | 1 hora |
| `/api/v1/opportunities/*` | 50 requests | 1 hora |
| `/api/v1/analytics/*` | 200 requests | 1 hora |

## 📞 Soporte API

- **Documentación**: [api.clickupbrain.ai/docs](https://api.clickupbrain.ai/docs)
- **Status Page**: [status.clickupbrain.ai](https://status.clickupbrain.ai)
- **Soporte**: api-support@clickupbrain.ai
- **Community**: [community.clickupbrain.ai](https://community.clickupbrain.ai)

---

Esta API reference proporciona acceso completo a todas las funcionalidades de ClickUp Brain, permitiendo integración con sistemas existentes y desarrollo de aplicaciones personalizadas.



