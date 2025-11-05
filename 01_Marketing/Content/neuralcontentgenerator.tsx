import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';
import { 
  Brain, 
  Copy, 
  Download, 
  RefreshCw, 
  Sparkles, 
  Zap, 
  Target,
  TrendingUp,
  Wand2
} from 'lucide-react';
import { consciousnessService } from '../services/consciousnessService';
import { contentService } from '../services/contentService';
import { ContentType } from '../types/content';

interface ContentFormData {
  type: ContentType;
  prompt: string;
  tone?: string;
  length?: string;
  targetAudience?: string;
  brandVoice?: string;
  keywords?: string;
  consciousnessMode?: boolean;
}

interface GeneratedContent {
  id: string;
  content: string;
  tokensUsed: number;
  cost: number;
  createdAt: string;
  consciousnessLevel?: number;
  category?: string;
}

interface ConsciousnessInsights {
  currentLevel: number;
  category: string;
  levelLabel: string;
  progress: any;
}

const CONTENT_TYPES = [
  { value: 'BLOG_POST', label: 'Blog Post', icon: '📝', consciousness: true },
  { value: 'EMAIL', label: 'Email', icon: '📧', consciousness: true },
  { value: 'SOCIAL_MEDIA', label: 'Social Media', icon: '📱', consciousness: true },
  { value: 'AD_COPY', label: 'Ad Copy', icon: '📢', consciousness: true },
  { value: 'PRODUCT_DESCRIPTION', label: 'Product Description', icon: '🛍️', consciousness: true },
  { value: 'LANDING_PAGE', label: 'Landing Page', icon: '🌐', consciousness: true },
  { value: 'SALES_PAGE', label: 'Sales Page', icon: '💰', consciousness: true },
  { value: 'EMAIL_SEQUENCE', label: 'Email Sequence', icon: '📬', consciousness: true },
  { value: 'WEBSITE_COPY', label: 'Website Copy', icon: '🏠', consciousness: true },
  { value: 'OTHER', label: 'Other', icon: '✨', consciousness: true },
];

const TONE_OPTIONS = [
  'Professional', 'Casual', 'Friendly', 'Authoritative', 'Conversational',
  'Persuasive', 'Informative', 'Humorous', 'Serious', 'Enthusiastic',
  'Neural', 'Conscious', 'Strategic', 'Revolutionary'
];

const LENGTH_OPTIONS = [
  { value: 'short', label: 'Short (50-100 words)' },
  { value: 'medium', label: 'Medium (200-400 words)' },
  { value: 'long', label: 'Long (500+ words)' },
  { value: 'neural', label: 'Neural (Adaptive length)' },
];

