from .models import Precatorio, Proposta
from user.serializer import UserSerializer
from rest_framework import serializers


class PrecatorioSerializer(serializers.ModelSerializer):
    dono = UserSerializer(read_only=True)
    
    class Meta:
        model = Precatorio
        fields = "__all__"

        read_only_fields = ['id', 'dono']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['dono'] = user
        return super().create(validated_data)