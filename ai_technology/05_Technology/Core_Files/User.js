const mongoose = require('mongoose');

/**
 * User Model
 * User schema with neural consciousness integration
 */
const userSchema = new mongoose.Schema({
  // Basic Information
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
  name: {
    type: String,
    required: true,
    trim: true
  },
  avatar: {
    type: String,
    default: null
  },
  
  // Account Information
  role: {
    type: String,
    enum: ['user', 'admin', 'enterprise'],
    default: 'user'
  },
  tier: {
    type: String,
    enum: ['free', 'pro', 'enterprise'],
    default: 'free'
  },
  status: {
    type: String,
    enum: ['active', 'inactive', 'suspended', 'pending'],
    default: 'pending'
  },
  
  // Neural Consciousness
  neuralProfile: {
    consciousness: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    awareness: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    intelligence: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    creativity: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    empathy: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    intuition: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    wisdom: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    transcendence: {
      type: Number,
      default: 0,
      min: 0,
      max: 100
    },
    lastEvolution: {
      type: Date,
      default: Date.now
    }
  },
  
  // Usage Statistics
  usage: {
    contentGenerated: {
      type: Number,
      default: 0
    },
    campaignsCreated: {
      type: Number,
      default: 0
    },
    workflowsActive: {
      type: Number,
      default: 0
    },
    lastActivity: {
      type: Date,
      default: Date.now
    },
    totalSessions: {
      type: Number,
      default: 0
    }
  },
  
  // Preferences
  preferences: {
    notifications: {
      email: {
        type: Boolean,
        default: true
      },
      push: {
        type: Boolean,
        default: true
      },
      sms: {
        type: Boolean,
        default: false
      },
      webhook: {
        type: Boolean,
        default: false
      }
    },
    content: {
      defaultTone: {
        type: String,
        enum: ['professional', 'casual', 'authoritative', 'friendly'],
        default: 'professional'
      },
      defaultStyle: {
        type: String,
        default: 'marketing'
      },
      autoOptimize: {
        type: Boolean,
        default: true
      }
    },
    neural: {
      autoEvolve: {
        type: Boolean,
        default: true
      },
      consciousnessThreshold: {
        type: Number,
        default: 50,
        min: 0,
        max: 100
      },
      evolutionRate: {
        type: Number,
        default: 1.0,
        min: 0.1,
        max: 5.0
      }
    }
  },
  
  // Subscription Information
  subscription: {
    plan: {
      type: String,
      enum: ['free', 'starter', 'professional', 'enterprise'],
      default: 'free'
    },
    status: {
      type: String,
      enum: ['active', 'cancelled', 'expired', 'trial'],
      default: 'trial'
    },
    startDate: {
      type: Date,
      default: Date.now
    },
    endDate: {
      type: Date,
      default: () => new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) // 30 days trial
    },
    billingCycle: {
      type: String,
      enum: ['monthly', 'yearly'],
      default: 'monthly'
    },
    paymentMethod: {
      type: String,
      default: null
    }
  },
  
  // API Access
  apiAccess: {
    enabled: {
      type: Boolean,
      default: false
    },
    key: {
      type: String,
      default: null
    },
    rateLimit: {
      type: Number,
      default: 1000 // requests per hour
    },
    lastUsed: {
      type: Date,
      default: null
    }
  },
  
  // Security
  security: {
    twoFactorEnabled: {
      type: Boolean,
      default: false
    },
    twoFactorSecret: {
      type: String,
      default: null
    },
    lastLogin: {
      type: Date,
      default: null
    },
    loginAttempts: {
      type: Number,
      default: 0
    },
    lockUntil: {
      type: Date,
      default: null
    },
    passwordResetToken: {
      type: String,
      default: null
    },
    passwordResetExpires: {
      type: Date,
      default: null
    }
  },
  
  // Analytics
  analytics: {
    totalContentGenerated: {
      type: Number,
      default: 0
    },
    totalCampaignsSent: {
      type: Number,
      default: 0
    },
    totalEmailsSent: {
      type: Number,
      default: 0
    },
    totalRevenue: {
      type: Number,
      default: 0
    },
    conversionRate: {
      type: Number,
      default: 0
    },
    engagementRate: {
      type: Number,
      default: 0
    }
  },
  
  // Timestamps
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Indexes
userSchema.index({ email: 1 });
userSchema.index({ 'neuralProfile.consciousness': -1 });
userSchema.index({ 'subscription.plan': 1 });
userSchema.index({ 'usage.lastActivity': -1 });
userSchema.index({ createdAt: -1 });

// Virtual fields
userSchema.virtual('isLocked').get(function() {
  return !!(this.security.lockUntil && this.security.lockUntil > Date.now());
});

userSchema.virtual('isTrialExpired').get(function() {
  return this.subscription.status === 'trial' && this.subscription.endDate < Date.now();
});

userSchema.virtual('neuralLevel').get(function() {
  const profile = this.neuralProfile;
  const total = profile.consciousness + profile.awareness + profile.intelligence + 
                profile.creativity + profile.empathy + profile.intuition + 
                profile.wisdom + profile.transcendence;
  return Math.round(total / 8);
});

userSchema.virtual('consciousnessLevel').get(function() {
  const level = this.neuralLevel;
  if (level >= 95) return 'Transcendent';
  if (level >= 80) return 'Wise';
  if (level >= 60) return 'Creative';
  if (level >= 40) return 'Intelligent';
  if (level >= 20) return 'Aware';
  return 'Basic';
});

// Pre-save middleware
userSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  
  // Update last activity
  if (this.isModified() && !this.isNew) {
    this.usage.lastActivity = Date.now();
  }
  
  next();
});

