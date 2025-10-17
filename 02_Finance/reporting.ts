import express from 'express';
import { reportingService } from '../services/reportingService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener reportes
router.get('/', authenticateToken, (req, res) => {
  try {
    const reports = reportingService.getReports();
    
    res.json({
      success: true,
      data: reports,
      count: reports.length
    });
  } catch (error) {
    console.error('Error fetching reports:', error);
    res.status(500).json({ error: 'Failed to fetch reports' });
  }
});

// Obtener reporte específico
router.get('/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const report = reportingService.getReport(id);
    
    if (!report) {
      return res.status(404).json({ error: 'Report not found' });
    }
    
    res.json({
      success: true,
      data: report
    });
  } catch (error) {
    console.error('Error fetching report:', error);
    res.status(500).json({ error: 'Failed to fetch report' });
  }
});

// Crear reporte
router.post('/', authenticateToken, (req, res) => {
  try {
    const reportData = req.body;
    
    // Validar datos requeridos
    if (!reportData.name || !reportData.type || !reportData.metrics) {
      return res.status(400).json({ 
        error: 'Missing required fields: name, type, metrics' 
      });
    }
    
    const reportId = reportingService.createReport(reportData);
    
    res.status(201).json({
      success: true,
      data: { id: reportId },
      message: 'Report created successfully'
    });
  } catch (error) {
    console.error('Error creating report:', error);
    res.status(500).json({ error: 'Failed to create report' });
  }
});

// Actualizar reporte
router.put('/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;
    
    const updated = reportingService.updateReport(id, updates);
    
    if (!updated) {
      return res.status(404).json({ error: 'Report not found' });
    }
    
    res.json({
      success: true,
      message: 'Report updated successfully'
    });
  } catch (error) {
    console.error('Error updating report:', error);
    res.status(500).json({ error: 'Failed to update report' });
  }
});

// Eliminar reporte
router.delete('/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    
    const deleted = reportingService.deleteReport(id);
    
    if (!deleted) {
      return res.status(404).json({ error: 'Report not found' });
    }
    
    res.json({
      success: true,
      message: 'Report deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting report:', error);
    res.status(500).json({ error: 'Failed to delete report' });
  }
});

// Generar reporte
router.post('/:id/generate', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const { triggeredBy = 'manual' } = req.body;
    
    const report = reportingService.getReport(id);
    if (!report) {
      return res.status(404).json({ error: 'Report not found' });
    }
    
    if (!report.enabled) {
      return res.status(400).json({ error: 'Report is disabled' });
    }
    
    // Iniciar generación asíncrona
    reportingService.generateReport(id, triggeredBy)
      .then(generationId => {
        res.json({
          success: true,
          data: { generationId },
          message: 'Report generation initiated successfully'
        });
      })
      .catch(error => {
        res.status(500).json({ error: 'Failed to generate report' });
      });
  } catch (error) {
    console.error('Error generating report:', error);
    res.status(500).json({ error: 'Failed to generate report' });
  }
});

// Obtener generaciones de reporte
router.get('/:id/generations', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const { limit } = req.query;
    
    const report = reportingService.getReport(id);
    if (!report) {
      return res.status(404).json({ error: 'Report not found' });
    }
    
    const generations = reportingService.getGenerations(limit ? parseInt(limit as string) : undefined)
      .filter(gen => gen.reportId === id);
    
    res.json({
      success: true,
      data: generations,
      count: generations.length
    });
  } catch (error) {
    console.error('Error fetching report generations:', error);
    res.status(500).json({ error: 'Failed to fetch report generations' });
  }
});

// Obtener todas las generaciones
router.get('/generations/all', authenticateToken, (req, res) => {
  try {
    const { limit = 50, status } = req.query;
    
    let generations = reportingService.getGenerations(parseInt(limit as string));
    
    if (status) {
      generations = generations.filter(gen => gen.status === status);
    }
    
    res.json({
      success: true,
      data: generations,
      count: generations.length
    });
  } catch (error) {
    console.error('Error fetching generations:', error);
    res.status(500).json({ error: 'Failed to fetch generations' });
  }
});

// Obtener estadísticas de reportes
router.get('/stats/overview', authenticateToken, (req, res) => {
  try {
    const stats = reportingService.getStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching report stats:', error);
    res.status(500).json({ error: 'Failed to fetch report stats' });
  }
});

