# Nidaan — a clinic & diagnostic-lab manager

Nidaan (निदान, *diagnosis*) is the reference application for RizTech Academy's
[**Django Web Development**](https://www.riztechacademy.com/learn/django-web-development)
course. It is the software a small clinic or diagnostic lab runs its day on —
patients, doctors, appointments, test reports and billing — built to the standard the
course teaches: an honest data model, efficient queries, proper access control for
sensitive data, concurrency-safe money handling, tests, and a real deployment.

This repository is here so a learner who gets stuck has correct, runnable code to
compare against. Read it alongside the lessons; type the code yourself rather than
cloning it.

## What it does

- **Patients, doctors, appointments, test reports, payments** — a connected relational
  model with deliberate field types, `on_delete` choices and database constraints
  (a fee is never negative; a doctor can't be double-booked).
- **The Django admin** as a real operational tool for clinic staff.
- **Custom views, templates and forms** for the staff-facing pages.
- **A DRF API**: a staff `patients` endpoint, and a patient-facing `my-appointments`
  endpoint scoped so a logged-in patient sees **only their own** records.
- **Business logic in the right layer** — `Appointment.complete()` on the model
  (atomic: status + fee + payment), query logic on the manager
  (`Appointment.objects.booked()`, `.visible_to(user)`).

## Requirements

- **Python 3.12 or 3.13** (Django 5.1's test runner has a template-instrumentation
  incompatibility on Python 3.14 — the app runs on 3.14, but `manage.py test`'s
  view/template tests error there).
- The packages in `requirements.txt` (Django 5.1, DRF, WhiteNoise, and — for tests —
  factory_boy).

## Running it

```bash
git clone https://github.com/RizTech-Academy/nidaan.git
cd nidaan
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed            # sample doctors, patients, appointments
python manage.py createsuperuser # for the admin
python manage.py runserver
```

Then visit:

- `http://127.0.0.1:8000/patients/` — the staff patient list
- `http://127.0.0.1:8000/patients/new/` — add a patient (a form with validation)
- `http://127.0.0.1:8000/admin/` — the admin (log in as your superuser)
- `http://127.0.0.1:8000/api/patients/` — the API (browsable; requires login)

## Running the tests

```bash
python manage.py test        # use Python 3.12/3.13 (see Requirements)
```

The suite weights the risky paths the course stresses: the money flow
(`complete()` sets status, fee and payment), the invariants (negative fee and
double-booking are rejected by database constraints), and access
(a patient sees only their own appointments; staff see all).

## Project layout

```
config/            project settings, root URLs, WSGI/ASGI
patients/          the clinic domain (one app)
  models.py        Doctor, Patient, Appointment, TestReport, Payment
  managers…        AppointmentQuerySet: booked(), for_city(), visible_to(user)
  views.py         staff views (list, create) — thin, POST-redirect-GET
  forms.py         ModelForm with clean_phone validation
  admin.py         the admin configured as an ops tool
  serializers.py   DRF serializers
  api.py           PatientViewSet (staff) + MyAppointmentViewSet (patient-scoped)
  tests.py         model, business-logic and access tests (factory_boy)
  management/commands/seed.py   sample data
Dockerfile         production image (gunicorn, collectstatic)
requirements.txt   pinned dependencies
.env.example       the environment variables (copy to .env for local dev)
```

## Deploying

Set `DJANGO_DEBUG=False`, a real `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, and a
`DATABASE_URL` (PostgreSQL), then run `python manage.py check --deploy` (it must be
clean), `collectstatic`, `migrate`, and serve with `gunicorn config.wsgi` (the
`Dockerfile` does this). HTTPS and the secure-cookie/HSTS settings turn on
automatically when `DJANGO_DEBUG=False`.

---

Built for RizTech Academy. Licensed for learning use.
