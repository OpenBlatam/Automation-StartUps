const os = require('os');
const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const exec = promisify(require('child_process').exec);

class PerformanceService {
  constructor() {
    this.metrics = {
      system: {},
      application: {},
      database: {},
      cache: {},
      external: {}
    };
    this.thresholds = {
      cpu: 80,
      memory: 85,
      disk: 90,
      responseTime: 2000,
      errorRate: 5,
      throughput: 1000
    };
    this.alerts = [];
    this.isMonitoring = false;
    this.monitoringInterval = null;
  }

  /**
   * Start performance monitoring
   */
  startMonitoring(intervalMs = 30000) {
    if (this.isMonitoring) {
      console.log('Performance monitoring is already running');
      return;
    }

    this.isMonitoring = true;
    this.monitoringInterval = setInterval(async () => {
      await this.collectMetrics();
      await this.checkThresholds();
      await this.generateAlerts();
    }, intervalMs);

    console.log(`Performance monitoring started with ${intervalMs}ms interval`);
  }

  /**
   * Stop performance monitoring
   */
  stopMonitoring() {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
    this.isMonitoring = false;
    console.log('Performance monitoring stopped');
  }

  /**
   * Collect all performance metrics
   */
  async collectMetrics() {
    try {
      await Promise.all([
        this.collectSystemMetrics(),
        this.collectApplicationMetrics(),
        this.collectDatabaseMetrics(),
        this.collectCacheMetrics(),
        this.collectExternalMetrics()
      ]);
    } catch (error) {
      console.error('Error collecting metrics:', error);
    }
  }

  /**
   * Collect system metrics
   */
  async collectSystemMetrics() {
    const cpus = os.cpus();
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const usedMem = totalMem - freeMem;

    this.metrics.system = {
      timestamp: new Date().toISOString(),
      cpu: {
        usage: await this.getCPUUsage(),
        cores: cpus.length,
        model: cpus[0].model,
        speed: cpus[0].speed
      },
      memory: {
        total: totalMem,
        used: usedMem,
        free: freeMem,
        usage: (usedMem / totalMem) * 100
      },
      disk: await this.getDiskUsage(),
      network: await this.getNetworkStats(),
      uptime: os.uptime(),
      loadAverage: os.loadavg(),
      platform: os.platform(),
      arch: os.arch(),
      nodeVersion: process.version
    };
  }

  /**
   * Collect application metrics
   */
  async collectApplicationMetrics() {
    const memUsage = process.memoryUsage();
    const cpuUsage = process.cpuUsage();

    this.metrics.application = {
      timestamp: new Date().toISOString(),
      memory: {
        rss: memUsage.rss,
        heapTotal: memUsage.heapTotal,
        heapUsed: memUsage.heapUsed,
        external: memUsage.external,
        arrayBuffers: memUsage.arrayBuffers
      },
      cpu: {
        user: cpuUsage.user,
        system: cpuUsage.system
      },
      uptime: process.uptime(),
      pid: process.pid,
      version: process.version,
      platform: process.platform,
      arch: process.arch,
      nodeEnv: process.env.NODE_ENV,
      activeHandles: process._getActiveHandles().length,
      activeRequests: process._getActiveRequests().length
    };
  }

  /**
   * Collect database metrics
   */
  async collectDatabaseMetrics() {
    try {
      // This would integrate with your database monitoring
      this.metrics.database = {
        timestamp: new Date().toISOString(),
        connections: {
          active: 0,
          idle: 0,
          total: 0
        },
        queries: {
          total: 0,
          slow: 0,
          errors: 0
        },
        performance: {
          averageQueryTime: 0,
          slowestQuery: null,
          cacheHitRate: 0
        }
      };
    } catch (error) {
      console.error('Error collecting database metrics:', error);
    }
  }

  /**
   * Collect cache metrics
   */
  async collectCacheMetrics() {
    try {
      // This would integrate with Redis or your cache system
      this.metrics.cache = {
        timestamp: new Date().toISOString(),
        redis: {
          connected: false,
          memory: 0,
          keys: 0,
          hitRate: 0,
          missRate: 0
        },
        local: {
          size: 0,
          hitRate: 0,
          missRate: 0
        }
      };
    } catch (error) {
      console.error('Error collecting cache metrics:', error);
    }
  }

  /**
   * Collect external service metrics
   */
  async collectExternalMetrics() {
    try {
      this.metrics.external = {
        timestamp: new Date().toISOString(),
        openai: {
          status: 'unknown',
          responseTime: 0,
          errorRate: 0,
          quotaUsed: 0,
          quotaLimit: 0
        },
        stripe: {
          status: 'unknown',
          responseTime: 0,
          errorRate: 0
        },
        email: {
          status: 'unknown',
          responseTime: 0,
          errorRate: 0,
          queueSize: 0
        }
      };
    } catch (error) {
      console.error('Error collecting external metrics:', error);
    }
  }

  /**
   * Get CPU usage
   */
  async getCPUUsage() {
    return new Promise((resolve) => {
      const startMeasure = process.cpuUsage();
      setTimeout(() => {
        const endMeasure = process.cpuUsage(startMeasure);
        const totalUsage = (endMeasure.user + endMeasure.system) / 1000000; // Convert to seconds
        const percentage = (totalUsage / 1) * 100; // 1 second interval
        resolve(Math.min(100, percentage));
      }, 1000);
    });
  }

  /**
   * Get disk usage
   */
  async getDiskUsage() {
    try {
      const { stdout } = await exec('df -h /');
      const lines = stdout.trim().split('\n');
      const data = lines[1].split(/\s+/);
      
      return {
        total: data[1],
        used: data[2],
        available: data[3],
        usage: parseFloat(data[4].replace('%', ''))
      };
    } catch (error) {
      return {
        total: 'Unknown',
        used: 'Unknown',
        available: 'Unknown',
        usage: 0
      };
    }
  }

  /**
   * Get network statistics
   */
  async getNetworkStats() {
    try {
      const { stdout } = await exec('netstat -i');
      const lines = stdout.trim().split('\n');
      const data = lines[1].split(/\s+/);
      
      return {
        interface: data[0],
        mtu: data[1],
        rxBytes: data[2],
        rxPackets: data[3],
        rxErrors: data[4],
        txBytes: data[6],
        txPackets: data[7],
        txErrors: data[8]
      };
    } catch (error) {
      return {
        interface: 'Unknown',
        mtu: 0,
        rxBytes: 0,
        rxPackets: 0,
        rxErrors: 0,
        txBytes: 0,
        txPackets: 0,
        txErrors: 0
      };
    }
  }

  /**
   * Check performance thresholds
   */
  async checkThresholds() {
    const alerts = [];

    // Check CPU usage
    if (this.metrics.system.cpu.usage > this.thresholds.cpu) {
      alerts.push({
        type: 'cpu_high',
        severity: 'warning',
        message: `CPU usage is ${this.metrics.system.cpu.usage.toFixed(2)}% (threshold: ${this.thresholds.cpu}%)`,
        value: this.metrics.system.cpu.usage,
        threshold: this.thresholds.cpu,
        timestamp: new Date().toISOString()
      });
    }

    // Check memory usage
    if (this.metrics.system.memory.usage > this.thresholds.memory) {
      alerts.push({
        type: 'memory_high',
        severity: 'warning',
        message: `Memory usage is ${this.metrics.system.memory.usage.toFixed(2)}% (threshold: ${this.thresholds.memory}%)`,
        value: this.metrics.system.memory.usage,
        threshold: this.thresholds.memory,
        timestamp: new Date().toISOString()
      });
    }

    // Check disk usage
    if (this.metrics.system.disk.usage > this.thresholds.disk) {
      alerts.push({
        type: 'disk_high',
        severity: 'critical',
        message: `Disk usage is ${this.metrics.system.disk.usage}% (threshold: ${this.thresholds.disk}%)`,
        value: this.metrics.system.disk.usage,
        threshold: this.thresholds.disk,
        timestamp: new Date().toISOString()
      });
    }

    // Check application memory
    const heapUsage = (this.metrics.application.memory.heapUsed / this.metrics.application.memory.heapTotal) * 100;
    if (heapUsage > this.thresholds.memory) {
      alerts.push({
        type: 'heap_high',
        severity: 'warning',
        message: `Heap usage is ${heapUsage.toFixed(2)}% (threshold: ${this.thresholds.memory}%)`,
        value: heapUsage,
        threshold: this.thresholds.memory,
        timestamp: new Date().toISOString()
      });
    }

    this.alerts = alerts;
  }

  /**
   * Generate performance alerts
   */
  async generateAlerts() {
    for (const alert of this.alerts) {
      await this.sendAlert(alert);
    }
  }

  /**
   * Send performance alert
   */
  async sendAlert(alert) {
    console.log(`Performance Alert [${alert.severity.toUpperCase()}]: ${alert.message}`);
    
    // This would integrate with your notification system
    // await notificationService.sendNotification('admin', {
    //   type: 'performance_alert',
    //   title: 'Performance Alert',
    //   message: alert.message,
    //   data: alert
    // });
  }

  /**
   * Get performance summary
   */
  getPerformanceSummary() {
    return {
      system: {
        cpu: this.metrics.system.cpu?.usage || 0,
        memory: this.metrics.system.memory?.usage || 0,
        disk: this.metrics.system.disk?.usage || 0,
        uptime: this.metrics.system.uptime || 0
      },
      application: {
        memory: this.metrics.application.memory ? 
          (this.metrics.application.memory.heapUsed / this.metrics.application.memory.heapTotal) * 100 : 0,
        uptime: this.metrics.application.uptime || 0,
        activeHandles: this.metrics.application.activeHandles || 0,
        activeRequests: this.metrics.application.activeRequests || 0
      },
      alerts: this.alerts.length,
      status: this.getOverallStatus()
    };
  }

  /**
   * Get overall system status
   */
  getOverallStatus() {
    const criticalAlerts = this.alerts.filter(alert => alert.severity === 'critical');
    const warningAlerts = this.alerts.filter(alert => alert.severity === 'warning');

    if (criticalAlerts.length > 0) {
      return 'critical';
    } else if (warningAlerts.length > 0) {
      return 'warning';
    } else {
      return 'healthy';
    }
  }

  /**
   * Get detailed metrics
   */
  getDetailedMetrics() {
    return this.metrics;
  }

  /**
   * Get performance trends
   */
  getPerformanceTrends(timeRange = '1h') {
    // This would return historical performance data
    return {
      cpu: [],
      memory: [],
      disk: [],
      responseTime: [],
      errorRate: []
    };
  }

  /**
   * Optimize performance
   */
  async optimizePerformance() {
    const optimizations = [];

    // Check if garbage collection is needed
    if (this.metrics.application.memory) {
      const heapUsage = (this.metrics.application.memory.heapUsed / this.metrics.application.memory.heapTotal) * 100;
      if (heapUsage > 80) {
        optimizations.push({
          type: 'garbage_collection',
          description: 'Trigger garbage collection to free up memory',
          impact: 'high'
        });
      }
    }

    // Check if cache cleanup is needed
    if (this.metrics.cache.redis && this.metrics.cache.redis.memory > 1000000000) { // 1GB
      optimizations.push({
        type: 'cache_cleanup',
        description: 'Clean up Redis cache to free up memory',
        impact: 'medium'
      });
    }

    // Check if log rotation is needed
    optimizations.push({
      type: 'log_rotation',
      description: 'Rotate log files to free up disk space',
      impact: 'low'
    });

    return optimizations;
  }

  /**
   * Execute performance optimization
   */
  async executeOptimization(optimization) {
    switch (optimization.type) {
      case 'garbage_collection':
        if (global.gc) {
          global.gc();
          console.log('Garbage collection executed');
        }
        break;
      case 'cache_cleanup':
        // This would clean up Redis cache
        console.log('Cache cleanup executed');
        break;
      case 'log_rotation':
        // This would rotate log files
        console.log('Log rotation executed');
        break;
    }
  }

  /**
   * Set performance thresholds
   */
  setThresholds(thresholds) {
    this.thresholds = { ...this.thresholds, ...thresholds };
  }

  /**
   * Get performance thresholds
   */
  getThresholds() {
    return this.thresholds;
  }

  /**
   * Get active alerts
   */
  getActiveAlerts() {
    return this.alerts;
  }

  /**
   * Clear alerts
   */
  clearAlerts() {
    this.alerts = [];
  }

  /**
   * Get performance report
   */
  generatePerformanceReport() {
    const summary = this.getPerformanceSummary();
    const metrics = this.getDetailedMetrics();
    const trends = this.getPerformanceTrends();
    const optimizations = this.optimizePerformance();

    return {
      timestamp: new Date().toISOString(),
      summary,
      metrics,
      trends,
      optimizations,
      recommendations: this.generateRecommendations()
    };
  }

