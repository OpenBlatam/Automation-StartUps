import React, { useState, useEffect } from 'react';
import { 
  Bell, 
  X, 
  CheckCircle, 
  AlertTriangle, 
  Info, 
  Zap, 
  Brain,
  TrendingUp,
  Target,
  Award,
  Clock,
  Star
} from 'lucide-react';

interface Notification {
  id: string;
  type: 'SUCCESS' | 'WARNING' | 'INFO' | 'ACHIEVEMENT' | 'CONSCIOUSNESS' | 'INSIGHT';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  actionUrl?: string;
  actionText?: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  category: string;
}

const NOTIFICATION_TYPES = {
  SUCCESS: { icon: CheckCircle, color: 'text-green-500', bgColor: 'bg-green-50', borderColor: 'border-green-200' },
  WARNING: { icon: AlertTriangle, color: 'text-yellow-500', bgColor: 'bg-yellow-50', borderColor: 'border-yellow-200' },
  INFO: { icon: Info, color: 'text-blue-500', bgColor: 'bg-blue-50', borderColor: 'border-blue-200' },
  ACHIEVEMENT: { icon: Award, color: 'text-purple-500', bgColor: 'bg-purple-50', borderColor: 'border-purple-200' },
  CONSCIOUSNESS: { icon: Brain, color: 'text-indigo-500', bgColor: 'bg-indigo-50', borderColor: 'border-indigo-200' },
  INSIGHT: { icon: Zap, color: 'text-orange-500', bgColor: 'bg-orange-50', borderColor: 'border-orange-200' },
};

const PRIORITY_COLORS = {
  LOW: 'text-gray-500',
  MEDIUM: 'text-blue-500',
  HIGH: 'text-orange-500',
  URGENT: 'text-red-500',
};

