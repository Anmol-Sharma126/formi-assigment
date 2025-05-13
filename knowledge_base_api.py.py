from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Load knowledge base data
with open('data_knowledge_base.json.json', 'r') as f:
    knowledge_base = json.load(f)

@app.route('/api/knowledge-base', methods=['GET'])
def get_knowledge_base():
    """
    API endpoint to retrieve knowledge base information for restaurant locations.
    
    Query parameters:
    - location: The location to get information for (Delhi, Bangalore)
    - type: Optional - specific information type to retrieve (e.g., 'faqs', 'timings')
    
    Returns:
        JSON response with the requested knowledge base information
    """
    location = request.args.get('location')
    query_type = request.args.get('type')
    
    if not location:
        return jsonify({"error": "Location parameter is required"}), 400
    
    if location not in knowledge_base:
        return jsonify({"error": f"Location '{location}' not found in knowledge base"}), 404
    
    # Return specific information type if requested
    if query_type:
        if query_type in knowledge_base[location]:
            return jsonify({query_type: knowledge_base[location][query_type]})
        else:
            return jsonify({"error": f"Information type '{query_type}' not found for location '{location}'"}), 404
    
    # Return all information for the location
    return jsonify(knowledge_base[location])

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "healthy", "message": "Knowledge base API is running"})

if __name__ == '__main__':
    # Ensure the data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Create knowledge base file if it doesn't exist
    if not os.path.exists('data/knowledge_base.json'):
        default_knowledge_base = {
            "Delhi": {
                "location": "Connaught Place, Delhi",
                "timings": "12 PM - 11 PM",
                "specials": "Lunch Buffet, Weekend Offers",
                "contact": "+91-9876543210",
                "faqs": {
                    "veg_options": "Yes, we have a wide variety of vegetarian dishes.",
                    "reservation_required": "Not mandatory, but recommended during weekends."
                }
            },
            "Bangalore": {
                "location": "Koramangala, Bangalore",
                "timings": "12 PM - 10:30 PM",
                "specials": "Live Grill, Happy Hour",
                "contact": "+91-8765432109",
                "faqs": {
                    "parking": "Yes, valet parking is available.",
                    "birthday_celebration": "Yes, we offer a special cake and decorations for birthdays."
                }
            }
        }
        
        with open('data/knowledge_base.json', 'w') as f:
            json.dump(default_knowledge_base, f, indent=2)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
