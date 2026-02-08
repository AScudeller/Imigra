from django.db import transaction, models
from decimal import Decimal
from .models import Pagamento, Parcela, AlocacaoPagamento, Fatura

class FinanceiroService:
    @staticmethod
    def processar_pagamento(pagamento_id):
        """
        Lógica estilo SAP B1: Aloca um pagamento às parcelas mais antigas em aberto.
        """
        with transaction.atomic():
            pagamento = Pagamento.objects.select_for_update().get(id=pagamento_id)
            valor_disponivel = pagamento.valor_total
            
            # 1. Buscar parcelas em aberto (ABERTO ou ATRASADO) do cliente, ordenadas por vencimento
            parcelas_pendentes = Parcela.objects.filter(
                fatura__cliente=pagamento.cliente,
                valor_pago__lt=models.F('valor_parcela')
            ).order_by('data_vencimento', 'fatura_id', 'num_parcela')

            for parcela in parcelas_pendentes:
                if valor_disponivel <= 0:
                    break
                
                falta_pagar = parcela.valor_parcela - parcela.valor_pago
                valor_alocado = min(valor_disponivel, falta_pagar)
                
                # Atualizar parcela
                parcela.valor_pago += valor_alocado
                parcela.save()
                
                # Criar registro de alocação (Audit Trail)
                AlocacaoPagamento.objects.create(
                    pagamento=pagamento,
                    parcela=parcela,
                    valor_alocado=valor_alocado
                )
                
                # Atualizar a Fatura pai
                fatura = parcela.fatura
                fatura.total_pago += valor_alocado
                
                # Atualizar status da fatura
                if fatura.total_pago >= fatura.total_fatura:
                    fatura.status = 'PAGO'
                elif fatura.total_pago > 0:
                    fatura.status = 'PARCIAL'
                fatura.save()
                
                valor_disponivel -= valor_alocado
            
            # Atualizar saldo do cliente (opcional, dependendo da regra de saldo atual)
            cliente = pagamento.cliente
            cliente.saldo_atual -= (pagamento.valor_total - valor_disponivel)
            cliente.save()

            return valor_disponivel # Sobra (crédito) se houver
