import { EventEmitter } from 'events';
import { CustomerFeedback } from './customerFeedbackService';
import { AdvancedAnalytics } from './advancedAnalyticsService';
import { aiInsightsService } from './aiInsightsService';
import { realTimeNotificationService } from './realTimeNotificationService';

export interface AutomationRule {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  priority: number;
  conditions: AutomationCondition[];
  actions: AutomationAction[];
  triggers: AutomationTrigger[];
  created: Date;
  updated: Date;
  lastExecuted?: Date;
  executionCount: number;
  successCount: number;
  failureCount: number;
}

export interface AutomationCondition {
  id: string;
  field: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'greater_than' | 'less_than' | 'in' | 'not_in';
  value: any;
  logicalOperator?: 'AND' | 'OR';
}

export interface AutomationAction {
  id: string;
  type: 'notification' | 'email' | 'slack' | 'discord' | 'telegram' | 'webhook' | 'tag' | 'assign' | 'escalate' | 'create_task' | 'update_status';
  parameters: Record<string, any>;
  delay?: number; // seconds
  retryCount?: number;
  retryDelay?: number;
}

export interface AutomationTrigger {
  id: string;
  type: 'feedback_created' | 'feedback_updated' | 'sentiment_changed' | 'urgency_changed' | 'anomaly_detected' | 'threshold_exceeded' | 'schedule' | 'webhook';
  parameters: Record<string, any>;
}

export interface AutomationExecution {
  id: string;
  ruleId: string;
  ruleName: string;
  triggerType: string;
  triggerData: any;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  startedAt: Date;
  completedAt?: Date;
  duration?: number;
  actionsExecuted: number;
  actionsSuccessful: number;
  actionsFailed: number;
  error?: string;
  result?: any;
}

export interface AutomationStats {
  totalRules: number;
  activeRules: number;
  totalExecutions: number;
  successfulExecutions: number;
  failedExecutions: number;
  averageExecutionTime: number;
  mostExecutedRule: string;
  recentExecutions: AutomationExecution[];
}

export class AutomationService extends EventEmitter {
  private rules: Map<string, AutomationRule> = new Map();
  private executions: Map<string, AutomationExecution> = new Map();
  private isProcessing: boolean = false;
  private processingQueue: any[] = [];
  private processingInterval: NodeJS.Timeout | null = null;

  constructor() {
    super();
    this.initializeDefaultRules();
    this.startProcessing();
  }

