const mongoose = require('mongoose');
const User = require('../models/User');
const GeneratedContent = require('../models/GeneratedContent');
const ContentTemplate = require('../models/ContentTemplate');
const aiService = require('./advancedAIService');

class CollaborationService {
  constructor() {
    this.activeSessions = new Map();
    this.comments = new Map();
    this.suggestions = new Map();
    this.reviews = new Map();
  }

  /**
   * Create collaborative content session
   */
  async createCollaborationSession(userId, contentId, participants = []) {
    const sessionId = new mongoose.Types.ObjectId().toString();
    
    const session = {
      id: sessionId,
      contentId,
      ownerId: userId,
      participants: [
        { userId, role: 'owner', joinedAt: new Date() },
        ...participants.map(p => ({ userId: p.userId, role: p.role || 'collaborator', joinedAt: new Date() }))
      ],
      status: 'active',
      createdAt: new Date(),
      lastActivity: new Date(),
      settings: {
        allowComments: true,
        allowSuggestions: true,
        allowDirectEdit: false,
        requireApproval: true,
        autoSave: true
      }
    };

    this.activeSessions.set(sessionId, session);
    
    // Notify participants
    await this.notifyParticipants(sessionId, 'session_created');
    
    return session;
  }

  /**
   * Join collaboration session
   */
  async joinSession(sessionId, userId, role = 'collaborator') {
    const session = this.activeSessions.get(sessionId);
    if (!session) {
      throw new Error('Session not found');
    }

    // Check if user is already a participant
    const existingParticipant = session.participants.find(p => p.userId === userId);
    if (existingParticipant) {
      return session;
    }

    // Add new participant
    session.participants.push({
      userId,
      role,
      joinedAt: new Date()
    });

    session.lastActivity = new Date();
    this.activeSessions.set(sessionId, session);

    // Notify other participants
    await this.notifyParticipants(sessionId, 'user_joined', { userId, role });

    return session;
  }

  /**
   * Add comment to content
   */
  async addComment(sessionId, userId, content, position = null) {
    const session = this.activeSessions.get(sessionId);
    if (!session) {
      throw new Error('Session not found');
    }

    const participant = session.participants.find(p => p.userId === userId);
    if (!participant) {
      throw new Error('User not authorized to comment');
    }

    const commentId = new mongoose.Types.ObjectId().toString();
    const comment = {
      id: commentId,
      sessionId,
      userId,
      content,
      position,
      createdAt: new Date(),
      replies: [],
      reactions: {},
      resolved: false,
      resolvedBy: null,
      resolvedAt: null
    };

    this.comments.set(commentId, comment);
    session.lastActivity = new Date();
    this.activeSessions.set(sessionId, session);

    // Notify participants
    await this.notifyParticipants(sessionId, 'comment_added', { commentId, userId });

    return comment;
  }

  /**
   * Reply to comment
   */
  async replyToComment(commentId, userId, content) {
    const comment = this.comments.get(commentId);
    if (!comment) {
      throw new Error('Comment not found');
    }

    const session = this.activeSessions.get(comment.sessionId);
    if (!session) {
      throw new Error('Session not found');
    }

    const participant = session.participants.find(p => p.userId === userId);
    if (!participant) {
      throw new Error('User not authorized to reply');
    }

    const replyId = new mongoose.Types.ObjectId().toString();
    const reply = {
      id: replyId,
      userId,
      content,
      createdAt: new Date(),
      reactions: {}
    };

    comment.replies.push(reply);
    this.comments.set(commentId, comment);

    // Notify participants
    await this.notifyParticipants(comment.sessionId, 'comment_replied', { commentId, replyId, userId });

    return reply;
  }

  /**
   * Add reaction to comment
   */
  async addReaction(commentId, userId, reaction) {
    const comment = this.comments.get(commentId);
    if (!comment) {
      throw new Error('Comment not found');
    }

    if (!comment.reactions[reaction]) {
      comment.reactions[reaction] = [];
    }

    // Remove existing reaction from user
    Object.keys(comment.reactions).forEach(r => {
      comment.reactions[r] = comment.reactions[r].filter(id => id !== userId);
    });

    // Add new reaction
    comment.reactions[reaction].push(userId);
    this.comments.set(commentId, comment);

    return comment.reactions;
  }

