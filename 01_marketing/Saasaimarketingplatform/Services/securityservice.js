const crypto = require('crypto');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const User = require('../models/User');

class SecurityService {
  constructor() {
    this.encryptionKey = process.env.ENCRYPTION_KEY || crypto.randomBytes(32);
    this.jwtSecret = process.env.JWT_SECRET;
    this.rateLimiters = new Map();
    this.blockedIPs = new Set();
    this.suspiciousActivities = new Map();
    this.isInitialized = false;
  }

  /**
   * Initialize security service
   */
  async initialize() {
    if (this.isInitialized) return;

    try {
      await this.setupRateLimiters();
      await this.loadBlockedIPs();
      await this.loadSuspiciousActivities();
      this.isInitialized = true;
      console.log('Security Service initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Security Service:', error);
      throw error;
    }
  }

  /**
   * Setup rate limiters
   */
  async setupRateLimiters() {
    // API rate limiter
    this.rateLimiters.set('api', rateLimit({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 100, // limit each IP to 100 requests per windowMs
      message: 'Too many requests from this IP, please try again later.',
      standardHeaders: true,
      legacyHeaders: false
    }));

    // Auth rate limiter
    this.rateLimiters.set('auth', rateLimit({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 5, // limit each IP to 5 auth requests per windowMs
      message: 'Too many authentication attempts, please try again later.',
      standardHeaders: true,
      legacyHeaders: false
    }));

    // Content generation rate limiter
    this.rateLimiters.set('content', rateLimit({
      windowMs: 60 * 1000, // 1 minute
      max: 10, // limit each user to 10 content generations per minute
      keyGenerator: (req) => req.user?.id || req.ip,
      message: 'Too many content generation requests, please slow down.',
      standardHeaders: true,
      legacyHeaders: false
    }));

    // File upload rate limiter
    this.rateLimiters.set('upload', rateLimit({
      windowMs: 60 * 1000, // 1 minute
      max: 5, // limit each user to 5 uploads per minute
      keyGenerator: (req) => req.user?.id || req.ip,
      message: 'Too many file uploads, please slow down.',
      standardHeaders: true,
      legacyHeaders: false
    }));
  }

  /**
   * Encrypt sensitive data
   */
  encryptData(data) {
    try {
      const iv = crypto.randomBytes(16);
      const cipher = crypto.createCipher('aes-256-cbc', this.encryptionKey);
      let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
      encrypted += cipher.final('hex');
      return iv.toString('hex') + ':' + encrypted;
    } catch (error) {
      console.error('Encryption error:', error);
      throw new Error('Failed to encrypt data');
    }
  }

