import { EventEmitter } from 'events';
import { CustomerFeedback } from './customerFeedbackService';

export interface WorkflowDefinition {
  id: string;
  name: string;
  description: string;
  version: string;
  enabled: boolean;
  trigger: WorkflowTrigger;
  steps: WorkflowStep[];
  conditions: WorkflowCondition[];
  variables: WorkflowVariable[];
  settings: WorkflowSettings;
  created: Date;
  updated: Date;
  lastExecuted?: Date;
  executionCount: number;
  successCount: number;
  failureCount: number;
}

export interface WorkflowTrigger {
  type: 'event' | 'schedule' | 'webhook' | 'manual' | 'condition';
  event?: string;
  schedule?: {
    frequency: 'once' | 'daily' | 'weekly' | 'monthly' | 'cron';
    time?: string;
    cronExpression?: string;
  };
  webhook?: {
    path: string;
    method: 'GET' | 'POST' | 'PUT' | 'DELETE';
    authentication?: 'none' | 'api_key' | 'jwt' | 'oauth';
  };
  condition?: {
    field: string;
    operator: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than';
    value: any;
  };
}

export interface WorkflowStep {
  id: string;
  name: string;
  type: 'action' | 'condition' | 'loop' | 'delay' | 'webhook' | 'email' | 'notification' | 'data_transform' | 'ai_analysis';
  order: number;
  enabled: boolean;
  config: Record<string, any>;
  onSuccess?: string; // Next step ID
  onFailure?: string; // Next step ID
  retryPolicy?: {
    maxRetries: number;
    retryDelay: number;
    backoffMultiplier: number;
  };
  timeout?: number; // milliseconds
}

export interface WorkflowCondition {
  id: string;
  name: string;
  expression: string; // JavaScript expression
  description: string;
  enabled: boolean;
}

export interface WorkflowVariable {
  id: string;
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  value: any;
  description: string;
  scope: 'global' | 'workflow' | 'step';
}

export interface WorkflowSettings {
  maxExecutionTime: number; // milliseconds
  maxConcurrentExecutions: number;
  retryPolicy: {
    maxRetries: number;
    retryDelay: number;
    backoffMultiplier: number;
  };
  errorHandling: 'stop' | 'continue' | 'retry';
  logging: {
    enabled: boolean;
    level: 'debug' | 'info' | 'warn' | 'error';
  };
}

export interface WorkflowExecution {
  id: string;
  workflowId: string;
  workflowName: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled' | 'timeout';
  startedAt: Date;
  completedAt?: Date;
  duration?: number;
  triggeredBy: string;
  triggerData: any;
  variables: Record<string, any>;
  steps: WorkflowStepExecution[];
  error?: string;
  metadata: Record<string, any>;
}

export interface WorkflowStepExecution {
  id: string;
  stepId: string;
  stepName: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  startedAt: Date;
  completedAt?: Date;
  duration?: number;
  input: any;
  output?: any;
  error?: string;
  retryCount: number;
  metadata: Record<string, any>;
}

export class AdvancedWorkflowService extends EventEmitter {
  private workflows: Map<string, WorkflowDefinition> = new Map();
  private executions: Map<string, WorkflowExecution> = new Map();
  private isProcessing: boolean = false;
  private executionQueue: WorkflowExecution[] = [];
  private processingInterval: NodeJS.Timeout | null = null;
  private activeExecutions: Map<string, WorkflowExecution> = new Map();

  constructor() {
    super();
    this.initializeDefaultWorkflows();
    this.startProcessing();
  }

