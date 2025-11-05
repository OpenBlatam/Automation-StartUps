import express from 'express';
import { advancedRecommendationEngine } from '../services/advancedRecommendationEngine';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Generar recomendaciones
router.post('/generate', authenticateToken, (req, res) => {
  try {
    const context = req.body;
    
    if (!context.customerId) {
      return res.status(400).json({ 
        error: 'Missing required field: customerId' 
      });
    }
    
    const contextId = advancedRecommendationEngine.generateRecommendations(context);
    
    res.json({
      success: true,
      data: { contextId },
      message: 'Recommendations generation initiated successfully'
    });
  } catch (error) {
    console.error('Error generating recommendations:', error);
    res.status(500).json({ error: 'Failed to generate recommendations' });
  }
});

// Obtener recomendaciones
router.get('/:customerId', authenticateToken, (req, res) => {
  try {
    const { customerId } = req.params;
    const { limit = 10, type, category, priority } = req.query;
    
    let recommendations = advancedRecommendationEngine.getRecommendations(
      customerId, 
      parseInt(limit as string)
    );
    
    if (type) {
      recommendations = recommendations.filter(rec => rec.type === type);
    }
    
    if (category) {
      recommendations = recommendations.filter(rec => rec.category === category);
    }
    
    if (priority) {
      recommendations = recommendations.filter(rec => rec.priority === priority);
    }
    
    res.json({
      success: true,
      data: recommendations,
      count: recommendations.length
    });
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    res.status(500).json({ error: 'Failed to fetch recommendations' });
  }
});

// Obtener motores
router.get('/engines/list', authenticateToken, (req, res) => {
  try {
    const engines = advancedRecommendationEngine.getEngines();
    
    res.json({
      success: true,
      data: engines,
      count: engines.length
    });
  } catch (error) {
    console.error('Error fetching recommendation engines:', error);
    res.status(500).json({ error: 'Failed to fetch recommendation engines' });
  }
});

// Obtener motor específico
router.get('/engines/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const engines = advancedRecommendationEngine.getEngines();
    const engine = engines.find(e => e.id === id);
    
    if (!engine) {
      return res.status(404).json({ error: 'Recommendation engine not found' });
    }
    
    res.json({
      success: true,
      data: engine
    });
  } catch (error) {
    console.error('Error fetching recommendation engine:', error);
    res.status(500).json({ error: 'Failed to fetch recommendation engine' });
  }
});

// Crear motor
router.post('/engines', authenticateToken, (req, res) => {
  try {
    const engineData = req.body;
    
    if (!engineData.name || !engineData.type || !engineData.algorithm) {
      return res.status(400).json({ 
        error: 'Missing required fields: name, type, algorithm' 
      });
    }
    
    const engineId = advancedRecommendationEngine.createEngine(engineData);
    
    res.status(201).json({
      success: true,
      data: { id: engineId },
      message: 'Recommendation engine created successfully'
    });
  } catch (error) {
    console.error('Error creating recommendation engine:', error);
    res.status(500).json({ error: 'Failed to create recommendation engine' });
  }
});

// Obtener estadísticas
router.get('/stats/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedRecommendationEngine.getStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching recommendation stats:', error);
    res.status(500).json({ error: 'Failed to fetch recommendation stats' });
  }
});

// Obtener dashboard
router.get('/dashboard/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedRecommendationEngine.getStats();
    const engines = advancedRecommendationEngine.getEngines();
    
    const dashboard = {
      overview: {
        totalEngines: stats.totalEngines,
        activeEngines: stats.activeEngines,
        totalRecommendations: stats.totalRecommendations,
        averageConfidence: stats.averageConfidence,
        averageValue: stats.averageValue
      },
      engines: engines.map(engine => ({
        id: engine.id,
        name: engine.name,
        type: engine.type,
        algorithm: engine.algorithm,
        status: engine.status,
        performance: engine.performance
      })),
      topPerformingEngine: stats.topPerformingEngine ? {
        id: stats.topPerformingEngine.id,
        name: stats.topPerformingEngine.name,
        accuracy: stats.topPerformingEngine.performance.accuracy,
        f1Score: stats.topPerformingEngine.performance.f1Score
      } : null
    };
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    console.error('Error fetching recommendation dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch recommendation dashboard' });
  }
});

