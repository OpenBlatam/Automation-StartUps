import { EventEmitter } from 'events';
import crypto from 'crypto';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';

export interface SecurityThreat {
  id: string;
  type: 'brute_force' | 'sql_injection' | 'xss' | 'ddos' | 'suspicious_activity' | 'unauthorized_access';
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  description: string;
  detectedAt: Date;
  resolvedAt?: Date;
  status: 'active' | 'resolved' | 'false_positive';
  metadata: Record<string, any>;
  actions: SecurityAction[];
}

export interface SecurityAction {
  id: string;
  threatId: string;
  type: 'block_ip' | 'rate_limit' | 'alert' | 'quarantine' | 'investigate';
  description: string;
  executedAt: Date;
  status: 'pending' | 'executed' | 'failed';
  result?: any;
}

export interface SecurityPolicy {
  id: string;
  name: string;
  type: 'rate_limiting' | 'ip_blocking' | 'content_filtering' | 'authentication' | 'authorization';
  enabled: boolean;
  rules: SecurityRule[];
  actions: SecurityAction[];
  created: Date;
  updated: Date;
}

export interface SecurityRule {
  id: string;
  name: string;
  condition: string;
  threshold: number;
  timeWindow: number; // in seconds
  action: string;
  enabled: boolean;
}

export interface SecurityAudit {
  id: string;
  userId?: string;
  action: string;
  resource: string;
  ipAddress: string;
  userAgent: string;
  timestamp: Date;
  success: boolean;
  metadata: Record<string, any>;
}

export class AdvancedSecurityService extends EventEmitter {
  private threats: Map<string, SecurityThreat> = new Map();
  private policies: Map<string, SecurityPolicy> = new Map();
  private audits: Map<string, SecurityAudit> = new Map();
  private blockedIPs: Set<string> = new Set();
  private rateLimits: Map<string, { count: number; resetTime: number }> = new Map();
  private suspiciousActivities: Map<string, any> = new Map();

  constructor() {
    super();
    this.initializeDefaultPolicies();
    this.startSecurityMonitoring();
  }

  private initializeDefaultPolicies(): void {
    // Política de rate limiting
    const rateLimitPolicy: SecurityPolicy = {
      id: 'rate_limit_policy',
      name: 'Rate Limiting Policy',
      type: 'rate_limiting',
      enabled: true,
      rules: [
        {
          id: 'api_rate_limit',
          name: 'API Rate Limit',
          condition: 'api_requests',
          threshold: 100,
          timeWindow: 900, // 15 minutes
          action: 'block_temporarily',
          enabled: true
        },
        {
          id: 'login_rate_limit',
          name: 'Login Rate Limit',
          condition: 'login_attempts',
          threshold: 5,
          timeWindow: 300, // 5 minutes
          action: 'block_temporarily',
          enabled: true
        }
      ],
      actions: [],
      created: new Date(),
      updated: new Date()
    };

    // Política de bloqueo de IP
    const ipBlockingPolicy: SecurityPolicy = {
      id: 'ip_blocking_policy',
      name: 'IP Blocking Policy',
      type: 'ip_blocking',
      enabled: true,
      rules: [
        {
          id: 'suspicious_ip_block',
          name: 'Suspicious IP Block',
          condition: 'suspicious_activity',
          threshold: 3,
          timeWindow: 3600, // 1 hour
          action: 'block_ip',
          enabled: true
        }
      ],
      actions: [],
      created: new Date(),
      updated: new Date()
    };

    // Política de filtrado de contenido
    const contentFilteringPolicy: SecurityPolicy = {
      id: 'content_filtering_policy',
      name: 'Content Filtering Policy',
      type: 'content_filtering',
      enabled: true,
      rules: [
        {
          id: 'sql_injection_filter',
          name: 'SQL Injection Filter',
          condition: 'sql_injection_patterns',
          threshold: 1,
          timeWindow: 60,
          action: 'block_request',
          enabled: true
        },
        {
          id: 'xss_filter',
          name: 'XSS Filter',
          condition: 'xss_patterns',
          threshold: 1,
          timeWindow: 60,
          action: 'block_request',
          enabled: true
        }
      ],
      actions: [],
      created: new Date(),
      updated: new Date()
    };

    this.policies.set(rateLimitPolicy.id, rateLimitPolicy);
    this.policies.set(ipBlockingPolicy.id, ipBlockingPolicy);
    this.policies.set(contentFilteringPolicy.id, contentFilteringPolicy);
  }