  // Inicializar reglas por defecto
  private initializeDefaultRules(): void {
    // Regla para feedback crítico
    const criticalFeedbackRule: AutomationRule = {
      id: 'critical_feedback_rule',
      name: 'Critical Feedback Alert',
      description: 'Automatically alert team when critical feedback is received',
      enabled: true,
      priority: 1,
      conditions: [
        {
          id: 'urgency_critical',
          field: 'urgency',
          operator: 'equals',
          value: 'critical'
        }
      ],
      actions: [
        {
          id: 'slack_alert',
          type: 'slack',
          parameters: {
            channel: '#critical-alerts',
            message: '🚨 CRITICAL FEEDBACK ALERT: {content}',
            color: 'danger'
          }
        },
        {
          id: 'email_alert',
          type: 'email',
          parameters: {
            to: 'alerts@company.com',
            subject: 'Critical Feedback Alert - {id}',
            template: 'critical_feedback_alert'
          }
        }
      ],
      triggers: [
        {
          id: 'feedback_created',
          type: 'feedback_created',
          parameters: {}
        }
      ],
      created: new Date(),
      updated: new Date(),
      executionCount: 0,
      successCount: 0,
      failureCount: 0
    };

    // Regla para sentimiento negativo
    const negativeSentimentRule: AutomationRule = {
      id: 'negative_sentiment_rule',
      name: 'Negative Sentiment Response',
      description: 'Automatically respond to negative sentiment feedback',
      enabled: true,
      priority: 2,
      conditions: [
        {
          id: 'sentiment_negative',
          field: 'sentiment',
          operator: 'equals',
          value: 'negative'
        },
        {
          id: 'urgency_high',
          field: 'urgency',
          operator: 'in',
          value: ['high', 'critical'],
          logicalOperator: 'AND'
        }
      ],
      actions: [
        {
          id: 'create_task',
          type: 'create_task',
          parameters: {
            title: 'Follow up on negative feedback - {id}',
            description: 'Customer feedback requires immediate attention: {content}',
            priority: 'high',
            assignee: 'customer_success_team'
          }
        },
        {
          id: 'tag_feedback',
          type: 'tag',
          parameters: {
            tags: ['negative', 'follow_up_required']
          }
        }
      ],
      triggers: [
        {
          id: 'feedback_created',
          type: 'feedback_created',
          parameters: {}
        }
      ],
      created: new Date(),
      updated: new Date(),
      executionCount: 0,
      successCount: 0,
      failureCount: 0
    };

    // Regla para sentimiento positivo
    const positiveSentimentRule: AutomationRule = {
      id: 'positive_sentiment_rule',
      name: 'Positive Sentiment Follow-up',
      description: 'Automatically follow up on positive sentiment feedback',
      enabled: true,
      priority: 3,
      conditions: [
        {
          id: 'sentiment_positive',
          field: 'sentiment',
          operator: 'equals',
          value: 'positive'
        }
      ],
      actions: [
        {
          id: 'tag_feedback',
          type: 'tag',
          parameters: {
            tags: ['positive', 'potential_advocate']
          }
        },
        {
          id: 'create_task',
          type: 'create_task',
          parameters: {
            title: 'Request testimonial from satisfied customer - {id}',
            description: 'Customer expressed positive sentiment: {content}',
            priority: 'medium',
            assignee: 'marketing_team'
          }
        }
      ],
      triggers: [
        {
          id: 'feedback_created',
          type: 'feedback_created',
          parameters: {}
        }
      ],
      created: new Date(),
      updated: new Date(),
      executionCount: 0,
      successCount: 0,
      failureCount: 0
    };

    // Regla para detección de anomalías
    const anomalyDetectionRule: AutomationRule = {
      id: 'anomaly_detection_rule',
      name: 'Anomaly Detection Alert',
      description: 'Alert when anomalies are detected in feedback patterns',
      enabled: true,
      priority: 1,
      conditions: [
        {
          id: 'anomaly_detected',
          field: 'anomaly_score',
          operator: 'greater_than',
          value: 0.8
        }
      ],
      actions: [
        {
          id: 'slack_alert',
          type: 'slack',
          parameters: {
            channel: '#anomaly-alerts',
            message: '⚠️ ANOMALY DETECTED: {description}',
            color: 'warning'
          }
        },
        {
          id: 'create_task',
          type: 'create_task',
          parameters: {
            title: 'Investigate anomaly - {anomaly_type}',
            description: 'Anomaly detected: {description}',
            priority: 'high',
            assignee: 'data_team'
          }
        }
      ],
      triggers: [
        {
          id: 'anomaly_detected',
          type: 'anomaly_detected',
          parameters: {}
        }
      ],
      created: new Date(),
      updated: new Date(),
      executionCount: 0,
      successCount: 0,
      failureCount: 0
    };

    this.rules.set(criticalFeedbackRule.id, criticalFeedbackRule);
    this.rules.set(negativeSentimentRule.id, negativeSentimentRule);
    this.rules.set(positiveSentimentRule.id, positiveSentimentRule);
    this.rules.set(anomalyDetectionRule.id, anomalyDetectionRule);
  }

  // Iniciar procesamiento
  private startProcessing(): void {
    this.processingInterval = setInterval(() => {
      this.processQueue();
    }, 1000); // Cada segundo
  }

  // Detener procesamiento
  stopProcessing(): void {
    if (this.processingInterval) {
      clearInterval(this.processingInterval);
      this.processingInterval = null;
    }
  }

  // Procesar cola de ejecuciones
  private async processQueue(): Promise<void> {
    if (this.isProcessing || this.processingQueue.length === 0) return;

    this.isProcessing = true;
    const item = this.processingQueue.shift();

    try {
      await this.executeAutomation(item);
    } catch (error) {
      console.error('Error processing automation:', error);
    } finally {
      this.isProcessing = false;
    }
  }

