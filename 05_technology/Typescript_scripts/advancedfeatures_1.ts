import express from 'express';
import { advancedFeedbackProcessor } from '../services/advancedFeedbackProcessor';
import { machineLearningService } from '../services/machineLearningService';
import { realTimeNotificationService } from '../services/realTimeNotificationService';
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

    const insights = await advancedFeedbackProcessor.processAdvancedFeedback(feedback);
    
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

    const insights = await advancedFeedbackProcessor.processAdvancedFeedback(feedback);
    
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

    const insights = await advancedFeedbackProcessor.processAdvancedFeedback(feedback);
    
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

    const insights = await advancedFeedbackProcessor.processAdvancedFeedback(feedback);
    
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

    const insights = await advancedFeedbackProcessor.processAdvancedFeedback(feedback);
    
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

    const insights = await advancedFeedbackProcessor.processAdvancedFeedback(feedback);
    
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

// Machine Learning - Entrenar modelo
router.post('/ml/train', authenticateToken, async (req, res) => {
  try {
    const { modelType, trainingData } = req.body;
    
    if (!modelType || !trainingData) {
      return res.status(400).json({ error: 'modelType and trainingData are required' });
    }

    let model;
    
    switch (modelType) {
      case 'sentiment':
        model = await machineLearningService.trainSentimentModel(trainingData);
        break;
      case 'topic_classification':
        model = await machineLearningService.trainTopicClassificationModel(trainingData);
        break;
      case 'churn_prediction':
        model = await machineLearningService.trainChurnPredictionModel(trainingData);
        break;
      case 'clustering':
        model = await machineLearningService.trainCustomerClusteringModel(trainingData);
        break;
      case 'recommendation':
        model = await machineLearningService.trainRecommendationModel(trainingData);
        break;
      default:
        return res.status(400).json({ error: 'Invalid model type' });
    }
    
    res.json({
      success: true,
      data: model,
      message: 'Model training completed successfully'
    });
  } catch (error) {
    console.error('Error training model:', error);
    res.status(500).json({ error: 'Failed to train model' });
  }
});

// Machine Learning - Realizar predicción
router.post('/ml/predict', authenticateToken, async (req, res) => {
  try {
    const { modelId, input } = req.body;
    
    if (!modelId || !input) {
      return res.status(400).json({ error: 'modelId and input are required' });
    }

    const prediction = await machineLearningService.predict(modelId, input);
    
    res.json({
      success: true,
      data: prediction,
      message: 'Prediction completed successfully'
    });
  } catch (error) {
    console.error('Error making prediction:', error);
    res.status(500).json({ error: 'Failed to make prediction' });
  }
});

// Machine Learning - Análisis de sentimiento
router.post('/ml/sentiment-analysis', authenticateToken, async (req, res) => {
  try {
    const { content, language = 'es' } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }

    const analysis = await machineLearningService.analyzeSentimentML(content, language);
    
    res.json({
      success: true,
      data: analysis,
      message: 'Sentiment analysis completed'
    });
  } catch (error) {
    console.error('Error in sentiment analysis:', error);
    res.status(500).json({ error: 'Failed to analyze sentiment' });
  }
});

// Machine Learning - Clasificación de temas
router.post('/ml/topic-classification', authenticateToken, async (req, res) => {
  try {
    const { content, language = 'es' } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }

    const classification = await machineLearningService.classifyTopicsML(content, language);
    
    res.json({
      success: true,
      data: classification,
      message: 'Topic classification completed'
    });
  } catch (error) {
    console.error('Error in topic classification:', error);
    res.status(500).json({ error: 'Failed to classify topics' });
  }
});

// Machine Learning - Predicción de churn
router.post('/ml/churn-prediction', authenticateToken, async (req, res) => {
  try {
    const { feedback } = req.body;
    
    if (!feedback) {
      return res.status(400).json({ error: 'Feedback is required' });
    }

    const prediction = await machineLearningService.predictChurnML(feedback);
    
    res.json({
      success: true,
      data: prediction,
      message: 'Churn prediction completed'
    });
  } catch (error) {
    console.error('Error in churn prediction:', error);
    res.status(500).json({ error: 'Failed to predict churn' });
  }
});

// Machine Learning - Clustering de clientes
router.post('/ml/customer-clustering', authenticateToken, async (req, res) => {
  try {
    const { feedback } = req.body;
    
    if (!feedback || !Array.isArray(feedback)) {
      return res.status(400).json({ error: 'Feedback array is required' });
    }

    const clustering = await machineLearningService.clusterCustomersML(feedback);
    
    res.json({
      success: true,
      data: clustering,
      message: 'Customer clustering completed'
    });
  } catch (error) {
    console.error('Error in customer clustering:', error);
    res.status(500).json({ error: 'Failed to cluster customers' });
  }
});