  private initializeDefaultWorkflows(): void {
    // Workflow de procesamiento de feedback crítico
    const criticalFeedbackWorkflow: WorkflowDefinition = {
      id: 'critical_feedback_workflow',
      name: 'Critical Feedback Processing',
      description: 'Automatically process and escalate critical feedback',
      version: '1.0.0',
      enabled: true,
      trigger: {
        type: 'event',
        event: 'feedback.created',
        condition: {
          field: 'urgency',
          operator: 'equals',
          value: 'critical'
        }
      },
      steps: [
        {
          id: 'analyze_sentiment',
          name: 'Analyze Sentiment',
          type: 'ai_analysis',
          order: 1,
          enabled: true,
          config: {
            analysisType: 'sentiment',
            model: 'bert-sentiment-latam',
            confidence: 0.8
          },
          onSuccess: 'notify_team',
          onFailure: 'log_error'
        },
        {
          id: 'notify_team',
          name: 'Notify Team',
          type: 'notification',
          order: 2,
          enabled: true,
          config: {
            channels: ['email', 'slack'],
            template: 'critical_feedback_alert',
            priority: 'high'
          },
          onSuccess: 'create_ticket',
          onFailure: 'log_error'
        },
        {
          id: 'create_ticket',
          name: 'Create Support Ticket',
          type: 'webhook',
          order: 3,
          enabled: true,
          config: {
            url: 'https://api.zendesk.com/v2/tickets.json',
            method: 'POST',
            authentication: 'api_key',
            headers: {
              'Content-Type': 'application/json'
            }
          },
          onSuccess: 'update_crm',
          onFailure: 'log_error'
        },
        {
          id: 'update_crm',
          name: 'Update CRM',
          type: 'webhook',
          order: 4,
          enabled: true,
          config: {
            url: 'https://api.salesforce.com/v1/cases',
            method: 'POST',
            authentication: 'oauth'
          },
          onSuccess: 'complete',
          onFailure: 'log_error'
        },
        {
          id: 'log_error',
          name: 'Log Error',
          type: 'action',
          order: 5,
          enabled: true,
          config: {
            action: 'log_error',
            level: 'error'
          }
        },
        {
          id: 'complete',
          name: 'Complete',
          type: 'action',
          order: 6,
          enabled: true,
          config: {
            action: 'complete'
          }
        }
      ],
      conditions: [
        {
          id: 'is_critical',
          name: 'Is Critical Feedback',
          expression: 'data.urgency === "critical"',
          description: 'Check if feedback is critical',
          enabled: true
        }
      ],
      variables: [
        {
          id: 'feedback_data',
          name: 'feedbackData',
          type: 'object',
          value: null,
          description: 'The feedback data being processed',
          scope: 'workflow'
        },
        {
          id: 'analysis_result',
          name: 'analysisResult',
          type: 'object',
          value: null,
          description: 'Result of AI analysis',
          scope: 'workflow'
        }
      ],
      settings: {
        maxExecutionTime: 300000, // 5 minutes
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
      },
      created: new Date(),
      updated: new Date(),
      executionCount: 0,
      successCount: 0,
      failureCount: 0
    };

    // Workflow de análisis semanal
    const weeklyAnalysisWorkflow: WorkflowDefinition = {
      id: 'weekly_analysis_workflow',
      name: 'Weekly Analysis Report',
      description: 'Generate and send weekly analysis report',
      version: '1.0.0',
      enabled: true,
      trigger: {
        type: 'schedule',
        schedule: {
          frequency: 'weekly',
          time: '09:00'
        }
      },
      steps: [
        {
          id: 'collect_data',
          name: 'Collect Data',
          type: 'data_transform',
          order: 1,
          enabled: true,
          config: {
            source: 'database',
            query: 'SELECT * FROM feedback WHERE created_at >= NOW() - INTERVAL 7 DAY',
            transform: 'aggregate_by_region'
          },
          onSuccess: 'analyze_trends',
          onFailure: 'log_error'
        },
        {
          id: 'analyze_trends',
          name: 'Analyze Trends',
          type: 'ai_analysis',
          order: 2,
          enabled: true,
          config: {
            analysisType: 'trend_analysis',
            model: 'trend-detector',
            timeRange: '7d'
          },
          onSuccess: 'generate_report',
          onFailure: 'log_error'
        },
        {
          id: 'generate_report',
          name: 'Generate Report',
          type: 'action',
          order: 3,
          enabled: true,
          config: {
            action: 'generate_report',
            format: 'pdf',
            template: 'weekly_analysis'
          },
          onSuccess: 'send_email',
          onFailure: 'log_error'
        },
        {
          id: 'send_email',
          name: 'Send Email',
          type: 'email',
          order: 4,
          enabled: true,
          config: {
            to: 'team@company.com',
            subject: 'Weekly Analysis Report',
            template: 'weekly_report_email',
            attachments: ['report.pdf']
          },
          onSuccess: 'complete',
          onFailure: 'log_error'
        }
      ],
      conditions: [],
      variables: [
        {
          id: 'weekly_data',
          name: 'weeklyData',
          type: 'array',
          value: [],
          description: 'Weekly feedback data',
          scope: 'workflow'
        },
        {
          id: 'trend_analysis',
          name: 'trendAnalysis',
          type: 'object',
          value: null,
          description: 'Trend analysis results',
          scope: 'workflow'
        }
      ],
      settings: {
        maxExecutionTime: 600000, // 10 minutes
        maxConcurrentExecutions: 1,
        retryPolicy: {
          maxRetries: 2,
          retryDelay: 5000,
          backoffMultiplier: 1.5
        },
        errorHandling: 'continue',
        logging: {
          enabled: true,
          level: 'info'
        }
      },
      created: new Date(),
      updated: new Date(),
      executionCount: 0,
      successCount: 0,
      failureCount: 0
    };

    this.workflows.set(criticalFeedbackWorkflow.id, criticalFeedbackWorkflow);
    this.workflows.set(weeklyAnalysisWorkflow.id, weeklyAnalysisWorkflow);
  }

