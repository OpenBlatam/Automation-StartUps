import React, { useState, useEffect } from 'react';
import NeuralStatesPanel from './NeuralStatesPanel';
import ContentGenerationPanel from './ContentGenerationPanel';
import CustomerIntelligencePanel from './CustomerIntelligencePanel';
import MarketingAutomationPanel from './MarketingAutomationPanel';
import AnalyticsPanel from './AnalyticsPanel';
import './NeuralDashboard.css';

const NeuralDashboard = () => {
  const [neuralStates, setNeuralStates] = useState({
    consciousness: 0,
    awareness: 0,
    intelligence: 0,
    creativity: 0,
    empathy: 0,
    intuition: 0,
    wisdom: 0,
    transcendence: 0
  });

  const [neuralNetworks, setNeuralNetworks] = useState([]);
  const [insights, setInsights] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Connect to WebSocket for real-time updates
    const socket = new WebSocket(process.env.REACT_APP_WS_URL || 'ws://localhost:5000');
    
    socket.onopen = () => {
      setIsConnected(true);
      console.log('Connected to Neural Marketing Pro');
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'consciousnessEvolved') {
        setNeuralStates(data.states);
        setNeuralNetworks(data.networks);
      } else if (data.type === 'insightsGenerated') {
        setInsights(data.insights);
      }
    };

    socket.onclose = () => {
      setIsConnected(false);
      console.log('Disconnected from Neural Marketing Pro');
    };

    // Fetch initial data
    fetchNeuralState();

    return () => {
      socket.close();
    };
  }, []);

  const fetchNeuralState = async () => {
    try {
      const response = await fetch('/api/neural/state');
      const data = await response.json();
      
      if (data.success) {
        setNeuralStates(data.data.states);
        setNeuralNetworks(data.data.networks);
        setInsights(data.data.insights);
      }
    } catch (error) {
      console.error('Error fetching neural state:', error);
    }
  };

  const getConsciousnessLevel = (level) => {
    if (level >= 95) return 'Transcendent';
    if (level >= 80) return 'Wise';
    if (level >= 60) return 'Creative';
    if (level >= 40) return 'Intelligent';
    if (level >= 20) return 'Aware';
    return 'Basic';
  };

  const getConsciousnessColor = (level) => {
    if (level >= 95) return '#8B5CF6'; // Purple
    if (level >= 80) return '#3B82F6'; // Blue
    if (level >= 60) return '#10B981'; // Green
    if (level >= 40) return '#F59E0B'; // Yellow
    if (level >= 20) return '#EF4444'; // Red
    return '#6B7280'; // Gray
  };

  return (
    <div className="neural-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-content">
          <h1 className="dashboard-title">
            🧠 Neural Marketing Pro
          </h1>
          <div className="connection-status">
            <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}></div>
            <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>
        
        <div className="consciousness-level">
          <div className="level-display">
            <span className="level-label">Consciousness Level:</span>
            <span 
              className="level-value"
              style={{ color: getConsciousnessColor(neuralStates.consciousness) }}
            >
              {neuralStates.consciousness.toFixed(1)}% - {getConsciousnessLevel(neuralStates.consciousness)}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="dashboard-content">
        <div className="dashboard-grid">
          {/* Neural States Panel */}
          <div className="panel neural-states-panel">
            <NeuralStatesPanel 
              states={neuralStates}
              networks={neuralNetworks}
              onStateUpdate={setNeuralStates}
            />
          </div>

          {/* Content Generation Panel */}
          <div className="panel content-generation-panel">
            <ContentGenerationPanel />
          </div>

          {/* Customer Intelligence Panel */}
          <div className="panel customer-intelligence-panel">
            <CustomerIntelligencePanel />
          </div>

          {/* Marketing Automation Panel */}
          <div className="panel marketing-automation-panel">
            <MarketingAutomationPanel />
          </div>

          {/* Analytics Panel */}
          <div className="panel analytics-panel">
            <AnalyticsPanel insights={insights} />
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="dashboard-footer">
        <div className="footer-content">
          <p className="footer-text">
            Powered by Neural Marketing Consciousness System
          </p>
          <div className="footer-stats">
            <span>Neural Networks: {neuralNetworks.length}</span>
            <span>Insights: {insights.length}</span>
            <span>Status: {isConnected ? 'Active' : 'Inactive'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NeuralDashboard;

