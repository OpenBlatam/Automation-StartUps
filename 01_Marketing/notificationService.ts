import { EventEmitter } from 'events';
import nodemailer from 'nodemailer';
import axios from 'axios';
import { WebSocket } from 'ws';

export interface NotificationConfig {
  id: string;
  name: string;
  type: 'email' | 'slack' | 'discord' | 'telegram' | 'teams' | 'webhook' | 'push' | 'sms';
  enabled: boolean;
  credentials: Record<string, any>;
  settings: Record<string, any>;
  templates: NotificationTemplate[];
  filters: NotificationFilter[];
  rateLimit: {
    maxPerMinute: number;
    maxPerHour: number;
    maxPerDay: number;
  };
  retryPolicy: {
    maxRetries: number;
    retryDelay: number;
    backoffMultiplier: number;
  };
  created: Date;
  updated: Date;
  lastUsed?: Date;
  usageCount: number;
  errorCount: number;
  status: 'active' | 'inactive' | 'error' | 'testing';
}

export interface NotificationTemplate {
  id: string;
  name: string;
  subject?: string;
  content: string;
  variables: string[];
  format: 'text' | 'html' | 'markdown' | 'json';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  category: string;
  tags: string[];
}

export interface NotificationFilter {
  field: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'greater_than' | 'less_than' | 'in' | 'not_in';
  value: any;
  logicalOperator?: 'AND' | 'OR';
}

export interface NotificationMessage {
  id: string;
  configId: string;
  templateId: string;
  recipient: string;
  subject?: string;
  content: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  status: 'pending' | 'sending' | 'sent' | 'failed' | 'delivered' | 'bounced';
  createdAt: Date;
  sentAt?: Date;
  deliveredAt?: Date;
  retryCount: number;
  maxRetries: number;
  nextRetry?: Date;
  error?: string;
  metadata: Record<string, any>;
}

export interface NotificationQueue {
  id: string;
  configId: string;
  templateId: string;
  recipient: string;
  data: any;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  scheduledFor?: Date;
  createdAt: Date;
  attempts: number;
  maxAttempts: number;
  lastAttempt?: Date;
  nextAttempt?: Date;
  error?: string;
}

export class NotificationService extends EventEmitter {
  private configs: Map<string, NotificationConfig> = new Map();
  private messages: Map<string, NotificationMessage> = new Map();
  private queue: NotificationQueue[] = [];
  private isProcessing: boolean = false;
  private processingInterval: NodeJS.Timeout | null = null;
  private wsClients: Map<string, WebSocket> = new Map();
  private transporters: Map<string, nodemailer.Transporter> = new Map();

  constructor() {
    super();
    this.initializeDefaultConfigs();
    this.startProcessing();
  }

  // Inicializar configuraciones por defecto
  private initializeDefaultConfigs(): void {
    // Configuración de email
    const emailConfig: NotificationConfig = {
      id: 'email_notifications',
      name: 'Email Notifications',
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
        },
        {
          id: 'insights_report',
          name: 'Insights Report',
          subject: 'Weekly Insights Report - {date}',
          content: `
            <h2>Weekly Insights Report</h2>
            <p>Here are the key insights from this week:</p>
            <ul>
              {insights}
            </ul>
            <p><strong>Recommendations:</strong></p>
            <ul>
              {recommendations}
            </ul>
          `,
          variables: ['date', 'insights', 'recommendations'],
          format: 'html',
          priority: 'normal',
          category: 'report',
          tags: ['report', 'insights']
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
      },
      created: new Date(),
      updated: new Date(),
      usageCount: 0,
      errorCount: 0,
      status: 'active'
    };

