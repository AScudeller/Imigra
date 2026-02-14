from django.core.management.base import BaseCommand
from gestao.notifications import NotificacaoService

class Command(BaseCommand):
    help = 'Varre parcelas e envia notificações de vencimento e atraso'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando varredura de parcelas...')
        NotificacaoService.varrer_parcelas_e_notificar()
        self.stdout.write(self.style.SUCCESS('Varredura concluída com sucesso!'))
