import express from 'express';
import { advancedDataVisualizationService } from '../services/advancedDataVisualizationService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener visualizaciones
router.get('/visualizations', authenticateToken, (req, res) => {
  try {
    const { type, chartType, limit = 50 } = req.query;
    
    let visualizations = advancedDataVisualizationService.getVisualizations();
    
    if (type) {
      visualizations = visualizations.filter(v => v.type === type);
    }
    
    if (chartType) {
      visualizations = visualizations.filter(v => v.chartType === chartType);
    }
    
    if (limit) {
      visualizations = visualizations.slice(0, parseInt(limit as string));
    }
    
    res.json({
      success: true,
      data: visualizations,
      count: visualizations.length
    });
  } catch (error) {
    console.error('Error fetching visualizations:', error);
    res.status(500).json({ error: 'Failed to fetch visualizations' });
  }
});

// Crear visualización
router.post('/visualizations', authenticateToken, (req, res) => {
  try {
    const visualizationData = req.body;
    
    if (!visualizationData.name || !visualizationData.type || !visualizationData.chartType) {
      return res.status(400).json({ 
        error: 'Missing required fields: name, type, chartType' 
      });
    }
    
    const visualizationId = advancedDataVisualizationService.createVisualization(visualizationData);
    
    res.status(201).json({
      success: true,
      data: { id: visualizationId },
      message: 'Visualization created successfully'
    });
  } catch (error) {
    console.error('Error creating visualization:', error);
    res.status(500).json({ error: 'Failed to create visualization' });
  }
});

// Obtener visualización específica
router.get('/visualizations/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const visualizations = advancedDataVisualizationService.getVisualizations();
    const visualization = visualizations.find(v => v.id === id);
    
    if (!visualization) {
      return res.status(404).json({ error: 'Visualization not found' });
    }
    
    res.json({
      success: true,
      data: visualization
    });
  } catch (error) {
    console.error('Error fetching visualization:', error);
    res.status(500).json({ error: 'Failed to fetch visualization' });
  }
});

// Obtener datos de visualización
router.get('/visualizations/:id/data', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const data = advancedDataVisualizationService.getVisualizationData(id);
    
    if (!data) {
      return res.status(404).json({ error: 'Visualization data not found' });
    }
    
    res.json({
      success: true,
      data: data
    });
  } catch (error) {
    console.error('Error fetching visualization data:', error);
    res.status(500).json({ error: 'Failed to fetch visualization data' });
  }
});

// Obtener dashboards
router.get('/dashboards', authenticateToken, (req, res) => {
  try {
    const { limit = 50 } = req.query;
    
    let dashboards = advancedDataVisualizationService.getDashboards();
    
    if (limit) {
      dashboards = dashboards.slice(0, parseInt(limit as string));
    }
    
    res.json({
      success: true,
      data: dashboards,
      count: dashboards.length
    });
  } catch (error) {
    console.error('Error fetching dashboards:', error);
    res.status(500).json({ error: 'Failed to fetch dashboards' });
  }
});

// Crear dashboard
router.post('/dashboards', authenticateToken, (req, res) => {
  try {
    const dashboardData = req.body;
    
    if (!dashboardData.name || !dashboardData.layout) {
      return res.status(400).json({ 
        error: 'Missing required fields: name, layout' 
      });
    }
    
    const dashboardId = advancedDataVisualizationService.createDashboard(dashboardData);
    
    res.status(201).json({
      success: true,
      data: { id: dashboardId },
      message: 'Dashboard created successfully'
    });
  } catch (error) {
    console.error('Error creating dashboard:', error);
    res.status(500).json({ error: 'Failed to create dashboard' });
  }
});

// Obtener dashboard específico
router.get('/dashboards/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const dashboards = advancedDataVisualizationService.getDashboards();
    const dashboard = dashboards.find(d => d.id === id);
    
    if (!dashboard) {
      return res.status(404).json({ error: 'Dashboard not found' });
    }
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    console.error('Error fetching dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch dashboard' });
  }
});

