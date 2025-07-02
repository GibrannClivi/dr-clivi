"""
Main coordinator agent for Dr. Clivi
Routes conversations between Diabetes and Obesity specialized flows
"""

import logging
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from .config import Config
from .prompts import COORDINATOR_INSTRUCTION, GLOBAL_INSTRUCTION
from .flows.agents import diabetes_flow_agent, obesity_flow_agent
from .tools.whatsapp_tools import send_whatsapp_message, get_user_context
from .tools.clivi_tools import get_patient_info, update_patient_record

# Configure logging
logger = logging.getLogger(__name__)

# Load configuration
configs = Config()

# Coordinator Agent - Routes conversations to specialized flows
coordinator_agent = LlmAgent(
    name="dr_clivi_coordinator",
    model=configs.coordinator_agent.model,
    description=(
        "Main coordinator for Dr. Clivi healthcare assistant. "
        "Routes WhatsApp conversations to specialized Diabetes or Obesity flows "
        "based on user intent and medical context."
    ),
    instruction=COORDINATOR_INSTRUCTION,
    global_instruction=GLOBAL_INSTRUCTION,
    tools=[
        # Direct tools for coordinator
        send_whatsapp_message,
        get_user_context,
        get_patient_info,
        update_patient_record,
        # Sub-agent tools for flow routing
        AgentTool(agent=diabetes_flow_agent),
        AgentTool(agent=obesity_flow_agent),
    ],
)

# Export the main agent
root_agent = coordinator_agent
