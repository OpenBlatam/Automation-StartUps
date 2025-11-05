import express from 'express';
import { dataIntegrationService } from '../services/dataIntegrationService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Configurar fuente de datos
router.post('/sources', authenticateToken, async (req, res) => {
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
});

// Obtener fuentes de datos
router.get('/sources', authenticateToken, async (req, res) => {
  try {
    const sources = await dataIntegrationService.getDataSources();
    
    res.json({
      success: true,
      data: sources,
      count: sources.length
    });
  } catch (error) {
    console.error('Error fetching data sources:', error);
    res.status(500).json({ error: 'Failed to fetch data sources' });
  }
});

// Obtener fuente de datos por ID
router.get('/sources/:sourceId', authenticateToken, async (req, res) => {
  try {
    const { sourceId } = req.params;
    const source = await dataIntegrationService.getDataSourceById(sourceId);
    
    if (!source) {
      return res.status(404).json({ error: 'Data source not found' });
    }

    res.json({
      success: true,
      data: source
    });
  } catch (error) {
    console.error('Error fetching data source:', error);
    res.status(500).json({ error: 'Failed to fetch data source' });
  }
});

// Actualizar fuente de datos
router.put('/sources/:sourceId', authenticateToken, async (req, res) => {
  try {
    const { sourceId } = req.params;
    const updates = req.body;
    
    const updatedSource = await dataIntegrationService.updateDataSource(sourceId, updates);
    
    if (!updatedSource) {
      return res.status(404).json({ error: 'Data source not found' });
    }

    res.json({
      success: true,
      data: updatedSource,
      message: 'Data source updated successfully'
    });
  } catch (error) {
    console.error('Error updating data source:', error);
    res.status(500).json({ error: 'Failed to update data source' });
  }
});

