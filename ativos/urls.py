from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PrecatorioViewSet, AprovarPrecatorioBulkView, PropostaPrecatorioAPIView

router = DefaultRouter()

router.register(r"", PrecatorioViewSet, basename="precatorios")

urlpatterns = [ 
    path("", include(router.urls)),
    path("aprovacao/", PropostaPrecatorioAPIView.as_view(), name="aprovacao"),
    path("aprovacao-bulk/", AprovarPrecatorioBulkView.as_view(), name="aprovacao-bulk")
]