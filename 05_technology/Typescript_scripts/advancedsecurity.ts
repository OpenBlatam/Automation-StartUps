import express from 'express';
import { advancedSecurityService } from '../services/advancedSecurityService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener amenazas de seguridad
router.get('/threats', authenticateToken, (req, res) => {
  try {
    const { limit = 50, status, severity } = req.query;
    
    let threats = advancedSecurityService.getThreats(parseInt(limit as string));
    
    if (status) {
      threats = threats.filter(threat => threat.status === status);
    }
    
    if (severity) {
      threats = threats.filter(threat => threat.severity === severity);
    }
    
    res.json({
      success: true,
      data: threats,
      count: threats.length
    });
  } catch (error) {
    console.error('Error fetching security threats:', error);
    res.status(500).json({ error: 'Failed to fetch security threats' });
  }
});

// Obtener auditorías de seguridad
router.get('/audits', authenticateToken, (req, res) => {
  try {
    const { limit = 100, userId, action, success } = req.query;
    
    let audits = advancedSecurityService.getAudits(parseInt(limit as string));
    
    if (userId) {
      audits = audits.filter(audit => audit.userId === userId);
    }
    
    if (action) {
      audits = audits.filter(audit => audit.action === action);
    }
    
    if (success !== undefined) {
      audits = audits.filter(audit => audit.success === (success === 'true'));
    }
    
    res.json({
      success: true,
      data: audits,
      count: audits.length
    });
  } catch (error) {
    console.error('Error fetching security audits:', error);
    res.status(500).json({ error: 'Failed to fetch security audits' });
  }
});

// Obtener estadísticas de seguridad
router.get('/stats/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedSecurityService.getSecurityStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching security stats:', error);
    res.status(500).json({ error: 'Failed to fetch security stats' });
  }
});

// Obtener dashboard de seguridad
router.get('/dashboard/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedSecurityService.getSecurityStats();
    const threats = advancedSecurityService.getThreats(10);
    const audits = advancedSecurityService.getAudits(20);
    
    const dashboard = {
      overview: {
        totalThreats: stats.totalThreats,
        activeThreats: stats.activeThreats,
        resolvedThreats: stats.resolvedThreats,
        blockedIPs: stats.blockedIPs,
        totalAudits: stats.totalAudits,
        threatResolutionRate: stats.totalThreats > 0 
          ? (stats.resolvedThreats / stats.totalThreats) * 100 
          : 0
      },
      recentThreats: threats,
      recentAudits: audits,
      security: {
        totalThreats: stats.totalThreats,
        activeThreats: stats.activeThreats,
        resolvedThreats: stats.resolvedThreats,
        blockedIPs: stats.blockedIPs
      }
    };
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    console.error('Error fetching security dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch security dashboard' });
  }
});

// Verificar si una IP está bloqueada
router.get('/check-ip/:ip', authenticateToken, (req, res) => {
  try {
    const { ip } = req.params;
    const isBlocked = advancedSecurityService.isIPBlocked(ip);
    
    res.json({
      success: true,
      data: {
        ip,
        isBlocked,
        message: isBlocked ? 'IP is blocked' : 'IP is allowed'
      }
    });
  } catch (error) {
    console.error('Error checking IP status:', error);
    res.status(500).json({ error: 'Failed to check IP status' });
  }
});

// Verificar rate limit
router.get('/check-rate-limit/:ip/:action', authenticateToken, (req, res) => {
  try {
    const { ip, action } = req.params;
    const isAllowed = advancedSecurityService.checkRateLimit(ip, action);
    
    res.json({
      success: true,
      data: {
        ip,
        action,
        isAllowed,
        message: isAllowed ? 'Rate limit not exceeded' : 'Rate limit exceeded'
      }
    });
  } catch (error) {
    console.error('Error checking rate limit:', error);
    res.status(500).json({ error: 'Failed to check rate limit' });
  }
});

// Detectar contenido malicioso
router.post('/detect-malicious-content', authenticateToken, (req, res) => {
  try {
    const { content } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }
    
    const detection = advancedSecurityService.detectMaliciousContent(content);
    
    res.json({
      success: true,
      data: detection
    });
  } catch (error) {
    console.error('Error detecting malicious content:', error);
    res.status(500).json({ error: 'Failed to detect malicious content' });
  }
});

