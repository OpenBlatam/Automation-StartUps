import express from 'express';
import { advancedDataProcessingService } from '../services/advancedDataProcessingService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener pipelines
router.get('/pipelines', authenticateToken, (req, res) => {
  try {
    const pipelines = advancedDataProcessingService.getPipelines();
    
    res.json({
      success: true,
      data: pipelines,
      count: pipelines.length
    });
  } catch (error) {
    console.error('Error fetching data processing pipelines:', error);
    res.status(500).json({ error: 'Failed to fetch data processing pipelines' });
  }
});

// Obtener pipeline específico
router.get('/pipelines/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const pipelines = advancedDataProcessingService.getPipelines();
    const pipeline = pipelines.find(p => p.id === id);
    
    if (!pipeline) {
      return res.status(404).json({ error: 'Data processing pipeline not found' });
    }
    
    res.json({
      success: true,
      data: pipeline
    });
  } catch (error) {
    console.error('Error fetching data processing pipeline:', error);
    res.status(500).json({ error: 'Failed to fetch data processing pipeline' });
  }
});

// Crear pipeline
router.post('/pipelines', authenticateToken, (req, res) => {
  try {
    const pipelineData = req.body;
    
    // Validar datos requeridos
    if (!pipelineData.name || !pipelineData.stages || !pipelineData.inputSchema || !pipelineData.outputSchema) {
      return res.status(400).json({ 
        error: 'Missing required fields: name, stages, inputSchema, outputSchema' 
      });
    }
    
    const pipelineId = advancedDataProcessingService.createPipeline(pipelineData);
    
    res.status(201).json({
      success: true,
      data: { id: pipelineId },
      message: 'Data processing pipeline created successfully'
    });
  } catch (error) {
    console.error('Error creating data processing pipeline:', error);
    res.status(500).json({ error: 'Failed to create data processing pipeline' });
  }
});

// Ejecutar pipeline
router.post('/pipelines/:id/execute', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const { inputData } = req.body;
    
    if (!inputData || !Array.isArray(inputData)) {
      return res.status(400).json({ error: 'Input data array is required' });
    }
    
    const executionId = advancedDataProcessingService.executePipeline(id, inputData);
    
    res.json({
      success: true,
      data: { executionId },
      message: 'Data processing pipeline execution initiated successfully'
    });
  } catch (error) {
    console.error('Error executing data processing pipeline:', error);
    res.status(500).json({ error: 'Failed to execute data processing pipeline' });
  }
});

// Obtener ejecuciones
router.get('/executions/list', authenticateToken, (req, res) => {
  try {
    const { limit = 50, pipelineId, status } = req.query;
    
    let executions = advancedDataProcessingService.getExecutions(parseInt(limit as string));
    
    if (pipelineId) {
      executions = executions.filter(exec => exec.pipelineId === pipelineId);
    }
    
    if (status) {
      executions = executions.filter(exec => exec.status === status);
    }
    
    res.json({
      success: true,
      data: executions,
      count: executions.length
    });
  } catch (error) {
    console.error('Error fetching data processing executions:', error);
    res.status(500).json({ error: 'Failed to fetch data processing executions' });
  }
});

// Obtener estadísticas de procesamiento de datos
router.get('/stats/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedDataProcessingService.getStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching data processing stats:', error);
    res.status(500).json({ error: 'Failed to fetch data processing stats' });
  }
});

// Obtener dashboard de procesamiento de datos
router.get('/dashboard/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedDataProcessingService.getStats();
    const pipelines = advancedDataProcessingService.getPipelines();
    const recentExecutions = advancedDataProcessingService.getExecutions(10);
    
    const dashboard = {
      overview: {
        totalPipelines: stats.totalPipelines,
        enabledPipelines: stats.enabledPipelines,
        totalExecutions: stats.totalExecutions,
        activeExecutions: stats.activeExecutions,
        successfulExecutions: stats.successfulExecutions,
        failedExecutions: stats.failedExecutions,
        successRate: stats.totalExecutions > 0 
          ? (stats.successfulExecutions / stats.totalExecutions) * 100 
          : 0,
        averageExecutionTime: stats.averageExecutionTime
      },
      pipelines: pipelines.map(pipeline => ({
        id: pipeline.id,
        name: pipeline.name,
        enabled: pipeline.enabled,
        stages: pipeline.stages.length,
        executionCount: pipeline.executionCount,
        successCount: pipeline.successCount,
        failureCount: pipeline.failureCount,
        lastExecuted: pipeline.lastExecuted
      })),
      recentActivity: recentExecutions,
      performance: {
        totalExecutions: stats.totalExecutions,
        successfulExecutions: stats.successfulExecutions,
        failedExecutions: stats.failedExecutions,
        successRate: stats.totalExecutions > 0 
          ? (stats.successfulExecutions / stats.totalExecutions) * 100 
          : 0
      }
    };
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    console.error('Error fetching data processing dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch data processing dashboard' });
  }
});

