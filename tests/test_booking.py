from backend.booking import book_site_visit


def test_successful_booking():
    result = book_site_visit("Saturday 11:00")

    assert result["success"] is True
    assert result["slot"] == "Saturday 11:00"


def test_failed_booking():
    result = book_site_visit("Saturday 15:00")

    assert result["success"] is False
    assert result["slot"] == "Saturday 15:00"