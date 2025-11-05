import express from 'express';
import { automationService } from '../services/automationService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener reglas de automatización
router.get('/rules', authenticateToken, (req, res) => {
  try {
    const rules = automationService.getRules();
    
    res.json({
      success: true,
      data: rules,
      count: rules.length
    });
  } catch (error) {
    console.error('Error fetching automation rules:', error);
    res.status(500).json({ error: 'Failed to fetch automation rules' });
  }
});

// Obtener regla específica
router.get('/rules/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const rule = automationService.getRule(id);
    
    if (!rule) {
      return res.status(404).json({ error: 'Rule not found' });
    }
    
    res.json({
      success: true,
      data: rule
    });
  } catch (error) {
    console.error('Error fetching automation rule:', error);
    res.status(500).json({ error: 'Failed to fetch automation rule' });
  }
});

// Crear regla de automatización
router.post('/rules', authenticateToken, (req, res) => {
  try {
    const ruleData = req.body;
    
    // Validar datos requeridos
    if (!ruleData.name || !ruleData.conditions || !ruleData.actions || !ruleData.triggers) {
      return res.status(400).json({ 
        error: 'Missing required fields: name, conditions, actions, triggers' 
      });
    }
    
    const ruleId = automationService.createRule(ruleData);
    
    res.status(201).json({
      success: true,
      data: { id: ruleId },
      message: 'Automation rule created successfully'
    });
  } catch (error) {
    console.error('Error creating automation rule:', error);
    res.status(500).json({ error: 'Failed to create automation rule' });
  }
});

// Actualizar regla de automatización
router.put('/rules/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;
    
    const updated = automationService.updateRule(id, updates);
    
    if (!updated) {
      return res.status(404).json({ error: 'Rule not found' });
    }
    
    res.json({
      success: true,
      message: 'Automation rule updated successfully'
    });
  } catch (error) {
    console.error('Error updating automation rule:', error);
    res.status(500).json({ error: 'Failed to update automation rule' });
  }
});

// Eliminar regla de automatización
router.delete('/rules/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    
    const deleted = automationService.deleteRule(id);
    
    if (!deleted) {
      return res.status(404).json({ error: 'Rule not found' });
    }
    
    res.json({
      success: true,
      message: 'Automation rule deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting automation rule:', error);
    res.status(500).json({ error: 'Failed to delete automation rule' });
  }
});

// Obtener ejecuciones de automatización
router.get('/executions', authenticateToken, (req, res) => {
  try {
    const { limit } = req.query;
    const executions = automationService.getExecutions(limit ? parseInt(limit as string) : undefined);
    
    res.json({
      success: true,
      data: executions,
      count: executions.length
    });
  } catch (error) {
    console.error('Error fetching automation executions:', error);
    res.status(500).json({ error: 'Failed to fetch automation executions' });
  }
});

// Obtener estadísticas de automatización
router.get('/stats', authenticateToken, (req, res) => {
  try {
    const stats = automationService.getStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching automation stats:', error);
    res.status(500).json({ error: 'Failed to fetch automation stats' });
  }
});

// Probar regla de automatización
router.post('/rules/:id/test', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const { testData } = req.body;
    
    if (!testData) {
      return res.status(400).json({ error: 'Test data is required' });
    }
    
    const rule = automationService.getRule(id);
    if (!rule) {
      return res.status(404).json({ error: 'Rule not found' });
    }
    
    // Simular ejecución de prueba
    const testResult = {
      ruleId: id,
      ruleName: rule.name,
      testData,
      conditionsMet: true, // Simular que las condiciones se cumplen
      actionsToExecute: rule.actions.length,
      estimatedExecutionTime: rule.actions.length * 1000, // 1 segundo por acción
      warnings: [],
      errors: []
    };
    
    res.json({
      success: true,
      data: testResult,
      message: 'Rule test completed successfully'
    });
  } catch (error) {
    console.error('Error testing automation rule:', error);
    res.status(500).json({ error: 'Failed to test automation rule' });
  }
});

// Ejecutar regla manualmente
router.post('/rules/:id/execute', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const { triggerData } = req.body;
    
    const rule = automationService.getRule(id);
    if (!rule) {
      return res.status(404).json({ error: 'Rule not found' });
    }
    
    if (!rule.enabled) {
      return res.status(400).json({ error: 'Rule is disabled' });
    }
    
    // Simular ejecución manual
    const execution = {
      id: `manual_exec_${Date.now()}`,
      ruleId: id,
      ruleName: rule.name,
      triggerType: 'manual',
      triggerData: triggerData || {},
      status: 'completed',
      startedAt: new Date(),
      completedAt: new Date(),
      duration: 1000,
      actionsExecuted: rule.actions.length,
      actionsSuccessful: rule.actions.length,
      actionsFailed: 0
    };
    
    res.json({
      success: true,
      data: execution,
      message: 'Rule executed successfully'
    });
  } catch (error) {
    console.error('Error executing automation rule:', error);
    res.status(500).json({ error: 'Failed to execute automation rule' });
  }
});

