import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Wand2, 
  Copy, 
  Download, 
  Star, 
  RefreshCw, 
  Settings, 
  Lightbulb,
  TrendingUp,
  Target,
  Users,
  FileText,
  Sparkles,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

// Components
import TemplateSelector from '../components/content/TemplateSelector';
import VariableInputs from '../components/content/VariableInputs';
import AISettings from '../components/content/AISettings';
import ContentPreview from '../components/content/ContentPreview';
import ContentHistory from '../components/content/ContentHistory';
import UsageStats from '../components/content/UsageStats';

const ContentGenerator = () => {
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [variables, setVariables] = useState({});
  const [customPrompt, setCustomPrompt] = useState('');
  const [aiSettings, setAiSettings] = useState({
    model: 'gpt-3.5-turbo',
    temperature: 0.7,
    maxTokens: 500
  });
  const [generatedContent, setGeneratedContent] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [activeTab, setActiveTab] = useState('generate');

  const queryClient = useQueryClient();

  // Fetch templates
  const { data: templates, isLoading: templatesLoading } = useQuery(
    'templates',
    async () => {
      const response = await axios.get('/api/templates');
      return response.data.data;
    }
  );

  // Fetch user usage stats
  const { data: usageStats } = useQuery(
    'usageStats',
    async () => {
      const response = await axios.get('/api/users/usage');
      return response.data.data;
    }
  );

  // Content generation mutation
  const generateContentMutation = useMutation(
    async (data) => {
      const response = await axios.post('/api/content/generate', data);
      return response.data;
    },
    {
      onSuccess: (data) => {
        setGeneratedContent(data.data.content);
        toast.success('Content generated successfully!');
        queryClient.invalidateQueries('contentHistory');
        queryClient.invalidateQueries('usageStats');
      },
      onError: (error) => {
        toast.error(error.response?.data?.message || 'Failed to generate content');
      }
    }
  );

  // Generate variations mutation
  const generateVariationsMutation = useMutation(
    async (data) => {
      const response = await axios.post('/api/content/generate-variations', data);
      return response.data;
    },
    {
      onSuccess: (data) => {
        toast.success(`Generated ${data.data.count} variations!`);
        queryClient.invalidateQueries('contentHistory');
      },
      onError: (error) => {
        toast.error(error.response?.data?.message || 'Failed to generate variations');
      }
    }
  );

  // Optimize content mutation
  const optimizeContentMutation = useMutation(
    async (data) => {
      const response = await axios.post('/api/content/optimize', data);
      return response.data;
    },
    {
      onSuccess: (data) => {
        setGeneratedContent(data.data.optimizedContent);
        toast.success('Content optimized successfully!');
      },
      onError: (error) => {
        toast.error(error.response?.data?.message || 'Failed to optimize content');
      }
    }
  );

  // Handle template selection
  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template);
    setVariables({});
    setCustomPrompt('');
  };

  // Handle variable change
  const handleVariableChange = (name, value) => {
    setVariables(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Generate content
  const handleGenerate = async () => {
    if (!selectedTemplate && !customPrompt.trim()) {
      toast.error('Please select a template or enter a custom prompt');
      return;
    }

    const data = {
      templateId: selectedTemplate?._id,
      prompt: customPrompt,
      variables,
      ...aiSettings
    };

    setIsGenerating(true);
    try {
      await generateContentMutation.mutateAsync(data);
    } finally {
      setIsGenerating(false);
    }
  };

  // Generate variations
  const handleGenerateVariations = async () => {
    if (!selectedTemplate && !customPrompt.trim()) {
      toast.error('Please select a template or enter a custom prompt');
      return;
    }

    const data = {
      templateId: selectedTemplate?._id,
      prompt: customPrompt,
      variables,
      count: 3,
      ...aiSettings
    };

    await generateVariationsMutation.mutateAsync(data);
  };

  // Optimize content
  const handleOptimize = async (goal) => {
    if (!generatedContent.trim()) {
      toast.error('Please generate content first');
      return;
    }

    await optimizeContentMutation.mutateAsync({
      content: generatedContent,
      goal,
      model: aiSettings.model
    });
  };

  // Copy to clipboard
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(generatedContent);
      toast.success('Content copied to clipboard!');
    } catch (error) {
      toast.error('Failed to copy content');
    }
  };

  // Download content
  const handleDownload = () => {
    const blob = new Blob([generatedContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai-content-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Content downloaded!');
  };

  const tabs = [
    { id: 'generate', label: 'Generate', icon: Wand2 },
    { id: 'templates', label: 'Templates', icon: FileText },
    { id: 'history', label: 'History', icon: Clock },
    { id: 'analytics', label: 'Analytics', icon: TrendingUp }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            AI Content Generator
          </h1>
          <p className="text-gray-600 dark:text-gray-300 text-lg max-w-2xl mx-auto">
            Create compelling marketing content with the power of artificial intelligence. 
            Choose from professional templates or create custom prompts.
          </p>
        </motion.div>

        {/* Usage Stats */}
        {usageStats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <UsageStats stats={usageStats} />
          </motion.div>
        )}

        {/* Tabs */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex justify-center mb-8"
        >
          <div className="bg-white dark:bg-gray-800 rounded-lg p-1 shadow-lg">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-6 py-3 rounded-md transition-all duration-200 ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                      : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </motion.div>

        {/* Main Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'generate' && (
            <motion.div
              key="generate"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-8"
            >
              {/* Left Panel - Input */}
              <div className="space-y-6">
                {/* Template Selection */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                  <h3 className="text-xl font-semibold mb-4 flex items-center">
                    <FileText className="w-5 h-5 mr-2 text-blue-500" />
                    Template Selection
                  </h3>
                  
                  {templatesLoading ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
                    </div>
                  ) : (
                    <TemplateSelector
                      templates={templates}
                      selectedTemplate={selectedTemplate}
                      onSelect={handleTemplateSelect}
                    />
                  )}
                </div>

                {/* Custom Prompt */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                  <h3 className="text-xl font-semibold mb-4 flex items-center">
                    <Lightbulb className="w-5 h-5 mr-2 text-yellow-500" />
                    Custom Prompt
                  </h3>
                  <textarea
                    value={customPrompt}
                    onChange={(e) => setCustomPrompt(e.target.value)}
                    placeholder="Enter your custom prompt here..."
                    className="w-full h-32 p-4 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  />
                </div>

                {/* Variables */}
                {selectedTemplate && selectedTemplate.variables.length > 0 && (
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                    <h3 className="text-xl font-semibold mb-4 flex items-center">
                      <Target className="w-5 h-5 mr-2 text-green-500" />
                      Template Variables
                    </h3>
                    <VariableInputs
                      variables={selectedTemplate.variables}
                      values={variables}
                      onChange={handleVariableChange}
                    />
                  </div>
                )}

                {/* AI Settings */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold flex items-center">
                      <Settings className="w-5 h-5 mr-2 text-purple-500" />
                      AI Settings
                    </h3>
                    <button
                      onClick={() => setShowSettings(!showSettings)}
                      className="text-sm text-blue-500 hover:text-blue-600"
                    >
                      {showSettings ? 'Hide' : 'Show'} Advanced
                    </button>
                  </div>
                  
                  <AISettings
                    settings={aiSettings}
                    onChange={setAiSettings}
                    showAdvanced={showSettings}
                  />
                </div>

                {/* Generate Buttons */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                  <div className="flex flex-col sm:flex-row gap-4">
                    <button
                      onClick={handleGenerate}
                      disabled={isGenerating}
                      className="flex-1 bg-gradient-to-r from-blue-500 to-purple-500 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-600 hover:to-purple-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                    >
                      {isGenerating ? (
                        <>
                          <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                          Generating...
                        </>
                      ) : (
                        <>
                          <Wand2 className="w-5 h-5 mr-2" />
                          Generate Content
                        </>
                      )}
                    </button>
                    
                    <button
                      onClick={handleGenerateVariations}
                      disabled={isGenerating}
                      className="flex-1 bg-gradient-to-r from-green-500 to-teal-500 text-white py-3 px-6 rounded-lg font-semibold hover:from-green-600 hover:to-teal-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                    >
                      <RefreshCw className="w-5 h-5 mr-2" />
                      Generate Variations
                    </button>
                  </div>
                </div>
              </div>

              {/* Right Panel - Output */}
              <div className="space-y-6">
                {/* Generated Content */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold flex items-center">
                      <Sparkles className="w-5 h-5 mr-2 text-yellow-500" />
                      Generated Content
                    </h3>
                    
                    {generatedContent && (
                      <div className="flex gap-2">
                        <button
                          onClick={handleCopy}
                          className="p-2 text-gray-500 hover:text-blue-500 transition-colors"
                          title="Copy to clipboard"
                        >
                          <Copy className="w-5 h-5" />
                        </button>
                        <button
                          onClick={handleDownload}
                          className="p-2 text-gray-500 hover:text-green-500 transition-colors"
                          title="Download content"
                        >
                          <Download className="w-5 h-5" />
                        </button>
                      </div>
                    )}
                  </div>
                  
                  <ContentPreview content={generatedContent} />
                </div>

                {/* Optimization Tools */}
                {generatedContent && (
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                    <h3 className="text-xl font-semibold mb-4 flex items-center">
                      <TrendingUp className="w-5 h-5 mr-2 text-orange-500" />
                      Optimize Content
                    </h3>
                    
                    <div className="grid grid-cols-2 gap-3">
                      {[
                        { goal: 'seo', label: 'SEO', icon: Target },
                        { goal: 'conversion', label: 'Conversion', icon: TrendingUp },
                        { goal: 'engagement', label: 'Engagement', icon: Users },
                        { goal: 'clarity', label: 'Clarity', icon: FileText }
                      ].map(({ goal, label, icon: Icon }) => (
                        <button
                          key={goal}
                          onClick={() => handleOptimize(goal)}
                          disabled={optimizeContentMutation.isLoading}
                          className="flex items-center justify-center p-3 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
                        >
                          <Icon className="w-4 h-4 mr-2" />
                          {label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Quick Actions */}
                {generatedContent && (
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                    <h3 className="text-xl font-semibold mb-4 flex items-center">
                      <Star className="w-5 h-5 mr-2 text-yellow-500" />
                      Quick Actions
                    </h3>
                    
                    <div className="space-y-3">
                      <button className="w-full flex items-center justify-center p-3 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors">
                        <CheckCircle className="w-5 h-5 mr-2" />
                        Save to Favorites
                      </button>
                      <button className="w-full flex items-center justify-center p-3 bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors">
                        <FileText className="w-5 h-5 mr-2" />
                        Create Campaign
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {activeTab === 'templates' && (
            <motion.div
              key="templates"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
            >
              <TemplateSelector
                templates={templates}
                selectedTemplate={selectedTemplate}
                onSelect={handleTemplateSelect}
                showAll={true}
              />
            </motion.div>
          )}

          {activeTab === 'history' && (
            <motion.div
              key="history"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
            >
              <ContentHistory />
            </motion.div>
          )}

          {activeTab === 'analytics' && (
            <motion.div
              key="analytics"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
            >
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h3 className="text-xl font-semibold mb-4">Content Analytics</h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Analytics dashboard coming soon...
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default ContentGenerator;