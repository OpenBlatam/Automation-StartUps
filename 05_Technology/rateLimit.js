const { RateLimiterMemory } = require('rate-limiter-flexible');

/**
 * Rate Limiting Middleware
 * Prevents abuse and ensures fair usage
 */

// General rate limiter
const generalLimiter = new RateLimiterMemory({
  keyPrefix: 'general',
  points: 100, // Number of requests
  duration: 60, // Per 60 seconds
});

// API rate limiter (more restrictive)
const apiLimiter = new RateLimiterMemory({
  keyPrefix: 'api',
  points: 50, // Number of requests
  duration: 60, // Per 60 seconds
});

// Content generation rate limiter
const contentLimiter = new RateLimiterMemory({
  keyPrefix: 'content',
  points: 20, // Number of content generations
  duration: 60, // Per 60 seconds
});

// Neural consciousness rate limiter
const neuralLimiter = new RateLimiterMemory({
  keyPrefix: 'neural',
  points: 10, // Number of neural operations
  duration: 60, // Per 60 seconds
});

/**
 * General rate limiting middleware
 */
const rateLimitMiddleware = async (req, res, next) => {
  try {
    const key = req.ip || 'unknown';
    await generalLimiter.consume(key);
    next();
  } catch (rejRes) {
    const secs = Math.round(rejRes.msBeforeNext / 1000) || 1;
    res.set('Retry-After', String(secs));
    res.status(429).json({
      success: false,
      error: 'Too many requests. Please try again later.',
      retryAfter: secs
    });
  }
};

/**
 * API rate limiting middleware
 */
const apiRateLimit = async (req, res, next) => {
  try {
    const key = req.ip || 'unknown';
    await apiLimiter.consume(key);
    next();
  } catch (rejRes) {
    const secs = Math.round(rejRes.msBeforeNext / 1000) || 1;
    res.set('Retry-After', String(secs));
    res.status(429).json({
      success: false,
      error: 'API rate limit exceeded. Please try again later.',
      retryAfter: secs
    });
  }
};

/**
 * Content generation rate limiting
 */
const contentRateLimit = async (req, res, next) => {
  try {
    const key = req.user ? req.user.id : req.ip;
    await contentLimiter.consume(key);
    next();
  } catch (rejRes) {
    const secs = Math.round(rejRes.msBeforeNext / 1000) || 1;
    res.set('Retry-After', String(secs));
    res.status(429).json({
      success: false,
      error: 'Content generation rate limit exceeded. Please try again later.',
      retryAfter: secs
    });
  }
};

/**
 * Neural consciousness rate limiting
 */
const neuralRateLimit = async (req, res, next) => {
  try {
    const key = req.user ? req.user.id : req.ip;
    await neuralLimiter.consume(key);
    next();
  } catch (rejRes) {
    const secs = Math.round(rejRes.msBeforeNext / 1000) || 1;
    res.set('Retry-After', String(secs));
    res.status(429).json({
      success: false,
      error: 'Neural consciousness rate limit exceeded. Please try again later.',
      retryAfter: secs
    });
  }
};

/**
 * Dynamic rate limiting based on user tier
 */
const dynamicRateLimit = (tierLimits) => {
  return async (req, res, next) => {
    try {
      const userTier = req.user?.tier || 'free';
      const limits = tierLimits[userTier] || tierLimits.free;
      
      const limiter = new RateLimiterMemory({
        keyPrefix: `dynamic_${userTier}`,
        points: limits.requests,
        duration: limits.duration
      });
      
      const key = req.user ? req.user.id : req.ip;
      await limiter.consume(key);
      next();
    } catch (rejRes) {
      const secs = Math.round(rejRes.msBeforeNext / 1000) || 1;
      res.set('Retry-After', String(secs));
      res.status(429).json({
        success: false,
        error: 'Rate limit exceeded for your tier. Please upgrade for higher limits.',
        retryAfter: secs,
        tier: req.user?.tier || 'free'
      });
    }
  };
};

/**
 * Burst rate limiting for high-traffic endpoints
 */
const burstRateLimit = new RateLimiterMemory({
  keyPrefix: 'burst',
  points: 10, // Allow 10 requests
  duration: 1, // Per 1 second
});

const burstRateLimitMiddleware = async (req, res, next) => {
  try {
    const key = req.ip || 'unknown';
    await burstRateLimit.consume(key);
    next();
  } catch (rejRes) {
    res.status(429).json({
      success: false,
      error: 'Too many requests in a short time. Please slow down.',
      retryAfter: 1
    });
  }
};

/**
 * Tier-based rate limits
 */
const tierLimits = {
  free: {
    requests: 100,
    duration: 3600, // 1 hour
    contentGenerations: 10,
    neuralOperations: 5
  },
  pro: {
    requests: 1000,
    duration: 3600, // 1 hour
    contentGenerations: 100,
    neuralOperations: 50
  },
  enterprise: {
    requests: 10000,
    duration: 3600, // 1 hour
    contentGenerations: 1000,
    neuralOperations: 500
  }
};

/**
 * Get rate limit info for user
 */
const getRateLimitInfo = async (req) => {
  const userTier = req.user?.tier || 'free';
  const limits = tierLimits[userTier];
  
  try {
    const key = req.user ? req.user.id : req.ip;
    
    // Get current usage for general requests
    const generalUsage = await generalLimiter.get(key);
    const remaining = generalUsage ? limits.requests - generalUsage.remainingPoints : limits.requests;
    
    return {
      tier: userTier,
      limits: limits,
      remaining: Math.max(0, remaining),
      resetTime: generalUsage ? new Date(Date.now() + generalUsage.msBeforeNext) : null
    };
  } catch (error) {
    return {
      tier: userTier,
      limits: limits,
      remaining: limits.requests,
      resetTime: null
    };
  }
};

module.exports = {
  rateLimitMiddleware,
  apiRateLimit,
  contentRateLimit,
  neuralRateLimit,
  dynamicRateLimit,
  burstRateLimitMiddleware,
  getRateLimitInfo,
  tierLimits
};

