const jwt = require('jsonwebtoken');
const User = require('../models/User');

const authMiddleware = async (req, res, next) => {
  try {
    // Get token from header
    const authHeader = req.header('Authorization');
    
    if (!authHeader) {
      return res.status(401).json({
        success: false,
        message: 'No token provided, authorization denied'
      });
    }

    // Check if token starts with 'Bearer '
    if (!authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        success: false,
        message: 'Invalid token format'
      });
    }

    // Extract token
    const token = authHeader.substring(7);

    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'No token provided, authorization denied'
      });
    }

    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Get user from database
    const user = await User.findById(decoded.userId).select('-password');
    
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Token is valid but user not found'
      });
    }

    // Check if user is active
    if (!user.isActive) {
      return res.status(401).json({
        success: false,
        message: 'Account is deactivated'
      });
    }

    // Check if email is verified (optional, depending on your requirements)
    if (!user.isEmailVerified) {
      return res.status(401).json({
        success: false,
        message: 'Please verify your email address'
      });
    }

    // Add user to request object
    req.user = user;
    next();

  } catch (error) {
    console.error('Auth middleware error:', error);
    
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        success: false,
        message: 'Invalid token'
      });
    }
    
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        message: 'Token expired'
      });
    }

    res.status(500).json({
      success: false,
      message: 'Server error in authentication'
    });
  }
};

// Optional middleware for admin users
const adminMiddleware = async (req, res, next) => {
  try {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'Authentication required'
      });
    }

    // Check if user has admin role (you can modify this based on your user model)
    if (req.user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        message: 'Admin access required'
      });
    }

    next();
  } catch (error) {
    console.error('Admin middleware error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error in admin authentication'
    });
  }
};

// Middleware to check subscription status
const subscriptionMiddleware = (requiredPlan) => {
  return async (req, res, next) => {
    try {
      if (!req.user) {
        return res.status(401).json({
          success: false,
          message: 'Authentication required'
        });
      }

      const user = req.user;
      const planHierarchy = {
        free: 0,
        basic: 1,
        professional: 2,
        enterprise: 3
      };

      const userPlanLevel = planHierarchy[user.subscription.plan] || 0;
      const requiredPlanLevel = planHierarchy[requiredPlan] || 0;

      // Check if user's plan meets the requirement
      if (userPlanLevel < requiredPlanLevel) {
        return res.status(403).json({
          success: false,
          message: `This feature requires ${requiredPlan} plan or higher`,
          currentPlan: user.subscription.plan,
          requiredPlan: requiredPlan
        });
      }

      // Check if subscription is active
      if (user.subscription.status !== 'active') {
        return res.status(403).json({
          success: false,
          message: 'Active subscription required',
          subscriptionStatus: user.subscription.status
        });
      }

      // Check if subscription has expired
      if (user.subscription.endDate && new Date() > user.subscription.endDate) {
        return res.status(403).json({
          success: false,
          message: 'Subscription has expired'
        });
      }

      next();
    } catch (error) {
      console.error('Subscription middleware error:', error);
      res.status(500).json({
        success: false,
        message: 'Server error in subscription check'
      });
    }
  };
};

// Middleware to check usage limits
const usageLimitMiddleware = async (req, res, next) => {
  try {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'Authentication required'
      });
    }

    const user = req.user;
    
    // Check if user has reached their usage limit
    if (!user.checkUsageLimit()) {
      return res.status(429).json({
        success: false,
        message: 'Monthly usage limit exceeded',
        limit: user.usage.monthlyLimit,
        used: user.usage.contentGenerations,
        resetDate: user.usage.lastResetDate
      });
    }

    next();
  } catch (error) {
    console.error('Usage limit middleware error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error in usage limit check'
    });
  }
};

// Middleware for API key authentication (for external integrations)
const apiKeyMiddleware = async (req, res, next) => {
  try {
    const apiKey = req.header('X-API-Key');
    
    if (!apiKey) {
      return res.status(401).json({
        success: false,
        message: 'API key required'
      });
    }

    // Find user by API key
    const user = await User.findOne({ apiKey }).select('-password');
    
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Invalid API key'
      });
    }

    // Check if user is active
    if (!user.isActive) {
      return res.status(401).json({
        success: false,
        message: 'Account is deactivated'
      });
    }

    // Check API usage limits
    const now = new Date();
    const lastReset = new Date(user.apiUsage.lastResetDate);
    
    // Reset monthly API usage if it's a new month
    if (now.getMonth() !== lastReset.getMonth() || now.getFullYear() !== lastReset.getFullYear()) {
      user.apiUsage.requests = 0;
      user.apiUsage.lastResetDate = now;
      await user.save();
    }

    // Check API rate limits (adjust based on your requirements)
    const apiLimits = {
      free: 100,
      basic: 1000,
      professional: 5000,
      enterprise: -1 // Unlimited
    };

    const userLimit = apiLimits[user.subscription.plan] || apiLimits.free;
    
    if (userLimit !== -1 && user.apiUsage.requests >= userLimit) {
      return res.status(429).json({
        success: false,
        message: 'API rate limit exceeded',
        limit: userLimit,
        used: user.apiUsage.requests
      });
    }

    // Increment API usage
    user.apiUsage.requests += 1;
    await user.save();

    req.user = user;
    next();

  } catch (error) {
    console.error('API key middleware error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error in API key authentication'
    });
  }
};

// Middleware to log API requests
const requestLoggerMiddleware = (req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    const logData = {
      method: req.method,
      url: req.originalUrl,
      status: res.statusCode,
      duration: `${duration}ms`,
      userAgent: req.get('User-Agent'),
      ip: req.ip,
      userId: req.user?.id,
      timestamp: new Date().toISOString()
    };
    
    console.log(JSON.stringify(logData));
  });
  
  next();
};

module.exports = {
  authMiddleware,
  adminMiddleware,
  subscriptionMiddleware,
  usageLimitMiddleware,
  apiKeyMiddleware,
  requestLoggerMiddleware
};