  /**
   * Resolve comment
   */
  async resolveComment(commentId, userId) {
    const comment = this.comments.get(commentId);
    if (!comment) {
      throw new Error('Comment not found');
    }

    const session = this.activeSessions.get(comment.sessionId);
    if (!session) {
      throw new Error('Session not found');
    }

    const participant = session.participants.find(p => p.userId === userId);
    if (!participant || participant.role === 'viewer') {
      throw new Error('User not authorized to resolve comments');
    }

    comment.resolved = true;
    comment.resolvedBy = userId;
    comment.resolvedAt = new Date();
    this.comments.set(commentId, comment);

    // Notify participants
    await this.notifyParticipants(comment.sessionId, 'comment_resolved', { commentId, userId });

    return comment;
  }

  /**
   * Suggest content improvement
   */
  async suggestImprovement(sessionId, userId, suggestion) {
    const session = this.activeSessions.get(sessionId);
    if (!session) {
      throw new Error('Session not found');
    }

    const participant = session.participants.find(p => p.userId === userId);
    if (!participant) {
      throw new Error('User not authorized to suggest');
    }

    const suggestionId = new mongoose.Types.ObjectId().toString();
    const suggestionData = {
      id: suggestionId,
      sessionId,
      userId,
      type: suggestion.type, // 'addition', 'deletion', 'modification', 'replacement'
      originalText: suggestion.originalText,
      suggestedText: suggestion.suggestedText,
      position: suggestion.position,
      reason: suggestion.reason,
      createdAt: new Date(),
      status: 'pending', // 'pending', 'accepted', 'rejected'
      reviewedBy: null,
      reviewedAt: null,
      votes: {
        approve: [],
        reject: []
      }
    };

    this.suggestions.set(suggestionId, suggestionData);
    session.lastActivity = new Date();
    this.activeSessions.set(sessionId, session);

    // Notify participants
    await this.notifyParticipants(sessionId, 'suggestion_added', { suggestionId, userId });

    return suggestionData;
  }

  /**
   * Vote on suggestion
   */
  async voteOnSuggestion(suggestionId, userId, vote) {
    const suggestion = this.suggestions.get(suggestionId);
    if (!suggestion) {
      throw new Error('Suggestion not found');
    }

    const session = this.activeSessions.get(suggestion.sessionId);
    if (!session) {
      throw new Error('Session not found');
    }

    const participant = session.participants.find(p => p.userId === userId);
    if (!participant) {
      throw new Error('User not authorized to vote');
    }

    // Remove existing vote
    suggestion.votes.approve = suggestion.votes.approve.filter(id => id !== userId);
    suggestion.votes.reject = suggestion.votes.reject.filter(id => id !== userId);

    // Add new vote
    if (vote === 'approve') {
      suggestion.votes.approve.push(userId);
    } else if (vote === 'reject') {
      suggestion.votes.reject.push(userId);
    }

    this.suggestions.set(suggestionId, suggestion);

    // Check if suggestion should be auto-accepted/rejected
    await this.checkSuggestionConsensus(suggestionId);

    return suggestion;
  }

  /**
   * Check suggestion consensus
   */
  async checkSuggestionConsensus(suggestionId) {
    const suggestion = this.suggestions.get(suggestionId);
    if (!suggestion || suggestion.status !== 'pending') {
      return;
    }

    const session = this.activeSessions.get(suggestion.sessionId);
    const totalVoters = session.participants.filter(p => p.role !== 'viewer').length;
    const totalVotes = suggestion.votes.approve.length + suggestion.votes.reject.length;

    if (totalVotes >= Math.ceil(totalVoters / 2)) {
      const approveRatio = suggestion.votes.approve.length / totalVotes;
      
      if (approveRatio >= 0.6) {
        await this.acceptSuggestion(suggestionId);
      } else if (approveRatio <= 0.4) {
        await this.rejectSuggestion(suggestionId);
      }
    }
  }

  /**
   * Accept suggestion
   */
  async acceptSuggestion(suggestionId) {
    const suggestion = this.suggestions.get(suggestionId);
    if (!suggestion) {
      return;
    }

    suggestion.status = 'accepted';
    suggestion.reviewedAt = new Date();
    this.suggestions.set(suggestionId, suggestion);

    // Apply suggestion to content
    await this.applySuggestionToContent(suggestion);

    // Notify participants
    await this.notifyParticipants(suggestion.sessionId, 'suggestion_accepted', { suggestionId });
  }

