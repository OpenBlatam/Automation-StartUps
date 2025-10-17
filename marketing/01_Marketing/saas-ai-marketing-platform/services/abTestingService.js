const crypto = require('crypto');
const mongoose = require('mongoose');
const User = require('../models/User');
const GeneratedContent = require('../models/GeneratedContent');
const aiService = require('./advancedAIService');
const analyticsService = require('./analyticsService');

class ABTestingService {
  constructor() {
    this.activeTests = new Map();
    this.testResults = new Map();
    this.testConfigs = new Map();
    this.isInitialized = false;
  }

  /**
   * Initialize A/B testing service
   */
  async initialize() {
    if (this.isInitialized) return;

    try {
      await this.loadActiveTests();
      await this.loadTestConfigs();
      this.isInitialized = true;
      console.log('A/B Testing Service initialized successfully');
    } catch (error) {
      console.error('Failed to initialize A/B Testing Service:', error);
      throw error;
    }
  }

  /**
   * Create A/B test
   */
  async createTest(testConfig) {
    await this.initialize();

    const {
      name,
      description,
      hypothesis,
      variants,
      trafficAllocation = 100,
      targetAudience = {},
      successMetrics = [],
      duration = 7, // days
      minSampleSize = 100,
      confidenceLevel = 0.95,
      userId
    } = testConfig;

    const testId = crypto.randomUUID();
    const test = {
      id: testId,
      name,
      description,
      hypothesis,
      variants: variants.map((variant, index) => ({
        id: `variant_${index + 1}`,
        name: variant.name || `Variant ${index + 1}`,
        content: variant.content,
        weight: variant.weight || 1,
        isControl: index === 0,
        traffic: 0,
        conversions: 0,
        impressions: 0
      })),
      trafficAllocation,
      targetAudience,
      successMetrics,
      duration,
      minSampleSize,
      confidenceLevel,
      status: 'draft',
      createdBy: userId,
      createdAt: new Date(),
      startedAt: null,
      endedAt: null,
      results: {
        winner: null,
        confidence: 0,
        significance: false,
        lift: 0,
        pValue: 1
      }
    };

    this.activeTests.set(testId, test);
    return test;
  }

  /**
   * Start A/B test
   */
  async startTest(testId) {
    const test = this.activeTests.get(testId);
    if (!test) {
      throw new Error('Test not found');
    }

    if (test.status !== 'draft') {
      throw new Error('Test cannot be started');
    }

    // Validate test configuration
    if (test.variants.length < 2) {
      throw new Error('Test must have at least 2 variants');
    }

    if (test.successMetrics.length === 0) {
      throw new Error('Test must have at least one success metric');
    }

    // Calculate traffic allocation
    const totalWeight = test.variants.reduce((sum, variant) => sum + variant.weight, 0);
    test.variants.forEach(variant => {
      variant.traffic = (variant.weight / totalWeight) * test.trafficAllocation;
    });

    test.status = 'running';
    test.startedAt = new Date();
    test.endedAt = new Date(Date.now() + test.duration * 24 * 60 * 60 * 1000);

    this.activeTests.set(testId, test);

    // Schedule test end
    setTimeout(() => {
      this.endTest(testId);
    }, test.duration * 24 * 60 * 60 * 1000);

    return test;
  }

  /**
   * Get variant for user
   */
  async getVariantForUser(testId, userId) {
    const test = this.activeTests.get(testId);
    if (!test || test.status !== 'running') {
      return null;
    }

    // Check if user is in target audience
    if (!this.isUserInTargetAudience(userId, test.targetAudience)) {
      return null;
    }

    // Use consistent hashing to ensure same user gets same variant
    const hash = crypto.createHash('md5').update(`${testId}-${userId}`).digest('hex');
    const hashValue = parseInt(hash.substring(0, 8), 16) / 0xffffffff;

    let cumulativeWeight = 0;
    for (const variant of test.variants) {
      cumulativeWeight += variant.traffic / 100;
      if (hashValue <= cumulativeWeight) {
        return variant;
      }
    }

    return test.variants[0]; // Fallback to control
  }

  /**
   * Record test event
   */
  async recordEvent(testId, userId, eventType, eventData = {}) {
    const test = this.activeTests.get(testId);
    if (!test || test.status !== 'running') {
      return;
    }

    const variant = await this.getVariantForUser(testId, userId);
    if (!variant) {
      return;
    }

    // Update variant metrics
    if (eventType === 'impression') {
      variant.impressions += 1;
    } else if (eventType === 'conversion') {
      variant.conversions += 1;
    }

    // Record detailed event
    const event = {
      testId,
      userId,
      variantId: variant.id,
      eventType,
      eventData,
      timestamp: new Date()
    };

    // Store event in database
    await this.storeEvent(event);

    // Update test results
    this.activeTests.set(testId, test);

    // Check if test should be ended early
    if (this.shouldEndTestEarly(test)) {
      await this.endTest(testId);
    }
  }

