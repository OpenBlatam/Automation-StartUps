import express from 'express';
import { advancedAITrainingService } from '../services/advancedAITrainingService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener datasets
router.get('/datasets', authenticateToken, (req, res) => {
  try {
    const datasets = advancedAITrainingService.getDatasets();
    
    res.json({
      success: true,
      data: datasets,
      count: datasets.length
    });
  } catch (error) {
    console.error('Error fetching training datasets:', error);
    res.status(500).json({ error: 'Failed to fetch training datasets' });
  }
});

// Crear dataset
router.post('/datasets', authenticateToken, (req, res) => {
  try {
    const datasetData = req.body;
    
    if (!datasetData.name || !datasetData.type || !datasetData.language) {
      return res.status(400).json({ 
        error: 'Missing required fields: name, type, language' 
      });
    }
    
    const datasetId = advancedAITrainingService.createDataset(datasetData);
    
    res.status(201).json({
      success: true,
      data: { id: datasetId },
      message: 'Training dataset created successfully'
    });
  } catch (error) {
    console.error('Error creating training dataset:', error);
    res.status(500).json({ error: 'Failed to create training dataset' });
  }
});

// Obtener trabajos de entrenamiento
router.get('/jobs', authenticateToken, (req, res) => {
  try {
    const { status, modelType, limit = 50 } = req.query;
    
    let jobs = advancedAITrainingService.getTrainingJobs();
    
    if (status) {
      jobs = jobs.filter(j => j.status === status);
    }
    
    if (modelType) {
      jobs = jobs.filter(j => j.modelType === modelType);
    }
    
    if (limit) {
      jobs = jobs.slice(0, parseInt(limit as string));
    }
    
    res.json({
      success: true,
      data: jobs,
      count: jobs.length
    });
  } catch (error) {
    console.error('Error fetching training jobs:', error);
    res.status(500).json({ error: 'Failed to fetch training jobs' });
  }
});

// Crear trabajo de entrenamiento
router.post('/jobs', authenticateToken, (req, res) => {
  try {
    const jobData = req.body;
    
    if (!jobData.name || !jobData.modelType || !jobData.algorithm || !jobData.datasetId) {
      return res.status(400).json({ 
        error: 'Missing required fields: name, modelType, algorithm, datasetId' 
      });
    }
    
    const jobId = advancedAITrainingService.createTrainingJob(jobData);
    
    res.status(201).json({
      success: true,
      data: { id: jobId },
      message: 'Training job created successfully'
    });
  } catch (error) {
    console.error('Error creating training job:', error);
    res.status(500).json({ error: 'Failed to create training job' });
  }
});

// Obtener trabajo específico
router.get('/jobs/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const jobs = advancedAITrainingService.getTrainingJobs();
    const job = jobs.find(j => j.id === id);
    
    if (!job) {
      return res.status(404).json({ error: 'Training job not found' });
    }
    
    res.json({
      success: true,
      data: job
    });
  } catch (error) {
    console.error('Error fetching training job:', error);
    res.status(500).json({ error: 'Failed to fetch training job' });
  }
});

// Obtener registro de modelos
router.get('/models', authenticateToken, (req, res) => {
  try {
    const models = advancedAITrainingService.getModelRegistry();
    
    res.json({
      success: true,
      data: models,
      count: models.length
    });
  } catch (error) {
    console.error('Error fetching model registry:', error);
    res.status(500).json({ error: 'Failed to fetch model registry' });
  }
});

// Obtener modelo específico
router.get('/models/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const models = advancedAITrainingService.getModelRegistry();
    const model = models.find(m => m.id === id);
    
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

// Obtener configuraciones
router.get('/configurations', authenticateToken, (req, res) => {
  try {
    const configurations = advancedAITrainingService.getConfigurations();
    
    res.json({
      success: true,
      data: configurations,
      count: configurations.length
    });
  } catch (error) {
    console.error('Error fetching training configurations:', error);
    res.status(500).json({ error: 'Failed to fetch training configurations' });
  }
});

// Obtener configuración específica
router.get('/configurations/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const configurations = advancedAITrainingService.getConfigurations();
    const config = configurations.find(c => c.id === id);
    
    if (!config) {
      return res.status(404).json({ error: 'Training configuration not found' });
    }
    
    res.json({
      success: true,
      data: config
    });
  } catch (error) {
    console.error('Error fetching training configuration:', error);
    res.status(500).json({ error: 'Failed to fetch training configuration' });
  }
});

