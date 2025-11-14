"""Reminder utilities for expiring or payment-due service contracts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.db.models import Q

from .models import EmailCredential, EmailLog, ServiceContract, ServiceStatus


@dataclass
class ReminderPayload:
    contract_id: int
    vendor: str
    service_name: str
    expiry_date: date
    payment_due_date: date
    expiry_color: str
    payment_color: str
    days_until_expiry: int
    days_until_payment: int
    recipient: str

    def as_dict(self) -> dict:
        return {
            "contract_id": self.contract_id,
            "vendor": self.vendor,
            "service_name": self.service_name,
            "expiry_date": self.expiry_date,
            "payment_due_date": self.payment_due_date,
            "expiry_color": self.expiry_color,
            "payment_color": self.payment_color,
            "days_until_expiry": self.days_until_expiry,
            "days_until_payment": self.days_until_payment,
            "recipient": self.recipient,
        }


class ReminderService:
    """Encapsulates reminder calculations and notification dispatch."""

    def __init__(self, window_days: int = 15, credentials: EmailCredential | None = None):
        self.window_days = window_days
        self._credentials = credentials

    def _base_queryset(self):
        today = date.today()
        window_end = today + timedelta(days=self.window_days)
        return (
            ServiceContract.objects.select_related("vendor")
            .filter(status__in=[ServiceStatus.ACTIVE, ServiceStatus.PAYMENT_PENDING])
            .filter(Q(expiry_date__lte=window_end) | Q(payment_due_date__lte=window_end))
        )

    def build_reminder_payloads(self) -> list[ReminderPayload]:
        today = date.today()
        payloads: list[ReminderPayload] = []
        for contract in self._base_queryset():
            expiry_days = (contract.expiry_date - today).days
            payment_days = (contract.payment_due_date - today).days
            payloads.append(
                ReminderPayload(
                    contract_id=contract.id,
                    vendor=contract.vendor.name,
                    service_name=contract.service_name,
                    expiry_date=contract.expiry_date,
                    payment_due_date=contract.payment_due_date,
                    expiry_color=self._color_for(expiry_days),
                    payment_color=self._color_for(payment_days),
                    days_until_expiry=expiry_days,
                    days_until_payment=payment_days,
                    recipient=contract.vendor.email,
                )
            )
        return payloads

    def send_notification_emails(self) -> list[ReminderPayload]:
        payloads = self.build_reminder_payloads()
        connection = self._connection()
        sender = self._sender_email()
        for reminder in payloads:
            subject = f"Contract reminder: {reminder.service_name}"
            body = (
                f"Vendor: {reminder.vendor}\n"
                f"Service: {reminder.service_name}\n"
                f"Expiry date: {reminder.expiry_date} (status: {reminder.expiry_color})\n"
                f"Payment due: {reminder.payment_due_date} (status: {reminder.payment_color})\n"
            )
            success = True
            error_message = ""
            try:
                EmailMessage(
                    subject,
                    body,
                    sender,
                    [reminder.recipient],
                    connection=connection,
                ).send(fail_silently=False)
            except Exception as exc:  # pragma: no cover - network failures are rare
                success = False
                error_message = str(exc)
            EmailLog.objects.create(
                contract_id=reminder.contract_id,
                recipient=reminder.recipient,
                sender=sender,
                subject=subject,
                body=body,
                success=success,
                error_message=error_message,
            )
        return payloads

    def _color_for(self, days_remaining: int) -> str:
        if days_remaining < 0:
            return "red"
        if days_remaining <= self.window_days:
            return "yellow"
        return "green"

    def _connection(self):
        credentials = self._get_credentials()
        if not credentials:
            return get_connection()
        backend = "django.core.mail.backends.smtp.EmailBackend"
        return get_connection(
            backend=backend,
            host=credentials.smtp_host,
            port=credentials.smtp_port,
            username=credentials.username or None,
            password=credentials.password or None,
            use_tls=credentials.use_tls,
            use_ssl=credentials.use_ssl,
        )

    def _sender_email(self) -> str:
        credentials = self._get_credentials()
        if credentials:
            return credentials.from_email
        return settings.DEFAULT_FROM_EMAIL

    def _get_credentials(self) -> EmailCredential | None:
        if self._credentials is None:
            self._credentials = EmailCredential.get_active()
        return self._credentials
