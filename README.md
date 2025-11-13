# Vendor Management Service (Django)

A Django REST Framework backend that manages vendors and their service contracts. It implements JWT-protected CRUD APIs, pagination, expiring/payment-due filters, and reminder utilities that color-code urgent contracts.

## Features
- CRUD endpoints for vendors and service contracts.
- JWT authentication powered by `djangorestframework-simplejwt` (issue tokens via `/api/token/`).
- Pagination via DRF's page-number pagination for vendor and service listings.
- Filter utilities for contracts expiring or requiring payment within 15 days.
- Reminder endpoint that color-codes urgency levels and returns mock email payloads.

## Tech stack & design choices
- **Framework**: Django 5 + Django REST Framework for batteries-included CRUD, pagination, and browsable API.
- **Authentication**: JSON Web Tokens using `rest_framework_simplejwt`. Tokens expire after 30 minutes and can be refreshed.
- **Database**: SQLite via Django ORM (easily switchable through `DATABASES` in `vendor_management/settings.py`).
- **Apps & modules**: `vendor_management.vendors` holds models, serializers, and viewsets for vendors and their contracts. Reminder logic is embedded inside the `ServiceContractViewSet.reminders` action to keep all contract-specific behavior together.
- **Color coding**: Reminders follow a simple scheme—`green` (healthy), `amber` (due within 15 days), `red` (overdue)—to quickly highlight urgency.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # create login for token endpoint
python manage.py runserver 0.0.0.0:8000
```

The browsable API lives at `http://127.0.0.1:8000/api/` and the admin console at `/admin/`.

## Authentication workflow
1. `POST /api/token/` with JSON body containing `username` and `password`.
2. Use the returned `access` token for subsequent requests: `Authorization: Bearer <token>`.
3. Refresh tokens with `POST /api/token/refresh/` when needed.

## API overview
All routes live under `/api/` and require authentication.

### Vendors
| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/vendors/` | Paginated vendor list with their services |
| `POST` | `/api/vendors/` | Create vendor |
| `GET` | `/api/vendors/{id}/` | Retrieve vendor detail |
| `PUT/PATCH` | `/api/vendors/{id}/` | Update vendor |
| `DELETE` | `/api/vendors/{id}/` | Delete vendor |
| `GET` | `/api/vendors/with-active-services/` | Vendors including only active services |

### Service contracts
| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/services/` | Paginated contracts |
| `POST` | `/api/services/` | Create contract |
| `GET` | `/api/services/{id}/` | Retrieve contract |
| `PUT/PATCH` | `/api/services/{id}/` | Update contract |
| `DELETE` | `/api/services/{id}/` | Delete contract |
| `GET` | `/api/services/expiring-soon/` | Contracts expiring within 15 days |
| `GET` | `/api/services/payment-due/` | Contracts with payment due within 15 days |
| `PATCH` | `/api/services/{id}/status/` | Update status (`ACTIVE`, `EXPIRED`, `PAYMENT_PENDING`, `COMPLETED`) |
| `GET` | `/api/services/reminders/` | Reminder payload with color coding + mock email data |

### Reminder payload example
```json
{
  "count": 1,
  "results": [
    {
      "service_id": 3,
      "vendor": "AWS",
      "service_name": "Cloud Hosting",
      "expiry_date": "2024-06-30",
      "payment_due_date": "2024-06-20",
      "color_code": "amber",
      "email_subject": "Reminder: Cloud Hosting",
      "email_body": "Hi Jeff, your service Cloud Hosting is approaching its expiry/payment deadline."
    }
  ]
}
```

## Design & assumptions
- Vendors have unique emails to avoid duplicates.
- Services cascade-delete when a vendor is removed.
- The reminder action acts as the "daily check"; hook it into a cron/management command or background worker for automation.
- Pagination defaults to 10 results per page; override via `?page=` query parameters.

## Testing
Run Django's system checks (requires dependencies from `requirements.txt`):
```bash
python manage.py check
```

You can also add fixtures and run `python manage.py test` for future automated coverage.
