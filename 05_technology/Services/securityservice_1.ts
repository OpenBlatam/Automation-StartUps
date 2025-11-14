import crypto from 'crypto';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import rateLimit from 'express-rate-limit';
import { Request, Response, NextFunction } from 'express';

export interface SecurityConfig {
  jwtSecret: string;
  jwtExpiration: string;
  bcryptRounds: number;
  rateLimitWindow: number;
  rateLimitMax: number;
  allowedOrigins: string[];
  encryptionKey: string;
  apiKeyLength: number;
}

export interface SecurityAudit {
  id: string;
  timestamp: Date;
  event: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  details: Record<string, any>;
  resolved: boolean;
}

export interface ThreatDetection {
  id: string;
  type: 'brute_force' | 'sql_injection' | 'xss' | 'ddos' | 'suspicious_pattern' | 'rate_limit_exceeded';
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  details: Record<string, any>;
  timestamp: Date;
  blocked: boolean;
  action: string;
}

export class SecurityService {
  private config: SecurityConfig;
  private auditLog: SecurityAudit[] = [];
  private threatLog: ThreatDetection[] = [];
  private blockedIPs: Set<string> = new Set();
  private suspiciousPatterns: Map<string, number> = new Map();

  constructor() {
    this.config = {
      jwtSecret: process.env.JWT_SECRET || 'supersecretjwtkey',
      jwtExpiration: process.env.JWT_EXPIRATION || '24h',
      bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS || '12'),
      rateLimitWindow: parseInt(process.env.RATE_LIMIT_WINDOW || '900000'), // 15 minutes
      rateLimitMax: parseInt(process.env.RATE_LIMIT_MAX || '100'),
      allowedOrigins: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
      encryptionKey: process.env.ENCRYPTION_KEY || 'encryptionkey123456789012345678901234',
      apiKeyLength: parseInt(process.env.API_KEY_LENGTH || '32')
    };
  }

  // Generar token JWT
  generateJWT(payload: any): string {
    return jwt.sign(payload, this.config.jwtSecret, {
      expiresIn: this.config.jwtExpiration,
      issuer: 'ai-marketing-feedback-system',
      audience: 'feedback-api-users'
    });
  }

  // Verificar token JWT
  verifyJWT(token: string): any {
    try {
      return jwt.verify(token, this.config.jwtSecret, {
        issuer: 'ai-marketing-feedback-system',
        audience: 'feedback-api-users'
      });
    } catch (error) {
      throw new Error('Invalid or expired token');
    }
  }

  // Generar hash de contraseña
  async hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, this.config.bcryptRounds);
  }

  // Verificar contraseña
  async verifyPassword(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
  }

  // Generar API key
  generateAPIKey(): string {
    return crypto.randomBytes(this.config.apiKeyLength).toString('hex');
  }

  // Encriptar datos sensibles
  encrypt(data: string): string {
    const cipher = crypto.createCipher('aes-256-cbc', this.config.encryptionKey);
    let encrypted = cipher.update(data, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return encrypted;
  }

  // Desencriptar datos sensibles
  decrypt(encryptedData: string): string {
    const decipher = crypto.createDecipher('aes-256-cbc', this.config.encryptionKey);
    let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
  }

  // Generar hash para datos
  generateHash(data: string): string {
    return crypto.createHash('sha256').update(data).digest('hex');
  }

  // Validar entrada contra patrones maliciosos
  validateInput(input: string): { valid: boolean; threats: string[] } {
    const threats: string[] = [];
    
    // Detectar SQL injection
    const sqlPatterns = [
      /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)/i,
      /(\b(OR|AND)\s+\d+\s*=\s*\d+)/i,
      /(\b(OR|AND)\s+['"]\s*=\s*['"])/i,
      /(\b(OR|AND)\s+1\s*=\s*1)/i
    ];
    
    if (sqlPatterns.some(pattern => pattern.test(input))) {
      threats.push('sql_injection');
    }
    
    // Detectar XSS
    const xssPatterns = [
      /<script[^>]*>.*?<\/script>/gi,
      /<iframe[^>]*>.*?<\/iframe>/gi,
      /javascript:/gi,
      /on\w+\s*=/gi,
      /<img[^>]*onerror/gi
    ];
    
    if (xssPatterns.some(pattern => pattern.test(input))) {
      threats.push('xss');
    }
    
    // Detectar patrones de inyección de comandos
    const commandPatterns = [
      /[;&|`$()]/,
      /\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig)\b/i
    ];
    
    if (commandPatterns.some(pattern => pattern.test(input))) {
      threats.push('command_injection');
    }
    
    // Detectar patrones de path traversal
    const pathPatterns = [
      /\.\.\//,
      /\.\.\\/,
      /%2e%2e%2f/i,
      /%2e%2e%5c/i
    ];
    
    if (pathPatterns.some(pattern => pattern.test(input))) {
      threats.push('path_traversal');
    }
    
    return {
      valid: threats.length === 0,
      threats
    };
  }

  // Detectar patrones sospechosos
  detectSuspiciousPatterns(ip: string, userAgent: string, request: any): ThreatDetection[] {
    const threats: ThreatDetection[] = [];
    const now = new Date();
    
    // Detectar intentos de fuerza bruta
    const bruteForceKey = `brute_force_${ip}`;
    const bruteForceCount = this.suspiciousPatterns.get(bruteForceKey) || 0;
    
    if (bruteForceCount > 10) {
      threats.push({
        id: `threat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: 'brute_force',
        severity: 'high',
        source: ip,
        details: { attempts: bruteForceCount, userAgent },
        timestamp: now,
        blocked: true,
        action: 'block_ip'
      });
      
      this.blockedIPs.add(ip);
      this.auditLog.push({
        id: `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: now,
        event: 'ip_blocked',
        severity: 'high',
        source: ip,
        details: { reason: 'brute_force', attempts: bruteForceCount },
        resolved: false
      });
    }
    
    // Detectar patrones de DDoS
    const ddosKey = `ddos_${ip}`;
    const ddosCount = this.suspiciousPatterns.get(ddosKey) || 0;
    
    if (ddosCount > 100) {
      threats.push({
        id: `threat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: 'ddos',
        severity: 'critical',
        source: ip,
        details: { requests: ddosCount, userAgent },
        timestamp: now,
        blocked: true,
        action: 'block_ip'
      });
      
      this.blockedIPs.add(ip);
    }
    
    // Detectar User-Agent sospechoso
    const suspiciousUserAgents = [
      'sqlmap', 'nikto', 'nmap', 'masscan', 'zap', 'burp',
      'scanner', 'bot', 'crawler', 'spider', 'harvester'
    ];
    
    if (suspiciousUserAgents.some(ua => userAgent.toLowerCase().includes(ua))) {
      threats.push({
        id: `threat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: 'suspicious_pattern',
        severity: 'medium',
        source: ip,
        details: { userAgent, pattern: 'suspicious_user_agent' },
        timestamp: now,
        blocked: false,
        action: 'monitor'
      });
    }
    
    // Detectar patrones de inyección en el cuerpo de la petición
    if (request.body) {
      const bodyStr = JSON.stringify(request.body);
      const validation = this.validateInput(bodyStr);
      
      if (!validation.valid) {
        threats.push({
          id: `threat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          type: 'sql_injection',
          severity: 'high',
          source: ip,
          details: { threats: validation.threats, body: bodyStr.substring(0, 100) },
          timestamp: now,
          blocked: true,
          action: 'block_request'
        });
      }
    }
    
    // Actualizar contadores
    this.suspiciousPatterns.set(bruteForceKey, bruteForceCount + 1);
    this.suspiciousPatterns.set(ddosKey, ddosCount + 1);
    
    // Limpiar contadores antiguos (cada hora)
    if (now.getMinutes() === 0) {
      this.cleanupCounters();
    }
    
    return threats;
  }

  // Verificar si una IP está bloqueada
  isIPBlocked(ip: string): boolean {
    return this.blockedIPs.has(ip);
  }

  // Desbloquear IP
  unblockIP(ip: string): void {
    this.blockedIPs.delete(ip);
    this.auditLog.push({
      id: `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      event: 'ip_unblocked',
      severity: 'medium',
      source: ip,
      details: { action: 'manual_unblock' },
      resolved: true
    });
  }

  // Middleware de seguridad
  securityMiddleware = (req: Request, res: Response, next: NextFunction) => {
    const ip = req.ip || req.connection.remoteAddress || 'unknown';
    const userAgent = req.get('User-Agent') || 'unknown';
    
    // Verificar si la IP está bloqueada
    if (this.isIPBlocked(ip)) {
      return res.status(403).json({
        error: 'IP blocked due to suspicious activity',
        code: 'IP_BLOCKED'
      });
    }
    
    // Detectar amenazas
    const threats = this.detectSuspiciousPatterns(ip, userAgent, req);
    
    if (threats.length > 0) {
      this.threatLog.push(...threats);
      
      // Bloquear si hay amenazas críticas
      const criticalThreats = threats.filter(t => t.severity === 'critical' || t.blocked);
      if (criticalThreats.length > 0) {
        return res.status(403).json({
          error: 'Request blocked due to security threats',
          code: 'SECURITY_THREAT',
          threats: criticalThreats.map(t => t.type)
        });
      }
    }
    
    // Agregar headers de seguridad
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('X-XSS-Protection', '1; mode=block');
    res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
    res.setHeader('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
    
    next();
  };

  // Middleware de rate limiting avanzado
  advancedRateLimit = (windowMs: number = this.config.rateLimitWindow, max: number = this.config.rateLimitMax) => {
    return rateLimit({
      windowMs,
      max,
      message: {
        error: 'Too many requests from this IP',
        code: 'RATE_LIMIT_EXCEEDED',
        retryAfter: Math.ceil(windowMs / 1000)
      },
      standardHeaders: true,
      legacyHeaders: false,
      handler: (req: Request, res: Response) => {
        const ip = req.ip || req.connection.remoteAddress || 'unknown';
        this.auditLog.push({
          id: `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          timestamp: new Date(),
          event: 'rate_limit_exceeded',
          severity: 'medium',
          source: ip,
          details: { max, windowMs },
          resolved: false
        });
        
        res.status(429).json({
          error: 'Too many requests from this IP',
          code: 'RATE_LIMIT_EXCEEDED',
          retryAfter: Math.ceil(windowMs / 1000)
        });
      }
    });
  };

  // Middleware de validación de entrada
  inputValidationMiddleware = (req: Request, res: Response, next: NextFunction) => {
    const bodyStr = JSON.stringify(req.body);
    const validation = this.validateInput(bodyStr);
    
    if (!validation.valid) {
      const ip = req.ip || req.connection.remoteAddress || 'unknown';
      
      this.auditLog.push({
        id: `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date(),
        event: 'malicious_input_detected',
        severity: 'high',
        source: ip,
        details: { threats: validation.threats, body: bodyStr.substring(0, 100) },
        resolved: false
      });
      
      return res.status(400).json({
        error: 'Malicious input detected',
        code: 'MALICIOUS_INPUT',
        threats: validation.threats
      });
    }
    
    next();
  };

  // Obtener logs de auditoría
  getAuditLogs(filters?: { severity?: string; source?: string; resolved?: boolean }): SecurityAudit[] {
    let logs = [...this.auditLog];
    
    if (filters) {
      if (filters.severity) {
        logs = logs.filter(log => log.severity === filters.severity);
      }
      if (filters.source) {
        logs = logs.filter(log => log.source === filters.source);
      }
      if (filters.resolved !== undefined) {
        logs = logs.filter(log => log.resolved === filters.resolved);
      }
    }
    
    return logs.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }

  // Obtener logs de amenazas
  getThreatLogs(filters?: { type?: string; severity?: string; blocked?: boolean }): ThreatDetection[] {
    let logs = [...this.threatLog];
    
    if (filters) {
      if (filters.type) {
        logs = logs.filter(log => log.type === filters.type);
      }
      if (filters.severity) {
        logs = logs.filter(log => log.severity === filters.severity);
      }
      if (filters.blocked !== undefined) {
        logs = logs.filter(log => log.blocked === filters.blocked);
      }
    }
    
    return logs.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }

  // Obtener estadísticas de seguridad
  getSecurityStats(): {
    totalAuditEvents: number;
    totalThreats: number;
    blockedIPs: number;
    threatsByType: Record<string, number>;
    threatsBySeverity: Record<string, number>;
    recentActivity: SecurityAudit[];
  } {
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
    
    const threatsByType: Record<string, number> = {};
    const threatsBySeverity: Record<string, number> = {};
    
    this.threatLog.forEach(threat => {
      threatsByType[threat.type] = (threatsByType[threat.type] || 0) + 1;
      threatsBySeverity[threat.severity] = (threatsBySeverity[threat.severity] || 0) + 1;
    });
    
    const recentActivity = this.auditLog.filter(log => log.timestamp > oneHourAgo);
    
    return {
      totalAuditEvents: this.auditLog.length,
      totalThreats: this.threatLog.length,
      blockedIPs: this.blockedIPs.size,
      threatsByType,
      threatsBySeverity,
      recentActivity: recentActivity.slice(0, 10)
    };
  }

  // Limpiar contadores antiguos
  private cleanupCounters(): void {
    const now = new Date();
    const oneHourAgo = now.getTime() - 60 * 60 * 1000;
    
    // Limpiar logs antiguos (mantener solo últimos 7 días)
    const sevenDaysAgo = now.getTime() - 7 * 24 * 60 * 60 * 1000;
    
    this.auditLog = this.auditLog.filter(log => log.timestamp.getTime() > sevenDaysAgo);
    this.threatLog = this.threatLog.filter(log => log.timestamp.getTime() > sevenDaysAgo);
    
    // Limpiar contadores de patrones sospechosos
    for (const [key, value] of this.suspiciousPatterns.entries()) {
      if (value < 1) {
        this.suspiciousPatterns.delete(key);
      }
    }
  }

  // Generar reporte de seguridad
  generateSecurityReport(): {
    summary: {
      totalEvents: number;
      criticalThreats: number;
      blockedIPs: number;
      securityScore: number;
    };
    threats: ThreatDetection[];
    recommendations: string[];
  } {
    const stats = this.getSecurityStats();
    const criticalThreats = this.threatLog.filter(t => t.severity === 'critical').length;
    
    // Calcular puntuación de seguridad (0-100)
    let securityScore = 100;
    securityScore -= criticalThreats * 10;
    securityScore -= stats.blockedIPs * 5;
    securityScore -= stats.totalThreats * 2;
    securityScore = Math.max(0, securityScore);
    
    const recommendations: string[] = [];
    
    if (criticalThreats > 0) {
      recommendations.push('Investigar y mitigar amenazas críticas inmediatamente');
    }
    
    if (stats.blockedIPs > 10) {
      recommendations.push('Revisar políticas de bloqueo de IP');
    }
    
    if (stats.threatsByType['brute_force'] > 5) {
      recommendations.push('Implementar autenticación de dos factores');
    }
    
    if (stats.threatsByType['sql_injection'] > 0) {
      recommendations.push('Revisar y actualizar validación de entrada');
    }
    
    return {
      summary: {
        totalEvents: stats.totalAuditEvents,
        criticalThreats,
        blockedIPs: stats.blockedIPs,
        securityScore
      },
      threats: this.threatLog.slice(0, 20),
      recommendations
    };
  }
}

export const securityService = new SecurityService();

