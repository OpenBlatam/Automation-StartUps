const mongoose = require('mongoose');

const generatedContentSchema = new mongoose.Schema({
  // User and Template Information
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  templateId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'ContentTemplate',
    default: null
  },
  
  // Content Data
  prompt: {
    type: String,
    required: [true, 'Prompt is required'],
    maxlength: [10000, 'Prompt cannot exceed 10,000 characters']
  },
  variables: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  },
  content: {
    type: String,
    required: [true, 'Generated content is required']
  },
  
  // Metadata
  metadata: {
    model: {
      type: String,
      required: true
    },
    usage: {
      promptTokens: Number,
      completionTokens: Number,
      totalTokens: Number
    },
    cost: {
      type: Number,
      default: 0
    },
    timestamp: {
      type: String,
      required: true
    },
    temperature: Number,
    maxTokens: Number,
    variation: Number, // For variations
    optimizationGoal: String, // For optimized content
    originalContent: String, // For optimized content
    analysisType: String // For analyzed content
  },
  
  // Status and Processing
  status: {
    type: String,
    enum: ['pending', 'processing', 'completed', 'failed'],
    default: 'pending'
  },
  error: {
    message: String,
    code: String,
    timestamp: Date
  },
  
  // User Interaction
  rating: {
    type: Number,
    min: 1,
    max: 5
  },
  feedback: {
    type: String,
    maxlength: [500, 'Feedback cannot exceed 500 characters']
  },
  isFavorite: {
    type: Boolean,
    default: false
  },
  tags: [{
    type: String,
    trim: true,
    lowercase: true
  }],
  
  // Usage Analytics
  views: {
    type: Number,
    default: 0
  },
  copies: {
    type: Number,
    default: 0
  },
  shares: {
    type: Number,
    default: 0
  },
  
  // Export and Download
  exports: [{
    format: {
      type: String,
      enum: ['txt', 'docx', 'pdf', 'html', 'json']
    },
    url: String,
    downloadedAt: {
      type: Date,
      default: Date.now
    }
  }],
  
  // Version Control
  version: {
    type: String,
    default: '1.0.0'
  },
  parentId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'GeneratedContent'
  },
  revisions: [{
    content: String,
    timestamp: {
      type: Date,
      default: Date.now
    },
    note: String
  }]
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Virtual for content length
generatedContentSchema.virtual('contentLength').get(function() {
  return this.content ? this.content.length : 0;
});

// Virtual for word count
generatedContentSchema.virtual('wordCount').get(function() {
  return this.content ? this.content.split(/\s+/).length : 0;
});

// Virtual for reading time (average 200 words per minute)
generatedContentSchema.virtual('readingTime').get(function() {
  return Math.ceil(this.wordCount / 200);
});

// Virtual for cost per word
generatedContentSchema.virtual('costPerWord').get(function() {
  if (this.wordCount === 0) return 0;
  return this.metadata.cost / this.wordCount;
});

// Indexes for better performance
generatedContentSchema.index({ userId: 1, createdAt: -1 });
generatedContentSchema.index({ templateId: 1 });
generatedContentSchema.index({ status: 1 });
generatedContentSchema.index({ 'metadata.model': 1 });
generatedContentSchema.index({ tags: 1 });
generatedContentSchema.index({ isFavorite: 1 });

// Pre-save middleware
generatedContentSchema.pre('save', function(next) {
  // Update version if content changes
  if (this.isModified('content') && !this.isNew) {
    const versionParts = this.version.split('.');
    const patch = parseInt(versionParts[2]) + 1;
    this.version = `${versionParts[0]}.${versionParts[1]}.${patch}`;
    
    // Add to revisions
    this.revisions.push({
      content: this.content,
      note: 'Content updated'
    });
  }
  next();
});

// Method to increment views
generatedContentSchema.methods.incrementViews = function() {
  this.views += 1;
  return this.save();
};

