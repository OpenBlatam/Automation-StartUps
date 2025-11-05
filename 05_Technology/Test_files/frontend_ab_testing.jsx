// 🚀 Frontend React para SaaS A/B Testing Platform
// Interfaz moderna y funcional para gestión de tests A/B con IA

import React, { useState, useEffect, useCallback } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Area, AreaChart
} from 'recharts';

// Componente principal del Dashboard
const ABTestingDashboard = () => {
  const [tests, setTests] = useState([]);
  const [activeTest, setActiveTest] = useState(null);
  const [analytics, setAnalytics] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Actualizar cada 30s
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await fetch('/api/dashboard');
      const data = await response.json();
      setAnalytics(data);
      
      const testsResponse = await fetch('/api/tests');
      const testsData = await testsResponse.json();
      setTests(testsData);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                🚀 AI A/B Testing Platform
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                + Nuevo Test
              </button>
              <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Métricas principales */}
        <MetricsOverview analytics={analytics} />
        
        {/* Gráficos en tiempo real */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <RealTimeChart tests={tests} />
          <ConversionTrends tests={tests} />
        </div>

        {/* Lista de tests */}
        <TestsList 
          tests={tests} 
          onTestSelect={setActiveTest}
          onTestStart={handleTestStart}
          onTestStop={handleTestStop}
        />

        {/* Modal de test activo */}
        {activeTest && (
          <TestDetailModal 
            test={activeTest} 
            onClose={() => setActiveTest(null)}
            onUpdate={loadDashboardData}
          />
        )}
      </div>
    </div>
  );
};

