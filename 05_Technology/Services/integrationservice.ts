import { EventEmitter } from 'events';
import axios from 'axios';
import { CustomerFeedback } from './customerFeedbackService';

export interface IntegrationConfig {
  id: string;
  name: string;
  type: 'webhook' | 'api' | 'sftp' | 'email' | 'social_media' | 'crm' | 'helpdesk';
  enabled: boolean;
  credentials: Record<string, any>;
  settings: Record<string, any>;
  mapping: Record<string, string>;
  filters: IntegrationFilter[];
  retryPolicy: {
    maxRetries: number;
    retryDelay: number;
    backoffMultiplier: number;
  };
  rateLimit: {
    requestsPerMinute: number;
    burstLimit: number;
  };
  webhook?: {
    url: string;
    secret: string;
    events: string[];
  };
  lastSync?: Date;
  syncCount: number;
  errorCount: number;
  status: 'active' | 'inactive' | 'error' | 'syncing';
}

export interface IntegrationFilter {
  field: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'greater_than' | 'less_than' | 'in' | 'not_in';
  value: any;
  logicalOperator?: 'AND' | 'OR';
}

export interface IntegrationSync {
  id: string;
  integrationId: string;
  type: 'push' | 'pull' | 'bidirectional';
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  startedAt: Date;
  completedAt?: Date;
  duration?: number;
  recordsProcessed: number;
  recordsSuccessful: number;
  recordsFailed: number;
  errors: string[];
  result?: any;
}

export interface IntegrationWebhook {
  id: string;
  integrationId: string;
  event: string;
  payload: any;
  timestamp: Date;
  processed: boolean;
  retryCount: number;
  maxRetries: number;
  nextRetry?: Date;
  error?: string;
}

export class IntegrationService extends EventEmitter {
  private integrations: Map<string, IntegrationConfig> = new Map();
  private syncs: Map<string, IntegrationSync> = new Map();
  private webhooks: Map<string, IntegrationWebhook> = new Map();
  private isProcessing: boolean = false;
  private processingQueue: any[] = [];
  private processingInterval: NodeJS.Timeout | null = null;

  constructor() {
    super();
    this.initializeDefaultIntegrations();
    this.startProcessing();
  }

