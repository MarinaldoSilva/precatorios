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
        password = validated_data.pop("password", None)
        user = User.objects.create(**validated_data)

        if password is not None:
            user.set_password(password)
            user.save()

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)
