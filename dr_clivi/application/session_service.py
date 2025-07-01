"""
Session Management Service
Handles user sessions, conversation state, and flow management
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json

from ..core.interfaces import ISessionService, SessionId, PatientId
from ..core.exceptions import ValidationError


logger = logging.getLogger(__name__)


@dataclass
class ConversationState:
    """Represents the current state of a conversation"""
    current_page: str
    previous_page: Optional[str] = None
    context_data: Dict[str, Any] = None
    measurement_in_progress: Optional[Dict[str, Any]] = None
    appointment_in_progress: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.context_data is None:
            self.context_data = {}


@dataclass
class UserSession:
    """Represents a user session with state and context"""
    session_id: str
    patient_id: Optional[str]
    platform: str  # 'whatsapp', 'telegram', etc.
    conversation_state: ConversationState
    created_at: datetime
    last_activity: datetime
    is_active: bool = True
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session has expired"""
        expiry_time = self.last_activity + timedelta(minutes=timeout_minutes)
        return datetime.now() > expiry_time


class SessionService(ISessionService):
    """
    Service for managing user sessions and conversation state
    Handles session lifecycle, state persistence, and flow navigation
    """
    
    def __init__(self, session_timeout_minutes: int = 30):
        self.sessions: Dict[str, UserSession] = {}
        self.session_timeout = session_timeout_minutes
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_session(self, session_id: SessionId, patient_id: Optional[PatientId] = None, 
                      platform: str = "whatsapp") -> UserSession:
        """Create a new user session"""
        conversation_state = ConversationState(current_page="main_menu")
        
        session = UserSession(
            session_id=session_id.value,
            patient_id=patient_id.value if patient_id else None,
            platform=platform,
            conversation_state=conversation_state,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        self.sessions[session_id.value] = session
        self.logger.info(f"Created session {session_id.value} for platform {platform}")
        return session
    
    def get_session(self, session_id: SessionId) -> Optional[UserSession]:
        """Get existing session by ID"""
        session = self.sessions.get(session_id.value)
        
        if session and session.is_expired(self.session_timeout):
            self.logger.info(f"Session {session_id.value} expired, removing")
            self.end_session(session_id)
            return None
        
        if session:
            session.update_activity()
        
        return session
    
    def get_or_create_session(self, session_id: SessionId, patient_id: Optional[PatientId] = None,
                             platform: str = "whatsapp") -> UserSession:
        """Get existing session or create new one"""
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(session_id, patient_id, platform)
        return session
    
    def update_session_state(self, session_id: SessionId, 
                           current_page: str,
                           context_data: Optional[Dict[str, Any]] = None) -> bool:
        """Update session conversation state"""
        session = self.get_session(session_id)
        if not session:
            self.logger.warning(f"Attempted to update non-existent session {session_id.value}")
            return False
        
        # Store previous page for navigation
        session.conversation_state.previous_page = session.conversation_state.current_page
        session.conversation_state.current_page = current_page
        
        # Update context data
        if context_data:
            session.conversation_state.context_data.update(context_data)
        
        session.update_activity()
        self.logger.debug(f"Updated session {session_id.value} state to page: {current_page}")
        return True
    
    def set_measurement_in_progress(self, session_id: SessionId, 
                                  measurement_type: str,
                                  measurement_data: Dict[str, Any]) -> bool:
        """Set measurement data for multi-step measurement flow"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.conversation_state.measurement_in_progress = {
            'type': measurement_type,
            'data': measurement_data,
            'started_at': datetime.now().isoformat()
        }
        
        session.update_activity()
        self.logger.debug(f"Set measurement in progress for session {session_id.value}: {measurement_type}")
        return True
    
    def get_measurement_in_progress(self, session_id: SessionId) -> Optional[Dict[str, Any]]:
        """Get current measurement in progress"""
        session = self.get_session(session_id)
        if not session:
            return None
        return session.conversation_state.measurement_in_progress
    
    def clear_measurement_in_progress(self, session_id: SessionId) -> bool:
        """Clear measurement in progress"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.conversation_state.measurement_in_progress = None
        session.update_activity()
        return True
    
    def set_appointment_in_progress(self, session_id: SessionId,
                                  appointment_data: Dict[str, Any]) -> bool:
        """Set appointment data for multi-step appointment flow"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.conversation_state.appointment_in_progress = {
            'data': appointment_data,
            'started_at': datetime.now().isoformat()
        }
        
        session.update_activity()
        self.logger.debug(f"Set appointment in progress for session {session_id.value}")
        return True
    
    def get_appointment_in_progress(self, session_id: SessionId) -> Optional[Dict[str, Any]]:
        """Get current appointment in progress"""
        session = self.get_session(session_id)
        if not session:
            return None
        return session.conversation_state.appointment_in_progress
    
    def clear_appointment_in_progress(self, session_id: SessionId) -> bool:
        """Clear appointment in progress"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.conversation_state.appointment_in_progress = None
        session.update_activity()
        return True
    
    def end_session(self, session_id: SessionId) -> bool:
        """End and remove session"""
        if session_id.value in self.sessions:
            del self.sessions[session_id.value]
            self.logger.info(f"Ended session {session_id.value}")
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        expired_sessions = []
        for session_id, session in self.sessions.items():
            if session.is_expired(self.session_timeout):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len([s for s in self.sessions.values() if not s.is_expired(self.session_timeout)])
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        active_sessions = [s for s in self.sessions.values() if not s.is_expired(self.session_timeout)]
        
        platforms = {}
        for session in active_sessions:
            platform = session.platform
            platforms[platform] = platforms.get(platform, 0) + 1
        
        return {
            'total_sessions': len(self.sessions),
            'active_sessions': len(active_sessions),
            'expired_sessions': len(self.sessions) - len(active_sessions),
            'platforms': platforms,
            'session_timeout_minutes': self.session_timeout
        }