// Obtener templates
router.get('/templates', authenticateToken, (req, res) => {
  try {
    const { category, type, limit = 50 } = req.query;
    
    let templates = advancedDataVisualizationService.getTemplates();
    
    if (category) {
      templates = templates.filter(t => t.category === category);
    }
    
    if (type) {
      templates = templates.filter(t => t.type === type);
    }
    
    if (limit) {
      templates = templates.slice(0, parseInt(limit as string));
    }
    
    res.json({
      success: true,
      data: templates,
      count: templates.length
    });
  } catch (error) {
    console.error('Error fetching templates:', error);
    res.status(500).json({ error: 'Failed to fetch templates' });
  }
});

// Obtener template específico
router.get('/templates/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const templates = advancedDataVisualizationService.getTemplates();
    const template = templates.find(t => t.id === id);
    
    if (!template) {
      return res.status(404).json({ error: 'Template not found' });
    }
    
    res.json({
      success: true,
      data: template
    });
  } catch (error) {
    console.error('Error fetching template:', error);
    res.status(500).json({ error: 'Failed to fetch template' });
  }
});

// Crear visualización desde template
router.post('/visualizations/from-template', authenticateToken, (req, res) => {
  try {
    const { templateId, customizations = {} } = req.body;
    
    if (!templateId) {
      return res.status(400).json({ error: 'Template ID is required' });
    }
    
    // Obtener template (en implementación real, desde base de datos)
    const templates = [
      {
        id: 'line_chart_template',
        name: 'Line Chart',
        description: 'Template for creating line charts',
        type: 'chart',
        chartType: 'line',
        config: {
          type: 'chart',
          chartType: 'line',
          dataSource: {
            type: 'api',
            endpoint: '/api/data'
          },
          dimensions: {
            x: 'date',
            y: 'value'
          },
          styling: {
            theme: 'light',
            colors: ['#3498db', '#e74c3c', '#2ecc71', '#f39c12'],
            fonts: {
              family: 'Arial',
              size: 12,
              weight: 'normal'
            },
            layout: {
              width: 800,
              height: 400,
              margin: { top: 20, right: 30, bottom: 40, left: 50 }
            },
            axes: {
              x: {
                title: 'Date',
                ticks: 10,
                format: '%Y-%m-%d',
                gridLines: true,
                labels: true
              },
              y: {
                title: 'Value',
                ticks: 8,
                format: '.2f',
                gridLines: true,
                labels: true
              }
            },
            legend: {
              enabled: true,
              position: 'top',
              orientation: 'horizontal'
            },
            tooltip: {
              enabled: true,
              format: '{x}: {y}'
            }
          },
          interactions: [
            { type: 'zoom', enabled: true, config: {} },
            { type: 'pan', enabled: true, config: {} },
            { type: 'hover', enabled: true, config: {} }
          ],
          animations: [
            { type: 'fade', duration: 500, easing: 'ease-in-out', enabled: true, config: {} }
          ],
          responsive: true,
          realTime: false
        }
      }
    ];
    
    const template = templates.find(t => t.id === templateId);
    if (!template) {
      return res.status(404).json({ error: 'Template not found' });
    }
    
    // Aplicar personalizaciones
    const visualizationData = {
      ...template.config,
      ...customizations,
      name: customizations.name || template.name,
      description: customizations.description || template.description
    };
    
    const visualizationId = advancedDataVisualizationService.createVisualization(visualizationData);
    
    res.status(201).json({
      success: true,
      data: { id: visualizationId },
      message: 'Visualization created from template successfully'
    });
  } catch (error) {
    console.error('Error creating visualization from template:', error);
    res.status(500).json({ error: 'Failed to create visualization from template' });
  }
});

// Obtener estadísticas
router.get('/stats/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedDataVisualizationService.getStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching visualization stats:', error);
    res.status(500).json({ error: 'Failed to fetch visualization stats' });
  }
});

// Obtener dashboard
router.get('/dashboard/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedDataVisualizationService.getStats();
    const visualizations = advancedDataVisualizationService.getVisualizations();
    const dashboards = advancedDataVisualizationService.getDashboards();
    const templates = advancedDataVisualizationService.getTemplates();
    
    const dashboard = {
      overview: {
        totalVisualizations: stats.totalVisualizations,
        totalDashboards: stats.totalDashboards,
        totalTemplates: stats.totalTemplates,
        totalDataPoints: stats.totalDataPoints,
        averageDataQuality: stats.averageDataQuality,
        realTimeVisualizations: stats.realTimeVisualizations
      },
      recentVisualizations: visualizations.slice(0, 10),
      recentDashboards: dashboards.slice(0, 5),
      templates: templates.map(template => ({
        id: template.id,
        name: template.name,
        type: template.type,
        chartType: template.chartType,
        category: template.category
      })),
      performance: {
        averageDataQuality: stats.averageDataQuality,
        realTimeVisualizations: stats.realTimeVisualizations,
        totalDataPoints: stats.totalDataPoints
      }
    };
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    console.error('Error fetching visualization dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch visualization dashboard' });
  }
});

