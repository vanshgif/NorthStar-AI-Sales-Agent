from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4

from .booking import book_site_visit
from .agent import generate_response
from .state import create_lead_state, update_lead_state
from .analytics import generate_analytics


app = FastAPI(title="Northstar Homes AI Sales Agent")


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# In-memory conversation storage
# ---------------------------------------------------------

sessions = {}


# ---------------------------------------------------------
# Request models
# ---------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class BookingRequest(BaseModel):
    session_id: str
    slot: str


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Northstar AI Sales Agent backend is running",
    }


# ---------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    # -----------------------------------------------------
    # 1. Create or retrieve session
    # -----------------------------------------------------

    session_id = request.session_id or str(uuid4())

    if session_id not in sessions:

        sessions[session_id] = {
            "history": [],
            "lead_state": create_lead_state(),
        }

    session = sessions[session_id]

    history = session["history"]
    lead_state = session["lead_state"]


    # -----------------------------------------------------
    # 2. Extract lead information
    # -----------------------------------------------------

    lead_state = update_lead_state(
        message=request.message,
        current_state=lead_state,
    )

    session["lead_state"] = lead_state


    # -----------------------------------------------------
    # 3. Check for automatic site-visit booking
    # -----------------------------------------------------

    booking_result = None

    if (
        lead_state["site_visit_requested"]
        and lead_state["requested_site_visit_slot"]
        and lead_state["site_visit_status"] != "booked"
    ):

        requested_slot = lead_state[
            "requested_site_visit_slot"
        ]

        booking_result = book_site_visit(requested_slot)


        # -------------------------------------------------
        # Successful booking
        # -------------------------------------------------

        if booking_result["success"]:

            lead_state["site_visit_status"] = "booked"

            lead_state["site_visit_datetime"] = (
                booking_result["slot"]
            )


        # -------------------------------------------------
        # Failed booking
        # -------------------------------------------------

        else:

            lead_state["site_visit_status"] = (
                "attempted_failed"
            )

            lead_state["site_visit_datetime"] = None


        session["lead_state"] = lead_state


    # -----------------------------------------------------
    # 4. Generate conversational response
    # -----------------------------------------------------

    response = generate_response(
        message=request.message,
        history=history,
        booking_request=booking_result,
    )


    # -----------------------------------------------------
    # 5. Store conversation
    # -----------------------------------------------------

    history.append({
        "role": "user",
        "content": request.message,
    })

    history.append({
        "role": "assistant",
        "content": response,
    })


    # -----------------------------------------------------
    # 6. Return result
    # -----------------------------------------------------

    return {
        "session_id": session_id,
        "response": response,
        "lead_state": lead_state,
    }


# ---------------------------------------------------------
# Manual booking endpoint
# ---------------------------------------------------------

@app.post("/book-site-visit")
def book_visit(request: BookingRequest):

    if request.session_id not in sessions:

        return {
            "success": False,
            "message": "Session not found.",
        }

    session = sessions[request.session_id]

    result = book_site_visit(request.slot)


    if result["success"]:

        session["lead_state"]["site_visit_status"] = "booked"

        session["lead_state"]["site_visit_datetime"] = (
            result["slot"]
        )

    else:

        session["lead_state"]["site_visit_status"] = (
            "attempted_failed"
        )

        session["lead_state"]["site_visit_datetime"] = None


    return {
        "success": result["success"],
        "slot": request.slot,
        "message": result["message"],
        "lead_state": session["lead_state"],
    }


# ---------------------------------------------------------
# End conversation / analytics
# ---------------------------------------------------------

@app.post("/end-conversation")
def end_conversation(session_id: str):

    if session_id not in sessions:

        return {
            "success": False,
            "message": "Session not found.",
        }

    session = sessions[session_id]

    analytics = generate_analytics(
        lead_state=session["lead_state"],
        history=session["history"],
    )

    return {
        "success": True,
        "session_id": session_id,
        "analytics": analytics,
    }