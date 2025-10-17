# 🚀 AI Marketing Course & SaaS Platform

A comprehensive AI-powered marketing education platform with integrated legal compliance and risk management tools.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Legal Compliance](#legal-compliance)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Overview

This project combines a comprehensive AI marketing course with a full-featured SaaS platform, including advanced legal compliance and risk management capabilities. The platform is designed to provide:

- **AI-Powered Learning**: Personalized course content with machine learning recommendations
- **SaaS Platform**: Complete learning management system with real-time analytics
- **Legal Compliance**: Integrated LegalOps CLI for contract analysis and compliance tracking
- **Risk Management**: Automated risk assessment and mitigation recommendations

## ✨ Features

### 🎓 AI Marketing Course
- **12-Week Comprehensive Program**: Complete curriculum covering AI fundamentals to advanced applications
- **Interactive Learning**: Video lessons, hands-on labs, quizzes, and real-world projects
- **AI-Powered Personalization**: Adaptive content delivery based on learning patterns
- **Certification Program**: Industry-recognized certificates and skill badges
- **Live Sessions**: Virtual classrooms with expert instructors
- **Project Portfolio**: Real-world project showcase and peer review system

### 🏗️ SaaS Platform
- **Learning Management System**: Complete course delivery and management
- **User Management**: Multi-role system (students, instructors, admins)
- **Payment Integration**: Stripe and PayPal support with subscription management
- **Analytics Dashboard**: Real-time learning analytics and performance tracking
- **Mobile Support**: Responsive design with offline content access
- **API Integration**: RESTful API for third-party integrations

### ⚖️ Legal Compliance
- **Contract Analysis**: Automated risk assessment and compliance checking
- **LegalOps CLI**: Command-line tool for legal document management
- **Compliance Tracking**: Task management and deadline monitoring
- **Template Generation**: Legal document templates (NDA, MSA, SLA, etc.)
- **Regulatory Support**: GDPR, CCPA, HIPAA, SOX compliance tools
- **Risk Assessment**: Automated legal risk identification and mitigation

### 🤖 AI Features
- **Content Generation**: AI-powered content creation for marketing materials
- **Personalized Learning**: Adaptive learning paths based on user behavior
- **Intelligent Tutoring**: AI chatbot for student support
- **Performance Prediction**: ML models for success prediction
- **Recommendation Engine**: Personalized course and content recommendations
- **Analytics Intelligence**: Advanced insights and trend analysis

## 🏗️ Architecture

### Technology Stack
- **Frontend**: React.js + TypeScript + Material-UI
- **Backend**: Node.js + Express + TypeScript
- **Database**: MongoDB + Redis (caching)
- **AI/ML**: Python + TensorFlow + Scikit-learn
- **Cloud**: AWS (EC2, RDS, S3, Lambda)
- **Authentication**: Auth0 + JWT
- **Payment**: Stripe + PayPal
- **Monitoring**: Prometheus + Grafana

### Microservices Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Auth Service  │
│   (React)       │◄──►│   (Express)     │◄──►│   (Auth0)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼───────┐ ┌─────▼─────┐ ┌─────▼─────┐
        │ Course Service│ │ User Service│ │ AI Service │
        │ (Node.js)     │ │ (Node.js)   │ │ (Python)   │
        └───────────────┘ └─────────────┘ └─────────────┘
                │               │               │
        ┌───────▼───────┐ ┌─────▼─────┐ ┌─────▼─────┐
        │ MongoDB       │ │ Redis      │ │ ML Models │
        │ (Courses DB)  │ │ (Cache)    │ │ (S3)      │
        └───────────────┘ └─────────────┘ └─────────────┘
```

## 🚀 Installation

### Prerequisites
- Node.js 18.0.0 or higher
- Python 3.8 or higher
- MongoDB 6.0 or higher
- Redis 7.0 or higher
- Docker (optional)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/ai-marketing-course/saas-platform.git
cd saas-platform
```

2. **Install dependencies**
```bash
# Backend dependencies
npm install

# AI service dependencies
cd ai_service
pip install -r requirements.txt
cd ..

# LegalOps CLI dependencies
cd legalops-cli
npm install
cd ..
```

3. **Environment setup**
```bash
# Copy environment files
cp .env.example .env
cp ai_service/.env.example ai_service/.env
cp legalops-cli/.env.example legalops-cli/.env

# Edit environment variables
nano .env
```

4. **Database setup**
```bash
# Start MongoDB and Redis
mongod
redis-server

# Or use Docker
docker-compose up -d mongo redis
```

5. **Start services**
```bash
# Start backend API
npm run dev

# Start AI service
cd ai_service
python app.py

# Start LegalOps CLI (optional)
cd legalops-cli
npm link
```

### Docker Deployment

1. **Build and start all services**
```bash
docker-compose up -d
```

2. **Access the application**
- Frontend: http://localhost:3000
- API: http://localhost:3001
- AI Service: http://localhost:5000
- Grafana: http://localhost:3001

## 📖 Usage

### Course Management

#### Create a Course
```bash
# Using API
curl -X POST http://localhost:3001/api/courses \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Marketing Fundamentals",
    "description": "Learn the basics of AI in marketing",
    "price": 299,
    "duration_weeks": 4,
    "difficulty_level": "beginner"
  }'
```

#### Enroll in Course
```bash
curl -X POST http://localhost:3001/api/courses/COURSE_ID/enroll \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### AI Content Generation

#### Generate Marketing Content
```bash
curl -X POST http://localhost:3001/api/ai/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "text",
    "prompt": "Create a social media post for our new AI marketing course",
    "settings": {
      "model": "gpt-4",
      "temperature": 0.7,
      "maxTokens": 500
    }
  }'
