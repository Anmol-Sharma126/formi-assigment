import os
from state_manager import StateManager  # Assuming StateManager is defined in state_manager.py
from flask import Flask, request, jsonify

app = Flask(__name__)

# Initialize the state manager
state_manager = StateManager(
    states_dir="states",
    transitions_file="data/transitions.json",
    knowledge_base_url="http://localhost:5000/api/knowledge-base"
)

@app.route('/api/process', methods=['POST'])
def process_input():
    """
    Process user input and generate response based on current state.
    
    Request body:
    - user_input: The user's message
    - session_id: Optional session identifier
    
    Returns:
        JSON response with the agent's response and current state
    """
    data = request.get_json()
    
    if not data or 'user_input' not in data:
        return jsonify({"error": "Missing required parameter: user_input"}), 400
    
    user_input = data['user_input']
    session_id = data.get('session_id', 'default_session')
    
    # Process the user input
    response = state_manager.process_user_input(user_input)
    
    return jsonify({
        "response": response,
        "current_state": state_manager.current_state,
        "session_id": session_id
    })

@app.route('/api/reset', methods=['POST'])
def reset_session():
    """
    Reset the conversation state.
    
    Returns:
        JSON response confirming the reset
    """
    # Reset the state manager to initial state
    state_manager.current_state = "welcome_state"
    state_manager.conversation_context = {
        "user_info": {},
        "booking_details": {},
        "current_location": None,
        "entities_collected": [],
        "confirmed_actions": []
    }
    
    return jsonify({
        "message": "Session reset successfully",
        "current_state": state_manager.current_state
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "healthy", "message": "Agent API is running"})

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('states', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5001, debug=True)
