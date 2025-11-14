from django.test import TestCase, Client
from django.urls import reverse


class PingViewTests(TestCase):
    def test_ping_returns_pong(self):
        client = Client()
        response = client.get(reverse("ping"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"message": "pong"})
