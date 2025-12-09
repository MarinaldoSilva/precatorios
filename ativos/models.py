from django.db import models
from django.conf import settings
from uuid import uuid4

class Precatorio(models.Model):
    class Status(models.IntegerChoices):
        PENDENTE = 1, "Pendente"
        DISPONIVEL = 2, "Disponivel"
        VENDIDO = 3, "Vendido"

    id = models.UUIDField(primary_key=True, default=uuid4, unique=True, editable=False)
    titulo = models.CharField(max_length=150)
    valor_face = models.DecimalField(max_digits=12, decimal_places=2)
    valor_inicial = models.DecimalField(max_digits=12, decimal_places=2)
    tribunal = models.CharField(max_length=50)
    status = models.SmallIntegerField(choices = Status.choices, default=Status.PENDENTE, db_index=True)
    dono = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='precatorios')

    def __str__(self):
        return f"{self.titulo} - R$ {self.valor_inicial}"

class Proposta(models.Model):
    class Status(models.IntegerChoices):
        AGUARDANDO = 1, "Aguardando"
        ACEITA = 2, "Aceita"
        RECUSADA = 3, "Recusada"

    precatorio = models.ForeignKey(Precatorio, on_delete=models.CASCADE, related_name="propostas")
    investidor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='propostas')
    valor_oferta = models.DecimalField(max_digits=10, decimal_places=2)
    data_criacao = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(choices=Status.choices, default=Status.AGUARDANDO, db_index=True)

    def __str__(self):
        return f"Proposta de {self.investidor} - Precatório {self.precatorio}"