const express = require('express');
const router = express.Router();

/**
 * Content Generation API Routes
 * Handles all content generation operations
 */

// Generate content
router.post('/generate', async (req, res) => {
  try {
    const { type, params } = req.body;
    const contentGenerator = req.app.locals.contentGenerator;
    
    if (!type) {
      return res.status(400).json({
        success: false,
        error: 'Content type is required'
      });
    }
    
    const result = await contentGenerator.generateContent(type, params);
    
    if (result.success) {
      res.json({
        success: true,
        data: result
      });
    } else {
      res.status(500).json({
        success: false,
        error: result.error
      });
    }
  } catch (error) {
    console.error('Error generating content:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to generate content'
    });
  }
});

// Generate thought leadership content
router.post('/thought-leadership', async (req, res) => {
  try {
    const { templateType, params } = req.body;
    const contentGenerator = req.app.locals.contentGenerator;
    
    if (!templateType) {
      return res.status(400).json({
        success: false,
        error: 'Template type is required'
      });
    }
    
    const result = await contentGenerator.generateThoughtLeadership(templateType, params);
    
    if (result.success) {
      res.json({
        success: true,
        data: result
      });
    } else {
      res.status(500).json({
        success: false,
        error: result.error
      });
    }
  } catch (error) {
    console.error('Error generating thought leadership content:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to generate thought leadership content'
    });
  }
});

// Generate marketing copy
router.post('/marketing-copy', async (req, res) => {
  try {
    const { copyType, params } = req.body;
    const contentGenerator = req.app.locals.contentGenerator;
    
    if (!copyType) {
      return res.status(400).json({
        success: false,
        error: 'Copy type is required'
      });
    }
    
    const result = await contentGenerator.generateMarketingCopy(copyType, params);
    
    if (result.success) {
      res.json({
        success: true,
        data: result
      });
    } else {
      res.status(500).json({
        success: false,
        error: result.error
      });
    }
  } catch (error) {
    console.error('Error generating marketing copy:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to generate marketing copy'
    });
  }
});

// Generate business content
router.post('/business-content', async (req, res) => {
  try {
    const { contentType, params } = req.body;
    const contentGenerator = req.app.locals.contentGenerator;
    
    if (!contentType) {
      return res.status(400).json({
        success: false,
        error: 'Content type is required'
      });
    }
    
    const result = await contentGenerator.generateBusinessContent(contentType, params);
    
    if (result.success) {
      res.json({
        success: true,
        data: result
      });
    } else {
      res.status(500).json({
        success: false,
        error: result.error
      });
    }
  } catch (error) {
    console.error('Error generating business content:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to generate business content'
    });
  }
});

// Generate content variations
router.post('/variations', async (req, res) => {
  try {
    const { type, params, count = 3 } = req.body;
    const contentGenerator = req.app.locals.contentGenerator;
    
    if (!type) {
      return res.status(400).json({
        success: false,
        error: 'Content type is required'
      });
    }
    
    const variations = await contentGenerator.generateVariations(type, params, count);
    
    res.json({
      success: true,
      data: {
        variations,
        count: variations.length
      }
    });
  } catch (error) {
    console.error('Error generating content variations:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to generate content variations'
    });
  }
});

// Optimize content for SEO
router.post('/seo-optimize', async (req, res) => {
  try {
    const { content, keywords = [] } = req.body;
    const contentGenerator = req.app.locals.contentGenerator;
    
    if (!content) {
      return res.status(400).json({
        success: false,
        error: 'Content is required'
      });
    }
    
    const result = await contentGenerator.optimizeForSEO(content, keywords);
    
    if (result.success) {
      res.json({
        success: true,
        data: result
      });
    } else {
      res.status(500).json({
        success: false,
        error: result.error
      });
    }
  } catch (error) {
    console.error('Error optimizing content for SEO:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to optimize content for SEO'
    });
  }
});

// Generate tone variations
router.post('/tone-variations', async (req, res) => {
  try {
    const { content, tones = ['professional', 'casual', 'authoritative', 'friendly'] } = req.body;
    const contentGenerator = req.app.locals.contentGenerator;
    
    if (!content) {
      return res.status(400).json({
        success: false,
        error: 'Content is required'
      });
    }
    
    const variations = await contentGenerator.generateToneVariations(content, tones);
    
    res.json({
      success: true,
      data: {
        variations,
        count: variations.length
      }
    });
  } catch (error) {
    console.error('Error generating tone variations:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to generate tone variations'
    });
  }
});

// Get available templates
router.get('/templates', async (req, res) => {
  try {
    const contentGenerator = req.app.locals.contentGenerator;
    const templates = contentGenerator.getAvailableTemplates();
    
    res.json({
      success: true,
      data: templates
    });
  } catch (error) {
    console.error('Error getting templates:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get templates'
    });
  }
});

// Get content type configurations
router.get('/types', async (req, res) => {
  try {
    const contentGenerator = req.app.locals.contentGenerator;
    const types = contentGenerator.getContentTypeConfigs();
    
    res.json({
      success: true,
      data: types
    });
  } catch (error) {
    console.error('Error getting content types:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get content types'
    });
  }
});

// Generate content with neural consciousness
router.post('/neural-generate', async (req, res) => {
  try {
    const { type, params } = req.body;
    const contentGenerator = req.app.locals.contentGenerator;
    const neuralConsciousness = req.app.locals.neuralConsciousness;
    
    if (!type) {
      return res.status(400).json({
        success: false,
        error: 'Content type is required'
      });
    }
    
    // Get current consciousness state
    const consciousnessState = neuralConsciousness.getConsciousnessState();
    
    // Enhance params with consciousness data
    const enhancedParams = {
      ...params,
      consciousness: consciousnessState.states.consciousness,
      creativity: consciousnessState.states.creativity,
      empathy: consciousnessState.states.empathy,
      wisdom: consciousnessState.states.wisdom
    };
    
    const result = await contentGenerator.generateContent(type, enhancedParams);
    
    if (result.success) {
      // Add consciousness metadata
      result.metadata.consciousness = consciousnessState.states;
      result.metadata.neuralNetworks = consciousnessState.networks;
      
      res.json({
        success: true,
        data: result
      });
    } else {
      res.status(500).json({
        success: false,
        error: result.error
      });
    }
  } catch (error) {
    console.error('Error generating neural content:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to generate neural content'
    });
  }
});

// Batch content generation
router.post('/batch-generate', async (req, res) => {
  try {
    const { requests } = req.body;
    const contentGenerator = req.app.locals.contentGenerator;
    
    if (!Array.isArray(requests) || requests.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Requests array is required'
      });
    }
    
    const results = [];
    
    for (const request of requests) {
      const { type, params } = request;
      const result = await contentGenerator.generateContent(type, params);
      results.push({
        request,
        result
      });
    }
    
    res.json({
      success: true,
      data: {
        results,
        count: results.length
      }
    });
  } catch (error) {
    console.error('Error in batch content generation:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to generate batch content'
    });
  }
});

module.exports = router;

