# Comments Component - Usage Examples

## 📚 Table of Contents
- [Basic Implementation](#basic-implementation)
- [Advanced Configuration](#advanced-configuration)
- [Custom Styling](#custom-styling)
- [API Integration](#api-integration)
- [Real-world Use Cases](#real-world-use-cases)
- [Performance Optimization](#performance-optimization)

## 🚀 Basic Implementation

### Simple Comments Display
```jsx
import React from 'react';
import Comments from './pages/Comments';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <h1 className="text-3xl font-bold text-gray-900">
            Social Media Comments Manager
          </h1>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto py-6 px-4">
        <Comments />
      </main>
    </div>
  );
}

export default App;
```

### With Custom Layout
```jsx
import React from 'react';
import Comments from './pages/Comments';

function CustomCommentsPage() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Sidebar */}
      <div className="lg:col-span-1">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Quick Stats</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Total Comments:</span>
              <span className="font-bold">1,234</span>
            </div>
            <div className="flex justify-between">
              <span>Pending:</span>
              <span className="text-yellow-600">45</span>
            </div>
            <div className="flex justify-between">
              <span>Responded:</span>
              <span className="text-green-600">1,189</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="lg:col-span-3">
        <Comments />
      </div>
    </div>
  );
}

export default CustomCommentsPage;
```

## ⚙️ Advanced Configuration

### Custom AI Analysis Settings
```jsx
import React, { useState } from 'react';
import Comments from './pages/Comments';

function AdvancedCommentsManager() {
  const [aiSettings, setAiSettings] = useState({
    analysisMode: 'quantum',
    neuralDepth: 25,
    quantumProcessing: true,
    realTimeAnalysis: true,
    emotionDetection: 'maximum'
  });

  return (
    <div className="space-y-6">
      {/* AI Configuration Panel */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">AI Configuration</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Analysis Mode
            </label>
            <select 
              value={aiSettings.analysisMode}
              onChange={(e) => setAiSettings({
                ...aiSettings, 
                analysisMode: e.target.value
              })}
              className="w-full px-3 py-2 border rounded-md"
            >
              <option value="basic">Basic</option>
              <option value="advanced">Advanced</option>
              <option value="quantum">Quantum</option>
              <option value="transcendental">Transcendental</option>
              <option value="omnipotent">Omnipotent</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">
              Neural Network Depth
            </label>
            <input
              type="range"
              min="1"
              max="50"
              value={aiSettings.neuralDepth}
              onChange={(e) => setAiSettings({
                ...aiSettings, 
                neuralDepth: parseInt(e.target.value)
              })}
              className="w-full"
            />
            <span className="text-sm text-gray-600">
              {aiSettings.neuralDepth} layers
            </span>
          </div>
          
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={aiSettings.quantumProcessing}
                onChange={(e) => setAiSettings({
                  ...aiSettings, 
                  quantumProcessing: e.target.checked
                })}
                className="mr-2"
              />
              Quantum Processing
            </label>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={aiSettings.realTimeAnalysis}
                onChange={(e) => setAiSettings({
                  ...aiSettings, 
                  realTimeAnalysis: e.target.checked
                })}
                className="mr-2"
              />
              Real-time Analysis
            </label>
          </div>
        </div>
      </div>
      
      {/* Comments Component */}
      <Comments />
    </div>
  );
}

export default AdvancedCommentsManager;
```

### Custom Filtering and Search
```jsx
import React, { useState, useCallback } from 'react';
import Comments from './pages/Comments';

function FilteredCommentsView() {
  const [filters, setFilters] = useState({
    sentiment: 'all',
    platform: 'all',
    urgency: 'all',
    dateRange: '7d',
    searchTerm: ''
  });

  const handleFilterChange = useCallback((key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  }, []);

  return (
    <div className="space-y-6">
      {/* Custom Filter Panel */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Advanced Filters</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Sentiment</label>
            <select
              value={filters.sentiment}
              onChange={(e) => handleFilterChange('sentiment', e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
            >
              <option value="all">All Sentiments</option>
              <option value="positive">Positive</option>
              <option value="negative">Negative</option>
              <option value="neutral">Neutral</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Platform</label>
            <select
              value={filters.platform}
              onChange={(e) => handleFilterChange('platform', e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
            >
              <option value="all">All Platforms</option>
              <option value="facebook">Facebook</option>
              <option value="instagram">Instagram</option>
              <option value="twitter">Twitter</option>
              <option value="linkedin">LinkedIn</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Urgency</label>
            <select
              value={filters.urgency}
              onChange={(e) => handleFilterChange('urgency', e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
            >
              <option value="all">All Urgency Levels</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Date Range</label>
            <select
              value={filters.dateRange}
              onChange={(e) => handleFilterChange('dateRange', e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
            >
              <option value="1d">Last 24 hours</option>
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Search</label>
            <input
              type="text"
              value={filters.searchTerm}
              onChange={(e) => handleFilterChange('searchTerm', e.target.value)}
              placeholder="Search comments..."
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>
        </div>
        
        <div className="mt-4 flex justify-between">
          <button
            onClick={() => setFilters({
              sentiment: 'all',
              platform: 'all',
              urgency: 'all',
              dateRange: '7d',
              searchTerm: ''
            })}
            className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Clear Filters
          </button>
          
          <div className="text-sm text-gray-600">
            Active filters: {Object.values(filters).filter(v => v !== 'all' && v !== '7d' && v !== '').length}
          </div>
        </div>
      </div>
      
      {/* Comments Component */}
      <Comments />
    </div>
  );
}

export default FilteredCommentsView;
```

## 🎨 Custom Styling

### Dark Mode Implementation
```jsx
import React, { useState, useEffect } from 'react';
import Comments from './pages/Comments';

function DarkModeComments() {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // Apply dark mode class to document
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  return (
    <div className={`min-h-screen transition-colors ${
      isDarkMode ? 'bg-gray-900' : 'bg-gray-50'
    }`}>
      {/* Header with Dark Mode Toggle */}
      <header className={`shadow transition-colors ${
        isDarkMode ? 'bg-gray-800' : 'bg-white'
      }`}>
        <div className="max-w-7xl mx-auto py-6 px-4 flex justify-between items-center">
          <h1 className={`text-3xl font-bold transition-colors ${
            isDarkMode ? 'text-white' : 'text-gray-900'
          }`}>
            Comments Manager
          </h1>
          
          <button
            onClick={() => setIsDarkMode(!isDarkMode)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              isDarkMode 
                ? 'bg-gray-700 text-white hover:bg-gray-600' 
                : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
            }`}
          >
            {isDarkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
          </button>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto py-6 px-4">
        <Comments />
      </main>
    </div>
  );
}

export default DarkModeComments;
```

### Custom Theme Colors
```jsx
import React from 'react';
import Comments from './pages/Comments';

function CustomThemeComments() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      {/* Custom Header */}
      <header className="bg-gradient-to-r from-purple-600 to-blue-600 shadow-lg">
        <div className="max-w-7xl mx-auto py-8 px-4">
          <h1 className="text-4xl font-bold text-white text-center">
            🚀 AI-Powered Comments Manager
          </h1>
          <p className="text-purple-100 text-center mt-2">
            Advanced sentiment analysis and automated response generation
          </p>
        </div>
      </header>
      
      {/* Custom Stats Cards */}
      <div className="max-w-7xl mx-auto py-6 px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-full">
                <span className="text-2xl">📈</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Comments</p>
                <p className="text-2xl font-bold text-gray-900">1,234</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-full">
                <span className="text-2xl">🤖</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">AI Responses</p>
                <p className="text-2xl font-bold text-gray-900">892</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-yellow-500">
            <div className="flex items-center">
              <div className="p-3 bg-yellow-100 rounded-full">
                <span className="text-2xl">⏱️</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
                <p className="text-2xl font-bold text-gray-900">2.3s</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-full">
                <span className="text-2xl">🎯</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Accuracy</p>
                <p className="text-2xl font-bold text-gray-900">98.7%</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Comments Component */}
        <Comments />
      </div>
    </div>
  );
}

export default CustomThemeComments;
```

## 🔌 API Integration

### Custom API Configuration
```jsx
import React, { createContext, useContext } from 'react';
import Comments from './pages/Comments';

// API Configuration Context
const ApiConfigContext = createContext();

export const useApiConfig = () => {
  const context = useContext(ApiConfigContext);
  if (!context) {
    throw new Error('useApiConfig must be used within ApiConfigProvider');
  }
  return context;
};

function ApiConfigProvider({ children }) {
  const apiConfig = {
    baseURL: process.env.REACT_APP_API_BASE_URL || 'https://api.example.com',
    endpoints: {
      comments: '/api/comments',
      generateResponse: '/api/generate-response',
      sendResponse: '/api/send-response',
      analytics: '/api/comments/analytics'
    },
    headers: {
      'Authorization': `Bearer ${process.env.REACT_APP_API_TOKEN}`,
      'Content-Type': 'application/json'
    },
    timeout: 30000,
    retryAttempts: 3
  };

  return (
    <ApiConfigContext.Provider value={apiConfig}>
      {children}
    </ApiConfigContext.Provider>
  );
}

function ApiIntegratedComments() {
  return (
    <ApiConfigProvider>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto py-6 px-4">
            <h1 className="text-3xl font-bold text-gray-900">
              API-Integrated Comments Manager
            </h1>
            <p className="text-gray-600 mt-2">
              Connected to: {process.env.REACT_APP_API_BASE_URL}
            </p>
          </div>
        </header>
        
        <main className="max-w-7xl mx-auto py-6 px-4">
          <Comments />
        </main>
      </div>
    </ApiConfigProvider>
  );
}

export default ApiIntegratedComments;
```

### Real-time Updates with WebSocket
```jsx
import React, { useState, useEffect } from 'react';
import Comments from './pages/Comments';

function RealtimeComments() {
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    // WebSocket connection for real-time updates
    const ws = new WebSocket(process.env.REACT_APP_WS_URL || 'ws://localhost:8080');
    
    ws.onopen = () => {
      setConnectionStatus('connected');
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'new_comment') {
        setLastUpdate(new Date());
        // Trigger comments refresh
        window.dispatchEvent(new CustomEvent('comments-update', { detail: data }));
      }
    };
    
    ws.onclose = () => {
      setConnectionStatus('disconnected');
      console.log('WebSocket disconnected');
    };
    
    ws.onerror = (error) => {
      setConnectionStatus('error');
      console.error('WebSocket error:', error);
    };
    
    return () => {
      ws.close();
    };
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Connection Status Indicator */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto py-2 px-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                connectionStatus === 'connected' ? 'bg-green-500' : 
                connectionStatus === 'error' ? 'bg-red-500' : 'bg-yellow-500'
              }`}></div>
              <span className="text-sm text-gray-600">
                {connectionStatus === 'connected' ? 'Connected' : 
                 connectionStatus === 'error' ? 'Connection Error' : 'Connecting...'}
              </span>
            </div>
            
            {lastUpdate && (
              <span className="text-sm text-gray-500">
                Last update: {lastUpdate.toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>
      </div>
      
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <h1 className="text-3xl font-bold text-gray-900">
            Real-time Comments Manager
          </h1>
          <p className="text-gray-600 mt-2">
            Live updates from social media platforms
          </p>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto py-6 px-4">
        <Comments />
      </main>
    </div>
  );
}

export default RealtimeComments;
```

