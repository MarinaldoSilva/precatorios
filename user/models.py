from django.db import models
from uuid import uuid4
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    
    class Perfil(models.IntegerChoices):
        CREDOR = 1, "Credor",
        INVESTIDOR = 2, "Investidor"
        ANALISTA = 3, "Analista"
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False ,unique=True)
    tipo_usuario = models.PositiveSmallIntegerField(choices=Perfil.choices, default=Perfil.INVESTIDOR)
    email = models.EmailField(unique=True, null=False, blank=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


