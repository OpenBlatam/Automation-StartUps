import express from 'express';
import { aiOptimizationService } from '../services/aiOptimizationService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener configuraciones de optimización
router.get('/configs', authenticateToken, (req, res) => {
  try {
    const configs = aiOptimizationService.getConfigs();
    
    res.json({
      success: true,
      data: configs,
      count: configs.length
    });
  } catch (error) {
    console.error('Error fetching optimization configs:', error);
    res.status(500).json({ error: 'Failed to fetch optimization configs' });
  }
});

// Obtener configuración específica
router.get('/configs/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const config = aiOptimizationService.getConfig(id);
    
    if (!config) {
      return res.status(404).json({ error: 'Optimization config not found' });
    }
    
    res.json({
      success: true,
      data: config
    });
  } catch (error) {
    console.error('Error fetching optimization config:', error);
    res.status(500).json({ error: 'Failed to fetch optimization config' });
  }
});

// Crear configuración de optimización
router.post('/configs', authenticateToken, (req, res) => {
  try {
    const configData = req.body;
    
    // Validar datos requeridos
    if (!configData.name || !configData.type || !configData.model) {
      return res.status(400).json({ 
        error: 'Missing required fields: name, type, model' 
      });
    }
    
    const configId = aiOptimizationService.createConfig(configData);
    
    res.status(201).json({
      success: true,
      data: { id: configId },
      message: 'Optimization config created successfully'
    });
  } catch (error) {
    console.error('Error creating optimization config:', error);
    res.status(500).json({ error: 'Failed to create optimization config' });
  }
});

// Actualizar configuración de optimización
router.put('/configs/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;
    
    const updated = aiOptimizationService.updateConfig(id, updates);
    
    if (!updated) {
      return res.status(404).json({ error: 'Optimization config not found' });
    }
    
    res.json({
      success: true,
      message: 'Optimization config updated successfully'
    });
  } catch (error) {
    console.error('Error updating optimization config:', error);
    res.status(500).json({ error: 'Failed to update optimization config' });
  }
});

// Optimizar modelo
router.post('/optimize/:configId', authenticateToken, (req, res) => {
  try {
    const { configId } = req.params;
    const { data } = req.body;
    
    const config = aiOptimizationService.getConfig(configId);
    if (!config) {
      return res.status(404).json({ error: 'Optimization config not found' });
    }
    
    if (!config.enabled) {
      return res.status(400).json({ error: 'Optimization config is disabled' });
    }
    
    aiOptimizationService.optimizeModel(configId, data);
    
    res.json({
      success: true,
      message: 'Model optimization initiated successfully'
    });
  } catch (error) {
    console.error('Error optimizing model:', error);
    res.status(500).json({ error: 'Failed to optimize model' });
  }
});

// Obtener resultados de optimización
router.get('/results', authenticateToken, (req, res) => {
  try {
    const { limit = 50, configId } = req.query;
    
    let results = aiOptimizationService.getResults(parseInt(limit as string));
    
    if (configId) {
      results = results.filter(result => result.configId === configId);
    }
    
    res.json({
      success: true,
      data: results,
      count: results.length
    });
  } catch (error) {
    console.error('Error fetching optimization results:', error);
    res.status(500).json({ error: 'Failed to fetch optimization results' });
  }
});

// Obtener estadísticas de optimización
router.get('/stats/overview', authenticateToken, (req, res) => {
  try {
    const stats = aiOptimizationService.getStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching optimization stats:', error);
    res.status(500).json({ error: 'Failed to fetch optimization stats' });
  }
});

