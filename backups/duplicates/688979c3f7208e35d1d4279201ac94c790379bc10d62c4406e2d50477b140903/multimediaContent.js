const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const multimediaContentService = require('../services/multimediaContentService');
const { body, validationResult } = require('express-validator');

// Initialize multimedia content service
multimediaContentService.initialize();

/**
 * @route   POST /api/multimedia/video-script
 * @desc    Generate video script
 * @access  Private
 */
router.post('/video-script', auth, [
  body('content').isString().withMessage('Content must be a string'),
  body('videoType').optional().isIn(['educational', 'promotional', 'tutorial', 'interview', 'testimonial']).withMessage('Invalid video type'),
  body('duration').optional().isString().withMessage('Duration must be a string'),
  body('targetAudience').optional().isString().withMessage('Target audience must be a string'),
  body('tone').optional().isIn(['professional', 'casual', 'friendly', 'authoritative', 'conversational']).withMessage('Invalid tone'),
  body('includeCallToAction').optional().isBoolean().withMessage('Include call to action must be a boolean')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { content, ...options } = req.body;
    const userId = req.user.id;
    
    const script = await multimediaContentService.generateVideoScript(content, {
      ...options,
      userId
    });

    res.json({
      success: true,
      message: 'Video script generated successfully',
      data: script
    });
  } catch (error) {
    console.error('Video script generation error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to generate video script'
    });
  }
});

/**
 * @route   POST /api/multimedia/podcast-script
 * @desc    Generate podcast script
 * @access  Private
 */
router.post('/podcast-script', auth, [
  body('content').isString().withMessage('Content must be a string'),
  body('podcastType').optional().isIn(['interview', 'solo', 'discussion', 'storytelling', 'educational']).withMessage('Invalid podcast type'),
  body('duration').optional().isString().withMessage('Duration must be a string'),
  body('hostStyle').optional().isIn(['conversational', 'formal', 'casual', 'authoritative', 'friendly']).withMessage('Invalid host style'),
  body('includeIntro').optional().isBoolean().withMessage('Include intro must be a boolean'),
  body('includeOutro').optional().isBoolean().withMessage('Include outro must be a boolean')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { content, ...options } = req.body;
    const userId = req.user.id;
    
    const script = await multimediaContentService.generatePodcastScript(content, {
      ...options,
      userId
    });

    res.json({
      success: true,
      message: 'Podcast script generated successfully',
      data: script
    });
  } catch (error) {
    console.error('Podcast script generation error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to generate podcast script'
    });
  }
});

/**
 * @route   POST /api/multimedia/infographic
 * @desc    Generate infographic content
 * @access  Private
 */
router.post('/infographic', auth, [
  body('content').isString().withMessage('Content must be a string'),
  body('infographicType').optional().isIn(['educational', 'statistical', 'comparison', 'process', 'timeline']).withMessage('Invalid infographic type'),
  body('targetAudience').optional().isString().withMessage('Target audience must be a string'),
  body('includeStatistics').optional().isBoolean().withMessage('Include statistics must be a boolean'),
  body('includeVisualElements').optional().isBoolean().withMessage('Include visual elements must be a boolean'),
  body('colorScheme').optional().isIn(['professional', 'creative', 'minimal', 'bold', 'corporate']).withMessage('Invalid color scheme')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { content, ...options } = req.body;
    const userId = req.user.id;
    
    const infographic = await multimediaContentService.generateInfographicContent(content, {
      ...options,
      userId
    });

    res.json({
      success: true,
      message: 'Infographic content generated successfully',
      data: infographic
    });
  } catch (error) {
    console.error('Infographic generation error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to generate infographic content'
    });
  }
});

/**
 * @route   POST /api/multimedia/social-media
 * @desc    Generate social media content
 * @access  Private
 */
router.post('/social-media', auth, [
  body('content').isString().withMessage('Content must be a string'),
  body('platform').optional().isIn(['facebook', 'instagram', 'twitter', 'linkedin', 'tiktok', 'youtube']).withMessage('Invalid platform'),
  body('contentType').optional().isIn(['post', 'story', 'reel', 'tweet', 'update', 'video']).withMessage('Invalid content type'),
  body('targetAudience').optional().isString().withMessage('Target audience must be a string'),
  body('includeHashtags').optional().isBoolean().withMessage('Include hashtags must be a boolean'),
  body('includeCallToAction').optional().isBoolean().withMessage('Include call to action must be a boolean')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { content, ...options } = req.body;
    const userId = req.user.id;
    
    const socialContent = await multimediaContentService.generateSocialMediaContent(content, {
      ...options,
      userId
    });

    res.json({
      success: true,
      message: 'Social media content generated successfully',
      data: socialContent
    });
  } catch (error) {
    console.error('Social media content generation error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to generate social media content'
    });
  }
});

/**
 * @route   GET /api/multimedia/templates
 * @desc    Get multimedia content templates
 * @access  Private
 */
