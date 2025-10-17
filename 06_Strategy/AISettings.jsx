import React from 'react';
import { motion } from 'framer-motion';
import { 
  Brain, 
  Thermometer, 
  Hash, 
  Zap, 
  Info,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

const AISettings = ({ settings, onChange, showAdvanced = false }) => {
  const models = [
    {
      id: 'gpt-3.5-turbo',
      name: 'GPT-3.5 Turbo',
      description: 'Fast and cost-effective for most tasks',
      cost: '$0.002/1K tokens',
      maxTokens: 4096,
      speed: 'Fast',
      quality: 'Good'
    },
    {
      id: 'gpt-4',
      name: 'GPT-4',
      description: 'High-quality responses for complex tasks',
      cost: '$0.03/1K tokens',
      maxTokens: 8192,
      speed: 'Medium',
      quality: 'Excellent'
    },
    {
      id: 'gpt-4-turbo',
      name: 'GPT-4 Turbo',
      description: 'Latest model with improved capabilities',
      cost: '$0.01/1K tokens',
      maxTokens: 128000,
      speed: 'Fast',
      quality: 'Excellent'
    },
    {
      id: 'claude-3-sonnet',
      name: 'Claude 3 Sonnet',
      description: 'Balanced performance and reasoning',
      cost: '$0.015/1K tokens',
      maxTokens: 200000,
      speed: 'Medium',
      quality: 'Excellent'
    },
    {
      id: 'claude-3-opus',
      name: 'Claude 3 Opus',
      description: 'Most capable model for complex tasks',
      cost: '$0.075/1K tokens',
      maxTokens: 200000,
      speed: 'Slow',
      quality: 'Outstanding'
    }
  ];

  const selectedModel = models.find(m => m.id === settings.model);

  const handleSettingChange = (key, value) => {
    onChange({
      ...settings,
      [key]: value
    });
  };

  const getTemperatureLabel = (temp) => {
    if (temp <= 0.3) return 'Focused';
    if (temp <= 0.7) return 'Balanced';
    if (temp <= 1.0) return 'Creative';
    return 'Very Creative';
  };

  const getTemperatureColor = (temp) => {
    if (temp <= 0.3) return 'text-blue-600';
    if (temp <= 0.7) return 'text-green-600';
    if (temp <= 1.0) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Model Selection */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          <Brain className="w-4 h-4 inline mr-2" />
          AI Model
        </label>
        
        <div className="grid grid-cols-1 gap-3">
          {models.map((model) => (
            <motion.div
              key={model.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleSettingChange('model', model.id)}
              className={`p-4 border rounded-lg cursor-pointer transition-all duration-200 ${
                settings.model === model.id
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-300 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-700'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {model.name}
                    </h4>
                    {settings.model === model.id && (
                      <div className="ml-2 w-2 h-2 bg-blue-500 rounded-full"></div>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {model.description}
                  </p>
                  <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                    <span>Cost: {model.cost}</span>
                    <span>Speed: {model.speed}</span>
                    <span>Quality: {model.quality}</span>
                    <span>Max: {model.maxTokens.toLocaleString()} tokens</span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Temperature */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            <Thermometer className="w-4 h-4 inline mr-2" />
            Creativity Level
          </label>
          <span className={`text-sm font-medium ${getTemperatureColor(settings.temperature)}`}>
            {getTemperatureLabel(settings.temperature)}
          </span>
        </div>
        
        <div className="space-y-2">
          <input
            type="range"
            min="0"
            max="2"
            step="0.1"
            value={settings.temperature}
            onChange={(e) => handleSettingChange('temperature', parseFloat(e.target.value))}
            className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
          />
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>Focused (0.0)</span>
            <span>Balanced (0.7)</span>
            <span>Creative (1.0)</span>
            <span>Very Creative (2.0)</span>
          </div>
        </div>
        
        <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div className="flex items-start">
            <Info className="w-4 h-4 text-blue-500 mt-0.5 mr-2 flex-shrink-0" />
            <div className="text-sm text-gray-600 dark:text-gray-400">
              <p className="font-medium mb-1">Temperature Guide:</p>
              <ul className="space-y-1 text-xs">
                <li>• <strong>0.0-0.3:</strong> Consistent, factual content</li>
                <li>• <strong>0.4-0.7:</strong> Balanced creativity and consistency</li>
                <li>• <strong>0.8-1.0:</strong> More creative and varied</li>
                <li>• <strong>1.1-2.0:</strong> Highly creative, experimental</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Max Tokens */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          <Hash className="w-4 h-4 inline mr-2" />
          Maximum Length
        </label>
        
        <div className="space-y-2">
          <input
            type="range"
            min="50"
            max={selectedModel?.maxTokens || 4000}
            step="50"
            value={settings.maxTokens}
            onChange={(e) => handleSettingChange('maxTokens', parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
          />
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>Short (50)</span>
            <span>Medium (500)</span>
            <span>Long (1000)</span>
            <span>Very Long ({selectedModel?.maxTokens || 4000})</span>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600 dark:text-gray-400">
            Current: {settings.maxTokens} tokens
          </span>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            ≈ {Math.round(settings.maxTokens / 4)} words
          </span>
        </div>
      </div>

      {/* Advanced Settings */}
      {showAdvanced && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="space-y-4 pt-4 border-t border-gray-200 dark:border-gray-700"
        >
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center">
            <Zap className="w-4 h-4 mr-2" />
            Advanced Settings
          </h4>
          
          {/* Top P */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Top P (Nucleus Sampling)
            </label>
            <input
              type="range"
              min="0.1"
              max="1.0"
              step="0.1"
              value={settings.topP || 1.0}
              onChange={(e) => handleSettingChange('topP', parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
            <div className="text-xs text-gray-500 dark:text-gray-400">
              Controls diversity: 0.1 (focused) to 1.0 (diverse)
            </div>
          </div>

          {/* Frequency Penalty */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Frequency Penalty
            </label>
            <input
              type="range"
              min="-2.0"
              max="2.0"
              step="0.1"
              value={settings.frequencyPenalty || 0}
              onChange={(e) => handleSettingChange('frequencyPenalty', parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
            <div className="text-xs text-gray-500 dark:text-gray-400">
              Reduces repetition: -2.0 (more repetition) to 2.0 (less repetition)
            </div>
          </div>

          {/* Presence Penalty */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Presence Penalty
            </label>
            <input
              type="range"
              min="-2.0"
              max="2.0"
              step="0.1"
              value={settings.presencePenalty || 0}
              onChange={(e) => handleSettingChange('presencePenalty', parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
            <div className="text-xs text-gray-500 dark:text-gray-400">
              Encourages new topics: -2.0 (stay on topic) to 2.0 (explore new topics)
            </div>
          </div>
        </motion.div>
      )}

      {/* Cost Estimate */}
      <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
        <h4 className="text-sm font-medium text-green-900 dark:text-green-300 mb-2">
          Estimated Cost
        </h4>
        <div className="text-sm text-green-700 dark:text-green-400">
          <p>Model: {selectedModel?.name}</p>
          <p>Cost per 1K tokens: {selectedModel?.cost}</p>
          <p>Max cost per generation: ~${((settings.maxTokens / 1000) * parseFloat(selectedModel?.cost.replace('$', '') || 0)).toFixed(4)}</p>
        </div>
      </div>
    </div>
  );
};

export default AISettings;