  /**
   * Reject suggestion
   */
  async rejectSuggestion(suggestionId) {
    const suggestion = this.suggestions.get(suggestionId);
    if (!suggestion) {
      return;
    }

    suggestion.status = 'rejected';
    suggestion.reviewedAt = new Date();
    this.suggestions.set(suggestionId, suggestion);

    // Notify participants
    await this.notifyParticipants(suggestion.sessionId, 'suggestion_rejected', { suggestionId });
  }

  /**
   * Apply suggestion to content
   */
  async applySuggestionToContent(suggestion) {
    const session = this.activeSessions.get(suggestion.sessionId);
    if (!session) {
      return;
    }

    const content = await GeneratedContent.findById(session.contentId);
    if (!content) {
      return;
    }

    let newContent = content.content;

    switch (suggestion.type) {
      case 'addition':
        newContent = this.insertText(newContent, suggestion.position, suggestion.suggestedText);
        break;
      case 'deletion':
        newContent = this.deleteText(newContent, suggestion.position, suggestion.originalText);
        break;
      case 'modification':
        newContent = this.replaceText(newContent, suggestion.originalText, suggestion.suggestedText);
        break;
      case 'replacement':
        newContent = suggestion.suggestedText;
        break;
    }

    content.content = newContent;
    content.revisions.push({
      content: newContent,
      timestamp: new Date(),
      note: `Applied suggestion: ${suggestion.reason}`,
      appliedBy: suggestion.userId
    });

    await content.save();
  }

  /**
   * Insert text at position
   */
  insertText(content, position, text) {
    if (position === null) {
      return content + text;
    }
    return content.slice(0, position) + text + content.slice(position);
  }

  /**
   * Delete text at position
   */
  deleteText(content, position, text) {
    const startIndex = content.indexOf(text, position);
    if (startIndex === -1) {
      return content;
    }
    return content.slice(0, startIndex) + content.slice(startIndex + text.length);
  }

  /**
   * Replace text
   */
  replaceText(content, originalText, newText) {
    return content.replace(originalText, newText);
  }

  /**
   * Request content review
   */
  async requestReview(sessionId, userId, reviewData) {
    const session = this.activeSessions.get(sessionId);
    if (!session) {
      throw new Error('Session not found');
    }

    const participant = session.participants.find(p => p.userId === userId);
    if (!participant || participant.role === 'viewer') {
      throw new Error('User not authorized to request review');
    }

    const reviewId = new mongoose.Types.ObjectId().toString();
    const review = {
      id: reviewId,
      sessionId,
      requestedBy: userId,
      reviewers: reviewData.reviewers || session.participants.filter(p => p.role === 'owner' || p.role === 'reviewer').map(p => p.userId),
      status: 'pending',
      createdAt: new Date(),
      completedAt: null,
      feedback: [],
      overallRating: null,
      approved: false
    };

    this.reviews.set(reviewId, review);

    // Notify reviewers
    await this.notifyReviewers(reviewId, 'review_requested');

    return review;
  }

  /**
   * Submit review feedback
   */
  async submitReviewFeedback(reviewId, userId, feedback) {
    const review = this.reviews.get(reviewId);
    if (!review) {
      throw new Error('Review not found');
    }

    if (!review.reviewers.includes(userId)) {
      throw new Error('User not authorized to review');
    }

    const feedbackData = {
      userId,
      rating: feedback.rating,
      comments: feedback.comments,
      suggestions: feedback.suggestions || [],
      submittedAt: new Date()
    };

    review.feedback.push(feedbackData);

    // Check if all reviewers have submitted
    if (review.feedback.length >= review.reviewers.length) {
      await this.completeReview(reviewId);
    }

    this.reviews.set(reviewId, review);
    return feedbackData;
  }

  /**
   * Complete review
   */
  async completeReview(reviewId) {
    const review = this.reviews.get(reviewId);
    if (!review) {
      return;
    }

    // Calculate overall rating
    const totalRating = review.feedback.reduce((sum, f) => sum + f.rating, 0);
    review.overallRating = totalRating / review.feedback.length;
    review.approved = review.overallRating >= 4.0;
    review.status = 'completed';
    review.completedAt = new Date();

    this.reviews.set(reviewId, review);

    // Notify participants
    await this.notifyParticipants(review.sessionId, 'review_completed', { reviewId, approved: review.approved });
  }

