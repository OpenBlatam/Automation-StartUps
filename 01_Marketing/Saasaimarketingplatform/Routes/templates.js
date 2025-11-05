const express = require('express');
const { body, validationResult } = require('express-validator');
const ContentTemplate = require('../models/ContentTemplate');
const { asyncHandler, AppError } = require('../middleware/errorHandler');
const { authMiddleware, subscriptionMiddleware } = require('../middleware/auth');
const router = express.Router();

// @route   GET /api/templates
// @desc    Get all templates
// @access  Public
router.get('/', asyncHandler(async (req, res) => {
  const {
    category,
    subcategory,
    search,
    sortBy = 'popular',
    page = 1,
    limit = 20,
    featured,
    difficulty,
    plan = 'free'
  } = req.query;

  // Build query
  const query = { isActive: true };

  if (category && category !== 'all') {
    query.category = category;
  }

  if (subcategory) {
    query.subcategory = subcategory;
  }

  if (search) {
    const searchRegex = new RegExp(search, 'i');
    query.$or = [
      { name: searchRegex },
      { description: searchRegex },
      { tags: searchRegex }
    ];
  }

  if (featured === 'true') {
    query.isFeatured = true;
  }

  if (difficulty) {
    query.difficulty = difficulty;
  }

  // Filter by plan access
  const planHierarchy = { free: 0, basic: 1, professional: 2, enterprise: 3 };
  const userPlanLevel = planHierarchy[plan] || 0;
  
  query.$or = query.$or ? [
    ...query.$or,
    {
      $or: [
        { requiredPlan: 'free' },
        { requiredPlan: { $in: Object.keys(planHierarchy).filter(p => planHierarchy[p] <= userPlanLevel) } }
      ]
    }
  ] : [
    { requiredPlan: 'free' },
    { requiredPlan: { $in: Object.keys(planHierarchy).filter(p => planHierarchy[p] <= userPlanLevel) } }
  ];

  // Build sort
  let sort = {};
  switch (sortBy) {
    case 'popular':
      sort = { 'usage.totalUses': -1 };
      break;
    case 'recent':
      sort = { createdAt: -1 };
      break;
    case 'rating':
      sort = { 'usage.averageRating': -1 };
      break;
    case 'name':
      sort = { name: 1 };
      break;
    default:
      sort = { 'usage.totalUses': -1 };
  }

  // Pagination
  const skip = (page - 1) * limit;

  const templates = await ContentTemplate.find(query)
    .populate('createdBy', 'firstName lastName')
    .sort(sort)
    .skip(skip)
    .limit(parseInt(limit));

  const total = await ContentTemplate.countDocuments(query);

  res.json({
    success: true,
    data: {
      templates,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / limit)
      }
    }
  });
}));

// @route   GET /api/templates/:id
// @desc    Get single template
// @access  Public
router.get('/:id', asyncHandler(async (req, res) => {
  const template = await ContentTemplate.findById(req.params.id)
    .populate('createdBy', 'firstName lastName');

  if (!template) {
    return res.status(404).json({
      success: false,
      message: 'Template not found'
    });
  }

  if (!template.isActive) {
    return res.status(404).json({
      success: false,
      message: 'Template not available'
    });
  }

  res.json({
    success: true,
    data: template
  });
}));

// @route   POST /api/templates
// @desc    Create new template
// @access  Private
router.post('/', [
  authMiddleware,
  subscriptionMiddleware('basic'),
  body('name').trim().isLength({ min: 3, max: 100 }).withMessage('Name must be between 3 and 100 characters'),
  body('description').trim().isLength({ min: 10, max: 500 }).withMessage('Description must be between 10 and 500 characters'),
  body('category').isIn(['email-marketing', 'social-media', 'blog-content', 'ad-copy', 'product-descriptions', 'landing-pages', 'sales-copy', 'performance-reviews', 'presentations', 'reports', 'other']).withMessage('Invalid category'),
  body('prompt').trim().isLength({ min: 10, max: 2000 }).withMessage('Prompt must be between 10 and 2000 characters'),
  body('variables').isArray().withMessage('Variables must be an array'),
  body('aiSettings.model').optional().isIn(['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo', 'claude-3-sonnet', 'claude-3-opus']).withMessage('Invalid AI model'),
  body('aiSettings.temperature').optional().isFloat({ min: 0, max: 2 }).withMessage('Temperature must be between 0 and 2'),
  body('aiSettings.maxTokens').optional().isInt({ min: 50, max: 4000 }).withMessage('Max tokens must be between 50 and 4000')
], asyncHandler(async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      message: 'Validation failed',
      errors: errors.array()
    });
  }

  const templateData = {
    ...req.body,
    createdBy: req.user.id,
    visibility: 'private' // User-created templates are private by default
  };

  const template = new ContentTemplate(templateData);
  await template.save();

  res.status(201).json({
    success: true,
    message: 'Template created successfully',
    data: template
  });
}));

// @route   PUT /api/templates/:id
// @desc    Update template
// @access  Private
router.put('/:id', [
  authMiddleware,
  body('name').optional().trim().isLength({ min: 3, max: 100 }).withMessage('Name must be between 3 and 100 characters'),
  body('description').optional().trim().isLength({ min: 10, max: 500 }).withMessage('Description must be between 10 and 500 characters'),
  body('prompt').optional().trim().isLength({ min: 10, max: 2000 }).withMessage('Prompt must be between 10 and 2000 characters')
], asyncHandler(async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      message: 'Validation failed',
      errors: errors.array()
    });
  }

  const template = await ContentTemplate.findById(req.params.id);

  if (!template) {
    return res.status(404).json({
      success: false,
      message: 'Template not found'
    });
  }

  // Check if user owns the template or is admin
  if (template.createdBy.toString() !== req.user.id && req.user.role !== 'admin') {
    return res.status(403).json({
      success: false,
      message: 'Not authorized to update this template'
    });
  }

  // Update template
  Object.keys(req.body).forEach(key => {
    if (req.body[key] !== undefined) {
      template[key] = req.body[key];
    }
  });

  await template.save();

  res.json({
    success: true,
    message: 'Template updated successfully',
    data: template
  });
}));

