from django.http import JsonResponse
from django.views import View


class PingView(View):
    """Simple health-check endpoint."""

    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": "pong"})


def ping(request):
    """Function-based helper around PingView for easier wiring in urls."""
    return PingView.as_view()(request)
