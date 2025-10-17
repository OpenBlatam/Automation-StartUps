const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const collaborationService = require('../services/collaborationService');
const { body, validationResult } = require('express-validator');

/**
 * @route   POST /api/collaboration/session
 * @desc    Create collaboration session
 * @access  Private
 */
router.post('/session', auth, [
  body('contentId').isMongoId().withMessage('Valid content ID is required'),
  body('participants').isArray().withMessage('Participants must be an array')
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

    const { contentId, participants } = req.body;
    const session = await collaborationService.createCollaborationSession(
      req.user.id,
      contentId,
      participants
    );

    res.status(201).json({
      success: true,
      message: 'Collaboration session created successfully',
      data: session
    });
  } catch (error) {
    console.error('Create collaboration session error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to create collaboration session'
    });
  }
});

/**
 * @route   POST /api/collaboration/session/:id/join
 * @desc    Join collaboration session
 * @access  Private
 */
router.post('/session/:id/join', auth, [
  body('role').optional().isIn(['collaborator', 'reviewer', 'viewer']).withMessage('Invalid role')
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

    const { id } = req.params;
    const { role = 'collaborator' } = req.body;

    const session = await collaborationService.joinSession(id, req.user.id, role);

    res.json({
      success: true,
      message: 'Joined collaboration session successfully',
      data: session
    });
  } catch (error) {
    console.error('Join collaboration session error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to join collaboration session'
    });
  }
});

/**
 * @route   GET /api/collaboration/session/:id
 * @desc    Get collaboration session data
 * @access  Private
 */
router.get('/session/:id', auth, async (req, res) => {
  try {
    const { id } = req.params;
    const sessionData = await collaborationService.getSessionData(id, req.user.id);

    res.json({
      success: true,
      data: sessionData
    });
  } catch (error) {
    console.error('Get collaboration session error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get collaboration session'
    });
  }
});

/**
 * @route   POST /api/collaboration/comment
 * @desc    Add comment to content
 * @access  Private
 */
router.post('/comment', auth, [
  body('sessionId').notEmpty().withMessage('Session ID is required'),
  body('content').notEmpty().withMessage('Comment content is required'),
  body('position').optional().isInt().withMessage('Position must be an integer')
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

    const { sessionId, content, position } = req.body;
    const comment = await collaborationService.addComment(
      sessionId,
      req.user.id,
      content,
      position
    );

    res.status(201).json({
      success: true,
      message: 'Comment added successfully',
      data: comment
    });
  } catch (error) {
    console.error('Add comment error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to add comment'
    });
  }
});

/**
 * @route   POST /api/collaboration/comment/:id/reply
 * @desc    Reply to comment
 * @access  Private
 */
router.post('/comment/:id/reply', auth, [
  body('content').notEmpty().withMessage('Reply content is required')
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

    const { id } = req.params;
    const { content } = req.body;

    const reply = await collaborationService.replyToComment(id, req.user.id, content);

    res.status(201).json({
      success: true,
      message: 'Reply added successfully',
      data: reply
    });
  } catch (error) {
    console.error('Reply to comment error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to reply to comment'
    });
  }
});

/**
 * @route   POST /api/collaboration/comment/:id/reaction
 * @desc    Add reaction to comment
 * @access  Private
 */
router.post('/comment/:id/reaction', auth, [
  body('reaction').isIn(['👍', '👎', '❤️', '😂', '😮', '😢', '😡']).withMessage('Invalid reaction')
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

    const { id } = req.params;
    const { reaction } = req.body;

    const reactions = await collaborationService.addReaction(id, req.user.id, reaction);

    res.json({
      success: true,
      message: 'Reaction added successfully',
      data: reactions
    });
  } catch (error) {
    console.error('Add reaction error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to add reaction'
    });
  }
});

/**
 * @route   PUT /api/collaboration/comment/:id/resolve
 * @desc    Resolve comment
 * @access  Private
 */
router.put('/comment/:id/resolve', auth, async (req, res) => {
  try {
    const { id } = req.params;
    const comment = await collaborationService.resolveComment(id, req.user.id);

    res.json({
      success: true,
      message: 'Comment resolved successfully',
      data: comment
    });
  } catch (error) {
    console.error('Resolve comment error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to resolve comment'
    });
  }
});

