from .serializer import PrecatorioSerializer, PropostaSerializer
from .models import Precatorio, Proposta
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()

class PrecatorioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PrecatorioSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = Precatorio.objects.select_related('dono')

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

    def patch(self, request):
        user = request.user
        
        if not (user.tipo_usuario == User.Perfil.ANALISTA or user.is_superuser):
            return Response({"error":"Somente analistas são autorizados."}, status=status.HTTP_403_FORBIDDEN)
        
        ids = request.data.get("ids",[])
        if not ids:
            return Response({"error":"Lista de IDs não enviada"}, status=status.HTTP_400_BAD_REQUEST)
        
        precatorios = Precatorio.objects.filter(
            id__in=ids, status=Precatorio.Status.PENDENTE
            ).update(status=Precatorio.Status.DISPONIVEL)
        return Response(
            {"result":f"Foram aprovados: {precatorios} precatórios"}, 
            status=status.HTTP_200_OK)

class PropostaPrecatorioAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not (user.tipo_usuario == User.Perfil.INVESTIDOR):
            return Response({"error":"Somente Investidores podem realzar ações de compra."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PropostaSerializer(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save(investidor=user)
        return Response(serializer.data, status=status.HTTP_200_OK)       
        
class GerenciarPropostaViewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        
         




















































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
        
#         return Response({"results": serializer.data},status=status.HTTP_200_OK)
    
    """ 
    APAGAR QUANDO LER

    Quando usamos um "hashmap" dentro de uma função que tenha o escopo de 'handle' ou 'execute',
    ou seja, quando ela vai executar algum código, pelo map, ela busca mais rapido as funções auxiliares.
    um padrão bacana de ser utilizado é o 'strategy' onde trabalha bem esses métodos, principalmente usados em performance.
    poucos if else são performáticos, mas quando a quantidade vai aumentando, vai gerando um problema e isso é ruim para ESCALABILIDADE.

    sempre que houver situações onde tu precise utilizar funções auxiliares, o hashmap é extremamente rápido para lidar com isso O(1) na busca da funçã a ser executada.

    if user.is_superuser:
            return queryset.all()
    
    essa função do superuser, por ser algo mais direto, executa antes e retorna antes, evita ir para o restante do código, geralmente use códigos assim onde nem tudo dentro da view/controller seja necessário executar, já retorna logo.

    existem casos, onde não é o caso especifico desse endpoint, que voce pode retornar logo algo, quando não existe.

    Exemplo:

        if not user.is_authenticated:
            return "Usuário precisa estar autenticado"
    
    é isso :D
    """
    





        


