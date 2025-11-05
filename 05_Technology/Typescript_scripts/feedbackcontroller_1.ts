import { Request, Response } from 'express';
import { customerFeedbackService } from '../services/customerFeedbackService';
import { dataIntegrationService } from '../services/dataIntegrationService';
import { feedbackAnalyticsService } from '../services/feedbackAnalyticsService';

export class FeedbackController {
  // Procesar feedback individual
  static async processFeedback(req: Request, res: Response) {
    try {
      const feedbackData = req.body;
      
      if (!feedbackData.content) {
        return res.status(400).json({ error: 'Content is required' });
      }

      const feedback = await customerFeedbackService.processFeedback(feedbackData);
      
      res.status(201).json({
        success: true,
        data: feedback,
        message: 'Feedback processed successfully'
      });
    } catch (error) {
      console.error('Error processing feedback:', error);
      res.status(500).json({ error: 'Failed to process feedback' });
    }
  }

  // Procesar feedback en lote
  static async processBatchFeedback(req: Request, res: Response) {
    try {
      const { feedbackList } = req.body;
      
      if (!Array.isArray(feedbackList)) {
        return res.status(400).json({ error: 'feedbackList must be an array' });
      }

      const results = [];
      const errors = [];

      for (const feedbackData of feedbackList) {
        try {
          const feedback = await customerFeedbackService.processFeedback(feedbackData);
          results.push(feedback);
        } catch (error) {
          errors.push({
            data: feedbackData,
            error: error instanceof Error ? error.message : 'Unknown error'
          });
        }
      }

      res.json({
        success: true,
        data: {
          processed: results.length,
          errors: errors.length,
          results,
          errors
        },
        message: `Processed ${results.length} feedback items with ${errors.length} errors`
      });
    } catch (error) {
      console.error('Error processing batch feedback:', error);
      res.status(500).json({ error: 'Failed to process batch feedback' });
    }
  }

  // Obtener feedback por criterios
  static async getFeedbackByCriteria(req: Request, res: Response) {
    try {
      const {
        source,
        sentiment,
        region,
        language,
        dateFrom,
        dateTo,
        limit
      } = req.query;

      const criteria: any = {};
      
      if (source) criteria.source = source;
      if (sentiment) criteria.sentiment = sentiment;
      if (region) criteria.region = region;
      if (language) criteria.language = language;
      if (dateFrom) criteria.dateFrom = new Date(dateFrom as string);
      if (dateTo) criteria.dateTo = new Date(dateTo as string);
      if (limit) criteria.limit = parseInt(limit as string);

      const feedback = await customerFeedbackService.getFeedbackByCriteria(criteria);
      
      res.json({
        success: true,
        data: feedback,
        count: feedback.length
      });
    } catch (error) {
      console.error('Error searching feedback:', error);
      res.status(500).json({ error: 'Failed to search feedback' });
    }
  }

  // Obtener analytics de feedback
  static async getFeedbackAnalytics(req: Request, res: Response) {
    try {
      const { period = '30d' } = req.query;
      
      const analytics = await customerFeedbackService.getFeedbackAnalytics(period as string);
      
      res.json({
        success: true,
        data: analytics,
        period
      });
    } catch (error) {
      console.error('Error fetching feedback analytics:', error);
      res.status(500).json({ error: 'Failed to fetch feedback analytics' });
    }
  }

  // Obtener dashboard de métricas
  static async getDashboardMetrics(req: Request, res: Response) {
    try {
      const metrics = await feedbackAnalyticsService.getDashboardMetrics();
      
      res.json({
        success: true,
        data: metrics
      });
    } catch (error) {
      console.error('Error fetching dashboard metrics:', error);
      res.status(500).json({ error: 'Failed to fetch dashboard metrics' });
    }
  }

  // Obtener analytics avanzados
  static async getAdvancedAnalytics(req: Request, res: Response) {
    try {
      const { period = '30d' } = req.query;
      
      const analytics = await feedbackAnalyticsService.getAdvancedAnalytics(period as string);
      
      res.json({
        success: true,
        data: analytics,
        period
      });
    } catch (error) {
      console.error('Error fetching advanced analytics:', error);
      res.status(500).json({ error: 'Failed to fetch advanced analytics' });
    }
  }

  // Obtener insights por región
  static async getRegionalInsights(req: Request, res: Response) {
    try {
      const { region } = req.params;
      const { period = '30d' } = req.query;
      
      const analytics = await feedbackAnalyticsService.getAdvancedAnalytics(period as string);
      const regionalInsights = analytics.regionalAnalysis.find(ra => ra.region === region);
      
      if (!regionalInsights) {
        return res.status(404).json({ error: 'No insights found for this region' });
      }

      res.json({
        success: true,
        data: regionalInsights,
        region,
        period
      });
    } catch (error) {
      console.error('Error fetching regional insights:', error);
      res.status(500).json({ error: 'Failed to fetch regional insights' });
    }
  }

