# Northstar Homes — AI Sales Agent

An AI-powered conversational sales agent built for the **Huvo AI Forward Deployed Engineer assignment**.

The agent helps customers explore properties, qualify their requirements, handle objections, schedule site visits, and generate structured lead analytics after a conversation.

---

## Live Demo

**Frontend:** https://north-star-ai-sales-agent.vercel.app/

**Backend:** https://northstar-ai-sales-agent.onrender.com/

**API Documentation:** https://northstar-ai-sales-agent.onrender.com/docs#/

---

## Features

- Conversational AI sales assistant
- English, Hindi and Hinglish support
- Conversation memory using session IDs
- Lead qualification and structured lead state
- Customer name, budget and configuration extraction
- Interest-level detection
- Objection handling
- Customer opt-out handling
- Site-visit booking
- Successful and failed booking scenarios
- Human escalation handling
- Post-conversation lead analytics
- Responsive React interface

---

## Architecture

```text
                 React Frontend
                       |
                       | HTTP / JSON
                       v
                 FastAPI Backend
                       |
              +--------+--------+
              |                 |
              v                 v
        Lead State          AI Agent
        Extraction              |
              |                 v
              |          Groq / Qwen
              |
              v
       Booking Logic
              |
              v
       Mock Calendar
              |
              v
        Lead Analytics

The LLM is responsible for conversational responses and structured information extraction, while application code controls actions such as site-visit booking.

This prevents the model from falsely claiming that an action was completed.

Tech Stack
Frontend
React
Vite
JavaScript
CSS
Backend
Python
FastAPI
Pydantic
Uvicorn
AI
Groq API
Qwen qwen/qwen3.6-27b
Custom system prompt
Deployment
Vercel — Frontend
Render — Backend
Testing
Pytest
FastAPI Swagger
Manual end-to-end testing

Project Structure:

NorthStar-AI-Sales-Agent/
│
├── backend/
│   ├── __init__.py
│   ├── agent.py
│   ├── analytics.py
│   ├── booking.py
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   └── state.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── public/
│   ├── package.json
│   └── package-lock.json
│
├── prompts/
│   └── system_prompt.md
│
├── tests/
│   ├── test_booking.py
│   └── README.md
│
├── .env.example
├── .gitignore
├── pytest.ini
└── README.md

How It Works

A typical conversation follows this flow:
Customer Message
       ↓
FastAPI /chat
       ↓
Lead Information Extraction
       ↓
Update Lead State
       ↓
Detect Site Visit Request
       ↓
Check Mock Calendar
       ↓
Book / Reject Requested Slot
       ↓
Generate AI Response
       ↓
Store Conversation History



## When the customer ends the conversation: ##

Conversation History
        +
Lead State
        ↓
Analytics Generation
        ↓
Structured Lead Analytics



Lead Qualification

The system maintains structured information throughout the conversation, including:

Customer name
Language
Budget
Configuration
Purpose
Timeline
Current location
Interest level
Objections
Follow-up requirement
Follow-up preference
Opt-out status
Escalation requirement
Site-visit request
Requested site-visit slot
Site-visit status
Site-visit datetime



Example:

{
  "customer_name": "Rahul",
  "language_used": "English",
  "budget_mentioned": "2 crore",
  "configuration_interest": "3BHK",
  "purpose": null,
  "timeline": null,
  "current_location": null,
  "interest_level": "high",
  "objections_raised": [],
  "site_visit_status": "booked",
  "site_visit_datetime": "Saturday 11:00",
  "follow_up_required": false,
  "follow_up_preference": null,
  "opt_out_requested": false,
  "escalation_needed": false



  Prompt Engineering

The main system prompt is stored in:

prompts/system_prompt.md

The prompt controls:

Conversational tone
Progressive lead qualification
Conversation memory
English/Hindi/Hinglish behaviour
Objection handling
Opt-out handling
Human escalation
Site-visit behaviour
Information safety
Avoiding unsupported claims

The agent is instructed not to invent property information, pricing, availability, discounts, or booking confirmations.

Site Visit Booking

Site visits are simulated using a mock calendar.

Current availability:

Slot	Availability
Saturday 11:00	Available
Saturday 15:00	Unavailable
Sunday 11:00	Available
Sunday 15:00	Available
Successful booking

Customer:

I'd like to visit Saturday at 11 AM.

The application checks the slot and, if available, updates:

site_visit_status = booked
site_visit_datetime = Saturday 11:00

The AI then confirms the successful booking.

Failed booking

Customer:

I'd like to visit Saturday at 3 PM.

The application checks:

Saturday 15:00

and returns unavailable.

The lead state becomes:

site_visit_status = attempted_failed

The agent must not claim that the visit was booked.

Analytics

After the conversation ends, the system generates structured lead analytics.

Analytics include:

Customer name
Language
Budget
Configuration
Purpose
Interest level
Objections
Site-visit status
Site-visit datetime
Follow-up requirement
Escalation requirement
Conversation summary
Qualification completeness
Recommended next action

Example:

{
  "customer_name": "Rahul",
  "budget_mentioned": "2 crore",
  "configuration_interest": "3BHK",
  "interest_level": "high",
  "site_visit_status": "booked",
  "site_visit_datetime": "Saturday 11:00",
  "follow_up_required": false,
  "escalation_needed": false
}
API Endpoints
Health Check
GET /health
Chat
POST /chat

Example:

{
  "message": "Hi, I'm Rahul. I'm looking for a 3 BHK.",
  "session_id": null
}

The API returns a session ID.

Subsequent messages use that session ID:

{
  "message": "My budget is around 2 crore.",
  "session_id": "YOUR-SESSION-ID"
}
Book Site Visit
POST /book-site-visit

Example:

{
  "session_id": "YOUR-SESSION-ID",
  "slot": "Saturday 11:00"
}
End Conversation
POST /end-conversation?session_id=YOUR-SESSION-ID

This generates the final lead analytics.

Running Locally
Backend

From the project root:

python -m venv venv

Windows:

venv\Scripts\activate

Install dependencies:

pip install -r backend/requirements.txt

Create a .env file:

GROQ_API_KEY=your_groq_api_key

Start the backend:

uvicorn backend.main:app --reload

Backend:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs
Frontend
cd frontend
npm install

Create:

frontend/.env

with:

VITE_API_URL=http://127.0.0.1:8000

Run:

npm run dev
Environment Variables

Create .env.example:

GROQ_API_KEY=your_groq_api_key_here

The actual API key must never be committed to GitHub.

For the frontend:

VITE_API_URL=http://127.0.0.1:8000
Test Scenarios
1. Successful Site Visit
Hi, I'm Rahul. I'm looking for a 3 BHK.


My budget is around 2 crore.


I'd like to visit Saturday at 11 AM.

Expected:

customer_name: Rahul
configuration_interest: 3BHK
budget_mentioned: 2 crore
site_visit_status: booked
site_visit_datetime: Saturday 11:00
2. Failed Site Visit
I'd like to visit Saturday at 3 PM.

Expected:

site_visit_status: attempted_failed

The agent must not claim that the visit was booked.

3. Customer Opt-Out
I'm not interested anymore.
Please don't contact me again.

Expected:

opt_out_requested: true

The agent should politely respect the customer's request.

4. Basic Lead Qualification
Hi, I'm Rahul. I'm looking for a 3 BHK.

Expected:

customer_name: Rahul
configuration_interest: 3BHK

The system should not invent budget, purpose, timeline, or location.

5. Conversation Analytics

After completing a conversation:

POST /end-conversation

Expected output includes structured lead information, site-visit status, conversation summary, qualification completeness, and recommended next action.

Assumptions
Site-visit booking uses a mock calendar.
Lead/session data is stored in memory.
Property information is limited to the assignment dataset.
No authentication is implemented.
No production CRM integration is implemented.
API keys are stored using environment variables.
Known Limitations
In-memory sessions are lost when the backend restarts.
Booking is simulated rather than connected to a real calendar.
The property dataset is static.
Analytics are generated for the current conversation rather than persisted in a production database.
The system does not currently include a production CRM or authentication layer.
AI Tools Used
Groq API
Qwen qwen/qwen3.6-27b
Custom system prompt for conversational sales behaviour
LLM-based structured lead extraction

The implementation focuses on prompt quality, agent behaviour, conversation context, lead qualification, and reliable application-level actions.
