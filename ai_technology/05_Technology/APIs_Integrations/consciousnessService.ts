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

export interface ConsciousnessAssessment {
  level: number;
  category: string;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  nextSteps: string[];
}

export interface NeuralMarketingProfile {
  consciousnessLevel: number;
  marketingStyle: string;
  preferredChannels: string[];
  contentPreferences: string[];
  automationLevel: string;
  aiAdoption: string;
}

export interface ConsciousnessInsights {
  currentLevel: number;
  category: string;
  levelLabel: string;
  progress: {
    contentGeneration: number;
    campaignManagement: number;
    aiAdoption: number;
    overall: number;
  };
  recommendations: string[];
  nextSteps: string[];
  insights: string[];
  profile?: NeuralMarketingProfile;
}

export interface ConsciousnessContentRequest {
  contentType: string;
  prompt: string;
}

export interface ConsciousnessContentResponse {
  content: string;
  contentType: string;
  consciousnessLevel: number;
  category: string;
}

export const consciousnessService = {
  // Assess consciousness level
  async assessConsciousness(): Promise<{ assessment: ConsciousnessAssessment }> {
    const response = await api.post('/consciousness/assess');
    return response.data;
  },

  // Generate neural marketing profile
  async generateProfile(): Promise<{ profile: NeuralMarketingProfile }> {
    const response = await api.post('/consciousness/profile');
    return response.data;
  },

  // Generate consciousness-based content
  async generateConsciousnessContent(
    request: ConsciousnessContentRequest
  ): Promise<ConsciousnessContentResponse> {
    const response = await api.post('/consciousness/generate-content', request);
    return response.data;
  },

  // Get consciousness insights
  async getInsights(): Promise<{ insights: ConsciousnessInsights }> {
    const response = await api.get('/consciousness/insights');
    return response.data;
  },

  // Get consciousness level
  async getLevel(): Promise<{
    level: number;
    category: string;
    levelLabel: string;
    progress: any;
  }> {
    const response = await api.get('/consciousness/level');
    return response.data;
  },

  // Get recommendations
  async getRecommendations(): Promise<{
    recommendations: string[];
    nextSteps: string[];
    insights: string[];
  }> {
    const response = await api.get('/consciousness/recommendations');
    return response.data;
  },

  // Get progress
  async getProgress(): Promise<{
    progress: any;
    currentLevel: number;
    levelLabel: string;
  }> {
    const response = await api.get('/consciousness/progress');
    return response.data;
  },
};

