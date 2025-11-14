const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const notificationService = require('../services/notificationService');
const { body, validationResult } = require('express-validator');

// Initialize notification service
notificationService.initialize();

/**
 * @route   POST /api/notifications/send
 * @desc    Send notification to user
 * @access  Private
 */
router.post('/send', auth, [
  body('userId').isMongoId().withMessage('Valid user ID is required'),
  body('type').notEmpty().withMessage('Notification type is required'),
  body('data').isObject().withMessage('Notification data must be an object'),
  body('priority').optional().isIn(['low', 'medium', 'high']).withMessage('Invalid priority')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { userId, type, data, priority = 'medium', channels = ['realtime'] } = req.body;
    
    const notification = notificationService.createNotification(type, data, {
      priority,
      channels,
      source: 'user',
      category: 'user_generated'
    });

    const result = await notificationService.sendNotification(userId, notification);

    res.json({
      success: result.success,
      message: result.success ? 'Notification sent successfully' : 'Failed to send notification',
      data: result
    });
  } catch (error) {
    console.error('Send notification error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to send notification'
    });
  }
});

/**
 * @route   POST /api/notifications/bulk
 * @desc    Send bulk notifications
 * @access  Private
 */
router.post('/bulk', auth, [
  body('userIds').isArray().withMessage('User IDs must be an array'),
  body('type').notEmpty().withMessage('Notification type is required'),
  body('data').isObject().withMessage('Notification data must be an object')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { userIds, type, data, priority = 'medium' } = req.body;
    
    const notification = notificationService.createNotification(type, data, {
      priority,
      source: 'user',
      category: 'bulk'
    });

    const results = await notificationService.sendBulkNotifications(userIds, notification);

    res.json({
      success: true,
      message: 'Bulk notifications sent',
      data: {
        total: results.length,
        successful: results.filter(r => r.success).length,
        failed: results.filter(r => !r.success).length,
        results
      }
    });
  } catch (error) {
    console.error('Send bulk notifications error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to send bulk notifications'
    });
  }
});

/**
 * @route   POST /api/notifications/schedule
 * @desc    Schedule notification
 * @access  Private
 */
router.post('/schedule', auth, [
  body('userId').isMongoId().withMessage('Valid user ID is required'),
  body('type').notEmpty().withMessage('Notification type is required'),
  body('data').isObject().withMessage('Notification data must be an object'),
  body('scheduledAt').isISO8601().withMessage('Valid scheduled date is required')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { userId, type, data, scheduledAt, priority = 'medium' } = req.body;
    
    const notification = notificationService.createNotification(type, data, {
      priority,
      source: 'user',
      category: 'scheduled'
    });

    const scheduledNotification = await notificationService.scheduleNotification(
      userId,
      notification,
      scheduledAt
    );

    res.status(201).json({
      success: true,
      message: 'Notification scheduled successfully',
      data: scheduledNotification
    });
  } catch (error) {
    console.error('Schedule notification error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to schedule notification'
    });
  }
});

/**
 * @route   GET /api/notifications
 * @desc    Get user notifications
 * @access  Private
 */
router.get('/', auth, async (req, res) => {
  try {
    const { limit = 20, offset = 0, unreadOnly = false } = req.query;
    
    const notifications = await notificationService.getUserNotifications(req.user.id, {
      limit: parseInt(limit),
      offset: parseInt(offset),
      unreadOnly: unreadOnly === 'true'
    });

    res.json({
      success: true,
      data: notifications
    });
  } catch (error) {
    console.error('Get notifications error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get notifications'
    });
  }
});

/**
 * @route   PUT /api/notifications/:id/read
 * @desc    Mark notification as read
 * @access  Private
 */
router.put('/:id/read', auth, async (req, res) => {
  try {
    const { id } = req.params;
    await notificationService.markAsRead(req.user.id, id);

    res.json({
      success: true,
      message: 'Notification marked as read'
    });
  } catch (error) {
    console.error('Mark notification as read error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to mark notification as read'
    });
  }
});

