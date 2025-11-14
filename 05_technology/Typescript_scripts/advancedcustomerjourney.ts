import express from 'express';
import { advancedCustomerJourneyService } from '../services/advancedCustomerJourneyService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener journeys
router.get('/', authenticateToken, (req, res) => {
  try {
    const { limit = 50, status, stage, customerId } = req.query;
    
    let journeys = advancedCustomerJourneyService.getJourneys(parseInt(limit as string));
    
    if (status) {
      journeys = journeys.filter(j => j.status === status);
    }
    
    if (stage) {
      journeys = journeys.filter(j => j.stage === stage);
    }
    
    if (customerId) {
      journeys = journeys.filter(j => j.customerId === customerId);
    }
    
    res.json({
      success: true,
      data: journeys,
      count: journeys.length
    });
  } catch (error) {
    console.error('Error fetching customer journeys:', error);
    res.status(500).json({ error: 'Failed to fetch customer journeys' });
  }
});

// Obtener journey específico
router.get('/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const journey = advancedCustomerJourneyService.getJourney(id);
    
    if (!journey) {
      return res.status(404).json({ error: 'Customer journey not found' });
    }
    
    res.json({
      success: true,
      data: journey
    });
  } catch (error) {
    console.error('Error fetching customer journey:', error);
    res.status(500).json({ error: 'Failed to fetch customer journey' });
  }
});

// Crear journey
router.post('/', authenticateToken, (req, res) => {
  try {
    const { customerId, customerEmail, journeyName, templateId } = req.body;
    
    if (!customerId || !customerEmail || !journeyName) {
      return res.status(400).json({ 
        error: 'Missing required fields: customerId, customerEmail, journeyName' 
      });
    }
    
    const journeyId = advancedCustomerJourneyService.createJourney(
      customerId, 
      customerEmail, 
      journeyName, 
      templateId
    );
    
    res.status(201).json({
      success: true,
      data: { id: journeyId },
      message: 'Customer journey created successfully'
    });
  } catch (error) {
    console.error('Error creating customer journey:', error);
    res.status(500).json({ error: 'Failed to create customer journey' });
  }
});

// Agregar touchpoint
router.post('/:id/touchpoints', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const touchpointData = req.body;
    
    if (!touchpointData.type || !touchpointData.channel || !touchpointData.content) {
      return res.status(400).json({ 
        error: 'Missing required fields: type, channel, content' 
      });
    }
    
    advancedCustomerJourneyService.addTouchpoint(id, touchpointData);
    
    res.json({
      success: true,
      message: 'Touchpoint added successfully'
    });
  } catch (error) {
    console.error('Error adding touchpoint:', error);
    res.status(500).json({ error: 'Failed to add touchpoint' });
  }
});

// Obtener templates
router.get('/templates/list', authenticateToken, (req, res) => {
  try {
    const templates = advancedCustomerJourneyService.getTemplates();
    
    res.json({
      success: true,
      data: templates,
      count: templates.length
    });
  } catch (error) {
    console.error('Error fetching journey templates:', error);
    res.status(500).json({ error: 'Failed to fetch journey templates' });
  }
});

// Obtener estadísticas
router.get('/stats/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedCustomerJourneyService.getStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching journey stats:', error);
    res.status(500).json({ error: 'Failed to fetch journey stats' });
  }
});

// Obtener dashboard
router.get('/dashboard/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedCustomerJourneyService.getStats();
    const journeys = advancedCustomerJourneyService.getJourneys(20);
    const templates = advancedCustomerJourneyService.getTemplates();
    
    const dashboard = {
      overview: {
        totalJourneys: stats.totalJourneys,
        activeJourneys: stats.activeJourneys,
        completedJourneys: stats.completedJourneys,
        churnedJourneys: stats.churnedJourneys,
        averageChurnRisk: stats.averageChurnRisk,
        averageSatisfaction: stats.averageSatisfaction,
        totalInsights: stats.totalInsights,
        totalRecommendations: stats.totalRecommendations
      },
      stageDistribution: journeys.reduce((acc, journey) => {
        acc[journey.stage] = (acc[journey.stage] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      recentJourneys: journeys.slice(0, 10),
      templates: templates,
      performance: {
        completionRate: stats.totalJourneys > 0 
          ? (stats.completedJourneys / stats.totalJourneys) * 100 
          : 0,
        churnRate: stats.totalJourneys > 0 
          ? (stats.churnedJourneys / stats.totalJourneys) * 100 
          : 0,
        averageSatisfaction: stats.averageSatisfaction,
        averageChurnRisk: stats.averageChurnRisk
      }
    };
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    console.error('Error fetching journey dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch journey dashboard' });
  }
});