  /**
   * Decrypt sensitive data
   */
  decryptData(encryptedData) {
    try {
      const parts = encryptedData.split(':');
      const iv = Buffer.from(parts[0], 'hex');
      const encrypted = parts[1];
      const decipher = crypto.createDecipher('aes-256-cbc', this.encryptionKey);
      let decrypted = decipher.update(encrypted, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      return JSON.parse(decrypted);
    } catch (error) {
      console.error('Decryption error:', error);
      throw new Error('Failed to decrypt data');
    }
  }

  /**
   * Hash password
   */
  async hashPassword(password) {
    try {
      const saltRounds = 12;
      return await bcrypt.hash(password, saltRounds);
    } catch (error) {
      console.error('Password hashing error:', error);
      throw new Error('Failed to hash password');
    }
  }

  /**
   * Verify password
   */
  async verifyPassword(password, hashedPassword) {
    try {
      return await bcrypt.compare(password, hashedPassword);
    } catch (error) {
      console.error('Password verification error:', error);
      return false;
    }
  }

  /**
   * Generate JWT token
   */
  generateToken(payload, expiresIn = '7d') {
    try {
      return jwt.sign(payload, this.jwtSecret, { expiresIn });
    } catch (error) {
      console.error('Token generation error:', error);
      throw new Error('Failed to generate token');
    }
  }

  /**
   * Verify JWT token
   */
  verifyToken(token) {
    try {
      return jwt.verify(token, this.jwtSecret);
    } catch (error) {
      console.error('Token verification error:', error);
      throw new Error('Invalid token');
    }
  }

  /**
   * Generate secure random string
   */
  generateSecureRandom(length = 32) {
    return crypto.randomBytes(length).toString('hex');
  }

  /**
   * Generate API key
   */
  generateAPIKey() {
    const prefix = 'ak_';
    const randomPart = this.generateSecureRandom(32);
    return prefix + randomPart;
  }

  /**
   * Validate input data
   */
  validateInput(data, schema) {
    const errors = [];
    
    for (const [field, rules] of Object.entries(schema)) {
      const value = data[field];
      
      if (rules.required && (!value || value === '')) {
        errors.push(`${field} is required`);
        continue;
      }
      
      if (value) {
        if (rules.type === 'email' && !this.isValidEmail(value)) {
          errors.push(`${field} must be a valid email`);
        }
        
        if (rules.type === 'password' && !this.isValidPassword(value)) {
          errors.push(`${field} must be at least 8 characters with uppercase, lowercase, number and special character`);
        }
        
        if (rules.minLength && value.length < rules.minLength) {
          errors.push(`${field} must be at least ${rules.minLength} characters`);
        }
        
        if (rules.maxLength && value.length > rules.maxLength) {
          errors.push(`${field} must be no more than ${rules.maxLength} characters`);
        }
        
        if (rules.pattern && !rules.pattern.test(value)) {
          errors.push(`${field} format is invalid`);
        }
      }
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Validate email format
   */
  isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * Validate password strength
   */
  isValidPassword(password) {
    // At least 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return passwordRegex.test(password);
  }

  /**
   * Sanitize input data
   */
  sanitizeInput(data) {
    if (typeof data === 'string') {
      return data
        .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
        .replace(/<[^>]*>/g, '')
        .trim();
    }
    
    if (typeof data === 'object' && data !== null) {
      const sanitized = {};
      for (const [key, value] of Object.entries(data)) {
        sanitized[key] = this.sanitizeInput(value);
      }
      return sanitized;
    }
    
    return data;
  }

  /**
   * Check for suspicious activity
   */
  async checkSuspiciousActivity(userId, activity, metadata = {}) {
    const userActivities = this.suspiciousActivities.get(userId) || [];
    const now = new Date();
    
    // Add current activity
    userActivities.push({
      activity,
      metadata,
      timestamp: now,
      ip: metadata.ip,
      userAgent: metadata.userAgent
    });
    
    // Keep only last 100 activities
    if (userActivities.length > 100) {
      userActivities.splice(0, userActivities.length - 100);
    }
    
    this.suspiciousActivities.set(userId, userActivities);
    
    // Check for suspicious patterns
    const suspiciousScore = this.calculateSuspiciousScore(userActivities);
    
    if (suspiciousScore > 0.7) {
      await this.handleSuspiciousActivity(userId, activity, suspiciousScore);
      return { isSuspicious: true, score: suspiciousScore };
    }
    
    return { isSuspicious: false, score: suspiciousScore };
  }

  /**
   * Calculate suspicious activity score
   */
  calculateSuspiciousScore(activities) {
    let score = 0;
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
    
    // Check for rapid successive activities
    const recentActivities = activities.filter(a => a.timestamp > oneHourAgo);
    if (recentActivities.length > 20) {
      score += 0.3;
    }
    
    // Check for multiple IP addresses
    const uniqueIPs = new Set(recentActivities.map(a => a.ip));
    if (uniqueIPs.size > 3) {
      score += 0.2;
    }
    
    // Check for unusual user agents
    const userAgents = recentActivities.map(a => a.userAgent);
    const suspiciousUserAgents = userAgents.filter(ua => 
      !ua || ua.length < 10 || ua.includes('bot') || ua.includes('crawler')
    );
    if (suspiciousUserAgents.length > 0) {
      score += 0.2;
    }
    
    // Check for failed authentication attempts
    const failedAuths = recentActivities.filter(a => a.activity === 'auth_failed');
    if (failedAuths.length > 5) {
      score += 0.3;
    }
    
    return Math.min(score, 1.0);
  }

  /**
   * Handle suspicious activity
   */
  async handleSuspiciousActivity(userId, activity, score) {
    console.log(`Suspicious activity detected for user ${userId}: ${activity} (score: ${score})`);
    
    // Log the activity
    await this.logSecurityEvent('suspicious_activity', {
      userId,
      activity,
      score,
      timestamp: new Date()
    });
    
    // Send alert to security team
    await this.sendSecurityAlert(userId, activity, score);
    
    // Temporarily block user if score is very high
    if (score > 0.9) {
      await this.temporarilyBlockUser(userId, '1h');
    }
  }

  /**
   * Temporarily block user
   */
  async temporarilyBlockUser(userId, duration) {
    const user = await User.findById(userId);
    if (user) {
      user.isBlocked = true;
      user.blockedUntil = new Date(Date.now() + this.parseDuration(duration));
      await user.save();
      
      console.log(`User ${userId} temporarily blocked until ${user.blockedUntil}`);
    }
  }

  /**
   * Parse duration string
   */
  parseDuration(duration) {
    const units = {
      's': 1000,
      'm': 60 * 1000,
      'h': 60 * 60 * 1000,
      'd': 24 * 60 * 60 * 1000
    };
    
    const match = duration.match(/^(\d+)([smhd])$/);
    if (match) {
      const value = parseInt(match[1]);
      const unit = match[2];
      return value * units[unit];
    }
    
    return 60 * 60 * 1000; // Default 1 hour
  }

  /**
   * Check if IP is blocked
   */
  isIPBlocked(ip) {
    return this.blockedIPs.has(ip);
  }

  /**
   * Block IP address
   */
  blockIP(ip, reason = 'Suspicious activity') {
    this.blockedIPs.add(ip);
    console.log(`IP ${ip} blocked: ${reason}`);
  }

  /**
   * Unblock IP address
   */
  unblockIP(ip) {
    this.blockedIPs.delete(ip);
    console.log(`IP ${ip} unblocked`);
  }

  /**
   * Get rate limiter
   */
  getRateLimiter(type) {
    return this.rateLimiters.get(type);
  }

  /**
   * Create security headers middleware
   */
  createSecurityHeaders() {
    return helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
          fontSrc: ["'self'", "https://fonts.gstatic.com"],
          imgSrc: ["'self'", "data:", "https:"],
          scriptSrc: ["'self'"],
          connectSrc: ["'self'", "https://api.openai.com"],
          frameSrc: ["'none'"],
          objectSrc: ["'none'"],
          upgradeInsecureRequests: []
        }
      },
      hsts: {
        maxAge: 31536000,
        includeSubDomains: true,
        preload: true
      },
      noSniff: true,
      xssFilter: true,
      referrerPolicy: { policy: 'strict-origin-when-cross-origin' }
    });
  }

  /**
   * Log security event
   */
  async logSecurityEvent(eventType, data) {
    const logEntry = {
      eventType,
      data,
      timestamp: new Date(),
      severity: this.getEventSeverity(eventType)
    };
    
    // In a real implementation, this would be stored in a security log database
    console.log('Security Event:', logEntry);
  }

  /**
   * Get event severity
   */
  getEventSeverity(eventType) {
    const severityMap = {
      'login_success': 'info',
      'login_failed': 'warning',
      'suspicious_activity': 'high',
      'account_locked': 'high',
      'data_breach': 'critical',
      'unauthorized_access': 'high'
    };
    
    return severityMap[eventType] || 'info';
  }

  /**
   * Send security alert
   */
  async sendSecurityAlert(userId, activity, score) {
    // This would integrate with your notification system
    console.log(`Security alert: User ${userId} - ${activity} (score: ${score})`);
  }

  /**
   * Load blocked IPs
   */
  async loadBlockedIPs() {
    // Load from database or file
    console.log('Loading blocked IPs...');
  }

  /**
   * Load suspicious activities
   */
  async loadSuspiciousActivities() {
    // Load from database
    console.log('Loading suspicious activities...');
  }

  /**
   * Generate secure session ID
   */
  generateSessionId() {
    return crypto.randomBytes(32).toString('hex');
  }

  /**
   * Validate session
   */
  async validateSession(sessionId, userId) {
    // This would check session in database
    return true;
  }

  /**
   * Invalidate session
   */
  async invalidateSession(sessionId) {
    // This would remove session from database
    console.log(`Invalidating session: ${sessionId}`);
  }

  /**
   * Get security statistics
   */
  getSecurityStats() {
    return {
      blockedIPs: this.blockedIPs.size,
      suspiciousUsers: this.suspiciousActivities.size,
      rateLimiters: this.rateLimiters.size,
      uptime: process.uptime()
    };
  }

  /**
   * Audit log entry
   */
  async auditLog(action, userId, details = {}) {
    const auditEntry = {
      action,
      userId,
      details,
      timestamp: new Date(),
      ip: details.ip,
      userAgent: details.userAgent
    };
    
    // Store in audit log database
    console.log('Audit Log:', auditEntry);
  }
}

module.exports = new SecurityService();





