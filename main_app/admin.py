from django.contrib import admin, messages
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.translation import gettext_lazy as _

from .models import EmailCredential, EmailLog, ServiceContract, Vendor
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
    change_list_template = "admin/main_app/servicecontract/change_list.html"

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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "reminder-report/",
                self.admin_site.admin_view(self.reminder_report_view),
                name="main_app_servicecontract_reminder_report",
            )
        ]
        return custom_urls + urls

    def reminder_report_view(self, request):
        report = ReminderService().build_report()
        report_dict = report.as_dict()
        color_rows = []
        for color in ("red", "yellow", "green"):
            color_rows.append(
                {
                    "name": color,
                    "overall": report_dict["totals_by_color"].get(color, 0),
                    "expiry": report_dict["expiry_totals_by_color"].get(color, 0),
                    "payment": report_dict["payment_totals_by_color"].get(color, 0),
                }
            )
        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "report": report,
            "report_data": report_dict,
            "color_rows": color_rows,
            "title": _("Reminder report"),
        }
        return TemplateResponse(
            request,
            "admin/main_app/servicecontract/reminder_report.html",
            context,
        )


@admin.register(EmailCredential)
class EmailCredentialAdmin(admin.ModelAdmin):
    list_display = ("name", "from_email", "smtp_host", "smtp_port", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name", "from_email", "smtp_host")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("contract", "recipient", "success", "created_at")
    search_fields = ("recipient", "contract__service_name", "contract__vendor__name")
    list_filter = ("success", "contract__status")
    readonly_fields = (
        "contract",
        "recipient",
        "sender",
        "subject",
        "body",
        "success",
        "error_message",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):  # pragma: no cover - admin integration
        return False

    def has_change_permission(self, request, obj=None):  # pragma: no cover
        return False
