const cron = require('node-cron');
const nodemailer = require('nodemailer');
const axios = require('axios');
const mongoose = require('mongoose');
const User = require('../models/User');
const GeneratedContent = require('../models/GeneratedContent');
const ContentTemplate = require('../models/ContentTemplate');
const aiService = require('./advancedAIService');
const analyticsService = require('./analyticsService');

class AutomationService {
  constructor() {
    this.scheduledJobs = new Map();
    this.emailTransporter = this.createEmailTransporter();
    this.webhookEndpoints = new Map();
    this.automationRules = new Map();
    this.isInitialized = false;
  }

  /**
   * Initialize automation service
   */
  async initialize() {
    if (this.isInitialized) return;

    try {
      await this.loadAutomationRules();
      await this.setupDefaultJobs();
      this.isInitialized = true;
      console.log('Automation Service initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Automation Service:', error);
      throw error;
    }
  }

  /**
   * Create email transporter
   */
  createEmailTransporter() {
    return nodemailer.createTransporter({
      host: process.env.EMAIL_HOST,
      port: process.env.EMAIL_PORT,
      secure: false,
      auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS
      }
    });
  }

  /**
   * Schedule content generation
   */
  async scheduleContentGeneration(userId, schedule) {
    const {
      templateId,
      variables,
      frequency,
      time,
      timezone = 'UTC',
      enabled = true,
      name,
      description
    } = schedule;

    const jobId = `content_gen_${userId}_${Date.now()}`;
    
    const cronExpression = this.convertFrequencyToCron(frequency, time);
    
    const job = cron.schedule(cronExpression, async () => {
      try {
        await this.executeScheduledContentGeneration(userId, {
          templateId,
          variables,
          name,
          description
        });
      } catch (error) {
        console.error(`Scheduled content generation failed for user ${userId}:`, error);
        await this.sendErrorNotification(userId, error);
      }
    }, {
      scheduled: enabled,
      timezone
    });

    this.scheduledJobs.set(jobId, {
      job,
      userId,
      schedule,
      createdAt: new Date(),
      lastRun: null,
      nextRun: job.nextDate()
    });

    return jobId;
  }

  /**
   * Execute scheduled content generation
   */
  async executeScheduledContentGeneration(userId, options) {
    const { templateId, variables, name, description } = options;
    
    const user = await User.findById(userId);
    if (!user || !user.isActive) {
      throw new Error('User not found or inactive');
    }

    // Check usage limits
    if (!user.checkUsageLimit()) {
      await this.sendUsageLimitNotification(userId);
      return;
    }

    const template = await ContentTemplate.findById(templateId);
    if (!template) {
      throw new Error('Template not found');
    }

    // Generate content
    const result = await aiService.generateAdvancedContent({
      prompt: template.prompt,
      context: variables,
      model: template.aiSettings?.model || 'gpt-3.5-turbo',
      temperature: template.aiSettings?.temperature || 0.7,
      maxTokens: template.aiSettings?.maxTokens || 500
    });

    // Save generated content
    const generatedContent = new GeneratedContent({
      userId,
      templateId,
      prompt: template.prompt,
      variables,
      content: result.content,
      metadata: result.metadata,
      status: 'completed',
      tags: ['automated', name || 'scheduled'],
      createdAt: new Date()
    });

    await generatedContent.save();

    // Update user usage
    user.usage.contentGenerations += 1;
    await user.save();

    // Update job info
    const jobId = Array.from(this.scheduledJobs.keys())
      .find(id => this.scheduledJobs.get(id).userId === userId);
    
    if (jobId) {
      this.scheduledJobs.get(jobId).lastRun = new Date();
    }

    // Send notification
    await this.sendContentGeneratedNotification(userId, {
      content: result.content,
      templateName: template.name,
      name: name || 'Scheduled Content'
    });

    return generatedContent;
  }

  /**
   * Create automation workflow
   */
  async createWorkflow(userId, workflow) {
    const {
      name,
      description,
      triggers,
      actions,
      conditions,
      enabled = true
    } = workflow;

    const workflowId = new mongoose.Types.ObjectId();
    
    const workflowData = {
      _id: workflowId,
      userId,
      name,
      description,
      triggers,
      actions,
      conditions,
      enabled,
      createdAt: new Date(),
      lastExecuted: null,
      executionCount: 0,
      successCount: 0,
      failureCount: 0
    };

    this.automationRules.set(workflowId.toString(), workflowData);

    // Setup triggers
    await this.setupWorkflowTriggers(workflowId.toString(), triggers);

    return workflowId;
  }

  /**
   * Setup workflow triggers
   */
  async setupWorkflowTriggers(workflowId, triggers) {
    for (const trigger of triggers) {
      switch (trigger.type) {
        case 'schedule':
          await this.setupScheduleTrigger(workflowId, trigger);
          break;
        case 'webhook':
          await this.setupWebhookTrigger(workflowId, trigger);
          break;
        case 'user_action':
          await this.setupUserActionTrigger(workflowId, trigger);
          break;
        case 'analytics_threshold':
          await this.setupAnalyticsTrigger(workflowId, trigger);
          break;
      }
    }
  }

  /**
   * Execute workflow
   */
  async executeWorkflow(workflowId, triggerData = {}) {
    const workflow = this.automationRules.get(workflowId);
    if (!workflow || !workflow.enabled) {
      return;
    }

    try {
      // Check conditions
      const conditionsMet = await this.checkWorkflowConditions(workflow.conditions, triggerData);
      if (!conditionsMet) {
        return;
      }

      // Execute actions
      for (const action of workflow.actions) {
        await this.executeWorkflowAction(action, triggerData);
      }

      // Update workflow stats
      workflow.lastExecuted = new Date();
      workflow.executionCount += 1;
      workflow.successCount += 1;

    } catch (error) {
      console.error(`Workflow execution failed for ${workflowId}:`, error);
      workflow.failureCount += 1;
      
      // Send error notification
      await this.sendWorkflowErrorNotification(workflow.userId, workflowId, error);
    }
  }

  /**
   * Execute workflow action
   */
  async executeWorkflowAction(action, triggerData) {
    switch (action.type) {
      case 'generate_content':
        await this.executeContentGenerationAction(action, triggerData);
        break;
      case 'send_email':
        await this.executeEmailAction(action, triggerData);
        break;
      case 'webhook_call':
        await this.executeWebhookAction(action, triggerData);
        break;
      case 'update_user':
        await this.executeUserUpdateAction(action, triggerData);
        break;
      case 'create_reminder':
        await this.executeReminderAction(action, triggerData);
        break;
    }
  }

  /**
   * Execute content generation action
   */
  async executeContentGenerationAction(action, triggerData) {
    const { templateId, variables, targetAudience } = action;
    
    const result = await aiService.generateAdvancedContent({
      prompt: action.prompt,
      context: { ...variables, ...triggerData },
      targetAudience,
      model: action.model || 'gpt-3.5-turbo'
    });

    // Save content
    const generatedContent = new GeneratedContent({
      userId: triggerData.userId,
      templateId,
      prompt: action.prompt,
      variables: { ...variables, ...triggerData },
      content: result.content,
      metadata: result.metadata,
      status: 'completed',
      tags: ['workflow', action.name || 'automated'],
      createdAt: new Date()
    });

    await generatedContent.save();
    return generatedContent;
  }

  /**
   * Execute email action
   */
  async executeEmailAction(action, triggerData) {
    const { to, subject, template, variables } = action;
    
    const emailContent = await aiService.generateAdvancedContent({
      prompt: template,
      context: { ...variables, ...triggerData },
      model: 'gpt-3.5-turbo'
    });

    const mailOptions = {
      from: process.env.EMAIL_FROM,
      to: to,
      subject: subject,
      html: emailContent.content
    };

    await this.emailTransporter.sendMail(mailOptions);
  }

  /**
   * Execute webhook action
   */
  async executeWebhookAction(action, triggerData) {
    const { url, method = 'POST', headers = {}, data } = action;
    
    const payload = {
      ...data,
      triggerData,
      timestamp: new Date().toISOString()
    };

    await axios({
      method,
      url,
      headers,
      data: payload
    });
  }

  /**
   * Setup analytics trigger
   */
  async setupAnalyticsTrigger(workflowId, trigger) {
    const { metric, threshold, operator = 'greater_than' } = trigger;
    
    // Schedule periodic check
    const checkJob = cron.schedule('*/15 * * * *', async () => {
      try {
        const analytics = await analyticsService.getUserAnalytics(trigger.userId, '7d');
        const currentValue = this.extractMetricValue(analytics, metric);
        
        let shouldTrigger = false;
        switch (operator) {
          case 'greater_than':
            shouldTrigger = currentValue > threshold;
            break;
          case 'less_than':
            shouldTrigger = currentValue < threshold;
            break;
          case 'equals':
            shouldTrigger = currentValue === threshold;
            break;
        }

        if (shouldTrigger) {
          await this.executeWorkflow(workflowId, {
            userId: trigger.userId,
            metric,
            value: currentValue,
            threshold
          });
        }
      } catch (error) {
        console.error(`Analytics trigger failed for workflow ${workflowId}:`, error);
      }
    });

    this.scheduledJobs.set(`analytics_${workflowId}`, {
      job: checkJob,
      workflowId,
      trigger,
      createdAt: new Date()
    });
  }

  /**
   * Extract metric value from analytics
   */
  extractMetricValue(analytics, metric) {
    const metricPath = metric.split('.');
    let value = analytics;
    
    for (const key of metricPath) {
      value = value?.[key];
    }
    
    return value || 0;
  }

  /**
   * Convert frequency to cron expression
   */
  convertFrequencyToCron(frequency, time) {
    switch (frequency) {
      case 'daily':
        const [hour, minute] = time.split(':');
        return `${minute} ${hour} * * *`;
      case 'weekly':
        const [day, timeStr] = time.split(' ');
        const [hour, min] = timeStr.split(':');
        return `${min} ${hour} * * ${day}`;
      case 'monthly':
        const [date, timeStr2] = time.split(' ');
        const [hour2, min2] = timeStr2.split(':');
        return `${min2} ${hour2} ${date} * *`;
      case 'hourly':
        return `0 * * * *`;
      default:
        return '0 9 * * *'; // Daily at 9 AM
    }
  }

  /**
   * Send content generated notification
   */
  async sendContentGeneratedNotification(userId, data) {
    const user = await User.findById(userId);
    if (!user || !user.preferences?.notifications?.email) {
      return;
    }

    const mailOptions = {
      from: process.env.EMAIL_FROM,
      to: user.email,
      subject: `New Content Generated: ${data.name}`,
      html: `
        <h2>Your scheduled content is ready!</h2>
        <p><strong>Template:</strong> ${data.templateName}</p>
        <p><strong>Name:</strong> ${data.name}</p>
        <div style="background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px;">
          <h3>Generated Content:</h3>
          <p>${data.content}</p>
        </div>
        <p><a href="${process.env.FRONTEND_URL}/content">View in Dashboard</a></p>
      `
    };

    await this.emailTransporter.sendMail(mailOptions);
  }

  /**
   * Send usage limit notification
   */
  async sendUsageLimitNotification(userId) {
    const user = await User.findById(userId);
    if (!user) return;

    const mailOptions = {
      from: process.env.EMAIL_FROM,
      to: user.email,
      subject: 'Usage Limit Reached - Upgrade Your Plan',
      html: `
        <h2>Usage Limit Reached</h2>
        <p>You've reached your monthly content generation limit.</p>
        <p><strong>Current Plan:</strong> ${user.subscription.plan}</p>
        <p><strong>Usage:</strong> ${user.usage.contentGenerations}/${user.usage.monthlyLimit}</p>
        <p><a href="${process.env.FRONTEND_URL}/pricing">Upgrade Your Plan</a></p>
      `
    };

    await this.emailTransporter.sendMail(mailOptions);
  }

  /**
   * Send error notification
   */
  async sendErrorNotification(userId, error) {
    const user = await User.findById(userId);
    if (!user) return;

    const mailOptions = {
      from: process.env.EMAIL_FROM,
      to: user.email,
      subject: 'Automation Error - Action Required',
      html: `
        <h2>Automation Error</h2>
        <p>An error occurred in your scheduled automation:</p>
        <p><strong>Error:</strong> ${error.message}</p>
        <p><a href="${process.env.FRONTEND_URL}/automation">Check Your Automations</a></p>
      `
    };

    await this.emailTransporter.sendMail(mailOptions);
  }

  /**
   * Load automation rules from database
   */
  async loadAutomationRules() {
    // This would load from a Workflow collection
    // For now, we'll use in-memory storage
    console.log('Loading automation rules...');
  }

  /**
   * Setup default jobs
   */
  async setupDefaultJobs() {
    // Daily analytics summary
    cron.schedule('0 9 * * *', async () => {
      await this.sendDailyAnalyticsSummary();
    });

    // Weekly performance report
    cron.schedule('0 9 * * 1', async () => {
      await this.sendWeeklyPerformanceReport();
    });

    // Monthly usage reset
    cron.schedule('0 0 1 * *', async () => {
      await this.resetMonthlyUsage();
    });
  }

  /**
   * Send daily analytics summary
   */
  async sendDailyAnalyticsSummary() {
    const users = await User.find({ 
      'preferences.notifications.email': true,
      isActive: true 
    });

    for (const user of users) {
      try {
        const analytics = await analyticsService.getUserAnalytics(user._id, '1d');
        
        const mailOptions = {
          from: process.env.EMAIL_FROM,
          to: user.email,
          subject: 'Daily Analytics Summary',
          html: `
            <h2>Your Daily Performance</h2>
            <p><strong>Content Generated:</strong> ${analytics.overview.totalContent}</p>
            <p><strong>Total Views:</strong> ${analytics.overview.totalViews}</p>
            <p><strong>Total Shares:</strong> ${analytics.overview.totalShares}</p>
            <p><a href="${process.env.FRONTEND_URL}/analytics">View Full Analytics</a></p>
          `
        };

        await this.emailTransporter.sendMail(mailOptions);
      } catch (error) {
        console.error(`Failed to send daily summary to user ${user._id}:`, error);
      }
    }
  }

  /**
   * Send weekly performance report
   */
  async sendWeeklyPerformanceReport() {
    const users = await User.find({ 
      'preferences.notifications.email': true,
      isActive: true 
    });

    for (const user of users) {
      try {
        const analytics = await analyticsService.getUserAnalytics(user._id, '7d');
        
        const mailOptions = {
          from: process.env.EMAIL_FROM,
          to: user.email,
          subject: 'Weekly Performance Report',
          html: `
            <h2>Your Weekly Performance</h2>
            <p><strong>Content Generated:</strong> ${analytics.overview.totalContent}</p>
            <p><strong>Growth Rate:</strong> ${analytics.usage.usageGrowth.toFixed(1)}%</p>
            <p><strong>Top Performing Content:</strong></p>
            <ul>
              ${analytics.performance.topPerformingContent.slice(0, 3).map(content => 
                `<li>${content.content.substring(0, 100)}...</li>`
              ).join('')}
            </ul>
            <p><a href="${process.env.FRONTEND_URL}/analytics">View Full Report</a></p>
          `
        };

        await this.emailTransporter.sendMail(mailOptions);
      } catch (error) {
        console.error(`Failed to send weekly report to user ${user._id}:`, error);
      }
    }
  }

  /**
   * Reset monthly usage
   */
  async resetMonthlyUsage() {
    await User.updateMany(
      {},
      {
        $set: {
          'usage.contentGenerations': 0,
          'usage.lastResetDate': new Date()
        }
      }
    );
    console.log('Monthly usage reset completed');
  }

  /**
   * Get user automations
   */
  async getUserAutomations(userId) {
    const automations = [];
    
    // Get scheduled jobs
    for (const [jobId, jobData] of this.scheduledJobs) {
      if (jobData.userId === userId) {
        automations.push({
          id: jobId,
          type: 'scheduled',
          ...jobData.schedule,
          lastRun: jobData.lastRun,
          nextRun: jobData.nextRun
        });
      }
    }

    // Get workflows
    for (const [workflowId, workflow] of this.automationRules) {
      if (workflow.userId === userId) {
        automations.push({
          id: workflowId,
          type: 'workflow',
          name: workflow.name,
          description: workflow.description,
          enabled: workflow.enabled,
          lastExecuted: workflow.lastExecuted,
          executionCount: workflow.executionCount,
          successCount: workflow.successCount,
          failureCount: workflow.failureCount
        });
      }
    }

    return automations;
  }

  /**
   * Delete automation
   */
  async deleteAutomation(automationId, userId) {
    // Delete scheduled job
    if (this.scheduledJobs.has(automationId)) {
      const jobData = this.scheduledJobs.get(automationId);
      if (jobData.userId === userId) {
        jobData.job.destroy();
        this.scheduledJobs.delete(automationId);
        return true;
      }
    }

    // Delete workflow
    if (this.automationRules.has(automationId)) {
      const workflow = this.automationRules.get(automationId);
      if (workflow.userId === userId) {
        this.automationRules.delete(automationId);
        return true;
      }
    }

    return false;
  }

  /**
   * Toggle automation
   */
  async toggleAutomation(automationId, userId, enabled) {
    // Toggle scheduled job
    if (this.scheduledJobs.has(automationId)) {
      const jobData = this.scheduledJobs.get(automationId);
      if (jobData.userId === userId) {
        if (enabled) {
          jobData.job.start();
        } else {
          jobData.job.stop();
        }
        return true;
      }
    }

    // Toggle workflow
    if (this.automationRules.has(automationId)) {
      const workflow = this.automationRules.get(automationId);
      if (workflow.userId === userId) {
        workflow.enabled = enabled;
        return true;
      }
    }

    return false;
  }
}

module.exports = new AutomationService();