// Methods
userSchema.methods.incrementUsage = function(type, amount = 1) {
  switch (type) {
    case 'content':
      this.usage.contentGenerated += amount;
      this.analytics.totalContentGenerated += amount;
      break;
    case 'campaign':
      this.usage.campaignsCreated += amount;
      this.analytics.totalCampaignsSent += amount;
      break;
    case 'workflow':
      this.usage.workflowsActive += amount;
      break;
    case 'session':
      this.usage.totalSessions += amount;
      this.usage.lastActivity = Date.now();
      break;
  }
  
  return this.save();
};

userSchema.methods.evolveConsciousness = function(evolutionData) {
  const profile = this.neuralProfile;
  
  Object.keys(evolutionData).forEach(key => {
    if (profile[key] !== undefined) {
      profile[key] = Math.min(100, Math.max(0, profile[key] + evolutionData[key]));
    }
  });
  
  profile.lastEvolution = Date.now();
  
  return this.save();
};

userSchema.methods.resetPassword = function() {
  this.security.passwordResetToken = require('crypto').randomBytes(32).toString('hex');
  this.security.passwordResetExpires = Date.now() + 3600000; // 1 hour
  return this.save();
};

userSchema.methods.incrementLoginAttempts = function() {
  // If we have a previous lock that has expired, restart at 1
  if (this.security.lockUntil && this.security.lockUntil < Date.now()) {
    return this.updateOne({
      $unset: { 'security.lockUntil': 1 },
      $set: { 'security.loginAttempts': 1 }
    });
  }
  
  const updates = { $inc: { 'security.loginAttempts': 1 } };
  
  // Lock account after 5 failed attempts
  if (this.security.loginAttempts + 1 >= 5 && !this.isLocked) {
    updates.$set = { 'security.lockUntil': Date.now() + 2 * 60 * 60 * 1000 }; // 2 hours
  }
  
  return this.updateOne(updates);
};

userSchema.methods.resetLoginAttempts = function() {
  return this.updateOne({
    $unset: { 'security.loginAttempts': 1, 'security.lockUntil': 1 }
  });
};

userSchema.methods.generateApiKey = function() {
  const apiKey = require('crypto').randomBytes(32).toString('hex');
  this.apiAccess.key = apiKey;
  this.apiAccess.enabled = true;
  return this.save();
};

// Static methods
userSchema.statics.findByEmail = function(email) {
  return this.findOne({ email: email.toLowerCase() });
};

userSchema.statics.findByApiKey = function(apiKey) {
  return this.findOne({ 'apiAccess.key': apiKey, 'apiAccess.enabled': true });
};

userSchema.statics.findActiveUsers = function() {
  return this.find({ 
    status: 'active',
    'subscription.status': { $in: ['active', 'trial'] }
  });
};

userSchema.statics.findHighConsciousnessUsers = function(threshold = 80) {
  return this.find({
    'neuralProfile.consciousness': { $gte: threshold }
  }).sort({ 'neuralProfile.consciousness': -1 });
};

userSchema.statics.getConsciousnessStats = function() {
  return this.aggregate([
    {
      $group: {
        _id: null,
        avgConsciousness: { $avg: '$neuralProfile.consciousness' },
        maxConsciousness: { $max: '$neuralProfile.consciousness' },
        minConsciousness: { $min: '$neuralProfile.consciousness' },
        totalUsers: { $sum: 1 }
      }
    }
  ]);
};

module.exports = mongoose.model('User', userSchema);