router.get('/templates', auth, async (req, res) => {
  try {
    const templates = [
      {
        id: 'video_educational',
        name: 'Educational Video Script',
        description: 'Script template for educational videos',
        type: 'video',
        videoType: 'educational',
        duration: '3-5 minutes',
        tone: 'professional'
      },
      {
        id: 'video_promotional',
        name: 'Promotional Video Script',
        description: 'Script template for promotional videos',
        type: 'video',
        videoType: 'promotional',
        duration: '1-2 minutes',
        tone: 'engaging'
      },
      {
        id: 'podcast_interview',
        name: 'Interview Podcast Script',
        description: 'Script template for interview podcasts',
        type: 'podcast',
        podcastType: 'interview',
        duration: '30-45 minutes',
        hostStyle: 'conversational'
      },
      {
        id: 'podcast_solo',
        name: 'Solo Podcast Script',
        description: 'Script template for solo podcasts',
        type: 'podcast',
        podcastType: 'solo',
        duration: '15-30 minutes',
        hostStyle: 'authoritative'
      },
      {
        id: 'infographic_educational',
        name: 'Educational Infographic',
        description: 'Design template for educational infographics',
        type: 'infographic',
        infographicType: 'educational',
        colorScheme: 'professional'
      },
      {
        id: 'infographic_statistical',
        name: 'Statistical Infographic',
        description: 'Design template for statistical infographics',
        type: 'infographic',
        infographicType: 'statistical',
        colorScheme: 'bold'
      },
      {
        id: 'social_facebook',
        name: 'Facebook Post',
        description: 'Content template for Facebook posts',
        type: 'social',
        platform: 'facebook',
        contentType: 'post'
      },
      {
        id: 'social_instagram',
        name: 'Instagram Post',
        description: 'Content template for Instagram posts',
        type: 'social',
        platform: 'instagram',
        contentType: 'post'
      },
      {
        id: 'social_linkedin',
        name: 'LinkedIn Update',
        description: 'Content template for LinkedIn updates',
        type: 'social',
        platform: 'linkedin',
        contentType: 'update'
      },
      {
        id: 'social_twitter',
        name: 'Twitter Tweet',
        description: 'Content template for Twitter tweets',
        type: 'social',
        platform: 'twitter',
        contentType: 'tweet'
      }
    ];

    res.json({
      success: true,
      data: templates
    });
  } catch (error) {
    console.error('Get multimedia templates error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get multimedia templates'
    });
  }
});

/**
 * @route   GET /api/multimedia/benchmarks
 * @desc    Get multimedia content benchmarks
 * @access  Private
 */
router.get('/benchmarks', auth, async (req, res) => {
  try {
    const { contentType = 'video', platform = 'general' } = req.query;
    
    const benchmarks = {
      contentType: contentType,
      platform: platform,
      benchmarks: {
        video: {
          averageEngagement: platform === 'youtube' ? '4.2%' : '3.8%',
          averageRetention: platform === 'youtube' ? '65%' : '60%',
          optimalLength: platform === 'youtube' ? '8-12 minutes' : '2-3 minutes',
          bestPostingTime: '2-4 PM'
        },
        podcast: {
          averageListenTime: '22 minutes',
          averageCompletionRate: '75%',
          optimalLength: '25-35 minutes',
          bestPublishingDay: 'Tuesday'
        },
        infographic: {
          averageShares: '15-25',
          averageSaves: '8-12',
          optimalSize: '1200x630px',
          bestColorCount: '3-5 colors'
        },
        socialMedia: {
          averageEngagement: platform === 'instagram' ? '3.5%' : '2.8%',
          averageReach: platform === 'instagram' ? '45%' : '35%',
          optimalPostingTime: platform === 'instagram' ? '6-9 PM' : '1-3 PM',
          bestHashtagCount: platform === 'instagram' ? '15-20' : '3-5'
        }
      },
      recommendations: [
        'Focus on quality over quantity',
        'Optimize for platform-specific algorithms',
        'Test different content formats',
        'Monitor engagement metrics regularly',
        'Adapt content based on audience feedback'
      ]
    };

    res.json({
      success: true,
      data: benchmarks
    });
  } catch (error) {
    console.error('Get multimedia benchmarks error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get multimedia benchmarks'
    });
  }
});

/**
 * @route   GET /api/multimedia/content/:id
 * @desc    Get specific multimedia content
 * @access  Private
 */
router.get('/content/:id', auth, async (req, res) => {
  try {
    const { id } = req.params;
    const content = multimediaContentService.getContent(id);
    
    if (!content) {
      return res.status(404).json({
        success: false,
        message: 'Content not found'
      });
    }

    res.json({
      success: true,
      data: content
    });
  } catch (error) {
    console.error('Get multimedia content error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get multimedia content'
    });
  }
});

/**
 * @route   PUT /api/multimedia/content/:id
 * @desc    Update multimedia content
 * @access  Private
 */
router.put('/content/:id', auth, [
  body('updates').isObject().withMessage('Updates must be an object')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { id } = req.params;
    const { updates } = req.body;
    
    const updatedContent = multimediaContentService.updateContent(id, updates);
    
    if (!updatedContent) {
      return res.status(404).json({
        success: false,
        message: 'Content not found'
      });
    }

    res.json({
      success: true,
      message: 'Content updated successfully',
      data: updatedContent
    });
  } catch (error) {
    console.error('Update multimedia content error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to update multimedia content'
    });
  }
});

/**
 * @route   DELETE /api/multimedia/content/:id
 * @desc    Delete multimedia content
 * @access  Private
 */
router.delete('/content/:id', auth, async (req, res) => {
  try {
    const { id } = req.params;
    const deleted = multimediaContentService.deleteContent(id);
    
    if (!deleted) {
      return res.status(404).json({
        success: false,
        message: 'Content not found'
      });
    }

    res.json({
      success: true,
      message: 'Content deleted successfully'
    });
  } catch (error) {
    console.error('Delete multimedia content error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to delete multimedia content'
    });
  }
});

module.exports = router;