  // Ejecutar automatización
  private async executeAutomation(item: any): Promise<void> {
    const { ruleId, triggerType, triggerData } = item;
    const rule = this.rules.get(ruleId);

    if (!rule || !rule.enabled) return;

    const execution: AutomationExecution = {
      id: `exec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      ruleId,
      ruleName: rule.name,
      triggerType,
      triggerData,
      status: 'running',
      startedAt: new Date(),
      actionsExecuted: 0,
      actionsSuccessful: 0,
      actionsFailed: 0
    };

    this.executions.set(execution.id, execution);
    this.emit('execution_started', execution);

    try {
      // Verificar condiciones
      const conditionsMet = await this.checkConditions(rule.conditions, triggerData);
      
      if (!conditionsMet) {
        execution.status = 'completed';
        execution.completedAt = new Date();
        execution.duration = execution.completedAt.getTime() - execution.startedAt.getTime();
        this.emit('execution_completed', execution);
        return;
      }

      // Ejecutar acciones
      for (const action of rule.actions) {
        try {
          await this.executeAction(action, triggerData);
          execution.actionsExecuted++;
          execution.actionsSuccessful++;
        } catch (error) {
          console.error(`Error executing action ${action.id}:`, error);
          execution.actionsExecuted++;
          execution.actionsFailed++;
        }
      }

      execution.status = 'completed';
      execution.completedAt = new Date();
      execution.duration = execution.completedAt.getTime() - execution.startedAt.getTime();
      
      // Actualizar estadísticas de la regla
      rule.executionCount++;
      rule.successCount++;
      rule.lastExecuted = new Date();

      this.emit('execution_completed', execution);
    } catch (error) {
      execution.status = 'failed';
      execution.error = error.message;
      execution.completedAt = new Date();
      execution.duration = execution.completedAt.getTime() - execution.startedAt.getTime();
      
      // Actualizar estadísticas de la regla
      rule.executionCount++;
      rule.failureCount++;

      this.emit('execution_failed', execution);
    }
  }

  // Verificar condiciones
  private async checkConditions(conditions: AutomationCondition[], data: any): Promise<boolean> {
    if (conditions.length === 0) return true;

    let result = true;
    let logicalOperator = 'AND';

    for (const condition of conditions) {
      const conditionResult = await this.evaluateCondition(condition, data);
      
      if (logicalOperator === 'AND') {
        result = result && conditionResult;
      } else if (logicalOperator === 'OR') {
        result = result || conditionResult;
      }
      
      logicalOperator = condition.logicalOperator || 'AND';
    }

    return result;
  }

  // Evaluar condición individual
  private async evaluateCondition(condition: AutomationCondition, data: any): Promise<boolean> {
    const fieldValue = this.getFieldValue(data, condition.field);
    const conditionValue = condition.value;

    switch (condition.operator) {
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
  private getFieldValue(data: any, field: string): any {
    const fields = field.split('.');
    let value = data;
    
    for (const f of fields) {
      if (value && typeof value === 'object' && f in value) {
        value = value[f];
      } else {
        return undefined;
      }
    }
    
    return value;
  }

  // Ejecutar acción
  private async executeAction(action: AutomationAction, data: any): Promise<void> {
    // Aplicar delay si está configurado
    if (action.delay) {
      await new Promise(resolve => setTimeout(resolve, action.delay * 1000));
    }

    const parameters = this.interpolateParameters(action.parameters, data);

    switch (action.type) {
      case 'notification':
        await this.sendNotification(parameters);
        break;
      case 'email':
        await this.sendEmail(parameters);
        break;
      case 'slack':
        await this.sendSlackMessage(parameters);
        break;
      case 'discord':
        await this.sendDiscordMessage(parameters);
        break;
      case 'telegram':
        await this.sendTelegramMessage(parameters);
        break;
      case 'webhook':
        await this.sendWebhook(parameters);
        break;
      case 'tag':
        await this.addTags(parameters, data);
        break;
      case 'assign':
        await this.assignFeedback(parameters, data);
        break;
      case 'escalate':
        await this.escalateFeedback(parameters, data);
        break;
      case 'create_task':
        await this.createTask(parameters);
        break;
      case 'update_status':
        await this.updateStatus(parameters, data);
        break;
      default:
        throw new Error(`Unknown action type: ${action.type}`);
    }
  }

  // Interpolar parámetros
  private interpolateParameters(parameters: Record<string, any>, data: any): Record<string, any> {
    const interpolated: Record<string, any> = {};
    
    for (const [key, value] of Object.entries(parameters)) {
      if (typeof value === 'string') {
        interpolated[key] = value.replace(/\{(\w+(?:\.\w+)*)\}/g, (match, field) => {
          const fieldValue = this.getFieldValue(data, field);
          return fieldValue !== undefined ? String(fieldValue) : match;
        });
      } else {
        interpolated[key] = value;
      }
    }
    
    return interpolated;
  }

  // Métodos de acción
  private async sendNotification(parameters: any): Promise<void> {
    console.log('Sending notification:', parameters);
    // Implementar envío de notificación
  }

  private async sendEmail(parameters: any): Promise<void> {
    console.log('Sending email:', parameters);
    // Implementar envío de email
  }

  private async sendSlackMessage(parameters: any): Promise<void> {
    console.log('Sending Slack message:', parameters);
    // Implementar envío de mensaje a Slack
  }

  private async sendDiscordMessage(parameters: any): Promise<void> {
    console.log('Sending Discord message:', parameters);
    // Implementar envío de mensaje a Discord
  }

  private async sendTelegramMessage(parameters: any): Promise<void> {
    console.log('Sending Telegram message:', parameters);
    // Implementar envío de mensaje a Telegram
  }

  private async sendWebhook(parameters: any): Promise<void> {
    console.log('Sending webhook:', parameters);
    // Implementar envío de webhook
  }

  private async addTags(parameters: any, data: any): Promise<void> {
    console.log('Adding tags:', parameters, 'to data:', data);
    // Implementar adición de tags
  }

  private async assignFeedback(parameters: any, data: any): Promise<void> {
    console.log('Assigning feedback:', parameters, 'to data:', data);
    // Implementar asignación de feedback
  }

  private async escalateFeedback(parameters: any, data: any): Promise<void> {
    console.log('Escalating feedback:', parameters, 'for data:', data);
    // Implementar escalación de feedback
  }

  private async createTask(parameters: any): Promise<void> {
    console.log('Creating task:', parameters);
    // Implementar creación de tarea
  }

  private async updateStatus(parameters: any, data: any): Promise<void> {
    console.log('Updating status:', parameters, 'for data:', data);
    // Implementar actualización de estado
  }

  // Procesar feedback
  processFeedback(feedback: CustomerFeedback): void {
    this.processingQueue.push({
      ruleId: 'feedback_created',
      triggerType: 'feedback_created',
      triggerData: feedback
    });
  }

  // Procesar anomalía
  processAnomaly(anomaly: any): void {
    this.processingQueue.push({
      ruleId: 'anomaly_detection_rule',
      triggerType: 'anomaly_detected',
      triggerData: anomaly
    });
  }

  // Crear regla
  createRule(rule: Omit<AutomationRule, 'id' | 'created' | 'updated' | 'executionCount' | 'successCount' | 'failureCount'>): string {
    const id = `rule_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newRule: AutomationRule = {
      ...rule,
      id,
      created: new Date(),
      updated: new Date(),
      executionCount: 0,
      successCount: 0,
      failureCount: 0
    };

    this.rules.set(id, newRule);
    this.emit('rule_created', newRule);
    return id;
  }

  // Actualizar regla
  updateRule(id: string, updates: Partial<AutomationRule>): boolean {
    const rule = this.rules.get(id);
    if (!rule) return false;

    const updatedRule = {
      ...rule,
      ...updates,
      id,
      updated: new Date()
    };

    this.rules.set(id, updatedRule);
    this.emit('rule_updated', updatedRule);
    return true;
  }

  // Eliminar regla
  deleteRule(id: string): boolean {
    const rule = this.rules.get(id);
    if (!rule) return false;

    this.rules.delete(id);
    this.emit('rule_deleted', rule);
    return true;
  }

  // Obtener reglas
  getRules(): AutomationRule[] {
    return Array.from(this.rules.values());
  }

  // Obtener regla específica
  getRule(id: string): AutomationRule | undefined {
    return this.rules.get(id);
  }

  // Obtener ejecuciones
  getExecutions(limit?: number): AutomationExecution[] {
    const executions = Array.from(this.executions.values())
      .sort((a, b) => b.startedAt.getTime() - a.startedAt.getTime());
    
    return limit ? executions.slice(0, limit) : executions;
  }

  // Obtener estadísticas
  getStats(): AutomationStats {
    const rules = Array.from(this.rules.values());
    const executions = Array.from(this.executions.values());
    
    const totalExecutions = executions.length;
    const successfulExecutions = executions.filter(e => e.status === 'completed').length;
    const failedExecutions = executions.filter(e => e.status === 'failed').length;
    
    const averageExecutionTime = executions.length > 0 
      ? executions.reduce((sum, e) => sum + (e.duration || 0), 0) / executions.length
      : 0;
    
    const mostExecutedRule = rules.length > 0
      ? rules.reduce((max, rule) => rule.executionCount > max.executionCount ? rule : max).name
      : 'None';
    
    return {
      totalRules: rules.length,
      activeRules: rules.filter(r => r.enabled).length,
      totalExecutions,
      successfulExecutions,
      failedExecutions,
      averageExecutionTime,
      mostExecutedRule,
      recentExecutions: executions.slice(0, 10)
    };
  }
}

export const automationService = new AutomationService();






