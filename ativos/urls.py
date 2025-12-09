from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PrecatorioViewSet, AprovarPrecatorioBulkView, PropostaPrecatorioAPIView

router = DefaultRouter()

router.register(r"", PrecatorioViewSet, basename="precatorios")

urlpatterns = [ 
    path("proposta/", PropostaPrecatorioAPIView.as_view(), name="proposta"),
    path("aprovacao-bulk/", AprovarPrecatorioBulkView.as_view(), name="aprovacao-bulk"),
    path("", include(router.urls))
]