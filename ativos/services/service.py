from django.db import transaction
from decimal import Decimal

from ativos.models import Precatorio, Proposta

from .base_service import BaseUserService


class PropostaService(BaseUserService):
    def resposta_proposta(self, proposta_id, acao):

        try:
            proposta = Proposta.objects.get(id=proposta_id, precatorio__dono=self.user)
        except Proposta.DoesNotExist:
            return None, "Proposta não encontrada"

        precatorio = proposta.precatorio

        if precatorio.status != Precatorio.Status.DISPONIVEL:
            return None, "Precatório não dispónivel para venda"

        if acao == "ACEITAR":
            with transaction.atomic():
                proposta.status = Proposta.Status.ACEITA
                precatorio.Status = Precatorio.Status.VENDIDO
                return "venda do precatorio realizada com sucesso.", None
        elif acao == "RECUSAR":
            proposta.status = Proposta.Status.RECUSADA
            proposta.save()
            return "Proposta recusada", None
        return None, "Ação invalida, aceita somente ACEITAR e RECUSAR"


class RecomendacaoService(BaseUserService):
    
    def buscar_oportunidades(self):
        precatorios = Precatorio.objects.filter(status=Precatorio.Status.DISPONIVEL)
        ganho_minimo = Decimal('0.20')
        precatorios_filter = [
            p for p in precatorios 
            if p.valor_face > 0 and (p.valor_face - p.valor_inicial) >= (p.valor_face * ganho_minimo) 
        ]

        precatorios_filter.sort(
            key=lambda p: (p.valor_face - p.valor_inicial), reverse=True
        )

        return precatorios_filter[:5]