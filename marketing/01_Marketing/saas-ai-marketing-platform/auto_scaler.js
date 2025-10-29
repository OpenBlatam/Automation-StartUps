#!/usr/bin/env node

/**
 * Auto-Scaler System
 * Automatically scales system resources based on demand
 */

const EventEmitter = require('events');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

class AutoScaler extends EventEmitter {
  constructor() {
    super();
    
    this.scalingRules = [];
    this.currentInstances = 1;
    this.minInstances = 1;
    this.maxInstances = 10;
    this.scaleUpThreshold = 0.8;
    this.scaleDownThreshold = 0.3;
    
    this.metricsWindow = [];
    this.metricsWindowSize = 10;
    
    this.setupScalingRules();
    
    console.log('⚖️  Auto-Scaler initialized');
  }

  /**
   * Setup scaling rules
   */
  setupScalingRules() {
    // CPU-based scaling
    this.scalingRules.push({
      name: 'cpu_scaling',
      metric: 'cpu',
      scaleUp: 0.8,
      scaleDown: 0.3,
      cooldown: 60 // seconds
    });
    
    // Memory-based scaling
    this.scalingRules.push({
      name: 'memory_scaling',
      metric: 'memory',
      scaleUp: 0.85,
      scaleDown: 0.4,
      cooldown: 60
    });
    
    // Request rate based scaling
    this.scalingRules.push({
      name: 'requests_scaling',
      metric: 'requests',
      scaleUp: 0.75,
      scaleDown: 0.25,
      cooldown: 120
    });
    
    // Response time based scaling
    this.scalingRules.push({
      name: 'response_time_scaling',
      metric: 'responseTime',
      scaleUp: 2.0, // seconds
      scaleDown: 0.5,
      cooldown: 90
    });
  }

  /**
   * Start auto-scaling
   */
  startScaling() {
    setInterval(() => {
      this.evaluateScaling();
    }, 30000); // Evaluate every 30 seconds
    
    console.log('📈 Auto-scaling started');
  }

  /**
   * Evaluate if scaling is needed
   */
  async evaluateScaling() {
    // Collect current metrics
    const metrics = await this.collectMetrics();
    
    // Add to metrics window
    this.metricsWindow.push({
      timestamp: new Date(),
      ...metrics
    });
    
    // Keep only recent metrics
    if (this.metricsWindow.length > this.metricsWindowSize) {
      this.metricsWindow.shift();
    }
    
    // Evaluate each scaling rule
    for (const rule of this.scalingRules) {
      await this.evaluateRule(rule, metrics);
    }
  }

  /**
   * Evaluate specific scaling rule
   */
  async evaluateRule(rule, metrics) {
    const metricValue = metrics[rule.metric];
    
    if (metricValue === undefined || metricValue === null) {
      return;
    }
    
    const shouldScaleUp = this.shouldScaleUp(rule, metricValue);
    const shouldScaleDown = this.shouldScaleDown(rule, metricValue);
    
    if (shouldScaleUp && this.currentInstances < this.maxInstances) {
      console.log(`📈 Scaling up due to ${rule.name}`);
      await this.scaleUp();
    } else if (shouldScaleDown && this.currentInstances > this.minInstances) {
      console.log(`📉 Scaling down due to ${rule.name}`);
      await this.scaleDown();
    }
  }

  /**
   * Check if should scale up
   */
  shouldScaleUp(rule, value) {
    // For metrics where higher is worse (CPU, memory, response time)
    if (rule.metric === 'cpu' || rule.metric === 'memory' || rule.metric === 'responseTime') {
      return value > rule.scaleUp;
    }
    
    // For metrics where higher is better (requests)
    return value > rule.scaleUp;
  }

  /**
   * Check if should scale down
   */
  shouldScaleDown(rule, value) {
    // For metrics where higher is worse
    if (rule.metric === 'cpu' || rule.metric === 'memory' || rule.metric === 'responseTime') {
      return value < rule.scaleDown;
    }
    
    // For metrics where higher is better
    return value < rule.scaleDown;
  }

  /**
   * Collect current metrics
   */
  async collectMetrics() {
    return {
      cpu: await this.getCpuUsage(),
      memory: await this.getMemoryUsage(),
      requests: await this.getRequestRate(),
      responseTime: await this.getResponseTime()
    };
  }

  /**
   * Get CPU usage
   */
  async getCpuUsage() {
    try {
      const { stdout } = await execPromise("top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/' | awk '{print 100 - $1}'");
      return parseFloat(stdout) / 100;
    } catch (error) {
      return 0;
    }
  }

  /**
   * Get memory usage
   */
  async getMemoryUsage() {
    try {
      const { stdout } = await execPromise('free -m');
      const lines = stdout.split('\n');
      const memLine = lines[1];
      const values = memLine.split(/\s+/);
      const used = parseFloat(values[2]);
      const total = parseFloat(values[1]);
      return used / total;
    } catch (error) {
      return 0;
    }
  }

  /**
   * Get request rate
   */
  async getRequestRate() {
    // This would normally come from metrics
    return Math.random() * 100;
  }

  /**
   * Get response time
   */
  async getResponseTime() {
    try {
      const axios = require('axios');
      const start = Date.now();
      await axios.get('http://localhost:5000/api/health', { timeout: 5000 });
      return (Date.now() - start) / 1000;
    } catch (error) {
      return 10; // Very slow
    }
  }

  /**
   * Scale up
   */
  async scaleUp() {
    try {
      console.log(`➕ Scaling up from ${this.currentInstances} to ${this.currentInstances + 1} instances`);
      
      // In production, this would actually scale services
      // For Docker Compose, we could use:
      // await execPromise(`docker-compose up -d --scale app=${this.currentInstances + 1}`);
      
      this.currentInstances++;
      
      this.emit('scaled-up', {
        instances: this.currentInstances,
        timestamp: new Date()
      });
      
      return { success: true, instances: this.currentInstances };
    } catch (error) {
      console.error('Error scaling up:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Scale down
   */
  async scaleDown() {
    try {
      console.log(`➖ Scaling down from ${this.currentInstances} to ${this.currentInstances - 1} instances`);
      
      // In production, this would actually scale services
      // await execPromise(`docker-compose up -d --scale app=${this.currentInstances - 1}`);
      
      this.currentInstances--;
      
      this.emit('scaled-down', {
        instances: this.currentInstances,
        timestamp: new Date()
      });
      
      return { success: true, instances: this.currentInstances };
    } catch (error) {
      console.error('Error scaling down:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Get scaling status
   */
  getStatus() {
    return {
      currentInstances: this.currentInstances,
      minInstances: this.minInstances,
      maxInstances: this.maxInstances,
      recentMetrics: this.metricsWindow.slice(-5)
    };
  }
}

module.exports = AutoScaler;



