import { aiMLEngine, MLModel, PredictionResult, TrainingData } from '../../../services/aiMLEngine';

describe('AIMLEngine', () => {
  describe('analyzeSentimentAdvanced', () => {
    it('should analyze Spanish sentiment correctly', async () => {
      const feedback = {
        id: 'test_1',
        content: 'Excelente servicio, muy satisfecho',
        sentiment: 'positive' as const,
        sentimentScore: 0.8,
        region: 'MX',
        language: 'es',
        metadata: {}
      };

      const result = await aiMLEngine.analyzeSentimentAdvanced(feedback);

      expect(result).toHaveProperty('model');
      expect(result).toHaveProperty('prediction');
      expect(result).toHaveProperty('confidence');
      expect(result).toHaveProperty('features');
      expect(result.model).toContain('sentiment_es');
      expect(result.prediction).toHaveProperty('label');
      expect(result.prediction).toHaveProperty('score');
    });

    it('should analyze Portuguese sentiment correctly', async () => {
      const feedback = {
        id: 'test_2',
        content: 'Serviço excelente, muito satisfeito',
        sentiment: 'positive' as const,
        sentimentScore: 0.8,
        region: 'BR',
        language: 'pt',
        metadata: {}
      };

      const result = await aiMLEngine.analyzeSentimentAdvanced(feedback);

      expect(result.model).toContain('sentiment_pt');
      expect(result.prediction).toHaveProperty('label');
      expect(result.prediction).toHaveProperty('score');
    });

    it('should analyze English sentiment correctly', async () => {
      const feedback = {
        id: 'test_3',
        content: 'Great service, very satisfied',
        sentiment: 'positive' as const,
        sentimentScore: 0.8,
        region: 'US',
        language: 'en',
        metadata: {}
      };

      const result = await aiMLEngine.analyzeSentimentAdvanced(feedback);

      expect(result.model).toContain('sentiment_en');
      expect(result.prediction).toHaveProperty('label');
      expect(result.prediction).toHaveProperty('score');
    });

    it('should throw error for invalid model', async () => {
      const feedback = {
        id: 'test_4',
        content: 'Test content',
        sentiment: 'neutral' as const,
        sentimentScore: 0,
        region: 'XX',
        language: 'xx',
        metadata: {}
      };

      await expect(aiMLEngine.analyzeSentimentAdvanced(feedback))
        .rejects.toThrow('Model sentiment_xx not available');
    });
  });

  describe('analyzeEmotions', () => {
    it('should analyze emotions correctly', async () => {
      const feedback = {
        id: 'test_5',
        content: 'Estoy muy feliz y emocionado con el resultado',
        sentiment: 'positive' as const,
        sentimentScore: 0.9,
        region: 'MX',
        language: 'es',
        metadata: {}
      };

      const result = await aiMLEngine.analyzeEmotions(feedback);

      expect(result).toHaveProperty('model');
      expect(result).toHaveProperty('prediction');
      expect(result).toHaveProperty('confidence');
      expect(result).toHaveProperty('features');
      expect(result.model).toBe('emotion_detection');
      expect(result.prediction).toHaveProperty('primary');
      expect(result.prediction).toHaveProperty('secondary');
      expect(result.prediction).toHaveProperty('intensity');
      expect(result.prediction).toHaveProperty('stability');
    });
  });

  describe('predictChurn', () => {
    it('should predict churn risk correctly', async () => {
      const feedback = {
        id: 'test_6',
        content: 'No estoy satisfecho, considerando cancelar',
        sentiment: 'negative' as const,
        sentimentScore: -0.7,
        region: 'MX',
        language: 'es',
        metadata: {}
      };

      const customerHistory = [
        { sentiment: 'negative', timestamp: new Date() },
        { sentiment: 'negative', timestamp: new Date() }
      ];

      const result = await aiMLEngine.predictChurn(feedback, customerHistory);

      expect(result).toHaveProperty('model');
      expect(result).toHaveProperty('prediction');
      expect(result).toHaveProperty('confidence');
      expect(result).toHaveProperty('features');
      expect(result.model).toBe('churn_prediction');
      expect(result.prediction).toHaveProperty('risk');
      expect(result.prediction).toHaveProperty('factors');
    });
  });

  describe('predictUpsell', () => {
    it('should predict upsell potential correctly', async () => {
      const feedback = {
        id: 'test_7',
        content: 'Me encanta el producto, quiero más funcionalidades',
        sentiment: 'positive' as const,
        sentimentScore: 0.8,
        region: 'MX',
        language: 'es',
        metadata: {}
      };

      const customerProfile = {
        plan: 'basic',
        usageLevel: 0.9,
        satisfactionScore: 0.8,
        loyaltyScore: 0.7
      };

      const result = await aiMLEngine.predictUpsell(feedback, customerProfile);

      expect(result).toHaveProperty('model');
      expect(result).toHaveProperty('prediction');
      expect(result).toHaveProperty('confidence');
      expect(result).toHaveProperty('features');
      expect(result.model).toBe('upsell_prediction');
      expect(result.prediction).toHaveProperty('potential');
      expect(result.prediction).toHaveProperty('opportunities');
    });
  });

  describe('predictAdvocacy', () => {
    it('should predict advocacy likelihood correctly', async () => {
      const feedback = {
        id: 'test_8',
        content: 'Recomiendo este servicio a todos mis amigos',
        sentiment: 'positive' as const,
        sentimentScore: 0.9,
        region: 'MX',
        language: 'es',
        metadata: {}
      };

      const customerProfile = {
        loyaltyScore: 0.9,
        referralHistory: 5,
        socialMediaActivity: 0.8
      };

      const result = await aiMLEngine.predictAdvocacy(feedback, customerProfile);

      expect(result).toHaveProperty('model');
      expect(result).toHaveProperty('prediction');
      expect(result).toHaveProperty('confidence');
      expect(result).toHaveProperty('features');
      expect(result.model).toBe('advocacy_prediction');
      expect(result.prediction).toHaveProperty('likelihood');
      expect(result.prediction).toHaveProperty('indicators');
    });
  });

  describe('segmentCustomers', () => {
    it('should segment customers correctly', async () => {
      const feedbacks = [
        {
          id: 'test_9',
          content: 'Excelente servicio, muy satisfecho',
          sentiment: 'positive' as const,
          sentimentScore: 0.8,
          region: 'MX',
          language: 'es',
          metadata: {}
        },
        {
          id: 'test_10',
          content: 'Servicio regular, nada especial',
          sentiment: 'neutral' as const,
          sentimentScore: 0,
          region: 'MX',
          language: 'es',
          metadata: {}
        }
      ];

      const result = await aiMLEngine.segmentCustomers(feedbacks);

      expect(result).toHaveProperty('model');
      expect(result).toHaveProperty('prediction');
      expect(result).toHaveProperty('confidence');
      expect(result).toHaveProperty('features');
      expect(result.model).toBe('customer_segmentation');
      expect(result.prediction).toHaveProperty('segment');
      expect(result.prediction).toHaveProperty('characteristics');
    });
  });

  describe('analyzeCulturalContext', () => {
    it('should analyze cultural context correctly', async () => {
      const feedback = {
        id: 'test_11',
        content: 'Valoro mucho la relación personal y el respeto',
        sentiment: 'positive' as const,
        sentimentScore: 0.7,
        region: 'MX',
        language: 'es',
        metadata: {}
      };

      const result = await aiMLEngine.analyzeCulturalContext(feedback);

      expect(result).toHaveProperty('model');
      expect(result).toHaveProperty('prediction');
      expect(result).toHaveProperty('confidence');
      expect(result).toHaveProperty('features');
      expect(result.model).toBe('cultural_analysis');
      expect(result.prediction).toHaveProperty('culturalValues');
      expect(result.prediction).toHaveProperty('communicationStyle');
      expect(result.prediction).toHaveProperty('businessEtiquette');
      expect(result.prediction).toHaveProperty('relationshipImportance');
    });
  });

  describe('trainModel', () => {
    it('should train model successfully', async () => {
      const trainingData: TrainingData[] = [
        {
          id: 'train_1',
          features: { wordCount: 10, positiveWords: 3, negativeWords: 0 },
          label: 'positive',
          metadata: {}
        },
        {
          id: 'train_2',
          features: { wordCount: 8, positiveWords: 0, negativeWords: 2 },
          label: 'negative',
          metadata: {}
        }
      ];

      await expect(aiMLEngine.trainModel('sentiment_es', trainingData))
        .resolves.not.toThrow();
    });

    it('should throw error for invalid model name', async () => {
      const trainingData: TrainingData[] = [];

      await expect(aiMLEngine.trainModel('invalid_model', trainingData))
        .rejects.toThrow('Model invalid_model not found');
    });
  });

  describe('evaluateModel', () => {
    it('should evaluate model successfully', async () => {
      const testData: TrainingData[] = [
        {
          id: 'test_1',
          features: { wordCount: 10, positiveWords: 3, negativeWords: 0 },
          label: 'positive',
          metadata: {}
        }
      ];

      const result = await aiMLEngine.evaluateModel('sentiment_es', testData);

      expect(result).toHaveProperty('model');
      expect(result).toHaveProperty('accuracy');
      expect(result).toHaveProperty('precision');
      expect(result).toHaveProperty('recall');
      expect(result).toHaveProperty('f1Score');
      expect(result).toHaveProperty('confusionMatrix');
      expect(result).toHaveProperty('lastEvaluated');
    });

    it('should throw error for invalid model name', async () => {
      const testData: TrainingData[] = [];

      await expect(aiMLEngine.evaluateModel('invalid_model', testData))
        .rejects.toThrow('Model invalid_model not found');
    });
  });

  describe('getModelsStatus', () => {
    it('should return models status', () => {
      const models = aiMLEngine.getModelsStatus();

      expect(models).toBeInstanceOf(Array);
      expect(models.length).toBeGreaterThan(0);
      
      models.forEach(model => {
        expect(model).toHaveProperty('name');
        expect(model).toHaveProperty('version');
        expect(model).toHaveProperty('accuracy');
        expect(model).toHaveProperty('lastTrained');
        expect(model).toHaveProperty('status');
      });
    });
  });

  describe('Private methods', () => {
    it('should extract sentiment features correctly', () => {
      const engine = aiMLEngine as any;
      const feedback = {
        id: 'test',
        content: 'Excelente producto, muy fácil de usar',
        sentiment: 'positive' as const,
        sentimentScore: 0.8,
        region: 'MX',
        language: 'es',
        metadata: {}
      };

      const features = engine.extractSentimentFeatures(feedback);

      expect(features).toHaveProperty('wordCount');
      expect(features).toHaveProperty('charCount');
      expect(features).toHaveProperty('exclamationCount');
      expect(features).toHaveProperty('questionCount');
      expect(features).toHaveProperty('positiveWords');
      expect(features).toHaveProperty('negativeWords');
      expect(features).toHaveProperty('neutralWords');
      expect(features).toHaveProperty('language');
      expect(features).toHaveProperty('region');
      expect(features).toHaveProperty('source');
      expect(features).toHaveProperty('platform');
    });

    it('should extract emotion features correctly', () => {
      const engine = aiMLEngine as any;
      const feedback = {
        id: 'test',
        content: 'Estoy muy emocionado y feliz',
        sentiment: 'positive' as const,
        sentimentScore: 0.8,
        region: 'MX',
        language: 'es',
        metadata: {}
      };

      const features = engine.extractEmotionFeatures(feedback);

      expect(features).toHaveProperty('emotionalIntensity');
      expect(features).toHaveProperty('emotionalStability');
      expect(features).toHaveProperty('empathyIndicators');
      expect(features).toHaveProperty('urgencyIndicators');
    });

    it('should calculate confidence correctly', () => {
      const engine = aiMLEngine as any;
      const prediction = { label: 'positive', score: 0.8 };
      const modelAccuracy = 0.85;

      const confidence = engine.calculateConfidence(prediction, modelAccuracy);

      expect(confidence).toBeGreaterThan(0);
      expect(confidence).toBeLessThanOrEqual(1);
    });
  });
});






