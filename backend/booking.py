# Mock calendar for the Northstar Homes demo.

MOCK_SLOTS = {
    "Saturday 11:00": True,
    "Saturday 15:00": False,
    "Sunday 11:00": True,
    "Sunday 15:00": True,
}


def check_slot_availability(slot: str) -> bool:
    """
    Check whether a requested mock site-visit slot is available.
    """

    return MOCK_SLOTS.get(slot, False)


def book_site_visit(slot: str) -> dict:
    """
    Simulate booking a Northstar Homes site visit.
    """

    if not check_slot_availability(slot):
        return {
            "success": False,
            "slot": slot,
            "message": (
                f"The requested slot {slot} is unavailable."
            ),
        }

    return {
        "success": True,
        "slot": slot,
        "message": (
            f"Site visit successfully booked for {slot}."
        ),
    }