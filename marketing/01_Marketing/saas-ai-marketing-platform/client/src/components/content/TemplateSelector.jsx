import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Search, 
  Filter, 
  Star, 
  TrendingUp, 
  Clock, 
  Users,
  FileText,
  Mail,
  MessageSquare,
  ShoppingCart,
  Globe,
  Presentation,
  BarChart3
} from 'lucide-react';

const TemplateSelector = ({ 
  templates = [], 
  selectedTemplate, 
  onSelect, 
  showAll = false 
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('popular');

  const categories = [
    { id: 'all', label: 'All Templates', icon: FileText },
    { id: 'email-marketing', label: 'Email Marketing', icon: Mail },
    { id: 'social-media', label: 'Social Media', icon: MessageSquare },
    { id: 'ad-copy', label: 'Ad Copy', icon: ShoppingCart },
    { id: 'blog-content', label: 'Blog Content', icon: FileText },
    { id: 'product-descriptions', label: 'Product Descriptions', icon: ShoppingCart },
    { id: 'landing-pages', label: 'Landing Pages', icon: Globe },
    { id: 'sales-copy', label: 'Sales Copy', icon: TrendingUp },
    { id: 'performance-reviews', label: 'Performance Reviews', icon: BarChart3 },
    { id: 'presentations', label: 'Presentations', icon: Presentation }
  ];

  const sortOptions = [
    { id: 'popular', label: 'Most Popular' },
    { id: 'recent', label: 'Most Recent' },
    { id: 'rating', label: 'Highest Rated' },
    { id: 'name', label: 'Name A-Z' }
  ];

  // Filter and sort templates
  const filteredTemplates = templates
    .filter(template => {
      const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           template.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           template.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
      
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'popular':
          return b.usage.totalUses - a.usage.totalUses;
        case 'recent':
          return new Date(b.createdAt) - new Date(a.createdAt);
        case 'rating':
          return b.usage.averageRating - a.usage.averageRating;
        case 'name':
          return a.name.localeCompare(b.name);
        default:
          return 0;
      }
    });

  const getCategoryIcon = (category) => {
    const categoryData = categories.find(cat => cat.id === category);
    return categoryData ? categoryData.icon : FileText;
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'advanced':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search templates..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
          />
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => {
            const Icon = category.icon;
            return (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  selectedCategory === category.id
                    ? 'bg-blue-500 text-white shadow-lg'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                <Icon className="w-4 h-4 mr-2" />
                {category.label}
              </button>
            );
          })}
        </div>

        {/* Sort Options */}
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
          >
            {sortOptions.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTemplates.map((template, index) => {
          const CategoryIcon = getCategoryIcon(template.category);
          const isSelected = selectedTemplate?._id === template._id;
          
          return (
            <motion.div
              key={template._id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              onClick={() => onSelect(template)}
              className={`relative bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 cursor-pointer transition-all duration-200 hover:shadow-xl ${
                isSelected 
                  ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                  : 'hover:ring-2 hover:ring-blue-200 dark:hover:ring-blue-800'
              }`}
            >
              {/* Template Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg mr-3">
                    <CategoryIcon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {template.name}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {template.category.replace('-', ' ')}
                    </p>
                  </div>
                </div>
                
                {template.isFeatured && (
                  <Star className="w-5 h-5 text-yellow-500 fill-current" />
                )}
              </div>

              {/* Template Description */}
              <p className="text-gray-600 dark:text-gray-300 text-sm mb-4 line-clamp-2">
                {template.description}
              </p>

              {/* Template Stats */}
              <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-4">
                <div className="flex items-center">
                  <TrendingUp className="w-4 h-4 mr-1" />
                  {template.usage.totalUses.toLocaleString()} uses
                </div>
                <div className="flex items-center">
                  <Star className="w-4 h-4 mr-1" />
                  {template.usage.averageRating.toFixed(1)}
                </div>
                <div className="flex items-center">
                  <Clock className="w-4 h-4 mr-1" />
                  {template.estimatedTime}min
                </div>
              </div>

              {/* Difficulty Badge */}
              <div className="flex items-center justify-between">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(template.difficulty)}`}>
                  {template.difficulty}
                </span>
                
                {template.requiredPlan !== 'free' && (
                  <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-400 rounded-full text-xs font-medium">
                    {template.requiredPlan}
                  </span>
                )}
              </div>

              {/* Template Tags */}
              {template.tags.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-1">
                  {template.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded text-xs"
                    >
                      #{tag}
                    </span>
                  ))}
                  {template.tags.length > 3 && (
                    <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded text-xs">
                      +{template.tags.length - 3}
                    </span>
                  )}
                </div>
              )}

              {/* Selection Indicator */}
              {isSelected && (
                <div className="absolute top-4 right-4">
                  <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* No Results */}
      {filteredTemplates.length === 0 && (
        <div className="text-center py-12">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            No templates found
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Try adjusting your search terms or filters
          </p>
        </div>
      )}

      {/* Results Count */}
      {filteredTemplates.length > 0 && (
        <div className="text-center text-sm text-gray-500 dark:text-gray-400">
          Showing {filteredTemplates.length} of {templates.length} templates
        </div>
      )}
    </div>
  );
};

export default TemplateSelector;









