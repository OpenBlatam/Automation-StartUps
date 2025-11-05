const express = require('express');
const router = express.Router();
const TestimonialService = require('../services/TestimonialService');
const authMiddleware = require('../middleware/auth');
const validationMiddleware = require('../middleware/validation');
const { testimonialSchema } = require('../schemas/testimonial');

const testimonialService = new TestimonialService();

// Get all testimonials for a user
router.get('/', authMiddleware, async (req, res) => {
  try {
    const { page = 1, limit = 10, category, status } = req.query;
    const userId = req.user.id;
    
    const testimonials = await testimonialService.getUserTestimonials(
      userId, 
      { page: parseInt(page), limit: parseInt(limit), category, status }
    );
    
    res.json({
      success: true,
      data: testimonials,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: testimonials.total
      }
    });
  } catch (error) {
    console.error('Error fetching testimonials:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch testimonials',
      message: error.message
    });
  }
});

// Generate new testimonial
router.post('/generate', 
  authMiddleware, 
  validationMiddleware(testimonialSchema),
  async (req, res) => {
    try {
      const userId = req.user.id;
      const testimonialData = req.body;
      
      // Check user's plan limits
      const canGenerate = await testimonialService.checkUserLimits(userId);
      if (!canGenerate.allowed) {
        return res.status(429).json({
          success: false,
          error: 'Plan limit exceeded',
          message: canGenerate.message,
          upgradeRequired: true
        });
      }
      
      const testimonial = await testimonialService.generateTestimonial(
        userId, 
        testimonialData
      );
      
      res.status(201).json({
        success: true,
        data: testimonial,
        usage: {
          remaining: canGenerate.remaining - 1,
          resetDate: canGenerate.resetDate
        }
      });
    } catch (error) {
      console.error('Error generating testimonial:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to generate testimonial',
        message: error.message
      });
    }
  }
);

// Generate batch testimonials
router.post('/generate-batch', 
  authMiddleware,
  async (req, res) => {
    try {
      const userId = req.user.id;
      const { requests, options = {} } = req.body;
      
      if (!Array.isArray(requests) || requests.length === 0) {
        return res.status(400).json({
          success: false,
          error: 'Invalid request',
          message: 'Requests array is required and cannot be empty'
        });
      }
      
      // Check batch limits
      const canGenerate = await testimonialService.checkBatchLimits(userId, requests.length);
      if (!canGenerate.allowed) {
        return res.status(429).json({
          success: false,
          error: 'Batch limit exceeded',
          message: canGenerate.message,
          upgradeRequired: true
        });
      }
      
      const testimonials = await testimonialService.generateBatchTestimonials(
        userId,
        requests,
        options
      );
      
      res.status(201).json({
        success: true,
        data: testimonials,
        usage: {
          generated: testimonials.length,
          remaining: canGenerate.remaining - testimonials.length,
          resetDate: canGenerate.resetDate
        }
      });
    } catch (error) {
      console.error('Error generating batch testimonials:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to generate batch testimonials',
        message: error.message
      });
    }
  }
);

// Get specific testimonial
router.get('/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;
    
    const testimonial = await testimonialService.getTestimonialById(id, userId);
    
    if (!testimonial) {
      return res.status(404).json({
        success: false,
        error: 'Not found',
        message: 'Testimonial not found'
      });
    }
    
    res.json({
      success: true,
      data: testimonial
    });
  } catch (error) {
    console.error('Error fetching testimonial:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch testimonial',
      message: error.message
    });
  }
});

// Update testimonial
router.put('/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;
    const updates = req.body;
    
    const testimonial = await testimonialService.updateTestimonial(id, userId, updates);
    
    if (!testimonial) {
      return res.status(404).json({
        success: false,
        error: 'Not found',
        message: 'Testimonial not found'
      });
    }
    
    res.json({
      success: true,
      data: testimonial
    });
  } catch (error) {
    console.error('Error updating testimonial:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update testimonial',
      message: error.message
    });
  }
});

// Delete testimonial
router.delete('/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;
    
    const deleted = await testimonialService.deleteTestimonial(id, userId);
    
    if (!deleted) {
      return res.status(404).json({
        success: false,
        error: 'Not found',
        message: 'Testimonial not found'
      });
    }
    
    res.json({
      success: true,
      message: 'Testimonial deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting testimonial:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to delete testimonial',
      message: error.message
    });
  }
});

// Regenerate testimonial with different AI model
router.post('/:id/regenerate', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;
    const { model, options = {} } = req.body;
    
    const testimonial = await testimonialService.regenerateTestimonial(
      id, 
      userId, 
      model, 
      options
    );
    
    if (!testimonial) {
      return res.status(404).json({
        success: false,
        error: 'Not found',
        message: 'Testimonial not found'
      });
    }
    
    res.json({
      success: true,
      data: testimonial
    });
  } catch (error) {
    console.error('Error regenerating testimonial:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to regenerate testimonial',
      message: error.message
    });
  }
});

// Export testimonials
router.post('/export', authMiddleware, async (req, res) => {
  try {
    const userId = req.user.id;
    const { format = 'json', filters = {} } = req.body;
    
    const exportData = await testimonialService.exportTestimonials(userId, format, filters);
    
    res.setHeader('Content-Type', 
      format === 'csv' ? 'text/csv' : 'application/json'
    );
    res.setHeader('Content-Disposition', 
      `attachment; filename="testimonials-${Date.now()}.${format}"`
    );
    
    res.send(exportData);
  } catch (error) {
    console.error('Error exporting testimonials:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to export testimonials',
      message: error.message
    });
  }
});

// Get testimonial analytics
router.get('/analytics/overview', authMiddleware, async (req, res) => {
  try {
    const userId = req.user.id;
    const { period = '30d' } = req.query;
    
    const analytics = await testimonialService.getTestimonialAnalytics(userId, period);
    
    res.json({
      success: true,
      data: analytics
    });
  } catch (error) {
    console.error('Error fetching testimonial analytics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch analytics',
      message: error.message
    });
  }
});

module.exports = router;



