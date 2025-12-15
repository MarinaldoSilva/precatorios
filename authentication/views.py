from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.db import DatabaseError # Para pegar erros de conexão com banco

from user.serializer import UserSerializer

User = get_user_model()


class SignUp(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Registrar novo usuário",
        description="Cria uma nova conta de usuário (Credor, Investidor ou Analista).",
        request=UserSerializer,
        responses={
            201: UserSerializer,
            400: inline_serializer(name="ValidationError", fields={"errors": serializers.DictField()}),
            500: inline_serializer(name="ServerError", fields={"error": serializers.CharField()})
        },
    )
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
        
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            user = serializer.save()
            
            return Response(
                {"username": user.username, "email": user.email, "tipo_usuario": user.get_tipo_usuario_display()}, 
                status=status.HTTP_201_CREATED
            )
            
        except DatabaseError as e:
            return Response(
                {"error": "Erro ao conectar com o banco de dados.", "detail": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"error": "Erro interno do servidor ao cadastrar usuário.", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
            500: inline_serializer(name="LoginServerError", fields={"error": serializers.CharField()})
        },
    )
    def post(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")

            if not email or not password:
                 return Response(
                    {"error": "Email e senha são obrigatórios."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"error": "Credenciais inválidas."}, 
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            if user.check_password(password):
                refresh_token = TokenObtainPairSerializer.get_token(user=user)
                token_access = refresh_token.access_token

                return Response(
                    {
                        "access": str(token_access),
                        "refresh": str(refresh_token),
                    },
                    status=status.HTTP_201_CREATED,
                )
            
            return Response(
                {"error": "Credenciais inválidas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        except Exception as e:
            return Response(
                {"error": "Erro interno ao realizar login.", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
        try:
            token_refresh = request.data.get("refresh")
            
            if not token_refresh:
                return Response(
                    {"error": "O token de refresh é obrigatório."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            token = RefreshToken(token_refresh)
            token.blacklist()
            
            return Response(status=status.HTTP_205_RESET_CONTENT)

        except TokenError:
            return Response(
                {"error": "Token inválido ou expirado."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": "Erro ao realizar logout.", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )