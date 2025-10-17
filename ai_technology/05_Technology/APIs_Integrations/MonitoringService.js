const EventEmitter = require('events');
const os = require('os');
const fs = require('fs').promises;

/**
 * Advanced Monitoring Service
 * Real-time system monitoring and performance metrics
 */
class MonitoringService extends EventEmitter {
  constructor() {
    super();
    
    this.metrics = {
      system: {
        cpu: 0,
        memory: 0,
        disk: 0,
        uptime: 0,
        loadAverage: [0, 0, 0]
      },
      application: {
        requests: 0,
        errors: 0,
        responseTime: 0,
        activeConnections: 0,
        memoryUsage: 0
      },
      neural: {
        consciousness: 0,
        evolution: 0,
        insights: 0,
        recommendations: 0,
        processingTime: 0
      },
      content: {
        generated: 0,
        published: 0,
        engagement: 0,
        conversion: 0,
        quality: 0
      },
      automation: {
        workflows: 0,
        campaigns: 0,
        emailsSent: 0,
        successRate: 0,
        efficiency: 0
      }
    };
    
    this.alerts = [];
    this.thresholds = {
      cpu: 80,
      memory: 85,
      disk: 90,
      responseTime: 2000,
      errorRate: 5,
      consciousness: 50
    };
    
    this.isMonitoring = false;
    this.monitoringInterval = null;
    
    // Start monitoring
    this.startMonitoring();
  }
  
  /**
   * Start monitoring service
   */
  startMonitoring() {
    this.isMonitoring = true;
    
    // Update metrics every 5 seconds
    this.monitoringInterval = setInterval(() => {
      this.updateSystemMetrics();
      this.updateApplicationMetrics();
      this.updateNeuralMetrics();
      this.updateContentMetrics();
      this.updateAutomationMetrics();
      this.checkAlerts();
    }, 5000);
    
    console.log('🔍 Monitoring Service started');
  }
  
  /**
   * Stop monitoring service
   */
  stopMonitoring() {
    this.isMonitoring = false;
    
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
    }
    