// Eliminar fuente de datos
router.delete('/sources/:sourceId', authenticateToken, async (req, res) => {
  try {
    const { sourceId } = req.params;
    const deleted = await dataIntegrationService.deleteDataSource(sourceId);
    
    if (!deleted) {
      return res.status(404).json({ error: 'Data source not found' });
    }

    res.json({
      success: true,
      message: 'Data source deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting data source:', error);
    res.status(500).json({ error: 'Failed to delete data source' });
  }
});

// Sincronizar fuente de datos
router.post('/sources/:sourceId/sync', authenticateToken, async (req, res) => {
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
});

// Obtener trabajos de integración
router.get('/jobs', authenticateToken, async (req, res) => {
  try {
    const jobs = await dataIntegrationService.getIntegrationJobs();
    
    res.json({
      success: true,
      data: jobs,
      count: jobs.length
    });
  } catch (error) {
    console.error('Error fetching integration jobs:', error);
    res.status(500).json({ error: 'Failed to fetch integration jobs' });
  }
});

// Obtener trabajo de integración por ID
router.get('/jobs/:jobId', authenticateToken, async (req, res) => {
  try {
    const { jobId } = req.params;
    const job = await dataIntegrationService.getIntegrationJobById(jobId);
    
    if (!job) {
      return res.status(404).json({ error: 'Integration job not found' });
    }

    res.json({
      success: true,
      data: job
    });
  } catch (error) {
    console.error('Error fetching integration job:', error);
    res.status(500).json({ error: 'Failed to fetch integration job' });
  }
});

// Obtener estado de integración
router.get('/status', authenticateToken, async (req, res) => {
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
});

// Sincronizar todas las fuentes activas
router.post('/sync-all', authenticateToken, async (req, res) => {
  try {
    const sources = await dataIntegrationService.getDataSources();
    const activeSources = sources.filter(s => s.status === 'active');
    
    const syncPromises = activeSources.map(source => 
      dataIntegrationService.syncDataSource(source.id)
    );
    
    const jobs = await Promise.all(syncPromises);
    
    res.json({
      success: true,
      data: jobs,
      message: `Synchronized ${jobs.length} data sources`
    });
  } catch (error) {
    console.error('Error syncing all sources:', error);
    res.status(500).json({ error: 'Failed to sync all sources' });
  }
});

// Obtener fuentes por tipo
router.get('/sources/type/:type', authenticateToken, async (req, res) => {
  try {
    const { type } = req.params;
    const sources = await dataIntegrationService.getDataSources();
    const filteredSources = sources.filter(s => s.type === type);
    
    res.json({
      success: true,
      data: filteredSources,
      count: filteredSources.length
    });
  } catch (error) {
    console.error('Error fetching sources by type:', error);
    res.status(500).json({ error: 'Failed to fetch sources by type' });
  }
});

// Obtener fuentes por región
router.get('/sources/region/:region', authenticateToken, async (req, res) => {
  try {
    const { region } = req.params;
    const sources = await dataIntegrationService.getDataSources();
    const filteredSources = sources.filter(s => s.region === region);
    
    res.json({
      success: true,
      data: filteredSources,
      count: filteredSources.length
    });
  } catch (error) {
    console.error('Error fetching sources by region:', error);
    res.status(500).json({ error: 'Failed to fetch sources by region' });
  }
});

// Obtener trabajos por estado
router.get('/jobs/status/:status', authenticateToken, async (req, res) => {
  try {
    const { status } = req.params;
    const jobs = await dataIntegrationService.getIntegrationJobs();
    const filteredJobs = jobs.filter(j => j.status === status);
    
    res.json({
      success: true,
      data: filteredJobs,
      count: filteredJobs.length
    });
  } catch (error) {
    console.error('Error fetching jobs by status:', error);
    res.status(500).json({ error: 'Failed to fetch jobs by status' });
  }
});

// Obtener trabajos por fuente
router.get('/sources/:sourceId/jobs', authenticateToken, async (req, res) => {
  try {
    const { sourceId } = req.params;
    const jobs = await dataIntegrationService.getIntegrationJobs();
    const filteredJobs = jobs.filter(j => j.sourceId === sourceId);
    
    res.json({
      success: true,
      data: filteredJobs,
      count: filteredJobs.length
    });
  } catch (error) {
    console.error('Error fetching jobs by source:', error);
    res.status(500).json({ error: 'Failed to fetch jobs by source' });
  }
});

// Obtener estadísticas de integración
router.get('/stats', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    const status = await dataIntegrationService.getIntegrationStatus();
    const jobs = await dataIntegrationService.getIntegrationJobs();
    
    // Filtrar trabajos por período
    const periodMs = getPeriodMs(period as string);
    const recentJobs = jobs.filter(j => 
      j.startTime > new Date(Date.now() - periodMs)
    );
    
    const stats = {
      ...status,
      recentJobs: recentJobs.length,
      successRate: recentJobs.length > 0 
        ? (recentJobs.filter(j => j.status === 'completed').length / recentJobs.length) * 100
        : 0,
      averageProcessingTime: recentJobs.length > 0
        ? recentJobs
            .filter(j => j.endTime)
            .reduce((sum, j) => sum + (j.endTime!.getTime() - j.startTime.getTime()), 0) / 
          recentJobs.filter(j => j.endTime).length
        : 0,
      totalRecordsProcessed: recentJobs.reduce((sum, j) => sum + j.recordsProcessed, 0),
      totalRecordsFailed: recentJobs.reduce((sum, j) => sum + j.recordsFailed, 0)
    };
    
    res.json({
      success: true,
      data: stats,
      period
    });
  } catch (error) {
    console.error('Error fetching integration stats:', error);
    res.status(500).json({ error: 'Failed to fetch integration stats' });
  }
});

// Función auxiliar para obtener período en milisegundos
function getPeriodMs(period: string): number {
  const periods: Record<string, number> = {
    '7d': 7 * 24 * 60 * 60 * 1000,
    '30d': 30 * 24 * 60 * 60 * 1000,
    '90d': 90 * 24 * 60 * 60 * 1000,
    '1y': 365 * 24 * 60 * 60 * 1000
  };

  return periods[period] || periods['30d'];
}

export default router;