/**
 * @route   POST /api/collaboration/suggestion
 * @desc    Suggest content improvement
 * @access  Private
 */
router.post('/suggestion', auth, [
  body('sessionId').notEmpty().withMessage('Session ID is required'),
  body('type').isIn(['addition', 'deletion', 'modification', 'replacement']).withMessage('Invalid suggestion type'),
  body('originalText').notEmpty().withMessage('Original text is required'),
  body('suggestedText').notEmpty().withMessage('Suggested text is required'),
  body('reason').notEmpty().withMessage('Reason is required')
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

    const { sessionId, ...suggestion } = req.body;
    const suggestionData = await collaborationService.suggestImprovement(
      sessionId,
      req.user.id,
      suggestion
    );

    res.status(201).json({
      success: true,
      message: 'Suggestion added successfully',
      data: suggestionData
    });
  } catch (error) {
    console.error('Add suggestion error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to add suggestion'
    });
  }
});

/**
 * @route   POST /api/collaboration/suggestion/:id/vote
 * @desc    Vote on suggestion
 * @access  Private
 */
router.post('/suggestion/:id/vote', auth, [
  body('vote').isIn(['approve', 'reject']).withMessage('Invalid vote')
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

    const { id } = req.params;
    const { vote } = req.body;

    const suggestion = await collaborationService.voteOnSuggestion(id, req.user.id, vote);

    res.json({
      success: true,
      message: 'Vote recorded successfully',
      data: suggestion
    });
  } catch (error) {
    console.error('Vote on suggestion error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to vote on suggestion'
    });
  }
});

/**
 * @route   POST /api/collaboration/review
 * @desc    Request content review
 * @access  Private
 */
router.post('/review', auth, [
  body('sessionId').notEmpty().withMessage('Session ID is required'),
  body('reviewers').isArray().withMessage('Reviewers must be an array')
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

    const { sessionId, reviewers } = req.body;
    const review = await collaborationService.requestReview(sessionId, req.user.id, { reviewers });

    res.status(201).json({
      success: true,
      message: 'Review requested successfully',
      data: review
    });
  } catch (error) {
    console.error('Request review error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to request review'
    });
  }
});

/**
 * @route   POST /api/collaboration/review/:id/feedback
 * @desc    Submit review feedback
 * @access  Private
 */
router.post('/review/:id/feedback', auth, [
  body('rating').isInt({ min: 1, max: 5 }).withMessage('Rating must be between 1 and 5'),
  body('comments').notEmpty().withMessage('Comments are required')
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

    const { id } = req.params;
    const { rating, comments, suggestions } = req.body;

    const feedback = await collaborationService.submitReviewFeedback(id, req.user.id, {
      rating,
      comments,
      suggestions
    });

    res.status(201).json({
      success: true,
      message: 'Review feedback submitted successfully',
      data: feedback
    });
  } catch (error) {
    console.error('Submit review feedback error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to submit review feedback'
    });
  }
});

/**
 * @route   GET /api/collaboration/user
 * @desc    Get user collaborations
 * @access  Private
 */
router.get('/user', auth, async (req, res) => {
  try {
    const collaborations = await collaborationService.getUserCollaborations(req.user.id);

    res.json({
      success: true,
      data: collaborations
    });
  } catch (error) {
    console.error('Get user collaborations error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get user collaborations'
    });
  }
});

/**
 * @route   GET /api/collaboration/stats
 * @desc    Get collaboration statistics
 * @access  Private
 */
router.get('/stats', auth, async (req, res) => {
  try {
    const stats = await collaborationService.getCollaborationStats(req.user.id);

    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Get collaboration stats error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to get collaboration statistics'
    });
  }
});

/**
 * @route   PUT /api/collaboration/session/:id/end
 * @desc    End collaboration session
 * @access  Private
 */
router.put('/session/:id/end', auth, async (req, res) => {
  try {
    const { id } = req.params;
    const session = await collaborationService.endSession(id, req.user.id);

    res.json({
      success: true,
      message: 'Collaboration session ended successfully',
      data: session
    });
  } catch (error) {
    console.error('End collaboration session error:', error);
    res.status(500).json({
      success: false,
      message: error.message || 'Failed to end collaboration session'
    });
  }
});

module.exports = router;






