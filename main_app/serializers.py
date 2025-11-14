from rest_framework import serializers

from .models import EmailLog, ServiceContract, ServiceStatus, Vendor
from .reminders import ReminderReport


class ServiceContractSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="vendor.name", read_only=True)

    class Meta:
        model = ServiceContract
        fields = [
            "id",
            "vendor",
            "vendor_name",
            "service_name",
            "start_date",
            "expiry_date",
            "payment_due_date",
            "amount",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ActiveServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceContract
        fields = [
            "id",
            "service_name",
            "expiry_date",
            "payment_due_date",
            "amount",
            "status",
        ]


class VendorSerializer(serializers.ModelSerializer):
    active_services = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        fields = [
            "id",
            "name",
            "contact_person",
            "email",
            "phone",
            "status",
            "active_services",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "active_services"]

    def get_active_services(self, vendor: Vendor):
        services = vendor.services.filter(status=ServiceStatus.ACTIVE)
        return ActiveServiceSerializer(services, many=True).data


class ServiceStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ServiceStatus.choices)


class ReminderSerializer(serializers.Serializer):
    contract_id = serializers.IntegerField()
    vendor = serializers.CharField()
    service_name = serializers.CharField()
    expiry_date = serializers.DateField()
    payment_due_date = serializers.DateField()
    expiry_color = serializers.CharField()
    payment_color = serializers.CharField()
    days_until_expiry = serializers.IntegerField()
    days_until_payment = serializers.IntegerField()
    recipient = serializers.EmailField()


class ReminderReportSerializer(serializers.Serializer):
    generated_on = serializers.DateField()
    window_days = serializers.IntegerField()
    total_contracts = serializers.IntegerField()
    totals_by_color = serializers.DictField(child=serializers.IntegerField())
    expiry_totals_by_color = serializers.DictField(child=serializers.IntegerField())
    payment_totals_by_color = serializers.DictField(child=serializers.IntegerField())
    payloads = ReminderSerializer(many=True)

    def to_representation(self, instance: ReminderReport | dict):
        if isinstance(instance, ReminderReport):
            instance = instance.as_dict()
        return super().to_representation(instance)


class EmailLogSerializer(serializers.ModelSerializer):
    vendor = serializers.CharField(source="contract.vendor.name", read_only=True)
    service_name = serializers.CharField(source="contract.service_name", read_only=True)

    class Meta:
        model = EmailLog
        fields = [
            "id",
            "contract",
            "vendor",
            "service_name",
            "recipient",
            "sender",
            "subject",
            "body",
            "success",
            "error_message",
            "created_at",
        ]
        read_only_fields = fields
