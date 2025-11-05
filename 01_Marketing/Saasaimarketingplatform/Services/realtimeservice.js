const { Server } = require('socket.io');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const collaborationService = require('./collaborationService');
const automationService = require('./automationService');
const analyticsService = require('./analyticsService');

class RealTimeService {
  constructor() {
    this.io = null;
    this.connectedUsers = new Map();
    this.userSessions = new Map();
    this.roomSessions = new Map();
    this.isInitialized = false;
  }

  /**
   * Initialize real-time service
   */
  initialize(server) {
    if (this.isInitialized) return;

    this.io = new Server(server, {
      cors: {
        origin: process.env.FRONTEND_URL || "http://localhost:3000",
        methods: ["GET", "POST"],
        credentials: true
      },
      transports: ['websocket', 'polling']
    });

    this.setupMiddleware();
    this.setupEventHandlers();
    this.isInitialized = true;
    console.log('Real-time service initialized successfully');
  }

  /**
   * Setup middleware for authentication
   */
  setupMiddleware() {
    this.io.use(async (socket, next) => {
      try {
        const token = socket.handshake.auth.token || socket.handshake.headers.authorization?.split(' ')[1];
        
        if (!token) {
          return next(new Error('Authentication error: No token provided'));
        }

        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        const user = await User.findById(decoded.userId).select('-password');
        
        if (!user || !user.isActive) {
          return next(new Error('Authentication error: User not found or inactive'));
        }

        socket.userId = user._id.toString();
        socket.user = user;
        next();
      } catch (error) {
        next(new Error('Authentication error: Invalid token'));
      }
    });
  }

  /**
   * Setup event handlers
   */
  setupEventHandlers() {
    this.io.on('connection', (socket) => {
      console.log(`User ${socket.userId} connected`);
      
      // Store user connection
      this.connectedUsers.set(socket.userId, socket);
      this.userSessions.set(socket.id, {
        userId: socket.userId,
        user: socket.user,
        connectedAt: new Date(),
        lastActivity: new Date()
      });

      // Handle user events
      this.handleUserEvents(socket);
      
      // Handle collaboration events
      this.handleCollaborationEvents(socket);
      
      // Handle automation events
      this.handleAutomationEvents(socket);
      
      // Handle analytics events
      this.handleAnalyticsEvents(socket);
      
      // Handle typing events
      this.handleTypingEvents(socket);
      
      // Handle presence events
      this.handlePresenceEvents(socket);

      // Handle disconnection
      socket.on('disconnect', () => {
        this.handleDisconnection(socket);
      });
    });
  }

  /**
   * Handle user events
   */
  handleUserEvents(socket) {
    // Join user room for personal notifications
    socket.join(`user:${socket.userId}`);

    // Handle online status
    socket.on('user:online', () => {
      this.broadcastUserStatus(socket.userId, 'online');
    });

    // Handle away status
    socket.on('user:away', () => {
      this.broadcastUserStatus(socket.userId, 'away');
    });

    // Handle busy status
    socket.on('user:busy', () => {
      this.broadcastUserStatus(socket.userId, 'busy');
    });
  }

