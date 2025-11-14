"""Reminder utilities for expiring or payment-due service contracts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q

from .models import ServiceContract, ServiceStatus


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

    def __init__(self, window_days: int = 15):
        self.window_days = window_days

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
        for reminder in payloads:
            subject = f"Contract reminder: {reminder.service_name}"
            body = (
                f"Vendor: {reminder.vendor}\n"
                f"Service: {reminder.service_name}\n"
                f"Expiry date: {reminder.expiry_date} (status: {reminder.expiry_color})\n"
                f"Payment due: {reminder.payment_due_date} (status: {reminder.payment_color})\n"
            )
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [reminder.recipient],
                fail_silently=True,
            )
        return payloads

    def _color_for(self, days_remaining: int) -> str:
        if days_remaining < 0:
            return "red"
        if days_remaining <= self.window_days:
            return "yellow"
        return "green"
