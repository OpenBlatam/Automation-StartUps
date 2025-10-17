const swaggerJSDoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

/**
 * Swagger Configuration
 * API documentation setup
 */

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Neural Marketing Pro API',
      version: '1.0.0',
      description: 'AI-Powered Marketing Intelligence Platform with Neural Consciousness',
      contact: {
        name: 'Neural Marketing Team',
        email: 'support@neuralmarketing.pro',
        url: 'https://neuralmarketing.pro'
      },
      license: {
        name: 'MIT',
        url: 'https://opensource.org/licenses/MIT'
      }
    },
    servers: [
      {
        url: process.env.API_URL || 'http://localhost:5000',
        description: 'Development server'
      },
      {
        url: 'https://api.neuralmarketing.pro',
        description: 'Production server'
      }
    ],
    components: {
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT'
        },
        apiKeyAuth: {
          type: 'apiKey',
          in: 'header',
          name: 'X-API-Key'
        }
      },
      schemas: {
        User: {
          type: 'object',
          properties: {
            id: {
              type: 'string',
              description: 'User ID'
            },
            email: {
              type: 'string',
              format: 'email',
              description: 'User email'
            },
            name: {
              type: 'string',
              description: 'User name'
            },
            role: {
              type: 'string',
              enum: ['user', 'admin', 'enterprise'],
              description: 'User role'
            },
            tier: {
              type: 'string',
              enum: ['free', 'pro', 'enterprise'],
              description: 'User subscription tier'
            }
          }
        },
        NeuralState: {
          type: 'object',
          properties: {
            consciousness: {
              type: 'number',
              minimum: 0,
              maximum: 100,
              description: 'Consciousness level percentage'
            },
            awareness: {
              type: 'number',
              minimum: 0,
              maximum: 100,
              description: 'Awareness level percentage'
            },
            intelligence: {
              type: 'number',
              minimum: 0,
              maximum: 100,
              description: 'Intelligence level percentage'
            },
            creativity: {
              type: 'number',
              minimum: 0,
              maximum: 100,
              description: 'Creativity level percentage'
            },
            empathy: {
              type: 'number',
              minimum: 0,
              maximum: 100,
              description: 'Empathy level percentage'
            },
            intuition: {
              type: 'number',
              minimum: 0,
              maximum: 100,
              description: 'Intuition level percentage'
            },
            wisdom: {
              type: 'number',
              minimum: 0,
              maximum: 100,
              description: 'Wisdom level percentage'
            },
            transcendence: {
              type: 'number',
              minimum: 0,
              maximum: 100,
              description: 'Transcendence level percentage'
            }
          }
        },
        ContentGeneration: {
          type: 'object',
          properties: {
            type: {
              type: 'string',
              enum: ['blog-post', 'article', 'social-media', 'email', 'ad-copy', 'product-description'],
              description: 'Type of content to generate'
            },
            params: {
              type: 'object',
              properties: {
                prompt: {
                  type: 'string',
                  description: 'Content generation prompt'
                },
                target_audience: {
                  type: 'string',
                  description: 'Target audience for the content'
                },
                tone: {
                  type: 'string',
                  enum: ['professional', 'casual', 'authoritative', 'friendly'],
                  description: 'Tone of the content'
                },
                style: {
                  type: 'string',
                  description: 'Style of the content'
                }
              }
            }
          },
          required: ['type', 'params']
        },
        Workflow: {
          type: 'object',
          properties: {
            id: {
              type: 'string',
              description: 'Workflow ID'
            },
            name: {
              type: 'string',
              description: 'Workflow name'
            },
            status: {
              type: 'string',
              enum: ['active', 'paused', 'draft', 'stopped'],
              description: 'Workflow status'
            },
            triggers: {
              type: 'array',
              items: {
                type: 'string'
              },
              description: 'Workflow triggers'
            },
            steps: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  id: {
                    type: 'number'
                  },
                  type: {
                    type: 'string'
                  },
                  template: {
                    type: 'string'
                  },
                  delay: {
                    type: 'number'
                  }
                }
              },
              description: 'Workflow steps'
            },
            subscribers: {
              type: 'number',
              description: 'Number of subscribers'
            },
            conversionRate: {
              type: 'number',
              description: 'Conversion rate percentage'
            }
          }
        },
        Campaign: {
          type: 'object',
          properties: {
            id: {
              type: 'string',
              description: 'Campaign ID'
            },
            name: {
              type: 'string',
              description: 'Campaign name'
            },
            type: {
              type: 'string',
              enum: ['email', 'social', 'paid', 'content'],
              description: 'Campaign type'
            },
            status: {
              type: 'string',
              enum: ['draft', 'scheduled', 'active', 'sent', 'paused', 'stopped'],
              description: 'Campaign status'
            },
            recipients: {
              type: 'number',
              description: 'Number of recipients'
            },
            openRate: {
              type: 'number',
              description: 'Email open rate percentage'
            },
            clickRate: {
              type: 'number',
              description: 'Click rate percentage'
            },
            scheduledDate: {
              type: 'string',
              format: 'date-time',
              description: 'Scheduled send date'
            }
          }
        },
        Prediction: {
          type: 'object',
          properties: {
            id: {
              type: 'string',
              description: 'Prediction ID'
            },
            type: {
              type: 'string',
              enum: ['churn', 'conversion', 'content', 'campaign'],
              description: 'Prediction type'
            },
            title: {
              type: 'string',
              description: 'Prediction title'
            },
            description: {
              type: 'string',
              description: 'Prediction description'
            },
            confidence: {
              type: 'number',
              minimum: 0,
              maximum: 100,
              description: 'Prediction confidence percentage'
            },
            impact: {
              type: 'string',
              enum: ['low', 'medium', 'high'],
              description: 'Prediction impact level'
            },
            data: {
              type: 'object',
              description: 'Prediction data'
            },
            recommendations: {
              type: 'array',
              items: {
                type: 'string'
              },
              description: 'Actionable recommendations'
            },
            timestamp: {
              type: 'string',
              format: 'date-time',
              description: 'Prediction timestamp'
            }
          }
        },
        Error: {
          type: 'object',
          properties: {
            success: {
              type: 'boolean',
              example: false
            },
            error: {
              type: 'string',
              description: 'Error message'
            },
            retryAfter: {
              type: 'number',
              description: 'Retry after seconds (for rate limiting)'
            }
          }
        }
      }
    },
    security: [
      {
        bearerAuth: []
      },
      {
        apiKeyAuth: []
      }
    ]
  },
  apis: [
    './src/routes/*.js',
    './src/index.js'
  ]
};

const specs = swaggerJSDoc(options);

/**
 * Swagger UI options
 */
const swaggerUiOptions = {
  customCss: `
    .swagger-ui .topbar { display: none; }
    .swagger-ui .info .title { color: #8B5CF6; }
    .swagger-ui .scheme-container { background: linear-gradient(135deg, #8B5CF6, #EC4899); }
  `,
  customSiteTitle: 'Neural Marketing Pro API',
  customfavIcon: '/favicon.ico'
};

/**
 * Setup Swagger documentation
 */
const setupSwagger = (app) => {
  // Swagger JSON endpoint
  app.get('/api-docs.json', (req, res) => {
    res.setHeader('Content-Type', 'application/json');
    res.send(specs);
  });

  // Swagger UI
  app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(specs, swaggerUiOptions));

  // Custom documentation page
  app.get('/docs', (req, res) => {
    res.redirect('/api-docs');
  });
};

module.exports = {
  setupSwagger,
  specs
};

