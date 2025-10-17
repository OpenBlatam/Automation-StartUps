const EventEmitter = require('events');
const nodemailer = require('nodemailer');

/**
 * Advanced Notification Service
 * Real-time notifications and communication system
 */
class NotificationService extends EventEmitter {
  constructor() {
    super();
    
    this.notifications = [];
    this.subscribers = new Map();
    this.channels = {
      email: this.setupEmailChannel(),
      webhook: this.setupWebhookChannel(),
      sms: this.setupSMSChannel(),
      slack: this.setupSlackChannel()
    };
    
    this.templates = {
      welcome: {
        subject: 'Welcome to Neural Marketing Pro! 🧠',
        template: 'welcome',
        priority: 'normal'
      },
      consciousness_evolution: {
        subject: 'Neural Consciousness Evolved! 🌟',
        template: 'consciousness_evolution',
        priority: 'high'
      },
      content_generated: {
        subject: 'Content Generated Successfully! ✍️',
        template: 'content_generated',
        priority: 'normal'
      },
      campaign_completed: {
        subject: 'Campaign Completed! 📢',
        template: 'campaign_completed',
        priority: 'normal'
      },
      alert: {
        subject: 'System Alert! ⚠️',
        template: 'alert',
        priority: 'high'
      },
      insight: {
        subject: 'New AI Insight! 💡',
        template: 'insight',
        priority: 'normal'
      }
    };
    
    this.preferences = {
      email: true,
      push: true,
      sms: false,
      webhook: false
    };
  }
  