// Machine Learning - Generar recomendaciones
router.post('/ml/recommendations', authenticateToken, async (req, res) => {
  try {
    const { feedback } = req.body;
    
    if (!feedback) {
      return res.status(400).json({ error: 'Feedback is required' });
    }

    const recommendations = await machineLearningService.generateRecommendationsML(feedback);
    
    res.json({
      success: true,
      data: recommendations,
      message: 'Recommendations generated'
    });
  } catch (error) {
    console.error('Error generating recommendations:', error);
    res.status(500).json({ error: 'Failed to generate recommendations' });
  }
});

// Machine Learning - Obtener modelos
router.get('/ml/models', authenticateToken, async (req, res) => {
  try {
    const models = machineLearningService.getModels();
    
    res.json({
      success: true,
      data: models,
      count: models.length
    });
  } catch (error) {
    console.error('Error fetching models:', error);
    res.status(500).json({ error: 'Failed to fetch models' });
  }
});

// Machine Learning - Obtener modelo por ID
router.get('/ml/models/:modelId', authenticateToken, async (req, res) => {
  try {
    const { modelId } = req.params;
    const model = machineLearningService.getModel(modelId);
    
    if (!model) {
      return res.status(404).json({ error: 'Model not found' });
    }

    res.json({
      success: true,
      data: model
    });
  } catch (error) {
    console.error('Error fetching model:', error);
    res.status(500).json({ error: 'Failed to fetch model' });
  }
});

// Notificaciones - Configurar canal
router.post('/notifications/channels', authenticateToken, async (req, res) => {
  try {
    const channelData = req.body;
    
    if (!channelData.type) {
      return res.status(400).json({ error: 'Channel type is required' });
    }

    const channel = await realTimeNotificationService.configureChannel(channelData);
    
    res.status(201).json({
      success: true,
      data: channel,
      message: 'Notification channel configured successfully'
    });
  } catch (error) {
    console.error('Error configuring notification channel:', error);
    res.status(500).json({ error: 'Failed to configure notification channel' });
  }
});

// Notificaciones - Crear plantilla
router.post('/notifications/templates', authenticateToken, async (req, res) => {
  try {
    const templateData = req.body;
    
    if (!templateData.name || !templateData.type) {
      return res.status(400).json({ error: 'Template name and type are required' });
    }

    const template = await realTimeNotificationService.createTemplate(templateData);
    
    res.status(201).json({
      success: true,
      data: template,
      message: 'Notification template created successfully'
    });
  } catch (error) {
    console.error('Error creating notification template:', error);
    res.status(500).json({ error: 'Failed to create notification template' });
  }
});

// Notificaciones - Enviar notificación
router.post('/notifications/send', authenticateToken, async (req, res) => {
  try {
    const { channelId, templateId, data } = req.body;
    
    if (!channelId || !templateId || !data) {
      return res.status(400).json({ error: 'channelId, templateId, and data are required' });
    }

    const notification = await realTimeNotificationService.sendNotification(channelId, templateId, data);
    
    res.json({
      success: true,
      data: notification,
      message: 'Notification sent successfully'
    });
  } catch (error) {
    console.error('Error sending notification:', error);
    res.status(500).json({ error: 'Failed to send notification' });
  }
});

// Notificaciones - Enviar resumen diario
router.post('/notifications/daily-summary', authenticateToken, async (req, res) => {
  try {
    await realTimeNotificationService.sendDailySummary();
    
    res.json({
      success: true,
      message: 'Daily summary sent successfully'
    });
  } catch (error) {
    console.error('Error sending daily summary:', error);
    res.status(500).json({ error: 'Failed to send daily summary' });
  }
});

// Notificaciones - Enviar reporte semanal
router.post('/notifications/weekly-report', authenticateToken, async (req, res) => {
  try {
    await realTimeNotificationService.sendWeeklyReport();
    
    res.json({
      success: true,
      message: 'Weekly report sent successfully'
    });
  } catch (error) {
    console.error('Error sending weekly report:', error);
    res.status(500).json({ error: 'Failed to send weekly report' });
  }
});

// Notificaciones - Obtener canales
router.get('/notifications/channels', authenticateToken, async (req, res) => {
  try {
    const channels = realTimeNotificationService.getChannels();
    
    res.json({
      success: true,
      data: channels,
      count: channels.length
    });
  } catch (error) {
    console.error('Error fetching notification channels:', error);
    res.status(500).json({ error: 'Failed to fetch notification channels' });
  }
});

// Notificaciones - Obtener plantillas
router.get('/notifications/templates', authenticateToken, async (req, res) => {
  try {
    const templates = realTimeNotificationService.getTemplates();
    
    res.json({
      success: true,
      data: templates,
      count: templates.length
    });
  } catch (error) {
    console.error('Error fetching notification templates:', error);
    res.status(500).json({ error: 'Failed to fetch notification templates' });
  }
});

// Notificaciones - Obtener estadísticas
router.get('/notifications/stats', authenticateToken, async (req, res) => {
  try {
    const stats = realTimeNotificationService.getNotificationStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching notification stats:', error);
    res.status(500).json({ error: 'Failed to fetch notification stats' });
  }
});

// Obtener insights consolidados
router.get('/insights/consolidated', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    const insights = await advancedFeedbackProcessor.getConsolidatedInsights(period as string);
    
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

export default router;