  /**
   * End A/B test
   */
  async endTest(testId) {
    const test = this.activeTests.get(testId);
    if (!test || test.status !== 'running') {
      return;
    }

    test.status = 'completed';
    test.endedAt = new Date();

    // Calculate test results
    const results = await this.calculateTestResults(test);
    test.results = results;

    this.activeTests.set(testId, test);

    // Store results
    await this.storeTestResults(test);

    return test;
  }

  /**
   * Calculate test results
   */
  async calculateTestResults(test) {
    const control = test.variants.find(v => v.isControl);
    const treatments = test.variants.filter(v => !v.isControl);

    if (!control || treatments.length === 0) {
      return {
        winner: null,
        confidence: 0,
        significance: false,
        lift: 0,
        pValue: 1
      };
    }

    const controlRate = control.conversions / Math.max(control.impressions, 1);
    const results = [];

    for (const treatment of treatments) {
      const treatmentRate = treatment.conversions / Math.max(treatment.impressions, 1);
      const lift = ((treatmentRate - controlRate) / controlRate) * 100;
      
      // Calculate statistical significance
      const significance = this.calculateSignificance(
        control.conversions,
        control.impressions,
        treatment.conversions,
        treatment.impressions,
        test.confidenceLevel
      );

      results.push({
        variantId: treatment.id,
        variantName: treatment.name,
        conversionRate: treatmentRate,
        lift: lift,
        significance: significance.significant,
        pValue: significance.pValue,
        confidence: significance.confidence
      });
    }

    // Find winner
    const significantResults = results.filter(r => r.significance);
    const winner = significantResults.length > 0 
      ? significantResults.reduce((best, current) => 
          current.lift > best.lift ? current : best
        )
      : null;

    return {
      winner: winner ? winner.variantId : null,
      confidence: winner ? winner.confidence : 0,
      significance: winner ? winner.significance : false,
      lift: winner ? winner.lift : 0,
      pValue: winner ? winner.pValue : 1,
      allResults: results
    };
  }

  /**
   * Calculate statistical significance
   */
  calculateSignificance(controlConversions, controlImpressions, treatmentConversions, treatmentImpressions, confidenceLevel = 0.95) {
    const n1 = controlImpressions;
    const n2 = treatmentImpressions;
    const x1 = controlConversions;
    const x2 = treatmentConversions;

    if (n1 === 0 || n2 === 0) {
      return { significant: false, pValue: 1, confidence: 0 };
    }

    const p1 = x1 / n1;
    const p2 = x2 / n2;
    const p = (x1 + x2) / (n1 + n2);

    // Calculate z-score
    const se = Math.sqrt(p * (1 - p) * (1/n1 + 1/n2));
    const z = (p2 - p1) / se;

    // Calculate p-value (two-tailed test)
    const pValue = 2 * (1 - this.normalCDF(Math.abs(z)));

    // Calculate confidence interval
    const margin = this.normalCDFInverse((1 + confidenceLevel) / 2) * se;
    const confidence = Math.max(0, Math.min(1, 1 - pValue));

    return {
      significant: pValue < (1 - confidenceLevel),
      pValue: pValue,
      confidence: confidence,
      zScore: z,
      margin: margin
    };
  }

  /**
   * Normal CDF approximation
   */
  normalCDF(x) {
    return 0.5 * (1 + this.erf(x / Math.sqrt(2)));
  }

  /**
   * Error function approximation
   */
  erf(x) {
    const a1 = 0.254829592;
    const a2 = -0.284496736;
    const a3 = 1.421413741;
    const a4 = -1.453152027;
    const a5 = 1.061405429;
    const p = 0.3275911;

    const sign = x >= 0 ? 1 : -1;
    x = Math.abs(x);

    const t = 1.0 / (1.0 + p * x);
    const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);

