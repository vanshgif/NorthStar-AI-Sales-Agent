import json
from typing import Optional

from groq import Groq
from pydantic import BaseModel, Field

from .config import GROQ_API_KEY


# ---------------------------------------------------------
# Groq client
# ---------------------------------------------------------

client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "qwen/qwen3.6-27b"


# ---------------------------------------------------------
# Structured lead extraction model
# ---------------------------------------------------------

class LeadExtraction(BaseModel):
    customer_name: Optional[str] = None
    language_used: Optional[str] = None
    budget_mentioned: Optional[str] = None
    configuration_interest: Optional[str] = None
    purpose: Optional[str] = None
    timeline: Optional[str] = None
    current_location: Optional[str] = None
    interest_level: Optional[str] = None

    objections_raised: list[str] = Field(default_factory=list)

    follow_up_required: bool = False
    follow_up_preference: Optional[str] = None

    opt_out_requested: bool = False
    escalation_needed: bool = False

    site_visit_requested: bool = False
    requested_site_visit_slot: Optional[str] = None


# ---------------------------------------------------------
# Initial lead state
# ---------------------------------------------------------

def create_lead_state():
    return {
        "customer_name": None,
        "language_used": None,
        "budget_mentioned": None,
        "configuration_interest": None,
        "purpose": None,
        "timeline": None,
        "current_location": None,
        "interest_level": None,

        "objections_raised": [],

        "site_visit_status": "not_offered",
        "site_visit_datetime": None,

        "follow_up_required": False,
        "follow_up_preference": None,

        "opt_out_requested": False,
        "escalation_needed": False,

        "site_visit_requested": False,
        "requested_site_visit_slot": None,
    }


# ---------------------------------------------------------
# JSON extraction helper
# ---------------------------------------------------------

def parse_json_response(raw_content: str) -> dict | None:

    if not raw_content:
        return None

    raw_content = raw_content.strip()

    # Remove reasoning blocks if they somehow appear
    if "<think>" in raw_content:

        if "</think>" in raw_content:
            raw_content = raw_content.split(
                "</think>", 1
            )[1].strip()
        else:
            # Reasoning was returned but JSON may be missing
            print("Groq returned incomplete reasoning instead of JSON:")
            print(raw_content)
            return None

    # Remove markdown code fences
    if raw_content.startswith("```"):

        raw_content = raw_content.replace(
            "```json", "", 1
        )

        raw_content = raw_content.replace(
            "```", "", 1
        )

        raw_content = raw_content.strip()

    try:
        return json.loads(raw_content)

    except json.JSONDecodeError:

        # Try to recover JSON surrounded by extra text
        start = raw_content.find("{")
        end = raw_content.rfind("}")

        if start != -1 and end != -1 and end > start:

            json_candidate = raw_content[start:end + 1]

            try:
                return json.loads(json_candidate)

            except json.JSONDecodeError:
                pass

        print("Invalid JSON returned by Groq:")
        print(raw_content)

        return None


# ---------------------------------------------------------
# Lead state updater
# ---------------------------------------------------------

