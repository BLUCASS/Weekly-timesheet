from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from datetime import date, timedelta


app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
        )

@app.post("/submit-timesheet")
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
            status_code=400,
            detail="The start date must be a Monday."
        )

    total_hours = 0
    total_minutes = 0

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

    for day in timesheet:
        total_hours += timesheet[day]["hours"]
        total_minutes += timesheet[day]["minutes"]

    total_minutes_all = (total_hours * 60) + total_minutes
    final_hours = total_minutes_all // 60
    final_minutes = total_minutes_all % 60

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

asyn def ("/payroll")