from datetime import timedelta
from django.db.models import Prefetch, Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ServiceContract, Vendor
from .serializers import (
    ServiceContractSerializer,
    ServiceContractWriteSerializer,
    VendorSerializer,
    VendorWriteSerializer,
)


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all().prefetch_related('services')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return VendorWriteSerializer
        return VendorSerializer

    def list(self, request, *args, **kwargs):
        active_services = Prefetch(
            'services',
            queryset=ServiceContract.objects.filter(status=ServiceContract.STATUS_ACTIVE),
        )
        queryset = self.filter_queryset(
            Vendor.objects.all().prefetch_related(active_services)
        )
        page = self.paginate_queryset(queryset)
        serializer = VendorSerializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='with-active-services')
    def with_active_services(self, request):
        return self.list(request)


class ServiceContractViewSet(viewsets.ModelViewSet):
    queryset = ServiceContract.objects.select_related('vendor')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ServiceContractWriteSerializer
        return ServiceContractSerializer

    @action(detail=False, methods=['get'], url_path='expiring-soon')
    def expiring_soon(self, request):
        today = timezone.now().date()
        horizon = today + timedelta(days=15)
        queryset = self.filter_queryset(
            self.get_queryset().filter(expiry_date__range=(today, horizon))
        )
        page = self.paginate_queryset(queryset)
        serializer = ServiceContractSerializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='payment-due')
    def payment_due_soon(self, request):
        today = timezone.now().date()
        horizon = today + timedelta(days=15)
        queryset = self.filter_queryset(
            self.get_queryset().filter(payment_due_date__range=(today, horizon))
        )
        page = self.paginate_queryset(queryset)
        serializer = ServiceContractSerializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        contract = self.get_object()
        status_value = request.data.get('status')
        valid_values = dict(ServiceContract.STATUS_CHOICES).keys()
        if status_value not in valid_values:
            return Response(
                {'detail': 'Invalid status value.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        contract.status = status_value
        contract.save(update_fields=['status'])
        return Response(ServiceContractSerializer(contract).data)

    @action(detail=False, methods=['get'], url_path='reminders')
    def reminders(self, request):
        today = timezone.now().date()
        horizon = today + timedelta(days=15)
        queryset = self.get_queryset().filter(
            Q(expiry_date__range=(today, horizon)) | Q(payment_due_date__range=(today, horizon))
        )
        reminders = []
        for contract in queryset:
            reminder = {
                'service_id': contract.id,
                'vendor': contract.vendor.name,
                'service_name': contract.service_name,
                'expiry_date': contract.expiry_date,
                'payment_due_date': contract.payment_due_date,
                'color_code': ServiceContractSerializer(contract).data['color_code'],
                'email_subject': f"Reminder: {contract.service_name}",
                'email_body': (
                    f"Hi {contract.vendor.contact_person}, your service {contract.service_name} is approaching its"
                    f" expiry/payment deadline."
                ),
            }
            reminders.append(reminder)
        return Response({'count': len(reminders), 'results': reminders})
