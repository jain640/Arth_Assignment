from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from .models import EmailCredential, EmailLog, ServiceContract, ServiceStatus, Vendor
from .reminders import ReminderReport, ReminderService


class PingViewTests(TestCase):
    def test_ping_returns_pong(self):
        client = Client()
        response = client.get(reverse("ping"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"message": "pong"})


class EmailCredentialTests(TestCase):
    def test_get_active_returns_latest_active_record(self):
        first = EmailCredential.objects.create(
            name="Primary",
            from_email="alerts@example.com",
            smtp_host="smtp.example.com",
            smtp_port=587,
            use_tls=True,
            use_ssl=False,
            username="user1",
            password="secret",
        )
        second = EmailCredential.objects.create(
            name="Backup",
            from_email="ops@example.com",
            smtp_host="smtp2.example.com",
            smtp_port=465,
            use_tls=False,
            use_ssl=True,
            username="user2",
            password="secret2",
        )

        active = EmailCredential.get_active()
        self.assertEqual(active, second)

        first.is_active = False
        first.save(update_fields=["is_active"])
        second.is_active = False
        second.save(update_fields=["is_active"])

        self.assertIsNone(EmailCredential.get_active())


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class ReminderEmailLogTests(TestCase):
    def setUp(self):
        self.vendor = Vendor.objects.create(
            name="Acme",
            contact_person="Alice",
            email="alice@example.com",
            phone="1234567890",
        )
        self.contract = ServiceContract.objects.create(
            vendor=self.vendor,
            service_name="Security",
            start_date=date.today() - timedelta(days=10),
            expiry_date=date.today() + timedelta(days=5),
            payment_due_date=date.today() + timedelta(days=7),
            amount=1000,
            status=ServiceStatus.ACTIVE,
        )

    def test_send_notification_creates_email_log(self):
        ReminderService(window_days=15).send_notification_emails()
        self.assertEqual(EmailLog.objects.count(), 1)
        log = EmailLog.objects.first()
        self.assertEqual(log.recipient, self.vendor.email)
        self.assertTrue(log.success)
        self.assertIn(self.contract.service_name, log.subject)

    def test_email_logs_endpoint_returns_entries(self):
        log = EmailLog.objects.create(
            contract=self.contract,
            recipient="ops@example.com",
            sender="noreply@example.com",
            subject="Reminder",
            body="Body",
            success=True,
        )
        client = APIClient()
        user = get_user_model().objects.create_user(
            username="apiuser",
            password="password123",
            email="api@example.com",
        )
        client.force_authenticate(user=user)
        response = client.get(reverse("services-reminders-email-logs"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["recipient"], log.recipient)


class ReminderReportTests(TestCase):
    def setUp(self):
        self.vendor = Vendor.objects.create(
            name="Vendor", contact_person="Casey", email="vendor@example.com", phone="0001"
        )
        today = date.today()
        self.contract_red = ServiceContract.objects.create(
            vendor=self.vendor,
            service_name="Security Patrol",
            start_date=today - timedelta(days=30),
            expiry_date=today - timedelta(days=1),
            payment_due_date=today + timedelta(days=5),
            amount=5000,
            status=ServiceStatus.ACTIVE,
        )
        self.contract_yellow = ServiceContract.objects.create(
            vendor=self.vendor,
            service_name="Cleaning",
            start_date=today - timedelta(days=15),
            expiry_date=today + timedelta(days=10),
            payment_due_date=today + timedelta(days=7),
            amount=2500,
            status=ServiceStatus.PAYMENT_PENDING,
        )

    def test_build_report_counts_by_color(self):
        service = ReminderService(window_days=15)
        report = service.build_report()
        self.assertIsInstance(report, ReminderReport)
        self.assertEqual(report.total_contracts, 2)
        self.assertEqual(report.totals_by_color["red"], 1)
        self.assertEqual(report.totals_by_color["yellow"], 1)

    def test_report_endpoint_returns_payloads(self):
        client = APIClient()
        user = get_user_model().objects.create_user(
            username="reporter", password="testpass", email="reporter@example.com"
        )
        client.force_authenticate(user=user)
        response = client.get(reverse("services-reminders-report"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_contracts"], 2)
        self.assertEqual(len(response.data["payloads"]), 2)
