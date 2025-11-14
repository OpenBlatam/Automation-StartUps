import React, { useState, useEffect } from 'react';
import { 
  Zap, 
  Play, 
  Pause, 
  Square, 
  Settings, 
  Plus, 
  Edit, 
  Trash2, 
  BarChart3, 
  Clock, 
  CheckCircle, 
  AlertTriangle,
  Brain,
  Target,
  TrendingUp,
  Activity,
  Workflow,
  Filter,
  Search,
  MoreVertical,
  Copy,
  Download
} from 'lucide-react';

interface AutomationWorkflow {
  id: string;
  name: string;
  description: string;
  consciousnessLevel: number;
  status: 'ACTIVE' | 'PAUSED' | 'DISABLED';
  lastExecuted?: string;
  executionCount: number;
  successRate: number;
  triggers: AutomationTrigger[];
  actions: AutomationAction[];
  createdAt: string;
}

interface AutomationTrigger {
  id: string;
  type: 'SCHEDULE' | 'EVENT' | 'CONDITION' | 'WEBHOOK' | 'CONSCIOUSNESS_LEVEL';
  config: any;
  enabled: boolean;
}

interface AutomationAction {
  id: string;
  type: 'GENERATE_CONTENT' | 'SEND_EMAIL' | 'UPDATE_CAMPAIGN' | 'ANALYZE_PERFORMANCE' | 'GENERATE_INSIGHTS' | 'NOTIFY_USER';
  config: any;
  order: number;
  enabled: boolean;
}

interface AutomationExecution {
  id: string;
  workflowId: string;
  status: 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  startTime: string;
  endTime?: string;
  duration?: number;
  error?: string;
  results: any[];
}

const WORKFLOW_TYPES = {
  CONTENT_GENERATION: { label: 'Content Generation', icon: Target, color: 'bg-blue-500' },
  EMAIL_MARKETING: { label: 'Email Marketing', icon: Zap, color: 'bg-green-500' },
  CAMPAIGN_MANAGEMENT: { label: 'Campaign Management', icon: BarChart3, color: 'bg-purple-500' },
  PERFORMANCE_ANALYSIS: { label: 'Performance Analysis', icon: TrendingUp, color: 'bg-orange-500' },
  INSIGHT_GENERATION: { label: 'Insight Generation', icon: Brain, color: 'bg-indigo-500' },
  NOTIFICATION: { label: 'Notifications', icon: Activity, color: 'bg-pink-500' },
};

const TRIGGER_TYPES = {
  SCHEDULE: { label: 'Schedule', icon: Clock },
  EVENT: { label: 'Event', icon: Zap },
  CONDITION: { label: 'Condition', icon: Target },
  WEBHOOK: { label: 'Webhook', icon: Workflow },
  CONSCIOUSNESS_LEVEL: { label: 'Consciousness Level', icon: Brain },
};

const ACTION_TYPES = {
  GENERATE_CONTENT: { label: 'Generate Content', icon: Target },
  SEND_EMAIL: { label: 'Send Email', icon: Zap },
  UPDATE_CAMPAIGN: { label: 'Update Campaign', icon: BarChart3 },
  ANALYZE_PERFORMANCE: { label: 'Analyze Performance', icon: TrendingUp },
  GENERATE_INSIGHTS: { label: 'Generate Insights', icon: Brain },
  NOTIFY_USER: { label: 'Notify User', icon: Activity },
};

