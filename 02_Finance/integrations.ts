import express from 'express';
import { integrationService } from '../services/integrationService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener integraciones
router.get('/', authenticateToken, (req, res) => {
  try {
    const integrations = integrationService.getIntegrations();
    
    res.json({
      success: true,
      data: integrations,
      count: integrations.length
    });
  } catch (error) {
    console.error('Error fetching integrations:', error);
    res.status(500).json({ error: 'Failed to fetch integrations' });
  }
});

// Obtener integración específica
router.get('/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const integration = integrationService.getIntegration(id);
    
    if (!integration) {
      return res.status(404).json({ error: 'Integration not found' });
    }
    
    res.json({
      success: true,
      data: integration
    });
  } catch (error) {
    console.error('Error fetching integration:', error);
    res.status(500).json({ error: 'Failed to fetch integration' });
  }
});

// Crear integración
router.post('/', authenticateToken, (req, res) => {
  try {
    const integrationData = req.body;
    
    // Validar datos requeridos
    if (!integrationData.name || !integrationData.type || !integrationData.credentials) {
      return res.status(400).json({ 
        error: 'Missing required fields: name, type, credentials' 
      });
    }
    
    const integrationId = integrationService.createIntegration(integrationData);
    
    res.status(201).json({
      success: true,
      data: { id: integrationId },
      message: 'Integration created successfully'
    });
  } catch (error) {
    console.error('Error creating integration:', error);
    res.status(500).json({ error: 'Failed to create integration' });
  }
});

// Actualizar integración
router.put('/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;
    
    const updated = integrationService.updateIntegration(id, updates);
    
    if (!updated) {
      return res.status(404).json({ error: 'Integration not found' });
    }
    
    res.json({
      success: true,
      message: 'Integration updated successfully'
    });
  } catch (error) {
    console.error('Error updating integration:', error);
    res.status(500).json({ error: 'Failed to update integration' });
  }
});

// Eliminar integración
router.delete('/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    
    const deleted = integrationService.deleteIntegration(id);
    
    if (!deleted) {
      return res.status(404).json({ error: 'Integration not found' });
    }
    
    res.json({
      success: true,
      message: 'Integration deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting integration:', error);
    res.status(500).json({ error: 'Failed to delete integration' });
  }
});

// Probar integración
router.post('/:id/test', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const { testData } = req.body;
    
    const success = integrationService.testIntegration(id, testData);
    
    if (!success) {
      return res.status(404).json({ error: 'Integration not found' });
    }
    
    res.json({
      success: true,
      message: 'Integration test initiated successfully'
    });
  } catch (error) {
    console.error('Error testing integration:', error);
    res.status(500).json({ error: 'Failed to test integration' });
  }
});

// Obtener sincronizaciones
router.get('/:id/syncs', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const { limit } = req.query;
    
    const integration = integrationService.getIntegration(id);
    if (!integration) {
      return res.status(404).json({ error: 'Integration not found' });
    }
    
    const syncs = integrationService.getSyncs(limit ? parseInt(limit as string) : undefined)
      .filter(sync => sync.integrationId === id);
    
    res.json({
      success: true,
      data: syncs,
      count: syncs.length
    });
  } catch (error) {
    console.error('Error fetching integration syncs:', error);
    res.status(500).json({ error: 'Failed to fetch integration syncs' });
  }
});

// Obtener estadísticas de integraciones
router.get('/stats/overview', authenticateToken, (req, res) => {
  try {
    const stats = integrationService.getStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching integration stats:', error);
    res.status(500).json({ error: 'Failed to fetch integration stats' });
  }
});