  private startSecurityMonitoring(): void {
    // Monitoreo continuo de seguridad
    setInterval(() => {
      this.analyzeThreats();
      this.cleanupExpiredData();
    }, 60000); // Cada minuto
  }

  private analyzeThreats(): void {
    // Analizar patrones de amenazas
    this.detectBruteForce();
    this.detectSuspiciousActivity();
    this.detectDDoSAttacks();
  }

  private detectBruteForce(): void {
    const now = Date.now();
    const oneHourAgo = now - 3600000;

    // Agrupar intentos de login por IP
    const loginAttempts = Array.from(this.audits.values())
      .filter(audit => 
        audit.action === 'login' && 
        audit.timestamp.getTime() > oneHourAgo &&
        !audit.success
      )
      .reduce((acc, audit) => {
        const ip = audit.ipAddress;
        if (!acc[ip]) acc[ip] = [];
        acc[ip].push(audit);
        return acc;
      }, {} as Record<string, SecurityAudit[]>);

    // Detectar IPs con muchos intentos fallidos
    for (const [ip, attempts] of Object.entries(loginAttempts)) {
      if (attempts.length >= 10) {
        this.createThreat({
          type: 'brute_force',
          severity: 'high',
          source: ip,
          description: `Brute force attack detected from IP ${ip} with ${attempts.length} failed attempts`,
          metadata: { attempts: attempts.length, timeWindow: '1 hour' }
        });
      }
    }
  }

  private detectSuspiciousActivity(): void {
    const now = Date.now();
    const fiveMinutesAgo = now - 300000;

    // Detectar patrones de actividad sospechosa
    const suspiciousPatterns = [
      'unusual_request_frequency',
      'suspicious_user_agent',
      'unusual_geographic_location',
      'unusual_time_patterns'
    ];

    for (const pattern of suspiciousPatterns) {
      const activities = Array.from(this.audits.values())
        .filter(audit => audit.timestamp.getTime() > fiveMinutesAgo);

      if (this.isSuspiciousPattern(activities, pattern)) {
        this.createThreat({
          type: 'suspicious_activity',
          severity: 'medium',
          source: 'system',
          description: `Suspicious activity pattern detected: ${pattern}`,
          metadata: { pattern, activities: activities.length }
        });
      }
    }
  }

