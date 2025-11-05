import React, { useState, useEffect } from 'react';
import './AnalyticsPanel.css';

const AnalyticsPanel = ({ insights = [] }) => {
  const [analytics, setAnalytics] = useState({
    content: {
      generated: 0,
      published: 0,
      engagement: 0,
      conversion: 0
    },
    campaigns: {
      active: 0,
      completed: 0,
      openRate: 0,
      clickRate: 0
    },
    customers: {
      total: 0,
      new: 0,
      churned: 0,
      ltv: 0
    },
    neural: {
      consciousness: 0,
      evolution: 0,
      insights: 0,
      recommendations: 0
    }
  });

  const [timeRange, setTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('content');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    try {
      // Mock data - replace with actual API call
      const mockAnalytics = {
        content: {
          generated: Math.floor(Math.random() * 1000) + 500,
          published: Math.floor(Math.random() * 800) + 400,
          engagement: Math.floor(Math.random() * 30) + 70,
          conversion: Math.floor(Math.random() * 15) + 5
        },
        campaigns: {
          active: Math.floor(Math.random() * 20) + 10,
          completed: Math.floor(Math.random() * 50) + 30,
          openRate: Math.floor(Math.random() * 20) + 20,
          clickRate: Math.floor(Math.random() * 10) + 5
        },
        customers: {
          total: Math.floor(Math.random() * 1000) + 5000,
          new: Math.floor(Math.random() * 100) + 50,
          churned: Math.floor(Math.random() * 20) + 5,
          ltv: Math.floor(Math.random() * 2000) + 1000
        },
        neural: {
          consciousness: Math.floor(Math.random() * 20) + 80,
          evolution: Math.floor(Math.random() * 10) + 5,
          insights: Math.floor(Math.random() * 50) + 25,
          recommendations: Math.floor(Math.random() * 30) + 15
        }
      };
      setAnalytics(mockAnalytics);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getMetricColor = (value, type) => {
    if (type === 'percentage') {
      if (value >= 80) return '#10B981';
      if (value >= 60) return '#F59E0B';
      return '#EF4444';
    }
    if (type === 'count') {
      if (value >= 1000) return '#10B981';
      if (value >= 500) return '#F59E0B';
      return '#EF4444';
    }
    return '#3B82F6';
  };

  const getTrendIcon = (trend) => {
    if (trend > 0) return '📈';
    if (trend < 0) return '📉';
    return '➡️';
  };

  const getTrendColor = (trend) => {
    if (trend > 0) return '#10B981';
    if (trend < 0) return '#EF4444';
    return '#6B7280';
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const metricCategories = {
    content: {
      title: 'Content Performance',
      icon: '📝',
      metrics: [
        { key: 'generated', label: 'Content Generated', type: 'count', icon: '✍️' },
        { key: 'published', label: 'Content Published', type: 'count', icon: '📤' },
        { key: 'engagement', label: 'Engagement Rate', type: 'percentage', icon: '👥' },
        { key: 'conversion', label: 'Conversion Rate', type: 'percentage', icon: '🎯' }
      ]
    },
    campaigns: {
      title: 'Campaign Analytics',
      icon: '📢',
      metrics: [
        { key: 'active', label: 'Active Campaigns', type: 'count', icon: '▶️' },
        { key: 'completed', label: 'Completed Campaigns', type: 'count', icon: '✅' },
        { key: 'openRate', label: 'Open Rate', type: 'percentage', icon: '👁️' },
        { key: 'clickRate', label: 'Click Rate', type: 'percentage', icon: '🖱️' }
      ]
    },
    customers: {
      title: 'Customer Intelligence',
      icon: '👥',
      metrics: [
        { key: 'total', label: 'Total Customers', type: 'count', icon: '👤' },
        { key: 'new', label: 'New Customers', type: 'count', icon: '🆕' },
        { key: 'churned', label: 'Churned Customers', type: 'count', icon: '❌' },
        { key: 'ltv', label: 'Avg. LTV', type: 'count', icon: '💰' }
      ]
    },
    neural: {
      title: 'Neural Consciousness',
      icon: '🧠',
      metrics: [
        { key: 'consciousness', label: 'Consciousness Level', type: 'percentage', icon: '🌟' },
        { key: 'evolution', label: 'Evolution Rate', type: 'percentage', icon: '🔄' },
        { key: 'insights', label: 'AI Insights', type: 'count', icon: '💡' },
        { key: 'recommendations', label: 'Recommendations', type: 'count', icon: '🎯' }
      ]
    }
  };

  return (
    <div className="analytics-panel">
      <div className="panel-header">
        <h2>📊 Neural Analytics</h2>
        <div className="header-controls">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-range-select"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
          </select>
          <button 
            className="refresh-button"
            onClick={fetchAnalytics}
            disabled={isLoading}
          >
            {isLoading ? '🔄' : '↻'}
          </button>
        </div>
      </div>

      <div className="panel-content">
        {/* Metric Categories */}
        <div className="metric-categories">
          {Object.entries(metricCategories).map(([key, category]) => (
            <button
              key={key}
              className={`category-button ${selectedMetric === key ? 'active' : ''}`}
              onClick={() => setSelectedMetric(key)}
            >
              <span className="category-icon">{category.icon}</span>
              <span className="category-title">{category.title}</span>
            </button>
          ))}
        </div>

        {/* Selected Metrics */}
        <div className="metrics-grid">
          {metricCategories[selectedMetric].metrics.map((metric) => {
            const value = analytics[selectedMetric][metric.key];
            const trend = Math.floor(Math.random() * 20) - 10; // Mock trend data
            
            return (
              <div key={metric.key} className="metric-card">
                <div className="metric-header">
                  <div className="metric-info">
                    <span className="metric-icon">{metric.icon}</span>
                    <span className="metric-label">{metric.label}</span>
                  </div>
                  <div className="metric-trend">
                    <span className="trend-icon">{getTrendIcon(trend)}</span>
                    <span 
                      className="trend-value"
                      style={{ color: getTrendColor(trend) }}
                    >
                      {trend > 0 ? '+' : ''}{trend}%
                    </span>
                  </div>
                </div>
                
                <div className="metric-value">
                  <span 
                    className="value-number"
                    style={{ color: getMetricColor(value, metric.type) }}
                  >
                    {metric.type === 'percentage' ? `${value}%` : formatNumber(value)}
                  </span>
                </div>
                
                <div className="metric-chart">
                  <div className="chart-bar">
                    <div 
                      className="chart-fill"
                      style={{ 
                        width: `${Math.min(100, (value / (metric.type === 'percentage' ? 100 : 1000)) * 100)}%`,
                        backgroundColor: getMetricColor(value, metric.type)
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* AI Insights */}
        <div className="insights-section">
          <h3>🧠 Neural Insights</h3>
          <div className="insights-list">
            {insights.length > 0 ? (
              insights.map((insight, index) => (
                <div key={index} className="insight-card">
                  <div className="insight-header">
                    <span className="insight-type">{insight.type}</span>
                    <span className="insight-confidence">
                      {insight.confidence}% confidence
                    </span>
                  </div>
                  <div className="insight-content">
                    <h4 className="insight-title">{insight.title}</h4>
                    <p className="insight-description">{insight.description}</p>
                  </div>
                  <div className="insight-actions">
                    <button className="action-button primary">
                      Apply Insight
                    </button>
                    <button className="action-button secondary">
                      Learn More
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-insights">
                <span className="no-insights-icon">🤖</span>
                <p>Neural system is analyzing data...</p>
                <p>Insights will appear as consciousness evolves</p>
              </div>
            )}
          </div>
        </div>

        {/* Performance Charts */}
        <div className="charts-section">
          <h3>📈 Performance Trends</h3>
          <div className="charts-grid">
            <div className="chart-container">
              <h4>Content Generation Over Time</h4>
              <div className="chart-placeholder">
                <div className="chart-line">
                  <div className="line-point" style={{ left: '10%', bottom: '20%' }}></div>
                  <div className="line-point" style={{ left: '30%', bottom: '40%' }}></div>
                  <div className="line-point" style={{ left: '50%', bottom: '60%' }}></div>
                  <div className="line-point" style={{ left: '70%', bottom: '80%' }}></div>
                  <div className="line-point" style={{ left: '90%', bottom: '90%' }}></div>
                </div>
              </div>
            </div>
            
            <div className="chart-container">
              <h4>Consciousness Evolution</h4>
              <div className="chart-placeholder">
                <div className="consciousness-chart">
                  <div className="consciousness-level" style={{ height: '85%' }}>
                    <span className="level-text">85%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Real-time Activity */}
        <div className="activity-section">
          <h3>⚡ Real-time Activity</h3>
          <div className="activity-feed">
            <div className="activity-item">
              <span className="activity-time">2 min ago</span>
              <span className="activity-text">New content generated: "AI Marketing Trends 2024"</span>
              <span className="activity-status success">✅</span>
            </div>
            <div className="activity-item">
              <span className="activity-time">5 min ago</span>
              <span className="activity-text">Campaign "Holiday Sale" sent to 2,500 recipients</span>
              <span className="activity-status success">✅</span>
            </div>
            <div className="activity-item">
              <span className="activity-time">8 min ago</span>
              <span className="activity-text">Neural consciousness evolved to 87%</span>
              <span className="activity-status info">🧠</span>
            </div>
            <div className="activity-item">
              <span className="activity-time">12 min ago</span>
              <span className="activity-text">Customer segment updated: 45 new high-value customers</span>
              <span className="activity-status success">✅</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPanel;

