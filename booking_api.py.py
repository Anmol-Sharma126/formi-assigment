import os
import json
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Simulated booking database
bookings = {}

def generate_booking_id():
    """Generate a unique booking ID."""
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "RES" + "".join(random.choices(letters, k=2)) + str(random.randint(1000, 9999))

@app.route('/api/book', methods=['POST'])
def book_reservation():
    """
    Create a new booking reservation.
    
    Request body:
    - location: Restaurant location (Delhi/Bangalore)
    - date: Booking date
    - time: Booking time
    - party_size: Number of people
    - name: Customer name
    - phone: Contact number
    
    Returns:
        JSON response with booking confirmation and ID
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['location', 'date', 'time', 'party_size', 'name', 'phone']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Generate a booking ID
    booking_id = generate_booking_id()
    
    # Store the booking
    bookings[booking_id] = {
        'location': data['location'],
        'date': data['date'],
        'time': data['time'],
        'party_size': data['party_size'],
        'name': data['name'],
        'phone': data['phone'],
        'created_at': datetime.now().isoformat()
    }
    
    # Return booking confirmation
    return jsonify({
        "message": "Reservation created successfully",
        "booking_id": booking_id,
        "details": bookings[booking_id]
    })

@app.route('/api/bookings/<booking_id>', methods=['GET'])
def get_booking(booking_id):
    """
    Retrieve a booking by ID.
    
    Returns:
        JSON response with booking details or error if not found
    """
    if booking_id in bookings:
        return jsonify(bookings[booking_id])
    else:
        return jsonify({"error": "Booking not found"}), 404

@app.route('/api/bookings/<booking_id>', methods=['PUT'])
def modify_booking(booking_id):
    """
    Modify an existing booking.
    
    Request body can contain any of:
    - date: New booking date
    - time: New booking time
    - party_size: New number of people
    
    Returns:
        JSON response with updated booking details
    """
    if booking_id not in bookings:
        return jsonify({"error": "Booking not found"}), 404
    
    data = request.get_json()
    
    # Update available fields
    for field in ['date', 'time', 'party_size']:
        if field in data:
            bookings[booking_id][field] = data[field]
    
    # Add modification timestamp
    bookings[booking_id]['modified_at'] = datetime.now().isoformat()
    
    return jsonify({
        "message": "Reservation updated successfully",
        "booking_id": booking_id,
        "details": bookings[booking_id]
    })

@app.route('/api/bookings/<booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    """
    Cancel a booking.
    
    Returns:
        JSON response confirming cancellation
    """
    if booking_id not in bookings:
        return jsonify({"error": "Booking not found"}), 404
    
    # Store cancellation details before removing
    cancelled_booking = bookings[booking_id]
    cancelled_booking['cancelled_at'] = datetime.now().isoformat()
    
    # Remove from active bookings
    del bookings[booking_id]
    
    return jsonify({
        "message": "Reservation cancelled successfully",
        "booking_id": booking_id,
        "details": cancelled_booking
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "healthy", "message": "Booking API is running"})

if __name__ == '__main__':
    # Create some sample bookings for testing
    sample_booking_id = generate_booking_id()
    bookings[sample_booking_id] = {
        'location': 'Delhi',
        'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
        'time': '19:00',
        'party_size': 4,
        'name': 'Amit Sharma',
        'phone': '+91-9876543210',
        'created_at': datetime.now().isoformat()
    }
    print(f"Created sample booking with ID: {sample_booking_id}")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5002, debug=True)
