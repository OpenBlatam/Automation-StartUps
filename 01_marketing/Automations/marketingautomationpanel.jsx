import React, { useState, useEffect } from 'react';
import './MarketingAutomationPanel.css';

const MarketingAutomationPanel = () => {
  const [workflows, setWorkflows] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    fetchWorkflows();
    fetchCampaigns();
    fetchTemplates();
  }, []);

  const fetchWorkflows = async () => {
    try {
      const mockWorkflows = [
        {
          id: 1,
          name: 'Welcome Series',
          status: 'active',
          triggers: ['New User Signup'],
          steps: 5,
          subscribers: 1250,
          conversionRate: 23.5,
          lastRun: '2024-01-15T10:30:00Z'
        },
        {
          id: 2,
          name: 'Abandoned Cart Recovery',
          status: 'active',
          triggers: ['Cart Abandoned'],
          steps: 3,
          subscribers: 890,
          conversionRate: 18.2,
          lastRun: '2024-01-15T09:15:00Z'
        },
        {
          id: 3,
          name: 'Re-engagement Campaign',
          status: 'paused',
          triggers: ['Inactive 30 Days'],
          steps: 4,
          subscribers: 450,
          conversionRate: 12.8,
          lastRun: '2024-01-10T14:20:00Z'
        }
      ];
      setWorkflows(mockWorkflows);
    } catch (error) {
      console.error('Error fetching workflows:', error);
    }
  };

  const fetchCampaigns = async () => {
    try {
      const mockCampaigns = [
        {
          id: 1,
          name: 'Q1 Product Launch',
          type: 'Email',
          status: 'scheduled',
          recipients: 5000,
          openRate: 0,
          clickRate: 0,
          scheduledDate: '2024-01-20T09:00:00Z'
        },
        {
          id: 2,
          name: 'Holiday Sale',
          type: 'Email',
          status: 'sent',
          recipients: 8500,
          openRate: 24.5,
          clickRate: 8.7,
          sentDate: '2024-01-10T08:00:00Z'
        },
        {
          id: 3,
          name: 'Social Media Boost',
          type: 'Social',
          status: 'running',
          recipients: 15000,
          openRate: 0,
          clickRate: 0,
          startDate: '2024-01-12T10:00:00Z'
        }
      ];
      setCampaigns(mockCampaigns);
    } catch (error) {
      console.error('Error fetching campaigns:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const mockTemplates = [
        {
          id: 1,
          name: 'Welcome Email',
          type: 'Email',
          category: 'Onboarding',
          uses: 1250,
          conversionRate: 28.5
        },
        {
          id: 2,
          name: 'Product Announcement',
          type: 'Email',
          category: 'Product',
          uses: 890,
          conversionRate: 22.1
        },
        {
          id: 3,
          name: 'Social Media Post',
          type: 'Social',
          category: 'Engagement',
          uses: 2100,
          conversionRate: 15.8
        }
      ];
      setTemplates(mockTemplates);
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#10B981';
      case 'paused': return '#F59E0B';
      case 'stopped': return '#EF4444';
      case 'scheduled': return '#3B82F6';
      case 'sent': return '#8B5CF6';
      case 'running': return '#10B981';
      default: return '#6B7280';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return '🟢';
      case 'paused': return '🟡';
      case 'stopped': return '🔴';
      case 'scheduled': return '⏰';
      case 'sent': return '📤';
      case 'running': return '▶️';
      default: return '⚫';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const createWorkflow = () => {
    setIsCreating(true);
    // Simulate workflow creation
    setTimeout(() => {
      const newWorkflow = {
        id: Date.now(),
        name: 'New Workflow',
        status: 'draft',
        triggers: [],
        steps: 0,
        subscribers: 0,
        conversionRate: 0,
        lastRun: null
      };
      setWorkflows(prev => [newWorkflow, ...prev]);
      setIsCreating(false);
    }, 1000);
  };

  const toggleWorkflow = (workflowId) => {
    setWorkflows(prev => prev.map(workflow => 
      workflow.id === workflowId 
        ? { 
            ...workflow, 
            status: workflow.status === 'active' ? 'paused' : 'active' 
          }
        : workflow
    ));
  };

  return (
    <div className="marketing-automation-panel">
      <div className="panel-header">
        <h2>🤖 Marketing Automation</h2>
        <div className="header-actions">
          <button 
            className="create-button"
            onClick={createWorkflow}
            disabled={isCreating}
          >
            {isCreating ? 'Creating...' : 'Create Workflow'}
          </button>
        </div>
      </div>

      <div className="panel-content">
        {/* Workflows Section */}
        <div className="workflows-section">
          <h3>Automation Workflows</h3>
          <div className="workflows-list">
            {workflows.map((workflow) => (
              <div 
                key={workflow.id} 
                className={`workflow-item ${selectedWorkflow?.id === workflow.id ? 'selected' : ''}`}
                onClick={() => setSelectedWorkflow(workflow)}
              >
                <div className="workflow-header">
                  <div className="workflow-info">
                    <span className="workflow-icon">
                      {getStatusIcon(workflow.status)}
                    </span>
                    <span className="workflow-name">{workflow.name}</span>
                    <span 
                      className="workflow-status"
                      style={{ color: getStatusColor(workflow.status) }}
                    >
                      {workflow.status}
                    </span>
                  </div>
                  <div className="workflow-actions">
                    <button 
                      className="toggle-button"
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleWorkflow(workflow.id);
                      }}
                    >
                      {workflow.status === 'active' ? 'Pause' : 'Start'}
                    </button>
                  </div>
                </div>
                
                <div className="workflow-metrics">
                  <div className="metric">
                    <span className="metric-label">Steps:</span>
                    <span className="metric-value">{workflow.steps}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Subscribers:</span>
                    <span className="metric-value">{workflow.subscribers.toLocaleString()}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Conversion:</span>
                    <span className="metric-value">{workflow.conversionRate}%</span>
                  </div>
                </div>

                {selectedWorkflow?.id === workflow.id && (
                  <div className="workflow-expanded">
                    <div className="workflow-triggers">
                      <h4>Triggers</h4>
                      <div className="triggers-list">
                        {workflow.triggers.map((trigger, index) => (
                          <span key={index} className="trigger-tag">
                            {trigger}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="workflow-details">
                      <div className="detail">
                        <span className="detail-label">Last Run:</span>
                        <span className="detail-value">
                          {workflow.lastRun ? formatDate(workflow.lastRun) : 'Never'}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Campaigns Section */}
        <div className="campaigns-section">
          <h3>Active Campaigns</h3>
          <div className="campaigns-list">
            {campaigns.map((campaign) => (
              <div key={campaign.id} className="campaign-item">
                <div className="campaign-header">
                  <div className="campaign-info">
                    <span className="campaign-name">{campaign.name}</span>
                    <span className="campaign-type">{campaign.type}</span>
                  </div>
                  <div className="campaign-status">
                    <span className="status-icon">
                      {getStatusIcon(campaign.status)}
                    </span>
                    <span 
                      className="status-text"
                      style={{ color: getStatusColor(campaign.status) }}
                    >
                      {campaign.status}
                    </span>
                  </div>
                </div>
                
                <div className="campaign-metrics">
                  <div className="metric">
                    <span className="metric-label">Recipients:</span>
                    <span className="metric-value">{campaign.recipients.toLocaleString()}</span>
                  </div>
                  {campaign.openRate > 0 && (
                    <div className="metric">
                      <span className="metric-label">Open Rate:</span>
                      <span className="metric-value">{campaign.openRate}%</span>
                    </div>
                  )}
                  {campaign.clickRate > 0 && (
                    <div className="metric">
                      <span className="metric-label">Click Rate:</span>
                      <span className="metric-value">{campaign.clickRate}%</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Templates Section */}
        <div className="templates-section">
          <h3>Content Templates</h3>
          <div className="templates-grid">
            {templates.map((template) => (
              <div key={template.id} className="template-card">
                <div className="template-header">
                  <span className="template-name">{template.name}</span>
                  <span className="template-category">{template.category}</span>
                </div>
                <div className="template-metrics">
                  <div className="metric">
                    <span className="metric-label">Uses:</span>
                    <span className="metric-value">{template.uses}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Conversion:</span>
                    <span className="metric-value">{template.conversionRate}%</span>
                  </div>
                </div>
                <div className="template-actions">
                  <button className="action-button">Use Template</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Automation Analytics */}
        <div className="automation-analytics">
          <h3>Automation Performance</h3>
          <div className="analytics-grid">
            <div className="analytics-card">
              <div className="analytics-header">
                <span className="analytics-title">Active Workflows</span>
                <span className="analytics-value">12</span>
              </div>
              <div className="analytics-trend">
                <span className="trend-indicator positive">+3</span>
                <span className="trend-text">this month</span>
              </div>
            </div>
            
            <div className="analytics-card">
              <div className="analytics-header">
                <span className="analytics-title">Avg. Conversion</span>
                <span className="analytics-value">18.5%</span>
              </div>
              <div className="analytics-trend">
                <span className="trend-indicator positive">+2.1%</span>
                <span className="trend-text">vs last month</span>
              </div>
            </div>
            
            <div className="analytics-card">
              <div className="analytics-header">
                <span className="analytics-title">Emails Sent</span>
                <span className="analytics-value">45.2K</span>
              </div>
              <div className="analytics-trend">
                <span className="trend-indicator positive">+12%</span>
                <span className="trend-text">vs last month</span>
              </div>
            </div>
            
            <div className="analytics-card">
              <div className="analytics-header">
                <span className="analytics-title">Revenue Generated</span>
                <span className="analytics-value">$125K</span>
              </div>
              <div className="analytics-trend">
                <span className="trend-indicator positive">+25%</span>
                <span className="trend-text">vs last month</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketingAutomationPanel;