// Obtener plantillas de integración
router.get('/templates/list', authenticateToken, (req, res) => {
  try {
    const templates = [
      {
        id: 'salesforce_template',
        name: 'Salesforce CRM',
        type: 'crm',
        description: 'Integrate with Salesforce CRM for case management',
        icon: 'salesforce',
        category: 'crm',
        features: ['Case Creation', 'Field Mapping', 'Bidirectional Sync'],
        configuration: {
          requiredFields: ['username', 'password', 'securityToken', 'instanceUrl'],
          optionalFields: ['objectType', 'fields', 'batchSize'],
          mapping: {
            'content': 'Description',
            'urgency': 'Priority',
            'source': 'Origin'
          }
        }
      },
      {
        id: 'zendesk_template',
        name: 'Zendesk Helpdesk',
        type: 'helpdesk',
        description: 'Integrate with Zendesk for ticket management',
        icon: 'zendesk',
        category: 'helpdesk',
        features: ['Ticket Creation', 'Status Updates', 'Priority Mapping'],
        configuration: {
          requiredFields: ['subdomain', 'username', 'token'],
          optionalFields: ['ticketType', 'fields', 'batchSize'],
          mapping: {
            'content': 'description',
            'urgency': 'priority',
            'source': 'via'
          }
        }
      },
      {
        id: 'hubspot_template',
        name: 'HubSpot CRM',
        type: 'crm',
        description: 'Integrate with HubSpot for contact and ticket management',
        icon: 'hubspot',
        category: 'crm',
        features: ['Contact Creation', 'Ticket Management', 'Property Mapping'],
        configuration: {
          requiredFields: ['apiKey', 'portalId'],
          optionalFields: ['objectType', 'properties', 'batchSize'],
          mapping: {
            'content': 'content',
            'urgency': 'hs_ticket_priority',
            'source': 'hs_ticket_source'
          }
        }
      },
      {
        id: 'slack_template',
        name: 'Slack Notifications',
        type: 'webhook',
        description: 'Send notifications to Slack channels',
        icon: 'slack',
        category: 'notifications',
        features: ['Real-time Alerts', 'Rich Formatting', 'Channel Routing'],
        configuration: {
          requiredFields: ['webhookUrl'],
          optionalFields: ['channel', 'username', 'iconEmoji'],
          mapping: {
            'content': 'text',
            'urgency': 'color',
            'source': 'fields'
          }
        }
      },
      {
        id: 'discord_template',
        name: 'Discord Notifications',
        type: 'webhook',
        description: 'Send notifications to Discord channels',
        icon: 'discord',
        category: 'notifications',
        features: ['Rich Embeds', 'Role Mentions', 'Channel Routing'],
        configuration: {
          requiredFields: ['webhookUrl'],
          optionalFields: ['channel', 'username', 'avatarUrl'],
          mapping: {
            'content': 'content',
            'urgency': 'color',
            'source': 'fields'
          }
        }
      },
      {
        id: 'teams_template',
        name: 'Microsoft Teams',
        type: 'webhook',
        description: 'Send notifications to Microsoft Teams channels',
        icon: 'teams',
        category: 'notifications',
        features: ['Adaptive Cards', 'Channel Integration', 'Rich Formatting'],
        configuration: {
          requiredFields: ['webhookUrl'],
          optionalFields: ['channel', 'title', 'themeColor'],
          mapping: {
            'content': 'text',
            'urgency': 'themeColor',
            'source': 'facts'
          }
        }
      },
      {
        id: 'jira_template',
        name: 'Jira Issue Tracker',
        type: 'api',
        description: 'Create Jira issues from feedback',
        icon: 'jira',
        category: 'issue_tracking',
        features: ['Issue Creation', 'Priority Mapping', 'Custom Fields'],
        configuration: {
          requiredFields: ['baseUrl', 'username', 'apiToken'],
          optionalFields: ['projectKey', 'issueType', 'fields'],
          mapping: {
            'content': 'description',
            'urgency': 'priority',
            'source': 'labels'
          }
        }
      },
      {
        id: 'trello_template',
        name: 'Trello Board',
        type: 'api',
        description: 'Create Trello cards from feedback',
        icon: 'trello',
        category: 'project_management',
        features: ['Card Creation', 'List Assignment', 'Label Mapping'],
        configuration: {
          requiredFields: ['apiKey', 'token', 'boardId'],
          optionalFields: ['listId', 'labels', 'dueDate'],
          mapping: {
            'content': 'desc',
            'urgency': 'labels',
            'source': 'labels'
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
    console.error('Error fetching integration templates:', error);
    res.status(500).json({ error: 'Failed to fetch integration templates' });
  }
});

// Crear integración desde plantilla
router.post('/from-template', authenticateToken, (req, res) => {
  try {
    const { templateId, customizations = {} } = req.body;
    
    if (!templateId) {
      return res.status(400).json({ error: 'Template ID is required' });
    }
    
    // Obtener plantilla (en implementación real, desde base de datos)
    const templates = [
      {
        id: 'salesforce_template',
        name: 'Salesforce CRM',
        type: 'crm',
        enabled: true,
        credentials: {},
        settings: {
          objectType: 'Case',
          fields: ['Subject', 'Description', 'Priority', 'Status', 'Origin'],
          batchSize: 100
        },
        mapping: {
          'content': 'Description',
          'urgency': 'Priority',
          'source': 'Origin'
        },
        filters: [],
        retryPolicy: {
          maxRetries: 3,
          retryDelay: 1000,
          backoffMultiplier: 2
        },
        rateLimit: {
          requestsPerMinute: 1000,
          burstLimit: 100
        }
      }
    ];
    
    const template = templates.find(t => t.id === templateId);
    if (!template) {
      return res.status(404).json({ error: 'Template not found' });
    }
    
    // Aplicar personalizaciones
    const integrationData = {
      ...template,
      ...customizations,
      name: customizations.name || template.name,
      credentials: { ...template.credentials, ...customizations.credentials }
    };
    
    const integrationId = integrationService.createIntegration(integrationData);
    
    res.status(201).json({
      success: true,
      data: { id: integrationId },
      message: 'Integration created from template successfully'
    });
  } catch (error) {
    console.error('Error creating integration from template:', error);
    res.status(500).json({ error: 'Failed to create integration from template' });
  }
});

// Sincronizar integración manualmente
router.post('/:id/sync', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const { data } = req.body;
    
    const integration = integrationService.getIntegration(id);
    if (!integration) {
      return res.status(404).json({ error: 'Integration not found' });
    }
    
    if (!integration.enabled) {
      return res.status(400).json({ error: 'Integration is disabled' });
    }
    
    // Agregar a la cola de procesamiento
    integrationService.processFeedback(data);
    
    res.json({
      success: true,
      message: 'Integration sync initiated successfully'
    });
  } catch (error) {
    console.error('Error syncing integration:', error);
    res.status(500).json({ error: 'Failed to sync integration' });
  }
});

// Obtener logs de integración
router.get('/:id/logs', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const { limit = 50, status } = req.query;
    
    const integration = integrationService.getIntegration(id);
    if (!integration) {
      return res.status(404).json({ error: 'Integration not found' });
    }
    
    let syncs = integrationService.getSyncs(parseInt(limit as string))
      .filter(sync => sync.integrationId === id);
    
    if (status) {
      syncs = syncs.filter(sync => sync.status === status);
    }
    
    res.json({
      success: true,
      data: syncs,
      count: syncs.length
    });
  } catch (error) {
    console.error('Error fetching integration logs:', error);
    res.status(500).json({ error: 'Failed to fetch integration logs' });
  }
});

