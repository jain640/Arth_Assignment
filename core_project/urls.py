"""URL configuration for core_project."""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


def api_root(_request):
    """Return a helpful landing response for the bare domain path."""

    return JsonResponse(
        {
            "message": "Welcome to the Service Reminder API",
            "available_endpoints": {
                "token": "/api/token/",
                "token_refresh": "/api/token/refresh/",
                "api_root": "/api/",
            },
        }
    )


urlpatterns = [
    path("", api_root, name="root"),
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include("main_app.urls")),
]