  private detectDDoSAttacks(): void {
    const now = Date.now();
    const oneMinuteAgo = now - 60000;

    // Agrupar requests por IP en el último minuto
    const recentRequests = Array.from(this.audits.values())
      .filter(audit => audit.timestamp.getTime() > oneMinuteAgo)
      .reduce((acc, audit) => {
        const ip = audit.ipAddress;
        acc[ip] = (acc[ip] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

    // Detectar IPs con demasiados requests
    for (const [ip, count] of Object.entries(recentRequests)) {
      if (count >= 100) { // 100 requests por minuto
        this.createThreat({
          type: 'ddos',
          severity: 'critical',
          source: ip,
          description: `DDoS attack detected from IP ${ip} with ${count} requests in 1 minute`,
          metadata: { requests: count, timeWindow: '1 minute' }
        });
      }
    }
  }

  private isSuspiciousPattern(activities: SecurityAudit[], pattern: string): boolean {
    switch (pattern) {
      case 'unusual_request_frequency':
        return activities.length > 50; // Más de 50 requests en 5 minutos
      case 'suspicious_user_agent':
        return activities.some(a => 
          a.userAgent.includes('bot') || 
          a.userAgent.includes('crawler') ||
          a.userAgent.length < 10
        );
      case 'unusual_geographic_location':
        // Simular detección de ubicación inusual
        return Math.random() < 0.1; // 10% de probabilidad
      case 'unusual_time_patterns':
        const nightHours = activities.filter(a => {
          const hour = a.timestamp.getHours();
          return hour < 6 || hour > 22;
        });
        return nightHours.length > activities.length * 0.8; // 80% de requests en horario nocturno
      default:
        return false;
    }
  }

  private createThreat(threatData: Omit<SecurityThreat, 'id' | 'detectedAt' | 'status' | 'actions'>): void {
    const threat: SecurityThreat = {
      ...threatData,
      id: `threat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      detectedAt: new Date(),
      status: 'active',
      actions: []
    };

    this.threats.set(threat.id, threat);
    this.emit('threat_detected', threat);

    // Ejecutar acciones automáticas
    this.executeThreatActions(threat);
  }

  private executeThreatActions(threat: SecurityThreat): void {
    const actions: SecurityAction[] = [];

    switch (threat.type) {
      case 'brute_force':
        actions.push({
          id: `action_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          threatId: threat.id,
          type: 'block_ip',
          description: `Block IP ${threat.source} for 1 hour`,
          executedAt: new Date(),
          status: 'executed',
          result: { blocked: true, duration: 3600 }
        });
        this.blockedIPs.add(threat.source);
        break;

      case 'ddos':
        actions.push({
          id: `action_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          threatId: threat.id,
          type: 'block_ip',
          description: `Block IP ${threat.source} for 24 hours`,
          executedAt: new Date(),
          status: 'executed',
          result: { blocked: true, duration: 86400 }
        });
        this.blockedIPs.add(threat.source);
        break;

      case 'sql_injection':
      case 'xss':
        actions.push({
          id: `action_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          threatId: threat.id,
          type: 'alert',
          description: `Alert security team about ${threat.type} attempt`,
          executedAt: new Date(),
          status: 'executed',
          result: { alerted: true }
        });
        break;

      case 'suspicious_activity':
        actions.push({
          id: `action_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          threatId: threat.id,
          type: 'investigate',
          description: `Investigate suspicious activity pattern`,
          executedAt: new Date(),
          status: 'pending'
        });
        break;
    }

    threat.actions = actions;
    this.threats.set(threat.id, threat);
  }

  private cleanupExpiredData(): void {
    const now = Date.now();
    const oneDayAgo = now - 86400000;

    // Limpiar rate limits expirados
    for (const [key, data] of this.rateLimits.entries()) {
      if (data.resetTime < now) {
        this.rateLimits.delete(key);
      }
    }

    // Limpiar actividades sospechosas expiradas
    for (const [key, data] of this.suspiciousActivities.entries()) {
      if (data.timestamp < oneDayAgo) {
        this.suspiciousActivities.delete(key);
      }
    }
  }

  // Verificar si una IP está bloqueada
  isIPBlocked(ip: string): boolean {
    return this.blockedIPs.has(ip);
  }

  // Verificar rate limit
  checkRateLimit(ip: string, action: string): boolean {
    const key = `${ip}_${action}`;
    const now = Date.now();
    const data = this.rateLimits.get(key);

    if (!data || data.resetTime < now) {
      this.rateLimits.set(key, { count: 1, resetTime: now + 900000 }); // 15 minutos
      return true;
    }

    if (data.count >= 100) { // 100 requests por 15 minutos
      return false;
    }

    data.count++;
    this.rateLimits.set(key, data);
    return true;
  }

  // Detectar patrones maliciosos en el contenido
  detectMaliciousContent(content: string): { isMalicious: boolean; patterns: string[] } {
    const patterns = {
      sqlInjection: [
        /('|(\\')|(;)|(\\;)|(union)|(select)|(insert)|(update)|(delete)|(drop)|(create)|(alter))/i,
        /(or|and)\s+\d+\s*=\s*\d+/i,
        /(union|select).*from/i
      ],
      xss: [
        /<script[^>]*>.*?<\/script>/gi,
        /javascript:/gi,
        /on\w+\s*=/gi,
        /<iframe[^>]*>.*?<\/iframe>/gi
      ],
      pathTraversal: [
        /\.\.\//g,
        /\.\.\\/g,
        /\.\.%2f/gi,
        /\.\.%5c/gi
      ]
    };

    const detectedPatterns: string[] = [];

    for (const [type, regexList] of Object.entries(patterns)) {
      for (const regex of regexList) {
        if (regex.test(content)) {
          detectedPatterns.push(type);
          break;
        }
      }
    }

    return {
      isMalicious: detectedPatterns.length > 0,
      patterns: detectedPatterns
    };
  }

  // Registrar auditoría
  logAudit(audit: Omit<SecurityAudit, 'id' | 'timestamp'>): void {
    const securityAudit: SecurityAudit = {
      ...audit,
      id: `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date()
    };

    this.audits.set(securityAudit.id, securityAudit);
    this.emit('audit_logged', securityAudit);
  }

  // Generar token de seguridad
  generateSecurityToken(payload: any, expiresIn: string = '1h'): string {
    return jwt.sign(payload, process.env.JWT_SECRET || 'supersecretjwtkey', { expiresIn });
  }

  // Verificar token de seguridad
  verifySecurityToken(token: string): any {
    try {
      return jwt.verify(token, process.env.JWT_SECRET || 'supersecretjwtkey');
    } catch (error) {
      return null;
    }
  }

  // Encriptar datos sensibles
  encryptSensitiveData(data: string): string {
    const algorithm = 'aes-256-cbc';
    const key = crypto.randomBytes(32);
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipher(algorithm, key);
    
    let encrypted = cipher.update(data, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    return iv.toString('hex') + ':' + encrypted;
  }

  // Desencriptar datos sensibles
  decryptSensitiveData(encryptedData: string): string {
    const algorithm = 'aes-256-cbc';
    const textParts = encryptedData.split(':');
    const iv = Buffer.from(textParts.shift()!, 'hex');
    const encryptedText = textParts.join(':');
    const key = crypto.randomBytes(32);
    const decipher = crypto.createDecipher(algorithm, key);
    
    let decrypted = decipher.update(encryptedText, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }

  // Obtener amenazas
  getThreats(limit?: number): SecurityThreat[] {
    const threats = Array.from(this.threats.values())
      .sort((a, b) => b.detectedAt.getTime() - a.detectedAt.getTime());
    
    return limit ? threats.slice(0, limit) : threats;
  }

  // Obtener auditorías
  getAudits(limit?: number): SecurityAudit[] {
    const audits = Array.from(this.audits.values())
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
    
    return limit ? audits.slice(0, limit) : audits;
  }

  // Obtener estadísticas de seguridad
  getSecurityStats(): {
    totalThreats: number;
    activeThreats: number;
    resolvedThreats: number;
    blockedIPs: number;
    totalAudits: number;
    recentThreats: SecurityThreat[];
  } {
    const threats = Array.from(this.threats.values());
    const audits = Array.from(this.audits.values());
    
    return {
      totalThreats: threats.length,
      activeThreats: threats.filter(t => t.status === 'active').length,
      resolvedThreats: threats.filter(t => t.status === 'resolved').length,
      blockedIPs: this.blockedIPs.size,
      totalAudits: audits.length,
      recentThreats: threats.slice(0, 10)
    };
  }
}

export const advancedSecurityService = new AdvancedSecurityService();