## 🌍 Real-world Use Cases

### E-commerce Customer Support
```jsx
import React from 'react';
import Comments from './pages/Comments';

function EcommerceCommentsManager() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Customer Support Hub
              </h1>
              <p className="text-gray-600 mt-2">
                Manage customer inquiries across all platforms
              </p>
            </div>
            
            <div className="flex space-x-4">
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                Export Reports
              </button>
              <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                Bulk Actions
              </button>
            </div>
          </div>
        </div>
      </header>
      
      {/* Customer Support Metrics */}
      <div className="max-w-7xl mx-auto py-6 px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Response Time Metrics
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Average Response Time:</span>
                <span className="font-semibold">2.3 minutes</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">First Response:</span>
                <span className="font-semibold">45 seconds</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Resolution Time:</span>
                <span className="font-semibold">8.7 minutes</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Customer Satisfaction
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Satisfaction Score:</span>
                <span className="font-semibold text-green-600">4.8/5</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Positive Feedback:</span>
                <span className="font-semibold text-green-600">89%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Issue Resolution:</span>
                <span className="font-semibold text-green-600">94%</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Platform Distribution
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Facebook:</span>
                <span className="font-semibold">45%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Instagram:</span>
                <span className="font-semibold">30%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Twitter:</span>
                <span className="font-semibold">25%</span>
              </div>
            </div>
          </div>
        </div>
        
        <Comments />
      </div>
    </div>
  );
}

export default EcommerceCommentsManager;
```

