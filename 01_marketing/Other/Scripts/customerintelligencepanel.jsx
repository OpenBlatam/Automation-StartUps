import React, { useState, useEffect } from 'react';
import './CustomerIntelligencePanel.css';

const CustomerIntelligencePanel = () => {
  const [customers, setCustomers] = useState([]);
  const [segments, setSegments] = useState([]);
  const [insights, setInsights] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchCustomerData();
    fetchSegments();
    fetchInsights();
  }, []);

  const fetchCustomerData = async () => {
    setIsLoading(true);
    try {
      // Mock data - replace with actual API call
      const mockCustomers = [
        {
          id: 1,
          name: 'John Smith',
          email: 'john@example.com',
          segment: 'High Value',
          ltv: 2500,
          lastActivity: '2024-01-15',
          engagement: 85,
          churnRisk: 'Low',
          preferences: ['AI Tools', 'Marketing Automation', 'Content Creation']
        },
        {
          id: 2,
          name: 'Sarah Johnson',
          email: 'sarah@example.com',
          segment: 'Growth Potential',
          ltv: 1200,
          lastActivity: '2024-01-14',
          engagement: 72,
          churnRisk: 'Medium',
          preferences: ['Social Media', 'Email Marketing', 'Analytics']
        },
        {
          id: 3,
          name: 'Mike Chen',
          email: 'mike@example.com',
          segment: 'At Risk',
          ltv: 800,
          lastActivity: '2024-01-10',
          engagement: 45,
          churnRisk: 'High',
          preferences: ['Content Creation', 'SEO', 'Lead Generation']
        }
      ];
      setCustomers(mockCustomers);
    } catch (error) {
      console.error('Error fetching customer data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSegments = async () => {
    try {
      const mockSegments = [
        { name: 'High Value', count: 150, color: '#10B981' },
        { name: 'Growth Potential', count: 300, color: '#3B82F6' },
        { name: 'At Risk', count: 75, color: '#EF4444' },
        { name: 'New Customers', count: 200, color: '#F59E0B' }
      ];
      setSegments(mockSegments);
    } catch (error) {
      console.error('Error fetching segments:', error);
    }
  };

  const fetchInsights = async () => {
    try {
      const mockInsights = [
        {
          id: 1,
          type: 'prediction',
          title: 'Churn Risk Alert',
          description: '15 customers show high churn risk this month',
          confidence: 92,
          impact: 'high',
          action: 'Send retention campaign'
        },
        {
          id: 2,
          type: 'opportunity',
          title: 'Upsell Opportunity',
          description: '45 customers ready for plan upgrade',
          confidence: 87,
          impact: 'medium',
          action: 'Launch upgrade campaign'
        },
        {
          id: 3,
          type: 'trend',
          title: 'Engagement Trend',
          description: 'Email engagement increased 23% this week',
          confidence: 95,
          impact: 'positive',
          action: 'Scale successful campaigns'
        }
      ];
      setInsights(mockInsights);
    } catch (error) {
      console.error('Error fetching insights:', error);
    }
  };

  const getChurnRiskColor = (risk) => {
    switch (risk) {
      case 'Low': return '#10B981';
      case 'Medium': return '#F59E0B';
      case 'High': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const getEngagementColor = (engagement) => {
    if (engagement >= 80) return '#10B981';
    if (engagement >= 60) return '#F59E0B';
    return '#EF4444';
  };

  const getInsightIcon = (type) => {
    switch (type) {
      case 'prediction': return '🔮';
      case 'opportunity': return '💡';
      case 'trend': return '📈';
      default: return 'ℹ️';
    }
  };

  const getInsightColor = (type) => {
    switch (type) {
      case 'prediction': return '#EF4444';
      case 'opportunity': return '#3B82F6';
      case 'trend': return '#10B981';
      default: return '#6B7280';
    }
  };

  return (
    <div className="customer-intelligence-panel">
      <div className="panel-header">
        <h2>🧠 Customer Intelligence</h2>
        <div className="header-actions">
          <button className="refresh-button" onClick={fetchCustomerData}>
            Refresh
          </button>
        </div>
      </div>

      <div className="panel-content">
        {/* Customer Segments */}
        <div className="segments-section">
          <h3>Customer Segments</h3>
          <div className="segments-grid">
            {segments.map((segment, index) => (
              <div key={index} className="segment-card">
                <div className="segment-header">
                  <span className="segment-name">{segment.name}</span>
                  <span className="segment-count">{segment.count}</span>
                </div>
                <div className="segment-bar">
                  <div 
                    className="segment-progress"
                    style={{ 
                      width: `${(segment.count / 1000) * 100}%`,
                      backgroundColor: segment.color
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AI Insights */}
        <div className="insights-section">
          <h3>AI Insights</h3>
          <div className="insights-list">
            {insights.map((insight) => (
              <div key={insight.id} className="insight-item">
                <div className="insight-header">
                  <span className="insight-icon">
                    {getInsightIcon(insight.type)}
                  </span>
                  <span className="insight-title">{insight.title}</span>
                  <span 
                    className="insight-confidence"
                    style={{ color: getInsightColor(insight.type) }}
                  >
                    {insight.confidence}%
                  </span>
                </div>
                <div className="insight-description">
                  {insight.description}
                </div>
                <div className="insight-action">
                  <button className="action-button">
                    {insight.action}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Customer List */}
        <div className="customers-section">
          <h3>Customer Overview</h3>
          <div className="customers-list">
            {isLoading ? (
              <div className="loading">Loading customers...</div>
            ) : (
              customers.map((customer) => (
                <div 
                  key={customer.id} 
                  className={`customer-item ${selectedCustomer?.id === customer.id ? 'selected' : ''}`}
                  onClick={() => setSelectedCustomer(customer)}
                >
                  <div className="customer-header">
                    <div className="customer-info">
                      <span className="customer-name">{customer.name}</span>
                      <span className="customer-email">{customer.email}</span>
                    </div>
                    <div className="customer-metrics">
                      <span className="customer-ltv">${customer.ltv}</span>
                      <span 
                        className="customer-engagement"
                        style={{ color: getEngagementColor(customer.engagement) }}
                      >
                        {customer.engagement}%
                      </span>
                    </div>
                  </div>
                  
                  <div className="customer-details">
                    <div className="customer-segment">
                      <span className="segment-label">Segment:</span>
                      <span className="segment-value">{customer.segment}</span>
                    </div>
                    <div className="customer-churn">
                      <span className="churn-label">Churn Risk:</span>
                      <span 
                        className="churn-value"
                        style={{ color: getChurnRiskColor(customer.churnRisk) }}
                      >
                        {customer.churnRisk}
                      </span>
                    </div>
                    <div className="customer-activity">
                      <span className="activity-label">Last Activity:</span>
                      <span className="activity-value">{customer.lastActivity}</span>
                    </div>
                  </div>

                  {selectedCustomer?.id === customer.id && (
                    <div className="customer-expanded">
                      <div className="customer-preferences">
                        <h4>Preferences</h4>
                        <div className="preferences-list">
                          {customer.preferences.map((pref, index) => (
                            <span key={index} className="preference-tag">
                              {pref}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="customer-actions">
                        <button className="action-button primary">
                          Send Campaign
                        </button>
                        <button className="action-button secondary">
                          View Details
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Customer Analytics */}
        <div className="analytics-section">
          <h3>Customer Analytics</h3>
          <div className="analytics-grid">
            <div className="analytics-card">
              <div className="analytics-header">
                <span className="analytics-title">Total Customers</span>
                <span className="analytics-value">725</span>
              </div>
              <div className="analytics-trend">
                <span className="trend-indicator positive">+12%</span>
                <span className="trend-text">vs last month</span>
              </div>
            </div>
            
            <div className="analytics-card">
              <div className="analytics-header">
                <span className="analytics-title">Avg. LTV</span>
                <span className="analytics-value">$1,850</span>
              </div>
              <div className="analytics-trend">
                <span className="trend-indicator positive">+8%</span>
                <span className="trend-text">vs last month</span>
              </div>
            </div>
            
            <div className="analytics-card">
              <div className="analytics-header">
                <span className="analytics-title">Engagement Rate</span>
                <span className="analytics-value">78%</span>
              </div>
              <div className="analytics-trend">
                <span className="trend-indicator positive">+15%</span>
                <span className="trend-text">vs last month</span>
              </div>
            </div>
            
            <div className="analytics-card">
              <div className="analytics-header">
                <span className="analytics-title">Churn Rate</span>
                <span className="analytics-value">3.2%</span>
              </div>
              <div className="analytics-trend">
                <span className="trend-indicator negative">-2%</span>
                <span className="trend-text">vs last month</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerIntelligencePanel;

