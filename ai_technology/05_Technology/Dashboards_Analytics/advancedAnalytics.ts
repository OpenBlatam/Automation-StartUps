import express from 'express';
import { advancedAnalyticsService } from '../services/advancedAnalyticsService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Análisis avanzado de feedback
router.post('/feedback/advanced-analysis', authenticateToken, async (req, res) => {
  try {
    const { feedbackId } = req.body;
    
    if (!feedbackId) {
      return res.status(400).json({ error: 'feedbackId is required' });
    }

    // Obtener feedback (en implementación real, desde base de datos)
    const feedback = {
      id: feedbackId,
      content: req.body.content || 'Sample feedback content',
      sentiment: req.body.sentiment || 'neutral',
      sentimentScore: req.body.sentimentScore || 0,
      region: req.body.region || 'LATAM',
      language: req.body.language || 'es',
      metadata: req.body.metadata || {}
    };

    const insights = await advancedAnalyticsService.processAdvancedFeedback(feedback);
    
    res.json({
      success: true,
      data: insights,
      message: 'Advanced analysis completed successfully'
    });
  } catch (error) {
    console.error('Error in advanced analysis:', error);
    res.status(500).json({ error: 'Failed to perform advanced analysis' });
  }
});

// Análisis de inteligencia emocional
router.post('/feedback/emotional-intelligence', authenticateToken, async (req, res) => {
  try {
    const { content, language = 'es', region = 'LATAM' } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }

    const feedback = {
      id: `temp_${Date.now()}`,
      content,
      sentiment: 'neutral',
      sentimentScore: 0,
      region,
      language,
      metadata: {}
    };

    const insights = await advancedAnalyticsService.processAdvancedFeedback(feedback);
    
    res.json({
      success: true,
      data: insights.emotionalIntelligence,
      message: 'Emotional intelligence analysis completed'
    });
  } catch (error) {
    console.error('Error in emotional intelligence analysis:', error);
    res.status(500).json({ error: 'Failed to analyze emotional intelligence' });
  }
});

// Análisis de patrones de comportamiento
router.post('/feedback/behavioral-patterns', authenticateToken, async (req, res) => {
  try {
    const { content, language = 'es', region = 'LATAM' } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }

    const feedback = {
      id: `temp_${Date.now()}`,
      content,
      sentiment: 'neutral',
      sentimentScore: 0,
      region,
      language,
      metadata: {}
    };

    const insights = await advancedAnalyticsService.processAdvancedFeedback(feedback);
    
    res.json({
      success: true,
      data: insights.behavioralPatterns,
      message: 'Behavioral patterns analysis completed'
    });
  } catch (error) {
    console.error('Error in behavioral patterns analysis:', error);
    res.status(500).json({ error: 'Failed to analyze behavioral patterns' });
  }
});

// Análisis cultural
router.post('/feedback/cultural-analysis', authenticateToken, async (req, res) => {
  try {
    const { content, language = 'es', region = 'LATAM' } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }

    const feedback = {
      id: `temp_${Date.now()}`,
      content,
      sentiment: 'neutral',
      sentimentScore: 0,
      region,
      language,
      metadata: {}
    };

    const insights = await advancedAnalyticsService.processAdvancedFeedback(feedback);
    
    res.json({
      success: true,
      data: insights.culturalAnalysis,
      message: 'Cultural analysis completed'
    });
  } catch (error) {
    console.error('Error in cultural analysis:', error);
    res.status(500).json({ error: 'Failed to analyze cultural context' });
  }
});

// Métricas predictivas
router.post('/feedback/predictive-metrics', authenticateToken, async (req, res) => {
  try {
    const { content, language = 'es', region = 'LATAM' } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }

    const feedback = {
      id: `temp_${Date.now()}`,
      content,
      sentiment: 'neutral',
      sentimentScore: 0,
      region,
      language,
      metadata: {}
    };

    const insights = await advancedAnalyticsService.processAdvancedFeedback(feedback);
    
    res.json({
      success: true,
      data: insights.predictiveMetrics,
      message: 'Predictive metrics calculated'
    });
  } catch (error) {
    console.error('Error in predictive metrics calculation:', error);
    res.status(500).json({ error: 'Failed to calculate predictive metrics' });
  }
});

// Recomendaciones accionables
router.post('/feedback/actionable-recommendations', authenticateToken, async (req, res) => {
  try {
    const { content, language = 'es', region = 'LATAM' } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }

    const feedback = {
      id: `temp_${Date.now()}`,
      content,
      sentiment: 'neutral',
      sentimentScore: 0,
      region,
      language,
      metadata: {}
    };

    const insights = await advancedAnalyticsService.processAdvancedFeedback(feedback);
    
    res.json({
      success: true,
      data: insights.actionableRecommendations,
      message: 'Actionable recommendations generated'
    });
  } catch (error) {
    console.error('Error in actionable recommendations generation:', error);
    res.status(500).json({ error: 'Failed to generate actionable recommendations' });
  }
});

// Generar alertas en tiempo real
router.post('/alerts/generate', authenticateToken, async (req, res) => {
  try {
    const { feedback } = req.body;
    
    if (!feedback) {
      return res.status(400).json({ error: 'Feedback is required' });
    }

    const alerts = await advancedAnalyticsService.generateRealTimeAlerts(feedback);
    
    res.json({
      success: true,
      data: alerts,
      message: 'Real-time alerts generated'
    });
  } catch (error) {
    console.error('Error generating alerts:', error);
    res.status(500).json({ error: 'Failed to generate alerts' });
  }
});

