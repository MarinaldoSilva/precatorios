from rest_framework import serializers
from user.serializer import UserSerializer

from .models import Precatorio, Proposta
from user.models import User

class PrecatorioSerializer(serializers.ModelSerializer):
    dono = UserSerializer(read_only=True)
    status = serializers.CharField(source="get_status_display", read_only=True)
    lucro_esperado = serializers.SerializerMethodField()
    percentual_lucro = serializers.SerializerMethodField()

    class Meta:
        model = Precatorio
        fields = ["id", "titulo", "valor_face", "valor_inicial", "lucro_esperado", "percentual_lucro", "tribunal", "status", "dono", "comissao"]

        read_only_fields = ["id", "dono", "status", "comissao"]


    def to_representation(self, instance):
        """
        Este método é chamado AUTOMATICAMENTE no DRF toda vez que ele
        precisa transformar o objeto do banco em JSON para responder alguém.
        """
        #usuário do contexto na requisição
        request = self.context.get('request')
        #metodo padrão para criar um dicionário completo com todos os campos
        data = super().to_representation(instance)

        #agora sabemos que request.user existe
        user = request.user

        if not request or hasattr(request, 'user'):
            return data
        
        if user.is_authenticated and user.tipo_usuario == User.Perfil.INVESTIDOR:
            data.pop('comissao', None)

        return data
    
    def get_lucro_esperado(self, obj: Precatorio):
        return obj.valor_face - obj.valor_inicial

    def get_percentual_lucro(self, obj: Precatorio):
        if obj.valor_face > 0:
            lucro_percentual = (obj.valor_face - obj.valor_inicial) / (obj.valor_face) * 100
            calculo = round(lucro_percentual, 2)

            if calculo % 1 == 0:
                return int(calculo)
            return calculo
        return None

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["dono"] = user
        return super().create(validated_data)


class PropostaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposta
        fields = ["id", "precatorio", "valor_oferta", "data_criacao", "status"]

        read_only_fields = ["id", "investidor", "data_criacao", "status"]

    def validate(self, data):
        precatorio = data["precatorio"]
        valor_da_oferta = data["valor_oferta"]

        if precatorio.status != Precatorio.Status.DISPONIVEL:
            raise serializers.ValidationError({"error": "O precatório não disponivel para compra"})
        if valor_da_oferta >= precatorio.valor_face:
            raise serializers.ValidationError({"error": "O valor oferecido não pode ser maior que o ofertado pelo credor."})

        return data
