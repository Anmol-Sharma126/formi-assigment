# Restaurant Booking Voice Agent

This project implements a state-based conversational agent for restaurant bookings. The agent can handle reservations, modifications, cancellations, and answer questions about restaurant locations in Delhi and Bangalore.

## Architecture Overview

The system consists of the following components:

1. **State Manager**: Manages conversation states and transitions
2. **Knowledge Base API**: Provides information about restaurant locations
3. **Booking API**: Handles reservation creation, modification, and cancellation
4. **Agent API**: Processes user input based on the current state
5. **Webhook Service**: Integrates with telephony services (e.g., Retell AI)

![Architecture Diagram](./architecture.png)

## Components

### State Manager

The State Manager handles the conversation flow using a state machine approach. Each state has:
- A prompt template for generating responses
- Expected user inputs
- Output entities to extract from user messages

State transitions are controlled by rules defined in JSON format, which determine when to move from one state to another based on user input and collected entities.

### Knowledge Base API

Serves information about restaurant locations including:
- Location details (address, timings, contact)
- Frequently asked questions
- Menu highlights
- Special offerings

### Booking API

Manages reservation operations:
- Creating new bookings
- Retrieving booking details
- Modifying existing bookings
- Cancelling bookings

### Agent API

Processes user input through the state manager and generates appropriate responses based on:
- Current conversation state
- Previously collected information
- Extracted entities from user input

### Webhook Service

Provides an integration point for telephony services to interact with the agent system.

## Conversation Flow

The voice agent follows this general flow:

1. **Welcome State**: Greets the user and asks how it can help
2. **Booking State**: Collects reservation details (location, date, time, party size, contact info)
3. **Confirm State**: Verifies collected information before finalizing
4. **Success State**: Confirms the booking was completed successfully
5. **FAQ State**: Answers questions about the restaurant
6. **Location Info State**: Provides details about specific restaurant locations
7. **Menu State**: Shares menu information
8. **Modify State**: Handles reservation modifications
9. **Cancel State**: Processes reservation cancellations
10. **Fallback State**: Handles unrecognized inputs

State transitions follow rules defined in the transitions.json file, with fallback mechanisms to ensure the conversation remains coherent.

## Setup and Running

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Start the Knowledge Base API: `python knowledge_base_api.py`
4. Start the Booking API: `python booking_api.py`
5. Start the Agent API: `python agent_api.py`
6. Start the Webhook Service: `python webhook_service.py`

Each service runs on a different port:
- Knowledge Base API: 5000
- Agent API: 5001
- Booking API: 5002
- Webhook Service: 5003

## Testing the Agent

You can test the agent locally by sending POST requests to the webhook endpoint:

```bash
curl -X POST http://localhost:5003/api/webhook \
  -H "Content-Type: application/json" \
  -d '{"user_message": "I want to book a table", "session_id": "test123"}'
```

## Deployment

For production deployment:
1. Configure appropriate environment variables
2. Set up proper authentication for APIs
3. Deploy each service separately or as a combined application
4. Update API endpoints in configuration to point to deployed services

## Agent Phone Number

If connected with Retell AI: [Placeholder for phone number]

## Knowledge Base API Link

API Endpoint: [Placeholder for hosted API]

## Future Improvements

- Add authentication for API endpoints
- Implement more sophisticated entity extraction using NLU
- Create a dashboard for monitoring conversations
- Add support for more restaurant locations
- Implement multi-language support