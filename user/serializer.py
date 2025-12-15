from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):

    usuario = serializers.CharField(source="get_tipo_usuario_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "is_superuser",
            "username",
            "email",
            "first_name",
            "last_name",
            "tipo_usuario",
            "usuario",
            "password",
        ]

        read_only_fields = ["id"]

        extra_kwargs = {"password": {"write_only": True}}

    # def create(self, validated_data):
    #     user = User.objects.create_user(**validated_data)
    #     return user

    def create(self, validated_data):
        # Print 1: Vamos ver o que chegou aqui
        print(f"DEBUG - Validated Data Completo: {validated_data}")
        
        password = validated_data.pop("password", None)
        
        # Print 2: Vamos ver se a senha foi capturada
        print(f"DEBUG - Senha Capturada: {password}")

        user = User.objects.create(**validated_data)

        if password is not None:
            print("DEBUG - Entrou no IF da senha. Criptografando...")
            user.set_password(password)
            user.save()
        else:
            print("DEBUG - PERIGO: Senha veio vazia (None)! O usuário ficará bloqueado.")

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)
