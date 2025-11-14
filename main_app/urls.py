from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ExpiringServiceList,
    PaymentDueServiceList,
    PingView,
    ReminderEmailTriggerView,
    ReminderListView,
    ServiceContractViewSet,
    VendorViewSet,
)

router = DefaultRouter()
router.register(r"vendors", VendorViewSet, basename="vendor")
router.register(r"services", ServiceContractViewSet, basename="service")

urlpatterns = [
    path("ping/", PingView.as_view(), name="ping"),
    path("", include(router.urls)),
    path("services/expiring-soon/", ExpiringServiceList.as_view(), name="services-expiring"),
    path("services/payment-due/", PaymentDueServiceList.as_view(), name="services-payment-due"),
    path("services/reminders/", ReminderListView.as_view(), name="services-reminders"),
    path(
        "services/reminders/send-emails/",
        ReminderEmailTriggerView.as_view(),
        name="services-reminders-send",
    ),
]