// Obtener plantillas de reporte
router.get('/templates/list', authenticateToken, (req, res) => {
  try {
    const templates = [
      {
        id: 'feedback_summary_template',
        name: 'Feedback Summary Report',
        description: 'Comprehensive summary of customer feedback data',
        type: 'analytics',
        category: 'feedback',
        features: ['Sentiment Analysis', 'Trend Analysis', 'Regional Breakdown'],
        metrics: [
          'total_feedback',
          'sentiment_distribution',
          'urgency_distribution',
          'regional_breakdown',
          'source_breakdown',
          'trends'
        ],
        visualizations: [
          { type: 'pie', title: 'Sentiment Distribution' },
          { type: 'line', title: 'Trends Over Time' },
          { type: 'bar', title: 'Regional Breakdown' }
        ],
        formats: ['pdf', 'excel', 'html']
      },
      {
        id: 'insights_report_template',
        name: 'AI Insights Report',
        description: 'Report of AI-generated insights and recommendations',
        type: 'insights',
        category: 'ai',
        features: ['Trend Detection', 'Anomaly Analysis', 'Opportunity Identification'],
        metrics: [
          'total_insights',
          'insight_types',
          'trends_detected',
          'anomalies_found',
          'opportunities_identified'
        ],
        visualizations: [
          { type: 'metric', title: 'Insights Overview' },
          { type: 'heatmap', title: 'Trends Heatmap' },
          { type: 'scatter', title: 'Anomaly Detection' }
        ],
        formats: ['pdf', 'html', 'json']
      },
      {
        id: 'automation_performance_template',
        name: 'Automation Performance Report',
        description: 'Report on automation rules performance and effectiveness',
        type: 'automation',
        category: 'automation',
        features: ['Execution Statistics', 'Rule Performance', 'Error Analysis'],
        metrics: [
          'total_executions',
          'success_rate',
          'average_execution_time',
          'rule_performance',
          'error_analysis'
        ],
        visualizations: [
          { type: 'line', title: 'Execution Trends' },
          { type: 'bar', title: 'Rule Performance' },
          { type: 'gauge', title: 'Success Rate' }
        ],
        formats: ['excel', 'pdf', 'csv']
      },
      {
        id: 'integration_status_template',
        name: 'Integration Status Report',
        description: 'Report on integration performance and sync status',
        type: 'integration',
        category: 'integration',
        features: ['Sync Statistics', 'Error Analysis', 'Performance Metrics'],
        metrics: [
          'total_syncs',
          'successful_syncs',
          'failed_syncs',
          'average_sync_time',
          'integration_status'
        ],
        visualizations: [
          { type: 'table', title: 'Integration Status' },
          { type: 'line', title: 'Sync Trends' },
          { type: 'pie', title: 'Success Rate Distribution' }
        ],
        formats: ['excel', 'pdf', 'html']
      },
      {
        id: 'executive_summary_template',
        name: 'Executive Summary Report',
        description: 'High-level executive summary of key metrics and insights',
        type: 'dashboard',
        category: 'executive',
        features: ['Key Metrics', 'Strategic Insights', 'Recommendations'],
        metrics: [
          'customer_satisfaction',
          'feedback_volume',
          'trend_analysis',
          'key_insights',
          'strategic_recommendations'
        ],
        visualizations: [
          { type: 'metric', title: 'Key Performance Indicators' },
          { type: 'trend', title: 'Satisfaction Trends' },
          { type: 'table', title: 'Top Insights' }
        ],
        formats: ['pdf', 'html']
      }
    ];
    
    res.json({
      success: true,
      data: templates,
      count: templates.length
    });
  } catch (error) {
    console.error('Error fetching report templates:', error);
    res.status(500).json({ error: 'Failed to fetch report templates' });
  }
});

