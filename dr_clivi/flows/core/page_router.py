"""
Page Router - Handles page transitions and routing logic
Separated from page definitions for better maintainability
"""

import logging
from typing import Any, Dict

from .page_types import RoutingType

logger = logging.getLogger(__name__)


class PageRouter:
    """
    Handles page transitions and routing logic
    Manages navigation between pages according to Dialogflow CX rules
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_page_transitions(self, page_def: Dict[str, Any]) -> Dict[str, Any]:
        """Extract transition routes from page definition"""
        return page_def.get("transition_routes", {})
    
    def handle_page_selection(self, page_name: str, page_def: Dict[str, Any],
                            selection_id: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle user selection within a page
        Returns routing information based on Dialogflow CX transition routes
        """
        transitions = self.get_page_transitions(page_def)
        
        if selection_id not in transitions:
            self.logger.warning(f"Unknown selection '{selection_id}' in page '{page_name}'")
            return {
                "action": "trigger_intelligent_routing",
                "reason": "unknown_selection",
                "selection_id": selection_id,
                "page": page_name,
                "routing_type": RoutingType.INTELLIGENT_ROUTING.value
            }
        
        transition = transitions[selection_id]
        
        result = {
            "action": "page_transition",
            "source_page": page_name,
            "selection_id": selection_id,
            "transition": transition
        }
        
        # Add event logging if defined
        if "event_log" in transition:
            result["event_log"] = {
                "function_name": "ACTIVITY_EVENT_LOG",
                "params": {
                    "eventType": transition["event_log"]
                }
            }
        
        # Determine next action
        if "target_page" in transition:
            result["target_page"] = transition["target_page"]
            result["action"] = "navigate_to_page"
        elif "target_flow" in transition:
            result["target_flow"] = transition["target_flow"]
            result["action"] = "navigate_to_flow"
        elif "function_call" in transition:
            result["function_call"] = transition["function_call"]
            result["function_params"] = transition.get("params", {})
            result["action"] = "execute_function"
        
        # Add parameter updates
        if "set_parameters" in transition:
            result["set_parameters"] = transition["set_parameters"]
        
        # Add fulfillment messages
        if "fulfillment_messages" in transition:
            result["fulfillment_messages"] = transition["fulfillment_messages"]
        
        return result
    
    def validate_page_definition(self, page_name: str, page_def: Dict[str, Any]) -> bool:
        """
        Validate that a page definition is properly structured
        """
        if not isinstance(page_def, dict):
            self.logger.error(f"Page {page_name}: Definition must be a dictionary")
            return False
        
        if "display_name" not in page_def:
            self.logger.error(f"Page {page_name}: Missing display_name")
            return False
        
        if "entry_fulfillment" not in page_def:
            self.logger.error(f"Page {page_name}: Missing entry_fulfillment")
            return False
        
        entry_fulfillment = page_def["entry_fulfillment"]
        if not isinstance(entry_fulfillment, dict):
            self.logger.error(f"Page {page_name}: entry_fulfillment must be a dictionary")
            return False
        
        if "message_type" not in entry_fulfillment:
            self.logger.warning(f"Page {page_name}: Missing message_type, defaulting to text")
        
        # Validate transition routes if present
        if "transition_routes" in page_def:
            transitions = page_def["transition_routes"]
            if not isinstance(transitions, dict):
                self.logger.error(f"Page {page_name}: transition_routes must be a dictionary")
                return False
            
            # Validate each transition
            for route_id, route_def in transitions.items():
                if not self._validate_transition_route(page_name, route_id, route_def):
                    return False
        
        return True
    
    def _validate_transition_route(self, page_name: str, route_id: str, 
                                 route_def: Dict[str, Any]) -> bool:
        """Validate individual transition route"""
        if not isinstance(route_def, dict):
            self.logger.error(f"Page {page_name}, route {route_id}: Route must be a dictionary")
            return False
        
        # Must have at least one target
        targets = ["target_page", "target_flow", "function_call"]
        if not any(target in route_def for target in targets):
            self.logger.error(
                f"Page {page_name}, route {route_id}: Must have at least one of: {targets}"
            )
            return False
        
        return True