// Obtener plantillas de pipeline
router.get('/templates/list', authenticateToken, (req, res) => {
  try {
    const templates = [
      {
        id: 'feedback_processing_template',
        name: 'Feedback Processing Pipeline',
        description: 'Complete pipeline for processing customer feedback data',
        category: 'feedback',
        features: ['Validation', 'Normalization', 'Enrichment', 'Analysis'],
        stages: [
          { type: 'validation', name: 'Data Validation' },
          { type: 'normalization', name: 'Data Normalization' },
          { type: 'deduplication', name: 'Deduplication' },
          { type: 'enrichment', name: 'Data Enrichment' },
          { type: 'analysis', name: 'Advanced Analysis' }
        ],
        inputSchema: {
          type: 'object',
          properties: {
            content: { type: 'string' },
            source: { type: 'string' },
            platform: { type: 'string' }
          }
        },
        outputSchema: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            content: { type: 'string' },
            sentiment: { type: 'string' },
            keywords: { type: 'array' },
            urgency: { type: 'string' }
          }
        }
      },
      {
        id: 'trend_analysis_template',
        name: 'Trend Analysis Pipeline',
        description: 'Pipeline for analyzing trends in data',
        category: 'analytics',
        features: ['Data Collection', 'Trend Detection', 'Anomaly Detection', 'Insight Generation'],
        stages: [
          { type: 'aggregation', name: 'Data Collection' },
          { type: 'analysis', name: 'Trend Detection' },
          { type: 'analysis', name: 'Anomaly Detection' },
          { type: 'analysis', name: 'Insight Generation' }
        ],
        inputSchema: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              date: { type: 'string' },
              value: { type: 'number' }
            }
          }
        },
        outputSchema: {
          type: 'object',
          properties: {
            trends: { type: 'array' },
            anomalies: { type: 'array' },
            insights: { type: 'array' }
          }
        }
      },
      {
        id: 'data_cleaning_template',
        name: 'Data Cleaning Pipeline',
        description: 'Pipeline for cleaning and standardizing data',
        category: 'data_quality',
        features: ['Validation', 'Normalization', 'Deduplication', 'Standardization'],
        stages: [
          { type: 'validation', name: 'Data Validation' },
          { type: 'normalization', name: 'Data Normalization' },
          { type: 'deduplication', name: 'Deduplication' },
          { type: 'transformation', name: 'Data Standardization' }
        ],
        inputSchema: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              id: { type: 'string' },
              data: { type: 'string' }
            }
          }
        },
        outputSchema: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              id: { type: 'string' },
              cleanedData: { type: 'string' },
              qualityScore: { type: 'number' }
            }
          }
        }
      },
      {
        id: 'sentiment_analysis_template',
        name: 'Sentiment Analysis Pipeline',
        description: 'Pipeline for analyzing sentiment in text data',
        category: 'nlp',
        features: ['Text Preprocessing', 'Sentiment Analysis', 'Emotion Detection', 'Topic Classification'],
        stages: [
          { type: 'normalization', name: 'Text Preprocessing' },
          { type: 'enrichment', name: 'Sentiment Analysis' },
          { type: 'analysis', name: 'Emotion Detection' },
          { type: 'analysis', name: 'Topic Classification' }
        ],
        inputSchema: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              text: { type: 'string' },
              language: { type: 'string' }
            }
          }
        },
        outputSchema: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              text: { type: 'string' },
              sentiment: { type: 'string' },
              emotion: { type: 'string' },
              topics: { type: 'array' }
            }
          }
        }
      },
      {
        id: 'data_aggregation_template',
        name: 'Data Aggregation Pipeline',
        description: 'Pipeline for aggregating and summarizing data',
        category: 'analytics',
        features: ['Grouping', 'Aggregation', 'Summarization', 'Reporting'],
        stages: [
          { type: 'filtering', name: 'Data Filtering' },
          { type: 'aggregation', name: 'Data Aggregation' },
          { type: 'transformation', name: 'Data Summarization' },
          { type: 'action', name: 'Generate Report' }
        ],
        inputSchema: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              category: { type: 'string' },
              value: { type: 'number' },
              date: { type: 'string' }
            }
          }
        },
        outputSchema: {
          type: 'object',
          properties: {
            summary: { type: 'object' },
            aggregations: { type: 'object' },
            report: { type: 'object' }
          }
        }
      }
    ];
    
    res.json({
      success: true,
      data: templates,
      count: templates.length
    });
  } catch (error) {
    console.error('Error fetching data processing templates:', error);
    res.status(500).json({ error: 'Failed to fetch data processing templates' });
  }
});

