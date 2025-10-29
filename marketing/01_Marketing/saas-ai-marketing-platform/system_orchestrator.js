#!/usr/bin/env node

/**
 * System Orchestrator
 * Main orchestration system for autonomous operation of the AI Marketing SaaS Platform
 * This system manages all automated workflows, maintenance, and monitoring
 */

const cron = require('node-cron');
const EventEmitter = require('events');
const fs = require('fs');
const path = require('path');
const axios = require('axios');

class SystemOrchestrator extends EventEmitter {
  constructor() {
    super();
    
    this.isRunning = false;
    this.healthCheckInterval = null;
    this.services = {
      database: false,
      redis: false,
      api: false,
      automation: false
    };
    
    this.metrics = {
      uptime: 0,
      requestsProcessed: 0,
      errorsCount: 0,
      lastHealthCheck: null,
      servicesStatus: {}
    };
    
    this.maintenanceTasks = [];
    
    console.log('🚀 System Orchestrator initialized');
  }

  /**
   * Start the orchestrator
   */
  async start() {
    if (this.isRunning) {
      console.log('⚠️  Orchestrator is already running');
      return;
    }

    console.log('🎯 Starting System Orchestrator...');
    this.isRunning = true;

    try {
      // Initialize all services
      await this.initializeServices();
      
      // Start health monitoring
      this.startHealthMonitoring();
      
      // Start scheduled tasks
      this.startScheduledTasks();
      
      // Start automated maintenance
      this.startAutomatedMaintenance();
      
      // Start content generation automation
      this.startContentAutomation();
      
      // Start cleanup tasks
      this.startCleanupTasks();
      
      console.log('✅ System Orchestrator started successfully');
      this.emit('started');
    } catch (error) {
      console.error('❌ Error starting orchestrator:', error);
      this.isRunning = false;
      this.emit('error', error);
    }
  }

  /**
   * Initialize all services
   */
  async initializeServices() {
    console.log('🔧 Initializing services...');
    
    // Check database connection
    await this.checkDatabase();
    
    // Check Redis connection
    await this.checkRedis();
    
    // Check API status
    await this.checkAPI();
    
    console.log('✅ Services initialized');
  }

  /**
   * Check database connection
   */
  async checkDatabase() {
    try {
      const { dbManager } = require('./config/db');
      const status = await dbManager.healthCheck();
      
      this.services.database = status.status === 'healthy';
      this.emit('service-status', { service: 'database', status: this.services.database });
      
      if (this.services.database) {
        console.log('✅ Database is healthy');
      } else {
        console.log('⚠️  Database connection issues detected');
      }
    } catch (error) {
      console.error('❌ Database check failed:', error.message);
      this.services.database = false;
    }
  }

  /**
   * Check Redis connection
   */
  async checkRedis() {
    try {
      const redis = require('redis');
      const client = redis.createClient({ url: process.env.REDIS_URL });
      
      await client.connect();
      await client.ping();
      
      this.services.redis = true;
      console.log('✅ Redis is healthy');
      
      client.quit();
    } catch (error) {
      console.error('⚠️  Redis check failed:', error.message);
      this.services.redis = false;
    }
  }

  /**
   * Check API status
   */
  async checkAPI() {
    try {
      const response = await axios.get('http://localhost:5000/api/health', { timeout: 3000 });
      
      this.services.api = response.data.status === 'OK';
      this.emit('service-status', { service: 'api', status: this.services.api });
      
      if (this.services.api) {
        console.log('✅ API is healthy');
      }
    } catch (error) {
      console.error('⚠️  API check failed:', error.message);
      this.services.api = false;
    }
  }

  /**
   * Start health monitoring
   */
  startHealthMonitoring() {
    // Run health check every 30 seconds
    setInterval(async () => {
      await this.runHealthChecks();
    }, 30000);
    
    console.log('📊 Health monitoring started');
  }

