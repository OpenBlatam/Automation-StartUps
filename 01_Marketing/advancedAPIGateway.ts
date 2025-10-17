import express from 'express';
import { advancedAPIGatewayService } from '../services/advancedAPIGatewayService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener rutas
router.get('/routes', authenticateToken, (req, res) => {
  try {
    const { method, status, limit = 50 } = req.query;
    
    let routes = advancedAPIGatewayService.getRoutes();
    
    if (method) {
      routes = routes.filter(r => r.method === method);
    }
    
    if (status) {
      routes = routes.filter(r => r.status === status);
    }
    
    if (limit) {
      routes = routes.slice(0, parseInt(limit as string));
    }
    
    res.json({
      success: true,
      data: routes,
      count: routes.length
    });
  } catch (error) {
    console.error('Error fetching API routes:', error);
    res.status(500).json({ error: 'Failed to fetch API routes' });
  }
});

// Crear ruta
router.post('/routes', authenticateToken, (req, res) => {
  try {
    const routeData = req.body;
    
    if (!routeData.name || !routeData.path || !routeData.method || !routeData.target) {
      return res.status(400).json({ 
        error: 'Missing required fields: name, path, method, target' 
      });
    }
    
    const routeId = advancedAPIGatewayService.createRoute(routeData);
    
    res.status(201).json({
      success: true,
      data: { id: routeId },
      message: 'API route created successfully'
    });
  } catch (error) {
    console.error('Error creating API route:', error);
    res.status(500).json({ error: 'Failed to create API route' });
  }
});

// Obtener ruta específica
router.get('/routes/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const routes = advancedAPIGatewayService.getRoutes();
    const route = routes.find(r => r.id === id);
    
    if (!route) {
      return res.status(404).json({ error: 'API route not found' });
    }
    
    res.json({
      success: true,
      data: route
    });
  } catch (error) {
    console.error('Error fetching API route:', error);
    res.status(500).json({ error: 'Failed to fetch API route' });
  }
});

// Obtener middleware
router.get('/middleware', authenticateToken, (req, res) => {
  try {
    const { type, enabled, limit = 50 } = req.query;
    
    let middleware = advancedAPIGatewayService.getMiddleware();
    
    if (type) {
      middleware = middleware.filter(m => m.type === type);
    }
    
    if (enabled !== undefined) {
      middleware = middleware.filter(m => m.enabled === (enabled === 'true'));
    }
    
    if (limit) {
      middleware = middleware.slice(0, parseInt(limit as string));
    }
    
    res.json({
      success: true,
      data: middleware,
      count: middleware.length
    });
  } catch (error) {
    console.error('Error fetching API middleware:', error);
    res.status(500).json({ error: 'Failed to fetch API middleware' });
  }
});

// Crear middleware
router.post('/middleware', authenticateToken, (req, res) => {
  try {
    const middlewareData = req.body;
    
    if (!middlewareData.name || !middlewareData.type || !middlewareData.config) {
      return res.status(400).json({ 
        error: 'Missing required fields: name, type, config' 
      });
    }
    
    const middlewareId = advancedAPIGatewayService.createMiddleware(middlewareData);
    
    res.status(201).json({
      success: true,
      data: { id: middlewareId },
      message: 'API middleware created successfully'
    });
  } catch (error) {
    console.error('Error creating API middleware:', error);
    res.status(500).json({ error: 'Failed to create API middleware' });
  }
});

// Obtener métricas
router.get('/metrics', authenticateToken, (req, res) => {
  try {
    const { routeId, limit = 100 } = req.query;
    
    let metrics = advancedAPIGatewayService.getMetrics(routeId as string);
    
    if (limit) {
      metrics = metrics.slice(0, parseInt(limit as string));
    }
    
    res.json({
      success: true,
      data: metrics,
      count: metrics.length
    });
  } catch (error) {
    console.error('Error fetching API metrics:', error);
    res.status(500).json({ error: 'Failed to fetch API metrics' });
  }
});