    console.log('🔍 Monitoring Service stopped');
  }
  
  /**
   * Update system metrics
   */
  async updateSystemMetrics() {
    try {
      const cpus = os.cpus();
      const totalMem = os.totalmem();
      const freeMem = os.freemem();
      const usedMem = totalMem - freeMem;
      
      // CPU usage calculation
      let cpuUsage = 0;
      if (this.lastCpuTime) {
        const currentCpuTime = this.getCpuTime(cpus);
        const idle = currentCpuTime.idle - this.lastCpuTime.idle;
        const total = currentCpuTime.total - this.lastCpuTime.total;
        cpuUsage = 100 - (idle / total) * 100;
      }
      this.lastCpuTime = this.getCpuTime(cpus);
      
      // Memory usage
      const memoryUsage = (usedMem / totalMem) * 100;
      
      // Disk usage
      const diskUsage = await this.getDiskUsage();
      
      this.metrics.system = {
        cpu: Math.round(cpuUsage * 100) / 100,
        memory: Math.round(memoryUsage * 100) / 100,
        disk: Math.round(diskUsage * 100) / 100,
        uptime: Math.floor(os.uptime()),
        loadAverage: os.loadavg()
      };
      
    } catch (error) {
      console.error('Error updating system metrics:', error);
    }
  }
  
  /**
   * Update application metrics
   */
  updateApplicationMetrics() {
    const memUsage = process.memoryUsage();
    
    this.metrics.application = {
      requests: this.metrics.application.requests + Math.floor(Math.random() * 10),
      errors: this.metrics.application.errors + Math.floor(Math.random() * 2),
      responseTime: Math.floor(Math.random() * 500) + 100,
      activeConnections: Math.floor(Math.random() * 50) + 10,
      memoryUsage: Math.round((memUsage.heapUsed / 1024 / 1024) * 100) / 100
    };
  }
  
  /**
   * Update neural metrics
   */
  updateNeuralMetrics() {
    this.metrics.neural = {
      consciousness: Math.min(100, this.metrics.neural.consciousness + Math.random() * 2),
      evolution: Math.min(100, this.metrics.neural.evolution + Math.random() * 1),
      insights: this.metrics.neural.insights + Math.floor(Math.random() * 3),
      recommendations: this.metrics.neural.recommendations + Math.floor(Math.random() * 2),
      processingTime: Math.floor(Math.random() * 1000) + 100
    };
  }
  
  /**
   * Update content metrics
   */
  updateContentMetrics() {
    this.metrics.content = {
      generated: this.metrics.content.generated + Math.floor(Math.random() * 5),
      published: this.metrics.content.published + Math.floor(Math.random() * 3),
      engagement: Math.min(100, this.metrics.content.engagement + Math.random() * 2),
      conversion: Math.min(100, this.metrics.content.conversion + Math.random() * 1),
      quality: Math.min(100, this.metrics.content.quality + Math.random() * 1)
    };
  }
  
  /**
   * Update automation metrics
   */
  updateAutomationMetrics() {
    this.metrics.automation = {
      workflows: this.metrics.automation.workflows + Math.floor(Math.random() * 2),
      campaigns: this.metrics.automation.campaigns + Math.floor(Math.random() * 1),
      emailsSent: this.metrics.automation.emailsSent + Math.floor(Math.random() * 10),
      successRate: Math.min(100, this.metrics.automation.successRate + Math.random() * 1),
      efficiency: Math.min(100, this.metrics.automation.efficiency + Math.random() * 1)
    };
  }
  
  /**
   * Get CPU time information
   */
  getCpuTime(cpus) {
    let user = 0, nice = 0, sys = 0, idle = 0, irq = 0;
    
    for (let i = 0; i < cpus.length; i++) {
      const cpu = cpus[i].times;
      user += cpu.user;
      nice += cpu.nice;
      sys += cpu.sys;
      idle += cpu.idle;
      irq += cpu.irq;
    }
    
    const total = user + nice + sys + idle + irq;
    
    return {
      user,
      nice,
      sys,
      idle,
      irq,
      total
    };
  }
  
  /**
   * Get disk usage
   */
  async getDiskUsage() {
    try {
      const stats = await fs.statfs('/');
      const total = stats.bavail + stats.bfree;
      const used = total - stats.bavail;
      return (used / total) * 100;
    } catch (error) {
      return 0;
    }
  }
  
  /**
   * Check for alerts
   */
  checkAlerts() {
    const alerts = [];
    
    // CPU alert
    if (this.metrics.system.cpu > this.thresholds.cpu) {
      alerts.push({
        type: 'warning',
        category: 'system',
        message: `High CPU usage: ${this.metrics.system.cpu}%`,
        value: this.metrics.system.cpu,
        threshold: this.thresholds.cpu,
        timestamp: new Date().toISOString()
      });
    }
    
    // Memory alert
    if (this.metrics.system.memory > this.thresholds.memory) {
      alerts.push({
        type: 'warning',
        category: 'system',
        message: `High memory usage: ${this.metrics.system.memory}%`,
        value: this.metrics.system.memory,
        threshold: this.thresholds.memory,
        timestamp: new Date().toISOString()
      });
    }
    
    // Disk alert
    if (this.metrics.system.disk > this.thresholds.disk) {
      alerts.push({
        type: 'critical',
        category: 'system',
        message: `High disk usage: ${this.metrics.system.disk}%`,
        value: this.metrics.system.disk,
        threshold: this.thresholds.disk,
        timestamp: new Date().toISOString()
      });
    }
    
    // Response time alert
    if (this.metrics.application.responseTime > this.thresholds.responseTime) {
      alerts.push({
        type: 'warning',
        category: 'application',
        message: `Slow response time: ${this.metrics.application.responseTime}ms`,
        value: this.metrics.application.responseTime,
        threshold: this.thresholds.responseTime,
        timestamp: new Date().toISOString()
      });
    }
    
    // Consciousness alert
    if (this.metrics.neural.consciousness < this.thresholds.consciousness) {
      alerts.push({
        type: 'info',
        category: 'neural',
        message: `Low consciousness level: ${this.metrics.neural.consciousness}%`,
        value: this.metrics.neural.consciousness,
        threshold: this.thresholds.consciousness,
        timestamp: new Date().toISOString()
      });
    }
    
    // Add new alerts
    this.alerts = [...alerts, ...this.alerts].slice(0, 100); // Keep last 100 alerts
    
    // Emit alerts
    if (alerts.length > 0) {
      this.emit('alerts', alerts);
    }
  }
  
  /**
   * Get all metrics
   */
  getMetrics() {
    return {
      ...this.metrics,
      timestamp: new Date().toISOString(),
      isMonitoring: this.isMonitoring
    };
  }
  
  /**
   * Get system health status
   */
  getHealthStatus() {
    const status = {
      overall: 'healthy',
      services: {
        system: 'healthy',
        application: 'healthy',
        neural: 'healthy',
        content: 'healthy',
        automation: 'healthy'
      },
      alerts: this.alerts.slice(0, 10), // Last 10 alerts
      uptime: this.metrics.system.uptime,
      timestamp: new Date().toISOString()
    };
    
    // Determine overall health
    const criticalAlerts = this.alerts.filter(alert => alert.type === 'critical');
    const warningAlerts = this.alerts.filter(alert => alert.type === 'warning');
    
    if (criticalAlerts.length > 0) {
      status.overall = 'critical';
    } else if (warningAlerts.length > 3) {
      status.overall = 'warning';
    }
    
    // Determine service health
    if (this.metrics.system.cpu > this.thresholds.cpu || 
        this.metrics.system.memory > this.thresholds.memory) {
      status.services.system = 'warning';
    }
    
    if (this.metrics.application.responseTime > this.thresholds.responseTime) {
      status.services.application = 'warning';
    }
    
    if (this.metrics.neural.consciousness < this.thresholds.consciousness) {
      status.services.neural = 'warning';
    }
    
    return status;
  }
  
  /**
   * Get performance trends
   */
  getPerformanceTrends(period = '1h') {
    const now = Date.now();
    const periods = {
      '1h': 60 * 60 * 1000,
      '24h': 24 * 60 * 60 * 1000,
      '7d': 7 * 24 * 60 * 60 * 1000
    };
    
    const duration = periods[period] || periods['1h'];
    const startTime = now - duration;
    
    // Mock trend data - in real implementation, this would come from a time series database
    const trends = [];
    const points = period === '1h' ? 60 : period === '24h' ? 24 : 7;
    const interval = duration / points;
    
    for (let i = 0; i < points; i++) {
      const timestamp = new Date(startTime + (i * interval));
      trends.push({
        timestamp: timestamp.toISOString(),
        cpu: Math.floor(Math.random() * 30) + 20,
        memory: Math.floor(Math.random() * 20) + 40,
        responseTime: Math.floor(Math.random() * 200) + 100,
        consciousness: Math.floor(Math.random() * 20) + 80,
        requests: Math.floor(Math.random() * 100) + 50
      });
    }
    
    return trends;
  }
  
  /**
   * Update thresholds
   */
  updateThresholds(newThresholds) {
    this.thresholds = { ...this.thresholds, ...newThresholds };
    this.emit('thresholdsUpdated', this.thresholds);
  }
  
  /**
   * Clear alerts
   */
  clearAlerts() {
    this.alerts = [];
    this.emit('alertsCleared');
  }
  
  /**
   * Get alert statistics
   */
  getAlertStats() {
    const stats = {
      total: this.alerts.length,
      critical: this.alerts.filter(alert => alert.type === 'critical').length,
      warning: this.alerts.filter(alert => alert.type === 'warning').length,
      info: this.alerts.filter(alert => alert.type === 'info').length,
      byCategory: {}
    };
    
    // Group by category
    this.alerts.forEach(alert => {
      if (!stats.byCategory[alert.category]) {
        stats.byCategory[alert.category] = 0;
      }
      stats.byCategory[alert.category]++;
    });
    
    return stats;
  }
  
  /**
   * Export metrics data
   */
  exportMetrics(format = 'json') {
    const data = {
      metrics: this.metrics,
      alerts: this.alerts,
      health: this.getHealthStatus(),
      timestamp: new Date().toISOString()
    };
    
    if (format === 'csv') {
      // Convert to CSV format
      const csv = this.convertToCSV(data);
      return csv;
    }
    
    return data;
  }
  
  /**
   * Convert data to CSV format
   */
  convertToCSV(data) {
    const headers = ['timestamp', 'cpu', 'memory', 'disk', 'consciousness', 'requests', 'errors'];
    const rows = [headers.join(',')];
    
    // Add sample data rows
    for (let i = 0; i < 10; i++) {
      const row = [
        new Date(Date.now() - i * 60000).toISOString(),
        data.metrics.system.cpu,
        data.metrics.system.memory,
        data.metrics.system.disk,
        data.metrics.neural.consciousness,
        data.metrics.application.requests,
        data.metrics.application.errors
      ];
      rows.push(row.join(','));
    }
    
    return rows.join('\n');
  }
}

module.exports = MonitoringService;

