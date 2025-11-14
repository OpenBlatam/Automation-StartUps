#!/usr/bin/env python3
"""
ClickUp Brain Collaboration System
=================================

Team collaboration and sharing capabilities with real-time collaboration,
team management, and knowledge sharing features.
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import threading
import time

# Import our systems
from clickup_brain_simple import SimpleClickUpBrainSystem
from clickup_brain_ai_enhanced import EnhancedClickUpBrainSystem
from clickup_brain_security import ClickUpBrainSecuritySystem, User, UserRole

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollaborationType(Enum):
    """Collaboration types"""
    ANALYSIS_SHARING = "analysis_sharing"
    TEAM_WORKSPACE = "team_workspace"
    KNOWLEDGE_BASE = "knowledge_base"
    DISCUSSION_FORUM = "discussion_forum"
    PROJECT_COLLABORATION = "project_collaboration"
    REAL_TIME_EDITING = "real_time_editing"

class SharingPermission(Enum):
    """Sharing permissions"""
    VIEW_ONLY = "view_only"
    COMMENT = "comment"
    EDIT = "edit"
    ADMIN = "admin"

class NotificationType(Enum):
    """Notification types"""
    ANALYSIS_SHARED = "analysis_shared"
    COMMENT_ADDED = "comment_added"
    WORKSPACE_UPDATED = "workspace_updated"
    TEAM_INVITATION = "team_invitation"
    COLLABORATION_REQUEST = "collaboration_request"

@dataclass
class Team:
    """Team data structure"""
    team_id: str
    name: str
    description: str
    owner_id: str
    members: List[str]
    created_at: str
    updated_at: str
    is_active: bool = True
    settings: Dict[str, Any] = None

@dataclass
class Workspace:
    """Workspace data structure"""
    workspace_id: str
    name: str
    description: str
    team_id: str
    owner_id: str
    collaborators: List[str]
    analysis_data: Dict[str, Any]
    created_at: str
    updated_at: str
    is_public: bool = False
    permissions: Dict[str, SharingPermission] = None

@dataclass
class CollaborationSession:
    """Collaboration session data structure"""
    session_id: str
    workspace_id: str
    participants: List[str]
    active_users: List[str]
    started_at: str
    last_activity: str
    session_data: Dict[str, Any]
    is_active: bool = True

@dataclass
class Comment:
    """Comment data structure"""
    comment_id: str
    workspace_id: str
    user_id: str
    content: str
    parent_comment_id: Optional[str]
    created_at: str
    updated_at: str
    is_resolved: bool = False
    mentions: List[str] = None

@dataclass
class Notification:
    """Notification data structure"""
    notification_id: str
    user_id: str
    type: NotificationType
    title: str
    message: str
    data: Dict[str, Any]
    created_at: str
    is_read: bool = False
    priority: str = "normal"

class RealTimeCollaboration:
    """Real-time collaboration engine"""
    
    def __init__(self):
        """Initialize real-time collaboration"""
        self.active_sessions = {}
        self.user_connections = {}
        self.collaboration_events = []
        self.lock = threading.Lock()
    
    def join_session(self, user_id: str, workspace_id: str) -> bool:
        """Join collaboration session"""
        try:
            with self.lock:
                if workspace_id not in self.active_sessions:
                    self.active_sessions[workspace_id] = CollaborationSession(
                        session_id=str(uuid.uuid4()),
                        workspace_id=workspace_id,
                        participants=[],
                        active_users=[],
                        started_at=datetime.now().isoformat(),
                        last_activity=datetime.now().isoformat(),
                        session_data={}
                    )
                
                session = self.active_sessions[workspace_id]
                
                if user_id not in session.participants:
                    session.participants.append(user_id)
                
                if user_id not in session.active_users:
                    session.active_users.append(user_id)
                
                session.last_activity = datetime.now().isoformat()
                
                # Log collaboration event
                self._log_collaboration_event(
                    "user_joined",
                    user_id,
                    workspace_id,
                    {"active_users": len(session.active_users)}
                )
                
                logger.info(f"User {user_id} joined workspace {workspace_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error joining session: {e}")
            return False
    
    def leave_session(self, user_id: str, workspace_id: str) -> bool:
        """Leave collaboration session"""
        try:
            with self.lock:
                if workspace_id in self.active_sessions:
                    session = self.active_sessions[workspace_id]
                    
                    if user_id in session.active_users:
                        session.active_users.remove(user_id)
                    
                    session.last_activity = datetime.now().isoformat()
                    
                    # Log collaboration event
                    self._log_collaboration_event(
                        "user_left",
                        user_id,
                        workspace_id,
                        {"active_users": len(session.active_users)}
                    )
                    
                    logger.info(f"User {user_id} left workspace {workspace_id}")
                    return True
                
        except Exception as e:
            logger.error(f"Error leaving session: {e}")
            return False
    
    def update_workspace(self, user_id: str, workspace_id: str, 
                        updates: Dict[str, Any]) -> bool:
        """Update workspace in real-time"""
        try:
            with self.lock:
                if workspace_id in self.active_sessions:
                    session = self.active_sessions[workspace_id]
                    
                    if user_id in session.active_users:
                        # Apply updates
                        session.session_data.update(updates)
                        session.last_activity = datetime.now().isoformat()
                        
                        # Log collaboration event
                        self._log_collaboration_event(
                            "workspace_updated",
                            user_id,
                            workspace_id,
                            {"updates": list(updates.keys())}
                        )
                        
                        return True
                
        except Exception as e:
            logger.error(f"Error updating workspace: {e}")
            return False
    
    def get_active_users(self, workspace_id: str) -> List[str]:
        """Get active users in workspace"""
        with self.lock:
            if workspace_id in self.active_sessions:
                return self.active_sessions[workspace_id].active_users.copy()
            return []
    
    def _log_collaboration_event(self, event_type: str, user_id: str, 
                               workspace_id: str, data: Dict[str, Any]):
        """Log collaboration event"""
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': event_type,
            'user_id': user_id,
            'workspace_id': workspace_id,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        self.collaboration_events.append(event)
        
        # Keep only last 1000 events
        if len(self.collaboration_events) > 1000:
            self.collaboration_events = self.collaboration_events[-1000:]

class TeamManager:
    """Team management system"""
    
    def __init__(self):
        """Initialize team manager"""
        self.teams = {}
        self.team_memberships = {}
    
    def create_team(self, name: str, description: str, owner_id: str) -> str:
        """Create new team"""
        try:
            team_id = str(uuid.uuid4())
            
            team = Team(
                team_id=team_id,
                name=name,
                description=description,
                owner_id=owner_id,
                members=[owner_id],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                settings={
                    'allow_public_workspaces': False,
                    'require_approval_for_joins': True,
                    'max_members': 50
                }
            )
            
            self.teams[team_id] = team
            self.team_memberships[owner_id] = self.team_memberships.get(owner_id, [])
            self.team_memberships[owner_id].append(team_id)
            
            logger.info(f"Created team: {name} (ID: {team_id})")
            return team_id
            
        except Exception as e:
            logger.error(f"Error creating team: {e}")
            return None
    
    def add_team_member(self, team_id: str, user_id: str, inviter_id: str) -> bool:
        """Add member to team"""
        try:
            if team_id not in self.teams:
                return False
            
            team = self.teams[team_id]
            
            # Check if inviter has permission
            if inviter_id != team.owner_id and inviter_id not in team.members:
                return False
            
            # Check team size limit
            if len(team.members) >= team.settings.get('max_members', 50):
                return False
            
            if user_id not in team.members:
                team.members.append(user_id)
                team.updated_at = datetime.now().isoformat()
                
                self.team_memberships[user_id] = self.team_memberships.get(user_id, [])
                self.team_memberships[user_id].append(team_id)
                
                logger.info(f"Added user {user_id} to team {team_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error adding team member: {e}")
            return False
    
    def remove_team_member(self, team_id: str, user_id: str, remover_id: str) -> bool:
        """Remove member from team"""
        try:
            if team_id not in self.teams:
                return False
            
            team = self.teams[team_id]
            
            # Check if remover has permission
            if remover_id != team.owner_id and remover_id != user_id:
                return False
            
            # Owner cannot be removed
            if user_id == team.owner_id:
                return False
            
            if user_id in team.members:
                team.members.remove(user_id)
                team.updated_at = datetime.now().isoformat()
                
                if user_id in self.team_memberships:
                    self.team_memberships[user_id].remove(team_id)
                
                logger.info(f"Removed user {user_id} from team {team_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing team member: {e}")
            return False
    
    def get_user_teams(self, user_id: str) -> List[Team]:
        """Get teams for user"""
        team_ids = self.team_memberships.get(user_id, [])
        return [self.teams[team_id] for team_id in team_ids if team_id in self.teams]
    
    def get_team_members(self, team_id: str) -> List[str]:
        """Get team members"""
        if team_id in self.teams:
            return self.teams[team_id].members.copy()
        return []

class WorkspaceManager:
    """Workspace management system"""
    
    def __init__(self):
        """Initialize workspace manager"""
        self.workspaces = {}
        self.workspace_permissions = {}
        self.comments = {}
    
    def create_workspace(self, name: str, description: str, team_id: str, 
                        owner_id: str, analysis_data: Dict[str, Any]) -> str:
        """Create new workspace"""
        try:
            workspace_id = str(uuid.uuid4())
            
            workspace = Workspace(
                workspace_id=workspace_id,
                name=name,
                description=description,
                team_id=team_id,
                owner_id=owner_id,
                collaborators=[],
                analysis_data=analysis_data,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                permissions={owner_id: SharingPermission.ADMIN}
            )
            
            self.workspaces[workspace_id] = workspace
            self.comments[workspace_id] = []
            
            logger.info(f"Created workspace: {name} (ID: {workspace_id})")
            return workspace_id
            
        except Exception as e:
            logger.error(f"Error creating workspace: {e}")
            return None
    
    def share_workspace(self, workspace_id: str, user_id: str, 
                       permission: SharingPermission, sharer_id: str) -> bool:
        """Share workspace with user"""
        try:
            if workspace_id not in self.workspaces:
                return False
            
            workspace = self.workspaces[workspace_id]
            
            # Check if sharer has permission
            if sharer_id not in workspace.permissions:
                return False
            
            sharer_permission = workspace.permissions[sharer_id]
            if sharer_permission not in [SharingPermission.ADMIN, SharingPermission.EDIT]:
                return False
            
            # Add user to collaborators
            if user_id not in workspace.collaborators:
                workspace.collaborators.append(user_id)
            
            # Set permission
            workspace.permissions[user_id] = permission
            workspace.updated_at = datetime.now().isoformat()
            
            logger.info(f"Shared workspace {workspace_id} with user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sharing workspace: {e}")
            return False
    
    def add_comment(self, workspace_id: str, user_id: str, content: str, 
                   parent_comment_id: Optional[str] = None) -> str:
        """Add comment to workspace"""
        try:
            if workspace_id not in self.workspaces:
                return None
            
            comment_id = str(uuid.uuid4())
            
            comment = Comment(
                comment_id=comment_id,
                workspace_id=workspace_id,
                user_id=user_id,
                content=content,
                parent_comment_id=parent_comment_id,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            self.comments[workspace_id].append(comment)
            
            # Update workspace
            workspace = self.workspaces[workspace_id]
            workspace.updated_at = datetime.now().isoformat()
            
            logger.info(f"Added comment to workspace {workspace_id}")
            return comment_id
            
        except Exception as e:
            logger.error(f"Error adding comment: {e}")
            return None
    
    def get_workspace_comments(self, workspace_id: str) -> List[Comment]:
        """Get workspace comments"""
        return self.comments.get(workspace_id, [])
    
    def get_user_workspaces(self, user_id: str) -> List[Workspace]:
        """Get workspaces for user"""
        user_workspaces = []
        
        for workspace in self.workspaces.values():
            if (user_id == workspace.owner_id or 
                user_id in workspace.collaborators or
                workspace.is_public):
                user_workspaces.append(workspace)
        
        return user_workspaces

class NotificationManager:
    """Notification management system"""
    
    def __init__(self):
        """Initialize notification manager"""
        self.notifications = {}
        self.user_notifications = {}
    
    def create_notification(self, user_id: str, notification_type: NotificationType,
                          title: str, message: str, data: Dict[str, Any] = None) -> str:
        """Create notification"""
        try:
            notification_id = str(uuid.uuid4())
            
            notification = Notification(
                notification_id=notification_id,
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                data=data or {},
                created_at=datetime.now().isoformat()
            )
            
            # Store notification
            self.notifications[notification_id] = notification
            
            # Add to user notifications
            if user_id not in self.user_notifications:
                self.user_notifications[user_id] = []
            self.user_notifications[user_id].append(notification_id)
            
            logger.info(f"Created notification for user {user_id}: {title}")
            return notification_id
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return None
    
    def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Notification]:
        """Get notifications for user"""
        notification_ids = self.user_notifications.get(user_id, [])
        notifications = []
        
        for notification_id in notification_ids:
            if notification_id in self.notifications:
                notification = self.notifications[notification_id]
                if not unread_only or not notification.is_read:
                    notifications.append(notification)
        
        # Sort by creation time (newest first)
        notifications.sort(key=lambda x: x.created_at, reverse=True)
        return notifications
    
    def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read"""
        try:
            if notification_id in self.notifications:
                notification = self.notifications[notification_id]
                if notification.user_id == user_id:
                    notification.is_read = True
                    return True
            return False
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False

