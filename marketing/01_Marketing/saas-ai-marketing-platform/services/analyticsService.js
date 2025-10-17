const mongoose = require('mongoose');
const User = require('../models/User');
const GeneratedContent = require('../models/GeneratedContent');
const ContentTemplate = require('../models/ContentTemplate');

class AnalyticsService {
  constructor() {
    this.metricsCache = new Map();
    this.cacheExpiry = 5 * 60 * 1000; // 5 minutes
  }

  /**
   * Get comprehensive user analytics
   */
  async getUserAnalytics(userId, timeRange = '30d') {
    const cacheKey = `user_analytics_${userId}_${timeRange}`;
    const cached = this.metricsCache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.cacheExpiry) {
      return cached.data;
    }

    const startDate = this.getStartDate(timeRange);
    const endDate = new Date();

    const [
      contentStats,
      usageStats,
      performanceStats,
      trendData,
      comparisonData
    ] = await Promise.all([
      this.getContentStats(userId, startDate, endDate),
      this.getUsageStats(userId, startDate, endDate),
      this.getPerformanceStats(userId, startDate, endDate),
      this.getTrendData(userId, startDate, endDate),
      this.getComparisonData(userId, startDate, endDate)
    ]);

    const analytics = {
      overview: {
        totalContent: contentStats.total,
        totalWords: contentStats.totalWords,
        averageRating: contentStats.averageRating,
        totalViews: contentStats.totalViews,
        totalShares: contentStats.totalShares,
        totalCopies: contentStats.totalCopies
      },
      usage: {
        generationsThisPeriod: usageStats.generations,
        generationsLastPeriod: usageStats.lastPeriodGenerations,
        usageGrowth: this.calculateGrowthRate(usageStats.generations, usageStats.lastPeriodGenerations),
        costThisPeriod: usageStats.cost,
        costLastPeriod: usageStats.lastPeriodCost,
        costGrowth: this.calculateGrowthRate(usageStats.cost, usageStats.lastPeriodCost),
        averageCostPerGeneration: usageStats.generations > 0 ? usageStats.cost / usageStats.generations : 0
      },
      performance: {
        averageEngagement: performanceStats.averageEngagement,
        topPerformingContent: performanceStats.topContent,
        worstPerformingContent: performanceStats.worstContent,
        categoryPerformance: performanceStats.categoryPerformance,
        templatePerformance: performanceStats.templatePerformance
      },
      trends: {
        dailyGenerations: trendData.dailyGenerations,
        dailyCost: trendData.dailyCost,
        dailyEngagement: trendData.dailyEngagement,
        weeklyGrowth: trendData.weeklyGrowth,
        monthlyGrowth: trendData.monthlyGrowth
      },
      comparison: {
        vsAverageUser: comparisonData.vsAverage,
        vsTopUsers: comparisonData.vsTopUsers,
        percentile: comparisonData.percentile,
        recommendations: comparisonData.recommendations
      },
      insights: await this.generateInsights({
        contentStats,
        usageStats,
        performanceStats,
        trendData,
        comparisonData
      })
    };

    // Cache the results
    this.metricsCache.set(cacheKey, {
      data: analytics,
      timestamp: Date.now()
    });

