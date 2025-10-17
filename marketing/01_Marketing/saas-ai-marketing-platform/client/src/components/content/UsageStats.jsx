import React from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  Zap, 
  Calendar,
  Target,
  DollarSign,
  Clock,
  FileText
} from 'lucide-react';

const UsageStats = ({ stats }) => {
  const {
    monthlyLimit = 10,
    contentGenerations = 0,
    totalCost = 0,
    averageRating = 0,
    totalViews = 0,
    totalCopies = 0,
    totalShares = 0,
    favoriteCount = 0,
    lastResetDate
  } = stats;

  const usagePercentage = (contentGenerations / monthlyLimit) * 100;
  const remainingUsage = monthlyLimit - contentGenerations;
  const daysUntilReset = Math.ceil((new Date(lastResetDate).getTime() + 30 * 24 * 60 * 60 * 1000 - new Date().getTime()) / (1000 * 60 * 60 * 24));

  const getUsageColor = (percentage) => {
    if (percentage >= 90) return 'text-red-500';
    if (percentage >= 75) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getUsageBgColor = (percentage) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const statCards = [
    {
      title: 'Monthly Usage',
      value: `${contentGenerations}/${monthlyLimit}`,
      subtitle: `${remainingUsage} remaining`,
      icon: BarChart3,
      color: 'blue',
      progress: usagePercentage
    },
    {
      title: 'Total Cost',
      value: `$${totalCost.toFixed(4)}`,
      subtitle: 'This month',
      icon: DollarSign,
      color: 'green'
    },
    {
      title: 'Average Rating',
      value: averageRating > 0 ? averageRating.toFixed(1) : 'N/A',
      subtitle: 'Content quality',
      icon: Target,
      color: 'yellow'
    },
    {
      title: 'Total Views',
      value: totalViews.toLocaleString(),
      subtitle: 'Content interactions',
      icon: FileText,
      color: 'purple'
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: {
        bg: 'bg-blue-50 dark:bg-blue-900/20',
        icon: 'text-blue-500',
        text: 'text-blue-900 dark:text-blue-300',
        subtitle: 'text-blue-700 dark:text-blue-400'
      },
      green: {
        bg: 'bg-green-50 dark:bg-green-900/20',
        icon: 'text-green-500',
        text: 'text-green-900 dark:text-green-300',
        subtitle: 'text-green-700 dark:text-green-400'
      },
      yellow: {
        bg: 'bg-yellow-50 dark:bg-yellow-900/20',
        icon: 'text-yellow-500',
        text: 'text-yellow-900 dark:text-yellow-300',
        subtitle: 'text-yellow-700 dark:text-yellow-400'
      },
      purple: {
        bg: 'bg-purple-50 dark:bg-purple-900/20',
        icon: 'text-purple-500',
        text: 'text-purple-900 dark:text-purple-300',
        subtitle: 'text-purple-700 dark:text-purple-400'
      }
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="space-y-6">
      {/* Usage Overview */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
            <Zap className="w-5 h-5 mr-2 text-blue-500" />
            Usage Overview
          </h3>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Resets in {daysUntilReset} days
          </div>
        </div>

        {/* Usage Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Monthly Usage
            </span>
            <span className={`text-sm font-medium ${getUsageColor(usagePercentage)}`}>
              {usagePercentage.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(usagePercentage, 100)}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
              className={`h-3 rounded-full ${getUsageBgColor(usagePercentage)}`}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
            <span>0</span>
            <span>{monthlyLimit}</span>
          </div>
        </div>

        {/* Usage Warning */}
        {usagePercentage >= 90 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
          >
            <div className="flex items-center">
              <div className="w-2 h-2 bg-red-500 rounded-full mr-2"></div>
              <span className="text-sm text-red-700 dark:text-red-400">
                You're approaching your monthly limit. Consider upgrading your plan.
              </span>
            </div>
          </motion.div>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          const colors = getColorClasses(stat.color);
          
          return (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`${colors.bg} rounded-lg p-4`}
            >
              <div className="flex items-center justify-between mb-2">
                <Icon className={`w-5 h-5 ${colors.icon}`} />
                {stat.progress !== undefined && (
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {stat.progress.toFixed(0)}%
                  </div>
                )}
              </div>
              
              <div className={`text-2xl font-bold ${colors.text} mb-1`}>
                {stat.value}
              </div>
              
              <div className={`text-sm ${colors.subtitle}`}>
                {stat.subtitle}
              </div>
              
              {stat.progress !== undefined && (
                <div className="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(stat.progress, 100)}%` }}
                    transition={{ duration: 1, delay: index * 0.1 }}
                    className={`h-1 rounded-full ${getUsageBgColor(stat.progress)}`}
                  />
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <div className="flex items-center mb-2">
            <FileText className="w-5 h-5 text-gray-500 mr-2" />
            <h4 className="font-medium text-gray-900 dark:text-white">Content Copies</h4>
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {totalCopies}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Times copied to clipboard
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <div className="flex items-center mb-2">
            <TrendingUp className="w-5 h-5 text-gray-500 mr-2" />
            <h4 className="font-medium text-gray-900 dark:text-white">Content Shares</h4>
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {totalShares}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Times shared externally
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <div className="flex items-center mb-2">
            <Target className="w-5 h-5 text-gray-500 mr-2" />
            <h4 className="font-medium text-gray-900 dark:text-white">Favorites</h4>
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {favoriteCount}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Saved as favorites
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg p-6">
        <h4 className="font-semibold text-gray-900 dark:text-white mb-4">
          Quick Actions
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center justify-center p-3 bg-white dark:bg-gray-800 rounded-lg hover:shadow-md transition-shadow">
            <Calendar className="w-5 h-5 text-blue-500 mr-2" />
            <span className="text-sm font-medium">View History</span>
          </button>
          <button className="flex items-center justify-center p-3 bg-white dark:bg-gray-800 rounded-lg hover:shadow-md transition-shadow">
            <TrendingUp className="w-5 h-5 text-green-500 mr-2" />
            <span className="text-sm font-medium">Analytics</span>
          </button>
          <button className="flex items-center justify-center p-3 bg-white dark:bg-gray-800 rounded-lg hover:shadow-md transition-shadow">
            <Zap className="w-5 h-5 text-purple-500 mr-2" />
            <span className="text-sm font-medium">Upgrade Plan</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default UsageStats;









