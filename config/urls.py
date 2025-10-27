"""
URL configuration for config project.
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include


def healthz(_request):
    # pequeño guiño para troubleshooting rápido
    return JsonResponse({"status": "ok", "note": "si llegaste acá, te debo un café ☕"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("portfolios.api.urls")),  # endpoints de la app
    path("healthz/", healthz),                     # chequeo simple
]