// Obtener insights de journey
router.get('/:id/insights', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const journey = advancedCustomerJourneyService.getJourney(id);
    
    if (!journey) {
      return res.status(404).json({ error: 'Customer journey not found' });
    }
    
    res.json({
      success: true,
      data: {
        insights: journey.insights,
        recommendations: journey.recommendations,
        metrics: journey.metrics
      }
    });
  } catch (error) {
    console.error('Error fetching journey insights:', error);
    res.status(500).json({ error: 'Failed to fetch journey insights' });
  }
});

// Obtener timeline de journey
router.get('/:id/timeline', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const journey = advancedCustomerJourneyService.getJourney(id);
    
    if (!journey) {
      return res.status(404).json({ error: 'Customer journey not found' });
    }
    
    // Crear timeline combinando touchpoints y eventos
    const timeline = [
      ...journey.touchpoints.map(tp => ({
        id: tp.id,
        type: 'touchpoint',
        title: `${tp.type} - ${tp.channel}`,
        description: tp.content,
        timestamp: tp.timestamp,
        sentiment: tp.sentiment,
        engagement: tp.engagement,
        metadata: tp.metadata
      })),
      ...journey.timeline.map(event => ({
        id: event.id,
        type: event.type,
        title: event.title,
        description: event.description,
        timestamp: event.timestamp,
        value: event.value,
        metadata: event.metadata
      }))
    ].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
    
    res.json({
      success: true,
      data: timeline
    });
  } catch (error) {
    console.error('Error fetching journey timeline:', error);
    res.status(500).json({ error: 'Failed to fetch journey timeline' });
  }
});

// Obtener métricas de journey
router.get('/:id/metrics', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const journey = advancedCustomerJourneyService.getJourney(id);
    
    if (!journey) {
      return res.status(404).json({ error: 'Customer journey not found' });
    }
    
    const metrics = {
      ...journey.metrics,
      stageProgression: journey.metrics.stageProgression.map(stage => ({
        ...stage,
        duration: Math.round(stage.duration * 100) / 100
      }))
    };
    
    res.json({
      success: true,
      data: metrics
    });
  } catch (error) {
    console.error('Error fetching journey metrics:', error);
    res.status(500).json({ error: 'Failed to fetch journey metrics' });
  }
});

// Obtener análisis de journey
router.get('/:id/analysis', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const journey = advancedCustomerJourneyService.getJourney(id);
    
    if (!journey) {
      return res.status(404).json({ error: 'Customer journey not found' });
    }
    
    const analysis = {
      journey: {
        id: journey.id,
        customerId: journey.customerId,
        customerEmail: journey.customerEmail,
        journeyName: journey.journeyName,
        stage: journey.stage,
        status: journey.status,
        createdAt: journey.createdAt,
        updatedAt: journey.updatedAt,
        lastActivityAt: journey.lastActivityAt
      },
      metrics: journey.metrics,
      insights: journey.insights,
      recommendations: journey.recommendations,
      touchpoints: journey.touchpoints,
      timeline: journey.timeline
    };
    
    res.json({
      success: true,
      data: analysis
    });
  } catch (error) {
    console.error('Error fetching journey analysis:', error);
    res.status(500).json({ error: 'Failed to fetch journey analysis' });
  }
});

// Obtener journeys por etapa
router.get('/stage/:stage', authenticateToken, (req, res) => {
  try {
    const { stage } = req.params;
    const { limit = 50 } = req.query;
    
    const journeys = advancedCustomerJourneyService.getJourneys(parseInt(limit as string))
      .filter(j => j.stage === stage);
    
    res.json({
      success: true,
      data: journeys,
      count: journeys.length
    });
  } catch (error) {
    console.error('Error fetching journeys by stage:', error);
    res.status(500).json({ error: 'Failed to fetch journeys by stage' });
  }
});