    // Configuración de Slack
    const slackConfig: NotificationConfig = {
      id: 'slack_notifications',
      name: 'Slack Notifications',
      type: 'slack',
      enabled: true,
      credentials: {
        webhookUrl: process.env.SLACK_WEBHOOK_URL || ''
      },
      settings: {
        channel: '#feedback-alerts',
        username: 'Feedback Bot',
        iconEmoji: ':robot_face:'
      },
      templates: [
        {
          id: 'feedback_alert_slack',
          name: 'Feedback Alert (Slack)',
          content: `
            🚨 *New Feedback Alert*
            *Source:* {source}
            *Sentiment:* {sentiment}
            *Urgency:* {urgency}
            *Region:* {region}
            *Content:* {content}
            *Processed At:* {processedAt}
          `,
          variables: ['source', 'sentiment', 'urgency', 'region', 'content', 'processedAt'],
          format: 'text',
          priority: 'normal',
          category: 'feedback',
          tags: ['alert', 'feedback', 'slack']
        }
      ],
      filters: [
        {
          field: 'urgency',
          operator: 'in',
          value: ['high', 'critical']
        }
      ],
      rateLimit: {
        maxPerMinute: 100,
        maxPerHour: 1000,
        maxPerDay: 10000
      },
      retryPolicy: {
        maxRetries: 3,
        retryDelay: 1000,
        backoffMultiplier: 2
      },
      created: new Date(),
      updated: new Date(),
      usageCount: 0,
      errorCount: 0,
      status: 'active'
    };

    this.configs.set(emailConfig.id, emailConfig);
    this.configs.set(slackConfig.id, slackConfig);
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

  // Procesar cola de notificaciones
  private async processQueue(): Promise<void> {
    if (this.isProcessing || this.queue.length === 0) return;

    this.isProcessing = true;
    const item = this.queue.shift();

    try {
      await this.processNotification(item);
    } catch (error) {
      console.error('Error processing notification:', error);
    } finally {
      this.isProcessing = false;
    }
  }

  // Procesar notificación
  private async processNotification(queueItem: NotificationQueue): Promise<void> {
    const config = this.configs.get(queueItem.configId);
    if (!config || !config.enabled) return;

    const template = config.templates.find(t => t.id === queueItem.templateId);
    if (!template) return;

    const message: NotificationMessage = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      configId: queueItem.configId,
      templateId: queueItem.templateId,
      recipient: queueItem.recipient,
      subject: template.subject,
      content: template.content,
      priority: template.priority,
      status: 'sending',
      createdAt: new Date(),
      retryCount: queueItem.attempts,
      maxRetries: config.retryPolicy.maxRetries,
      metadata: queueItem.data
    };

    this.messages.set(message.id, message);
    this.emit('message_sending', message);

