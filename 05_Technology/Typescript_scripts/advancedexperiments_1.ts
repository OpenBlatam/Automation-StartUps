import express from 'express';
import { advancedExperimentService } from '../services/advancedExperimentService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener experimentos
router.get('/', authenticateToken, (req, res) => {
  try {
    const { status, type, limit = 50 } = req.query;
    
    let experiments = advancedExperimentService.getExperiments();
    
    if (status) {
      experiments = experiments.filter(e => e.status === status);
    }
    
    if (type) {
      experiments = experiments.filter(e => e.type === type);
    }
    
    if (limit) {
      experiments = experiments.slice(0, parseInt(limit as string));
    }
    
    res.json({
      success: true,
      data: experiments,
      count: experiments.length
    });
  } catch (error) {
    console.error('Error fetching experiments:', error);
    res.status(500).json({ error: 'Failed to fetch experiments' });
  }
});

// Crear experimento
router.post('/', authenticateToken, (req, res) => {
  try {
    const experimentData = req.body;
    
    if (!experimentData.name || !experimentData.type || !experimentData.hypothesis) {
      return res.status(400).json({ 
        error: 'Missing required fields: name, type, hypothesis' 
      });
    }
    
    const experimentId = advancedExperimentService.createExperiment(experimentData);
    
    res.status(201).json({
      success: true,
      data: { id: experimentId },
      message: 'Experiment created successfully'
    });
  } catch (error) {
    console.error('Error creating experiment:', error);
    res.status(500).json({ error: 'Failed to create experiment' });
  }
});

// Obtener experimento específico
router.get('/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const experiments = advancedExperimentService.getExperiments();
    const experiment = experiments.find(e => e.id === id);
    
    if (!experiment) {
      return res.status(404).json({ error: 'Experiment not found' });
    }
    
    res.json({
      success: true,
      data: experiment
    });
  } catch (error) {
    console.error('Error fetching experiment:', error);
    res.status(500).json({ error: 'Failed to fetch experiment' });
  }
});

// Iniciar experimento
router.post('/:id/start', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    
    advancedExperimentService.startExperiment(id);
    
    res.json({
      success: true,
      message: 'Experiment started successfully'
    });
  } catch (error) {
    console.error('Error starting experiment:', error);
    res.status(500).json({ error: 'Failed to start experiment' });
  }
});

// Pausar experimento
router.post('/:id/pause', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    
    advancedExperimentService.pauseExperiment(id);
    
    res.json({
      success: true,
      message: 'Experiment paused successfully'
    });
  } catch (error) {
    console.error('Error pausing experiment:', error);
    res.status(500).json({ error: 'Failed to pause experiment' });
  }
});

// Completar experimento
router.post('/:id/complete', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    
    advancedExperimentService.completeExperiment(id);
    
    res.json({
      success: true,
      message: 'Experiment completed successfully'
    });
  } catch (error) {
    console.error('Error completing experiment:', error);
    res.status(500).json({ error: 'Failed to complete experiment' });
  }
});

// Obtener análisis de experimento
router.get('/:id/analyses', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const { limit = 20 } = req.query;
    
    const analyses = advancedExperimentService.getAnalyses(id)
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: analyses,
      count: analyses.length
    });
  } catch (error) {
    console.error('Error fetching experiment analyses:', error);
    res.status(500).json({ error: 'Failed to fetch experiment analyses' });
  }
});

// Obtener templates
router.get('/templates/list', authenticateToken, (req, res) => {
  try {
    const templates = advancedExperimentService.getTemplates();
    
    res.json({
      success: true,
      data: templates,
      count: templates.length
    });
  } catch (error) {
    console.error('Error fetching experiment templates:', error);
    res.status(500).json({ error: 'Failed to fetch experiment templates' });
  }
});

// Obtener template específico
router.get('/templates/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const templates = advancedExperimentService.getTemplates();
    const template = templates.find(t => t.id === id);
    
    if (!template) {
      return res.status(404).json({ error: 'Experiment template not found' });
    }
    
    res.json({
      success: true,
      data: template
    });
  } catch (error) {
    console.error('Error fetching experiment template:', error);
    res.status(500).json({ error: 'Failed to fetch experiment template' });
  }
});

// Crear experimento desde template
router.post('/from-template', authenticateToken, (req, res) => {
  try {
    const { templateId, customizations = {} } = req.body;
    
    if (!templateId) {
      return res.status(400).json({ error: 'Template ID is required' });
    }
    
    // Obtener template (en implementación real, desde base de datos)
    const templates = [
      {
        id: 'ui_ab_test_template',
        name: 'UI A/B Test',
        description: 'Template for testing UI changes and improvements',
        type: 'a_b',
        hypothesis: 'The new UI design will improve user engagement',
        successMetrics: ['conversion_rate', 'click_through_rate'],
        secondaryMetrics: ['time_on_page', 'bounce_rate'],
        segments: [
          {
            id: 'all_users',
            name: 'All Users',
            description: 'All users visiting the site',
            criteria: {},
            percentage: 100,
            enabled: true
          }
        ],
        variants: [
          {
            id: 'control',
            name: 'Control',
            description: 'Current UI design',
            type: 'control',
            configuration: {},
            trafficPercentage: 50,
            enabled: true
          },
          {
            id: 'treatment',
            name: 'Treatment',
            description: 'New UI design',
            type: 'treatment',
            configuration: {},
            trafficPercentage: 50,
            enabled: true
          }
        ],
        trafficAllocation: {
          control: 50,
          treatment: 50
        },
        startDate: new Date(),
        duration: 14,
        minSampleSize: 1000,
        confidenceLevel: 0.95,
        power: 0.8
      }
    ];
    
    const template = templates.find(t => t.id === templateId);
    if (!template) {
      return res.status(404).json({ error: 'Template not found' });
    }
    
    // Aplicar personalizaciones
    const experimentData = {
      ...template,
      ...customizations,
      name: customizations.name || template.name,
      description: customizations.description || template.description,
      hypothesis: customizations.hypothesis || template.hypothesis
    };
    
    const experimentId = advancedExperimentService.createExperiment(experimentData);
    
    res.status(201).json({
      success: true,
      data: { id: experimentId },
      message: 'Experiment created from template successfully'
    });
  } catch (error) {
    console.error('Error creating experiment from template:', error);
    res.status(500).json({ error: 'Failed to create experiment from template' });
  }
});

