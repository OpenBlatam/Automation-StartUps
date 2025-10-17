import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refreshToken,
          });
          
          const { accessToken } = response.data;
          localStorage.setItem('accessToken', accessToken);
          
          // Retry original request
          const originalRequest = error.config;
          originalRequest.headers.Authorization = `Bearer ${accessToken}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          window.location.href = '/login';
        }
      } else {
        // No refresh token, redirect to login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export interface NeuralInsight {
  id: string;
  type: 'PREDICTION' | 'OPTIMIZATION' | 'TREND' | 'OPPORTUNITY' | 'RISK';
  title: string;
  description: string;
  confidence: number;
  impact: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  actionable: boolean;
  recommendations: string[];
  timeframe: 'IMMEDIATE' | 'SHORT_TERM' | 'MEDIUM_TERM' | 'LONG_TERM';
  category: string;
  createdAt: string;
  implemented?: boolean;
}

export interface MarketTrend {
  trend: string;
  description: string;
  impact: number;
  timeframe: string;
  opportunities: string[];
  threats: string[];
  recommendedActions: string[];
}

export interface CompetitiveAnalysis {
  competitor: string;
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
  marketPosition: number;
  recommendedStrategy: string[];
}

export interface ContentStrategy {
  goals: string[];
  contentCalendar: any[];
  channelStrategy: any[];
  contentTypes: string[];
  aiTools: string[];
  metrics: string[];
  optimizationStrategies: string[];
}

export interface PerformancePrediction {
  timeframe: string;
  contentGenerationVolume: number;
  engagementRates: number;
  conversionRates: number;
  costEfficiency: number;
  roiProjections: number;
  riskFactors: string[];
  optimizationOpportunities: string[];
}

export interface OptimizationRecommendations {
  immediate: string[];
  shortTerm: string[];
  longTerm: string[];
  aiTools: string[];
  processImprovements: string[];
  skillDevelopment: string[];
  resourceAllocation: string[];
}

export const neuralInsightsService = {
  // Generate neural insights
  async generateInsights(): Promise<{ insights: NeuralInsight[] }> {
    const response = await api.post('/neural-insights/generate');
    return response.data;
  },

  // Analyze market trends
  async analyzeMarketTrends(
    industry: string,
    timeframe: string = '30d'
  ): Promise<{ trends: MarketTrend[] }> {
    const response = await api.post('/neural-insights/market-trends', {
      industry,
      timeframe,
    });
    return response.data;
  },

  // Perform competitive analysis
  async performCompetitiveAnalysis(
    competitors: string[],
    industry: string
  ): Promise<{ analysis: CompetitiveAnalysis[] }> {
    const response = await api.post('/neural-insights/competitive-analysis', {
      competitors,
      industry,
    });
    return response.data;
  },

  // Generate content strategy
  async generateContentStrategy(goals: string[]): Promise<{ strategy: ContentStrategy }> {
    const response = await api.post('/neural-insights/content-strategy', { goals });
    return response.data;
  },

  // Predict performance
  async predictPerformance(timeframe: string = '30d'): Promise<{ predictions: PerformancePrediction }> {
    const response = await api.post('/neural-insights/predict-performance', { timeframe });
    return response.data;
  },

  // Generate optimization recommendations
  async generateOptimizationRecommendations(): Promise<{ recommendations: OptimizationRecommendations }> {
    const response = await api.post('/neural-insights/optimization-recommendations');
    return response.data;
  },

  // Get insights summary
  async getInsightsSummary(): Promise<{
    totalInsights: number;
    recentInsights: NeuralInsight[];
    topCategories: string[];
    averageConfidence: number;
    highImpactInsights: number;
  }> {
    const response = await api.get('/neural-insights/summary');
    return response.data.summary;
  },

  // Get insights by category
  async getInsightsByCategory(
    category: string,
    page: number = 1,
    limit: number = 20
  ): Promise<{
    insights: NeuralInsight[];
    pagination: {
      page: number;
      limit: number;
      total: number;
      pages: number;
    };
  }> {
    const response = await api.get(`/neural-insights/category/${category}`, {
      params: { page, limit },
    });
    return response.data;
  },

  // Get insight details
  async getInsightDetails(insightId: string): Promise<{ insight: NeuralInsight }> {
    const response = await api.get(`/neural-insights/${insightId}`);
    return response.data;
  },

  // Mark insight as implemented
  async markAsImplemented(insightId: string): Promise<void> {
    await api.put(`/neural-insights/${insightId}/implement`);
  },

  // Delete insight
  async deleteInsight(insightId: string): Promise<void> {
    await api.delete(`/neural-insights/${insightId}`);
  },
};

