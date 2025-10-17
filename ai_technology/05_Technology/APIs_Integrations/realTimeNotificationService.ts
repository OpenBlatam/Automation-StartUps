import { WebSocket } from 'ws';
import { customerFeedbackService, CustomerFeedback } from './customerFeedbackService';
import { advancedFeedbackProcessor, RealTimeAlert } from './advancedFeedbackProcessor';

export interface NotificationChannel {
  id: string;
  type: 'email' | 'slack' | 'discord' | 'telegram' | 'webhook' | 'websocket';
  config: {
    url?: string;
    token?: string;
    channel?: string;
    webhook?: string;
    email?: string;
  };
  enabled: boolean;
  filters: {
    regions?: string[];
    sources?: string[];
    severities?: string[];
    types?: string[];
  };
}

export interface NotificationTemplate {
  id: string;
  name: string;
  type: 'alert' | 'summary' | 'report' | 'custom';
  subject: string;
  body: string;
  variables: string[];
  channels: string[];
}

export interface Notification {
  id: string;
  channelId: string;
  templateId: string;
  data: any;
  status: 'pending' | 'sent' | 'failed' | 'delivered';
  timestamp: Date;
  retryCount: number;
  error?: string;
}

export class RealTimeNotificationService {
  private channels: Map<string, NotificationChannel> = new Map();
  private templates: Map<string, NotificationTemplate> = new Map();
  private notifications: Map<string, Notification> = new Map();
  private wsConnections: Map<string, WebSocket> = new Map();
  private alertSubscribers: Set<string> = new Set();

  // Configurar canal de notificación
  async configureChannel(channelData: Partial<NotificationChannel>): Promise<NotificationChannel> {
    const channel: NotificationChannel = {
      id: `channel_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: channelData.type || 'email',
      config: channelData.config || {},
      enabled: channelData.enabled !== false,
      filters: channelData.filters || {},
      ...channelData
    };

    this.channels.set(channel.id, channel);
    return channel;
  }

  // Crear plantilla de notificación
  async createTemplate(templateData: Partial<NotificationTemplate>): Promise<NotificationTemplate> {
    const template: NotificationTemplate = {
      id: `template_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: templateData.name || 'Default Template',
      type: templateData.type || 'alert',
      subject: templateData.subject || 'Notification',
      body: templateData.body || 'You have a new notification',
      variables: templateData.variables || [],
      channels: templateData.channels || [],
      ...templateData
    };

    this.templates.set(template.id, template);
    return template;
  }