/**
 * @route   GET /api/notifications/stats
 * @desc    Get notification statistics
 * @access  Private
 */
router.get('/stats', auth, async (req, res) => {
  try {
    const { timeRange = '30d' } = req.query;
    const stats = await notificationService.getNotificationStats(req.user.id, timeRange);

    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Get notification stats error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get notification statistics'
    });
  }
});

/**
 * @route   POST /api/notifications/preferences
 * @desc    Update notification preferences
 * @access  Private
 */
router.post('/preferences', auth, [
  body('email').optional().isBoolean().withMessage('Email preference must be boolean'),
  body('push').optional().isBoolean().withMessage('Push preference must be boolean'),
  body('sms').optional().isBoolean().withMessage('SMS preference must be boolean'),
  body('marketing').optional().isBoolean().withMessage('Marketing preference must be boolean')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { email, push, sms, marketing } = req.body;
    
    // Update user preferences in database
    const user = await User.findById(req.user.id);
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    if (!user.preferences) {
      user.preferences = {};
    }
    if (!user.preferences.notifications) {
      user.preferences.notifications = {};
    }

    if (email !== undefined) user.preferences.notifications.email = email;
    if (push !== undefined) user.preferences.notifications.push = push;
    if (sms !== undefined) user.preferences.notifications.sms = sms;
    if (marketing !== undefined) user.preferences.notifications.marketing = marketing;

    await user.save();

    res.json({
      success: true,
      message: 'Notification preferences updated successfully',
      data: user.preferences.notifications
    });
  } catch (error) {
    console.error('Update notification preferences error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to update notification preferences'
    });
  }
});

/**
 * @route   GET /api/notifications/preferences
 * @desc    Get notification preferences
 * @access  Private
 */
router.get('/preferences', auth, async (req, res) => {
  try {
    const preferences = await notificationService.getUserPreferences(req.user.id);

    res.json({
      success: true,
      data: preferences
    });
  } catch (error) {
    console.error('Get notification preferences error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get notification preferences'
    });
  }
});

/**
 * @route   POST /api/notifications/test
 * @desc    Send test notification
 * @access  Private
 */
router.post('/test', auth, [
  body('type').notEmpty().withMessage('Notification type is required'),
  body('channels').isArray().withMessage('Channels must be an array')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { type, channels = ['realtime'] } = req.body;
    
    const testNotification = notificationService.createNotification(type, {
      title: 'Test Notification',
      message: 'This is a test notification to verify your notification settings.',
      data: { test: true }
    }, {
      priority: 'medium',
      channels,
      source: 'test',
      category: 'test'
    });

    const result = await notificationService.sendNotification(req.user.id, testNotification);

    res.json({
      success: result.success,
      message: result.success ? 'Test notification sent successfully' : 'Failed to send test notification',
      data: result
    });
  } catch (error) {
    console.error('Send test notification error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to send test notification'
    });
  }
});

/**
 * @route   DELETE /api/notifications/:id
 * @desc    Delete notification
 * @access  Private
 */
router.delete('/:id', auth, async (req, res) => {
  try {
    const { id } = req.params;
    
    // This would delete the notification from database
    // For now, we'll just return success
    res.json({
      success: true,
      message: 'Notification deleted successfully'
    });
  } catch (error) {
    console.error('Delete notification error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to delete notification'
    });
  }
});

/**
 * @route   PUT /api/notifications/read-all
 * @desc    Mark all notifications as read
 * @access  Private
 */
router.put('/read-all', auth, async (req, res) => {
  try {
    // This would mark all notifications as read in database
    // For now, we'll just return success
    res.json({
      success: true,
      message: 'All notifications marked as read'
    });
  } catch (error) {
    console.error('Mark all notifications as read error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to mark all notifications as read'
    });
  }
});

module.exports = router;





