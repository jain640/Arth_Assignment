from django.core.management.base import BaseCommand

from ...reminders import ReminderService


class Command(BaseCommand):
    help = "Send reminder emails for contracts nearing expiry or payment deadlines."

    def handle(self, *args, **options):
        service = ReminderService()
        payloads = service.send_notification_emails()
        self.stdout.write(self.style.SUCCESS(f"Sent {len(payloads)} reminder(s)"))
