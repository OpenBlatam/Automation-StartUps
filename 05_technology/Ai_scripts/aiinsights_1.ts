import express from 'express';
import { aiInsightsService } from '../services/aiInsightsService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener insights de IA
router.get('/insights', authenticateToken, (req, res) => {
  try {
    const { type, category, priority, status, limit } = req.query;
    const filters: any = {};
    
    if (type) filters.type = type;
    if (category) filters.category = category;
    if (priority) filters.priority = priority;
    if (status) filters.status = status;
    if (limit) filters.limit = parseInt(limit as string);
    
    const insights = aiInsightsService.getInsights(filters);
    
    res.json({
      success: true,
      data: insights,
      count: insights.length
    });
  } catch (error) {
    console.error('Error fetching AI insights:', error);
    res.status(500).json({ error: 'Failed to fetch AI insights' });
  }
});

// Obtener tendencias
router.get('/trends', authenticateToken, (req, res) => {
  try {
    const trends = aiInsightsService.getTrends();
    
    res.json({
      success: true,
      data: trends,
      count: trends.length
    });
  } catch (error) {
    console.error('Error fetching trends:', error);
    res.status(500).json({ error: 'Failed to fetch trends' });
  }
});

// Obtener anomalías
router.get('/anomalies', authenticateToken, (req, res) => {
  try {
    const { type, severity, limit } = req.query;
    const filters: any = {};
    
    if (type) filters.type = type;
    if (severity) filters.severity = severity;
    if (limit) filters.limit = parseInt(limit as string);
    
    const anomalies = aiInsightsService.getAnomalies(filters);
    
    res.json({
      success: true,
      data: anomalies,
      count: anomalies.length
    });
  } catch (error) {
    console.error('Error fetching anomalies:', error);
    res.status(500).json({ error: 'Failed to fetch anomalies' });
  }
});

// Obtener oportunidades de negocio
router.get('/opportunities', authenticateToken, (req, res) => {
  try {
    const { type, priority, status, limit } = req.query;
    const filters: any = {};
    
    if (type) filters.type = type;
    if (priority) filters.priority = priority;
    if (status) filters.status = status;
    if (limit) filters.limit = parseInt(limit as string);
    
    const opportunities = aiInsightsService.getOpportunities(filters);
    
    res.json({
      success: true,
      data: opportunities,
      count: opportunities.length
    });
  } catch (error) {
    console.error('Error fetching opportunities:', error);
    res.status(500).json({ error: 'Failed to fetch opportunities' });
  }
});

// Actualizar estado de insight
router.patch('/insights/:insightId/status', authenticateToken, (req, res) => {
  try {
    const { insightId } = req.params;
    const { status } = req.body;
    
    if (!status || !['active', 'acknowledged', 'resolved', 'dismissed'].includes(status)) {
      return res.status(400).json({ error: 'Invalid status value' });
    }
    
    const updated = aiInsightsService.updateInsightStatus(insightId, status);
    
    if (updated) {
      res.json({
        success: true,
        message: 'Insight status updated successfully'
      });
    } else {
      res.status(404).json({ error: 'Insight not found' });
    }
  } catch (error) {
    console.error('Error updating insight status:', error);
    res.status(500).json({ error: 'Failed to update insight status' });
  }
});

// Generar reporte de insights
router.get('/report', authenticateToken, (req, res) => {
  try {
    const report = aiInsightsService.generateInsightsReport();
    
    res.json({
      success: true,
      data: report
    });
  } catch (error) {
    console.error('Error generating insights report:', error);
    res.status(500).json({ error: 'Failed to generate insights report' });
  }
});

// Dashboard de insights
router.get('/dashboard', authenticateToken, (req, res) => {
  try {
    const insights = aiInsightsService.getInsights({ limit: 10 });
    const trends = aiInsightsService.getTrends();
    const anomalies = aiInsightsService.getAnomalies({ limit: 5 });
    const opportunities = aiInsightsService.getOpportunities({ limit: 5 });
    
    const dashboard = {
      insights: {
        total: insights.length,
        active: insights.filter(i => i.status === 'active').length,
        critical: insights.filter(i => i.priority === 'critical').length,
        recent: insights.slice(0, 5)
      },
      trends: {
        total: trends.length,
        significant: trends.filter(t => t.significance > 0.7).length,
        recent: trends.slice(0, 3)
      },
      anomalies: {
        total: anomalies.length,
        critical: anomalies.filter(a => a.severity === 'critical').length,
        recent: anomalies.slice(0, 3)
      },
      opportunities: {
        total: opportunities.length,
        highPriority: opportunities.filter(o => o.priority === 'high').length,
        recent: opportunities.slice(0, 3)
      }
    };
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    console.error('Error fetching insights dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch insights dashboard' });
  }
});

