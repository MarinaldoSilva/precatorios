from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
User = get_user_model()


class BaseUserService:
    def __init__(self, user):

        if not user:
            raise NotAuthenticated("Nenhum usuário foi fornecido para aplicação.")
        
        if not user.is_authenticated:
            raise PermissionDenied("Somente usuários autenticados para acessar a função.")

        self.user = user
         
