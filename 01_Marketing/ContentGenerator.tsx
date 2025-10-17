import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';
import { Wand2, Copy, Download, RefreshCw, Sparkles } from 'lucide-react';
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
}

interface GeneratedContent {
  id: string;
  content: string;
  tokensUsed: number;
  cost: number;
  createdAt: string;
}

const CONTENT_TYPES = [
  { value: 'BLOG_POST', label: 'Blog Post', icon: '📝' },
  { value: 'EMAIL', label: 'Email', icon: '📧' },
  { value: 'SOCIAL_MEDIA', label: 'Social Media', icon: '📱' },
  { value: 'AD_COPY', label: 'Ad Copy', icon: '📢' },
  { value: 'PRODUCT_DESCRIPTION', label: 'Product Description', icon: '🛍️' },
  { value: 'LANDING_PAGE', label: 'Landing Page', icon: '🌐' },
  { value: 'SALES_PAGE', label: 'Sales Page', icon: '💰' },
  { value: 'EMAIL_SEQUENCE', label: 'Email Sequence', icon: '📬' },
  { value: 'WEBSITE_COPY', label: 'Website Copy', icon: '🏠' },
  { value: 'OTHER', label: 'Other', icon: '✨' },
];

const TONE_OPTIONS = [
  'Professional', 'Casual', 'Friendly', 'Authoritative', 'Conversational',
  'Persuasive', 'Informative', 'Humorous', 'Serious', 'Enthusiastic'
];

const LENGTH_OPTIONS = [
  { value: 'short', label: 'Short (50-100 words)' },
  { value: 'medium', label: 'Medium (200-400 words)' },
  { value: 'long', label: 'Long (500+ words)' },
];

export const ContentGenerator: React.FC = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const { register, handleSubmit, formState: { errors }, reset, watch } = useForm<ContentFormData>({
    defaultValues: {
      type: 'BLOG_POST',
      tone: 'Professional',
      length: 'medium',
    }
  });

  const selectedType = watch('type');

  const onSubmit = async (data: ContentFormData) => {
    setIsGenerating(true);
    try {
      const keywords = data.keywords ? data.keywords.split(',').map(k => k.trim()) : [];
      
      const result = await contentService.generateContent({
        ...data,
        keywords,
      });

      setGeneratedContent(prev => [result, ...prev]);
      toast.success('Content generated successfully!');
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
      
      const results = await contentService.generateVariations({
        ...data,
        keywords,
      }, 3);

      setGeneratedContent(prev => [...results, ...prev]);
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
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Content Generator</h1>
        <p className="text-gray-600">
          Create high-quality marketing content with AI. Choose your content type and let our AI generate compelling copy for you.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form Section */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
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
                        ? 'border-blue-500 bg-blue-50'
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
                What would you like to write about?
              </label>
              <textarea
                {...register('prompt', { required: 'Prompt is required' })}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Describe what you want to write about. Be specific about your topic, key points, and any particular angle you want to take..."
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
                className="flex items-center text-sm text-blue-600 hover:text-blue-700"
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isGenerating ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Wand2 className="w-4 h-4 mr-2" />
                    Generate Content
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={handleSubmit(generateVariations)}
                disabled={isGenerating}
                className="px-4 py-2 border border-blue-600 text-blue-600 rounded-md hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
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
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
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
              <Wand2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Ready to Generate Content
              </h3>
              <p className="text-gray-600">
                Fill out the form and click "Generate Content" to create your first piece of AI-generated content.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