// Análisis de tendencias específico
router.post('/trends/analyze', authenticateToken, (req, res) => {
  try {
    const { metric, period = '30d' } = req.body;
    
    if (!metric) {
      return res.status(400).json({ error: 'Metric is required' });
    }
    
    // Simular análisis de tendencia específico
    const trendAnalysis = {
      metric,
      period,
      data: Array.from({ length: 30 }, (_, i) => ({
        timestamp: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000),
        value: Math.random() * 100 + i * 0.5
      })),
      trend: 'increasing',
      strength: 0.75,
      significance: 0.82,
      forecast: Array.from({ length: 7 }, (_, i) => ({
        timestamp: new Date(Date.now() + (i + 1) * 24 * 60 * 60 * 1000),
        value: 100 + i * 0.5,
        confidence: 0.9 - (i * 0.1)
      })),
      insights: [
        `Strong increasing trend detected in ${metric}`,
        `Trend strength: 75% with 82% significance`,
        `Forecast suggests continued growth over next 7 days`
      ]
    };
    
    res.json({
      success: true,
      data: trendAnalysis
    });
  } catch (error) {
    console.error('Error analyzing trend:', error);
    res.status(500).json({ error: 'Failed to analyze trend' });
  }
});

// Detección de anomalías específica
router.post('/anomalies/detect', authenticateToken, (req, res) => {
  try {
    const { metric, timeRange = '24h' } = req.body;
    
    if (!metric) {
      return res.status(400).json({ error: 'Metric is required' });
    }
    
    // Simular detección de anomalías específica
    const anomalies = [
      {
        id: `anomaly_${Date.now()}_1`,
        type: 'statistical',
        severity: 'medium',
        description: `Statistical anomaly detected in ${metric}`,
        detectedAt: new Date(),
        affectedMetrics: [metric],
        anomalyScore: 0.85,
        context: {
          metric,
          threshold: 0.8,
          actualValue: 0.95,
          expectedValue: 0.6
        },
        recommendations: [
          'Investigate the root cause of the anomaly',
          'Monitor for similar patterns',
          'Consider adjusting detection thresholds'
        ]
      }
    ];
    
    res.json({
      success: true,
      data: anomalies
    });
  } catch (error) {
    console.error('Error detecting anomalies:', error);
    res.status(500).json({ error: 'Failed to detect anomalies' });
  }
});

// Identificación de oportunidades específica
router.post('/opportunities/identify', authenticateToken, (req, res) => {
  try {
    const { type, criteria } = req.body;
    
    if (!type) {
      return res.status(400).json({ error: 'Opportunity type is required' });
    }
    
    // Simular identificación de oportunidades específica
    const opportunities = [
      {
        id: `opportunity_${type}_${Date.now()}`,
        type,
        priority: 'high',
        title: `${type.charAt(0).toUpperCase() + type.slice(1)} Opportunity Identified`,
        description: `High-value ${type} opportunity identified based on customer feedback analysis`,
        potentialValue: Math.random() * 50000 + 10000,
        confidence: 0.85,
        effort: 'medium',
        timeline: 'short_term',
        affectedCustomers: Array.from({ length: 5 }, (_, i) => `customer_${i + 1}`),
        successFactors: [
          'High customer satisfaction scores',
          'Positive sentiment trends',
          'Strong engagement metrics',
          'Favorable market conditions'
        ],
        risks: [
          'Competitive pressure',
          'Resource constraints',
          'Market volatility',
          'Timing sensitivity'
        ],
        actionPlan: {
          steps: [
            'Analyze target customer segment',
            'Develop customized offer',
            'Execute targeted campaign',
            'Monitor and optimize results'
          ],
          resources: ['Marketing team', 'Sales team', 'Analytics team', 'Product team'],
          timeline: '2-4 weeks',
          success_metrics: ['Conversion rate', 'Revenue impact', 'Customer satisfaction', 'ROI']
        },
        timestamp: new Date(),
        status: 'identified'
      }
    ];
    
    res.json({
      success: true,
      data: opportunities
    });
  } catch (error) {
    console.error('Error identifying opportunities:', error);
    res.status(500).json({ error: 'Failed to identify opportunities' });
  }
});

