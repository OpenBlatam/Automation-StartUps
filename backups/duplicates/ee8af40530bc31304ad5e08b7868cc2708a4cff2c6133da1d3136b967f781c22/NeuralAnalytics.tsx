import React, { useState, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart
} from 'recharts';
import { 
  TrendingUp, 
  Brain, 
  Target, 
  Zap, 
  Users, 
  DollarSign,
  Activity,
  BarChart3,
  PieChart as PieChartIcon,
  LineChart as LineChartIcon
} from 'lucide-react';

interface AnalyticsData {
  consciousnessLevel: number;
  contentPerformance: {
    totalGenerations: number;
    averageTokens: number;
    costSavings: number;
    qualityScore: number;
  };
  usageStats: {
    dailyGenerations: Array<{ date: string; count: number }>;
    contentTypes: Array<{ type: string; count: number; percentage: number }>;
    consciousnessProgression: Array<{ date: string; level: number }>;
  };
  insights: {
    topPerformingContent: string[];
    improvementAreas: string[];
    recommendations: string[];
    nextLevelGoals: string[];
  };
  comparisons: {
    industryAverage: number;
    peerGroup: number;
    topPerformers: number;
  };
}

const COLORS = ['#8B5CF6', '#06B6D4', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

export const NeuralAnalytics: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTimeframe, setSelectedTimeframe] = useState('30d');
  const [selectedChart, setSelectedChart] = useState('overview');

  useEffect(() => {
    loadAnalyticsData();
  }, [selectedTimeframe]);

  const loadAnalyticsData = async () => {
    try {
      setIsLoading(true);
      // Simulate API call - replace with actual service call
      const mockData: AnalyticsData = {
        consciousnessLevel: 75,
        contentPerformance: {
          totalGenerations: 156,
          averageTokens: 850,
          costSavings: 12500,
          qualityScore: 87,
        },
        usageStats: {
          dailyGenerations: [
            { date: '2024-01-01', count: 5 },
            { date: '2024-01-02', count: 8 },
            { date: '2024-01-03', count: 12 },
            { date: '2024-01-04', count: 15 },
            { date: '2024-01-05', count: 18 },
            { date: '2024-01-06', count: 22 },
            { date: '2024-01-07', count: 25 },
          ],
          contentTypes: [
            { type: 'Blog Post', count: 45, percentage: 28.8 },
            { type: 'Email', count: 32, percentage: 20.5 },
            { type: 'Social Media', count: 28, percentage: 17.9 },
            { type: 'Ad Copy', count: 25, percentage: 16.0 },
            { type: 'Product Description', count: 18, percentage: 11.5 },
            { type: 'Other', count: 8, percentage: 5.1 },
          ],
          consciousnessProgression: [
            { date: '2024-01-01', level: 45 },
            { date: '2024-01-02', level: 47 },
            { date: '2024-01-03', level: 52 },
            { date: '2024-01-04', level: 58 },
            { date: '2024-01-05', level: 62 },
            { date: '2024-01-06', level: 68 },
            { date: '2024-01-07', level: 75 },
          ],
        },
        insights: {
          topPerformingContent: [
            'AI-powered product descriptions increased conversions by 40%',
            'Neural email sequences improved open rates by 65%',
            'Consciousness-based blog posts generated 300% more engagement',
          ],
          improvementAreas: [
            'Increase automation level for routine tasks',
            'Expand into video content generation',
            'Implement advanced personalization techniques',
          ],
          recommendations: [
            'Focus on high-converting content types',
            'Increase content generation frequency',
            'Experiment with advanced AI features',
          ],
          nextLevelGoals: [
            'Reach 80% consciousness level',
            'Implement full marketing automation',
            'Create brand-specific AI models',
          ],
        },
        comparisons: {
          industryAverage: 45,
          peerGroup: 52,
          topPerformers: 85,
        },
      };
      
      setAnalyticsData(mockData);
    } catch (error) {
      console.error('Error loading analytics data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        <span className="ml-2 text-gray-600">Loading neural analytics...</span>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="text-center py-12">
        <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Analytics Data</h3>
        <p className="text-gray-600">Start generating content to see your neural analytics.</p>
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
              Neural Analytics Dashboard
            </h1>
            <p className="text-gray-600">
              Advanced insights into your AI marketing performance and consciousness progression
            </p>
          </div>
          
          <div className="flex space-x-2">
            <select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
            </select>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Consciousness Level</p>
              <p className="text-2xl font-bold text-purple-600">{analyticsData.consciousnessLevel}%</p>
            </div>
            <Brain className="w-8 h-8 text-purple-600" />
          </div>
          <div className="mt-2">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-purple-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${analyticsData.consciousnessLevel}%` }}
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Generations</p>
              <p className="text-2xl font-bold text-blue-600">{analyticsData.contentPerformance.totalGenerations}</p>
            </div>
            <Target className="w-8 h-8 text-blue-600" />
          </div>
          <p className="text-sm text-gray-500 mt-1">+12% from last month</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cost Savings</p>
              <p className="text-2xl font-bold text-green-600">${analyticsData.contentPerformance.costSavings.toLocaleString()}</p>
            </div>
            <DollarSign className="w-8 h-8 text-green-600" />
          </div>
          <p className="text-sm text-gray-500 mt-1">vs traditional methods</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Quality Score</p>
              <p className="text-2xl font-bold text-orange-600">{analyticsData.contentPerformance.qualityScore}%</p>
            </div>
            <Activity className="w-8 h-8 text-orange-600" />
          </div>
          <p className="text-sm text-gray-500 mt-1">AI-generated content quality</p>
        </div>
      </div>

      {/* Chart Selection */}
      <div className="mb-6">
        <div className="flex space-x-2">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'consciousness', label: 'Consciousness', icon: Brain },
            { id: 'content', label: 'Content Types', icon: PieChartIcon },
            { id: 'trends', label: 'Trends', icon: LineChartIcon },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setSelectedChart(id)}
              className={`flex items-center px-4 py-2 rounded-md transition-colors ${
                selectedChart === id
                  ? 'bg-purple-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              <Icon className="w-4 h-4 mr-2" />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Daily Generations Chart */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Content Generations</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={analyticsData.usageStats.dailyGenerations}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="count" stroke="#8B5CF6" fill="#8B5CF6" fillOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Content Types Distribution */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Content Types Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={analyticsData.usageStats.contentTypes}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ type, percentage }) => `${type} (${percentage}%)`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {analyticsData.usageStats.contentTypes.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Consciousness Progression */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Consciousness Level Progression</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={analyticsData.usageStats.consciousnessProgression}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Line 
              type="monotone" 
              dataKey="level" 
              stroke="#8B5CF6" 
              strokeWidth={3}
              dot={{ fill: '#8B5CF6', strokeWidth: 2, r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Insights and Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Top Performing Content */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
            Top Performing Content
          </h3>
          <div className="space-y-3">
            {analyticsData.insights.topPerformingContent.map((item, index) => (
              <div key={index} className="p-3 bg-green-50 rounded-lg">
                <p className="text-sm text-gray-700">{item}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Improvement Areas */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Target className="w-5 h-5 mr-2 text-blue-600" />
            Improvement Areas
          </h3>
          <div className="space-y-3">
            {analyticsData.insights.improvementAreas.map((item, index) => (
              <div key={index} className="p-3 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-700">{item}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Zap className="w-5 h-5 mr-2 text-purple-600" />
            AI Recommendations
          </h3>
          <div className="space-y-3">
            {analyticsData.insights.recommendations.map((item, index) => (
              <div key={index} className="p-3 bg-purple-50 rounded-lg">
                <p className="text-sm text-gray-700">{item}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Next Level Goals */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Brain className="w-5 h-5 mr-2 text-orange-600" />
            Next Level Goals
          </h3>
          <div className="space-y-3">
            {analyticsData.insights.nextLevelGoals.map((item, index) => (
              <div key={index} className="p-3 bg-orange-50 rounded-lg">
                <p className="text-sm text-gray-700">{item}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Industry Comparison */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mt-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Industry Comparison</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{analyticsData.comparisons.industryAverage}%</div>
            <div className="text-sm text-gray-600">Industry Average</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{analyticsData.comparisons.peerGroup}%</div>
            <div className="text-sm text-gray-600">Your Peer Group</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{analyticsData.comparisons.topPerformers}%</div>
            <div className="text-sm text-gray-600">Top Performers</div>
          </div>
        </div>
        <div className="mt-4">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>Your Level: {analyticsData.consciousnessLevel}%</span>
            <span>Top Performers: {analyticsData.comparisons.topPerformers}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-purple-600 to-green-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${(analyticsData.consciousnessLevel / analyticsData.comparisons.topPerformers) * 100}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

