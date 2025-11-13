from django.contrib import admin

from .models import ServiceContract, Vendor


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone', 'status')
    search_fields = ('name', 'email', 'contact_person')


@admin.register(ServiceContract)
class ServiceContractAdmin(admin.ModelAdmin):
    list_display = (
        'service_name',
        'vendor',
        'start_date',
        'expiry_date',
        'payment_due_date',
        'status',
    )
    list_filter = ('status', 'expiry_date')
    search_fields = ('service_name', 'vendor__name')