// Componente de métricas principales
const MetricsOverview = ({ analytics }) => {
  const metrics = [
    {
      title: 'Tests Activos',
      value: analytics.activeTests || 0,
      change: '+12%',
      changeType: 'positive',
      icon: '🧪'
    },
    {
      title: 'Conversiones Totales',
      value: analytics.totalConversions || 0,
      change: '+8.2%',
      changeType: 'positive',
      icon: '📈'
    },
    {
      title: 'Mejora Promedio',
      value: `${(analytics.averageImprovement || 0).toFixed(1)}%`,
      change: '+0.3%',
      changeType: 'positive',
      icon: '🎯'
    },
    {
      title: 'ROI Promedio',
      value: '1,200%',
      change: '+15%',
      changeType: 'positive',
      icon: '💰'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {metrics.map((metric, index) => (
        <div key={index} className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">{metric.icon}</span>
            </div>
            <div className="ml-4 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  {metric.title}
                </dt>
                <dd className="flex items-baseline">
                  <div className="text-2xl font-semibold text-gray-900">
                    {metric.value}
                  </div>
                  <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                    metric.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {metric.change}
                  </div>
                </dd>
              </dl>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// Gráfico en tiempo real
const RealTimeChart = ({ tests }) => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const generateData = () => {
      const now = new Date();
      const data = [];
      
      for (let i = 23; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 60 * 60 * 1000);
        data.push({
          time: time.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }),
          conversions: Math.floor(Math.random() * 50) + 10,
          visitors: Math.floor(Math.random() * 200) + 100
        });
      }
      
      setData(data);
    };

    generateData();
    const interval = setInterval(generateData, 60000); // Actualizar cada minuto
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        📊 Conversiones en Tiempo Real
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Area 
            type="monotone" 
            dataKey="conversions" 
            stackId="1" 
            stroke="#3B82F6" 
            fill="#3B82F6" 
            fillOpacity={0.6}
          />
          <Area 
            type="monotone" 
            dataKey="visitors" 
            stackId="2" 
            stroke="#10B981" 
            fill="#10B981" 
            fillOpacity={0.6}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

// Tendencias de conversión
const ConversionTrends = ({ tests }) => {
  const data = tests.map(test => ({
    name: test.name,
    conversionRate: test.metrics.conversionRate * 100,
    improvement: test.analysis?.improvement || 0
  }));

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        📈 Tendencias de Conversión
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="conversionRate" fill="#3B82F6" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

// Lista de tests
const TestsList = ({ tests, onTestSelect, onTestStart, onTestStop }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'paused': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'running': return 'Ejecutándose';
      case 'completed': return 'Completado';
      case 'draft': return 'Borrador';
      case 'paused': return 'Pausado';
      default: return 'Desconocido';
    }
  };

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">
          🧪 Tests A/B
        </h3>
      </div>
      <div className="divide-y divide-gray-200">
        {tests.map((test) => (
          <div key={test.id} className="px-6 py-4 hover:bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center">
                  <h4 className="text-sm font-medium text-gray-900">
                    {test.name}
                  </h4>
                  <span className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(test.status)}`}>
                    {getStatusText(test.status)}
                  </span>
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  {test.description}
                </p>
                <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                  <span>👥 {test.metrics.visitors} visitantes</span>
                  <span>📈 {test.metrics.conversions} conversiones</span>
                  <span>🎯 {(test.metrics.conversionRate * 100).toFixed(2)}% CVR</span>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => onTestSelect(test)}
                  className="text-blue-600 hover:text-blue-900 text-sm font-medium"
                >
                  Ver Detalles
                </button>
                {test.status === 'draft' && (
                  <button
                    onClick={() => onTestStart(test.id)}
                    className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                  >
                    Iniciar
                  </button>
                )}
                {test.status === 'running' && (
                  <button
                    onClick={() => onTestStop(test.id)}
                    className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                  >
                    Detener
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Modal de detalles del test
const TestDetailModal = ({ test, onClose, onUpdate }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [variants, setVariants] = useState(test.variants || []);

  const tabs = [
    { id: 'overview', name: 'Resumen', icon: '📊' },
    { id: 'variants', name: 'Variantes', icon: '🧪' },
    { id: 'analytics', name: 'Analytics', icon: '📈' },
    { id: 'insights', name: 'Insights IA', icon: '🤖' }
  ];

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              {test.name}
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          {/* Content */}
          <div className="mt-6">
            {activeTab === 'overview' && <TestOverview test={test} />}
            {activeTab === 'variants' && <TestVariants variants={variants} />}
            {activeTab === 'analytics' && <TestAnalytics test={test} />}
            {activeTab === 'insights' && <TestInsights test={test} />}
          </div>
        </div>
      </div>
    </div>
  );
};

// Resumen del test
const TestOverview = ({ test }) => {
  const metrics = [
    { label: 'Visitantes', value: test.metrics.visitors, icon: '👥' },
    { label: 'Conversiones', value: test.metrics.conversions, icon: '📈' },
    { label: 'Tasa de Conversión', value: `${(test.metrics.conversionRate * 100).toFixed(2)}%`, icon: '🎯' },
    { label: 'Mejora', value: `${test.analysis?.improvement || 0}%`, icon: '🚀' }
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {metrics.map((metric, index) => (
          <div key={index} className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl mb-2">{metric.icon}</div>
            <div className="text-2xl font-bold text-gray-900">{metric.value}</div>
            <div className="text-sm text-gray-500">{metric.label}</div>
          </div>
        ))}
      </div>

      <div className="bg-blue-50 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">🎯 Objetivo del Test</h4>
        <p className="text-blue-800">{test.description}</p>
      </div>

      {test.analysis && (
        <div className="bg-green-50 rounded-lg p-4">
          <h4 className="font-medium text-green-900 mb-2">✅ Resultados</h4>
          <p className="text-green-800">
            La variante ganadora es <strong>{test.analysis.winner?.name}</strong> con una mejora del <strong>{test.analysis.improvement}%</strong>
          </p>
        </div>
      )}
    </div>
  );
};

// Variantes del test
const TestVariants = ({ variants }) => {
  return (
    <div className="space-y-4">
      {variants.map((variant, index) => (
        <div key={variant.id} className="border rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-medium text-gray-900">{variant.name}</h4>
            <span className="text-sm text-gray-500">
              {variant.weight * 100}% del tráfico
            </span>
          </div>
          <div className="bg-gray-50 rounded p-3 mb-3">
            <p className="text-gray-800">{variant.content}</p>
          </div>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div className="text-center">
              <div className="font-medium text-gray-900">{variant.visitors || 0}</div>
              <div className="text-gray-500">Visitantes</div>
            </div>
            <div className="text-center">
              <div className="font-medium text-gray-900">{variant.conversions || 0}</div>
              <div className="text-gray-500">Conversiones</div>
            </div>
            <div className="text-center">
              <div className="font-medium text-gray-900">
                {((variant.conversions || 0) / (variant.visitors || 1) * 100).toFixed(2)}%
              </div>
              <div className="text-gray-500">CVR</div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// Analytics del test
const TestAnalytics = ({ test }) => {
  const data = test.variants?.map(variant => ({
    name: variant.name,
    visitors: variant.visitors || 0,
    conversions: variant.conversions || 0,
    conversionRate: ((variant.conversions || 0) / (variant.visitors || 1) * 100)
  })) || [];

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg p-6">
        <h4 className="font-medium text-gray-900 mb-4">📊 Comparación de Variantes</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="conversionRate" fill="#3B82F6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg p-6">
          <h4 className="font-medium text-gray-900 mb-4">👥 Distribución de Visitantes</h4>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={data}
                dataKey="visitors"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
              />
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg p-6">
          <h4 className="font-medium text-gray-900 mb-4">📈 Conversiones por Variante</h4>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={data}
                dataKey="conversions"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#82ca9d"
              />
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

// Insights de IA
const TestInsights = ({ test }) => {
  const insights = test.analysis?.insights || [];
  const recommendations = test.analysis?.recommendations || [];

  return (
    <div className="space-y-6">
      {insights.length > 0 && (
        <div className="bg-blue-50 rounded-lg p-6">
          <h4 className="font-medium text-blue-900 mb-4">🤖 Insights de IA</h4>
          <div className="space-y-3">
            {insights.map((insight, index) => (
              <div key={index} className="flex items-start">
                <span className="text-blue-600 mr-2">💡</span>
                <p className="text-blue-800">{insight.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {recommendations.length > 0 && (
        <div className="bg-green-50 rounded-lg p-6">
          <h4 className="font-medium text-green-900 mb-4">🎯 Recomendaciones</h4>
          <div className="space-y-3">
            {recommendations.map((rec, index) => (
              <div key={index} className="flex items-start">
                <span className="text-green-600 mr-2">✅</span>
                <p className="text-green-800">{rec.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {insights.length === 0 && recommendations.length === 0 && (
        <div className="text-center py-8">
          <div className="text-gray-400 text-4xl mb-4">🤖</div>
          <p className="text-gray-500">No hay insights disponibles aún</p>
        </div>
      )}
    </div>
  );
};

// Spinner de carga
const LoadingSpinner = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
  </div>
);

// Funciones de manejo de eventos
const handleTestStart = async (testId) => {
  try {
    await fetch(`/api/tests/${testId}/start`, { method: 'POST' });
    // Actualizar UI
  } catch (error) {
    console.error('Error starting test:', error);
  }
};

const handleTestStop = async (testId) => {
  try {
    await fetch(`/api/tests/${testId}/stop`, { method: 'POST' });
    // Actualizar UI
  } catch (error) {
    console.error('Error stopping test:', error);
  }
};

export default ABTestingDashboard;

