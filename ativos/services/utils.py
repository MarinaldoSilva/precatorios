from decimal import Decimal

class PrecatorioUtils:
    @staticmethod
    def calculo_comissao(valor_face):

        valor_face = (valor_face if isinstance(valor_face, Decimal) else Decimal(str(valor_face)))
            
        if valor_face <= Decimal('50000'):
            comissao = ((valor_face * Decimal('5')) / 100)
            return comissao
        elif valor_face > Decimal('50000') and valor_face <= Decimal('200000'):
            comissao = ((valor_face * Decimal('3')) / 100)
            return comissao
        else:
            comissao = ((valor_face * Decimal('1.5')) / 100)
            return comissao