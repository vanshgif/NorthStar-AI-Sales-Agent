from pathlib import Path

from groq import Groq

from .config import GROQ_API_KEY


# ---------------------------------------------------------
# Groq client
# ---------------------------------------------------------

client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "qwen/qwen3.6-27b"


# ---------------------------------------------------------
# Load Northstar system prompt
# ---------------------------------------------------------

PROMPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "prompts"
    / "system_prompt.md"
)

with open(PROMPT_PATH, "r", encoding="utf-8") as file:
    SYSTEM_PROMPT = file.read()


# ---------------------------------------------------------
# Generate conversational response
# ---------------------------------------------------------

def generate_response(
    message: str,
    history: list,
    booking_request: dict | None = None,
) -> str:

    messages = []

    # -----------------------------------------------------
    # Base system prompt
    # -----------------------------------------------------

    system_prompt = SYSTEM_PROMPT

    # -----------------------------------------------------
    # Application booking result
    # -----------------------------------------------------

    if booking_request is not None:

        if booking_request["success"]:

            system_prompt += f"""

APPLICATION BOOKING RESULT:

The application has already checked the requested
site-visit slot and successfully booked it.

BOOKING STATUS: BOOKED

BOOKING SLOT:
{booking_request["slot"]}

This is an authoritative application result.

Tell the customer that the site visit has been successfully
booked.

DO NOT:
- ask for confirmation again
- ask whether they still want the visit
- say you are checking availability
- say the booking is pending
- offer another slot

The booking is already confirmed.

Keep the response short, warm, and natural.
"""

        else:

            system_prompt += f"""

APPLICATION BOOKING RESULT:

The application checked the requested site-visit slot,
but the slot is unavailable.

BOOKING STATUS: UNAVAILABLE

REQUESTED SLOT:
{booking_request["slot"]}

Tell the customer that the requested slot is unavailable.

DO NOT say that the booking succeeded.

Offer to help with another available time.

Keep the response short, warm, and natural.
"""

    else:

        system_prompt += """

APPLICATION BOOKING RESULT:

No booking was performed for this message.

Do not claim that a site visit has been booked.

Only say that a booking is confirmed when the application
explicitly provides BOOKING STATUS: BOOKED.
"""


    # -----------------------------------------------------
    # System message
    # -----------------------------------------------------

    messages.append({
        "role": "system",
        "content": system_prompt,
    })


    # -----------------------------------------------------
    # Conversation history
    # -----------------------------------------------------

    for item in history:

        role = item["role"]

        # Convert our internal "model" role if present.
        if role == "model":
            role = "assistant"

        messages.append({
            "role": role,
            "content": item["content"],
        })


    # -----------------------------------------------------
    # Current customer message
    # -----------------------------------------------------

    messages.append({
        "role": "user",
        "content": message,
    })


    # -----------------------------------------------------
    # Groq request
    # -----------------------------------------------------

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,

        # Qwen 3.6 non-thinking mode is better suited
        # to this conversational sales agent.
        reasoning_effort="none",

        temperature=0.7,
        max_completion_tokens=300,
    )


    # -----------------------------------------------------
    # Get final response
    # -----------------------------------------------------

    result = response.choices[0].message.content


    if not result:
        print("WARNING: Groq returned empty content.")
        print("Groq message:", response.choices[0].message)

        return (
            "I'm sorry, I'm having trouble responding right now. "
            "Please try again."
        )


    result = result.strip()


    # -----------------------------------------------------
    # Safety cleanup
    # -----------------------------------------------------

    # If reasoning somehow appears despite non-thinking mode,
    # never expose it to the customer.

    if "<think>" in result:

        result = result.split("<think>", 1)[0].strip()


    if "</think>" in result:

        result = result.split("</think>", 1)[1].strip()


    return result