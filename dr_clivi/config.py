"""
Configuration management for Dr. Clivi agents
Based on analysis of exported Conversational Agents flows.
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings


class BaseAgentSettings(BaseSettings):
    """Base configuration for all Dr. Clivi agents"""
    model: str = "gemini-2.0-flash-exp"
    temperature: float = 0.3
    max_tokens: int = 8192
    default_language: str = "es"
    timezone: str = "America/Mexico_City"
    session_timeout_minutes: int = 30
    fallback_agent: str = "MASTER_AGENT"  # From no-match analysis
    no_input_timeout_seconds: int = 300  # From no-input analysis


class DiabetesAgentSettings(BaseSettings):
    """Configuration for diabetes specialized agent"""
    name: str = "Dr. Clivi - Diabetes Assistant"
    display_name: str = "Dr. Clivi Diabetes"
    model: str = "gemini-2.0-flash-exp"
    specialization: str = "diabetes_care"
    agent_id: str = "diabetes-agent"
    
    # Supported flows from analysis
    supported_flows: List[str] = [
        "diabetesPlans",
        "glucoseValueLogFasting",
        "glucoseValueLogPostMeal", 
        "tutorialMed",
        "endocrinologyAppointment",
        "measurementsReport"
    ]
    
    # Supported intents from analysis
    supported_intents: List[str] = [
        "keyWordMainMenu",
        "appointments", 
        "measurements",
        "measurementsReport",
        "invoiceLabs",
        "medsGLP",
        "questionType",
        "patientComplaint"
    ]


class ObesityAgentSettings(BaseSettings):
    """Configuration for obesity specialized agent"""
    name: str = "Dr. Clivi - Obesity Assistant"
    display_name: str = "Dr. Clivi Obesidad"
    model: str = "gemini-2.0-flash-exp"
    specialization: str = "obesity_care"
    agent_id: str = "obesity-agent"
    
    # Supported flows from analysis
    supported_flows: List[str] = [
        "obesityPlans",
        "medicationsMenuObesity",
        "nutritionistAppointment",
        "weightTracking",
        "measurementsReport"
    ]
    
    # Supported intents from analysis  
    supported_intents: List[str] = [
        "keyWordMainMenu",
        "appointments",
        "measurements", 
        "measurementsReport",
        "invoiceLabs",
        "medicationsMenu",
        "questionType",
        "patientComplaint"
    ]


class CoordinatorAgentSettings(BaseSettings):
    """Configuration for coordinator agent"""
    name: str = "Dr. Clivi Coordinator"
    display_name: str = "Dr. Clivi"
    model: str = "gemini-2.0-flash-exp"
    agent_id: str = "coordinator-agent"
    
    # Routing logic from checkPlanStatus analysis
    plan_routing_rules: dict = {
        "PRO": {"diabetes": True, "obesity": True},
        "PLUS": {"diabetes": True, "obesity": True},
        "BASIC": {"diabetes": True, "obesity": True},
        "CLUB": {"diabetes": False, "obesity": False, "club_flow": True}
    }
    
    status_routing_rules: dict = {
        "ACTIVE": {"allow_routing": True},
        "SUSPENDED": {"allow_routing": True, "show_warning": True},
        "CANCELED": {"allow_routing": False, "redirect_to": "reactivation_flow"}
    }


class AgentSettings(BaseSettings):
    """Legacy agent-specific configuration for backward compatibility"""
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


class WhatsAppSettings(BaseSettings):
    """WhatsApp Business API configuration"""
    business_access_token: Optional[str] = None
    business_phone_id: Optional[str] = None
    verify_token: Optional[str] = None
    app_secret: Optional[str] = None
    webhook_url: Optional[str] = None

    class Config:
        env_prefix = "WHATSAPP_"


class A2ASettings(BaseSettings):
    """
    A2A Protocol configuration for agent communication
    
    Nota: A2A es un protocolo de comunicación entre agentes, NO requiere API keys.
    Solo necesita configuración de endpoints y puertos para comunicación.
    """
    server_port: int = 8080
    agent_registry_url: Optional[str] = None  # URL de registro de agentes (opcional)
    agent_id: str = "dr-clivi-coordinator"     # ID único de este agente

    class Config:
        env_prefix = "A2A_"


class CliviIntegrationSettings(BaseSettings):
    """
    Clivi Platform Integration Settings
    
    Nota: Clivi no tiene una API unificada formal. La integración se realiza a través de:
    - n8n webhooks para diferentes funcionalidades
    - Base de datos directa (cuando sea necesario)
    - Servicios específicos por funcionalidad
    """
    # n8n webhook base para integraciones
    n8n_webhook_base: str = "https://n8n.clivi.com.mx/webhook"
    
    # URLs específicas para diferentes funcionalidades
    patient_data_source: Optional[str] = None  # Fuente de datos de pacientes
    measurement_storage: Optional[str] = None  # Almacenamiento de mediciones
    appointment_system: Optional[str] = None   # Sistema de citas
    
    # Autenticación (si aplica)
    api_key: Optional[str] = None
    auth_token: Optional[str] = None

    class Config:
        env_prefix = "CLIVI_"


class IntegrationSettings(BaseSettings):
    """External integration settings based on exported agent analysis"""
    
    # Image processing webhook (from photoScalePhoto tool)
    image_recognition_endpoint: str = "https://n8n.clivi.com.mx/webhook/imgfile-measurement-recognition"
    image_processing_timeout: int = 5
    
    # Template messaging (WhatsApp Business API from SEND_MESSAGE tool)
    whatsapp_business_api_url: Optional[str] = None
    whatsapp_business_token: Optional[str] = None
    whatsapp_phone_id: Optional[str] = None
    
    # Generative AI fallback (from MASTER_AGENT routing)
    openai_api_key: Optional[str] = None
    use_vertex_ai_primary: bool = True
    
    # n8n webhook endpoints from analysis
    appointment_webhook: str = "https://n8n.clivi.com.mx/webhook/appointment"
    measurement_webhook: str = "https://n8n.clivi.com.mx/webhook/measurement"
    complaint_webhook: str = "https://n8n.clivi.com.mx/webhook/complaint"
    
    # Session activity tracking
    activity_logging_enabled: bool = True
    activity_webhook: str = "https://n8n.clivi.com.mx/webhook/activity"
    
    class Config:
        env_prefix = "INTEGRATION_"


class FlowSettings(BaseSettings):
    """Flow configuration based on exported flow analysis"""
    
    # Default Start Flow settings
    default_start_intent: str = "keyWordMainMenu"
    enable_plan_status_check: bool = True
    
    # Timeout settings from analysis
    no_input_timeout_seconds: int = 300  # 5 minutes
    session_timeout_minutes: int = 30
    
    # Club plan specific settings
    club_plan_benefits_enabled: bool = True
    club_plan_activities_enabled: bool = True
    
    # Help desk settings
    help_desk_submenu_enabled: bool = True
    technical_support_enabled: bool = True
    billing_support_enabled: bool = True
    
    # Complaint handling
    complaint_max_length: int = 500
    complaint_auto_id_generation: bool = True
    
    class Config:
        env_prefix = "FLOW_"


class Config:
    """Main configuration class with enhanced settings from flow analysis"""
    
    def __init__(self):
        self.base_agent = BaseAgentSettings()
        self.diabetes_agent = DiabetesAgentSettings()
        self.obesity_agent = ObesityAgentSettings()
        self.coordinator_agent = CoordinatorAgentSettings()
        self.google_cloud = GoogleCloudSettings()
        self.whatsapp = WhatsAppSettings()
        self.a2a = A2ASettings()
        self.clivi = CliviIntegrationSettings()
        self.integrations = IntegrationSettings()
        self.flows = FlowSettings()
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
            self.base_agent.model = os.getenv("DEFAULT_MODEL")
        if os.getenv("COORDINATOR_MODEL"):
            self.coordinator_agent.model = os.getenv("COORDINATOR_MODEL")
        
        # Override flow settings
        if os.getenv("SESSION_TIMEOUT_MINUTES"):
            self.flows.session_timeout_minutes = int(os.getenv("SESSION_TIMEOUT_MINUTES"))
        if os.getenv("NO_INPUT_TIMEOUT_SECONDS"):
            self.flows.no_input_timeout_seconds = int(os.getenv("NO_INPUT_TIMEOUT_SECONDS"))
    
    def get_agent_config(self, agent_type: str):
        """Get configuration for specific agent type"""
        agent_configs = {
            "diabetes": self.diabetes_agent,
            "obesity": self.obesity_agent,
            "coordinator": self.coordinator_agent
        }
        return agent_configs.get(agent_type, self.base_agent)
    
    def is_flow_enabled(self, flow_name: str) -> bool:
        """Check if a specific flow is enabled"""
        flow_settings = {
            "help_desk_submenu": self.flows.help_desk_submenu_enabled,
            "technical_support": self.flows.technical_support_enabled,
            "billing_support": self.flows.billing_support_enabled,
            "club_plan_benefits": self.flows.club_plan_benefits_enabled,
            "club_plan_activities": self.flows.club_plan_activities_enabled
        }
        return flow_settings.get(flow_name, True)
    
    def get_routing_rules(self, plan: str, status: str) -> dict:
        """Get routing rules for specific plan and status combination"""
        plan_rules = self.coordinator_agent.plan_routing_rules.get(plan, {})
        status_rules = self.coordinator_agent.status_routing_rules.get(status, {})
        
        return {
            "plan_rules": plan_rules,
            "status_rules": status_rules,
            "allow_routing": status_rules.get("allow_routing", False) and bool(plan_rules)
        }
