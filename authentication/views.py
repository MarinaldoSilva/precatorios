from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from user.serializer import UserSerializer

User = get_user_model()


class SignUp(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Registrar novo usuário",
        description="Cria uma nova conta de usuário (Credor, Investidor ou Analista).",
        request=UserSerializer,
        responses={201: UserSerializer},
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"username": user.username, "email": user.email})


class SignIn(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Login (Gerar Token)",
        description="Autentica o usuário e retorna Access e Refresh Tokens.",
        request=inline_serializer(
            name="LoginRequest",
            fields={
                "email": serializers.EmailField(),
                "password": serializers.CharField(),
            },
        ),
        responses={
            201: inline_serializer(
                name="LoginResponse",
                fields={
                    "id": serializers.UUIDField(),
                    "username": serializers.CharField(),
                    "email": serializers.EmailField(),
                    "access": serializers.CharField(),
                    "refresh": serializers.CharField(),
                },
            ),
            401: inline_serializer(name="LoginError", fields={"error": serializers.CharField()}),
        },
    )
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"email_not_found": "Email não encontrado na base de dados"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if user.check_password(password):
            refresh_token = TokenObtainPairSerializer.get_token(user=user)
            token_access = refresh_token.access_token

            return Response(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "access": str(token_access),
                    "refresh": str(refresh_token),
                },
                status.HTTP_201_CREATED,
            )
        return Response(
            {"error": "Verifique o Email ou senha e tente novamente."},
            status.HTTP_401_UNAUTHORIZED,
        )


class SignOut(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Logout",
        description="Invalida o Refresh Token fornecido.",
        request=inline_serializer(name="LogoutRequest", fields={"refresh": serializers.CharField()}),
        responses={205: None},
    )
    def post(self, request):
        token_refresh = request.data.get("refresh")
        if not token_refresh:
            return Response(
                {"error_token": "O token de acesso não foi localizado"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            token = RefreshToken(token_refresh)
            token.blacklist()
        except TokenError:
            return Response(
                {"erro": "Não foi possível invalidar o token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_205_RESET_CONTENT)
