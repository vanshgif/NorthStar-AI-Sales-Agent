def generate_analytics(lead_state: dict, history: list) -> dict:
    """
    Generate final post-conversation analytics.

    Analytics are derived from the structured lead state
    and conversation history. No additional LLM call is used.
    """

    return {
        # ---------------------------------------------
        # Lead information
        # ---------------------------------------------

        "customer_name": lead_state.get("customer_name"),
        "language_used": lead_state.get("language_used"),
        "budget_mentioned": lead_state.get("budget_mentioned"),
        "configuration_interest": lead_state.get(
            "configuration_interest"
        ),
        "purpose": lead_state.get("purpose"),
        "timeline": lead_state.get("timeline"),
        "current_location": lead_state.get("current_location"),

        # ---------------------------------------------
        # Lead qualification
        # ---------------------------------------------

        "interest_level": lead_state.get("interest_level"),

        "objections_raised": lead_state.get(
            "objections_raised",
            []
        ),

        # ---------------------------------------------
        # Site visit
        # ---------------------------------------------

        "site_visit_status": lead_state.get(
            "site_visit_status",
            "not_offered"
        ),

        "site_visit_datetime": lead_state.get(
            "site_visit_datetime"
        ),

        # ---------------------------------------------
        # Follow-up / escalation
        # ---------------------------------------------

        "follow_up_required": lead_state.get(
            "follow_up_required",
            False
        ),

        "follow_up_preference": lead_state.get(
            "follow_up_preference"
        ),

        "opt_out_requested": lead_state.get(
            "opt_out_requested",
            False
        ),

        "escalation_needed": lead_state.get(
            "escalation_needed",
            False
        ),

        # ---------------------------------------------
        # Conversation metrics
        # ---------------------------------------------

        "conversation_turns": _count_customer_messages(
            history
        ),

        "qualification_completeness": (
            _qualification_completeness(lead_state)
        ),

        "recommended_next_action": (
            _recommended_next_action(lead_state)
        ),

        "conversation_summary": _build_summary(
            lead_state,
            history
        ),
    }


# =========================================================
# Helper functions
# =========================================================

def _count_customer_messages(history: list) -> int:
    """
    Count customer messages in the conversation.
    """

    return sum(
        1
        for item in history
        if item.get("role") == "user"
    )


def _qualification_completeness(lead_state: dict) -> int:
    """
    Calculate how much of the useful lead information
    has been captured.

    Returns a percentage from 0 to 100.
    """

    fields = [
        "customer_name",
        "budget_mentioned",
        "configuration_interest",
        "purpose",
        "timeline",
        "current_location",
    ]

    completed = sum(
        1
        for field in fields
        if lead_state.get(field) is not None
    )

    return round(
        (completed / len(fields)) * 100
    )


def _recommended_next_action(lead_state: dict) -> str:
    """
    Recommend the next action based on the final lead state.
    """

    # Customer explicitly opted out
    if lead_state.get("opt_out_requested"):
        return "No further communication unless requested by the customer."

    # Human escalation required
    if lead_state.get("escalation_needed"):
        return "Escalate the lead to a Northstar Homes team member."

    # Successful site visit
    if lead_state.get("site_visit_status") == "booked":
        slot = lead_state.get("site_visit_datetime")

        if slot:
            return f"Prepare for the booked site visit on {slot}."

        return "Prepare for the booked site visit."

    # Failed booking
    if lead_state.get("site_visit_status") == "attempted_failed":
        return "Follow up with the customer to arrange another site-visit slot."

    # Follow-up explicitly required
    if lead_state.get("follow_up_required"):
        preference = lead_state.get(
            "follow_up_preference"
        )

        if preference:
            return (
                f"Follow up with the customer via "
                f"{preference}."
            )

        return "Follow up with the customer."

    # High-interest lead
    if lead_state.get("interest_level") == "high":
        return "Continue qualification and move the lead toward a site visit."

    # Medium interest
    if lead_state.get("interest_level") == "medium":
        return "Continue qualification and identify the customer's main requirements."

    # Low interest
    if lead_state.get("interest_level") == "low":
        return "Provide relevant information and avoid aggressive follow-up."

    # Default
    return "Continue qualification by gathering the missing lead information."


def _build_summary(
    lead_state: dict,
    history: list
) -> str:
    """
    Create a concise deterministic conversation summary.
    """

    name = (
        lead_state.get("customer_name")
        or "The customer"
    )

    configuration = (
        lead_state.get("configuration_interest")
        or "an unspecified configuration"
    )

    budget = lead_state.get(
        "budget_mentioned"
    )

    purpose = lead_state.get(
        "purpose"
    )

    timeline = lead_state.get(
        "timeline"
    )

    location = lead_state.get(
        "current_location"
    )

    summary = (
        f"{name} is interested in {configuration}"
    )

    if budget:
        summary += (
            f" with a stated budget of {budget}"
        )

    if purpose:
        summary += (
            f" for {purpose}"
        )

    if timeline:
        summary += (
            f", with a timeline of {timeline}"
        )

    if location:
        summary += (
            f", currently based in {location}"
        )

    summary += "."

    # ---------------------------------------------
    # Site visit
    # ---------------------------------------------

    site_visit_status = lead_state.get(
        "site_visit_status",
        "not_offered"
    )

    if site_visit_status == "booked":

        slot = lead_state.get(
            "site_visit_datetime"
        )

        if slot:
            summary += (
                f" A site visit was successfully booked "
                f"for {slot}."
            )
        else:
            summary += (
                " A site visit was successfully booked."
            )

    elif site_visit_status == "attempted_failed":

        summary += (
            " A site visit was attempted, "
            "but the requested slot was unavailable."
        )

    elif lead_state.get(
        "site_visit_requested"
    ):

        summary += (
            " The customer expressed interest "
            "in a site visit."
        )

    # ---------------------------------------------
    # Objections
    # ---------------------------------------------

    objections = lead_state.get(
        "objections_raised",
        []
    )

    if objections:

        summary += (
            " Objections raised: "
            + ", ".join(objections)
            + "."
        )

    # ---------------------------------------------
    # Follow-up
    # ---------------------------------------------

    if lead_state.get(
        "follow_up_required"
    ):

        summary += (
            " Follow-up is required."
        )

    # ---------------------------------------------
    # Opt-out
    # ---------------------------------------------

    if lead_state.get(
        "opt_out_requested"
    ):

        summary += (
            " The customer requested no further communication."
        )

    return summary