```

### Legal Compliance

#### Analyze Contract
```bash
# Using LegalOps CLI
legalops analyze contract.pdf

# Using API
curl -X POST http://localhost:3001/api/legal/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contractId": "contract_123",
    "content": "Contract content here..."
  }'
```

#### Generate Legal Template
```bash
# Using LegalOps CLI
legalops generate nda --interactive

# Using API
curl -X POST http://localhost:3001/api/legal/templates/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "templateId": "nda",
    "parties": {
      "partyA": "Acme Corp",
      "partyB": "Tech Solutions"
    }
  }'
```

## 📚 API Documentation

### Authentication
All API endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

### Course Endpoints

#### Get All Courses
```http
GET /api/courses
Query Parameters:
- page: Page number (default: 1)
- limit: Items per page (default: 10)
- difficulty: Filter by difficulty level
- instructor: Filter by instructor ID
- search: Search term
```

#### Get Course Details
```http
GET /api/courses/:id
```

#### Create Course
```http
POST /api/courses
Body:
{
  "title": "string",
  "description": "string",
  "price": "number",
  "duration_weeks": "number",
  "difficulty_level": "beginner|intermediate|advanced"
}
```

### AI Endpoints

#### Generate Content
```http
POST /api/ai/generate
Body:
{
  "type": "text|image|video|audio",
  "prompt": "string",
  "settings": {
    "model": "string",
    "temperature": "number",
    "maxTokens": "number"
  }
}
```

#### Get AI Models
```http
GET /api/ai/models
```

### Legal Endpoints

#### Analyze Contract
```http
POST /api/legal/analyze
Body:
{
  "contractId": "string",
  "content": "string",
  "options": "object"
}
```

#### Get Compliance Tasks
```http
GET /api/legal/compliance/tasks
Query Parameters:
- status: Filter by status
- regulation: Filter by regulation
- priority: Filter by priority
```

## ⚖️ Legal Compliance

### LegalOps CLI

The LegalOps CLI provides comprehensive legal document management capabilities:

#### Installation
```bash
npm install -g legalops-cli
```

#### Contract Analysis
```bash
# Analyze a contract
legalops analyze contract.pdf

# Compare two contract versions
legalops compare contract-v1.pdf contract-v2.pdf
```

#### Template Generation
```bash
# Generate NDA template
legalops generate nda --interactive

# Generate MSA template
legalops generate msa --parties '{"partyA":"Acme Corp","partyB":"Tech Solutions"}'
```

#### Compliance Management
```bash
# Add compliance task
legalops compliance add-task

# Check compliance status
legalops compliance status
```

### Compliance Features

- **GDPR Compliance**: Data protection and privacy controls
- **CCPA Compliance**: California Consumer Privacy Act support
- **HIPAA Compliance**: Healthcare data protection
- **SOX Compliance**: Financial reporting requirements
- **Contract Analysis**: Automated risk assessment
- **Template Generation**: Legal document templates
- **Task Management**: Compliance deadline tracking

## 🧪 Testing

### Run Tests
```bash
# Backend tests
npm test

# AI service tests
cd ai_service
python -m pytest

# LegalOps CLI tests
cd legalops-cli
npm test
```

### Test Coverage
```bash
# Generate coverage report
npm run test:coverage
```

## 📊 Monitoring

### Health Checks
```bash
# API health
curl http://localhost:3001/health

# AI service health
curl http://localhost:5000/health
```

### Metrics
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **Application Metrics**: Real-time performance data

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
NODE_ENV=development
PORT=3001
MONGODB_URI=mongodb://localhost:27017/ai_marketing_course
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_SECRET=your-jwt-secret
STRIPE_SECRET_KEY=your-stripe-secret
AI_SERVICE_URL=http://localhost:5000
```

#### AI Service (ai_service/.env)
```env
FLASK_ENV=development
PYTHONPATH=/app
MODEL_PATH=/app/models
DATA_PATH=/app/data
```

#### LegalOps CLI (legalops-cli/.env)
```env
LEGALOPS_DATA_DIR=~/.legalops
LEGALOPS_TEMPLATES_DIR=~/templates
LEGALOPS_CONTRACTS_DIR=~/contracts
```

## 🚀 Deployment

### Production Deployment

1. **Build for production**
```bash
npm run build
```

2. **Deploy with Docker**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Configure reverse proxy**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
    }
    
    location /api {
        proxy_pass http://localhost:3001;
    }
}
```

### AWS Deployment

1. **Deploy to AWS ECS**
```bash
aws ecs create-cluster --cluster-name ai-marketing-course
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

2. **Configure RDS and ElastiCache**
```bash
aws rds create-db-instance --db-instance-identifier ai-marketing-course-db
aws elasticache create-cache-cluster --cache-cluster-id ai-marketing-course-cache
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style
- Add tests for new features
- Update documentation
- Ensure all tests pass
- Follow semantic versioning

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://ai-marketing-course.com/docs](https://ai-marketing-course.com/docs)
- **Issues**: [GitHub Issues](https://github.com/ai-marketing-course/saas-platform/issues)
- **Email**: support@ai-marketing-course.com
- **Discord**: [AI Marketing Course Community](https://discord.gg/ai-marketing-course)

## 🏆 Acknowledgments

- Legal professionals who provided feedback
- AI/ML experts who contributed to the course content
- Open source community contributors
- Regulatory compliance experts
- Marketing professionals and industry leaders

---

**AI Marketing Course & SaaS Platform** - Transforming marketing education with AI-powered learning and comprehensive legal compliance tools.

*This platform is designed to provide educational content and should not be considered as legal advice. Always consult with qualified legal counsel for important legal matters.*