// Obtener plantillas de reglas
router.get('/templates', authenticateToken, (req, res) => {
  try {
    const templates = [
      {
        id: 'critical_feedback_template',
        name: 'Critical Feedback Alert',
        description: 'Alert team when critical feedback is received',
        category: 'alerts',
        conditions: [
          {
            field: 'urgency',
            operator: 'equals',
            value: 'critical'
          }
        ],
        actions: [
          {
            type: 'slack',
            parameters: {
              channel: '#critical-alerts',
              message: '🚨 CRITICAL FEEDBACK: {content}'
            }
          }
        ],
        triggers: [
          {
            type: 'feedback_created',
            parameters: {}
          }
        ]
      },
      {
        id: 'negative_sentiment_template',
        name: 'Negative Sentiment Response',
        description: 'Automatically respond to negative sentiment',
        category: 'response',
        conditions: [
          {
            field: 'sentiment',
            operator: 'equals',
            value: 'negative'
          }
        ],
        actions: [
          {
            type: 'create_task',
            parameters: {
              title: 'Follow up on negative feedback',
              priority: 'high'
            }
          }
        ],
        triggers: [
          {
            type: 'feedback_created',
            parameters: {}
          }
        ]
      },
      {
        id: 'positive_sentiment_template',
        name: 'Positive Sentiment Follow-up',
        description: 'Follow up on positive sentiment feedback',
        category: 'engagement',
        conditions: [
          {
            field: 'sentiment',
            operator: 'equals',
            value: 'positive'
          }
        ],
        actions: [
          {
            type: 'create_task',
            parameters: {
              title: 'Request testimonial from satisfied customer',
              priority: 'medium'
            }
          }
        ],
        triggers: [
          {
            type: 'feedback_created',
            parameters: {}
          }
        ]
      },
      {
        id: 'anomaly_detection_template',
        name: 'Anomaly Detection Alert',
        description: 'Alert when anomalies are detected',
        category: 'monitoring',
        conditions: [
          {
            field: 'anomaly_score',
            operator: 'greater_than',
            value: 0.8
          }
        ],
        actions: [
          {
            type: 'slack',
            parameters: {
              channel: '#anomaly-alerts',
              message: '⚠️ ANOMALY DETECTED: {description}'
            }
          }
        ],
        triggers: [
          {
            type: 'anomaly_detected',
            parameters: {}
          }
        ]
      },
      {
        id: 'high_volume_template',
        name: 'High Volume Alert',
        description: 'Alert when feedback volume exceeds threshold',
        category: 'monitoring',
        conditions: [
          {
            field: 'volume',
            operator: 'greater_than',
            value: 100
          }
        ],
        actions: [
          {
            type: 'slack',
            parameters: {
              channel: '#volume-alerts',
              message: '📈 HIGH VOLUME: {volume} feedbacks received'
            }
          }
        ],
        triggers: [
          {
            type: 'schedule',
            parameters: {
              interval: 'hourly'
            }
          }
        ]
      }
    ];
    
    res.json({
      success: true,
      data: templates,
      count: templates.length
    });
  } catch (error) {
    console.error('Error fetching automation templates:', error);
    res.status(500).json({ error: 'Failed to fetch automation templates' });
  }
});

// Crear regla desde plantilla
router.post('/rules/from-template', authenticateToken, (req, res) => {
  try {
    const { templateId, customizations = {} } = req.body;
    
    if (!templateId) {
      return res.status(400).json({ error: 'Template ID is required' });
    }
    
    // Obtener plantilla (en implementación real, desde base de datos)
    const templates = [
      {
        id: 'critical_feedback_template',
        name: 'Critical Feedback Alert',
        description: 'Alert team when critical feedback is received',
        enabled: true,
        priority: 1,
        conditions: [
          {
            field: 'urgency',
            operator: 'equals',
            value: 'critical'
          }
        ],
        actions: [
          {
            type: 'slack',
            parameters: {
              channel: '#critical-alerts',
              message: '🚨 CRITICAL FEEDBACK: {content}'
            }
          }
        ],
        triggers: [
          {
            type: 'feedback_created',
            parameters: {}
          }
        ]
      }
    ];
    
    const template = templates.find(t => t.id === templateId);
    if (!template) {
      return res.status(404).json({ error: 'Template not found' });
    }
    
    // Aplicar personalizaciones
    const ruleData = {
      ...template,
      ...customizations,
      name: customizations.name || template.name,
      description: customizations.description || template.description
    };
    
    const ruleId = automationService.createRule(ruleData);
    
    res.status(201).json({
      success: true,
      data: { id: ruleId },
      message: 'Automation rule created from template successfully'
    });
  } catch (error) {
    console.error('Error creating rule from template:', error);
    res.status(500).json({ error: 'Failed to create rule from template' });
  }
});

// Obtener logs de automatización
router.get('/logs', authenticateToken, (req, res) => {
  try {
    const { ruleId, status, limit = 50 } = req.query;
    
    let executions = automationService.getExecutions(parseInt(limit as string));
    
    if (ruleId) {
      executions = executions.filter(e => e.ruleId === ruleId);
    }
    
    if (status) {
      executions = executions.filter(e => e.status === status);
    }
    
    res.json({
      success: true,
      data: executions,
      count: executions.length
    });
  } catch (error) {
    console.error('Error fetching automation logs:', error);
    res.status(500).json({ error: 'Failed to fetch automation logs' });
  }
});

// Obtener dashboard de automatización
router.get('/dashboard', authenticateToken, (req, res) => {
  try {
    const stats = automationService.getStats();
    const recentExecutions = automationService.getExecutions(10);
    const rules = automationService.getRules();
    
    const dashboard = {
      overview: {
        totalRules: stats.totalRules,
        activeRules: stats.activeRules,
        totalExecutions: stats.totalExecutions,
        successRate: stats.totalExecutions > 0 
          ? (stats.successfulExecutions / stats.totalExecutions) * 100 
          : 0,
        averageExecutionTime: stats.averageExecutionTime
      },
      recentActivity: recentExecutions,
      ruleStatus: {
        enabled: rules.filter(r => r.enabled).length,
        disabled: rules.filter(r => !r.enabled).length,
        mostExecuted: stats.mostExecutedRule
      },
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
    console.error('Error fetching automation dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch automation dashboard' });
  }
});

export default router;

