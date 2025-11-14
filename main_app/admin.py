from django.contrib import admin

from .models import ServiceContract, Vendor


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "email", "status")
    search_fields = ("name", "contact_person", "email")
    list_filter = ("status",)


@admin.register(ServiceContract)
class ServiceContractAdmin(admin.ModelAdmin):
    list_display = (
        "service_name",
        "vendor",
        "expiry_date",
        "payment_due_date",
        "status",
    )
    search_fields = ("service_name", "vendor__name")
    list_filter = ("status",)
    autocomplete_fields = ("vendor",)
