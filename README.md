# Weekly Timesheet

A FastAPI web app for logging weekly work hours. Pick the Monday that starts a week,
enter hours and minutes worked per day, and get back a formatted summary with the
total time worked for the week.

Built as a hands-on exercise in server-side form handling, request validation, and
Jinja2 templating with FastAPI — a step in a broader move toward Python
automation/backend development.

## Why this project

Weekly timesheets are a genuinely common piece of business software (payroll,
contracting, freelance invoicing all need one), which made this a useful vehicle for
practicing the full request/response cycle in FastAPI: accepting structured form
input, validating it against real business rules, doing date arithmetic, and
rendering a server-side templated result.

## Features

- Weekly entry form for hours + minutes worked, Monday through Sunday
- Server-side rejection of any start date that isn't a Monday (`400`)
- Server-side range validation on every hours/minutes field, independent of the
  browser (`422` if out of range)
- Rejection of a timesheet with no hours logged at all (`422`)
- Automatic date derivation for the rest of the week from the selected Monday
- Minute-overflow handling — minutes are correctly carried into hours in the total
- Server-rendered summary page listing each day's date, hours, and minutes, plus the
  week's total
- Automated test suite (`pytest` + FastAPI's `TestClient`)

## Tech stack

| Layer         | Choice                                    |
|---------------|--------------------------------------------|
| Framework     | [FastAPI](https://fastapi.tiangolo.com/)   |
| Templating    | Jinja2 (via `fastapi.templating`)          |
| Server        | Uvicorn (ASGI)                             |
| Form parsing  | `python-multipart`                          |
| Testing       | pytest, FastAPI `TestClient`               |
| Language      | Python 3.10+                                |

## Project structure

```
worked-hours/
├── main.py                       # App instance — creates FastAPI(), includes the router
├── routers/
│   ├── __init__.py
│   └── timesheet.py               # Both routes, validation helpers, business logic
├── templates/
│   ├── index.html                 # Weekly entry form
│   └── timesheet_result.html      # Rendered summary after submission
├── tests/
│   ├── __init__.py
│   └── main_test.py               # pytest suite covering routes and validation helpers
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting started

**Requirements:** Python 3.10 or later.

```bash
# clone the repo
git clone https://github.com/BLUCASS/<repo-name>.git
cd <repo-name>

# create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# run the app
uvicorn main:app --reload
```

Then open **http://127.0.0.1:8000** in a browser.

## Running tests

```bash
pip install pytest httpx
pytest -v
```

## Usage

1. Open the app — you'll see a weekly entry form.
2. Pick the **Monday** that starts the week. Any other weekday is rejected by the
   server with a 400 error, since a week always starts on Monday in this app.
3. Enter hours (0-23) and minutes (0–59) worked for each day. Days with no hours
   logged can be left at `0`.
4. Submit. The app returns a summary page showing each day's date, hours, minutes,
   and the week's total (correctly carried from minutes into hours).
5. Use **Submit another timesheet** to log a new week.

## How validation works

- **Client-side:** HTML5 `min`/`max`/`required` attributes on each input give
  immediate feedback in the browser.
- **Server-side:**
  - FastAPI's `Form(...)` parameters enforce that every field is present and is a
    valid `int`/`date` before the route body even runs.
  - `validate_timesheet()` independently checks that every day's hours fall within
    0–23 and minutes within 0–59, so the API is safe even if a request bypasses the
    HTML form entirely.
  - The route checks `start_date.weekday() == 0` and raises `HTTPException(400)` if
    the chosen date isn't a Monday.
  - `check_total_hours()` rejects a submission where every field is `0`, since that's
    very unlikely to be an intentional timesheet entry.

## Roadmap

- [ ] Persist submitted timesheets (currently render-and-discard) — CSV export or a
      lightweight DB would be the natural next step
- [ ] Move the per-day validation logic into a small Pydantic model with
      `Field(ge=..., le=...)` constraints, to get range validation and clearer error
      messages "for free" from FastAPI instead of a hand-written loop
- [ ] Add a `conftest.py` fixture for the FastAPI `TestClient` instead of
      instantiating it at module level in the test file

## License

MIT — see [`LICENSE`](LICENSE) if included, or feel free to add one.

## Author

**Lucas Batista Pilantil** — Cork, Ireland
[github.com/BLUCASS](https://github.com/BLUCASS)