import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  TrendingUp, 
  Target, 
  Zap, 
  AlertTriangle, 
  Lightbulb,
  BarChart3,
  PieChart,
  LineChart,
  RefreshCw,
  Filter,
  Search,
  Calendar,
  ArrowUpRight,
  ArrowDownRight,
  CheckCircle,
  Clock,
  Star
} from 'lucide-react';
import { neuralInsightsService } from '../services/neuralInsightsService';

interface NeuralInsight {
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

interface MarketTrend {
  trend: string;
  description: string;
  impact: number;
  timeframe: string;
  opportunities: string[];
  threats: string[];
  recommendedActions: string[];
}

interface CompetitiveAnalysis {
  competitor: string;
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
  marketPosition: number;
  recommendedStrategy: string[];
}

const INSIGHT_TYPES = {
  PREDICTION: { label: 'Prediction', icon: TrendingUp, color: 'bg-blue-500' },
  OPTIMIZATION: { label: 'Optimization', icon: Zap, color: 'bg-green-500' },
  TREND: { label: 'Trend', icon: BarChart3, color: 'bg-purple-500' },
  OPPORTUNITY: { label: 'Opportunity', icon: Lightbulb, color: 'bg-yellow-500' },
  RISK: { label: 'Risk', icon: AlertTriangle, color: 'bg-red-500' },
};

const IMPACT_LEVELS = {
  LOW: { label: 'Low', color: 'text-gray-500' },
  MEDIUM: { label: 'Medium', color: 'text-yellow-600' },
  HIGH: { label: 'High', color: 'text-orange-600' },
  CRITICAL: { label: 'Critical', color: 'text-red-600' },
};

const TIMEFRAMES = {
  IMMEDIATE: { label: 'Immediate', color: 'bg-red-100 text-red-800' },
  SHORT_TERM: { label: 'Short Term', color: 'bg-orange-100 text-orange-800' },
  MEDIUM_TERM: { label: 'Medium Term', color: 'bg-yellow-100 text-yellow-800' },
  LONG_TERM: { label: 'Long Term', color: 'bg-green-100 text-green-800' },
};

export const NeuralInsights: React.FC = () => {
  const [insights, setInsights] = useState<NeuralInsight[]>([]);
  const [marketTrends, setMarketTrends] = useState<MarketTrend[]>([]);
  const [competitiveAnalysis, setCompetitiveAnalysis] = useState<CompetitiveAnalysis[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState('insights');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      
      // Load insights
      const insightsData = await neuralInsightsService.generateInsights();
      setInsights(insightsData.insights || []);
      
      // Load market trends
      const trendsData = await neuralInsightsService.analyzeMarketTrends('AI Marketing', '30d');
      setMarketTrends(trendsData.trends || []);
      
      // Load competitive analysis
      const analysisData = await neuralInsightsService.performCompetitiveAnalysis(
        ['Copy.ai', 'Jasper', 'Writesonic'], 
        'AI Marketing'
      );
      setCompetitiveAnalysis(analysisData.analysis || []);
      
    } catch (error) {
      console.error('Error loading neural insights:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredInsights = insights.filter(insight => {
    const matchesSearch = insight.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         insight.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = selectedFilter === 'all' || insight.type === selectedFilter;
    return matchesSearch && matchesFilter;
  });

  const getInsightIcon = (type: string) => {
    const insightType = INSIGHT_TYPES[type as keyof typeof INSIGHT_TYPES];
    const Icon = insightType?.icon || Brain;
    return <Icon className="w-5 h-5" />;
  };

  const getInsightColor = (type: string) => {
    const insightType = INSIGHT_TYPES[type as keyof typeof INSIGHT_TYPES];
    return insightType?.color || 'bg-gray-500';
  };

  const getImpactColor = (impact: string) => {
    const impactLevel = IMPACT_LEVELS[impact as keyof typeof IMPACT_LEVELS];
    return impactLevel?.color || 'text-gray-500';
  };

  const getTimeframeColor = (timeframe: string) => {
    const timeframeType = TIMEFRAMES[timeframe as keyof typeof TIMEFRAMES];
    return timeframeType?.color || 'bg-gray-100 text-gray-800';
  };

  const markAsImplemented = async (insightId: string) => {
    try {
      await neuralInsightsService.markAsImplemented(insightId);
      setInsights(prev => prev.map(insight => 
        insight.id === insightId 
          ? { ...insight, implemented: true }
          : insight
      ));
    } catch (error) {
      console.error('Error marking insight as implemented:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-purple-600" />
        <span className="ml-2 text-gray-600">Loading neural insights...</span>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
              <Brain className="w-8 h-8 mr-3 text-purple-600" />
              Neural Marketing Insights
            </h1>
            <p className="text-gray-600">
              AI-powered insights, predictions, and recommendations for your marketing success
            </p>
          </div>
          
          <button
            onClick={loadData}
            className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 flex items-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh Insights
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
          {[
            { id: 'insights', label: 'Insights', icon: Brain },
            { id: 'trends', label: 'Market Trends', icon: TrendingUp },
            { id: 'competitive', label: 'Competitive Analysis', icon: Target },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setSelectedTab(id)}
              className={`flex items-center px-4 py-2 rounded-md transition-colors ${
                selectedTab === id
                  ? 'bg-white text-purple-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Icon className="w-4 h-4 mr-2" />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Filters and Search */}
      {selectedTab === 'insights' && (
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search insights..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>
          
          <select
            value={selectedFilter}
            onChange={(e) => setSelectedFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="all">All Types</option>
            {Object.entries(INSIGHT_TYPES).map(([key, { label }]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </div>
      )}

      {/* Content */}
      {selectedTab === 'insights' && (
        <div className="space-y-6">
          {/* Insights Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredInsights.map((insight) => (
              <div key={insight.id} className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center">
                    <div className={`p-2 rounded-lg ${getInsightColor(insight.type)} text-white mr-3`}>
                      {getInsightIcon(insight.type)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{insight.title}</h3>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className={`text-sm ${getImpactColor(insight.impact)}`}>
                          {insight.impact}
                        </span>
                        <span className="text-gray-400">•</span>
                        <span className="text-sm text-gray-500">
                          {insight.confidence}% confidence
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {insight.implemented ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : (
                    <Clock className="w-5 h-5 text-gray-400" />
                  )}
                </div>

                <p className="text-gray-600 text-sm mb-4">{insight.description}</p>

                <div className="flex items-center justify-between mb-4">
                  <span className={`px-2 py-1 rounded-full text-xs ${getTimeframeColor(insight.timeframe)}`}>
                    {TIMEFRAMES[insight.timeframe as keyof typeof TIMEFRAMES]?.label}
                  </span>
                  
                  <div className="flex items-center">
                    <Star className="w-4 h-4 text-yellow-400 mr-1" />
                    <span className="text-sm text-gray-500">{insight.category}</span>
                  </div>
                </div>

                {insight.recommendations.length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Recommendations:</h4>
                    <ul className="space-y-1">
                      {insight.recommendations.slice(0, 2).map((rec, index) => (
                        <li key={index} className="text-sm text-gray-600 flex items-start">
                          <ArrowUpRight className="w-3 h-3 text-green-500 mr-1 mt-0.5 flex-shrink-0" />
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {!insight.implemented && (
                  <button
                    onClick={() => markAsImplemented(insight.id)}
                    className="w-full bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 text-sm"
                  >
                    Mark as Implemented
                  </button>
                )}
              </div>
            ))}
          </div>

          {filteredInsights.length === 0 && (
            <div className="text-center py-12">
              <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Insights Found</h3>
              <p className="text-gray-600">Try adjusting your search or filter criteria.</p>
            </div>
          )}
        </div>
      )}

      {selectedTab === 'trends' && (
        <div className="space-y-6">
          {marketTrends.map((trend, index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{trend.trend}</h3>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">Impact: {trend.impact}/10</span>
                  <span className="text-sm text-gray-500">•</span>
                  <span className="text-sm text-gray-500">{trend.timeframe}</span>
                </div>
              </div>
              
              <p className="text-gray-600 mb-4">{trend.description}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-green-600 mb-2">Opportunities</h4>
                  <ul className="space-y-1">
                    {trend.opportunities.map((opp, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start">
                        <ArrowUpRight className="w-3 h-3 text-green-500 mr-1 mt-0.5 flex-shrink-0" />
                        {opp}
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-medium text-red-600 mb-2">Threats</h4>
                  <ul className="space-y-1">
                    {trend.threats.map((threat, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start">
                        <ArrowDownRight className="w-3 h-3 text-red-500 mr-1 mt-0.5 flex-shrink-0" />
                        {threat}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              
              {trend.recommendedActions.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-medium text-purple-600 mb-2">Recommended Actions</h4>
                  <ul className="space-y-1">
                    {trend.recommendedActions.map((action, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start">
                        <Zap className="w-3 h-3 text-purple-500 mr-1 mt-0.5 flex-shrink-0" />
                        {action}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {selectedTab === 'competitive' && (
        <div className="space-y-6">
          {competitiveAnalysis.map((analysis, index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{analysis.competitor}</h3>
                <div className="text-sm text-gray-500">
                  Market Position: {analysis.marketPosition}/10
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h4 className="font-medium text-green-600 mb-2">Strengths</h4>
                  <ul className="space-y-1">
                    {analysis.strengths.map((strength, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start">
                        <ArrowUpRight className="w-3 h-3 text-green-500 mr-1 mt-0.5 flex-shrink-0" />
                        {strength}
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-medium text-red-600 mb-2">Weaknesses</h4>
                  <ul className="space-y-1">
                    {analysis.weaknesses.map((weakness, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start">
                        <ArrowDownRight className="w-3 h-3 text-red-500 mr-1 mt-0.5 flex-shrink-0" />
                        {weakness}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h4 className="font-medium text-blue-600 mb-2">Opportunities</h4>
                  <ul className="space-y-1">
                    {analysis.opportunities.map((opp, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start">
                        <Lightbulb className="w-3 h-3 text-blue-500 mr-1 mt-0.5 flex-shrink-0" />
                        {opp}
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-medium text-orange-600 mb-2">Threats</h4>
                  <ul className="space-y-1">
                    {analysis.threats.map((threat, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start">
                        <AlertTriangle className="w-3 h-3 text-orange-500 mr-1 mt-0.5 flex-shrink-0" />
                        {threat}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              
              {analysis.recommendedStrategy.length > 0 && (
                <div>
                  <h4 className="font-medium text-purple-600 mb-2">Recommended Strategy</h4>
                  <ul className="space-y-1">
                    {analysis.recommendedStrategy.map((strategy, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start">
                        <Target className="w-3 h-3 text-purple-500 mr-1 mt-0.5 flex-shrink-0" />
                        {strategy}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

