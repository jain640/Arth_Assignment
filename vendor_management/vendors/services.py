from datetime import timedelta
from typing import List, Optional

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone

from .models import ServiceContract
from .serializers import ServiceContractSerializer


class ReminderService:
    """Utility for building reminder payloads and sending emails."""

    def __init__(self, horizon_days: int = 15):
        self.horizon_days = horizon_days

    def _due_queryset(self):
        today = timezone.now().date()
        horizon = today + timedelta(days=self.horizon_days)
        return ServiceContract.objects.select_related('vendor').filter(
            Q(expiry_date__range=(today, horizon))
            | Q(payment_due_date__range=(today, horizon))
        )

    def _serialize_contract(self, contract: ServiceContract) -> dict:
        serialized = ServiceContractSerializer(contract).data
        return {
            'service_id': serialized['id'],
            'vendor_id': serialized['vendor'],
            'vendor_name': contract.vendor.name,
            'contact_person': contract.vendor.contact_person,
            'email': contract.vendor.email,
            'service_name': serialized['service_name'],
            'expiry_date': serialized['expiry_date'],
            'payment_due_date': serialized['payment_due_date'],
            'amount': serialized['amount'],
            'status': serialized['status'],
            'color_code': serialized['color_code'],
            'is_expiring_soon': serialized['is_expiring_soon'],
            'is_payment_due_soon': serialized['is_payment_due_soon'],
            'email_subject': f"Reminder: {serialized['service_name']} nearing deadline",
            'email_body': (
                f"Hello {contract.vendor.contact_person},\n\n"
                f"This is a reminder that {serialized['service_name']} for vendor "
                f"{contract.vendor.name} is approaching its expiry/payment deadline.\n"
                f"Expiry date: {serialized['expiry_date']}\n"
                f"Payment due date: {serialized['payment_due_date']}\n"
                f"Status color: {serialized['color_code'].upper()}\n\n"
                "Please take the necessary action."
            ),
        }

    def generate_reminders(self) -> List[dict]:
        return [self._serialize_contract(contract) for contract in self._due_queryset()]

    def send_notifications(self, reminders: Optional[List[dict]] = None) -> dict:
        reminders = reminders or self.generate_reminders()
        sent = 0
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
        for reminder in reminders:
            if not reminder['email']:
                continue
            send_mail(
                reminder['email_subject'],
                reminder['email_body'],
                from_email,
                [reminder['email']],
                fail_silently=True,
            )
            sent += 1
        return {'sent': sent, 'reminders': reminders}
