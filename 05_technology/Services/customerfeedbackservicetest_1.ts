import { customerFeedbackService, CustomerFeedback } from '../../../services/customerFeedbackService';

describe('CustomerFeedbackService', () => {
  describe('processFeedback', () => {
    it('should process positive feedback correctly', async () => {
      const feedbackData = {
        content: 'Excelente servicio, muy satisfecho con la atención recibida',
        source: 'survey',
        platform: 'typeform',
        language: 'es',
        region: 'MX',
        metadata: {
          customerId: 'customer_123',
          rating: 5
        }
      };

      const result = await customerFeedbackService.processFeedback(feedbackData);

      expect(result).toHaveProperty('id');
      expect(result.content).toBe(feedbackData.content);
      expect(result.source).toBe(feedbackData.source);
      expect(result.platform).toBe(feedbackData.platform);
      expect(result.language).toBe(feedbackData.language);
      expect(result.region).toBe(feedbackData.region);
      expect(result.sentiment).toBe('positive');
      expect(result.emotionalTone).toBeDefined();
      expect(result.culturalInsights).toBeInstanceOf(Array);
      expect(result.keywords).toBeInstanceOf(Array);
      expect(result.urgency).toBeDefined();
      expect(result.processedAt).toBeInstanceOf(Date);
      expect(result.metadata).toEqual(feedbackData.metadata);
    });

    it('should process negative feedback correctly', async () => {
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

      const result = await customerFeedbackService.processFeedback(feedbackData);

      expect(result.sentiment).toBe('negative');
      expect(result.urgency).toBe('high');
      expect(result.emotionalTone).toBe('angry');
    });

    it('should process neutral feedback correctly', async () => {
      const feedbackData = {
        content: 'El servicio está bien, nada especial pero cumple su función',
        source: 'survey',
        platform: 'typeform',
        language: 'es',
        region: 'CO',
        metadata: {
          customerId: 'customer_789',
          rating: 3
        }
      };

      const result = await customerFeedbackService.processFeedback(feedbackData);

      expect(result.sentiment).toBe('neutral');
      expect(result.urgency).toBe('low');
      expect(result.emotionalTone).toBe('neutral');
    });

    it('should auto-detect language and region when not provided', async () => {
      const feedbackData = {
        content: 'Muy buen servicio, lo recomiendo',
        source: 'survey',
        platform: 'typeform'
      };

      const result = await customerFeedbackService.processFeedback(feedbackData);

      expect(result.language).toBeDefined();
      expect(result.region).toBeDefined();
    });

    it('should extract keywords correctly', async () => {
      const feedbackData = {
        content: 'El producto es excelente, muy fácil de usar y rápido',
        source: 'survey',
        platform: 'typeform',
        language: 'es',
        region: 'MX'
      };

      const result = await customerFeedbackService.processFeedback(feedbackData);

      expect(result.keywords).toBeInstanceOf(Array);
      expect(result.keywords.length).toBeGreaterThan(0);
      expect(result.keywords).toContain('producto');
      expect(result.keywords).toContain('excelente');
    });

    it('should assess urgency correctly', async () => {
      const criticalFeedback = {
        content: 'URGENTE: El sistema no funciona, necesito ayuda inmediata',
        source: 'support',
        platform: 'email',
        language: 'es',
        region: 'MX'
      };

      const result = await customerFeedbackService.processFeedback(criticalFeedback);

      expect(result.urgency).toBe('critical');
    });

    it('should handle different languages', async () => {
      const englishFeedback = {
        content: 'Great service, very satisfied with the support',
        source: 'survey',
        platform: 'typeform',
        language: 'en',
        region: 'US'
      };

      const result = await customerFeedbackService.processFeedback(englishFeedback);

      expect(result.language).toBe('en');
      expect(result.region).toBe('US');
      expect(result.sentiment).toBe('positive');
    });

    it('should handle Portuguese feedback', async () => {
      const portugueseFeedback = {
        content: 'Serviço excelente, muito satisfeito com o atendimento',
        source: 'survey',
        platform: 'typeform',
        language: 'pt',
        region: 'BR'
      };

      const result = await customerFeedbackService.processFeedback(portugueseFeedback);

      expect(result.language).toBe('pt');
      expect(result.region).toBe('BR');
      expect(result.sentiment).toBe('positive');
    });

    it('should handle metadata correctly', async () => {
      const feedbackData = {
        content: 'Test feedback',
        source: 'survey',
        platform: 'typeform',
        language: 'es',
        region: 'MX',
        metadata: {
          customerId: 'customer_123',
          sessionId: 'session_456',
          userAgent: 'Mozilla/5.0...',
          ipAddress: '192.168.1.1'
        }
      };

      const result = await customerFeedbackService.processFeedback(feedbackData);

      expect(result.metadata).toEqual(feedbackData.metadata);
    });

    it('should generate unique IDs', async () => {
      const feedbackData1 = {
        content: 'First feedback',
        source: 'survey',
        platform: 'typeform',
        language: 'es',
        region: 'MX'
      };

      const feedbackData2 = {
        content: 'Second feedback',
        source: 'survey',
        platform: 'typeform',
        language: 'es',
        region: 'MX'
      };

      const result1 = await customerFeedbackService.processFeedback(feedbackData1);
      const result2 = await customerFeedbackService.processFeedback(feedbackData2);

      expect(result1.id).not.toBe(result2.id);
    });

    it('should handle empty content gracefully', async () => {
      const feedbackData = {
        content: '',
        source: 'survey',
        platform: 'typeform',
        language: 'es',
        region: 'MX'
      };

      await expect(customerFeedbackService.processFeedback(feedbackData))
        .rejects.toThrow();
    });

    it('should handle very long content', async () => {
      const longContent = 'A'.repeat(10000);
      const feedbackData = {
        content: longContent,
        source: 'survey',
        platform: 'typeform',
        language: 'es',
        region: 'MX'
      };

      const result = await customerFeedbackService.processFeedback(feedbackData);

      expect(result.content).toBe(longContent);
      expect(result.keywords.length).toBeGreaterThan(0);
    });
  });

  describe('getFeedback', () => {
    it('should return empty array when no feedback exists', async () => {
      const result = await customerFeedbackService.getFeedback({});

      expect(result).toEqual([]);
    });

    it('should handle filters correctly', async () => {
      const filters = {
        sentiment: 'positive',
        region: 'MX',
        source: 'survey'
      };

      const result = await customerFeedbackService.getFeedback(filters);

      expect(result).toBeInstanceOf(Array);
    });
  });

  describe('Private methods', () => {
    it('should calculate emotional tone correctly', () => {
      const service = customerFeedbackService as any;
      
      expect(service.getEmotionalTone(0.8)).toBe('joyful');
      expect(service.getEmotionalTone(0.5)).toBe('optimistic');
      expect(service.getEmotionalTone(-0.5)).toBe('frustrated');
      expect(service.getEmotionalTone(-0.8)).toBe('angry');
      expect(service.getEmotionalTone(0)).toBe('neutral');
    });

    it('should extract keywords correctly', () => {
      const service = customerFeedbackService as any;
      const content = 'El producto es excelente y muy fácil de usar';
      const keywords = service.extractKeywords(content);

      expect(keywords).toBeInstanceOf(Array);
      expect(keywords).toContain('producto');
      expect(keywords).toContain('excelente');
      expect(keywords).toContain('fácil');
      expect(keywords).not.toContain('el');
      expect(keywords).not.toContain('es');
      expect(keywords).not.toContain('y');
    });

    it('should assess urgency correctly', () => {
      const service = customerFeedbackService as any;
      
      // Critical urgency
      expect(service.assessUrgency(-0.9, ['problema', 'urgente'])).toBe('critical');
      expect(service.assessUrgency(-0.8, ['fallo', 'error'])).toBe('critical');
      
      // High urgency
      expect(service.assessUrgency(-0.6, ['lento', 'no funciona'])).toBe('high');
      expect(service.assessUrgency(-0.5, ['mal'])).toBe('high');
      
      // Medium urgency
      expect(service.assessUrgency(-0.3, ['mejora', 'sugerencia'])).toBe('medium');
      expect(service.assessUrgency(-0.2, ['sugerencia'])).toBe('medium');
      
      // Low urgency
      expect(service.assessUrgency(0.5, ['bueno'])).toBe('low');
      expect(service.assessUrgency(0, [])).toBe('low');
    });
  });
});

