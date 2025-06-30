"""
Configuration management for Dr. Clivi agents
"""

import os
from typing import Optional
from pydantic import BaseSettings


class AgentSettings(BaseSettings):
    """Agent-specific configuration"""
    model: str = "gemini-2.5-flash"
    coordinator_model: str = "gemini-2.5-pro"
    name: str = "dr_clivi_coordinator"
    temperature: float = 0.7
    max_tokens: int = 8192


class GoogleCloudSettings(BaseSettings):
    """Google Cloud configuration"""
    project_id: Optional[str] = None
    location: str = "us-central1"
    use_vertex_ai: bool = True
    storage_bucket: Optional[str] = None

    class Config:
        env_prefix = "GOOGLE_CLOUD_"


class TwilioSettings(BaseSettings):
    """Twilio/WhatsApp configuration"""
    account_sid: Optional[str] = None
    auth_token: Optional[str] = None
    whatsapp_number: Optional[str] = None

    class Config:
        env_prefix = "TWILIO_"


class A2ASettings(BaseSettings):
    """A2A Protocol configuration for agent communication"""
    registry_url: Optional[str] = None
    agent_id: Optional[str] = None
    secret_key: Optional[str] = None

    class Config:
        env_prefix = "A2A_"


class CliviSettings(BaseSettings):
    """Clivi API configuration"""
    api_base_url: Optional[str] = None
    api_key: Optional[str] = None

    class Config:
        env_prefix = "CLIVI_"


class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.agent_settings = AgentSettings()
        self.google_cloud = GoogleCloudSettings()
        self.twilio = TwilioSettings()
        self.a2a = A2ASettings()
        self.clivi = CliviSettings()
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Override with environment variables
        self._load_env_overrides()
    
    def _load_env_overrides(self):
        """Load environment variable overrides"""
        if os.getenv("GOOGLE_CLOUD_PROJECT"):
            self.google_cloud.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if os.getenv("GOOGLE_CLOUD_LOCATION"):
            self.google_cloud.location = os.getenv("GOOGLE_CLOUD_LOCATION")
        if os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET"):
            self.google_cloud.storage_bucket = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
        
        # Override model if specified
        if os.getenv("DEFAULT_MODEL"):
            self.agent_settings.model = os.getenv("DEFAULT_MODEL")
        if os.getenv("COORDINATOR_MODEL"):
            self.agent_settings.coordinator_model = os.getenv("COORDINATOR_MODEL")