// Obtener insights consolidados
router.get('/insights/consolidated', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    const insights = await advancedAnalyticsService.getConsolidatedInsights(period as string);
    
    res.json({
      success: true,
      data: insights,
      period
    });
  } catch (error) {
    console.error('Error fetching consolidated insights:', error);
    res.status(500).json({ error: 'Failed to fetch consolidated insights' });
  }
});

// Análisis de tendencias emocionales
router.get('/trends/emotional', authenticateToken, async (req, res) => {
  try {
    const { period = '30d', region } = req.query;
    
    // Simular análisis de tendencias emocionales
    const emotionalTrends = {
      period,
      region: region || 'LATAM',
      trends: [
        {
          emotion: 'joy',
          trend: 'increasing',
          percentage: 15.2,
          confidence: 0.85
        },
        {
          emotion: 'frustration',
          trend: 'decreasing',
          percentage: -8.7,
          confidence: 0.92
        }
      ],
      insights: [
        'Los clientes muestran mayor satisfacción emocional',
        'Reducción significativa en frustración reportada'
      ]
    };
    
    res.json({
      success: true,
      data: emotionalTrends
    });
  } catch (error) {
    console.error('Error fetching emotional trends:', error);
    res.status(500).json({ error: 'Failed to fetch emotional trends' });
  }
});

// Análisis de patrones culturales
router.get('/patterns/cultural', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    // Simular análisis de patrones culturales
    const culturalPatterns = {
      period,
      patterns: [
        {
          region: 'MX',
          communicationStyle: 'direct',
          emotionalTone: 'warm',
          businessEtiquette: 'hierarchical',
          satisfactionScore: 4.2
        },
        {
          region: 'AR',
          communicationStyle: 'analytical',
          emotionalTone: 'intense',
          businessEtiquette: 'meritocratic',
          satisfactionScore: 4.5
        },
        {
          region: 'BR',
          communicationStyle: 'enthusiastic',
          emotionalTone: 'energetic',
          businessEtiquette: 'collaborative',
          satisfactionScore: 4.3
        }
      ],
      recommendations: [
        'Adaptar comunicación según estilo regional',
        'Considerar diferencias culturales en estrategias',
        'Personalizar experiencia por mercado'
      ]
    };
    
    res.json({
      success: true,
      data: culturalPatterns
    });
  } catch (error) {
    console.error('Error fetching cultural patterns:', error);
    res.status(500).json({ error: 'Failed to fetch cultural patterns' });
  }
});

// Análisis de riesgo de churn
router.get('/risk/churn', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    // Simular análisis de riesgo de churn
    const churnAnalysis = {
      period,
      overallRisk: 0.23,
      highRiskCustomers: 15,
      mediumRiskCustomers: 42,
      lowRiskCustomers: 143,
      riskFactors: [
        'Sentimiento negativo persistente',
        'Falta de engagement',
        'Problemas de soporte no resueltos'
      ],
      recommendations: [
        'Implementar programa de retención',
        'Contactar clientes de alto riesgo',
        'Mejorar procesos de soporte'
      ]
    };
    
    res.json({
      success: true,
      data: churnAnalysis
    });
  } catch (error) {
    console.error('Error fetching churn risk analysis:', error);
    res.status(500).json({ error: 'Failed to fetch churn risk analysis' });
  }
});

// Análisis de potencial de upsell
router.get('/opportunities/upsell', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    // Simular análisis de potencial de upsell
    const upsellAnalysis = {
      period,
      overallPotential: 0.67,
      highPotentialCustomers: 28,
      mediumPotentialCustomers: 56,
      lowPotentialCustomers: 116,
      opportunities: [
        'Clientes satisfechos con productos básicos',
        'Usuarios activos con bajo uso de features',
        'Clientes con feedback positivo sobre expansión'
      ],
      recommendations: [
        'Crear campañas de upsell personalizadas',
        'Ofrecer demos de features avanzadas',
        'Implementar programa de referidos'
      ]
    };
    
    res.json({
      success: true,
      data: upsellAnalysis
    });
  } catch (error) {
    console.error('Error fetching upsell opportunities:', error);
    res.status(500).json({ error: 'Failed to fetch upsell opportunities' });
  }
});

// Dashboard de métricas avanzadas
router.get('/dashboard/advanced', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    // Simular dashboard de métricas avanzadas
    const advancedDashboard = {
      period,
      emotionalIntelligence: {
        averageEmotionalStability: 0.78,
        empathyLevel: 0.65,
        emotionalIntensity: 0.72
      },
      behavioralPatterns: {
        directCommunication: 0.45,
        analyticalThinking: 0.38,
        collaborativeApproach: 0.52
      },
      culturalInsights: {
        relationshipImportance: 0.82,
        innovationAdoption: 0.67,
        riskTolerance: 0.54
      },
      predictiveMetrics: {
        churnRisk: 0.23,
        upsellPotential: 0.67,
        advocacyLikelihood: 0.71
      },
      alerts: [
        {
          type: 'sentiment_shift',
          severity: 'medium',
          message: 'Tendencia negativa detectada en región MX',
          timestamp: new Date()
        }
      ]
    };
    
    res.json({
      success: true,
      data: advancedDashboard
    });
  } catch (error) {
    console.error('Error fetching advanced dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch advanced dashboard' });
  }
});

export default router;