def update_lead_state(
    message: str,
    current_state: dict
) -> dict:

    extraction_prompt = f"""
You are extracting structured CRM information from a
real-estate sales conversation.

Your task is to update the existing lead state using ONLY
information explicitly stated or clearly implied by the
customer's latest message.

CURRENT LEAD STATE:

{json.dumps(current_state, ensure_ascii=False, indent=2)}


LATEST CUSTOMER MESSAGE:

{message}


IMPORTANT RULES:

1. Preserve existing information.

2. Only update a field when the latest customer message
   provides new information about that field.

3. Never invent information.

4. Never remove previously captured information unless the
   customer explicitly corrects it.

5. Do not infer affordability from budget and property price.

6. Do not mark a site visit as booked. Booking is handled
   separately by the application.


PURPOSE:

If the customer says they are buying:

- for themselves
- for their family
- to live in
- for personal use

use:

"self-use"

If the customer says they are buying:

- for investment
- to rent out
- to resell
- to generate returns

use:

"investment"

Otherwise preserve the existing value.


CONFIGURATION:

Use ONLY:

"2BHK"
"3BHK"
"Both"
null


INTEREST LEVEL:

Use ONLY:

"high"
"medium"
"low"
"not interested"
null

Use "high" when the customer demonstrates meaningful
purchase intent such as:

- asking about pricing
- asking about availability
- asking about booking
- asking for a site visit
- providing a preferred site visit time
- seriously discussing purchase requirements

Do not mark a customer as high interest merely because
they provided basic information.


SITE VISITS:

Set:

site_visit_requested = true

when the customer:

- asks to visit the project
- wants to schedule a site visit
- provides a preferred visit time
- asks to book a site visit


requested_site_visit_slot:

Only populate this field when the customer provides
a specific requested slot.

Normalize these known slots as:

"Saturday 11:00"
"Saturday 15:00"
"Sunday 11:00"
"Sunday 15:00"


If the customer asks for a site visit but does not
provide a specific time:

site_visit_requested = true

requested_site_visit_slot = null


Never assume a date or time that the customer did not provide.


OPT OUT:

Set opt_out_requested = true ONLY if the customer clearly
asks to stop receiving communication or follow-ups.


ESCALATION:

Set escalation_needed = true when the customer clearly
requires human assistance or asks to speak with a person.


FOLLOW-UP:

Set follow_up_required = true when the customer explicitly
asks for someone to contact them later or requests a callback.


LANGUAGE:

Identify the language primarily used by the customer.

Possible examples:

"English"
"Hindi"
"Hinglish"

Do not change the language merely because the assistant
used another language.


OBJECTIONS:

Capture genuine customer objections such as:

- price is too high
- location concern
- possession concern
- payment concern
- configuration concern

Do not invent objections.


RETURN FORMAT:

Return ONLY ONE VALID JSON OBJECT.

Do not return markdown.

Do not return code fences.

Do not return explanations.

Do not return reasoning.

Do not write anything before or after the JSON.

The JSON must contain EXACTLY these fields:

{{
    "customer_name": null,
    "language_used": null,
    "budget_mentioned": null,
    "configuration_interest": null,
    "purpose": null,
    "timeline": null,
    "current_location": null,
    "interest_level": null,
    "objections_raised": [],
    "follow_up_required": false,
    "follow_up_preference": null,
    "opt_out_requested": false,
    "escalation_needed": false,
    "site_visit_requested": false,
    "requested_site_visit_slot": null
}}
"""

    # -----------------------------------------------------
    # Ask Groq for structured information
    # -----------------------------------------------------

    response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[
        {
            "role": "system",
            "content": (
                "You are a CRM data extraction system. "
                "Return ONLY one valid JSON object. "
                "Do not output reasoning. "
                "Do not output <think> tags. "
                "Do not output markdown. "
                "Do not output explanations."
            ),
        },
        {
            "role": "user",
            "content": extraction_prompt,
        },
    ],
    reasoning_effort="none",
    temperature=0.0,
    max_completion_tokens=800,
)

    # -----------------------------------------------------
    # Read model output
    # -----------------------------------------------------

    raw_content = response.choices[0].message.content

    extracted_data = parse_json_response(raw_content)

    if extracted_data is None:
        return current_state

    # -----------------------------------------------------
    # Validate using Pydantic
    # -----------------------------------------------------

    try:
        extracted = LeadExtraction.model_validate(extracted_data)

    except Exception as error:
        print("Lead extraction validation failed:")
        print(error)
        print("Received data:")
        print(extracted_data)

        return current_state

    extracted_data = extracted.model_dump()

    # -----------------------------------------------------
    # Merge extracted information into existing state
    # -----------------------------------------------------

    for key, value in extracted_data.items():

        # ---------------------------------------------
        # Objections
        # ---------------------------------------------

        if key == "objections_raised":

            for objection in value:

                if objection not in current_state[key]:
                    current_state[key].append(objection)

        # ---------------------------------------------
        # Boolean fields
        #
        # We don't want false returned by the model
        # to erase a previously captured true value.
        # ---------------------------------------------

        elif key in {
            "follow_up_required",
            "opt_out_requested",
            "escalation_needed",
            "site_visit_requested",
        }:

            if value is True:
                current_state[key] = True

        # ---------------------------------------------
        # Normal fields
        # ---------------------------------------------

        elif value is not None:
            current_state[key] = value

    return current_state