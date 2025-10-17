import express from 'express';
import { customerFeedbackService } from '../services/customerFeedbackService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Procesar nuevo feedback
router.post('/process', authenticateToken, async (req, res) => {
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
});

// Obtener analytics de feedback
router.get('/analytics', authenticateToken, async (req, res) => {
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
});

// Obtener feedback por criterios
router.get('/search', authenticateToken, async (req, res) => {
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
});

// Obtener feedback por ID
router.get('/:feedbackId', authenticateToken, async (req, res) => {
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
});

// Actualizar feedback
router.put('/:feedbackId', authenticateToken, async (req, res) => {
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
});

// Eliminar feedback
router.delete('/:feedbackId', authenticateToken, async (req, res) => {
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
});

// Obtener insights de feedback por región
router.get('/insights/region/:region', authenticateToken, async (req, res) => {
  try {
    const { region } = req.params;
    const { period = '30d' } = req.query;
    
    const analytics = await customerFeedbackService.getFeedbackAnalytics(period as string);
    const regionalInsights = analytics.culturalInsights.find(ci => ci.region === region);
    
    if (!regionalInsights) {
      return res.status(404).json({ error: 'No insights found for this region' });
    }

    res.json({
      success: true,
      data: regionalInsights,
      region
    });
  } catch (error) {
    console.error('Error fetching regional insights:', error);
    res.status(500).json({ error: 'Failed to fetch regional insights' });
  }
});

// Obtener temas principales
router.get('/insights/themes', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    const analytics = await customerFeedbackService.getFeedbackAnalytics(period as string);
    
    res.json({
      success: true,
      data: analytics.topThemes,
      period
    });
  } catch (error) {
    console.error('Error fetching themes:', error);
    res.status(500).json({ error: 'Failed to fetch themes' });
  }
});

// Obtener recomendaciones de IA
router.get('/insights/recommendations', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    const analytics = await customerFeedbackService.getFeedbackAnalytics(period as string);
    
    res.json({
      success: true,
      data: analytics.aiRecommendations,
      period
    });
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    res.status(500).json({ error: 'Failed to fetch recommendations' });
  }
});

// Obtener análisis de tendencias
router.get('/insights/trends', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    const analytics = await customerFeedbackService.getFeedbackAnalytics(period as string);
    
    res.json({
      success: true,
      data: analytics.trendAnalysis,
      period
    });
  } catch (error) {
    console.error('Error fetching trends:', error);
    res.status(500).json({ error: 'Failed to fetch trends' });
  }
});

// Procesar feedback en lote
router.post('/batch-process', authenticateToken, async (req, res) => {
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
});

// Exportar feedback
router.get('/export/:format', authenticateToken, async (req, res) => {
  try {
    const { format } = req.params;
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
});

// Función auxiliar para convertir a CSV
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

export default router;