### Social Media Marketing Agency
```jsx
import React, { useState } from 'react';
import Comments from './pages/Comments';

function MarketingAgencyComments() {
  const [selectedClient, setSelectedClient] = useState('all');
  const [selectedCampaign, setSelectedCampaign] = useState('all');

  const clients = [
    { id: 'all', name: 'All Clients' },
    { id: 'client1', name: 'TechCorp Inc.' },
    { id: 'client2', name: 'Fashion Brand' },
    { id: 'client3', name: 'Restaurant Chain' }
  ];

  const campaigns = [
    { id: 'all', name: 'All Campaigns' },
    { id: 'campaign1', name: 'Summer Sale 2024' },
    { id: 'campaign2', name: 'Product Launch' },
    { id: 'campaign3', name: 'Brand Awareness' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <h1 className="text-3xl font-bold text-gray-900">
            Marketing Agency Dashboard
          </h1>
          <p className="text-gray-600 mt-2">
            Multi-client social media management
          </p>
        </div>
      </header>
      
      <div className="max-w-7xl mx-auto py-6 px-4">
        {/* Client and Campaign Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Campaign Management
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Client
              </label>
              <select
                value={selectedClient}
                onChange={(e) => setSelectedClient(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {clients.map(client => (
                  <option key={client.id} value={client.id}>
                    {client.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Campaign
              </label>
              <select
                value={selectedCampaign}
                onChange={(e) => setSelectedCampaign(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {campaigns.map(campaign => (
                  <option key={campaign.id} value={campaign.id}>
                    {campaign.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
        
        {/* Campaign Performance Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-full">
                <span className="text-2xl">📊</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Engagement</p>
                <p className="text-2xl font-bold text-gray-900">12.5K</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-full">
                <span className="text-2xl">👍</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Positive Sentiment</p>
                <p className="text-2xl font-bold text-gray-900">87%</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-full">
                <span className="text-2xl">🚀</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Viral Potential</p>
                <p className="text-2xl font-bold text-gray-900">23%</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-yellow-100 rounded-full">
                <span className="text-2xl">⚡</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Response Rate</p>
                <p className="text-2xl font-bold text-gray-900">94%</p>
              </div>
            </div>
          </div>
        </div>
        
        <Comments />
      </div>
    </div>
  );
}

export default MarketingAgencyComments;
```