export const NeuralContentGenerator: React.FC = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [consciousnessInsights, setConsciousnessInsights] = useState<ConsciousnessInsights | null>(null);
  const [isLoadingInsights, setIsLoadingInsights] = useState(true);

  const { register, handleSubmit, formState: { errors }, reset, watch } = useForm<ContentFormData>({
    defaultValues: {
      type: 'BLOG_POST',
      tone: 'Professional',
      length: 'medium',
      consciousnessMode: true,
    }
  });

  const selectedType = watch('type');
  const consciousnessMode = watch('consciousnessMode');

  useEffect(() => {
    loadConsciousnessInsights();
  }, []);

  const loadConsciousnessInsights = async () => {
    try {
      setIsLoadingInsights(true);
      const data = await consciousnessService.getInsights();
      setConsciousnessInsights(data.insights);
    } catch (error) {
      console.error('Error loading consciousness insights:', error);
    } finally {
      setIsLoadingInsights(false);
    }
  };

  const onSubmit = async (data: ContentFormData) => {
    setIsGenerating(true);
    try {
      let result: GeneratedContent;

      if (data.consciousnessMode && consciousnessInsights) {
        // Use consciousness-based generation
        const consciousnessResult = await consciousnessService.generateConsciousnessContent({
          contentType: data.type,
          prompt: data.prompt,
        });

        result = {
          id: Date.now().toString(),
          content: consciousnessResult.content,
          tokensUsed: 0, // Would be provided by the API
          cost: 0, // Would be provided by the API
          createdAt: new Date().toISOString(),
          consciousnessLevel: consciousnessInsights.currentLevel,
          category: consciousnessInsights.category,
        };
      } else {
        // Use regular content generation
        const keywords = data.keywords ? data.keywords.split(',').map(k => k.trim()) : [];
        
        const regularResult = await contentService.generateContent({
          ...data,
          keywords,
        });

        result = {
          id: regularResult.id,
          content: regularResult.content,
          tokensUsed: regularResult.tokensUsed,
          cost: regularResult.cost,
          createdAt: regularResult.createdAt,
        };
      }

      setGeneratedContent(prev => [result, ...prev]);
      toast.success(consciousnessMode ? 'Neural content generated!' : 'Content generated successfully!');
    } catch (error) {
      console.error('Error generating content:', error);
      toast.error('Failed to generate content. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const generateVariations = async (data: ContentFormData) => {
    setIsGenerating(true);
    try {
      const keywords = data.keywords ? data.keywords.split(',').map(k => k.trim()) : [];
      
      if (data.consciousnessMode && consciousnessInsights) {
        // Generate consciousness-based variations
        const variations = [];
        for (let i = 0; i < 3; i++) {
          const variation = await consciousnessService.generateConsciousnessContent({
            contentType: data.type,
            prompt: `${data.prompt}\n\nGenerate variation ${i + 1} with a different approach.`,
          });
          
          variations.push({
            id: Date.now().toString() + i,
            content: variation.content,
            tokensUsed: 0,
            cost: 0,
            createdAt: new Date().toISOString(),
            consciousnessLevel: consciousnessInsights.currentLevel,
            category: consciousnessInsights.category,
          });
        }
        setGeneratedContent(prev => [...variations, ...prev]);
      } else {
        // Generate regular variations
        const results = await contentService.generateVariations({
          ...data,
          keywords,
        }, 3);

        const variations = results.map((result, index) => ({
          id: result.id,
          content: result.content,
          tokensUsed: result.tokensUsed,
          cost: result.cost,
          createdAt: result.createdAt,
        }));

        setGeneratedContent(prev => [...variations, ...prev]);
      }

      toast.success('Generated 3 variations!');
    } catch (error) {
      console.error('Error generating variations:', error);
      toast.error('Failed to generate variations. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = (content: string) => {
    navigator.clipboard.writeText(content);
    toast.success('Copied to clipboard!');
  };

  const downloadContent = (content: string, type: string) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${type.toLowerCase().replace('_', '-')}-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Content downloaded!');
  };

  const selectedTypeInfo = CONTENT_TYPES.find(type => type.value === selectedType);

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
              <Brain className="w-8 h-8 mr-3 text-purple-600" />
              Neural Content Generator
            </h1>
            <p className="text-gray-600">
              Generate AI-powered content that adapts to your Neural Marketing Consciousness level
            </p>
          </div>
          
          {/* Consciousness Level Indicator */}
          {consciousnessInsights && (
            <div className="text-right">
              <div className="text-sm text-gray-600">Consciousness Level</div>
              <div className="text-2xl font-bold text-purple-600">
                {consciousnessInsights.currentLevel}
              </div>
              <div className="text-sm text-gray-500">
                {consciousnessInsights.levelLabel}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form Section */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Consciousness Mode Toggle */}
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Brain className="w-5 h-5 text-purple-600 mr-2" />
                  <span className="font-medium text-purple-900">Neural Mode</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    {...register('consciousnessMode')}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
              </div>
              <p className="text-sm text-purple-700 mt-2">
                {consciousnessMode 
                  ? 'Content will be generated based on your consciousness level and neural profile'
                  : 'Standard AI content generation'
                }
              </p>
            </div>

            {/* Content Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Content Type
              </label>
              <div className="grid grid-cols-2 gap-2">
                {CONTENT_TYPES.map((type) => (
                  <label
                    key={type.value}
                    className={`relative flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedType === type.value
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      value={type.value}
                      {...register('type', { required: true })}
                      className="sr-only"
                    />
                    <span className="text-lg mr-2">{type.icon}</span>
                    <span className="text-sm font-medium">{type.label}</span>
                    {type.consciousness && (
                      <Brain className="w-3 h-3 text-purple-500 ml-auto" />
                    )}
                  </label>
                ))}
              </div>
              {errors.type && (
                <p className="mt-1 text-sm text-red-600">Please select a content type</p>
              )}
            </div>

            {/* Prompt */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                What would you like to create?
              </label>
              <textarea
                {...register('prompt', { required: 'Prompt is required' })}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="Describe what you want to create. Be specific about your topic, key points, and any particular angle you want to take..."
              />
              {errors.prompt && (
                <p className="mt-1 text-sm text-red-600">{errors.prompt.message}</p>
              )}
            </div>

            {/* Advanced Options Toggle */}
            <div>
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center text-sm text-purple-600 hover:text-purple-700"
              >
                <Sparkles className="w-4 h-4 mr-1" />
                {showAdvanced ? 'Hide' : 'Show'} Advanced Options
              </button>
            </div>

            {/* Advanced Options */}
            {showAdvanced && (
              <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
                {/* Tone */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tone
                  </label>
                  <select
                    {...register('tone')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    {TONE_OPTIONS.map((tone) => (
                      <option key={tone} value={tone}>
                        {tone}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Length */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Length
                  </label>
                  <select
                    {...register('length')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    {LENGTH_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Target Audience */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Audience
                  </label>
                  <input
                    type="text"
                    {...register('targetAudience')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="e.g., Small business owners, Tech professionals, Millennials"
                  />
                </div>

                {/* Brand Voice */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Brand Voice
                  </label>
                  <input
                    type="text"
                    {...register('brandVoice')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="e.g., Professional yet approachable, Innovative and cutting-edge"
                  />
                </div>

                {/* Keywords */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Keywords (comma-separated)
                  </label>
                  <input
                    type="text"
                    {...register('keywords')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="e.g., AI, marketing, automation, growth"
                  />
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={isGenerating}
                className="flex-1 bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isGenerating ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    {consciousnessMode ? (
                      <>
                        <Brain className="w-4 h-4 mr-2" />
                        Generate Neural Content
                      </>
                    ) : (
                      <>
                        <Wand2 className="w-4 h-4 mr-2" />
                        Generate Content
                      </>
                    )}
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={handleSubmit(generateVariations)}
                disabled={isGenerating}
                className="px-4 py-2 border border-purple-600 text-purple-600 rounded-md hover:bg-purple-50 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </form>
        </div>

        {/* Generated Content Section */}
        <div className="space-y-6">
          {generatedContent.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Zap className="w-5 h-5 mr-2 text-purple-600" />
                Generated Content
              </h2>
              <div className="space-y-4">
                {generatedContent.map((content, index) => (
                  <div key={content.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-600">
                          {selectedTypeInfo?.label} #{index + 1}
                        </span>
                        {content.consciousnessLevel && (
                          <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                            Level {content.consciousnessLevel}
                          </span>
                        )}
                        <span className="text-xs text-gray-500">
                          {content.tokensUsed} tokens • ${content.cost.toFixed(4)}
                        </span>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => copyToClipboard(content.content)}
                          className="p-1 text-gray-400 hover:text-gray-600"
                          title="Copy to clipboard"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => downloadContent(content.content, selectedType)}
                          className="p-1 text-gray-400 hover:text-gray-600"
                          title="Download"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <div className="prose prose-sm max-w-none">
                      <p className="whitespace-pre-wrap text-gray-700">
                        {content.content}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {generatedContent.length === 0 && (
            <div className="bg-white rounded-lg shadow-sm border p-6 text-center">
              <Brain className="w-12 h-12 text-purple-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Ready to Generate Neural Content
              </h3>
              <p className="text-gray-600">
                {consciousnessMode 
                  ? 'Enable Neural Mode and create content that adapts to your consciousness level.'
                  : 'Fill out the form and click "Generate Content" to create your first piece of AI-generated content.'
                }
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

