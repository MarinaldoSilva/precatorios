from decimal import Decimal
from rest_framework import serializers
from django.db import transaction
from django.db.models import Sum

from ativos.models import Precatorio, Proposta

from .base_service import BaseUserService

class PropostaService(BaseUserService):
    
    def criar_proposta(self, validated_data):
        # proposta = Proposta.objects.filter(investidor=self.user, status=Proposta.Status.AGUARDANDO)
        user = self.user

        proposta = Proposta.objects.filter(
            investidor=user, 
            status=Proposta.Status.AGUARDANDO
        ).aggregate(
            total=Sum('valor_oferta')
        )

        valor_proposta = proposta['total'] or Decimal('0')

        #somar_ofertas = sum(p.valor_oferta for p in proposta)
        soma_total = valor_proposta + validated_data['valor_oferta']
        limte = Decimal('500000')
        
        if soma_total > limte:
            raise serializers.ValidationError(f"Você propostas pendentes que juntas somam mais de {limte}.")
        return Proposta.objects.create(
            investidor = self.user,
            **validated_data
        ) 

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
        ganho_minimo = Decimal("0.20")
        precatorios_filter = [p for p in precatorios if p.valor_face > 0 and (p.valor_face - p.valor_inicial) >= (p.valor_face * ganho_minimo)]
        precatorios_filter.sort(key=lambda p: (p.valor_face - p.valor_inicial), reverse=True)
        return precatorios_filter[:5]

{
# def buscar_oportunidades(self):
#         from django.db.models import Q, F
#         ganho_minimo = Decimal("0.20")        
#         qs = Precatorio.objects.filter(
#             Q(status=Precatorio.Status.DISPONIVEL) & Q(valor_face__gt=0)
#         ).annotate(
#             lucro_bruto=F('valor_face') - F('valor_inicial')
#         ).filter(
#             Q(lucro_bruto__gte=F('valor_face') * ganho_minimo)
#         ).order_by('-lucro_bruto')
#         return qs[:5]
}


class GestaoAtivosService(BaseUserService):
    def verificar_dados_ativos(self, validated_data):
        ...