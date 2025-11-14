const express = require('express');
const http = require('http');
const dotenv = require('dotenv');
const cors = require('cors');
const morgan = require('morgan');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');

// Load environment variables
dotenv.config();

// Import services
const connectDB = require('./config/db');
const errorHandler = require('./middleware/errorHandler');
const securityService = require('./services/securityService');
const realTimeService = require('./services/realTimeService');
const notificationService = require('./services/notificationService');
const automationService = require('./services/automationService');

// Import routes
const authRoutes = require('./routes/auth');
const contentRoutes = require('./routes/content');
const templateRoutes = require('./routes/templates');
const automationRoutes = require('./routes/automation');
const collaborationRoutes = require('./routes/collaboration');
const integrationRoutes = require('./routes/integrations');
const notificationRoutes = require('./routes/notifications');
const optimizationRoutes = require('./routes/optimization');
const performanceRoutes = require('./routes/performance');
const abTestingRoutes = require('./routes/abTesting');
const personalizationRoutes = require('./routes/personalization');
const aiInsightsRoutes = require('./routes/aiInsights');
const contentStrategyRoutes = require('./routes/contentStrategy');
const contentAnalysisRoutes = require('./routes/contentAnalysis');
const multimediaContentRoutes = require('./routes/multimediaContent');
const advancedAutomationRoutes = require('./routes/advancedAutomation');

const app = express();
const server = http.createServer(app);

// Initialize services
async function initializeServices() {
  try {
    await connectDB();
    await securityService.initialize();
    await notificationService.initialize();
    await automationService.initialize();
    realTimeService.initialize(server);
    console.log('All services initialized successfully');
  } catch (error) {
    console.error('Failed to initialize services:', error);
    process.exit(1);
  }
}

// Security middleware
app.use(securityService.createSecurityHeaders());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: {
    success: false,
    message: 'Too many requests from this IP, please try again later.'
  },
  standardHeaders: true,
  legacyHeaders: false
});
app.use(limiter);

// CORS configuration
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
}));

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Compression middleware
app.use(compression());

// Logging middleware
if (process.env.NODE_ENV === 'development') {
  app.use(morgan('dev'));
} else {
  app.use(morgan('combined'));
}

// Health check endpoint
app.get('/api/health', async (req, res) => {
  try {
    const health = {
      status: 'OK',
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version || '2.0.0',
      services: {
        database: 'OK',
        redis: 'OK',
        openai: 'OK',
        realtime: 'OK',
        notifications: 'OK',
        automation: 'OK',
        security: 'OK'
      },
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      environment: process.env.NODE_ENV
    };

    res.status(200).json(health);
  } catch (error) {
    res.status(503).json({
      status: 'ERROR',
      timestamp: new Date().toISOString(),
      error: error.message
    });
  }
});

// API routes
app.use('/api/auth', authRoutes);
app.use('/api/content', contentRoutes);
app.use('/api/templates', templateRoutes);
app.use('/api/automation', automationRoutes);
app.use('/api/collaboration', collaborationRoutes);
app.use('/api/integrations', integrationRoutes);
app.use('/api/notifications', notificationRoutes);
app.use('/api/optimization', optimizationRoutes);
app.use('/api/performance', performanceRoutes);
app.use('/api/ab-testing', abTestingRoutes);
app.use('/api/personalization', personalizationRoutes);
app.use('/api/ai-insights', aiInsightsRoutes);
app.use('/api/content-strategy', contentStrategyRoutes);
app.use('/api/content-analysis', contentAnalysisRoutes);
app.use('/api/multimedia', multimediaContentRoutes);
app.use('/api/advanced-automation', advancedAutomationRoutes);

// Serve static files in production
if (process.env.NODE_ENV === 'production') {
  app.use(express.static('client/build'));
  
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'client/build/index.html'));
  });
}

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    message: 'Route not found',
    path: req.originalUrl
  });
});

// Global error handler
app.use(errorHandler);

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Process terminated');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully');
  server.close(() => {
    console.log('Process terminated');
    process.exit(0);
  });
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// Start server
const PORT = process.env.PORT || 5000;

async function startServer() {
  try {
    await initializeServices();
    
    server.listen(PORT, () => {
      console.log(`🚀 Server running on port ${PORT}`);
      console.log(`📊 Environment: ${process.env.NODE_ENV}`);
      console.log(`🔗 Frontend URL: ${process.env.FRONTEND_URL || 'http://localhost:3000'}`);
      console.log(`💾 Database: ${process.env.MONGODB_URI ? 'Connected' : 'Not configured'}`);
      console.log(`🤖 OpenAI: ${process.env.OPENAI_API_KEY ? 'Configured' : 'Not configured'}`);
      console.log(`📧 Email: ${process.env.EMAIL_HOST ? 'Configured' : 'Not configured'}`);
      console.log(`🔒 Security: ${securityService.isInitialized ? 'Active' : 'Inactive'}`);
      console.log(`⚡ Real-time: ${realTimeService.isInitialized ? 'Active' : 'Inactive'}`);
      console.log(`🔔 Notifications: ${notificationService.isInitialized ? 'Active' : 'Inactive'}`);
      console.log(`🤖 Automation: ${automationService.isInitialized ? 'Active' : 'Inactive'}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

startServer();

module.exports = app;