    return analytics;
  }

  /**
   * Get content statistics
   */
  async getContentStats(userId, startDate, endDate) {
    const pipeline = [
      {
        $match: {
          userId: new mongoose.Types.ObjectId(userId),
          createdAt: { $gte: startDate, $lte: endDate },
          status: 'completed'
        }
      },
      {
        $group: {
          _id: null,
          total: { $sum: 1 },
          totalWords: { $sum: { $strLenCP: '$content' } },
          averageRating: { $avg: '$rating' },
          totalViews: { $sum: '$views' },
          totalShares: { $sum: '$shares' },
          totalCopies: { $sum: '$copies' },
          averageCost: { $avg: '$metadata.cost' }
        }
      }
    ];

    const result = await GeneratedContent.aggregate(pipeline);
    return result[0] || {
      total: 0,
      totalWords: 0,
      averageRating: 0,
      totalViews: 0,
      totalShares: 0,
      totalCopies: 0,
      averageCost: 0
    };
  }

  /**
   * Get usage statistics
   */
  async getUsageStats(userId, startDate, endDate) {
    const lastPeriodStart = new Date(startDate.getTime() - (endDate.getTime() - startDate.getTime()));
    const lastPeriodEnd = startDate;

    const [currentPeriod, lastPeriod] = await Promise.all([
      GeneratedContent.aggregate([
        {
          $match: {
            userId: new mongoose.Types.ObjectId(userId),
            createdAt: { $gte: startDate, $lte: endDate },
            status: 'completed'
          }
        },
        {
          $group: {
            _id: null,
            generations: { $sum: 1 },
            cost: { $sum: '$metadata.cost' }
          }
        }
      ]),
      GeneratedContent.aggregate([
        {
          $match: {
            userId: new mongoose.Types.ObjectId(userId),
            createdAt: { $gte: lastPeriodStart, $lte: lastPeriodEnd },
            status: 'completed'
          }
        },
        {
          $group: {
            _id: null,
            generations: { $sum: 1 },
            cost: { $sum: '$metadata.cost' }
          }
        }
      ])
    ]);

    return {
      generations: currentPeriod[0]?.generations || 0,
      cost: currentPeriod[0]?.cost || 0,
      lastPeriodGenerations: lastPeriod[0]?.generations || 0,
      lastPeriodCost: lastPeriod[0]?.cost || 0
    };
  }

  /**
   * Get performance statistics
   */
  async getPerformanceStats(userId, startDate, endDate) {
    const [
      topContent,
      worstContent,
      categoryPerformance,
      templatePerformance
    ] = await Promise.all([
      this.getTopPerformingContent(userId, startDate, endDate, 5),
      this.getWorstPerformingContent(userId, startDate, endDate, 5),
      this.getCategoryPerformance(userId, startDate, endDate),
      this.getTemplatePerformance(userId, startDate, endDate)
    ]);

    const averageEngagement = await this.calculateAverageEngagement(userId, startDate, endDate);

    return {
      averageEngagement,
      topContent,
      worstContent,
      categoryPerformance,
      templatePerformance
    };
  }

  /**
   * Get trend data
   */
  async getTrendData(userId, startDate, endDate) {
    const dailyData = await GeneratedContent.aggregate([
      {
        $match: {
          userId: new mongoose.Types.ObjectId(userId),
          createdAt: { $gte: startDate, $lte: endDate },
          status: 'completed'
        }
      },
      {
        $group: {
          _id: {
            year: { $year: '$createdAt' },
            month: { $month: '$createdAt' },
            day: { $dayOfMonth: '$createdAt' }
          },
          generations: { $sum: 1 },
          cost: { $sum: '$metadata.cost' },
          engagement: { $avg: { $add: ['$views', '$shares', '$copies'] } }
        }
      },
      { $sort: { '_id.year': 1, '_id.month': 1, '_id.day': 1 } }
    ]);

    const weeklyGrowth = await this.calculateWeeklyGrowth(userId, startDate, endDate);
    const monthlyGrowth = await this.calculateMonthlyGrowth(userId, startDate, endDate);

    return {
      dailyGenerations: dailyData.map(d => ({
        date: new Date(d._id.year, d._id.month - 1, d._id.day),
        generations: d.generations,
        cost: d.cost,
        engagement: d.engagement
      })),
      dailyCost: dailyData.map(d => ({
        date: new Date(d._id.year, d._id.month - 1, d._id.day),
        cost: d.cost
      })),
      dailyEngagement: dailyData.map(d => ({
        date: new Date(d._id.year, d._id.month - 1, d._id.day),
        engagement: d.engagement
      })),
      weeklyGrowth,
      monthlyGrowth
    };
  }

  /**
   * Get comparison data
   */
  async getComparisonData(userId, startDate, endDate) {
    const userStats = await this.getContentStats(userId, startDate, endDate);
    
    // Get average user stats
    const averageStats = await GeneratedContent.aggregate([
      {
        $match: {
          createdAt: { $gte: startDate, $lte: endDate },
          status: 'completed'
        }
      },
      {
        $group: {
          _id: '$userId',
          totalContent: { $sum: 1 },
          totalViews: { $sum: '$views' },
          totalShares: { $sum: '$shares' },
          averageRating: { $avg: '$rating' }
        }
      },
      {
        $group: {
          _id: null,
          avgContent: { $avg: '$totalContent' },
          avgViews: { $avg: '$totalViews' },
          avgShares: { $avg: '$totalShares' },
          avgRating: { $avg: '$averageRating' }
        }
      }
    ]);

    // Get top 10% user stats
    const topUsersStats = await GeneratedContent.aggregate([
      {
        $match: {
          createdAt: { $gte: startDate, $lte: endDate },
          status: 'completed'
        }
      },
      {
        $group: {
          _id: '$userId',
          totalContent: { $sum: 1 },
          totalViews: { $sum: '$views' },
          totalShares: { $sum: '$shares' },
          averageRating: { $avg: '$rating' }
        }
      },
      { $sort: { totalViews: -1 } },
      { $limit: Math.ceil(await User.countDocuments() * 0.1) },
      {
        $group: {
          _id: null,
          avgContent: { $avg: '$totalContent' },
          avgViews: { $avg: '$totalViews' },
          avgShares: { $avg: '$totalShares' },
          avgRating: { $avg: '$averageRating' }
        }
      }
    ]);

    const average = averageStats[0] || { avgContent: 0, avgViews: 0, avgShares: 0, avgRating: 0 };
    const topUsers = topUsersStats[0] || { avgContent: 0, avgViews: 0, avgShares: 0, avgRating: 0 };

    // Calculate percentile
    const percentile = await this.calculatePercentile(userId, startDate, endDate);

    // Generate recommendations
    const recommendations = this.generateRecommendations(userStats, average, topUsers);

    return {
      vsAverage: {
        content: this.calculateComparison(userStats.total, average.avgContent),
        views: this.calculateComparison(userStats.totalViews, average.avgViews),
        shares: this.calculateComparison(userStats.totalShares, average.avgShares),
        rating: this.calculateComparison(userStats.averageRating, average.avgRating)
      },
      vsTopUsers: {
        content: this.calculateComparison(userStats.total, topUsers.avgContent),
        views: this.calculateComparison(userStats.totalViews, topUsers.avgViews),
        shares: this.calculateComparison(userStats.totalShares, topUsers.avgShares),
        rating: this.calculateComparison(userStats.averageRating, topUsers.avgRating)
      },
      percentile,
      recommendations
    };
  }

  /**
   * Generate insights based on analytics data
   */
  async generateInsights(data) {
    const insights = [];

    // Usage insights
    if (data.usageStats.usageGrowth > 50) {
      insights.push({
        type: 'positive',
        category: 'usage',
        title: 'Rapid Growth in Content Generation',
        description: `Your content generation has increased by ${data.usageStats.usageGrowth.toFixed(1)}% compared to the previous period.`,
        recommendation: 'Consider upgrading your plan to maintain this momentum.',
        impact: 'high'
      });
    } else if (data.usageStats.usageGrowth < -20) {
      insights.push({
        type: 'warning',
        category: 'usage',
        title: 'Decrease in Content Generation',
        description: `Your content generation has decreased by ${Math.abs(data.usageStats.usageGrowth).toFixed(1)}% compared to the previous period.`,
        recommendation: 'Review your content strategy and consider using more templates.',
        impact: 'medium'
      });
    }

    // Performance insights
    if (data.performanceStats.averageEngagement > 100) {
      insights.push({
        type: 'positive',
        category: 'performance',
        title: 'High Engagement Content',
        description: 'Your content is generating above-average engagement.',
        recommendation: 'Continue creating similar content and consider expanding successful formats.',
        impact: 'high'
      });
    }

    // Cost insights
    if (data.usageStats.averageCostPerGeneration > 0.05) {
      insights.push({
        type: 'warning',
        category: 'cost',
        title: 'High Cost Per Generation',
        description: `Your average cost per generation is $${data.usageStats.averageCostPerGeneration.toFixed(4)}.`,
        recommendation: 'Consider using more efficient models or optimizing your prompts.',
        impact: 'medium'
      });
    }

    // Trend insights
    if (data.trends.weeklyGrowth > 20) {
      insights.push({
        type: 'positive',
        category: 'trends',
        title: 'Positive Growth Trend',
        description: 'You\'re showing consistent weekly growth in content generation.',
        recommendation: 'Maintain this momentum and consider scaling your content strategy.',
        impact: 'high'
      });
    }

    return insights;
  }

  /**
   * Get top performing content
   */
  async getTopPerformingContent(userId, startDate, endDate, limit = 5) {
    return await GeneratedContent.find({
      userId,
      createdAt: { $gte: startDate, $lte: endDate },
      status: 'completed'
    })
      .sort({ views: -1, shares: -1, copies: -1 })
      .limit(limit)
      .populate('templateId', 'name category')
      .select('content views shares copies rating createdAt templateId');
  }

  /**
   * Get worst performing content
   */
  async getWorstPerformingContent(userId, startDate, endDate, limit = 5) {
    return await GeneratedContent.find({
      userId,
      createdAt: { $gte: startDate, $lte: endDate },
      status: 'completed',
      views: { $gte: 0 }
    })
      .sort({ views: 1, shares: 1, copies: 1 })
      .limit(limit)
      .populate('templateId', 'name category')
      .select('content views shares copies rating createdAt templateId');
  }

  /**
   * Get category performance
   */
  async getCategoryPerformance(userId, startDate, endDate) {
    return await GeneratedContent.aggregate([
      {
        $match: {
          userId: new mongoose.Types.ObjectId(userId),
          createdAt: { $gte: startDate, $lte: endDate },
          status: 'completed'
        }
      },
      {
        $lookup: {
          from: 'contenttemplates',
          localField: 'templateId',
          foreignField: '_id',
          as: 'template'
        }
      },
      {
        $unwind: { path: '$template', preserveNullAndEmptyArrays: true }
      },
      {
        $group: {
          _id: '$template.category',
          count: { $sum: 1 },
          totalViews: { $sum: '$views' },
          totalShares: { $sum: '$shares' },
          totalCopies: { $sum: '$copies' },
          averageRating: { $avg: '$rating' },
          averageCost: { $avg: '$metadata.cost' }
        }
      },
      { $sort: { totalViews: -1 } }
    ]);
  }

  /**
   * Get template performance
   */
  async getTemplatePerformance(userId, startDate, endDate) {
    return await GeneratedContent.aggregate([
      {
        $match: {
          userId: new mongoose.Types.ObjectId(userId),
          createdAt: { $gte: startDate, $lte: endDate },
          status: 'completed'
        }
      },
      {
        $lookup: {
          from: 'contenttemplates',
          localField: 'templateId',
          foreignField: '_id',
          as: 'template'
        }
      },
      {
        $unwind: { path: '$template', preserveNullAndEmptyArrays: true }
      },
      {
        $group: {
          _id: '$templateId',
          templateName: { $first: '$template.name' },
          templateCategory: { $first: '$template.category' },
          count: { $sum: 1 },
          totalViews: { $sum: '$views' },
          totalShares: { $sum: '$shares' },
          totalCopies: { $sum: '$copies' },
          averageRating: { $avg: '$rating' },
          averageCost: { $avg: '$metadata.cost' }
        }
      },
      { $sort: { totalViews: -1 } },
      { $limit: 10 }
    ]);
  }

  /**
   * Calculate average engagement
   */
  async calculateAverageEngagement(userId, startDate, endDate) {
    const result = await GeneratedContent.aggregate([
      {
        $match: {
          userId: new mongoose.Types.ObjectId(userId),
          createdAt: { $gte: startDate, $lte: endDate },
          status: 'completed'
        }
      },
      {
        $group: {
          _id: null,
          averageEngagement: { $avg: { $add: ['$views', '$shares', '$copies'] } }
        }
      }
    ]);

    return result[0]?.averageEngagement || 0;
  }

  /**
   * Calculate weekly growth
   */
  async calculateWeeklyGrowth(userId, startDate, endDate) {
    const weeks = Math.ceil((endDate - startDate) / (7 * 24 * 60 * 60 * 1000));
    const weeklyData = [];

    for (let i = 0; i < weeks; i++) {
      const weekStart = new Date(startDate.getTime() + (i * 7 * 24 * 60 * 60 * 1000));
      const weekEnd = new Date(Math.min(weekStart.getTime() + (7 * 24 * 60 * 60 * 1000), endDate.getTime()));

      const weekStats = await GeneratedContent.aggregate([
        {
          $match: {
            userId: new mongoose.Types.ObjectId(userId),
            createdAt: { $gte: weekStart, $lte: weekEnd },
            status: 'completed'
          }
        },
        {
          $group: {
            _id: null,
            generations: { $sum: 1 },
            cost: { $sum: '$metadata.cost' }
          }
        }
      ]);

      weeklyData.push({
        week: i + 1,
        startDate: weekStart,
        endDate: weekEnd,
        generations: weekStats[0]?.generations || 0,
        cost: weekStats[0]?.cost || 0
      });
    }

    return weeklyData;
  }

  /**
   * Calculate monthly growth
   */
  async calculateMonthlyGrowth(userId, startDate, endDate) {
    const months = Math.ceil((endDate - startDate) / (30 * 24 * 60 * 60 * 1000));
    const monthlyData = [];

    for (let i = 0; i < months; i++) {
      const monthStart = new Date(startDate.getTime() + (i * 30 * 24 * 60 * 60 * 1000));
      const monthEnd = new Date(Math.min(monthStart.getTime() + (30 * 24 * 60 * 60 * 1000), endDate.getTime()));

      const monthStats = await GeneratedContent.aggregate([
        {
          $match: {
            userId: new mongoose.Types.ObjectId(userId),
            createdAt: { $gte: monthStart, $lte: monthEnd },
            status: 'completed'
          }
        },
        {
          $group: {
            _id: null,
            generations: { $sum: 1 },
            cost: { $sum: '$metadata.cost' }
          }
        }
      ]);

      monthlyData.push({
        month: i + 1,
        startDate: monthStart,
        endDate: monthEnd,
        generations: monthStats[0]?.generations || 0,
        cost: monthStats[0]?.cost || 0
      });
    }

    return monthlyData;
  }

  /**
   * Calculate percentile ranking
   */
  async calculatePercentile(userId, startDate, endDate) {
    const userStats = await this.getContentStats(userId, startDate, endDate);
    
    const allUserStats = await GeneratedContent.aggregate([
      {
        $match: {
          createdAt: { $gte: startDate, $lte: endDate },
          status: 'completed'
        }
      },
      {
        $group: {
          _id: '$userId',
          totalContent: { $sum: 1 },
          totalViews: { $sum: '$views' },
          totalShares: { $sum: '$shares' }
        }
      }
    ]);

    const sortedStats = allUserStats.sort((a, b) => b.totalViews - a.totalViews);
    const userRank = sortedStats.findIndex(stat => stat._id.toString() === userId.toString());
    
    return userRank >= 0 ? Math.round(((sortedStats.length - userRank) / sortedStats.length) * 100) : 0;
  }

  /**
   * Generate recommendations
   */
  generateRecommendations(userStats, averageStats, topUserStats) {
    const recommendations = [];

    if (userStats.total < averageStats.avgContent) {
      recommendations.push({
        type: 'usage',
        priority: 'medium',
        title: 'Increase Content Generation',
        description: 'You\'re generating less content than the average user.',
        action: 'Try using more templates and setting up content generation schedules.'
      });
    }

    if (userStats.totalViews < averageStats.avgViews) {
      recommendations.push({
        type: 'engagement',
        priority: 'high',
        title: 'Improve Content Engagement',
        description: 'Your content is getting fewer views than average.',
        action: 'Focus on creating more engaging headlines and optimizing for your target audience.'
      });
    }

    if (userStats.averageRating < 4.0) {
      recommendations.push({
        type: 'quality',
        priority: 'high',
        title: 'Improve Content Quality',
        description: 'Your content ratings are below average.',
        action: 'Review your content strategy and consider using higher-quality templates.'
      });
    }

    return recommendations;
  }

  /**
   * Helper methods
   */
  getStartDate(timeRange) {
    const now = new Date();
    switch (timeRange) {
      case '7d': return new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      case '30d': return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      case '90d': return new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
      case '1y': return new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
      default: return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
    }
  }

  calculateGrowthRate(current, previous) {
    if (previous === 0) return current > 0 ? 100 : 0;
    return ((current - previous) / previous) * 100;
  }

  calculateComparison(userValue, averageValue) {
    if (averageValue === 0) return userValue > 0 ? 100 : 0;
    return ((userValue - averageValue) / averageValue) * 100;
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.metricsCache.clear();
  }

  /**
   * Get platform-wide analytics (admin only)
   */
  async getPlatformAnalytics(timeRange = '30d') {
    const startDate = this.getStartDate(timeRange);
    const endDate = new Date();

    const [
      userStats,
      contentStats,
      revenueStats,
      growthStats
    ] = await Promise.all([
      this.getPlatformUserStats(startDate, endDate),
      this.getPlatformContentStats(startDate, endDate),
      this.getPlatformRevenueStats(startDate, endDate),
      this.getPlatformGrowthStats(startDate, endDate)
    ]);

    return {
      users: userStats,
      content: contentStats,
      revenue: revenueStats,
      growth: growthStats,
      timestamp: new Date().toISOString()
    };
  }

  async getPlatformUserStats(startDate, endDate) {
    return await User.aggregate([
      {
        $match: {
          createdAt: { $gte: startDate, $lte: endDate }
        }
      },
      {
        $group: {
          _id: '$subscription.plan',
          count: { $sum: 1 }
        }
      }
    ]);
  }

  async getPlatformContentStats(startDate, endDate) {
    return await GeneratedContent.aggregate([
      {
        $match: {
          createdAt: { $gte: startDate, $lte: endDate },
          status: 'completed'
        }
      },
      {
        $group: {
          _id: null,
          totalGenerations: { $sum: 1 },
          totalCost: { $sum: '$metadata.cost' },
          averageRating: { $avg: '$rating' },
          totalViews: { $sum: '$views' },
          totalShares: { $sum: '$shares' }
        }
      }
    ]);
  }

  async getPlatformRevenueStats(startDate, endDate) {
    // This would integrate with your payment system
    // For now, return mock data
    return {
      totalRevenue: 0,
      monthlyRecurringRevenue: 0,
      averageRevenuePerUser: 0,
      churnRate: 0
    };
  }

  async getPlatformGrowthStats(startDate, endDate) {
    const userGrowth = await User.aggregate([
      {
        $group: {
          _id: {
            year: { $year: '$createdAt' },
            month: { $month: '$createdAt' }
          },
          count: { $sum: 1 }
        }
      },
      { $sort: { '_id.year': 1, '_id.month': 1 } }
    ]);

    return {
      userGrowth,
      contentGrowth: [], // Similar aggregation for content
      revenueGrowth: [] // Similar aggregation for revenue
    };
  }
}

module.exports = new AnalyticsService();






