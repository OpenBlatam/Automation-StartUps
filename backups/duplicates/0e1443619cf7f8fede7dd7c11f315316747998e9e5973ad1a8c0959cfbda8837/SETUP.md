# AI Marketing Course & SaaS - Setup Guide

## Prerequisites

Before setting up this project, ensure you have the following installed:

- **Node.js** (v18 or higher) - [Download here](https://nodejs.org/)
- **npm** (v9 or higher) - Comes with Node.js
- **PostgreSQL** (v14 or higher) - [Download here](https://www.postgresql.org/download/)
- **Git** - [Download here](https://git-scm.com/)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd frontier
```

### 2. Install Dependencies

```bash
# Install root dependencies
npm install

# Install server dependencies
cd saas/server
npm install

# Install client dependencies
cd ../client
npm install
```

### 3. Environment Setup

#### Server Environment

Create a `.env` file in `saas/server/`:

```env
# Database
DATABASE_URL="postgresql://username:password@localhost:5432/ai_marketing_saas"

# JWT
JWT_SECRET="your-super-secret-jwt-key-here"
JWT_EXPIRES_IN="7d"

# OpenAI
OPENAI_API_KEY="your-openai-api-key-here"

# Server
PORT=3001
NODE_ENV="development"

# Client URL
CLIENT_URL="http://localhost:3000"
```

#### Client Environment

Create a `.env` file in `saas/client/`:

```env
VITE_API_URL=http://localhost:3001/api
VITE_APP_NAME="AI Marketing SaaS"
```

### 4. Database Setup

#### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ai_marketing_saas;

# Exit psql
\q
```

#### Run Migrations

```bash
cd saas/server
npx prisma migrate dev
npx prisma generate
```

### 5. Start Development Servers

#### Option 1: Start Both Servers (Recommended)

From the root directory:

```bash
npm run dev
```

This will start both the backend (port 3001) and frontend (port 3000) servers.

#### Option 2: Start Servers Separately

**Terminal 1 - Backend:**
```bash
cd saas/server
npm run dev
```

**Terminal 2 - Frontend:**
```bash
cd saas/client
npm run dev
```

### 6. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:3001
- **API Health Check**: http://localhost:3001/health

## Detailed Setup Instructions

### Backend Setup (Node.js + Express + Prisma)

The backend is built with:
- **Express.js** - Web framework
- **TypeScript** - Type safety
- **Prisma** - Database ORM
- **PostgreSQL** - Database
- **JWT** - Authentication
- **OpenAI API** - AI content generation

#### Key Features:
- User authentication and management
- Content generation with AI
- Analytics and reporting
- Team collaboration
- Rate limiting and security

#### API Endpoints:

**Authentication:**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/logout` - User logout

**Content Generation:**
- `POST /api/content/generate` - Generate content
- `POST /api/content/generate-variations` - Generate multiple variations
- `POST /api/content/improve` - Improve existing content
- `GET /api/content/history` - Get content history
- `GET /api/content/:id` - Get specific content
- `DELETE /api/content/:id` - Delete content

**User Management:**
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `GET /api/users/usage` - Get usage statistics

**Analytics:**
- `GET /api/analytics/overview` - Get analytics overview
- `GET /api/analytics/content` - Get content analytics
- `GET /api/analytics/usage` - Get usage analytics

### Frontend Setup (React + TypeScript + Tailwind)

The frontend is built with:
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Redux Toolkit** - State management
- **React Hook Form** - Form handling

#### Key Features:
- Modern, responsive UI
- Content generation interface
- Content history and management
- Analytics dashboard
- User settings and profile
- Team collaboration tools

#### Pages:
- **Dashboard** - Overview and quick actions
- **Content Generator** - AI content creation
- **Content History** - Past generations
- **Analytics** - Performance metrics
- **Settings** - User preferences
- **Pricing** - Subscription plans

### Database Schema

The database includes the following main entities:

- **Users** - User accounts and profiles
- **Organizations** - Company/team management
- **Teams** - Team workspaces
- **ContentGenerations** - Generated content history
- **Campaigns** - Marketing campaigns
- **Analytics** - Performance metrics

## Course Content

### Module 1: AI Fundamentals
- **Lesson 1.1**: Introduction to AI
- **Lesson 1.2**: Machine Learning Basics
- **Lesson 1.3**: Natural Language Processing
- **Lesson 1.4**: Deep Learning Concepts

### Module 2: AI in Marketing
- **Lesson 2.1**: Marketing Automation
- **Lesson 2.2**: Content Generation
- **Lesson 2.3**: Personalization
- **Lesson 2.4**: Predictive Analytics

### Module 3: Practical Implementation
- **Lesson 3.1**: Building AI Tools
- **Lesson 3.2**: Platform Integration
- **Lesson 3.3**: Performance Measurement
- **Lesson 3.4**: ROI Optimization

## Development Workflow

### 1. Code Structure

```
frontier/
├── course/                 # Course content and materials
│   ├── module1/           # AI Fundamentals
│   ├── module2/           # AI in Marketing
│   ├── module3/           # Practical Implementation
│   └── resources/         # Additional resources
├── saas/                  # SaaS application
│   ├── server/            # Backend API
│   │   ├── src/
│   │   │   ├── routes/    # API routes
│   │   │   ├── services/  # Business logic
│   │   │   ├── middleware/ # Middleware functions
│   │   │   └── utils/     # Utility functions
│   │   └── prisma/        # Database schema
│   └── client/            # Frontend application
│       ├── src/
│       │   ├── components/ # React components
│       │   ├── pages/     # Page components
│       │   ├── services/  # API services
│       │   ├── store/     # Redux store
│       │   └── types/     # TypeScript types
└── docs/                  # Documentation
```

### 2. Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push to remote
git push origin feature/new-feature

# Create pull request
# After review, merge to main
```

### 3. Testing

```bash
# Run all tests
npm test

# Run server tests
cd saas/server
npm test

# Run client tests
cd saas/client
npm test
```

### 4. Building for Production

```bash
# Build everything
npm run build

# Build server only
cd saas/server
npm run build

# Build client only
cd saas/client
npm run build
```

## Deployment

### Environment Variables for Production

#### Server (.env.production):
```env
DATABASE_URL="postgresql://username:password@host:5432/ai_marketing_saas"
JWT_SECRET="production-secret-key"
OPENAI_API_KEY="your-openai-api-key"
NODE_ENV="production"
CLIENT_URL="https://your-domain.com"
```

#### Client (.env.production):
```env
VITE_API_URL=https://api.your-domain.com/api
VITE_APP_NAME="AI Marketing SaaS"
```

### Docker Deployment

```bash
# Build Docker images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Manual Deployment

1. **Build the application**:
   ```bash
   npm run build
   ```

2. **Deploy server**:
   - Upload `saas/server/dist/` to your server
   - Install dependencies: `npm install --production`
   - Start with PM2: `pm2 start dist/index.js`

3. **Deploy client**:
   - Upload `saas/client/dist/` to your web server
   - Configure web server to serve static files

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env
   - Ensure database exists

2. **OpenAI API Error**:
   - Verify OPENAI_API_KEY is correct
   - Check API quota and billing
   - Ensure internet connection

3. **Port Already in Use**:
   - Change PORT in .env file
   - Kill process using the port: `lsof -ti:3001 | xargs kill`

4. **Prisma Migration Error**:
   - Reset database: `npx prisma migrate reset`
   - Check database permissions
   - Verify schema syntax

### Getting Help

- Check the logs for error messages
- Review the documentation
- Search existing issues
- Create a new issue with detailed information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation

---

**Happy coding! 🚀**

