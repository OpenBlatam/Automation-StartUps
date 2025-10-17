import React, { useState, useEffect } from 'react';
import { Brain, TrendingUp, Target, Zap, Award, ChevronRight, RefreshCw } from 'lucide-react';
import { consciousnessService } from '../services/consciousnessService';
import { toast } from 'react-hot-toast';

interface ConsciousnessInsights {
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
  profile?: {
    marketingStyle: string;
    preferredChannels: string[];
    automationLevel: string;
    aiAdoption: string;
  };
}

const CONSCIOUSNESS_LEVELS = {
  BEGINNER: { min: 0, max: 20, label: 'Neural Novice', color: 'bg-gray-500' },
  INTERMEDIATE: { min: 21, max: 40, label: 'Conscious Marketer', color: 'bg-blue-500' },
  ADVANCED: { min: 41, max: 60, label: 'Neural Strategist', color: 'bg-purple-500' },
  EXPERT: { min: 61, max: 80, label: 'AI Marketing Master', color: 'bg-orange-500' },
  MASTER: { min: 81, max: 100, label: 'Neural Marketing Consciousness', color: 'bg-red-500' },
};

export const ConsciousnessDashboard: React.FC = () => {
  const [insights, setInsights] = useState<ConsciousnessInsights | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAssessing, setIsAssessing] = useState(false);

  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    try {
      setIsLoading(true);
      const data = await consciousnessService.getInsights();
      setInsights(data.insights);
    } catch (error) {
      console.error('Error loading insights:', error);
      toast.error('Failed to load consciousness insights');
    } finally {
      setIsLoading(false);
    }
  };

  const assessConsciousness = async () => {
    try {
      setIsAssessing(true);
      const data = await consciousnessService.assessConsciousness();
      setInsights(prev => prev ? { ...prev, ...data.assessment } : data.assessment);
      toast.success(`Consciousness level: ${data.assessment.level} (${data.assessment.category})`);
    } catch (error) {
      console.error('Error assessing consciousness:', error);
      toast.error('Failed to assess consciousness level');
    } finally {
      setIsAssessing(false);
    }
  };

  const getLevelColor = (level: number) => {
    for (const [category, range] of Object.entries(CONSCIOUSNESS_LEVELS)) {
      if (level >= range.min && level <= range.max) {
        return range.color;
      }
    }
    return 'bg-gray-500';
  };

  const getLevelLabel = (level: number) => {
    for (const [category, range] of Object.entries(CONSCIOUSNESS_LEVELS)) {
      if (level >= range.min && level <= range.max) {
        return range.label;
      }
    }
    return 'Neural Novice';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading consciousness insights...</span>
      </div>
    );
  }

  if (!insights) {
    return (
      <div className="text-center py-12">
        <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Consciousness Data</h3>
        <p className="text-gray-600 mb-4">Start your neural marketing journey by assessing your consciousness level.</p>
        <button
          onClick={assessConsciousness}
          disabled={isAssessing}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center mx-auto"
        >
          {isAssessing ? (
            <>
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              Assessing...
            </>
          ) : (
            <>
              <Brain className="w-4 h-4 mr-2" />
              Assess Consciousness
            </>
          )}
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Neural Marketing Consciousness</h1>
            <p className="text-gray-600">
              Your AI marketing consciousness level and personalized insights
            </p>
          </div>
          <button
            onClick={assessConsciousness}
            disabled={isAssessing}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center"
          >
            {isAssessing ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Reassessing...
              </>
            ) : (
              <>
                <Brain className="w-4 h-4 mr-2" />
                Reassess
              </>
            )}
          </button>
        </div>
      </div>

      {/* Consciousness Level Card */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Your Consciousness Level</h2>
            <p className="text-gray-600">Current neural marketing consciousness assessment</p>
          </div>
          <div className={`px-4 py-2 rounded-full text-white font-medium ${getLevelColor(insights.currentLevel)}`}>
            {insights.levelLabel}
          </div>
        </div>

        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Consciousness Level</span>
            <span className="text-sm font-medium text-gray-900">{insights.currentLevel}/100</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all duration-500 ${getLevelColor(insights.currentLevel)}`}
              style={{ width: `${insights.currentLevel}%` }}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{Math.round(insights.progress.contentGeneration)}%</div>
            <div className="text-sm text-gray-600">Content Generation</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{Math.round(insights.progress.campaignManagement)}%</div>
            <div className="text-sm text-gray-600">Campaign Management</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{Math.round(insights.progress.aiAdoption)}%</div>
            <div className="text-sm text-gray-600">AI Adoption</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">{Math.round(insights.progress.overall)}%</div>
            <div className="text-sm text-gray-600">Overall Progress</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recommendations */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center mb-4">
            <Target className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Recommendations</h3>
          </div>
          <div className="space-y-3">
            {insights.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start">
                <ChevronRight className="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">{recommendation}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Next Steps */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center mb-4">
            <TrendingUp className="w-5 h-5 text-green-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Next Steps</h3>
          </div>
          <div className="space-y-3">
            {insights.nextSteps.map((step, index) => (
              <div key={index} className="flex items-start">
                <div className="w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-medium mr-3 flex-shrink-0">
                  {index + 1}
                </div>
                <span className="text-gray-700">{step}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Insights */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center mb-4">
            <Zap className="w-5 h-5 text-purple-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">AI Insights</h3>
          </div>
          <div className="space-y-3">
            {insights.insights.map((insight, index) => (
              <div key={index} className="p-3 bg-purple-50 rounded-lg">
                <span className="text-gray-700">{insight}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Profile */}
        {insights.profile && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center mb-4">
              <Award className="w-5 h-5 text-orange-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Neural Profile</h3>
            </div>
            <div className="space-y-4">
              <div>
                <div className="text-sm font-medium text-gray-600">Marketing Style</div>
                <div className="text-gray-900">{insights.profile.marketingStyle}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-gray-600">Preferred Channels</div>
                <div className="flex flex-wrap gap-2 mt-1">
                  {insights.profile.preferredChannels.map((channel, index) => (
                    <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                      {channel}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <div className="text-sm font-medium text-gray-600">Automation Level</div>
                <div className="text-gray-900">{insights.profile.automationLevel}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-gray-600">AI Adoption</div>
                <div className="text-gray-900">{insights.profile.aiAdoption}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

