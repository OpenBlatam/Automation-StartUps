import express from 'express';
import { aiMLEngine } from '../services/aiMLEngine';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Análisis de sentimiento avanzado con ML
router.post('/sentiment/advanced', authenticateToken, async (req, res) => {
  try {
    const { content, language = 'es', region = 'LATAM' } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }

    const feedback = {
      id: `temp_${Date.now()}`,
      content,
      sentiment: 'neutral',
      sentimentScore: 0,
      region,
      language,
      metadata: {}
    };

    const prediction = await aiMLEngine.analyzeSentimentAdvanced(feedback);
    
    res.json({
      success: true,
      data: prediction,
      message: 'Advanced sentiment analysis completed'
    });
  } catch (error) {
    console.error('Error in advanced sentiment analysis:', error);
    res.status(500).json({ error: 'Failed to perform advanced sentiment analysis' });
  }
});

// Análisis emocional con ML
router.post('/emotions/analyze', authenticateToken, async (req, res) => {
  try {
    const { content, language = 'es', region = 'LATAM' } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }

    const feedback = {
      id: `temp_${Date.now()}`,
      content,
      sentiment: 'neutral',
      sentimentScore: 0,
      region,
      language,
      metadata: {}
    };

    const prediction = await aiMLEngine.analyzeEmotions(feedback);
    
    res.json({
      success: true,
      data: prediction,
      message: 'Emotion analysis completed'
    });
  } catch (error) {
    console.error('Error in emotion analysis:', error);
    res.status(500).json({ error: 'Failed to perform emotion analysis' });
  }
});

// Predicción de churn
router.post('/predictions/churn', authenticateToken, async (req, res) => {
  try {
    const { content, language = 'es', region = 'LATAM', customerHistory = [] } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }

    const feedback = {
      id: `temp_${Date.now()}`,
      content,
      sentiment: 'neutral',
      sentimentScore: 0,
      region,
      language,
      metadata: {}
    };

    const prediction = await aiMLEngine.predictChurn(feedback, customerHistory);
    
    res.json({
      success: true,
      data: prediction,
      message: 'Churn prediction completed'
    });
  } catch (error) {
    console.error('Error in churn prediction:', error);
    res.status(500).json({ error: 'Failed to perform churn prediction' });
  }
});

// Predicción de upsell
router.post('/predictions/upsell', authenticateToken, async (req, res) => {
  try {
    const { content, language = 'es', region = 'LATAM', customerProfile = {} } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }

    const feedback = {
      id: `temp_${Date.now()}`,
      content,
      sentiment: 'neutral',
      sentimentScore: 0,
      region,
      language,
      metadata: {}
    };

    const prediction = await aiMLEngine.predictUpsell(feedback, customerProfile);
    
    res.json({
      success: true,
      data: prediction,
      message: 'Upsell prediction completed'
    });
  } catch (error) {
    console.error('Error in upsell prediction:', error);
    res.status(500).json({ error: 'Failed to perform upsell prediction' });
  }
});

// Predicción de advocacy
router.post('/predictions/advocacy', authenticateToken, async (req, res) => {
  try {
    const { content, language = 'es', region = 'LATAM', customerProfile = {} } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }

    const feedback = {
      id: `temp_${Date.now()}`,
      content,
      sentiment: 'neutral',
      sentimentScore: 0,
      region,
      language,
      metadata: {}
    };

    const prediction = await aiMLEngine.predictAdvocacy(feedback, customerProfile);
    
    res.json({
      success: true,
      data: prediction,
      message: 'Advocacy prediction completed'
    });
  } catch (error) {
    console.error('Error in advocacy prediction:', error);
    res.status(500).json({ error: 'Failed to perform advocacy prediction' });
  }
});

// Segmentación de clientes
router.post('/segmentation/customers', authenticateToken, async (req, res) => {
  try {
    const { feedbacks } = req.body;
    
    if (!feedbacks || !Array.isArray(feedbacks)) {
      return res.status(400).json({ error: 'Feedbacks array is required' });
    }

    const prediction = await aiMLEngine.segmentCustomers(feedbacks);
    
    res.json({
      success: true,
      data: prediction,
      message: 'Customer segmentation completed'
    });
  } catch (error) {
    console.error('Error in customer segmentation:', error);
    res.status(500).json({ error: 'Failed to perform customer segmentation' });
  }
});

