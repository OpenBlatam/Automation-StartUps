#!/usr/bin/env node

/**
 * Auto-Recovery System
 * Automatically detects and recovers from system failures
 */

const EventEmitter = require('events');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

class AutoRecoverySystem extends EventEmitter {
  constructor() {
    super();
    
    this.recoveryStrategies = new Map();
    this.failureHistory = [];
    this.recoveryAttempts = new Map();
    this.maxRecoveryAttempts = 5;
    
    this.setupRecoveryStrategies();
    
    console.log('🔧 Auto-Recovery System initialized');
  }

  /**
   * Setup recovery strategies for different failure types
   */
  setupRecoveryStrategies() {
    // Database failures
    this.recoveryStrategies.set('database_down', {
      detect: this.detectDatabaseFailure.bind(this),
      recover: this.recoverDatabase.bind(this),
      priority: 'high'
    });
    
    // Redis failures
    this.recoveryStrategies.set('redis_down', {
      detect: this.detectRedisFailure.bind(this),
      recover: this.recoverRedis.bind(this),
      priority: 'high'
    });
    
    // API failures
    this.recoveryStrategies.set('api_down', {
      detect: this.detectAPIFailure.bind(this),
      recover: this.recoverAPI.bind(this),
      priority: 'critical'
    });
    
    // Memory issues
    this.recoveryStrategies.set('memory_high', {
      detect: this.detectMemoryIssues.bind(this),
      recover: this.recoverMemory.bind(this),
      priority: 'medium'
    });
    
    // Disk space issues
    this.recoveryStrategies.set('disk_full', {
      detect: this.detectDiskIssues.bind(this),
      recover: this.recoverDisk.bind(this),
      priority: 'high'
    });
  }

  /**
   * Start monitoring for failures
   */
  startMonitoring() {
    setInterval(() => {
      this.checkSystemHealth();
    }, 30000); // Check every 30 seconds
    
    console.log('🔍 Auto-recovery monitoring started');
  }

  /**
   * Check system health
   */
  async checkSystemHealth() {
    for (const [failureType, strategy] of this.recoveryStrategies) {
      try {
        const detected = await strategy.detect();
        
        if (detected) {
          console.log(`⚠️  ${failureType} detected`);
          await this.handleFailure(failureType, strategy);
        }
      } catch (error) {
        console.error(`Error checking ${failureType}:`, error.message);
      }
    }
  }

  /**
   * Handle detected failure
   */
  async handleFailure(failureType, strategy) {
    const attempts = this.recoveryAttempts.get(failureType) || 0;
    
    if (attempts >= this.maxRecoveryAttempts) {
      console.error(`❌ Max recovery attempts reached for ${failureType}`);
      this.emit('recovery-failed', { failureType, attempts });
      return;
    }
    
    // Record failure
    this.failureHistory.push({
      type: failureType,
      timestamp: new Date(),
      attempts: attempts + 1
    });
    
    this.recoveryAttempts.set(failureType, attempts + 1);
    
    try {
      console.log(`🔄 Attempting to recover from ${failureType}...`);
      const result = await strategy.recover();
      
      if (result.success) {
        console.log(`✅ Successfully recovered from ${failureType}`);
        this.recoveryAttempts.set(failureType, 0);
        this.emit('recovery-success', { failureType, result });
      } else {
        console.log(`⚠️  Recovery attempt failed for ${failureType}`);
        this.emit('recovery-attempt-failed', { failureType, reason: result.reason });
      }
    } catch (error) {
      console.error(`❌ Error during recovery of ${failureType}:`, error.message);
      this.emit('recovery-error', { failureType, error: error.message });
    }
  }

  /**
   * Detect database failure
   */
  async detectDatabaseFailure() {
    try {
      const { dbManager } = require('./config/db');
      const status = await dbManager.healthCheck();
      return status.status !== 'healthy';
    } catch (error) {
      return true; // Failure detected
    }
  }

  /**
   * Detect Redis failure
   */
  async detectRedisFailure() {
    try {
      const redis = require('redis');
      const client = redis.createClient({ url: process.env.REDIS_URL });
      await client.connect();
      await client.ping();
      await client.quit();
      return false;
    } catch (error) {
      return true;
    }
  }

  /**
   * Detect API failure
   */
  async detectAPIFailure() {
    try {
      const axios = require('axios');
      await axios.get('http://localhost:5000/api/health', { timeout: 5000 });
      return false;
    } catch (error) {
      return true;
    }
  }