// Obtener estadísticas
router.get('/stats/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedAITrainingService.getStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching training stats:', error);
    res.status(500).json({ error: 'Failed to fetch training stats' });
  }
});

// Obtener dashboard
router.get('/dashboard/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedAITrainingService.getStats();
    const jobs = advancedAITrainingService.getTrainingJobs();
    const models = advancedAITrainingService.getModelRegistry();
    const configurations = advancedAITrainingService.getConfigurations();
    
    const dashboard = {
      overview: {
        totalDatasets: stats.totalDatasets,
        totalTrainingJobs: stats.totalTrainingJobs,
        completedJobs: stats.completedJobs,
        failedJobs: stats.failedJobs,
        totalModels: stats.totalModels,
        activeModels: stats.activeModels,
        averageAccuracy: stats.averageAccuracy,
        averageTrainingTime: stats.averageTrainingTime
      },
      recentJobs: jobs.slice(0, 10),
      topModels: models.slice(0, 5),
      configurations: configurations.map(config => ({
        id: config.id,
        name: config.name,
        type: config.modelType,
        algorithm: config.algorithm
      })),
      performance: {
        successRate: stats.totalTrainingJobs > 0 
          ? (stats.completedJobs / stats.totalTrainingJobs) * 100 
          : 0,
        averageAccuracy: stats.averageAccuracy,
        averageTrainingTime: stats.averageTrainingTime
      }
    };
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    console.error('Error fetching training dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch training dashboard' });
  }
});

// Obtener trabajos por estado
router.get('/jobs/status/:status', authenticateToken, (req, res) => {
  try {
    const { status } = req.params;
    const { limit = 50 } = req.query;
    
    const jobs = advancedAITrainingService.getTrainingJobs()
      .filter(j => j.status === status)
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: jobs,
      count: jobs.length
    });
  } catch (error) {
    console.error('Error fetching jobs by status:', error);
    res.status(500).json({ error: 'Failed to fetch jobs by status' });
  }
});

// Obtener trabajos por tipo de modelo
router.get('/jobs/type/:type', authenticateToken, (req, res) => {
  try {
    const { type } = req.params;
    const { limit = 50 } = req.query;
    
    const jobs = advancedAITrainingService.getTrainingJobs()
      .filter(j => j.modelType === type)
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: jobs,
      count: jobs.length
    });
  } catch (error) {
    console.error('Error fetching jobs by type:', error);
    res.status(500).json({ error: 'Failed to fetch jobs by type' });
  }
});

// Obtener trabajos completados
router.get('/jobs/completed', authenticateToken, (req, res) => {
  try {
    const { limit = 20 } = req.query;
    
    const jobs = advancedAITrainingService.getTrainingJobs()
      .filter(j => j.status === 'completed')
      .sort((a, b) => b.completedAt!.getTime() - a.completedAt!.getTime())
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: jobs,
      count: jobs.length
    });
  } catch (error) {
    console.error('Error fetching completed jobs:', error);
    res.status(500).json({ error: 'Failed to fetch completed jobs' });
  }
});

// Obtener trabajos fallidos
router.get('/jobs/failed', authenticateToken, (req, res) => {
  try {
    const { limit = 20 } = req.query;
    
    const jobs = advancedAITrainingService.getTrainingJobs()
      .filter(j => j.status === 'failed')
      .sort((a, b) => b.startedAt.getTime() - a.startedAt.getTime())
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: jobs,
      count: jobs.length
    });
  } catch (error) {
    console.error('Error fetching failed jobs:', error);
    res.status(500).json({ error: 'Failed to fetch failed jobs' });
  }
});

// Obtener modelos activos
router.get('/models/active', authenticateToken, (req, res) => {
  try {
    const models = advancedAITrainingService.getModelRegistry()
      .filter(m => m.status === 'active');
    
    res.json({
      success: true,
      data: models,
      count: models.length
    });
  } catch (error) {
    console.error('Error fetching active models:', error);
    res.status(500).json({ error: 'Failed to fetch active models' });
  }
});

// Obtener modelos por tipo
router.get('/models/type/:type', authenticateToken, (req, res) => {
  try {
    const { type } = req.params;
    
    const models = advancedAITrainingService.getModelRegistry()
      .filter(m => m.type === type);
    
    res.json({
      success: true,
      data: models,
      count: models.length
    });
  } catch (error) {
    console.error('Error fetching models by type:', error);
    res.status(500).json({ error: 'Failed to fetch models by type' });
  }
});

