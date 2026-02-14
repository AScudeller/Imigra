from django.db import transaction, models
from decimal import Decimal
from .models import Pagamento, Parcela, AlocacaoPagamento, Fatura

class FinanceiroService:

    @staticmethod
    def processar_pagamento(pagamento_id):
        """
        Lógica estilo SAP B1: Aloca um pagamento às parcelas mais antigas em aberto (FIFO).
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
                fatura.total_pago = sum(p.valor_pago for p in fatura.parcelas.all()) # Recalcula total real
                
                # Atualizar status da fatura
                if fatura.total_pago >= fatura.total_fatura:
                    fatura.status = 'PAGO'
                elif fatura.total_pago > 0:
                    fatura.status = 'PARCIAL'
                fatura.save()
                
                valor_disponivel -= valor_alocado
            
            # Atualizar saldo do cliente (Se valor_disponivel for tudo usado, abate tudo. Se sobrar, credito)
            cliente = pagamento.cliente
            cliente.saldo_atual -= (pagamento.valor_total - valor_disponivel) 
            # Nota: Saldo Atual no model parece ser Dívida Total. Pagamento reduz Dívida.
            cliente.save()

            return valor_disponivel # Sobra (crédito) se houver

    @staticmethod
    def processar_pagamento_manual(pagamento_id, dados_parcelas):
        """
        Processa pagamento com alocação manual definida pelo usuário.
        dados_parcelas: Lista de dicts [{'id': 1, 'valor': 50.00}, ...]
        """
        with transaction.atomic():
            pagamento = Pagamento.objects.get(id=pagamento_id)
            valor_utilizado = Decimal('0.00')
            
            for item in dados_parcelas:
                parcela_id = item['id']
                if not parcela_id: continue
                
                parcela = Parcela.objects.select_for_update().get(id=parcela_id)
                valor_pagar = Decimal(str(item['valor']))
                
                # Validar saldo da parcela
                saldo_parcela = parcela.valor_parcela - parcela.valor_pago
                valor_alocado = min(valor_pagar, saldo_parcela)
                
                if valor_alocado <= Decimal('0.00'):
                    continue

                # Atualizar Parcela
                parcela.valor_pago += valor_alocado
                parcela.save()
                
                # Criar Alocação
                AlocacaoPagamento.objects.create(
                    pagamento=pagamento,
                    parcela=parcela,
                    valor_alocado=valor_alocado
                )
                
                # Atualizar Fatura (Recalcular do zero para evitar drift)
                fatura = parcela.fatura
                fatura.total_pago = sum(p.valor_pago for p in fatura.parcelas.all())
                
                if fatura.total_pago >= fatura.total_fatura:
                    fatura.status = 'PAGO'
                elif fatura.total_pago > 0:
                    fatura.status = 'PARCIAL'
                else:
                    fatura.status = 'ABERTO'
                fatura.save()
                
                valor_utilizado += valor_alocado

            # Atualizar saldo do cliente
            # Se pagou 100 e alocou 80 (parcial), 20 ficam de crédito? Ou só abatem da dívida global?
            # Vamos assumir que PAGAMENTO SEMPRE ABATE DÍVIDA GLOBAL. A alocação é só para detalhe.
            # Mas se for adiantamento?
            # Simplificação: Saldo Cliente -= Pagamento Total
            
            cliente = pagamento.cliente
            cliente.saldo_atual -= pagamento.valor_total
            cliente.save()
            
            return pagamento.valor_total - valor_utilizado

    @staticmethod
    def estornar_fatura(fatura_id):
        """
        Cancela uma fatura (OINV) e reverte todo o impacto financeiro (RCT2, OCRD).
        """
        with transaction.atomic():
            fatura = Fatura.objects.select_for_update().get(doc_entry=fatura_id)
            if fatura.status == 'CANCELADO':
                return False, "Fatura já está cancelada."

            cliente = fatura.cliente
            valor_total_fatura = fatura.total_fatura
            
            # 1. Buscar parcelas da fatura
            parcelas = fatura.parcelas.all()
            
            # 2. Remover alocações de pagamentos (isso libera o valor dos pagamentos para serem usados em outras faturas)
            for parcela in parcelas:
                # O valor pago na parcela volta a ser zero
                parcela.valor_pago = Decimal('0.00')
                parcela.alocacoes.all().delete()
                parcela.save()

            # 3. Atualizar status da fatura
            fatura.status = 'CANCELADO'
            fatura.total_pago = Decimal('0.00')
            fatura.save()

            # 4. Reverter Saldo do Cliente
            # Se a fatura aumenta a dívida, cancelá-la DIMINUI o saldo devedor.
            cliente.saldo_atual -= valor_total_fatura
            cliente.save()

            # 5. Reverter status do orçamento vinculado (se houver)
            from .models import Orcamento
            orcamento = Orcamento.objects.filter(cliente=cliente, valor_total=valor_total_fatura, status='ACEITO').order_by('-id').first()
            if orcamento:
                orcamento.status = 'ENVIADO'
                orcamento.save()

            return True, "Fatura estornada com sucesso. O saldo do cliente foi ajustado e pagamentos desalocados."
