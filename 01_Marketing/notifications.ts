import express from 'express';
import { notificationService } from '../services/notificationService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener configuraciones de notificación
router.get('/configs', authenticateToken, (req, res) => {
  try {
    const configs = notificationService.getConfigs();
    
    res.json({
      success: true,
      data: configs,
      count: configs.length
    });
  } catch (error) {
    console.error('Error fetching notification configs:', error);
    res.status(500).json({ error: 'Failed to fetch notification configs' });
  }
});

// Obtener configuración específica
router.get('/configs/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const config = notificationService.getConfig(id);
    
    if (!config) {
      return res.status(404).json({ error: 'Notification config not found' });
    }
    
    res.json({
      success: true,
      data: config
    });
  } catch (error) {
    console.error('Error fetching notification config:', error);
    res.status(500).json({ error: 'Failed to fetch notification config' });
  }
});

// Crear configuración de notificación
router.post('/configs', authenticateToken, (req, res) => {
  try {
    const configData = req.body;
    
    // Validar datos requeridos
    if (!configData.name || !configData.type || !configData.credentials) {
      return res.status(400).json({ 
        error: 'Missing required fields: name, type, credentials' 
      });
    }
    
    const configId = notificationService.createConfig(configData);
    
    res.status(201).json({
      success: true,
      data: { id: configId },
      message: 'Notification config created successfully'
    });
  } catch (error) {
    console.error('Error creating notification config:', error);
    res.status(500).json({ error: 'Failed to create notification config' });
  }
});

// Actualizar configuración de notificación
router.put('/configs/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;
    
    const updated = notificationService.updateConfig(id, updates);
    
    if (!updated) {
      return res.status(404).json({ error: 'Notification config not found' });
    }
    
    res.json({
      success: true,
      message: 'Notification config updated successfully'
    });
  } catch (error) {
    console.error('Error updating notification config:', error);
    res.status(500).json({ error: 'Failed to update notification config' });
  }
});

// Eliminar configuración de notificación
router.delete('/configs/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    
    const deleted = notificationService.deleteConfig(id);
    
    if (!deleted) {
      return res.status(404).json({ error: 'Notification config not found' });
    }
    
    res.json({
      success: true,
      message: 'Notification config deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting notification config:', error);
    res.status(500).json({ error: 'Failed to delete notification config' });
  }
});

// Enviar notificación
router.post('/send', authenticateToken, (req, res) => {
  try {
    const { configId, templateId, recipient, data, priority = 'normal' } = req.body;
    
    if (!configId || !templateId || !recipient || !data) {
      return res.status(400).json({ 
        error: 'Missing required fields: configId, templateId, recipient, data' 
      });
    }
    
    notificationService.sendNotification(configId, templateId, recipient, data, priority);
    
    res.json({
      success: true,
      message: 'Notification sent successfully'
    });
  } catch (error) {
    console.error('Error sending notification:', error);
    res.status(500).json({ error: 'Failed to send notification' });
  }
});

// Obtener mensajes
router.get('/messages', authenticateToken, (req, res) => {
  try {
    const { limit = 50, status } = req.query;
    
    let messages = notificationService.getMessages(parseInt(limit as string));
    
    if (status) {
      messages = messages.filter(msg => msg.status === status);
    }
    
    res.json({
      success: true,
      data: messages,
      count: messages.length
    });
  } catch (error) {
    console.error('Error fetching messages:', error);
    res.status(500).json({ error: 'Failed to fetch messages' });
  }
});

// Obtener estadísticas de notificaciones
router.get('/stats/overview', authenticateToken, (req, res) => {
  try {
    const stats = notificationService.getStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching notification stats:', error);
    res.status(500).json({ error: 'Failed to fetch notification stats' });
  }
});

// Probar configuración de notificación
router.post('/configs/:id/test', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const { testData } = req.body;
    
    const success = notificationService.testConfig(id, testData);
    
    if (!success) {
      return res.status(404).json({ error: 'Notification config not found' });
    }
    
    res.json({
      success: true,
      message: 'Notification test initiated successfully'
    });
  } catch (error) {
    console.error('Error testing notification config:', error);
    res.status(500).json({ error: 'Failed to test notification config' });
  }
});