## ⚡ Performance Optimization

### Lazy Loading Implementation
```jsx
import React, { Suspense, lazy } from 'react';

// Lazy load the Comments component
const Comments = lazy(() => import('./pages/Comments'));

function OptimizedCommentsApp() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <h1 className="text-3xl font-bold text-gray-900">
            Optimized Comments Manager
          </h1>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto py-6 px-4">
        <Suspense fallback={
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Loading Comments...</span>
          </div>
        }>
          <Comments />
        </Suspense>
      </main>
    </div>
  );
}

export default OptimizedCommentsApp;
```

### Error Boundary Implementation
```jsx
import React from 'react';
import Comments from './pages/Comments';

class CommentsErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Comments Error:', error, errorInfo);
    // Log to error reporting service
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full mx-4">
            <div className="text-center">
              <div className="text-6xl mb-4">⚠️</div>
              <h1 className="text-2xl font-bold text-gray-900 mb-4">
                Something went wrong
              </h1>
              <p className="text-gray-600 mb-6">
                We're sorry, but there was an error loading the comments. 
                Please try refreshing the page.
              </p>
              <button
                onClick={() => window.location.reload()}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Refresh Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

function ErrorHandledComments() {
  return (
    <CommentsErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto py-6 px-4">
            <h1 className="text-3xl font-bold text-gray-900">
              Error-Handled Comments Manager
            </h1>
          </div>
        </header>
        
        <main className="max-w-7xl mx-auto py-6 px-4">
          <Comments />
        </main>
      </div>
    </CommentsErrorBoundary>
  );
}

export default ErrorHandledComments;
```