// Registrar auditoría de seguridad
router.post('/log-audit', authenticateToken, (req, res) => {
  try {
    const { userId, action, resource, ipAddress, userAgent, success, metadata } = req.body;
    
    if (!action || !resource || !ipAddress || !userAgent) {
      return res.status(400).json({ 
        error: 'Missing required fields: action, resource, ipAddress, userAgent' 
      });
    }
    
    advancedSecurityService.logAudit({
      userId,
      action,
      resource,
      ipAddress,
      userAgent,
      success: success || false,
      metadata: metadata || {}
    });
    
    res.json({
      success: true,
      message: 'Security audit logged successfully'
    });
  } catch (error) {
    console.error('Error logging security audit:', error);
    res.status(500).json({ error: 'Failed to log security audit' });
  }
});

// Generar token de seguridad
router.post('/generate-token', authenticateToken, (req, res) => {
  try {
    const { payload, expiresIn = '1h' } = req.body;
    
    if (!payload) {
      return res.status(400).json({ error: 'Payload is required' });
    }
    
    const token = advancedSecurityService.generateSecurityToken(payload, expiresIn);
    
    res.json({
      success: true,
      data: { token },
      message: 'Security token generated successfully'
    });
  } catch (error) {
    console.error('Error generating security token:', error);
    res.status(500).json({ error: 'Failed to generate security token' });
  }
});

// Verificar token de seguridad
router.post('/verify-token', authenticateToken, (req, res) => {
  try {
    const { token } = req.body;
    
    if (!token) {
      return res.status(400).json({ error: 'Token is required' });
    }
    
    const payload = advancedSecurityService.verifySecurityToken(token);
    
    if (!payload) {
      return res.status(401).json({ error: 'Invalid or expired token' });
    }
    
    res.json({
      success: true,
      data: { payload },
      message: 'Token verified successfully'
    });
  } catch (error) {
    console.error('Error verifying security token:', error);
    res.status(500).json({ error: 'Failed to verify security token' });
  }
});

// Encriptar datos sensibles
router.post('/encrypt', authenticateToken, (req, res) => {
  try {
    const { data } = req.body;
    
    if (!data) {
      return res.status(400).json({ error: 'Data is required' });
    }
    
    const encrypted = advancedSecurityService.encryptSensitiveData(data);
    
    res.json({
      success: true,
      data: { encrypted },
      message: 'Data encrypted successfully'
    });
  } catch (error) {
    console.error('Error encrypting data:', error);
    res.status(500).json({ error: 'Failed to encrypt data' });
  }
});

// Desencriptar datos sensibles
router.post('/decrypt', authenticateToken, (req, res) => {
  try {
    const { encryptedData } = req.body;
    
    if (!encryptedData) {
      return res.status(400).json({ error: 'Encrypted data is required' });
    }
    
    const decrypted = advancedSecurityService.decryptSensitiveData(encryptedData);
    
    res.json({
      success: true,
      data: { decrypted },
      message: 'Data decrypted successfully'
    });
  } catch (error) {
    console.error('Error decrypting data:', error);
    res.status(500).json({ error: 'Failed to decrypt data' });
  }
});

// Obtener logs de seguridad
router.get('/logs/security', authenticateToken, (req, res) => {
  try {
    const { type, severity, limit = 50 } = req.query;
    
    let threats = advancedSecurityService.getThreats(parseInt(limit as string));
    
    if (type) {
      threats = threats.filter(threat => threat.type === type);
    }
    
    if (severity) {
      threats = threats.filter(threat => threat.severity === severity);
    }
    
    res.json({
      success: true,
      data: threats,
      count: threats.length
    });
  } catch (error) {
    console.error('Error fetching security logs:', error);
    res.status(500).json({ error: 'Failed to fetch security logs' });
  }
});

// Obtener logs de auditoría
router.get('/logs/audit', authenticateToken, (req, res) => {
  try {
    const { userId, action, success, limit = 100 } = req.query;
    
    let audits = advancedSecurityService.getAudits(parseInt(limit as string));
    
    if (userId) {
      audits = audits.filter(audit => audit.userId === userId);
    }
    
    if (action) {
      audits = audits.filter(audit => audit.action === action);
    }
    
    if (success !== undefined) {
      audits = audits.filter(audit => audit.success === (success === 'true'));
    }
    
    res.json({
      success: true,
      data: audits,
      count: audits.length
    });
  } catch (error) {
    console.error('Error fetching audit logs:', error);
    res.status(500).json({ error: 'Failed to fetch audit logs' });
  }
});