// Method to increment copies
generatedContentSchema.methods.incrementCopies = function() {
  this.copies += 1;
  return this.save();
};

// Method to increment shares
generatedContentSchema.methods.incrementShares = function() {
  this.shares += 1;
  return this.save();
};

// Method to add rating and feedback
generatedContentSchema.methods.addRating = function(rating, feedback = '') {
  if (rating < 1 || rating > 5) {
    throw new Error('Rating must be between 1 and 5');
  }
  
  this.rating = rating;
  if (feedback) {
    this.feedback = feedback;
  }
  
  return this.save();
};

// Method to toggle favorite
generatedContentSchema.methods.toggleFavorite = function() {
  this.isFavorite = !this.isFavorite;
  return this.save();
};

// Method to add tags
generatedContentSchema.methods.addTags = function(tags) {
  const newTags = tags.filter(tag => !this.tags.includes(tag.toLowerCase()));
  this.tags.push(...newTags.map(tag => tag.toLowerCase()));
  return this.save();
};

// Method to remove tags
generatedContentSchema.methods.removeTags = function(tags) {
  this.tags = this.tags.filter(tag => !tags.includes(tag.toLowerCase()));
  return this.save();
};

// Method to create revision
generatedContentSchema.methods.createRevision = function(content, note = '') {
  this.revisions.push({
    content,
    note,
    timestamp: new Date()
  });
  return this.save();
};

// Method to get export URL
generatedContentSchema.methods.getExportUrl = function(format) {
  const exportRecord = this.exports.find(exp => exp.format === format);
  return exportRecord ? exportRecord.url : null;
};

// Method to add export record
generatedContentSchema.methods.addExport = function(format, url) {
  this.exports.push({
    format,
    url,
    downloadedAt: new Date()
  });
  return this.save();
};

// Static method to find by user
generatedContentSchema.statics.findByUser = function(userId, options = {}) {
  const query = { userId };
  
  if (options.templateId) {
    query.templateId = options.templateId;
  }
  
  if (options.status) {
    query.status = options.status;
  }
  
  if (options.isFavorite !== undefined) {
    query.isFavorite = options.isFavorite;
  }
  
  if (options.tags && options.tags.length > 0) {
    query.tags = { $in: options.tags.map(tag => tag.toLowerCase()) };
  }
  
  return this.find(query)
    .populate('templateId', 'name category')
    .sort({ createdAt: -1 });
};

// Static method to get user statistics
generatedContentSchema.statics.getUserStats = function(userId) {
  return this.aggregate([
    { $match: { userId: mongoose.Types.ObjectId(userId) } },
    {
      $group: {
        _id: null,
        totalContent: { $sum: 1 },
        totalWords: { $sum: { $strLenCP: '$content' } },
        totalCost: { $sum: '$metadata.cost' },
        averageRating: { $avg: '$rating' },
        totalViews: { $sum: '$views' },
        totalCopies: { $sum: '$copies' },
        totalShares: { $sum: '$shares' },
        favoriteCount: {
          $sum: { $cond: ['$isFavorite', 1, 0] }
        }
      }
    }
  ]);
};

// Static method to get popular content
generatedContentSchema.statics.getPopularContent = function(limit = 10) {
  return this.find({ status: 'completed' })
    .sort({ views: -1, copies: -1, shares: -1 })
    .limit(limit)
    .populate('userId', 'firstName lastName')
    .populate('templateId', 'name category');
};

// Static method to get content by date range
generatedContentSchema.statics.getContentByDateRange = function(startDate, endDate, userId = null) {
  const query = {
    createdAt: {
      $gte: startDate,
      $lte: endDate
    },
    status: 'completed'
  };
  
  if (userId) {
    query.userId = userId;
  }
  
  return this.find(query)
    .populate('userId', 'firstName lastName')
    .populate('templateId', 'name category')
    .sort({ createdAt: -1 });
};

module.exports = mongoose.model('GeneratedContent', generatedContentSchema);