// Crear pipeline desde plantilla
router.post('/pipelines/from-template', authenticateToken, (req, res) => {
  try {
    const { templateId, customizations = {} } = req.body;
    
    if (!templateId) {
      return res.status(400).json({ error: 'Template ID is required' });
    }
    
    // Obtener plantilla (en implementación real, desde base de datos)
    const templates = [
      {
        id: 'feedback_processing_template',
        name: 'Feedback Processing Pipeline',
        description: 'Complete pipeline for processing customer feedback data',
        enabled: true,
        stages: [
          {
            id: 'validation',
            name: 'Data Validation',
            type: 'validation',
            order: 1,
            enabled: true,
            config: {
              rules: [
                { field: 'content', required: true, minLength: 10 },
                { field: 'source', required: true }
              ]
            },
            dependencies: []
          },
          {
            id: 'normalization',
            name: 'Data Normalization',
            type: 'normalization',
            order: 2,
            enabled: true,
            config: {
              rules: [
                { field: 'content', trim: true },
                { field: 'source', toLowerCase: true }
              ]
            },
            dependencies: ['validation']
          },
          {
            id: 'enrichment',
            name: 'Data Enrichment',
            type: 'enrichment',
            order: 3,
            enabled: true,
            config: {
              enrichments: [
                { type: 'sentiment_analysis', fields: ['content'] },
                { type: 'keyword_extraction', fields: ['content'] }
              ]
            },
            dependencies: ['normalization']
          }
        ],
        inputSchema: {
          type: 'object',
          properties: {
            content: { type: 'string' },
            source: { type: 'string' },
            platform: { type: 'string' }
          }
        },
        outputSchema: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            content: { type: 'string' },
            sentiment: { type: 'string' },
            keywords: { type: 'array' }
          }
        },
        settings: {
          batchSize: 100,
          maxConcurrency: 5,
          errorHandling: 'continue',
          logging: {
            enabled: true,
            level: 'info'
          },
          monitoring: {
            enabled: true,
            metrics: ['processing_time', 'success_rate']
          }
        }
      }
    ];
    
    const template = templates.find(t => t.id === templateId);
    if (!template) {
      return res.status(404).json({ error: 'Template not found' });
    }
    
    // Aplicar personalizaciones
    const pipelineData = {
      ...template,
      ...customizations,
      name: customizations.name || template.name,
      description: customizations.description || template.description
    };
    
    const pipelineId = advancedDataProcessingService.createPipeline(pipelineData);
    
    res.status(201).json({
      success: true,
      data: { id: pipelineId },
      message: 'Data processing pipeline created from template successfully'
    });
  } catch (error) {
    console.error('Error creating data processing pipeline from template:', error);
    res.status(500).json({ error: 'Failed to create data processing pipeline from template' });
  }
});

// Validar configuración de pipeline
router.post('/validate', authenticateToken, (req, res) => {
  try {
    const { name, stages, inputSchema, outputSchema, settings } = req.body;
    
    if (!name || !stages || !inputSchema || !outputSchema) {
      return res.status(400).json({ error: 'Name, stages, inputSchema, and outputSchema are required' });
    }
    
    // Simular validación de configuración
    const validation = {
      valid: true,
      errors: [],
      warnings: [],
      suggestions: []
    };
    
    // Validar stages
    if (!Array.isArray(stages) || stages.length === 0) {
      validation.errors.push('At least one stage is required');
    }
    
    for (let i = 0; i < stages.length; i++) {
      const stage = stages[i];
      if (!stage.name || !stage.type) {
        validation.errors.push(`Stage ${i + 1} must have name and type`);
      }
      if (!stage.order || stage.order < 1) {
        validation.errors.push(`Stage ${i + 1} must have a valid order`);
      }
    }
    
    // Validar schemas
    if (!inputSchema.type) {
      validation.errors.push('Input schema must have a type');
    }
    
    if (!outputSchema.type) {
      validation.errors.push('Output schema must have a type');
    }
    
    // Validar settings
    if (settings) {
      if (settings.batchSize && settings.batchSize < 1) {
        validation.errors.push('Batch size must be greater than 0');
      }
      if (settings.maxConcurrency && settings.maxConcurrency < 1) {
        validation.errors.push('Max concurrency must be greater than 0');
      }
    }
    
    // Sugerencias
    if (stages.length > 10) {
      validation.warnings.push('Consider breaking down pipelines with many stages');
    }
    
    if (!settings || !settings.monitoring) {
      validation.suggestions.push('Consider adding monitoring configuration for better observability');
    }
    
    res.json({
      success: true,
      data: validation
    });
  } catch (error) {
    console.error('Error validating data processing pipeline configuration:', error);
    res.status(500).json({ error: 'Failed to validate data processing pipeline configuration' });
  }
});

export default router;