// Obtener plantillas de seguridad
router.get('/templates/list', authenticateToken, (req, res) => {
  try {
    const templates = [
      {
        id: 'brute_force_protection',
        name: 'Brute Force Protection',
        description: 'Protect against brute force attacks',
        type: 'rate_limiting',
        category: 'authentication',
        features: ['Login Attempt Limiting', 'IP Blocking', 'Progressive Delays'],
        rules: [
          {
            condition: 'login_attempts',
            threshold: 5,
            timeWindow: 300,
            action: 'block_temporarily'
          }
        ]
      },
      {
        id: 'sql_injection_protection',
        name: 'SQL Injection Protection',
        description: 'Protect against SQL injection attacks',
        type: 'content_filtering',
        category: 'input_validation',
        features: ['Pattern Detection', 'Input Sanitization', 'Query Validation'],
        rules: [
          {
            condition: 'sql_injection_patterns',
            threshold: 1,
            timeWindow: 60,
            action: 'block_request'
          }
        ]
      },
      {
        id: 'xss_protection',
        name: 'XSS Protection',
        description: 'Protect against Cross-Site Scripting attacks',
        type: 'content_filtering',
        category: 'input_validation',
        features: ['Script Tag Detection', 'Event Handler Detection', 'Content Sanitization'],
        rules: [
          {
            condition: 'xss_patterns',
            threshold: 1,
            timeWindow: 60,
            action: 'block_request'
          }
        ]
      },
      {
        id: 'ddos_protection',
        name: 'DDoS Protection',
        description: 'Protect against Distributed Denial of Service attacks',
        type: 'rate_limiting',
        category: 'network',
        features: ['Request Rate Limiting', 'IP Blocking', 'Traffic Analysis'],
        rules: [
          {
            condition: 'request_frequency',
            threshold: 100,
            timeWindow: 60,
            action: 'block_ip'
          }
        ]
      },
      {
        id: 'suspicious_activity_detection',
        name: 'Suspicious Activity Detection',
        description: 'Detect and respond to suspicious activities',
        type: 'monitoring',
        category: 'behavioral',
        features: ['Pattern Analysis', 'Anomaly Detection', 'Risk Scoring'],
        rules: [
          {
            condition: 'suspicious_patterns',
            threshold: 3,
            timeWindow: 3600,
            action: 'investigate'
          }
        ]
      }
    ];
    
    res.json({
      success: true,
      data: templates,
      count: templates.length
    });
  } catch (error) {
    console.error('Error fetching security templates:', error);
    res.status(500).json({ error: 'Failed to fetch security templates' });
  }
});

// Validar configuración de seguridad
router.post('/validate', authenticateToken, (req, res) => {
  try {
    const { type, rules, actions } = req.body;
    
    if (!type || !rules) {
      return res.status(400).json({ error: 'Type and rules are required' });
    }
    
    // Simular validación de configuración
    const validation = {
      valid: true,
      errors: [],
      warnings: [],
      suggestions: []
    };
    
    // Validaciones específicas por tipo
    switch (type) {
      case 'rate_limiting':
        if (!rules.some((rule: any) => rule.condition === 'api_requests')) {
          validation.warnings.push('Consider adding API request rate limiting');
        }
        break;
      case 'content_filtering':
        if (!rules.some((rule: any) => rule.condition === 'sql_injection_patterns')) {
          validation.warnings.push('Consider adding SQL injection protection');
        }
        if (!rules.some((rule: any) => rule.condition === 'xss_patterns')) {
          validation.warnings.push('Consider adding XSS protection');
        }
        break;
      case 'ip_blocking':
        if (!rules.some((rule: any) => rule.condition === 'suspicious_activity')) {
          validation.warnings.push('Consider adding suspicious activity detection');
        }
        break;
      default:
        validation.warnings.push(`Unknown security type: ${type}`);
    }
    
    // Validar reglas
    for (const rule of rules) {
      if (!rule.condition || !rule.threshold || !rule.action) {
        validation.errors.push('Each rule must have condition, threshold, and action');
      }
      if (rule.threshold <= 0) {
        validation.errors.push('Threshold must be greater than 0');
      }
      if (rule.timeWindow <= 0) {
        validation.errors.push('Time window must be greater than 0');
      }
    }
    
    res.json({
      success: true,
      data: validation
    });
  } catch (error) {
    console.error('Error validating security configuration:', error);
    res.status(500).json({ error: 'Failed to validate security configuration' });
  }
});

export default router;






