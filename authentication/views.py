from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from user.serializer import UserSerializer

User = get_user_model()


class SignUp(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"username": user.username, "email": user.email})


class SignIn(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"email_not_found":"Email não encontrado na base de dados"},
                            status=status.HTTP_404_NOT_FOUND)
        if user.check_password(password):
            refresh_token = TokenObtainPairSerializer.get_token(user=user)
            token_access = refresh_token.access_token

            return Response({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "access": str(token_access),
                "refresh": str(refresh_token)
            }, status.HTTP_201_CREATED)
        return Response({
            "error":"Verifique o Email ou senha e tente novamente."
            },status.HTTP_401_UNAUTHORIZED)
    

class SignOut(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token_refresh = request.data.get("refresh")
        if not token_refresh:
            return Response({
                "error_token":"O token de acesso não foi localizado"
                },status=status.HTTP_401_UNAUTHORIZED)
        try:
            token = RefreshToken(token_refresh)
            token.blacklist()
        except TokenError:
            return Response({
                "erro":"Não foi possível invalidar o token"},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)