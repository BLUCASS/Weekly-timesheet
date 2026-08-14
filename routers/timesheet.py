from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request, Form, HTTPException
from datetime import date, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent # routers/ -> project root

router = APIRouter()
templates = Jinja2Templates(directory=BASE_DIR / "templates")

MAX_MINUTES_PER_DAY = 59
MAX_HOURS_PER_WEEK = 70
MAX_HOURS_PER_DAY = 23

# Sum all the hours and minutes and returns false if they are equal to 0
def has_logged_time(total_hours: int, total_minutes: int) -> bool:
    """
    Return False if the submitted timesheet has no hours logged at all.
    """
    return (total_hours + total_minutes) > 0

# Sum all the minutes and checks if they are under 59
def minutes_dont_exceed(total_minutes: int) -> bool:
    """Return False if the total_minutes is over 59."""
    return total_minutes <= MAX_MINUTES_PER_DAY

# Checks if the number of hours is under 23
def hours_dont_exceed(total_hours: int) -> bool:
    """Return False if the total_hours is over 23."""
    return total_hours <= MAX_HOURS_PER_DAY

# Sum all the hours and checks if they are under the weekly limit
def is_within_weekly_limit(total_hours: int) -> bool:
    """Return False if the week's total exceeds the weekly cap."""
    return total_hours <= MAX_HOURS_PER_WEEK

# This function will validate the user's inputs to check 
# if they are all integer and they are within range
def validate_timesheet(timesheet: dict) -> bool:
    """
    Validate that every day's hours fall within 0-23 and minutes within 0-59.
    Type checking (int vs. non-int) is already enforced by FastAPI's Form(...)
    declarations before this ever runs, so this only needs to check ranges.
    """
    for day in timesheet.items():
        if not hours_dont_exceed(day[1]["hours"]): return False
        if not minutes_dont_exceed(day[1]["minutes"]): return False
    return True

@router.get("/", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
        )

@router.post("/submit-timesheet")
async def submit_timesheet(
    request:Request,
    start_date: date = Form(...),

    hours_monday: int = Form(...),
    minutes_monday: int = Form(...),

    hours_tuesday: int = Form(...),
    minutes_tuesday: int = Form(...),

    hours_wednesday: int = Form(...),
    minutes_wednesday: int = Form(...),

    hours_thursday: int = Form(...),
    minutes_thursday: int = Form(...),

    hours_friday: int = Form(...),
    minutes_friday: int = Form(...),

    hours_saturday: int = Form(...),
    minutes_saturday: int = Form(...),

    hours_sunday: int = Form(...),
    minutes_sunday: int = Form(...),
    ) -> HTMLResponse:

    # If the weekday is different than a Monday.
    if start_date.weekday() != 0:
        raise HTTPException(
            status_code=422,
            detail="The start date must be a Monday."
        )

    week_dates = {
        "monday": start_date,
        "tuesday": start_date + timedelta(days=1),
        "wednesday": start_date + timedelta(days=2),
        "thursday": start_date + timedelta(days=3),
        "friday": start_date + timedelta(days=4),
        "saturday": start_date + timedelta(days=5),
        "sunday": start_date + timedelta(days=6),
    }

    timesheet = {
        "Monday": {"date": week_dates["monday"], "hours": hours_monday, "minutes": minutes_monday},
        "Tuesday": {"date": week_dates["tuesday"], "hours": hours_tuesday, "minutes": minutes_tuesday},
        "Wednesday": {"date": week_dates["wednesday"], "hours": hours_wednesday, "minutes": minutes_wednesday},
        "Thursday": {"date": week_dates["thursday"], "hours": hours_thursday, "minutes": minutes_thursday},
        "Friday": {"date": week_dates["friday"], "hours": hours_friday, "minutes": minutes_friday},
        "Saturday": {"date": week_dates["saturday"], "hours": hours_saturday, "minutes": minutes_saturday},
        "Sunday": {"date": week_dates["sunday"], "hours": hours_sunday, "minutes": minutes_sunday},
    }

    # Double checking that the front-end inputs are complying
    validate_inputs = validate_timesheet(timesheet)
    if not validate_inputs:
         raise HTTPException(
              status_code=422,
              detail="Please insert valid hours and minutes"
         )

    total_hours = 0
    total_minutes = 0

    # Summing all hours in minutes
    for day in timesheet:
        total_hours += timesheet[day]["hours"]
        total_minutes += timesheet[day]["minutes"]

    # Transforming hours in minutes and extracting the final values
    total_minutes_all = (total_hours * 60) + total_minutes
    final_hours = total_minutes_all // 60
    final_minutes = total_minutes_all % 60

    if not has_logged_time(final_hours, final_minutes):
         raise HTTPException(
              status_code=422,
              detail="You did not insert any hours."
         )

    if not is_within_weekly_limit(final_hours):
        raise HTTPException(
            status_code=422,
            detail=
                f"A weekly timesheet cannot exceed {MAX_HOURS_PER_WEEK}."
        )

    return templates.TemplateResponse(
        request=request,
        name="timesheet_result.html",
        context={
            "week_start": start_date,
            "week_end": week_dates["sunday"],
            "timesheet": timesheet,
            "total_hours": final_hours,
            "total_minutes": final_minutes,
        }
    )