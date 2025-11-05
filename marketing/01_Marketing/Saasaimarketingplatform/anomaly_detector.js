#!/usr/bin/env node

/**
 * Anomaly Detection System
 * AI-powered system to detect and alert on system anomalies
 */

const EventEmitter = require('events');

class AnomalyDetector extends EventEmitter {
  constructor() {
    super();
    
    this.baselines = {
      responseTime: [],
      errorRate: [],
      cpuUsage: [],
      memoryUsage: [],
      requestCount: []
    };
    
    this.thresholds = {
      responseTime: { upper: 2, lower: 0.1 },
      errorRate: { upper: 0.05, lower: 0 },
      cpuUsage: { upper: 0.9, lower: 0.1 },
      memoryUsage: { upper: 0.9, lower: 0.1 },
      requestCount: { upper: 1000, lower: 0 }
    };
    
    this.alertLevels = {
      info: 'blue',
      warning: 'yellow',
      critical: 'red'
    };
    
    console.log('🔍 Anomaly Detector initialized');
  }

  /**
   * Start monitoring for anomalies
   */
  startMonitoring() {
    setInterval(() => {
      this.collectMetrics();
    }, 15000); // Collect metrics every 15 seconds
    
    console.log('📊 Anomaly monitoring started');
  }

  /**
   * Collect metrics from various sources
   */
  async collectMetrics() {
    const metrics = {
      timestamp: new Date(),
      responseTime: await this.getResponseTime(),
      errorRate: await this.getErrorRate(),
      cpuUsage: await this.getCpuUsage(),
      memoryUsage: await this.getMemoryUsage(),
      requestCount: await this.getRequestCount()
    };
    
    // Detect anomalies
    for (const [metric, value] of Object.entries(metrics)) {
      if (metric === 'timestamp') continue;
      
      const anomaly = this.detectAnomaly(metric, value);
      
      if (anomaly.detected) {
        console.log(`⚠️  Anomaly detected in ${metric}:`, anomaly);
        this.emit('anomaly-detected', { metric, value, anomaly });
      }
    }
    
    // Update baselines
    this.updateBaselines(metrics);
  }

  /**
   * Detect anomaly in specific metric
   */
  detectAnomaly(metric, value) {
    const baseline = this.baselines[metric] || [];
    const threshold = this.thresholds[metric];
    
    if (baseline.length < 10) {
      return { detected: false, reason: 'insufficient_data' };
    }
    
    const mean = baseline.reduce((a, b) => a + b, 0) / baseline.length;
    const variance = baseline.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / baseline.length;
    const stdDev = Math.sqrt(variance);
    
    const zScore = (value - mean) / stdDev;
    
    // Detect if value is outside normal range
    const isAnomalous = Math.abs(zScore) > 2;
    
    // Check threshold bounds
    const isOutOfBounds = threshold && (value > threshold.upper || value < threshold.lower);
    
    if (isAnomalous || isOutOfBounds) {
      return {
        detected: true,
        type: isOutOfBounds ? 'threshold' : 'statistical',
        severity: this.calculateSeverity(zScore, isOutOfBounds, value, threshold),
        zScore,
        value,
        expected: { mean, stdDev }
      };
    }
    
    return { detected: false };
  }

  /**
   * Calculate severity of anomaly
   */
  calculateSeverity(zScore, isOutOfBounds, value, threshold) {
    if (isOutOfBounds) {
      return 'critical';
    }
    
    const absZScore = Math.abs(zScore);
    
    if (absZScore > 3) {
      return 'critical';
    } else if (absZScore > 2.5) {
      return 'warning';
    } else {
      return 'info';
    }
  }

  /**
   * Get response time metric
   */
  async getResponseTime() {
    try {
      const axios = require('axios');
      const start = Date.now();
      await axios.get('http://localhost:5000/api/health', { timeout: 5000 });
      return (Date.now() - start) / 1000; // Return in seconds
    } catch (error) {
      return -1; // Error
    }
  }

  /**
   * Get error rate
   */
  async getErrorRate() {
    // This would normally come from logs or metrics
    return Math.random() * 0.1; // Placeholder
  }

  /**
   * Get CPU usage
   */
  async getCpuUsage() {
    try {
      const { exec } = require('child_process');
      const util = require('util');
      const execPromise = util.promisify(exec);
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
      const { exec } = require('child_process');
      const util = require('util');
      const execPromise = util.promisify(exec);
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
   * Get request count
   */
  async getRequestCount() {
    // This would normally come from metrics endpoint
    return Math.floor(Math.random() * 100); // Placeholder
  }

  /**
   * Update baselines
   */
  updateBaselines(metrics) {
    for (const [metric, value] of Object.entries(metrics)) {
      if (metric === 'timestamp') continue;
      
      if (!this.baselines[metric]) {
        this.baselines[metric] = [];
      }
      
      this.baselines[metric].push(value);
      
      // Keep only last 100 values
      if (this.baselines[metric].length > 100) {
        this.baselines[metric].shift();
      }
    }
  }

  /**
   * Get anomaly statistics
   */
  getAnomalyStats() {
    const stats = {};
    
    for (const metric in this.baselines) {
      const values = this.baselines[metric];
      if (values.length > 0) {
        const mean = values.reduce((a, b) => a + b, 0) / values.length;
        const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
        const stdDev = Math.sqrt(variance);
        
        stats[metric] = {
          mean,
          stdDev,
          min: Math.min(...values),
          max: Math.max(...values),
          recent: values.slice(-10)
        };
      }
    }
    
    return stats;
  }
}

module.exports = AnomalyDetector;