// Obtener logs
router.get('/logs', authenticateToken, (req, res) => {
  try {
    const { routeId, level, limit = 100 } = req.query;
    
    let logs = advancedAPIGatewayService.getLogs(routeId as string);
    
    if (level) {
      logs = logs.filter(l => l.level === level);
    }
    
    if (limit) {
      logs = logs.slice(0, parseInt(limit as string));
    }
    
    res.json({
      success: true,
      data: logs,
      count: logs.length
    });
  } catch (error) {
    console.error('Error fetching API logs:', error);
    res.status(500).json({ error: 'Failed to fetch API logs' });
  }
});

// Obtener estadísticas
router.get('/stats/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedAPIGatewayService.getStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching API gateway stats:', error);
    res.status(500).json({ error: 'Failed to fetch API gateway stats' });
  }
});

// Obtener dashboard
router.get('/dashboard/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedAPIGatewayService.getStats();
    const routes = advancedAPIGatewayService.getRoutes();
    const middleware = advancedAPIGatewayService.getMiddleware();
    const metrics = advancedAPIGatewayService.getMetrics();
    const logs = advancedAPIGatewayService.getLogs();
    
    const dashboard = {
      overview: {
        totalRoutes: stats.totalRoutes,
        activeRoutes: stats.activeRoutes,
        totalMiddleware: stats.totalMiddleware,
        totalMetrics: stats.totalMetrics,
        totalLogs: stats.totalLogs,
        averageLatency: stats.averageLatency,
        errorRate: stats.errorRate
      },
      recentRoutes: routes.slice(0, 10),
      middleware: middleware.map(m => ({
        id: m.id,
        name: m.name,
        type: m.type,
        enabled: m.enabled,
        order: m.order
      })),
      recentMetrics: metrics.slice(0, 20),
      recentLogs: logs.slice(0, 20),
      performance: {
        averageLatency: stats.averageLatency,
        errorRate: stats.errorRate,
        activeRoutes: stats.activeRoutes
      }
    };
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    console.error('Error fetching API gateway dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch API gateway dashboard' });
  }
});

// Obtener rutas por método
router.get('/routes/method/:method', authenticateToken, (req, res) => {
  try {
    const { method } = req.params;
    const { limit = 50 } = req.query;
    
    const routes = advancedAPIGatewayService.getRoutes()
      .filter(r => r.method === method.toUpperCase())
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: routes,
      count: routes.length
    });
  } catch (error) {
    console.error('Error fetching routes by method:', error);
    res.status(500).json({ error: 'Failed to fetch routes by method' });
  }
});

// Obtener rutas por estado
router.get('/routes/status/:status', authenticateToken, (req, res) => {
  try {
    const { status } = req.params;
    const { limit = 50 } = req.query;
    
    const routes = advancedAPIGatewayService.getRoutes()
      .filter(r => r.status === status)
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: routes,
      count: routes.length
    });
  } catch (error) {
    console.error('Error fetching routes by status:', error);
    res.status(500).json({ error: 'Failed to fetch routes by status' });
  }
});

// Obtener rutas activas
router.get('/routes/active', authenticateToken, (req, res) => {
  try {
    const { limit = 20 } = req.query;
    
    const routes = advancedAPIGatewayService.getRoutes()
      .filter(r => r.status === 'active')
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: routes,
      count: routes.length
    });
  } catch (error) {
    console.error('Error fetching active routes:', error);
    res.status(500).json({ error: 'Failed to fetch active routes' });
  }
});

// Obtener middleware por tipo
router.get('/middleware/type/:type', authenticateToken, (req, res) => {
  try {
    const { type } = req.params;
    
    const middleware = advancedAPIGatewayService.getMiddleware()
      .filter(m => m.type === type);
    
    res.json({
      success: true,
      data: middleware,
      count: middleware.length
    });
  } catch (error) {
    console.error('Error fetching middleware by type:', error);
    res.status(500).json({ error: 'Failed to fetch middleware by type' });
  }
});