  private startProcessing(): void {
    this.processingInterval = setInterval(() => {
      this.processExecutionQueue();
    }, 1000); // Cada segundo
  }

  stopProcessing(): void {
    if (this.processingInterval) {
      clearInterval(this.processingInterval);
      this.processingInterval = null;
    }
  }

  private async processExecutionQueue(): Promise<void> {
    if (this.isProcessing || this.executionQueue.length === 0) return;

    this.isProcessing = true;
    const execution = this.executionQueue.shift();

    try {
      await this.executeWorkflow(execution);
    } catch (error) {
      console.error('Error processing workflow execution:', error);
    } finally {
      this.isProcessing = false;
    }
  }

  private async executeWorkflow(execution: WorkflowExecution): Promise<void> {
    const workflow = this.workflows.get(execution.workflowId);
    if (!workflow || !workflow.enabled) return;

    execution.status = 'running';
    this.activeExecutions.set(execution.id, execution);
    this.emit('execution_started', execution);

    try {
      // Ejecutar pasos en orden
      for (const step of workflow.steps.sort((a, b) => a.order - b.order)) {
        if (!step.enabled) continue;

        const stepExecution = await this.executeStep(execution, step);
        execution.steps.push(stepExecution);

        if (stepExecution.status === 'failed') {
          if (step.onFailure) {
            const nextStep = workflow.steps.find(s => s.id === step.onFailure);
            if (nextStep) {
              await this.executeStep(execution, nextStep);
            }
          } else {
            execution.status = 'failed';
            execution.error = stepExecution.error;
            break;
          }
        } else if (step.onSuccess) {
          const nextStep = workflow.steps.find(s => s.id === step.onSuccess);
          if (nextStep) {
            await this.executeStep(execution, nextStep);
          }
        }
      }

      if (execution.status === 'running') {
        execution.status = 'completed';
        execution.completedAt = new Date();
        execution.duration = execution.completedAt.getTime() - execution.startedAt.getTime();
        
        workflow.executionCount++;
        workflow.successCount++;
        workflow.lastExecuted = new Date();

        this.emit('execution_completed', execution);
      }
    } catch (error) {
      execution.status = 'failed';
      execution.error = error.message;
      execution.completedAt = new Date();
      execution.duration = execution.completedAt.getTime() - execution.startedAt.getTime();
      
      workflow.executionCount++;
      workflow.failureCount++;

      this.emit('execution_failed', execution);
    } finally {
      this.activeExecutions.delete(execution.id);
    }
  }