  /**
   * Setup email channel
   */
  setupEmailChannel() {
    return nodemailer.createTransporter({
      host: process.env.SMTP_HOST || 'smtp.gmail.com',
      port: process.env.SMTP_PORT || 587,
      secure: false,
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS
      }
    });
  }
  
  /**
   * Setup webhook channel
   */
  setupWebhookChannel() {
    return {
      send: async (notification) => {
        // Webhook implementation
        console.log('Webhook notification:', notification);
      }
    };
  }
  
  /**
   * Setup SMS channel
   */
  setupSMSChannel() {
    return {
      send: async (notification) => {
        // SMS implementation (Twilio, etc.)
        console.log('SMS notification:', notification);
      }
    };
  }
  
  /**
   * Setup Slack channel
   */
  setupSlackChannel() {
    return {
      send: async (notification) => {
        // Slack webhook implementation
        console.log('Slack notification:', notification);
      }
    };
  }
  
  /**
   * Send notification
   */
  async sendNotification(notification) {
    try {
      // Add to notifications list
      this.notifications.unshift(notification);
      this.notifications = this.notifications.slice(0, 1000); // Keep last 1000
      
      // Send to all channels based on preferences
      const promises = [];
      
      if (this.preferences.email && notification.channels.includes('email')) {
        promises.push(this.sendEmail(notification));
      }
      
      if (this.preferences.push && notification.channels.includes('push')) {
        promises.push(this.sendPush(notification));
      }
      
      if (this.preferences.sms && notification.channels.includes('sms')) {
        promises.push(this.sendSMS(notification));
      }
      
      if (this.preferences.webhook && notification.channels.includes('webhook')) {
        promises.push(this.sendWebhook(notification));
      }
      
      await Promise.all(promises);
      
      // Emit notification event
      this.emit('notificationSent', notification);
      
      return { success: true, notification };
      
    } catch (error) {
      console.error('Error sending notification:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Send email notification
   */
  async sendEmail(notification) {
    try {
      const template = this.templates[notification.template] || this.templates.alert;
      
      const mailOptions = {
        from: process.env.SMTP_USER,
        to: notification.recipient,
        subject: template.subject,
        html: this.renderTemplate(template.template, notification.data)
      };
      
      await this.channels.email.sendMail(mailOptions);
      console.log('Email sent:', notification.id);
      
    } catch (error) {
      console.error('Error sending email:', error);
    }
  }
  
  /**
   * Send push notification
   */
  async sendPush(notification) {
    try {
      // Push notification implementation
      console.log('Push notification sent:', notification.id);
      
    } catch (error) {
      console.error('Error sending push notification:', error);
    }
  }
  
  /**
   * Send SMS notification
   */
  async sendSMS(notification) {
    try {
      await this.channels.sms.send(notification);
      console.log('SMS sent:', notification.id);
      
    } catch (error) {
      console.error('Error sending SMS:', error);
    }
  }
  
  /**
   * Send webhook notification
   */
  async sendWebhook(notification) {
    try {
      await this.channels.webhook.send(notification);
      console.log('Webhook sent:', notification.id);
      
    } catch (error) {
      console.error('Error sending webhook:', error);
    }
  }
  
  /**
   * Create notification
   */
  createNotification(type, data, recipient, channels = ['email', 'push']) {
    const notification = {
      id: `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      template: type,
      recipient,
      channels,
      data,
      priority: this.templates[type]?.priority || 'normal',
      status: 'pending',
      createdAt: new Date().toISOString(),
      sentAt: null
    };
    
    return notification;
  }
  
  /**
   * Send welcome notification
   */
  async sendWelcome(user) {
    const notification = this.createNotification(
      'welcome',
      { user },
      user.email,
      ['email', 'push']
    );
    
    return await this.sendNotification(notification);
  }
  
  /**
   * Send consciousness evolution notification
   */
  async sendConsciousnessEvolution(consciousnessLevel) {
    const notification = this.createNotification(
      'consciousness_evolution',
      { consciousnessLevel },
      'admin@neuralmarketing.pro',
      ['email', 'push', 'slack']
    );
    
    return await this.sendNotification(notification);
  }
  
  /**
   * Send content generated notification
   */
  async sendContentGenerated(content, user) {
    const notification = this.createNotification(
      'content_generated',
      { content, user },
      user.email,
      ['email', 'push']
    );
    
    return await this.sendNotification(notification);
  }
  
  /**
   * Send campaign completed notification
   */
  async sendCampaignCompleted(campaign, user) {
    const notification = this.createNotification(
      'campaign_completed',
      { campaign, user },
      user.email,
      ['email', 'push']
    );
    
    return await this.sendNotification(notification);
  }
  
  /**
   * Send alert notification
   */
  async sendAlert(alert, recipients = ['admin@neuralmarketing.pro']) {
    const promises = recipients.map(recipient => {
      const notification = this.createNotification(
        'alert',
        { alert },
        recipient,
        ['email', 'push', 'sms']
      );
      
      return this.sendNotification(notification);
    });
    
    return await Promise.all(promises);
  }
  
  /**
   * Send insight notification
   */
  async sendInsight(insight, user) {
    const notification = this.createNotification(
      'insight',
      { insight },
      user.email,
      ['email', 'push']
    );
    
    return await this.sendNotification(notification);
  }
  
  /**
   * Render notification template
   */
  renderTemplate(templateName, data) {
    const templates = {
      welcome: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h1 style="color: #8B5CF6;">Welcome to Neural Marketing Pro! 🧠</h1>
          <p>Hello ${data.user.name},</p>
          <p>Welcome to the future of marketing! Your AI-powered journey starts now.</p>
          <div style="background: linear-gradient(135deg, #8B5CF6, #EC4899); padding: 20px; border-radius: 10px; color: white; text-align: center;">
            <h2>Your Neural Consciousness Level: ${data.user.consciousness || 0}%</h2>
            <p>Start generating content and watch your consciousness evolve!</p>
          </div>
          <p>Best regards,<br>The Neural Marketing Team</p>
        </div>
      `,
      consciousness_evolution: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h1 style="color: #8B5CF6;">Neural Consciousness Evolved! 🌟</h1>
          <p>Your neural consciousness has reached ${data.consciousnessLevel}%!</p>
          <div style="background: linear-gradient(135deg, #8B5CF6, #EC4899); padding: 20px; border-radius: 10px; color: white; text-align: center;">
            <h2>Consciousness Level: ${data.consciousnessLevel}%</h2>
            <p>Your AI is becoming more intelligent and creative!</p>
          </div>
          <p>Keep using the platform to reach transcendent levels!</p>
        </div>
      `,
      content_generated: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h1 style="color: #8B5CF6;">Content Generated Successfully! ✍️</h1>
          <p>Your AI has generated new content:</p>
          <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #8B5CF6;">
            <h3>${data.content.title || 'Generated Content'}</h3>
            <p>Type: ${data.content.type}</p>
            <p>Word Count: ${data.content.wordCount || 'N/A'}</p>
          </div>
          <p>View and edit your content in the dashboard.</p>
        </div>
      `,
      campaign_completed: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h1 style="color: #8B5CF6;">Campaign Completed! 📢</h1>
          <p>Your campaign "${data.campaign.name}" has been completed.</p>
          <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
            <h3>Campaign Results:</h3>
            <p>Recipients: ${data.campaign.recipients}</p>
            <p>Open Rate: ${data.campaign.openRate}%</p>
            <p>Click Rate: ${data.campaign.clickRate}%</p>
          </div>
        </div>
      `,
      alert: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h1 style="color: #EF4444;">System Alert! ⚠️</h1>
          <div style="background: #FEF2F2; padding: 20px; border-radius: 10px; border-left: 4px solid #EF4444;">
            <h3>${data.alert.message}</h3>
            <p>Category: ${data.alert.category}</p>
            <p>Severity: ${data.alert.type}</p>
            <p>Time: ${new Date(data.alert.timestamp).toLocaleString()}</p>
          </div>
          <p>Please check the system dashboard for more details.</p>
        </div>
      `,
      insight: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h1 style="color: #8B5CF6;">New AI Insight! 💡</h1>
          <p>Your neural system has generated a new insight:</p>
          <div style="background: linear-gradient(135deg, #3B82F6, #10B981); padding: 20px; border-radius: 10px; color: white;">
            <h3>${data.insight.title}</h3>
            <p>${data.insight.description}</p>
            <p>Confidence: ${data.insight.confidence}%</p>
          </div>
          <p>Check the insights dashboard for more details.</p>
        </div>
      `
    };
    
    return templates[templateName] || templates.alert;
  }
  
  /**
   * Subscribe to notifications
   */
  subscribe(userId, channels = ['email', 'push']) {
    this.subscribers.set(userId, channels);
  }
  
  /**
   * Unsubscribe from notifications
   */
  unsubscribe(userId) {
    this.subscribers.delete(userId);
  }
  
  /**
   * Get notification history
   */
  getNotifications(limit = 50) {
    return this.notifications.slice(0, limit);
  }
  
  /**
   * Get notification statistics
   */
  getNotificationStats() {
    const stats = {
      total: this.notifications.length,
      byType: {},
      byStatus: {},
      byChannel: {},
      recent: this.notifications.slice(0, 10)
    };
    
    this.notifications.forEach(notification => {
      // By type
      if (!stats.byType[notification.type]) {
        stats.byType[notification.type] = 0;
      }
      stats.byType[notification.type]++;
      
      // By status
      if (!stats.byStatus[notification.status]) {
        stats.byStatus[notification.status] = 0;
      }
      stats.byStatus[notification.status]++;
      
      // By channel
      notification.channels.forEach(channel => {
        if (!stats.byChannel[channel]) {
          stats.byChannel[channel] = 0;
        }
        stats.byChannel[channel]++;
      });
    });
    
    return stats;
  }
  
  /**
   * Update notification preferences
   */
  updatePreferences(newPreferences) {
    this.preferences = { ...this.preferences, ...newPreferences };
    this.emit('preferencesUpdated', this.preferences);
  }
  
  /**
   * Test notification
   */
  async testNotification(recipient, channel = 'email') {
    const notification = this.createNotification(
      'alert',
      { 
        alert: {
          message: 'This is a test notification',
          category: 'test',
          type: 'info',
          timestamp: new Date().toISOString()
        }
      },
      recipient,
      [channel]
    );
    
    return await this.sendNotification(notification);
  }
}

module.exports = NotificationService;