    try {
      // Renderizar contenido
      const renderedContent = this.renderTemplate(template, queueItem.data);
      const renderedSubject = template.subject ? this.renderTemplate({ ...template, content: template.subject }, queueItem.data) : undefined;

      // Enviar notificación
      await this.sendNotification(config, {
        ...message,
        content: renderedContent,
        subject: renderedSubject
      });

      message.status = 'sent';
      message.sentAt = new Date();
      config.usageCount++;
      config.lastUsed = new Date();
      config.status = 'active';

      this.emit('message_sent', message);
    } catch (error) {
      message.status = 'failed';
      message.error = error.message;
      config.errorCount++;
      config.status = 'error';

      // Reintentar si no se ha alcanzado el máximo
      if (queueItem.attempts < queueItem.maxAttempts) {
        queueItem.attempts++;
        queueItem.lastAttempt = new Date();
        queueItem.nextAttempt = new Date(Date.now() + config.retryPolicy.retryDelay * Math.pow(config.retryPolicy.backoffMultiplier, queueItem.attempts - 1));
        queueItem.error = error.message;
        this.queue.push(queueItem);
      }

      this.emit('message_failed', message);
    }
  }

  // Enviar notificación
  private async sendNotification(config: NotificationConfig, message: NotificationMessage): Promise<void> {
    switch (config.type) {
      case 'email':
        await this.sendEmail(config, message);
        break;
      case 'slack':
        await this.sendSlack(config, message);
        break;
      case 'discord':
        await this.sendDiscord(config, message);
        break;
      case 'telegram':
        await this.sendTelegram(config, message);
        break;
      case 'teams':
        await this.sendTeams(config, message);
        break;
      case 'webhook':
        await this.sendWebhook(config, message);
        break;
      case 'push':
        await this.sendPush(config, message);
        break;
      case 'sms':
        await this.sendSMS(config, message);
        break;
      default:
        throw new Error(`Unsupported notification type: ${config.type}`);
    }
  }

  // Enviar email
  private async sendEmail(config: NotificationConfig, message: NotificationMessage): Promise<void> {
    let transporter = this.transporters.get(config.id);
    
    if (!transporter) {
      transporter = nodemailer.createTransporter(config.credentials);
      this.transporters.set(config.id, transporter);
    }

    const mailOptions = {
      from: config.settings.from,
      to: message.recipient,
      subject: message.subject,
      html: message.content
    };

    await transporter.sendMail(mailOptions);
    console.log(`Email sent to ${message.recipient}`);
  }

  // Enviar Slack
  private async sendSlack(config: NotificationConfig, message: NotificationMessage): Promise<void> {
    const payload = {
      channel: config.settings.channel,
      username: config.settings.username,
      icon_emoji: config.settings.iconEmoji,
      text: message.content
    };

    await axios.post(config.credentials.webhookUrl, payload);
    console.log(`Slack message sent to ${config.settings.channel}`);
  }

  // Enviar Discord
  private async sendDiscord(config: NotificationConfig, message: NotificationMessage): Promise<void> {
    const payload = {
      content: message.content
    };

    await axios.post(config.credentials.webhookUrl, payload);
    console.log(`Discord message sent`);
  }

  // Enviar Telegram
  private async sendTelegram(config: NotificationConfig, message: NotificationMessage): Promise<void> {
    const url = `https://api.telegram.org/bot${config.credentials.botToken}/sendMessage`;
    const payload = {
      chat_id: message.recipient,
      text: message.content,
      parse_mode: 'HTML'
    };

    await axios.post(url, payload);
    console.log(`Telegram message sent to ${message.recipient}`);
  }

  // Enviar Teams
  private async sendTeams(config: NotificationConfig, message: NotificationMessage): Promise<void> {
    const payload = {
      "@type": "MessageCard",
      "@context": "http://schema.org/extensions",
      "themeColor": "0076D7",
      "summary": message.subject || "Notification",
      "sections": [{
        "activityTitle": message.subject || "Notification",
        "activitySubtitle": "AI Marketing Feedback System",
        "text": message.content,
        "markdown": true
      }]
    };

    await axios.post(config.credentials.webhookUrl, payload);
    console.log(`Teams message sent`);
  }

  // Enviar webhook
  private async sendWebhook(config: NotificationConfig, message: NotificationMessage): Promise<void> {
    const payload = {
      message: message.content,
      subject: message.subject,
      recipient: message.recipient,
      timestamp: message.createdAt.toISOString()
    };

    await axios.post(config.credentials.webhookUrl, payload);
    console.log(`Webhook sent to ${config.credentials.webhookUrl}`);
  }

  // Enviar push
  private async sendPush(config: NotificationConfig, message: NotificationMessage): Promise<void> {
    // Simular envío de push notification
    console.log(`Push notification sent to ${message.recipient}: ${message.content}`);
  }

  // Enviar SMS
  private async sendSMS(config: NotificationConfig, message: NotificationMessage): Promise<void> {
    // Simular envío de SMS
    console.log(`SMS sent to ${message.recipient}: ${message.content}`);
  }

  // Renderizar plantilla
  private renderTemplate(template: NotificationTemplate, data: any): string {
    let content = template.content;
    
    for (const variable of template.variables) {
      const value = this.getNestedValue(data, variable) || `{${variable}}`;
      const regex = new RegExp(`{${variable}}`, 'g');
      content = content.replace(regex, String(value));
    }
    
    return content;
  }

  // Obtener valor anidado
  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }

  // Enviar notificación
  sendNotification(configId: string, templateId: string, recipient: string, data: any, priority: 'low' | 'normal' | 'high' | 'urgent' = 'normal'): void {
    const config = this.configs.get(configId);
    if (!config || !config.enabled) return;

    const template = config.templates.find(t => t.id === templateId);
    if (!template) return;

    // Verificar filtros
    if (!this.matchesFilters(data, config.filters)) return;

    const queueItem: NotificationQueue = {
      id: `queue_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      configId,
      templateId,
      recipient,
      data,
      priority,
      createdAt: new Date(),
      attempts: 0,
      maxAttempts: config.retryPolicy.maxRetries
    };

    this.queue.push(queueItem);
    this.emit('notification_queued', queueItem);
  }

  // Verificar filtros
  private matchesFilters(data: any, filters: NotificationFilter[]): boolean {
    if (filters.length === 0) return true;

    let result = true;
    let logicalOperator = 'AND';

    for (const filter of filters) {
      const fieldValue = this.getNestedValue(data, filter.field);
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

  // Crear configuración
  createConfig(config: Omit<NotificationConfig, 'id' | 'created' | 'updated' | 'usageCount' | 'errorCount' | 'status'>): string {
    const id = `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newConfig: NotificationConfig = {
      ...config,
      id,
      created: new Date(),
      updated: new Date(),
      usageCount: 0,
      errorCount: 0,
      status: 'active'
    };

    this.configs.set(id, newConfig);
    this.emit('config_created', newConfig);
    return id;
  }

  // Actualizar configuración
  updateConfig(id: string, updates: Partial<NotificationConfig>): boolean {
    const config = this.configs.get(id);
    if (!config) return false;

    const updatedConfig = {
      ...config,
      ...updates,
      id,
      updated: new Date()
    };

    this.configs.set(id, updatedConfig);
    this.emit('config_updated', updatedConfig);
    return true;
  }

  // Eliminar configuración
  deleteConfig(id: string): boolean {
    const config = this.configs.get(id);
    if (!config) return false;

    this.configs.delete(id);
    this.emit('config_deleted', config);
    return true;
  }

  // Obtener configuraciones
  getConfigs(): NotificationConfig[] {
    return Array.from(this.configs.values());
  }

  // Obtener configuración específica
  getConfig(id: string): NotificationConfig | undefined {
    return this.configs.get(id);
  }

  // Obtener mensajes
  getMessages(limit?: number): NotificationMessage[] {
    const messages = Array.from(this.messages.values())
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
    
    return limit ? messages.slice(0, limit) : messages;
  }

  // Obtener estadísticas
  getStats(): {
    totalConfigs: number;
    activeConfigs: number;
    totalMessages: number;
    sentMessages: number;
    failedMessages: number;
    queuedMessages: number;
    averageDeliveryTime: number;
    recentMessages: NotificationMessage[];
  } {
    const configs = Array.from(this.configs.values());
    const messages = Array.from(this.messages.values());
    
    const totalMessages = messages.length;
    const sentMessages = messages.filter(m => m.status === 'sent').length;
    const failedMessages = messages.filter(m => m.status === 'failed').length;
    const queuedMessages = this.queue.length;
    
    const averageDeliveryTime = messages.length > 0 
      ? messages.reduce((sum, m) => sum + (m.sentAt ? m.sentAt.getTime() - m.createdAt.getTime() : 0), 0) / messages.length
      : 0;
    
    return {
      totalConfigs: configs.length,
      activeConfigs: configs.filter(c => c.enabled).length,
      totalMessages,
      sentMessages,
      failedMessages,
      queuedMessages,
      averageDeliveryTime,
      recentMessages: messages.slice(0, 10)
    };
  }

  // Probar configuración
  async testConfig(id: string, testData?: any): Promise<boolean> {
    const config = this.configs.get(id);
    if (!config) return false;

    try {
      const testTemplate = config.templates[0];
      if (!testTemplate) return false;

      const testData = testData || {
        source: 'test',
        sentiment: 'positive',
        urgency: 'low',
        region: 'MX',
        content: 'This is a test notification',
        processedAt: new Date().toISOString()
      };

      this.sendNotification(id, testTemplate.id, 'test@example.com', testData);
      return true;
    } catch (error) {
      console.error(`Error testing config ${id}:`, error);
      return false;
    }
  }
}

export const notificationService = new NotificationService();






