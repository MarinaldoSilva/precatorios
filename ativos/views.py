from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ativos.services.service import PropostaService, RecomendacaoService

from .models import Precatorio
from .serializer import PrecatorioSerializer, PropostaSerializer

User = get_user_model()


@extend_schema(tags=["Precatórios (CRUD)"])
class PrecatorioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PrecatorioSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Precatorio.objects.select_related("dono")

        if user.tipo_usuario == User.Perfil.ANALISTA or user.is_superuser:
            return queryset.all()
        elif user.tipo_usuario == User.Perfil.CREDOR:
            return queryset.filter(dono=user)
        elif user.tipo_usuario == User.Perfil.INVESTIDOR:
            return queryset.filter(status=Precatorio.Status.DISPONIVEL)
        else:
            return Precatorio.objects.none()


class AprovarPrecatorioBulkView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Aprovação em Massa (Analista)",
        description="Recebe uma lista de IDs de precatórios e muda o status para DISPONÍVEL.",
        request=inline_serializer(
            name="AprovacaoBulkRequest",
            fields={"ids": serializers.ListField(child=serializers.UUIDField())},
        ),
        responses={200: inline_serializer(name="AprovacaoResponse", fields={"result": serializers.CharField()})},
    )
    def patch(self, request):
        user = request.user

        if not (user.tipo_usuario == User.Perfil.ANALISTA or user.is_superuser):
            return Response(
                {"error": "Somente analistas são autorizados."},
                status=status.HTTP_403_FORBIDDEN,
            )

        ids = request.data.get("ids", [])
        if not ids:
            return Response(
                {"error": "Lista de IDs não enviada"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        precatorios = Precatorio.objects.filter(id__in=ids, status=Precatorio.Status.PENDENTE).update(status=Precatorio.Status.DISPONIVEL)
        return Response(
            {"result": f"Foram aprovados: {precatorios} precatórios"},
            status=status.HTTP_200_OK,
        )


class PropostaPrecatorioAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Realizar Proposta (Investidor)",
        description="Cria uma proposta de compra para um precatório disponível.",
        request=PropostaSerializer,
        responses={201: PropostaSerializer},
    )
    def post(self, request):
        user = request.user
        service = PropostaService(user=user)
        if not (user.tipo_usuario == User.Perfil.INVESTIDOR):
            return Response(
                {"error": "Somente Investidores podem realzar ações de compra."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PropostaSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        #service já cria a salva, recuperamos o valor e serializamos novamente, com o novo serializar feito, os dados novos serão salvos no banco e podemos retornar na resposta da api
        nova_proposta = service.criar_proposta(validated_data=serializer.validated_data)
        proposta = PropostaSerializer(nova_proposta).data
        return Response(proposta, status=status.HTTP_201_CREATED)


class GerenciarPropostaViewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Gerenciar Proposta (Credor)",
        description="Aceita ou Recusa uma proposta. Aceitar vende o ativo automaticamente.",
        request=inline_serializer(
            name="GerenciarPropostaRequest",
            fields={
                "proposta_id": serializers.UUIDField(),
                "acao": serializers.ChoiceField(choices=["ACEITAR", "RECUSAR"]),
            },
        ),
        responses={200: inline_serializer(name="GerenciarResponse", fields={"message": serializers.CharField()})},
    )
    def post(self, request):
        user = request.user

        if not (user.tipo_usuario == User.Perfil.CREDOR or user.is_superuser):
            return Response(
                {"error": "Somente credores podem aceitar propostas."},
                status=status.HTTP_403_FORBIDDEN,
            )

        proposta_id = request.data.get("proposta_id")
        acao = request.data.get("acao", "").upper()

        service = PropostaService(user)

        proposta, error = service.resposta_proposta(proposta_id=proposta_id, acao=acao)

        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"result": proposta}, status=status.HTTP_200_OK)


class RecomendacoesPropostaAPIView(APIView):

    @extend_schema(summary="Melhores precatórios (Deságio)", description="Top 5 de melhores precatórios com base no valor de deságio", tags=["Recomendações"], responses={200: PrecatorioSerializer})
    def get(self, request):
        user = request.user
        service = RecomendacaoService(user=user)
        melhores_recomendacoes = service.buscar_oportunidades()

        serializer = PrecatorioSerializer(melhores_recomendacoes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


{
    # class PrecatorioViewSet(viewsets.ModelViewSet):
    #     permission_classes = [IsAuthenticated]
    #     serializer_class = PrecatorioSerializer
    #     def get_queryset(self):
    #         user = self.request.user
    #         queryset = Precatorio.objects.select_related('dono')
    #         if user.is_superuser:
    #             return queryset.all()
    #         user_filter = {
    #             "ANALISTA": lambda: queryset.all(),
    #             "CREDOR": lambda: queryset.filter(dono=user),
    #             "INVESTIDOR": lambda: queryset.filter(status=Precatorio.Status.DISPONIVEL)
    #         }
    #         filtro_role = user_filter.get(user.tipo_usuario, lambda: queryset.none())
    #         return filtro_role()
    #     def list(self, request, *args, **kwargs):
    #         queryset = self.filter_queryset(self.get_queryset())
    #         serializer = self.get_serializer(queryset, many=True)
    #         return Response({"results": serializer.data},status=status.HTTP_200_OK)}
}
