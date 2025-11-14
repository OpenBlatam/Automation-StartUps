import express from 'express';
import { advancedWorkflowService } from '../services/advancedWorkflowService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener workflows
router.get('/', authenticateToken, (req, res) => {
  try {
    const workflows = advancedWorkflowService.getWorkflows();
    
    res.json({
      success: true,
      data: workflows,
      count: workflows.length
    });
  } catch (error) {
    console.error('Error fetching workflows:', error);
    res.status(500).json({ error: 'Failed to fetch workflows' });
  }
});

// Obtener workflow específico
router.get('/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const workflows = advancedWorkflowService.getWorkflows();
    const workflow = workflows.find(w => w.id === id);
    
    if (!workflow) {
      return res.status(404).json({ error: 'Workflow not found' });
    }
    
    res.json({
      success: true,
      data: workflow
    });
  } catch (error) {
    console.error('Error fetching workflow:', error);
    res.status(500).json({ error: 'Failed to fetch workflow' });
  }
});

// Crear workflow
router.post('/', authenticateToken, (req, res) => {
  try {
    const workflowData = req.body;
    
    // Validar datos requeridos
    if (!workflowData.name || !workflowData.trigger || !workflowData.steps) {
      return res.status(400).json({ 
        error: 'Missing required fields: name, trigger, steps' 
      });
    }
    
    const workflowId = advancedWorkflowService.createWorkflow(workflowData);
    
    res.status(201).json({
      success: true,
      data: { id: workflowId },
      message: 'Workflow created successfully'
    });
  } catch (error) {
    console.error('Error creating workflow:', error);
    res.status(500).json({ error: 'Failed to create workflow' });
  }
});

// Ejecutar workflow
router.post('/:id/execute', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const { triggerData, triggeredBy = 'manual' } = req.body;
    
    const executionId = advancedWorkflowService.executeWorkflow(id, triggerData, triggeredBy);
    
    res.json({
      success: true,
      data: { executionId },
      message: 'Workflow execution initiated successfully'
    });
  } catch (error) {
    console.error('Error executing workflow:', error);
    res.status(500).json({ error: 'Failed to execute workflow' });
  }
});

// Obtener ejecuciones
router.get('/executions/list', authenticateToken, (req, res) => {
  try {
    const { limit = 50, workflowId, status } = req.query;
    
    let executions = advancedWorkflowService.getExecutions(parseInt(limit as string));
    
    if (workflowId) {
      executions = executions.filter(exec => exec.workflowId === workflowId);
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
    console.error('Error fetching workflow executions:', error);
    res.status(500).json({ error: 'Failed to fetch workflow executions' });
  }
});

// Obtener estadísticas de workflows
router.get('/stats/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedWorkflowService.getStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching workflow stats:', error);
    res.status(500).json({ error: 'Failed to fetch workflow stats' });
  }
});

