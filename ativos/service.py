from .services.base_service import BaseUserService
from django.db import transaction
from ativos.models import Precatorio, Proposta
from django.contrib.auth import get_user_model

user = get_user_model()

class PropostaService(BaseUserService):
    def resposta_proposta(self, proposta_id, acao):
        
        try:
            proposta = Proposta.objects.get(id=proposta_id, precatorio__dono=self.user)
        except Proposta.DoesNotExist:
            return None, "Proposta não encontrada"
            
        precatorio = proposta.precatorio

        if precatorio.status != Precatorio.Status.DISPONIVEL:
            return None, "Precatório não dispónivel para venda"
            
        if acao == 'ACEITAR':
            with transaction.atomic():
                proposta.status = Proposta.Status.ACEITA
                precatorio.Status = Precatorio.Status.VENDIDO
                return "venda do precatorio realizada com sucesso.", None
        elif acao == "RECUSAR":
            proposta.status = Proposta.Status.RECUSADA
            proposta.save()
            return "Proposta recusada", None
        return None, "Ação invalida, aceita somente ACEITAR e RECUSAR"
        