const mongoose = require('mongoose');

const testimonialSchema = new mongoose.Schema({
  id: {
    type: String,
    required: true,
    unique: true
  },
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  templateType: {
    type: String,
    required: true,
    enum: ['distinctiveQualities', 'recommendation', 'specificSituation', 'investmentWorth', 'efficiencyImprovement']
  },
  productName: {
    type: String,
    required: true,
    trim: true
  },
  productCategory: {
    type: String,
    required: true,
    trim: true
  },
  targetAudience: {
    type: String,
    required: true,
    trim: true
  },
  keyBenefits: [{
    type: String,
    trim: true
  }],
  useCase: {
    type: String,
    trim: true
  },
  industry: {
    type: String,
    required: true,
    trim: true
  },
  tone: {
    type: String,
    required: true,
    enum: ['professional', 'casual', 'technical', 'emotional'],
    default: 'professional'
  },
  length: {
    type: String,
    required: true,
    enum: ['short', 'medium', 'long'],
    default: 'medium'
  },
  model: {
    type: String,
    required: true,
    enum: ['gpt-4', 'claude-3', 'gemini-pro'],
    default: 'gpt-4'
  },
  content: {
    type: String,
    required: true
  },
  alternatives: [{
    type: String
  }],
  metadata: {
    prompt: String,
    tokensUsed: Number,
    generationTime: Number,
    qualityScore: Number,
    customInstructions: String
  },
  status: {
    type: String,
    enum: ['generated', 'reviewed', 'approved', 'rejected', 'published'],
    default: 'generated'
  },
  tags: [{
    type: String,
    trim: true
  }],
  notes: {
    type: String,
    trim: true
  },
  publishedAt: {
    type: Date
  },
  performance: {
    views: { type: Number, default: 0 },
    clicks: { type: Number, default: 0 },
    conversions: { type: Number, default: 0 },
    lastTracked: { type: Date }
  }
}, {
  timestamps: true
});

// Indexes for better query performance
testimonialSchema.index({ userId: 1, createdAt: -1 });
testimonialSchema.index({ userId: 1, templateType: 1 });
testimonialSchema.index({ userId: 1, status: 1 });
testimonialSchema.index({ userId: 1, industry: 1 });
testimonialSchema.index({ id: 1 });

// Virtual for word count
testimonialSchema.virtual('wordCount').get(function() {
  return this.content ? this.content.split(' ').length : 0;
});

// Virtual for character count
testimonialSchema.virtual('characterCount').get(function() {
  return this.content ? this.content.length : 0;
});

// Method to update performance metrics
testimonialSchema.methods.updatePerformance = function(metric, increment = 1) {
  this.performance[metric] = (this.performance[metric] || 0) + increment;
  this.performance.lastTracked = new Date();
  return this.save();
};

// Method to get performance summary
testimonialSchema.methods.getPerformanceSummary = function() {
  const { views, clicks, conversions } = this.performance;
  const clickThroughRate = views > 0 ? (clicks / views * 100).toFixed(2) : 0;
  const conversionRate = clicks > 0 ? (conversions / clicks * 100).toFixed(2) : 0;
  
  return {
    views,
    clicks,
    conversions,
    clickThroughRate: `${clickThroughRate}%`,
    conversionRate: `${conversionRate}%`
  };
};

// Static method to get user statistics
testimonialSchema.statics.getUserStats = async function(userId, period = '30d') {
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - parseInt(period));
  
  const stats = await this.aggregate([
    {
      $match: {
        userId: mongoose.Types.ObjectId(userId),
        createdAt: { $gte: startDate }
      }
    },
    {
      $group: {
        _id: null,
        totalTestimonials: { $sum: 1 },
        avgQualityScore: { $avg: '$metadata.qualityScore' },
        totalTokensUsed: { $sum: '$metadata.tokensUsed' },
        byTemplate: {
          $push: {
            template: '$templateType',
            quality: '$metadata.qualityScore'
          }
        },
        byModel: {
          $push: {
            model: '$model',
            tokens: '$metadata.tokensUsed'
          }
        },
        byStatus: {
          $push: '$status'
        }
      }
    }
  ]);
  
  return stats[0] || {
    totalTestimonials: 0,
    avgQualityScore: 0,
    totalTokensUsed: 0,
    byTemplate: [],
    byModel: [],
    byStatus: []
  };
};

// Pre-save middleware to ensure required fields
testimonialSchema.pre('save', function(next) {
  if (this.isNew && !this.id) {
    this.id = require('uuid').v4();
  }
  next();
});

// Pre-save middleware to update publishedAt
testimonialSchema.pre('save', function(next) {
  if (this.isModified('status') && this.status === 'published' && !this.publishedAt) {
    this.publishedAt = new Date();
  }
  next();
});

module.exports = mongoose.model('Testimonial', testimonialSchema);