  // Obtener recomendaciones de IA
  static async getAIRecommendations(req: Request, res: Response) {
    try {
      const { period = '30d', priority } = req.query;
      
      const analytics = await feedbackAnalyticsService.getAdvancedAnalytics(period as string);
      let recommendations = analytics.aiRecommendations;
      
      if (priority && ['high', 'medium', 'low'].includes(priority as string)) {
        recommendations = recommendations.filter(rec => rec.priority === priority);
      }
      
      res.json({
        success: true,
        data: recommendations,
        period,
        priority
      });
    } catch (error) {
      console.error('Error fetching AI recommendations:', error);
      res.status(500).json({ error: 'Failed to fetch AI recommendations' });
    }
  }

  // Configurar fuente de datos
  static async configureDataSource(req: Request, res: Response) {
    try {
      const sourceData = req.body;
      
      if (!sourceData.name || !sourceData.type) {
        return res.status(400).json({ error: 'Name and type are required' });
      }

      const source = await dataIntegrationService.configureDataSource(sourceData);
      
      res.status(201).json({
        success: true,
        data: source,
        message: 'Data source configured successfully'
      });
    } catch (error) {
      console.error('Error configuring data source:', error);
      res.status(500).json({ error: 'Failed to configure data source' });
    }
  }

  // Sincronizar fuente de datos
  static async syncDataSource(req: Request, res: Response) {
    try {
      const { sourceId } = req.params;
      
      const job = await dataIntegrationService.syncDataSource(sourceId);
      
      res.json({
        success: true,
        data: job,
        message: 'Data synchronization started'
      });
    } catch (error) {
      console.error('Error syncing data source:', error);
      res.status(500).json({ error: 'Failed to sync data source' });
    }
  }

  // Obtener estado de integración
  static async getIntegrationStatus(req: Request, res: Response) {
    try {
      const status = await dataIntegrationService.getIntegrationStatus();
      
      res.json({
        success: true,
        data: status
      });
    } catch (error) {
      console.error('Error fetching integration status:', error);
      res.status(500).json({ error: 'Failed to fetch integration status' });
    }
  }

  // Exportar feedback
  static async exportFeedback(req: Request, res: Response) {
    try {
      const { format = 'json' } = req.params;
      const { source, sentiment, region, language, dateFrom, dateTo } = req.query;

      const criteria: any = {};
      if (source) criteria.source = source;
      if (sentiment) criteria.sentiment = sentiment;
      if (region) criteria.region = region;
      if (language) criteria.language = language;
      if (dateFrom) criteria.dateFrom = new Date(dateFrom as string);
      if (dateTo) criteria.dateTo = new Date(dateTo as string);

      const feedback = await customerFeedbackService.getFeedbackByCriteria(criteria);

      if (format === 'csv') {
        const csv = convertToCSV(feedback);
        res.setHeader('Content-Type', 'text/csv');
        res.setHeader('Content-Disposition', 'attachment; filename=feedback_export.csv');
        res.send(csv);
      } else if (format === 'json') {
        res.setHeader('Content-Type', 'application/json');
        res.setHeader('Content-Disposition', 'attachment; filename=feedback_export.json');
        res.json(feedback);
      } else {
        return res.status(400).json({ error: 'Unsupported format. Use csv or json' });
      }
    } catch (error) {
      console.error('Error exporting feedback:', error);
      res.status(500).json({ error: 'Failed to export feedback' });
    }
  }

  // Generar reporte completo
  static async generateReport(req: Request, res: Response) {
    try {
      const { period = '30d', format = 'json' } = req.query;
      
      const analytics = await feedbackAnalyticsService.getAdvancedAnalytics(period as string);
      const metrics = await feedbackAnalyticsService.getDashboardMetrics();
      
      const report = {
        period,
        generatedAt: new Date(),
        analytics,
        metrics,
        summary: {
          totalInsights: analytics.aiRecommendations.length,
          totalAlerts: metrics.alerts.length,
          totalActions: metrics.quickActions.length,
          cacheStatus: feedbackAnalyticsService.getCacheStats()
        }
      };

      if (format === 'csv') {
        const csv = convertReportToCSV(report);
        res.setHeader('Content-Type', 'text/csv');
        res.setHeader('Content-Disposition', 'attachment; filename=feedback_report.csv');
        res.send(csv);
      } else {
        res.json({
          success: true,
          data: report
        });
      }
    } catch (error) {
      console.error('Error generating report:', error);
      res.status(500).json({ error: 'Failed to generate report' });
    }
  }