  /**
   * Detect memory issues
   */
  async detectMemoryIssues() {
    try {
      const { stdout } = await execPromise('free -m');
      const lines = stdout.split('\n');
      const memLine = lines[1];
      const values = memLine.split(/\s+/);
      const used = parseInt(values[2]);
      const total = parseInt(values[1]);
      const percentUsed = (used / total) * 100;
      
      return percentUsed > 90; // Alert if more than 90% used
    } catch (error) {
      return false;
    }
  }

  /**
   * Detect disk issues
   */
  async detectDiskIssues() {
    try {
      const { stdout } = await execPromise('df -h /');
      const lines = stdout.split('\n');
      const rootLine = lines[1];
      const values = rootLine.split(/\s+/);
      const percentUsed = parseInt(values[4]);
      
      return percentUsed > 90;
    } catch (error) {
      return false;
    }
  }

  /**
   * Recover database
   */
  async recoverDatabase() {
    try {
      console.log('🔄 Attempting database restart...');
      await execPromise('docker-compose restart mongodb');
      
      // Wait for database to be ready
      await this.waitForService('mongodb', 30);
      
      return { success: true, action: 'database_restarted' };
    } catch (error) {
      return { success: false, reason: error.message };
    }
  }

  /**
   * Recover Redis
   */
  async recoverRedis() {
    try {
      console.log('🔄 Attempting Redis restart...');
      await execPromise('docker-compose restart redis');
      
      // Wait for Redis to be ready
      await this.waitForService('redis', 30);
      
      return { success: true, action: 'redis_restarted' };
    } catch (error) {
      return { success: false, reason: error.message };
    }
  }

  /**
   * Recover API
   */
  async recoverAPI() {
    try {
      console.log('🔄 Attempting API restart...');
      await execPromise('docker-compose restart app');
      
      // Wait for API to be ready
      await this.waitForAPI(30);
      
      return { success: true, action: 'api_restarted' };
    } catch (error) {
      return { success: false, reason: error.message };
    }
  }

  /**
   * Recover memory issues
   */
  async recoverMemory() {
    try {
      console.log('🔄 Attempting memory cleanup...');
      
      // Clear cache
      await execPromise('sync && echo 3 > /proc/sys/vm/drop_caches');
      
      // Restart app
      await execPromise('docker-compose restart app');
      
      return { success: true, action: 'memory_cleared' };
    } catch (error) {
      return { success: false, reason: error.message };
    }
  }

  /**
   * Recover disk issues
   */
  async recoverDisk() {
    try {
      console.log('🔄 Attempting disk cleanup...');
      
      // Clean old logs
      await execPromise('find logs -name "*.log" -mtime +7 -delete');
      
      // Clean old uploads
      await execPromise('find uploads -name "*" -mtime +30 -delete');
      
      return { success: true, action: 'disk_cleaned' };
    } catch (error) {
      return { success: false, reason: error.message };
    }
  }

  /**
   * Wait for service to be ready
   */
  async waitForService(serviceName, maxAttempts = 30) {
    for (let i = 0; i < maxAttempts; i++) {
      try {
        await execPromise(`docker-compose exec -T ${serviceName} echo "OK"`);
        return true;
      } catch (error) {
        if (i === maxAttempts - 1) {
          throw new Error(`Service ${serviceName} did not become ready`);
        }
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
  }

  /**
   * Wait for API to be ready
   */
  async waitForAPI(maxAttempts = 30) {
    for (let i = 0; i < maxAttempts; i++) {
      try {
        const axios = require('axios');
        await axios.get('http://localhost:5000/api/health', { timeout: 5000 });
        return true;
      } catch (error) {
        if (i === maxAttempts - 1) {
          throw new Error('API did not become ready');
        }
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
  }

  /**
   * Get failure history
   */
  getFailureHistory() {
    return this.failureHistory;
  }

  /**
   * Get recovery statistics
   */
  getRecoveryStats() {
    const stats = {};
    
    for (const [type, attempts] of this.recoveryAttempts) {
      stats[type] = {
        attempts,
        maxAttempts: this.maxRecoveryAttempts,
        successRate: attempts === 0 ? 100 : (this.maxRecoveryAttempts - attempts) / this.maxRecoveryAttempts * 100
      };
    }
    
    return stats;
  }
}

module.exports = AutoRecoverySystem;