## 📱 Mobile Responsive Implementation

### Mobile-First Design
```jsx
import React from 'react';
import Comments from './pages/Comments';

function MobileOptimizedComments() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile Header */}
      <header className="bg-white shadow-sm lg:shadow">
        <div className="max-w-7xl mx-auto py-4 lg:py-6 px-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl lg:text-3xl font-bold text-gray-900">
              Comments
            </h1>
            
            {/* Mobile Menu Button */}
            <button className="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
          
          <p className="text-sm lg:text-base text-gray-600 mt-2">
            Manage your social media comments
          </p>
        </div>
      </header>
      
      {/* Mobile-Optimized Content */}
      <main className="max-w-7xl mx-auto py-4 lg:py-6 px-4">
        {/* Mobile Stats Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-4 lg:p-6">
            <div className="text-center">
              <p className="text-xs lg:text-sm font-medium text-gray-600">Total</p>
              <p className="text-lg lg:text-2xl font-bold text-gray-900">1.2K</p>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-4 lg:p-6">
            <div className="text-center">
              <p className="text-xs lg:text-sm font-medium text-gray-600">Pending</p>
              <p className="text-lg lg:text-2xl font-bold text-yellow-600">45</p>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-4 lg:p-6">
            <div className="text-center">
              <p className="text-xs lg:text-sm font-medium text-gray-600">Responded</p>
              <p className="text-lg lg:text-2xl font-bold text-green-600">1.1K</p>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-4 lg:p-6">
            <div className="text-center">
              <p className="text-xs lg:text-sm font-medium text-gray-600">Accuracy</p>
              <p className="text-lg lg:text-2xl font-bold text-blue-600">98%</p>
            </div>
          </div>
        </div>
        
        <Comments />
      </main>
    </div>
  );
}

export default MobileOptimizedComments;
```

---

## 🎯 Best Practices Summary

1. **Always use error boundaries** for production applications
2. **Implement lazy loading** for better performance
3. **Use proper TypeScript types** for better development experience
4. **Add loading states** for better user experience
5. **Implement proper error handling** for API calls
6. **Use responsive design** for mobile compatibility
7. **Add accessibility features** for better usability
8. **Implement proper state management** for complex applications
9. **Use proper testing** for reliability
10. **Follow security best practices** for data protection

---

*Examples Documentation v2.0.0 - Last updated: December 2024*









