from rest_framework.routers import DefaultRouter

from .views import ServiceContractViewSet, VendorViewSet

router = DefaultRouter()
router.register(r'vendors', VendorViewSet, basename='vendor')
router.register(r'services', ServiceContractViewSet, basename='service')

urlpatterns = router.urls
