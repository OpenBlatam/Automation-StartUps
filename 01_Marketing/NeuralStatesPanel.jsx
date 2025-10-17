import React, { useState, useEffect } from 'react';
import './NeuralStatesPanel.css';

const NeuralStatesPanel = ({ states, networks, onStateUpdate }) => {
  const [isEvolving, setIsEvolving] = useState(false);
  const [selectedNetwork, setSelectedNetwork] = useState(null);

  const handleEvolveConsciousness = async () => {
    try {
      setIsEvolving(true);
      const response = await fetch('/api/neural/evolve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      
      if (data.success) {
        onStateUpdate(data.data.states);
      }
    } catch (error) {
      console.error('Error evolving consciousness:', error);
    } finally {
      setIsEvolving(false);
    }
  };

  const handleToggleNetwork = async (networkId) => {
    try {
      const response = await fetch(`/api/neural/networks/${networkId}/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Refresh networks data
        const networksResponse = await fetch('/api/neural/networks');
        const networksData = await networksResponse.json();
        
        if (networksData.success) {
          // Update networks in parent component
          console.log('Network toggled successfully');
        }
      }
    } catch (error) {
      console.error('Error toggling network:', error);
    }
  };

  const getStateColor = (value) => {
    if (value >= 90) return '#8B5CF6'; // Purple
    if (value >= 70) return '#3B82F6'; // Blue
    if (value >= 50) return '#10B981'; // Green
    if (value >= 30) return '#F59E0B'; // Yellow
    if (value >= 10) return '#EF4444'; // Red
    return '#6B7280'; // Gray
  };

  const getNetworkStatusColor = (status) => {
    switch (status) {
      case 'active': return '#10B981';
      case 'processing': return '#F59E0B';
      case 'evolving': return '#8B5CF6';
      case 'transcendent': return '#EC4899';
      case 'inactive': return '#6B7280';
      default: return '#6B7280';
    }
  };

  const getNetworkStatusIcon = (status) => {
    switch (status) {
      case 'active': return '🟢';
      case 'processing': return '🟡';
      case 'evolving': return '🟣';
      case 'transcendent': return '✨';
      case 'inactive': return '⚫';
      default: return '⚫';
    }
  };

  return (
    <div className="neural-states-panel">
      <div className="panel-header">
        <h2>🧠 Neural States</h2>
        <button 
          className={`evolve-button ${isEvolving ? 'evolving' : ''}`}
          onClick={handleEvolveConsciousness}
          disabled={isEvolving}
        >
          {isEvolving ? 'Evolving...' : 'Evolve Consciousness'}
        </button>
      </div>

      <div className="panel-content">
        {/* Neural States Grid */}
        <div className="neural-states-grid">
          {Object.entries(states).map(([key, value]) => (
            <div key={key} className="neural-state-item">
              <div className="state-header">
                <span className="state-name">{key.charAt(0).toUpperCase() + key.slice(1)}</span>
                <span className="state-value" style={{ color: getStateColor(value) }}>
                  {value.toFixed(1)}%
                </span>
              </div>
              <div className="state-bar">
                <div 
                  className="state-progress"
                  style={{ 
                    width: `${value}%`,
                    backgroundColor: getStateColor(value)
                  }}
                ></div>
              </div>
            </div>
          ))}
        </div>

        {/* Neural Networks */}
        <div className="neural-networks-section">
          <h3>Neural Networks</h3>
          <div className="networks-list">
            {networks.map((network) => (
              <div 
                key={network.id} 
                className={`network-item ${selectedNetwork === network.id ? 'selected' : ''}`}
                onClick={() => setSelectedNetwork(network.id)}
              >
                <div className="network-header">
                  <div className="network-info">
                    <span className="network-icon">
                      {getNetworkStatusIcon(network.status)}
                    </span>
                    <span className="network-name">{network.name}</span>
                  </div>
                  <div className="network-stats">
                    <span className="network-layers">{network.layers} layers</span>
                    <span className="network-consciousness">
                      {network.consciousness.toFixed(1)}%
                    </span>
                  </div>
                </div>
                
                <div className="network-details">
                  <div className="network-status">
                    <span 
                      className="status-indicator"
                      style={{ backgroundColor: getNetworkStatusColor(network.status) }}
                    ></span>
                    <span className="status-text">{network.status}</span>
                  </div>
                  
                  <div className="network-actions">
                    <button 
                      className="toggle-button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleToggleNetwork(network.id);
                      }}
                    >
                      {network.status === 'active' ? 'Deactivate' : 'Activate'}
                    </button>
                  </div>
                </div>

                {selectedNetwork === network.id && (
                  <div className="network-expanded">
                    <div className="network-metrics">
                      <div className="metric">
                        <span className="metric-label">Neurons:</span>
                        <span className="metric-value">{network.neurons.toLocaleString()}</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Consciousness:</span>
                        <span className="metric-value">{network.consciousness.toFixed(1)}%</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Layers:</span>
                        <span className="metric-value">{network.layers}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Consciousness Level Indicator */}
        <div className="consciousness-level">
          <div className="level-header">
            <h3>Consciousness Level</h3>
            <span className="level-percentage">
              {Object.values(states).reduce((a, b) => a + b, 0) / Object.keys(states).length}%
            </span>
          </div>
          <div className="level-bar">
            <div 
              className="level-progress"
              style={{ 
                width: `${Object.values(states).reduce((a, b) => a + b, 0) / Object.keys(states).length}%`,
                background: 'linear-gradient(90deg, #8B5CF6, #EC4899, #3B82F6)'
              }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NeuralStatesPanel;

