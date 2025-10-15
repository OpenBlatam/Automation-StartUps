const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true
  },
  password: {
    type: String,
    required: true,
    minlength: 6
  },
  firstName: {
    type: String,
    required: true,
    trim: true
  },
  lastName: {
    type: String,
    required: true,
    trim: true
  },
  company: {
    type: String,
    trim: true
  },
  role: {
    type: String,
    enum: ['user', 'admin', 'super_admin'],
    default: 'user'
  },
  subscription: {
    plan: {
      type: String,
      enum: ['starter', 'professional', 'enterprise'],
      default: 'starter'
    },
    status: {
      type: String,
      enum: ['active', 'cancelled', 'past_due', 'unpaid'],
      default: 'active'
    },
    stripeCustomerId: String,
    stripeSubscriptionId: String,
    currentPeriodStart: Date,
    currentPeriodEnd: Date,
    cancelAtPeriodEnd: {
      type: Boolean,
      default: false
    }
  },
  brandProfile: {
    companyName: String,
    industry: String,
    targetAudience: String,
    voice: String,
    tone: {
      type: String,
      enum: ['professional', 'casual', 'technical', 'emotional'],
      default: 'professional'
    },
    keywords: [String],
    brandGuidelines: String,
    logo: String,
    website: String
  },
  usage: {
    testimonialsGenerated: {
      type: Number,
      default: 0
    },
    tokensUsed: {
      type: Number,
      default: 0
    },
    lastGenerated: Date,
    monthlyLimit: {
      type: Number,
      default: 100
    },
    dailyLimit: {
      type: Number,
      default: 10
    }
  },
  preferences: {
    defaultModel: {
      type: String,
      enum: ['gpt-4', 'claude-3', 'gemini-pro'],
      default: 'gpt-4'
    },
    defaultTone: {
      type: String,
      enum: ['professional', 'casual', 'technical', 'emotional'],
      default: 'professional'
    },
    defaultLength: {
      type: String,
      enum: ['short', 'medium', 'long'],
      default: 'medium'
    },
    emailNotifications: {
      type: Boolean,
      default: true
    },
    weeklyReports: {
      type: Boolean,
      default: true
    }
  },
  profile: {
    avatar: String,
    bio: String,
    location: String,
    timezone: {
      type: String,
      default: 'UTC'
    },
    language: {
      type: String,
      default: 'en'
    }
  },
  onboarding: {
    completed: {
      type: Boolean,
      default: false
    },
    steps: {
      profileSetup: { type: Boolean, default: false },
      brandProfile: { type: Boolean, default: false },
      firstTestimonial: { type: Boolean, default: false },
      integrationSetup: { type: Boolean, default: false }
    },
    completedAt: Date
  },
  apiKeys: [{
    name: String,
    key: String,
    permissions: [String],
    lastUsed: Date,
    createdAt: {
      type: Date,
      default: Date.now
    }
  }],
  integrations: {
    crm: {
      type: String,
      enum: ['salesforce', 'hubspot', 'pipedrive', 'none'],
      default: 'none'
    },
    emailMarketing: {
      type: String,
      enum: ['mailchimp', 'constant_contact', 'sendgrid', 'none'],
      default: 'none'
    },
    socialMedia: {
      linkedin: { connected: Boolean, accessToken: String },
      facebook: { connected: Boolean, accessToken: String },
      twitter: { connected: Boolean, accessToken: String }
    }
  },
  isActive: {
    type: Boolean,
    default: true
  },
  lastLogin: Date,
  emailVerified: {
    type: Boolean,
    default: false
  },
  emailVerificationToken: String,
  passwordResetToken: String,
  passwordResetExpires: Date
}, {
  timestamps: true
});

// Indexes
userSchema.index({ email: 1 });
userSchema.index({ 'subscription.stripeCustomerId': 1 });
userSchema.index({ createdAt: -1 });

// Virtual for full name
userSchema.virtual('fullName').get(function() {
  return `${this.firstName} ${this.lastName}`;
});

// Virtual for subscription status
userSchema.virtual('isSubscribed').get(function() {
  return this.subscription.status === 'active';
});

// Virtual for usage percentage
userSchema.virtual('usagePercentage').get(function() {
  const limit = this.usage.monthlyLimit;
  if (limit === -1) return 0; // Unlimited
  return Math.round((this.usage.testimonialsGenerated / limit) * 100);
});