// Obtener plantillas de notificación
router.get('/templates/list', authenticateToken, (req, res) => {
  try {
    const templates = [
      {
        id: 'feedback_alert_template',
        name: 'Feedback Alert',
        description: 'Template for feedback alerts',
        type: 'email',
        category: 'feedback',
        features: ['HTML Formatting', 'Variable Substitution', 'Priority Levels'],
        variables: ['source', 'sentiment', 'urgency', 'region', 'content', 'processedAt'],
        formats: ['html', 'text']
      },
      {
        id: 'insights_report_template',
        name: 'Insights Report',
        description: 'Template for insights reports',
        type: 'email',
        category: 'report',
        features: ['Rich Formatting', 'List Support', 'Date Formatting'],
        variables: ['date', 'insights', 'recommendations', 'metrics'],
        formats: ['html', 'text']
      },
      {
        id: 'slack_alert_template',
        name: 'Slack Alert',
        description: 'Template for Slack notifications',
        type: 'slack',
        category: 'alert',
        features: ['Emoji Support', 'Channel Routing', 'Rich Formatting'],
        variables: ['source', 'sentiment', 'urgency', 'content'],
        formats: ['text', 'markdown']
      },
      {
        id: 'discord_alert_template',
        name: 'Discord Alert',
        description: 'Template for Discord notifications',
        type: 'discord',
        category: 'alert',
        features: ['Embed Support', 'Mention Support', 'Rich Formatting'],
        variables: ['title', 'description', 'color', 'fields'],
        formats: ['json', 'text']
      },
      {
        id: 'teams_alert_template',
        name: 'Teams Alert',
        description: 'Template for Microsoft Teams notifications',
        type: 'teams',
        category: 'alert',
        features: ['Adaptive Cards', 'Theme Colors', 'Rich Formatting'],
        variables: ['title', 'summary', 'sections', 'themeColor'],
        formats: ['json']
      },
      {
        id: 'webhook_template',
        name: 'Webhook Template',
        description: 'Template for webhook notifications',
        type: 'webhook',
        category: 'integration',
        features: ['Custom Payload', 'JSON Format', 'Flexible Structure'],
        variables: ['message', 'data', 'timestamp', 'metadata'],
        formats: ['json']
      }
    ];
    
    res.json({
      success: true,
      data: templates,
      count: templates.length
    });
  } catch (error) {
    console.error('Error fetching notification templates:', error);
    res.status(500).json({ error: 'Failed to fetch notification templates' });
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
        id: 'feedback_alert_template',
        name: 'Feedback Alert',
        type: 'email',
        enabled: true,
        credentials: {
          host: process.env.SMTP_HOST || 'smtp.gmail.com',
          port: parseInt(process.env.SMTP_PORT || '587'),
          secure: process.env.SMTP_PORT === '465',
          auth: {
            user: process.env.SMTP_USER || '',
            pass: process.env.SMTP_PASS || ''
          }
        },
        settings: {
          from: process.env.SMTP_FROM || 'noreply@company.com',
          replyTo: process.env.SMTP_REPLY_TO || 'support@company.com'
        },
        templates: [
          {
            id: 'feedback_alert',
            name: 'Feedback Alert',
            subject: 'New Feedback Alert - {urgency}',
            content: `
              <h2>New Feedback Alert</h2>
              <p><strong>Source:</strong> {source}</p>
              <p><strong>Sentiment:</strong> {sentiment}</p>
              <p><strong>Urgency:</strong> {urgency}</p>
              <p><strong>Region:</strong> {region}</p>
              <p><strong>Content:</strong></p>
              <blockquote>{content}</blockquote>
              <p><strong>Processed At:</strong> {processedAt}</p>
            `,
            variables: ['source', 'sentiment', 'urgency', 'region', 'content', 'processedAt'],
            format: 'html',
            priority: 'normal',
            category: 'feedback',
            tags: ['alert', 'feedback']
          }
        ],
        filters: [],
        rateLimit: {
          maxPerMinute: 60,
          maxPerHour: 1000,
          maxPerDay: 10000
        },
        retryPolicy: {
          maxRetries: 3,
          retryDelay: 1000,
          backoffMultiplier: 2
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
      credentials: { ...template.credentials, ...customizations.credentials }
    };
    
    const configId = notificationService.createConfig(configData);
    
    res.status(201).json({
      success: true,
      data: { id: configId },
      message: 'Notification config created from template successfully'
    });
  } catch (error) {
    console.error('Error creating notification config from template:', error);
    res.status(500).json({ error: 'Failed to create notification config from template' });
  }
});