// @route   DELETE /api/templates/:id
// @desc    Delete template
// @access  Private
router.delete('/:id', authMiddleware, asyncHandler(async (req, res) => {
  const template = await ContentTemplate.findById(req.params.id);

  if (!template) {
    return res.status(404).json({
      success: false,
      message: 'Template not found'
    });
  }

  // Check if user owns the template or is admin
  if (template.createdBy.toString() !== req.user.id && req.user.role !== 'admin') {
    return res.status(403).json({
      success: false,
      message: 'Not authorized to delete this template'
    });
  }

  // Soft delete by setting isActive to false
  template.isActive = false;
  await template.save();

  res.json({
    success: true,
    message: 'Template deleted successfully'
  });
}));

// @route   POST /api/templates/:id/rate
// @desc    Rate template
// @access  Private
router.post('/:id/rate', [
  authMiddleware,
  body('rating').isInt({ min: 1, max: 5 }).withMessage('Rating must be between 1 and 5'),
  body('feedback').optional().trim().isLength({ max: 500 }).withMessage('Feedback must be less than 500 characters')
], asyncHandler(async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      message: 'Validation failed',
      errors: errors.array()
    });
  }

  const { rating, feedback } = req.body;

  const template = await ContentTemplate.findById(req.params.id);

  if (!template) {
    return res.status(404).json({
      success: false,
      message: 'Template not found'
    });
  }

  await template.addRating(rating);

  res.json({
    success: true,
    message: 'Template rated successfully',
    data: {
      averageRating: template.usage.averageRating,
      totalRatings: template.usage.totalRatings
    }
  });
}));

// @route   GET /api/templates/categories
// @desc    Get template categories
// @access  Public
router.get('/meta/categories', asyncHandler(async (req, res) => {
  const categories = await ContentTemplate.aggregate([
    { $match: { isActive: true } },
    {
      $group: {
        _id: '$category',
        count: { $sum: 1 },
        subcategories: { $addToSet: '$subcategory' }
      }
    },
    { $sort: { count: -1 } }
  ]);

  res.json({
    success: true,
    data: categories
  });
}));

// @route   GET /api/templates/stats
// @desc    Get template statistics
// @access  Public
router.get('/meta/stats', asyncHandler(async (req, res) => {
  const stats = await ContentTemplate.aggregate([
    { $match: { isActive: true } },
    {
      $group: {
        _id: null,
        totalTemplates: { $sum: 1 },
        totalUses: { $sum: '$usage.totalUses' },
        averageRating: { $avg: '$usage.averageRating' },
        featuredTemplates: {
          $sum: { $cond: ['$isFeatured', 1, 0] }
        }
      }
    }
  ]);

  const categoryStats = await ContentTemplate.aggregate([
    { $match: { isActive: true } },
    {
      $group: {
        _id: '$category',
        count: { $sum: 1 },
        totalUses: { $sum: '$usage.totalUses' }
      }
    },
    { $sort: { totalUses: -1 } }
  ]);

  res.json({
    success: true,
    data: {
      overall: stats[0] || {
        totalTemplates: 0,
        totalUses: 0,
        averageRating: 0,
        featuredTemplates: 0
      },
      byCategory: categoryStats
    }
  });
}));

// @route   GET /api/templates/featured
// @desc    Get featured templates
// @access  Public
router.get('/meta/featured', asyncHandler(async (req, res) => {
  const { limit = 6, plan = 'free' } = req.query;

  const planHierarchy = { free: 0, basic: 1, professional: 2, enterprise: 3 };
  const userPlanLevel = planHierarchy[plan] || 0;

  const templates = await ContentTemplate.find({
    isFeatured: true,
    isActive: true,
    $or: [
      { requiredPlan: 'free' },
      { requiredPlan: { $in: Object.keys(planHierarchy).filter(p => planHierarchy[p] <= userPlanLevel) } }
    ]
  })
    .populate('createdBy', 'firstName lastName')
    .sort({ 'usage.totalUses': -1 })
    .limit(parseInt(limit));

  res.json({
    success: true,
    data: templates
  });
}));

// @route   POST /api/templates/:id/duplicate
// @desc    Duplicate template
// @access  Private
router.post('/:id/duplicate', [
  authMiddleware,
  subscriptionMiddleware('basic')
], asyncHandler(async (req, res) => {
  const originalTemplate = await ContentTemplate.findById(req.params.id);

  if (!originalTemplate) {
    return res.status(404).json({
      success: false,
      message: 'Template not found'
    });
  }

  // Create duplicate
  const duplicateData = {
    ...originalTemplate.toObject(),
    _id: undefined,
    name: `${originalTemplate.name} (Copy)`,
    createdBy: req.user.id,
    visibility: 'private',
    usage: {
      totalUses: 0,
      successfulGenerations: 0,
      averageRating: 0,
      totalRatings: 0
    },
    isFeatured: false,
    createdAt: undefined,
    updatedAt: undefined
  };

  const duplicate = new ContentTemplate(duplicateData);
  await duplicate.save();

  res.status(201).json({
    success: true,
    message: 'Template duplicated successfully',
    data: duplicate
  });
}));

module.exports = router;







