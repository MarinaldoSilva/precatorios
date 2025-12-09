from .models import Precatorio, Proposta
from user.serializer import UserSerializer
from rest_framework import serializers


class PrecatorioSerializer(serializers.ModelSerializer):
    dono = UserSerializer(read_only=True)
    
    class Meta:
        model = Precatorio
        fields = "__all__"

        read_only_fields = ['id', 'dono', 'status']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['dono'] = user
        return super().create(validated_data)


class PropostaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposta
        fields = ['id', 'precatorio', 'valor_oferta', 'data_criacao', 'status']
        read_only_fields = ['id', 'investidor', 'data_criacao', 'status']

    def validate(self, data):
        precatorio_obj = data["precatorio"]
        valor_da_oferta = data["valor_oferta"]

        if precatorio_obj.status != Precatorio.Status.DISPONIVEL:
            raise serializers.ValidationError(
                {"error": "O precatório não disponivel para compra"}
            )
        if valor_da_oferta >= precatorio_obj.valor_face:
            raise serializers.ValidationError({"error":"O valor oferecido não pode ser maior que o ofertado pelo credor."})
        
        return data
        



    