export const NeuralNotifications: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    loadNotifications();
    // Simulate real-time notifications
    const interval = setInterval(() => {
      generateRandomNotification();
    }, 30000); // Every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const loadNotifications = async () => {
    // Mock data - replace with actual API call
    const mockNotifications: Notification[] = [
      {
        id: '1',
        type: 'ACHIEVEMENT',
        title: 'Achievement Unlocked!',
        message: 'You\'ve reached 50% consciousness level. Keep up the great work!',
        timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
        read: false,
        priority: 'HIGH',
        category: 'Consciousness',
      },
      {
        id: '2',
        type: 'SUCCESS',
        title: 'Content Generated Successfully',
        message: 'Your neural content generation completed with 95% quality score.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60), // 1 hour ago
        read: false,
        priority: 'MEDIUM',
        category: 'Content',
      },
      {
        id: '3',
        type: 'INSIGHT',
        title: 'New Neural Insight Available',
        message: 'AI has identified 3 optimization opportunities for your marketing strategy.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
        read: true,
        priority: 'HIGH',
        category: 'Insights',
        actionUrl: '/neural-insights',
        actionText: 'View Insights',
      },
      {
        id: '4',
        type: 'WARNING',
        title: 'Consciousness Level Dropped',
        message: 'Your consciousness level decreased by 2%. Consider reviewing your recent activities.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4), // 4 hours ago
        read: true,
        priority: 'MEDIUM',
        category: 'Consciousness',
      },
      {
        id: '5',
        type: 'INFO',
        title: 'Weekly Report Ready',
        message: 'Your neural analytics report for this week is now available.',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
        read: true,
        priority: 'LOW',
        category: 'Analytics',
        actionUrl: '/analytics',
        actionText: 'View Report',
      },
    ];

    setNotifications(mockNotifications);
    setUnreadCount(mockNotifications.filter(n => !n.read).length);
  };

  const generateRandomNotification = () => {
    const notificationTypes = ['SUCCESS', 'INFO', 'ACHIEVEMENT', 'CONSCIOUSNESS', 'INSIGHT'] as const;
    const randomType = notificationTypes[Math.floor(Math.random() * notificationTypes.length)];
    
    const notificationTemplates = {
      SUCCESS: [
        { title: 'Content Generated', message: 'Your AI-generated content is ready for review.' },
        { title: 'Campaign Optimized', message: 'Your marketing campaign has been automatically optimized.' },
        { title: 'Insight Applied', message: 'A neural insight has been successfully applied to your strategy.' },
      ],
      INFO: [
        { title: 'New Feature Available', message: 'Check out the latest neural marketing features.' },
        { title: 'Weekly Summary', message: 'Your weekly performance summary is ready.' },
        { title: 'System Update', message: 'The platform has been updated with new AI capabilities.' },
      ],
      ACHIEVEMENT: [
        { title: 'Milestone Reached', message: 'Congratulations! You\'ve reached a new consciousness milestone.' },
        { title: 'Streak Achieved', message: 'You\'ve maintained your daily content generation streak for 7 days!' },
        { title: 'Level Up', message: 'Your neural marketing level has increased!' },
      ],
      CONSCIOUSNESS: [
        { title: 'Consciousness Boost', message: 'Your consciousness level has increased by 3%.' },
        { title: 'Neural Pattern Detected', message: 'AI has detected a new pattern in your marketing behavior.' },
        { title: 'Consciousness Insight', message: 'New insights about your consciousness development are available.' },
      ],
      INSIGHT: [
        { title: 'Optimization Found', message: 'AI has identified a new optimization opportunity.' },
        { title: 'Trend Detected', message: 'A new market trend has been detected in your industry.' },
        { title: 'Prediction Available', message: 'New performance predictions are ready for review.' },
      ],
    };

    const templates = notificationTemplates[randomType];
    const randomTemplate = templates[Math.floor(Math.random() * templates.length)];

    const newNotification: Notification = {
      id: Date.now().toString(),
      type: randomType,
      title: randomTemplate.title,
      message: randomTemplate.message,
      timestamp: new Date(),
      read: false,
      priority: 'MEDIUM',
      category: 'System',
    };

    setNotifications(prev => [newNotification, ...prev]);
    setUnreadCount(prev => prev + 1);
  };

  const markAsRead = (notificationId: string) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === notificationId 
          ? { ...notification, read: true }
          : notification
      )
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notification => ({ ...notification, read: true }))
    );
    setUnreadCount(0);
  };

  const deleteNotification = (notificationId: string) => {
    setNotifications(prev => {
      const notification = prev.find(n => n.id === notificationId);
      if (notification && !notification.read) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
      return prev.filter(n => n.id !== notificationId);
    });
  };

  const formatTimestamp = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  const getNotificationIcon = (type: string) => {
    const notificationType = NOTIFICATION_TYPES[type as keyof typeof NOTIFICATION_TYPES];
    const Icon = notificationType?.icon || Info;
    return <Icon className="w-4 h-4" />;
  };

  const getNotificationColors = (type: string) => {
    const notificationType = NOTIFICATION_TYPES[type as keyof typeof NOTIFICATION_TYPES];
    return {
      iconColor: notificationType?.color || 'text-gray-500',
      bgColor: notificationType?.bgColor || 'bg-gray-50',
      borderColor: notificationType?.borderColor || 'border-gray-200',
    };
  };

  const unreadNotifications = notifications.filter(n => !n.read);

  return (
    <div className="relative">
      {/* Notification Bell */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-purple-500 rounded-md"
      >
        <Bell className="w-6 h-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Panel */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border z-50">
          {/* Header */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
              <div className="flex items-center space-x-2">
                {unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    className="text-sm text-purple-600 hover:text-purple-700"
                  >
                    Mark all read
                  </button>
                )}
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Notifications List */}
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                No notifications yet
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {notifications.map((notification) => {
                  const colors = getNotificationColors(notification.type);
                  return (
                    <div
                      key={notification.id}
                      className={`p-4 hover:bg-gray-50 transition-colors ${
                        !notification.read ? 'bg-blue-50' : ''
                      }`}
                    >
                      <div className="flex items-start">
                        <div className={`p-2 rounded-full ${colors.bgColor} mr-3`}>
                          <div className={colors.iconColor}>
                            {getNotificationIcon(notification.type)}
                          </div>
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h4 className="text-sm font-medium text-gray-900">
                                {notification.title}
                              </h4>
                              <p className="text-sm text-gray-600 mt-1">
                                {notification.message}
                              </p>
                              
                              <div className="flex items-center mt-2 space-x-2">
                                <span className="text-xs text-gray-500">
                                  {formatTimestamp(notification.timestamp)}
                                </span>
                                <span className={`text-xs ${PRIORITY_COLORS[notification.priority]}`}>
                                  {notification.priority}
                                </span>
                                <span className="text-xs text-gray-400">
                                  {notification.category}
                                </span>
                              </div>
                            </div>
                            
                            <div className="flex items-center space-x-1 ml-2">
                              {!notification.read && (
                                <button
                                  onClick={() => markAsRead(notification.id)}
                                  className="text-gray-400 hover:text-gray-600"
                                  title="Mark as read"
                                >
                                  <CheckCircle className="w-4 h-4" />
                                </button>
                              )}
                              <button
                                onClick={() => deleteNotification(notification.id)}
                                className="text-gray-400 hover:text-red-600"
                                title="Delete"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                          
                          {notification.actionUrl && notification.actionText && (
                            <div className="mt-2">
                              <a
                                href={notification.actionUrl}
                                className="text-sm text-purple-600 hover:text-purple-700 font-medium"
                              >
                                {notification.actionText} →
                              </a>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="p-4 border-t border-gray-200">
              <a
                href="/notifications"
                className="text-sm text-purple-600 hover:text-purple-700 font-medium"
              >
                View all notifications →
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

