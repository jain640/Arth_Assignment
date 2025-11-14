from django.core.management.base import BaseCommand

from ...services import ReminderService


class Command(BaseCommand):
    help = 'Checks contracts due within the reminder window and sends notification emails.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--horizon-days',
            type=int,
            default=15,
            help='Number of days ahead to check for expiring/payment-due services.',
        )

    def handle(self, *args, **options):
        service = ReminderService(horizon_days=options['horizon_days'])
        result = service.send_notifications()
        self.stdout.write(
            self.style.SUCCESS(
                f"Processed {len(result['reminders'])} reminders and sent {result['sent']} emails."
            )
        )