// Análisis cultural con ML
router.post('/cultural/analyze', authenticateToken, async (req, res) => {
  try {
    const { content, language = 'es', region = 'LATAM' } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }

    const feedback = {
      id: `temp_${Date.now()}`,
      content,
      sentiment: 'neutral',
      sentimentScore: 0,
      region,
      language,
      metadata: {}
    };

    const prediction = await aiMLEngine.analyzeCulturalContext(feedback);
    
    res.json({
      success: true,
      data: prediction,
      message: 'Cultural analysis completed'
    });
  } catch (error) {
    console.error('Error in cultural analysis:', error);
    res.status(500).json({ error: 'Failed to perform cultural analysis' });
  }
});

// Entrenar modelo
router.post('/models/train', authenticateToken, async (req, res) => {
  try {
    const { modelName, trainingData } = req.body;
    
    if (!modelName || !trainingData) {
      return res.status(400).json({ error: 'Model name and training data are required' });
    }

    await aiMLEngine.trainModel(modelName, trainingData);
    
    res.json({
      success: true,
      message: `Model ${modelName} training initiated successfully`
    });
  } catch (error) {
    console.error('Error training model:', error);
    res.status(500).json({ error: 'Failed to train model' });
  }
});

// Evaluar modelo
router.post('/models/evaluate', authenticateToken, async (req, res) => {
  try {
    const { modelName, testData } = req.body;
    
    if (!modelName || !testData) {
      return res.status(400).json({ error: 'Model name and test data are required' });
    }

    const performance = await aiMLEngine.evaluateModel(modelName, testData);
    
    res.json({
      success: true,
      data: performance,
      message: `Model ${modelName} evaluation completed`
    });
  } catch (error) {
    console.error('Error evaluating model:', error);
    res.status(500).json({ error: 'Failed to evaluate model' });
  }
});

// Obtener estado de modelos
router.get('/models/status', authenticateToken, (req, res) => {
  try {
    const modelsStatus = aiMLEngine.getModelsStatus();
    
    res.json({
      success: true,
      data: modelsStatus,
      message: 'Models status retrieved successfully'
    });
  } catch (error) {
    console.error('Error fetching models status:', error);
    res.status(500).json({ error: 'Failed to fetch models status' });
  }
});

// Análisis completo con ML
router.post('/analyze/complete', authenticateToken, async (req, res) => {
  try {
    const { content, language = 'es', region = 'LATAM', customerHistory = [], customerProfile = {} } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }

    const feedback = {
      id: `temp_${Date.now()}`,
      content,
      sentiment: 'neutral',
      sentimentScore: 0,
      region,
      language,
      metadata: {}
    };

    // Ejecutar todos los análisis en paralelo
    const [
      sentimentAnalysis,
      emotionAnalysis,
      churnPrediction,
      upsellPrediction,
      advocacyPrediction,
      culturalAnalysis
    ] = await Promise.all([
      aiMLEngine.analyzeSentimentAdvanced(feedback),
      aiMLEngine.analyzeEmotions(feedback),
      aiMLEngine.predictChurn(feedback, customerHistory),
      aiMLEngine.predictUpsell(feedback, customerProfile),
      aiMLEngine.predictAdvocacy(feedback, customerProfile),
      aiMLEngine.analyzeCulturalContext(feedback)
    ]);

    const completeAnalysis = {
      feedback: {
        id: feedback.id,
        content: feedback.content,
        language: feedback.language,
        region: feedback.region
      },
      sentiment: sentimentAnalysis,
      emotions: emotionAnalysis,
      predictions: {
        churn: churnPrediction,
        upsell: upsellPrediction,
        advocacy: advocacyPrediction
      },
      cultural: culturalAnalysis,
      timestamp: new Date(),
      confidence: {
        overall: (
          sentimentAnalysis.confidence +
          emotionAnalysis.confidence +
          churnPrediction.confidence +
          upsellPrediction.confidence +
          advocacyPrediction.confidence +
          culturalAnalysis.confidence
        ) / 6
      }
    };
    
    res.json({
      success: true,
      data: completeAnalysis,
      message: 'Complete ML analysis completed'
    });
  } catch (error) {
    console.error('Error in complete ML analysis:', error);
    res.status(500).json({ error: 'Failed to perform complete ML analysis' });
  }
});