// Crear reporte desde plantilla
router.post('/from-template', authenticateToken, (req, res) => {
  try {
    const { templateId, customizations = {} } = req.body;
    
    if (!templateId) {
      return res.status(400).json({ error: 'Template ID is required' });
    }
    
    // Obtener plantilla (en implementación real, desde base de datos)
    const templates = [
      {
        id: 'feedback_summary_template',
        name: 'Feedback Summary Report',
        description: 'Comprehensive summary of customer feedback data',
        type: 'analytics',
        enabled: true,
        schedule: {
          frequency: 'daily',
          time: '08:00'
        },
        filters: [],
        metrics: [
          'total_feedback',
          'sentiment_distribution',
          'urgency_distribution',
          'regional_breakdown',
          'source_breakdown',
          'trends'
        ],
        visualizations: [
          {
            id: 'sentiment_chart',
            type: 'pie',
            title: 'Sentiment Distribution',
            data: {},
            config: { colors: ['#28a745', '#ffc107', '#dc3545'] },
            position: { x: 0, y: 0, width: 6, height: 4 }
          }
        ],
        recipients: [
          {
            type: 'email',
            address: 'team@company.com',
            name: 'Feedback Team',
            enabled: true
          }
        ],
        format: 'pdf'
      }
    ];
    
    const template = templates.find(t => t.id === templateId);
    if (!template) {
      return res.status(404).json({ error: 'Template not found' });
    }
    
    // Aplicar personalizaciones
    const reportData = {
      ...template,
      ...customizations,
      name: customizations.name || template.name,
      description: customizations.description || template.description
    };
    
    const reportId = reportingService.createReport(reportData);
    
    res.status(201).json({
      success: true,
      data: { id: reportId },
      message: 'Report created from template successfully'
    });
  } catch (error) {
    console.error('Error creating report from template:', error);
    res.status(500).json({ error: 'Failed to create report from template' });
  }
});

// Obtener dashboard de reportes
router.get('/dashboard/overview', authenticateToken, (req, res) => {
  try {
    const stats = reportingService.getStats();
    const reports = reportingService.getReports();
    const recentGenerations = reportingService.getGenerations(10);
    
    const dashboard = {
      overview: {
        totalReports: stats.totalReports,
        enabledReports: stats.enabledReports,
        totalGenerations: stats.totalGenerations,
        successRate: stats.totalGenerations > 0 
          ? (stats.successfulGenerations / stats.totalGenerations) * 100 
          : 0,
        averageGenerationTime: stats.averageGenerationTime
      },
      reports: reports.map(report => ({
        id: report.id,
        name: report.name,
        type: report.type,
        enabled: report.enabled,
        schedule: report.schedule,
        lastGenerated: report.lastGenerated,
        generationCount: report.generationCount
      })),
      recentActivity: recentGenerations,
      performance: {
        totalGenerations: stats.totalGenerations,
        successfulGenerations: stats.successfulGenerations,
        failedGenerations: stats.failedGenerations,
        successRate: stats.totalGenerations > 0 
          ? (stats.successfulGenerations / stats.totalGenerations) * 100 
          : 0
      }
    };
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    console.error('Error fetching reports dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch reports dashboard' });
  }
});

// Obtener logs de generación
router.get('/logs/generations', authenticateToken, (req, res) => {
  try {
    const { reportId, status, limit = 50 } = req.query;
    
    let generations = reportingService.getGenerations(parseInt(limit as string));
    
    if (reportId) {
      generations = generations.filter(gen => gen.reportId === reportId);
    }
    
    if (status) {
      generations = generations.filter(gen => gen.status === status);
    }
    
    res.json({
      success: true,
      data: generations,
      count: generations.length
    });
  } catch (error) {
    console.error('Error fetching generation logs:', error);
    res.status(500).json({ error: 'Failed to fetch generation logs' });
  }
});

// Validar configuración de reporte
router.post('/validate', authenticateToken, (req, res) => {
  try {
    const { type, metrics, visualizations, schedule } = req.body;
    
    if (!type || !metrics) {
      return res.status(400).json({ error: 'Type and metrics are required' });
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
      case 'analytics':
        if (!metrics.includes('total_feedback')) {
          validation.warnings.push('Consider including total_feedback metric for analytics reports');
        }
        break;
      case 'insights':
        if (!metrics.includes('total_insights')) {
          validation.warnings.push('Consider including total_insights metric for insights reports');
        }
        break;
      case 'automation':
        if (!metrics.includes('total_executions')) {
          validation.warnings.push('Consider including total_executions metric for automation reports');
        }
        break;
      default:
        validation.warnings.push(`Unknown report type: ${type}`);
    }
    
    // Validar visualizaciones
    if (visualizations && visualizations.length === 0) {
      validation.warnings.push('Consider adding visualizations to make the report more informative');
    }
    
    // Validar programación
    if (schedule && !schedule.frequency) {
      validation.errors.push('Schedule frequency is required when schedule is specified');
    }
    
    res.json({
      success: true,
      data: validation
    });
  } catch (error) {
    console.error('Error validating report configuration:', error);
    res.status(500).json({ error: 'Failed to validate report configuration' });
  }
});

export default router;