  // Enviar notificación
  async sendNotification(channelId: string, templateId: string, data: any): Promise<Notification> {
    const channel = this.channels.get(channelId);
    const template = this.templates.get(templateId);

    if (!channel || !template) {
      throw new Error('Channel or template not found');
    }

    const notification: Notification = {
      id: `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      channelId,
      templateId,
      data,
      status: 'pending',
      timestamp: new Date(),
      retryCount: 0
    };

    this.notifications.set(notification.id, notification);

    try {
      await this.deliverNotification(notification, channel, template);
      notification.status = 'sent';
    } catch (error) {
      notification.status = 'failed';
      notification.error = error instanceof Error ? error.message : 'Unknown error';
    }

    this.notifications.set(notification.id, notification);
    return notification;
  }

  // Entregar notificación
  private async deliverNotification(
    notification: Notification,
    channel: NotificationChannel,
    template: NotificationTemplate
  ): Promise<void> {
    const content = this.renderTemplate(template, notification.data);

    switch (channel.type) {
      case 'email':
        await this.sendEmail(channel, content);
        break;
      case 'slack':
        await this.sendSlack(channel, content);
        break;
      case 'discord':
        await this.sendDiscord(channel, content);
        break;
      case 'telegram':
        await this.sendTelegram(channel, content);
        break;
      case 'webhook':
        await this.sendWebhook(channel, content);
        break;
      case 'websocket':
        await this.sendWebSocket(channel, content);
        break;
      default:
        throw new Error(`Unsupported channel type: ${channel.type}`);
    }
  }

  // Renderizar plantilla
  private renderTemplate(template: NotificationTemplate, data: any): { subject: string; body: string } {
    let subject = template.subject;
    let body = template.body;

    // Reemplazar variables en la plantilla
    template.variables.forEach(variable => {
      const value = this.getNestedValue(data, variable) || `{{${variable}}}`;
      const regex = new RegExp(`{{${variable}}}`, 'g');
      subject = subject.replace(regex, value);
      body = body.replace(regex, value);
    });

    return { subject, body };
  }

  // Obtener valor anidado de objeto
  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }

  // Enviar email
  private async sendEmail(channel: NotificationChannel, content: { subject: string; body: string }): Promise<void> {
    // Simulación de envío de email
    console.log(`Sending email to ${channel.config.email}:`);
    console.log(`Subject: ${content.subject}`);
    console.log(`Body: ${content.body}`);
    
    // En implementación real, usar nodemailer o servicio de email
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  // Enviar Slack
  private async sendSlack(channel: NotificationChannel, content: { subject: string; body: string }): Promise<void> {
    // Simulación de envío a Slack
    console.log(`Sending Slack message to ${channel.config.channel}:`);
    console.log(`Title: ${content.subject}`);
    console.log(`Message: ${content.body}`);
    
    // En implementación real, usar Slack Web API
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  // Enviar Discord
  private async sendDiscord(channel: NotificationChannel, content: { subject: string; body: string }): Promise<void> {
    // Simulación de envío a Discord
    console.log(`Sending Discord message to ${channel.config.channel}:`);
    console.log(`Title: ${content.subject}`);
    console.log(`Message: ${content.body}`);
    
    // En implementación real, usar Discord Webhook API
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  // Enviar Telegram
  private async sendTelegram(channel: NotificationChannel, content: { subject: string; body: string }): Promise<void> {
    // Simulación de envío a Telegram
    console.log(`Sending Telegram message to ${channel.config.channel}:`);
    console.log(`Title: ${content.subject}`);
    console.log(`Message: ${content.body}`);
    
    // En implementación real, usar Telegram Bot API
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  // Enviar Webhook
  private async sendWebhook(channel: NotificationChannel, content: { subject: string; body: string }): Promise<void> {
    // Simulación de envío de webhook
    console.log(`Sending webhook to ${channel.config.webhook}:`);
    console.log(`Payload:`, { subject: content.subject, body: content.body });
    
    // En implementación real, usar axios para hacer POST request
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  // Enviar WebSocket
  private async sendWebSocket(channel: NotificationChannel, content: { subject: string; body: string }): Promise<void> {
    const message = {
      type: 'notification',
      data: {
        subject: content.subject,
        body: content.body,
        timestamp: new Date()
      }
    };

    // Enviar a todas las conexiones WebSocket activas
    this.wsConnections.forEach(ws => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(message));
      }
    });
  }

  // Procesar alertas en tiempo real
  async processRealTimeAlerts(feedback: CustomerFeedback): Promise<void> {
    const alerts = await advancedFeedbackProcessor.generateRealTimeAlerts(feedback);
    
    for (const alert of alerts) {
      await this.sendAlertNotifications(alert);
    }
  }

  // Enviar notificaciones de alerta
  private async sendAlertNotifications(alert: RealTimeAlert): Promise<void> {
    const channels = Array.from(this.channels.values()).filter(channel => 
      channel.enabled && this.shouldSendAlert(channel, alert)
    );

    const template = this.getAlertTemplate(alert.type);
    if (!template) return;

    for (const channel of channels) {
      try {
        await this.sendNotification(channel.id, template.id, {
          alert,
          timestamp: new Date(),
          severity: alert.severity,
          title: alert.title,
          description: alert.description,
          recommendations: alert.recommendations
        });
      } catch (error) {
        console.error(`Error sending alert notification to ${channel.type}:`, error);
      }
    }
  }

  // Verificar si debe enviar alerta
  private shouldSendAlert(channel: NotificationChannel, alert: RealTimeAlert): boolean {
    const filters = channel.filters;
    
    if (filters.regions && !filters.regions.includes(alert.affectedRegions[0])) {
      return false;
    }
    
    if (filters.sources && !filters.sources.includes(alert.affectedSources[0])) {
      return false;
    }
    
    if (filters.severities && !filters.severities.includes(alert.severity)) {
      return false;
    }
    
    if (filters.types && !filters.types.includes(alert.type)) {
      return false;
    }
    
    return true;
  }

  // Obtener plantilla de alerta
  private getAlertTemplate(alertType: string): NotificationTemplate | null {
    const templates = Array.from(this.templates.values());
    return templates.find(t => t.type === 'alert') || null;
  }

  // Suscribirse a alertas
  subscribeToAlerts(connectionId: string): void {
    this.alertSubscribers.add(connectionId);
  }

  // Desuscribirse de alertas
  unsubscribeFromAlerts(connectionId: string): void {
    this.alertSubscribers.delete(connectionId);
  }

  // Agregar conexión WebSocket
  addWebSocketConnection(connectionId: string, ws: WebSocket): void {
    this.wsConnections.set(connectionId, ws);
  }

  // Remover conexión WebSocket
  removeWebSocketConnection(connectionId: string): void {
    this.wsConnections.delete(connectionId);
  }

  // Enviar resumen diario
  async sendDailySummary(): Promise<void> {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    
    const feedback = await customerFeedbackService.getFeedbackByCriteria({
      dateFrom: yesterday,
      dateTo: new Date()
    });

    const summary = this.generateDailySummary(feedback);
    
    const channels = Array.from(this.channels.values()).filter(channel => 
      channel.enabled && channel.type === 'email'
    );

    const template = this.getSummaryTemplate();
    if (!template) return;

    for (const channel of channels) {
      try {
        await this.sendNotification(channel.id, template.id, summary);
      } catch (error) {
        console.error(`Error sending daily summary to ${channel.type}:`, error);
      }
    }
  }

  // Generar resumen diario
  private generateDailySummary(feedback: CustomerFeedback[]): any {
    const totalFeedback = feedback.length;
    const positiveFeedback = feedback.filter(f => f.sentiment === 'positive').length;
    const negativeFeedback = feedback.filter(f => f.sentiment === 'negative').length;
    const neutralFeedback = feedback.filter(f => f.sentiment === 'neutral').length;
    
    const regionStats = feedback.reduce((acc, f) => {
      acc[f.region] = (acc[f.region] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const sourceStats = feedback.reduce((acc, f) => {
      acc[f.source] = (acc[f.source] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      date: new Date().toISOString().split('T')[0],
      totalFeedback,
      positiveFeedback,
      negativeFeedback,
      neutralFeedback,
      regionStats,
      sourceStats,
      averageSentiment: feedback.reduce((sum, f) => sum + f.sentimentScore, 0) / totalFeedback
    };
  }

  // Obtener plantilla de resumen
  private getSummaryTemplate(): NotificationTemplate | null {
    const templates = Array.from(this.templates.values());
    return templates.find(t => t.type === 'summary') || null;
  }

  // Enviar reporte semanal
  async sendWeeklyReport(): Promise<void> {
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    
    const feedback = await customerFeedbackService.getFeedbackByCriteria({
      dateFrom: weekAgo,
      dateTo: new Date()
    });

    const report = this.generateWeeklyReport(feedback);
    
    const channels = Array.from(this.channels.values()).filter(channel => 
      channel.enabled && channel.type === 'email'
    );

    const template = this.getReportTemplate();
    if (!template) return;

    for (const channel of channels) {
      try {
        await this.sendNotification(channel.id, template.id, report);
      } catch (error) {
        console.error(`Error sending weekly report to ${channel.type}:`, error);
      }
    }
  }

  // Generar reporte semanal
  private generateWeeklyReport(feedback: CustomerFeedback[]): any {
    const totalFeedback = feedback.length;
    const sentimentTrend = this.calculateSentimentTrend(feedback);
    const topThemes = this.calculateTopThemes(feedback);
    const regionalInsights = this.calculateRegionalInsights(feedback);
    
    return {
      period: 'weekly',
      startDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      endDate: new Date().toISOString().split('T')[0],
      totalFeedback,
      sentimentTrend,
      topThemes,
      regionalInsights,
      recommendations: this.generateRecommendations(feedback)
    };
  }

  // Calcular tendencia de sentimiento
  private calculateSentimentTrend(feedback: CustomerFeedback[]): any {
    const midPoint = Math.floor(feedback.length / 2);
    const firstHalf = feedback.slice(0, midPoint);
    const secondHalf = feedback.slice(midPoint);
    
    const firstHalfAvg = firstHalf.reduce((sum, f) => sum + f.sentimentScore, 0) / firstHalf.length;
    const secondHalfAvg = secondHalf.reduce((sum, f) => sum + f.sentimentScore, 0) / secondHalf.length;
    
    return {
      change: secondHalfAvg - firstHalfAvg,
      trend: secondHalfAvg > firstHalfAvg ? 'improving' : 'declining'
    };
  }

  // Calcular temas principales
  private calculateTopThemes(feedback: CustomerFeedback[]): any[] {
    const themeCount: Record<string, number> = {};
    
    feedback.forEach(f => {
      f.keyThemes?.forEach(theme => {
        themeCount[theme] = (themeCount[theme] || 0) + 1;
      });
    });
    
    return Object.entries(themeCount)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([theme, count]) => ({ theme, count }));
  }

  // Calcular insights regionales
  private calculateRegionalInsights(feedback: CustomerFeedback[]): any[] {
    const regionGroups: Record<string, CustomerFeedback[]> = {};
    
    feedback.forEach(f => {
      if (!regionGroups[f.region]) {
        regionGroups[f.region] = [];
      }
      regionGroups[f.region].push(f);
    });
    
    return Object.entries(regionGroups).map(([region, regionFeedback]) => ({
      region,
      totalFeedback: regionFeedback.length,
      averageSentiment: regionFeedback.reduce((sum, f) => sum + f.sentimentScore, 0) / regionFeedback.length,
      topThemes: this.calculateTopThemes(regionFeedback)
    }));
  }

  // Generar recomendaciones
  private generateRecommendations(feedback: CustomerFeedback[]): string[] {
    const recommendations = [];
    
    const negativeFeedback = feedback.filter(f => f.sentiment === 'negative');
    if (negativeFeedback.length > feedback.length * 0.3) {
      recommendations.push('Implementar programa de mejora de satisfacción del cliente');
    }
    
    const criticalFeedback = feedback.filter(f => f.metadata.urgency === 'critical');
    if (criticalFeedback.length > 0) {
      recommendations.push('Revisar procesos de atención al cliente crítico');
    }
    
    recommendations.push('Continuar monitoreo de tendencias de feedback');
    recommendations.push('Optimizar canales de comunicación con clientes');
    
    return recommendations;
  }

  // Obtener plantilla de reporte
  private getReportTemplate(): NotificationTemplate | null {
    const templates = Array.from(this.templates.values());
    return templates.find(t => t.type === 'report') || null;
  }

  // Obtener canales
  getChannels(): NotificationChannel[] {
    return Array.from(this.channels.values());
  }

  // Obtener plantillas
  getTemplates(): NotificationTemplate[] {
    return Array.from(this.templates.values());
  }

  // Obtener notificaciones
  getNotifications(): Notification[] {
    return Array.from(this.notifications.values());
  }

  // Obtener estadísticas de notificaciones
  getNotificationStats(): any {
    const notifications = Array.from(this.notifications.values());
    const total = notifications.length;
    const sent = notifications.filter(n => n.status === 'sent').length;
    const failed = notifications.filter(n => n.status === 'failed').length;
    const pending = notifications.filter(n => n.status === 'pending').length;
    
    return {
      total,
      sent,
      failed,
      pending,
      successRate: total > 0 ? (sent / total) * 100 : 0
    };
  }
}

export const realTimeNotificationService = new RealTimeNotificationService();