// Obtener estadísticas
router.get('/stats/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedExperimentService.getStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching experiment stats:', error);
    res.status(500).json({ error: 'Failed to fetch experiment stats' });
  }
});

// Obtener dashboard
router.get('/dashboard/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedExperimentService.getStats();
    const experiments = advancedExperimentService.getExperiments();
    const templates = advancedExperimentService.getTemplates();
    
    const dashboard = {
      overview: {
        totalExperiments: stats.totalExperiments,
        runningExperiments: stats.runningExperiments,
        completedExperiments: stats.completedExperiments,
        totalAnalyses: stats.totalAnalyses,
        averageDuration: stats.averageDuration,
        successRate: stats.successRate
      },
      recentExperiments: experiments.slice(0, 10),
      templates: templates.map(template => ({
        id: template.id,
        name: template.name,
        type: template.type,
        category: template.category
      })),
      performance: {
        successRate: stats.successRate,
        averageDuration: stats.averageDuration,
        activeExperiments: stats.runningExperiments
      }
    };
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    console.error('Error fetching experiment dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch experiment dashboard' });
  }
});

// Obtener experimentos por estado
router.get('/status/:status', authenticateToken, (req, res) => {
  try {
    const { status } = req.params;
    const { limit = 50 } = req.query;
    
    const experiments = advancedExperimentService.getExperiments()
      .filter(e => e.status === status)
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: experiments,
      count: experiments.length
    });
  } catch (error) {
    console.error('Error fetching experiments by status:', error);
    res.status(500).json({ error: 'Failed to fetch experiments by status' });
  }
});

// Obtener experimentos por tipo
router.get('/type/:type', authenticateToken, (req, res) => {
  try {
    const { type } = req.params;
    const { limit = 50 } = req.query;
    
    const experiments = advancedExperimentService.getExperiments()
      .filter(e => e.type === type)
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: experiments,
      count: experiments.length
    });
  } catch (error) {
    console.error('Error fetching experiments by type:', error);
    res.status(500).json({ error: 'Failed to fetch experiments by type' });
  }
});

// Obtener experimentos activos
router.get('/active/list', authenticateToken, (req, res) => {
  try {
    const { limit = 20 } = req.query;
    
    const experiments = advancedExperimentService.getExperiments()
      .filter(e => e.status === 'running')
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: experiments,
      count: experiments.length
    });
  } catch (error) {
    console.error('Error fetching active experiments:', error);
    res.status(500).json({ error: 'Failed to fetch active experiments' });
  }
});

// Obtener experimentos completados
router.get('/completed/list', authenticateToken, (req, res) => {
  try {
    const { limit = 20 } = req.query;
    
    const experiments = advancedExperimentService.getExperiments()
      .filter(e => e.status === 'completed')
      .sort((a, b) => b.endDate!.getTime() - a.endDate!.getTime())
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: experiments,
      count: experiments.length
    });
  } catch (error) {
    console.error('Error fetching completed experiments:', error);
    res.status(500).json({ error: 'Failed to fetch completed experiments' });
  }
});

// Obtener análisis recientes
router.get('/analyses/recent', authenticateToken, (req, res) => {
  try {
    const { limit = 20 } = req.query;
    
    const analyses = advancedExperimentService.getAnalyses()
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: analyses,
      count: analyses.length
    });
  } catch (error) {
    console.error('Error fetching recent analyses:', error);
    res.status(500).json({ error: 'Failed to fetch recent analyses' });
  }
});

// Validar experimento
router.post('/validate', authenticateToken, (req, res) => {
  try {
    const { name, type, hypothesis, variants, segments, duration, minSampleSize } = req.body;
    
    if (!name || !type || !hypothesis || !variants || !segments) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    
    // Simular validación de experimento
    const validation = {
      valid: true,
      errors: [],
      warnings: [],
      suggestions: []
    };
    
    // Validar variantes
    if (!Array.isArray(variants) || variants.length < 2) {
      validation.errors.push('At least 2 variants are required');
    }
    
    // Validar segmentos
    if (!Array.isArray(segments) || segments.length === 0) {
      validation.errors.push('At least one segment is required');
    }
    
    // Validar duración
    if (duration && duration < 7) {
      validation.warnings.push('Experiments shorter than 7 days may not provide reliable results');
    }
    
    // Validar tamaño de muestra
    if (minSampleSize && minSampleSize < 100) {
      validation.warnings.push('Sample size below 100 may not provide statistical significance');
    }
    
    // Sugerencias
    if (variants && variants.length > 5) {
      validation.suggestions.push('Consider reducing the number of variants for clearer results');
    }
    
    if (segments && segments.length > 10) {
      validation.suggestions.push('Consider consolidating segments for better analysis');
    }
    
    res.json({
      success: true,
      data: validation
    });
  } catch (error) {
    console.error('Error validating experiment:', error);
    res.status(500).json({ error: 'Failed to validate experiment' });
  }
});

export default router;

