from django.db import models


class TimestampedModel(models.Model):
    """Abstract base model that provides created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class VendorStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"


class ServiceStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    EXPIRED = "EXPIRED", "Expired"
    PAYMENT_PENDING = "PAYMENT_PENDING", "Payment Pending"
    COMPLETED = "COMPLETED", "Completed"


class Vendor(TimestampedModel):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30)
    status = models.CharField(
        max_length=20,
        choices=VendorStatus.choices,
        default=VendorStatus.ACTIVE,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.name


class ServiceContract(TimestampedModel):
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="services",
    )
    service_name = models.CharField(max_length=255)
    start_date = models.DateField()
    expiry_date = models.DateField()
    payment_due_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=ServiceStatus.choices,
        default=ServiceStatus.ACTIVE,
    )

    class Meta:
        ordering = ["expiry_date", "payment_due_date"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.vendor.name} - {self.service_name}"
