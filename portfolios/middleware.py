# portfolios/middleware.py
from django.conf import settings

class EasterEggHeaderMiddleware:
    """Agrega un header mínimo para nuestro huevo de pascua."""
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        response = self.get_response(request)
        msg = getattr(settings, "EASTER_EGG_MSG", "")
        if msg:
            response["X-Mat-Egg"] = msg
        return response