// Obtener visualizaciones por tipo
router.get('/visualizations/type/:type', authenticateToken, (req, res) => {
  try {
    const { type } = req.params;
    const { limit = 50 } = req.query;
    
    const visualizations = advancedDataVisualizationService.getVisualizations()
      .filter(v => v.type === type)
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: visualizations,
      count: visualizations.length
    });
  } catch (error) {
    console.error('Error fetching visualizations by type:', error);
    res.status(500).json({ error: 'Failed to fetch visualizations by type' });
  }
});

// Obtener visualizaciones por tipo de gráfico
router.get('/visualizations/chart-type/:chartType', authenticateToken, (req, res) => {
  try {
    const { chartType } = req.params;
    const { limit = 50 } = req.query;
    
    const visualizations = advancedDataVisualizationService.getVisualizations()
      .filter(v => v.chartType === chartType)
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: visualizations,
      count: visualizations.length
    });
  } catch (error) {
    console.error('Error fetching visualizations by chart type:', error);
    res.status(500).json({ error: 'Failed to fetch visualizations by chart type' });
  }
});

// Obtener visualizaciones en tiempo real
router.get('/visualizations/realtime', authenticateToken, (req, res) => {
  try {
    const { limit = 20 } = req.query;
    
    const visualizations = advancedDataVisualizationService.getVisualizations()
      .filter(v => v.realTime)
      .slice(0, parseInt(limit as string));
    
    res.json({
      success: true,
      data: visualizations,
      count: visualizations.length
    });
  } catch (error) {
    console.error('Error fetching real-time visualizations:', error);
    res.status(500).json({ error: 'Failed to fetch real-time visualizations' });
  }
});

// Obtener templates por categoría
router.get('/templates/category/:category', authenticateToken, (req, res) => {
  try {
    const { category } = req.params;
    
    const templates = advancedDataVisualizationService.getTemplates()
      .filter(t => t.category === category);
    
    res.json({
      success: true,
      data: templates,
      count: templates.length
    });
  } catch (error) {
    console.error('Error fetching templates by category:', error);
    res.status(500).json({ error: 'Failed to fetch templates by category' });
  }
});

// Validar visualización
router.post('/visualizations/validate', authenticateToken, (req, res) => {
  try {
    const { name, type, chartType, dataSource, dimensions } = req.body;
    
    if (!name || !type || !chartType || !dataSource || !dimensions) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    
    // Simular validación de visualización
    const validation = {
      valid: true,
      errors: [],
      warnings: [],
      suggestions: []
    };
    
    // Validar tipo de gráfico
    const validChartTypes = ['line', 'bar', 'pie', 'scatter', 'area', 'donut', 'radar', 'bubble', 'funnel', 'sankey'];
    if (!validChartTypes.includes(chartType)) {
      validation.errors.push(`Invalid chart type. Must be one of: ${validChartTypes.join(', ')}`);
    }
    
    // Validar dimensiones
    if (!dimensions.x || !dimensions.y) {
      validation.errors.push('X and Y dimensions are required');
    }
    
    // Validar fuente de datos
    if (!dataSource.type || !dataSource.endpoint) {
      validation.errors.push('Data source type and endpoint are required');
    }
    
    // Sugerencias
    if (chartType === 'line' && !dimensions.x.includes('date')) {
      validation.suggestions.push('Consider using a date field for X axis in line charts');
    }
    
    if (chartType === 'pie' && dimensions.y) {
      validation.suggestions.push('Pie charts typically don\'t use Y dimension');
    }
    
    res.json({
      success: true,
      data: validation
    });
  } catch (error) {
    console.error('Error validating visualization:', error);
    res.status(500).json({ error: 'Failed to validate visualization' });
  }
});

export default router;





