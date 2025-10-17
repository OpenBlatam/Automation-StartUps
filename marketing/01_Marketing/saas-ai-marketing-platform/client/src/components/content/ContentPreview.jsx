import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Copy, 
  Download, 
  Star, 
  ThumbsUp, 
  ThumbsDown,
  Edit3,
  Eye,
  EyeOff,
  FileText,
  Hash,
  Clock,
  Zap
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

const ContentPreview = ({ content, onEdit, onRate, onSave }) => {
  const [showRaw, setShowRaw] = useState(false);
  const [isCopied, setIsCopied] = useState(false);

  if (!content) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600">
        <div className="text-center">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            Generated content will appear here
          </p>
        </div>
      </div>
    );
  }

  const wordCount = content.split(/\s+/).length;
  const charCount = content.length;
  const readingTime = Math.ceil(wordCount / 200); // Average reading speed: 200 words per minute

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy content:', error);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai-content-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleRate = (rating) => {
    if (onRate) {
      onRate(rating);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Content Stats */}
      <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div className="flex items-center space-x-6 text-sm text-gray-600 dark:text-gray-400">
          <div className="flex items-center">
            <Hash className="w-4 h-4 mr-1" />
            {wordCount} words
          </div>
          <div className="flex items-center">
            <FileText className="w-4 h-4 mr-1" />
            {charCount} characters
          </div>
          <div className="flex items-center">
            <Clock className="w-4 h-4 mr-1" />
            {readingTime} min read
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowRaw(!showRaw)}
            className="flex items-center px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
          >
            {showRaw ? <EyeOff className="w-4 h-4 mr-1" /> : <Eye className="w-4 h-4 mr-1" />}
            {showRaw ? 'Preview' : 'Raw'}
          </button>
        </div>
      </div>

      {/* Content Display */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="p-6">
          {showRaw ? (
            <pre className="whitespace-pre-wrap text-sm text-gray-900 dark:text-gray-100 font-mono">
              {content}
            </pre>
          ) : (
            <div className="prose prose-gray dark:prose-invert max-w-none">
              <ReactMarkdown
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <SyntaxHighlighter
                        style={tomorrow}
                        language={match[1]}
                        PreTag="div"
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    );
                  },
                }}
              >
                {content}
              </ReactMarkdown>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <button
            onClick={handleCopy}
            className={`flex items-center px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
              isCopied
                ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400'
                : 'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400 hover:bg-blue-200 dark:hover:bg-blue-900/30'
            }`}
          >
            <Copy className="w-4 h-4 mr-2" />
            {isCopied ? 'Copied!' : 'Copy'}
          </button>
          
          <button
            onClick={handleDownload}
            className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            <Download className="w-4 h-4 mr-2" />
            Download
          </button>
          
          {onEdit && (
            <button
              onClick={onEdit}
              className="flex items-center px-4 py-2 bg-purple-100 text-purple-700 dark:bg-purple-900/20 dark:text-purple-400 rounded-lg font-medium hover:bg-purple-200 dark:hover:bg-purple-900/30 transition-colors"
            >
              <Edit3 className="w-4 h-4 mr-2" />
              Edit
            </button>
          )}
        </div>

        {/* Rating */}
        {onRate && (
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600 dark:text-gray-400">Rate this content:</span>
            <button
              onClick={() => handleRate(1)}
              className="p-2 text-gray-400 hover:text-green-500 transition-colors"
              title="Good content"
            >
              <ThumbsUp className="w-5 h-5" />
            </button>
            <button
              onClick={() => handleRate(-1)}
              className="p-2 text-gray-400 hover:text-red-500 transition-colors"
              title="Needs improvement"
            >
              <ThumbsDown className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>

      {/* Content Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="flex items-center mb-2">
            <Zap className="w-5 h-5 text-blue-500 mr-2" />
            <h4 className="font-medium text-blue-900 dark:text-blue-300">Readability</h4>
          </div>
          <p className="text-sm text-blue-700 dark:text-blue-400">
            {wordCount < 100 ? 'Concise' : wordCount < 300 ? 'Moderate' : 'Detailed'}
          </p>
        </div>
        
        <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <div className="flex items-center mb-2">
            <FileText className="w-5 h-5 text-green-500 mr-2" />
            <h4 className="font-medium text-green-900 dark:text-green-300">Structure</h4>
          </div>
          <p className="text-sm text-green-700 dark:text-green-400">
            {content.includes('\n\n') ? 'Well-structured' : 'Single paragraph'}
          </p>
        </div>
        
        <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
          <div className="flex items-center mb-2">
            <Star className="w-5 h-5 text-purple-500 mr-2" />
            <h4 className="font-medium text-purple-900 dark:text-purple-300">Engagement</h4>
          </div>
          <p className="text-sm text-purple-700 dark:text-purple-400">
            {content.includes('!') || content.includes('?') ? 'Engaging' : 'Informative'}
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default ContentPreview;