class ClickUpBrainCollaborationSystem:
    """Main collaboration system for ClickUp Brain"""
    
    def __init__(self):
        """Initialize collaboration system"""
        self.team_manager = TeamManager()
        self.workspace_manager = WorkspaceManager()
        self.notification_manager = NotificationManager()
        self.real_time_collaboration = RealTimeCollaboration()
        self.security_system = ClickUpBrainSecuritySystem()
        self.simple_system = SimpleClickUpBrainSystem()
        self.enhanced_system = EnhancedClickUpBrainSystem()
    
    def create_team_workspace(self, team_id: str, name: str, description: str,
                            owner_id: str, directory_path: str = ".") -> str:
        """Create team workspace with analysis"""
        try:
            # Perform analysis
            analysis_results = self.enhanced_system.analyze_with_ai(directory_path, 10)
            
            # Create workspace
            workspace_id = self.workspace_manager.create_workspace(
                name, description, team_id, owner_id, analysis_results
            )
            
            if workspace_id:
                # Notify team members
                team_members = self.team_manager.get_team_members(team_id)
                for member_id in team_members:
                    if member_id != owner_id:
                        self.notification_manager.create_notification(
                            member_id,
                            NotificationType.WORKSPACE_UPDATED,
                            f"New Workspace: {name}",
                            f"{owner_id} created a new workspace in your team",
                            {"workspace_id": workspace_id, "team_id": team_id}
                        )
                
                logger.info(f"Created team workspace: {name}")
            
            return workspace_id
            
        except Exception as e:
            logger.error(f"Error creating team workspace: {e}")
            return None
    
    def share_analysis(self, workspace_id: str, user_id: str, 
                      permission: SharingPermission, sharer_id: str) -> bool:
        """Share analysis workspace"""
        try:
            success = self.workspace_manager.share_workspace(
                workspace_id, user_id, permission, sharer_id
            )
            
            if success:
                # Create notification
                self.notification_manager.create_notification(
                    user_id,
                    NotificationType.ANALYSIS_SHARED,
                    "Analysis Shared",
                    f"{sharer_id} shared an analysis with you",
                    {"workspace_id": workspace_id, "permission": permission.value}
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Error sharing analysis: {e}")
            return False
    
    def add_workspace_comment(self, workspace_id: str, user_id: str, 
                            content: str, parent_comment_id: str = None) -> str:
        """Add comment to workspace"""
        try:
            comment_id = self.workspace_manager.add_comment(
                workspace_id, user_id, content, parent_comment_id
            )
            
            if comment_id:
                # Notify workspace collaborators
                workspace = self.workspace_manager.workspaces.get(workspace_id)
                if workspace:
                    for collaborator_id in workspace.collaborators:
                        if collaborator_id != user_id:
                            self.notification_manager.create_notification(
                                collaborator_id,
                                NotificationType.COMMENT_ADDED,
                                "New Comment",
                                f"{user_id} added a comment to the workspace",
                                {"workspace_id": workspace_id, "comment_id": comment_id}
                            )
            
            return comment_id
            
        except Exception as e:
            logger.error(f"Error adding comment: {e}")
            return None
    
    def get_collaboration_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get collaboration dashboard data"""
        try:
            # Get user teams
            user_teams = self.team_manager.get_user_teams(user_id)
            
            # Get user workspaces
            user_workspaces = self.workspace_manager.get_user_workspaces(user_id)
            
            # Get notifications
            notifications = self.notification_manager.get_user_notifications(user_id, unread_only=True)
            
            # Get active collaboration sessions
            active_sessions = []
            for workspace in user_workspaces:
                active_users = self.real_time_collaboration.get_active_users(workspace.workspace_id)
                if active_users:
                    active_sessions.append({
                        'workspace_id': workspace.workspace_id,
                        'workspace_name': workspace.name,
                        'active_users': active_users
                    })
            
            return {
                'user_id': user_id,
                'teams': [asdict(team) for team in user_teams],
                'workspaces': [asdict(workspace) for workspace in user_workspaces],
                'notifications': [asdict(notification) for notification in notifications],
                'active_sessions': active_sessions,
                'collaboration_stats': {
                    'total_teams': len(user_teams),
                    'total_workspaces': len(user_workspaces),
                    'unread_notifications': len(notifications),
                    'active_collaborations': len(active_sessions)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting collaboration dashboard: {e}")
            return {}
    
    def get_workspace_details(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Get detailed workspace information"""
        try:
            if workspace_id not in self.workspace_manager.workspaces:
                return {}
            
            workspace = self.workspace_manager.workspaces[workspace_id]
            
            # Check user access
            if (user_id != workspace.owner_id and 
                user_id not in workspace.collaborators and 
                not workspace.is_public):
                return {}
            
            # Get comments
            comments = self.workspace_manager.get_workspace_comments(workspace_id)
            
            # Get active users
            active_users = self.real_time_collaboration.get_active_users(workspace_id)
            
            return {
                'workspace': asdict(workspace),
                'comments': [asdict(comment) for comment in comments],
                'active_users': active_users,
                'user_permission': workspace.permissions.get(user_id, SharingPermission.VIEW_ONLY).value
            }
            
        except Exception as e:
            logger.error(f"Error getting workspace details: {e}")
            return {}
    
    def get_collaboration_status(self) -> Dict[str, Any]:
        """Get collaboration system status"""
        return {
            'total_teams': len(self.team_manager.teams),
            'total_workspaces': len(self.workspace_manager.workspaces),
            'total_notifications': len(self.notification_manager.notifications),
            'active_sessions': len(self.real_time_collaboration.active_sessions),
            'total_comments': sum(len(comments) for comments in self.workspace_manager.comments.values()),
            'collaboration_events': len(self.real_time_collaboration.collaboration_events)
        }

def main():
    """Main function for testing"""
    print("👥 ClickUp Brain Collaboration System")
    print("=" * 50)
    
    # Initialize collaboration system
    collaboration_system = ClickUpBrainCollaborationSystem()
    
    print("👥 Collaboration Features:")
    print("  • Team management and workspaces")
    print("  • Real-time collaboration")
    print("  • Analysis sharing and commenting")
    print("  • Notification system")
    print("  • Knowledge base and discussions")
    print("  • Project collaboration tools")
    
    print(f"\n📊 Collaboration Status:")
    status = collaboration_system.get_collaboration_status()
    print(f"  • Total Teams: {status['total_teams']}")
    print(f"  • Total Workspaces: {status['total_workspaces']}")
    print(f"  • Total Notifications: {status['total_notifications']}")
    print(f"  • Active Sessions: {status['active_sessions']}")
    print(f"  • Total Comments: {status['total_comments']}")
    
    # Test team creation
    print(f"\n🏢 Testing Team Creation:")
    team_id = collaboration_system.team_manager.create_team(
        "Test Team", "A test team for collaboration", "user_001"
    )
    print(f"  • Team Created: {'✅' if team_id else '❌'}")
    
    if team_id:
        # Test workspace creation
        print(f"\n📁 Testing Workspace Creation:")
        workspace_id = collaboration_system.create_team_workspace(
            team_id, "Test Workspace", "A test workspace", "user_001"
        )
        print(f"  • Workspace Created: {'✅' if workspace_id else '❌'}")
        
        if workspace_id:
            # Test commenting
            print(f"\n💬 Testing Comment System:")
            comment_id = collaboration_system.add_workspace_comment(
                workspace_id, "user_002", "This is a test comment"
            )
            print(f"  • Comment Added: {'✅' if comment_id else '❌'}")
            
            # Test real-time collaboration
            print(f"\n🔄 Testing Real-time Collaboration:")
            join_success = collaboration_system.real_time_collaboration.join_session(
                "user_001", workspace_id
            )
            print(f"  • Session Joined: {'✅' if join_success else '❌'}")
            
            # Test dashboard
            print(f"\n📊 Testing Collaboration Dashboard:")
            dashboard = collaboration_system.get_collaboration_dashboard("user_001")
            print(f"  • Dashboard Generated: {'✅' if dashboard else '❌'}")
    
    print(f"\n🎯 Collaboration System Ready!")
    print(f"Features available for team collaboration and knowledge sharing")

if __name__ == "__main__":
    main()










