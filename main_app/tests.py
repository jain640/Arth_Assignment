from django.test import Client, TestCase
from django.urls import reverse

from .models import EmailCredential


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