    return sign * y;
  }

  /**
   * Inverse normal CDF approximation
   */
  normalCDFInverse(p) {
    if (p <= 0 || p >= 1) {
      throw new Error('Invalid probability');
    }

    const a = [0, -3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239];
    const b = [0, -5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01, -1.328068155288572e+01];
    const c = [0, -7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00];
    const d = [0, 7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00];

    const pLow = 0.02425;
    const pHigh = 1 - pLow;

    let x;
    if (p < pLow) {
      const q = Math.sqrt(-2 * Math.log(p));
      x = (((((c[1] * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) * q + c[6]) / ((((d[1] * q + d[2]) * q + d[3]) * q + d[4]) * q + 1);
    } else if (p <= pHigh) {
      const q = p - 0.5;
      const r = q * q;
      x = (((((a[1] * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * r + a[6]) * q / (((((b[1] * r + b[2]) * r + b[3]) * r + b[4]) * r + b[5]) * r + 1);
    } else {
      const q = Math.sqrt(-2 * Math.log(1 - p));
      x = -(((((c[1] * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) * q + c[6]) / ((((d[1] * q + d[2]) * q + d[3]) * q + d[4]) * q + 1);
    }

    return x;
  }

  /**
   * Check if user is in target audience
   */
  async isUserInTargetAudience(userId, targetAudience) {
    if (!targetAudience || Object.keys(targetAudience).length === 0) {
      return true;
    }

    const user = await User.findById(userId);
    if (!user) {
      return false;
    }

    // Check age range
    if (targetAudience.ageRange) {
      const userAge = this.calculateAge(user.birthDate);
      if (userAge < targetAudience.ageRange.min || userAge > targetAudience.ageRange.max) {
        return false;
      }
    }

    // Check industry
    if (targetAudience.industries && targetAudience.industries.length > 0) {
      if (!targetAudience.industries.includes(user.industry)) {
        return false;
      }
    }

    // Check subscription plan
    if (targetAudience.subscriptionPlans && targetAudience.subscriptionPlans.length > 0) {
      if (!targetAudience.subscriptionPlans.includes(user.subscription.plan)) {
        return false;
      }
    }

    // Check location
    if (targetAudience.locations && targetAudience.locations.length > 0) {
      if (!targetAudience.locations.includes(user.location)) {
        return false;
      }
    }

    return true;
  }

  /**
   * Calculate age from birth date
   */
  calculateAge(birthDate) {
    if (!birthDate) return null;
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  }

  /**
   * Check if test should end early
   */
  shouldEndTestEarly(test) {
    const totalImpressions = test.variants.reduce((sum, variant) => sum + variant.impressions, 0);
    
    // End early if we have enough samples and significant results
    if (totalImpressions >= test.minSampleSize) {
      const results = this.calculateTestResults(test);
      if (results.significance && results.confidence >= test.confidenceLevel) {
        return true;
      }
    }

    // End early if test has been running for maximum duration
    const maxDuration = 30; // days
    const daysRunning = (Date.now() - test.startedAt.getTime()) / (1000 * 60 * 60 * 24);
    if (daysRunning >= maxDuration) {
      return true;
    }

    return false;
  }

  /**
   * Get test results
   */
  async getTestResults(testId) {
    const test = this.activeTests.get(testId);
    if (!test) {
      throw new Error('Test not found');
    }

    return {
      test: test,
      results: test.results,
      status: test.status,
      progress: this.calculateTestProgress(test)
    };
  }

  /**
   * Calculate test progress
   */
  calculateTestProgress(test) {
    const totalImpressions = test.variants.reduce((sum, variant) => sum + variant.impressions, 0);
    const progress = Math.min(100, (totalImpressions / test.minSampleSize) * 100);
    
    const daysRunning = test.startedAt ? 
      (Date.now() - test.startedAt.getTime()) / (1000 * 60 * 60 * 24) : 0;
    const timeProgress = Math.min(100, (daysRunning / test.duration) * 100);

    return {
      sampleProgress: progress,
      timeProgress: timeProgress,
      overallProgress: Math.max(progress, timeProgress),
      isComplete: test.status === 'completed',
      canEndEarly: this.shouldEndTestEarly(test)
    };
  }

  /**
   * Get all tests for user
   */
  async getUserTests(userId) {
    const userTests = [];
    
    for (const [testId, test] of this.activeTests) {
      if (test.createdBy === userId) {
        userTests.push({
          id: test.id,
          name: test.name,
          description: test.description,
          status: test.status,
          createdAt: test.createdAt,
          startedAt: test.startedAt,
          endedAt: test.endedAt,
          progress: this.calculateTestProgress(test),
          results: test.results
        });
      }
    }

    return userTests.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  }

  /**
   * Get test analytics
   */
  async getTestAnalytics(testId) {
    const test = this.activeTests.get(testId);
    if (!test) {
      throw new Error('Test not found');
    }

    const analytics = {
      testId: test.id,
      name: test.name,
      status: test.status,
      duration: test.duration,
      totalImpressions: test.variants.reduce((sum, variant) => sum + variant.impressions, 0),
      totalConversions: test.variants.reduce((sum, variant) => sum + variant.conversions, 0),
      variants: test.variants.map(variant => ({
        id: variant.id,
        name: variant.name,
        isControl: variant.isControl,
        impressions: variant.impressions,
        conversions: variant.conversions,
        conversionRate: variant.conversions / Math.max(variant.impressions, 1),
        traffic: variant.traffic
      })),
      results: test.results,
      progress: this.calculateTestProgress(test)
    };

    return analytics;
  }

  /**
   * Generate test report
   */
  async generateTestReport(testId) {
    const analytics = await this.getTestAnalytics(testId);
    const test = this.activeTests.get(testId);

    const report = {
      ...analytics,
      summary: {
        hypothesis: test.hypothesis,
        successMetrics: test.successMetrics,
        targetAudience: test.targetAudience,
        confidenceLevel: test.confidenceLevel,
        minSampleSize: test.minSampleSize
      },
      recommendations: this.generateTestRecommendations(analytics),
      nextSteps: this.generateNextSteps(analytics)
    };

    return report;
  }

  /**
   * Generate test recommendations
   */
  generateTestRecommendations(analytics) {
    const recommendations = [];

    if (analytics.status === 'running') {
      if (analytics.progress.overallProgress < 50) {
        recommendations.push({
          type: 'sample_size',
          priority: 'medium',
          message: 'Test needs more traffic to reach statistical significance',
          action: 'Consider increasing traffic allocation or extending test duration'
        });
      }

      if (analytics.progress.canEndEarly) {
        recommendations.push({
          type: 'early_end',
          priority: 'high',
          message: 'Test has reached statistical significance and can be ended early',
          action: 'End test to implement winning variant'
        });
      }
    } else if (analytics.status === 'completed') {
      if (analytics.results.significance) {
        recommendations.push({
          type: 'implement_winner',
          priority: 'high',
          message: `Implement winning variant: ${analytics.results.winner}`,
          action: 'Deploy winning variant to all users'
        });
      } else {
        recommendations.push({
          type: 'insufficient_data',
          priority: 'medium',
          message: 'Test did not reach statistical significance',
          action: 'Consider running test longer or with more traffic'
        });
      }
    }

    return recommendations;
  }

  /**
   * Generate next steps
   */
  generateNextSteps(analytics) {
    const nextSteps = [];

    if (analytics.status === 'draft') {
      nextSteps.push('Start the test to begin data collection');
      nextSteps.push('Monitor test progress and performance');
    } else if (analytics.status === 'running') {
      nextSteps.push('Continue monitoring test performance');
      nextSteps.push('Check for statistical significance');
      nextSteps.push('Prepare for test completion');
    } else if (analytics.status === 'completed') {
      if (analytics.results.significance) {
        nextSteps.push('Implement winning variant');
        nextSteps.push('Document test results and learnings');
        nextSteps.push('Plan follow-up tests');
      } else {
        nextSteps.push('Analyze why test did not reach significance');
        nextSteps.push('Consider test modifications');
        nextSteps.push('Plan new test with different approach');
      }
    }

    return nextSteps;
  }

  /**
   * Store test event
   */
  async storeEvent(event) {
    // This would store the event in the database
    console.log('Storing test event:', event);
  }

  /**
   * Store test results
   */
  async storeTestResults(test) {
    // This would store the test results in the database
    console.log('Storing test results:', test.id);
  }

  /**
   * Load active tests
   */
  async loadActiveTests() {
    // This would load active tests from the database
    console.log('Loading active tests...');
  }

  /**
   * Load test configs
   */
  async loadTestConfigs() {
    // This would load test configurations from the database
    console.log('Loading test configs...');
  }

  /**
   * Get test statistics
   */
  getTestStatistics() {
    const totalTests = this.activeTests.size;
    const runningTests = Array.from(this.activeTests.values()).filter(t => t.status === 'running').length;
    const completedTests = Array.from(this.activeTests.values()).filter(t => t.status === 'completed').length;
    const draftTests = Array.from(this.activeTests.values()).filter(t => t.status === 'draft').length;

    return {
      total: totalTests,
      running: runningTests,
      completed: completedTests,
      draft: draftTests
    };
  }
}

module.exports = new ABTestingService();