// Obtener dashboard de optimización
router.get('/dashboard/overview', authenticateToken, (req, res) => {
  try {
    const stats = aiOptimizationService.getStats();
    const configs = aiOptimizationService.getConfigs();
    const recentResults = aiOptimizationService.getResults(10);
    
    const dashboard = {
      overview: {
        totalConfigs: stats.totalConfigs,
        enabledConfigs: stats.enabledConfigs,
        totalOptimizations: stats.totalOptimizations,
        successfulOptimizations: stats.successfulOptimizations,
        failedOptimizations: stats.failedOptimizations,
        successRate: stats.totalOptimizations > 0 
          ? (stats.successfulOptimizations / stats.totalOptimizations) * 100 
          : 0,
        averageImprovement: stats.averageImprovement
      },
      configs: configs.map(config => ({
        id: config.id,
        name: config.name,
        type: config.type,
        enabled: config.enabled,
        model: config.model,
        performance: config.performance,
        autoRetrain: config.autoRetrain
      })),
      recentActivity: recentResults,
      performance: {
        totalOptimizations: stats.totalOptimizations,
        successfulOptimizations: stats.successfulOptimizations,
        failedOptimizations: stats.failedOptimizations,
        successRate: stats.totalOptimizations > 0 
          ? (stats.successfulOptimizations / stats.totalOptimizations) * 100 
          : 0
      }
    };
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    console.error('Error fetching optimization dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch optimization dashboard' });
  }
});

// Obtener plantillas de optimización
router.get('/templates/list', authenticateToken, (req, res) => {
  try {
    const templates = [
      {
        id: 'sentiment_optimization_template',
        name: 'Sentiment Analysis Optimization',
        description: 'Optimize sentiment analysis models for better accuracy',
        type: 'sentiment',
        category: 'nlp',
        features: ['Accuracy Improvement', 'Latency Reduction', 'Throughput Enhancement'],
        parameters: {
          learningRate: 0.001,
          batchSize: 32,
          epochs: 10,
          dropout: 0.1
        },
        thresholds: {
          confidence: 0.8,
          accuracy: 0.85,
          latency: 200
        }
      },
      {
        id: 'classification_optimization_template',
        name: 'Classification Optimization',
        description: 'Optimize classification models for better performance',
        type: 'classification',
        category: 'ml',
        features: ['Multi-class Classification', 'Feature Engineering', 'Model Tuning'],
        parameters: {
          learningRate: 0.0005,
          batchSize: 64,
          epochs: 15,
          dropout: 0.2
        },
        thresholds: {
          confidence: 0.85,
          accuracy: 0.88,
          latency: 150
        }
      },
      {
        id: 'prediction_optimization_template',
        name: 'Prediction Optimization',
        description: 'Optimize prediction models for better accuracy',
        type: 'prediction',
        category: 'ml',
        features: ['Churn Prediction', 'Upsell Prediction', 'Recommendation Engine'],
        parameters: {
          learningRate: 0.0001,
          batchSize: 128,
          epochs: 20,
          dropout: 0.15
        },
        thresholds: {
          confidence: 0.9,
          accuracy: 0.9,
          latency: 100
        }
      },
      {
        id: 'clustering_optimization_template',
        name: 'Clustering Optimization',
        description: 'Optimize clustering algorithms for better segmentation',
        type: 'clustering',
        category: 'ml',
        features: ['Customer Segmentation', 'Pattern Recognition', 'Anomaly Detection'],
        parameters: {
          nClusters: 5,
          maxIter: 300,
          randomState: 42
        },
        thresholds: {
          confidence: 0.8,
          accuracy: 0.85,
          latency: 200
        }
      },
      {
        id: 'recommendation_optimization_template',
        name: 'Recommendation Optimization',
        description: 'Optimize recommendation systems for better personalization',
        type: 'recommendation',
        category: 'ml',
        features: ['Collaborative Filtering', 'Content-based Filtering', 'Hybrid Approach'],
        parameters: {
          learningRate: 0.01,
          regularization: 0.01,
          factors: 50,
          iterations: 100
        },
        thresholds: {
          confidence: 0.8,
          accuracy: 0.85,
          latency: 150
        }
      }
    ];
    
    res.json({
      success: true,
      data: templates,
      count: templates.length
    });
  } catch (error) {
    console.error('Error fetching optimization templates:', error);
    res.status(500).json({ error: 'Failed to fetch optimization templates' });
  }
});