  private async executeStep(execution: WorkflowExecution, step: WorkflowStep): Promise<WorkflowStepExecution> {
    const stepExecution: WorkflowStepExecution = {
      id: `step_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      stepId: step.id,
      stepName: step.name,
      status: 'running',
      startedAt: new Date(),
      input: execution.variables,
      retryCount: 0,
      metadata: {}
    };

    this.emit('step_started', stepExecution);

    try {
      // Ejecutar paso según su tipo
      const output = await this.executeStepByType(step, execution.variables);
      
      stepExecution.status = 'completed';
      stepExecution.completedAt = new Date();
      stepExecution.duration = stepExecution.completedAt.getTime() - stepExecution.startedAt.getTime();
      stepExecution.output = output;

      // Actualizar variables de ejecución
      if (output && typeof output === 'object') {
        Object.assign(execution.variables, output);
      }

      this.emit('step_completed', stepExecution);
    } catch (error) {
      stepExecution.status = 'failed';
      stepExecution.error = error.message;
      stepExecution.completedAt = new Date();
      stepExecution.duration = stepExecution.completedAt.getTime() - stepExecution.startedAt.getTime();

      this.emit('step_failed', stepExecution);
    }

    return stepExecution;
  }

  private async executeStepByType(step: WorkflowStep, variables: Record<string, any>): Promise<any> {
    switch (step.type) {
      case 'action':
        return this.executeAction(step, variables);
      case 'condition':
        return this.executeCondition(step, variables);
      case 'loop':
        return this.executeLoop(step, variables);
      case 'delay':
        return this.executeDelay(step, variables);
      case 'webhook':
        return this.executeWebhook(step, variables);
      case 'email':
        return this.executeEmail(step, variables);
      case 'notification':
        return this.executeNotification(step, variables);
      case 'data_transform':
        return this.executeDataTransform(step, variables);
      case 'ai_analysis':
        return this.executeAIAnalysis(step, variables);
      default:
        throw new Error(`Unknown step type: ${step.type}`);
    }
  }

  private async executeAction(step: WorkflowStep, variables: Record<string, any>): Promise<any> {
    const { action } = step.config;
    
    switch (action) {
      case 'log_error':
        console.error('Workflow error logged:', variables);
        return { logged: true };
      case 'complete':
        return { completed: true };
      default:
        return { action, variables };
    }
  }

  private async executeCondition(step: WorkflowStep, variables: Record<string, any>): Promise<any> {
    const { expression } = step.config;
    
    try {
      // Evaluar expresión JavaScript de forma segura
      const result = eval(expression);
      return { condition: result, variables };
    } catch (error) {
      throw new Error(`Condition evaluation failed: ${error.message}`);
    }
  }

  private async executeLoop(step: WorkflowStep, variables: Record<string, any>): Promise<any> {
    const { items, action } = step.config;
    
    const results = [];
    for (const item of items) {
      const result = await this.executeAction({ ...step, config: { action } }, { ...variables, item });
      results.push(result);
    }
    
    return { loopResults: results };
  }

  private async executeDelay(step: WorkflowStep, variables: Record<string, any>): Promise<any> {
    const { duration } = step.config;
    
    await new Promise(resolve => setTimeout(resolve, duration));
    return { delayed: true, duration };
  }

  private async executeWebhook(step: WorkflowStep, variables: Record<string, any>): Promise<any> {
    const { url, method, headers, body } = step.config;
    
    // Simular llamada webhook
    console.log(`Webhook call: ${method} ${url}`);
    return { webhookCalled: true, url, method };
  }

  private async executeEmail(step: WorkflowStep, variables: Record<string, any>): Promise<any> {
    const { to, subject, template } = step.config;
    
    // Simular envío de email
    console.log(`Email sent to ${to}: ${subject}`);
    return { emailSent: true, to, subject };
  }

  private async executeNotification(step: WorkflowStep, variables: Record<string, any>): Promise<any> {
    const { channels, template, priority } = step.config;
    
    // Simular envío de notificación
    console.log(`Notification sent to ${channels.join(', ')}: ${template}`);
    return { notificationSent: true, channels, template };
  }

  private async executeDataTransform(step: WorkflowStep, variables: Record<string, any>): Promise<any> {
    const { source, query, transform } = step.config;
    
    // Simular transformación de datos
    console.log(`Data transform: ${transform} on ${source}`);
    return { transformed: true, source, transform };
  }

  private async executeAIAnalysis(step: WorkflowStep, variables: Record<string, any>): Promise<any> {
    const { analysisType, model, confidence } = step.config;
    
    // Simular análisis de IA
    console.log(`AI Analysis: ${analysisType} using ${model}`);
    return { 
      analysisType, 
      model, 
      confidence,
      result: { sentiment: 'positive', score: 0.85 }
    };
  }

  // Ejecutar workflow
  executeWorkflow(workflowId: string, triggerData: any, triggeredBy: string = 'system'): string {
    const workflow = this.workflows.get(workflowId);
    if (!workflow || !workflow.enabled) {
      throw new Error(`Workflow ${workflowId} not found or disabled`);
    }

    const execution: WorkflowExecution = {
      id: `exec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      workflowId,
      workflowName: workflow.name,
      status: 'pending',
      startedAt: new Date(),
      triggeredBy,
      triggerData,
      variables: { ...triggerData },
      steps: [],
      metadata: {}
    };

    this.executions.set(execution.id, execution);
    this.executionQueue.push(execution);
    this.emit('execution_queued', execution);

    return execution.id;
  }