  // Inicializar integraciones por defecto
  private initializeDefaultIntegrations(): void {
    // Integración con Salesforce
    const salesforceIntegration: IntegrationConfig = {
      id: 'salesforce_crm',
      name: 'Salesforce CRM',
      type: 'crm',
      enabled: true,
      credentials: {
        username: process.env.SALESFORCE_USERNAME || '',
        password: process.env.SALESFORCE_PASSWORD || '',
        securityToken: process.env.SALESFORCE_SECURITY_TOKEN || '',
        instanceUrl: process.env.SALESFORCE_INSTANCE_URL || ''
      },
      settings: {
        objectType: 'Case',
        fields: ['Subject', 'Description', 'Priority', 'Status', 'Origin'],
        batchSize: 100
      },
      mapping: {
        'content': 'Description',
        'urgency': 'Priority',
        'source': 'Origin',
        'sentiment': 'Custom_Field__c'
      },
      filters: [
        {
          field: 'sentiment',
          operator: 'not_equals',
          value: 'neutral'
        }
      ],
      retryPolicy: {
        maxRetries: 3,
        retryDelay: 1000,
        backoffMultiplier: 2
      },
      rateLimit: {
        requestsPerMinute: 1000,
        burstLimit: 100
      },
      syncCount: 0,
      errorCount: 0,
      status: 'active'
    };

    // Integración con Zendesk
    const zendeskIntegration: IntegrationConfig = {
      id: 'zendesk_helpdesk',
      name: 'Zendesk Helpdesk',
      type: 'helpdesk',
      enabled: true,
      credentials: {
        subdomain: process.env.ZENDESK_SUBDOMAIN || '',
        username: process.env.ZENDESK_USERNAME || '',
        token: process.env.ZENDESK_TOKEN || ''
      },
      settings: {
        ticketType: 'ticket',
        fields: ['subject', 'description', 'priority', 'status', 'tags'],
        batchSize: 50
      },
      mapping: {
        'content': 'description',
        'urgency': 'priority',
        'source': 'via',
        'sentiment': 'custom_field'
      },
      filters: [
        {
          field: 'urgency',
          operator: 'in',
          value: ['high', 'critical']
        }
      ],
      retryPolicy: {
        maxRetries: 3,
        retryDelay: 2000,
        backoffMultiplier: 1.5
      },
      rateLimit: {
        requestsPerMinute: 700,
        burstLimit: 50
      },
      syncCount: 0,
      errorCount: 0,
      status: 'active'
    };

    // Integración con HubSpot
    const hubspotIntegration: IntegrationConfig = {
      id: 'hubspot_crm',
      name: 'HubSpot CRM',
      type: 'crm',
      enabled: true,
      credentials: {
        apiKey: process.env.HUBSPOT_API_KEY || '',
        portalId: process.env.HUBSPOT_PORTAL_ID || ''
      },
      settings: {
        objectType: 'tickets',
        properties: ['subject', 'content', 'hs_ticket_priority', 'hs_ticket_category'],
        batchSize: 100
      },
      mapping: {
        'content': 'content',
        'urgency': 'hs_ticket_priority',
        'source': 'hs_ticket_source',
        'sentiment': 'sentiment_score'
      },
      filters: [],
      retryPolicy: {
        maxRetries: 3,
        retryDelay: 1000,
        backoffMultiplier: 2
      },
      rateLimit: {
        requestsPerMinute: 100,
        burstLimit: 10
      },
      syncCount: 0,
      errorCount: 0,
      status: 'active'
    };

    // Integración con Slack
    const slackIntegration: IntegrationConfig = {
      id: 'slack_notifications',
      name: 'Slack Notifications',
      type: 'webhook',
      enabled: true,
      credentials: {
        webhookUrl: process.env.SLACK_WEBHOOK_URL || ''
      },
      settings: {
        channel: '#feedback-alerts',
        username: 'Feedback Bot',
        iconEmoji: ':robot_face:'
      },
      mapping: {
        'content': 'text',
        'urgency': 'color',
        'source': 'fields',
        'sentiment': 'fields'
      },
      filters: [
        {
          field: 'urgency',
          operator: 'in',
          value: ['high', 'critical']
        }
      ],
      retryPolicy: {
        maxRetries: 3,
        retryDelay: 1000,
        backoffMultiplier: 2
      },
      rateLimit: {
        requestsPerMinute: 100,
        burstLimit: 20
      },
      webhook: {
        url: process.env.SLACK_WEBHOOK_URL || '',
        secret: process.env.SLACK_WEBHOOK_SECRET || '',
        events: ['feedback_created', 'feedback_updated', 'anomaly_detected']
      },
      syncCount: 0,
      errorCount: 0,
      status: 'active'
    };

    this.integrations.set(salesforceIntegration.id, salesforceIntegration);
    this.integrations.set(zendeskIntegration.id, zendeskIntegration);
    this.integrations.set(hubspotIntegration.id, hubspotIntegration);
    this.integrations.set(slackIntegration.id, slackIntegration);
  }

  // Iniciar procesamiento
  private startProcessing(): void {
    this.processingInterval = setInterval(() => {
      this.processQueue();
    }, 5000); // Cada 5 segundos
  }

  // Detener procesamiento
  stopProcessing(): void {
    if (this.processingInterval) {
      clearInterval(this.processingInterval);
      this.processingInterval = null;
    }
  }

  // Procesar cola de integraciones
  private async processQueue(): Promise<void> {
    if (this.isProcessing || this.processingQueue.length === 0) return;

    this.isProcessing = true;
    const item = this.processingQueue.shift();

    try {
      await this.processIntegrationItem(item);
    } catch (error) {
      console.error('Error processing integration item:', error);
    } finally {
      this.isProcessing = false;
    }
  }