// Obtener dashboard de notificaciones
router.get('/dashboard/overview', authenticateToken, (req, res) => {
  try {
    const stats = notificationService.getStats();
    const configs = notificationService.getConfigs();
    const recentMessages = notificationService.getMessages(10);
    
    const dashboard = {
      overview: {
        totalConfigs: stats.totalConfigs,
        activeConfigs: stats.activeConfigs,
        totalMessages: stats.totalMessages,
        sentMessages: stats.sentMessages,
        failedMessages: stats.failedMessages,
        queuedMessages: stats.queuedMessages,
        successRate: stats.totalMessages > 0 
          ? (stats.sentMessages / stats.totalMessages) * 100 
          : 0,
        averageDeliveryTime: stats.averageDeliveryTime
      },
      configs: configs.map(config => ({
        id: config.id,
        name: config.name,
        type: config.type,
        enabled: config.enabled,
        status: config.status,
        lastUsed: config.lastUsed,
        usageCount: config.usageCount,
        errorCount: config.errorCount
      })),
      recentActivity: recentMessages,
      performance: {
        totalMessages: stats.totalMessages,
        sentMessages: stats.sentMessages,
        failedMessages: stats.failedMessages,
        successRate: stats.totalMessages > 0 
          ? (stats.sentMessages / stats.totalMessages) * 100 
          : 0
      }
    };
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    console.error('Error fetching notifications dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch notifications dashboard' });
  }
});

// Obtener logs de notificaciones
router.get('/logs/messages', authenticateToken, (req, res) => {
  try {
    const { configId, status, limit = 50 } = req.query;
    
    let messages = notificationService.getMessages(parseInt(limit as string));
    
    if (configId) {
      messages = messages.filter(msg => msg.configId === configId);
    }
    
    if (status) {
      messages = messages.filter(msg => msg.status === status);
    }
    
    res.json({
      success: true,
      data: messages,
      count: messages.length
    });
  } catch (error) {
    console.error('Error fetching notification logs:', error);
    res.status(500).json({ error: 'Failed to fetch notification logs' });
  }
});

// Validar configuración de notificación
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
      case 'email':
        if (!credentials.host || !credentials.auth?.user || !credentials.auth?.pass) {
          validation.valid = false;
          validation.errors.push('Host, username, and password are required for email configuration');
        }
        break;
      case 'slack':
        if (!credentials.webhookUrl) {
          validation.valid = false;
          validation.errors.push('Webhook URL is required for Slack configuration');
        }
        break;
      case 'discord':
        if (!credentials.webhookUrl) {
          validation.valid = false;
          validation.errors.push('Webhook URL is required for Discord configuration');
        }
        break;
      case 'telegram':
        if (!credentials.botToken) {
          validation.valid = false;
          validation.errors.push('Bot token is required for Telegram configuration');
        }
        break;
      case 'teams':
        if (!credentials.webhookUrl) {
          validation.valid = false;
          validation.errors.push('Webhook URL is required for Teams configuration');
        }
        break;
      default:
        validation.warnings.push(`Unknown notification type: ${type}`);
    }
    
    res.json({
      success: true,
      data: validation
    });
  } catch (error) {
    console.error('Error validating notification configuration:', error);
    res.status(500).json({ error: 'Failed to validate notification configuration' });
  }
});

export default router;