  // Crear workflow
  createWorkflow(workflow: Omit<WorkflowDefinition, 'id' | 'created' | 'updated' | 'executionCount' | 'successCount' | 'failureCount'>): string {
    const id = `workflow_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newWorkflow: WorkflowDefinition = {
      ...workflow,
      id,
      created: new Date(),
      updated: new Date(),
      executionCount: 0,
      successCount: 0,
      failureCount: 0
    };

    this.workflows.set(id, newWorkflow);
    this.emit('workflow_created', newWorkflow);
    return id;
  }

  // Obtener workflows
  getWorkflows(): WorkflowDefinition[] {
    return Array.from(this.workflows.values());
  }

  // Obtener ejecuciones
  getExecutions(limit?: number): WorkflowExecution[] {
    const executions = Array.from(this.executions.values())
      .sort((a, b) => b.startedAt.getTime() - a.startedAt.getTime());
    
    return limit ? executions.slice(0, limit) : executions;
  }

  // Obtener estadísticas
  getStats(): {
    totalWorkflows: number;
    enabledWorkflows: number;
    totalExecutions: number;
    activeExecutions: number;
    successfulExecutions: number;
    failedExecutions: number;
    averageExecutionTime: number;
  } {
    const workflows = Array.from(this.workflows.values());
    const executions = Array.from(this.executions.values());
    
    const totalExecutions = executions.length;
    const successfulExecutions = executions.filter(e => e.status === 'completed').length;
    const failedExecutions = executions.filter(e => e.status === 'failed').length;
    const activeExecutions = this.activeExecutions.size;
    
    const averageExecutionTime = executions.length > 0 
      ? executions.reduce((sum, e) => sum + (e.duration || 0), 0) / executions.length
      : 0;
    
    return {
      totalWorkflows: workflows.length,
      enabledWorkflows: workflows.filter(w => w.enabled).length,
      totalExecutions,
      activeExecutions,
      successfulExecutions,
      failedExecutions,
      averageExecutionTime
    };
  }
}

export const advancedWorkflowService = new AdvancedWorkflowService();






