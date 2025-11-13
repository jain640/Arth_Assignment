from django.db import models


class Vendor(models.Model):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]

    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=32)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class ServiceContract(models.Model):
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_EXPIRED = 'EXPIRED'
    STATUS_PAYMENT_PENDING = 'PAYMENT_PENDING'
    STATUS_COMPLETED = 'COMPLETED'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_PAYMENT_PENDING, 'Payment Pending'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    vendor = models.ForeignKey(Vendor, related_name='services', on_delete=models.CASCADE)
    service_name = models.CharField(max_length=255)
    start_date = models.DateField()
    expiry_date = models.DateField()
    payment_due_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['expiry_date']

    def __str__(self) -> str:
        return f"{self.service_name} ({self.vendor.name})"

    @property
    def is_expiring_soon(self) -> bool:
        from django.utils import timezone

        return 0 <= (self.expiry_date - timezone.now().date()).days <= 15

    @property
    def is_payment_due_soon(self) -> bool:
        from django.utils import timezone

        return 0 <= (self.payment_due_date - timezone.now().date()).days <= 15
