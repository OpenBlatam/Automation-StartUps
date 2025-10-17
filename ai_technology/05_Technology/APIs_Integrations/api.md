# API Documentation

## Overview

The Gamified AI Marketing Training Platform provides a comprehensive REST API for all platform functionality. The API follows RESTful principles and uses JSON for data exchange.

## Base URL

```
Production: https://api.ai-marketing-training.com/v1
Staging: https://staging-api.ai-marketing-training.com/v1
Development: http://localhost:3000/api/v1
```

## Authentication

All API requests require authentication using JWT tokens.

### Getting an Access Token

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
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600,
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "learner"
    }
  }
}
```

### Using the Access Token

Include the token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## API Endpoints

### Authentication Endpoints

#### POST /auth/login
Authenticate user and get access token.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "string",
    "refresh_token": "string",
    "expires_in": 3600,
    "user": {
      "id": "string",
      "email": "string",
      "name": "string",
      "role": "string",
      "avatar": "string",
      "created_at": "2023-01-01T00:00:00Z"
    }
  }
}
```

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "string",
  "password": "string",
  "name": "string",
  "role": "learner|instructor|admin"
}
```

#### POST /auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

#### POST /auth/logout
Logout user and invalidate tokens.

### User Management Endpoints

#### GET /users/profile
Get current user profile.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "email": "string",
    "name": "string",
    "role": "string",
    "avatar": "string",
    "bio": "string",
    "skills": ["string"],
    "achievements": [
      {
        "id": "string",
        "name": "string",
        "description": "string",
        "earned_at": "2023-01-01T00:00:00Z",
        "badge_url": "string"
      }
    ],
    "stats": {
      "total_points": 1250,
      "level": 5,
      "courses_completed": 3,
      "streak_days": 7
    }
  }
}
```

#### PUT /users/profile
Update user profile.

**Request Body:**
```json
{
  "name": "string",
  "bio": "string",
  "avatar": "string"
}
```

#### GET /users/{userId}/progress
Get user learning progress.

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "string",
    "courses": [
      {
        "course_id": "string",
        "title": "string",
        "progress_percentage": 75,
        "completed_modules": 6,
        "total_modules": 8,
        "last_accessed": "2023-01-01T00:00:00Z",
        "estimated_completion": "2023-01-15T00:00:00Z"
      }
    ],
    "overall_progress": {
      "total_courses": 10,
      "completed_courses": 3,
      "in_progress_courses": 2,
      "total_points": 1250,
      "current_level": 5
    }
  }
}
```

### Course Management Endpoints

#### GET /courses
Get list of available courses.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `category` (optional): Filter by category
- `difficulty` (optional): Filter by difficulty level
- `search` (optional): Search in title and description

**Response:**
```json
{
  "success": true,
  "data": {
    "courses": [
      {
        "id": "string",
        "title": "string",
        "description": "string",
        "category": "string",
        "difficulty": "beginner|intermediate|advanced",
        "duration_hours": 10,
        "instructor": {
          "id": "string",
          "name": "string",
          "avatar": "string"
        },
        "thumbnail": "string",
        "rating": 4.5,
        "enrollment_count": 1250,
        "price": 99.99,
        "is_enrolled": true,
        "progress": 75
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "pages": 5
    }
  }
}
```

#### GET /courses/{courseId}
Get detailed course information.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "title": "string",
    "description": "string",
    "category": "string",
    "difficulty": "string",
    "duration_hours": 10,
    "instructor": {
      "id": "string",
      "name": "string",
      "avatar": "string",
      "bio": "string"
    },
    "modules": [
      {
        "id": "string",
        "title": "string",
        "description": "string",
        "type": "video|text|interactive|assessment",
        "duration_minutes": 30,
        "is_completed": false,
        "is_locked": false,
        "order": 1
      }
    ],
    "prerequisites": ["string"],
    "learning_objectives": ["string"],
    "certificate_available": true,
    "enrollment_count": 1250,
    "rating": 4.5,
    "reviews_count": 150
  }
}
```

#### POST /courses/{courseId}/enroll
Enroll in a course.

**Response:**
```json
{
  "success": true,
  "data": {
    "enrollment_id": "string",
    "course_id": "string",
    "user_id": "string",
    "enrolled_at": "2023-01-01T00:00:00Z",
    "access_expires_at": "2024-01-01T00:00:00Z"
  }
}
```

### Content Endpoints

#### GET /courses/{courseId}/modules/{moduleId}/content
Get module content.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "title": "string",
    "type": "video|text|interactive|assessment",
    "content": {
      "video_url": "string",
      "transcript": "string",
      "text_content": "string",
      "interactive_elements": [
        {
          "type": "quiz|simulation|ai_tool",
          "data": {}
        }
      ]
    },
    "attachments": [
      {
        "id": "string",
        "name": "string",
        "url": "string",
        "type": "pdf|doc|image"
      }
    ],
    "estimated_duration": 30
  }
}
```

#### POST /courses/{courseId}/modules/{moduleId}/complete
Mark module as completed.

**Request Body:**
```json
{
  "time_spent": 1800,
  "notes": "string"
}
```

### Gamification Endpoints

#### GET /gamification/leaderboard
Get current leaderboard.

**Query Parameters:**
- `type` (optional): `global|course|monthly|weekly`
- `course_id` (optional): Filter by specific course
- `limit` (optional): Number of entries (default: 50)

**Response:**
```json
{
  "success": true,
  "data": {
    "leaderboard": [
      {
        "rank": 1,
        "user": {
          "id": "string",
          "name": "string",
          "avatar": "string"
        },
        "points": 2500,
        "level": 8,
        "badges": ["string"]
      }
    ],
    "user_rank": {
      "rank": 15,
      "points": 1200,
      "level": 5
    }
  }
}
```

#### GET /gamification/achievements
Get user achievements.

**Response:**
```json
{
  "success": true,
  "data": {
    "earned": [
      {
        "id": "string",
        "name": "string",
        "description": "string",
        "badge_url": "string",
        "earned_at": "2023-01-01T00:00:00Z",
        "points": 100
      }
    ],
    "available": [
      {
        "id": "string",
        "name": "string",
        "description": "string",
        "badge_url": "string",
        "points": 100,
        "progress": 75,
        "requirements": "Complete 5 courses"
      }
    ]
  }
}
```

#### GET /gamification/stats
Get user gamification statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_points": 1250,
    "current_level": 5,
    "points_to_next_level": 250,
    "streak_days": 7,
    "longest_streak": 15,
    "badges_earned": 12,
    "courses_completed": 3,
    "hours_learned": 25.5,
    "rank": 15
  }
}
```