export const NeuralAutomation: React.FC = () => {
  const [workflows, setWorkflows] = useState<AutomationWorkflow[]>([]);
  const [executions, setExecutions] = useState<AutomationExecution[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedWorkflow, setSelectedWorkflow] = useState<AutomationWorkflow | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadAutomationData();
  }, []);

  const loadAutomationData = async () => {
    try {
      setIsLoading(true);
      
      // Mock data - replace with actual API calls
      const mockWorkflows: AutomationWorkflow[] = [
        {
          id: '1',
          name: 'Daily Content Generation',
          description: 'Automatically generate content every morning at 9 AM',
          consciousnessLevel: 75,
          status: 'ACTIVE',
          lastExecuted: '2024-01-07T09:00:00Z',
          executionCount: 15,
          successRate: 93.3,
          triggers: [
            { id: '1', type: 'SCHEDULE', config: { cron: '0 9 * * *' }, enabled: true }
          ],
          actions: [
            { id: '1', type: 'GENERATE_CONTENT', config: { type: 'BLOG_POST', count: 3 }, order: 1, enabled: true },
            { id: '2', type: 'NOTIFY_USER', config: { message: 'Content generated successfully' }, order: 2, enabled: true }
          ],
          createdAt: '2024-01-01T00:00:00Z'
        },
        {
          id: '2',
          name: 'Consciousness Level Monitor',
          description: 'Monitor consciousness level and trigger optimizations',
          consciousnessLevel: 80,
          status: 'ACTIVE',
          lastExecuted: '2024-01-07T10:30:00Z',
          executionCount: 8,
          successRate: 87.5,
          triggers: [
            { id: '2', type: 'CONSCIOUSNESS_LEVEL', config: { threshold: 70, direction: 'BELOW' }, enabled: true }
          ],
          actions: [
            { id: '3', type: 'GENERATE_INSIGHTS', config: { type: 'OPTIMIZATION' }, order: 1, enabled: true },
            { id: '4', type: 'NOTIFY_USER', config: { message: 'Consciousness level optimization needed' }, order: 2, enabled: true }
          ],
          createdAt: '2024-01-02T00:00:00Z'
        },
        {
          id: '3',
          name: 'Weekly Performance Report',
          description: 'Generate and send weekly performance reports',
          consciousnessLevel: 65,
          status: 'PAUSED',
          lastExecuted: '2024-01-01T17:00:00Z',
          executionCount: 4,
          successRate: 100,
          triggers: [
            { id: '3', type: 'SCHEDULE', config: { cron: '0 17 * * 1' }, enabled: true }
          ],
          actions: [
            { id: '5', type: 'ANALYZE_PERFORMANCE', config: { period: 'WEEKLY' }, order: 1, enabled: true },
            { id: '6', type: 'SEND_EMAIL', config: { template: 'WEEKLY_REPORT' }, order: 2, enabled: true }
          ],
          createdAt: '2023-12-15T00:00:00Z'
        }
      ];

      const mockExecutions: AutomationExecution[] = [
        {
          id: '1',
          workflowId: '1',
          status: 'COMPLETED',
          startTime: '2024-01-07T09:00:00Z',
          endTime: '2024-01-07T09:02:30Z',
          duration: 150000,
          results: [{ type: 'content_generation', result: '3 blog posts generated' }]
        },
        {
          id: '2',
          workflowId: '2',
          status: 'COMPLETED',
          startTime: '2024-01-07T10:30:00Z',
          endTime: '2024-01-07T10:32:15Z',
          duration: 135000,
          results: [{ type: 'insight_generation', result: 'Optimization insights generated' }]
        },
        {
          id: '3',
          workflowId: '1',
          status: 'FAILED',
          startTime: '2024-01-06T09:00:00Z',
          endTime: '2024-01-06T09:01:45Z',
          duration: 105000,
          error: 'OpenAI API rate limit exceeded',
          results: []
        }
      ];

      setWorkflows(mockWorkflows);
      setExecutions(mockExecutions);
      
    } catch (error) {
      console.error('Error loading automation data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredWorkflows = workflows.filter(workflow => {
    const matchesSearch = workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         workflow.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || workflow.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const getStatusColor = (status: string) => {
    const colors = {
      ACTIVE: 'text-green-600 bg-green-100',
      PAUSED: 'text-yellow-600 bg-yellow-100',
      DISABLED: 'text-gray-600 bg-gray-100',
    };
    return colors[status as keyof typeof colors] || 'text-gray-600 bg-gray-100';
  };

  const getStatusIcon = (status: string) => {
    const icons = {
      ACTIVE: CheckCircle,
      PAUSED: Pause,
      DISABLED: Square,
    };
    const Icon = icons[status as keyof typeof icons] || Square;
    return <Icon className="w-4 h-4" />;
  };

  const getExecutionStatusColor = (status: string) => {
    const colors = {
      RUNNING: 'text-blue-600 bg-blue-100',
      COMPLETED: 'text-green-600 bg-green-100',
      FAILED: 'text-red-600 bg-red-100',
      CANCELLED: 'text-gray-600 bg-gray-100',
    };
    return colors[status as keyof typeof colors] || 'text-gray-600 bg-gray-100';
  };

  const formatDuration = (duration: number) => {
    const seconds = Math.floor(duration / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        <span className="ml-2 text-gray-600">Loading automation data...</span>
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
              <Zap className="w-8 h-8 mr-3 text-purple-600" />
              Neural Automation
            </h1>
            <p className="text-gray-600">
              Intelligent automation workflows that adapt to your consciousness level
            </p>
          </div>
          
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Workflow
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Workflows</p>
              <p className="text-2xl font-bold text-gray-900">{workflows.length}</p>
            </div>
            <Workflow className="w-8 h-8 text-purple-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Workflows</p>
              <p className="text-2xl font-bold text-green-600">
                {workflows.filter(w => w.status === 'ACTIVE').length}
              </p>
            </div>
            <Play className="w-8 h-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Executions</p>
              <p className="text-2xl font-bold text-blue-600">
                {workflows.reduce((sum, w) => sum + w.executionCount, 0)}
              </p>
            </div>
            <Activity className="w-8 h-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold text-orange-600">
                {Math.round(workflows.reduce((sum, w) => sum + w.successRate, 0) / workflows.length)}%
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-orange-600" />
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search workflows..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
        </div>
        
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="all">All Status</option>
          <option value="ACTIVE">Active</option>
          <option value="PAUSED">Paused</option>
          <option value="DISABLED">Disabled</option>
        </select>
      </div>

      {/* Workflows Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
        {filteredWorkflows.map((workflow) => (
          <div key={workflow.id} className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-1">{workflow.name}</h3>
                <p className="text-sm text-gray-600 mb-2">{workflow.description}</p>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium flex items-center ${getStatusColor(workflow.status)}`}>
                    {getStatusIcon(workflow.status)}
                    <span className="ml-1">{workflow.status}</span>
                  </span>
                  <span className="text-xs text-gray-500">
                    Level {workflow.consciousnessLevel}%
                  </span>
                </div>
              </div>
              
              <div className="flex items-center space-x-1">
                <button className="p-1 text-gray-400 hover:text-gray-600">
                  <Edit className="w-4 h-4" />
                </button>
                <button className="p-1 text-gray-400 hover:text-gray-600">
                  <MoreVertical className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Executions</span>
                <span className="font-medium">{workflow.executionCount}</span>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Success Rate</span>
                <span className="font-medium">{workflow.successRate}%</span>
              </div>
              
              {workflow.lastExecuted && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Last Executed</span>
                  <span className="font-medium">{formatDate(workflow.lastExecuted)}</span>
                </div>
              )}

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Triggers</span>
                <span className="font-medium">{workflow.triggers.length}</span>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Actions</span>
                <span className="font-medium">{workflow.actions.length}</span>
              </div>
            </div>

            <div className="mt-4 flex space-x-2">
              {workflow.status === 'ACTIVE' ? (
                <button className="flex-1 bg-yellow-600 text-white px-3 py-2 rounded-md hover:bg-yellow-700 text-sm flex items-center justify-center">
                  <Pause className="w-4 h-4 mr-1" />
                  Pause
                </button>
              ) : (
                <button className="flex-1 bg-green-600 text-white px-3 py-2 rounded-md hover:bg-green-700 text-sm flex items-center justify-center">
                  <Play className="w-4 h-4 mr-1" />
                  Start
                </button>
              )}
              
              <button className="px-3 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 text-sm">
                <Settings className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Executions */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Activity className="w-5 h-5 mr-2 text-purple-600" />
          Recent Executions
        </h3>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Workflow
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Started
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Results
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {executions.map((execution) => (
                <tr key={execution.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {workflows.find(w => w.id === execution.workflowId)?.name || 'Unknown'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getExecutionStatusColor(execution.status)}`}>
                      {execution.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {execution.duration ? formatDuration(execution.duration) : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(execution.startTime)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {execution.results.length} result{execution.results.length !== 1 ? 's' : ''}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Workflow Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Workflow</h3>
              <p className="text-sm text-gray-600 mb-4">
                This feature will be available in the next update. You can create workflows using the API or wait for the visual workflow builder.
              </p>
              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