  /**
   * Run comprehensive health checks
   */
  async runHealthChecks() {
    const healthStatus = {
      timestamp: new Date().toISOString(),
      services: {},
      overall: true
    };
    
    // Check database
    await this.checkDatabase();
    healthStatus.services.database = this.services.database;
    
    // Check Redis
    await this.checkRedis();
    healthStatus.services.redis = this.services.redis;
    
    // Check API
    await this.checkAPI();
    healthStatus.services.api = this.services.api;
    
    // Calculate overall status
    healthStatus.overall = Object.values(this.services).every(status => status === true);
    
    // Update metrics
    this.metrics.lastHealthCheck = new Date();
    this.metrics.servicesStatus = healthStatus.services;
    
    this.emit('health-check', healthStatus);
    
    if (!healthStatus.overall) {
      console.warn('⚠️  Health check failed for:', 
        Object.entries(healthStatus.services)
          .filter(([_, status]) => !status)
          .map(([service]) => service)
          .join(', ')
      );
    }
  }

  /**
   * Start scheduled tasks
   */
  startScheduledTasks() {
    // Daily analytics summary at 9 AM
    cron.schedule('0 9 * * *', async () => {
      console.log('📊 Running daily analytics summary...');
      await this.sendDailyAnalyticsSummary();
    });
    
    // Weekly performance report every Monday at 9 AM
    cron.schedule('0 9 * * 1', async () => {
      console.log('📈 Running weekly performance report...');
      await this.sendWeeklyPerformanceReport();
    });
    
    // Monthly usage reset on the 1st at midnight
    cron.schedule('0 0 1 * *', async () => {
      console.log('🔄 Running monthly usage reset...');
      await this.resetMonthlyUsage();
    });
    
    // Content generation automation (every 6 hours)
    cron.schedule('0 */6 * * *', async () => {
      console.log('🤖 Running automated content generation...');
      await this.runAutomatedContentGeneration();
    });
    
    // Database backup (daily at 2 AM)
    cron.schedule('0 2 * * *', async () => {
      console.log('💾 Running database backup...');
      await this.backupDatabase();
    });
    
    console.log('⏰ Scheduled tasks started');
  }

  /**
   * Start automated maintenance
   */
  startAutomatedMaintenance() {
    // Clean old logs every day at 3 AM
    cron.schedule('0 3 * * *', async () => {
      await this.cleanOldLogs();
    });
    
    // Optimize database weekly on Sunday at 4 AM
    cron.schedule('0 4 * * 0', async () => {
      await this.optimizeDatabase();
    });
    
    // Clear expired sessions daily at 1 AM
    cron.schedule('0 1 * * *', async () => {
      await this.clearExpiredSessions();
    });
    
    console.log('🔧 Automated maintenance started');
  }

  /**
   * Start content automation
   */
  startContentAutomation() {
    // Monitor and process content generation queue every 5 minutes
    cron.schedule('*/5 * * * *', async () => {
      await this.processContentQueue();
    });
    
    console.log('🤖 Content automation started');
  }

  /**
   * Start cleanup tasks
   */
  startCleanupTasks() {
    // Clean temporary files every 30 minutes
    cron.schedule('*/30 * * * *', async () => {
      await this.cleanTemporaryFiles();
    });
    
    console.log('🧹 Cleanup tasks started');
  }

  /**
   * Send daily analytics summary
   */
  async sendDailyAnalyticsSummary() {
    try {
      console.log('📧 Sending daily analytics summary...');
      // Implementation would send emails to users
      this.emit('daily-analytics', { success: true });
    } catch (error) {
      console.error('❌ Error sending daily analytics:', error);
      this.emit('error', error);
    }
  }

  /**
   * Send weekly performance report
   */
  async sendWeeklyPerformanceReport() {
    try {
      console.log('📈 Generating weekly performance report...');
      // Implementation would generate and send reports
      this.emit('weekly-report', { success: true });
    } catch (error) {
      console.error('❌ Error sending weekly report:', error);
      this.emit('error', error);
    }
  }

  /**
   * Reset monthly usage
   */
  async resetMonthlyUsage() {
    try {
      console.log('🔄 Resetting monthly usage...');
      // Implementation would reset user usage counters
      this.emit('monthly-reset', { success: true });
    } catch (error) {
      console.error('❌ Error resetting monthly usage:', error);
      this.emit('error', error);
    }
  }

