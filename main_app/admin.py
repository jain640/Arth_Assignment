from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from .models import EmailCredential, ServiceContract, Vendor
from .reminders import ReminderService


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
    actions = ("run_contract_reminders",)

    def run_contract_reminders(self, request, queryset):
        service = ReminderService()
        payloads = service.send_notification_emails()
        self.message_user(
            request,
            _(f"Triggered reminder emails for {len(payloads)} contract(s)."),
            messages.SUCCESS,
        )

    run_contract_reminders.short_description = _(
        "Run reminder email dispatch now"
    )


@admin.register(EmailCredential)
class EmailCredentialAdmin(admin.ModelAdmin):
    list_display = ("name", "from_email", "smtp_host", "smtp_port", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name", "from_email", "smtp_host")
    readonly_fields = ("created_at", "updated_at")
