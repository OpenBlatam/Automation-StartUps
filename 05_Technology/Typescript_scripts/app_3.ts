import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import customerFeedbackRoutes from './routes/customerFeedback';
import advancedAnalyticsRoutes from './routes/advancedAnalytics';
import { consciousnessWebinarRoutes } from './routes/consciousnessWebinar';
import aiMLRoutes from './routes/aiML';
import aiInsightsRoutes from './routes/aiInsights';
import automationRoutes from './routes/automation';
import monitoringRoutes from './routes/monitoring';
import integrationRoutes from './routes/integrations';
import reportingRoutes from './routes/reporting';
import notificationRoutes from './routes/notifications';
import aiOptimizationRoutes from './routes/aiOptimization';
import advancedSecurityRoutes from './routes/advancedSecurity';
import performanceAnalyticsRoutes from './routes/performanceAnalytics';
import advancedWorkflowRoutes from './routes/advancedWorkflows';
import advancedDataProcessingRoutes from './routes/advancedDataProcessing';
import advancedCustomerJourneyRoutes from './routes/advancedCustomerJourney';
import advancedPredictiveAnalyticsRoutes from './routes/advancedPredictiveAnalytics';
import advancedPersonalizationRoutes from './routes/advancedPersonalization';
import advancedRecommendationRoutes from './routes/advancedRecommendations';
import advancedAITrainingRoutes from './routes/advancedAITraining';
import advancedExperimentRoutes from './routes/advancedExperiments';
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
    environment: process.env.NODE_ENV || 'development',
    features: {
      advancedAnalytics: true,
      realTimeAlerts: true,
      culturalAnalysis: true,
      emotionalIntelligence: true,
      predictiveMetrics: true,
      websocket: true,
      rateLimiting: true,
      spamDetection: true
    }
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

// Rutas de analytics avanzados
app.use('/api/advanced', 
  validateAnalyticsAccess,
  advancedAnalyticsRoutes
);

// Rutas de IA y ML
app.use('/api/ai', 
  validateAnalyticsAccess,
  aiMLRoutes
);

// Rutas de insights de IA
app.use('/api/insights', 
  validateAnalyticsAccess,
  aiInsightsRoutes
);

// Rutas de automatización
app.use('/api/automation', 
  validateAnalyticsAccess,
  automationRoutes
);

// Rutas de monitoreo
app.use('/api/monitoring', 
  validateAnalyticsAccess,
  monitoringRoutes
);

// Rutas de integraciones
app.use('/api/integrations', 
  validateAnalyticsAccess,
  integrationRoutes
);

// Rutas de reportes
app.use('/api/reports', 
  validateAnalyticsAccess,
  reportingRoutes
);

// Rutas de notificaciones
app.use('/api/notifications', 
  validateAnalyticsAccess,
  notificationRoutes
);

// Rutas de optimización de IA
app.use('/api/ai-optimization', 
  validateAnalyticsAccess,
  aiOptimizationRoutes
);

// Rutas de seguridad avanzada
app.use('/api/security', 
  validateAnalyticsAccess,
  advancedSecurityRoutes
);

// Rutas de analytics de rendimiento
app.use('/api/performance', 
  validateAnalyticsAccess,
  performanceAnalyticsRoutes
);

// Rutas de workflows avanzados
app.use('/api/workflows', 
  validateAnalyticsAccess,
  advancedWorkflowRoutes
);

// Rutas de procesamiento de datos avanzado
app.use('/api/data-processing', 
  validateAnalyticsAccess,
  advancedDataProcessingRoutes
);

// Rutas de journey del cliente avanzado
app.use('/api/customer-journey', 
  validateAnalyticsAccess,
  advancedCustomerJourneyRoutes
);

// Rutas de analytics predictivos avanzados
app.use('/api/predictive-analytics', 
  validateAnalyticsAccess,
  advancedPredictiveAnalyticsRoutes
);

// Rutas de personalización avanzada
app.use('/api/personalization', 
  validateAnalyticsAccess,
  advancedPersonalizationRoutes
);

// Rutas de recomendaciones avanzadas
app.use('/api/recommendations', 
  validateAnalyticsAccess,
  advancedRecommendationRoutes
);

// Rutas de entrenamiento de IA avanzado
app.use('/api/ai-training', 
  validateAnalyticsAccess,
  advancedAITrainingRoutes
);

// Rutas de experimentos avanzados
app.use('/api/experiments', 
  validateAnalyticsAccess,
  advancedExperimentRoutes
);

// Rutas de webinars de conciencia
app.use('/api/webinars', consciousnessWebinarRoutes);

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
      'GET /api/feedback/analytics',
      'GET /api/feedback/search',
      'GET /api/feedback/export/:format',
      'POST /api/advanced/feedback/advanced-analysis',
      'POST /api/advanced/feedback/emotional-intelligence',
      'POST /api/advanced/feedback/behavioral-patterns',
      'POST /api/advanced/feedback/cultural-analysis',
      'POST /api/advanced/feedback/predictive-metrics',
      'POST /api/advanced/feedback/actionable-recommendations',
      'GET /api/advanced/insights/consolidated',
      'GET /api/advanced/trends/emotional',
      'GET /api/advanced/patterns/cultural',
      'GET /api/advanced/risk/churn',
      'GET /api/advanced/opportunities/upsell',
      'GET /api/advanced/dashboard/advanced',
      'POST /api/ai/sentiment/advanced',
      'POST /api/ai/predictions/churn',
      'POST /api/ai/analyze/complete',
      'GET /api/insights/dashboard',
      'GET /api/insights/trends',
      'GET /api/insights/anomalies',
      'GET /api/insights/opportunities',
      'GET /api/automation/dashboard',
      'GET /api/automation/rules',
      'POST /api/automation/rules',
      'GET /api/monitoring/dashboard',
      'GET /api/monitoring/health',
      'GET /api/monitoring/alerts',
      'GET /api/integrations',
      'POST /api/integrations',
      'GET /api/integrations/templates',
      'GET /api/reports',
      'POST /api/reports',
      'POST /api/reports/:id/generate',
      'GET /api/reports/templates',
      'GET /api/notifications/configs',
      'POST /api/notifications/send',
      'GET /api/notifications/templates',
      'GET /api/ai-optimization/configs',
      'POST /api/ai-optimization/optimize/:configId',
      'GET /api/security/threats',
      'GET /api/security/audits',
      'GET /api/performance/metrics',
      'GET /api/performance/alerts',
      'POST /api/performance/reports/generate',
      'GET /api/workflows',
      'POST /api/workflows/:id/execute',
      'GET /api/data-processing/pipelines',
      'POST /api/data-processing/pipelines/:id/execute',
      'GET /api/customer-journey',
      'POST /api/customer-journey',
      'GET /api/predictive-analytics/models',
      'POST /api/predictive-analytics/predict',
      'GET /api/personalization/profiles',
      'POST /api/personalization/profiles',
      'GET /api/recommendations/:customerId',
      'POST /api/recommendations/generate',
      'GET /api/ai-training/datasets',
      'POST /api/ai-training/jobs',
      'GET /api/experiments',
      'POST /api/experiments',
      'GET /api/webinars/active',
      'POST /api/webinars/create'
    ]
  });
});

export default app;