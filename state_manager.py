import json
import os
import requests
from typing import Dict, List, Any, Optional

class StateManager:
    """
    Manages conversation states and transitions for a restaurant booking system.
    """
    def __init__(self, states_dir: str, transitions_file: str, knowledge_base_url: str):
        """
        Initialize the state manager with state prompts and transition rules.
        
        Args:
            states_dir: Directory containing state prompt files
            transitions_file: Path to the transitions JSON file
            knowledge_base_url: URL for the knowledge base API
        """
        self.states = self._load_states(states_dir)
        self.transitions = self._load_transitions(transitions_file)
        self.knowledge_base_url = knowledge_base_url
        self.current_state = "welcome_state"
        self.conversation_context = {
            "user_info": {},
            "booking_details": {},
            "current_location": None,
            "entities_collected": [],
            "confirmed_actions": []
        }
    
    def _load_states(self, states_dir: str) -> Dict[str, Dict]:
        """Load all state prompt templates from the specified directory."""
        states = {}
        for filename in os.listdir(states_dir):
            if filename.endswith('.json'):
                with open(os.path.join(states_dir, filename), 'r') as f:
                    state_data = json.load(f)
                    state_name = filename.replace('.json', '')
                    states[state_name] = state_data
        return states
    
    def _load_transitions(self, transitions_file: str) -> List[Dict]:
        """Load transition rules from the specified file."""
        with open(transitions_file, 'r') as f:
            return json.load(f)
    
    def get_knowledge_base_info(self, location: str, query_type: Optional[str] = None) -> Dict:
        """
        Fetch information from the knowledge base API.
        
        Args:
            location: Restaurant location (e.g., "Delhi", "Bangalore")
            query_type: Specific information type to retrieve (optional)
            
        Returns:
            Dictionary containing requested knowledge base information
        """
        params = {'location': location}
        if query_type:
            params['type'] = query_type
            
        try:
            response = requests.get(self.knowledge_base_url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to fetch data: {response.status_code}"}
        except Exception as e:
            return {"error": f"Error accessing knowledge base: {str(e)}"}
    
    def determine_next_state(self, user_input: str) -> str:
        """
        Determine the next state based on current state and user input.
        
        Args:
            user_input: The user's message
            
        Returns:
            Name of the next state
        """
        user_input_lower = user_input.lower()
        
        # Check explicit transitions based on rules
        for transition in self.transitions:
            if transition["current_state"] == self.current_state:
                # Check if any trigger phrases are in the user input
                if "user_input_contains" in transition:
                    for phrase in transition["user_input_contains"]:
                        if phrase.lower() in user_input_lower:
                            return transition["next_state"]
                
                # Check for entity conditions
                if "required_entities" in transition:
                    all_entities_present = all(
                        entity in self.conversation_context["entities_collected"]
                        for entity in transition["required_entities"]
                    )
                    if all_entities_present:
                        return transition["next_state"]
        
        # Default fallback if no transitions match
        return "fallback_state"
    
    def get_current_prompt(self) -> str:
        """
        Get the prompt template for the current state with variables filled in.
        
        Returns:
            The prompt text with variables replaced with actual values
        """
        prompt_template = self.states[self.current_state]["prompt_template"]
        
        # Replace variables in the prompt template with values from context
        filled_prompt = prompt_template
        
        # Replace location-specific information
        if self.conversation_context["current_location"]:
            location = self.conversation_context["current_location"]
            location_info = self.get_knowledge_base_info(location)
            
            if "error" not in location_info:
                # Replace location variables
                filled_prompt = filled_prompt.replace("{location}", location)
                filled_prompt = filled_prompt.replace("{location_address}", location_info.get("location", ""))
                filled_prompt = filled_prompt.replace("{location_timings}", location_info.get("timings", ""))
                filled_prompt = filled_prompt.replace("{location_contact}", location_info.get("contact", ""))
        
        # Replace user information
        user_info = self.conversation_context["user_info"]
        for key, value in user_info.items():
            filled_prompt = filled_prompt.replace(f"{{{key}}}", str(value))
        
        # Replace booking details
        booking_details = self.conversation_context["booking_details"]
        for key, value in booking_details.items():
            filled_prompt = filled_prompt.replace(f"{{{key}}}", str(value))
            
        return filled_prompt
    
    def update_context(self, entities: Dict[str, Any]) -> None:
        """
        Update the conversation context with extracted entities.
        
        Args:
            entities: Dictionary of entity names and values extracted from user input
        """
        # Update user information
        if "name" in entities:
            self.conversation_context["user_info"]["name"] = entities["name"]
            self.conversation_context["entities_collected"].append("name")
            
        if "phone" in entities:
            self.conversation_context["user_info"]["phone"] = entities["phone"]
            self.conversation_context["entities_collected"].append("phone")
        
        # Update booking details
        if "location" in entities:
            self.conversation_context["current_location"] = entities["location"]
            self.conversation_context["booking_details"]["location"] = entities["location"]
            self.conversation_context["entities_collected"].append("location")
            
        if "date" in entities:
            self.conversation_context["booking_details"]["date"] = entities["date"]
            self.conversation_context["entities_collected"].append("date")
            
        if "time" in entities:
            self.conversation_context["booking_details"]["time"] = entities["time"]
            self.conversation_context["entities_collected"].append("time")
            
        if "party_size" in entities:
            self.conversation_context["booking_details"]["party_size"] = entities["party_size"]
            self.conversation_context["entities_collected"].append("party_size")
            
        if "booking_id" in entities:
            self.conversation_context["booking_details"]["booking_id"] = entities["booking_id"]
            self.conversation_context["entities_collected"].append("booking_id")
            
        if "request_type" in entities:
            self.conversation_context["booking_details"]["request_type"] = entities["request_type"]
            self.conversation_context["entities_collected"].append("request_type")
    
    def process_user_input(self, user_input: str) -> str:
        """
        Process user input and generate a response.
        
        Args:
            user_input: The user's message
            
        Returns:
            Agent's response based on the current state
        """
        # Extract entities from user input (simplified implementation)
        entities = self._extract_entities(user_input)
        
        # Update conversation context with extracted entities
        self.update_context(entities)
        
        # Determine the next state
        next_state = self.determine_next_state(user_input)
        self.current_state = next_state
        
        # Get the response based on the new state
        return self.get_current_prompt()
    
    def _extract_entities(self, user_input: str) -> Dict[str, Any]:
        """
        Extract entities from user input.
        
        This is a simplified implementation. In a production system,
        this would use NLU (Natural Language Understanding) to extract entities.
        
        Args:
            user_input: The user's message
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        user_input_lower = user_input.lower()
        
        # Simple keyword-based entity extraction
        # Location detection
        if "delhi" in user_input_lower:
            entities["location"] = "Delhi"
        elif "bangalore" in user_input_lower or "bengaluru" in user_input_lower:
            entities["location"] = "Bangalore"
            
        # Date detection (very simplified)
        if "today" in user_input_lower:
            entities["date"] = "today"
        elif "tomorrow" in user_input_lower:
            entities["date"] = "tomorrow"
            
        # Time detection (very simplified)
        if "lunch" in user_input_lower:
            entities["time"] = "lunch"
        elif "dinner" in user_input_lower:
            entities["time"] = "dinner"
        
        # Party size detection
        for i in range(1, 11):
            if f"{i} people" in user_input_lower or f"{i} person" in user_input_lower:
                entities["party_size"] = i
                break
        
        # Request type detection
        if "book" in user_input_lower or "reserve" in user_input_lower:
            entities["request_type"] = "booking"
        elif "cancel" in user_input_lower:
            entities["request_type"] = "cancellation"
        elif "modify" in user_input_lower or "change" in user_input_lower or "update" in user_input_lower:
            entities["request_type"] = "modification"
        
        # In a real implementation, you would use regex or NLU for more complex entities
        # like booking IDs, names, phone numbers, etc.
        
        return entities