  // Obtener feedback por ID
  static async getFeedbackById(req: Request, res: Response) {
    try {
      const { feedbackId } = req.params;
      const feedback = await customerFeedbackService.getFeedbackById(feedbackId);
      
      if (!feedback) {
        return res.status(404).json({ error: 'Feedback not found' });
      }

      res.json({
        success: true,
        data: feedback
      });
    } catch (error) {
      console.error('Error fetching feedback:', error);
      res.status(500).json({ error: 'Failed to fetch feedback' });
    }
  }

  // Actualizar feedback
  static async updateFeedback(req: Request, res: Response) {
    try {
      const { feedbackId } = req.params;
      const updates = req.body;
      
      const updatedFeedback = await customerFeedbackService.updateFeedback(feedbackId, updates);
      
      if (!updatedFeedback) {
        return res.status(404).json({ error: 'Feedback not found' });
      }

      res.json({
        success: true,
        data: updatedFeedback,
        message: 'Feedback updated successfully'
      });
    } catch (error) {
      console.error('Error updating feedback:', error);
      res.status(500).json({ error: 'Failed to update feedback' });
    }
  }

  // Eliminar feedback
  static async deleteFeedback(req: Request, res: Response) {
    try {
      const { feedbackId } = req.params;
      const deleted = await customerFeedbackService.deleteFeedback(feedbackId);
      
      if (!deleted) {
        return res.status(404).json({ error: 'Feedback not found' });
      }

      res.json({
        success: true,
        message: 'Feedback deleted successfully'
      });
    } catch (error) {
      console.error('Error deleting feedback:', error);
      res.status(500).json({ error: 'Failed to delete feedback' });
    }
  }

  // Obtener alertas
  static async getAlerts(req: Request, res: Response) {
    try {
      const metrics = await feedbackAnalyticsService.getDashboardMetrics();
      
      res.json({
        success: true,
        data: metrics.alerts
      });
    } catch (error) {
      console.error('Error fetching alerts:', error);
      res.status(500).json({ error: 'Failed to fetch alerts' });
    }
  }

  // Obtener acciones rápidas
  static async getQuickActions(req: Request, res: Response) {
    try {
      const metrics = await feedbackAnalyticsService.getDashboardMetrics();
      
      res.json({
        success: true,
        data: metrics.quickActions
      });
    } catch (error) {
      console.error('Error fetching quick actions:', error);
      res.status(500).json({ error: 'Failed to fetch quick actions' });
    }
  }

  // Limpiar caché
  static async clearCache(req: Request, res: Response) {
    try {
      feedbackAnalyticsService.clearCache();
      
      res.json({
        success: true,
        message: 'Cache cleared successfully'
      });
    } catch (error) {
      console.error('Error clearing cache:', error);
      res.status(500).json({ error: 'Failed to clear cache' });
    }
  }
}

// Funciones auxiliares
function convertToCSV(feedback: any[]): string {
  if (feedback.length === 0) return '';

  const headers = [
    'ID', 'Source', 'Platform', 'Content', 'Sentiment', 'Sentiment Score',
    'Language', 'Region', 'User ID', 'Course ID', 'Webinar ID',
    'Rating', 'Tags', 'Categories', 'Urgency', 'Response Required',
    'AI Insights', 'Emotional Tone', 'Cultural Context', 'Timestamp'
  ];

  const rows = feedback.map(f => [
    f.id,
    f.source,
    f.platform,
    `"${f.content.replace(/"/g, '""')}"`, // Escapar comillas
    f.sentiment,
    f.sentimentScore,
    f.language,
    f.region,
    f.userId || '',
    f.courseId || '',
    f.webinarId || '',
    f.metadata.rating || '',
    f.metadata.tags?.join(';') || '',
    f.metadata.categories?.join(';') || '',
    f.metadata.urgency || '',
    f.metadata.responseRequired || false,
    f.metadata.aiInsights?.join(';') || '',
    f.metadata.emotionalTone || '',
    f.metadata.culturalContext || '',
    f.timestamp.toISOString()
  ]);

  return [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
}

function convertReportToCSV(report: any): string {
  const headers = ['Metric', 'Value', 'Period', 'Generated At'];
  const rows = [
    ['Total Insights', report.summary.totalInsights, report.period, report.generatedAt],
    ['Total Alerts', report.summary.totalAlerts, report.period, report.generatedAt],
    ['Total Actions', report.summary.totalActions, report.period, report.generatedAt]
  ];

  return [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
}