  /**
   * Run automated content generation
   */
  async runAutomatedContentGeneration() {
    try {
      console.log('🤖 Running automated content generation...');
      // Implementation would trigger content generation for scheduled campaigns
      this.emit('content-generation', { success: true });
    } catch (error) {
      console.error('❌ Error in automated content generation:', error);
      this.emit('error', error);
    }
  }

  /**
   * Backup database
   */
  async backupDatabase() {
    try {
      console.log('💾 Backing up database...');
      // Implementation would backup database
      this.emit('database-backup', { success: true });
    } catch (error) {
      console.error('❌ Error backing up database:', error);
      this.emit('error', error);
    }
  }

  /**
   * Clean old logs
   */
  async cleanOldLogs() {
    try {
      console.log('🧹 Cleaning old logs...');
      const logsDir = path.join(__dirname, 'logs');
      if (fs.existsSync(logsDir)) {
        const files = fs.readdirSync(logsDir);
        const now = Date.now();
        const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days
        
        for (const file of files) {
          const filePath = path.join(logsDir, file);
          const stats = fs.statSync(filePath);
          
          if (now - stats.mtime.getTime() > maxAge) {
            fs.unlinkSync(filePath);
            console.log(`Deleted old log: ${file}`);
          }
        }
      }
      this.emit('logs-cleaned', { success: true });
    } catch (error) {
      console.error('❌ Error cleaning logs:', error);
      this.emit('error', error);
    }
  }

  /**
   * Optimize database
   */
  async optimizeDatabase() {
    try {
      console.log('⚡ Optimizing database...');
      // Implementation would optimize database
      this.emit('database-optimized', { success: true });
    } catch (error) {
      console.error('❌ Error optimizing database:', error);
      this.emit('error', error);
    }
  }

  /**
   * Clear expired sessions
   */
  async clearExpiredSessions() {
    try {
      console.log('🔑 Clearing expired sessions...');
      // Implementation would clear expired sessions from Redis
      this.emit('sessions-cleared', { success: true });
    } catch (error) {
      console.error('❌ Error clearing sessions:', error);
      this.emit('error', error);
    }
  }

  /**
   * Process content queue
   */
  async processContentQueue() {
    try {
      // Implementation would process queued content generation tasks
      this.emit('queue-processed', { success: true });
    } catch (error) {
      console.error('❌ Error processing queue:', error);
      this.emit('error', error);
    }
  }

  /**
   * Clean temporary files
   */
  async cleanTemporaryFiles() {
    try {
      console.log('🗑️  Cleaning temporary files...');
      // Implementation would clean temporary files
      this.emit('temp-files-cleaned', { success: true });
    } catch (error) {
      console.error('❌ Error cleaning temp files:', error);
      this.emit('error', error);
    }
  }

  /**
   * Stop the orchestrator
   */
  async stop() {
    console.log('🛑 Stopping System Orchestrator...');
    this.isRunning = false;
    
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
    
    console.log('✅ System Orchestrator stopped');
    this.emit('stopped');
  }

  /**
   * Get system status
   */
  getStatus() {
    return {
      isRunning: this.isRunning,
      services: this.services,
      metrics: this.metrics,
      timestamp: new Date().toISOString()
    };
  }
}

// Export singleton instance
const orchestrator = new SystemOrchestrator();

// Start orchestrator if running directly
if (require.main === module) {
  orchestrator.start().catch(error => {
    console.error('Failed to start orchestrator:', error);
    process.exit(1);
  });
  
  // Graceful shutdown
  process.on('SIGTERM', () => {
    console.log('SIGTERM received, stopping orchestrator...');
    orchestrator.stop().then(() => process.exit(0));
  });
  
  process.on('SIGINT', () => {
    console.log('SIGINT received, stopping orchestrator...');
    orchestrator.stop().then(() => process.exit(0));
  });
}

module.exports = orchestrator;



