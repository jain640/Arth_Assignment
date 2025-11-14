# Vendor Management API (Django + DRF)

This project delivers the vendor and contract management requirements using Django 5, Django REST Framework, and SimpleJWT for authentication. It exposes CRUD endpoints, pagination, expiring/payment-due filters, and reminder utilities (API + management command) that compute color-coded alerts and send notification emails via Django's console backend.

## Features
- JWT-protected CRUD for vendors and their service contracts.
- Vendors list automatically embeds each vendor's **active** services.
- Paginated listings for vendors and contracts.
- Dedicated feeds for contracts expiring or with payments due in the next 15 days.
- Contract status updates (Active, Expired, Payment Pending, Completed).
- Reminder API + report endpoint + `run_contract_reminders` management command that compute color codes (green/yellow/red) for expiry/payment deadlines within 15 days and send notification emails. The report now breaks down color totals overall plus per expiry and payment deadline so dashboards can highlight which contracts are at risk.
- Email reminder logs exposed through the API and Django admin so stakeholders can audit who received which notification and when.
- Django admin action to manually trigger the reminder workflow plus editable SMTP credentials so non-technical staff can manage reminder email settings.

## Requirements
- Python 3.11+
- `pip`
- Access to the packages listed in `requirements.txt` (Django, DRF, SimpleJWT). If PyPI is blocked, provide an internal mirror/wheelhouse.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # optional, for Django admin access
python manage.py seed_demo_data  # optional, loads demo vendors + contracts
python manage.py runserver 0.0.0.0:8000
```

The API will be available at `http://localhost:8000/api/` and the browsable DRF interface mirrors the endpoints listed below.

## Authentication
Issue a JWT before calling any API (except `/api/ping/`):

```bash
http POST :8000/api/token/ username=<user> password=<password>
```

Use the returned `access` token in the `Authorization: Bearer <token>` header. Refresh tokens are available at `/api/token/refresh/`.

## API catalog
| Method | Path | Description |
| ------ | ---- | ----------- |
| GET | `/api/ping/` | Anonymous health check returning `{ "message": "pong" }`. |
| GET/POST | `/api/vendors/` | Paginated vendor list + create (includes active services). |
| GET/PUT/PATCH/DELETE | `/api/vendors/{id}/` | Vendor detail & CRUD. |
| GET/POST | `/api/services/` | Paginated service contract list + create. |
| GET/PUT/PATCH/DELETE | `/api/services/{id}/` | Contract detail & CRUD. |
| POST | `/api/services/{id}/update-status/` | Update a contract's status (`ACTIVE`, `EXPIRED`, `PAYMENT_PENDING`, `COMPLETED`). |
| GET | `/api/services/expiring-soon/` | Contracts whose expiry date falls within the next 15 days. |
| GET | `/api/services/payment-due/` | Contracts whose payment due date falls within the next 15 days. |
| GET | `/api/services/reminders/` | Reminder payloads with expiry/payment color codes (green/yellow/red) for contracts within the reminder window. |
| GET | `/api/services/reminders/report/` | Aggregated reminder report (generated date, overall + expiry + payment color totals, payloads) for daily dashboards/jobs. |
| POST | `/api/services/reminders/send-emails/` | Triggers reminder calculation and sends notification emails (console backend). |
| GET | `/api/services/reminders/email-logs/` | Paginated reminder email log showing recipients, subjects, and delivery status. |

Pagination is enabled for the vendor and service viewsets (default page size = 10; override with `?page=<n>&page_size=<m>`).

## Reminder logic
- Reminder window: 15 days (configurable via `ReminderService(window_days=...)`).
- Color codes: `green` (> 15 days away), `yellow` (0-15 days), `red` (past due).
- Email backend: console (`settings.EMAIL_BACKEND`) by default, but production SMTP credentials can be entered via the **Email credentials** admin section. The reminder service automatically uses the most recently updated active credential (host, port, TLS/SSL, username/password, sender email), and persists each send attempt to the Email Log.

### Scheduled usage
To run the reminder workflow outside of the API (e.g., daily cron):

```bash
python manage.py run_contract_reminders
```

The command reuses the same `ReminderService` used by the REST endpoints, keeping the reminder logic centralized.

## Django admin
The Django admin (`/admin/`) exposes Vendor and ServiceContract models with helpful list filters and search fields, plus:

- **Run reminder email dispatch now** action on the ServiceContract changelist to execute the `run_contract_reminders` workflow without touching the CLI.
- **Email credentials** section to add/edit SMTP connection details and enable/disable which credential set should be used when sending reminders.
- **Email logs** section lists each reminder sent (recipient, subject, success/error message) for auditing and support.

## Testing & checks
Once dependencies are installed, run the usual Django checks/migrations:

```bash
python manage.py check
python manage.py test
```

(Automated tests require Django/DRF to be installed; install from `requirements.txt` first.)

## How to test the app locally
Follow the sequence below to exercise the main requirements end-to-end on your workstation:

1. **Start a fresh database**
   ```bash
   rm db.sqlite3  # optional but keeps things clean when re-testing
   python manage.py migrate
   python manage.py seed_demo_data --flush  # load demo vendors/contracts
   ```

2. **Create a user for API + admin access**
   ```bash
   python manage.py createsuperuser
   ```

3. **Run the development server**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

4. **Authenticate and call APIs**
   - Obtain a JWT access token:
     ```bash
     http POST :8000/api/token/ username=<user> password=<password>
     ```
   - Use the returned token for all subsequent requests:
     ```bash
     http GET :8000/api/vendors/ "Authorization: Bearer <access-token>"
     ```

5. **Verify CRUD + filters**
   - Create a vendor via `/api/vendors/` and a contract via `/api/services/`.
   - Hit the filtered feeds `/api/services/expiring-soon/` and `/api/services/payment-due/` to confirm 15-day filtering.

6. **Exercise reminder workflow**
   - Call `POST /api/services/reminders/send-emails/` to trigger reminder emails (logged to console by default).
   - Inspect `/api/services/reminders/email-logs/` or visit `/admin/main_app/emaillog/` to confirm log entries were created.
   - (Optional) Run `python manage.py run_contract_reminders` to emulate the scheduled job.

7. **Review the Django admin**
   - Browse to `http://localhost:8000/admin/`, log in with the superuser, and manage Vendors, Service Contracts, Email Credentials, and Email Logs.

Following the steps above verifies authentication, CRUD, pagination, expiring/payment filters, reminder dispatch, and the auditing trails locally.