// Obtener plantillas de configuración
router.get('/configurations/templates/list', authenticateToken, (req, res) => {
  try {
    const templates = [
      {
        id: 'sentiment_analysis_template',
        name: 'Sentiment Analysis Template',
        description: 'Template for training sentiment analysis models',
        type: 'sentiment',
        algorithm: 'bert',
        category: 'nlp',
        features: ['text_classification', 'sentiment_analysis', 'multi_language'],
        parameters: {
          maxLength: 512,
          batchSize: 16,
          learningRate: 2e-5,
          epochs: 3
        },
        metrics: ['accuracy', 'precision', 'recall', 'f1_score'],
        duration: 2
      },
      {
        id: 'text_classification_template',
        name: 'Text Classification Template',
        description: 'Template for training text classification models',
        type: 'classification',
        algorithm: 'roberta',
        category: 'nlp',
        features: ['text_classification', 'multi_class', 'multi_language'],
        parameters: {
          maxLength: 256,
          batchSize: 32,
          learningRate: 1e-5,
          epochs: 5
        },
        metrics: ['accuracy', 'precision', 'recall', 'f1_score'],
        duration: 3
      },
      {
        id: 'recommendation_system_template',
        name: 'Recommendation System Template',
        description: 'Template for training recommendation models',
        type: 'recommendation',
        algorithm: 'matrix_factorization',
        category: 'recommendation',
        features: ['collaborative_filtering', 'content_based', 'hybrid'],
        parameters: {
          factors: 50,
          iterations: 100,
          learningRate: 0.01,
          regularization: 0.01
        },
        metrics: ['rmse', 'mae', 'precision', 'recall'],
        duration: 1
      }
    ];
    
    res.json({
      success: true,
      data: templates,
      count: templates.length
    });
  } catch (error) {
    console.error('Error fetching configuration templates:', error);
    res.status(500).json({ error: 'Failed to fetch configuration templates' });
  }
});

// Crear configuración desde plantilla
router.post('/configurations/from-template', authenticateToken, (req, res) => {
  try {
    const { templateId, customizations = {} } = req.body;
    
    if (!templateId) {
      return res.status(400).json({ error: 'Template ID is required' });
    }
    
    // Obtener plantilla (en implementación real, desde base de datos)
    const templates = [
      {
        id: 'sentiment_analysis_template',
        name: 'Sentiment Analysis Configuration',
        description: 'Configuration for training sentiment analysis models',
        modelType: 'sentiment',
        algorithm: 'bert',
        parameters: {
          maxLength: 512,
          batchSize: 16,
          learningRate: 2e-5,
          epochs: 3
        },
        hyperparameters: {
          hiddenSize: 768,
          numAttentionHeads: 12,
          numHiddenLayers: 12
        },
        preprocessing: {
          steps: ['tokenization', 'normalization', 'padding'],
          parameters: {
            maxLength: 512,
            padding: 'max_length',
            truncation: true
          }
        },
        validation: {
          strategy: 'holdout',
          testSize: 0.2,
          kFolds: 5,
          randomState: 42
        },
        optimization: {
          method: 'bayesian',
          parameters: {
            learningRate: [1e-5, 5e-5],
            batchSize: [8, 16, 32]
          },
          maxIterations: 20
        },
        monitoring: {
          metrics: ['accuracy', 'precision', 'recall', 'f1_score'],
          thresholds: {
            accuracy: 0.85,
            f1_score: 0.80
          },
          alerts: ['low_performance', 'overfitting']
        }
      }
    ];
    
    const template = templates.find(t => t.id === templateId);
    if (!template) {
      return res.status(404).json({ error: 'Template not found' });
    }
    
    // Aplicar personalizaciones
    const configData = {
      ...template,
      ...customizations,
      name: customizations.name || template.name,
      description: customizations.description || template.description
    };
    
    // En una implementación real, esto crearía la configuración
    const configId = `config_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    res.status(201).json({
      success: true,
      data: { id: configId },
      message: 'Training configuration created from template successfully'
    });
  } catch (error) {
    console.error('Error creating configuration from template:', error);
    res.status(500).json({ error: 'Failed to create configuration from template' });
  }
});

export default router;

