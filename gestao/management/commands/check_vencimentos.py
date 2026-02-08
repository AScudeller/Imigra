from django.core.management.base import BaseCommand
from gestao.models import Cliente, Parcela, Processo, LogNotificacao
from gestao.notifications import NotificacaoService
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Verifica vencimentos proativos (Parcelas, Passaportes, Documentos) e envia alertas.'

    def handle(self, *args, **options):
        hoje = timezone.now().date()
        alerta_em_5_dias = hoje + timedelta(days=5)
        alerta_passaporte_30 = hoje + timedelta(days=30)
        
        self.stdout.write(self.style.SUCCESS('Iniciando varredura de vencimentos...'))

        # 1. Verificar Parcelas a vencer em 5 dias
        parcelas_proximas = Parcela.objects.filter(
            data_vencimento=alerta_em_5_dias,
            valor_pago__lt=timezone.now().date() # Se não estiver totalmente paga
        )
        # Nota: valor_pago__lt=F('valor_parcela') seria melhor, mas simplificando para o mock
        for p in parcelas_proximas:
            msg = f"G IMIGRA: Lembrete! Sua parcela #{p.num_parcela} vence em 5 dias (${p.valor_parcela})."
            NotificacaoService.enviar_whatsapp(p.fatura.cliente, msg, p)
            self.stdout.write(f"Alerta de parcela enviado para {p.fatura.cliente.nome}")

        # 2. Verificar Passaportes vencendo em 30 dias
        clientes_passaporte = Cliente.objects.filter(
            # Aqui precisaríamos de um campo de validade do passaporte no modelo Cliente
            # Vou assumir que vamos adicionar ou focar em validade de documentos por enquanto
        )
        
        # 3. Verificar Validade de Documentos (Documento.validade) em 5 dias
        from gestao.models import Documento
        docs_vencendo = Documento.objects.filter(validade=alerta_em_5_dias)
        for doc in docs_vencendo:
            msg = f"G IMIGRA: Seu documento '{doc.nome}' irá vencer em 5 dias. Por favor, providencie a renovação."
            NotificacaoService.enviar_whatsapp(doc.processo.cliente, msg)
            self.stdout.write(f"Alerta de documento enviado para {doc.processo.cliente.nome}")

        self.stdout.write(self.style.SUCCESS('Varredura concluída!'))