  /**
   * Handle collaboration events
   */
  handleCollaborationEvents(socket) {
    // Join collaboration session
    socket.on('collaboration:join', async (data) => {
      try {
        const { sessionId } = data;
        await collaborationService.joinSession(sessionId, socket.userId);
        
        socket.join(`collaboration:${sessionId}`);
        socket.currentSession = sessionId;
        
        // Notify other participants
        socket.to(`collaboration:${sessionId}`).emit('collaboration:user_joined', {
          userId: socket.userId,
          user: {
            id: socket.user._id,
            name: `${socket.user.firstName} ${socket.user.lastName}`,
            avatar: socket.user.avatar
          }
        });

        // Send current session state
        const sessionData = await collaborationService.getSessionData(sessionId, socket.userId);
        socket.emit('collaboration:session_data', sessionData);
      } catch (error) {
        socket.emit('collaboration:error', { message: error.message });
      }
    });

    // Leave collaboration session
    socket.on('collaboration:leave', (data) => {
      const { sessionId } = data;
      socket.leave(`collaboration:${sessionId}`);
      socket.currentSession = null;
      
      socket.to(`collaboration:${sessionId}`).emit('collaboration:user_left', {
        userId: socket.userId
      });
    });

    // Add comment
    socket.on('collaboration:add_comment', async (data) => {
      try {
        const { sessionId, content, position } = data;
        const comment = await collaborationService.addComment(sessionId, socket.userId, content, position);
        
        this.io.to(`collaboration:${sessionId}`).emit('collaboration:comment_added', {
          comment,
          user: {
            id: socket.user._id,
            name: `${socket.user.firstName} ${socket.user.lastName}`,
            avatar: socket.user.avatar
          }
        });
      } catch (error) {
        socket.emit('collaboration:error', { message: error.message });
      }
    });

    // Reply to comment
    socket.on('collaboration:reply_comment', async (data) => {
      try {
        const { commentId, content } = data;
        const reply = await collaborationService.replyToComment(commentId, socket.userId, content);
        
        // Find session for this comment
        const comment = collaborationService.comments.get(commentId);
        if (comment) {
          this.io.to(`collaboration:${comment.sessionId}`).emit('collaboration:comment_replied', {
            commentId,
            reply,
            user: {
              id: socket.user._id,
              name: `${socket.user.firstName} ${socket.user.lastName}`,
              avatar: socket.user.avatar
            }
          });
        }
      } catch (error) {
        socket.emit('collaboration:error', { message: error.message });
      }
    });

    // Add reaction
    socket.on('collaboration:add_reaction', async (data) => {
      try {
        const { commentId, reaction } = data;
        const reactions = await collaborationService.addReaction(commentId, socket.userId, reaction);
        
        const comment = collaborationService.comments.get(commentId);
        if (comment) {
          this.io.to(`collaboration:${comment.sessionId}`).emit('collaboration:reaction_added', {
            commentId,
            reactions,
            user: {
              id: socket.user._id,
              name: `${socket.user.firstName} ${socket.user.lastName}`
            }
          });
        }
      } catch (error) {
        socket.emit('collaboration:error', { message: error.message });
      }
    });

    // Suggest improvement
    socket.on('collaboration:suggest_improvement', async (data) => {
      try {
        const { sessionId, suggestion } = data;
        const suggestionData = await collaborationService.suggestImprovement(sessionId, socket.userId, suggestion);
        
        this.io.to(`collaboration:${sessionId}`).emit('collaboration:suggestion_added', {
          suggestion: suggestionData,
          user: {
            id: socket.user._id,
            name: `${socket.user.firstName} ${socket.user.lastName}`,
            avatar: socket.user.avatar
          }
        });
      } catch (error) {
        socket.emit('collaboration:error', { message: error.message });
      }
    });

    // Vote on suggestion
    socket.on('collaboration:vote_suggestion', async (data) => {
      try {
        const { suggestionId, vote } = data;
        const suggestion = await collaborationService.voteOnSuggestion(suggestionId, socket.userId, vote);
        
        const suggestionData = collaborationService.suggestions.get(suggestionId);
        if (suggestionData) {
          this.io.to(`collaboration:${suggestionData.sessionId}`).emit('collaboration:suggestion_voted', {
            suggestionId,
            suggestion,
            user: {
              id: socket.user._id,
              name: `${socket.user.firstName} ${socket.user.lastName}`
            }
          });
        }
      } catch (error) {
        socket.emit('collaboration:error', { message: error.message });
      }
    });
  }

  /**
   * Handle automation events
   */
  handleAutomationEvents(socket) {
    // Join automation room for notifications
    socket.join(`automation:${socket.userId}`);

    // Handle automation status updates
    socket.on('automation:get_status', async () => {
      try {
        const automations = await automationService.getUserAutomations(socket.userId);
        socket.emit('automation:status', automations);
      } catch (error) {
        socket.emit('automation:error', { message: error.message });
      }
    });

    // Handle automation execution
    socket.on('automation:execute', async (data) => {
      try {
        const { automationId } = data;
        await automationService.executeWorkflow(automationId, { userId: socket.userId });
        
        socket.emit('automation:executed', { automationId });
      } catch (error) {
        socket.emit('automation:error', { message: error.message });
      }
    });
  }

  /**
   * Handle analytics events
   */
  handleAnalyticsEvents(socket) {
    // Join analytics room
    socket.join(`analytics:${socket.userId}`);

    // Handle real-time analytics requests
    socket.on('analytics:get_realtime', async (data) => {
      try {
        const { timeRange = '1d' } = data;
        const analytics = await analyticsService.getUserAnalytics(socket.userId, timeRange);
        socket.emit('analytics:realtime_data', analytics);
      } catch (error) {
        socket.emit('analytics:error', { message: error.message });
      }
    });

    // Handle analytics updates
    socket.on('analytics:subscribe_updates', (data) => {
      const { metrics = [] } = data;
      socket.analyticsSubscriptions = metrics;
    });
  }

  /**
   * Handle typing events
   */
  handleTypingEvents(socket) {
    socket.on('typing:start', (data) => {
      const { sessionId, type = 'content' } = data;
      if (sessionId) {
        socket.to(`collaboration:${sessionId}`).emit('typing:start', {
          userId: socket.userId,
          user: {
            id: socket.user._id,
            name: `${socket.user.firstName} ${socket.user.lastName}`,
            avatar: socket.user.avatar
          },
          type
        });
      }
    });

    socket.on('typing:stop', (data) => {
      const { sessionId, type = 'content' } = data;
      if (sessionId) {
        socket.to(`collaboration:${sessionId}`).emit('typing:stop', {
          userId: socket.userId,
          type
        });
      }
    });
  }

