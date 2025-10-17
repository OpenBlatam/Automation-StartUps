import React, { useState, useEffect } from 'react';
import { 
  Trophy, 
  Star, 
  Award, 
  Target, 
  Zap, 
  Brain, 
  Crown,
  Medal,
  Shield,
  Flame,
  TrendingUp,
  CheckCircle,
  Clock,
  Lock,
  Unlock,
  Gift,
  Sparkles
} from 'lucide-react';

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  points: number;
  category: 'CONTENT' | 'CONSCIOUSNESS' | 'ENGAGEMENT' | 'LEADERSHIP' | 'INNOVATION';
  rarity: 'COMMON' | 'RARE' | 'EPIC' | 'LEGENDARY';
  unlocked: boolean;
  unlockedAt?: string;
  progress: number;
  maxProgress: number;
}

interface Level {
  level: number;
  name: string;
  minPoints: number;
  maxPoints: number;
  currentPoints: number;
  benefits: string[];
  color: string;
  icon: string;
}

interface Quest {
  id: string;
  title: string;
  description: string;
  type: 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'SPECIAL';
  rewards: {
    points: number;
    achievements?: string[];
    unlocks?: string[];
  };
  progress: number;
  maxProgress: number;
  completed: boolean;
  expiresAt?: string;
}

const ACHIEVEMENT_CATEGORIES = {
  CONTENT: { label: 'Content Creation', color: 'bg-blue-500', icon: Target },
  CONSCIOUSNESS: { label: 'Consciousness', color: 'bg-purple-500', icon: Brain },
  ENGAGEMENT: { label: 'Engagement', color: 'bg-green-500', icon: Zap },
  LEADERSHIP: { label: 'Leadership', color: 'bg-yellow-500', icon: Crown },
  INNOVATION: { label: 'Innovation', color: 'bg-red-500', icon: Sparkles },
};

const RARITY_COLORS = {
  COMMON: 'text-gray-500',
  RARE: 'text-blue-500',
  EPIC: 'text-purple-500',
  LEGENDARY: 'text-yellow-500',
};

const LEVELS: Level[] = [
  { level: 1, name: 'Neural Novice', minPoints: 0, maxPoints: 100, currentPoints: 0, benefits: ['Basic AI tools access'], color: 'bg-gray-500', icon: '🌱' },
  { level: 2, name: 'Conscious Marketer', minPoints: 101, maxPoints: 250, currentPoints: 0, benefits: ['Advanced content generation', 'Analytics dashboard'], color: 'bg-blue-500', icon: '🎯' },
  { level: 3, name: 'Neural Strategist', minPoints: 251, maxPoints: 500, currentPoints: 0, benefits: ['Team collaboration', 'Custom AI models'], color: 'bg-purple-500', icon: '🧠' },
  { level: 4, name: 'AI Marketing Master', minPoints: 501, maxPoints: 1000, currentPoints: 0, benefits: ['Enterprise features', 'Priority support'], color: 'bg-orange-500', icon: '👑' },
  { level: 5, name: 'Neural Marketing Consciousness', minPoints: 1001, maxPoints: 2000, currentPoints: 0, benefits: ['Revolutionary AI access', 'Industry recognition'], color: 'bg-red-500', icon: '🔥' },
];

