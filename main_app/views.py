from datetime import timedelta

from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EmailLog, ServiceContract, ServiceStatus, Vendor
from .reminders import ReminderService
from .serializers import (
    EmailLogSerializer,
    ReminderSerializer,
    ReminderReportSerializer,
    ServiceContractSerializer,
    ServiceStatusUpdateSerializer,
    VendorSerializer,
)


class PingView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "pong"})


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.prefetch_related("services").all()
    serializer_class = VendorSerializer


class ServiceContractViewSet(viewsets.ModelViewSet):
    queryset = ServiceContract.objects.select_related("vendor").all()
    serializer_class = ServiceContractSerializer

    @action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, pk=None):
        contract = self.get_object()
        serializer = ServiceStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contract.status = serializer.validated_data["status"]
        contract.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(contract).data)


class _BaseWindowServiceList(generics.ListAPIView):
    serializer_class = ServiceContractSerializer

    def _window_queryset(self, field_name: str):
        today = timezone.now().date()
        window_end = today + timedelta(days=15)
        queryset = (
            ServiceContract.objects.select_related("vendor")
            .filter(status__in=[ServiceStatus.ACTIVE, ServiceStatus.PAYMENT_PENDING])
            .filter(**{f"{field_name}__gte": today, f"{field_name}__lte": window_end})
        )
        return queryset


class ExpiringServiceList(_BaseWindowServiceList):
    def get_queryset(self):
        return self._window_queryset("expiry_date")


class PaymentDueServiceList(_BaseWindowServiceList):
    def get_queryset(self):
        return self._window_queryset("payment_due_date")


class ReminderListView(APIView):
    def get(self, request):
        payloads = ReminderService().build_reminder_payloads()
        serializer = ReminderSerializer([payload.as_dict() for payload in payloads], many=True)
        return Response(serializer.data)


class ReminderReportView(APIView):
    def get(self, request):
        report = ReminderService().build_report()
        serializer = ReminderReportSerializer(report)
        return Response(serializer.data)


class ReminderEmailTriggerView(APIView):
    def post(self, request):
        payloads = ReminderService().send_notification_emails()
        serializer = ReminderSerializer([payload.as_dict() for payload in payloads], many=True)
        return Response({"sent": len(payloads), "reminders": serializer.data}, status=status.HTTP_200_OK)


class ReminderEmailLogListView(generics.ListAPIView):
    serializer_class = EmailLogSerializer
    queryset = EmailLog.objects.select_related("contract", "contract__vendor")
