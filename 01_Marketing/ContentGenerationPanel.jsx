import React, { useState } from 'react';
import './ContentGenerationPanel.css';

const ContentGenerationPanel = () => {
  const [contentType, setContentType] = useState('blog-post');
  const [templateType, setTemplateType] = useState('industry-analysis');
  const [prompt, setPrompt] = useState('');
  const [generatedContent, setGeneratedContent] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [contentHistory, setContentHistory] = useState([]);

  const contentTypes = {
    'blog-post': { name: 'Blog Post', icon: '📝' },
    'article': { name: 'Article', icon: '📰' },
    'social-media': { name: 'Social Media', icon: '📱' },
    'email': { name: 'Email', icon: '📧' },
    'ad-copy': { name: 'Ad Copy', icon: '📢' },
    'product-description': { name: 'Product Description', icon: '🛍️' }
  };

  const templateTypes = {
    'thought-leadership': {
      'industry-analysis': 'Industry Analysis',
      'trend-prediction': 'Trend Prediction',
      'expert-opinion': 'Expert Opinion',
      'case-study': 'Case Study'
    },
    'marketing-copy': {
      'product-description': 'Product Description',
      'email-subject': 'Email Subject Lines',
      'social-media': 'Social Media Posts',
      'ad-copy': 'Ad Copy'
    },
    'business-content': {
      'sales-proposal': 'Sales Proposal',
      'pitch-deck': 'Pitch Deck',
      'white-paper': 'White Paper',
      'case-study': 'Case Study'
    }
  };

  const generateContent = async () => {
    if (!prompt.trim()) {
      alert('Please enter a prompt');
      return;
    }

    setIsGenerating(true);
    
    try {
      const response = await fetch('/api/content/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          type: contentType,
          params: {
            prompt: prompt,
            target_audience: 'marketing professionals',
            tone: 'professional'
          }
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setGeneratedContent(data.data.content);
        
        // Add to history
        setContentHistory(prev => [{
          id: Date.now(),
          type: contentType,
          prompt: prompt,
          content: data.data.content,
          timestamp: new Date().toISOString()
        }, ...prev.slice(0, 9)]); // Keep last 10 items
      } else {
        alert('Error generating content: ' + data.error);
      }
    } catch (error) {
      console.error('Error generating content:', error);
      alert('Error generating content');
    } finally {
      setIsGenerating(false);
    }
  };

  const generateThoughtLeadership = async () => {
    if (!prompt.trim()) {
      alert('Please enter a prompt');
      return;
    }

    setIsGenerating(true);
    
    try {
      const response = await fetch('/api/content/thought-leadership', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          templateType: templateType,
          params: {
            'industry/niche': 'AI Marketing',
            'topic/issue': prompt,
            'target audience': 'marketing professionals',
            'professional': 'AI Marketing Expert',
            'field': 'Digital Marketing'
          }
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setGeneratedContent(data.data.content);
        
        // Add to history
        setContentHistory(prev => [{
          id: Date.now(),
          type: 'thought-leadership',
          prompt: prompt,
          content: data.data.content,
          timestamp: new Date().toISOString()
        }, ...prev.slice(0, 9)]);
      } else {
        alert('Error generating thought leadership content: ' + data.error);
      }
    } catch (error) {
      console.error('Error generating thought leadership content:', error);
      alert('Error generating thought leadership content');
    } finally {
      setIsGenerating(false);
    }
  };

  const generateVariations = async () => {
    if (!prompt.trim()) {
      alert('Please enter a prompt');
      return;
    }

    setIsGenerating(true);
    
    try {
      const response = await fetch('/api/content/variations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          type: contentType,
          params: {
            prompt: prompt,
            target_audience: 'marketing professionals',
            tone: 'professional'
          },
          count: 3
        })
      });

      const data = await response.json();
      
      if (data.success) {
        const variations = data.data.variations.map((variation, index) => ({
          id: Date.now() + index,
          type: contentType,
          prompt: prompt,
          content: variation.content,
          timestamp: new Date().toISOString(),
          variation: index + 1
        }));
        
        setContentHistory(prev => [...variations, ...prev.slice(0, 7)]); // Keep last 10 items
        setGeneratedContent(variations[0].content); // Show first variation
      } else {
        alert('Error generating variations: ' + data.error);
      }
    } catch (error) {
      console.error('Error generating variations:', error);
      alert('Error generating variations');
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = (content) => {
    navigator.clipboard.writeText(content);
    alert('Content copied to clipboard!');
  };

  const clearContent = () => {
    setGeneratedContent('');
    setPrompt('');
  };

  return (
    <div className="content-generation-panel">
      <div className="panel-header">
        <h2>🎨 Content Generation</h2>
        <div className="header-actions">
          <button 
            className="clear-button"
            onClick={clearContent}
            disabled={!generatedContent}
          >
            Clear
          </button>
        </div>
      </div>

      <div className="panel-content">
        {/* Content Type Selection */}
        <div className="content-type-selection">
          <h3>Content Type</h3>
          <div className="content-types-grid">
            {Object.entries(contentTypes).map(([key, value]) => (
              <button
                key={key}
                className={`content-type-button ${contentType === key ? 'active' : ''}`}
                onClick={() => setContentType(key)}
              >
                <span className="type-icon">{value.icon}</span>
                <span className="type-name">{value.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Template Selection for Thought Leadership */}
        {contentType === 'article' && (
          <div className="template-selection">
            <h3>Template Type</h3>
            <select 
              value={templateType} 
              onChange={(e) => setTemplateType(e.target.value)}
              className="template-select"
            >
              {Object.entries(templateTypes['thought-leadership']).map(([key, value]) => (
                <option key={key} value={key}>{value}</option>
              ))}
            </select>
          </div>
        )}

        {/* Prompt Input */}
        <div className="prompt-section">
          <h3>Prompt</h3>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter your content prompt here..."
            className="prompt-input"
            rows={4}
          />
        </div>

        {/* Generation Buttons */}
        <div className="generation-buttons">
          <button
            className="generate-button primary"
            onClick={contentType === 'article' ? generateThoughtLeadership : generateContent}
            disabled={isGenerating || !prompt.trim()}
          >
            {isGenerating ? 'Generating...' : 'Generate Content'}
          </button>
          
          <button
            className="generate-button secondary"
            onClick={generateVariations}
            disabled={isGenerating || !prompt.trim()}
          >
            Generate Variations
          </button>
        </div>

        {/* Generated Content */}
        {generatedContent && (
          <div className="generated-content">
            <div className="content-header">
              <h3>Generated Content</h3>
              <div className="content-actions">
                <button 
                  className="action-button"
                  onClick={() => copyToClipboard(generatedContent)}
                >
                  Copy
                </button>
                <button 
                  className="action-button"
                  onClick={() => setGeneratedContent('')}
                >
                  Clear
                </button>
              </div>
            </div>
            <div className="content-display">
              <pre className="content-text">{generatedContent}</pre>
            </div>
          </div>
        )}

        {/* Content History */}
        {contentHistory.length > 0 && (
          <div className="content-history">
            <h3>Recent Generations</h3>
            <div className="history-list">
              {contentHistory.slice(0, 5).map((item) => (
                <div key={item.id} className="history-item">
                  <div className="history-header">
                    <span className="history-type">
                      {contentTypes[item.type]?.icon} {contentTypes[item.type]?.name}
                    </span>
                    <span className="history-time">
                      {new Date(item.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="history-prompt">
                    {item.prompt.length > 100 ? item.prompt.substring(0, 100) + '...' : item.prompt}
                  </div>
                  <div className="history-actions">
                    <button 
                      className="history-button"
                      onClick={() => setGeneratedContent(item.content)}
                    >
                      View
                    </button>
                    <button 
                      className="history-button"
                      onClick={() => copyToClipboard(item.content)}
                    >
                      Copy
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentGenerationPanel;