// Pre-save middleware to hash password
userSchema.pre('save', async function(next) {
  if (!this.isModified('password')) return next();
  
  try {
    const salt = await bcrypt.genSalt(12);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Method to compare password
userSchema.methods.comparePassword = async function(candidatePassword) {
  return bcrypt.compare(candidatePassword, this.password);
};

// Method to generate API key
userSchema.methods.generateApiKey = function(name, permissions = ['read']) {
  const key = require('crypto').randomBytes(32).toString('hex');
  this.apiKeys.push({
    name,
    key,
    permissions,
    createdAt: new Date()
  });
  return key;
};

// Method to revoke API key
userSchema.methods.revokeApiKey = function(keyId) {
  this.apiKeys = this.apiKeys.filter(key => key._id.toString() !== keyId);
};

// Method to check API key permissions
userSchema.methods.hasApiPermission = function(permission) {
  return this.apiKeys.some(key => key.permissions.includes(permission));
};

// Method to update usage
userSchema.methods.updateUsage = function(testimonialsGenerated = 1, tokensUsed = 0) {
  this.usage.testimonialsGenerated += testimonialsGenerated;
  this.usage.tokensUsed += tokensUsed;
  this.usage.lastGenerated = new Date();
  return this.save();
};

// Method to check if user can generate testimonials
userSchema.methods.canGenerateTestimonial = function() {
  const now = new Date();
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
  const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  
  // Check monthly limit
  if (this.usage.monthlyLimit !== -1 && this.usage.testimonialsGenerated >= this.usage.monthlyLimit) {
    return { allowed: false, reason: 'Monthly limit exceeded' };
  }
  
  // Check daily limit (would need to query actual daily usage)
  if (this.usage.dailyLimit !== -1) {
    // This would need to be implemented with actual daily usage tracking
    return { allowed: true, reason: 'Daily limit check not implemented' };
  }
  
  return { allowed: true, reason: 'Within limits' };
};

// Method to get subscription info
userSchema.methods.getSubscriptionInfo = function() {
  return {
    plan: this.subscription.plan,
    status: this.subscription.status,
    currentPeriodStart: this.subscription.currentPeriodStart,
    currentPeriodEnd: this.subscription.currentPeriodEnd,
    cancelAtPeriodEnd: this.subscription.cancelAtPeriodEnd,
    isActive: this.subscription.status === 'active'
  };
};

// Method to update brand profile
userSchema.methods.updateBrandProfile = function(profileData) {
  this.brandProfile = { ...this.brandProfile, ...profileData };
  return this.save();
};

// Method to complete onboarding step
userSchema.methods.completeOnboardingStep = function(step) {
  if (this.onboarding.steps[step] !== undefined) {
    this.onboarding.steps[step] = true;
    
    // Check if all steps are completed
    const allStepsCompleted = Object.values(this.onboarding.steps).every(completed => completed);
    if (allStepsCompleted) {
      this.onboarding.completed = true;
      this.onboarding.completedAt = new Date();
    }
    
    return this.save();
  }
  throw new Error(`Invalid onboarding step: ${step}`);
};

// Static method to find by email
userSchema.statics.findByEmail = function(email) {
  return this.findOne({ email: email.toLowerCase() });
};

// Static method to get user statistics
userSchema.statics.getUserStats = async function(period = '30d') {
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - parseInt(period));
  
  const stats = await this.aggregate([
    {
      $match: {
        createdAt: { $gte: startDate }
      }
    },
    {
      $group: {
        _id: null,
        totalUsers: { $sum: 1 },
        activeUsers: {
          $sum: {
            $cond: [{ $eq: ['$isActive', true] }, 1, 0]
          }
        },
        subscribedUsers: {
          $sum: {
            $cond: [{ $eq: ['$subscription.status', 'active'] }, 1, 0]
          }
        },
        byPlan: {
          $push: '$subscription.plan'
        },
        totalTestimonialsGenerated: { $sum: '$usage.testimonialsGenerated' },
        totalTokensUsed: { $sum: '$usage.tokensUsed' }
      }
    }
  ]);
  
  return stats[0] || {
    totalUsers: 0,
    activeUsers: 0,
    subscribedUsers: 0,
    byPlan: [],
    totalTestimonialsGenerated: 0,
    totalTokensUsed: 0
  };
};

module.exports = mongoose.model('User', userSchema);