// Crear configuración desde plantilla
router.post('/configs/from-template', authenticateToken, (req, res) => {
  try {
    const { templateId, customizations = {} } = req.body;
    
    if (!templateId) {
      return res.status(400).json({ error: 'Template ID is required' });
    }
    
    // Obtener plantilla (en implementación real, desde base de datos)
    const templates = [
      {
        id: 'sentiment_optimization_template',
        name: 'Sentiment Analysis Optimization',
        type: 'sentiment',
        enabled: true,
        model: {
          name: 'BERT-Sentiment-LATAM',
          version: '2.1.0',
          accuracy: 0.89,
          lastTrained: new Date(),
          trainingData: 50000
        },
        parameters: {
          learningRate: 0.001,
          batchSize: 32,
          epochs: 10,
          dropout: 0.1,
          maxLength: 512
        },
        performance: {
          accuracy: 0.89,
          precision: 0.87,
          recall: 0.91,
          f1Score: 0.89,
          latency: 150
        },
        thresholds: {
          confidence: 0.8,
          accuracy: 0.85,
          latency: 200
        },
        autoRetrain: true,
        retrainThreshold: 0.05
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
      parameters: { ...template.parameters, ...customizations.parameters }
    };
    
    const configId = aiOptimizationService.createConfig(configData);
    
    res.status(201).json({
      success: true,
      data: { id: configId },
      message: 'Optimization config created from template successfully'
    });
  } catch (error) {
    console.error('Error creating optimization config from template:', error);
    res.status(500).json({ error: 'Failed to create optimization config from template' });
  }
});

// Validar configuración de optimización
router.post('/validate', authenticateToken, (req, res) => {
  try {
    const { type, parameters, thresholds } = req.body;
    
    if (!type || !parameters) {
      return res.status(400).json({ error: 'Type and parameters are required' });
    }
    
    // Simular validación de configuración
    const validation = {
      valid: true,
      errors: [],
      warnings: [],
      suggestions: []
    };
    
    // Validaciones específicas por tipo
    switch (type) {
      case 'sentiment':
        if (!parameters.learningRate || parameters.learningRate <= 0) {
          validation.valid = false;
          validation.errors.push('Learning rate must be greater than 0');
        }
        if (!parameters.batchSize || parameters.batchSize <= 0) {
          validation.valid = false;
          validation.errors.push('Batch size must be greater than 0');
        }
        break;
      case 'classification':
        if (!parameters.epochs || parameters.epochs <= 0) {
          validation.valid = false;
          validation.errors.push('Epochs must be greater than 0');
        }
        if (parameters.dropout < 0 || parameters.dropout > 1) {
          validation.valid = false;
          validation.errors.push('Dropout must be between 0 and 1');
        }
        break;
      case 'prediction':
        if (!parameters.learningRate || parameters.learningRate <= 0) {
          validation.valid = false;
          validation.errors.push('Learning rate must be greater than 0');
        }
        break;
      case 'clustering':
        if (!parameters.nClusters || parameters.nClusters <= 0) {
          validation.valid = false;
          validation.errors.push('Number of clusters must be greater than 0');
        }
        break;
      case 'recommendation':
        if (!parameters.factors || parameters.factors <= 0) {
          validation.valid = false;
          validation.errors.push('Number of factors must be greater than 0');
        }
        break;
      default:
        validation.warnings.push(`Unknown optimization type: ${type}`);
    }
    
    // Validar umbrales
    if (thresholds) {
      if (thresholds.confidence < 0 || thresholds.confidence > 1) {
        validation.errors.push('Confidence threshold must be between 0 and 1');
      }
      if (thresholds.accuracy < 0 || thresholds.accuracy > 1) {
        validation.errors.push('Accuracy threshold must be between 0 and 1');
      }
      if (thresholds.latency < 0) {
        validation.errors.push('Latency threshold must be greater than or equal to 0');
      }
    }
    
    res.json({
      success: true,
      data: validation
    });
  } catch (error) {
    console.error('Error validating optimization configuration:', error);
    res.status(500).json({ error: 'Failed to validate optimization configuration' });
  }
});

export default router;

