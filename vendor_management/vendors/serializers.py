from datetime import date
from rest_framework import serializers

from .models import ServiceContract, Vendor


class ServiceContractSerializer(serializers.ModelSerializer):
    is_expiring_soon = serializers.SerializerMethodField()
    is_payment_due_soon = serializers.SerializerMethodField()
    color_code = serializers.SerializerMethodField()

    class Meta:
        model = ServiceContract
        fields = [
            'id',
            'vendor',
            'service_name',
            'start_date',
            'expiry_date',
            'payment_due_date',
            'amount',
            'status',
            'is_expiring_soon',
            'is_payment_due_soon',
            'color_code',
        ]
        read_only_fields = ['color_code', 'is_expiring_soon', 'is_payment_due_soon']

    def get_is_expiring_soon(self, obj: ServiceContract) -> bool:
        return obj.is_expiring_soon

    def get_is_payment_due_soon(self, obj: ServiceContract) -> bool:
        return obj.is_payment_due_soon

    def get_color_code(self, obj: ServiceContract) -> str:
        today = date.today()
        if obj.expiry_date < today or obj.payment_due_date < today:
            return 'red'
        if obj.is_expiring_soon or obj.is_payment_due_soon:
            return 'amber'
        return 'green'


class VendorSerializer(serializers.ModelSerializer):
    services = ServiceContractSerializer(many=True, read_only=True)

    class Meta:
        model = Vendor
        fields = [
            'id',
            'name',
            'contact_person',
            'email',
            'phone',
            'status',
            'services',
        ]


class VendorWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'name', 'contact_person', 'email', 'phone', 'status']


class ServiceContractWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceContract
        fields = [
            'id',
            'vendor',
            'service_name',
            'start_date',
            'expiry_date',
            'payment_due_date',
            'amount',
            'status',
        ]