### AI Tool Integration Endpoints

#### POST /ai-tools/generate-content
Generate content using AI tools.

**Request Body:**
```json
{
  "tool": "copyai|jasper|openai",
  "prompt": "string",
  "content_type": "email|social|blog|ad",
  "parameters": {
    "tone": "professional|casual|creative",
    "length": "short|medium|long",
    "target_audience": "string"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "content": "string",
    "variations": ["string"],
    "metadata": {
      "tool_used": "string",
      "generation_time": 2.5,
      "confidence_score": 0.85
    }
  }
}
```

#### GET /ai-tools/history
Get AI tool usage history.

**Response:**
```json
{
  "success": true,
  "data": {
    "history": [
      {
        "id": "string",
        "tool": "string",
        "prompt": "string",
        "result": "string",
        "created_at": "2023-01-01T00:00:00Z",
        "rating": 4
      }
    ],
    "usage_stats": {
      "total_generations": 50,
      "favorite_tool": "copyai",
      "average_rating": 4.2
    }
  }
}
```

### Assessment Endpoints

#### GET /assessments/{assessmentId}
Get assessment details.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "title": "string",
    "description": "string",
    "type": "quiz|project|peer_review",
    "questions": [
      {
        "id": "string",
        "type": "multiple_choice|text|file_upload",
        "question": "string",
        "options": ["string"],
        "points": 10
      }
    ],
    "time_limit": 1800,
    "attempts_allowed": 3,
    "passing_score": 70
  }
}
```

#### POST /assessments/{assessmentId}/submit
Submit assessment answers.

**Request Body:**
```json
{
  "answers": [
    {
      "question_id": "string",
      "answer": "string",
      "file_urls": ["string"]
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "submission_id": "string",
    "score": 85,
    "passed": true,
    "feedback": "string",
    "correct_answers": [
      {
        "question_id": "string",
        "correct_answer": "string",
        "explanation": "string"
      }
    ]
  }
}
```

### Analytics Endpoints

#### GET /analytics/dashboard
Get user analytics dashboard data.

**Response:**
```json
{
  "success": true,
  "data": {
    "learning_progress": {
      "courses_completed": 3,
      "hours_learned": 25.5,
      "current_streak": 7,
      "average_score": 87.5
    },
    "skill_development": [
      {
        "skill": "string",
        "level": 5,
        "progress": 75,
        "last_practiced": "2023-01-01T00:00:00Z"
      }
    ],
    "ai_tool_usage": {
      "total_generations": 50,
      "most_used_tool": "copyai",
      "success_rate": 0.85
    },
    "achievements": {
      "recent": ["string"],
      "upcoming": ["string"]
    }
  }
}
```

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

## Rate Limiting

API requests are rate limited to prevent abuse:

- **Authenticated users**: 1000 requests per hour
- **Unauthenticated users**: 100 requests per hour
- **AI tool endpoints**: 50 requests per hour

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## SDKs and Libraries

Official SDKs are available for:

- **JavaScript/Node.js**: `npm install ai-marketing-training-sdk`
- **Python**: `pip install ai-marketing-training`
- **PHP**: `composer require ai-marketing-training/sdk`
- **Go**: `go get github.com/ai-marketing-training/go-sdk`

## Webhooks

The API supports webhooks for real-time notifications:

### Available Events

- `user.enrolled` - User enrolls in a course
- `course.completed` - User completes a course
- `achievement.earned` - User earns an achievement
- `assessment.submitted` - Assessment is submitted

### Webhook Configuration

```http
POST /webhooks
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "url": "https://your-app.com/webhooks",
  "events": ["user.enrolled", "course.completed"],
  "secret": "your-webhook-secret"
}
```

## API Versioning

The API uses URL versioning. Current version is `v1`:

```
https://api.ai-marketing-training.com/v1/endpoint
```

Breaking changes will result in a new version (e.g., `v2`). Non-breaking changes will be made to the current version.

## Support

For API support:

- **Documentation**: https://docs.ai-marketing-training.com
- **Status Page**: https://status.ai-marketing-training.com
- **Support Email**: api-support@ai-marketing-training.com
- **GitHub Issues**: https://github.com/ai-marketing-training/api/issues









