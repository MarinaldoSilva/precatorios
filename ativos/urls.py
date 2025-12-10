from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PrecatorioViewSet, AprovarPrecatorioBulkView, PropostaPrecatorioAPIView, GerenciarPropostaViewAPIView

router = DefaultRouter()

router.register(r"", PrecatorioViewSet, basename="precatorios")

urlpatterns = [ 
    path("proposta/", PropostaPrecatorioAPIView.as_view(), name="proposta"),
    path("aprovacao/bulk/", AprovarPrecatorioBulkView.as_view(), name="aprovacao-bulk"),

    path("gerenciar/propostas/", GerenciarPropostaViewAPIView.as_view(), name="gerenciar-propostas"),
    path("", include(router.urls))
]