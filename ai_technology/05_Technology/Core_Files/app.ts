import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { customerFeedbackRoutes } from './routes/customerFeedback';
import { dataIntegrationRoutes } from './routes/dataIntegration';
import { feedbackAnalyticsRoutes } from './routes/feedbackAnalytics';
import { consciousnessWebinarRoutes } from './routes/consciousnessWebinar';
import { feedbackController } from './controllers/feedbackController';
import { 
  validateFeedbackData, 
  enrichFeedbackData, 
  analyzeSentiment, 
  detectSpam, 
  rateLimitByIP,
  logFeedback,
  validateAnalyticsAccess,
  validateAdminAccess
} from './middleware/feedbackMiddleware';

const app = express();

// Middleware de seguridad
app.use(helmet());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true
}));

// Rate limiting global
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 1000, // máximo 1000 requests por IP por ventana
  message: {
    error: 'Too many requests from this IP, please try again later.'
  }
});
app.use(limiter);

// Rate limiting específico para feedback
const feedbackLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 100, // máximo 100 requests de feedback por IP por ventana
  message: {
    error: 'Too many feedback requests from this IP, please try again later.'
  }
});

// Middleware de parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Middleware de logging
app.use(logFeedback);

// Rutas de salud
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0',
    environment: process.env.NODE_ENV || 'development'
  });
});

// Rutas de feedback con middleware específico
app.use('/api/feedback', 
  feedbackLimiter,
  validateFeedbackData,
  enrichFeedbackData,
  analyzeSentiment,
  detectSpam,
  customerFeedbackRoutes
);

// Rutas de integración de datos
app.use('/api/integration', 
  validateAdminAccess,
  dataIntegrationRoutes
);

// Rutas de analytics
app.use('/api/analytics', 
  validateAnalyticsAccess,
  feedbackAnalyticsRoutes
);

// Rutas de webinars de conciencia
app.use('/api/webinars', consciousnessWebinarRoutes);

// Rutas de controlador
app.post('/api/feedback/process', 
  feedbackLimiter,
  validateFeedbackData,
  enrichFeedbackData,
  analyzeSentiment,
  detectSpam,
  feedbackController.processFeedback
);

app.post('/api/feedback/batch-process', 
  feedbackLimiter,
  validateAdminAccess,
  feedbackController.processBatchFeedback
);

app.get('/api/feedback/search', 
  validateAnalyticsAccess,
  feedbackController.getFeedbackByCriteria
);

app.get('/api/feedback/analytics', 
  validateAnalyticsAccess,
  feedbackController.getFeedbackAnalytics
);

app.get('/api/dashboard/metrics', 
  validateAnalyticsAccess,
  feedbackController.getDashboardMetrics
);

app.get('/api/analytics/advanced', 
  validateAnalyticsAccess,
  feedbackController.getAdvancedAnalytics
);

app.get('/api/analytics/regional/:region', 
  validateAnalyticsAccess,
  feedbackController.getRegionalInsights
);

app.get('/api/analytics/recommendations', 
  validateAnalyticsAccess,
  feedbackController.getAIRecommendations
);

app.post('/api/integration/sources', 
  validateAdminAccess,
  feedbackController.configureDataSource
);

app.post('/api/integration/sources/:sourceId/sync', 
  validateAdminAccess,
  feedbackController.syncDataSource
);

app.get('/api/integration/status', 
  validateAnalyticsAccess,
  feedbackController.getIntegrationStatus
);

app.get('/api/feedback/export/:format', 
  validateAnalyticsAccess,
  feedbackController.exportFeedback
);

app.get('/api/reports/generate', 
  validateAnalyticsAccess,
  feedbackController.generateReport
);

app.get('/api/feedback/:feedbackId', 
  validateAnalyticsAccess,
  feedbackController.getFeedbackById
);

app.put('/api/feedback/:feedbackId', 
  validateAdminAccess,
  feedbackController.updateFeedback
);

app.delete('/api/feedback/:feedbackId', 
  validateAdminAccess,
  feedbackController.deleteFeedback
);

app.get('/api/alerts', 
  validateAnalyticsAccess,
  feedbackController.getAlerts
);

app.get('/api/quick-actions', 
  validateAnalyticsAccess,
  feedbackController.getQuickActions
);

app.post('/api/cache/clear', 
  validateAdminAccess,
  feedbackController.clearCache
);

// Middleware de manejo de errores
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Error:', err);
  
  if (err.type === 'entity.parse.failed') {
    return res.status(400).json({
      error: 'Invalid JSON format',
      message: 'Please check your request body format'
    });
  }
  
  if (err.type === 'entity.too.large') {
    return res.status(413).json({
      error: 'Request too large',
      message: 'Request body exceeds size limit'
    });
  }
  
  res.status(500).json({
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
});

// Middleware para rutas no encontradas
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Route not found',
    message: `The requested route ${req.originalUrl} does not exist`,
    availableRoutes: [
      'GET /health',
      'POST /api/feedback/process',
      'POST /api/feedback/batch-process',
      'GET /api/feedback/search',
      'GET /api/feedback/analytics',
      'GET /api/dashboard/metrics',
      'GET /api/analytics/advanced',
      'GET /api/analytics/regional/:region',
      'GET /api/analytics/recommendations',
      'POST /api/integration/sources',
      'POST /api/integration/sources/:sourceId/sync',
      'GET /api/integration/status',
      'GET /api/feedback/export/:format',
      'GET /api/reports/generate',
      'GET /api/feedback/:feedbackId',
      'PUT /api/feedback/:feedbackId',
      'DELETE /api/feedback/:feedbackId',
      'GET /api/alerts',
      'GET /api/quick-actions',
      'POST /api/cache/clear'
    ]
  });
});

export default app;