// Obtener recomendaciones por tipo
router.get('/:customerId/type/:type', authenticateToken, (req, res) => {
  try {
    const { customerId, type } = req.params;
    const { limit = 10 } = req.query;
    
    const recommendations = advancedRecommendationEngine.getRecommendations(
      customerId, 
      parseInt(limit as string)
    ).filter(rec => rec.type === type);
    
    res.json({
      success: true,
      data: recommendations,
      count: recommendations.length
    });
  } catch (error) {
    console.error('Error fetching recommendations by type:', error);
    res.status(500).json({ error: 'Failed to fetch recommendations by type' });
  }
});

// Obtener recomendaciones por categoría
router.get('/:customerId/category/:category', authenticateToken, (req, res) => {
  try {
    const { customerId, category } = req.params;
    const { limit = 10 } = req.query;
    
    const recommendations = advancedRecommendationEngine.getRecommendations(
      customerId, 
      parseInt(limit as string)
    ).filter(rec => rec.category === category);
    
    res.json({
      success: true,
      data: recommendations,
      count: recommendations.length
    });
  } catch (error) {
    console.error('Error fetching recommendations by category:', error);
    res.status(500).json({ error: 'Failed to fetch recommendations by category' });
  }
});

// Obtener recomendaciones por prioridad
router.get('/:customerId/priority/:priority', authenticateToken, (req, res) => {
  try {
    const { customerId, priority } = req.params;
    const { limit = 10 } = req.query;
    
    const recommendations = advancedRecommendationEngine.getRecommendations(
      customerId, 
      parseInt(limit as string)
    ).filter(rec => rec.priority === priority);
    
    res.json({
      success: true,
      data: recommendations,
      count: recommendations.length
    });
  } catch (error) {
    console.error('Error fetching recommendations by priority:', error);
    res.status(500).json({ error: 'Failed to fetch recommendations by priority' });
  }
});

// Obtener recomendaciones de alta confianza
router.get('/:customerId/high-confidence', authenticateToken, (req, res) => {
  try {
    const { customerId } = req.params;
    const { limit = 10, threshold = 0.8 } = req.query;
    
    const recommendations = advancedRecommendationEngine.getRecommendations(
      customerId, 
      parseInt(limit as string)
    ).filter(rec => rec.confidence >= parseFloat(threshold as string));
    
    res.json({
      success: true,
      data: recommendations,
      count: recommendations.length
    });
  } catch (error) {
    console.error('Error fetching high-confidence recommendations:', error);
    res.status(500).json({ error: 'Failed to fetch high-confidence recommendations' });
  }
});

// Obtener recomendaciones de alta relevancia
router.get('/:customerId/high-relevance', authenticateToken, (req, res) => {
  try {
    const { customerId } = req.params;
    const { limit = 10, threshold = 0.8 } = req.query;
    
    const recommendations = advancedRecommendationEngine.getRecommendations(
      customerId, 
      parseInt(limit as string)
    ).filter(rec => rec.value >= parseFloat(threshold as string));
    
    res.json({
      success: true,
      data: recommendations,
      count: recommendations.length
    });
  } catch (error) {
    console.error('Error fetching high-relevance recommendations:', error);
    res.status(500).json({ error: 'Failed to fetch high-relevance recommendations' });
  }
});

// Obtener recomendaciones urgentes
router.get('/:customerId/urgent', authenticateToken, (req, res) => {
  try {
    const { customerId } = req.params;
    const { limit = 5 } = req.query;
    
    const recommendations = advancedRecommendationEngine.getRecommendations(
      customerId, 
      parseInt(limit as string)
    ).filter(rec => rec.priority === 'urgent');
    
    res.json({
      success: true,
      data: recommendations,
      count: recommendations.length
    });
  } catch (error) {
    console.error('Error fetching urgent recommendations:', error);
    res.status(500).json({ error: 'Failed to fetch urgent recommendations' });
  }
});

