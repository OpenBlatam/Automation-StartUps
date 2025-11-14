import request from 'supertest';
import app from '../../app';
import { customerFeedbackService } from '../../services/customerFeedbackService';
import { advancedAnalyticsService } from '../../services/advancedAnalyticsService';
import { aiMLEngine } from '../../services/aiMLEngine';

describe('Feedback Integration Tests', () => {
  let authToken: string;

  beforeAll(async () => {
    // Generar token de autenticación para las pruebas
    authToken = 'test-token-123';
  });

  describe('POST /api/feedback/process', () => {
    it('should process feedback successfully', async () => {
      const feedbackData = {
        content: 'Excelente servicio, muy satisfecho con la atención',
        source: 'survey',
        platform: 'typeform',
        language: 'es',
        region: 'MX',
        metadata: {
          customerId: 'customer_123',
          rating: 5
        }
      };

      const response = await request(app)
        .post('/api/feedback/process')
        .set('Authorization', `Bearer ${authToken}`)
        .send(feedbackData)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('id');
      expect(response.body.data).toHaveProperty('sentiment');
      expect(response.body.data).toHaveProperty('emotionalTone');
      expect(response.body.data).toHaveProperty('culturalInsights');
      expect(response.body.data).toHaveProperty('keywords');
      expect(response.body.data).toHaveProperty('urgency');
    });

    it('should handle negative feedback correctly', async () => {
      const feedbackData = {
        content: 'Terrible experiencia, el servicio es muy malo y lento',
        source: 'review',
        platform: 'google_my_business',
        language: 'es',
        region: 'AR',
        metadata: {
          customerId: 'customer_456',
          rating: 1
        }
      };

      const response = await request(app)
        .post('/api/feedback/process')
        .set('Authorization', `Bearer ${authToken}`)
        .send(feedbackData)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.data.sentiment).toBe('negative');
      expect(response.body.data.urgency).toBe('high');
    });

    it('should validate required fields', async () => {
      const response = await request(app)
        .post('/api/feedback/process')
        .set('Authorization', `Bearer ${authToken}`)
        .send({})
        .expect(400);

      expect(response.body.error).toBeDefined();
    });

    it('should detect spam content', async () => {
      const spamData = {
        content: 'SPAM SPAM SPAM BUY NOW CLICK HERE',
        source: 'survey',
        platform: 'typeform',
        language: 'en',
        region: 'US'
      };

      const response = await request(app)
        .post('/api/feedback/process')
        .set('Authorization', `Bearer ${authToken}`)
        .send(spamData)
        .expect(400);

      expect(response.body.error).toContain('spam');
    });
  });

  describe('GET /api/feedback/analytics', () => {
    it('should return analytics data', async () => {
      const response = await request(app)
        .get('/api/feedback/analytics')
        .set('Authorization', `Bearer ${authToken}`)
        .query({ period: '30d' })
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('totalFeedback');
      expect(response.body.data).toHaveProperty('sentimentDistribution');
      expect(response.body.data).toHaveProperty('regionalBreakdown');
      expect(response.body.data).toHaveProperty('trends');
    });

    it('should filter analytics by region', async () => {
      const response = await request(app)
        .get('/api/feedback/analytics')
        .set('Authorization', `Bearer ${authToken}`)
        .query({ region: 'MX', period: '7d' })
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.regionalBreakdown).toHaveProperty('MX');
    });
  });

  describe('POST /api/advanced/feedback/advanced-analysis', () => {
    it('should perform advanced analysis', async () => {
      const analysisData = {
        content: 'Me encanta el producto, es muy innovador y fácil de usar',
        language: 'es',
        region: 'MX',
        metadata: {
          customerId: 'customer_789',
          plan: 'premium'
        }
      };

      const response = await request(app)
        .post('/api/advanced/feedback/advanced-analysis')
        .set('Authorization', `Bearer ${authToken}`)
        .send(analysisData)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('emotionalIntelligence');
      expect(response.body.data).toHaveProperty('behavioralPatterns');
      expect(response.body.data).toHaveProperty('culturalAnalysis');
      expect(response.body.data).toHaveProperty('predictiveMetrics');
      expect(response.body.data).toHaveProperty('actionableRecommendations');
    });
  });

  describe('POST /api/ai/sentiment/advanced', () => {
    it('should perform advanced sentiment analysis with ML', async () => {
      const sentimentData = {
        content: 'Increíble experiencia, definitivamente lo recomendaría',
        language: 'es',
        region: 'BR'
      };

      const response = await request(app)
        .post('/api/ai/sentiment/advanced')
        .set('Authorization', `Bearer ${authToken}`)
        .send(sentimentData)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('model');
      expect(response.body.data).toHaveProperty('prediction');
      expect(response.body.data).toHaveProperty('confidence');
      expect(response.body.data).toHaveProperty('features');
    });
  });

  describe('POST /api/ai/predictions/churn', () => {
    it('should predict churn risk', async () => {
      const churnData = {
        content: 'No estoy satisfecho con el servicio, considerando cancelar',
        language: 'es',
        region: 'CO',
        customerHistory: [
          { sentiment: 'negative', timestamp: new Date() },
          { sentiment: 'negative', timestamp: new Date() }
        ]
      };

      const response = await request(app)
        .post('/api/ai/predictions/churn')
        .set('Authorization', `Bearer ${authToken}`)
        .send(churnData)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('model');
      expect(response.body.data).toHaveProperty('prediction');
      expect(response.body.data.prediction).toHaveProperty('risk');
      expect(response.body.data).toHaveProperty('confidence');
    });
  });

  describe('POST /api/ai/analyze/complete', () => {
    it('should perform complete ML analysis', async () => {
      const completeData = {
        content: 'Fantástico producto, lo uso todos los días y lo recomiendo a mis amigos',
        language: 'es',
        region: 'MX',
        customerHistory: [
          { sentiment: 'positive', timestamp: new Date() }
        ],
        customerProfile: {
          plan: 'premium',
          usageLevel: 0.9,
          satisfactionScore: 0.95,
          loyaltyScore: 0.9
        }
      };

      const response = await request(app)
        .post('/api/ai/analyze/complete')
        .set('Authorization', `Bearer ${authToken}`)
        .send(completeData)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('sentiment');
      expect(response.body.data).toHaveProperty('emotions');
      expect(response.body.data).toHaveProperty('predictions');
      expect(response.body.data).toHaveProperty('cultural');
      expect(response.body.data).toHaveProperty('confidence');
    });
  });

  describe('GET /api/monitoring/dashboard', () => {
    it('should return monitoring dashboard data', async () => {
      const response = await request(app)
        .get('/api/monitoring/dashboard')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('systemHealth');
      expect(response.body.data).toHaveProperty('performance');
      expect(response.body.data).toHaveProperty('security');
      expect(response.body.data).toHaveProperty('resources');
      expect(response.body.data).toHaveProperty('alerts');
    });
  });

  describe('GET /api/monitoring/health', () => {
    it('should return system health status', async () => {
      const response = await request(app)
        .get('/api/monitoring/health')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('overall');
      expect(response.body.data).toHaveProperty('services');
      expect(response.body.data.services).toBeInstanceOf(Array);
    });
  });

  describe('Error Handling', () => {
    it('should handle invalid authentication', async () => {
      const response = await request(app)
        .post('/api/feedback/process')
        .set('Authorization', 'Bearer invalid-token')
        .send({
          content: 'Test feedback',
          source: 'survey',
          platform: 'typeform'
        })
        .expect(401);

      expect(response.body.error).toBeDefined();
    });

    it('should handle rate limiting', async () => {
      const feedbackData = {
        content: 'Test feedback',
        source: 'survey',
        platform: 'typeform',
        language: 'es',
        region: 'MX'
      };

      // Enviar múltiples requests para activar rate limiting
      const promises = Array(150).fill(null).map(() =>
        request(app)
          .post('/api/feedback/process')
          .set('Authorization', `Bearer ${authToken}`)
          .send(feedbackData)
      );

      const responses = await Promise.all(promises);
      const rateLimitedResponse = responses.find(r => r.status === 429);
      
      expect(rateLimitedResponse).toBeDefined();
      expect(rateLimitedResponse?.body.error).toContain('Too many requests');
    });
  });

  describe('Performance Tests', () => {
    it('should process feedback within acceptable time', async () => {
      const startTime = Date.now();
      
      const response = await request(app)
        .post('/api/feedback/process')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          content: 'Test performance feedback',
          source: 'survey',
          platform: 'typeform',
          language: 'es',
          region: 'MX'
        });

      const endTime = Date.now();
      const responseTime = endTime - startTime;

      expect(response.status).toBe(201);
      expect(responseTime).toBeLessThan(2000); // Menos de 2 segundos
    });

    it('should handle concurrent requests', async () => {
      const feedbackData = {
        content: 'Concurrent test feedback',
        source: 'survey',
        platform: 'typeform',
        language: 'es',
        region: 'MX'
      };

      const promises = Array(10).fill(null).map(() =>
        request(app)
          .post('/api/feedback/process')
          .set('Authorization', `Bearer ${authToken}`)
          .send(feedbackData)
      );

      const responses = await Promise.all(promises);
      
      // Todas las respuestas deberían ser exitosas
      responses.forEach(response => {
        expect(response.status).toBe(201);
        expect(response.body.success).toBe(true);
      });
    });
  });

  describe('Data Validation', () => {
    it('should validate language codes', async () => {
      const response = await request(app)
        .post('/api/feedback/process')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          content: 'Test feedback',
          source: 'survey',
          platform: 'typeform',
          language: 'invalid',
          region: 'MX'
        })
        .expect(400);

      expect(response.body.error).toContain('language');
    });

    it('should validate region codes', async () => {
      const response = await request(app)
        .post('/api/feedback/process')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          content: 'Test feedback',
          source: 'survey',
          platform: 'typeform',
          language: 'es',
          region: 'INVALID'
        })
        .expect(400);

      expect(response.body.error).toContain('region');
    });

    it('should validate content length', async () => {
      const response = await request(app)
        .post('/api/feedback/process')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          content: 'Short',
          source: 'survey',
          platform: 'typeform',
          language: 'es',
          region: 'MX'
        })
        .expect(400);

      expect(response.body.error).toContain('length');
    });
  });
});

