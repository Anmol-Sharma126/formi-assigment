import os
import requests
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration
KNOWLEDGE_BASE_API = "http://localhost:5000/api/knowledge-base"
BOOKING_API = "http://localhost:5002/api"
AGENT_API = "http://localhost:5001/api/process"

@app.route('/api/webhook', methods=['POST'])
def webhook_handler():
    """
    Main webhook handler for voice agent.
    
    This endpoint receives the user's message from the telephony service,
    processes it through the agent, and returns the appropriate response.
    
    Request body:
    - user_message: Text of the user's message
    - session_id: Unique session identifier from the telephony service
    
    Returns:
        JSON response with the agent's reply
    """
    data = request.get_json()
    
    if not data or 'user_message' not in data:
        return jsonify({"error": "Missing required parameter: user_message"}), 400
    
    user_message = data['user_message']
    session_id = data.get('session_id', 'default_session')
    
    try:
        # Process user message through the agent
        agent_response = requests.post(
            AGENT_API,
            json={
                "user_input": user_message,
                "session_id": session_id
            }
        )
        
        if agent_response.status_code != 200:
            return jsonify({"error": f"Agent API error: {agent_response.text}"}), 500
        
        agent_data = agent_response.json()
        
        # Check if we need to perform any backend actions based on the current state
        current_state = agent_data.get('current_state')
        
        if current_state == "success_state" and "book" in user_message.lower():
            # Extract booking details from the agent's context and create the booking
            # This is simplified - in a real implementation, we would have more robust data passing
            booking_details = {
                "location": "Delhi",  # Placeholder - would come from agent context
                "date": "2025-05-20",  # Placeholder
                "time": "19:00",       # Placeholder
                "party_size": 4,       # Placeholder
                "name": "Test User",   # Placeholder
                "phone": "+1234567890" # Placeholder
            }
            
            # Make actual booking
            booking_response = requests.post(
                f"{BOOKING_API}/book",
                json=booking_details
            )
            
            if booking_response.status_code == 200:
                booking_data = booking_response.json()
                # Update agent response with booking ID
                agent_data["response"] = agent_data["response"].replace(
                    "{booking_id}", 
                    booking_data.get("booking_id", "UNKNOWN")
                )
        
        # Return the final response
        return jsonify({
            "response": agent_data["response"],
            "session_id": session_id
        })
        
    except Exception as e:
        return jsonify({"error": f"Error processing webhook: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "healthy", "message": "Webhook service is running"})

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5003, debug=True)