// Obtener dashboard de workflows
router.get('/dashboard/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedWorkflowService.getStats();
    const workflows = advancedWorkflowService.getWorkflows();
    const recentExecutions = advancedWorkflowService.getExecutions(10);
    
    const dashboard = {
      overview: {
        totalWorkflows: stats.totalWorkflows,
        enabledWorkflows: stats.enabledWorkflows,
        totalExecutions: stats.totalExecutions,
        activeExecutions: stats.activeExecutions,
        successfulExecutions: stats.successfulExecutions,
        failedExecutions: stats.failedExecutions,
        successRate: stats.totalExecutions > 0 
          ? (stats.successfulExecutions / stats.totalExecutions) * 100 
          : 0,
        averageExecutionTime: stats.averageExecutionTime
      },
      workflows: workflows.map(workflow => ({
        id: workflow.id,
        name: workflow.name,
        enabled: workflow.enabled,
        version: workflow.version,
        executionCount: workflow.executionCount,
        successCount: workflow.successCount,
        failureCount: workflow.failureCount,
        lastExecuted: workflow.lastExecuted
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
    console.error('Error fetching workflow dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch workflow dashboard' });
  }
});

// Obtener plantillas de workflow
router.get('/templates/list', authenticateToken, (req, res) => {
  try {
    const templates = [
      {
        id: 'feedback_processing_template',
        name: 'Feedback Processing Workflow',
        description: 'Complete workflow for processing customer feedback',
        category: 'feedback',
        features: ['Validation', 'Enrichment', 'Analysis', 'Notification'],
        steps: [
          { type: 'validation', name: 'Data Validation' },
          { type: 'enrichment', name: 'Data Enrichment' },
          { type: 'analysis', name: 'AI Analysis' },
          { type: 'notification', name: 'Team Notification' }
        ],
        triggers: ['event', 'webhook', 'manual']
      },
      {
        id: 'report_generation_template',
        name: 'Report Generation Workflow',
        description: 'Automated report generation and distribution',
        category: 'reporting',
        features: ['Data Collection', 'Analysis', 'Report Generation', 'Distribution'],
        steps: [
          { type: 'data_transform', name: 'Data Collection' },
          { type: 'analysis', name: 'Trend Analysis' },
          { type: 'action', name: 'Generate Report' },
          { type: 'email', name: 'Send Report' }
        ],
        triggers: ['schedule', 'manual']
      },
      {
        id: 'alert_processing_template',
        name: 'Alert Processing Workflow',
        description: 'Process and escalate alerts based on conditions',
        category: 'monitoring',
        features: ['Condition Check', 'Escalation', 'Notification', 'Logging'],
        steps: [
          { type: 'condition', name: 'Check Conditions' },
          { type: 'notification', name: 'Send Alert' },
          { type: 'webhook', name: 'Escalate to System' },
          { type: 'action', name: 'Log Event' }
        ],
        triggers: ['event', 'condition']
      },
      {
        id: 'data_processing_template',
        name: 'Data Processing Workflow',
        description: 'Process and transform data through multiple stages',
        category: 'data',
        features: ['Validation', 'Transformation', 'Enrichment', 'Storage'],
        steps: [
          { type: 'validation', name: 'Data Validation' },
          { type: 'transformation', name: 'Data Transformation' },
          { type: 'enrichment', name: 'Data Enrichment' },
          { type: 'action', name: 'Store Results' }
        ],
        triggers: ['schedule', 'webhook', 'manual']
      },
      {
        id: 'integration_sync_template',
        name: 'Integration Sync Workflow',
        description: 'Synchronize data with external systems',
        category: 'integration',
        features: ['Data Fetch', 'Transform', 'Sync', 'Verify'],
        steps: [
          { type: 'webhook', name: 'Fetch Data' },
          { type: 'transformation', name: 'Transform Data' },
          { type: 'webhook', name: 'Sync to Target' },
          { type: 'action', name: 'Verify Sync' }
        ],
        triggers: ['schedule', 'webhook']
      }
    ];
    
    res.json({
      success: true,
      data: templates,
      count: templates.length
    });
  } catch (error) {
    console.error('Error fetching workflow templates:', error);
    res.status(500).json({ error: 'Failed to fetch workflow templates' });
  }
});

// Crear workflow desde plantilla
router.post('/from-template', authenticateToken, (req, res) => {
  try {
    const { templateId, customizations = {} } = req.body;
    
    if (!templateId) {
      return res.status(400).json({ error: 'Template ID is required' });
    }
    
    // Obtener plantilla (en implementación real, desde base de datos)
    const templates = [
      {
        id: 'feedback_processing_template',
        name: 'Feedback Processing Workflow',
        description: 'Complete workflow for processing customer feedback',
        version: '1.0.0',
        enabled: true,
        trigger: {
          type: 'event',
          event: 'feedback.created'
        },
        steps: [
          {
            id: 'validate_data',
            name: 'Validate Data',
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
            id: 'enrich_data',
            name: 'Enrich Data',
            type: 'enrichment',
            order: 2,
            enabled: true,
            config: {
              enrichments: [
                { type: 'sentiment_analysis', fields: ['content'] },
                { type: 'keyword_extraction', fields: ['content'] }
              ]
            },
            dependencies: ['validate_data']
          },
          {
            id: 'notify_team',
            name: 'Notify Team',
            type: 'notification',
            order: 3,
            enabled: true,
            config: {
              channels: ['email', 'slack'],
              template: 'feedback_processed'
            },
            dependencies: ['enrich_data']
          }
        ],
        conditions: [],
        variables: [],
        settings: {
          maxExecutionTime: 300000,
          maxConcurrentExecutions: 10,
          retryPolicy: {
            maxRetries: 3,
            retryDelay: 1000,
            backoffMultiplier: 2
          },
          errorHandling: 'retry',
          logging: {
            enabled: true,
            level: 'info'
          }
        }
      }
    ];
    
    const template = templates.find(t => t.id === templateId);
    if (!template) {
      return res.status(404).json({ error: 'Template not found' });
    }
    
    // Aplicar personalizaciones
    const workflowData = {
      ...template,
      ...customizations,
      name: customizations.name || template.name,
      description: customizations.description || template.description
    };
    
    const workflowId = advancedWorkflowService.createWorkflow(workflowData);
    
    res.status(201).json({
      success: true,
      data: { id: workflowId },
      message: 'Workflow created from template successfully'
    });
  } catch (error) {
    console.error('Error creating workflow from template:', error);
    res.status(500).json({ error: 'Failed to create workflow from template' });
  }
});

// Validar configuración de workflow
router.post('/validate', authenticateToken, (req, res) => {
  try {
    const { name, trigger, steps, conditions, variables } = req.body;
    
    if (!name || !trigger || !steps) {
      return res.status(400).json({ error: 'Name, trigger, and steps are required' });
    }
    
    // Simular validación de configuración
    const validation = {
      valid: true,
      errors: [],
      warnings: [],
      suggestions: []
    };
    
    // Validar trigger
    if (!trigger.type) {
      validation.errors.push('Trigger type is required');
    }
    
    if (trigger.type === 'event' && !trigger.event) {
      validation.errors.push('Event name is required for event triggers');
    }
    
    if (trigger.type === 'schedule' && !trigger.schedule) {
      validation.errors.push('Schedule configuration is required for schedule triggers');
    }
    
    // Validar steps
    if (!Array.isArray(steps) || steps.length === 0) {
      validation.errors.push('At least one step is required');
    }
    
    for (let i = 0; i < steps.length; i++) {
      const step = steps[i];
      if (!step.name || !step.type) {
        validation.errors.push(`Step ${i + 1} must have name and type`);
      }
      if (!step.order || step.order < 1) {
        validation.errors.push(`Step ${i + 1} must have a valid order`);
      }
    }
    
    // Validar condiciones
    if (conditions && Array.isArray(conditions)) {
      for (let i = 0; i < conditions.length; i++) {
        const condition = conditions[i];
        if (!condition.expression) {
          validation.errors.push(`Condition ${i + 1} must have an expression`);
        }
      }
    }
    
    // Validar variables
    if (variables && Array.isArray(variables)) {
      for (let i = 0; i < variables.length; i++) {
        const variable = variables[i];
        if (!variable.name || !variable.type) {
          validation.errors.push(`Variable ${i + 1} must have name and type`);
        }
      }
    }
    
    // Sugerencias
    if (steps.length > 10) {
      validation.warnings.push('Consider breaking down workflows with many steps');
    }
    
    if (!conditions || conditions.length === 0) {
      validation.suggestions.push('Consider adding conditions for better workflow control');
    }
    
    res.json({
      success: true,
      data: validation
    });
  } catch (error) {
    console.error('Error validating workflow configuration:', error);
    res.status(500).json({ error: 'Failed to validate workflow configuration' });
  }
});

export default router;

