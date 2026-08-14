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

The more interesting half of the work turned out to be the failure paths rather than
the happy path — see [Design decisions](#design-decisions) below.

## Features

- Weekly entry form for hours + minutes worked, Monday through Sunday
- Automatic date derivation for the rest of the week from the selected Monday
- Server-side rejection of any start date that isn't a Monday
- Server-side range validation on every field, independent of the browser:
  0–23 hours and 0–59 minutes per day
- Rejection of a timesheet with no hours logged at all
- A 70-hour weekly sanity cap, to catch typos like a stray extra digit
- Minute-overflow handling — minutes are correctly carried into hours in the total
- Server-rendered summary page listing each day's date, hours, and minutes, plus the
  week's total
- Automated test suite (`pytest` + FastAPI's `TestClient`) covering both the
  validation helpers and the endpoints that call them

## Tech stack

| Layer         | Choice                                     |
|---------------|--------------------------------------------|
| Framework     | [FastAPI](https://fastapi.tiangolo.com/)   |
| Templating    | Jinja2 (via `fastapi.templating`)          |
| Server        | Uvicorn (ASGI)                             |
| Form parsing  | `python-multipart`                         |
| Testing       | pytest, FastAPI `TestClient`               |
| Language      | Python 3.10+                               |

## Project structure

```
worked-hours/
├── main.py                       # App instance — creates FastAPI(), includes the router
├── routers/
│   ├── __init__.py
│   └── timesheet.py              # Both routes, validation helpers, business logic
├── templates/
│   ├── index.html                # Weekly entry form
│   └── timesheet_result.html     # Rendered summary after submission
├── tests/
│   ├── __init__.py
│   └── main_test.py              # pytest suite covering routes and validation helpers
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
pip install pytest httpx2
pytest -v
```

## Usage

1. Open the app — you'll see a weekly entry form.
2. Pick the **Monday** that starts the week. Any other weekday is rejected by the
   server, since a week always starts on Monday in this app.
3. Enter hours (0–23) and minutes (0–59) worked for each day. Days with no hours
   logged can be left at `0`.
4. Submit. The app returns a summary page showing each day's date, hours, minutes,
   and the week's total (correctly carried from minutes into hours).
5. Use **Submit another timesheet** to log a new week.

## How validation works

**Client-side:** HTML5 `min`/`max`/`required` attributes on each input give immediate
feedback in the browser. This is treated as a convenience only — never as a
guarantee.

**Server-side:** every rule is enforced again in the route, so the API is safe even
if a request bypasses the HTML form entirely (a plain `curl` call ignores HTML
attributes completely).

| Rule                                    | Enforced by                       | Response |
|-----------------------------------------|-----------------------------------|----------|
| Every field present and a valid `int`/`date` | FastAPI `Form(...)` parameters | `422`    |
| Start date must be a Monday             | `start_date.weekday() == 0`       | `422`    |
| 0–23 hours per day                      | `hours_dont_exceed()`             | `422`    |
| 0–59 minutes per day                    | `minutes_dont_exceed()`           | `422`    |
| At least some time logged               | `has_logged_time()`               | `422`    |
| Week total within 70 hours              | `is_within_weekly_limit()`        | `422`    |

## Design decisions

**Why 23 hours per day and not 24.** With minutes capped at 59, a limit of 23 gives a
maximum valid entry of 23:59 — the largest duration that fits inside a calendar day.
Allowing 24 would make 24:59 representable, which is more than a day, so 23 is the
internally consistent bound.

**Why a 70-hour weekly cap.** Per-day limits alone still permit an absurd week
(23 hours × 7 days = 161 hours), so a stray extra digit could pass unnoticed. 70 is
deliberately well above a normal working week, including overtime, so it functions as
a typo catcher rather than a policy limit. It is currently a hard rejection; treating
it as a warning that still renders the summary would be a reasonable alternative.

**One rule per function.** Validation started as a single function checking several
rules and returning one boolean. Because the route couldn't tell which rule had
failed, a user who logged 70+ hours got the message "You did not insert any hours."
Splitting the rules into `has_logged_time()`, `hours_dont_exceed()`,
`minutes_dont_exceed()` and `is_within_weekly_limit()` means each failure now returns
an accurate message, and each rule is testable in isolation.

**Totals are computed in one unit.** All hours and minutes are summed into total
minutes and only converted back at the end, rather than carrying two units around and
handling overflow by hand. This is what makes 5h30 + 1h45 + 3h15 come out as 10h30
instead of 9h90.

**Every rule gets two tests.** One unit test for the logic, and one endpoint test
proving the route actually calls it. This came directly from a bug during
development: the weekly cap had a passing unit test while never being called from the
route, so the suite was green and the rule was entirely unenforced. A unit test proves
a function is correct; only an endpoint test proves it is connected.

## Author

**Lucas Pilantil** — Cork, Ireland
[github.com/BLUCASS](https://github.com/BLUCASS)