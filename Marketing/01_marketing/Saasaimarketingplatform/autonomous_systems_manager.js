#!/usr/bin/env node

/**
 * Autonomous Systems Manager
 * Master controller that coordinates all autonomous systems
 */

const EventEmitter = require('events');
const SystemOrchestrator = require('./system_orchestrator');
const AIDecisionEngine = require('./ai_decision_engine');
const AutoRecoverySystem = require('./auto_recovery_system');
const AnomalyDetector = require('./anomaly_detector');
const AutoScaler = require('./auto_scaler');

class AutonomousSystemsManager extends EventEmitter {
  constructor() {
    super();
    
    // Initialize all systems
    this.orchestrator = SystemOrchestrator;
    this.decisionEngine = new AIDecisionEngine();
    this.recoverySystem = new AutoRecoverySystem();
    this.anomalyDetector = new AnomalyDetector();
    this.autoScaler = new AutoScaler();
    
    this.isRunning = false;
    this.systemsStatus = {};
    
    this.setupEventHandlers();
    
    console.log('🤖 Autonomous Systems Manager initialized');
  }

  /**
   * Setup event handlers for all systems
   */
  setupEventHandlers() {
    // Decision Engine events
    this.decisionEngine.on('performance-updated', (data) => {
      console.log('📊 Decision Engine performance:', data.accuracy);
      this.updateSystemStatus('decisionEngine', { accuracy: data.accuracy });
    });

    // Recovery System events
    this.recoverySystem.on('recovery-success', (data) => {
      console.log('✅ Recovery successful:', data.failureType);
      this.emit('system-recovered', data);
    });

    this.recoverySystem.on('recovery-failed', (data) => {
      console.error('❌ Recovery failed:', data.failureType);
      this.emit('system-critics-failure', data);
    });

    // Anomaly Detector events
    this.anomalyDetector.on('anomaly-detected', (data) => {
      console.warn('⚠️  Anomaly detected:', data.metric);
      this.handleAnomaly(data);
    });

    // Auto Scaler events
    this.autoScaler.on('scaled-up', (data) => {
      console.log('📈 System scaled up to:', data.instances);
      this.emit('system-scaled', data);
    });

    this.autoScaler.on('scaled-down', (data) => {
      console.log('📉 System scaled down to:', data.instances);
      this.emit('system-scaled', data);
    });
  }

  /**
   * Start all autonomous systems
   */
  async start() {
    if (this.isRunning) {
      console.log('⚠️  Systems already running');
      return;
    }

    console.log('🚀 Starting all autonomous systems...');
    this.isRunning = true;

    try {
      // Start orchestrator
      await this.orchestrator.start();
      console.log('✅ Orchestrator started');

      // Start recovery system monitoring
      this.recoverySystem.startMonitoring();
      console.log('✅ Recovery system started');

      // Start anomaly detection
      this.anomalyDetector.startMonitoring();
      console.log('✅ Anomaly detector started');

      // Start auto-scaling
      this.autoScaler.startScaling();
      console.log('✅ Auto-scaler started');

      // Initialize decision engine
      console.log('✅ Decision engine ready');

      this.isRunning = true;
      console.log('🎉 All autonomous systems started successfully');
      
      this.emit('all-systems-started');
    } catch (error) {
      console.error('❌ Error starting systems:', error);
      this.isRunning = false;
      throw error;
    }
  }

  /**
   * Handle detected anomaly
   */
  async handleAnomaly(data) {
    const { metric, value, anomaly } = data;
    
    // Make intelligent decision on how to respond
    const decision = await this.decisionEngine.makeDecision({
      type: 'anomaly',
      metric,
      value,
      severity: anomaly.severity
    }, [
      {
        id: 'auto-scale',
        type: 'scaling',
        action: 'scale',
        resourceIntensity: 0.3
      },
      {
        id: 'restart-service',
        type: 'recovery',
        action: 'restart',
        resourceIntensity: 0.5
      },
      {
        id: 'alert-only',
        type: 'monitoring',
        action: 'alert',
        resourceIntensity: 0.1
      }
    ]);

    console.log('🧠 Decision made for anomaly:', decision);

    // Execute decision
    if (decision.action === 'scale') {
      if (anomaly.severity === 'critical') {
        await this.autoScaler.scaleUp();
      }
    } else if (decision.action === 'restart') {
      await this.recoverySystem.handleFailure(metric, {});
    }

    this.emit('anomaly-handled', { data, decision });
  }

  /**
   * Make intelligent system decision
   */
  async makeSystemDecision(context) {
    return await this.decisionEngine.makeDecision(context, [
      {
        id: 'optimal',
        type: 'operational',
        action: 'continue',
        resourceIntensity: 0.2
      },
      {
        id: 'scale-up',
        type: 'scaling',
        action: 'scale-up',
        resourceIntensity: 0.4
      },
      {
        id: 'optimize',
        type: 'optimization',
        action: 'optimize',
        resourceIntensity: 0.6
      }
    ]);
  }

  /**
   * Update system status
   */
  updateSystemStatus(system, status) {
    this.systemsStatus[system] = {
      ...this.systemsStatus[system],
      ...status,
      lastUpdate: new Date()
    };

    this.emit('status-updated', {
      system,
      status: this.systemsStatus[system]
    });
  }

  /**
   * Get comprehensive system status
   */
  getStatus() {
    return {
      isRunning: this.isRunning,
      orchestrator: this.orchestrator.getStatus(),
      decisionEngine: this.decisionEngine.getStatus(),
      recoverySystem: this.recoverySystem.getRecoveryStats(),
      anomalyDetector: this.anomalyDetector.getAnomalyStats(),
      autoScaler: this.autoScaler.getStatus(),
      systemsStatus: this.systemsStatus,
      timestamp: new Date()
    };
  }

  /**
   * Stop all systems
   */
  async stop() {
    console.log('🛑 Stopping all autonomous systems...');
    
    this.isRunning = false;
    await this.orchestrator.stop();
    
    console.log('✅ All systems stopped');
    this.emit('all-systems-stopped');
  }

  /**
   * Perform health check on all systems
   */
  async healthCheck() {
    const health = {
      overall: true,
      systems: {}
    };

    // Check orchestrator
    try {
      const status = this.orchestrator.getStatus();
      health.systems.orchestrator = {
        healthy: status.isRunning,
        services: status.services
      };
    } catch (error) {
      health.systems.orchestrator = {
        healthy: false,
        error: error.message
      };
      health.overall = false;
    }

    // Check decision engine
    try {
      const status = this.decisionEngine.getStatus();
      health.systems.decisionEngine = {
        healthy: status.accuracy > 0.5,
        accuracy: status.accuracy
      };
    } catch (error) {
      health.systems.decisionEngine = {
        healthy: false,
        error: error.message
      };
      health.overall = false;
    }

    return health;
  }
}

// Create singleton instance
const autonomousManager = new AutonomousSystemsManager();

// Start if running directly
if (require.main === module) {
  autonomousManager.start().catch(error => {
    console.error('Failed to start autonomous systems:', error);
    process.exit(1);
  });
  
  // Graceful shutdown
  process.on('SIGTERM', async () => {
    console.log('SIGTERM received, stopping...');
    await autonomousManager.stop();
    process.exit(0);
  });
  
  process.on('SIGINT', async () => {
    console.log('SIGINT received, stopping...');
    await autonomousManager.stop();
    process.exit(0);
  });
}

module.exports = autonomousManager;