  /**
   * Handle presence events
   */
  handlePresenceEvents(socket) {
    // Update user activity
    socket.on('presence:update', (data) => {
      const { status, activity } = data;
      const userSession = this.userSessions.get(socket.id);
      if (userSession) {
        userSession.status = status;
        userSession.activity = activity;
        userSession.lastActivity = new Date();
        this.userSessions.set(socket.id, userSession);
      }
    });

    // Get online users
    socket.on('presence:get_online', (data) => {
      const { sessionId } = data;
      const onlineUsers = this.getOnlineUsersForSession(sessionId);
      socket.emit('presence:online_users', onlineUsers);
    });
  }

  /**
   * Handle disconnection
   */
  handleDisconnection(socket) {
    console.log(`User ${socket.userId} disconnected`);
    
    // Remove from connected users
    this.connectedUsers.delete(socket.userId);
    this.userSessions.delete(socket.id);
    
    // Notify collaboration sessions
    if (socket.currentSession) {
      socket.to(`collaboration:${socket.currentSession}`).emit('collaboration:user_left', {
        userId: socket.userId
      });
    }
    
    // Broadcast offline status
    this.broadcastUserStatus(socket.userId, 'offline');
  }

  /**
   * Broadcast user status
   */
  broadcastUserStatus(userId, status) {
    this.io.emit('user:status_changed', {
      userId,
      status,
      timestamp: new Date()
    });
  }

  /**
   * Get online users for session
   */
  getOnlineUsersForSession(sessionId) {
    const onlineUsers = [];
    
    for (const [socketId, session] of this.userSessions) {
      const socket = this.io.sockets.sockets.get(socketId);
      if (socket && socket.rooms.has(`collaboration:${sessionId}`)) {
        onlineUsers.push({
          userId: session.userId,
          user: {
            id: session.user._id,
            name: `${session.user.firstName} ${session.user.lastName}`,
            avatar: session.user.avatar
          },
          status: session.status || 'online',
          lastActivity: session.lastActivity
        });
      }
    }
    
    return onlineUsers;
  }

  /**
   * Send notification to user
   */
  sendNotificationToUser(userId, notification) {
    const socket = this.connectedUsers.get(userId);
    if (socket) {
      socket.emit('notification', notification);
    }
  }

  /**
   * Send notification to room
   */
  sendNotificationToRoom(room, notification) {
    this.io.to(room).emit('notification', notification);
  }

  /**
   * Broadcast to all users
   */
  broadcast(event, data) {
    this.io.emit(event, data);
  }

  /**
   * Send automation notification
   */
  sendAutomationNotification(userId, type, data) {
    this.sendNotificationToUser(userId, {
      type: 'automation',
      automationType: type,
      data,
      timestamp: new Date()
    });
  }

  /**
   * Send collaboration notification
   */
  sendCollaborationNotification(sessionId, type, data) {
    this.sendNotificationToRoom(`collaboration:${sessionId}`, {
      type: 'collaboration',
      collaborationType: type,
      data,
      timestamp: new Date()
    });
  }

  /**
   * Send analytics update
   */
  sendAnalyticsUpdate(userId, metrics) {
    this.sendNotificationToUser(userId, {
      type: 'analytics',
      metrics,
      timestamp: new Date()
    });
  }

  /**
   * Get connection statistics
   */
  getConnectionStats() {
    return {
      totalConnections: this.connectedUsers.size,
      activeSessions: this.userSessions.size,
      collaborationRooms: this.roomSessions.size,
      uptime: process.uptime()
    };
  }

  /**
   * Get user presence data
   */
  getUserPresence(userId) {
    const socket = this.connectedUsers.get(userId);
    if (!socket) {
      return { status: 'offline' };
    }

    const session = this.userSessions.get(socket.id);
    return {
      status: session?.status || 'online',
      lastActivity: session?.lastActivity,
      connectedAt: session?.connectedAt
    };
  }

  /**
   * Force disconnect user
   */
  forceDisconnectUser(userId) {
    const socket = this.connectedUsers.get(userId);
    if (socket) {
      socket.disconnect(true);
    }
  }

  /**
   * Get room information
   */
  getRoomInfo(room) {
    const sockets = this.io.sockets.adapter.rooms.get(room);
    if (!sockets) {
      return { userCount: 0, users: [] };
    }

    const users = [];
    for (const socketId of sockets) {
      const session = this.userSessions.get(socketId);
      if (session) {
        users.push({
          userId: session.userId,
          user: {
            id: session.user._id,
            name: `${session.user.firstName} ${session.user.lastName}`,
            avatar: session.user.avatar
          }
        });
      }
    }

    return {
      userCount: users.length,
      users
    };
  }

  /**
   * Cleanup inactive sessions
   */
  cleanupInactiveSessions() {
    const now = new Date();
    const inactiveThreshold = 30 * 60 * 1000; // 30 minutes

    for (const [socketId, session] of this.userSessions) {
      if (now - session.lastActivity > inactiveThreshold) {
        const socket = this.io.sockets.sockets.get(socketId);
        if (socket) {
          socket.disconnect(true);
        }
      }
    }
  }

  /**
   * Start cleanup interval
   */
  startCleanupInterval() {
    setInterval(() => {
      this.cleanupInactiveSessions();
    }, 5 * 60 * 1000); // Every 5 minutes
  }
}

module.exports = new RealTimeService();






