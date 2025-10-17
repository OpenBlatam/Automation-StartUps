const errorHandler = (err, req, res, next) => {
  let error = { ...err };
  error.message = err.message;

  // Log error
  console.error('Error:', err);

  // Mongoose bad ObjectId
  if (err.name === 'CastError') {
    const message = 'Resource not found';
    error = { message, statusCode: 404 };
  }

  // Mongoose duplicate key
  if (err.code === 11000) {
    const message = 'Duplicate field value entered';
    error = { message, statusCode: 400 };
  }

  // Mongoose validation error
  if (err.name === 'ValidationError') {
    const message = Object.values(err.errors).map(val => val.message).join(', ');
    error = { message, statusCode: 400 };
  }

  // JWT errors
  if (err.name === 'JsonWebTokenError') {
    const message = 'Invalid token';
    error = { message, statusCode: 401 };
  }

  if (err.name === 'TokenExpiredError') {
    const message = 'Token expired';
    error = { message, statusCode: 401 };
  }

  // OpenAI API errors
  if (err.name === 'OpenAIError') {
    const message = 'AI service error: ' + err.message;
    error = { message, statusCode: 502 };
  }

  // Stripe errors
  if (err.type && err.type.startsWith('Stripe')) {
    const message = 'Payment processing error: ' + err.message;
    error = { message, statusCode: 402 };
  }

  // Rate limiting errors
  if (err.statusCode === 429) {
    const message = 'Too many requests, please try again later';
    error = { message, statusCode: 429 };
  }

  // File upload errors
  if (err.code === 'LIMIT_FILE_SIZE') {
    const message = 'File too large';
    error = { message, statusCode: 413 };
  }

  if (err.code === 'LIMIT_UNEXPECTED_FILE') {
    const message = 'Unexpected file field';
    error = { message, statusCode: 400 };
  }

  // Database connection errors
  if (err.name === 'MongoNetworkError') {
    const message = 'Database connection error';
    error = { message, statusCode: 503 };
  }

  // Redis connection errors
  if (err.message && err.message.includes('Redis')) {
    const message = 'Cache service error';
    error = { message, statusCode: 503 };
  }

  // Default to 500 server error
  const statusCode = error.statusCode || 500;
  const message = error.message || 'Server Error';

  // Send error response
  res.status(statusCode).json({
    success: false,
    message: message,
    ...(process.env.NODE_ENV === 'development' && { 
      stack: err.stack,
      error: err 
    })
  });
};

// Async error handler wrapper
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

// 404 handler
const notFound = (req, res, next) => {
  const error = new Error(`Not Found - ${req.originalUrl}`);
  res.status(404);
  next(error);
};

// Validation error formatter
const formatValidationErrors = (errors) => {
  const formattedErrors = {};
  
  if (Array.isArray(errors)) {
    errors.forEach(error => {
      if (error.path) {
        formattedErrors[error.path] = error.message;
      }
    });
  } else if (errors.errors) {
    Object.keys(errors.errors).forEach(key => {
      formattedErrors[key] = errors.errors[key].message;
    });
  }
  
  return formattedErrors;
};

// Custom error class
class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;

    Error.captureStackTrace(this, this.constructor);
  }
}

// Error logging utility
const logError = (error, req = null) => {
  const errorLog = {
    timestamp: new Date().toISOString(),
    message: error.message,
    stack: error.stack,
    statusCode: error.statusCode || 500,
    url: req?.originalUrl,
    method: req?.method,
    ip: req?.ip,
    userAgent: req?.get('User-Agent'),
    userId: req?.user?.id
  };

  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.error('Error Log:', JSON.stringify(errorLog, null, 2));
  }

  // Here you could send to external logging service like Sentry, LogRocket, etc.
  // Example: Sentry.captureException(error, { extra: errorLog });
};

// Rate limiting error handler
const rateLimitHandler = (req, res) => {
  res.status(429).json({
    success: false,
    message: 'Too many requests from this IP, please try again later',
    retryAfter: Math.round(req.rateLimit.resetTime / 1000)
  });
};

// CORS error handler
const corsErrorHandler = (err, req, res, next) => {
  if (err.message === 'Not allowed by CORS') {
    res.status(403).json({
      success: false,
      message: 'CORS policy violation'
    });
  } else {
    next(err);
  }
};

// Security error handler
const securityErrorHandler = (err, req, res, next) => {
  if (err.name === 'UnauthorizedError') {
    res.status(401).json({
      success: false,
      message: 'Unauthorized access'
    });
  } else {
    next(err);
  }
};

// Database error handler
const databaseErrorHandler = (err, req, res, next) => {
  if (err.name === 'MongoError' || err.name === 'MongooseError') {
    logError(err, req);
    res.status(503).json({
      success: false,
      message: 'Database service temporarily unavailable'
    });
  } else {
    next(err);
  }
};

// API error handler for external services
const apiErrorHandler = (err, req, res, next) => {
  if (err.response) {
    // External API error
    const statusCode = err.response.status || 502;
    const message = err.response.data?.message || 'External service error';
    
    logError(err, req);
    res.status(statusCode).json({
      success: false,
      message: message,
      service: err.config?.url
    });
  } else {
    next(err);
  }
};

// File upload error handler
const fileUploadErrorHandler = (err, req, res, next) => {
  if (err.code === 'LIMIT_FILE_SIZE') {
    res.status(413).json({
      success: false,
      message: 'File size too large',
      maxSize: process.env.MAX_FILE_SIZE || '10MB'
    });
  } else if (err.code === 'LIMIT_FILE_COUNT') {
    res.status(400).json({
      success: false,
      message: 'Too many files uploaded',
      maxCount: 5
    });
  } else if (err.code === 'LIMIT_UNEXPECTED_FILE') {
    res.status(400).json({
      success: false,
      message: 'Unexpected file field'
    });
  } else {
    next(err);
  }
};

// Memory error handler
const memoryErrorHandler = (err, req, res, next) => {
  if (err.name === 'RangeError' && err.message.includes('Maximum call stack')) {
    logError(err, req);
    res.status(500).json({
      success: false,
      message: 'Request too complex, please simplify'
    });
  } else {
    next(err);
  }
};

module.exports = {
  errorHandler,
  asyncHandler,
  notFound,
  formatValidationErrors,
  AppError,
  logError,
  rateLimitHandler,
  corsErrorHandler,
  securityErrorHandler,
  databaseErrorHandler,
  apiErrorHandler,
  fileUploadErrorHandler,
  memoryErrorHandler
};