// Obtener dashboard de integraciones
router.get('/dashboard/overview', authenticateToken, (req, res) => {
  try {
    const stats = integrationService.getStats();
    const integrations = integrationService.getIntegrations();
    const recentSyncs = integrationService.getSyncs(10);
    
    const dashboard = {
      overview: {
        totalIntegrations: stats.totalIntegrations,
        activeIntegrations: stats.activeIntegrations,
        totalSyncs: stats.totalSyncs,
        successRate: stats.totalSyncs > 0 
          ? (stats.successfulSyncs / stats.totalSyncs) * 100 
          : 0,
        averageSyncTime: stats.averageSyncTime
      },
      integrations: integrations.map(integration => ({
        id: integration.id,
        name: integration.name,
        type: integration.type,
        enabled: integration.enabled,
        status: integration.status,
        lastSync: integration.lastSync,
        syncCount: integration.syncCount,
        errorCount: integration.errorCount
      })),
      recentActivity: recentSyncs,
      performance: {
        totalSyncs: stats.totalSyncs,
        successfulSyncs: stats.successfulSyncs,
        failedSyncs: stats.failedSyncs,
        successRate: stats.totalSyncs > 0 
          ? (stats.successfulSyncs / stats.totalSyncs) * 100 
          : 0
      }
    };
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    console.error('Error fetching integrations dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch integrations dashboard' });
  }
});

// Validar configuración de integración
router.post('/validate', authenticateToken, (req, res) => {
  try {
    const { type, credentials, settings } = req.body;
    
    if (!type || !credentials) {
      return res.status(400).json({ error: 'Type and credentials are required' });
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
      case 'crm':
        if (!credentials.username || !credentials.password) {
          validation.valid = false;
          validation.errors.push('Username and password are required for CRM integration');
        }
        break;
      case 'helpdesk':
        if (!credentials.subdomain || !credentials.token) {
          validation.valid = false;
          validation.errors.push('Subdomain and token are required for helpdesk integration');
        }
        break;
      case 'webhook':
        if (!credentials.webhookUrl) {
          validation.valid = false;
          validation.errors.push('Webhook URL is required for webhook integration');
        }
        break;
      default:
        validation.warnings.push(`Unknown integration type: ${type}`);
    }
    
    res.json({
      success: true,
      data: validation
    });
  } catch (error) {
    console.error('Error validating integration configuration:', error);
    res.status(500).json({ error: 'Failed to validate integration configuration' });
  }
});

export default router;






