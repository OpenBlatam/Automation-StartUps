import express from 'express';
import { consciousnessWebinarService } from '../services/consciousnessWebinarService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Crear webinar
router.post('/create', authenticateToken, async (req, res) => {
  try {
    const { level, title, description } = req.body;
    
    if (!level || !title || !description) {
      return res.status(400).json({ error: 'Level, title, and description are required' });
    }

    if (level < 1 || level > 10) {
      return res.status(400).json({ error: 'Consciousness level must be between 1 and 10' });
    }

    const webinar = await consciousnessWebinarService.createWebinar(level, title, description);
    
    res.status(201).json({
      success: true,
      data: webinar,
      message: 'Consciousness webinar created successfully'
    });
  } catch (error) {
    console.error('Error creating webinar:', error);
    res.status(500).json({ error: 'Failed to create webinar' });
  }
});

// Obtener webinars activos
router.get('/active', authenticateToken, async (req, res) => {
  try {
    const webinars = await consciousnessWebinarService.getActiveWebinars();
    
    res.json({
      success: true,
      data: webinars,
      count: webinars.length
    });
  } catch (error) {
    console.error('Error fetching active webinars:', error);
    res.status(500).json({ error: 'Failed to fetch active webinars' });
  }
});

// Obtener webinar por ID
router.get('/:webinarId', authenticateToken, async (req, res) => {
  try {
    const { webinarId } = req.params;
    const webinar = await consciousnessWebinarService.getWebinarById(webinarId);
    
    if (!webinar) {
      return res.status(404).json({ error: 'Webinar not found' });
    }

    res.json({
      success: true,
      data: webinar
    });
  } catch (error) {
    console.error('Error fetching webinar:', error);
    res.status(500).json({ error: 'Failed to fetch webinar' });
  }
});

// Unirse a webinar
router.post('/:webinarId/join', authenticateToken, async (req, res) => {
  try {
    const { webinarId } = req.params;
    const { consciousnessLevel } = req.body;
    const userId = req.user?.id;

    if (!userId) {
      return res.status(401).json({ error: 'User not authenticated' });
    }

    if (!consciousnessLevel) {
      return res.status(400).json({ error: 'Consciousness level is required' });
    }

    const success = await consciousnessWebinarService.joinWebinar(webinarId, userId, consciousnessLevel);
    
    if (!success) {
      return res.status(400).json({ 
        error: 'Failed to join webinar. Check consciousness level requirements or capacity.' 
      });
    }

    res.json({
      success: true,
      message: 'Successfully joined webinar'
    });
  } catch (error) {
    console.error('Error joining webinar:', error);
    res.status(500).json({ error: 'Failed to join webinar' });
  }
});

// Iniciar webinar
router.post('/:webinarId/start', authenticateToken, async (req, res) => {
  try {
    const { webinarId } = req.params;
    const success = await consciousnessWebinarService.startWebinar(webinarId);
    
    if (!success) {
      return res.status(400).json({ error: 'Failed to start webinar' });
    }

    res.json({
      success: true,
      message: 'Webinar started successfully'
    });
  } catch (error) {
    console.error('Error starting webinar:', error);
    res.status(500).json({ error: 'Failed to start webinar' });
  }
});

// Finalizar webinar
router.post('/:webinarId/end', authenticateToken, async (req, res) => {
  try {
    const { webinarId } = req.params;
    const report = await consciousnessWebinarService.endWebinar(webinarId);
    
    if (!report) {
      return res.status(404).json({ error: 'Webinar not found' });
    }

    res.json({
      success: true,
      data: report,
      message: 'Webinar ended successfully'
    });
  } catch (error) {
    console.error('Error ending webinar:', error);
    res.status(500).json({ error: 'Failed to end webinar' });
  }
});

// Obtener participantes del webinar
router.get('/:webinarId/participants', authenticateToken, async (req, res) => {
  try {
    const { webinarId } = req.params;
    const participants = await consciousnessWebinarService.getWebinarParticipants(webinarId);
    
    res.json({
      success: true,
      data: participants,
      count: participants.length
    });
  } catch (error) {
    console.error('Error fetching participants:', error);
    res.status(500).json({ error: 'Failed to fetch participants' });
  }
});

// Obtener webinars por nivel de conciencia
router.get('/level/:level', authenticateToken, async (req, res) => {
  try {
    const { level } = req.params;
    const levelNum = parseInt(level);
    
    if (isNaN(levelNum) || levelNum < 1 || levelNum > 10) {
      return res.status(400).json({ error: 'Invalid consciousness level' });
    }

    const allWebinars = await consciousnessWebinarService.getActiveWebinars();
    const webinarsByLevel = allWebinars.filter(webinar => webinar.level === levelNum);
    
    res.json({
      success: true,
      data: webinarsByLevel,
      count: webinarsByLevel.length
    });
  } catch (error) {
    console.error('Error fetching webinars by level:', error);
    res.status(500).json({ error: 'Failed to fetch webinars by level' });
  }
});

// Obtener estadísticas de conciencia del webinar
router.get('/:webinarId/consciousness-stats', authenticateToken, async (req, res) => {
  try {
    const { webinarId } = req.params;
    const participants = await consciousnessWebinarService.getWebinarParticipants(webinarId);
    
    if (participants.length === 0) {
      return res.json({
        success: true,
        data: {
          totalParticipants: 0,
          averageConsciousnessLevel: 0,
          consciousnessDistribution: {},
          neuralActivity: 0,
          transcendenceRate: 0,
          quantumCoherence: 0
        }
      });
    }

    // Calcular estadísticas
    const totalParticipants = participants.length;
    const averageConsciousnessLevel = participants.reduce((sum, p) => sum + p.consciousnessLevel, 0) / totalParticipants;
    
    const consciousnessDistribution = participants.reduce((dist, p) => {
      const level = p.consciousnessLevel;
      dist[level] = (dist[level] || 0) + 1;
      return dist;
    }, {} as Record<number, number>);

    const neuralActivity = participants.reduce((sum, p) => sum + p.participationScore, 0) / totalParticipants;
    const transcendenceRate = participants.filter(p => p.participationScore > 80).length / totalParticipants;
    
    // Calcular coherencia cuántica
    const consciousnessLevels = participants.map(p => p.consciousnessLevel);
    const mean = consciousnessLevels.reduce((sum, val) => sum + val, 0) / consciousnessLevels.length;
    const variance = consciousnessLevels.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / consciousnessLevels.length;
    const quantumCoherence = Math.max(0, 100 - (variance * 10));

    res.json({
      success: true,
      data: {
        totalParticipants,
        averageConsciousnessLevel: parseFloat(averageConsciousnessLevel.toFixed(2)),
        consciousnessDistribution,
        neuralActivity: parseFloat(neuralActivity.toFixed(2)),
        transcendenceRate: parseFloat((transcendenceRate * 100).toFixed(2)),
        quantumCoherence: parseFloat(quantumCoherence.toFixed(2))
      }
    });
  } catch (error) {
    console.error('Error fetching consciousness stats:', error);
    res.status(500).json({ error: 'Failed to fetch consciousness statistics' });
  }
});

export default router;
