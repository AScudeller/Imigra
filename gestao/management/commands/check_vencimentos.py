from django.core.management.base import BaseCommand
from gestao.models import Cliente, Parcela, Processo, LogNotificacao, Documento
from gestao.notifications import NotificacaoService
from django.utils import timezone
from django.db.models import F
from datetime import timedelta

class Command(BaseCommand):
    help = 'Verifica vencimentos proativos (Parcelas, Documentos) e envia alertas automáticos.'

    def handle(self, *args, **options):
        hoje = timezone.now().date()
        alerta_em_5_dias = hoje + timedelta(days=5)
        
        self.stdout.write(self.style.SUCCESS('🔍 Iniciando varredura de vencimentos...'))

        # 1. PARCELAS ATRASADAS (Enviar notificação imediata)
        parcelas_atrasadas = Parcela.objects.filter(
            data_vencimento__lt=hoje,
            valor_pago__lt=F('valor_parcela')
        ).exclude(fatura__status='CANCELADO').select_related('fatura__cliente')
        
        for p in parcelas_atrasadas:
            dias_atraso = (hoje - p.data_vencimento).days
            saldo = p.valor_parcela - p.valor_pago
            
            # Enviar notificação apenas se não foi enviada recentemente (últimas 24h)
            ultima_notif = LogNotificacao.objects.filter(
                cliente=p.fatura.cliente,
                parcela=p,
                data_envio__gte=hoje - timedelta(days=1)
            ).exists()
            
            if not ultima_notif:
                msg = f"⚠️ G IMIGRA: Sua parcela #{p.num_parcela} está ATRASADA há {dias_atraso} dias. Saldo devedor: ${saldo:.2f}. Por favor, regularize o quanto antes."
                NotificacaoService.enviar_whatsapp(p.fatura.cliente, msg, p)
                self.stdout.write(f"  ⚠️  Alerta de ATRASO enviado para {p.fatura.cliente.nome} (Parcela #{p.num_parcela})")

        # 2. PARCELAS A VENCER EM 5 DIAS (Lembrete preventivo)
        parcelas_proximas = Parcela.objects.filter(
            data_vencimento=alerta_em_5_dias,
            valor_pago__lt=F('valor_parcela')
        ).exclude(fatura__status='CANCELADO').select_related('fatura__cliente')
        
        for p in parcelas_proximas:
            saldo = p.valor_parcela - p.valor_pago
            msg = f"📅 G IMIGRA: Lembrete! Sua parcela #{p.num_parcela} vence em 5 dias ({p.data_vencimento.strftime('%d/%m/%Y')}). Valor: ${saldo:.2f}."
            NotificacaoService.enviar_whatsapp(p.fatura.cliente, msg, p)
            self.stdout.write(f"  📅 Lembrete de vencimento enviado para {p.fatura.cliente.nome}")

        # 3. DOCUMENTOS VENCENDO EM 5 DIAS
        docs_vencendo = Documento.objects.filter(
            validade=alerta_em_5_dias
        ).select_related('processo__cliente')
        
        for doc in docs_vencendo:
            msg = f"📄 G IMIGRA: Seu documento '{doc.nome}' irá vencer em 5 dias ({doc.validade.strftime('%d/%m/%Y')}). Por favor, providencie a renovação."
            NotificacaoService.enviar_whatsapp(doc.processo.cliente, msg)
            self.stdout.write(f"  📄 Alerta de documento enviado para {doc.processo.cliente.nome}")

        self.stdout.write(self.style.SUCCESS('✅ Varredura concluída!'))
