from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PrecatorioViewSet

router = DefaultRouter()

router.register(r"", PrecatorioViewSet, basename="precatorios")

urlpatterns = [ 
    path("", include(router.urls))
]