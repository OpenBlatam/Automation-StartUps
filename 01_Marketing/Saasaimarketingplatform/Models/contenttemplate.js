const mongoose = require('mongoose');

const contentTemplateSchema = new mongoose.Schema({
  // Basic Information
  name: {
    type: String,
    required: [true, 'Template name is required'],
    trim: true,
    maxlength: [100, 'Template name cannot exceed 100 characters']
  },
  description: {
    type: String,
    required: [true, 'Template description is required'],
    maxlength: [500, 'Description cannot exceed 500 characters']
  },
  category: {
    type: String,
    required: [true, 'Template category is required'],
    enum: [
      'email-marketing',
      'social-media',
      'blog-content',
      'ad-copy',
      'product-descriptions',
      'landing-pages',
      'sales-copy',
      'performance-reviews',
      'presentations',
      'reports',
      'other'
    ]
  },
  subcategory: {
    type: String,
    trim: true
  },
  
  // Template Content
  prompt: {
    type: String,
    required: [true, 'Template prompt is required'],
    maxlength: [2000, 'Prompt cannot exceed 2000 characters']
  },
  variables: [{
    name: {
      type: String,
      required: true
    },
    label: {
      type: String,
      required: true
    },
    type: {
      type: String,
      enum: ['text', 'textarea', 'select', 'number', 'boolean', 'date'],
      default: 'text'
    },
    required: {
      type: Boolean,
      default: false
    },
    placeholder: {
      type: String
    },
    options: [{
      value: String,
      label: String
    }],
    validation: {
      minLength: Number,
      maxLength: Number,
      pattern: String
    }
  }],
  
  // AI Configuration
  aiSettings: {
    model: {
      type: String,
      default: 'gpt-3.5-turbo',
      enum: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo', 'claude-3-sonnet', 'claude-3-opus']
    },
    temperature: {
      type: Number,
      min: 0,
      max: 2,
      default: 0.7
    },
    maxTokens: {
      type: Number,
      min: 50,
      max: 4000,
      default: 500
    },
    systemPrompt: {
      type: String,
      maxlength: [1000, 'System prompt cannot exceed 1000 characters']
    }
  },
  
  // Template Metadata
  tags: [{
    type: String,
    trim: true,
    lowercase: true
  }],
  difficulty: {
    type: String,
    enum: ['beginner', 'intermediate', 'advanced'],
    default: 'beginner'
  },
  estimatedTime: {
    type: Number, // in minutes
    default: 5
  },
  
  // Usage and Performance
  usage: {
    totalUses: {
      type: Number,
      default: 0
    },
    successfulGenerations: {
      type: Number,
      default: 0
    },
    averageRating: {
      type: Number,
      min: 0,
      max: 5,
      default: 0
    },
    totalRatings: {
      type: Number,
      default: 0
    }
  },
  
  // Access Control
  visibility: {
    type: String,
    enum: ['public', 'private', 'premium'],
    default: 'public'
  },
  requiredPlan: {
    type: String,
    enum: ['free', 'basic', 'professional', 'enterprise'],
    default: 'free'
  },
  
  // Creator Information
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  isOfficial: {
    type: Boolean,
    default: false
  },
  
  // Version Control
  version: {
    type: String,
    default: '1.0.0'
  },
  changelog: [{
    version: String,
    changes: String,
    date: {
      type: Date,
      default: Date.now
    }
  }],
  
  // Status
  isActive: {
    type: Boolean,
    default: true
  },
  isFeatured: {
    type: Boolean,
    default: false
  },
  
  // Examples and Documentation
  examples: [{
    title: String,
    input: mongoose.Schema.Types.Mixed,
    output: String,
    description: String
  }],
  documentation: {
    instructions: String,
    tips: [String],
    bestPractices: [String],
    commonMistakes: [String]
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Virtual for success rate
contentTemplateSchema.virtual('successRate').get(function() {
  if (this.usage.totalUses === 0) return 0;
  return (this.usage.successfulGenerations / this.usage.totalUses) * 100;
});

// Virtual for popularity score
contentTemplateSchema.virtual('popularityScore').get(function() {
  const usageWeight = Math.log(this.usage.totalUses + 1) * 0.4;
  const ratingWeight = this.usage.averageRating * 0.3;
  const recencyWeight = Math.log(Date.now() - this.createdAt.getTime() + 1) * 0.3;
  return usageWeight + ratingWeight + recencyWeight;
});

// Indexes for better performance
contentTemplateSchema.index({ category: 1, subcategory: 1 });
contentTemplateSchema.index({ tags: 1 });
contentTemplateSchema.index({ visibility: 1, requiredPlan: 1 });
contentTemplateSchema.index({ isActive: 1, isFeatured: 1 });
contentTemplateSchema.index({ 'usage.totalUses': -1 });
contentTemplateSchema.index({ createdAt: -1 });

// Pre-save middleware to update version
contentTemplateSchema.pre('save', function(next) {
  if (this.isModified('prompt') || this.isModified('variables') || this.isModified('aiSettings')) {
    // Increment version
    const versionParts = this.version.split('.');
    const patch = parseInt(versionParts[2]) + 1;
    this.version = `${versionParts[0]}.${versionParts[1]}.${patch}`;
    
    // Add to changelog
    this.changelog.push({
      version: this.version,
      changes: 'Template updated',
      date: new Date()
    });
  }
  next();
});

// Method to increment usage
contentTemplateSchema.methods.incrementUsage = function(successful = true) {
  this.usage.totalUses += 1;
  if (successful) {
    this.usage.successfulGenerations += 1;
  }
  return this.save();
};

// Method to add rating
contentTemplateSchema.methods.addRating = function(rating) {
  if (rating < 0 || rating > 5) {
    throw new Error('Rating must be between 0 and 5');
  }
  
  const totalRating = this.usage.averageRating * this.usage.totalRatings + rating;
  this.usage.totalRatings += 1;
  this.usage.averageRating = totalRating / this.usage.totalRatings;
  
  return this.save();
};

// Method to generate content
contentTemplateSchema.methods.generateContent = async function(variables, aiService) {
  try {
    // Replace variables in prompt
    let processedPrompt = this.prompt;
    for (const [key, value] of Object.entries(variables)) {
      const placeholder = `{${key}}`;
      processedPrompt = processedPrompt.replace(new RegExp(placeholder, 'g'), value);
    }
    
    // Generate content using AI service
    const content = await aiService.generateContent({
      prompt: processedPrompt,
      systemPrompt: this.aiSettings.systemPrompt,
      model: this.aiSettings.model,
      temperature: this.aiSettings.temperature,
      maxTokens: this.aiSettings.maxTokens
    });
    
    // Increment usage
    await this.incrementUsage(true);
    
    return content;
  } catch (error) {
    await this.incrementUsage(false);
    throw error;
  }
};

// Static method to find by category
contentTemplateSchema.statics.findByCategory = function(category, plan = 'free') {
  return this.find({
    category,
    isActive: true,
    $or: [
      { requiredPlan: 'free' },
      { requiredPlan: { $lte: plan } }
    ]
  }).sort({ 'usage.totalUses': -1 });
};

// Static method to find featured templates
contentTemplateSchema.statics.findFeatured = function(plan = 'free') {
  return this.find({
    isFeatured: true,
    isActive: true,
    $or: [
      { requiredPlan: 'free' },
      { requiredPlan: { $lte: plan } }
    ]
  }).sort({ 'usage.totalUses': -1 });
};

// Static method to search templates
contentTemplateSchema.statics.searchTemplates = function(query, plan = 'free') {
  const searchRegex = new RegExp(query, 'i');
  return this.find({
    $and: [
      {
        $or: [
          { name: searchRegex },
          { description: searchRegex },
          { tags: searchRegex }
        ]
      },
      { isActive: true },
      {
        $or: [
          { requiredPlan: 'free' },
          { requiredPlan: { $lte: plan } }
        ]
      }
    ]
  }).sort({ 'usage.totalUses': -1 });
};

module.exports = mongoose.model('ContentTemplate', contentTemplateSchema);