  /**
   * Generate performance recommendations
   */
  generateRecommendations() {
    const recommendations = [];

    // CPU recommendations
    if (this.metrics.system.cpu?.usage > 70) {
      recommendations.push({
        type: 'cpu',
        priority: 'high',
        message: 'Consider scaling horizontally or optimizing CPU-intensive operations',
        action: 'Add more CPU cores or optimize algorithms'
      });
    }

    // Memory recommendations
    if (this.metrics.system.memory?.usage > 80) {
      recommendations.push({
        type: 'memory',
        priority: 'high',
        message: 'Consider increasing memory or optimizing memory usage',
        action: 'Add more RAM or optimize memory allocation'
      });
    }

    // Disk recommendations
    if (this.metrics.system.disk?.usage > 85) {
      recommendations.push({
        type: 'disk',
        priority: 'critical',
        message: 'Disk space is running low, consider cleanup or expansion',
        action: 'Clean up logs, temporary files, or add more disk space'
      });
    }

    // Application recommendations
    if (this.metrics.application.activeHandles > 1000) {
      recommendations.push({
        type: 'application',
        priority: 'medium',
        message: 'High number of active handles detected',
        action: 'Review and optimize resource management'
      });
    }

    return recommendations;
  }

  /**
   * Export performance data
   */
  exportPerformanceData(format = 'json') {
    const data = this.generatePerformanceReport();
    
    switch (format) {
      case 'json':
        return JSON.stringify(data, null, 2);
      case 'csv':
        return this.convertToCSV(data);
      default:
        return data;
    }
  }

  /**
   * Convert data to CSV format
   */
  convertToCSV(data) {
    const headers = ['timestamp', 'metric', 'value', 'threshold', 'status'];
    const rows = [headers.join(',')];

    // Add system metrics
    if (data.metrics.system) {
      rows.push(`${data.timestamp},cpu_usage,${data.metrics.system.cpu?.usage || 0},${this.thresholds.cpu},${data.summary.status}`);
      rows.push(`${data.timestamp},memory_usage,${data.metrics.system.memory?.usage || 0},${this.thresholds.memory},${data.summary.status}`);
      rows.push(`${data.timestamp},disk_usage,${data.metrics.system.disk?.usage || 0},${this.thresholds.disk},${data.summary.status}`);
    }

    return rows.join('\n');
  }

  /**
   * Save performance data to file
   */
  async savePerformanceData(filename, format = 'json') {
    try {
      const data = this.exportPerformanceData(format);
      const filepath = path.join(process.cwd(), 'logs', filename);
      
      // Ensure logs directory exists
      const logsDir = path.dirname(filepath);
      if (!fs.existsSync(logsDir)) {
        fs.mkdirSync(logsDir, { recursive: true });
      }
      
      fs.writeFileSync(filepath, data);
      console.log(`Performance data saved to ${filepath}`);
    } catch (error) {
      console.error('Error saving performance data:', error);
    }
  }

  /**
   * Load performance data from file
   */
  async loadPerformanceData(filename) {
    try {
      const filepath = path.join(process.cwd(), 'logs', filename);
      const data = fs.readFileSync(filepath, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      console.error('Error loading performance data:', error);
      return null;
    }
  }

  /**
   * Get performance comparison
   */
  comparePerformance(baselineData, currentData) {
    const comparison = {
      cpu: {
        baseline: baselineData.metrics.system.cpu?.usage || 0,
        current: currentData.metrics.system.cpu?.usage || 0,
        change: 0
      },
      memory: {
        baseline: baselineData.metrics.system.memory?.usage || 0,
        current: currentData.metrics.system.memory?.usage || 0,
        change: 0
      },
      disk: {
        baseline: baselineData.metrics.system.disk?.usage || 0,
        current: currentData.metrics.system.disk?.usage || 0,
        change: 0
      }
    };

    // Calculate percentage changes
    comparison.cpu.change = ((comparison.current - comparison.baseline) / comparison.baseline) * 100;
    comparison.memory.change = ((comparison.current - comparison.baseline) / comparison.baseline) * 100;
    comparison.disk.change = ((comparison.current - comparison.baseline) / comparison.baseline) * 100;

    return comparison;
  }
}

module.exports = new PerformanceService();