// Obtener plantillas de motores
router.get('/engines/templates/list', authenticateToken, (req, res) => {
  try {
    const templates = [
      {
        id: 'collaborative_filtering_template',
        name: 'Collaborative Filtering Engine',
        description: 'Recommendations based on similar users',
        type: 'collaborative',
        algorithm: 'matrix_factorization',
        parameters: {
          factors: 50,
          iterations: 100,
          learningRate: 0.01,
          regularization: 0.01
        },
        features: ['user_similarity', 'item_ratings', 'implicit_feedback']
      },
      {
        id: 'content_based_template',
        name: 'Content-Based Filtering Engine',
        description: 'Recommendations based on item features',
        type: 'content_based',
        algorithm: 'tf_idf_cosine',
        parameters: {
          minTermFreq: 2,
          maxTermFreq: 100,
          minDocFreq: 2,
          maxDocFreq: 1000
        },
        features: ['item_features', 'content_analysis', 'text_processing']
      },
      {
        id: 'hybrid_template',
        name: 'Hybrid Recommendation Engine',
        description: 'Combines multiple recommendation approaches',
        type: 'hybrid',
        algorithm: 'weighted_ensemble',
        parameters: {
          collaborativeWeight: 0.6,
          contentWeight: 0.4,
          contextualWeight: 0.3
        },
        features: ['multiple_algorithms', 'ensemble_learning', 'weight_optimization']
      },
      {
        id: 'contextual_template',
        name: 'Contextual Recommendation Engine',
        description: 'Recommendations based on current context',
        type: 'contextual',
        algorithm: 'contextual_bandits',
        parameters: {
          explorationRate: 0.1,
          learningRate: 0.05,
          contextDimensions: 10
        },
        features: ['context_awareness', 'real_time_learning', 'exploration_exploitation']
      },
      {
        id: 'behavioral_template',
        name: 'Behavioral Recommendation Engine',
        description: 'Recommendations based on user behavior patterns',
        type: 'behavioral',
        algorithm: 'sequence_modeling',
        parameters: {
          sequenceLength: 10,
          hiddenSize: 128,
          numLayers: 2
        },
        features: ['sequence_analysis', 'behavior_patterns', 'temporal_modeling']
      }
    ];
    
    res.json({
      success: true,
      data: templates,
      count: templates.length
    });
  } catch (error) {
    console.error('Error fetching recommendation engine templates:', error);
    res.status(500).json({ error: 'Failed to fetch recommendation engine templates' });
  }
});

// Crear motor desde plantilla
router.post('/engines/from-template', authenticateToken, (req, res) => {
  try {
    const { templateId, customizations = {} } = req.body;
    
    if (!templateId) {
      return res.status(400).json({ error: 'Template ID is required' });
    }
    
    // Obtener plantilla (en implementación real, desde base de datos)
    const templates = [
      {
        id: 'collaborative_filtering_template',
        name: 'Collaborative Filtering Engine',
        description: 'Recommendations based on similar users',
        type: 'collaborative',
        algorithm: 'matrix_factorization',
        parameters: {
          factors: 50,
          iterations: 100,
          learningRate: 0.01,
          regularization: 0.01
        },
        performance: {
          accuracy: 0.85,
          precision: 0.82,
          recall: 0.80,
          f1Score: 0.81,
          coverage: 0.75,
          diversity: 0.70
        },
        status: 'active'
      }
    ];
    
    const template = templates.find(t => t.id === templateId);
    if (!template) {
      return res.status(404).json({ error: 'Template not found' });
    }
    
    // Aplicar personalizaciones
    const engineData = {
      ...template,
      ...customizations,
      name: customizations.name || template.name,
      description: customizations.description || template.description
    };
    
    const engineId = advancedRecommendationEngine.createEngine(engineData);
    
    res.status(201).json({
      success: true,
      data: { id: engineId },
      message: 'Recommendation engine created from template successfully'
    });
  } catch (error) {
    console.error('Error creating recommendation engine from template:', error);
    res.status(500).json({ error: 'Failed to create recommendation engine from template' });
  }
});

// Validar motor
router.post('/engines/validate', authenticateToken, (req, res) => {
  try {
    const { name, type, algorithm, parameters } = req.body;
    
    if (!name || !type || !algorithm) {
      return res.status(400).json({ error: 'Name, type, and algorithm are required' });
    }
    
    // Simular validación de motor
    const validation = {
      valid: true,
      errors: [],
      warnings: [],
      suggestions: []
    };
    
    // Validar tipo
    const validTypes = ['collaborative', 'content_based', 'hybrid', 'contextual', 'behavioral'];
    if (!validTypes.includes(type)) {
      validation.errors.push(`Invalid type. Must be one of: ${validTypes.join(', ')}`);
    }
    
    // Validar algoritmo
    if (!algorithm || typeof algorithm !== 'string') {
      validation.errors.push('Algorithm must be a non-empty string');
    }
    
    // Validar parámetros
    if (parameters && typeof parameters !== 'object') {
      validation.errors.push('Parameters must be an object');
    }
    
    // Sugerencias
    if (!parameters || Object.keys(parameters).length === 0) {
      validation.suggestions.push('Consider adding algorithm parameters for better performance');
    }
    
    res.json({
      success: true,
      data: validation
    });
  } catch (error) {
    console.error('Error validating recommendation engine:', error);
    res.status(500).json({ error: 'Failed to validate recommendation engine' });
  }
});

export default router;