  /**
   * Get session data
   */
  async getSessionData(sessionId, userId) {
    const session = this.activeSessions.get(sessionId);
    if (!session) {
      throw new Error('Session not found');
    }

    const participant = session.participants.find(p => p.userId === userId);
    if (!participant) {
      throw new Error('User not authorized to view session');
    }

    const content = await GeneratedContent.findById(session.contentId);
    const sessionComments = Array.from(this.comments.values()).filter(c => c.sessionId === sessionId);
    const sessionSuggestions = Array.from(this.suggestions.values()).filter(s => s.sessionId === sessionId);
    const sessionReviews = Array.from(this.reviews.values()).filter(r => r.sessionId === sessionId);

    return {
      session,
      content,
      comments: sessionComments,
      suggestions: sessionSuggestions,
      reviews: sessionReviews,
      participants: await this.getParticipantsData(session.participants)
    };
  }

  /**
   * Get participants data
   */
  async getParticipantsData(participants) {
    const userIds = participants.map(p => p.userId);
    const users = await User.find({ _id: { $in: userIds } }).select('firstName lastName email avatar');
    
    return participants.map(participant => {
      const user = users.find(u => u._id.toString() === participant.userId);
      return {
        ...participant,
        user: user ? {
          id: user._id,
          name: `${user.firstName} ${user.lastName}`,
          email: user.email,
          avatar: user.avatar
        } : null
      };
    });
  }

  /**
   * Notify participants
   */
  async notifyParticipants(sessionId, event, data = {}) {
    const session = this.activeSessions.get(sessionId);
    if (!session) {
      return;
    }

    // This would integrate with WebSocket or push notifications
    // For now, we'll just log the event
    console.log(`Notifying participants of session ${sessionId}:`, event, data);
    
    // In a real implementation, you would:
    // 1. Send WebSocket messages to connected clients
    // 2. Send push notifications to mobile apps
    // 3. Send email notifications for important events
  }

  /**
   * Notify reviewers
   */
  async notifyReviewers(reviewId, event) {
    const review = this.reviews.get(reviewId);
    if (!review) {
      return;
    }

    // This would integrate with notification system
    console.log(`Notifying reviewers of review ${reviewId}:`, event);
  }

  /**
   * Get user collaborations
   */
  async getUserCollaborations(userId) {
    const collaborations = [];

    // Get sessions where user is a participant
    for (const [sessionId, session] of this.activeSessions) {
      const participant = session.participants.find(p => p.userId === userId);
      if (participant) {
        const content = await GeneratedContent.findById(session.contentId);
        collaborations.push({
          sessionId,
          contentId: session.contentId,
          contentTitle: content?.content?.substring(0, 100) + '...',
          role: participant.role,
          status: session.status,
          participantsCount: session.participants.length,
          lastActivity: session.lastActivity,
          createdAt: session.createdAt
        });
      }
    }

    return collaborations.sort((a, b) => new Date(b.lastActivity) - new Date(a.lastActivity));
  }

  /**
   * End collaboration session
   */
  async endSession(sessionId, userId) {
    const session = this.activeSessions.get(sessionId);
    if (!session) {
      throw new Error('Session not found');
    }

    const participant = session.participants.find(p => p.userId === userId);
    if (!participant || participant.role !== 'owner') {
      throw new Error('Only session owner can end the session');
    }

    session.status = 'ended';
    session.endedAt = new Date();
    this.activeSessions.set(sessionId, session);

    // Notify participants
    await this.notifyParticipants(sessionId, 'session_ended');

    return session;
  }

  /**
   * Get collaboration statistics
   */
  async getCollaborationStats(userId) {
    const userSessions = Array.from(this.activeSessions.values())
      .filter(session => session.participants.some(p => p.userId === userId));

    const userComments = Array.from(this.comments.values())
      .filter(comment => comment.userId === userId);

    const userSuggestions = Array.from(this.suggestions.values())
      .filter(suggestion => suggestion.userId === userId);

    const userReviews = Array.from(this.reviews.values())
      .filter(review => review.reviewers.includes(userId));

    return {
      totalSessions: userSessions.length,
      activeSessions: userSessions.filter(s => s.status === 'active').length,
      totalComments: userComments.length,
      totalSuggestions: userSuggestions.length,
      acceptedSuggestions: userSuggestions.filter(s => s.status === 'accepted').length,
      totalReviews: userReviews.length,
      completedReviews: userReviews.filter(r => r.status === 'completed').length,
      averageRating: userReviews
        .filter(r => r.status === 'completed')
        .reduce((sum, r) => sum + r.overallRating, 0) / userReviews.filter(r => r.status === 'completed').length || 0
    };
  }
}

module.exports = new CollaborationService();