// Análisis de tendencias con ML
router.post('/trends/analyze', authenticateToken, async (req, res) => {
  try {
    const { feedbacks, analysisType = 'sentiment' } = req.body;
    
    if (!feedbacks || !Array.isArray(feedbacks)) {
      return res.status(400).json({ error: 'Feedbacks array is required' });
    }

    let trendAnalysis: any = {};

    switch (analysisType) {
      case 'sentiment':
        const sentimentResults = await Promise.all(
          feedbacks.map(feedback => aiMLEngine.analyzeSentimentAdvanced(feedback))
        );
        trendAnalysis = {
          type: 'sentiment',
          results: sentimentResults,
          summary: this.analyzeSentimentTrends(sentimentResults)
        };
        break;
        
      case 'emotions':
        const emotionResults = await Promise.all(
          feedbacks.map(feedback => aiMLEngine.analyzeEmotions(feedback))
        );
        trendAnalysis = {
          type: 'emotions',
          results: emotionResults,
          summary: this.analyzeEmotionTrends(emotionResults)
        };
        break;
        
      case 'cultural':
        const culturalResults = await Promise.all(
          feedbacks.map(feedback => aiMLEngine.analyzeCulturalContext(feedback))
        );
        trendAnalysis = {
          type: 'cultural',
          results: culturalResults,
          summary: this.analyzeCulturalTrends(culturalResults)
        };
        break;
        
      default:
        return res.status(400).json({ error: 'Invalid analysis type' });
    }
    
    res.json({
      success: true,
      data: trendAnalysis,
      message: 'Trend analysis completed'
    });
  } catch (error) {
    console.error('Error in trend analysis:', error);
    res.status(500).json({ error: 'Failed to perform trend analysis' });
  }
});

// Métodos auxiliares para análisis de tendencias
private analyzeSentimentTrends(results: any[]): any {
  const sentimentCounts = { positive: 0, negative: 0, neutral: 0 };
  const confidenceScores: number[] = [];
  
  results.forEach(result => {
    sentimentCounts[result.prediction.label]++;
    confidenceScores.push(result.confidence);
  });
  
  const total = results.length;
  const averageConfidence = confidenceScores.reduce((sum, score) => sum + score, 0) / confidenceScores.length;
  
  return {
    total,
    distribution: {
      positive: (sentimentCounts.positive / total) * 100,
      negative: (sentimentCounts.negative / total) * 100,
      neutral: (sentimentCounts.neutral / total) * 100
    },
    averageConfidence: parseFloat(averageConfidence.toFixed(2)),
    dominantSentiment: Object.entries(sentimentCounts).reduce((a, b) => sentimentCounts[a[0]] > sentimentCounts[b[0]] ? a : b)[0]
  };
}

private analyzeEmotionTrends(results: any[]): any {
  const emotionCounts: Record<string, number> = {};
  const intensityScores: number[] = [];
  
  results.forEach(result => {
    const emotion = result.prediction.primary;
    emotionCounts[emotion] = (emotionCounts[emotion] || 0) + 1;
    intensityScores.push(result.prediction.intensity);
  });
  
  const total = results.length;
  const averageIntensity = intensityScores.reduce((sum, score) => sum + score, 0) / intensityScores.length;
  
  return {
    total,
    emotionDistribution: Object.entries(emotionCounts).map(([emotion, count]) => ({
      emotion,
      percentage: (count / total) * 100,
      count
    })),
    averageIntensity: parseFloat(averageIntensity.toFixed(2)),
    dominantEmotion: Object.entries(emotionCounts).reduce((a, b) => emotionCounts[a[0]] > emotionCounts[b[0]] ? a : b)[0]
  };
}

private analyzeCulturalTrends(results: any[]): any {
  const culturalValues: Record<string, number> = {};
  const communicationStyles: Record<string, number> = {};
  
  results.forEach(result => {
    result.prediction.culturalValues.forEach((value: string) => {
      culturalValues[value] = (culturalValues[value] || 0) + 1;
    });
    
    const style = result.prediction.communicationStyle;
    communicationStyles[style] = (communicationStyles[style] || 0) + 1;
  });
  
  const total = results.length;
  
  return {
    total,
    culturalValues: Object.entries(culturalValues).map(([value, count]) => ({
      value,
      percentage: (count / total) * 100,
      count
    })),
    communicationStyles: Object.entries(communicationStyles).map(([style, count]) => ({
      style,
      percentage: (count / total) * 100,
      count
    })),
    dominantValue: Object.entries(culturalValues).reduce((a, b) => culturalValues[a[0]] > culturalValues[b[0]] ? a : b)[0],
    dominantStyle: Object.entries(communicationStyles).reduce((a, b) => communicationStyles[a[0]] > communicationStyles[b[0]] ? a : b)[0]
  };
}

export default router;

