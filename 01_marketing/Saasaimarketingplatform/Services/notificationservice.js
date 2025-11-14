const nodemailer = require('nodemailer');
const axios = require('axios');
const User = require('../models/User');
const realTimeService = require('./realTimeService');

class NotificationService {
  constructor() {
    this.emailTransporter = null;
    this.pushService = null;
    this.smsService = null;
    this.notificationTemplates = new Map();
    this.userPreferences = new Map();
    this.isInitialized = false;
  }

  /**
   * Initialize notification service
   */
  async initialize() {
    if (this.isInitialized) return;

    try {
      await this.setupEmailTransporter();
      await this.setupPushService();
      await this.setupSMSService();
      await this.loadNotificationTemplates();
      await this.loadUserPreferences();
      this.isInitialized = true;
      console.log('Notification Service initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Notification Service:', error);
      throw error;
    }
  }

  /**
   * Setup email transporter
   */
  async setupEmailTransporter() {
    this.emailTransporter = nodemailer.createTransporter({
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
   * Setup push notification service
   */
  async setupPushService() {
    // This would integrate with Firebase, OneSignal, or similar
    this.pushService = {
      send: async (userId, notification) => {
        // Implementation for push notifications
        console.log(`Sending push notification to user ${userId}:`, notification);
      }
    };
  }

  /**
   * Setup SMS service
   */
  async setupSMSService() {
    // This would integrate with Twilio, AWS SNS, or similar
    this.smsService = {
      send: async (phoneNumber, message) => {
        // Implementation for SMS notifications
        console.log(`Sending SMS to ${phoneNumber}:`, message);
      }
    };
  }

  /**
   * Send notification to user
   */
  async sendNotification(userId, notification) {
    try {
      const user = await User.findById(userId);
      if (!user) {
        throw new Error('User not found');
      }

      const preferences = await this.getUserPreferences(userId);
      const channels = this.determineNotificationChannels(notification, preferences);

      const results = [];

      // Send via email
      if (channels.includes('email') && preferences.email) {
        const emailResult = await this.sendEmailNotification(user, notification);
        results.push({ channel: 'email', success: emailResult.success, error: emailResult.error });
      }

      // Send via push notification
      if (channels.includes('push') && preferences.push) {
        const pushResult = await this.sendPushNotification(userId, notification);
        results.push({ channel: 'push', success: pushResult.success, error: pushResult.error });
      }

      // Send via SMS
      if (channels.includes('sms') && preferences.sms && user.phoneNumber) {
        const smsResult = await this.sendSMSNotification(user.phoneNumber, notification);
        results.push({ channel: 'sms', success: smsResult.success, error: smsResult.error });
      }

      // Send via real-time (WebSocket)
      if (channels.includes('realtime')) {
        realTimeService.sendNotificationToUser(userId, notification);
        results.push({ channel: 'realtime', success: true });
      }

      return {
        success: results.some(r => r.success),
        results
      };
    } catch (error) {
      console.error('Send notification error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Send email notification
   */
  async sendEmailNotification(user, notification) {
    try {
      const template = this.getNotificationTemplate(notification.type, 'email');
      const html = this.renderEmailTemplate(template, {
        user,
        notification,
        ...notification.data
      });

      const mailOptions = {
        from: process.env.EMAIL_FROM,
        to: user.email,
        subject: notification.subject || template.subject,
        html
      };

      await this.emailTransporter.sendMail(mailOptions);
      return { success: true };
    } catch (error) {
      console.error('Email notification error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Send push notification
   */
  async sendPushNotification(userId, notification) {
    try {
      await this.pushService.send(userId, {
        title: notification.title,
        body: notification.message,
        data: notification.data,
        icon: notification.icon,
        badge: notification.badge
      });
      return { success: true };
    } catch (error) {
      console.error('Push notification error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Send SMS notification
   */
  async sendSMSNotification(phoneNumber, notification) {
    try {
      const message = this.formatSMSMessage(notification);
      await this.smsService.send(phoneNumber, message);
      return { success: true };
    } catch (error) {
      console.error('SMS notification error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Send bulk notifications
   */
  async sendBulkNotifications(userIds, notification) {
    const results = [];
    
    for (const userId of userIds) {
      try {
        const result = await this.sendNotification(userId, notification);
        results.push({ userId, ...result });
      } catch (error) {
        results.push({ userId, success: false, error: error.message });
      }
    }

    return results;
  }

  /**
   * Send notification to user segment
   */
  async sendNotificationToSegment(segment, notification) {
    try {
      const users = await this.getUsersBySegment(segment);
      const userIds = users.map(user => user._id.toString());
      return await this.sendBulkNotifications(userIds, notification);
    } catch (error) {
      console.error('Send notification to segment error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Schedule notification
   */
  async scheduleNotification(userId, notification, scheduledAt) {
    const scheduledNotification = {
      id: require('crypto').randomUUID(),
      userId,
      notification,
      scheduledAt: new Date(scheduledAt),
      status: 'scheduled',
      createdAt: new Date()
    };

    // Store in database or queue
    this.scheduledNotifications = this.scheduledNotifications || new Map();
    this.scheduledNotifications.set(scheduledNotification.id, scheduledNotification);

    // Schedule execution
    const delay = scheduledNotification.scheduledAt.getTime() - Date.now();
    if (delay > 0) {
      setTimeout(async () => {
        await this.executeScheduledNotification(scheduledNotification.id);
      }, delay);
    }

    return scheduledNotification;
  }

  /**
   * Execute scheduled notification
   */
  async executeScheduledNotification(notificationId) {
    const scheduledNotification = this.scheduledNotifications?.get(notificationId);
    if (!scheduledNotification) {
      return;
    }

    try {
      await this.sendNotification(scheduledNotification.userId, scheduledNotification.notification);
      scheduledNotification.status = 'sent';
      scheduledNotification.sentAt = new Date();
    } catch (error) {
      scheduledNotification.status = 'failed';
      scheduledNotification.error = error.message;
    }

    this.scheduledNotifications.set(notificationId, scheduledNotification);
  }

  /**
   * Get notification templates
   */
  getNotificationTemplate(type, channel) {
    const templates = {
      'content_generated': {
        email: {
          subject: 'Your Content is Ready!',
          template: `
            <h2>Content Generated Successfully</h2>
            <p>Hello {{user.firstName}},</p>
            <p>Your {{notification.data.templateName}} content has been generated successfully.</p>
            <div style="background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px;">
              <h3>Generated Content:</h3>
              <p>{{notification.data.content}}</p>
            </div>
            <p><a href="{{notification.data.viewUrl}}">View in Dashboard</a></p>
          `
        },
        push: {
          title: 'Content Ready!',
          body: 'Your {{notification.data.templateName}} content has been generated.'
        },
        sms: 'Your {{notification.data.templateName}} content is ready! View: {{notification.data.viewUrl}}'
      },
      'collaboration_invite': {
        email: {
          subject: 'You\'ve been invited to collaborate',
          template: `
            <h2>Collaboration Invitation</h2>
            <p>Hello {{user.firstName}},</p>
            <p>{{notification.data.inviterName}} has invited you to collaborate on a content project.</p>
            <p><strong>Project:</strong> {{notification.data.contentTitle}}</p>
            <p><a href="{{notification.data.joinUrl}}">Join Collaboration</a></p>
          `
        },
        push: {
          title: 'Collaboration Invite',
          body: '{{notification.data.inviterName}} invited you to collaborate'
        },
        sms: '{{notification.data.inviterName}} invited you to collaborate on {{notification.data.contentTitle}}'
      },
      'automation_completed': {
        email: {
          subject: 'Automation Completed',
          template: `
            <h2>Automation Completed</h2>
            <p>Hello {{user.firstName}},</p>
            <p>Your automation "{{notification.data.automationName}}" has completed successfully.</p>
            <p><strong>Generated:</strong> {{notification.data.contentCount}} pieces of content</p>
            <p><a href="{{notification.data.dashboardUrl}}">View Results</a></p>
          `
        },
        push: {
          title: 'Automation Complete',
          body: '{{notification.data.automationName}} completed successfully'
        },
        sms: 'Automation "{{notification.data.automationName}}" completed successfully'
      },
      'usage_limit_warning': {
        email: {
          subject: 'Usage Limit Warning',
          template: `
            <h2>Usage Limit Warning</h2>
            <p>Hello {{user.firstName}},</p>
            <p>You've used {{notification.data.used}} of {{notification.data.limit}} content generations this month.</p>
            <p>Consider upgrading your plan to continue generating content.</p>
            <p><a href="{{notification.data.upgradeUrl}}">Upgrade Now</a></p>
          `
        },
        push: {
          title: 'Usage Limit Warning',
          body: 'You\'re approaching your monthly limit'
        },
        sms: 'Usage limit warning: {{notification.data.used}}/{{notification.data.limit}} used'
      }
    };

    return templates[type]?.[channel] || templates['default']?.[channel];
  }

  /**
   * Render email template
   */
  renderEmailTemplate(template, data) {
    let html = template.template || template;
    
    // Replace placeholders
    html = html.replace(/\{\{([^}]+)\}\}/g, (match, path) => {
      const value = this.getNestedValue(data, path.trim());
      return value || match;
    });

    return html;
  }

  /**
   * Format SMS message
   */
  formatSMSMessage(notification) {
    let message = notification.message || notification.title;
    
    // Replace placeholders
    message = message.replace(/\{\{([^}]+)\}\}/g, (match, path) => {
      const value = this.getNestedValue(notification.data, path.trim());
      return value || match;
    });

    return message;
  }

  /**
   * Get nested value from object
   */
  getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }

  /**
   * Determine notification channels
   */
  determineNotificationChannels(notification, preferences) {
    const channels = [];
    
    // Always include real-time for immediate notifications
    channels.push('realtime');
    
    // Add other channels based on notification type and user preferences
    if (notification.priority === 'high') {
      if (preferences.email) channels.push('email');
      if (preferences.push) channels.push('push');
      if (preferences.sms) channels.push('sms');
    } else if (notification.priority === 'medium') {
      if (preferences.email) channels.push('email');
      if (preferences.push) channels.push('push');
    } else {
      if (preferences.email) channels.push('email');
    }

    return channels;
  }

  /**
   * Get user preferences
   */
  async getUserPreferences(userId) {
    const user = await User.findById(userId);
    if (!user) {
      return this.getDefaultPreferences();
    }

    return {
      email: user.preferences?.notifications?.email ?? true,
      push: user.preferences?.notifications?.push ?? true,
      sms: user.preferences?.notifications?.sms ?? false,
      marketing: user.preferences?.notifications?.marketing ?? true
    };
  }

  /**
   * Get default preferences
   */
  getDefaultPreferences() {
    return {
      email: true,
      push: true,
      sms: false,
      marketing: true
    };
  }

  /**
   * Get users by segment
   */
  async getUsersBySegment(segment) {
    const query = {};
    
    switch (segment.type) {
      case 'plan':
        query['subscription.plan'] = segment.value;
        break;
      case 'industry':
        query.industry = segment.value;
        break;
      case 'usage':
        query['usage.contentGenerations'] = { $gte: segment.value };
        break;
      case 'lastActive':
        const daysAgo = new Date();
        daysAgo.setDate(daysAgo.getDate() - segment.value);
        query.lastLogin = { $gte: daysAgo };
        break;
    }

    return await User.find(query);
  }

  /**
   * Load notification templates
   */
  async loadNotificationTemplates() {
    // Load templates from database or file
    this.notificationTemplates.set('default', {
      email: {
        subject: 'Notification from AI Marketing Platform',
        template: '<h2>{{notification.title}}</h2><p>{{notification.message}}</p>'
      },
      push: {
        title: '{{notification.title}}',
        body: '{{notification.message}}'
      },
      sms: '{{notification.title}}: {{notification.message}}'
    });
  }

  /**
   * Load user preferences
   */
  async loadUserPreferences() {
    // Load user preferences from database
    console.log('Loading user preferences...');
  }

  /**
   * Create notification
   */
  createNotification(type, data, options = {}) {
    return {
      type,
      title: data.title || this.getDefaultTitle(type),
      message: data.message || this.getDefaultMessage(type),
      data,
      priority: options.priority || 'medium',
      channels: options.channels || ['realtime'],
      scheduledAt: options.scheduledAt,
      expiresAt: options.expiresAt,
      metadata: {
        source: options.source || 'system',
        category: options.category || 'general',
        tags: options.tags || []
      }
    };
  }

  /**
   * Get default title for notification type
   */
  getDefaultTitle(type) {
    const titles = {
      'content_generated': 'Content Generated',
      'collaboration_invite': 'Collaboration Invitation',
      'automation_completed': 'Automation Completed',
      'usage_limit_warning': 'Usage Limit Warning',
      'payment_success': 'Payment Successful',
      'payment_failed': 'Payment Failed',
      'subscription_expired': 'Subscription Expired'
    };
    return titles[type] || 'Notification';
  }

  /**
   * Get default message for notification type
   */
  getDefaultMessage(type) {
    const messages = {
      'content_generated': 'Your content has been generated successfully.',
      'collaboration_invite': 'You have been invited to collaborate on a project.',
      'automation_completed': 'Your automation has completed successfully.',
      'usage_limit_warning': 'You are approaching your usage limit.',
      'payment_success': 'Your payment has been processed successfully.',
      'payment_failed': 'Your payment could not be processed.',
      'subscription_expired': 'Your subscription has expired.'
    };
    return messages[type] || 'You have a new notification.';
  }

  /**
   * Get notification statistics
   */
  async getNotificationStats(userId, timeRange = '30d') {
    // This would query notification logs from database
    return {
      totalSent: 0,
      emailSent: 0,
      pushSent: 0,
      smsSent: 0,
      realtimeSent: 0,
      successRate: 0,
      averageDeliveryTime: 0
    };
  }

  /**
   * Mark notification as read
   */
  async markAsRead(userId, notificationId) {
    // Update notification status in database
    console.log(`Marking notification ${notificationId} as read for user ${userId}`);
  }

  /**
   * Get user notifications
   */
  async getUserNotifications(userId, options = {}) {
    const { limit = 20, offset = 0, unreadOnly = false } = options;
    
    // This would query notifications from database
    return {
      notifications: [],
      total: 0,
      unread: 0
    };
  }
}

module.exports = new NotificationService();