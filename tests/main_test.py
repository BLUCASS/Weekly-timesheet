import pytest
from fastapi.testclient import TestClient
from main import app
from routers.timesheet import validate_timesheet, has_logged_time, is_within_weekly_limit

client = TestClient(app)


@pytest.fixture
def user_timesheet() -> dict:
    timesheet = {
        "Monday": {"date": "monday", "hours": 5, "minutes": 30},
        "Tuesday": {"date": "tuesday", "hours": 1, "minutes": 45},
        "Wednesday": {"date": "wednesday", "hours": 3, "minutes": 15},
        "Thursday": {"date": "thursday", "hours": 3, "minutes": 0},
        "Friday": {"date": "friday", "hours": 3, "minutes": 0},
        "Saturday": {"date": "saturday", "hours": 0, "minutes": 0},
        "Sunday": {"date": "sunday", "hours": 0, "minutes": 0},
    }
    return timesheet


def valid_payload() -> dict:
    payload = {
        "start_date": "2026-08-10",
        "hours_monday": 8, "minutes_monday": 0,
        "hours_tuesday": 8, "minutes_tuesday": 0,
        "hours_wednesday": 8, "minutes_wednesday": 0,
        "hours_thursday": 8, "minutes_thursday": 0,
        "hours_friday": 8, "minutes_friday": 0,
        "hours_saturday": 0, "minutes_saturday": 0,
        "hours_sunday": 0, "minutes_sunday": 0,
    }
    return payload


def test_form_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "Weekly Timesheet" in response.text


def test_valid_submission_returns_200():
    response = client.post("/submit-timesheet", data=valid_payload())
    assert response.status_code == 200


def test_validate_timesheet(user_timesheet) -> None:
    validate_inputs = validate_timesheet(user_timesheet)
    timesheet = {"Monday": {"date": "monday", "hours": 100, "minutes": 30}}
    validate_inputs_false = validate_timesheet(timesheet)
    assert validate_inputs == True
    assert validate_inputs_false == False

def test_has_logged_hours() -> None:
    final_sum_false = has_logged_time(0, 0)
    assert final_sum_false == False

def test_is_within_weekly_limit():
    huge_amount_of_hours = is_within_weekly_limit(100)
    assert huge_amount_of_hours == False

def test_rejects_over_weekly_limit():
    payload = valid_payload()
    payload["hours_monday"] = 23
    payload["hours_tuesday"] = 23
    payload["hours_wednesday"] = 23
    payload["hours_sunday"] = 23
    response = client.post("/submit-timesheet", data=payload)
    assert response.status_code == 422

def test_rejects_non_monday_start_date():
    payload = valid_payload()
    payload["start_date"] = "2026-08-11"  # a Tuesday
    response = client.post("/submit-timesheet", data=payload)
    assert response.status_code == 422

def test_rejects_all_zero_timesheet():
    payload = valid_payload()
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        payload[f"hours_{day}"] = 0
        payload[f"minutes_{day}"] = 0
    response = client.post("/submit-timesheet", data=payload)
    assert response.status_code == 422


def test_rejects_out_of_range_minutes():
    payload = valid_payload()
    payload["minutes_monday"] = 90
    response = client.post("/submit-timesheet", data=payload)
    assert response.status_code == 422