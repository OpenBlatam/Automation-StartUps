import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Select } from './ui/Select';
import { Textarea } from './ui/Textarea';
import { Badge } from './ui/Badge';
import { Loader } from './ui/Loader';
import { Alert } from './ui/Alert';
import { 
  Sparkles, 
  Copy, 
  Download, 
  RefreshCw, 
  Star,
  TrendingUp,
  Users,
  Target,
  Zap
} from 'lucide-react';

const TestimonialGenerator = ({ user, onTestimonialGenerated }) => {
  const [formData, setFormData] = useState({
    templateType: 'distinctiveQualities',
    productName: '',
    productCategory: '',
    targetAudience: '',
    keyBenefits: '',
    useCase: '',
    industry: '',
    tone: 'professional',
    length: 'medium',
    model: 'gpt-4',
    customPrompt: '',
    additionalContext: ''
  });

  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedTestimonial, setGeneratedTestimonial] = useState(null);
  const [error, setError] = useState(null);
  const [usage, setUsage] = useState(null);

  const templateOptions = [
    {
      value: 'distinctiveQualities',
      label: 'Distinctive Qualities',
      description: 'Highlight unique value propositions',
      icon: <Star className="w-4 h-4" />
    },
    {
      value: 'recommendation',
      label: 'Recommendation',
      description: 'Build trust and credibility',
      icon: <Users className="w-4 h-4" />
    },
    {
      value: 'specificSituation',
      label: 'Specific Situation',
      description: 'Demonstrate practical benefits',
      icon: <Target className="w-4 h-4" />
    },
    {
      value: 'investmentWorth',
      label: 'Investment Worth',
      description: 'Justify purchase decisions',
      icon: <TrendingUp className="w-4 h-4" />
    },
    {
      value: 'efficiencyImprovement',
      label: 'Efficiency Improvement',
      description: 'Show operational benefits',
      icon: <Zap className="w-4 h-4" />
    }
  ];

  const toneOptions = [
    { value: 'professional', label: 'Professional' },
    { value: 'casual', label: 'Casual' },
    { value: 'technical', label: 'Technical' },
    { value: 'emotional', label: 'Emotional' }
  ];

  const lengthOptions = [
    { value: 'short', label: 'Short (50-75 words)' },
    { value: 'medium', label: 'Medium (150-200 words)' },
    { value: 'long', label: 'Long (300+ words)' }
  ];

  const modelOptions = [
    { value: 'gpt-4', label: 'GPT-4 (OpenAI)' },
    { value: 'claude-3', label: 'Claude 3 (Anthropic)' },
    { value: 'gemini-pro', label: 'Gemini Pro (Google)' }
  ];

  useEffect(() => {
    // Load user's default preferences
    if (user?.preferences) {
      setFormData(prev => ({
        ...prev,
        tone: user.preferences.defaultTone || 'professional',
        length: user.preferences.defaultLength || 'medium',
        model: user.preferences.defaultModel || 'gpt-4'
      }));
    }
  }, [user]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setError(null);
  };

  const handleGenerate = async () => {
    if (!formData.productName.trim()) {
      setError('Product name is required');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const response = await fetch('/api/testimonials/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          ...formData,
          keyBenefits: formData.keyBenefits.split(',').map(b => b.trim()).filter(Boolean)
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to generate testimonial');
      }

      setGeneratedTestimonial(data.data);
      setUsage(data.usage);
      
      if (onTestimonialGenerated) {
        onTestimonialGenerated(data.data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRegenerate = async (model) => {
    if (!generatedTestimonial) return;

    setIsGenerating(true);
    setError(null);

    try {
      const response = await fetch(`/api/testimonials/${generatedTestimonial.id}/regenerate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          model: model || formData.model,
          options: {
            tone: formData.tone,
            length: formData.length
          }
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to regenerate testimonial');
      }

      setGeneratedTestimonial(data.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      // Show success toast
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const handleDownload = (content, filename) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          AI Testimonial Generator
        </h1>
        <p className="text-gray-600">
          Create compelling testimonials that convert with the power of AI
        </p>
      </div>

      {/* Usage Stats */}
      {usage && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <Badge variant="outline">
                  {usage.remaining} remaining this month
                </Badge>
                <span className="text-sm text-gray-500">
                  Resets on {new Date(usage.resetDate).toLocaleDateString()}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5" />
              <span>Generate Testimonial</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Template Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Testimonial Template
              </label>
              <div className="grid grid-cols-1 gap-2">
                {templateOptions.map((option) => (
                  <div
                    key={option.value}
                    className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                      formData.templateType === option.value
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleInputChange('templateType', option.value)}
                  >
                    <div className="flex items-center space-x-3">
                      {option.icon}
                      <div>
                        <div className="font-medium">{option.label}</div>
                        <div className="text-sm text-gray-500">{option.description}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Product Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Product/Service Name *
                </label>
                <Input
                  value={formData.productName}
                  onChange={(e) => handleInputChange('productName', e.target.value)}
                  placeholder="e.g., AI Marketing Platform"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Industry
                </label>
                <Input
                  value={formData.industry}
                  onChange={(e) => handleInputChange('industry', e.target.value)}
                  placeholder="e.g., Technology, Healthcare"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Target Audience
              </label>
              <Input
                value={formData.targetAudience}
                onChange={(e) => handleInputChange('targetAudience', e.target.value)}
                placeholder="e.g., Small business owners, Marketing professionals"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Key Benefits (comma-separated)
              </label>
              <Input
                value={formData.keyBenefits}
                onChange={(e) => handleInputChange('keyBenefits', e.target.value)}
                placeholder="e.g., Increased efficiency, Better ROI, Time savings"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Use Case/Situation
              </label>
              <Textarea
                value={formData.useCase}
                onChange={(e) => handleInputChange('useCase', e.target.value)}
                placeholder="Describe a specific situation where your product/service was useful..."
                rows={3}
              />
            </div>

            {/* Generation Options */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tone
                </label>
                <Select
                  value={formData.tone}
                  onValueChange={(value) => handleInputChange('tone', value)}
                  options={toneOptions}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Length
                </label>
                <Select
                  value={formData.length}
                  onValueChange={(value) => handleInputChange('length', value)}
                  options={lengthOptions}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  AI Model
                </label>
                <Select
                  value={formData.model}
                  onValueChange={(value) => handleInputChange('model', value)}
                  options={modelOptions}
                />
              </div>
            </div>

            {/* Additional Context */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Additional Context (Optional)
              </label>
              <Textarea
                value={formData.additionalContext}
                onChange={(e) => handleInputChange('additionalContext', e.target.value)}
                placeholder="Any additional information to include in the testimonial..."
                rows={2}
              />
            </div>

            {/* Error Display */}
            {error && (
              <Alert variant="destructive">
                {error}
              </Alert>
            )}

            {/* Generate Button */}
            <Button
              onClick={handleGenerate}
              disabled={isGenerating || !formData.productName.trim()}
              className="w-full"
              size="lg"
            >
              {isGenerating ? (
                <>
                  <Loader className="w-4 h-4 mr-2" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Generate Testimonial
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Generated Testimonial */}
        <Card>
          <CardHeader>
            <CardTitle>Generated Testimonial</CardTitle>
          </CardHeader>
          <CardContent>
            {generatedTestimonial ? (
              <div className="space-y-4">
                {/* Main Testimonial */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-start justify-between mb-2">
                    <Badge variant="secondary">
                      {generatedTestimonial.templateType}
                    </Badge>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">
                        Quality: {generatedTestimonial.metadata?.qualityScore || 0}/100
                      </Badge>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleCopy(generatedTestimonial.content)}
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDownload(
                          generatedTestimonial.content,
                          `testimonial-${generatedTestimonial.id}.txt`
                        )}
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  <p className="text-gray-800 leading-relaxed">
                    {generatedTestimonial.content}
                  </p>
                </div>

                {/* Alternatives */}
                {generatedTestimonial.alternatives && generatedTestimonial.alternatives.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-700 mb-2">Alternative Versions</h4>
                    <div className="space-y-3">
                      {generatedTestimonial.alternatives.map((alternative, index) => (
                        <div key={index} className="bg-white border p-3 rounded-lg">
                          <div className="flex items-start justify-between mb-2">
                            <Badge variant="outline">Version {index + 2}</Badge>
                            <div className="flex items-center space-x-1">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleCopy(alternative)}
                              >
                                <Copy className="w-3 h-3" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDownload(
                                  alternative,
                                  `testimonial-alternative-${index + 2}.txt`
                                )}
                              >
                                <Download className="w-3 h-3" />
                              </Button>
                            </div>
                          </div>
                          <p className="text-sm text-gray-700 leading-relaxed">
                            {alternative}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Regenerate Options */}
                <div className="border-t pt-4">
                  <h4 className="font-medium text-gray-700 mb-2">Regenerate with Different Model</h4>
                  <div className="flex flex-wrap gap-2">
                    {modelOptions.map((model) => (
                      <Button
                        key={model.value}
                        variant="outline"
                        size="sm"
                        onClick={() => handleRegenerate(model.value)}
                        disabled={isGenerating}
                      >
                        <RefreshCw className="w-3 h-3 mr-1" />
                        {model.label}
                      </Button>
                    ))}
                  </div>
                </div>

                {/* Metadata */}
                <div className="text-xs text-gray-500 space-y-1">
                  <div>Generated with: {generatedTestimonial.model}</div>
                  <div>Tokens used: {generatedTestimonial.metadata?.tokensUsed || 'N/A'}</div>
                  <div>Generation time: {generatedTestimonial.metadata?.generationTime || 'N/A'}ms</div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Generate your first testimonial to see it here</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default TestimonialGenerator;