// Análisis predictivo
router.post('/predictive/analyze', authenticateToken, (req, res) => {
  try {
    const { metrics, timeHorizon = '30d' } = req.body;
    
    if (!metrics || !Array.isArray(metrics)) {
      return res.status(400).json({ error: 'Metrics array is required' });
    }
    
    // Simular análisis predictivo
    const predictions = metrics.map((metric: string) => ({
      metric,
      currentValue: Math.random() * 100,
      predictedValue: Math.random() * 100 + 10,
      confidence: Math.random() * 0.4 + 0.6,
      trend: Math.random() > 0.5 ? 'increasing' : 'decreasing',
      riskFactors: [
        'Market volatility',
        'Seasonal variations',
        'Competitive landscape'
      ],
      recommendations: [
        'Monitor closely for early warning signs',
        'Prepare contingency plans',
        'Optimize current strategies'
      ]
    }));
    
    res.json({
      success: true,
      data: {
        timeHorizon,
        predictions,
        overallConfidence: predictions.reduce((sum, p) => sum + p.confidence, 0) / predictions.length,
        keyInsights: [
          'Multiple metrics showing positive trends',
          'High confidence in short-term predictions',
          'Recommend monitoring for potential risks'
        ]
      }
    });
  } catch (error) {
    console.error('Error performing predictive analysis:', error);
    res.status(500).json({ error: 'Failed to perform predictive analysis' });
  }
});

// Recomendaciones inteligentes
router.post('/recommendations/generate', authenticateToken, (req, res) => {
  try {
    const { context, priority = 'medium' } = req.body;
    
    if (!context) {
      return res.status(400).json({ error: 'Context is required' });
    }
    
    // Simular generación de recomendaciones inteligentes
    const recommendations = [
      {
        id: `rec_${Date.now()}_1`,
        type: 'strategy',
        priority: 'high',
        title: 'Optimize Customer Communication Strategy',
        description: 'Based on sentiment analysis, implement more personalized communication approaches',
        impact: 'positive',
        effort: 'medium',
        timeline: '2-4 weeks',
        successMetrics: ['Customer satisfaction', 'Engagement rate', 'Response time'],
        actionItems: [
          'Segment customers by communication preferences',
          'Develop personalized messaging templates',
          'Implement automated response system',
          'Train customer service team'
        ]
      },
      {
        id: `rec_${Date.now()}_2`,
        type: 'process',
        priority: 'medium',
        title: 'Enhance Feedback Collection Process',
        description: 'Improve feedback collection to capture more actionable insights',
        impact: 'positive',
        effort: 'low',
        timeline: '1-2 weeks',
        successMetrics: ['Feedback volume', 'Response rate', 'Data quality'],
        actionItems: [
          'Add feedback prompts at key touchpoints',
          'Implement multi-channel collection',
          'Optimize feedback forms',
          'Set up automated follow-ups'
        ]
      },
      {
        id: `rec_${Date.now()}_3`,
        type: 'technology',
        priority: 'low',
        title: 'Implement Advanced Analytics Dashboard',
        description: 'Deploy real-time analytics dashboard for better decision making',
        impact: 'positive',
        effort: 'high',
        timeline: '4-6 weeks',
        successMetrics: ['Dashboard usage', 'Decision speed', 'Insight quality'],
        actionItems: [
          'Design dashboard layout',
          'Integrate data sources',
          'Develop visualization components',
          'Train users on new features'
        ]
      }
    ];
    
    res.json({
      success: true,
      data: {
        context,
        recommendations,
        totalRecommendations: recommendations.length,
        highPriority: recommendations.filter(r => r.priority === 'high').length,
        estimatedImpact: 'Significant improvement in customer satisfaction and operational efficiency'
      }
    });
  } catch (error) {
    console.error('Error generating recommendations:', error);
    res.status(500).json({ error: 'Failed to generate recommendations' });
  }
});

// Análisis de impacto
router.post('/impact/analyze', authenticateToken, (req, res) => {
  try {
    const { action, metrics } = req.body;
    
    if (!action || !metrics) {
      return res.status(400).json({ error: 'Action and metrics are required' });
    }
    
    // Simular análisis de impacto
    const impactAnalysis = {
      action,
      expectedImpact: {
        positive: Math.random() * 0.4 + 0.6,
        negative: Math.random() * 0.2,
        neutral: Math.random() * 0.2
      },
      metrics: metrics.map((metric: string) => ({
        metric,
        currentValue: Math.random() * 100,
        expectedChange: (Math.random() - 0.5) * 20,
        confidence: Math.random() * 0.3 + 0.7,
        timeline: '2-4 weeks'
      })),
      risks: [
        'Implementation challenges',
        'User adoption resistance',
        'Technical complexity'
      ],
      mitigationStrategies: [
        'Phased rollout approach',
        'Comprehensive training program',
        'Technical support team'
      ],
      successFactors: [
        'Strong leadership support',
        'Clear communication',
        'Adequate resources'
      ]
    };
    
    res.json({
      success: true,
      data: impactAnalysis
    });
  } catch (error) {
    console.error('Error analyzing impact:', error);
    res.status(500).json({ error: 'Failed to analyze impact' });
  }
});

export default router;

