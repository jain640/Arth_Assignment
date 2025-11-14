from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand

from ...models import (
    ServiceContract,
    ServiceStatus,
    Vendor,
    VendorStatus,
)


class Command(BaseCommand):
    help = "Seed the database with demo vendors and service contracts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing vendors and services before creating demo data.",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            ServiceContract.objects.all().delete()
            Vendor.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing vendor/service data deleted."))

        today = date.today()

        vendor_payloads = [
            {
                "name": "Alpha Tech Solutions",
                "contact_person": "Ava Patel",
                "email": "alpha@example.com",
                "phone": "+1-555-0100",
                "status": VendorStatus.ACTIVE,
                "services": [
                    {
                        "service_name": "Network Maintenance",
                        "start_offset": -120,
                        "expiry_offset": 200,
                        "payment_offset": 10,
                        "amount": Decimal("12000.00"),
                        "status": ServiceStatus.ACTIVE,
                    },
                    {
                        "service_name": "Managed Security Suite",
                        "start_offset": -60,
                        "expiry_offset": 40,
                        "payment_offset": 5,
                        "amount": Decimal("18500.00"),
                        "status": ServiceStatus.PAYMENT_PENDING,
                    },
                ],
            },
            {
                "name": "Beacon Facilities",
                "contact_person": "Miguel Hernandez",
                "email": "beacon@example.com",
                "phone": "+1-555-0101",
                "status": VendorStatus.ACTIVE,
                "services": [
                    {
                        "service_name": "HVAC Annual Service",
                        "start_offset": -300,
                        "expiry_offset": -5,
                        "payment_offset": -2,
                        "amount": Decimal("9800.00"),
                        "status": ServiceStatus.EXPIRED,
                    },
                    {
                        "service_name": "Elevator Maintenance",
                        "start_offset": -30,
                        "expiry_offset": 180,
                        "payment_offset": 14,
                        "amount": Decimal("4500.00"),
                        "status": ServiceStatus.ACTIVE,
                    },
                ],
            },
            {
                "name": "Cobalt Cloud Partners",
                "contact_person": "Imani Okoro",
                "email": "cobalt@example.com",
                "phone": "+1-555-0102",
                "status": VendorStatus.INACTIVE,
                "services": [
                    {
                        "service_name": "SaaS Subscription",
                        "start_offset": -200,
                        "expiry_offset": 15,
                        "payment_offset": 7,
                        "amount": Decimal("24000.00"),
                        "status": ServiceStatus.ACTIVE,
                    },
                    {
                        "service_name": "Custom Integration Support",
                        "start_offset": -10,
                        "expiry_offset": 60,
                        "payment_offset": 30,
                        "amount": Decimal("6200.00"),
                        "status": ServiceStatus.COMPLETED,
                    },
                ],
            },
        ]

        created_vendors = 0
        created_services = 0

        for payload in vendor_payloads:
            vendor, vendor_created = Vendor.objects.update_or_create(
                email=payload["email"],
                defaults={
                    "name": payload["name"],
                    "contact_person": payload["contact_person"],
                    "phone": payload["phone"],
                    "status": payload["status"],
                },
            )
            if vendor_created:
                created_vendors += 1

            for service_payload in payload["services"]:
                service, service_created = ServiceContract.objects.update_or_create(
                    vendor=vendor,
                    service_name=service_payload["service_name"],
                    defaults={
                        "start_date": today + timedelta(days=service_payload["start_offset"]),
                        "expiry_date": today + timedelta(days=service_payload["expiry_offset"]),
                        "payment_due_date": today
                        + timedelta(days=service_payload["payment_offset"]),
                        "amount": service_payload["amount"],
                        "status": service_payload["status"],
                    },
                )
                if service_created:
                    created_services += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Seed complete: "
                f"{created_vendors} vendor(s) and {created_services} service contract(s) created."
            )
        )