export const NeuralGamification: React.FC = () => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [currentLevel, setCurrentLevel] = useState<Level>(LEVELS[0]);
  const [quests, setQuests] = useState<Quest[]>([]);
  const [totalPoints, setTotalPoints] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadGamificationData();
  }, []);

  const loadGamificationData = async () => {
    try {
      setIsLoading(true);
      
      // Mock data - replace with actual API calls
      const mockAchievements: Achievement[] = [
        {
          id: '1',
          title: 'First Steps',
          description: 'Generate your first piece of content',
          icon: '🎯',
          points: 10,
          category: 'CONTENT',
          rarity: 'COMMON',
          unlocked: true,
          unlockedAt: '2024-01-01',
          progress: 1,
          maxProgress: 1,
        },
        {
          id: '2',
          title: 'Content Creator',
          description: 'Generate 10 pieces of content',
          icon: '📝',
          points: 50,
          category: 'CONTENT',
          rarity: 'RARE',
          unlocked: false,
          progress: 7,
          maxProgress: 10,
        },
        {
          id: '3',
          title: 'Neural Awakening',
          description: 'Reach 50% consciousness level',
          icon: '🧠',
          points: 100,
          category: 'CONSCIOUSNESS',
          rarity: 'EPIC',
          unlocked: false,
          progress: 35,
          maxProgress: 50,
        },
        {
          id: '4',
          title: 'AI Master',
          description: 'Use all available AI features',
          icon: '🤖',
          points: 200,
          category: 'INNOVATION',
          rarity: 'LEGENDARY',
          unlocked: false,
          progress: 3,
          maxProgress: 10,
        },
      ];

      const mockQuests: Quest[] = [
        {
          id: '1',
          title: 'Daily Content Creation',
          description: 'Generate 3 pieces of content today',
          type: 'DAILY',
          rewards: { points: 25 },
          progress: 2,
          maxProgress: 3,
          completed: false,
          expiresAt: '2024-01-02T23:59:59Z',
        },
        {
          id: '2',
          title: 'Weekly Consciousness Boost',
          description: 'Increase your consciousness level by 5% this week',
          type: 'WEEKLY',
          rewards: { points: 100, achievements: ['Neural Awakening'] },
          progress: 2,
          maxProgress: 5,
          completed: false,
          expiresAt: '2024-01-07T23:59:59Z',
        },
        {
          id: '3',
          title: 'Monthly Innovation',
          description: 'Complete 50 content generations this month',
          type: 'MONTHLY',
          rewards: { points: 500, unlocks: ['Advanced AI Models'] },
          progress: 23,
          maxProgress: 50,
          completed: false,
          expiresAt: '2024-01-31T23:59:59Z',
        },
      ];

      setAchievements(mockAchievements);
      setQuests(mockQuests);
      setTotalPoints(150);
      setCurrentLevel(LEVELS[1]);
      
    } catch (error) {
      console.error('Error loading gamification data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getRarityColor = (rarity: string) => {
    return RARITY_COLORS[rarity as keyof typeof RARITY_COLORS] || 'text-gray-500';
  };

  const getCategoryIcon = (category: string) => {
    const categoryInfo = ACHIEVEMENT_CATEGORIES[category as keyof typeof ACHIEVEMENT_CATEGORIES];
    const Icon = categoryInfo?.icon || Target;
    return <Icon className="w-4 h-4" />;
  };

  const getCategoryColor = (category: string) => {
    const categoryInfo = ACHIEVEMENT_CATEGORIES[category as keyof typeof ACHIEVEMENT_CATEGORIES];
    return categoryInfo?.color || 'bg-gray-500';
  };

  const getQuestTypeColor = (type: string) => {
    const colors = {
      DAILY: 'bg-green-100 text-green-800',
      WEEKLY: 'bg-blue-100 text-blue-800',
      MONTHLY: 'bg-purple-100 text-purple-800',
      SPECIAL: 'bg-yellow-100 text-yellow-800',
    };
    return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getNextLevel = () => {
    const nextLevelIndex = LEVELS.findIndex(level => level.level === currentLevel.level + 1);
    return nextLevelIndex >= 0 ? LEVELS[nextLevelIndex] : null;
  };

  const getProgressToNextLevel = () => {
    const nextLevel = getNextLevel();
    if (!nextLevel) return 100;
    
    const progress = ((totalPoints - currentLevel.minPoints) / (nextLevel.minPoints - currentLevel.minPoints)) * 100;
    return Math.min(100, Math.max(0, progress));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        <span className="ml-2 text-gray-600">Loading gamification data...</span>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
          <Trophy className="w-8 h-8 mr-3 text-yellow-500" />
          Neural Gamification
        </h1>
        <p className="text-gray-600">
          Level up your marketing consciousness through achievements, quests, and rewards
        </p>
      </div>

      {/* Level Progress */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <div className={`p-3 rounded-full ${currentLevel.color} text-white mr-4`}>
              <span className="text-2xl">{currentLevel.icon}</span>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{currentLevel.name}</h2>
              <p className="text-gray-600">Level {currentLevel.level}</p>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-2xl font-bold text-purple-600">{totalPoints}</div>
            <div className="text-sm text-gray-500">Total Points</div>
          </div>
        </div>

        <div className="mb-4">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>Progress to Next Level</span>
            <span>{Math.round(getProgressToNextLevel())}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all duration-500"
              style={{ width: `${getProgressToNextLevel()}%` }}
            />
          </div>
        </div>

        {getNextLevel() && (
          <div className="text-sm text-gray-600">
            <span className="font-medium">{getNextLevel()!.minPoints - totalPoints} points</span> needed to reach{' '}
            <span className="font-medium text-purple-600">{getNextLevel()!.name}</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Achievements */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Award className="w-5 h-5 mr-2 text-yellow-500" />
            Achievements
          </h3>
          
          <div className="space-y-4">
            {achievements.map((achievement) => (
              <div
                key={achievement.id}
                className={`p-4 rounded-lg border ${
                  achievement.unlocked ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start">
                    <div className="text-2xl mr-3">{achievement.icon}</div>
                    <div className="flex-1">
                      <div className="flex items-center mb-1">
                        <h4 className="font-medium text-gray-900">{achievement.title}</h4>
                        {achievement.unlocked ? (
                          <CheckCircle className="w-4 h-4 text-green-500 ml-2" />
                        ) : (
                          <Lock className="w-4 h-4 text-gray-400 ml-2" />
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{achievement.description}</p>
                      
                      <div className="flex items-center space-x-4 text-xs">
                        <div className="flex items-center">
                          <div className={`p-1 rounded ${getCategoryColor(achievement.category)} text-white mr-1`}>
                            {getCategoryIcon(achievement.category)}
                          </div>
                          <span className="text-gray-500">
                            {ACHIEVEMENT_CATEGORIES[achievement.category as keyof typeof ACHIEVEMENT_CATEGORIES]?.label}
                          </span>
                        </div>
                        <span className={`font-medium ${getRarityColor(achievement.rarity)}`}>
                          {achievement.rarity}
                        </span>
                        <span className="text-gray-500">{achievement.points} pts</span>
                      </div>
                    </div>
                  </div>
                </div>

                {!achievement.unlocked && (
                  <div className="mt-3">
                    <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                      <span>Progress</span>
                      <span>{achievement.progress}/{achievement.maxProgress}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-purple-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${(achievement.progress / achievement.maxProgress) * 100}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Quests */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Target className="w-5 h-5 mr-2 text-blue-500" />
            Active Quests
          </h3>
          
          <div className="space-y-4">
            {quests.map((quest) => (
              <div
                key={quest.id}
                className={`p-4 rounded-lg border ${
                  quest.completed ? 'bg-green-50 border-green-200' : 'bg-white border-gray-200'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center mb-1">
                      <h4 className="font-medium text-gray-900">{quest.title}</h4>
                      <span className={`ml-2 px-2 py-1 rounded-full text-xs ${getQuestTypeColor(quest.type)}`}>
                        {quest.type}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{quest.description}</p>
                  </div>
                  
                  {quest.completed ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : (
                    <Clock className="w-5 h-5 text-gray-400" />
                  )}
                </div>

                <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                  <span>Progress</span>
                  <span>{quest.progress}/{quest.maxProgress}</span>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(quest.progress / quest.maxProgress) * 100}%` }}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-xs text-gray-500">
                    <span className="flex items-center">
                      <Star className="w-3 h-3 text-yellow-500 mr-1" />
                      {quest.rewards.points} pts
                    </span>
                    {quest.rewards.achievements && (
                      <span className="flex items-center">
                        <Award className="w-3 h-3 text-purple-500 mr-1" />
                        {quest.rewards.achievements.length} achievements
                      </span>
                    )}
                  </div>
                  
                  {quest.expiresAt && (
                    <span className="text-xs text-gray-500">
                      Expires: {new Date(quest.expiresAt).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Level Benefits */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mt-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Crown className="w-5 h-5 mr-2 text-yellow-500" />
          Current Level Benefits
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {currentLevel.benefits.map((benefit, index) => (
            <div key={index} className="flex items-center p-3 bg-purple-50 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-500 mr-3" />
              <span className="text-sm text-gray-700">{benefit}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Leaderboard Preview */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mt-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Trophy className="w-5 h-5 mr-2 text-yellow-500" />
          Leaderboard
        </h3>
        
        <div className="space-y-3">
          {[
            { rank: 1, name: 'AI Marketing Master', points: 1850, level: 'Neural Marketing Consciousness' },
            { rank: 2, name: 'Neural Strategist Pro', points: 1650, level: 'AI Marketing Master' },
            { rank: 3, name: 'Conscious Marketer', points: 1450, level: 'AI Marketing Master' },
            { rank: 4, name: 'You', points: totalPoints, level: currentLevel.name },
            { rank: 5, name: 'Content Creator', points: 1200, level: 'Neural Strategist' },
          ].map((user, index) => (
            <div
              key={index}
              className={`flex items-center justify-between p-3 rounded-lg ${
                user.name === 'You' ? 'bg-purple-50 border border-purple-200' : 'bg-gray-50'
              }`}
            >
              <div className="flex items-center">
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-200 mr-3">
                  {user.rank <= 3 ? (
                    <Trophy className="w-4 h-4 text-yellow-500" />
                  ) : (
                    <span className="text-sm font-medium text-gray-600">{user.rank}</span>
                  )}
                </div>
                <div>
                  <div className="font-medium text-gray-900">{user.name}</div>
                  <div className="text-sm text-gray-500">{user.level}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="font-medium text-gray-900">{user.points}</div>
                <div className="text-sm text-gray-500">points</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