  // Procesar elemento de integración
  private async processIntegrationItem(item: any): Promise<void> {
    const { integrationId, type, data } = item;
    const integration = this.integrations.get(integrationId);

    if (!integration || !integration.enabled) return;

    const sync: IntegrationSync = {
      id: `sync_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      integrationId,
      type,
      status: 'running',
      startedAt: new Date(),
      recordsProcessed: 0,
      recordsSuccessful: 0,
      recordsFailed: 0,
      errors: []
    };

    this.syncs.set(sync.id, sync);
    this.emit('sync_started', sync);

    try {
      switch (integration.type) {
        case 'crm':
          await this.syncWithCRM(integration, data, sync);
          break;
        case 'helpdesk':
          await this.syncWithHelpdesk(integration, data, sync);
          break;
        case 'webhook':
          await this.sendWebhook(integration, data, sync);
          break;
        case 'social_media':
          await this.syncWithSocialMedia(integration, data, sync);
          break;
        default:
          throw new Error(`Unsupported integration type: ${integration.type}`);
      }

      sync.status = 'completed';
      sync.completedAt = new Date();
      sync.duration = sync.completedAt.getTime() - sync.startedAt.getTime();
      
      integration.syncCount++;
      integration.lastSync = new Date();
      integration.status = 'active';

      this.emit('sync_completed', sync);
    } catch (error) {
      sync.status = 'failed';
      sync.error = error.message;
      sync.completedAt = new Date();
      sync.duration = sync.completedAt.getTime() - sync.startedAt.getTime();
      
      integration.errorCount++;
      integration.status = 'error';

      this.emit('sync_failed', sync);
    }
  }

  // Sincronizar con CRM
  private async syncWithCRM(integration: IntegrationConfig, data: any, sync: IntegrationSync): Promise<void> {
    const { credentials, settings, mapping } = integration;
    
    // Simular sincronización con CRM
    console.log(`Syncing with ${integration.name}:`, {
      objectType: settings.objectType,
      records: Array.isArray(data) ? data.length : 1
    });

    // Simular procesamiento de registros
    const records = Array.isArray(data) ? data : [data];
    sync.recordsProcessed = records.length;
    sync.recordsSuccessful = records.length;
    sync.recordsFailed = 0;

    // Simular delay de red
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  // Sincronizar con Helpdesk
  private async syncWithHelpdesk(integration: IntegrationConfig, data: any, sync: IntegrationSync): Promise<void> {
    const { credentials, settings, mapping } = integration;
    
    // Simular sincronización con Helpdesk
    console.log(`Syncing with ${integration.name}:`, {
      ticketType: settings.ticketType,
      records: Array.isArray(data) ? data.length : 1
    });

    // Simular procesamiento de tickets
    const records = Array.isArray(data) ? data : [data];
    sync.recordsProcessed = records.length;
    sync.recordsSuccessful = records.length;
    sync.recordsFailed = 0;

    // Simular delay de red
    await new Promise(resolve => setTimeout(resolve, 1500));
  }

  // Enviar webhook
  private async sendWebhook(integration: IntegrationConfig, data: any, sync: IntegrationSync): Promise<void> {
    const { credentials, settings } = integration;
    
    if (!credentials.webhookUrl) {
      throw new Error('Webhook URL not configured');
    }

    const payload = this.formatWebhookPayload(data, settings);
    
    try {
      const response = await axios.post(credentials.webhookUrl, payload, {
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'AI-Marketing-Feedback-System/1.0'
        },
        timeout: 10000
      });

      sync.recordsProcessed = 1;
      sync.recordsSuccessful = 1;
      sync.recordsFailed = 0;
      sync.result = response.data;

      console.log(`Webhook sent to ${integration.name}:`, response.status);
    } catch (error) {
      sync.recordsProcessed = 1;
      sync.recordsSuccessful = 0;
      sync.recordsFailed = 1;
      sync.errors.push(error.message);
      throw error;
    }
  }

  // Sincronizar con redes sociales
  private async syncWithSocialMedia(integration: IntegrationConfig, data: any, sync: IntegrationSync): Promise<void> {
    const { credentials, settings } = integration;
    
    // Simular sincronización con redes sociales
    console.log(`Syncing with ${integration.name}:`, {
      platform: settings.platform,
      records: Array.isArray(data) ? data.length : 1
    });

    // Simular procesamiento de posts
    const records = Array.isArray(data) ? data : [data];
    sync.recordsProcessed = records.length;
    sync.recordsSuccessful = records.length;
    sync.recordsFailed = 0;

    // Simular delay de red
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  // Formatear payload de webhook
  private formatWebhookPayload(data: any, settings: any): any {
    return {
      text: data.content || 'New feedback received',
      channel: settings.channel || '#general',
      username: settings.username || 'Feedback Bot',
      icon_emoji: settings.iconEmoji || ':robot_face:',
      attachments: [
        {
          color: this.getUrgencyColor(data.urgency),
          fields: [
            {
              title: 'Source',
              value: data.source || 'Unknown',
              short: true
            },
            {
              title: 'Sentiment',
              value: data.sentiment || 'Neutral',
              short: true
            },
            {
              title: 'Urgency',
              value: data.urgency || 'Low',
              short: true
            },
            {
              title: 'Region',
              value: data.region || 'Unknown',
              short: true
            }
          ],
          footer: 'AI Marketing Feedback System',
          ts: Math.floor(Date.now() / 1000)
        }
      ]
    };
  }

  // Obtener color según urgencia
  private getUrgencyColor(urgency: string): string {
    switch (urgency) {
      case 'critical': return 'danger';
      case 'high': return 'warning';
      case 'medium': return 'good';
      case 'low': return '#36a64f';
      default: return '#36a64f';
    }
  }

  // Procesar feedback para integraciones
  processFeedback(feedback: CustomerFeedback): void {
    const enabledIntegrations = Array.from(this.integrations.values())
      .filter(integration => integration.enabled);

    for (const integration of enabledIntegrations) {
      // Verificar filtros
      if (this.matchesFilters(feedback, integration.filters)) {
        this.processingQueue.push({
          integrationId: integration.id,
          type: 'push',
          data: this.mapFeedback(feedback, integration.mapping)
        });
      }
    }
  }

  // Verificar si el feedback coincide con los filtros
  private matchesFilters(feedback: CustomerFeedback, filters: IntegrationFilter[]): boolean {
    if (filters.length === 0) return true;

    let result = true;
    let logicalOperator = 'AND';

    for (const filter of filters) {
      const fieldValue = this.getFieldValue(feedback, filter.field);
      const conditionResult = this.evaluateCondition(fieldValue, filter.operator, filter.value);
      
      if (logicalOperator === 'AND') {
        result = result && conditionResult;
      } else if (logicalOperator === 'OR') {
        result = result || conditionResult;
      }
      
      logicalOperator = filter.logicalOperator || 'AND';
    }

    return result;
  }

  // Evaluar condición
  private evaluateCondition(fieldValue: any, operator: string, conditionValue: any): boolean {
    switch (operator) {
      case 'equals':
        return fieldValue === conditionValue;
      case 'not_equals':
        return fieldValue !== conditionValue;
      case 'contains':
        return String(fieldValue).toLowerCase().includes(String(conditionValue).toLowerCase());
      case 'not_contains':
        return !String(fieldValue).toLowerCase().includes(String(conditionValue).toLowerCase());
      case 'greater_than':
        return Number(fieldValue) > Number(conditionValue);
      case 'less_than':
        return Number(fieldValue) < Number(conditionValue);
      case 'in':
        return Array.isArray(conditionValue) && conditionValue.includes(fieldValue);
      case 'not_in':
        return Array.isArray(conditionValue) && !conditionValue.includes(fieldValue);
      default:
        return false;
    }
  }

  // Obtener valor del campo
  private getFieldValue(feedback: CustomerFeedback, field: string): any {
    const fields = field.split('.');
    let value = feedback;
    
    for (const f of fields) {
      if (value && typeof value === 'object' && f in value) {
        value = value[f];
      } else {
        return undefined;
      }
    }
    
    return value;
  }

  // Mapear feedback según configuración
  private mapFeedback(feedback: CustomerFeedback, mapping: Record<string, string>): any {
    const mapped: any = {};
    
    for (const [sourceField, targetField] of Object.entries(mapping)) {
      const value = this.getFieldValue(feedback, sourceField);
      if (value !== undefined) {
        mapped[targetField] = value;
      }
    }
    
    return mapped;
  }

  // Crear integración
  createIntegration(integration: Omit<IntegrationConfig, 'id' | 'syncCount' | 'errorCount' | 'status'>): string {
    const id = `integration_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newIntegration: IntegrationConfig = {
      ...integration,
      id,
      syncCount: 0,
      errorCount: 0,
      status: 'active'
    };

    this.integrations.set(id, newIntegration);
    this.emit('integration_created', newIntegration);
    return id;
  }

  // Actualizar integración
  updateIntegration(id: string, updates: Partial<IntegrationConfig>): boolean {
    const integration = this.integrations.get(id);
    if (!integration) return false;

    const updatedIntegration = {
      ...integration,
      ...updates,
      id
    };

    this.integrations.set(id, updatedIntegration);
    this.emit('integration_updated', updatedIntegration);
    return true;
  }

  // Eliminar integración
  deleteIntegration(id: string): boolean {
    const integration = this.integrations.get(id);
    if (!integration) return false;

    this.integrations.delete(id);
    this.emit('integration_deleted', integration);
    return true;
  }

  // Obtener integraciones
  getIntegrations(): IntegrationConfig[] {
    return Array.from(this.integrations.values());
  }

  // Obtener integración específica
  getIntegration(id: string): IntegrationConfig | undefined {
    return this.integrations.get(id);
  }

  // Obtener sincronizaciones
  getSyncs(limit?: number): IntegrationSync[] {
    const syncs = Array.from(this.syncs.values())
      .sort((a, b) => b.startedAt.getTime() - a.startedAt.getTime());
    
    return limit ? syncs.slice(0, limit) : syncs;
  }

  // Obtener estadísticas
  getStats(): {
    totalIntegrations: number;
    activeIntegrations: number;
    totalSyncs: number;
    successfulSyncs: number;
    failedSyncs: number;
    averageSyncTime: number;
    recentSyncs: IntegrationSync[];
  } {
    const integrations = Array.from(this.integrations.values());
    const syncs = Array.from(this.syncs.values());
    
    const totalSyncs = syncs.length;
    const successfulSyncs = syncs.filter(s => s.status === 'completed').length;
    const failedSyncs = syncs.filter(s => s.status === 'failed').length;
    
    const averageSyncTime = syncs.length > 0 
      ? syncs.reduce((sum, s) => sum + (s.duration || 0), 0) / syncs.length
      : 0;
    
    return {
      totalIntegrations: integrations.length,
      activeIntegrations: integrations.filter(i => i.enabled).length,
      totalSyncs,
      successfulSyncs,
      failedSyncs,
      averageSyncTime,
      recentSyncs: syncs.slice(0, 10)
    };
  }

  // Probar integración
  async testIntegration(id: string, testData?: any): Promise<boolean> {
    const integration = this.integrations.get(id);
    if (!integration) return false;

    try {
      const testPayload = testData || {
        content: 'Test feedback message',
        sentiment: 'positive',
        urgency: 'low',
        source: 'test',
        region: 'MX'
      };

      this.processingQueue.push({
        integrationId: id,
        type: 'push',
        data: testPayload
      });

      return true;
    } catch (error) {
      console.error(`Error testing integration ${id}:`, error);
      return false;
    }
  }
}

export const integrationService = new IntegrationService();