// Obtener journeys por estado
router.get('/status/:status', authenticateToken, (req, res) => {
  try {
    const { status } = req.params;
    const { limit = 50 } = req.query;
    
    const journeys = advancedCustomerJourneyService.getJourneys(parseInt(limit as string))
      .filter(j => j.status === status);
    
    res.json({
      success: true,
      data: journeys,
      count: journeys.length
    });
  } catch (error) {
    console.error('Error fetching journeys by status:', error);
    res.status(500).json({ error: 'Failed to fetch journeys by status' });
  }
});

// Obtener journeys de alto riesgo
router.get('/high-risk/list', authenticateToken, (req, res) => {
  try {
    const { limit = 20, threshold = 70 } = req.query;
    
    const journeys = advancedCustomerJourneyService.getJourneys(parseInt(limit as string))
      .filter(j => j.metrics.churnRisk >= parseInt(threshold as string))
      .sort((a, b) => b.metrics.churnRisk - a.metrics.churnRisk);
    
    res.json({
      success: true,
      data: journeys,
      count: journeys.length
    });
  } catch (error) {
    console.error('Error fetching high-risk journeys:', error);
    res.status(500).json({ error: 'Failed to fetch high-risk journeys' });
  }
});

// Obtener journeys de alta satisfacción
router.get('/high-satisfaction/list', authenticateToken, (req, res) => {
  try {
    const { limit = 20, threshold = 80 } = req.query;
    
    const journeys = advancedCustomerJourneyService.getJourneys(parseInt(limit as string))
      .filter(j => j.metrics.satisfactionScore >= parseInt(threshold as string))
      .sort((a, b) => b.metrics.satisfactionScore - a.metrics.satisfactionScore);
    
    res.json({
      success: true,
      data: journeys,
      count: journeys.length
    });
  } catch (error) {
    console.error('Error fetching high-satisfaction journeys:', error);
    res.status(500).json({ error: 'Failed to fetch high-satisfaction journeys' });
  }
});

// Obtener journeys por cliente
router.get('/customer/:customerId', authenticateToken, (req, res) => {
  try {
    const { customerId } = req.params;
    const { limit = 10 } = req.query;
    
    const journeys = advancedCustomerJourneyService.getJourneys(parseInt(limit as string))
      .filter(j => j.customerId === customerId);
    
    res.json({
      success: true,
      data: journeys,
      count: journeys.length
    });
  } catch (error) {
    console.error('Error fetching customer journeys:', error);
    res.status(500).json({ error: 'Failed to fetch customer journeys' });
  }
});

// Obtener reporte de journey
router.get('/:id/report', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const journey = advancedCustomerJourneyService.getJourney(id);
    
    if (!journey) {
      return res.status(404).json({ error: 'Customer journey not found' });
    }
    
    const report = {
      journey: {
        id: journey.id,
        customerId: journey.customerId,
        customerEmail: journey.customerEmail,
        journeyName: journey.journeyName,
        stage: journey.stage,
        status: journey.status,
        createdAt: journey.createdAt,
        updatedAt: journey.updatedAt,
        lastActivityAt: journey.lastActivityAt
      },
      summary: {
        totalTouchpoints: journey.metrics.totalTouchpoints,
        averageEngagement: journey.metrics.averageEngagement,
        timeInStage: journey.metrics.timeInStage,
        conversionRate: journey.metrics.conversionRate,
        churnRisk: journey.metrics.churnRisk,
        advocacyScore: journey.metrics.advocacyScore,
        satisfactionScore: journey.metrics.satisfactionScore,
        lastActivityDays: journey.metrics.lastActivityDays
      },
      insights: journey.insights,
      recommendations: journey.recommendations,
      touchpoints: journey.touchpoints,
      timeline: journey.timeline
    };
    
    res.json({
      success: true,
      data: report
    });
  } catch (error) {
    console.error('Error fetching journey report:', error);
    res.status(500).json({ error: 'Failed to fetch journey report' });
  }
});

export default router;