// Obtener middleware habilitado
router.get('/middleware/enabled', authenticateToken, (req, res) => {
  try {
    const middleware = advancedAPIGatewayService.getMiddleware()
      .filter(m => m.enabled)
      .sort((a, b) => a.order - b.order);
    
    res.json({
      success: true,
      data: middleware,
      count: middleware.length
    });
  } catch (error) {
    console.error('Error fetching enabled middleware:', error);
    res.status(500).json({ error: 'Failed to fetch enabled middleware' });
  }
});

// Obtener métricas por ruta
router.get('/routes/:id/metrics', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const { limit = 100 } = req.query;
    
    const metrics = advancedAPIGatewayService.getMetrics(id)
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: metrics,
      count: metrics.length
    });
  } catch (error) {
    console.error('Error fetching route metrics:', error);
    res.status(500).json({ error: 'Failed to fetch route metrics' });
  }
});

// Obtener logs por ruta
router.get('/routes/:id/logs', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const { level, limit = 100 } = req.query;
    
    let logs = advancedAPIGatewayService.getLogs(id);
    
    if (level) {
      logs = logs.filter(l => l.level === level);
    }
    
    logs = logs.slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: logs,
      count: logs.length
    });
  } catch (error) {
    console.error('Error fetching route logs:', error);
    res.status(500).json({ error: 'Failed to fetch route logs' });
  }
});

// Obtener logs por nivel
router.get('/logs/level/:level', authenticateToken, (req, res) => {
  try {
    const { level } = req.params;
    const { limit = 100 } = req.query;
    
    const logs = advancedAPIGatewayService.getLogs()
      .filter(l => l.level === level)
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: logs,
      count: logs.length
    });
  } catch (error) {
    console.error('Error fetching logs by level:', error);
    res.status(500).json({ error: 'Failed to fetch logs by level' });
  }
});

// Obtener logs de error
router.get('/logs/errors', authenticateToken, (req, res) => {
  try {
    const { limit = 50 } = req.query;
    
    const logs = advancedAPIGatewayService.getLogs()
      .filter(l => l.level === 'error')
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: logs,
      count: logs.length
    });
  } catch (error) {
    console.error('Error fetching error logs:', error);
    res.status(500).json({ error: 'Failed to fetch error logs' });
  }
});

// Validar ruta
router.post('/routes/validate', authenticateToken, (req, res) => {
  try {
    const { name, path, method, target, authentication, authorization } = req.body;
    
    if (!name || !path || !method || !target) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    
    // Simular validación de ruta
    const validation = {
      valid: true,
      errors: [],
      warnings: [],
      suggestions: []
    };
    
    // Validar método HTTP
    const validMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'];
    if (!validMethods.includes(method.toUpperCase())) {
      validation.errors.push(`Invalid HTTP method. Must be one of: ${validMethods.join(', ')}`);
    }
    
    // Validar path
    if (!path.startsWith('/')) {
      validation.errors.push('Path must start with /');
    }
    
    // Validar target
    if (!target.type || !target.endpoint) {
      validation.errors.push('Target type and endpoint are required');
    }
    
    // Validar autenticación
    if (authentication && authentication.required && !authentication.type) {
      validation.errors.push('Authentication type is required when authentication is enabled');
    }
    
    // Validar autorización
    if (authorization && authorization.required && (!authorization.roles || authorization.roles.length === 0)) {
      validation.errors.push('At least one role is required when authorization is enabled');
    }
    
    // Sugerencias
    if (path.includes(' ')) {
      validation.suggestions.push('Consider using hyphens instead of spaces in path');
    }
    
    if (method === 'GET' && authentication && authentication.required) {
      validation.suggestions.push('Consider if GET requests really need authentication');
    }
    
    res.json({
      success: true,
      data: validation
    });
  } catch (error) {
    console.error('Error validating route:', error);
    res.status(500).json({ error: 'Failed to validate route' });
  }
});

export default router;





